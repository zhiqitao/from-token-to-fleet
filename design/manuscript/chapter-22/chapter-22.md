# Chapter 22 — How to Think Like an AI Solution Architect

## The Architect's Question

Before any model is selected, any GPU is counted, any latency budget is allocated, the architect must answer one question: *what is the actual token-scale cost of delivering the stakeholder's request?* This chapter exists to make that question automatic. We do not reach for vendor marketing numbers or rule-of-thumb heuristics. Instead we trace a vague stakeholder ask — "we need a Q&A system over our internal documents" — through a canonical loop that turns it into concrete architectural bounds. The output is a set of derived quantities (token throughput, KV cache memory, prefill FLOPs, decode bandwidth) that are verifiable, derived from first principles, and grounded in the canonical ~2,000 user, ~10 rps / ~40 rps peak, RAG Q&A, 70B dense FP16 scenario that every other chapter in this handbook cites. The reasoning is traced by the architect and the system investigating together.

## 1. Concept

The unit we price, size, and optimize is the **token**. We established what a token is in Chapter 1 — not a word, character, or byte, but whatever the model's tokenizer carves text into via learned byte-pair merging; that token counts are never proportional to character counts; and that “one token ≈ 4 characters” is a rough rule for general-English prose, to be confirmed against the *actual* tokenizer before pricing anything [Ch. 1 §1]. We do not restate that here; this chapter builds on it.

What Chapter 22 adds is not a re-derivation of the token but a **re-framing of it as the input to a decision loop**. The architect treats a token as a metered unit of thought — the way a kilowatt-hour meters electricity — not because one token is meaningful by itself, but because every downstream cost and capacity number is denominated in it. The durable mental model, unchanged from Chapter 1's: *tokens are the interface between a human's request and a machine's arithmetic, and anything we are asked to size or price reduces to “how many tokens, in what context, with what precision.”* The loop below turns that unit into concrete bounds.

## 2. Mental Model

The prefill/decode split is the figure the rest of the book builds on, and it was established in Ch 2 §2 (in the canonical operating point, long-prompt prefill is compute-bound — a large burst of FLOPs once per request — while low-batch decode is bandwidth-bound — a small amount of work repeated for every output token). Ch 22 does not re-derive that distinction; it uses it. What this chapter adds is the **reasoning loop**: the architect does not have to hold every quantity in their head, because the loop turns a vague ask into a small, ordered set of token-scale bounds that the downstream chapters price against. The mental model, distilled, is that **the loop is the discipline** — derive the unit, then the traffic, then the split, in that order, so every later number is anchored rather than guessed.

## 3. Worked Example — The Canonical Loop

We now demonstrate the canonical loop: turning a vague stakeholder ask into concrete bounds. The stakeholder says: *"We need a Q&A system over our internal documents. About 2,000 employees will use it, they'll ask questions throughout the day, and the answers should be accurate and fast."* From this single sentence we will derive a full set of token-scale quantities that every downstream chapter will price against.

**Step 1 — Identify the unit.** The ask mentions "Q&A over internal documents." We do not assume "one question = one page" or "one question = 500 words." We go to the model's tokenizer and ask: how many tokens does a typical prompt contain? We extract representative prompts from the documented corpus, run them through the tokenizer, and measure. In the canonical scenario, the prompt consists of ~1,200 tokens of query text plus ~8,000 tokens of retrieved RAG context, yielding **~9,200 input tokens**. The answer generated is ~300 tokens. These are the book's `[canonical scenario]` inputs (Ch 4, Table 4-3) — an author-defined illustrative workload, *not* a vendor-reported `[1P]` figure, so they are labeled `[canonical scenario][ASSUMPTION]`, not `[1P]`.

**Step 2 — Establish the traffic profile.** The ask says "about 2,000 employees" and "throughout the day." We instrument or survey to find the per-user rate. The canonical scenario settles on ~10 requests/s average, with peaks of ~40 rps. These are derived quantities [ILLUSTRATIVE][DERIVED], not stipulated.

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

(At the ~40 req/s peak these rise to ~368,000 and ~12,000 tokens/s respectively.) [ILLUSTRATIVE][DERIVED]

