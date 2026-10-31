"""fig-16-1601 — TCO break-even across three serve modes (Ch 16).

CANONICAL generator for design/manuscript/chapter-16/figures/fig-16-1601.{png,pdf}.

Every number is sourced from the shared root helper `render/tco_model.py` reading
`design/canonical-workload.yaml` — there is NO parallel literal price table here.
All prices are [ILLUSTRATIVE][ASSUMPTION] Q4-2026 scenario values, not market facts.

Values (computed at run time, not stated here):
  self-host      = 21-host ideal-active included cost (capex + energy + staff), flat
  cloud          = default paid-occupancy INPUT (6 x 730 = 4,380 host-hours) — an
                   assumption, NOT a measured duty cycle / load-duration integral
  managed API    = $0.0208/req linear ($20.80/1K)
  break-even     = self / api_per_req, with the $15-25/1K price band

X-AXIS DIMENSION (R04 / F0201) — stated, not implied:
  The x-axis varies (A) served volume through duration / duty-cycle at a FIXED
  40 rps peak and a FIXED 21-host fleet.  It does NOT do (B) — scaling
  average and peak together and re-running N_hosts(volume) with the integer
  slot floor — which would stair-step the self-host line upward instead of
  leaving it flat.  Because the fleet and its cost are frozen, the
  155,816.93 / 0.0208 = 7.49M break-even is a FROZEN-FLEET crossover, not a
  generalized scalable crossover.
  Feasible served-volume bound under (A): 40 rps x 624,000 canonical active
  seconds/month = 24,960,000 = 24.96M requests/month.  The band right of that
  is INFEASIBLE for this frozen fleet; it is shaded and labelled, and the
  feasible-max bound is drawn as a dashed reference.

Print-size authored (6.1 x 5.0 landscape column, US Letter textwidth 439.2pt);
placed labels are >= 8pt. Regenerating this file alone must not reflow anything
else — no global regen is implied or performed.
"""
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as _mt
import matplotlib as _mpl
import numpy as np

# Literal '$' everywhere in this figure: disable mathtext parsing so paired '$'
# cannot enter math mode (which drops spaces), and emit plain '$' — the old
# '\\$' escape rendered a VISIBLE backslash in non-math strings (R23-C16-02).
_mpl.rcParams['text.parse_math'] = False

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'render'))
import tco_model as tm  # noqa: E402  (import-safe, side-effect free)

# ---- root primitives (single source of truth) ----
prim = tm.load_primitives()
prices = tm.validate_prices(prim['tco']['prices'])
sz = prim['tco']['sizing']
cal = prim['tco']['calendar']
occ = prim['tco']['cloud_paid_host_hours']
sc = prim['scenario']

req_month = tm.request_month(sc['avg_rps'], cal['request_hours_per_day'],
                             cal['request_workdays_per_year'],
                             cal['request_months_per_year'])
fleet = tm.fleet_counts(sz['kv_slot_floor_fp16'], sz['w_plan_s'],
                         sc['avg_rps'], sc['peak_rps'])
n_hosts = fleet['n_peak_total']                      # 21, zero spare
billing_h = cal['billing_hours_per_month']           # 730 h (separate calendar)

m1 = tm.self_host_costs(n_hosts, prices, billing_h)
self_total = m1['total']                             # 155,816.93
m2 = tm.cloud_costs(occ['default_assumption'], prices)
cloud_total = m2['total']                            # 87,600 (4,380 host-hours)
m3 = tm.api_costs(prices, req_month, sc['input_tokens'], sc['output_tokens'])
api_per_req = m3['per_req']                          # 0.0208
be = tm.breakeven_vs_api(self_total, prices, api_per_req)

api_lo = prices['api_price_band_lo_usd_per_req']     # 0.015
api_hi = prices['api_price_band_hi_usd_per_req']     # 0.025

# ---- feasible served-volume bound (R04 / F0201) ----------------------------
# Dimension (A): volume moves with duration/duty-cycle at a FIXED 40 rps peak
# and this FIXED fleet.  The canonical active window is 624,000 active
# seconds/month (6,240,000 requests / 10 rps), so the frozen 21-host fleet can
# serve at most 40 x 624,000 = 24,960,000 = 24.96M requests/month.  Right of
# that the plot is INFEASIBLE for this fleet (it would need a re-size, i.e.
# option (B) with N_hosts(volume) stair-stepping the cost).
active_s = req_month / sc['avg_rps']                 # 624,000 active s/month
vol_max = sc['peak_rps'] * active_s                 # 24,960,000 req/month

