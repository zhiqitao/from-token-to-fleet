#!/usr/bin/env python3
"""fig-13-1301: the reference-architecture escalation path (horizontal, non-hierarchical).

PASS-24 fix: the Archify 'ladder' version stacked Single GPU at the TOP and Cluster/
fleet at the BOTTOM, so a ladder metaphor implied the top tier was 'best'. It also drew
the escalation-trigger pills directly on the rung borders (straddling the connectors)
and truncated one trigger ('forces local'). This is a HORIZONTAL escalation path: tiers
advance left-to-right as requirements grow, so there is no best/worst vertical reading,
and each trigger label sits in clear whitespace BELOW the connector (not on it). The
trigger is the reason to escalate, so it is drawn as the arrow's label.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

W = 6.1
FS = 8.2
fig, ax = plt.subplots(figsize=(W, W*0.62))
fig._hermes_print_sized = True
ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis('off')

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
y0 = 3.3
xs = [0.45 + i*2.42 for i in range(4)]
for (name, sub, fc, ec), x in zip(tiers, xs):
    ax.add_patch(FancyBboxPatch((x, y0), bw, bh, boxstyle='round,pad=0.02,rounding_size=0.3',
                                fc=fc, ec=ec, lw=1.5))
    ax.text(x+bw/2, y0+bh-0.5, name, ha='center', va='center', fontsize=FS, fontweight='bold', color='#1a3a2a')
    ax.text(x+bw/2, y0+0.5, sub, ha='center', va='center', fontsize=7.2, color='#33523a')

# escalation connectors (left->right) with trigger labels in clear whitespace BELOW
for i in range(len(xs)-1):
    ax.annotate('', xy=(xs[i+1], y0+bh/2), xytext=(xs[i]+bw, y0+bh/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#555'))
    trig_l, trig_r, cl, cr = triggers[i]
    midx = (xs[i]+bw + xs[i+1])/2
    # red trigger (reason) below-left, green flip (becomes) below-right
    ax.text(midx-0.05, y0-0.45, trig_l, ha='center', va='top', fontsize=7.6, color=cl, fontweight='bold')
    ax.text(midx-0.05, y0-0.95, trig_r, ha='center', va='top', fontsize=7.6, color=cr, fontweight='bold')

ax.text(5.0, 5.75, 'The reference-architecture escalation path', ha='center', va='center',
        fontsize=10.5, fontweight='bold', color='#1a1a1a')
ax.text(5.0, 0.35, 'escalate when the workload outgrows the current tier; the tiers are orthogonal levels of scale, not a quality ranking',
        ha='center', va='center', fontsize=7.4, color='#666')

out = 'design/manuscript/chapter-13/figures/fig-13-1301.png'
plt.savefig(out, dpi=170)
plt.close()
print('wrote fig-13-1301 (horizontal escalation path)')
