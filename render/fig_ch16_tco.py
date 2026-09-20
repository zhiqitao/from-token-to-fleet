import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-16-1601: TCO break-even across three serve modes ----
# Values are the FLEET-SCALED costs from Ch16 §16.4 (canonical ~20-host fleet):
#   self-hosted (20x8xH100)  ~ $148K/mo flat (reserved capacity)  — $5.7/1K @ 26M req
#   cloud on-demand         ~ $72K/mo (bursts to ~20, runs ~5 avg @ 40% duty) — $2.8/1K
#   managed API             $20.80/1K linear
# These are the corrected FLEET numbers (not the single-host $16.9K/$5.8K from an
# earlier draft). We recompute the self-host-vs-managed break-even against the fleet line.
req = np.logspace(4, 8, 300)
self_host = np.full_like(req, 148000.0)        # ~$148K/mo flat (20-host reserved fleet)
cloud_od  = np.full_like(req, 72000.0)         # ~$72K/mo (cloud, 5-host avg / 40% duty)
managed   = 0.0208 * req                       # $20.80/1K -> linear

fig, ax = plt.subplots(figsize=(9, 6))
ax.loglog(req, self_host, '-', color='#27408b', lw=2.4, label='self-hosted fleet (20×8×H100, ~$148K/mo flat)')
ax.loglog(req, cloud_od, '--', color='#6f9e5f', lw=2.2, label='cloud on-demand (~$72K/mo, 5-host avg/40% duty)')
ax.loglog(req, managed, '-', color='#c0392b', lw=2.4, label='managed API ($20.80/1K, linear)')

ax.set_xlabel('Requests per month (log)')
ax.set_ylabel('Cost per month (USD, log)')
ax.set_title('TCO break-even across the three serve modes (canonical ~20-host fleet)', fontsize=12)
ax.set_xlim(1e4, 1e8); ax.set_ylim(1e3, 1e7)
ax.grid(alpha=0.3, which='both')

# reference lines
ax.axvline(2.6e7, color='#27408b', ls=':', lw=1.4)
ax.text(2.0e7, 2.5e5, 'canonical 26M req/mo', fontsize=8.5, color='#27408b', ha='right')

# break-even self-host fleet vs managed: solve 0.0208*x = 148000
be = 148000 / 0.0208
ax.plot([be], [148000], '*', ms=18, color='#c0392b', mec='#7b241c', zorder=6)
ax.text(be*0.55, 8e5, f'break-even ≈ {be/1e6:.1f}M req/mo\n(self-host fleet vs managed API)', fontsize=9,
        color='#c0392b', fontweight='bold')

# legend OUTSIDE the axes (below), so it does not occlude data
ax.legend(fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=1, frameon=False)

# assumptions in clear space below (leading, not cramped)
ax.text(0.02, -0.24, 'self-hosted flat (reserved capacity, ~20-host fleet); managed API linear (per-request);',
        transform=ax.transAxes, fontsize=8.5, color='#444')
ax.text(0.02, -0.29, 'cloud on-demand @ 40% duty, 5-host average bursting to ~20 — excludes staff/integration (see §16.4).',
        transform=ax.transAxes, fontsize=8.5, color='#6f9e5f')

plt.tight_layout(rect=(0, 0.10, 1, 1))
plt.savefig('design/manuscript/chapter-16/figures/fig-16-1601.png', dpi=150)
plt.close()
print('wrote fig-16-1601 (FLEET-scaled TCO values; recomputed break-even)')
