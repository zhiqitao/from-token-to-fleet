import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

# ---- fig-11-1102: discrete vs continuous batching (Orca-style slot diagram) ----
# Left: discrete batching — one batch runs to completion, others wait; slots idle.
# Right: continuous batching — slots are filled as soon as a sequence finishes.
# Compact narrow so it places at column width.

fig, axes = plt.subplots(1, 2, figsize=(6.1, 5.3))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
colors = ['#3a6ea5', '#6f9e5f', '#e67e22', '#c0392b', '#8055b5']

# ---------- discrete (left) ----------
ax = axes[0]
ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis('off')
ax.text(5, 4.55, 'Discrete batching', fontsize=11, fontweight='bold', ha='center')
for i in range(4):
    x0 = 0.1; x1 = 9.9
    ax.add_patch(Rectangle((x0, 4 - 0.7*i - 0.55), x1 - x0, 0.6, fc='#f5c6c6', ec='#c0392b', ls=':', lw=0.8))
tasks = [(0, 1.8, 0), (0, 2.6, 1), (0, 1.5, 2), (0, 3.0, 3)]
for (x0, w, s) in tasks:
    ax.add_patch(Rectangle((x0, 4 - 0.7*s - 0.55), w, 0.6, fc=colors[s], ec='none', alpha=0.9))
ax.text(8.2, 4 - 0.7*2 - 0.25, 'idle (bubble)', fontsize=8.0, color='#c0392b', ha='left', fontweight='bold')
ax.annotate('', xy=(7.7, 4 - 0.7*2 - 0.55), xytext=(7.9, 4 - 0.7*2 - 0.25),
            arrowprops=dict(arrowstyle='-', lw=0.7, color='#c0392b'))
ax.add_patch(Rectangle((1.0, 0.4), 3.0, 0.6, fc='#bbb', ec='none', alpha=0.6))
ax.text(2.5, 0.7, 'next batch waits', fontsize=9, color='#333', ha='center', fontweight='bold')
ax.annotate('', xy=(2.5, 1.0), xytext=(2.5, 0.7),
            arrowprops=dict(arrowstyle='-', lw=0.7, color='#555'))
ax.text(5.0, 0.1, 'GPU slots idle (pink) when a\nsequence finishes early', fontsize=8.2, color='#c0392b', ha='center')

# ---------- continuous (right) ----------
ax = axes[1]
ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis('off')
ax.text(5, 4.55, 'Continuous batching', fontsize=11, fontweight='bold', ha='center')
ctasks = [(0, 2.0, 0, False), (0.6, 2.4, 1, False), (1.0, 1.6, 2, False), (1.4, 2.8, 3, False),
          (2.2, 1.8, 0, True), (3.2, 2.0, 2, True), (3.6, 1.6, 1, True), (4.4, 2.2, 3, True),
          (5.0, 1.9, 0, True), (5.9, 2.0, 1, True)]
for (x0, w, s, backfill) in ctasks:
    y = 0.5 + (s % 4) * 0.7
    col = '#2e8b57' if backfill else colors[s % 5]
    lw_e = 1.6 if backfill else 0
    ec = '#1e6b42' if backfill else 'none'
    ax.add_patch(Rectangle((x0, y), w, 0.6, fc=col, ec=ec, lw=lw_e, alpha=0.95 if backfill else 0.9))
# time arrow: points RIGHT (time = the horizontal axis, per the caption "the
# horizontal axis is time"); the earlier vertical arrow contradicted the
# caption and the discrete panel's horizontal time direction (v8 review).
ax.annotate('', xy=(9.85, 0.2), xytext=(0.1, 0.2), arrowprops=dict(arrowstyle='-|>', lw=1.3, color='#555'))
ax.text(5.0, 0.02, 'time  (decode steps / iterations)', fontsize=8.5, color='#555', ha='center', va='bottom')
# consolidated legend (v8 review: the color key was a set of small, incomplete
# inline callouts; a single legend makes the color->meaning mapping explicit).
# Figure-level so it spans both panels (idle/sequence are in the left panel,
# backfill in the right).
from matplotlib.patches import Patch
fig.legend(handles=[
    Patch(fc='#f5c6c6', ec='#c0392b', ls=':', label='idle slot (bubble)'),
    Patch(fc=colors[0], label='sequence in flight'),
    Patch(fc='#2e8b57', ec='#1e6b42', label='new sequence (backfill)'),
], loc='upper center', bbox_to_anchor=(0.5, 1.0), fontsize=8.2, frameon=False, ncol=3,
   handlelength=1.2, columnspacing=1.2)
# annotation in the clear top-right band (above the top slot row, which ends at
# x=6.6); the arrow points down to the last backfilled green slot — no overlap
# with the slot rectangles.
ax.text(9.8, 4.15, 'a finishing sequence frees\nits slot immediately',
        fontsize=8.2, color='#555', ha='right', va='top')
ax.annotate('', xy=(6.55, 2.95), xytext=(7.3, 3.5),
            arrowprops=dict(arrowstyle='->', lw=0.9, color='#555'))
ax.text(5.0, 0.35, 'new sequences (green) snap into freed slots', fontsize=8.2, color='#2e8b57', ha='center')

# Ch 11.1 IMPROVE: the "decode-only" scope is in the caption; put it in the
# figure too so a reader cannot mistake it for full mixed prefill/decode
# scheduling. Figure-level so it spans both panels, below the time axis.
fig.text(0.5, 0.015,
         'Decode-only illustration: every shown request is in the per-token decode phase.\n'
         'A real stack also interleaves prefill of new requests into the same steps (Ch 11 Sec. 4, Ch 15).',
         fontsize=8.0, color='#555', ha='center', va='bottom', style='italic')

plt.tight_layout(rect=(0, 0.05, 1, 1))
plt.savefig('design/manuscript/chapter-11/figures/fig-11-1102.png', dpi=150)
plt.close()
print('wrote fig-11-1102')
