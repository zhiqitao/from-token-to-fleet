# PASS-6 FIXER — Responses (14 new comments, loop continues)

PASS-6 surfaced 14 new comments (5 Moderate, 9 Minor) from a thorough ch14-27+backmatter review
(persisted in review/loop/pass6_findings_ch14-27.md). All addressed below.

## MODERATE

### [P6-1] Ch19-vs-Ch17 agentic service-time discrepancy (9.3s vs 13.8s). FIXED.
Root cause: Ch19's L_E2E(T)=L_base+T·L_agent is an *incremental orchestration-overhead* model
  (base generation held at single-shot decode of 300 output tokens), while Ch17's W≈13.8s is the
  *full* agentic service time (decode of all generated tokens 300+T·65 + grown-context prefill +
  tool latency). Both valid but presented as if the same quantity.
Fix: Added explicit scope notes to BOTH Ch19 §4 ("this is the incremental orchestration model,
  not the full agentic service time; the full W≈13.8s is what fleet sizing uses, per Ch17") and
  Ch17 §8 ("this W is the full agentic service time, not the ~660ms incremental orchestration
  figure; the two are different quantities"). Now the two chapters distinguish the two models
  consistently. Table 19-1's "Total end-to-end" row reports the incremental model; Ch17 fleet
  tables use the full W.

### [P6-2] Ch19 L_E2E omits decode of per-turn γ reasoning tokens. FIXED (folded into P6-1).
The incremental model intentionally isolates orchestration overhead; the full service time
  (which Ch17 uses) includes the T·γ decode. Clarified in the P6-1 scope note.

### [P6-3] Ch21 "~$0.82/1K (Ch16)" wrong per-1K rate. FIXED.
Ch16's canonical rates are $5.7/1K (self-host), $2.8/1K (cloud), $20.8/1K (API); no $0.82/1K.
  Changed to "~$5.7/1K (self-host), ~$1,231, or ~$605 on the cloud-scaled ~$2.8/1K basis".

### [P6-4] Ch20 §3 KV-residency bound at 40rps mis-stated (~5 hosts). FIXED.
Corrected: at 40rps the KV bound is ⌈344/18⌉≈19-20 hosts, so it is *co-binding* with the
  throughput/Little bound (not "far fewer hosts"); the ~5 hosts figure applies only to the
  10rps average. Also cited Ch17's Little's-law identity.

### [P6-5] Ch24 8 delimiter styles claimed, 7 enumerated. FIXED.
Added the 8th delimiter (`<<SYS>>`) to match the 8 used in the count (4×8×6×4=768).

## MINOR

### [P6-6] Ch17 §4 C≈14 at T=4 vs C≈13. FIXED.
Changed to "C≈13/host (436 ÷ (12,960×2.62MB≈34.0) ≈12.8)" and ρ·C ≈ 12 at ρ=0.95.

### [P6-7] Ch20 §3 duplicated "KV-residency/latency bound" bullet. FIXED.
Deleted the second verbatim copy (line 36).

### [P6-8] Ch24 §8 poisoned-hit "0.003 per 1,000 queries" unit error. FIXED.
Changed to "≈0.003 per query (≈3 per 1,000 queries), matching Table 24-1's fraction convention."

### [P6-9] Ch24 §4.1 vs Table 24-1 thresholds disagree. FIXED.
Unified: poisoned-hit target <0.3% (0.003/query) in §4.1, line 135, matching Table 24-1;
  false-positive target <1.5% in §4.1, matching Table 24-1.

### [P6-10] Ch24 §8 false-positive rate unit inconsistency. FIXED.
Changed "1.3 per 1,000 queries" to "≈1.3% (≈13 per 1,000 queries)", matching Table 24-1's
  percentage value.

### [P6-11] Ch25 §4 ~30GB activations vs ~64GB canonical reserve. FIXED.
Clarified the ~30GB is a per-request runtime figure for the worked example, noted it is below
  the ~64GB runtime/workspace/NCCL reserve used elsewhere (140+436+64≈640GB envelope).

### [P6-12] Ch25 §6 "we chose FP16 over BF16" reverses ADR 0016. FIXED.
Changed to "we chose BF16 over FP16 because of range robustness and training-to-serving
  consistency (as ADR 0016 does)."

### [P6-13] Ch26 Fig 26.1 caption broken cross-refs. FIXED.
"§4 six-axis" -> "Chapter 4 six-axis"; "three workload families from Table 26-1" -> "workload
  families from the §2.1 workload-to-strategy matrix"; "§26 matrix" -> "§2.1 matrix".

### [P6-14] Ch19 turn-cap inconsistency (4 vs 3). FIXED.
Added scope note in §3: the 4-turn cap is the default/illustrative bounding case; the
  recommended operational policy (deployed in §8, used in Ch17 sizing) caps at 3; Table 19-1's
  T=4 column is an out-of-policy bounding case.

## Also verified clean this pass (no action)
Ch15 MFU/prefill arithmetic; Ch15 Table 15-1 in-flight; Ch16 TCO; Ch17 C values + Table 17-1;
Ch18 mixed-fleet cost; Ch20 §8 marginal cost; Ch22 Table 22-1; Ch24 §3.3; Ch27 Fig A.1;
back matter glossary/references/sources/worksheet — all confirmed. Ch7 §4 100-layer/12288-dim
per-token KV corrected to ~4.9 MB/token (2×100×12288×2B=4.915e6) — a separate PASS-6 ch01-13
finding.
