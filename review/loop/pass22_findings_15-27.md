# PASS-22 — Re-review of PASS-20/21 fixes — Chapters 15–27 + Back Matter
## Book: "From Token to Fleet" (from-token-to-fleet-v20260913-full.pdf, 308 pp, rebuilt 2026-09-21 10:40)
## Scope: confirm the PASS-20/21 Fig A.2 GridSpec fix LANDED in the RENDERED (raster) PDF;
##   confirm Fig 15.1 / A.1 / A.3 / A.4 / 20.1 / Ch18 §3.2 / Ch16 §16.4 still hold; report NEW findings
## Review date: 2026-09-21  PASS walk: #22
## Method: pymupdf page render at 300 dpi (RGB, DeviceRGB n=3) + FULL row-band and column-extent
##   ink/color pixel histograms measured directly on the PLACED-page RASTER. The PDF text layer was
##   used only to LOCATE pages/glyph bands as a sanity cross-check and REJECTED as the basis for any
##   figure finding; source-PNG-only geometry was NOT used (all measurements are on the placed page).
##   A 2x-region crop was inspected visually as a cross-check and AGREED with the pixel measurement
##   on every confirmed item. NOTE: an initial render batch was miscounted (0-based vs 1-based page
##   index off-by-one) and was discarded; all numbers below were re-measured from the CORRECT pages.

--------------------------------------------------------------------------------

## A. CONFIRMATION OF PASS-20/21 FIXES (Did each land in the raster?)

### FIX #1 — Fig A.2 (PDF p.292): 'NOT COMPARABLE ACROSS PANELS' banner in its own
###        GridSpec bottom band, clear of the 'KV /token' / 'FLOP /token' tick labels
- **LANDED — CONFIRMED.** Measured directly on the placed-page raster at 300 dpi (page 292):
    * All six "/token" second-line tick-label glyphs occupy rows 1953–1982 (dark-ink glyph band,
      anti-alias tail to row 1983); the "KV"/"FLOP" first lines occupy rows 1911–1936.
    * Banner box: red top border first row = **2086**; pink fill + red border band rows 2086–2162;
      box x-extent **848–1720** (centred under the three panels; saturates at 149 / is coloured).
    * **Gap between the "/token" glyph bottom (1983) and the banner box top border (2086) =
      103 px** at 300 dpi — comfortably ≥ the required 50 px clear gap. The row band 1984–2084 is
      completely blank (no non-white ink) so the banner sits in its OWN band, entirely below all
      six tick-label rows. No row overlap between the banner and any "/token" label.
    * All six "/token" labels present and intact / fully readable; per-label x-extents measured
      479–591, 795–907, 1070–1182, 1386–1499, 1662–1774, 1978–2090. The banner is vertically below
      all of them (no vertical overlap) and no label is clipped at the page/figure edge (rightmost
      label ends at x=2090 on a 2550-wide page).
    * Banner colour preserved in the placed raster: fill = (253,236,234) light pink, border =
      (192,57,43) red (matching prior passes' red-border/pink-fill banner).
    * Visual cross-check of a 2x zoom of the bottom region AGREED: bars → x-axis → "KV"/"FLOP"
      first line → "/token" second line → clear white gap → red-bordered pink "NOT COMPARABLE
      ACROSS PANELS" banner in its own band → white gap → sub-note ('each bar is a model's
      reduction relative to its OWN stated predecessor/reference…') → figure caption. No overlap.
- PASS-20's unresolved item (PASS-20 NEW FINDING #1) remains RESOLVED — the fix landed and holds.

### Also confirmed (all PASS-20/21 confirmation targets still hold, no regression):
- **Fig 15.1 (p.175):** Holds. Two bottom annotation blocks separated by a clear white gutter:
  left red "O(L²) HBM traffic: every query re-reads the row-block" and right green "O(L) HBM
  traffic: each tile read once, softmax online", each inside its own grey panel, no overlap.
- **Fig 20.1 (p.234):** Holds. Blue "≈28 hosts: 70% target" call-out present in the bottom panel,
  anchored to the ρ=0.70 reference line near Host≈28; readable and not overlapped by the orange
  per-host-utilization curve or the red "~20 hosts: saturation" call-out.
- **Fig A.1 (p.288):** Holds. Four horizontal bars (GLM 5.6%, Qwen 4.8%, Kimi 3.7%, DeepSeek 4.6%)
  on a LINEAR 0–10% x-axis with evenly spaced 0/5/10 ticks and grid lines; bar lengths proportional
  to labels; all four % labels clear at bar ends, no overlap; no log-axis residue.
- **Fig A.3 (p.295):** Holds. Stacked-era "layer cake": white bar labels contained in bars, "~YYYY"
  era markers in white space clear of the bars, three-entry legend legible, no overlap/clipping.
- **Fig A.4 (p.296):** Holds. Red leader arrow points UP (arrowhead at the top of the stack,
  above "Across a fleet of specialised models"), shaft running down along the left margin.
- **Ch18 §3.2 (p.207):** Holds. "Basis note (reconciled with Ch16's TCO)" paragraph present,
  explaining the ≈4× gap ($2.50/1M vs ~$0.60/1M) is a per-model-nominal vs fleet-amortized
  utilization/throughput basis difference, not a contradiction.
- **Ch16 §16.4 (p.185):** Holds. "Provisioning sensitivity (explicit)" block present: full-util
  ≈20 hosts vs the 70%-util ≈28 hosts → ≈$163K capex + ≈$30K opex + ≈$10K staff ≈ $203K/month,
  per-request ≈$203K/26M ≈ $7.8/1K vs $5.7/1K; conclusion-holds-under-either-policy.

--------------------------------------------------------------------------------

## B. NEW FINDINGS THIS PASS
- **NO NEW FINDINGS.** The only content change in this build relative to PASS-21 was the Fig A.2
  rebuild, which is verified LANDED and compositionally clean (own-band banner, 103 px clear gap,
  all six "/token" labels fully readable, banner colour preserved, caption in place). All
  previously-flagged figure/prose items hold. No CRITICAL / MAJOR / MODERATE / MINOR defect was
  found in ch15–27 + back matter this pass.

--------------------------------------------------------------------------------

## C. REMAINING-RISK ASSESSMENT
- ALL PASS-20/21 confirmation targets are LANDED and correct in the raster (Fig A.2, 15.1, 20.1,
  A.1, A.3, A.4, Ch18 §3.2, Ch16 §16.4). No regression.
- The long-running Fig A.2 banner-overlap defect is closed for a second consecutive pass and the
  fix is stable. Guardrail: any future figure-space edit must be re-verified against the placed-page
  RASTER (this pass's 300 dpi row-band/column-extent pixel measurement + vision cross-check), not
  the generator's tight_layout headroom or the source PNG.
