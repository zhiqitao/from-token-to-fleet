#!/usr/bin/env python3
"""Parametric TCO calculator for From Token to Fleet (Chapter 16).

Fleet-first: size the fleet from the KV-residency / service-time SCREEN
(Chapter 17/20), then price each delivery mode on that fleet.  Mirrors the
book's three modes and its core thesis: token -> workload -> system -> fleet ->
economics.

Every default primitive is read from ``design/canonical-workload.yaml`` via
``render/tco_model.py`` -- the single machine-readable home; no parallel
literal tables live here.  ``--primitives PATH`` points the whole calculation
at an alternate canonical YAML (isolated single-source fixture).

Screens, not guarantees: the host counts below are KV-residency / service-time
SCREENS.  They are NOT measured SLO-goodput, not a proven maximum of
independent compute/queueing bounds, and measured engine allocation, compute
and goodput are absent.  Nothing here promises an SLO-meeting output, a
portable fleet size, or that FP8 halves a real deployment.

Calendars are SEPARATE inputs: the business-hours request calendar sets request
volume; the 730 h/month billing/energy calendar sets energy and cloud billing.
Cloud paid host-hours are an independent illustrative occupancy input -- never
inferred from the request calendar, never a trace-derived integral, never a
guaranteed lower bound, never a measured duty cycle.

All money is USD; costs are per 1,000 requests and/or per month.  Every price
is ``[ILLUSTRATIVE][ASSUMPTION]`` Q4-2026 scenario data -- not a market quote.
Re-verify before budgeting.  Unpriced external items (rack / external network
/ site) are declared exclusions; this model totals included illustrative lines
only and is not procurement-complete.

Run (defaults = the canonical Chapter 16 worked-example values):
    python3 render/tco_calc.py
    python3 render/tco_calc.py --json
    python3 render/tco_calc.py --rps-peak 60 --util 0.7 --spare 1
    python3 render/tco_calc.py --fp8 --util 0.95
    python3 render/tco_calc.py --paid-host-hours 1000
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tco_model as tm  # noqa: E402  (path set above; import is side-effect free)


def fmt_usd(x):
    if x >= 1e6:
        return "$%.2fM" % (x / 1e6)
    if x >= 1e3:
        return "$%.1fK" % (x / 1e3)
    return "$%.2f" % x


def build_parser(doc):
    sc = doc["scenario"]
    lat = doc["latency_and_throughput"]
    eq = doc["equations"]
    hw = doc["hardware"]
    siz = doc["tco"]["sizing"]
    cal = doc["tco"]["calendar"]

    ap = argparse.ArgumentParser(
        description="Chapter 16 parametric TCO model (fleet-first)")
    ap.add_argument("--primitives", default=None,
                    help="path to an alternate canonical YAML (isolated single-source fixture)")
    ap.add_argument("--rps-avg", type=float, default=float(sc["avg_rps"]),
                    help="canonical average requests/s")
    ap.add_argument("--rps-peak", type=float, default=float(sc["peak_rps"]),
                    help="canonical peak requests/s")
    ap.add_argument("--in-tok", type=float, default=float(sc["input_tokens"]))
    ap.add_argument("--out-tok", type=float, default=float(sc["output_tokens"]))

    # Request calendar (SEPARATE from the billing/energy calendar).
    ap.add_argument("--req-hours-per-day", type=float,
                    default=float(cal["request_hours_per_day"]),
                    help="business-hours REQUEST calendar hours per day")
    ap.add_argument("--req-workdays", type=float,
                    default=float(cal["request_workdays_per_year"]),
                    help="business-hours REQUEST calendar workdays per year")
    ap.add_argument("--req-months", type=float,
                    default=float(cal["request_months_per_year"]),
                    help="months per year used to average the request calendar")
    ap.add_argument("--billing-hours", type=float,
                    default=float(cal["billing_hours_per_month"]),
                    help="SEPARATE billing/energy calendar hours per month")

    # Fleet sizing (Chapter 17/20): service time and per-host request concurrency.
    ap.add_argument("--ttft", type=float, default=float(lat["ttft_s"]),
                    help="prefill TTFT (s), canonical Ch8")
    ap.add_argument("--ms-per-tok", type=float,
                    default=float(lat["tpot_ms_per_token"]),
                    help="decode ms/token, canonical Ch8")
    ap.add_argument("--kv-bytes-per-tok", type=float,
                    default=float(eq["kv_per_token_bytes"]),
                    help="per-token KV bytes (canonical 2.62 MB decimal / 2.5 MiB)")
    ap.add_argument("--kv-budget-gb", type=float, default=float(hw["kv_budget_gb"]),
                    help="KV budget per host (640-140-64)")
    ap.add_argument("--util", type=float, default=1.0,
                    help="fleet capacity utilization target (1.0 = full; 0.7 = headroom)")
    ap.add_argument("--spare", type=int, default=int(siz["headline_spares"]),
                    help="reserve hosts added ON TOP of the serving bound; a reserve "
                         "never contributes serving capacity")
    ap.add_argument("--fp8", action="store_true", default=False,
                    help="use FP8 KV; default is the FP16 baseline")
    ap.add_argument("--no-fp8", dest="fp8", action="store_false")
    ap.add_argument("--fp8-factor", type=float,
                    default=float(siz["kv_raw_byte_factor_fp8"]),
                    help="FP8 KV byte factor vs FP16; the canonical default is raw "
                         "tensor byte-halving. A custom value is a USER-SUPPLIED "
                         "scenario coefficient, never a vendor-measured footprint")
    ap.set_defaults(fp8=False)
    ap.add_argument("--w-mode", choices=("plan", "exec"),
                    default=str(siz["w_default_mode"]),
                    help="service time driving sizing: plan (rounded) or exec (unrounded)")
    ap.add_argument("--w-plan", type=float, default=float(siz["w_plan_s"]),
                    help="ROUNDED planning service time W (s) -- canonical default")
    ap.add_argument("--w-exec", type=float, default=None,
                    help="explicit override of UNROUNDED execution estimate W (s); "
                         "otherwise derived from TTFT + output tokens x decode time")

    # Mode 1 (self-hosted) -- per 8xH100 server.
    # EVERY default below is read from the canonical YAML (single machine-readable
    # home); no price is restated here as a literal.
    pr = doc["tco"]["prices"]
    ap.add_argument("--capex", type=float, default=float(pr["host_capex_usd"]),
                    help="fully built 8xH100 server")
    ap.add_argument("--dep-years", type=float,
                    default=float(pr["depreciation_years"]))
    ap.add_argument("--usd-per-kwh", type=float, default=float(pr["usd_per_kwh"]))
    ap.add_argument("--staff-per-year", type=float,
                    default=float(pr["staff_usd_per_year"]))
    ap.add_argument("--gpu-count", type=int, default=int(pr["gpus_per_host"]))
    ap.add_argument("--gpu-watt", type=float, default=float(pr["gpu_watt"]),
                    help="per-GPU TDP (W) -> GPU IT load")
    ap.add_argument("--host-other-kw", type=float,
                    default=float(pr["host_other_kw"]),
                    help="host/network/other IT load (kW)")
    ap.add_argument("--pue", type=float, default=float(pr["pue"]))
    ap.add_argument("--power-kw", type=float, default=None,
                    help="explicit facility power per host (kW); if unset, derived")

    # Mode 2 (cloud on-demand)
    ap.add_argument("--cloud-usd-per-hr", type=float,
                    default=float(pr["cloud_usd_per_host_hour"]),
                    help="8xH100 instance hourly price")
    ap.add_argument("--paid-host-hours", type=float, default=None,
                    help="explicit cloud paid host-hours (occupancy input; "
                         "independent of the request calendar)")
    ap.add_argument("--cloud-hosts", type=int, default=None,
                    help="always-on cloud hosts -> N x billing hours "
                         "(continuous-traffic alternative)")

    # Mode 3 (managed API)
    ap.add_argument("--api-in-usd-per-1k", type=float,
                    default=float(pr["api_in_usd_per_1k"]))
    ap.add_argument("--api-out-usd-per-1k", type=float,
                    default=float(pr["api_out_usd_per_1k"]))

    ap.add_argument("--json", action="store_true",
                    help="emit machine-readable JSON only (no human text)")
    return ap


def compute(a, doc):
    cal = doc["tco"]["calendar"]
    pr = doc["tco"]["prices"]
    siz = doc["tco"]["sizing"]

    for name, value in (("input tokens", a.in_tok), ("output tokens", a.out_tok),
                        ("TTFT", a.ttft), ("decode ms/token", a.ms_per_tok)):
        if not math.isfinite(value) or value < 0.0:
            raise tm.PrimitiveError("%s must be finite and >= 0 (got %r)" % (name, value))

    req_month = tm.request_month(
        a.rps_avg, a.req_hours_per_day, a.req_workdays, a.req_months)
    billing_hours = a.billing_hours
    if not math.isfinite(billing_hours) or billing_hours <= 0:
        raise tm.PrimitiveError(
            "billing hours per month must be > 0 (got %r)" % (billing_hours,))
    request_active_hours = (a.req_hours_per_day * a.req_workdays / a.req_months)

    w_exec_derived = a.ttft + (a.out_tok * a.ms_per_tok / 1000.0)
    w_exec = w_exec_derived if a.w_exec is None else a.w_exec
    w_used = a.w_plan if a.w_mode == "plan" else w_exec

    kv_factor = a.fp8_factor if a.fp8 else 1.0
    c_floor = tm.kv_slot_floor(
        a.kv_budget_gb, a.kv_bytes_per_tok, a.in_tok + a.out_tok, kv_factor)
    fleet = tm.fleet_counts(c_floor, w_used, a.rps_avg, a.rps_peak,
                            util=a.util, spare=a.spare)
    fleet.update({
        "screen": siz["screen_label"],
        "w_plan_s": a.w_plan,
        "w_exec_s": w_exec,
        "w_exec_basis": "TTFT + output tokens x decode time" if a.w_exec is None else "explicit --w-exec override",
        "w_exec_derived_s": w_exec_derived,
        "w_used_s": w_used,
        "w_mode": a.w_mode,
        "kv_bytes_per_tok": a.kv_bytes_per_tok,
        "kv_budget_gb": a.kv_budget_gb,
        "kv_request_tokens": a.in_tok + a.out_tok,
        "kv_factor": kv_factor,
        "fp8": bool(a.fp8),
        "declared_floor_fp16": siz["kv_slot_floor_fp16"],
        "declared_floor_fp8": siz["kv_slot_floor_fp8"],
    })
    n_hosts = fleet["n_peak_total"]

    prices = dict(pr)
    prices.update({
        "host_capex_usd": a.capex,
        "depreciation_years": a.dep_years,
        "gpus_per_host": a.gpu_count,
        "gpu_watt": a.gpu_watt,
        "host_other_kw": a.host_other_kw,
        "pue": a.pue,
        "usd_per_kwh": a.usd_per_kwh,
        "staff_usd_per_year": a.staff_per_year,
        "cloud_usd_per_host_hour": a.cloud_usd_per_hr,
        "api_in_usd_per_1k": a.api_in_usd_per_1k,
        "api_out_usd_per_1k": a.api_out_usd_per_1k,
    })
    tm.validate_prices(prices)

    if a.power_kw is None:
        power_kw_host = None
        power_note = "GPU IT %.1f kW + host %.1f kW, x PUE %.2f /host" % (
            (a.gpu_count * a.gpu_watt) / 1000.0, a.host_other_kw, a.pue)
    else:
        power_kw_host = a.power_kw
        power_note = "explicit /host"

    mode1 = tm.self_host_costs(n_hosts, prices, billing_hours, power_kw_host)
    mode1["per_1k"] = mode1["total"] / req_month * 1000.0
    mode1["power_note"] = power_note
    mode1["spare_hosts"] = fleet["spare_hosts"]
    mode1["serving_hosts"] = fleet["n_peak_serving"]

    # Mode 2: paid host-hours are an INDEPENDENT occupancy input, never
    # inferred from the business-hours request calendar.
    if a.paid_host_hours is not None and a.cloud_hosts is not None:
        raise tm.PrimitiveError(
            "--paid-host-hours and --cloud-hosts are mutually exclusive occupancy inputs")
    if a.paid_host_hours is not None:
        paid_host_hours = a.paid_host_hours
        occupancy = "explicit --paid-host-hours"
    elif a.cloud_hosts is not None:
        if a.cloud_hosts < 0:
            raise tm.PrimitiveError(
                "--cloud-hosts must be >= 0 (got %r)" % (a.cloud_hosts,))
        paid_host_hours = a.cloud_hosts * billing_hours
        occupancy = "always-on %d hosts x billing hours" % a.cloud_hosts
    else:
        paid_host_hours = fleet["n_avg"] * billing_hours
        occupancy = "default occupancy N_avg(%d) x billing hours" % fleet["n_avg"]

    mode2 = tm.cloud_costs(paid_host_hours, prices)
    mode2["n_hosts"] = (None if a.paid_host_hours is not None else
                        a.cloud_hosts if a.cloud_hosts is not None else fleet["n_avg"])
    mode2["occupancy_basis"] = occupancy
    mode2["per_1k"] = mode2["total"] / req_month * 1000.0
    mode2["basis"] = doc["tco"]["cloud_paid_host_hours"]["status"]
    mode2["continuous_alternative"] = (
        "Continuous-traffic alternative: --cloud-hosts N bills N x billing_hours "
        "always-on (%d -> %s h -> %s USD/month). Request-active hours "
        "and billed hours are distinct state variables; the default occupancy leg "
        "is independent of the request calendar." % (
            n_hosts, format(n_hosts * billing_hours, ',g'),
            format(n_hosts * billing_hours * prices['cloud_usd_per_host_hour'], ',g')))

    mode3 = tm.api_costs(prices, req_month, a.in_tok, a.out_tok)
    be = tm.breakeven_vs_api(mode1["total"], prices, mode3["per_req"])

    calendar = {
        "request_rps_avg": a.rps_avg,
        "hours_per_day": a.req_hours_per_day,
        "workdays_per_year": a.req_workdays,
        "months_per_year": a.req_months,
        "requests_per_month": req_month,
        "request_active_hours_per_month": request_active_hours,
        "billing_hours_per_month": billing_hours,
        "billing_calendar_note": cal["billing_calendar_note"],
    }

    return {
        "status": doc["tco"]["status"],
        "primitives": _rel(tm.DEFAULT_PRIMITIVES_PATH),
        "calendar": calendar,
        "fleet": fleet,
        "mode1_self_host": mode1,
        "mode2_cloud": mode2,
        "mode3_api": mode3,
        "breakeven_vs_api": be,
        "exclusions": doc["tco"]["exclusions"],
    }


def _rel(path):
    path = os.path.abspath(str(path))
    try:
        return os.path.relpath(path, tm.REPO_ROOT)
    except ValueError:
        return path


def render_human(res, a):
    cal = res["calendar"]
    f = res["fleet"]
    m1 = res["mode1_self_host"]
    m2 = res["mode2_cloud"]
    m3 = res["mode3_api"]
    be = res["breakeven_vs_api"]
    kv_fp16 = f["kv_bytes_per_tok"] * f["kv_request_tokens"] / 1e9
    print("=== CHAPTER 16 PARAMETRIC TCO (fleet-first) ===")
    print("status: %s" % res["status"])
    print("traffic : %s rps avg / %s rps peak = %s req/month" % (
        cal["request_rps_avg"], a.rps_peak, cal["requests_per_month"]))
    print("         %s in + %s out tokens/req" % (a.in_tok, a.out_tok))
    print("         request calendar %s h/day x %s workdays/%s = %.1f request-active h/month" % (
        cal["hours_per_day"], cal["workdays_per_year"],
        cal["months_per_year"],
        cal["request_active_hours_per_month"]))
    print("         billing calendar %s h/month (SEPARATE input)" % (
        cal["billing_hours_per_month"],))
    print()
    print("Step 1 -- fleet sizing (Ch 17/20):")
    print("  SCREEN            : %s" % f["screen"])
    print("  W_plan (rounded)  : %.2f s   W_exec (unrounded) : %.2f s  (derived %.2f s)" % (
        f["w_plan_s"], f["w_exec_s"], f["w_exec_derived_s"]))
    print("  W used            : %.2f s  (mode=%s)" % (f["w_used_s"], f["w_mode"]))
    print("  KV per request    : %.2f GB (FP16) -> %.2f GB (%s)" % (
        kv_fp16, kv_fp16 * f["kv_factor"], "FP8" if f["fp8"] else "FP16"))
    print("  hard-slot floor C : %d  (FLOOR before util and host ceil)" % f["kv_slot_floor"])
    print("  per-host rate     : %.6f req/s" % f["per_host_rps"])
    print("  N_hosts (avg)     : %d" % f["n_avg"])
    print("  N_hosts (peak)    : %d serving + %d spare = %d   (util target %.0f%%)" % (
        f["n_peak_serving"], f["spare_hosts"], f["n_peak_total"], f["util"] * 100))
    print()
    print("Mode 1 self-hosted (%d x 8xH100)" % m1["n"])
    print("  capex/mo   : %s" % fmt_usd(m1["capex"]))
    print("  power/mo   : %s  (%.2f kW/host; %s)" % (
        fmt_usd(m1["power"]), m1["power_kw_host"], m1["power_note"]))
    print("  staff/mo   : %s" % fmt_usd(m1["staff"]))
    print("  total/mo   : %s" % fmt_usd(m1["total"]))
    print("  cost/1K req: %s" % fmt_usd(m1["per_1k"]))
    print()
    print("Mode 2 cloud (%s paid host-hours, independent of the request calendar)" % (
        m2["paid_host_hours"],))
    print("  occupancy  : %s" % m2["occupancy_basis"])
    print("  total/mo   : %s" % fmt_usd(m2["total"]))
    print("  cost/1K req: %s" % fmt_usd(m2["per_1k"]))
    print()
    print("Mode 3 managed API")
    print("  total/mo   : %s" % fmt_usd(m3["month"]))
    print("  cost/1K req: %s" % fmt_usd(m3["per_1k"]))
    print()
    print("self-host breaks even vs API at ~%s req/month (band %s - %s)" % (
        be["mid"], be["lo"], be["hi"]))
    print()
    print("Exclusions / unknowns (unpriced, not included):")
    for e in res["exclusions"]:
        print("  - %s" % e)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    boot = argparse.ArgumentParser(add_help=False)
    boot.add_argument("--primitives", default=None)
    try:
        pre, _ = boot.parse_known_args(argv)
        doc = tm.load_primitives(pre.primitives)
    except tm.PrimitiveError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    ap = build_parser(doc)
    a = ap.parse_args(argv)
    if pre.primitives is not None:
        a.primitives = pre.primitives
    try:
        res = compute(a, doc)
    except tm.PrimitiveError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    if a.primitives is not None:
        res["primitives"] = _rel(a.primitives)
    if a.json:
        print(json.dumps(res, indent=2, sort_keys=False))
    else:
        render_human(res, a)
    return 0


if __name__ == "__main__":
    sys.exit(main())