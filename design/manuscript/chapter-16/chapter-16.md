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

TCO is meaningless until we know **how many hosts the workload actually requires**. A common sizing mistake is to start from a single host: a single 8×H100 host can only sustain ~2.0 req/s under the KV/latency analytical planning bound (Chapter 17/20), so it cannot serve even the canonical 10 rps average, let alone the 40 rps peak. We therefore size the fleet first (Ch 17) and price it second.

**Step 1 — fleet size.** The canonical workload requires N_hosts = max(N_throughput, N_KV, N_SLO). With the ~8.6 s service time and C≈17.5 KV-resident requests/host (Ch 17; byte-accurate 17.51, conservative integer floor 17):

| Sizing bound | Average (10 rps) | Peak (40 rps) |
|---|---|---|
| Throughput (per-host ~2.0 req/s) | ⌈10/2.0⌉ = 5 hosts | ⌈40/2.0⌉ = 20 hosts |
| KV (in-flight λ·W / C) | ⌈10×8.6/17.5⌉ = 5 hosts | ⌈40×8.6/17.5⌉ = 20 hosts |
| **N_hosts (max)** | **~5 hosts** | **~20 hosts** |

So the canonical workload's *peak* requires roughly **20 hosts** (FP16 KV, full utilization; **29 working hosts** at the 70% utilization target — **30 total with N−1**), and even the *average* needs ~5 — a fleet, not one box. (FP8 KV roughly halves this to ~10 hosts at peak — C ≈ 35.0, so ⌈344/35.0⌉ = 10, matching Ch 17.) **Every TCO figure below is scaled to this fleet requirement; pricing a single host would understate the cost by roughly 4–20×.**

**What kind of number is ~2.0 req/s?** The per-host rate `C_KV / W ≈ 17.5 / 8.6 ≈ 2.0 req/s` is an *upper-order planning estimate under a particular concurrency, timing, and cache geometry* — not an observed service rate. It is an average-in-system relation, not a measured goodput. The three quantities behind `N_hosts = max(N_throughput, N_KV, N_SLO)` are **three different models that must be derived and measured separately**, and the formula is only as strong as the weakest one:

- **N_KV (KV-memory occupancy ceiling)** — how many requests *reside* in KV cache given the host's usable HBM and the per-token KV footprint. This is an arithmetic allocation bound (the ~17.5 figure).
- **N_throughput (phase capacity)** — how many requests the host can *complete* per second given the service time. The ~8.6 s service time is an uncontended request-level estimate, and `C/W` treats it as fixed.
- **N_SLO (queueing / goodput)** — the number of hosts needed to hold p95/p99 TTFT, TPOT, and success rate under *concurrent* arrival. **Little's law relates average in-system work to elapsed time under stability; it does not independently prove a throughput ceiling or a p99 latency.** At concurrency ~17, TTFT and TPOT can differ substantially from the isolated ~8.6 s used to obtain `C/W`, because batch efficiency, per-request duration, and interference are all coupled to load.

So the 20-host figure is a **scenario-specific bound contingent on the 8.6-second service time remaining valid under concurrent execution**, not a deployment-validated estimate. Before budgeting against it, measure `λ_goodput` per host at the target p95/p99 TTFT, TPOT, and success rate on the actual workload, and re-derive N_hosts. (See the falsification protocol in Ch 17.)

**Treat both provisioning policies explicitly.** The headline $ figures below use the full-utilization fleet (≈20 hosts, provisioned exactly at the 40 rps peak with no headroom). The capacity-planning rule (Ch 17 Table 17-1) uses a 70% max-operating-utilization target, which gives **29 *working* hosts** at the peak ⌈40×8.6/(17.5×0.7)⌉ = ⌈344/12.25⌉ = 29; because one host must be able to drain (failover/maintenance) while the fleet still clears the peak, the N−1 policy requires **30 hosts total** (29 working + 1 spare — 29 surviving × 2.0 × 0.70 ≈ 40.6 ≥ 40 rps). That spare is a *reserve* host, not serving capacity. Both outcomes belong in the decision:

| Provisioning policy | Full-utilization (≈20 hosts) | 70% target + N−1 (≈30 hosts; 29 working + 1 spare) |
|---|---|---|
| Peak fleet | ~20 hosts | ~30 hosts (29 working + 1 spare) |
| Self-host (capex+opex+staff) | ~$148K/mo | ~$217K/mo |
| Per 1,000 requests | ~$5.7 | ~$8.4 |

 