# ---- plot ----
req = np.logspace(4, 8, 300)
self_host = np.full_like(req, self_total)            # flat: fleet paid regardless
cloud_line = np.full_like(req, cloud_total)          # occupancy-input flat line
managed = api_per_req * req                          # zero-intercept linear
managed_lo = api_lo * req
managed_hi = api_hi * req

fig, ax = plt.subplots(figsize=(6.1, 5.0))
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow
# NOTE on '$': text.parse_math is OFF for this figure (set above), so every '$'
# below renders as a literal dollar glyph — no backslash escapes, no mathtext.
ax.fill_between(req, managed_lo, managed_hi, color='#c0392b', alpha=0.12,
                label='price band $15–25/1K')
ax.loglog(req, managed_lo, ':', color='#c0392b', lw=1.1, alpha=0.9)
ax.loglog(req, managed_hi, ':', color='#c0392b', lw=1.1, alpha=0.9)
ax.loglog(req, self_host, '-', color='#27408b', lw=2.0,
          label=f'self-host ${self_total/1000:.1f}K/mo ({n_hosts} hosts)')
ax.loglog(req, cloud_line, '--', color='#6f9e5f', lw=1.9,
          label=f'cloud ${cloud_total/1000:.1f}K/mo (occupancy input)')
ax.loglog(req, managed, '-', color='#c0392b', lw=2.0,
          label=f'managed ${m3["per_1k"]:.2f}/1K')

# ---- feasible bound + INFEASIBLE band (R04 / F0201) -----------------------
# Drawn at zorder 0 so it sits under every curve, band and reference line.
ax.axvspan(vol_max, 1e8, facecolor='0.55', alpha=0.30, hatch='///',
           edgecolor='0.30', zorder=0)
ax.axvline(vol_max, color='0.30', ls='--', lw=1.4, zorder=5)
# feasible max: box sits well LEFT of the gray bound with a clear horizontal
# leader running right to the bound, so the white face never occludes the dashed
# line and the association is explicit. (R27 P2: the box was floating and its
# white face broke the reference line; a box centred on the line still occluded
# it, so it is offset left with a visible leader.)
ax.annotate('feasible max 24.96M',
            xy=(vol_max, 8.8e6), xytext=(vol_max*0.16, 8.8e6),
            ha='center', va='center', fontsize=8.0, color='0.15', fontweight='bold',
            arrowprops=dict(arrowstyle='-|>', lw=1.2, color='0.15',
                            mutation_scale=10, shrinkA=3, shrinkB=0),
            bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='0.55',
                      lw=0.7, alpha=0.92), zorder=8)
# INFEASIBLE: solid dark leader line from the box down into the hatched region.
ax.annotate('INFEASIBLE\n(> 24.96M)',
            xy=(5.0e7, 1.4e6), xytext=(5.0e7, 3.4e6),
            ha='center', va='center', fontsize=8.2, color='#7b241c',
            fontweight='bold',
            arrowprops=dict(arrowstyle='-|>', lw=1.0, color='0.15',
                            mutation_scale=9, shrinkA=1, shrinkB=1),
            bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='0.45',
                      lw=0.7, alpha=0.92), zorder=8)

ax.set_xlabel('Requests/month (log)', fontsize=9)
ax.set_ylabel('Cost/month (USD, log)', fontsize=9)
ax.set_xlim(1e4, 1e8)
ax.set_ylim(1e3, 1e7)
ax.grid(alpha=0.3, which='both')
ax.xaxis.set_major_formatter(_mt.FuncFormatter(
    lambda v, p: '1e%g' % round(math.log10(v)) if v > 0 else ''))
ax.yaxis.set_major_formatter(_mt.FuncFormatter(
    lambda v, p: '1e%g' % round(math.log10(v)) if v > 0 else ''))
ax.tick_params(labelsize=9)

# reference line: the CANONICAL volume is the business-hours request calendar
# (10 rps x 8 h x 3600 x 260 / 12), NOT a round-the-clock extrapolation. The break-even star
# sits just above it, which is the point: at the canonical volume self-host costs
# more than the managed API on the included-cost lines.
ax.axvline(req_month, color='#27408b', ls=':', lw=1.2)
ax.text(req_month * 0.8, 4.0e5,
        f'canonical {req_month/1e6:.2f}M req/mo',
        fontsize=9, color='#27408b', ha='right')

