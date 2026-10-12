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

fig, ax = plt.subplots(figsize=(6.1, 4.7))
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
    fc = '#6f9e5f' if name == 'Serve' else '#3a6ea5'
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.04', fc=fc, ec='#1a3a6b', lw=1.2))
    ax.text(x + w/2, y + h/2, name, ha='center', va='center', fontsize=9.2, color='white', fontweight='bold')

# forward arrows along stage row
for x in xs[:-1]:
    ax.annotate('', xy=(x + w + 0.5, y + h/2), xytext=(x + w + 0.05, y + h/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.7, color='#555'))

# ---- measurement gate row (orange), one beneath every non-terminal stage ----
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
for (stage, crit), x in zip(gates, xs):
    ax.plot([x + w/2, x + w/2], [y, gy + gh], color='#c0392b', lw=1.0, ls=':', zorder=1)
    ax.add_patch(FancyBboxPatch((x, gy), gw, gh, boxstyle='round,pad=0.04',
                                fc='#fbe6e0', ec='#c0392b', lw=1.7, zorder=2))
    ax.text(x + gw/2, gy + gh - 0.58, stage, ha='center', va='center',
            fontsize=9.2, color='#8c2d1a', fontweight='bold', zorder=3)
    ax.text(x + gw/2, gy + gh - 1.30, crit, ha='center', va='center',
            fontsize=9.2, color='#3a2a24', zorder=3)
    ax.text(x + gw/2, gy + 0.42, '\u2713 PASS', ha='center', va='center',
            fontsize=8.8, color='#c0392b', fontweight='bold', zorder=3)

# ---- FAIL path: any gate that does not pass -> rollback / last-known-good ----
# The FAIL box must span from below the leftmost gate (Data, centre x=2.0) to below
# the rightmost (Promote, centre x=18.5) so every gate's dashed drop lands on it.
ax.add_patch(FancyBboxPatch((1.0, 3.35), 18.0, 1.15, boxstyle='round,pad=0.04',
                            fc='#c0392b', ec='#6d1a0e', lw=1.4))
ax.text(10.0, 4.14, 'FAIL', ha='center', va='center', fontsize=8.4, color='white', fontweight='bold')
ax.text(10.0, 3.68, 'rollback to last-known-good & re-validate', ha='center', va='center',
        fontsize=8.0, color='white')
# dashed links from the 6 GATED stages (xs[:6]; Serve is terminal, no gate) down to
# the FAIL node — any gate breach rolls back
for x in xs[:6]:
    ax.add_patch(FancyArrowPatch((x + w/2, gy), (x + w/2, 4.5),
                 arrowstyle='-|>', lw=1.2, color='#c0392b', ls='--', zorder=1))

# ---- green production feedback loop: Serve -> data / evaluation (bottom, clear of gates) ----
# Route the return leg to the LEFT of the Data gate box (x=0.3 < gate left edge 0.6)
# so the vertical segment no longer passes through the gate; enter the Data stage
# box at its left edge.
loopverts = [
    (xs[6] + w/2, y),                       # start: Serve bottom
    (xs[6] + w/2, 1.5), (0.3, 1.5),
    (0.3, y + h/2), (xs[0], y + h/2),       # end: Data stage left edge
]
loopcodes = [Path.MOVETO] + [Path.LINETO]*4
ax.add_patch(FancyArrowPatch(path=Path(loopverts, loopcodes), arrowstyle='-|>',
                             lw=2.2, color='#2f6f4f', zorder=1))
ax.text(12.0, 0.85, 'production feedback \u2192 data / evaluation (each cycle re-gated)',
        fontsize=8.2, ha='center', color='#2f6f4f', fontweight='bold')

ax.text(12.0, 0.25, '[ILLUSTRATIVE][DERIVED] Gates pass on measured throughput / SLO / cost; a breach rolls back.',
        fontsize=8.0, ha='center', color='#777')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-21/figures/fig-21-2101.png', dpi=150)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-21/figures/fig-21-2101.pdf')
plt.close()
print('wrote fig-21-2101')
