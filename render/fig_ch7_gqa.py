import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ---- fig-07-0703: GQA head-sharing (many-query-share-fewer-KV) ----
# Density reduction (publication review): one clean funnel schematic; NO per-head
# numeric labels, NO per-group "grp N" brackets, NO bottom annotation/summary box.
# The 8:1 ratio is carried by the geometry (a row of 8 Q cells -> one K/V cell)
# and the ratio/takeaway text lives in the figure caption, not in the raster.
fig, ax = plt.subplots(figsize=(6.1, 4.0))
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow
ax.set_xlim(0, 10); ax.set_ylim(0, 6.6); ax.axis('off')
ax.set_position((0, 0, 1, 1))    # fill the whole figure canvas

# ---- title (short; the takeaway numbers move to the caption) ----
ax.text(5.0, 6.30, 'Grouped-Query Attention (GQA)', fontsize=11.5,
        fontweight='bold', ha='center', va='center', color='#1a1a1a')
ax.text(5.0, 5.90, 'many query heads  →  few shared K/V heads',
        fontsize=9.0, ha='center', va='center', color='#555555')

# ---- layout ----
Q_FILL, Q_EDGE = '#cfe3f2', '#4a7fb5'
KV_FILL, KV_EDGE = '#e67e22', '#b3591f'

# Three visible groups (rows of 8 query heads) + an ellipsis to signal "many more".
group_x = [1.65, 4.55, 7.45]     # cell-row centre x per group
n_per_group = 8
cell_w, cell_h, pitch = 0.26, 0.34, 0.30
q_row_y0 = 4.85                  # bottom of the query-head cells
kv_top = 3.40                    # top of each shared K/V cell

for gx in group_x:
    x0 = gx - (n_per_group - 1) * pitch / 2.0
    # a row of 8 query-head cells
    for i in range(n_per_group):
        cx = x0 + i * pitch
        ax.add_patch(Rectangle((cx, q_row_y0), cell_w, cell_h,
                               fc=Q_FILL, ec=Q_EDGE, lw=0.8))
    # thin converging connectors from each head down to the single K/V cell
    for i in range(n_per_group):
        cx = x0 + i * pitch + cell_w / 2.0
        ax.plot([cx, gx], [q_row_y0, kv_top], color='#8a9aa5', lw=0.6, alpha=0.65)
    # one shared K/V cell (larger, accent colour)
    kv_w, kv_h = 1.25, 0.72
    kv_x = gx - kv_w / 2.0
    ax.add_patch(Rectangle((kv_x, kv_top - kv_h), kv_w, kv_h,
                           fc=KV_FILL, ec=KV_EDGE, lw=1.0))
    ax.text(gx, kv_top - kv_h / 2.0, 'K/V', ha='center', va='center',
            fontsize=8.8, color='white', fontweight='bold')

# ellipsis signals the pattern repeats across many groups / heads
ax.text(9.35, q_row_y0 + cell_h / 2.0, '⋯', fontsize=13, ha='center', va='center',
        color='#8a9aa5')
ax.text(9.35, kv_top - 0.36, '⋯', fontsize=13, ha='center', va='center',
        color='#8a9aa5')

# ---- minimal row labels (no per-cell / per-group text) ----
ax.text(0.35, 5.75, 'query heads', fontsize=8.2, ha='left', va='center',
        color='#4a7fb5', fontweight='bold')
ax.text(0.35, 2.35, 'shared K/V heads', fontsize=8.2, ha='left', va='center',
        color='#b3591f', fontweight='bold')

# 8 : 1 ratio badge (kept short; the MB/token takeaway is in the caption)
ax.text(5.0, 1.62, '8 query heads : 1 K/V head  (× 8 groups)',
        fontsize=8.8, ha='center', va='center', color='#333333',
        bbox=dict(boxstyle='round,pad=0.35', fc='#f5f5f5', ec='#b9b9b9', lw=0.8))

plt.savefig('design/manuscript/chapter-07/figures/fig-07-0703.png', dpi=150)
plt.close()
print('wrote fig-07-0703')
