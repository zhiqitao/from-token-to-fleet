import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ---- fig-07-0705: Memory Tetris — how the 8xH100 host's 640 GB fills at three contexts ----
# Canonical (Ch 7): weights 140 GB, runtime/NCCL ~64 GB, KV FP16 ~2.5 MB/token
# 9.5K max -> ~24.9 GB KV ; 32K -> ~84 GB ; 128K -> ~335 GB
# NOTE: height bumped +0.4 (4.74 -> 5.14) so the caption/legend have clear bottom
# breathing room; labels are placed INSIDE the axes (ylim extended down) and the
# axes rectangle is pinned toward the top, reserving a blank bottom band.
# Title sized so it fits within the 6.1in column (12.0pt was ~6.18in -> clipped).
fig, ax = plt.subplots(figsize=(6.1, 5.6))
ax.set_xlim(0, 8.0); ax.set_ylim(-640, 760)
ax.axis('off')   # schematic; regen tight-crops to content
ax.set_title('Memory Tetris: how the 8×H100 host (640 GB) fills with context',
             fontsize=11.0, fontweight='bold', pad=14)

bar_w = 2.1
ctxs = [('9.5K max', 24.9), ('32K context', 84), ('128K context', 335)]
xs = [1.6, 4.0, 6.4]
cols = {'runtime': '#95a5a6', 'weights': '#27408b', 'kv': '#e67e22'}

# Put each segment's total label ABOVE its bar, outside the fill, so nothing
# collides with an in-bar value.  Bars carry only a small white value where it
# fits; the KV value (the one that varies) is always shown above its bar.
for x, (label, kv) in zip(xs, ctxs):
    ax.bar(x, 64, width=bar_w, bottom=0, color=cols['runtime'], hatch='//', edgecolor='white', linewidth=0.8)
    ax.bar(x, 140, width=bar_w, bottom=64, color=cols['weights'], hatch='xx', edgecolor='white', linewidth=0.8)
    ax.bar(x, kv, width=bar_w, bottom=204, color=cols['kv'], hatch='..', edgecolor='white', linewidth=0.8, alpha=0.92)
    total = 204 + kv
    # KV value above its bar (clip_on=False so it is never cut off)
    ax.text(x+bar_w/2, 204+kv+16, f'{kv:.1f} GB KV'.replace('.0 GB',' GB'),
            ha='center', va='bottom', fontsize=10.5, color='#c0392b', fontweight='bold', clip_on=False)
    # context label + total, below the bar
    ax.text(x+bar_w/2, -40, label, ha='center', fontsize=10, fontweight='bold')
    ax.text(x+bar_w/2, -70, f'= {total:.0f} GB used', ha='center', fontsize=9, color='#555')

ax.axhline(640, color='#a93226', lw=2.2, ls='--')
ax.text(0.15, 662, '640 GB pool = 8×H100 HBM', fontsize=9.5, color='#a93226', fontweight='bold')

leg = [mpatches.Patch(color=cols['kv'], hatch='..', edgecolor='white', lw=0.5, label='KV cache (grows w/ context)'),
       mpatches.Patch(color=cols['weights'], label='weights 140 GB'),
       mpatches.Patch(color=cols['runtime'], label='runtime / NCCL ~64 GB')]

ax.text(0.2, -260, 'baseline (weights + runtime) is context-independent;\nthe KV cache is the lever that grows with context.\nFP16 ~2.5 MB/token [ILLUSTRATIVE][DERIVED].',
        fontsize=8.6, color='#444')
ax.text(0.2, -420, 'AGGREGATE RESIDENCY SCREEN \u2260 PER-RANK FIT GUARANTEE\n(total < 640 GB is a first-order check;\nsharding / fragmentation still validated per GPU)',
        fontsize=8.6, color='#c0392b', fontweight='bold')
ax.legend(handles=leg, loc='lower left', bbox_to_anchor=(0.0, -0.28), fontsize=9.5, frameon=False, ncol=1)

fig.subplots_adjust(top=0.90, bottom=0.04, left=0.06, right=0.96)
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0705.png', dpi=150, bbox_inches='tight', pad_inches=0.05)
plt.close()
print('fig-07-0705 done')
