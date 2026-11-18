#!/usr/bin/env python3
"""fig-08-0802: Hardware hierarchy mental model (where inference work happens).

Author at exactly the 6.1in book column width so regen_figs does NOT boost fonts.

Job: give the reader a memorable physical model of where inference compute and
data movement actually occur, and why FLOPS / HBM-bandwidth / HBM-capacity /
interconnect-bandwidth become distinct architectural constraints.  Central
tension: small + very fast + close <-> large + slower + farther.

Three clean columns: [A] the hierarchy ladder (top->bottom), [B] what runs at
each level, [C] the speed<->capacity gradient.  1 data unit == 1 point.

Round-7 fixes:
  FIG-161-01  the compute box ("tensor cores / ALU") is no longer a rung of the
              memory ladder: it is offset into its own group at the left, braced
              apart from the memory hierarchy, so the red capacity/speed gradient
              (which spans registers -> HBM only) no longer appears to cover it.
  FIG-161-02  every in-box label now sits on a semi-opaque dark pill, so the
              white text holds contrast over the orange cross-hatch / green dot
              fills at print size and in grayscale.
  F81-05      each column-B label is tied to its left-hand box by a faint row
              rule, so the pairing no longer rests on vertical alignment alone.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
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
fig._hermes_print_sized = True   # regen must not re-boost/reflow (already 6.1in column)
XL, XR = -18, 455
ax.set_xlim(XL, XR); ax.set_ylim(0, Ht); ax.axis('off')
CX = (XL + XR) / 2.0

C_ONCHIP='#27408b'; C_MEM='#e67e22'; C_NET='#2e9e63'; C_TEN='#c0392b'
# Loop-4 FIG-8.1-02: each semantic class also gets a fill PATTERN, not just a hue,
# so the compute / memory / interconnect grouping survives grayscale printing.
HATCH = {C_ONCHIP: '///', C_MEM: 'xxx', C_NET: '...'}
matplotlib.rcParams['hatch.linewidth'] = 0.8
# horizontal scale, measured off the rendered ladder fill: 658px@400dpi = 118.4pt / 150 units
PT_PER_UNIT = 0.79

# FIG-161-02: white type over an x-hatch or dot fill loses contrast at print size,
# so every in-box label carries a semi-opaque dark pill (the fig-7.7 treatment).
PILL = dict(boxstyle='round,pad=0.16', fc=(0, 0, 0, 0.34), ec='none')

def label(cx, cy, text, color='#444', fs=FS-0.4, ha='center', weight='normal',
          style='normal', pill=False):
    bbox = PILL if pill else None
    ax.text(cx, cy, text, ha=ha, va='center', fontsize=fs, color=color,
            fontweight=weight, style=style, bbox=bbox, zorder=4)

label(CX, Ht-4, 'Where inference computation and\ndata movement actually live',
      '#1a1a1a', FS+0.6, weight='bold')
# column boundaries
colA_cx = 80      # hierarchy ladder
colB_x  = 172     # what-runs-here (left-aligned)
colC_x  = 372     # gradient

# FIG-161-01: the compute box is NOT a ladder rung — the ladder lists memory levels
# only (registers -> HBM) plus the interconnect group.  Compute is drawn separately
# at the left, braced off the ladder.
levels = [
    ('registers', 'fastest · smallest', C_MEM, 'memory'),
    ('shared mem\n(SRAM)', 'on-chip · close', C_MEM, 'memory'),
    ('L2 cache', 'on-die', C_MEM, 'memory'),
    ('HBM (GPU\nmemory)', 'large · slower', C_MEM, 'memory'),
    # Loop-4 FIG-8.1-1: name on ONE line so the wrapped role below fits the box.
    ('GPU interconnect', 'GPU↔GPU and\nhost links', C_NET, 'net'),
    ('other GPUs\n/ remote', 'farthest', C_NET, 'net'),
]
ladder_w = 150; h = 42; gap = 6
top = 325.0
ys=[]; y=top
for name, role, c, grp in levels:
    ax.add_patch(FancyBboxPatch((colA_cx-ladder_w/2, y-h/2), ladder_w, h,
                  boxstyle='round,pad=0.02,rounding_size=1.2', fc=c,
                  ec='#16295c' if c in (C_ONCHIP,C_NET) else '#8a3a12', lw=1.3,
                  hatch=HATCH.get(c), clip_on=False, zorder=2))
    nl = name.count('\n') + 1      # 1 or 2 name lines
    nrole = role.count('\n') + 1
    if nl == 2:
        label(colA_cx, y+h*0.20, name, '#ffffff', FS-1.4, weight='bold', pill=True)
        label(colA_cx, y-h*0.28, role, '#ffffff', FS-1.1, pill=True)
    elif nrole == 2:
        label(colA_cx, y+h*0.27, name, '#ffffff', FS-1.2, weight='bold', pill=True)
        label(colA_cx, y-h*0.26, role, '#ffffff', FS-1.0, pill=True)
    else:
        label(colA_cx, y+h*0.22, name, '#ffffff', FS-1.0, weight='bold', pill=True)
        label(colA_cx, y-h*0.24, role, '#ffffff', FS-1.1, pill=True)
    ys.append((y, c, grp)); y -= (h+gap)
for i in range(len(ys)-1):
    ax.annotate('', xy=(colA_cx, ys[i+1][0]+h/2), xytext=(colA_cx, ys[i][0]-h/2),
                arrowprops=dict(arrowstyle='-|>', lw=1.0, color='#555', shrinkA=0, shrinkB=0))

# ---- group braces on the left: memory ladder vs interconnect (FIG-161-01) ----
def brace(y_hi, y_lo, text, color='#8a3a12'):
    xb = colA_cx - ladder_w/2 - 10
    ax.plot([xb+4, xb, xb, xb+4], [y_hi, y_hi, y_lo, y_lo], color=color, lw=1.0,
            clip_on=False, zorder=3)
    ax.text(xb-4, (y_hi+y_lo)/2, text, rotation=90, ha='center', va='center',
            fontsize=FS-2.2, color=color, fontweight='bold')

y_mem_hi = ys[0][0] + h/2; y_mem_lo = ys[3][0] - h/2
y_net_hi = ys[4][0] + h/2; y_net_lo = ys[5][0] - h/2
brace(y_mem_hi, y_mem_lo, 'memory hierarchy')
brace(y_net_hi, y_net_lo, 'interconnect', '#1d6b45')

# ---- compute: its own group, offset OUT of the ladder (FIG-161-01) ----
cw, chh = 114, 40
cx = 44                      # left of the ladder's centre line: the box hangs out of the column
cy = top + h/2 + 12 + chh/2  # above the ladder, separated by a 12-pt gap
ax.add_patch(FancyBboxPatch((cx-cw/2, cy-chh/2), cw, chh,
              boxstyle='round,pad=0.02,rounding_size=1.2', fc=C_ONCHIP,
              ec='#16295c', lw=1.3, hatch=HATCH[C_ONCHIP], clip_on=False, zorder=2))
label(cx, cy+7, 'tensor cores / ALU', '#ffffff', FS-1.3, weight='bold', pill=True)
label(cx, cy-9, 'matrix multiply', '#ffffff', FS-1.6, pill=True)
ax.plot([cx+cw/2+6, cx+cw/2+14, cx+cw/2+14, cx+cw/2+6], [cy+chh/2, cy+chh/2, cy-chh/2, cy-chh/2],
        color='#16295c', lw=1.0, clip_on=False, zorder=3)
ax.text(cx+cw/2+16, cy+6, 'compute (separate group)', ha='left', va='center',
        fontsize=FS-3.0, color='#16295c', fontweight='bold')

# column B: what runs here, at each level (memory / interconnect rows only --
# 'matrix multiply' now lives inside the compute group, not on a ladder rung)
ops = [
    'tile values in flight',
    'attention tiling',
    'recent tiles',
    'weights + KV cache',
    # Loop-5 F17(a): TP/PP are expanded only 18-21 pages later, so spell them out
    # in-figure at first use (two lines keep the column-B width unchanged).
    'TP/PP\ncommunication',
    'P/D KV transfer',
]
label(colB_x, top+h/2+10, 'what runs here →', '#333', FS-0.7, ha='left', weight='bold')
yy=top
for t in ops:
    # F81-05: a faint row rule ties each label to its box, so the pairing does not
    # depend on the reader scanning horizontally across a gap.
    ax.plot([colA_cx+ladder_w/2+3, 332], [yy-8.5, yy-8.5], color='#999999', lw=0.6,
            alpha=0.45, zorder=1)
    label(colB_x, yy, t, '#333', FS-0.8, ha='left')
    yy -= (h+gap)

# column C: gradient (far right)
gy0=ys[-1][0]; gy1=top
gx=colC_x+52
# Loop-5 F17(b): the old two-line form broke as "small · fast" / "· close", leaving an
# orphaned leading middle-dot on line 2.  Non-breaking spaces bind each "· word" so the
# label stays ONE line with no dangling dot; one size step down keeps it inside the
# right-hand column (measured: 10pt line spans x 336..452 data, axes right edge 453).
label(gx, gy1-2, 'small\u00a0·\u00a0fast\u00a0·\u00a0close', '#555', FS-1.5, ha='center')
# Round-5 F-15: the bottom label is split — 'large · slow' sits level with HBM
# (the memory-hierarchy end of the arrow), 'far' level with the interconnect rows.
gy_hbm = ys[3][0]
label(gx, gy_hbm+2, 'large\u00a0·\u00a0slow', '#555', FS-1.5, ha='center')
label(gx, gy0+2, 'far', '#555', FS-1.5, ha='center')
# Round-5 FIG-8.1-01: the gradient arrow spans ONLY the memory hierarchy
# (registers -> HBM); compute and interconnect are separate groups, not levels
# of the same ladder, so distance is a property of the interconnect rows alone.
ax.annotate('', xy=(gx, gy_hbm), xytext=(gx, gy1),
            arrowprops=dict(arrowstyle='<|-|>', lw=1.6, color=C_TEN, shrinkA=14, shrinkB=14))
label(gx-42, (gy_hbm+gy1)/2, 'capacity grows\nspeed drops\ndistance grows', C_TEN, FS-1.0, ha='center', weight='bold')

# Loop-4 FIG-8.1-02: compact three-swatch key (compute / memory / interconnect),
# each swatch carrying the same hue + hatch pattern as its group.
KEY_Y = 34
kx = colB_x
for c, kname in ((C_ONCHIP, 'compute'), (C_MEM, 'memory'), (C_NET, 'interconnect')):
    ax.add_patch(Rectangle((kx, KEY_Y-5.5), 11, 11, fc=c,
                ec='#16295c' if c in (C_ONCHIP, C_NET) else '#8a3a12',
                lw=1.0, hatch=HATCH[c], clip_on=False))
    label(kx+15, KEY_Y, kname, '#333', FS-1.6, ha='left')
    kx += 15 + rw(kname, FS-1.6) * 0.72 / PT_PER_UNIT + 20

# footnote
label(CX, 10, 'not every component shown — the gradient makes compute, bandwidth,\ncapacity and interconnect distinct constraints', '#555', FS-0.6)

plt.tight_layout(pad=0.2)
plt.savefig('design/manuscript/chapter-08/figures/fig-08-0802.png', dpi=400)
plt.close()
print('wrote fig-08-0802')
