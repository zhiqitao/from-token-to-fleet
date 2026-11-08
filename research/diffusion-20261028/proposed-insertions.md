# Proposed English insertions — diffusion mechanisms and language models

Editorial status: developed candidate book text, not applied to the manuscript. Figures are original assets in this research directory. Final figure numbering, cross-chapter references and full-book pagination remain the parent editor's responsibility. The two figure IDs D1/D2 are temporary. Claim IDs refer to claims.json, whose evidence records contain retained primary-source URLs, quotations, line numbers and byte hashes. No model or service benchmark was executed for this package.

## Placement and non-duplication map

| Anchor | Exact existing target | Proposed action |
|---|---|---|
| P03A, P03B | `design/manuscript/chapter-03/chapter-03.md`, after the paragraph beginning `The architect-relevant distinction: total parameters` (line 14), before `A note on provenance` | Add one subordinate section, `Alternative inference: the token is not the execution step`. Keep dense/MoE arithmetic and its worked examples. Split the new section at P03B only for editorial navigation; both anchors belong to the same section. Place D1 after the training/sampling explanation, D2 after the cache-boundary explanation. |
| P07 | `design/manuscript/chapter-07/chapter-07.md`, immediately after the two-item definition beginning `Residency floor` / `Practical host requirement` (lines 13–18), before `## 2. Mental Model` | Add the state-lifetime box. Do not duplicate the existing KV byte derivation or change the canonical AR budget. |
| P08 | `design/manuscript/chapter-08/chapter-08.md:11`, after the paragraph beginning `For a dense transformer layer`, before `But FLOPs alone do not tell the full story` | Add the execution-work box and its illustrative example. This is a separate sensitivity example, not a replacement for the canonical scenario. |
| P11 | `design/manuscript/chapter-11/chapter-11.md`, after the paragraph beginning `The columns read as knobs` below Table 11-2 (line 149), before `## 7. What We Still Don't Know` | Add the algorithm-specific serving qualification. It narrows engine-wide feature claims without adding another engine-ranking table. |
| P14 | `design/manuscript/chapter-14/chapter-14.md:15`, after the paragraph beginning `The core insight`, before `## 2. Mental Model` | Add commit-aware measurement paragraphs. Preserve the existing SLO-goodput definition; define successful-request goodput separately. |
| P05 | `design/manuscript/chapter-05/chapter-05.md:15`, after item 5 (`Retrieve-then-generate vs end-to-end`), before `The core reframe` | Add the selection paragraph. Point to P03/P14 rather than repeat mechanisms. |
| PFRONT | Separate new dated addendum, outside the frozen four-family Appendix A comparison in `design/manuscript/chapter-27/chapter-27.md:3–14` | Add dated release/support observations only. Do not silently extend the August 30 cutoff or its single September 27 exception. |

Scope reminders, not replacement chapters: Chapter 1 already says `text-tokenized autoregressive models`, and Chapter 2 already says `In an autoregressive model`. The nearby K/V-invariance statement in Chapter 2 can begin `With a fixed causal prefix, ...`. Chapter 7's weights-plus-KV floor can be introduced as `For the autoregressive baseline used here, ...`. These reminders preserve correct existing scope. [D29][DERIVED]

---

<a id="P03A"></a>
## P03A — Alternative inference: the token is not the execution step

Dense versus MoE describes parameter allocation. Autoregressive versus diffusion generation describes a different axis: how the model constructs an output and which intermediate states it revisits. A diffusion language model can itself be dense or MoE. The active-parameter count still matters, but final output tokens no longer count the model's work on their own. We also need the sequence of model evaluations, the positions recomputed in each evaluation, and the point at which output becomes final. [D07–D19][1P][FACT]; accounting interpretation [D33][DERIVED]

### From corruption to learned generation

A diffusion model learns to reverse a specified corruption process. In a continuous denoising diffusion model, the forward process progressively adds noise to data. Training constructs corrupted examples and teaches a model to predict information needed for the reverse process, such as the added noise. At generation time, sampling starts from a simple prior and repeatedly applies learned reverse updates. The forward process is not an inference pipeline that first corrupts the requested answer: the answer is not available during generation. The forward process defines the learning problem. [D01][1P][FACT]

