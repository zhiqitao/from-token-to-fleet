#!/usr/bin/env python3
"""ink_conf_all.py — run ink_confirm across all figures, report REAL ink-overlap clusters."""
import pymupdf, numpy as np, itertools, os, subprocess, sys

ROOT = os.path.join(os.path.dirname(__file__), '..', 'design', 'manuscript')

def analyze(path, dpi=300):
    doc = pymupdf.open(path)
    page = doc[0]
    pix = page.get_pixmap(dpi=dpi)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    gray = img[..., :3].mean(axis=2)
    ink = gray < 150
    scale = dpi / 72.0

    cs = []
    for bi, blk in enumerate(page.get_text('rawdict')['blocks']):
        for line in blk.get('lines', []):
            for span in line.get('spans', []):
                sid = (bi, id(span))
                for ch in span.get('chars', []):
                    b = ch['bbox']
                    cs.append((b[0], b[1], b[2], b[3], ch['c'], sid))
    doc.close()

    results = []
    for a, b in itertools.combinations(cs, 2):
        if a[5] == b[5]:
            continue
        if not (not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])):
            continue
        ix0 = max(a[0], b[0]); iy0 = max(a[1], b[1])
        ix1 = min(a[2], b[2]); iy1 = min(a[3], b[3])
        if ix1 <= ix0 or iy1 <= iy0:
            continue
        px0 = max(int(ix0 * scale), 0); px1 = min(int(ix1 * scale), pix.width)
        py0 = max(int(iy0 * scale), 0); py1 = min(int(iy1 * scale), pix.height)
        if px1 <= px0 or py1 <= py0:
            continue
        # Require substantial overlap in BOTH dimensions: two stacked text lines have
        # char boxes that touch at a thin sliver even when their glyphs are separated
        # by whitespace; a genuine collision overlaps a meaningful area in both x and y.
        if (ix1 - ix0) * scale < 1.5 * scale or (iy1 - iy0) * scale < 1.0 * scale:
            continue
        region = ink[py0:py1, px0:px1]
        # Ground-truth discriminator: stacked text lines ALWAYS have a fully-white row
        # between their glyphs (the line gap), even though their padded char boxes
        # overlap. A genuine glyph collision has CONTINUOUS vertical ink across the
        # overlap (no white gap row). If the region contains any near-empty row, the two
        # glyphs are vertically separated -> benign line-stacking.
        row_d = region.mean(axis=1)
        if row_d.size and (row_d.min() < 0.02):
            continue
        density = float(region.mean())
        results.append((round(a[0]), round(a[1]), a[4], b[4], density))

    # cluster by location bucket, take max density
    from collections import defaultdict
    groups = defaultdict(list)
    for x0, y0, ca, cb, d in results:
        groups[(x0 // 40, y0 // 30)].append((x0, y0, ca, cb, d))
    real_clusters = 0
    cluster_list = []
    for key in sorted(groups):
        lst = groups[key]
        x0, y0, ca, cb, d = lst[0]
        md = max(l[4] for l in lst)
        if md > 0.10:
            real_clusters += 1
            cluster_list.append((x0, y0, ca, cb, round(md, 2), len(lst)))
    return real_clusters, cluster_list

def main():
    figs = []
    for dirpath, _, files in os.walk(ROOT):
        for f in files:
            if f.lower().endswith('.pdf') and f.lower().startswith('fig-'):
                figs.append(os.path.join(dirpath, f))
    figs.sort()
    print(f"{'figure':32} realClusters  detail")
    print('-' * 100)
    total = 0
    for path in figs:
        rc, cl = analyze(path)
        if rc:
            total += rc
            print(f"{os.path.basename(path):32} {rc:2d}")
            for x0, y0, ca, cb, md, n in cl[:14]:
                print(f"    ~({x0},{y0}) '{ca}'vs'{cb}' ink={md:.2f} n={n}")
        else:
            print(f"{os.path.basename(path):32}  0")
    print('-' * 100)
    print(f"TOTAL real ink-overlap clusters: {total}")

if __name__ == '__main__':
    main()
