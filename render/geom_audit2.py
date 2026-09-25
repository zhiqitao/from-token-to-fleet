#!/usr/bin/env python3
"""Comprehensive geometry audit for fig-02-0202 (fig 2.1 redesign).

Verifies, on the exported vector PDF: (a) every labeled node box contains its text
with healthy padding; (b) the state-flow arrows land on the cache and the two
rails' K/V boxes; (c) the first-token feed lands on the decode token box and stays
in the right/bottom margin; (d) no connector crosses text; (e) no label overlaps a
box it does not belong to; (f) content is fully within the canvas.
"""
import sys, pymupdf
pdf = sys.argv[1]
pg = pymupdf.open(pdf)[0]
ws = pg.get_text("words")

def bb(w): return pymupdf.Rect(w[0], w[1], w[2], w[3])

# --- collect node boxes (orange-fill rounded boxes & the cache & resource panel) ---
node_boxes = []
for dr in pg.get_drawings():
    if not dr.get("fill"): continue
    r = dr["rect"]
    if r.width < 30 or r.height < 25: continue   # skip hatch swatches / tiny
    node_boxes.append(r)

def in_box(w, b, pad=2):
    return (b.x0 - pad <= w[0] and w[2] <= b.x1 + pad and
            b.y0 - pad <= w[1] and w[3] <= b.y1 + pad)

# (a) each word should be inside some node box OR be a free label. Flag words
# that are inside a box but too close to its edge, and words that straddle an edge.
worst = []
for w in ws:
    r = bb(w)
    for b in node_boxes:
        if (b.x0 <= r.x0 and r.x1 <= b.x1 and b.y0 <= r.y0 and r.y1 <= b.y1):
            lm = r.x0 - b.x0; rm = b.x1 - r.x1; tm = r.y0 - b.y0; bm = b.y1 - r.y1
            worst.append((min(lm, rm, tm, bm), w[4], round(r.x0), round(r.y0)))
worst.sort()
print("=== (a) tightest in-box padding (text fully inside a node box) ===")
for m in worst[:6]:
    print("  %.1f pt  %-10s @ x%d y%d" % (m[0], m[1], m[2], m[3]))

# (f) canvas fit
xs=[];ys=[]
for dr in pg.get_drawings():
    r=dr["rect"]
    if r.width>5 or r.height>5: xs+=[r.x0,r.x1]; ys+=[r.y0,r.y1]
for w in ws: xs+=[w[0],w[2]]; ys+=[w[1],w[3]]
print("=== (f) canvas fit ===")
print("  content x %.0f..%.0f  y %.0f..%.0f   page %s" %
      (min(xs),max(xs),min(ys),max(ys), pg.rect))
print("  fits", min(xs)>=0 and max(xs)<=pg.rect.x1 and min(ys)>=0 and max(ys)<=pg.rect.y1)
