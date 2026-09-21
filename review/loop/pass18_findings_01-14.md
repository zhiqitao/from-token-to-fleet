# PASS-18 REVIEW — Chapters 1–14 (rendered PDF) — PASS-17 FIX VERIFICATION + NEW FINDINGS

Re-verified every PASS-17 ch1–14 fix against the REBUILT rendered PDF
(`/home/ubuntu/from-token-to-fleet-v20260913-full.pdf`), by rendering the actual
figure pages at 150–600 dpi with PyMuPDF and inspecting the raster visually
(vision + pixel-level crops), **not** by trusting the source `.md` or the
extracted PDF text layer. Figure page numbers match PASS-17 (ch1 = PDF p.22,
ch15 = p.171; figure pages unchanged in the rebuild).

---

## RESULT SUMMARY

- **7 of the 8 explicitly-listed ch1–14 PASS-17 fixes CONFIRMED LANDED.**
- **PASS-17 fix P17-2 (Figure 10.2) DID NOT LAND.** The "experts 6-1" defect and
  the clipped "PP · Pipeline Paralle" / "CP · Context Paralle" sub-labels are
  **still visibly present** in the rendered book.
- **Important correction to the task premise:** the PDF text layer *does* contain
  the full correct strings ("experts 6-10", "PP · Pipeline Parallel",
  "CP · Context Parallel"), but that does **NOT** mean the defect is absent. The
  clipping/occlusion happens at **render** time — the glyphs are truncated by
  overlapping child boxes and by sub-label text whose bounding box is wider than
  its parent box. Text-only or extracted-text review still misses it, exactly as
  PASS-17 warned. Verified at 600 dpi; the correct strings exist as PDF text but
  are not legible to the reader.

---

## A. PASS-17 FIXES — VERIFICATION TABLE

| PASS-17 ID | Figure (PDF p.) | Status | Evidence (rendered inspection) |
|---|---|---|---|
| P17-1 | Fig 8.1 ladder (p.110) | **LANDED** | All seven box labels fully inside their boxes, no clipping; title/subtitle clear of the top registers box (no overlap). Boxes: registers / tensor cores·ALU / shared mem (SRAM) / L2 cache / HBM (GPU memory) / GPU interconnect / other GPUs·remote. |
| P17-3 | Fig 7.3 memory floor (p.103) | **LANDED** | Full fine-tune bar now reads **~1120 GB** (was ~1260). Inference **~165 GB**, QLoRA **~60 GB**. x-tick labels fully wrapped, none truncated; no arrow/label overlap. |
| P17-9 | Fig 7.2 KV vs context (p.102) | **LANDED** | Legend moved **outside** the plot (right margin), off the 640 GB line/curves. FP8 curve re-labelled **"full-MHA FP8 (byte-halving bound, ~1.3 MB/tok)"**. "9.2K ≈ 24 GB (FP16 bound)" annotation now clear of the ~436 GB KV-budget line. |
| P17-8 | Fig 7.4 host pool (p.104) | **LANDED** | FP8 row now carries its own **"140 GB weights"** and **"~64 GB"** labels; runtime segment drawn at its true ~64 GB width; in-figure title matches caption lead-in ("The concurrency budget: where a 70B host's 640 GB pool goes"). |
| P17-4 | Fig 4.1 six dimensions (p.68) | **LANDED** | Six left axes now the framework dimensions: **Quality requirements / Traffic·concurrency / Token profile / Latency SLO / Economic constraints / Operational constraints**, each mapped to a true architectural consequence. |
| P17-10 | Fig 12.1 decode note (p.156) | **LANDED** | Grey "decode pool: 8×H100 host / bandwidth-bound (no digit)" note repositioned into the margin above the axes, clear of the (b) P/D-disagg bar and the "~19.8K" value label. |
| P17-7 | Fig 6.2 mean 0.85 vs 0.84 (p.86) | **LANDED** | Figure labels "mean = 0.85s"; the reconciling note now lives in §6.4.1 prose (p.85): "mean ≈ 0.84 s; the figure's exact simulated stream mean ≈ 0.85 s — the 0.84 is the two-point analytic approximation". Figure and text now agree. |
| P17-2 | Fig 10.2 parallelization (p.135) | **NOT LANDED** | See finding [P18-1] below. |

Additional ch1–14 PASS-17 findings (not in the 8-item list) re-checked:

| PASS-17 ID | Figure | Status | Evidence |
|---|---|---|---|
| P17-5 | Fig 6.1 diagnostic chain (p.84) | **LANDED** | Legend box "Direction of the chain" added, mapping green solid = Causation ↓ (workload→serving) and red dashed = Diagnosis ↑ (serving→workload). Directional meaning now explicit. (Arrows still in legend markers rather than on the connector lines — acceptable, conveys the direction.) |
| P17-6 | Fig 10.1 compose (p.130) | **PARTIALLY LANDED** | Purple-box bold title "the per-stage DP × TP mesh" and the monospaced sentence "the same GPUs also take part in EP all-to-all" are now clearly separated (whitespace between). **Residual (minor):** the orange band titles ("Expert parallel (all-to-all)", "Pipeline (DP × TP × PP)") still sit ON the dashed container top border via a white tab that overprints the dashed line, rather than fully above it. |

