import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

# ---- preface traceability map: 2 columns of Parts (I-III / IV-VI).  One
#      chapter per row inside each part band; derived quantity (left zone)
#      and decision hint (right zone) are kept short so they never collide.

parts = [
    ('Part I — The Token', [
        ('Ch1', 'token = cost', 'price & KV floor'),
        ('Ch2', 'decode vs prefill', 'which binds'),
        ('Ch3', 'total vs active', 'model tier'),
        ('Ch4', 'six-dim fingerprint', 'to characterize'),
    ]),
    ('Part II — The Workload', [
        ('Ch5', 'capability screen', 'model family'),
        ('Ch6', 'SLOs + goodput', 'measure & gate'),
    ]),
    ('Part III — The System', [
        ('Ch7', 'KV/token × ctx', 'fit & concurrency'),
        ('Ch8', 'roofline vs ridge', 'compute/mem-bound'),
        ('Ch9', 'interconnect', 'comm cost'),
        ('Ch10', 'parallelism', 'GPUs & split'),
        ('Ch11', 'batching/cache/P-D', 'serving stack'),
    ]),
    ('Part IV — The Architecture', [
        ('Ch12', 'candidate arch.', 'synthesis & score'),
        ('Ch13', 'tier ladder', 'deploy tier'),
        ('Ch14', 'two-stage bmark', 'accept / reject'),
        ('Ch15', 'congestion & MFU', 'fleet saturated?'),
        ('Ch16', 'TCO · 3 modes', 'host / cloud / API'),
    ]),
    ('Part V — The Fleet', [
        ('Ch17', 'H = λL/(C·util)', 'fleet size'),
        ('Ch18', 'route by cap/cost', 'multi-model routing'),
        ('Ch19', 'KV per agent turn', 'depth × capacity'),
        ('Ch20', 'fleet req/s', 'QPS vs host'),
        ('Ch21', 'gate + rollback', 'safe rollout'),
    ]),
    ('Part VI — The Architect', [
        ('Ch22', 'bottleneck diverge', 'where to invest'),
        ('Ch23', 'vague ask → bounds', 'scope it'),
        ('Ch24', 'red/green probe', 'stress-test design'),
        ('Ch25', 'ADR template', 'record decision'),
        ('Ch26', 'workload → strategy', 'pick pattern'),
        ('ApA', '2026 constants', 're-derive anchors'),
    ]),
]

fig, ax = plt.subplots(figsize=(7.4, 9.6))
ax.set_xlim(0, 16.0); ax.set_ylim(0, 42.0); ax.axis('off')
ax.set_title('Read the book two ways: layer-by-layer (parts) or '
             'question-by-question (traceability)\neach chapter supplies a '
             'derived quantity, which feeds a decision',
             fontsize=8.8, fontweight='bold')

COLW = 7.2          # part-band width (2 columns)
X0 = 0.4
col_x = [X0, X0 + 7.8]
col_parts = [parts[0:3], parts[3:6]]
ROW_H = 1.30
HEAD = 1.20
GAP = 0.50          # inter-band gap (was 0.7)

for colidx, colgrp in enumerate(col_parts):
    bx = col_x[colidx]
    y_cursor = 41.0
    for ptitle, rows in colgrp:
        band_h = HEAD + ROW_H * len(rows) + 0.35
        band_top = y_cursor
        y_cursor = band_top - band_h - GAP
        ax.add_patch(FancyBboxPatch((bx - 0.15, band_top - band_h),
                     COLW + 0.3, band_h, boxstyle='round,pad=0.02',
                     fc='#eef2f7', ec='#3a6ea5', lw=1.1))
        # Part title: clear top padding inside the band (not flush with border)
        ax.text(bx + 0.10, band_top - 0.42, ptitle, fontsize=8.9,
                fontweight='bold', color='#27408b', va='center')
        for ci, (tag, qty, dec) in enumerate(rows):
            ry = band_top - HEAD - (ci + 0.5) * ROW_H
            rx = bx + 0.14
            ax.add_patch(Rectangle((rx, ry - 0.16), 0.60, 0.32, fc='#27408b',
                                   ec='white', lw=0.6))
            ax.text(rx + 0.30, ry, tag, fontsize=8.4, ha='center', va='center',
                    color='white', fontweight='bold')
            # derived quantity — left zone
            ax.text(rx + 0.78, ry, qty, fontsize=8.6, color='#333', va='center')
            # decision — anchored to the band's right edge (never overruns)
            ax.text(rx + COLW - 0.18, ry, '→ ' + dec, fontsize=8.4,
                    color='#555', va='center', ha='right')

plt.tight_layout()
plt.savefig('render/latex/assets/preface-trace.pdf', format='pdf', bbox_inches='tight')
plt.savefig('render/latex/assets/preface-trace.png', dpi=200, bbox_inches='tight')
plt.close()
print('wrote preface-trace.png/.pdf')
