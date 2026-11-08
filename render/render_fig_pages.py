#!/usr/bin/env python3
"""Render figure pages of the built PDF to PNGs for the vision review pass.
Run with the venv python that has fitz/pymupdf:
  <venv>/bin/python3 render/render_fig_pages.py <outdir>
Pages: union of 'Fig N.M' caption pages and raster-image pages.
"""
import os
import re
import sys
import json

import fitz  # pymupdf

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(REPO, "render/build/from-token-to-fleet-v20260913-plain.pdf")
RASTER = [91, 142, 157, 202, 327]


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        REPO, "review/loop_v3/pages")
    os.makedirs(outdir, exist_ok=True)
    pdf = fitz.open(PDF)
    pages = set(RASTER)
    for pno in range(pdf.page_count):
        if re.search(r"Fig \d+\.\d+", pdf[pno].get_text()):
            pages.add(pno + 1)
    pages = sorted(pages)
    manifest = []
    for p in pages:
        out = os.path.join(outdir, "page_%03d.png" % p)
        if not os.path.exists(out):
            pix = pdf[p - 1].get_pixmap(dpi=150)
            pix.save(out)
        manifest.append({"page": p, "file": os.path.basename(out)})
    json.dump(manifest, open(os.path.join(outdir, "manifest.json"), "w"),
              indent=1)
    print("rendered %d pages -> %s" % (len(pages), outdir))


if __name__ == "__main__":
    main()