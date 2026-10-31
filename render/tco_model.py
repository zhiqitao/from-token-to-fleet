#!/usr/bin/env python3
"""Pure, import-safe shared fleet-sizing + TCO model (single source of truth).

Every default primitive is read from ``design/canonical-workload.yaml`` -- the
ONE machine-readable home -- via :func:`load_primitives`.  Scripts, figures and
tests must not re-state these as fresh parallel literal tables.

Importing this module is SIDE-EFFECT FREE: no printing, no file writes, no
argument parsing, no environment mutation.

Fixed policy conventions (not questions):
  * Hard-slot KV floor: ``floor()`` BEFORE any utilization adjustment and
    BEFORE the host ceil.  A hard "full requests that fit" ceiling must never
    round up from a non-integer quotient.
  * ``W_plan = 8.6 s`` (rounded planning time) is the DEFAULT sizing input;
    ``W_exec = 8.58 s`` (1.08 + 300 x 0.025, unrounded execution estimate) is
    exposed and labeled, never silently substituted.
  * The business-hours REQUEST calendar and the 730 h/month BILLING/energy
    calendar are SEPARATE inputs.
  * Cloud paid host-hours are an independent illustrative occupancy input --
    never inferred from the request calendar.
  * All prices are ``[ILLUSTRATIVE][ASSUMPTION]`` Q4-2026 scenario values.

Screens, not guarantees: host counts produced here are KV-residency /
service-time SCREENS.  They are NOT measured SLO-goodput, not a proven maximum
of independent compute/queueing bounds, and measured engine allocation,
compute and goodput are absent.  No SLO-meeting output, portable fleet size,
or "FP8 halves the real deployment" is promised.
"""
from __future__ import annotations

import math
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIMITIVES_PATH = REPO_ROOT / "design" / "canonical-workload.yaml"

_REQUIRED_BLOCKS = (
    "scenario",
    "model",
    "hardware",
    "equations",
    "latency_and_throughput",
    "tco",
)


class PrimitiveError(ValueError):
    """Invalid primitive or scenario input (never silently divide by zero)."""


