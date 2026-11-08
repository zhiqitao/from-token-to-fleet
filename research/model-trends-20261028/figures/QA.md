# Figure QA — recent model trends

Inspection date: 2026-10-28 UTC. Scope: original research figures and isolated placement proofs, not the integrated book PDF. The worker did not edit or rebuild the manuscript. This record distinguishes measured geometry, image-tool observations, and unverified physical production.

## Reproduction and objective checks

From the repository root:

    python3 research/model-trends-20261028/figures/generate.py
    python3 research/model-trends-20261028/figures/verify.py
    python3 research/model-trends-20261028/validate.py
    python3 -m py_compile research/model-trends-20261028/figures/generate.py research/model-trends-20261028/figures/verify.py

The generator successfully executed Inkscape SVG-to-PNG and SVG-to-PDF rendering. Pillow supplied text metrics and grayscale/crop generation; PyMuPDF supplied vector-text inspection and Letter placement proofs. The installed `fitz` alias produces a deprecation warning but did not prevent successful execution. No external model code was executed. `verification.json` contains the executable checks and final asset hashes; `geometry-checks.json` contains individual label bounds. Reproduction requires the dependencies and font named in manifest.json; byte-identical PDF metadata across separate runs is not promised.

| Check | MT-1 history state | MT-2 depth execution |
|---|---|---|
| Intended physical size | 6.1 × 3.95 inches | 6.1 × 4.54 inches |
| PNG pixels | 2440 × 1580 | 2440 × 1816 |
| Effective raster resolution | 400 PPI | 400 PPI |
| Vector width | 439.2 PDF points | 439.2 PDF points |
| Minimum placed text | 9.36 pt | 9.36 pt |
| SVG/PDF label bounds | PASS | PASS |
| Pairwise text-label collisions | none | none |
| Successful SVG/PNG/PDF generation | PASS | PASS |
| Figure reference in English prose | B, once | A, once |
| Evidence IDs | Q02, Q05 | R01–R05 |

Text width is established from current `book.tex` Letter format and `book.sty` 1.2-inch side margins: 8.5 − 1.2 − 1.2 = 6.1 inches. The isolated proof pages are 612 × 792 PDF points. The proof raster is a digital page-view approximation, not a calibrated physical display. SVG typography uses 100 coordinate units per inch; 13-unit type becomes 9.36 pt. Linework is vector; standard 1.3-unit outlines become approximately 0.94 pt. No artwork is scaled below its specified width in the proofs.

Measured minimum text contrast is 7.46:1, including the inactive gray pass label against white. Minimum tested colored-outline contrast against the associated pale fill is 4.76:1. Roles remain named by text, positions and line style; legends do not require hue. Contrast ratios are mathematical checks, not press/paper certification.

## Whole-figure, detail and grayscale inspection actually performed

The available `vision_analyze` tool successfully inspected these rendered assets during this run:

- Both `*-letter-proof.png` pages, first review and revised self-critical reviews: complete artwork, intended-width context, hierarchy, caption clearance and visible arrow topology.
- `mt-1-history-state-detail-top.png`: token inputs, update/state labels, previous-state routing, arrowheads, and the complete successive-snapshots note. The final crop bounds retain that note and stop before the lower heading rather than leaving a partial heading at the crop boundary.
- `mt-2-depth-execution-detail-bottom.png`: actual-stop bypass, inactive pass 3, fully executed post-hoc lane, selection labels and the full legend.
- Both complete `*-grayscale.png` figures: readable labels and outlines, non-hue semantics, inactive-pass distinction and complete legends.
- MT-1 Letter proof again after expanding key/value (KV) in the lower heading: the longer heading fit without collision and all four requested rating dimensions passed.

The initial detail crop cut descenders in MT-1's explanatory note at its artificial crop boundary. The original complete artwork did not clip that note. Crop bounds were corrected; subsequent detail inspection confirmed complete descenders. Whole-artwork bounds and vector-text checks independently pass.

## Findings and corrections, including second critical review

### MT-1

