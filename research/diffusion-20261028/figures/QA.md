# Figure QA — diffusion mechanisms and language-generation schedules

Scope: original research assets only. Digital visual inspection is complete. This is not a full-book pagination check, a physical print test, model execution, or a publication-readiness certification. The parent must verify integration independently.

## Build geometry and reproducibility

Read `render/latex/book.tex:7` (US Letter, 11pt) and `render/latex/book.sty:61` (1.2-in left and right margins). Available text width = 8.5 - 1.2 - 1.2 = 6.1 in. Follow the active build/style palette and CONTRIBUTING.md:163–165: memory/state blue, compute orange, redundant line/shape encoding. The older conflicting palette in design/book-architecture.md:222 was noted but not edited.

Reproduce from repository root:

    python3 research/diffusion-20261028/calculate.py
    python3 research/diffusion-20261028/figures/generate_figures.py
    python3 research/diffusion-20261028/validate_artifacts.py

The figure generator uses Python 3, Pillow, PyMuPDF, Inkscape and Liberation Sans. It reads its adjacent figure-data.json, not network data. Original editable SVGs, 400-PPI PNGs, vector PDFs, grayscale PNGs, whole-figure overviews, detail crops and Letter proof pages are produced inside this directory. The overview previews are downsampled inspection aids, not print deliverables. The print files are D1.png and D2.png; prefer D1.pdf and D2.pdf for vector insertion.

| Asset | Intended placement | Print PNG | Normal minimum font | Math subscript |
|---|---|---|---|---|
| D1 | 6.1 x 4.65 in | 2440 x 1860 px, 400 PPI | 10.08 pt | theta: 8.064 pt |
| D2 | 6.1 x 6.65 in | 2440 x 2660 px, 400 PPI | 10.08 pt | none |

## Deterministic checks actually executed

- Generator successfully invoked Inkscape for both PNG and PDF exports, twice after substantive revision and again after the final context-label spacing fix. Final commands exited 0.
- SVG XML parsed successfully. Rendered dimensions match width/height x 400 PPI exactly. PDF figure widths match the physical placement. Both proof PDFs are 612 x 792 pt US Letter, with figure left edge at 1.2 in and top at 1.0 in.
- Font measurements and conservative text bounds were computed. Final `geometry-checks.json` and `../validation.json` show zero text out-of-bounds and zero conservative text-text overlaps. An intermediate conservative overlap between the two context-box lines was resolved by increasing their baseline spacing from 16 to 18 SVG units; the final raster was inspected again.
- Actual vector-PDF text spans were independently checked against PDF page bounds: 38 spans for D1, 58 for D2, zero outside-page spans. This is a geometry check, not a substitute for raster inspection.
- All eight D1 process arrows were independently parsed: every black q arrow points right and every orange learned reverse arrow points left. D2 sequence arrows and repeat loops were checked in raster review.
- Both grayscale conversions contain visible dark content against white, and were inspected as complete figures. Question marks/MASK labels remain a redundant channel if fine hatching becomes faint in printing.
- Figure references, all eight prose anchors, all figure claim IDs, raw-source hashes and quote locations were checked by validate_artifacts.py. Final validation PASS: 41 claims, 5 benchmark records, 100 retrieval records including 99 successful byte-hash checks and one retained failed attempt; 98 source quotations checked. The failed dInfer main-branch lookup was resolved by the separately retained successful default-branch README.
- The worked arithmetic is illustrative, not a performance curve: 64 sequential block evaluations, 2,048 output-position evaluations, 28.672 TFLOP projection proxy, 256 MiB example logits. calculate.py and validation use independent expressions to check these results.

## Rendered inspection actually performed

The available vision tool (`vision_analyze`) succeeded. It was not blocked. The following are records of observed checks and revisions, not a claim that a reviewer can infer correctness from successful file creation.

### Pass 1 — whole-figure review

D1-overview.png: all q/p_theta directions correct; labels, tokens, hatching and flow-matching caveat readable; no clipping or overlap reported. Suggested conventional theta subscript. The generator was changed to render a real lowered theta subscript, then regenerated.

D2-overview.png: substantive issues were found. Orange active-block boundaries encroached on adjacent cells; the floating repeat arrows did not connect clearly to refinement; accepted IDs, finalized prefix state and inactive future positions were under-specified. These were treated as P1 clarity/semantic risks, not dismissed because the file rendered.

### Revision following pass 1

