# Chapter 5 — From Workload to Model Selection

## The Architect's Question

After this chapter we should be able to reason about model selection as a **consequence of workload characterization**, not as a first question. We should also be able to walk the two-part selection that defines a RAG system: (a) choosing an embedding model for the retrieval leg, and (b) choosing a generation model for the answer leg. The chapter works toward showing that "which model is best?" is the wrong first question; the right first question is "what job does this system do, and how quantitatively?"

## 1. Concept

Model selection proceeds across five surfaces, each derived from the workload characterization (Ch 4, Table 4-2):

1. **Capability / quality needed** — does the workload require multi-step reasoning, tool use, or modality handling? A workload that needs chain-of-thought reasoning needs a different model class than one that only needs fact retrieval.
2. **Latency / compute budget** — can the system meet TTFT and TPOT SLOs with the candidate model on the target hardware? This surface determines whether we need a dense 70B, a distilled 13B, or a MoE variant.
3. **Context / KV cost** — how much memory does the input context consume in the KV cache, and what does that mean for feasible context length on the target infrastructure? An 8K-context workload has a very different cost profile from a 32K-context one.
4. **Cost per token** — what is the $/million-tokens for the full request (prefill + decode) on the target infrastructure? This surface makes the economic difference between model sizes concrete.
5. **Retrieve-then-generate vs end-to-end** — does the system architecture split the job into a retrieval leg (embedding model + vector search) followed by a generation leg (base model + prompt), or does it use a single model that jointly retrieves and generates? This architectural decision drives the embedding‑vs‑generation model contrast.

The core reframe — modeled in Chapter 4 — is that **model selection is a consequence of workload characterization**. When the workload is specified in token counts, request rates, latency budgets, and economic constraints, the feasible model space narrows naturally. The architect does not start with a model and reason forward; they start with the workload and reason backward into model space.

### A model candidate includes its deployment precision

A model name alone does not identify a deployable candidate. The same checkpoint can produce different quality, memory use and execution paths under different quantization recipes.[^oct-qz-awq]^,^[^oct-qz-gptq] We therefore compare a base-model revision together with its tensor precisions, calibration or recovery procedure, export schema and serving backend. The quality gate applies to that exported deployment, including its tokenizer, prompt template and modal branches. A language-only quantization result does not establish that a vision encoder, projector or tool-use workload retains the same behavior. The mechanism and byte accounting appear in Chapter 7; Chapter 14 supplies the acceptance test. [1P][DERIVED]

### Inference mode is a candidate, not a selection verdict

The same task can favor different inference modes at different concurrency levels. Parallel refinement is worth investigating when low-batch latency or constrained infilling dominates, but neither advantage follows from a model-family label. AR fill-in-the-middle models are a necessary editing baseline. Structured output adds another gate: an API that documents JSON-schema generation and a self-hosted backend that rejects grammar constraints are not interchangeable candidates.[^oct-df-struct] The selection question is whether the specific model, sampler and runtime meet the workload's quality, output and SLO requirements together. The mechanisms in Chapter 3 explain the candidate; the measurements in Chapter 14 decide whether it belongs in the architecture. [DERIVED]

## 2. Mental Model

Model selection is really **system design, not model picking**. The workload is the architect's input; the model is a component that must satisfy the workload's constraints. If the workload is input-heavy (9.2K average input, 300-token output, ~30× more input than output), the system is memory‑capacity‑bound (KV residency) and prefill‑dominated — prefill itself sits in the compute‑bound regime (Ch 2). If the workload were output‑heavy, it would be decode‑bandwidth‑bound. The mental model holds both profiles in view: the same "which model?" question produces opposite answers depending on the token profile.

A useful image for the full pipeline:

> **Workload → Selection surfaces → Model category → Specific model**

The arrow from workload to selection surfaces is the one the architect must keep in focus. Every other arrow follows from it.

## 3. Worked Example — Embedding‑Model vs Generation‑Model Selection for the Canonical RAG Workload

Per the canonical workload (Ch 4, Table 4-2): the enterprise Q&A RAG tool — input-heavy, ~9.2K input (1,200 prompt + 8K retrieved) + 300-token output; 70B-class dense FP16 model (~140 GB) on one 8×H100 host. TTFT budget 1.2 s (retrieval ~120 ms + prefill), TPOT ~25 ms/token; p95 TTFT ≤ 2 s, p95 TPOT ≤ 35 ms.

