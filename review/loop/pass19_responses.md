# PASS-19 FIXER RESPONSES — re-review confirmation + new findings

PASS-19 re-reviewed the rebuilt PDF with raster/pixel inspection. Confirmed the PASS-18 CRITICAL
fix (Fig 10.2 "experts 6-10" with visible "0", non-overlapping child boxes, full "PP/CP ·
Parallel" terminal "l") LANDED, and all PASS-17 ch1-14 figure fixes hold (no regression).
Two MINOR findings addressed:

| # | Severity | Location | Problem | Disposition |
|---|----------|----------|---------|-------------|
| P19-1 | MINOR | Fig 10.1 | Orange band titles sit ON the dashed container top border (an opaque white tab masks the dashes), so the dashed edge is interrupted | **FIXED** — moved the band-title banners INSIDE their containers just below the top dashed edge (deliver banner y 46→64, title y 60→78; pipeline 516→534, 530→548). The dashed border now runs unbroken across each container top, and the titles are clear of the child boxes below (frame top 60, banner 64–80, child top 90). Verified in render. |
| P19-2 | MINOR | Fig A.2 | "NOT COMPARABLE ACROSS PANELS" banner (at fig y=0.045) overlaps the "/token" second line of the KV/FLOP x-tick labels in panels 2–3 | **FIXED** — increased tight_layout bottom rect margin (0.07→0.14) so the panels sit higher, giving the banner and tick-label rows clear bottom headroom. Verified: banner sits clearly below all three "/token" labels with all second lines fully visible. |

## Verification
- Fig 10.1: dashed borders unbroken above both titles; titles inside containers, clear of child boxes.
- Fig A.2: banner below tick labels; all three "KV /token"/"FLOP /token" pairs fully visible.
- All PASS-18 critical + PASS-17 figure fixes confirmed still holding (no regression).

## Convergence
PASS-19 = 2 MINOR-only findings (both figure-composition), no CRITICAL/MAJOR/MODERATE.
These are the last cosmetic items in a figure-legibility convergence tail that began at
PASS-17. Progress toward the zero-new-comment exit continues.
