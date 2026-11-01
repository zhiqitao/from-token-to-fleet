#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-03-0304: Wan2.2 A14B active != resident parameters ----
# Vector redraw of the hand-drawn raster (design/.../fig-03-0304-*.png, which
# has no generator).  Content/labels/colors transcribed 1:1 from the PNG.
# Authored at the 6.1in print column, 1pt == 1pt on page (>=8pt labels).
# Saves ONLY the .pdf: the original hand-drawn .png stays as the raster
# fallback, and the fresh .pdf mtime is newer so copy_figures picks the vector.

W, H = 6.1, 3.95
NAVY, PEACH, ORANGE = '#1F3D8C', '#E6ECF7', '#E07B2A'
PEACH_FILL, INK, BLACK = '#FCE9D6', '#1A1A1A', '#000000'

fig = plt.figure(figsize=(W, H))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')


def rbox(x, y, w, h, fc, ec, lw, r=0.07):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle=f'round,pad=0,rounding_size={r}',
                 fc=fc, ec=ec, lw=lw, mutation_aspect=1))


def ctext(x, y, s, size=8.5, weight='normal', color=INK):
    ax.text(x, y, s, ha='center', va='center', fontsize=size,
            fontweight=weight, color=color)


# title
ctext(W / 2, 3.80, 'Wan2.2 A14B: active \u2260 resident parameters',
      size=11, weight='bold', color=INK)

# blue residency container + two white checkpoints
rbox(0.18, 2.62, 5.74, 0.98, PEACH, NAVY, 1.6)
ctext(W / 2, 3.42, 'Both-on-GPU assumption: about 27B resident parameters',
      size=9.5, weight='bold', color=NAVY)
rbox(0.42, 2.74, 2.43, 0.46, 'white', NAVY, 1.4, r=0.05)
rbox(3.25, 2.74, 2.43, 0.46, 'white', NAVY, 1.4, r=0.05)
ctext(1.635, 2.97, 'High-noise expert checkpoint', size=9, color=NAVY)
ctext(4.465, 2.97, 'Low-noise expert checkpoint', size=9, color=NAVY)

# dashed schedule arrows (checkpoint -> stage); tips overlap the stage-box top
# edge by ~0.015in so no white gap shows between arrowhead and border.
for x in (1.635, 4.465):
    ax.add_patch(FancyArrowPatch((x, 2.74), (x, 2.085),
                 arrowstyle='-|>', mutation_scale=11, lw=1.4,
                 linestyle=(0, (4, 3)), color=NAVY, shrinkA=0, shrinkB=0))
ctext(W / 2, 2.48, 'Denoising schedule progresses \u2192', size=8.5)
ctext(W / 2, 2.28, 'Not two experts within one forward', size=8.5)

# orange stage boxes + the single solid schedule arrow
rbox(0.42, 1.42, 2.43, 0.68, PEACH_FILL, ORANGE, 1.6)
rbox(3.25, 1.42, 2.43, 0.68, PEACH_FILL, ORANGE, 1.6)
ctext(1.635, 1.90, 'High-noise stage', size=9.5, weight='bold')
ctext(1.635, 1.63, 'Only high-noise expert runs', size=8.5)
ctext(4.465, 1.90, 'Low-noise stage', size=9.5, weight='bold')
ctext(4.465, 1.63, 'Only low-noise expert runs', size=8.5)
ax.add_patch(FancyArrowPatch((2.86, 1.76), (3.26, 1.76),
             arrowstyle='-|>', mutation_scale=11, lw=1.6, color=BLACK,
             shrinkA=0, shrinkB=0))

# footer
for y, s in ((1.12, 'About 14B active per forward evaluation.'),
             (0.87, 'If both experts stay on GPU: about 27B resident.'),
             (0.62, 'Schematic: stage widths do not encode step counts.'),
             (0.37, 'Offload lowers GPU residency but adds weight transfers.')):
    ctext(W / 2, y, s, size=8.5)

out = 'design/manuscript/chapter-03/figures/fig-03-0304-wan-noise-experts.pdf'
with matplotlib.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig(out, format='pdf')
print('wrote', out)