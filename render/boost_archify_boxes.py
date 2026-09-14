#!/usr/bin/env python3
"""Boost an Archify SVG's text-to-layout ratio so fine labels are readable at
print, then re-crop to content.

To raise the ON-PAGE font size we must grow fonts faster than the diagram
footprint (a uniform geometry scale is cancelled by the viewBox re-crop).  So:
  * every font-size *= FONT_REL   (text grows)
  * every box (<rect> with real x/y/w/h) grows about its own centre by a SMALLER
    GBOX, moving its edges outward just enough to hold the bigger label
Labels stay centred (their x/y anchor is the box centre), and the connector
paths (fixed coords) stay put, so a modest GBOX keeps arrows attached.

Run from repo root:
    python3 render/boost_archify_boxes.py fig-1-1-kv-cache
"""
import os
import re
import sys

ARCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archify")
FONT_REL = float(os.environ.get("FONT_REL", "1.40"))
GBOX = float(os.environ.get("GBOX", "1.18"))


def boost(min_html):
    t = open(min_html, encoding="utf-8").read()
    svg_m = re.search(r"<svg.*?</svg>", t, re.S)
    if not svg_m:
        print("  no svg"); return False
    svg = svg_m.group(0)

    # 1) grow fonts
    def _f(m):
        return m.group(1) + "%g" % (float(m.group(2)) * FONT_REL) + m.group(3)
    svg = re.sub(r'(font-size\s*:\s*)([0-9.]+)(px)', _f, svg)
    svg = re.sub(r'(font-size\s*=\s*")([0-9.]+)(")', _f, svg)

    # 2) grow every box rect about its own centre by GBOX.  Skip: the full-canvas
    #    background rect (no class / 'width="100%"'), and the tiny icon/label
    #    backplates (<~50px) which scale with their own marker/def.
    def _g(m):
        pre = m.group(1)
        x = float(m.group(2)); y = float(m.group(3))
        w = float(m.group(4)); h = float(m.group(5))
        if w <= 0 or h <= 0:
            return m.group(0)
        nx = x + w / 2.0; ny = y + h / 2.0
        nw = w * GBOX; nh = h * GBOX
        return '%sx="%.1f" y="%.1f" width="%.1f" height="%.1f"' % (
            pre, nx - nw / 2, ny - nh / 2, nw, nh)
    svg = re.sub(r'(<rect\b(?![^>]*class="c-(mask)")[^>]*?)\sx="([0-9.+-]+)"'
                 r'\sy="([0-9.+-]+)"\swidth="([0-9.+-]+)"\sheight="([0-9.+-]+)"',
                 _g, svg)

    t = t[:svg_m.start()] + svg + t[svg_m.end():]
    open(min_html, "w", encoding="utf-8").write(t)
    return True


if __name__ == "__main__":
    names = sys.argv[1:]
    for n in names:
        p = os.path.join(ARCH, n + "-min.html")
        if not os.path.exists(p):
            print("no min.html for", n); continue
        ok = boost(p)
        print(n, "boosted" if ok else "failed")
