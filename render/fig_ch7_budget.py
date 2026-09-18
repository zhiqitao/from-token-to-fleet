"""Fig 7.4 - The concurrency budget: where a 70B host's 640 GB HBM pool goes.

   weights 140 GB + runtime/NCCL ~64 GB + KV budget ~436 GB = 640 GB pool
   C(FP16) = 436 / 24.9 per-request KV (9.5K max) ~ 18 concurrent requests
   C(FP8)  = 436 / 13.4            ~ 33 concurrent requests
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

weights, runtime, kv = 140, 64, 436
total = weights + runtime + kv  # 640
kv_fp16_req = 24.9
kv_fp8_req = 13.4
C_fp16 = kv / kv_fp16_req
C_fp8 = kv / kv_fp8_req

fig, ax = plt.subplots(figsize=(9, 5.2))

y = 0.0
kv_start = weights + runtime

# FP16 row
ax.barh(y, weights, left=0, height=0.8, color='#3a6ea5', edgecolor='white', hatch='//', lw=0.5)
ax.barh(y, runtime, left=weights, height=0.8, color='#9aa0a6', edgecolor='white', hatch='xx', lw=0.5)
ax.barh(y, kv, left=weights + runtime, height=0.8, color='#6f9e5f', edgecolor='white', hatch='..', lw=0.5)

# FP8 row (faint overlay)
y8 = -0.95
ax.barh(y8, weights, left=0, height=0.7, color='#3a6ea5', alpha=0.35, edgecolor='none')
ax.barh(y8, runtime, left=weights, height=0.7, color='#9aa0a6', alpha=0.35, edgecolor='none')
ax.barh(y8, kv, left=weights + runtime, height=0.7, color='#6f9e5f', alpha=0.30, edgecolor='none')

# KV slot ticks
x = kv_start
while x + kv_fp16_req <= total + 0.5:
    ax.axvline(x, ymin=0.18, ymax=0.82, color='white', lw=0.8, alpha=0.7)
    x += kv_fp16_req
xx = kv_start
while xx + kv_fp8_req <= total + 0.5:
    ax.axvline(xx, ymin=0.12, ymax=0.88, color='white', lw=0.5, alpha=0.5, ls=':')
    xx += kv_fp8_req

# ---- In-segment labels (white, inside each segment => never overlap a neighbor) ----
ax.text(weights / 2, y, f'{weights} GB\nweights', ha='center', va='center', color='white', fontsize=9.5, fontweight='bold')
ax.text(weights + runtime / 2, y, f'~{runtime} GB\nruntime', ha='center', va='center', color='white', fontsize=8.8, fontweight='bold')
ax.text(kv_start + kv / 2, y, f'KV budget\n~{kv} GB', ha='center', va='center', color='white', fontsize=9.5, fontweight='bold')

# ---- Totals & derivation above/below the bars (single baseline each) ----
ax.text(kv_start + kv / 2, y + 0.95, f'~{kv} GB KV @ FP16 (2.62 MB/token, 9.5K max)', ha='center', va='bottom', color='#27408b', fontsize=9)

# FP8 note below
ax.text(kv_start + kv / 2, y8 - 0.55, f'FP8 KV: ~{C_fp8:.0f} slots (436 ÷ {kv_fp8_req:.1f} GB/request)', ha='center', va='top', color='#6f9e5f', fontsize=9.5, style='italic')

# Concurrency derivation callout to the right
ax.annotate(f'C ≈ {C_fp16:.0f} concurrent\nrequests @ FP16\n(436 ÷ {kv_fp16_req:.1f} GB/request)',
            xy=(total, y), xytext=(total + 18, y + 0.1), fontsize=9.5, color='#27408b',
            ha='left', va='center', arrowprops=dict(arrowstyle='->', color='#27408b', lw=1.1))
ax.text(total + 18, y - 0.75, '8×H100 pool = 640 GB', fontsize=9, color='#666', ha='left', va='center')

ax.set_xlim(-5, total + 95)
ax.set_ylim(-2.4, 1.6)
ax.set_yticks([y, y8])
ax.set_yticklabels(['FP16 KV', 'FP8 KV'], fontsize=10)
ax.set_xlabel('on-host HBM (GB, per 8×H100 host)', fontsize=10.5)
ax.set_title('Fig 7.4 — Where a 640 GB host pool goes [2° DERIVED]', fontsize=11)
ax.tick_params(axis='x', labelsize=9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0704.png', dpi=150)
plt.close()
print('wrote fig-07-0704')
