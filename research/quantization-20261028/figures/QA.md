# Quantization figures — actual QA record

Scope: original isolated research assets, not an integrated-book or publication-readiness audit. All work remains in research/quantization-20261028/. No figure has been inserted into the manuscript. Final intended placement is US Letter 8.5 × 11 inches, not 6 × 9.

## Build and actual-size basis

- Read current `render/latex/book.tex:7`: letterpaper. Read `render/latex/book.sty:61`: left/right margins each 1.2in. Exact Decimal arithmetic in generate.py gives 8.5 − 1.2 − 1.2 = 6.1in text width.
- Read existing print-sized pipeline guidance (`render/fig_ch2_pipeline.py:1–53`) and architecture drafting conventions. Use grayscale, thin borders, explicit arrows, a short label hierarchy and Liberation Sans. Current style and architecture file disagree about semantic colors; no semantic color mapping is introduced.
- Executed `python3 research/quantization-20261028/figures/generate.py`. Both renders succeeded. QF1 final PNG: 3660 × 3500px; QF2: 3660 × 2600px, both 600dpi nominal. Editable SVGs and the generator are present. PNGs are drawn from the same primitives as SVG, not screenshots or copied vendor art.
- Authored font sizes: 9pt minimum, 10pt section labels, 12pt titles at 6.1in. These values are checked from drawing records, rather than inferred from a resized preview. Actual sizes and pixel/DPI metadata are also checked by validate_deliverables.py.
- SVG XML is parsed in package validation. PNG production uses the original generator's Pillow raster path; an independent SVG-renderer test was not performed. Interpreting the SVG with another renderer still requires the specified font. The provided final PNG does not depend on font substitution.
- Whole previews are 1220px wide; Letter placement previews are 1275 × 1650px at 150dpi, with a 915px (6.1in) diagram canvas starting 180px (1.2in) from each side. Detail crops are explicitly crops, not standalone artwork.

## Programmatic checks actually run

See checks.json and validation.json for machine-readable results.

- All text ink bounds are inside their figure canvas. Pairwise text bounding boxes do not overlap. This check alone does not detect line/text collisions; visual review below supplied that missing check.
- Exact block arithmetic assertions: 32 × 4/8 = 16 B; MXFP4 16+1 = 17 B per32; common1D NVFP4 16+2 = 18 B per32, plus4B per tensor. Local totals are 0.53125/0.5625 B/value and4.25/4.5 bit/value. Full matrix/resource arithmetic is independently executed by independent_calculations.py.
- Payload/local-scale bar widths use the same18pt/B scale: 288pt payload,18pt for each local scale byte. Tensor-global text is an annotation, not a proportional bar. The figure explicitly disclaims physical byte ordering.
- All figure colors are grayscale. Dark text #222222 on the darkest background behind text #dddddd gives contrast11.7136:1, calculated from sRGB luminance. Borders are #444444; scale cells #777777 carry no overprinted text. Meaning is also conveyed by text and divisions, not color alone.
- Manifest paths, claim IDs, prose anchors, PNG metadata, SVG text counts and generated-file hashes are validated. Successful rendering is not used as a claim of semantic correctness.

## First actual whole-figure and detail inspection

Used the available vision_analyze tool on both whole previews and both detail crops. All four calls succeeded; vision was not blocked.

### QF1 findings and revisions

- [P1, resolved] The initial execution branches mixed a tensor-precision policy (“weight-only”) with arithmetic (“native FP4”) and dispatch outcome (“fallback”). Renamed the branches as execution implementations: native FP4 math, fused dequantization, and higher-precision reconstruction.
- [P1, resolved] Unqualified fan-out could imply an INT4 tensor could dispatch directly into native FP4. Added an explicit kernel-required runtime-layout stage, compatible-dispatch label, supported-combinations restriction, and no-compatible-kernel rejection. Fallback is explicitly not guaranteed.
- [P2, resolved] INT4 alone did not specify scales. Changed to “INT4 + scheme” and stated that scale type/grouping are explicit. Method text now says calibration guides error reduction rather than asserting identical AWQ/GPTQ optimization.
- Geometry observations: upper arrows enter the packed tensor inside the container; lower arrows terminate at their own execution boxes. Initial whole/detail inspection found no clipping or arrow/text collisions. The intentional detail crop excludes the parent portion of the diagram; that is not a full-image defect.

