# Diffusion research delivery status

Overall: RESEARCH PACKAGE COMPLETE; PARENT INTEGRATION / PUBLICATION REVIEW PENDING.

Owner directory: /home/ubuntu/hermes-work/from-token-to-fleet/research/diffusion-20261028/
Scope: diffusion mechanisms and diffusion language models. No video/Wan product survey. All authored outputs stay inside this directory. No manuscript/shared-figure/configuration edits, additional delegation, commits or pushes were performed by this worker. Pre-existing unrelated working-tree modifications were left alone.

## Separate acceptance states

| Area | State | Deliverable / evidence |
|---|---|---|
| Chinese research synthesis | COMPLETE | research.md: mechanisms, releases, cache/resource/serving consequences, counterexamples, matched-quality protocol, chapter integration and cutoff handling |
| English developed book text | COMPLETE — candidate, not integrated | proposed-insertions.md: substantive prose, worked compute/memory examples, eight placement anchors, figure citations and source handoff. Validation reports 4,062 words including editorial notes/references; not an outline. |
| Primary-source / claim ledger | COMPLETE within stated evidence boundaries | claims.json: 41 claims including five condition-qualified benchmark records; source-manifest.json: 100 retrieval records, 99 successful retained-byte hash checks, one retained failed lookup subsequently resolved by corrected default-branch retrieval; source-index.md |
| Figure planning | COMPLETE | figure-plan.md: two necessary mechanisms, placement/composition, real build geometry and design guidance |
| Figure sources | COMPLETE | figures/figure-data.json, generate_figures.py, editable D1.svg and D2.svg; manifest.json carries reproduction commands, dimensions, captions, alt text, prose anchors and evidence IDs |
| Figure rendering | COMPLETE | two original 6.1-in-wide figures, 400-PPI PNGs, vector PDFs, grayscale PNGs and US Letter actual-size digital proofs. D1: 2440x1860 px. D2: 2440x2660 px. |
| Figure inspection | COMPLETE — digital whole/detail/grayscale/actual-size proof | figures/QA.md records successful vision inspections, initial defects, substantive fixes, second self-critical review, final exact-asset check and residual P2 production/integration boundaries. No final P0/P1 drawing defect found. |
| Artifact / evidence validation | PASS | validation.json; validate_artifacts.py checks 99 raw-byte hashes, 98 source quotations, benchmark field completeness, figure references/claim IDs, eight prose anchors, PNG geometry, PDF text bounds, arrow directions and arithmetic. Final run has no errors. |
| Model/API/engine performance testing | NOT PERFORMED | No weights loaded, model/API request, GPU kernel compilation, deployment launch or benchmark. Source-reported performance is not local measurement. |
| Manuscript integration / full-book PDF | PENDING — parent-owned | No insertions applied, no shared figure replacement, no final numbering/cross-reference/pagination certification. Standalone figure proofs do not establish whole-book readiness. |
| Physical paper print | NOT PERFORMED | Digital actual-size and grayscale inspections passed. Physical hatching/subscript reproduction remains a P2 production check. |

## Strongest findings

- Dense/MoE parameter allocation and AR/diffusion inference schedule are separate axes. Sequential rounds, all processed positions, attention work and commitment boundaries replace final-token count as the internal execution ledger.
- Both blanket cache claims are wrong: arbitrary bidirectional refinement does not preserve ordinary AR K/V invariance, but block-causal/encoder-context separation and implementation-specific approximate refresh support reuse.
- The illustrative block example reduces sequential evaluations to 64 while evaluating 2,048 output positions (28.672 TFLOP projection proxy for 7B active parameters). It is not a measured speedup or an equal-quality comparison. A 256-position / 262,144-vocabulary FP32 logits tensor is 256 MiB at batch one, before other live buffers.
- Vendor API and runtime support are distinct. At the pinned SGLang revision, Gemma4Renoise restrictions include quantized loading, radix caching, chunked prefill, pipeline/context parallelism and grammar requests; this cannot be overridden by vendor speed/precision claims for another runtime.
- DiffusionGemma is a source-verified open experimental release (2026-06-10). Mercury 3 is a source-verified closed vendor API launch (2026-10-19), outside the frozen August comparison. Neither fact certifies deployment quality or performance.

## Evidence and remaining gaps

Read: review/publication_v2_20261028/MASTER_INSTRUCTIONS.md, relevant manuscript sources, active build/style and contributor visual guidance; research model-release and serving skills plus figure rendering/inspection skill. Tool clock verified at start and again at 2026-10-28T00:03:56-07:00. Directory date is the assignment date; retrieval timestamps are preserved individually.

Primary evidence includes original papers, public model cards/configs, vendor releases/API docs and revision-pinned serving code. Missing benchmark revisions, hardware, precision, lengths, NFE and service conditions remain explicitly UNVERIFIED. No unsupported speed ranking is produced. Current downloaded versions do not certify historical August source contents.

Known source retrieval issue: inclusionAI/dInfer/main/README.md returned 404; official repository metadata identified the default branch and the correct README was fetched successfully. Failed discovery remains visible rather than being erased.

[P0] No unresolved final figure defect found.
[P1] No unresolved final figure defect found; initial outline/loop/state-encoding issues were corrected and re-inspected.
[P2] Parent must integrate, renumber, resolve bibliography/cross-chapter references and inspect the complete rendered book. No width reduction without fresh legibility review. Physical print proof remains outside this run.

## Reproduction

From repository root:

    python3 research/diffusion-20261028/calculate.py
    python3 research/diffusion-20261028/figures/generate_figures.py
    python3 research/diffusion-20261028/validate_artifacts.py

All three write only within this owned output directory. Network collectors are separate; rerunning them fetches potentially changed upstream content and is not required to reproduce figures or offline validation. Existing retained source bytes and hashes define this evidence snapshot.
