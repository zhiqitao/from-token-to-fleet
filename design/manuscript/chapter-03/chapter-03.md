# Chapter 3 — Understanding the Model

## The Architect's Question

After this chapter we should be able to reason about what a model's parameter structure means for deployment: dense versus Mixture-of-Experts (MoE), total parameters versus active parameters per token, and what each implies for compute budgets and memory budgets. We will meet the mechanisms (how MoE routes, how attention weights are computed) not to learn how to train a model but so that, as architects, we can look at a model card and immediately know whether the quoted parameter count is what we actually pay for at inference time, and whether the KV cache will grow as expected. After this chapter we can ask: *given a workload and a model architecture, what is the real residency and compute cost per token?*

## 1. Concept

The **parameter allocation regime** of a model determines how many of its weights are touched on each forward pass. This regime is not a property of the model family name alone; it is a consequence of the training objective and the routing mechanism.

- **Dense models** activate *all* parameters for every token. A 70B dense model reads all 70B weights (or close to it) for every token, because every layer's full hidden dimension participates in every attention and feed-forward computation. The parameter count on the model card is the inference cost count.
- **Mixture-of-Experts (MoE) models** route each token to a *fraction* of the total parameters. A MoE model may have 236B total parameters (an illustrative figure) distributed across eight experts, but only the top-2 (or top-1) experts are activated per token. The quoted total parameter count includes the unused experts; the *active* parameter count per token is the fraction that routing selects.

The architect-relevant distinction: **total parameters ≠ active parameters per token.** This inequality is the single most important number to read from a model card when sizing a deployment, because it directly changes the compute cost per token. However, the KV cache does not share this privilege — we will show why MoE sparsity saves compute but not memory.

A note on provenance: the total-versus-active distinction arises from the training regime. In dense pre-training, every token sees the full model gradient; in MoE pre-training, a routing loss directs each token to the most relevant expert(s), and the unused experts receive no gradient for that step. The routing mechanism itself (top-k, importance sampling, learned gates) is an architectural decision that outlives training and becomes a deployment fact.

## 2. Mental Model

A model's parameters form a **resource pool** that is allocated differently depending on the routing regime.

