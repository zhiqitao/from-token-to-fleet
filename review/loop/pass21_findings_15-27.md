# PASS-21 — Re-review of PASS-20 fixes — Chapters 15–27 + Back Matter
## Book: "From Token to Fleet" (from-token-to-fleet-v20260913-full.pdf, 308 pp)
## Scope: confirm the PASS-20 Fig A.2 fix LANDED in the RENDERED (raster) PDF; report NEW findings
## Review date: 2026-09-21
## Method: pymupdf page render at 300 dpi + full row/column ink histograms and color-band
##   pixel measurement (REJECTED the PDF text layer and source-PNG-only geometry for all
##   figure findings). Placed-page RASTER geometry was measured directly. Visual inspection
##   of a 3x region crop used only as a cross-check, and AGREED with the pixel measurement.

--------------------------------------------------------------------------------

## A. CONFIRMATION OF PASS-20 FIXES (Did each land in the raster?)

### FIX #1 — Fig A.2 (PDF p.292): 'NOT COMPARABLE ACROSS PANELS' banner in its own
###        GridSpec bottom band, clear of the 'KV /token' / 'FLOP /token' tick labels
- **LANDED — CONFIRMED.** Measured directly on the placed-page raster at 300 dpi:
    * "/token" second-line tick-label glyphs occupy rows 1952–1983 (grey ink band,
      measured across all three panels; first line "KV"/"FLOP" at rows 1910–1937).
    * Banner box (red border) top border row = 2086; pink fill rows 2103–2135;
      box x-extent 849–1719 (centred under the three panels).
    * **Gap between the "/token" glyph bottom row (1983) and the banner top border
      (2086) = 103 px** at 300 dpi — comfortably ≥ the required 50 px clear gap.
      The entire row range 1984–2085 is blank (no non-white ink except the banner's
      own top edge at 2085), so the banner sits in its OWN band, fully below all
      tick labels — not merely pushed slightly down. No row overlap between the
      banner and any of the six "/token" labels.
    * All six "/token" labels present and intact (per-label x-extents: 478–587,
      795–903, 1070–1178, 1386–1495, 1661–1770, 1978–2086); none is overlapped,
      truncated, or hidden by the banner (the banner is vertically below all of
      them). No label is clipped at the figure/page edge.
    * Visual cross-check of the bottom region confirmed: all six "KV /token" /
      "FLOP /token" labels fully legible, clear white vertical gap between the
      "/token" baselines and the banner top, banner reads "NOT COMPARABLE ACROSS
      PANELS", banner not clipped and not overlapping any axis/bar/label/note.
- PASS-20's single unresolved item (NEW FINDING #1 from that pass) is now RESOLVED.

### Also confirmed (all PASS-20 confirmation targets still hold, no regression):
- **Fig 15.1 (p.175): two bottom annotation blocks separated.** Holds. FlashAttention
  figure: left box with red "O(L²) HBM traffic: every query re-reads the row-block"
  and right box with green "O(L) HBM traffic: each tile read once, softmax online"
  — the two three-line annotation blocks sit in a clear white gutter with no overlap.
- **Fig A.1 (p.288): linear active-fraction bars.** Holds. Horizontal bars on a LINEAR
  0–10% x-axis with evenly spaced 0/5/10 ticks and grid lines; bar lengths
  proportional to labelled values (GLM 5.6%, Qwen 4.8%, Kimi 3.7%, DeepSeek 4.6%);
  no log-axis residue; labels clear at the bar ends, no overlap.
- **Fig A.3 (p.295): stacked-era layer cake.** Holds. Nine stacked era bars with white
  labels contained in bars, "~YYYY" era markers in white space clear of the bars,
  three-entry legend legible, no overlap/clipping. (Caption flags dates as
  approximate era markers, not a rigorous chronology.)
- **Fig A.4 (p.296): red leader arrow points UP.** Holds. Pixel-measured: the red arrow
  tip is at the TOP (row ~806) tapering/widening downward — the arrowhead sits at
  the top of the stack, shaft running down the left margin, consistent with the
  externalization thesis.
- **Fig 20.1 (p.234): '≈28 hosts' 70%-target annotation.** Holds. Bottom panel contains
  the blue two-line call-out "≈28 hosts: 70% target / ([40/(2.1×0.70)] = 28)" pointing
  to the ρ=0.70 reference line near Host≈28; readable, not overlapped by the utilization
  curve or the red saturation annotations.
- **Ch18 §3.2 (p.207): basis note reconciling per-1M with Ch16 ~$0.60/1M.** Holds.
  Dedicated "Basis note (reconciled with Ch16's TCO)" paragraph present, explaining
  the ≈4× gap ($2.50/1M vs ~$0.60/1M) is a utilization/throughput basis difference,
  not a contradiction.
- **Ch16 §16.4 (p.185): provisioning-sensitivity block.** Holds. "Provisioning
  sensitivity (explicit)" block present: full-util ≈20 hosts vs the 70%-util ≈28 hosts →
  ≈$163K capex + ≈$30K opex + ≈$10K staff ≈ $203K/month, ≈$203K/26M ≈ $7.8/1K vs
  $5.7/1K; conclusion-holds-under-either-policy.

--------------------------------------------------------------------------------

## B. NEW FINDINGS THIS PASS
- **NO NEW FINDINGS.** The only content change in this build was the Fig A.2 rebuild,
  which is verified landed and compositionally clean. All previously-flagged figure and
  prose items hold; no CRITICAL / MAJOR / MODERATE / MINOR defect was found in ch15–27
  + back matter this pass.

--------------------------------------------------------------------------------

## C. REMAINING-RISK ASSESSMENT
- ALL PASS-20 confirmation targets are LANDED and correct in the raster (Fig A.2, 15.1,
  A.1, A.3, A.4, 20.1, Ch18 §3.2, Ch16 §16.4). No regression.
- The long-running Fig A.2 "not-comparable banner" overlap defect is now closed. The
  remaining guardrail is to keep any future figure-space edits (e.g. changing the
  banner/axis margins) verified against the placed-page RASTER, not the generator's
  tight_layout headroom — this pass's method (300 dpi row-band/column-extent pixel
  measurement + vision cross-check) is the reliable check for that.
