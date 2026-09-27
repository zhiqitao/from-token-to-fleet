#!/usr/bin/env python3
"""fig-13-1301: reference-architecture escalation ladder — VERTICAL, causal-arrow-dominant.

DESIGN (designer pass): the escalation TRIGGERS dominate the tier cards. A bold
vertical up-arrow (the causal "escalator") is the visual spine; between every two
tiers a LARGE trigger label states what FORCES the climb (KV residency overruns /
host goodput < demand / demand exceeds ceiling). Tier cards are deliberately small
ladder-rungs on the left. A thin dashed GREEN down-arrow on the right is the
de-escalation path (privacy, sovereignty, cost). A small green STOP label hangs off
every rung ("constraints met? STOP here") so the exit is visible at each level and
the reader never reads the ladder as a best/worst ranking.

CHANNEL-REDUNDANCY: escalation vs de-escalation differ by colour AND arrow style
(filled solid up-arrow vs open dashed down-arrow) AND label, never colour alone.
Tier cards are a single neutral green (all are "tiers", not categories), so there
is no colour-categorical reading.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon

W = 6.1
fig, ax = plt.subplots(figsize=(W, 7.0))
fig._hermes_print_sized = True   # print-size authored; regen must not re-boost/reflow
ax.set_xlim(0, 10); ax.set_ylim(0, 12.4); ax.axis('off')

# ---------------------------------------------------------------------------
# Tier ladder (LEFT column) — deliberately small neutral-green rungs.
# bottom -> top is the direction the workload escalates.
# ---------------------------------------------------------------------------
tiers = [
    ('Single GPU', 'one accel.\nlocal mem.'),
    ('Single host', 'GPU node\nNVLink fabric'),
    ('Multi-host', 'several nodes\ncluster fabric'),
    ('Cluster / fleet', 'many nodes\nnetwork spine'),
]
tier_y = [2.0, 4.7, 7.4, 10.1]
bw, bh = 1.8, 0.9
tx = 0.5
for (name, sub), y in zip(tiers, tier_y):
    ax.add_patch(FancyBboxPatch((tx, y - bh/2), bw, bh,
                                boxstyle='round,pad=0.02,rounding_size=0.15',
                                fc='#eef7f0', ec='#1e8449', lw=1.2))
    ax.text(tx + bw/2, y + 0.16, name, ha='center', va='center',
            fontsize=8.2, fontweight='bold', color='#1a3a2a')
    ax.text(tx + bw/2, y - 0.22, sub, ha='center', va='center',
            fontsize=6.0, color='#33523a')
    # small STOP branch hanging off each rung (the escape at every level)
    ax.text(tx + bw/2, y - bh/2 - 0.36, '\u25bc constraints \u2192 STOP',
            ha='center', va='center', fontsize=5.6, color='#1e8449')

# ---------------------------------------------------------------------------
# Dominant CAUSAL up-arrow (the escalator spine) — fat red shaft + triangle head.
# ---------------------------------------------------------------------------
shaft_x0, shaft_x1 = 5.9, 6.7
ax.add_patch(Rectangle((shaft_x0, 0.9), shaft_x1 - shaft_x0, 9.6,
                       fc='#c0392b', ec='none', zorder=1))
ax.add_patch(Polygon([(shaft_x0 - 0.6, 10.5), (shaft_x1 + 0.6, 10.5),
                      ((shaft_x0 + shaft_x1)/2, 11.5)],
                     fc='#c0392b', ec='none', zorder=1))
# thin rung-to-escalator connectors at each tier
for y in tier_y:
    ax.plot([tx + bw, shaft_x0], [y, y], color='#c0392b', lw=1.0, zorder=0)

# ---------------------------------------------------------------------------
# ESCALATION TRIGGERS — LARGE, dominant, red; "what forces the next".
# ---------------------------------------------------------------------------
triggers = [
    (3.35, 'KV residency overruns\n\u2192 forces scale-up'),
    (6.05, 'host goodput < demand\n\u2192 forces scale-up'),
    (8.75, 'demand exceeds ceiling\n\u2192 forces scale-up'),
]
for y, label in triggers:
    ax.text(2.6, y, label, ha='left', va='center',
            fontsize=11.0, fontweight='bold', color='#a01515', linespacing=1.35)

# ---------------------------------------------------------------------------
# DE-ESCALATION — thin dashed GREEN down-arrow (policy/governance), right side.
# ---------------------------------------------------------------------------
ax.annotate('', xy=(9.5, 0.95), xytext=(9.5, 10.1), arrowprops=dict(
    arrowstyle='-|>', lw=1.6, color='#1e8449', ls='--', shrinkA=0, shrinkB=0))
ax.text(7.9, 5.3, 'DE-ESCALATE:\nprivacy \u00b7 cost', ha='center', va='center',
        fontsize=6.8, color='#1e8449', fontweight='bold', linespacing=1.3)

# ---------------------------------------------------------------------------
# Headings
# ---------------------------------------------------------------------------
ax.text(5.0, 12.15, 'The reference-architecture escalation ladder',
        fontsize=12.0, fontweight='bold', ha='center', va='center', color='#1a1a1a')
ax.text(5.0, 0.35,
        'escalate only when a constraint binds \u2014 else STOP; tiers are orthogonal levels of scale, not a ranking',
        ha='center', va='center', fontsize=7.6, color='#666')

out = 'design/manuscript/chapter-13/figures/fig-13-1301.png'
plt.savefig(out, dpi=170)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig(out[:-4] + '.pdf', format='pdf')
plt.close()
print('wrote fig-13-1301 (vertical escalation ladder, triggers dominate)')
