# fix_pack_10 responses — round_5 disposition (24 items: ch25 + ch06 + ch22)

Format: Severity | Location | Problem | Change | Status | evidence

1. P2 | Ch 25 §4 Measurement item 1 (chapter-25.md L141-142) | the stated formula evaluates to 24.117 GB ≈ 24.1, text printed 24.2 | 24.2 GB → 24.1 GB in the §4 formula result and in the same item's envelope sentence ("while the 24.1 GB KV is held per request in flight") | FIXED | 2×80×9,200×8,192×2 = 24,117,248,000 B = 24.117 GB (recomputed); grep "24.2" over design/manuscript *.md → 0 hits, so no downstream text depended on it (Table 22-1 already prints ~24.1).

2. P1 | Ch 25 §7 preamble (L239) | universal "Each item below is a hypothesis … none has FACT instrumentation" is falsified by the same list's [1P][FACT] Tooling-gaps bullet | reworded to "Each item below is either an open hypothesis or, where tagged [1P][FACT], a factual observation — the open items have no FACT instrumentation yet:" | FIXED | new preamble present verbatim before the list; the [FACT] bullet (L244) untouched; grep "hypothesis awaiting verification" → 0 hits.

3. P3 | Ch 25 §6 Integration-with-CI bullet (L176) | CI rule requires a Rationale field the copy-ready template (§25.3.1) does not contain | "a status, a rationale, and at least one evidence tag" → "a status, a trade-offs section, and at least one evidence tag" (template carries Status, Trade-offs & consequences, Evidence) | FIXED | grep "a rationale, and at least" → 0 hits; "a trade-offs section" present; template section dump confirms Trade-offs & consequences at L104.

4. P1 | Ch 25 §8 ADR 0017 Context (L257) and Consequences → Positive bullet (L260) | ~15% KV term / ~1 FLOP/byte are batch-1 values stated at the ADR's own C ≈ 17.5 operating point, where KV dominates and FP8 KV's benefit is materially understated | Context's intensity now labelled "— ~1 FLOP/byte at batch 1"; Positive bullet recomputed at C ≈ 17.5: KV read 17.5 × ~24.9 GB ≈ 435.6 GB (FP16) vs 140 GB weights, so halving KV-read bytes cuts decode memory traffic ≈38% (575.6 → 357.8 GB) and raises intensity ≈4.3 → ≈6.9 FLOP/byte; the ~15% / ~1 FLOP/byte figures kept only with the batch-1 label | FIXED | python recompute: 435.6 GB ✓, 1−357.8/575.6 = 37.8% ✓, 2.45e12/5.756e11 = 4.26 ✓, 2.45e12/3.578e11 = 6.85 ✓, batch-1 share 24.9/(24.9+140) = 15.1% ✓; grep "nearly unchanged" → 0 hits.

