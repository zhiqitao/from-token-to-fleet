#!/usr/bin/env python3
"""Run fix_pdf_meta + verify on the plain build (venv pymupdf)."""
import subprocess, sys, os

VENV = ("/home/ubuntu/.hermes/installs/5f0a1ff4045d044e/environments/"
        "02af1ccff96b479ca1900df1726f28a4/venv/bin/python3")
REPO = "/home/ubuntu/hermes-work/from-token-to-fleet"
SRC = "render/latex/book.pdf"
DST = "render/build/from-token-to-fleet-v20260913-plain.pdf"

r = subprocess.run([VENV, "render/fix_pdf_meta.py", SRC, DST],
                   cwd=REPO, capture_output=True, text=True)
print(r.stdout[-2000:], r.stderr[-2000:])
if r.returncode != 0:
    sys.exit("fix_pdf_meta failed rc=%d" % r.returncode)

import pymupdf
d = pymupdf.open(os.path.join(REPO, DST))
cat = d.pdf_catalog()
print("pages:", len(d))
print("StructTreeRoot (expect None for plain):", d.xref_get_key(cat, "StructTreeRoot"))
print("MarkInfo (expect None for plain):", d.xref_get_key(cat, "MarkInfo"))
print("page labels:", d.get_page_labels())
print("toc entries:", len(d.get_toc()))
print("PLAIN BUILD OK")