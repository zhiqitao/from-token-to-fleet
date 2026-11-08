# Intel GPU/XPU independent research — delivery status

Final checkpoint: 2026-10-28T07:19:35Z. Initial verified clock: 2026-10-27T23:37:41-07:00. The directory uses the UTC date.

Scope: research, developed candidate English text and original figure assets only. No manuscript edit, shared-configuration edit, other-agent file edit, delegation, commit, push or publication. Existing unrelated dirty files remain outside this task's ownership.

## Deliverable states

| Component | State | Evidence |
|---|---|---|
| Chinese investigation | DELIVERED | intel-xpu-research.md: identities, hardware/resource table, version/feature boundaries, comparison protocol, adoption/falsification assessment, chronology and gaps |
| Structured claims | DELIVERED / mechanically checked | claims.json: 33 claims, 72 source records, 69 usable records and 3 excluded records; excerpts/line ranges, exact URLs, release/event dates, UTC retrieval times, immutable pins, provenance, conditions and disposition |
| Developed English text | DELIVERED / candidate, not applied | proposed-insertions.md: substantive prose, worked example, exact chapter/section map, replacement passages, compact validation checklist, explicit figure reference and dated appendix box; not merely an outline |
| Figure plan | DELIVERED | figure-plan.md: learning objective, mechanism, placement, composition, actual text width and necessity |
| Figure source | DELIVERED / reproducible | figures/generate.py and editable figures/intel-backend-paths.svg |
| Figure render | DELIVERED / dimensions checked | one original figure; 1830 × 1890 PNG at 300 ppi, intended 6.1 × 6.3 inches; optional vector PDF, grayscale PNG, detail crop and isolated Letter placement proof |
| Figure inspection | PERFORMED / no remaining observed P0/P1/P2 | figures/QA.md: whole-figure, detail, grayscale and actual-size Letter placement inspections; final inspected hashes recorded |
| Reproduction manifest | DELIVERED / linked IDs checked | figures/manifest.json: source/render paths, command, intended width, caption, alt text, related prose anchors and claim/source IDs |
| Verification record | DELIVERED | verification.json, arithmetic.json, manuscript-read-inventory.json |

## Evidence and chapter coverage actually completed

- Read review/publication_v2_20261028/MASTER_INSTRUCTIONS.md and the relevant source chapters: 05, 07–18, 20, 21, 27 (16 chapters). Coverage is substantive source-text reading, not only headings. Source hashes are recorded in manuscript-read-inventory.json. Chapter 08's latter sections were explicitly checked through its final line.
- Verified immutable baseline PDF again: 361 pages, 612 × 792 pt, US Letter; SHA256 66f8392d6b768de7af4695b3d93d70b48858eb75a944020dbcfa9f4d1768b758. No full-PDF visual audit claimed.
- Verified live style: render/latex/book.sty uses 1.2-inch left/right margins, so the 8.5-inch page provides 6.1 inches of figure/text width. The legacy 6 × 9 visual-review prompt was not used as the current trim specification.
- Preserved source snapshots, original downloaded PDFs where acquired, UTC retrieval records and citation ledger. SearXNG was initially unreachable; a keyless search fallback was used without changing configuration.
- Distinguished Intel GPU torch.xpu, oneAPI/SYCL/Level Zero/library roles, native SYCL engines, OpenVINO client routes, and Gaudi hpu/HCCL.
- Retrieved latest release metadata and pinned relevant PyTorch/vLLM/SGLang/llama.cpp source content. SGLang commit a1966e1b5d8b750b494d7e53cca1d2464f960038 was separately confirmed by commit API, with commit time 2026-10-28T06:26:29Z; its newer main features are not assigned automatically to the October 19 release.
- Preserved the Appendix A 2026-08-30 cutoff and separate September observation. Proposed a separate 2026-10-28 box, not a silent date update.
- Computed analytical memory, weights-only scan and directional network examples with Python. No analytical number is labeled measured.

## Corrections and conflicts retained rather than hidden

- Crescent Island chronology was updated using retrieved Hot Chips/OCP evidence: current D-series/D270 sampling statement, Intel-branded 160 GB card, partner configurations up to 480 GB. GA remains unverified.
- Flex 170 identity: reject misleading URL with SKU 230020 returning Flex 140; use verified SKU 230019. Source 48 is excluded.
- Wrong SGLang path/source 15 and Page Not Found OMIX/source 70 are excluded. The initial fetcher accepted some sufficiently long error pages; detection was tightened and final registry excludes them.
- Failed fetches remain in retrievals.jsonl/claims.json: gaudi-stack, torch-pinned-doc, xe-driver-matrix. Gaudi porting/HCCL documentation, the correctly named PyTorch Markdown file and valid driver overview provide narrower alternative evidence. No failed matrix is treated as retrieved support.
- vLLM pinned requirements and installation guide disagree on Triton version. Graph code/setup guidance and the generic CUDA-graph table are not reduced to an unconditional yes/no. SGLang source-install wording and container instructions are likewise kept as a documentation inconsistency.
- B70 datasheet render note conflicts with the launch announcement on Intel-branded card purchase availability. Both statements are recorded; stock was not independently checked.
- B60's May 2025 announcement describes June sampling, not June GA. Personal April 2026 purchase is an attributed observation, not global stock evidence.
- EmbeddedLLM acknowledges Sparkle-provided hardware and Intel technical support. It is not labeled an independent controlled cross-vendor benchmark.
- The first figure inspection found ambiguous connector semantics. A dashed SVG style then failed to appear in the renderer; grayscale/Letter vision checks caught it. The generator now draws explicit dash segments. Final whole-figure, detail and placement inspections confirmed the correction with no remaining observed P0/P1/P2.

## Checks actually executed

    python research/intel-xpu-20261028/figures/generate.py
    python research/intel-xpu-20261028/build_registry.py
    python research/intel-xpu-20261028/finalize.py
    python -m py_compile research/intel-xpu-20261028/build_registry.py research/intel-xpu-20261028/fetch_sources.py research/intel-xpu-20261028/finalize.py research/intel-xpu-20261028/figures/generate.py

All completed with exit 0 in the final checks. Finalize checks source excerpt equality, citation/claim links, no you/your wording in proposed book text, manifest assets and hashes, PNG/PDF dimensions, minimum PDF label size, baseline PDF identity and reading inventory. It records current Git status without altering it. PyMuPDF emits a non-fatal deprecation warning for the legacy fitz import; rendering and validation succeeded with the installed version.

## NOT VERIFIED / not implied by delivery

- No Intel GPU, client NPU or Gaudi hardware execution; no wheel/container pull, install, digest validation or serving launch.
- No complete device × OS/kernel/firmware/runtime matrix; no allocation-limit, peer-access or topology measurement; no universal weight/activation/KV quantization, multimodal, EP, graph or multi-node validation.
- No measured model quality, request isolation, latency/goodput, benchmark reproduction, whole-system energy, production utilization, market share, independently confirmed inventory, current quote or TCO result.
- No conclusion that Intel universally wins or has established a commercial rise. Upstream integration and limited deployment signals are the supported finding.
- No full-manuscript insertion/rebuild, page/caption/numbering check, final-PDF font preflight, physical paper proof or release certification. The isolated figure's actual-size inspection is separate from those tasks.
- No legal clearance for redistribution of cached third-party documents. The proposed prose and geometry are original; no copied vendor art or benchmark curve is proposed for publication.

The required research/text/figure artifacts are delivered for parent verification and integration. The empirical and publication checks above remain explicitly open; delivery is not a claim that those checks passed.
