import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# Fig A.3 — The layered evolution of frontier systems (Appendix section 6)
# Horizontal chain: Transformer -> ... -> Agent Fleet, color-coded efficiency(adds context/cost) vs capability(raises intelligence)

fig, ax = plt.subplots(figsize=(16, 5.5))
ax.set_xlim(0, 16); ax.set_ylim(0, 5.5)
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

step_w = 1.42
x = 0.4
buttons = []
for i, (name, kind, tag) in enumerate(steps):
    box = FancyBboxPatch((x, 1.9), step_w, 1.7, boxstyle='round,pad=0.02',
                         fc=color_of(kind), ec='none', alpha=0.9)
    ax.add_patch(box)
    ax.text(x+step_w/2, 2.75, name, fontsize=10.5, fontweight='bold', color='white', ha='center', va='center')
    # arrow to next
    if i < len(steps)-1:
        ax.annotate('', xy=(x+step_w+0.12, 2.75), xytext=(x+step_w+0.0, 2.75),
                    arrowprops=dict(arrowstyle='-|>', lw=2, color='#555'))
    x += step_w + 0.22

# legend: capability vs efficiency entries, each label immediately followed by its colour swatch, placed in the clear band above the box row
ax.add_patch(Rectangle((7.0, 4.85), 0.32, 0.32, fc=color_of('cap'), ec='none', alpha=0.9))
ax.text(7.4, 5.01, 'Capability-led (reasoning / test-time / agentic)', fontsize=9, color='#5a9bd5', va='center')
ax.add_patch(Rectangle((0.4, 4.85), 0.32, 0.32, fc=color_of('eff'), ec='none', alpha=0.9))
ax.text(0.8, 5.01, 'Efficiency-led (context / cost / capacity-per-FLOP)', fontsize=9, color='#cf9240', va='center')

ax.text(8.0, 0.6, 'From a single model to a whole system — the spine of this handbook (Appendix §6)', fontsize=10,
        fontstyle='italic', color='#555', ha='center')
ax.set_ylim(0, 5.6)

plt.tight_layout()
out = 'design/manuscript/chapter-27/figures/fig-27-2703.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
