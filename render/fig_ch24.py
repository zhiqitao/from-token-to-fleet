import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-24-2401: Red Team / Green Team cycle ----
# Stages laid out as a 2x3 grid (each box is wide relative to its label so the
# labels never clip), probe domains below, a single explicit feedback loop, and
# a metrics->backlog drop.  Generous spacing on every side.
STAGES = [
    ('1 Red Team',   '#a83232', '//'),
    ('2 Probes',     '#c0392b', 'xx'),
    ('3 Exposure',   '#e67e22', 'oo'),
    ('4 Guardrails', '#d68910', '..'),
    ('5 Metrics',    '#16a085', '\\\\\\\\'),
    ('6 Green Team', '#2980b9', '||'),
]
# 2 rows x 3 cols
cols_x = [0.8, 9.6, 18.4]
rows_y = [9.0, 6.2]
W = 7.8; H = 1.5

fig, ax = plt.subplots(figsize=(6.1, 5.77))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.set_xlim(0, 27); ax.set_ylim(0, 12.6); ax.axis('off')

ax.text(13.5, 11.9, 'Red Team / Green Team cycle: probe, measure, harden, loop',
        fontsize=11, fontweight='bold', ha='center', color='#1a1a1a')
ax.text(13.5, 11.2, '(1\u21926 forward cycle; one red feedback loop back to step 1)',
        fontsize=8, ha='center', color='#555')

for i, (label, col, hatch) in enumerate(STAGES):
    r = i // 3; c = i % 3
    x = cols_x[c]; y = rows_y[r]
    ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle='round,pad=0.02',
                                fc=col, ec='#333', lw=0.8, hatch=hatch))
    ax.text(x+W/2, y+H/2, label, ha='center', va='center',
            color='white', fontsize=10, fontweight='bold')
# row 1 forward arrows: 1->2->3 ; row 0 arrows: 4->5->6
for c in [0, 1]:
    # row 0 (y=rows_y[0]) stages 1,2,3
    x=cols_x[c]
    ax.annotate('', xy=(x+W+0.95, rows_y[1]+H/2), xytext=(x+W+0.15, rows_y[1]+H/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#555'))
    # row 1 (y=rows_y[0]) stages 4,5,6
    ax.annotate('', xy=(x+W+0.95, rows_y[0]+H/2), xytext=(x+W+0.15, rows_y[0]+H/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#555'))

# ---- Probe domains: moved to the caption/prose to reduce clutter (the reviewer's ask) ----
# (the probe examples — jailbreak/persona, escalation/fuzz, poisoning/injection — now live
#  in the Fig 24.1 caption, not as three extra dense boxes)

# ---- Single strong feedback loop below the stages (Green -> next Red cycle) ----
ax.annotate('', xy=(2.0, 1.9), xytext=(25.0, 1.9),
            arrowprops=dict(arrowstyle='-|>', lw=3.0, color='#a83232',
                            connectionstyle='arc3,rad=-0.10'))
ax.text(13.5, 0.9, 'loop: findings from Green Team → next Red Team cycle (strong feedback leg)',
        fontsize=9, ha='center', color='#a83232', fontweight='bold')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-24/figures/fig-24-2401.png',
            dpi=200, bbox_inches='tight', pad_inches=0.08)
plt.close()
print('fig-24-2401 rewritten (2x3 grid)')
