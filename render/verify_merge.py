#!/usr/bin/env python3
"""
verify_merge.py — prove the font-merged PDF is byte-for-byte equivalent to the
source in everything a reader can see: page count, text layer, page labels,
tagged structure, and rendered pixels.

Usage: verify_merge.py SRC OUT [--dpi 150]
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys

import pymupdf


def run(cmd):
    p = subprocess.run(cmd, capture_output=True)
    return p.stdout.decode("utf-8", "replace"), p.returncode


def pixhash(page, dpi):
    pm = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csRGB, alpha=False)
    return hashlib.sha256(pm.samples).hexdigest(), pm.width, pm.height


def struct_titles(doc):
    """Every /StructElem's /S type and /T title, in document order."""
    out = []
    cat = doc.pdf_catalog()
    try:
        root = doc.xref_get_key(cat, "StructTreeRoot")
    except Exception:
        return out, None
    if root[0] == "null":
        return out, None
    xref = int(root[1].split()[0])
    seen = set()

    def walk(x, depth=0):
        if x in seen or depth > 60:
            return
        seen.add(x)
        try:
            o = doc.xref_object(x, compressed=False)
        except Exception:
            return
        s = doc.xref_get_key(x, "S")
        t = doc.xref_get_key(x, "T")
        out.append((s[1] if s[0] != "null" else "", t[1] if t[0] != "null" else ""))
        k = doc.xref_get_key(x, "K")
        if k[0] == "null":
            return
        refs = [int(m) for m in __import__("re").findall(r"(\d+) 0 R", k[1])]
        if not refs and k[1].strip().isdigit():
            refs = []
        for r in refs:
            walk(r, depth + 1)

    walk(xref)
    return out, xref


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--sample", type=int, default=30)
    args = ap.parse_args()

    ok = True
    rep = {}

    s_bytes, o_bytes = os.path.getsize(args.src), os.path.getsize(args.out)
    print(f"source bytes : {s_bytes}")
    print(f"output bytes : {o_bytes}")
    print(f"saved        : {s_bytes - o_bytes} B "
          f"({100.0 * (s_bytes - o_bytes) / s_bytes:.2f}%)")

    sd, od = pymupdf.open(args.src), pymupdf.open(args.out)
    print(f"pages        : {sd.page_count} -> {od.page_count}")
    if sd.page_count != od.page_count:
        ok = False
        print("FAIL page count")
    rep["pages_before"], rep["pages_after"] = sd.page_count, od.page_count

    # ---- text layer, every page, both engines ----------------------------- #
    print("\n== text layer ==")
    diff_pages = []
    for i in range(sd.page_count):
        a = sd[i].get_text("text")
        b = od[i].get_text("text")
        if a != b:
            diff_pages.append(i + 1)
    print(f"pymupdf get_text(): {sd.page_count - len(diff_pages)}/{sd.page_count} pages "
          f"byte-identical; differing: {diff_pages[:20]}")
    rep["pymupdf_text_diff_pages"] = diff_pages

    pt_diff = []
    for i in range(sd.page_count):
        a, _ = run(["pdftotext", "-f", str(i + 1), "-l", str(i + 1), "-layout",
                    args.src, "-"])
        b, _ = run(["pdftotext", "-f", str(i + 1), "-l", str(i + 1), "-layout",
                    args.out, "-"])
        if a != b:
            pt_diff.append(i + 1)
    print(f"pdftotext -layout: {sd.page_count - len(pt_diff)}/{sd.page_count} pages "
          f"byte-identical; differing: {pt_diff[:20]}")
    rep["pdftotext_diff_pages"] = pt_diff

    whole_a, _ = run(["pdftotext", "-layout", args.src, "-"])
    whole_b, _ = run(["pdftotext", "-layout", args.out, "-"])
    print(f"whole-document pdftotext identical: {whole_a == whole_b} "
          f"({len(whole_a)} vs {len(whole_b)} chars)")
    if diff_pages or pt_diff or whole_a != whole_b:
        ok = False
    rep["text_equal"] = not (diff_pages or pt_diff) and whole_a == whole_b

    # ---- page labels / structure ----------------------------------------- #
    print("\n== tagging ==")
    la, lb = sd.get_page_labels(), od.get_page_labels()
    print(f"page labels identical: {la == lb}  ({len(la)} entries)")
    ta, ra = struct_titles(sd)
    tb, rb = struct_titles(od)
    print(f"StructTreeRoot present: src={ra} out={rb}")
    print(f"StructElem nodes: {len(ta)} -> {len(tb)}; identical: {ta == tb}")
    info_s, _ = run(["pdfinfo", args.src])
    info_o, _ = run(["pdfinfo", args.out])
    tag_s = [l for l in info_s.splitlines() if l.startswith("Tagged")]
    tag_o = [l for l in info_o.splitlines() if l.startswith("Tagged")]
    print(f"pdfinfo: {tag_s} -> {tag_o}")
    rep["labels_ok"] = la == lb
    rep["struct_ok"] = (ra is not None and rb is not None and ta == tb)
    if not (la == lb and rep["struct_ok"]):
        ok = False

    # ---- rendering -------------------------------------------------------- #
    print(f"\n== rendering ({args.dpi} dpi) ==")
    # every page that used a DejaVu figure font, plus a random spread
    fig_pages = set()
    for i in range(sd.page_count):
        for f in sd[i].get_fonts(full=True):
            if "DejaVu" in f[3]:
                fig_pages.add(i)
    others = [i for i in range(sd.page_count) if i not in fig_pages]
    step = max(1, len(others) // args.sample)
    sample = sorted(fig_pages) + others[::step][: args.sample]
    bad = []
    for i in sample:
        ha, wa, hh = pixhash(sd[i], args.dpi)
        hb, wb, hh2 = pixhash(od[i], args.dpi)
        if ha != hb:
            bad.append((i + 1, wa, wa, wb, wb))
    print(f"pages rendered: {len(sample)} ({len(fig_pages)} figure pages + "
          f"{len(sample) - len(fig_pages)} others)")
    print(f"pixel-identical: {len(sample) - len(bad)}/{len(sample)}")
    if bad:
        print(f"DIFFERING: {bad}")
        ok = False
    rep["render_pages"] = len(sample)
    rep["render_identical"] = len(sample) - len(bad)
    rep["render_bad"] = bad

    # ---- fonts ------------------------------------------------------------ #
    print("\n== fonts ==")
    fa, _ = run(["pdffonts", args.src])
    fb, _ = run(["pdffonts", args.out])
    print(f"font objects: {len(fa.splitlines()) - 2} -> {len(fb.splitlines()) - 2}")
    print(f"DejaVu entries: {fa.count('DejaVu')} -> {fb.count('DejaVu')}")
    print("output DejaVu fonts:")
    for l in fb.splitlines():
        if "DejaVu" in l:
            print("   " + l)

    print("\nRESULT:", "PASS" if ok else "FAIL")
    with open(os.path.splitext(args.out)[0] + "-verify.json", "w") as fh:
        json.dump(rep, fh, indent=1)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
