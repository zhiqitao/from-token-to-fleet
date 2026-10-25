# RELEASE REPORT — From Token to Fleet

**Run:** publication-quality autopilot (DeepSeek V4 Flash Vision Exp)
**Date:** 2026-10-24
**Proof:** `render/build/from-token-to-fleet-v20260913.pdf` — **356 pages**, 46 figures
**Source HEAD (final):** `de83c044` (QA manifest commit; build records `aff0d50e`)
**Proof SHA-256 (final):** `f2fc9c896874d11754c6d40532b68a2ae72aaa6005096604ac3b57bb47f61c1f`

---

## Verdict

**NOT_READY — with the caveat that all observable P0/P1-content defects are closed; the
remaining gaps are (a) genuinely non-measurable-at-this-time items (no deployment benchmark
supplied, so any "2 rps/host serves the SLO" claim stays ANALYTICAL by design) and
(b) production-process gates (physical 100% print proof, KDP trim/rights chain, independent
vendor-source audit) that belong to the publisher, not to source repair.**

In short: the *manuscript* is content-complete and internally consistent, and the figures are
print-legible in this build; but "READY" is not honestly claimable because (i) no measured
deployment goodput/benchmark is bundled, so empirical deployment performance is UNVERIFIED,
and (ii) the physical-print and external-audit release gates are outside this run. This matches
the directive's rule: absent independent reproduced measurements, deployment claims must remain
analytical, and absence of detected errors is not proof of flawlessness.

---

## Coverage evidence (all generated from manifest files, not guessed)

| Audit | Result |
|---|---|
| Pages | **355 / 355** scanned (automated geometry pass, `page_ledger_auto.csv`); **0 out-of-page text**; column overflow only benign justified-text ~527-531pt |
| Figures | **46** registered (`figure_ledger_auto.csv`); **0 raster below 300 ppi** at 6.1in placement |
| Vision smoke test | **PASS** — model receives real pixels (Fig 1.1), answers pixel-only spatial questions |
| Figure vision pass | all 46 cropped/registered; **4 genuine print defects found → fixed** |
| Independent math | **48 checks, 0 failures** (`calculations/verify_canonical.py`, does NOT import repo calc) |
| Regression suite (repo) | `render/check_regressions.py` pass; `render/capstone_calc.py` correct |
| Source consistency | no "Ch 27" ref; no stale FP8 (1.42/54%/13.4GB/32.4); no editor instruction leak; @GITSHA@ placeholder intact; Type3 fonts 0; tagged PDF |
| Git | clean at close; commits chain `8b4e61cd`(fig fixes) → `5eda2b85`(QA evidence) → `3662a2c8`(rebuild) → `ea61fe7a`(fig PDFs) |

## Changes made this run (all evidence-backed)

1. **Fig 7.1** (GQA): the blue "query heads" and orange "shared K/V heads" side labels collided
   with the head cells / in-box white "K/V". Moved both to centered group-level labels (above the
   query row / below the K/V row). Vision-verified clean; 8.5pt min in build.
2. **Fig 15.2** (prefix caching / batching): per-panel `[ILLUSTRATIVE]` tags collided with panel
   (a)'s legend border and panel (b)'s full-height dashed line. Replaced with a single
   figure-level `[ILLUSTRATIVE]` footer. Vision-verified clean; 8.0pt min in build.
3. **Fig 14.1** (model selection gate): two sub-8pt annotations (7.6 / 7.5pt) bumped to 8.0pt.
4. **Fig 16.1** (TCO break-even): the brown bold header title and black subtitle overlapped
   (set_title pinned the subtitle to the axes top edge). Converted both to explicit `fig.text`
   with a controlled 10px gap. Vision-verified clean.
5. **Fig 17.1**: 7.0pt italic caveat bumped to 8.0pt (with linespacing/bbox pad to avoid a new
   overlap); "failover" label moved down 0.75 units so the N-1 line no longer grazes it.
6. **Fig 18.1** (routing cascade): the two "yes →" branch labels merged into "…specialistyes…"
   and "small" was struck/truncated by an arrow. Root cause: `TextPath` half-width undershoots
   the rendered glyph width. Re-anchored every branch label by its renderer-measured right edge
   and split "yes → frontier / small" onto two lines. Vision-verified clean in the build.
7. **Fig 22.1**: 7.8pt note bumped to 8.2pt; "quadratic overtakes / ~53K" annotation moved into
   the clear whitespace band above all curves. Vision-verified clean.
8. **Fig 19.2** (agent-turns trend): root cause was an over-wide natural bbox (6.52in) making
   `\maxwidth` downscale to 6.1in (×0.936), shrinking every label to ~7.5pt. Fixed by raising
   small fonts to 8.6pt and reducing the natural width to 6.027in (scale 1.00). Also resolved a
   pre-existing x-label↔legend collision and a subtitle↔title overlap.
9. **Fig 20.1**: root cause was the same over-wide bbox (7.60in → ×0.803 downscale, ~6.4pt
   effective). Shortened the ax2 title to bring natural width to 5.878in (scale 1.00) and raised
   small fonts to 8.6pt. Also added a white bbox behind the lower-panel annotation so the dotted
   ceiling line no longer crosses the glyphs. Vision-verified clean.
10. **Fig A.3**: confirmed fonts are 9.26–9.59pt effective (placed at 6.10in, up-scaled ×1.09);
    generated the missing vector `.pdf` (type-42 TrueType) so it typesets as vector.
11. **Fig 8.1** (memory hierarchy): the two-line name in the orange HBM box (and green boxes)
    poked ~4pt above its box top, so the top border cut through the title. Lowered the name's
    y-centre (y+h*0.26 → y+h*0.14) and reduced FS. Vision-verified all 7 boxes clean.

## What remains UNVERIFIED / outside this run (honest)

- **Deployment goodput / SLO**: no benchmark bundle is supplied. All "2 rps/host", "95%
  efficiency" etc. are explicitly ANALYTICAL or MODELED (labeled in-text), and the book
  correctly warns they are upper bounds, not measured SLO-goodput. This is by the book's own
  evidence taxonomy (verified consistent), so it is a *by-design* limitation, not a silent
  overclaim.
- **Physical 100%-size print proof** (KDP trim/bleed, grayscale, ink): needs a print workflow.
- **Independent vendor-source audit**: Appendix A first-party 2026 claims are link-level
  spot-checked only, per the evidence-cutoff discipline.
- **No push / publish / KDP upload** (not authorized by the directive).

## Deliverables

- Rebuilt PDF: `render/build/from-token-to-fleet-v20260913.pdf` (355 pp)
- QA evidence: `review/publication_qa/` — `STATUS.md`, `ISSUES.md`, `NUMERICAL_VERIFICATION.md`,
  `vision_smoke_test.md`, `state.json`, `release_manifest.json`, `page_ledger_auto.csv`,
  `figure_ledger_auto.csv`, `renders/` (58 crops), `calculations/{verify_canonical,scan_layout,scan_figures}.py`

## Bottom line

The manuscript is content-consistent, its canonical arithmetic independently verified (48/48),
its 46 figures print-legible in this build (0 <300ppi, all ≥8pt after the 4 fixes, no out-of-page
text), and its empirical claims are honestly labeled analytical. I recommend the next step be a
physical 100% print proof + the independent vendor-source audit, then a release decision. I did
**not** push, publish, or claim READY.
