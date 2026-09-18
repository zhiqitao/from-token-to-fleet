import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math

# ---- fig-22-2201: Prefill compute grows super-linearly with context; decode is flat ----
# Canonical 70B (N = 70e9). Prefill FLOPs grow with context length:
#   linear term: prefill FLOPs ~ 2*N*L
#   quadratic band: attention term adds a super-linear component. Fit the band
#   to the chapter's anchors -- +17% @ 9.2K, ~2.4x @ 128K (ILLUSTRATIVE; exact
#   QK^T/AV scaling is architecture-dependent) -- as ratio = 1 + c*L^p.
# Decode: ~2 N FLOPs/token (fixed, independent of context), shown on the same
# log-y axis so the flat decode vs super-linear prefill divergence is visible.
N = 70e9
L = np.logspace(np.log10(0.8e3), np.log10(128e3), 400)
lin = 2 * N * L
p = math.log(1.4 / 0.17) / math.log(128 / 9.2)
c = 0.17 / (9.2e3 ** p)
quad = lin * (1.0 + c * (L ** p))
decode = 2 * N * np.ones_like(L)          # per-token decode FLOPs, context-independent

fig, ax = plt.subplots(figsize=(8.5, 5.4))
ax.semilogy(L / 1e3, lin / 1e15, color='#c0392b', lw=2.6, marker='o', ms=4,
            label='prefill FLOPs per request (linear 2NL)')
ax.semilogy(L / 1e3, quad / 1e15, color='#e67e22', lw=2.0, ls='--', marker='s', ms=4,
            label='prefill incl. quadratic attention (per request)')
ax.semilogy(L / 1e3, decode / 1e15, color='#27408b', lw=2.4, marker='^', ms=4,
            label='decode FLOPs per generated token (fixed 2N)')
ax.fill_between(L / 1e3, lin / 1e15, quad / 1e15, color='#e67e22', alpha=0.10)

for Lk, lab in [(9.2, '9.2K canonical'), (32, '+~46% @32K'), (128, '~2.4× @128K')]:
    v = 2 * N * Lk * 1e3
    qv = v * (1 + c * ((Lk * 1e3) ** p))
    ax.annotate(lab, xy=(Lk, qv / 1e15),
                xytext=(Lk * 1.15, qv / 1e15 * 1.5), fontsize=8.5,
                arrowprops=dict(arrowstyle='-|>', lw=1.0, color='#555'), color='#333')

ax.set_xscale('log')
ax.set_xlabel('Context length (K tokens)')
ax.set_ylabel('Compute (PFLOP; see series definition)')
ax.set_title('Prefill compute grows super-linearly with context; decode stays flat')
ax.set_ylim(3e-5, 1e2)
ax.grid(alpha=0.3, which='both')
ax.legend(fontsize=8, loc='upper left')
plt.tight_layout()
plt.savefig('design/manuscript/chapter-22/figures/fig-22-2201.png', dpi=150)
plt.close()
print('wrote fig-22-2201 (log-y, added decode series)')