5. P2 | Ch 25 §3 ADR 0016, after Evidence Tags (L67) | the flagship worked ADR carries none of the apparatus blocks §3.1 calls most important; the only record carrying them (ADR 0015) is a HOLD | added a *Record scope* paragraph: ADR 0016 is a deliberately minimal record (the five core fields of §25.1 plus Rationale and Evidence Tags), and the template's apparatus blocks — decision owner, validation plan, rollback plan, review trigger, falsification path — are demonstrated in full in the worked HOLD record ADR 0015 | FIXED | paragraph present immediately before §3.1; 0015's five blocks verified at L227-235; no apparatus claim made for ADR 0017 (it carries none — the pack's own evidence says so).

6. P2 | Ch 25 ADR 0015 Context (L193) + Ch 26 Table 26-2 closing note (chapter-26.md L124) | ~$20.8/1K (ch25) and ~$11.6/1K (ch26) are unreconciled managed-API per-request prices for the same canonical volume | both sides now state scope: ch25's ~$20.8/1K is the *frontier-class* API tier ($2/$8 per 1M, Ch 16) vs Ch 4's *mid-tier* ~$11.6/1K ($1.20/$2.00 per 1M = $0.01164/request) — same 9,200/300 token mix and 6.24M requests/mo, different model tier, not interchangeable; the ch26 note names both tiers and cross-references ADR 0015 | FIXED | scopes traced to source, not invented: ch04 L195 "The *frontier-class* API used in the Ch 16 TCO comparison … ~$0.0208 per request" and ch16 L126 "$0.0208 per request … = $20.80 per 1,000 requests"; grep "frontier-class" → 1 hit in ch25, 1 in ch26. Price date and included-services are stated nowhere in the book, so none was added.

7. P3 | Ch 25 ADR 0016 Consequences → Positive (L57) + Ch 26 §3 (chapter-26.md L54) | ADR 0016 (Accepted) switches the fleet to BF16 while ch25/ch26 still frame the canonical deployment as FP16, with no sentence saying whether the canonical precision label changed | added to 0016's Positive consequence: "Accepted, this record sets the canonical deployment's precision label to BF16; because FP16 and BF16 are both 2 B/parameter, every footprint, KV and cost figure in this handbook is unchanged"; Ch 26 §3 now reads "RAG Q&A over a 70B dense FP16 model (FP16 label; see ADR 0016)." | FIXED | both sentences present verbatim (grep "precision label to BF16" → 1, "FP16 label; see ADR 0016" → 1); the 2 B/parameter non-effect is already sourced in-chapter (L49, L143), so no new claim was introduced.

8. P3 | Ch 25 §4 item 1 parenthetical (L141) | the sentence derives KV at 9.2K (24.1 GB) then multiplies by 17 with the 9.5K-maximum figure (24.9 GB) without saying the context length changed | sentence now: "per-request KV at 9.2K = 24.1 GB (…): KV, already inside the ~436 GB KV budget at concurrency — at concurrency the 9.5K-maximum per-request figure applies (17 × ~24.9 GB ≈ 423 GB)" | FIXED | both context lengths named in the one sentence; 17 × 24.9 = 423.3 ✓; value reads 24.1 because item 1 corrected it first — distinct defect (missing labels) in the same sentence, so both were applied, not deduped.

9. P3 | Ch 25 §6 lead-in (L170) | category slip: subject "the handbook" does not match a list of fleet-team practice consequences | → "Introducing ADRs into the fleet team's engineering practice has several architecture-level consequences:" | FIXED | grep "\"From Token to Fleet\" handbook has several" → 0 hits; the five bullets below are unchanged.

10. P3 | Ch 25 §7 preamble (L239) | same preamble sentence as item 2 | — | DUPLICATE | identical sentence already reworded under CH25-02; no second edit made.

11. P2 | Ch 6 §3 regime-detection prefill bullet | BF16 label for 0.989 PFLOPS drifts from Ch 8 / Table 8-1's FP16 | — | SKIPPED_PREMISE | current source already reads "~0.989 PFLOPS dense BF16 peak (FP16/BF16: same H100 peak) (1.19 > 0.989)" — the pack's option-B parenthetical is present (sibling round-5 edit to chapter-06.md).

12. P2 | Ch 6 §1 metric hierarchy, workload bullet | TTFT/TPOT (SLO targets) placed inside the workload layer | — | SKIPPED_PREMISE | current bullet ends "~9,200 input + ~300 output tokens per request." and the serving row now carries "the canonical SLO targets are TTFT 1.2 s / TPOT ~25 ms".

13. P2 | Ch 6 §2 Mental Model | "when numbers are healthy, the chain confirms our architecture was right" | — | SKIPPED_PREMISE | current text: "… so when numbers are healthy, the chain shows the system meets the SLO under the observed workload."

14. P2 | Ch 6 §1 workload bullet (+ resource bullet) | concurrency and queue depth presented as exogenous inputs | — | SKIPPED_PREMISE | current bullet: "These are the independent variables — the *offered* load … Admitted concurrency is a serving/scheduler state (Little's law), not a workload input", and queue depth now sits in the serving row as "**queue depth** (a scheduler state)", removed from the resource row.

15. P3 | Ch 6 §1 serving-metrics bullet | goodput defined without a per-second denominator | — | SKIPPED_PREMISE | current text: "**goodput** (tokens per second that actually meet the SLO)".

16. P3 | Ch 6 Fig 6.1 caption | caption points at §6.2 for an example that lives in §6.3 | — | SKIPPED_PREMISE | current caption: "see §6.3 for the p95 TTFT worked example."

17. P3 | Ch 6 §7 first bullet | "525% simulated throughput" ambiguous between increase and of-baseline | — | SKIPPED_PREMISE | current text: "Mooncake: a 525% throughput increase (simulated) and 75% more requests [S4][1P][FACT]" — "throughput increase" fixes the baseline ambiguity the finding named.

18. P3 | Fig 6.2 — generator render/fig_ch6_hist.py → design/manuscript/chapter-06/figures/fig-06-0602.png + .pdf | p90 (0.94) and p95 (0.99) shared colour and dash pattern in the rendered figure (0.05 s apart) | regenerated ONLY fig-06-0602 with `python render/regen_one.py render/fig_ch6_hist.py` (RC=0, PNG+PDF written); no generator edit was needed — the script already carries pct_ls {50:'--', 90:'-.', 95:':'} (committed 1b4a9bb0) but the binary was stale (PNG 2026-11-12 15:47 pre-dates that commit) | FIXED | pixel run-lengths of the new PNG: p90 = 40 px dash + 5 px dot alternating, p95 = uniform 5–6 px dots, p50 = ~23 px dashes — three distinct patterns; grayscale 4× crop vision read-back: "the left line (p90) is a dash-dot pattern … the right line (p95) … uniform dotted … clearly distinguishable". (The regen also baked in a sibling's uncommitted label edits to the same script — 'sample p99' and the population-p99 legend line — which is the current source of truth.)

19. P3 | Ch 6 §3 lead-in to the E[L] display (L45) | the two-point approximation was called "the mean of that stream" while the figure prints mean = 0.85 s | — | SKIPPED_PREMISE | current text: "The two-point approximation of the mean is E[L] ≈ 0.99 × 0.8 + 0.01 × 5.0 ≈ 0.84 s", and L54 already separates "the figure's exact simulated stream mean ≈ 0.85 s — the 0.84 is the two-point analytic approximation".

20. P1 | Ch 22 §3 Step 4 (L41) | "whole-model, fleet-level requirement" contradicts the same sentence's "a per-host constraint, not a fleet-wide one" | "fleet-level requirement" → "host-level requirement" | FIXED | grep "fleet-level requirement" in chapter-22.md → 0 hits; "host-level requirement" → 1 hit; sentence now reads per-host throughout.

21. P2 | Ch 22 §3 figure note (L71) | ~17% / ~2.4× / ~3.4× ratios printed with no counting convention, while the note above discusses both conventions | "Name the ratios explicitly (under full-square counting): …" and appended "Under causal-triangle counting the same three ratios are ~8.6%, ~1.2×, and ~2.2×." | FIXED | both phrases present verbatim; ratios recomputed from the book's own geometry (70B, 80 layers, d=8192): full-square 17.2% / 2.40× / 3.40×, causal 8.6% / 1.20× / 2.20×.

22. P2 | Ch 22 §4 Measurement item 2 (L79) | "input on memory/prefill" conflates KV capacity with the compute-bound prefill phase | → "input on prefill compute and KV-cache capacity, output on decode bandwidth" | FIXED | grep "memory/prefill" in chapter-22.md → 0 hits; one resource named per leg, matching the chapter's own "Prefill is compute-bound" statement.

23. P2 | Ch 22 §6 ADR Context bullet (L115) | "10 rps × 8 h × 260 workdays ÷ 12" is not dimensionally evaluable (yields 1,733, not 6.24M) | → "10 rps × 8 h × 3,600 s/h × 260 workdays ÷ 12" | FIXED | 10 × 8 × 3,600 × 260 ÷ 12 = 6,240,000 = the printed 6.24M (recomputed); the rest of the clause ("— not 24×7, Ch 4/Ch 16") unchanged.

24. P3 | Ch 22 §2 Mental Model, first sentence (L15) | metaphorical "figure" collides with the book's numbered-figure usage in a chapter that contains Fig 22.1 | "is the figure the rest of the book builds on" → "is the distinction the rest of the book builds on" | FIXED | grep "is the figure the rest of the book" → 0 hits; no other occurrence of metaphorical "figure" added.

## Counts

- FIXED: 15 (items 1,2,3,4,5,6,7,8,9,18,20,21,22,23,24)
- SKIPPED_PREMISE: 8 (items 11,12,13,14,15,16,17,19 — all eight already carry their fix in the current chapter-06.md, edited by the sibling round-5 fixer)
- NEEDS_REGEN: 0
- DUPLICATE: 1 (item 10)
- Total: 24

## Files changed

- design/manuscript/chapter-25/chapter-25.md (items 1,2,3,4,5,6,7,8,9)
- design/manuscript/chapter-22/chapter-22.md (items 20,21,22,23,24)
- design/manuscript/chapter-26/chapter-26.md (items 6 and 7 — the ch26 side each fix_instruction explicitly names)
- design/manuscript/chapter-06/figures/fig-06-0602.png + .pdf (item 18, regenerated; generator render/fig_ch6_hist.py not modified by this pack)
- review/loop_v3/round_5/disposition/fix/fix_pack_10_responses.md (this file)

chapter-06.md was NOT edited by this pack: every ch06 text item's premise was already gone in the current source.

## Gates

- render/check_md_leaks.py → "no markdown leak risks detected" (rc=0)
- render/check_tables.py → "all markdown tables: column counts consistent" (rc=0)
- render/check_stale_values.py → "OK - no stale superseded values found in live manuscript text" (rc=0)
- All new arithmetic re-verified in python (24.117 GB, 435.6 GB, 37.8%, 4.26→6.85 FLOP/byte, 6,240,000 req/mo, 17.2/8.6%, 2.40/1.20/2.20×)
- Figure: regen_one.py RC=0, PNG+PDF written, grayscale vision read-back confirms p90/p95 separable
- Whole PDF deliberately not rebuilt.