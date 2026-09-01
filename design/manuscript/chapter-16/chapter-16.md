# Chapter 16 — TCO: The Total Cost Reality Check

## The Architect's Question

After this chapter we should be able to answer the question every stakeholder actually asks — *what does this really cost?* — with a defensible number, not a guess. We will build a total-cost-of-ownership model that separates capital, operating, and opportunity costs, then price the canonical workload across three delivery modes: self-hosted on our own cards, cloud GPU instances, and a managed inference API. After this chapter, "we save money by self-hosting" is either proven or refuted by arithmetic, and the break-even point between modes is explicit.

## 1. Concept

Total Cost of Ownership (TCO) is the sum of everything required to deliver a capability over its lifetime, not just the price tag of the hardware or the per-token rate. It has three cost families:

1. **Capital (capex)** — the one-time cost of the cards, servers, networking, racks, and cooling that make up the system. For self-hosted inference this dominates up front: an 8×H100 server with networking and infrastructure carries a large price. [2° FACT]

2. **Operating (opex)** — the recurring cost of running it: electricity and cooling, staff, software/licenses, cloud instance rental, and replacement/amortization of hardware. For cloud and managed API this is the whole cost; for self-hosted it compounds on capex.

3. **Opportunity** — the cost of the *alternative not taken*: the team time spent operating vs building, the delay to market, and the engineering hours that do not scale with either card or token counts. This is the most omitted and often the largest term.

The architect's job is not to minimize capex, nor opex, nor provider bill — it is to minimize **the number that matters for the organization's decision**, which usually means total cost per useful request at the required quality and SLO.

## 2. Mental Model

Think of TCO as **a utilization-weighted average over the whole system, not a sticker price.** Three mental moves keep the arithmetic honest:

- **Amortize, don't stare at the price tag.** A $400K server is an asset consumed over ~5 years; spread it into dollars-per-month, then into dollars-per-request, before comparing to a per-token API rate. [2° DERIVED]

- **Follow the token, not the GPU.** The thing being bought is completed, SLO-meeting requests. Two systems with the same card count can differ 10× in cost per request if one has 3× the goodput per card, better utilization, or no idle coasting.

- **Include what does not scale.** Staff, power, networking engineering, and the latency of procurement are sunk or recurring whether utilization is 20% or 80%. A low-cost-per-card system that burns engineers can be the most expensive.

The decision shape is a **break-even graph**: at low volume, managed/cloud-and-shut-down wins (no idle capex); at high volume, self-hosted cards amortize below the per-token rate. The crossover point is what we compute.

## 3. Worked Example

### Pricing the Canonical Workload Across Three Modes

We price the canonical 70B enterprise-Q&A workload at the canonical traffic (~10 rps average, ~40 rps peak, ~9,200 input + ~300 output tokens per request). [1P §14]

**Mode 1 — self-hosted on owned cards (8×H100).**

- Capex: assume ~$350K for a fully built 8×H100 server (cards, host, NVSwitch, networking, rack, cooling), amortized over 5 years → ~$70K/year, ~$5,800/month. [2° FACT, illustrative]
- Opex: power + cooling for 8×H100 at ~50 kW, ~$0.15/kWh, always on → ~$65K/year; staff/engineering alloc ~$120K/year; total opex ~$185K/year. [2° DERIVED, illustrative]
- Monthly total ≈ $5,800 (capex) + $15,400 (opex) ≈ **$21,200/month**.
- Per request at ~10 rps average = ~864,000 requests/day ≈ 26M/month. **Cost ≈ $21,200 / 26M ≈ $0.00082/request ≈ $0.82 per 1,000 requests.** [2° DERIVED] *(worked example, not reference)*

**Mode 2 — cloud GPU instances (rent, shut down when idle).**

- An 8×H100 on-demand instance ~$3.50/hr (Ch4 reconciled), paid only while running, say ~40% duty cycle to cover peaks → ~$1.40/hr average effective → ~$1,000/month. [2° DERIVED]
- Per request: at 10 rps the same ~26M requests/month. **Cost ≈ $1,000 / 26M ≈ $0.000038/request ≈ $0.04 per 1,000 requests.** [2° DERIVED] *(cloud beats self-host per request ONLY at low duty cycle; the $/hr must cover staff & integration too.)*

**Mode 3 — managed inference API.**

- A hosted frontier-70B-class API at ~$0.002/input + ~$0.008/output per 1K tokens (typical as of 2026). The per-request token cost is

$$
\text{cost/req} = p_\text{in} \cdot \frac{I}{1000} + p_\text{out} \cdot \frac{O}{1000} = 0.002 \times 9.2 + 0.008 \times 0.3 \approx \$0.0184 + \$0.0024 \approx \$0.0208 \approx \$20.8 \text{ per 1,000 requests}
$$

[2° FACT, illustrative]
- At the canonical 25.9M requests/month: ~$539,000/month — an order of magnitude above self-host. [2° DERIVED]

**Reading the result.** Self-hosted (~$0.82/1K reqs) beats the API (~$20.8/1K reqs) by ~25× on pure token cost at this volume — but only because we assume steady near-canonical utilization plus in-house staff we are not separately billing. Cloud-on-demand ($0.04/1K) looks cheapest only if duty cycle is low AND we ignore staff/integration. The honest TCO answer for a business-critical, always-on service at canonical volume is **self-hosted cards**, with the caveat that the staff term is the real swing factor. [2° DERIVED]

