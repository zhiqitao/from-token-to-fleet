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

**Step 1 — fleet size.** The canonical workload's KV-residency / service-time screen is N_hosts = ⌈λ·W/C⌉ with the hard-slot floor 17 (436 GB ÷ (2.62 MB/token × 9,500 tokens) = 17.51 → floor 17, applied BEFORE any utilization adjustment and BEFORE the host ceil; Ch 17) and W_plan = 8.6 s (the rounded planning service time; the distinct execution estimate 8.58 s is exposed and labeled, never silently substituted):

| Sizing screen | Average (10 rps) | Peak (40 rps) |
|---|---|---|
| KV-residency / service-time screen (⌈λ·W/C⌉, floor C = 17) | ⌈10×8.6/17⌉ = 6 hosts | ⌈40×8.6/17⌉ = 21 hosts |
| Independent prefill screen (⌈tokens/s ÷ 19,770 tok/s/host⌉) | 5 hosts | 19 hosts |
| **N_hosts (KV screen max)** | **6 hosts** | **21 hosts** |

Two things about that table are load-bearing. First, the ~2.0 rps per-host figure (C/W = 17/8.6 = 1.9767) is the KV-residency bound divided by the service time — a **service-time surrogate inside the KV screen**, not a second, independent throughput ceiling; an earlier draft of this table listed a separate "throughput ⌈40/2.0⌉ row" beside the KV row, and the two are algebraically the same bound, so that duplicate row is gone. Second, the prefill row is a genuinely *independent* compute screen — the scope ledger's 5 avg / 19 peak, ⌈368,000 ÷ 19,770⌉ = 19 at peak — and it is deliberately NOT forced to equal the KV row. The third scope, N_SLO (queueing / goodput under concurrency), has **no number here because it is unmeasured**: it is a named scope, not a row.

So the canonical workload's peak KV screen is **21 hosts** (⌈344/17⌉, zero spare — the headline policy provisions exactly at the 40 rps peak with no headroom), and the average needs **6** — a fleet, not one box. Ch 17's whole-slot convention floors C to 17 first and gives 21; equivalently the floored whole-slot rule gives 21 — this TCO prices that 21-host scenario, and a one-host difference changes no mode comparison. FP8 changes only the KV arithmetic: the raw FP8 byte factor 0.5 gives a hard floor of 35 slots BEFORE efficiency and the host ceil, so the FP8 KV screen is ⌈344/35.0⌉ = 10 at peak (11 at the 95% scheduling factor) — KV-residency arithmetic on a screen, **not an assertion that real deployments halve in size**; measured allocation, compute and goodput are absent, and the independent prefill and unmeasured SLO scopes do not shrink with it. **Every TCO figure below is scaled to this 21-host KV-screen fleet; pricing a single host would understate the cost by roughly 6–21×.**

**What kind of number is ~2.0 req/s?** The per-host rate `C_KV / W ≈ 17 / 8.6 ≈ 2.0 req/s` is an *upper-order planning estimate under a particular concurrency, timing, and cache geometry* — not an observed service rate. It is an average-in-system relation, not a measured goodput, and it is derived *from* the KV bound, so it does not add an independent constraint. The scopes behind fleet sizing must be derived and measured separately, and the formula is only as strong as the weakest one:

- **N_KV (KV-memory occupancy ceiling)** — how many requests *reside* in KV cache given the host's usable HBM and the per-token KV footprint. This is an arithmetic allocation bound (the floor-17 figure).
- **C/W (service-time surrogate inside the KV screen)** — the ~8.6 s W_plan is an uncontended request-level estimate; C/W inherits both the KV bound and the service-time assumption, so it is not an independent compute bound and not an independently measured throughput.
- **Independent prefill screen** — a separate compute bound (5 avg / 19 peak from ⌈368,000 ÷ 19,770⌉), legitimately independent of KV size.
- **N_SLO (queueing / goodput)** — the number of hosts needed to hold p95/p99 TTFT, TPOT, and success rate under *concurrent* arrival. **This scope is unmeasured here. Little's law relates average in-system work to elapsed time under stability; it does not independently prove a throughput ceiling or a p99 latency.** At concurrency ~17, TTFT and TPOT can differ substantially from the isolated ~8.6 s used to obtain `C/W`, because batch efficiency, per-request duration, and interference are all coupled to load.

So the 21-host figure is a **scenario-specific KV/service-time screen contingent on the 8.6-second service time remaining valid under concurrent execution**, not a deployment-validated estimate. Before budgeting against it, measure `λ_goodput` per host at the target p95/p99 TTFT, TPOT, and success rate on the actual workload, and re-derive N_hosts. (See the falsification protocol in Ch 17.)

