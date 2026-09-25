import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

# =====================================================================
# fig-12-1201 "Candidate architecture synthesis"
# ---------------------------------------------------------------------
# REDESIGN (publication review): the prior version was a "document inside
# a diagram" — Stage 4 stacked three boxes each carrying 2-3 lines of
# embedded prose, so the decision chain was buried under text.  New version
# keeps the clean top-down chain (requirements -> constraints -> generate ->
# test -> outcome) but renders the TEST stage as a compact GATE TABLE — one
# row per candidate, one column per gate — so the trade-offs read at a glance.
# Each stage box is tall enough for its own title line + detail line (measured
# so the two never overlap); per-cell gate text is a short token, the arithmetic
# and cross-references live in the caption and §12.4.
# =====================================================================
BOLD = FontProperties(weight='bold')
fig, ax = plt.subplots(figsize=(6.1, 5.6))
fig._hermes_print_sized = True
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')


def box(x, y, w, h, fc, ec, lw=1.4, r=0.03):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=2))


def arrow(y0, y1, color='#444'):
    ax.add_patch(FancyArrowPatch((CX, y0), (CX, y1), arrowstyle='-|>', mutation_scale=13,
                                 lw=1.6, color=color, zorder=1))


def title(x, y, s, color='#333'):
    ax.text(x, y, s, fontsize=8.8, color=color, fontweight='bold', ha='center', va='center', zorder=3)


def detail(x, y, s, size=7.2, color='#555', weight='normal'):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha='center', va='center', zorder=3)


X0, W = 0.05, 0.90
CX = X0 + W / 2

# ---- Stage 1 REQUIREMENTS (tALL enough for title + detail) ----
box(X0, 0.870, W, 0.100, '#eaf1fb', '#3a6ea5')
title(CX, 0.940, '① REQUIREMENTS  —  canonical enterprise-Q&A RAG', '#27408b')
detail(CX, 0.898, '~2,000 users · ~10/40 rps · 9.2K-in / 300-out · quality ~70B')
arrow(0.870, 0.832)

# ---- Stage 2 CONSTRAINTS ----
box(X0, 0.720, W, 0.100, '#fdf3e0', '#d68910')
title(CX, 0.790, '② CONSTRAINTS  —  three hard gates', '#935116')
detail(CX, 0.748, 'MEMORY  ·  LATENCY  ·  ECONOMICS')
arrow(0.720, 0.682)

# ---- Stage 3 GENERATE ----
box(X0, 0.570, W, 0.100, '#e7f5ec', '#1e8449')
title(CX, 0.640, '③ GENERATE CANDIDATES', '#145a32')
detail(CX, 0.598, '(a) 8×H100 + prefix cache  ·  (b) P/D 2-pool  ·  (c) KV-quant 7B')
arrow(0.570, 0.532)

# ---- Stage 4 TEST — compact gate table ----
box(X0, 0.300, W, 0.220, '#f4f4f4', '#555555')
# gate columns (x-left, width) sized from measured text
col = [
    ('CANDIDATE', X0+0.030, 0.300),
    ('MEM',       X0+0.360, 0.075),
    ('LAT',       X0+0.455, 0.075),
    ('ECON',      X0+0.555, 0.090),
    ('VERDICT',   X0+0.680, 0.180),
]
thdr = 0.500
for h, cx, cw in col:
    ax.text(cx, thdr, h, fontsize=7.4, fontweight='bold', color='#333', ha='left', va='center', zorder=3)
ax.plot([X0+0.025, X0+W-0.02], [thdr-0.018, thdr-0.018], color='#999', lw=0.7, zorder=3)

cands = [
    ('(a) 8×H100 + prefix cache', '✓', '✓', '✓', '✗ capacity — ~5 hosts', '#3a6ea5'),
    ('(b) P/D 2-pool',            '✓', '✓', '~2×', '✗ at 1 prefill host → scales to ~5', '#e67e22'),
    ('(c) KV-quant 7B',           '✓', 'cheap', '✓', '✗ quality — excluded', '#c0392b'),
]
row0 = 0.455
rh = 0.055
for i, (name, mem, lat, eco, verdict, edge) in enumerate(cands):
    ry = row0 - i * (rh + 0.012)
    ax.plot([X0+0.025, X0+W-0.02], [ry, ry], color='#e3e3e3', lw=0.6, zorder=3)
    ax.text(col[0][1], ry, name, fontsize=7.4, fontweight='bold', color=edge, ha='left', va='center', zorder=3)
    ax.text(col[1][1], ry, mem,   fontsize=7.4, color='#3a6a4a', ha='left', va='center', zorder=3)
    ax.text(col[2][1], ry, lat,   fontsize=7.4, color='#444',    ha='left', va='center', zorder=3)
    ax.text(col[3][1], ry, eco,   fontsize=7.4, color='#8a6d1a', ha='left', va='center', zorder=3)
    ax.text(col[4][1], ry, verdict, fontsize=7.3, color=edge, fontweight='bold', ha='left', va='center', zorder=3)

arrow(0.300, 0.262)

# ---- Stage 5 OUTCOME ----
sx = X0 + 0.02
sw = (W - 0.04) * 0.58
box(sx, 0.100, sw, 0.140, '#e7f5ec', '#1e8449')
title(sx + sw/2, 0.205, '⑤ OUTCOME — SURVIVORS', '#145a32')
detail(sx + sw/2, 0.160, '(a) latency baseline   (b) prefill pool scales to ~5')
bx = sx + sw + 0.03
bw = W - 0.04 - sw - 0.03
box(bx, 0.100, bw, 0.140, '#fdecea', '#c0392b')
title(bx + bw/2, 0.205, '✗ REJECTED', '#7b241c')
detail(bx + bw/2, 0.160, '(c) fails quality gate')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-12/figures/fig-12-1201.png', dpi=150)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-12/figures/fig-12-1201.pdf', format='pdf')
plt.close()
print('wrote fig-12-1201 (decision chain with gate table)')
