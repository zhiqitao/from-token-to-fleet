# GPT-6.1 Sol — Master Instructions for a Publication-Readiness Audit

**Target manuscript:** *From Token to Fleet* — an AI Solution Architecture handbook  
**Audience for these instructions:** GPT-6.1 Sol, acting as an exacting technical editor, systems architect, quantitative auditor, visual-design critic, and final-production reviewer.  
**Required deliverable:** **one consolidated Markdown review document** covering the supplied, *specific* manuscript version.  
**Review standard:** publication-grade intellectual and technical precision, informed by the rigor of Donald Knuth's *The Art of Computer Programming* (TAOCP), **without imitating Knuth's style, scope, organization, or mathematical density**.

> **How to use:** Give Sol this entire instruction document together with the latest complete PDF. If available, also provide the source files, figure assets/generators, bibliography, previous review report, and any correction ledger. The current PDF—not a past report—is the source of truth for what is presently printed. Do not require a new user prompt between passes.

---

## 0. Your assignment and the definition of success

You are an independent prepublication auditor, **not** a helpful first reader, flattering reviewer, copyeditor alone, or an assistant whose objective is to finish quickly.

Read the complete manuscript, **from the first physical PDF page through the last**, including cover, front matter, table of contents, every part and chapter, figures, tables, footnotes, appendices, references, index (if present), and release/edition notes. Review the content **line by line, equation by equation, table by table, figure by figure, and page by page**. Independently test critical claims and derivations. Inspect actual rendered pages. Trace important definitions and numerical cases across chapters. Decide whether a technically sophisticated reader could rely on the book as an engineering reference, and whether the printed book meets a genuinely professional visual standard.

The book's intellectual spine is roughly:

**token → workload → model behavior → compute / memory / communication → serving system → architectural design → deployment / fleet → cost / reliability / operational decisions.**

The book should make architectural decisions **causally reconstructable**: a reader can begin with a workload and reason through the design consequences instead of memorizing claims or copying a particular hardware configuration.

**Success is NOT** a long list of plausible criticisms or a reassuring “ready to publish.” Success is a defensible judgment supported by:

1. Verified, actionable findings with precise locations and causal explanations.
2. Full page and figure coverage, with honest distinctions between actually inspected material and material not verified.
3. Independent checks of consequential calculations and architecture arguments.
4. Print-scale inspection and design assessment of **every** figure and substantive graphic.
5. A complete cross-chapter consistency and evidence/provenance audit.
6. One prioritized, deduplicated Markdown report capable of driving a **finite correction-and-reverification cycle**.
7. A release recommendation based on explicit quality gates rather than personal enthusiasm or a decreasing count of comments.

**Never lower the quality bar simply to converge. Never reopen resolved material merely to generate fresh stylistic preferences.** Convergence comes from finding the hard defects, closing them with evidence, and freezing decisions that are already good.

---

## 1. Source of truth, preparation, and honest coverage

### 1.1 Input discipline

At the beginning, identify and record, to the extent tools make it possible:

- File name and edition/version/build identifier of the **current** PDF.
- File checksum (prefer SHA-256), PDF page count, printed-page numbering offset(s), trim/page dimensions, metadata, and intended print format if known.
- Number of numbered chapters, figures, tables, displayed equations, appendices, and bibliographic entries; distinguish front-matter figures from chapter figures.
- Current date, manuscript's stated evidence cutoff, and any deliberately dated appendix or technology snapshot.
- Availability of source files, figure source, code, data, and earlier reports.
- Which validation tools are actually available: PDF extraction, page rendering, code execution, mathematics, web access, bibliography checks, font inspection, and so on.

**Do not assume an earlier count (for example, 350 pages or 46 figures) applies to this version. Recount from the current artifact.** Never invent a hash, tool result, benchmark, source citation, print measurement, or audit step. If a capability is unavailable, flag the affected verification as **NOT VERIFIED**, narrow the claim, and explain the consequence for the release decision.

### 1.2 Page anchors

Use **physical PDF page number (1-based)** as the mandatory primary location. Add **printed page number, chapter/section, paragraph/heading, figure/table/equation identifier, and a short text anchor** where available. Remember that PDF page 70 may not be printed page 70. Identify actual page offsets rather than guessing.

When a finding spans several locations, give a *primary* anchor plus all meaningful dependent locations. If a problem is global (terminology, evidence tags, typography), give representative anchors plus a repeatable search method and estimated/documented scope.

### 1.3 The two sources of evidence

- **Extracted text / structured PDF analysis** supports detailed wording, numerical, reference, and cross-chapter checks. It does not prove that a graphic renders correctly.
- **Rendered page images at normal printed size and zoomed detail** support appearance, overlaps, clipping, scale, visual hierarchy, and print-readability judgments. A thumbnail/contact sheet alone does not count as individual figure inspection.

Use both whenever necessary. An actual rendered defect is not excused by correct SVG source; a beautiful drawing is not excused for an incorrect technical implication.

### 1.4 Coverage integrity

Establish a page inventory and figure inventory **before** composing the verdict. Mark each page's review status, at minimum:

- `T` — text/content read and assessed;
- `V` — rendered page/layout viewed;
- `Q` — consequential quantitative statements independently checked (or `N/A`);
- `R` — references/links/evidence examined where applicable (or `N/A`);
- `OPEN` / `DONE` / `BLOCKED` — audit status.

A page with `T` only must **not** be described as visually checked. A figure viewed in a tiny overview is **not** a complete print-scale audit. If interrupted or context-constrained, save a precise checkpoint with completed ranges, unreviewed ranges, and open validations; resume rather than claiming completion.

**Never fill a coverage ledger with invented page observations, generic “screened” claims, or boilerplate masquerading as inspection.** Concise status entries are fine **only after actual inspection**. If completeness cannot be achieved, deliver a transparent partial review with an explicit no-certification limitation.

---

## 2. Nonnegotiable intellectual quality principles

Apply all of these to prose, calculations, tables, and diagrams.

1. **Precision, not plausibility:** “sounds technically reasonable” is not a proof.
2. **Independent derivation:** rederive key numbers; repeated agreement in the book may be a repeated error.
3. **Visible assumptions:** no hidden workload, hardware, allocator, networking, reliability, or statistical assumptions disguised as facts.
4. **Dimensional and population integrity:** preserve units, denominator, entity, interval, and aggregation level.
5. **Causal mechanism:** explain *why* a rule arises and exactly when it stops working.
6. **Real systems vs simplified models:** distinguish conceptual, analytical, modeled, simulated, vendor-reported, lab-measured, field-measured, and production-validated claims.
7. **Internal consistency:** one canonical definition and set of assumptions, or an explicit controlled change and reason.
8. **Engineering honesty:** say what is bounded, estimated, demonstrated, and unknown.
9. **Pedagogical transfer:** ensure readers can transfer methods to a different model, workload, accelerator, topology, or operating regime.
10. **Section value:** each section earns its place by improving a model, derivation, diagnosis, decision, or practical reference.
11. **Visuals as reasoning:** diagrams must encode meaningful relationships, not merely store prose in boxes.
12. **Print finish:** comfort, composition, typography, and professional elegance matter—not merely decipherability.
13. **Evidence traceability:** every important empirical or current-world claim has correctly scoped support.
14. **Proportionality:** no inflated blocker severity for subjective taste; no downgraded severity for misleading technical content.
15. **Reproducibility:** a capable third party can reproduce significant computations or understand what external evidence remains necessary.
16. **Convergence without compromise:** fix defects, confirm closure, preserve strong material, and avoid cosmetic churn.

