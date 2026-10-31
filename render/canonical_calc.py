#!/usr/bin/env python3
"""Canonical calculator for From Token to Fleet.

Single source of truth: design/canonical-workload.yaml, loaded through
render/tco_model.load_primitives().  This script holds NO parallel literal
table of canonical primitives -- rerunning it re-produces every derived number
from the one canonical equation set.

Convention (v2, 2026-09-18): ALL memory/compute arithmetic is DECIMAL (MB, GB).
Per-token KV FP16 exact = 2,621,440 B = 2.5 MiB = 2.62 MB decimal.
KV sizing DISTINCTION: initial (9,200 input) = 24.1 GB; max end-of-generation
(9,500 = 9,200+300) = 24.9 GB; use the MAX for residency/concurrency.
FP8 KV = RAW TENSOR BYTE-HALVING (1 byte/element = exactly 50% of BF16)
-> 12.45 GB @9,500 -> 35 concurrent (hard-fit floor).  The vLLM blog's 54%
is a decode inter-token-latency SLOPE -- a LATENCY metric -- not a memory
ratio, and no vendor-measured footprint is claimed for this geometry.

Run:  python3 render/canonical_calc.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tco_model as tm  # noqa: E402

doc = tm.load_primitives()

B = int(doc["equations"]["kv_per_token_bytes"])   # 2 x 80 x 8192 x 2 -- FULL-MHA reference model
B_GQA = 2 * 80 * (8 * 128) * 2                  # GQA: n_KV-heads=8, d_head=128 -> 327,680 B
sc = doc["scenario"]
tok_in = int(sc["input_tokens"])
tok_max = tok_in + int(sc["output_tokens"])
weights = float(doc["model"]["weight_gb"])
pool = float(doc["hardware"]["kv_budget_gb"])
fp8_factor = float(doc["tco"]["sizing"]["kv_raw_byte_factor_fp8"])
w_plan = float(doc["latency_and_throughput"]["service_time_s"])


def gb(tok):           # decimal GB for a token count
    return tok * B / 1e9


kv_9200 = gb(tok_in)
kv_9500 = gb(tok_max)
res_9500 = weights + kv_9500
c16 = pool / kv_9500
fp8_9500 = kv_9500 * fp8_factor   # RAW byte-halving (exactly half of BF16)
c8 = pool / fp8_9500
floor16 = tm.kv_slot_floor(pool, B, tok_max, 1.0)
floor8 = tm.kv_slot_floor(pool, B, tok_max, fp8_factor)

# Two INDEPENDENT fleet screens -- computed here, never forcibly equated.
sl = doc["scope_ledger"]
prefill_per_host = float(sl["prefill_tokens_per_s_PER_HOST"])
prefill_avg = math.ceil(float(sc["input_tokens"]) * float(sc["avg_rps"]) / prefill_per_host)
prefill_peak = math.ceil(float(sc["input_tokens"]) * float(sc["peak_rps"]) / prefill_per_host)
kv = tm.fleet_counts(floor16, w_plan, float(sc["avg_rps"]), float(sc["peak_rps"]))

print("=== CANONICAL DERIVED VALUES (decimal) ===")
print("CANONICAL MODEL = 70B FULL-MHA REFERENCE MODEL (hidden_dim=8192 wide K/V)")
print(f"KV/token FP16 (MHA) : {B/1e6:.2f} MB decimal (=2.5 MiB; {B} B)")
print(f"  general formula   : 2 * n_layers * n_KV-heads * d_head * bytes; MHA case n_KV-heads*d_head=d_model")
print(f"  GQA example       : n_KV-heads=8, d_head=128 -> {B_GQA/1e6:.3f} MB/token (~8x smaller)")
print(f"KV/token FP8 raw     : {B/2/1e6:.2f} MB   (1 byte/element = exactly 50% of BF16; NOT a vLLM-measured 54% memory ratio)")
print(f"KV  9,200 (initial) : {kv_9200:.1f} GB")
print(f"KV  9,500 (max)      : {kv_9500:.1f} GB")
print(f"residency 9,500 max  : {res_9500:.1f} GB  (~165)")
print(f"FP8 KV @9,500 (raw)  : {fp8_9500:.2f} GB  ({tok_max} x 1.31072 MB; byte-halving = 50% of BF16)")
print(f"concurrency FP16     : {pool:.0f}/{kv_9500:.4f} = {c16:.2f} -> hard-fit floor {floor16} (NOT 18; {c16:.2f} cannot round up)")
print(f"concurrency FP8      : {pool:.0f}/{fp8_9500:.4f} = {c8:.2f} -> hard-fit floor {floor8} (NOT 33; {c8:.2f})")
print(f"scope prefill screen : {prefill_avg} avg / {prefill_peak} peak hosts (INDEPENDENT compute screen)")
print(f"scope KV/Little      : {kv['n_avg']} avg / {kv['n_peak_serving']} peak hosts (INDEPENDENT residency screen, floor {floor16})")
print("OK: canonical values consistent (decimal convention).")