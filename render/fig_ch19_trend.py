import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-19-1902: token + KV growth across agent turns (Ch19 Table 19-1) ----
# Two aligned panels. Authored NARROW (6.4in) + tight bbox so it never overflows
# the ~6.1in print column or clips the title/labels.
I0, d, g, Of = 9200, 800, 65, 300
kv_mb = 2.62   # canonical decimal KB/token (max-KV convention incl. output)
Ts = np.arange(0, 5)
inp = I0 + Ts*d + Ts*g
out = Of
kv_gb = (inp + out) * kv_mb / 1000

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.1, 4.3), sharex=True)
fig._hermes_print_sized = True   # regen must not re-boost/reflow
w = 0.4
x = Ts

# Panel 1: token accumulation — split initial context vs turn-by-turn additions
# so the two are distinguishable in grayscale (distinct grays + distinct hatches).
base = np.full(5, I0)               # initial prompt context (constant)
added = Ts*(d + g)                  # appended per turn (delta retrieved + gamma generated)
ax1.bar(x - w/2, base, w, color='#2f5a8f', hatch='//', edgecolor='white', linewidth=0.6, label='initial context (I0)')
ax1.bar(x - w/2, added, w, bottom=base, color='#d98a2b', hatch='//', edgecolor='#7a4a10', linewidth=0.6, label='added per turn (T\u00b7\u03b4 + T\u00b7\u03b3)')
ax1.bar(x - w/2, [Of]*5, w, bottom=inp, color='#6f9e5f', hatch='xx', edgecolor='white', linewidth=0.6, label='output tokens')
ax1.set_ylabel('Tokens / request', fontsize=9)
ax1.set_title('(a) Tokens accumulate', fontsize=9.5)
ax1.grid(alpha=0.3, axis='y')
ax1.legend(fontsize=7.7, loc='upper center', bbox_to_anchor=(0.5, -0.42), ncol=3, frameon=False)
ax1.tick_params(labelsize=8)

# Panel 2: resulting KV
ax2.bar(x, kv_gb, 0.5, color='#c0392b', hatch='..', edgecolor='white', linewidth=0.6, label='KV / request (FP16)')
for i, v in enumerate(kv_gb):
    ax2.annotate(f'{v:.1f}', xy=(x[i], v), xytext=(x[i], v+0.6), ha='center', fontsize=8, color='#c0392b', fontweight='bold')
ax2.axhline(24.9, color='#888', ls=':', lw=1)
ax2.set_ylabel('KV / request (GB, FP16)', fontsize=9)
ax2.set_title('(b) KV grows 24.9 \u2192 34.0 GB', fontsize=9.5)
ax2.grid(alpha=0.3, axis='y')
ax2.legend(fontsize=7.5, loc='upper center', bbox_to_anchor=(0.5, -0.42), ncol=1, frameon=False)
ax2.tick_params(labelsize=8)
# headroom so the tallest value label (34.0) is not clipped at the top spine
ax2.set_ylim(0, 38)

for ax in (ax1, ax2):
    ax.set_xticks(x)
    ax.set_xticklabels(['0\n(single-shot)', '1', '2', '3', '4'], fontsize=8)

# single shared x-label at the very bottom (clear of both legends)
fig.text(0.5, 0.015, 'Agent turns', fontsize=9, ha='center')

fig.suptitle('Token growth vs resulting KV growth across agent turns', fontsize=10.5, fontweight='bold')
# explicit in-plot statement that this is an append-only illustrative model
fig.text(0.5, 0.875, 'append-only illustrative model: context only ever accumulates across turns — nothing is evicted',
         ha='center', va='top', fontsize=7.5, style='italic', color='#444')
plt.tight_layout(rect=(0, 0.05, 1, 0.86))
plt.savefig('design/manuscript/chapter-19/figures/fig-19-1902.png',
            dpi=200, bbox_inches='tight', pad_inches=0.05)
plt.close()
print('wrote fig-19-1902 (narrow, tight-bbox, append-only label + grayscale hatch split)')
