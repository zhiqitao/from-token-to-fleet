#!/usr/bin/env python3
"""Geometry audit for a figure PDF (the fig 2.1 production requirement).

Checks on the exported vector PDF, not the source layout: (a) min text->box
padding, (b) connector-arrow vs text overlap, (c) arrowhead vs target box,
(d) box dims consistency.  We report numbers; the caller interprets them.
"""
import pymupdf, itertools, collections, sys

pdf = sys.argv[1]
pg = pymupdf.open(pdf)[0]
ws = pg.get_text("words")

# --- (a) text-to-edge margin inside each large box ---
bxs = [dr["rect"] for dr in pg.get_drawings()
       if dr.get("fill") and dr["rect"].width > 45 and dr["rect"].height > 28]
print(f"== boxes: {len(bxs)} ==")
min_margin = 99
for r in bxs:
    for w in ws:
        wr = pymupdf.Rect(w[0], w[1], w[2], w[3])
        if wr.x0 >= r.x0 and wr.x1 <= r.x1 and wr.y0 >= r.y0 and wr.y1 <= r.y1:
            m = min(wr.x0 - r.x0, r.x1 - wr.x1, wr.y0 - r.y0, r.y1 - wr.y1)
            if m < min_margin:
                min_margin = m
                mininfo = (w[4], round(r.x0), round(r.y0), round(m, 1))
print(f"min text->edge margin in a box: {min_margin:.1f} pt  {mininfo}")

# --- (b) connector segments that pass through a text word bbox ---
segs = []
for dr in pg.get_drawings():
    if dr.get("fill"):
        continue
    for it in dr["items"]:
        if it[0] == "l":
            p1, p2 = it[1], it[2]
            if max(abs(p2.x - p1.x), abs(p2.y - p1.y)) > 6:
                segs.append((p1, p2))
print(f"== connector segments: {len(segs)} ==")
over = 0
for p1, p2 in segs:
    lb = pymupdf.Rect(min(p1.x, p2.x), min(p1.y, p2.y),
                      max(p1.x, p2.x), max(p1.y, p2.y))
    if lb.width < 40 and lb.height < 40:
        continue
    for w in ws:
        wr = pymupdf.Rect(w[0], w[1], w[2], w[3])
        if lb.intersects(wr):
            # require the segment to actually cross the interior, not just touch
            shrunk = pymupdf.Rect(wr.x0 + 1, wr.y0 + 1, wr.x1 - 1, wr.y1 - 1)
            if lb.intersects(shrunk):
                over += 1
                if over <= 12:
                    print(f"   seg ({p1.x:.0f},{p1.y:.0f})->({p2.x:.0f},{p2.y:.0f}) crosses '{w[4]}'")
print(f"total segment-through-text crossings: {over}")

# --- (c) polyline endpoints far from any box (floating arrowheads) ---
def polylines(segments):
    adj = collections.defaultdict(list)
    for p1, p2 in segments:
        a = (round(p1.x, 1), round(p1.y, 1)); b = (round(p2.x, 1), round(p2.y, 1))
        adj[a].append(b); adj[b].append(a)
    seen = set(); chains = []
    for p1, p2 in segments:
        a = (round(p1.x, 1), round(p1.y, 1))
        if a in seen:
            continue
        chain = [a]; seen.add(a); cur = a
        while True:
            nxts = [n for n in adj[cur] if n not in seen]
            if not nxts:
                break
            nxt = nxts[0]; seen.add(nxt); chain.append(nxt); cur = nxt
        chains.append(chain)
    return chains

def pt2r(x, y, r):
    dx = max(r.x0 - x, 0, x - r.x1); dy = max(r.y0 - y, 0, y - r.y1)
    return (dx * dx + dy * dy) ** 0.5

def chain_len(ch):
    return sum(abs(ch[i+1][0]-ch[i][0]) + abs(ch[i+1][1]-ch[i][1]) for i in range(len(ch)-1))

floating = []
for ch in polylines(segs):
    if chain_len(ch) > 1500:
        continue
    for endpt in (ch[0], ch[-1]):
        d = min(pt2r(endpt[0], endpt[1], r) for r in bxs)
        if d > 14:
            floating.append((endpt, round(d), round(chain_len(ch))))
print("== floating arrowhead candidates (end >14pt from any box) ==")
for e in sorted(set(floating))[:20]:
    print(f"   end {e[0]} far={e[1]} chainlen={e[2]}")
