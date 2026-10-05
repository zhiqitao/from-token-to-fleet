# Full-Book Review — Three-Model Cross-Audit (2026-10-05)

Reviewers (all via opencode server free-model API, TAOCP-standard prompt):
- **Muse Spark 1.3 (free)** — full 313 rendered pages + full manuscript. Report: `full-book-audit-muse-spark-1.3-free-20261005.md` (45.5K chars, complete, 46/46 figures).
- **Fledge Alpha (free)** — 60-page subset (front matter + all 44 figure pages) + full manuscript. Report: `full-book-audit-fledge-alpha-free-20261005.md` (20.9K chars, complete, 46/46 figures).
- **Space Bunny (free)** — same 60-page subset. First run truncated at 4.5K chars (saved as `full-book-audit-space-bunny-free-20261005-TRUNCATED.md`); full re-run in progress.

Adjudication: where reviewers disagreed, the rendered page was inspected directly (Qwen3.8-27B native vision) and the source script checked.

## A. Confirmed issues (2+ reviewers, or verified against source)

### P0 — publication blockers
1. **Fig 19.3 title/legend overprint** (Muse MAJOR/REDESIGN + Fledge P0 + Bunny p.207 overprint). Title "Agentic context: the KV block grows every turn" overprints the legend row; bar labels indecipherable at the overlap.
2. **Fig 7.4 essential numbers illegible** (Muse MAJOR + Fledge P0/P1 + Bunny). White "≈436 GB KV budget" on light-green dotted fill fails print legibility and grayscale; the load-bearing capacity relation is the least-readable element.
3. **Fig 13.1 red trigger labels struck through by the red arrow** (Fledge P0/P1 + Bunny p.146 collision). "demand exceeds ceiling → forces scale-up" etc. printed across the wide vertical red arrow.
4. **Table 19-1 split across pp.210–211 mid-row** (Muse). Repaginate (landscape single page).
5. **Ch.24 candidate pair (4×/8×H100) incoherent with fleet sizing** (Muse P0-4). §24.4.3 derives a 16.3-host realistic floor / 20-host KV fleet, then tables candidates as 4 vs 8 hosts. Retable as 8 vs 20, or banner both as sub-fleet illustrative slices.
6. **Ch.18 claims 82% savings before checking the SLO it violates** (Muse P0-5). Route 80% of traffic to a ~600 ms Tier-1 against a 500 ms SLA, then admit the violation. Gate first, price second.

