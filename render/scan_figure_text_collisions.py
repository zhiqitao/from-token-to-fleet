#!/usr/bin/env python3
"""Scan figure/built-book PDFs for TEXT-ON-TEXT COLLISIONS (word-box overlap).

The definitive way to catch a text element sitting on top of another text element
(legend over an axis title, a footnote over an axis label, an in-plot annotation
over a legend entry, a label over a box). It reads the VECTOR-PDF text layer via
pymupdf — NOT a rendered PNG — so it is authoritative and pixel-exact (the vision
model over/under-reports and cannot be trusted for this class).

Why this matters: matplotlib figures are embedded in the book as vector .pdf
siblings (regen_figs.py emits them). pymupdf extracts each figure's text with
bounding boxes, so we can detect collisions directly.

Method: for every page / figure, take all extracted word rectangles and report
pairs that (a) overlap with substantial area AND (b) are on recognizably different
text lines (y-centers differ by more than ~a word height). The line filter keeps
normal intra-line kerning from firing; without it every sentence self-reports.

Usage (single figure PDF):
    python3 scan_figure_text_collisions.py <fig.pdf> [min_iol]

Usage (every figure's own vector PDF in a repo):
    python3 scan_figure_text_collisions.py --dir <repo>/design/manuscript 0.10

Usage (a built book PDF — catches figure-vs-body AND figure-internal collisions):
    python3 scan_figure_text_collisions.py <book.pdf> 0.15

min_iol = intersection-over-union of the two word boxes, a fraction 0..1.
Pick the threshold by target: the fig 7.2 legend-over-title collision measured
~0.20-0.25; tight-but-legible legend spacing reads ~0.18-0.23 and is a FALSE
positive; compact table header-over-value spacing reads ~0.10-0.13 (also false).
Recommended: 0.15 goldilocks for a book scan, then manually eyeball each hit.

READING THE OUTPUT:
- A hit like  "'req/mo.'(x189,y329)  <->  'Requests/month'(x193,y332)"  with both
  words sharing a y-band = GENUINE overlap. The x-overlap + y-overlap is direct.
- A hit where the two words are on clearly separate lines with a small gap (e.g.
  a table header at y229-241 and its value at y238-248) = TIGHT-but-separate,
  a false positive. Confirm by checking the gap: if the word boxes share only
  ~3pt of y and the glyphs render with a visible white gap, it's fine.
- A hit on subscript/superscript math ('turns'<->'turn', 'I0'<->'in') = reduced-height
  type, a false positive. Do not chase.
"""
import sys, os, glob, itertools, pymupdf


def _overlap(a, b):
    ox = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    oy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    return ox * oy


def _area(w):
    return max(1.0, (w[2] - w[0]) * (w[3] - w[1]))


def scan_page(page, min_iol):
    ws = page.get_text("words")
    if len(ws) < 4:
        return []
    hits = []
    for a, b in itertools.combinations(ws, 2):
        ay = (a[1] + a[3]) / 2.0
        by = (b[1] + b[3]) / 2.0
        # ignore same-line kerning
        if abs(ay - by) < max(2.0, (a[3] - a[1]) * 0.30):
            continue
        o = _overlap(a, b)
        if o <= 0:
            continue
        union = _area(a) + _area(b) - o
        iol = o / union
        if iol >= min_iol:
            hits.append((iol, a[4], b[4], a, b))
    return hits


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    if "--dir" in sys.argv:
        d = args[0] if args else "."
        mi = float(args[1]) if len(args) > 1 else 0.30
        pdfs = sorted(glob.glob(os.path.join(d, "chapter-*/figures/fig-*.pdf")))
        ncoll = 0
        for p in pdfs:
            doc = pymupdf.open(p)
            hits = scan_page(doc[0], mi)
            if hits:
                ncoll += len(hits)
                print(f"\n### {os.path.basename(p)}")
                for iol, wa, wb, a, b in sorted(hits, reverse=True):
                    print(f"  [{iol:.2f}] '{wa}'(x{a[0]:.0f},y{a[1]:.0f}) <-> '{wb}'(x{b[0]:.0f},y{b[1]:.0f})")
        print(f"\nTOTAL figure text collisions: {ncoll}")
        return
    pdf = args[0]
    mi = float(args[1]) if len(args) > 1 else 0.15
    doc = pymupdf.open(pdf)
    total = 0
    for p in range(len(doc)):
        hits = scan_page(doc[p], mi)
        if hits:
            print(f"\n=== page {p} ===")
            for iol, wa, wb, a, b in sorted(hits, reverse=True)[:40]:
                total += 1
                print(f"  [{iol:.2f}] '{wa}'(x{a[0]:.0f},y{a[1]:.0f}) <-> '{wb}'(x{b[0]:.0f},y{b[1]:.0f})")
    print(f"\nTOTAL cross-element text overlaps: {total}")


if __name__ == "__main__":
    main()
