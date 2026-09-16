import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-25-2501: Architecture Decision Record (ADR) supersession chain ----
# Authored at ~6.1in (print column) so it places 1:1 and nothing clips.  The
# last box ('Consequences') has generous right margin; the loop annotation is
# short so it never self-overlaps.
fig, ax = plt.subplots(figsize=(6.1, 3.2))
ax.set_xlim(0, 26); ax.set_ylim(0, 7.2); ax.axis('off')
ax.set_title('Architecture Decision Record: an ADR supersedes an old one', fontsize=9.5,
             fontweight='bold', color='#1a1a1a')

stages = ['Context', 'Options', 'Decision', 'Rationale', 'Consequences']
n = len(stages)
w = 4.6; gap = 0.7
total = n*w + (n-1)*gap
x0 = (24 - total)/2.0
z = 3.6
for i, name in enumerate(stages):
    x = x0 + i*(w+gap)
    ax.add_patch(FancyBboxPatch((x, z), w, 1.2, boxstyle='round,pad=0.05', fc='#3a6ea5', ec='#1a3a6b', lw=1.1))
    ax.text(x+w/2, z+0.6, name, ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')
    if i < n-1:
        ax.annotate('', xy=(x+w+gap-0.1, z+0.6), xytext=(x+w+0.1, z+0.6),
                    arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#444'))

# feedback: consequences -> context (supersession loop), kept clear of the caption
ax.add_patch(FancyArrowPatch((x0+4*(w+gap)+w/2, z), (x0+w/2, z-1.9),
             connectionstyle='arc3,rad=-0.32', arrowstyle='-|>', lw=1.8, color='#c0392b',
             ls='--'))
ax.text(15.0, 1.9, 'consequences of one decision become the\ncontext of the next (why is captured at decision time)',
        fontsize=8.5, ha='center', va='center', color='#c0392b',
        bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='none', alpha=0.95))

plt.tight_layout()
plt.savefig('design/manuscript/chapter-25/figures/fig-25-2501.png',
            dpi=200, bbox_inches='tight', pad_inches=0.08)
plt.close()
print('wrote fig-25-2501 (narrow)')
