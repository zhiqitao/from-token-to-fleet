import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 2026 Frontier Architecture data [1P]
# Active fraction (%) per model, total/active params annotated.
# Layout tightened so EVERYTHING fits inside the 6.1in column at 11pt body scale.
names = ['DeepSeek V4-Pro/Flash', 'Kimi K3', 'Qwen3.8-Flash-Next', 'GLM-5.3-Flash']
total_b = [284, 2800, 125, 320]       # total params (B) [1P]
active_b = [13, 104, 6, 18]           # active params (B) [1P]
frac = [a/t*100 for a, t in zip(active_b, total_b)]

# Tightened figsize; y-axis label space reduced; xlim tight enough that the
# right-edge annotations stay inside the panel.
fig, ax = plt.subplots(figsize=(6.1, 3.30))
fig._hermes_print_sized = True   # print-size authored; regen must not re-boost/reflow

y = np.arange(len(names))[::-1]      # top-down listing
h = 0.55

# Two-tier annotation per row, BOTH placed WELL inside the axes:
#   1) fraction value JUST PAST the bar end (orange, bold)
#   2) "{total}B/{active}B active" placed at a fixed x within the axes
# Allocate the right third of the panel (x ∈ [axis_max*0.55, axis_max]) exclusively
# for annotations. Bars themselves top out near frac_max ~= 6%; truncate the bar
# plot x-axis at axis_max=7.0 but reserve the last 2.5 axis-units for labels.
axis_max = 7.0
ax.set_xlim(0, axis_max)
bar_label_x = axis_max * 0.55          # beyond this x, the param note lives
param_label_x = axis_max * 0.99         # hard right margin for param note

bars = ax.barh(y, frac, height=h, color='#ff8c42', edgecolor='none')

for i_orig, i_rev in enumerate(range(len(names))):
    a = active_b[i_orig]
    t = total_b[i_orig]
    fr = frac[i_orig]
    # Fraction
    ax.text(bar_label_x, y[i_rev], f'{fr:.1f}%',
            va='center', ha='left', fontsize=10.5, color='#b25a1e', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.18', fc='white', ec='none', alpha=0.85))
    # Param note — anchored to right edge, ha='right' pulls it inward so it
    # never bleeds past axis_max.
    ax.text(param_label_x, y[i_rev], f'{t}B/{a}B active',
            va='center', ha='right', fontsize=9.0, color='#555')

ax.set_yticks(y)
ax.set_yticklabels(names, fontsize=10.5)
ax.set_xlabel('Active parameters as % of total', fontsize=11)
ax.tick_params(labelsize=10)
ax.grid(alpha=0.3, axis='x')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Shorter, action-oriented title that fits the column at 6.1in width.
ax.set_title('Extreme sparsity: single-digit active (2026)',
             fontsize=11, loc='left', pad=4)

# Vendor-reported caveat as a compact one-line footnote BELOW the axis.
fig.text(0.04, 0.005,
         'VENDOR-REPORTED active fractions; parameter definitions vary across vendors.',
         fontsize=8.5, color='#777', ha='left', va='bottom')

# Tight layout reserves enough room for the y-tick labels and footer.
plt.subplots_adjust(left=0.36, right=0.99, top=0.90, bottom=0.20)
out = 'design/manuscript/chapter-27/figures/fig-27-2701.png'
plt.savefig(out, dpi=150)
import matplotlib as _mpl
with _mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-27/figures/fig-27-2701.pdf', format='pdf')
print('wrote', out)