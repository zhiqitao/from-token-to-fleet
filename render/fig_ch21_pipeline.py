import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path

# ---- fig-21-2101: AI Factory promotion pipeline, MEASUREMENT GATE emphasis ----
# The forward chain is Data->Train->Eval->Canary->Observe->Promote->Serve.
# The point of this figure is NOT to show another CI/CD box-and-arrow chain:
# every stage is fronted by a MEASUREMENT GATE -- a pass/fail decision on a
# measured metric (throughput, SLO, cost, quality).  A gate that FAILs pulls
# the candidate back to rollback / last-known-good (red dashed branch).  The
# green arrow is the normal production feedback loop back to data + evaluation.
# 2026-09 review: the gate boxes carried three small text lines and read as
# visual texture.  Each gate is now a SHORT one-line criterion at a larger
# size (details live in the caption/body), and PASS is a compact badge.

fig, ax = plt.subplots(figsize=(6.1, 4.1))
fig._hermes_print_sized = True   # authored at 6.1in; regen must not re-boost/reflow
ax.set_xlim(0, 24); ax.set_ylim(0, 13.4); ax.axis('off')

ax.set_title('AI Factory promotion: a measured gate on each transition',
             fontsize=11.5, fontweight='bold', ha='center', color='#1a1a1a')
ax.text(12, 12.5, 'every promotion is a PASS/FAIL decision on a measured metric, not a hand-off',
        fontsize=8.2, ha='center', color='#555', style='italic')

# ---- stage row (blue) ----
stages  = ['Data', 'Train', 'Eval', 'Canary', 'Observe', 'Promote', 'Serve']
xs      = [0.6, 3.9, 7.2, 10.5, 13.8, 17.1, 20.4]
w, h, y = 2.8, 1.25, 9.6
for name, x in zip(stages, xs):
    if name == 'Serve':
        # R27 P2: the green Serve box collapsed to the same mid-gray as the blue
        # stage boxes in grayscale; a diagonal hatch makes it distinguishable.
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.04',
                                    fc='#6f9e5f', ec='#1a3a6b', lw=1.2, hatch='///'))
    else:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.04', fc='#3a6ea5', ec='#1a3a6b', lw=1.2))
    ax.text(x + w/2, y + h/2, name, ha='center', va='center', fontsize=9.2, color='white', fontweight='bold')

# forward arrows along stage row
for x in xs[:-1]:
    ax.annotate('', xy=(x + w + 0.5, y + h/2), xytext=(x + w + 0.05, y + h/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.7, color='#555'))

# ---- measurement gates align with the six actual transition seams ----
# One-line short criterion per gate, larger type; PASS badge below.
gates = [
    ('Data',    'src valid'),
    ('Train',   'cost ok'),
    ('Eval',    'qual ok'),
    ('Canary',  'health ok'),
    ('Observe', 'TTFT ok'),
    ('Promote', 'cost ok'),
]
gy, gw, gh = 5.55, 2.85, 2.2
seams = [(left + w + right) / 2 for left, right in zip(xs[:-1], xs[1:])]
for (stage, crit), seam in zip(gates, seams):
    x = seam - gw / 2
    ax.plot([seam, seam], [y + h/2 - 0.22, y + h/2 + 0.22],
            color='#c0392b', lw=2.0, zorder=4)
    ax.plot([seam, seam], [y + h/2 - 0.22, gy + gh],
            color='#c0392b', lw=1.0, ls=':', zorder=1)
    ax.add_patch(FancyBboxPatch((x, gy), gw, gh, boxstyle='round,pad=0.04',
                                fc='#fbe6e0', ec='#c0392b', lw=1.7, zorder=2))
    ax.text(x + gw/2, gy + gh - 0.58, stage, ha='center', va='center',
            fontsize=9.2, color='#8c2d1a', fontweight='bold', zorder=3)
    ax.text(x + gw/2, gy + gh - 1.30, crit, ha='center', va='center',
            fontsize=9.2, color='#3a2a24', zorder=3)
    ax.text(x + gw/2, gy + 0.42, '\u2713 PASS', ha='center', va='center',
            fontsize=8.8, color='#c0392b', fontweight='bold', zorder=3)

# ---- FAIL path: any gate that does not pass -> rollback / last-known-good ----
# Every gate's dashed failure drop lands on this common rollback node.
ax.add_patch(FancyBboxPatch((2.0, 3.35), 19.5, 1.15, boxstyle='round,pad=0.04',
                            fc='#c0392b', ec='#6d1a0e', lw=1.4))
ax.text(11.75, 4.14, 'FAIL', ha='center', va='center', fontsize=8.4, color='white', fontweight='bold')
ax.text(11.75, 3.68, 'rollback to last-known-good & re-validate', ha='center', va='center',
        fontsize=8.0, color='white')
# dashed links from the 6 GATED stages (xs[:6]; Serve is terminal, no gate) down to
# the FAIL node — any gate breach rolls back
for seam in seams:
    ax.add_patch(FancyArrowPatch((seam, gy), (seam, 4.5),
                 arrowstyle='-|>', lw=1.2, color='#c0392b', ls='--', zorder=1))
    ax.text(seam + 0.13, (gy + 4.5)/2, 'FAIL', ha='left', va='center',
            fontsize=8.0, color='#a32b20', fontweight='bold', zorder=3)

# ---- green production feedback loop: Serve -> data / evaluation (bottom, clear of gates) ----
# R27 P2: the old loop ended with a single arrowhead on the Data box, but the
# caption says "returns evidence to data/evaluation" — Eval was never pointed to.
# The loop now runs up the left side, across the top (above the stage boxes), and
# drops into Eval, with a short branch arrow into Data, so BOTH are targeted.
TOP_Y = 11.6   # above the stage boxes (top y+h=10.85), below the subtitle (12.5)
loopverts = [
    (xs[6] + w/2, y),                       # start: Serve bottom
    (xs[6] + w/2, 1.5), (0.3, 1.5),
    (0.3, TOP_Y), (xs[2] + w/2, TOP_Y), (xs[2] + w/2, y + h),  # up, across, down to Eval top
]
loopcodes = [Path.MOVETO] + [Path.LINETO]*5
ax.add_patch(FancyArrowPatch(path=Path(loopverts, loopcodes), arrowstyle='-|>',
                             lw=2.2, color='#2f6f4f', zorder=1))
# short branch arrow into the Data stage box (left edge)
ax.annotate('', xy=(xs[0], y + h/2), xytext=(0.3, y + h/2),
            arrowprops=dict(arrowstyle='-|>', lw=2.2, color='#2f6f4f',
                            shrinkA=0, shrinkB=0))
ax.text(12.0, 0.85, 'production feedback \u2192 data / evaluation (each cycle re-gated)',
        fontsize=8.2, ha='center', color='#2f6f4f', fontweight='bold')

ax.text(12.0, 0.25, 'Gates check measured throughput / SLO / cost; a breach rolls back.',
        fontsize=8.0, ha='center', color='#777')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-21/figures/fig-21-2101.png', dpi=350)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-21/figures/fig-21-2101.pdf')
plt.close()
print('wrote fig-21-2101')
