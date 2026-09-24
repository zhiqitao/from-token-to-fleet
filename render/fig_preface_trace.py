#!/usr/bin/env python3
"""Preface Fig 2 — two ways to read the book (REDESIGN).

The prior 'preface-trace' figure crammed all 26 chapters + appendix into six small
Part boxes, so the layering-by-parts vs quantity-to-decision contrast faded into a wall
of tiny text. This version rebuilds it as TWO LARGE EXPLICIT PATHS side by side, each a
coarse 6-step walk with far fewer words (the per-chapter detail lives in the TOC/prose):

  LEFT  — "Read layer-by-layer (Parts)"  : Part I -> II -> ... -> VI, each a single card.
  RIGHT — "Read by question (traceability)": a concrete quantity -> decision chain
          (token -> cost & KV floor -> fits host? -> which phase binds? -> few or many
          hosts? -> who serves it?) that traces how one quantity cascades, so the
          two reading modes are spatially distinct at a glance.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(6.1, 5.6))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.set_xlim(0, 20); ax.set_ylim(0, 11.6); ax.axis('off')

# Title
ax.text(10, 11.25, 'Read the book two ways', fontsize=13, fontweight='bold', ha='center', color='#1a1a1a')
ax.text(10, 10.7, 'layer-by-layer (Parts), or question-by-question (traceability)', fontsize=9,
        ha='center', color='#555', style='italic')

# ---- LEFT PATH: layer-by-layer ----
LX0, LW = 0.6, 8.4
ax.text(LX0 + LW/2, 9.9, 'A · LAYER-BY-LAYER  (Parts I → VI)', fontsize=10,
        fontweight='bold', ha='center', color='#27408b')
parts = [
    'I · The Token', 'II · The Workload', 'III · The System',
    'IV · The Architecture', 'V · The Fleet', 'VI · The Architect',
]
yp = 9.4
ph = 1.05
pgap = 0.32
for i, p in enumerate(parts):
    yb = yp - i*(ph+pgap) - ph
    ax.add_patch(FancyBboxPatch((LX0, yb), LW, ph, boxstyle='round,pad=0.02,rounding_size=0.18',
                                fc='#eaf1fb', ec='#3a6ea5', lw=1.6))
    ax.text(LX0 + LW/2, yb + ph/2, p, fontsize=10, fontweight='bold', ha='center',
            va='center', color='#27408b')
    if i < 5:
        # arrow in the left margin pointing DOWN: Part I -> II -> ... -> VI (top-to-bottom,
        # matching the stated "Parts I -> VI" order)
        ax.add_patch(FancyArrowPatch((LX0 - 0.5, yb), (LX0 - 0.5, yb - pgap),
                     arrowstyle='-|>', mutation_scale=13, lw=1.8, color='#555'))
ax.text(LX0 + LW/2, 0.62, 'build the substrate, then the discipline', fontsize=8,
        ha='center', color='#555', style='italic')

# ---- RIGHT PATH: question-by-question (traceability) ----
RX0, RW = 11.2, 8.2
ax.text(RX0 + RW/2, 9.9, 'B · QUESTION-BY-QUESTION', fontsize=10,
        fontweight='bold', ha='center', color='#c0392b')
steps = [
    ('token → cost', 'Ch1'),
    ('fits host? → KV', 'Ch3/7'),
    ('which phase binds?', 'Ch2/8'),
    ('1 host or fleet?', 'Ch17'),
    ('who serves it?', 'Ch18'),
    ('is it the right call?', 'Ch21/26'),
]
for i, (q, ch) in enumerate(steps):
    yb = 9.4 - i*(ph+pgap) - ph
    ax.add_patch(FancyBboxPatch((RX0, yb), RW, ph, boxstyle='round,pad=0.02,rounding_size=0.18',
                                fc='#fdecea', ec='#c0392b', lw=1.6))
    ax.text(RX0 + 0.35, yb + ph/2, q, fontsize=9.5, fontweight='bold', ha='left',
            va='center', color='#7b241c')
    ax.text(RX0 + RW - 0.35, yb + ph/2, ch, fontsize=8.5, ha='right', va='center', color='#a53226')
    if i < 5:
        # arrow in the right margin pointing DOWN: token -> cost -> ... (top-to-bottom,
        # matching the stated "token -> cost -> KV -> ..." trace direction)
        ax.add_patch(FancyArrowPatch((RX0 + RW + 0.5, yb), (RX0 + RW + 0.5, yb - pgap),
                     arrowstyle='-|>', mutation_scale=13, lw=1.8, color='#c0392b'))
ax.text(RX0 + RW/2, 0.62, 'each question → the chapter that answers it', fontsize=8,
        ha='center', color='#555', style='italic')

plt.tight_layout()
plt.savefig('render/latex/assets/preface-trace.png', dpi=200, bbox_inches='tight')
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('render/latex/assets/preface-trace.pdf', format='pdf', bbox_inches='tight')
plt.close()
print('wrote preface-trace.png/.pdf (two-path redesign)')
