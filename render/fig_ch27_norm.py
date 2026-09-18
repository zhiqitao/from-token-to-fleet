import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-27-2704: vendor-reported KV/token and FLOP/token reductions ----
# The percentages are each model's vendor-reported ratio of its OWN stated
# reference (e.g. DeepSeek V4 vs V3.2), so they are NOT comparable across a
# shared y-axis with a canonical 70B baseline.  We therefore show ONLY the
# vendor models here, and move the canonical 70B dense full-MHA teaching model
# into a separate callout text (not a bar on the same axis).
models = ['DeepSeek\nV4-Flash', 'DeepSeek\nV4-Pro', 'GLM-5.3\nFlash']
kv = [7, 10, 23]     # vendor-reported KV vs own reference
flop = [10, 27, 33]  # vendor-reported FLOP vs own reference

x = np.arange(len(models))
w = 0.38
fig, ax = plt.subplots(figsize=(6.3, 3.9))
b1 = ax.bar(x - w/2, kv, w, label='KV per token (vs its own reference)', color='#c0392b', alpha=0.9)
b2 = ax.bar(x + w/2, flop, w, label='inference FLOP per token (vs its own reference)', color='#3a6ea5', alpha=0.9)
for bars in (b1, b2):
    for r in bars:
        ax.text(r.get_x() + r.get_width()/2, r.get_height() + 1.2, f'~{int(r.get_height())}%',
                ha='center', fontsize=8.5, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=8.5)
ax.set_ylabel('Vendor-reported reduction vs stated reference (%)', fontsize=8.5)
ax.set_ylim(0, 45)
ax.set_title('Vendor-reported KV/FLOP reduction relative to each model\u2019s\nstated predecessor/reference (not a cross-model baseline)', fontsize=8.5)
ax.legend(fontsize=7.5, loc='upper right', ncol=1, frameon=False)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('design/manuscript/chapter-27/figures/fig-27-2704.png',
            dpi=200, bbox_inches='tight', pad_inches=0.08)
plt.close()
print('wrote fig-27-2704 (vendor-only, no canonical-100% bar)')
