#!/usr/bin/env python3
"""Parametric TCO calculator for From Token to Fleet (Chapter 16).

The durable form of the Chapter 16 TCO worked example: size the fleet FIRST
(N_hosts = max of the throughput, KV, and SLO bounds from Chapter 17/20), then
price each delivery mode on that fleet. Mirrors the book's three modes and its
core thesis: token -> workload -> system -> fleet -> economics.

Run (defaults = the canonical Chapter 16 worked-example values):
    python3 render/tco_calc.py
    python3 render/tco_calc.py --rps-peak 60 --util 0.7
    python3 render/tco_calc.py --no-fp8 --staff-per-year 120000

All money is USD; costs are per 1,000 SLO-meeting requests and/or per month.
Defaults are [2deg DERIVED] illustrative as of Q4 2026 -- re-verify before budgeting.
"""
import argparse
import math


def fmt_usd(x):
    if x >= 1e6:
        return f"${x/1e6:.2f}M"
    if x >= 1e3:
        return f"${x/1e3:.1f}K"
    return f"${x:.2f}"


def main():
    ap = argparse.ArgumentParser(description="Chapter 16 parametric TCO model (fleet-first)")
    ap.add_argument("--rps-avg", type=float, default=10, help="canonical average requests/s")
    ap.add_argument("--rps-peak", type=float, default=40, help="canonical peak requests/s")
    ap.add_argument("--in-tok", type=float, default=9200)
    ap.add_argument("--out-tok", type=float, default=300)
    ap.add_argument("--days", type=float, default=30)

    # Fleet sizing (Chapter 17/20): service time and per-host request concurrency.
    ap.add_argument("--ttft", type=float, default=1.08, help="prefill TTFT (s), canonical Ch8")
    ap.add_argument("--ms-per-tok", type=float, default=25, help="decode ms/token, canonical Ch8")
    ap.add_argument("--kv-bytes-per-tok", type=float, default=2621440,
                    help="per-token KV bytes (canonical 2.62 MB decimal / 2.5 MiB)")
    ap.add_argument("--kv-budget-gb", type=float, default=436, help="KV budget per host (640-140-64)")
    ap.add_argument("--util", type=float, default=1.0,
                    help="fleet capacity utilization target (1.0 = full; 0.7 = headroom)")
    ap.add_argument("--fp8", action="store_true", default=False,
                    help="use FP8 KV (vLLM ~54% of BF16); default is the FP16 baseline. Pass --fp8 to halve the fleet")
    ap.add_argument("--fp8-factor", type=float, default=0.54)
    ap.add_argument("--no-fp8", dest="fp8", action="store_false")
    ap.set_defaults(fp8=False)

    # Mode 1 (self-hosted) -- per 8xH100 server
    ap.add_argument("--capex", type=float, default=350000, help="fully built 8xH100 server")
    ap.add_argument("--dep-years", type=float, default=5)
    ap.add_argument("--usd-per-kwh", type=float, default=0.15)
    ap.add_argument("--staff-per-year", type=float, default=120000)
    ap.add_argument("--gpu-count", type=int, default=8)
    ap.add_argument("--gpu-watt", type=float, default=700, help="per-GPU TDP (W) -> GPU IT load")
    ap.add_argument("--host-other-kw", type=float, default=2.2, help="host/network/other IT load (kW)")
    ap.add_argument("--pue", type=float, default=1.3)
    ap.add_argument("--power-kw", type=float, default=None,
                    help="explicit facility power per host (kW); if unset, derived")

    # Mode 2 (cloud on-demand)
    ap.add_argument("--cloud-usd-per-hr", type=float, default=20.0, help="8xH100 instance ($2.50/GPU-hr x 8)")

    # Mode 3 (managed API)
    ap.add_argument("--api-in-usd-per-1k", type=float, default=0.002)
    ap.add_argument("--api-out-usd-per-1k", type=float, default=0.008)

    a = ap.parse_args()

    req_month = a.rps_avg * 86400 * a.days

    # ---- Step 1: size the fleet (Chapter 17/20), N_hosts = max(throughput, KV, SLO) ----
    service_time = a.ttft + (a.out_tok * a.ms_per_tok / 1000.0)
    kv_gb_per_req = a.kv_bytes_per_tok * (a.in_tok + a.out_tok) / 1e9
    kv_factor = a.fp8_factor if a.fp8 else 1.0
    C = (a.kv_budget_gb * 1e9) / (a.kv_bytes_per_tok * (a.in_tok + a.out_tok)) / kv_factor
    per_host_rps = C / service_time
    N_peak = math.ceil((a.rps_peak * service_time) / (C * a.util))
    N_avg = math.ceil((a.rps_avg * service_time) / (C * a.util))
    n_hosts = N_peak  # provision for peak

    # ---- Step 2: price each mode on n_hosts ----
    # Mode 1: capex+power scale with the fleet; staff is a fixed alloc.
    capex_mon = (a.capex / (a.dep_years * 12)) * n_hosts
    hours_mon = 24 * a.days
    if a.power_kw is None:
        gpu_it_kw = (a.gpu_count * a.gpu_watt) / 1000.0
        a.power_kw = (gpu_it_kw + a.host_other_kw) * a.pue
        power_note = "GPU IT {:.1f} kW + host {:.1f} kW, x PUE {:.2f} /host".format(
            gpu_it_kw, a.host_other_kw, a.pue)
    else:
        power_note = "explicit /host"
    power_mon = a.power_kw * a.usd_per_kwh * hours_mon * n_hosts
    staff_mon = a.staff_per_year / 12
    mode1_total_mon = capex_mon + power_mon + staff_mon
    mode1_cost_1k = mode1_total_mon / req_month * 1000

    # Mode 2: cloud scales with load (burst to peak, run avg). Bill ~ avg instances running.
    eff_instances = N_avg  # sustained average; burst to N_peak at peak
    mode2_mon = a.cloud_usd_per_hr * 24 * a.days * eff_instances
    mode2_cost_1k = mode2_mon / req_month * 1000

    # Mode 3
    per_req = (a.in_tok * a.api_in_usd_per_1k + a.out_tok * a.api_out_usd_per_1k) / 1000
    mode3_mon = per_req * req_month
    mode3_cost_1k = per_req * 1000

    print("=== CHAPTER 16 PARAMETRIC TCO (fleet-first) ===")
    print(f"traffic : {a.rps_avg:.0f} rps avg / {a.rps_peak:.0f} rps peak = {req_month:.0f} req/month")
    print(f"         {a.in_tok:.0f} in + {a.out_tok:.0f} out tokens/req")
    print()
    print("Step 1 -- fleet sizing (Ch 17/20):")
    print(f"  service time W    = {service_time:.2f} s  ({a.ttft:.2f} s prefill + {a.out_tok:.0f} x {a.ms_per_tok:.0f} ms decode)")
    print(f"  KV per request    = {kv_gb_per_req:.2f} GB (FP16) -> {kv_gb_per_req*kv_factor:.2f} GB ({'FP8' if a.fp8 else 'FP16'})")
    print(f"  per-host C        = {C:.0f} concurrent  -> per-host ~{per_host_rps:.2f} req/s")
    print(f"  N_hosts (avg)     = {N_avg}")
    print(f"  N_hosts (peak)    = {N_peak}   (util target {a.util:.0%}) -> provisioning {n_hosts}")
    print()
    print(f"Mode 1 self-hosted ({n_hosts} x 8xH100)")
    print(f"  capex/mo   : {fmt_usd(capex_mon)}")
    print(f"  power/mo   : {fmt_usd(power_mon)}  ({a.power_kw:.1f} kW/host @ ${a.usd_per_kwh}/kWh x {n_hosts} hosts; {power_note})")
    print(f"  staff/mo   : {fmt_usd(staff_mon)}")
    print(f"  total/mo   : {fmt_usd(mode1_total_mon)}")
    print(f"  cost/1K req: {fmt_usd(mode1_cost_1k)}")
    print()
    print(f"Mode 2 cloud on-demand (scale to ~{eff_instances} avg instances, burst to ~{N_peak})")
    print(f"  total/mo   : {fmt_usd(mode2_mon)}")
    print(f"  cost/1K req: {fmt_usd(mode2_cost_1k)}")
    print()
    print("Mode 3 managed API")
    print(f"  total/mo   : {fmt_usd(mode3_mon)}")
    print(f"  cost/1K req: {fmt_usd(mode3_cost_1k)}")
    print()
    if mode3_cost_1k > 0:
        be = mode1_total_mon / per_req
        print(f"self-host breaks even vs API at ~{be:.0f} req/month (~{be/req_month:.1f}x current volume)")


if __name__ == "__main__":
    main()
