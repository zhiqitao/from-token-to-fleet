import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ---- fig-07-0705: Memory Tetris — how the 8xH100 host's 640 GB fills at three contexts ----
# Canonical (Ch 7): weights 140 GB, runtime/NCCL ~64 GB, KV FP16 ~2.5 MB/token
# 9.2K -> ~23.8 GB KV ; 32K -> ~80 GB ; 128K -> ~320 GB
fig, ax = plt.subplots(figsize=(7.2, 5.6))
ax.set_xlim(0, 8.0); ax.set_ylim(0, 720)
ax.axis('off')   # no numeric axes: it's a schematic -> regen tight-crops to content
ax.set_title('Memory Tetris: how the 8×H100 host (640 GB) fills with context',
             fontsize=12.5, fontweight='bold', pad=14)

bar_w = 2.1
ctxs = [('9.2K context', 23.8), ('32K context', 80), ('128K context', 320)]
xs = [1.6, 4.0, 6.4]
cols = {'runtime': '#95a5a6', 'weights': '#27408b', 'kv': '#e67e22'}

def val(x, y, s, fs=9, bold=False, c='white'):
    ax.text(x+bar_w/2, y, s, ha='center', va='center', fontsize=fs, color=c,
            fontweight='bold' if bold else 'normal', clip_on=False)

for x, (label, kv) in zip(xs, ctxs):
    ax.bar(x, 64, width=bar_w, bottom=0, color=cols['runtime'], hatch='//', edgecolor='white', linewidth=0.8)
    val(x, 27, '64', fs=9)
    ax.bar(x, 140, width=bar_w, bottom=64, color=cols['weights'], hatch='xx', edgecolor='white', linewidth=0.8)
    val(x, 122, '140', fs=10, bold=True)
    ax.bar(x, kv, width=bar_w, bottom=204, color=cols['kv'], hatch='..', edgecolor='white', linewidth=0.8, alpha=0.92)
    total = 204 + kv
    ax.text(x+bar_w/2, 204+kv+18, f'{kv:.1f}'.rstrip('0').rstrip('.')+' GB KV',
            ha='center', va='bottom', fontsize=10, color='#c0392b',
            fontweight='bold', clip_on=False)
    ax.text(x+bar_w/2, -34, label, ha='center', fontsize=10, fontweight='bold')
    ax.text(x+bar_w/2, -62, f'= {total:.0f} GB used', ha='center', fontsize=9,
            color='#555')

ax.axhline(640, color='#a93226', lw=2.2, ls='--')
ax.text(0.15, 656, '640 GB pool = 8×H100 HBM', fontsize=9.5, color='#a93226',
        fontweight='bold')

# legend below the axes (vertical, compact so the figure isn't a wide sliver)
leg = [mpatches.Patch(color=cols['kv'], hatch='..', edgecolor='white', lw=0.5, label='KV cache (grows w/ context)'),
       mpatches.Patch(color=cols['weights'], label='weights 140 GB'),
       mpatches.Patch(color=cols['runtime'], label='runtime / NCCL ~64 GB')]
ax.legend(handles=leg, loc='upper center', bbox_to_anchor=(0.5, -0.13),
          fontsize=9, frameon=False, ncol=1)

ax.text(0.2, -96, 'baseline (weights + runtime) is context-independent; the KV cache is the lever that grows\nwith context.  FP16 ~2.5 MB/token [2° DERIVED].',
        fontsize=8.5, color='#444')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0705.png', dpi=150)
plt.close()
print('fig-07-0705 done')
