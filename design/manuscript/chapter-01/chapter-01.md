# Chapter 1 — It All Starts With the First Token

## The Architect's Question

Before we can size a model, a context window, or a serving budget, we have to know what the input actually is. After this chapter we should be able to reason about an AI system's **smallest unit of cost and meaning** — the token — and to translate between human units (a sentence, a page, a word) and the machine unit every architecture decision is priced against. This is the first rung of the token→fleet spine: everything downstream (memory, compute, latency, cost) is ultimately a statement about *tokens*.

## 1. Concept

A **token** is the atomic unit of text that a language model reads and writes. It is not a word, not a character, and not a byte — it is whatever the model's *tokenizer* decided to carve the text into. A single token can be a whole word (`handbook`), a common subword (`hand`), a single character, a short punctuation+space pair, or in worst cases a fragment of a character.

The disconnection from human units is the first thing an architect has to internalize: **cost and capacity in an LLM are measured in tokens, not words or characters**, because every model operation — embedding lookup, attention arithmetic, KV-cache memory, decode time — prices by token. This chapter exists to make that switch automatic.

### Tokenization

Tokenization splits a string into an ordered list of integer IDs from the model's **vocabulary** (typically tens of thousands, up to ~256k entries). The split is data-driven: learned from a large corpus, byte-pair encoding (BPE) repeatedly merges the most frequent adjacent byte/subword pairs until the vocabulary is built, so the boundaries are wherever the corpus statistics happened to fall — not where a grammarian would put them. Two practical consequences follow. First, the mapping is looser than a perfect round-trip: the detokenizer reconstructs text deterministically, but the token boundaries themselves carry little semantic meaning — `architecture` and `architect` may or may not share a token depending on corpus frequency. Second, token counts are **not proportional to character counts in any fixed way**.[2°] A high-frequency English word is often one token ([1P] verifiable on most vendor tokenizer demos — e.g. common words like *the*, *we*, *run* render as single tokens); a rare technical term, a long digit string, or dense code is frequently several. The "one token ≈ 4 characters" rule of thumb is for rough estimation of general-English prose, never a law — we confirm against the model's own tokenizer before pricing anything.

### Context window

The **context window** is the maximum number of tokens the model can attend to in a single forward pass — the sum of the prompt (input) and the tokens it generates (output). It is a hard architectural constraint: exceed it and the request fails or must be truncated. Current-gen models commonly ship windows ranging from roughly 8K up to a million-plus tokens, varying by model and vendor ([2°] vendor model cards, e.g. 128K/1M+ windows as of 2026); the exact number is a fixed, checkable property of the model we choose — verify it on the card, never assume it from the family name. The context window is one of the first numbers we will be quoted, and one of the easiest to overcommit against, because it bounds memory and cost whether we use every token or not.

### Embeddings

Text enters the model as token IDs, but the model does arithmetic on vectors. An **embedding** is the learned dense vector that represents a token (or a position, or a subword context) in a high-dimensional space — typically 128 to a few thousand dimensions. Embeddings are the bridge between discrete tokens and continuous computation: nearby tokens (in a learned sense) map to nearby vectors, which is what lets attention and downstream layers do useful math.

For the architect the practical facts are: embeddings live in a lookup table sized `vocab × dim`, they account for a real but small slice of a model's parameter count (a 100k × 4096 table is ~0.4B params — a rounding error next to a 70B model, but not zero), and they are the first thing a *vocabulary mismatch* or a *re-tokenized prompt* can silently change.

### Attention

Attention is the mechanism by which each token's representation is recomputed as a weighted blend of the representations of all tokens before it in the context. The weights come from a similarity (query·key) between the *current* token and every *prior* token, normalized, and used to mix the value vectors. It is the mechanism that makes a model "pay attention to" relevant earlier tokens when producing the next one.

The architect-relevant fact: attention's cost scales **quadratically with context length** in the full-attention regime — the number of input×output position pairs grows as `L²`. That quadratic term is the single biggest reason context windows feel expensive, and it is the pivot for every optimization downstream (sparse/linear attention, KV caching, retrieval to keep context short).

One precision matters before the mental model hardens: the `L²` term is a **prefill** cost — it describes computing attention across all position pairs in one pass over the full input. During **decode**, each generated token attends once to the growing prefix, so the per-token step is a *linear* cost in context length, and the length shows up as a *growing KV-cache memory footprint* (per-token key/values) rather than as per-step compute. The practical read is therefore *"long context is quadratic in prefill compute, and linear-but-memory-growing in decode"* — a distinction as important as the quadratic fact itself, and one we return to in Chapter 2 (compute gears), Chapter 7 (memory arithmetic) and Chapter 8 (roofline). Keeping prefill and decode separate is what prevents the over-simple "long context = quadratic inference" once we optimize context in later chapters.

