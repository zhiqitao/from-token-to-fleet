# Chapter 14 — Benchmarking: Predicting Real Experience, Not a Leaderboard

## The Architect's Question

After this chapter we should be able to look at a benchmark result and judge whether it predicts what our users will actually experience. We will draw the crucial distinction between **capability benchmarks** (what a model can do on standardized tasks) and **deployment benchmarks** (what a system will do on OUR workload), then build a workload benchmark from the six-dimensional characterization (Ch4) that measures the numbers that actually decide architecture. After this chapter, "the model scores well on MMLU" is recognized as a weak claim — and "it meets our p95-TTFT SLO at 40 rps on our token profile" is a strong one.

## 1. Concept

Benchmarking fails most often because the wrong benchmark is used for the wrong decision. The fix is to separate two very different instruments:

1. **Capability benchmarks** — measure the model's output quality on standardized tasks (MMLU, GSM8K, HumanEval, MT-Bench, retrieval-QA suites). They answer: *is this model good enough at the skill our workload needs?* They do NOT tell us how fast, how cheap, or how it behaves under our traffic — model capability is the goal (Ch4's Quality dimension), never the bottleneck.

2. **Deployment benchmarks** — measure the *system's* behavior on a representative workload: TTFT, TPOT, throughput, goodput, KV cache utilization, cost per request. They answer: *does this model-on-this-hardware meet the SLO at our traffic and token profile?* These are the numbers that actually pick the architecture.

The core insight: **a capability leaderboard is a poor proxy for serving performance.** Two models with identical MMLU can differ wildly in TTFT under the same batching, because serving depends on tokenizer, context length, KV layout, and scheduler — none of which a leaderboard scores. Benchmarks select models only after capability filters and deployment measurement both pass.

## 2. Mental Model

Capability benchmarks serve as **screening** and deployment benchmarks as **selection**. Screening answers "which models are even in the running?" cheaply and broadly. Selection answers "among the screened-in models, which system actually works for our workload?" expensively and precisely. The two-stage mental model prevents two classic errors:

- Screening with deployment metrics — e.g. benchmarking a model's MMLU to pick a serving stack. (Wrong tool.)
- Selecting with leaderboards — e.g. taking the top-scoring MMLU model and assuming it will meet our SLO. (Wrong tool, again.)

Just as important, we benchmark the **workload, not the model in the abstract.** A deployment benchmark that doesn't reproduce our token profile (input/output ratio, context length), our traffic (rps, concurrency, burst), and our SLO (percentiles) is measuring someone else's problem.

## 3. Worked Example

### Designing a Deployment Benchmark for the Canonical Workload

We build a deployment benchmark for the canonical enterprise-Q&A RAG workload (canonical scenario (Ch 4, Table 4-2)): ~10 rps average / 40 rps peak, ~9,200 input tokens (1,200 query + 8K retrieved) + ~300 output, TTFT budget (median ≤ 1.2 s, p95 ≤ 2 s), TPOT ~25 ms/token. [canonical scenario (Ch 4, Table 4-2)]

**Step 1 — representative queries.** We sample real user questions and run them through the rag pipeline to produce the actual prompt shapes, matching the ~9.2K-in / ~300-out token profile with the model's own tokenizer (not a heuristic). [2°]

**Step 2 — sweep the offered load, not a single point.** The analytical KV quotient C ≈ 17.5 gives at most 17 whole-context slots, not a deployable concurrency of 17.5. At the assumed 8.6-second execution time, 17/8.6 ≈ 1.98 req/s is a residency ceiling before headroom and competing resource limits. We sweep offered load and measure the tail rather than treating that ceiling as achieved capacity. An illustrative single-host sweep can cover 2, 4, 8, 12 and 16 active requests. Higher offered concurrency tests queueing or rejection; it does not imply that all requests are simultaneously resident. At each level we record:

- **TTFT** p50/p95/p99 (must be median ≤ 1.2 s, p95 ≤ 2 s).
- **TPOT** p50/p95 (≤ ~25 ms median).
- **Goodput** — tokens/s that meet the SLO (Ch6), not raw throughput.
- **KV cache utilization** and prefix-cache hit ratio (to validate the serving choices of Ch11).
- **Admission / rejection** — the offered-load level at which the server starts queueing or rejecting (the saturation knee).

The analytical ceiling sets the range of the sweep. The scenario's 40 req/s peak and assumed 8.6-second execution time imply about 344 executing requests fleet-wide, not resident requests on one host. Chapter 17 distinguishes the integer-slot planning minimum, occupancy headroom and spare capacity; those are not measured fleet capacity. The benchmark supplies the highest offered load that still meets the SLO. That measured SLO-goodput, not the analytical C/W, becomes the provisioning input.

