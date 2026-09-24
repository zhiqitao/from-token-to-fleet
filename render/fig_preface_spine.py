#!/usr/bin/env python3
"""Preface Fig 1 — the architect's decision loop (the book's spine).

Replaces the Archify 'spine-decision-loop' asset, whose transition labels
(define/size/justify/iterate) collided with the card borders and left-side
connector, and whose layout read as a stacked waterfall rather than a loop.
This matplotlib version draws an unmistakable 4-stage CYCLE: Understand ->
Design & size -> Validate & Defend -> Commit, with the return edge (Commit ->
Understand) drawn as a bold visible arrow up the left and each transition
label placed in the clear whitespace BETWEEN cards, clear of every border
and connector.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(6.1, 6.6))
fig._hermes_print_sized = True
ax.set_xlim(0, 11); ax.set_ylim(0, 12.0); ax.axis('off')

stages = [
    ('01 · Understand', 'requirements & workload', 'inputs', '#eef1f5'),
    ('02 · Design & size', 'candidates, benchmark, bottleneck', 'design', '#e4f0e4'),
    ('03 · Validate & Defend', 'TCO, recommendation', 'economics', '#ece8f7'),
    ('04 · Commit', 'red team, then final choice', 'decide', '#f7e6e8'),
]
# Vertical stack (top to bottom) with a WHITE gap between cards for the label.
CX = 5.0
CARD_W = 8.0
CARD_H = 1.9
GAP = 0.9
top = 10.9
ys = []
y = top
for _ in stages:
    ys.append(y)
    y -= (CARD_H + GAP)

colors = ['#3a6ea5', '#2f6f4f', '#6f4fa0', '#a53226']

# forward connector (Understand -> ... -> Commit) drops down the CENTER of the cards,
# from the bottom-center of one card to the top-center of the next (so the loop reads
# symmetric: forward flow down the middle, iterate return up the right).
for i in range(3):
    ax.add_patch(FancyArrowPatch((CX, ys[i] - CARD_H), (CX, ys[i+1]),
                 arrowstyle='-|>', mutation_scale=14, lw=2.2, color='#555', zorder=1))
# return edge Commit -> Understand: hook out from the MIDDLE of Commit's right edge,
# run up the far right, and land on the MIDDLE of Understand's right edge (symmetric),
# with a clear arrowhead that closes the loop.
from matplotlib.path import Path
ret_x = CX + CARD_W/2 + 1.0
ret_verts = [(CX + CARD_W/2, ys[3] - CARD_H/2), (ret_x, ys[3] - CARD_H/2),
             (ret_x, ys[0] - CARD_H/2), (CX + CARD_W/2, ys[0] - CARD_H/2)]
ret_codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO]
ax.add_patch(FancyArrowPatch(path=Path(ret_verts, ret_codes), arrowstyle='-|>',
             mutation_scale=18, lw=2.6, color='#c0392b', zorder=1))

for (name, sub, foot, fill), yy, col in zip(stages, ys, colors):
    ax.add_patch(FancyBboxPatch((CX - CARD_W/2, yy - CARD_H), CARD_W, CARD_H,
                 boxstyle='round,pad=0.02,rounding_size=0.25',
                 fc=fill, ec=col, lw=1.8, zorder=2))
    ax.text(CX - CARD_W/2 + 0.35, yy - 0.50, name, fontsize=11, fontweight='bold',
            color=col, va='center', zorder=3)
    ax.text(CX - CARD_W/2 + 0.35, yy - 1.05, sub, fontsize=8.5, color='#555',
            va='center', zorder=3)
    ax.text(CX + CARD_W/2 - 0.35, yy - 0.65, foot, fontsize=8.5, color=col,
            ha='right', va='center', style='italic', zorder=3)

# transition labels in the clear GAP between cards (beside the centered forward arrow)
trans = ['define', 'size', 'justify']
for i, lab in enumerate(trans):
    gy = ys[i] - CARD_H - GAP/2
    ax.text(CX + 0.20, gy, lab, fontsize=9, color='#555', ha='left', va='center',
            fontweight='bold', zorder=3)
# iterate label on the return edge
ax.text(CX + CARD_W/2 + 1.55, (ys[0] - CARD_H + ys[3]) / 2, 'iterate', fontsize=9,
        color='#c0392b', ha='center', va='center', fontweight='bold', rotation=90, zorder=3)

ax.text(CX, top + 0.35, "the architect's decision loop (the book's spine)", fontsize=11,
        fontweight='bold', ha='center', color='#1a1a1a')

plt.tight_layout(pad=0.2)
plt.savefig('render/latex/assets/spine-decision-loop.png', dpi=200, bbox_inches='tight')
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('render/latex/assets/spine-decision-loop.pdf', format='pdf', bbox_inches='tight')
plt.close()
print('wrote spine-decision-loop.png/.pdf (matplotlib cycle)')
