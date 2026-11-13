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
residual is ~6.0 req/s.

P1-02 (review 2026-11-01): every capacity line is an IDEAL ρ = 1 analytical service ceiling,
not an SLO claim. The N-1 = 3 residual (~6.0) clears the ~5.5 req/s burst ONLY at ρ = 1:
at ρ = 0.85 (the low end of the book's LB range) 3 x 2.0 x 0.85 = 5.1 req/s, BELOW the
burst, and the residual only clears it for rho >= 5.5/(3 x 2.0) = 0.9167. The figure
therefore draws the ρ = 0.85 residual line as well and labels the ideal lines as ρ = 1.
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
# Single-line direct label for the one-host bound, placed ABOVE the dashed
# y=2 line at the RIGHT end of the axes, where the red burst curve has already
# dropped away (t ends at x=10) -- so nothing crowds it and it sits fully inside
# the axes. The old two-line form (va='top' at y=1.78) pushed its second line
# BELOW the y=0 axis line and into the tick row: the base-region collision.
ax.text(11.3, host_cap+0.30, 'one host ~2.0 req/s', fontsize=8, color='#666',
        ha='right', va='bottom')
ax.axhline(N1res, color='#e67e22', ls=':', lw=2.0)
# P1-02: robust lower bound at the low end of the book's LB range (rho=0.85):
# 3 surviving hosts x 2.0 x 0.85 = 5.1 req/s, BELOW the ~5.5 burst. Drawn as a thin
# dash-dot line labelled at the RIGHT end (x=11.3), where the burst curve has dropped
# away, so it cannot collide with the hump or with the N-1 label on the left.
N1res_085 = 3 * host_cap * 0.85       # ~5.1 (ρ = 0.85)
ax.axhline(N1res_085, color='#e67e22', ls='-.', lw=1.2, alpha=0.9)
# N-1 residual label lifted clear ABOVE its dotted line so the line no longer
# cuts through the text (previously y = 6.2 against the y=6 line).
ax.text(0.9, N1res+0.72, 'N-1 residual (~6.0 ideal, ρ = 1)', fontsize=8,
        color='#b5590a', ha='left', fontweight='bold')
# FIG17.1-GRAY-01: the N = 4 line/legend sample is a LONG dash so all four
# legend samples are unique by style alone in grayscale (vs the solid burst).
ax.axhline(N4, color='#3a6ea5', ls=(0, (7, 2)), lw=1.8)
# N = 4 label lifted clear ABOVE its line and the green headroom band top.
# Two lines (bottom-anchored) so the label stays LEFT of the italic note box
# (its one-line form ran under the box and got faded by the box's white fill).
ax.text(0.4, N4+0.55, 'N = 4 fleet (3 working\n+ 1 reserve, ~8.0, ideal)', fontsize=8, color='#27408b',
        ha='left', va='bottom', fontweight='bold')

# Burst-peak call-out. The old label (xytext=(4.5,4.4), ha='left') was ~3 units
# wide and sat exactly where the hump rises, so the CURVE ran straight through
# the text and its leader. Moved ABOVE the hump into the empty band between the
# N-1 line (y=6) and the 'N = 4 capacity' label -- clear of the curve, of the
# 'N-1 residual' label (which ends at x~5.4) and of the headroom/failover
# labels (x >= 10) -- with a short leader dropping to the apex.
ax.annotate('burst peak ~5.5 req/s',
            xy=(6.3, peak), xytext=(6.4, 6.85),
            fontsize=8, color='#c0392b', ha='left', va='center',
            fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.2))
# Single-host note in the lower-left, pointing at the curve where the one-host
# bound (~2.0) first falls far below the rising burst.
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
ax.text(bx+0.3, peak - 1.15, 'failover', fontsize=8, color='#27408b',
        ha='left', va='center', fontweight='bold')
ax.text(bx+0.3, (N1res+N4)/2, 'headroom', fontsize=8, color='#1e6b3a',
        ha='left', va='center', fontweight='bold')

ax.set_xlabel('time of day (h, schematic)', fontsize=9)
ax.set_ylabel('load / capacity (req·s⁻¹)', fontsize=9)
# P0-04 (review): the title must not be clipped at the printed column width.
# Use a SHORT two-line title (the full qualifier lives in the caption), sized
# so it always fits within the axes width at column scale.
ax.set_title('Sizing a fleet of one model\n'
             '(ideal ρ = 1 analytical ceilings; small ~5.5 req/s burst)',
             fontsize=9.5, fontweight='bold')
# T-02 (review): the smooth curve is *offered-load capacity*, not a queueing
# proof. Note rendered as two centered lines INSIDE the axes (top, empty region
# above y=8) so bbox_inches='tight' cannot clip it and it stays clear of the
# '12' tick and the top border. Font sized down so it fits the plot width.
# P1 (review nov1e): the threshold symbol is written as matplotlib mathtext
# r'$\geq$' (a real >= glyph from the embedded DejaVu subset), never as a raw
# U+2265/U+2273 text char, so no notdef/tofu box can reach the figure PDF.
ax.text(0.975, 0.985,
        'Ideal ρ = 1 analytical ceiling \u2014 no SLO claim.\n'
        'N-1 clears the burst only at ρ = 1:\n'
        'at ρ = 0.85 the residual = ~5.1 < ~5.5, need $\\geq$ 0.917.',
        transform=ax.transAxes, fontsize=8.6, color='#444', ha='right', va='top',
        style='italic', linespacing=1.05,
        bbox=dict(boxstyle='round,pad=0.10', fc='white', ec='none', alpha=0.85))
ax.set_yticks([0, 2, 4, 6, 8, 10, 12])
ax.grid(alpha=0.25, axis='y')
# FIG17.1-GRAY-01: N = 4 sample/line is a long dash and the handle is 3.0 em
# long so the dash GAP is actually visible inside the legend sample — all four
# legend samples are then unique by style alone in grayscale.
ax.legend(handles=[Line2D([], [], color='#c0392b', lw=2),
                   Line2D([], [], color='#8a8a8a', ls='--', lw=1.4),
                   Line2D([], [], color='#3a6ea5', ls=(0, (7, 2)), lw=1.8),
                   Line2D([], [], color='#e67e22', ls=':', lw=2)],
          labels=['offered load (burst)', 'one host bound (~2.0, ideal)',
                  'N = 4 fleet capacity (~8.0, ideal)', 'N-1 residual (1 host drains, ideal)'],
          fontsize=8.0, loc='upper center', bbox_to_anchor=(0.5, -0.42),
          ncol=2, frameon=False, handlelength=3.0)
plt.tight_layout(rect=(0, 0, 1, 0.93))
plt.savefig('design/manuscript/chapter-17/figures/fig-17-1701.png', dpi=400,
            bbox_inches='tight', pad_inches=0.05)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-17/figures/fig-17-1701.pdf', format='pdf')
plt.close()
print('fig-17-1701 (burst + failure capacity)')
