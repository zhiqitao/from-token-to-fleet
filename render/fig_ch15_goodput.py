import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-15-1501: TWO SEPARATE EFFECTS (do not conflate) ----
# Panel (a): prefill work removed by prefix caching (effects the PREFILL phase).
# Panel (b): decode goodput vs decode batch size (the DECODE bottleneck —
# UNAFFECTED by prefix caching).
batch = np.array([1, 2, 4, 8, 16, 32, 64])
# (a) effective prefill FLOPs per request (% of the no-cache baseline), falling
# as shared-prefix reuse grows (more reuse => less prefill work per request).
prefill_nocache = np.full_like(batch, 100.0, dtype=float)
prefill_cache  = np.array([99, 94, 90, 84, 78, 72, 60], dtype=float)
# (b) decode goodput vs batch (arbitrary units; memory-bound decode is unchanged)
goodput = np.array([8, 16, 29, 49, 74, 93, 100], dtype=float)

fig, (axa, axb) = plt.subplots(1, 2, figsize=(10, 4.4))

# Panel (a): prefill saving
axa.plot(batch, prefill_nocache, '-o', color='#c0392b', lw=2, label='no prefix cache (always refill prefill)')
axa.plot(batch, prefill_cache, '-s', color='#2f6f4f', lw=2, label='with prefix cache (reuse shared prefix)')
axa.set_xscale('log')
axa.set_xlabel('Shared-prefix reuse (turns/requests with the same prefix)')
axa.set_ylabel('Effective prefill FLOPs per request (% of no-cache)')
axa.set_title('(a) Prefix caching removes PREFILL work', fontsize=10.5)
axa.legend(fontsize=7.5, loc='upper right')
axa.grid(alpha=0.3, which='both')
axa.set_ylim(0, 110)

# Panel (b): decode goodput
axb.plot(batch, goodput, '-o', color='#27408b', lw=2, label='decode goodput vs batch size')
axb.set_xscale('log')
axb.set_xlabel('Decode batch size')
axb.set_ylabel('Relative decode goodput (a.u.)')
axb.set_title('(b) Decode bottleneck is UNAFFECTED by caching', fontsize=10.5)
axb.grid(alpha=0.3, which='both')
axb.set_ylim(0, 110)
axb.text(1.2, 90, 'prefix caching does not\nspeed up a single decode step', fontsize=7.5, color='#27408b')

fig.suptitle('Prefix caching vs batching: two independent effects (do not conflate)', fontsize=12, fontweight='bold')
axa.set_xlim(1, 64); axb.set_xlim(1, 64)
plt.tight_layout(rect=(0, 0, 1, 0.94))
plt.savefig('design/manuscript/chapter-15/figures/fig-15-1501.png', dpi=150)
plt.close()
print('wrote fig-15-1501 (two independent effects)')
