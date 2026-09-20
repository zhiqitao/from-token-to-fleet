import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 2026 Frontier Architecture data [1P]
# Horizontal paired bars: model name on the y-axis (full room, no collision),
# total vs active params on a log x-axis, active fraction annotated inline.
names = ['DeepSeek V4-Pro/Flash', 'Kimi K3', 'Qwen3.8-Flash-Next', 'GLM-5.3-Flash']
total_b = [284, 2800, 125, 320]       # total params (B) [1P]
active_b = [13, 104, 6, 18]           # active params (B) [1P]
frac = [a/t*100 for a, t in zip(active_b, total_b)]

fig, ax = plt.subplots(figsize=(6.1, 2.82))
y = np.arange(len(names))          # model index
h = 0.36

# horizontal bars (log x)
ax.barh(y + h/2, total_b, height=h, label='Total parameters', color='#4682b4')
ax.barh(y - h/2, active_b, height=h, label='Active parameters', color='#ff8c42')

# annotate each active bar with its fraction
for i in range(len(names)):
    ax.text(active_b[i]*1.15, y[i] - h/2, f'{frac[i]:.1f}% of total',
            va='center', fontsize=8.5, color='#b25a1e')

ax.set_xscale('log')
ax.set_yticks(y)
ax.set_yticklabels(names, fontsize=9.5)
ax.set_xlabel('Parameters (B, log scale)', fontsize=9.5)
ax.set_xlim(1, 9000)
ax.tick_params(labelsize=9.5)
ax.grid(alpha=0.3, which='both', axis='x')
# legend below the axes so it never overlaps the in-row % labels
ax.legend(fontsize=8.5, loc='upper center', bbox_to_anchor=(0.5, -0.16),
          ncol=2, frameon=False)

# the point, up front
ax.set_title('2026 frontier MoE: extreme sparsity —  single-digit active fraction of total',
             fontsize=10, loc='left')

plt.tight_layout()
out = 'design/manuscript/chapter-27/figures/fig-27-2701.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
