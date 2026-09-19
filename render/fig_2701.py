import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 2026 Frontier Architecture data [1P]
# Short abbreviations on the axis (readable at book size); full names in a
# legend/footnote so the labels never crowd or overlap.
abbrev = ['DeepSeek V4', 'Kimi K3', 'Qwen3.8', 'GLM-5.3']
total_b = [284, 2800, 125, 320]       # total params (B) [1P]
active_b = [13, 104, 6, 18]           # active params (B) [1P]

fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.7), gridspec_kw={'wspace': 0.30})

# Panel 1: Total vs Active (log scale)
x = np.arange(len(abbrev))
width = 0.36
ax = axes[0]
ax.bar(x - width/2, total_b, width, label='Total', color='#4682b4')
ax.bar(x + width/2, active_b, width, label='Active', color='#ff8c42')
ax.set_yscale('log')
ax.set_xticks(x)
ax.set_xticklabels(abbrev, fontsize=9.5, rotation=0, ha='center')
ax.set_ylabel('Params (B, log)', fontsize=9.5)
ax.set_title('Total vs active', fontsize=10)
ax.legend(fontsize=8, loc='upper left')
ax.grid(alpha=0.3, which='both')
ax.tick_params(labelsize=10)
ax.set_ylim(1, 6000)

# Panel 2: Active fraction (sparsity)
ax = axes[1]
fr = [a/t*100 for a, t in zip(active_b, total_b)]
bars = ax.bar(x, fr, 0.5, color='#6a9fb5')
for i, b in enumerate(bars):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.15, f'{fr[i]:.1f}%', ha='center', fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(abbrev, fontsize=9.5, rotation=0, ha='center')
ax.set_ylabel('Active fraction (% of total)', fontsize=9.5)
ax.set_title('Extreme MoE sparsity', fontsize=10)
ax.grid(alpha=0.3, axis='y')
ax.tick_params(labelsize=10)
ax.set_ylim(0, max(fr)*1.25)

# legend below the panels (keeps axis labels short & uncluttered)
fig.text(0.5, 0.03,
         'DeepSeek V4 = V4-Pro/Flash · GLM-5.3 = GLM-5.3-Flash.  Active parameters are per model card [1P].',
         ha='center', fontsize=8, color='#555')

plt.tight_layout(rect=(0, 0.06, 1, 1))
out = 'design/manuscript/chapter-27/figures/fig-27-2701.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
