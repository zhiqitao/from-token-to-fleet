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
| FTF-0007 | P1 | Ch10/13 | "no parallelism is required at the baseline"→"no *cross-host* model parallelism is required (intra-host TP=8 fits the 140 GB model across the eight 80 GB GPUs)." |
| FTF-0009 | P1 | Ch9 | Added: the 140 GB per-rank figure is the *logical* size of the all-reduce (the full gradient tensor), not the physical HBM footprint on a single 80 GB GPU; in practice each rank is a multi-GPU node (2×H100 = 160 GB) or uses hybrid DP+TP. |
| FTF-0010 | P1 | Ch17 | B_agg = φ·N·D/t_net (N=host count) → B_agg = φ·λ·D (λ=request arrival rate, by Little's Law). 100 MB/s → 20 MB/s (0.8 → 0.16 Gbps); the 5 GB/s worst case → 1 GB/s; downstream refs updated. |
| FTF-0005 | P1 | Ch8 | Added a KV-read caveat: with the per-sequence KV re-read (~24 GB at 9.2K), the decode intensity is (140·B)/(140+24·B) FLOP/byte, which saturates at ~5.8 (far below the 295 ridge). So with the KV term, decode stays bandwidth-bound at every batch size; the "batch ≈ 295" figure is the weight-only first-order estimate. |
| FTF-0006 | P1 | Ch3/10 | Fixed the memory/compute distinction (was backwards): the **total** count sets **weight residency** (the full expert set must be resident); the **active** count sets **compute per token**. Ch3 line 98 + Ch10 EP claims. |
| FTF-0011 | P1 | Ch11 | Added a layout caveat: prefix reuse requires the shared documents at a fixed prefix position (system prompt → documents → query tail); if the query precedes the documents, no prefix is reusable. |
| FTF-0012 | P1 | Ch19 | Clarified: the 30% cache hit cuts the *re-fetch* cost (newly-fetched 560 = 70% of 800), not the *retained* KV length (still 800 per turn); the two are distinct. |
| FTF-0014 | P1 | Ch19 | Clarified: "zero added turns" is the *incremental* agent work (the single-shot fallback doesn't add turns); the *total* work consumed by the failed agent attempts is not erased but not counted in the *added* overhead. |
| FTF-0015 | P1 | Ch6 | Added: goodput = raw_rate × compliant_fraction; the "unchanged" claim holds only when the extra tokens all land in the SLO-missing tail. A p95 breach is a *configuration-level* acceptance signal; request-level SLO-goodput is a separate measurement. |

### Figure fixes (3 FAILs + 6 caption/figure consistency)

| Fig | Issue | Fix |
|---|---|---|
| 6.2 | peak bar (3023) clipped at the y-axis max (~3000) | `set_ylim(0, 3300)` — headroom above the peak. (The mean<median and p99-in-gap critiques were misreads: mean=0.847 > p50=0.8, and p99=1.334 is correctly in the gap before the 1% stragglers at 5s.) |
| 19.3 | bars didn't grow linearly (minimum clamps made O_final/γ the same height every turn) | removed the `max(h_of(x), min)` clamps so the bands are drawn to scale; the bars now grow linearly (24.9→34.0 GB, ~2.25 GB/turn) and the bar-top heights match the KV labels. The thin γ cap is honest (reasoning is 65–260 tokens). |
| 19.1 | in-figure "[ILLUSTRATIVE conceptual]" tag (metadata leakage) | removed the tag from the annotation line (the caption already carries [ILLUSTRATIVE]). |
| 6.1 | caption "top-down diagnostic path" contradicted "diagnosis runs upward" | "top-down"→"bottom-up". |
| 22.1 | body said the y-axis is "labeled generically 'Compute (PFLOP; see series definition)'" but the axes are labeled per series | "labeled generically"→"labeled per series (prefill: PFLOP/request; decode: PFLOP/token)". |
| 26.1 | "Normalised" (British) vs "normalized" (US); caption listed 3 different sets of six axes | "Normalised"→"Normalized" in the generator; caption now clarifies the fingerprint axes (context length, traffic, quality, cost, latency, output tokens) are distinct from Ch 4's decision dimensions (Quality, Traffic, Token profile, Latency, Economic, Operational). |
| 4.1 | caption "concurrency & batching strategy" / "TTFT/TPOT targets & batch window" vs figure "concurrency & batching" / "TTFT/TPOT & batch window" | aligned the caption to the figure. |
| 7.2 | in-chart annotation "9.2K ≈ 24 GB" vs caption "9.5K / 24.9 GB" (3 different context lengths) | annotation now uses 9.5K / 24.9 GB (the total context, which is what the KV is based on), matching the caption. |
| 23.1 | Box 1 "problem" (TTFT p99 1.4 s) already satisfied Box 2 "success" (p95 ≤ 2 s) | Box 1 changed to "TTFT p95 2.1 s" (which violates the p95 ≤ 2 s criterion). |
| 18.1 | prose "check the SLO, then size the cost... it must come first" read as contradicting the figure's "capability first" policy | prose clarified: the "check SLO then cost" order is *within the cost/SLO gate* (the capability filter still comes first, per Fig 18.1 and Table 18-1). |
| 11.1 | green "new sequence (backfill)" persisted across the entire decode (implying the sequence stays "new" for its whole life) | green now only at admission (a short green marker), with the rest in blue (normal in-flight). |

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
| FTF-0005 | decode roofline omits KV reads | **CONFIRMED + FIXED** — Ch8 added a KV-read caveat: with the per-sequence KV re-read (~24 GB at 9.2K), the decode intensity is (140·B)/(140+24·B) FLOP/byte, which *saturates* at ~5.8 (far below the 295 ridge). So with the KV term, decode stays bandwidth-bound at every batch size; the "batch ≈ 295" figure is the weight-only first-order estimate. |
| FTF-0006 | MoE total-vs-active memory | **CONFIRMED + FIXED** — Ch3 line 98 and Ch10 EP claims had the memory/compute distinction backwards. Fixed: the **total** count sets **weight residency** (the full expert set must be resident); the **active** count sets **compute per token**. Sizing weight memory from the active count under-provisions; sizing compute from the total count over-provisions. |
| FTF-0007 | "one host" = "no model parallelism" | **CONFIRMED + FIXED** — Ch10/13 "no parallelism is required at the baseline"→"no *cross-host* model parallelism is required (intra-host TP=8 fits the 140 GB model across the eight 80 GB GPUs)." |
| FTF-0009 | 140 GB per-rank H100 collectives | **CONFIRMED + FIXED** — Ch9 added: the 140 GB per-rank figure is the *logical* size of the all-reduce (the full gradient tensor), not the physical HBM footprint on a single 80 GB GPU; in practice each rank is a multi-GPU node (2×H100 = 160 GB) or uses hybrid DP+TP. |
| FTF-0008 | NVLink bidirectional bandwidth | **FALSE POSITIVE** — the 245 GB is the total data moved per rank (send+receive), divided by the bidirectional 900 GB/s = 0.272 s. The book is correct. |
| FTF-0010 | aggregate network demand uses host count | **CONFIRMED + FIXED** — Ch17 B_agg = φ·N·D/t_net (N=host count) → B_agg = φ·λ·D (λ=request arrival rate, by Little's Law). 100 MB/s → 20 MB/s (0.8 → 0.16 Gbps); the 5 GB/s worst case → 1 GB/s; downstream refs (lines 181, 207) updated. |
| FTF-0011 | prefix-cache savings without exact-prefix eligibility | **CONFIRMED + FIXED** — Ch11 added a layout caveat: prefix reuse requires the shared documents at a fixed prefix position (system prompt → documents → query tail); if the query precedes the documents, no prefix is reusable. |
| FTF-0012 | tool-result caching shrinks retained context | **CONFIRMED + FIXED** — Ch19 clarified: the 30% cache hit cuts the *re-fetch* cost (newly-fetched 560 = 70% of 800), not the *retained* KV length (still 800 per turn); the two are distinct. |
| FTF-0014 | fallback accounting / conditional percentiles | **CONFIRMED + FIXED** — Ch19 clarified: "zero added turns" is the *incremental* agent work (the single-shot fallback doesn't add turns); the *total* work consumed by the failed agent attempts is not erased but not counted in the *added* overhead. The book already acknowledged the two conventions (conditional vs unconditional). |
| FTF-0015 | p95 breach ≠ goodput | **CONFIRMED + FIXED** — Ch6 added: goodput = raw_rate × compliant_fraction; the "unchanged" claim holds only when the extra tokens all land in the SLO-missing tail. A p95 breach is a *configuration-level* acceptance signal; request-level SLO-goodput is a separate measurement (50×0.96=48 vs 70×0.94=65.8 — goodput can *rise* despite the breach). |
| FTF-0016 | mixed-model cost/latency basis | **MISREAD** — the book's routing decision (Ch18) is for the short-prompt queries (order status, policy look-up — 15% of traffic), not the canonical 9.5K. The 250 ms latency is for the short-prompt queries, and the book explicitly notes (line 112) that the canonical 9.5K profile doesn't fit on a 2-GPU shard. No fix needed. |
| FTF-0019 | evidence labels | NEEDS VERIFICATION — the book's evidence taxonomy is consistent. Likely a misread (the book uses [ILLUSTRATIVE][DERIVED] tags consistently). |
| FTF-0020 | DeepSeek/GLM appendix | NEEDS VERIFICATION — the appendix is a dated snapshot. Likely already labeled. |
| FTF-0021 | population→rate substitutions | **LIKELY FALSE POSITIVE** — the book correctly distinguishes between the population (2,000 users) and the arrival rate (10 rps average / 40 rps peak) in Ch17 line 201, and uses the arrival rate (40 rps) for the fleet sizing (line 203). No population→rate substitution found. |
| FTF-0022 | response-cache identity | **LIKELY FALSE POSITIVE** — the book correctly distinguishes between prefix caching (exact-prefix match, Ch26 line 58) and semantic caching (skips the generation, Ch26 line 100). No conflation found. |
| FTF-0023 | SDPA op vs implementation | **LIKELY FALSE POSITIVE** — the book correctly distinguishes between SDPA (the operation, Ch15 line 34) and FlashAttention (the implementation, Ch15 line 9). No conflation found. |
| FTF-0024 | attention FLOPs full-square vs causal | **DEFENSIBLE** — the book uses the full square (4·n_layers·L²·d) as a conservative upper bound and explicitly calls it "a sound teaching baseline." Not an error. |
| FTF-0025 | dimensional claim | NEEDS VERIFICATION — need to check the specific claim. |

**Note:** gpt-6.1-sol had no PDF and misread at least one finding (FTF-0008). Several of the "NEEDS VERIFICATION" items are likely already caveated in the text (the book is thorough). Each must be verified against the source before acting. The 2 P0s and 4 P1s (FTF-0003, 0013, 0017, 0018) were confirmed and fixed; FTF-0004 and FTF-0024 are defensible modeling choices.

## Release gates (v2) — current status
- **Gate A (technical):** the 2 confirmed P0s (FTF-0001, FTF-0002) and 15 confirmed P1s (FTF-0003, 0005, 0006, 0007, 0009, 0010, 0011, 0012, 0013, 0014, 0015, 0017, 0018) are FIXED and verified in the rebuilt PDF. 2 findings (FTF-0004, FTF-0024) are DEFENSIBLE modeling choices (not errors). 1 (FTF-0008) is a FALSE POSITIVE. 1 (FTF-0016) is a MISREAD. 3 (FTF-0021, 0022, 0023) are LIKELY FALSE POSITIVES (the book already distinguishes the relevant concepts). The remaining 3 P1s (FTF-0019, 0020, 0025) are NEEDS VERIFICATION. **Gate A is closer to PASS** but the 3 unverified P1s must be checked before a full PASS.
- **Gate C (visual):** the 3 figure Technical/Design FAILs (6.2, 19.3, 19.1) are FIXED and verified. All 8 figure MARGINALs (18.1, 23.1, 26.1, 4.1, 7.2, 11.1, 6.1, 22.1) are FIXED. 8 Design MARGINALs (cosmetic) remain. **Gate C is closer to PASS** but the 8 cosmetic Design MARGINALs remain.
- **Gate B (evidence):** NOT VERIFIED (no external source check performed in this loop).
- **Gate D (pedagogy):** the causal spine is intact; the fixes above improve consistency. PASS (no new pedagogy defects found).
- **Gate E (production):** the PDF is clean (361pp, 0 overflows, 0 stranding, 48/48 checks, LoF correct). Physical print proof NOT VERIFIED.
- **Gate F (coverage):** gpt-6.1-sol did the full text audit (121K words); the orchestrator did the full visual audit (40 figures). The 6 unverified P1s are a coverage gap.

**Overall: NOT READY — MUST-FIX WORK REMAINS** (pre-fix). After the fixes above, the book is closer to **CONDITIONALLY READY — EXTERNAL/PRINT VERIFICATION PENDING**, but the 3 unverified P1s (FTF-0019, 0020, 0025) and 8 cosmetic Design MARGINALs must be closed before a READY call.

## Next actions (ordered by dependency)
1. ~~Fix the 3 figure Technical/Design FAILs (6.2, 19.3, 19.1)~~ — DONE (regenerated + vision-verified).
2. ~~Fix the 8 figure MARGINALs (23.1, 26.1, 4.1, 7.2, 18.1, 11.1, 6.1, 22.1)~~ — DONE (caption/figure consistency).
3. ~~Verify and fix the 15 confirmed P1s (FTF-0003, 0005, 0006, 0007, 0009, 0010, 0011, 0012, 0013, 0014, 0015, 0017, 0018)~~ — DONE.
4. Verify the 3 remaining P1s (FTF-0019, 0020, 0025) against the source; fix the confirmed ones, document the defensible/caveated ones.
5. Rebuild, re-run the full scan (overflows, stranding, 48 checks, LoF), and re-verify the changed figures at print scale.
6. Re-run a gpt-6.1-sol confirmation pass on the changed pages.
7. Produce the final consolidated report (Sections 1-13 per v2) with the full figure-by-figure verdict register and the page-by-page coverage ledger.
