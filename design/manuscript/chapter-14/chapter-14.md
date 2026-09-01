# Chapter 14 — Benchmarking: Predicting Real Experience, Not a Leaderboard

## The Architect's Question

After this chapter we should be able to look at a benchmark result and judge whether it predicts what our users will actually experience. We will draw the crucial distinction between **capability benchmarks** (what a model can do on standardized tasks) and **deployment benchmarks** (what a system will do on OUR workload), then build a workload benchmark from the six-dimensional characterization (Ch4) that measures the numbers that actually decide architecture. After this chapter, "the model scores well on MMLU" is recognized as a weak claim — and "it meets our p95-TTFT SLO at 40 rps on our token profile" is a strong one.

## 1. Concept

Benchmarking fails most often because the wrong benchmark is used for the wrong decision. The fix is to separate two very different instruments:

1. **Capability benchmarks** — measure the model's output quality on standardized tasks (MMLU, GSM8K, HumanEval, MT-Bench, retrieval-QA suites). They answer: *is this model good enough at the skill our workload needs?* They do NOT tell us how fast, how cheap, or how it behaves under our traffic — model capability is the goal (Ch4's Quality dimension), never the bottleneck.

2. **Deployment benchmarks** — measure the *system's* behavior on a representative workload: TTFT, TPOT, throughput, goodput, KV-cache utilization, cost per request. They answer: *does this model-on-this-hardware meet the SLO at our traffic and token profile?* These are the numbers that actually pick the architecture.

The core insight: **a capability leaderboard is a poor proxy for serving performance.** Two models with identical MMLU can differ wildly in TTFT under the same batching, because serving depends on tokenizer, context length, KV layout, and scheduler — none of which a leaderboard scores. Benchmarks select models only after capability filters and deployment measurement both pass.

## 2. Mental Model

Think of capability benchmarks as **screening** and deployment benchmarks as **selection**. Screening answers "which models are even in the running?" cheaply and broadly. Selection answers "among the screened-in models, which system actually works for our workload?" expensively and precisely. The two-stage mental model prevents two classic errors:

- Screening with deployment metrics — e.g. benchmarking a model's MMLU to pick a serving stack. (Wrong tool.)
- Selecting with leaderboards — e.g. taking the top-scoring MMLU model and assuming it will meet our SLO. (Wrong tool, again.)

Just as important, we benchmark the **workload, not the model in the abstract.** A deployment benchmark that doesn't reproduce our token profile (input/output ratio, context length), our traffic (rps, concurrency, burst), and our SLO (percentiles) is measuring someone else's problem.

## 3. Worked Example

### Designing a Deployment Benchmark for the Canonical Workload

We build a deployment benchmark for the canonical enterprise-Q&A RAG workload (§14): ~10 rps average / 40 rps peak, ~9,200 input tokens (1,200 query + 8K retrieved) + ~300 output, TTFT budget 1.2 s, TPOT ~25 ms/token. [1P §14]

**Step 1 — representative queries.** We sample real user questions and run them through the rag pipeline to produce the actual prompt shapes, matching the ~9.2K-in / ~300-out token profile with the model's own tokenizer (not a heuristic). [2°]

**Step 2 — measurement protocol.** We load the candidate server with the same concurrency as our peak (~40 rps / ~100 concurrent equivalent) and record, across many requests:

- **TTFT** p50/p95/p99 (must be ≤ 1.2 s median, ≤ 2 s p95).
- **TPOT** p50/p95 (≤ ~25 ms median).
- **Goodput** — tokens/s that meet the SLO (Ch6), not raw throughput.
- **KV-cache utilization** and prefix-cache hit ratio (to validate the serving choices of Ch11).

**Step 3 — read the result.** Suppose candidate A (a 70B dense on 8×H100) shows p95 TTFT 1.9 s and goodput 9,800 tok/s at 40 rps concurrency — **meets** the canonical SLO. Candidate B (a smaller 7B) shows 0.6 s TTFT — much faster — but scores lower on the capability screen for the retrieval-QA quality threshold. We therefore *select* A for deployment (capability + deployment both pass), not B (capability fails despite speed). The benchmark did not score one number; it reproduced the decision. [2° DERIVED]

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

## 5. Common Mistakes

- **Citing a capability leaderboard as proof of serving fitness.** MMLU does not predict TTFT; it screens capability only.
- **Benchmarking a single request.** Real SLOs break under concurrency; a single-request benchmark hides the tail.
- **Mean-only latency reporting.** A 0.84 s mean hides a 5 s tail that breaches the p95 SLO (Ch6).
- **Using the wrong tokenizer estimate.** Under-counting context via the 4-char heuristic mis-sizes KV cache and prefill.
- **Optimizing raw throughput past the SLO window.** Bigger datch sizes raise tokens/s but push TTFT over the deadline, zeroing goodput (Ch6, Ch11).

## 6. Architecture Consequence

The benchmark is the bridge from candidate architectures (Ch12) to selection and then to TCO (Ch16):

- **Capability screen** narrows the candidate models (from Ch3/Ch5 model-selection) to those that meet the accuracy/quality threshold.
- **Deployment benchmark** then measures each surviving candidate under the canonical workload, producing the TTFT/goodput/cost numbers that drive the choice.
- **The chosen system** becomes the basis for the TCO and performance-engineering work of Ch15-16.

The benchmark is not a one-time event; it is the recurring production validation that catches drift (model updates, traffic shape changes, memory pressure) before they breach the SLO.

![Fig 14.1 — Capability screen then deployment benchmark [ILLUSTRATIVE conceptual]](figures/fig-14-1401.png)

*Fig 14.1 — Two-stage benchmarking: capability screen (which models qualify) → deployment benchmark (which system meets our SLO), feeding selection and TCO.*

<!-- Figure spec: mechanism-first flowchart; left box = candidate models → capability screen (MMLU/GSM8K/retrieval-QA) → surviving models → deployment benchmark against canonical workload (TTFT/goodput/KV) → selection + TCO; annotate the SLO gate. -->

## 7. What We Still Don't Know

- **How closely capability benchmarks predict enterprise Q&A quality** for a given domain is [VERIFY]; a custom retrieval-QA screen on real documents is stronger but costly.
- **Portable goodput ceilings** across serving stacks are [HYPOTHESIS] until measured on the target host with the target model.
- **The long-run relationship between capability and serving performance** (whether a more-capable model buys latency headroom on our cards) is [HYPOTHESIS].

## 8. End-of-Chapter Mini-Case

A team of skeptical engineers tells the architect: "The new model tops MMLU, we should just deploy it." Applying this chapter, the architect separates the claims. Yes, the model passes the capability screen for retrieval-QA quality. But the architect refuses to stop there: they build a deployment benchmark reproducing the canonical workload — real prompts at ~9.2K in / ~300 out, 40 rps concurrency, the 1.2 s/25 ms SLO — and measure the new model on the existing hardware. The result: the leaderboard-topping model has a wider output tokenizer and slower prefill, driving p95 TTFT to 2.6 s — breaching the SLO that the incumbent 70B met at 1.9 s. The team does not deploy the leaderboard winner. The architect's discipline — screen with capability, select with deployment — prevented a service degradation that a single MMLU score would have caused. The benchmark, done right, did not rank models; it predicted experience and saved the service.
