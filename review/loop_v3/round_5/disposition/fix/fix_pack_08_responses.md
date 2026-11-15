# Fix Pack 08 — responses (round_5)

Format: Severity | Location | Problem | Change | Status | Evidence

1. P1 | Ch 26 §8 Step 3 | Hypothesis ties the test to 2,000→3,000 user growth while assumptions hold offered rate (~2.0 rps), concurrency and hit ratio constant, so user growth is operationally neutral | Kept hypothesis/assumptions/result; added four sentences stating why the offered rate stays flat at 1.5× users (declared input capped at the host's ~2.0 rps sustainable ceiling, not a per-user rate; ~100→~150 concurrent implies ~33% lower per-concurrent-user rate) and acknowledging the staged test covers configuration robustness under constant load, not user scaling (a genuine user-scaling test would grow offered load to ~3.0 rps) | FIXED | Both quoted clauses still verbatim at ch26 L111 before the edit; new text inserted after "…rather than treating a user count as an arrival model."; gates check_regressions/check_stale_values pass.

2. P2 | Ch 26 §8 Step 1/Step 2 | 320 ms component labeled "worst-case" while the 450 ms total is labeled "p99"; no equivalence stated | Kept both labels and added one sentence in Step 1 declaring and justifying the worst-case↔p99 equivalence for this declared scenario (worst-case = how components were chosen, p99 = the role the 450 ms total plays; not a claim about measured statistics) | FIXED | Both labels confirmed at ch26 L107 pre-edit ("representative worst-case estimates" / "baseline p99 scenario value"); equivalence sentence now follows "…not a p99 of a separate measured distribution."

3. P2 | Ch 26 §8 Step 2, two-point-model sentence | One sentence nested a parenthesis in a parenthesis with a dash-aside, italics and an identity (10+ asides in the paragraph) | Split into five sentences: main sentence (hit ~50 ms / miss ~250 ms), scenario-input qualification, queue-drain derivation (120+80+50=250), Step 3 load-test caveat, then the CDF statement | FIXED | Original nested sentence confirmed verbatim at ch26 L109 pre-edit; replacement preserves every clause (scenario input, ρ-near-1 inflation, 320→120 ms, both distributions = Step 3 targets) and passes check_md_leaks.

4. P3 | Ch 26 Step 2 vs Table 26-3 (and Steps 0–1, Scenario) | Same unit abbreviated "rps" (10×) and "req/s" (9×) within the chapter | Standardized chapter-26.md on "rps" (book-dominant: 369 rps vs 76 req/s book-wide) — all 9 "req/s" occurrences converted; also converted ch04's single "req/s" (in pack targets); propagation to chapters outside this pack (ch17/ch20 etc.) is outside pack scope | FIXED | Post-edit grep: chapter-26.md "req/s" = 0, "rps" = 19; chapter-04.md "req/s" = 0; check_tables/check_md_leaks pass.

5. P3 | Ch 26 §9 lead-in (line 131) vs Table 26-3 header | Prose says eight fields; table has seven columns (problem solved + triggering symptom merged) | Rewrote lead-in to "seven table columns covering eight fields (problem solved and triggering symptom share one column): …" keeping the eight-field list | FIXED | Quote confirmed at ch26 L134 pre-edit; header still 7 columns; check_tables.py: "column counts consistent".

6. P2 | Ch 26 Table 26-2 (GPU Shard row) + closing note + utilization note | Cache removes 35% of engine load (2.0→1.3 rps) yet modeled SM util rises 45%→68%; note disclaimed instead of explaining | Applied the instruction's first option: Table 26-2 cell 68% → ~29% (45% × 1.3/2.0, same SM-utilization definition at the cached engine load); provenance note now states each value's measurement point (45% at uncached ~2.0 rps, ~29% at cached ~1.3 rps, one definition, direction matches the mechanism); utilization note updated to ~29% | FIXED | 45%/68% pair confirmed at ch26 L107/L119/L124/L130 pre-edit; post-edit "68%" = 0 in ch26; capstone_calc.py and fig_ch26_*.py contain no 68% (no regen needed); gates pass.

7. P2 | Ch 26 §3 Capstone Execution and §8 Step 2 | Rejected "48% (or 47%)" headline referenced a figure never presented in the book | Deleted both 48% references; replaced with positive cost-basis statements (§3: only defensible saving is the marginal-generation-work cache-hit share, no all-in percentage claimed; §8 Step 2: deeper-continuous-batching saving rejected because the lever is rejected, cost statement keeps only the cache-hit share) | FIXED | Both rejection notes confirmed verbatim at ch26 L60/L109 pre-edit; post-edit "48%" = 0 in the whole manuscript; check_regressions still passes (its 48% is arithmetic-only, not a manuscript scan).

8. P2 | Ch 26 §8 Step 3 hypothesis/assumptions | Same defect and same text as item 1 (hypothesis vs constant-load assumptions) | No separate edit — text already fixed under CH26-STEP3-01 | DUPLICATE | Item 1's quoted hypothesis + scaling-assumption clauses are the identical spans; pack rule: second of two items on the same text is DUPLICATE.

9. P3 | Ch 26 §2 (first use of R-codes) | R-01/03/04/05/07/10/13 cited with no definition anywhere in the manuscript | Added a "Rule key (R-codes)" paragraph at the end of §2 stating the rule text for all seven codes, derived from each code's in-chapter usage (no rule list exists elsewhere, so cross-reference was impossible per the instruction) | FIXED | Grep pre-edit: R-codes only in ch26 (lines 54–140), zero definitions book-wide; key now precedes first use (§3 Pattern A) and covers exactly the seven cited codes.

10. P3 | Ch 26 §8 Step 0 vs §26.1 matrix | Step 0 routes to "the matrix's short-input latency-bound rows" — no such row exists (RAG row is Long 8K+) | Added a "Short-prompt RAG Q&A" row to the §2.1 matrix (Short input / Short output / Tail latency and queueing (p99 TTFT) / Semantic response cache, circuit breaker (Ch 26)) and rephrased Step 0 to name that row | FIXED | Matrix rows confirmed at ch26 L29–41 pre-edit with no short-prompt RAG row; row + Step 0 wording verified at L32/L105; pandoc renders the row; check_tables passes.

11. P3 | Ch 26 §9 lead-in vs Table 26-3 | Same sentence and same table as item 5 (seven columns vs eight fields) | No separate edit — text already fixed under CH26-TABLE263-01 | DUPLICATE | Item 5's quoted clause is the identical line-131 sentence; pack rule: second of two items on the same text is DUPLICATE.

12. P3 | Ch 26 §26.2.1 table (source separator) | Five near-equal columns; "First strategy to evaluate" cells wrapped to 7 lines while Workload/Input had padding | Set explicit relative widths in the delimiter row (18/11/12/17/43 dashes → 17.8/10.9/11.9/16.8/42.6%); no cell now wraps beyond ~3 lines and the table still fits the text block | FIXED | pandoc 3.7 on the edited file emits p{…×\real{0.1782/0.1089/0.1188/0.1683/0.4257}} for this table (was five × 0.2000); md_to_latex.fix_colspec converts these to p{frac\linewidth}; check_tables passes (all separator cells ≥3 dashes).

13. P3 | Ch 26 Fig 26.2 caption (figure + caption showed no SLO target) | Loop drawn with no criterion for "validate"; finding's "80 ms" was a misread — source says p99 ≤ 800 ms | Caption edit (preferred path, no generator change): added clause stating what validate compares — measured TTFT p99 against the hypothesis criterion (TTFT p99 < 300 ms, §8 Step 3) under the capstone's p99 ≤ 800 ms TTFT target (§8 Step 0) | FIXED | Caption at ch26 L126 now carries the criterion and the correct 800 ms target (L105); fig_ch26_feedback.py contains no target text and needed no change, so no binary was touched and no regen was required.

14. P2 | Ch 4 §6 serving-configuration bullet | "…so the fleet needs ~6 hosts" attributed the KV/service-time result to prefill throughput (92,000/19,800 = 4.65 → 5) | — | SKIPPED_PREMISE | Defect already gone: current ch04 reads "prefill alone needs ≥5 hosts at average; the KV-residency screen (86 in-flight ÷ 17 slots = 5.06) is the binding bound and raises this to ~6 hosts (§4.3)"; old clause absent.

15. P1 | Ch 4 §3/§6/§8 KV-resident requests per host | §6 derived 436 ÷ 24.1 ≈ 18 while §3/§8 state C ≈ 17.5 unreconciled | — | SKIPPED_PREMISE | Defect already gone: §6 now derives 436 GB ÷ 24.9 GB ≈ 17.5 floored to 17 and relabels 436 ÷ 24.1 ≈ 18 as the input-only figure; §3/§8 both show the 24.9 GB (9.5K resident) denominator; "436 GB ÷ 24.1 GB ≈ 18" as a standalone capacity claim absent.

16. P3 | Ch 4 §4.3 Economic Constraints, Infrastructure bullet | On-demand hourly rental labeled "Capital cost" | — | SKIPPED_PREMISE | Defect already gone: line now reads "On-demand rental (operating) cost ≈ $20/hour ($2.50/GPU-hr)"; "Capital cost" absent from chapter-04.md.

17. P2 | Ch 4 §6 opening vs Fig 4.1 caption | "directly dictates the architectural path" contradicted the caption's "heuristic influence, not deterministic" | — | SKIPPED_PREMISE | Defect already gone: sentence now reads "The six‑dimension characterization informs and constrains the architectural path"; "directly dictates" absent.

18. P2 | Ch 4 §6 operational topology bullet | 99.9% SLA alone presented as requiring multi-region active-active and exactly 2× cost | — | SKIPPED_PREMISE | Defect already gone: bullet now conditions on topology — "99.9% availability alone does not require it, since a single-region multi-AZ design can meet 99.9%…", "not necessarily 2×", plus the UNPRICED/NOT VALIDATED caveat; old sentence absent.

19. P1 | Ch 4 §3 sidebar vs §3 Cost per request | $14.04/1K (wall-clock paid occupancy) vs $3.33/1K and $0.0033/req with no reconciliation | — | SKIPPED_PREMISE | Defect already gone: sidebar column header states the hour basis ("wall-clock paid-occupancy cost ÷ active-hours volume"), the active-hours row (6 × 173.3 h × $20 = $20,800 → ≈ $3.33) exists, and §3 bridges the bases ("the sidebar's $87,600/month… assumes the fleet is paid for all 730 wall-clock hours").

20. P2 | Ch 4 §6 memory planning vs §3/§8 | Three values for one quantity (~18–20, ≈18, 17.5→17) unreconciled | — | SKIPPED_PREMISE | Defect already gone: "around ~18–20" absent; §6 states ~17 (436 ÷ 24.9 ≈ 17.5 floored to 17) with the input-only 24.1 GB ≈ 18 reconciliation; canonical box names both KV bases (24.1 GB input-only, 24.9 GB resident slot-counting).

21. P2 | Ch 4 §5 Common Mistakes | Tokenization and context-window bullets re-ran Ch 1 §5 | — | SKIPPED_PREMISE | Defect already gone: those bullets replaced by Ch-4-specific mistakes ("Using the ~10 s planning round as Little's-law W", "Sizing KV and the fleet from the mean context and the average fleet") with an explicit cross-reference ("token ≈ word, context window as free capacity — are Ch 1 §5's; measure there, not re-derived here"); old bullet text absent.

22. P3 | Ch 4 §3 canonical box, Average arrival rate row | 24×7 extrapolation used a 30-day month (25.9M) beside an active-hours figure on the 260-workday calendar (6.24M) | — | SKIPPED_PREMISE | Defect already gone: row now computes ~18.7M/month on the same 260-workday calendar (10 × 3,600 × 24 × 260/12 = 18,720,000; ~9,360/user/month); "~25.9M" absent.

23. P3 | Front matter + Ch 3 §8 (references quoted from Ch 4 §4, Ch 4 §3, Ch 2 §1, Ch 3 §8) | §chapter.section convention never stated; redundant "Ch 3 §3.6" states the chapter twice | Stated the convention once in the front matter (render/latex/preface.tex, "Reading conventions": "Section cross-references use the § chapter.section form: a bare §N.M refers to chapter N, section M — so §1.4 is Ch. 1, Section 4 (Measurement)…"; lead-in updated "Three" → "Four conventions") and normalized "Ch 3 §3.6" → "Ch 3 §6" in chapter-03.md | FIXED | Pre-edit grep across the repo: no convention statement anywhere and "Ch 3 §3.6" present once (ch03 L202); post-edit: convention present in preface.tex, "§3.6" = 0; the new block compiles under lualatex (mini test, exit 0). Ch 1/Ch 2 references themselves needed no change.

24. P3 | Ch 4 §3 Arithmetic Walk-Through step 2 | "(Chapter 8)" cited for the fleet-sizing 8.6 s service time; Ch 8 defers the derivation to Ch 17 | — | SKIPPED_PREMISE | Defect already gone: sentence now reads "(Chapters 16–17 use it for Little's-law occupancy; Chapter 8 gives the prefill + decode decomposition)"; "(Chapter 8)" as a fleet-sizing cite absent.

## Counts

- FIXED: 12 (CH26-STEP3-01, CH26-STEP2-01, CH26-STEP2-02, CH26-UNITS-01, CH26-TABLE263-01, CH26-TABLE262-SMUTIL-01, CH26-03-48PCT-01, CH26-02-RRULES-01, CH26-08-STEP0-01, TBL-26.2-01, FIG-26.2-05, BOOK-XREF-21)
- SKIPPED_PREMISE: 10 (CH4-02, CH4-01, CH4-07, CH4-05, CH4-08, CH4-COSTBASIS-02, CH4-KVSLOTS-05, CH4-MISTAKES-12, CH4-MONTHBASIS-16, CH4-CANON-LEDGER-22)
- DUPLICATE: 2 (CH26-08-HYPOTHESIS-01, CH26-09-FIELDS-01)
- NEEDS_REGEN: 0
- Total: 24

## Files changed

- design/manuscript/chapter-26/chapter-26.md (items 1–7, 9–10, 12–13)
- design/manuscript/chapter-04/chapter-04.md (item 4 unit standardization only; items 14–22, 24 premises already satisfied)
- design/manuscript/chapter-03/chapter-03.md (item 23, §3.6 → §6 normalization)
- render/latex/preface.tex (item 23, cross-reference convention in front matter)

## Gates

check_tables.py OK; check_md_leaks.py OK; check_stale_values.py OK; check_regressions.py OK (all numeric regression checks passed, stale-value gate OK). No figure binary touched; no PDF rebuild.