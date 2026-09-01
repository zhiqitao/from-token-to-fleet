# Chapter 23 — Working With Customers: From Vague Ask to Defensible Scope

## The Architect's Question

After this chapter we should be able to sit with a customer or stakeholder who says "we want to build something with AI" and turn that vague ambition into a bounded, measurable, defensible scope. We will apply the book's core loop in a conversational setting: ask the questions that surface the real workload (Ch4), the quality bar (Ch3/5), the latency and cost constraints, and the operational reality — then restate the requirement in terms we can architect against. After this chapter, "let's go build an AI thing" becomes "here are the bounds, the SLO, and the open questions" — and the customer knows exactly what they asked for.

## 1. Concept

Most AI projects fail in requirements, not in technology. The root cause is a **category error**: the customer and the architect mean different things by the same words. "Fast," "good," "smart," and "it should just work" are not contracts; they are vibes. The architect's first job is to convert vibes into **quantified, testable bounds** using the disciplines of the earlier chapters.

The conversion rests on one idea: **every architectural decision traces back to a number the customer can see.** Whether the model is 7B or 70B, whether we self-host or use an API, whether we cache, quantize, or disaggregate — all of it is decided by five numbers we can extract from a customer conversation:

1. **The traffic** — how many users, at what concurrency, with what peak-to-average ratio (Ch4/Ch17).
2. **The token profile** — what inputs look like, how long contexts are, the input/output ratio (Ch4/Ch6).
3. **The quality bar** — what "good enough" means on *this* task, on *their* data (Ch3/Ch5/Ch14).
4. **The latency/cost budget** — the SLO and the money they can spend (Ch6/Ch16).
5. **The operational reality** — data privacy, geography, available staff, time-to-value (Ch13/Ch21/Ch24).

## 2. Mental Model

Think of the customer conversation as **buying information, not delivering answers.** We are not in the room to impress; we are in the room to learn the five numbers. Three mental moves keep the conversation productive:

- **The Socratic funnel.** Start broad ("what problem are we solving?") and narrow through a scripted set of questions that each commit the customer to a concrete bound. Every "vague" answer gets followed by a request for magnitude: "roughly how many users?" "what's the slowest acceptable answer?"
- **The mirror test.** Restate their words back as a quantified requirement and check they still agree. "So: ~2,000 users, under 2 seconds to first token, on company-internal data — did I get that right?" The restatement is where scope actually gets locked.
- **The two-window honesty.** Separate what the customer *thinks* (goals) from what the *system* can guarantee (SLOs). Goals are aspirations; SLOs are contracts. Confusing them breeds every fee dispute and scope fight.

## 3. Worked Example

### The Requirements Dialogue: Turning "an internal AI assistant" Into Bounds

**[Worked example dialogue — illustrative, not reference.]** An internal-platform lead says: "We want an AI assistant for our sales teams — it should answer questions from our product docs and CRM data, and it should be fast." [2°]

**Architect:** "~How many people will use it, and how often?"
**Lead:** "~2,000 on the platform; maybe 10% are in it at once at peaks."
**Architect:** "So ~200 concurrent at peak, and realistically a fraction of that firing requests. Roughly how many questions per second at the busiest minute?"
**Lead:** "If everyone on the sales floor asked at once, maybe 40 a second."
**→ Bound 1: ~2,000 users, ~10 rps average, ~40 rps peak.** [1P §14]

**Architect:** "What does a question look like? Short or with long context?"
**Lead:** "They paste product specs and contracts, so the prompt can be lengthy — a few pages."
**→ Bound 2: long ~9,200-token inputs with retrieval, ~300-token outputs.** [1P §14]

**Architect:** "What's 'fast'? First-word delay, or time to full answer?"
**Lead:** "Feels slow if we wait more than two seconds to see something start."
**→ Bound 3: TTFT ≤ 2 s (p95), ~25 ms/token thereafter.** [1P §14]

**Architect:** "What does 'good answer' mean for your team — and can we define a handful of sample questions to test against?"
**Lead:** "It should be accurate on our docs and not make up contract terms. We can give the validation team 50 real questions."
**→ Bound 4: a 50-question retrieval-QA quality benchmark on their actual data.** [1P §14]

**Architect:** "Data sensitivity — can this touch a public cloud, and how much can it cost?"
**Lead:** "It's internal and regulated; keep it on-prem if at all possible."
**→ Bound 5: operational constraint forces the local/server tier (Ch13).** [1P §14]

**Architect (mirror):** "So to lock it: ~2,000 sales users, ~10 rps average / 40 peak, prompts with ~9,200-token retrieval context, answers starting under 2 s, quality judged on 50 of your real questions, and fully on-prem because it's regulated. Have I captured it?"
**Lead:** "Yes — that's exactly it."

