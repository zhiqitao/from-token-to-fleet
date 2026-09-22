#!/usr/bin/env python3
"""Boost Archify hand-drawn diagram legibility for print.

Problem: these diagrams are authored as an SVG at a large viewBox (e.g. 1000x600)
with inline font-size ~7-11px, rendered to a 12in-wide PDF, then placed at the
6.1in book column.  Every font shrinks ~0.44x, so an 11px label renders ~4.8pt.
The nodes have generous internal padding.

Fix (per diagram):
  * Multiply the inline SVG font-size values by `BOOST` so labels are larger
    relative to the viewBox.
  * Optionally recompute the viewBox to the drawn-content bounding box (with a
    little padding) so the diagram fills more of the column instead of sitting
    small in a wide empty canvas -- this makes every label larger on the page.
  * Re-render to a vector PDF (for LaTeX) and a PNG (for HTML) at the target
    chapter figure file.

Run from repo root:
    python3 render/boost_archify_fonts.py [diagram1 diagram2 ...]
"""
import glob
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
ARCH = os.path.join(REPO, "archify")
CHROME = os.environ.get("CHROME") or \
    "/home/ubuntu/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"
BOOST = float(os.environ.get("BOOST", "1.45"))

# diagram (json base) -> target figure file relative to design/manuscript
DEFAULTS = {
    "ch5-two-leg":            "design/manuscript/chapter-05/figures/fig-05-0501",
    "fleet-hierarchy":        "design/manuscript/chapter-17/figures/fig-17-1701",
    "spine-decision-loop":    "design/manuscript/chapter-22/figures/fig-22-2201",
    "agent-loop-lifecycle":  "design/manuscript/chapter-19/figures/fig-19-1901",
}


def find_chrome():
    for c in [CHROME, "/snap/bin/chromium", "/usr/bin/chromium-browser"]:
        if os.path.exists(c):
            return c
    return shutil_which_chrome()


def shutil_which_chrome():
    import shutil
    for name in ["chromium", "chromium-browser", "google-chrome", "chrome"]:
        p = shutil.which(name)
        if p:
            return p
    return None


def boost_svg_fonts(min_html):
    """Scale every inline font-size (px or unitless) in the SVG by BOOST."""
    t = open(min_html, encoding="utf-8").read()
    # font-size="N" and font-size:Npx / font-size: N
    def repl_px(m):
        v = float(m.group(1)) * BOOST
        return f"font-size=\"{v:.1f}\""
    t = re.sub(r'font-size="([0-9.]+)"', repl_px, t)
    def repl_css(m):
        v = float(m.group(1)) * BOOST
        return "font-size:%.1f%s" % (v, m.group(2))
    t = re.sub(r"font-size:\s*([0-9.]+)(px)", repl_css, t)
    open(min_html, "w", encoding="utf-8").write(t)
    return t


def render(min_html, out_pdf, out_png):
    html_path = "file://" + os.path.abspath(min_html)
    chrome = find_chrome()
    if not chrome:
        print("  no chrome; skipping", min_html)
        return False
    # Vector PDF
    subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                    "--print-to-pdf=" + out_pdf, "--no-pdf-header-footer",
                    html_path], check=False, capture_output=True)
    # PNG at natural aspect x2
    try:
        vb = open(min_html, encoding="utf-8").read()
        m = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', vb)
        W, H = (int(float(m.group(1))), int(float(m.group(2)))) if m else (1000, 600)
    except Exception:
        W, H = 1000, 600
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
        boost_svg_fonts(min_html)
        out_pdf = target + ".pdf"
        out_png = target + ".png"
        ok = render(min_html, out_pdf, out_png)
        print(f"[{name}] -> {target}  rendered={ok}")


if __name__ == "__main__":
    main()
