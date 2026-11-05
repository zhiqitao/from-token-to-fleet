#!/usr/bin/env bash
# Plain (non-tagged) book build.  Drops the PDF/UA structure tree so the
# output PDF is substantially smaller; NOT an accessibility build and NOT
# PDF/UA conformance evidence.  Keeps the same letter 8.5x11 book class,
# fonts and figures as build.sh, and opens on the premium-minimal cover.
#
# Usage:  bash render/build_plain.sh
# Output: render/build/from-token-to-fleet-v20260913-plain.pdf
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

echo "== check_tables / check_md_leaks / check_regressions / check_stale_values (fail loud) =="
python3 render/check_tables.py
python3 render/check_md_leaks.py
python3 render/check_regressions.py
python3 render/check_stale_values.py

echo "== md_to_latex =="
python3 render/latex/md_to_latex.py

echo "== emit_book (PLAIN mode) =="
BOOK_BUILD_MODE=plain python3 render/latex/emit_book.py

cd render/latex
rm -f book.aux book.out book.toc book.lof book.log book.pdf book.bbl
# inject the source revision (git SHA) into backmatter/sources.tex, restore after
GITSHA="$(git -C "$REPO" rev-parse HEAD)"
SOURCE_BACKUP="$(mktemp "${TMPDIR:?TMPDIR must point to scratch}/ftf-sources.XXXXXX.tex")"
cp backmatter/sources.tex "$SOURCE_BACKUP"
trap 'cp "$SOURCE_BACKUP" backmatter/sources.tex; rm -f "$SOURCE_BACKUP"' EXIT
python3 - "$GITSHA" <<'PY'
from pathlib import Path
import sys
p = Path('backmatter/sources.tex')
p.write_text(p.read_text().replace('@GITSHA@', sys.argv[1]))
PY
echo "== lualatex passes (plain, no tagging) =="
for i in 1 2 3; do
  lualatex -interaction=nonstopmode -halt-on-error book.tex >/dev/null 2>&1 || {
    echo "lualatex pass $i FAILED"; exit 1; }
done
cp "$SOURCE_BACKUP" backmatter/sources.tex
rm -f "$SOURCE_BACKUP"
trap - EXIT

echo "== fix_pdf_meta (page labels + linearize) =="
cd "$REPO"
python3 render/fix_pdf_meta.py render/latex/book.pdf \
        render/build/from-token-to-fleet-v20260913-plain.pdf

echo "== verify output =="
python3 - <<'PY'
import pymupdf
d = pymupdf.open("render/build/from-token-to-fleet-v20260913-plain.pdf")
cat = d.pdf_catalog()
print("pages:", len(d))
print("StructTreeRoot (expect None for plain):", d.xref_get_key(cat, "StructTreeRoot"))
print("MarkInfo (expect None for plain):", d.xref_get_key(cat, "MarkInfo"))
print("page labels:", d.get_page_labels())
PY
echo "PLAIN BUILD OK"
