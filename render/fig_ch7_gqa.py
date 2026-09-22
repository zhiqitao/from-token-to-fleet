import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D

# ---- fig-07-0703: GQA head-grouping (64 query heads over 8 KV heads) ----
# Narrower layout (figsize 7.4x6.4, tighter 8-col pitch) so the tight-crop content
# fits the print column and the cell labels place ~8pt on-page.
fig, ax = plt.subplots(figsize=(6.1, 5.28))
ax.set_xlim(0, 10.5); ax.set_ylim(0, 8.4); ax.axis('off')

ax.text(5.25, 8.1, 'Grouped-Query Attention (GQA): why the cache is 8× smaller',
        fontsize=10.5, fontweight='bold', ha='center')
ax.text(5.25, 7.65, '64 query heads (8 groups of 8)  →  8 shared KV heads', fontsize=7.6, fontweight='bold', ha='center')

colors = ['#3a6ea5','#6f9e5f','#e67e22','#c0392b','#8055b5','#2a9d8f','#d4a017','#5b7d94']

nq = 64
cols = 8
cell_w, cell_h2 = 0.62, 0.30
pitch = 1.10
xs = [0.35 + c*pitch for c in range(cols)]
cell_xys = {}
for i in range(nq):
    g = i // 8
    r = i % 8
    c = g
    x0 = xs[c]
    y0 = 6.85 - r*0.34
    ax.add_patch(Rectangle((x0, y0), cell_w, cell_h2, fc=colors[g%8], ec='white'))
    cell_xys.setdefault(g, []).append((x0+cell_w/2, y0+cell_h2/2))

# Group BRACKETS spanning each 8-head column (labels above the bracket, so the
# many-to-one grouping does not rely on colour alone — PASS-23b/24 grayscale ask).
grp_top = 7.15
for g in range(8):
    gx = xs[g]
    ax.plot([gx, gx], [grp_top, grp_top-0.14], color='#555', lw=1.0)
    ax.plot([gx+cell_w, gx+cell_w], [grp_top, grp_top-0.14], color='#555', lw=1.0)
    ax.plot([gx, gx+cell_w], [grp_top, grp_top], color='#555', lw=1.0)
    ax.text(gx+cell_w/2, grp_top+0.18, f'grp {g+1}', fontsize=7.0, ha='center',
            color=colors[g], fontweight='bold')

kv_w, kv_h = 0.78, 0.95
kv_ys = {}
for j in range(8):
    x0 = xs[j] + (cell_w - kv_w)/2
    y0 = 1.3
    ax.add_patch(Rectangle((x0, y0), kv_w, kv_h, fc=colors[j], ec='white'))
    ax.text(x0+kv_w/2, y0+kv_h/2, f'K/V {j+1}', ha='center', va='center', fontsize=7, color='white', fontweight='bold')
    kv_ys[j] = (x0+kv_w/2, y0+kv_h)
ax.text(0.5, 2.6, '8 shared KV heads', fontsize=7.6, fontweight='bold', color='#555')

for g in range(8):
    kx, ky = kv_ys[g]
    for (cx, cy) in cell_xys[g]:
        ax.plot([cx, kx], [cy-0.1, ky+0.05], color=colors[g], lw=0.6, alpha=0.7, zorder=1)

# Bottom banner: the byte accounting (narrower to fit)
bx0, by0, bw, bh = 0.25, 0.25, 9.7, 0.95
ax.add_patch(Rectangle((bx0, by0), bw, bh, fc='#fbf2ec', ec='#c0392b', lw=1.3, zorder=5))
ax.text(bx0+0.3, by0+0.62, 'MHA (full): 64 K/V per token → 2.62 MB/token', fontsize=6.6, color='#333', zorder=6)
ax.text(bx0+0.3, by0+0.18, 'GQA: 8 K/V per token → ~0.33 MB/token — 8× smaller cache', fontsize=6.6, color='#c0392b', fontweight='bold', zorder=6)

plt.tight_layout()
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0703.png', dpi=150)
plt.close()
print('wrote fig-07-0703')
