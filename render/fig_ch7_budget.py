"""Fig 7.4 - The concurrency budget, redrawn (publication review: too dense).

The reviewer flagged this as one of the densest figures: "too many tiny
quantities around a small graphical core".  Redesign around the DOMINANT
budget relationship: C = KV budget / KV per request, shown as one large
equation with a single region-band bar carrying the physical decomposition.
Secondary arithmetic (FP8 variant, integer-floor detail, per-rank geometry)
is moved to the figure caption / body, not drawn in the raster.

Authored at column width so fonts print near-native, print-sized.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

weights, runtime, kv = 140, 64, 436
total = weights + runtime + kv
kv_fp16_req = 24.9037
C_fp16 = kv / kv_fp16_req          # ~17.51 -> integer floor 17

fig, ax = plt.subplots(figsize=(6.1, 3.9))
fig._hermes_print_sized = True
ax.set_xlim(0, 10); ax.set_ylim(0, 6.6); ax.axis('off')
ax.set_position((0, 0, 1, 1))

# ---- title (short; explanation lives in the caption) ----
ax.text(5.0, 6.28, 'Concurrency budget — one 8×H100 host',
        fontsize=11.0, fontweight='bold', ha='center', va='center', color='#1a1a1a')

# ---- region-band budget bar (0..640 GB mapped across the width) ----
bx0, bx1 = 0.5, 10.4                 # bar spans this x range
bar_y, bar_h = 4.85, 0.85
def gb_to_x(g): return bx0 + (g / total) * (bx1 - bx0)
def label(x, gb, txt, fc):
    ax.text(x, bar_y + bar_h / 2.0, txt, ha='center', va='center',
            fontsize=9.0, color='white', fontweight='bold')

# weights region
ax.add_patch(Rectangle((gb_to_x(0), bar_y), gb_to_x(weights) - gb_to_x(0), bar_h,
                       fc='#3a6ea5', ec='white', hatch='//', lw=0.5))
label((gb_to_x(0) + gb_to_x(weights)) / 2.0, 0, '140 GB\nweights', '#ffffff')
# runtime region
ax.add_patch(Rectangle((gb_to_x(weights), bar_y), gb_to_x(weights + runtime) - gb_to_x(weights), bar_h,
                       fc='#9aa0a6', ec='white', hatch='xx', lw=0.5))
label((gb_to_x(weights) + gb_to_x(weights + runtime)) / 2.0, 0, '~64 GB\nruntime', '#ffffff')
# KV budget region (the dominant band)
ax.add_patch(Rectangle((gb_to_x(weights + runtime), bar_y), gb_to_x(total) - gb_to_x(weights + runtime), bar_h,
                       fc='#6f9e5f', ec='white', hatch='..', lw=0.5))
label((gb_to_x(weights + runtime) + gb_to_x(total)) / 2.0, 0, '~436 GB\nKV budget', '#ffffff')

# per-request slot ticks inside the KV budget band (17.5 slots of 24.9 GB)
for k in range(1, 18):                      # 17 full slots + partial
    g = weights + runtime + k * kv_fp16_req
    if g < total:
        ax.plot([gb_to_x(g), gb_to_x(g)], [bar_y, bar_y + bar_h],
                color='#ffffff', lw=0.7, alpha=0.8)
# faint 640 GB pool reference above the bar
ax.plot([gb_to_x(0), gb_to_x(total)], [bar_y + bar_h + 0.12, bar_y + bar_h + 0.12],
        color='#7f8c8d', lw=1.0)
ax.text(gb_to_x(total), bar_y + bar_h + 0.34, '640 GB pool', ha='right', va='center',
        fontsize=8.0, color='#777777')

# ---- the DOMINANT budget equation (large, centered) ----
eq_y = 2.72
ax.text(5.0, eq_y, 'in-flight  ≈  KV budget  ÷  KV per request',
        fontsize=10.5, ha='center', va='center', color='#333333')
ax.text(5.0, eq_y - 0.85,
        f'≈  {kv:.0f} GB  ÷  {kv_fp16_req:.1f} GB  ≈  {C_fp16:.1f}   →   ~{int(C_fp16)} requests',
        fontsize=13.0, fontweight='bold', ha='center', va='center', color='#27408b')

plt.savefig('design/manuscript/chapter-07/figures/fig-07-0704.png', dpi=150)
plt.close()
print('wrote fig-07-0704')