**Treat both provisioning policies explicitly.** The headline $ figures below use the 21-host ideal-active fleet (zero spare, provisioned exactly at the 40 rps peak). The capacity-planning rule (Ch 17 Table 17-1) uses a 70% max-operating-utilization target, which gives **29 working hosts** at the peak ⌈40×8.6/(17×0.7)⌉ = ⌈344/11.9⌉ = 29 and **30 total with N−1**; because one host must be able to drain (failover/maintenance) while the fleet still clears the peak, the N−1 policy requires 30 hosts total (29 working + 1 reserve — 29 surviving × 1.9767 × 0.70 ≈ 40.1 ≥ 40 rps). That spare is a *reserve* host, not serving capacity. A third, separate model row is the 95% scheduling factor: **22 hosts, also zero spare — NOT a reserve**, an efficiency derate of the same screen ($162,760.59/mo, $26.08/1K). All three outcomes belong in the decision:

| Provisioning policy | 21-host ideal-active (headline, zero spare) | 70% target + N−1 (30 hosts; 29 working + 1 reserve) |
|---|---|---|
| Peak fleet | 21 hosts (22 at the 95% scheduling factor) | 30 hosts (29 working + 1 reserve) |
| Self-host (capex+energy+staff) | ~$155.8K/mo | ~$218.3K/mo |
| Per 1,000 requests | ~$24.97 | ~$34.99 |

*Provisioning sensitivity (explicit):* the TCO figures below **assume the 21-host ideal-active fleet (provisioned exactly at the 40 rps peak without headroom)** so that the cost comparison is not double-counting idle capacity. If instead the fleet is provisioned at the 70% utilization target that the sizing rule (Ch 17 Table 17-1) actually uses — **30 hosts (29 working + 1 N−1 reserve)** — capex is exactly 30 × $350,000 / 60 months = **$175,000**, plus energy 30 × $1,110.33 = $33,309.90, plus $10,000 staff ≈ **~$218.3K/month** ($218,309.90 computed exactly, rounded only for display), and per-request cost rises to ≈ $218,309.90 / 6.24M ≈ **~$34.99 per 1,000 requests** (vs the $24.97/1K below). Which mode looks favorable depends on the named assumptions and holds under either provisioning policy; the *specific* $24.97/1K number is the 21-host headline figure.

**Step 2 — price each mode on N_hosts = 21 (FP16 KV screen, provisioned for the 40 rps peak).**

**Mode 1 — self-hosted on owned cards (21 × 8×H100).**

- Capex: ~$350K per fully built 8×H100 server, amortized over 5 years → $5,833.33/month/host → **$122,500/month** for 21 hosts. [ILLUSTRATIVE][DERIVED], scenario value [ILLUSTRATIVE]
- Energy + staff: per host, 8 H100 GPUs at ~700 W ≈ 5.6 kW GPU IT + ~2.2 kW host/network ≈ 7.8 kW IT, × PUE 1.3 ≈ 10.14 kW at the wall; at ~$0.15/kWh over the 730 h/month billing/energy calendar (a separate input from the request calendar) that is $1,110.33/month/host → **$23,316.93/month** for 21 hosts. Staff/engineering alloc $10,000/month. [ILLUSTRATIVE][DERIVED], scenario value [ILLUSTRATIVE]
- Monthly total = $122,500 + $23,316.93 + $10,000 = **$155,816.93/month** for 21 hosts (zero spare).
- Per request at ~10 rps average over the active business-hours window (Ch 4: 10 rps × 8 h × 3,600 s × 260 workdays ÷ 12 = **6,240,000 requests/month**, not 24×7; request-active time is 173.33 h/month, distinct from the 730 h billing calendar). **Cost = $155,816.93 / 6.24M ≈ $0.024971/request ≈ $24.97 per 1,000 requests** (24.97066185897436 exact). [ILLUSTRATIVE][DERIVED] *(worked example, not reference)*

**Mode 2 — cloud GPU instances (rent, occupancy-input priced).** An 8×H100 on-demand instance ~$20/hr (canonical $2.50/GPU-hr × 8). Because the workload's *peak* is 40 rps, the fleet must be able to burst to 21 instances, but what the bill actually depends on is **paid host-hours** — an INPUT this chapter does not derive:

$$
H_\text{cloud,month} = \text{paid host-hours (an occupancy INPUT, supplied or assumed)}
$$

The honest cloud bill would be the integral of required capacity over time, plus the warm-pool and capacity-reservation terms:

$$
H_\text{cloud,month} = \int_0^T N_\text{required}(t)\,dt \; \; \text{plus a warm/startup pool and any capacity-reservation guarantee}
$$

