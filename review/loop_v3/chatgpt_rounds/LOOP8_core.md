# *From Token to Fleet* — Loop 8 Publication-Readiness Review

## 1. Audit identity and scope

| Item | Audit record |
|---|---|
| Manuscript | `from-token-to-fleet-v20260913.pdf`, by Zhiqi Tao |
| Supplied SHA-256 | `e5451a24ef1acc5b2a0ae87a47b059294ed6055c997717cd3882e64f6875a94c` — **not independently computed** |
| Supplied physical extent | 362 US Letter pages — **PDF not supplied for direct inspection** |
| Text actually available | Extracted manuscript, cover through final worksheet |
| Counts recoverable from supplied text | **26 numbered chapters**, Appendix A; **40 chapter figures + 4 appendix figures + 2 front-matter figures = 46 figures** |
| Count discrepancies | Supplied identity says 27 chapters and 40 numbered figures. The supplied text contains chapters 1–26, not chapter 27; 40 excludes the appendix figures. |
| Tables/equations | Supplied table count of 33 not independently certified; additional substantive unnumbered tables exist. No complete displayed-equation count established. |
| Evidence cutoff | Stated as 2026-08-30, with separately identified 2026-09-27 addendum |
| Review date | 2026-03-10. The manuscript’s stated snapshot and addendum dates are future dates relative to this review environment. Their claimed source capture cannot presently be authenticated here. |
| Tools/assets | No PDF rendering, code execution, browsing, source repository, manifests, datasets, or prior issue register available |
| Visual responsibility | Pixel-level inspection delegated by the user to the orchestrator. This review assesses **caption, extracted labels, graphical semantics, and surrounding reasoning only**. |

**Location convention:** Body physical PDF locations below are calculated from the supplied relationship **PDF page = printed folio + 18**. They are text locations mapped using that supplied offset, **not independently inspected PDF pages**. Front-matter physical locations are not guessed.

**Coverage:** The entire supplied extracted text was read and challenged. Rendered-page coverage is **0/362**; pixel-level figure coverage **0/46**; live external-source verification **0**. Quantitative checks below are independent hand recalculations, not executed scripts. This is a substantive text audit, **not full PDF or print certification**.

---

## 2. Executive decision and scorecard

### **NOT READY — RELEASE BLOCKERS**

The manuscript still contains consequential contradictions in the canonical economics, the claimed fleet reduction from FP8 KV, and the flagship capstone’s baseline and savings model. Several corrections are locally acknowledged in caveats but remain contradicted by headings, equations, tables, or final recommendations; another cautionary paragraph will not close them.

**Unique findings:** **2 P0, 23 P1, 3 P2.** These are current-text findings, not inherited findings from previous loops.

The smallest coherent repair is to freeze one workload/time basis, establish separate memory and phase-capacity models, rebuild the agent example from a call trace, and then regenerate the dependent economics and capstone.

| Quality gate | Result | Principal reason |
|---|---|---|
| 1. Technical correctness | **FAIL** | Residency, parallelism, cache semantics, and communication errors remain |
| 2. Canonical numerical consistency | **FAIL** | Business-hours workload becomes continuous monthly traffic; FP8 memory savings become unsupported fleet savings |
| 3. Equations and quantitative examples | **FAIL** | Invalid network aggregation; incomplete decode roofline; inconsistent agent accounting |
| 4. Evidence/citations | **FAIL** | Synthetic inputs/results still become FACT, DERIVED, or purported telemetry |
| 5. Visual/figure print readiness | **NOT VERIFIED** | No pixels inspected; several semantic/caption defects confirmed |
| 6. Story/pedagogy | **FAIL** | Key synthesis sections teach conclusions contradicted by the mechanism chapters |
| 7. Typography and PDF production | **NOT VERIFIED** | Actual PDF unavailable |
| 8. References/links/accessibility | **NOT VERIFIED** | No browsing or PDF navigation inspection |
| 9. Version/rights/reproducibility | **NOT VERIFIED** | Supplied hash, commit, license, source captures, and signed manifest not authenticated |
| 10. Full audit coverage | **NOT VERIFIED** | Complete supplied-text reading, but no complete physical-artifact audit |

---

## 3. P0/P1 priority queue

