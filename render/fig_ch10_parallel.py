#!/usr/bin/env python3
"""fig-10-1001: The five parallelization strategies and what each splits.

A compact comparison MATRIX, not five repeated fan-out diagrams.

PASS-23b design decision: the earlier versions drew five near-identical
parent->3-children fan-outs, so (a) the reader had to read captions to learn what
DIFFERS between TP/PP/DP/EP/CP, and (b) the figure had to be very tall to hold all
five, so its text fell below comfortable print size.  Both fail the book-quality bar.

The insight the figure must carry is the DIFFERENCE, so we draw a matrix: one row
per strategy (TP/PP/DP/EP/CP), three labelled columns (WHAT SPLITS / REPLICATED /
COMMUNICATE).  Reading down a column shows how each axis changes across strategies;
reading across a row gives one strategy's full trade-off.  This is legible at the
6.1in column width and directly encodes the causal difference.  Grayscale-safe via
edge hue per row.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

FS = 8.6
W = 6.1

rows = [
    ("TP · tensor",    "W weights (rows)", "activations", "partial sums → all-reduce"),
    ("PP · pipeline",  "transformer layers", "hidden states", "hidden states (P2P)"),
    ("DP · data",      "data batch", "model + optimizer", "gradients → all-reduce"),
    ("EP · experts",   "MoE experts", "attention / weights", "routes → all-to-all"),
    ("CP · context",   "token sequence", "model weights", "KV (ring)"),
]

fig, ax = plt.subplots(figsize=(W, W*0.62))
# Mark as print-size-authored so regen_figs.py does NOT font-boost + reflow it
# (boosting these fixed pill boxes clips the strategy labels). Mirrors the
# fig_ch18_routing exemption.
fig._hermes_print_sized = True
ax.set_xlim(0, 11.8); ax.set_ylim(0, 6.2); ax.axis('off')

# column headers
hdr_y = 5.7
# faint vertical column dividers so the four columns read unambiguously
for xd in (2.3, 4.6, 7.9):
    ax.plot([xd, xd], [0.85, 5.55], color='#d0d0d0', lw=0.8, zorder=0)
ax.text(0.2, hdr_y, 'STRATEGY', fontsize=FS, fontweight='bold', color='#1a1a1a', ha='left', va='center')
ax.text(2.4, hdr_y, 'WHAT SPLITS', fontsize=FS, fontweight='bold', color='#27408b', ha='left', va='center')
ax.text(4.7, hdr_y, 'REPLICATED', fontsize=FS, fontweight='bold', color='#555', ha='left', va='center')
ax.text(8.0, hdr_y, 'COMMUNICATE', fontsize=FS, fontweight='bold', color='#c0392b', ha='left', va='center')

row_colors = ['#27408b', '#3a6ea5', '#4d8fc4', '#6aa0d8', '#8fb8e0']
y0 = 4.7; dh = 0.92
for i, (strat, part, repl, comm) in enumerate(rows):
    y = y0 - i*dh
    ax.add_patch(FancyBboxPatch((0.1, y-0.34), 2.2, 0.7, boxstyle='round,pad=0.02',
                                fc=row_colors[i], ec='none'))
    ax.text(0.25, y, strat, fontsize=FS-0.5, fontweight='bold', color='white', ha='left', va='center')
    ax.text(2.4, y, part, fontsize=FS-0.9, color='#222', ha='left', va='center')
    ax.text(4.7, y, repl, fontsize=FS-0.9, color='#444', ha='left', va='center')
    ax.text(8.0, y, comm, fontsize=FS-0.9, color='#a53226', ha='left', va='center')

# footnote
ax.text(0.1, 0.25, 'The only difference between the strategies is WHICH of these three things is split vs replicated, and what is exchanged. '
        'Compose them (DP x TP x PP, or TP+CP in a decode pool + prefill pool). [ILLUSTRATIVE conceptual]',
        fontsize=FS-1.4, color='#666', va='center')

out = 'design/manuscript/chapter-10/figures/fig-10-1001.png'
plt.savefig(out, dpi=170)
plt.close()
print('wrote fig-10-1001 (comparison matrix)')