Score-based formulations express related dynamics through the score, the gradient of the log density of perturbed data. The associated reverse-time stochastic differential equation and probability-flow ordinary differential equation provide different sampling trajectories. In the ideal formulation they can share time-marginal distributions; this does not make their finite-step numerical errors, randomness or network-evaluation counts identical. A deterministic solver can still require many sequential evaluations. [D02][1P][FACT]

Text requires a discrete construction because token IDs are categories, not continuous pixel values. Discrete diffusion defines corruption through transitions between categorical states. Uniform token replacement and an absorbing MASK state are different choices. In masked diffusion, training hides selected tokens and learns to recover them from the visible sequence. MDLM and LLaDA connect this procedure to diffusion likelihood objectives; it is not merely a fixed-rate masked-language-model loss with a new name. LLaDA samples mask rates and weights the masked-token loss accordingly. Its conditional fine-tuning leaves the prompt clean while corrupting the response. This teaches the reverse model to reconstruct an answer conditioned on a known request. [D05–D07][1P][FACT]

Figure D1 separates the specified forward process from learned reverse generation. Its two lanes also separate continuous and categorical state spaces. Neither lane is a benchmark, and the token example is not an actual model response.

![Figure D1 — Corruption and learned reverse generation. Rightward q arrows specify corruption; leftward p_theta arrows denote learned reverse updates. Continuous-valued noise and categorical MASK are different state spaces. Masked diffusion is one discrete construction, not a definition of every diffusion model. The drawings are conceptual, not measurements. [1P][FACT] D01–D07; drawing [ILLUSTRATIVE].](figures/D1.png){width=6.1in}

Flow matching belongs next to this discussion, but not inside a synonym list. It regresses a vector field on a chosen probability path; the family of paths can include diffusion paths and can extend beyond them. Rectified flow uses straight interpolants to learn transport and can iteratively rectify the coupling. Straight training interpolants do not guarantee that any trained model has perfectly straight generation trajectories or equal-quality one-step sampling. The shared systems question is repeated model evaluation along a path. The objectives and samplers remain distinct. [D03–D04][1P][FACT]

### A language-generation trajectory

A basic masked language sampler allocates an output canvas containing unresolved positions. Each evaluation predicts token distributions using the current canvas and the prompt. The sampler accepts some predictions and leaves other positions unresolved. A confidence policy may accept several positions at once, so generation need not advance strictly left to right. In the inspected LLaDA base sampler, already accepted token IDs are retained; remasking low-confidence candidates does not mean that every accepted token is repeatedly edited. The configured output capacity and evaluation schedule still determine work even when later display logic removes an EOS suffix. [D08][1P][FACT]

Parallel predictions are not free joint reasoning. Several position-wise predictions from one canvas evaluation are conditioned on the old canvas, not necessarily on one another's newly sampled values. Individually plausible tokens can form an implausible combination. Confidence thresholds, extra rounds and verification can improve this tradeoff, but they change the amount of work and may change task quality. A lower iteration count is therefore not a quality-neutral implementation improvement by default. [D10][1P][FACT]

The inference loop is also not an agent loop. An agent turn may invoke a model, inspect a tool result and decide its next action. A diffusion round updates an internal output state. An autoregressive model with a long chain of thought remains autoregressive. A diffusion draft model can also propose blocks for an autoregressive verifier, as in DFlash; that combination does not turn the verifier's target distribution into a fully diffusion-based language model. [D28][1P][FACT]

<a id="P03B"></a>
### State reuse follows dependency boundaries

The ordinary causal-cache argument depends on a fixed prefix. Later output tokens cannot change an earlier token's causal hidden state. Under bidirectional attention, an unchanged token ID can acquire a different representation when another canvas position changes. Its previous K/V tensors can therefore be stale even though its spelling is unchanged. Approximate cache policies exploit empirical stability, delayed caching or selective refresh; those policies require quality and refresh-cost measurements. Fast-dLLM and dKV-Cache are concrete examples, not proof that ordinary autoregressive caching transfers unchanged. [D11–D12][1P][FACT]

