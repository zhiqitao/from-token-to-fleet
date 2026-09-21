# PASS-21 REVIEW — Chapters 1–14 (rendered PDF) — PASS-20 FIX VERIFICATION

Re-reviewed the REBUILT rendered PDF (`/home/ubuntu/from-token-to-fleet-v20260913-full.pdf`,
build D:20260921083651-07'00', 308 pages) by raster-rendering the figure pages with PyMuPDF
at 250–600 dpi and inspecting **placed-page pixel** data (full row/column histograms + colour
masks + zoomed crops). **Not** the PDF text layer, **not** source PNGs alone. Figure page
numbers re-confirmed against this build: ch1 = p.22; Fig 4.1 = p.68, Fig 6.1 = p.84,
Fig 6.2 = p.86, Fig 7.2 = p.102, Fig 7.3 = p.103, Fig 7.4 = p.104, Fig 8.1 = p.110,
Fig 10.1 = p.130, Fig 10.2 = p.135, Fig 12.1 = p.156.

> Method note (same lesson as prior passes): low-zoom full-page vision repeatedly over-reports
> the OLD symptoms (Fig 10.1 dashed border "masked", Fig 8.1 registers label "clipped").
> Every such claim was re-checked against the authoritative pixel data at the exact rows/cols.
> Pixel verdicts below.

---

## RESULT SUMMARY

- **P20-1 (Fig 10.1 pill-to-card clearance ≥10 pt) — FAILED TO LAND.** Placed-page pixel
  measurement shows the band-title white pill **still abuts** the first child card: top band
  pill bottom ≈ row 2073 (600 dpi) vs GPU A card top border ≈ row 2074 (~**0.12 pt** gap);
  pipeline band pill bottom ≈ row 1909 (300 dpi) vs PP stage-1 card top ≈ row 1912
  (~**0.72 pt** gap). Not the claimed ~10.4 pt. Root cause: the Archify source
  `render/archify/ch10-compose.json` still has EP child y=90 / PP stage y=560 (pre-fix values;
  fixer claimed 90→100 / 560→570), and `ch10-compose-deliver.html` contains **BOTH** the old
  (y=90/560) and new (y=100/570) element sets, so the placed render shows the old card
  position. Only a single card band is present (peach fill starts row 1040 @300 dpi — no
  second card at the shifted position).
- **P20-2 (Fig 12.1 note separation) — PARTIALLY LANDED.** The grey note and the red
  annotation are now separated **from each other** (grey note rows ~1030–1118 / red
  annotation rows ~1237–1317 in the prefill panel — disjoint rows and disjoint col ranges:
  grey cols ≤1578, red cols ≥1859). **But BOTH still overprint the black panel-2 title:**
  grey "decode pool:" / "bandwidth-bound" sit on top of "(2) Prefill throughput (idealized
  **aggregate, 8×H100** host)" (over "aggregate, 8×H100"), and red "(c) **excluded at**" sits
  on top of "...host**)**". The fixer's claim "grey and red in separate whitespace, **both
  clear of black axis/category text**" is **not** met on the placed page.
- **PASS-19 Fig 10.1 dashed-border fix HOLDS.** Top container border row 973 runs UNBROKEN
  (77 dash segments, uniform ~8 px gaps, max gap 8 px, **19 dashes present across the
  title x-range 560–960**); pipeline container border rows 1848/1849 likewise unbroken
  (67–68 dashes, max gap ≤9 px). Both band titles sit inside below an unbroken dashed edge.
