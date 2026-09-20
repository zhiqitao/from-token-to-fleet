# Chapter 16 — TCO: The Total Cost Reality Check

## The Architect's Question

After this chapter we should be able to answer the question every stakeholder actually asks — *what does this really cost?* — with a defensible number, not a guess. We will build a total-cost-of-ownership model that separates capital, operating, and opportunity costs, then price the canonical workload across three delivery modes: self-hosted on our own cards, cloud GPU instances, and a managed inference API. After this chapter, "we save money by self-hosting" is either proven or refuted by arithmetic, and the break-even point between modes is explicit.

## 1. Concept

Total Cost of Ownership (TCO) is the sum of everything required to deliver a capability over its lifetime, not just the price tag of the hardware or the per-token rate. It has three cost families:

1. **Capital (capex)** — the one-time cost of the cards, servers, networking, racks, and cooling that make up the system. For self-hosted inference this dominates up front: an 8×H100 server with networking and infrastructure carries a large price. [ILLUSTRATIVE][DERIVED]

2. **Operating (opex)** — the recurring cost of running it: electricity and cooling, staff, software/licenses, cloud instance rental, and replacement/amortization of hardware. For cloud and managed API this is the whole cost; for self-hosted it compounds on capex.

3. **Opportunity** — the cost of the *alternative not taken*: the team time spent operating vs building, the delay to market, and the engineering hours that do not scale with either card or token counts. This is the most omitted and often the largest term.

The architect's job is not to minimize capex, nor opex, nor provider bill — it is to minimize **the number that matters for the organization's decision**, which usually means total cost per useful request at the required quality and SLO.

## 2. Mental Model

TCO is **a utilization-weighted average over the whole system, not a sticker price.** Three mental moves keep the arithmetic honest:

- **Amortize, don't stare at the price tag.** A $400K server is an asset consumed over ~5 years; spread it into dollars-per-month, then into dollars-per-request, before comparing to a per-token API rate. [ILLUSTRATIVE][DERIVED]

- **Follow the token, not the GPU.** The thing being bought is completed, SLO-meeting requests. Two systems with the same card count can differ 10× in cost per request if one has 3× the goodput per card, better utilization, or no idle coasting.

- **Include what does not scale.** Staff, power, networking engineering, and the latency of procurement are sunk or recurring whether utilization is 20% or 80%. A low-cost-per-card system that burns engineers can be the most expensive.

The decision shape is a **break-even graph**: at low volume, managed/cloud-and-shut-down wins (no idle capex); at high volume, self-hosted cards amortize below the per-token rate. The crossover point is what we compute.

## 3. Worked Example

### Size the fleet first, then price it

TCO is meaningless until we know **how many hosts the workload actually requires**. The reviewer's sharpest point stands: a single 8×H100 host can only sustain ~2.1 req/s under the KV/latency bound (Chapter 17/20), so it cannot serve even the canonical 10 rps average, let alone the 40 rps peak. We therefore size the fleet first (Ch 17) and price it second.

**Step 1 — fleet size.** The canonical workload requires N_hosts = max(N_throughput, N_KV, N_SLO). With the ~8.6 s service time and C≈18 KV-resident requests/host (Ch 17):

| Sizing bound | Average (10 rps) | Peak (40 rps) |
|---|---|---|
| Throughput (per-host ~2.1 req/s) | ⌈10/2.1⌉ = 5 hosts | ⌈40/2.1⌉ = 20 hosts |
| KV (in-flight λ·W / C) | ⌈10×8.6/18⌉ = 5 hosts | ⌈40×8.6/18⌉ = 20 hosts |
| **N_hosts (max)** | **~5 hosts** | **~20 hosts** |

So the canonical workload's *peak* requires roughly **20 hosts** (FP16 KV, full utilization; ~28 at the 70% utilization target), and even the *average* needs ~5 — a fleet, not one box. (FP8 KV roughly halves this to ~11 hosts at peak.) **Every TCO figure below is scaled to this fleet requirement — the earlier drafts priced a single host, which understated the cost by roughly 4–20×.**

**Step 2 — price each mode on N_hosts ≈ 20 (FP16, provisioned for the 40 rps peak).**

**Mode 1 — self-hosted on owned cards (20 × 8×H100).**

