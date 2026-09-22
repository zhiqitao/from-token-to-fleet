#!/usr/bin/env python3
"""fig-06-0601: the metric hierarchy as a diagnostic chain.

PASS-24 fix: the Archify version drew two plain vertical rails (solid-green left,
red-dashed right) with NO arrowheads, so the causal-vs-diagnostic direction was only
explained in a detached legend. This matplotlib version puts an arrowhead on every
connector: solid-green DOWN = causation (workload -> serving) and red-dashed UP =
diagnosis (serving -> workload). Direction now reads off the diagram itself, and the
two rails are distinguished by both style AND colour.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

FS = 9.0
W = 6.1
fig, ax = plt.subplots(figsize=(W, W*0.78))
fig._hermes_print_sized = True
ax.set_xlim(0, 10); ax.set_ylim(0, 7.8); ax.axis('off')

levels = [
    ('Workload metrics', 'tokens/s · context · response-time', '#e7f5ec', '#1e8449', 6.4),
    ('Resource metrics', 'GPU util · memory · bandwidth', '#e7f5ec', '#1e8449', 4.3),
    ('Serving metrics', 'TTFT · TPOT · goodput · KV', '#e7f5ec', '#1e8449', 2.2),
]
bw, bh = 7.4, 1.4
xc = 5.0
for (name, sub, fc, ec, y) in levels:
    ax.add_patch(FancyBboxPatch((xc-bw/2, y-bh/2), bw, bh, boxstyle='round,pad=0.02,rounding_size=0.3',
                                fc=fc, ec=ec, lw=1.4))
    ax.text(xc, y+0.22, name, ha='center', va='center', fontsize=FS, fontweight='bold', color='#1a1a1a')
    ax.text(xc, y-0.34, sub, ha='center', va='center', fontsize=7.8, color='#3a5a3a')

# ---- CAUSATION rail: solid-green, arrows point DOWN (workload -> serving) ----
x_c = xc - bw/2 + 0.15
for y_top, y_bot in [(6.4, 4.3), (4.3, 2.2)]:
    ax.annotate('', xy=(x_c, y_bot+0.62), xytext=(x_c, y_top-0.62),
                arrowprops=dict(arrowstyle='-|>', lw=2.2, color='#1e8449', shrinkA=0, shrinkB=0))

# ---- DIAGNOSIS rail: red-dashed, arrows point UP (serving -> workload) ----
x_d = xc + bw/2 - 0.15
for y_top, y_bot in [(6.4, 4.3), (4.3, 2.2)]:
    ax.annotate('', xy=(x_d, y_top-0.62), xytext=(x_d, y_bot+0.62),
                arrowprops=dict(arrowstyle='-|>', lw=2.0, color='#c0392b', ls='--', shrinkA=0, shrinkB=0))

# inline direction cues beside each rail (so the reading order is explicit, not legend-only)
ax.text(x_c-0.35, 5.35, 'causation', fontsize=8.0, ha='right', va='center', color='#1e8449', fontweight='bold',
        rotation=90)
ax.text(x_d+0.35, 5.35, 'diagnosis', fontsize=8.0, ha='left', va='center', color='#c0392b', fontweight='bold',
        rotation=90)

# legend
ax.text(5.0, 1.05, 'causation \u2193 (workload \u2192 serving)   |   diagnosis \u2191 (serving \u2192 workload)',
        ha='center', va='center', fontsize=8.2, color='#444')

out = 'design/manuscript/chapter-06/figures/fig-06-0601.png'
plt.savefig(out, dpi=170)
plt.close()
print('wrote fig-06-0601 (diagnostic chain, matplotlib)')