### P0/P1 — quantitative presentation (misleads by layout even though text retracts)
7. **2NL labeled "Prefill FLOPs" in Tables 2-1/8-1/22-1 without the attention-term qualifier** (Muse P0-2; Fledge confirms the +17%/+60%/2.4× corrections are correct but only stated in Ch.8/22). Rename rows "parameterized-linear floor (excl. attention term)".
8. **5.6 vs 3.35 TB/s adjacent columns = aggregate-vs-per-device visual assertion** (Muse P0-3 + Fledge: Ch.6 Table 6-1 decode row still shows unsharded framing). Split into "aggregate model-wide (illustrative)" vs "per-GPU shard under TP8" rows.
9. **FP8/8-bit KV nomenclature drift: 1.31 nominal vs 1.42 measured collapsed to "~1.3" in Ch.3 Table 3-1, Ch.5, Ch.12** (Muse P0-6; Fledge ledger flags the same). Global replace with "1.31 nominal / 1.42 measured" on first use per chapter.
10. **Single-host language leaks as capacity claims in Ch.4 §6, Ch.5 §3, Ch.11 §6, Ch.13 §3** (Muse P0-1). Freeze one canonical sentence; delete variants.
11. **Ch.9 vs Ch.10 ring all-reduce factor inconsistency** (FLEDGE-ONLY, verified against source). Ch.9 uses T_ring = 2(N-1)/N·M/B_eff (N=8 → 1.75×, 0.27 s / 6.1 s); Ch.10 §3 DP gradient sync uses plain T = bytes/B_eff (280/25 ≈ 11 s, 280/900 ≈ 0.31 s) — silently drops the 1.75 factor for the same operation. Align formulas and state the assumption.
12. **Fig 22.1 "flat across context" is unconditional in the graphic** (Fledge + Bunny p.233; adjudicated POLISH, not Muse's MAJOR — the y-axes are separate and the banner disclaims comparability, so the axis objection fails). The 2N line is context-independent, but total per-token decode grows linearly via the attention term ≈4·n_layers·L·d (comparable at 32K, dominant at 100K). Add the attention line/band to the right panel + reword annotation/caption.

### P1 — storyline / value
13. **Ch.22 is largely Ch.1+2 re-set** (Muse + Bunny: four Common Mistakes near-verbatim from Ch.1 §5; §8 mini-case near-verbatim from Ch.2 §8). Cut to ~6 pages: loop + Table 22-1 + redesigned Fig 22.1.
14. **Ch.17/Ch.20 are substantially one chapter wearing two** (Muse + Bunny: same 2.0 req/s, same 20-host, same Little's law). Keep Ch.20's unique scheduler-added vs end-to-end separation + infeasible-100ms-SLO rejection; delete the rest as pointer.
15. **Ch.18 lowest value-per-page** (Muse + Bunny): vendor-catalog + worked arithmetic that does not transfer. Compress to routing method + consolidation-vs-separation rule + one table.
16. **Ch.12 weak as standalone** (Muse): three worked candidates all fail; value is the method + Table 12-1. Shorten; move throughput arithmetic back to Ch.8 by reference.
17. **Ch.24 PIES/poisoning toy metrics** (Muse): explicitly non-portable null-model arithmetic the text itself disqualifies. Keep §24.4.3 (fixed) + guardrail consequences; delete or box the toy arithmetic.
18. **Ch.26 capstone 800 ms p99 TTFT never reconciled with canonical p95 ≤ 2 s** (Muse + Fledge ledger flag). Promote to a table banner or quarantine as a separate scenario.
19. **App.A Ornith post-snapshot sidebar violates the 2026-08-30 hard boundary it declares** (Muse). Delete or move outside the appendix with a distinct date banner.
20. **Four throughput rates never reconciled in one place** (Muse): 50 tok/s single-stream floor (Ch.5) vs 19,800 tok/s idealized prefill aggregate (Ch.8) vs 35–70k tok/s batched serving (Ch.15) vs 2.0 req/s KV/service-time bound (Ch.17/20). Add one reconciliation box in Ch.17 §4 or Ch.8 §4.
21. **Ch.4 vs Ch.16 per-request cost 10× seam** (BUNNY-ONLY, adjudicated P1 not P0): Ch.4's "$0.00056/request" is single-host on-demand marginal ($20/hr ÷ 10 rps); Ch.16's $5.7/1K is the 20-host full-TCO. Ch.4's basis note does not say $20/hr is per single host while the workload needs 5–20. Fix: state the host count explicitly in the Ch.4 note.
22. **Cloud TCO elasticity assumption understates the hard problem** (Muse P1-2): $72K/mo assumes fast scale-up + 140 GB load; if those dominate, cloud approaches always-on-at-peak $288K/mo and the headline flips. Carry two cloud columns (elastic-ideal vs always-on-at-peak).
23. **Reliability N-1 is asserted but never tabulated** (Muse + Fledge): no quantitative N-1 fleet row in Table 17-1.

### P1/P2 — figures (adjudicated)
24. **Fig 11.2 — MAJOR REVISION** (adjudicated; Muse said REDESIGN, Fledge said KEEP). The vertical spine (Request stream → central arrow → Output tokens) imposes a top-to-bottom order on the 2×2 grid, reading as two sequential phases — the opposite of "not a stack". Slide-deck styling (oversized pastel cards, ALL-CAPS labels, centered block ignoring text width). Fix: horizontal stream across the top, four compact cards below with short vertical connectors, book-figure styling, full text width.
25. **Fig 6.2 — POLISH** (adjudicated; Muse said MAJOR REVISION, Fledge said POLISH). The "p50/p90/p95 leader-line tangle" claim is FALSE — the callouts form a clean non-crossing fan and are legible. Real defects: (a) the red straggler annotation "~5 s (crosses the SLO)" is drawn over the x=5 histogram bar, partially obscuring "crosses"; (b) large page whitespace (figure occupies middle third). Fix: move the annotation off the bar; enlarge the figure.
26. **Fig 20.1 — POLISH (evidence label)** (Bunny-ONLY, adjudicated). The blue curve is labeled "MEASURED deployment throughput" but the figure is tagged [ILLUSTRATIVE][DERIVED] and the caption describes it as a derived construction (ceiling × ~95% efficiency, clipped at 40 rps) — not a benchmark. Relabel "MEASURED" → "PROJECTED (derived)" or similar. Minor: caption says "thin grey dashed" (drawn solid) and "grey dashed" (drawn dotted) — line-style words don't match the drawing.
27. **Fig 7.2 — MAJOR REVISION** (Muse; Fledge POLISH + verify 160 GB rule). Four log-log lines + two ceilings + two diagonal callouts crossing the lines they annotate; 6pt legend; paragraph title. Split legend outside axes, reroute callouts, shorten title.
28. **Fig 19.2 — MAJOR REVISION** (Muse P1; Fledge POLISH). Agentic KV growth → fleet argument; panel (a)/(b) title clipping, value-label collisions (fixed in earlier pass but re-flagged), 4-entry single-line legend cramped.
29. **Duplicate figure pairs — merge** (Muse + Fledge): 7.4 vs 7.5 (same 140+64+436), 19.2 vs 19.3 (same 24.9→34.0 GB), 2.1 vs 11.3 (same prefill→KV→decode topology). Keep one of each; for 7.4/7.5 keep 7.5 (better labels) and fold the concurrency equation in.
30. **Systemic: single-figure pages with 40–60% whitespace** (Fledge, 24 pages listed: pp.6,7,36,52,66,69,71,87–90,99,107,124,146,152,160,174,197,201,207,226,254,262,268,281,284). Enlarge figures or place section text beneath.
31. **Systemic: in-figure grey/olive italic qualifiers set smaller/lighter than body** (Fledge): "ANALYTICAL [DERIVED]" stamps, source footers, Fig 19.1/26.2 footnote lines carry epistemic weight but are not print-durable.
32. **Systemic: color-only semantics** (Fledge + Muse): Fig 11.1 (red idle vs green new), Fig 16.1 (red managed API), Fig 7.2 (four colors collapse in grayscale). Add line-style/marker redundancy.
33. **Systemic: inconsistent arrow semantics across figures** (Fledge): dependency (4.1), data flow (2.1/11.3), causation (6.1), conceptual association (A.4) all use similar single arrows. Add a one-line legend note in Ch.2.
34. **Table 18-1 duplicate "70B 8-bit GGUF" row** (Muse §8). Deduplicate; separate weight-residency from KV-inclusive fit.
35. **Table 4-1 "Dimension" hyphenated to "Di-men-sion"** (Muse §8, source-level column-width defect). Widen first column.
36. **Table 10-1 header stranded from its single continuation line across p.116/117** (Muse §8). Keep together.
37. **Fig 1.1/1.2 POLISH** (both reviewers): small, <50% page width, 6pt labels. Rebuild at full text width, 9pt minimum.
38. **Fig 8.1/8.2 POLISH** (Muse): white text on dark fills at 7–8pt; red double-arrow annotation collides with box edges (8.1); ridge labels need enlarging (8.2).
39. **Fig 10.1 POLISH** (Muse): red all-reduce annotations at 6.5pt; panel A arrows thin.
40. **Fig 15.2 / 16.1 / 18.1 / 20.1 / 21.1 / 24.1 / 26.1 POLISH** (Muse §7 P2 list) — per-figure actions in the Muse report.

## B. Rejected claims (verified false)
- **Bunny P0-A: "Ch.18 Table 18-2 has a 1000× unit error."** FALSE. 6.65M tokens × $1.25/1M = 6.65 × $1.25 = $8.31 ✓; 1.9M × $1.00 = $1.90 ✓; 0.95M × $2.50 = $2.38 ✓; total $12.59 vs single-FP16 9.5 × $2.50 = $23.75 ✓; monthly savings (23.75−12.59)×720 = $8,035 ✓. The "M" in "6.65M" is million and the price is per-million; the arithmetic is correct and self-consistent. Bunny's own "corrected" figure ($16.63) is 6.65 × $2.50 — it used the wrong price.
- **Muse: "Fig 6.2 percentile leader lines tangle into an unreadable smear."** FALSE (adjudicated on the rendered page). Clean non-crossing fan; labels legible.
- **Muse: "Fig 22.1 shared axis invites comparing incommensurable units."** FALSE (adjudicated). Y-axes are separate; the per-request/per-token distinction is flagged in four places including the banner. The real defect is the unqualified "flat across context" (item 12).
- **Muse: "Fig 11.2 has 10-word labels."** Minor inaccuracy (labels are 1–2 words, 7 total) — does not change the MAJOR REVISION verdict.

## C. Both reviewers' ledgers agree on
All canonical quantities are consistent book-wide (70B dense FP16, 140 GB, 9,200/300 tokens, 2.62 MB/token, 24.1/24.9 GB, 436 GB, C≈17.5, 1.29 PFLOP, 989 TFLOPS, 3.35 TB/s, ridge 295, 1.2 s/25 ms SLO, W≈8.6 s, 100/400 users, 86/344 in-flight, 10/40 rps, 2.0 req/s, 19,800 tok/s idealized, 5/20/29 hosts, $148K/$72K/$541K TCO, 800+65 agentic growth). No value drift beyond the flagged items (MoE table headers, 1.31/1.42 collapse, Ch.26 800 ms TTFT, Ch.18 basis note).

## D. Suggested execution order (by impact)
1. P0 visuals: Fig 19.3, 7.4, 13.1, 6.2 (annotation), Table 19-1 repagination.
2. Global relabels: 2NL floor, 5.6/3.35 split, 1.31/1.42, single-host sentence, Ch.9/10 ring factor, Ch.4 basis note.
3. Ch.24 retable (8 vs 20) + Ch.18 SLO-gating order + Ch.18 compression.
4. Fig 11.2 major revision; Fig 22.1 attention line; Fig 20.1 relabel; merge 7.4/7.5, 19.2/19.3, 2.1/11.3.
5. Redundancy compression (Ch.3 §3.7.1, Ch.9 B/C, Ch.12, Ch.13, Ch.20, Ch.22, Ch.24 toys) — target −25 to −35 pages.
6. Whitespace sweep (24 single-figure pages) + in-figure qualifier typography + color redundancy.
7. Table fixes (18-1 dedup, 4-1 column width, 10-1 keep-together, 17-1 N-1 row).
8. Pre-publication verification sweep (App.A links, prices, H100 specs, vLLM FP8) with visible re-verify date.
