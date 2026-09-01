"""Fig 7.4 - The concurrency budget: where a 70B host's 640 GB HBM pool goes.

The single most-reused arithmetic in the book (Ch4/7/11/12/15/17/19 all cite it):
   weights 140 GB + runtime/NCCL ~64 GB + KV budget ~436 GB = 640 GB pool
   C(FP16) = 436 / 23.8 per-request KV ≈ 18 concurrent requests
   C(FP8)  = 436 / 12.4            ≈ 35 concurrent requests
This is the picture that locks the Ch7 <-> Ch17 handoff.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

weights, runtime, kv = 140, 64, 436
total = weights + runtime + kv  # 640
kv_fp16_req = 23.8   # GB per request, canonical FP16 KV
kv_fp8_req = 12.4
C_fp16 = kv / kv_fp16_req
C_fp8 = kv / kv_fp8_req

fig, ax = plt.subplots(figsize=(9, 5.2))

# ---- stacked horizontal bar (one row, y=0) ----
y = 0.0
span_weights = (0, weights)
span_runtime = (weights, weights + runtime)
span_kv = (weights + runtime, total)

ax.barh(y, weights, left=0, height=0.8, color='#3a6ea5', edgecolor='none')
ax.barh(y, runtime, left=weights, height=0.8, color='#9aa0a6', edgecolor='none')
ax.barh(y, kv, left=weights + runtime, height=0.8, color='#6f9e5f', edgecolor='none')

# ---- segment labels ----
ax.text(weights / 2, y, f'{weights} GB\nweights', ha='center', va='center',
        color='white', fontsize=10.5, fontweight='bold')
ax.text(weights + runtime / 2, y + 0.55, f'~{runtime} GB runtime/NCCL', ha='center', va='bottom',
        color='#555', fontsize=9)
ax.text((weights + runtime) + kv / 2, y, 'KV budget', ha='center', va='center',
        color='white', fontsize=11, fontweight='bold')
ax.text((weights + runtime) + kv / 2, y + 0.52, f'~{kv} GB (70B FP16, 2.5 MB/token)', ha='center', va='bottom',
        color='#27408b', fontsize=8.5)

# ---- tick the KV region in 23.8 GB slots (FP16, C~18) ----
kv_start = weights + runtime
slot = kv_fp16_req
n = 0
x = kv_start
while x + slot <= total + 0.5:
    ax.axvline(x, ymin=0.18, ymax=0.82, color='white', lw=0.8, alpha=0.7)
    x += slot
    n += 1

# ---- faint FP8 overlay (second, thinner bar) showing ~35 slots ----
y8 = -0.95
ax.barh(y8, weights, left=0, height=0.7, color='#3a6ea5', alpha=0.35, edgecolor='none')
ax.barh(y8, runtime, left=weights, height=0.7, color='#9aa0a6', alpha=0.35, edgecolor='none')
ax.barh(y8, kv, left=weights + runtime, height=0.7, color='#6f9e5f', alpha=0.30, edgecolor='none')
xx = kv_start
nn = 0
while xx + kv_fp8_req <= total + 0.5:
    ax.axvline(xx, ymin=0.12, ymax=0.88, color='white', lw=0.5, alpha=0.5, ls=':')
    xx += kv_fp8_req
    nn += 1
ax.text(kv_start + kv / 2, y8 - 0.5, f'FP8 KV: ~{C_fp8:.0f} slots (436 ÷ {kv_fp8_req:.1f} GB/request)',
        ha='center', va='top', fontsize=9.5, color='#6f9e5f', style='italic')

# ---- callouts ----
# FP16 tally to the right of the bar
ax.annotate(f'C ≈ {C_fp16:.0f} concurrent\nrequests @ FP16\n(436 ÷ 23.8 GB/request)',
            xy=(total, y), xytext=(total + 22, y + 0.25),
            fontsize=10, color='#27408b', ha='left', va='center',
            arrowprops=dict(arrowstyle='->', color='#27408b', lw=1.2))
ax.text(total + 22, y - 0.6, f'8×H100 pool = 640 GB', fontsize=9, color='#666', ha='left', va='center')

ax.set_xlim(-5, total + 95)
ax.set_ylim(-2.2, 1.3)
ax.set_yticks([y, y8])
ax.set_yticklabels(['FP16 KV', 'FP8 KV'], fontsize=10)
ax.set_xlabel('on-host HBM (GB, per 8×H100 host)', fontsize=10.5)
ax.set_title('Fig 7.4 — Where a serving host\'s 640 GB pool goes: the concurrency budget [2° DERIVED]',
             fontsize=11)
ax.tick_params(axis='x', labelsize=9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0704.png', dpi=150)
plt.close()
print('wrote fig-07-0704')
