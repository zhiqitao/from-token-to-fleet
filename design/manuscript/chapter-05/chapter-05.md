# Chapter 5 — From Workload to Model Selection

## The Architect's Question

After this chapter we should be able to reason about model selection as a **consequence of workload characterization**, not as a first question. We should also be able to walk the two-part selection that defines a RAG system: (a) choosing an embedding model for the retrieval leg, and (b) choosing a generation model for the answer leg. The chapter works toward showing that "which model is best?" is the wrong first question; the right first question is "what job does this system do, and how quantitatively?"

## 1. Concept

Model selection surfaces across five selection surfaces that are each derived from the workload characterization (Ch 4, Table 4-3):

1. **Capability / quality needed** — does the workload require multi-step reasoning, tool use, or modality handling? A workload that needs chain-of-thought reasoning needs a different model class than one that only needs fact retrieval.
2. **Latency / compute budget** — can the system meet TTFT and TPOT SLOs with the candidate model on the target hardware? This surface determines whether we need a dense 70B, a distilled 13B, or a MoE variant.
3. **Context / KV cost** — how much memory does the input context consume in the KV cache, and what does that mean for feasible context length on the target infrastructure? An 8K-context workload has a very different cost profile from a 32K-context one.
4. **Cost per token** — what is the $/million-tokens for the full request (prefill + decode) on the target infrastructure? This surface makes the economic difference between model sizes concrete.
5. **Retrieve-then-generate vs end-to-end** — does the system architecture split the job into a retrieval leg (embedding model + vector search) followed by a generation leg (base model + prompt), or does it use a single model that jointly retrieves and generates? This architectural decision drives the embedding‑vs‑generation model contrast.

The core reframe — modeled in Chapter 4 — is that **model selection is a consequence of workload characterization**. When the workload is specified in token counts, request rates, latency budgets, and economic constraints, the feasible model space narrows naturally. The architect does not start with a model and reason forward; they start with the workload and reason backward into model space.

## 2. Mental Model

Think of model selection as **system design, not model picking**. The workload is the architect's input; the model is a component that must satisfy the workload's constraints. If the workload is input-heavy (9.2K average input, 300-token output, ~30× more input than output), the system is memory‑bound and prefill‑dominated. If the workload were output‑heavy, it would be decode‑bound. The mental model holds both profiles in view: the same "which model?" question produces opposite answers depending on the token profile.

A useful image for the full pipeline:

> **Workload → Selection surfaces → Model category → Specific model**

The arrow from workload to selection surfaces is the one the architect must keep in focus. Every other arrow follows from it.

## 3. Worked Example — Embedding‑Model vs Generation‑Model Selection for the Canonical RAG Workload

The canonical scenario (the enterprise Q&A over internal documents, RAG — see Ch 4 Table 4-3) is: ~2,000 registered users, ~10 requests/s average, ~40 rps peak; average prompt of 1,200 tokens + 8K retrieved context (~9.2K input), 300-token output; 70B-class dense model, FP16 (~140 GB), 1 host with 8×H100-class GPUs (80 GB each). TTFT budget 1.2 s (retrieval ~120 ms + prefill), TPOT budget ~25 ms/token. SLO: p95 TTFT ≤ 2 s, p95 TPOT ≤ 35 ms.

We walk the two‑model selection for this workload.

### (a) Embedding‑model selection for the retrieval leg
KV cache per-token figures are at FP16 (~2.62 MB/token) unless an 8-bit (~1.3 MB/token) variant is explicitly stated.

The retrieval leg maps chunks of internal documents to dense vectors so that a user query can be matched to the most relevant context. The architect must choose an embedding model — specifically, its embedding dimension and parameter count — against the retrieval quality the workload demands.

Three realistic options, each with documented properties:

| Embedding model | Dim | Params ~ | FLOPs per embedding | Typical use case |
|---|---|---|---|---|
| all‑MiniLM‑L6‑v2 | 384 | ~85M | ~0.3 GFLOPs | Light‑weight, high‑throughput search |
| all‑mpnet‑base‑v2 | 768 | ~110M | ~1 GFLOPs | General‑purpose, quality‑first |
| bge‑large‑en | 1024 | ~335M | ~2 GFLOPs | Dense-retrieval-optimal, technical docs |

