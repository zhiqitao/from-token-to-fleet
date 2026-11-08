# Parent acceptance and corrections — LFM3 investigation

## Verified

- Research report, 32-claim ledger, source index, raw evidence, insertion proposals, SVG/PDF/PNG and QA files exist and are nonempty.
- Fresh GET of the official HF configuration returned HTTP 200 and exactly matched the saved config bytes. It lists 24 layers: 13 convolution, 5 sliding attention, 6 global attention; 4 KV heads, head dimension 128, BF16 config, sliding window 256.
- Independently recomputed raw BF16 global-layer KV: 12,288 B/token = 12 KiB/token. At 131,072 tokens: 1,610,612,736 B (1.5 GiB). At 262,144 tokens: 3,221,225,472 B (3 GiB). Five retained 256-token SWA windows: 2,621,440 B (2.5 MiB), assuming runtime cropping.
- Observed model code uses a fixed convolution state and accepts wide-kernel buffer sizes 6 or 7; kernel width alone does not establish a universal 6-token allocation.

## Corrected before acceptance

1. Removed an unsupported inference that 256K context fits a ~1 GB device because quantized weights are ~1 GB. KV, weights, convolution state, allocator/workspace and runtime reserves are distinct terms.
2. Reclassified the vendor's 1.6 GB figure as vendor-reported, not confirmed vendor-measured.
3. Replaced universal absence assertions for technical report/GitHub repository with bounded search conclusions.
4. Corrected the prose layer-sequence explanation and the per-layer versus five-layer SWA accounting.
5. Made SWA memory bounds conditional on runtime cache cropping; avoided calling a stateful convolution categorically non-recurrent.
6. Corrected the proposal's broken `../report.md` sibling references.
7. Repaired real figure clipping and legend overlap. Added source-specific `figures/regenerate.py`; two runs passed 52 object-bound checks, zero same-baseline text collisions, min 8.5 pt and zero Type3 fonts. Parent visual reinspection confirmed complete text endpoints and no overlap. See `figures/parent_geometry.json` and the superseding section in `figures/QA.md`.

## Scope and next integration boundary

This accepts the corrected architecture/state mechanism as a research candidate, not all 32 claims as independently validated. Benchmark tables remain source-reported; no inference/benchmark was run. Search absence does not prove nonexistence of an official report. Runtime compatibility is not established by a model-card support list. The standalone diagram is not yet a built-book figure.

Any insertion must remain an explicitly dated post-2026-08-30 supplement. Prefer one substantive memory/architecture explanation and a short pointer over repeating a product survey in five chapters. Do not silently add LFM3 to the frozen August comparison. Publication approval remains open.
