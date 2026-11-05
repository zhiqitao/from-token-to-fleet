#!/usr/bin/env python3
"""Stale-value gate (review 2026-11-04 follow-up).

Every value below is a SUPERSEDED literal that a prior fix replaced. If any of
these appears as a LIVE value in the manuscript source, this script exits 1 and
fails the build. This converts classes of defect that were previously caught
only by a lucky self-review pass (a fix that landed in the main table/prose but
left a neighbor paragraph or a cross-chapter reference on the old value) into a
machine-enforced invariant.

Two exceptions are allowed and must be written as such:
- A literal that the text EXPLICITLY introduces as a superseded value
  (e.g. 'the 13.85 s figure quoted in earlier passes was a single-prefill
  approximation and is superseded') is an intentional mention, not a live use.
  We detect this by requiring a nearby 'superseded'/previously'/'earlier'
  marker, so a bare live use is still caught.

Run from repo root:  python3 render/check_stale_values.py
"""
import os
import re
import sys
import glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MSG = os.path.join(REPO, "design", "manuscript")
SUSPEND_IF_PRECEDED_BY = r"(superseded|previously|earlier|old|was quoted as|approximation)"

# (superseded literal, context description)
STALE = [
    (r"W\s*≈\s*13\.8\s*s\s+for\s+the\s+T=3", "agentic W(3) as the T=3 service time"),
    (r"13\.854\s*s", "single-prefill W(3) 13.854 s (superseded by 17.70/14.16)"),
    (r"1,?380\s*/(\s*13\s*×\s*0\.70\s*×\s*0\.95)", "old agentic in-flight 1380/(13*0.665)"),
    (r"⌈1[,]?380\s*/", "old agentic FP16 host count 1380/(13...)"),
    (r"≈\s*160\s*hosts", "old agentic FP16 100-rps host count 160"),
    (r"77\s*working\s+hosts", "old agentic FP8 100-rps host count 77 (non-agentic ch13 '77 working + 1 spare = 78' is a DIFFERENT correct value)"),
    (r"excluding\s+the\s+fallback['’]s\s+failed-attempt\s+work\s+gives\s+23,?601", "old excl-all-fallback 23,601 (should be 23,795 for failed-only)"),
    (r"\+\s*814", "old fallback exclusion delta +814 (correct is +620)"),
]


def scan_file(path):
    text = open(path, encoding="utf-8").read()
    hits = []
    for pat, desc in STALE:
        for m in re.finditer(pat, text):
            # intentional superseded-mention? look back for a marker
            back = text[max(0, m.start() - 60):m.start()]
            if re.search(SUSPEND_IF_PRECEDED_BY, back, re.I):
                continue
            hits.append((desc, pat, m.start()))
    return hits


def main():
    files = sorted(glob.glob(os.path.join(MSG, "**", "*.md"), recursive=True))
    bad = 0
    for f in files:
        for desc, pat, pos in scan_file(f):
            line_no = open(f, encoding="utf-8").read()[:pos].count("\n") + 1
            print(f"STALE [{desc}] in {os.path.relpath(f, REPO)}:{line_no} (pattern {pat})")
            bad += 1
    if bad:
        print(f"FAIL: {bad} stale-value use(s) found. Fix or mark as intentional-superseded.")
        sys.exit(1)
    print("OK - no stale superseded values found in live manuscript text.")


if __name__ == "__main__":
    main()