| ID | Priority | Primary PDF / printed location | Required correction |
|---|---|---|---|
| FTF-0001 | P0 | 210 / 192, Ch. 16 | Reprice the canonical workload on its declared business-hours schedule |
| FTF-0002 | P0 | 324–327 / 306–309, Ch. 26 | Replace the capstone’s already-sharded baseline and unsupported fixed-cost savings |
| FTF-0003 | P1 | 209, 228 / 191, 210 | Stop converting KV savings or shorter decode directly into full fleet reductions |
| FTF-0004 | P1 | 208–215, 223 / 190–197, 205 | Apply one integer-slot and reserve convention throughout |
| FTF-0005 | P1 | 132–134 / 114–116 | Include KV reads in decode intensity and batching analysis |
| FTF-0006 | P1 | 51, 56, 153–154 / 33, 38, 135–136 | Correct total-versus-active memory rules and MoE rejection |
| FTF-0007 | P1 | 153, 182, 184 / 135, 164, 166 | Restore intra-host model parallelism to the canonical deployment |
| FTF-0008 | P1 | 139–141 / 121–123 | Recalculate NVLink collective times using a consistent directional bandwidth |
| FTF-0009 | P1 | 139–142 / 121–124 | Replace impossible 140-GB-per-rank H100 collectives/test instructions |
| FTF-0010 | P1 | 230, 232, 235 / 212, 214, 217 | Use request arrival rate, not host count, to derive aggregate network traffic |
| FTF-0011 | P1 | 103, 105–106, 158 / 85, 87–88, 140 | Establish exact-prefix eligibility before assigning prefix-cache savings |
| FTF-0012 | P1 | 234, 261 / 216, 243 | Separate search-result caching, prefix reuse, and retained KV |
| FTF-0013 | P1 | 250–254 / 232–236 | Rebuild agent tokens and service time from an explicit invocation trace |
| FTF-0014 | P1 | 224, 260 / 206, 242 | Correct fallback accounting and conditional/unconditional percentiles |
| FTF-0015 | P1 | 101, 104 / 83, 86 | Derive goodput from compliant outcomes, not a p95 breach alone |
| FTF-0016 | P1 | 240–245 / 222–227 | Compare mixed-model cost and latency on the same request/hardware basis |
| FTF-0017 | P1 | 297–298 / 279–280 | Replace the nontransitive PIES “equivalence relation” |
| FTF-0018 | P1 | 301–305 / 283–287 | Repair security denominators and sampling adequacy |
| FTF-0019 | P1 | 89, 205–206, 260, 328 / 71, 187–188, 242, 310 | Reconcile evidence labels with actual origin and validation status |
| FTF-0020 | P1 | 332, 338 / 314, 320 | Correct DeepSeek variant identity and GLM metric scope in appendix figures |
| FTF-0021 | P1 | 145, 227, 281 / 127, 209, 263 | Remove residual population-to-rate/concurrency substitutions |
| FTF-0022 | P1 | 323 / 305 | Specify safe response-cache identity and distinguish exact from semantic caching |
| FTF-0023 | P1 | 194–204 / 176–186 | Distinguish the SDPA operation/API from its selected implementation |
| FTF-0024 | P1 | 128, 196, 285 / 110, 178, 267 | Declare whether attention FLOPs count full-square or causal triangular work |
| FTF-0025 | P1 | 265, 270 / 247, 252 | Correct the claim that matched token-rate/request-size division is dimensionally invalid |

Acceptance criteria and dependent locations follow.

---

## 4. Detailed issue register

### FTF-0001 — P0 — The canonical TCO uses the monthly traffic volume explicitly rejected by Chapter 4

