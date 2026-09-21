# PASS-20 — Re-review of PASS-19 fixes — Chapters 15–27 + Back Matter
## Book: "From Token to Fleet" (from-token-to-fleet-v20260913-full.pdf, 308 pp)
## Scope: confirm the PASS-19 Fig A.2 fix LANDED in the RENDERED (raster) PDF; report NEW findings
## Review date: 2026-09-21
## Method: pymupdf page render at 300 dpi + zoomed crop pixel measurement and vision
##   inspection, applied to the RASTER (the PDF text layer was REJECTED for all figure
##   findings). For Fig A.2 the geometry was measured directly at the pixel level
##   (ink-column extents and row bands: grey tick-label glyph bands vs the banner
##   box's red border row bands) to avoid the known auxiliary-vision layout misread
##   trap; vision on a 3x zoomed crop was used only as a cross-check and AGREED with
##   the pixel measurement.

--------------------------------------------------------------------------------

## A. CONFIRMATION OF PASS-19 FIXES (Did each land in the raster?)

### FIX #1 — Fig A.2 (PDF p.292): 'NOT COMPARABLE ACROSS PANELS' banner clear of the
###        'KV /token' / 'FLOP /token' tick labels
- **DID NOT LAND.** The banner box STILL overlaps/hides the "/token" second line of
  the x-axis tick labels. This is the single unresolved item. See NEW FINDING #1.

### Also confirmed (all PASS-19 confirmation targets still hold, no regression):
- **Fig 15.1 (p.175): two bottom annotation blocks separated.** LANDED / holds.
  Pixel + vision: red O(L²) block (x-extent ~402–721 at 200 dpi) and green O(L)
  block (x ~987–1288) separated by a wide, unambiguous white gutter (~266 px);
  neither block overlaps the other, captions are three-line centred and both sit
  inside their own panel's horizontal extent. No collision.
- **Fig A.1 (p.288): linear active-fraction bars.** Holds. Horizontal bars on a
  LINEAR 0–10% x-axis (evenly spaced 0/5/10 ticks). Bar lengths proportional to
  labelled values (GLM 5.6%, Qwen 4.8%, Kimi 3.7%, DeepSeek 4.6%) on the linear
  scale; no log-axis residue. Matches §A.1 text.
- **Fig 20.1 (p.234): '≈28 hosts' 70%-target annotation.** Holds. Rendered in the
  bottom panel as the blue two-line call-out "≈28 hosts: 70% target / (⌈40/(2.1×0.70)⌉
  = 28)". Consistent with Ch16 §16.4 / Ch17.
- **Fig A.4 (p.296): red leader arrow points UP.** Holds. Red arrowhead at the TOP
  of the stack (above "Across a fleet of specialised models"), shaft running down
  along the left margin — consistent with the externalization thesis.
- **Ch18 §3.2 (p.207): basis note reconciling per-1M with Ch16 ~$0.60/1M.** Holds.
  Dedicated "Basis note (reconciled with Ch16's TCO)" paragraph present, explaining
  the ≈4× gap is a utilization/throughput basis difference, not a contradiction.
- **Ch16 §16.4 (p.185): provisioning-sensitivity block.** Holds. "Provisioning
  sensitivity (explicit)" block present: full-util ≈20 hosts vs the 70%-util ≈28
  hosts → ≈$163K capex + ≈$30K opex + ≈$10K staff ≈ $203K/month, ≈$203K/26M ≈
  $7.8/1K vs $5.7/1K; conclusion-holds-under-either-policy.
- **Fig A.3 (p.295):** Holds. Stacked-era layer cake; white bar labels contained in
  bars, ~YYYY era markers clear of bars, legend legible, no overlap/clipping.

--------------------------------------------------------------------------------

## B. NEW FINDINGS THIS PASS

