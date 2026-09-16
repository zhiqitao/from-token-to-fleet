import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-27-2704: normalized KV-per-token and FLOP-per-token vs canonical 70B dense (100%) ----
# Legend placed ABOVE the plot and category labels kept short so they never
# collide.  Authored at ~6.1in so it places 1:1 (no downscale).
models = ['Canonical\n70B dense', 'DeepSeek\nV4-Flash', 'DeepSeek\nV4-Pro', 'GLM-5.3\nFlash']
kv = [100, 7, 10, 23]
flop = [100, 10, 27, 33]

x = np.arange(len(models))
w = 0.38
fig, ax = plt.subplots(figsize=(6.3, 3.9))
b1 = ax.bar(x - w/2, kv, w, label='KV per token', color='#c0392b', alpha=0.9)
b2 = ax.bar(x + w/2, flop, w, label='inference FLOP per token', color='#3a6ea5', alpha=0.9)
for bars in (b1, b2):
    for r in bars:
        ax.text(r.get_x() + r.get_width()/2, r.get_height() + 2, f'{int(r.get_height())}%',
                ha='center', fontsize=8, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=8)
ax.set_ylabel('% of 70B dense full-MHA baseline', fontsize=8.5)
ax.set_ylim(0, 130)
ax.set_title('KV/token and FLOP/token are a moving target\n(hybrid attention cuts both; canonical 70B dense = 100%)', fontsize=9)
ax.legend(fontsize=8, loc='upper center', bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False)
ax.grid(axis='y', alpha=0.3)
ax.axhline(100, color='#888', ls='--', lw=1)
ax.tick_params(labelsize=7.5)
plt.tight_layout()
plt.savefig('design/manuscript/chapter-27/figures/fig-27-2704.png',
            dpi=200, bbox_inches='tight', pad_inches=0.08)
plt.close()
print('wrote fig-27-2704 (legend above, narrow)')
