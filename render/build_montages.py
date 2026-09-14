#!/usr/bin/env python3
"""Build page-numbered contact-sheet montages from the rendered page PNGs.

Reads ~/fleet-review/pages/pg-NNN.png (90 DPI), lays them in a 5x5 grid of
5 sheets per page (25 pages/sheet), stamps a red 'p<N>' label in each cell
top-left, writes gsheet<N>.png. Runs on oci2 in ~/fleet-review.
"""
import glob, os, re
from PIL import Image, ImageDraw

def num(p):
    m = re.search(r"pg-(\d+)\.png", p)
    return int(m.group(1))

pages = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ".", "pages", "pg-*.png")), key=num)
COLS, ROWS = 5, 5
PER = COLS * ROWS
thumb_w, thumb_h = 230, 340
import PIL
print("pages:", len(pages))
for s in range((len(pages) + PER - 1) // PER):
    chunk = pages[s * PER:(s + 1) * PER]
    cols, rows = COLS, ROWS
    # build a canvas
    W = cols * thumb_w
    H = rows * thumb_h
    sheet = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(sheet)
    for i, p in enumerate(chunk):
        im = Image.open(p).convert("RGB")
        im.thumbnail((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = c * thumb_w
        y = r * thumb_h
        sheet.paste(im, (x, y))
        pgid = num(p)
        # red page label
        d.rectangle([x, y, x + 58, y + 20], fill="white")
        d.text((x + 3, y + 3), "p%d" % pgid, fill="red")
    out = "gsheet%d.png" % s
    sheet.save(out)
    print("wrote", out, sheet.size)
