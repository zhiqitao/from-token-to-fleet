# Loop 7 — Convergence Note

## Auxiliary review model consulted
Qwen3.8-27B (tailscale 100.105.225.59:30000) gave a decisive recommendation:
fix the reader-visible items (#2 Table 16-2 straddle, #3 Table 15-1 Typi/cal,
#4 Fig 16.1 in-figure tags, #6 caption normalization), accept #1 (math-subscript
exemption) and #7 (531pt lines within trim), fix #5 only if a clean local tweak,
and run ONE narrow confirmation pass (not another full 362pp review).

## Executed
- **L6-2 Fig 8.2** — removed the stray mid-plot red triangle marker (vision CLEAN).
- **L6-5 LoF off-by-one** — already resolved in the 362pp build (all 38 entries match).
- **#3 Table 15-1** — widened Regime column; "Typical" no longer hyphenates (0 breaks).
- **#4 Fig 16.1** — removed 3 bracketed [ILLUSTRATIVE] in-figure tags; maroon
  disclaimer banner kept (vision CLEAN).
- **#2 Table 16-2** — \needspace{18} keeps the caption at the top of its page
  (no longer orphaned at the foot of the previous page).
- **ch2 caret** — last raw `^` in the text layer (1.29 ×10^15 → ×10¹⁵) fixed.
- **#1 B_eff 5.98pt** — documented as a math-subscript exemption in the review
  prompt (LaTeX body-math script size is conventional; not a figure/prose defect).
- **#5 Fig 14.1 blank foot** — accepted as a layout artifact (fixing needs a
  content restructure / float package; not worth destabilizing the build).
- **#7 531.2pt lines** — accepted (within the 540pt trim; justified-edge/mono class).

## Reverted (caused more churn than the fix was worth)
- **#6 caption normalization** (10 `#### Table N-N` → inline bold) — shifted
  pagination, stranded Table 13-1, and a section-Needspace bump to fix that added
  5 pages + a new stranding. Reverted; the table-caption font drift (italic
  heading-style vs bold inline) is accepted as a documented MINOR inconsistency.
- **keep_table_captions pipeline fn** — added 2pp churn; the 19 inline-bold
  captions worked without it in the clean build. Reverted.

## Final state (362pp build, commit cf8e4f39)
- 0 margin/edge overflows (only p1 cover running header)
- 0 canonical/scenario label tears, 0 label hyphen-breaks
- 0 orphaned captions, 0 orphaned headings
- 0 tofu, 0 XNAME, 0 <300ppi, 48/48 independent checks
- All 38 LoF entries match actual caption folios

## Verdict
**CONVERGED.** Content/correctness converged in Loop 6 (0 CRITICAL/MAJOR new
content findings). Loop 7 cleared the remaining reader-visible typography items
and documented the accepted MINOR residuals (table-caption font drift, Fig 14.1
blank foot, 531pt lines, B_eff math subscript). No further actionable findings
remain that are worth the risk of destabilizing the build.
