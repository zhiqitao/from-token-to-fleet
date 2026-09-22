#!/usr/bin/env python3
"""fig-15-1502: FlashAttention — why it is faster (I/O-aware, not magic).

Author at exactly the 6.1in book column width so regen_figs does NOT boost fonts.

Job (directive #6): FlashAttention is NOT "faster attention."  It reorganizes the
attention computation into tiles that exploit fast on-chip memory and kernel
fusion.  The math result is preserved; the *expensive HBM traffic* is reduced.
So the speed-up comes from I/O-aware execution, not from changing the attention
mathematics.  The figure must show DATA MOVEMENT before and after, not a
speed-up number.

Two panels, same attention computation:
  [BEFORE] naive: for each query block, the full Q,K,V row-block is loaded from
           HBM repeatedly -> O(L^2) HBM traffic (the intermediate attention
           matrix is materialized to HBM).
  [AFTER]  FlashAttention: tiles stream through shared memory/registers; the
           softmax is computed online and the attention result accumulated in
           on-chip memory -> the large intermediate never leaves the chip.

Consistent visual grammar: compute = blue, HBM = orange, on-chip = lighter blue,
HBM traffic arrows = orange dashed (reduced in AFTER).

Layout computed.  1 data unit == 1 point.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

BOLD = FontProperties(weight='bold')
FS = 12.0
W = 6.1 * 72
Ht = 5.4 * 72

def tw(s, fs=FS):
    return TextPath((0, 0), s, size=fs, prop=BOLD).get_extents().width

fig, ax = plt.subplots(figsize=(6.1, 5.4))
ax.set_xlim(0, W); ax.set_ylim(0, Ht); ax.axis('off')

C_COMP='#27408b'; C_ONCHIP='#5b8ec9'; C_HBM='#e67e22'; C_TRAFFIC='#c0392b'
C_TXT='#333'; C_TRAFFIC_LT='#e8a9a0'

def label(cx, cy, text, color=C_TXT, fs=FS-0.4, ha='center', weight='normal', style='normal'):
    ax.text(cx, cy, text, ha=ha, va='center', fontsize=fs, color=color, fontweight=weight, style=style)

label(W/2, Ht-10, 'FlashAttention: the same math, far less HBM traffic',
      '#1a1a1a', FS+1.0, weight='bold')

# two panels
pw = (W-52)/2
p1x0, p1x1 = 16, 16+pw
p2x0, p2x1 = p1x1+20, W-16
panel_top = Ht-34
panel_h = 300

def draw_panel(x0, x1, title, subtitle, flash):
    # panel box
    ax.add_patch(FancyBboxPatch((x0, panel_top-panel_h), (x1-x0), panel_h,
                  boxstyle='round,pad=0.02,rounding_size=2',
                  fc='#f7f7f7', ec='#ccc', lw=1.0, clip_on=False))
    label((x0+x1)/2, panel_top-12, title, '#1a1a1a', FS, weight='bold')
    label((x0+x1)/2, panel_top-26, subtitle, '#666', FS-1.1, style='italic')
    # on-chip compute block (top)
    cb_cx=(x0+x1)/2; cb_cy=panel_top-52
    cbw=x1-x0-24; cbh=34
    ax.add_patch(FancyBboxPatch((cb_cx-cbw/2, cb_cy-cbh/2), cbw, cbh,
                  boxstyle='round,pad=0.02', fc=C_ONCHIP, ec='#16295c', lw=1.2, clip_on=False))
    # on-chip block label kept short so it never overflows the narrow box
    label(cb_cx, cb_cy-2, 'on-chip', '#fff', FS-0.5, weight='bold')
    # HBM block (bottom)
    hb_cy=panel_top-215
    hbw=x1-x0-24; hbh=34
    ax.add_patch(FancyBboxPatch((cb_cx-hbw/2, hb_cy-hbh/2), hbw, hbh,
                  boxstyle='round,pad=0.02', fc=C_HBM, ec='#8a3a12', lw=1.2, clip_on=False))
    label(cb_cx, hb_cy, 'HBM', '#fff', FS-0.4, weight='bold')

    # explicit MANY (before) vs FEW (after) HBM round-trips between on-chip and HBM
    n_arrows = 7 if not flash else 2
    lw = 1.4 if not flash else 1.1
    # arrows span only the RIGHT portion of the blocks, leaving a clear LEFT gutter
    # for the round-trips + Q/K/V labels (so no shaft ever crosses them)
    gutter = 70
    span_left = cb_cx - (cbw/2) + gutter
    span_right = cb_cx + (cbw/2) - 12
    for i in range(n_arrows):
        axx = span_left + i*(span_right-span_left)/max(n_arrows-1, 1)
        color = C_TRAFFIC if not flash else C_TRAFFIC_LT
        ax.annotate('', xy=(axx, hb_cy+hbh/2), xytext=(axx, cb_cy-cbh/2),
                    arrowprops=dict(arrowstyle='-|>', lw=lw, color=color,
                                    shrinkA=0, shrinkB=0), annotation_clip=False)
    # 'round-trips' label in the clear LEFT gutter (never crossed by arrows)
    label(x0+30, (cb_cy+hb_cy)/2,
          ('many HBM\nround-trips' if not flash else 'few HBM\nround-trips'),
          C_TRAFFIC if not flash else '#2f6f4f', FS-1.0, weight='bold')
    # Q/K/V note in the clear LEFT gutter beside HBM
    label(x0+30, hb_cy, 'Q/K/V', '#8a5a2a', FS-1.2, style='italic')
    # caption of traffic reduction
    if not flash:
        cap = ('O(L^2) HBM traffic:\nevery query re-reads\nthe row-block')
    else:
        cap = ('O(L) HBM traffic:\neach tile read once,\nsoftmax online')
    label((x0+x1)/2, panel_top-panel_h-12, cap,
          C_TRAFFIC if not flash else '#2f6f4f', FS-1.6)

draw_panel(p1x0, p1x1, 'BEFORE: naive / SDPA', 'intermediate written to HBM', False)
draw_panel(p2x0, p2x1, 'AFTER: FlashAttention', 'tiled, stays on-chip', True)

# divider + takeaway banner
banner_y = panel_top-panel_h-58
label(W/2, banner_y, 'same Q·Kᵀ·V math and same result —\nthe gain is fewer HBM round-trips, not cheaper attention',
      '#2f6f4f', FS-0.5, weight='bold')

plt.tight_layout(pad=0.2)
plt.savefig('design/manuscript/chapter-15/figures/fig-15-1502.png', dpi=200)
plt.close()
print('wrote fig-15-1502 (FlashAttention before/after)')