[HYPOTHESIS]: *within a given embedding family or a controlled dimensionality experiment*, reducing the embedding dimension may trade retrieval quality for lower storage and compute — e.g. a 384‑dim variant of the same model family can cost roughly half the FLOPs and index storage of a 768‑dim one. **Dimension alone is not a cross‑model quality metric**: a 1024‑dim embedding model is not intrinsically better than a 768‑dim one merely because its vector has more dimensions; retrieval quality depends on model architecture, training objective/data, corpus/query distribution, normalization, and retrieval strategy. Any observed quality‑vs‑dimension relationship (reports range from a few to ~15% MAP difference) is domain‑ and corpus‑specific and must be validated on the target corpus.

[2°] DERIVED: for a 1 M‑chunk corpus, the index storage for a $D$‑dim float32 vector corpus is $\text{bytes} = n_\text{chunks} \times D \times 4$. For 768‑dim: $1{\times}10^6 \times 768 \times 4 = 3.07$ GB; for 384‑dim: $1{\times}10^6 \times 384 \times 4 = 1.54$ GB; a difference of ~1.5 GB. At 10× the corpus (10 M chunks), that difference grows to ~15 GB. Small relative to a 140 GB base model, but not negligible at large corpus scale: storage is a persistent footprint that scales with corpus size, not a one‑time cost that vanishes.

[HYPOTHESIS]: for the canonical 2,000‑user workload with ~10 rps average, the incremental per‑request compute cost of 768‑dim vs 384‑dim embeddings is ~0.8 ms on a single CPU core, well within the ~120 ms retrieval budget. The decision hinges on whether the ~15% retrieval quality gain translates into sufficient answer‑quality improvement to justify the 2×FLOP cost — a workload‑specific tradeoff, not a universal rule.

**Takeaway for the canonical RAG workload:** 768‑dim (all‑mpnet‑base‑v2) is the recommended embedding model. It places the workload in the quality‑positive regime without introducing per‑request latency that threatens the TTFT SLO. The 384‑dim option is viable only if storage or compute budget is extremely constrained; the bge‑large‑en option is overkill for this scale and its marginal quality gain does not offset the 4×FLOP cost over all‑mpnet‑base‑v2.

**Table 5-1** — Model-selection decision: embedding vs generation model
| metric | value | derivation |
|---|---|---|
| Embedding dimension (recommended) | 768 | all‑mpnet‑base‑v2 [ILLUSTRATIVE][DERIVED] |
| Embedding model size | ~110M parameters | all‑mpnet‑base‑v2 [ILLUSTRATIVE][DERIVED] |
| Per-request context/KV cost at 9.2K input | ~24.1 GB (FP16 KV cache, initial) | 70B FP16, 80 layers, 9.2K context [1P DERIVED] |
| Tokens/s per dollar (generation, runtime) | 9,000 tokens per dollar‑hour | 50 tok/s × 3600 s/hr ÷ $20/hr [ILLUSTRATIVE][DERIVED] |
| Verdict | Embedding: all‑mpnet‑base‑v2 (768‑dim); Generation: 70B FP16 on 8×H100 | Selection surfaces (§4 §5)
### (b) Generation‑model selection for the answer leg

The generation leg produces the 300-token answer given the 9.2K retrieved context. The architect must decide whether a base 70B‑class dense model, a smaller dense model, or a fine‑tuned variant best satisfies the latency, quality, and economic constraints.

#### Real‑derived arithmetic for the 70B candidate

[1P] FACT: a 70B‑parameter model at FP16 occupies 70B × 2 bytes = ~140 GB (model-card specification, vendor‑published). [1P] FACT: 8×H100 GPUs provide 8 ×80 GB = 640 GB aggregate HBM memory.

[DERIVED] KV cache cost per token at FP16: for a Llama‑style 70B model, n_layers = 80, d_model = 8192, bytes per element = 2 (FP16). KV cache per token = n_layers × 2 × d_model × bytes = 80 ×2 × 8192 ×2 = 2,621,440 bytes ≈ 2.62 MB/token (FP16; = 2.5 MiB) (key + value across all layers). For the canonical 9.2K input: 9,200 ×2.62 MB ≈ 24.1 GB of KV cache (initial residency).

