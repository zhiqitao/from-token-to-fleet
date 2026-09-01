# Craft — How We Develop the Book

> The book (`design/`) is the *what*; this directory is the **how**.
>
> From Token to Fleet is built by an AI agent working under a strict, evolving
> discipline. That discipline is itself worth sharing — it is the difference between
> a book with figures and a book whose figures are *defensible*. So alongside the
> manuscript we publish our **working methods**: the pipelines, the rules, and the
> hard-won lessons that produce the deliverables in `render/build/`.
>
> These are living notes, kept honestly — including the mistakes (mis-judged tool
> capabilities, silently-dropped requests) and the corrections that followed. The
> craft advances every time the pipeline bites us.

---

## Index

- **`archify-diagram-craft.md`** — the full figure pipeline: picking a diagram type,
  authoring typed JSON, the Archify validation gate, and the extract→SVG→PDF/PNG
  integration into the book. Includes the hard lessons (explicit `fromSide`/`toSide`
  for vertical fan-out, short labels, disabling the old generator so regen can't
  clobber an asset).
- **`archify/shape-semantics.md`** — the empirical inventory of Archify's geometric
  shape language (which type = which shape = which meaning), the single most
  misconception-prone part of working with it.

*More craft documents land here as we hit new pipelines (LaTeX math, table redesign,
multi-model research). See `pipelines.md` when it appears.*

---

## What "craft" captures that the book can't

The manuscript is a polished artifact — it hides the work. The craft records:

- **The evidence discipline**: every number labeled `[1P]`/`[2°]`/`[VERIFY]` and
  `FACT`/`DERIVED`/`HYPOTHESIS`, home-lab marked "worked example, not reference".
- **The verification bar**: nothing is "done" until a validator is `ok:true` *and* a
  vision check confirms it at book size.
- **The honesty discipline**: a request we silently dropped is admitted and then done;
  a mis-judged capability is retracted on evidence, never defended.
- **The versioning**: each release is a dated build; the commit chain is the evolution log.

If the book teaches you to *reason like an architect*, the craft shows you how to
*build like one* — methodically, verifiably, and honestly.
