import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-26-2601: Pattern Application Diagram (capstone) ----
# The Pattern-Measurement-Feedback loop applied to the chapter's capstone scenario
# (Ch 26 §8). Simpler/prose-backed redesign: a closed 3-stage clockwise CYCLE
# (FACT -> DERIVED -> PATTERN -> back to FACT), flat fills (no heavy hatching), and
# larger type. Per-pattern composition detail (A/B/C) lives in the caption/prose.
fig, ax = plt.subplots(figsize=(6.1, 4.9))
fig._hermes_print_sized = True   # regen must not re-boost/reflow this figure
ax.set_xlim(0, 20); ax.set_ylim(0, 11.4); ax.axis('off')

ax.set_title('Pattern Application Diagram',
             fontsize=12.5, fontweight='bold', ha='center', color='#1a1a1a', pad=6)
ax.text(10, 10.6, 'the Pattern-Measurement-Feedback Loop on the capstone scenario (70B FP16 · 8×H100)',
        fontsize=9, ha='center', color='#555')

def box(x, y, w, h, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05',
                                fc=fc, ec='#333', lw=1.2, alpha=0.92))

def stage_text(x, y, lines, big):
    # text kept SHORT so it never clips the box width (box w=7.4 at x). 
    tx = x + 0.5; ty = y + 2.0
    ax.text(tx, ty, lines[0], ha='left', va='top', color='white', fontsize=big, fontweight='bold')
    ax.text(tx, ty - 0.55, '\n'.join(lines[1:]), ha='left', va='top', color='white',
            fontsize=8.2, linespacing=1.4)

BW = 7.4
# Top row: FACT (left) -> DERIVED (right)
box(0.8, 7.4, BW, 2.5, '#2980b9')
stage_text(0.8, 7.4, ['1 · FACT',
                      'request rate ~2 rps',
                      'utilization 45%',
                      'TTFT 320 ms'], big=9.8)
box(11.8, 7.4, BW, 2.5, '#16a085')
stage_text(11.8, 7.4, ['2 · DERIVED',
                       'sharding ⇒ bandwd-bound',
                       'cache 35% ⇒ 2.0→1.3 rps',
                       'TTFT p99 210 ms'], big=9.8)

# Bottom row: PATTERN (right, below DERIVED) so the flow turns clockwise
box(11.8, 1.0, BW, 2.5, '#c0392b')
stage_text(11.8, 1.0, ['3 · PATTERN',
                       'A · Inference Sharding',
                       'B · Semantic Cache',
                       'C · Circuit Breaker'], big=9.8)

def arrow(p1, p2, color, lw=2.2, rad=0.0):
    ax.annotate('', xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle='-|>', lw=lw, color=color,
                                connectionstyle=f'arc3,rad={rad}'))

# Step 1 -> 2 (top, left to right), short label fitted in the narrow gap
arrow((8.2 + 0.1, 8.65), (11.8, 8.65), '#2980b9')
ax.text(10.0, 8.15, 'trace', fontsize=8.2, ha='center', color='#2980b9', fontweight='bold')
# Step 2 -> 3 (right side, down)
arrow((15.5, 7.4), (15.5, 3.5), '#16a085')
ax.text(16.6, 5.4, 'validate', fontsize=8.5, ha='left', va='center', color='#16a085', fontweight='bold')

# Step 3 -> 1: a SINGLE L-shaped return edge (left along the bottom, then up the left
# side to FACT), so the loop closes unambiguously.
from matplotlib.path import Path
ret_verts = [(11.8, 2.25), (4.5, 2.25), (4.5, 7.4)]
ret_codes = [Path.MOVETO, Path.LINETO, Path.LINETO]
ax.add_patch(FancyArrowPatch(path=Path(ret_verts, ret_codes), arrowstyle='-|>',
             mutation_scale=18, lw=2.6, color='#a83232', zorder=1))
ax.text(8.0, 1.7, 'adjust + pick pattern', fontsize=8.5, ha='center', color='#a83232', fontweight='bold')
ax.text(3.9, 5.4, 'feedback', fontsize=8.5, ha='right', va='center', color='#a83232', fontweight='bold')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-26/figures/fig-26-2601.png',
            dpi=200, bbox_inches='tight', pad_inches=0.08)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-26/figures/fig-26-2601.pdf', format='pdf', bbox_inches='tight')
plt.close()
print('wrote fig-26-2601 (capstone pattern-application, closed 3-stage cycle)')
