# From Token to Fleet — Book Architecture

*This is the authoritative architecture for the book. It fixes the central mental models, the spine (the requirement→architecture decision loop), the recurring chapter template, the evidence taxonomy (with its [1P]/[2°] provenance rules), the canonical worked examples, and the progression of architectural decisions. Individual chapters grow incrementally against this frame.*

---

## 1. Title & positioning

**From Token to Fleet: An AI Solution Architect's Handbook**

The author wanted to build the systematic knowledge of what it means to work
as an AI Solution Architect: how to reason across the layers of an AI system
--- from tokens and models to workloads, systems, infrastructure, and fleets
--- so that a vague requirement can be turned into a defensible architecture.
The best way for the author to build that knowledge was to go through the
journey of writing it, documenting the body of knowledge as it is learned,
chapter by chapter, and keeping the notes updated as the field moves.
Writing turns implicit understanding into explicit models, and the act of
writing exposes the holes in the author's own understanding that point to
what to learn next --- a feedback loop (Curiosity \rightarrow question
\rightarrow research \rightarrow model \rightarrow write \rightarrow discover
a gap \rightarrow new question) that drives the whole project. The book is a
documentation of that learning journey, shared.

---

## 2. The spine (the reason the book exists)

The book has one thesis, and it is the spine of every chapter:

> **Given an ambiguous problem, how do I systematically arrive at a defensible AI architecture?**

The canonical loop (Ch. 22 makes it explicit, and every chapter echoes it):

```
Requirements
    ↓
Workload characterization
    ↓
Constraints
    ↓
Candidate architectures
    ↓
Benchmark
    ↓
Bottleneck analysis
    ↓
Optimization
    ↓
TCO
    ↓
Recommendation
    ↓
Red team → challenge → final architecture
```

Parts I–V teach the technical substrate. **Part VI teaches the discipline.** The six parts are organized so the reader is always asking the architect's method, not merely memorizing layer facts.

---

## 3. Constraint Hierarchy (a reusable mental model)

Established in Part III and referenced everywhere:

```
Can it fit?          → Memory capacity
Can it compute?      → Compute capacity
Can it communicate?  → Interconnect
Can it serve?        → Scheduling / batching
Can it scale?        → Fleet economics
```

A good architect does not merely know that NVLink is fast or that FP4 saves memory — they know **which constraint matters for the workload**. This is the durable skill.

---

## 4. The recurring chapter template

Every chapter follows this shape (mandatory):

1. **The Architect's Question** — what should I learn to reason about after this chapter?
2. **Concept** — the mechanism.
3. **Mental Model** — how to think about it.
4. **Worked Example** — numbers, clearly labeled as a worked example (not reference).
5. **Measurement** — how to measure it.
6. **Common Mistakes** — where architects go wrong.
7. **Architecture Consequence** — which architectural decision this enables.
8. **What We Still Don't Know** — intellectual honesty.
9. **End-of-chapter mini-case** — a short scenario exercising the Architect's Question (adopted in §12; the continuous-scenario idea and reading paths are in §14).

---

## 5. Evidence taxonomy (binding)

Every quantitative claim carries **two orthogonal labels**:

