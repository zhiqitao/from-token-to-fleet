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
quad = 4 * nl * (L ** 2) * d          # CASE (ii) full-square (un-masked) attention term per request
decode = 2 * N * np.ones_like(L)      # per-token decode FLOPs, context-independent

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.1, 5.2))
fig._hermes_print_sized = True   # print-size authored; regen must not re-boost/reflow

# ---- LEFT panel: prefill FLOPs per request, decomposed (linear vs quadratic term) ----
ax1.loglog(L / 1e3, lin / 1e15, color='#c0392b', lw=2.6, label='linear 2\u00b7N\u00b7L')
ax1.loglog(L / 1e3, quad / 1e15, color='#8e44ad', lw=2.4, ls='-.',
           label='quadratic 4\u00b7n_layers\u00b7L\u00b2\u00b7d')
ax1.loglog(L / 1e3, (lin + quad) / 1e15, color='#e67e22', lw=2.4, ls='--',
           label='total (full-square)')
# P2-05: causal-triangle SENSITIVITY curve - a causal mask does half the
# attention-pair work (2*nl*L^2*d = quad/2), so the total falls and the
# crossover moves 53.4K -> 106.8K. One curve, one legend entry: a 4-entry
# legend is what leaves the annotation band clear (verified by bbox probe).
ax1.loglog(L / 1e3, (lin + quad / 2) / 1e15, color='#0e7a5f', lw=2.4, ls=':',
           label='total (causal-triangle)')
ax1.fill_between(L / 1e3, lin / 1e15, (lin + quad) / 1e15, color='#e67e22', alpha=0.10)
ax1.set_xlabel('Context length (K tokens)', fontsize=9.5)
ax1.set_ylabel('Prefill compute (PFLOP / request)', fontsize=9.5)
ax1.set_title('PREFILL  (per request)', fontsize=10, fontweight='bold', color='#5a2a7a')
ax1.set_ylim(1e-2, 1e3)
# P1 legibility floor: ch22 places this figure at width=0.95\linewidth
# (0.95 x 439.2pt = 417.24pt), so every authored size is multiplied by 0.95
# on the page. 8.5pt ticks/legend landed at 8.07pt and the 8.2pt panel note at
# 7.79pt (< 8pt print floor). Author at 8.6pt -> 8.17pt placed, >= 8pt.
ax1.tick_params(which='major', labelsize=8.6)
ax1.tick_params(which='minor', labelsize=0)   # hide minor tick labels (log-axis clutter); keep grid
ax1.yaxis.set_major_formatter(FuncFormatter(_logfmt))  # "10^e" at full tick size
ax1.xaxis.set_major_formatter(FuncFormatter(_logfmt))
ax1.grid(alpha=0.3, which='both')
ax1.legend(fontsize=8.6, loc='upper right', framealpha=0.92, frameon=True)
# Crossover annotations: equality of linear (2*N*L) with the quadratic term.
#   full-square:      L* = N / (2*nl*d) = 70e9 / (2*80*8192) = 53,406 tokens
#   causal-triangle:  L* = N / (nl*d)   = 70e9 / (80*8192)   = 106,812 tokens
# ONE concise arrow annotation per crossover; the full explanation (incl. the
# 9.2K / 32K / 128K ratios and the FLOP-counting convention) lives in the figure
# caption, so each label stays short. The full-square label sits in the clear
# horizontal whitespace band between the curves (max y = total(68K) ~= 21.6) and
# the legend; a short near-vertical leader arrow drops to the crossover.
Lstar = N / (2 * nl * d)          # full-square: 4·nl·L²·d = 2N·L  -> 53,406
Lstar_c = N / (nl * d)            # causal-triangle (÷2)           -> 106,812
ax1.annotate('full-square quad\novertakes ~%.1fK' % (Lstar/1e3),
             xy=(Lstar/1e3, (2*N*Lstar)/1e15),
             xytext=(40.0, 24.0), fontsize=8.8, color='#8e44ad', fontweight='bold',
             ha='right', va='center',
             arrowprops=dict(arrowstyle='-|>', lw=1.1, color='#8e44ad'))