[DERIVED] per‑request memory budget: 640 GB total HBM − 140 GB weights = 500 GB headroom. The 24.1 GB KV cache for 9.2K input consumes 4.7% of headroom, leaving ~476.6 GB for activations, intermediate buffers, and OS overhead. This is comfortably within a single 8×H100 node's capacity.

[2°] DERIVED: vLLM continuous batching on 8×H100 with a 70B FP16 model and 9.2K context yields ~50 tokens/s aggregate throughput for 300‑token outputs. The prefill phase (9.2K tokens) dominates TTFT: at ~1.08 s it leaves ~0.12 s under the 1.2 s TTFT budget (retrieval ~120 ms + prefill ~1.08 s = ~1.20 s, at the SLO), with the p95 ≤ 2 s target giving the real margin.

[2°] DERIVED: tokens/s per dollar for generation. On‑demand H100 list price ~$2.50/hour per GPU → 8×H100 = $20/hour. At ~50 tok/s aggregate throughput, the effective cost is ~0.40 $/tok/s, or equivalently ~2.5 tokens/s per dollar-hour. In tokens‑per‑dollar terms: 50 tok/s × 3600 s/hr ÷ $20/hr = 9,000 tokens per dollar per hour of runtime.

> **Economics unit note (reconciliation with Ch. 4).** Both chapters use the same on-demand price basis: ~$2.50/hr per H100 → ~$20/hr per 8×H100 host. They differ only in *unit convention*: this chapter expresses **tokens per dollar-hour** (token-rate × 3600 s ÷ hourly cost), while Chapter 4 expresses **tokens per second per dollar** (token-rate ÷ per-second cost). A reader comparing across Part II should convert units (÷3600 to go tokens/dollar-hour → tokens/s/dollar). [ILLUSTRATIVE][DERIVED]

[2°] DERIVED: tokens/s per dollar with prefill included. The same 9,000 tokens per dollar-hour figure is a combined prefill+decode metric. Because this workload is input‑heavy (9.2K vs 300 tokens), the prefill leg consumes ~70% of the total tokens per request but only ~40% of the total compute time (prefill is compute‑intensive but batchable; decode is sequentially limited). The per‑dollar economics therefore favor models that reduce prefill cost (smaller context, lower KV cache per token) more than models that optimize decode throughput.

### (c) Base‑model + RAG + guardrails vs fine‑tuned model

The architect must choose between two paradigms:

**Paradigm 1 — Base model + RAG + guardrails:**
- The base 70B model receives the retrieved 9.2K context via prompt injection.
- Guardrails (PII redaction, style enforcement, refusal filtering) are applied as post‑generation or prefix‑check layers.
- No model weights are trained on domain data; the knowledge source is the vector database.

**Paradigm 2 — Fine‑tuned model on domain‑specific Q‑A pairs:**
- The base model is fine‑tuned (full or LoRA) on thousands of question‑answer pairs reflecting the enterprise's terminology and reasoning patterns.
- Inference uses the fine‑tuned weights without a retrieval step (or with a much shorter context, since the model has "memorized" much of the corpus).
- Additional costs: training compute, storage of fine‑tuned weights, and reduced flexibility for new topics.

[2°] DERIVED (illustrative — not a reference measurement): for the canonical workload, a well‑designed RAG + guardrails pipeline *approximately* matches a fine‑tuned model's answer quality on in‑domain queries. The economic comparison should be framed **parametrically**, not with a single number, because the break‑even depends on the quality uplift (domain‑specific) and the query volume (workload‑specific). The decision variable is the break‑even query volume $Q^*$ where the annualized cost of fine‑tuning, divided by its quality advantage, crosses the RAG baseline:

$$
Q^*\; \propto\; \frac{C_\text{train} + C_\text{weights-extra}}{\Delta Q \cdot \text{value per corrected query}}
$$

where $C_\text{train}$ is the one‑time training compute, $C_\text{weights-extra}$ is the incremental storage/carry cost, and $\Delta Q$ is the (domain‑specific, must‑be‑measured) quality uplift in corrected answers per query. Below $Q^*$, RAG + guardrails is economically dominant because the fine‑tuning cost is spread over too few queries to be repaid; above it, fine‑tuning may recover its upfront cost through quality gain. [Scenario structure, not a single claimed break‑even volume; the exact $C_\text{train}$, $C_\text{weights-extra}$, and $\Delta Q$ are workload‑ and domain‑specific and should be measured, not assumed.]

