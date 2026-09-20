import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

# Fig 3.1 — Dense vs MoE: distinguish ACTIVE parameters (per token) from TOTAL
# RESIDENT weights. Key correctness point: an MoE still stores all its experts;
# only the compute per token is reduced to the top-k active set. So the
# '~28 GB' is the ACTIVE compute footprint, NOT the resident weight residency.
# Authored at COLUMN width, tall figure with generous leading between every
# element so nothing crowds another.
fig, axes = plt.subplots(1, 2, figsize=(6.7, 6.2))

# Left: Dense 70B — every token activates all 70B params
ax = axes[0]
ax.set_xlim(0, 10); ax.set_ylim(0, 18); ax.axis('off')
for r in range(4):
    for cc in range(6):
        ax.add_patch(Rectangle((0.8+cc*1.35, 14.6-r*1.05), 1.1, 0.8, fc='#3a6ea5', ec='white'))
ax.text(5, 17.0, 'Dense 70B', fontsize=12, fontweight='bold', ha='center')
ax.text(5, 10.6, 'ALL 70B params active', fontsize=10.5, fontweight='bold', color='#3a6ea5', ha='center')
ax.text(5, 9.0, 'every token', fontsize=10, color='#333', ha='center')
ax.text(5, 7.0, 'resident weights ≈ 140 GB', fontsize=10, color='#555', ha='center', linespacing=1.6)
ax.text(5, 5.0, 'active per token ≈ 140 GB', fontsize=10, color='#555', ha='center', linespacing=1.6)
ax.text(5, 3.0, 'KV grows linearly with context', fontsize=10, color='#555', ha='center', linespacing=1.6)

# Right: MoE — top-2 of 8 experts activates ~14B
ax = axes[1]
ax.set_xlim(0, 10); ax.set_ylim(0, 18); ax.axis('off')
exp_pos = [(0.6,11.9),(3.3,11.9),(6.0,11.9),(0.6,9.7),(3.3,9.7),(6.0,9.7),(0.6,7.5),(3.3,7.5)]
active = {0,3}  # top-2 experts active
for i,(x,y) in enumerate(exp_pos):
    col = '#e67e22' if i in active else '#d9d9d9'
    ax.add_patch(Rectangle((x,y), 1.7, 1.3, fc=col, ec='white'))
    ax.text(x+0.85, y+0.65, f'E{i+1}', ha='center', va='center', fontsize=9.5, color='white' if i in active else '#555')
ax.text(5, 17.0, 'MoE (8 experts)', fontsize=12, fontweight='bold', ha='center')
ax.text(5, 5.6, 'top-2 active → ~14B', fontsize=10, fontweight='bold', color='#e67e22', ha='center')
ax.text(5, 3.9, 'resident weights ≈ full expert set', fontsize=10, color='#555', ha='center', linespacing=1.6)
ax.text(5, 2.4, 'active per token ≈ 28 GB', fontsize=10, color='#555', ha='center', linespacing=1.6)

# ---- KV bars: identical under both columns (the whole residual point) ----
for axx in axes:
    axx.add_patch(Rectangle((0.9, 0.6), 8.2, 0.9, fc='#c0392b', ec='white'))
    axx.text(5, 1.05, 'KV same as dense', ha='center', va='center', fontsize=10, color='white', fontweight='bold')
    axx.set_ylim(-0.4, 18)

plt.tight_layout()
plt.savefig('design/manuscript/chapter-03/figures/fig-03-0301.png', dpi=150)
plt.close()
print('wrote fig-03-0301 (column width; generous leading; separated KV caption)')
