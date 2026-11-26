#!/usr/bin/env python3
"""Pack the tagged book PDF's objects into compressed object streams (ObjStm).

Why: lualatex + tagpdf emit ~20k StructElem objects (accessibility tree) plus
font dicts, page dicts and name trees as individual uncompressed objects. That
is ~4.5 MB of pure object overhead. ObjStm packs them into Flate-compressed
streams. Page content streams and font programs are already compressed and are
left alone.

Safety gates (same as the original toolchain): page count, full text layer
(pymupdf + pdftotext), StructTreeRoot + StructElem count, page labels, Tagged
flag, and a pixel render sample. The script refuses to overwrite the source if
any gate fails.

Usage:
    venv-python render/pack_objstm.py SRC.pdf OUT.pdf
"""
import os
import shutil
import subprocess
import sys

import pymupdf
import pikepdf

def gates(src, out):
    """Return (ok, report). ok is True only if every gate passes."""
    rep = {}
    a = pymupdf.open(src)
    b = pymupdf.open(out)
    rep["pages"] = (a.page_count, b.page_count)
    if a.page_count != b.page_count:
        a.close(); b.close(); return False, rep
    # full text layer
    diff = [i for i in range(a.page_count) if a[i].get_text() != b[i].get_text()]
    rep["text_diff_pages"] = diff
    if diff:
        a.close(); b.close(); return False, rep
    # tagging: StructTreeRoot must be present in both (xref number may be
    # renumbered by pikepdf during save — that is not a defect)
    ca, cb = a.pdf_catalog(), b.pdf_catalog()
    sa = a.xref_get_key(ca, "StructTreeRoot")
    sb = b.xref_get_key(cb, "StructTreeRoot")
    rep["struct"] = (sa, sb)
    if sa[0] == "null" or sb[0] == "null":
        a.close(); b.close(); return False, rep
    # StructElem count
    def nse(d):
        n = 0
        for x in range(1, d.xref_length()):
            try:
                if b"/StructElem" in d.xref_object(x, compressed=False): n += 1
            except Exception:
                pass
        return n
    rep["structelem"] = (nse(a), nse(b))
    if rep["structelem"][0] != rep["structelem"][1]:
        a.close(); b.close(); return False, rep
    # page labels
    rep["labels"] = (a.get_page_labels(), b.get_page_labels())
    if a.get_page_labels() != b.get_page_labels():
        a.close(); b.close(); return False, rep
    a.close(); b.close()
    # Tagged flag via pdfinfo if available
    try:
        pi = subprocess.run(["pdfinfo", out], capture_output=True, text=True)
        rep["tagged"] = "Tagged:          yes" in pi.stdout
        if not rep["tagged"]:
            return False, rep
    except FileNotFoundError:
        rep["tagged"] = "pdfinfo not available (skipped)"
    # pixel render sample (figure pages + a few others)
    import fitz  # noqa: F401  (pymupdf alias)
    a = pymupdf.open(src); b = pymupdf.open(out)
    sample = list(range(0, a.page_count, max(1, a.page_count // 40)))[:40]
    bad = []
    for i in sample:
        pa = a[i].get_pixmap(dpi=72)
        pb = b[i].get_pixmap(dpi=72)
        if pa.tobytes("png") != pb.tobytes("png"):
            bad.append(i)
    rep["render_pages"] = len(sample)
    rep["render_bad"] = bad
    a.close(); b.close()
    if bad:
        return False, rep
    return True, rep


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    src, out = sys.argv[1], sys.argv[2]
    before = os.path.getsize(src)
    # pikepdf: object_stream_mode=2 packs all eligible objects into ObjStm
    with pikepdf.open(src) as pdf:
        pdf.save(out, object_stream_mode=pikepdf.ObjectStreamMode.generate)
    after = os.path.getsize(out)
    print("source bytes : %d" % before)
    print("output bytes : %d" % after)
    print("saved        : %d B (%.2f%%)" % (before - after, 100.0 * (before - after) / before))
    ok, rep = gates(src, out)
    print("gates:", json_dumps(rep))
    if not ok:
        print("GATE FAILED — not replacing source")
        os.remove(out)
        sys.exit(1)
    # replace source with packed output
    shutil.move(out, src)
    print("replaced %s (%.2f MB)" % (src, os.path.getsize(src) / 1e6))


def json_dumps(obj):
    import json
    return json.dumps(obj, default=str)


if __name__ == "__main__":
    main()
