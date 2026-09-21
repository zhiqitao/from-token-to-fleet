# PASS-19 — Re-review of PASS-18 fixes — Chapters 15–27 + Back Matter
## Book: "From Token to Fleet" (from-token-to-fleet-v20260913-full.pdf, 308 pp)
## Scope: confirm PASS-18 fixes landed in the RENDERED (raster) PDF; report NEW findings
## Review date: 2026-09-21
## Method: pymupdf page render at 140–400 dpi + zoomed crop pixel measurement and
##   vision inspection, applied to the RASTER (rejected the PDF text layer for all
##   figure findings). For Fig 15.1 / Fig A.2 / Fig A.4, pixel geometry measured
##   directly (ink-column extents, banner-box row band vs tick-label row band) to
##   avoid the known auxiliary-vision layout misread trap; vision used only as a
##   cross-check after the pixel measurement.

--------------------------------------------------------------------------------

## A. CONFIRMATION OF PASS-18 FIXES (Did each land in the raster?)

### FIX #1 — Fig 15.1 (p.175): TWO BOTTOM ANNOTATION BLOCKS SEPARATED (no gutter collision)
- **LANDED.** Verified on rendered p.175 (PASS-18 called this only PARTIALLY landed).
  The generator (fig_ch15_flashattn.py) now emits THREE-LINE centred captions
  instead of two long lines. Pixel-measured at 200 dpi (page render):
    RED annotation lines at rows 1301–1397, x-extent 402–721
    GREEN annotation lines at rows 1301–1397, x-extent 987–1288
  Horizontal GAP between the red block right edge (x≈721) and the green block
  left edge (x≈987) = **≈266 px (~96 pt)** — a wide, unmistakable gutter. The
  caption line-splitting fix fully resolves the PASS-17/PASS-18 residual
  "colliding-in-the-gutter" defect. RED ends "the row-block", GREEN starts
  "each tile read once" — both clearly inside their own panel's horizontal
  extent. DONE. (The residual NEW FINDING #3 from PASS-18 is now closed.)

### FIX #2 — Fig A.1 (p.288): LINEAR ACTIVE-FRACTION BARS
- **LANDED.** Verified on rendered p.288. Horizontal bar chart on a LINEAR x-axis
  labelled "Active parameters as % of total", 0–10% linear (ticks 0/5/10). Four
  single-orange bars:
    GLM-5.3-Flash          5.6%   (320B total / 18B active)
    Qwen3.8-Flash-Next     4.8%   (125B total / 6B active)
    Kimi K3                3.7%   (2800B total / 104B active)
    DeepSeek V4-Pro/Flash  4.6%   (284B total / 13B active)
  Bar lengths proportional on a linear scale; values match §A.1 text. The
  log-axis bar-length defect is fully resolved. DONE.

### FIX #3 — Ch18 §3.2 (p.207): BASIS NOTE RECONCILING PER-1M WITH Ch16 ~$0.60/1M
- **LANDED.** Verified on rendered p.207. Directly beneath the 70B dense/8-bit/
  MoE/GGUF cost table is a dedicated "Basis note (reconciled with Ch16's TCO)"
  paragraph. It distinguishes the per-model nominal per-1M routing rates from the
  fleet-amortized ~$0.60/1M in Ch16 §16.4, and states the ≈4× gap is a
  utilization/throughput basis difference, not a contradiction. DONE.

### FIX #4 — Ch16 §16.4 (p.185): PROVISIONING-SENSITIVITY BLOCK
- **LANDED.** Verified on rendered p.185. "Provisioning sensitivity (explicit)"
  block present: full-utilization assumption (≈20 hosts, provisioned exactly at
  the 40 rps peak), plus the 70%-utilization scenario (≈28 hosts → ≈$163K capex
  + ≈$30K opex + ≈$10K staff ≈ $203K/month, per-request ≈$203K/26M ≈ $7.8/1K vs
  the full-util $5.7/1K), and the conclusion-holds-under-either-policy statement.
  DONE.

### Also confirmed (the two PASS-18 NEW-finding fixes rebuilt in this PDF):
- **Fig 20.1 (p.234): "~27 hosts" → "≈28 hosts".** LANDED. The blue 70%-target
  annotation now reads "≈28 hosts: 70% target (⌈40/(2.1×0.70)⌉ = 28)" with the
  ceiling convention applied. Matches Ch16 §16.4 / Ch17.
- **Fig A.4 (p.296): red leader arrow now points UP.** LANDED. Verified on
  rendered p.296 — the red arrowhead is at the TOP of the stack (above "Across a
  fleet of specialised models"), shaft running down toward "Inside weights",
  consistent with the externalization thesis. PASS-18 NEW FINDING #2 resolved.

--------------------------------------------------------------------------------

## B. NEW FINDINGS THIS PASS

### NEW FINDING #1 — [MINOR][figure-composition] Fig A.2 the "NOT COMPARABLE
###     ACROSS PANELS" banner's top edge cuts through the "/token" second line of
###     the x-axis tick labels in panels 2 and 3
- Location: Fig A.2 (rendered p.292), the three independent per-model bar panels
  (generator `render/fig_ch27_norm.py` → render/latex/figures/fig-27-2704.pdf;
  the banner `fig.text(0.5, 0.045, ...)` boxed call-out placed at the figure
  bottom, overlapping the `ax.set_xticklabels(['KV\n/token','FLOP\n/token'])`).
- Problem: On the rendered page (pixel-measured at 400 dpi), the banner's pink
  fill box spans rows 2640–2727 and its red border top edge is at ~row 2635,
  while the grey two-line tick-label text occupies rows ~2575–2665 (first line
  "KV"/"FLOP" at 2575–2605, second line "/token" at ~2630–2665). The banner box
  therefore sits ON TOP of the second line in the panels it spans: for the middle
  panel the "/token" line is essentially hidden under the banner, and for the
  right panel the "KV /token" second line is partially obscured. Only the
  leftmost panel's labels remain fully visible (it sits clear of the banner's
  left edge). Confirmed by zoomed crop inspection and by two independent pixel
  row-band measurements; not a montage/vision artifact.
- Why it matters: Section 23/24 figure-composition and figure-legibility. The
  banner is intended as a prominent not-comparable warning, but in placing it at
  figure y=0.045 it collides with the axis tick labels it is meant to sit below,
  hiding the unit/category tags ("KV /token", "FLOP /token") that a reader needs
  to interpret each bar. A reader focusing on the middle/right panels sees the
  warning banner where the genre labels should be.
- Recommended: Lower the banner / push the tick-label row up (e.g. place the
  banner at `fig.text(0.5, 0.005, ...)` and drop the panel bottoms via
  `tight_layout(rect=(0.04, 0.09, 1, 1))`), or shorten the banner to one line and
  shrink its padding so it sits cleanly below the axis labels. Re-measure on the
  placed page after the change (source PDF min ≠ placed page).

--------------------------------------------------------------------------------

## C. VERIFIED THIS PASS — NO ISSUE (sweep over the remaining ch15–27 figures)
- Fig A.3 (p.295): stacked-era layer-cake; white labels contained in bars, ~YYYY
  era markers clear of bars, legend clean. Legible. No issue.
- Back matter Sources/Method (p.304): two-axis [PROVENANCE][EPISTEMIC-STATUS]
  taxonomy coherent and consistent. Only previously-noted cosmetic items
  remain (the "[ASSUMP- TION]" hyphenation across a line break, and printed folio
  "284" vs physical page 304 — a back-matter pagination/front-matter offset that
  is intentional in this build, not a defect; the same was noted at PASS-18 and
  is carried forward as known, not a new finding).
- Fig 20.1 (p.234), Fig A.1 (p.288), Fig A.4 (p.296): all confirmed clean and
  consistent with their source generators (see section A).

--------------------------------------------------------------------------------

## D. REMAINING-RISK ASSESSMENT
- All four PASS-18 confirmation targets (+ both PASS-18 NEW-finding fixes:
  Fig 20.1 ≈28 hosts, Fig A.4 arrow-up) are **LANDED** and correct in the raster.
- One NEW MINOR figure-composition finding this pass: Fig A.2 the not-comparable
  banner overlaps the "/token" second line of the x-axis tick labels in panels
  2–3. This is the only item newly surfaced; it is the same class as prior
  figure-composition defects (banner placed too low, colliding with axis labels).
- No CRITICAL / MAJOR / MODERATE defect in ch15–27 + back matter this pass.
