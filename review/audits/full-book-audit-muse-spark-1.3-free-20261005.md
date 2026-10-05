# TAOCP-Standard Publication Audit: *From Token to Fleet*

## 1. OVERALL ASSESSMENT

**Strengths.** The manuscript is unusually disciplined for an architecture handbook. The canonical scenario (2,000 users / 10 rps avg / 40 rps peak / 9.2K-in + 300-out / 70B dense FP16 / 8xH100) is pinned in Ch.4 Table 4-3 and re-cited in essentially every chapter. The two-axis evidence taxonomy ([1P]/[2°]/[ILLUSTRATIVE] x [FACT]/[DERIVED]/[ASSUMPTION]/[HYPOTHESIS]) is applied consistently. The kernel-regime vs workload-capacity-deficit separation (Ch.2/6/8/15/17/20), the total-vs-active vs residency separation (Ch.3/7/10), the aggregate-vs-per-rank caveat (Ch.7/9/10/17), and the full-service-time Little's-law discipline (W~8.6s exec vs ~10s planning round, in-flight 86/344 vs active users 100/400) are stated explicitly and repeatedly. Numerical chains recompute correctly: 2x70Bx9.2K=1.29 PFLOP; 2x80x8192x2B=2,621,440B=2.62MB/token; 9,500x2.62MB=24.9GB; 140+24.9=164.9~165GB; 640-140-64=436GB; 436/24.9=17.51; 40x8.6=344; 344/17.5~20 hosts (29 at 70%); 989/3.35~295 ridge. This is a real quantitative spine, not decorative arithmetic.

**Remaining weaknesses preventing publication.**

1. The book is numerically self-consistent only because it repeats its caveats verbatim in many places. Repetition now costs more than it buys: Ch.2/6/8/15/22 re-derive the same 1.29 PFLOP / 5.6 TB/s pair; Ch.7/15/17/19 re-derive the same 24.9GB / 17.5 / 436GB triple; Ch.16/17/20 re-derive the same 20-host fleet. A reader experiences this as defensiveness, not rigor.
2. Visual finish is not at publication standard. Roughly one-third of figures are clean (KEEP); one-third need polish; one-third have material defects: unreadable essential labels at print size (Figs.1.1, 6.2, 7.4, 19.2, 19.3), annotation collisions (Figs.6.2, 7.2, 13.1, 22.1), slide-shrunk-onto-page composition with vast whitespace (Figs.11.2, 23.1), and box-and-arrow prose where geometry encodes nothing (Figs.11.2, 12.1, 23.1, 24.1).
3. Several sections are technically correct but low storyline value: Ch.24 PIES/RAG-poisoning toy metrics, Ch.18 three-tier GGUF mini-case, Ch.22 as a near-duplicate of Ch.1+2, and the Ch.12/13 candidate-vs-tier overlap.
4. The per-host throughput story has a visible seam: Ch.5's ~50 tok/s single-stream floor vs Ch.15's 35,000-70,000 tok/s batched serving range vs Ch.8's 19,800 prefill-tok/s idealized aggregate vs Ch.17/20's 2.0 req/s KV/service-time bound. Each is scoped correctly in-text, but a reader comparing tables will conclude the book contradicts itself unless the four quantities are reconciled in one place.

No catastrophic derivation error was found. The blocks to publication are finish, redundancy, and a small set of conceptual overclaims detailed below.

## 2. HIGHEST-PRIORITY TECHNICAL / CONCEPTUAL ISSUES

**P0-1. Single-host language still leaks.** The manuscript correctly distinguishes per-request latency feasibility (one 8xH100 meets TTFT 1.2s / TPOT 25ms for one request) from fleet capacity (5 hosts avg / 20 hosts peak). But Ch.4 §6, Ch.5 §3, Ch.11 §6, Ch.13 §3 each contain at least one sentence where "fits on a single 8xH100 host" or "meets SLO on a single host" can be read as a capacity claim. The scope notes repair the reading, but the repair should not be needed eight times. Fix: freeze one canonical sentence and reuse it verbatim; delete all variants.

**P0-2. 2NL presented as "prefill FLOPs" without the qualifier in tables.** Body text correctly calls 2NL the parameterized-linear FLOP floor excluding the quadratic attention term (+17% at 9.2K, +60% at 32K, ~2.4x at 128K per Ch.8/22). Tables 2-1, 8-1, 22-1 label the row "Prefill FLOPs (2x params x tokens)" with the exclusion buried in a footnote or a later paragraph. A reader copying the table will under-size long-context prefill. Fix: rename every such row "Prefill parameterized-linear floor (excl. attention term)" and add the attention-term column or pointer.

**P0-3. Decode 5.6 TB/s vs 3.35 TB/s comparison is aggregate-vs-device.** The book knows this (Ch.2/6 state the sharded reading: ~0.70 TB/s per GPU vs 3.35, plus comms; the invariant reason is intensity ~1 FLOP/byte << ridge 295). But Table 2-1 and Table 6-1 still place "5.6 TB/s demand" next to "3.35 TB/s H100 capacity" in adjacent columns, which visually asserts a per-device shortfall the text then retracts. Fix: split the row into "aggregate model-wide weight-read rate (illustrative)" and "per-GPU shard rate under TP8" or remove the adjacent-column layout.

**P0-4. Ch.24's 4xH100 vs 8xH100 candidate pair is incoherent with the fleet sizing.** §24.4.3 sizes peak prefill at 51.5 PFLOP/s, floor 6.5 hosts at 100% efficiency (~16.3 hosts at 40% MFU), then tables Candidate A as "4xH100 hosts" vs Candidate B as "8xH100 hosts." Neither 4 nor 8 satisfies the chapter's own 16-host realistic floor or the book's 20-host KV fleet. The section's valid point (size to peak/tail/failure-domain, not average) survives, but the specific candidates imply 8 hosts is defensible when the book elsewhere proves it is not. Fix: retable as 8 vs 20 hosts, or mark both as sub-fleet illustrative slices with explicit "not a fleet proposal" banner.

**P0-5. Ch.18 latency arithmetic violates the book's own SLO discipline.** §18.4.4 averages per-model latencies (247 ms/request) while §18.5 correctly warns percentiles are not linearly composable. The mini-case then routes 80% of traffic to a ~600 ms Tier-1 against a 500 ms SLA and claims 82% savings before admitting the violation. The admission is honest but the structure teaches "claim savings, then check SLO" backwards. Fix: gate first (drop or reshape Tier-1), then price the SLO-compliant fleet.

