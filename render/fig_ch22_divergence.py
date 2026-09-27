import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

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
ax1.tick_params(labelsize=8.5)
ax1.grid(alpha=0.3, which='both')
ax1.legend(fontsize=7.6, loc='upper right', framealpha=0.92, frameon=True)
ax1.annotate('quadratic dominates\n\u2265 ~32K',
             xy=(32, (2*N*32e3 + 4*nl*(32e3**2)*d)/1e15),
             xytext=(1.7, 0.06), fontsize=10.5, color='#8e44ad', fontweight='bold',
             ha='left', va='bottom',
             arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#8e44ad'))
# canonical 9.2K point (Figure caption footnote refers to it)
ax1.scatter([9.2], [(2 * N * 9.2e3) / 1e15], color='#c0392b', zorder=5, s=26)

# ---- RIGHT panel: decode FLOPs per token (flat, context-independent) ----
ax2.loglog(L / 1e3, decode / 1e15, color='#27408b', lw=3.4)
ax2.set_xlabel('Context length (K tokens)', fontsize=9.5)
ax2.set_ylabel('Decode compute (PFLOP / token)', fontsize=9.5)
ax2.set_title('DECODE  (per token)', fontsize=10, fontweight='bold', color='#27408b')
ax2.set_ylim(1e-5, 1e-3)
ax2.tick_params(labelsize=8.5)
ax2.grid(alpha=0.3, which='both')
ax2.text(1.2, 2.6e-5, '\u2248 1.4e-4 PFLOP/token\n(flat across context)',
         fontsize=10.5, color='#27408b', fontweight='bold', va='center', ha='left')

fig.text(0.5, 0.975, 'LEFT: PER REQUEST   |   RIGHT: PER GENERATED TOKEN',
         ha='center', va='top', fontsize=10, fontweight='bold', color='#7a0000',
         bbox=dict(boxstyle='round,pad=0.40', facecolor='#fff2f2', edgecolor='#c0392b', lw=2.0))

plt.subplots_adjust(left=0.12, right=0.97, top=0.80, bottom=0.10, wspace=0.30)
plt.savefig('design/manuscript/chapter-22/figures/fig-22-2201.png', dpi=150)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-22/figures/fig-22-2201.pdf', format='pdf')
plt.close()
print('wrote fig-22-2201 (dramatic side-by-side prefill-vs-decode, one annotation line each)')
