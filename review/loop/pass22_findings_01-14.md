# PASS-22 REVIEW — Chapters 1–14 (rendered PDF) — PASS-21 FIX VERIFICATION

Re-reviewed the REBUILT rendered PDF (`/home/ubuntu/from-token-to-fleet-v20260913-full.pdf`,
build D:20260921103831-07'00', 308 pages) by raster-rendering the figure pages with PyMuPDF
and inspecting **placed-page pixel** data (full row/column histograms + tight colour masks,
at 300 and 600 dpi). **Not** the PDF text layer, **not** source PNGs alone. Figure page
numbers re-confirmed for this build: Fig 8.1 = p.110, Fig 7.3 = p.103, Fig 7.2 = p.102,
Fig 7.4 = p.104, Fig 4.1 = p.68, Fig 6.1 = p.84, Fig 6.2 = p.86, Fig 10.1 = p.130,
Fig 10.2 = p.135, Fig 12.1 = p.156.

> Method note (same lesson as prior passes): low-zoom full-page vision repeatedly over-reports
> the OLD symptoms. This pass vision flagged Fig 8.1 "fastest · smallest" as "clipped by the
> registers box border" — re-checked against the authoritative pixel data, the sub-label
> bottom sits **26 px (6.2 pt)** above the registers box bottom edge, i.e. fully contained.
> Pixel verdicts below.

---

## RESULT SUMMARY

- **P21-1 (Fig 10.1 pill-to-card clearance) — LANDED.** Placed-page pixel measurement at 600 dpi:
  top band ("Expert parallel (all-to-all)") pill bottom ≈ row 1881 vs GPU A card top border ≈
  row 1983 → gap = **102 px = 12.24 pt**; pipeline band pill bottom ≈ row 3982 vs PP stage-1
  card top border ≈ row 4084 → gap = **102 px = 12.24 pt**. Both ≥ 10 pt. The pill also now
  sits clear of the dashed top border (top band pill top ≈ row 1818 vs dash bottom ≈ row 1721,
  **97 px = 11.6 pt**; pipeline pill top ≈ 3920 vs dash bottom ≈ 3822, 98 px = 11.76 pt),
  so the band title floats in its own whitespace between an unbroken dashed edge above and the
  first card below.
- **P21-2 (Fig 12.1 note separation) — LANDED.** Grey note ("decode pool:" / "bandwidth-bound")
  glyphs at *y 336.5–360, x 331–408* pt; red annotation ("(c) excluded at" / "quality gate")
  at *y 304.7–323.9, x 446–519.7* pt; panel-2 black title glyphs at *y 292–306, x 92–461.6* pt.
  Grey note is **30 pt below** the title bottom (clear). Red annotation sits just below the
  title's baseline (its lowest glyph row 302.6 pt vs red top 304.7 pt → **2.1 pt** vertical
  clearance, and 0 black/red glyph-column collisions) and to the right of the axis spine
  (446 vs spine 425.6 pt), in the right margin. Grey note and red annotation no longer
  overprint the title or each other.
- **PASS-19 Fig 10.1 dashed-border fix HOLDS (no regression from the pill move).** Top band
  dash row 1719–1721 runs UNBROKEN (86 dash segments, uniform gaps 14–15 px, max 15 px,
  **16 segments present across the title x-range 1027–1664**); pipeline band dash row
  3820–3822 likewise unbroken (76 segments, uniform 14–15 px gaps, **14 segments across the
  pill x-range 1032–1567**).
