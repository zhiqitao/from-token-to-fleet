import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

# ---- fig-11-1102: discrete vs continuous batching (Orca-style slot diagram) ----
# Left: discrete batching — one batch runs to completion, others wait; slots idle.
# Right: continuous batching — slots are filled as soon as a sequence finishes.

fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
colors = ['#3a6ea5', '#6f9e5f', '#e67e22', '#c0392b', '#8055b5']

# ---------- discrete (left) ----------
ax = axes[0]
ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis('off')
ax.text(5, 4.7, 'Discrete batching', fontsize=12, fontweight='bold', ha='center')
# batch 1 occupies all 4 slots until all finish; batch 2 queues; idle slots when a seq finishes early
# shade idle tail of each slot in RED
for i in range(4):
    x0 = 0.1; x1 = 9.9
    ax.add_patch(Rectangle((x0, 4 - 0.7*i - 0.55), x1 - x0, 0.6, fc='#f5c6c6', ec='#c0392b', ls=':', lw=0.8))
tasks = [(0, 1.8, 0), (0, 2.6, 1), (0, 1.5, 2), (0, 3.0, 3)]  # (x0, width, slot)
for (x0, w, s) in tasks:
    ax.add_patch(Rectangle((x0, 4 - 0.7*s - 0.55), w, 0.6, fc=colors[s], ec='none', alpha=0.9))
ax.text(8.3, 4 - 0.7*2 - 0.25, 'idle (bubble)', fontsize=7.5, color='#c0392b', ha='left', fontweight='bold')
# waiting marker for next batch
ax.add_patch(Rectangle((1.0, 0.4), 3.0, 0.6, fc='#bbb', ec='none', alpha=0.6))
ax.text(2.5, 0.7, 'next batch waits', fontsize=8, color='#555', ha='center')
ax.text(5.0, 0.1, 'GPU slots idle (red) whenever a sequence \nfinishes early within the batch', fontsize=8, color='#c0392b', ha='center')

# ---------- continuous (right) ----------
ax = axes[1]
ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis('off')
ax.text(5, 4.7, 'Continuous batching', fontsize=12, fontweight='bold', ha='center')
# sequences staggered and filled into freed slots as soon as they complete
# `green` marks a backfilled (new) sequence snapping into a just-freed slot
ctasks = [(0, 2.0, 0, False), (0.6, 2.4, 1, False), (1.0, 1.6, 2, False), (1.4, 2.8, 3, False),
          (2.2, 1.8, 0, True), (3.2, 2.0, 2, True), (3.6, 1.6, 1, True), (4.4, 2.2, 3, True),
          (5.0, 1.9, 0, True), (5.9, 2.0, 1, True)]
for (x0, w, s, backfill) in ctasks:
    y = 0.5 + (s % 4) * 0.7
    col = '#2e8b57' if backfill else colors[s % 5]
    lw_e = 1.6 if backfill else 0
    ec = '#1e6b42' if backfill else 'none'
    ax.add_patch(Rectangle((x0, y), w, 0.6, fc=col, ec=ec, lw=lw_e, alpha=0.95 if backfill else 0.9))
ax.annotate('', xy=(9.8, 2.95), xytext=(9.8, 0.5), arrowprops=dict(arrowstyle='-|>', lw=1.3, color='#555'))
ax.text(9.35, 1.7, 'a finishing sequence\nfrees its slot\nimmediately', fontsize=7.5, color='#555', ha='right')
ax.text(5.0, 0.1, 'new sequences (green) snap into the freed slot → higher GPU utilization', fontsize=8, color='#2e8b57', ha='center')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-11/figures/fig-11-1102.png', dpi=150)
plt.close()
print('wrote fig-11-1102')