def load_primitives(path=None):
    """Load the canonical YAML.  Pure read; no caching, no writes."""
    p = Path(path) if path is not None else DEFAULT_PRIMITIVES_PATH
    with open(p, "r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    if not isinstance(doc, dict):
        raise PrimitiveError("%s: expected a mapping at the document root" % p)
    for block in _REQUIRED_BLOCKS:
        if block not in doc:
            raise PrimitiveError("%s: missing required block %r" % (p, block))
    if not isinstance(doc["tco"], dict) or "sizing" not in doc["tco"]:
        raise PrimitiveError("%s: 'tco' block must contain 'sizing'" % p)
    return doc


def kv_slot_floor(kv_budget_gb, kv_bytes_per_tok, tokens, kv_factor=1.0):
    """Hard-integer "full requests that fit" ceiling -- FLOOR, never round up.

    Applied BEFORE any utilization adjustment and BEFORE the host ceil.
    """
    budget = float(kv_budget_gb)
    if not math.isfinite(budget) or budget <= 0.0:
        raise PrimitiveError("KV budget must be finite and > 0 (got %r)" % budget)
    denom = float(kv_bytes_per_tok) * float(tokens) * float(kv_factor)
    if not math.isfinite(denom) or denom <= 0.0:
        raise PrimitiveError(
            "KV per-request bytes must be a finite value > 0 (got %r)" % denom)
    c = math.floor((budget * 1e9) / denom)
    if c < 1:
        raise PrimitiveError(
            "KV budget %s GB fits fewer than 1 full %s-token request "
            "(%s B/token x %s tokens x factor %s)"
            % (kv_budget_gb, tokens, kv_bytes_per_tok, tokens, kv_factor))
    return int(c)


def fleet_counts(c_floor, w_s, rps_avg, rps_peak, util=1.0, spare=0):
    """KV-residency / service-time SCREEN (see module docstring for limits)."""
    util = float(util)
    if not (0.0 < util <= 1.0):
        raise PrimitiveError("util must be in (0, 1], got %r" % (util,))
    w_s = float(w_s)
    if not math.isfinite(w_s) or w_s <= 0.0:
        raise PrimitiveError("service time W must be > 0 (got %r)" % (w_s,))
    for name, value in (("average request volume", rps_avg), ("peak request volume", rps_peak)):
        if not math.isfinite(float(value)) or float(value) <= 0.0:
            raise PrimitiveError("%s must be finite and > 0 (got %r)" % (name, value))
    spare_i = int(spare)
    if spare_i < 0 or float(spare) != float(spare_i):
        raise PrimitiveError("spare hosts must be a non-negative integer (got %r)" % (spare,))
    n_avg = math.ceil(float(rps_avg) * w_s / (c_floor * util))
    n_peak = math.ceil(float(rps_peak) * w_s / (c_floor * util))
    return {
        "kv_slot_floor": int(c_floor),
        "util": util,
        "spare_hosts": spare_i,
        "per_host_rps": float(c_floor) / w_s,
        "n_avg": int(n_avg),
        "n_peak_serving": int(n_peak),
        "n_peak_total": int(n_peak) + spare_i,
    }


def request_month(rps_avg, hours_per_day, workdays_per_year, months_per_year):
    """Business-hours request calendar -> requests per month."""
    rps = float(rps_avg)
    if not math.isfinite(rps) or rps <= 0.0:
        raise PrimitiveError("request volume must be > 0 rps (got %r)" % (rps,))
    calendar = {
        "request hours per day": float(hours_per_day),
        "request workdays per year": float(workdays_per_year),
        "request months per year": float(months_per_year),
    }
    for name, value in calendar.items():
        if not math.isfinite(value) or value <= 0.0:
            raise PrimitiveError("%s must be finite and > 0 (got %r)" % (name, value))
    return (rps * calendar["request hours per day"] * 3600.0
            * calendar["request workdays per year"] / calendar["request months per year"])


def validate_prices(prices):
    """Reject nonsensical prices loudly -- never silently divide by zero."""
    for key in ("host_capex_usd", "usd_per_kwh", "staff_usd_per_year",
                "cloud_usd_per_host_hour", "api_in_usd_per_1k",
                "api_out_usd_per_1k", "api_price_band_lo_usd_per_req",
                "api_price_band_hi_usd_per_req", "gpu_watt", "host_other_kw"):
        v = float(prices[key])
        if not math.isfinite(v) or v < 0.0:
            raise PrimitiveError(
                "%s must be a finite price >= 0 (got %r)" % (key, prices[key]))
    dep = float(prices["depreciation_years"])
    if not math.isfinite(dep) or dep <= 0.0:
        raise PrimitiveError(
            "depreciation_years must be > 0 (got %r)" % (prices["depreciation_years"]))
    pue = float(prices["pue"])
    if not math.isfinite(pue) or pue <= 0.0:
        raise PrimitiveError("pue must be > 0 (got %r)" % (prices["pue"]))
    if float(prices["gpus_per_host"]) < 1:
        raise PrimitiveError(
            "gpus_per_host must be >= 1 (got %r)" % (prices["gpus_per_host"]))
    if float(prices["api_price_band_hi_usd_per_req"]) <= float(
            prices["api_price_band_lo_usd_per_req"]):
        raise PrimitiveError("api price band must satisfy lo < hi")
    return prices


def self_host_costs(n, prices, billing_hours, power_kw_host=None):
    """Mode 1: capex + power scale with the fleet; staff is a fixed alloc.

    Components are computed EXACTLY and only rounded for display -- never
    multiplied from component-rounded values.
    """
    n = float(n)
    capex_host_mo = prices["host_capex_usd"] / (prices["depreciation_years"] * 12.0)
    if power_kw_host is None:
        gpu_it_kw = (prices["gpus_per_host"] * prices["gpu_watt"]) / 1000.0
        power_kw_host = (gpu_it_kw + prices["host_other_kw"]) * prices["pue"]
    if not math.isfinite(power_kw_host) or power_kw_host < 0.0:
        raise PrimitiveError("facility power kW must be finite and >= 0 (got %r)" % power_kw_host)
    power_host_mo = power_kw_host * prices["usd_per_kwh"] * float(billing_hours)
    staff_mo = prices["staff_usd_per_year"] / 12.0
    capex = n * capex_host_mo
    power = n * power_host_mo
    total = capex + power + staff_mo
    return {
        "n": int(n),
        "capex_host_mo": capex_host_mo,
        "power_kw_host": power_kw_host,
        "power_host_mo": power_host_mo,
        "staff_mo": staff_mo,
        "capex": capex,
        "power": power,
        "staff": staff_mo,
        "total": total,
        "per_1k": None,  # filled by caller once requests_per_month is known
    }


def cloud_costs(paid_host_hours, prices):
    """Mode 2: paid host-hours x hourly price (occupancy input, see YAML)."""
    h = float(paid_host_hours)
    if not math.isfinite(h) or h < 0.0:
        raise PrimitiveError("paid host-hours must be >= 0 (got %r)" % (paid_host_hours,))
    return {
        "paid_host_hours": h,
        "usd_per_host_hour": prices["cloud_usd_per_host_hour"],
        "total": h * prices["cloud_usd_per_host_hour"],
    }


def api_costs(prices, requests_per_month, in_tok, out_tok):
    """Mode 3: managed API, priced per request from token counts."""
    per_req = (float(in_tok) * prices["api_in_usd_per_1k"]
               + float(out_tok) * prices["api_out_usd_per_1k"]) / 1000.0
    return {
        "per_req": per_req,
        "per_1k": per_req * 1000.0,
        "month": per_req * float(requests_per_month),
    }


def breakeven_vs_api(self_total, prices, api_per_req):
    """Self-host monthly total / API price per request (mid + price band)."""
    if api_per_req <= 0.0:
        raise PrimitiveError("API price per request must be > 0 (got %r)" % (api_per_req,))
    return {
        "mid": self_total / api_per_req,
        "lo": self_total / prices["api_price_band_hi_usd_per_req"],
        "hi": self_total / prices["api_price_band_lo_usd_per_req"],
        "mid_price": api_per_req,
        "lo_price": prices["api_price_band_hi_usd_per_req"],
        "hi_price": prices["api_price_band_lo_usd_per_req"],
    }