- Capex: ~$350K per fully built 8×H100 server, amortized over 5 years → ~$5.8K/month/host → ~$116K/month for ~20 hosts. [ILLUSTRATIVE][DERIVED], scenario value [ILLUSTRATIVE]
- Opex (power + staff): per host, 8 H100 GPUs at ~700 W ≈ 5.6 kW GPU IT + ~2.2 kW host/network ≈ 7.8 kW IT, × PUE ~1.3 ≈ ~10.1 kW at the wall; at ~$0.15/kWh always-on that is ~$1.1K/month/host → ~$22K/month for ~20 hosts. Staff/engineering alloc ~$10K/month. [ILLUSTRATIVE][DERIVED], scenario value [ILLUSTRATIVE]
- Monthly total ≈ $116K + $22K + $10K ≈ **~$148K/month** for ~20 hosts.
- Per request at ~10 rps average = ~26M/month. **Cost ≈ $148K / 26M ≈ $0.0057/request ≈ $5.7 per 1,000 requests.** [ILLUSTRATIVE][DERIVED] *(worked example, not reference)*

**Mode 2 — cloud GPU instances (rent, scale to load).** An 8×H100 on-demand instance ~$20/hr (canonical $2.50/GPU-hr × 8). Because the workload's *peak* is 40 rps, the fleet must be able to burst to ~20 instances, but the *average* load is ~5 hosts' worth — so the honest cloud bill is the instance-hours actually required. That requires a **load-duration / capacity-occupancy model**, not a single average. Parameterize the monthly cloud host-hours as the integral of required capacity over time, plus the warm-pool and capacity-reservation terms:

$$
H_\text{cloud,month} = \int_0^T N_\text{required}(t)\,dt \;\; \text{plus a warm/startup pool and any capacity-reservation guarantee}
$$

where $N_\text{required}(t)$ is the number of hosts that must be running at time $t$ (a step function that rises with the load curve at that hour of the day/week). This depends on the actual temporal load profile — the **burst duration and frequency**, the **scale-up latency** (how many seconds/minutes to attach and load a fresh instance), the **model-loading/warmup time** (loading a 140 GB model into a new host is not instant), the **minimum warm pool** to serve the base load without cold-starting, **provider capacity/availability**, and **billing granularity**. Only if the provider can attach instances faster than the load curve demands, with a warm pool already holding the model, can the cloud bill approach the pure average-load figure.

Under a simplified assumption of a continuously-arriving ~5-host average load that bursts briefly to ~20 at the peak, with a steady warm pool and fast scale-up, that is ≈ 5 × $20/hr × 720 hr ≈ ~$72K/month (scaling the fleet with load; always-on-at-peak would be ~$288K/month). **[ILLUSTRATIVE][DERIVED]** — this is *explicitly* a assumed load-duration curve and fast elastically-scalable capacity, not a measured or guaranteed cost. If the burst is long-lived or scale-up is slow, the real cloud cost rises toward the always-on-at-peak figure and the "cloud is cheapest" result weakens accordingly. The durable lesson — *fleet size first, price second* — does not depend on this elasticity assumption, but the specific $2.8/1K number does.

- Per request: ~26M/month. **Cost ≈ $72K / 26M ≈ $0.0028/request ≈ $2.8 per 1,000 requests.** [ILLUSTRATIVE][DERIVED] *(The "duty cycle" here is **fleet capacity utilization** — how many of the provisioned hosts are busy on average — NOT the literal fraction of wall-clock time an instance is powered on. A continuously-arriving 10-rps workload cannot be served by shutting the only instance off 60% of the time; it needs a fleet that is always available and scales with load. Staff & integration add on top.)*

**Mode 3 — managed inference API.**

- A hosted frontier-70B-class API at ~$0.002/input + ~$0.008/output per 1K tokens (typical as of 2026). The per-request token cost is

$$
\begin{aligned}
\text{cost/req} &= p_\text{in} \cdot \frac{I}{1000} + p_\text{out} \cdot \frac{O}{1000}\\
&= 0.002 \times 9.2 + 0.008 \times 0.3 \approx \$0.0184 + \$0.0024\\
&\approx \$0.0208 \approx \$20.8 \text{ per 1,000 requests}
\end{aligned}
$$

[ILLUSTRATIVE][DERIVED], a scenario value [ILLUSTRATIVE]
- At the canonical ~26M requests/month: ~$539,000/month.