**Step 4 — Derive architecture-relevant quantities.** The 30× input/output ratio is one of the most important derived quantity here. It means this workload is input-heavy: the token budget is dominated by prefill (processing the 9.2K prompt), not decode (generating the 300 answer tokens). Combined with the canonical model, precision, serving, and SLO assumptions, this 30× ratio pushes the design toward high prefill compute and KV-capacity pressure. The ratio alone does not settle which resource dominates — that also depends on model architecture, attention/KV-head count, precision, batching, hardware, kernel efficiency, prefix caching, and output-generation speed — but under the canonical assumptions the prefill-compute and KV-capacity terms are where the pressure lands, not decode bandwidth. Every downstream chapter (memory, compute, cost) will price against these derived numbers.

**Step 5 — Record in Table 22-1.** The full table of derived quantities appears below.

This loop — stakeholder ask → measured token counts → traffic profile → token throughput → architecture-relevant derived quantities — is the canonical thought process an AI solution architect runs, every time, before a single architecture decision is made. It is how we move from "we need a Q&A system" to "at the canonical operating point our prefill will be compute-bound at ~1.29 PFLOP per request, and our decode will be bandwidth-bound at a required weight-read rate of ~5.6 TB/s over each ~25 ms token interval." The loop is the chapter's central contribution; the quantities that issue from it are the evidence [1P]/[2°]/(to be verified) that every following chapter trades on.

