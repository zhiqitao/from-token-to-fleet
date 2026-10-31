import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# ---- fig-19-1902: token + KV growth across agent turns (Ch19 Table 19-1) ----
# Two aligned panels. Authored NARROW (6.4in) + tight bbox so it never overflows
# the ~6.1in print column or clips the title/labels.
I0, d, g, Of = 9200, 800, 65, 300
kv_mb = 2.62   # canonical decimal MB/token (max-KV convention incl. output)
Ts = np.arange(0, 5)
inp = I0 + Ts*d + Ts*g
out = Of
kv_gb = (inp + out) * kv_mb / 1000

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.1, 5.4), sharex=True)
fig._hermes_print_sized = True   # regen must not re-boost/reflow

w = 0.4
x = Ts

# Panel 1: token accumulation — split initial context vs turn-by-turn additions
# so the two are distinguishable in grayscale (distinct grays + distinct hatches).
# R27 P2: the old combined 'added per turn' bar (orange //) and the O bar (green
# xx) used patterns that CONFLICTED with Fig 19.3 (delta=teal dots, gamma=orange
# cross, O=green solid). We now split 'added' into delta + gamma and match 19.3's
# fill+hatch for every shared quantity, and the legend uses explicit Patch handles
# so each entry shows its swatch (the old auto-handles left I0 and 'added' blank).
base  = np.full(5, I0)        # initial prompt context (constant)
delta = Ts*d                  # retrieved per turn
gamma = Ts*g                  # generated per turn
ax1.bar(x - w/2, base,  w, color='#c8d8ea', hatch='//',  edgecolor='#27408b', linewidth=0.6, label='initial context (I\u2080)')
ax1.bar(x - w/2, delta, w, bottom=base,        color='#7fc6b5', hatch='...', edgecolor='#1a7a63', linewidth=0.6, label='retrieved (\u03b4=800)')
ax1.bar(x - w/2, gamma, w, bottom=base+delta,  color='#f5c98b', hatch='xx',  edgecolor='#e67e22', linewidth=0.6, label='generated (\u03b3=65)')
ax1.bar(x - w/2, [Of]*5, w, bottom=inp,        color='#6f9e5f',             edgecolor='#1e7a59', linewidth=0.6, label='output (O=300)')
ax1.set_ylabel('Tokens / request', fontsize=9)
ax1.set_title('(a) Tokens accumulate', fontsize=9.5)
ax1.grid(alpha=0.3, axis='y')
_legend_a = [
    ('initial context (I\u2080)', '#c8d8ea', '//'),
    ('retrieved (\u03b4=800)',     '#7fc6b5', '...'),
    ('generated (\u03b3=65)',      '#f5c98b', 'xx'),
    ('output (O=300)',             '#6f9e5f', ''),
]
ax1.legend(handles=[Patch(fc=c, ec='#333', hatch=h, label=l) for l, c, h in _legend_a],
           fontsize=8.6, loc='upper center', bbox_to_anchor=(0.5, -0.35), ncol=2, frameon=False)
ax1.tick_params(labelsize=8.6)
# headroom so the tallest bar (turn 4 ~12.7K) is not clipped at the top spine
ax1.set_ylim(0, 14000)

# Panel 2: resulting KV
ax2.bar(x, kv_gb, 0.5, color='#c0392b', hatch='..', edgecolor='white', linewidth=0.6, label='KV / request (FP16)')
# value labels rotated 90° (vertical) so adjacent numbers can't collide horizontally
# (each label is ~0.39in wide but bars are only ~0.27in apart)
for i, v in enumerate(kv_gb):
    ax2.annotate(f'{v:.1f}', xy=(x[i], v), xytext=(x[i], v+0.4), ha='center', va='bottom',
                 rotation=90, fontsize=8.6, color='#c0392b', fontweight='bold')
# The first bar and its value already identify the single-shot baseline.
# An additional unlabeled 24.9-GB rule duplicates that value without a key.
ax2.set_ylabel('KV / request (GB, FP16)', fontsize=9)
# title shortened so "GB" is not clipped at the right edge of the panel
ax2.set_title('(b) KV 24.9 \u2192 34.0 GB', fontsize=9)
ax2.grid(alpha=0.3, axis='y')
ax2.legend(handles=[Patch(fc='#c0392b', ec='#333', hatch='..', label='KV / request (FP16)')],
           fontsize=8.6, loc='upper center', bbox_to_anchor=(0.5, -0.35), ncol=1, frameon=False)
ax2.tick_params(labelsize=8.6)
# headroom so the tallest rotated value label (34.0 + its vertical extent) is not clipped at the top spine
ax2.set_ylim(0, 48)

for ax in (ax1, ax2):
    ax.set_xticks(x)
    ax.set_xticklabels(['0\n(single-shot)', '1', '2', '3', '4'], fontsize=8.6)
    # x-axis title directly under each panel's ticks (was a single floating fig.text
    # that landed far below the legends, detached from the axes)
    ax.set_xlabel('Agent turns', fontsize=8.6)

fig.suptitle('Token growth vs resulting KV growth across agent turns', fontsize=10.5, fontweight='bold')
# explicit in-plot statement that this is an append-only illustrative model
fig.text(0.5, 0.86, 'append-only illustrative model: context only ever accumulates across turns — nothing is evicted',
         ha='center', va='top', fontsize=8.6, style='italic', color='#444')
# counterfactual column semantics (R08): each column is a SEPARATE completion
# after T turns (incl. one final 300-token answer), not successive states of one
# live agent.  Placed in the empty band between the x-labels and the legend.
fig.text(0.5, 0.135,
         'counterfactual: each column = a separate completion after T turns,\n'
         'including one final 300-token answer — not successive states of one live agent.',
         ha='center', va='center', fontsize=8.4, color='#222')
plt.subplots_adjust(left=0.12, right=0.97, top=0.78, bottom=0.28, wspace=0.40)
plt.savefig('design/manuscript/chapter-19/figures/fig-19-1902.png',
            dpi=400, bbox_inches='tight', pad_inches=0.05)
plt.close()
print('wrote fig-19-1902 (narrow, tight-bbox, append-only label + grayscale hatch split)')
