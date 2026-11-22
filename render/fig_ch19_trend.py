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
ax1.bar(x - w/2, base,  w, color='#c8d8ea', hatch='//',  edgecolor='#27408b', linewidth=0.6, label='initial context (I₀ = 9,200)')
ax1.bar(x - w/2, delta, w, bottom=base,        color='#7fc6b5', hatch='...', edgecolor='#1a7a63', linewidth=0.6, label='retrieved (\u03b4=800)')
ax1.bar(x - w/2, gamma, w, bottom=base+delta,  color='#f5c98b', hatch='xx',  edgecolor='#e67e22', linewidth=0.6, label='generated (\u03b3=65)')
ax1.bar(x - w/2, [Of]*5, w, bottom=inp,        color='#6f9e5f', hatch='\\\\', edgecolor='#1e7a59', linewidth=0.6, label='output (O=300)')
# FIG-347-06: leader lines with VALUES call out the two thin bands (generated γ
# and output O) — at print scale their hatches are below resolution, so each is
# named with its value and pointed at its segment on the T = 4 bar; the note
# under the panels still states γ's resolution limit.
ax1.annotate('generated γ = 65/turn', xy=(3.8, 12530), xytext=(2.2, 13900),
             ha='right', fontsize=8.0, color='#a35a10',
             arrowprops=dict(arrowstyle='-', lw=0.8, color='#a35a10'))
ax1.annotate('output O = 300', xy=(3.8, 12810), xytext=(4.35, 13900),
             ha='right', fontsize=8.0, color='#3d6b33',
             arrowprops=dict(arrowstyle='-', lw=0.8, color='#3d6b33'))
ax1.set_ylabel('Tokens / request', fontsize=9)
ax1.set_title('(a) Tokens accumulate', fontsize=9.5)
ax1.grid(alpha=0.3, axis='y')
_legend_a = [
    ('initial context (I₀ = 9,200)', '#c8d8ea', '//'),
    ('retrieved (\u03b4=800)',     '#7fc6b5', '...'),
    ('generated (\u03b3=65)',      '#f5c98b', 'xx'),
    ('output (O=300)',             '#6f9e5f', '\\\\'),
]
# FIG-19.2-02: legend pulled up into a band directly beneath the panel, ABOVE
# the four-line note (was -0.35, which dropped it below the note block). The
# probe checks >= 6 pt clearance from the note and >= 8 pt legend type (8.6).
ax1.legend(handles=[Patch(fc=c, ec='#333', hatch=h, label=l) for l, c, h in _legend_a],
           fontsize=8.6, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=1, frameon=False)
ax1.tick_params(labelsize=8.6)
# FIG-19.2-06: thousands separators on panel (a) ticks to match '9,200' in the legend
from matplotlib.ticker import FuncFormatter as _FF
ax1.yaxis.set_major_formatter(_FF(lambda v, _pos: f'{int(v):,}'))
# headroom so the tallest bar (turn 4 ~12.7K) plus the leader-line labels
# (FIG-347-06, up to ~14.4K) are not clipped at the top spine
ax1.set_ylim(0, 14600)

# Panel 2: resulting KV
ax2.bar(x, kv_gb, 0.5, color='#c0392b', hatch='..', edgecolor='white', linewidth=0.6, label='KV / request (FP16)')
# FIG-19.2-04: value labels are HORIZONTAL, centred above each bar with ~2.4 pt
# clearance from the bar top (0.7 data units on a 0-40 axis ≈ 2.9 px... see
# check below); labels sit at staggered heights (24.9 < 27.2 < ...) so adjacent
# numbers never collide (label ~0.55 units wide vs 1 unit bar pitch).
for i, v in enumerate(kv_gb):
    ax2.annotate(f'{v:.1f}', xy=(x[i], v), xytext=(x[i], v+0.7), ha='center', va='bottom',
                 rotation=0, fontsize=8.6, color='#c0392b', fontweight='bold')
# The first bar and its value already identify the single-shot baseline.
# An additional unlabeled 24.9-GB rule duplicates that value without a key.
ax2.set_ylabel('KV / request (GB, FP16)', fontsize=9)
# title shortened so "GB" is not clipped at the right edge of the panel
ax2.set_title('(b) KV 24.9 \u2192 34.0 GB', fontsize=9)
ax2.grid(alpha=0.3, axis='y')
ax2.legend(handles=[Patch(fc='#c0392b', ec='#333', hatch='..', label='KV / request (FP16)')],
           fontsize=8.6, loc='upper center', bbox_to_anchor=(0.5, -0.29), ncol=1, frameon=False)
ax2.tick_params(labelsize=8.6)
# headroom check: tallest horizontal label = 34.0 + 0.7 offset + ~3.0 units of
# text height ≈ 37.7 < 40, so nothing clips at the top spine (was 48 when the
# labels were rotated and stood ~13 units tall).
ax2.set_ylim(0, 40)

for ax in (ax1, ax2):
    ax.set_xticks(x)
    ax.set_xticklabels(['0\n(single-shot)', '1', '2', '3', '4'], fontsize=8.6)
    # x-axis title directly under each panel's ticks (was a single floating fig.text
    # that landed far below the legends, detached from the axes)
    ax.set_xlabel('Agent turns', fontsize=8.6)

fig.suptitle('Token growth vs resulting KV growth across agent turns', fontsize=10.5, fontweight='bold')
# explicit in-plot statement that this is an append-only illustrative model
fig.text(0.5, 0.86, 'append-only bounding case: context only ever accumulates across turns — nothing is evicted',
         ha='center', va='top', fontsize=8.6, style='italic', color='#444')
# counterfactual column semantics (R08): each column is a SEPARATE completion
# after T turns (incl. one final 300-token answer), not successive states of one
# live agent.  Placed in the empty band between the x-labels and the legend —
# NOTE (FIG-19.2-02): the legend now sits ABOVE this block, so the reader meets
# the swatches before the note. Last line is the FIG-19.2-1 resolution note.
fig.text(0.5, 0.060,
         'counterfactual: each column = a separate completion after T turns,\n'
         'including one final 300-token answer — not successive states of one live agent.\n'
         'Bars are RETAINED context/KV, not summed per-call processed or billed tokens;\n'
         'tokens per submitted request grow ~2.5x under no prefix reuse (mix 68/25/5/2%, Table 19-1: 2.52x).\n'
         '(a) generated (γ=65/turn) is below visual resolution at this scale — see legend and Fig 19.3.\n'
         '(b) KV GB = tokens × 2.62 MB/token (FP16).',
         ha='center', va='center', fontsize=8.6, color='#222')
plt.subplots_adjust(left=0.12, right=0.97, top=0.78, bottom=0.385, wspace=0.40)
plt.savefig('design/manuscript/chapter-19/figures/fig-19-1902.png',
            dpi=400, bbox_inches='tight', pad_inches=0.05)
# vector copy for the build's vector guard (mtime(pdf) >= mtime(png)); PDF saved last
with plt.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-19/figures/fig-19-1902.pdf', format='pdf')
plt.close()
print('wrote fig-19-1902 (narrow, tight-bbox, append-only label + grayscale hatch split)')