[HYPOTHESIS] Fine‑tuning does **not** make the model smaller — pruning is a separate operation. A full fine‑tune keeps the ~140 GB 70B weight set (and adds a checkpoint), while a LoRA adapter is tiny but does not change the live weight footprint. Consequently the latency effect of fine‑tuning is not "smaller effective model" and cannot be assumed to cut TTFT; any TTFT change must be measured. The real cost changes are: (a) one‑time training compute, and (b) incremental storage, both against the RAG pipeline's prefill cost (~1.08 s, which dominates any plausible TTFT delta). Parametrically, fine‑tuning becomes worth it only when its annualized cost over $Q$ queries is repaid by $\Delta Q \cdot \text{value}$ — this is exactly the $Q^*$ above. The illustrative cloud‑GPU training cost is presented as a scenario range, not a fact, and must be benchmark‑validated against a target workload.

**Takeaway:** For the canonical enterprise Q&A RAG workload, the base‑model + RAG + guardrails paradigm is the economically preferred choice. Fine‑tuning becomes compelling only when the query distribution is highly concentrated, the domain vocabulary is extremely specialized, and the workload volume sustains the training amortization threshold.

## 4. Measurement

How does an architect measure the workload dimensions that drive model selection? Three concrete checks:

1. **Actual token count, not the rule of thumb.** Run the model's own tokenizer on representative prompts from the target domain. The "4 chars ≈ 1 token" heuristic is for estimation only; real counts differ by language, formatting, code, and tokenizer version. For the canonical workload, measure the exact prompt+context token count on real employee queries before fixing the model.

2. **Input vs output split.** Measure both legs of the request (prompt tokens and generated tokens), because they land on different bottlenecks — input on memory/prefill, output on decode — and on different cost line items. The canonical ratio of ~30× more input than output is the single biggest driver of this system's cost structure.

3. **Peak vs average context.** Log the distribution of context lengths, not just the mean. A workload that averages 9.2K input tokens but peaks at 32K (a variant flagged in Ch. 4) has a very different KV cache and latency profile. The architect must know the 95th‑percentile context length to size the KV budget correctly.

This measurement habit is the token-layer answer to the book's recurring question, "what would I actually measure here?" — we measure token counts and their distribution, at the edge, before any architecture decision is made.

## 5. Common Mistakes

- **Starting with "which model is best?"** Instead of characterizing the workload first. The workload's token profile, latency budget, and economic constraints are what narrow the model space; starting with a model short‑circuits the reasoning chain and leads to post hoc justification.

- **Ignoring the KV cache cost of long contexts.** A 9.2K input on a 70B model costs ~24.1 GB of KV cache (initial). An architect who does not account for this will either over‑provision infrastructure or hit SLO violations when the cache spills to host memory or SSD.

- **Quoting context window as free capacity.** The 128K or 1M token window is an upper bound, not a recommendation. Using even 9.2K of a 128K window still costs for the length actually used. The cost is proportional to the *used* length, not the *available* length.

- **Assuming embedding dimension is a free parameter.** Increasing embedding dimensionality *within a given model family or controlled configuration* can improve retrieval fidelity, but dimensionality alone does not predict quality across different embedding models. Higher dimension also raises FLOP cost, index storage, and per‑query latency, so the architect must balance these against the workload's quality requirements rather than treat dimension as a cost‑free or universally-better knob (see the caveat in §3).

- **Over‑engineering the fine‑tuning path.** Fine‑tuning adds training compute and model/checkpoint‑management cost; depending on the adaptation and serving method, it may also add inference or operational overhead (e.g. a LoRA adapter applied dynamically at serve time can introduce overhead, whereas a merged/fully‑fine‑tuned model of identical architecture need not change the inference shape). The break‑even analysis (the parametric $Q^*$ in §3) shows that for most enterprise RAG workloads, the RAG + guardrails paradigm dominates on TCO. Fine‑tuning should be a deliberate choice triggered by a sustained query volume, not a default.

## 6. Architecture Consequence

Whatever we learned here, file it under **"can I size the workload before I pick a model?"** Concretely, the decision this chapter enables is:

- Estimate tokens‑per‑request (input and output separately), and therefore tokens‑per‑second capacity and cost, before choosing a model or a serving configuration.
- Use the selection surfaces (quality, latency, KV cost, cost/token, retrieve‑vs‑generate) to narrow the model space from the full vendor catalog to a handful of viable candidates.
- For RAG workloads, select the embedding model and generation model as a two‑part decision, not a single choice. The embedding model is chosen at ingestion time (compute‑light, storage‑bound); the generation model is chosen at serving time (compute‑bound, latency‑bound).

This consequence feeds directly into Pattern 12 (Fine‑tuning for specific workloads) and Pattern 11 (RAG): the architect first characterizes the workload, then lets the characterization speak the model selection, not the other way around.

## 7. What We Still Don't Know

[HYPOTHESIS]: the interaction between embedding dimension and retrieval quality across diverse enterprise domains is not yet characterized with reproducible benchmarks. Early evidence suggests 768 dim is a sweet spot, but the quality drop‑off from 768 to 1024 dim varies by corpus genre (legal vs. engineering vs. creative), and no public study quantifies this domain‑dependence.

[HYPOTHESIS] the break‑even point between RAG + guardrails and fine‑tuned models as a function of query volume and domain specialization is **model‑ and domain‑dependent**: it is set by the $Q^*$ equation above (training + storage cost over the quality uplift), not by a universal rule of thumb. Any quoted break‑even volume is a derived scenario value; more data points and a measured $\Delta Q$ are needed before it can be stated as a general principle.

[HYPOTHESIS]: guardrail latency (PII redaction, refusal checking) on generated 300‑token outputs, ~2–8 ms/request on CPU in the illustrative scenario; measure on the target stack (the figure depends on the guardrail implementation and hardware).

Each of these flags is an open empirical question a team should resolve against its own target workload — promoted to [1P] or [2°] DERIVED, dropped, or demoted into the "What We Still Don't Know" section — rather than left as an untested assumption.

## 8. End-of-Chapter Mini-Case

*(Continuous scenario: the enterprise Q&A architect must now pick the model given the Ch. 4 characterization.)*

An architect is assembled for a design review of the enterprise Q&A tool described in Chapter 4. The requirement has been characterized: ~2,000 registered users, ~10 rps average, ~9.2K input tokens + 300 output tokens, input‑heavy profile, TTFT SLO p95 ≤ 2 s, TPOT SLO p95 ≤ 35 ms. The team has also agreed on the retrieval architecture: vector search with embeddings, 768‑dim all‑mpnet‑base‑v2, late‑max retrieval over a 1 M‑chunk corpus.

From the token‑layer perspective (as we worked through in Chapter 5), the architect can immediately check the consequences:

- **768‑dim embeddings** give adequate retrieval quality at ~1 GFLOPs per embedding, with ~3.1 GB index storage for a 1 M‑chunk corpus (vs ~1.5 GB at 384‑dim) — a persistent footprint that scales with corpus size, alongside the 70B base model.
- **9.2K input** at ~2.62 MB/KV‑token costs ~24.1 GB of cache (initial) on the 70B generation model, well within the 8×H100 node's 640 GB HBM. The prefill TTFT of ~1.08 s plus retrieval (~120 ms) sits at the 1.2 s TTFT budget, with the p95 ≤ 2 s SLO giving the real margin.
- The **30× input‑vs‑output ratio** means this system is prefill‑dominated; model selection must weigh KV cache cost and prefill throughput more heavily than decode throughput.
- The **base‑model + RAG + guardrails** paradigm produces the lower **modeled** TCO under the illustrative cost and quality assumptions used in this worked example (see the parametric $Q^*$ break‑even above). This is not a general 10× cost relationship — the actual ratio depends on the domain‑specific quality uplift and the query volume, and must be measured rather than assumed.

The architect now has a concrete model shortlist: 768‑dim all‑mpnet‑base‑v2 for the retrieval leg, and the 70B FP16 base model for the generation leg, served on 8×H100 with vLLM continuous batching. No fine‑tuning is needed at this scale. The architecture decision record (to be written in Chapter 25) will reference this characterization and the selection surfaces that drove it.

---

![Fig 5.1 — Model selection for RAG: workload → five selection surfaces → two legs (retrieval/embedding, generation/70B) → the system decision [ILLUSTRATIVE conceptual]](figures/fig-05-0501.png)


---

**End of Chapter 5**
