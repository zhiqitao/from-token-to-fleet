import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D

# ---- fig-07-0703: GQA head-grouping (64 query heads over 8 KV heads) ----
fig, ax = plt.subplots(figsize=(12, 6.6))
ax.set_xlim(0, 22); ax.set_ylim(0, 8.4); ax.axis('off')

ax.text(11, 8.1, 'Grouped-Query Attention (GQA): why the cache is 8× smaller', fontsize=14, fontweight='bold', ha='center')

colors = ['#3a6ea5','#6f9e5f','#e67e22','#c0392b','#8055b5','#2a9d8f','#d4a017','#5b7d94']
ax.text(1.5, 7.5, '64 query heads (8 groups of 8)  →  8 shared KV heads', fontsize=10, fontweight='bold')

# Query heads: 64 in an 8x8 grid — each COLUMN is one group of 8 fanning to one KV head
nq = 64
cols = 8
cell_w, cell_h = 1.3, 0.5
xs = [0.8 + c*2.05 for c in range(cols)]
cell_xys = {}  # group -> list of (cx, cy) centers
cell_h2 = 0.34
for i in range(nq):
    g = i // 8        # group = column
    r = i % 8         # row within the column
    c = g
    x0 = xs[c]
    y0 = 6.85 - r*0.45
    ax.add_patch(Rectangle((x0, y0), cell_w, cell_h2, fc=colors[g%8], ec='white'))
    cell_xys.setdefault(g, []).append((x0+cell_w/2, y0+cell_h2/2))

# group labels
for g in range(8):
    gx = xs[0] + 0.65 + g*2.05
    ax.text(gx, 6.92, f'grp {g+1}', fontsize=8, ha='center', color=colors[g], fontweight='bold')

# KV heads: 8 large boxes in the same columns
kv_w, kv_h = 1.55, 1.5
kv_ys = {}
for j in range(8):
    x0 = xs[j] + (cell_w - kv_w)/2
    y0 = 1.3
    ax.add_patch(Rectangle((x0, y0), kv_w, kv_h, fc=colors[j], ec='white'))
    ax.text(x0+kv_w/2, y0+kv_h/2, f'K/V {j+1}', ha='center', va='center', fontsize=9, color='white', fontweight='bold')
    kv_ys[j] = (x0+kv_w/2, y0+kv_h)
ax.text(1.5, 3.3, '8 shared KV heads', fontsize=10, fontweight='bold', color='#555')

# Fan-in connection lines: each query head -> its shared KV head
for g in range(8):
    kx, ky = kv_ys[g]
    for (cx, cy) in cell_xys[g]:
        ax.plot([cx, kx], [cy-0.1, ky+0.05], color=colors[g], lw=0.8, alpha=0.7, zorder=1)

# Bottom banner: the byte accounting
bx0, by0, bw, bh = 0.6, 0.3, 20.8, 1.7
ax.add_patch(Rectangle((bx0, by0), bw, bh, fc='#fbf2ec', ec='#c0392b', lw=1.6, zorder=5))
ax.text(bx0+0.8, by0+1.15, 'MHA (full): 64 K/V per token → 2.5 MB/token (worst case)          ', fontsize=10, color='#333')
ax.text(bx0+0.8, by0+0.55, 'GQA: 8 K/V per token → ~0.33 MB/token — an 8× smaller cache (Ch. 7 note)', fontsize=10, color='#c0392b', fontweight='bold')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0703.png', dpi=150)
plt.close()
print('wrote fig-07-0703')