- In a **dense** model, the pool is *fully allocated* every time. If the model is 70B params in FP16, we need 140 GB of weight memory available for every token. There is no "spending less" — the full 140 GB is the residency floor.
- In an **MoE** model, the pool is *fractionally allocated*. The total pool may be large (reflecting the model's capacity and training compute), but what we actually wire up per token is a slice. With top-2 routing from 8 experts, roughly 2/8 = 25% of the total parameter mass is active per token. This fraction saves compute (fewer FLOPs) but the attention layers still see every token, so the KV cache still grows with context length just as in a dense model.

The durable mental model: **total parameters set the ceiling; active parameters per token set the floor.** The architect must track both numbers.

## 3. Worked Example

We now carry concrete arithmetic using the canonical enterprise Q&A scenario (Ch 4, Table 4-2: ~2,000 users, ~10 rps average, ~40 rps peak, 1,200 + 8K context ~9.2K input, 300-token output, 70B-class model, FP16, 1 host 8×H100). The numbers below are worked out explicitly; where a model's exact spec is not first-party verified, it is flagged [UNRESOLVED].

### Dense 70B model (canonical teaching model, [canonical scenario][ASSUMPTION])

The 70B dense full-MHA model below is a *constructed teaching reference* (the canonical scenario, Ch 4 Table 4-2), not a named vendor model — so its geometry is [canonical scenario][ASSUMPTION] and its arithmetic is [canonical scenario][DERIVED]. Reserve [1P] for a named, traceable first-party model specification.

**Table 3-1 — Dense 70B model parameter arithmetic (worked example, not reference).**

| Metric | Value | Derivation |
|---|---|---|
| Total parameters | 70B | canonical scenario (Ch 4, Table 4-2) [canonical scenario][ASSUMPTION] reference model |
| FP16 residency (total) | 140 GB | 70B × 2 bytes = 140 GB [canonical scenario][DERIVED] |
| Active parameters per token | 70B | All parameters active for every token (dense) [canonical scenario][DERIVED] |
| FLOPs per forward pass (approx.) | ~0.14T | 70B × 2 FLOP/param (multiply-add = 2 FLOPs, Ch 8) [canonical scenario][DERIVED] |

### MoE model representative (Mixtral 8x7B class, [ILLUSTRATIVE][ASSUMPTION])

We contrast with a representative MoE model in the Mixtral lineage. The exact parameter split is not always published in vendor model cards; the numbers below are plausibility-checked and flagged.

**Table 3-2 — MoE model parameter arithmetic (worked example, not reference). The active fraction for top-2-of-8 routing is ~25–30% of total, not single-digit. Note the contrast with the 2026 frontier models in Appendix A, where active fractions do fall to a few percent (Qwen 6B/125B, Kimi 104B/2.8T) because those use extreme expert sparsity plus shared/offloadable parameters.**

| Metric | Value | Derivation |
|---|---|---|
| Total parameters (across 8 experts) | ~47B | ~5.7B per expert × 8 ≈ 45.6B + always-on attention/shared + embeddings ≈ 47B (per-expert rounded to ~6B) [ILLUSTRATIVE][DERIVED] |
| Active parameters per token (top-2 routing) | ~14B | 2 routed FFN experts + always-on attention/shared weights ≈ 14B (~30% of the ~47B total; ~25% counting expert-FFN mass alone) [ILLUSTRATIVE][DERIVED] |
| Active/total fraction | ~30% | 14B ÷ 47B ≈ 29.8% (≈25–30% for top-2-from-8) [ILLUSTRATIVE][DERIVED] |
| FP16 active weight-read per token | ~28 GB | 14B × 2 bytes = 28 GB read per token (compute/bandwidth; does NOT set residency) [ILLUSTRATIVE][DERIVED] |
| FLOPs per forward pass (approx.) | ~0.028T | 14B active × 2 FLOP/param = 28B [ILLUSTRATIVE][DERIVED] |
| Compute ratio vs dense 70B | ~0.20× (~5× less) | (14B × 2) ÷ (70B × 2) = 28 GFLOP ÷ 140 GFLOP [ILLUSTRATIVE][DERIVED] |

### Why MoE saves compute but not KV cache memory

The compute savings are straightforward: if only $n_a = 14$B of $n_t = 47$B total parameters are active per token, the FLOP count drops by the active fraction relative to a *same-size dense* model. But note the active fraction for top-2-of-8 routing is ~$14/47 \approx 30\%$, not single-digit — so the relative saving is about 5× versus the canonical 70B *dense* comparison, not 20× or 30×. Concretely,

$$
\text{FLOP}_{\text{MoE/token}} = n_a \times 2 \text{ FLOP/param} = 14\text{ B} \times 2 \approx 0.028\text{ T}
$$

which is $0.028/0.14 \approx 0.20\times$ of the dense 70B figure — roughly a **5× reduction** in compute per token. (It is also $14/47 \approx 30\%$ of a hypothetical dense model of the *same* 47B total; the 5× figure uses the book's canonical 70B dense as the comparison, so always state which baseline the ratio is against.)

The KV cache story is the surprising part. Recall from Chapter 1 (KV cache as a concept) that the KV cache stores one key and one value tensor per token, per layer. The cache size per token scales with the canonical Chapter 1 formula (the full-MHA case, where n_KV-heads × head_dim = hidden_dim; for a GQA/MQA model substitute n_KV-heads × head_dim), $KV_{\text{per-token}} = 2 \times n_\text{layers} \times d_\text{hidden} \times \text{bytes-per-value}$. Critically, **the attention mechanism processes every token in the context densely** — each token's query attends to all previous tokens' keys and values, regardless of whether the model is dense or MoE. MoE sparsity operates in the feed-forward sub-layer; it does not change the attention sub-layer's behavior.

Therefore, for a 70B-class model (dense or MoE) with 8K–9.2K input context:

- **Dense 70B**: KV cache ~1.31 MB per token × 9,200 tokens ≈ 12.06 GB (at 8-bit, the raw tensor byte-halving figure = 1.31 MB/token, exactly 50% of BF16 — the block-overhead and '54%' ITL-slope caveats are stated once in Ch 1; see Ch 7) or ~24 GB (at FP16 precision for the key/value storage pattern discussed in Ch. 7).
- **MoE 70B-equivalent**: The KV cache is *identical* in size, because attention still processes all 9,200 tokens densely. The fact that only 14B of 47B total parameters are active in the feed-forward layers does not reduce the number of keys/values emitted by the attention layers.

In other words: MoE sparsity = compute sparsity (fewer FLOPs per token). MoE sparsity ≠ memory sparsity (KV cache still grows linearly with context length, same as dense). Only changing the attention mechanism itself (e.g., hybrid/linear attention, compressed latent attention, or KV offload) can stop the cache from growing. This distinction — compute-sparsity versus memory-sparsity — is one an architect has to get exactly right.

> **Key takeaway:** MoE provides **compute sparsity** (far fewer FLOPs per token because a fraction of experts is active), not automatic **weight-residency sparsity** — the full expert set normally remains resident unless it is explicitly offloaded or sharded in a way that changes residency. And the KV cache budget must be provisioned as if the model were dense. Do not assume MoE reduces KV cache memory, and do not confuse active-compute savings with a residency saving. (This restates at the parameter level the sparsity lesson introduced conceptually in Ch 1 and developed arithmetically for the canonical model in Ch 7; each chapter teaches it at its own rung of the spine.)

> **Boxed rule — two distinct accounting lines.** Keep two numbers separate and never blur them:
> 1. **total parameters → weight residency.** The resident weights (all experts, for MoE) are what the GPUs must hold. For a 70B dense model this is ~140 GB FP16; for a ~47B MoE this is ~94 GB (full expert set) unless experts are explicitly offloaded.
> 2. **active parameters/token → approximate compute per token.** The routed top-k fraction (e.g. ~14B active) sets the FLOPs per token (~28 GB of active weights read per token). This is not a memory-freeing lever unless offloading is in play.

## 4. Measurement

How do we determine the total-versus-active split for a model we haven't trained?

1. **Model card inspection.** Most model vendors publish the total parameter count. The active-per-token count is harder to find; it requires reading the architecture documentation for the routing mechanism (top-k, top-1, importance-based). If the model card says "70B parameters" without qualification, assume dense unless it explicitly describes an MoE layout.

2. **Runtime measurement.** For a given input, profile the number of FLOPs or the memory footprint of active weights. Tools such as `torch.profiler` can count active parameters, but this is an empirical measurement, not a first-party spec.

3. **Architecture diagram.** For MoE models, the number of experts × parameters-per-expert gives the total; the routing hyperparameter (top-k) × parameters-per-expert gives the active per token. This is a derived fact from the source code/release, not always on the model card.

> **Practical habit:** When we encounter a model quoted in "X billion parameters," pause and ask: *is this total or active?* For dense models they are the same; for MoE models they diverge. Misreading this is the most common source of KV cache and compute underestimation.

## 5. Common Mistakes

- **Assuming total parameters = active parameters per token.** This is one of the costliest misreads. For a MoE model, the quoted "236B" or "47B" is the total across all experts; the active count per token is a fraction. The two counts drive *different* budgets: the **total** count sets **weight residency** (the full expert set must be resident — 236B × 2 bytes, not just the active footprint), while the **active** count sets **compute per token** (only the routed experts are read). Sizing *weight memory* from the active count under-provisions it (the un-routed experts still occupy HBM); sizing *compute* from the total count over-provisions it (the un-routed experts are not read per token). The opposite error — sizing for active parameters while forgetting the KV cache is dense — under-provisions the KV budget.

- **Confusing compute sparsity with memory sparsity.** MoE reduces FLOPs per token because fewer parameters are active. It does *not* reduce the number of keys/values written to the KV cache. An architect who assumes MoE shrinks KV cache will be blindsided by memory pressure at long context lengths.

- **Using MoE as a free lunch for long-context workloads.** The compute savings from MoE are real, but the memory cost (weights + KV cache) must be provisioned at the total-parameter scale for weight residency and at the-full-context scale for KV cache. Neither benefit is "free" in the other domain.

- **Ignoring routing overhead.** Top-k routing itself requires computing routing scores (a softmax over expert assignments). This adds a small but non-zero compute cost that is sometimes omitted from published FLOP counts. It is usually negligible compared to the feed-forward arithmetic but should be acknowledged.

## 6. Architecture Consequence

Knowing whether a model is dense or MoE, and whether the quoted parameter count is total or active, directly changes three architectural decisions:

1. **Weight residency budget.** For a dense 70B model, provision 140 GB of FP16 weight memory per host. For an MoE model with ~47B total and ~14B active, distinguish two numbers: the **resident** budget (the full expert set, ~47B × 2 bytes ≈ 94 GB, unless experts are offloaded/swapped) and the **active per-token** footprint (~14B × 2 bytes ≈ 28 GB read per token). The active number governs compute; the resident number governs whether the weights stay on device. MoE therefore does not automatically lower the weight-residency floor — it only gives the *option* to offload inactives at the cost of bandwidth.

2. **KV cache provisioning.** Provision the KV cache as for a dense model of the same context length and hidden dimension. Do not apply a MoE sparsity factor to the KV cache. If we are running a 9.2K-token input on a 70B-class model (dense or MoE), the KV cache memory is the same order of magnitude — plan accordingly.

3. **Parallelism and routing strategy.** MoE deployment requires a routing strategy (e.g., expert placement, dispatcher, switchboard) and often expert parallelism across GPUs. This adds infrastructure complexity (cross-GPU communication for expert routing) that dense models do not have. The architectural choice between dense and MoE is therefore not just a parameter-count decision; it is a deployment-complexity decision.

### The 2026 baseline shift: same framework, new constants

**The 2026 trend signal (forward-looking; an interpretation of the sample we surveyed, not an established industry-wide convergence).** By August 2026 the four frontier open-weight families surveyed for this edition share a notable pattern, and it is not more of the same dense scaling: extreme MoE sparsity (single-digit active-parameter fractions — Qwen 6B of 125B, Kimi K3 104B of 2.8T) coupled with **hybrid attention** (compressed/sparse/linear hybrids such as Gated DeltaNet + sparse attention) has become a common way to make long-context inference affordable. Appendix A documents these at full depth with first-party provenance; what matters here, in the model-understanding chapter, is that this is not a competing mechanism but the *same* dense-vs-MoE, total-vs-active, KV-vs-compute machinery this chapter just taught — with new constants. We hold that view explicitly as the **forward-looking direction** the architect should size toward, and flag it below as continuing future work (the frontier moves; this handbook is a living document, and Appendix A is where the moving part lives).

**Why the trend signal should not be read as "dense is dead".** This pattern among the four frontier families we surveyed describes the top of the market — the ~100B-and-up tier that anchor ~2.8T-parameter fleets. It is not a claim that dense models have disappeared. On the contrary, the smaller, denser tier is alive and actively shipping in 2026 for exactly the constrained-deployment reasons this chapter teaches: **Qwen3.8-27B** ([1P][FACT], source: HF Qwen/Qwen3.8-27B) is a dense 27.8B model whose 4-bit weights fit on a single 24 GB consumer GPU, and **Muse Glimmer 30B** ([1P][FACT], source: Meta via vLLM-Recipes) is a dense 29.6B local-agentic model that runs in ~18 GB. These exist because the dense-vs-MoE trade is itself a *deployment* decision, not a date: MoE buys active-parameter efficiency at the cost of total-parameter memory and routing complexity — worthwhile when serving many requests from a large pool of resident weights, but hard to justify when the whole budget is one consumer GPU whose total weights already overrun. That is precisely why this book keeps its canonical on the dense tier: the canonical must serve the architect whose *whole fleet* is a handful of boxes, not only the one sizing a 2.8T datacenter model. The framework does not change between tiers — total vs active, KV per-token, and residency budgeting apply identically to a 27B dense laptop model and a 125B/6B MoE fleet model.

**Why the rest of this chapter's canonical stays a dense full-MHA model.** If the trend is MoE + hybrid, why does this book's canonical still size a dense 70B full-MHA workload? Because a dense model with full multi-head attention gives the cleanest single-constant KV formula (`2 × layers × hidden × bytes`) and the largest KV footprint — the conservative worst case an architect should always size against first. Teaching against that bound means the reader learns the framework on the hardest memory case and then relaxes it. It is a deliberate teaching simplification, not a claim that in 2026 an enterprise RAG fleet really runs on dense 70B.

**One verified 2026 transfer: Qwen3.8-Flash-Next.** The model card [1P][FACT] (source: HF Qwen/Qwen3.8-Flash-Next) is the Qwen4-architecture preview: **125B total / 6B active** (plus a separate 51B of offloadable N-gram embedding parameters), **512 MoE experts** (10 routed + 1 shared per token), and **hybrid attention** — Gated DeltaNet (GDN) on three of every four layers plus Qwen Sparse Attention (QSA) on the fourth. This is exactly the "125B/6B active MoE + Gated DeltaNet/QSA" class of model a 2026 architect actually considers. Stepping through this book's own arithmetic:

- **Weight residency** (Ch. 7's floor): the active-weight working set for Qwen is ~6 × 10⁹ params × 2 bytes/param = ~12 GB read per token, not the canonical 140 GB — MoE sparsity reduced the per-token weight traffic by ~12×. But this is a *compute/bandwidth* statement, not a residency one: the total weights dominate the memory ceiling, ~125 × 10⁹ params × 2 bytes/param ≈ 250 GB (plus the offloadable N-gram). So the *total-vs-active* split of this chapter is not a footnote — it is the difference between fitting on one host and sharding across several, and the ~250 GB total (not the ~12 GB active working set) is what must be resident unless experts are explicitly offloaded.
- **KV cache** (Ch. 7/8): the canonical `2 × layers × hidden × bytes` KV formula is the full-MHA bound. Qwen's hybrid attention attacks the KV constant itself at the mechanism level — GDN keeps a fixed-size recurrent state (context cost no longer grows linearly per token across those layers) and QSA attends sparsely at micro-block granularity — so per-token KV no longer follows the dense formula. The framework question ("does it fit?") is unchanged; the *function* plugged in for KV is not the dense one.
- **Compute** (Ch. 8): active-parameter FLOPs drop to ~2 ×6B per token, but the QSA/GDN layers ride different roofline points than a dense 70B prefill/decode split, so the throttled-resource conclusion must be re-derived per model (Ch. 8's measurement discipline, not a one-time number).

**The architect's move is unchanged.** For the canonical dense model this book sizes memory, compute, and fleet with one clean constant set. For a 2026 MoE/hybrid model the architect does the *same* decision loop — read the model card, get total vs active, get the KV scheme's per-token function, size residency and roofline, then decide parallelism (Ch. 10) and serving (Ch. 11). Only the constants differ; the framework does not. Appendix A walks the four frontier models through exactly this re-derivation and flags which vendor numbers still carry a verify-on-own-hardware caveat.

> **Recorded as future work.** This forward-looking view is intentionally a *pointer*, not the full treatment — the complete, current analysis of the 2026 frontier lives in Appendix A. Because the frontier moves quickly and every vendor figure in it carries a verify-on-own-hardware caveat, we treat the trend as a living section to be updated against new model cards, rather than a set of frozen gospel numbers. An architect should re-check Appendix A before any capacity decision — the constants, not the framework, are what change.

## 7. What We Still Don't Know

As of 2026-08, several questions remain open and are flagged [UNRESOLVED]:

- **Exact active-fraction per token for commercial MoE models.** Model cards rarely publish the precise top-k routing distribution under real workloads. We know the architectural top-k (e.g., top-2 from 8 experts), but the actual fraction of active parameters may vary with prompt content, token position, and expert availability.
- **Whether router latency offsets MoE compute savings.** The cost of computing routing scores and dispatching to experts is not always included in published FLOP counts. On some hardware the routing overhead can be significant enough to narrow the compute gap between MoE and dense.
- **KV cache behavior under MoE with expert swapping.** When experts do not fit on a single GPU and must be swapped (offloaded), does the KV cache interact with the swapping mechanism in ways that change its effective size or access pattern? This has not been systematically characterized.

These flags exist because home-lab measurements are not reference per the evidence taxonomy; each is an open empirical question a team should validate against its own target workload, not a claim the handbook has settled.

## 8. End-of-Chapter Mini-Case: Total vs. Active Parameters, and the KV Constant

*(Continuous scenario — chained from the enterprise Q&A thread.)*

An architect is fleshing out the design of the internal Q&A tool described in Chapter 1's mini-case. The team's standing decision from Chapter 2 is the dense 70B model; a MoE model with 8 experts (roughly 47B total params, ~14B active per token) is the challenger under consideration. They ask: "If we go MoE, can we cut our GPU memory budget?"

From the model-understanding chapter, the architect can answer: Active-compute memory yes — only ~14B of the ~47B total is active per token, so ~28 GB of *active* weight footprint is read per token vs. 140 GB for a dense 70B. But *resident* memory is a different question. An MoE model normally keeps its **full expert set resident** — the non-active experts still occupy HBM unless we explicitly use expert offload/swapping (Ch 3 §3.6, Ch. 18), which itself costs bandwidth. So MoE reduces compute per token, and it gives us the *option* to offload some experts to shrink residency, but it does **not** automatically reduce the weight-residency floor. And KV cache memory no — the attention layers still process every token densely, so the cache budget for a 9.2K-context input is the same regardless of whether the model is dense or MoE. We still need to provision for ~12 GB of KV cache (at 8-bit) or ~24 GB (at the precision pattern discussed in Ch. 7) per request, and we'll also need expert-routing infrastructure on top of that.

The architect's decision therefore hinges on whether the compute savings from MoE (fewer FLOPs per token, potentially lower \$/token) outweigh the added routing complexity and the fact that KV cache memory is unchanged. On that accounting the MoE challenger fails: it does not cut the memory budget the team asked about, and it would add routing infrastructure — including a GPU dedicated to the routing dispatcher [ILLUSTRATIVE][ASSUMPTION], not a vendor-published requirement — on top. The team therefore keeps the Chapter 2 decision, the dense 70B model, and provisions the KV cache budget at the dense-model rate.

* * *
![Fig 3.1 — Dense vs MoE parameter allocation and KV cache behavior. Controlled comparison: same attention geometry, same context and cache dtype — so the KV footprint is identical — while weight residency (140 GB dense vs ~94 GB for the ~47B MoE challenger) and the active-compute fraction (~100% vs ~30%) both differ. Schematic, not to scale. An MoE model that also uses GQA or a different attention mechanism is a different comparison (Ch. 7). [ILLUSTRATIVE][DERIVED]](figures/fig-03-0301.png)

*Parameter-activation contrast. A dense 70B activates all 70B parameters per token (residency ≈ 140 GB, KV grows linearly with context). An 8-expert MoE still stores its full expert set as resident weights (not shown to scale), but only the top-2 (~14B) are active per token (active compute footprint ≈ 28 GB). KV cache growth with context is identical to dense — attention still processes every token.*

\needspace{11\baselineskip}

**Table 3-3** — Parameter and KV cache arithmetic: dense 70B vs MoE (8×7B class)

| metric | dense 70B | MoE (8×7B class) | derivation |
|---|---|---|---|
| total parameters | 70B | ~47B | [ILLUSTRATIVE][ASSUMPTION] expert split |
| active params per token | 70B | ~14B | top-2 from 8 ≈ 2/8 = 25% of expert mass [ILLUSTRATIVE][DERIVED] |
| active/total fraction | 100% | ~30% | 14B ÷ 47B ≈ 29.8% [ILLUSTRATIVE][DERIVED] |
| FP16 residency (total) | 140 GB | ~94 GB | 70B × 2 / 47B × 2 |
| FP16 weight-read per token | 140 GB | ~28 GB | 70B × 2 / 14B × 2 (read per token, not residency) |
| KV cache per request (9.2K ctx, 8-bit) | ~12 GB | ~12 GB | identical — attention dense |
| FLOPs per forward pass | ~0.14T | ~0.028T | 70B × 2 / 14B × 2 |
| compute ratio vs dense 70B | 1× | ~0.20× (~5× less) | (14B × 2) ÷ (70B × 2) = 28B ÷ 140B [ILLUSTRATIVE][DERIVED] |

*All figures trace to the canonical scenario (Ch 4, Table 4-2); the MoE column is an [ILLUSTRATIVE][ASSUMPTION] worked variant, not a measurement claim.*

---
*Next chapter: Chapter 4 — The Anatomy of an AI Workload, which characterizes the enterprise Q&A RAG workload across the six dimensions (quality, traffic, token profile, latency, economic, operational constraints) and uses the same continuous mini-case scenario.*

*Canonical scenario citation: all numerical values in this chapter that trace to the canonical enterprise Q&A RAG workload are drawn from the fixed reference set in Ch 4 (Table 4-2). The dense 70B numbers carry [canonical scenario] provenance with the per-row [ASSUMPTION]/[DERIVED] split; MoE numbers carry [ILLUSTRATIVE] provenance with the same split — plausibility-checked variants.*