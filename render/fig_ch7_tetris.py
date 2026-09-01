import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ---- fig-07-0705: Memory Tetris — how the 8xH100 host's 640 GB fills at three contexts ----
# Canonical (Ch 7): weights 140 GB, runtime/NCCL ~64 GB, KV FP16 ~2.5 MB/token
# 9.2K -> ~23.8 GB KV ; 32K -> ~80 GB ; 128K -> ~320 GB
fig, ax = plt.subplots(figsize=(9.5, 6.6))
ax.set_xlim(0, 8.0); ax.set_ylim(0, 720)
ax.set_yticks([]); ax.set_xticks([])
ax.set_title('Memory Tetris: how the 8×H100 host (640 GB) fills as context grows', fontsize=12.5, fontweight='bold')

bar_w = 1.5
ctxs = [('9.2K context', 23.8), ('32K context', 80), ('128K context', 320)]
xs = [1.0, 3.5, 6.0]
cols = {'runtime': '#95a5a6', 'weights': '#27408b', 'kv': '#e67e22'}

def val(x, y, s, fs=8.5, bold=False, c='white'):
    ax.text(x+bar_w/2, y, s, ha='center', va='center', fontsize=fs, color=c, fontweight='bold' if bold else 'normal', clip_on=False)

for x, (label, kv) in zip(xs, ctxs):
    ax.bar(x, 64, width=bar_w, bottom=0, color=cols['runtime'], edgecolor='white', linewidth=0.8)
    val(x, 27, '64', fs=8)
    ax.bar(x, 140, width=bar_w, bottom=64, color=cols['weights'], edgecolor='white', linewidth=0.8)
    val(x, 122, '140', fs=10, bold=True)
    ax.bar(x, kv, width=bar_w, bottom=204, color=cols['kv'], edgecolor='white', linewidth=0.8, alpha=0.92)
    total = 204 + kv
    ax.text(x+bar_w/2, 204+kv+20, f'{kv:.1f}'.rstrip('0').rstrip('.')+' GB KV', ha='center', va='bottom', fontsize=10, color='#c0392b', fontweight='bold', clip_on=False)
    ax.text(x+bar_w/2, -34, label, ha='center', fontsize=10, fontweight='bold')
    ax.text(x+bar_w/2, -56, f'= {total:.0f} GB used', ha='center', fontsize=8, color='#555')

ax.axhline(640, color='#a93226', lw=2.2, ls='--')
ax.text(0.15, 654, '640 GB pool = 8×H100 HBM', fontsize=9.5, color='#a93226', fontweight='bold')

# legend mapping colors to segments
leg = [mpatches.Patch(color=cols['kv'], label='KV cache (grows with context)'),
       mpatches.Patch(color=cols['weights'], label='weights 140 GB'),
       mpatches.Patch(color=cols['runtime'], label='runtime / NCCL ~64 GB')]
ax.legend(handles=leg, loc='upper left', fontsize=8.5, frameon=True, bbox_to_anchor=(0.0, 1.02))

ax.annotate('approaches the ceiling —\nKV, not weights, decides residency', xy=(7.0, 524), xytext=(7.62, 280),
            arrowprops=dict(arrowstyle='->', color='#a93226', lw=1.3), fontsize=8, color='#a93226', ha='left')

ax.text(0.15, -100, 'baseline (weights + runtime) is context-independent; the KV cache is the lever that grows with context.  FP16 ~2.5 MB/token [2° DERIVED].',
        fontsize=7.5, color='#444')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0705.png', dpi=150)
plt.close()
print('fig-07-0705 done')