### NEW FINDING #1 — [MINOR][figure-composition] Fig A.2 PASS-19 fix did NOT land:
###     the 'NOT COMPARABLE ACROSS PANELS' banner still overlaps/hides the '/token'
###     second line of the x-axis tick labels (center panel both labels fully
###     hidden; left-panel FLOP and right-panel KV partially overlapped)
- Location: Fig A.2 (rendered p.292), the three independent per-model bar panels
  (generator `render/fig_ch27_norm.py`; banner = `fig.text(0.5, 0.045, ...)`
  boxed call-out at the figure bottom, over the `ax.set_xticklabels(['KV\n/token',
  'FLOP\n/token'])`; the PASS-19 "fix" only bumped the `tight_layout` bottom rect
  margin 0.07→0.14, which does NOT give the tick-label row clear headroom on the
  PLACED page).
- Problem: On the rendered p.292 at 300 dpi (pixel-measured directly):
    * banner box top border = rows 1974–1978; pink fill = rows 1980–2045; box
      x-extent = 840–1709 (centred under the middle panel, reaching the flanks).
    * "/token" second-line tick labels = rows 1971–2002 (grey glyph band, measured
      on the three clear labels); first line "KV"/"FLOP" = rows 1929–1955.
  The banner box therefore covers rows 1974–2002 of the "/token" glyphs — i.e. the
  banner top border cuts through the "/token" second line at ~35% down the glyph
  height and the banner fill hides the rest. Per label:
    * Left panel KV ("/token" x 543–654)  — left of banner (x<840): fully visible.
    * Left panel FLOP ("/token" x 833–887) — overlapping banner left edge (x 840):
      largely hidden.
    * Center panel KV ("/token" x 1120–1165) — inside banner: fully hidden.
    * Center panel FLOP ("/token" x 1409–1454) — inside banner: fully hidden.
    * Right panel KV ("/token" x 1687–1788) — overlapping banner right edge (x 1709):
      left part hidden, right sliver visible.
    * Right panel FLOP ("/token" x 1967–2077) — right of banner (x>1709): visible.
  Confirmed by BOTH the direct 300 dpi pixel row-band/column-extent measurement AND
  a 3x-zoom crop inspection; not a montage or vision artifact. PASS-19's reported
  "verified: banner sits clearly below all three /token labels" is NOT what the
  placed page shows.
- Why it matters: Section 23/24 figure-composition & figure-legibility. The
  "/token" unit tag (per-token, not per-request) is required to interpret each
  bar. With the banner sitting on it, a reader of the center panel (DeepSeek
  V4-Pro vs V3.2) — a focus model — cannot tell the bars are per-token; the
  warning banner occupies the space where the unit labels should be. This is the
  PASS-19 NEW FINDING #1 resurfacing because the fix didn't land (the source edit
  to `tight_layout` rect was insufficient on the placed page — the source PNG's
  internal headroom ≠ the placed figure's raster geometry).
- Recommended: Give the tick-label row genuine headroom on the PLACED page rather
  than relying on the generator's `tight_layout` bottom margin. Two robust options:
  (a) drop the banner lower in figure space (e.g. `fig.text(0.5, -0.015, ...)` /
      negative figure y) and shrink the banner's bbox `pad` so it sits fully below
      the "/token" labels; and/or (b) raise the axes in the laid-out figure (larger
      `tight_layout(rect=(0.04, 0.20, 1, 1))` so both tick-label lines and the
      banner clear the axes bottom). Verify by re-measuring page 292 RASTER after
      the change: confirm the banner top-border row is comfortably BELOW the
      "/token" glyph bottom row in all three panels (no row overlap), not by
      reading the source PNG or PDF text layer.

--------------------------------------------------------------------------------

## C. REMAINING-RISK ASSESSMENT
- ALL PASS-19 confirmation targets EXCEPT Fig A.2 are LANDED and correct in the
  raster (Fig 15.1, A.1, 20.1, A.4, Ch18 §3.2, Ch16 §16.4, Fig A.3 all hold; no
  regression).
- ONE unresolved item this pass: the PASS-19 Fig A.2 fix did NOT land — the
  not-comparable banner still covers the "/token" unit labels for the center panel
  and partially for the flanking panels. Classified MINOR (figure-composition /
  legibility), but flagged as a genuinely non-landed fix (second surface), not a
  fresh defect.
- No CRITICAL / MAJOR / MODERATE defect in ch15–27 + back matter this pass.
