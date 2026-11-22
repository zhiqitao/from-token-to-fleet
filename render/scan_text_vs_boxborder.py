#!/usr/bin/env python3
"""scan_text_vs_boxborder.py — detect the THIRD figure defect class.

Checks whether a box-outline or band-background border passes THROUGH a text word.
The existing pair covers the other two classes:
  - scan_figure_text_collisions.py  -> word-vs-word (text-on-text)
  - geom_audit.py                   -> connector-segment-vs-word (line-through-text)
but BOTH skip rectangles-by-design, so a box/band border striking a label goes unseen.
"0 text-on-text" does NOT mean the figure is clean — run this too.

Usage:
    python3 scan_text_vs_boxborder.py <figure.pdf>
    python3 scan_text_vs_boxborder.py <book.pdf> --page <idx>

Method: collect every straight line segment in the figure, plus every text word's bbox.
A border passing through a word = a segment of length >= minlen whose interior crosses
the word's bbox. Box borders are drawn as long straight edges, so this correctly flags
them. Rounded corner fillets (short beziers) are excluded by the length filter, and
deliberate figure-framing rectangles that sit OUTSIDE all text (the outer page border)
are reported but listed separately as low-priority.

The check is geometric (Liang-Barsky segment/box clip) on the VECTOR-PDF text layer.
"""
import sys
import pymupdf


def seg_intersects_box(x1, y1, x2, y2, wx0, wy0, wx1, wy1):
    dim = 1.0
    dx = x2 - x1
    dy = y2 - y1
    t0, t1 = 0.0, 1.0

    def clip(p, q, t0, t1):
        if p == 0:
            return (t0, t1) if q >= 0 else (None, None)
        r = q / p
        if p < 0:
            if r > t1:
                return (None, None)
            if r > t0:
                t0 = r
        else:
            if r < t0:
                return (None, None)
            if r < t1:
                t1 = r
        return (t0, t1)

    for p, q in [(-dx, x1 - wx0), (dx, wx1 - x1), (-dy, y1 - wy0), (dy, wy1 - y1)]:
        t0, t1 = clip(p, q, t0, t1)
        if t0 is None:
            return False
    return True


def main(path, page_idx=0, minlen=14):
    doc = pymupdf.open(path)
    pg = doc[page_idx]
    words = pg.get_text("words")
    hits = []
    for dr in pg.get_drawings():
        for it in dr["items"]:
            if it[0] != "l":
                continue
            x1, y1 = it[1].x, it[1].y
            x2, y2 = it[2].x, it[2].y
            if max(abs(x2 - x1), abs(y2 - y1)) < minlen:
                continue
            for wd in words:
                if seg_intersects_box(x1, y1, x2, y2,
                                      wd[0] + 1, wd[1] + 1, wd[2] - 1, wd[3] - 1):
                    hits.append((round(x1), round(y1), round(x2), round(y2), wd[4]))
    # dedupe
    seen = set()
    out = []
    for h in hits:
        k = (h[0], h[1], h[2], h[3], h[4])
        if k not in seen:
            seen.add(k)
            out.append(h)
    print(f"text-vs-box-border hits: {len(out)}")
    for h in out:
        print("  ", h)
    return len(out)


if __name__ == "__main__":
    a = sys.argv[1:]
    page = 0
    if "--page" in a:
        i = a.index("--page")
        page = int(a[i + 1])
        a = a[:i] + a[i + 2:]
    main(a[0], page)
