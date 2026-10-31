#!/usr/bin/env python3
"""Regenerate Fig 1.2 (token-travel) print assets with a font legibility floor.

Scope: ONLY fig-1-2-token-travel. Owned asset driver — canonical repeatability:
every run rebuilds *-min.html from the JSON source via archify deliver +
gen_archify_min, so there are no undocumented hand edits to min.html.

Pipeline (deterministic):
  1. node archify deliver  -> render/archify/fig-1-2-token-travel-deliver.html
  2. gen_archify_min.py    -> render/archify/fig-1-2-token-travel-min.html
  3. crop_archify_viewbox.crop_viewbox with FONTBOOST=1.45 GBOX=1.0 INCLUDE_PATHS=1
     (GBOX=1.0 keeps the four horizontal arrowheads un-buried; INCLUDE_PATHS=1
      keeps the full f6 feedback loop inside the viewBox)
  4. FONT FLOOR (this driver, AFTER crop — not another crop/fontboost):
     every numeric font-size inside the inline <svg> is raised to
     >= FONT_FLOOR px.  % values resolve against the owning <text> size
     (else 16px root default); <tspan> without its own size inherits the
     floored parent, with its own size floored directly.
  5. crop_archify_viewbox.render -> design/manuscript/chapter-01/figures/
     fig-01-token-travel.{pdf,png}

Usage:  python3 render/regenerate_ch1_token_travel.py
"""
import os
import re
import subprocess
import sys
import html as html_module
import http.server
import json
import threading

sys.dont_write_bytecode = True   # keep the repo clean: no render/__pycache__ writes

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = os.path.join(REPO, "render", "archify")
NAME = "fig-1-2-token-travel"
JSON_SRC = os.path.join(ARCH, NAME + ".json")
MIN_HTML = os.path.join(ARCH, NAME + "-min.html")
DELIVER = os.path.join(ARCH, NAME + "-deliver.html")
TARGET = os.path.join(REPO, "design/manuscript/chapter-01/figures/fig-01-token-travel")
ARCHIFY = "/home/ubuntu/tools/archify/archify/bin/archify.mjs"

FONT_FLOOR = float(os.environ.get("FONT_FLOOR", "14.6"))  # px in SVG units
FONTBOOST = "1.45"
GBOX = "1.0"
INCLUDE_PATHS = "1"


def sh(cmd):
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    sys.stdout.write(r.stdout[-2000:])
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:])
        raise SystemExit("command failed: %s" % " ".join(cmd))
    return r


def apply_font_floor(html, floor=FONT_FLOOR):
    """Raise every numeric font-size inside the inline <svg> to >= floor px.

    Handles: attribute form font-size="NN" / "NNpx" / "NN%", CSS form
    font-size:NNpx, and % resolved against the owning <text> font-size
    (16px root default when no ancestor specifies one).  <tspan> elements
    with no own size inherit the already-floored parent; with own size they
    are floored directly by the same pass.
    """
    m = re.search(r"(<svg\b.*?</svg>)", html, re.S)
    if not m:
        raise SystemExit("no inline <svg> found")
    svg = m.group(1)

    # parent (text/element) declared size, for %-resolution
    def parent_size(fragment_start, search_from):
        seg = svg[max(0, search_from - 400):fragment_start]
        mm = list(re.finditer(r"font-size\s*=\s*\"([0-9.]+)(%?)\"", seg))
        if mm:
            v = float(mm[-1].group(1))
            return v * 16.0 / 100.0 if mm[-1].group(2) == "%" else v
        return 16.0

    out = []
    last = 0
    changed = 0
    for fm in re.finditer(r"font-size\s*=\s*\"([0-9.]+)(%?)\"", svg):
        raw = float(fm.group(1))
        val = raw * parent_size(fm.start(), fm.start()) / 100.0 if fm.group(2) else raw
        new = max(val, floor)
        if new > val + 1e-9:
            changed += 1
        out.append(svg[last:fm.start()])
        out.append('font-size="%g"' % new)
        last = fm.end()
    out.append(svg[last:])
    svg = "".join(out)

    # CSS form inside the svg (none expected, handled for safety)
    def _css(mm):
        v = float(mm.group(2))
        return mm.group(1) + "%g" % max(v, floor)
    svg = re.sub(r"(font-size\s*:\s*)([0-9.]+)px", _css, svg)

    return html[:m.start(1)] + svg + html[m.end(1):], changed


