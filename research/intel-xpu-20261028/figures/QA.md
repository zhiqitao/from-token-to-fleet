# IX-F1 — Render and inspection QA

Scope: one original proposed figure and its isolated US Letter placement proof. This is not a full-manuscript visual audit, a physical print inspection, an independent technical benchmark, or publication certification.

## State

- Figure source: COMPLETE — figures/generate.py and editable figures/intel-backend-paths.svg.
- Render: COMPLETE — color PNG, grayscale PNG, vector PDF, detail crop and isolated Letter placement proof.
- Whole-figure inspection: PERFORMED with the available vision tool, including the final regenerated grayscale raster.
- Detail inspection: PERFORMED on the actual rendered GPU/Gaudi runtime/hardware crop and the final qualification-gate crop.
- Actual-size placement inspection: PERFORMED with the final US Letter placement proof at 6.1-inch figure width.
- Second self-critical review: PERFORMED in this run after the first visible defect was fixed. Repeated vision calls are additional inspections, not an independent hardware validation or a different research agent.
- Remaining observed figure defects: [P0] none; [P1] none; [P2] none in the final inspected assets.

## Print dimensions and deterministic checks actually run

Input style: render/latex/book.sty line 61 sets 1.2-inch left/right margins. The verified baseline page is 8.5 × 11 inches. Available width: 8.5 − 1.2 − 1.2 = 6.1 inches.

Generator output and finalization checks:

| Check | Actual result |
|---|---|
| Figure intended size | 6.1 × 6.3 inches |
| Color PNG | 1830 × 1890 pixels |
| Effective resolution | 300 ppi at intended size |
| PDF page width | 6.099999745686849 inches, floating-point conversion tolerance |
| Minimum source label size after placement | 10.08 pt |
| Minimum PDF text-span size | 10.079999923706055 pt, floating-point conversion tolerance |
| Labels | 49 |
| Downward connectors | 12: nine solid dependencies, three dashed qualification links |
| Text/connector bounding-box intersections | 0 |
| Text inside its containing card | Assertion checks passed |
| Dark text/white contrast ratio | approximately 15.45:1; card fills also remain light |
| Nonblank content and edge clipping | Pixel-content bounding box (33, 38, 1797, 1875) inside the 1830 × 1890 canvas |
| Caption, alt text and evidence links | Present in figures/manifest.json |
| Asset SHA256 | Checked against the manifest by finalize.py |

Geometry checks verify dimensions, estimated/actual font metrics, card containment, and vertical line/label separation. They do not prove that the SVG renderer displayed every glyph. Raster vision inspection supplied that separate check. The Letter page proof is 150 ppi for inspection; the delivered figure is 300 ppi and the optional PDF is vector. The proof raster is not the final print asset.

## First pass: actual defect and correction

The first whole-figure inspection found no clipping, overlap or unreadable labels. It identified a [P2] semantic ambiguity: the same solid connector style represented stack dependencies and entry into a qualification gate.

The subtitle and final connectors were changed to distinguish solid dependency links from dashed qualification links. The first regenerated SVG used stroke-dasharray. Subsequent grayscale and Letter-proof inspections found that all three qualification connectors still looked solid; one inspection graded the legend mismatch [P1]. This was a real renderer discrepancy, not an inference from the SVG text layer.

The generator was corrected to draw explicit separated line segments instead of relying on stroke-dasharray. The figure, grayscale asset, detail crop, vector PDF and Letter proof were regenerated. This correction was made in the generator, not painted into the PNG.

## Final second-pass inspection

The vision tool inspected:

1. Final whole grayscale figure: all three qualification connectors visibly dashed; nine dependency arrows visibly solid; complete text; no clipped labels; separate accelerator paths; no observed P0/P1/P2.
2. Final color detail crop, original coordinates [15, 1430, 1810, 1830]: each qualification connector has separated dash segments and a downward arrowhead; all four gate text lines fit; no observed P0/P1/P2. The intentional crop through hardware labels is not a full-figure defect.
3. Final Letter placement proof: at the intended width, labels readable without enlargement, dash distinction visible, boxes/arrows/caption separated, no clipped content; no observed P0/P1/P2. Blank space below the isolated figure is not a defect in the full book, which has not been rebuilt here.

Semantic self-check: Intel GPU offers a framework XPU path or an engine-native SYCL alternative. Gaudi hpu and HCCL are separate from GPU XPU. The client NPU route is OpenVINO-based and not the integrated GPU. The common gate explicitly qualifies the complete configuration, not the hardware alone. It includes memory, operators/cache, correctness/isolation, collectives when used and a measured SLO. No arrow represents measured performance. No color-only distinction is required to understand the figure.

## Exact final inspected raster identities

- intel-backend-paths.png: 41848f684b8f527237a3d3463bf939343434847d6f573bb544bc280caa29d358
- intel-backend-paths-gray.png: e94c29addedf01840139ad3d92cd98c18ae52b7b67f9ea34dbe797ef5057e189
- letter-placement-proof.png: 6d558b58951e6c59e1815dcd473614cc239ab29091339b9362549901d464fc8a

## Remaining integration and verification boundaries

No observed figure-local P0/P1/P2 remains. The following are NOT VERIFIED, not claimed passes:

- Full-manuscript insertion, final figure numbering, page breaks, caption placement and cross-references.
- Actual printed paper proof, ink behavior and physical reading-distance inspection.
- Font embedding/legal preflight in a final publication PDF. The main print asset is the 300 ppi PNG; the optional vector PDF/isolated proof is not a certified book-production PDF.
- Device/driver/kernel/model execution, numerical correctness, runtime support and SLOs. The gate describes required evidence; it does not report any configuration as having passed.

Reproduction from the repository root:

    python research/intel-xpu-20261028/figures/generate.py
    python research/intel-xpu-20261028/build_registry.py
    python research/intel-xpu-20261028/finalize.py

No package installation, shared configuration edit or manuscript rebuild was needed. Dependencies used: installed PyMuPDF and Pillow. Local measurements and manifests remain inside this assigned research directory.
