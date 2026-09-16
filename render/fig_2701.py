import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 2026 Frontier Architecture data [1P]
models = ['DeepSeek-V4', 'Kimi K3', 'Qwen3.8', 'GLM-5.3']
total_b = [284, 2800, 125, 320]       # total params (B) [1P]
active_b = [13, 104, 6, 18]           # active params (B) [1P]

fig, axes = plt.subplots(1, 2, figsize=(6.3, 3.5), gridspec_kw={'wspace': 0.4})

# Panel 1: Total vs Active (log scale)
x = np.arange(len(models))
width = 0.38
ax = axes[0]
ax.bar(x - width/2, total_b, width, label='Total', color='#4682b4')
ax.bar(x + width/2, active_b, width, label='Active', color='#ff8c42')
ax.set_yscale('log')
ax.set_xticklabels(models, fontsize=9)
ax.set_ylabel('Params (B, log)', fontsize=9)
ax.set_title('Total vs active', fontsize=9.5)
ax.legend(fontsize=7.5, loc='upper left')
ax.grid(alpha=0.3, which='both')
ax.tick_params(labelsize=10)

# Panel 2: Active fraction (sparsity)
ax = axes[1]
fr = [a/t*100 for a,t in zip(active_b, total_b)]
bars = ax.bar(x, fr, 0.5, color='#6a9fb5')
for i,b in enumerate(bars):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.2, f'{fr[i]:.1f}%', ha='center', fontsize=8.5)
ax.set_xticklabels(models, fontsize=9)
ax.set_ylabel('Active fraction (% of total)', fontsize=9)
ax.set_title('Extreme MoE sparsity', fontsize=9.5)
ax.grid(alpha=0.3, axis='y')
ax.tick_params(labelsize=10)

plt.tight_layout()
out = 'design/manuscript/chapter-27/figures/fig-27-2701.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