- **All other named prior ch1–14 figure fixes HOLD (no regression):** Fig 10.2 ("experts
  6-10" final "0" visible, children non-overlapping, "PP/CP · Parallel" terminals inside),
  Fig 8.1 (labels inside boxes; "fastest · smallest" sub-label bottom 6.2 pt above the
  registers box edge — fully contained), Fig 7.3 (~1120 / ~165 / ~60 GB all legible),
  Fig 6.2 ("mean = 0.85s"), plus Fig 7.2, 7.4, 4.1, 6.1 (unchanged figure files; prior
  holdings re-confirmed). Fig 20.1 "~28 hosts" and Fig A.4 arrow-up (outside ch1–14; not
  touched by the PASS-21 build — hold per PASS-18/20 confirmation).
- No CRITICAL / MAJOR / MODERATE / MINOR findings.

---

## A. PASS-21 FIX VERIFICATION (placed-page pixel)

### A1. P21-1 — Fig 10.1 pill-to-card clearance (PDF p.130)

| Check (≥10 pt intended) | Result | Evidence (placed raster, 600 dpi) |
|---|---|---|
| Top band title pill clear of GPU A card | **PASS** | Pill bottom row 1881; GPU A card top border row 1983 → **102 px = 12.24 pt**. |
| Pipeline band title pill clear of PP stage-1 card | **PASS** | Pill bottom row 3982; PP stage-1 card top border row 4084 → **102 px = 12.24 pt**. |
| Pill clear of dashed top border (moved label) | **PASS** | Top: pill top 1818 vs dash bottom 1721 → 97 px = 11.6 pt. Pipeline: 3920 vs 3822 → 98 px = 11.76 pt. |

**Verdict:** P21-1 is **CLOSED**. Both band-title pills now have a ~12.2 pt visible gap to
their first child card (≥10 pt) and an ~11.6–11.8 pt gap to the dashed border above.

### A2. P21-2 — Fig 12.1 note separation (PDF p.156)

| Check | Result | Evidence (placed raster, 600 dpi → pt) |
|---|---|---|
| Grey note vs red annotation separated | **PASS** | Grey *x 331–408*, red *x 446–519.7* — disjoint x-ranges; disjoint rows. |
| Grey note clear of black title | **PASS** | Grey y 336.5–360 vs title y 292–306 → **30 pt** below. |
| Red annotation clear of black title | **PASS** | Red y 304.7–323.9; title lowest glyph row 302.6 → 2.1 pt clearance, 0 glyph-column collisions; red also right of axis spine (446 vs 425.6 pt). |

**Verdict:** P21-2 is **CLOSED**. Grey and red notes are now both clear of the panel-2 title
and of each other. (Red sits ~2 pt below the title baseline — close but non-colliding; no
overprint.)

---

## B. PRIOR-FIX REGRESSION CHECK (rendered; all HOLD)

| Prior ID | Figure (p.) | PASS-22 status | Evidence |
|---|---|---|---|
| P19-1 / P18-2 | Fig 10.1 unbroken dashed border (p.130) | **HOLDS** | Dash rows 1719–1721 & 3820–3822; 86/76 segments, max gap 15 px, present across title x-range. |
| P18-1 | Fig 10.2 "experts 6-10" + non-overlap (p.135) | **HOLDS** | Full "experts 6-10" incl. final "0"; children separated; terminals inside. |
| P17-1 | Fig 8.1 ladder (p.110) | **HOLDS** | "fastest · smallest" bottom 26 px = 6.2 pt above registers box bottom (fully contained). |
| P17-3 | Fig 7.3 memory floor (p.103) | **HOLDS** | ~1120 / ~165 / ~60 GB all legible in raster. |
| P17-7 | Fig 6.2 mean (p.86) | **HOLDS** | "mean = 0.85s" legible. |
| P17-4 | Fig 4.1 six dimensions (p.68) | **HOLDS** | Six labels legible, unclipped. |
| P17-5 | Fig 6.1 chain legend (p.84) | **HOLDS** | Direction legend present, legible. |
| P17-9 | Fig 7.2 KV vs context (p.102) | **HOLDS** | Axes/labels/call-outs legible, non-overlapping. |
| P17-8 | Fig 7.4 host pool (p.104) | **HOLDS** | All annotations legible, unclipped. |
| P18 | Fig 20.1 "~28 hosts" | **HOLDS** | (outside ch1–14; not touched) |
| P18 | Fig A.4 arrow-up | **HOLDS** | (not touched) |

---

## C. FINDINGS

No NEW findings. All PASS-21 fix-verification items are closed, all named prior ch1–14
figure fixes hold with no regression, and no new defect, legibility problem, numerical
inconsistency, or cross-chapter contradiction surfaced in the verified ch1–14 figure set.

---

## D. FINAL VERDICT

- **PASS-21 Fig 10.1 pill-to-card clearance (P21-1): LANDED** (~12.24 pt both bands, ≥10 pt
  target met; pill also clear of unbroken dashed top border). Closed.
- **PASS-21 Fig 12.1 note separation (P21-2): LANDED** (grey note 30 pt below title; red note
  2.1 pt below title + right of axis, no glyph collisions; grey/red mutually separated). Closed.
- **PASS-19 Fig 10.1 unbroken dashed border HOLDS** (re-confirmed; no regression from the
  pill shift).
- **All named prior ch1–14 figure fixes hold** (Fig 10.2, 8.1, 7.3, 7.2, 7.4, 4.1, 6.1, 6.2,
  plus 20.1 and A.4 outside ch1–14) — no regression.
- **No CRITICAL / MAJOR / MODERATE / MINOR findings.** The ch1–14 figure-legibility
  convergence tail is clean. [Illustrative] figure legibility items previously open in
  ch1–14 are all resolved on the placed-page raster.