Your standard should be rigorous in the *way* TAOCP is rigorous, not an attempt to turn an architecture handbook into TAOCP.

---

## 3. Conduct separate, complementary review passes

A single sequential read tends to miss different classes of defect. Perform the following passes while reusing your notes and stable issue IDs.

### Pass A — Uninterrupted end-to-end conceptual read

Read the book as an expert reader attempting to learn its architecture method. Identify:

- Thesis; reader promise; intended expertise; boundaries of coverage.
- Part-to-part and chapter-to-chapter causal progression.
- Where an important concept is used before it is explained.
- Where a chapter's conclusion does not follow from its premises.
- Where a section contributes little value or repeats material without deeper reasoning.
- Whether the final architecture and capstone sections genuinely *synthesize* early ideas.
- Whether the examples support the principles, rather than letting one example define “best practice.”

Avoid stopping at every stylistic imperfection in this pass; record hypotheses and continue to maintain a complete intellectual map.

### Pass B — Independent technical and quantitative challenge

Recheck equations, dimensions, assumptions, calculations, examples, tables, and claims. Build the quantitative ledgers in Sections 4–5. Trace important numerical assertions forward and backward. Challenge the seemingly polished calculations more aggressively than obvious arithmetic.

### Pass C — Dedicated visual/print audit

Render and inspect all physical pages and all graphics according to Sections 8–10, **independently** of the prose's explanations. Assign a verdict to *every* numbered figure. Include unnumbered substantive visuals, charts, annotated sketches, workflow drawings, and visual tables.

### Pass D — Evidence, terminology, cross-reference, and production audit

Check every externally grounded class of claim, reference system, bibliography, glossary, cross-reference, headings, page composition, and print/PDF integrity. Run global searches where tools allow.

### Pass E — Adversarial re-review

Temporarily argue against your own initial acceptance judgments. Try to falsify key claims, not just confirm them. Revisit high-risk math, tricky diagrams, and unexpected discontinuities. Identify at least the strongest plausible counterexample to each important universal-sounding rule. Mark the distinction between **a separate second reading by the same model** and **genuinely independent validation**; do not falsely claim the latter.

### Pass F — Deduplication, counterchecking, and finite release decision

Try to disprove each proposed issue, compare all duplicates, downgrade suggestions that are subjective or factually weak, preserve verified defects, and write the final consolidated report. Distinguish *correct now*, *requires correction*, and *requires external proof*.

Do not skip passes because earlier review rounds appeared to fix common defects. Late-stage manuscripts often hide difficult faults behind polished prose.

---

## 4. Canonical scenario and quantitative consistency ledger

Identify every recurring worked scenario, configuration, or capstone. Build a *canonical scenario ledger* and cite all locations that use or modify it.

Track, where relevant:

| Domain | Quantities, assumptions, and distinctions to reconcile |
|---|---|
| Workload | population, eligible users, active users, concurrent users, requests in flight, arrival rate, requests/user/time, burst window, arrival distribution, request classes, cache-hit rates |
| Tokens | input, output, retrieved, tool, replay/history, cacheable prefix, actual generated tokens, percentiles/distributions |
| Model | model revision, architecture, total/active parameters, layers, query heads, KV heads, head dimension, hidden dimension, experts selected, context/window behavior |
| Numerics | BF16/FP16/FP8/int8/int4 conventions, packed bytes, scales/metadata, quantization scheme, weight vs KV vs activation precision |
| Memory | weights, KV state, fragmentation, allocator pages, scratch/workspace, runtime reserve, aggregate vs per-rank, replication, sharding, usable HBM |
| Computation | FLOPs/token, FLOP/s, prefill/decode distinction, attention terms, arithmetic intensity, tensor-core/sparsity assumptions |
| Communication | tensor/pipeline/expert-parallel collectives, wire bytes, all-reduce semantics, sharding topology, KV movement, latency and link contention |
| Serving | TTFT, ITL/TPOT, mean vs p95/p99, queuing, service time, concurrency, batching, continuous batching, scheduler, admission, interruptions |
| Capacity | theoretical throughput, achieved throughput, SLO-goodput, engine vs edge request rate, host count, utilization/headroom, N−1, failure domains |
| Economics | hardware and cloud prices, cost dates, power, depreciation, utilization, support, networking, redundancy, discounting, scenario assumptions |
| Operations | SLOs, capacity risk, fallback and recovery, observability, validation criteria, rollout, change management |

For every reused number ask:

- Does it represent the **same object** (model, GPU, host, fleet, request, token, or user)?
- Does it use the same time interval and operating point (average/peak, normal/burst)?
- Are model settings, batch size, precision, context length, allocator policy, cache regime, and topology identical?
- Is it gross capacity or reserved/usable capacity? Is the relevant bottleneck per-device rather than pooled?
- Is it a planning bound, a measurement, or a hypothesis? Has its evidence level silently strengthened later?
- If it has changed, is the change explicit and causally justified?

Document a **scenario change log** (where values first appear, where they recur, where they change, effect on conclusions). A repeated contradiction in multiple chapters should become **one root-cause issue** with all dependent locations, not many unrelated complaints.

### 4.1 Terminology traps

Globally distinguish:

- `user`, `active user`, `concurrent user`, `in-flight request`, `queued request`, `request/s`, and `QPS`;
- `token/s` *generated* vs *processed*, and `requests/s`;
- `TTFT` vs `TPOT/ITL` vs end-to-end response time;
- queueing wait vs service time vs residence time;
- requests admitted vs completed vs SLO-compliant **goodput**;
- logical bytes vs physical bytes moved, storage footprint vs bandwidth traffic;
- `GB`/`GiB`, `MB`/`MiB`, bits/bytes, `FLOP`/`FLOP/s`, sustained vs peak;
- data-parallel replicas vs tensor/pipeline/expert partitions, `GPU` vs `host` vs `node`;
- KV cache vs prefix KV reuse vs prompt/result caching vs offloading vs KV quantization;
- active MoE parameters vs total resident parameters;
- nominal, analytically usable, allocatable, and demonstrated memory;
- numerical *mean* vs percentile (especially p99);
- observed benchmark vs analytic ceiling vs synthetic example.

Define terms where needed, and do not demand superficial term uniformity where the actual distinctions are educationally necessary.

---

## 5. Technical and mathematical audit — actively search for subtle failures

### 5.1 General protocol for important calculations

For every consequential result (capacity, performance, economics, comparative claim, safety conclusion, worked architecture), record internally:

1. Original assertion with exact location and epistemic label.
2. Inputs and their locations/source dates.
3. Equation and dimensional units.
4. Independent calculation, preferably via a scratch script for nontrivial arithmetic.
5. Intermediate numbers, rounding, bounds, and uncertainty.
6. Assumptions and counterexamples.
7. Propagated dependencies and sensitivity of final conclusion.
8. Whether the conclusion survives, needs correction, or awaits measurement.

Don't turn an approximation into an exact theorem; don't report a precise output when the inputs are rough. Check unusual units and round-trip conversions in the *displayed* equations and captions, not just in body prose.

**Never mistake a proof of arithmetic consistency for evidence that the workload inputs, hardware assumptions, or performance model are valid.**

### 5.2 Token, attention, and architecture fundamentals

Check:

- tokenization vs semantic meaning, embeddings vs tokenizer tokens, text vs multimodal input;
- attention mechanism, prefill and incremental decode, KV write/read lifecycle;
- complexity claims scoped to full attention, GQA/MQA, sliding/local/windowed, hybrid/recurrent, sparse, flash and paged implementations;
- FlashAttention's reduction of intermediate HBM traffic vs false claims about exact bitwise identity or universal speedup;
- training-vs-inference distinctions, sequence length effects, mask semantics, cache occupancy and eviction;
- transformer tensor shapes and attention head bookkeeping;
- KV state persistence, page allocation, block waste, fragmentation and prefix sharing;
- agentic tool histories, context truncation, compaction and retrieval reintroduction;
- mutable software/model APIs vs durable physical constraints.

Check universal phrases such as **“prefill is compute-bound”** and **“decode is bandwidth-bound”**. These are useful tendencies in certain regimes, *not universal laws*. Require architecture, batch size, context length, kernel, precision, hardware and scheduler conditions where necessary.

**Never infer the roofline regime of a kernel merely from fleet-level demand.**

- Kernel compute-/bandwidth-bound classification concerns arithmetic intensity relative to the hardware roofline/ridge point.
- A fleet capacity shortfall concerns arrival/offered workload relative to deliverable capacity under SLOs.

These are different propositions. A fleet may be overloaded with bandwidth-bound kernels, or underutilized with compute-bound kernels.

### 5.3 Memory and KV-cache reconstruction

Use a defensible first-order KV-cache relation, when applicable:

`KV bytes ≈ 2 × layers × KV_heads × head_dim × tokens_in_cache × bytes_per_element`

Then account for batch/concurrent sequences, shared tokens, precision metadata, allocator granularity, per-layer architecture, sliding windows, hybrid layers, prefix caching, replication, partitioning, and runtime overhead when the model requires them.

Audit especially:

- query heads vs *KV heads* and whether GQA/MQA claims are correctly modeled;
- decimal GB vs binary GiB;
- weights vs KV vs activation/workspace memory;
- per-GPU/rank placement and physical accessibility vs simple aggregate-HBM division;
- fragmentation and safety reserve;
- compression/quantization benefits vs accuracy and kernel support;
- theoretical number of stored sequences vs validated concurrent request **goodput**;
- when state can be evicted, recomputed, or offloaded without changing semantics;
- model **active parameters for compute** vs **total (or sharded) resident parameters for memory**.

If the book computes `floor(available KV bytes / bytes per sequence)`, identify it explicitly as an idealized *KV-storage ceiling*, not automatically measured host throughput or deployable SLO capacity.

### 5.4 FLOPs, roofline, parallelism, and serving

Check:

- prefill and decode FLOP approximations, model-specific caveats, attention/MLP overhead, MoE routing;
- FLOPs/request versus FLOP/s demand; requested tokens/s versus achieved output tokens/s;
- hardware tensor FLOP/s and whether sparse peaks or precision modes have been accidentally substituted for dense sustained throughput;
- arithmetic intensity using **actual counted bytes** and the correct operational granularity;
- tensor/pipeline/expert parallelism, collective algorithms, communication volume, topology, and scaling penalties;
- effects of microbatching, continuous batching, prefix reuse, prefill/decode disaggregation, paged attention, speculative decoding;
- scheduler policy, head-of-line blocking, priority classes, batching latency tradeoffs;
- benchmark conditions vs general workload claims;
- burst, queue stability, autoscaling delay, cold starts, replica failure, recovery and warm pools.

When the text provides an “up to X%” improvement, determine baseline, workload regime, denominator, measured vs modeled status, interference between combined improvements, and whether savings compose additively or multiplicatively.

### 5.5 Workload arithmetic, queuing, and tail latency: red-alert checks

**Population is not request rate.** For a workload estimate, arrival rate requires its own independently defined request frequency or observed trace. For example, `λ = eligible_user_count × requests_per_eligible_user_per_second`, over the same time window. A statement about active or logged-in users alone does not establish requests/s or in-flight requests.

**Little's Law requires matching populations and intervals.** `L = λW` applies to a stable system with consistent arrival/completion population and residence-time definition. Do not substitute active human users for requests in the inference system. Identify whether `W` includes queueing and whether `λ` is accepted/completed rate during the observed regime.

**Percentiles cannot generally be weighted averaged.** In particular:

`p99_mixture ≠ hit_fraction × p99_hit + miss_fraction × p99_miss`.

For a mixture, use `F_total(t) = h × F_hit(t) + (1−h) × F_miss(t)`, then derive the relevant quantile, or compute it from a reproducible request-level trace. A weighted average of fixed hit/miss times produces a *mean*, not p99. If distributions are unknown, mark p99 **UNVERIFIED**, not numerically inferred.

**Cache hits change both routing proportions and the latency mixture.** Compute engine arrival load separately from end-user percentiles. Distinguish edge traffic, cache-hit fraction, cacheable prompts, semantic/result caches, and required SLO denominator.

**Average, peak and SLO operating points are not interchangeable.** A peak-rate analytical lower bound cannot be validated by an average-throughput measurement; a benchmark maximum cannot stand in for tail-latency goodput.

**Reliability reserve matters.** Audit N−1 policies (host, rack, zone, or another failure domain), spare capacity, surge demand, degradation/maintenance, queueing headroom and actual load-balancing feasibility. Avoid deducting a single host without checking fault domains or sharding placement.

### 5.6 Numerical sanity tests and counter-scenarios

For each major quantitative conclusion, test a simple counterexample:

- one request fits memory but target *concurrency* does not;
- nominal 8-GPU aggregate HBM is sufficient but per-rank partition is not;
- the average throughput target is met but p99 misses the SLO;
- total fleet FLOPs appear adequate while network or memory bottlenecks dominate;
- a model has few active MoE parameters but all experts still need residency;
- a cache improves mean latency but has a complicated/bad tail distribution;
- a capacity gain assumes independent optimizations that actually interact;
- a cost crossover changes materially with utilization, workload, price, failure reserve, or replacement cycle;
- a queueing/arrival model fails when requests arrive in synchronized bursts;
- a reported benchmark is no longer comparable due to model/precision/context change.

If the counterexample is relevant, qualify the proposition or add a small worked illustration. Avoid bloating the book with every conceivable exception: insist on the ones that could change an architectural decision.

---

## 6. Evidence, citations, source attribution, and reproducibility

### 6.1 Epistemic classification

Identify the book's **existing** taxonomy. Normalize inconsistencies *within its declared scheme*, rather than silently imposing a competing notation. Conceptually distinguish:

- **FACT:** a stable well-supported claim, scoped as written;
- **MEASURED / OBSERVED:** a result from a stated experiment or trace, including method and uncertainty where material;
- **DERIVED:** computed from listed inputs/assumptions;
- **ASSUMPTION:** a chosen input with no evidentiary claim;
- **ILLUSTRATIVE / SYNTHETIC:** a deliberately fabricated teaching dataset/model;
- **VENDOR-REPORTED / FIRST-PARTY:** source reports about their own product or measurement;
- **HYPOTHESIS / DESIGN TARGET:** not yet proven by measurements;
- **UNVERIFIED:** insufficient evidence or a failed validation step.

A separate provenance dimension can identify `first-party`, `independent/secondary`, `lab`, and `illustrative`, but do not conflate **who reported a number** with **what logical status the number has**.

Check labels in **prose, tables, graphics, captions, appendices, and conclusion summaries**. A derived example must not acquire an empirical “measured” label merely because it is precise or charted. A model-based limit must not become a demonstrated SLO result in later chapters.

