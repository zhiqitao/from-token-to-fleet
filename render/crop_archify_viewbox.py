#!/usr/bin/env python3
"""Enlarge Archify hand-drawn diagrams for print legibility.

Problem: these diagrams are authored as an SVG at a large viewBox (e.g. 1000x600)
whose CONTENT only fills the centre, so when placed at the 6.1in book column the
whole graphic is small and its fonts render ~0.4-0.5x of body size.

Fix: crop the SVG viewBox to the bounding box of the actual drawn content
(every <rect>/<path>/<g>/<text>).  This scales the WHOLE diagram up uniformly
(boxes AND fonts together) so it fills the column and its text is readable -- no
box/text overflow because proportions are preserved.  Re-render to a vector PDF
(LaTeX) and a PNG (HTML) at the target chapter figure file.

Run from repo root:
    python3 render/crop_archify_viewbox.py [diagram1 diagram2 ...]
"""
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
ARCH = os.path.join(REPO, "archify")
CHROME = os.environ.get("CHROME") or \
    "/home/ubuntu/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"
PAD = float(os.environ.get("PAD", "0.02"))   # fraction of width to pad

# diagram (json base) -> target figure file relative to design/manuscript
DEFAULTS = {
    "ch5-two-leg":            "design/manuscript/chapter-05/figures/fig-05-0501",
    "ch13-ladder":            "design/manuscript/chapter-13/figures/fig-13-1301",
    "ch6-metric-hierarchy":   "design/manuscript/chapter-06/figures/fig-06-0601",
    "fleet-hierarchy":        "design/manuscript/chapter-17/figures/fig-17-1701",
    "ch10-compose":           "design/manuscript/chapter-10/figures/fig-10-1002",
    "ch10-parallel":          "design/manuscript/chapter-10/figures/fig-10-1001",
    "spine-decision-loop":    "render/latex/assets/spine-decision-loop",
    "agent-loop-lifecycle":   "design/manuscript/chapter-19/figures/fig-19-1901",
    "fig-1-1-kv-cache":       "design/manuscript/chapter-01/figures/fig-01-kv-cache",
    "fig-1-2-token-travel":   "design/manuscript/chapter-01/figures/fig-01-token-travel",
}


def find_chrome():
    import shutil
    for c in [CHROME, "/snap/bin/chromium", "/usr/bin/chromium-browser"]:
        if os.path.exists(c):
            return c
    for name in ["chromium", "chromium-browser", "google-chrome", "chrome"]:
        p = shutil.which(name)
        if p:
            return p
    return None


def content_bbox(svg, vbw=1000.0, vbh=600.0):
    """Return (x0,y0,x1,y1) bounding box of drawn content in the SVG,
    EXCLUDING the full-canvas background/grid <rect> (a rect covering most of
    the viewBox)."""
    xs, ys = [], []
    # Content boxes are explicit <rect> with an absolute px size.  Use only
    # reasonably-sized box rects (>=40px) so we exclude the full-canvas
    # background/grid rect, small icons (8px) and label backplates (~38px).
    for m in re.finditer(r'<rect\b[^>]*>', svg):
        a = m.group(0)
        gx = _num(a, "x"); gy = _num(a, "y")
        w = _num(a, "width"); h = _num(a, "height")
        if gx is None or gy is None or w is None or h is None:
            continue
        if w < 40 or h < 40:
            continue
        xs += [gx, gx + w]; ys += [gy, gy + h]
    # (Connectors, icons and labels sit between/inside the boxes, so the box
    #  extents give a safe, tight viewBox.  We deliberately do NOT parse
    #  <path> fan-out coords here -- they can extend well past the boxes.)
    # Optional: also include <path> route extents (for loop-back diagrams whose
    #  feedback path runs outside the node band). Enabled via INCLUDE_PATHS=1.
    if os.environ.get("INCLUDE_PATHS", "0") == "1":
        for m in re.finditer(r'<path\b[^>]*\bd="([^"]*)"', svg):
            d = m.group(1)
            for mm in re.finditer(r'(-?[\d.]+)[ ,]+(-?[\d.]+)', d):
                xs.append(float(mm.group(1))); ys.append(float(mm.group(2)))
    if not xs or not ys:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def _num(tag, name):
    m = re.search(r'%s="([0-9.+-]+)"' % name, tag)
    if not m:
        m = re.search(r'%s="([0-9.+-]+)px"' % name, tag)
    return float(m.group(1)) if m else None


