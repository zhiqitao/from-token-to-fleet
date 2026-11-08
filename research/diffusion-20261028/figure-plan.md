# Diffusion figure plan

Scope update accepted: English prose and rendered, inspected original figures are required. No manuscript integration, shared-file edits, model benchmark, delegation or publication certification.

## Print/build discovery

- render/latex/book.tex:7 declares `letterpaper,11pt,openany`.
- render/latex/book.sty:61 sets left/right margins to 1.2 in.
- Intended available width is US Letter 8.5 in minus 2 x 1.2 in = 6.1 in. The generator and QA compute this, rather than assuming a 6 x 9 trim.
- book.sty:106–112 and CONTRIBUTING.md:163–165 specify memory blue (#27408B), compute orange (#E67E22), economics green, redundant non-color encoding. design/book-architecture.md:222 contains an older conflicting palette. Follow the active build/style and contributor instructions; record the conflict, do not edit shared guidance.
- Original vector mechanism diagrams: light background, Liberation Sans, short labels, clean aligned geometry, labeled arrows, dark text. Blue context/state boxes, orange computation/reverse-step arrows. Grayscale uses labels, hatch, dashed vs solid outlines, not hue alone.
- All ordinary figure text >= 10.08 pt at intended 6.1-in placement (14 SVG units at 100 units/in); primary text generally larger. Conventional theta subscripts in p_theta use 80% size (8.064 pt) and were inspected in raster detail. PNG at 400 PPI; vector SVG/PDF also supplied.

## Figure D1 — Corruption and learned generation are different processes

Learning objective: distinguish fixed forward corruption used to construct training pairs from the learned reverse generator used for sampling; separate continuous/noise and categorical/MASK state spaces.

Mechanism: two state-space lanes. Each lane has a clean state, an intermediate corrupted state and a terminal prior. Rightward black arrows denote the specified forward process q; separate leftward orange arrows denote learned reverse steps p_theta. Explicit state examples are illustrative, not sampled benchmark evidence. The continuous lane depicts schematic continuous values; the categorical lane uses token IDs and MASK cells. Text below states that masked diffusion is one discrete choice, and flow matching regresses a vector field on a chosen path rather than being the identical loss/process.

Placement: Chapter 3 after the new `Alternative inference: the token is not the execution step` subsection, mechanism paragraphs, before cache/resource consequences. Candidate prose anchor P03A.

Composition: two 3-state lanes with separate forward and reverse arrow channels. No arrow through token/state labels. State-space labels precede the lanes. Local text explains the fixed-versus-learned distinction. Caption carries sources and conceptual scope, not a dense legend.

Why needed: the schedule figure alone cannot explain why denoising is learned or why discrete MASK is not continuous Gaussian noise. This figure prevents equating all iterative generation with diffusion and prevents equating diffusion with flow matching.

Evidence: D01–D07. No numerical performance data. Sources: original DDPM, score-SDE, D3PM, MDLM, flow-matching and rectified-flow papers.

## Figure D2 — Dependency order and cache lifetime change together

Learning objective: compare AR append-only decoding, a full-canvas masked sampler, and block-causal diffusion without implying equal wall-clock time or unchanged AR cache support.

Mechanism: three vertically stacked schedules. Each has a blue fixed-context box and a sequence of token-state snapshots. AR extends a causal prefix. The chosen full-canvas masked sampler accepts positions out of order while recomputing bidirectional states. Block diffusion refines a mutable block, finalizes/caches it, then advances the immutable causal prefix. Repeat loops connect to unresolved intermediate regions. State symbols: letters = accepted IDs, solid lower brackets = finalized reusable prefix state, hatched `?` = unresolved, unhatched `-` = inactive future, orange dashed canvas = recomputed output representations. Accepted IDs and finalized cached state are separate concepts. AR snapshots include processing of the newest accepted token, as the caption specifies; other samplers can edit or renoise.

Placement: Chapter 3 immediately after the cache-boundary paragraphs (P03B); Chapter 7/8/11 cross-reference it instead of reproducing it. Figure code D2 is temporary; the parent must assign final figure numbering only after integration.

Composition: vertical lanes at full text width; snapshot columns labeled evaluation order, not elapsed time. Local cache and emission notes below each lane. No performance curves, no proportional timing bars, no invented measured rates.

Why needed: model sampling order, validity of cached state and external commit boundaries are the architecture-changing mechanism. A generic noise-to-text picture does not show these consequences.

Evidence: D08, D11–D15, D18, D24–D26, D33–D34. The block lane is a block-causal design, not a universal diagram of every diffusion system.

## Deliverables and QA gates

Generator plus explicit figure data, editable SVG, print PNG, vector PDF, grayscale PNG, actual-size proof PDF and overview/detail inspection images live in figures/. figures/manifest.json records reproduction commands, dimensions, captions, alt text and claim/prose anchors.

Render gate: expected physical width and 400-PPI dimensions; SVG XML valid; nonempty pixel content; PDF dimensions; font and shape bounds; no text-box or connector collisions.

Inspection gate: whole-figure color and grayscale plus crop/detail review through available vision tools. Second self-critical pass checks arrow direction, q/p_theta semantics, non-universal cache statements, commit status and placement-size typography. Record failures and residual P0/P1/P2 issues in figures/QA.md. Rendering alone does not satisfy this gate.
