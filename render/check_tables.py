#!/usr/bin/env python3
"""Validate every markdown table in the manuscript for column-count consistency.

A pipe table must have the SAME number of cells (pipes+1) in the header row,
the separator row, and every data row. A mismatch makes pandoc silently drop
the table and render it as literal '|---|---|...' text -- a defect that is
invisible to a build that merely compiles cleanly.

This check runs before the LaTeX build so such a defect fails loudly instead
of shipping as a wall of pipe characters.
"""
import glob, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOBS = ["design/manuscript/chapter-*/chapter-*.md"]

def pipes(line):
    return line.strip().count("|")

def is_separator(line):
    s = line.strip().strip("|")
    s = s.replace(" ", "").replace(":", "")
    return s != "" and set(s) <= set("-")

def check_file(path):
    bad = []
    lines = open(path, encoding="utf-8").read().split("\n")
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("|"):
            block = []
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                block.append(lines[j].strip()); j += 1
            if len(block) >= 2 and is_separator(block[1]):
                header_n = pipes(block[0])
                sep_n = pipes(block[1])
                if sep_n != header_n:
                    bad.append((i + 1, "separator", header_n, sep_n, block[0][:60]))
                for k, row in enumerate(block[2:], start=3):
                    if pipes(row) != header_n:
                        bad.append((i + k, "row", header_n, pipes(row), row[:60]))
            i = j
        else:
            i += 1
    return bad

def main():
    problems = []
    for g in GLOBS:
        for f in sorted(glob.glob(os.path.join(REPO, g))):
            for (ln, kind, exp, got, preview) in check_file(f):
                rel = os.path.relpath(f, REPO)
                problems.append(f"{rel}:{ln}: {kind} has {got} cells but header has {exp} -> {preview}")
    if problems:
        print("TABLE COLUMN MISMATCH (pandoc will render these as literal pipes):")
        for p in problems:
            print("  " + p)
        sys.exit(1)
    print("all markdown tables: column counts consistent")

if __name__ == "__main__":
    main()
