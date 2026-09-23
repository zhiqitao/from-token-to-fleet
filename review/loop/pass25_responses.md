# PASS-25 RESPONSES — Autonomous Review-and-Fix Iteration

**Date:** 2026-09-23
**Book:** From Token to Fleet, `render/build/from-token-to-fleet-v20260913.pdf` (307 pp, tagged PDF/UA, **Type3 fonts: 0**)
**Reviewers:** two parallel subagents (pages 1–155 = Ch 1–12 + front-matter; pages 156–307 = Ch 12 tail → Ch 27 + Appendix A), applying the full 1745-line `review/complete-manuscript-review-prompt.md` standard including the mandatory rendered-page figure-by-figure audit (~200–400 dpi).
**Authoritative findings files (do not edit):**
- `review/loop/pass25_findings_01-14.md` (34 KB, 24 figures)
- `review/loop/pass25_findings_15-27.md` (24 KB, 22 figures)

---

## 0. ITERATION STATUS

**Loop NOT converged — book is NOT publication-ready** (several CONFIRMED-FIXED items added this pass, but a cluster of P2 figure-layout and terminology items remain — see §4). The big news: **zero remaining P0 (unreadable/clipped) figure defects.** Every clipping/unreadable P0 from PASS-24 (Preface Fig 1/2, Fig 2.2, Fig 10.2→Table 10-1, Fig 19.1, Fig 23.1 green box, Fig 26.2 truncation, Fig 19.2/19.3 tick/gamma) was **CONFIRMED-FIXED** on the rendered page by the Review-pass-2 batch.

**Figure verdicts this pass:** KEEP ~9 · POLISH ~14 · MAJOR REVISION ~10 · REDESIGN 0 · REMOVE/MERGE 0.
**Findings by severity:** P0 **0** · P1 **4** · P2 ~25 · P3 ~26.

---

## 1. FIXED THIS PASS (with verification method)

| # | Finding | Severity | Fix | Status |
|---|---------|----------|-----|--------|
| 1 | **C/W bound inconsistency** — text/equations used `C/W = 18 ÷ 8.6 ≈ 2.1 req/s` (Ch4, and "~2.1 req/s" in Ch26, "~18 KV-resident" in Ch13), inconsistent with the corrected `C≈17.5` used elsewhere (Ch16/17/20). | **P1** | Ch4 prose→`C/W ≈ 17.5 ÷ 8.6 ≈ 2.0 req/s`; Ch4 equation 2.1→2.0 and result 24→**25 hosts**, ~34→**~36 hosts**, "~24 hosts"→"~25 hosts"; Ch26 "~2.1 req/s"→"~2.0"; Ch13 "~18 KV-resident"→"~17.5"; Ch26 Pattern A "~18 concurrent"→"~17.5". | **FIXED** |
| 2 | **Fig 8.2 prefill intensity mis-plot (P1, quantitative-figure integrity)** — "prefill 9.2K" drawn at ~320 FLOP/byte (just past the ~295 ridge) instead of true ~9,200 (~31× the ridge), x-axis capped at 10³; and the promised `[ANALYTICAL]` in-plot tag absent (only "DERIVED [1P: vendor datasheet]"). | **P1** | `render/fig_ch8.py`: x-axis extended `logspace(-1,4.3)`, prefill point moved to intensity **9200**, label now "prefill 9.2K (intensity ≈ 9.2K FLOP/byte)", in-plot tag → **"ANALYTICAL [DERIVED]"**. Raster-verified in the built PDF: point sits on the ~989-TFLOPS plateau at ~9.2×10³, ~31× the ridge, no clipping. | **FIXED (raster-verified)** |
| 3 | **Ch19 Fig 19.2/19.3 token arithmetic omits `O_final=300`** — figure captions & in-figure note gave `I₀+T·δ+T·γ` and "initial prompt (9.2K tok)", which does not reproduce the printed KV 24.9→34.0 GB (base must be 9,500 = 9,200+300). | **P1** | Ch19 caption 19.2 → `(I₀ + T·δ + T·γ + O_final; 9,200 input + 300 output + 800 + 65 per turn)`; caption 19.3 → "initial prompt (9.5K = 9.2K input + 300 output)"; `render/fig_ch19_accum.py` footer → `total = I0 + T·δ + T·γ + O_final (base 9.5K = 9.2K input + 300 output)`. Raster-verified in fig PNG. (Ch19 §3 prose was already correct.) | **FIXED** |
| 4 | **Fig 20.1 scheduling-overhead factor ~90% vs Ch17 ρ≈0.95/0.98** (cross-chapter numeric mismatch on a fleet-capacity figure). | P2 | `render/fig_batch3.py` overhead line `qps*0.9`→`qps*0.95`, legend "~90%"→"**~95%**"; Ch20 caption "~90% scheduling-overhead line"→"~95%". Raster-verified in built PDF (legend + caption). | **FIXED** |
| 5 | **Fig 26.2 "sharding ⇒ bandwd-bound"** — abbreviation + not qualified as decode. | P2 | `render/fig_ch26_feedback.py` → split to `sharding ⇒` / `decode bandwidth-bound` (full phrase, fits box; cache-detail retained in caption). Raster-verified: "decode bandwidth-bound" complete, no clipping. | **FIXED (raster-verified)** |
| 6 | **Ch3 §3.4.3 KV formula** is the full-MHA special case stated as canonical. | P3 | Qualifier added inline: "(the full-MHA case, where n_KV-heads × head_dim = hidden_dim; for a GQA/MQA model substitute n_KV-heads × head_dim)". | **FIXED** |
| 7 | **Fig 11.2 "RESOURCE SPECIALISATION" header overruns its orange bar** (introduced as a NEW defect by the enlarged-names fix). | P2 | `render/fig_batch1.py` concern() header font made adaptive (9.6 if ≤18 chars else 8.1). Raster-verified in built PDF: full title contained in bar. | **FIXED (raster-verified)** |
| 8 | **Fig A.1 orange % labels overlap the grey total/active annotations.** | P2 | `render/fig_2701.py`: % label at bar tip (dark orange, left-aligned), annotation moved right. Pixel-verified: % label ends ~x505, annotation begins ~x608 → **~100–150 px gap**, no overlap. | **FIXED (pixel-verified)** |