**P0-6. FP8 vs 8-bit KV nomenclature drift.** The book uses three distinct constants: nominal byte-halving 1.31 MB/token (1.25 MiB), measured FP8 serving 1.42 MB/token (54% of BF16, [S6]), and shorthand "~1.3 MB/token." Most chapters distinguish them; Ch.3 Table 3-1, Ch.5 §3, and Ch.12 §3 each collapse to "~12GB" without stating which constant. Fix: global replace — always write "1.31 nominal / 1.42 measured" on first use per chapter.

**P1-1. MoE residency numbers refer to different MoEs.** Ch.3's ~47B/14B-active/94GB-resident Mixtral-class variant vs Ch.18's 70B-MoE 140GB rows vs App.A's 125B/6B and 2.8T/104B frontier MoEs. Each is internally correct; placed together they look contradictory. Fix: add a one-line header to every MoE table: "which MoE (total/active)."

**P1-2. TCO cloud-elasticity assumption understates the hard problem.** Ch.16 prices cloud at ~5-host average (~$72K/mo) bursting to 20, with an explicit integral formula and warm-pool caveats. This is labeled [ILLUSTRATIVE] but still anchors the "$2.8/1K beats $5.7/1K" headline. If scale-up latency + 140GB model load + reservation dominate, the cloud bill approaches always-on-at-peak (~$288K/mo) and the headline flips. Fix: carry two cloud columns (elastic-ideal vs always-on-at-peak) instead of one.

**P1-3. "Prefill is compute-bound / decode is bandwidth-bound" survives in headings and glossary as unconditional.** Body text qualifies correctly (canonical long-prompt low-batch operating point; ridge-dependent). Headings (§2.4, §8.4.4), glossary entries for prefill/decode, and several figure captions do not. Fix: append "at the canonical operating point" to every heading/caption/glossary definition.

## 3. STORYLINE / VALUE-BASED REVIEW

The intended spine TOKEN -> WORKLOAD -> SYSTEM -> ARCHITECTURE -> FLEET -> DECISION is visible and mostly honored. Specific verdicts:

