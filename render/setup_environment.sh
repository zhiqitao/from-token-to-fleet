#!/bin/bash
# setup_environment.sh — install/verify the toolchain needed to build the book PDF.
#
# Build chain: pandoc (markdown -> LaTeX) + tectonic (LaTeX -> PDF).
# Strategy: use system binaries if present; otherwise download static binaries
# into ./render/bin (git-ignored). Keeps the repo self-contained/reproducible
# on Linux (macOS/WSL work too; Windows needs WSL or manual install).
#
# Usage:  bash render/setup_environment.sh
set -e

PANDOC_VER="3.1.11.1"
TECTONIC_VER="0.17.0"

BIN_DIR="$(cd "$(dirname "$0")/.." && pwd)/render/bin"
mkdir -p "$BIN_DIR"

say(){ printf '\n[setup] %s\n' "$*"; }

# Helpers: try system, else cached binary, else download.
resolve_pandoc(){
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

resolve_tectonic(){
  if command -v tectonic >/dev/null 2>&1; then
    echo "$(command -v tectonic)"; return 0
  fi
  if [ -x "$BIN_DIR/tectonic" ]; then
    echo "$BIN_DIR/tectonic"; return 0
  fi
  say "downloading tectonic ${TECTONIC_VER} static binary..."
  curl -fL -o "$BIN_DIR/tectonic.tar.gz" \
    "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40${TECTONIC_VER}/tectonic-${TECTONIC_VER}-x86_64-unknown-linux-gnu.tar.gz"
  tar xzf "$BIN_DIR/tectonic.tar.gz" -C "$BIN_DIR"
  chmod +x "$BIN_DIR/tectonic"
  rm -f "$BIN_DIR/tectonic.tar.gz"
  echo "$BIN_DIR/tectonic"
}

PANDOC="$(resolve_pandoc)"
TECTONIC="$(resolve_tectonic)"

say "PANDOC=$PANDOC  (check: $("$PANDOC" --version | head -1))"
say "TECTONIC=$TECTONIC"
printf '%s\n%s\n' "$PANDOC" "$TECTONIC" > "$BIN_DIR/.paths"
say "DONE. Run: bash render/make_render.sh"