**Reading the result.** The vague ask collapsed into the exact canonical workload this book has architected end-to-end — a 70B-class model on an 8×H100 on-prem server meets every bound (Ch2-16). The conversation did not sell a model; it *exposed the numbers* that then chose the architecture with almost no further input. [2° DERIVED] *(worked example, not reference)*

**Table 23-1** — The six questions that turn any vague AI ask into architectable bounds

| Question | Surface it reveals | Canonical answer (this example) |
|---|---|---|
| ~How many users, how concurrent? | Traffic & concurrency (Ch4/17) | ~2,000 users, ~10/40 rps |
| What do inputs look like? | Token profile (Ch4/6) | ~9.2K in / ~300 out |
| What's "fast"? | SLO (Ch6) | TTFT ≤ 2 s, ~25 ms/token |
| What's "good"? | Quality bar (Ch3/14) | 50-question retrieval-QA set |
| Data sensitive? Cloud OK? | Tier & ops (Ch13) | on-prem, regulated |
| How much can it cost? | TCO (Ch16) | within self-host budget |

## 4. Measurement

The requirements dialogue has its own quality metrics:

1. **Bound coverage** — did the conversation surface all five numbers (traffic, tokens, quality, latency/cost, ops)? Missing one is a future scope surprise.
2. **Customer buy-in** — did the mirrored restatement get an explicit "yes"? An unconfirmed restatement is not a scope.
3. **Decision lead time** — how quickly the five bounds let us produce a defensible draft architecture. The whole point is that extracting numbers, not more meetings, unlocks the design.
4. **Assumption log** — every guess we made that the customer did not explicitly confirm, tracked as [VERIFY] items, not silent defaults.

## 5. Common Mistakes

- **Selling before scoping.** Pitching a model or a price before extracting the five numbers commits us to an answer we cannot yet defend.
- **Accepting aspirations as SLOs.** "Make it fast" is a goal; "p95 TTFT under 2 s" is a contract. Write the contract.
- **Letting the customer choose the technology.** "We want a 70B model" is a solution, not a requirement; the architect derives the model from the bounds (Ch5), not from the customer's guess.
- **Ignoring the operational constraint.** "It has to be on-prem / private / no cloud" often decides more than any performance number — surface it early.
- **Not logging assumptions.** Every silence becomes a hidden assumption that surfaces as a dispute later. Write them down as [VERIFY] items.

## 6. Architecture Consequence

The requirements conversation is where the book's entire loop is *fed.* The five bounds it extracts are exactly the inputs Ch1-16 consume: traffic feeds capacity (Ch17), tokens feed KV/memory (Ch7), quality feeds model selection (Ch5), latency feeds serving (Ch11), cost feeds TCO (Ch16), and the operational constraint picks the tier (Ch13). A good requirements session is not a warm-up to architecture — it *is* the first chapter of the architecture, and every downstream decision traces back to the numbers it locked. [2°]

![Fig 23.1 — From vague ask to architectural bounds [ILLUSTRATIVE conceptual]](figures/fig-23-2301.png)

*Fig 23.1 — The framing funnel: broad ask → five Socratic questions (problem, success, data, constraints, scope) → confirmed bounds. This is the *dialogue* that surfaces requirements; the *six* architectural surfaces in Table 23-1 are what each answer reveals (traffic, token profile, SLO, quality, ops/tier, TCO). [ILLUSTRATIVE conceptual]*

<!-- Figure spec: mechanism-first funnel diagram; top = vague ambition; five labeled question gates narrow it; bottom = quantified scope feeding the architecture loop. -->

## 7. What We Still Don't Know

- **How accurate the customer's own-told numbers are** ("40 rps peak") is [VERIFY]; peak estimates are notoriously optimistic and should be triangulated with real logs where possible.
- **Whether the quality bar once defined stays stable** is [HYPOTHESIS]; as users adopt the tool, their expectations and the data they query both shift.
- **The right number of questions to lock quality** is [VERIFY]; 50 worked here as a representative proxy but a larger, task-distributed set is stronger.

## 8. End-of-Chapter Mini-Case

A CTO emails the architect: "We heard LLMs are great — let's put one on our customer portal to answer support tickets. Shipping it next month." Rather than confirm the launch date, the architect books a 30-minute session and runs the funnel. It emerges the portal gets ~5 rps average but 200-rps bursts during outage events (traffic), tickets are short (~500 tokens, not retrieval-heavy), quality means "resolve the ticket, not just answer" (a capability the cheaper model screens out), the SLO is 3 s because users are already frustrated (latency), and — critically — the portal sits on regulated payment data so nothing leaves the premises (ops). The mirrored restatement turns "let's ship AI next month" into "a 7B-class model on one on-prem GPU, resolving baseline tickets under 3 s, with a 200-rps burst buffer, quality-gated on real resolved tickets — and a two-week pilot on 5% of tickets to confirm the referral quality before full rollout." The customer's vague excitement became a defensible, bounded, shippable scope — and the architect is already architecting, not guessing.
