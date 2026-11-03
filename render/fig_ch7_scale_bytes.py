#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ---- fig-07-0708: four-bit payloads + scale bytes (MXFP4 vs NVFP4) ----
# Vector redraw of the hand-drawn raster (design/.../fig-07-0708-*.png, which
# has no generator).  Labels/geometry transcribed 1:1 from the PNG; bar widths
# stay proportional to bytes (16:1 and 8:8:1:1).  Authored at the 6.1in print
# column (1 data unit = 1 inch) so every label lands at >=8.5pt on page.
# Saves ONLY the .pdf: the original hand-drawn .png stays as the raster
# fallback and the fresh .pdf mtime is newer, so copy_figures embeds the vector.

W, H = 6.1, 4.33
INK, STROKE = '#1A1A1A', '#4D4D4D'
PAYLOAD, SCALE = '#D9D9D9', '#707070'
X0, S, BH = 0.18, 0.305, 0.38   # left edge, inches per byte, bar height

fig = plt.figure(figsize=(W, H))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')


def ctext(x, y, s, size=8.5, weight='normal', ha='center'):
    ax.text(x, y, s, ha=ha, va='center', fontsize=size,
            fontweight=weight, color=INK)


def bar(y, cells):
    """cells: list of (bytes, fill, label|None)."""
    x = X0
    for nb, fc, label in cells:
        ax.add_patch(Rectangle((x, y), nb * S, BH, fc=fc, ec=STROKE, lw=1.1))
        if label:
            ctext(x + nb * S / 2, y + BH / 2, label)
        x += nb * S
    ax.add_patch(Rectangle((X0, y), (x - X0), BH, fc='none', ec=STROKE, lw=1.3))
    return x


ctext(W / 2, 4.16, 'Four-bit values, different scale bills', size=11,
      weight='bold')
ctext(W / 2, 3.90, 'Payload and local-scale bar widths are proportional to bytes.',
      size=9)

# MXFP4 row
ctext(X0, 3.52, 'MXFP4: one E8M0 scale per 32 values', size=9.5,
      weight='bold', ha='left')
end1 = bar(2.98, [(16, PAYLOAD, '32 E2M1 values = 16 B'), (1, SCALE, None)])
ax.plot([end1 - S / 2, end1 - S / 2], [2.98, 2.86], color=STROKE, lw=1.1)
ctext(end1 - S / 2, 2.74, '1 B scale')
ctext(X0, 2.48, 'Local: 17 B / 32 = 0.53125 B/value = 4.25 bit/value',
      size=9.5, weight='bold', ha='left')

# NVFP4 row
ctext(X0, 2.10, 'NVFP4 (common 1D): one E4M3 scale per 16 values', size=9.5,
      weight='bold', ha='left')
end2 = bar(1.56, [(8, PAYLOAD, '16 values = 8 B'),
                  (8, PAYLOAD, '16 values = 8 B'),
                  (1, SCALE, None), (1, SCALE, None)])
# grouping bracket under the two 1-B scale cells — an OPEN bracket (an under-brace:
# two short upward ticks joined by a baseline line) so it reads as a grouping mark,
# NOT an empty filled box (review: the closed white rectangle looked like a stray/leftover
# element, inconsistent with the MXFP4 row's single tick line).
_gx = end2 - S  # centre below the two scale cells
ax.plot([_gx - S, _gx - S], [1.58, 1.48], color=STROKE, lw=1.0)
ax.plot([_gx - S, _gx + S], [1.48, 1.48], color=STROKE, lw=1.0)
ax.plot([_gx + S, _gx + S], [1.48, 1.58], color=STROKE, lw=1.0)
ax.text(_gx, 1.34, '2 B scales', ha='center', va='center')
ctext(X0, 1.02, 'Local: 18 B / 32 = 0.5625 B/value = 4.5 bit/value',
      size=9.5, weight='bold', ha='left')

ctext(W / 2, 0.70, 'NVFP4 global FP32 scale: 4 B per tensor, not per block.',
      size=9.5, weight='bold')
ctext(W / 2, 0.44, 'Byte accounting only; not a physical packing order.')
ctext(W / 2, 0.20, 'No padding, extra copies, headers or high-precision exceptions.')

out = 'design/manuscript/chapter-07/figures/fig-07-0708-block-scale-bytes.pdf'
with matplotlib.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig(out, format='pdf')
print('wrote', out)