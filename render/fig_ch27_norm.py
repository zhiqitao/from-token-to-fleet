import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.font_manager import FontProperties

# ---- fig-27-2704 / Figure A.2: vendor-reported KV/token and FLOP/token reductions
# MAJOR REDESIGN per the publication review. The old before->after cards stacked
# every label in one small box, superimposing name / reference / KV row / 100% / ~X%
# at print size.
#
# New encoding: a HORIZONTAL per-family comparison grid. One row per model family,
# each element in its own x cell so nothing shares coordinates:
#   model family | its own baseline | KV/token 100%->~X% | FLOP/token 100%->~Y%
# The separate 'own baseline' column makes explicit there is no shared scale.

BOLD = FontProperties(weight='bold')

rows = [
    ("DeepSeek V4-Flash", "vs V3.2",       7,  10, "#c0392b"),
    ("DeepSeek V4-Pro",   "vs V3.2",      10,  27, "#3a6ea5"),
    ("GLM-5.3-Flash",     "vs stated ref", 23, 33, "#6f9e5f"),
]

W, H = 6.1 * 72, 5.4 * 72
FS_H, FS_F, FS_C, FS_R = 10.0, 9.6, 9.0, 8.8

fig, ax = plt.subplots(figsize=(W/72, H/72))
fig._hermes_print_sized = True
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

# ---- explicit column x-centres (data coords) ----
c_name = 92        # family name (left-anchored from ~12)
c_base = 202       # own baseline
c_kv   = 284       # KV/token "100% -> ~X%" cluster centre
c_flop = 382       # FLOP/token cluster centre
h_kv   = 36        # half span of the 100%/arrow/~X% cluster

# ---- title / warning ----
ax.text(W/2, H-16, 'Vendor-reported KV / FLOP reduction', fontsize=FS_H+1.6,
        fontweight='bold', ha='center', va='center', color='#1a1a1a')
ax.text(W/2, H-38,
        'Each figure is relative to that model\'s OWN stated baseline — no shared scale',
        fontsize=FS_R-0.4, ha='center', va='center', color='#c0392b', fontweight='bold')

# ---- column headers ----
hy = H - 70
ax.text(c_name, hy, 'model family', fontsize=FS_H, fontweight='bold', ha='center', va='center', color='#333')
ax.text(c_base, hy, 'own baseline', fontsize=FS_H, fontweight='bold', ha='center', va='center', color='#333')
ax.text(c_kv,   hy, 'KV / token',   fontsize=FS_H, fontweight='bold', ha='center', va='center', color='#333')
ax.text(c_flop, hy, 'FLOP / token', fontsize=FS_H, fontweight='bold', ha='center', va='center', color='#333')

sep_y = hy - 13
ax.plot([12, W-12], [sep_y, sep_y], color='#999', lw=1.0)

# ---- one row per family ----
row0 = sep_y - 20
pitch = 34
for r, (name, base, kv, flop, col) in enumerate(rows):
    ry = row0 - r * pitch
    ax.text(12, ry, name, fontsize=FS_F, fontweight='bold', ha='left', va='center', color=col)
    ax.text(c_base, ry, base, fontsize=FS_C, fontstyle='italic', ha='center', va='center', color='#555')
    for (cc, pct) in ((c_kv, kv), (c_flop, flop)):
        ax.text(cc - h_kv*0.62, ry, '100%', fontsize=FS_R+0.3, fontweight='bold',
                ha='center', va='center', color='#555')
        ax.annotate('', xy=(cc + h_kv*0.18, ry), xytext=(cc - h_kv*0.20, ry),
                    arrowprops=dict(arrowstyle='-|>', lw=2.2, color=col, shrinkA=0, shrinkB=0))
        ax.text(cc + h_kv*0.58, ry, '~%d%%' % pct, fontsize=FS_R+1.0, fontweight='bold',
                ha='center', va='center', color=col)

# ---- footnote ----
fy = row0 - len(rows)*pitch - 16
ax.text(W/2, fy,
        'Each reduction is relative to the model\'s OWN stated predecessor — no common denominator.',
        fontsize=FS_R-0.2, ha='center', va='center', color='#555')
ax.text(W/2, fy - 20,
        'Value source: vendor-reported [1P] (arXiv 2606.19348; HF zai-org), not yet independently reprofiled.',
        fontsize=FS_R-0.6, ha='center', va='center', color='#777', fontstyle='italic')

plt.savefig('design/manuscript/chapter-27/figures/fig-27-2704.png', dpi=200)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-27/figures/fig-27-2704.pdf', format='pdf')
plt.close()
print('wrote fig-27-2704 (horizontal per-family grid; own-baseline column)')
