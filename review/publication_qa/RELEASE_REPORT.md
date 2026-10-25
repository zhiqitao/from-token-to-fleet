# RELEASE REPORT — From Token to Fleet

**Run:** publication-quality autopilot (DeepSeek V4 Flash Vision Exp)
**Date:** 2026-10-24
**Proof:** `render/build/from-token-to-fleet-v20260913.pdf` — **355 pages**, 46 figures
**Source HEAD (final):** `ea61fe7a309048d9ef7bc92652e55d151a9f9e08`
**Proof SHA-256 (final):** `fd1859ed85bbeb61fc7a423a53f85a07489b30845c1cf42d57347c837d3552a6`

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
   Verified 8.0pt min in build.
4. (Checked, no change) Fig 19.2 sub-8pt report was a false alarm — measured 9.96pt in build;
   Fig 20.1 footer measured 9.96pt (false alarm vs reported 6.4pt — the report measured a
   different scale).

BTW: the build changed pages 355 (from the reviewer's 352) because the 15th-review content
fixes added the matched-TCO table, feasibility check, and expanded notes — consistent, not a
regression.

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
