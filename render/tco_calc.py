#!/usr/bin/env python3
"""Parametric TCO calculator for From Token to Fleet (Chapter 16).

The durable form of the Chapter 16 TCO worked example: same arithmetic,
with GPU price, electricity, staffing, capacity, and API price as inputs,
so an architect re-runs it with real numbers instead of memorising one
answer. Mirrors the book's three delivery modes.

Run (defaults = the canonical Chapter 16 worked-example values):
    python3 render/tco_calc.py
    python3 render/tco_calc.py --req-per-day 864000 --util 0.8

All money is USD; costs are per 1,000 SLO-meeting requests and/or per month.
Defaults are [2\u00b0 DERIVED] illustrative as of Q4 2026 -- [VERIFY] before budgeting.
"""
import argparse


def fmt_usd(x):
    if x >= 1e6:
        return f"${x/1e6:.2f}M"
    if x >= 1e3:
        return f"${x/1e3:.1f}K"
    return f"${x:.2f}"


def main():
    ap = argparse.ArgumentParser(description="Chapter 16 parametric TCO model")
    ap.add_argument("--req-per-day", type=float, default=864000, help="canonical ~10 rps avg")
    ap.add_argument("--in-tok", type=float, default=9200)
    ap.add_argument("--out-tok", type=float, default=300)
    ap.add_argument("--days", type=float, default=30)

    # Mode 1 (self-hosted)
    ap.add_argument("--capex", type=float, default=350000, help="fully built 8\u00d7H100 server")
    ap.add_argument("--dep-years", type=float, default=5)
    ap.add_argument("--power-kw", type=float, default=50)
    ap.add_argument("--usd-per-kwh", type=float, default=0.15)
    ap.add_argument("--staff-per-year", type=float, default=120000)
    ap.add_argument("--util", type=float, default=1.0, help="self-host on-time duty (1.0 = always on)")

    # Mode 2 (cloud on-demand)
    ap.add_argument("--cloud-usd-per-hr", type=float, default=3.50, help="8\u00d7H100 instance")
    ap.add_argument("--cloud-duty", type=float, default=0.40)

    # Mode 3 (managed API)
    ap.add_argument("--api-in-usd-per-1k", type=float, default=0.002)
    ap.add_argument("--api-out-usd-per-1k", type=float, default=0.008)

    a = ap.parse_args()

    req_month = a.req_per_day * a.days

    # Mode 1
    capex_mon = a.capex / (a.dep_years * 12)
    hours_mon = 24 * a.days * a.util
    power_mon = a.power_kw * a.usd_per_kwh * hours_mon
    staff_mon = a.staff_per_year / 12
    mode1_total_mon = capex_mon + power_mon + staff_mon
    mode1_cost_1k = mode1_total_mon / req_month * 1000

    # Mode 2
    mode2_mon = a.cloud_usd_per_hr * 24 * a.days * a.cloud_duty
    mode2_cost_1k = mode2_mon / req_month * 1000

    # Mode 3
    per_req = (a.in_tok * a.api_in_usd_per_1k + a.out_tok * a.api_out_usd_per_1k) / 1000
    mode3_mon = per_req * req_month
    mode3_cost_1k = per_req * 1000

    print("=== CHAPTER 16 PARAMETRIC TCO ===")
    print(f"traffic : {a.req_per_day:.0f} req/day = {req_month:.0f} req/month")
    print(f"         {a.in_tok:.0f} in + {a.out_tok:.0f} out tokens/req")
    print()
    print("Mode 1 self-hosted (8\u00d7H100, util={:.0%})".format(a.util))
    print(f"  capex/mo   : {fmt_usd(capex_mon)}")
    print(f"  power/mo   : {fmt_usd(power_mon)}  ({a.power_kw} kW @ ${a.usd_per_kwh}/kWh, {hours_mon:.0f} h)")
    print(f"  staff/mo   : {fmt_usd(staff_mon)}")
    print(f"  total/mo   : {fmt_usd(mode1_total_mon)}")
    print(f"  cost/1K req: {fmt_usd(mode1_cost_1k)}")
    print()
    print("Mode 2 cloud on-demand (duty={:.0%})".format(a.cloud_duty))
    print(f"  total/mo   : {fmt_usd(mode2_mon)}")
    print(f"  cost/1K req: {fmt_usd(mode2_cost_1k)}")
    print()
    print("Mode 3 managed API")
    print(f"  total/mo   : {fmt_usd(mode3_mon)}")
    print(f"  cost/1K req: {fmt_usd(mode3_cost_1k)}")
    print()
    # break-even vs API
    if mode3_cost_1k > 0:
        # volume V (req/month) where self-host cost/1k == API cost/1k
        # mode1_total_mon / V *1000 == per_req*1000 -> V = mode1_total_mon/per_req
        be = mode1_total_mon / per_req
        print(f"self-host breaks even vs API at ~{be:.0f} req/month (~{be/req_month:.1f}\u00d7 current volume)")


if __name__ == "__main__":
    main()
