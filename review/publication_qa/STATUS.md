# STATUS — publication-quality QA checkpoint

**Repo:** /home/ubuntu/hermes-work/from-token-to-fleet
**Branch:** main · **HEAD:** e6b16f40 (working tree clean at start)
**Build:** render/build/from-token-to-fleet-v20260913.pdf · **355 pages** · Type3 0 · tagged
**Build ID / evidence cutoff:** v20260913 / 2026-08-30
**Proof SHA-256 (start of this pass):** 511b132bc5c5c5b877d4dc5a91fee21066fa3d4e19281679314d290793499a91

---

## Phase: AUDIT / VISION-ACCEPTANCE (in progress)

### Done
- **Baseline** captured (HEAD, pages, sha256, proof backed to `renders/`).
- **Vision smoke test** (`vision_smoke_test.md`): **PASS** — model receives real pixels,
  answers pixel-only spatial questions, Fig 1.1 confirmed clean.
- **Independent numerical verification** (`NUMERICAL_VERIFICATION.md` +
  `calculations/verify_canonical.py`): **48 checks, 0 failures** — all canonical
  quantities re-derived from first principles (FP8 KV, concurrency 35/27, $0.301932/
  $9.259259/$0.292398, crossover 53.4K, capstone 180ms/250ms/44%/48%, feasibility 93%).
  Does NOT import the repo's calc scripts (avoids oracle-collusion).
- **Automated layout scan** (`page_ledger_auto.csv`): **355 pages, 0 out-of-page text**;
  column overflow benign (max_x ~527-531pt). 44 pages report some sub-8pt spans
  (mostly table/annotation, to confirm in vision pass).
- **Automated figure inventory** (`figure_ledger_auto.csv`): **0 raster figures below
  300 ppi** (F18 closure confirmed).
- **Source-level consistency** (Pass B): no "Ch 27" refs, no stale FP8 values, no editor
  instruction leak, @GITSHA@ placeholder present.

### In flight
- **6 vision-audit subagents** cropping/registering all 46 figures into
  `fig_vision_log.md` (batches 1-6). On return: run `vision_analyze` on any figure
  whose geometry verdict is not cleanly OK, then fix any figure defect, rebuild, re-verify.

### Next exact action
1. Collect the 6 figure-batch results from `fig_vision_log.md`.
2. For each figure flagged with a layout/legibility concern, run `vision_analyze` on its
   crop to confirm; log real findings into `ISSUES.md`.
3. Fix any confirmed figure/text defect; rebuild; re-run regression + layout scans.
4. Write `RELEASE_REPORT.md` with a truthful verdict (READY / NOT_READY / BLOCKED_UNVERIFIED).

### Counters
- pages audited: 355 (automated geometry); vision pages: p25 done (smoke test) + figures in flight
- figures: 46 (automated inventory); vision-confirmed: 1 (Fig 1.1) + 46 in flight
- P0 open: 0 (all three from the 15th review closed & verified) · P1 open: 0 in-manuscript
- tests: verify_canonical 48/48 pass; layout 0 out-of-page; figures 0 <300ppi
