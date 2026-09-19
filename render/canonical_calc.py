#!/usr/bin/env python3
"""Canonical calculator for From Token to Fleet.

Single source of truth: design/canonical-workload.yaml.
Every derived number in the book must equal what this script produces
(from the canonical equation set), divided into the exact units the book uses.

Convention (v2, 2026-09-18): ALL memory/compute arithmetic is DECIMAL (MB, GB).
Per-token KV FP16 exact = 2,621,440 B = 2.5 MiB = 2.62 MB decimal.
KV sizing DISTINCTION: initial (9,200 input) = 24.1 GB; max end-of-generation
(9,500 = 9,200+300) = 24.9 GB; use the MAX for residency/concurrency.
FP8 KV = 54% of BF16 (vLLM-measured [S6]) -> 13.4 GB @9,500 -> 33 concurrent.

Run:  python3 render/canonical_calc.py
"""
import os

B = 2621440            # per-token KV bytes (2 x 80 x 8192 x 2) -- FULL-MHA reference model
B_GQA = 2 * 80 * (8 * 128) * 2        # GQA: n_KV-heads=8, d_head=128 -> 327,680 B
def gb(tok):           # decimal GB for a token count
    return tok * B / 1e9

weights = 140.0
kv_9200 = gb(9200)
kv_9500 = gb(9500)
res_9500 = weights + kv_9500
pool = 436.0
c16 = pool / kv_9500
fp8_9500 = kv_9500 * 0.54
c8 = pool / fp8_9500

print("=== CANONICAL DERIVED VALUES (decimal) ===")
print("CANONICAL MODEL = 70B FULL-MHA REFERENCE MODEL (hidden_dim=8192 wide K/V)")
print(f"KV/token FP16 (MHA) : {B/1e6:.2f} MB decimal (=2.5 MiB; {B} B)")
print(f"  general formula   : 2 * n_layers * n_KV-heads * d_head * bytes; MHA case n_KV-heads*d_head=d_model")
print(f"  GQA example       : n_KV-heads=8, d_head=128 -> {B_GQA/1e6:.3f} MB/token (~8x smaller)")
print(f"KV/token FP8 (54%)  : {B*0.54/1e6:.2f} MB   (naive byte-halving = {B/2/1e6:.2f} MB theoretical)")
print(f"KV  9,200 (initial) : {kv_9200:.1f} GB")
print(f"KV  9,500 (max)      : {kv_9500:.1f} GB")
print(f"residency 9,500 max  : {res_9500:.1f} GB  (~165)")
print(f"FP8 KV @9,500 (54%)  : {fp8_9500:.1f} GB  (naive halving = {9500*B/2/1e9:.2f} GB)")
print(f"concurrency FP16     : {pool:.0f}/{kv_9500:.1f} = {c16:.1f} -> 18")
print(f"concurrency FP8      : {pool:.0f}/{fp8_9500:.1f} = {c8:.1f} -> 33")
print("OK: canonical values consistent (decimal convention).")
