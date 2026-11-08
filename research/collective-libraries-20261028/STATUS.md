# Status

Scope: independent collective-library research and unapplied integration proposal only. No delegation. Writes restricted to this directory.

Started: 2026-10-27 23:40 PDT / 2026-10-28 UTC (tool date).

Checkpoint 1: controlling MASTER_INSTRUCTIONS.md read; relevant chapter discovery and primary-source retrieval in progress. Frozen PDF is the review baseline; mutable chapter 09 is parent-owned and will not be edited.

Checkpoint 2 (2026-10-28 UTC): frozen proof independently opened: 361 pages, 612 x 792 pt, SHA-256 66f8392d6b768de7af4695b3d93d70b48858eb75a944020dbcfa9f4d1768b758. Physical 141 / printed 123 confirms 245 GB divided by bidirectional 900 GB/s. Primary nccl-tests documentation and independent ring accounting support correction to 245/450 = 490/900 = 0.54444 s under the stated point-to-point model. Mutable chapter 09 remains parent-owned; its partially corrected source is not proof of correction in the frozen PDF.

Checkpoint 3: MPI 5.0 PDF, NCCL v2.32.3-1 header/implementation, oneCCL 2022.1.0 header/legacy plugin/transport implementations, PyTorch v2.9.0 docs and pinned torch-xpu-ops ProcessGroupXCCL implementation retrieved. oneCCL repository is not archived; deprecated torch-ccl bindings are a different project. Current oneCCL default branch is master-v2. Version 2022.1.0 was released 2026-08-15; the version string is not a release year. Intel/xccl endpoint returned 404; no standalone successor-library claim is supported. Open MPI v5.0.x docs expressly restrict CUDA-aware nonblocking reductions. No GPU execution attempted.

Checkpoint 4 (final worker delivery, 2026-10-28T00:22:14-07:00): mandatory prose-and-figures extension fulfilled inside this directory. Branch observed main; this directory remains untracked. No manuscript/config edits, delegation, commit, push or external publication performed.

## Separate deliverable states

- Text: COMPLETE AS UNAPPLIED CANDIDATE. research.md is Chinese; proposed-insertions.md contains substantive English mechanisms, worked examples, source citations, exact chapter/section anchors and cross-chapter boundaries. Whole candidate file including its editorial map contains 4,485 words. Parent owns Chapter 9 correction and all manuscript integration.
- Evidence: COMPLETE FOR SCOPED RESEARCH. claims.json contains 37 claims linked to 45 actually fetched primary sources, local quotes, raw hashes, retrieval times, release dates where established, version scope and limitations. sources.md resolves citation keys. Eight failed requests remain explicitly recorded and are not cited as successful evidence. oneCCL C-wrapper exception/missing-callback handling was inspected in tagged src/api.cpp; stale inherited plugin-doc wording is separately scoped.
- Calculations: PASS. independent_calculations.py passed seven CPU tests. Includes exact directional-byte derivation, FP16 illustration, round-by-round four-rank ring ownership/movement, TP/EP/FSDP payload examples and finite-precision order example. No accelerator/network measurements.
- Figure source: COMPLETE. figure-plan.md and generate_figures.py; two original editable SVGs plus vector PDFs. F1 explains SUM→reduce-scatter→all-gather and directional bytes. F2 separates backend/library/algorithm/runtime/transport/topology with dashed setup and possible GPU-aware MPI payload.
- Render: PASS. Intended width 6.1 in from actual US Letter style. F1 1830×1809, F2 1830×2092 at300 dpi; grayscale, detail and96 dpi actual-width previews present. Manifest records reproduction, captions, alt text, placements, prose/source/claim links and PNG hashes. Geometry checks report no failures; final PDF minimum font9.5 pt.
- Inspection: COMPLETE AS WORKER QA. Actual rendered whole-color, grayscale, detail and final actual-width previews inspected with vision_analyze; second self-critical review performed. Dashed-control rendering fixed; subtitle and crops clarified. figures/QA.md records checks, resolved findings and limitations. No remaining figure-local P0/P1/P2 observed after these checks; this does not certify publication readiness.
- Offline artifact integrity: PASS. verify_deliverables.py generated validation.json. Rechecked raw source SHA-256, exact stored quotes, prose citation/claim-anchor links, Markdown table column counts, figure files/hashes/dimensions/fonts and manifest links. The claims builder, seven-test calculation script and figure generator also completed together under &&, avoiding masked intermediate failures.

## Remaining parent-owned gates

PENDING: controlled treatment of post-2026-08-30 evidence; independent technical review; integration with parent Chapter 9 arithmetic/memory corrections; figure numbering/placement and caption fit; rebuilt complete-proof visual review; release certification. No manuscript or integrated PDF was produced here. No accelerator/library execution, cross-vendor performance ranking, wheel-compatibility certification or device-offload support matrix is claimed.

## Reproduce from repository root

    python3 research/collective-libraries-20261028/build_claims.py
    python3 research/collective-libraries-20261028/independent_calculations.py
    python3 research/collective-libraries-20261028/generate_figures.py
    python3 research/collective-libraries-20261028/verify_deliverables.py

Rendering requires PyMuPDF and Pillow (versions in manifest). These offline commands write only task-local derived artifacts; retrieval is not required for reproduction. Re-running generation cannot replace the recorded human/vision inspection of a changed figure revision.
