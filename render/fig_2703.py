import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# Fig A.3 — The layered evolution of frontier systems (Appendix section 6)
# Horizontal chain: Transformer -> ... -> Agent Fleet, color-coded efficiency(adds context/cost) vs capability(raises intelligence)

fig, ax = plt.subplots(figsize=(8.8, 6.2))
ax.set_xlim(0, 16.6); ax.set_ylim(0, 7.8)
ax.axis('off')

steps = [
    ("Transformer", 'eff', 'e'),
    ("Efficient\nTransformer", 'eff', 'e'),
    ("MoE\nTransformer", 'eff+cap', 'e'),
    ("Reasoning\nModel", 'cap', 'c'),
    ("Test-Time\nCompute", 'cap', 'c'),
    ("Tool-Using\nModel", 'cap', 'c'),
    ("Agent", 'cap', 'c'),
    ("Agent\nSystem", '5', 'c'),
    ("Agent\nFleet", 'fleet', 'c'),
]

colors = {
    'eff': '#f0b35f',      # efficiency-led (amber)
    'eff+cap': '#cf9240',  # mixed
    'cap': '#5a9bd5',      # capability-led (blue)
    '5': '#5a9bd5',
    'fleet': '#8055b5',    # fleet (purple)
}

def color_of(k):
    return colors.get(k, '#888')

def border_of(k):
    # non-color group distinction: dashed border for efficiency-led, solid for capability-led
    return '--' if k in ('eff', 'eff+cap') else '-'

step_w = 1.68
x = 0.05
buttons = []
for i, (name, kind, tag) in enumerate(steps):
    box = FancyBboxPatch((x, 2.9), step_w, 2.0, boxstyle='round,pad=0.02',
                         fc=color_of(kind), ec='white', lw=1.2, linestyle=border_of(kind), alpha=0.9)
    ax.add_patch(box)
    ax.text(x+step_w/2, 3.9, name, fontsize=9.5, fontweight='bold', color='white', ha='center', va='center')
    # arrow to next
    if i < len(steps)-1:
        ax.annotate('', xy=(x+step_w+0.12, 3.9), xytext=(x+step_w+0.0, 3.9),
                    arrowprops=dict(arrowstyle='-|>', lw=2, color='#555'))
    x += step_w + 0.16

# legend: capability vs efficiency entries, each label immediately followed by its colour swatch, placed in the clear band above the box row
ax.add_patch(Rectangle((7.0, 6.3), 0.34, 0.34, fc=color_of('cap'), ec='none', alpha=0.9))
ax.text(7.42, 6.47, 'Capability-led (reasoning / test-time / agentic)', fontsize=10, color='#5a9bd5', va='center')
ax.add_patch(Rectangle((0.4, 6.3), 0.34, 0.34, fc=color_of('eff'), ec='none', alpha=0.9))
ax.text(0.82, 6.47, 'Efficiency-led (context / cost / capacity-per-FLOP)', fontsize=10, color='#cf9240', va='center')

ax.text(8.0, 1.0, 'From a single model to a whole system — the spine of this handbook (Appendix §6)', fontsize=10.5,
        fontstyle='italic', color='#555', ha='center')
ax.set_ylim(0, 7.8)

plt.tight_layout()
out = 'design/manuscript/chapter-27/figures/fig-27-2703.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
