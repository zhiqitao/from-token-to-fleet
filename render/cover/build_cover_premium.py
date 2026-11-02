#!/usr/bin/env python3
"""Build the KDP cover wrap (back + spine + front) for the 8.5x11 letter trim of
"From Token to Fleet" using the premium-minimal front cover design
(cover_premium_letter.svg).  Back + spine typographic, colors matched to the
premium palette.  Rendered to a single full-bleed PDF.

Usage:
    python3 render/cover/build_cover_premium.py <pages>
"""
import sys, os, base64, subprocess

PAGES = int(sys.argv[1]) if len(sys.argv) > 1 else 361

TRIM_W, TRIM_H = 8.5, 11.0
BLEED = 0.125
SPINE = PAGES * 0.002252
BACK_W = TRIM_W + BLEED
FRONT_W = TRIM_W + BLEED
TOTAL_W = BACK_W + SPINE + FRONT_W
TOTAL_H = TRIM_H + 2 * BLEED

PT = 72.0
def pt(v): return "%.2f" % (v * PT)

BACK_X = 0.0
SPINE_X = BACK_W
FRONT_X = BACK_W + SPINE
SPINE_CX = SPINE_X + SPINE / 2.0

here = os.path.dirname(os.path.abspath(__file__))

# Embed the front cover as VECTOR SVG, inlined into the HTML (not as an img
# src) so Chrome renders it as vector type, keeping the wrap crisp and small.
front_svg = os.path.join(here, "cover_premium_letter.svg")
with open(front_svg, encoding="utf-8") as f:
    svg_data = f.read()

vals = dict(
    TW=pt(TOTAL_W), TH=pt(TOTAL_H), BW=pt(BACK_W), SW=pt(SPINE),
    FW=pt(FRONT_W), SX=pt(SPINE_X), FX=pt(FRONT_X),
    SCX=pt(SPINE_CX), BL=pt(BLEED), TRIMW=pt(TRIM_W), TRIMH=pt(TRIM_H),
    IMGW=pt(TRIM_W), IMGH=pt(TRIM_H), SVGINLINE=svg_data,
)

TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  :root{ --ivory:#F8F5EE; --ink:#17263B; --navy:#203750; --char:#586470;
         --orange:#E87836; --teal:#3A9AA8; --cyan:#79C1CB; --slate:#7B8283; }
  *{margin:0;padding:0;box-sizing:border-box;}
  html,body{margin:0;padding:0;width:100%;}
  body{font-family:'Inter Display','Inter','Helvetica Neue',Arial,sans-serif;color:var(--ink);}
  .wrap{position:relative;width:@TW@pt;height:@TH@pt;overflow:hidden;}
  .panel{position:absolute;top:0;bottom:0;}
  .back{left:0;width:@BW@pt;background:var(--ivory);}
  .spine{left:@SX@pt;width:@SW@pt;background:linear-gradient(180deg,var(--orange) 0 25%%,var(--teal) 25% 50%%,var(--cyan) 50% 75%%,var(--navy) 75%% 100%%);opacity:0.94;}
  .front{left:@FX@pt;width:@FW@pt;background:var(--ivory);}

  .bcontent{position:absolute;left:@BL@pt;top:@BL@pt;width:@TRIMW@pt;height:@TRIMH@pt;
    padding:0.7in 0.6in;display:flex;flex-direction:column;}
  .btitle{font-size:30pt;font-weight:850;letter-spacing:-0.02em;line-height:1.05;color:var(--ink);}
  .btitle .spark{color:var(--orange);}
  .bsub{margin-top:0.22in;font-size:13pt;font-weight:600;color:var(--char);}
  .blurb{margin-top:0.5in;font-size:12.5pt;line-height:1.55;color:var(--ink);}
  .bbox{margin-top:0.55in;border:2px solid var(--navy);border-radius:0.16in;padding:0.28in 0.3in;}
  .bbox h3{font-size:12pt;font-weight:900;margin-bottom:0.14in;color:var(--navy);letter-spacing:0.06em;}
  .bbox .row{display:flex;align-items:center;gap:0.18in;padding:0.1in 0;border-top:1px solid rgba(32,55,80,0.15);font-size:12pt;}
  .bbox .row .n{flex:0 0 0.5in;font-weight:900;color:var(--orange);}
  .bbox .row .d{flex:1;font-weight:600;}
  .bnote{margin-top:0.18in;font-size:10pt;color:var(--slate);font-style:italic;}
  .bfooter{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;font-size:11pt;color:var(--slate);font-weight:600;}
  .barcode{display:flex;flex-direction:column;align-items:flex-end;}
  .barcode .bars{display:flex;gap:2px;height:0.5in;align-items:stretch;}
  .barcode .bars span{display:inline-block;width:0.055in;background:var(--ink);}
  .barcode .isbn{margin-top:0.12in;font-size:9pt;color:var(--slate);}

  .spine .stitle{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) rotate(-90deg);
    white-space:nowrap;font-size:12pt;font-weight:800;color:#fff;letter-spacing:0.04em;}
  .spine .sauthor{position:absolute;left:50%;top:82%;transform:translate(-50%,-50%) rotate(-90deg);
    white-space:nowrap;font-size:11pt;font-weight:700;color:#fff;}

  .frontimg{position:absolute;left:@BL@pt;top:@BL@pt;width:@TRIMW@pt;height:@TRIMH@pt;}
</style>
</head>
<body>
<div class="wrap">

  <div class="panel back">
    <div class="bcontent">
      <div class="btitle">FROM TOKEN<br>TO <span class="spark">FLEET</span></div>
      <div class="bsub">An AI Solution Architect's Handbook</div>
      <div class="blurb">From a single token's cost to a fleet of specialised models,
      this book traces how to reason about, build, and operate production AI systems.
      It moves from the economics of one token through parallelism, memory, and
      serving, up to fleet-level architecture and a red-team / green-team discipline
      for honest evaluation.</div>
      <div class="bbox">
        <h3>WHAT'S INSIDE</h3>
        <div class="row"><div class="n">01</div><div class="d">The token as the cost unit</div></div>
        <div class="row"><div class="n">02</div><div class="d">Memory as the first constraint</div></div>
        <div class="row"><div class="n">03</div><div class="d">Parallelism, batching &amp; serving</div></div>
        <div class="row"><div class="n">04</div><div class="d">Fleet-level architecture</div></div>
        <div class="row"><div class="n">05</div><div class="d">Red-team / green-team evaluation</div></div>
        <div class="bnote">A pragmatic field guide for engineers and architects.</div>
      </div>
      <div class="bfooter">
        <span>Zhiqi Tao</span>
        <div class="barcode">
          <div class="bars"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
          <div class="isbn">ISBN 000-0-000000-00-0 (placeholder)</div>
        </div>
      </div>
    </div>
  </div>

  <div class="panel spine">
    <div class="stitle">FROM TOKEN TO FLEET</div>
    <div class="sauthor">Zhiqi Tao</div>
  </div>

  <div class="panel front">
    <div class="frontimg">@SVGINLINE@</div>
  </div>

</div>
</body>
</html>"""

html = TPL
for k, v in vals.items():
    html = html.replace('@'+k+'@', v)
html = html.replace('%%', '%')

out_html = os.path.join(here, "cover_premium_wrap.html")
open(out_html, "w", encoding="utf-8").write(html)

chrome = "/home/ubuntu/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"
out_pdf = os.path.join(here, "cover_premium_wrap.pdf")
inject = ("<style>html,body{margin:0;padding:0;width:100%;height:100%;}"
          "@page{size:" + vals["TW"] + "pt " + vals["TH"] + "pt;margin:0}</style>")
html2 = html.replace("</head>", inject + "</head>")
render_html = out_html + ".render.html"
open(render_html, "w", encoding="utf-8").write(html2)
subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                "--print-to-pdf=" + out_pdf, "--no-pdf-header-footer",
                "--no-margins", "file://" + os.path.abspath(render_html)],
               check=False, capture_output=True)
print("premium cover wrap written: %s  (%.2f x %.2f in, spine %.2f in, %d pages)"
      % (out_pdf, TOTAL_W, TOTAL_H, SPINE, PAGES))
