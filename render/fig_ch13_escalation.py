#!/usr/bin/env python3
"""fig-13-1301: the reference-architecture escalation path (horizontal, non-hierarchical).

PASS-24 fix: the Archify 'ladder' version stacked Single GPU at the TOP and Cluster/
fleet at the BOTTOM, so a ladder metaphor implied the top tier was 'best'. It also drew
the escalation-trigger pills directly on the rung borders (straddling the connectors)
and truncated one trigger ('forces local'). This is a HORIZONTAL escalation path: tiers
advance left-to-right as requirements grow, so there is no best/worst vertical reading,
and each trigger label sits in clear whitespace BELOW the connector (not on it).

PASS-2 add: make 'STOP when constraints are satisfied' first-class. Escalation is only
for a BINDING constraint; if the current tier satisfies the workload, stay put. Each
tier card carries a green STOP branch (down arrow + 'constraints satisfied? STOP here')
so the reader sees the exit at every tier, and the footer states the rule explicitly.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

W = 6.1
FS = 8.2
fig, ax = plt.subplots(figsize=(W, W*0.88))
fig._hermes_print_sized = True
ax.set_xlim(0, 10); ax.set_ylim(0, 8.2); ax.axis('off')

tiers = [
    ('Single GPU', 'one accelerator\nlocal memory', '#e7f5ec', '#1e8449'),
    ('Single host', 'GPU rack node\nNVLink fabric', '#e7f5ec', '#1e8449'),
    ('Multi-host', 'several nodes\ncluster fabric', '#e7f5ec', '#1e8449'),
    ('Cluster / fleet', 'many nodes\nnetwork spine', '#e7f5ec', '#1e8449'),
]
triggers = [
    ('outgrows 1 GPU', 'forces local', '#c0392b', '#1e8449'),
    ('KV overflows floor', 'privacy', '#c0392b', '#1e8449'),
    ('fleet demand', 'cost pressure', '#c0392b', '#1e8449'),
]
bw, bh = 1.9, 1.5
y0 = 4.6
xs = [0.45 + i*2.42 for i in range(4)]
for (name, sub, fc, ec), x in zip(tiers, xs):
    ax.add_patch(FancyBboxPatch((x, y0), bw, bh, boxstyle='round,pad=0.02,rounding_size=0.3',
                                fc=fc, ec=ec, lw=1.5))
    ax.text(x+bw/2, y0+bh-0.5, name, ha='center', va='center', fontsize=FS, fontweight='bold', color='#1a3a2a')
    ax.text(x+bw/2, y0+0.5, sub, ha='center', va='center', fontsize=7.8, color='#33523a')

# escalation connectors (left->right) with trigger labels in clear whitespace BELOW
for i in range(len(xs)-1):
    ax.annotate('', xy=(xs[i+1], y0+bh/2), xytext=(xs[i]+bw, y0+bh/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#555'))
    trig_l, trig_r, cl, cr = triggers[i]
    midx = (xs[i]+bw + xs[i+1])/2
    ax.text(midx-0.05, y0-0.55, trig_l, ha='center', va='top', fontsize=7.6, color=cl, fontweight='bold')
    ax.text(midx-0.05, y0-1.05, trig_r, ha='center', va='top', fontsize=7.6, color=cr, fontweight='bold')

# STOP branch below each tier: 'constraints satisfied? STOP here' (the escape at every tier)
STOP_Y = y0 - 2.7
for x in xs:
    cx = x + bw/2
    ax.annotate('', xy=(cx, y0-0.02), xytext=(cx, y0-2.1),
                arrowprops=dict(arrowstyle='-|>', lw=2.0, color='#1e8449'))
    ax.add_patch(FancyBboxPatch((cx-0.82, STOP_Y-0.62), 1.64, 0.62,
                 boxstyle='round,pad=0.02,rounding_size=0.12', fc='#f2f9f4', ec='#1e8449', lw=1.3))
    ax.text(cx, STOP_Y-0.30, 'constraints\nsatisfied? STOP', ha='center', va='center',
            fontsize=8.0, color='#1e8449', fontweight='bold')

ax.text(5.0, 7.75, 'The reference-architecture escalation path', fontsize=10.5,
        fontweight='bold', ha='center', va='center', color='#1a1a1a')
ax.text(5.0, 0.5, 'escalate only when a constraint binds — else STOP; tiers are orthogonal levels of scale, not a ranking',
        ha='center', va='center', fontsize=7.6, color='#666')

out = 'design/manuscript/chapter-13/figures/fig-13-1301.png'
plt.savefig(out, dpi=170)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig(out[:-4]+'.pdf', format='pdf')
plt.close()
print('wrote fig-13-1301 (horizontal escalation path + STOP-when-satisfied)')
