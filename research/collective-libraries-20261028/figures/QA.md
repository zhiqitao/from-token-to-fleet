# Figure QA — actual checks and remaining integration boundary

Final assets: CCL-F1-reduction and CCL-F2-layers. Research-only candidates; this is worker QA, not independent publication certification. Parent inspection of the rebuilt book remains required.

## Physical and design checks

- Read the book architecture guidance, existing communication-figure generator conventions, and book.sty. Frozen proof is US Letter 612×792 pt. Style margins are 1.2 in left/right; available width is 6.1 in. This is not a 6×9 template.
- Authored vector width is 439.2 PostScript pt. No wide-source downscaling or bbox-tight rescaling is used. Final PDF page widths measured by PyMuPDF are 439.1999817 pt.
- F1 height: 434 pt (6.0278 in), 300 dpi raster: 1830×1809 pixels. F2 height: 502 pt (6.9722 in), raster: 1830×2092 pixels. Captions are supplied in manifest, not baked into a tiny footer.
- Minimum actual PDF text span measured: 9.4999990 pt for both (floating-point representation of 9.5 pt). Main labels are 10–11 pt and titles 12.5–13 pt. This verifies the font-floor concern raised in the final preview review; it is not inferred solely from the SVG text layer.
- Book palette: memory/structure blue #27408B, compute orange #E67E22, constraint/setup red #C0392B; dark text on pale fills. Meaning also uses numbered headings, explicit labels, positions and solid versus segmented lines, not hue alone.

## Reproduction and deterministic checks

Command from repo root:

    python3 research/collective-libraries-20261028/generate_figures.py

The generator emits editable self-contained SVG, vector PDF, 300 dpi PNG, grayscale PNG, 96 dpi actual-width preview, detail crops and manifest. Dependencies are Python, PyMuPDF and Pillow; exact versions are in manifest. Only the assigned directory is written.

Successful execution returned zero geometry failures for both figures. Checks include conservative text bounds, text/text collisions, and exact slab intersection of connector segments with text rectangles. Shape containment is intentional and is not counted as overlap. This test is geometric support, not a substitute for rendered inspection.

A raster check of the final grayscale control corridor sampled the x=8 pt path between y=110–210 pt. It found 251 dark pixels and 157 white pixels, confirming visible dash gaps in the rendered raster. This is important because the first SVG converter rendering did not visibly preserve stroke-dasharray as intended. The generator now renders actual separate segments rather than relying on dash styling.

The independent CPU calculation suite passed seven tests, including a round-by-round four-rank ring simulation. That test confirms the pictured ownership after reduce-scatter, the clockwise neighbor order, all-gather replication, six payload bytes sent/received per phase and twelve per direction overall. Python struct binary16 checks confirm that all depicted small integer-valued FP16 inputs/results are exactly representable. It does not execute NCCL or oneCCL.

## Rendered whole-figure and detail inspection log

The vision_analyze tool was successfully used on actual rendered PNGs, not just source or PDF text extraction.

### F1 — reduction/data movement

First whole-color review: passed numerical SUM, phase-boundary states, 8 B input, 6 B/phase/direction, 12 B sent +12 B received, ring wrap arrow, clipping and readability.

Self-critical source pass: changed int16 wording to FP16. This avoids implying that NCCL supports an int16 dtype merely because an abstract semantics example uses two-byte integers; all small values and sums remain exactly representable. Payload counts are unchanged.

Second whole grayscale review: no P0/P1/P2 observed. The reviewer independently read all inputs and outputs, verified the three rounds per phase and the R3→R0 wrap arrow, and found no loss of meaning without color.

Detail review: the first crop intentionally removed parts of adjacent panels and the reviewer correctly flagged those crop edges. This was not treated as clipping of the full asset. The crop was remade to include the full three-phase-panel region; reinspection found no glyph clipping, collisions or numerical defects within those panels.

Final actual-width preview review: pass. This was the final FP16 revision at 6.1 in /96 dpi, in addition to the 300 dpi whole image and detail inspections.

### F2 — layered payload/control path

First whole-color review: no P0, but a P1 was raised because setup connectors appeared solid rather than dashed, weakening grayscale distinction. The rendering path was corrected to explicit line segments. Color distinctions between layers were not accepted as a required semantic dependency: numbered headings and explicit category labels already carry the categories.

Second whole grayscale review after correction: no P0/P1/P2 observed. Control paths visibly segmented; all six inter-layer payload arrows solid and downward; both setup arrows inward into the library rows. MPI appears in setup, eligible payload transport, and an explicit GPU-aware note, not as CPU-only.

Detail review: the intentional crop excludes the full legend and lower runtime/hardware rows, so observations about absent lower layers/legend were not treated as full-figure defects. The oneCCL subtitle was nevertheless tightened from “Plugin / selected algorithm” to “Selected collective algorithm” to avoid mixing extension mechanism with algorithm choice. The final crop was bounded between complete visible rows. Reinspection found no clipping, overlaps or confusing arrow direction in the visible boxes.

Final actual-width preview review: no P0/P1. The reviewer raised only a P2 verification item: small labels/footer near the 9.5 pt floor should be measured in the master. Master PDF measurement returned 9.4999990 pt minimum, closing that item. “Payload / device execution” is a conceptual layered relationship, not an exhaustive function call graph or a claim that every named device supports every path.

## Second self-critical review and remaining issues

Closed findings:

- P1 dashed-control encoding: fixed in actual raster by explicit segments; verified in grayscale and by pixel sampling.
- P2 plugin/algorithm subtitle ambiguity: wording fixed; final detail reviewed.
- P2 font-floor uncertainty: actual master measured at 9.5 pt.
- Crop-boundary observations: inspection artifacts remade; full assets were never cropped at those locations.

Remaining figure-local defects observed: P0 none, P1 none, P2 none after the checks above. This is a scoped worker observation, not an assertion that the figures are publication-certified.

Remaining integration gates:

- Parent must verify actual placed width, figure height plus caption fit, page breaks, final cross-references, and auto-numbering in a rebuilt complete proof. No integrated book PDF was created by this worker.
- Current named implementation paths are a 2026-10-28 research snapshot. They must not be silently inserted into the frozen 2026-08-30 evidence envelope.
- No accelerator/network benchmark, cross-vendor performance comparison, or released-wheel compatibility matrix was executed. F1 is an original analytical mechanism example, not a measured trace. F2 is a conceptual architecture figure, not a hardware support guarantee.