*Provisioning sensitivity (explicit):* the TCO figures below **assume the full-utilization fleet (≈20 hosts, provisioned exactly at the 40 rps peak without headroom)** so that the cost comparison is not double-counting idle capacity. If instead the fleet is provisioned at the 70% utilization target that the sizing rule (Ch17 Table 17-1) actually uses — **30 hosts (29 working + 1 N−1 spare)** — capex scales to ≈30/20 = 1.5×: ≈$174K capex (30 × ~$5.8K/host/mo) + ≈$33K opex + ≈$10K staff ≈ **~$217K/month**, and per-request cost rises to ≈ $217K / 26M ≈ **~$8.4 per 1,000 requests** (vs the $5.7/1K below). The durable conclusion — self-host loses to scale-to-load cloud on this workload — holds under either provisioning policy; the *specific* $5.7/1K number is the full-utilization figure and should be read with that assumption.

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

Under a simplified assumption of a continuously-arriving ~5-host average load that bursts briefly to ~20 at the peak, with a steady warm pool and fast scale-up, that is ≈ 5 × $20/hr × 730 hr ≈ ~$73K/month (scaling the fleet with load; always-on-at-peak would be ~$292K/month). **[ILLUSTRATIVE][DERIVED]** — this is *explicitly* an assumed load-duration curve and fast elastically-scalable capacity, not a measured or guaranteed cost. If the burst is long-lived or scale-up is slow, the real cloud cost rises toward the always-on-at-peak figure and the "cloud is cheapest" result weakens accordingly.

**The cloud case is a family, not a single line.** $73K and $292K are the two endpoints (ideal fast-scale vs always-on-at-peak). The realistic midpoint is set by two *parameters* — the **hours-at-peak** per day/week and the **reserved-warm-instance** count held to avoid cold-start. For example, a mid-case with ~5 reserved warm hosts + ~15 burst hosts held for ~4 peak hours/day, at $20/hr (burst) and the warm pool at a reserved rate, lands between the two endpoints; the exact number depends on the provider's reserved/discount and billing-granularity terms, which are scenario inputs, not market facts. The durable lesson — *fleet size first, price second* — does not depend on this elasticity assumption, but the specific $2.8/1K number does and should be read as the *fast-scale ideal*, not the default decision line.

- Per request: ~26M/month. **Cost ≈ $73K / 26M ≈ $0.0028/request ≈ $2.8 per 1,000 requests.** [ILLUSTRATIVE][DERIVED] *(The "duty cycle" here is **fleet capacity utilization** — how many of the provisioned hosts are busy on average — NOT the literal fraction of wall-clock time an instance is powered on. A continuously-arriving 10-rps workload cannot be served by shutting the only instance off 60% of the time; it needs a fleet that is always available and scales with load. Staff & integration add on top.)*

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
- At the canonical ~26M requests/month: ~$541,000/month (26M × $0.0208 ≈ $541K).

**Reading the result.** Once the fleet is sized correctly (~20 hosts), the comparison flips entirely versus the single-host framing. Self-hosted (~$5.7/1K reqs) is now **roughly twice the cloud-scaled rate** ($2.8/1K) on a fully-loaded basis ($148K/mo vs ~$73K/mo), because the canonical workload genuinely needs a multi-host fleet, and self-hosting a 20-host fleet carries ~$116K/mo of capex amortization. It is nonetheless still **well below the managed-API rate** ($20.8/1K), so at this volume self-hosting beats the API but loses to scale-to-load cloud. **This is an illustrative lower-bound for cloud, NOT an apples-to-apples comparison** — the $73K cloud figure assumes ideal scale-to-load elasticity and a continuously-arriving ~5-host average that bursts briefly to ~20, whereas the $148K self-host figure is an always-provisioned 20-host fleet. They do **not** share the same availability ceiling, failover reserve, warm-capacity cost, peak-duration assumption, or p95 SLO. **Cloud-scaled being cheapest is therefore a lower-bound result of an asymmetric scenario, not a demonstrated mode ranking.** Without a measured traffic trace and equalized SLO/failover/availability assumptions on both sides, the definitive economic winner is **not determined**.

**Apples-to-apples caveat.** The $73K cloud figure does not yet include an N−1 failover reserve, capacity held for failures/maintenance, warm-capacity cost during idle periods, model-startup time, or provider availability variance; the self-host figure does not charge for the same availability target's redundancy. So the two are **not compared on equal reliability or load-serving assumptions**. Before treating cloud as cheaper, add: the same served-load trace, p95 SLO, peak duration, availability target, failover coverage, warm capacity, model startup time, and price period to *both* sides. Under a nonideal elastic case (a reserved warm pool sized for N−1 plus slower scale-up), the cloud cost rises toward the always-on-at-peak figure and the "cloud is cheapest" result may not hold. The durable lesson — *fleet size first, price second* — does not depend on this elasticity assumption, but the specific $2.8/1K number should be read as an **optimistic lower bound**, and the decision framed as "cloud is cheaper **if** scale-up is fast and a warm pool can be held cheaply," not as an unconditional ranking. The decisive caveat remains the **staff/ops term and whether it is sunk**, and now also the **fleet requirement** — a single-host TCO understates the real cost by 4–20×.

