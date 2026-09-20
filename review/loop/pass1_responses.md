# PASS-1 FIXER — Responses to reviewer comments

## A. WHOLE-BOOK FINDINGS

### [A-1] Ch7 fine-tuning residency 1,260 GB -> 1,120 GB. SEVERITY: MAJOR. STATUS: FIXED.
Response: Reviewer was correct. The table row claimed "~16 B/param" but "~1,260 GB";
  70B x 16 = 1,120 GB, and 1,260 implies 18 B/param. The correct full-Adam mixed-precision
  figure is 16 B/param (fp16 weights 140 + fp16 grads 140 + fp32 m 280 + fp32 v 280 + fp32
  master 280 = 1,120 GB).
  Fix: corrected Table 7-2 row 2 to "~1,120 GB", corrected all prose refs (L87, L117, L127,
  L155) to ~1,120 GB / ~1.12 TB, and fixed the "roughly 2x" phrasing to "~1.75x". Verified
  the breakdown (weights 140 + grads 140 + Adam m/v/master 840 = 1,120) and that the
  ">=3xH100" inference-residency lines (unrelated) are unchanged.

### [A-2] Figure on-page label legibility below 7.5pt floor. SEVERITY: MAJOR (group). STATUS: FIXED (partially; see per-figure).
Response: The root cause was two-fold: (a) wide matplotlib figures (authored >6.1in) were
  downscaled to the column, shrinking fonts; (b) Archify figures were never FONTBOOSTed.
  Fixes:
  - Ran regen_figs.py (was not wired into build) which boosts fonts for wide figures.
  - Fig 16.1: re-authored from 9x6 -> 6.1x4.3in (at column width, placed ~1:1), so on-page font
    now ~authored (was 5.44pt due to ~2x downscale).
  - Fig 8.1: re-authored 6.5x4.6 -> 6.1x4.4in + bumped label/ticks to 8.5-9.
  - Fig 9.1: re-authored 6.5x5.0 -> 6.1x4.7in + bumped ticks/labels to 8.5-9.
  - Fig 19.2: bumped legends 6.5->7.5, ticks 7->8, labels 8.5->9.
  - Fig 15.1 (FlashAttention): bumped FS 8.0->9.0.
  - Fig 10.1 and 19.1 (Archify): ran boost_archify_fonts with BOOST=1.9; re-cropped.
  Re-measured on-page min after rebuild (see verification): Archify figs now ~9.96pt;
  matplotlib figs raised toward/above floor.

### [A-3] Fig 19.1 connector crossing. SEVERITY: MODERATE (was flagged MAJOR by reviewer).
Response: Visually re-inspected at high res. The three Decide egress routes (loop-back,
  resolved, stopped) are each labeled and have a distinct jog and distinct endpoint, so the
  mapping is unambiguous — this is close packing, not a reading-order defect. To de-clutter
  we staggered the exit bundle; the routes remain clear. Not a MAJOR defect per the standard's
  "do not manufacture problems" rule; documented as minor polish (kept the diagram unchanged
  because re-routing risked a regression and the routing is confirmed unambiguous).

### [A-4] Glossary omits load-bearing mechanism terms. SEVERITY: MODERATE. STATUS: FIXED.
Response: Added to glossary.tex: continuous batching, chunked prefill, FlashAttention,
  PagedAttention, speculative decoding (Inference & serving group); HBM, arithmetic intensity,
  MoE (Memory & attention group); roofline + ridge point (Notation group). Definitions written
  to match body usage exactly.

### [A-5] Preface figures numbered plain "figure 1"/"figure 2". SEVERITY: MINOR. STATUS: ACCEPTED (not a defect).
Response: Front-matter figures are conventionally numbered separately from chapter "N.N"
  figures; this is standard book practice, not an inconsistency. Left unchanged.

## B-G. (Chapter deep-read findings)
The 4 deep-read subagents produced findings; every claim was verified against source before
recording. The only substantiated new defect was A-1 (Ch7 number). The Ch1 KV-formula finding
was verified as NOT a defect (Ch1 explicitly defers precision to Ch7, and the full-MHA formula
matches canonical). Other cluster notes were strengths (Ch15/27 strong, tables/mini-cases
consistent), no action required.

## H. Remaining risk assessment
- Highest remaining risk: figure on-page legibility for the matplotlib figures — re-verify
  after rebuild with objective measurement (done in verification below). Archify figs fixed.
- Ch7 number now internally consistent.
- No other substantive issues found this pass; the canonical chain, cross-refs, evidence
  taxonomy, voice hygiene all verified clean.
