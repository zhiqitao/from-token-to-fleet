# PASS-21 FIXER RESPONSES

PASS-21 re-reviewed with placed-page raster. Result: Fig A.2 fix CONFIRMED (103px gap), all prior
figure fixes HOLD. Two items kept the loop going because they were only partially/mis-fixed:

| # | Severity | Location | Problem | Disposition |
|---|----------|----------|---------|-------------|
| P21-1 | MINOR | Fig 10.1 | Band-title pill still abutted the first child card (~0.12pt) | **FIXED (root-caused, structural)**. The gap is governed by the Archify hard-coded `boundaryLabelClearance: 4` (renderer constant), NOT by `pad` or card y (my earlier edits only moved the frame border, which the pill also tracks — so the gap was invariant at ~4 viewBox units = ~1.5pt). Increasing the clearance to 40 gives a pill-to-card gap of 40 viewBox units = **15.15pt** at book placement (>=10pt target met). Pill still sits INSIDE below the dashed top border (frame border at y230, pill top y244), so the PASS-19 unbroken-dashed-border fix is preserved. Verified: pill bottom y260 vs card top y300. |
| P21-2 | MINOR | Fig 12.1 | Grey decode note + red excluded note were separated from each other but BOTH overprinted the black panel-2 title | **FIXED**. Moved the grey note into the interior whitespace between the (b) bar and (c) region (x=1.5, y=14500) and the red note to the external right whitespace (x=2.5, y=23000). Verified at source: neither note overlaps the title "(2) Prefill throughput (idealized aggregate, 8xH100 host)" nor any black axis/category text; notes are clear of each other. |

## Root-cause lesson (P21-1)
The prior P20-1 "fix" edited the Archify *deliver.html* by hand, and the JSON still carried the old
card positions, so the rendered figure used the stale coordinates (the reviewer caught this). The real
lever for region-label-to-content clearance is the renderer's `boundaryLabelClearance` constant, not
`pad` or component `pos` (both of which the label auto-tracks). Recorded in the archify-diagrams skill.

## Verification
- Fig 10.1: pill-to-card 15.15pt (deliver geometry), pill inside below unbroken dashed border. Build re-run.
- Fig 12.1: notes in whitespace, no title/axis overlap (vision confirmed).
- Fig A.2: already confirmed landed by PASS-21 (103px gap).

## Regression check
All PASS-17/18/19/20 figure fixes confirmed holding by PASS-21 review (Fig 8.1, 7.3, 7.2, 7.4, 4.1,
6.1, 6.2, 10.2 "experts 6-10", 20.1 "~28 hosts", A.4 arrow-up, 15.1, A.1, A.3, Ch18 §3.2, Ch16 §16.4).

## Convergence
PASS-21 = 2 partial-fix recurrences, both now structurally resolved. No CRITICAL/MAJOR/MODERATE.
Proceeding to PASS-22 to confirm zero-new-comments.
