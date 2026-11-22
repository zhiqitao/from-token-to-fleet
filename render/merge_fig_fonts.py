#!/usr/bin/env python3
"""
merge_fig_fonts.py — collapse matplotlib's per-figure DejaVu Identity-H font
subsets in the book PDF into ONE subset per face, without touching any text.

WHY THIS IS SAFE (and why no content stream is rewritten)
---------------------------------------------------------
matplotlib's PDF backend embeds one DejaVu subset per figure and, for every
subset, it builds the CID space as the *Unicode codepoint space*: for each
non-zero CID c the /ToUnicode CMap maps c -> the single character U+00c.
This script verifies that invariant per font (and the /W width, and the glyph
outline itself) before it will touch a font.  Because every subset of a face
therefore speaks the same CID space, the glyph IDs used in the page content
streams stay valid as-is: we only repoint each Type0 font of that face at a
single shared CIDFontType2 whose /CIDToGIDMap, /W and /ToUnicode cover the
union of glyphs.  Old CID -> merged CID is the identity; old CID -> old GID ->
merged GID is recorded per font in the JSON report.

A font is left completely untouched (partial merge, never an approximation) if
any of these cannot be proven:
  * /CIDToGIDMap is /Identity instead of an explicit array (different CID space)
  * CID 0 maps to a real glyph (e.g. the single-glyph "fi" ligature fonts)
  * ToUnicode(c) is not exactly chr(c)
  * the embedded glyph outline differs from the system DejaVu outline
  * a CID actually used by a page content stream is not present in the subset
  * its advance width for some CID disagrees with the other subsets of the face

Usage:
    merge_fig_fonts.py --src build/from-token-to-fleet-v20260913.pdf \
                       --out build/from-token-to-fleet-v20260913-merged.pdf
    merge_fig_fonts.py --dry-run          # print the plan, write nothing
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import struct
import sys
import zlib
from collections import defaultdict

import pymupdf
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

# --------------------------------------------------------------------------- #
# config
# --------------------------------------------------------------------------- #

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DEFAULT = os.path.join(HERE, "build", "from-token-to-fleet-v20260913.pdf")
OUT_DEFAULT = os.path.join(HERE, "build", "from-token-to-fleet-v20260913-merged.pdf")
REPORT_DEFAULT = os.path.join(HERE, "build", "merge_fig_fonts_report.json")

FONT_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu"]
FACE_FILE = {
    "DejaVuSans": "DejaVuSans.ttf",
    "DejaVuSans-Bold": "DejaVuSans-Bold.ttf",
    "DejaVuSans-Oblique": "DejaVuSans-Oblique.ttf",
    "DejaVuSans-BoldOblique": "DejaVuSans-BoldOblique.ttf",
    "DejaVuSansMono": "DejaVuSansMono.ttf",
    "DejaVuSansMono-Bold": "DejaVuSansMono-Bold.ttf",
}
SUBSET_TAG = "FTFMRG"          # 6 uppercase letters, as required by the spec
TAG_RE = re.compile(r"^[A-Z]{6}\+")


def face_of(basefont: str) -> str:
    return TAG_RE.sub("", basefont)


def system_font(face: str) -> str | None:
    name = FACE_FILE.get(face)
    if not name:
        return None
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return None


# --------------------------------------------------------------------------- #
# PDF helpers
# --------------------------------------------------------------------------- #

def refnum(obj_text: str, key: str):
    m = re.search(re.escape(key) + r"\s+(\d+)\s+0\s+R", obj_text)
    return int(m.group(1)) if m else None


def name_of(obj_text: str, key: str):
    m = re.search(re.escape(key) + r"\s*/([^\s/<>\[\]()]+)", obj_text)
    return m.group(1) if m else None


def resolve(doc, xref, key):
    """Return the xref a dict key points to (following one indirect ref), or None."""
    o = doc.xref_object(xref, compressed=False)
    return refnum(o, key)


def parse_tounicode(data: bytes) -> dict[int, str]:
    """cid -> replacement text, from a ToUnicode CMap (bfchar + both bfrange forms)."""
    s = data.decode("latin-1")
    out: dict[int, str] = {}

    def u16(hexs: str) -> str:
        b = bytes.fromhex(hexs if len(hexs) % 2 == 0 else "0" + hexs)
        try:
            return b.decode("utf-16-be")
        except UnicodeDecodeError:
            return "\ufffd"

    for block in re.findall(r"beginbfchar(.*?)endbfchar", s, re.S):
        for src, dst in re.findall(r"<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>", block):
            out[int(src, 16)] = u16(dst)
    for block in re.findall(r"beginbfrange(.*?)endbfrange", s, re.S):
        # <lo> <hi> [ <d1> <d2> ... ]
        for lo, hi, body in re.findall(
            r"<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*\[(.*?)\]", block, re.S
        ):
            lo_i, hi_i = int(lo, 16), int(hi, 16)
            dsts = re.findall(r"<([0-9a-fA-F]+)>", body)
            for k, d in enumerate(dsts):
                if lo_i + k <= hi_i:
                    out[lo_i + k] = u16(d)
        # <lo> <hi> <dst>   (incrementing form)
        stripped = re.sub(r"<[0-9a-fA-F]+>\s*<[0-9a-fA-F]+>\s*\[.*?\]", " ", block, flags=re.S)
        for lo, hi, dst in re.findall(
            r"<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>", stripped
        ):
            lo_i, hi_i = int(lo, 16), int(hi, 16)
            base = bytes.fromhex(dst)
            if len(base) != 2:
                continue
            b0 = int.from_bytes(base, "big")
            for k in range(hi_i - lo_i + 1):
                out[lo_i + k] = chr(b0 + k) if b0 + k <= 0x10FFFF else "\ufffd"
    return out


def parse_w(data: str) -> dict[int, float]:
    """/W array -> {cid: width}.  Handles both the `c [w...]` and `c1 c2 w` forms."""
    body = data[data.find("[") + 1: data.rfind("]")]
    toks = re.findall(r"\[|\]|-?\d+\.?\d*", body)
    out: dict[int, float] = {}
    i = 0
    while i < len(toks):
        if toks[i] in "[]":
            i += 1
            continue
        first = float(toks[i])
        if i + 1 < len(toks) and toks[i + 1] == "[":
            j = i + 2
            ws = []
            while j < len(toks) and toks[j] != "]":
                ws.append(float(toks[j]))
                j += 1
            for k, w in enumerate(ws):
                out[int(first) + k] = w
            i = j + 1
        elif i + 2 < len(toks) and toks[i + 1] not in "[]" and toks[i + 2] not in "[]":
            c1, c2, w = int(float(toks[i])), int(float(toks[i + 1])), float(toks[i + 2])
            for c in range(c1, c2 + 1):
                out[c] = w
            i += 3
        else:
            i += 1
    return out


def fmt_w(widths: dict[int, float]) -> str:
    """{cid: width} -> compact /W array text."""
    parts = []
    cids = sorted(widths)
    i = 0
    while i < len(cids):
        j = i
        while j + 1 < len(cids) and cids[j + 1] == cids[j] + 1:
            j += 1
        run = cids[i: j + 1]
        vals = " ".join(str(int(widths[c])) if float(widths[c]).is_integer() else f"{widths[c]:g}"
                        for c in run)
        parts.append(f"{run[0]} [ {vals} ]")
        i = j + 1
    return "[ " + " ".join(parts) + " ]"


# --------------------------------------------------------------------------- #
# content stream lexer (read-only: we only *look* at CIDs, never rewrite them)
# --------------------------------------------------------------------------- #

DELIM = b" \t\r\n\f\x00/[]<>(){}%"


def lex(data: bytes):
    """Yield (kind, value) tokens of a PDF content stream."""
    i, n = 0, len(data)
    while i < n:
        c = data[i: i + 1]
        if c in b" \t\r\n\f\x00":
            i += 1
            continue
        if c == b"%":
            while i < n and data[i: i + 1] not in b"\r\n":
                i += 1
            continue
        if c == b"(":
            depth, i, buf = 1, i + 1, bytearray()
            while i < n and depth:
                ch = data[i: i + 1]
                if ch == b"\\":
                    buf += data[i: i + 2]
                    i += 2
                    continue
                if ch == b"(":
                    depth += 1
                elif ch == b")":
                    depth -= 1
                if depth:
                    buf += ch
                i += 1
            yield ("str", bytes(buf))
            continue
        if c == b"<":
            if data[i: i + 2] == b"<<":
                yield ("op", "<<")
                i += 2
                continue
            j = data.find(b">", i)
            if j < 0:
                return
            yield ("hex", data[i + 1: j].strip())
            i = j + 1
            continue
        if c == b">":
            if data[i: i + 2] == b">>":
                yield ("op", ">>")
                i += 2
                continue
            i += 1
            continue
        if c in b"[]{}":
            yield ("op", c.decode())
            i += 1
            continue
        if c == b"/":
            j = i + 1
            while j < n and data[j: j + 1] not in DELIM:
                j += 1
            yield ("name", data[i + 1: j].decode("latin-1"))
            i = j
            continue
        j = i
        while j < n and data[j: j + 1] not in DELIM:
            j += 1
        tok = data[i: j]
        try:
            yield ("num", float(tok))
        except ValueError:
            yield ("op", tok.decode("latin-1"))
        i = j


class PageCidScanner:
    """Tracks /F<n> Tf and collects the 2-byte CIDs shown with each font."""

    INLINE_IMG = re.compile(rb"\bBI\b.*?\bEI\b", re.S)

    def __init__(self, doc, name_to_xref):
        self.doc = doc
        self.map = name_to_xref

    def scan_stream(self, raw: bytes) -> dict[int, set[int]]:
        used: dict[int, set[int]] = defaultdict(set)
        # inline image data is binary and may contain '<' or 'Tf'-like bytes
        raw = self.INLINE_IMG.sub(b" ", raw)
        cur = None
        pending_name = None
        last_hex = None
        arr: list[bytes] | None = None
        for kind, val in lex(raw):
            if kind == "name":
                pending_name = val
            elif kind == "hex":
                if arr is not None:
                    arr.append(val)
                last_hex = val
            elif kind == "op":
                if val == "[":
                    arr = []
                elif val == "]":
                    arr = None
                elif val == "Tf":
                    cur = self.map.get(pending_name)
                elif val in ("Tj", "'", '"'):
                    if cur is not None and last_hex:
                        used[cur].update(cids_of(last_hex))
                    last_hex = None
                elif val == "TJ":
                    if cur is not None and arr:
                        for h in arr:
                            used[cur].update(cids_of(h))
                    arr = None
                    last_hex = None
        return used


def cids_of(hexstr: bytes) -> list[int]:
    h = re.sub(rb"\s", b"", hexstr)
    if len(h) % 4:            # not a 2-byte CID string
        return []
    try:
        b = bytes.fromhex(h.decode("ascii"))
    except ValueError:
        return []
    return [int.from_bytes(b[i: i + 2], "big") for i in range(0, len(b), 2)]


# --------------------------------------------------------------------------- #
# font inventory
# --------------------------------------------------------------------------- #

class FontRec:
    __slots__ = ("type0", "basefont", "face", "descendant", "tounicode", "descriptor",
                 "fontfile2", "w_xref", "c2g_xref", "c2g", "tu", "widths",
                 "tt", "cmap", "data", "raw_len", "pages", "names", "used_cids",
                 "why_not")

    def __init__(self):
        self.why_not = []
        self.pages = []
        self.names = set()
        self.used_cids = set()


def inventory(doc) -> list[FontRec]:
    recs = []
    for x in range(1, doc.xref_length()):
        try:
            o = doc.xref_object(x, compressed=False)
        except Exception:
            continue
        if "/Subtype /Type0" not in o or "DejaVu" not in o:
            continue
        r = FontRec()
        r.type0 = x
        r.basefont = name_of(o, "/BaseFont")
        r.face = face_of(r.basefont)
        r.descendant = int(re.search(r"/DescendantFonts \[\s*(\d+)\s+0\s+R", o).group(1))
        r.tounicode = refnum(o, "/ToUnicode")
        do = doc.xref_object(r.descendant, compressed=False)
        r.descriptor = refnum(do, "/FontDescriptor")
        r.w_xref = refnum(do, "/W")
        r.c2g_xref = refnum(do, "/CIDToGIDMap")
        fd = doc.xref_object(r.descriptor, compressed=False)
        r.fontfile2 = refnum(fd, "/FontFile2")
        r.data = doc.xref_stream(r.fontfile2)
        r.raw_len = len(doc.xref_stream_raw(r.fontfile2))   # on-disk (compressed)
        r.tt = TTFont(io.BytesIO(r.data))
        r.cmap = r.tt.getBestCmap()
        r.tu = parse_tounicode(doc.xref_stream(r.tounicode))
        if r.w_xref is None:
            r.widths = {}
        else:
            r.widths = parse_w(doc.xref_object(r.w_xref, compressed=False))
        if r.c2g_xref is None:
            r.c2g = None                      # /Identity
        else:
            raw = doc.xref_stream(r.c2g_xref)
            r.c2g = list(struct.unpack(">%dH" % (len(raw) // 2), raw))
        recs.append(r)
    return recs


def balanced(text: str, start: int) -> str:
    """Return the balanced << ... >> block beginning at or after `start`."""
    i = text.find("<<", start)
    if i < 0:
        return ""
    depth = 0
    j = i
    while j < len(text):
        if text.startswith("<<", j):
            depth += 1
            j += 2
            continue
        if text.startswith(">>", j):
            depth -= 1
            j += 2
            if depth == 0:
                return text[i:j]
            continue
        j += 1
    return text[i:]


def dict_value(doc, obj_text: str, key: str) -> str:
    """Body of `key` in a dict, following one indirect ref or an inline <<...>>."""
    m = re.search(re.escape(key) + r"\s+(\d+)\s+0\s+R", obj_text)
    if m:
        return doc.xref_object(int(m.group(1)), compressed=False)
    m = re.search(re.escape(key) + r"\s*<<", obj_text)
    if m:
        return balanced(obj_text, m.start())
    return ""


# --------------------------------------------------------------------------- #
# glyph hashing
# --------------------------------------------------------------------------- #

def glyph_hash(font: TTFont, gname: str) -> str:
    """Index-independent outline signature.

    A compiled composite glyph embeds the *glyph indices* of its components, so
    the same shape hashes differently in two subsets with different glyph order.
    Decomposing to contours compares the actual outline instead.
    """
    gs = font.getGlyphSet()
    pen = DecomposingRecordingPen(gs)
    gs[gname].draw(pen)
    return hashlib.sha256(repr(pen.value).encode()).hexdigest()


# --------------------------------------------------------------------------- #
# merged font construction
# --------------------------------------------------------------------------- #

def build_merged(face: str, codepoints: set[int], syspath: str) -> TTFont:
    opts = Options()
    opts.hinting = True            # keep fpgm/prep/cvt: identical rasterisation
    opts.desubroutinize = False
    opts.retain_gids = False
    opts.notdef_outline = True
    opts.recommended_glyphs = True
    opts.name_IDs = ["*"]
    opts.name_legacy = True
    opts.name_languages = ["*"]
    opts.layout_features = ["*"]
    opts.glyph_names = True
    opts.symbol_cmap = False
    opts.legacy_cmap = False
    opts.prune_unicode_ranges = False
    opts.recalc_bounds = False
    opts.recalc_timestamp = False
    opts.canonical_order = True

    font = TTFont(syspath, recalcBBoxes=False, recalcTimestamp=False)
    sub = Subsetter(options=opts)
    sub.populate(unicodes=sorted(codepoints))
    sub.subset(font)
    # PDF viewers never read the name table (they use /BaseFont + /ToUnicode) and
    # never apply OpenType math layout; both are pure weight here.
    if "name" in font:
        font["name"].names = [
            n for n in font["name"].names
            if n.nameID in (0, 1, 2, 3, 4, 5, 6)
            and (n.platformID, n.platEncID, n.langID) in ((3, 1, 0x409), (1, 0, 0))
        ]
    if "MATH" in font:
        del font["MATH"]
    return font


def font_bytes(font: TTFont) -> bytes:
    buf = io.BytesIO()
    font.save(buf)
    return buf.getvalue()


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC_DEFAULT)
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--report", default=REPORT_DEFAULT)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--objstm", action="store_true",
                    help="also pack object definitions into compressed object "
                         "streams (PDF 1.5+, unrelated to the font merge)")
    args = ap.parse_args(argv)

    src_bytes = os.path.getsize(args.src)
    print(f"source : {args.src}  ({src_bytes} bytes)")

    doc = pymupdf.open(args.src)
    pages_before = doc.page_count
    print(f"pages  : {pages_before}")

    recs = inventory(doc)
    print(f"DejaVu Type0 fonts: {len(recs)}")
    by_face = defaultdict(list)
    for r in recs:
        by_face[r.face].append(r)

    # ---- usage: page association (for the report) + CIDs actually shown --- #
    # matplotlib draws each figure into a Form XObject; the DejaVu subsets live
    # in *its* /Resources, not the page's.  So: page.get_fonts() for the
    # page<->font association, and a scan of every object that carries a
    # /Resources /Font dict (pages and Form XObjects alike) for the CIDs.
    for page in doc:
        for f in page.get_fonts(full=True):
            fx, base, nm = f[0], f[3], f[4]
            for r in recs:
                if r.type0 == fx:
                    r.pages.append(page.number + 1)
                    r.names.add(nm)

    scanner = PageCidScanner(doc, {})
    scanned = 0
    for x in range(1, doc.xref_length()):
        try:
            o = doc.xref_object(x, compressed=False)
        except Exception:
            continue
        if "/Font" not in o:
            continue
        res = dict_value(doc, o, "/Resources") if "/Resources" in o else o
        if not res:
            continue
        fonts = dict_value(doc, res, "/Font")
        if not fonts:
            continue
        nm = {n: int(t) for n, t in
              re.findall(r"/([^\s/<>\[\]()]+)\s+(\d+)\s+0\s+R", fonts)}
        if not any(any(r.type0 == v for r in recs) for v in nm.values()):
            continue
        raw = doc.xref_stream(x)
        if not raw:
            continue
        scanned += 1
        scanner.map = nm
        for fx, cids in scanner.scan_stream(raw).items():
            for r in recs:
                if r.type0 == fx:
                    r.used_cids |= cids

    print(f"pages using DejaVu: {len({p for r in recs for p in r.pages})} "
          f"({scanned} content streams scanned for CIDs)")

    # ---- classify --------------------------------------------------------- #
    for r in recs:
        if r.c2g is None:
            r.why_not.append("CIDToGIDMap is /Identity")
            continue
        if len(r.c2g) != (max([i for i, v in enumerate(r.c2g) if v], default=-1) + 1):
            r.why_not.append("CIDToGIDMap array longer than last non-zero CID")
        if r.c2g and r.c2g[0] != 0:
            r.why_not.append("CID 0 maps to a real glyph (ligature font)")
        for cid, gid in enumerate(r.c2g):
            if gid == 0:
                continue
            t = r.tu.get(cid)
            if t is None or len(t) != 1 or ord(t) != cid:
                r.why_not.append(f"ToUnicode({cid})={t!r} != {chr(cid)!r}")
                break
            if cid not in r.cmap:
                r.why_not.append(f"subset has no cmap entry for U+{cid:04X}")
                break
        missing = {c for c in r.used_cids if c and (c >= len(r.c2g) or r.c2g[c] == 0)}
        if missing:
            r.why_not.append(
                f"{len(missing)} shown CID(s) absent from subset, e.g. "
                + ", ".join(f"0x{c:04x}" for c in sorted(missing)[:5])
            )

    # ---- per-face width consistency --------------------------------------- #
    for face, group in by_face.items():
        seen: dict[int, float] = {}
        for r in group:
            for cid, w in r.widths.items():
                if cid in seen and seen[cid] != w:
                    r.why_not.append(f"width conflict at CID {cid}: {w} vs {seen[cid]}")
                seen.setdefault(cid, w)

    # ---- glyph outline identity vs the system font ------------------------ #
    for face, group in by_face.items():
        syspath = system_font(face)
        if not syspath:
            for r in group:
                r.why_not.append(f"no system font for face {face}")
            continue
        sysf = TTFont(syspath, recalcBBoxes=False, recalcTimestamp=False)
        syscmap = sysf.getBestCmap()
        for r in group:
            if r.why_not:
                continue
            bad = 0
            for cid, gid in enumerate(r.c2g):
                if not gid:
                    continue
                if cid not in syscmap:
                    bad += 1
                    continue
                if glyph_hash(r.tt, r.cmap[cid]) != glyph_hash(sysf, syscmap[cid]):
                    bad += 1
            if bad:
                r.why_not.append(f"{bad} glyph outline(s) differ from {os.path.basename(syspath)}")
        sysf.close()

    eligible = [r for r in recs if not r.why_not]
    skipped = [r for r in recs if r.why_not]

    print("\n--- eligibility ---")
    for face in sorted(by_face):
        g = by_face[face]
        el = [r for r in g if not r.why_not]
        print(f"{face:26s} {len(g):3d} fonts, {len(el):3d} mergeable, "
              f"{sum(r.raw_len for r in g):7d} B on disk, "
              f"{sum(r.raw_len for r in el):7d} B mergeable")
    for r in skipped:
        print(f"  skip {r.type0:6d} {r.basefont:34s} {r.raw_len:6d} B : {r.why_not[0]}")

    # ---- build the merged font per face ----------------------------------- #
    merged = {}
    for face in sorted({r.face for r in eligible}):
        group = [r for r in eligible if r.face == face]
        cps = set()
        for r in group:
            cps |= {cid for cid, gid in enumerate(r.c2g) if gid}
        syspath = system_font(face)
        tt = build_merged(face, cps, syspath)
        mcmap = tt.getBestCmap()

        # exact glyph-outline check of the merged font against every original
        ok = True
        for r in group:
            for cid, gid in enumerate(r.c2g):
                if not gid:
                    continue
                if cid not in mcmap:
                    r.why_not.append(f"merged font lost U+{cid:04X}")
                    ok = False
                    break
                if glyph_hash(tt, mcmap[cid]) != glyph_hash(r.tt, r.cmap[cid]):
                    r.why_not.append(f"merged glyph differs at U+{cid:04X}")
                    ok = False
                    break
            if not ok:
                break
        if not ok:
            continue
        data = font_bytes(tt)
        old_bytes = sum(r.raw_len for r in group)
        if len(data) >= old_bytes:
            for r in group:
                r.why_not.append(
                    f"merged subset ({len(data)} B) not smaller than {old_bytes} B")
            continue
        cid2gid = {}
        for cid in sorted(cps):
            cid2gid[cid] = tt.getGlyphID(mcmap[cid])
        widths: dict[int, float] = {}
        for r in group:
            for cid, w in r.widths.items():
                widths.setdefault(cid, w)
        merged[face] = dict(tt=tt, data=data, cid2gid=cid2gid, widths=widths,
                            cps=cps, group=group, raw_len=len(zlib.compress(data)))

    # fonts that failed the merged check fall back to untouched
    eligible = [r for r in eligible if r.face in merged and r in merged[r.face]["group"]]

    print("\n--- merged subsets ---")
    tot_old = sum(r.raw_len for r in eligible)
    tot_new = sum(m["raw_len"] for m in merged.values())
    for face, m in sorted(merged.items()):
        old = sum(r.raw_len for r in m["group"])
        print(f"{face:26s} {len(m['group']):3d} fonts -> 1   "
              f"{old:7d} B -> {m['raw_len']:6d} B   ({len(m['cps'])} glyphs)")
    print(f"{'TOTAL':26s} {len(eligible):3d} fonts -> {len(merged)}   "
          f"{tot_old:7d} B -> {tot_new:6d} B   expected saving {tot_old - tot_new} B")
    if args.dry_run:
        print("\n(dry run: nothing written)")
        return 0

    # ---- write ------------------------------------------------------------ #
    work = args.out + ".work"
    shutil.copy2(args.src, work)                 # never touch the source
    doc.close()
    doc = pymupdf.open(work)

    # re-resolve the same objects by their identifying keys (xrefs are stable
    # in the copy because it is a byte-for-byte copy).
    created = {}
    for face, m in merged.items():
        tt = m["tt"]
        hhea, head, post = tt["hhea"], tt["head"], tt["post"]
        upem = head.unitsPerEm
        s = 1000.0 / upem
        bbox = [int(round(v * s)) for v in (head.xMin, head.yMin, head.xMax, head.yMax)]
        cap = 0
        try:
            cap = int(round(getattr(tt["OS/2"], "sCapHeight", 0) * s))
        except Exception:
            pass
        asc = int(round(hhea.ascent * s))
        desc = int(round(hhea.descent * s))
        fname = f"{SUBSET_TAG}+{face}"

        x_ff = doc.get_new_xref()
        doc.update_object(x_ff, "<< /Length 0 >>")
        doc.update_stream(x_ff, m["data"], compress=True)
        doc.xref_set_key(x_ff, "Length1", str(len(m["data"])))
        m["raw_len"] = len(doc.xref_stream_raw(x_ff))

        x_fd = doc.get_new_xref()
        doc.update_object(
            x_fd,
            f"<< /Type /FontDescriptor /FontName /{fname} /Flags 32 "
            f"/FontBBox [ {' '.join(map(str, bbox))} ] /ItalicAngle "
            f"{int(round(post.italicAngle))} /Ascent {asc} /Descent {desc} "
            f"/CapHeight {cap} /StemV 0 /FontFile2 {x_ff} 0 R >>",
        )

        # /CIDToGIDMap as an explicit big-endian array (CID stays == codepoint)
        maxcid = max(m["cid2gid"])
        arr = bytearray(2 * (maxcid + 1))
        for cid, gid in m["cid2gid"].items():
            struct.pack_into(">H", arr, 2 * cid, gid)
        x_c2g = doc.get_new_xref()
        doc.update_object(x_c2g, "<< /Length 0 >>")
        doc.update_stream(x_c2g, bytes(arr), compress=True)

        x_w = doc.get_new_xref()
        doc.update_object(x_w, fmt_w(m["widths"]))

        x_cid = doc.get_new_xref()
        doc.update_object(
            x_cid,
            f"<< /Type /Font /Subtype /CIDFontType2 /BaseFont /{fname} "
            f"/CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> "
            f"/FontDescriptor {x_fd} 0 R /W {x_w} 0 R /CIDToGIDMap {x_c2g} 0 R /DW 1000 >>",
        )

        # ToUnicode: CID -> chr(CID), identical to what each original declared
        lines = []
        cids = sorted(m["cid2gid"])
        i = 0
        while i < len(cids):
            j = i
            while j + 1 < len(cids) and cids[j + 1] == cids[j] + 1:
                j += 1
            lines.append(f"<{cids[i]:04X}> <{cids[j]:04X}> <{cids[i]:04X}>")
            i = j + 1
        cmap = (
            "/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n"
            "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n"
            "/CMapName /Adobe-Identity-UCS def\n/CMapType 2 def\n"
            "1 begincodespacerange\n<0000> <FFFF>\nendcodespacerange\n"
            f"{len(lines)} beginbfrange\n" + "\n".join(lines) +
            "\nendbfrange\nendcmap\nCMapName currentdict /CMap defineresource pop\nend\nend\n"
        )
        x_tu = doc.get_new_xref()
        doc.update_object(x_tu, "<< /Length 0 >>")
        doc.update_stream(x_tu, cmap.encode("latin-1"), compress=True)

        created[face] = dict(cid=x_cid, tu=x_tu, fd=x_fd, ff=x_ff, w=x_w, c2g=x_c2g, name=fname)
        print(f"built {face:26s} fontfile2={len(m['data']):6d} B  glyphs={len(m['cps'])}")

    # repoint every mergeable Type0 font
    n_rep = 0
    for r in eligible:
        c = created[r.face]
        o = doc.xref_object(r.type0, compressed=False)
        o2 = re.sub(r"/DescendantFonts \[\s*\d+\s+0\s+R\s*\]",
                    f"/DescendantFonts [ {c['cid']} 0 R ]", o)
        o2 = re.sub(r"/ToUnicode\s+\d+\s+0\s+R", f"/ToUnicode {c['tu']} 0 R", o2)
        o2 = re.sub(r"/BaseFont\s*/\S+", f"/BaseFont /{c['name']}", o2)
        doc.update_object(r.type0, o2)
        n_rep += 1
    print(f"repointed {n_rep} Type0 fonts at {len(created)} merged descendants")

    doc.save(args.out, garbage=4, deflate=True, clean=False, pretty=False,
             use_objstms=1 if args.objstm else 0)
    doc.close()
    os.remove(work)

    out_bytes = os.path.getsize(args.out)
    print(f"\nwritten: {args.out}  {out_bytes} bytes "
          f"({src_bytes - out_bytes} saved, {100.0 * (src_bytes - out_bytes) / src_bytes:.2f}%)")

    # ---- report ----------------------------------------------------------- #
    rep = {
        "source": args.src, "source_bytes": src_bytes,
        "output": args.out, "output_bytes": out_bytes,
        "saving_bytes": src_bytes - out_bytes,
        "pages": pages_before,
        "fonts_total": len(recs), "fonts_merged": len(eligible),
        "fonts_untouched": len(skipped),
        "merged_faces": {
            f: {"from": len(m["group"]),
                "bytes_before": sum(r.raw_len for r in m["group"]),
                "bytes_after": m["raw_len"],
                "bytes_after_decompressed": len(m["data"]),
                "glyphs": len(m["cps"]),
                "fonts": [{"xref": r.type0, "basefont": r.basefont, "pages": r.pages,
                           "names": sorted(r.names),
                           "cid_to_merged_cid": {str(c): c for c in sorted(m["cid2gid"]) if c in r.used_cids},
                           "cid_to_gid_old": {str(c): r.c2g[c] for c in sorted(r.used_cids) if c < len(r.c2g)},
                           "cid_to_gid_merged": {str(c): m["cid2gid"][c] for c in sorted(r.used_cids) if c in m["cid2gid"]}}
                          for r in m["group"]]}
            for f, m in merged.items()},
        "untouched": [{"xref": r.type0, "basefont": r.basefont, "bytes": r.raw_len,
                       "reason": r.why_not[0]} for r in skipped],
    }
    with open(args.report, "w") as fh:
        json.dump(rep, fh, indent=1)
    print(f"report : {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
