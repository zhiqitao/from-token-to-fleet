#!/usr/bin/env python3
"""fig-10-1001: Three-panel TP / PP / DP topology — one parallelism pattern per panel.

REVIEWER DEMAND (Fig 10.1): the old single "composition" crammed a GPU mesh, a
partitioned/replicated/communication table, and every label into one canvas, so
the reader had to decode the topologies from tiny boxes and the summary table
competed with the diagram.  This replaces it with a CLEAN THREE-PANEL
decomposition:

  Panel A  tensor parallel (TP)   -- shards one layer's weights
  Panel B  pipeline parallel (PP) -- splits the layer stack into stages
  Panel C  data parallel (DP)     -- replicates the model, shards the batch

Each panel is a full-column-width card (~4x the old cell area), carries only a
one-line title and a one-line communication/where footer; the manuscript caption
carries the partitioned / replicated / communication detail that used to clutter
the figure.  Colour follows the book's code: weights/memory = blue,
GPU/compute = orange, data = green, communication = red.

Authored at the exact 6.1in print column (fig._hermes_print_sized) so regen_figs
places it 1:1 and never re-boosts the fonts into the fixed boxes.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BLUE_F, BLUE_E   = '#d6e2f4', '#27408b'   # weights / memory
ORAN_F, ORAN_E   = '#fbe3c8', '#c0761a'   # GPU / compute
GREEN_F, GREEN_E = '#d8efdd', '#2e9e63'   # data / batch
RED              = '#c0392b'              # communication
INK, MUTE        = '#1a1a1a', '#666666'

# ---- print-size authoring (6.1in column) --------------------------------
W_IN, H_IN = 6.1, 6.45
fig, ax = plt.subplots(figsize=(W_IN, H_IN))
fig._hermes_print_sized = True
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
X, Y = 61.0, 64.5                 # 1 data unit = 0.1 in
ax.set_xlim(0, X); ax.set_ylim(0, Y); ax.axis('off')


def card(y0):
    """Panel card (x 1..60) with bottom edge at y0, height 18.5."""
    ax.add_patch(FancyBboxPatch((1.0, y0), 59.0, 18.5,
                                boxstyle='round,pad=0.05,rounding_size=0.4',
                                fc='#fcfcfc', ec='#dcdcdc', lw=1.0, zorder=0))
    ax.plot([3.0, 58.0], [y0 + 15.4, y0 + 15.4], color='#ededed', lw=0.8, zorder=1)


def cbox(x0, y0, w, h, fc, ec, lw=1.3, z=2):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h,
                                boxstyle='round,pad=0.05,rounding_size=0.25',
                                fc=fc, ec=ec, lw=lw, zorder=z))


def txt(x, y, s, size=9.0, color=INK, weight='normal', ha='center', z=4):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
            ha=ha, va='center', zorder=z)


def arrow(x0, y0, x1, y1, color, lw=1.4, style='-|>', z=3):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style,
                                 mutation_scale=11, lw=lw, color=color,
                                 shrinkA=0, shrinkB=0, zorder=z))


# ======================================================================
# Panel A — TENSOR PARALLEL (TP): shards one layer's weights
# ======================================================================
yA = 44.5
card(yA)
txt(3.0, yA + 16.5, 'A · Tensor parallel (TP) — splits one layer’s weights',
    size=10.5, weight='bold', ha='left')
# weight matrix, split in half
cbox(9.0, yA + 11.2, 43.0, 2.4, BLUE_F, BLUE_E)
ax.plot([30.5, 30.5], [yA + 11.2, yA + 13.6], ls='--', color=BLUE_E, lw=1.2, zorder=3)
txt(19.5, yA + 12.4, 'W₀', size=9.5, color=BLUE_E, weight='bold')
txt(41.5, yA + 12.4, 'W₁', size=9.5, color=BLUE_E, weight='bold')
txt(30.5, yA + 14.7, 'one layer’s weight matrix W', size=8.5, color=MUTE)
# the two GPUs that each hold one shard
cbox(9.0, yA + 6.5, 20.0, 3.2, ORAN_F, ORAN_E)
cbox(32.0, yA + 6.5, 20.0, 3.2, ORAN_F, ORAN_E)
txt(19.0, yA + 8.1, 'GPU 0', size=9.5, weight='bold', color='#7a4a08')
txt(42.0, yA + 8.1, 'GPU 1', size=9.5, weight='bold', color='#7a4a08')
arrow(19.0, yA + 11.2, 19.0, yA + 9.7, ORAN_E)
arrow(42.0, yA + 11.2, 42.0, yA + 9.7, ORAN_E)
# all-reduce of the partial sums
cbox(17.0, yA + 4.5, 27.0, 1.5, '#ffffff', RED, lw=1.3)
txt(30.5, yA + 5.25, 'all-reduce partial sums  →  full output', size=8.6, color=RED)
arrow(19.0, yA + 6.5, 22.5, yA + 6.0, RED)
arrow(42.0, yA + 6.5, 38.5, yA + 6.0, RED)
txt(3.0, yA + 2.3, 'communication: all-reduce every layer  →  on-node only (NVLink)',
    size=8.5, color=MUTE, ha='left')

# ======================================================================
# Panel B — PIPELINE PARALLEL (PP): splits the layer stack into stages
# ======================================================================
yB = 26.0
card(yB)
txt(3.0, yB + 16.5, 'B · Pipeline parallel (PP) — splits the layer stack',
    size=10.5, weight='bold', ha='left')
stages = [(5.0, 'GPU 0', 'layers 1–8'), (22.5, 'GPU 1', 'layers 9–16'), (40.0, 'GPU 2', 'layers 17–24')]
for x0, g, lay in stages:
    cbox(x0, yB + 7.0, 15.0, 5.0, ORAN_F, ORAN_E)
    txt(x0 + 7.5, yB + 10.5, g, size=9.5, weight='bold', color='#7a4a08')
    txt(x0 + 7.5, yB + 8.4, lay, size=8.6, color='#7a4a08')
arrow(20.0, yB + 9.5, 22.5, yB + 9.5, RED)
arrow(37.5, yB + 9.5, 40.0, yB + 9.5, RED)
txt(30.0, yB + 13.3, 'activations  →  P2P at stage boundaries', size=8.5, color=MUTE)
# the pipeline bubble: stage 1 idle while the pipeline fills / drains
ax.add_patch(FancyBboxPatch((5.0, yB + 4.7), 15.0, 1.4,
                            boxstyle='round,pad=0.05,rounding_size=0.2',
                            fc='#f2f2f2', ec='#b8b8b8', lw=0.9, ls='--', zorder=1))
txt(12.5, yB + 5.4, 'idle (bubble) at fill/drain', size=8.5, color=MUTE)
txt(3.0, yB + 2.3, 'communication-light: only stage boundaries move  →  spans nodes',
    size=8.5, color=MUTE, ha='left')

# ======================================================================
# Panel C — DATA PARALLEL (DP): replicates the model, shards the batch
# ======================================================================
yC = 3.5
card(yC)
txt(3.0, yC + 16.5, 'C · Data parallel (DP) — splits the data batch',
    size=10.5, weight='bold', ha='left')
# data shards
cbox(9.0, yC + 11.6, 20.0, 2.2, GREEN_F, GREEN_E)
cbox(32.0, yC + 11.6, 20.0, 2.2, GREEN_F, GREEN_E)
txt(19.0, yC + 12.7, 'batch shard A', size=9.0, color=GREEN_E, weight='bold')
txt(42.0, yC + 12.7, 'batch shard B', size=9.0, color=GREEN_E, weight='bold')
# two GPU replicas, each holding the whole model
cbox(9.0, yC + 6.3, 20.0, 4.0, ORAN_F, ORAN_E)
cbox(32.0, yC + 6.3, 20.0, 4.0, ORAN_F, ORAN_E)
txt(19.0, yC + 9.0, 'GPU 0', size=9.5, weight='bold', color='#7a4a08')
txt(42.0, yC + 9.0, 'GPU 1', size=9.5, weight='bold', color='#7a4a08')
txt(19.0, yC + 7.4, 'full model (replica)', size=8.6, color=BLUE_E)
txt(42.0, yC + 7.4, 'full model (replica)', size=8.6, color=BLUE_E)
arrow(19.0, yC + 11.6, 19.0, yC + 10.3, GREEN_E)
arrow(42.0, yC + 11.6, 42.0, yC + 10.3, GREEN_E)
arrow(29.0, yC + 8.3, 32.0, yC + 8.3, RED, style='<|-|>')
txt(30.5, yC + 5.1, 'gradients ↔ all-reduce (training only)', size=8.5, color=RED)
txt(3.0, yC + 2.3, 'inference: independent replicas, no sync  ·  throughput scales linearly',
    size=8.5, color=MUTE, ha='left')

# ---- shared colour legend (redundant channel: label text, not hue alone) ----
txt(30.5, 1.6, 'blue = weights · orange = GPU · green = data · red = comms',
    size=8.5, color=MUTE)

# ---- guard: no text may run outside the 6.1in column ------------------------
fig.canvas.draw()
_ren = fig.canvas.get_renderer()
_axbb = ax.get_window_extent(_ren)
for _t in ax.texts:
    _bb = _t.get_window_extent(_ren)
    if _bb.x0 < _axbb.x0 - 0.5 or _bb.x1 > _axbb.x1 + 0.5:
        print('OVERFLOW-X:', repr(_t.get_text()[:45]),
              'x=[%.1f,%.1f]' % (_bb.x0, _bb.x1), 'col x=[%.1f,%.1f]' % (_axbb.x0, _axbb.x1))

out_png = 'design/manuscript/chapter-10/figures/fig-10-1001.png'
fig.savefig(out_png, dpi=200)
with matplotlib.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    fig.savefig('design/manuscript/chapter-10/figures/fig-10-1001.pdf', format='pdf')
plt.close()
print('wrote fig-10-1001 (three-panel TP/PP/DP)')