**Multi-region active-active availability is NOT priced in this TCO.** The canonical workload's stated SLA (Ch 4) is multi-region active-active at 99.9% availability, but **every** `$/1K` figure in this chapter (and the host counts in Ch 17) prices a **single-region** deployment with **N−1 single-host failover**, **not** multi-region active-active. Multi-region active-active is a **different provisioning problem** from N−1 single-host failover: it requires cross-region capacity duplication (no single region's loss may take the service down), region-failure tolerance, data locality and traffic routing (geo/health-based routing, per-region caches and indices), and consistent state/data replication (model weights + KV/index replication across regions). None of that is priced or validated here, and none of it is implied by the N−1 reserve host above. Accordingly the canonical cost figures **understate the cost of the canonical workload's own stated 99.9% availability requirement** — read the `$/1K` and monthly totals as *single-region, N−1-only* numbers, and add a separate multi-region capacity + replication cost line (on the order of ≥2× the single-region fleet on the capacity-duplication term alone) before the availability SLA can be considered met.

**Table 16-1** — TCO comparison across delivery modes (illustrative worked example; N_hosts ≈ 20 at the canonical peak). **ILLUSTRATIVE LOWER-BOUND, NOT APPLES-TO-APPLES:** the modes are NOT compared on equal availability, failover, warm-capacity, peak-duration, or p95-SLO assumptions — the cloud-scaled $73K assumes ideal elasticity while the self-host $148K is an always-provisioned fleet. Use as a *scenario* comparison, not a ranking; the definitive winner is **not determined** without a measured traffic trace and equalized assumptions on both sides.

| Mode | Capacity | Opex/month | Cost/1K req | $/month @26M req | When it wins |
|---|---|---|---|---|---|
| Self-hosted (20×8×H100) | ~20 hosts | ~$148K | ~$5.7 | ~$148K | staff already in-house (sunk) and sustained near-peak utilization; no burst variability |
| Cloud on-demand (scaled) | bursts to ~20, runs ~5 avg | ~$73K | ~$2.8 | ~$73K | variable load, no idle capex, staff shared — **only if scale-up is fast and the average run is ~5 hosts** |
| Cloud on-demand (always-on-at-peak) | ~20 hosts all month | ~$292K | ~$11.2 | ~$292K | scale-up is slow or the load is sustained near peak; the elastic-ideal $73K does not apply |
| Managed API | — | usage | ~$21 | ~$541K | tiny volume, fastest time-to-value |

(Figures are worked-example estimates — a **Q4 2026 illustrative pricing scenario, not market quotes** — and treat as [ILLUSTRATIVE][DERIVED], to be re-priced before budgeting. These are *scenario inputs the architect chooses and re-prices*, not assertions governed by the 2026-08-30 evidence cutoff; they do not claim to be a source available at that date. The fleet requirement ~20 hosts (peak) / ~5 hosts (avg) is from the canonical Ch17 sizing; FP8 KV cuts the peak fleet to ~10. **GQA operating configuration:** the ~20-host figure assumes the canonical full-MHA KV constant (2.62 MB/token). A 2026 production model with grouped-query attention (GQA) uses roughly 8× less KV per token, which raises the per-host KV-residency ceiling C by ~8× and cuts the KV-bound fleet to on the order of ~3 hosts at the same 40 rps. **That ~3-host figure assumes per-host throughput also scales ~8× with C (a KV/memory-bound host); the throughput bound (⌈40/2.0⌉ ≈ 20 hosts) is independent of KV size and still applies if the host is compute/bandwidth-bound — so the true fleet is max(N_throughput, N_KV), the larger of the two, not the KV bound alone.** The full-MHA number is the conservative teaching case; own the 6–7× gap explicitly rather than quoting ~20 hosts for a GQA deployment.)

**Table 16-2 — Matched SLO/availability comparison (decision view).** The three modes below are compared on the canonical workload's stated **multi-region active-active 99.9% SLA** (Ch 4). They are **[ILLUSTRATIVE][ASSUMPTION] planning rows, NOT measured.** The **not-apples-to-apples caveat** of Table 16-1 still governs (the modes are not compared on equal availability, failover, warm-capacity, peak-duration, or p95-SLO assumptions). This table only makes the availability mismatch explicit. It does not change the Table 16-1 result. The single-region rows are the **single-region teaching baseline** computed above.

