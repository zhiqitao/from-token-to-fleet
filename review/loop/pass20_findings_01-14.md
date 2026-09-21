# PASS-20 REVIEW — Chapters 1–14 (rendered PDF) — PASS-19 FIX VERIFICATION + NEW FINDINGS

Re-reviewed the REBUILT rendered PDF (`/home/ubuntu/from-token-to-fleet-v20260913-full.pdf`,
built 2026-09-21 07:12) by raster-rendering the figure pages at 300 dpi with PyMuPDF and
inspecting the **pixel** crops (colour-column scans + zoomed vision), **not** the PDF text
layer. Figure page numbers carried over and re-confirmed against the current build (ch1 =
p.22, ch15 = p.171). Focal pages: Fig 10.1 = p.130, Fig 10.2 = p.135, Fig 8.1 = p.110,
Fig 7.3 = p.103, Fig 7.2 = p.102, Fig 7.4 = p.104, Fig 4.1 = p.68, Fig 12.1 = p.156,
Fig 6.2 = p.86, Fig 6.1 = p.84.

> Note on method: the full-page (low-zoom) vision passes on Fig 10.1/10.2 initially reported
> the OLD symptoms. Every such claim was re-checked against the **pixel** column data at the
> exact border rows, which is authoritative. All verdicts below are pixel-derived.

---

## RESULT SUMMARY

- **PASS-19 Fig 10.1 fix (P19-1) HAS LANDED.** Pixel-verified: both orange dashed container
  top borders run **UNBROKEN** across the full container width (uniform ~9–10 px dash gaps,
  no white masking gap at the border row), and the two band titles sit **INSIDE** their
  containers, well below the top dashed edge. The title **text** is clear of the child boxes.
- **All 10 named prior ch1–14 figure fixes still HOLD** (no regression): Fig 10.2 (the
  PASS-18 critical fix), Fig 8.1, 7.3, 7.2, 7.4, 4.1, 12.1, 6.2, 6.1.
- **TWO NEW MINOR findings** (both cosmetic figure-composition):
  - **P20-1** — each Fig 10.1 band-title's white pill background abuts the top border of the
    first child card (~1 px clearance, vs ~10 px intended), i.e. the label banner is flush
    against the first child box.
  - **P20-2** — Fig 12.1 decode-pool note region has overlapping layers: the red
    "excluded at quality gate" glyphs overprint the grey "bandwidth-bound" line, and the
    large black "8×H100 host)" axis text overprints the grey note.

---

## A. PASS-19 FIG 10.1 FIX — VERIFICATION (PDF p.130 @ 300 dpi)

