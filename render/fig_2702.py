import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Fig A.2 — Where should intelligence live? (Appendix section 7)
# Vertical stack of 8 host layers, each mapped to book chapters

fig, ax = plt.subplots(figsize=(11, 9))
ax.set_xlim(0, 11); ax.set_ylim(0, 10.8)
ax.axis('off')

layers = [
    ("Across a fleet of specialised models", "Ch18 Operating Multiple Models, Ch20 Fleet-Level Optimization", '#27408b', 8.8),
    ("Inside the agent runtime", "persistent state, runbooks, execution control — Ch17-20, Ch24", '#3a6ea5', 7.8),
    ("Inside tools", "compute allocated via a harness — Ch19 Agentic, Ch24", '#4d8fc4', 6.8),
    ("Inside test-time search", "adaptive inference, more compute on hard tasks — Ch8, Ch20", '#6aa0d8', 5.8),
    ("Inside post-training", "reasoning, RL, verification — Ch19 Agentic, Ch21 Factory", '#8fb8e0', 4.8),
    ("Inside MoE routing", "capacity per FLOP — Ch10 Parallelism", '#4c7246', 3.8),
    ("Inside attention", "context / efficiency — Ch7 Memory, Ch8 Compute", '#6f9e5f', 2.8),
    ("Inside weights", "dense capacity — Ch3 Model, Ch8 Compute", '#9ac98a', 1.8),
]

# title (top, clear of the stack which ends at y=9.22)
ax.text(5.5, 10.45, 'Where Should Intelligence Live?', fontsize=15, fontweight='bold', ha='center', color='#1a1a1a')
ax.text(5.5, 10.0, 'The 2026 frontier question for an AI Solution Architect (Appendix §7)', fontsize=10, ha='center', color='#555', style='italic')

# upward arrow in the left margin, clear of the box column (boxes start at x=1.0)
ax.annotate('', xy=(0.5, 1.5), xytext=(0.5, 9.1),
            arrowprops=dict(arrowstyle='-|>', lw=2.5, color='#c0392b'))
ax.text(0.6, 5.3, 'more of the intelligence\nand compute budget', fontsize=9, color='#c0392b', rotation=90, va='center', ha='left')

for i, (name, ch, color, y) in enumerate(layers):
    box = FancyBboxPatch((1.0, y-0.42), 6.9, 0.82,
                         boxstyle='round,pad=0.02', fc=color, ec='none', alpha=0.92)
    ax.add_patch(box)
    ax.text(1.2, y, name, fontsize=11.5, fontweight='bold', color='white', va='center')
    ax.text(8.1, y, ch, fontsize=8, color='#333', va='center')

ax.text(5.5, 0.55, 'Model intelligence ≠ system intelligence', fontsize=11, fontweight='bold',
        ha='center', color='#c0392b', bbox=dict(boxstyle='round,pad=0.4', fc='#fdecea', ec='#c0392b'))

plt.tight_layout()
out = 'design/manuscript/chapter-27/figures/fig-27-2702.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
