# ISSUES — publication-quality QA ledger

Severity: P0 (wrong core arithmetic / release blocker) · P1 (important unvalidated claim /
misleading diagram / print-readability) · P2 (prose/pedagogy/layout) · P3 (cosmetic).
State: NEW / REPRODUCED / PATCHED / VERIFIED / CLOSED / BLOCKED / UNVERIFIED.

## Closed from prior reviews (verified in THIS 355-page build)

The 15 prior external reviews (comprehensive → publishing-readiness rounds) produced a wide
P0/P1/P2 register. All were repaired and are verified present in `render/build/
from-token-to-fleet-v20260913.pdf` (see git log: `8c645b2b`, `028adf80`, and predecessors).
Notable confirmed closures:

| id | severity | claim | state |
|---|---|---|---|
| P0-01 (r15) | P0 | Ch4 Table 4-1 traffic = scenario inputs, NOT Little's Law from active users | CLOSED/VERIFIED |
| P0-02 (r15) | P0 | Self-host per-1M = $0.301932 / $9.259259 / $0.292398 (not $0.030/$0.93) | CLOSED/VERIFIED |
| P0-03 (r15) | P0 | Editor 'Note to the editor' instruction removed (reader-facing note added) | CLOSED/VERIFIED |
| P0-01 (r13,r14) | P0 | FP8 KV = 1.31 MB/token (raw byte-halving, not vendor 1.42/54% memory); C=35/27 | CLOSED/VERIFIED |
| P0-02 (r14) | P0 | Capstone mean 180ms vs p99 250ms (two-point mixture); −44%/−48% | CLOSED/VERIFIED |
| P1-01 (r14,r15) | P1 | Traffic time-basis (business-hours health); −100 as in-flight | CLOSED/VERIFIED |
| P1-04 (r14,r15) | P1 | 2rps/host is ANALYTICAL; feasibility 18,400/19,780=93% stated | CLOSED/VERIFIED |
| P1-09 (r14,r15) | P1 | Fig A.2 '% remaining vs predecessor' (7% remaining = 93% reduction) | CLOSED/VERIFIED |
| F18 (r14,r15) | P1 | All figure rasters >= 300 ppi at 6.1in placement (scan confirms 0 <300) | CLOSED/VERIFIED |

## Figure fixes (this QA run — all VERIFIED)

| id | severity | defect | state |
|---|---|---|---|
| Fig 7.1 | P1 | "query heads"/"shared K/V heads" side labels collided with cells/in-box K/V | VERIFIED (centered group labels) |
| Fig 8.1 | P1 | two-line title poked above box top; border cut through title (HBM/green boxes) | VERIFIED (lowered name y-centre) |
| Fig 14.1 | P1 | sub-8pt annotations (7.6/7.5) | VERIFIED (8.0pt) |
| Fig 15.2 | P1 | per-panel `[ILLUSTRATIVE]` tag collided w/ legend border + full-height line | VERIFIED (single footer) |
| Fig 16.1 | P1 | header title / subtitle overlap | VERIFIED (fig.text gap) |
| Fig 17.1 | P1 | 7.0pt caveat + "failover" grazed by N-1 line | VERIFIED (8.0pt + moved label) |
| Fig 18.1 | P1 | "…specialistyes…" merge + "small" struck/truncated by arrow | VERIFIED (renderer-measured anchor, split to 2 lines) |
| Fig 19.2 | P1 | sub-8pt effective (over-wide 6.52in bbox → ×0.936 downscale) | VERIFIED (8.6pt, nat 6.027in) |
| Fig 20.1 | P1 | sub-8pt effective (7.60in → ×0.803) + dotted line crossed annotation | VERIFIED (8.6pt + white bbox) |
| Fig 22.1 | P1 | 7.8pt note + annotation on-curve | VERIFIED (8.2pt + moved to whitespace) |
| Fig A.3 | P2 | raster-only, font unconfirmable | VERIFIED (9.26–9.59pt effective; vector .pdf generated) |

## Open / under vision

The current pass is independently verifying that the BUILT PDF's 46 figures and 355 pages
satisfy the release gates (print legibility, no collision, no clipping, semantic fidelity,
readable at final scale). The six figure-crop subagents are registering each figure into
`fig_vision_log.md`; any figure whose geometry verdict is not cleanly OK gets an entry here
for a targeted `vision_analyze` confirm + fix.

_Pending results — fig_vision_log.md (appended by subagents)._
