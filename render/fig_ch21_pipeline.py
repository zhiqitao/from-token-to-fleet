import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-21-2101: AI Factory promotion pipeline with canary gate + rollback ----
# Correct semantics: the forward chain is Data->Train->Evaluate->Canary->Observe->
# Promote->Serve (NO 'Rollback' stage in the forward path).  Rollback is a
# CONDITIONAL branch: on an observe/canary SLO breach, revert to the last-known-good
# model and re-validate; the green arrow is the normal production feedback loop.
fig, ax = plt.subplots(figsize=(9.2, 5.4))
ax.set_xlim(0, 24); ax.set_ylim(0, 9); ax.axis('off')

ax.set_title('The AI Factory promotion pipeline (canary gate, rollback branch)',
             fontsize=12, fontweight='bold', ha='center', color='#1a1a1a')

stages = ['Data', 'Train', 'Evaluate', 'Canary', 'Observe', 'Promote', 'Serve']
xs = [0.8, 3.8, 6.8, 9.8, 12.8, 15.8, 19.0]
w = 2.4; h = 1.3; y = 6.2
for name, x in zip(stages, xs):
    fc = '#6f9e5f' if name == 'Serve' else '#3a6ea5'
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.04', fc=fc, ec='#1a3a6b', lw=1.2))
    ax.text(x+w/2, y+h/2, name, ha='center', va='center', fontsize=9, color='white', fontweight='bold')

# forward arrows
for x in xs[:-1]:
    ax.annotate('', xy=(x+w+0.9, y+h/2), xytext=(x+w+0.05, y+h/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#555'))
# canary gate label
ax.text(xs[2]+w+0.45, y+h+0.25, 'gate', fontsize=8, ha='center', color='#c0392b', fontweight='bold')

# Rollback CONDITIONAL branch: from Observe (SLO breach) back to a last-known-good.
# Draw a red dashed path from Observe up-and-back over the pipeline to 'Promote'
# (the last-known-good), labelled 'rollback on SLO breach'.
ax.add_patch(FancyArrowPatch((xs[4]+w/2, y+h), (xs[5]+w/2, y+h+3.2),
             connectionstyle='arc3,rad=-0.25', arrowstyle='-|>', lw=2.0,
             color='#c0392b', ls='--'))
ax.text(xs[4]+w/2+0.2, y+h+2.4, 'rollback: revert to\nlast-known-good on SLO breach\n(conditional branch, not a forward stage)',
        fontsize=7.8, ha='left', color='#c0392b')

# Green production feedback loop: Serve -> Data/evaluation.
ax.add_patch(FancyArrowPatch((xs[6]+w/2, y), (xs[0]+w/2+0.5, y-3.0),
             connectionstyle='arc3,rad=0.32', arrowstyle='-|>', lw=2.2, color='#2f6f4f'))
ax.text(12.0, 2.2, 'production feedback → data / evaluation',
        fontsize=8.5, ha='center', color='#2f6f4f', fontweight='bold')

ax.text(12.0, 0.8, 'metrics gate: promote only after canary/observe pass; otherwise rollback to last-known-good. [2° DERIVED]',
        fontsize=8, ha='center', color='#666')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-21/figures/fig-21-2101.png', dpi=150)
plt.close()
print('wrote fig-21-2101')