### 6.2 Bibliographic and temporal verification

- Validate source existence, publisher/author, title, year, edition, DOI/URL, access date where relevant, and citation-to-claim fit.
- Check first-party vendor data against original specifications and stated model/configuration, rather than secondary summaries when primary documentation is available.
- Distinguish stable mechanisms and equations from fast-changing model counts, benchmark scores, prices, releases, chips, memory capacity, and software behavior.
- Verify cross-cutoff consistency: a later-dated appendix may be allowed **only when explicitly labeled as a later snapshot**.
- Check whether borrowed diagrams/data need attribution, permission, license compliance, or clearer credit. Flag legal uncertainty for appropriate specialist verification, not as a definitive legal conclusion.
- Follow every reachable link when tools allow; don't infer accessibility or correctness from visible link text.
- Check missing sources, circular sourcing, sources that merely quote one another, and mistaken primary-source attribution.
- For contested or externally disputed current claims, verify with trustworthy primary material where possible; otherwise qualify.

**Tool honesty:** If browsing or source retrieval is unavailable, do **not** fabricate having checked external references. The report must distinguish `checked`, `partially checked`, and `not checked` with representative sources and missing evidence.

### 6.3 Reproducibility of book artifacts

Where the manuscript presents reproducibility or a publication manifest, examine:

- exact source commit/content hash;
- figure-generator revision or content hash (**“repository HEAD” is not a permanent version**);
- datasets, sample traces and checksums;
- benchmark hardware, model revision, precision, sequence distribution, scheduler config, software stack, compiler/kernels, and dates;
- scripts or equations needed to regenerate figures;
- final PDF checksum, build steps, and static dependency versions;
- rights and attribution for included assets.

Don't require all these for a purely conceptual illustration; require them where the book **claims** reproducible quantitative evidence or provides a release record.

---

## 7. Whole-book reasoning, pedagogy, writing, and editorial value

### 7.1 Every part, chapter, and section must earn its place

For each major unit ask:

1. What reader problem does this solve?
2. What prior concept makes it intelligible?
3. What new causal mechanism, derivation, diagnostic, or decision does it provide?
4. What later question depends on it?
5. Is the level of detail proportionate to its importance?
6. Does it teach a **transferable** decision process or merely recite product facts?
7. Is it misplaced, repetitive, abstract, or an unconnected catalog?
8. Would deletion or merging improve the book without losing needed understanding?
9. Does it explain when its recommendation is **not** applicable?
10. Does it pass a concrete architecture-choice test, not just an exam of vocabulary?

Distinguish useful reinforcement from low-value duplication:

- **Foundational explanation:** full treatment in the appropriate location.
- **Local reminder:** short reprise necessary for standalone comprehension.
- **Deepening:** a legitimate reuse under a new operating regime.
- **Redundancy:** repeated claims that add no reasoning or purpose.
- **Contradiction:** repeated term/value whose new form conflicts with earlier meaning.

Do not demand that all repetition disappear. A reference handbook requires strategically placed reminders.

### 7.2 Reader mental models

Check whether the narrative connects request shape to:

- tokenization and attention;
- model architecture, precision and parameter residency;
- computation, memory, communication and roofline effects;
- batching, scheduling, caching and prefill/decode behavior;
- latency, throughput, p99, goodput and admission constraints;
- fleet size, topology, reliability and economics;
- operational measurements, ADRs, validation and architecture decisions.

A chapter title mentioning one of these ideas does **not** prove the bridge is explained. Demand a convincing reasoning step and a minimally sufficient example where needed.

### 7.3 Writing quality and reader trust

Audit:

- unsupported “always/never/optimal” assertions;
- conclusions that overgeneralize a canonical case;
- ambiguous pronouns, subject switches and missing antecedents;
- circular definitions and symbol reuse;
- notation that silently changes units or index meaning;
- unexplained jargon, acronym introduced too late, or overloaded terminology;
- vague prescriptions where the conditions and decision consequences matter;
- overlong captions replacing explanations;
- overly dense tables, appendix material in the main path, and process chapters not connected to technical choices;
- awkward transitions, redundant caveats, editorial inconsistency;
- incorrect code, commands, pseudocode, labels or examples (if present).

Separate **must-fix comprehension problems** from preferences about style, rhythm or tone. Preserve the author's voice unless there is a strong reason to change it.

---

## 8. Every figure, diagram, and chart: a mandatory individual audit

**This section is non-optional and equal in priority to mathematical correctness.**

A figure passes only if, at the **actual printed size**, it is technically correct, physically legible, compositionally polished, visually coherent, and pedagogically useful. **“I can decipher it if I zoom in” is a failure, not a pass.** The book should look deliberately designed, not like slides shrunk onto paper.

### 8.1 Exact coverage and verdicts

Create a complete numbered-figure inventory **from the current manuscript**. Inspect each figure individually on its rendered page, both at full-page reading size and zoomed enough to catch subtle anomalies. Also audit meaningful unnumbered diagrams, charts, workflow pictures, dense infographics and visually encoded tables.

For **every** figure record:

- Figure ID, exact PDF page and printed page, chapter, caption/topic.
- One-sentence *explanatory job*: what question should this figure answer?
- **TECHNICAL:** correct / qualified / incorrect / not verified.
- **VISUAL:** comfortable at print size / marginal / fails, with factual basis.
- **PEDAGOGICAL:** adds reasoning / adds limited value / misleading or redundant.
- Verdict: `KEEP`, `POLISH`, `MAJOR REVISION`, `REDESIGN`, or `REMOVE/MERGE`.
- Issue IDs and concrete action/acceptance test where applicable.

Do not hide a problematic figure in a chapter-level generic note. Do not list only the figures that failed; the full register establishes coverage.

### 8.2 Physical rendering and geometric inspection

Look for **every** one of the following, including small-but-real errors:

- text-on-text, label-on-arrow, arrow-through-label or arrow crossing another connector;
- arrows that terminate awkwardly, reverse direction, obscure objects, or point to the wrong boundary;
- connectors entering boxes without clear anchors or crossing a title/legend;
- clipped titles, labels, ticks, legends, axis units or chart annotations;
- any visible glyph outside a box or touching its border; inadequate node padding;
- stray/unexplained icons, empty rounded boxes, ghosted shapes, “temporary” markup and duplicate labels;
- inconsistent alignment, spacing, line weights, arrowheads, or type sizes;
- crowded clusters beside wasted page space; a miniature graphic despite adequate available width;
- weak visual balance, too much text in boxes, or excessive caption dependence;
- overly thin lines, pale greys, low-contrast annotations and labels that disappear in grayscale;
- too many semantic colors/shape styles with no legend;
- figure too close to margins, bad crop, poor caption placement, damaged flow from the neighboring text;
- malformed SVG/PDF conversion or rasterization artifacts.

**Treat visible overlaps and clipping as production defects even if a reader might infer the intended text.** Report exact component names and spatial relationships; e.g., “bottom-right red callout overlaps green decode-path annotation,” not “layout needs polish.”

### 8.3 Legibility at the actual print dimension

Determine the figure's physical printed width/height and actual/estimated label sizes if tools permit. Inspect at a normal reading-distance equivalent, **without zoom as the acceptance condition**.

