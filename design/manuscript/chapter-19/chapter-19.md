# Chapter 19 — Agentic Systems

## The Architect's Question

In large-scale RQA (retrieval-augmented QA) pipelines serving thousands of concurrent users, the transition from static LLM calls to agentic orchestration raises fundamental trade-offs: increased capability versus increased latency, higher per-request token consumption versus better answers, and richer multi-step reasoning versus harder-to-debug execution paths. This chapter addresses the architect's central question: how to design agentic layers that amplify intelligence without unsustainably inflating cost and latency.

We begin from the canonical deployment scenario (Ch 4, Table 4-2): ~10 requests/second average and ~40 requests/second peak. Each request carries ~9,200 input tokens and produces ~300 output tokens. The base model is a 70B dense FP16 engine running on 8×H100 GPUs (640 GB total memory). The agentic layer sits above this foundation, introducing tool use, retrieval, and multi-step reasoning. The question we answer is how much additional overhead this layer introduces, whether the quality gain justifies the cost, and how to size the infrastructure accordingly.

## 1. Concept

An agentic system is one in which the LLM does not merely complete a single prompt but iteratively decides which actions to take — calling tools, querying databases, running checks, and then reasoning about the results before producing a final answer. The core idioms are:

- **Tool use**: The model emits a structured call (often JSON) to invoke an external function — a search API, a database query, a code interpreter, or a guardrail validator.
- **Retrieval**: Within each turn, the agent may trigger a vector search, re-rank results, and feed the top-k passages back into the prompt.
- **Multi-step reasoning**: The agent maintains an internal “thought” chain, appending each new observation and its interpretation before deciding on the next action.
- **Guardrails**: Pre- and post-hoc checks that validate whether the model's intended action is safe, on-topic, or within budget.

The agent loop terminates when a stop condition is met: a final answer is emitted, a maximum turn count is exceeded, or a guardrail blocks further progress. This design pattern replaces the “single-shot” prompt — one LLM call, one response — with a dynamic sequence of calls whose length is data-dependent.

The architect must decide not only which tools the agent may call but also how to instrument each call for latency and token accounting, and how to set termination thresholds so that the system degrades gracefully under load.

## 2. Mental Model

The mental model we adopt visualizes the agent as a state machine with four recurring states: **Plan**, **Execute**, **Observe**, and **Decide**. In each cycle:

1. **Plan**: The model reads the current context (original user query + accumulated observations) and emits a plan — either “proceed with final answer” or “call tool X with parameters Y.”
2. **Execute**: The system routes the tool call to the appropriate backend, waits for results, and formats them back into text.
3. **Observe**: The result text is appended to the conversation history, and the token count is updated.
4. **Decide**: The model evaluates whether the observation resolves the user query or whether another cycle is needed.

This loop is deterministic in structure but data-dependent in length. A simple query (“What is the capital of France?”) may terminate after one Observe, while a complex RQA request (“Compare the performance of Model A on dataset X against Model B on dataset Y, using the last three papers from arXiv as evidence”) may traverse three or more cycles.

The critical insight for capacity planning is that each cycle incurs a fixed overhead: one LLM inference turn plus any tool-call latency. The variable portion is the number of cycles the model chooses. Our mental model therefore separates *fixed cost per turn* from *variable turn count*, and we will quantify both in the next section.

