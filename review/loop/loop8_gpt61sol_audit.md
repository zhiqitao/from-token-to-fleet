# Loop 8 — gpt-6.1-sol Publication-Readiness Audit

**Manuscript:** `from-token-to-fleet-v20260913.pdf` (362 pp, US Letter)
**SHA-256 (pre-fix):** `e5451a24ef1acc5b2a0ae87a47b059294ed6055c997717cd3882e64f6875a94c`
**Reviewer:** gpt-6.1-sol (the configured `auxiliary.review` model, via copilot `/responses`), text-only (no PDF pixels). Visual audit (Pass C) done by the orchestrator with rendered pages.
**Standard:** `loop8_master_instructions_v2.md` (the enhanced v2, with §8.8 visual-design quality as an independent release criterion).

## Method and honest coverage
- gpt-6.1-sol read the full extracted text (121K words) and produced 25 findings (2 P0, 23 P1, 3 P2), cut off at FTF-0019 by the output limit.
- gpt-6.1-sol had **no PDF access** (0/362 rendered pages, 0/46 figures). Every finding was therefore **trust-but-verified against the source** before acting.
- The orchestrator did the full **visual audit of all 40 numbered figures** at print scale (4-dimension ratings per v2 §8.8).
- Findings are marked CONFIRMED (verified in source), FALSE POSITIVE (gpt-6.1-sol misread), or NEEDS VERIFICATION (not yet checked).

## Executive decision
**NOT READY — MUST-FIX WORK REMAINS** (pre-fix). Two P0s (canonical TCO volume basis; capstone sharding/cost model) were confirmed and fixed. After the fixes below, the book is closer to CONDITIONALLY READY, but the remaining P1s (several confirmed, several unverified) and the figure defects must be closed before a READY call.

## Fixed in this loop (verified in the rebuilt PDF)

