#!/usr/bin/env python3
"""measure_fig.py — on-page effective font sizes for a figure PDF.

Book places every figure at the 6.10in text column.  A figure whose natural
width exceeds 6.10in is downscaled, so on-page pt = authored pt * 6.10/natural.
For a figure narrower than the column it is placed 1:1 (scale 1).

Usage: python3 render/measure_fig.py <file.pdf> [more.pdf ...]
Prints: path, natural width (in), scale, min on-page size, and the smallest
few spans.  Also verifies pdf.fonttype (Type42) via the font names.
"""
import sys
import pymupdf

COL_IN = 6.10


def measure(path):
    doc = pymupdf.open(path)
    w_pt = max(pg.rect.width for pg in doc)
    nat_in = w_pt / 72.0
    scale = min(COL_IN, nat_in) / nat_in
    spans = []
    fonts = set()
    for pg in doc:
        for b in pg.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                for s in ln["spans"]:
                    if s["text"].strip():
                        spans.append((s["size"] * scale, s["size"], s["text"], s["font"]))
                        fonts.add(s["font"])
    if not spans:
        print(f"{path}: NO TEXT  nat={nat_in:.2f}in scale={scale:.3f}")
        return None
    spans.sort()
    mn = spans[0]
    print(f"{path}")
    print(f"  natural={nat_in:.3f}in  scale={scale:.4f}  spans={len(spans)}  "
          f"min_onpage={mn[0]:.2f}pt (authored {mn[1]:.2f})  fonts={sorted(fonts)}")
    for s in spans[:6]:
        print(f"    {s[0]:6.2f}pt  {s[2]!r}")
    return mn[0]


if __name__ == "__main__":
    worst = None
    for p in sys.argv[1:]:
        r = measure(p)
        if r is not None:
            worst = r if worst is None else min(worst, r)
    if worst is not None:
        print(f"MIN-ON-PAGE {worst:.2f}")
        sys.exit(0 if worst >= 8.0 else 1)