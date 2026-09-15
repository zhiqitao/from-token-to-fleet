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
