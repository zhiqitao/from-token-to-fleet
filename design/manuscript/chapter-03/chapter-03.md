# Chapter 3 — Understanding the Model

## The Architect's Question

After this chapter we should be able to reason about what a model's parameter structure means for deployment: dense versus Mixture-of-Experts (MoE), total parameters versus active parameters per token, and what each implies for compute budgets and memory budgets. We will meet the mechanisms (how MoE routes, how attention weights are computed) not to learn how to train a model but so that, as architects, we can look at a model card and immediately know whether the quoted parameter count is what we actually pay for at inference time, and whether the KV cache will grow as expected. After this chapter we can ask: *given a workload and a model architecture, what is the real residency and compute cost per token?*

## 1. Concept

The **parameter allocation regime** of a model determines how many of its weights are touched on each forward pass. This regime is not a property of the model family name alone; it is a consequence of the training objective and the routing mechanism.

- **Dense models** activate *all* parameters for every token. A 70B dense model reads all 70B weights (or close to it) for every token, because every layer's full hidden dimension participates in every attention and feed-forward computation. The parameter count on the model card is the inference cost count.
- **Mixture-of-Experts (MoE) models** route each token to a *fraction* of the total parameters. A MoE model may have 236B total parameters distributed across eight experts, but only the top-2 (or top-1) experts are activated per token. The quoted total parameter count includes the unused experts; the *active* parameter count per token is the fraction that routing selects.

The architect-relevant distinction: **total parameters ≠ active parameters per token.** This inequality is the single most important number to read from a model card when sizing a deployment, because it directly changes the compute cost per token. However, the KV cache does not share this privilege — we will show why MoE sparsity saves compute but not memory.

A note on provenance: the total-versus-active distinction arises from the training regime. In dense pre-training, every token sees the full model gradient; in MoE pre-training, a routing loss directs each token to the most relevant expert(s), and the unused experts receive no gradient for that step. The routing mechanism itself (top-k, importance sampling, learned gates) is an architectural decision that outlives training and becomes a deployment fact.

## 2. Mental Model

Think of a model's parameters as a **resource pool** that is allocated differently depending on the routing regime.

