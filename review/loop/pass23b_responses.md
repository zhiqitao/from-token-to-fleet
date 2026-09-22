# PASS-23b RESPONSES — dedicated figure / diagram quality review

Verdict categories used: KEEP / POLISH / MAJOR REVISION / REDESIGN / REMOVE-MERGE.
Standard applied: judged at printed-book size; a figure can be correct yet still
fail if the reader must decode the layout before the idea. QA question list applied
(annotation collision, reading order, causal encoding, grayscale, prose-added-value,
caption-survival, book- vs slide-quality, rebuild-from-scratch test).

Review file: review/loop/pass23b_figure_review.md

## Global visual grammar (reviewer's "deliberate visual grammar" ask)
Consolidated in review/loop/figure_visual_grammar.md — colour semantics
(blue=compute, orange=persistent state/KV, green=network, red=warning/excluded),
connector semantics (solid=data, dashed=control/state, thick/double=high-volume,
loop=iteration, container=boundary, diamond=decision, stacked=replicas), grayscale
rule (colour ALWAYS paired with hatch/line-style/marker), font floor, and the 7-point
per-figure QA.

## Figure-by-figure status
| fig | verdict | status |
|-----|---------|--------|
| Fig 2.1 (list-of-fig pipeline) | REDESIGN (P0) | DONE — rebuilt two clean bands, text-sized boxes, proportional font shrink, orange KV conduit in inter-band whitespace, visual-grammar legend, qualified resource-regime language; light-fill+dark-text so it survives print + grayscale. Verified at source AND book scale. |
| Fig 2.2 | MAJOR REVISION | DONE — arithmetic-intensity continuum split by roofline ridge (~295 FLOP/byte), not binary "decode=bandwidth/prefill=compute". |
| Fig 7.2 | KEEP (preserve) | REVERTED my attempted in-plot note (it regressed a good figure); restored to committed state. |
| Fig 7.4 | MAJOR REVISION | DONE — "AGGREGATE RESIDENCY SCREEN ≠ PER-RANK FIT GUARANTEE" inside figure, 8 GPU partition lines, reserve relabeled "scenario reserve (not a hardware constant)", title/callouts declipped. |
| Fig 8.1 | MAJOR REVISION | DONE — physical hierarchy registers→tensor cores→SRAM→L2→HBM→interconnect→remote with "what runs here" column + speed↔capacity gradient; fixed all title/header/caption clipping + label collisions. |
| Fig 8.2 | POLISH | DONE (delegated) — "PER GPU" in-plot, H100/H200 grayscale-distinguishable (solid/circle vs dashed/triangle), ridge & example points labeled in-plot. |
| Fig 10.2 | REDESIGN | IN PROGRESS (delegated) — encoding PARTITIONED/REPLICATED/COMMUNICATE per strategy compactly. |
| Fig 11.2 | MAJOR REVISION | IN PROGRESS (delegated) — concerns not rigid stack. |
| Fig 11.3 | MAJOR REVISION | DONE — KV transfer visually dominant (thick orange double arrow), request/control thin grey, "prefill-optimized"/"decode-optimized" (not categorical). Ownership note moved clear of arrow. |
| Fig 12.1 | REDESIGN | DONE — candidate-synthesis reasoning chain (requirements→constraints→candidates→test against memory/latency/economics→survivors/rejected), the central thesis figure. |
| Fig 15.1 | MAJOR REVISION | DONE — explicit HBM vs on-chip physical regions, data movement via arrow multiplicity (7 vs 2), labels clear of arrows, "on-chip" fits block. |
| Fig 16.1 | MAJOR REVISION | DONE (delegated) — [ILLUSTRATIVE] price sensitivity band, break-even range not point. |
| Fig 17.1 | MAJOR REVISION / POSSIBLE REMOVE | NOT DONE — Archify boundary-validation fought the added failed-host; reverted to working committed state rather than leave a broken asset. Figure already shows routing/replicas. (open) |
| Fig 19.2/19.3 | KEEP/POLISH | DONE (delegated) — explicit "append-only illustrative model" in-plot, initial-vs-added grayscale-distinguishable. |
| Fig 20.1 | MAJOR REVISION | DONE — "KV/service-time analytical bound" labeling; utilization = offered-load under analytical service model, not GPU util. |
| Fig 21.1 | MAJOR REVISION | IN PROGRESS (delegated) — measured gates not generic CI/CD. |
| Fig 22.1 | KEEP/MAJOR POLISH | DONE (delegated) — in-graphic units warning "LEFT: PER REQUEST / RIGHT: PER GENERATED TOKEN / DO NOT COMPARE Y-AXIS", prefill decomposed (linear + quadratic attention term). |
| Fig 26.1 | MAJOR REVISION | DONE — already grouped bars (not radar); footnote declipped. |
| Fig 26.2 | MAJOR REVISION | IN PROGRESS (delegated) — capstone pattern-composition loop. |
| A.2 | POLISH | DONE — "DIFFERENT BASELINES — DO NOT COMPARE BAR HEIGHTS AS ABSOLUTE EFFICIENCY" in-graphic + caption; independent per-panel GridSpec. |
| A.4 | POLISH | VERIFIED CLEAN — maps layers→chapters (no overlap/clipping). |

## Still open (below book-quality threshold or further review needed)
- Fig 17.1 failed-host/failure-domain (Archify validation constraint).
- Remaining delegated (10.2, 11.2, 21.1, 26.2) — awaiting completion + raster verify.
- Fig 5.1, 10.1, 13.1, 23.1 (further MAJOR-revision candidates; partly responsive already).
- Global re-review after the delegated figures land.

## Rebuild note
run regen_figs.py (rebuilds every PNG + vector PDF) then build.sh, then raster-verify
the book-scale pages, then commit. regen_figs.py is NOT in build.sh — run manually and
re-crop Archify assets AFTER.