::: {#tab-22-1}
### Table 22-1 — Derived quantities from the canonical loop (worked example, not reference)

| metric | value | derivation |
|---|---|---|
| input tokens / request | ~9,200 | 1,200 prompt + 8K RAG context [canonical scenario][ASSUMPTION] |
| output tokens / request | ~300 | generated answer length [canonical scenario][ASSUMPTION] |
| input / output ratio | ~30× | 9,200 ÷ 300 [canonical scenario][DERIVED] |
| input tokens/s @ 10 rps | ~92,000 | 9,200 ×10 [ILLUSTRATIVE][DERIVED] |
| input tokens/s @ peak 40 rps | ~368,000 | 9,200 ×40 [ILLUSTRATIVE][DERIVED] |
| output tokens/s @ 10 rps | ~3,000 | 300 ×10 [ILLUSTRATIVE][DERIVED] |
| output tokens/s @ peak 40 rps | ~12,000 | 300 ×40 [ILLUSTRATIVE][DERIVED] |
| prefill FLOPs per request | ~1.29 PFLOP | 2 ×70B × 9.2K ≈ 1.29 ×10¹⁵ [DERIVED] |
| decode weight-read per token | ~140 GB | full-weight-read model (70B FP16) [ILLUSTRATIVE][DERIVED] |
| decode required BW rate | ~5.6 TB/s | ~140 GB / 25 ms TPOT (= traffic / decode interval) [ILLUSTRATIVE][DERIVED] |
| KV cache memory per request | ~24.1 GB (9.2K, FP16) / ~24.9 GB (9.5K max) | 2.62 MB/token × 9,200 / 9,500 tokens [ILLUSTRATIVE][DERIVED]; *(sensitivity: at 8-bit KV the same 9.2K context falls to ~12 GB under ideal byte-halving (2.62→1.31 MB/token); the measured FP8 constant is ~1.42 MB/token (54% of BF16, [S6]) giving ~13.4 GB — the 1.31 vs 1.42 MB/token distinction is the nominal-halving vs measured-FP8 difference used elsewhere in the book)* |

:::

![Fig 22.1 - Prefill vs decode scaling as context grows; two panels (different units, NOT directly comparable). LEFT = PREFILL PER REQUEST (linear 2NL, quadratic 4·n_layers·L²·d, total): the quadratic attention term dominates at long context (≥ ~32K). RIGHT = DECODE PER TOKEN (fixed 2N ≈ 1.4e-4 PFLOP/token, flat across context). The quadratic term is the textbook 4·n_layers·L²·d and matches Chapter 8 [ILLUSTRATIVE][DERIVED]](figures/fig-22-2201.png)

*For standard full attention, attention work scales quadratically with sequence length while the MLP/projection portion stays roughly linear, so total prefill compute becomes increasingly dominated by the quadratic attention term as context grows (the 9.2K canonical point is marked; +17% at 9.2K → ~2.4× at 128K). Prefill is compute-bound (~1.29 PFLOP/request → ~1.19 PFLOPS required at the ~1.08 s budget vs H100 ~0.989 PFLOPS peak). The decode series is FLOPs per generated token, and is not literally flat: attending over an increasingly long KV cache carries context-length-dependent work and traffic, so per-token decode cost grows with generated-token index/context (relegated to a narrow band here; see Chapter 8). Note the aggregation units differ per series: the two prefill series are FLOPs *per request* (whole-context), the decode series is FLOPs *per generated token* (~140 GFLOP/token, independent of context length at the decoding step considered) — this is why the y-axis is labeled generically "Compute (PFLOP; see series definition)". The two regimes remain deliberately separate: decode lands in the bandwidth-bound regime at low batch (Ch6), prefill in the compute-bound regime at long prompt (Ch8) — each an operating-point property, not an identity.*

## 4. Measurement

For this chapter, measurement reduces to **counting tokens correctly**, because a miscount at the input silently misprices everything downstream. Three things an architect can and should check:

1. **Actual token count, not the rule of thumb.** Run the model's *own tokenizer* on representative prompts from the actual traffic. The "4 chars ≈ 1 token" heuristic is for estimation only; real counts differ by language, formatting, code, and tokenizer version. Measure on our traffic, not the marketing figure.

2. **Input vs output split.** Measure both legs of the request (prompt tokens and generated tokens), because they land on different bottlenecks — input on memory/prefill, output on decode — and on different cost line items. A request that is 90% input and 10% output has a very different cost profile than one that is 50/50, even at the same total token count.

3. **Peak vs average context.** Log the distribution of context lengths, not just the mean. A workload that averages 9.2K input tokens but peaks at 32K (illustrative variant) has a very different KV cache and latency profile. The 90th-percentile context length is often the number the architect must design for.

This measurement habit is the token-level answer to the book's recurring question, "what would I actually measure here?" We measure token counts and their distribution, at the edge, before any architecture decision is made.

## 5. Common Mistakes

- **Assuming one token ≈ one word.** It is a useful heuristic for general English prose and nothing more. Code, numerics, and non-Latin scripts routinely run 2–5× the naive estimate, which misprices capacity and cost.

- **Ignoring the input/output asymmetry.** Treating a request as "one unit" hides that input-heavy workloads tend toward high prefill compute and KV-capacity pressure, while output-heavy ones are decode-bound (run-time per generated token) — opposite bottlenecks with opposite fixes. (Note: "capacity pressure" is a memory-*capacity* constraint, not a memory-*bandwidth* bound; see Ch 4/8.) The 30× input/output ratio in the canonical loop is the concrete illustration of this principle.

- **Quoting context window as free capacity.** The window is an upper bound, not a recommendation; using it fully is expensive. Keeping a 9.2K average inside a 128K window still costs for the length we actually use.

- **Trusting a vendor's tokenizer count without checking.** Tokenizer versions change and report differently; measure on *our* traffic, not the marketing figure.

- **Skipping the canonical loop.** Assuming that the stakeholder's description is sufficient to size the system. The loop exists because vague asks almost always underspecify the token-scale cost; skipping it produces architectures that fail latency or cost SLOs.

## 6. Architecture Consequence

The canonical loop's derived quantities have immediate and concrete architecture consequences. The 30× input/output ratio means this workload's prefill phase dominates: ~1.29 PFLOP of compute per request, and a KV cache that grows with 9.2K input tokens. The decode phase, while smaller in total tokens, requires a weight-read rate of ~5.6 TB/s sustained over each ~25 ms decode step (the ~140 GB weight-read interval), against one GPU's ~3.35 TB/s — a bandwidth-bound design at low batch. (Note the units: 5.6 TB/s is a *rate*; the *per-token weight traffic* is ~140 GB under the full-weight-read model, and rate = traffic / TPOT.)

These opposite bottlenecks lead to a central architectural decision: **can we disaggregate prefill and decode?** If prefill needs FLOPS and decode needs bandwidth, a single homogeneous GPU pool is suboptimal. A two-pool architecture — a prefill cluster optimized for compute (more GPUs, higher FLOPS, model parallelism) and a decode cluster optimized for bandwidth (faster HBM, PagedAttention, continuous batching) — is an architecture worth benchmarking. Whether it needs fewer GPUs than a homogeneous design depends on achievable utilization, duplicated model residency, KV-transfer cost, interconnect topology, workload shape, burstiness, and the hardware assigned to each pool — those effects must be measured before the GPU-count conclusion is drawn. This is the central theme of Chapter 11 (Serving) and Pattern 4 (Prefill/decode disaggregation). The architect who runs the canonical loop and records the derived quantities in Table 22-1 is already positioned to make this decision with numbers, not intuition.

Importantly, the loop does not end at a serving topology; it ends at a *decision about where the intelligence lives*. A 70B dense pool on the fleet is one placement; an 8-bit or MoE variant, a retrieval-first design that buys capability with context rather than parameters, a test-time-search loop that spends compute on hard queries, or an agent runtime that orchestrates several specialized models are all alternative placements of the same capability. The canonical loop's derived quantities — token throughput, KV footprint, prefill FLOPs, TCO — are precisely the numbers an architect uses to compare those placements. So the full hierarchy the loop supports is:

> Requirement → Workload → Intelligence (where the capability comes from) → System → Architecture → Fleet → **Decision**.

The **Decision** rung is where the loop's output is committed — an ADR, an owner, a review trigger (Chapters 25–26). Every earlier derived quantity exists to inform that final, committed decision, and Appendix A's closing question — *where should the intelligence live?* — is the architectural form of that same question, made explicit at the top of the hierarchy rather than hidden at the bottom.

## 7. What We Still Don't Know

This chapter's numbers lean on the same open questions the book raises at the
mechanism layer. Rather than restating them, we point to the fuller treatment:

- **Sustained HBM bandwidth for weight-read kernels** — discussed in Chapter 2 §7; the 3.35 TB/s H100 figure is a theoretical peak and real serving kernels may sustain less. (a hypothesis awaiting verification)
- **Prefill FLOP cost under continuous batching** — Chapter 2 §7; the 2 × params × tokens approximation ignores activation reuse across batched requests. (a hypothesis awaiting verification)
- **Effect of quantization on decode vs prefill** — Chapter 2 §7; quantization shifts both bottlenecks but the precise trade-off point is workload-dependent. (a hypothesis awaiting verification)
- **Cross-technology bandwidth numbers** — Chapter 2 §7; HBM3e and MI300X publish higher peaks, which move the GPU-count equation without changing the compute-bound vs bandwidth-bound classification. [ILLUSTRATIVE][DERIVED]

## 8. End-of-Chapter Mini-Case: The Token-to-Fleet Thought Loop

The architect is still in the early design conversation about the internal Q&A tool described throughout this handbook. The team has settled on a 70B-class dense model for accuracy, and they have a rough traffic estimate: ~2,000 registered employees, each roughly as active as the canonical scenario (~10 requests/s average, peaks ~40 rps), with prompts of ~1,200 tokens of internal documents plus ~8K retrieved context and ~300 tokens of answer.

From the unit-and-token work of Ch 1 alone, the architect can already state the hard numbers: each request carries ~9.2K input tokens and ~300 output tokens. At 10 rps average, the system must sustain ~92,000 input tokens/s in prefill and ~3,000 output tokens/s in decode. At 40 rps peak, those numbers jump to ~368,000 and ~12,000 respectively. The architect can also state the two opposite bottlenecks: prefill will be compute-bound (~1.29 PFLOP per request at 9.2K input), and decode will be bandwidth-bound (a ~140 GB/token weight-read requiring ~5.6 TB/s sustained over the ~25 ms decode interval). The team's immediate architectural choice is whether to build a single homogeneous GPU cluster or to separate prefill and decode pools — the arithmetic from this chapter makes clear that a homogeneous design will be suboptimal for either bottleneck, and that the disaggregation option explored in Chapter 11 is worth evaluating early.

Before passing this workload to Chapter 7 (Memory), where the KV and residency arithmetic is built, the architect locks in one more number: the tokens-per-request split. This is the currency every downstream chapter will price against, and it has already been established as ~9.2K input + ~300 output per request. The rest of the design — model fitting, memory budget, latency budget, cost — can now proceed in token-denominated terms.