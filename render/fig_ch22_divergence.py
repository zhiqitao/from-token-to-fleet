import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-22-2201: Prefill compute grows super-linearly with context; decode is flat ----
# Canonical 70B (N = 70e9). Prefill FLOPs grow with context length:
#   linear term: prefill FLOPs ~ 2*N*L
#   quadratic attention term (textbook, matches Ch8): 4*nl*L^2*d
# Decode: ~2 N FLOPs/token (fixed, context-independent).
# Because prefill is quoted PER REQUEST (grows with L) while decode is quoted PER TOKEN
# (fixed 2N), these two are NOT unit-comparable on one absolute 0-* axis. We therefore
# render TWO aligned panels — left: prefill per-request (linear vs linear+quadratic),
# right: decode per-token (flat 2N) — so no reader is invited to compare their heights.
N = 70e9
nl, d = 80, 8192
L = np.logspace(np.log10(0.8e3), np.log10(128e3), 400)
lin = 2 * N * L
quad = 4 * nl * (L ** 2) * d          # exact quadratic attention term per request
decode = 2 * N * np.ones_like(L)      # per-token decode FLOPs, context-independent

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.1, 4.6), sharey=False)
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow

# Left panel: prefill FLOPs per request, DECOMPOSED into its two components so the
# growing quadratic attention term is visible on its own (not just the sum).
ax1.loglog(L / 1e3, lin / 1e15, color='#c0392b', lw=2.4,
           label='linear term (2·N·L)')
ax1.loglog(L / 1e3, quad / 1e15, color='#8e44ad', lw=2.0, ls='-.',
           label='quadratic attention term (4·nl·L²·d)')
ax1.loglog(L / 1e3, (lin + quad) / 1e15, color='#e67e22', lw=2.2, ls='--',
           label='total = linear + quadratic')
ax1.fill_between(L / 1e3, lin / 1e15, (lin + quad) / 1e15, color='#e67e22', alpha=0.10)
for Lk, lab in [(9.2, '+17% @9.2K'), (32, '+60% @32K'), (128, '~2.4× @128K')]:
    v = lin[0]  # placeholder; recompute at Lk
    lk = Lk * 1e3
    qv = (2 * N * lk + 4 * nl * (lk ** 2) * d) / 1e15
    ax1.annotate(lab, xy=(Lk, qv), xytext=(Lk * 1.4, qv * 1.6),
                 fontsize=8.5, arrowprops=dict(arrowstyle='-|>', lw=1.0, color='#555'), color='#333')
ax1.scatter([9.2], [(2 * N * 9.2e3) / 1e15], color='#c0392b', zorder=5, s=30)
ax1.set_xlabel('Context length (K tokens)')
ax1.set_ylabel('Prefill compute (PFLOP / request)', fontsize=8.5)
ax1.set_title('Prefill per request (decomposed):\nlinear + quadratic attention', fontsize=9.5)
ax1.set_ylim(1e-2, 1e3)
ax1.grid(alpha=0.3, which='both')
ax1.legend(fontsize=7.5, loc='upper center', bbox_to_anchor=(0.5, -0.13), frameon=False)

# Right panel: decode FLOPs per token (flat, context-independent)
ax2.loglog(L / 1e3, decode / 1e15, color='#27408b', lw=2.4)
ax2.set_xlabel('Context length (K tokens)')
ax2.set_ylabel('Decode compute (PFLOP / token)')
ax2.set_title('Decode per token:\nfixed 2N (context-independent)', fontsize=9.5)
ax2.set_ylim(1e-5, 1e-3)
ax2.grid(alpha=0.3, which='both')
ax2.text(1.2, 2.5e-5, '≈ 1.4e-4 PFLOP/token\n(fixed; same at all context)', fontsize=8, color='#27408b')

fig.text(0.5, 0.965,
         '⚠  LEFT: PER REQUEST   |   RIGHT: PER GENERATED TOKEN',
         ha='center', va='top', fontsize=11, fontweight='bold', color='#7a0000',
         bbox=dict(boxstyle='round,pad=0.45', facecolor='#fff2f2', edgecolor='#c0392b', lw=2.0))
fig.text(0.5, 0.915,
         'DO NOT COMPARE Y-AXIS MAGNITUDES DIRECTLY  — different units, different baselines',
         ha='center', va='top', fontsize=9, fontweight='bold', color='#c0392b')
fig.text(0.5, 0.872,
         'Left = total prefill compute for ONE request (grows with context L). Right = compute for ONE generated token '
         '(fixed 2N, context-independent). The quadratic term is the textbook 4·n_layers·L²·d (matches Chapter 8). '
         '[ILLUSTRATIVE][DERIVED]',
         ha='center', va='top', fontsize=7.8, color='#555', wrap=True)

plt.tight_layout(rect=(0, 0.07, 1, 0.82))
plt.savefig('design/manuscript/chapter-22/figures/fig-22-2201.png', dpi=150)
plt.close()
print('wrote fig-22-2201 (decomposed prefill: linear + quadratic; prominent per-request-vs-per-token warning)')
