# Figure QA — original video/Wan candidates

Inspection date: 2026-10-28 UTC. Scope: standalone original assets, not manuscript pages. No publication-readiness certification. Both figures are original programmatic SVG, not copied vendor art.

## Build and physical-size verification

- Actual style read: `render/latex/book.tex:7` declares US Letter; `render/latex/book.sty:61` sets left/right margins to 1.2 in. Tool calculation: 8.5 − 1.2 − 1.2 = 6.1 in available text width.
- Design guidance read: `design/book-architecture.md` §3/§5/§6, semantic palette in `book.sty:104–112`, existing print-native `render/fig_ch7_budget.py` at 6.1 in. An older render review prompt mentions 6×9 and 258 pages; those stale dimensions/counts were not used.
- Renderer actually executed: Inkscape 1.4.3 (0d15f75042, 2025-12-25), SVG → PNG at 350 dpi. Reproduction: `python3 research/video-generation-20261028/figures/generate_figures.py` from repository root.
- Editable source: SVG text/shapes and `generate_figures.py`; `figure-data.json` contains the worked geometry and evidence IDs. Manifest stores paths, captions, alt text, anchors, commands, dimensions and PNG hashes.
- Minimum label size is 13 SVG units at 100 units/in = 9.36 pt at full 6.1 in width; title is 12.24 pt. Liberation Sans is installed and used by Inkscape. PNG metadata reads approximately 349.9866 dpi because of pixels/metre quantization; render setting is 350 dpi.

| Asset | SVG intended size | Final PNG | All nonwhite ink bbox (pixels) | Actual-size proof |
|---|---|---|---|---|
| `video-latent-work` | 6.1 × 6.0 in | 2135 × 2100 | (32,37)–(2103,2047) | 150 dpi proof, 915 px wide |
| `wan-noise-experts` | 6.1 × 3.95 in | 2135 × 1383 | (60,37)–(2075,1330) | 150 dpi proof, 915 px wide |

Nonwhite ink does not touch the canvas edge. SVG has no content-clipping mask. `geometry-QA.json` records actual shaped-text bounds from Inkscape, not a string-length estimate. Both figures have zero text outside canvas, zero text/text intersections, and zero arrow-segment/text intersections using exact slab intersection rather than endpoint sampling.

## Raster, grayscale and legibility checks actually performed

1. Opened generated PNGs with Pillow and checked dimensions, nonblank ink bounds, and DPI metadata.
2. Inspected initial whole-figure 150 dpi proofs through the available vision tool at a declared 6.1 in print width.
3. Inspected initial denoising and expert-bank raster detail crops through the same tool. Natural connector continuation beyond crop edges was not mistaken for full-canvas clipping.
4. Corrected the initial whole-figure P1: the legend said `Solid: evolving state` although prompt preprocessing arrows were also solid. Final legend is `Solid: data/state flow. Dashed: denoiser conditioning.`
5. Also clarified Wan2.2 identity, latent axes, only-one-expert execution, resident wording, and checkpoint-to-stage arrow origins. Removed the overstrong claim that whole-clip state alone sets admission. Regenerated all SVG, color/gray PNGs, proofs, detail crops, manifest and geometric results.
6. Inspected each final whole figure in grayscale and each final color detail crop through vision. The final detail reviews found no P0/P1 visual defect. The whole-figure reviews confirmed visible labels, correct arrowheads, the ≠ glyph, unclipped loop, and useful grayscale contrast.
7. Checked quantitative text contrast in code: ink #1A1A1A against white 17.404:1, pale memory fill #F1F4FA 15.797:1, pale compute fill #FFF5EB 16.172:1. Fill colors are not required to decode state/conditioning or resident/active semantics; words, position and line styles preserve meaning.

These checks are screen/raster/geometry inspections at declared print scale, not a physical press proof. Actual final book placement has not been generated here.

## Second self-critical semantic review and evidence adjudication

### Figure V1

