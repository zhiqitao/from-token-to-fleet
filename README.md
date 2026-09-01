# From Token to Fleet: An AI Solution Architect's Handbook

I wanted to build the systematic knowledge of what it means to work as an AI Solution Architect: how to reason across the layers of an AI system — from tokens and models to workloads, systems, infrastructure, and fleets — so that a vague requirement can be turned into a defensible architecture. I kept looking for the resource that would lay all of that down in one coherent thread. What I found were deep dives into single layers, but no single spine that connected them.

Eventually I realized the most honest way to build that knowledge was to develop the book myself. First and foremost this is a **learning tool I wrote for myself**; if it helps you build the same systematic mental model, then it has outdone what I had planned it for.

> **Status.** Living document; **27 chapters drafted** (26 body + 1 appendix). The six-part architecture is defined in [`design/book-architecture.md`](design/book-architecture.md); the chapter skeleton is mirrored in [`design/book.yaml`](design/book.yaml). Full renders (light PDF + dark HTML, all figures vector inlined) are produced by the tooling under [`render/`](render/) into `render/build/`. Each release is a dated build.

---

## What this is

This is a living learning resource, not an index of answers. It carries the latest frontier-model information (2026 architectures in the appendix) while grounding every mechanism in reproducible arithmetic, and every quantitative claim in a first-party or second-hand source.

---

## Architecture

The book is organized in six parts, each an abstraction layer — the way an architect actually thinks about a problem. The authoritative architecture (spine, constraint hierarchy, recurring chapter template, evidence taxonomy, canonical scenario) lives in [`design/book-architecture.md`](design/book-architecture.md); the chapter skeleton is mirrored in [`design/book.yaml`](design/book.yaml). Each chapter lives in its own directory under `design/manuscript/` (flat by chapter, each as `chapter-NN/chapter-NN.md`; parts are a logical grouping).

### Part I — The Token

1. [It All Starts With the First Token](design/manuscript/chapter-01/chapter-01.md)
2. [What Actually Happens During Inference](design/manuscript/chapter-02/chapter-02.md)
3. [Understanding the Model](design/manuscript/chapter-03/chapter-03.md)

### Part II — The Workload

4. [The Anatomy of an AI Workload](design/manuscript/chapter-04/chapter-04.md)
5. [From Workload to Model Selection](design/manuscript/chapter-05/chapter-05.md)
6. [Measuring What Matters](design/manuscript/chapter-06/chapter-06.md)

### Part III — The System

7. [Memory Is the First Constraint](design/manuscript/chapter-07/chapter-07.md)
8. [Compute](design/manuscript/chapter-08/chapter-08.md)
9. [Communication](design/manuscript/chapter-09/chapter-09.md)
10. [Parallelism](design/manuscript/chapter-10/chapter-10.md)
11. [Serving](design/manuscript/chapter-11/chapter-11.md)

### Part IV — The Architecture

12. [Designing the AI System](design/manuscript/chapter-12/chapter-12.md)
13. [Reference Architectures](design/manuscript/chapter-13/chapter-13.md)
14. [Benchmarking](design/manuscript/chapter-14/chapter-14.md)
15. [Performance Engineering](design/manuscript/chapter-15/chapter-15.md)
16. [TCO](design/manuscript/chapter-16/chapter-16.md)

### Part V — The Fleet

17. [From Server to Fleet](design/manuscript/chapter-17/chapter-17.md)
18. [Operating Multiple Models](design/manuscript/chapter-18/chapter-18.md)
19. [Agentic Systems](design/manuscript/chapter-19/chapter-19.md)
20. [Fleet-Level Optimization](design/manuscript/chapter-20/chapter-20.md)
21. [The AI Factory](design/manuscript/chapter-21/chapter-21.md)

### Part VI — The Architect

22. [How to Think Like an AI Solution Architect](design/manuscript/chapter-22/chapter-22.md)
23. [Working With Customers](design/manuscript/chapter-23/chapter-23.md)
24. [Red Team / Green Team](design/manuscript/chapter-24/chapter-24.md)
25. [The Architecture Decision Record](design/manuscript/chapter-25/chapter-25.md)
26. [The Solution Architect's Toolkit + Patterns Library](design/manuscript/chapter-26/chapter-26.md)

### Appendix

27. [Appendix A — 2026 Frontier Architectures](design/manuscript/chapter-27/chapter-27.md)

---

## Evidence rule (binding)

Every quantitative claim carries **two orthogonal labels** (per the architecture §5):

> **Source** — *where the number came from*:  
> **[1P]** first-party to the subject (model vendor's spec / model card)  
> **[2°]** reputable second-hand (textbook, survey, third-party benchmark report)  
> **[VERIFY]** not yet anchored — a *status*, resolved before publication (promote / drop / demote)
>
> **Claim type** — *whether it was computed*:  
> **FACT** directly stated by the cited source · **DERIVED** calculated from documented facts · **HYPOTHESIS** reasoned conclusion
>
> **Home-lab experiments are not reference.** Worked examples may appear, clearly labeled as "worked example, not reference."

---

## Render

Build tooling lives in [`render/`](render/). Two pipelines share one manuscript and one set of source figures:

- **LaTeX PDF** — `render/latex/emit_book.py` assembles `book.tex` (title page → preface → TOC → 27 chapters), `render/latex/md_to_latex.py` converts each chapter, and `xelatex` produces the PDF. All figures are embedded as **vector PDF** (28 matplotlib + the hand-drawn rough.js figures hardened to SVG/PDF). [Download `from-token-to-fleet-v20260831.pdf`](render/build/from-token-to-fleet-v20260831.pdf)
- **Self-contained HTML** — `render/make_html.py` renders the whole book as one dark-mode, dependency-free HTML file with every figure inlined (SVG first, PNG fallback) as base64 data URIs. [Download `from-token-to-fleet-v20260831.html`](render/build/from-token-to-fleet-v20260831.html)

Deliverables land in `render/build/` named **`from-token-to-fleet-vYYYYMMDD.{pdf,html}`** — the date is the version (e.g. `from-token-to-fleet-v20260831.pdf`).

```
python3 render/make_html.py                 # -> render/build/from-token-to-fleet-v<date>.html
# LaTeX:
cd render/latex && python3 emit_book.py     # -> book.tex
python3 md_to_latex.py                      # -> chapters/*.tex
xelatex -interaction=nonstopmode book.tex   # (3 passes) -> render/build/...pdf
```

The `render/fig_*.py` scripts regenerate the matplotlib figures (vector of each); `render/harden_kv_svg.py` converts the hand-drawn rough.js figures to static SVG/PDF.

---

## Craft — how we build the book

The book is the *what*; [`craft/`](craft/) is the **how**. It publishes our working
methods — the pipelines, rules, and hard-won lessons that produce these deliverables —
so the build process itself is as inspectable as the content. See [`craft/README.md`](craft/README.md)
for the index, and [`craft/archify-diagram-craft.md`](craft/archify-diagram-craft.md)
for the figure pipeline in full.

Contributing? Start with [`CONTRIBUTING.md`](CONTRIBUTING.md) — it covers the
binding evidence rules, the build runbook, and the verification bar.

---

## License

This work is licensed under a **custom source-available license** (see [`LICENSE`](LICENSE)): free for personal use, study, and non-commercial redistribution with attribution — but **commercial use or publication requires the author's prior written approval**. It is not an open-source license. For permission, contact Zhiqi Tao.
