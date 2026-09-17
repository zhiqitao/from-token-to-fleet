import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-16-1601: TCO break-even across three serve modes ----
# self-hosted: high fixed (reserved capacity, flat vs volume)
# cloud on-demand: low fixed (per-use, flat at a duty-cycle assumption)
# managed API: linear per-request
req = np.logspace(4, 8, 300)
self_host = np.full_like(req, 16900.0)        # ~$16.9k/mo flat (reserved capacity)
cloud_od  = np.full_like(req, 5800.0)          # ~$5.8k/mo flat (on-demand @ 40% duty, $20/hr node)
managed   = 0.0208 * req                       # $20.80/1K -> linear

fig, ax = plt.subplots(figsize=(9, 6))
ax.loglog(req, self_host, '-', color='#27408b', lw=2.4, label='self-hosted (reserved capacity, ~$16.9k/mo flat)')
ax.loglog(req, cloud_od, '--', color='#6f9e5f', lw=2.2, label='cloud on-demand (~$5.8k/mo flat @ 40% duty)')
ax.loglog(req, managed, '-', color='#c0392b', lw=2.4, label='managed API ($20.80/1K, linear)')

ax.set_xlabel('Requests per month (log)')
ax.set_ylabel('Cost per month (USD, log)')
ax.set_title('TCO break-even across the three serve modes', fontsize=12)
ax.set_xlim(1e4, 1e8); ax.set_ylim(3e2, 3e6)
ax.legend(fontsize=8.5, loc='upper left')
ax.grid(alpha=0.3, which='both')

# reference lines
ax.axvline(1e6, color='#888', ls=':', lw=1.2)
ax.text(1.05e6, 4e2, '1M req/mo', fontsize=8, color='#888')
ax.axvline(2.6e7, color='#27408b', ls=':', lw=1.4)
ax.text(2.7e7, 3e3, 'canonical 26M req/mo', fontsize=8, color='#27408b')

# break-even self-host vs managed: solve 0.0208*x = 21200
be = 21200/0.0208
ax.plot([be], [21200], '*', ms=18, color='#c0392b', mec='#7b241c', zorder=6)
ax.text(be*0.6, 5e4, f'break-even ≈ {be/1e6:.2f}M req/mo\n(self-host vs managed API)', fontsize=9,
        color='#c0392b', fontweight='bold')

# annotations placed OUTSIDE the plot area (in figure margin), not over data
ax.text(0.02, -0.16, 'self-hosted flat (reserved capacity); managed API linear (per-request)',
        transform=ax.transAxes, fontsize=8.5, color='#444')
ax.text(0.02, -0.22, 'cloud on-demand flat @ 40% duty — excludes staff/integration (see §16.4)',
        transform=ax.transAxes, fontsize=8.5, color='#6f9e5f')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-16/figures/fig-16-1601.png', dpi=150)
plt.close()
print('wrote fig-16-1601')
