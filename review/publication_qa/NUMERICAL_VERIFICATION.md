# NUMERICAL VERIFICATION

Independent re-derivation of every canonical-scenario quantity from first principles.
The verification code does **NOT** import the repository's `render/canonical_calc.py`,
`render/check_regressions.py`, or the YAML — it recomputes from the stated geometry/units,
so a shared code bug or a "test that agrees with its own oracle" trap is avoided.

**Script:** `review/publication_qa/calculations/verify_canonical.py` (run from repo root)
**Result:** 48 checks, **0 failures** (`ALL INDEPENDENT CHECKS PASS`).

## Key checked results (all PASS)

| Quantity | Formula | Computed |
|---|---|---|
| KV/token FP16 (MHA) | 2×80×8192×2 B | 2,621,440 B = 2.62144 MB = 2.5 MiB |
| KV/token FP8 (raw) | 2×80×8192×1 B | 1,310,720 B = 1.31072 MB |
| KV @ 9,500 tok (FP16) | 9500 × 2621440 / 1e9 | 24.90368 GB |
| KV @ 12,095 tok (FP16) | 12095 × 2621440 / 1e9 | 31.7063 GB |
| Concurrency C_fp16 @9.5K | 436 / 24.90368 | 17.507 (floor 17) |
| Concurrency C_fp8 @9.5K | 436 / 12.45184 | 35.015 (floor 35) |
| Concurrency C_fp8 @12,095 | 436 / 15.853 | 27.502 (floor 27) |
| input tok/s @10 rps | 9200 × 10 | 92,000 |
| output tok/s @10 rps | 300 × 10 | 3,000 |
| Execution occupancy @10 rps | 10 × (1.08+7.5) | 85.8 (≈86) |
| Execution occupancy @40 rps | 40 × 8.58 | 343.2 (≈344) |
| requests/month if 24×7 | 10 × 86400 × 30 | 25,920,000 (12,960/user) |
| Prefill demand PFLOP @9.2K | 2·N·L / 1e15 | 1.288 PF |
| Attention quad @9.2K | 4·80·9200²·8192 | ≈0.222 PF |
| Prefill crossover L* | N/(2·80·8192) | 53,405.8 tokens |
| attn/linear @32K | 4·80·32000²·8192/(2N·32000) | 0.5992 |
| Idealized prefill tok/s/host | 8×0.989e15×0.35/(2×70e9) | 19,780 (35% MFU) |
| Prefill demand at 2 rps | 2 × 9200 | 18,400 tok/s/host |
| **Ratio demand/ceiling** | 18400 / 19780 | **0.930 (93% — very tight)** |
| whole-fleet $/1M input | 100/(92000×3600)×1e6 | **$0.301932** |
| whole-fleet $/1M output | 100/(3000×3600)×1e6 | **$9.259259** |
| whole-fleet $/1M combined | 100/(95000×3600)×1e6 | **$0.292398** |
| Capstone mean TTFT | 0.35×50 + 0.65×250 | 180 ms |
| Capstone p99 TTFT | (two-point; 0.99 quantile in miss) | 250 ms |
| Capstone TTFT reduction | (450−250)/450 | 44.4% |
| Capstone cost reduction | 0.35 + 0.65×0.20 | 48% |
| Break-even req/month | 148000/(20.8/1000) | ≈7.12M |

## What this verifies
- All P0-02 cost normalization figures (now corrected in the manuscript to $0.301932
  / $9.259259 / $0.292398).
- All P0-01/P1-05 population-vs-occupancy figures (≈86 / ≈344 in-flight requests,
  distinct from the active-user population).
- P1-04 feasibility ratio 93% (very tight prefill/decode coexistence).
- P1-09 / P1-03 scenario values.

## What it does NOT verify
- Measured real-hardware goodput / SLO (no deployment benchmark supplied) — those
  claims stay ANALYTICAL, per the evidence taxonomy, and are marked as such.
- 2026 vendor model-card values (spot-checked at link level only).
- Traffic trace realism (a scenario input, now explicitly labeled a business-hours
  stress profile; the 24×7-implausibility is documented in the manuscript).