# break-even self-host fleet vs managed: solve api_per_req * x = self_total
be_mid = be['mid']
be_lo = be['lo']      # crossover at the HIGH end of the price band
be_hi = be['hi']      # crossover at the LOW end of the price band
ax.plot([be_mid], [self_total], '*', ms=11, color='#c0392b', mec='#7b241c', zorder=6)
# sensitivity span: horizontal bracket just ABOVE the self-host line, end-ticks down.
span_y = self_total * 1.12
ax.plot([be_lo, be_hi], [span_y, span_y], '-', color='#c0392b', lw=1.6, zorder=7)
ax.plot([be_lo, be_lo], [self_total, span_y], '-', color='#c0392b', lw=1.0, zorder=7)
ax.plot([be_hi, be_hi], [self_total, span_y], '-', color='#c0392b', lw=1.0, zorder=7)
# break-even annotation: left-middle clear band — below the legend, above the
# self-host line, left of the canonical vline label — so its box intersects no
# legend line, curve, or reference label. The old (1.2e6, 1.2e6) spot collided
# with the legend's third line (R23-C16-02, parent-confirmed). A thin leader
# line now runs from the box to the break-even star (R27 P2: box was floating).
ax.annotate(f'break-even ≈ {be_mid/1e6:.1f}M\n'
            f'sensitivity ≈ {be_lo/1e6:.1f}–{be_hi/1e6:.1f}M\n'
            f'(a region, not a point)',
            xy=(be_mid, self_total), xytext=(6.0e4, 4.2e5),
            ha='center', va='center', fontsize=8.5, color='#c0392b',
            fontweight='bold',
            arrowprops=dict(arrowstyle='-', lw=0.5, color='#c0392b',
                            shrinkA=1, shrinkB=1),
            bbox=dict(boxstyle='round,pad=0.30', fc='white', ec='#c0392b',
                      lw=0.8), zorder=8)

# legend inside top-left (clear of data), assumptions as a compact footer OUTSIDE
ax.legend(fontsize=8.8, loc='upper left', ncol=1, frameon=False,
          handlelength=1.3, labelspacing=0.25, bbox_to_anchor=(0.02, 0.97))
# The x-axis dimension is named ON the axis (R04/F0201): option (A),
# duration/duty-cycle varied at a FIXED 40 rps peak + FIXED 21-host fleet.
ax.set_xlabel('Requests/month (log) — duration varied at FIXED 40 rps peak, '
              'FIXED 21-host fleet', fontsize=9, labelpad=6)
# Header: two fig.text lines with a clear box-gap (va='top', stepped y).
fig.text(0.5, 0.99,
         'ILLUSTRATIVE SCENARIO — NOT APPLES-TO-APPLES (see Table 16-1 / Ch 16)',
         fontsize=8.6, color='#8a3a12', ha='center', va='top', fontweight='bold')
fig.text(0.5, 0.945,
         f'TCO break-even ({n_hosts}-host fleet)',
         fontsize=9.5, color='black', ha='center', va='top')
fig.text(0.11, 0.012,
         f'Assumptions: self-host flat (${self_total/1000:.1f}K/mo, {n_hosts} hosts, '
         f'incl. ${m1["staff"]/1000:.0f}K/mo staff);\n'
         f'cloud ${cloud_total/1000:.1f}K/mo = {m2["paid_host_hours"]:,.0f} paid '
         f'host-hours (occupancy INPUT, not a measured duty cycle).\n'
         f'Sensitivity: a ${api_lo*1000:.0f}–{api_hi*1000:.0f}/1K price band moves '
         f'the break-even to ~{be_lo/1e6:.1f}–{be_hi/1e6:.1f}M req/mo.\n'
         f'x varies duration/duty-cycle at a FIXED {sc["peak_rps"]:.0f} rps peak + '
         f'FIXED {n_hosts}-host fleet (option A),\n'
         f'NOT re-sized per volume: a frozen-fleet cost, not a scalable crossover.\n'
         f'Feasible max = {sc["peak_rps"]:.0f} rps × {active_s:,.0f} active s/mo '
         f'= {vol_max/1e6:.2f}M req/mo; right of it INFEASIBLE.',
         fontsize=8.2, color='#555', ha='left', va='bottom')

plt.subplots_adjust(left=0.13, right=0.97, top=0.90, bottom=0.30)
out_png = REPO / 'design' / 'manuscript' / 'chapter-16' / 'figures' / 'fig-16-1601.png'
out_pdf = out_png.with_suffix('.pdf')
plt.savefig(out_png, dpi=350)
with _mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig(out_pdf, format='pdf')
plt.close()
print(f'wrote fig-16-1601 (self {self_total:.2f}, cloud {cloud_total:.2f} '
      f'@ {m2["paid_host_hours"]:.0f} h, be {be_mid:.2f}, {n_hosts}-host fleet)')