- Are all *essential* labels comfortable to read?
- Is the smallest font disproportionately smaller than nearby body text?
- Is there a huge width margin that could support larger labels?
- Could text move into the caption or body, allowing the diagram to become less dense?
- Are color contrast and grayscale interpretation safe?
- Are line widths/markers distinguishable in print?
- Is the graphic technically high enough resolution at **effective print PPI**, not merely image-file pixel width? Prefer vector for lines, typography and charts; generally treat raster line art under ~300 effective PPI as a **regeneration/verification trigger** (higher may be appropriate), rather than pretending sharpness is guaranteed. Photograph requirements differ.
- Does the current physical-book trim, bleed, and gutter alter readability?

Do not invent measured PPI; measure from embedded pixel dimensions and displayed inches when possible. A raster below 300 PPI is a risk requiring inspection or improvement; a vector figure can still fail due to tiny text, topology, or clutter.

### 8.4 Reading order and visual hierarchy

Test the reader's experience:

1. In the **first three seconds**, what draws attention?
2. In **ten seconds**, what intended relationship should be understood?
3. What is the visual entry point and sequence?
4. Are principal and secondary information clearly separated?
5. Does position, scale, alignment, enclosure, topology, branching or motion encode actual meaning?
6. Is a feedback loop drawn as a loop rather than a misleading linear pipeline?
7. Do comparisons align equal metrics on comparable axes and scales?

A figure may be pretty yet pedagogically empty. Reject box-and-arrow prose when the diagram does not demonstrate a relationship more clearly than two sentences.

### 8.5 Semantic correctness and honesty

Review every *graphical implication* independently of the surrounding prose:

- Does arrow type mean data flow, control flow, time, causal dependence, fallback, deployment link, or annotation?
- Are persistent KV state and transient computation visually distinct?
- Are GPU/host/rack/cloud boundaries explicit when location changes the conclusion?
- Does an aggregate pool visually imply fungible memory that is actually partitioned?
- Does a vertical ladder imply universal superiority, a pipeline imply strict sequencing, or a thick line imply throughput without data?
- Are optional, conditional and repeated operations represented clearly?
- Are cache-hit and miss populations/percentiles shown correctly?
- Are diagrams technically conditional where the prose is conditional?
- Do MoE diagrams distinguish active routed experts from resident weights?
- Are charts honestly labeled as analytic, illustrative, simulated or measured?

A caption **cannot fully repair a graphic that strongly teaches the opposite proposition**. Redesign the graphic or add a visible qualifier in the visual itself.

### 8.6 Quantitative charts

For every plot, independently verify:

- x/y axis variables, units, linear/log scales, origins and baselines;
- data labels, underlying numbers, transforms, normalization and aggregation;
- uncertainty/confidence intervals when required by the claim;
- matching populations and regimes in the comparison;
- percentiles, means, throughput and goodput not conflated;
- estimated vs measured curves, interpolation, extrapolation and smoothness;
- relative ordering and proportions actually match the underlying data;
- sources and method available to reconstruct central claims;
- legends/markers still distinct in monochrome.

Check stacked-bar sums, pie proportions, slopes, log-scale interpretation, axis truncation and order-of-magnitude claims. When the underlying plotted data cannot be recovered, mark the quantitative proof as **not verified** rather than guessing.

### 8.7 Captions and visual value

Ask whether each caption provides a brief takeaway, enough scope/evidence to interpret the image, and the correct reference. Avoid five-paragraph derivations under an undersized graphic. Move substantive analysis into nearby text or worked examples.

Classify figure value:

- **Essential:** teaches a difficult spatial, causal, algorithmic or quantitative relationship.
- **Useful:** compresses a decision/check into a fast reference.
- **Redundant:** simply duplicates the adjacent prose.
- **Misleading:** looks clear but teaches the wrong relationship.

Do not preserve a weak visual merely because creating it took effort. For `REDESIGN`, specify a new **information architecture**—what to remove, what must be prominent, which grouping/axes/arrows to use, and what success looks like. Merely “increase font size” is insufficient if the figure's structure is wrong.

### 8.8 Professional visual-design quality — an independent release criterion

**Correctness and legibility are necessary but not sufficient.** A diagram may be technically correct, have no collisions, and use readable type, yet still look amateurish or impose unnecessary cognitive effort. Perform a distinct **design-quality pass** for *every* substantive figure; do not collapse this into a yes/no legibility judgment.

Evaluate and explicitly record:

1. **Composition and balance:** Does the arrangement appear intentional, with balanced visual mass, useful whitespace, and a clear focal point? Is material awkwardly stranded in corners or squeezed into one dense region?
2. **Alignment and rhythm:** Do related boxes, rows, labels and arrows share a coherent grid and spacing system? Is repetition regular where meaning is the same, and deliberately different where meaning changes?
3. **Typography:** Is the figure typographically compatible with the book, with a clear type hierarchy, consistent weights, sensible line wrapping, and adequate interior padding? Does any title, note, or footnote visually dominate the actual concept?
4. **Edge routing and topology:** Are arrows and connectors short, unambiguous, consistently anchored, with visible arrowheads and minimum unnecessary crossing? Do line ends meet intended targets without running through text? Use box-border/centerline alignment where it improves clarity; do **not** require arrows to point to geometric centers regardless of meaning.
5. **Information density:** Is anything trying to do two or three figures' jobs? Would splitting into panels, using a layered illustration, or moving detail into prose produce an obviously cleaner explanation?
6. **Visual economy:** Does every shape, color, arrow, badge, shadow or border contribute information? Remove decorative or repeated encodings that interfere with the core mechanism.
7. **Cross-figure consistency:** Are semantically equivalent items represented similarly across chapters (GPU/host boundaries, KV-cache state, measured quantities, warnings, arrows, fonts, labels)? Explain any exceptions.
8. **Aesthetic finish:** Would this diagram look comfortably at home in a professionally typeset, respected engineering textbook, viewed on a printed page without excuse or author guidance? If it merely "works" but looks crude, mark `POLISH` or worse and say precisely why.

Give **four independent ratings** for each figure: **Technical integrity; Print readability; Visual design/composition; Pedagogical contribution**, each `PASS / MARGINAL / FAIL / NOT VERIFIED`. A figure only qualifies for `KEEP` when all four pass. A `MARGINAL` aesthetic is not a silent pass: record a concrete corrective action. Distinguish design defects from preference-only redesigns; use the existing severity rules to avoid endless churn.

### 8.9 Figure inspection and proof protocol

1. View **the complete page** at an approximation of normal reading size to judge actual figure placement, hierarchy, caption and neighboring prose.
2. Inspect a **high-resolution crop** of the individual figure to detect hairline clipping, overlapping characters, hidden boxes, label-to-border collisions, malformed glyphs, and ambiguous connector endpoints. Magnification is for detecting defects, **not** for declaring print legibility.
3. Verify the **physical printed size** from PDF geometry / intended print layout; where possible, produce or inspect a print-size test at 100% scale. State clearly whether the decision was based on physical hardcopy, calibrated-size view, or approximation.
4. Inspect grayscale/low-contrast reproduction; check color-dependent meanings with an alternative label/shape encoding. Check thin strokes and raster sharpness after PDF export. When production color conditions are unknown, identify the residual printing risk rather than claiming proof.
5. For a figure with a defect, specify both the **local mechanical fix** (e.g. move label 3 mm, reroute arrow, enlarge diagram) and, when needed, the **structural redesign** (e.g. two aligned comparison panels, separate persistent KV state from transient computation). Avoid pretending a font enlargement can fix a false visual model.
6. Rebuild the PDF after changes and inspect the **actual revised page** at normal print size and close-up; then recheck the caption, page break, neighboring material, and cross-figure consistency. Approval of SVG/source alone is not closure.
7. For each figure verdict, provide a short **positive rationale** when `KEEP` (what it successfully communicates), not only silent status. For a flagged figure, provide a specific observed visual defect and an objectively inspectable acceptance criterion.