| ID | Sev | Location | Fix |
|---|---|---|---|
| FTF-0001 | P0 | Ch16/21/26 | TCO repriced from 24×7 (26M req/mo) to the active business-hours schedule (6.24M req/mo) per Ch4's explicit instruction. Self-host $5.7→$23.7/1K, cloud $2.8→$11.7/1K, managed $541K→$129.8K/mo, 30-host $8.4→$34.8/1K. Table 16-1, Ch21 bad-release cost, Ch26 $0.0057→$0.0237 all updated. |
| FTF-0002 | P0 | Ch26 capstone | Baseline is a single 8×H100 node (already TP=8), so "unsharded baseline"→"single-node baseline"; the 20% per-token saving is from deeper continuous batching on the already-sharded engine (not double-counted sharding); Table 26-2 $0.003→$0.012/query (consequence of FTF-0001). |
| FTF-0003 | P1 | Ch16 | "FP8 KV cuts the peak fleet to ~10"→clarified: FP8 cuts the *KV-bound* fleet to ~10, but the true peak fleet stays ~20 (the throughput bound ⌈40/2.0⌉, independent of KV size); fleet = max(N_throughput, N_KV). |
| FTF-0013 | P1 | Ch19 | Agent token accounting: "call 3 = 9,200 + 2×(800+65) + 300 ≈ 12,095"→"3×(800+65) = 12,095" (the formula gave 11,230); task_input 9,200+10,350+12,095=31,645→9,200+10,365+12,095=31,660 (10,350 was a 15-token error vs the table's 10,365). |
| FTF-0017 | P1 | Ch24 | PIES "equivalence relation"→"deterministic clustering rule" (thresholded NLE ≤ 0.25 is not transitive: 0000~0001, 0001~0011, but 0000!~0011). |
| FTF-0018 | P1 | Ch24 | False-positive rate "≈13 per 1,000 queries"→"≈0.05 per 1,000 (1.3% of the 4.1 interventions per 1,000)" — the false positives cannot exceed the total interventions. |

## False positive (no action)
- **FTF-0008 (P1)** — gpt-6.1-sol claimed the NVLink ring all-reduce uses bidirectional 900 GB/s for a unidirectional 245 GB send (→ 0.544 s, not 0.27 s). **Misread:** the 245 GB is the *total* data moved per rank (send+receive, 2(N-1)/N·M), divided by the *bidirectional* 900 GB/s = 0.272 s. The book is correct.

## Visual audit (Pass C) — all 40 numbered figures, 4-dimension ratings
**All 4 PASS (KEEP):** 2.1, 2.2, 5.1, 7.3, 7.4, 8.1, 8.2, 10.1, 11.2, 11.3, 12.1, 15.1, 15.2, 16.1, 17.1, 20.1, 21.1, 24.1, 25.1, 26.2.

**Defects found (need fixing):**
| Fig | Dim | Defect |
|---|---|---|
| 6.2 | Technical FAIL | mean=0.85s is *below* the median/p50 (~0.9s) — impossible for a right-skewed distribution with a heavy tail; p99=1.33s sits in an empty histogram gap (inconsistent with the 1% stragglers at ~5s); peak bar clipped at the top (y-axis max 3000 too low). |
| 19.3 | Technical FAIL | the teal δ and orange γ segments are drawn at the *same* height every turn (they don't accumulate), contradicting the caption's "cumulative" claim and the formula I₀+T·δ+T·γ+O_final; bar-top steps are non-uniform while KV rises a uniform ~2.2-2.3 GB/turn. |
| 19.1 | Design FAIL | in-figure annotation line ends with the bracketed tag "[ILLUSTRATIVE conceptual]" (metadata leakage; same class as the Fig 16.1 tags already fixed). |
| 18.1 | Technical/Design/Pedag MARGINAL | green branch labels "yes→specialist"/"yes→frontier/small" misaligned (shifted left) of their drop arrows; prose's "feature gate / Tier 1/2/3" scheme is unmapped from the figure's capability-filter + family-leaf scheme; "SLO check must come first" vs the figure's "capability first" policy. |
| 23.1 | Technical MARGINAL | Box 1 "problem" (TTFT p99 = 1.4 s) already satisfies Box 2 "success" (p95 ≤ 2 s), since p95 ≤ p99 = 1.4 s < 2 s — the stated problem doesn't violate the success criterion. |
| 22.1 | Technical MARGINAL | body says the y-axis is "labeled generically 'Compute (PFLOP; see series definition)'" but the actual axes are labeled specifically "Prefill compute (PFLOP/request)" / "Decode compute (PFLOP/token)" — stale text; also "two prefill series" vs three in the legend. |
| 26.1 | Technical MARGINAL | caption lists raw inputs {traffic, token profile, SLO, quality, ops, TCO} that don't map to the displayed axes {context length, traffic, quality, cost, latency, output tokens}; "Normalised" (British) vs "normalized" (US). |
| 6.1 | Technical MARGINAL | caption first sentence "top-down diagnostic path" should be "bottom-up" (diagnosis runs serving→workload, per the diagram's "diagnosis ↑" and the caption's own second sentence). |
| 4.1 | Technical MARGINAL | figure↔caption wording mismatch at rows 2 & 4 ("concurrency & batching" vs "...batching strategy"; "TTFT/TPOT & batch window" vs "TTFT/TPOT targets & batch window"). |
| 7.2 | Technical MARGINAL | in-chart annotation "9.2K ≈ 24 GB" (arrow at x=10K) vs caption "9.5K / 24.9 GB" — three different context lengths for one callout; 24.9 rounds to 25 not 24. |
| 11.1 | Technical MARGINAL | left panel rows 3-4 non-monotonic blue width (a locked batch's active count can only decrease); right panel green "new" persisting across steps (should turn blue after admission); caption "staggered" not matched by aligned columns. |

**Design MARGINAL (cosmetic, lower priority):** 1.1 (read-K label detached, stray bracket, token₁ routing), 1.2 (stray UI glyphs in all 6 boxes, stray green bracket, read path not drawn), 3.1 (orphaned grey "resident" legend swatch in the Dense panel), 7.1 (Table 7-2 continuation leaves a blank area), 7.5 (stray dash at the right end of the red 640 GB rule), 9.1 (top-right annotation crowds the RoCE curve), 14.1 (large blank bands; "benchmark" label misaligned), 19.2 (dead space; unbalanced legend; "O_final" split across lines).

## Remaining gpt-6.1-sol P1s — verification queue (not yet individually verified)
FTF-0004 (fractional concurrency 17 vs 17.5), FTF-0005 (decode roofline omits KV reads), FTF-0006 (MoE total-vs-active memory), FTF-0007 ("one host" = "no model parallelism"), FTF-0009 (140 GB per-rank H100 collectives), FTF-0010 (aggregate network demand uses host count), FTF-0011 (prefix-cache savings without exact-prefix eligibility), FTF-0012 (tool-result caching shrinks retained context), FTF-0014 (fallback accounting / conditional percentiles), FTF-0015 (p95 breach ≠ goodput), FTF-0016 (mixed-model cost/latency basis), FTF-0019 (evidence labels), FTF-0020 (DeepSeek/GLM appendix), FTF-0021 (population→rate substitutions), FTF-0022 (response-cache identity), FTF-0023 (SDPA op vs implementation), FTF-0024 (attention FLOPs full-square vs causal), FTF-0025 (dimensional claim). Plus FTF-0019 (cut off in the report).

**Note:** gpt-6.1-sol had no PDF and misread at least one finding (FTF-0008). Each item in the queue must be verified against the source before acting — several may be false positives or already-caveated in the text.

## Release gates (v2)
- Gate A (technical): FAIL pre-fix (2 P0s); the 6 fixes above address the confirmed P0s + 4 P1s. Remaining P1s in the queue must be verified/closed.
- Gate C (visual): FAIL — Figs 6.2 and 19.3 are Technical FAIL; Fig 19.1 is Design FAIL; 8 figures are MARGINAL. These must be fixed (regenerate + re-verify at print scale).
- Gates B/D/E: NOT VERIFIED (no external source check, no physical print proof).

## Next actions (ordered by dependency)
1. Fix the 3 figure Technical/Design FAILs (6.2, 19.3, 19.1) — regenerate + vision-verify.
2. Fix the 8 figure MARGINALs (18.1, 23.1, 22.1, 26.1, 6.1, 4.1, 7.2, 11.1) — caption/prose consistency + figure annotation fixes.
3. Verify the 18 remaining P1s in the queue against the source; fix the confirmed ones.
4. Rebuild, re-run the full scan (overflows, stranding, 48 checks), and re-verify the changed figures at print scale.
5. Re-run a gpt-6.1-sol confirmation pass on the changed pages.
