# Video-generation research status

State: DELIVERABLES_COMPLETE_FOR_PARENT_REVIEW. These are isolated research/candidate publication assets, not an integrated or publication-certified book.

## Boundary and clocks

Own directory: `/home/ubuntu/hermes-work/from-token-to-fleet/research/video-generation-20261028/` only. No further delegation, manuscript edits, shared configuration changes, commits or pushes were performed by this worker. Pre-existing working-tree changes were observed and not reset/cleaned. Controlling `review/publication_v2_20261028/MASTER_INSTRUCTIONS.md` was read; release-investigation, serving-research and figure-rendering guidance was used.

Research date: 2026-10-28 UTC. Initial verified clock was 2026-10-27T23:40:50-07:00; latest checked local clock before final handoff was 2026-10-28T00:17:04-07:00. Machine verification timestamps are in `validation.json` and source manifests. Frozen book cutoff remains 2026-08-30. Supplied frozen book is 361 pages, US Letter; no independent pagination check was run. All proposed video additions are explicitly a controlled current-snapshot update. Earlier model/report release dates do not make current code/licenses/engine details historical August facts.

## Separate deliverable states

| Component | State | Evidence |
|---|---|---|
| English text | DEVELOPED; not applied | `proposed-insertions.md`: substantive mechanism/causal prose, exact chapter/section and phrase anchors, worked Wan5B example, explicit figure calls and primary-source footnotes |
| Chinese research | DEVELOPED | `research.md`: official inventory, architecture/attention boundaries, serving/fleet implications, licensing/safety caveats, bounded evaluation plan |
| Claims and calculations | GENERATED AND CHECKED | `claims.json`: 43 claims; `calculations.json`, `benchmark-evidence.json`, `source-catalogue.md`, `verify_sources_and_math.py` |
| Figure source | COMPLETE AND EDITABLE | `figure-plan.md`; two original SVGs; `figures/generate_figures.py`; `figures/figure-data.json`; `figures/manifest.json` |
| Render | SUCCESSFUL | Two 350-dpi print PNGs, grayscale versions, 150-dpi actual-size proofs and detail crops; intended width 6.1 in |
| Inspection | PERFORMED; standalone only | Whole-figure and detail vision inspection, revision, second self-critical/source-adjudicated pass; actual findings and P0/P1/P2 disposition in `figures/QA.md`; exact geometry in `figures/geometry-QA.json` |
| Artifact validation | PASS at last run | `validation.json` and reproducible `verify_artifacts.py`; source hashes, calculations, citations, files, release metadata, raster hashes, labels and collision checks |
| Final-book integration / placed-page inspection | NOT PERFORMED | Parent-owned; no manuscript or book PDF was modified |

## Evidence and executable checks

- 97 public-source fetch records: 94 retrieved; three gated LTX-2.5 raw card/config requests returned 401. No credentials were requested and no gate was bypassed.
- 19/19 recorded immutable-pin byte checks match. This does not claim that every source is commit-pinned. Archived bytes carry SHA-256 and retrieval dates.
- Wan public HF inventory contains 27 entries, not 27 independent architectures. Current hosted Wan3 preview IDs are separated from public-weight architectures.
- Final standalone figures: `video-latent-work` and `wan-noise-experts`. Dense Wan2.2 TI2V-5B geometry is not mixed with A14B expert routing.
- Successful tool execution: source/math verifier, claims builder, Inkscape SVG rendering, geometric/raster validation and artifact verifier. No video inference, GPU timing, energy measurement or production-serving benchmark was run.
- Reproduction from repository root:

  `python3 research/video-generation-20261028/verify_sources_and_math.py`

  `python3 research/video-generation-20261028/build_claims.py`

  `python3 research/video-generation-20261028/figures/generate_figures.py`

  `python3 research/video-generation-20261028/verify_artifacts.py`

The first command performs public network pin checks; the remaining commands operate on archived inputs. Rendering requires Inkscape and Pillow. No command installs or configures a serving engine.

## Review checkpoints and corrections

1. Official discovery rejected contradictory third-party Wan2.7 openness/architecture snippets. Official current overview/API instead substantiated hosted `wan3.0-video` / `wan3.0-video-prime` preview IDs without implying public architecture or weights.
2. Report/code/config cross-checks preserved LTX parameter conflicts, gated access, Wan2.2's older report-link limitation, and Hunyuan report/release/license date boundaries.
3. Source pins and math were executed. Benchmark review corrected Hunyuan timing to seconds per diffusion step / 50-step run on eight H800 and LTX scope to 121 frames, 720p, Euler, CFG=1. These remain incomplete vendor tuples, not comparable cost measurements.
4. Mandatory figure scope was implemented, not merely planned. First-pass legend ambiguity was fixed; sources, figures and print proofs were regenerated. Vision-model numerical objections were checked against exact source/config before acceptance or rejection. See QA for actual findings.
5. Final source audit corrected draft-only Animate2 citation/date to arXiv:2608.06009 / 2026-08-06, Dancer submission to 2026-07-10, and Hunyuan1.5 config to hidden2048 / 16 heads / 54 dual-stream blocks. Unsupported Qwen encoder parameter precision was removed. Animate2-Base versus causal chunk-wise Lite was added as a bounded architecture distinction, without inventing KV-cache internals.
6. Required artifacts now exist, including `figures/QA.md`; the earlier checkpoint's drafting/planning/pending states are superseded by the separate states above.

## Open boundaries for parent review

Parent figure-clarity follow-up (2026-10-28 UTC): addressed within this directory only, without redoing the broad research. Text state: linked English captions synchronized, explanatory body unchanged. Figure-source state: targeted generator edits complete. Render state: both figures regenerated at 350 ppi / 6.1 in width with 9.36-pt minimum labels; heights now 6.0 in (V1) and 3.95 in (V2). Inspection state: final full color proofs, full grayscale rasters and color detail crops inspected, including a second self-critical pass. V1 explicitly labels denoising/scheduler iteration, prompt tokens, VAE factors and aligned temporal endpoint. V2 explicitly labels schedule progression (not two experts within one forward), expert checkpoints, conditional GPU residency and schematic stage widths. Official rounded parameter counts retained without an invented split/threshold. Accepted/rejected issues and VLM objections are adjudicated in `figures/QA.md`. No unresolved standalone P0/P1/P2 raster defect; physical-print/final-book placement remains unverified. Local validators rerun; authoritative latest count/status is in `validation.json`.

- Three gated LTX-2.5 sources; exact inaccessible transformer/VAE details remain unknown. Official engine documentation does not equal a locally validated serving path.
- LTX-2 report says 14B+5B in abstract versus 13B+3B in conclusion. No invented reconciliation.
- API availability/preview status does not establish exact first-public-release dates, public checkpoints, architecture or self-hosting support.
- No matched quality/cost benchmark tuple exists in this package; no price-per-usable-clip conclusion is justified. The bounded plan states missing measurements.
- Full frozen-cutoff historical checkout was not performed. Parent must either authorize a dated update or exclude/reverify these current-source additions.
- Final page placement, caption/numbering, page breaks, placed type size and physical-print inspection remain pending. The 6.1-in assets must not be silently reduced without a new legibility check.
- Worker self-report and artifact PASS do not establish publication readiness or replace independent primary-source review.
