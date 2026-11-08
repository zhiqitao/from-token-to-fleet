# Research checkpoint

Scope: public model research and proposed prose only. No manuscript changes. No delegation, commits, publication, or gateway changes.

Clock observed: 2026-10-27T23:36:02-07:00 (2026-10-28 UTC). Directory date is the UTC research snapshot, not an assumed local date.

Loaded model-release-investigation, llm-serving-tech-research and searxng-web-research. Read MASTER_INSTRUCTIONS.md. Standards applied: causal mechanisms; scope/denominator integrity; vendor-reported versus measured; explicit dated update. Full-PDF audit is outside this research assignment.

Primary cards/configs now fetched for Qwen/Qwen3.8-27B, ornith-ai/Ornith-1.5-{397B,35B-A3B,9B,122B}, DeepSeek-V4-Flash, GLM-5.3-Flash, MiMo-V2-Flash and Gemini 3.8 Flash. Newer public records found and fetched: DeepSeek-V4.1-Flash(-1017), MiMo-V2.6-Flash-RL. All speed/quality comparisons remain vendor-reported, not independently measured.

Important manuscript-context discovery: current Chapter 3 already covers Qwen3.8-27B and Flash-Next; Appendix A already has four-family hybrid-attention analysis, an explicit 2026-08-30 boundary and a 2026-09-27 Ornith observation. Do not duplicate these as entirely new additions. August 19 cannot be assumed as the sole current cutoff. Research must propose an explicitly separate October 28 update and reconcile existing source-version boundaries.

Material unresolved issues: MiMo-V2 card's simplified 5:1 layout differs from config and full report's 39 SWA / 9 global layers; MiMo-V2.6 card says 5-layer speculative decoder while config has num_nextn_predict_layers=3. GLM's linked GLM-5 February report is not direct evidence for all 5.3-Flash-specific claims. DeepSeek arXiv 2606.19348 abs returned an April 26 submission date despite the June identifier prefix; preserve this metadata inconsistency, not a silently repaired date. Captured metadata and SHA256 are in fetch-log.json.

Huginn and Ouro primary paper/card/config/code fetched. Huginn's card explicitly needs recurrence-aware cache and labels adaptive compute zero-shot proof-of-concept. Ouro current arXiv revision is v6, 2026-10-11 (initial 2025-10-29); its short model card omits key serving details, requiring full-report/code crosscheck. PDF text extracted locally; no remote code executed.

Tool limitations: execute_code is blocked in unattended mode. SearXNG is unreachable; built-in web_search used its explicitly reported keyless rescue. Use direct HTTP fetches and a saved Python collector next. No private content has been sent to web endpoints.

Completed deliverables: model-trends-research.md (Chinese), claims.json (40 evidence-scoped claims), proposed-insertions.md (English candidate prose, not applied). Supporting primary-sources.md/source-index.json and local public-source snapshots retained. 78 distinct source attempts, 74 successful GET artifacts, 4 explicit failures; all accepted claim supports match stored SHA256. Candidate prose has 20 successfully fetched citation URLs and 10 complete footnotes. validate.py passed schema, citation/hash, table, arithmetic and no-you/your checks; all four helper scripts passed py_compile. Validation rerun after final edits is authoritative in validation.json.

Baseline pdfinfo confirms 361 pages, 612×792 pts (USLetter). No baseline manuscript-page rendering/layout audit performed. Eight read chapter versions remained unchanged at validation. Existing unrelated changes were left untouched. No model benchmarks or remote downloaded model code executed. Unresolved source/version issues remain explicit.

Mandatory text-and-figures update: expanded proposed-insertions.md with mixed-state checkpoint/rollback consequences, a derived Qwen storage example, an illustrative executed-depth work budget, communication, scheduling, latency and quality-compliant cost analysis. Added original MT-1 and MT-2 SVG/PNG/PDF figures, generator and data, manifest, grayscale and detail renders, and isolated Letter placement proofs. All authored files remain in this assigned directory. Figure plan precedes rendering. First vision review found disconnected outer weight branches and KV alignment issues; revised and re-rendered. Further reviews prompted explicit successive-state labeling and hue-independent legends. Exact geometry checks resolve the vision review's inaccurate residual-centering estimate. QA.md and STATUS.md are the final acceptance/limitation records, not this checkpoint's earlier pre-update completion state. No integrated manuscript or physical print acceptance is claimed.
