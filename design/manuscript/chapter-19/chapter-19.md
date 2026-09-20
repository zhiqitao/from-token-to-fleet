# Chapter 19: Agentic Systems

## The Architect's Question

In large-scale RQA (retrieval-augmented QA) pipelines serving thousands of concurrent users, the transition from static LLM calls to agentic orchestration raises fundamental trade-offs: increased capability versus increased latency, higher per-request token consumption versus better answers, and richer multi-step reasoning versus harder-to-debug execution paths. This chapter addresses the architect's central question: how to design agentic layers that amplify intelligence without unsustainably inflating cost and latency.

We begin from a concrete deployment scenario: ~2,000 users with ~5% concurrent access, driving ~10 requests/second average and ~40 requests/second peak. Each request carries ~9,200 input tokens and produces ~300 output tokens. The base model is a 70B dense FP16 engine running on 8×H100 GPUs (640 GB total memory). The agentic layer sits above this foundation, introducing tool use, retrieval, and multi-step reasoning. The question we answer is how much additional overhead this layer introduces, whether the quality gain justifies the cost, and how to size the infrastructure accordingly.

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

![Fig 19.1 - The agent loop as a four-state state machine (Plan, Execute, Observe, Decide) with a loop-back to Plan and the terminal outcomes final answer and stopped [ILLUSTRATIVE conceptual]](figures/fig-19-1901.png)

## 3. Worked Example

Consider a user query routed to an agentic RQA pipeline. The pipeline’s default policy is a maximum of 4 turns; if the model has not terminated by then, the system returns a fallback answer “I’m sorry, I couldn’t find a definitive answer within the allowed reasoning steps.”

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
- Amplification factor: 10,650 / 9,500 ≈ 1.12×

Now consider a harder query that exhausts all 4 turns. Using the chapter's per-turn convention (each turn adds δ≈800 tokens of retrieved context plus γ≈65 tokens of model-generated reasoning), the token trajectory grows approximately linearly: after *k* turns, total input tokens ≈ 9,200 + k·(800+65), and total output ≈ 300 (final answer) plus the intermediate reasoning (≈65 tokens per turn). After 4 turns, input ≈ 9,200 + 4×800 + 4×65 = 12,660 tokens, output ≈ 300 tokens, giving a total of ~12,960 tokens. The amplification factor vs. single-shot is 12,960 / 9,500 ≈ 1.36×.

This worked example demonstrates that the cost increase is moderate for short reasoning paths but compounds as the agent loops deeper. The architect must weigh the probability of deep loops against the budget per request.

## 4. Measurement

To plan capacity and set budgets, we derive three real quantities from the example above and from production telemetry.

First, a scoping note that matters more than any single number: a production agent turn is **not** guaranteed to be exactly "one LLM inference + one tool call." A turn may contain zero or more model invocations, parallel or chained tool calls, retrieval + reranking, model-generated reasoning, tool output, context compaction, or cached prefixes. Treating "1 turn = 1 LLM call + 1 tool call" is a *simplified execution model*, useful for first-pass arithmetic but not the general agent model. A more faithful capacity model is an **execution trace**: request → model invocation(s) → tool invocation(s) → observation(s) → model invocation(s) → final response, with its own token and latency totals. The amplification framework below (token *α*, latency *β*) is one concrete, simplified instantiation of that trace — it is what an architect can compute before instrumenting a real system, and it must be validated against measured traces afterwards.

### Per-agent-turn token amplification

Let *T* be the number of agent turns and *I₀* the initial input tokens (9,200 in our scenario). Each turn adds *δ* tokens of retrieved context and *γ* tokens of model-generated reasoning. The total token count after *T* turns is:

$$
\text{Total}(T) = (I_0 + T \cdot \delta + T \cdot \gamma) + O_\text{final}
$$

where *O_final* is the final output (≈300 tokens). The per-turn amplification *α* is the ratio of total tokens to the single-shot baseline *I₀ + O_final*:

$$
\alpha(T) = \frac{I_0 + T\cdot\delta + T\cdot\gamma + O_\text{final}}{I_0 + O_\text{final}}
$$

With *δ* = 800, *γ* = 65, *O_final* = 300, and *T* = 3:

