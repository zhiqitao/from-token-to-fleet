# Chapter 22 — How to Think Like an AI Solution Architect

## The Architect's Question

Before any model is selected, any GPU is counted, any latency budget is allocated, the architect must answer one question: *what is the actual token-scale cost of delivering the stakeholder's request?* This chapter exists to make that question automatic. We do not reach for vendor marketing numbers or rule-of-thumb heuristics. Instead we trace a vague stakeholder ask — "we need a Q&A system over our internal documents" — through a canonical loop that turns it into concrete architectural bounds. The output is a set of derived quantities (token throughput, KV-cache memory, prefill FLOPs, decode bandwidth) that are verifiable, derived from first principles, and grounded in the canonical ~2,000 user, ~10 rps / ~40 rps peak, RAG Q&A, 70B dense FP16 scenario that every other chapter in this handbook cites. We use a we-voice throughout: no shoulds, no musts. Only "we" — the architect and the system — and the reasoning that connects them.

## 1. Concept

The unit we price, size, and optimise is the **token**. We established what a token is in Chapter 1 — not a word, character, or byte, but whatever the model's tokenizer carves text into via learned byte-pair merging; that token counts are never proportional to character counts; and that “one token ≈ 4 characters” is a rough rule for general-English prose, to be confirmed against the *actual* tokenizer before pricing anything [Ch. 1 §1]. We do not restate that here; this chapter builds on it.

What Chapter 22 adds is not a re-derivation of the token but a **re-framing of it as the input to a decision loop**. The architect treats a token as a metered unit of thought — the way a kilowatt-hour meters electricity — not because one token is meaningful by itself, but because every downstream cost and capacity number is denominated in it. The durable mental model, unchanged from Chapter 1's: *tokens are the interface between a human's request and a machine's arithmetic, and anything we are asked to size or price reduces to “how many tokens, in what context, with what precision.”* The loop below turns that unit into concrete bounds.

## 2. Mental Model

Think of inference as two gears turning at different speeds. The prefill gear is large and toothed: it does a lot of work per revolution (many FLOPs), but it only turns once per request. The decode gear is small and smooth: it turns every token, doing relatively little work per step, but it keeps turning for every output token. The prefill gear is limited by how fast the compute engines can crank (FLOPS); the decode gear is limited by how fast data can be fed from memory (GB/s). When we ask "is this workload compute-bound or bandwidth-bound?" the answer depends entirely on which gear is doing the work.

A useful concrete image: prefill is like filling a bucket from a fire hose — a burst of high-rate flow that fills the entire capacity in one go. Decode is like drinking from that bucket one sip at a time — each sip is small, but we keep sipping until the bucket is empty. The hose is limited by pipe width (bandwidth); the sips are limited by cup size and swallowing rate (compute).

The architect's mental model, distilled: **tokens are the unit of measure; prefill and decode are opposite-bound processes that require different levers.** This distinction is the single biggest discriminator between an architecture that meets its SLOs and one that does not.

## 3. Worked Example — The Canonical Loop

We now demonstrate the canonical loop: turning a vague stakeholder ask into concrete bounds. The stakeholder says: *"We need a Q&A system over our internal documents. About 2,000 employees will use it, they'll ask questions throughout the day, and the answers should be accurate and fast."* From this single sentence we will derive a full set of token-scale quantities that every downstream chapter will price against.

**Step 1 — Identify the unit.** The ask mentions "Q&A over internal documents." We do not assume "one question = one page" or "one question = 500 words." We go to the model's tokenizer and ask: how many tokens does a typical prompt contain? We extract representative prompts from the documented corpus, run them through the tokenizer, and measure. In the canonical scenario, the prompt consists of ~1,200 tokens of query text plus ~8,000 tokens of retrieved RAG context, yielding **~9,200 input tokens**. The answer generated is ~300 tokens. These numbers are not assumed; they are measured [1P].

**Step 2 — Establish the traffic profile.** The ask says "about 2,000 employees" and "throughout the day." We instrument or survey to find the per-user rate. The canonical scenario settles on ~10 requests/s average, with peaks of ~40 rps. These are derived quantities [2° DERIVED], not stipulated.

**Step 3 — Compute the token throughput.** With $I = 9{,}200$ input tokens and $O = 300$ output tokens per request, and $\lambda = 10$ req/s average:

$$
\text{input tokens/s} = I \cdot \lambda = 9{,}200 \times 10 = 92{,}000 \text{ tokens/s}
$$

$$
\text{output tokens/s} = O \cdot \lambda = 300 \times 10 = 3{,}000 \text{ tokens/s}
$$

$$
\text{input/output ratio} = \frac{I}{O} = \frac{9{,}200}{300} \approx 30\times
$$

(At the ~40 req/s peak these rise to ~368,000 and ~12,000 tokens/s respectively.) [2° DERIVED]

