import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# Fig A.3 — A conceptual layering of frontier AI systems (Appendix section 6)
# VERTICAL timeline: one full-width row per stage (labels never clip), with a
# separated legend and an approximate date band.  Color + border style give
# grayscale-safe redundancy.
steps = [
    ("Transformer", 'eff', '~2017'),
    ("Efficient Transformer", 'eff', '~2020'),
    ("MoE Transformer", 'effcap', '~2022'),
    ("Reasoning Model", 'cap', '~2023'),
    ("Test-Time Compute", 'cap', '~2024'),
    ("Tool-Using Model", 'cap', '~2024'),
    ("Agent", 'cap', '~2025'),
    ("Agent System", 'cap', '~2025'),
    ("Agent Fleet", 'fleet', '~2026'),
]
colors = {'eff': '#f0b35f', 'effcap': '#cf9240', 'cap': '#5a9bd5', 'fleet': '#8055b5'}
border = {'eff': '--', 'effcap': '--', 'cap': '-', 'fleet': '-'}

n = len(steps)
row_h = 1.0
fig, ax = plt.subplots(figsize=(6.6, 6.6))
ax.set_xlim(0, 12); ax.axis('off')

# Legend (three clearly separated rows at the top)
legend = [
    ('Efficiency-led (dashed) \u2014 context / cost / capacity', colors['eff'], '--', 1.2),
    ('Capability-led (solid) \u2014 reasoning / test-time / agentic', colors['cap'], '-', 1.2),
    ('Fleet (thick) \u2014 multi-model "intelligence placement"', colors['fleet'], '-', 2.4),
]
yl = n*row_h + 0.3
for text, col, ls, lw in legend:
    ax.add_patch(Rectangle((0.4, yl), 0.42, 0.42, fc=col, ec='#333', ls=ls, lw=lw))
    ax.text(0.92, yl+0.21, text, fontsize=8.5, color='#333', va='center')
    yl -= 0.75

y = yl - 0.4
for i, (name, kind, yr) in enumerate(steps):
    col = colors[kind]
    ax.add_patch(FancyBboxPatch((0.4, y), 9.6, row_h, boxstyle='round,pad=0.02',
                                fc=col, ec='#333', lw=1.4, ls=border[kind], alpha=0.92))
    ax.text(5.2, y+row_h/2, name, fontsize=8.5, fontweight='bold', color='white',
            ha='center', va='center')
    ax.text(10.35, y+row_h/2, yr, fontsize=8.2, color='#444', va='center', style='italic')
    if i < n-1:
        ax.annotate('', xy=(2.2, y-0.02), xytext=(2.2, y+0.02),
                    arrowprops=dict(arrowstyle='-', lw=1.0, color='#999'))
    y -= row_h + 0.18

# set the vertical limits to the actual content range (legend top .. caption bottom)
y_top = n*row_h + 0.9
y_bottom = y - 1.0
ax.set_ylim(y_bottom, y_top)

ax.text(5.9, y-0.35, 'From a single model to a whole system \u2014 the spine of this handbook (Appendix \u00a76).\n'
                    'Dates are approximate era markers for chronology, not release dates. [ILLUSTRATIVE][DERIVED]',
        fontsize=8, fontstyle='italic', color='#555', ha='center')

plt.tight_layout()
out = 'design/manuscript/chapter-27/figures/fig-27-2703.png'
plt.savefig(out, dpi=200, bbox_inches='tight', pad_inches=0.08)
print('wrote A.3 vertical timeline')
