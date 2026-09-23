import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 2026 Frontier Architecture data [1P]
# Re-encoded so the sparsity message is visually primary: a LINEAR bar of the
# active fraction (% of total) per model, since on a log x-axis bar LENGTH is
# proportional to log(value) and a 20-27x total:active ratio collapses to a fixed
# log-distance. Plotting the fraction directly makes "single-digit active" the
# dominant visual, with total/active params annotated alongside.
names = ['DeepSeek V4-Pro/Flash', 'Kimi K3', 'Qwen3.8-Flash-Next', 'GLM-5.3-Flash']
total_b = [284, 2800, 125, 320]       # total params (B) [1P]
active_b = [13, 104, 6, 18]           # active params (B) [1P]
frac = [a/t*100 for a, t in zip(active_b, total_b)]

fig, ax = plt.subplots(figsize=(6.1, 2.82))
y = np.arange(len(names))          # model index
h = 0.5

# set xlim with room for the row annotations (defined before the annotation loop)
axis_max = 11.0
ax.set_xlim(0, axis_max)

bars = ax.barh(y, frac, height=h, color='#ff8c42', edgecolor='none')

# annotate within/beside each bar: the fraction, plus the underlying params
for i in range(len(names)):
    # fraction value at the bar end
    ax.text(frac[i] + 0.12, y[i], f'{frac[i]:.1f}%',
            va='center', fontsize=10.5, color='#b25a1e', fontweight='bold')
    # total / active params annotation to the right of the row (clear of the bar)
    ax.text(axis_max, y[i], f'  {total_b[i]}B total / {active_b[i]}B active',
            va='center', fontsize=9.5, color='#555')

ax.set_yticks(y)
ax.set_yticklabels(names, fontsize=11.5)
ax.set_xlabel('Active parameters as % of total', fontsize=11.5)
ax.tick_params(labelsize=11.5)
ax.grid(alpha=0.3, axis='x')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# the point, up front
ax.set_title('2026 frontier MoE: extreme sparsity —  single-digit active fraction of total',
             fontsize=12, loc='left')
ax.text(0.0, -0.16, 'VENDOR-REPORTED active-parameter fractions (mutable snapshot, ~2026 mid-year);\nparameter definitions are not perfectly harmonized across vendors',
        transform=ax.transAxes, fontsize=9.5, color='#555', va='top')

plt.tight_layout()
out = 'design/manuscript/chapter-27/figures/fig-27-2701.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
