import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Fig A.2 — Where should intelligence live? (Appendix section 7)
# Vertical stack of 8 host layers, each mapped to book chapters

fig, ax = plt.subplots(figsize=(6.1, 7.6))
fig._hermes_print_sized = True
ax.set_xlim(0, 8.0); ax.set_ylim(0, 10.8)
ax.axis('off')

layers = [
    ("Across a fleet of models", "Ch18, Ch20", '#27408b', 8.8),
    ("Inside agent runtime", "Ch17-20, Ch24", '#3a6ea5', 7.8),
    ("Inside tools", "Ch19, Ch24", '#4d8fc4', 6.8),
    ("Inside test-time search", "Ch8, Ch20", '#6aa0d8', 5.8),
    ("Inside post-training", "Ch19, Ch21", '#8fb8e0', 4.8),
    ("Inside MoE routing", "Ch10", '#4c7246', 3.8),
    ("Inside attention", "Ch7, Ch8", '#6f9e5f', 2.8),
    ("Inside weights", "Ch3, Ch8", '#9ac98a', 1.8),
]

# title (top, clear of the stack)
ax.text(4.0, 10.45, 'Where Should Intelligence Live?', fontsize=13, fontweight='bold', ha='center', color='#1a1a1a')
ax.text(4.0, 10.0, 'The 2026 frontier question for an AI Solution Architect (Appendix §7)', fontsize=9, ha='center', color='#555', style='italic')

# upward arrow in the left margin: points UP toward the externalized/fleet rows,
# matching the book's thesis that intelligence shifts up out of the weights.
# Label the axis as SCOPE OF PLACEMENT, NOT superiority (the vertical axis is location,
# not quality — there is no 'highest/best' tier).
ax.annotate('', xy=(0.45, 9.1), xytext=(0.45, 1.5),
            arrowprops=dict(arrowstyle='-|>', lw=2.3, color='#c0392b'))
# horizontalized side annotation (was rotation=90, awkward at book size):
ax.text(6.2, 0.95, 'scope of placement: intelligence shifts up out of the weights (vertical axis = WHERE it lives, not BETTER/HIGHER)',
        fontsize=8.0, color='#c0392b', ha='left', va='center')

for i, (name, ch, color, y) in enumerate(layers):
    box = FancyBboxPatch((1.0, y-0.42), 4.7, 0.82,
                         boxstyle='round,pad=0.02', fc=color, ec='none', alpha=0.92)
    ax.add_patch(box)
    ax.text(1.15, y, name, fontsize=8.6, fontweight='bold', color='white', va='center')
    ax.text(5.85, y, ch, fontsize=7.8, color='#333', va='center')

ax.text(4.0, 0.55, 'Model intelligence ≠ system intelligence', fontsize=9.5, fontweight='bold',
        ha='center', color='#c0392b', bbox=dict(boxstyle='round,pad=0.4', fc='#fdecea', ec='#c0392b'))

plt.tight_layout()
out = 'design/manuscript/chapter-27/figures/fig-27-2702.png'
plt.savefig(out, dpi=150)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-27/figures/fig-27-2702.pdf')
print('wrote', out)