**Source (provenance of the source document):** `[1P]` first-party to the subject (the model vendor's own spec / model card) / `[2°]` reputable second-hand (textbook, survey, third-party benchmark report) / `[VERIFY]` not yet anchored. The source axis labels *where the number came from*, not whether it was computed.

**Claim type (optional enrichment):** `FACT` directly stated by the cited source · `DERIVED` calculated from documented facts · `HYPOTHESIS` reasoned conclusion requiring validation. The claim-type axis alone carries "is this computed."

> **`EXPERIMENT` is not used as reference.** Author home-lab measurements are not reference per the evidence rule; when a worked example uses real numbers they are explicitly labeled "worked example, not reference." This preserves independent-verification integrity.

**Anchored examples** (written into the chapters, not here):

- "The X-Y model card specifies a 70B parameter count. [1P] FACT" — directly stated on a first-party primary source, no arithmetic.
- "A 70B model needs ~140 GB at FP16 (2 bytes × 70B). [1P] DERIVED" — the inputs are first-party (model card: 70B params, FP16); the arithmetic itself is carried by DERIVED.
- "Across surveyed providers, serving 70B-class models typically uses vLLM-class continuous batching. [2°] DERIVED" — second-hand source, computed comparison.
- "Under optimal batching, throughput scales roughly linearly with batch size until memory saturates. [VERIFY] HYPOTHESIS" — reasoned, to be validated against benchmarks before publication.

**`[VERIFY]` is a status, not a provenance** — a placeholder to be replaced during editing. A `[VERIFY] HYPOTHESIS` claim has three exits before publication: promote (anchor to `[1P]` / `[2°]` evidence and relabel), drop (the claim is dropped), or demote (move it into the chapter's "What We Still Don't Know" as a flagged open question). The default is promote; a claim left `[VERIFY]` at publication marks incomplete editing.

---

## 6. The anti-catalog rule (binding)

For every section, ask: **what architectural decision does this knowledge enable?**

If the answer is only "the reader should know what this technology is," minimize it. If it is "this changes which architecture you should choose under these workload constraints," it belongs. This keeps the book durable for years.

---

## 7. Workload-characterization framework (Part II)

A workload is defined by:

- **Quality** — accuracy, reasoning capability, tool use, modality
- **Traffic** — requests/sec, concurrency, burstiness
- **Token profile** — input length, output length, context length, generation pattern
- **Latency** — TTFT, TPOT, end-to-end
- **Economic constraints** — $/request, $/million tokens, infrastructure utilization
- **Operational constraints** — availability, privacy, locality, update frequency

Model selection becomes a **consequence of workload characterization**. "Which model is best?" is usually the wrong first question.

---

## 8. Architecture Patterns library (Part VI, Ch. 26)

Patterns — each with when-to-use, constraints, architecture, bottlenecks, benchmark, failure modes, economics (12 patterns):

1. Single-node inference
2. Multi-GPU model parallelism
3. Distributed MoE inference
4. Prefill/decode disaggregation
5. Model router
6. Heterogeneous model fleet
7. Agent fleet
8. Local/private AI
9. Hybrid cloud AI
10. AI factory
11. RAG (Retrieval-Augmented Generation) — retrieval, embedding-model selection, vector-database latency, context-window management, hybrid search, reranking, caching; TTFT impact, memory pressure from long contexts
12. Fine-tuning for specific workloads — when to fine-tune vs. RAG vs. prompting; memory footprint contrast (weights + gradients + optimizer states vs. weights + KV); LoRA vs. full fine-tuning; update frequency; quality improvement vs. TCO; decay management

---

## 9. Revised chapter skeleton

> Changes vs v1: KV-cache deep-dive moved out of Part I into Part III (Memory) as the core case study; Part I is three chapters so the Token part does not borrow a Workload chapter; Ch. 19 Agentic Systems reframed as *agent-as-a-workload*; TCO reframed as the bridge between engineering and business; the Constraint Hierarchy added to Part III.

### Part I — The Token
The chapter opens the token→model thread that the book title promises.

- **Ch 1 · What Is a Token?** — Tokenization, context, embeddings, attention, KV cache as a concept.
- **Ch 2 · What Actually Happens During Inference** — Prefill vs decode, bandwidth, compute, latency; why decode is bandwidth-bound.
- **Ch 3 · Understanding the Model** — Dense vs MoE, total vs active, reasoning models (chain-of-thought, test-time scaling), hybrid attention. Includes how training shapes what you deploy (pretraining objective, RL, distillation → reasoning behavior; hybrid attention and MoE routing arise from the training regime) so the architect can reason about a model without training one.

### Part II — The Workload
The job the system does. RAG is the recurring worked example threaded through this part.

- **Ch 4 · The Anatomy of an AI Workload** — the workload-characterization framework (Section 7); worked example: characterize a RAG workload (e.g., enterprise Q&A) across the six dimensions.
- **Ch 5 · From Workload to Model Selection** — why "which model is best?" is the wrong first question; worked example: embedding model vs. generation model selection. Includes the base-model + RAG + guardrails vs. fine-tuned-model decision (feeds Pattern 12).
- **Ch 6 · Measuring What Matters** — TTFT, TPOT, throughput, concurrency, quality, cost; worked example: RAG latency budget (retrieval + generation TTFT).

### Part III — The System
The constraint hierarchy (Section 3) is introduced here. Ch. 7 introduces the hierarchy as Part III's organizing frame and teaches level 1 (memory); levels 2–4 are taught in their respective chapters (compute, communication, serving). Level 5, fleet economics, is introduced here as a concept but cashed out in Parts IV–V (Ch. 16 TCO, Ch. 20 Fleet-Level Optimization).

- **Ch 7 · Memory Is the First Constraint** — weights, KV cache (the central case study), activations, quantization, residency floor. *KV-cache deep-dive lives here.* Includes the architect-relevant contrast: inference residency (weights + KV) vs. fine-tuning residency (weights + gradients + optimizer states).
- **Ch 8 · Compute** — FLOPs, utilization, arithmetic intensity.
- **Ch 9 · Communication** — PCIe, NVLink, Ethernet, InfiniBand, collectives.
- **Ch 10 · Parallelism** — TP, PP, DP, EP, CP and when each matters.
- **Ch 11 · Serving** — batching, PagedAttention/vLLM, prefix caching, P/D disaggregation, spec decode, KV offload.

### Part IV — The Architecture
Designing and validating a system; benchmarking precedes architecture selection.

- **Ch 12 · Designing the AI System** — producing candidate architectures from the substrate (memory/compute/communication/parallelism); distinct from Ch. 22, which teaches the meta-method (the spine loop itself applied to an ambiguous requirement).
- **Ch 13 · Reference Architectures** — local → server → cluster → hyperscale.
- **Ch 14 · Benchmarking** — predict real experience, not a leaderboard. Serves both architecture selection (per the spine loop) and ongoing production validation.
- **Ch 15 · Performance Engineering** — find the bottleneck, not the easiest metric.
- **Ch 16 · TCO** — *Performance tells you what a system can do; TCO tells you whether to build it.* The bridge to business.

### Part V — The Fleet
From one good system to operating thousands.

- **Ch 17 · From Server to Fleet** — heterogeneous accelerators, placement, scheduling.
- **Ch 18 · Operating Multiple Models** — *fleet-level* operations across nodes/servers: routing, selection, fallbacks. (Distinct from Pattern 5, the request-level routing algorithm.)
- **Ch 19 · Agentic Systems** — *agent as a workload*, not a technology: variable model calls, tool latency, context growth, retries, parallel subagents, routing, state, long-running sessions, failure recovery. (Distinct from Pattern 7, the fleet-level agent orchestration recipe.)
- **Ch 20 · Fleet-Level Optimization** — capacity, utilization, reliability, cost.
- **Ch 21 · The AI Factory** — the data center as an AI production system. Includes the model update/retrain loop (new model versions flow into the fleet; see Pattern 12).

### Part VI — The Architect
The discipline; the spine made explicit.

- **Ch 22 · How to Think Like an AI Solution Architect** — the spine loop (Section 2) made explicit.
- **Ch 23 · Working With Customers** — vague requirement → measurable workload.
- **Ch 24 · Red Team / Green Team** — challenge the recommendation.
- **Ch 25 · The Architecture Decision Record** — why you chose what you chose.
- **Ch 26 · The Solution Architect's Toolkit + Patterns Library** — Section 8.

---

## 10. Why this stays a living document

The frame above is fixed so chapters can grow incrementally without the book collapsing into a collection of interesting AI essays. Writing is the mechanism by which the author learns; the book is the structured externalization of that evolving knowledge — but evidence integrity and the anti-catalog rule keep it from becoming either a vanity notebook or a vendor index.

---


**Binding drafting conventions:**

- **Visual language** — a shared look across chapters: the spine loop as a labeled flow (Requirements → Workload → Constraints → Candidates → Benchmark → Bottleneck → Optimize → TCO → Recommend → Red team, with return edges drawn: red-team failure → candidates / benchmark / workload re-characterization); the Constraint Hierarchy as a vertical stack (Memory → Compute → Communication → Scheduling → Economics); shared color-coding (memory = red, compute = blue, communication = green, economic/latency = amber); one pattern-diagram template (when-to-use / constraints / architecture / bottlenecks / benchmark / failure modes / economics).
- **Chapter-length target** — 15–25 pages each; the constraint is usefulness to the architect, not page count. Heavier chapters (Ch. 7 Memory, Ch. 11 Serving, Ch. 26 Patterns) may run longer; lighter ones (Ch. 1) shorter.
- **Named tools as dated instances** — tools (vLLM, PagedAttention, NVLink) appear as "dated instances of a mechanism" (e.g. continuous batching, e.g. vLLM as of 2026), never as the mechanism itself, keeping the book durable as vendors churn.

---

## 14. Canonical scenario + reading paths

**The canonical scenario (one set of numbers, cited by every chapter).** Written once here so Ch. 4–6, Pattern 11, the Ch. 6 latency budget, and Ch. 7 memory arithmetic all draw on the same source of truth — cross-chapter numeric drift starts the moment drafting begins, so the numbers are fixed now:

> **Canonical workload: enterprise Q&A over internal documents (RAG).** ~2,000 registered users (~5% concurrently active, each issuing a request roughly every ~200 s, yielding ~10 requests/s average; peaks ~40 rps), average prompt 1,200 tokens + 8K retrieved context (~9.2K input), 300-token output. 70B-class dense model, FP16 (weights ≈ 140 GB), 1 host with 8 × H100-class GPUs (80 GB each). TTFT budget 1.2 s (retrieval ~120 ms + prefill), TPOT budget ~25 ms/token. SLO: p95 TTFT ≤ 2 s, p95 TPOT ≤ 35 ms. Operated multi-region for availability; economics framed as tokens/s per dollar. *(All `[1P]`/`[2°]` anchors checked against sources at drafting; figures here are the canonical input set, not measurement claims.)*

**On the canonical being a dense full-MHA model.** The canonical deliberately uses a 70B dense model with full multi-head attention, even though 2026 frontier deployments are dominated by MoE + hybrid-attention models (Ch. 3's bridge section and Ch. 27). This is a **teaching choice, not a market snapshot**: full-MHA yields the cleanest single-constant KV formula and the largest (conservative worst-case) memory footprint, so the architect learns the framework on the hardest memory case and relaxes it. The framework is architecture-agnostic — substitutable constants (KV scheme, active vs total params, roofline points) are what change, and Ch. 3 §"2026 baseline shift" plus Ch. 27 walk the transfer explicitly. Chapters may vary parameters **only** to illustrate a mechanism (clearly flagged "variant"); the default is to reuse these numbers so the reader builds one continuous mental model.

**Reading paths.** Two documented entry points, so the book works cover-to-cover or selectively:

- **Cover-to-cover (Parts I→VI)** — the full climb from token to architect; each chapter assumes the previous ones' mental models. Best for someone becoming an architect.
- **From a decision (spine-first)** — a practitioner facing a concrete architecture question reads the spine (Ch. 22) first, then pulls the substrate chapters they need (Part III/IV, or the pattern library in Ch. 26). Signposted at each Part boundary.

Both paths converge on the same mental model; the difference is ordering, not content.

**Continuous mini-case scenario.** The 26 end-of-chapter mini-cases trace a single growing requirement (vague enterprise Q&A → characterized workload → system → fleet), so Ch. 23's "vague requirement → measurable workload" becomes the payoff of a continuous thread rather than a fresh example.

**Machine-readable canonical source.** The scenario above is the human-readable statement of a single authoritative dataset, frozen in `design/canonical-workload.yaml`, with every derived number computed by `render/canonical_calc.py`. Any chapter that needs a quantitative claim derives it from that set (weights 140 GB; KV/token FP16 ≈ 2.5 MB or exactly 2 × layers × hidden × bytes; M_kv ≈ 436 GB after weights and runtime on the 8×H100 host; per-request KV ≈ 23.8 GB at 9,500 tokens; KV-residency concurrency C ≈ 18 baseline / 16 at T=2 / 14 at T=4; FP8 KV ≈ 1.3 MB/token roughly doubling C). If a chapter's number disagrees with the canonical calculator, the reconciliation rule is: fix the chapter, never the canonical set — unless the canonical set itself is proven wrong against a primary source.

**Architecture-variable notation (one symbol system).** To keep derivations comparable across chapters, the book uses a single notation layer: λ (request arrival rate), I and O (input/output tokens per request), C (concurrency), L (request latency); for the model, P (parameters), A (active params), L_model (layers), H (hidden dim), H_KV and D_head (KV heads and head dimension), b_w / b_kv (bytes per weight / KV element); for hardware, M (usable HBM), B_BW (sustained HBM bandwidth), F_peak / F_sustained (peak/sustained FLOPs); for serving, B (batch), K (KV capacity), R (prefix-cache hit rate); economics, capex/opex/U (utilization). Every chapter's equations use these symbols so cross-chapter arithmetic is directly comparable.

**Evidence taxonomy — five categories.** The book labels every quantitative claim with both provenance ([1P] first-party, [2°] secondary) and epistemic status: **FACT** (directly stated by the cited source), **MEASURED** (a real benchmark the author or a cited source ran), **DERIVED** (computed from known facts via shown arithmetic), **ILLUSTRATIVE** (a hypothetical teaching number chosen for its shape, not asserted as real), and **HYPOTHESIS** (an untested prediction). Every worked example states quantity, unit, formula, substitution, result, and a sanity check (e.g. "MFU cannot exceed 1.0", "weights cannot exceed usable HBM", "KV uses KV-head count, not hidden dim, for GQA/MQA models"). The five-way split is what keeps hypothetical numbers from masquerading as DERIVED.

### Closed in this review (v7 diff)

- **Feedback arrows folded into the visual-language spec** — the §13 visual-language entry for the spine loop now includes the return edges (red-team failure → candidates / benchmark / workload re-characterization), so chapters draw the loop as a loop, not a chain.
- **Ch. 19 boundary line added** — agent-as-a-workload (Ch. 19) vs Pattern 7 (agent fleet) distinguished the same way Ch. 18 vs Pattern 5 was.
- **Discipline-chapter mini-case** — for Ch. 23–25 the mini-case (element 9) may *be* the chapter's payoff (e.g., the ADR written in Ch. 25) rather than a separate exercise, per "never boilerplate."

*Version trail: v8 is the current version of the authoritative architecture. v8 applies the Qwen 3.8 Max v7 review — cross-reference consolidation (continuous-scenario → §14), taxonomy orthogonality completion (FACT = directly stated by the cited source), canonical scenario precision (hosts→GPUs, users↔rps linkage), Part III owner-chapter clarity, and reading-path wording. Version history (v1→v8) is preserved in git.*


