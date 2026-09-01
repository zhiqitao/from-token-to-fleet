#!/bin/bash
cd "$(cd "$(dirname "$0")/.." && pwd)"
set -e
OUT=render/build
mkdir -p $OUT

# --- locate pandoc + tectonic (system > render/bin from setup_environment.sh > legacy /tmp) ---
BIN_DIR=render/bin
if [ -f "$BIN_DIR/.paths" ]; then
  P=$(sed -n '1p' "$BIN_DIR/.paths")
  T=$(sed -n '2p' "$BIN_DIR/.paths")
else
  P=$(command -v pandoc || echo /tmp/pandoc-3.1.11.1/bin/pandoc)
  T=$(command -v tectonic || echo /tmp/tectonic)
fi
echo "pandoc: $P"
echo "tectonic: $T"
[ -x "$P" ] || { echo "ERROR: pandoc not found. Run render/setup_environment.sh first."; exit 1; }
[ -x "$T" ] || { echo "ERROR: tectonic not found. Run render/setup_environment.sh first."; exit 1; }

CHAPTERS=(
  chapter-01-first-principles-cost.md
  chapter-02-architecture-cost.md
  chapter-03-training-flop.md
  chapter-04-posttrain-memory.md
  chapter-05-quant-residency.md
  chapter-06-serving-bandwidth.md
  chapter-07-agent-loophorizon.md
  chapter-08-fleet-synthesis.md
)

> $OUT/book.md
# Frontmatter (How to Use / learning path) first, unprocessed (no fig/table numbering)
if [ -f "frontmatter-how-to-use.md" ]; then
  cat frontmatter-how-to-use.md >> $OUT/book.md
  echo >> $OUT/book.md
  echo "\\clearpage" >> $OUT/book.md
fi
ch_i=0
for f in "${CHAPTERS[@]}"; do
  if [ -f "$f" ]; then
    ch_i=$((ch_i+1))
    echo "\\clearpage" >> $OUT/book.md
    python3 render/preprocess_md.py "$ch_i" "$f" >> $OUT/book.md
    echo >> $OUT/book.md
  fi
done

# pandoc -> latex at REPO ROOT (so \includegraphics{diagrams/...} resolves from cwd=repo root)
# LaTeX/Latin Modern lacks CJK & some math glyphs; ASCII-safe substitutions before pandoc.
#   U+2248 ≈ -> $\\approx$
#   U+2212 − -> -
#   U+2260 ≠ -> $\\neq$
#   U+00D7 × -> $\\times$
cp "$OUT/book.md" "$OUT/book.latex.md"
sed -i -e 's/≈/$\\approx$/g' \
       -e 's/≠/$\\neq$/g' \
       -e 's/×/$\\times$/g' \
       -e 's/−/-/g' \
       -e 's/…/.../g' "$OUT/book.latex.md"
BOOKT="From Token to Fleet: An AI Solution Architect's Handbook"
BOOKA="Zhiqi Tao"
BOOKD="2026-08-29"
$P -s -f markdown -t latex --metadata title="$BOOKT" --metadata author="$BOOKA" --metadata date="$BOOKD" -o book.tex $OUT/book.latex.md 2>&1 | head -20 || true
# Replace the plain \maketitle with the real-book title page (render/titlepage.tex).
# Keeps \title/\author/\date metadata for PDF info, but drops the auto title block.
sed -i 's/\\maketitle/\\input{render\/titlepage.tex}%/' book.tex
# tectonic from repo root, input book.tex at repo root
$T book.tex 2>&1 | tail -8 || true
# move outputs
mv -f book.pdf $OUT/book.pdf 2>/dev/null || true
mv -f book.epub $OUT/book.epub 2>/dev/null || true
 echo "--- epub ---"
$P -s -f markdown -t epub3 --metadata title="$BOOKT" --metadata author="$BOOKA" --metadata date="$BOOKD" -o $OUT/book.epub $OUT/book.md 2>&1 | tail -3 || true
rm -f book.tex book.xdv book.log book.out 2>/dev/null
ls -la $OUT/book.pdf $OUT/book.epub 2>/dev/null
