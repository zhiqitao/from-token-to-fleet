#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-07-0707: quantization choices vs execution guarantees ----
# Vector redraw of the hand-drawn raster (design/.../fig-07-0707-*.png, which
# has no generator).  Content/labels/structure transcribed 1:1 from the PNG.
# Authored at the 6.1in print column (1 data unit = 1 inch), so every label
# lands at its authored >=8.5pt on page.  Saves ONLY the .pdf: the original
# hand-drawn .png stays as the raster fallback and the fresh .pdf mtime is
# newer, so copy_figures embeds the vector.

W, H = 6.1, 5.83
INK, STROKE = '#1A1A1A', '#3A3A3A'
LEAF, CONTAINER = '#E9E9E9', '#F2F2F2'

fig = plt.figure(figsize=(W, H))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')


def rbox(x, y, w, h, fc, ec, lw, r=0.07):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle=f'round,pad=0,rounding_size={r}',
                 fc=fc, ec=ec, lw=lw, mutation_aspect=1))


def ctext(x, y, s, size=8.5, weight='normal'):
    ax.text(x, y, s, ha='center', va='center', fontsize=size,
            fontweight=weight, color=INK)


def down(x, y0, y1, lw=1.4):
    ax.add_patch(FancyArrowPatch((x, y0), (x, y1), arrowstyle='-|>',
                 mutation_scale=11, lw=lw, color=STROKE, shrinkA=0, shrinkB=0))


ctext(W / 2, 5.65, 'Quantization choices are not execution guarantees',
      size=11, weight='bold')

# row 1: two independent questions
rbox(0.18, 4.72, 2.82, 0.70, LEAF, STROKE, 1.4)
rbox(3.10, 4.72, 2.82, 0.70, LEAF, STROKE, 1.4)
ctext(1.59, 5.24, 'Error-control method', size=9.5, weight='bold')
ctext(1.59, 5.02, 'AWQ / GPTQ')
ctext(1.59, 4.84, 'Calibration guides error reduction')
ctext(4.51, 5.24, 'Numerical representation', size=9.5, weight='bold')
ctext(4.51, 5.02, 'INT4 + scheme / MXFP4 / NVFP4')
ctext(4.51, 4.84, 'Scale type and grouping are explicit')

# row 2: container wrapping the packed tensor
rbox(0.18, 3.02, 5.74, 1.42, CONTAINER, STROKE, 1.4)
rbox(0.45, 3.40, 5.20, 0.74, LEAF, STROKE, 1.2, r=0.05)
ctext(W / 2, 3.96, 'Packed tensor: values + scales (+ zero points, if used)',
      size=9.5, weight='bold')
ctext(W / 2, 3.62, 'Layout, padding and alignment are implementation-specific')
ctext(W / 2, 3.20, 'Container wraps tensors + metadata: e.g., GGUF / safetensors')
# tips overlap the nested-box top edge (4.14) so no white gap shows
down(1.30, 4.72, 4.115)
down(4.80, 4.72, 4.115)

# container -> runtime layout
down(W / 2, 3.02, 2.505)
ax.text(3.16, 2.78, 'load / repack', ha='left', va='center', fontsize=8.5,
        color=INK)

rbox(0.75, 2.00, 4.60, 0.52, LEAF, STROKE, 1.4)
ctext(W / 2, 2.34, 'Runtime tensors in the kernel-required layout',
      size=9.5, weight='bold')
ctext(W / 2, 2.12, 'Repacking does not imply numerical conversion.')

# dispatch branch: stem -> bar -> three drops
down(W / 2, 2.00, 1.605)
ax.text(3.16, 1.82, 'compatible dispatch', ha='left', va='center',
        fontsize=8.5, color=INK)
centers = (1.053, 3.05, 5.047)
ax.plot([centers[0], centers[-1]], [1.62, 1.62], color=STROKE, lw=1.4,
        solid_capstyle='butt')
for x in centers:
    down(x, 1.62, 1.325)

# row 4: the three execution paths
bw = 1.7467
for x0, head, l1, l2 in (
        (0.18, 'Native FP4 math', 'Compatible low-bit', 'operand arithmetic'),
        (2.1767, 'Fused dequant', 'Weight dequantization', 'e.g., W4A16 GEMM'),
        (4.1733, 'Reconstruct', 'Higher-precision', 'weights + GEMM')):
    rbox(x0, 0.66, bw, 0.68, LEAF, STROKE, 1.4)
    cx = x0 + bw / 2
    ctext(cx, 1.17, head, size=9.5, weight='bold')
    ctext(cx, 0.97, l1)
    ctext(cx, 0.80, l2)

ctext(W / 2, 0.40, 'Only supported combinations can load and execute.')
ctext(W / 2, 0.18, 'No compatible kernel: reject; fallback is not guaranteed.')

out = 'design/manuscript/chapter-07/figures/fig-07-0707-quantization-layers.pdf'
with matplotlib.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig(out, format='pdf')
print('wrote', out)