| Check | Result | Evidence (rendered raster) |
|---|---|---|
| Top container dashed border UNBROKEN across top | **PASS** | Border row ~973–974 spans x≈415–2140 px; orange-run analysis gives uniform ~9–10 px dash gaps with **no** wide white gap anywhere (incl. the label's x-range). |
| Pipeline container dashed border UNBROKEN across top | **PASS** | Border row ~1848–1849 spans x≈425–1938 px; uniform ~9–10 px dash gaps, no wide gap. |
| Band title INSIDE container below dashed border | **PASS** | "Expert parallel (all-to-all)" text rows ~1018–1030 vs border ~973 (≈45 px below); "Pipeline (DP × TP × PP)" text rows ~1888–1905 vs border ~1848 (≈40 px below). |
| Band title text clear of child boxes | **PASS** | Top: title glyphs end ~row 1030, GPU A card top border ~row 1037 → ~7 px gap. Pipeline: title glyphs end ~row 1905, PP stage-1 card top ~row 1913 → ~8 px gap. No glyph overlaps a child box. |

**Verdict: the PASS-19 fix LANDED.** The two orange dashed container edges are no longer
masked/interrupted by the title pill; each band title sits inside its container below an
unbroken dashed top edge, and the title glyphs are clear of the child boxes. **P19-1 / P18-2
can be closed.**

*(Remaining nuance → finding P20-1: the title's white pill background extends down to abut the
first child card's top border — cosmetic.)*

---

## B. PASS-18 CRITICAL FIX — STILL HOLDS (Fig 10.2, PDF p.135 @ 300 dpi)

| Check | Result | Evidence |
|---|---|---|
| EP "experts 6-10" final "0" visible & un-occluded | **PASS** | Zoomed crop + glyph extents: full "experts 6-10" present; the "0" is fully inside GPU B (text ends x≈451.8 pt, well left of the box right edge) and clear of GPU C (white gap between boxes). |
| EP child boxes non-overlapping | **PASS** | Three green child cards separated by visible white gaps; no intersecting rectangles. |
| "PP · Pipeline Parallel" terminal "l" inside | **PASS** | Word ends x≈482.7 pt; cyan parent-box right border at x≈504.7 pt → **22 pt** inside margin. |
| "CP · Context Parallel" terminal "l" inside | **PASS** | Word ends x≈250.8 pt; grey parent-box right border at x≈274.8 pt → **24 pt** inside margin. |

**Fig 10.2 critical fix still fully HOLDS. P17-2 / P18-1 remains closed.**

---

## C. PRIOR-FIX REGRESSION CHECK (rendered; all HOLD)

| Prior ID | Figure (p.) | Prior status | PASS-20 status | Evidence |
|---|---|---|---|---|
| P17-1 | Fig 8.1 ladder (p.110) | LANDED | **HOLDS** | All seven box labels inside their boxes; title/subtitle clear of the top "registers" box. |
| P17-3 | Fig 7.3 memory floor (p.103) | LANDED | **HOLDS** | Full fine-tune reads **~1120 GB**; inference **~165 GB**; QLoRA **~60 GB**; ticks legible, no truncation/overlap. |
| P17-9 | Fig 7.2 KV vs context (p.102) | LANDED | **HOLDS** | Legend outside plot (right margin), clear of curves; FP8 labelled "full-MHA FP8 (byte-halving bound, ~1.3 MB/tok)"; "9.2K ≈ 24 GB (FP16 bound)" clear of the ~436 GB KV-budget line. |
| P17-8 | Fig 7.4 host pool (p.104) | LANDED | **HOLDS** | FP8 row carries its own "140 GB weights" + "~64 GB"; in-figure title matches caption lead-in. (Runtime block visually ≈140–200 GB (~60 GB) though labelled ~64 GB — same pre-existing approximation accepted in prior passes; not a regression.) |
| P17-4 | Fig 4.1 six dimensions (p.68) | LANDED | **HOLDS** | Six left axes present (Quality requirements / Traffic & concurrency / Token profile / Latency SLO / Economic constraints / Operational constraints), each mapped one-to-one to a consequence. |
| P17-10 | Fig 12.1 note (p.156) | LANDED | **HOLDS** | Decode-pool note clear of the (b) P/D-disagg bar and the "~19.8K" label. (Note-region overlap with the red annotation → new P20-2.) |
| P17-7 | Fig 6.2 mean 0.85 (p.86) | LANDED | **HOLDS** | Figure labels **"mean = 0.85s"**; no 0.84. |
| P17-5 | Fig 6.1 chain (p.84) | LANDED | **HOLDS** | Legend "Direction of the chain": green = Causation ↓ (workload→serving), red dashed = Diagnosis ↑ (serving→workload); legible, non-overlapping. |

---

## D. FINDINGS

### [P20-1] MINOR — Fig 10.1 band-title white pills abut the top border of the first child card
- **Location:** Chapter 10 (Parallelism), Fig 10.1 "Composing the parallel dimensions", PDF
  p.130; both bands ("Expert parallel (all-to-all)" over GPU A, "Pipeline (DP × TP × PP)"
  over PP stage 1).
- **Problem:** At 300 dpi pixel columns, each title's opaque white pill background extends
  down to **abut** (≈1 px clearance to) the top border of the first child card: top band pill
  bottom row ≈1036 vs GPU A card top ≈1037; pipeline pill bottom ≈1911 vs PP stage-1 card top
  ≈1913. The band label therefore sits **flush** against the first child box rather than with
  clear whitespace (~10 px was intended by the fixer: banner 64–80, child top 90). The title
  text glyphs themselves remain clear (≈7–8 px above the card), so legibility is unaffected.
- **Why it matters:** §23 publication-quality figure; a container title that sits flat against
  its first child looks cramped and reduces the visual separation intended between the band
  label and the content. Cosmetic only — not a factual error.
- **Recommended:** In the Archify source `render/archify/ch10-compose.json` / deliver HTML,
  reduce the banner's bottom padding or add ~8–10 px of vertical clearance between the bottom
  of each band-title pill and the top of the first child card, so the label floats in its own
  space below the unbroken dashed border.

### [P20-2] MINOR — Fig 12.1 decode-pool note region has overlapping text layers
- **Location:** Chapter 12 (Candidate architecture synthesis), Fig 12.1 (2) prefill panel,
  PDF p.156, margin above the axes.
- **Problem:** In the rendered raster at 600 dpi, the grey decode-pool note
  ("decode pool: … / bandwidth-bound (no digit)") is over-printed: the red
  "excluded at quality gate" annotation's line 1 ("excluded at") is **superimposed on** the
  grey "bandwidth-bound" line, and the large black axis-category text "8×H100 host)"
  over-prints the grey "decode pool:" / "bandwidth-bound" lines. Pixel colour-mask analysis
  confirms the red and grey bounding boxes overlap (~182 px × ~79 px), and the text-layer word
  extents interleave (e.g. grey "host)" x≈458–489 pt vs red "excluded" x≈460–505 pt, same
  y-band). The note is still clear of the (b) bar and the "~19.8K" label (so P17-10 holds),
  but the note text itself collides with the red annotation and the black axis label.
- **Why it matters:** §23 figure polish; overlapping grey/red/black text in the margin is
  visually noisy and marginally reduces legibility of the note. Cosmetic, not factual.
- **Recommended:** In the Fig 12.1 source, offset the red "excluded at quality gate"
  annotation (e.g. move it up/right or add a blank line above the grey note) and pull the grey
  decode-pool note clear of the black "8×H100 host)" category text, so the three layers each
  sit in their own whitespace.

No other new defect, legibility problem, numerical inconsistency, or cross-chapter
contradiction surfaced in the verified ch1–14 figure set.

---

## E. FINAL VERDICT

- **PASS-19 Fig 10.1 fix LANDED.** The two orange dashed container top borders now run
  UNBROKEN, band titles sit inside below them, and title text is clear of the child boxes.
  Close P19-1 / P18-2.
- **All named prior ch1–14 figure fixes hold** (Fig 10.2 critical + Fig 8.1, 7.3, 7.2, 7.4,
  4.1, 12.1, 6.2, 6.1) — no regression.
- **Two NEW MINOR cosmetic findings:** P20-1 (Fig 10.1 title pills flush against first child
  card) and P20-2 (Fig 12.1 note-region grey/red/black text overlap).
- **No CRITICAL / MAJOR / MODERATE findings.** The figure-legibility convergence tail
  continues toward a clean exit; remaining items are MINOR-only styling.