One architectural consequence to hold now: *which layers emit a per-token cache is a property of the attention architecture*, not the context length alone — dense attention emits a key/value per token on every layer, while hybrid/linear-attention layers (Mamba-style state, compressed latent attention) hold a state that does not grow with length. This is why "the KV problem" and its fixes are really a *model-architecture* question (Ch. 3) that lands as a *memory* question (Ch. 7) — and why the token layer is the right place to have met it. We only need the concept here; the mechanism inventory is Chapter 3's, the arithmetic Chapter 7's.

### KV cache as a concept

When the model generates one token at a time, it recomputes the same prefix repeatedly unless it saves the intermediate results. The **KV cache** (key–value cache) is the stored key and value tensors for every token in the context, so that generating the next token only computes attention against the new token rather than re-deriving the whole prefix. It is the reason "long conversations are expensive in memory, not just in compute."

KV cache size per token scales with

$$
KV_{\text{per-token}} = 2 \times n_\text{layers} \times d_\text{hidden} \times \text{bytes-per-value}
$$

(one key and one value per layer) — on the order of **~256 KB per token for a 7B-class model and ~1.3 MB per token for a 70B-class model** at 8-bit precision, so a long context (say 32K tokens) alone can be tens of GB of memory. A first non-obvious architectural lesson hides here: *model sparsity does not reduce the KV cache.* A Mixture-of-Experts model activates only a fraction of its neurons per token, which saves compute, but the attention layers still process every token densely and emit a key/value per token — so MoE shrinks compute-per-token, not memory-per-context. Only changing the *attention mechanism* (hybrid/linear attention, compressed latent attention) actually stops the cache from growing. This distinction — compute-sparsity vs memory-sparsity — is one an architect has to get exactly right, and it is why "the KV problem" is an attention-architecture question more than a model-size question (developed fully in Ch. 3 and Ch. 7). We deliberately keep this to concept + order of magnitude here; Chapter 7 (Memory) does the verified arithmetic against the canonical scenario.

![Fig 1.1 — The KV cache: every decoded token adds one K+V per layer per head [ILLUSTRATIVE conceptual]](figures/fig-01-kv-cache.png)

*Fig 1.1 — The KV cache: attention keeps every past token's key and value, so cache memory grows linearly with sequence length (concept; the verified arithmetic is Ch. 7's).*

## 2. Mental Model

Think of a token as a **metered unit of thought**, the way electricity is metered by the kilowatt-hour — important not because a single kilowatt-hour is meaningful by itself, but because *every* downstream cost and capacity number is denominated in it.

A useful image for the full pipeline:

![Fig 1.2 — How a token travels: text → tokenizer → IDs → embedding → attention → KV cache [ILLUSTRATIVE conceptual]](figures/fig-01-token-travel.png)

*Fig 1.2 — How a token travels. The token is the interface between a human's request and the machine's arithmetic: carved by the tokenizer, embedded into a vector, attended against past context, and remembered in the KV cache. (Concept; mechanism inventory in Ch. 3, arithmetic in Ch. 7.)*

> Text → **tokenizer** → discrete IDs → **embedding** → vectors → **attention** recomputes each token → **KV cache** remembers the prefix → generate one token at a time.

We do not need to hold all of this as a practitioner. The durable mental model is: **tokens are the interface between a human's request and a machine's arithmetic**, and *anything* we are asked to size or price in an LLM system reduces, one way or another, to "how many tokens, in what context, with what precision."

## 3. Worked Example

The canonical scenario (defined in the Architecture doc, §14 — one set of numbers every chapter cites) is an enterprise Q&A system: ~2,000 registered users, ~10 requests/s average, prompt of ~1,200 tokens plus ~8K retrieved context (~9.2K input), ~300-token output, on a 70B-class dense model. We reuse those numbers everywhere, so let us read one concrete property off them here.

*Worked example, not reference.* If average request is ~9.2K input + ~300 output ≈ **9.5K tokens** per request, and traffic is ~10 req/s, then the system ingests:

- **Input tokens/s**: 9,200 tokens/req × 10 req/s = **92,000 tokens/s** (peaks higher at ~40 req/s → ~368k).
- **Output tokens/s**: 300 × 10 = **3,000 tokens/s** output.
- Roughly **30× more input tokens than output tokens** in this workload (9.2K ÷ 300).

**Table 1-1** — Token throughput of the canonical workload (worked example, not reference).

