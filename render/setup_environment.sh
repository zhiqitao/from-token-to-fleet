#!/bin/bash
# setup_environment.sh — install/verify the toolchain needed to build the book PDF
# AND reproduce the 5.36 MB shrink pipeline (vector figures + font merge + objstm).
#
# Build chain actually used by render/build.sh:
#   pandoc (markdown -> LaTeX) + lualatex (LaTeX -> PDF, tagpdf structure tree)
# Verification/shrink tools:
#   pymupdf, fontTools, mutool, pdftotext, pdfinfo
#
# Strategy: use system binaries if present; otherwise download static binaries
# into ./render/bin (git-ignored). Idempotent. Linux/macOS/WSL; Windows needs WSL.
#
# Usage:  bash render/setup_environment.sh
set -e

PANDOC_VER="3.1.11.1"
TECTONIC_VER="0.17.0"   # legacy/HTML path; the PDF path uses system lualatex

REPO="$(cd "$(dirname "$0")/.." && pwd)"
BIN_DIR="$REPO/render/bin"
mkdir -p "$BIN_DIR"

say() { printf '\n[setup] %s\n' "$*"; }
ok() {  printf '  [ok]   %s\n' "$*"; }
note() { printf '  [note] %s\n' "$*"; }

# ---------------------------------------------------------------- python deps
install_python_deps() {
  say "python dependencies (render/requirements.txt)"
  local PY="${PYTHON:-python3}"
  if "$PY" -m pip --version >/dev/null 2>&1; then
    if "$PY" -m pip install -r "$REPO/render/requirements.txt"; then
      ok "pymupdf fontTools matplotlib Pillow PyYAML installed"
    else
      note "pip install failed — run manually: $PY -m pip install -r render/requirements.txt"
    fi
  else
    note "no pip on $PY — run manually: pip install -r render/requirements.txt"
  fi
}

# ---------------------------------------------------------------- pandoc
resolve_pandoc() {
  if command -v pandoc >/dev/null 2>&1; then
    echo "$(command -v pandoc)"; return 0
  fi
  if [ -x "$BIN_DIR/pandoc" ]; then
    echo "$BIN_DIR/pandoc"; return 0
  fi
  say "downloading pandoc ${PANDOC_VER} static binary..."
  curl -fL -o "$BIN_DIR/pandoc.tar.gz" \
    "https://github.com/jgm/pandoc/releases/download/${PANDOC_VER}/pandoc-${PANDOC_VER}-linux-amd64.tar.gz"
  tar xzf "$BIN_DIR/pandoc.tar.gz" -C "$BIN_DIR"
  mv "$BIN_DIR/pandoc-${PANDOC_VER}/bin/pandoc" "$BIN_DIR/pandoc"
  rm -rf "$BIN_DIR/pandoc-${PANDOC_VER}" "$BIN_DIR/pandoc.tar.gz"
  echo "$BIN_DIR/pandoc"
}

# ---------------------------------------------------------------- lualatex (the real PDF engine)
check_lualatex() {
  if command -v lualatex >/dev/null 2>&1; then
    ok "lualatex: $(command -v lualatex)"
    return 0
  fi
  note "lualatex NOT FOUND — render/build.sh needs it (tagpdf structure tree)."
  note "  Debian/Ubuntu: sudo apt-get install -y texlive-luatex texlive-latex-extra texlive-fonts-recommended"
  note "  (xelatex/tectonic cannot emit the structure tree — do NOT substitute.)"
  return 1
}

# ---------------------------------------------------------------- verification tools
check_tools() {
  say "verification / shrink tools"
  local t
  for t in mutool pdftotext pdfinfo fc-match pyftsubset; do
    if command -v "$t" >/dev/null 2>&1; then ok "$t"; else note "$t NOT FOUND (mupdf-tools / poppler-utils / fonttools)"; fi
  done
}

# ---------------------------------------------------------------- fonts (fontspec)
check_fonts() {
  say "fonts required by fontspec (render/latex/book.sty), via luaotfload (what lualatex resolves)"
  local f resolved missing=0
  # luaotfload-tool is the resolver lualatex actually uses; fc-match CANNOT see
  # TeX Live fonts (they are outside fontconfig's path) and falsely reports a
  # fallback, so we must use luaotfload-tool, not fc-match.
  if ! command -v luaotfload-tool >/dev/null 2>&1; then
    note "luaotfload-tool not found — install TeX Live (texlive-luatex) to resolve fonts."
    return 1
  fi
  for f in "Linux Libertine O" "Source Code Pro" "EB Garamond" "Noto Serif" "Liberation Sans" "Latin Modern Mono" "Liberation Mono"; do
    resolved="$(luaotfload-tool --find="$f" 2>/dev/null | grep 'Resolved file name' | head -1 | sed 's/.*Resolved file name \"//; s/\"$//')"
    if [ -n "$resolved" ]; then
      printf '  [ok]   %-20s -> %s\n' "$f" "$(basename "$resolved")"
    else
      printf '  [MISS] %-20s -> not found (lualatex will fall back)\n' "$f"
      missing=$((missing+1))
    fi
  done
  if [ "$missing" -gt 0 ]; then
    note "$missing font(s) missing — install TeX Live fonts (texlive-fonts-extra / fonts-linuxlibertine / fonts-noto / fonts-liberation)."
  else
    note "all fontspec fonts resolve via luaotfload."
  fi
}

# ---------------------------------------------------------------- legacy tectonic (HTML/legacy path only)
resolve_tectonic() {
  if command -v tectonic >/dev/null 2>&1; then
    echo "$(command -v tectonic)"; return 0
  fi
  if [ -x "$BIN_DIR/tectonic" ]; then
    echo "$BIN_DIR/tectonic"; return 0
  fi
  say "downloading tectonic ${TECTONIC_VER} (legacy; PDF path uses lualatex)..."
  curl -fL -o "$BIN_DIR/tectonic.tar.gz" \
    "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40${TECTONIC_VER}/tectonic-${TECTONIC_VER}-x86_64-unknown-linux-gnu.tar.gz"
  tar xzf "$BIN_DIR/tectonic.tar.gz" -C "$BIN_DIR"
  chmod +x "$BIN_DIR/tectonic"
  rm -f "$BIN_DIR/tectonic.tar.gz"
  echo "$BIN_DIR/tectonic"
}

# ---------------------------------------------------------------- run
install_python_deps
PANDOC="$(resolve_pandoc)";   ok "pandoc: $("$PANDOC" --version | head -1)"
TECTONIC="$(resolve_tectonic)"; ok "tectonic: $TECTONIC (legacy/HTML)"
check_lualatex
check_tools
check_fonts
printf '%s\n%s\n' "$PANDOC" "$TECTONIC" > "$BIN_DIR/.paths"

say "DONE. Reproduce the 5.36 MB build:"
say "  1) bash render/build.sh                                             # -> ~10.3 MB tagged PDF (vector figures)"
say "  2) python3 render/merge_fig_fonts.py --src <10.3MB> --out <9.2MB>   # -> ~9.2 MB (DejaVu subset merge)"
say "  3) python3 render/merge_fig_fonts.py --src <9.2MB> --out <5.4MB> --objstm  # -> ~5.4 MB (object-stream)"
say "  verify each step: python3 render/verify_merge.py <src> <out>"
