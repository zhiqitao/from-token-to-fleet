#!/usr/bin/env python3
"""Fig 17.1: burst and failure capacity of a fleet of one model.

The Archify 'fleet-hierarchy' figure showed only the LB->N-hosts fan-out topology —
the same composition as Fig 10.1 — and conveyed none of the *capacity* content the
caption promises (sizing above peak, N-1 residual after a host drains). This matplotlib
redesign shows the actual argument: offered load ramps toward a burst peak; a single
host's ~2.0 req/s analytical planning bound is far below it; the fleet must be sized ABOVE peak;
and if one host drains (health-check fail) the N-1 residual must still clear the burst.

Canonical numbers (frozen): per-host ~2.0 req/s analytical planning bound (C/W = 17.5/8.6);
N = 4 in the canonical scenario (aggregate ~8.0 req/s); after one host drains, the N-1 = 3
residual is ~6.0 req/s, still above the ~5.5 req/s burst peak.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

fig, ax = plt.subplots(figsize=(6.1, 3.7))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.set_xlim(0, 11.6); ax.set_ylim(0, 12.0)

# Time axis (hours of a workday); offered load follows a smooth burst.
t = np.linspace(0, 10, 300)
offered = 1.9 + 3.6*np.exp(-((t-6.3)**2)/2.0)
peak = offered.max()                       # ~5.5 req/s

host_cap = 2.0                             # one host analytical planning bound (C/W = 17.5/8.6 ≈ 2.0)

# Reference capacity levels (at the analytical per-host bound).
N4 = 4 * host_cap          # ~8.0
N1res = 3 * host_cap       # ~6.0  (one host drains)

# Offered load burst.
ax.fill_between(t, 0, offered, color='#c0392b', alpha=0.14)
ax.plot(t, offered, color='#c0392b', lw=2.0, label='offered load (burst)')

# Reference lines.
ax.axhline(host_cap, color='#8a8a8a', ls='--', lw=1.4)
ax.text(9.5, host_cap-0.22, 'one host\n~2.0 req/s', fontsize=8, color='#666',
        ha='right', va='top')
ax.axhline(N1res, color='#e67e22', ls=':', lw=2.0)
ax.text(0.9, N1res+0.20, 'N-1 residual (~6.0, 1 host drains)', fontsize=8,
        color='#b5590a', ha='left', fontweight='bold')
ax.axhline(N4, color='#3a6ea5', lw=1.8)
ax.text(0.9, N4+0.20, 'N = 4 fleet capacity (~8.0)', fontsize=8, color='#27408b',
        ha='left', fontweight='bold')

# Call-outs in clear whitespace. The burst label + pointer sit BELOW the
# orange dotted N-1 line (y=6) and LEFT of the grey failover brace (x=9.7) so
# neither crosses them; the pointer runs up to the peak from below. va='bottom'
# keeps the text top clearly under y=6 and clear of the 'N-1 residual' label.
ax.annotate('burst peak ~5.5 req/s',
            xy=(6.3, peak), xytext=(4.5, 4.4),
            fontsize=8, color='#c0392b', ha='left', va='bottom',
            fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#c0392b'))
# Single-host note moved to the lower-left, pointing at the curve where the
# one-host bound (~2.0) first falls far below the rising burst.
ax.annotate('one host cannot meet\nthe burst on its own',
            xy=(3.4, host_cap+0.05), xytext=(0.7, 2.75),
            fontsize=8, color='#555', ha='left', va='bottom',
            arrowprops=dict(arrowstyle='->', color='#555'))

# Distinguish headroom vs failover (v8 review: the combined "(headroom +
# failover)" annotation lumped them). The failover margin (burst peak 5.5 ->
# N-1 residual 6.0) is only ~0.5 req/s, too thin to shade, so a right-side
# vertical brace spans the whole margin (5.5 -> 8.0) with a tick at 6.0; the
# two labels sit to the RIGHT of the brace, clear of the reference lines.
ax.axhspan(N1res, N4, color='#2c7a4b', alpha=0.16)   # headroom band (visible)
bx = 9.7
ax.plot([bx, bx], [peak, N4], color='#555', lw=1.2)   # brace
ax.plot([bx-0.15, bx+0.15], [N1res, N1res], color='#555', lw=1.2)  # tick at N-1
ax.text(bx+0.3, (peak+N1res)/2, 'failover', fontsize=8, color='#27408b',
        ha='left', va='center', fontweight='bold')
ax.text(bx+0.3, (N1res+N4)/2, 'headroom', fontsize=8, color='#1e6b3a',
        ha='left', va='center', fontweight='bold')

ax.set_xlabel('time of day', fontsize=9)
ax.set_ylabel('offered load / req·s⁻¹', fontsize=9)
# P2-04 (review): the 5.5-rps burst is a small illustrative example, NOT the
# canonical 40-rps workload — make that explicit in the title so it is not
# misread from a screenshot.
ax.set_title('Sizing a fleet of one model (small illustrative ~5.5-rps burst, '
             'NOT the canonical 40-rps workload): burst peak, headroom, failover',
             fontsize=10, fontweight='bold')
# T-02 (review): the smooth curve is *offered-load capacity*, not a queueing
# proof. Note rendered as two centered lines INSIDE the axes (top, empty region
# above y=8) so bbox_inches='tight' cannot clip it and it stays clear of the
# '12' tick and the top border. Font sized down so it fits the plot width.
ax.text(0.5, 0.985,
        'Offered-load capacity only \u2014 not a proof of p99 TTFT/TPOT;\n'
        'tail latency needs a measured queueing model (Ch 14)',
        transform=ax.transAxes, fontsize=7.0, color='#444', ha='center', va='top',
        style='italic', bbox=dict(boxstyle='round,pad=0.20', fc='white', ec='none', alpha=0.85))
ax.set_yticks([0, 2, 4, 6, 8, 10, 12])
ax.grid(alpha=0.25, axis='y')
ax.legend(handles=[Line2D([], [], color='#c0392b', lw=2),
                   Line2D([], [], color='#8a8a8a', ls='--', lw=1.4),
                   Line2D([], [], color='#3a6ea5', lw=1.8),
                   Line2D([], [], color='#e67e22', ls=':', lw=2)],
          labels=['offered load (burst)', 'one host bound (~2.0)',
                  'N = 4 fleet capacity (~8.0)', 'N-1 residual (1 host drains)'],
          fontsize=8.0, loc='lower center', bbox_to_anchor=(0.5, -0.52), ncol=2, frameon=False)
plt.tight_layout(rect=(0, 0, 1, 0.93))
plt.savefig('design/manuscript/chapter-17/figures/fig-17-1701.png', dpi=200,
            bbox_inches='tight', pad_inches=0.05)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-17/figures/fig-17-1701.pdf', format='pdf')
plt.close()
print('fig-17-1701 (burst + failure capacity)')
