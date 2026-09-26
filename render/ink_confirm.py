#!/usr/bin/env python3
"""ink_confirm.py — confirm genuine text/text overlaps via raster ink density.

Longitudinal (vertical) the char-bbox scan over-reports because a char bbox spans the
full line-height, so stacked title/subtitle lines "overlap" in bbox even when their
ink is separated by whitespace. For each flagged char pair we render the intersection
region and measure dark-ink density. If the shared region contains real ink from BOTH
glyphs, it is a genuine collision; if it is essentially empty, it is benign line-stacking.

We also handle the case where two glyphs merely have overlapping ADVANCE boxes but their
actual ink is separated. Output: per figure, per collision cluster -> ink density of the
intersection, and a verdict.

Usage: python3 ink_confirm.py <pdf> [dpi]
"""
import pymupdf, numpy as np, sys

def char_boxes(page):
    out = []
    for bi, blk in enumerate(page.get_text('rawdict')['blocks']):
        for line in blk.get('lines', []):
            for span in line.get('spans', []):
                sid = (bi, id(span))
                for ch in span.get('chars', []):
                    b = ch['bbox']
                    out.append((b[0], b[1], b[2], b[3], ch['c'], sid))
    return out

def ov(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

def main():
    path = sys.argv[1]
    dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    doc = pymupdf.open(path)
    page = doc[0]
    pix = page.get_pixmap(dpi=dpi)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    scale = dpi / 72.0
    gray = img[..., :3].mean(axis=2)
    ink = gray < 150  # dark glyph/line ink

    cs = char_boxes(page)
    # cluster colliding pairs by location
    results = []
    for a, b in itertools_combinations(cs, 2):
        if a[5] == b[5]:
            continue
        if not ov(a[:4], b[:4]):
            continue
        # intersection rect in page pts
        ix0 = max(a[0], b[0]); iy0 = max(a[1], b[1])
        ix1 = min(a[2], b[2]); iy1 = min(a[3], b[3])
        if ix1 <= ix0 or iy1 <= iy0:
            continue
        # pixels
        px0 = int(ix0 * scale); px1 = int(ix1 * scale)
        py0 = int(iy0 * scale); py1 = int(iy1 * scale)
        px0 = max(px0, 0); py0 = max(py0, 0)
        px1 = min(px1, pix.width); py1 = min(py1, pix.height)
        if px1 <= px0 or py1 <= py0:
            continue
        region = ink[py0:py1, px0:px1]
        density = float(region.mean()) if region.size else 0.0
        results.append((round(a[0]), round(a[1]), a[4], b[4], density, region.size))

    # group by top-left location bucket
    from collections import defaultdict
    groups = defaultdict(list)
    for x0, y0, ca, cb, d, n in results:
        groups[(x0 // 40, y0 // 30)].append((x0, y0, ca, cb, d))
    print(f"page {dpi}dpi  collision clusters: {len(groups)}")
    for key in sorted(groups):
        lst = groups[key]
        x0, y0, ca, cb, d = lst[0]
        dens = [l[4] for l in lst]
        verdict = "REAL" if max(dens) > 0.10 else "stacking/benign"
        print(f"  ~({x0},{y0}) '{ca}'vs'{cb}'  n={len(lst)}  maxink={max(dens):.2f}  -> {verdict}")
    doc.close()

import itertools as _it
def itertools_combinations(seq, r):
    return _it.combinations(seq, r)

if __name__ == '__main__':
    main()