- **All other named prior ch1–14 figure fixes HOLD (no regression):** Fig 10.2 ("experts
  6-10" final "0" visible, children non-overlapping, "PP/CP · Parallel" terminals inside),
  Fig 8.1 (labels inside boxes; "fastest · smallest" at rows 797–825 inside registers box
  690–857, ~7.7 pt bottom margin), Fig 7.3 (~1120 / ~165 / ~60 GB all legible), Fig 6.2
  ("mean = 0.85s"), plus Fig 7.2, 7.4, 4.1, 6.1 (not touched by the PASS-20 build; prior
  holdings re-confirmed). Fig 20.1 "~28 hosts" and Fig A.4 arrow-up (outside ch1–14; not
  touched by PASS-20 build — hold per PASS-18/20 confirmation).
- No CRITICAL / MAJOR / MODERATE findings. Two MINOR items, both **PASS-20 fix-verification
  failures** (see below).

---

## A. PASS-20 FIX VERIFICATION (placed-page pixel)

### A1. P20-1 — Fig 10.1 pill-to-card clearance (PDF p.130)

| Check (≥10 pt intended) | Result | Evidence (placed raster) |
|---|---|---|
| Top band title pill clear of GPU A card (≥10 pt) | **FAIL** | Pill (white, over title text rows 1019–1028 @300 dpi) bottom = row ~2073 @600 dpi; GPU A card top border = row ~2074 @600 dpi → gap ≈ **1 px = 0.12 pt**. Peach card fill starts row 1040 @300 dpi. |
| Pipeline band title pill clear of PP stage-1 card | **FAIL** | Pill bottom ≈ row 1909 @300 dpi; PP stage-1 card top ≈ row 1912 @300 dpi → gap ≈ **3 px = 0.72 pt**. |
| Card top at the fixed y=100 / y=570 position | **FAIL** | Single card band only, top at row 1037 @300 dpi (y=90 position). No card at the shifted y=100 position. Source `ch10-compose.json` still y=90 / y=560. |

**Verdict:** P20-1 is **NOT closed**. The pill-to-card clearance is still ~0.1–0.7 pt
(essentially flush), not the claimed ~10.4 pt.

### A2. P20-2 — Fig 12.1 note separation (PDF p.156)

| Check | Result | Evidence (placed raster) |
|---|---|---|
| Grey note vs red annotation separated | **PASS** | Grey note rows 1030–1118 (cols 878–1578); red annotation rows 1237–1317 (cols 1859–2164) — disjoint rows and cols. |
| Grey note clear of black title text | **FAIL** | Grey "decode pool:" / "bandwidth-bound" overprint black panel-2 title "(2) Prefill throughput (idealized **aggregate, 8×H100** host)" over the words "aggregate, 8×H100". Confirmed at 600 dpi. |
| Red annotation clear of black title text | **FAIL** | Red "(c) **excluded at**" sits on the black "**host)**" tail of the title. |

**Verdict:** P20-2 only **partially** landed (grey/red mutual-separation achieved, but both
layers still overprint the panel-2 title). The fixer's "both clear of black axis/category
text" is not satisfied.

---

## B. PRIOR-FIX REGRESSION CHECK (rendered; all HOLD)

| Prior ID | Figure (p.) | PASS-21 status | Evidence |
|---|---|---|---|
| P19-1 / P18-2 | Fig 10.1 unbroken dashed border (p.130) | **HOLDS** | Row 973 & 1848/1849 dash runs uniform (max gap ≤9 px), present across title x-range. |
| P18-1 | Fig 10.2 "experts 6-10" + non-overlap (p.135) | **HOLDS** | Full "experts 6-10" incl. final "0"; three green children separated; "PP/CP · Parallel" terminals inside. |
| P17-1 | Fig 8.1 ladder (p.110) | **HOLDS** | Labels inside boxes; "fastest · smallest" rows 797–825 inside registers box 690–857 (~7.7 pt margin). |
| P17-3 | Fig 7.3 memory floor (p.103) | **HOLDS** | Full fine-tune ~1120 GB, inference ~165 GB, QLoRA ~60 GB; ticks legible. |
| P17-7 | Fig 6.2 mean (p.86) | **HOLDS** | Label reads "mean = 0.85s". |
| P17-4 | Fig 4.1 six dimensions (p.68) | **HOLDS** | (not touched by PASS-20 build) |
| P17-5 | Fig 6.1 chain legend (p.84) | **HOLDS** | (not touched) |
| P17-9 | Fig 7.2 KV vs context (p.102) | **HOLDS** | (not touched) |
| P17-8 | Fig 7.4 host pool (p.104) | **HOLDS** | (not touched) |
| P18 | Fig 20.1 "~28 hosts" | **HOLDS** | (outside ch1–14; not touched) |
| P18 | Fig A.4 arrow-up | **HOLDS** | (not touched) |

---

## C. FINDINGS

### [P21-1] MINOR — Fig 10.1 P20-1 pill-to-card clearance fix did NOT land
- **Location:** Chapter 10, Fig 10.1 "Composing the parallel dimensions", PDF p.130; both
  bands ("Expert parallel (all-to-all)" over GPU A, "Pipeline (DP × TP × PP)" over PP stage 1).
- **Problem:** In the placed-page raster the band-title white pill still abuts the first
  child card (~0.12 pt top band, ~0.72 pt pipeline band) — not the ~10.4 pt the PASS-20
  fixer reports. The card top border sits at the pre-fix row (1037 @300 dpi, i.e. the
  y=90/y=560 position). The title glyphs themselves are clear of the card (≈7–8 px), so
  legibility is unaffected — but the intended whitespace was not achieved.
- **Why it matters:** §23 publication-quality figure. The band label reads as flush against
  its first child rather than floating in its own whitespace; also a fix-verification failure.
- **Recommended:** Actually commit the shift in `render/archify/ch10-compose.json` (EP child
  y 90→100, PP stage y 560→570), remove the stale y=90/560 element set from
  `ch10-compose-deliver.html`, and re-render; re-measure to ≥10 pt pill-to-card clearance on
  the placed page.

### [P21-2] MINOR — Fig 12.1 P20-2 note fix only partially landed (notes still overprint title)
- **Location:** Chapter 12, Fig 12.1 panel (2) Prefill throughput, PDF p.156, note region
  above the axes.
- **Problem:** Grey/red separation is achieved (grey note and red annotation no longer
  overprint each other), but the grey note ("decode pool:" / "bandwidth-bound") still
  overprints the black panel-2 title "(2) Prefill throughput (idealized aggregate, 8×H100
  host)" over "aggregate, 8×H100", and the red "(c) excluded at" still overprints the title
  tail "host)". Three text layers still collide on the placed page.
