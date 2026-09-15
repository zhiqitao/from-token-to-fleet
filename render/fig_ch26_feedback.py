import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-26-2601: The Pattern-Measurement-Feedback Loop (closed control loop) ----
# A real closed loop, not a row of disconnected boxes:
#   FACT instruments -> DERIVED computes -> HYPOTHESIS validates -> pattern adjusts,
#   with a feedback arc back to the beginning and cross-pattern consequence tracing.
fig, ax = plt.subplots(figsize=(9, 6))
ax.set_xlim(0, 20); ax.set_ylim(0, 12); ax.axis('off')

ax.set_title('Pattern-Measurement-Feedback Loop (closed control loop)',
             fontsize=13, fontweight='bold', ha='center', color='#1a1a1a')
ax.text(10, 11.0, 'measure → validate → adjust → remeasure (one closed cycle)',
        fontsize=8.8, ha='center', color='#555')

# Four stages laid out clockwise: Facts (top-left), Derived (top-right),
# Hypothesis (bottom-right), Adjust (bottom-left).
stages = [
    ('1  FACT\ninstruments', '#2980b9', '||', 1.0, 8.6),   # top-left
    ('2  DERIVED\ncomputes', '#16a085', 'xx', 10.6, 8.6),  # top-right
    ('3  HYPOTHESIS\nvalidate', '#e67e22', 'oo', 10.6, 2.4), # bottom-right
    ('4  PATTERN\nadjust / decision', '#c0392b', '\\\\', 1.0, 2.4), # bottom-left
]
for label, col, hatch, x, y in stages:
    ax.add_patch(FancyBboxPatch((x, y), 7.6, 2.5, boxstyle='round,pad=0.05',
                                fc=col, ec='#333', lw=1.0, hatch=hatch, alpha=0.92))
    ax.text(x+3.8, y+1.25, label, ha='center', va='center', color='white',
            fontsize=10, fontweight='bold')

# Clockwise connectors (each labelled with the transfer)
conns = [
    ((4.8, 8.6), (10.6, 9.85), 'trace the quantity', '#2980b9'),
    ((14.4, 8.6), (14.4, 4.9), 'compare to target', '#16a085'),
    ((10.6, 2.4), (4.8, 2.4), 'confirm / reject', '#e67e22'),
    ((1.0, 2.4), (1.0, 4.9), 'adjust + pick pattern', '#c0392b'),
]
for (x1, y1), (x2, y2), lab, col in conns:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', lw=2.0, color=col))
    ax.text((x1+x2)/2, (y1+y2)/2 - 0.45, lab, fontsize=8, ha='center', color=col)

# Feedback arc: 'Adjust' back to 'Facts' (the loop closes) along the left side.
ax.annotate('', xy=(1.0, 6.6), xytext=(1.0, 4.9),
            arrowprops=dict(arrowstyle='-|>', lw=2.4, color='#a83232',
                            connectionstyle='arc3,rad=-0.35'))
ax.text(6.0, 5.6, 'feedback: observed effect feeds the next cycle',
        fontsize=8.5, ha='center', color='#a83232')

# Cross-pattern consequence tracing (a light note at the bottom)
ax.text(10, 0.7, 'cross-pattern consequence tracing: one pattern change can ripple into another',
        fontsize=8, ha='center', color='#666')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-26/figures/fig-26-2601.png', dpi=150)
plt.close()
print('wrote fig-26-2601 (closed loop)')