![Fig 19.1 — The agent loop is a four-state machine (Plan, Execute, Observe, Decide) whose turn/token budget, not the model's judgment, prevents an infinite loop. Assumption: an append-only context from the 9,200-token prompt at 2.62 MB/token KV, each depicted path a counterfactual completion, status [ILLUSTRATIVE]. Caveat: real systems add guardrails, compaction and fallbacks not shown here.](figures/fig-19-1901.png)

## 3. Worked Example

Take a user query routed to an agentic RQA pipeline. The pipeline’s default policy is a maximum of 4 turns; if the model has not terminated by then, the system returns a fallback answer “I’m sorry, I couldn’t find a definitive answer within the allowed reasoning steps.” (**Scope note on the turn cap.** This worked example uses a *default* cap of 4 to illustrate the binding worst case and the token-amplification curve out to T = 4. The *recommended operational* policy — deployed in the §8 mini-case and used for fleet sizing in Chapter 17 — caps turns at 3, per the §4 guidance and the 95th-percentile sizing rule; the 2% of requests that exceed the limit fall back to single-shot. Table 19-1's "T = 4 (over cap)" column is therefore an *out-of-policy bounding* case, not an in-policy turn count.)

**Turn 0 (initial prompt)**:

- Input: 9,200 tokens (user query + retrieved passages)
- Model emits a tool-call: `search(query="relevant concepts")`
- System routes the call to the search backend, returns top-5 passages (≈ 800 tokens of snippets)
- Total tokens after Turn 0: 9,200 + 800 = 10,000

**Turn 1**:

- Input: 10,000 tokens (history + new passages)
- Model emits a second tool-call: `db_query(sql="SELECT ... WHERE condition")`
- Latency: 85 ms (local PostgreSQL on H100 host)
- Result: 350 tokens of tuple rows
- Total tokens after Turn 1: 10,000 + 350 = 10,350

**Turn 2**:

- Input: 10,350 tokens
- Model decides to synthesize: emits a final answer
- Output: 300 tokens
- Conversation ends

**Token accounting**:

- Base single-shot: 9,200 input + 300 output = 9,500 tokens
- Agentic: 10,350 input + 300 output = 10,650 tokens
- Amplification factor: 10,650 / 9,500 ≈ 1.12× (this specific hand-worked trace, tool outputs 800 + 350; the per-turn convention of §4/Table 19-1 — δ=800 + γ=65 per turn — gives α(T=2) = (9,500 + 2×865)/9,500 = 11,230/9,500 ≈ 1.18× — different conventions, not a discrepancy)

A harder query that exhausts all 4 turns is the upper-bound case. Using the chapter's per-turn convention (each turn adds δ≈800 tokens of retrieved context plus γ≈65 tokens of model-generated reasoning), the token trajectory grows approximately linearly: after *k* turns, total input tokens ≈ 9,200 + k·(800+65), and total output ≈ 300 (final answer) plus the intermediate reasoning (≈65 tokens per turn). After 4 turns, input ≈ 9,200 + 4×800 + 4×65 = 12,660 tokens, output ≈ 300 tokens, giving a total of ~12,960 tokens. The amplification factor vs. single-shot is 12,960 / 9,500 ≈ 1.36×.

This worked example demonstrates that the cost increase is moderate for short reasoning paths but compounds as the agent loops deeper. The architect must weigh the probability of deep loops against the budget per request.

## 4. Measurement

To plan capacity and set budgets, we derive three quantities from the example above and the illustrative turn distribution below. A production deployment must estimate these quantities from its own telemetry.

First, a scoping note that matters more than any single number: a production agent turn is **not** guaranteed to be exactly "one LLM inference + one tool call." A turn may contain zero or more model invocations, parallel or chained tool calls, retrieval + reranking, model-generated reasoning, tool output, context compaction, or cached prefixes. Treating "1 turn = 1 LLM call + 1 tool call" is a *simplified execution model*, useful for first-pass arithmetic but not the general agent model. A more faithful capacity model is an **execution trace**: request → model invocation(s) → tool invocation(s) → observation(s) → model invocation(s) → final response, with its own token and latency totals. The amplification framework below (token *α*, latency *β*) is one concrete, simplified instantiation of that trace — it is what an architect can compute before instrumenting a real system, and it must be validated against measured traces afterwards.

### Per-agent-turn token amplification

Let *T* be the number of agent turns and *I₀* the initial input tokens (9,200 in our scenario). Each turn adds *δ* tokens of retrieved context and *γ* tokens of model-generated reasoning. The total token count after *T* turns is:

$$
\text{Total}(T) = (I_0 + T \cdot \delta + T \cdot \gamma) + O_\text{final}
$$

where $O_\text{final}$ is the final output (≈300 tokens). The per-turn amplification *α* is the ratio of total tokens to the single-shot baseline $I_0 + O_\text{final}$:

$$
\alpha(T) = \frac{I_0 + T\cdot\delta + T\cdot\gamma + O_\text{final}}{I_0 + O_\text{final}}
$$

With *δ* = 800, *γ* = 65, $O_\text{final}$ = 300, and *T* = 3:

$$
\alpha(3) = \frac{9{,}200 + 3\cdot800 + 3\cdot65 + 300}{9{,}200 + 300} = \frac{9{,}200 + 2{,}400 + 195 + 300}{9{,}500} = \frac{12{,}095}{9{,}500} \approx 1.27\times
$$

For *T* = 4: α(4) ≈ 1.36× as computed in the worked example. In production, the distribution of *T* depends on query complexity. Consistent with the mini-case telemetry in §8 (68% T = 1, 25% T = 2, 5% T = 3, 2% fallback), the illustrative turn distribution here has median *T* = 1, 90th percentile *T* = 2, and 95th percentile *T* = 3 [ILLUSTRATIVE][ASSUMPTION] — derived from the §8 distribution.

**What α does and does not measure.** *α* measures **retained/accumulated task context** under the simplified turn model — the unique content that must be held (and, absent compaction, resent as context) as the conversation grows. It is **not** the total model-processed or API-billed token multiplier: if the model is invoked repeatedly on the growing prefix, that retained context may be counted in *multiple* input calls, and the per-call outputs must be counted separately. So α ≈ 1.27× at *T* = 3 says the *context* is ~27% larger than single-shot — it does *not* say the task costs 1.27× the API spend or 1.27× the prefill FLOPs. Compute actual task tokens by summing the inputs and outputs of every model invocation, with cached-token accounting recorded separately:

$$\text{task\_input} = \sum_i \text{input}(call_i), \qquad \text{task\_output} = \sum_i \text{output}(call_i)$$

with `cached`, `uncached`, and `billed` token quantities recorded separately (a prefix-cache hit means a call's input is not re-processed from scratch, so billed/FLOP input differs from context-carried input). **Boundary rule.** A call's *input* never contains output tokens, so `task_input` must sum per-call inputs only — never the “Total tokens (incl. 300 output)” column (10,365 / 11,230 / 12,095 / 12,960 are *retained context + final output*, i.e. the α and Ch 17 KV quantities). The event-level ledger below derives `task_input`, `task_output`, peak residency, and billed tokens for the T = 3 trace under a stated cache policy. Concurrency/queueing and economics follow the call-trace totals, not α.

**Token-quantity definitions (distinct terms, used consistently).** The five quantities below are different and must not be collapsed:

| Term | Definition | Example (T = 3, δ = 800, γ = 65, $O_\text{final}$ = 300) |
|---|---|---|
| `req_in`, `req_out` | tokens of the single-shot baseline request | 9,200 input + 300 output = 9,500 |
| `newly_generated_output` | tokens the model *produces as output* in a call (final answer + per-turn reasoning γ) | last call 300; each reasoning pass ~65 |
| `retained_history` | prior turns' context carried into the current call's *input* (the grown prefix) | the synthesis call carries 12,095 − 300 = 11,795 as its input prefix |
| `current_input_length` | the full input of a given call (retained history + new retrieval δ + prompt) | synthesis-call input = 9,200 + 3×(800+65) = 11,795; request total incl. $O_\text{final}$ = 12,095 |
| `task_input / task_output` | Σ over all calls of input / output tokens (the execution-trace totals) | uncached task_input = 41,990; task_output = 495 (ledger below) |
| `cached / uncached / billed` | fraction of task_input served by prefix cache vs re-processed; billed per provider rules | a cache hit makes billed input smaller than task_input |

**Event-level call ledger (T = 3, δ = 800, γ = 65, $O_\text{final}$ = 300).** Under the chapter's per-turn convention each agent turn is one model invocation that emits γ reasoning *and* a tool call, the tool returns δ, and a terminal synthesis call reads the grown context and emits $O_\text{final}$ — so T = 3 agent turns (3 tool round-trips) is **4 model invocations**, exactly the §4 scoping note that “1 turn = 1 LLM call + 1 tool call” is a simplified execution model. (§3's hand-worked trace is a still simpler illustration that counts only tool outputs; the α, Table 19-1, and Ch 17 arithmetic uses the per-turn convention below, which also retains γ — the §6 append-only policy, condition (iii).) Every row is one event, and input and output never mix:

| Call (event) | Input before call | New model output | Tool output | Post-call retained context |
|---|---|---|---|---|
| 1 — turn 1 | 9,200 | 65 (γ₁) | 800 (δ₁) | 10,065 |
| 2 — turn 2 | 10,065 | 65 (γ₂) | 800 (δ₂) | 10,930 |
| 3 — turn 3 | 10,930 | 65 (γ₃) | 800 (δ₃) | 11,795 |
| 4 — synthesis | 11,795 | 300 ($O_\text{final}$) | — | 12,095 |

Derived totals for that same trace [DERIVED]:

- `task_input` = 9,200 + 10,065 + 10,930 + 11,795 = **41,990** — Σ pure per-call inputs; no output token is ever counted as input. (The earlier example crossed the boundary by summing two *incl.-300-output* totals as if they were call inputs.)
- `task_output` = 3 × 65 + 300 = **495** — exactly Ch 17 §8's ~495 generated tokens at T = 3 (300 final + 3 × 65 intermediate).
- **Peak residency** = 12,095 tokens (synthesis input + $O_\text{final}$) → × 2.62 MB ≈ **31.7 GB** FP16 KV = Ch 17's I(3); single-shot peak 9,500 → 24.9 GB. It is the same 12,095 that α and Table 19-1 report, so ledger, amplification, and Ch 17 per-request KV are one arithmetic.
- **Billed, no prefix cache** (the §6 append-only bounding policy): 41,990 input + 495 output = **42,485** tokens; the execution-trace multiplier is 42,485 / 9,500 ≈ **4.47×**, while α stays 1.27× — the gap is the grown prefix being re-read on every call, which is precisely what α does *not* measure.
- **Billed, perfect prefix cache**: only each call's newly appended tokens are re-processed, 9,200 + 3 × 865 = **11,795** input + 495 output = **12,290** tokens. `cached` / `uncached` / `billed` stay recorded separately from context-carried input.

The δ tokens are *generated once* (as retrieval/tool output), then *retained* as part of later turns' input context — they are counted once as output-of-tool and again (as carried context) in each later call's input. That is correct and intended, but it means total tokens ≠ context size: the amplification α (retained context) and the task totals (Σ per-call) are explicitly different, and neither is the billed amount without a cache/billing rule.

### Tool-call latency budget

Crucially, the agentic layer adds latency **on top of** the base answer generation, not instead of it. We keep two terms rigidly separate:

- **Base inference latency *L*base** — the time to generate the final answer itself. Under the canonical model this is ~8.6 s: 1.08 s prefill (Ch 8) + ~7.5 s decode of the 300-token answer at ~25 ms/token (Ch 8). Every agentic request pays this at least once, and usually again for the intermediate reasoning the loop generates (the T·γ tokens).
- **Agent orchestration / tool-call overhead *L*agent** — the per-turn cost of the loop *around* the model: the LLM's short decision step to formulate the tool call, plus the tool backend round-trip. On 8×H100 the per-turn agent step averages ~120 ms for a 10,000-token context; tool backends (search, SQL) add 50–150 ms depending on data volume. So per-turn orchestration overhead *L*agent ≈ 220 ms (median).

$$
L_\text{agent} = \lambda_\text{step} + \lambda_\text{tool}
$$

where $\lambda_\text{step} \approx 120$ ms (the model's tool-call decision step) and $\lambda_\text{tool} \approx 100$ ms (median, tool backend). For *T* turns the **added** orchestration overhead is $T\cdot L_\text{agent}$ ≈ 220 ms at the median *T* = 1, ≈ 440 ms at the 90th percentile *T* = 2, and ≈ 660 ms at the 95th-percentile *T* = 3 (consistent with the §8 turn distribution and the §4 turn-distribution note; *T* is capped at 3, and the 2% fallback is a zero-added-turn single-shot *for this incremental expectation* — its failed-attempt work is counted unconditionally in the §8 fallback ledger). These are the **incremental agent-orchestration** numbers, not the full request latency — see the next section.

### Multi-step reasoning cost

The "cost" of multi-step reasoning has two facets: token amplification (already quantified as *α*) and latency. The **incremental end-to-end latency** — the base generation plus the added orchestration overhead — is:

$$
L_\text{E2E}(T) = L_\text{base} + T \cdot L_\text{agent}
$$

where $L_\text{base} \approx 8.6$ s is the canonical full answer generation (1.08 s prefill + 7.5 s decode of 300 output tokens) and $T \cdot L_\text{agent}$ is the added agent-orchestration overhead (≈ 220 ms per turn). So the agentic layer does *not* replace the ~8.6 s generation with ~440 ms — it *adds* a few hundred milliseconds of orchestration/tool overhead on top of a request that already takes ~8.6 s to generate its answer.

**Scope note — two different quantities, separated in Table 19-1.** The $L_\text{E2E}(T)$ above holds the base generation at the *single-shot* decode (300 output tokens) and adds only the per-turn orchestration overhead; it deliberately isolates *how much the agentic layer's orchestration adds*. The **full** agentic service time — the quantity used for fleet sizing in Chapter 17 — must additionally account for (a) the decode of the per-turn model-generated reasoning tokens ($\gamma \approx 65$ tokens/turn, at ~25 ms/token ≈ 1.6 s/turn) and (b) the longer prefill of the grown context ($I(T) = 9{,}200 + T(800+65) + 300$):

$$
W(T) = T_\text{prefill}(I(T)) + 25\text{ ms/token}\cdot\big(O_\text{final} + T\cdot\gamma\big) + T\cdot\lambda_\text{tool/retr}
$$

Chapter 17 §8 derives that full service time as $W \approx 13.8$ s at $T = 3$ (1.08 s prefill held at the canonical 9.2K representative — the 12,095-token context would scale it to ~1.42 s, giving W ≈ 14.2 s, so 13.8 s is a lower bound — plus ~12.4 s decode of ~495 generated tokens and ~0.4 s tool latency). Applying the same formula to the other columns gives W(1) ≈ 10.3 s, W(2) ≈ 12.1 s, W(4) ≈ 15.6 s, and W(0) = 8.6 s single-shot [DERIVED] — only W(3) ≈ 13.8 s is Chapter 17's stated figure. So: the **incremental orchestration overhead** is $T \cdot L_\text{agent}$ (~660 ms at T = 3, $\beta \approx 1.08\times$), while the **full end-to-end service time** of an agentic request is ~13.8 s at T = 3 — the two are *different quantities*, and the latter is what sets concurrency and fleet size. They are also **not additive**: $T \cdot L_\text{agent}$ is this chapter's 220 ms/turn orchestration budget ($\lambda_\text{step} + \lambda_\text{tool}$), whereas W's tool leg is Chapter 17's ~133 ms/turn tool/retrieval-only rate — Chapter 17 §8 itself notes that a single model should use one rate consistently — and W already carries the per-turn model work inside the γ decode. Table 19-1 therefore reports them as two separate rows: *Incremental orchestration (Lbase + T·L_agent)* (~8.8 / ~9.0 / ~9.3 / ~9.5 s) and *Full agentic service time W (Ch 17 §8)* (~10.3 / ~12.1 / ~13.8 / ~15.6 s), the latter matching Chapter 17's fleet-sizing tables at the same T. The latency amplification is better expressed as overhead, not a multiple of a sub-second single-shot number:

$$
\beta(T) = \frac{L_\text{base} + T\cdot L_\text{agent}}{L_\text{base}} \approx 1 + \frac{T \cdot 220\text{ ms}}{8.6\text{ s}}
$$

At *T* = 3, $\beta(3)$ is 1 + 660 ms / 8.6 s ≈ **1.08×**: the **orchestration-only** component adds ~8% — the agent loop is *not* "2–6× slower" in the orchestration sense. But $\beta$ measures only the incremental orchestration overhead, **not** the full task slowdown. The full service time of a three-turn task grows from ~8.6 s (single-shot) to at least ~13.8 s (~1.6×) once the per-turn reasoning decode (~65 γ tokens/turn) and grown-context prefill are counted — a full increase of ~5.2–5.6 s. So $\beta$ is $\beta_\text{orch}$ (orchestration-only), and the true task-level multiplier is $L_\text{task E2E}/L_\text{base} \approx 1.6$–$1.65\times$ at *T* = 3. The bound that actually matters: the *added* orchestration overhead is ~220 ms per turn (budget it), while fleet sizing follows the *total* request time — the ~13.8 s full service time, not the ~8.6 s single-shot generation.

These derived quantities give the architect concrete numbers to set policies: cap *T* at 3 unless the quality gain is statistically significant, and allocate ~220 ms *per turn* in the orchestration-latency budget.

### Internal depth, agent turns, and training rollouts

An internal depth iteration is not an agent turn. A recurrent model can repeat an internal block within one model invocation without emitting a tool call. An agent turn can contain prefill, internal computation, output generation, and tool interaction. A training rollout is a third object: a trajectory collected for the training procedure, not a request-time turn budget. This distinction prevents a training method or internal execution setting from being mistaken for the orchestration trace that the fleet must serve.[^oct19-depth]

Model qualification records the benchmark harness, context policy, reasoning effort, sampling settings, and success metric with the model revision. A best-of-several-trials result is not interchangeable with pass-at-one. Averaging independent single-attempt success indicators can estimate pass-at-one only under the declared sampling and task protocol. An advertised context window does not establish useful long-context quality, target concurrency, or the cost of serving it. The deployment decision follows measured task success, invocation traces, and SLO-goodput, not a model-family label alone. [ILLUSTRATIVE][DERIVED]

[^oct19-depth]: Geiping et al., *Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach*, arXiv:2502.05171v2, 17 February 2025, [https://arxiv.org/abs/2502.05171v2](https://arxiv.org/abs/2502.05171v2); Ornith Team, *Ornith-1.5: From Self-Scaffolding to Self-Improvement*, August 2026, [https://ornith.ai/ornith_1_5.html](https://ornith.ai/ornith_1_5.html). These primary accounts distinguish recurrent internal computation and training trajectories; neither establishes the request-time turn count of the book's hypothetical agent. Sources inspected 28 October 2026 as part of the separately dated addendum, not a refresh of the August comparison tables.

## 5. Common Mistakes

1. **Unbounded or miscalibrated turn limits.** Setting the maximum number of agent turns too high for the task leads to runaway token consumption and latency spikes. A poorly scoped tool can let a model loop until token or deadline limits stop the request. [HYPOTHESIS] The right cap is task-calibrated: measure the distribution of useful completion turns, loop-failure turns, and marginal value per turn for the workload, then set the cap where marginal value drops off (the canonical policy caps at 3, with a 2% fallback to single-shot — §4, §8); the number is a policy parameter, not a constant.

2. **Neglecting token accounting per turn.** Many architects track only the initial input tokens and forget that each retrieval or tool call adds context that persists for all subsequent turns. Turn *T* therefore sees an input base that grows linearly with *T*. Concretely the append-only total is I₀ + T·δ + T·γ + O_final = 9,200 + 800T + 65T + 300, which at 2.62 MB/token takes FP16 KV from 24.9 GB (single-shot, 9,500 tokens) to 34.0 GB (four turns, 12,960 tokens).

3. **Overlooking tool latency variance.** A tool that typically responds in 30 ms may, under cache misses or lock contention, take 2 s. Without a timeout and fallback, the entire agent loop blocks. Always instrument timeouts and provide a “best-effort” fallback path.

4. **Confusing 'agentic' with 'more prompts'.** Adding extra prompts without a structured loop (Plan/Execute/Observe/Decide) does not give the model reasoning power; it just inflates token count. The agentic value comes from the model’s ability to reinterpret prior observations and decide the next action.

5. **Skipping guardrails.** Without pre-call validation (e.g., query sanitization, budget checks) and post-call verification (answer relevance, hallucination detection), agentic systems can produce plausible but incorrect or unsafe outputs. Guardrails are not optional — they are the safety net that makes *bounded* loops safe in production. A production agent needs explicit termination, budget, recovery, and escalation policies: hard turn/token/cost/wall-time limits, tool timeouts, cancellation, idempotency/retry discipline, state checkpointing, and human escalation. A logical multi-step task may be resumed across bounded execution windows rather than granted unlimited resources — guardrails make the loop *safe*, not *unbounded*.

## 6. Architecture Consequence

Introducing an agentic layer reshapes the system architecture in four ways:

**State-management policy sets the trajectory.** Before quantifying context/KV growth, the architect must decide the *state-management policy*, because that policy — not the model — determines whether context grows unbounded. The quantitative path that follows (Fig 19.2/19.3) uses an **append-only bounding case** with this exact retention policy: (i) the initial prompt is retained in full; (ii) each turn's tool outputs are retained in full (not externalized); (iii) the model's per-turn reasoning tokens are visible and retained in the context (not hidden); (iv) no prefix cache is assumed to be reused across turns (each turn's request is rebuilt from the full accumulated context); (v) no truncation or compaction is applied. Under that policy the context is only ever appended and never evicted, so it is the worst case — a deliberate upper bound, not the deployed design. Two token counts must be kept distinct: the **billable tokens** (what the API charges, = the full accumulated context sent each turn) and the **KV-resident tokens** (what occupies the cache, = the same accumulated context under this no-reuse policy); with prefix caching enabled the billable count can fall while the KV-resident count stays, so the two diverge. The durable architectural lesson is that the growth rate is set by the policy levers — summarization (compress the accumulated history each turn), truncation (drop the oldest context beyond a budget), externalized tool state (store retrieval results out-of-band rather than in-context), replay policy (re-derive rather than retain), and cache policy (prefix caching, KV precision). A design that applies these levers can hold context roughly flat while an append-only design grows it ~36% by turn 4; the append-only number is the *stress case* that bounds what the system must tolerate if the levers fail, not the expected operating point.

**Inference scaling.** The base model (70B FP16, 8×H100) must now serve variable-length contexts, and — critically — the KV-residency conclusion is far more severe than a per-latency convenience because the canonical per-token KV is ~2.62 MB/token (Chapter 7's full-MHA reference geometry). A request that triggers 4 agent turns carries ~12,960 tokens vs. 9,500 for single-shot (Table 19-1) — that is not a "35% GPU memory" tweak but a move from ~24.9 GB KV per request (9,500 tokens × 2.62 MB) to ~34.0 GB (12,960 ×2.62 MB) — roughly a 36% growth, on top of an already-large KV footprint. At the canonical workload's ~86 average in-flight requests at 10 rps ($L_{\mathrm{exec}}$ = λ × $W_{\mathrm{exec}}$ ≈ 10 × 8.6 per Ch 4; distinct from the ~100 *active-user* population) with the median single-turn profile (~27.2 GB/request at 10,365 tokens), the aggregate KV alone is ~86 × 27.2 GB ≈ 2.3 TB — far beyond one host's ~436 GB KV budget, so **agents do not just stress memory, they force a fleet** (Chapter 17). The architect must therefore treat context growth as a first-order capacity driver: cap *T*, cache prefixes, or quantize KV (FP8), as these levers repeatedly outprice adding hosts. Note we must be precise: the per-request KV is set by the model's canonical per-token KV (all layers), not by per-layer figures; the honest number is tens of GB per request, which is exactly why agentic depth is a fleet-sizing problem.

![Fig 19.2 — Per-request tokens and FP16 KV cache climb linearly with agent turns, from 24.9 GB single-shot to 34.0 GB at four turns. Assumption: an append-only bounding case where each column is a counterfactual completion (9,200 input + 300 output + 800 + 65 per turn), status [DERIVED] from Ch 19 arithmetic. Caveat: a production stack that compacts or prefix-caches can hold this flat.](figures/fig-19-1902.png)

*Why agentic depth is a fleet-sizing problem. Both the token count and the FP16 KV cache grow linearly with turns; four turns take a request from ~24.9 GB to ~34.0 GB of KV — a 36% jump on an already-large footprint, which is exactly why a fleet (Ch17), prefix caching, or FP8 KV pay for themselves on agentic workloads.*

![Fig 19.3 — The agentic context block stacks an initial prompt, cumulative tool output and reasoning, and a fixed final answer, lifting FP16 KV 24.9 → 34.0 GB. Assumption: a strict append-only policy where each column is a counterfactual completion (I0 9.2K, delta 800, gamma 65, O 300 per turn), status [ILLUSTRATIVE][DERIVED]. Caveat: compaction, truncation or prefix caching can hold KV flat or shrink it.](figures/fig-19-1903.png)

*Agentic context accumulation as a memory sequence. Each turn appends retrieved context (δ ≈ 800 tokens) plus generated reasoning (γ ≈ 65 tokens) to a context that persists across every later turn; the FP16 KV block therefore grows from ~24.9 GB (single-shot) to ~34.0 GB (four turns) — a 36% footprint rise driven purely by cumulative context, not by extra requests. This is the mechanism behind the fleet-sizing argument in Fig 19.2.*

**Task economics.** The deepest shift an agentic workload imposes is a change in *what the architect optimizes*. For conventional inference, the unit of cost is the token: the architect optimizes token economics — cost per token, latency per token, KV per token. For an agentic system, the unit of value is the *task*: the architect optimizes task economics, because a task consumes a variable, data-dependent number of model calls, tool calls, and tokens, and may fail. The right denominator is therefore **cost per successful task**, not cost per token:

$$
\text{cost per successful task} \approx \frac{\begin{aligned}
&\text{model calls/task} \times \text{tokens/call} \times \$/\text{token} \\
&{}+ \text{tool calls/task} \times \$/\text{tool} \\
&{}+ \text{retries/task} \times \text{cost/retry}
\end{aligned}}{p_{\text{success}}}
$$

where $p_\text{success} > 0$ is the task success rate and tokens/call is itself inflated by the agentic amplification *α* from Section 4. Two consequences follow. First, a more expensive model that completes tasks in one turn can be cheaper *per successful task* than a cheap model that needs three turns — the amplification term can dominate the base price. Second, the success rate is as important as the unit cost: a 10% cheaper pipeline that fails 5% more often can be net more expensive once retries and human intervention are counted. This is a genuinely different objective from *cheapest tokens*, and it is why agentic workloads cannot be priced or capacity-planned with the single-shot token arithmetic alone. An architect should instrument tasks (success, turns, calls, retries) and optimize cost per successful task, exactly as an architect of a deterministic service optimizes cost per completed request.

**Tool backend provisioning.** Search indexes, SQL pools, and code interpreters become first-class infrastructure components. Their capacity (concurrent queries, connection pool size, query throughput) must be dimensioned alongside the LLM GPU pool. A bottleneck in the tool backend will manifest as increased $\lambda_\text{tool}$, which directly inflates the per-turn latency *L* and therefore the overall request latency.

**Observability requirements.** Each turn generates a tuple of (turn number, model input tokens, tool call, tool latency, tool output tokens, decision). Correlating these tuples across turns for a single request, and across requests for the fleet, requires structured logging and tracing. Without it, debugging why a request took 2 s and consumed 15,000 tokens is nearly impossible.

**Fallback & degradation pathways.** Because the agentic layer introduces data-dependent depth, the system must have graceful degradation: if the turn limit is reached, return the best partial answer so far, or fall back to a simpler single-shot prompt. This preserves user experience even when the agent fails to converge.

## 7. What We Still Don't Know

Despite the quantified arithmetic above, several questions remain open and would benefit from targeted research:

- **Turn-count distribution shift with model scale.** Do larger-context models (e.g., 405B FP16) exhibit different *T* distributions? Does the ability to "see more" reduce the need for multi-step loops, or does the model reason more deeply and actually increase *T*?
- **Token amplification vs. answer quality curve.** We can compute *α(T)* from the illustrative token counts, but we have not firmly established the marginal quality gain per additional turn. Is the 1.27× → 1.36× move from *T* = 3 to *T* = 4 worth the 7% token increase? A/B tests across query categories would help.
- **Latency tail under spike load.** Our 95th-percentile *added* orchestration latency of ~660 ms (T = 3, the scenario turn cap; conditional on a completed agent run, with the fallback-inclusive ledger in §8 giving the same p95 but p99 = 860 ms) assumes GPU inference time is constant. Under traffic spikes, GPU saturation can increase inference latency non-linearly. Empirical measurement under controlled load is needed to validate the linear *T·L* model.
- **Optimal tool design for minimal turn count.** Some tools could return more comprehensive results in a single call, reducing the need for multiple rounds. The design space of "rich vs. narrow" tools and its impact on *T* is underexplored.
- **Cross-user context caching.** If many users ask related questions (e.g., "What does the policy say about X?"), can we cache intermediate retrieval results and avoid redundant tool calls? The savings could be substantial but require careful invalidation logic.

## 8. End-of-Chapter Mini-Case: Agentic Turn Distribution and KV Growth

**Scenario.** An enterprise RQA system serves 2,000 knowledge workers. The baseline single-shot configuration uses a 70B FP16 model on 8×H100, with 9,200 input tokens and 300 output tokens, at 10 rps average / 40 rps peak. The team introduces an agentic layer with a maximum of 3 turns, using the chapter's per-turn convention (δ≈800 + γ≈65 ≈ 865 tokens/turn). The guardrail budget caps total input at 13,000 tokens.

**Measurement results.** The scenario's 30-day telemetry shows [ILLUSTRATIVE][ASSUMPTION] — the same turn distribution §4 labels illustrative, here as scenario data rather than a reported production trace:

- 68% of requests terminate in 1 turn
- 25% terminate in 2 turns
- 5% terminate in 3 turns
- 2% exceed the turn limit and fall back to single-shot

**Token and latency impact (added orchestration overhead).** Using the chapter's per-turn convention (each turn adds δ=800 retrieved + γ=65 reasoning = 865 tokens), and treating the 2% fallback as single-shot (zero added turns *for this retained-context expectation* — its failed-attempt work is counted unconditionally in the fallback ledger below), the expected input tokens across the distribution are:

- Expected input tokens: 0.68×(9,200+865) + 0.25×(9,200+1,730) + 0.05×(9,200+2,595) + 0.02×9,200 ≈ 6,844 + 2,733 + 590 + 184 ≈ **10,350 tokens** (expected total incl. 300-token output ≈ 10,650).
- Amplification *α*: 10,650 / 9,500 ≈ **1.12×** — about a **12%** token overhead. (The 2% fallback is explicitly included here at zero added turns: it adds no *retained* agent tokens, so its contribution to this expectation is 2% × 0 = 0, which the weighted sum above keeps. This expectation is over *retained context*; the fallback's failed-attempt tokens are counted in the unconditional ledger below.)
- **Conditional completed-agent percentiles (explicit label).** Added agent-orchestration overhead (per-turn step + tool) is 220 ms/turn. Because 68% terminate in one turn, the **median turns is T = 1**, so the median added overhead is **1 × 220 ms ≈ 220 ms**; the **90th-percentile** is T = 2 (conditional cumulative **94.9%** by T ≤ 2) → **440 ms**; and the **95th-percentile** is T = 3 (conditional cumulative 100% by T ≤ 3) → **660 ms** — *not* T ≈ 4, since the scenario caps turns at 3 and the 2% fallback is modelled as an immediate single-shot fallback, not a fourth attempted turn. **Percentile conditioning:** these percentiles are computed over the **non-fallback (completed-turn) request distribution** — they are *conditional on a completed agent run* (98% of requests; renormalized cumulative 69.4% by T ≤ 1, 94.9% by T ≤ 2, 100% by T ≤ 3), so the conditional p50/p90/p95 = **220 / 440 / 660 ms** with mean ≈ **299 ms** and a maximum of 660 ms. Under this convention the 2% fallback is a high-tail/failure category that incurs *zero added turns* (single-shot) — the *incremental* agent work beyond the single-shot baseline is zero, so it adds nothing to the p90/p95 values; but the *total* work the failed agent attempts already consumed is not erased, it is simply not counted here. The unconditional ledger below counts it, and states which convention is in use.
- **Unconditional fallback-inclusive ledger (all 100 requests).** Stated assumptions [ILLUSTRATIVE][ASSUMPTION]: a fallback request attempts the full cap (T = 3 — 3 model calls + 3 tool calls) before the guardrail trips, then re-dispatches a single-shot fallback (9,200 + 300); guardrail evaluation + re-dispatch adds ~200 ms. Per-class model tokens are the §4 event-level ledger's Σ per-call inputs and outputs:

| Request class (share) | Added orchestration | Model input tok | Model output tok | Total tok |
|---|---|---|---|---|
| Completed T = 1 (68%) | 220 ms | 19,265 | 365 | 19,630 |
| Completed T = 2 (25%) | 440 ms | 30,195 | 430 | 30,625 |
| Completed T = 3 (5%) | 660 ms | 41,990 | 495 | 42,485 |
| Fallback: 3 attempted turns + single-shot (2%) | 660 ms + ~200 ms ≈ 860 ms | 39,395 | 495 | 39,890 |

  Derived over all 100 requests: p50 = 220 ms, p90 = 440 ms, **p95 = 660 ms** (the 93rd–98th percentile band), **p99 = 860 ms** (the fallback band — invisible under the conditional convention, whose maximum is 660 ms), mean ≈ **310 ms** vs ≈ 299 ms conditional. **Cost per completed request** = 2,392,670 tokens ÷ 98 completed = **24,415 tokens** (≈ 24,017 input + ≈ 398 output); excluding the fallback's failed-attempt work gives 23,601, so the excluded work is **+814 tokens (+3.4%) per completed request**. The unconditional p95 happens to equal the conditional p95 — the fallback occupies only the top 2%, so it cannot move the 95th percentile — but p99, the mean, and cost-per-completed-request all move, which is exactly why the convention must be stated with the number. The fallback's failed-attempt *decode* (3 × 65 = 195 tokens ≈ 4.9 s at 25 ms/token) is real GPU time: it does not appear in the orchestration-only metric, it appears in the full service time *W* (§4) and in these token totals.
- Total latency rows: the *incremental* request is dominated by the ~8.6 s base generation (Ch 8), not the added orchestration; the ~220–660 ms figures are the *added* agent/tool overhead, not the complete request latency. The complete request is the *full agentic service time W* row of Table 19-1 — ~10.3 s at the median T = 1 and ~13.8 s at T = 3 — which is the quantity Chapter 17 sizes the fleet against.

**Architectural actions.** The team sets the turn limit to 3, instruments each turn's token and orchestration latency, and adds a context cache for the search tool. With a cache hit rate of 30% on recurring queries, the *newly-fetched* portion of δ drops to ~560 tokens per turn (70% of 800; the cached 30% is not re-fetched) — a 30% cut in retrieval re-fetch transport. **Note:** the *retained* context still carries the full 800 tokens per turn (cached or not), so absent a concrete context-reduction policy this cache yields no LLM-token or KV-resident saving; the re-fetch cost and the KV-resident length are distinct (see the billable-vs-KV-resident distinction in §19.3). The median added orchestration overhead is still T = 1 → ~220 ms. The claim "meets an SLA of <1 s" must be scoped carefully: the *added agent-orchestration* latency is comfortably under 1 s, but the **end-to-end** request is ~9 s because of the base generation. The architect therefore scopes the <1 s SLA to orchestration overhead *excluding* final generation, and treats end-to-end as bounded by the ~8.6 s base generation in the incremental view (or by the full service time *W* ≈ 10.3 s at the median T = 1 in the fleet-sizing view).

**Lesson.** The agentic layer added an expected ~12% token overhead (distribution-weighted, §8) and, at the median T = 1, ~220 ms of orchestration latency (on top of an ~8.6 s base generation), but improved answer correctness on multi-step reasoning queries by an estimated 22% in an illustrative human-eval reading [ILLUSTRATIVE] scenario result, not a reported production measurement. The trade-off was acceptable — the added overhead is small relative to the base generation — and context caching cut the retrieval re-fetch cost (transport only — the retained context is unchanged). The architect's key decisions were: (a) capping turns at 3, (b) adding a search cache, and (c) providing a single-shot fallback when the limit is hit.

\Needspace{32\baselineskip}

---

**Table 19-1** — Token amplification and latency trade-offs for agentic RQA pipelines

| Metric | T = 1 (med.) | T = 2 (p90) | T = 3 (p95) | T = 4 (over cap) | Single-shot |
|--------------------|------|------|------|------|------|
| Input tokens (9,200 + T·800 + T·65) | 10,065 | 10,930 | 11,795 | 12,660 | 9,200 |
| Total tokens (incl. 300 output) | 10,365 | 11,230 | 12,095 | 12,960 | 9,500 |
| Token amplification *α* | 1.09× | 1.18× | 1.27× | 1.36× | 1.00× |
| Per-turn agent step, 10K ctx | ~120 ms | ~120 ms | ~120 ms | ~120 ms | — |
| Tool latency (median) | ~100 ms | ~100 ms | ~100 ms | ~100 ms | — |
| Added orchestration overhead (T × 220 ms) | ~220 ms | ~440 ms | ~660 ms | ~880 ms | 0 ms |
| Base answer generation *L*base | ~8.6 s | ~8.6 s | ~8.6 s | ~8.6 s | ~8.6 s |
| Incremental orchestration (Lbase + T·L_agent) | ~8.8 s | ~9.0 s | ~9.3 s | ~9.5 s | ~8.6 s |
| Full agentic service time *W* (Ch 17 §8) | ~10.3 s | ~12.1 s | ~13.8 s | ~15.6 s | ~8.6 s |
| KV cache @ 2.62 MB/token | ~27.2 GB | ~29.4 GB | ~31.7 GB | ~34.0 GB | ~24.9 GB |

*All token counts use δ=800, γ=65, O=300; orchestration overhead uses $\lambda_\text{step} \approx 120$ ms + $\lambda_\text{tool} \approx 100$ ms per turn; base generation uses the canonical ~8.6 s (§4). The two latency rows are different quantities and must not be added: **Incremental orchestration** = Lbase + T·L_agent, dominated by the base generation, NOT the agent overhead; **Full agentic service time W** = Ch 17 §8's prefill + decode of all generated tokens + tool leg, with the prefill **held at the canonical 1.08 s** (the 9.2K representative) rather than scaled to the grown I(T) — so W(3) = 1.08 + 0.025×495 + 3×0.133 = **13.854 s** (rounds to 13.9 s); the table reports **13.8 s**, Chapter 17's stated lower bound (scaling the prefill to the 12,095-token context would give ~1.42 s and W ≈ 14.2 s). This is the row that sets concurrency and fleet size. Canonical-model [DERIVED] values, not measured production figures.*