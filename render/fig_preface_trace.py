import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# ---- preface traceability map, 2 columns of Parts (I-III / IV-VI) ----
# Each chapter is a stacked cell: [ChN] chip, derived quantity, decision. Cells in a
# 3-column grid inside each part band; bands sized to hold up to 2 cell rows.
parts = [
    ('Part I — The Token', [
        ('Ch1', 'token = cost unit', 'per-token price & KV floor'),
        ('Ch2', 'decode vs prefill', 'which resource binds'),
        ('Ch3', 'total vs active', 'model selection tier'),
        ('Ch4', 'six-dim fingerprint', 'what to characterize'),
    ]),
    ('Part II — The Workload', [
        ('Ch5', 'capability screen', 'which model family'),
        ('Ch6', 'SLOs + goodput', 'what to measure & gate'),
    ]),
    ('Part III — The System', [
        ('Ch7', 'KV/token x context', 'fit / concurrency'),
        ('Ch8', 'roofline vs ridge', 'compute- vs memory-bound'),
        ('Ch9', 'interconnect', 'comm cost'),
        ('Ch10', 'parallelism', 'GPUs / which split'),
        ('Ch11', 'batching, cache, P-D', 'serving stack'),
    ]),
    ('Part IV — The Architecture', [
        ('Ch12', 'candidate arch.', 'synthesis & score'),
        ('Ch13', 'tier ladder', 'deployment tier'),
        ('Ch14', 'two-stage bmark', 'accept / reject'),
        ('Ch15', 'congestion & MFU', 'fleet saturated?'),
        ('Ch16', 'TCO 3 modes', 'host/cloud/API'),
    ]),
    ('Part V — The Fleet', [
        ('Ch17', 'H = λL/(C·util)', 'fleet size'),
        ('Ch18', 'route by cap/cost', 'multi-model routing'),
        ('Ch19', 'KV per agent turn', 'depth x capacity'),
        ('Ch20', 'fleet req/s', 'QPS-vs-host'),
        ('Ch21', 'gate + rollback', 'safe rollout'),
    ]),
    ('Part VI — The Architect', [
        ('Ch22', 'bottleneck divergence', 'where to invest'),
        ('Ch23', 'vague ask -> bounds', 'scope the problem'),
        ('Ch24', 'red/green probe', 'stress-test design'),
        ('Ch25', 'ADR template', 'record the decision'),
        ('Ch26', 'workload->strategy', 'pick the pattern'),
        ('ApA', '2026 constants', 're-derive anchors'),
    ]),
]

fig, ax = plt.subplots(figsize=(6.6, 10.5))
ax.set_xlim(0, 15.0); ax.set_ylim(0, 25.0); ax.axis('off')
ax.set_title('Read the book two ways: layer-by-layer (parts) or '
             'question-by-question (traceability)\neach chapter supplies a '
             'derived quantity, which feeds a decision',
             fontsize=8.8, fontweight='bold')

COLW = 3.7          # part-band width
BAND_H = 3.4        # vertical space per part (holds 2 cell rows)
X0 = 0.3
col_x = [X0, X0 + 7.2]
col_parts = [parts[0:3], parts[3:6]]

for colidx, colgrp in enumerate(col_parts):
    bx = col_x[colidx]
    y_top = 23.8
    for ri, (ptitle, rows) in enumerate(colgrp):
        band_top = y_top - ri*BAND_H
        # part band
        ax.add_patch(FancyBboxPatch((bx-0.1, band_top-3.05), COLW+0.2, 3.3,
                     boxstyle='round,pad=0.0', fc='#eef2f7', ec='#3a6ea5', lw=1.0))
        ax.text(bx+0.06, band_top-0.22, ptitle, fontsize=6.6, fontweight='bold',
                color='#27408b', va='center')
        # 3-col grid of stacked cells, up to 2 rows
        for ci, (tag, qty, dec) in enumerate(rows):
            gx = bx + 0.25 + (ci % 3)*1.20
            gy = band_top - 1.45 - (ci // 3)*1.35
            # chip
            ax.add_patch(Rectangle((gx, gy), 0.52, 0.28, fc='#3a6ea5', ec='white'))
            ax.text(gx+0.26, gy+0.14, tag, fontsize=7.2, ha='center', va='center',
                    color='white', fontweight='bold')
            ax.text(gx+0.62, gy+0.14, qty, fontsize=6.9, color='#333', va='center')
            ax.text(gx+0.02, gy-0.22, '↓ '+dec, fontsize=6.7, color='#555', va='top')

plt.tight_layout()
plt.savefig('render/latex/assets/preface-trace.pdf', format='pdf', bbox_inches='tight')
plt.savefig('render/latex/assets/preface-trace.png', dpi=200, bbox_inches='tight')
plt.close()
print('wrote preface-trace.png/.pdf')
