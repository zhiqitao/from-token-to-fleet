# Figure plan — video systems / Wan

## Format and design constraints

- Actual build: `render/latex/book.tex:7` uses `letterpaper,11pt`; `render/latex/book.sty:61` sets left/right margins to 1.2 in. Available width is 8.5 − 1.2 − 1.2 = 6.1 in (calculated by generator).
- Existing guidance: `design/book-architecture.md` §3 constraint hierarchy, §5 two-axis evidence, §6 anti-catalog rule; `book.sty:104–112` semantic palette. Existing `render/fig_ch7_budget.py` uses a 6.1 in canvas with native print-sized sans labels.
- Use white background, Liberation Sans, dark text, memory blue #27408B, compute orange #E67E22, economics green #1E6B42 only where semantically justified. Labels and line styles preserve meaning in grayscale. No hand-font requirement is inferred from older mixed-style assets.
- SVG viewBox uses 100 units/in; all labels ≥13 units =9.36 pt at full intended width. Render color and grayscale PNG at 350 dpi. Avoid `bbox_inches=tight` or autosizing that changes intended scale.
- The full book is not rebuilt or altered. Standalone actual-size assets are checked; final page placement remains the parent integration task. The supplied 361-page frozen count is context, not a count re-certified here.

## V1 — Whole-clip denoising: Wan2.2 TI2V-5B

Learning objective: connect conditioning and exact video geometry to repeated whole-clip work, rather than treating frames as autoregressive text tokens.

Mechanism: separate T2V prompt → UMT5; optional I2V reference → VAE encode; initial FP32 latent noise → full-video denoising with CFG → VAE decode → frames → media completion. The selected worked example is TI2V-5B T2V: 121 frames, 1280×704, 31×44×80×48 latent tensor, patch=(1,2,2), N=27,280. Optional reference-image conditioning is shown as a distinct branch, not added to the T2V arithmetic.

Placement: candidate Ch8 §6 subsection `Beyond autoregressive decode: the video work unit`; cited by candidate anchor `video-resource-budget`. A brief Ch2 pointer reuses the same figure rather than creating a second introduction figure.

Composition: top row of separate conditioning/noise inputs; encoders and latent shape in second row; one central repeated denoising block with an explicitly labeled denoising/scheduler loop; VAE decode shows stride (4,16,16) and the aligned first-frame endpoint inverse. Dashed connectors mean conditioning, solid connectors mean data/state flow. Footer preserves communication implications. Parent-review revision uses 6.1×6.0 in without reducing the 9.36-pt minimum font.

Why necessary: the prose alone leaves room to confuse VAE causality, denoiser attention, CFG branch evaluations, and output frames. A single mechanism diagram gives the worked arithmetic a spatial object.

Sources/claims: VG005–VG010, VG024–VG029, VG031. Original artwork; no vendor art. Not a generic diagram of every Wan variant or of native audio generation.

Files: `figures/video-latent-work.svg`, `.png`, `-gray.png`; editable generator `figures/generate_figures.py`; data `figures/figure-data.json`.

## V2 — Active experts are not the resident weight set

Learning objective: distinguish noise-stage expert selection from per-token language-MoE routing and from weight residency.

Mechanism: two stored A14B expert checkpoints feed different noise stages. Only the selected expert runs in a given evaluation. About 27B total versus about 14B active are official rounded counts. A timeline is explicitly schematic; it does not allocate equal sampled-step counts or depict the 0.875 boundary as an equal-time midpoint.

Placement: candidate Ch3 §6 after `The 2026 baseline shift: same framework, new constants`, anchor `video-expert-residency`; cross-reference from Ch8 example without implying the dense 5B has experts.

Composition: blue enclosing resident-bank outline with high-noise/low-noise expert checkpoint boxes; dashed downward links into two orange stage boxes. A labeled denoising-schedule progression explicitly excludes chaining two experts within one forward. Text makes both-on-GPU residency conditional and states that stage widths do not encode step counts. Counts remain official rounded values, not a parameter split or falsely proportional bar. Parent-review revision uses 6.1×3.95 in without reducing the 9.36-pt minimum font.

Why necessary: Figure V1 concerns the dense 5B example. It cannot safely carry the separate A14B activation/residency lesson without suggesting a hybrid architecture that does not exist.

Sources/claims: VG002–VG004, VG030–VG031. No benchmark or speedup curve.

Files: `figures/wan-noise-experts.svg`, `.png`, `-gray.png`; shared generator/data above.

## Verification plan

1. Regenerate from archived configuration-derived data and calculations.
2. Inkscape SVG → PNG rendering; test PNG dimensions and DPI metadata.
3. Deterministic font-bounding-box, canvas, pairwise-text and arrow/label intersection tests. Confirm intentional containment rather than treating text inside a box as collision.
4. Check rendered ink extents and grayscale contrast. Create 150 dpi actual-width proofs and detail crops.
5. Use available vision on each whole figure and each important detail. Think HARD; second self-critical review checks arrow semantics and architecture mixing, not only appearance.
6. Record actual results and [P0]/[P1]/[P2] unresolved items in `figures/QA.md`. No claim of manuscript-page inspection or publication certification.
