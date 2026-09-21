# PASS-19 REVIEW — Chapters 1–14 (rendered PDF) — PASS-18 FIX VERIFICATION + NEW FINDINGS

Re-verified every named PASS-18 / PASS-17 ch1–14 fix against the REBUILT rendered PDF
(`/home/ubuntu/from-token-to-fleet-v20260913-full.pdf`) by rendering the actual figure
pages at 300 dpi with PyMuPDF and inspecting the **raster** (pixel-level crops + vision),
**not** the PDF text layer. Figure page numbers carried over from PASS-18 (ch1 = PDF p.22,
ch15 = p.171; Fig 10.2 = p.135, Fig 10.1 = p.130, Fig 20.1 = p.234, Fig A.4 = p.296,
Fig 15.1 = p.175).

---

## RESULT SUMMARY

- **PASS-18 CRITICAL fix (Fig 10.2) HAS LANDED.** Verified in the rendered raster at 300 dpi
  (pixel crops): the EP "expert …" child boxes no longer overlap; GPU B reads
  **"experts 6-10"** with the final **"0" fully visible** (not occluded by GPU C);
  the Pipeline and Context parent sub-labels read **"PP · Pipeline Parallel"** and
  **"CP · Context Parallel"** with the terminal **"l" fully visible** inside each box.
- **All 7 of the 8 previously-confirmed PASS-17 ch1–14 figure fixes still HOLD** (no regression).
- **The PASS-17 fix P17-6 (Fig 10.1) main item still holds** (purple title vs monospaced
  sentence now clearly separated); its **minor residual (P18-2) is STILL OPEN** — the orange
  band titles still overprint the dashed container top borders inside a white tab.
- **Confirmation figures all hold:** Fig 20.1 "≈28 hosts: 70% target (⌈40/(2.1×0.70)⌉ = 28)"
  fully legible; Fig A.4 red axis **arrow points UP**; Fig 15.1 Before/After panel headings
  clearly separated.
- **NO NEW FINDINGS** in the verified ch1–14 figure set beyond the already-known P18-2 minor
  residual (reported below as still-open). All canonical numerics re-checked remain consistent.

---

## A. PASS-18 CRITICAL FIX — VERIFICATION (Fig 10.2, PDF p.135 @ 300 dpi)

| Check | Result | Evidence (rendered raster) |
|---|---|---|
| EP "experts 6-10" final "0" NOT occluded | **PASS** | GPU B child box reads **"experts 6-10"**; the "0" is fully inside the box and clear of GPU C. |
| EP child boxes do not overlap | **PASS** | GPU A / B / C child boxes are clearly separated with visible white gaps between them; no intersecting rectangles. |
| "PP · Pipeline Parallel" terminal "l" visible | **PASS** | Full string inside the cyan parent box; terminal "l" fully inside with padding, not on/crossing the right border. |
| "CP · Context Parallel" terminal "l" visible | **PASS** | Full string inside the grey parent box; terminal "l" fully inside with padding, not clipped. |
| EP parent sub-label "EP · Expert Parallel" | **PASS** | Complete and centered under "MoE experts". |

**Verdict: the PASS-18 critical fix LANDED and is confirmed in the raster.** The earlier
P17-2/P18-1 report can be closed.

---

## B. CONFIRMATION FIGURES (rendered)

| Figure (PDF p.) | Check | Result |
|---|---|---|
| Fig 20.1 (p.234) | "≈28 hosts: 70% target (⌈40/(2.1×0.70)⌉ = 28)" | **PASS** — fully legible, blue annotation + leader arrow to the 70% line; clear of the red "~20 hosts: saturation" note. |
| Fig A.4 (p.296) | arrow points up | **PASS** — single red vertical axis with arrowhead at the top (north of tail), running bottom-to-top "more of the intelligence and compute budget". |
| Fig 15.1 (p.175) | captions separated | **PASS** — "BEFORE: naive / SDPA" and "AFTER: FlashAttention" headings each inside their own grey panel with clear whitespace; no overlap. |

---

## C. PASS-17 FIX REGRESSION CHECK (rendered; no regressions)