$$
\alpha(3) = \frac{9{,}200 + 3\cdot800 + 3\cdot65 + 300}{9{,}200 + 300} = \frac{9{,}200 + 2{,}400 + 195 + 300}{9{,}500} = \frac{12{,}095}{9{,}500} \approx 1.27\times
$$

For *T* = 4: α(4) ≈ 1.36× as computed in the worked example. In production, the distribution of *T* depends on query complexity. Consistent with the mini-case telemetry in §8 (68% T=1, 25% T=2, 5% T=3, 2% fallback), the illustrative turn distribution here has median *T* = 1, 90th percentile *T* = 2, and 95th percentile *T* = 3 [ILLUSTRATIVE assumption, derived from the §8 distribution].

### Tool-call latency budget

Crucially, the agentic layer adds latency **on top of** the base answer generation, not instead of it. We keep two terms rigidly separate:

- **Base inference latency *L*base** — the time to generate the final answer itself. Under the canonical model this is ~8.6 s: 1.08 s prefill (Ch 8) + ~7.5 s decode of the 300-token answer at ~25 ms/token (Ch 8). Every agentic request pays this at least once, and usually again for the intermediate reasoning the loop generates (the T·γ tokens).
- **Agent orchestration / tool-call overhead *L*agent** — the per-turn cost of the loop *around* the model: the LLM's short decision step to formulate the tool call, plus the tool backend round-trip. On 8×H100 the per-turn agent step averages ~120 ms for a 10,000-token context; tool backends (search, SQL) add 50–150 ms depending on data volume. So per-turn orchestration overhead *L*agent ≈ ~220 ms (median).

$$
L_\text{agent} = \lambda_\text{step} + \lambda_\text{tool}
$$

