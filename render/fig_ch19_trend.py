import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-19-1902: token + KV growth across agent turns (Ch19 Table 19-1) ----
# Two aligned panels (NOT a dual-axis) so token accumulation and the resulting
# KV are read as effect->consequence without implying a shared causal axis.
# I0=9200, delta=800, gamma=65, O_final=300, per-token KV=2.5 MB
I0, d, g, Of = 9200, 800, 65, 300
kv_mb = 2.5
Ts = np.arange(0, 5)
inp = I0 + Ts*d + Ts*g
out = Of
kv_gb = (inp + out) * kv_mb / 1000   # per-request KV (decimal convention)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.6), sharex=True)
w = 0.4
x = Ts

# Panel 1: token accumulation
b1 = ax1.bar(x - w/2, inp, w, color='#3a6ea5', hatch='//', edgecolor='white', linewidth=0.6, label='input tokens')
b2 = ax1.bar(x - w/2, [Of]*5, w, bottom=inp, color='#6f9e5f', hatch='..', edgecolor='white', linewidth=0.6, label='output tokens')
ax1.set_ylabel('Tokens per request')
ax1.set_title('(a) Tokens accumulate', fontsize=11)
ax1.grid(alpha=0.3, axis='y')
ax1.legend(fontsize=8, loc='upper left')

# Panel 2: resulting KV
ax2.bar(x, kv_gb, 0.5, color='#c0392b', hatch='..', edgecolor='white', linewidth=0.6, label='KV cache per request (FP16)')
for i, v in enumerate(kv_gb):
    ax2.annotate(f'{v:.1f}', xy=(x[i], v), xytext=(x[i], v+0.6), ha='center', fontsize=8.5, color='#c0392b', fontweight='bold')
ax2.axhline(23.8, color='#888', ls=':', lw=1)
ax2.text(0.05, 24.6, 'single-shot 23.8', fontsize=7.5, color='#555')
ax2.set_ylabel('KV cache per request (GB, FP16)')
ax2.set_title('(b) KV grows 23.8 → 32.4 GB', fontsize=11)
ax2.grid(alpha=0.3, axis='y')
ax2.legend(fontsize=8, loc='upper left')

for ax in (ax1, ax2):
    ax.set_xlabel('Agent turns')
    ax.set_xticks(x)
    ax.set_xticklabels(['0 (single-shot)', '1', '2', '3', '4'])

fig.suptitle('Ch19 — token growth and the resulting KV growth across agent turns', fontsize=12, fontweight='bold')
plt.tight_layout(rect=(0, 0, 1, 0.95))
plt.savefig('design/manuscript/chapter-19/figures/fig-19-1902.png', dpi=150)
plt.close()
print('wrote fig-19-1902 (two-panel)')
