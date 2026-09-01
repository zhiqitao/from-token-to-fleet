import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# ---- preface traceability strips: Each PART gets a band, then its chapters' derived-quantity -> decision ----
parts = [
    ('Part I — The Token', [
        ('Ch1', 'token = cost unit', 'per-token price & KV floor'),
        ('Ch2', 'decode vs prefill', 'which resource binds'),
        ('Ch3', 'total vs active', 'model selection tier'),
        ('Ch4', 'six-dimension fingerprint', 'what to characterize'),
    ]),
    ('Part II — The Workload', [
        ('Ch5', 'capability screen', 'which model family'),
        ('Ch6', 'SLOs + goodput', 'what to measure & gate'),
    ]),
    ('Part III — The System', [
        ('Ch7', 'KV/token × context', 'does it fit / concurrency'),
        ('Ch8', 'roofline: AI vs ridge', 'compute- vs memory-bound'),
        ('Ch9', 'interconnect (time-vs-size)', 'comm cost'),
        ('Ch10', 'parallelism composition', 'how many GPUs / which split'),
        ('Ch11', 'batching / caching / P-D', 'serving stack'),
    ]),
    ('Part IV — The Architecture', [
        ('Ch12', 'candidate architectures', 'synthesis & score'),
        ('Ch13', 'reference tier ladder', 'deployment tier'),
        ('Ch14', 'two-stage benchmark', 'accept / reject'),
        ('Ch15', 'congestion & MFU', 'is the fleet saturated'),
        ('Ch16', 'TCO three modes', 'self-host vs cloud vs API'),
    ]),
    ('Part V — The Fleet', [
        ('Ch17', 'hosts H = λL/(C·util)', 'fleet size'),
        ('Ch18', 'route by capability/cost', 'multi-model routing'),
        ('Ch19', 'token/KV per agent turn', 'depth × capacity'),
        ('Ch20', 'fleet req/s @3.7/host', 'QPS-vs-host'),
        ('Ch21', 'promote via gate+rollback', 'safe rollout'),
    ]),
    ('Part VI — The Architect', [
        ('Ch22', 'bottleneck divergence', 'where to invest'),
        ('Ch23', 'vague ask → bounds', 'scope the problem'),
        ('Ch24', 'red/green probe', 'stress-test design'),
        ('Ch25', 'ADR template', 'record the decision'),
        ('Ch26', 'workload → strategy matrix', 'pick the pattern'),
        ('ApA', '2026 constants vs canonical', 're-derive anchors'),
    ]),
]

fig, ax = plt.subplots(figsize=(16, 13))
ax.set_xlim(0, 18.5); ax.set_ylim(0, 13.2); ax.axis('off')
ax.set_title('Read the book two ways: layer-by-layer (parts) or question-by-question (traceability)\neach chapter supplies a derived quantity, which feeds a decision',
             fontsize=12, fontweight='bold')

row_h = 1.9
X0 = 0.6
COLW = 2.95
COLW_fixed = 2.55   # fixed width for the text column after each chip

y_top = 12.3
# rows go downward; band at top of each row region, chips below in the row
for ri, (title, rows) in enumerate(parts):
    y_band = y_top - ri*row_h - 0.5
    # Part title band (own dedicated strip), stops short of the last chip's text
    ax.add_patch(FancyBboxPatch((X0-0.2, y_band-0.3), 17.6, 0.55, boxstyle='round,pad=0.0', fc='#eef2f7', ec='#3a6ea5', lw=1.3))
    ax.text(X0+0.1, y_band+0.0, title, fontsize=10.5, fontweight='bold', color='#27408b', va='center')
    # chapter cells beneath the band
    cy = y_band - 0.95
    for ci, (tag, qty, dec) in enumerate(rows):
        cx = X0 + ci*COLW
        # chip
        ax.add_patch(Rectangle((cx, cy), 0.95, 0.5, fc='#3a6ea5', ec='white'))
        ax.text(cx+0.47, cy+0.25, tag, fontsize=9, ha='center', va='center', color='white', fontweight='bold')
        # derived quantity; keep short enough to never truncate
        ax.text(cx+1.1, cy+0.25, qty, fontsize=8.0, color='#333', va='center',
                bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none'))
        # decision below (indented), arrow down
        ax.text(cx+0.2, cy-0.5, '↳ '+dec, fontsize=7.6, color='#555', va='top')

plt.tight_layout()
plt.savefig('render/latex/assets/preface-trace.png', dpi=160, bbox_inches='tight')
plt.close()
print('wrote preface-trace.png')
