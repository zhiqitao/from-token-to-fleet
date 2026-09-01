#!/bin/bash
# =============================================================================
# render/make_book.sh — build the FULL BOOK as a real PDF (dedicated title page,
# copyright page, preface, table of contents, full chapter text, remaining-chapter
# skeletons) via pandoc + tectonic.
#
# Pipeline: markdown sources (design/manuscript/chapter-NN/chapter-NN.md) +
# front matter -> pandoc (md -> LaTeX) -> tectonic (LaTeX -> PDF).
#
# Produces:
#   render/build/book.pdf    the whole book, real-book typography
#
# Toolchain: pandoc + tectonic located via render/setup_environment.sh. The
# generated PDF and LaTeX contain no absolute filesystem paths (paths are
# relative to the repo root); the artifact is portable.
#
# Usage:  bash render/make_book.sh
# =============================================================================
set -e
cd "$(cd "$(dirname "$0")/.." && pwd)"
REPO="$PWD"
OUT="$REPO/render/build"
mkdir -p "$OUT"

# ---- locate pandoc + tectonic (render/bin/.paths > render/bin/ > system) ----
P=""; T=""
if [ -f render/bin/.paths ]; then
  read -r P < render/bin/.paths 2>/dev/null || true
fi
[ -x "$P" ] || P="$REPO/render/bin/pandoc"
[ -x "$P" ] || P="$(command -v pandoc || true)"
T="$REPO/render/bin/tectonic"
[ -x "$T" ] || T="$(command -v tectonic || true)"
[ -x "$P" ] || { echo "ERROR: pandoc not found. Run render/setup_environment.sh first."; exit 1; }
[ -x "$T" ] || { echo "ERROR: tectonic not found. Run render/setup_environment.sh first."; exit 1; }
echo "pandoc: $P"; echo "tectonic: $T"

# ---- assemble the markdown book (front matter + ch1 + skeletons) into one file ----
BOOKMD="$OUT/_book.md"
python3 render/make_book_body.py > "$BOOKMD"
PYTHON="$(command -v python3)"

# ---- ASCII-safe substitutions (Latin Modern lacks some glyphs; skip ```math blocks) ----
LMD="$OUT/_book.latex.md"
cp "$BOOKMD" "$LMD"
$PYTHON render/md_ascii_subs.py < "$LMD" > "$LMD.tmp" && mv "$LMD.tmp" "$LMD"

BOOKT="From Token to Fleet: An AI Solution Architect's Handbook"
BOOKA="Zhiqi Tao"
BOOKD="2026-08-30"
PYTHON="$(command -v python3)"

# pandoc md -> LaTeX at REPO ROOT; --resource-path lets \\includegraphics resolve
# figures/... relative to each chapter dir.
# ---- all chapters as resource paths so pandoc resolves figures/... ----
RES=""
for c in $(seq -w 1 26); do RES+="design/manuscript/chapter-$c:"; done
RESOURCES="${RES%:}"
"$P" -s -f markdown-implicit_figures-yaml_metadata_block -t latex --resource-path="$RESOURCES" \
  --toc --toc-depth=1 \
  --metadata title="$BOOKT" --metadata author="$BOOKA" --metadata date="$BOOKD" \
  -o "$OUT/book.tex" "$LMD" 2>&1 | head -20 || true

# Replace pandoc's \\maketitle with the real-book title page
# (\\input{titlepage.tex}: tectonic resolves it via -Z search-path=render)
$PYTHON "$REPO/render/_inject_titlepage.py" "$OUT/book.tex"

# tectonic from REPO ROOT; titlepage lives in render/, figures/ lives in each
# chapter dir. -Z search-path points at both.
cd "$REPO"
SEARCH="-Z search-path=render"
for c in $(seq -w 1 26); do SEARCH+=" -Z search-path=design/manuscript/chapter-$c"; done
"$T" $SEARCH "$OUT/book.tex" 2>&1 | tail -12 || true

mv -f "$OUT/book.pdf" "$OUT/book.pdf" 2>/dev/null || true
rm -f book.tex book.xdv book.log book.out 2>/dev/null
echo "--- output ---"
ls -la "$OUT/book.pdf"