| Deployment / availability mode | Scope | Cost (from above) | Availability covered | Status |
|---|---|---|---|---|
| Self-host, single-region, N−1 | ~20 hosts peak / ~30 hosts (70% + N−1) | ~$148K/mo ($5.7/1K); ~$217K/mo at 70%+N−1 ($8.4/1K) | Single-region; survives one host loss | **[ILLUSTRATIVE][ASSUMPTION]** single-region teaching baseline, already computed |
| Cloud elastic, single-region | bursts to ~20, runs ~5 avg | ~$73K/mo (ideal fast-scale) to ~$292K/mo (always-on at peak); ~$2.8/1K | Single-region | **[ILLUSTRATIVE][ASSUMPTION]** single-region teaching baseline, already computed |
| Multi-region active-active | **UNSIZED**: mandatory capacity duplication, region-failure tolerance, data replication, traffic routing, error budget | **NOT PRICED / NOT VALIDATED in this chapter** | 99.9% active-active | **Decision deferred** pending regional capacity and failure test |

**The multi-region row is NOT priced and NOT validated in this chapter.** Multi-region active-active provisioning differs from N−1 single-host failover (Ch 16 §3, Ch 17 §6). It requires cross-region capacity duplication, region-failure tolerance, geo/health-based traffic routing, and consistent state/data replication. None of it is priced or validated here. Treat the multi-region row as a **provisional scenario** for planning visibility only. It is **not a procurement recommendation** and **not a validated cost**. The single-region $/1K and monthly figures in this chapter therefore read as the *single-region teaching baseline*; the true cost of the canonical workload's own stated 99.9% active-active SLA is materially higher and is **deferred** until regional capacity and a region-failure test are defined.

**Parametric sensitivity is the durable form.** All the fixed inputs above — GPU price, electricity, staffing, capacity, API price, and the fleet size itself — are [ILLUSTRATIVE] scenario values; the *structure* of the model is what generalizes. The architect computes N_hosts from the workload first (Ch 17/20), then re-runs this TCO with the customer's real numbers (Chapter 23). A runnable, parameterised version ships with the book as `render/tco_calc.py`.

Crucially, these are **independent sensitivity dimensions**, and each pushes the break-even in a different direction; do not collapse them into one "the assumptions vary" disclaimer:

- **Fleet size** (N_hosts) — driven by the KV/throughput/SLO ceiling (Ch 17-20), not by TCO. A larger fleet raises the flat self-host line (more capex+opex) and shifts break-even right.
- **Duty cycle** — a burst-sized fleet does *not* run every host at full paid duty all month. Self-hosted reserved cards bill flat regardless of utilization; cloud on-demand bills only what runs. Separating these two is what makes the self-host (high fixed, low variable) vs cloud (low fixed, high variable) comparison meaningful.
- **Utilization** — the *provisioning* utilization target (70% vs 100%, Ch 17) sets how many hosts are needed, not how much they cost per unit; it is a separate line from the price-per-host.
- **Reserved / on-demand mix** — whether capacity is committed (cheaper, flat) or burst (pricier, on-demand) is a distinct lever; a mixed fleet has both a flat and a variable term.
- **Failover reserve** — N-1/headroom hosts (Ch 17) add cost but are not production-serving capacity; they must be counted as a separate reserve line, not folded into the served-load hosts.
- **Staffing** — the dominant human term for self-hosting; it is frequently the decider at low volume (Ch16 §16.8 mini-case) and should be its own sensitivity dimension, not absorbed into opex.

Because these dimensions are independent, the break-even is a **region**, not a point: the figure marks the [ILLUSTRATIVE] price band, and the honest output is a range (here ~5.9–9.9M req/mo) rather than a single "the break-even is 7.1M" claim. The headline range varies the **API price** against the full-utilization self-host cost ($148K/mo): the low end (~5.9M) is 148,000 ÷ 0.025 (the $25/1K top of the band) and the high end (~9.9M) is 148,000 ÷ 0.015 (the $15/1K bottom of the band) — the same ~5.9–9.9M range reported with Fig 16.1 and in §16.6. The **70%-utilization provisioning case** is a separate dimension and is named separately: the $217K/mo self-host cost against the canonical $20.8/1K API rate gives 217,000 ÷ 0.0208 ≈ 10.4M req/mo. Report the range and name which dimension is being varied.


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