- Enlarged cell/block gaps and kept the dashed block boundary strictly between cells.
- Replaced floating loops with return arrows attached to unresolved intermediate regions; no loop attaches to the final completed snapshot.
- Introduced solid lower brackets for finalized prefix state, letters for accepted IDs, hatched question marks for unresolved active positions and unhatched hyphens for inactive future positions.
- Removed dashed recomputation enclosures from completed output snapshots.
- Clarified that the full-canvas dashed region marks recomputed output representations, not necessarily editable IDs, and makes no invariant-prompt-state assumption.
- Caption explicitly says AR snapshots include processing of the newest accepted token before its K/V are shown finalized. ID acceptance is not equated with immediate K/V creation.

### Pass 2 — self-critical whole/detail/grayscale/actual-size review

- D2-overview.png: no definite P0/P1 issue reported after revision. Remaining observations concerned the AR snapshot timing caveat and fine print strokes; the caption now makes the former explicit.
- D1-detail.png: individual q and p_theta arrows, subscripts, token text and hatching were readable. The tool noted that the crop excludes left-hand labels and MASK definition. That is intentional cropping of an inspection detail, not clipping of the delivered whole figure; the whole D1 and its Letter proof were separately inspected.
- D2-block-detail.png: active-block borders were between cells and brackets were separate. The loop arrowhead meets the dashed boundary intentionally. The tool asked for accepted-versus-finalized context that is outside this crop; full-figure review confirmed the bracket legend supplies it. Cropped detail alone is not used as a semantic acceptance test.
- D1-gray-overview.png: all q/p_theta arrows, both lanes, state labels and MASK notation distinguishable without hue. The text explicitly keeps flow matching distinct. No visible clipping. Fine hatching and theta subscripts were flagged for print sensitivity, not current unreadability.
- D2-gray-overview.png: no P0/P1 issue; requested color-independent bracket wording and an explicit hatch legend. Both were implemented. Bracket versus dashed outline remains distinguishable by shape and location.
- D2-letter-proof.png: complete figure inspected at the correct Letter placement. Title, panel C, legend and bottom clearance readable; no clipping. This is an actual-size digital proof, not a photographed paper print.

### Final asset reviews

D1-letter-proof.png: final digital review found no P0/P1/P2 defect; both lanes, theta subscripts, explanatory notes and caveats readable, arrows complete, no edge clipping.

D2-gray-overview.png after wording changes: final grayscale review found no P0/P1/P2 defect; hatching, brackets, outlines, loop direction, all labels and legend clear. Bracket/outline proximity was specifically checked and judged non-obscuring.

D2-letter-proof.png after the final +2-unit context-line spacing fix: final exact-asset review found all fixed-prefix/fixed-prompt/causal-prefix lines inside their boxes, no glyph clipping or overlap, complete legend, correct loop scope/directions, no P0/P1/P2 defect.

These observations were considered together with deterministic geometry rather than accepted blindly. In particular, crop omissions were not mistaken for whole-asset defects, and intentional loop-to-boundary connections were not removed as accidental collisions.

## Semantic self-review

D1: q is specified corruption; p_theta is learned reverse generation. The forward process is a training construction, not a requirement to corrupt an unknown answer during inference. Continuous state bars have no axes and are explicitly schematic, not probability bars, sourced data or benchmark curves. The categorical lane is explicitly one masked discrete construction. Flow matching is separately described, not relabeled diffusion.

D2: diagrams are examples, not universal schedules. Repeated full bidirectional evaluation can change representations of fixed IDs. Block-causal prefix reuse requires both a valid causal boundary and state finalized against the accepted contents. No exact ordinary-AR cache transfer is claimed for arbitrary dLLMs; approximate refresh, editing and uniform renoising remain implementation-specific. Repeated work, dependency depth and wall-clock speed are not equated. Future AR positions are not drawn as instantiated MASK tokens.

Text/asset consistency: proposed-insertions.md cites both PNGs and explains the cache and commitment distinctions. manifest.json contains captions, alt text, physical sizes, reproduction commands, related prose anchors and evidence IDs. All diagram states are [ILLUSTRATIVE], not model output measurements.

## Remaining issues and boundaries

[P0] None found in the final delivered assets.

[P1] None found in the final delivered assets. Initial P1 issues described above were revised and re-inspected.

[P2] Integration remains pending: final figure numbers, caption pagination, cross-chapter references and collision with surrounding manuscript content cannot be certified without parent integration and a full-book build. D2 is intentionally a substantial full-width figure; reducing its width would shrink 10.08-pt ordinary text and requires a fresh inspection.

[P2] Physical printer/paper reproduction has not been tested. Vector output and 400-PPI PNGs are delivered, grayscale digital checks passed, and redundant symbols preserve meaning if hatch strokes weaken. A physical proof is still useful for fine hatching and conventional small theta subscripts.

No unresolved drawing defect is being concealed by these boundaries. Neither a static source review nor visual figure QA establishes runtime compatibility, model quality, service reliability or benchmark reproduction.
