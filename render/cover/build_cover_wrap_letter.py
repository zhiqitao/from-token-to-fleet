#!/usr/bin/env python3
"""Build the KDP cover wrap (back + spine + front) for the 8.5x11 letter trim
of "From Token to Fleet".  Sized to KDP's full-bleed template at points-per-inch
(72) so font-size values are natural pt.  Rendered to a single full-bleed PDF.

Usage:
    python3 render/cover/build_cover_wrap_letter.py <pages>
"""
import sys, os, subprocess

PAGES = int(sys.argv[1]) if len(sys.argv) > 1 else 259

# ---- KDP wrap sizing (inches) for an 8.5 x 11 letter trim ----
TRIM_W, TRIM_H = 8.5, 11.0
BLEED = 0.125
SPINE = PAGES * 0.002252              # per-page thickness (KDP 60# offset)
BACK_W = TRIM_W + BLEED               # bleed only on the outer (left) edge
FRONT_W = TRIM_W + BLEED
TOTAL_W = BACK_W + SPINE + FRONT_W
TOTAL_H = TRIM_H + 2 * BLEED

PT = 72.0

def pt(v):
    return "%.2f" % (v * PT)

BACK_X = 0.0
SPINE_X = BACK_W
FRONT_X = BACK_W + SPINE
SPINE_CX = SPINE_X + SPINE / 2.0

vals = dict(
    TW=pt(TOTAL_W), TH=pt(TOTAL_H), BW=pt(BACK_W), SW=pt(SPINE),
    FW=pt(FRONT_W), SX=pt(SPINE_X), FX=pt(FRONT_X),
    SCX=pt(SPINE_CX), BL=pt(BLEED), TRIMW=pt(TRIM_W), TRIMH=pt(TRIM_H),
    p01=pt(0.7), p02=pt(0.22), p03=pt(0.5), p04=pt(0.6), p05=pt(0.18),
    p06=pt(0.4), p07=pt(0.45), p08=pt(0.2), p09=pt(0.35), p10=pt(0.14),
    p11=pt(0.55), p12=pt(0.3), p13=pt(0.055), p14=pt(0.12), p15=pt(0.5),
    p16=pt(0.9), p17=pt(0.8), p18=pt(0.28), p19=pt(0.7), p20=pt(0.55),
    p21=pt(0.1), p22=pt(0.24), p23=pt(1.0), p24=pt(0.16), p25=pt(1.6),
    p26=pt(0.85), p27=pt(0.18), p28=pt(0.5),
)

TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  :root{
    --cream:#F4F1EA; --ink:#101014; --char:#575B63;
    --orange:#E8651A; --cyan:#148A99; --slate:#5B6B7A; --navy:#1B2A3A;
  }
  *{margin:0;padding:0;box-sizing:border-box;}
  html,body{margin:0;padding:0;width:100%;}
  body{font-family:'Inter','Helvetica Neue',Arial,sans-serif;color:var(--ink);}
  .wrap{position:relative;width:@TW@pt;height:@TH@pt;overflow:hidden;}
  .panel{position:absolute;top:0;bottom:0;}
  .back{left:0;width:@BW@pt;background:var(--cream);}
  .spine{left:@SX@pt;width:@SW@pt;background:linear-gradient(180deg,var(--orange) 0 33%%,var(--cyan) 33% 66%%,var(--slate) 66%% 100%%);opacity:0.9;}
  .front{left:@FX@pt;width:@FW@pt;background:var(--cream);}
  .front::before{content:'';position:absolute;inset:0;pointer-events:none;opacity:0.5;
    background-image:repeating-linear-gradient(58deg,rgba(27,42,58,0.05) 0 1px,transparent 1px 46px),
                     repeating-linear-gradient(-58deg,rgba(27,42,58,0.05) 0 1px,transparent 1px 46px);}

  .bcontent{position:absolute;left:@BL@pt;top:@BL@pt;width:@TRIMW@pt;height:@TRIMH@pt;
    padding:@p01@pt @p01@pt;display:flex;flex-direction:column;}
  .btitle{font-size:34pt;font-weight:900;letter-spacing:-0.02em;line-height:1.0;color:var(--ink);}
  .btitle .spark{color:var(--orange);}
  .bsub{margin-top:@p02@pt;font-size:14pt;font-weight:600;color:var(--char);}
  .blurb{margin-top:@p03@pt;font-size:13pt;line-height:1.5;color:var(--ink);}
  .bbox{margin-top:@p04@pt;border:2px solid var(--navy);border-radius:@p05@pt;padding:@p06@pt @p07@pt;}
  .bbox h3{font-size:13pt;font-weight:900;margin-bottom:@p08@pt;color:var(--navy);letter-spacing:0.05em;}
  .bbox .row{display:flex;align-items:center;gap:@p09@pt;padding:@p10@pt 0;border-top:1px solid rgba(27,42,58,0.15);font-size:12pt;}
  .bbox .row .n{flex:0 0 @p11@pt;font-weight:900;color:var(--orange);}
  .bbox .row .d{flex:1;font-weight:600;}
  .bnote{margin-top:@p12@pt;font-size:10pt;color:var(--slate);font-style:italic;}
  .bfooter{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;font-size:11pt;color:var(--slate);font-weight:600;}
  .barcode{display:flex;flex-direction:column;align-items:flex-end;}
  .barcode .bars{display:flex;gap:2px;height:@p15@pt;align-items:stretch;}
  .barcode .bars span{display:inline-block;width:@p13@pt;background:var(--ink);}
  .barcode .isbn{margin-top:@p14@pt;font-size:9pt;color:var(--slate);}

  .spine .stitle{position:absolute;left:50%;top:50%;transform:translate(-50%%,-50%%) rotate(-90deg);
    white-space:nowrap;font-size:13pt;font-weight:800;color:#fff;letter-spacing:0.04em;}
  .spine .sauthor{position:absolute;left:50%%;top:82%%;transform:translate(-50%%,-50%%) rotate(-90deg);
    white-space:nowrap;font-size:12pt;font-weight:700;color:#fff;}

  .fcontent{position:absolute;left:@BL@pt;top:@BL@pt;width:@TRIMW@pt;height:@TRIMH@pt;
    padding:@p16@pt @p17@pt;display:flex;flex-direction:column;z-index:2;}
  .ftitle{font-size:72pt;font-weight:900;letter-spacing:-0.028em;line-height:0.95;}
  .ftitle .spark{color:var(--orange);}
  .fsub{margin-top:@p18@pt;font-size:22pt;font-weight:600;color:var(--char);letter-spacing:0.01em;}
  .fstages{margin-top:@p19@pt;}
  .fstage{display:flex;align-items:center;justify-content:space-between;padding:@p20@pt 0;border-top:1px solid rgba(27,42,58,0.18);}
  .fstage:last-of-type{border-bottom:1px solid rgba(27,42,58,0.18);}
  .fkicker{font-size:11pt;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:var(--slate);}
  .fname{font-size:34pt;font-weight:900;text-transform:uppercase;letter-spacing:-0.01em;line-height:1;}
  .ffooter{margin-top:auto;padding-top:@p12@pt;border-top:1px solid rgba(27,42,58,0.25);display:flex;justify-content:space-between;font-size:11pt;color:var(--slate);font-weight:600;}
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
    <div class="fcontent">
      <div class="ftitle">FROM TOKEN<br>TO <span class="spark">FLEET</span></div>
      <div class="fsub">An AI Solution Architect's Handbook</div>
      <div class="fstages">
        <div class="fstage">
          <div><div class="fkicker">Macro</div><div class="fname" style="color:var(--slate)">Fleet</div></div>
          <div style="display:flex;gap:@p22@pt;align-items:center">
            <div style="width:@p23@pt;height:@p23@pt;border:2px solid var(--navy);border-radius:@p24@pt;background:#7C8A99"></div>
            <div style="width:@p23@pt;height:@p23@pt;border:2px solid var(--navy);border-radius:@p24@pt;background:#E8651A"></div>
            <div style="width:@p23@pt;height:@p23@pt;border:2px solid var(--navy);border-radius:@p24@pt;background:#148A99"></div>
          </div>
        </div>
        <div class="fstage">
          <div><div class="fkicker">System</div><div class="fname" style="color:var(--cyan)">Compute</div></div>
          <div style="width:@p25@pt;height:@p26@pt;border:2px solid var(--navy);border-radius:@p24@pt;background:#148A99"></div>
        </div>
        <div class="fstage">
          <div><div class="fkicker">Micro</div><div class="fname" style="color:var(--orange)">Token</div></div>
          <div style="display:flex;gap:@p27@pt;align-items:center">
            <div style="width:@p28@pt;height:@p28@pt;border:2px solid var(--navy);border-radius:@p21@pt;background:#E8651A"></div>
            <div style="width:@p28@pt;height:@p28@pt;border:2px solid var(--navy);border-radius:@p21@pt;background:#148A99"></div>
            <div style="width:@p28@pt;height:@p28@pt;border:2px solid var(--navy);border-radius:@p21@pt;background:#9AA7B3"></div>
          </div>
        </div>
      </div>
      <div class="ffooter">
        <span>v20260913</span>
        <span>Zhiqi Tao</span>
      </div>
    </div>
  </div>

</div>
</body>
</html>"""

html = TPL
for k, v in vals.items():
    html = html.replace('@'+k+'@', v)
html = html.replace('%%', '%')

here = os.path.dirname(os.path.abspath(__file__))
out_html = os.path.join(here, "cover_wrap_letter.html")
open(out_html, "w", encoding="utf-8").write(html)

chrome = "/home/ubuntu/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"
out_pdf = os.path.join(here, "cover_wrap_letter.pdf")
inject = ("<style>html,body{margin:0;padding:0;width:100%%;height:100%%;}"
          "@page{size:%spt %spt;margin:0}</style>" % (vals["TW"], vals["TH"]))
html2 = html.replace("</head>", inject + "</head>")
render_html = out_html + ".render.html"
open(render_html, "w", encoding="utf-8").write(html2)
subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                "--print-to-pdf=" + out_pdf, "--no-pdf-header-footer",
                "--no-margins", "file://" + os.path.abspath(render_html)],
               check=False, capture_output=True)
print("cover wrap written: %s  (%.2f x %.2f in, spine %.2f in, %d pages)"
      % (out_pdf, TOTAL_W, TOTAL_H, SPINE, PAGES))
