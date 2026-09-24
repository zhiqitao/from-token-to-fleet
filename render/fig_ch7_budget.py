"""Fig 7.4 - The concurrency budget: where a 70B host's 640 GB HBM pool goes.

   weights 140 GB + runtime/NCCL ~64 GB + KV budget ~436 GB = 640 GB pool
   C(FP16) = 436 / 24.9037 per-request KV (9.5K max) ~ 17.5 (conservative integer floor 17) concurrent requests
   C(FP8)  = 436 / 13.448            ~ 32.4 (floor 32) concurrent requests

   Authored at COLUMN width (6.5in) so fonts print near-native, and the tiny
   "~64 GB runtime" label is moved OUT of its narrow segment into a call-out
   (a ~64 GB segment is too thin to house a comfortable in-bar label).
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

weights, runtime, kv = 140, 64, 436
total = weights + runtime + kv  # 640
kv_fp16_req = 24.9037
kv_fp8_req = 13.448
C_fp16 = kv / kv_fp16_req
C_fp8 = kv / kv_fp8_req

fig, ax = plt.subplots(figsize=(6.5, 4.6))

y = 0.0
kv_start = weights + runtime

# FP16 row
ax.barh(y, weights, left=0, height=0.8, color='#3a6ea5', edgecolor='white', hatch='//', lw=0.5)
ax.barh(y, runtime, left=weights, height=0.8, color='#9aa0a6', edgecolor='white', hatch='xx', lw=0.5)
ax.barh(y, kv, left=weights + runtime, height=0.8, color='#6f9e5f', edgecolor='white', hatch='..', lw=0.5)

# FP8 row (faint overlay) -- hatch 'o' adds non-colour (grayscale) redundancy vs FP16
y8 = -0.95
halo = [pe.withStroke(linewidth=3.0, foreground='white')]
ax.barh(y8, weights, left=0, height=0.7, color='#3a6ea5', alpha=0.35, hatch='o', edgecolor='#3a6ea5', lw=0.8)
ax.barh(y8, runtime, left=weights, height=0.7, color='#9aa0a6', alpha=0.35, hatch='o', edgecolor='#9aa0a6', lw=0.8)
ax.barh(y8, kv, left=weights + runtime, height=0.7, color='#6f9e5f', alpha=0.35, hatch='o', edgecolor='#6f9e5f', lw=0.8)
# FP8 row labels (weights/runtime so meaning need not be inferred from the FP16 row)
ax.text(weights / 2, y8, f'{weights} GB\nweights', ha='center', va='center', color='#27408b', fontsize=9.5, fontweight='bold', path_effects=halo)
ax.text(weights + runtime / 2, y8, f'~{runtime} GB\nruntime', ha='center', va='center', color='#555', fontsize=9, path_effects=halo)
ax.text(kv_start + kv / 2, y8, f'KV budget\n~{kv} GB', ha='center', va='center', color='#3a6a4a', fontsize=9.5, fontweight='bold', path_effects=halo)

# KV slot ticks
x = kv_start
while x + kv_fp16_req <= total + 0.5:
    ax.axvline(x, ymin=0.18, ymax=0.82, color='white', lw=0.8, alpha=0.7)
    x += kv_fp16_req
xx = kv_start
while xx + kv_fp8_req <= total + 0.5:
    ax.axvline(xx, ymin=0.12, ymax=0.88, color='white', lw=0.5, alpha=0.5, ls=':')
    xx += kv_fp8_req

# ---- NATIVE per-rank geometry: the pool is 8 × 80 GB ranks. Draw prominent
# 80 GB rank-boundary gridlines across BOTH bar rows so "aggregate ≠ per-rank"
# lives in the bar geometry (not only in the scale strip below). ----
for g in range(80, 640, 80):
    ax.plot([g, g], [y8 - 0.30, y + 0.44], color='#3d3d3d', lw=1.0,
            ls=(0, (4, 2)), zorder=2)   # behind the value labels (z3) so rank lines don't cut glyphs

# ---- In-segment labels (white, inside the roomy segments only) ----
ax.text(weights / 2, y, f'{weights} GB\nweights', ha='center', va='center', color='white', fontsize=9.5, fontweight='bold', path_effects=[pe.withStroke(linewidth=3.0, foreground='white')])
ax.text(kv_start + kv / 2, y, f'KV budget\n~{kv} GB', ha='center', va='center', color='white', fontsize=9.5, fontweight='bold', path_effects=[pe.withStroke(linewidth=3.0, foreground='white')])
# runtime label moved OUT of the thin ~64 GB segment into a clear call-out above it
ax.annotate('~64 GB runtime', xy=(weights + runtime / 2, y + 0.42), xytext=(weights + runtime / 2, 1.15),
            ha='center', fontsize=9, color='#444',
            arrowprops=dict(arrowstyle='->', color='#888', lw=1.0))

# ---- Totals & derivation above/below the bars ----
# move the KV label ABOVE the bar but offset right so it clears the reserve call-out at left
ax.text(kv_start + kv / 2, y + 1.35, f'~{kv} GB KV @ FP16 (2.62 MB/token, 9.5K max)', ha='center', va='bottom', color='#27408b', fontsize=9)

# FP8 note below
ax.text(kv_start + kv / 2, y8 - 0.55, f'FP8 KV: ~{C_fp8:.1f} slots (436 ÷ {kv_fp8_req:.3f} GB/request)', ha='center', va='top', color='#6f9e5f', fontsize=9.5, style='italic')

# concurrency derivation callout to the right (clear of the bar end)
ax.text(total + 12, y + 0.15, f'C ≈ {C_fp16:.1f} concurrent\nrequests @ FP16', fontsize=9.5, color='#27408b', ha='left', va='center')
ax.text(total + 12, y - 0.75, '8×H100 = 640 GB', fontsize=9, color='#666', ha='left', va='center')

# ---- reviewer's ask (Fig 7.4): aggregate screen != per-rank fit; mark reserve; show 8 GPUs ----
# Native per-rank geometry: add a dedicated 8-rank scale strip BELOW the bars (separate from
# the data), so the pool's 8x80 GB structure is encoded natively without cluttering the bars.
import numpy as np
from matplotlib.patches import Rectangle
rank_w = total / 8.0
strip_y = -2.85
for g in range(8):
    ax.add_patch(Rectangle((g * rank_w, strip_y), rank_w, 0.5, fc='#eef1f5', ec='#8a8a8a', lw=0.8))
    ax.text(g * rank_w + rank_w/2, strip_y + 0.25, f'{(g+1)*80:.0f}G', ha='center', va='center', fontsize=7.2, color='#555')
# per-rank caption BELOW the strip (va=top so it extends downward, clear of the strip and the FP8 note)
ax.text(0.05, strip_y - 0.18, '8 × 80 GB per-rank pool  (the aggregate screen ≠ a per-rank fit guarantee)',
        ha='left', va='top', fontsize=7.8, color='#777', style='italic')

# 2. Reserve is a SCENARIO assumption, not a hardware constant (placed in the
#    clearly-free upper-LEFT whitespace, above the weight segment)
ax.text(weights + runtime/2, 1.10, 'scenario reserve\n(not a hardware constant)', ha='center', va='center',
        fontsize=8, color='#444', bbox=dict(boxstyle='round,pad=0.15', fc='#f4f4f4', ec='#bbbbbb', lw=0.6))

# 3. Prominent aggregate-vs-per-rank warning
ax.text(total*0.5, 1.85, 'AGGREGATE RESIDENCY SCREEN ≠ PER-RANK FIT GUARANTEE', ha='center', va='center',
        fontsize=10, color='#c0392b', fontweight='bold')

ax.set_xlim(-5, total + 320)
ax.set_ylim(-3.6, 2.3)
ax.set_yticks([y, y8])
ax.set_yticklabels(['FP16 KV', 'FP8 KV'], fontsize=10)
ax.set_xlabel('on-host HBM (GB, per 8×H100 host)', fontsize=10.5)
ax.set_title("Concurrency budget: where a 70B host's 640 GB pool goes", fontsize=11)
ax.tick_params(axis='x', labelsize=9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.subplots_adjust(left=0.14, right=0.97, top=0.88, bottom=0.12)
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0704.png', dpi=150)
plt.close()
print('wrote fig-07-0704 (column width; runtime label moved out of thin segment)')