---

## B. NEW / STILL-OPEN FINDINGS (severity classified)

### [P18-1] CRITICAL (did not land / regression of P17-2) — Figure 10.2 still clips "experts 6-1" and truncates "PP · Pipeline Paralle" / "CP · Context Paralle"
- **Location:** Chapter 10 (Parallelism), figure 10.2 "The five parallelization strategies and what each splits", PDF p.135 (book p.115), Expert-Parallel and Pipeline/Context parent boxes.
- **Problem:** Confirmed at 600 dpi. (a) The Expert-Parallel **GPU B** child box still renders **"experts 6-1"** — the "0" of the intended "6-10" is **completely occluded** by the adjacent GPU-C child box (the three child boxes **overlap**: GPU B right edge ≈461.2 pt > GPU C left edge ≈458.7 pt; GPU A right ≈405.3 > GPU B left ≈402.9), so the reader sees an **incorrect expert range**. (b) The Pipeline parent sub-label renders **"PP · Pipeline Paralle"** (final "l" clipped — sub-label bbox x≈373.8–479.4 vs parent box x≈375.9–477.3, so the text is wider than the box). (c) The Context parent sub-label renders **"CP · Context Paralle"** (final "l" clipped — sub-label bbox x≈137.3–238.0 vs box x≈140.2–235.2).
- **Why it matters:** §23/§49 — publication-quality figure must not clip content. More importantly, "experts 6-1" is a **factual error** the reader can read: it misstates the EP split. This is the same defect PASS-17 flagged as CRITICAL and the reason ch0 perf/figure passes kept converging falsely: the PDF **text layer is correct** ("experts 6-10", "…Pipeline Parallel", "…Context Parallel"), so any text-only verification passes, yet the raster reader still sees the clipped/misleading string. The PASS-18 task premise that "the text layer shows full … so the defect is absent" is therefore **incorrect** — the defect is still present in the rendered book.
- **Recommended change:** In `render/fig_ch10_*.py`: (i) stop the three EP child boxes from overlapping (use non-overlapping x positions / wider figure or smaller child-box width) so "experts 6-10" is fully visible; (ii) widen the PP and CP parent boxes (or reduce sub-label font) so "…Pipeline Parallel" / "…Context Parallel" fit fully inside with padding. Regenerate `fig-10-*.png` and rebuild. Re-verify by pixel crop, not by text extraction.
- **Root cause to also fix:** the child boxes are drawn overlapping each other, which is what hides the "0" — self-occlusion, distinct from the parent-box text-underflow case.

### [P18-2] MINOR (residual of P17-6) — Figure 10.1 band titles still overprint the dashed container borders
- **Location:** Chapter 10, figure 10.1 "Composing the parallel dimensions", PDF p.130.
- **Problem:** The orange band titles "Expert parallel (all-to-all)" and "Pipeline (DP × TP × PP)" still sit on the top edge of their dashed containers inside a white tab that overprints the dashed border, rather than cleanly above it.
- **Why it matters:** §23 — minor visual overlap; the main P17-6 overlap (purple title overprinting the monospaced sentence) is fixed, so only this small border-interruption remains.
- **Recommended change:** Move the band titles fully above (not on) the dashed container top edges.

---

## C. RE-VERIFICATION OF WIDER CONTENT (no new defect found outside the figures)

Beyond the fix-verification, I re-checked the ch1–14 canonical numerics against the prose
(the audit items PASS-17 already confirmed) and they remain internally consistent:
KV/token 2.62/1.31/1.42 MB/tok; 24.1/24.9 GB; 140 GB weights; ~64 GB runtime; ~436 GB KV
budget; C≈18 (FP16) / ~33 (FP8); 1.29 PFLOP prefill; 346 TFLOPS©; 2,471 & 19,800 tok/s;
~295 FLOP/byte; ~344 in flight; ~5 avg / ~19–20 peak hosts; $0.012/req; 16.5M in / 540K
out tokens/$. No new prose/numerical/cross-chapter contradiction surfaced.

---

## D. FINAL VERDICT

- **7 of 8 listed ch1–14 PASS-17 figure fixes landed and are visually verified.**
- **One critical fix did NOT land:** Figure 10.2 "experts 6-1" + "PP/CP … Paralle" clipping
  (P17-2). This is the sole remaining ch1–14 figure defect, and it is the kind that only a
  rendered-raster pass catches — the PDF text layer is correct, so any extracted-text
  verification will (wrongly) report it as fixed.
- **One minor residual:** Figure 10.1 band titles still overprint the dashed container edges
  (P17-6 partially landed).
- **Recommendation:** Regenerate Figure 10.2 (widen/stop overlapping child boxes and parent
  boxes, or shrink sub-label font) and re-verify by pixel crop; then re-run the sibling
  visual pass on ch15–27 to confirm no analogous clipping there.
