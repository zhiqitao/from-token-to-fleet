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


def panel_setup(ax, title, color, tx=5.0):
    ax.set_xlim(0, 10); ax.set_ylim(2.6, 19); ax.axis('off')
    # Loop-5 N3: the title must sit over ITS OWN grid.  The dense grid spans
    # 0.8..8.9 (centre 4.85 ~ 5) but the MoE grid spans 0.8..7.0 (centre 3.9),
    # so the right panel passes its grid centre explicitly.
    ax.text(tx, 18.3, title, fontsize=11.5, fontweight='bold', ha='center', color=color)


def legend_row(ax, y, fc, ec, text, tcolor, va='center'):
    ax.add_patch(Rectangle((0.4, y), 0.5, 0.32, fc=fc, ec=ec, lw=0.8))
    ax.text(1.05, y+0.16, text, fontsize=9.2, color=tcolor, ha='left', va=va)


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
ax.text(4.725, cell_top(0)+0.42, 'ALL active', fontsize=9, color='#c0392b', ha='center', fontweight='bold')
# Dense: every param is BOTH resident and active (140 GB), so a single blue legend
# row replaces the old grey 'resident' + blue 'active' pair — the grey swatch matched
# no cell (all cells are blue) and read as orphaned (A-015).
legend_row(ax, A_RES, '#3a6ea5', '#333', 'all 140 GB resident & active', '#333')
ax.text(5, A_SENT, 'every token activates all 70B params', fontsize=9.0, color='#333', ha='center')
ax.text(5, A_KV, 'KV grows linearly with context', fontsize=9.0, color='#555', ha='center')

# ================= RIGHT: MoE (8 experts, top-2 active) =================
ax = axes[1]
panel_setup(ax, 'MoE (8 experts)', '#e67e22', tx=3.9)   # centred over the 0.8..7.0 expert grid
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
ax.text(3.9, cell_top(0)+0.42, 'top-2 active', fontsize=9, color='#c0392b', ha='center', fontweight='bold')
legend_row(ax, A_RES, '#cccccc', '#888', 'resident weights \u2248 94 GB', '#444')
# P1-02: the ledger's per-token active-weight bytes are 12.8B x 2 = 25.6 GB
# (was a stale '~28 GB' left over from the retired 14B-active ledger).  The
# label is wrapped to two lines so it stays inside the panel column at the
# authored 9.2pt (measure_fig.py gate: min on-page >= 8.0pt, no shrinking).
legend_row(ax, A_ACT, '#e67e22', '#333', 'per-token active-weight bytes\n\u2248 25.6 GB (12.8B \u00d7 2 bytes)', '#333')
# P1-02 (caption conflation): name the two components of the 12.8B total-active
# count so it is not read as "top-2 experts alone" — always-on 1.4B + the two
# routed experts 11.4B (2 x 5.7B) = 12.8B, per Tables 3-2/3-3.
ax.text(5, A_SENT, 'per token: 11.4B top-2 + 1.4B always-on', fontsize=9.0, color='#333', ha='center')
ax.text(5, A_KV, 'KV grows linearly with context', fontsize=9.0, color='#555', ha='center')

# ---- KV bars: bytes are set by attention SHAPE, not by MoE routing ----
# Each panel is only ~2.9in wide (6.1in / 2), so the 8.8/10 bar is ~184pt. The
# label must stay under ~150pt to keep right margin. P1 (review nov1e): the old
# "KV: identical (dense = MoE)" + "same attention geometry" note claimed a
# controlled comparison the parameter ledger contradicts — the ~47B challenger's
# ~1.4B always-on implies a 32L/4096H GQA attention stack, not the dense
# 80L/8192H full-MHA one, so the two KV footprints are NOT equal (Table 3-3:
# 1.31 MB/token x 9,200 = 12.06 GB vs 0.0655 MB/token x 9,200 = 0.60 GB, 8-bit).
# The bars now state the recomputed bytes and the attribution. Width budget is
# set by the ORIGINAL figure (tight_layout sizes the axes to the widest string):
# bar text <= ~140pt inside the 154.4pt bar, note lines <= 156.9pt (the original
# widest line) -- measured: bar 133.2pt, note 149.7/150.1pt, so the axes, the bar
# and every grid cell keep their original geometry (no reflow, no font shrinking).
# Final strings (measured): bar 'dense 12 GB vs MoE 0.6 GB' 135.6pt < 154.4pt bar;
# note '8-bit KV set by shape, not routing:' 144.6pt and '80L/8192H MHA vs
# 32L/4096H GQA' 150.1pt, both < 156.9pt (the original widest line). The bar names
# both models and the note carries the precision, so '12 vs 0.6' cannot be misread
# as two precisions of one model.
for axx in axes:
    axx.add_patch(Rectangle((0.6, KV_Y), 8.8, 0.9, fc='#c0392b', ec='white'))
    axx.text(5, KV_Y+0.45, 'dense 12 GB vs MoE 0.6 GB',
             ha='center', va='center', fontsize=8.8, color='white', fontweight='bold')
    axx.text(5, KV_Y-0.55, '8-bit KV set by shape, not routing:\n80L/8192H MHA vs 32L/4096H GQA',
             ha='center', va='center', fontsize=8.4, color='#7a1f1f', style='italic')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-03/figures/fig-03-0301.png', dpi=350)
# PDF sibling (Type42 fonts) — this is what LaTeX typesets, and what
# render/measure_fig.py checks for the on-page minimum font size.
import matplotlib as _mpl
with _mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-03/figures/fig-03-0301.pdf', format='pdf')
plt.close()
print('wrote fig-03-0301 (aligned dual panel; consistent resident/active channel)')
