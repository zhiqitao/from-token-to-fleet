#!/usr/bin/env python3
"""
make_book_body.py — emit the full-book markdown body (front matter + Ch.1 full
text + Ch.2-26 skeletons) to stdout, for render/make_book.sh to pipe into pandoc.

Sections in order:
  - Preface (distilled from design/book-architecture.md)
  - Table of Contents (all 26 chapters, per part)
  - Part I / Chapter 1 full text (design/manuscript/chapter-01/chapter-01.md)
  - Parts II-VI skeletons (one-line theses from book-architecture.md §9)

It renders markdown only (no base64, no absolute paths) so the output compiles
cleanly with pandoc + tectonic into a portable PDF.
"""

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESIGN = os.path.join(REPO, "design")
MANUSCRIPT = os.path.join(DESIGN, "manuscript")
ARCH = os.path.join(DESIGN, "book-architecture.md")
YAML = os.path.join(DESIGN, "book.yaml")


def read(p):
    return open(p, encoding="utf-8").read()


def load_chapters():
    text = read(YAML)
    book_title = re.search(r'title: "(.+?)"', text).group(1)
    parts = []
    cur = None
    for line in text.splitlines():
        m = re.match(r"\s+- id: (\w+)", line)
        if m:
            cur = {"id": m.group(1), "chapters": []}
            parts.append(cur)
            continue
        m = re.match(r"\s+title: \"(.+?)\"", line)
        if m and cur is not None and "title" not in cur:
            cur["title"] = m.group(1)
            continue
        m = re.match(r"\s+- \{n: (\d+), title: \"(.+?)\", status: \"(\w+)\"\}", line)
        if m and cur is not None:
            cur["chapters"].append((int(m.group(1)), m.group(2), m.group(3)))
    return book_title, parts


def load_skeleton():
    arch = read(ARCH)
    m = re.search(r"## 9\. Revised chapter skeleton(.*?)(?=\n## 10\.|\Z)", arch, re.S)
    out = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        mm = re.match(r"- \*\*Ch (\d+) · (.+?)\*\*[— ]+(.*)$", line.strip())
        if mm:
            out[int(mm.group(1))] = mm.group(3).strip()
    return out


def load_preface():
    arch = read(ARCH)
    paras = []
    m = re.search(
        r"A learning resource.*?rather than a specialist of any single layer\.", arch, re.S
    )
    if m:
        paras.append(m.group(0).strip())
    m = re.search(r"## 2\. The spine.*?\n> (.+?)\n", arch, re.S)
    if m:
        paras.append(
            "The book has one thesis, and it is the spine of every chapter: \""
            + m.group(1).strip() + "\""
        )
    m = re.search(r"\*\*Reading paths\.\*\*(.*?)(?=\n\n|\Z)", arch, re.S)
    if m:
        paras.append("How to read it: " + m.group(1).strip())
    return paras


SKELETON_NOTE = (
    "Each planned chapter appears below as its one-line thesis from the "
    "architecture document. Drafted chapters will replace these blocks as they land."
)


def build():
    book_title, parts = load_chapters()
    skeleton = load_skeleton()
    preface = load_preface()

    L = []
    # ---- Preface ----
    L.append("# Preface")
    L.append("")
    for p in preface:
        L.append(p)
        L.append("")

    # ---- Table of contents (as a set of parts + chapters) ----
    L.append("# Table of Contents")
    L.append("")
    for p in parts:
        L.append("## Part %s — %s" % (p["id"], p["title"]))
        L.append("")
        for n, t, s in p["chapters"]:
            tag = "/" if n == 1 else " (skeleton)"
            L.append("- **Ch %d.** %s%s" % (n, t, tag))
        L.append("")

    # ---- All 26 chapters full text ----
    for p in parts:
        for n, t, s in p["chapters"]:
            chp = os.path.join(MANUSCRIPT, "chapter-%02d" % n, "chapter-%02d.md" % n)
            if not os.path.exists(chp):
                L.append("## Ch %d. %s" % (n, t))
                L.append("")
                L.append("*(thesis not yet drafted — see architecture §9)*")
                L.append("")
                continue
            body = read(chp)
            body = re.sub(r"^# Chapter \d+.*?\n", "# Chapter %d\n" % n, body, count=1, flags=re.S)
            L.append(body.rstrip())
            L.append("")

    sys.stdout.write("\n".join(L))


if __name__ == "__main__":
    build()