# P2-05: second crossover, causal-triangle sensitivity (half the attention-pair
# term doubles the crossing). Positions were chosen with a renderer bbox probe
# (text-only extents vs legend vs sampled curves): purple sits in the clear band
# between total(40K)=9.8 and the 4-entry legend; teal is right-anchored at x=126
# so its left edge (7.0K) clears quad/2 (0.064 > 0.036); the 'canonical 9.2K'
# label sits at y=3.0, above every curve in its x-range (max total(7.7K)=1.30)
# and below the purple annotation; its short leader drops to the marker.
ax1.annotate('causal-triangle:\ncrossover ~%.1fK' % (Lstar_c/1e3),
             xy=(Lstar_c/1e3, (2*N*Lstar_c)/1e15),
             xytext=(126.0, 0.022), fontsize=8.8, color='#0e7a5f', fontweight='bold',
             ha='right', va='center',
             arrowprops=dict(arrowstyle='-|>', lw=1.1, color='#0e7a5f'))
# canonical 9.2K point (Figure caption footnote refers to it)
ax1.scatter([9.2], [(2 * N * 9.2e3) / 1e15], color='#c0392b', zorder=5, s=26)
# R27 P2: the red dot was unexplained (no legend/annotation). Label it as the
# canonical 9.2K context so the marker has a clear referent.
ax1.annotate('canonical 9.2K', xy=(9.2, (2 * N * 9.2e3) / 1e15), xytext=(0.85, 3.0),
             fontsize=8.6, color='#c0392b', ha='left', va='center',
             arrowprops=dict(arrowstyle='-', lw=0.6, color='#c0392b'))

# ---- RIGHT panel: decode FLOPs per token (flat, context-independent) ----
ax2.loglog(L / 1e3, decode / 1e15, color='#27408b', lw=3.4,
           label='decode  2·N  (per token,\nPARAMETER term only)')
ax2.set_xlabel('Context length (K tokens)', fontsize=9.5)
ax2.set_ylabel('Decode compute (PFLOP / token)', fontsize=9.5)
ax2.set_title('DECODE  (per token)', fontsize=10, fontweight='bold', color='#27408b')
ax2.set_ylim(1e-5, 1e-3)
ax2.tick_params(which='major', labelsize=8.6)
ax2.tick_params(which='minor', labelsize=0)   # hide minor tick labels (log-axis clutter); keep grid
ax2.yaxis.set_major_formatter(FuncFormatter(_logfmt))  # "10^e" at full tick size
ax2.xaxis.set_major_formatter(FuncFormatter(_logfmt))
ax2.grid(alpha=0.3, which='both')
ax2.legend(fontsize=8.6, loc='upper right', framealpha=0.92, frameon=True)
ax2.text(0.83, 3.2e-5, '2·N only — full decode\nadds KV attention',
         fontsize=8.6, color='#27408b', fontweight='bold', va='center', ha='left')

fig.text(0.5, 0.975, 'LEFT: PER REQUEST   |   RIGHT: PER GENERATED TOKEN',
         ha='center', va='top', fontsize=10, fontweight='bold', color='#7a0000',
         bbox=dict(boxstyle='round,pad=0.40', facecolor='#fff2f2', edgecolor='#c0392b', lw=2.0))

plt.subplots_adjust(left=0.12, right=0.97, top=0.80, bottom=0.10, wspace=0.30)
plt.savefig('design/manuscript/chapter-22/figures/fig-22-2201.png', dpi=350)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-22/figures/fig-22-2201.pdf', format='pdf')
plt.close()
print('wrote fig-22-2201 (prefill-vs-decode, full-square + causal-triangle sensitivity, two crossovers)')
