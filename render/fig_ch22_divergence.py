import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# Log-axis tick labels as "10^e" with Unicode superscripts, so the exponent
# renders at the FULL tick size (matplotlib's mathtext exponents are 0.7x,
# which put them below the 8pt print floor).
_SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
def _logfmt(x, pos):
    if x <= 0:
        return ""
    e = int(round(np.log10(x)))
    return "10" + str(e).translate(_SUP)

# ---- fig-22-2201: Prefill compute grows super-linearly with context; decode is flat ----
# Canonical 70B (N = 70e9). Prefill FLOPs grow with context length:
#   linear term:      prefill FLOPs ~ 2*N*L
#   quadratic term (textbook, matches Ch8): 4*nl*L^2*d
# Decode: ~2 N FLOPs/token (fixed, context-independent).
# Prefill is quoted PER REQUEST (grows with L); decode is quoted PER TOKEN (fixed 2N).
# These are NOT unit-comparable on one absolute 0-* axis, so we render TWO aligned
# panels and the reader is never invited to compare their heights.
#
# DESIGNER PASS (synthesis figure): the left/right comparison gets dramatic space.
# Two large side-by-side panels (~48% of the figure width each, near-zero gutter so the
# panels dominate the width), a taller canvas, larger title/axis/annotation type, and
# ONE short bold annotation line per panel. Channel redundancy is preserved: the
# quadratic term and the total are distinguished by line style (dash) AND colour AND label.
N = 70e9
nl, d = 80, 8192
L = np.logspace(np.log10(0.8e3), np.log10(128e3), 400)
lin = 2 * N * L
quad = 4 * nl * (L ** 2) * d          # exact quadratic attention term per request
decode = 2 * N * np.ones_like(L)      # per-token decode FLOPs, context-independent

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.1, 5.2))
fig._hermes_print_sized = True   # print-size authored; regen must not re-boost/reflow

# ---- LEFT panel: prefill FLOPs per request, decomposed (linear vs quadratic term) ----
ax1.loglog(L / 1e3, lin / 1e15, color='#c0392b', lw=2.6, label='linear 2\u00b7N\u00b7L')
ax1.loglog(L / 1e3, quad / 1e15, color='#8e44ad', lw=2.4, ls='-.',
           label='quadratic 4\u00b7n\u2097\u00b7L\u00b2\u00b7d')
ax1.loglog(L / 1e3, (lin + quad) / 1e15, color='#e67e22', lw=2.4, ls='--',
           label='total = linear + quadratic')
ax1.fill_between(L / 1e3, lin / 1e15, (lin + quad) / 1e15, color='#e67e22', alpha=0.10)
ax1.set_xlabel('Context length (K tokens)', fontsize=9.5)
ax1.set_ylabel('Prefill compute (PFLOP / request)', fontsize=9.5)
ax1.set_title('PREFILL  (per request)', fontsize=10, fontweight='bold', color='#5a2a7a')
ax1.set_ylim(1e-2, 1e3)
ax1.tick_params(which='major', labelsize=8.5)
ax1.tick_params(which='minor', labelsize=0)   # hide minor tick labels (log-axis clutter); keep grid
ax1.yaxis.set_major_formatter(FuncFormatter(_logfmt))  # "10^e" at full tick size
ax1.xaxis.set_major_formatter(FuncFormatter(_logfmt))
ax1.grid(alpha=0.3, which='both')
ax1.legend(fontsize=8.5, loc='upper right', framealpha=0.92, frameon=True)
# Crossover: equality of linear (2*N*L) and quadratic (4*nl*L^2*d) terms:
#   L* = N / (2*nl*d) = 70e9 / (2*80*8192) = 53,406 tokens  (P0-03 fix).
# ONE concise arrow annotation at the crossover; the full explanation (incl. the
# 9.2K / 32K / 128K ratios) lives in the figure caption, so the label stays short.
# The label sits in the clear horizontal whitespace band between the curves
# (max y = total(68K) ~= 21.6) and the legend (bottom edge y ~= 124). At y=45 the
# text box spans data y ~= 27.8..72.9, wholly above every curve and below the
# legend, so it never obscures a curve. Anchored ha='right' at x=68 so it stays
# inside the panel; a short near-vertical leader arrow drops to the crossover.
Lstar = N / (2 * nl * d)
ax1.annotate('quadratic overtakes\nlinear at ~%.0fK' % (Lstar/1e3),
             xy=(Lstar/1e3, (2*N*Lstar)/1e15),
             xytext=(68.0, 45.0), fontsize=8.8, color='#8e44ad', fontweight='bold',
             ha='right', va='center',
             arrowprops=dict(arrowstyle='-|>', lw=1.1, color='#8e44ad'))
# canonical 9.2K point (Figure caption footnote refers to it)
ax1.scatter([9.2], [(2 * N * 9.2e3) / 1e15], color='#c0392b', zorder=5, s=26)

# ---- RIGHT panel: decode FLOPs per token (flat, context-independent) ----
ax2.loglog(L / 1e3, decode / 1e15, color='#27408b', lw=3.4,
           label='decode  2·N  (per token,\nPARAMETER term only)')
ax2.set_xlabel('Context length (K tokens)', fontsize=9.5)
ax2.set_ylabel('Decode compute (PFLOP / token)', fontsize=9.5)
ax2.set_title('DECODE  (per token)', fontsize=10, fontweight='bold', color='#27408b')
ax2.set_ylim(1e-5, 1e-3)
ax2.tick_params(which='major', labelsize=8.5)
ax2.tick_params(which='minor', labelsize=0)   # hide minor tick labels (log-axis clutter); keep grid
ax2.yaxis.set_major_formatter(FuncFormatter(_logfmt))  # "10^e" at full tick size
ax2.xaxis.set_major_formatter(FuncFormatter(_logfmt))
ax2.grid(alpha=0.3, which='both')
ax2.legend(fontsize=8.5, loc='upper right', framealpha=0.92, frameon=True)
ax2.text(0.83, 3.2e-5, '2·N only — full decode\nadds KV attention',
         fontsize=8.2, color='#27408b', fontweight='bold', va='center', ha='left')

fig.text(0.5, 0.975, 'LEFT: PER REQUEST   |   RIGHT: PER GENERATED TOKEN',
         ha='center', va='top', fontsize=10, fontweight='bold', color='#7a0000',
         bbox=dict(boxstyle='round,pad=0.40', facecolor='#fff2f2', edgecolor='#c0392b', lw=2.0))

plt.subplots_adjust(left=0.12, right=0.97, top=0.80, bottom=0.10, wspace=0.30)
plt.savefig('design/manuscript/chapter-22/figures/fig-22-2201.png', dpi=350)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-22/figures/fig-22-2201.pdf', format='pdf')
plt.close()
print('wrote fig-22-2201 (dramatic side-by-side prefill-vs-decode, one annotation line each)')
