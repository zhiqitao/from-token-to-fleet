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
- Opex (power + staff): power decomposed — 8 H100 GPUs at ~700 W TDP ≈ 5.6 kW of GPU IT load, plus ~2.2 kW for the host/network/other IT load → ~7.8 kW total IT; at a facility PUE (power-usage-effectiveness) of ~1.3 that is ~10.1 kW at the wall. At ~$0.15/kWh, always on, that is ~$1.1K/month. Staff/engineering alloc ~$10K/month. Total opex ≈ ~$11.1K/month. [2° DERIVED, illustrative]
- Monthly total ≈ $5.8K (capex) + $11.1K (opex) ≈ **$16.9K/month**.
- Per request at ~10 rps average = ~864,000 requests/day ≈ 26M/month. **Cost ≈ $16.9K / 26M ≈ $0.00065/request ≈ $0.65 per 1,000 requests.** [2° DERIVED] *(worked example, not reference)*

**Mode 2 — cloud GPU instances (rent, shut down when idle).**

- An 8×H100 on-demand instance ~$20/hr (canonical: $2.50/GPU-hr × 8), paid only while running, say ~40% duty cycle to cover peaks → ~$8/hr average effective → ~$5,760/month. [2° DERIVED]
- Per request: at 10 rps the same ~26M requests/month. **Cost ≈ $5,760 / 26M ≈ $0.00022/request ≈ $0.22 per 1,000 requests.** [2° DERIVED] *(cloud now roughly ties or exceeds self-host per request at this volume/duty; the $/hr-per-node basis and the duty-cycle assumption are the two levers. Staff & integration add on top.)*

**Mode 3 — managed inference API.**

- A hosted frontier-70B-class API at ~$0.002/input + ~$0.008/output per 1K tokens (typical as of 2026). The per-request token cost is

$$
\begin{aligned}
\text{cost/req} &= p_\text{in} \cdot \frac{I}{1000} + p_\text{out} \cdot \frac{O}{1000}\\
&= 0.002 \times 9.2 + 0.008 \times 0.3 \approx \$0.0184 + \$0.0024\\
&\approx \$0.0208 \approx \$20.8 \text{ per 1,000 requests}
\end{aligned}
$$

[2° FACT, illustrative]
- At the canonical 25.9M requests/month: ~$539,000/month — an order of magnitude above self-host. [2° DERIVED]

**Reading the result.** Self-hosted (~$0.65/1K reqs) beats the API (~$20.8/1K reqs) by ~32× on pure token cost at this volume — but only because we assume steady near-canonical utilization plus in-house staff we are not separately billing. Cloud-on-demand (~$0.22/1K) is roughly a third of self-host per request at this duty — but only if the duty cycle is ~40% and we ignore staff/integration. **The honest TCO answer depends on the duty cycle and on whether the staff term is a sunk cost.** Because self-host is a *fixed* cost (capex amortized + always-on power + staff); cloud on-demand is a *variable* cost (you pay only while the instance runs). Table 16-1b prices cloud across duty cycles against self-host on two bases — fully-loaded (staff billed) and staff-in-house (staff already on payroll, so sunk):

**Table 16-1b** — Cloud on-demand cost vs duty cycle (illustrative worked example; $/1K at canonical ~26M req/mo)

| Duty cycle | Cloud/mo | Cloud $/1K | vs self-host $0.65/1K (staff billed) | vs self-host $0.27/1K (staff sunk) |
|---|---|---|---|---|
| 20% | ~$2.9K | ~$0.11 | cloud wins | cloud wins |
| 40% | ~$5.8K | ~$0.22 | cloud wins | cloud wins |
| 60% | ~$8.6K | ~$0.33 | cloud wins | near crossover |
| 80% | ~$11.5K | ~$0.44 | cloud wins | self-host wins |
| 100% | ~$14.4K | ~$0.55 | cloud still cheaper | self-host wins |

*(Self-host with staff sunk ≈ $6.9K/mo → ~$0.27/1K: capex ~$5.8K + power ~$1.1K, no incremental staff.)*

