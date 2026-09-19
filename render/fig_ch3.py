import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

# Fig 3.1 — Dense vs MoE: distinguish ACTIVE parameters (per token) from TOTAL
# RESIDENT weights.  Key correctness point: an MoE still stores all its experts;
# only the compute per token is reduced to the top-k active set.  So the
# '~28 GB' is the ACTIVE compute footprint, NOT the resident weight residency.
# Dense 70B in FP16: ~140 GB resident, ~140 GB active per token.
# MoE 8x7B-class (top-2 of 8): ~140-280 GB resident (weights), ~14B active
# params per token -> ~28 GB active compute footprint.
fig, axes = plt.subplots(1, 2, figsize=(12, 5.4))

# Left: Dense 70B — every token activates all 70B params
ax = axes[0]
ax.set_xlim(0, 10); ax.set_ylim(0, 12.5); ax.axis('off')
for r in range(4):
    for cc in range(6):
        ax.add_patch(Rectangle((0.8+cc*1.35, 8.4-r*1.2), 1.1, 0.8, fc='#3a6ea5', ec='white'))
ax.text(1.4, 3.4, 'ALL 70B params active', fontsize=10, fontweight='bold', color='#3a6ea5')
ax.text(1.4, 2.6, 'every token', fontsize=9, color='#333')
ax.text(5, 10.6, 'Dense 70B', fontsize=13, fontweight='bold', ha='center')
ax.text(5, 1.9, 'resident weights ≈ 140 GB', fontsize=9, color='#555', ha='center')
ax.text(5, 1.2, 'active per token ≈ 140 GB', fontsize=9, color='#555', ha='center')
ax.text(5, 0.5, 'KV grows linearly with context', fontsize=9, color='#555', ha='center')

# Right: MoE — top-2 of 8 experts activates ~14B
ax = axes[1]
ax.set_xlim(0, 10); ax.set_ylim(0, 12.5); ax.axis('off')
exp_pos = [(1.2,7.9),(4.2,7.9),(7.2,7.9),(1.2,5.9),(4.2,5.9),(7.2,5.9),(1.2,3.9),(4.2,3.9)]
active = {0,3}  # top-2 experts active
for i,(x,y) in enumerate(exp_pos):
    col = '#e67e22' if i in active else '#d9d9d9'
    ax.add_patch(Rectangle((x,y), 1.6, 1.2, fc=col, ec='white'))
    ax.text(x+0.8, y+0.6, f'E{i+1}', ha='center', va='center', fontsize=9, color='white' if i in active else '#555')
ax.text(6.6, 4.6, 'top-2 active → ~14B', fontsize=9, fontweight='bold', color='#e67e22')
ax.text(5, 10.6, 'MoE (8 experts)', fontsize=13, fontweight='bold', ha='center')
ax.text(5, 1.9, 'resident weights ≈ full expert set', fontsize=9, color='#555', ha='center')
ax.text(5, 1.2, 'active per token ≈ 28 GB', fontsize=9, color='#555', ha='center')
ax.text(5, 0.5, 'MoE routing alone does not reduce KV cache growth;\nKV footprint is set by the attention architecture', fontsize=9, color='#555', ha='center')

# ---- KV bars: identical under both columns (the whole residual point) ----
for axx in axes:
    axx.add_patch(Rectangle((1.4, -0.9), 7.2, 0.5, fc='#c0392b', ec='white'))
    axx.text(5, -1.4, 'same KV cache (attention is still dense)', ha='center', fontsize=9, color='#c0392b')
    axx.set_ylim(-2.4, 12.5)

plt.tight_layout()
plt.savefig('design/manuscript/chapter-03/figures/fig-03-0301.png', dpi=150)
plt.close()
print('wrote fig-03-0301 (resident vs active distinguished)')
