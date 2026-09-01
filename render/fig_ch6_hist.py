import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-06-0602: Latency distribution (p50/p90/p95/p99 + mean), 99%@0.8s + 1%@5s ----
# Build a synthetic-but-honest distribution matching the Ch6 example:
# 99% of requests ~0.8 s (log-normal around a healthy p50 ~0.75), 1% stragglers ~5 s.
# Marked with p50 / p90 / p95 / p99 and the mean (~0.84 s) to show the mean hides the tail.
rng = np.random.default_rng(42)
healthy = rng.lognormal(mean=np.log(0.8), sigma=0.12, size=9900)   # 99% around 0.8 s
stragg = np.full(100, 5.0)                                          # 1% exactly at 5 s
lat = np.concatenate([healthy, stragg])
lat = np.clip(lat, 0.2, 6.0)

fig, ax = plt.subplots(figsize=(8.5, 5))
ax.hist(lat, bins=60, color='#3a6ea5', alpha=0.75, edgecolor='white', lw=0.3)
# percentiles
mean = lat.mean()
for p, c, dyo in [(50, '#6f9e5f',0.0),(95, '#c0392b',0.5),(99, '#27408b',1.0)]:
    v = np.percentile(lat, p)
    ax.axvline(v, color=c, ls='--', lw=1.3)
    ax.annotate(f'p{p} ≈ {v:.2f}s', xy=(v, ax.get_ylim()[1]*0.9), xytext=(v+0.25, ax.get_ylim()[1]*(0.84+dyo)), fontsize=8, color=c)
ax.axvline(mean, color='#555', ls='-', lw=1.8)
ax.annotate(f'mean ≈ {mean:.2f}s — looks fine', xy=(mean, ax.get_ylim()[1]*0.95), xytext=(mean*1.02, ax.get_ylim()[1]*0.94), fontsize=8.5, color='#333')
# 2 s SLO line (the review-required service objective)
ax.axvline(2.0, color='#27408b', ls='-.', lw=2.0)
ax.annotate('SLO 2 s', xy=(2.0, ax.get_ylim()[1]*0.97), xytext=(2.05, ax.get_ylim()[1]*0.96), fontsize=9, color='#27408b', fontweight='bold')
ax.axvspan(3.5, 6.0, color='#c0392b', alpha=0.08)
ax.text(4.9, ax.get_ylim()[1]*0.45, '1% stragglers\n(blow the p95 budget)', fontsize=8.5, color='#c0392b', ha='center')
ax.set_xlabel('Request latency (s)')
ax.set_ylabel('Request count')
ax.set_title('Ch6 — latency distribution: the mean hides the tail (ILLUSTRATIVE)')
ax.set_xlim(0, 6.2)
ax.grid(alpha=0.2, axis='y')
plt.tight_layout()
plt.savefig('design/manuscript/chapter-06/figures/fig-06-0602.png', dpi=150)
plt.close()
print('wrote fig-06-0602')
