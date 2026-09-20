# PASS-4 FIXER — Responses (NEW comments surfaced; loop continues)

## [P4-1] Ch19 §4 median/95th-percentile turn miscount. SEVERITY: Major. STATUS: FIXED.
Location: Ch19 §4 "Tool-call latency budget" (line 108).
Problem: Line 108 stated "440 ms at median T=2, 880 ms at 95th-percentile T=4". But Ch19's own
  turn distribution (68% T=1 / 25% T=2 / 5% T=3 / 2% fallback), stated in line 95 and in the §8
  mini-case (line 195), makes the median T=1, 90th percentile T=2, 95th percentile T=3. Line 108
  was an internal contradiction within Ch19.
Fix: line 108 now reads "220 ms at median T=1, 440 ms at 90th pct T=2, 660 ms at 95th pct T=3
  (consistent with §8 turn distribution; T capped at 3, 2% fallback = zero-added-turn single-shot)."
Verified: Table 19-1 already correct (median/90th/95th/beyond-limit headers; 220/440/660/880 ms);
  only line 108's prose had the error.

## [P4-2] Ch19 §4 "median 2-turn profile" inconsistency. SEVERITY: MINOR (follow-on from P4-1). STATUS: FIXED.
Location: Ch19 §4 "Inference scaling" (line 141 line ~144).
Problem: Referenced "median 2-turn profile (~29.4 GB/request at 11,230 tokens)" — but the median
  is T=1, so the median profile is 10,365 tokens (~27.2 GB). The 2-turn profile is the 90th
  percentile, not the median.
Fix: changed to "median single-turn profile (~27.2 GB/request at 10,365 tokens)"; aggregate KV
  ~2.9 TB -> ~2.7 TB (100 x 27.2 GB = 2,720 GB). Verified 10,365 x 2.62/1000 = 27.2 GB.

## [P4-3] Ch25 §8 ADR 0017 "~1 s per request" wrong service time. SEVERITY: MODERATE. STATUS: FIXED.
Location: Ch25 §8 mini-case, ADR 0017 Context (line 185).
Problem: "~40 rps at ~1 s per request implies ~40 in-flight requests". The canonical service
  time is W ~ 8.6 s, giving 40 x 8.6 = 344 in-flight (consistent with Ch17), not 40.
Fix: "~40 rps at the canonical ~8.6 s service time implies ~344 in-flight requests — far more
  than one host can hold (a single host holds ~18 concurrent)."

## Confirmed non-defect (from PASS-4 deep-read + vision)
- Fig 7.2 "finding": the vision model misread the log-log chart. Source script plots
  ctx=[1,4,9.2,32,128] with kv=2.62xctx, giving 24.1GB@9.2K and 335GB@128K (canonical). The
  9.2K=24GB annotation uses the 9.2K input; the 24.9GB value is the separate 9.5K max-context
  budget point. Verified against source + body text.
