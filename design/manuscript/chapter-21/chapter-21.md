# Chapter 21 — The AI Factory: Turning Inference Into an Industrial Process

## The Architect's Question

After this chapter we should be able to treat AI delivery as an *industrial process* rather than a one-off project: a repeatable factory with automated pipelines for data, evaluation, promotion, and rollback. We will separate the three layers of the factory (the model lifecycle, the serving pipeline, and the operations loop), then build the economics of promotion gating and retraining cadence for the canonical workload. After this chapter, "we ship a better model" is a gated, measurable, reversible event — not a risky redeploy.

## 1. Concept

The AI Factory is the discipline of making model delivery routine. We use the term as a **generic architectural concept** — the idea that model delivery can be run as an industrial, gate-driven process — not as any one vendor's marketing vocabulary. It rests on three pillars:

1. **Data pipeline** — the automated intake, cleaning, versioning, and labelling of the data that trains or evaluates the model. For a RAG system this includes the retrieval corpus, its freshness, and its quality gates. [ILLUSTRATIVE][DERIVED]

2. **Evaluation & promotion gate** — a systematic process that scores a candidate model or configuration against defined metrics (quality, latency, cost) on a held-out benchmark before it can replace the incumbent in production. This is where Ch14's deployment benchmarking becomes a recurring gate rather than a one-time event.

3. **Serve + observe + rollback** — the serving layer (Ch11) plus a feedback loop that measures real traffic, detects drift or regression, and can roll the production model back safely. [ILLUSTRATIVE][DERIVED]

The factory converts the architect's recurring question from "should we adopt this model?" (a one-off decision) into "does this candidate pass the automated gate?" (a routine, repeatable decision with the same rigor every time).

## 2. Mental Model

The AI Factory is best read as a **release pipeline with a quality gate placed before every promotion**, mirroring how software CI/CD gated deployments decades ago. Three mental moves:

- **Models are artifacts like code.** They get versioned, tested, reviewed, and promoted through environments (staging → canary → production) with automated checks at each step — not dropped into prod on a hunch.
- **The gate is the memory of the factory.** The evaluation suite and its thresholds encode everything we've learned about what "good enough" means (Ch4 capability, Ch14 deployment). If the gate is weak, the factory has no standards.
- **Everything is reversible.** A promotion that regresses metrics must be rollback-able in minutes. The factory's value is not eliminating errors but making them cheap and safe.

The factory's shape is a **pipeline with decisions**: data in → train/fine-tune → evaluate → push to canary → observe → promote or rollback → serve. Each arrow is a decision point, and each decision point is where an architect has influence.

## 3. Worked Example

The example below works the economics of promotion gating on the canonical 70B RAG workload.

### The Economics of Promotion Gating for the Canonical Workload

We show the factory's value by comparing *ungated* and *gated* adoption of a candidate model on the canonical 70B RAG workload (~10 rps average, ~9.2K-in/~300-out). [canonical scenario] (Ch 4, Table 4-2)

**Setup.** Suppose a new model candidate claims better retrieval-QA quality but no one has measured its serving behavior. Two adoption paths:

- **Ungated**: deploy the candidate to all production traffic immediately. If it regresses (say p95 TTFT degrades because of a slower tokenizer, or quality drops on a subset), the service suffers until rollback.
- **Gated**: run the candidate on a 5% canary for N hours, measure TTFT/goodput/quality against the incumbent, promote only if it beats every threshold.

\Needspace{5\baselineskip}