- **Confidence:** CONFIRMED
- **PDF / printed page:** 65 / 47; 210–218 / 192–200; dependent 241 / 223, 274–275 / 256–257, 327 / 309.
- **Anchor:** Canonical workload “active business-hours window”; Ch. 16 “Per request at ~10 rps average = ~26M/month.”
- **Observed:** Chapter 4 specifies 10 rps over **8 hours × 260 workdays/year**, expressly rejecting 24×7 extrapolation. Chapter 16 nevertheless divides costs by approximately 26 million monthly requests and prices the API at that volume.
- **Independent recomputation:**
  \[
  V_{\rm year}=10\times3600\times8\times260=74{,}880{,}000
  \]
  \[
  V_{\rm month}=6{,}240{,}000.
  \]
  Keeping the displayed illustrative monthly infrastructure totals:
  - $148K/month → **$23.72/1K requests**, not $5.7.
  - $217K/month → **$34.78/1K**, not $8.4.
  - Managed API: \(6.24M\times\$0.0208=\mathbf{\$129{,}792/month}\), not $541K.
  - A $73K cloud bill, **if independently justified**, would normalize to **$11.70/1K**, not $2.8.
- **Why it matters:** The stated self-host-versus-API result reverses at the canonical business-hours volume: $148K exceeds $129.8K. Cloud host-hours also require a new schedule calculation, not merely a new request denominator.
- **Root cause/dependencies:** Ch. 16 Tables 16-1/16-2, Fig. 16.1’s “canonical 26M” marker, Ch. 18’s approximately $0.60/M normalization, Ch. 21 daily volume, Ch. 26’s $0.0057 baseline.
- **Required correction:** Choose the canonical schedule once. Recalculate volume, cloud host-hours, effective utilization, normalized costs, comparisons, and downstream savings. If continuous traffic is retained as a separate scenario, name it separately.
- **Acceptance test:** Every canonical monthly request count equals 6.24M on an annualized-average-month basis; every cost denominator and economic conclusion follows that schedule.
- **Status:** OPEN

### FTF-0002 — P0 — The capstone double-counts sharding and treats fixed fleet expenditure as per-request variable cost

- **Confidence:** CONFIRMED
- **PDF / printed page:** 321–329 / 303–311.
- **Anchor:** “single 8×H100 node”; “uncached, unsharded baseline”; “×0.65×0.80”; rejection of a second host.
- **Observed:** The starting deployment already serves a 140-GB model across an 8×H100 node. Pattern A then applies that same intra-node sharding and claims a further 20% lower generation cost. The example multiplies Chapter 16’s **fully loaded, peak-provisioned fleet average cost** by cache-miss fraction and that sharding discount.
- **Evidence:** The local baseline is already multi-GPU: 140 GB cannot reside on one 80-GB GPU. Cache hits reduce generation work, but do not automatically reduce the owned fleet’s depreciation, staffing, or provisioned capacity by 35%. The displayed 48% is arithmetic on **assumed variable-cost fractions**, not a derived reduction in that fixed-cost ledger.
- **Additional contradiction:** §26.3 initially invokes canonical 10/40-rps demand; §26.8 changes the edge rate to 2 rps. At 40 edge rps, a 35% result-cache hit rate still sends **26 rps** to the engine. A single approximately 2-rps planning unit does not serve that workload. Extra replicas address concurrency precisely because concurrency is binding; “<5% per-request latency improvement” does not reject their capacity value.
- **Why it matters:** The book’s final synthesis currently demonstrates an invalid architectural and economic comparison.
- **Required correction:** Specify:
  1. baseline topology and traffic;
  2. the actual architectural change;
  3. separately measured/assumed cache-hit and miss paths;
  4. fixed, variable, and avoidable cost;
  5. capacity and quality of the fallback path.
  
  Retain the valid two-point quantile illustration, but do not present its assumed miss latency or cost discount as an established architectural consequence.
- **Acceptance test:** No optimization is credited twice; costs reconcile to actual provisioned host-hours or an explicitly variable API/compute ledger; edge and engine rates reconcile; the revised capstone has one baseline throughout.
- **Status:** OPEN

### FTF-0003 — P1 — FP8 KV and faster decode are incorrectly converted into full fleet reductions