- **Why it matters:** §23 figure polish; text-on-text overprint of the panel title is
  visually noisy and marginally degrades legibility of the title. Cosmetic, not factual.
- **Recommended:** In the Fig 12.1 source, move the grey note further left/down into the
  plot-area whitespace and the red annotation into the right margin, both clear of the panel
  title baseline (title is centered across cols ~384–1953 @300 dpi); re-verify on the placed
  raster with row/col histograms, not just the deliver PNG.

No other new defect, legibility problem, numerical inconsistency, or cross-chapter
contradiction surfaced in the verified ch1–14 figure set.

---

## D. FINAL VERDICT

- **PASS-20 Fig 10.1 pill-to-card clearance (P20-1): NOT LANDED** (still ~0.1–0.7 pt flush;
  source JSON un-updated, deliver HTML has duplicate old+new elements). P20-1 remains open.
- **PASS-20 Fig 12.1 note separation (P20-2): PARTIALLY LANDED** — grey/red separated, but
  both still overprint the panel-2 title. The "clear of black axis text" requirement is not
  met. P20-2 remains partially open.
- **PASS-19 Fig 10.1 unbroken dashed border HOLDS** (re-confirmed; no regression).
- **All named prior ch1–14 figure fixes hold** (Fig 10.2, 8.1, 7.3, 7.2, 7.4, 4.1, 6.1, 6.2,
  plus 20.1 and A.4 outside ch1–14) — no regression.
- **No CRITICAL / MAJOR / MODERATE findings.** Two MINOR items, both PASS-20 fix-verification
  failures. The figure-legibility convergence tail continues; remaining items are MINOR-only,
  but the two PASS-20 fixes must actually be applied (committed to source + re-rendered)
  before the loop can exit cleanly.
