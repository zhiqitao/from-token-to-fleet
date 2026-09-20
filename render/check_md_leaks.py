#!/usr/bin/env python3
"""
Detect markdown constructs that pandoc SILENTLY leaks into the rendered PDF.

A heading or emphasis marker that is not properly separated (no blank line
before a heading, a table row missing its trailing '|', an unbalanced '**')
is absorbed into the preceding paragraph/table by pandoc and then printed
LITERALLY -- e.g. "### (b) ..." or "** Threshold..." appearing as text in the
book. This is invisible to a build that just compiles cleanly; it is only
visible when you read the RENDERED PDF. This check fails loudly before the build.

Checks:
  1. A heading line (^#{1,6}) whose previous non-fence line is NOT blank
     (pandoc appends it to that line's paragraph -> leaks '###').
  2. A table data row missing its trailing '|' (pandoc continues the table
     into the next line -> leaks the next line's '###' or bold text).
  3. An unmatched opening or closing '**' emphasis marker on a line.
"""
import glob, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOBS = ["design/manuscript/chapter-*/chapter-*.md"]

def check_file(path):
    problems = []
    lines = open(path, encoding="utf-8").read().split("\n")
    in_code = False
    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        stripped = line.strip()
        # track code blocks so we don't false-positive on templates in fences
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        # 1. heading after non-blank non-fence line
        if re.match(r"^#{1,6}\s", stripped):
            prev = lines[i - 2].rstrip() if i >= 2 else ""
            prev_s = prev.strip()
            if prev_s and not prev_s.startswith(("```", ":::", "|")):
                # heading directly after plain text
                problems.append(f"  L{i}: heading '{stripped[:40]}' not preceded by blank line (pandoc will leak '#')")
        # 2. table row missing trailing '|' (line starts with | but doesn't end with |)
        if stripped.startswith("|") and not stripped.endswith("|"):
            # only if it's really a table row (contains at least 2 pipes)
            if stripped.count("|") >= 2:
                problems.append(f"  L{i}: table row missing trailing '|' -> '{stripped[:50]}'")
        # 3. unbalanced '**' on a line (count of '**' is odd) -- but not a standalone hr '***'
        if stripped in ("***", "---", "* * *", "___"):
            continue
        if stripped.count("**") % 2 == 1:
            problems.append(f"  L{i}: unbalanced '**' -> '{stripped[:60]}'")
    return problems

def main():
    allp = []
    for g in GLOBS:
        for f in sorted(glob.glob(os.path.join(REPO, g))):
            p = check_file(f)
            for x in p:
                allp.append(os.path.relpath(f, REPO) + x)
    if allp:
        print("MARKDOWN LEAK RISKS (will render literally in the PDF):")
        for p in allp:
            print("  " + p)
        sys.exit(1)
    print("no markdown leak risks detected")

if __name__ == "__main__":
    main()