**Parametric sensitivity is the durable form.** All the fixed inputs above — GPU price, electricity, staffing, capacity, API price — are [ILLUSTRATIVE] scenario values; the *structure* of the model is what generalizes. The architect can see the decision flip with utilization and volume: if effective utilization is low (~20%, e.g. a demo or dev workload), self-hosted cards sit idle while depreciating, and managed on-demand wins; near the crossover (~50–60% utilization at canonical volume) the two are close and the decision hinges on the staff/risk terms; only at sustained high utilization (~80%+) does self-hosted clearly win on cost-per-request. Rather than memorize one answer, the durable tool is a small parametric model — exact same arithmetic with GPU $/hr, $/kWh, staffing, and API price as inputs — which the architect re-runs with the customer's real numbers (Chapter 23). This is what makes TCO a decision *framework*, not a single verdict. A runnable, parameterised version of exactly this model ships with the book as `render/tco_calc.py` (defaults reproduce these numbers; override GPU $/hr, $/kWh, staffing, and API price as flags).

**Table 16-1** — TCO comparison across delivery modes (illustrative worked example)

| Mode | Capex | Opex/month | Cost/1K req | $/month @26M req | When it wins |
|---|---|---|---|---|---|
| Self-hosted 8×H100 | ~$350K | ~$21.2K | ~$0.82 | ~$21K | steady high utilization, staff available |
| Cloud on-demand | $0 | ~$1K (40% duty) | ~$0.04 | ~$1K+staff | low duty cycle, bursty, no staff for ops |
| Managed API | $0 | usage | ~$21 | ~$546K | tiny volume, fastest time-to-value |

*(Figures are worked-example estimates as of Q4 2026, not vendor quotes; treat as [2° DERIVED] illustrative, [VERIFY] before budgeting.)*

## 4. Measurement

Four metrics keep the TCO model honest:

1. **Cost per useful (SLO-meeting) request** — the decision number; divide total cost by goodput-meeting requests (Ch6), not raw tokens.
2. **Effective utilization** — actual goodput ÷ theoretical capacity across the billing period; low utilization is the hidden tax in both capex and rented instances.
3. **Break-even volume** — the requests/month where self-host cost-per-request crosses managed API; below it, don't buy cards.
4. **Staff/duty-cycle adjusters** — the engineering-hours and duty-cycle assumptions that dominate the comparisons; measure them, don't assume.

## 5. Common Mistakes

- **Comparing sticker price to per-token rate.** A $/1K-token API quote already includes amortization; a card price tag does not. Amortize both.
- **Ignoring the staff/ops term.** Self-host "saves money" on paper and loses the moment two engineers are consumed full-time.
- **Assuming 100% utilization.** Idle cards are still burning electricity and depreciation; bake duty cycle in.
- **Forgetting opportunity cost.** A 6-month procurement cycle versus a same-week API integration is a real cost measured in time-to-value.
- **Using peak capacity for cost-per-request.** Peak sizing (40 rps) overstates cost if average (10 rps) utilization is what governs.

## 6. Architecture Consequence

TCO is the final gate in the design loop (Ch12 candidates → Ch14 benchmark → Ch16 cost). It settles which candidate survives: the 70B 8×H100 self-host passes the capability screen, meets the SLO in the benchmark, and wins on TCO at canonical volume — completing the chain from vague requirement to a defensible, costed architecture. It also feeds fleet decisions (Ch17-18): the break-even curve is what justifies buying a second host versus renting peaks, and the staff term is what pushes toward consolidation (Ch18).

![Fig 16.1 — TCO break-even: self-hosted vs managed API [2° DERIVED]](figures/fig-16-1601.png)

*Fig 16.1 — Break-even: monthly cost vs monthly volume for self-hosted and managed API across three serve modes, crossing at the ~1.02 M-request scale.*

<!-- Figure spec: mechanism-first plot; x = requests/month, y = cost per 1K requests; self-host curve high-intercept low-slope; managed-API zero-intercept linear; mark break-even volume; annotate the utilization assumption. -->

## 7. What We Still Don't Know

- **Real equipment/power/staff numbers** for a given deployment are [VERIFY] site-specific; the illustrative quotes above must be re-priced.
- **How rapidly GPU list and amortization prices fall** over the 5-year horizon is [HYPOTHESIS]; newer cards (H200/B200-class) change the per-card economics.
- **The true staff overhead of self-hosting** (SRE time, security, upgrades) is [HYPOTHESIS] until the team bills its own time honestly.

## 8. End-of-Chapter Mini-Case

A startup's CTO shows the architect a warrant to buy two 8×H100 servers for the new internal RAG assistant, citing "we'll save on token fees." Applying TCO discipline, the architect does not dispute the raw token math. Instead they price it: at this startup's *actual* early volume — ~5 rps average, ~5M requests/month, and only 0.5 engineers fully available for GPU ops — the break-even against a managed API sits just below that volume, and the staff term dwarfs the token savings. The honest number: self-hosting two servers ~$40K/month all-in vs ~$105K/month API at current volume, but the two-server option consumes a full engineer to keep utilization and reliability up — an opportunity cost the startup cannot yet afford. The architect's verdict: **start on the managed API now, revisit self-host at ~2× this volume or when a second engineer frees up**, and re-run the same model then. The CTO did not buy the servers — the break-even graph, with staff honestly included, made the answer self-evident.