**Step 3 — interpret a candidate result.** This example is hypothetical, not a measurement made for this book. Suppose candidate A (70B dense on 8×H100) passes the capability screen and achieves p95 TTFT 1.9 s at an illustrative offered load of 1.3 req/s, with the other request SLOs also satisfied. At the assumed 8.6-second execution time, the mean executing population is 1.3 × 8.6 ≈ 11.2 requests; a mean does not guarantee that bursts fit the 17-slot limit. Its prefill demand is 1.3 × 9,200 = 11,960 input tok/s. That lies below Chapter 8's approximately 19,800 input tok/s idealized prefill ceiling, but the ceiling alone cannot establish mixed prefill/decode goodput or tail latency. Suppose candidate B (7B) instead achieves p95 TTFT 0.6 s but fails the retrieval-QA quality threshold. A qualifies at the tested point; B does not. A's accepted operating point would then be an input to fleet sizing, not proof that one host serves the 40 req/s peak. [ILLUSTRATIVE][ASSUMPTION][UNMEASURED]

#### Table 14-1 — Capability vs deployment benchmarks

| Instrument | Answers | Example metrics | Picks | Risk if misused |
|---|---|---|---|---|
| Capability benchmark | is it good enough at the skill? | MMLU, GSM8K, HumanEval, retrieval-QA | which models qualify | using it to pick a serving stack |
| Deployment benchmark | does the system meet the SLO on our workload? | TTFT/TPOT p50-p99, goodput, KV util, $/request | which system to deploy | mistaking a leaderboard for this |

## 4. Measurement

Four habits make benchmarks trustworthy:

1. **Use the model's own tokenizer** on representative real prompts. The "4 chars ≈ 1 token" estimate can be 2-5× off for code/JSON/technical text (Ch6).
2. **Measure distributions, not means** — log p50/p90/p95/p99 for every latency metric and the full token-length distribution. A 32K-tail context is a different workload than a 9.2K average.
3. **Reproduce the concurrency and burst** — a benchmark must hit the model at our peak concurrency, not a single request, or it won't show the queuing and KV contention that break SLOs.
4. **Include goodput and cost, not just latency** — the SLO-windowed throughput and $/request complete the picture for the economics (Ch16).

These four habits are the standard. The guidance below applies them to each candidate change a deployment benchmark actually has to judge — a precision recipe, an iterative or media generation path, a serving backend, and a communication library. Each needs an explicit boundary: what is held constant on both sides, what counts as a completed result, and what counts as acceptable quality.

<a id="q-validation"></a>

### Acceptance test for a quantized deployment

The comparison is paired: one base-model revision, fixed tokenizer and prompt template, fixed decoding/reasoning budget, the same workload and the same hardware. The candidate differs by a documented precision recipe and its required kernel path. Calibration data are separate from test data. If a high-precision baseline was never published, that absence remains explicit; the experiment cannot establish loss relative to unavailable original weights. [DERIVED]

Accuracy is checked on the actual exported implementation. Reasoning tasks need verifiable answers under a fixed effort budget. Code tasks need execution and tests, not only syntactic validity. Tool tasks need correct tool selection, valid arguments, completed outcomes and a record of retries or unsafe actions. Multimodal tasks fix preprocessing and evaluate every affected modal branch. Long-context tests cover both retrieval and dependencies over position and generation length; weight precision and KV precision are varied separately. A favorable perplexity result does not establish all of these capabilities. These are acceptance criteria for the proposed experiment, not claims that a particular format passes them. [ILLUSTRATIVE][ASSUMPTION][UNMEASURED]

The load test keeps arrival traces, prompt/output distributions, parallelism and cache state fixed. It measures load peak, steady/reserved HBM, kernel selection, TTFT, inter-token latency, completion time, errors and task quality. A bounded first screen can use at least 200 paired examples per critical task and three repetitions per load point, but these are illustrative starting budgets, not proof of rare-failure or p99 reliability. Final sample sizes follow the predeclared degradation bound and statistical power. Only candidates that pass the quality gate enter a comparison of SLO-goodput and cost per successful task. [ILLUSTRATIVE][ASSUMPTION][UNMEASURED]

### Measure drafts, commitments and valid results separately

Iterative generation introduces more than one plausible "first token." A service can expose a provisional draft, commit an irreversible prefix or block, and later finish a valid response. Those are different events. A first-draft timestamp measures early visibility. A first-commit timestamp measures when a downstream consumer can safely act on text that will not be overwritten. Time to a validated answer includes any required schema checks, unit tests or task acceptance. Comparisons need the same boundary on both sides. [1P][FACT]; metric definitions [DERIVED]