where $N_\text{required}(t)$ is the number of hosts that must be running at time $t$ (a step function that rises with the load curve at that hour of the day/week). This depends on the actual temporal load profile — the **burst duration and frequency**, the **scale-up latency** (how many seconds/minutes to attach and load a fresh instance), the **model-loading/warmup time** (loading a 140 GB model into a new host is not instant), the **minimum warm pool** to serve the base load without cold-starting, **provider capacity/availability**, and **billing granularity**. Only if the provider can attach instances faster than the load curve demands, with a warm pool already holding the model, can the cloud bill approach a pure average-load figure.

**Default paid-occupancy ASSUMPTION.** The canonical default bills **6 × 730 = 4,380 host-hours → $87,600/month → $14.04 per 1,000 requests** (14.038461538461538 exact). This is an explicit illustrative occupancy INPUT: it is **not a measured duty cycle, not a load-duration integral, not a guaranteed lower bound, not a complete warm-plus-burst forecast, and not a proven feasible serving schedule** — and it must never be inferred from the 6/21 host-count ratio (a ratio of selected host counts, not an occupancy). The always-on-at-peak alternative bills 21 × 730 = 15,330 host-hours → **$306,600/month → $49.13 per 1,000** (49.13461538461539 exact). **[ILLUSTRATIVE][DERIVED]**

**The cloud case is a family, not a single line.** $87.6K and $306.6K are the two named endpoints (default occupancy input vs always-on at the 21-host peak). Anything between them requires the customer's own trace or occupancy input (`render/tco_calc.py --paid-host-hours`). For example, a mid-case with ~6 reserved warm hosts + ~15 burst hosts held for ~4 peak hours/day, at $20/hr (burst) and the warm pool at a reserved rate, lands between the two endpoints; the exact number depends on the provider's reserved/discount and billing-granularity terms, which are scenario inputs, not market facts. The durable lesson — *fleet size first, price second* — does not depend on this occupancy assumption, but the specific $14.04/1K number does and should be read as the *default occupancy INPUT*, not a decision line.

- Per request: 6.24M/month (active business-hours window, Ch 4). **Cost = $87,600 / 6.24M ≈ $0.014038/request ≈ $14.04 per 1,000 requests.** [ILLUSTRATIVE][DERIVED] *(The "duty cycle" here is **fleet capacity utilization** — how many of the provisioned hosts are busy on average — NOT the literal fraction of wall-clock time an instance is powered on. A continuously-arriving 10-rps workload cannot be served by shutting the only instance off 60% of the time; it needs a fleet that is always available and scales with load. Staff & integration add on top.)*

**Mode 3 — managed inference API.**

- A hosted frontier-70B-class API at ~$0.002/input + ~$0.008/output per 1K tokens (typical as of 2026). The per-request token cost is

$$
\begin{aligned}
\text{cost/req} &= p_\text{in} \cdot \frac{I}{1000} + p_\text{out} \cdot \frac{O}{1000}\\
&= 0.002 \times 9.2 + 0.008 \times 0.3 \approx \$0.0184 + \$0.0024\\
&\approx \$0.0208 \approx \$20.8 \text{ per 1,000 requests}
\end{aligned}
$$

[ILLUSTRATIVE][DERIVED], a scenario value [ILLUSTRATIVE] — at the canonical 6,240,000 requests/month (active business-hours window, Ch 4): **$129,792/month** (~$129.8K; 6.24M × $0.0208).

**Reading the result.** Once the fleet is sized correctly (21 hosts), the comparison changes entirely versus the single-host framing. On the included-cost lines above: self-hosted is **$24.97/1K** ($155,816.93/mo), the cloud default-occupancy input is **$14.04/1K** ($87,600/mo), and the managed API is **$20.8/1K** ($129,792/mo). The self-host-to-default-cloud ratio is **~1.8** (155,816.93 ÷ 87,600 = 1.78) — a ~1.8 ratio, not a 2× gap — and self-host sits **above** the API at the canonical 6.24M volume, with the API break-even at ~7.5M. **None of these three numbers is an unconditional ranking.** The $87.6K cloud line is a paid-occupancy INPUT assumption (not a measured duty cycle or a proven feasible serving schedule), the $155.8K self-host line is an always-provisioned 21-host fleet carrying a fixed staff alloc, and the scopes are not equalized — the not-apples-to-apples caveat under Table 16-1 names the specific mismatches. **Any "cheaper" reading is conditional on those named inputs, not demonstrated.**

