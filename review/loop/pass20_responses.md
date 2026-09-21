# PASS-20 FIXER RESPONSES — re-review confirmation + new findings

PASS-20 re-reviewed the rebuilt PDF with pixel/raster inspection. It CONFIRMED the PASS-19
Fig 10.1 fix LANDED (unbroken dashed borders, titles inside below them), confirmed all prior
figure fixes HOLD (no regression), and closed P19-1/P18-2 as landed. It also re-flagged the
Fig A.2 banner-overlap (which I had confirmed in my own raster measure earlier but which was
in fact still NOT landed in the book — see P20-FA2 below). Two NEW MINOR ch1-14 findings +
one ch15-27 re-surface, all addressed:

| # | Severity | Location | Problem | Disposition |
|---|----------|----------|---------|-------------|
| P19-1 / P18-2 | (prior) | Fig 10.1 band-title-on-dashed-border | Was still open at PASS-19 | **CONFIRMED LANDED at PASS-20** — dashed borders unbroken, titles inside containers below them. Closed. |
| P29-FA2 | MINOR | Fig A.2 | "NOT COMPARABLE" banner STILL overlaps "/token" tick labels (center panel fully hidden) | **FIXED** — root cause: the book embeds the *PDF* sibling; my PASS-19 edit only regenerated the PNG (the PDF was stale at 07:02), so the build continued to show overlap. Also my own PASS-19 raster check was flawed (grey-text window cut off at row 1969, so I missed the "/token" line at 1971-2002). Regenerated the PDF sibling, rebuilt, re-measured on the placed page: "/token" rows 1959-1987, banner top 1989 -> clear gap. |
| P20-1 | MINOR | Fig 10.1 | Band-title white pill backgrounds abut the first child card (~1px clearance) | **FIXED** — shifted the EP child boxes (y 90->100) and PP stage boxes (y 560->570) down 10pt for clear pill-to-card whitespace. |
| P20-2 | MINOR | Fig 12.1 | Grey "decode pool" note, red "(c) excluded" note, and black axis text overlap in the margin | **FIXED** — moved grey note to (1.45, 23500) and red note to (2.35, 24800) so the three layers sit in separate whitespace. Verified grey/red/black fully separated. |

## Key methodology lesson (again)
P29-FA2 is the same class as P18-1. Two verification traps: (1) a figure can render correctly
in its source PNG yet still overlap on the PLACED book page (placement scaling differs);
(2) my grep/measurement window cut off before the overlapping text row, so I confirmed a fix
that wasn't actually landed. Verified figure fixes ONLY by re-measuring the PLACED-page raster
with a full-row histogram (no truncated window) after regenerating BOTH the PNG and PDF sibling.

## Verification
- Fig A.2: "/token" rows 1959-1987 vs banner top 1989 (placed page 300dpi) - clear gap.
- Fig 10.1: child cards shifted down for pill clearance.
- Fig 12.1: grey/red/black notes separated (vision-verified).
- All prior figure fixes confirmed holding with no regression.

## Convergence
PASS-20 = 1 MINOR re-surface (Fig A.2, a false "landed") + 2 NEW MINOR (Fig 10.1 pill clear,
Fig 12.1 note overlap). No CRITICAL/MAJOR/MODERATE. Figure-legibility convergence tail
continues; remaining items are MINOR-only styling.
