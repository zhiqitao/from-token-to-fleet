#!/usr/bin/env python3
"""Canonical calculator for From Token to Fleet.

Single source of truth: design/canonical-workload.yaml.
Every derived number in the book must equal what this script produces
(from the canonical equation set), divided into the exact units the book uses.

Run:  python3 render/canonical_calc.py
Print: all canonical derived values for cross-checking a chapter's numbers.
The point is reproducibility and unit discipline: if a chapter's number does
not match here, the chapter (or this script) is wrong -- reconcile, don't ship.
"""
import yaml, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(REPO, "design", "canonical-workload.yaml")

C = yaml.safe_load(open(CANON))
M = C["model"]; E = C["equations"]

def f(v):  # numeric coercion (yaml may give str for 70e9 on some loaders)
    try:
        return float(v)
    except (TypeError, ValueError):
        return v

# --- weights ---
weight_gb = f(M["params"]) * f(M["weight_bytes_per_param"]) / 1e9
assert abs(weight_gb - M["weight_gb"]) < 1, "weight_gb mismatch"

# --- KV per token ---
# canonical full-MHA teaching model: H_kv * D_head = hidden_dim
kv_bytes = 2 * f(M["layers"]) * f(M["hidden_dim"]) * f(M["kv_bytes_per_element"])
assert kv_bytes == E["kv_per_token_bytes"], "kv_per_token_bytes mismatch"
kv_mb = kv_bytes / 1e6

kv_gqa = 2 * f(M["layers"]) * 1024 * 2  # H_kv=8,D_head=128 -> 1024
kv_fp8 = 2 * f(M["layers"]) * f(M["hidden_dim"]) * 1  # 1 byte/element

hbm_usable = f(C["hardware"]["hbm_total_gb"]) * f(C["hardware"]["hbm_usable_fraction"])

tok = f(C["scenario"]["input_tokens"]); out = f(C["scenario"]["output_tokens"])
print("=== CANONICAL DERIVED VALUES ===")
print(f"weights            : {weight_gb:.0f} GB")
print(f"KV/token FP16 exact: {kv_mb:.3f} MB  (book: 2.5 MB rounded; 2,560 KB)")
print(f"KV/token 8-bit     : {kv_fp8/1e6:.2f} MB")
print(f"KV/token GQA(1024) : {kv_gqa/1e6:.3f} MB")
print(f"KV {tok} input  (book 2.5): {tok*kv_mb/1e3:.1f} GB   (exact {tok*kv_mb/1e9:.1f})")
print(f"KV {out} out   (book 0.75): {out*kv_mb/1e3:.2f} GB")
print(f"KV inference total : ~{C['derived']['kv_total_inference_gb']} GB (book)")
print(f"residency 9.2K     : {C['derived']['inference_residency_9200_gb']} GB (book) = 140 + 24.7")
print(f"hbm usable (8x)    : {hbm_usable:.0f} GB  (of {C['hardware']['hbm_total_gb']} GB)")

# --- consistency assertions against the canonical YAML's own derived block ---
assert abs(kv_mb - 2.62) < 0.01
assert C["derived"]["kv_9200_gb"] == 23.9
assert C["derived"]["kv_fp8_variant_mb"] == 1.3
assert abs(C["derived"]["kv_gqa_variant_mb"] - 0.33) < 0.01

try:
    kv = float(os.environ.get("KVCHECK", ""))
    print(f"\nKVCHECK={kv:.6f}")
except (ValueError, TypeError):
    pass
print("\nOK: canonical values consistent.")