**Step 4 — Derive architecture-relevant quantities.** The 30× input/output ratio is the single most important derived quantity here. It means this workload is input-heavy: the great majority of latency, memory, and energy is spent in prefill (processing the 9.2K prompt), not decode (generating the 300 answer tokens). This ratio alone dictates that KV-cache memory and prefill compute dominate the design — not decode bandwidth. Every downstream chapter (memory, compute, cost) will price against these derived numbers.

**Step 5 — Record in Table 22-1.** The full table of derived quantities appears below.

This loop — stakeholder ask → measured token counts → traffic profile → token throughput → architecture-relevant derived quantities — is the canonical thought process an AI solution architect runs, every time, before a single architecture decision is made. It is how we move from "we need a Q&A system" to "our prefill will be compute-bound at ~1.29 PFLOP per request, and our decode will be bandwidth-bound at ~5.6 TB/s per token." The loop is the chapter's central contribution; the quantities that issue from it are the evidence [1P]/[2°]/[VERIFY] that every following chapter trades on.

::: {#tab-22-1}
### Table 22-1 — Derived quantities from the canonical loop (worked example, not reference)

| metric | value | derivation |
|---|---|---|
| input tokens / request | ~9,200 | 1,200 prompt + 8K RAG context [1P DERIVED] |
| output tokens / request | ~300 | generated answer length [1P DERIVED] |
| input / output ratio | ~30× | 9,200 ÷ 300 [2° DERIVED] |
| input tokens/s @ 10 rps | ~92,000 | 9,200 × 10 [2° DERIVED] |
| input tokens/s @ peak 40 rps | ~368,000 | 9,200 × 40 [2° DERIVED] |
| output tokens/s @ 10 rps | ~3,000 | 300 × 10 [2° DERIVED] |
| output tokens/s @ peak 40 rps | ~12,000 | 300 × 40 [2° DERIVED] |
| prefill FLOPs per request | ~1.29 PFLOP | 2 × 70B × 9.2K ≈ 1.29 × 10¹⁵ [DERIVED] |
| decode bandwidth per token | ~5.6 TB/s | 140 GB weights / 25 ms TPOT [DERIVED] |
| KV-cache memory per request | ~12 GB (70B, 8-bit KV) | 1.3 MB/token × 9,200 tokens [1P DERIVED] |

:::

![Fig 22.1 - Prefill vs decode bottleneck divergence [2° DERIVED]](figures/fig-22-2201.png)

*Fig 22.1 — Prefill FLOPs grow sharply with context length (linear 2NL, red) and faster still once the quadratic attention term is added (orange band, +17% at 9.2K → ~2.4× at 128K); the 9.2K canonical point is marked. Prefill is compute-bound (~1.29 PFLOP/request → ~1.19 PFLOPS required at the ~1.08 s budget vs H100 ~0.989 PFLOPS peak). Decode is absent from this axis because it is a fixed ~140 GFLOP/token (~0.00014 PFLOP, ~9,000× below this axis' floor) and stays bandwidth-bound (Ch6): the two regimes are deliberately drawn on different resources. *

## 4. Measurement

For this chapter, measurement reduces to **counting tokens correctly**, because a miscount at the input silently misprices everything downstream. Three things an architect can and should check:

1. **Actual token count, not the rule of thumb.** Run the model's *own tokenizer* on representative prompts from the actual traffic. The "4 chars ≈ 1 token" heuristic is for estimation only; real counts differ by language, formatting, code, and tokenizer version. Measure on our traffic, not the marketing figure.

2. **Input vs output split.** Measure both legs of the request (prompt tokens and generated tokens), because they land on different bottlenecks — input on memory/prefill, output on decode — and on different cost line items. A request that is 90% input and 10% output has a very different cost profile than one that is 50/50, even at the same total token count.

3. **Peak vs average context.** Log the distribution of context lengths, not just the mean. A workload that averages 9.2K input tokens but peaks at 32K (illustrative variant) has a very different KV-cache and latency profile. The 90th-percentile context length is often the number the architect must design for.

This measurement habit is the token-layer answer to the book's recurring question, "what would I actually measure here?" We measure token counts and their distribution, at the edge, before any architecture decision is made.

## 5. Common Mistakes

- **Assuming one token ≈ one word.** It is a useful heuristic for general English prose and nothing more. Code, numerics, and non-Latin scripts routinely run 2–5× the naive estimate, which misprices capacity and cost.

- **Ignoring the input/output asymmetry.** Treating a request as "one unit" hides that input-heavy workloads are memory-bound and output-heavy ones are decode-bound — opposite bottlenecks with opposite fixes. The 30× input/output ratio in the canonical loop is the concrete illustration of this principle.

- **Quoting context window as free capacity.** The window is an upper bound, not a recommendation; using it fully is expensive. Keeping a 9.2K average inside a 128K window still costs for the length we actually use.

- **Trusting a vendor's tokenizer count without checking.** Tokenizer versions change and report differently; measure on *our* traffic, not the marketing figure.

- **Skipping the canonical loop.** Assuming that the stakeholder's description is sufficient to size the system. The loop exists because vague asks almost always underspecify the token-scale cost; skipping it produces architectures that fail latency or cost SLOs.

## 6. Architecture Consequence

The canonical loop's derived quantities have immediate and concrete architecture consequences. The 30× input/output ratio means this workload's prefill phase dominates: ~1.29 PFLOP of compute per request, and a KV-cache that grows with 9.2K input tokens. The decode phase, while smaller in total tokens, requires ~5.6 TB/s of HBM bandwidth per generated token — a bandwidth-bound design.

These opposite bottlenecks lead to a central architectural decision: **can we disaggregate prefill and decode?** If prefill needs FLOPS and decode needs bandwidth, a single homogeneous GPU pool is suboptimal. A two-pool architecture — a prefill cluster optimized for compute (more GPUs, higher FLOPS, model parallelism) and a decode cluster optimized for bandwidth (faster HBM, PagedAttention, continuous batching) — can achieve the same serving SLO with fewer total GPUs than a homogeneous design. This is the central theme of Chapter 11 (Serving) and Pattern 4 (Prefill/decode disaggregation). The architect who runs the canonical loop and records the derived quantities in Table 22-1 is already positioned to make this decision with numbers, not intuition.

Importantly, the loop does not end at a serving topology; it ends at a *decision about where the intelligence lives*. A 70B dense pool on the fleet is one placement; an 8-bit or MoE variant, a retrieval-first design that buys capability with context rather than parameters, a test-time-search loop that spends compute on hard queries, or an agent runtime that orchestrates several specialised models are all alternative placements of the same capability. The canonical loop's derived quantities — token throughput, KV footprint, prefill FLOPs, TCO — are precisely the numbers an architect uses to compare those placements. So the full hierarchy the loop supports is:

> Requirement → Workload → Intelligence (where the capability comes from) → System → Architecture → Fleet → **Decision**.

The **Decision** rung is where the loop's output is committed — an ADR, an owner, a review trigger (Chapters 25–26). Every earlier derived quantity exists to inform that final, committed decision, and Appendix A's closing question — *where should the intelligence live?* — is the architectural form of that same question, made explicit at the top of the hierarchy rather than hidden at the bottom.

## 7. What We Still Don't Know

This chapter's numbers lean on the same open questions the book raises at the
mechanism layer. Rather than restating them, we point to the fuller treatment:

- **Sustained HBM bandwidth for weight-read kernels** — discussed in Chapter 2 §7; the 3.35 TB/s H100 figure is a theoretical peak and real serving kernels may sustain less. [VERIFY HYPOTHESIS]
- **Prefill FLOP cost under continuous batching** — Chapter 2 §7; the 2 × params × tokens approximation ignores activation reuse across batched requests. [VERIFY HYPOTHESIS]
- **Effect of quantization on decode vs prefill** — Chapter 2 §7; quantization shifts both bottlenecks but the precise trade-off point is workload-dependent. [VERIFY HYPOTHESIS]
- **Cross-technology bandwidth numbers** — Chapter 2 §7; HBM3e and MI300X publish higher peaks, which move the GPU-count equation without changing the compute-bound vs bandwidth-bound classification. [2° FACT]

## 8. End-of-Chapter Mini-Case

The architect is still in the early design conversation about the internal Q&A tool described throughout this handbook. The team has settled on a 70B-class dense model for accuracy, and they have a rough traffic estimate: ~2,000 registered employees, each roughly as active as the canonical scenario (~10 requests/s average, peaks ~40 rps), with prompts of ~1,200 tokens of internal documents plus ~8K retrieved context and ~300 tokens of answer.

From the token layer alone, the architect can already state the hard numbers: each request carries ~9.2K input tokens and ~300 output tokens. At 10 rps average, the system must sustain ~92,000 input tokens/s in prefill and ~3,000 output tokens/s in decode. At 40 rps peak, those numbers jump to ~368,000 and ~12,000 respectively. The architect can also state the two opposite bottlenecks: prefill will be compute-bound (~1.29 PFLOP per request at 9.2K input), and decode will be bandwidth-bound (~5.6 TB/s required weight-read rate per token). The team's immediate architectural choice is whether to build a single homogeneous GPU cluster or to separate prefill and decode pools — the arithmetic from this chapter makes clear that a homogeneous design will be suboptimal for either bottleneck, and that the disaggregation option explored in Chapter 11 is worth evaluating early.

Before passing this workload to Chapter 23 (Memory), the architect locks in one more number: the tokens-per-request split. This is the currency every downstream chapter will price against, and it has already been established as ~9.2K input + ~300 output per request. The rest of the design — model fitting, memory budget, latency budget, cost — can now proceed in token-denominated terms.