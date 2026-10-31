# Chapter 7 — Memory Is the First Constraint

## The Architect's Question

After this chapter we should be able to answer the architect's fundamental constraint question: *does the model and its context fit in the memory floor before we ask whether it can compute or communicate?* We will build the arithmetic for the KV cache from first principles, reconcile it with the canonical ~1.3 MB/token figure from Chapter 1, and contrast inference residency (weights + KV) with fine-tuning residency (weights + gradients + optimizer states). The goal is to make "does it fit?" a concrete, quantified check — not a back-of-the-envelope guess. Throughout, the arithmetic anchors to the canonical enterprise-Q&A RAG scenario (Ch 4, Table 4-2): ~10 rps average / ~40 rps peak traffic served by a 70B **FP16** model on an 8×H100 host. KV cache per-token figures are given at the referenced precision throughout: ~1.3 MB/token at **8-bit** (this is Chapter 1's reference figure), ~2.62 MB/token (exactly 2.5 MiB/token) at **FP16** — and the canonical scenario's KV constant is the **FP16** 2.62 MB/token figure, not the 8-bit ~1.3 MB/token number.

## 1. Concept

Memory is the first constraint because every LLM workload begins with a residency check: can the model and its active data structures be placed on the target hardware? The KV cache is the primary expression of this constraint during inference: it grows linearly with context length, and its size depends on the model's layer count, hidden dimension, and the precision chosen for key and value storage. Unlike FLOPs, which scale with operations per token, the KV cache occupies memory continuously for the lifetime of a request — it is always resident, always consuming HBM bandwidth for every re-read. The architect must therefore size two distinct memory loads: the static weight footprint and the dynamic KV footprint that varies with prompt length. Quantization (FP8, FP4, 2-bit asymmetric) reduces both, but the KV cache is the one component whose reduction must be quoted per precision, not as a uniform factor: FP8 KV realizes ~50% in serving today (raw byte-halving), while 4-bit KV's raw bound is a full 4× (2.62 → 0.66 MB/token at this chapter's geometry) — realized savings land between, once per-block scale/offset metadata and per-token variation are counted — rather than the single 2×–4× that weight-only quantization applies to weights. The residency floor is therefore set by weights + KV (+ activations, in fine-tuning), and the architect's first question is whether this sum fits on the target GPUs. This is why "does it fit?" is the architect's primary gate: before we ask whether the model can compute or communicate, we must first establish that the working set — weights plus the context-dependent KV state — resides on-GPU. If it does not, every subsequent decision (offload, recompute, page) is a degradation, not a cost-optimization.

The residency floor has two distinct regimes. For inference, the floor is weights + KV: the model's static parameters plus the context-dependent key/value tensors that grow with every token added to the prompt. In fine-tuning, the floor rises further to weights + gradients + optimizer states, because every parameter update requires its own momentum and velocity vectors (Adam) or per-parameter scaling (LAMB/RMSProp). The contrast between these two floors — inference ~164.1 GB for a 70B model at FP16 with 9.2K input (140 + 24.1; the 9.5K-max is 164.9 ≈ 165 GB) [canonical scenario][DERIVED], fine-tuning exceeding 1 TB [canonical scenario][DERIVED] — is the architect's central memory-takeaway.

We keep two terms rigidly distinct in this chapter, and the distinction is the antidote to "does it fit?" mistakes:

- **Residency floor** = weights + KV. This is the minimum memory the model's parameters and active KV tensors must *occupy* for a single request. It is what the numbers in this chapter quote (~140 GB weights + ~24.9 GB KV ≈ 165 GB at 9.5K max).
- **Practical host requirement** = weights + KV + runtime/workspace + safety margin. Deploying a model on a GPU requires additional VRAM for CUDA kernels, activation buffers, NCCL (NVIDIA Collective Communications Library) communication, a warmup/KV-allocation safety pool, and (on a multi-GPU host) tensor- or pipeline-parallel copies. On the canonical 8×H100 host this runtime/workspace term is ~64 GB, turning the ~165 GB residency floor into a larger *deployment* footprint. [ILLUSTRATIVE][ASSUMPTION] The ~64 GB is a planning reserve, not a measured constant; a representative split is ~8 GB CUDA context/driver + ~16 GB activation buffers (batch + intermediate tensors) + ~8 GB NCCL communication buffers (tensor-parallel all-reduce staging) + ~32 GB warmup/KV-allocation safety pool. The exact value must come from a deployment benchmark on the target stack (Chapter 14); the 436 GB KV budget (640 − 140 − 64) shifts by the same amount if the measured reserve differs.

When the text says a workload "fits" or "does not fit," we are always talking about the residency floor first; the practical host requirement is a superset that must be checked before committing hardware. Conflating the two is exactly what produces a "165 GB fits in 160 GB" error.

### Count state by lifetime, not by the model label

The weights-plus-KV floor in this chapter describes the autoregressive baseline. A diffusion language runtime needs a state-lifetime inventory before the same capacity calculation can be applied. We distinguish resident weights, reusable context state, mutable canvas state, peak activations and logits, kernel workspace, and runtime allocations. These categories must be disjoint at the instant being measured; two names for the same buffer do not create two memory costs. [DERIVED]

The KV tensor byte formula remains valid for actual K/V tensors. What changes is the proof that those tensors can be reused: Chapter 3's dependency figure shows why unchanged token IDs are insufficient under bidirectional refinement. A block-causal boundary can make an earlier prefix immutable. Approximate cache policies instead trade refresh work against quality. Memory capacity and cache validity are separate checks. [1P][FACT]

Repeated sequential evaluations need not multiply peak memory by the number of rounds when inference releases temporary buffers after each round. Retained histories, previous-round logits for self-conditioning, or simultaneous verification views change that lifetime calculation. As a shape-only example, a 256-position canvas over a 262,144-entry vocabulary needs 256 × 262,144 × 4 = 268,435,456 bytes, or 256 MiB, for one FP32 logits tensor at batch one. This excludes probabilities, sampling workspace, retained logits, attention buffers and the rest of the model. It is not a measured model footprint. [ILLUSTRATIVE][ASSUMPTION][DERIVED]

This distinction affects admission control. A runtime may have enough capacity for prefix state yet fail when many requests enter a high-workspace refinement phase together. Weight precision alone cannot certify fit: the inspected LLaDA sampling code (observation 2026-10-28; [LLaDA generation code](https://github.com/ML-GSAI/LLaDA)) can use FP64 sampling intermediates even when the network weights use a lower precision. The deployed sampler's live tensor shapes and lifetimes decide the practical requirement. [1P][FACT] for the inspected code; the admission consequence is [DERIVED].

None of this changes the canonical autoregressive budget above — it changes what must be inventoried before that budget's arithmetic is reused for a different generation mechanism.

## 2. Mental Model

The KV cache is **per-request state that persists across autoregressive decode steps for the lifetime of the active sequence** — unlike weights, which are loaded once and reused across requests, the KV cache is allocated per request and grows with every token added to the context. A 9.2K prompt on a 70B model at FP16 carries ~24 GB of KV state that must remain on-GPU for the entire prefill + decode sequence. If it does not fit, the serving stack must page, offload, or recompute — each option degrades latency or throughput. The durable mental model is: *every token we add to the context exacts a fixed memory toll, and that toll is paid in HBM every time the GPU re-reads the cache during decode.* This is why context length is the single most powerful lever on inference memory pressure, and why "does it fit?" is the architect's primary gate.

### Persistent state is architecture-specific

The KV formula in this chapter describes keys and values retained across autoregressive steps. A whole-clip denoiser has a different lifetime model. Its latent video changes after each scheduler update, so video keys and values cannot simply be retained as immutable prefix entries for every later step. The inspected Wan2.2 path recomputes attention from the current clip representation (observation 2026-10-28; [Wan2.2 sampling loop](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/textimage2video.py), [attention defaults `causal=False`, `window_size=(-1,-1)`](https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/modules/attention.py)). Static prompt embeddings can remain reusable, but that is not the growing autoregressive cache. [1P][FACT]

The corresponding fit test includes resident weights and encoders, latent and scheduler state, per-layer activations, attention workspace, temporary conversion buffers, and VAE reconstruction. The peak is the maximum of the live allocations at each stage, not the sum of all tensors ever created. Tiled or chunked reconstruction can reduce a decoder peak without reducing the denoiser's token count. CPU offload can reduce GPU residency while adding host-memory and transfer requirements. A model that loads successfully has not yet passed the largest-shape inference test. [1P][FACT] for the documented implementation mechanisms; the budget interpretation is [ILLUSTRATIVE][DERIVED].

The canonical KV table below is untouched: it prices the autoregressive text path this chapter sizes. The boundary changes which state function we plug into "does it fit?" for a different generator — the same decision, a different inventory.

## 3. Worked Example

We anchor all arithmetic in the canonical scenario (Ch 4, Table 4-2): a **canonical 80-layer, hidden-8192, full-MHA 70B reference model** (every query head carries its own K,V, so the per-token KV width equals the model's hidden dimension), FP16 weights (2 bytes per parameter), 8 ×GPUs (80 GB each, 640 GB total VRAM), ~9.2K input tokens + 300 output tokens. We compute KV cache size per token, total KV for the canonical context, and contrast with long-context variants. The per-token formula is general — KV/token = 2 × layers × n_KV-heads × head_dim × bytes — and the full-MHA special case (n_KV-heads × head_dim = hidden_dim) gives the ~2.62 MB/token conservative baseline used throughout; a grouped-query attention (GQA) model would use a much smaller constant (see the sensitivity note, below).

**Table 7-1** — KV cache size per token and per-context arithmetic for the canonical 80-layer, hidden-8192, **full-MHA 70B reference** at FP16. *(The 9.2K/9.5K per-context totals, residency figures, and fit/non-fit verdicts below are [canonical scenario][DERIVED] from the general per-token formula `2 × layers × n_KV-heads × head_dim × bytes` (MHA case here); the 32K/128K rows are non-canonical what-if variants [ILLUSTRATIVE][DERIVED]. The 70B reference is a constructed teaching geometry, not a named vendor model, so it carries no model-card provenance.)*

| metric | value | derivation |
|---|---|---|
| layers | 80 | canonical 70B full-MHA teaching model [canonical scenario][ASSUMPTION] |
| hidden_dim | 8192 | canonical 70B full-MHA teaching model [canonical scenario][ASSUMPTION] |
| bytes per parameter (FP16) | 2 | FP16 = 2 bytes/param [1P: IEEE 754 binary16] |
| KV cache per token per layer | 2 × hidden_dim × bytes | one key + one value per layer |
| KV cache per token (FP16) | 2 ×80 ×8192 ×2 B ≈ 2.62 MB | = 2,560 KB = 2.5 MiB; exact decimal 2.62 MB |
| KV cache per token (8-bit) | 2 ×80 ×8192 ×1 B ≈ 1.3 MB | = 1,310,720 B = 1.25 MiB; reconciles with Ch.1 |
| KV cache per token (FP8) | 1.31 MB | = 1,310,720 B = 1.25 MiB; raw tensor byte-halving, exactly 50% of BF16; any block-layout/scale-offset metadata overhead is NOT vendor-measured (see §7.4) |
| 9.2K input KV cache (initial) | 9,200 ×2.62 MB ≈ 24.1 GB | 9,200 ×2,621,440 B; initial KV residency |
| 300 output KV cache | 300 ×2.62 MB ≈ 0.8 GB | 300 ×2,621,440 B |
| total inference KV (9.5K max) | ≈ 24.9 GB | 9,500 × 2,621,440 B ≈ 24.9 GB |
| 32K input KV cache | 32,000 ×2.62 MB ≈ 83.9 GB | 32,000 ×2,621,440 B; long-context variant |
| 128K input KV cache | 128,000 ×2.62 MB ≈ 335.5 GB | 128,000 ×2,621,440 B; aggressive long-context variant |
| 70B FP16 weights | 70B × 2 B = 140 GB | [canonical scenario][DERIVED from 70B × 2 bytes] |
| inference residency (weights + KV, 9.5K max) | ≈ 165 GB | 140 + 24.9 GB |
| inference residency (weights + KV, 32K) | ≈ 224 GB | 140 + 83.9 GB |
| inference residency (weights + KV, 128K) | ≈ 475 GB | 140 + 335.5 GB |
| 2×H100 total VRAM | 2 ×80 GB = 160 GB | [1P: NVIDIA H100 spec] |
| 8×H100 total VRAM | 8 ×80 GB = 640 GB | [1P: NVIDIA H100 spec] |
| 3×H100 total VRAM | 3 ×80 GB = 240 GB | [DERIVED] 165 GB < 240 GB |
| fits 2×H100 at 9.2K? | no, 164.1 GB > 160 GB | does not fit in 2×H100; needs ≥3×H100 by aggregate capacity (or lower precision / more GPUs) |
| fits 8×H100 at 9.2K? | yes | 164.1 GB < 640 GB |
| fits 3×H100 at 9.2K? | yes | 164.1 GB < 240 GB |
| fits 8×H100 at 32K? | yes | 224.0 GB < 640 GB |
| fits 8×H100 at 128K? | yes, barely | 475.5 GB < 640 GB |
| fits 1×H100 at 9.2K? | no | 164.1 GB > 80 GB; needs ≥3×H100 by aggregate capacity |

*Note on “does it fit?”: this residency check answers a single-request question — does ONE request’s weights + KV fit in the pool? It says nothing yet about how many such requests fit concurrently. For that, an architect must subtract the runtime/activation/workspace floor (~64 GB on the 8×H100 host) from the 640 GB pool before sizing KV. We compute that concurrent capacity — the ~436 GB KV budget and ~17.5 requests/host (byte-accurate 17.51; conservative integer floor 17) — in Chapter 17. Keep the two numbers separate: the ~500 GB headroom (Ch. 4/7, single-request) and the ~436 GB KV budget (Ch. 17, concurrency) answer different questions.*

*Attention-family sensitivity note.* The ~2.62 MB/token (2.5 MiB) figure is the **full-MHA** (multi-head attention) upper bound: n_KV-heads = n_query-heads, and n_KV-heads × head_dim = hidden_dim, i.e.

$$
KV_{\text{MHA per-token}} = 2 \times n_\text{layers} \times d_\text{hidden} \times B
$$

Real 70B-class dense models commonly use **grouped-query attention (GQA)**: LLaMA-2 70B, for instance, has 64 query heads but only 8 KV heads, so per-token KV shrinks by the head ratio to

$$
KV_{\text{GQA per-token}} = 2 \times n_\text{layers} \times n_\text{KV-heads} \times d_\text{head} \times B = 2 \times 80 \times (8 \times 128) \times 2 \text{ B} \approx 0.33 \text{ MB/token}
$$

— about **8× smaller**. For the canonical 9.2K context that is ~3 GB of KV instead of ~24 GB, and the fleet-sizing arithmetic of Chapter 17 changes accordingly (many more concurrent requests fit for KV). We keep the full-MHA bound as the canonical conservative residual because an architect should size against the worst case the *chosen* model actually presents — the honest move is to read the model card’s KV-head count and substitute it into the GQA formula above. The framework is unchanged; only the constant changes. (`kv_gqa_variant_mb` is recorded in `canonical-workload.yaml`.)

![Fig 7.1 — Grouped-Query Attention cuts per-token KV. The head glyphs are schematic; the load-bearing number is the **n_q : n_kv ratio (8 : 1 here)** — 8 query heads share one K/V head, so the per-token KV falls ~8× (the full arithmetic is in the text below). [ILLUSTRATIVE][DERIVED]](figures/fig-07-0703.png)

The figure shows one group's geometry: **8 query heads funnel into a single shared K/V head.** Because GQA caches only one K/V per group (8 K/V per token) instead of one per query head (64 K/V per token), the per-token KV falls ~8× — from ~2.62 MB/token (full MHA) to ~0.33 MB/token. That is the takeaway: many query heads can share a few K/V heads, and the cache shrinks by exactly the 8:1 head ratio. Head count is the real dial: substitute the model's KV-head count into `2 × layers × KV_heads × head_dim × bytes`.

### A smaller-model counterexample: fit is a gate, not a prediction

An illustrative 8-billion-parameter model stored entirely in FP16 has raw weights of 16 GB. Assume 32 attention layers, eight KV heads per layer, a head dimension of 128 and two bytes per KV element. This is a separate GQA example, not the handbook's canonical 70B attention layout, and none of its constants feed the canonical tables in this chapter. The KV storage per resident token is 2 × 32 × 8 × 128 × 2 = 131,072 bytes.

At 9,500 resident tokens, one sequence needs 1.245184 GB of raw KV. With an explicitly assumed 4 GB reserve for runtime state and workspace, the analytical budget is 21.245184 GB. A nominal 24 GB device passes this preliminary capacity gate. It does not yet pass an allocation or serving test. The reserve is an assumption, and the calculation excludes unmodeled conversion peaks, fragmentation and additional sequences. [ILLUSTRATIVE][DERIVED]

The counterexample is equally important. Ideal four-bit storage for 70 billion weights is already 35 GB before scales, alignment, unquantized layers, KV or workspace. Neither a 24 GB nor a 32 GB card holds that unsharded tensor. Two 24 GB cards provide 48 GB in total, but a working placement still needs supported sharding and a feasible budget on each rank. Shared client memory adds another constraint: the installed system capacity must also serve the operating system and other devices. It is not a guaranteed GPU allocation. Device capacities are first-party specifications ([Intel Arc Pro B70 datasheet](https://intel.com/content/dam/www/central-libraries/us/en/documents/2026-03/datasheet-b70-gpu.pdf), [B65 datasheet](https://intel.com/content/dam/www/central-libraries/us/en/documents/2026-03/datasheet-b65-gpu.pdf), [Arc Pro B60 datasheet](https://download.intel.com/newsroom/2025/client-computing/Intel-Arc-Pro-B60-Data-Sheet.pdf), retrieved 2026-10-28); the 35 GB figure is [ILLUSTRATIVE][DERIVED] from them.

Capacity and bandwidth answer different questions. Reading the illustrative 16 GB of weights once at the B60's nominal 456 GB/s takes at least about 35.1 ms in a simple weights-only streaming model; at the B70/B65 nominal 608 GB/s the corresponding value is about 26.3 ms. These are analytical byte-transfer floors, not measured token latencies. They ignore attention, KV traffic, launch overhead and communication, and they assume the nominal bandwidth is achieved. Batching or reuse can also change the bytes moved per output token. Passing the capacity gate therefore justifies a measurement, not a throughput or cost claim. [ILLUSTRATIVE][DERIVED]

### A dense model with a mixed history-state budget

The history budget has two terms, and the second one is not a KV cache. Each recurrent update replaces a fixed-shape summary of previous tokens, while a separate attention layer retains token-indexed keys and values. The states below are shown at successive times; the recurrent snapshots are not all retained together. The schematic does not claim that every operation within the model has constant memory or constant execution time.

![Fig 7.2 — History recurrence and attention history have different lifetimes: a recurrent layer group updates bounded, fixed-shape state, while a separate full-attention layer group retains growing KV history. Three token positions are schematic; recurrent snapshots are successive, not jointly retained. Configuration-backed example (Qwen3.8-27B), not a measured memory ratio.](figures/fig-07-0706-history-state.png)

The full-attention component of [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) illustrates the transfer from a configuration to a memory estimate. Its language configuration has 16 full-attention layers, four KV heads per layer, and a head dimension of 256 ([released configuration](https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/config.json), retrieved 2026-10-28). With BF16 KV storage, the raw component is:

`2 × 16 × 4 × 256 × 2 = 65,536 bytes per cached token.`

At 262,144 cached tokens, this component occupies 16 GiB. This analytical result assumes one sequence and unsharded raw tensors. It excludes the recurrent and convolution states of the other 48 language layers, visual processing, runtime buffers, and allocation overhead. It is neither the complete request footprint nor a measured concurrency limit. [1P][FACT] for the configuration; [DERIVED] for the storage.

At 131,072 tokens the same component is 8 GiB. Doubling history therefore adds 8 GiB to this component under the stated assumptions; it does not double every memory object in the request. In notation, the simplified history budget is `M_history(L) = L × 65,536 bytes + M_recurrent`, where `M_recurrent` covers fixed-shape recurrent and convolution state for this decode path. Temporary prefill workspaces remain outside that expression. These are derived storage estimates, not measured allocations. [DERIVED]

The serving consequence follows from the state lifetimes. Capacity planning needs both terms, including any replication or sharding imposed by the engine. A prefix checkpoint for an intermediate position must preserve the time-recurrent state corresponding to that position, not merely a list of attention pages. A preempted or branched request can require additional snapshots, and speculative rollback needs the correct pre-draft state. Bounded live decode state therefore does not imply free checkpointing or unrestricted prefix sharing; the implementation determines which extra copies are retained. [DERIVED]

Recurrence across depth is a separate cache problem. Huginn revisits a recurrent block within one token's execution, and its model card requires `HuginnDynamicCache` so later block calls do not overwrite earlier iterations' K/V ([Huginn model card, KV-cache Details](https://huggingface.co/tomg-group-umd/huginn-0125/raw/main/README.md), [recurrent-depth paper](https://arxiv.org/abs/2502.05171)). That iteration-aware attention cache does not establish a bounded time-recurrent state footprint. Its own retention or sharing policy belongs in the resource budget. [1P][FACT] for the card; [DERIVED] for the accounting distinction.

Less history traffic can relax one memory bottleneck without removing the weight-read or compute bottleneck. A recurrent token mixer and a full-attention layer also expose different prefill execution opportunities. Their kernel mix and sequence-length dependence must be measured separately before transferring a decode-state estimate into a throughput forecast. The architectural decision is which state representation the engine can maintain correctly at the required concurrency, not which family label sounds smaller.

The original memory-fit decision remains; the state function inserted into that decision changes. A full-MHA comparison is meaningful only under its stated geometry and precision, and it is not a universal upper bound for arbitrary recurrent-depth execution. This is a different model's configuration carried as its own assumptions — the canonical 80-layer, hidden-8192, full-MHA numbers in this chapter are unchanged by it.

\needspace{9\baselineskip}

**Table 7-2** — Inference residency vs. fine-tuning residency contrast for the canonical 80-layer, hidden-8192, full-MHA 70B reference model.

| scenario | memory resident | bytes per param | total (70B) | fits 8×H100 |
|---|---|---|---|---|
| inference (weights + KV, 9.2K input) | weights + KV cache | FP16: 2 B; KV adds ~2.62 MB/token | ~164.1 GB (9.2K; 140 + 24.1) | yes |
| fine-tuning (weights + gradients + optimizer) | weights + gradients + optimizer states | Adam: ~16 B/param (m + v + ΔW) | ~1,120 GB | no |
| fine-tuning (weights + gradients, FP16) | weights + gradients FP16 | 4 B/param (weights FP16 2 B + gradients FP16 2 B) | ~280 GB | yes |
| fine-tuning (QLoRA, 4-bit base + LoRA) | quantized base + LoRA adapters | NF4: nominal 4-bit (~0.5 B/param) + quantization metadata; adds adapters/gradients/optimizer/activations | ~50–70 GB | yes |
| inference with FP8 KV | weights FP16 + KV FP8 | KV: ~50% of BF16 (raw byte-halving) | ~152 GB (9.5K; 140 + 12.45; KV alone 12.45 GB) | yes |

*Inference residency = weights + KV cache; the KV footprint scales with context length. Fine-tuning residency adds optimizer states (Adam m, v, and master weights), which for 70B at ~16 bytes/param totals ~1,120 GB — roughly 1.75× the 640 GB of 8×H100. This contrast is the architect's central takeaway: inference is memory-limited by weights + KV, while fine-tuning is memory-limited by weights + gradients + optimizer, a substantially higher floor. Note the ~1,120 GB is the **parameter/optimizer floor** (weights + gradients + Adam m/v/master), which is fixed by model size and precision. The **actual training peak** is higher and is not inferable from that floor alone: it also includes activation memory (scales with batch size × sequence length × hidden dim, and is the dominant term for long-context or large-batch runs), temporary kernel workspace, allocator fragmentation, and checkpointing buffers. A host that fits the 1,120 GB floor can still fail to fit a given training run if its activation peak exceeds the remaining HBM — so the fit verdict for training must be checked against the measured peak for the specific batch/sequence configuration, not the parameter floor. (QLoRA's ~50–70 GB figure is likewise a floor: it holds the 4-bit base + adapters + a small optimizer, and its activation peak still depends on the run's batch and sequence length.)*

### Quantization describes several different choices

"Four-bit model" leaves several architectural questions open. Which tensors use four-bit values? How are those values chosen? What do the four bits represent? Where are scales stored? Which kernel consumes the resulting tensors? The figure below separates these questions. A calibration method, a tensor encoding and a checkpoint container can participate in the same deployment; they are not competing answers to one question.

![Fig 7.3 — Quantization choices and execution paths: error-control method, numerical representation, packed tensors and checkpoint container describe different parts of a deployment, and loading still requires a kernel-required runtime layout with compatible dispatch. Unsupported combinations may be rejected; fallback is not guaranteed. Mechanism and storage accounting, not an accuracy or throughput comparison.](figures/fig-07-0707-quantization-layers.png)

AWQ and GPTQ primarily address error control during post-training weight quantization. AWQ uses representative activations to identify important channels and chooses equivalent channel scaling that reduces the error introduced by quantizing weights. "Activation-aware" describes the information used by the method; it does not mean that activations are also stored in four bits. The paper's exploratory observation about protecting a small fraction of salient weights is not a definition requiring those weights to remain FP16. Its scaling method seeks protection without that irregular mixed-precision storage. [1P][FACT] ([AWQ, §3](https://arxiv.org/pdf/2306.00978v6)).

GPTQ instead uses approximate second-order information to compensate for quantization error in the remaining weights as quantization proceeds. Its original implementation targets weight quantization, not activation quantization. Neither method name uniquely specifies a group size, scale dtype, zero-point layout, permutation or checkpoint packing. Those fields are needed to reproduce both accuracy and memory use. Calibration data must represent the intended workload; a method's reported behavior on one evaluation does not establish behavior on another distribution. [1P][FACT] ([GPTQ, §2–4](https://arxiv.org/pdf/2210.17323v2)).

A container answers a different question. GGUF stores model metadata, tensor descriptions, tensor types and aligned tensor payloads. It is not a single numerical precision. Its tensor-type field permits different encodings within one model. Consequently, a comparison labeled "AWQ versus GGUF" confounds an error-control method with a file format unless both sides are expanded into complete deployment configurations. The useful comparison specifies the method, tensor encodings, mixed-precision exceptions and execution backend. The same caution applies to safetensors: storing tensors in a recognized container does not establish that a loader understands their quantized schema. [1P][DERIVED] ([GGUF specification, pinned revision](https://github.com/ggml-org/ggml/blob/da8e2a54b919557b816b1c2beb432ccb766f7ce0/docs/gguf.md), retrieved 2026-10-28).

A compact configuration record can keep the axes separate:

| Field | Architectural question |
|---|---|
| Target tensors | Weights, activations and KV cache each need an explicit precision policy. |
| Error-control procedure | What calibration, optimization, fine-tuning or distillation selected the values? |
| Numerical scheme | What are the value encoding, scale encoding, group axis and zero-point rule? |
| Export and packing | What container, tensor schema, padding and alignment does the loader expect? |
| Execution path | Which operator, device and kernel consume the tensors, and what happens if unsupported? |

The record is more durable than a list of product names. It also exposes a missing assumption before a memory estimate becomes a hardware recommendation.

#### Shared scales change the storage calculation

OCP MXFP4 1.0 uses E2M1 four-bit values, with one eight-bit E8M0 scale shared by a block of 32 values. E8M0 represents a power-of-two scale. The common one-dimensional NVFP4 scheme also uses E2M1 values, but shares an E4M3 local scale over 16 values and uses an additional FP32 tensor-global scale. Neither scheme uses an affine integer zero point in this comparison. The local scale's encoding and granularity change the set of representable values and its adaptation to a block's dynamic range; smaller groups also require more scale bytes. This is a mechanism difference, not an automatic accuracy ranking. [1P][FACT] ([OCP MX 1.0, §4–6](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf); [NVIDIA NVFP4 explanation, 2025-06-24](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/)).

The next figure holds the number of logical values constant. The same 32 four-bit values require 16 payload bytes in either scheme. MXFP4 adds one local-scale byte, producing 17 bytes per 32 values, or 0.53125 B/value. Common 1D NVFP4 adds two local-scale bytes, producing 18 bytes per 32 values, or 0.5625 B/value, before the tensor-global scale. For a tensor with N values in complete blocks, this example's compact NVFP4 storage is 0.5625N + 4 bytes. The four global-scale bytes are shared across the tensor, not repeated for each block. [1P][DERIVED]

![Fig 7.4 — Four-bit payloads and shared scale storage: both rows represent 32 E2M1 values, MXFP4 adding one local-scale byte (17 B per 32 values) and common 1D NVFP4 two (18 B per 32 values) plus a separate FP32 scale per tensor. Bars are proportional only for payload and local-scale bytes. Totals exclude padding, headers, extra copies and high-precision exceptions. Derived storage accounting, not an accuracy or throughput comparison.](figures/fig-07-0708-block-scale-bytes.png)

These rates are not the total footprint of a model. A mixed-precision model retains some tensors at higher precision. A file adds metadata and alignment gaps. A runtime may pad dimensions, reorder scales, create extra representations or reserve workspace. The memory ledger therefore separates checkpoint bytes, resident tensors, load/repack peak, activations, KV cache and workspace. A checkpoint that fits on disk may still fail during loading, and a successfully loaded checkpoint may not leave enough memory for the intended context and concurrency. The exact runtime layouts remain implementation-dependent. [1P][DERIVED]

#### Worked example: scale overhead is small but not zero

A 4096 × 4096 weight matrix holds 16,777,216 values. The shape is illustrative; the byte results follow the stated layouts. BF16 payload occupies 33,554,432 bytes. MXFP4 with complete 32-value blocks occupies 8,912,896 bytes. Common 1D NVFP4 with complete 16-value blocks and one FP32 global scale occupies 9,437,188 bytes. The difference comes from the chosen scale representation and grouping, not a different number of four-bit payload values. Both calculations exclude padding, additional scale copies and non-weight tensors. [ILLUSTRATIVE][DERIVED]

An integer scheme can produce a different bill again. With groups of 128, an illustrative INT4 layout containing an FP16 scale and a packed four-bit zero point per group uses 8,716,288 bytes for the same matrix. Replacing the packed zero with an FP16 scaled-zero increases that layout to 8,912,896 bytes. Equal total bytes do not make this integer scheme numerically equivalent to MXFP4. The example explains why an estimate needs the actual scale and zero layout rather than "four bits plus a little overhead." It does not choose an accuracy or speed winner. [ILLUSTRATIVE][DERIVED]

For a separate resource sensitivity, a 70B-parameter teaching model that stores 98% of parameters in MXFP4 and 2% in BF16 — fractions deliberately chosen, not a real checkpoint inventory — needs 39.24375 GB of compact weight storage rather than 140 GB. Retaining this chapter's full-MHA, BF16 KV assumptions (80 layers, KV width 8192, 9,500 tokens per sequence) leaves raw KV at 24.90368 GB per sequence. In a 640 GB aggregate pool with a fixed 64 GB reserve, the storage-only integer ceiling rises from 17 sequences to 21, not in proportion to the weight compression. The added KV budget does not prove that the ranks can place it or that 21 requests meet the latency SLO. Workspace, fragmentation and per-rank balance still need measurement, and the reserve itself may change. [ILLUSTRATIVE][DERIVED]

The causal consequence is narrower than "quantization solves memory." Weight compression frees one term in the memory ledger. If KV dominates the remaining footprint, context length and concurrency can still bind. Weight precision and KV precision remain separate decisions, with separate scale calibration, attention-kernel support and quality validation. KIVI's separate treatment of key and value statistics is one example of a KV-specific method, not a consequence of choosing an AWQ weight checkpoint. [1P][FACT] ([KIVI](https://arxiv.org/abs/2402.02750v2)).

#### Methods, containers and representations at a glance

This table compares roles, not competing vendors or measured performance. Time-sensitive implementation details are dated separately rather than asserted here.

| Item | What it specifies | What remains to establish |
|---|---|---|
| AWQ / GPTQ | Error control for post-training weight quantization | Encoding, groups, scales, packing, exceptions and selected kernel |
| GGUF | Container metadata and typed tensor payloads | Each tensor encoding and the loader/backend's actual coverage |
| GGML K / IQ | Specific block encodings and decoding rules | Tensor mix, calibration/imatrix policy and backend support |
| MXFP4 | E2M1 values and shared E8M0 block scaling in OCP 1.0 | Recipe, tensor roles, runtime layout and native or emulated arithmetic |
| Common 1D NVFP4 | E2M1 values, 16-value E4M3 scales and tensor FP32 scale | Training/inference recipe, padding, device and kernel support |
| FP8 / INT8 / INT4 | Value type or bitwidth, only partially specified by the name | Scaling, grouping, zero rule and operand precision |

FP8 also needs a precise definition: E4M3 and E5M2 differ in range and special-value behavior, and the OFP8 specification does not choose the scaling algorithm. SmoothQuant is a W8A8 calibration method, not another name for INT8. NF4 is a nonuniform representation used by QLoRA; a four-bit frozen training base does not imply native FP4 GEMM or describe the memory used by adapters, activations, gradients and optimizer state. [1P][FACT] ([OFP8](https://www.opencompute.org/documents/ocp-8-bit-floating-point-specification-ofp8-revision-1-0-2023-12-01-pdf-1); [SmoothQuant](https://arxiv.org/abs/2211.10438v7); [QLoRA](https://arxiv.org/abs/2305.14314v1)).

## 4. Measurement

Four practical measurement habits follow from the arithmetic above:

1. **Compute KV cache per-token cost for the model.** The per-token KV footprint of a fully-cached (MHA) attention head is

$$
KV_{\text{per-token}} = 2 \times n_\text{layers} \times d_\text{hidden} \times \text{bytes-per-value}
$$

(one key and one value per layer, each $d_\text{hidden}$ wide), evaluated at the chosen precision. For a 70B model at FP16 the answer is $2 \times 80 \times 8192 \times 2 \text{ B} = 2{,}621{,}440$ B $\approx 2.62$ MB/token (exactly **2.5 MiB/token**; 2,621,440 bytes is 2.62144 decimal MB). At 8-bit the per-token value halves to ~1.31 MB/token (~1.25 MiB; the Ch.1 reference). Do not assume the 1.3 MB/token figure applies at FP16 — it does not; it is an 8-bit number. When evaluating a model where the hidden dimension or layer count differs from LLaMA-70B, recompute the constant factor — a model with 64 layers and 8192 dim will have ~2.1 MB/token at FP16 (2 × 64 × 8192 × 2 B = 2,097,152 B), while a model with 100 layers and 12288 dim will have ~4.9 MB/token (2 × 100 × 12288 × 2 B = 4,915,200 B).

2. **Log peak context length, not just average.** A workload that averages 9.2K input tokens but has a long tail toward 32K or 128K will have a very different KV cache profile. Log the 95th-percentile context length and re-run the KV arithmetic; the memory floor may shift from fitting on 2×H100 to needing 8×H100. This is especially important for RAG workloads, where the retrieved context may average 8K but occasionally peak at 32K+ for technical documents.

3. **Measure inference residency as weights + KV, not weights alone.** It is common to see the 140 GB weight footprint (70B FP16) fit across **two** 80-GB accelerators and conclude that 160 GB is sufficient. But 140 GB of weights leaves only ~20 GB before runtime/workspace and KV are added; at 9.2K input the KV cache adds ~24.1 GB, pushing the total to ~164.1 GB — already over the 160 GB aggregate, so the model does *not* fit on two accelerators once KV is counted. Always include KV when we state the memory floor for inference.

4. **Account for KV quantization when reporting residency.** If the serving stack uses FP8 KV, the per-token KV cost drops from ~2.62 MB to ~1.31 MB (raw tensor byte-halving, exactly 50% of BF16 = 2,621,440/2 = 1,310,720 B = 1.25 MiB), and the 9.5K max residency falls from ~165 GB to ~152 GB (weights 140 GB + KV 12.45 GB). State both the BF16 and FP8 residency numbers, because the choice of KV dtype changes the hardware requirement decisively. **Note the accounting basis:** the ~1.31 MB/token figure is the raw tensor byte-halving of the same MHA tensors (one byte per K/V element, exactly half of BF16's two bytes); it is NOT a vendor-measured serving footprint, and any block-layout or per-token scale/offset metadata overhead is not included. **Do not generalize a fixed ratio to all FP8-KV deployments:** the realized per-token footprint depends on the engine version, cache-block layout, scale/offset metadata, allocator rounding, and the accounting boundary (logical payload vs allocated cache vs observed resident memory), so re-derive it for the target serving stack rather than inheriting a multiplier. (For reference, the 9.5K total at this byte-halving basis is ~152 GB — still above a single H100, but now within 2×H100, 160 GB.)

## 5. Common Mistakes

- **Assuming KV cache size scales sub-linearly.** The KV cache grows linearly with context length. Doubling the context from 9.2K to 18.4K doubles the KV memory, all else equal. There is no automatic compression unless the attention mechanism itself is hybrid or sparse.

- **Using the 8-bit KV figure (~1.3 MB/token) at FP16.** Chapter 1's ~1.3 MB/token is explicitly at 8-bit precision. At FP16, the per-token KV cost is ~2× that, ≈2.62 MB/token (2.5 MiB — §7.4). Mixing the two figures produces wrong residency calls.

- **Ignoring the weight + KV residency contrast.** Quoting only the weight footprint (140 GB for 70B FP16) and claiming it fits on one H100 (80 GB) is a category error. Weights alone exceed one H100; KV must be added.

- **Quoting one KV-quant reduction for every precision.** KV cache quantization must be read per bit width: FP8 KV ≈50% of BF16 (raw byte-halving) is what serving stacks realize today, while 4-bit KV's raw bound is a full 4× (2.62 → 0.66 MB/token here; 0.52 → 0.13 for a 7B, §12.3) — realized savings land between, once block/scale metadata is counted. (The vLLM "54%" figure is a decode inter-token-latency slope ratio, not a memory ratio.) Weight-only quantization's 2×–4× applies to weights; do not transfer an expectation across precisions or across tensors without naming the bit width.

- **Overlooking the fine-tuning residency floor.** Full fine-tuning of 70B requires ~1.12 TB with Adam optimizer states — roughly 1.75× the 8×H100 host. This is not a temporary overhead; it is the permanent memory floor for the training duration.

## 6. Architecture Consequence

The memory floor is the first constraint every architecture decision respects, because unlike compute or bandwidth it cannot be moved by better kernels — it is fixed by weights + KV + (for training) optimizer state. Several concrete consequences follow for the canonical enterprise-Q&A workload:

- **Model residency decides host count.** A 70B FP16 model (140 GB weights) at the 9.5K max context (9.2K in + 300 out) needs ~24.9 GB of KV cache (FP16), so the max end-of-generation residency ≈ 165 GB — it does *not* fit on a single 80 GB H100, nor within the 160 GB aggregate of 2×H100 (160 GB < 165 GB). By *aggregate memory capacity* it needs **≥ 3×80 GB** (240 GB) — but note this is an **aggregate-HBM lower bound on card count, NOT a validated 3-way tensor-parallel configuration**: whether three 80-GB cards actually admit a 70B model depends on head/layer shard divisibility, KV-head routing, TP=3 support, workspace/communication layout, and per-rank fragmentation, none of which the aggregate sum establishes. A practical TP topology (e.g. TP=4 or TP=8) must be checked against the serving engine and model geometry before three cards are treated as deployable. The canonical single host of 8×H100 (640 GB) is not justified by basic capacity alone — three 80 GB GPUs already clear the 165 GB residency floor; the 8×H100 host is chosen for compute, bandwidth, topology, concurrency, implementation constraints, and headroom. [canonical scenario][DERIVED]

- **KV cache quantization buys back memory, not compute.** FP8 KV ≈ 50% of BF16 (raw byte-halving), dropping the 9.5K max residency from ~165 GB toward ~152 GB. This is a *memory* lever, orthogonal to bandwidth/compute fixes — the architect pulls it when the KV floor, not decode bandwidth, binds.

- **Fine-tuning is a different memory regime than inference.** The same model that serves in ~165 GB demands ~1,120 GB under full Adam fine-tuning (weights 140 GB + gradients 140 GB + Adam m/v/master states 840 GB) — roughly 1.75× the 8×H100 host. This is why the architect separates the serving fleet from the training fleet: the memory floors differ by an order of magnitude. [canonical scenario][DERIVED]

- **Context length is the largest controllable KV lever.** Doubling context from 9.2K to 18.4K doubles KV (~24.1 GB → ~48 GB); 128K context drives KV to ~335 GB, which forces quantization or model parallelism. The architecture must set a context-length ceiling to keep the served model within host memory. [ILLUSTRATIVE][DERIVED]

In short: the architect sizes the host by weights + KV at the longest supported context, treats KV quantization as a spare memory dial, and keeps inference and training on separate memory-planning tracks.

## 7. What We Still Don't Know

- Per-model KV state beyond K/V — the additional per-head state and per-layer scale/offset metadata some attention implementations store alongside keys and values. The `2 × layers × n_KV-heads × head_dim × bytes` formula prices the K/V entries themselves (§7.3 covers GQA/MQA exactly by substituting the model card's KV-head count), but the extra per-token bytes an implementation adds on top of K/V are not derived in this chapter and must be established per architecture and serving stack.

- Quality loss from aggressive KV quantization (2-bit KIVI, or sub-4-bit schemes) at very long context lengths (128K+, MoE experts). The primary sources anchor FP8 KV ≈50% of BF16 (raw byte-halving) at near-zero quality loss, but 2-bit asymmetric patterns and their interaction with RoPE and sliding-window layers are not fully mapped.

- Whether per-request KV caching can be partially offloaded to CPU DRAM during decode without TTFT impact, beyond the vLLM KV Offloading Connector's 2–22× TTFT reduction range [S7][1P][FACT], which is highly prompt-size-dependent. The community is converging on tiered KV storage (GPU resident hot set + CPU/DRAM cold set), but the latency trade-offs at concurrency > 1 are not yet primary-anchored.

- **Frontier 2026 has begun re-engineering the KV constant factor, not just quantizing it.** All four 2026-class open architectures attack KV cache size at the attention layer itself, on top of the per-token footprint this chapter derives: DeepSeek-V4's hybrid CSA+HCA reports KV cache at only ~10% (Pro) / ~7% (Flash) of DeepSeek-V3.2 at 1M-token context [1P: arXiv 2606.19348]; GLM-5.3-Flash's sparse+linear hybrid reports ~4.4× smaller per-layer average BF16 KV cache than GLM-5.3 [1P: Z.ai GLM-5.3-Flash release article, 2026-08-26]; Kimi K3's Kimi Delta Attention + Attention Residuals targets information flow across long sequences [1P: arXiv 2607.24653]; Qwen3.8-Flash-Next combines Gated DeltaNet (compress history) with Qwen Sparse Attention (micro-block indexing) for long-context cost [1P: HF Qwen/Qwen3.8-Flash-Next]. For the architect this is a decisive shift: the KV arithmetic in this chapter (per-token × context) is *not* a fixed constant across model generations — a 2026 hybrid-attention model can hold dramatically more context per byte of KV than the canonical 70B/8×H100 framing assumed. Size the host against the *specific* model's KV scheme, not a universal constant.

- The impact of MoE routing on KV cache: does each token really emit a full key/value per layer across all experts, or does routing activate only a subset? The total-vs-active and MoE-vs-dense facts of Ch 3 (total parameters ≠ active parameters per token; MoE gives compute sparsity, not weight-residency sparsity) confirm that attention layers process every token densely and emit key/value per token, so MoE sparsity does not reduce KV — but the constant factor for MoE models (e.g., number of experts per layer) needs per-model validation.

![Fig 7.5 — KV cache size vs context length, canonical 80-layer reference geometry (full-MHA vs GQA, FP8/8-bit): **parameter count does not determine KV size** — KV per token is set by the *attention shape* (layers × KV-heads × head-dim × precision), so a 70B full-MHA and a 70B GQA differ; full-MHA is the conservative upper-bound baseline, GQA ~8× smaller. **Scope:** FP16 ~2.62 MB/token, FP8/8-bit ~1.31; at 128K the FP16 KV footprint is ~335 GB (vs the ~436 GB KV budget), ~24.9 GB at 9.5K (total weights+KV residency then ~165 GB, §7.1). The FP8 value is raw byte-halving (50% of BF16), not a vLLM-measured footprint — block/scale-metadata not included (Table 7-1). [ILLUSTRATIVE][DERIVED]](figures/fig-07-0701.png)

<!-- Figure spec: X = context tokens (1K,4K,9.2K,32K,128K), Y = KV cache GB (log scale); three lines FP16/FP8/8-bit; horizontal 640 GB 8×H100 ceiling; callouts at 9.2K (~24 GB FP16) and 32K (~80 GB). -->

![Fig 7.6 — Inference vs fine-tuning memory floor. The same 70B model serves in ~165 GB (weights + KV, max 9.5K) but needs ~1,120 GB for full Adam fine-tuning; QLoRA fits ~50–70 GB on a single GPU. [ILLUSTRATIVE][DERIVED]](figures/fig-07-0702.png)

![Fig 7.7 — The concurrency budget: where a 70B (canonical 80-layer full-MHA teaching geometry) host's 640 GB pool goes. **Aggregate-feasibility caveat:** the 640 GB figure is an *aggregate* across eight 80-GB H100s, not a single freely-allotable heap. Whether a given allocation actually fits depends on tensor-parallel sharding, KV partitioning, replication, runtime layout, per-rank fragmentation, workspace requirements, and communication topology — so "total bytes < total HBM" is a necessary but not sufficient test. Per-rank fit and sharding must also be validated (Chapters 9–10). **Per-rank example (TP=8):** the 140 GB of weights shard to ~17.5 GB per GPU; the ~64 GB runtime/NCCL reserve is per-host (not per-rank); the ~436 GB KV budget shards to ~54.5 GB per GPU, and under tensor-parallel attention the per-request KV (24.9 GB) also shards across the 8 ranks, so the per-rank KV per request is ~3.1 GB — the 17.5 concurrent figure is the *aggregate* bound, and the per-rank fit must be checked separately (a rank can be the binding constraint even when the aggregate fits). The figure shows the one dominant budget relationship: the on-host pool decomposes into weights + runtime + a leftover KV budget, and that KV budget divided by the per-request KV price sets concurrency. 140 GB weights + ~64 GB runtime/NCCL leaves ~436 GB of KV budget; at the 24.9 GB/request max-FP16 KV that gives C ≈ 17.5 concurrent requests (byte-accurate 436÷24.9037 = 17.51; the conservative integer "requests that fit" floor is 17, not 18), and FP8 (~12.45 GB/request) roughly raises it to ~35.0. This is the arithmetic behind the single-host capacity in Ch17. **This is an analytical upper bound, not a validated concurrent-request count** — the actual achievable concurrency must be measured under the target workload (Ch 14). [ILLUSTRATIVE][DERIVED]](figures/fig-07-0704.png)

![Fig 7.8 — Memory Tetris: how the 8×H100 host's 640 GB **aggregate** pool fills at 9.5K / 32K / 128K for the canonical 80-layer full-MHA 70B. **Takeaway: context length is the dominant memory lever** — the FP16 KV cache (orange) is the only block that grows, consuming the fixed ~436 GB KV budget (~17.5 concurrent at 9.5K, floor 17; only ~1–2 at 128K). **Aggregate-feasibility caveat:** an aggregate residency test, not a proof each allocation maps onto per-rank HBM — the 80 GB rank-boundary lines are a *visualization guide*; sharding, KV partitioning, fragmentation, interconnect must be validated per rank. [ILLUSTRATIVE][DERIVED]](figures/fig-07-0705.png)

<!-- Figure spec: one horizontal stacked bar (140 weights + 64 runtime + 436 KV = 640 GB pool); tick KV region in 24.9 GB slots -> C~17.5; faint FP8 overlay ~35.0 slots. Locks Ch7 <-> Ch17 handoff. -->

## 8. End-of-Chapter Mini-Case: Sizing Memory First for the 5,000-Employee Wiki

An architect is asked to design an internal Q&A system over the company's document repository. The initial ask is vague: "We need to let all 5,000 employees ask questions over our internal wikis." Before any architecture can be defended, the architect must turn this vague desire into a machine-denominated statement using the chapter's core constraint.

From the unit-and-token work of Ch 1 alone, the architect can already establish several facts. The unit is tokens; the request shape will be prompt + retrieved context + output; the workload is input-heavy (retrieved context dominates); and the first number to lock down is tokens-per-request, because every downstream decision (which model fits, how much memory, what latency is possible) is priced against it.

Running the KV arithmetic: if each request uses ~9.2K input tokens (the canonical ~1,200 prompt + 8K retrieved) plus ~300 output tokens, the request grows to a **9.5K max KV sequence** by the end of generation. The KV cache per request at 70B FP16 is ~24.9 GB (max, 9.5K), against ~24.1 GB for the initial 9.2K-prefill residency. The weight footprint is 140 GB. Total max inference residency is ≈165 GB, which does **not** fit within the nominal 160 GB aggregate HBM of 2×80 GB H100s; practical deployment therefore requires additional capacity, lower precision, or a larger GPU configuration. It fits comfortably within the 640 GB aggregate HBM of an 8×H100 host. If the context is extended to 32K (e.g., wider document retrieval), the KV cache rises to ~84 GB, pushing total residency to ~224 GB — still fitting in 8×H100 but requiring a multi-GPU node.

The architect can now speak the system's currency: tokens, KV bytes, and the residency floor. The next step — turning "5,000 employees" into ~2,000 registered users (~100 concurrent typical / ~400 at peak), ~10 requests/s, and a specific model-and-hardware choice — is Chapter 4's job (workload anatomy). Here the point is narrower and sharper: we can now say, with quantified memory numbers, whether the system fits on the available hardware, and we can compare inference vs. fine-tuning residency floors before committing to an architecture decision. This is the chapter's payoff: the vague request has been translated into concrete constraint numbers, and the architect can defend a recommendation based on whether the workload fits, not on intuition alone.