- **Confidence:** CONFIRMED
- **PDF / printed page:** 209 / 191; 214 / 196; 223, 228, 232 / 205, 210, 214; 234–236 / 216–218.
- **Anchor:** “FP8 KV roughly halves this to ~10 hosts”; service-time sensitivity “~6 hosts.”
- **Observed:** The book repeatedly promotes a halved **KV-only host requirement** into a halved fleet, despite its unchanged prefill requirement.
- **Independent recomputation:**
  \[
  F_{\rm prefill,peak}=40\times2(70\times10^9)(9200)
  =51.52\ {\rm PFLOP/s}.
  \]
  At the stated 35% planning MFU:
  \[
  F_{\rm host}=8(0.989)(0.35)=2.7692\ {\rm PFLOP/s},
  \]
  requiring **ceil(51.52/2.7692) = 19 hosts for linear prefill alone**, before decode coexistence and other costs. Ten FP8-KV hosts do not clear that screen.
  
  The “six hosts” fast-decode sensitivity fails even the **100%-peak** prefill test:
  \(6\times7.912=47.472<51.52\) PFLOP/s.
- **Why it matters:** The recommended cheapest fleet-reduction lever may not reduce the actual fleet at all when prefill binds.
- **Required correction:** Label each sensitivity **KV-only** and take the maximum with separately derived prefill, decode, SLO, and failure-domain requirements. State any prefix-hit or efficiency change needed to obtain a smaller fleet.
- **Acceptance test:** No full-fleet claim falls below its own phase-capacity screen; FP8 changes only the inputs it actually affects.
- **Status:** OPEN

### FTF-0004 — P1 — Fractional concurrency is used after the book declares whole-slot reservation

- **Confidence:** CONFIRMED
- **PDF / printed page:** 208–215 / 190–197; 223 / 205; 235–236 / 217–218.
- **Anchor:** “conservative integer floor 17”; “~5 hosts average / ~20 peak.”
- **Observed:** The manuscript explicitly reserves a 9.5K maximum context per request and floors concurrency to 17, but its full-utilization fleet calculations continue to divide by 17.5.
- **Independent recomputation under that declared reservation policy:**
  \[
  N_{\rm avg}=\lceil86/17\rceil=\mathbf6,\qquad
  N_{\rm peak}=\lceil344/17\rceil=\mathbf{21}.
  \]
  At 70%:
  \[
  \lceil344/(17\times0.7)\rceil=29,
  \]
  plus one spare = 30.
- **Related reserve error:** Table 16-2 labels the approximately 20-host configuration “N−1” and says it survives one host loss, although the full-utilization calculation has no such reserve.
- **Why it matters:** The average fleet changes by 20% under the book’s own whole-slot convention; the failure guarantee is misstated.
- **Required correction:** Either use fixed whole maximum-context slots consistently, or model time-varying allocated bytes and sequence lengths explicitly. Do not mix the two.
- **Acceptance test:** All host counts follow the selected admission/allocation convention, and each N−1 claim satisfies demand after one host is removed.
- **Status:** OPEN

### FTF-0005 — P1 — The canonical decode batching roofline omits its dominant growing KV traffic

- **Confidence:** CONFIRMED
- **PDF / printed page:** 132–134 / 114–116; dependent 228 / 210.
- **Anchor:** “decode intensity ≈ batch size”; “compute-bound decode needs batch ≈295.”
- **Observed:** The batch-size crossover uses weight bytes only, although each canonical sequence also reads approximately 24 GB of KV per decode step.
- **Independent reconstruction**, at 9.2K context, FP16 full MHA:
  - Weight bytes/step: approximately 140 GB.
  - KV bytes/sequence/step: approximately 24.117 GB.
  - Parameter FLOPs/sequence: 140 GFLOP.
  - Attention FLOPs/sequence: approximately \(4(80)(8192)(9200)=24.117\) GFLOP.
  
  Ignoring other traffic:
  \[
  AI(B)\approx\frac{164.117B}{140+24.117B}\ {\rm FLOP/byte}.
  \]
  At \(B=17\), this is approximately **5.07 FLOP/byte**, not 17. As \(B\to\infty\), it approaches **6.80**, not 295.
- **Why it matters:** The book teaches a crossover that does not exist in this canonical full-MHA, long-context model under the stated HBM-streaming assumptions.
- **Required correction:** Present \(AI\approx B\) as a **weight-dominated approximation**, then add the KV term and its context-dependent saturation. Recalculate latency floors at realistic concurrent batch sizes.
- **Acceptance test:** The canonical batching curve counts both weights and KV; any compute-bound crossover identifies an actually applicable model, context, precision, and traffic regime.
- **Status:** OPEN

### FTF-0006 — P1 — MoE memory conclusions contradict the correctly stated total-residency rule

