import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-25-2501: Architecture Decision Record (ADR) supersession chain ----
# An ADR supersedes an old one: the why is captured at decision time.
fig, ax = plt.subplots(figsize=(9.4, 3.8))
ax.set_xlim(0, 24); ax.set_ylim(0, 6); ax.axis('off')
ax.set_title('Architecture Decision Record: an ADR supersedes an old one', fontsize=11.5,
             fontweight='bold', color='#1a1a1a')

stages = ['Context', 'Options', 'Decision', 'Rationale', 'Consequences']
n = len(stages)
w = 3.2; gap = 1.2
total = n*w + (n-1)*gap
x0 = (24 - total)/2.0
z = 3.6
for i, name in enumerate(stages):
    x = x0 + i*(w+gap)
    ax.add_patch(FancyBboxPatch((x, z), w, 1.2, boxstyle='round,pad=0.05', fc='#3a6ea5', ec='#1a3a6b', lw=1.1))
    ax.text(x+w/2, z+0.6, name, ha='center', va='center', fontsize=10, color='white', fontweight='bold')
    if i < n-1:
        ax.annotate('', xy=(x+w+gap-0.1, z+0.6), xytext=(x+w+0.1, z+0.6),
                    arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#444'))

# feedback: consequences engender the next decision (supersession) -> back to context
ax.add_patch(FancyArrowPatch((x0+4*(w+gap)+w/2, z), (x0+w/2, z-2.2),
             connectionstyle='arc3,rad=-0.3', arrowstyle='-|>', lw=1.8, color='#c0392b',
             ls='--'))
ax.text(12.0, 1.2, 'consequences of a decision become the context of the next (why is captured at decision time)',
        fontsize=8.2, ha='center', color='#c0392b')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-25/figures/fig-25-2501.png', dpi=150)
plt.close()
print('wrote fig-25-2501')
