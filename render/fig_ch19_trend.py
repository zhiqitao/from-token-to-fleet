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

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.1, 3.24), sharex=True)
w = 0.4
x = Ts

# Panel 1: token accumulation
ax1.bar(x - w/2, inp, w, color='#3a6ea5', hatch='//', edgecolor='white', linewidth=0.6, label='input tokens')
ax1.bar(x - w/2, [Of]*5, w, bottom=inp, color='#6f9e5f', hatch='..', edgecolor='white', linewidth=0.6, label='output tokens')
ax1.set_ylabel('Tokens / request', fontsize=8.5)
ax1.set_title('(a) Tokens accumulate', fontsize=9)
ax1.grid(alpha=0.3, axis='y')
ax1.legend(fontsize=6.5, loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False)
ax1.tick_params(labelsize=7)

# Panel 2: resulting KV
ax2.bar(x, kv_gb, 0.5, color='#c0392b', hatch='..', edgecolor='white', linewidth=0.6, label='KV / request (FP16)')
for i, v in enumerate(kv_gb):
    ax2.annotate(f'{v:.1f}', xy=(x[i], v), xytext=(x[i], v+0.6), ha='center', fontsize=7.5, color='#c0392b', fontweight='bold')
ax2.axhline(24.9, color='#888', ls=':', lw=1)
ax2.set_ylabel('KV / request (GB, FP16)', fontsize=8.5)
ax2.set_title('(b) KV grows 24.9 → 34.0 GB', fontsize=9)
ax2.grid(alpha=0.3, axis='y')
ax2.legend(fontsize=6.5, loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=1, frameon=False)
ax2.tick_params(labelsize=7)
# headroom so the tallest value label (34.0) is not clipped at the top spine
ax2.set_ylim(0, 38)

for ax in (ax1, ax2):
    ax.set_xlabel('Agent turns', fontsize=8.5)
    ax.set_xticks(x)
    ax.set_xticklabels(['0 (single-shot)', '1', '2', '3', '4'], fontsize=7)

fig.suptitle('Token growth vs resulting KV growth across agent turns', fontsize=10, fontweight='bold')
plt.tight_layout(rect=(0, 0, 1, 0.92))
plt.savefig('design/manuscript/chapter-19/figures/fig-19-1902.png',
            dpi=200, bbox_inches='tight', pad_inches=0.05)
plt.close()
print('wrote fig-19-1902 (narrow, tight-bbox)')