* **Ch.1 (Token).** Earns place. Fixes the unit. Keep.
* **Ch.2 (Prefill/decode + resource model + causal chain).** Earns place; is the armature. The vocabulary table and 7-resource table are the book's best synthesis pages. Keep, but trim the 1.19-vs-0.989 single-H100 capacity illustration to one paragraph — it currently occupies two pages to prove what one sentence proves.
* **Ch.3 (Model).** Earns place. Total-vs-active and compute-vs-memory sparsity are load-bearing. The 2026-baseline-shift subsection (§3.7.1) is 4 pages of forward pointer that repeats App.A. Cut to 1 page + pointer.
* **Ch.4 (Workload).** Earns place. Is the single reference set. Tables 4-1/4-2 duplicate each other; merge. The dual-W (10s planning vs 8.6s exec) and active-users vs in-flight-requests tables are exemplary — keep verbatim as the book's terminology anchor.
* **Ch.5 (Model selection).** Mixed. Embedding-leg (§3a) and Q* parametric framing earn place. The 50 tok/s per-dollar economics (§3b) is a method illustration that now confuses because Ch.8/15 supersede the rate by 100-1000x. Keep the method, replace the rate with a pointer to Ch.15/17 measured-goodput basis, or delete the $/token rows.
* **Ch.6 (Metrics).** Earns place. Distribution-not-mean + goodput + regime-from-telemetry is essential. Keep.
* **Ch.7 (Memory).** Earns place. Is the KV bible. Figs.7.4/7.5 duplicate the same 140+64+436 decomposition; merge into one.
* **Ch.8 (Compute).** Earns place. Roofline + MFU + scope discipline are essential. The 5-host/20-host prefill-throughput fleet cross-check is valuable — keep, but label idealized-aggregate on every appearance, not just first.
* **Ch.9 (Communication).** Earns place but overlong for an inference handbook. The training all-reduce worked example (140GB ring, 0.27s/6.1s/98s) is correct and well-scoped as lower bound, but its relevance to inference is one paragraph (§9 mini-case: TP exchanges activations, not weights). Cut Options B/C derivation to half page, keep the inference naming paragraph.
* **Ch.10 (Parallelism).** Earns place. Training-vs-inference DP framing + Table 10-1 are excellent. Keep.
* **Ch.11 (Serving).** Earns place. Continuous batching / PagedAttention / prefix-cache / P/D is the book's most decision-relevant mechanism inventory. The engine-capability table is correctly labeled time-sensitive — keep with date stamp.
* **Ch.12 (Candidates).** Weak as a standalone chapter. It re-derives Ch.8 throughput gates to reject its own candidates (a fails throughput, b fails throughput at one host, c fails quality). The synthesis method (constrain->synthesize->measure->decide) is real, but the chapter's value is the method + Table 12-1, not three worked candidates that all fail. Shorten to method + table + handoff; move throughput arithmetic back to Ch.8 by reference.
* **Ch.13 (Tiers).** Overlaps Ch.12's escalation logic and Ch.17's fleet sizing. Keep the ladder (it is the only tier vocabulary) but delete the "placing the canonical workload" worked example — it repeats Ch.11/17 conclusions.
* **Ch.14 (Benchmarking).** Earns place. Screen-vs-select + sweep-don't-test-a-point are essential professional practice. Keep.
* **Ch.15 (Performance).** Earns place as the optimization map + FlashAttention/speculative/chunked mechanisms. Table 15-1's MFU 12/38/52% regime labels are [ILLUSTRATIVE] teaching shape — keep only with that banner on the table itself, not just the caption.
* **Ch.16 (TCO).** Earns place. Fleet-first-then-price + break-even-region-not-point are the correct durable forms. Keep the sensitivity-dimensions list verbatim.
* **Ch.17 (Fleet).** Earns place. Is the book's sizing core (C=Mkv/(I*kappa), H=ceil(λW/(C*u)), subsystems table, counter-scenarios A/B). Keep in full; consider making §17.4 the normative sizing reference all other chapters cite instead of re-deriving.
* **Ch.18 (Multi-model).** Lowest value-per-page. Routing-by-requests (not tokens) and basis-reconciliation notes are correct and worth one page. The rest (VRAM table with duplicate 70B 8-bit rows, Q4-2026 $/1M table, 1,000-req/hr $12.59/hr arithmetic, three-tier GGUF mini-case that violates its own SLA) is vendor-catalog + worked arithmetic that does not transfer beyond the example. Recommendation: compress to routing method + consolidation-vs-separation rule + one table; move the rest to appendix or delete.
* **Ch.19 (Agents).** Earns place. α(T)/β(T)/Lbase+T·Lagent separation and incremental-orchestration (~660ms at T=3) vs full-service-time (~13.8s at T=3) scope note are the book's hardest-won clarity. Figs.19.2/19.3 duplicate the same 24.9->34.0GB growth; keep one quantified chart + one mechanism schematic, not two bar charts. Table 19-1 split across pp.210-211 is a layout defect — repaginate as one landscape table.
* **Ch.20 (Fleet optimization).** Overlaps Ch.17 heavily (same 2.0 req/s, same 20-host, same Little's law). Its unique value is scheduler-added vs end-to-end latency separation + infeasible-100ms-SLO rejection. Keep those two pages; delete the rest as pointer to Ch.17.
* **Ch.21 (Factory).** Earns place. Gated-vs-ungated blast-radius (216K vs 3.6K) is concrete and transfers. Keep.
* **Ch.22 (Architect's loop).** Redundant by design — it restates Ch.1-2 + Table 22-1. As the Part VI opener this is defensible, but it should be 6 pages, not 9. Cut the prefill/decode re-derivation; keep the loop + Table 22-1 + Fig.22.1 (redesigned).
* **Ch.23 (Customers).** Earns place. Socratic funnel + mirror test + six-questions table transfer to practice. Keep.
* **Ch.24 (Red/Green).** Does not earn place in current form. PIES (author-defined NLE≤0.25 count, 768->217) and uniform-retrieval poisoning baseline (52 hits) are explicitly toy/null-model metrics the text itself disqualifies as non-portable. The architecture-that-fails §24.4.3 is valuable but contradicts the fleet sizing (see P0-4). Recommendation: keep §24.4.3 (fixed) + guardrail/tool-sandbox consequences as a 6-page adversarial-design chapter; delete PIES/poisoning toy arithmetic or move to a boxed "how not to count attack surface" sidebar.
* **Ch.25 (ADR).** Earns place. Copy-ready template + FP16-vs-BF16 worked ADR are reusable artifacts. Keep.
* **Ch.26 (Toolkit).** Mixed. Workload-to-strategy matrix (§2.1) + fingerprint Fig.26.1 earn place as the generalization beyond the canonical. Capstone (§26.3-26.9) replays Ch.17 numbers at ~2 rps with a stricter 800ms TTFT that is never reconciled with the canonical p95≤2s. Keep matrix + measurement table; cut or clearly quarantine capstone as a separate TTFT-leg scenario.
* **App.A (Frontier).** Earns place as dated snapshot with hard 2026-08-30 boundary, Observed/Interpretation/Hypothesis mapping, and per-model-own-baseline Fig.A.2 discipline. The Ornith post-snapshot sidebar violates the hard boundary it just declared — either delete or move outside the appendix with a distinct date banner. Keep otherwise.

Part-to-Part transitions: I->II (token to workload quantification) and III->IV (substrate to candidates) are clean. IV->V (candidates to fleet) is abrupt because Ch.12's candidates all fail and Ch.17 restarts sizing from scratch — add a one-paragraph handoff: "candidates (a)/(b) fail throughput at one host; fleet sizing (Ch.17) is the throughput answer." V->VI (fleet to architect) works via Ch.21 factory gate.

## 4. NUMERICAL / TERMINOLOGY / EVIDENCE AUDIT

### CROSS-CHAPTER CONSISTENCY LEDGER

| Quantity | Canonical value | Appears in | Consistency |
|---|---|---|---|
| Params total | 70B dense | Ch.1-8,10-17,19-22,25 | CONSISTENT. MoE variants explicitly labeled as variants (47B/14B Ch.3; 125B/6B, 2.8T/104B App.A). Ch.18 "70B MoE 140GB" rows ambiguous — flag, see P1-1. |
| Active/token | 70B (dense = total) | Ch.3 Table 3.1/3.2, Ch.8, App.A | CONSISTENT. MoE 14B (~30%) Ch.3; frontier single-digit % App.A. No drift. |
| Precision weights | FP16 2B/param | All | CONSISTENT. BF16 ADR Ch.25 correctly notes same 2B footprint. |
| Weight footprint | 140GB | Ch.2,3,4,5,7,8,10,11,16,17,22 | CONSISTENT. 70Bx2B recomputed correctly everywhere checked. |
| Input/context | 9,200 (1,200+8,000) | Ch.1,2,4,5,7,8,11,14,15,17,19,22 | CONSISTENT. |
| Output | 300 | Same as above | CONSISTENT. |
| KV/token FP16 MHA | 2.62MB (2,621,440B; ~2.5 MiB shorthand) | Ch.1,3,4,5,7,15,17,19,22,25 | CONSISTENT, with explicit 8-bit/FP8 separation in Ch.7/17. Shorthand "~2.5" always footnoted as MiB. |
| KV/token 8-bit nominal | 1.31MB (1,310,720B) | Ch.1,3,7,22, App.A | CONSISTENT where stated; collapsed to "~1.3" without nominal/measured tag in Ch.3 Table 3-1, Ch.5, Ch.12 — FLAG (P0-6). |
| KV/token FP8 measured | 1.42MB (54% BF16, [S6]) | Ch.3,4,7,11,15,17,19 | CONSISTENT as operating FP8 value. Correctly distinguished from 1.31 nominal in Ch.7/17; not in Ch.3/5/12. |
| KV/request 9.2K init | 24.1GB | Ch.4,5,7,11 | CONSISTENT. |
| KV/request 9.5K max | 24.9GB | Ch.7,15,17,19,22 | CONSISTENT. |
| Runtime/workspace | ~64GB | Ch.7,15,17 | CONSISTENT. (Ch.25 ADR cites ~30GB per-request working set as distinct quantity — correctly scoped, not a contradiction.) |
| HBM per GPU / per host | 80GB / 640GB aggregate | Ch.2,4,7,8,10,17 | CONSISTENT. Aggregate-feasibility caveat stated in Ch.7 Figs.7.4/7.5 + Ch.9/10. |
| Per-host KV budget | ~436GB (640-140-64) | Ch.7,15,17 | CONSISTENT. Distinct from Ch.4/7 ~500GB single-request headroom (640-140) — book states the difference explicitly; retain both with labels. |
| FLOPs/token | ~140 GFLOP (2x70B) | Ch.2,3,8,15,22 | CONSISTENT. |
| Prefill/req linear floor | 1.29 PFLOP | Ch.2,6,8,11,22,24 | CONSISTENT arithmetically; LABEL inconsistent (see P0-2). Attention term +17% at 9.2K stated in Ch.8/22 only. |
| H100 BF16 dense peak | 0.989 PFLOPS | Ch.2,4,6,8,15 | CONSISTENT. Sparsity-inclusive 1.979 explicitly excluded everywhere. |
| H100 HBM peak | 3.35 TB/s | Ch.2,6,8 | CONSISTENT. |
| Ridge FP16 | ~295 FLOP/byte | Ch.2,6,8 | CONSISTENT (989/3.35). H200 206, FP8 412 also consistent. |
| Arithmetic intensity prefill | ~9,200 FLOP/byte | Ch.2,6,8 | CONSISTENT. |
| Intensity decode b=1 | ~1.0 FLOP/byte | Ch.2,6,8 | CONSISTENT. |
| TTFT SLO | 1.2s (120ms retr + 1.08s prefill); p95 ≤2s | Ch.4 (authority), Ch.2,5,6,11,14 | CONSISTENT except Ch.26 capstone 800ms p99 TTFT stricter — FLAG as deliberate harder tail target (book does label it, but the label is one sentence; promote to table banner). |
| TPOT/ITL | 25 ms/tok; p95 ≤35ms | Same | CONSISTENT. Glossary equates TPOT/ITL with scheduling-gap note — acceptable. |
| Service time exec | Wexec ~8.6s (1.08+7.5) | Ch.4,8,15,17,19,20 | CONSISTENT. |
| Planning round | Wplan ~10s | Ch.4,17 | CONSISTENT, explicitly dual-named. No numeric contradiction. |
| Concurrency users | 100 avg (5%), 400 peak (20%) | Ch.4,15,17 | CONSISTENT as active-user population. |
| In-flight requests | ~86 avg, ~344 peak (λW, W=8.6) | Ch.4,15,17,20 | CONSISTENT. |
| Request rate λ | 10 rps avg / 40 rps peak | All | CONSISTENT. Peak defined as sustained provisioning burst — explicit. |
| Throughput/host | ~2.0 req/s (C/W=17.5/8.6) | Ch.8,14,16,17,20 | CONSISTENT as analytical planning bound. Labeled as such in Ch.17/20; labeled loosely as "throughput" in Ch.4 mini-case — fix label. |
| Prefill tput/host idealized | ~19,800 tok/s (8x2,471 at 35% MFU) | Ch.8,12 | CONSISTENT, scoped as idealized aggregate. |
| Host count | 5 avg / 20 peak (29 at 70%) | Ch.4,8,16,17,20 | CONSISTENT. FP8 ~11 (15 at 70%) consistent. |
| Utilization/headroom | 70% target; ρ 0.85-0.98 LB | Ch.16,17,20 | CONSISTENT. |
| TCO | self ~$148K/mo $5.7/1K; cloud ~$72K $2.8/1K; API ~$541K $20.8/1K; capex $350K/5yr; $20/hr; $2.50/GPU-hr | Ch.16 (authority) | INTERNALLY CONSISTENT. External plausibility of $2,500/mo reserved (-83%) in Ch.4 and $0.002/$0.008 API in Ch.16 not verified — both labeled [ILLUSTRATIVE], acceptable. Cloud-elasticity caveat required (P1-2). |
| Reliability | N-1, 99.9%, 5-15s failover | Ch.4,17 | CONSISTENT but thin — no quantitative N-1 fleet table; add. |
| Agentic δ/γ | 800 + 65 = 865/turn; T cap 3 (4 bounding); α 1.09/1.18/1.27/1.36; Lagent 220ms; Lbase 8.6s; W T=3 ~13.8s lower bound | Ch.17,19 | CONSISTENT. Turn distribution 68/25/5/2 consistent between Ch.17/19. Median T=1 / p90 T=2 / p95 T=3 consistent. |

**Terminology drift (global).** Host vs node vs GPU node: used interchangeably for 8xH100 unit — freeze "host = 8xH100 unit; GPU/rank = one H100." QPS vs RPS: Ch.4 uses both for same λ — freeze RPS. Active vs concurrent user vs in-flight request: Ch.4 fixes definitions; Ch.15 Table 15-1 header "KV-Cache/User" should read "KV-Cache/Request." Prefill vs prompt processing, decode vs detokenization: Ch.1/2 fix correctly. Throughput vs goodput: Ch.6 fixes; Ch.5/15 occasionally write "throughput" for goodput — fix. TPOT vs ITL: glossary equates with caveat — acceptable. KV vs prefix vs prompt cache: Ch.2 table fixes — keep. GB vs GiB: Ch.4/7 state SI decimal + MiB parenthetical — acceptable, but enforce on every KV table. Measured vs derived vs illustrative vs vendor-reported: taxonomy applied; Ch.15 mini-case 8,000->70,000 tok/s and Ch.18 $/1M tables are the two places where [ILLUSTRATIVE SCENARIO RESULT] appears mid-paragraph rather than in the table header — promote to header.

**Evidence.** Citation keys S1-S6 resolve (References pp.290-292). S5 (DFlash 2026) and S6 (vLLM FP8 blog 2026) are future-dated relative to knowledge cutoff but treated as in-universe first-party claims with re-measure caveats — acceptable within the book's fiction, provided the date stamp stays. App.A arXiv IDs (2606.19348, 2607.24653, 2602.15763) are in-universe; retain with verify-on-hardware caveat already present. No URL was click-verified in this audit; pre-publication, re-open every App.A HF/arXiv link.

## 5. FIGURE-BY-FIGURE VISUAL AUDIT

**FIGURE 1 — Decision loop (p.vii) — KEEP.** Page: vii. Purpose: book spine. Clean vertical loop, large type, red iterate leg legible at print size.

**FIGURE 2 — Two ways to read (p.viii) — KEEP.** Clear A/B columns. Small red triangles decorative but harmless.

**FIGURE 1.1 — KV cache (p.6) — POLISH.** Purpose: every decode appends K/V. First glance: pale, tiny. Defects: essential labels ("token, first decoded", "append", "KV cache K/V per layer x head") at ~6pt, low-contrast grey on white; thin arrows; figure occupies <50% page width while type is minimal. Semantic risk: none — concept correct. Action: rebuild at full text width, 9pt minimum, darken arrows, remove one redundant token box.

**FIGURE 1.2 — Token travels (p.7) — POLISH.** Purpose: text->IDs->embedding->attention->KV pipeline. Readable at print size but "split/emit/lookup/attend/append" edge labels butt against box borders; "ID to d-dim vector one vec/token" wraps awkwardly. Action: increase box padding, move edge verbs outside arrows, enlarge to 90% width.

**FIGURE 2.1 — End-to-end pipeline (p.14) — KEEP.** Three bands (prefill / persistent KV / decode) with populate/read/initialize/loop legs. Hierarchy clear, entry at PREFILL, reading order top->middle->bottom. Type small but comfortable. No collision. Keep as canonical figure; reuse its geometry for Fig.11.3 instead of redrawing.

**FIGURE 2.2 — Roofline regimes (p.19) — KEEP.** Purpose: decode ~1 vs prefill ~9.2K split by ~295 ridge. Exemplary: large axis labels, hatched regions redundant with color, single-purpose. Keep.

**FIGURE 3.1 — Dense vs MoE (p.36) — KEEP.** Purpose: ALL-active vs top-2-active, KV identical. Immediate: blue vs orange, E1/E4 highlighted. Grayscale: shade + label redundant. Keep.

**FIGURE 4.1 — Six dimensions -> decisions (p.52) — KEEP.** Six blue->orange arrows. One job, aligned baselines, large type. Caption correctly hedges deterministic mapping. Keep.

**FIGURE 5.1 — Model selection (p.66) — KEEP.** Workload->surfaces->two legs->decision. Clean funnel. Keep.

**FIGURE 6.1 — Metric hierarchy (p.69) — POLISH.** Purpose: causation down / diagnosis up across workload/resource/serving. Defect: three identical green boxes give equal weight to three layers; red dashed diagnosis leg visually weaker than green causation leg despite being the chapter's point; bottom caption line ("causation ↓ | diagnosis ↑") duplicates arrows at ~7pt. Action: thicken diagnosis leg, enlarge bottom legend, add layer numbers.

**FIGURE 6.2 — Latency distribution (p.71) — MAJOR REVISION.** Purpose: mean hides tail; even p99 hides 1% 5s stragglers. Defects: p50/p90/p95 green leader lines overlap into one smear; "mean=0.85s p99=1.33s SLO 2s (p99 still looks fine)" box at ~6pt grey on white; pink 1%-straggler wash extends to 6s while histogram body occupies 0.5-1.1s (95% whitespace); x-axis to 6s compresses the body. Semantic risk: reader cannot see the p50/p90/p95 separation the text argues. Action: redesign as two panels — (a) zoomed body 0-2s with distinct p-lines, (b) log-y tail to 6s with outlier-fraction callout; remove 3D leader-line tangle.

**FIGURE 7.1 — GQA (p.81) — KEEP.** 8 query heads -> 1 K/V head x8 groups. Single geometry, immediate. Keep.

**FIGURE 7.2 — KV vs context (p.87) — MAJOR REVISION.** Purpose: full-MHA vs GQA, FP16/FP8/8-bit scaling; parameter count ≠ KV. Defects: four log-log lines + two horizontal ceilings + two diagonal callouts ("9.2K=24GB", "9.2K≈3GB 8x saving") that cross the lines they annotate; legend at ~6pt; title is a paragraph. Grayscale: four colors collapse to similar greys (line style is the only cue — acceptable but thin). Action: split legend outside axes, reroute callouts outside data area, shorten title, thicken lines.

**FIGURE 7.3 — Inference vs fine-tune floor (p.88) — POLISH.** 165GB vs 1120GB vs 60GB bars. Defect: dashed ceiling legend (2xH100/8xH100/1xH100) at ~6pt overlapping the 1120GB bar's red annotation; x-labels "(weights+KV)(weights+grad+opt)(weights+adapters)" wrap to 3 lines. Action: move legend below, shorten x-labels, keep bars.

**FIGURE 7.4 — Concurrency budget (p.89) — MAJOR REVISION.** Purpose: 140+64+436=640 pool; 436/24.9=17.5->17. Defects: white text on hatched blue/green bars at ~7pt fails print-size legibility and grayscale (white-on-light-green vanishes when desaturated); "~436GB KV budget" label centered on a 60%-width bar is the essential number yet lowest contrast. Action: redesign as horizontal stacked bar with outside labels + large "≈17 requests" equation below (already present — promote it); remove pattern fills or darken.

**FIGURE 7.5 — Memory Tetris (p.90) — POLISH.** Three stacked bars (9.5K/32K/128K). Better than 7.4 (outside red KV labels, 80GB rank rules). Defect: light horizontal gridlines nearly invisible; "=229/288/539GB used" at ~7pt. Action: darken grid, enlarge totals. Otherwise keep — this is the figure to keep over 7.4 if merging.

**FIGURE 8.1 — Compute/data ladder (p.94) — POLISH.** Registers->other-GPUs hierarchy. Defect: white text on dark blue/orange/green at ~7-8pt; "tensor cores/ALU arithmetic units" line breaks mid-phrase; red double-arrow annotation ("capacity grows speed drops distance grows") collides with box edges. Action: increase box height/padding, left-align "what runs here" column, move red arrow outside.

**FIGURE 8.2 — Per-GPU roofline H100 vs H200 (p.99) — POLISH.** Rich but busy: two curves + two ridges (295/206) + decode-batch points + prefill 9.2K dot + three text colors. At print size the "decode batch=1" label and ridge values require close reading. Action: enlarge ridge labels, de-emphasize H200 dashed curve (grey), keep H100 solid as focus. Classification correct (per-GPU scope banner present — exemplary).

**FIGURE 9.1 — All-reduce vs volume (p.107) — KEEP.** Log-log, four tiers, 140GB marker, in-figure ANALYTICAL banner. Immediate. Keep.

**FIGURE 10.1 — TP/PP/DP (p.115) — POLISH.** Three panels with consistent color grammar (blue weights / orange GPU / green data / red comms — stated). Defect: red "all-reduce partial sums -> full output" and "gradients <-> all-reduce (training only)" at ~6.5pt; panel A arrow from W0/W1 to GPUs thin. Action: enlarge red annotations to 8pt, thicken arrows. Structure is right — do not redesign.

**FIGURE 11.1 — Discrete vs continuous batching (p.124) — KEEP.** Pink idle bubbles vs green backfill. Geometry encodes the argument (idle vs fed). Keep. Best serving figure in the book.

**FIGURE 11.2 — Four orthogonal concerns (p.127) — REDESIGN.** Purpose: scheduling/state/reuse/specialisation act in parallel, not stacked. As rendered: title + one blue bar + four pastel boxes in 2x2 + one grey bar, occupying 40% of page with 60% whitespace, 10-word labels centered in large boxes. This is a slide shrunk onto a page; geometry encodes nothing (2x2 position meaningless, central arrow implies a stack the caption denies). Action: redesign as four parallel lanes acting on a horizontal request-stream arrow (pipeline-parallel layout), each lane labeled with its trade (latency<->util, capacity->concurrency, FLOPs saved, regime->pool). Halve whitespace.

**FIGURE 11.3 — P/D topology (p.128) — POLISH.** Prefill pool -> KV transfer -> decode pool. Correct and minimal. Defect: two huge boxes with 8 small squares each waste vertical space; "prompt/tokens" arrows tiny. Action: shrink boxes 30%, enlarge arrow labels. Consider reusing Fig.2.1's band geometry for continuity.

**FIGURE 12.1 — Candidate synthesis (p.140) — KEEP.** Requirements->constraints->candidates->survivors/rejected. Clean, large type. The (c)-rejected verdict matches Table 12-1. Keep.

**FIGURE 13.1 — Escalation ladder (p.146) — MAJOR REVISION.** Purpose: single-GPU->host->multi-host->cluster with force-scale-up triggers and de-escalate leg. Defects: red trigger labels ("KV residency overruns -> forces scale-up", "host goodput < demand -> forces scale-up") run through the red up-arrow shaft; tier boxes at ~7pt with "constraints -> STOP" microcopy illegible; green de-escalate dashed leg visually disconnected. Action: move trigger labels outside arrow, enlarge tier boxes to full width, left-align STOP conditions.

**FIGURE 14.1 — Screen then benchmark (p.152) — KEEP.** Candidate->survivors->selection with screen/benchmark/gate legs. Simple, correct. Keep.

**FIGURE 15.1 — FlashAttention (p.158) — KEEP.** Before (many HBM round-trips, O(L²) traffic) vs after (few, O(L)). I/O story immediate, footer correctly states same math. Keep as model for mechanism figures.

**FIGURE 15.2 — Prefix vs batching (p.160) — POLISH.** Two panels showing independent effects (caching cuts prefill work; batching raises decode goodput). Correct separation. Defects: y-axes (Prefill FLOPs % vs Relative goodput) at ~7pt; red "[ILLUSTRATIVE]" tags tiny; vertical dashed "b16" line unexplained in-figure. Action: enlarge axes, explain b16 in-figure, keep two-panel structure.

**FIGURE 16.1 — TCO break-even (p.174) — POLISH.** Log-log cost/mo vs req/mo, 7.1M break-even, 5.9-9.9M sensitivity band, canonical 26M marker. Quantitatively honest (band, not point). Defect: footnote assumptions at ~6pt grey; dotted sensitivity envelope hard to see in grayscale. Action: enlarge footnote, use line-style (not just color) for self-host/cloud/managed.

**FIGURE 17.1 — Fleet by burst/headroom/failover (p.177) — KEEP.** Offered-load hump vs N=4 capacity vs N-1 residual vs one-host bound. Exemplary sizing figure. Keep.

**FIGURE 18.1 — Routing tree (p.197) — POLISH.** Capability->cost/SLO->fallthrough with specialist/general leaves. Defect: "only ONE model is selected per request" footnote at ~6pt; green down-arrows thin. Action: enlarge footnote, thicken decision arrows. Structure correct.

**FIGURE 19.1 — Agent loop (p.201) — KEEP.** Plan->Execute->Observe->Decide with Final/Stopped terminals. Clear state machine, loop-back dashed. Keep.

**FIGURE 19.2 — Token/KV growth (p.206) — MAJOR REVISION.** Purpose: quantify 24.9->34.0GB across turns. As rendered: two ~2-inch bar panels with y-axes at ~6pt, hatched fills obscuring values, red "27.2/29.4/31.7/34.0" labels colliding with bar tops. At print size neither panel is comfortably readable. Action: rebuild as one table-chart hybrid or enlarge to full width with outside data labels; remove hatching.

**FIGURE 19.3 — Context block (p.207) — REDESIGN.** Purpose: mechanism of accumulation (I0 + O + δ + γ per turn). Defects: P0 publication defect — title/legend line ("Initial prompt I0... generated reasoning") overprints the chart title; bar-internal labels ("I0(Irl)", "O", "δ", "γ") at ~5-6pt white on hatch, largely indecipherable without zoom; KV 24.9/27.2/29.4/31.7/34.0 red labels collide. The figure's mechanism duplicates Fig.19.2's quantification without adding topology. Action: redesign from scratch as a single horizontal accumulation strip (one row per turn, blocks appended left-to-right with δ/γ color + pattern redundant cue), full width, 9pt labels outside blocks. Do not merely enlarge.

**FIGURE 20.1 — Analytical bound vs measured (p.221) — POLISH.** Top: ceiling line; bottom: measured plateau at 40 rps. Correct bound-vs-reality separation. Defect: top panel's "canonical peak load=40 rps" blue dashed line label at ~7pt; bottom "~20 hosts -> reaches 40 rps" callout thin. Action: enlarge callouts. Keep structure.

**FIGURE 21.1 — Factory promotion (p.226) — POLISH.** Data->Train->Eval->Canary->Observe->Promote->Serve with PASS gates + FAIL rollback + production feedback. Dense but complete; type ~7pt throughout. Action: enlarge gate labels one point, keep layout.

**FIGURE 22.1 — Prefill vs decode scaling (p.233) — MAJOR REVISION.** Purpose: left per-request (linear 2NL + quadratic 4nL²d -> quadratic dominates ≥32K) vs right per-token (flat 2N). Defects: red banner "LEFT: PER REQUEST | RIGHT: PER GENERATED TOKEN" is a caption compensating for a design flaw (two panels with different units share no y-axis yet sit side-by-side inviting comparison); left panel's three lines (linear/quadratic/total) + purple "quadratic dominates beyond ~32K" curve-label collides with data; y-axis "Compute (PFLOP; see series definition)" generic; right panel is a flat line conveying one number. Semantic risk: HIGH — visual implies comparable quantities. Action: keep two panels but give each its own prominent unit subtitle, remove banner, move "quadratic dominates" outside axes, consider replacing right panel with a one-line table (flat 140 GFLOP/token) since a chart of a constant adds nothing.

**FIGURE 23.1 — Vague ask to bounds (p.242) — REDESIGN.** Five orange question boxes + green quantified-bounds box, centered column with 50% whitespace. Every box contains a full sentence; geometry encodes sequence only. This is box-and-arrow prose — the same information is fully contained in Table 23-1. Action: either remove (table suffices) or redesign so position encodes something prose cannot (e.g., funnel width = uncertainty reduction per gate, with the six Table 23-1 numbers as output meters).

**FIGURE 24.1 — Red/Green cycle (p.254) — POLISH.** Six boxes 1-6 with feedback leg. Defect: large empty center; "loop: findings -> next cycle" red footer duplicates the drawn loop. Action: tighten layout 30%, enlarge step numbers. Do not redesign structure.

**FIGURE 25.1 — ADR anatomy (p.262) — KEEP.** Context->Options->Decision->Rationale->Consequences with "consequences become next context" dashed return. Single causal idea, immediate. Keep.

**FIGURE 26.1 — Workload fingerprints (p.268) — POLISH.** Grouped bars (not radar — good) with hatch + color redundant encoding (good for grayscale). Defects: y to 1.4 for 0-1 normalized intensity (wasted headroom); legend at top ~7pt; x-labels ("Context length Traffic (rps) Quality required...") wrap. Action: set y 0-1.0, enlarge legend, keep grouped-bar choice.

**FIGURE 26.2 — Pattern loop (p.273) — KEEP.** FACT->DERIVED->PATTERN with trace/validate/adjust legs on capstone numbers. Clear, correctly scoped to TTFT. Keep.

**FIGURE A.1 — Frontier sparsity (p.276) — KEEP.** Four orange bars, % active + total/active labels, vendor-reported banner. Immediate. Keep.

**FIGURE A.2 — KV/FLOP reduction (p.281) — KEEP.** One row per model family with own baseline + 100%->X% (no shared scale). Exemplary anti-misleading design; the red "no shared scale" banner is the rare banner that earns its space. Keep as template for all comparison figures.

**FIGURE A.3 — System layering (p.284) — KEEP.** Efficiency-led (dashed) vs capability-led (solid) vs fleet (thick) with ~era markers disclaimed as loose signals. Keep.

**FIGURE A.4 — Where intelligence lives (p.285) — KEEP.** Eight placement rungs with chapter pointers. Clean ladder; vertical axis labeled as WHERE. Keep.

## 6. CROSS-FIGURE SYSTEMIC ISSUES

1. **Slide-shrunk-onto-page.** Figs.11.2, 23.1 (and to a lesser degree 11.3, 24.1) use large rounded boxes, centered short labels, and 40-60% whitespace — presentation composition at book width. Result: tiny type inside oversized containers. Rule: no figure shall occupy <60% text width while using <9pt type.
2. **White-on-pattern microtype.** Figs.7.4, 8.1, 19.2, 19.3 place 6-7pt white labels on hatched/color fills that vanish in grayscale and at print distance. Rule: essential numbers go outside patterned areas at ≥9pt.
3. **Caption-compensated weak visuals.** Figs.6.2, 11.2, 22.1, 23.1 rely on long captions or banners ("LEFT: PER REQUEST...", "This is a worked-example interrogation sequence...") to explain what geometry should encode. Rule: if the caption must reconstruct the figure, redesign the figure.
4. **Aggregate-pool drawings without rank cues.** Figs.7.4/7.5 draw 640GB as one bar. The text caveat is present but the visual asserts fungibility. Fig.7.5's "(light rules = 80GB rank boundaries)" is a good start — promote rank boundaries to a first-class visual in both.
5. **Inconsistent comparison grammar.** Fig.A.2 (per-model baselines, no shared scale) is exemplary; Figs.7.2/7.3/15.2 compare different units/baselines on shared axes without the same banner discipline. Apply A.2's banner rule book-wide.
6. **Duplicate decompositions.** 7.4 vs 7.5 (same 140+64+436), 19.2 vs 19.3 (same 24.9->34.0), 2.1 vs 11.3 (same prefill->KV->decode topology). Merge each pair; the book loses nothing.
7. **Table density.** Tables 4-1, 7-1, 16-1, 19-1, 25-1 use ~7pt body with wrapped derivation cells that span pages (19-1 splits across a page turn). Repaginate: allow landscape for 19-1 and 17-1; set minimum 8pt for tables.

## 7. VISUAL REVISION PRIORITY

**P0 (publication defects — fix before any other work).**
* Fig.19.3 — title/legend overprint collision; indecipherable bar labels. REDESIGN.
* Fig.6.2 — p50/p90/p95 leader-line tangle; essential percentile separation invisible. MAJOR REVISION.
* Fig.7.4 — essential "~436GB / ~17 requests" illegible (white-on-light-pattern). MAJOR REVISION.
* Fig.22.1 — shared-axis invitation to compare incommensurable units; banner compensates. MAJOR REVISION.
* Table 19-1 — split across pp.210-211 mid-row. Repaginate.

**P1 (foundational mental models damaged by weak design).**
* Fig.11.2 (serving concerns) — REDESIGN as parallel lanes.
* Fig.13.1 (tier ladder) — MAJOR REVISION (labels through arrow).
* Fig.7.2 (KV scaling + "params ≠ KV" lesson) — MAJOR REVISION.
* Fig.19.2 (agentic KV growth → fleet argument) — MAJOR REVISION.
* Fig.2.1/11.3 continuity — unify geometry (POLISH on 11.3 toward 2.1).

**P2 (substantial comprehension/professionalism).**
Figs.1.1, 1.2, 2.1-scope, 6.1, 7.3, 7.5, 8.1, 8.2, 10.1, 11.3, 15.2, 16.1, 18.1, 20.1, 21.1, 24.1, 26.1 — all POLISH as specified above.

**P3 (optional polish).**
Figs.2.2, 3.1, 4.1, 5.1, 7.1, 9.1, 11.1, 12.1, 13-ladder-after-fix, 14.1, 15.1, 17.1, 19.1, 25.1, 26.2, A.1-A.4, Preface 1-2 — KEEP; no action beyond final proof pass.

## 8. TABLE / PAGE-COMPOSITION ISSUES

* **Widows/orphans and stranded headings.** Ch.3 §3.4.1 table header stranded at p.27 bottom; Ch.10 Table 10-1 splits header (p.116) from single continuation line (p.117) — merge or keep together. Ch.19 Table 19-1 splits across spread — force landscape single page.
* **Table 18-1 (p.191).** Duplicate "70B 8-bit GGUF" row (appears twice); "# fit on 8xH100" column mixes weights-only ("~2 GPUs hold weights") with pool-fit claims. Deduplicate rows; separate weight-residency from KV-inclusive fit.
* **Table 4-1 (pp.40-41).** "Dimension" column hyphenated to "Di-men-sion" across lines — source-level column-width defect; widen first column.
* **Figure/caption separation.** Figs.7.2 (p.87), 16.1 (p.174), 22.1 (p.233) captions run to 6-8 lines at ~7pt and detach from figures across page breaks in extraction; keep figure+caption on same page, shorten captions by moving sensitivity notes into body.
* **Equation breaking.** Ch.17 Hmin and Ch.19 α(3)/β(T) break across lines cleanly — no defect. Ch.8 n_hosts fraction renders correctly.
* **Running heads.** All sampled heads match chapter titles; no collisions with page numbers observed.
* **No PDF text-extraction artifacts mistaken for defects above.** Overprint (Fig.19.3 title), hyphenation ("Di-men-sion"), and wrapped table cells were confirmed on rendered pages, not inferred from extraction.

## 9. PRIORITIZED REVISION PLAN

Ordered by impact, not chapter number:

1. **Fix P0 visuals (Figs.19.3, 6.2, 7.4, 22.1 + Table 19-1 pagination).** Nothing else matters if rendered defects remain. (Design time, no new research.)
2. **Freeze canonical sentences and relabel three quantities book-wide.** One sentence for single-host latency-vs-capacity; rename "prefill FLOPs" to "parameterized-linear floor" in all tables; split 5.6-vs-3.35 into aggregate vs per-shard rows. (Half day, global replace + proof.)
3. **Repair Ch.24 candidate coherence and Ch.18 SLO gating.** Retable Ch.24 as 8 vs 20 hosts with measurement-contingent verdict; gate Ch.18 tiers before pricing. (One day + recheck Ch.16/17 cross-refs.)
4. **Compress redundancy.** Merge Tables 4-1/4-2; merge Figs.7.4/7.5 and 19.2/19.3 (keep one each); cut Ch.3 §3.7.1 to pointer, Ch.9 Options B/C to half page, Ch.12 to method+table, Ch.13 worked example to pointer, Ch.20 to scheduler-vs-end-to-end pages, Ch.22 to loop+table, Ch.24 PIES/poisoning to sidebar-or-delete, Ch.18 to routing method. Target: -25 to -35 pages with zero mechanism loss.
5. **Reconcile the four throughput rates in one new box.** Place in Ch.17 §4 or Ch.8 §4: 50 tok/s single-stream floor (Ch.5 method) vs 19,800 tok/s idealized prefill aggregate (Ch.8) vs 35-70k tok/s batched serving range (Ch.15, to be benchmarked) vs 2.0 req/s KV/service-time bound (Ch.17/20, the provisioning input). State which to use for TCO/fleet (the last, validated by Ch.14 benchmark).
6. **Carry two cloud TCO columns and an N-1 fleet row.** Elastic-ideal vs always-on-at-peak (Ch.16); add N-1 headroom hosts to Table 17-1. (Recompute 3 numbers.)
7. **P1/P2 figure polish pass** per §5 instructions. Batch by designer, not by chapter.
8. **Pre-publication verification sweep.** Re-open every App.A HF/arXiv link; re-price $2.50/GPU-hr, $0.002/$0.008 API, $350K server; confirm H100 989/3.35 and vLLM 54% FP8 against current vendor docs; record dates. The book's dated-snapshot discipline requires this pass to be visible (add "reverified YYYY-MM-DD" line to Sources chapter).

## 10. PUBLICATION ASSESSMENT

The manuscript is **not yet publication-ready**, despite strong and in places exemplary technical content. What prevents it:

* Five rendered-figure publication defects (§7 P0) — any one alone blocks publication under the stated standard.
* Three quantitative presentation defects that mislead by layout even though the text retracts them (2NL label, 5.6-vs-3.35 adjacency, Ch.24 4-vs-8 hosts).
* Two storyline defects where savings are claimed before SLO gating (Ch.18) or fleet math contradicts itself (Ch.24).
* Redundancy that degrades finish: ~30 pages of re-derivation and three duplicate figure pairs that make the book feel defensive rather than finished.
* Terminology seams (50 tok/s vs 35k tok/s vs 19.8k tok/s vs 2.0 req/s; 800ms vs 2s TTFT; 15GB vs 20GB candidate-c) that are each scoped locally but never reconciled globally.

None requires new research. All are fixed by relabeling, merging, redesigning listed figures, and one verification sweep. After that, the book will meet its own standard: every important number traceable from stated assumptions through equations to conclusions, with visual and prose finish to match.

### FINAL QUALITY GATES

A. Complete manuscript read (Preface through Worksheet, pp.v-297 + full text dump): **YES.**
B. Major numerical chains independently recomputed (1.29 PFLOP, 2.62MB/token, 24.1/24.9GB, 165GB, 436GB, 17.51, 344, 5/20/29 hosts, 295 ridge, 92K/368K tok/s, $148K/$72K/$541K TCO): **YES — arithmetic checks out; labels, not values, are the issue.**
C. Theoretical / derived / illustrative / vendor-reported / measured separated: **YES, with P0-6 and Ch.15/18 header exceptions noted.**
D. Canonical scenario cross-chapter consistency checked: **YES — ledger above; no value drift beyond flagged MoE/TCO/cloud-elasticity ambiguities.**
E. Every major section storyline-vetted: **YES — keep/cut/merge verdicts above.**
F. Every rendered figure inspected at print scale (pp.6-285): **YES — all numbered figures plus Preface 1-2.**
G. Every numbered figure explicitly reported including passes: **YES — §5 lists all 44.**
H. Every figure checked for collisions, microtype, hierarchy, arrow semantics, misleading visuals, caption dependence, grayscale: **YES.**
I. Existence test asked per figure ("what is lost if deleted"): **YES — remove/merge recommendations for 11.2, 23.1, 7.4/7.5, 19.2/19.3 pairs.**
J. Tables and page composition checked at rendered size: **YES — §8.**
K. Global terminology drift checked: **YES — §4.**
L. Plausible-but-unestablished conclusions challenged: **YES — §2 P0/P1 items.**
M. Correct-but-low-value sections identified: **YES — §3 (Ch.12/18/20/22/24 trims).**
N. Standard not lowered for prior improvement: **YES — P0 defects block publication regardless of prose quality.**
