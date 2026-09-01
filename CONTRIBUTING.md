# Contributing to From Token to Fleet

> This is a **living document** and a **learning tool**. The book is the *what*;
> [`craft/`](craft/) is the *how*. Before you contribute, read
> [`craft/README.md`](craft/README.md) — it is the discipline that makes the
> book's numbers and figures *defensible*, and it is part of what this repo exists
> to share.

Contributions of every size are welcome — a typo, a sharper explanation, a
corrected number, a better figure, a new worked example, a whole chapter review.
This file explains how the repo is organized, how the build works, and the
**binding rules** every change must obey.

---

## Table of contents

1. [How the repo is organized](#how-the-repo-is-organized)
2. [The binding rules](#the-binding-rules)
3. [Running the build](#running-the-build)
4. [Editing content](#editing-content)
5. [Working on figures](#working-on-figures)
6. [Verification bar — getting to "done"](#verification-bar--getting-to-done)
7. [Making a change (workflow)](#making-a-change-workflow)
8. [Releases](#releases)
9. [License & commercial use](#license--commercial-use)

---

## How the repo is organized

| Path                | What it is                                                        | You edit it? |
|---------------------|-------------------------------------------------------------------|--------------|
| `design/manuscript/chapter-NN/` | The book source — one markdown file + figures per chapter | **Yes — the content** |
| `design/book-architecture.md`  | The authoritative architecture: spine, chapter template, evidence taxonomy, canonical scenario | Yes, deliberately (see below) |
| `design/book.yaml`  | Mirrored chapter skeleton                                           | Occasionally |
| `design/canonical-workload.yaml` | The canonical scenario's numbers                        | Yes, with care |
| `design/numerical-audit-ledger.md` | Every derived number, with its audit trail             | Yes, for every changed number |
| `render/`           | Build tooling: `make_html.py`, `emit_book.py`, `md_to_latex.py`, `regen_figs.py`, `fig_*.py` | Yes — the pipeline |
| `render/archify/`   | Hand-drawn figure pipeline (typed JSON → SVG/PDF)                  | Yes — the figure craft |
| `craft/`            | **The methodology** — "how we develop this book"                   | Yes — captures the rules |
| `render/build/`     | Dated deliverables (`from-token-to-fleet-vYYYYMMDD.{pdf,html}`)     | Auto-generated, committed |
| `LICENSE`           | The source-available license                                       | No |

The two documents that govern *every* content decision:

- **[`design/book-architecture.md`](design/book-architecture.md)** — the spine,
  the recurring chapter template, and §5 the **evidence taxonomy (binding)**.
- **[`craft/README.md`](craft/README.md)** — the working method: pipelines, the
  verification bar, and the honesty discipline.

Read both before your first edit.

---

## The binding rules

These are non-negotiable and enforced during review:

### 1. Every number is labeled and anchored
Every quantitative claim carries **two orthogonal labels** (per `book-architecture.md` §5):

> **Source** — *where the number came from*:
> **`[1P]`** first-party to the subject (vendor spec / model card)
> **`[2°]`** reputable second-hand (textbook, survey, third-party benchmark)
> **`[VERIFY]`** not yet anchored — a *status*, resolved before publication
>
> **Claim type** — *whether it was computed*:
> **`FACT`** directly stated by the source · **`DERIVED`** calculated from documented facts · **`HYPOTHESIS`** reasoned conclusion

**Home-lab experiments are not reference.** Worked examples may appear, clearly
labeled `worked example, not reference`.

### 2. Derived numbers are actually computed
No "from-memory" values. If a number is `DERIVED`, it must be traced through the
audit ledger ([`design/numerical-audit-ledger.md`](design/numerical-audit-ledger.md))
from its `[1P]`/`[2°]` inputs. When you change any number that other numbers build
on, **trace its dependents** and update them all — stale derived numbers are the
most common failure mode.

### 3. No machine-specific or private material
The repo is public. Never commit:
- personal tokens, API keys, passwords, or credentials (of any kind);
- machine/user-specific absolute paths (`/home/…`, `~/.hermes/…`, private IPs);
- personal contact info beyond the public author email.

Keep scripts portable: resolve tools via `PATH` or `$ENV` override, not hard-coded
system paths. If you must point at a helper, use a repo-relative or `~`-expanded
path with an env-var escape hatch.

### 4. Figures are design decisions — captions carry the labels
A figure is not decoration; it is a design decision that must stay **in sync with
the text**. New figures append a new number (`Fig 7.5` follows `Fig 7.4`) to avoid
renumbering cascades. Every figure image line carries its evidence labels in the
alt-text (`![Fig X.X — … [2° DERIVED]](figures/…png)`).

### 5. The verification bar
Nothing is "done" until a **validator returns `ok:true`** *and* (for figures) a
**visual check confirms it at book size**. See [Verification bar](#verification-bar--getting-to-done).

---

## Running the build

Two pipelines share one manuscript and one set of source figures.

### Toolchain
```bash
bash render/setup_environment.sh    # installs pandoc + tectonic if missing (repo-relative ./render/bin)
```

### Figures (optional, if you changed any)
```bash
python3 render/regen_figs.py         # regenerate matplotlib figs as PNG + vector PDF
```

### HTML (dark, self-contained, figures inlined)
```bash
python3 render/make_html.py          # -> render/build/from-token-to-fleet-v<date>.html
```

### LaTeX PDF
```bash
cd render/latex
python3 emit_book.py                 # -> book.tex (title page, preface, TOC, 27 chapters)
python3 md_to_latex.py               # -> chapters/*.tex
xelatex -interaction=nonstopmode book.tex   # run 3 passes
# -> copy to render/build/from-token-to-fleet-v<date>.pdf
```

Run LaTeX from inside `render/latex/` (paths are relative to it). The build
intermediates (`book.aux/log/out/toc/lof`) are git-ignored and must not be
committed; versioned deliverables in `render/build/` **are** committed for review.

---

## Editing content

- Each chapter is one file: `design/manuscript/chapter-NN/chapter-NN.md`.
- Follow the recurring chapter template in `book-architecture.md` §4.
- Numbered claims carry their source/type labels inline.
- Prepared to show your arithmetic in the audit ledger.

**Changing the architecture or the canonical scenario?** Those are high-leverage,
high-risk edits that ripple through many chapters. Propose them as an issue or a
focused change first, and trace dependent numbers before committing.

---

## Working on figures

There are two pipelines:

1. **Matplotlib figures** — `render/fig_*.py`; edit the script, run it from the
   repo root, verify the output. `regen_figs.py` emits both PNG (HTML) and vector
   PDF (LaTeX) so the book stays crisp at any zoom.
2. **Hand-drawn figures** — the Archify pipeline, documented in full in
   [`craft/archify-diagram-craft.md`](craft/archify-diagram-craft.md) and the shape
   language in [`render/archify/shape-semantics.md`](render/archify/shape-semantics.md).
   Author typed JSON → pass the Archify validation gate → extract SVG → harden →
   integrate as SVG/PDF into the book.

Keep the book's color code: **memory = blue · compute = orange · economics = green**.
Every data figure carries a redundant second channel (line style / marker / value
label) so it stays readable under color-vision deficiency — never rely on hue alone.

---

## Verification bar — getting to "done"

A contribution is *done* only when **all** of these hold:

- [ ] **Content:** edits follow the chapter template; claims carry `[1P]`/`[2°]` and `FACT`/`DERIVED`/`HYPOTHESIS` labels.
- [ ] **Numbers:** changed numbers are logged in the audit ledger; dependents traced and updated.
- [ ] **Figures:** any caption/alt-text change matches the figure; the figure renders at book size without overflow or truncation.
- [ ] **Build:** HTML and PDF both rebuild with **zero `??`** (unresolved references) and no fatal warnings.
- [ ] **Diff review:** no stray machine paths, no private credentials, no leftover scratch files committed.
- [ ] **We-voice / tone:** the book reads as a learning tool, not a lecture — no imperative "you should/must" framing outside a quoted template.

---

## Making a change (workflow)

1. **Fork** (or branch) and make focused edits on `main`.
2. **Rebuild** both deliverables locally and confirm the verification bar above.
3. **Run the sweep** for stray private material before committing:
   ```bash
   grep -rniE '/home/|/opt/|API[_-]?KEY|ghp_|sk-|BEGIN (RSA|OPENSSH|EC)' --include='*.py' --include='*.md' --include='*.sh' .
   ```
4. **Commit atomically** — one logical change per commit. If you touched
   generated files, commit them alongside their generator.
5. **Open a pull request** describing what changed and *why*, with the build
   output (`0 ??`) noted in the description.

Small, well-verified PRs merge fast. Large rewrites get review — please split them.

---

## Releases

- Each release is a **dated build**: `render/build/from-token-to-fleet-vYYYYMMDD.{pdf,html}`.
  The date is the version.
- There is intentionally no semver — the book is a living document; the commit
  chain and dated builds are the evolution log.
- The repo history is squashed at publication boundaries so no machine-specific or
  private material survives in git history. **Keep it that way**: never commit
  credentials or absolute paths, because they can't be fully erased once pushed.

---

## License & commercial use

This repo is under a **custom source-available license** (see [`LICENSE`](LICENSE)),
**not** an open-source license. It is free for personal use, study, and
non-commercial redistribution with attribution; **commercial use or publication
requires the author's prior written approval**. By contributing you agree your
contribution is licensed on the same terms. The methodology in `craft/` is part
of the licensed work — respect the same terms when reusing it.

Questions, corrections, or permission requests: contact Zhiqi Tao (author email in
[`LICENSE`](LICENSE)).
