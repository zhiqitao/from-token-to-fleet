# Figure Visual Grammar (PASS-23b consolidation)

Goal: keep the book's figure set visually consistent and self-describing at
printed-book size. A reader should be able to tell a figure's *type* from its
visual vocabulary within ~3s, and follow the reading order without the caption.

## Color semantics (consistent across figures)
- **Blue = compute / on-chip** (registers, tensor cores, SRAM, L2, model param blocks)
- **Orange = memory / persistent state** (HBM, KV cache) — the reviewer's proposed
  "orange = KV state, blue = compute"
- **Green = network / interconnect** (GPU interconnect, cross-node)
- **Grey = data / request / neutral annotative boxes**
- **Red = warning / excluded / rejected / emphasis** (only where it means "no" or "alert")
- Color is ALWAYS paired with hatching or line-style so the figure survives grayscale
  (hatch `//`, `..`, `xx`; line solid vs dashed; marker circle vs triangle).

## Connector semantics
- **Solid arrow → data / request / value flow**
- **Dashed arrow → control / health-check / state-connection** (not data volume)
- **Thick / double arrow → high-volume transfer** (e.g. KV transfer in Fig 11.3)
- **Loop arrow → iteration / feedback** (reading-order turns back)
- **Bounded container → a host / pool / system boundary**
- **Diamond / branch node → a decision**
- **Stacked identical boxes → replicas / shards**

## Type-to-shape (Archify corner sigils)
database=cylinder, cloud=cloud, security=shield, frontend=window,
backend=braces, messagebus=3-rails, external=arrow-out box. Use repeated
shape for repeated shards.

## Font/scale floor (frozen)
- Author at 6.1in column width; regen_figs does NOT boost (avoids double-boost).
- Effective print font = native_font × (6.5 ÷ native_fig_width_in); floor 7.5pt.
- regen_figs.py targets 8.5pt; run manually after figure edits (re-crop archify after).

## Per-figure QA to run on every conceptual figure (PASS-23b standard)
1. Does any annotation collide / crowd / squeeze into leftover space?
2. Is the reading order obvious without the caption?
3. Does the graphic encode the CAUSAL relationship, or merely name the concepts?
4. Could the figure be understood in grayscale (no color-only distinction)?
5. Does it teach something prose alone would teach less effectively?
6. If the caption disappeared, would the central insight survive?
7. Book-quality figure, or slide-quality diagram scaled down to fit a book?

## Verdict categories (frozen)
KEEP / POLISH / MAJOR REVISION / REDESIGN / REMOVE-MERGE.
A figure can be correct yet still fail if the reader must decode the layout
before the idea.
