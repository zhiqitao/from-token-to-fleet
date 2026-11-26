#!/usr/bin/env bash
# Canonical tagged book build. Tagging is not PDF/UA conformance evidence.
#
# Uses lualatex (not xelatex): lualatex fully supports the tagpdf package, which
# produces a structure tree and figure alt text; conformance needs separate validation.
# xelatex cannot emit the structure tree.
#
# Usage:  bash render/build.sh
# Output: render/build/from-token-to-fleet-v20260913.pdf (tagged proof)
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

# Ensure pymupdf (and other user-site packages) are importable no matter which
# python3 lands on PATH (base Hermes vs an activated venv with user-site disabled).
# Idempotent: adds the user site-packages dir only if it is not already in PYTHONPATH.
_PYUSERSITE="${HOME}/.local/lib/python3.14/site-packages"
if [ -d "$_PYUSERSITE" ]; then
	case ":${PYTHONPATH:-}:" in
		*":$_PYUSERSITE:"*) ;;
		*) export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$_PYUSERSITE" ;;
	esac
fi

echo "== check_tables (fail loud on column-count mismatch) =="
python3 render/check_tables.py
echo "== check_md_leaks (fail loud on markdown leaking into PDF) =="
python3 render/check_md_leaks.py
echo "== check_regressions (fail loud on canonical numeric drift) =="
python3 render/check_regressions.py

echo "== md_to_latex =="
python3 render/latex/md_to_latex.py
echo "== emit_book =="
python3 render/latex/emit_book.py

cd render/latex
rm -f book.aux book.out book.toc book.lof book.log book.pdf book.bbl
echo "== inject source revision (git SHA) =="
GITSHA="$(git -C "$REPO" rev-parse HEAD)"
# The @GITSHA@ placeholder lives in backmatter/sources.tex (an \input file),
# NOT in book.tex, so substitute there and restore afterward to keep the repo clean.
SOURCE_BACKUP="$(mktemp "${TMPDIR:?TMPDIR must point to scratch}/ftf-sources.XXXXXX.tex")"
cp backmatter/sources.tex "$SOURCE_BACKUP"
trap 'cp "$SOURCE_BACKUP" backmatter/sources.tex; rm -f "$SOURCE_BACKUP"' EXIT
python3 - "$GITSHA" <<'PY'
from pathlib import Path
import sys
p = Path('backmatter/sources.tex')
p.write_text(p.read_text().replace('@GITSHA@', sys.argv[1]))
PY
echo "== lualatex passes =="
for i in 1 2 3; do
  lualatex -interaction=nonstopmode -halt-on-error book.tex >/dev/null 2>&1 || {
    echo "lualatex pass $i FAILED"; exit 1; }
done
cp "$SOURCE_BACKUP" backmatter/sources.tex
rm -f "$SOURCE_BACKUP"
trap - EXIT
echo "== fix_fig_struct (drop orphan cover-Figure shells, descriptive figure alt) =="
cd "$REPO"
python3 render/fix_fig_struct.py render/latex/book.pdf render/latex/book.fig.pdf

echo "== fix_pdf_meta (page labels + linearize) =="
cd "$REPO"
python3 render/fix_pdf_meta.py render/latex/book.fig.pdf \
        render/build/from-token-to-fleet-v20260913.pdf

echo "== pack_objstm (object-stream compression: ~42% smaller, gates must pass) =="
cd "$REPO"
# pikepdf lives only in the Hermes venv; fall back to it if base python3 lacks it.
_VENV_PY="$HOME/.hermes/hermes-agent/venv/bin/python3"
if "$VENV_PY" -c "import pikepdf" >/dev/null 2>&1; then
    _PACKPY="$_VENV_PY"
else
    _PACKPY="python3"
fi
"$_PACKPY" render/pack_objstm.py render/build/from-token-to-fleet-v20260913.pdf \
        render/build/from-token-to-fleet-v20260913.packtmp.pdf

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
print("size: %.2f MB" % (__import__("os").path.getsize("render/build/from-token-to-fleet-v20260913.pdf")/1e6))
print("tagged (StructTreeRoot):", d.xref_get_key(cat, "StructTreeRoot"))
print("MarkInfo:", d.xref_get_key(cat, "MarkInfo"))
print("Type3 fonts:", len(t3))
print("page labels:", d.get_page_labels())
PY
echo "BUILD OK"
