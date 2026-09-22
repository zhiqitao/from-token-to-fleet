# PASS-24 RESPONSES — Autonomous Review-and-Fix Iteration

**Date:** 2026-09-21 / 2026-09-22 (build timestamp)
**Book:** From Token to Fleet, `render/build/from-token-to-fleet-v20260913.pdf` (309 pp)
**Reviewers:** two parallel subagents (pages 1–155 = Ch 1–12 + Ch 12 boundary; pages 156–309 = Ch 12 tail → Ch 26 + Appendix A + back-matter), applying the full 936-line `complete_manuscript_review_prompt.txt` standard including the MANDATORY rendered-page figure-by-figure audit.
**Authoritative findings files (do not edit):**
- `review/loop/pass24_findings_01-14.md` (48 KB, 25 figures)
- `review/loop/pass24_findings_15-27.md` (34 KB, 23 figures)

---

## 0. ITERATION STATUS

**The loop is NOT converged — the book is NOT publication-ready.**

Build for this pass: **BUILD OK**, 309 pages, tagged PDF/UA (StructTreeRoot present), **Type3 fonts: 0** (the interrupted PASS-23b/pass-24 working tree had a Type3 regression in fig-23-2301.pdf, fixed by rerunning the canonical `regen_figs.py` with `pdf.fonttype=42`). `check_tables.py` and `check_md_leaks.py` both pass clean.

The review found **~48 numbered figures and a systemic figure-floor problem**: across both halves only ~7 figures pass as KEEP; the large majority call for MAJOR REVISION or REDESIGN, with **7 P0 rendered-figure defects** (visible clipping / overlap / unreadable essential labels) and multiple P1 technical/terminology/conceptual inconsistencies. This is a substantial redesign program spanning the whole book — it cannot be cleared in a single pass, and doing so hastily would violate the review prompt's own "do not rush" standard. Two structural/terminology issues are genuinely derivable-in-code or manuscript and were fixed here; the figure re-layouts are documented below with concrete direction and are the top priority for the next passes.

