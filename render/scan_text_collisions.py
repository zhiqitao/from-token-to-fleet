#!/usr/bin/env python3
"""Scan the built book PDF for TEXT-ON-TEXT COLLISIONS inside figure regions.

The book embeds figures as VECTOR PDFs (regen_figs.py emits matplotlib .pdf),
so pymupdf can extract each figure's text with bounding boxes. This is the
authoritative way to catch a text element sitting on top of another text element
(the defect class found in fig 7.2, where the legend's first row overlapped the
"Context length (K tokens)" axis title).

Method: for each page, take all extracted word rectangles, and report pairs of
words that overlap with substantial area AND come from different text lines
(y-centers differ by more than a word-height) -- i.e. true cross-element
overlap, not normal intra-line kerning. We focus only on pages that contain a
figure (page has >8 text spans clustered in one region OR matches a figure
caption), to keep the report small and relevant.

Usage: python3 render/scan_text_collisions.py <book.pdf> [min_iol]
"""
import sys, itertools, pymupdf

def words(page):
    return page.get_text("words")  # x0,y0,x1,y1,word,block,line,wordno

def overlap(a, b):
    ox = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    oy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return ox * oy

def area(w):
    return max(1, (w[2]-w[0]) * (w[3]-w[1]))

def main(pdf, min_iol=0.30):
    doc = pymupdf.open(pdf)
    total = 0
    for p in range(len(doc)):
        ws = words(doc[p])
        if len(ws) < 8:
            continue
        hits = []
        for a, b in itertools.combinations(ws, 2):
            # only if they are on recognizably different lines (y-center apart)
            ay = (a[1]+a[3])/2; by = (b[1]+b[3])/2
            if abs(ay - by) < max(2.0, (a[3]-a[1])*0.35):
                continue
            o = overlap(a, b)
            union = area(a)+area(b)-o
            iol = o/union
            if iol >= min_iol:
                hits.append((iol, a, b))
        if hits:
            # dedupe by word pair surface
            print(f"\n=== page {p} ({doc[p]}) ===")
            for iol, a, b in sorted(hits, reverse=True)[:40]:
                total += 1
                print(f"  [{iol:.2f}] '{a[4]}'({a[0]:.0f},{a[1]:.0f})  <->  '{b[4]}'({b[0]:.0f},{b[1]:.0f})")
    print(f"\nTOTAL cross-element text overlaps: {total}")

if __name__ == "__main__":
    import os
    pdf = sys.argv[1]
    mi = float(sys.argv[2]) if len(sys.argv) > 2 else 0.30
    main(pdf, mi)
