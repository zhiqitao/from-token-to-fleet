import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-15-1501: TWO SEPARATE EFFECTS (do not conflate) ----
# Panel (a): prefill work removed by prefix caching (effects the PREFILL phase).
# Panel (b): decode goodput vs decode batch size (the DECODE bottleneck --
# UNAFFECTED by prefix caching).
# Authored NARROW (6.4in) and saved with bbox_inches='tight' so nothing clips
# at the print column (~6.1in) -- the earlier 10in-wide version overflowed both
# edges and truncated the title/x-labels/panel titles.
batch = np.array([1, 2, 4, 8, 16, 32, 64])
prefill_nocache = np.full_like(batch, 100.0, dtype=float)
prefill_cache  = np.array([99, 94, 90, 84, 78, 72, 60], dtype=float)
goodput = np.array([8, 16, 29, 49, 74, 93, 100], dtype=float)

fig, (axa, axb) = plt.subplots(1, 2, figsize=(6.4, 3.3))

# Panel (a): prefill saving
axa.plot(batch, prefill_nocache, '-o', color='#c0392b', lw=1.8, label='no cache')
axa.plot(batch, prefill_cache, '-s', color='#2f6f4f', lw=1.8, label='with prefix cache')
axa.set_xscale('log')
axa.set_xlabel('Avg prefix reuse', fontsize=8.5)
axa.set_ylabel('Prefill FLOPs / req\n(% of no-cache)', fontsize=8.5)
axa.set_title('(a) Caching removes\nprefill work', fontsize=9)
axa.legend(fontsize=8, loc='upper right')
axa.grid(alpha=0.3, which='both')
axa.set_ylim(0, 110)
axa.set_xlim(1, 64)
axa.tick_params(labelsize=10)

# Panel (b): decode goodput
axb.plot(batch, goodput, '-o', color='#27408b', lw=1.8)
axb.set_xscale('log')
axb.set_xlabel('Decode batch size', fontsize=8.5)
axb.set_ylabel('Relative decode\ngoodput (a.u.)', fontsize=8.5)
axb.set_title('(b) Decode bottleneck\nunaffected by caching', fontsize=9)
axb.grid(alpha=0.3, which='both')
axb.set_ylim(0, 110)
axb.set_xlim(1, 64)
axb.tick_params(labelsize=10)
axb.text(1.2, 85, 'caching does not\nspeed one decode step', fontsize=8, color='#27408b')

fig.suptitle('Prefix caching vs batching: two independent effects', fontsize=10.5, fontweight='bold')
plt.tight_layout(rect=(0, 0, 1, 0.93))
plt.savefig('design/manuscript/chapter-15/figures/fig-15-1501.png',
            dpi=200, bbox_inches='tight', pad_inches=0.05)
plt.close()
print('wrote fig-15-1501 (narrow, tight-bbox)')