A block-causal model creates a stronger boundary. Earlier finalized blocks cannot depend on later blocks, while the active block can use bidirectional attention internally. The runtime can reuse correctly finalized prefix state and repeatedly recompute the active block. Finalization must make cached state correspond to the accepted block contents; accepting token IDs alone is not always enough. DiffusionGemma uses a related separation between cached encoded context and a mutable decoder canvas, then encodes the completed canvas before continuing. These are architectural boundaries, not a universal property of the word “diffusion.” [D13,D18][1P][FACT]

Figure D2 compares these dependencies. Solid token IDs and reusable prefix state are deliberately separate visual concepts. The dashed region denotes recomputed output representations, not a promise that every enclosed token ID remains editable. The full-canvas lane makes no assumption that a clean prompt automatically has invariant bidirectional state.

![Figure D2 — Dependency order and cache lifetime. AR extends a causal prefix; its displayed snapshots include processing of the newest accepted token before that token's K/V are shown as finalized. The selected full-canvas masked sampler accepts positions out of order while recomputing bidirectional states. The block-causal example refines an active block, finalizes its state and then advances. Loops represent repeated evaluations, not fixed counts or proportional time. Solid brackets identify finalized prefix state; accepted token IDs alone do not establish reusable K/V. [1P][FACT] D08,D11–D15,D18,D24–D26; resource interpretation [DERIVED] D33–D34.](figures/D2.png){width=6.1in}

Not every language diffusion process starts from MASK or only fills holes. Uniform-state renoising can begin with ordinary token states. Editing models can replace accepted tokens or perform insertion/deletion operations within a bounded block. LLaDA2.2 restores its configured block length after such operations; this is not an unbounded global canvas. A stopping rule may test unresolved positions, stability, confidence, EOS or an iteration limit. These are operational termination rules, not proofs of semantic correctness. [D15,D18,D20,D25][1P][FACT]

The architectural consequence is conditional. Parallel positions can improve matrix utilization at low request concurrency, but repeated evaluation can increase total compute and communications. Block size changes both parallel work and the delay before commitment. A useful deployment comparison therefore fixes the task-quality requirement first, then measures the inference schedule, peak state and committed-output latency together. The token remains the application interface; the execution trace connects that interface to resources. [D33–D34][DERIVED]

---

<a id="P07"></a>
## P07 — Box: count state by lifetime, not by the model label

The weights-plus-KV floor in this chapter describes the autoregressive baseline. A diffusion language runtime needs a state-lifetime inventory before the same capacity calculation can be applied. We distinguish resident weights, reusable context state, mutable canvas state, peak activations and logits, kernel workspace, and runtime allocations. These categories must be disjoint at the instant being measured; two names for the same buffer do not create two memory costs. [D34][DERIVED]

The KV tensor byte formula remains valid for actual K/V tensors. What changes is the proof that those tensors can be reused. Figure D2 shows why unchanged token IDs are insufficient under bidirectional refinement. A block-causal boundary can make an earlier prefix immutable. Approximate cache policies instead trade refresh work against quality. Memory capacity and cache validity are separate checks. [D11–D13][1P][FACT]

Repeated sequential evaluations need not multiply peak memory by the number of rounds when inference releases temporary buffers after each round. Retained histories, previous-round logits for self-conditioning, or simultaneous verification views change that lifetime calculation. As a shape-only example, a 256-position canvas over a 262,144-entry vocabulary needs 256 × 262,144 × 4 = 268,435,456 bytes, or 256 MiB, for one FP32 logits tensor at batch one. This excludes probabilities, sampling workspace, retained logits, attention buffers and the rest of the model. It is not a measured model footprint. [ILLUSTRATIVE][ASSUMPTION][DERIVED]; calculations.json, D20,D34

This distinction affects admission control. A runtime may have enough capacity for prefix state yet fail when many requests enter a high-workspace refinement phase together. Weight precision alone cannot certify fit: the inspected LLaDA sampling code can use FP64 sampling intermediates even when the network weights use a lower precision. The deployed sampler's live tensor shapes and lifetimes decide the practical requirement. [D08,D34][1P][FACT / DERIVED]

---

<a id="P08"></a>
## P08 — Box: fewer sequential evaluations can mean more total work

For an iterative language generator, the approximately 2N projection-cost rule applies to processed positions, not just final output tokens. Let P_j be the active parameter count and Q_j the positions evaluated in network evaluation j. A projection-dominated work proxy is

    F_projection ≈ Σ_j 2 P_j Q_j.

The trace also needs attention pair counts, output-head work, routing, sampling, refresh and verification. For a full dense-attention evaluation over length L, attention work grows quadratically with L. For K active queries over a cached prefix of length C, the attention main term grows with K(C + K), before the architecture's head and layer factors. Reducing the number of recomputed query positions does not eliminate reads of a long prefix. [D33][DERIVED]

Consider an explicitly illustrative 7B-active-parameter model that emits 256 tokens in 32-token blocks and uses eight decoder evaluations per block. There are eight blocks, hence 64 sequential decoder evaluations. The decoder nevertheless evaluates 256 × 8 = 2,048 output positions. Its projection proxy is 2 × 7B × 2,048 = 28.672 TFLOP. A simplified output-only AR counter evaluates 256 positions and gives 3.584 TFLOP. The block example has one quarter as many sequential evaluations but eight times as much output-side projection work. These are different quantities, not contradictory results. [ILLUSTRATIVE][ASSUMPTION][DERIVED]; calculate.py and calculations.json

This arithmetic omits prompt encoding, context attention, block-finalization encoding, the output head, refresh, classifier-free guidance, verification and communication. It also simplifies the book's first-token-from-prefill convention. It compares counters, not equal-quality models, and predicts neither a fourfold speedup nor an eightfold end-to-end slowdown. A network-evaluation count must include extra verification passes and the shapes of any combined guidance branches, rather than count only outer sampler rounds. [D27,D33][DERIVED]

Why might the higher-work path still finish earlier? Processing more positions together can reuse loaded weights across more matrix rows and improve low-batch utilization. Why might it lose under load? Optimized AR request batching can already supply those rows, while refinement continues to repeat work. Distributed execution also repeats tensor-parallel collectives and any expert dispatch required by each evaluation. The number of sequential rounds and the total communicated bytes can move in opposite directions. [D16,D33][DERIVED]; low-concurrency qualification [B02][1P][FACT, vendor report]

MoE adds a working-set issue. Active parameters per token do not equal the union of experts touched by all positions in a parallel block. LLaDA2.2 explicitly limits a block's expert pool before per-token routing. That bounds an execution working set; it does not make the other resident experts disappear. The useful measurements are expert-union size, dispatch bytes, load imbalance and collective time, alongside active FLOPs. [D16][1P][FACT]; measurement consequence [DERIVED]

The resulting fleet decision follows measured service demand. At a fixed task-quality and latency target, GPU-seconds, successful-request throughput and resident state determine capacity. Output tokens divided by denoising steps do not determine the number of hosts. [D33–D34][DERIVED]

---

<a id="P11"></a>
## P11 — A serving feature belongs to an algorithm path

The capability table is a map of mechanisms, not a guarantee that every supported model can combine every row. Diffusion makes this qualification especially important. A paged allocator can manage buffers without proving that their contents remain valid across refinement. A prefix-cache key must describe finalized token content and compatible state, not an unresolved MASK canvas. Grammar constraints, quantized loading, graph capture and distributed parallelism also depend on the selected model implementation and sampler. [D24–D26,D36][1P][FACT]

Requests can require different numbers of refinement rounds. A lockstep batch waits for its slowest active member unless the scheduler can preserve unfinished state and admit or complete requests independently. The inspected SGLang diffusion scheduler implements a first-done-first-out path that retains partial block state. This is explicit iteration-aware scheduling, not evidence that the AR token loop works unchanged. Tail latency depends on the distribution of rounds, block sizes, queueing, refresh and cancellation—not merely the average accepted tokens per round. [D24][1P][FACT]; latency interpretation [DERIVED]

Figure D2 identifies the natural commitment boundary in the block-causal example. A prefill/decode split must place context encoding, block refinement and finalization on explicit resources. Any transferred state, repeated attention to that state, and finalization work belong in the service budget. The familiar principle survives: specialization is useful only when its benefit exceeds transfer and orchestration costs. The objects being transferred cannot be inferred from an AR KV formula alone. [D18,D33–D34][DERIVED]

---

<a id="P14"></a>
## P14 — Measure drafts, commitments and valid results separately

Iterative generation introduces more than one plausible “first token.” A service can expose a provisional draft, commit an irreversible prefix or block, and later finish a valid response. Those are different events. A first-draft timestamp measures early visibility. A first-commit timestamp measures when a downstream consumer can safely act on text that will not be overwritten. Time to a validated answer includes any required schema checks, unit tests or task acceptance. Comparisons need the same boundary on both sides. [D22,D26][1P][FACT]; metric definitions [DERIVED]

Burst streaming also changes the meaning of inter-token latency. A runtime may deliver an entire block in one event and pause while refining the next block. Splitting that event into individual client tokens creates near-zero within-block gaps without shortening the pause between blocks. We therefore retain final-token throughput but add block size, block-arrival gaps, first-commit latency and end-to-end p95/p99 latency. Figure D2 is a dependency diagram, not a proportional timing diagram. [D26,D33][DERIVED]

The existing token SLO-goodput definition still counts only service-compliant final output. Provisional text that is overwritten is not extra useful output. A separate successful-request metric can count requests that pass all three gates—task validity, required quality and the service SLO—per unit wall time. This is an additional metric, not a silent redefinition of token goodput. If retries, fallback or tool execution belong to the service, their time and cost remain inside the boundary. [D22,D33][DERIVED]

A reproducible comparison freezes model and tokenizer revisions, sampler, thresholds, block size, cache policy, quantization and runtime commit. It uses a calibration set to choose operating points and a separate holdout set to evaluate them. Both sides receive reasonable optimizations: optimized AR KV/batching and, where available, a speculative baseline; the applicable diffusion cache, refresh and verification paths. Speed is compared only after the quality gate is met. [D10–D14,D27–D28,D33][DERIVED protocol]

We measure a warmed single request, a concurrency sweep and an open-loop offered-load sweep. The workload includes long prompts, code infilling, fixed-region editing and structured tool calls. The execution trace records evaluations, recomputed positions, verification and final committed tokens; the service trace records queueing, drafts, commitment, completion, failures and cancellation. Hardware-matched experiments can support resource-efficiency claims. A closed API whose hardware and internal schedule are unknown belongs in a separate service-level comparison, not a GPU-FLOP ranking. [D21–D22,D33–D34][DERIVED protocol]

---

<a id="P05"></a>
## P05 — Inference mode is a candidate, not a selection verdict

The same task can favor different inference modes at different concurrency levels. Parallel refinement is worth investigating when low-batch latency or constrained infilling dominates, but neither advantage follows from a model-family label. AR fill-in-the-middle models are a necessary editing baseline. Structured output adds another gate: an API that documents JSON-schema generation and a self-hosted backend that rejects grammar constraints are not interchangeable candidates. The selection question is whether the specific model, sampler and runtime meet the workload's quality, output and SLO requirements together. The mechanisms in Chapter 3 explain the candidate; the measurements in Chapter 14 decide whether it belongs in the architecture. [D22,D26,D33][DERIVED]

---

<a id="PFRONT"></a>
## PFRONT — Dated research addendum: diffusion language generation, 2026-10-28 UTC

This observation is outside Appendix A's frozen 2026-08-30 comparison. It does not update that four-family table or treat a present-day source as proof of its historical contents.

Public artifacts now support more than one diffusion-language deployment pattern. LLaDA and Dream provide open checkpoints and generation code for masked/refinement-based language generation. Their announcements, paper dates and later checkpoint revisions are separate provenance events. LLaDA2.2 adds bounded block editing and block-level expert routing. DiffusionGemma is an explicitly experimental open release with an encoded context cache and a separately refined canvas; its uniform-state renoising does not require MASK. Mercury 3 is a vendor-documented closed API release dated 2026-10-19. Its internal schedule, precision and hardware allocation have not been independently established here. Gemini Diffusion's official page describes an experimental demo. These records establish different release and support boundaries, not a common production-readiness level. [D17–D23,D35][1P][FACT]

The inspected SGLang revision, `a1966e1b5d8b750b494d7e53cca1d2464f960038`, illustrates why engine names are insufficient. Its Gemma4Renoise path disables radix caching and chunked prefill, rejects quantized loading and pipeline/context parallelism, and accepts only specified attention backends. Its recipe rejects grammar/logit-bias requests. Vendor low-precision performance claims do not override those implementation restrictions. Conversely, the source contains an attention-backend-specific graph path, so an older recipe's eager-only shorthand is not a timeless limitation. These are static source observations, not a successful local deployment test. [D26,D36][1P][FACT]

The strongest evidence supports conditional hypotheses, not a speed ranking. Google's own DiffusionGemma report describes a low-concurrency benefit while acknowledging lower overall quality and potentially higher serving costs. Earlier LLaDA results differ by task. Recent cache/verify work compares against particular diffusion baselines and does not establish an equivalent gain over an optimized AR service. Published evaluations also identify format, replanning and exploration failures in earlier models; those findings cannot be projected unchanged onto later releases. The durable conclusion is to compare matched-quality service frontiers, with explicit cache and commitment semantics. [B01–B05][1P][FACT, source-reported, not reproduced]; [D31–D32][2°][FACT]

## Source handoff for references

These are the principal reference targets for typeset citation integration. The retained text, exact quotes and revision-specific implementation URLs are in claims.json and source-manifest.json; no bibliography identifier in the shared manuscript has been changed.

- D01: Ho et al., *Denoising Diffusion Probabilistic Models*, https://arxiv.org/abs/2006.11239.
- D02: Song et al., *Score-Based Generative Modeling through Stochastic Differential Equations*, https://arxiv.org/abs/2011.13456.
- D03: Lipman et al., *Flow Matching for Generative Modeling*, https://arxiv.org/abs/2210.02747.
- D04: Liu et al., *Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow*, https://arxiv.org/abs/2209.03003.
- D05: Austin et al., *Structured Denoising Diffusion Models in Discrete State-Spaces*, https://arxiv.org/abs/2107.03006.
- D06: Sahoo et al., *Simple and Effective Masked Diffusion Language Models*, https://arxiv.org/abs/2406.07524.
- D07–D08, B01: *Large Language Diffusion Models*, https://arxiv.org/abs/2502.09992; https://github.com/ML-GSAI/LLaDA.
- D09: *Dream 7B*, https://arxiv.org/abs/2508.15487v1; https://github.com/DreamLM/Dream.
- D10–D11: *Fast-dLLM*, https://arxiv.org/abs/2505.22618; https://github.com/NVlabs/Fast-dLLM.
- D12: *dKV-Cache*, https://arxiv.org/abs/2505.15781.
- D13: *Block Diffusion*, https://arxiv.org/abs/2503.09573.
- D14: *Fast-dLLM v2*, https://arxiv.org/abs/2509.26328.
- D15–D17, B04: https://arxiv.org/abs/2602.08676; https://github.com/inclusionAI/LLaDA2.X; https://huggingface.co/inclusionAI/LLaDA2.2-flash.
- D18–D20, B02: https://huggingface.co/google/diffusiongemma-26B-A4B-it; https://blog.google/innovation-and-ai/technology/developers-tools/diffusion-gemma-faster-text-generation/.
- D21–D22, B03: https://www.inceptionlabs.ai/blog/introducing-mercury-3; https://docs.inceptionlabs.ai/capabilities/streaming; https://docs.inceptionlabs.ai/capabilities/structured-outputs.
- D23: https://deepmind.google/models/gemini-diffusion/.
- D24–D26,D36: pinned SGLang documentation, scheduler, algorithm and tests in source-manifest.json, revision `a1966e1b5d8b750b494d7e53cca1d2464f960038`.
- D27, B05: *Flash-dLLM*, https://arxiv.org/abs/2609.26796; https://github.com/VILA-Lab/Flash-dLLM.
- D28: *DFlash*, https://arxiv.org/abs/2602.06036.
- D31–D32: original external model evaluations https://arxiv.org/abs/2601.12979 and https://arxiv.org/abs/2601.15165; classified [2°] for the evaluated models under the book's taxonomy.
- D29–D30: local manuscript scope and cutoff evidence, preserved by path/line/hash in claims.json.
- D33–D34: analytical resource interpretation linked to inspected implementations; illustrative arithmetic reproduced by `python3 research/diffusion-20261028/calculate.py`.
