# PASS-20 FIXER RESPONSES — updated after final verification

PASS-20 re-reviewed with pixel/raster inspection. Confirmed PASS-19 Fig 10.1 fix LANDED and all
prior figure fixes HOLD. Three items were addressed; the Fig A.2 banner fix required a robust
re-approach (below).

| # | Severity | Location | Problem | Disposition |
|---|----------|----------|---------|-------------|
| P29-FA2 | MINOR | Fig A.2 | "NOT COMPARABLE" banner overlapped/hid the "/token" tick labels (center panel fully) | **FIXED (deterministic)** — root cause: the banner was placed with `fig.text` at a figure-fraction y, and `bbox_inches='tight'` rescales such that the fraction position is unreliable relative to the axes tick labels; each y tweak still collided. Rebuilt the figure with `GridSpec`: the three panels occupy the top cell and the banner + note live in their OWN bottom axes, so they can never collide. Placed-page gap measured = 109px. |
| P20-1 | MINOR | Fig 10.1 | Band-title white pill abuts the first child card (~0px clearance) | **FIXED** — shifted the EP child boxes (y 90->100) and PP stage boxes (y 560->570) down 10pt. Measured 10.4pt pill-to-card clearance (pixel). |
| P20-2 | MINOR | Fig 12.1 | Grey "decode pool" note, red "(c) excluded" note, black axis text overlapped | **FIXED** — moved grey note to (1.45, 23500) and red note to (2.35, 24800). Verified at book scale: grey and red in separate whitespace, both clear of black axis/category text. |

## Honest correction on method
At PASS-20 I initially reported the Fig A.2 fix as landed based on a first raster measurement that
showed a 4px gap. That was WRONG on two counts: (1) my grey-pixel detection window had been
truncated and was not isolating the actual "/token" glyph row; (2) a 4px gap is not the clean
separation a publication figure needs. Only after rebuilding the banner into its own GridSpec band
did the placed page show a real, robust 109px gap. Lesson re-affirmed and now applied: verify
figure fixes by measuring the PLACED page raster with a full (untruncated) row histogram, and
prefer structurally-robust layouts (dedicated subplot/axes) over fragile figure-fraction callouts.

## Verification
- Fig A.2: 109px gap ("/token" bottom 1982 vs banner top 2091) on placed page 292 @300dpi.
- Fig 10.1: 10.4pt pill-to-card clearance.
- Fig 12.1: grey/red/black notes separated.
- All prior figure fixes confirmed holding (no regression).

## Convergence
PASS-20 = 1 re-surface + 2 NEW MINOR, all addressed. No CRITICAL/MAJOR/MODERATE. The
figure-legibility convergence tail continues; items are MINOR-only styling. Proceeding to
PASS-21 to confirm zero-new-comments.
