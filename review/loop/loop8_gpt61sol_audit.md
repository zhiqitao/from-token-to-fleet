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

### Text fixes (6 confirmed gpt-6.1-sol findings)

| ID | Sev | Location | Fix |
|---|---|---|---|
| FTF-0001 | P0 | Ch16/21/26 | TCO repriced from 24×7 (26M req/mo) to the active business-hours schedule (6.24M req/mo) per Ch4's explicit instruction. Self-host $5.7→$23.7/1K, cloud $2.8→$11.7/1K, managed $541K→$129.8K/mo, 30-host $8.4→$34.8/1K. Table 16-1, Ch21 bad-release cost, Ch26 $0.0057→$0.0237 all updated. |
| FTF-0002 | P0 | Ch26 capstone | Baseline is a single 8×H100 node (already TP=8), so "unsharded baseline"→"single-node baseline"; the 20% per-token saving is from deeper continuous batching on the already-sharded engine (not double-counted sharding); Table 26-2 $0.003→$0.012/query (consequence of FTF-0001). |
| FTF-0003 | P1 | Ch16 | "FP8 KV cuts the peak fleet to ~10"→clarified: FP8 cuts the *KV-bound* fleet to ~10, but the true peak fleet stays ~20 (the throughput bound ⌈40/2.0⌉, independent of KV size); fleet = max(N_throughput, N_KV). |
| FTF-0013 | P1 | Ch19 | Agent token accounting: "call 3 = 9,200 + 2×(800+65) + 300 ≈ 12,095"→"3×(800+65) = 12,095" (the formula gave 11,230); task_input 9,200+10,350+12,095=31,645→9,200+10,365+12,095=31,660 (10,350 was a 15-token error vs the table's 10,365). |
| FTF-0017 | P1 | Ch24 | PIES "equivalence relation"→"deterministic clustering rule" (thresholded NLE ≤ 0.25 is not transitive: 0000~0001, 0001~0011, but 0000!~0011). |
| FTF-0018 | P1 | Ch24 | False-positive rate "≈13 per 1,000 queries"→"≈0.05 per 1,000 (1.3% of the 4.1 interventions per 1,000)" — the false positives cannot exceed the total interventions. |

### Figure fixes (3 FAILs + 3 caption consistency)

| Fig | Issue | Fix |
|---|---|---|
| 6.2 | peak bar (3023) clipped at the y-axis max (~3000) | `set_ylim(0, 3300)` — headroom above the peak. (The mean<median and p99-in-gap critiques were misreads: mean=0.847 > p50=0.8, and p99=1.334 is correctly in the gap before the 1% stragglers at 5s.) |
| 19.3 | bars didn't grow linearly (minimum clamps made O_final/γ the same height every turn) | removed the `max(h_of(x), min)` clamps so the bands are drawn to scale; the bars now grow linearly (24.9→34.0 GB, ~2.25 GB/turn) and the bar-top heights match the KV labels. The thin γ cap is honest (reasoning is 65–260 tokens). |
| 19.1 | in-figure "[ILLUSTRATIVE conceptual]" tag (metadata leakage) | removed the tag from the annotation line (the caption already carries [ILLUSTRATIVE]). |
| 6.1 | caption "top-down diagnostic path" contradicted "diagnosis runs upward" | "top-down"→"bottom-up". |
| 22.1 | body said the y-axis is "labeled generically 'Compute (PFLOP; see series definition)'" but the axes are labeled per series | "labeled generically"→"labeled per series (prefill: PFLOP/request; decode: PFLOP/token)". |
| 26.1 | "Normalised" (British) vs "normalized" (US) | "Normalised"→"Normalized" in the generator. |

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

## Remaining gpt-6.1-sol P1s — verification status

| ID | Topic | Verdict |
|---|---|---|
| FTF-0004 | fractional concurrency 17 vs 17.5 | **DEFENSIBLE** — 17.5 is the average concurrency per host (correct for the fleet total ⌈344/17.5⌉=20); 17 is the whole-slot floor for a single host. Not an error. |
| FTF-0005 | decode roofline omits KV reads | NEEDS VERIFICATION — the book's decode FLOP/token is the parameter term; KV reads are a separate bandwidth term (Ch 8). Likely already caveated. |
| FTF-0006 | MoE total-vs-active memory | NEEDS VERIFICATION — the book distinguishes active (compute) vs total (residency) params. Likely already caveated. |
| FTF-0007 | "one host" = "no model parallelism" | NEEDS VERIFICATION — the book's "one 8×H100 host" is a single node with intra-node TP=8. The "no model parallelism" phrasing (if present) is imprecise. |
| FTF-0008 | NVLink bidirectional bandwidth | **FALSE POSITIVE** — the 245 GB is the total data moved per rank (send+receive), divided by the bidirectional 900 GB/s = 0.272 s. The book is correct. |
| FTF-0009 | 140 GB per-rank H100 collectives | NEEDS VERIFICATION — the 140 GB is the total model (sharded across 8 ranks). The per-rank collective volume is 140/8 = 17.5 GB. |
| FTF-0010 | aggregate network demand uses host count | NEEDS VERIFICATION — the book's network demand is per-host, not aggregate. Likely already caveated. |
| FTF-0011 | prefix-cache savings without exact-prefix eligibility | NEEDS VERIFICATION — the book's prefix caching requires exact-prefix matches. Likely already caveated. |
| FTF-0012 | tool-result caching shrinks retained context | NEEDS VERIFICATION — the book's tool-result caching is a separate mechanism. Likely already caveated. |
| FTF-0014 | fallback accounting / conditional percentiles | NEEDS VERIFICATION — the book's fallback is a separate path. Likely already caveated. |
| FTF-0015 | p95 breach ≠ goodput | NEEDS VERIFICATION — the book distinguishes p95 from goodput. Likely already caveated. |
| FTF-0016 | mixed-model cost/latency basis | NEEDS VERIFICATION — the book's mixed-model routing is a separate section. Likely already caveated. |
| FTF-0019 | evidence labels | NEEDS VERIFICATION — the book's evidence taxonomy is consistent. Likely a misread. |
| FTF-0020 | DeepSeek/GLM appendix | NEEDS VERIFICATION — the appendix is a dated snapshot. Likely already labeled. |
| FTF-0021 | population→rate substitutions | NEEDS VERIFICATION — the book distinguishes population from request rate. Likely already caveated. |
| FTF-0022 | response-cache identity | NEEDS VERIFICATION — the book's response caching is a separate mechanism. Likely already caveated. |
| FTF-0023 | SDPA op vs implementation | NEEDS VERIFICATION — the book's SDPA is the operator, not the implementation. Likely already caveated. |
| FTF-0024 | attention FLOPs full-square vs causal | **DEFENSIBLE** — the book uses the full square (4·n_layers·L²·d) as a conservative upper bound and explicitly calls it "a sound teaching baseline." Not an error. |
| FTF-0025 | dimensional claim | NEEDS VERIFICATION — need to check the specific claim. |

**Note:** gpt-6.1-sol had no PDF and misread at least one finding (FTF-0008). Several of the "NEEDS VERIFICATION" items are likely already caveated in the text (the book is thorough). Each must be verified against the source before acting. The 2 P0s and 4 P1s (FTF-0003, 0013, 0017, 0018) were confirmed and fixed; FTF-0004 and FTF-0024 are defensible modeling choices.

## Release gates (v2) — current status
- **Gate A (technical):** the 2 confirmed P0s (FTF-0001, FTF-0002) and 4 confirmed P1s (FTF-0003, 0013, 0017, 0018) are FIXED and verified in the rebuilt PDF. 2 findings (FTF-0004, FTF-0024) are DEFENSIBLE modeling choices (not errors). 1 (FTF-0008) is a FALSE POSITIVE. The remaining 16 P1s are NEEDS VERIFICATION (likely already caveated in the text). **Gate A is closer to PASS** but the 16 unverified P1s must be checked before a full PASS.
- **Gate C (visual):** the 3 figure Technical/Design FAILs (6.2, 19.3, 19.1) are FIXED and verified. 6 more figure MARGINALs (18.1, 23.1, 26.1, 4.1, 7.2, 11.1) — 23.1, 26.1, 4.1, 7.2 are FIXED; 18.1 and 11.1 remain (figure-generator alignment issues). 8 Design MARGINALs (cosmetic) remain. **Gate C is closer to PASS** but 18.1 and 11.1 need figure fixes.
- **Gate B (evidence):** NOT VERIFIED (no external source check performed in this loop).
- **Gate D (pedagogy):** the causal spine is intact; the fixes above improve consistency. PASS (no new pedagogy defects found).
- **Gate E (production):** the PDF is clean (361pp, 0 overflows, 0 stranding, 48/48 checks, LoF correct). Physical print proof NOT VERIFIED.
- **Gate F (coverage):** gpt-6.1-sol did the full text audit (121K words); the orchestrator did the full visual audit (40 figures). The 16 unverified P1s are a coverage gap.

**Overall: NOT READY — MUST-FIX WORK REMAINS** (pre-fix). After the fixes above, the book is closer to **CONDITIONALLY READY — EXTERNAL/PRINT VERIFICATION PENDING**, but the 16 unverified P1s and 2 remaining figure MARGINALs (18.1, 11.1) must be closed before a READY call.

## Next actions (ordered by dependency)
1. ~~Fix the 3 figure Technical/Design FAILs (6.2, 19.3, 19.1)~~ — DONE (regenerated + vision-verified).
2. ~~Fix the 4 figure MARGINALs (23.1, 26.1, 4.1, 7.2)~~ — DONE (caption/figure consistency).
3. Fix the 2 remaining figure MARGINALs (18.1 green-branch alignment + prose tier/keyword scheme; 11.1 non-monotonic blue width + green "new" persisting) — figure-generator fixes.
4. Verify the 16 unverified P1s (FTF-0005, 0006, 0007, 0009, 0010, 0011, 0012, 0014, 0015, 0016, 0019, 0020, 0021, 0022, 0023, 0025) against the source; fix the confirmed ones, document the defensible/caveated ones.
5. Rebuild, re-run the full scan (overflows, stranding, 48 checks, LoF), and re-verify the changed figures at print scale.
6. Re-run a gpt-6.1-sol confirmation pass on the changed pages.
7. Produce the final consolidated report (Sections 1-13 per v2) with the full figure-by-figure verdict register and the page-by-page coverage ledger.
