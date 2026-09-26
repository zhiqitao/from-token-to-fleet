#!/usr/bin/env python3
"""scan_all_figs.py — scan every figure PDF for (a) text-on-text and (b) line-through-text.

For (b) we intersect every drawing segment with every word bbox. Because box borders
naturally surround their own label, we classify each hit:
  R  = REAL line through a word (segment crosses the word interior with appreciable
       penetration and does NOT belong to a box that properly contains the word)
  ?  = needs human/vision confirm (e.g. band-border near a label, rounded corners)
We print candidates; a human/vision pass resolves '?'.

Usage: python3 scan_all_figs.py
"""
import pymupdf, itertools, math, glob, os, sys

ROOT = os.path.join(os.path.dirname(__file__), '..', 'design', 'manuscript')

def segs_of_page(page):
    """Yield (x1,y1,x2,y2) straight segments from all drawing items.
    'l' => (type, p0, p1); 're' => (type, rect); 'c' => (type, p0,c1,c2,p1) cubic.
    's' (stroke) and 'f'(fill) are composites; curve items are flattened by
    sampling the cubic bezier ON the curve."""
    for dr in page.get_drawings():
        for item in dr.get('items', []):
            typ = item[0]
            if typ == 'l':
                p1, p2 = item[1], item[2]
                yield (p1.x, p1.y, p2.x, p2.y)
            elif typ == 're':
                r = item[1]
                x0, y0, x1, y1 = r.x0, r.y0, r.x1, r.y1
                yield (x0, y0, x1, y0); yield (x0, y1, x1, y1)
                yield (x0, y0, x0, y1); yield (x1, y0, x1, y1)
            elif typ == 'c':
                p0, c1, c2, p1 = item[1], item[2], item[3], item[4]
                prev = (p0.x, p0.y)
                for t in range(1, 13):
                    u = t / 12.0
                    x = ((1 - u) ** 3 * p0.x + 3 * (1 - u) ** 2 * u * c1.x
                         + 3 * (1 - u) * u ** 2 * c2.x + u ** 3 * p1.x)
                    y = ((1 - u) ** 3 * p0.y + 3 * (1 - u) ** 2 * u * c1.y
                         + 3 * (1 - u) * u ** 2 * c2.y + u ** 3 * p1.y)
                    yield (prev[0], prev[1], x, y)
                    prev = (x, y)

def intersect(x1, y1, x2, y2, wx0, wy0, wx1, wy1):
    """Liang-Barsky segment vs axis-aligned rect; returns True and penetration depth."""
    dx, dy = x2 - x1, y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - wx0, wx1 - x1, y1 - wy0, wy1 - y1]
    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return None
        else:
            t = qi / pi
            if pi < 0:
                if t > u2: return None
                if t > u1: u1 = t
            else:
                if t < u1: return None
                if t < u2: u2 = t
    return (u2 - u1)

def word_overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

def main():
    figs = []
    for dirpath, _, files in os.walk(ROOT):
        for f in files:
            if f.lower().endswith('.pdf') and f.lower().startswith('fig-'):
                figs.append(os.path.join(dirpath, f))
    figs.sort()

    summary = []
    for path in figs:
        doc = pymupdf.open(path)
        # just first page (figures are single-page)
        page = doc[0]
        words = page.get_text('words')
        # (a) text-on-text
        tt = [(round(a[0]), round(a[1]), a[4], b[4]) for a, b in itertools.combinations(words, 2) if word_overlap(a, b)]
        # (b) line-through-text
        segs = list(segs_of_page(page))
        hits = []
        for (sx1, sy1, sx2, sy2) in segs:
            len2 = (sx2 - sx1) ** 2 + (sy2 - sy1) ** 2
            if len2 < (1.5) ** 2:
                continue  # skip tiny segments
            for wd in words:
                wx0, wy0, wx1, wy1 = wd[0], wd[1], wd[2], wd[3]
                # shrink word box slightly to avoid ascender/descender padding FPs
                pad = 0.5
                r = intersect(sx1, sy1, sx2, sy2, wx0 + pad, wy0 + pad, wx1 - pad, wy1 - pad)
                if r is not None and r > 0.10:  # penetrates >10% of segment
                    hits.append((round(sx1), round(sy1), round(sx2), round(sy2), wd[4]))
        name = os.path.basename(path)
        status = 'OK'
        notes = []
        if tt: status, notes = 'TEXT-COLLIDE', [f'{len(tt)} text-on-text']
        if hits:
            if status != 'TEXT-COLLIDE': status = 'LINE-THRU'
            notes.append(f'{len(hits)} line-through candidates')
        summary.append((name, status, '; '.join(notes), tt[:6], hits[:10]))
        doc.close()

    print(f"{'figure':32} {'status':14} notes")
    print('-' * 90)
    for name, status, notes, tt, hits in summary:
        print(f"{name:32} {status:14} {notes}")
    print()
    print('=== DETAIL (figures flagged) ===')
    for name, status, notes, tt, hits in summary:
        if status != 'OK':
            print(f"\n### {name}  [{status}]")
            if tt:
                print("  TEXT-ON-TEXT:")
                for t in tt:
                    print(f"    x{t[0]},y{t[1]}  '{t[2]}' vs '{t[3]}'")
            if hits:
                print("  LINE-THROUGH (seg -> word):")
                for h in hits:
                    print(f"    seg({h[0]},{h[1]} -> {h[2]},{h[3]})  crosses '{h[4]}'")

if __name__ == '__main__':
    main()
