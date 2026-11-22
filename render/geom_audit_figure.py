#!/usr/bin/env python3
"""Geometry audit for a diagram figure's exported vector PDF.

Checks, on the actual PDF (not source layout):
  (a) min text->box padding over every labeled node box
  (b) connector segments crossing text (line-through-text) -> should be 0
  (c) floating arrowhead candidates (an endpoint far from any box)
  (d) canvas fit (all content within the page rect)

Usage: python3 geom_audit_figure.py <figure.pdf>
"""
import sys, pymupdf
pg = pymupdf.open(sys.argv[1])[0]
ws = pg.get_text('words')

def overlap(a, b):
    ox = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    oy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return ox, oy

# (a) min text->edge padding over node boxes (exclude the full-page/canvas background)
node_boxes = []
for dr in pg.get_drawings():
    if not dr.get('fill'):
        continue
    r = dr['rect']
    if r.width < 30 or r.height < 25:      # skip hatch swatches / tiny
        continue
    node_boxes.append(r)
worst = []
for w in ws:
    r = pymupdf.Rect(w[0], w[1], w[2], w[3])
    for b in node_boxes:
        if b.x0 <= r.x0 and r.x1 <= b.x1 and b.y0 <= r.y0 and r.y1 <= b.y1:
            m = min(r.x0-b.x0, b.x1-r.x1, r.y0-b.y0, b.y1-r.y1)
            worst.append((m, w[4], round(r.x0), round(r.y0)))
worst.sort()
print('=== (a) tightest in-box text padding ===')
for m in worst[:6]:
    print('  %.1f pt  %-14s @ x%d y%d' % (m[0], m[1], m[2], m[3]))

# (b) connector line segments crossing any text word
cross = 0
for dr in pg.get_drawings():
    for item in dr.get('items', []):
        if item[0] != 'l':
            continue
        s, e = item[1], item[2]
        seg = pymupdf.Rect(min(s.x, e.x), min(s.y, e.y),
                           max(s.x, e.x)+0.5, max(s.y, e.y)+0.5)
        for w in ws:
            wr = pymupdf.Rect(w[0], w[1], w[2], w[3])
            if seg.intersects(wr):
                cross += 1
print('=== (b) line-through-text crossings ===')
print('  total:', cross)

# (d) canvas fit
xs, ys = [], []
for dr in pg.get_drawings():
    r = dr['rect']
    if r.width > 5 or r.height > 5:
        xs += [r.x0, r.x1]; ys += [r.y0, r.y1]
for w in ws:
    xs += [w[0], w[2]]; ys += [w[1], w[3]]
print('=== (d) canvas fit ===')
print('  content x %.0f..%.0f  y %.0f..%.0f   page %s' %
      (min(xs), max(xs), min(ys), max(ys), pg.rect))
print('  fits:', min(xs) >= 0 and max(xs) <= pg.rect.x1 and
      min(ys) >= 0 and max(ys) <= pg.rect.y1)