1. Initial [P2]: KV groups were left-aligned while count labels were centered. Corrected the geometry so each complete group is centered on its token column. The executable check verifies centers exactly 130, 310 and 490 source units.
2. Initial [P2]: successive recurrent-state boxes could be mistaken for jointly retained history. Added “Successive state snapshots, not jointly retained history.” The diagram represents separate layer groups, not a recurrent state growing into full-attention KV.
3. Initial [P2]: a color-only legend was weak in grayscale and “state flow” alone did not cover token inputs. Replaced it with role-based wording and explicit token-input/state-flow semantics. Complete grayscale inspection found all roles and outlines understandable.
4. Review suggestion [P2]: expand KV for a newcomer. The lower heading now says “key/value (KV) history”; final Letter-proof review confirmed fit and readability.
5. The second image review estimated a residual 5–10-pixel group offset. This was not accepted as a measured defect: exact SVG extents and group-center assertions establish the corrected centers. A later whole-image review confirmed clean alignment.
6. Some whole-page image descriptions incorrectly described the inter-token arrow as originating at the compute box. The SVG path and dedicated high-resolution review show the actual route: state-box right edge → upward elbow → next update's left edge. No source change was made to implement that already-present route. The three repeated “fixed-size state” labels are intentional pedagogical reinforcement, not an unresolved defect.

Positive rationale: the constant-sized recurrent snapshots and growing token-indexed cache are aligned in time but separated by layer group. The note prevents a false aggregate-memory interpretation. The caption explicitly disclaims measured ratios.

### MT-2

1. Initial [P1]: outer dashed weight branches started outside the shared-weight box. Widened the parameter box so all three branch origins meet it. Both vector checks and revised vision reviews confirm all three connections.
2. Initial [P2]: a solid border beneath an overlaid dashed border weakened the unexecuted-pass treatment. Removed the solid underlying outline. The inactive pass now has one dashed gray border, a readable label, no execution connector, and an explicit “not executed” note.
3. Initial [P2]: “dashed rail” did not describe the actual downward connectors and could confuse weight reuse with the inactive node. The legend now distinguishes dashed arrows (weight reuse) and dashed box (not executed).
4. Grayscale [P2]: the amber exit legend referred to a hue absent in grayscale. Replaced it with labeled exit/selection wording. Final complete grayscale inspection reported no remaining defect.

Positive rationale: one parameter inventory is visually distinct from multiple core executions and iteration-history objects. The lower comparison demonstrates omitted work versus post-hoc selection without inventing a speedup or quality curve. The caption states that the pass-2 exit is illustrative and not an Ouro result.

## Final ratings after corrections

| Figure | Technical integrity | Print readability, digital approximation | Visual design/composition | Pedagogical contribution |
|---|---|---|---|---|
| MT-1 | PASS | PASS | PASS | PASS |
| MT-2 | PASS | PASS | PASS | PASS |

These are worker-side digital candidate ratings. They do not establish publication readiness. The complete figure images, detail views and grayscale checks were inspected, not merely generated. The second self-critical review explicitly reconsidered topology, state identity, omission of work, confidence/quality assumptions, type size and label padding.

## Quantitative and semantic validation

- MT-1 is a mechanism schematic, not a memory-proportional chart. Three cells mean three token positions, not three layers or a measured ratio. Qwen's full-attention component is derived separately: `2 × 16 × 4 × 256 × 2 = 65,536 bytes/token`; at 131,072 / 262,144 tokens this is 8 / 16 GiB. Recurrent state, vision state, allocator/workspace and replication are excluded. Data and executed arithmetic are retained.
- MT-2 depicts the separate-iteration-cache case; it does not assert that every shared-depth model uses that layout. Cache sharing and prefill/decode policies require separate evidence. R05 supports the particular static-code distinction, not a runtime benchmark.
- The prose's `C + rF` example is explicitly illustrative. Inputs C=1, F=2, r=4 versus 3 produce 9 versus 7 work units. Core-only work falls 25%; total work falls 2/9. No hardware elapsed-time reduction is inferred. The figure's three passes and exit after pass 2 use a different illustrative index solely for readability.
- MoE selection, speculative drafting, external agent loops and Ornith training improvement are not relabeled as internal shared-depth execution. The figures do not rank vendors or imply a universal frontier-model shape.

## Remaining issues and acceptance boundaries

- [P0] None observed in delivered candidate text/figure assets.
- [P1] None observed in delivered figure topology, label geometry or digital readability after corrections.
- [P2] No unresolved concrete artwork defect. Printer-dependent fine-line, paper/ink and physical reading-distance behavior remain unverified production risks, not silently passed checks.
- NOT VERIFIED: physical hardcopy at 100%; calibrated display size; final integrated manuscript page breaks, caption binding, cross-reference numbering, EPUB layout, final press profile and independent parent acceptance.
- NOT PERFORMED: model inference, reproduced performance/quality benchmark, serving-engine compatibility certification or baseline full-PDF audit.
- Existing primary-source uncertainties remain in model-trends-research.md and claims.json. Producing these mechanism illustrations does not resolve them or justify promoting unverified model-specific claims.