The crossover emerges from the arithmetic, and it is **not** where one might expect. On a fully-loaded basis (staff billed at $10K/mo), **cloud is cheaper at every duty cycle** at this canonical volume, because an always-staffed self-host costs $16.9K/mo while the whole cloud bill tops out at ~$14.4K/mo even at 100% duty. Self-host only becomes clearly cheaper when the staff is *already in-house* (a sunk cost) *and* utilization is high — then the crossover lands around ~50–60% duty. This is the real lesson: at the scale of an internal Q&A tool, the decision is dominated by the **staff/ops term**, not the GPU rental rate. **The statement "self-host wins" is only true under the explicitly stated assumption that the team already exists and is not charged incrementally; under a fully-loaded cost basis, cloud wins at any duty cycle at this volume.** [2° DERIVED]

**Parametric sensitivity is the durable form.** All the fixed inputs above — GPU price, electricity, staffing, capacity, API price — are [ILLUSTRATIVE] scenario values; the *structure* of the model is what generalizes. The architect can see the decision flip with utilization and volume: at low effective utilization (~20%, e.g. a demo or dev workload), the always-staffed self-host sits idle while depreciating, so managed on-demand decisively wins; and even at high utilization, on a fully-loaded basis, cloud remains cheaper at this volume because the self-host staff term dominates. Self-host only clearly wins when the staff is *already in-house* (a sunk cost, not billed incrementally) *and* sustained utilization is high (~80%+). Rather than memorize one answer, the durable tool is a small parametric model — exact same arithmetic with GPU $/hr, $/kWh, staffing, and API price as inputs — which the architect re-runs with the customer's real numbers (Chapter 23). This is what makes TCO a decision *framework*, not a single verdict. A runnable, parameterised version of exactly this model ships with the book as `render/tco_calc.py` (defaults reproduce these numbers; override GPU $/hr, $/kWh, staffing, and API price as flags).

**Table 16-1** — TCO comparison across delivery modes (illustrative worked example)

| Mode | Capex | Opex/month | Cost/1K req | $/month @26M req | When it wins |
|---|---|---|---|---|---|
| Self-hosted 8×H100 | ~$350K | ~$16.9K | ~$0.65 | ~$16.9K | steady high utilization, staff available |
| Cloud on-demand | $0 | ~$5.8K (40% duty) | ~$0.22 | ~$5.8K+staff | low duty cycle, bursty, no staff for ops |
| Managed API | $0 | usage | ~$21 | ~$546K | tiny volume, fastest time-to-value |

*(Figures are worked-example estimates as of Q4 2026, not vendor quotes; treat as [2° DERIVED] illustrative, to be re-priced before budgeting.)*

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

*Break-even: monthly cost vs monthly volume for self-hosted and managed API across three serve modes, crossing at the ~1.02 M-request scale.*

<!-- Figure spec: mechanism-first plot; x = requests/month, y = cost per 1K requests; self-host curve high-intercept low-slope; managed-API zero-intercept linear; mark break-even volume; annotate the utilization assumption. -->

## 7. What We Still Don't Know

- **Real equipment/power/staff numbers** for a given deployment are (to be verified) site-specific; the illustrative quotes above must be re-priced.
- **How rapidly GPU list and amortization prices fall** over the 5-year horizon is (a hypothesis); newer cards (H200/B200-class) change the per-card economics.
- **The true staff overhead of self-hosting** (SRE time, security, upgrades) is (a hypothesis) until the team bills its own time honestly.

## 8. End-of-Chapter Mini-Case

A startup's CTO shows the architect a warrant to buy two 8×H100 servers for the new internal RAG assistant, citing "we'll save on token fees." Applying TCO discipline, the architect does not dispute the raw token math. Instead they price it: at this startup's *actual* early volume — ~5 rps average, ~5M requests/month, and only 0.5 engineers fully available for GPU ops — the break-even against a managed API sits just below that volume, and the staff term dwarfs the token savings. The honest number: self-hosting two servers ~$40K/month all-in vs ~$105K/month API at current volume, but the two-server option consumes a full engineer to keep utilization and reliability up — an opportunity cost the startup cannot yet afford. The architect's verdict: **start on the managed API now, revisit self-host at ~2× this volume or when a second engineer frees up**, and re-run the same model then. The CTO did not buy the servers — the break-even graph, with staff honestly included, made the answer self-evident.