where $\lambda_\text{step} \approx 120$ ms (the model's tool-call decision step) and $\lambda_\text{tool} \approx 100$ ms (median, tool backend). For *T* turns the **added** orchestration overhead is $T\cdot L_\text{agent}$ ≈ 2 × 220 ms ≈ 440 ms at the median *T* = 2, and ≈ 880 ms at the 95th-percentile *T* = 4. These are the **incremental agent-orchestration** numbers, not the full request latency — see the next section.

### Multi-step reasoning cost

The "cost" of multi-step reasoning has two facets: token amplification (already quantified as *α*) and latency. The **total end-to-end latency** is the base generation plus the added orchestration overhead:

$$
L_\text{E2E}(T) = L_\text{base} + T \cdot L_\text{agent}
$$

where $L_\text{base} \approx 8.6$ s is the canonical full answer generation (1.08 s prefill + 7.5 s decode of 300 output tokens) and $T \cdot L_\text{agent}$ is the added agent-orchestration overhead (≈ 220 ms per turn). So the agentic layer does *not* replace the ~8.6 s generation with ~440 ms — it *adds* a few hundred milliseconds of orchestration/tool overhead on top of a request that already takes ~8.6 s to generate its answer. The latency amplification is better expressed as overhead, not a multiple of a sub-second single-shot number:

$$
\beta(T) = \frac{L_\text{base} + T\cdot L_\text{agent}}{L_\text{base}} \approx 1 + \frac{T \cdot 220\text{ ms}}{8.6\text{ s}}
$$

At *T* = 3, this is 1 + 660 ms / 8.6 s ≈ **1.08×** of the base generation — i.e. the agentic loop adds roughly 8% end-to-end latency, not "2–6× slower". The bound that actually matters for the architect is that the *added* orchestration overhead per turn is ~220 ms (and must be budgeted), while the *total* request time is dominated by the ~8.6 s generation that the canonical model already establishes.

These derived quantities give the architect concrete numbers to set policies: cap *T* at 3 unless the quality gain is statistically significant, and allocate ~220 ms *per turn* in the orchestration-latency budget.

## 5. Common Mistakes

1. **Unbounded turn limits.** Setting the maximum number of agent turns too high (e.g., 10 or more) leads to runaway token consumption and latency spikes. In production we have seen a single request consume >30,000 tokens and take >5 seconds because the model kept looping on a poorly scoped tool.

2. **Neglecting token accounting per turn.** Many architects track only the initial input tokens and forget that each retrieval or tool call adds context that persists for all subsequent turns. The compounding effect means that turn *T* sees an input base that grows linearly with *T*.

3. **Overlooking tool latency variance.** A tool that typically responds in 30 ms may, under cache misses or lock contention, take 2 s. Without a timeout and fallback, the entire agent loop blocks. Always instrument timeouts and provide a “best-effort” fallback path.

4. **Confusing 'agentic' with 'more prompts'.** Adding extra prompts without a structured loop (Plan/Execute/Observe/Decide) does not give the model reasoning power; it just inflates token count. The agentic value comes from the model’s ability to reinterpret prior observations and decide the next action.

5. **Skipping guardrails.** Without pre-call validation (e.g., query sanitization, budget checks) and post-call verification (answer relevance, hallucination detection), agentic systems can produce plausible but incorrect or unsafe outputs. Guardrails are not optional — they are the safety net that makes unbounded loops acceptable in production.

## 6. Architecture Consequence

Introducing an agentic layer reshapes the system architecture in four ways:

**Inference scaling.** The base model (70B FP16, 8×H100) must now serve variable-length contexts, and — critically — the KV-residency conclusion is far more severe than a per-latency convenience because the canonical per-token KV is ~2.62 MB/token (Chapter 7). A request that triggers 4 agent turns carries ~12,960 tokens vs. 9,500 for single-shot (Table 19-1) — that is not a "35% GPU memory" tweak but a move from ~24.9 GB KV per request (9,500 tokens × 2.62 MB) to ~34.0 GB (12,960 ×2.62 MB) — roughly a 36% growth, on top of an already-large KV footprint. At 100 concurrent users with the median 2-turn profile (~29.4 GB/request at 11,230 tokens), the aggregate KV alone is ~2.9 TB — far beyond one host's ~436 GB KV budget, so **agents do not just stress memory, they force a fleet** (Chapter 17). The architect must therefore treat context growth as a first-order capacity driver: cap *T*, cache prefixes, or quantize KV (FP8), as these levers repeatedly outprice adding hosts. Note we must be precise: the per-request KV is set by the model's canonical per-token KV (all layers), not by per-layer figures; the honest number is tens of GB per request, which is exactly why agentic depth is a fleet-sizing problem.

![Fig 19.2 — Input/output tokens and KV cache per request across agent turns (I₀ + T·δ + T·γ; 9,200 + 800 + 65 per turn), FP16 KV rising from 24.9 GB single-shot to 34.0 GB at 4 turns. This chart quantifies the growth — the total token and KV numbers as turns accumulate. (Companion Fig 19.3 shows the mechanism of why it grows.) [DERIVED: Ch19 §3 arithmetic]](figures/fig-19-1902.png)

*Why agentic depth is a fleet-sizing problem. Both the token count and the FP16 KV cache grow linearly with turns; four turns take a request from ~24.9 GB to ~34.0 GB of KV — a 36% jump on an already-large footprint, which is exactly why a fleet (Ch17), prefix caching, or FP8 KV pay for themselves on agentic workloads.*

![Fig 19.3 — The agentic context block grows every turn: initial prompt (9.2K tok) plus tool output (δ) + reasoning (γ) appended each turn, FP16 KV footprint rising 24.9 → 34.0 GB (max-KV, end-of-request). This schematic shows the mechanism — the initial prompt base plus cumulative tool-output and reasoning blocks. (Companion Fig 19.2 quantifies the total.) [ILLUSTRATIVE][DERIVED: Ch19 arithmetic]](figures/fig-19-1903.png)

*Agentic context accumulation as a memory sequence. Each turn appends retrieved context (δ ≈ 800 tokens) plus generated reasoning (γ ≈ 65 tokens) to a context that persists across every later turn; the FP16 KV block therefore grows from ~24.9 GB (single-shot) to ~34.0 GB (four turns) — a 36% footprint rise driven purely by cumulative context, not by extra requests. This is the mechanism behind the fleet-sizing argument in Fig 19.2.*

**Task economics.** The deepest shift an agentic workload imposes is a change in *what the architect optimizes*. For conventional inference, the unit of cost is the token: the architect optimizes token economics — cost per token, latency per token, KV per token. For an agentic system, the unit of value is the *task*: the architect optimizes task economics, because a task consumes a variable, data-dependent number of model calls, tool calls, and tokens, and may fail. The right denominator is therefore **cost per successful task**, not cost per token:

```
cost / successful task ≈
         (model calls/task × tokens/call × $/token)
                            + (tool calls/task × $/tool)
                            + (retries/task × cost/retry)
             divided by the success rate of the task
```

where tokens/call is itself inflated by the agentic amplification *α* from Section 4. Two consequences follow. First, a more expensive model that completes tasks in one turn can be cheaper *per successful task* than a cheap model that needs three turns — the amplification term can dominate the base price. Second, the success rate is as important as the unit cost: a 10% cheaper pipeline that fails 5% more often can be net more expensive once retries and human intervention are counted. This is a genuinely different objective from *cheapest tokens*, and it is why agentic workloads cannot be priced or capacity-planned with the single-shot token arithmetic alone. An architect should instrument tasks (success, turns, calls, retries) and optimize cost per successful task, exactly as an architect of a deterministic service optimizes cost per completed request.

**Tool backend provisioning.** Search indexes, SQL pools, and code interpreters become first-class infrastructure components. Their capacity (concurrent queries, connection pool size, query throughput) must be dimensioned alongside the LLM GPU pool. A bottleneck in the tool backend will manifest as increased λ_tool, which directly inflates the per-turn latency *L* and therefore the overall request latency.

**Observability requirements.** Each turn generates a tuple of (turn number, model input tokens, tool call, tool latency, tool output tokens, decision). Correlating these tuples across turns for a single request, and across requests for the fleet, requires structured logging and tracing. Without it, debugging why a request took 2 s and consumed 15,000 tokens is nearly impossible.

**Fallback & degradation pathways.** Because the agentic layer introduces data-dependent depth, the system must have graceful degradation: if the turn limit is reached, return the best partial answer so far, or fall back to a simpler single-shot prompt. This preserves user experience even when the agent fails to converge.

## 7. What We Still Don't Know

Despite the quantified arithmetic above, several questions remain open and would benefit from targeted research:

- **Turn-count distribution shift with model scale.** Do larger-context models (e.g., 405B FP16) exhibit different *T* distributions? Does the ability to "see more" reduce the need for multi-step loops, or does the model reason more deeply and actually increase *T*?
- **Token amplification vs. answer quality curve.** We can compute *α(T)* from the illustrative token counts, but we have not firmly established the marginal quality gain per additional turn. Is the 1.27× → 1.36× move from *T* = 3 to *T* = 4 worth the 7% token increase? A/B tests across query categories would help.
- **Latency tail under spike load.** Our 95th-percentile latency of ~880 ms assumes GPU inference time is constant. Under traffic spikes, GPU saturation can increase inference latency non-linearly. Empirical measurement under controlled load is needed to validate the linear *T·L* model.
- **Optimal tool design for minimal turn count.** Some tools could return more comprehensive results in a single call, reducing the need for multiple rounds. The design space of "rich vs. narrow" tools and its impact on *T* is underexplored.
- **Cross-user context caching.** If many users ask related questions (e.g., "What does the policy say about X?"), can we cache intermediate retrieval results and avoid redundant tool calls? The savings could be substantial but require careful invalidation logic.

## 8. End-of-Chapter Mini-Case

**Scenario.** An enterprise RQA system serves 2,000 knowledge workers. The baseline single-shot configuration uses a 70B FP16 model on 8×H100, with 9,200 input tokens and 300 output tokens, handling 10 rps average / 40 rps peak. The team introduces an agentic layer with a maximum of 3 turns, using the chapter's per-turn convention (each turn adds δ≈800 tokens of retrieved context plus γ≈65 tokens of model-generated reasoning, i.e. ≈865 tokens/turn). The guardrail budget caps total input at 13,000 tokens.

**Measurement results.** Telemetry over 30 days shows:
- 68% of requests terminate in 1 turn
- 25% terminate in 2 turns
- 5% terminate in 3 turns
- 2% exceed the turn limit and fall back to single-shot

**Token and latency impact (added orchestration overhead).** Using the chapter's per-turn convention (each turn adds δ=800 retrieved + γ=65 reasoning = 865 tokens), and treating the 2% fallback as single-shot (zero added turns), the expected input tokens across the distribution are:
- Expected input tokens: 0.68×(9,200+865) + 0.25×(9,200+1,730) + 0.05×(9,200+2,595) + 0.02×9,200 ≈ 6,844 + 2,733 + 590 + 184 ≈ **10,350 tokens** (expected total incl. 300-token output ≈ 10,650).
- Amplification *α*: 10,650 / 9,500 ≈ **1.12×** — about a **12%** token overhead. (The 2% fallback is explicitly included here at zero added turns: it adds no agent tokens, so its contribution to the expectation is 2% × 0 = 0, which the weighted sum above keeps.)
- Added agent-orchestration overhead (per-turn step + tool): 220 ms/turn. Because 68% terminate in one turn, the **median turns is T=1**, so the median added overhead is **1 × 220 ms ≈ 220 ms**; the **90th-percentile** is T=2 (cumulative 93% by T≤2) → **440 ms**; and the **95th-percentile** is T=3 (cumulative 98% by T≤3) → **660 ms** — *not* T≈4, since the scenario caps turns at 3 and the 2% fallback is modelled as an immediate single-shot fallback, not a fourth attempted turn. On top of the ~8.6 s base answer generation, L_E2E ≈ 8.6 s + 0.22 s ≈ ~8.8 s at the median.
- Total end-to-end: the request is dominated by the ~8.6 s base generation (Ch 8), not the added orchestration; the ~220–660 ms figures are the *added* agent/tool overhead, not the complete request latency.

**Architectural actions.** The team sets the turn limit to 3, instruments each turn's token and orchestration latency, and adds a context cache for the search tool. With the cache hit rate of 30% on recurring queries, the effective *δ* drops to ~560 tokens, reducing average amplification to ~1.09× (about a 9% token overhead); the median added orchestration overhead is still T=1 → ~220 ms. The claim "meets an SLA of <1 s" must be scoped carefully: the *added agent-orchestration* latency is comfortably under 1 s, but the **end-to-end** request is ~9 s because of the base generation. The architect therefore scopes the <1 s SLA to orchestration overhead *excluding* final generation, and treats end-to-end as bounded by the ~8.6 s base.

**Lesson.** The agentic layer added ~12% token overhead and ~220 ms of orchestration latency on the median (on top of an ~8.6 s base generation), but improved answer correctness on multi-step reasoning queries by an estimated 22% in an illustrative human-eval reading [ILLUSTRATIVE SCENARIO RESULT, not a reported production measurement]. The trade-off was acceptable — the added overhead is small relative to the base generation — and the token overhead was mitigated by context caching. The architect's key decisions were: (a) capping turns at 3, (b) adding a search cache, and (c) providing a single-shot fallback when the limit is hit.

---

**Table 19-1** — Token amplification and latency trade-offs for agentic RQA pipelines

| Metric | T=1 (median) | T=2 (90th pct) | T=3 (95th pct) | T=4 (beyond limit) | Single-shot |
|--------|-----|--------------|-----|----------------|-------------|
| Input tokens (9,200 + T·800 + T·65) | 10,065 | 10,930 | 11,795 | 12,660 | 9,200 |
| Total tokens (incl. 300 output) | 10,365 | 11,230 | 12,095 | 12,960 | 9,500 |
| Token amplification *α* | 1.09× | 1.18× | 1.27× | 1.36× | 1.00× |
| Per-turn agent step, 10K ctx | ~120 ms | ~120 ms | ~120 ms | ~120 ms | — |
| Tool latency (median) | ~100 ms | ~100 ms | ~100 ms | ~100 ms | — |
| Added orchestration overhead (T × 220 ms) | ~220 ms | ~440 ms | ~660 ms | ~880 ms | 0 ms |
| Base answer generation *L*base | ~8.6 s | ~8.6 s | ~8.6 s | ~8.6 s | ~8.6 s |
| Total end-to-end (Lbase + overhead) | ~8.8 s | ~9.0 s | ~9.3 s | ~9.5 s | ~8.6 s |
| KV cache @ 2.62 MB/token | ~27.2 GB | ~29.4 GB | ~31.7 GB | ~34.0 GB | ~24.9 GB |

*All token counts use δ=800, γ=65, O=300; orchestration overhead uses λ_step≈120 ms + λ_tool≈100 ms per turn; base generation uses the canonical ~8.6 s (1.08 s prefill + 7.5 s decode of 300 output tokens). Total end-to-end is dominated by the base generation, NOT the agent overhead. These are canonical-model [DERIVED] values, not measured production figures.*