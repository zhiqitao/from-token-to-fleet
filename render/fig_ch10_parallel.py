#!/usr/bin/env python3
"""fig-10-1001: The five parallelization strategies and what each splits.

A compact comparison MATRIX, not five repeated fan-out diagrams.

PUBLICATION-REDESIGN (review): the matrix concept is right but the earlier cell
text was too small and the columns too narrow, so the data columns read as cramped
annotation texture and the strategy pill clipped its label.  Layout now uses
point-based columns sized to the MEASURED cell text widths (monospaced no more),
so every cell sits in its own non-overlapping column at a comfortably readable
9.0pt, and the strategy pill is wide enough for the longest label ("EP · experts").
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

BOLD = FontProperties(weight='bold')
FS  = 8.5            # data-cell font (comfortably above the 7.5pt floor)
FSC = 9.2            # header font
W   = 439.2          # 6.1in column, in points (data coords = points)

rows = [
    ("TP · tensor",    "W weights (rows)", "activations", "partial sums → all-reduce"),
    ("PP · pipeline",  "transformer layers", "hidden states", "hidden states (P2P)"),
    ("DP · data",      "data batch", "model + optimizer", "gradients → all-reduce"),
    ("EP · experts",   "MoE experts", "attention / weights", "routes → all-to-all"),
    ("CP · context",   "token sequence", "model weights", "KV (ring)"),
]

def cellw(s): return TextPath((0, 0), s, size=FS, prop=BOLD).get_extents().width + 2

# measured column widths
w_strat  = max(cellw(r[0]) for r in rows) + 4     # + pill room
w_split  = max(cellw(r[1]) for r in rows)
w_repl   = max(cellw(r[2]) for r in rows)
w_comm   = max(cellw(r[3]) for r in rows)

# left anchors, with a gutter between columns
gap = 12
x0 = 12
x_strat = x0
x_split = x_strat + w_strat + gap
x_repl  = x_split + w_split + gap
x_comm  = x_repl + w_repl + gap
right   = x_comm + w_comm + 10
assert right <= W, f"columns overflow {right:.0f} > {W}"

H = W * 0.72
fig, ax = plt.subplots(figsize=(W/72, H/72))
fig._hermes_print_sized = True
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

# ---- column dividers + headers ----
hdr_y = H - 22
div_y0, div_y1 = 30, H - 38
for xd in (x_split - gap/2, x_repl - gap/2, x_comm - gap/2):
    ax.plot([xd, xd], [div_y0, div_y1], color='#d0d0d0', lw=0.8, zorder=0)
ax.text(x_strat, hdr_y, 'STRATEGY',    fontsize=FSC, fontweight='bold', color='#1a1a1a', ha='left', va='center')
ax.text(x_split, hdr_y, 'WHAT SPLITS', fontsize=FSC, fontweight='bold', color='#27408b', ha='left', va='center')
ax.text(x_repl,  hdr_y, 'REPLICATED',  fontsize=FSC, fontweight='bold', color='#555',    ha='left', va='center')
ax.text(x_comm,  hdr_y, 'COMMUNICATE', fontsize=FSC, fontweight='bold', color='#c0392b', ha='left', va='center')

row_colors = ['#27408b', '#3a6ea5', '#4d8fc4', '#6aa0d8', '#8fb8e0']
row0 = div_y1 - 34; dh = 44
for i, (strat, part, repl, comm) in enumerate(rows):
    y = row0 - i*dh
    ax.add_patch(FancyBboxPatch((x_strat-4, y-16), w_strat+4, 32,
                                boxstyle='round,pad=0.02', fc=row_colors[i], ec='none', zorder=1))
    ax.text(x_strat, y, strat, fontsize=FS-0.2, fontweight='bold',
            color='white', ha='left', va='center', zorder=2)
    ax.text(x_split, y, part, fontsize=FS, color='#222', ha='left', va='center')
    ax.text(x_repl,  y, repl, fontsize=FS, color='#444', ha='left', va='center')
    ax.text(x_comm,  y, comm, fontsize=FS, color='#a53226', ha='left', va='center')

# ---- footnote ----
ax.text(x0, 8, 'The only difference is which of the three is split, replicated, or exchanged.',
        fontsize=FSC-1.6, color='#666', va='center')

out = 'design/manuscript/chapter-10/figures/fig-10-1001.png'
plt.savefig(out, dpi=170)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-10/figures/fig-10-1001.pdf', format='pdf')
plt.close()
print('wrote fig-10-1001 (matrix, point-sized columns: splits=%.0f repl=%.0f comm=%.0f)' %
      (w_split, w_repl, w_comm))
