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

fig, ax = plt.subplots(figsize=(6.1, 4.7))
ax.set_xlim(0, 24); ax.set_ylim(0, 13.4); ax.axis('off')

ax.set_title('AI Factory promotion: measured gates on every stage',
             fontsize=11.3, fontweight='bold', ha='center', color='#1a1a1a')
ax.text(12, 12.5, 'every promotion is a PASS/FAIL decision on a measured metric, not a hand-off',
        fontsize=8, ha='center', color='#555', style='italic')

# ---- stage row (blue) ----
stages  = ['Data', 'Train', 'Eval', 'Canary', 'Observe', 'Promote', 'Serve']
xs      = [0.6, 3.9, 7.2, 10.5, 13.8, 17.1, 20.4]
w, h, y = 2.8, 1.25, 9.6
for name, x in zip(stages, xs):
    fc = '#6f9e5f' if name == 'Serve' else '#3a6ea5'
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.04', fc=fc, ec='#1a3a6b', lw=1.2))
    ax.text(x + w/2, y + h/2, name, ha='center', va='center', fontsize=9, color='white', fontweight='bold')

# forward arrows along stage row
for x in xs[:-1]:
    ax.annotate('', xy=(x + w + 0.5, y + h/2), xytext=(x + w + 0.05, y + h/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.7, color='#555'))

# ---- measurement gate row (orange), one beneath every non-terminal stage ----
gates = [
    ('Data',    'source fresh\n& valid'),
    ('Train',   'cost <= budget\n@ tok/s'),
    ('Eval',    'quality >=\nSLO on suite'),
    ('Canary',  'throughput &\ngoodput >= SLO'),
    ('Observe', 'p95 TTFT &\nquality held'),
    ('Promote', 'cost & blast\nwithin plan'),
]
gy, gw, gh = 5.7, 2.85, 1.7
for (stage, measure), x in zip(gates, xs):
    ax.plot([x + w/2, x + w/2], [y, gy + gh], color='#c0392b', lw=1.0, ls=':', zorder=1)
    ax.add_patch(FancyBboxPatch((x, gy), gw, gh, boxstyle='round,pad=0.04',
                                fc='#fbe6e0', ec='#c0392b', lw=1.6, zorder=2))
    ax.text(x + gw/2, gy + gh - 0.36, stage + ' gate', ha='center', va='center',
            fontsize=8.2, color='#8c2d1a', fontweight='bold', zorder=3)
    ax.text(x + gw/2, gy + gh - 0.92, measure, ha='center', va='center',
            fontsize=6.4, color='#3a2a24', zorder=3)
    ax.text(x + gw/2, gy + 0.28, 'm\u2713 PASS', ha='center', va='center',
            fontsize=7.6, color='#c0392b', fontweight='bold', zorder=3)

# ---- FAIL path: any gate that does not pass -> rollback / last-known-good ----
ax.add_patch(FancyBboxPatch((6.4, 3.5), 11.2, 1.15, boxstyle='round,pad=0.04',
                            fc='#c0392b', ec='#6d1a0e', lw=1.4))
ax.text(12.0, 4.22, 'FAIL', ha='center', va='center', fontsize=7.8, color='white', fontweight='bold')
ax.text(12.0, 3.82, 'rollback to last-known-good & re-validate', ha='center', va='center',
        fontsize=7.2, color='white')
# dashed links from a representative gate down to the FAIL node
ax.add_patch(FancyArrowPatch((11.925, gy), (11.925, 4.65),
             arrowstyle='-|>', lw=1.6, color='#c0392b', ls='--'))
# dashed return from FAIL node back up to the Train gate
ax.add_patch(FancyArrowPatch((6.4, 4.1), (5.2, 5.7),
             connectionstyle='arc3,rad=0.22', arrowstyle='-|>', lw=1.6,
             color='#c0392b', ls='--'))

# ---- green production feedback loop: Serve -> data / evaluation (bottom, clear of gates) ----
loopverts = [
    (xs[6] + w/2, y),                       # start: Serve bottom
    (xs[6] + w/2, 2.55), (xs[6] + w/2, 1.5), (19.0, 1.5),
    (10.5, 1.5), (1.5, 1.5), (xs[0] + w/2, 2.6),
    (xs[0] + w/2, 5.2), (xs[0] + w/2, 7.4), (xs[0] + w/2, y),   # end: Data bottom
]
loopcodes = [Path.MOVETO] + [Path.CURVE4]*9
ax.add_patch(FancyArrowPatch(path=Path(loopverts, loopcodes), arrowstyle='-|>',
                             lw=2.2, color='#2f6f4f', zorder=1))
ax.text(12.0, 0.85, 'production feedback \u2192 data / evaluation (each cycle re-gated)',
        fontsize=8, ha='center', color='#2f6f4f', fontweight='bold')

ax.text(12.0, 0.25, '[ILLUSTRATIVE][DERIVED] Gates pass on measured throughput / SLO / cost; a breach rolls back.',
        fontsize=7.0, ha='center', color='#777')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-21/figures/fig-21-2101.png', dpi=150)
plt.close()
print('wrote fig-21-2101')
