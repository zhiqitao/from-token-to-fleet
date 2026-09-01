#!/usr/bin/env python3
# SUPERSEDED 2026-08-31: Fig 1.1 (KV cache) is now an Archify diagram, not a
# hand-drawn SVG. Source of truth:
#   render/archify/fig-1-1-kv-cache.json  ->  -deliver.html / -min.html
#   design/manuscript/chapter-01/figures/fig-01-kv-cache.{pdf,png}
# Do NOT regenerate the old Comic-Sans/cream hand-drawn style (it no longer
# matches the book's archify/matplotlib figure language). Rebuild the Archify
# asset instead: `node /tmp/archify/archify/bin/archify.mjs deliver architecture
# render/archify/fig-1-1-kv-cache.json ...` then re-export PDF+PNG via chromium.
print("fig-01-kv-cache: SUPERSEDED by Archify (render/archify/fig-1-1-kv-cache.json); skipped.")
