import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as _mt
import matplotlib as _mpl


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

# --- [ILLUSTRATIVE] sensitivity band: managed-API price across a plausible range ---
# The self-host-vs-managed break-even is NOT a single point: it moves with the API
# price the fleet is being compared against. By plotting the band (not one crossover)
# the chart keeps the decision honest about which assumptions it depends on.
api_lo, api_hi = 0.015, 0.025                   # $15/1K .. $25/1K
managed_lo = api_lo * req
managed_hi = api_hi * req

fig, ax = plt.subplots(figsize=(5.6, 11.0))
# [ILLUSTRATIVE] shaded sensitivity band + dotted boundary lines for API price
ax.fill_between(req, managed_lo, managed_hi, color='#c0392b', alpha=0.12,
                label='managed API price band [ILLUSTRATIVE] ($15–25/1K)')
ax.loglog(req, managed_lo, ':', color='#c0392b', lw=1.1, alpha=0.9)
ax.loglog(req, managed_hi, ':', color='#c0392b', lw=1.1, alpha=0.9)
ax.loglog(req, self_host, '-', color='#27408b', lw=2.0, label='self-host fleet (~$148K/mo)')
ax.loglog(req, cloud_od, '--', color='#6f9e5f', lw=1.9, label='cloud on-demand (~$72K/mo)')
ax.loglog(req, managed, '-', color='#c0392b', lw=2.0, label='managed API ($20.80/1K, base)')

ax.set_xlabel('Requests/month (log)', fontsize=9)
ax.set_ylabel('Cost/month (USD, log)', fontsize=9)
ax.set_title('TCO break-even (~20-host fleet)', fontsize=9.0)
ax.set_xlim(1e4, 1e8); ax.set_ylim(1e3, 1e7)
ax.grid(alpha=0.3, which='both')
ax.xaxis.set_major_formatter(_mt.FuncFormatter(lambda v, p: '1e%g' % round(__import__('math').log10(v)) if v>0 else ''))
ax.yaxis.set_major_formatter(_mt.FuncFormatter(lambda v, p: '1e%g' % round(__import__('math').log10(v)) if v>0 else ''))
ax.tick_params(labelsize=9)

# reference lines
ax.axvline(2.6e7, color='#27408b', ls=':', lw=1.2)
ax.text(2.0e7, 2.5e5, 'canonical 26M req/mo', fontsize=10, color='#27408b', ha='right')

# break-even self-host fleet vs managed: solve 0.0208*x = 148000
be = 148000 / 0.0208
# [ILLUSTRATIVE] break-even RANGE across the API-price band (band edges dotted)
be_lo = 148000 / api_hi   # crossover at the HIGH end of the price band
be_hi = 148000 / api_lo   # crossover at the LOW end of the price band
ax.plot([be], [148000], '*', ms=13, color='#c0392b', mec='#7b241c', zorder=6)
ax.plot([be_lo, be_hi], [148000, 148000], '-', lw=1.4, color='#c0392b', alpha=0.8,
        zorder=5, solid_capstyle='round')
ax.text(1.3e4, 6e5,
        f'break-even ≈ {be/1e6:.1f}M req/mo @ $20.80/1K\n'
        f'sensitivity ≈ {be_lo/1e6:.1f}–{be_hi/1e6:.1f}M [ILLUSTRATIVE]',
        fontsize=10, color='#c0392b', fontweight='bold', ha='left', va='bottom')

# legend OUTSIDE the axes (below), single column so it never clips at the right edge
ax.legend(fontsize=8.0, loc='upper center', bbox_to_anchor=(0.5, -0.04), ncol=1, frameon=False,
          handlelength=1.4, labelspacing=0.3)

# assumptions in clear space below the legend (figure-coord, wrapped to the figure width;
# each line verified to fit and not overlap the legend)
fig.text(0.12, 0.156, 'Assumptions: self-host fleet flat (~$148K/mo,\nreserved); cloud on-demand ~$72K/mo @40% duty;\nexcludes staff (§16.4).',
         fontsize=8.5, color='#444', va='top')
fig.text(0.12, 0.110, 'Sensitivity [ILLUSTRATIVE]: a $15–25/1K price band\nmoves the break-even (shown at 7.1M req/mo) to\n~5.9–9.9M; the decision is assumption-dependent, not\na single point.',
         fontsize=8.5, color='#c0392b', va='top')

# explicit margins (tight_layout can't satisfy outside-axes legend + footer; set manually)
plt.subplots_adjust(left=0.12, right=0.97, top=0.90, bottom=0.26)
plt.savefig('design/manuscript/chapter-16/figures/fig-16-1601.png', dpi=150)
plt.close()
print('wrote fig-16-1601 (FLEET-scaled TCO values; recomputed break-even)')