### QF2 findings and revisions

- [P2, resolved] The central payload divider crossed the aggregate NVFP4 payload label. Replaced that label with separate “16 values =8B” labels in the two halves.
- [P2, resolved] Clarified subtotal scope with “Local:”; removed the global-scale box that could be mistaken for another proportional bar; made both E4M3 scale cells the same fill.
- [P2, resolved] Letter-proof review identified residual scope ambiguity in the global-scale sentence and a callout using the scale divider as leader. Added “NVFP4” explicitly and replaced the leader with a bracket spanning both bytes. Retained explicit accounting-not-packing-order and overhead-exclusion notes.
- The first reviewers independently checked the displayed17B/32 and18B/32 arithmetic and the per-tensor global scale distinction. They did not establish execution performance or numerical quality.

## Second self-critical inspection and final recheck

Think HARD / second pass: inspected revised QF1 and QF2 whole previews and revised detail crops with vision_analyze (four successful calls). Separately inspected both Letter placement-proof PNGs (two successful calls). Following the final QF2 scope/bracket refinements, inspected its final whole preview and detail crop again (two successful calls).

- QF1 second whole review reported that both prior P1 semantic problems were resolved, and found no remaining concrete P0/P1/P2 issue. Its detail review confirmed the runtime-layout label, compatible-dispatch placement and all three downward arrowheads without clipping/overlap. Letter proof retained readable labels, complete arrows and clear margins at the intended relative page size.
- QF2 second whole/detail review confirmed that the payload divider no longer crosses text, the local/global distinction is correct, and there is no clipping. Its final whole/detail recheck confirmed the two-byte bracket, explicit NVFP4 global-scale scope, exact totals and no new collision. No remaining concrete P0/P1/P2 issue was identified in the final isolated asset.
- Both Letter proofs were inspected at the correct relative width on a page. The source-defined9pt minimum was verified programmatically. A vision preview cannot certify a physical point size or printer behavior by itself; that was not claimed.
- Read the evidence/claim definitions again for the conceptual boundary: MXFP4 is OCP1.0 here; NVFP4 is explicitly common1D, not TE2D training or a promise of GGML/NVIDIA checkpoint interchange. Neither panel ranks quality or speed. The three execution implementations are qualified examples, not exhaustive universally available branches.

## Remaining issues and limits

Observed defects in the final isolated assets: no remaining P0/P1/P2 defect identified by these checks. This is a bounded inspection result, not proof of absence of all defects.

Open integration/verification tasks:

- [P2 / integration pending] Parent must assign final figure numbers and validate captions, cross-references, line breaks and surrounding tables in the actual rendered manuscript. No integrated PDF was built or inspected here. Isolated6.1in proofs cannot establish page-break quality.
- [P2 / print verification pending] No physical print proof or printer-scale test. Do not reduce below6.1in without rechecking the resulting point sizes; the rendered-source9pt minimum assumes this width.
- [P2 / editable-source portability] The provided SVG uses Liberation Sans and explicit text lengths. Independent SVG-engine rendering and font-substitution behavior were not tested. Reproduce the supplied PNG through generate.py with the specified font, or verify another renderer before using its output.
- Not a figure defect: no hardware inference, checkpoint conversion, accuracy benchmark or load test was performed. These figures explain mechanisms and derived bytes only; they cannot substantiate deployment speedups, quality retention or SLO-goodput.

The parent will separately verify outputs and integration. Worker inspection does not establish publication readiness.
