import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-27-2704: normalized KV-per-token and FLOP-per-token vs canonical 70B dense (100%) ----
# canonical 70B dense full-MHA = 100% KV, 100% FLOP/token baseline
# Values from Appendix A verified 1P claims:
#  DeepSeek-V4-Flash: KV ~7% of V3.2, FLOP ~10%  (arXiv 2606.19348)
#  DeepSeek-V4-Pro:   KV ~10%,            FLOP ~27%
#  GLM-5.3-Flash:     KV ~1/4.4 ~ 23%,    attention-compute ~1/3 ~ 33%  (HF zai-org)
models = ['Canonical\n70B dense', 'DeepSeek\nV4-Flash', 'DeepSeek\nV4-Pro', 'GLM-5.3\nFlash']
kv = [100, 7, 10, 23]
flop = [100, 10, 27, 33]

x = np.arange(len(models))
w = 0.38
fig, ax = plt.subplots(figsize=(10, 5.6))
b1 = ax.bar(x - w/2, kv, w, label='KV per token (% of canonical 70B)', color='#c0392b', alpha=0.9)
b2 = ax.bar(x + w/2, flop, w, label='single-token inference FLOP (% of canonical)', color='#3a6ea5', alpha=0.9)
for bars in (b1, b2):
    for r in bars:
        ax.text(r.get_x() + r.get_width()/2, r.get_height() + 2, f'{int(r.get_height())}%',
                ha='center', fontsize=9, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=9)
ax.set_ylabel('% of a 70B dense full-MHA baseline')
ax.set_ylim(0, 120)
ax.set_title('Appendix A — the KV constant and FLOP/token are a moving target\n(hybrid attention cuts both at the mechanism; canonical 70B = 100%)')
ax.legend(fontsize=9, loc='upper right')
ax.grid(axis='y', alpha=0.3)
ax.axhline(100, color='#888', ls='--', lw=1)
plt.tight_layout()
plt.savefig('design/manuscript/chapter-27/figures/fig-27-2704.png', dpi=150)
plt.close()
print('wrote fig-27-2704')