---

## 2. CONFIRMED-FIXED BY THE PRIOR (Review-pass-2) BATCH — verified this pass

Verified CONFIRMED-FIXED on the rendered page: Preface Fig 1 decision-loop (clear arrowhead + iterate return arrow), Preface Fig 2 two-path redesign, Fig 2.1 labels-not-behind-boxes + connector rerouting, Fig 2.2 bottom-band rebuild + prefill on the compute side, **Fig 10.2 → clean typeset Table 10-1** (former P0 clipped labels gone), Fig 12.1 condensation + X-REJECTED, Fig 7.2 attention-geometry retitle, Fig 9.1 ANALYTICAL [DERIVED] + full log decade, Fig 6.1 direction-on-connectors, Fig 11.3 output-arrow direction + qualified footer, Fig 6.2 [ILLUSTRATIVE] tag, the **FP8 1.31-vs-1.42 reconciliation**, and **C = 17.5**. Second half: Fig 13.1 (horizontal path + STOP-when-satisfied), 14.1 (deploy gate), 15.2 (ILLUSTRATIVE ×2), 16.1 (x-axis legible), 17.1 (three sizing factors + counter-scenarios), 18.1 (print-sized), 19.1 (four-state re-space), 19.2/19.3 (tick/gamma/distinguishability + 27.2), 21.1 (stage names), 22.1 (layout + warning), 23.1 (green box + six-vs-five), 24.1 (simplify + feedback), 25.1 (red-on-red), 26.1 (grouped bars), A.2 (independent cards), A.4 (scope-of-placement), Table 24-1 ("tool-use exploit rate", lower-is-better).

---

## 3. STILL-OPEN (documented, for next passes)

- **P2 (biggest systemic):** color-only / grayscale-insecure encoding still on a large fraction of figures (2.1, 3.1, 4.1, 7.1’s 8 group hues, 7.3, 7.4 FP16/FP8, 8.1, 11.1 sequences, 11.2 four concerns).
- **P2 (book’s best idea):** "aggregate ≠ per-rank" still footnote/ruler-resident in Figs 7.4/7.5 rather than native per-rank (80 GB) bar geometry.
- **P2:** Fig 4.1 still box-and-arrow one-to-one (teaches false bijection); recommends matrix/link-graph redesign.
- **P2:** Fig 11.1 time encoded orthogonally across panels + call-out overlaps squares; Fig 7.1 missing MHA side-by-side (8× asserted not shown); Fig 7.4/7.5 labels on hatch/bar fills.
- **P2:** Fig 6.2 x-axis ~55% blank, percentile labels overlap, p99 not on axis, straggler band un-legended.
- **P2:** Ch20 QPS vs book-canonical rps terminology drift (§20.4–20.9); Ch20 mini-case 250 QPS/host illustrative (flagged as such).
- **P2:** host/node/instance/GPU-node not unified to one canonical term ("host" = 8×H100).
- **P3:** Ch10 parallelism-strategy content triple-presented (Table 10-1 p129 + embedded table in Fig 10.1 p128 + standalone table p133) — consolidate; Fig 13.1 page whitespace; Fig 21.1 gate density; Fig 26.1 y-axis to ~1.1.
- **Technical/numerics:** all canonical chains (140 GB, 2.62 MB/token, 24.1/24.9/84/335 GB, 436 GB, C≈17.5, prefill 1.29 PFLOP→1.19 PFLOPS, decode 5.6 TB/s, ridges 295/206, in-flight 344, $14.6K/mo, fleet matrix, TCO, agentic I(T)) recompute consistently — **no action**.

---

## 4. CONCLUSION

- **Loop status: NOT converged.** Zero-new-comments was NOT reached. All P0 figure defects are gone, and the resolution of the two most consequential P1 items (Fig 8.2 intensity integrity; C/W 2.0) plus the Ch19 O_final arithmetic and the Fig 20.1/26.2/A.1/11.2 items substantially tightens the book.
- **Remaining blocker class:** the systemic color-only/grayscale dependency and the per-rank-geometry conversion (Figs 7.4/7.5), plus a handful of P2 re-layouts (4.1, 11.1, 7.1, 6.2) and the Ch20 QPS / host-node terminology drift. These are layout/design work best taken one figure-system at a time with raster verification (per the no-rush standard).
- **Recommendation:** continue the loop; the next passes should (a) convert 7.4/7.5 to native per-rank geometry and (b) break the color-only dependency via hatch/linestyle/text redundancy across the affected figures, then (c) the 4.1/11.1/7.1/6.2 re-layouts and terminology unification.

## 5. DELIVERABLE
Built `render/build/from-token-to-fleet-v20260913.pdf` (307 pp, tagged, 0 Type3). `check_tables.py` and `check_md_leaks.py` clean (build fails loud on either). Committed with identity **Zhiqi Tao <zhiqi.tao@gmail.com>**.