We walk the two‑model selection for this workload.

### (a) Embedding‑model selection for the retrieval leg
KV cache per-token figures are at FP16 (~2.62 MB/token) unless an 8-bit (~1.3 MB/token) variant is explicitly stated.

The retrieval leg maps chunks of internal documents to dense vectors so that a user query can be matched to the most relevant context. The architect must choose an embedding model — specifically, its embedding dimension and parameter count — against the retrieval quality the workload demands.

Three realistic options, each with documented properties:

| Embedding model | Dim | Params | FLOPs per embedding (64-token query) | Typical use case |
|---|---|---|---|---|
| all‑MiniLM‑L6‑v2 | 384 | ~23M | ~2.9 GFLOPs | Light‑weight, high‑throughput search |
| all‑mpnet‑base‑v2 | 768 | ~110M | ~14 GFLOPs | General‑purpose, quality‑first |
| bge‑large‑en | 1024 | ~335M | ~43 GFLOPs | Dense-retrieval-optimal, technical docs |

*FLOPs per embedding = 2 × params × L at a 64-token query (L = 64); the value scales linearly with query length, so the model-to-model ratio equals the parameter ratio (bge‑large ≈ 3× mpnet). [DERIVED]*

[HYPOTHESIS]: *within a given embedding family or a controlled dimensionality experiment*, reducing the embedding dimension may trade retrieval quality for lower storage and compute — e.g. a 384‑dim variant of the same model family can cost roughly half the FLOPs and index storage of a 768‑dim one. **Dimension alone is not a cross‑model quality metric**: a 1024‑dim embedding model is not intrinsically better than a 768‑dim one merely because its vector has more dimensions; retrieval quality depends on model architecture, training objective/data, corpus/query distribution, normalization, and retrieval strategy. Any observed quality‑vs‑dimension relationship (reports range from a few to ~15% MAP difference) is domain‑ and corpus‑specific and must be validated on the target corpus.

[ILLUSTRATIVE][DERIVED]: for a 1 M‑chunk corpus (a Ch 5‑local illustrative input, not part of Table 4‑2), the index storage for a $D$‑dim float32 vector corpus is $\text{bytes} = n_\text{chunks} \times D \times 4$. For 768‑dim: $1{\times}10^6 \times 768 \times 4 = 3.07$ GB; for 384‑dim: $1{\times}10^6 \times 384 \times 4 = 1.54$ GB; a difference of ~1.5 GB. At 10× the corpus (10 M chunks), that difference grows to ~15 GB. Small relative to a 140 GB base model, but not negligible at large corpus scale: storage is a persistent footprint that scales with corpus size, not a one‑time cost that vanishes.