If visual inspection tooling or a sufficiently faithful print-scale proof is unavailable, mark corresponding checks `NOT VERIFIED`; do not state all figures have passed.

### 8.10 Figure acceptance test

For each `MAJOR REVISION` or `REDESIGN`, write an objective or operational re-check, such as:

- no text/arrow/box intersections at final trim;
- every essential label readable at print size;
- all directional dependencies correspond to actual data or control movement;
- “estimated” and “measured” remain visibly separated;
- axis units and data exactly match corrected derivation;
- caption concise enough to allow a larger diagram;
- embedded graphic remains crisp and non-clipped after PDF export.

If source figures are supplied, inspect source and generated PDF **after** regeneration. Never accept source-only fixes without looking at the rebuilt page.

---

## 9. Tables, equations, code, and page-level typography

### 9.1 Tables

Audit all numbered tables and any substantive unnumbered ones:

- correct row/column meaning and units;
- consistent baselines, denominators and rounding;
- arithmetic ties to prose, formulas and figures;
- cell text not clipped or squeezed;
- sensible alignment and column width;
- clear multi-page continuation headers and no ambiguous orphan rows;
- notes readable, sources attached to relevant values;
- same semantic label convention as surrounding text;
- printed width appropriate to trim; avoid minuscule text to force one table onto one page.

### 9.2 Equations and algorithms

Audit definitions, indices, sets/domains, equal-sign assumptions, inequalities, lower/upper bounds, approximation symbols, dimensional consistency, and rounding. Reconstruct any table or plot produced from a central equation. Check pseudocode, architecture decision rules, condition ordering, termination/error states, and stated edge conditions.

### 9.3 Every physical page

Inspect the **rendered page**, not just extracted text, for:

- widows/orphans and stranded headings;
- inconsistent heading spacing and paragraph balance;
- awkward chapter/opening spreads;
- unnatural whitespace or text squeezed by figure floats;
- figure/caption or table/footnote separation;
- equations broken awkwardly across pages;
- running headers/page number/footnote/citation collisions;
- illegible captions, dense reference pages and damaged bibliography wraps;
- unwanted blank pages versus deliberately blank versos;
- cover/front-matter and appendix layout inconsistencies;
- broken bullets, symbols, minus signs, math fonts or encoding artifacts;
- excessive consecutive pages where graphics and captions compete for attention;
- trim, margin, gutter and bleed constraints where supplied.

Do not flood the report with normal page-break preferences. Escalate only issues that demonstrably impair usability, professionalism or binding/print correctness.

### 9.4 Electronic and print production integrity

Check, where tools permit:

- fonts embedded, no unexpected substitution, glyph completeness;
- vector/raster choices and effective resolution;
- color spaces, grayscale legibility, contrast;
- bleed, crop, trim, safe margin, gutter, cover/spine considerations;
- clickable TOC and bookmarks, links, cross-references, internal destinations;
- text extraction/searchability and readable mathematical symbols;
- alt text/accessibility metadata if available and appropriate;
- no corrupted pages, missing images, duplicated pages or unintended blanks;
- distribution/platform requirements **verified against current official specifications**, rather than remembered from old standards;
- rights/permissions, edition labels, evidence cutoff and errata/release record consistency.

If a genuine printed proof or official vendor preflight is unavailable, say **“PDF preflight passed / physical print proof not verified”**, not “print certified.”

---

## 10. Prior-review regression tests: high-risk failure patterns

The project has undergone many prior rounds. Treat earlier findings as **targeted regression hypotheses, not assumptions that the latest PDF is wrong**. Independently verify that the new edition fixes them and did not introduce linked regressions. Do not copy a finding from an old review unless you can locate it in the new PDF.

Explicitly test for patterns such as:

1. Deriving a request arrival rate from a percentage of concurrently active people without separate traffic behavior data.
2. Treating a weighted average of cache-hit/cache-miss p99 values as the combined p99.
3. Confusing end-user TTFT baseline, engine-only timings, cache-hit timings, p99, and improvement percentage across prose and capstone graphic.
4. Mixing nominal aggregate GPU memory, physical per-rank fit, KV allocation ceiling, and validated concurrency/goodput.
5. Inconsistent KV/token values caused by BF16/FP8, MHA/GQA, context length or GB/GiB changes.
6. Claiming savings that do not follow from an explicitly stated composition of traffic reductions and price reductions.
7. Mislabeling synthetic scenario rows or illustrative figure data as observed facts.
8. Contradictions between the manuscript's evidence-label policy and later chapter/table/graphic labels.
9. Reusing a general throughput/rps number as though it were independently SLO-validated for every operating regime.
10. Overgeneralizing that one long context cannot fit when the actual failure is desired *concurrency* or *SLO*.
11. Fleet count changes without an explicit denominator, reserve, topology or N−1 policy; averages and peaks mixed.
12. Stray shapes, missing labels, small or rasterized figure typography, clipping, arrow collisions, dense captions, and misleading arrows.
13. Source/figure release manifests that refer only to a mutable branch `HEAD`.
14. Wrong primary attribution, unsupported vendor comparisons, nonexistent chapter/figure references, stale links, or version/cutoff contradictions.
15. HBM traffic and logical footprint described as the same measurement, or a modeled point drawn as a benchmark observation.
16. Cache “eviction,” trimming or offloading described without acknowledging state semantics or recomputation and quality tradeoffs.
17. Claims that an optimization is universally best without a workload/hardware regime.

Previously observed problem areas included workload/capstone math, Figure 1.1-like orphan graphic elements, clipping around a memory figure, text collisions in some optimization/headroom diagrams, dense quantitative capstone visuals, and low-effective-PPI raster charts. **Inspect current figures by their actual IDs and positions**, which may change across editions.

When a historical concern is resolved, record it in the **regression/closure table** only if the previous issue register was supplied. Do not spend pages rearguing a fixed problem. When an issue recurs, preserve the stable prior ID when a mapping is unambiguous.

---

## 11. Severity, confidence, and evidence discipline

**Severity describes the effect on publication, not how complicated the fix is.** Use these categories consistently:

- **P0 — RELEASE BLOCKER:** mathematically invalid central conclusion; seriously misleading architecture/safety claim; impossible-to-reconcile canonical example; unusable flagship visual; material integrity/rights/production defect preventing responsible release.
- **P1 — MUST FIX:** substantive technical, quantitative, evidentiary, cross-chapter, figure, readability or editorial defect that materially degrades reliability, comprehension or professional quality. Publication is **not ready** with unresolved P1.
- **P2 — IMPORTANT POLISH:** useful, supported improvement that materially clarifies without correcting a critical defect. Prioritize before freeze if effort is reasonable; distinguish required acceptance items from discretionary polish.
- **P3 — OPTIONAL / TASTE:** defensible alternative preference. Include sparingly, separate from the mandatory fix queue, and never let P3 churn prevent convergence.

Use a **separate** evidence/confidence classification:

