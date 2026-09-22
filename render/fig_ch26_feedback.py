import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-26-2601: Pattern Application Diagram (capstone) ----
# The Pattern-Measurement-Feedback loop applied to the chapter's capstone
# scenario (Ch 26 §8), so each stage carries the concrete scenario quantities
# rather than abstract labels.  A bottom "composition" band shows how the
# three patterns the loop selects (A sharding, B cache, C circuit breaker)
# combine into the capstone outcome.  Authored at 6.1in wide.
fig, ax = plt.subplots(figsize=(6.1, 6.5))
ax.set_xlim(0, 20); ax.set_ylim(0, 14.6); ax.axis('off')

# ---- header: loop motto above title, scenario subtitle below ----
ax.text(10, 14.2, 'instrument \u2192 observe FACT \u2192 compute DERIVED \u2192 validate HYPOTHESIS \u2192 adjust pattern',
        fontsize=7.3, ha='center', color='#555')
ax.set_title('Pattern Application Diagram',
             fontsize=11.5, fontweight='bold', ha='center', color='#1a1a1a', pad=8)
ax.text(10, 12.9, 'the Pattern-Measurement-Feedback Loop applied to the capstone scenario (70B FP16 \u00b7 8\u00d7H100)',
        fontsize=8, ha='center', color='#555')

# ---- four stages of the closed loop, with capstone content ----
def box(x, y, w, h, fc, hatch):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05',
                                fc=fc, ec='#333', lw=1.0, hatch=hatch, alpha=0.93))

def stage_text(x, y, lines):
    tx = x + 0.35; ty = y + 2.15
    ax.text(tx, ty, lines[0], ha='left', va='top', color='white',
            fontsize=8.4, fontweight='bold')
    ax.text(tx, ty - 0.4, '\n'.join(lines[1:]), ha='left', va='top', color='white',
            fontsize=7.0, linespacing=1.35)

# Row 1 (top): FACT (top-left) -> DERIVED (top-right)
box(0.6, 10.0, 7.6, 2.6, '#2980b9', '||')
stage_text(0.6, 10.0, [
    '1  FACT \u00b7 instrument',
    'request rate ~2 QPS',
    'GPU utilization 45%',
    'TTFT: compute 320 ms',
    '  I/O 80 ms',
    '  cache miss 50 ms',
])

box(11.8, 10.0, 7.6, 2.6, '#16a085', 'xx')
stage_text(11.8, 10.0, [
    '2  DERIVED \u00b7 compute',
    'sharding \u21d2 decode is',
    '  bandwidth-bound',
    'cache 35% \u21d2 engine',
    '  load 2.0 \u2192 1.3 QPS',
    'TTFT p99: 210 ms',
])

# Row 2 (bottom): HYPOTHESIS (bottom-right) -> PATTERN/adjust (bottom-left)
box(11.8, 5.0, 7.6, 2.6, '#e67e22', 'oo')
stage_text(11.8, 5.0, [
    '3  HYPOTHESIS \u00b7 validate',
    '\u201csharding + caching',
    ' keeps TTFT p99',
    ' < 300 ms at 3\u00d7 growth\u201d',
    'load test (3,000 users):',
    'p99 = 285 ms \u00b7 cost \u2212 55%',
])

box(0.6, 5.0, 7.6, 2.6, '#c0392b', '\\\\\\\\')
stage_text(0.6, 5.0, [
    '4  PATTERN \u00b7 adjust / apply',
    'A \u00b7 Inference Sharding',
    'B \u00b7 Semantic Response Cache',
    'C \u00b7 Circuit Breaker',
    'accept \u00b7 reject \u00b7 compose',
])

# ---- clockwise connectors (each labelled with the transfer) ----
def arrow(p1, p2, color, lw=2.0, rad=0.0):
    ax.annotate('', xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle='-|>', lw=lw, color=color,
                                connectionstyle=f'arc3,rad={rad}'))

arrow((8.2, 11.3), (11.8, 11.3), '#2980b9')          # 1 -> 2
ax.text(10.0, 11.75, 'trace the\nquantity', fontsize=7.2, ha='center', color='#2980b9')

arrow((15.6, 10.0), (15.6, 7.6), '#16a085')          # 2 -> 3 (right side)
ax.text(17.2, 8.8, 'compare to\ntarget', fontsize=7.2, ha='left', va='center', color='#16a085')

arrow((11.8, 6.3), (8.2, 6.3), '#e67e22')            # 3 -> 4
ax.text(10.0, 5.7, 'confirm / reject', fontsize=7.2,
        ha='center', va='top', color='#e67e22')

# 4 -> 1 closes the loop up the left side (the feedback leg)
arrow((4.4, 7.6), (4.4, 10.0), '#a83232', lw=2.4, rad=-0.22)
ax.text(3.9, 8.8, 'adjust + pick pattern', fontsize=7.2, ha='right', va='center', color='#a83232')

ax.text(10, 4.35, 'feedback: the observed effect feeds the next cycle',
        fontsize=7.4, ha='center', color='#a83232')

# ---- composition band: the patterns the loop selected, applied together ----
ax.plot([0.4, 19.6], [4.05, 4.05], color='#bbb', lw=0.8, ls='--')
ax.text(10, 3.75, 'COMPOSITION \u2014 the patterns the loop selected, applied together',
        fontsize=7.8, ha='center', color='#333', fontweight='bold')

def pattern(x, w, name, parts, col, hatch):
    box(x, 0.9, w, 2.4, col, hatch)
    ax.text(x + 0.3, 3.15, name, ha='left', va='top', color='white',
            fontsize=7.8, fontweight='bold')
    ax.text(x + 0.3, 2.6, '\n'.join(parts), ha='left', va='top', color='white',
            fontsize=6.6, linespacing=1.3)

pattern(0.6, 6.1, 'A \u00b7 Inference Sharding', ['8\u00d7H100 80 GB, TP=8', 'decode \u2192 bandwidth-bound'], '#2980b9', '||')
pattern(6.9, 6.2, 'B \u00b7 Semantic Cache',    ['LRU, TTL 5 min', 'hit ratio ~35%'], '#16a085', 'xx')
pattern(13.3, 6.1, 'C \u00b7 Circuit Breaker', ['trip after 5 timeouts', '2-s grace period'], '#c0392b', '\\\\')

ax.text(10, 0.45, 'composed \u21d2 680 ms p99 \u00b7 40% lower generation cost (vs uncached, unsharded baseline)',
        fontsize=7.6, ha='center', color='#1a1a1a', fontweight='bold')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-26/figures/fig-26-2601.png',
            dpi=200, bbox_inches='tight', pad_inches=0.08)
plt.close()
print('wrote fig-26-2601 (capstone pattern-application)')