| metric | value | derivation |
|---|---|---|
| input tokens / request | ~9,200 | §14 canonical (1,200 prompt + 8K context) |
| output tokens / request | ~300 | §14 canonical |
| input / output ratio | ~30× | 9,200 ÷ 300 [2° DERIVED] |
| input tokens/s @ 10 rps | ~92,000 | 9,200 × 10 [2° DERIVED] |
| input tokens/s @ peak 40 rps | ~368k | 9,200 × 40 [2° DERIVED] |
| output tokens/s @ 10 rps | ~3,000 | 300 × 10 [2° DERIVED] |

*(All figures trace to the §14 canonical scenario; none are measurement claims.)*

This ratio — input-heavy — is the *reason* memory (KV cache) and prefill dominate this system's cost rather than decode. We will not act on it here; Chapter 7 (Memory) and Chapter 8 (Compute) do. The point of the worked example in this chapter is to fix *the unit*: every one of those numbers is a statement about tokens, and we can now say it without translating from words or pages.

## 4. Measurement

For this concept chapter, measurement is about **counting tokens correctly**, because a miscount at the input silently misprices everything downstream. Three things an architect can actually check:

1. **Actual token count, not the rule of thumb.** Run the model's *own tokenizer* on representative prompts. The "4 chars ≈ 1 token" heuristic is for estimation only; real counts differ by language, formatting, code, and tokenizer version.
2. **Input vs output split.** Measure both legs of the request (prompt tokens and generated tokens), because they land on different bottlenecks — input on memory/prefill, output on decode — and on different cost line items.
3. **Peak vs average context.** Log the distribution of context lengths, not just the mean. A workload that averages 9.2K input tokens but peaks far higher (illustrative variant, say 32K) has a very different KV-cache and latency profile.

This measurement habit is the token-layer answer to the book's recurring question, "what would I actually measure here?" — we measure token counts and their distribution, at the edge, before any architecture decision is made.

## 5. Common Mistakes

- **Assuming one token ≈ one word.** It is a useful heuristic for general English and nothing more. Code, numerics, and non-Latin scripts routinely run 2–5× the naive estimate, which misprices capacity and cost.
- **Ignoring the input/output asymmetry.** Treating a request as "one unit" hides that input-heavy workloads are memory-bound and output-heavy ones are decode-bound — opposite bottlenecks with opposite fixes.
- **Quoting context window as free capacity.** The window is an upper bound, not a recommendation; using it fully is expensive. Keeping a 9.2K average inside a 128K window still costs for the length we actually use.
- **Trusting a vendor's tokenizer count without checking.** Tokenizer versions change and report differently; measure on *our* traffic, not the marketing figure.

## 6. Architecture Consequence

Whatever we learned here, file it under **"can I size an input before I buy capacity?"** Concretely, the decision this chapter enables is: *estimate tokens-per-second (input and output separately), and therefore tokens-per-second capacity and cost, before choosing a model or a serving configuration.* It is the load-bearing input to model selection (Ch. 5), the memory budget (Ch. 7), the compute budget (Ch. 8), and the token economics (Ch. 16). No downstream chapter runs without a token count to price against — this one gives us the unit.

## 7. What We Still Don't Know

*As of 2026-08:* tokenizer internals are rarely published in full, so exact per-token behavior for a given model is often only empirically observable, not specified ([VERIFY] — tokenizer construction details, e.g. exact BPE merge rules for commercial models, are not fully public). Whether a fully learned, near-optimal tokenization for *our* domain can beat the generic vocabulary by a repeatable, quantified margin is still an open, workload-dependent question. And the interaction between tokenizer choice and downstream reasoning quality is not yet crisply characterized — we flag it as an open area rather than a settled fact.

## 8. End-of-Chapter Mini-Case

*(Chains the continuous scenario — this is its first appearance.)*

An architect is pulled into an early-stage design conversation about a new internal Q&A tool. There is no model, no server, no budget — just the raw ask: "We have thousands of employees who want to ask questions over our internal documents." Before any architecture can be defended, we have to turn that vague desire into a *machine-denominated* statement.

from the token layer alone (which we worked through in this chapter), the architect can already establish: the unit is tokens; the request shape will be prompt + retrieved context + output; the workload is input-heavy; and the first number to lock down is tokens-per-request, because every downstream decision (which model fits, how much memory, what latency is possible) is priced against it. The specific sizing — turning "thousands of employees" into ~2,000 registered users, ~10 req/s, ~9.2K input tokens — is Chapter 4's job (workload anatomy). Here the point is narrower and sharper: *we can now speak the system's currency*, and that is a prerequisite for every architecture question that follows.