- **Confidence:** CONFIRMED
- **PDF / printed page:** 51–56 / 33–38; 94 / 76; 153–154 / 135–136.
- **Anchors:** “Using the total count to size memory over-provisions”; “the MoE challenger fails”; EP “memory-bound decision … against active parameters.”
- **Observed:** Three conclusions reverse the chapter’s correct rule:
  - §3.5 says total-parameter memory budgeting over-provisions.
  - The 47B challenger is rejected because it “does not cut the memory budget,” although its table gives **94 GB versus 140 GB** of resident weights with identical controlled KV.
  - Chapter 10 directs a memory-bound EP decision to active rather than total parameters.
- **Evidence:** At equal cache geometry, one-request weight-plus-KV residency changes from approximately 164.1 GB to **118.1 GB**. That is a real 46-GB reduction, although not a reduction proportional to active fraction.
- **Why it matters:** This can cause both undersizing of expert storage and rejection of a genuinely lower-residency candidate.
- **Required correction:** Use total resident inventory for storage and placement; active parameters for approximate per-token computation. Rework the rejection around an explicitly quantified routing, quality, latency, or operational disadvantage—not nonexistent memory savings.
- **Acceptance test:** No unoffloaded MoE deployment budgets only active experts; every challenger verdict agrees with its own weight/KV table.
- **Status:** OPEN

### FTF-0007 — P1 — “One host” is repeatedly mistaken for “no model parallelism”

- **Confidence:** CONFIRMED
- **PDF / printed page:** 153 / 135; 182, 184 / 164, 166.
- **Anchor:** “no parallelism is required at the baseline”; “parallelism is unnecessary (one node).”
- **Observed:** Chapters 10 and 13 remove parallelism from the canonical 140-GB model on eight separate 80-GB GPUs.
- **Evidence:** No individual GPU holds the weights. Earlier and later chapters explicitly assume TP=8, sharded weights, and sharded KV. Aggregate node memory is not automatically shared device memory.
- **Why it matters:** This erases the topology, communication, and per-rank fit requirements that justify the host.
- **Required correction:** State “no **cross-host** model parallelism is required; intra-host TP/PP or another explicitly supported execution scheme is required.” Also remove the claim that context partitioning and EP have no training analogue; EP is correctly described elsewhere as serving both modes.
- **Acceptance test:** The canonical execution topology is identical across Chapters 7, 9–13, 17, and 26.
- **Status:** OPEN

### FTF-0008 — P1 — NVLink bidirectional bandwidth is used as unilateral ring-send bandwidth

- **Confidence:** CONFIRMED
- **PDF / printed page:** 139–141 / 121–123; 152 / 134.
- **Anchor:** “900 GB/s … 450 GB/s per direction”; ring-adjusted 0.27 s.
- **Observed:** Ring traffic counted as bytes **sent per rank** is divided by the combined send-plus-receive bandwidth.
- **Independent recomputation using the book’s own convention:**
  \[
  V_{\rm sent}=1.75(140)=245\ {\rm GB};
  \quad t=245/450\approx\mathbf{0.544\ s},
  \]
  before latency/other overhead—not 0.27 s.
  
  Against the displayed 6.125-s IB and 98-s Ethernet estimates, ratios become approximately **11.3× and 180×**, not 22× and 350×. The analogous 280-GB-gradient NVLink time becomes approximately **1.09 s**, not 0.54 s.
- **Why it matters:** Communication costs and fabric comparisons are understated by about 2×.
- **Required correction:** Define whether bandwidth and byte volume are unidirectional or combined. Recompute examples, plots, and recommendations consistently.
- **Acceptance test:** Send bytes divide by send bandwidth, or combined bytes divide by combined bandwidth; no mixed convention remains.
- **Status:** OPEN

### FTF-0009 — P1 — The communication example and proposed benchmark do not fit their H100 ranks

