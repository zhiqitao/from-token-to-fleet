import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

# Fig 3.1 — Dense vs MoE parameter allocation and KV-cache behavior
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Left: Dense 70B — every token activates all 70B params
ax = axes[0]
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
for r in range(4):
    for cc in range(6):
        ax.add_patch(Rectangle((0.8+cc*1.35, 7.6-r*1.2), 1.1, 0.8, fc='#3a6ea5', ec='white'))
ax.text(1.4, 3.0, 'ALL 70B params active', fontsize=10, fontweight='bold', color='#3a6ea5')
ax.text(1.4, 2.2, 'every token', fontsize=9, color='#333')
ax.text(5, 9.4, 'Dense 70B', fontsize=13, fontweight='bold', ha='center')
ax.text(5, 1.2, 'weight residency ≈ 140 GB', fontsize=9, color='#555', ha='center')
ax.text(5, 0.5, 'KV grows linearly with context', fontsize=9, color='#555', ha='center')

# Right: MoE — top-2 of 8 experts activates ~14B
ax = axes[1]
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
exp_pos = [(1.2,7.3),(4.2,7.3),(7.2,7.3),(1.2,5.3),(4.2,5.3),(7.2,5.3),(1.2,3.3),(4.2,3.3)]
active = {0,3}  # top-2 experts active
for i,(x,y) in enumerate(exp_pos):
    col = '#e67e22' if i in active else '#cccccc'
    ax.add_patch(Rectangle((x,y), 1.6, 1.2, fc=col, ec='white'))
    ax.text(x+0.8, y+0.6, f'E{i+1}', ha='center', va='center', fontsize=9, color='white' if i in active else '#555')
ax.text(6.6, 4.0, 'top-2 active → ~14B', fontsize=9, fontweight='bold', color='#e67e22')
ax.text(5, 2.3, 'KV growth identical to dense', fontsize=9, color='#555', ha='center')
ax.text(5, 9.4, 'MoE (8 experts)', fontsize=13, fontweight='bold', ha='center')
ax.text(5, 1.4, 'weight residency ≈ 28 GB', fontsize=9, color='#555', ha='center')
ax.text(5, 0.7, 'KV grows identically to dense', fontsize=9, color='#555', ha='center')

# ---- KV bars: identical under both columns (the whole residual point) ----
for axx in axes:
    # equal-length KV bars at same y under each column -> 'KV identical'
    axx.add_patch(Rectangle((1.4, -1.1), 7.2, 0.5, fc='#c0392b', ec='white'))
    axx.text(5, -1.55, 'same KV cache (attention is still dense)', ha='center', fontsize=9, color='#c0392b')
    axx.set_ylim(-2.2, 10)

plt.tight_layout()
plt.savefig('design/manuscript/chapter-03/figures/fig-03-0301.png', dpi=150)
print('wrote fig-03-0301')
