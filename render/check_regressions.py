"""Book-wide numeric regression checks (Gate 1 of the 2026-10-24 review).

Prints every intermediate value with units and asserts the reviewer's
canonical TOK / MEM / CMP / FLT / TCO invariants. Fails with a non-zero exit
if any check is off. Run from the repo root:  python3 render/check_regressions.py
"""
import math

# ---- canonical reference (Ch 4 Table 4-3 + Ch 7) ----
LAYERS = 80
HIDDEN = 8192
N_PARAM = 70e9

# ---- TOK: canonical workload tokens ----
IN_TOK = 9200      # 1200 prompt + 8000 retrieved
OUT_TOK = 300
t_input_avg = IN_TOK * 10
t_output_avg = OUT_TOK * 10
t_input_peak = IN_TOK * 40
t_output_peak = OUT_TOK * 40
assert t_input_avg == 92000 and t_output_avg == 3000
assert t_input_peak == 368000 and t_output_peak == 12000

# ---- MEM: KV bytes/token (FP16 and FP8 raw) ----
kv_fp16_bytes = 2 * LAYERS * HIDDEN * 2      # 2,621,440 B
kv_fp8_bytes = 2 * LAYERS * HIDDEN * 1       # 1,310,720 B (raw byte-halving)
assert kv_fp16_bytes == 2621440, kv_fp16_bytes
assert kv_fp8_bytes == 1310720, kv_fp8_bytes
kv_fp16_mb = kv_fp16_bytes / 1e6              # 2.62144 MB
kv_fp8_mb = kv_fp8_bytes / 1e6                # 1.31072 MB
kv_9500_gb = 9500 * kv_fp16_bytes / 1e9       # 24.90368 GB
kv_12095_gb = 12095 * kv_fp16_bytes / 1e9     # 31.7063 GB
assert abs(kv_9500_gb - 24.90368) < 1e-4, kv_9500_gb
assert abs(kv_12095_gb - 31.7063) < 1e-4, kv_12095_gb

# ---- FP8 (raw) per-request GB and concurrency (corrected P0-01) ----
fp8_9500_gb = 9500 * kv_fp8_bytes / 1e9       # 12.45184 GB
fp8_12095_gb = 12095 * kv_fp8_bytes / 1e9     # 15.853 GB
POOL = 436.0
C_fp16_9500 = POOL / kv_9500_gb               # 17.507
C_fp16_12095 = POOL / kv_12095_gb             # 13.751
C_fp8_9500 = POOL / fp8_9500_gb               # 35.015
C_fp8_12095 = POOL / fp8_12095_gb             # 27.502
assert abs(C_fp16_9500 - 17.507) < 0.01, C_fp16_9500
assert abs(C_fp8_9500 - 35.015) < 0.01, C_fp8_9500
assert abs(C_fp8_12095 - 27.502) < 0.01, C_fp8_12095

# ---- CMP: prefill FLOPs and crossover ----
f_linear_9k = 2 * N_PARAM * IN_TOK            # FLOP parameterized-linear baseline
f_attn_9k = 4 * LAYERS * (IN_TOK ** 2) * HIDDEN
crossover = N_PARAM / (2 * LAYERS * HIDDEN)   # 53,405.76 tokens
assert abs(crossover - 53405.76) < 1.0, crossover
ratio_32k = 4 * LAYERS * (32000 ** 2) * HIDDEN / (2 * N_PARAM * 32000)
assert abs(ratio_32k - 0.5992) < 0.01, ratio_32k

# ---- FLT: integer-slot host counts (P1-01) ----
def host(lam, w, c_floor, util=0.70):
    return math.ceil(lam * w / (c_floor * util))
assert host(344, 1, 17) == 29      # 40rps T=0, FP16
assert host(860, 1, 17) == 73      # 100rps T=0
assert host(1720, 1, 17) == 145    # 200rps T=0
assert host(552, 1, 13) == 61      # 40rps T=3
assert host(1380, 1, 13) == 152    # 100rps T=3
assert host(2760, 1, 13) == 304    # 200rps T=3

# ---- TCO ----
assert abs(20.8e-3 * 26e6 - 540800.0) < 1.0       # managed-API monthly
assert abs(148000 / (20.8 / 1000) - 7.115e6) < 1e5

# ---- Capstone (Ch 26 F02/F04): mixture mean vs p99 ----
H = 0.35
mean_ttft = H * 50 + (1 - H) * 250               # 180 ms (mean, NOT p99)
p99_ttft = 250.0                                 # two-point: 0.99 quantile is the miss value
assert abs(mean_ttft - 180.0) < 1e-9, mean_ttft
assert p99_ttft == 250.0
improve = (450 - p99_ttft) / 450                 # 44.4%
assert abs(improve - 0.4444) < 0.01, improve
cost_red = H + (1 - H) * 0.20                    # 48%
assert abs(cost_red - 0.48) < 1e-9, cost_red

print("OK - all numeric regression checks passed.")
print(f"  KV FP16 {kv_fp16_bytes} B ({kv_fp16_mb:.3f} MB/tok); FP8 raw {kv_fp8_bytes} B ({kv_fp8_mb:.3f} MB/tok)")
print(f"  KV @9.5K FP16 {kv_9500_gb:.3f} GB (C={C_fp16_9500:.3f}, floor {math.floor(C_fp16_9500)}); "
      f"FP8 {fp8_9500_gb:.3f} GB (C={C_fp8_9500:.3f}, floor {math.floor(C_fp8_9500)})")
print(f"  prefill crossover L* = {crossover:.1f} tokens; ratio@32K = {ratio_32k:.3f}")
print(f"  capstone mean {mean_ttft:.0f} ms, p99 {p99_ttft:.0f} ms, improvement {improve*100:.1f}%, "
      f"cost reduction {cost_red*100:.0f}%")