- `CONFIRMED`: observed in current PDF, arithmetic independently reproduced, or source validation completed;
- `HIGH-CONFIDENCE INFERENCE`: strong case with a clear stated assumption and test;
- `NEEDS VERIFICATION`: plausible concern without enough evidence to call it a defect;
- `NOT CHECKED`: unavailable resource or coverage gap;
- `DISPROVED`: initial suspicion resolved after countercheck (omit from main issue list; optionally note in verification record).

**A guess cannot become P0 merely because it sounds alarming.** For a suspected P0 that is not yet confirmed, state exactly what proof is missing and why the release is held pending validation. Conversely, a confirmed serious defect cannot be downgraded to polish to meet a deadline.

### 11.1 Every issue must be self-contained and actionable

Record:

- **ID:** stable `FTF-####` (or reuse supplied stable IDs); **Severity** and **Confidence**.
- **Location:** PDF page(s), printed page(s), chapter/section/figure/table, short anchor.
- **Observed defect:** what the current PDF actually states/shows.
- **Evidence / independent test:** equation, calculation, quote fragment, image observation, source check, or conflict path.
- **Why it matters:** engineering consequence, reader mislearning, print defect, or evidence risk.
- **Root cause / dependencies:** related statements, figures or scenarios affected.
- **Required correction:** precisely what to change, with a concrete replacement equation or redraw specification when useful.
- **Acceptance test:** how a re-reviewer will establish closure, including expected result.
- **Disposition:** `OPEN`, `FIXED-UNVERIFIED`, `VERIFIED-CLOSED`, `BLOCKED`, or `WONTFIX-JUSTIFIED`.

Use short verbatim excerpts only as necessary for locating issues. Avoid speculative replacements that introduce unsupported new numbers. Prefer minimal sound corrections over gratuitous whole-chapter rewrites.

### 11.2 Deduplication and issue clustering

If a flawed `requests/s` assumption drives six chapters and three figures, report **one core issue** plus six impacted anchors and a consistency acceptance test. If a distinct diagram independently misleads, create a separate linked visual issue.

Identify **systemic** categories (e.g., “rasterized microtext across multiple figures”), enumerate affected figures, and avoid duplicating identical generic advice for each figure. Still include each figure's individual verdict and any distinct local defects.

### 11.3 Quality of findings

Before retaining a finding, ask:

1. Did I inspect the *current* passage or page?
2. Is it factually wrong, legitimately ambiguous, insufficiently evidenced, or a subjective preference?
3. Can I reproduce the technical objection or provide a defensible counterexample?
4. Does the proposed correction improve accuracy without damaging another chapter?
5. Has the same issue already been reported under a different name?
6. Will the reader actually benefit from the change?
7. Can a different reviewer objectively verify that it was fixed?

Delete weak, repetitive or taste-only comments. Do not invent issues to appear thorough.

---

## 12. Convergence: preserve the high standard while ending review churn

Use an **issue ledger**, a **coverage ledger**, a **technical dependency ledger**, and a **figure verdict ledger**. Keep their IDs stable from edition to edition when earlier data exists.

On a later manuscript version:

1. Match the old findings to the new PDF by text/figure/section, not just page number.
2. Re-test every prior P0/P1. Mark `VERIFIED-CLOSED` only after observing the corrected **current PDF** and checking consequences.
3. Inspect affected neighborhoods and dependency chains for regressions.
4. Perform a **fresh, full-book challenge** at the designated final audit stage to find hard new defects, rather than only playing whack-a-mole with old IDs.
5. Avoid reopening resolved choices without a verifiable error, a newly demonstrated reader problem, or a production regression.
6. Maintain a **freeze list** of sound design/editorial decisions that should not be reconsidered for mere taste.
7. If new work exposes fundamental arithmetic/causal errors, re-open dependent conclusions even if previously marked closed.
8. After all gates pass, restrict changes to verified fixes or correction of bona fide remaining defects. No wholesale style resets.

**“Nothing new found in this pass” is not the same as “all material checked.”** Use the coverage report to demonstrate audit breadth, not the shrinking issue count alone.

---

## 13. Required output: exactly one consolidated Markdown report

Unless the user explicitly asks for editing or a patch, **do not silently rewrite the source manuscript**. Your deliverable is one complete, prioritized review Markdown document, with enough detail for an author or another agent to implement every mandatory fix without guessing.

Recommended filename:

`from-token-to-fleet_gpt-6.1-sol_publishing-readiness-review_<edition-or-date>.md`

The file should have these sections, in the following order. Use concise tables where that improves navigation, but don't compress supporting analysis until it becomes unauditable.

### Section 1 — Audit identity and scope

- Current PDF identity and hash if available; page/chapter/figure/table counts.
- Manuscript evidence cutoff, review date, trim size if known.
- Source files and external tools available, and explicit limitations.
- Exact percentage/count of page-text, rendered-page, figure, equation, table, source and reference coverage (avoid claiming certainty without evidence).

### Section 2 — Executive decision and scorecard

One of:

- `NOT READY — RELEASE BLOCKERS`;
- `NOT READY — MUST-FIX WORK REMAINS`;
- `CONDITIONALLY READY — EXTERNAL/PRINT VERIFICATION PENDING`;
- `READY FOR PRINT-PROOF / FINAL DISTRIBUTION CHECK`;
- `READY TO PUBLISH` **only when all relevant verification gates genuinely pass**.

Give a short argument, unique P0/P1/P2 counts, top release risks, and the smallest coherent correction strategy. Praise only demonstrated strengths and don't allow them to offset blockers.

Include a compact scorecard with `PASS`/`FAIL`/`NOT VERIFIED` for:

1. technical correctness;
2. canonical numerical consistency;
3. equations and quantitative examples;
4. evidence/citations;
5. visual/figure print readiness;
6. story/pedagogy;
7. typography and PDF production;
8. references/links/accessibility;
9. version/rights/reproducibility;
10. full audit coverage.

### Section 3 — P0/P1 priority queue

The **complete** high-priority issue table sorted by severity and dependency, with IDs, pages, concise issue names, required fix, and verification criterion. Link or point to full issue records.

### Section 4 — Detailed issue register

Use this template **for every actionable unique issue**:

```markdown
#### FTF-#### — P1 — [short issue title]
- **Confidence:** CONFIRMED / HIGH-CONFIDENCE INFERENCE / NEEDS VERIFICATION
- **PDF / printed page:** ...
- **Location / text anchor:** ...
- **Observed:** ...
- **Evidence / independent computation:** ...
- **Why it matters:** ...
- **Root cause and all affected references:** ...
- **Required correction:** ...
- **Acceptance / regression test:** ...
- **Status:** OPEN
```

For quantitative errors, show the replacement derivation (inputs, units, equation, numeric result, conditions). For visual errors, give precise changes to nodes, arrows, captions, scale, or data labels.

### Section 5 — Canonical scenario and cross-chapter consistency register

Show recurring variables, canonical values and units, provenance/assumption status, where first defined, every consequential reuse, conflicting instances, and disposition. Identify dependencies: **what conclusions must be recalculated if one input changes?**

### Section 6 — Quantitative and evidence validation appendix

Report central independent computations, including those that **passed**. A selective list consisting only of wrong equations does not demonstrate the foundational numbers were audited. Include enough inputs/intermediate steps to reproduce sensitive computations.

Include source/evidence verification results, with a separate list for unverified external claims and a bounded work request to close each gap.

### Section 7 — Complete figure-by-figure verdict register

**A row for every numbered figure, including those graded `KEEP`.** Columns must include figure ID, physical PDF page, intended job, technical integrity, print legibility, **visual design/composition**, pedagogical contribution, verdict, a short evidence-backed pass rationale or defect, issue/action, and verification state. An optional short subsection can provide redesign blueprints for complex failed figures.

