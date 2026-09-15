import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# Fig A.3 — The layered evolution of frontier systems (Appendix section 6)
# Horizontal chain: Transformer -> ... -> Agent Fleet, color-coded efficiency
# (adds context/cost) vs capability (raises intelligence).  Symbol + color +
# border style give grayscale-safe redundancy; an approximate date band makes
# the chronology explicit.
fig, ax = plt.subplots(figsize=(9.4, 6.4))
ax.set_xlim(0, 18.2); ax.set_ylim(0, 8.2)
ax.axis('off')

steps = [
    ("Transformer", 'eff', 'e', '~2017'),
    ("Efficient\nTransformer", 'eff', 'e', '~2020'),
    ("MoE\nTransformer", 'eff+cap', 'E', '~2022'),
    ("Reasoning\nModel", 'cap', 'c', '~2023'),
    ("Test-Time\nCompute", 'cap', 'c', '~2024'),
    ("Tool-Using\nModel", 'cap', 'c', '~2024'),
    ("Agent", 'cap', 'C', '~2025'),
    ("Agent\nSystem", 'cap', 'C', '~2025'),
    ("Agent\nFleet", 'fleet', 'F', '~2026'),
]
colors = {'eff': '#f0b35f', 'eff+cap': '#cf9240', 'cap': '#5a9bd5', 'fleet': '#8055b5'}
# Non-color symbol per group
sym = {'eff': 'A', 'eff+cap': 'B', 'cap': 'C', 'fleet': 'F'}
# Border: dashed for efficiency/mixed, solid for capability, thick for fleet
border = {'eff': '--', 'eff+cap': '--', 'cap': '-', 'fleet': '-'}

step_w = 1.86
x = 0.5
for i, (name, kind, tag, yr) in enumerate(steps):
    lw = 2.4 if kind == 'fleet' else 1.2
    box = FancyBboxPatch((x, 3.0), step_w, 2.2, boxstyle='round,pad=0.02',
                         fc=colors[kind], ec='white', lw=lw, linestyle=border[kind], alpha=0.9)
    ax.add_patch(box)
    ax.text(x+step_w/2, 4.1, name, fontsize=8.3, fontweight='bold', color='white',
            ha='center', va='center')
    # date below the box (makes chronology explicit, non-color)
    ax.text(x+step_w/2, 2.55, yr, fontsize=8.5, color='#444', ha='center', style='italic')
    # next arrow
    if i < len(steps)-1:
        ax.annotate('', xy=(x+step_w+0.12, 4.1), xytext=(x+step_w+0.0, 4.1),
                    arrowprops=dict(arrowstyle='-|>', lw=2, color='#555'))
    x += step_w + 0.10

# Legend: two swatches at clearly separated positions along one band (top, high y)
ax.add_patch(Rectangle((0.4, 6.9), 0.34, 0.34, fc=colors['eff'], ec='#333', ls='--', lw=1.0))
ax.text(0.82, 7.07, 'Efficiency-led (dashed) — context / cost / capacity-per-FLOP [A]',
        fontsize=9.5, color='#cf9240', va='center')
ax.add_patch(Rectangle((11.6, 6.9), 0.34, 0.34, fc=colors['cap'], ec='#333', lw=1.0))
ax.text(12.02, 7.07, 'Capability-led (solid) — reasoning / test-time / agentic [C]',
        fontsize=9.5, color='#5a9bd5', va='center')
ax.add_patch(Rectangle((6.4, 6.0), 0.34, 0.34, fc=colors['fleet'], ec='#333', lw=2.0))
ax.text(6.82, 6.17, 'Fleet [F] — the multi-model "intelligence placement" end', fontsize=9.5,
        color='#8055b5', va='center')

ax.text(8.6, 0.9, 'From a single model to a whole system — the spine of this handbook (Appendix §6).\n'
                  'Dates are approximate era markers for chronology, not release dates. [2° DERIVED]',
        fontsize=9, fontstyle='italic', color='#555', ha='center')
ax.set_ylim(0, 8.2)
plt.tight_layout()
out = 'design/manuscript/chapter-27/figures/fig-27-2703.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
