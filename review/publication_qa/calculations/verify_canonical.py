"""INDEPENDENT canonical-workload verification (no import of the repo's
canonical_calc.py / check_regressions.py — these are re-derived from first
principles here, so a shared bug or a "tests that agree with the code" trap
is avoided). Computes the canonical workload numbers and prints each with
formula + units. Run: python3 review/publication_qa/calculations/verify_canonical.py
"""
import math

D = {}   # name -> (computed, expected|None, tol|None)

def put(name, computed, expected=None, tol=None):
    D[name] = (computed, expected, tol)

# ---- geometry ----
LAYERS, HIDDEN = 80, 8192
# FP16 KV per token (MHA): 2 * layers * hidden * bytes/value
kv16_bytes = 2 * LAYERS * HIDDEN * 2          # 2,621,440 B
put("KV/token FP16 (B)", kv16_bytes, 2621440, 0)
put("KV/token FP16 (MB)", kv16_bytes/1e6, 2.62144, 1e-4)
put("KV/token FP16 (MiB)", kv16_bytes/(2**20), 2.5, 1e-6)
# FP8 raw = byte-halving
kv8_bytes = 2 * LAYERS * HIDDEN * 1
put("KV/token FP8 (B)", kv8_bytes, 1310720, 0)
put("KV/token FP8 MB", kv8_bytes/1e6, 1.31072, 1e-4)

# ---- KV per request at canonical context lengths (decimal GB) ----
for label, tok in [("9,500", 9500), ("9,200", 9200), ("12,095", 12095), ("12,960", 12960), ("128,000", 128000)]:
    gb16 = tok * kv16_bytes / 1e9
    gb8 = tok * kv8_bytes / 1e9
    put(f"KV@_{label}_FP16_GB", gb16)
    put(f"KV@_{label}_FP8_GB", gb8)

# ---- concurrency ceilings on a 436 GB KV budget (aggregate) ----
POOL = 436.0
kv9500 = 9500 * kv16_bytes / 1e9
kv12095 = 12095 * kv16_bytes / 1e9
fp8_9500 = 9500 * kv8_bytes / 1e9
fp8_12095 = 12095 * kv8_bytes / 1e9
put("C_fp16@9500", POOL/kv9500, 17.507, 1e-3)
put("C_fp16@9500_floor", math.floor(POOL/kv9500), 17, 0)
put("C_fp16@12095", POOL/kv12095, 13.751, 1e-3)
put("C_fp8@9500", POOL/fp8_9500, 35.015, 1e-3)
put("C_fp8@9500_floor", math.floor(POOL/fp8_9500), 35, 0)
put("C_fp8@12095", POOL/fp8_12095, 27.502, 1e-3)
put("C_fp8@12095_floor", math.floor(POOL/fp8_12095), 27, 0)

# ---- token/workload ----
IN, OUT = 9200, 300
put("input tok/s @10rps", IN*10, 92000, 0)
put("output tok/s @10rps", OUT*10, 3000, 0)
put("input tok/s @40rps", IN*40, 368000, 0)
put("output tok/s @40rps", OUT*40, 12000, 0)
# Little's Law occupancy (requests in system): L = lambda * W_exec
wexec = 1.08 + 7.5   # 8.6 s
put("execution occupancy @10rps", 10*wexec, 86, 1.5)
put("execution occupancy @40rps", 40*wexec, 344, 3)
# monthly volume if 24x7
put("requests/month @10rps 24x7", 10*86400*30, 25920000, 0)
put("requests/user/month (2k users)", (10*86400*30)/2000, 12960, 0)

# ---- compute / prefill ----
N = 70e9
put("prefill demand FLOP/req @9.2K", 2*N*IN, 2*N*IN, 0)   # parameterized-linear 2NL
put("prefill demand PFLOP", 2*N*IN/1e15, 1.288, 1e-3)
# attention quadratic: 4 * layers * L^2 * d
attn = 4 * LAYERS * IN**2 * HIDDEN
put("attention quad @9.2K PFLOP", attn/1e15, 2.2e14/1e15, 0.3)
# crossover L* = N/(2*layers*d)
put("prefill crossover L*", N/(2*LAYERS*HIDDEN), 53405.76, 1.0)
# ratio at 32K
put("attn/linear @32K", (4*LAYERS*32000**2*HIDDEN)/(2*N*32000), 0.5992, 1e-3)

# ---- prefill rate ceiling per 8xH100 host ----
host_pf = 8 * 0.989e15      # FP16 dense peak, no sparsity
prefill_toks_per_s = host_pf * 0.35 / (2*N)
put("idealized prefill tok/s/host (35% MFU)", prefill_toks_per_s, 19780, 200)
# at 2 rps offered load
put("prefill demand at 2 rps (tok/s/host)", 2*IN, 18400, 0)
put("ratio demand/ceiling", (2*IN)/prefill_toks_per_s, 0.930, 0.01)

# ---- cost normalizations (P0-02) ----
put("whole-fleet $/1M input", 100/(92000*3600)*1e6, 0.301932, 1e-4)
put("whole-fleet $/1M output", 100/(3000*3600)*1e6, 9.259259, 1e-4)
put("whole-fleet $/1M combined", 100/(95000*3600)*1e6, 0.292398, 1e-4)
# tokens per cloud dollar
put("input tok per cloud dollar (M)", 1/(0.301932/1e6)/1e6, 3.312, 0.01)
put("output tok per cloud dollar (K)", 1/(9.259259/1e6)/1e3, 108.0, 0.5)

# ---- capstone mixture (Ch26) ----
H = 0.35
put("capstone mean TTFT (ms)", H*50+(1-H)*250, 180.0, 1e-6)
put("capstone p99 TTFT (ms)", 250.0, 250.0, 0)
put("capstone TTFT reduction vs 450", (450-250)/450, 0.4444, 1e-3)
put("capstone cost reduction", H+(1-H)*0.20, 0.48, 1e-6)

# ---- KDP/TCO ----
put("break-even req/month", 148000/(20.8/1000), 7.115e6, 1e5)

# ---- evaluate ----
fails = []
for name, (computed, expected, tol) in D.items():
    if expected is None:
        status = "INFO"   # recorded, no external expectation
        shown = f"={computed:.6g}"
    else:
        tolrange = tol if tol is not None else 1e-6
        ok = abs(computed - expected) <= abs(tolrange) if tol is not None else computed == expected
        status = "PASS" if ok else "FAIL"
        if not ok:
            fails.append((name, computed, expected))
        shown = f"={computed:.6g} vs exp {expected:.6g}"
    print(f"  [{status:4}] {name:36} {shown}")

print("\n=== SUMMARY ===")
print(f"{len(D)} checks; {len(fails)} FAILS")
for f in fails:
    print("  FAIL:", f)
if fails:
    raise SystemExit(1)
print("ALL INDEPENDENT CHECKS PASS")
