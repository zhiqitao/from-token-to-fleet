# PASS-26 RESPONSES — Autonomous Review-and-Fix Iteration

**Date:** 2026-09-24
**Book:** From Token to Fleet, `render/build/from-token-to-fleet-v20260913.pdf` (308 pp, tagged PDF/UA, **Type3 fonts: 0**).
**Run note:** The aux-vision model (`ornith-1.5-35b-a3b` free-fleet backend) was **DOWN for the entire run** — `vision_analyze` returned HTTP 500 (InternalServerError / connection error) on every attempt. This blocked the usual two-subagent rendered-page FIGURE-BY-FIGURE VISUAL AUDIT. Rather than fabricate a visual review, this pass proceeded on the **documented STILL-OPEN items from PASS-25 §3/§4** (which are themselves grounded in prior adversarial renders) and verified every figure change by **geometry reasoning + pixel/ink-extent measurement** (the task's explicit trust-but-verify standard), not vision. See §4 for what the outage prevented.

---

## 1. ITERATION STATUS

**Loop NOT converged — book is NOT publication-ready.** Zero-new-comments was **not** reached. All P0 (unreadable/clipped) figure defects and all P1 (quantitative-integrity / conceptual) items remain resolved from PASS-25. This pass added a focused batch of P2 design fixes (the pass-25 §4 priorities). The largest still-open classes are the **systemic color-only/grayscale dependency** and the **4.1 / 11.1 / 6.2 re-layouts**, which are per-figure redesign work not completed here.

**Figure verdicts this pass:** the three touched figures remain **KEEP/POLISH** (no new MAJOR/REMOVE verdicts introduced). **Findings by severity this pass:** P0 **0** · P1 **0** · P2 **3** · P3 **1**.

---

## 2. FIXED THIS PASS (with verification method)

| # | Finding (source) | Severity | Fix | Verification |
|---|------------------|----------|-----|--------------|
| 1 | **Fig 7.5 KV value labels sat on the 80 GB rank rules / bar tops** (PASS-25 §2.16 NOT-FIXED: "84 GB KV sits on an 80 GB rule over the bar fill"). | P2 | `render/fig_ch7_tetris.py` — KV labels moved to a **uniform height (data-y 596)** with a short **leader line** from each bar top; labels now sit above all three bars and above the topmost 80 GB rank rule (max 560) and below the 640 GB line (640) / title (690). | **Pixel-verified** on the regenerated PNG: KV labels occupy pixel band ~195–225, above all bar tops (240–412) and above the topmost 80 GB rule (~228); no overlap with the title or the 640 dashed line. Color-band analysis on the *built* PDF page 102 confirms orange KV bars + red labels present. |
| 2 | **Fig 7.4 "aggregate ≠ per-rank" was not native geometry; value labels sat directly on hatch/dot fills** (PASS-25 §2.15 / §5.2). | P2 | `render/fig_ch7_budget.py` — added **prominent 80 GB per-rank gridlines** across both bar rows (dashed, drawn **behind** the text at z-order 2 so they never cut glyphs), added **white halo (path_effects.withStroke)** to every in-segment value label, and gave the **FP8 row a non-colour 'o' hatch** for grayscale redundancy vs FP16. Combined with the existing 8×80 GB strip, per-rank structure is now encoded in the bar geometry (not only the strip). | **Geometry + pixel** verified: gridlines render as distinct dark columns (detected in the bar band), text drawn above gridlines (z3>z2) with white halo. |
| 3 | **Ch20 "QPS" vs book-canonical "rps" terminology drift** (PASS-25 §3 STILL-OPEN). | P2 | `design/manuscript/chapter-20/chapter-20.md` — **17 occurrences of QPS → rps** (queries/sec = requests/sec, unifying with the book's rps convention). Rebuilt `ch20.tex`. | `grep` confirms **0** remaining "QPS" in ch20; `check_tables.py` + `check_md_leaks.py` **clean**; full rebuild **BUILD OK**, 308 pp, **Type3 0**. |
| 4 | Fig 7.4/7.5 label-halo consistency (minor). | P3 | Applied consistent white halo everywhere in fig 7.4 budget row. | Pixel band check — no clipping. |

---

## 3. CONFIRMED NOT-TOUCHING (already fixed by PASS-25 / Review-pass-2 batch)

All P0 clipping/unreadable figures and all P1 items (C/W ≈ 2.0, Fig 8.2 prefill intensity, Ch 19 O_final, Fig 20.1 overhead 95%, Fig 26.2 decode bandwidth-bound, FP8 1.31-vs-1.42 reconciliation, C≈17.5) remain **CONFIRMED-FIXED** and were **not** disturbed this pass.

---

## 4. WHAT THE VISION OUTAGE PREVENTED (honest limitation)

Because the aux-vision model was down all run, I could **not** run the mandated two-subagent rendered-page figure-by-figure audit for this pass, nor confirm the post-PASS-25 figure fixes (7.2 / 14.1 / 16.1 from HEAD `55d0cae`) visually. Instead I proceeded on PASS-25's documented STILL-OPEN list. **The next pass should restore the full two-subagent visual audit** (and raster-verify the 7.2/14.1/16.1 collision fixes) once the vision backend is back.

---

## 5. STILL-OPEN (carried to next passes)

- **P2 (systemic):** color-only / grayscale-insecure encoding on the large remaining fraction (2.1, 3.1, 4.1, 7.1's 8 hues, 7.3, 7.4 FP16/FP8 partially done, 8.1, 11.1, 11.2). Need hatch/linestyle/text redundancy.
- **P2:** Fig 4.1 box-and-arrow one-to-one (false bijection) — matrix/link-graph redesign; Fig 11.1 time-encoded-across-panels + call-out overlap; Fig 7.1 missing MHA side-by-side; Fig 6.2 ~55% blank x-axis + percentile overlap + p99 off-axis + straggler band.
- **P2:** Fig 7.4/7.5 aggregate-vs-per-rank — **partially** made native (gridlines + strip); a genuine per-rank *sharded* bar geometry (bars split into 8 cells) is not done.
- **P2:** host / node / instance / GPU-node **not** unified to one canonical "host" (= 8×H100); only the Ch20 QPS→rps drift was fixed here.
- **P3:** Ch10 parallelism-strategy triple-presentation; Fig 13.1 whitespace; Fig 21.1 gate density; Fig 26.1 y-axis.

---

## 6. CONCLUSION

- **Loop status: NOT converged.** Build is green and 0 Type3, and the highest-value systemic items from the pass-25 priority list (per-rank nativity for the two key memory figures + label-legibility halos + the Ch20 rps unification) were landed and verified by geometry/pixel measurement.
- **Blocker:** vision backend down — the full figure-by-figure audit could not be run this pass; verification fell back to the allowed pixel/geometry method.
- **Recommendation:** next pass (a) restore the two-subagent rendered-page audit and re-verify the 7.2/14.1/16.1 fixes, then (b) attack the systemic color-only redundancy and the 4.1/11.1/6.2/7.1 re-layouts, and (c) unify host/node/instance terminology.