Burst streaming also changes the meaning of inter-token latency. A runtime may deliver an entire block in one event and pause while refining the next block. Splitting that event into individual client tokens creates near-zero within-block gaps without shortening the pause between blocks. We therefore retain final-token throughput but add block size, block-arrival gaps, first-commit latency and end-to-end p95/p99 latency. [DERIVED]

The existing token SLO-goodput definition still counts only service-compliant final output. Provisional text that is overwritten is not extra useful output. A separate successful-request metric can count requests that pass all three gates — task validity, required quality and the service SLO — per unit wall time. This is an additional metric, not a silent redefinition of token goodput. If retries, fallback or tool execution belong to the service, their time and cost remain inside the boundary. [DERIVED]

A reproducible comparison freezes model and tokenizer revisions, sampler, thresholds, block size, cache policy, quantization and runtime commit. It uses a calibration set to choose operating points and a separate holdout set to evaluate them. Both sides receive reasonable optimizations: optimized AR KV/batching and, where available, a speculative baseline; the applicable diffusion cache, refresh and verification paths. Speed is compared only after the quality gate is met. [DERIVED]

We measure a warmed single request, a concurrency sweep and an open-loop offered-load sweep. The workload includes long prompts, code infilling, fixed-region editing and structured tool calls. The execution trace records evaluations, recomputed positions, verification and final committed tokens; the service trace records queueing, drafts, commitment, completion, failures and cancellation. Hardware-matched experiments can support resource-efficiency claims. A closed API whose hardware and internal schedule are unknown belongs in a separate service-level comparison, not a GPU-FLOP ranking. [DERIVED]

### A video benchmark is a workload tuple {#video-benchmark-contract}

A reproducible video result identifies the exact model and revision; task and conditioning; hardware model, count, and topology; precision and quantization; pixel dimensions; frames and frames/s; scheduler and timestep sequence; guidance; branch evaluations; engine commit and attention backend; cache and offload settings; and output-quality criteria. It also identifies the timing boundary. Seconds per denoising step, seconds for all sampling steps, and seconds to a finalized clip are not interchangeable. [DERIVED]

A primary report can still leave that tuple incomplete. HunyuanVideo-1.5 reports 5.5070 versus 2.9475 seconds per diffusion step for dense versus sparse attention at 720 × 1,280 pixels and 241 frames. Those measurements use eight H800 GPUs with context parallelism and a CFG-distilled model. Its separate 50-step table adds SageAttention, compilation, and feature caching, and reports 96.78 versus 58.39 seconds for the same shape. Neither table establishes a single-GPU service rate or a complete request-to-media latency.[^oct14-vg-h15] [1P][FACT]

LTX-2's report compares 22.30 seconds/step for Wan2.2-14B with 1.22 seconds/step for LTX-2. The stated context is an H100 GPU, 121 frames, a 720p label, single-step Euler, and CFG=1. It is not a matched-quality completed-clip comparison. Missing precision, exact pixel shape, engine revision, and per-run quality prevent a price-per-usable-clip conclusion. The appropriate response to incomplete evidence is a bounded deployment experiment, not a TFLOP-to-price conversion.[^oct14-vg-ltx] [1P][FACT]

The deployment experiment pairs fixed prompts and reference assets across explicitly declared recipes. Warm and cold runs remain separate. Quality evaluation includes prompt adherence, identity and object persistence, motion continuity, flicker, geometry and physical plausibility, text rendering, and, where applicable, lip synchronization and speaker assignment. Quality gates and failure categories are fixed before throughput is compared. Reduced steps, approximate caches, sparse attention, and quantization are tested as separate quality-performance points, not treated as identical work. [DERIVED]

### Two fair comparisons answer different questions

A hardware-isolation comparison holds the model revision, numerical representation, KV format, request distribution and functional features constant. This limits the claim to the tested common path. A deployment comparison can instead use each backend's best available implementation, but all candidates must first satisfy the same quality and service constraints. If one candidate uses a different representation or disables a feature, the result concerns a different complete configuration — not hardware alone. [DERIVED]

Both comparisons need cold and warm runs, separate prefill and decode observations, a load sweep, and per-request timing. Request goodput counts successful requests that satisfy quality and every request-level SLO. Token goodput counts the output tokens of those compliant requests over the same wall-clock interval. Timeouts, failed attempts and fallback work still consume resources. A p95 threshold is a configuration-level statistic; it is not itself a count of compliant work. An increase in raw tokens per second can therefore coexist with unchanged or lower goodput. [DERIVED]