**Cost of a bad ungated release.** The canonical service does ~288,000 requests/workday (10 rps × 8 h × 3,600 s; ~6.24M/month — Ch 4's 8-h × 260-workday calendar basis, computed in Ch 16). Suppose a regression raises p95 TTFT from 1.9 s to 2.8 s (breaching the 2 s SLO) for 6 hours before discovery and rollback. That is 6/8 ×288,000 ≈ **216,000 requests** served at a broken SLO. At the Ch16 canonical self-hosted rate of ~$24.97/1K requests (active business-hours volume, Ch 4), the direct cost is 216,000 × 24.97066185897436 ÷ 1,000 ≈ **$5,394**, and it is ≈ **$3,032** on the Ch16 cloud-scaled ~$14.04/1K basis (216,000 × 14.038461538461538 ÷ 1,000 = 3,032.31) — modest relative to the *business* cost, but the dominant term is users experiencing a 47% latency regression, trust erosion, and the fire drill. [ILLUSTRATIVE][DERIVED] *(worked example, not reference)*

**Cost of a good gated release.** A canary at 5% traffic for 2 hours serves 5% × 288,000 ×2/8 ≈ **3,600 requests** through the candidate while it is measured against a full evaluation suite. If it passes, promotion is low-risk; if it fails, no users beyond canary were exposed. [ILLUSTRATIVE][DERIVED]

**Reading the result.** Gating turns a risky 216K-request exposure (ungated) into a controlled ~3.6K-request canary — a ~60× reduction in blast radius for the cost of a 2-hour evaluation. The factory makes this routine. [ILLUSTRATIVE][DERIVED]

**Table 21-1** — Ungated vs gated model adoption (illustrative worked example)

| Adoption | Requests exposed | SLO breach risk | Discovery | Rollback | Best when |
|---|---|---|---|---|---|
| Ungated | ~216K in a bad release | high (all traffic) | post-hoc | slow | tiny/experimental |
| Gated (5% canary) | ~3.6K | low (confined) | automated | fast | business-critical serving |

*(ILLUSTRATIVE worked example: the canary arithmetic is DERIVED from the stated workload inputs — 5% traffic, 2-hour window, ~288,000 requests/workday — and is illustrative, not a reference measurement. The workload inputs are sourced from the canonical scenario (Ch 4, Table 4-2); the 2-hour/5% choices are held-out example assumptions, to be re-set per deployment.)*

## 4. Measurement

The configuration qualification in Chapter 18 supplies the candidate identity for these gates: model, precision, backend and relevant runtime versions. A changed execution path needs new evidence; a previous model-level approval does not establish that the new configuration is safe to promote.

The factory is only as trustworthy as its gates. We measure four things continuously:

1. **Gate pass rate / false-promotion rate** — how often a gated change later regresses in production; a rising value means the evaluation suite is losing fidelity.
2. **Canary-to-production time** and **rollback time** — the speed of promotion and escape; both should be minutes, not days.
3. **Model freshness / data staleness** — time since the retrieval corpus or model was last validated; drift detection feeds the retraining decision.
4. **MTTR for a bad release** — mean time to detect + rollback; the factory's core reliability number.

## 5. Common Mistakes

- **No gate, or a decorative gate.** An evaluation that always passes is worse than none because it grants false confidence.
- **Promoting on quality only.** Quality passing but serving (Ch14) regressing still breaks the service; the gate must include deployment metrics.
- **Assuming retraining cadence is "as often as possible."** More frequent retraining is not free — it consumes compute, risk, and evaluation effort; the right cadence balances drift against churn (see Ch7-8 for training economics).
- **Skipping rollback rehearsal.** A rollback that has never been exercised will fail precisely when it is needed.
- **Treating the factory as a build-once artifact.** It is a living process that must absorb new models, new metrics, and new data sources continuously.

## 6. Architecture Consequence

The AI Factory is the operational backbone that makes the book's whole loop durable. Every architectural decision recomputes through it: model selection (Ch3/5) feeds the evaluation gate, serving choices (Ch11) determine canary mechanics, benchmarking (Ch14) becomes the recurring gate, TCO (Ch16) sets how much gating overhead is affordable, and fleet operations (Ch17-20) provide the rollout/rollback surfaces. Without the factory, each chapter's decision is a one-off; with it, they compound into a system that gets better and safer every cycle.

\begingroup\makeatletter\def\fps@figure{!htb}\makeatother

![Fig 21.1 — The model-lifecycle layer runs Data → Train → Eval → Canary → Observe → Promote → Serve. Six gates align with the transition seams: PASS permits the next stage; each labeled FAIL branch restores last-known-good state and re-validates. Production feedback returns evidence to data/evaluation, where the gates apply again. [ILLUSTRATIVE] conceptual](figures/fig-21-2101.png)

\endgroup

<!-- Figure spec: seven forward stages; decision ticks at the six transition seams; six labeled failure branches to a separate rollback node; production feedback to data/evaluation. -->

## 7. What We Still Don't Know

- **The true cost of model churn** (retraining + reeval + redeploy) per productivity gain is (a hypothesis) and workload-specific; there is no universal cadence.
- **How well evaluation suites generalize** across distribution shifts in real traffic is (to be verified); a suite tuned on last quarter's data may misjudge this quarter's model.
- **The right canary size** for a given risk posture is to be verified per service; 5% worked here but high-risk systems may need smaller, staged canaries.

## 8. End-of-Chapter Mini-Case: The Vendor's 'Better Bench': Canary and Rollback

A vendor pitches the architect a newer, cheaper model: "just swap it in — it scores better on the bench." A year ago the architect might have, and watched p95 TTFT silently drift past the SLO for a week. Now the AI Factory is in place. The architect drops the candidate into the pipeline: the data pipeline versions it, the evaluation gate scores it against quality AND the deployment benchmark (TTFT/goodput/cost) on the canonical workload, and a 5% canary serves it for two hours. The gate flags a quality regression on the legal-document subset the benchmark suite specifically covers — a subset the vendor's "better bench" never measured. The candidate is rejected automatically, the incumbent stays, and the legal subset keeps working. No fire drill, no user-visible regression, no manual heroics — the factory made the wrong vendor claim cost nothing to the business, which is precisely what industrializing the delivery loop is for.

## 9. Transition to Part VI

Parts I–V traced one engagement: token accounting defines workload demand; model architecture sets compute and memory costs; parallelism adds communication; serving schedules shared resources; fleet design determines capacity and cost; the AI Factory governs changes. These mechanisms connect request-level behavior to operational decisions.

Part VI applies these mechanisms to decisions under uncertainty rather than introducing another subsystem. It makes the decision process explicit: state workload assumptions, compare alternatives against resource bounds, and identify the measurements needed to resolve uncertainty. The next chapters provide a worksheet for recording the decision, its assumptions, and its validation criteria.