**Counts (consolidated from both findings files):**
- Figure verdicts: KEEP 7 · POLISH 9 · MAJOR REVISION 27 · REDESIGN 2 · REMOVE/MERGE 0 (of ~45 distinct numbered figures; front-matter figs 1–2 included).
- Figure-issue severity: **P0 × 7**, P1 × ~15 (figure + conceptual + terminology), P2 × ~12, P3 × few.
- Technical/canonical arithmetic: **independently recomputed and internally consistent** (prefill/decode FLOPs, KV/token 2.62 MB, per-request KV 24.9 GB, C≈18, Little's Law in-flight ≈344, fleet-sizing matrix, TCO chain, agentic growth) — with a small set of minor rounding/label discrepancies listed below.

---

## 1. WHAT WAS FIXED THIS PASS (CONFIRMED-FIXED)

| # | Finding | Severity | Resolution | Status |
|---|---------|----------|------------|--------|
| 1 | **Type3 font regression** in fig-23-2301.pdf (from the interrupted working tree, which regenerated Fig 23.1's PDF by running `fig_batch2.py` directly at `pdf.fonttype=3`). 4 DejaVu Type3 fonts on p255. | Build | Reran `python3 render/regen_figs.py` (writes every figure's vector PDF with `pdf.fonttype=42`), then rebuilt. Verify reports **Type3 fonts: 0**. | **FIXED** |
| 2 | **Fig 23.1 green output box text clipped on both sides** ("Quantified bounds → {TTFT, throughput, cost} budget" cut; leading "Q" and trailing "…t" of "budget" clipped). | **P0** | Widened the green box from 7.0→9.0 data-units (x 0.5–9.5) and increased its height (0.9→1.15) in `render/fig_batch2.py`. Raster-verified at 220 dpi: string now fully contained with comfortable padding, no clipping in the green box or any of the 5 orange boxes. | **FIXED (raster-verified)** |
| 3 | **Ch 26 Pattern A typo** — "8-way **tensor parity**" should be "tensor **parallelism**". | P3 | Corrected in `design/manuscript/chapter-26/chapter-26.md`. | **FIXED** |
| 4 | **QPS vs rps drift** — the book's canonical arrival-rate unit is `rps`; Ch 26 used `QPS`. | P2 | Replaced all QPS→rps in `chapter-26/chapter-26.md` (definition line + Scenario + Step 1 + Step 2 ×2) and in the Fig 26.2 generator `render/fig_ch26_feedback.py` ("request rate ~2 rps", "load 2.0 → 1.3 rps"). | **FIXED** |

Notes on Fig 26.2 numerics: the source generator `fig_ch26_feedback.py` already reads "TTFT p99: 210 ms", "p99 = 285 ms · cost − 55%", "composed ⇒ 680 ms p99 · 40% lower generation cost" — i.e. the **source already matches the Ch 26 §8 manuscript** (Step 2 210 ms, Step 3 285 ms / −55%). The reviewer's reported "310 ms / 600→393 ms" does not appear in the source and is believed to be a misread of truncated/clipped box text in the rendered figure (a real P0 layout defect, see open item F-26.2). The manuscript↔figure numeric mismatch as described by the reviewer was **not reproducible in the source**; the figure-side layout truncation remains the actionable P0.

---

## 2. FINDINGS BY FIGURE — VERDICT AND STATUS

Legend: **P0** publication gate (overlap/clip/unreadable/misleading). **P1** damages a foundational mental model. **P2** comprehension/professionalism. **P3** polish. **KEEP** — no change needed. Status: OPEN (needs the noted action), POLISH (minor), KEEP.

### Pages 1–155 (Ch 1–12 + front matter) — from `pass24_findings_01-14.md`

| Figure | Verdict | Severity | Status / Required action |
|--------|---------|----------|--------------------------|
| Fig 1 (front-matter "architect's decision loop") | MAJOR REVISION | P1 | OPEN — no arrowhead on loop-back; pill labels clip card borders; add explicit iterate→re-characterize return arrow; legend the dashed/solid distinction; enlarge tags. |
| Fig 2 (front-matter "reading the book by number") | MAJOR REVISION | P1 | OPEN — missing/ambiguous topic→decision arrows; restore arrows; align rows to a common grid; bump chip text. |
| **Fig 1.1** | KEEP | — | no change. |
| **Fig 1.2** | KEEP | — | no change (page 6 whitespace could be reflowed, P3). |
| **Fig 2.1** (canonical inference pipeline) | MAJOR REVISION | **P0** | OPEN — step labels on/over box borders; long connector crosses annotations; serial-chain implication for parallel prefill; color-only (grey/blue/orange) with no hatch. |
| **Fig 2.2** (arithmetic-intensity continuum) | MAJOR REVISION | P1 | OPEN — no numeric axis; ridge shown as exact ~295; prefill marker not at true ≈9.2K FLOP/byte; hard boundary vs the qualified prose. |
| **Fig 3.1** (dense vs MoE) | MAJOR REVISION | P1 | OPEN — active/inactive expert distinction is color-only; equal-size boxes imply equivalence; metrics in the inter-panel gutter. |
| **Fig 4.1** (six-dimension → decisions) | MAJOR REVISION | P1 | OPEN — one-to-one arrows imply a false bijection; box-arrow-prose; color-only. Redesign as matrix/link graph. |
| **Fig 5.1** (model selection ladder) | MAJOR REVISION | P1 | OPEN — arrows cross/graze labels; ambiguous "split" labels; tiny light-grey edge labels; slide-like margins. |
| **Fig 6.1** (metric hierarchy chain) | POLISH | P2 | OPEN — no arrowheads; directionality color-only (green/red); ladder implies rank. |
| **Fig 6.2** (latency distribution) | POLISH | P2 | OPEN — percentile labels overlap; x-axis ~70% empty; straggler band un-legendded; not marked ILLUSTRATIVE. |
| **Fig 7.1** (GQA cuts per-token KV) | MAJOR REVISION | **P0** | OPEN — top rectangle of all stacks clipped; only GQA drawn (no MHA side-by-side so the 8× is asserted not shown); color-only. |
| **Fig 7.2** (KV vs context) | POLISH | P2 | OPEN — tiny legend/ticks; call-outs overlap curves; straight log-log line implies precision. |
| **Fig 7.3** (inference vs fine-tuning floor) | POLISH | P2 | OPEN — annotation overlaps title/legend; value label against top spine; color-only threshold lines. |
| **Fig 7.4** (concurrency budget 640 GB) | MAJOR REVISION | P1 | OPEN — warning/call-out collision; no per-rank 80 GB delineation (aggregate-as-fungible-pool); color-only FP16/FP8. |
| **Fig 7.5** (Memory Tetris) | MAJOR REVISION | P1 | OPEN — red KV labels overlap; 32K bar shows a split-separator artifact; no per-rank ceiling so "539<640" falsely implies fit. |
| **Fig 8.1** (memory/compute hierarchy) | POLISH | P2 | OPEN — tiny secondary labels; ladder implies "higher=better"; color-only grouping; add "not to scale". |
| **Fig 8.2** (per-GPU roofline) | MAJOR REVISION | P1 | OPEN — prefill 9.2K drawn at ~300–400 FLOP/byte instead of true ≈9.2K (~31× ridge); annotation overlaps; legend inside axes. |
| **Fig 9.1** (all-reduce time vs volume) | POLISH | P2 | OPEN — y-axis log ticks skip 10⁴; 140 GB reference drawn outside plotted data range; cramped legend. |
| **Fig 10.1** (composing parallel dimensions) | MAJOR REVISION | P1 | OPEN — tiny monospace; CP absent; EP-arrow only to one GPU; ambiguous reading order. |
| **Fig 10.2** (five parallelization strategies) | **REDESIGN** | **P0** | OPEN — **clipped labels** ("PP·pipelin", "CP·contex", "W weights (row", "WHAT SPLIT" etc.), ~6–8 pt type, color-only. Redesign matrix at usable type / abbreviate with in-figure key. **Highest-priority figure in this slice.** |
| **Fig 11.1** (discrete vs continuous batching) | MAJOR REVISION | P1 | OPEN — time encoded orthogonally across panels; annotation overlaps; no common baseline (PASS-10 fail). |
| **Fig 11.2** (serving stack: four concerns) | MAJOR REVISION | P1 | OPEN — central top-to-bottom arrow contradicts "not a stack"; color-only; box-arrow-prose. |
| **Fig 11.3** (P/D disaggregation) | MAJOR REVISION | **P0** | OPEN — KV-transfer/ownership labels overlap GPU boxes; output arrow direction contradicts text; "starved" vs "bound" + per-GPU/aggregate ambiguity. |
| **Fig 12.1** (candidate architecture synthesis) | MAJOR REVISION | P1 | OPEN — OUTCOME label straddles SURVIVORS/REJECTED boundary; candidate lines run together; ~19.8K vs ~92K mixes per-host/system denominators; 164 vs 165 GB. |

### Pages 156–309 (Ch 12 tail → Ch 26 + Appendix A) — from `pass24_findings_15-27.md`

| Figure | Verdict | Severity | Status / Required action |
|--------|---------|----------|--------------------------|
| Fig 12.1 (boundary) | MAJOR REVISION | P1 | see pages 1–155 row above (same figure). |
| **Fig 13.1** | MAJOR REVISION | P1 | OPEN — trigger labels on opaque boxes straddle the connector/rung borders; ladder implies universal superiority. Move labels beside rung gaps; differentiate escalation direction. |
| **Fig 14.1** | KEEP | — | no change. |
| **Fig 15.1** | KEEP | — | no change. |
| **Fig 15.2** (prefix caching vs batching) | POLISH | P2 | OPEN — legend box occludes part of the series; cramped subplot titles. |
| **Fig 16.1** (TCO break-even) | MAJOR REVISION | P1 | OPEN — x-axis tick labels clipped/missing (request-volume scale unreadable); add legible x-axis + label; consider overlaying the 70%-utilization fleet line. |
| **Fig 17.1** (fleet of one model) | MAJOR REVISION | P1 | OPEN — doesn't show the three sizing factors (capacity, SLO headroom, failure tolerance) its own caption claims; container label overlaps border. REDESIGN to show N = max(capacity, SLO, failure) with a drained replica. |
| **Fig 18.1** (model-routing decision tree) | POLISH | P2 | OPEN — packed top row; "fallthrough" label near arrow; tiny caption. |
| **Fig 19.1** (agent loop 4-state machine) | MAJOR REVISION | **P0** | OPEN — grey secondary lines bleed across box boundaries and clip; bold titles sit over line tails; "turn limit / rej" partially hidden; loop/resolved wiring crowded. Needs re-spaced layout with real padding/gutters. |
| **Fig 19.2** (token/KV growth) | MAJOR REVISION | P1 | OPEN — red KV labels overlap bar tops; subtitle runs into panel titles; low-contrast "added per turn" segment; Turn-1 27.1 vs text 27.2. |
| **Fig 19.3** (agentic context block) | MAJOR REVISION | P1 | OPEN — γ layer essentially a line at Turn 1; small in-bar symbols; crowded KV labels; 27.1 vs 27.2. |
| **Fig 20.1** (fleet capacity + utilization) | MAJOR REVISION | P1 | OPEN — orange utilization curve clipped at top; 0.9× overhead factor vs Ch17 ρ=0.95/0.98; "[40/(2.1×0.70)] = 28" should be 27.2→27; busy annotations. |
| **Fig 21.1** (AI Factory promotion pipeline) | MAJOR REVISION | P1 | OPEN — gate boxes cramped with tiny stacked type; FAIL box overlaps dashed lines; feedback label tight. |
| **Fig 22.1** (prefill quadratic vs decode) | MAJOR REVISION | P1 | OPEN — red banner overlaps top of left axes; purple quadratic clipped at bottom; tiny grey note. |
| **Fig 23.1** (vague ask → worked example) | MAJOR REVISION | **P0 (clipping)** | **Green-box clipping FIXED** (see §1#2). **Open conceptual:** figure shows **5 gates** vs Table 23-1's **six questions** and §23.7 prose "six Socratic questions (…)" naming five; per-gate secondary type at print-size legibility limit; gate-2 "p95 TTFT < 300 ms" vs gate-1 "p99 1.4 s" and the book's canonical p95 ≤ 2 s. |
| **Fig 24.1** (Red/Green team cycle) | POLISH | P2 | OPEN — faint vertical white seam artifact in several nodes; probe-domain label tight. |
| **Fig 25.1** (anatomy of an ADR) | POLISH | P2 | OPEN — red annotation sits on the red dashed feedback loop (red-on-red). |
| **Fig 26.1** (workload fingerprints) | POLISH | P2 | OPEN — grey note immediately under rotated multi-word x-tick labels; small note/caption. (Grouped-bar redesign from radar = pass-23b requirement, satisfied.) |
| **Fig 26.2** (Pattern-Measurement-Feedback loop) | REDESIGN | **P0/P1** | OPEN — **multi-label truncation in the loop boxes** (headings cut: "3 HYPOTHESIS · valid…", "4 PATTERN · adjust /…"; box-1 "latency 50 ms" cut; "B · Semantic Cache" straddles A/B boundary). Source numerics already match manuscript (210/285/680) and QPS→rps fixed here; the unqualified "decode is bandwidth-bound" in-figure rule must be qualified; "680 ms p99 · 40% lower generation cost" should be labeled [DERIVED]/[ILLUSTRATIVE]. |
| **Fig A.1** | KEEP | — | no change. |
| **Fig A.2** | POLISH | P2 | OPEN — three panels share one y-axis label but have independent baselines/max (30/30/40); label each "own y-axis". |
| **Fig A.3** | KEEP | — | no change. |
| **Fig A.4** | KEEP | — | no change. |

---

## 3. NON-FIGURE FINDINGS — VERDICT AND STATUS

### Technical / numerical (most recomputed and confirmed consistent)
- **FP16/KV arithmetic** (140 GB, 2.62 MB/token, 24.1/24.9/84/335 GB, 436 GB budget, C≈18, prefill 1.29 PFLOP→1.19 PFLOPS, decode 5.6 TB/s, ridges 295/206, in-flight 344, $14.6K/mo, fleet matrix, TCO chain, agentic I(T)) — **CONFIRMED CORRECT** (independently recomputed by both reviewers). No action.
- **[P2] FP8 per-token KV inconsistency** — "~1.31 MB/token" (byte-halving bound, Fig 7.2/Ch1) vs "~1.42 MB/token (54% of BF16)" (realistic FP8 with scale metadata, Fig 7.4/Ch12). Also FP8 concurrency 436/12.4=~35 vs stated ~33. OPEN — reconcile and state which per-token value the ~33-slot figure assumes.
- **[P2] 164 vs 165 GB** — Fig 12.1/Table 12-1 use 164 (140+24, 9.2K) vs Ch13 165 (140+24.9, 9.5K). OPEN — canonical context is stated both as 9.2K (1200 prompt + 8K retrieved) and 9.5K elsewhere; reconcile the canonical prompt length or label the two different contexts.
- **[P2] 27.1 vs 27.2 GB** (Fig 19.2/19.3 use 27.1; Ch17/19 text and recomputation give 27.2 at 10,365 tokens × 2.62 MB = 27.16). OPEN — set figure labels to 27.2.
- **[P3] Ch3 §3.4.3 KV formula** stated as `2×nlayers×dhidden×bytes` is the full-MHA special case; should be qualified "full-MHA (n_KV×dhead=dhidden)" since Ch7 generalizes. OPEN.
- **[P2] Fig 20.1** overhead factor 0.90 vs Ch17 ρ=0.95/0.98; annotation rounding 27.2→28. OPEN — align to Ch17 and correct the quotient.

### Terminology / conceptual (OPEN unless noted)
- **[P1] Six questions vs five gates** (Table 23-1 "six questions" vs Fig 23.1 five funnel gates vs §23.7 prose "six Socratic questions (…)" naming five). OPEN — reconcile consistently.
- **[P1] Table 24-1 "Tool-use success rate" target direction** — a *success* rate shown with `target < 0.5`, a declining series, and Ch24.2 "if the tool-use success rate is above 0.5% … restrict" all treat it as a bad signal. OPEN — clarify the definition/direction (it appears to measure a spurious-rate, not success).
- **[P2] host/node/instance/GPU-node** used interchangeably for the 8×H100 box (Ch 3, 13, 26). OPEN — pick one canonical term ("host" = 8×H100) with an explicit glossary note at first use.
- **[P2] request vs query** muddled in Ch 18/24/26. OPEN — minor, worth a global pass.
- **[P2] QPS→rps** — **FIXED** (Ch 26, all occurrences). Other chapters were already rps-consistent.
- **[P3] "tensor parity"→"tensor parallelism"** — **FIXED**.

### Evidence / storyline / value
- Evidence taxonomy ([1P]/[DERIVED]/[ILLUSTRATIVE]/[canonical]/[2°]) is rigorous; no removal-worthy sections flagged. Fig 17.1 is the main "doesn't earn its space" case; the Ch 12/23 funnel/table partly duplicate. OPEN (design-level).
- **[P2] Fig 6.2** latency histogram not marked ILLUSTRATIVE (presents empirical authority). OPEN.
- **[P2] Fig 9.1** 140 GB annotation outside plotted data range implies extrapolation precision. OPEN.

### Tables / page composition
- **Table 4-3** — Monthly budget is ~10 prose lines in a cell; multi-line values lack hanging indent; "users ~2,000" absent from the table; FP16/KV-price rows break mid-parenthetical. OPEN (P2).
- **Table 17-1** (fleet-sizing matrix) and **Table 16-1** (TCO) — KEEP, excellent.
- **Table 24-1** — success-rate target-direction problem (see above, P1).
- **"Optimization Decision Map"** (Ch15 §4a multi-page table) — at density limit; consider re-flowing/splitting. OPEN (P2).
- Page breaks/headings across the whole book — clean; no widows/orphans/stranded headings observed.

---

## 4. SYSTEMIC (CROSS-FIGURE) ISSUES — OPEN

These are the highest-leverage structural fixes and should drive the next passes:

1. **Color-only encoding** (grayscale/no-hue failure) affects a large fraction of figures (3.1, 4.1, 5.1, 6.1, 7.1, 7.3, 8.1, 10.1, 10.2, 11.1, 11.2, 11.3, 12.1, 2.1). Add hatch/pattern/linetype/text redundancy.
2. **Box-and-arrow prose** (4.1, 5.1, 10.1, 10.2, 11.2, 12.1, 17.1, 23.1) — geometry doesn't encode the relationship; several could be replaced by a matrix/link-graph/single mechanism.
3. **Text not contained in its container** (10.2, 19.1, 26.2, 21.1, 12.1, 2.1) — the auto-generated vector figures size text to fixed boxes without reflow; a systemic layout-capacity problem.
4. **Aggregate-as-fungible-pool** in 7.4/7.5 — the per-rank 80 GB limit must be drawn in-figure (this is the book's best idea and its figures currently fight it).
5. **Qualification must survive the graphic** — compute-bound/bandwidth-bound hardens into an unconditional in-figure rule (2.1, 2.2, 11.3, 26.2); PASS-7.
6. **Adopt a shared figure visual grammar** (arrow semantics, persistent-KV state, hardware boundaries) so the same shapes aren't used for different relationships (PASS 4 / PASS 6).

---

## 5. CONCLUSION

- **Loop status: NOT converged.** Zero-new-comments was NOT reached. The book remains **NOT publication-ready** under the review gate ("a manuscript with even one obvious rendered-figure defect is not publication-ready" — this pass documented many).
- **Fixed this pass (4 items):** Type3 font regression → 0 Type3; Fig 23.1 green-box P0 clipping (raster-verified); "tensor parity"→"tensor parallelism"; QPS→rps in Ch 26 (manuscript + Fig 26.2 generator).
- **Confirmed correct (no action):** the entire canonical numerical machinery recomputes consistently across both halves.
- **Remaining (OPEN), highest priority:** the six other P0 figure defects (Fig 10.2, 7.1, 11.3, 2.1, 19.1, 26.2) plus P1 figure re-layouts (12.1, 16.1, 17.1, 19.2/19.3, 20.1, 21.1, 22.1, 23.1, 13.1), the grayscale/color-only and aggregate-vs-per-rank systemic fixes, and the P1 conceptual/terminology items (six-vs-five gates, Table 24-1 success-rate direction), plus the minor numerics (FP8 KV, 164/165, 27.1/27.2, Fig 20.1 overhead factor).

Next passes should take these one figure-system at a time (rendered-page raster verification for every edit) rather than attempting the whole set at once, in line with the review prompt's "no rush, many iterations" standard.

---

## PASS-24 SECOND TRANCHES (manual, committed 56c4d7a..19e8a64)

Figures fixed and verified at true book scale this drive (beyond the cron's own 9615a5c):
- Fig 16.1 x-axis clipped off page (CRITICAL regression) -> landscape rewrite (56c4d7a).
- Fig 19.1 agent-loop state-box overlap (CRITICAL) -> matplotlib rewrite.
- Fig 7.1 clipped group-head labels (P0) -> group brackets added.
- Fig 12.1 caption truncation + duplicate ⑤ numbering -> compact + X-REJECTED.
- Fig 7.5 aggregate-vs-per-rank warning (adds in-figure caveat).
- Fig 10.2 label clipping -> print-size flag + regen exemption (a377707).
- Fig 26.2 capstone truncation -> print-size flag + direct regen (8f4aee1).
- Fig 2.1 labels-behind-boxes + connector crossing -> print-size + fonts (dd15f51).
- Fig 11.3 output-arrow direction + KV-label clearance + qualified footer (3a09a77).
- Fig 6.1 direction-on-connectors (no longer legend-only) (425fd45).
- Fig 3.1 aligned dual-panel + consistent resident/active channel + 8 experts.
- Fig 10.1 concrete composition (not abstract bands) + CP + top-down.
- Fig 2.2 ridge clear of labels + grayscale (hatch/marker/text redundancy).
- Fig 13.1 horizontal escalation path (no top=best) + triggers clear (in flight).

SYSTEMIC ROOT CAUSE: regen_figs.py re-boosts + reflows every figure, which distorted
print-size-authored figures (clipped labels, undersized renders). Added a
`_hermes_print_sized` figure flag + matching exemption in regen_figs._scale_figure_fonts,
and marked the verified figures so the cron loop cannot re-distort them.

Ch23 six-vs-five gate framing and Ch24 'tool-use success rate' -> 'tool-use exploit rate'
(9ea50e5) resolve the two P1 conceptual/terminology items.
