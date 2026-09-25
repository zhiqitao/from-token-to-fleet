#!/usr/bin/env python3
"""Scan box-and-arrow diagram figures for connector ARROWHEADS that terminate in
whitespace rather than on a box (the fig 2.1 defect class: an arrow that should
feed a target box but ends in open space).

Method: for each figure PDF, (a) find the LARGE filled rectangles (the labeled
boxes), (b) find connector polylines (non-filled stroke segments), (c) for each
chain's two terminal points, compute the distance to the nearest large box.
A terminal that is far from every large box AND is a chain of modest length is a
candidate "floating" arrowhead.

Usage: python3 render/scan_floating_arrowheads.py <repo_override>
"""
import glob, os, sys, collections, pymupdf

repo = sys.argv[1] if len(sys.argv) > 1 else "/home/ubuntu/hermes-work/from-token-to-fleet"
pdfs = sorted(glob.glob(f"{repo}/design/manuscript/chapter-*/figures/fig-*.pdf"))

def big_boxes(page):
    rects = []
    for dr in page.get_drawings():
        if not dr.get("fill"):
            continue
        r = dr["rect"]
        if r.width > 30 and r.height > 18:      # labeled boxes, not hatch swatches
            rects.append(r)
    return rects

def polylines(segs):
    adj = collections.defaultdict(list)
    for p1, p2 in segs:
        a = (round(p1.x, 1), round(p1.y, 1)); b = (round(p2.x, 1), round(p2.y, 1))
        adj[a].append(b); adj[b].append(a)
    seen = set(); chains = []
    for p1, p2 in segs:
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

def pt_to_rect(x, y, r):
    dx = max(r.x0 - x, 0, x - r.x1); dy = max(r.y0 - y, 0, y - r.y1)
    return (dx * dx + dy * dy) ** 0.5

def chain_len(ch):
    return sum(abs(ch[i+1][0]-ch[i][0]) + abs(ch[i+1][1]-ch[i][1]) for i in range(len(ch)-1))

for p in pdfs:
    d = pymupdf.open(p); pg = d[0]
    bx = big_boxes(pg)
    if len(bx) < 2:
        continue                                       # not a multi-box diagram
    segs = []
    for dr in pg.get_drawings():
        if dr.get("fill"):
            continue
        for it in dr["items"]:
            if it[0] == "l":
                p1, p2 = it[1], it[2]
                if max(abs(p2.x-p1.x), abs(p2.y-p1.y)) > 6:
                    segs.append((p1, p2))
    if not segs:
        continue
    floating = []
    for ch in polylines(segs):
        L = chain_len(ch)
        if L > 1200:                                    # rails / guides, skip
            continue
        for endpt in (ch[0], ch[-1]):
            x, y = endpt
            dmin = min(pt_to_rect(x, y, r) for r in bx)
            if dmin > 14:
                floating.append((endpt, round(dmin), round(L)))
    if floating:
        uniq = sorted(set(floating))
        print(f"### {os.path.basename(p)}  ({len(bx)} boxes)")
        for e in uniq:
            print(f"    end {e[0]} far={e[1]} chainlen={e[2]}")