def fit_edge_backplates(document):
    """Size six label masks from actual browser text bounds, not old font sizes."""
    script = '''<script>window.addEventListener('load',()=>{
      let fitted=0;
      for (let g of document.querySelectorAll('g[data-detail="context"][data-edge-id]')) {
        let r=g.querySelector('rect.c-mask'), t=g.querySelector('text');
        if (!r || !t) throw new Error('Missing edge mask/text');
        let b=t.getBBox();
        for(let [k,v] of Object.entries({x:b.x-4,y:b.y-3,width:b.width+8,height:b.height+6}))
          r.setAttribute(k,v.toFixed(4));
        fitted++;
      }
      let p=document.createElement('pre');p.id='fit-result';
      p.textContent=JSON.stringify({fitted,svg:new XMLSerializer().serializeToString(document.querySelector('svg'))});
      document.body.appendChild(p);
    });</script>'''
    body = document.replace('</body>', script + '</body>').encode()
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, format, *args):
            pass
    # Loopback avoids snap's hidden-directory file restrictions and argv limits.
    server = http.server.HTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = subprocess.run(['chromium', '--headless=new', '--no-sandbox',
            '--disable-gpu', '--virtual-time-budget=3000', '--dump-dom',
            'http://127.0.0.1:%d/' % server.server_port],
            capture_output=True, text=True, check=True, timeout=40)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    m = re.search(r'<pre id="fit-result">(.*?)</pre>', result.stdout, re.S)
    if not m:
        raise RuntimeError('Browser did not return fitted edge backplates')
    fitted = json.loads(html_module.unescape(m.group(1)))
    if fitted['fitted'] != 6:
        raise RuntimeError('Expected six edge backplates')
    return re.sub(r'<svg\b.*?</svg>', lambda _: fitted['svg'], document, count=1, flags=re.S)


def main():
    # env for the shared crop module (PAD is read at import time)
    os.environ["FONTBOOST"] = FONTBOOST
    os.environ["GBOX"] = GBOX
    os.environ["INCLUDE_PATHS"] = INCLUDE_PATHS
    sys.path.insert(0, os.path.join(REPO, "render"))
    import crop_archify_viewbox as crop

    print("== 1. archify deliver ==")
    sh(["node", ARCHIFY, "validate", "architecture", JSON_SRC, "--quality", "showcase", "--json"])
    sh(["node", ARCHIFY, "deliver", "architecture", JSON_SRC, DELIVER, "--quality", "showcase", "--json"])
    if not os.path.exists(DELIVER):
        raise SystemExit("deliver output missing: " + DELIVER)

    print("== 2. gen_archify_min ==")
    sh([sys.executable, os.path.join(REPO, "render", "gen_archify_min.py"), NAME])

    print("== 3. crop (FONTBOOST=%s GBOX=%s INCLUDE_PATHS=%s) ==" % (FONTBOOST, GBOX, INCLUDE_PATHS))
    bb = crop.crop_viewbox(MIN_HTML)
    print("  bbox:", bb)

    print("== 4. font floor >= %gpx ==" % FONT_FLOOR)
    t = open(MIN_HTML, encoding="utf-8").read()
    t2, n = apply_font_floor(t)
    t2 = fit_edge_backplates(t2)
    open(MIN_HTML, "w", encoding="utf-8").write(t2)
    print("  raised %d font-size declarations" % n)

    print("== 5. render ==")
    ok = crop.render(MIN_HTML, TARGET + ".pdf", TARGET + ".png")
    print("  rendered=%s -> %s.{pdf,png}" % (ok, TARGET))
    if not ok:
        raise SystemExit("render failed")


if __name__ == "__main__":
    main()