[HYPOTHESIS]: for the canonical 2,000‑user workload with ~10 rps average, the incremental per‑request compute cost of 768‑dim vs 384‑dim embeddings is ~11.1 GFLOP per 64‑token query (2 × params × L: 14.08 − 2.94 GFLOP, Table 5‑1's own rows; a same‑family 384‑dim variant is the ~2× case) — ~56–370 ms if encoded on a single CPU core at a realistic 30–200 GFLOP/s, but only ~1.1 ms on a ~10 TFLOP/s GPU, which is the basis the ~120 ms retrieval budget already assumes (vector search and reranking on a local GPU, Ch 4). On that basis the incremental cost stays well within the ~120 ms retrieval budget; single‑core encoding is the configuration that would not fit. The decision hinges on whether the ~15% retrieval quality gain translates into sufficient answer‑quality improvement to justify the 2×FLOP cost — a workload‑specific tradeoff, not a universal rule.

**Takeaway for the canonical RAG workload:** 768‑dim (all‑mpnet‑base‑v2) is the recommended embedding model. It places the workload in the quality‑positive regime without introducing per‑request latency that threatens the TTFT SLO. The 384‑dim option is viable only if storage or compute budget is extremely constrained; the bge‑large‑en option is overkill for this scale and its marginal quality gain does not offset the ~3× FLOP cost over all‑mpnet‑base‑v2 (≈43 vs ≈14 GFLOPs per 64-token embedding in the table above, the same ratio as their parameter counts).

\needspace{250pt}
**Table 5-1** — Model-selection decision: embedding vs generation model

| metric | value | derivation |
|---|---|---|
| Embedding dimension (recommended) | 768 | all‑mpnet‑base‑v2 [1P][FACT] |
| Embedding model size | ~110M parameters | all‑mpnet‑base‑v2 [1P][FACT] |
| Per-request context/KV cost at 9.2K input | ~24.1 GB (FP16 KV cache, initial) | 70B FP16, 80 layers, 9.2K context [canonical scenario][DERIVED] |
| Tokens per dollar-hour (generation, runtime) | 9,000 tokens per dollar‑hour | 50 tok/s × 3600 s/hr ÷ $20/hr [ILLUSTRATIVE][DERIVED] |
| Verdict | Embedding: all‑mpnet‑base‑v2 (768‑dim); Generation: 70B FP16 on 8×H100 | Selection surfaces (§5.1) |

### (b) Generation‑model selection for the answer leg

The generation leg produces the 300-token answer given the 9.2K retrieved context. The architect must decide whether a base 70B‑class dense model, a smaller dense model, or a fine‑tuned variant best satisfies the latency, quality, and economic constraints.

#### Real‑derived arithmetic for the 70B candidate

[canonical scenario][DERIVED]: a 70B-class parameter model at FP16 occupies 70B × 2 bytes = ~140 GB (the 70B is the constructed canonical teaching geometry, Ch 4 Table 4-2; the 140 GB is derived from it, not a vendor-published model card). [1P][FACT]: 8×H100 GPUs provide 8 ×80 GB = 640 GB aggregate HBM memory (real hardware spec).

[canonical scenario][DERIVED] KV cache cost per token at FP16: for a Llama‑style 70B model, n_layers = 80, d_model = 8192, bytes per element = 2 (FP16). KV cache per token = n_layers × 2 × d_model × bytes = 80 ×2 × 8192 ×2 = 2,621,440 bytes ≈ 2.62 MB/token (FP16; = 2.5 MiB) (key + value across all layers). For the canonical 9.2K input: 9,200 ×2.62 MB ≈ 24.1 GB of KV cache (initial residency).

[canonical scenario][DERIVED] per‑request memory budget: 640 GB total HBM − 140 GB weights = 500 GB headroom (before the ~64 GB runtime reserve that the concurrency budget in Ch. 7 subtracts to reach the ~436 GB KV budget). The 24.1 GB KV cache for 9.2K input consumes ~4.8% of headroom, leaving ~475.9 GB for activations, intermediate buffers, and OS overhead. This is comfortably within a single 8×H100 node's capacity.

[ILLUSTRATIVE][ASSUMPTION]: vLLM continuous batching on 8×H100 with a 70B FP16 model and 9.2K context yields ~50 tokens/s aggregate throughput for 300‑token outputs. The prefill phase (9.2K tokens) dominates TTFT: at ~1.08 s it leaves ~0.12 s of headroom against the 1.2 s budget *for prefill alone*. Adding retrieval (~120 ms) puts the full TTFT (retrieval + prefill) at ~1.20 s, i.e. at the 1.2 s SLO line with no prefill-side margin; the real margin is the p95 ≤ 2 s target.

[ILLUSTRATIVE][DERIVED]: tokens/s per dollar for generation. On‑demand H100 list price ~$2.50/hour per GPU → 8×H100 = $20/hour. At ~50 tok/s aggregate throughput, the effective cost is ~0.40 $/tok/s, or equivalently ~2.5 tokens/s per dollar-hour. In tokens‑per‑dollar terms: 50 tok/s × 3600 s/hr ÷ $20/hr = 9,000 tokens per dollar per hour of runtime.

> **Economics unit note (reconciliation with Ch. 4 and Ch. 15).** Both chapters use the same on-demand price basis: ~$2.50/hr per H100 → ~$20/hr per 8×H100 host. Two things must be kept straight. First, *units*: this chapter expresses **tokens per dollar-hour** (token-rate × 3600 s ÷ hourly cost), while Chapter 4 expresses **tokens per second per dollar** (token-rate ÷ per-second cost); convert by ÷3600. Second, *throughput basis*: the ~50 tok/s used here is a deliberately **conservative single-stream / low-batch generation rate** adopted to illustrate the per-dollar *method*, **not** a claim about the host's batched serving throughput. Chapter 15's figures are two different quantities, and neither is the single-stream decode rate used here: its **~8,000 tok/s is a prefill-side / whole-request rate** (Chapter 4's ≈8.5K tokens/s prefill — 9,200 tokens ÷ ~1.08 s — not batch-1 *decode*, which at the canonical 25 ms/token is ~40 tok/s, Chapter 2), while its **~35,000–56,000 tok/s** is the multi-request *serving* throughput under FlashAttention + continuous batching. The ~50 tok/s here (single-stream decode) and Chapter 15's ~8,000 tok/s (prefill-side) are therefore different phases of the same host, not two values for one quantity. The per-dollar figures therefore scale up substantially at batch, and the 9,000 tokens/dollar-hour figure should be read as a floor set by the single-stream assumption, not as the host's economic optimum. [ILLUSTRATIVE][DERIVED]

[ILLUSTRATIVE][DERIVED]: tokens/s per dollar with prefill included. (Mixed-input convention: when a derivation mixes a canonical price with an illustrative rate, the result carries the non-canonical provenance — here the 50 tok/s rate input is [ILLUSTRATIVE][ASSUMPTION] while the $20/hr price is canonical.) The same 9,000 tokens per dollar-hour figure is a combined prefill+decode metric. Because this workload is input‑heavy (9.2K input vs 300 output tokens), the prefill leg consumes **~97% of the tokens** per request (9,200 ÷ 9,500) — and, because each prefill token runs the full $2\times70B$ forward FLOP, it is also **~97% of the linear forward-FLOP cost** (before the quadratic attention term). But it is only **~13% of the wall-clock time** (1.08 s prefill vs 7.5 s decode), because prefill is compute‑intensive yet batchable across concurrent requests, while decode is a sequentially‑limited token-by-token stream. So the honest picture is *both*: prefill dominates the compute/FLOP budget (and hence the GPU-hour cost of running the pipeline), and decode dominates the wall-clock latency budget (and hence per‑request service time). The per‑dollar economics therefore favor models that reduce the *prefill compute* burden (smaller context, larger batch, lower per‑token FLOP) more than models that optimize decode throughput alone — but a deployment must balance both, since decode still sets the latency SLO.

### (c) Base‑model + RAG + guardrails vs fine‑tuned model

The architect must choose between two paradigms:

**Paradigm 1 — Base model + RAG + guardrails:**

- The base 70B model receives the retrieved 9.2K context via prompt injection.
- Guardrails (PII redaction, style enforcement, refusal filtering) are applied as post‑generation or prefix‑check layers.
- No model weights are trained on domain data; the knowledge source is the vector database.

**Paradigm 2 — Fine‑tuned model on domain‑specific Q‑A pairs:**

- The base model is fine‑tuned (full-parameter, or low‑rank adaptation (LoRA)) on thousands of question‑answer pairs reflecting the enterprise's terminology and reasoning patterns.
- Inference uses the fine‑tuned weights without a retrieval step, or with a much shorter retrieved context. Fine‑tuning is **not** a dependable substitute for retrieval when the requirement is factual corpus access, freshness, attribution, or precise enterprise knowledge — fine‑tuning distills *behavior, style, task patterns, format, and tool‑use policy*, not a guarantee that arbitrary facts are recalled faithfully. Whether it reduces retrieval dependence for a *particular* task is an empirical question to be measured on that task's evaluation set.
- Additional costs: training compute, storage of fine‑tuned weights, and reduced flexibility for new topics.

([ILLUSTRATIVE][ASSUMPTION] — not a reference measurement): for the canonical workload, a well‑designed RAG + guardrails pipeline *may* approach a fine‑tuned model's answer quality on in‑domain queries. This is **task‑, model‑, data‑, and evaluation‑dependent** — it is not derivable from the architecture alone. The two mechanisms do different work: **RAG** supplies external, mutable knowledge (grounding, provenance, freshness); **fine‑tuning** shapes behavior, style, domain reasoning patterns, format, and tool‑use policy. Either or both can improve answer quality, and they can be combined. Whether fine‑tuning reduces retrieval dependence for this workload must be established by measuring answer quality on the actual evaluation set. The economic comparison should be framed **parametrically**, not with a single number, because the break‑even depends on the quality uplift (domain‑specific) and the query volume (workload‑specific). The decision variable is the break‑even query volume $Q^*$ where the annualized cost of fine‑tuning, divided by its quality advantage, crosses the RAG baseline:

$$
Q^*\; =\; \frac{C_\text{train} + C_\text{weights-extra}}{\Delta Q \cdot \text{value per corrected query}}
$$

where $C_\text{train}$ is the one‑time training compute, $C_\text{weights-extra}$ is the incremental storage/carry cost, and $\Delta Q$ is the (domain‑specific, must‑be‑measured) quality uplift in corrected answers per query. Below $Q^*$, RAG + guardrails is economically dominant because the fine‑tuning cost is spread over too few queries to be repaid; above it, fine‑tuning may recover its upfront cost through quality gain. (Scenario structure, not a single claimed break‑even volume; the exact $C_\text{train}$, $C_\text{weights-extra}$, and $\Delta Q$ are workload‑ and domain‑specific and should be measured, not assumed.)

Fine‑tuning does **not** make the model smaller — pruning is a separate operation. A full fine‑tune keeps the ~140 GB 70B weight set (and adds a checkpoint), while a LoRA adapter is tiny but does not change the live weight footprint. Consequently the latency effect of fine‑tuning is not "smaller effective model" and cannot be assumed to cut TTFT; any TTFT change must be measured. The real cost changes are: (a) one‑time training compute, and (b) incremental storage, both against the RAG pipeline's prefill cost (~1.08 s, which dominates any plausible TTFT delta). Parametrically, fine‑tuning becomes worth it only when its annualized cost over $Q$ queries is repaid by $\Delta Q \cdot \text{value}$ — this is exactly the $Q^*$ above. The illustrative cloud‑GPU training cost is presented as a scenario range, not a fact, and must be benchmark‑validated against a target workload.

**Takeaway:** For the canonical enterprise Q&A RAG workload, the base‑model + RAG + guardrails paradigm is the economically preferred choice. Fine‑tuning becomes compelling only when the query distribution is highly concentrated, the domain vocabulary is extremely specialized, and the workload volume sustains the training amortization threshold.

## 4. Measurement

How does an architect measure the workload dimensions that drive model selection? The token-counting habits of Ch 1 §1.4 apply unchanged; the three things the *selection* view adds are:

1. **Measure the token split on real employee queries, not the heuristic.** Run the model's own tokenizer on representative prompts from the target domain — the "4 chars ≈ 1 token" heuristic is for estimation only. For the canonical workload, measure the exact prompt+context token count on real employee queries before fixing the model, because the ~30× input-to-output ratio is the single biggest driver of this system's cost structure (Ch 4).
2. **Quantify the output size, since that drives decode cost and per-request latency.** The output token count determines decode bandwidth and p95 TPOT; a large-output paradigm (e.g. long-form generation) changes the model-selection calculus versus a short-output Q&A system.
3. **Know the 95th-percentile context length, not just the average.** Log the distribution of context lengths. A workload that averages 9.2K input but peaks at 32K (a variant flagged in Ch 4) requires a different KV budget and, with it, a different model-size or attention-hybridity choice. Size against the tail.

These checks let model selection be made on measured workload dimensions rather than a generic "bigger model is better" assumption.

### Model identity includes the execution path

Backend identity completes the candidate: the relevant identity includes the checkpoint revision, tokenizer, numerical representation, engine revision and device backend. A loader may recognize the model while a fused attention operator, recurrent-state update or quantized expert kernel is unavailable on the target device. A fallback can restore execution but change latency, memory use or numerical behavior. We therefore separate model-quality acceptance from backend qualification. Both must hold for the same configuration. A small successful completion does not validate long-context state, concurrent-request isolation or the intended serving SLO.[^oct-ix-t0]

## 5. Common Mistakes

- **Starting with "which model is best?"** Instead of characterizing the workload first. The workload's token profile, latency budget, and economic constraints are what narrow the model space; starting with a model short‑circuits the reasoning chain and leads to post hoc justification.

- **Ignoring the KV cache cost of long contexts.** A 9.2K input on a 70B model costs ~24.1 GB of KV cache (initial). An architect who does not account for this will either over‑provision infrastructure or hit SLO violations when the cache spills to host memory or SSD.

- **Quoting context window as free capacity.** The 128K or 1M token window is an upper bound, not a recommendation. Using even 9.2K of a 128K window still costs for the length actually used. The cost is proportional to the *used* length, not the *available* length.

- **Assuming embedding dimension is a free parameter.** Increasing embedding dimensionality *within a given model family or controlled configuration* can improve retrieval fidelity, but dimensionality alone does not predict quality across different embedding models. Higher dimension also raises FLOP cost, index storage, and per‑query latency, so the architect must balance these against the workload's quality requirements rather than treat dimension as a cost‑free or universally-better knob (see the caveat in §5.3).

- **Over‑engineering the fine‑tuning path.** Fine‑tuning adds training compute and model/checkpoint‑management cost; depending on the adaptation and serving method, it may also add inference or operational overhead (e.g. a LoRA adapter applied dynamically at serve time can introduce overhead, whereas a merged/fully‑fine‑tuned model of identical architecture need not change the inference shape). The break‑even analysis (the parametric $Q^*$ in §5.3) shows that for most enterprise RAG workloads, the RAG + guardrails paradigm dominates on TCO. Fine‑tuning should be a deliberate choice triggered by a sustained query volume, not a default.

## 6. Architecture Consequence

Whatever we learned here, file it under **"can I size the workload before I pick a model?"** Concretely, the decision this chapter enables is:

- Estimate tokens‑per‑request (input and output separately), and therefore tokens‑per‑second capacity and cost, before choosing a model or a serving configuration.
- Use the selection surfaces (quality, latency, KV cost, cost/token, retrieve‑vs‑generate) to narrow the model space from the full vendor catalog to a handful of viable candidates.
- For RAG workloads, select the embedding model and generation model as a two‑part decision, not a single choice. The embedding model is chosen at ingestion time (compute‑light, storage‑bound); the generation model is chosen at serving time (compute‑bound, latency‑bound).

This consequence feeds directly into the fine-tuning-for-specific-workloads pattern and the RAG pattern (both cataloged in Ch 26, Patterns Library): the architect first characterizes the workload, then lets the characterization speak the model selection, not the other way around.

## 7. What We Still Don't Know

[HYPOTHESIS]: the interaction between embedding dimension and retrieval quality across diverse enterprise domains is not yet characterized with reproducible benchmarks. Early evidence suggests 768 dim is a sweet spot, but the quality difference between 768 and 1024 dim varies by corpus genre (legal vs. engineering vs. creative), and no public study quantifies this domain‑dependence.

[HYPOTHESIS]: the break‑even point between RAG + guardrails and fine‑tuned models as a function of query volume and domain specialization is **model‑ and domain‑dependent**: it is set by the $Q^*$ equation above (training + storage cost over the quality uplift), not by a universal rule of thumb. Any quoted break‑even volume is a derived scenario value; more data points and a measured $\Delta Q$ are needed before it can be stated as a general principle.

[HYPOTHESIS]: guardrail latency (PII redaction, refusal checking) on generated 300‑token outputs, ~2–8 ms/request on CPU in the illustrative scenario; measure on the target stack (the figure depends on the guardrail implementation and hardware).

Each of these flags is an open empirical question a team should resolve against its own target workload — resolved by measurement into [1P][FACT] or [2°][FACT], promoted to [1P][DERIVED] or [2°][DERIVED] where the resolution is arithmetic, or dropped — rather than left as an untested assumption.

## 8. End-of-Chapter Mini-Case: Choosing the Model for the Enterprise Q&A

*(Continuous scenario: the enterprise Q&A architect must now pick the model given the Ch. 4 characterization.)*

An architect is assembled for a design review of the enterprise Q&A tool described in Chapter 4 — the canonical workload (Ch 4, Table 4-2). The team has agreed on the retrieval architecture: vector search with embeddings, 768‑dim all‑mpnet‑base‑v2, late‑interaction (MaxSim) retrieval over a 1 M‑chunk corpus.

From the unit-and-token work of Ch 1 alone (Ch 5's selection surfaces), the architect can immediately check the consequences:

- **768‑dim embeddings** give adequate retrieval quality at ~1 GFLOPs per embedding, with ~3.1 GB index storage for a 1 M‑chunk corpus (vs ~1.5 GB at 384‑dim) — a persistent footprint that scales with corpus size, alongside the 70B base model.
- **9.2K input** at ~2.62 MB/KV‑token costs ~24.1 GB of cache (initial) on the 70B generation model, well within the 8×H100 node's 640 GB HBM. The prefill TTFT of ~1.08 s plus retrieval (~120 ms) sits at the 1.2 s TTFT budget, with the p95 ≤ 2 s SLO giving the real margin.
- The **30× input‑vs‑output ratio** means this system is prefill‑dominated; model selection must weigh KV cache cost and prefill throughput more heavily than decode throughput.
- The **base‑model + RAG + guardrails** paradigm produces the lower **modeled** TCO under the illustrative cost and quality assumptions used in this worked example (see the parametric $Q^*$ break‑even above). This is not a general 10× cost relationship — the actual ratio depends on the domain‑specific quality uplift and the query volume, and must be measured rather than assumed.

The architect now has a concrete model shortlist: 768‑dim all‑mpnet‑base‑v2 for the retrieval leg, and the 70B FP16 base model for the generation leg (dense — the MoE challenger from Ch 3 was rejected on residency and KV grounds), served on 8×H100 with vLLM continuous batching. No fine‑tuning is needed at this scale. The architecture decision record (to be written in Chapter 25) will reference this characterization and the selection surfaces that drove it.

---

![Fig 5.1 — Model selection for RAG: workload → five selection surfaces → two legs (retrieval/embedding, generation/70B) → the system decision. The five surfaces are the *model-selection* dimensions; they are deliberately distinct from the **end-to-end evaluation gates** (retrieval quality, reranking, embedding recall, grounding, and final answer quality) that a RAG system must also pass — those gates are measured on the target corpus (§5.4) and are not shown here because this figure is a selection map, not an evaluation pipeline. [ILLUSTRATIVE conceptual]](figures/fig-05-0501.png)


---

**End of Chapter 5**

[^oct-qz-awq]: AWQ: activation-aware weight quantization of large language models (arXiv 2306.00978v6): https://arxiv.org/abs/2306.00978v6

[^oct-qz-gptq]: GPTQ: post-training quantization for generative pre-trained transformers (arXiv 2210.17323v2): https://arxiv.org/abs/2210.17323v2

[^oct-df-struct]: Structured-output documentation versus grammar-constraint rejection in inspected first-party sources, retrieved 2026-10-28 (outside the book's 2026-08-30 evidence cutoff): Mercury structured outputs (JSON-schema generation): https://docs.inceptionlabs.ai/capabilities/structured-outputs ; SGLang DiffusionGemma cookbook at pinned revision `a1966e1b5d8b750b494d7e53cca1d2464f960038` (the recipe rejects grammar-constrained requests): https://raw.githubusercontent.com/sgl-project/sglang/a1966e1b5d8b750b494d7e53cca1d2464f960038/docs/cookbook/autoregressive/Google/DiffusionGemma.mdx

[^oct-ix-t0]: Inspected first-party engine sources for device-backend-specific model, operator and fallback paths, retrieved 2026-10-28 (outside the book's 2026-08-30 evidence cutoff): vLLM supported models — XPU: https://docs.vllm.ai/en/stable/models/hardware_supported_models/xpu ; vLLM `vllm/platforms/xpu.py` at pinned revision `5df63a7203cdb9328d824a27b682e77c7b9928be`: https://raw.githubusercontent.com/vllm-project/vllm/5df63a7203cdb9328d824a27b682e77c7b9928be/vllm/platforms/xpu.py ; SGLang `docs/hardware-platforms/xpu.mdx` at pinned revision `a1966e1b5d8b750b494d7e53cca1d2464f960038`: https://raw.githubusercontent.com/sgl-project/sglang/a1966e1b5d8b750b494d7e53cca1d2464f960038/docs/docs/hardware-platforms/xpu.mdx