- **Confidence:** CONFIRMED
- **PDF / printed page:** 139–142 / 121–124; 151–152 / 133–134.
- **Anchor:** “M=140 GB per rank”; “one GPU per node”; nccl-tests “up to 140 GB.”
- **Observed:** A single 80-GB H100 is asked to hold a 140-GB collective input. Moving ranks across nodes does not fix that per-rank allocation. Chapter 10’s ordinary DP example likewise replicates a 140-GB model per 80-GB GPU.
- **Evidence:** The input tensor alone exceeds HBM, before output buffers, model state, or optimizer state.
- **Why it matters:** The proposed verification cannot run as described, and the worked deployment is not realizable.
- **Required correction:** Use feasible payloads/ranks, a chunked communication-only model explicitly distinguished from a single collective, or DP replicas that are themselves adequately model-sharded.
- **Acceptance test:** Every rank’s complete allocation fits; benchmark commands/configuration reproduce the stated byte boundary.
- **Status:** OPEN

### FTF-0010 — P1 — Aggregate network demand substitutes host count for concurrent requests

- **Confidence:** CONFIRMED
- **PDF / printed page:** 230, 232, 235 / 212, 214, 217.
- **Anchor:** \(B_{\rm agg}=\phi ND/t_{\rm net}\).
- **Observed:** \(N\) is the host count, but \(\phi N\) is called the expected number of concurrent cross-host requests.
- **Replacement derivation:** If a fraction \(\phi\) of requests produces one transfer of \(D\) bytes:
  \[
  \lambda_{\rm x}=\phi\lambda,\quad
  L_{\rm x}=\phi\lambda t_{\rm net},\quad
  B_{\rm avg}=L_{\rm x}D/t_{\rm net}=\mathbf{\phi\lambda D}.
  \]
  At 100 rps, \(\phi=0.05,D=5\) MB:
  \[
  B_{\rm avg}=25\ {\rm MB/s}=\mathbf{0.20\ Gbit/s},
  \]
  not 5.2–7.4 Gbit/s merely because 52–74 hosts exist.
- **Why it matters:** The text derives a ≥20-Gbit/s network upgrade from an invalid population substitution.
- **Required correction:** Separate average byte rate, burst/concurrency distribution, link paths, and transfer deadlines. \(D/t\) can be a required transfer rate, but is not automatically an observed burst or rack RTT.
- **Acceptance test:** Holding workload and transfer behavior fixed while changing replica count does not manufacture proportional aggregate traffic.
- **Status:** OPEN

### FTF-0011 — P1 — Shared documents and a low hit ratio do not establish prefix-cache savings

- **Confidence:** CONFIRMED
- **PDF / printed page:** 103–106 / 85–88; 158 / 140; 170 / 152.
- **Anchor:** “same retrieved documents”; “telemetry shows … enable prefix caching.”
- **Observed:** Prefix caching is prescribed as a demonstrated remedy without establishing exact token-prefix overlap, cache configuration, or sufficient reusable residency.
- **Counterexample:** If a unique question occurs before the retrieved documents, identical later document text does not yield reusable causal K/V for that document span. Different preceding tokens change its hidden states and K/V.
- **Why it matters:** The proposed configuration change may yield little or no benefit, despite the scenario claiming restored SLO.
- **Required correction:** Show the prompt layout and matching rule; measure reusable-prefix token lengths, hit rate, eviction/affinity, and FLOPs avoided. Treat low hit ratio as a symptom, not proof caching is disabled or useful.
- **Acceptance test:** A request trace demonstrates the claimed shared-prefix work and the corrected scenario’s capacity/SLO result.
- **Status:** OPEN

### FTF-0012 — P1 — Tool-result caching is incorrectly made to shrink retained context

- **Confidence:** CONFIRMED
- **PDF / printed page:** 234 / 216; 261 / 243.
- **Anchor:** “effective δ drops to ~560”; “eliminate … base prompt from the KV per turn.”
- **Observed:** A 30% search cache hit rate changes 800 returned tokens to 560 retained tokens. Elsewhere, prefix caching is said to eliminate the base prompt from per-turn KV.
- **Evidence:** Returning cached search results still returns the same 800 tokens if they are appended. Prefix reuse avoids recomputing existing K/V; it does not remove that logical context. Physical sharing can reduce duplicate storage across requests, but needs its own ownership/placement model.
- **Why it matters:** Both token amplification and fleet sizing credit savings to the wrong cache mechanism.
- **Required correction:** Keep search-result size unchanged unless an explicit deduplication, reference, truncation, or compaction policy changes it. Model physical prefix sharing separately from logical sequence length.
- **Acceptance test:** Cache on/off traces distinguish tool work, prompt tokens, newly processed tokens, billed tokens, and physical retained bytes.
- **Status:** OPEN

