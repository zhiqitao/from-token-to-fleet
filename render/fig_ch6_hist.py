import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-06-0602: Latency distribution (p50/p90/p95/p99 + mean) ----
# 99% of requests ~ log-normal around a healthy p50 ~0.75-0.8 s, 1% stragglers at 5 s.
# The point of Fig 6.2: the mean (~0.84 s) looks healthy, but the 1% tail is real.
# Percentiles are read off THIS synthetic stream (p50=0.80, p90=0.94, p95=0.99, p99=1.33);
# the 1% stragglers beyond the 99th percentile are the ones that cross the 2 s SLO.
rng = np.random.default_rng(42)
healthy = rng.lognormal(mean=np.log(0.8), sigma=0.12, size=9900)   # 99% around 0.8 s
stragg = np.full(100, 5.0)                                          # 1% at 5 s
lat = np.concatenate([healthy, stragg])
lat = np.clip(lat, 0.2, 6.0)

fig, ax = plt.subplots(figsize=(6.5, 5.0))
ax.hist(lat, bins=60, color='#3a6ea5', alpha=0.75, edgecolor='white', lw=0.3)
mean = lat.mean()
for p, yoff, xoff in [(50, 0.92, 0.05), (90, 0.80, 0.05), (95, 0.68, 0.05)]:
    v = np.percentile(lat, p)
    ax.axvline(v, color='#6f9e5f', ls='--', lw=1.3)
    ax.annotate(f'p{p} = {v:.2f}s', xy=(v, ax.get_ylim()[1]*0.9),
                xytext=(v+xoff, ax.get_ylim()[1]*yoff), fontsize=8, color='#2f6f4f')
# p99 breaches the tail: highlight it in red as the one the 1% stragglers set off beyond.
v99 = np.percentile(lat, 99)
ax.axvline(v99, color='#c0392b', ls='--', lw=1.8)
ax.annotate(f'p99 = {v99:.2f}s', xy=(v99, ax.get_ylim()[1]*0.56),
            xytext=(v99+0.25, ax.get_ylim()[1]*0.55), fontsize=8.5, color='#c0392b', fontweight='bold')
ax.axvline(mean, color='#555', ls='-', lw=1.8)
ax.annotate(f'mean = {mean:.2f}s', xy=(mean, ax.get_ylim()[1]*0.44),
            xytext=(mean*1.03, ax.get_ylim()[1]*0.43), fontsize=8, color='#333')
# 2 s SLO line
ax.axvline(2.0, color='#27408b', ls='-.', lw=2.0)
ax.annotate('SLO 2 s', xy=(2.0, ax.get_ylim()[1]*0.93),
            xytext=(2.05, ax.get_ylim()[1]*0.92), fontsize=8.5, color='#27408b', fontweight='bold')
ax.axvspan(4.0, 6.0, color='#c0392b', alpha=0.08)
ax.text(4.55, ax.get_ylim()[1]*0.36, '1% stragglers\nat ~5 s (cross the SLO)', fontsize=7.8, color='#c0392b', ha='center')
ax.set_xlabel('Request latency (s)')
ax.set_ylabel('Request count')
ax.set_title('Latency distribution: the mean hides the tail')
ax.set_xlim(0, 6.2)
ax.grid(alpha=0.2, axis='y')
plt.tight_layout()
plt.savefig('design/manuscript/chapter-06/figures/fig-06-0602.png', dpi=150)
plt.close()
print('wrote fig-06-0602')
