import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-06-0602: Latency distribution (p50/p90/p95/p99 + mean) ----
# 99% of requests ~ log-normal around a healthy p50 ~0.75-0.8 s, 1% stragglers at 5 s.
# The point of Fig 6.2: the mean (~0.84 s) looks healthy, but the 1% tail is real.
# Percentiles are read off THIS SYNTHETIC stream (p50=0.80, p90=0.94, p95=0.99, p99=1.33);
# the 1% stragglers beyond the 99th percentile are the ones that cross the 2 s SLO.
rng = np.random.default_rng(42)
healthy = rng.lognormal(mean=np.log(0.8), sigma=0.12, size=9900)   # 99% around 0.8 s
stragg = np.full(100, 5.0)                                          # 1% at 5 s
lat = np.concatenate([healthy, stragg])
lat = np.clip(lat, 0.2, 6.0)

fig, ax = plt.subplots(figsize=(6.1, 4.2))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.hist(lat, bins=60, color='#3a6ea5', alpha=0.75, edgecolor='white', lw=0.3)
mean = lat.mean()
# p50/p90/p95 lines cluster near the left (0.8-1.0s of a 6.2s axis), so label each
# directly above its own line in the upper whitespace (data-x, high data-y).
for p, yfrac in [(50, 0.90), (90, 0.83), (95, 0.76)]:
    v = np.percentile(lat, p)
    ax.axvline(v, color='#6f9e5f', ls='--', lw=1.3)
    ax.text(v+0.04, ax.get_ylim()[1]*yfrac, f'p{p}', fontsize=8.5, color='#2f6f4f', fontweight='bold', va='center')
# p99 breaches the tail? NO — p99=1.33 is still under the 2s SLO. Emphasize it in red.
v99 = np.percentile(lat, 99)
ax.axvline(v99, color='#c0392b', ls='--', lw=1.9)
# the 5s stragglers sit beyond p99 — between p99 and p100 — so a p99 line alone does
# not reveal them. Add the observation that the straggler mass is only visible at max.
ax.axvline(lat.max(), color='#c0392b', ls=':', lw=1.4)
# mean line
ax.axvline(mean, color='#555', ls='-', lw=1.7)
# 2 s SLO line
ax.axvline(2.0, color='#27408b', ls='-.', lw=2.2)
# Compact legend in the clear upper-right whitespace (the annotated lines all cluster
# near x=0.8-2.0 on a 6.2s axis, so label them as a legend, not along the crowded lines).
ax.text(3.45, ax.get_ylim()[1]*0.86, 'mean = %.2fs\np99 = %.2fs\nSLO 2 s\n(p99 still looks fine)' % (mean, v99),
        fontsize=8.5, color='#333', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.35', fc='#f7f7f7', ec='#cccccc', lw=0.8))
ax.axvspan(4.0, 6.0, color='#c0392b', alpha=0.08)
ax.text(5.0, 0.40, '1% stragglers\n~5 s (cross the SLO)', fontsize=8.5, color='#c0392b', ha='center')

ax.set_xlabel('Request latency (s)', fontsize=9.5)
ax.set_ylabel('Request count', fontsize=9.5)
ax.set_title('Latency distribution: the mean hides the tail', fontsize=10.5, pad=26)
# bold ILLUSTRATIVE tag as a distinct subtitle line (clear below the title)
ax.text(0.5, 1.055, '[ILLUSTRATIVE synthetic profile]', transform=ax.transAxes, fontsize=9,
        fontweight='bold', color='#8a3a12', ha='center', va='bottom')
ax.set_xlim(0, 6.2)
ax.grid(alpha=0.2, axis='y')
ax.tick_params(labelsize=9)
plt.tight_layout()
plt.savefig('design/manuscript/chapter-06/figures/fig-06-0602.png', dpi=150)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-06/figures/fig-06-0602.pdf', format='pdf')
plt.close()
print('wrote fig-06-0602')