### FTF-0013 — P1 — Agent accounting still lacks a consistent model-invocation trace

- **Confidence:** CONFIRMED
- **PDF / printed page:** 250–254 / 232–236; dependent 234–236 / 216–218.
- **Anchors:** “current_input_length”; “3-call task”; “Total end-to-end.”
- **Observed:**
  - The table states \(9200+2(865)+300\approx12095\); that expression equals **11230**.
  - Final output is included in quantities called current input.
  - A purported full end-to-end row excludes the stated intermediate reasoning generation.
  - Chapter 17’s fleet service time uses a single representative prefill despite Chapter 19’s declared no-prefix-reuse policy.
- **Independent consistent example:** For **three tool cycles followed by a final answer**, with 65 generated tokens and 800 tool tokens per cycle:
  
  | Model call | Input | Generated output |
  |---|---:|---:|
  | 0 | 9,200 | 65 |
  | 1 | 10,065 | 65 |
  | 2 | 10,930 | 65 |
  | 3 | 11,795 | 300 |
  | **Task totals** | **41,990** | **495** |
  
  Final accumulated content is 12,095 tokens, but uncached processed input is 41,990—not a 1.27× processing multiplier.
- **Why it matters:** The explanatory caveat correctly separates retained context from task cost, but the worked tables and fleet service-time example still do not implement that distinction.
- **Required correction:** Make one invocation trace authoritative. Derive retained KV, repeated prefill, generated outputs, tools, fallbacks, latency, and costs from it. Rename orchestration-only rows; do not call them total end-to-end.
- **Acceptance test:** Every input/output token belongs to a specific call; all task totals and service times reconstruct from that trace.
- **Status:** OPEN

### FTF-0014 — P1 — Agent fallback costs and turn percentiles use incompatible populations

- **Confidence:** CONFIRMED
- **PDF / printed page:** 224 / 206; 251 / 233; 260–261 / 242–243.
- **Anchor:** “2% exceed the turn limit”; “zero added turns”; “95th-percentile T=3.”
- **Observed:** Requests that exceed the turn cap are charged zero agent work. Their latency is simultaneously described as zero added overhead and a high-tail category excluded from percentiles.
- **Independent check:** If fallback is genuinely represented as \(T=0\):
  \[
  P(T\le1)=0.02+0.68=0.70,\quad P(T\le2)=0.95.
  \]
  Under \(q_p=\inf\{t:F(t)\ge p\}\), unconditional **p95 is T=2**. Conditional on the 98% completed-agent population, \(0.93/0.98\approx0.949<0.95\), so conditional p95 is T=3.
- **Why it matters:** These are different valid distributions, not interchangeable labels. A request discovered to exceed a cap has already consumed work; restarting single-shot does not erase it.
- **Required correction:** Separate completion turn count, attempted turns, fallback cost, final retained context, and conditional/unconditional latency. Publish the fleet sizing percentile’s denominator.
- **Acceptance test:** Expectations and quantiles reproduce from one explicit outcome table, including all work before fallback.
- **Status:** OPEN

### FTF-0015 — P1 — A p95 breach does not determine goodput or make it zero

- **Confidence:** CONFIRMED
- **PDF / printed page:** 101, 104 / 83, 86; 161 / 143; 190 / 172.
- **Anchor:** “goodput … effectively unchanged”; “zeroing goodput.”
- **Observed:** Raising throughput from 50 to 70 tokens/s and moving p95 beyond the SLO is asserted to leave goodput unchanged, without a compliant-request count.
- **Counterexample:** With equal output lengths, compliant fractions of 96% and 94% yield:
  \[
  G_1=50(0.96)=48,\quad G_2=70(0.94)=65.8.
  \]
  The second configuration can have p95 above the deadline while goodput increases.
- **Why it matters:** A configuration-level percentile acceptance test and request-level SLO-goodput are different measurements.
- **Required correction:** Supply request-level outcomes or distributions, define whether goodput is request- or token-weighted, and compute it. Replace “zeroing” unless the defined metric explicitly rejects an entire configuration.
- **Acceptance test:** Goodput claims can be reconstructed independently from accepted/completed/compliant populations.
- **Status:** OPEN

