# Figure plan — recent model trends

Scope: original explanatory artwork and candidate prose only. No manuscript changes. Figures describe mechanisms, not model rankings. Public-model evidence remains in claims.json and source-index.json.

## Layout and design evidence

Read `design/book-architecture.md`, binding drafting conventions, especially line 222: memory red, compute blue, communication green, latency/economics amber. Read `render/latex/book.sty`, lines 55–62 and 93–98; `render/latex/book.tex`, line 7; and existing generators `render/fig_ch3.py` and `render/fig_ch27_norm.py`. The book is US Letter 8.5 × 11 inches with 1.2-inch left and right margins. Available text width is 6.1 inches, not a 6 × 9 book column. Master review instructions §§8.2–8.9 govern physical and semantic checks.

Author at 6.1-inch width with explicit physical SVG dimensions. Use clear sans-serif labels, white background, flat outlined shapes, blue computation and red persistent state. Amber is reserved for exit/control cautions. All essential lettering is at least 9 pt at intended placement. Color is redundant with labels, enclosure and line style. Use vector PDF siblings and 400-PPI PNGs. No external artwork or quantitative benchmark plots.

## MT-1 — History recurrence does not remove all growing state

Learning objective: distinguish state updated across tokens from attention history retained across tokens; show why a dense FFN label does not determine request memory.

Mechanism: three ordered snapshots. A bounded recurrent state remains the same size while the full-attention KV inventory accumulates token entries. These are separate layer groups, not two alternative names for one cache. Exact token-to-token connectors denote temporal state updates; no connector is a bandwidth encoding.

Placement: Chapter 7, §3 Worked Example, candidate section B, immediately before the Qwen3.8-27B component calculation. Cross-reference from Chapter 3 §6 and the dated appendix update. Do not duplicate the existing dense-versus-MoE residency graphic.

Composition: aligned token-time columns; blue update computations; fixed-size red recurrent-state boxes; red append-only attention-history cells below. Clearly label snapshots and state scope. Token counts are schematic, not a particular model's layer schedule.

Necessity: a single KV formula or an MoE diagram cannot show two different state lifetimes in the same model. Claims Q02/Q05 support the named example. The diagram does not claim all hybrid models have the same cache shape.

## MT-2 — Weight sharing is not skipped execution

Learning objective: separate a shared parameter inventory, executed core passes, iteration-specific cached history, and the decision to stop computation.

Mechanism: three unrolled invocations use one shared weight object but retain distinct iteration-state slots. A separate two-lane comparison shows a genuine conditional exit versus post-hoc selection after every pass. Amber exit markers indicate control decisions, not measured quality or latency.

Placement: dated appendix update, section A, after “A stopping rule is not yet a runtime saving”; candidate Chapter 8/11 cross-references. This is not a second general MoE or agent-loop figure.

Composition: shared weight rail above three blue pass nodes; red cache slots below each pass. Bottom comparison has identical pass cells in both lanes, with a dashed omitted pass only in the actual-stop lane. The illustrated exit index is arbitrary, not an Ouro benchmark.

Necessity: shared weights alone visually encourage the false inference of shared state and lower latency. R01–R05 establish the relevant mechanism and the implementation distinction. No claim is made that the selected illustrative exit rule is shipped in a production engine.

## Reproduction and inspection

Editable SVGs, generator, data, PNGs, vector PDFs, grayscale previews, detail crops, and Letter-sized placement proofs stay in `figures/`. Reproduction commands and evidence IDs are in `figures/manifest.json`. Record measured typography, label bounds, raster dimensions, source arithmetic, grayscale checks, whole-figure and detail vision results in `figures/QA.md`. Physical hardcopy and final integrated manuscript layout remain parent-side checks. Think HARD: repeat semantic and design review after the first rendering and classify unresolved issues [P0]/[P1]/[P2].
