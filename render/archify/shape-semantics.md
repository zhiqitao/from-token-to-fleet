# Archify Geometry→Semantics: which shape for what

Research source: `/tmp/archify/archify/renderers/shared/utils.mjs` (SIGIL_SHAPE, SIGIL_TONE) +
renderers (architecture/lifecycle/workflow/dataflow/sequence) + schemas. Date 2026-08-31.

## The core language

An Archify **node is NOT 'a rounded rectangle.'** A node = a container + a **mandatory semantic
sigil** (`renderSemanticSigil(c.type, {x, y, size=11})`, data-semantic-sigil=...) drawn in its corner,
**plus** a fill colour and text colour bound to the very same type code. So EVERY node carries a
distinct, preset **geometric icon** determined by its `type`. The geometry lives in the sigil, not
the container.

## SIGIL_SHAPE — the 14 geometric forms (verbatim)

### Architecture component types (node type for components)
| type | colour (tone) | geometry | reads-as |
|------|--------------|----------|----------|
| `frontend` | cyan frontend | **window**: rect + title-bar line + 2 dots | UI / entry / user-facing / controller |
| `backend` | green backend | **braces** `}` `{` | processing / service / worker |
| `database` | violet database | **cylinder** (ellipse + side lines) | store / state / weights / KV |
| `cloud` | amber cloud | **cloud blob** | external host / GPU / cloud service |
| `security` | rose security | **shield** (with check) | guard / policy / federation / gateway |
| `messagebus` | orange messagebus | **3 rails + dots** | message / queue / bus / async |
| `external` | slate external | **arrow-out box** | outside world / boundary / context |

### Lifecycle state types (node type for states)
| type | tone | geometry | reads-as |
|------|------|----------|----------|
| `start` | frontend | **circle + play triangle** | entry / begin |
| `active` | backend | **lightning bolt** | running / executing |
| `waiting` | cloud | **hourglass / waves** | blocked / await / pending |
| `success` | database | **circle + check** | done / committed |
| `failure` | security | **circle + X** | rejected / failed |
| `neutral` | external | **box + dot** | neither |
| `decision` | security | falls back to `neutral` box (no own sigil) but is coloured security/rose | branch |

## SIGIL_TONE — cross-domain colour inheritance (the mapping to remember)
```
frontend↔start        backend↔active        database↔success
cloud↔waiting         security↔failure      messagebus↔messagebus     external↔neutral
```
Same archetype shares a colour family across the component and lifecycle vocabularies.

## Which shape for what (application guidance)
- **A thing that persists / is stored** (weights, KV cache, state, DB) → `database` = cylinder.
- **A running computation / worker / service** → `backend` = braces.
- **A user-facing or orchestration entry** (controller, gateway that fronts a system) → `frontend` = window.
- **A remote or external host / GPU / cloud** → `cloud` = cloud blob.
- **A guard / checkpoint / policy / auth boundary** → `security` = shield.
- **An async boundary / queue / stream between pieces** → `messagebus` = rails.
- **The outside world / an input context that enters the picture** → `external` = arrow-out box.

## Honest scoping (so I don't overclaim again)
- The **preset** shape language is rich (14 geometries) and IS what distinguishes concepts — my earlier
  'it's all one rounded rect' claim was wrong.
- BUT Geometry = the corner sigil at scale 11px. The node **container is still a fixed roun- rect**
  (rx 6–10 depending on renderer). You cannot make the *whole container* a cylinder/cloud/diamond.
  If the design needs a large free-form shape (a full-size matrix drawn as a square, a big cloud), that
  is outside Archify primitives and needs manual SVG.
- Brand marks (brand-marks/catalog.json, e.g. openai/claude/kubernetes...) attach a *third-party logo*
  in the opposite corner — a different axis (whos-this) from the semantic sigil (what-is-this).

## So for 'five parallelization strategies, each splitting a different-shaped object'
Archify CAN give the five strategy panels five different **semantic shapes** via sigils:
- Tensor/Pipeline splitter object = `database`(cylinder) / `frontend`(window: layer-stack)
- model replication = `cloud`; expert grouping = `messagebus`; context window = `external`.
(the fig-10-1001 built). The constraint that remains: each shape is 11px in the corner, not the whole
panel. If the brief is 'five BIG different geometric objects', that specific ask needs free geometry.
