import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# log-axis tick labels: show plain "1", "10" (not "10^0"/"10^1") so the
# exponent does not render at 0.7x (7pt) — same fix as Fig 22.1.
def _logfmt(x, pos):
    if x <= 0:
        return ""
    e = np.floor(np.log10(x))
    if abs(x - 10**e) < 1e-9:
        return f"{int(10**e)}"
    return f"{x:g}"

# ---- fig-15-1501: TWO SEPARATE EFFECTS (do not conflate) ----
# Panel (a): prefill work removed by prefix caching (effects the PREFILL phase).
# Panel (b): decode goodput vs decode batch size (the DECODE bottleneck --
# UNAFFECTED by prefix caching).
# Authored NARROW (6.4in) and saved with bbox_inches='tight' so nothing clips
# at the print column (~6.1in) -- the earlier 10in-wide version overflowed both
# edges and truncated the title/x-labels/panel titles.
batch = np.array([1, 2, 4, 8, 16, 32, 64])
# Panel (a) operand: AVERAGE PREFIX REUSE (reuses per repeated prompt) -- adjudicated
# from the mechanism, not renamed cosmetically: caching removes prefill work per
# REPEATED prompt, so the independent variable of panel (a) is reuse count; batch
# size affects decode (panel b) and cannot remove prefill FLOPs/request. Same
# log-spaced 1..64 grid, separate name so the operand matches the axis
# 'Avg prefix reuse' and the caption; values are synthetic [ILLUSTRATIVE].
reuse = np.array([1, 2, 4, 8, 16, 32, 64])
prefill_nocache = np.full_like(reuse, 100.0, dtype=float)
# FIG-15.2-02: replot panel (a) from the stated amortization law
# f(r) = (S + P/r) / (S + P) with P = 40% of the prompt (reusable prefix) and
# S = 60% (unique suffix): monotone and convex-decreasing on the log-r axis --
# largest drop between r=1 and r=10, flattening toward S/(S+P) = 60%.
# r=1 gives f(1)=1 exactly, so the point stays on the no-cache line at 100.
P_frac, S_frac = 0.40, 0.60
def _amort(r):
    return 100.0 * (S_frac + P_frac / np.asarray(r, dtype=float)) / (S_frac + P_frac)
prefill_cache = _amort(reuse)
# decode goodput rises with batch, THEN PLATEAUS as bandwidth saturates (~near batch 16):
# the knee is where further batching stops raising throughput but keeps raising tail latency.
goodput = np.array([8, 16, 29, 48, 66, 80, 88], dtype=float)

fig, (axa, axb) = plt.subplots(1, 2, figsize=(6.1, 3.5))
fig._hermes_print_sized = True   # regen must not re-boost/reflow

# Panel (a): prefill saving -- smooth law over the full axis (r=1..90) plus
# markers on the 1..64 reuse grid; label carries the formula and its P/S split.
reuse_dense = np.logspace(0.0, np.log10(90.0), 400)
axa.plot(reuse, prefill_nocache, '-o', color='#c0392b', lw=1.8, label='no cache')
axa.plot(reuse_dense, _amort(reuse_dense), '-', color='#2f6f4f', lw=1.8,
         label='with prefix cache')
axa.plot(reuse, prefill_cache, 's', color='#2f6f4f', ms=4.5)
axa.text(0.98, 0.40, 'f(r)=(S+P/r)/(S+P)\nP=40%, S=60%',
         transform=axa.transAxes, fontsize=7.0, color='#2f6f4f',
         ha='right', va='top')
axa.set_xscale('log')
axa.set_xlabel('Avg prefix reuse', fontsize=9)
axa.set_ylabel('Prefill FLOPs / req\n(% of no-cache)', fontsize=9)
axa.set_title('(a) Caching removes\nprefill work', fontsize=9.5)
axa.legend(fontsize=8, loc='lower left')
axa.grid(alpha=0.3, which='both')
axa.set_ylim(0, 110)
axa.set_xlim(0.9, 90)
axa.tick_params(labelsize=10)
axa.xaxis.set_major_formatter(FuncFormatter(_logfmt))

# Panel (b): decode goodput
axb.plot(batch, goodput, '-o', color='#27408b', lw=1.8)
axb.set_xscale('log')
axb.set_xlabel('Decode batch size', fontsize=9)
axb.set_ylabel('Relative decode\ngoodput (a.u.)', fontsize=9)
# FIG-15.2-03: title now states only what the axes encode (one series, batch
# size on x); the "unaffected by caching" claim moved to the chapter-15.md
# caption, next to "They are not competing on the same axis".
axb.set_title('(b) Decode goodput\nvs batch size', fontsize=9.5)
axb.grid(alpha=0.3, which='both')
axb.set_ylim(0, 100)
axb.set_xlim(1, 64)
axb.tick_params(labelsize=10)
axb.xaxis.set_major_formatter(FuncFormatter(_logfmt))
# knee: beyond ~batch 16 the goodput gain per added batch flattens while tail latency keeps rising
axb.axvline(16, color='#c0392b', ls='--', lw=1.1)
# R27 P2: the old "goodput plateau (~b16)" overclaimed — the curve keeps rising
# past b16 (66 -> 80 -> 88), it only shows diminishing gains. Reword to match.
axb.text(1.7, 90, 'diminishing gains\npast ~b16 (no hard\nplateau): goodput\nstill rises; tail\nlatency keeps rising',
         fontsize=8.0, color='#c0392b', va='top')

fig.suptitle('Prefix caching vs batching: two independent effects', fontsize=10.5, fontweight='bold')
# In-figure [ILLUSTRATIVE] footer removed (Loop-3): bracketed taxonomy tags
# inside a graphic read as metadata leakage; the .md caption already carries
# the figure's evidence label.
plt.tight_layout(rect=(0, 0, 1, 0.91))
plt.savefig('design/manuscript/chapter-15/figures/fig-15-1501.png',
            dpi=400, bbox_inches='tight', pad_inches=0.05)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-15/figures/fig-15-1501.pdf', format='pdf')
plt.close()
print('wrote fig-15-1501 (narrow, tight-bbox)')