TCO is the final gate in the design loop (Ch12 candidates → Ch14 benchmark → Ch16 cost). It settles which candidate survives: the 70B 8×H100 self-host **passes the capability screen and is analytically screened for feasibility — it *would* need a representative hardware benchmark to establish SLO-goodput** (the `C/W` and roofline estimates of Chs. 7–8 are planning bounds, not a measured p95 TTFT/TPOT pass at the target offered load), and on TCO it **beats the managed API at canonical volume but loses to scale-to-load cloud** — so the surviving recommendation is *conditional* (self-host wins only if the staff/ops term is sunk and sustained near-peak utilization holds and a benchmark confirms the SLO; otherwise scale-to-load cloud at ~$2.8/1K is cheapest). This completes the chain from vague requirement to a defensible, costed architecture, while being honest that the TCO gate is not an unconditional win and that the SLO pass is *provisional until benchmarked*. It also feeds fleet decisions (Ch17-18): the break-even curve is what justifies buying a second host versus renting peaks, and the staff term is what pushes toward consolidation (Ch18).

![Fig 16.1 — TCO break-even: self-hosted vs managed API (canonical 80-layer full-MHA geometry). The break-even volume is **illustrative, not portable** — it holds only for this 70B FP16 8×H100 config, 5-year amortization, \$20.80/1K API price, and 9.2K-in/300-out mix. **Not apples-to-apples across demand levels:** self-hosted = (capex ÷ 60 mo) + energy + staff/ops; managed-API = input×\$/1M + output×\$/1M-out; utilization = served ÷ provisioned — the self-host line assumes 40 rps peak provisioning, so break-even is a function of demand, not a fixed point. [ILLUSTRATIVE][DERIVED]](figures/fig-16-1601.png)

*Break-even: monthly cost vs monthly volume for self-hosted and managed API across three serve modes. The self-host line crosses the managed line over a **range** of ~5.9–9.9 M requests/mo (the \$15–25/1K price band), with the ~7.1 M mid-point at the canonical \$20.80/1K (\$148K/mo ÷ \$0.0208 per request). The figure marks the mid-point (star) and the full sensitivity span (horizontal line).*

<!-- Figure spec: mechanism-first plot; x = requests/month, y = cost per 1K requests; self-host curve high-intercept low-slope; managed-API zero-intercept linear; mark break-even volume; annotate the utilization assumption. -->

## 7. What We Still Don't Know

- **Real equipment/power/staff numbers** for a given deployment are (to be verified) site-specific; the illustrative quotes above must be re-priced.
- **How rapidly GPU list and amortization prices fall** over the 5-year horizon is (a hypothesis); newer cards (H200/B200-class) change the per-card economics.
- **The true staff overhead of self-hosting** (SRE time, security, upgrades) is (a hypothesis) until the team bills its own time honestly.

## 8. End-of-Chapter Mini-Case: TCO Discipline and the Staff Term

A startup's CTO shows the architect a warrant to buy two 8×H100 servers for the new internal RAG assistant, citing "we'll save on token fees." Applying TCO discipline, the architect does not dispute the raw token math. Instead they price it: at this startup's *actual* early volume — ~2 rps average, ~5M requests/month, and only 0.5 engineers fully available for GPU ops — the break-even against a managed API is this chapter's own division: $40,000 ÷ $0.0208 ≈ **1.9M requests/month**, so the current volume is already ~2.6× past the break-even. The honest number: self-hosting two servers ~$40K/month all-in vs ~$104K/month API at current volume (5M × $0.0208) — a **~$64K/month saving in favor of self-hosting, with the staff term already inside the $40K** (capex ~$11.6K + power ~$2.2K for two hosts leaves ≤ ~$26K for staff and upkeep — too small to dwarf a $64K saving). The token arithmetic therefore does not send this startup to the API; it points to self-hosting. Only one term can flip the decision: the *opportunity* cost of the GPU-ops time the two servers consume — the better part of the only engineer the startup can spare. To justify paying the API premium, that term must exceed **~$64K/month**, about $770K/year of product work the startup is not doing. The architect's verdict: **start on the managed API now, and revisit self-host the moment the consumed engineer's opportunity cost falls below ~$64K/month — for example when a second engineer frees up** — then re-run the same model. Request volume is not the lever: more volume only widens the ~$64K gap. The CTO did not buy the servers. The break-even graph did not make the answer self-evident; it narrowed the whole decision to one labeled assumption — this startup values its half-engineer's product time above $64K/month. A team that cannot say that, or that has a second engineer to spare, runs the same numbers and buys the servers.
