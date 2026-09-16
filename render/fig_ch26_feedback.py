import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-26-2601: The Pattern-Measurement-Feedback Loop (closed control loop) ----
# A real closed loop, not a row of disconnected boxes.  Authored narrow
# (6.1in) with the cycle note ABOVE the title, generous spacing between rows,
# and connector labels placed clear of the boxes.
fig, ax = plt.subplots(figsize=(6.2, 5.4))
ax.set_xlim(0, 20); ax.set_ylim(0, 13); ax.axis('off')

ax.text(10, 12.5, 'measure \u2192 validate \u2192 adjust \u2192 remeasure', 
        fontsize=8.5, ha='center', color='#555')
ax.set_title('Pattern-Measurement-Feedback Loop',
             fontsize=11, fontweight='bold', ha='center', color='#1a1a1a', pad=10)
ax.text(10, 11.5, '(one closed cycle)', fontsize=8, ha='center', color='#555')

# Four stages laid out clockwise with clear gaps: Facts (top-left), Derived
# (top-right), Hypothesis (bottom-right), Adjust (bottom-left).
stages = [
    ('1  FACT\ninstruments', '#2980b9', '||', 0.6, 8.4),   # top-left
    ('2  DERIVED\ncomputes', '#16a085', 'xx', 12.4, 8.4), # top-right
    ('3  HYPOTHESIS\nvalidate', '#e67e22', 'oo', 12.4, 1.6), # bottom-right
    ('4  PATTERN\nadjust / decision', '#c0392b', '\\\\\\\\', 0.6, 1.6), # bottom-left
]
for label, col, hatch, x, y in stages:
    ax.add_patch(FancyBboxPatch((x, y), 7.4, 2.5, boxstyle='round,pad=0.05',
                                fc=col, ec='#333', lw=1.0, hatch=hatch, alpha=0.92))
    ax.text(x+3.7, y+1.25, label, ha='center', va='center', color='white',
            fontsize=9, fontweight='bold')

# Clockwise connectors (each labelled with the transfer, placed in the gap)
conns = [
    ((8.2, 9.65), (12.4, 9.65), 'trace the quantity', '#2980b9', (10.3, 10.4)),
    ((16.1, 8.4), (16.1, 4.1), 'compare to target', '#16a085', (17.0, 6.25)),
    ((11.2, 2.85), (8.0, 2.85), 'confirm / reject', '#e67e22', (9.6, 1.6)),
    ((0.6, 4.1), (0.6, 6.8), 'adjust\n+ pick pattern', '#c0392b', None),
]
for (x1, y1), (x2, y2), lab, col, labpos in conns:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', lw=2.0, color=col, connectionstyle='arc3,rad=0.0'))
    if labpos:
        ax.text(labpos[0], labpos[1], lab, fontsize=8, ha='center', color=col)
    else:
        ax.text(1.7, (y1+y2)/2, lab, fontsize=8, ha='left', va='center', color=col)

# Feedback arc: 'Adjust' back to 'Facts' along the left side, terminating at box 1
ax.annotate('', xy=(2.4, 8.4), xytext=(0.6, 4.1),
            arrowprops=dict(arrowstyle='-|>', lw=2.4, color='#a83232',
                            connectionstyle='arc3,rad=-0.30'))
ax.text(3.8, 6.4, 'feedback: observed\neffect feeds the next cycle',
        fontsize=8, ha='center', color='#a83232')

# Cross-pattern consequence tracing note at the bottom
ax.text(10, 0.4, 'cross-pattern consequence tracing: one pattern change can ripple into another',
        fontsize=7.5, ha='center', color='#666')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-26/figures/fig-26-2601.png',
            dpi=200, bbox_inches='tight', pad_inches=0.08)
plt.close()
print('wrote fig-26-2601 (closed loop)')