def crop_viewbox(min_html):
    """Rewrite the SVG viewBox to the content bbox (+pad) AND grow every inline
    font and box so the fine diagram labels land at a readable print size.

    The Archify SVGs use 5.5-8px fonts in a ~1000-unit viewBox, so even after a
    content crop the labels sit well below ~9pt body text.  We grow fonts by
    FONTBOOST and boxes by a SMALLER GBOX (about each box's own centre), so the
    text-to-layout ratio rises: labels get relatively bigger than the diagram.
    Boxes grow just enough to hold the bigger text; labels stay centred; the
    connectors (fixed coords) are unchanged so arrows stay attached.  The crop
    is then computed on the GROWN content so nothing is clipped.  Save in place.
    """
    FONTBOOST = float(os.environ.get("FONTBOOST", "1.45"))
    GBOX = float(os.environ.get("GBOX", "1.18"))
    t = open(min_html, encoding="utf-8").read()
    m = re.search(r'(viewBox="0 0 )([0-9.]+) ([0-9.]+)(")', t)
    if not m:
        print("  no viewBox; skipping", min_html)
        return None
    vbw, vbh = float(m.group(2)), float(m.group(3))

    # 1) Grow every inline font (both 'font-size:NNpx' and 'font-size="NN"').
    def _boost(match):
        return match.group(1) + "%g" % (float(match.group(2)) * FONTBOOST) + match.group(3)
    t = re.sub(r'(font-size\s*:\s*)([0-9.]+)(px)', _boost, t)
    t = re.sub(r'(font-size\s*=\s*")([0-9.]+)(")', _boost, t)

    # 2) Grow every box <rect> about its own centre by GBOX.  Skip the
    #    full-canvas background rect (it has no x/y and 'width="100%"'), the
    #    tiny label backplates that belong to markers (<~50px), and the
    #    c-mask/c-external backplates already sized for their label.
    def _grow(match):
        pre = match.group(1)
        x = float(match.group(2)); y = float(match.group(3))
        w = float(match.group(4)); h = float(match.group(5))
        if w <= 0 or h <= 0:
            return match.group(0)
        nx = x + w / 2.0; ny = y + h / 2.0
        nw = w * GBOX; nh = h * GBOX
        return '%s x="%.1f" y="%.1f" width="%.1f" height="%.1f"' % (
            pre, nx - nw / 2, ny - nh / 2, nw, nh)
    t = re.sub(r'(<rect\b[^>]*?)\sx="([0-9.+-]+)"\sy="([0-9.+-]+)"'
               r'\swidth="([0-9.+-]+)"\sheight="([0-9.+-]+)"', _grow, t)

    # 3) Crop to the (now grown) content bbox.
    svg = re.search(r"<svg.*?</svg>", t, re.S)
    if not svg:
        return None
    bb = content_bbox(svg.group(0), vbw, vbh)
    if not bb:
        return None
    x0, y0, x1, y1 = bb
    w = max(x1 - x0, 1e-6); h = max(y1 - y0, 1e-6)
    pad = PAD * w
    x0 -= pad; y0 -= pad; x1 += pad; y1 += pad; w = x1 - x0; h = y1 - y0
    new_vb = 'viewBox="%.1f %.1f %.1f %.1f"' % (x0, y0, w, h)
    # Rewrite the viewBox by regex on the (grown) string: the m.start()/m.end()
    # indices describe the PRE-growth string and are stale after the growth
    # re.sub changed its length.
    t = re.sub(r'viewBox="[0-9.+-]+ [0-9.+-]+ [0-9.+-]+ [0-9.+-]+"', new_vb, t, count=1)

    open(min_html, "w", encoding="utf-8").write(t)
    return (x0, y0, x1, y1)


def render(min_html, out_pdf, out_png):
    html_path = "file://" + os.path.abspath(min_html)
    chrome = find_chrome()
    if not chrome:
        print("  no chrome; skipping", min_html)
        return False
    # Make the SVG fill the page exactly (no letterbox/min-width), so placing
    # the page at the 6.1in column makes the whole diagram fill the column.
    t = open(min_html, encoding="utf-8").read()
    vb = re.search(r'viewBox="([0-9.+-]+) ([0-9.+-]+) ([0-9.+-]+) ([0-9.+-]+)"', t)
    if vb:
        vbs = [float(vb.group(i)) for i in range(1, 5)]
        W = max(int(vbs[2]), 1); H = max(int(vbs[3]), 1)
    else:
        W, H = 1000, 600
    # Explicit @page size = the cropped content aspect -> NO letterbox, and the
    # PDF page IS the diagram, so \maxwidth{\textwidth} scales it to full column.
    inject = ("<style>html,body{margin:0;padding:0;width:100%;height:100%;"
              "background:#fff}svg{width:100%!important;height:100%!important;"
              "min-width:0!important;display:block}@page{size:" +
              str(W) + "px " + str(H) + "px;margin:0}</style>")
    t = t.replace("</head>", inject + "</head>")
    open(min_html, "w", encoding="utf-8").write(t)
    subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                    "--print-to-pdf=" + out_pdf, "--no-pdf-header-footer",
                    "--no-margins", html_path], check=False, capture_output=True)
    subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                    "--window-size=%d,%d" % (W * 2, H * 2),
                    "--force-device-scale-factor=2",
                    "--screenshot=" + out_png, "--hide-scrollbars",
                    html_path], check=False, capture_output=True)
    return True


def main():
    chrome = find_chrome()
    print("chrome:", chrome)
    if not chrome:
        sys.exit("no headless chrome available")
    names = sys.argv[1:] or list(DEFAULTS.keys())
    for name in names:
        target = DEFAULTS.get(name)
        if not target:
            print("no target for", name); continue
        min_html = os.path.join(ARCH, name + "-min.html")
        if not os.path.exists(min_html):
            print("no min.html for", name); continue
        bb = crop_viewbox(min_html)
        ok = render(min_html, target + ".pdf", target + ".png")
        print(f"[{name}] -> {target}  bbox={bb}  rendered={ok}")


if __name__ == "__main__":
    main()