| PASS-17 ID | Figure (PDF p.) | Prior status | PASS-19 status | Evidence |
|---|---|---|---|---|
| P17-1 | Fig 8.1 ladder (p.110) | LANDED | **HOLDS** | All seven box labels inside their boxes; title/subtitle clear of the top 'registers' box. (Secondary descriptors sit tight to box bottoms but with positive padding — no descender glyphs in those strings, so no clipping. Not a defect.) |
| P17-3 | Fig 7.3 memory floor (p.103) | LANDED | **HOLDS** | Full fine-tune bar reads **~1120 GB**; inference **~165 GB**; QLoRA **~60 GB**; x-tick labels fully wrapped, no truncation/overlap. |
| P17-9 | Fig 7.2 KV vs context (p.102) | LANDED | **HOLDS** | Legend outside plot (right margin), clear of curves; FP8 curve labelled **"full-MHA FP8 (byte-halving bound, ~1.3 MB/tok)"**; "9.2K ≈ 24 GB (FP16 bound)" annotation clear of the ~436 GB KV-budget line. |
| P17-8 | Fig 7.4 host pool (p.104) | LANDED | **HOLDS** | FP8 row carries its own **"140 GB weights"** and **"~64 GB"** labels; runtime segment at true ~64 GB width; in-figure title matches caption lead-in. |
| P17-4 | Fig 4.1 six dimensions (p.68) | LANDED | **HOLDS** | Six left axes: Quality requirements / Traffic-concurrency / Token profile / Latency SLO / Economic constraints / Operational constraints, each mapped to a consequence. |
| P17-10 | Fig 12.1 decode note (p.156) | LANDED | **HOLDS** | Grey "decode pool: 8×H100 host / bandwidth-bound (no digit)" note repositioned in the margin above the axes; clear of the (b) P/D-disagg bar and the "~19.8K" label. |
| P17-7 | Fig 6.2 mean 0.85 (p.86) | LANDED | **HOLDS** | Figure labels **"mean = 0.85s"**; no 0.84 anywhere in the figure. |
| P17-5 | Fig 6.1 diagnostic chain (p.84) | LANDED | **HOLDS** | Legend **"Direction of the chain"** maps green solid = Causation ↓ (workload→serving) and red dashed = Diagnosis ↑ (serving→workload); legible, non-overlapping. |
| P17-6 | Fig 10.1 compose (p.130) | PARTIALLY | **MAIN HOLDS; residual still open** | Purple-box title "the per-stage DP × TP mesh" and the monospaced "the same GPUs also take part in EP all-to-all" are now clearly separated. Band-title residual persists (see finding below). |

---

## D. FINDINGS

### [P19-1] MINOR (still-open residual of P17-6 / P18-2) — Figure 10.1 orange band titles still overprint the dashed container top borders
- **Location:** Chapter 10 (Parallelism), Fig 10.1 "Composing the parallel dimensions", PDF p.130, the "Expert parallel (all-to-all)" and "Pipeline (DP × TP × PP)" band titles.
- **Problem:** Confirmed at 300 dpi pixel crop. Each orange monospaced band title sits **on/through the top dashed border** of its orange dashed container. The renderer draws a continuous dashed rule, then composites an opaque **white rectangular tab** behind the title text that masks the dashes underneath; the dashes are visible on either side of the text but absent behind it. The words are not fully in blank space above the border.
- **Why it matters:** §23 — publication-quality figure; a title should not interrupt the dashed container edge. It is a small, purely visual defect, not a factual error, so severity is MINOR.
- **Recommended change:** In `render/fig_ch10_compose.py` (or the figure source), move each band title a full text-line **above** the dashed top edge so the dashed border runs unbroken across the full container width (remove the white masking tab, or place the label in empty space above the box).

No other new defect, legibility problem, numerical inconsistency, or cross-chapter contradiction surfaced in the verified ch1–14 figure set.

---

## E. FINAL VERDICT

- **PASS-18 CRITICAL fix (Fig 10.2) LANDED** and is verified in the rendered raster — "experts 6-10" with visible "0", non-overlapping child boxes, full "PP · Pipeline Parallel" / "CP · Context Parallel". Close P17-2/P18-1.
- **All 8 PASS-17 ch1–14 figure fixes still hold** (no regression), and the three confirmation figures (20.1 "≈28 hosts", A.4 up-arrow, 15.1 separated captions) are correct.
- **One MINOR residual remains open:** Fig 10.1 band titles overprint the dashed container top borders (P19-1, formerly P18-2). Recommend a small figure-source edit and one more raster re-check.
- **No other new findings.**