**Apples-to-apples caveat.** The $87.6K cloud figure is an occupancy input; it does not include an N−1 failover reserve, capacity held for failures/maintenance, warm-capacity cost during idle periods, model-startup time, or provider availability variance, and the self-host figure does not charge for the same availability target's redundancy. So the two are **not compared on equal reliability or load-serving assumptions**. Before treating any mode as cheaper, add: the same served-load trace, p95 SLO, peak duration, availability target, failover coverage, warm capacity, model startup time, occupancy evidence, and price period to *both* sides. Under a nonideal elastic case (a reserved warm pool sized for N−1 plus slower scale-up), the cloud cost rises toward the always-on-at-peak figure and any "cloud is cheapest" result may not hold. As above: the $14.04/1K figure is an **assumption-bounded input** — frame the decision as "cloud is cheaper **if** the occupancy input holds and a warm pool can be held cheaply," not as an unconditional ranking. The decisive caveat remains the **staff/ops term and whether it is sunk**, and now also the **fleet requirement** — a single-host TCO understates the real cost by roughly 6–21×.

**Included-cost scope and exclusions (from the canonical YAML, riding every CLI output).** No separate rack / external network / site price line exists in source; none is invented here. Fully-built-host capex covers only its stated scope; unpriced external items are exclusions/unknowns. Staffing, startup, reservation and availability costs are NOT equalized across delivery modes. This model totals included illustrative lines only; it is not procurement-complete.

**Multi-region active-active availability is NOT priced in this TCO.** The canonical workload's stated SLA (Ch 4) is multi-region active-active at 99.9% availability, but **every** `$/1K` figure in this chapter (and the host counts in Ch 17) prices a **single-region** deployment — the 21-host headline rows are the **ideal zero-spare** fleet with **no N−1 reserve priced**, and only the 30-host policy row carries the **29 working + 1 reserve** N−1 single-host failover — **not** multi-region active-active. Multi-region active-active is a **different provisioning problem** from N−1 single-host failover: it requires cross-region capacity duplication (no single region's loss may take the service down), region-failure tolerance, data locality and traffic routing (geo/health-based routing, per-region caches and indices), and consistent state/data replication (model weights + KV/index replication across regions). None of that is priced or validated here, and none of it is implied by the N−1 reserve host above (the 30-host policy row). Accordingly the canonical cost figures **understate the cost of the canonical workload's own stated 99.9% availability requirement** — read the `$/1K` and monthly totals as *single-region* numbers — zero-spare at the 21-host headline, N−1-reserve only at the 30-host policy — and add a separate multi-region capacity + replication cost line (on the order of ≥2× the single-region fleet on the capacity-duplication term alone) before the availability SLA can be considered met.

**Table 16-1** — TCO comparison across delivery modes (illustrative worked example; N_hosts = 21 at the canonical peak KV screen). **ILLUSTRATIVE SCENARIO, NOT APPLES-TO-APPLES:** the modes are NOT compared on equal availability, failover, warm-capacity, peak-duration, occupancy-evidence, or p95-SLO assumptions — the cloud $87.6K rests on a paid-occupancy INPUT while the self-host $155.8K is an always-provisioned fleet. Use as a *scenario* comparison, not an unconditional ranking; the definitive winner is **not determined** without a measured traffic trace and equalized assumptions on both sides.

| Mode | Provisioned | Monthly cost | $/1K req @6.24M | Qualification |
|---|---|---|---|---|
| **A.** Self-hosted (21×8×H100) | 21 hosts, zero spare | ~$155.8K ($155,816.93) | ~$24.97 | always-provisioned fleet; $10K/mo staff alloc inside; no N−1 reserve priced |
| **B.** Cloud, default paid-occupancy input | 4,380 paid host-hours (6 × 730 INPUT) | ~$87.6K | ~$14.04 | occupancy INPUT, not a measured duty cycle |
| **B.** Cloud, always-on at 21-host peak | 21 hosts all month (15,330 h) | ~$306.6K | ~$49.13 | scale-up slow or sustained near peak; default input does not apply |
| **C.** Managed API | — (usage-based) | ~$129.8K | ~$20.8 | no capacity held; fastest time-to-value |

**When each wins — A/B/C (the explanation lives here, not in a narrow table column).** **A** — self-host wins when staff is already in-house (sunk), utilization is sustained near peak, there is no burst variability, and volume sits above the ~7.5M API break-even. **B** (default paid-occupancy input) — cloud wins on variable load with no idle capex and shared staff, *only if* the occupancy input holds (fast scale-up, cheap warm pool); it is **not** a measured duty cycle. **B** (always-on at the 21-host peak) — the same cloud mode when scale-up is slow or the load is sustained near peak; the default occupancy input then does not apply. **C** — the managed API wins at tiny volume and for fastest time-to-value. **None of A/B/C is an unconditional ranking**; each is conditional on the qualifications in the last column.