- Correct model is dense Wan2.2 TI2V-5B, not A14B. Its official config sets VAE stride (4,16,16), z=48, patch=(1,2,2), 30 layers, 24 heads, dim=3072. Thus H=704 → H_l=44 and W=1280 → W_l=80. N=31×22×40=27,280. Calculations were executed, not inferred from the picture.
- One final grayscale vision response incorrectly substituted older/A14B spatial stride 8 and called the figure's shape a P1. This was rejected against the exact 5B configuration and HF VAE config, not accepted as a numerical correction. A final detail inspection with the verified 5B source scope confirmed the printed numbers and no visual defect. Source-based resolution: VG005–VG006/VG024–VG025.
- Initial noise is FP32 in the inspected code. The figure does not say all operations or activations are FP32. BF16 payload arithmetic remains separately hypothetical in the prose.
- The optional I2V branch is visibly separate; the numerical worked budget is T2V. No native audio branch is implied.
- The right loop returns into the denoiser. The downward path reaches VAE decode only after the latent trajectory. `50 steps × 2 CFG branch evaluations` belongs to this upstream loop, not every distilled/cached implementation.
- Footer does not claim that splitting N is free or universally supported; communication is explicit. Peak residency and all other stages are explained in the prose, not compressed into an inaccurate figure budget.

### Figure V2

- Both experts resident on GPU is explicitly an assumption. About 27B total and about 14B active are the official rounded descriptions. No exact per-checkpoint parameter count or proportional area encoding is invented.
- A final grayscale vision response suggested reconciling 27B versus 2×14B by adding a guessed per-expert range. This was rejected: the source itself gives rounded total/active counts. Caption and prose explicitly state the rounding. The final detail review confirmed that the image makes no exact 14B+14B assertion.
- Downward dashed links originate at their checkpoint borders; the solid horizontal arrow means high-to-low-noise stage progression, not running both experts every step.
- Equal-sized stage boxes are schematic. Caption explicitly disclaims equal timestep counts/durations. Offload can change residency but adds transfers.
- This figure is not the dense 5B model; the prose and caption keep those subjects separate.

## Severity and remaining limitations

[P0] None identified in the final standalone assets by the performed checks.

[P1] No unresolved standalone clipping, legibility, label-collision or source-verified semantic defect. This does not close integration checks: final page width, figure/caption pairing, numbering, page breaks and actual placed font size remain PENDING for the parent. They were not examined here.

[P2] No unresolved standalone raster defect after the parent-review revision below. Dashed blue shafts with black arrowheads and border-terminating arrows remain intentional, readable design choices. The previously unlabeled V1 loop is now labeled explicitly. Physical grayscale/press quality and any reduction below 6.1 in require a new placement/legibility review.

Text state: developed. Figure-source state: generated and editable. Render state: successful. Inspection state: whole plus detail, first pass plus second self-critical/source-adjudicated pass performed. Final book integration: not performed.

## Parent follow-up — targeted clarity correction, 2026-10-28 UTC

No broad research was repeated. Only figure generator/layout, linked captions, figure plan, local annotation regressions, QA/status and generated assets changed. Source archive and claim scope are unchanged.

### Reviewer issue disposition

| Issue | Decision and reason |
|---|---|
| V1 unlabeled return loop can suggest architectural recurrence | ACCEPTED. Added `Loop: denoising / scheduler iteration` inside the core at the return level; caption explicitly excludes architectural recurrence. Existing 50-step / two-CFG-branch scope retained. |
| V1 temporal/spatial factors and endpoint convention are not reconstructable standalone | ACCEPTED. VAE box shows stride `(T,H,W)=(4,16,16)` and `Aligned endpoint: 1 + 4 × (31 − 1) = 121 frames`. Caption states the fetched code's integer rule `T_l=(F−1)//4+1` and spatial `//16`; the inverse is explicitly limited to aligned `F=4k+1`. Source: `sources/wan22_ti2v.txt:284–287`, config evidence VG005–VG006/VG024–VG025. No generic decoder rule was invented. |
| V1 text tokens could mean output tokens | ACCEPTED. Changed encoder label to `≤512 prompt tokens`. No unverified UMT5 maximum-context or truncation-policy statement was added. |
| V1 ambiguous `revises` title | ACCEPTED. Title now `Whole-clip denoising: Wan2.2 TI2V-5B`. |
| Conditioning routing or extra color legend | NOT CHANGED. Existing orthogonal dashed conditioning and solid data/state semantics are complete, readable in grayscale, and non-crossing. Routing style is not a defect; another color legend would add clutter without information. |
| V2 transition may imply two expert executions in one forward | ACCEPTED. Image says `Denoising schedule progresses →` and `Not two experts within one forward`. Caption says the transition spans timestep evaluations, not chaining inside one forward. |
| V2 checkpoint/expert relationship and bottom GPU condition | ACCEPTED. Boxes now say `High-noise expert checkpoint` / `Low-noise expert checkpoint`; bottom line is explicitly `If both experts stay on GPU: about 27B resident.` |
| V2 equal stage widths could imply equal steps | ACCEPTED. Added image note `Schematic: stage widths do not encode step counts.` |
| Guessed 14B+13B split or numeric switching threshold | REJECTED. Official rounded about 27B total / about 14B active are preserved. No per-expert split can be deduced from rounded totals. No threshold number was needed for the qualitative mechanism. |

