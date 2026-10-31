import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# =====================================================================
# fig-12-1201 "Candidate architecture synthesis"
# ---------------------------------------------------------------------
# REDESIGN (reviewer, 2026-09-27): the prior version nested a per-gate table
# (MEM / LAT / ECON / verdict) inside stage 4 and packed every stage with a
# subtitle line, so the decision chain dissolved into text.  New version is four
# LARGE horizontal stages with a visible row divider between them and BIG stage
# labels; the fine-grained per-gate verdicts and the arithmetic now live in the
# caption and Table 12-1, not in the diagram.
# =====================================================================
fig, ax = plt.subplots(figsize=(6.1, 5.0))
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

X0, W = 0.04, 0.92
CX = X0 + W / 2

def box(x, y, w, h, fc, ec, lw=1.6, hatch=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.02',
                                fc=fc, ec=ec, lw=lw, zorder=2,
                                hatch=hatch if hatch else None))

def divider(y):
    ax.plot([X0, X0 + W], [y, y], color='#bbbbbb', lw=1.1, zorder=3)

def stagelabel(x, y, s, color, size=11.5):
    ax.text(x, y, s, ha='center', va='center', fontsize=size,
            color=color, fontweight='bold', zorder=3)

# ---- overall title ----
ax.text(CX, 0.982, 'Candidate architecture synthesis', fontsize=8.8,
        fontweight='bold', ha='center', color='#333')

def downarrow(y_top, y_bot):
    """vertical connector arrow between two stages (the reasoning chain)."""
    ax.annotate('', xy=(CX, y_bot), xytext=(CX, y_top),
                arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#555'))

# ---- Stage 1 REQUIREMENTS ----
box(X0, 0.790, W, 0.150, '#eaf1fb', '#3a6ea5')
stagelabel(CX, 0.865, '\u2460  REQUIREMENTS', '#27408b')
divider(0.778)
downarrow(0.778, 0.735)   # R27 P2: extend the tip into the box so it touches

# ---- Stage 2 CONSTRAINTS ----
box(X0, 0.600, W, 0.150, '#fdf3e0', '#d68910')
stagelabel(CX, 0.675, '\u2461  CONSTRAINTS', '#935116')
divider(0.588)
downarrow(0.588, 0.545)   # R27 P2: extend the tip into the box so it touches

# ---- Stage 3 CANDIDATES (taller: title + the candidate line) ----
box(X0, 0.335, W, 0.225, '#e7f5ec', '#1e8449')
stagelabel(CX, 0.510, '\u2462  CANDIDATES', '#145a32')
ax.text(CX, 0.435, '(a) 8\u00d7H100 + prefix cache \u00b7 (b) P/D 2-pool \u00b7 (c) KV-quant 7B',
        ha='center', va='center', fontsize=8.2, color='#1e8449', zorder=3)
divider(0.323)

# ---- Stage 4 OUTCOME — SURVIVORS vs REJECTED (one stage, two halves) ----
# (a) and (b) both clear the capacity gate (each needs a ~5-host prefill pool,
# so (a) is not disqualified); (c) is gated, not a finalist — pending the Ch 14
# quality gate.
sw = (W - 0.04) * 0.58
sx = X0
box(sx, 0.090, sw, 0.200, '#e7f5ec', '#1e8449')
stagelabel(sx + sw / 2, 0.245, '\u2463  OUTCOME', '#145a32')
ax.text(sx + sw / 2, 0.165, 'SURVIVORS  (a) \u00b7 (b)', ha='center', va='center',
        fontsize=8.4, color='#145a32', fontweight='bold', zorder=3)
ax.text(sx + sw / 2, 0.125, 'each needs a ~5-host prefill pool', ha='center', va='center',
        fontsize=8.0, color='#145a32', zorder=3)
bx = sx + sw + 0.04
bw = W - sw - 0.04
box(bx, 0.090, bw, 0.200, '#fdecea', '#c0392b', hatch='//')
stagelabel(bx + bw / 2, 0.245, '\u2717  GATED', '#7b241c')
ax.text(bx + bw / 2, 0.165, '(c)  pending Ch. 14', ha='center', va='center',
        fontsize=8.4, color='#7b241c', fontweight='bold', zorder=3)

# branch from CANDIDATES into BOTH outcome halves: a short central drop, a
# horizontal bus, then a vertical arrow into each box top, so the
# survivors-vs-rejected split is explicit (the old single arrow reached only
# OUTCOME and left the REJECTED path disembodied).
# R27 P2: the central drop was a third (redundant) arrowhead floating over the
# bus; it is now a plain connector line (no arrowhead) so only the two real
# targets (OUTCOME / GATED) carry arrowheads.
_bus_y = 0.305
_cx_out = sx + sw / 2
_cx_rej = bx + bw / 2
ax.plot([CX, CX], [0.323, _bus_y], color='#555', lw=1.6, zorder=3)
ax.plot([_cx_out, _cx_rej], [_bus_y, _bus_y], color='#555', lw=1.6, zorder=3)
ax.annotate('', xy=(_cx_out, 0.290), xytext=(_cx_out, _bus_y),
            arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#555'))
ax.annotate('', xy=(_cx_rej, 0.290), xytext=(_cx_rej, _bus_y),
            arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#555'))

plt.tight_layout()
plt.savefig('design/manuscript/chapter-12/figures/fig-12-1201.png', dpi=350)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-12/figures/fig-12-1201.pdf', format='pdf')
plt.close()
print('wrote fig-12-1201 (four-stage decision chain)')
