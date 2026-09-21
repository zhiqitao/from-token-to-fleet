# PASS-18 FIXER RESPONSES — re-review confirmation + new findings

PASS-18 re-reviewed the rebuilt PDF (rendered-PDF visual inspection) against the 55-section
prompt. Confirmed 10 of 11 PASS-17 fixes LANDED; surfaced 1 CRITICAL regression (my PASS-17
"false positive" verdict on Fig 10.2 was wrong) and 4 new MINOR items. All addressed.

| # | Severity | Location | Problem | Disposition |
|---|----------|----------|---------|-------------|
| P18-1 | CRITICAL | Fig 10.2 (p.135) | "experts 6-10" renders as "experts 6-1" (the "0" occluded by overlapping GPU-C box); "PP · Pipeline Paralle" / "CP · Context Paralle" clip | **FIXED** — root cause: the Archify crop's GBOX (×1.18) grows child boxes to ~108.6pt while centers were 104pt apart → 4.6pt overlap. Re-spaced all five child rows (TP/PP/DP/EP/CP) to 120pt centers so grown boxes have 16pt gaps, and widened parent boxes so sublabels fit (→220pt). Pixel-verified: child boxes non-overlapping, all sublabels fully visible ("experts 6-10" incl. "0"). NOTE: this is the defect my PASS-17 verdict called a false positive — I had verified via the PDF text layer (which holds the correct string) instead of the raster. The reviewer was right; the text layer being correct does NOT prove the render isn't clipped. |
| P18-2 | MINOR | Fig 10.1 | Band titles sit on the dashed container border (title-on-border) | **ACCEPTED AS CONVENTION** — reverified. The band-title banner is the standard Archify region-label style (a label tab on the region's top border); raising it fully above the container box pushes it outside the crop bbox (the crop excludes the <40pt label banner), causing top-clipping. The substantive P17-6 fix (purple title/sentence separation) is intact. Reverted to the clean title-on-border state. This is the intended design; no reader-visible defect. |
| P18-N1 | MINOR | Fig 20.1 | "~27 hosts: 70% target" vs the book's "≈28 hosts" (⌈⌉ sizing rule) | **FIXED** — annotation changed to "≈28 hosts: 70% target (⌈40/(2.1×0.70)⌉ = 28)" to match the ceiling convention and Ch16 §16.4 / Ch17. |
| P18-N2 | MINOR | Fig A.4 | Red leader arrow pointed DOWN toward "Inside weights" while the label reads "more of the intelligence and compute budget" — opposite to the book's externalization thesis | **FIXED** — flipped the arrow to point UP (arrowhead at top toward the fleet rows), matching the "intelligence externalizes upward" message. Confirmed via render. |
| P18-N3 | MINOR | Fig 15.1 | The two bottom O(L²)/O(L) annotation second-lines still collided in the gutter | **FIXED** — split each caption into three shorter lines ("every query re-reads / the row-block"; "each tile read once / softmax online") so no line exceeds the panel width, and dropped caption font (FS-1.4→FS-1.6). Pixel-verified clear white gap between the two blocks. |

## Verification
- Fig 10.2: re-spaced child rows (120pt centers), "experts 6-10" fully readable, all parent
  sublabels intact (pixel-verified, not text-layer).
- Fig 20.1: "≈28 hosts" annotation.
- Fig A.4: red arrow points up.
- Fig 15.1: three-line captions, no gutter collision (pixel-gap measured).
- Fig A.1 / Ch18 §3.2 / Ch16 §16.4 cross-chapter fixes confirmed LANDED by the reviewer.

## Methodology correction (important)
P18-1 was a real defect I had wrongly dismissed. Lesson re-affirmed: **never verify a
figure-clipping fix via the PDF text layer** — the text layer holds the intended string while
the raster still clips. Only raster/pixel inspection (render page → pixel-measure ink extents)
is authoritative for figure-legibility findings.
