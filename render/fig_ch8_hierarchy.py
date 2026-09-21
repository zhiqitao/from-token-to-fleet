#!/usr/bin/env python3
"""fig-08-0802: Hardware hierarchy mental model (where inference work happens).

Author at exactly the 6.1in book column width so regen_figs does NOT boost fonts.

Job: give the reader a memorable physical model of where inference compute and
data movement actually occur, and why FLOPS / HBM-bandwidth / HBM-capacity /
interconnect-bandwidth become distinct architectural constraints.  Central
tension: small + very fast + close <-> large + slower + farther.

Three clean columns: [A] the hierarchy ladder (top->bottom), [B] what runs at
each level, [C] the speed<->capacity gradient.  1 data unit == 1 point.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.font_manager import FontProperties

BOLD = FontProperties(weight='bold')
FS = 11.5
W = 6.1 * 72
Ht = 5.9 * 72
PADX = 0.28

def rw(s, fs=FS):
    """Width of a rendered bold string in points (uses the actual renderer, not the
    TextPath heuristic, which under-estimates the drawn DejaVu bold width ~40% and
    lets labels clip at the box edge)."""
    fig, ax = plt.subplots()
    fig.canvas.draw()
    t = ax.text(0, 0, s, fontsize=fs, fontweight='bold')
    w = t.get_window_extent(fig.canvas.get_renderer()).width
    plt.close(fig)
    return w

fig, ax = plt.subplots(figsize=(6.1, 5.9))
ax.set_xlim(0, W); ax.set_ylim(0, Ht); ax.axis('off')

C_ONCHIP='#27408b'; C_MEM='#e67e22'; C_NET='#2e9e63'; C_TEN='#c0392b'

def label(cx, cy, text, color='#444', fs=FS-0.4, ha='center', weight='normal', style='normal'):
    ax.text(cx, cy, text, ha=ha, va='center', fontsize=fs, color=color, fontweight=weight, style=style)

label(W/2, Ht-7, 'Where inference computation and data movement actually live',
      '#1a1a1a', FS+1.0, weight='bold')

# column boundaries
colA_cx = 80      # hierarchy ladder
colB_x  = 168     # what-runs-here (left-aligned)
colC_x  = 372     # gradient

levels = [
    ('registers', 'fastest · smallest', C_ONCHIP),
    ('tensor\ncores / ALU', 'arithmetic units', C_ONCHIP),
    ('shared mem\n(SRAM)', 'on-chip · close', C_ONCHIP),
    ('L2 cache', 'on-die', C_ONCHIP),
    ('HBM (GPU\nmemory)', 'large · slower', C_MEM),
    ('GPU\ninterconnect', 'host / multi-GPU', C_NET),
    ('other GPUs\n/ remote', 'farthest', C_NET),
]
ladder_w = 150; h = 46; gap = 6
top = Ht-45
ys=[]; y=top
for name, role, c in levels:
    ax.add_patch(FancyBboxPatch((colA_cx-ladder_w/2, y-h/2), ladder_w, h,
                  boxstyle='round,pad=0.02,rounding_size=1.2', fc=c,
                  ec='#16295c' if c in (C_ONCHIP,C_NET) else '#8a3a12', lw=1.3, clip_on=False))
    nl = name.count('\n') + 1      # 1 or 2 name lines
    if nl == 2:
        # two-line name centered in upper 60% of box; role in lower part
        label(colA_cx, y+h*0.24, name, '#ffffff', FS, weight='bold', style='normal')
        label(colA_cx, y-h*0.28, role, '#eaeaea', FS-0.9)
    else:
        label(colA_cx, y+h*0.22, name, '#ffffff', FS, weight='bold')
        label(colA_cx, y-h*0.26, role, '#eaeaea', FS-0.9)
    ys.append((y,c)); y -= (h+gap)
for i in range(len(ys)-1):
    ax.annotate('', xy=(colA_cx, ys[i+1][0]+h/2), xytext=(colA_cx, ys[i][0]-h/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.0, color='#555', shrinkA=0, shrinkB=0))

# column B: what runs here, at each level
ops = [
    'tile values in flight',
    'matrix multiply',
    'attention tiling / fusion',
    'recent tiles',
    'model weights + KV cache',
    'TP/PP communication',
    'P/D KV transfer',
]
label(colB_x, top+8, 'what runs here →', '#333', FS-0.7, ha='left', weight='bold')
yy=top
for t in ops:
    label(colB_x, yy, t, '#333', FS-0.8, ha='left')
    yy -= (h+gap)

# column C: gradient
label(colC_x+20, top+8, 'speed ↔ capacity', '#333', FS-0.7, ha='left', weight='bold')
# vertical gradient bar
gx=colC_x; gy0=ys[-1][0]; gy1=top
label(colC_x+14, gy1-4, 'small · fast · close', '#666', FS-0.8, ha='center')
label(colC_x+14, gy0+2, 'large · slow · far', '#666', FS-0.8, ha='center')
ax.annotate('', xy=(colC_x+14, gy0), xytext=(colC_x+14, gy1),
            arrowprops=dict(arrowstyle='<|-|>', lw=1.6, color=C_TEN, shrinkA=0, shrinkB=0))
label(colC_x+34, (gy0+gy1)/2, 'capacity grows, speed drops,\ndistance grows', C_TEN, FS-1.0, ha='left', weight='bold')

# footnote
label(W/2, 14, 'not every component shown — the gradient makes compute, bandwidth,\ncapacity and interconnect distinct constraints', '#666', FS-0.9)

plt.tight_layout(pad=0.2)
plt.savefig('design/manuscript/chapter-08/figures/fig-08-0802.png', dpi=200)
plt.close()
print('wrote fig-08-0802')
