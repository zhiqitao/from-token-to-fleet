#!/usr/bin/env python3
"""Assemble the reflowable EPUB/Kindle edition of "From Token to Fleet".

Front matter (title, copyright/license, preface) + all 27 chapters in order,
then pandoc -> epub3.  Uses the rasterized cover PNG and resolves figures by
resource-path.

Usage:
    python3 render/cover/build_epub_letter.py
"""
import os, glob, subprocess, re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAN = os.path.join(REPO, "design", "manuscript")
OUTDIR = os.path.join(REPO, "render", "build")

TITLE = "From Token to Fleet: An AI Solution Architect's Handbook"
AUTHOR = "Zhiqi Tao"
VERSION = "v20260913"

# ---- front matter (plain markdown, no LaTeX newpage markers) ----
FRONT = f"""# From Token to Fleet

## {TITLE}

**Zhiqi Tao · {VERSION}**

---

## Copyright

**Copyright © 2026 Zhiqi Tao. All rights reserved.**

**License.** This work — the book text, diagrams, figures, and build scripts — is
distributed under a *source-available* license:

- **You may** freely read, study, learn from, and **redistribute** the work
  (verbatim, with attribution) for personal and non-commercial purposes.
- **You may NOT** claim authorship, remove attribution, or sell the work as-is.
- The license covers the text and assets; the underlying *methods* described are
  general engineering practice.

## Preface

First and foremost a learning tool I wrote for myself — if it helps you too,
that is a bonus. This book traces how to reason about, build, and operate
production AI systems: from the economics of a single token, through
parallelism, memory, batching and serving, up to fleet-level architecture and a
red-team / green-team discipline for honest evaluation.

---

"""

# ---- assemble chapters ----
chapters = sorted(glob.glob(os.path.join(MAN, "chapter-*", "chapter-*.md")))
parts = subprocess.run(["python3", "-c",
    "import yaml;d=yaml.safe_load(open('%s'));print('ok')" % os.path.join(REPO, "design", "book.yaml")],
    capture_output=True, text=True)
md_parts = []
for ch in chapters:
    md = open(ch, encoding="utf-8").read()
    md_parts.append(md)

assembled = FRONT + "\n\n---\n\n".join(md_parts)
assem_md = os.path.join(OUTDIR, "_book_reflowable.md")
open(assem_md, "w", encoding="utf-8").write(assembled)

print("assembled %d chapters -> %s (%d chars)" % (len(chapters), assem_md, len(assembled)))

# ---- render the approved cover to a raster for the EPUB ---- 
import base64
cover_svg = os.path.join(REPO, "render", "cover", "cover_clean_front.svg")
cover_png = os.path.join(REPO, "render", "cover", "cover_clean_front.png")
if not os.path.exists(cover_png) or os.path.getmtime(cover_svg) > os.path.getmtime(cover_png):
    subprocess.run(["inkscape", cover_svg, "-o", cover_png, "-w", "850", "-h", "1100"],
                   check=False, capture_output=True)

# ---- resolve figure paths to repo-root-relative (pandoc resource-path) ----
# Rewrite 'figures/fig-N*.png' refs to 'design/manuscript/chapter-NN/figures/...'
content = open(assem_md, encoding="utf-8").read()
def fix_fig(m):
    return "(" + os.path.join("design", "manuscript", m.group(1), "figures", m.group(2)) + ")"
content = re.sub(r'\(figures/(chapter-?\d+)/figures/(fig-[^)]+\.png)\)', fix_fig, content)
content = re.sub(r'\(figures/(fig-[^)]+\.png)\)', lambda m: 
    os.path.join("design", "manuscript", "appendix", "figures", m.group(1)), content)
assem_md2 = os.path.join(OUTDIR, "_book_reflowable.md")
open(assem_md2, "w", encoding="utf-8").write(content)

out_epub = os.path.join(OUTDIR, "from-token-to-fleet-" + VERSION + ".epub")
_p = subprocess.run(["pandoc", assem_md2,
                "-f", "markdown-yaml_metadata_block",
                "-o", out_epub, "--to=epub3", "--toc", "--toc-depth=2",
                "--mathml",
                "--epub-cover-image=" + cover_png,
                "--metadata", "title=" + TITLE,
                "--metadata", "author=" + AUTHOR,
                "--metadata", "lang=en",
                "--resource-path=" + REPO], check=False, capture_output=True)
if _p.returncode != 0:
    raise SystemExit("EPUB build FAILED (pandoc rc=%s):\n%s" % (_p.returncode, _p.stderr.decode("utf-8", "ignore")))
if not os.path.exists(out_epub):
    raise SystemExit("EPUB build FAILED: no output file %s" % out_epub)
print("epub written: %s" % out_epub)