Also list substantive unnumbered visuals and significant visual tables in their own short register. Provide a global **visual system** diagnosis (systemic font, spacing, raster export, arrows, color semantics, caption style).

### Section 8 — Tables, equations, typography, and page-level production findings

Prioritized specifics; do not duplicate issues from Section 4. Include appendix/cover/TOC/bookmarks/links/fonts/printing concerns where supported.

### Section 9 — Storyline, pedagogy, and editorial value

For each part and chapter (compact is acceptable), state whether it advances the causal storyline, where reasoning is missing, whether repetition is justified, and what must be changed vs left alone. Give a short list of low-value or misplaced sections only when supported by specific explanations.

### Section 10 — Full physical-page coverage ledger

A **complete page-by-page ledger** from physical PDF page 1 to page N, including intentional blanks. At minimum:

`PDF page | printed page | unit | T/V/Q/R status | distinct issue IDs / specific note | open gap`

Use compact notation rather than hundreds of invented prose comments. This is a verification log, not a place to pad the report. If a full pass was impossible, leave exact unreviewed pages visibly unverified and adjust the executive verdict.

### Section 11 — Prior-issue regression and closure ledger

If prior reports are supplied, map original ID → current location → unchanged/modified/closed/regressed → evidence of verification. If not supplied, mark “prior issue register unavailable” and do not invent closure histories.

### Section 12 — Ordered correction plan and release gates

Sequence changes by **causal dependency**, not by easy-to-fix page order, e.g.:

1. Repair root-cause workload, memory, queueing, statistical and cost models.
2. Recalculate dependent chapter examples/tables/figures and synchronize the canonical scenario.
3. Reconcile evidence taxonomy and citations.
4. Redesign/rebuild visually or semantically defective figures.
5. Fix typography, references, PDF export and provenance records.
6. Re-render and verify affected pages, equations and figures.
7. Conduct final full-book adversarial and distribution/print preflight.

Provide exact **acceptance tests**, ownership recommendations only if useful, and a **do-not-change/freeze** list for already-good material.

### Section 13 — Final certification boundary

Write a candid summary of what was **verified**, what was **not verified**, and what must happen before it is responsible to say “ready.” Never assert completeness, print-proof quality, live-source verification or independent assessment that was not actually performed.

---

## 14. Hard release gates (all relevant gates must pass)

### Gate A — Technical and mathematical integrity

- Zero unresolved, confirmed P0/P1 defects.
- Consequential derivations independently checked or correctly labeled as unverified hypotheses (with no unsupported conclusion depending on them).
- No consequential unit/denominator/operating-point mix-up.
- Canonical work examples and dependent chapters reconcile.
- No unsound causal leap from analytic bound to practical deployment claim.

### Gate B — Evidence integrity

- Labels distinguish empirical findings, vendor data, modeling assumptions, derivations and synthetic examples.
- Crucial sources exist and actually support the published proposition, or the proposition is qualified/removed.
- Snapshot/cutoff/version chronology is internally valid.
- No unresolved editorial verification placeholder disguised as final text.

### Gate C — Visual communication

- **Every** numbered figure and significant unnumbered visual has an individual recorded verdict.
- No unresolved severe overlap, clipping, illegibility, ambiguous essential connector, incorrect plot or misleading graphic implication.
- Essential figure text is comfortable at actual print size and grayscale legibility has been considered.
- **Every** substantive figure has independently passed technical integrity, print legibility, **visual composition/elegance**, and pedagogical usefulness; an awkward but decipherable figure is not marked `KEEP`.
- For each changed figure, final-page inspection covers whole-page composition, a detailed crop, connector endpoints, and the actual/reliably approximated printed dimensions; limitations are reported.
- Problematic low-resolution raster charts have been regenerated or validated convincingly in the final PDF.
- All changed graphics checked **after** PDF build, not just in source.

### Gate D — Pedagogy and editorial quality

- Major sections contribute a defensible purpose and a coherent causal pathway.
- Necessary caveats survive transfer from the worked example to the general claim.
- Meaningful terms, symbols, chapter and figure references are consistent.
- No important explanation depends on deciphering a cramped chart or overloaded caption.

### Gate E — Production and distribution

- Book PDF is clean, correctly paginated and internally navigable.
- Fonts, figures, key links, references, trim/margins and any applicable platform-specific requirements are validated as far as available tools allow.
- Edition, source provenance, licensing/permissions and cutoff notes do not contradict the final artifact.
- Physical print proof is separately marked `PENDING` unless actually verified.

### Gate F — Coverage and review honesty

- All physical PDF pages examined at required levels, with a real ledger.
- All figures and consequential equations/tables accounted for.
- Unavailable evidence and unperformed checks explicitly disclosed.
- Prior P0/P1 corrections independently reverified if prior findings were provided.
- At least one fresh adversarial challenge completed after dependency fixes.

**If any relevant gate fails, do not declare `READY TO PUBLISH`.** A clean copyedit or a polished visual theme cannot compensate for unproven fleet sizing, invalid p99 analysis, or unreadable figures.

---

## 15. Model behavior instructions: thoroughness without hallucination or endless churn

- **Use available tools, not imagined ones.** If code execution, PDF imaging, web verification, full-text search or font inspection is unavailable, disclose precisely which checks cannot be claimed.
- **Compute rather than intuit** when a result is numerical. Show reproducible reasoning in the report for important disputed calculations.
- **Look at actual image pixels** for visual claims. Don't infer clipping or overlap just from malformed extracted text; don't infer visual quality from SVG source alone.
- **Reject fake certainty.** A reference may look correct but remain unchecked; a percentile may look plausible but have no distribution behind it.
- **Inspect adverse cases.** When a result seems neat, look for mismatched populations, missing costs, omitted fallbacks, hidden allocator reserve, change of precision, and a misleading denominator.
- **Never confuse high comment count with thoroughness.** Find root causes; suppress duplicates and subjective filler.
- **Never confuse a long output with a completed audit.** If pages or figures are unchecked, say so.
- **Protect publication quality against tool limits.** If a long job exceeds context or output capacity, leave durable exact checkpoints/ledgers and continue in the environment that supports it. Do not invent an inspected range.
- **Do not rush to a favorable verdict.** Conversely, do not endlessly raise the standard by adding optional stylistic whims after gates pass.
- **Respect the author's domain and voice.** Recommend redesign/rewrite only when the technical, pedagogical, or visual evidence justifies it.
- **Preserve high-value difficult material.** Fix ambiguity, proof, placement, and figures rather than simplifying away essential system reasoning.
- **Distinguish your own second-pass challenge from genuinely independent review.** Never claim an independent third-party check without one.
- **Make the next action obvious.** An author or agent should be able to close each mandatory issue and prove closure, without repeated clarification.

### Final directive

**Conduct a true publication audit, not a sentiment-based review.** Treat the manuscript as an engineering reference that people may build systems and make substantial decisions from. Be especially skeptical of attractive but unjustified numerical precision and of diagrams whose graphical semantics imply more than the supporting analysis establishes. Deliver **all substantiated actionable comments in one deduplicated Markdown report** with page/figure coverage and explicit release gates. Maintain the highest standard for both **technical reliability** and **pleasure of reading at print size**. Publication readiness is a conclusion to be *earned by verification*, not an encouraging phrase to be offered.