### Executed final inspection and self-critical second pass

1. Regenerated both SVGs and all print PNGs, gray versions, actual-size proofs and detail crops. Both minimum font em sizes remain 9.36 pt; width remains 6.1 in. Increased height rather than shrinking labels: V1 6.0 in, V2 3.95 in.
2. Executed exact Inkscape-shaped-text and segment/bbox geometry checks. Final results: zero text outside canvas, zero text/text collisions, zero arrow/text intersections in either figure. Pixel ink bounds and metadata are in the current table above.
3. Vision-inspected both final color whole-figure 150-dpi proofs. Both reviews found no clipping/overlap and accepted mechanism labels. One response marked type size P1; another marked it P2, estimating 6–8 pt from a supposed 1000/1024-pixel source. REJECTED those physical-size estimates: supplied proof files are 915 px wide; SVG minimum em is 13/100 in = 9.36 pt and native raster em is 45.5 px at 350 ppi. Glyph ink height and a resized display are not font-em size. No source font was reduced. The suggested UMT5 context-length example was also rejected as unsupported and unnecessary to resolve prompt/output ambiguity.
4. Second self-critical vision inspection used both final FULL grayscale rasters. V1 returned no P0/P1/P2 raster issue; V2 returned no P0/P1 and only requested source/export font/DPI confirmation. Local checks confirm those metrics. Grayscale preserves dashed/solid connectors, checkpoints/stages, and all required wording. No additional legend was requested by the final reviews.
5. Inspected both final color `*-detail.png` crops. V1 review explicitly confirmed complete `1 + 4 × (31 − 1) = 121 frames`, axes, token digits, conditioning arrowheads and loop return. V2 review confirmed complete checkpoint names, schedule/one-forward disclaimers, conditional residency and schematic widths. Both found no P0/P1. V1's entering/leaving connector shafts continue beyond its DETAIL crop intentionally; the FULL figure contains them. V2 title/≠ lies above its useful detail crop and is present in the inspected FULL figure. These crop boundaries are not clipped full-asset content.
6. Captions in `proposed-insertions.md` and the manifest were synchronized. Alt text was updated. Local validator additionally checks requested annotations, aligned endpoint arithmetic, archived shape rule, matching captions, detail paths and actual PNG DPI. These textual tests complement rather than replace the raster inspections.

Final standalone disposition: [P0] none identified; [P1] none unresolved; [P2] no unresolved raster defect. Explicit gaps remain physical-print proof and actual book placement/pagination/numbering, which were not performed. No measured video-model behavior or full-book readiness is claimed.

Final color PNG SHA-256:

- `video-latent-work.png`: `0ffea19a2b41f366c628377847a7e476f55f3201bca9c82142dc599d6e3c7107`
- `wan-noise-experts.png`: `192d721810e95cb4e6d555fa31aebaaf4cb9083f316268baa0071e28635ad253`

Reproduce: `python3 research/video-generation-20261028/figures/generate_figures.py`; then `python3 research/video-generation-20261028/verify_artifacts.py`. Last validator result is recorded in `../validation.json`; render geometry output in `render-run.txt` / `geometry-QA.json`.
