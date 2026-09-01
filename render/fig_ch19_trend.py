import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-19-1902: token + KV growth across agent turns (Ch19 Table 19-1) ----
# I0=9200, delta=800, gamma=65, O_final=300, per-token KV=2.5 MB
I0, d, g, Of = 9200, 800, 65, 300
kv_mb = 2.5
Ts = np.arange(0, 5)  # turns 0..4
inp = I0 + Ts*d + Ts*g         # input tokens at each turn count
out = Of
kv_gb = (inp + out) * kv_mb / 1000   # KV GB per request, decimal convention (/1000) to match prose 23.8->32.4

fig, ax = plt.subplots(figsize=(8.5, 5))
# grouped bars: input tokens (blue) + output (green) per turn profile
ax2 = ax.twinx()
w = 0.4
x = Ts
b1 = ax.bar(x - w/2, inp, w, color='#3a6ea5', label='input tokens')
b2 = ax.bar(x - w/2, [Of]*5, w, bottom=inp, color='#6f9e5f', label='output tokens')
# KV line on twin axis
ax2.plot(x, kv_gb, '-o', color='#c0392b', lw=2, label='KV cache (GB, FP16)')
for i, v in enumerate(kv_gb):
    ax2.annotate(f'{v:.1f} GB', xy=(x[i], v), xytext=(x[i]+0.15, v+0.5), fontsize=8, color='#c0392b')
ax.set_xlabel('Agent turns')
ax.set_ylabel('Tokens per request')
ax2.set_ylabel('KV cache per request (GB, FP16)')
ax.set_xticks(x)
ax.set_xticklabels(['0 (single-shot)', '1', '2', '3', '4'])
ax.set_title('Ch19 — token growth and KV growth across agent turns (23.8 → 32.4 GB)')
hline_y = np.interp(1.25, Ts, kv_gb)
ax2.axhline(23.8, color='#888', ls=':', lw=1)
ax2.text(3.6, 23.8+0.8, 'single-shot 23.8', fontsize=8, color='#555')
lines = [b1, b2]
labels = [l.get_label() for l in lines]
l1, lab1 = ax.get_legend_handles_labels()
l2, lab2 = ax2.get_legend_handles_labels()
ax.legend(l1+l2, lab1+lab2, fontsize=8, loc='upper left')
ax.grid(alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('design/manuscript/chapter-19/figures/fig-19-1902.png', dpi=150)
plt.close()
print('wrote fig-19-1902')
