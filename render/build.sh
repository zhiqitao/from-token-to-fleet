#!/usr/bin/env bash
# Canonical book build (TAGGED / PDF-UA accessible).
#
# Uses lualatex (not xelatex): lualatex fully supports the tagpdf package, which
# produces a tagged (PDF/UA) document with a structure tree and figure alt text.
# xelatex cannot emit the structure tree.
#
# Usage:  bash render/build.sh
# Output: render/build/from-token-to-fleet-v20260913.pdf  (tagged, accessible)
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

echo "== md_to_latex =="
python3 render/latex/md_to_latex.py
echo "== emit_book =="
python3 render/latex/emit_book.py

cd render/latex
rm -f book.aux book.out book.toc book.lof book.log book.pdf book.bbl
echo "== lualatex passes =="
for i in 1 2 3; do
  lualatex -interaction=nonstopmode -halt-on-error book.tex >/dev/null 2>&1 || {
    echo "lualatex pass $i FAILED"; exit 1; }
done
echo "== fix_pdf_meta (page labels + linearize) =="
cd "$REPO"
python3 render/fix_pdf_meta.py render/latex/book.pdf \
        render/build/from-token-to-fleet-v20260913.pdf

echo "== verify =="
python3 - <<'PY'
import pymupdf
d = pymupdf.open("render/build/from-token-to-fleet-v20260913.pdf")
cat = d.pdf_catalog()
t3 = set()
for p in range(len(d)):
    for f in d[p].get_fonts():
        if f[2] == "Type3": t3.add(f[3])
print("pages:", len(d))
print("tagged (StructTreeRoot):", d.xref_get_key(cat, "StructTreeRoot"))
print("MarkInfo:", d.xref_get_key(cat, "MarkInfo"))
print("Type3 fonts:", len(t3))
print("page labels:", d.get_page_labels())
PY
echo "BUILD OK"
