#!/usr/bin/env python3
"""Same-line glyph overlap scan for the built book PDF (render venv python).

Groups words by visual line (y0 bucket of 2pt, merged with neighbor buckets),
then reports adjacent same-line word pairs whose x-intervals overlap by >0.5pt.
This is the tiebreaker for table-column collisions that models miss.
"""
import pymupdf
from collections import defaultdict

d = pymupdf.open("render/build/from-token-to-fleet-v20260913-plain.pdf")
print("pages:", d.page_count)
hits = []
for i, pg in enumerate(d):
    words = pg.get_text("words")
    buckets = defaultdict(list)
    for w in words:
        buckets[round(w[1] / 2)].append(w)
    seen = set()
    for k, ws in buckets.items():
        cand = ws + buckets.get(k - 1, []) + buckets.get(k + 1, [])
        uu = []
        for w in cand:
            if id(w) in seen:
                continue
            seen.add(id(w))
            uu.append(w)
        uu.sort(key=lambda w: w[0])
        for a, b in zip(uu, uu[1:]):
            if abs(a[1] - b[1]) > 2:
                continue
            ov = a[2] - b[0]
            if ov > 0.5 and a[4] != b[4]:
                hits.append((i + 1, round(ov, 2), a[4], b[4]))
uniq = {}
for h in hits:
    uniq[(h[0], h[2], h[3])] = h
hits = sorted(uniq.values(), key=lambda x: (-x[1], x[0]))
print("SAME-LINE overlaps:", len(hits))
for h in hits[:30]:
    print("  p", h[0], "ov", h[1], repr(h[2]), "x", repr(h[3]))
t = d[301].get_text()
print("p302 Metric col:", "Metric" in t, "| N-1 note:", "N-1 failover" in t)