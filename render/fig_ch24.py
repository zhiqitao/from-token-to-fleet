import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-24-2401: Red Team / Green Team cycle ----
# Stages laid out as a 2x3 grid (each box is wide relative to its label so the
# labels never clip), probe domains below, a single explicit feedback loop, and
# a metrics->backlog drop.  Generous spacing on every side.
STAGES = [
    ('1 Red Team',   '#a83232'),
    ('2 Probes',     '#c0392b'),
    ('3 Exposure',   '#e67e22'),
    ('4 Guardrails', '#d68910'),
    ('5 Metrics',    '#16a085'),
    ('6 Green Team', '#2980b9'),
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

for i, (label, col) in enumerate(STAGES):
    r = i // 3; c = i % 3
    x = cols_x[c]; y = rows_y[r]
    ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle='round,pad=0.02',
                                fc=col, ec='#333', lw=0.8))
    ax.text(x+W/2, y+H/2, label, ha='center', va='center',
            color='white', fontsize=10, fontweight='bold')
# row 0 forward arrows: 1->2->3 ; row 1 arrows: 4->5->6
for c in [0, 1]:
    # row 0 (y=rows_y[1]) stages 1,2,3
    x=cols_x[c]
    ax.annotate('', xy=(x+W+0.95, rows_y[1]+H/2), xytext=(x+W+0.15, rows_y[1]+H/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#555'))
    # row 1 (y=rows_y[0]) stages 4,5,6
    ax.annotate('', xy=(x+W+0.95, rows_y[0]+H/2), xytext=(x+W+0.15, rows_y[0]+H/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#555'))
# 3 -> 4 down-connector (Exposure, top-right, to Guardrails, bottom-left). Straight
# L-shaped connector (cleaner than a curve) landing on box 4's TOP edge.
ax.annotate('', xy=(cols_x[0]+W/2, rows_y[1]+H), xytext=(cols_x[2]+W/2, rows_y[0]),
            arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#555',
                            connectionstyle='angle,angleA=0,angleB=90,rad=6'))

# ---- Probe domains: moved to the caption/prose to reduce clutter (the reviewer's ask) ----
# (the probe examples — jailbreak/persona, escalation/fuzz, poisoning/injection — now live
#  in the Fig 24.1 caption, not as three extra dense boxes)

# ---- Single strong feedback loop below the stages (Green -> next Red cycle) ----
# L-shaped return on the FAR LEFT (clear of box 4, which sits directly below box 1 at
# the same x): hook out from box 6 (Green Team, bottom row) bottom-center, run left
# along the bottom, up the left margin, then right into box 1 (Red Team, top row)
# LEFT-EDGE middle. Both ends attach to a box edge; the stem does not cross a box.
from matplotlib.path import Path
FBY = 1.9
LX  = 0.25                     # far-left rail, just inside canvas, left of box 4's left edge (x=0.8)
ret_verts = [(cols_x[2]+W/2, rows_y[1]), (cols_x[2]+W/2, FBY+0.35),
             (cols_x[2]+W/2, FBY), (LX, FBY),
             (LX, rows_y[0]+H/2), (cols_x[0], rows_y[0]+H/2)]
ret_codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO]
ax.add_patch(FancyArrowPatch(path=Path(ret_verts, ret_codes), arrowstyle='-|>',
             mutation_scale=18, lw=3.0, color='#a83232', zorder=1))
ax.text(13.5, 0.9, 'loop: findings from Green Team → next Red Team cycle (strong feedback leg)',
        fontsize=9, ha='center', color='#a83232', fontweight='bold')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-24/figures/fig-24-2401.png', dpi=200)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-24/figures/fig-24-2401.pdf', format='pdf')
plt.close()
print('fig-24-2401 rewritten (solid-colour 2x3 grid)')