**Reading the result.** Once the fleet is sized correctly (~20 hosts), the comparison flips entirely versus the single-host framing. Self-hosted (~$5.7/1K reqs) is now **roughly twice the cloud-scaled rate** ($2.8/1K) on a fully-loaded basis ($148K/mo vs ~$72K/mo), because the canonical workload genuinely needs a multi-host fleet, and self-hosting a 20-host fleet carries ~$116K/mo of capex amortization. It is nonetheless still **well below the managed-API rate** ($20.8/1K), so at this volume self-hosting beats the API but loses to scale-to-load cloud. Cloud-scaled (~$2.8/1K) is the cheapest at this volume because only the ~5 hosts the *average* load needs are paid for the *average* load needs, bursting to ~20 at the peak. The decisive caveat remains the **staff/ops term and whether it is sunk**, and now also the **fleet requirement** — a single-host TCO understates the real cost by 4–20×.

**Table 16-1** — TCO comparison across delivery modes (illustrative worked example; N_hosts ≈ 20 at the canonical peak)

| Mode | Capacity | Opex/month | Cost/1K req | $/month @26M req | When it wins |
|---|---|---|---|---|---|
| Self-hosted (20×8×H100) | ~20 hosts | ~$148K | ~$5.7 | ~$148K | staff already in-house (sunk) and sustained near-peak utilization; no burst variability |
| Cloud on-demand (scaled) | bursts to ~20, runs ~5 avg | ~$72K | ~$2.8 | ~$72K | variable load, no idle capex, staff shared |
| Managed API | — | usage | ~$21 | ~$539K | tiny volume, fastest time-to-value |

*(Figures are worked-example estimates as of Q4 2026, not vendor quotes; treat as [ILLUSTRATIVE][DERIVED] illustrative, to be re-priced before budgeting. The fleet requirement ~20 hosts (peak) / ~5 hosts (avg) is from the canonical Ch17 sizing; FP8 KV cuts the peak fleet to ~11.)*

**Parametric sensitivity is the durable form.** All the fixed inputs above — GPU price, electricity, staffing, capacity, API price, and the fleet size itself — are [ILLUSTRATIVE] scenario values; the *structure* of the model is what generalizes. The architect computes N_hosts from the workload first (Ch 17/20), then re-runs this TCO with the customer's real numbers (Chapter 23). A runnable, parameterised version ships with the book as `render/tco_calc.py`.


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

![Fig 16.1 — TCO break-even: self-hosted vs managed API [ILLUSTRATIVE][DERIVED]](figures/fig-16-1601.png)

*Break-even: monthly cost vs monthly volume for self-hosted and managed API across three serve modes, crossing at the ~7.1 M-request scale ($148K/mo ÷ $0.0208 per request).*

<!-- Figure spec: mechanism-first plot; x = requests/month, y = cost per 1K requests; self-host curve high-intercept low-slope; managed-API zero-intercept linear; mark break-even volume; annotate the utilization assumption. -->

## 7. What We Still Don't Know

- **Real equipment/power/staff numbers** for a given deployment are (to be verified) site-specific; the illustrative quotes above must be re-priced.
- **How rapidly GPU list and amortization prices fall** over the 5-year horizon is (a hypothesis); newer cards (H200/B200-class) change the per-card economics.
- **The true staff overhead of self-hosting** (SRE time, security, upgrades) is (a hypothesis) until the team bills its own time honestly.

## 8. End-of-Chapter Mini-Case: TCO Discipline and the Staff Term

A startup's CTO shows the architect a warrant to buy two 8×H100 servers for the new internal RAG assistant, citing "we'll save on token fees." Applying TCO discipline, the architect does not dispute the raw token math. Instead they price it: at this startup's *actual* early volume — ~5 rps average, ~5M requests/month, and only 0.5 engineers fully available for GPU ops — the break-even against a managed API sits just below that volume, and the staff term dwarfs the token savings. The honest number: self-hosting two servers ~$40K/month all-in vs ~$105K/month API at current volume, but the two-server option consumes a full engineer to keep utilization and reliability up — an opportunity cost the startup cannot yet afford. The architect's verdict: **start on the managed API now, revisit self-host at ~2× this volume or when a second engineer frees up**, and re-run the same model then. The CTO did not buy the servers — the break-even graph, with staff honestly included, made the answer self-evident.
