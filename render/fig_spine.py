import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- spine-decision-loop: the architect's decision loop (the book's spine) ----
# Redrawn (v8 review) so the main path and the feedback loop are EXPLICIT:
#   * a clear downward main path with arrowheads between the four stages,
#   * a visible "iterate" feedback loop (Commit -> Understand) on the right,
#   * transition labels anchored to their arrows (not floating on the borders),
#   * no distracting glyph markers.
# Color identity is preserved from the archify version:
#   Understand = slate blue, Design & size = emerald, Validate & Defend = violet,
#   Commit = crimson.
fig, ax = plt.subplots(figsize=(6.1, 6.4))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.set_xlim(-2.5, 26); ax.set_ylim(0, 30); ax.axis('off')
ax.set_title("The architect's decision loop", fontsize=12, fontweight='bold',
             color='#1a1a1a', pad=12)

stages = [
    # (num, title, subtitle, tag, fill, edge)
    ('01', 'Understand',        'requirements & workload',        'inputs',    '#e8edf3', '#34495e'),
    ('02', 'Design & size',     'candidates, benchmark, bottleneck','work',     '#e7f5ec', '#1e8449'),
    ('03', 'Validate & Defend', 'TCO, recommendation',            'economics', '#f0eaf7', '#7d3c98'),
    ('04', 'Commit',            'red team, then final choice',    'decide',    '#fdecea', '#c0392b'),
]
transitions = ['define', 'size', 'justify']   # main-path labels (3 gaps)

bx = 4.0          # box left
bw = 13.0         # box width
bh = 5.0          # box height (room for title + subtitle + tag on 3 lines)
gap = 2.4         # vertical gap between boxes (room for the main-path arrow + label)
top = 28.5        # top of the first box

def box_top(i):
    return top - i*(bh+gap)

# draw the four stage boxes
for i, (num, title, sub, tag, fill, edge) in enumerate(stages):
    y = box_top(i)
    ax.add_patch(FancyBboxPatch((bx, y-bh), bw, bh, boxstyle='round,pad=0.06,rounding_size=0.5',
                 fc=fill, ec=edge, lw=1.8))
    ax.text(bx+0.7, y-1.0, f'{num}  {title}', ha='left', va='center',
            fontsize=11.5, fontweight='bold', color=edge)
    ax.text(bx+0.7, y-2.4, sub, ha='left', va='center', fontsize=9.0, color='#555')
    ax.text(bx+0.7, y-3.8, tag, ha='left', va='center', fontsize=8.5,
            color=edge, style='italic')

# main path: downward arrows between consecutive boxes, centered, with anchored labels
cx = bx + bw/2
for i in range(3):
    y_from = box_top(i) - bh          # bottom of box i
    y_to   = box_top(i+1)             # top of box i+1
    ax.add_patch(FancyArrowPatch((cx, y_from), (cx, y_to),
                 arrowstyle='-|>', mutation_scale=22, lw=2.4, color='#34495e'))
    ax.text(cx+0.5, (y_from+y_to)/2, transitions[i], ha='left', va='center',
            fontsize=9.5, fontweight='bold', color='#34495e',
            bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.9))

# feedback loop: Commit (right) -> Understand (right), a visible loop on the
# right side, routed OUTSIDE the boxes (positive rad bulges right) so it never
# crosses the box text.
y_commit_mid = box_top(3) - bh/2
y_understand_mid = box_top(0) - bh/2
x_right = bx + bw          # endpoints at the box right edges (connected)
ax.add_patch(FancyArrowPatch((x_right, y_commit_mid), (x_right, y_understand_mid),
             connectionstyle='arc3,rad=0.4', arrowstyle='-|>', mutation_scale=22,
             lw=2.4, color='#c0392b', ls='dashed'))
ax.text(x_right+5.0, (y_commit_mid+y_understand_mid)/2, 'iterate', ha='left', va='center',
        fontsize=9.5, fontweight='bold', color='#c0392b', rotation=90,
        bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.9))

# inner loop: Validate & Defend (left) -> Design & size (left), a failed
# benchmark/TCO returns to re-derive the candidate. Routed OUTSIDE the boxes on
# the left (negative rad bulges left) so it never crosses the box text.
y_validate_mid = box_top(2) - bh/2
y_design_mid   = box_top(1) - bh/2
x_left = bx
ax.add_patch(FancyArrowPatch((x_left, y_validate_mid), (x_left, y_design_mid),
             connectionstyle='arc3,rad=-0.5', arrowstyle='-|>', mutation_scale=22,
             lw=2.4, color='#1e8449', ls='dashed'))
ax.text(x_left-1.2, (y_validate_mid+y_design_mid)/2, 're-derive', ha='right', va='center',
        fontsize=9.0, fontweight='bold', color='#1e8449', rotation=90,
        bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.9))

plt.tight_layout()
plt.savefig('render/latex/assets/spine-decision-loop.png',
            dpi=200, bbox_inches='tight', pad_inches=0.08)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('render/latex/assets/spine-decision-loop.pdf', format='pdf',
                bbox_inches='tight', pad_inches=0.08)
plt.close()
print('wrote spine-decision-loop (explicit main path + iterate feedback loop)')