Graph startup, cache warmth, host-side conversion and request isolation belong in the record. Reasoning workloads also need total generated-token counts and a fixed quality test. Fewer generated tokens can mean less work, not a faster implementation. These controls preserve the interpretation of Chapter 15's optimization map when the backend changes. This section states a comparison protocol and introduces no new measured performance claim. [DERIVED]

### A collective microbenchmark is not a serving-capacity claim

Collective microbenchmarks isolate one communication mechanism; they do not establish serving capacity. A deployment comparison preserves the layer shapes, precision, group mapping and arrival process, then measures device-completed work and SLO-goodput under contention. Cross-vendor tests compare complete systems unless hardware is controlled; they cannot isolate a library-only speedup. Chapter 9 supplies the correctness and traffic-accounting contract. [DERIVED]

## 5. Common Mistakes

- **Citing a capability leaderboard as proof of serving fitness.** MMLU does not predict TTFT; it screens capability only.
- **Benchmarking a single request.** Real SLOs break under concurrency; a single-request benchmark hides the tail.
- **Mean-only latency reporting.** A 0.84 s mean hides a 5 s tail that breaches the p95 SLO (Ch6).
- **Using the wrong tokenizer estimate.** Under-counting context via the 4-char heuristic mis-sizes KV cache and prefill.
- **Optimizing raw throughput past the SLO window.** Bigger batch sizes raise tokens/s but push TTFT over the deadline, zeroing goodput (Ch6, Ch11).

## 6. Architecture Consequence

The benchmark is the bridge from candidate architectures (Ch12) to selection and then to TCO (Ch16):

- **Capability screen** narrows the candidate models (from Ch3/Ch5 model-selection) to those that meet the accuracy/quality threshold.
- **Deployment benchmark** then measures each surviving candidate under the canonical workload, producing the TTFT/goodput/cost numbers that drive the choice.
- **The chosen system** becomes the basis for the TCO and performance-engineering work of Ch15-16.

The benchmark is not a one-time event; it is the recurring production validation that catches drift (model updates, traffic shape changes, memory pressure) before they breach the SLO.

![Fig 14.1 — Capability screen then deployment benchmark [ILLUSTRATIVE conceptual]](figures/fig-14-1401.png)

*Two-stage benchmarking: capability screen (which models qualify) → deployment benchmark (which system meets our SLO), feeding selection and TCO.*

<!-- Figure spec: mechanism-first flowchart; left box = candidate models → capability screen (MMLU/GSM8K/retrieval-QA) → surviving models → deployment benchmark against canonical workload (TTFT/goodput/KV) → selection + TCO; annotate the SLO gate. -->

## 7. What We Still Don't Know

- **How closely capability benchmarks predict enterprise Q&A quality** for a given domain is [UNRESOLVED]; a custom retrieval-QA screen on real documents is stronger but costly.
- **Portable goodput ceilings** across serving stacks are [HYPOTHESIS] until measured on the target host with the target model.
- **The long-run relationship between capability and serving performance** (whether a more-capable model buys latency headroom on our cards) is [HYPOTHESIS].

## 8. End-of-Chapter Mini-Case: Capability Screen vs. Deployment Benchmark

In this hypothetical mini-case, a team proposes a model because it tops MMLU. It also passes the task-specific retrieval-QA capability screen. The remaining question is deployment fitness. The comparison fixes prompt texts, output requirements, hardware, arrival trace and timing boundaries; each model uses its own tokenizer. A single-host load sweep establishes each replica's accepted operating point before the fleet is tested at the scenario's 40 req/s peak. The SLO remains median TTFT ≤ 1.2 s, p95 TTFT ≤ 2 s and median TPOT about 25 ms. Suppose the candidate generates more input tokens for the same prompt texts and the paired deployment test yields p95 TTFT 2.6 s, versus the incumbent's 1.9 s at that same offered load. Those are illustrative results, not book measurements. The candidate fails the latency gate despite passing the capability screen; diagnosis must separate token-count effects from implementation and queueing costs before a revised deployment is accepted. [ILLUSTRATIVE][ASSUMPTION][UNMEASURED]

[^oct14-vg-h15]: HunyuanVideo-1.5 Technical Report, arXiv:2511.18870, especially model architecture and §6 Tables 7–8. https://arxiv.org/html/2511.18870 . Official repository: https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5 . Retrieved 2026-10-28. Timing results are vendor-reported, not measurements made for this book.

[^oct14-vg-ltx]: LTX-2: Efficient Joint Audio-Visual Foundation Model, arXiv:2601.03233, architecture, §6.3/Table 1, limitations and conclusion. https://arxiv.org/html/2601.03233 . Retrieved 2026-10-28. Timing results are vendor-reported, not measurements made for this book.
