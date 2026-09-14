#!/usr/bin/env python3
"""Reflow fig-1-2-token-travel (5-lane single row) into 2 rows (3 + 2).

Row 1: Text(100) Tokenizer(315) Embedding(530)
Row 2: Attention(100) KV-cache(315)
Flow reads: Text -> Tokenizer -> Embedding -> (down) -> Attention -> KV-cache.

We move lane3 (Attention) & lane4 (KV) elements down by DY and snap their x to
the row-1 column positions, then rewrite the two connectors that involve them:
  f4 (emb->attn): from embedding row1 -> down -> attention row2 (elbow)
  f5 (attn->kv):  horizontal within row2
Also rewrite their edge-label chips and the arrowhead target positions.
"""
import re

PATH = "render/archify/fig-1-2-token-travel-min.html"
t = open(PATH, encoding="utf-8").read()

DY = 562
# lane3 (Attention) moves to col0 (x-center 100); lane4 (KV) to col1 (x-center 315)
# Note: emb->attn arrow currently at y=271. Row2 nodes place their box y at 239+562=801.
# We'll place row2 node box center-line at the same relative y as row1 (y 239..303 -> center 271+562=833).
# So attention node at x 38.4..161.6 (center100) y 801.1..864.9 ; kv node at x 253.4..376.6 y 801.1..864.9.

def xmap(v):
    v=float(v)
    # lane3 elements (x near 745 center, span 652.6-837.4, plus edge chip 805.5-899.6)
    if 640-30 <= v <= 867+40:
        # map to col0: offset so center 745 -> 100
        return v - 645
    if 890 <= v <= 1030:
        # lane4 elements (center 960) -> col1 (center315): -645
        return v - 645
    return v

def ymap(v):
    v=float(v)
    # elements belonging to moved lanes: shift down
    return v + DY

# Move all element x/y for lane3/lane4 by doing targeted replaces.
# Strategy: process the whole svg; for each element, if its x is in a moved
# lane's span, shift both x and y.
def reflow(m):
    tag=m.group(1); inner=m.group(2)
    xm=re.search(r'\bx="([-0-9.]+)"', inner)
    if not xm:
        return m.group(0)
    x=float(xm.group(1))
    moved = (640-30 <= x <= 1030)
    if not moved:
        return m.group(0)
    inner=inner.replace('x="%s"'%xm.group(1), 'x="%.1f"'%xmap(x))
    ym=re.search(r'\by="([-0-9.]+)"', inner)
    if ym:
        inner=inner.replace('y="%s"'%ym.group(1), 'y="%.1f"'%ymap(float(ym.group(1))))
    return "<%s%s>"%(tag,inner)

svg_orig=re.search(r"<svg.*?</svg>", t, re.S).group(0)
svg2=re.sub(r'<(rect|text|path)\b([^>]*?)/?>', reflow, svg_orig)

# --- rewrite connector f4 (emb->attn) and f5 (attn->kv) ---
# f4: from embedding(row1, x~586,y271) to attention(row2 col0 center100, node right edge x161.6,y833)
f4_old=r'<path data-edge-from="emb" data-edge-to="attn" data-edge-label="attend" data-edge-key="3" data-edge-id="f4" data-composition-points="586,271;689,271" d="M 586 271 L 689 271"'
f4_new=r'<path data-edge-from="emb" data-edge-to="attn" data-edge-label="attend" data-edge-key="3" data-edge-id="f4" data-composition-points="586,271;586,833;161.6,833" d="M 586 271 L 586 833 L 161.6 833"'
svg2=svg2.replace(f4_old, f4_new)

# f5: attn(center100) -> kv(center315) in row2, both boxes y 801..865, center 833
f5_old=r'<path data-edge-from="attn" data-edge-to="kv" data-edge-label="append K,V" data-edge-key="4" data-edge-id="f5" data-composition-points="801,271;904,271" d="M 801 271 L 904 271"'
f5_new=r'<path data-edge-from="attn" data-edge-to="kv" data-edge-label="append K,V" data-edge-key="4" data-edge-id="f5" data-composition-points="161.6,833;253.4,833" d="M 161.6 833 L 253.4 833"'
svg2=svg2.replace(f5_old, f5_new)

# Reflow the edge-label chips/texts for f4 ("attend") and f5 ("append K,V")
# f5 chip rect was x=805.5 y=248.7 -> moved (in col1) x=160.5 y=810.7 ; its text x=852.5->207.5 y=261->823
# f4 had no chip clearly; the 'attend' text was at x=637.5 y=261 (edge label of f4, in row1) - keep near new path? 
# The 'attend' chip (rect x=587.8 y=248.7 w=99.4) is the emb->attn label at row1 embedding-right. Keep as-is (row1).
# f5 label: 'append K,V' text was x=852.5 y=261 (near kv). After move -> row2. fix text 'append K,V'
svg2=svg2.replace('<text data-detail="fine" x="852.5" y="261"','<text data-detail="fine" x="207.5" y="823"')
svg2=svg2.replace('<rect x="805.5" y="248.7" width="94.1" height="29.7"','<rect x="160.5" y="803.7" width="94.1" height="29.7"')

# update viewBox: content now taller (row2 adds ~562). original vb "-13.3 3.1 1086.6 525.8"
# new height ~ 562+484+padding = ~1100 ; width stays ~ but col0 left = -13.3
new_vb=r'viewBox="-13.3 3.1 1086.6 1100.0"'
svg2=re.sub(r'viewBox="[^"]*"', new_vb, svg2, count=1)
print("reflowed svg len",len(svg2))
open("/tmp/tt_reflowed.svg","w").write(svg2)
print("done")
