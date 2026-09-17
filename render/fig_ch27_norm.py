import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-27-2704: vendor-reported KV/token and FLOP/token reductions ----
# HONEST normalisation: the percentages are each model's vendor-reported ratio
# of its *own* stated reference (e.g. DeepSeek V4 vs V3.2), NOT a cross-model
# percentage of a canonical 70B dense full-MHA.  We therefore do NOT label the
# y-axis "% of canonical 70B" (that would be an invalid normalisation bridge).
# Instead each bar is labelled against its stated reference, and the canonical
# 70B full-MHA bar (100%) is shown only as the book's teaching floor for scale.
models = ['Canonical\n70B dense\n(full-MHA)', 'DeepSeek\nV4-Flash', 'DeepSeek\nV4-Pro', 'GLM-5.3\nFlash']
kv = [100, 7, 10, 23]     # vendor-reported KV vs own reference
flop = [100, 10, 27, 33]  # vendor-reported FLOP vs own reference

x = np.arange(len(models))
w = 0.38
fig, ax = plt.subplots(figsize=(6.3, 3.9))
b1 = ax.bar(x - w/2, kv, w, label='KV per token (vs its own reference)', color='#c0392b', alpha=0.9)
b2 = ax.bar(x + w/2, flop, w, label='inference FLOP per token (vs its own reference)', color='#3a6ea5', alpha=0.9)
for bars in (b1, b2):
    for r in bars:
        lab = '100%' if abs(r.get_height()-100) < 1 else f'~{int(r.get_height())}%'
        ax.text(r.get_x() + r.get_width()/2, r.get_height() + 2, lab,
                ha='center', fontsize=7.5, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=7.5)
ax.set_ylabel('Vendor-reported reduction vs stated reference (%)', fontsize=8)
ax.set_ylim(0, 130)
ax.set_title('KV/token and FLOP/token are a moving target\n(vendor-reported vs each model\u2019s own reference, not a cross-model baseline)', fontsize=8.5)
ax.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, 1.0), ncol=1, frameon=False)
ax.grid(axis='y', alpha=0.3)
ax.axhline(100, color='#888', ls='--', lw=1)
ax.tick_params(labelsize=7.5)
plt.tight_layout()
plt.savefig('design/manuscript/chapter-27/figures/fig-27-2704.png',
            dpi=200, bbox_inches='tight', pad_inches=0.08)
plt.close()
print('wrote fig-27-2704 (honest per-model reference labels)')