- In a **dense** model, the pool is *fully allocated* every time. If the model is 70B params in FP16, we need 140 GB of weight memory available for every token. There is no "spending less" — the full 140 GB is the residency floor.
- In an **MoE** model, the pool is *fractionally allocated*. The total pool may be large (reflecting the model's capacity and training compute), but what we actually wire up per token is a slice. With top-2 routing from 8 experts, roughly 2/8 = 25% of the total parameter mass is active per token. This fraction saves compute (fewer FLOPs) but the attention layers still see every token, so the KV cache still grows with context length just as in a dense model.

The durable mental model: **total parameters set the ceiling; active parameters per token set the floor.** The architect must track both numbers.

## 3. Worked Example

We now carry concrete arithmetic using the canonical enterprise Q&A scenario (§14: ~2,000 users, ~10 rps average, ~40 rps peak, 1,200 + 8K context ~9.2K input, 300-token output, 70B-class model, FP16, 1 host 8×H100). The numbers below are worked out explicitly; where a model's exact spec is not first-party verified, it is labeled [VERIFY].

### Dense 70B model (canonical, [1P])

| Metric | Value | Derivation |
|---|---|---|
| Total parameters | 70B | §14 canonical scenario [1P] |
| FP16 residency (total) | 140 GB | 70B × 2 bytes = 140 GB [1P DERIVED] |
| Active parameters per token | 70B | All parameters active for every token [1P FACT] |
| FLOPs per forward pass (approx.) | ~2.8T | 70B × 4 FLOP/param typical for transformer [2° DERIVED] |

*Table 3.1 — Dense 70B model parameter arithmetic (worked example, not reference).*

### MoE model representative (Mixtral 8x7B class, [2°])

We contrast with a representative MoE model in the Mixtral lineage. The exact parameter split is not always published in vendor model cards; the numbers below are plausibility-checked and flagged.

| Metric | Value | Derivation |
|---|---|---|
| Total parameters (across 8 experts) | ~47B | ~6B per expert × 8 + embeddings [2° DERIVED] |
| Active parameters per token (top-2 routing) | ~14B | Top-2 from 8 experts, ~3–5% active/total ratio (frontier MoE [2° DERIVED]); actual activation ~25% for top-2-from-8 configuration shown |
| FP16 active residency per token | ~28 GB | 14B × 2 bytes = 28 GB [VERIFY DERIVED] |
| FLOPs per forward pass (approx.) | ~0.56T | 14B active × 4 FLOP/param [VERIFY DERIVED] |
| Compute ratio (active/total) | ~3–5% (frontier) | 14B ÷ 47B [2° DERIVED] |

*Table 3.2 — MoE model parameter arithmetic (worked example, not reference).*

### Why MoE saves compute but not KV-cache memory

The compute savings are straightforward: if only $n_a = 14$B of $n_t = 47$B total parameters are active per token, the FLOP count drops by the active fraction. Since per-token FLOPs scale with the number of parameters touched,

$$
\text{FLOP}_{\text{MoE/token}} = \frac{n_a}{n_t} \times \text{FLOP}_{\text{dense/token}} = \frac{14}{47} \times 2.8 \text{ T} \approx 0.56\text{ T}
$$

— roughly a 5× reduction in compute per token. This is why MoE models can be "larger" (more total parameters for the same training FLOP budget) while keeping per-token cost comparable to a smaller dense model.

The KV-cache story is the surprising part. Recall from Chapter 1 (§KV cache as a concept, Chapter 1) that the KV cache stores one key and one value tensor per token, per layer. The cache size per token scales with the canonical Chapter 1 formula, $KV_{\text{per-token}} = 2 \times n_\text{layers} \times d_\text{hidden} \times \text{bytes-per-value}$. Critically, **the attention mechanism processes every token in the context densely** — each token's query attends to all previous tokens' keys and values, regardless of whether the model is dense or MoE. MoE sparsity operates in the feed-forward sub-layer; it does not change the attention sub-layer's behavior.

Therefore, for a 70B-class model (dense or MoE) with 8K–9.2K input context:

- **Dense 70B**: KV cache ~1.3 MB per token × 9,200 tokens ≈ 12 GB (at 8-bit) or ~24 GB (at FP16-relevant precision for the key/value storage pattern discussed in Ch. 7).
- **MoE 70B-equivalent**: The KV cache is *identical* in size, because attention still processes all 9,200 tokens densely. The fact that only 14B of 47B total parameters are active in the feed-forward layers does not reduce the number of keys/values emitted by the attention layers.

In other words: MoE sparsity = compute sparsity (fewer FLOPs per token). MoE sparsity ≠ memory sparsity (KV cache still grows linearly with context length, same as dense). Only changing the attention mechanism itself (e.g., hybrid/linear attention, compressed latent attention, or KV offload) can stop the cache from growing. This distinction — compute-sparsity versus memory-sparsity — is one an architect has to get exactly right.

> **Key takeaway:** MoE lets us fit a larger total parameter budget within a weight-residency constraint (active weights take less FP16 memory), but the KV-cache budget must be provisioned as if the model were dense. Do not assume MoE reduces KV-cache memory.

## 4. Measurement

How do we determine the total-versus-active split for a model we haven't trained?

1. **Model card inspection.** Most model vendors publish the total parameter count. The active-per-token count is harder to find; it requires reading the architecture documentation for the routing mechanism (top-k, top-1, importance-based). If the model card says "70B parameters" without qualification, assume dense unless it explicitly describes an MoE layout.

2. **Runtime measurement.** For a given input, profile the number of FLOPs or the memory footprint of active weights. Tools such as `torch.profiler` can count active parameters, but this is an empirical measurement, not a first-party spec.

3. **Architecture diagram.** For MoE models, the number of experts × parameters-per-expert gives the total; the routing hyperparameter (top-k) × parameters-per-expert gives the active per token. This is a derived fact from the source code/release, not always on the model card.

> **Practical habit:** When we encounter a model quoted in "X billion parameters," pause and ask: *is this total or active?* For dense models they are the same; for MoE models they diverge. Misreading this is the most common source of KV-cache and compute underestimation.

## 5. Common Mistakes

- **Assuming total parameters = active parameters per token.** This is the single most costly misread. For a MoE model, the quoted "236B" or "47B" is the total across all experts; the active count per token is a fraction. Using the total number to size KV cache or memory will overestimate compute needs (if we think we need 236B × 2 bytes we'll over-provision weight memory) or underestimate it (if we size for active but forget KV cache is dense).

- **Confusing compute sparsity with memory sparsity.** MoE reduces FLOPs per token because fewer parameters are active. It does *not* reduce the number of keys/values written to the KV cache. An architect who assumes MoE shrinks KV cache will be blindsided by memory pressure at long context lengths.

- **Using MoE as a free lunch for long-context workloads.** The compute savings from MoE are real, but the memory cost (weights + KV cache) must be provisioned at the total-parameter scale for weight residency and at the-full-context scale for KV cache. Neither benefit is "free" in the other domain.

- **Ignoring routing overhead.** Top-k routing itself requires computing routing scores (a softmax over expert assignments). This adds a small but non-zero compute cost that is sometimes omitted from published FLOP counts. It is usually negligible compared to the feed-forward arithmetic but should be acknowledged.

## 6. Architecture Consequence

Knowing whether a model is dense or MoE, and whether the quoted parameter count is total or active, directly changes three architectural decisions:

1. **Weight residency budget.** For a dense 70B model, provision 140 GB of FP16 weight memory per host. For a MoE model with ~47B total and ~14B active, provision ~28 GB for the active weights + a smaller overhead for the unused experts (they may be swapped or kept on device depending on the deployment framework). MoE allows a larger total parameter budget within the same weight-memory ceiling, but the active-fraction budget is what matters for "weights on device."

2. **KV-cache provisioning.** Provision the KV cache as for a dense model of the same context length and hidden dimension. Do not apply a MoE sparsity factor to the KV cache. If we are running a 9.2K-token input on a 70B-class model (dense or MoE), the KV cache memory is the same order of magnitude — plan accordingly.

3. **Parallelism and routing strategy.** MoE deployment requires a routing strategy (e.g., expert placement, dispatcher, switchboard) and often expert parallelism across GPUs. This adds infrastructure complexity (cross-GPU communication for expert routing) that dense models do not have. The architectural choice between dense and MoE is therefore not just a parameter-count decision; it is a deployment-complexity decision.

### The 2026 baseline shift: same framework, new constants

**The 2026 trend signal (forward-looking).** By August 2026 the four frontier open-weight families converge on one direction, and it is not more of the same dense scaling: extreme MoE sparsity (single-digit active-parameter fractions — Qwen 6 B of 125 B, Kimi K3 104 B of 2.8 T) coupled with **hybrid attention** (compressed/sparse/linear hybrids such as Gated DeltaNet + sparse attention) has become the standard way to make long-context inference affordable. Chapter 27 (Appendix A) documents these at full depth with first-party provenance; what matters here, in the model-understanding chapter, is that this is not a competing mechanism but the *same* dense-vs-MoE, total-vs-active, KV-vs-compute machinery this chapter just taught — with new constants. We hold that view explicitly as the **forward-looking direction** the architect should size toward, and flag it below as continuing future work (the frontier moves; this handbook is a living document, and Appendix A is where the moving part lives).

**Why the trend signal should not be read as "dense is dead".** The convergence of the four *frontier* families on extreme MoE sparsity describes the top of the market — the ~100B-and-up tier that anchor ~2.8T-parameter fleets. It is not a claim that dense models have disappeared. On the contrary, the smaller, denser tier is alive and actively shipping in 2026 for exactly the constrained-deployment reasons this chapter teaches: **Qwen3.8-27B** ([1P: HF Qwen/Qwen3.8-27B]) is a dense 27.8B model whose 4-bit weights fit on a single 24 GB consumer GPU, and **Muse Glimmer 30B** ([1P: Meta via vLLM-Recipes]) is a dense 29.6B local-agentic model that runs in ~18 GB. These exist because the dense-vs-MoE trade is itself a *deployment* decision, not a date: MoE buys active-parameter efficiency at the cost of total-parameter memory and routing complexity — worthwhile when you serve many requests from a large pool of resident weights, but hard to justify when your whole budget is one consumer GPU whose total weights already overrun. That is precisely why this book keeps its canonical on the dense tier: the canonical must serve the architect whose *whole fleet* is a handful of boxes, not only the one sizing a 2.8T datacenter model. The framework does not change between tiers — total vs active, KV per-token, and residency budgeting apply identically to a 27B dense laptop model and a 125B/6B MoE fleet model.

**Why the rest of this chapter's canonical stays a dense full-MHA model.** If the trend is MoE + hybrid, why does this book's canonical still size a dense 70B full-MHA workload? Because a dense model with full multi-head attention gives the cleanest single-constant KV formula (`2 × layers × hidden × bytes`) and the largest KV footprint — the conservative worst case an architect should always size against first. Teaching against that bound means the reader learns the framework on the hardest memory case and then relaxes it. It is a deliberate teaching simplification, not a claim that in 2026 an enterprise RAG fleet really runs on dense 70B.

**One verified 2026 transfer: Qwen3.8-Flash-Next.** The model card [1P: HF Qwen/Qwen3.8-Flash-Next] is the Qwen4-architecture preview: **125 B total / 6 B active** (plus a separate 51 B of offloadable N-gram embedding parameters), **512 MoE experts** (10 routed + 1 shared per token), and **hybrid attention** — Gated DeltaNet (GDN) on three of every four layers plus Qwen Sparse Attention (QSA) on the fourth. This is exactly the "125B/6B active MoE + Gated DeltaNet/QSA" class of model a 2026 architect actually considers. Stepping through this book's own arithmetic:

- **Weight residency** (Ch. 7's floor): active weights are ~6 B × 2 B = ~12 GB, not the canonical 140 GB — MoE sparsity collapsed the on-GPU weight floor by ~12×. But total weights dominate the memory ceiling: ~125 B × 2 B ≈ 250 GB (plus the offloadable N-gram), so the *total-vs-active* split of this chapter is not a footnote — it is the difference between fitting on one host and sharding across several.
- **KV cache** (Ch. 7/8): the canonical `2 × layers × hidden × bytes` KV formula is the full-MHA bound. Qwen's hybrid attention attacks the KV constant itself at the mechanism level — GDN keeps a fixed-size recurrent state (context cost no longer grows linearly per token across those layers) and QSA attends sparsely at micro-block granularity — so per-token KV no longer follows the dense formula. The framework question ("does it fit?") is unchanged; the *function* you plug in for KV is not the dense one.
- **Compute** (Ch. 8): active-parameter FLOPs drop to ~2 × 6 B per token, but the QSA/GDN layers ride different roofline points than a dense 70B prefill/decode split, so the throttled-resource conclusion must be re-derived per model (Ch. 8's measurement discipline, not a one-time number).

**The architect's move is unchanged.** For the canonical dense model this book sizes memory, compute, and fleet with one clean constant set. For a 2026 MoE/hybrid model the architect does the *same* decision loop — read the model card, get total vs active, get the KV scheme's per-token function, size residency and roofline, then decide parallelism (Ch. 10) and serving (Ch. 11). Only the constants differ; the framework does not. Chapter 27 walks the four frontier models through exactly this re-derivation and flags which vendor numbers still carry a verify-on-own-hardware caveat.

> **Recorded as future work.** This forward-looking view is intentionally a *pointer*, not the full treatment — the complete, current analysis of the 2026 frontier lives in Chapter 27 (Appendix A). Because the frontier moves quickly and every vendor figure in it carries a verify-on-own-hardware caveat, we treat the trend as a living section to be updated against new model cards, rather than a set of frozen gospel numbers (per the handbook's "living document" framing, book-architecture.md §10). An architect should re-check Appendix A before any capacity decision — the constants, not the framework, are what change.

## 7. What We Still Don't Know

As of 2026-08, several questions remain open and are flagged [VERIFY]:

- **Exact active-fraction per token for commercial MoE models.** Model cards rarely publish the precise top-k routing distribution under real workloads. We know the architectural top-k (e.g., top-2 from 8 experts), but the actual fraction of active parameters may vary with prompt content, token position, and expert availability. [VERIFY HYPOTHESIS]
- **Whether router latency offsets MoE compute savings.** The cost of computing routing scores and dispatching to experts is not always included in published FLOP counts. On some hardware the routing overhead can be significant enough to narrow the compute gap between MoE and dense. [VERIFY HYPOTHESIS]
- **KV-cache behavior under MoE with expert swapping.** When experts do not fit on a single GPU and must be swapped (offloaded), does the KV cache interact with the swapping mechanism in ways that change its effective size or access pattern? This has not been systematically characterized. [VERIFY HYPOTHESIS]

These flags exist because home-lab measurements are not reference per the evidence taxonomy; they will be resolved (promoted, dropped, or demoted) before publication.

## 8. End-of-Chapter Mini-Case

*(Continuous scenario — this is its first appearance, chaining from the enterprise Q&A thread.)*

An architect is fleshing out the design of the internal Q&A tool described in Chapter 1's mini-case. The team is torn between a dense 70B model and a MoE model with 8 experts (adisedly total ~47B params, ~14B active per token). They ask: "If we go MoE, can we cut our GPU memory budget?"

From the model-understanding chapter, the architect can answer: *Weight residency yes — active parameters take ~28 GB vs. 140 GB for a dense 70B, we could fit the model on fewer GPUs or a smaller host. But KV-cache memory no — the attention layers still process every token densely, so the cache budget for a 9.2K-context input is the same regardless of whether the model is dense or MoE. We still need to provision for ~12 GB of KV cache (at 8-bit) or ~24 GB (at the precision pattern discussed in Ch. 7) per request, and we'll also need expert-routing infrastructure on top of that.*

The architect's decision therefore hinges on whether the compute savings from MoE (fewer FLOPs per token, potentially lower $/token) outweigh the added routing complexity and the fact that KV-cache memory is unchanged. The team decides on a MoE model for the compute/$ advantage, but provisions the KV-cache budget at the dense-model rate, and adds one GPU dedicated to the routing dispatcher.

* * *
![Fig 3.1 — Dense vs MoE parameter allocation and KV-cache behavior [2° DERIVED]](figures/fig-03-0301.png)

*Fig 3.1 — Parameter-activation contrast. A dense 70B activates all 70B parameters per token (residency ≈ 140 GB, KV grows linearly with context). An 8-expert MoE activates only the top-2 (~14B) per token (residency ≈ 28 GB active), but KV-cache growth with context is identical to dense — attention still processes every token.*

### Table 3-1 — Parameter and KV-cache arithmetic for the canonical workload

| metric | dense 70B | MoE (8×7B class) | derivation |
|---|---|---|---|
| total parameters | 70B | ~47B | [2°] expert split |
| active params per token | 70B | ~14B | top-2 from 8 [~3–5% frontier MoE [2° DERIVED]; Mistral top-2-from-8 ~25% for reference]
| FP16 residency (total) | 140 GB | ~94 GB | 70B × 2 / 47B × 2 |
| FP16 residency (active) | 140 GB | ~28 GB | 70B × 2 / 14B × 2 |
| KV cache per request (9.2K ctx, 8-bit) | ~12 GB | ~12 GB | identical — attention dense |
| FLOPs per forward pass | ~2.8T | ~0.56T | 70B × 4 / 14B × 4 |
| compute speedup (active/total) | 1× | ~5× | 14B ÷ 70B [~3–5% frontier; Mistral top-2-from-8 ~25% for reference]

*All figures trace to the §14 canonical scenario; MoE column is a [2°] worked variant, not a measurement claim.*

---
*Next chapter: Chapter 4 — The Anatomy of an AI Workload, which characterizes the enterprise Q&A RAG workload across the six dimensions (quality, traffic, token profile, latency, economic, operational constraints) and uses the same continuous mini-case scenario.*

*Canonical scenario citation: all numerical values in this chapter that trace to the §14 canonical enterprise Q&A RAG workload are drawn from the fixed source of truth defined in book-architecture.md §14. The dense 70B numbers are [1P] per the canonical scenario; MoE numbers are [2°] plausibility-checked variants.*