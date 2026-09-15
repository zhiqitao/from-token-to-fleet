#!/usr/bin/env python3
"""Generate a light-theme minimal HTML ('<name>-min.html') from an Archify
'deliver' HTML for diagrams that only have a deliver.html (no -min.html yet).

The Archify SVGs share the same class/CSS vocabulary, so we reuse the CSS
shell of an existing, known-good -min.html (ch5-two-leg) and swap in the new
inline <svg>.  The crop pipeline (crop_archify_viewbox.py) needs a -min.html
with 'viewBox="0 0 W H"' and a light theme / white body for print.

Usage:
    python3 render/gen_archify_min.py agent-loop-lifecycle [fig-1-1-kv-cache ...]
"""
import os, re, sys

ARCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archify")
SHELL = os.path.join(ARCH, "ch5-two-leg-min.html")   # known-good shell


def build(name):
    deliver = os.path.join(ARCH, name + "-deliver.html")
    if not os.path.exists(deliver):
        deliver = os.path.join(ARCH, name + ".html")
    minhtml = os.path.join(ARCH, name + "-min.html")
    if not os.path.exists(deliver):
        print("no deliver.html for", name); return False
    d = open(deliver, encoding="utf-8").read()
    m = re.search(r"<svg\b.*?</svg>", d, re.S)
    if not m:
        print("no inline <svg> in", deliver); return False
    svg = m.group(0)
    # ensure viewBox="0 0 W H" (crop pipeline expects it)
    vb = re.search(r'viewBox="([0-9.+-]+) ([0-9.+-]+) ([0-9.+-]+) ([0-9.+-]+)"', svg)
    if not vb:
        print("no viewBox in svg for", name); return False
    # shell: strip its own <svg>...</svg>, splice in ours
    s = open(SHELL, encoding="utf-8").read()
    s2 = re.sub(r"<svg\b.*?</svg>", svg, s, count=1, flags=re.S)
    if s2 == s:
        print("svg splice failed for", name); return False
    open(minhtml, "w", encoding="utf-8").write(s2)
    print("built", os.path.basename(minhtml))
    return True


if __name__ == "__main__":
    names = sys.argv[1:] or ["agent-loop-lifecycle"]
    for n in names:
        build(n)