### FTF-0016 — P1 — Mixed-model routing combines costs and latencies for different requests

- **Confidence:** CONFIRMED
- **PDF / printed page:** 240–245 / 222–227.
- **Anchor:** “cost … canonical 9.5K”; latency “short-prompt routing scenario.”
- **Observed:** The routing decision prices a 9.5K-token request but checks its SLO using 120/250/300-ms timings explicitly belonging to another request shape.
- **Additional hard fit failure:** The proposed one-H100 70B 8-bit tier has approximately 70 GB weights. Canonical FP16 KV adds 24.9 GB: **94.9 GB > 80 GB**, even before runtime.
- **Why it matters:** The weighted cost arithmetic is valid for assumed rates, but the “SLO-constrained saving” and placement decision are not demonstrated for the priced workload.
- **Required correction:** Use matched per-model token profiles, KV precision, hardware, throughput, latency distributions, and cost boundary. If the short-prompt example is retained, price that same short-prompt example.
- **Acceptance test:** Each tier physically fits and passes quality/SLO on the same request population used in the cost calculation.
- **Status:** OPEN

### FTF-0017 — P1 — PIES does not define equivalence classes

- **Confidence:** CONFIRMED
- **PDF / printed page:** 297–298 / 279–280; glossary 347 / 329.
- **Anchor:** “NLE ≤0.25 … equivalence relation.”
- **Observed:** Thresholded normalized edit distance is declared an equivalence relation defining distinct classes.
- **Counterexample:** For strings `0000`, `0001`, `0011`, adjacent distances are 0.25 and 0.25, but endpoint distance is 0.5. The relation is **not transitive**.
- **Why it matters:** Class count can depend on ordering or clustering algorithm. Moreover, a count of patterns one can **submit** does not necessarily decrease when guardrails block harmful outcomes.
- **Required correction:** Specify a deterministic clustering algorithm and linkage/order policy, or choose another partition. Define whether PIES counts accepted inputs, successful unauthorized outcomes, or tested attack families. Do not call textual proximity semantic equivalence.
- **Acceptance test:** Permuting the same probe corpus gives the declared reproducible result, and hardening changes the measured property the definition actually names.
- **Status:** OPEN

### FTF-0018 — P1 — Security metrics have impossible denominators and insufficient validation samples

- **Confidence:** CONFIRMED
- **PDF / printed page:** 301–305 / 283–287.
- **Anchor:** “4.1 interventions per 1,000”; “1.3% ≈13 per 1,000”; “samples 100 retrievals.”
- **Observed:** The final scenario reports 13 false blocks per 1,000 queries while reporting only 4.1 total guardrail interventions per 1,000. The former cannot be a subset of the latter.
- **Independent statistical check:** With zero poisoned-hit observations in 100 independent queries, the one-sided 95% upper bound is:
  \[
  1-0.05^{1/100}\approx\mathbf{2.95\%},
  \]
  not below the 0.3% target. Approximately **998 zero-hit independent queries** are needed even for that simple one-sided demonstration.
- **Related scope error:** The uniform-retrieval poisoning example is a null model, **not a minimum exposure**; an irrelevant poisoned chunk can have zero retrieval probability.
- **Why it matters:** The displayed success state is arithmetically impossible, and the stated data pipeline cannot establish its security threshold.
- **Required correction:** Define every numerator/denominator and unit; enforce subset constraints; attach confidence bounds and a suitable evaluation sample. Label the uniform model neither an empirical estimate nor a lower bound.
- **Acceptance test:** Counts reconcile; confidence intervals support the thresholds; query-level poisoned-hit rate is not confused with poisoned chunks/query.
- **Status:** OPEN

### FTF-0019 — P1 — Evidence labels still promote illustrative scenarios into observations or derivations

- **Confidence:** CONFIRMED
- **PDF / printed page:** Representative 89 / 71; 110–111 / 92–93; 205–206 / 187–188; 260 / 242; 328 / 310; 353 / 335.
- **Anchors:** “measured-range”; “Telemetry over 30 days shows”; Fig.