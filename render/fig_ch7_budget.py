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
ax.set_xlim(0, 10.9); ax.set_ylim(0, 6.6); ax.axis('off')
ax.set_position((0, 0, 1, 1))

# ---- title (short; explanation lives in the caption) ----
ax.text(5.45, 6.28, 'Concurrency budget — one 8×H100 host',
        fontsize=11.0, fontweight='bold', ha='center', va='center', color='#1a1a1a')

# ---- region-band budget bar (0..640 GB mapped across the width) ----
bx0, bx1 = 0.5, 10.4                 # bar spans this x range
bar_y, bar_h = 4.70, 1.15            # taller bar (v8 review: more breathing room for the two-line labels)
def gb_to_x(g): return bx0 + (g / total) * (bx1 - bx0)
def label(x, gb, txt, fc):
    # Solid bbox matching the fill (ec='none') so any hatch / slot lines drawn in the
    # region are hidden BEHIND the pill and never cross the white glyphs. This carries
    # into the vector PDF (path_effects do NOT), so it is the reliable fix for
    # text-over-white-pattern legibility (review: Fig 7.7).
    ax.text(x, bar_y + bar_h / 2.0, txt, ha='center', va='center',
            fontsize=9.0, color='white', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.12', fc=('#3a6ea5' if weights <= x <= gb_to_x(weights) else
                     ('#e67e22' if x >= gb_to_x(weights + runtime) else '#4a4e52')),
                     ec='none', alpha=1.0))

# weights region
ax.add_patch(Rectangle((gb_to_x(0), bar_y), gb_to_x(weights) - gb_to_x(0), bar_h,
                       fc='#3a6ea5', ec='white', hatch='//', lw=0.5))
label((gb_to_x(0) + gb_to_x(weights)) / 2.0, 0, '140 GB\nweights', '#ffffff')
# runtime region (darkened + NO hatch so the white "64" label is crisp — the earlier
# light gray + 'xx' dot hatch let the white dots fill the open top of the "6", making
# it read as "8"; a solid dark gray keeps the digit unambiguous and the contrast high)
ax.add_patch(Rectangle((gb_to_x(weights), bar_y), gb_to_x(weights + runtime) - gb_to_x(weights), bar_h,
                       fc='#4a4e52', ec='white', lw=0.5))
rt_cx = (gb_to_x(weights) + gb_to_x(weights + runtime)) / 2.0
label(rt_cx, 0, '~64 GB', '#ffffff')
# R4 fix (FIG-7.7-01): the segment's NAME moves out of the bar so the figure
# carries the caption's exact term.  Measured with the render venv at 9 pt bold:
# 'runtime/NCCL' = 101 px while the 64 GB segment is only 61 px wide (the 8 pt
# floor still needs 90 px), so the instructed in-bar wrap '~64 GB' / 'runtime/NCCL'
# cannot fit — the pill would cross both white segment boundaries by ~20 px a
# side.  The value stays in the bar (it fits: '~64 GB' = 55 px) and the name is
# set below the bar on a leader into the segment, verbatim as the caption has it.
ax.text(rt_cx, 4.15, 'runtime/NCCL', ha='center', va='top',
        fontsize=9.0, fontweight='bold', color='#4a4e52')
ax.plot([rt_cx, rt_cx], [4.15, bar_y], color='#4a4e52', lw=0.8)
# KV budget region (the dominant band).  R4 fix (FIG-7.7-7.8-1): it was green
# here while Fig 7.8's KV block is orange, so the same 640 GB pool was encoded
# two ways in adjacent figures.  Both now use orange + the same '..' dot hatch
# (7.8's pattern), so KV reads as KV across 7.7/7.8; the segment label still
# says "KV budget" (reserved) vs 7.8's "KV <n> GB" (used), and the white label
# stays crisp because the solid pill hides the dots and slot rules behind it
# (v8's dot-hatch legibility complaint was about text sitting directly on the
# pattern — the pill is the later fix for exactly that).
ax.add_patch(Rectangle((gb_to_x(weights + runtime), bar_y), gb_to_x(total) - gb_to_x(weights + runtime), bar_h,
                       fc='#e67e22', ec='white', lw=0.5, hatch='..'))
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
        fontsize=8.5, color='#4a4a4a', fontweight='bold')

# ---- the DOMINANT budget equation (large, centered) ----
eq_y = 2.72
ax.text(5.45, eq_y, 'in-flight  ≈  KV budget  ÷  KV per request',
        fontsize=10.5, ha='center', va='center', color='#333333')
ax.text(5.45, eq_y - 0.85,
        f'≈  {kv:.0f} GB  ÷  {kv_fp16_req:.1f} GB  ≈  {C_fp16:.1f}   →   ~{int(C_fp16)} requests',
        fontsize=13.0, fontweight='bold', ha='center', va='center', color='#27408b')

plt.savefig('design/manuscript/chapter-07/figures/fig-07-0704.png', dpi=350)
with matplotlib.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-07/figures/fig-07-0704.pdf', format='pdf')
plt.close()
print('wrote fig-07-0704')
