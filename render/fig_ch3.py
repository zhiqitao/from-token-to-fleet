import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

# Fig 3.1 — Dense vs MoE: distinguish ACTIVE parameters (per token) from TOTAL
# RESIDENT weights. Key correctness point: an MoE still stores all its experts;
# only the compute per token is reduced to the top-k active set.
#
# PASS-24 fix: both panels use ONE shared grid spec (same top edge, same cell
# height / row pitch), so the grids and the annotation rows register row-for-row.
# 'resident' vs 'active' is encoded by a consistent fill cue (grey=resident,
# coloured=active) in BOTH panels, not colour+text on one side only.
fig, axes = plt.subplots(1, 2, figsize=(6.1, 6.0))
fig._hermes_print_sized = True

# ---- shared grid spec: identical in both panels ----
TOP = 15.8        # top edge of row 0 (same for both)
CELL_H = 0.72     # cell height (same for both)
ROW_P = 0.95      # vertical pitch between row top edges (same for both)
NROWS = 4         # both panels draw 4 rows of cells
COLS = 6

# annotation row y-positions (shared so left/right text lines up)
A_RES = 9.6
A_ACT = 8.75
A_SENT = 7.7
A_KV = 6.5
KV_Y = 4.2


def cell_top(r):
    return TOP - r * ROW_P


def panel_setup(ax, title, color):
    ax.set_xlim(0, 10); ax.set_ylim(0, 19); ax.axis('off')
    ax.text(5, 18.3, title, fontsize=11.5, fontweight='bold', ha='center', color=color)


def legend_row(ax, y, fc, ec, text, tcolor):
    ax.add_patch(Rectangle((0.4, y), 0.5, 0.32, fc=fc, ec=ec, lw=0.8))
    ax.text(1.05, y+0.16, text, fontsize=9.2, color=tcolor, ha='left', va='center')


# ================= LEFT: Dense 70B (all resident & active) =================
ax = axes[0]
panel_setup(ax, 'Dense 70B', '#3a6ea5')
for r in range(NROWS):
    y = cell_top(r) - CELL_H
    for cc in range(COLS):
        ax.add_patch(Rectangle((0.8+cc*1.35, y), 1.1, CELL_H, fc='#3a6ea5', ec='white'))
# red bracket around ALL cells (all active)
ax.add_patch(Rectangle((0.62, cell_top(NROWS-1)-CELL_H-0.10),
                        COLS*1.35+0.55, (NROWS-1)*ROW_P+CELL_H+0.22, fc='none', ec='#c0392b', lw=2.0))
ax.text(9.0, cell_top(0)+0.42, 'ALL active', fontsize=9, color='#c0392b', ha='right', fontweight='bold')
legend_row(ax, A_RES, '#cccccc', '#888', 'resident \u2248 140 GB', '#444')
legend_row(ax, A_ACT, '#3a6ea5', '#333', 'active per token \u2248 140 GB', '#333')
ax.text(5, A_SENT, 'every token activates all 70B params', fontsize=9.0, color='#333', ha='center')
ax.text(5, A_KV, 'KV grows linearly with context', fontsize=9.0, color='#555', ha='center')

# ================= RIGHT: MoE (8 experts, top-2 active) =================
ax = axes[1]
panel_setup(ax, 'MoE (8 experts)', '#e67e22')
# 8 experts in a 3-col x 3-row arrangement (last cell of row 3 empty), same cell grid
expert_cells = [(r, c) for r in range(3) for c in range(3)][:8]   # 8 experts, not 9
activated = {(0, 0), (1, 0)}   # E1 (row0,col0), E4 (row1,col0)
for idx, (r, c) in enumerate(expert_cells):
    y = cell_top(r) - CELL_H
    active = (r, c) in activated
    fc = '#e67e22' if active else '#cccccc'
    ec = '#8a4a12' if active else '#888888'
    ax.add_patch(Rectangle((0.8+c*2.15, y), 1.9, CELL_H, fc=fc, ec=ec, lw=1.0))
    ax.text(0.8+c*2.15+0.95, y+CELL_H/2, f'E{idx+1}', ha='center', va='center', fontsize=8.6,
            color='white' if active else '#555', fontweight='bold' if active else 'normal')
# red bracket around the two active E1/E4 cells (col 0, rows 0-1)
ax.add_patch(Rectangle((0.66, cell_top(1)-CELL_H-0.10), 2.06, ROW_P+CELL_H+0.22, fc='none', ec='#c0392b', lw=2.0))
ax.text(9.0, cell_top(0)+0.42, 'top-2 active', fontsize=9, color='#c0392b', ha='right', fontweight='bold')
legend_row(ax, A_RES, '#cccccc', '#888', 'resident \u2248 full expert set', '#444')
legend_row(ax, A_ACT, '#e67e22', '#333', 'active per token \u2248 28 GB', '#333')
ax.text(5, A_SENT, 'only top-2 of 8 experts compute per token', fontsize=9.0, color='#333', ha='center')
ax.text(5, A_KV, 'KV grows linearly with context', fontsize=9.0, color='#555', ha='center')

# ---- KV bars: identical under both columns ----
for axx in axes:
    axx.add_patch(Rectangle((0.6, KV_Y), 8.8, 0.9, fc='#c0392b', ec='white'))
    axx.text(5, KV_Y+0.45, 'KV same as dense (matched attention)',
             ha='center', va='center', fontsize=8.8, color='white', fontweight='bold')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-03/figures/fig-03-0301.png', dpi=170)
plt.close()
print('wrote fig-03-0301 (aligned dual panel; consistent resident/active channel)')
