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
# Encoding: a HORIZONTAL per-model comparison grid. One row per REPORTED model,
# each element in its own x cell so nothing shares coordinates:
#   reported model | its own baseline | KV/token 100%->~X% | FLOP/token 100%->~Y%
# The separate 'own baseline' column makes explicit there is no shared scale.
#
# Loop-2 fixes carried here (the .md caption is corrected separately):
#   * Row scheme: the figure shows DeepSeek V4's two variants as two rows (one
#     family) and has no rows for Kimi K3 / Qwen3.8-Flash-Next, so "one row per
#     model family" was false.  The figure now states its own scheme in-figure:
#     one row per reported model, with the two families that publish no
#     predecessor-relative baseline named as having no row.
#   * Caption gap: the old 7.4in canvas carried ~101pt of blank BELOW the last
#     footnote -- that blank is the ~1.5in white band between the figure body
#     and its caption.  The canvas is now sized to the content plus a small PAD.

BOLD = FontProperties(weight='bold')

rows = [
    ("DeepSeek V4-Flash", "vs V3.2",        "reported 2026-06",  7,  10, "#c0392b"),
    ("DeepSeek V4-Pro",   "vs V3.2",        "reported 2026-06", 10,  27, "#3a6ea5"),
    ("GLM-5.3-Flash",     "vs GLM-5.3", "reported 2026-08", 23, 33, "#6f9e5f"),
]

W = 6.1 * 72
FS_H, FS_F, FS_C, FS_R = 10.0, 9.6, 9.0, 8.8

# ---- vertical layout: every y is an offset from the title baseline T ----
# (data coords, y up).  Canvas height = content span + PAD top and bottom.
PAD = 8.0
TOP_OFF = 7.8      # ink reaches this far ABOVE T (title ascender)
BOT_OFF = 399.0    # ink reaches this far BELOW T (last footnote descender)
H = PAD + TOP_OFF + BOT_OFF + PAD      # 422.8pt = 5.87in (was 7.4in)
T = H - PAD - TOP_OFF

fig, ax = plt.subplots(figsize=(W/72, H/72))
fig._hermes_print_sized = True
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

# ---- explicit column x-centres (data coords) ----
c_name = 92        # reported model (left-anchored from ~12)
c_base = 202       # own baseline
c_kv   = 284       # KV/token "100% -> ~X%" cluster centre
c_flop = 382       # FLOP/token cluster centre
h_kv   = 36        # half span of the 100%/arrow/~X% cluster

pitch = 60

# ---- title / warning ----
ax.text(W/2, T, 'Vendor-reported ratios: % remaining', fontsize=FS_H+1.6,
        fontweight='bold', ha='center', va='center', color='#1a1a1a')
ax.text(W/2, T - 16, 'vs each model\'s own predecessor',
        fontsize=FS_H-1.8, ha='center', va='center', color='#333')
ax.text(W/2, T - 44,
        'NOT A CROSS-MODEL PERFORMANCE RANKING',
        fontsize=FS_R-0.2, ha='center', va='center', color='#c0392b', fontweight='bold')
ax.text(W/2, T - 62,
        "Each figure is relative to that model's OWN stated baseline — no shared scale",
        fontsize=FS_R-0.6, ha='center', va='center', color='#c0392b')

# ---- row-scheme note (Loop-2): the grid is one row per REPORTED model ----
ax.text(W/2, T - 84,
        "One row per reported model — DeepSeek V4's two variants listed separately.",
        fontsize=FS_R-0.6, ha='center', va='center', color='#333')
ax.text(W/2, T - 102,
        'No row for Kimi K3 / Qwen3.8-Flash-Next: no predecessor-relative baseline reported.',
        fontsize=FS_R-0.6, ha='center', va='center', color='#333')

# ---- column headers ----
hy = T - 126
ax.text(c_name, hy, 'reported model', fontsize=FS_H, fontweight='bold', ha='center', va='center', color='#333')
ax.text(c_base, hy, 'own baseline', fontsize=FS_H, fontweight='bold', ha='center', va='center', color='#333')
ax.text(c_kv,   hy, 'KV cache*',   fontsize=FS_H, fontweight='bold', ha='center', va='center', color='#333')
ax.text(c_flop, hy, 'Compute*', fontsize=FS_H, fontweight='bold', ha='center', va='center', color='#333')

sep_y = hy - 13
ax.plot([12, W-12], [sep_y, sep_y], color='#999', lw=1.0)

# ---- one row per reported model ----
row0 = sep_y - 20
for r, (name, base, date, kv, flop, col) in enumerate(rows):
    ry = row0 - r * pitch
    ax.text(12, ry, name, fontsize=FS_F, fontweight='bold', ha='left', va='center', color=col)
    ax.text(c_base, ry, base, fontsize=FS_C, fontstyle='italic', ha='center', va='center', color='#555')
    ax.text(c_base, ry - 13, date, fontsize=8.0, ha='center', va='center', color='#888')
    for (cc, pct) in ((c_kv, kv), (c_flop, flop)):
        ax.text(cc - h_kv*0.62, ry, '100%', fontsize=FS_R+0.3, fontweight='bold',
                ha='center', va='center', color='#555')
        ax.annotate('', xy=(cc + h_kv*0.18, ry), xytext=(cc - h_kv*0.20, ry),
                    arrowprops=dict(arrowstyle='-|>', lw=2.2, color=col, shrinkA=0, shrinkB=0))
        ax.text(cc + h_kv*0.58, ry, '~%d%%' % pct, fontsize=FS_R+1.0, fontweight='bold',
                ha='center', va='center', color=col)

# GLM normalization comes from the August 26 release article, not the February
# GLM-5 parent report. Neither ratio is a whole-model inference/storage measure.
ry_glm = row0 - 2 * pitch
ax.text(c_kv, ry_glm - 14, 'BF16 / layer', fontsize=8.0, ha='center',
        va='center', color='#6f9e5f', style='italic')
ax.text(c_flop, ry_glm - 14, 'attention only', fontsize=8.0, ha='center',
        va='center', color='#6f9e5f', style='italic')
ax.text(c_flop, ry_glm - 26, 'per head / layer', fontsize=8.0, ha='center',
        va='center', color='#6f9e5f', style='italic')

# ---- footnote ----
fy = row0 - len(rows)*pitch - 16
ax.text(W/2, fy,
        "*Metric scopes differ. 7% remaining = 93% reduction.",
        fontsize=FS_R-0.2, ha='center', va='center', color='#555')
ax.text(W/2, fy - 20,
        'Value source: vendor-reported [1P] \u2014 DeepSeek V4: arXiv 2606.19348',
        fontsize=FS_R-0.8, ha='center', va='center', color='#777', fontstyle='italic')
ax.text(W/2, fy - 40,
        'GLM: z.ai/blog/glm-5.3-flash (2026-08-26). Vendor claims, not reproduced.',
        fontsize=FS_R-0.8, ha='center', va='center', color='#777', fontstyle='italic')

plt.savefig('design/manuscript/chapter-27/figures/fig-27-2704.png', dpi=400)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-27/figures/fig-27-2704.pdf', format='pdf')
plt.close()
print('wrote fig-27-2704 (one row per reported model; own-baseline column)')