(Worked-example estimates — a **Q4 2026 illustrative pricing scenario, not market quotes**, [ILLUSTRATIVE][DERIVED], to be re-priced before budgeting; *scenario inputs the architect chooses and re-prices*, not assertions governed by the 2026-08-30 evidence cutoff. Fleet requirement: 21 hosts (peak KV screen) / 6 (avg) from Ch 17 sizing (hard-slot floor 17); the Independent prefill screen gives 19 (peak) / 5 (avg), not forced to agree; measured SLO-goodput is unmeasured. FP8's raw byte factor 0.5 gives a hard floor of 35 slots before efficiency and the host ceil, so the FP8 KV screen is 10 at peak / 11 at 95% — KV-residency arithmetic, **not a claim that real deployments halve in size**. **GQA operating configuration:** the 21-host figure assumes the canonical full-MHA KV constant (2.62 MB/token). A 2026 production model with grouped-query attention (GQA) uses roughly 8× less KV per token, raising the per-host KV-residency ceiling C by ~8× and cutting the *KV screen* to ~3 hosts at the same 40 rps — but the **Independent prefill screen stays 19 at peak** (it does not shrink with KV size) and the SLO scope is still unmeasured, so the fleet is the max of the *named* screens, not the KV bound alone. The full-MHA number is the conservative teaching case; own the gap explicitly rather than quoting 21 hosts for a GQA deployment.)

\needspace{18\baselineskip}

**Table 16-2 — Matched SLO/availability comparison (decision view).** The three modes below are compared on the canonical workload's stated **multi-region active-active 99.9% SLA** (Ch 4). They are **[ILLUSTRATIVE][ASSUMPTION] planning rows, NOT measured.** The **not-apples-to-apples caveat** of Table 16-1 still governs. This table does not change the Table 16-1 result. Every $/1K below divides the monthly cost by the canonical 6,240,000 requests/month (10 rps over the 8 h × 260-workday business window, Ch 4 — not 24×7), the same basis as Table 16-1.

| Deployment / availability mode | Provisioned | Monthly cost | $/1K req @6.24M | Qualification |
|---|---|---|---|---|
| Self-host, single-region (mode A) | 21 hosts peak (zero spare) / 30 hosts (70% + N−1) | ~$155.8K/mo; ~$218.3K/mo at 70%+N−1 | ~$24.97; ~$34.99 | Single-region; one-host loss covered only by the 30-host (29 + 1) reserve — **[ILLUSTRATIVE][ASSUMPTION]** single-region teaching baseline, already computed |
| Cloud elastic, single-region (mode B) | 4,380 paid host-hours (default input) to 15,330 (always-on at peak) | ~$87.6K/mo to ~$306.6K/mo | ~$14.04–$49.13 | Single-region — **[ILLUSTRATIVE][ASSUMPTION]** single-region teaching baseline, already computed |
| Multi-region active-active | **UNSIZED**: mandatory capacity duplication, region-failure tolerance, data replication, traffic routing, error budget | **NOT PRICED / NOT VALIDATED in this chapter** | **NOT COMPARABLE** | **NOT COMPARABLE** — 99.9% active-active; **Decision deferred** pending regional capacity and failure test |

**Status note (moved out of the narrow Status column; the A/B/C letters of Table 16-1 apply).** The two single-region rows are **[ILLUSTRATIVE][ASSUMPTION] single-region teaching baselines, already computed** — planning rows, not measured. The multi-region row is **NOT COMPARABLE**: it is **UNSIZED** and **NOT PRICED**, so it carries no `$/1K` and cannot be ranked against A/B/C.

**The multi-region row is NOT priced — see the §16.3 multi-region statement (Ch 17 §17.6 applies it to the host counts); this table only makes the availability mismatch explicit.** Treat the row as a **provisional scenario** for planning visibility only: **not a procurement recommendation**, and **deferred** until regional capacity and a region-failure test are defined.

**Parametric sensitivity is the durable form.** All the fixed inputs above — GPU price, electricity, staffing, capacity, API price, occupancy, and the fleet size itself — are [ILLUSTRATIVE] scenario values; the *structure* of the model is what generalizes. The architect computes N_hosts from the workload first (Ch 17/20), then re-runs this TCO with the customer's real numbers (Chapter 23). A runnable, parameterised version ships with the book as `render/tco_calc.py` (its pure model is `render/tco_model.py`, reading `design/canonical-workload.yaml`).

Crucially, these are **independent sensitivity dimensions**, and each pushes the break-even in a different direction; do not collapse them into one "the assumptions vary" disclaimer:

- **Fleet size** (N_hosts) — driven by the KV/prefill/SLO scopes (Ch 17-20), not by TCO. A larger fleet raises the flat self-host line (more capex+opex) and shifts break-even right.
- **Paid occupancy** — the cloud bill is an occupancy INPUT (host-hours), while self-hosted reserved cards bill flat regardless of utilization. Separating these two is what makes the self-host (high fixed, low variable) vs cloud (low fixed, high variable) comparison meaningful — and it is exactly why the two scopes are not comparable until the occupancy is evidenced.
- **Utilization** — the *provisioning* utilization target (70% vs 100%, Ch 17) sets how many hosts are needed, not how much they cost per unit; it is a separate line from the price-per-host.
- **Reserved / on-demand mix** — whether capacity is committed (cheaper, flat) or burst (pricier, on-demand) is a distinct lever; a mixed fleet has both a flat and a variable term.
- **Failover reserve** — N-1/headroom hosts (Ch 17) add cost but are not production-serving capacity; they must be counted as a separate reserve line, not folded into the served-load hosts.
- **Staffing** — the dominant human term for self-hosting; it is frequently the decider at low volume (Ch 16 §16.8 mini-case) and should be its own sensitivity dimension, not absorbed into opex.

Because these dimensions are independent, the break-even is a **region**, not a point: the figure marks the [ILLUSTRATIVE] price band, and the honest output is a range (here ~6.2–10.4M req/mo) rather than a single "the break-even is 7.5M" claim. The headline range varies the **API price** against the 21-host self-host cost ($155,816.93/mo): the low end is 6,232,677.2 = 155,816.93 ÷ 0.025 (the $25/1K top of the band) and the high end is 10,387,795.33 = 155,816.93 ÷ 0.015 (the $15/1K bottom of the band) — the same ~6.2–10.4M range reported with Fig 16.1 and in §16.6; the mid-point at the canonical $20.8/1K is 7,491,198.56 ≈ **7.5M**. The **70%-utilization provisioning case** is a separate dimension and is named separately: the $218,309.90/mo 30-host cost against the canonical $20.8/1K API rate gives 218,309.90 ÷ 0.0208 ≈ **10.5M** req/mo. Report the range and name which dimension is being varied. Note also that these are **parameterized fixed-resource cost curves, not capacity forecasts**: the self-host line is flat because the 21 hosts are paid for regardless of volume, so nothing here predicts what volume the fleet can *serve* as requests grow.

**Which dimension the x-axis varies — stated explicitly (F0201).** Fig 16.1 varies **(A) served volume through duration / duty-cycle at a FIXED 40 rps peak and a FIXED fleet**: the 21-host ideal-active line (and the 30-host = 29 working + 1 reserve policy line) is held constant, and only how long the peak-shaped load runs inside the active window moves along x. It does **not** do **(B)** — scaling average and peak together and re-running `N_hosts(volume)` with the integer slot floor — which would stair-step the self-host line upward (⌈λ·8.6/17⌉ hosts per step) instead of leaving it flat. Because the fleet and its cost are frozen, **$155,816.93 ÷ $0.0208 = 7,491,198.56 ≈ 7.5M is a frozen-fleet crossover, not a generalized scalable crossover**: it holds only while those 21 hosts and that $155,816.93/month are held fixed, and it must not be read as "the volume at which a growing deployment becomes cheaper."

**Feasible served-volume bound (the figure marks it).** Under (A) the fixed 21-host fleet is sized for the 40 rps peak over the canonical active window of **624,000 active seconds/month** (6,240,000 requests ÷ 10 rps), so the most it can serve is 40 × 624,000 = **24,960,000 ≈ 24.96M requests/month**. Everything to the right of 24.96M on the x-axis — the plot runs to 10^8 — is **infeasible for this frozen fleet** and is drawn only to show the shape of the cost functions; the figure shades and labels that band. The break-even region (~6.2–10.4M) and the canonical 6.24M both sit inside the feasible band, so the crossover itself is reachable without re-sizing; only the far right of the plot is not. The break-even stays a **region, not a point**, and the dimension varied to produce that region is the **API price** ($15–25/1K band) against the frozen self-host cost — not volume, and not fleet size. The figure is **illustrative, not apples-to-apples**.

## 4. Measurement

Four metrics keep the TCO model honest:

1. **Cost per useful (SLO-meeting) request** — the decision number; divide total cost by goodput-meeting requests (Ch 6), not raw tokens.
2. **Effective utilization** — actual goodput ÷ theoretical capacity across the billing period; low utilization is the hidden tax in both capex and rented instances.
3. **Break-even volume** — the requests/month where self-host cost-per-request crosses managed API; below it, don't buy cards.
4. **Staff/occupancy adjusters** — the engineering-hours and paid-occupancy assumptions that dominate the comparisons; measure them, don't assume.

### Support lifecycle belongs in service cost

A lower accelerator price does not establish a lower service cost. Migration work, pinned-runtime maintenance, security updates, failed attempts, spare capacity, and fallback execution belong in the numerator. The denominator remains quality-qualified, SLO-compliant work. If a candidate needs more replicas because of worse tail latency or lower usable KV capacity, that requirement can reverse an apparent device-price advantage. This extends the cost model; it does not supply a backend ranking. [ILLUSTRATIVE][DERIVED]

**Software-lifecycle observation, 28 October 2026 — outside the 30 August evidence snapshot.** Intel's IPEX retirement guidance recommends upstream PyTorch and states that active development and official quarterly releases stopped after release 2.8. The inspected IPEX-LLM README separately declares that project archived, disclaims ongoing support, and warns of known security issues.[^oct16-lifecycle] An archived optimization may remain executable without being an appropriate default for a maintained service. An existing deployment therefore needs a documented migration or support decision. Current prices and measured service capacity are still required before either IPEX or IPEX-LLM receives a TCO recommendation; this is not a new price or capacity measurement.

[^oct16-lifecycle]: Intel, *Intel Extension for PyTorch*, “Retirement Plan,” retrieved 28 October 2026: https://intel.github.io/intel-extension-for-pytorch/xpu/latest . This is a dated observation of the retirement notice, not an independently verified completion date. Intel, *IPEX-LLM*, README at commit `de6bce27133ab250f13fd5d549c197519ce16d30`: https://raw.githubusercontent.com/intel/ipex-llm/de6bce27133ab250f13fd5d549c197519ce16d30/README.md . The pinned bytes match the 28 October archive; the archive warning does not identify a vulnerability in every possible deployment configuration.

## 5. Common Mistakes

- **Comparing sticker price to per-token rate.** A $/1K-token API quote already includes amortization; a card price tag does not. Amortize both.
- **Ignoring the staff/ops term.** Self-host "saves money" on paper and loses the moment two engineers are consumed full-time.
- **Assuming 100% utilization.** Idle cards are still burning electricity and depreciation; bake duty cycle in.
- **Forgetting opportunity cost.** A 6-month procurement cycle versus a same-week API integration is a real cost measured in time-to-value.
- **Using peak capacity for cost-per-request.** Peak sizing (40 rps) overstates cost if average (10 rps) utilization is what governs. (The headline $24.97/1K above does divide the peak-sized 21-host fleet by average volume — deliberately: this workload must clear the 40 rps peak, so peak capacity is real cost here; the mistake applies when peak sizing is avoidable, e.g. batch or queueable traffic.)
- **Treating an occupancy input as a measurement.** The cloud default (4,380 paid host-hours) is an assumption, not a trace; never promote it to a measured duty cycle or a guaranteed lower bound.

## 6. Architecture Consequence

TCO is the final gate in the design loop (Ch 12 candidates → Ch 14 benchmark → Ch 16 cost). It settles which candidate survives: the 70B 8×H100 self-host **passes the capability screen and is analytically screened for feasibility — it *would* need a representative hardware benchmark to establish SLO-goodput** (the `C/W` and roofline estimates of Chs. 7–8 are planning bounds, not a measured p95 TTFT/TPOT pass at the target offered load), and on TCO it **sits above the managed API at the canonical 6.24M volume** ($155,816.93/mo vs $129,792/mo — the ~7.5M API break-even sits above the canonical volume) and above the cloud default-occupancy input ($87,600/mo) **on that input's assumptions** — so the surviving recommendation is *conditional* (self-host wins only once volume passes the ~7.5M break-even — lower if the staff/ops term is sunk — with sustained near-peak utilization and a benchmark confirming the SLO; the cloud alternative is lower-cost **only if** its paid-occupancy input holds and the scopes are equalized; neither is an unconditional ranking).

This completes the chain from vague requirement to a defensible, costed architecture, while being honest that the TCO gate is not an unconditional win and that the SLO pass is *provisional until benchmarked*.

It also feeds fleet decisions (Ch 17-18): the break-even curve is what justifies buying a second host versus renting peaks, and the staff term is what pushes toward consolidation (Ch 18).

![Fig 16.1 — TCO break-even: self-hosted vs managed API (canonical 80-layer full-MHA geometry). The break-even volume is **illustrative, not portable** — it holds only for this 70B FP16 8×H100 config, 5-year amortization, \$20.80/1K API price, and 9.2K-in/300-out mix. **Not apples-to-apples across demand levels:** self-hosted = (capex ÷ 60 mo) + energy + staff/ops; managed-API = input×\$/1M + output×\$/1M-out; utilization = served ÷ provisioned — the self-host line assumes the 21-host peak KV-screen fleet (zero spare), so break-even is a function of demand, not a fixed point. **x varies duration/duty-cycle at a FIXED 40 rps peak and a FIXED 21-host fleet (option A, not a per-volume re-sizing); the feasible served-volume bound is 40 rps × 624,000 canonical active seconds/month ≈ 24.96M req/mo, and the shaded band right of it is infeasible for this frozen fleet.** [ILLUSTRATIVE][DERIVED]](figures/fig-16-1601.png)

*Break-even: monthly cost vs monthly volume for self-hosted and managed API across three serve modes. The self-host line crosses the managed line over a **range** of ~6.2–10.4 M requests/mo (the \$15–25/1K price band), with the ~7.5 M mid-point at the canonical \$20.80/1K (\$155,816.93/mo ÷ \$0.0208 per request) — a **frozen-fleet crossover, not a generalized scalable crossover**, because the 21-host cost is held fixed while only duration/duty-cycle moves along x. The figure marks the mid-point (star) and the full sensitivity span (horizontal line), annotates the feasible bound (24.96M = 40 rps × 624,000 active s), and shades the infeasible region beyond it.*

<!-- Figure spec: mechanism-first plot; x = requests/month, y = cost/month (log-log); self-host flat line at the 21-host included cost; cloud flat line at the default paid-occupancy input; managed-API zero-intercept linear; x-axis dimension = (A) duration/duty-cycle at fixed 40 rps peak + fixed 21-host fleet (fleet NOT re-sized per volume); feasible bound 40 rps x 624,000 active s = 24.96M req/mo with the region right of it shaded and labelled infeasible; mark break-even volume and price band; annotate the occupancy-input assumption. -->

## 7. What We Still Don't Know

- **Real equipment/power/staff numbers** for a given deployment are site-specific [UNRESOLVED]; the illustrative quotes above must be re-priced.
- **How rapidly GPU list and amortization prices fall** over the 5-year horizon is [HYPOTHESIS]; newer cards (H200/B200-class) change the per-card economics.
- **The true staff overhead of self-hosting** (SRE time, security, upgrades) is [HYPOTHESIS] until the team bills its own time honestly.

## 8. End-of-Chapter Mini-Case: TCO Discipline and the Staff Term

A startup's CTO shows the architect a warrant to buy two 8×H100 servers for the new internal RAG assistant, citing "we'll save on token fees." Applying TCO discipline, the architect does not dispute the raw token math. Instead they price it: at this startup's *actual* early volume — ~2 rps average, ~5M requests/month, and only 0.5 engineers fully available for GPU ops — the break-even against a managed API is this chapter's own division: $40,000 ÷ $0.0208 ≈ **1.9M requests/month**, so the current volume is already ~2.6× past the break-even.

The honest number: self-hosting two servers ~$40K/month all-in vs ~$104K/month API at current volume (5M × $0.0208) — a **~$64K/month saving in favor of self-hosting, with the staff term already inside the $40K** (capex ~$11.6K + power ~$2.2K for two hosts leaves ≤ ~$26K for staff — upkeep is the power line already counted, so ~$0.2K of the $26.2K remainder is unallocated — too small to dwarf a $64K saving). The staff term is on a different basis than Mode 1: the mini-case prices a startup's 0.5-FTE operator (~$26K/mo — ≈$624K/yr fully loaded for one engineer, a scenario value rather than a market rate), not Mode 1's mature-operator alloc (~$10K/mo for 21 hosts) — re-price on one staffing basis before comparing.

The token arithmetic therefore does not send this startup to the API; it points to self-hosting. Only one term can flip the decision: the *opportunity* cost of the GPU-ops time the two servers consume — the better part of the only engineer the startup can spare. To justify paying the API premium, that term must exceed **~$64K/month**, about $770K/year of product work the startup is not doing. The architect's verdict: **start on the managed API now, and revisit self-host the moment the consumed engineer's opportunity cost falls below ~$64K/month — for example when a second engineer frees up** — then re-run the same model. Request volume is not the lever: more volume only widens the ~$64K gap. The CTO did not buy the servers. The break-even graph did not make the answer self-evident; it narrowed the whole decision to one labeled assumption — this startup values its half-engineer's product time above $64K/month. A team that cannot say that, or that has a second engineer to spare, runs the same numbers and buys the servers.