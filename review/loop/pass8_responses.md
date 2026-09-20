# PASS-8 FIXER — Responses (12 new comments, loop continues)

PASS-8 surfaced 12 new comments (ch01-14: 6 [4 MODERATE, 2 MINOR]; ch15-27: 6 [all LOW]).
Findings in review/loop/pass8_findings_01-14.md and pass8_findings_15-27.md. All addressed.

## ch01-14 (P8-1..P8-6)
### [P8-1] Ch4 §8 mini-case ~50 rps from ~8.6s W. MODERATE. FIXED.
500/8.6=58 rps, not 50. Aligned the mini-case to the ~10 s planning-round W (500/10=50),
  consistent with the chapter's own Little's-law basis (100 concurrent/10s≈10 rps). 24-host count
  now stands.
### [P8-2] Ch4 §3 "one host can serve the canonical workload at target SLO". MODERATE. FIXED.
Scoped as per-request latency-SLO feasibility vs capacity: added "single host holds C≈18, cannot
  carry 40rps peak (~344 in flight); ~5 hosts at avg, ~20 at peak (Ch8, Ch16-17)."
### [P8-3] Ch10 §3 gradient labeled BF16 but uses 4B/param (280GB). MODERATE. FIXED.
Relabeled from "BF16 gradient" to "FP32 gradient" (70×10^9×4B=280GB is FP32).
### [P8-4] Ch14 §3 "Candidate A meets SLO" with goodput 2.6% of demand. MODERATE. FIXED.
The single 8×H100 host cannot hold 344 in-flight (C≈18), and 9,800 tok/s vs ~380K demand misses
  the SLO. Rewrote step 2/3: benchmark loaded at the concurrency the host can hold (C≈18,
  ~2.1 req/s), goodput ~19,800 tok/s (consistent with Ch8 ceiling and the ~20K tok/s demand
  there), and noted the full 40rps peak is a ~20-host fleet.
### [P8-5] Ch5 "4×FLOP" vs table ~2×. MINOR. FIXED.
all-mpnet ~1 GFLOPs vs bge-large ~2 GFLOPs = 2×; changed "4×FLOP" → "~2×FLOP".
### [P8-6] Ch7 Table 7-1 "at 9.2K" rows use 164.9 max value. MINOR. FIXED.
9.2K residency is 140+24.1=164.1 GB; changed the 4 "at 9.2K" rows from 164.9→164.1 GB.
  (9.5K-max rows correctly stay at 164.9/165 GB.)

## ch15-27 (P8-A..P8-F)
### [P8-A] Ch20 orphan "Table 20-1" caption (no body). LOW. FIXED.
Removed the orphan label; Fig 20.1 carries the fleet QPS/latency-vs-host-count content.
### [P8-B] Ch26 §8 "Tab 26.1" ref now stale after PASS-7 renumbering. LOW. FIXED.
"Tab 26.1" → "Table 26-2" (the Pattern Instance table).
### [P8-C] Ch26 "Precised-optimizer" typo. LOW. FIXED.
→ "Precision-aware optimizer (LoRA/QLoRA)".
### [P8-D] Ch18 §3.1 MoE FP16 "0 (same as dense)" contradicts dense row "1". LOW. FIXED.
Both have identical 140 GB FP16 residency, so MoE → "1 (same as dense FP16)".
### [P8-E] Ch18 §8 monthly $1,945/$8,855 inconsistent. LOW. FIXED.
$2.68/hr × 720 = $1,930/mo; savings = $10,800 − $1,930 = $8,870/mo. Updated both.
### [P8-F] Ch24 §8 tool-use 0.32% at PIES=143. LOW. FIXED (re-applied; PASS-7 fix not landed).
Set to 0.44% (matching Table 24-1 Cycle 2 at PIES=143). Verified in source.

## Verified clean this pass
Across ch15-27 all checked quantities reconcile (Ch17 host counts, Ch18 routing, Ch19 turn
  distribution, Ch24 PIES/poisoning, Ch25 ADRs, Ch27 Appendix A) — no HIGH/MEDIUM numeric errors.
