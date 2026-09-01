# Archify Diagram Craft

*The proven pipeline we use to turn a figure idea into a book-ready vector diagram —
captured so the next figure is faster and better than the last.*

Part of the **craft/** collection: not just *what* the book says, but *how we built it*.
This is the workflow that produced every Archify figure in the book
(Fig 6.1 metric hierarchy, Fig 10.1 parallelization, Fig 13.1 reference ladder,
preface spine loop, ch19 agent loop, ch17 fleet).

---

## 0. Why Archify at all

For figures whose point is **structure, topology and relationships between typed
components**, we hand Archify a typed JSON spec and it renders a clean, legible,
consistently-styled diagram with a hard validation gate. The alternative — a
hand-rolled matplotlib script — drifts in quality across figures and takes hours to
tune. Archify gives us a repeatable bar: no crossed arrows, no overlapping text,
composition checked against 9 artifact rules before we ever look at a pixel.

**When NOT to use it:** when the whole point is one object drawn at *large* geometric
scale (a big matrix square, a giant cloud). Archify's shape language lives in a
11px corner sigil, not in the container body (see `shape-semantics.md`). Free-form
large geometry needs manual SVG / matplotlib.

---

## 1. The setup (once)

```bash
git clone --depth 1 https://github.com/tt-a1i/archify.git /tmp/archify
cd /tmp/archify/archify && node bin/archify.mjs --help
```

No npm install — the `archify/` subdir is self-contained, Node only.

---

## 2. The core loop

1. **Pick the diagram type** (`guide "<scenario>" --json` gives a suggestion):
   - **workflow** — CI/CD, decisions, processes, the book spine loop, agent pipelines
   - **lifecycle** — state machines / status transitions (agent Plan-Execute-Observe-Decide)
   - **architecture** — components, services, boundaries, topology
   - **sequence** — API call chains
   - **dataflow** — pipelines, ETL, lineage
2. **Author a small typed JSON** spec (below), then
   `node bin/archify.mjs validate <type> <in.json> --quality showcase --json`
3. **Iterate until `ok:true`** (target: all 9 artifact checks, 0 composition errors).
   The validator is unforgiving and *right* — trust its suggestions more than your eye.
4. **Deliver** (freezes the spec, renders, commits, reports sha256):
   `node bin/archify.mjs deliver <type> <in.json> <out.html> --quality showcase --json`
5. **Screenshot for visual QA** with playwright chrome (NOT snap chromium — see §7),
   then vision-check the PNG before it goes anywhere near the book.

---

## 3. The shape language (the part that cost us the most)

Read [`archify/shape-semantics.md`](archify/shape-semantics.md) — the full empirical
inventory. The headline you must internalise:

**Archify distinguishes concepts by GEOMETRIC SHAPE — via the corner sigil, not the box.**
Each `type` binds to a distinct SVG shape: `database`=cylinder, `cloud`=cloud blob,
`security`=shield, `frontend`=window, `backend`=braces, `messagebus`=3 rails, `external`=
arrow-out box; lifecycle adds `start`=play, `active`=lightning, `waiting`=hourglass,
`success`=check, `failure`=X. Cross-domain colour inheritance: frontend↔start,
backend↔active, database↔success, cloud↔waiting, security↔failure, external↔neutral.

**Application rule:** when N concepts must be visually distinct, give each a different
`type` (different shape + colour). When you have N *instances of the same kind* (e.g. GPU
shards), give them ONE repeated type — the repetition is itself a signal.

The honest constraint: the shape is the 11px corner sigil, the container stays a rounded
rect. If the figure calls for big free-form objects, that is outside Archify's primitives.

---

## 4. JSON essentials (learned the hard way)

### Global
- `{ "schema_version": N, "diagram_type": "<type>", "meta": {...}, ... }`
- `meta.title` required; `meta.quality_profile: "showcase"` required for the strict 9-check gate.
- `meta.viewBox: [w, h]` (min 700×240; desktop-readability wants width ≲1440).

### architecture
- `components`: `{id, type, label, sublabel, pos:[x,y], size:[w,h], tag?}` — place `pos`/`size`
  manually to avoid fan-out crossing.
- **Vertical fan-out REQUIRES explicit `fromSide`/`toSide`** (e.g. `fromSide:"bottom"`,
  `toSide:"top"`). The renderer can't infer the endpoint side for a column stack otherwise
  (fails `clean-flow/endpoint-side-direction`).
- **Keep connection labels SHORT or omit them.** Auto-placed labels overlap the source
  component; let the `variant` colour carry the split meaning, or use an explicit
  `labelAt`/`labelDy`.
- `connections`: `{id, from, to, label?, variant?, fromSide?, toSide?, via?}`.
- **fan-out trap:** N sources × M targets sharing one corridor fails
  `ambiguous-corridor` — restructure topology through a shared hub rather than hand-routing.
- `boundaries`: `[{kind: region|security-group, label, wraps:[ids]}]`.

### workflow (schema v2)
- `lanes` (swimlanes), `phases` (column bands), `nodes` `{id, lane, col[0..5], type, label,
  sublabel, width}`, `edges` `{id, from, to, label?, variant?, route?}`, optional `mainPath`.
- **Cols are 0..5 max.** Keep `mainPath` monotonic non-decreasing (backward step = error).
- Label must fit node `width` — widen node or shorten label.
- Same-lane + same-col = node overlap. Stagger cols.

### lifecycle (schema v1)
- `states` `{id, type: start|active|waiting|decision|success|failure|neutral|external,
  label, sublabel, lane, col, step, tag, yOffset?}`, `transitions` `{id, from, to, label?,
  variant?, route?, fromSide?, toSide?, via?}`.
- **Terminal/outcome states only live in cols 0..2** (col 4 > 2 = invalid).
- Route enum: auto, straight, drop, bottom/top/right/left-channel (NO return-left).
- Transitions do NOT take `role`.
- Cross-figure loop-back → route `top-channel`/`bottom-channel`, or simplify topology.

---

## 5. From deliverable to book figure (the integration pipeline)

The delivered HTML is interactive; LaTeX wants a **vector PDF**, the HTML build wants a
**PNG**. Don't paste interactive HTML into the book.

1. **Extract SVG + styles, force light theme.** A bare `<svg>` extraction loses colours
   (they ride on CSS variables). Build a minimal standalone page carrying the page's
   `<style>` block + the `<svg>` with `data-theme="light"` on `<html>` (book pages are light).
2. **Vector PDF for LaTeX** (single page, CSS resolved):
   `chrome --headless=new --no-sandbox --disable-gpu --print-to-pdf=out.pdf --no-pdf-header-footer file:///min.html`
3. **PNG for the HTML build** at natural aspect ×2 for legibility:
   `chrome --headless=new --window-size=W,H --force-device-scale-factor=2 --screenshot=out.png file:///min.html`
4. **Name = the chapter figure id** (`fig-<NN>-<NNNN>.pdf` + `.png`) in
   `design/manuscript/chapter-NN/figures/`, matching the id the md already references.
5. **Reference it in the md** at the pedagogically right section — where the concept is
   described — and update the alt/caption to say what it actually shows.
6. **Disable the old matplotlib generator** for that id so `regen_figs.py` can't clobber
   the Archify asset (replace the owning block with a comment pointing at the asset).
7. **Rebuild & verify:** md_to_latex → emit_book → xelatex ×3 → copy PDF;
   make_html; confirm `??`/`undefined`/`LaTeX Error` = 0 and both figure ids are inlined.
8. **Vision-check the extracted BOOK page** (not just the /tmp PNG) at real book size —
   something legible at 2× can be too small at book width. That is a real re-design signal.

---

## 6. Quality discipline (the bar)

Never call it done until `validate --quality showcase` is `ok:true` AND a vision check of
the rendered figure (in the book, at book size) shows no crossed arrows, overlapping text,
or cut-off labels.

---

## 7. Environment gotchas

- **Use playwright chrome** (`~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome`), NOT
  snap chromium — the snap build fails headless (`cannot start document portal`) in our env.
- Don't rely on `archify visual-check` in headless — it needs a desktop session bus.

---

*Living document — updated each time the pipeline bites us so the next figure is faster.*
