#!/usr/bin/env python3
"""_inject_titlepage.py — replace pandoc's \maketitle with \input{titlepage.tex}%.

Usage: python3 render/_inject_titlepage.py render/build/book.tex
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()
if r"\maketitle" in s:
    s = s.replace(r"\maketitle", r"\input{titlepage.tex}%")
    open(path, "w", encoding="utf-8").write(s)
    print("injected: \maketitle -> \\input{titlepage.tex}")
else:
    print("WARN: no \\maketitle found in", path)
