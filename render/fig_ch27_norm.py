import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-27-2704: vendor-reported KV/token and FLOP/token reductions ----
# Each percentage is a model's vendor-reported ratio of its OWN stated reference
# (e.g. DeepSeek V4 vs V3.2), so they are NOT comparable across a shared axis.
# We therefore render ONE INDEPENDENT subplot per model, each with its own y-axis
# and its own reference label, so no cross-model height comparison is possible.
# The canonical 70B full-MHA teaching model is deliberately NOT drawn as a bar.
panels = [
    {"name": "DeepSeek V4-Flash", "ref": "vs V3.2", "kv": 7,  "flop": 10},
    {"name": "DeepSeek V4-Pro",   "ref": "vs V3.2", "kv": 10, "flop": 27},
    {"name": "GLM-5.3-Flash",     "ref": "vs stated ref", "kv": 23, "flop": 33},
]

fig, axes = plt.subplots(1, len(panels), figsize=(6.1, 3.79))
if len(panels) == 1:
    axes = [axes]
w = 0.36
for ax, p in zip(axes, panels):
    vals = [p["kv"], p["flop"]]
    labels = ['KV\n/token', 'FLOP\n/token']
    colors = ['#c0392b', '#3a6ea5']
    bars = ax.bar([0, 1], vals, w, color=colors, alpha=0.9)
    for r, v in zip(bars, vals):
        ax.text(r.get_x() + r.get_width()/2, r.get_height() + 1.0, f'~{v}%',
                ha='center', fontsize=9.5, fontweight='bold')
    ax.set_xticks([0, 1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, max(max(vals), 25) * 1.25)
    ax.set_title(p["name"] + "\n" + p["ref"], fontsize=9, color='#333')
    ax.grid(axis='y', alpha=0.3)
    ax.tick_params(labelsize=8.5)

# shared y axis label, but each panel's scale is its OWN (independent)
fig.text(0.01, 0.5, 'Vendor-reported reduction\n(vs each model’s own reference)', va='center',
         rotation=90, fontsize=9, color='#333')
# PROMINENT not-comparable warning (the reviewer's key point): bold boxed banner, not small grey text
fig.text(0.5, 0.045, 'NOT COMPARABLE ACROSS PANELS', ha='center', fontsize=10,
         fontweight='bold', color='#c0392b',
         bbox=dict(boxstyle='round,pad=0.35', fc='#fdecea', ec='#c0392b', lw=1.4))
fig.text(0.5, -0.01, 'Each bar is a model\u2019s reduction relative to its OWN stated predecessor/reference, '
                    'not a shared baseline.', ha='center', fontsize=8, color='#555')

plt.tight_layout(rect=(0.04, 0.07, 1, 1))
plt.savefig('design/manuscript/chapter-27/figures/fig-27-2704.png',
            dpi=200, bbox_inches='tight', pad_inches=0.08)
plt.close()
print('wrote fig-27-2704 (independent per-model panels, prominent not-comparable warning)')
