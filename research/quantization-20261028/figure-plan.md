# Quantization figure plan — unapplied research assets

## Geometry and design basis

Read `render/latex/book.tex:7` (letterpaper, 11pt) and `render/latex/book.sty:55–62,93–111`. The page is US Letter 8.5 × 11 inches. Left/right margins are 1.2 inches, so the available text width is 6.1 inches. The generator independently computes 8.5 − 1.2 − 1.2 rather than assuming a generic book size. Both figures are authored at exactly 6.1 inches, not enlarged thumbnails. At 600 dpi this is 3660 pixels wide. Body labels are 9 pt or larger; this is above the 8 pt minimum used by the existing print-sized pipeline figure (`render/fig_ch2_pipeline.py:37–53`).

Read the book architecture's binding drafting conventions (`design/book-architecture.md:220–224`) and the current pipeline figure design commentary (`render/fig_ch2_pipeline.py:1–38`). Apply a restrained academic diagram style: semantic boxes, explicit labeled arrows, no icons, no decorative textures, no miniature prose. The architecture document and current style disagree on semantic colors. Avoid asserting either conflicting color taxonomy: use grayscale throughout, with redundant text labels and borders. Use Liberation Sans, the current book heading sans face. Avoid a new illustration style and unsupported color semantics.

## QF1 — From quantization choices to an execution path

- Learning objective: distinguish an error-control method from a numerical representation, packed tensor layout, checkpoint container, and actual execution kernel.
- Mechanism: method selects quantized values/scales under a representation; packing places their bits into tensors; a container describes/stores those tensors; the runtime must load/repack them into a supported kernel. Execution may be native FP4, fused weight-only W4A16, or higher-precision fallback. These are alternatives, not a promised sequence or automatic performance ranking.
- Proposed placement: Ch7, after Table7-2 explanation and before §4; prose anchor `q-layers`. Ch11 refers back rather than duplicating the diagram.
- Composition: two independent input boxes (method and representation) feed one packed-tensor box within an explicitly labeled container enclosure. A load/repack arrow reaches a distinct kernel-required runtime-layout stage, then compatible dispatch reaches three execution implementations. Rejection is explicit if no compatible kernel exists; fallback is not guaranteed. Container examples are GGUF and safetensors, not a claim that every shown method/encoding combination has an interoperable export.
- Why necessary: a table of names alone does not show why an AWQ recipe and an NVFP4 representation can coexist, why a container is not a dtype, or where a supported checkpoint can fall back to another arithmetic path.
- Claims: Q01–Q06, Q09, Q12, Q19–Q21, Q28, Q32. Evidence URLs and pinned revisions are in claims.json/source-index.md.

## QF2 — Four-bit values, different scale bills

- Learning objective: expose the byte cost of block scales without implying equal encoding, quality, or throughput.
- Mechanism: show the same 32 logical values as 16 bytes of packed E2M1 payload. MXFP4 adds one 8-bit E8M0 scale; common 1D NVFP4 adds two 8-bit E4M3 local scales and a separate FP32 tensor-global scale. Neither representation uses an affine zero point in this comparison. The NVFP4 global scale is shared over the tensor, not appended to each 32-value block.
- Proposed placement: Ch7 proposed block-accounting subsection, prose anchor `q-block-bytes`, immediately after QF1's accompanying explanation.
- Composition: matched horizontal payload bars with explicitly separated scale rectangles, labels above/below rather than crammed into 1-byte cells. A separate NVFP4 tensor-level global-scale annotation prevents confusing per-tensor and per-block overhead; a bracket spans the two local scale bytes. Only data/local-scale bars are proportional to byte count. Notes exclude padding, duplicate scales, headers, and high-precision exceptions. No measured curve or invented data.
- Why necessary: nominal four-bit storage hides the exact recurring scale overhead, while the detached global-scale annotation explains why small and large tensors have different amortization.
- Claims: Q09–Q15, Q31; independent arithmetic in independent_calculations.py and figures/generate.py. MX uses OCP1.0 terminology to respect the book's August cutoff. NVFP4 common 1D definition is not generalized to TE 2D training or GGML's distinct block implementation.

## Required verification

Generate editable SVG, print PNG, grayscale PNG, actual-size Letter proof pages, a whole-figure inspection image and a detail crop. Run text-bounds/overlap/contrast checks from the shared drawing records; inspect both entire figures and details using the vision tool. Record the real observations and limitations in figures/QA.md. A print-sized proof is not a physical print proof or an integrated manuscript-page review. No manuscript build or publication claim is authorized.
