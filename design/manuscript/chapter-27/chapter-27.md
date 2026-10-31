# Appendix A — 2026 Frontier Architecture Signals: Four Open-Weight Model Families

> **Snapshot: 2026-08-30 technical evidence snapshot, with a separately labeled September 27 addendum and October 28 technology notes.** The body of this handbook works through durable mechanisms — tokens, memory floors, rooflines, parallelism, KV arithmetic — that do not change. But the industry moves, and the whole point of an architecture handbook is to stay current. In 2026 the four frontier open-weight MoE families — DeepSeek-V4, Kimi K3, Qwen3.8-Flash-Next, and GLM-5.3-Flash — all shipped within a short window. Reading them together is not a product tour; it is a single, coherent signal about where the mechanisms in this book are heading. Every mechanism below maps back to a chapter and an architectural decision.

> **Appendix verified through 2026-08-30 (source snapshot compiled through 30 August 2026).** This appendix is a snapshot of the frontier as of that date, compiled from the first-party technical reports and model cards listed in A.10 (First-hand Sources). The models, their parameter counts, constants, and claims are vendor-reported and move quickly. **This is a hard boundary for the four-family comparison and the First-hand Sources list: nothing released after 2026-08-30 is reflected in either, and model specifications and vendor claims should be reverified against the cited first-party sources before any procurement or deployment decision — and once more immediately before publication, because these are among the fastest-changing values in the book.** (The 2026-09-27 observation in A.6 and the separately dated 2026-10-28 technology notes are outside this compile envelope and are not part of the four-family comparison.) It illustrates how to apply the framework to a changing frontier; it is **not** a current model leaderboard.

**The four families at a glance (the scope of this appendix).** The four-family comparison that this appendix's figures (Fig A.1, A.2) and its First-hand Sources list (A.10) rest on comprises **exactly these four open-weight frontier MoE families — and only these four**:

1. **DeepSeek-V4** (A.3) — DeepSeek; MIT; hybrid CSA+HCA attention; 1M-token context. (V4-Pro and V4-Flash are *variants within this one family*, not additional families.)
2. **Kimi K3** (A.4) — Moonshot; vendor-reported first open 3T-class; KDA + AttnRes; stable-LatentMoE activating 16 of 896 routed experts.
3. **Qwen3.8-Flash-Next** (A.5) — Alibaba Qwen; Gated DeltaNet + QSA; N-gram embedding split.
4. **GLM-5.3-Flash** (A.6) — Z.ai; first natively multimodal GLM-5; sparse+linear attention.

Every other vendor/model mention in this appendix is either (a) a **sub-model / variant of one of these four families** (e.g. DeepSeek-V4-Flash, DeepSeek-V4-Pro) — named only to clarify a family member, never as an additional family — or (b) a **post-snapshot item explicitly outside the four-family comparison** (the 2026-09-27 Ornith-1.5-397B observation in A.6 and the separate 2026-10-28 technology notes). Neither is part of the four-family comparison, its comparative figures, or its First-hand Sources list; read them as subfamilies or out-of-scope side notes, never as a fifth family in the comparison.

## The Signal in One Paragraph

A striking number of 2026 frontier models — four open models we surveyed — converge on a **second-order architectural pattern**, which we read as an interpretation rather than an established historical fact. We should be precise about *what kind* of gain each lever delivers. The common error is to read architecture innovation as raw capability. In our interpretation, it is mostly **efficiency** (more context, less cost per token) that comes out of the attention and MoE changes below, not intelligence. The capability story — reasoning, post-training, test-time compute — lives elsewhere (A.8), and carries at least as much of the frontier's real progress. We separate the two explicitly.

![Fig A.1 — 2026 frontier MoE extreme sparsity: four open models, total vs activated parameters, and active fraction in single digits [1P]](figures/fig-27-2701.png)

*Definition of "active" (what counts in the activated-parameter numerator, and what it does **not** mean).* Here "active" (equivalently "activated") means the parameters that participate in the forward pass for a given token: the routed experts dispatched for that token, the shared/always-on experts, and the attention and embedding/head parameters that run for every token. It is **not** the same as any of these: (a) **resident** parameters — the full expert + attention + embedding fabric that must be held in memory (or sharded/offloaded), which is the total-parameter count, not the active count; (b) per-token **FLOPs**, since activation count is not a proxy for compute cost under softmax-routing and layered dispatch; (c) KV or attention-state **sparsity**, which is a different quantity (see the GQA/MLA discussion in Ch 7); and (d) **achievable serving speed** — a low active fraction does **not** translate proportionally into a faster served rate, because total-weight residency, expert routing/traffic, and attention cost still dominate. The four families use different expert counts, dispatch schemes, and embedding splits (Qwen's N-gram embedding table is counted in total but is offloadable), so the active fractions below are comparable only *after* this definition is fixed; the numbers are not a drop-in cross-model ranking of serving cost. (Here "active" contrasts total vs activated parameters — see the model/MoE discussion in Ch 3 and the GQA/MHA KV discussion in Ch 7.) [1P]

_Frontier MoE sparsity in 2026. Kimi K3 is the extreme case: 2.8 T total / 104 B active (~3.7% active); DeepSeek-V4-Flash 284 B/13 B (~4.6%); GLM-5.3-Flash 320 B/18 B (~5.6%); Qwen3.8-Flash-Next 125 B/6 B (~4.8% — *backbone-only ratio*: the denominator is the 125 B backbone; the separate 51 B n-gram embedding and 4 B MTP modules are excluded from both numerator and denominator, so this is a *backbone* fraction, not a fraction of the complete deployed parameter inventory). Active-parameter fraction in each of these four frontier MoE families is in the single digits — the anchor for the Ch10 expert-parallelism serving calculus. [1P] arXiv 2606.19348; arXiv 2607.24653; HF Qwen/Qwen3.8-Flash-Next; HF zai-org/GLM-5.3-Flash]_

Three **efficiency levers** every 2026 frontier family pulled:

1. **Hybrid attention as the new KV lever — an efficiency lever, not (by itself) a capability lever.** Every frontier model re-engineered attention to shrink long-context cost at the mechanism level — compressed/sparse hybrids (DeepSeek CSA+HCA), delta+sparse (Qwen Gated DeltaNet + QSA), delta/residual (Kimi KDA + AttnRes), sparse+linear (GLM). KV cache is no longer a fixed per-token constant we only quantize; it is a design surface the model vendor already optimized. The intended benefit is to preserve useful model capability while reducing long-context inference cost and/or extending practical context length — indispensable, but it does not by itself make the model smarter. Capability gains come from the post-training/reasoning stack in A.8.
2. **MoE sparsity went extreme — the capacity-per-FLOP lever.** Active-parameter fractions fell to single digits (Kimi 104B of 2.8T; Qwen 6B of 125B). In our reading, one could argue MoE is a *larger* architectural innovation than attention: it lets a lab grow knowledge/capacity without proportionally growing FLOPs per token. That is why the 2026 open landscape is heavily MoE-oriented. Expert parallelism and fused cross-expert communication moved from a footnote to a serving-critical capability.
3. **Efficiency is a first-class result, not an afterthought.** Training-stable optimizers (Muon) and post-training RL (GRPO, async RL) are now reported as core architecture, not tooling.

These three form the *cost/context* ledger of the frontier. The *capability* ledger — reasoning, post-training, test-time compute, agent harness — is where most of the qualitative improvement actually lives (A.8). Distinguishing efficiency levers from capability levers is the architect's first move when reading any new model card.

## How to read this appendix: Observed, Interpretation, Hypothesis

This appendix surveys vendor-reported material, so we are careful to separate three layers of statement that are easy to blur — especially in a fast-moving field full of first/"most-efficient"/3T-class claims:

- **Observed** — what the vendor's technical report or model card actually states (e.g., "DeepSeek-V4 reports a reduced KV footprint"). This is [1P] *fact about the claim*, not the same as the third layer.
- **Interpretation** — our read of what architectural mechanism the report demonstrates (e.g., "the KV reduction suggests the model changes how attention stores state"). This is analysis, ours, and could be wrong.
- **Hypothesis** — a prediction about consequence we draw for serving architecture (e.g., "we expect long-context serving to become more memory-comfortable at equal context"). This is a testable (a hypothesis), not a fact.

When we write "a number of frontier models converge" or "one could argue MoE is a larger architectural innovation," read those as **Interpretation / Hypothesis** — defensible reads of the frontier signal, not independent measurements. Vendor numbers stay tagged [1P] and flagged verify-on-own-hardware; our reads sit one register lower and should be read with the same skepticism we ask of any vendor claim. The practical rule: *if it's a percentage from a report, it's Observed [1P]; if it's a claim about what the industry trend means, it's ours — treat it as analysis, tune it against the reader's real workload.*

**Mapping onto the book's evidence taxonomy.** These three reader-friendly layers are an on-ramp to, not a replacement for, the three-axis taxonomy used throughout the book (provenance × epistemic status × measurement status): Axis 1 provenance [1P]/[2°]/[LAB]/[ILLUSTRATIVE] × Axis 2 status [FACT]/[DERIVED]/[ASSUMPTION]/[HYPOTHESIS]/[UNRESOLVED], with Axis 3 riding along.

- **Observed** ↔ [1P] · [FACT] — the vendor's stated claim, a fact *about the claim*.
- **Interpretation** ↔ [DERIVED] — the book's own analysis, a derivation from the evidence. (Where the book's taxonomy would label it [ILLUSTRATIVE], note that; the appendix uses "interpretation" only as plain prose for a derived read, never a separate sanctioned status.)
- **Hypothesis** ↔ [HYPOTHESIS] — a testable prediction, exactly the taxonomy's [HYPOTHESIS].
- **Measurement status** ↔ Axis 3 — ANALYTICAL / ILLUSTRATIVE / MODELED / MEASURED (or [UNMEASURED] where the stage is not yet determined): how far the number has climbed the measurement-status hierarchy, defined in the Sources, Method, and Reproducibility chapter.

The appendix's labels are the human-friendly framing; the three-axis labels are the precise book-wide convention. They should never conflict.

**This is a dated field guide, not an evergreen ranking.** The four-family comparison is a snapshot as of the 2026-08-30 cutoff (with separately dated September and October observations outside the comparison). A later edition re-verifies the vendor reports and *may* change the families, numbers, or the comparison; the ranking here is not a permanent verdict. **Reproduction status** is recorded per family in the First-hand Sources list (A.10): each entry carries its source URL/identifier, the version and release date where known, and the verification status (whether the claim is vendor-reported [1P] pending independent check, or independently verified). Where a number has not been independently validated, it is flagged — do not treat a model-card figure as an audited measurement. The vendor-fact / author-interpretation / hypothesis layers above, plus the per-family reproduction status, are the four columns a reader needs; a `sources.csv` manifest (source URL, accessed date, model variant, reported baseline, verification status) accompanies the repository's `render/` material for the fast-changing Appendix A claims.

## 1. DeepSeek-V4 — Making Long Context Cheap by Re-Architecting Attention

**Decisive fact [1P] — arXiv 2606.19348; HF deepseek-ai/DeepSeek-V4-Pro:** V4-Pro is 1.6 T total / 49 B activated, V4-Flash 284 B / 13 B activated, both 1M-token context, MIT-licensed. Its hybrid attention combines Compressed Sparse Attention (CSA) and Heavily Compressed Attention (HCA). At 1M context, DeepSeek reports **~27% (Pro) / ~10% (Flash) of V3.2's single-token inference FLOPs and ~10% / ~7% of its KV cache**.

**What this means for the architect (ties to Ch7 Memory, Ch8 Compute).** In our reading of the vendor reports, this is a strong confirmation that *KV-per-token is a moving target*. Chapter 7's arithmetic (per-token × context) is a floor for a given architecture; DeepSeek shows the *constant factor itself* can be cut ~10× without changing the model's parameter count. The architectural decision shifts from "how much KV memory does this context need?" to "which KV scheme does this model use, and is its vendor-published saving reproducible on my serving stack?"

## 2. Kimi K3 — Vendor-Reported First Open 3T-Class Model, and the MoE-Sparsity Extreme

**Decisive fact [1P] — arXiv 2607.24653; HF moonshotai/Kimi-K3:** 2.8 T total / 104 B activated, native vision, 1M context. Built on **Kimi Delta Attention (KDA)** + **Attention Residuals (AttnRes)**, with **Stable LatentMoE** activating just **16 of 896 routed experts** per token. Claims ~**2.5× scaling efficiency** over Kimi K2. Weights are QAT-trained from SFT onward with **MXFP4 weights / MXFP8 activations**. Full weights are released — per the vendor, the first open 3T-class model.

**What this means for the architect (ties to Ch3 Model, Ch10 Parallelism).** A model whose *total* size is 2.8 T but whose *activated* footprint is 104 B is a clear illustration of Ch3's total-vs-activated distinction and Ch10's expert-parallelism doctrine. Serving Kimi K3 requires accommodating the **2.8 T total parameter fabric** across the serving system (the full expert set must reside somewhere unless an explicit offload/load-on-demand architecture is used) while only ~104 B parameters participate in the computation of a given token. The architectural problem is therefore simultaneously one of **total weight residency/distribution** and **active-weight communication/computation** — sharding and scheduling the expert fabric, plus the KV for our context. The decision surface is expert-parallel communication and fused cross-expert kernels, not raw capacity.

## 3. Qwen3.8-Flash-Next — A Vendor-Framed Qwen4 Architecture Preview, Prioritizing Cost-Performance

**Decisive fact [1P] — HF Qwen/Qwen3.8-Flash-Next; GitHub QwenLM/Qwen3.8-Flash-Next:** 125 B total / 6 B activated, plus a separate 51 B of **N-gram embedding** parameters (offloadable to host memory). Native 262 K context (YaRN to 1M). **Hybrid attention: Gated DeltaNet (GDN) + Qwen Sparse Attention (QSA)**, where QSA operates at the *micro-block* level; **Gated Residual** widens the residual stream; 512 MoE experts (10 routed + 1 shared per token); Muon + AdamW. Reported training cost ~1/9 of Qwen3.7-Plus.

**What this means for the architect (ties to Ch3, Ch5 Model Selection, Ch16 TCO).** Qwen's [technical report, 26 August 2026](https://raw.githubusercontent.com/QwenLM/Qwen3.8-Flash-Next/69885871a64393807d988b27b1b5e380e8f28526/tech_report.pdf), describes the n-gram tables as held off the accelerator and prefetched from host memory. This is a vendor-reported mechanism, not only an architectural inference. Its effect on a particular deployment still depends on placement, bandwidth, overlap and engine support; the report does not establish a general serving-performance result for every backend. The 125B backbone, separate 51B n-gram tables and separately listed MTP module remain distinct parts of the residency inventory. Model selection therefore weighs heterogeneous memory and the supported transfer path alongside total and active parameters. [1P][FACT] mechanism; deployment consequence [DERIVED].

## 4. GLM-5.3-Flash — Vendor-Reported First Natively Multimodal GLM, Efficiency-Branded

**Decisive fact [1P] — HF zai-org/GLM-5.3-Flash; [Z.ai release article, 2026-08-26](https://z.ai/blog/glm-5.3-flash):** 320 B total / 18 B activated, 1M native context, 131 K output. Per the vendor, the first natively multimodal model in the GLM-5 series (text/image/video). It combines **sparse+linear attention** (first in the series per the vendor), Manifold-Constrained Hyper-Connections (mHC), W8A8 quantization with mixed-cache (INT8/FP8/BF16), and Encode-Prefill-Decode serving. The release article compares it with **GLM-5.3** using attention compute **per head per layer** and average **BF16 KV cache per layer**. On those normalized measures, it reports 3.0× less attention compute and a 4.4× smaller KV cache. These are not whole-model FLOP or total-cache ratios, and they do not establish an end-to-end speedup. The February GLM-5 parent report, arXiv:2602.15763, is not the source of these Flash-specific ratios. MIT weights. Z.ai positions it as approaching Claude Opus 4.8 on coding/agentic at ~1/10 the price.

**What this means for the architect (ties to Ch7 Memory, Ch8 Compute, Ch19 Agentic).** GLM's coupling of hybrid attention with *native multimodality* shows the model border is remaking: "LLM" and "vision/audio model" are converging in a single weight set, which changes workload characterization (Ch4) — a multimodal prompt has a different token/KV profile than text-only. And mHC + attention-mixing being reported as *scaling-efficiency* results reinforces Ch8's point that compute arithmetic is architecture-specific, not universal.

**Post-snapshot observation (recorded 2026-09-27; outside the 2026-08-30 compile-date envelope).** Beyond the four families above, *Ornith-1.5-397B* (released 2026-08-19 by DeepReinforce / `ornith-ai`) ships as another natively multimodal frontier model: 397 B MoE, ~262 K context, MIT weights, image-input via the inherited Qwen3.5 vision tower. We verified the image-input path end-to-end with a live API call carrying a base64-encoded PNG as `image_url` content: the model's own reasoning trace referenced the rendered pixels (a white-square test and a red/blue half-image test both answered correctly). **This is a [LAB] author observation — a single first-person capability *probe*: one API call, one ad-hoc image fixture, which establishes only that one function path (image input) is *reachable*.** It is **not a benchmark, not comparable across models, and not reproducible without re-running the call**: the exact model/API ID, sampling settings, prompt/image fixtures, and (credential-redacted) API response are not published as a reproducibility capsule, and the probe says nothing about benchmark quality, throughput, or cost. It must **not** be read as evidence for any comparative claim about Ornith-1.5-397B relative to the four families (which it is not a part of), nor as a measurement of capability or quality. It is recorded as a single-path capability hint and cited as an observational sidebar, **not** promoted into the four-family comparative figures or the First-hand Sources list above, both of which retain the 2026-08-30 compile-date stamp. Treat as a hint that the natively multimodal frontier continues to widen between snapshots — exactly the trajectory the four-family narrative above predicts.

## 5. What This Means for the Handbook's Canonical Arithmetic

![Fig A.2 — Vendor-reported percentages remaining relative to each model's own reference, not a shared baseline. GLM's rows are per-layer/per-head scope, not total FLOPs or total cache; no predecessor row exists for Kimi K3 or Qwen3.8-Flash-Next. [1P][DERIVED] Sources: DeepSeek V4 arXiv:2606.19348; Z.ai GLM-5.3-Flash release article, 2026-08-26.](figures/fig-27-2704.png)

*Same message as Fig 7.1's GQA line, taken to the frontier: the per-token KV and FLOP "constants" of Chapter 7/8 are not universal — they are the canonical full-MHA conservative upper-bound teaching model, which hybrid attention re-architects down at the mechanism. Each row is a model's vendor-reported ratio of its own stated reference (e.g. DeepSeek V4 vs V3.2); they do not share a common denominator, so they must not be read as percentages of a single baseline. The canonical 70B dense full-MHA model is the book's teaching floor, not the denominator for these percentages. An architect who re-derives them per candidate model avoids both over- (sizing a 7% KV model as if it were 100%) and under-provisioning. Values are vendor-published [1P], not yet independently reprofiled on a serving stack (see A.7).*

The book's canonical scenario is a 70B dense FP16, ~9.2K-token RAG workload on 8×H100. The 2026 frontier does not invalidate it — it *refines* the interpretation an architect should carry:

- The **KV constant** (Ch7: ~2.62 MB/token FP16; ~1.3 MB/token 8-bit) is the canonical full-MHA conservative upper-bound teaching model. (The 8-bit figure is the raw tensor byte-halving bound: ~1.31 MB/token, exactly 50% of BF16, which is what the fleet-sizing chapters use. vLLM's widely cited 54% [S6] is a decode inter-token-latency slope from its Llama-3.1-8B Table 3 — a latency metric, not a memory ratio; there is no vendor-measured FP8 memory footprint, and any allocator block/metadata overhead is not vendor-measured. The 8-bit KV constants are [ILLUSTRATIVE][DERIVED].) Hybrid-attention models cut it 4–10× at the mechanism, so "context fits on N GPUs" must be re-derived per model, not looked up once. [1P]
- The **roofline** (Ch8) still holds; what changed is where a frontier model's prefill/decode ride it. Vendor-reported FLOP/KV reductions are [1P] first-party claims but not yet independently reproduced — an architect should re-run Ch8's measurement on the candidate model before betting capacity. *Evidence status: first-party vendor claim; deployment-specific result not independently reproduced.*
- The **MoE memory decision** (Ch10) is jointly dominated by total-weight residency/sharding, active-parameter compute, KV footprint, and expert-fabric communication. Extreme sparsity reduces per-token compute; it does not eliminate total-weight residency, which still scales with the full parameter count unless experts are explicitly offloaded or sharded. [1P]

None of this changes the book's *mechanisms*; it changes the *constants* an architect plugs into them. This is exactly why we wrote the arithmetic as verifiable, first-principles reasoning rather than as a fixed catalog of numbers.

## 6. Where 2026 Capability Actually Comes From (beyond Architecture)

A recurring error — easy to fall into after reading four new model cards — is to attribute frontier gains to the attention mechanism splashed across the front page. The industry is converging not just on *architectures* (MoE + efficient attention + very long context) but on a *multi-layered recipe* in which architecture is one ingredient, and arguably not the dominant one. A qualitative decomposition of the recipe:

| Lever | Primary effect |
|---|---|
| Post-training / RL / reasoning | Capability (a major source in current frontier systems) |
| Test-time compute | Capability on hard tasks (more compute on hard problems) |
| Training data + optimization | General capability |
| MoE / parameter scaling | Capacity per FLOP |
| Attention innovation | Context + efficiency (makes the above affordable) |
| Inference / runtime optimization | Cost + latency |
| Agent harness / tool use | Real-world task completion |
| Multimodal architecture | New modalities |

**A frequently underestimated layer is the one the model card almost never shows: post-training.** Two models with broadly similar architectures and pre-training can end up materially different when one went through mediocre post-training and the other excellent. The recipe — the same families every lab now runs — is what carries much of the qualitative gap:

- RLVR / reinforcement learning for reasoning
- synthetic reasoning data
- verifier-based training
- preference optimization
- curriculum learning
- tool-use training and agent trajectories
- coding-specific trajectories
- multimodal reasoning
- long-horizon interaction training

This is why architecture alone never tells an architect how good a frontier model is, and why the decision can no longer stop at "which model" — the marginal capability may live in the post-training and the runtime that wraps it.

![Fig A.3 — A conceptual layering of frontier AI systems. The dates are approximate era markers, not a rigorously established chronology, and the vertical stacking is a *layering* (which capabilities sit on which substrate), not a causal lineage: a later layer does not require the one below it, and the eras overlap. Read it as "what exists at each stage," not "what caused what." [ILLUSTRATIVE] conceptual](figures/fig-27-2703.png)

From a single model to a whole system. The earlier stages (Transformer, Efficient, MoE) are *efficiency-led* — they make inference affordable and raise capacity-per-FLOP. The later stages (Reasoning, Test-Time Compute, Tool-Using, Agent, Agent System, Agent Fleet) are *capability-led* — they raise effective intelligence. [DERIVED]

This chain is the spine of this handbook — from a single model's tokens (Ch1–9) to parallelism (Ch10), serving (Ch11–16), and finally the fleet of specialized models and agents (Ch17–26). It also explains why two models with broadly similar base architectures can have very different practical intelligence (post-training/reasoning), and why an agent runtime can lift real-world performance without changing model weights at all: **model intelligence ≠ system intelligence anymore.**

## 7. The Frontier Question: Where Should Intelligence Live?

The most useful lens for an AI Solution Architect in 2026 is not "which attention mechanism does the model card list?" but *where the intelligence and the compute budget should be placed*:

![Fig A.4 — Where should intelligence live? The horizontal bands are a **design choice** (which layer owns which capability), not a ranking of superiority: a lower band is not "better" or "worse" than a higher one, and the boundaries shift with the workload, the trust model, and the cost/latency budget. Read each band as "what we put here and why," not "what is best here." [ILLUSTRATIVE] conceptual](figures/fig-27-2702.png)

The placement ladder. Every host layer that can carry intelligence is a place the architect may choose to push capability or cost; this book gives the arithmetic and decision framework for each (Ch3/7/8 weights & attention, Ch10 MoE routing, Ch19/21 post-training, Ch8/20 test-time, Ch19/24 tools, Ch17–20 runtime, Ch18/20 fleet). [ILLUSTRATIVE][DERIVED]

Every host layer maps to chapters in this book:

- **Inside weights** (dense capacity) — Ch3 Model, Ch8 Compute
- **Inside attention** (context / efficiency) — Ch7 Memory, Ch8 Compute
- **Inside MoE routing** (capacity per FLOP) — Ch10 Parallelism
- **Inside post-training** (reasoning, RL, verification) — Ch19 Agentic, Ch21 AI Factory
- **Inside test-time search** (adaptive inference, more compute on hard tasks) — Ch8 Compute, Ch20 Fleet-Level Optimization
- **Inside tools** (compute allocated via a harness) — Ch19 Agentic, Ch24 Red/Green Team
- **Inside the agent runtime** (persistent state, runbooks, execution control) — Ch17–20, Ch24
- **Across a fleet of specialized models** — Ch18 Operating Multiple Models, Ch20 Fleet-Level Optimization

Deciding where intelligence lives — rather than which attention variant a model card lists — is the actual job of an AI Solution Architect. The frontier of 2026 makes that explicit: DeepSeek-V4-Flash vs Qwen3.8-Flash vs a fleet of specialized agents on a 2×DGX cluster are no longer merely *model* choices; they are *placement-of-intelligence* choices whose economics this handbook's chapters give the tools to evaluate.

## Post-snapshot technology notes — 2026-10-28 {.unnumbered}

The following notes are outside the four-family comparison and its 2026-08-30 First-hand Sources list. They retain separate retrieval, release and implementation dates. They do not refresh the earlier comparison or establish locally measured performance. Sources inspected 28 October 2026 as part of this separately dated addendum, not a refresh of the August comparison tables. The long machine URLs behind the numbered source entries cited in these notes ([A-S01]–[A-S105]) are held in the release source ledger `source-verification.md`, pinned to immutable commit revisions where retrievable.

### Architecture dimensions and executed depth — 2026-10-28 {.unnumbered}

This update is separate from the four-family comparison compiled through 30 August 2026. A retrieval date is not a release date. Some examples below were available before that comparison; others are later releases or later paper revisions. The purpose is to examine mechanisms that change a deployment decision, not to extend a model ranking.

#### Three independent dimensions {.unnumbered}

A model description now needs at least three independent dimensions: parameter allocation, history-state representation, and execution depth. Dense feed-forward layers can coexist with recurrent token mixing. Sparse experts can coexist with global attention. Shared weights can execute repeatedly within one token prediction. None of these properties determines the others.

`Qwen/Qwen3.8-27B` is a useful counterexample to the idea that a dense model must use conventional full attention throughout. Its card describes dense feed-forward layers and native image/video understanding. Its language configuration contains 48 Gated DeltaNet layers and 16 full-attention layers. DeltaNet updates a recurrent history state; the full-attention layers retain a separate history-dependent KV component. Dense parameter allocation therefore does not imply a full-MHA cache formula.[^oct-mt-q27]

A different form of recurrence repeats a shared core over the current representation. Huginn and Ouro provide public research examples. Their shared weights reduce the unique parameter inventory relative to an equally deep untied network. The repeated executions still consume compute. Attention states can also differ between iterations, even when the weights are identical. These research artifacts are not evidence that adaptive-depth production serving is already routine.[^oct-mt-huginn]^,^[^oct-mt-ouro]

| Mechanism | Repeated or selected object | Main budget consequence | Important boundary |
|---|---|---|---|
| MoE routing | Selected feed-forward experts | Active compute and expert traffic differ from total residency | Sparse activation does not make all weights disappear |
| History recurrence | A state updated across input tokens | Some history components can have bounded decode state | Remaining attention layers can still grow with history |
| Shared-depth recurrence | A core reused within a prediction | Compute depends on executed depth; iteration caches may remain distinct | Shared weights do not imply shared KV |
| Speculative decoding | Draft candidates followed by target verification | Cost depends on accepted tokens per verification and draft overhead | It is not shared-depth reasoning |
| Agent orchestration | External model and tool calls | Turns, replay, branches, and tool time determine task cost | It is not an internal layer loop |

This table classifies mechanisms, not performance results. A single model can combine several rows.

#### Phase and storage tier matter {.unnumbered}

`deepseek-ai/DeepSeek-V4.1-Flash` changes more than one constant. Its vendor report describes a Causal Encoder-Decoder with 552B backbone parameters and a separate 196B Engram component. It reports 8B activated parameters per token during prefill and 16B during decode. A single active-parameter figure would obscure this phase difference. These counts describe the vendor's computation paths; they do not establish an elapsed-time ratio.[^oct-mt-ds41]

The report also separates memory objects. Cross-layer reuse and FP4 main-KV storage produce a reported global HBM KV footprint of 890 bytes per token. This is not total request memory. Bounded sliding-window state, weights, workspaces, and allocation overhead remain separate. The reported persistent-cache reduction to approximately one-eighth of DeepSeek-V4-Flash concerns host or SSD storage under SWA Bounded Replay. It is not the same metric as global HBM KV.

The transferable rule is to account for each independently stored state, its update rule, and its location. Sparse attention that reads selected history entries need not store only those entries. Cross-layer consumers can share one stored object. A local window can bound live state while prefix restoration still incurs storage or recomputation. Capacity across several accelerators also does not establish that each rank fits its assigned weights and state.

#### A stopping rule is not yet a runtime saving {.unnumbered}

Huginn's model card requires a recurrence-aware cache so that later core passes do not overwrite earlier KV entries. It also labels its per-token adaptive-compute facility a zero-shot proof of concept. Its stopping criteria include changes in latent state, output distributions, and prediction stability.[^oct-mt-huginn]

Ouro's revised paper studies learned exit decisions and cache sharing. It reports that prefill needs distinct iteration caches in the evaluated setting, while selected decode-only sharing strategies can reduce the cache component. These are phase-specific experiments, not a universal reduction in whole-request memory.[^oct-mt-ouro]

The released runtime path also matters. In the Ouro implementation retrieved for this update, the core loop computes all configured iterations before the language-model wrapper selects an exit representation. That path does not demonstrate skipped core computation merely because an earlier representation is selected. The model card separately states that its vLLM path does not support adaptive exit. A paper's stopping policy, a reference implementation, and an optimized serving engine are different evidence objects.[^oct-mt-ouro-code]^,^[^oct-mt-ouro-card]

A deployment evaluation would therefore record actual core executions, state bytes, and per-stage time alongside quality. Variable-depth scheduling could change batch efficiency and latency tails. That consequence remains a testable hypothesis until measured on the intended engine and workload.

Figure A.5 separates the parameter object from its invocations and the invocations from their cached histories. The lower lanes make the stopping boundary explicit. Only the upper lane avoids the final pass. The exit index in the drawing is illustrative; it does not prescribe a quality-preserving stopping rule for either research model.

![Fig A.5 — Shared-depth execution reuses weights, not necessarily history state. Distinct iteration caches are shown for the separate-cache case. A true exit omits later work; selecting an earlier representation after all passes does not. The exit after pass 2 is illustrative, not an Ouro performance result.](figures/fig-27-2705-depth-execution.png)


With separate caches, an iteration index is part of the state identity. Reusing the same weight pointer does not make different hidden representations interchangeable. A cache-sharing policy changes that assumption and needs its own phase-specific evidence. An adaptive stopping rule also needs an accuracy target: stable logits or a small latent-state change is a stopping signal, not proof of correct reasoning. These distinctions keep a research mechanism from being promoted into a production efficiency claim without the intervening engine and workload evidence.[^oct-mt-huginn]^,^[^oct-mt-ouro]

#### Training loops are not inference loops {.unnumbered}

Ornith-1.5 provides a useful boundary case. Its report describes joint improvement of training tasks, scaffolds, and solution rollouts. The released family builds on existing architectures with additional training. This is evidence about the training and evaluation system, not proof of shared-depth recurrence or online weight updates during a user request.[^oct-mt-ornith]

The same distinction applies within a vendor's product family. Z.ai describes GLM-5.3 as using the GLM-5.2 base with post-training gains, while GLM-5.3-Flash starts from a newly trained base and a redesigned hybrid architecture. The exact variant determines which explanation applies.[^oct-mt-glm]

“Flash” does not identify a common architecture or a small resident model. The open-weight examples combine different expert layouts, compressed or local attention, multimodal encoders, and drafting mechanisms. For `gemini-3.8-flash`, the public documentation establishes a service interface and token limits, but the sources examined here do not establish its exact parameter inventory or KV layout. Service price and product naming cannot fill that gap.[^oct-mt-gemini]

### Quantization implementation observations — 2026-10-28 {.unnumbered}

These observations concern pinned October implementations, not support at the August cutoff. No backend performance was measured for this note.

Current implementations illustrate why representation and execution are separate. At vLLM commit `41dd82e6a7392ead33b1e8a7d175442511e488ca`, NVFP4 has a CUTLASS low-bit path, a Marlin W4A16 path and a higher-precision emulation path. Its MXFP4 Marlin code explicitly ignores a requested activation-quantization configuration because that kernel is weight-only. These are different execution experiments even when the stored weights use the same named representation. They are code observations, not benchmarks or proof that a particular installed release selects the native path. [1P][FACT] ([NVFP4 CUTLASS](https://github.com/vllm-project/vllm/blob/41dd82e6a7392ead33b1e8a7d175442511e488ca/vllm/model_executor/kernels/linear/nvfp4/cutlass.py); [NVFP4 Marlin](https://github.com/vllm-project/vllm/blob/41dd82e6a7392ead33b1e8a7d175442511e488ca/vllm/model_executor/kernels/linear/nvfp4/marlin.py); [MXFP4 Marlin](https://github.com/vllm-project/vllm/blob/41dd82e6a7392ead33b1e8a7d175442511e488ca/vllm/model_executor/kernels/linear/mxfp4/marlin.py).)

The same separation appears in GGML/llama.cpp. At the pinned revision in the source ledger, `block_q4_K` occupies 144 bytes for 256 values: 4.5 effective bits/value. `Q4_K_M`, however, selects a mixture of tensor encodings and can promote selected tensors to Q6_K. IQ encodings have their own grid, sign, lookup and scale layouts; their imatrix requirements are type-specific. The complete model's average precision therefore follows a tensor inventory, not one block's byte rate. GGML's `block_nvfp4` also has a specific scale layout; the name alone does not establish interoperability with NVIDIA's tensor-global-scale representation. [1P][DERIVED][ANALYTICAL] ([block definitions](https://github.com/ggml-org/llama.cpp/blob/8ca4060b7e30e76baaa5670ee1ec1b760b7f8552/ggml/src/ggml-common.h); [tensor selection](https://github.com/ggml-org/llama.cpp/blob/8ca4060b7e30e76baaa5670ee1ec1b760b7f8552/src/llama-quant.cpp).)

Post-training calibration and training-based recovery also describe different work. PTQ estimates quantization parameters without a full model-training run; the particular algorithm can search scales or compensate weight errors. QAT updates model parameters while accounting for quantization effects. QAD additionally uses teacher targets to recover behavior. That recovery consumes training compute and memory, and a favorable fake-quant evaluation still needs confirmation after export through the real serving kernels. Calibration, recovery and inference therefore receive separate resource ledgers and separate quality records. [1P][DERIVED] ([Model Optimizer QAT/QAD example, pinned revision](https://github.com/NVIDIA/Model-Optimizer/blob/580ffff1cddb9b20a38b7434e6290654ebf96a8f/examples/llm_qat/README.md).)

An NVFP4 training recipe need not have the same storage arrangement as a one-dimensional inference storage budget. Transformer Engine documents two-dimensional 16×16 weight scaling, as well as gradient-specific stochastic rounding, transformations for weight-gradient computation and high-precision treatment of sensitive layers. These are additional recipe choices, not properties supplied by the four-bit value code. Training can also require multiple tensor orientations, higher-precision state and temporary buffers. The unique scale information of a 2D block is therefore not a prediction of resident training memory, nor a reason to reuse an inference footprint as the training budget. [1P][DERIVED] ([Transformer Engine NVFP4](https://docs.nvidia.com/deeplearning/transformer-engine/features/low_precision_training/nvfp4/nvfp4.html).)

OCP MicroXcaling 1.1 is dated 2026-10-09 and renames E8M0 to UE8M0 while clarifying conversion and boundary behavior. That revision is later than the book's cutoff. The August snapshot retains the 1.0 E8M0 terminology; later terminology is identified here with its revision date. Current Model Optimizer recipes also combine AWQ-lite error control with either INT4 or NVFP4 representations. This is evidence that the method and representation are combinable axes, not that every method/container/backend combination is available. [1P][FACT] ([OCP MicroXcaling 1.1](https://www.opencompute.org/wp-content/uploads/2026/10/OCP_MicroXcaling_Spec_v1.1.0.pdf); [INT4 AWQ preset](https://raw.githubusercontent.com/NVIDIA/Model-Optimizer/580ffff1cddb9b20a38b7434e6290654ebf96a8f/modelopt_recipes/configs/ptq/presets/model/int4_awq.yaml); [NVFP4 AWQ preset](https://raw.githubusercontent.com/NVIDIA/Model-Optimizer/580ffff1cddb9b20a38b7434e6290654ebf96a8f/modelopt_recipes/configs/ptq/presets/model/nvfp4_awq_lite.yaml).)

### Diffusion language generation — 2026-10-28 {.unnumbered}

This observation is outside Appendix A's frozen 2026-08-30 comparison. It does not update that four-family table or treat a present-day source as proof of its historical contents.

Public artifacts now support more than one diffusion-language deployment pattern. LLaDA and Dream provide open checkpoints and generation code for masked/refinement-based language generation. Their announcements, paper dates and later checkpoint revisions are separate provenance events. LLaDA2.2 adds bounded block editing and block-level expert routing. DiffusionGemma is an explicitly experimental open release with an encoded context cache and a separately refined canvas; its uniform-state renoising does not require MASK. Mercury 3 is a vendor-documented closed API release dated 2026-10-19. Its internal schedule, precision and hardware allocation have not been independently established here. Gemini Diffusion's official page describes an experimental demo. These records establish different release and support boundaries, not a common production-readiness level. [1P][FACT][^oct-diff-releases]

The inspected SGLang revision, `a1966e1b5d8b750b494d7e53cca1d2464f960038`, illustrates why engine names are insufficient. Its Gemma4Renoise path disables radix caching and chunked prefill, rejects quantized loading and pipeline/context parallelism, and accepts only specified attention backends. Its recipe rejects grammar/logit-bias requests. Vendor low-precision performance claims do not override those implementation restrictions. Conversely, the source contains an attention-backend-specific graph path, so an older recipe's eager-only shorthand is not a timeless limitation. These are static source observations, not a successful local deployment test. [1P][FACT][^oct-diff-engine]

The strongest evidence supports conditional hypotheses, not a speed ranking. Google's own DiffusionGemma report describes a low-concurrency benefit while acknowledging lower overall quality and potentially higher serving costs. Earlier LLaDA results differ by task. Recent cache/verify work compares against particular diffusion baselines and does not establish an equivalent gain over an optimized AR service. Published evaluations also identify format, replanning and exploration failures in earlier models; those findings cannot be projected unchanged onto later releases. The durable conclusion is to compare matched-quality service frontiers, with explicit cache and commitment semantics. [1P][FACT] (source-reported, not locally reproduced); [2°][FACT][^oct-diff-evaluations]

### Video systems snapshot — 2026-10-28 {.unnumbered}

This note extends the book's 30 August 2026 evidence cutoff explicitly. It records inspected public sources, not an exhaustive claim about private, gated, regional, or unretrieved releases. Model release dates and engine support dates remain separate.

The most useful comparison is not a ranking. It is which mechanism changes the resource model:

| Inspected model / path | Mechanism | Design boundary |
|---|---|---|
| Wan2.2 TI2V-5B | Dense whole-clip DiT; VAE stride (4,16,16); patch (1,2,2) | Compact video token grid. Peak workspace and repeated whole-clip work still matter. The worked example uses this model only. |
| Wan2.2 T2V/I2V-A14B | Noise-stage experts; about 27B total / 14B active; VAE stride (4,8,8) | Active compute and resident weights differ. Its token geometry is not the 5B geometry. |
| HunyuanVideo-1.5 | 8.3B; high-compression VAE; selective/sliding tile attention; distilled variants | Sparse attention and fewer evaluations are distinct optimization axes. A report's sparse checkpoint does not prove availability of every task variant. |
| LTX-2 / LTX-2.5 | LTX-2 report describes coupled video/audio streams and multistage inference; 2.5 is a separately documented release | Audio tokens, cross-modal work, upsampling, and multiple passes require their own budget. LTX-2 constants are not automatically LTX-2.5 constants. |
| `wan3.0-video` / `wan3.0-video-prime` | Current official asynchronous hosted API, labeled preview | Service contract is visible; public weights, parameter count, VAE geometry, and self-hosted runtime are not established by that API. |

[1P][FACT] mechanisms and product labels; resource consequences are scoped deductions.[^oct-vg-W22]^,^[^oct-vg-W5]^,^[^oct-vg-H15]^,^[^oct-vg-LTX]^,^[^oct-vg-LTX25]^,^[^oct-vg-WANAPI]

Wan's specialized paths further separate the task from the family name. Wan2.1 VACE supports video creation and editing through explicit condition representations. Wan2.2-S2V-14B conditions video on supplied audio, with reference-image and optional pose inputs; this is not evidence that the base model synthesizes native audio from text. Wan-Dancer and Wan-Animate-2 expose additional motion and animation research paths. Their recipes, auxiliary encoders, and quality criteria remain distinct from T2V. [1P][FACT][^oct-vg-VACE]^,^[^oct-vg-S2V]^,^[^oct-vg-DANCER]

Wan-Animate-2 also demonstrates why the attention boundary must follow the exact variant. Its Base path separates reference and denoising branches and uses sparse reference attention. Its Lite path instead applies causal chunk dependencies; the report illustrates eight-frame segments of the driving stream. Tokens in a current noisy chunk attend to preceding clean context and to one another. This is chunk-wise autoregression around iterative generation, not a single-token text decode loop. Earlier chunk delivery can change the latency contract, but accumulated errors and retained history still require a budget. The report does not establish a particular KV-cache layout or an unlimited constant-memory stream. [1P][FACT] architecture; [ILLUSTRATIVE][DERIVED] serving boundaries.[^oct-vg-ANIMATE]

Versioned implementation evidence is also narrower than production validation. Diffusers v0.35.0 documents Wan2.2; v0.37.0 introduces LTX-2; v0.40.0 documents Wan-Animate-2; v0.42.0 contains LTX-2.5 and HunyuanVideo-1.5 pipeline documentation. Their published release dates are 19 August 2025, 5 March 2026, 20 August 2026, and 23 October 2026 respectively. The last is outside the book cutoff. The existence of a pipeline does not establish a validated queueing service, multi-tenant isolation, every kernel backend, or a latency SLA. [1P][FACT][^oct-vg-ENGINES]

Two evidence limits remain material. LTX-2's report uses 14B+5B in its abstract and 13B+3B in its conclusion; this note does not choose an exact total from that conflict. LTX-2.5's official release notes date it to 11 August 2026, but raw gated configuration requests were not accessible in this investigation. Its official 22B label is not a tensor-count audit. The license text is accessible and must be considered separately. [1P][FACT][^oct-vg-LTX]^,^[^oct-vg-LTX25]

Public weights do not remove rights or safety obligations. Wan's inspected releases identify Apache-2.0, while LTX-2.5 and HunyuanVideo-1.5 use community licenses with commercial or territorial conditions. Input-image, audio, likeness, music, and output-use permissions are separate questions. Provenance records can retain checkpoint revision, recipe, seed, source-asset rights, moderation decisions, and output hashes. Such records support investigation; they do not establish that an output is legally cleared or factually authentic. No legal conclusion is implied. [1P][FACT] license observations; [ILLUSTRATIVE][DERIVED] provenance design.[^oct-vg-LICENSES]

### Intel backend supplement — 2026-10-28 {.unnumbered}

> Intel backend supplement — observed 2026-10-28 UTC; outside the 2026-08-30 evidence snapshot.
>
> Observed. The retrieved release APIs identify PyTorch v2.14.1 (September 30), vLLM v0.32.0 (October 18), SGLang v0.5.22 (October 19), OpenVINO Runtime 2026.4.1 and OpenVINO GenAI 2026.4.1.0 (October 1). These are release identities, not one validated combined environment. A later check on 28 October at 21:35 UTC also found PyTorch v2.15.0, published at 17:09 UTC that day.[^oct-ix-torch215] The newer framework release does not change the examined engine dependency pins. The examined vLLM XPU requirements pin PyTorch 2.14.0, Triton 3.8.0+xpu and vllm_xpu_kernels 0.1.15.4. Its guide and dependency file disagree on the Triton version, so installation instructions require resolution and testing. [^oct-ix-21]^,^[^oct-ix-22]^,^[^oct-ix-26]^,^[^oct-ix-42]^,^[^oct-ix-53]^,^[^oct-ix-67]^,^[^oct-ix-71]
>
> Observed. Intel's March announcement places Arc Pro B70 availability on March 25, 2026 and B65 availability in mid-April. Their datasheets both specify 32 GB and 608 GB/s, but different INT8 dense peaks. Intel's October OCP statement describes GPU D-series, formerly Crescent Island, as sampling. Its footnote distinguishes a 160 GB Intel-branded card from partner options up to 480 GB. General availability and independent performance are not established by that statement. [^oct-ix-7]^,^[^oct-ix-8]^,^[^oct-ix-13]^,^[^oct-ix-28]
>
> Interpretation. Upstream device and engine integration make Intel GPU configurations concrete candidates for evaluation. They do not establish parity across models, quantization paths, graph modes, collectives or hardware generations. Gaudi and client NPU paths remain separate. [^oct-ix-47]^,^[^oct-ix-49]^,^[^oct-ix-54]^,^[^oct-ix-55]^,^[^oct-ix-66]
>
> Hypothesis. Intel configurations may offer a useful capacity, energy or cost trade-off for particular workloads. This requires independent measurements at the same quality and SLO. Current upstream support, vendor availability announcements and a local deployment account do not establish a market-share trend or a universal winner. [^oct-ix-56]^,^[^oct-ix-60]^,^[^oct-ix-61]

[^oct-mt-q27]: Qwen, Qwen3.8-27B model card, “Model Overview,” “Benchmark Results,” and long-context guidance: [A-S13]. Released configuration: [A-S14]. Public implementation: [A-S15].

[^oct-mt-huginn]: Geiping et al., “Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach,” arXiv:2502.05171, v2, 17 February 2025: https://arxiv.org/abs/2502.05171. Huginn checkpoint card, “KV-cache Details” and “Per-Token Adaptive Compute”: [A-S17].

[^oct-mt-ouro]: Zhu et al., “Scaling Latent Reasoning via Looped Language Models,” arXiv:2510.25741v6, revised 11 October 2026, especially §5.4.2 and Table 14: https://arxiv.org/pdf/2510.25741v6 . Revision history: https://arxiv.org/abs/2510.25741 .

[^oct-mt-ouro-code]: ByteDance/Ouro-2.6B, released `modeling_ouro.py`, `OuroModel.forward` and exit-logit selection in `OuroForCausalLM.forward`, fetched revision archived in source-index.json: [A-S20]. This is a static code observation, not an executed performance measurement.

[^oct-mt-ouro-card]: ByteDance/Ouro-2.6B model card, adaptive-exit and vLLM notes: [A-S21]. Card/config layer-count differences remain unresolved: [A-S22].

[^oct-mt-ds41]: DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression,” Abstract and §§2.1–2.4, 3.2: [A-S23]. Model card: [A-S24]. The numerical memory and activation claims are vendor-reported, not independently reproduced.

[^oct-mt-ornith]: Ornith Team, “Ornith-1.5: From Self-Scaffolding to Self-Improvement,” August 2026: https://ornith.ai/ornith_1_5.html. Variant card: [A-S26].

[^oct-mt-glm]: Z.ai official GLM repository, “GLM-5.3 & GLM-5.3-Flash”: [A-S27]. Exact Flash card: [A-S28].

[^oct-mt-gemini]: Google DeepMind, Gemini 3.8 Flash model card, published 2 September 2026: https://deepmind.google/models/model-cards/gemini-3-8-flash/. Exact-model API documentation, updated 22 October 2026: [A-S30].

[^oct-diff-releases]: Primary sources and scoped evaluations retrieved 2026-10-28: [A-S31], [A-S32], [A-S33], [A-S34], [A-S35], [A-S36], [A-S37], [A-S38], [A-S39], [A-S40], [A-S41], [A-S42], [A-S43], [A-S44]. Source-reported findings; not locally reproduced.

[^oct-diff-engine]: Primary sources and scoped evaluations retrieved 2026-10-28: [A-S35], [A-S45]. Source-reported findings; not locally reproduced.

[^oct-diff-evaluations]: Primary sources and scoped evaluations retrieved 2026-10-28: [A-S46], [A-S34], [A-S33], [A-S39], [A-S47], [A-S48], [A-S49], [A-S50], [A-S51]. Source-reported findings; not locally reproduced.

[^oct-vg-W22]: Wan official README, release history, architecture, inference, licenses. [A-S52]. Wan2.2's report link resolves to the older Wan report; it is not treated as a Wan2.2-specific paper.

[^oct-vg-W5]: Wan2.2 official TI2V-5B configuration. [A-S53]. Cross-check: [A-S54] and [A-S55].

[^oct-vg-H15]: HunyuanVideo-1.5 Technical Report, arXiv:2511.18870, especially model architecture and §6 Tables 7–8. https://arxiv.org/html/2511.18870 . Official repository: https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5 . Timing results are vendor-reported, not measurements made for this book.

[^oct-vg-LTX]: LTX-2: Efficient Joint Audio-Visual Foundation Model, arXiv:2601.03233, architecture, §6.3/Table 1, limitations and conclusion. https://arxiv.org/html/2601.03233 .

[^oct-vg-LTX25]: Official release notes: [A-S59]; official model page: [A-S60]; versioned Diffusers documentation: [A-S61]. Gated raw configurations remain unverified.

[^oct-vg-WANAPI]: Alibaba Cloud Model Studio, current video overview and Wan3 API reference. [A-S62] and [A-S63]. Retrieved 2026-10-28; preview status is material.

[^oct-vg-VACE]: VACE: All-in-One Video Creation and Editing, arXiv:2503.07598, §3.3; official code https://github.com/ali-vilab/VACE . https://arxiv.org/html/2503.07598 .

[^oct-vg-S2V]: Official Wan-S2V technical report, §3–4. [A-S66]; official card https://huggingface.co/Wan-AI/Wan2.2-S2V-14B.

[^oct-vg-DANCER]: Wan-Dancer official code https://github.com/Wan-Video/Wan-Dancer ; report https://arxiv.org/html/2607.09581 .

[^oct-vg-ANIMATE]: Wan-Animate-2 report https://arxiv.org/html/2608.06009 and official repository https://github.com/Wan-Video/Wan-Animate-2 . The report was first submitted on 6 August 2026 and revised on 8 August 2026. Its Lite three-step distillation and the README's ten-step example are different recipes.

[^oct-vg-ENGINES]: Official release metadata: [A-S72], [A-S73], [A-S74], [A-S75].

[^oct-vg-LICENSES]: Wan license [A-S76]; LTX-2.x license [A-S77]; Hunyuan license [A-S78]. License observations are not legal advice.

[^oct-ix-torch215]: PyTorch v2.15.0 release metadata, published 2026-10-28T17:09:49Z and retrieved 2026-10-28T21:35:32Z: [A-S79]. Release publication is not validation of the vLLM XPU environment.

[^oct-ix-7]: First-party source retrieved 2026-10-28: [A-S80]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-8]: First-party source retrieved 2026-10-28: [A-S81]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-13]: First-party source retrieved 2026-10-28: [A-S82]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-21]: First-party source retrieved 2026-10-28: [A-S83]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-22]: First-party source retrieved 2026-10-28: [A-S84]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-26]: First-party source retrieved 2026-10-28: [A-S85]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-28]: First-party source retrieved 2026-10-28: [A-S86]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-42]: First-party source retrieved 2026-10-28: [A-S87]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-47]: First-party source retrieved 2026-10-28: <https://docs.habana.ai/en/latest/API_Reference_Guides/HCCL_APIs/index.html>. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-49]: First-party source retrieved 2026-10-28: [A-S89]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-53]: First-party source retrieved 2026-10-28: [A-S90]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-54]: First-party source retrieved 2026-10-28: [A-S91]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-55]: First-party source retrieved 2026-10-28: <https://docs.habana.ai/en/latest/PyTorch/PyTorch_Model_Porting/Porting_PyTorch_Models_to_Gaudi.html>. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-56]: First-party source retrieved 2026-10-28: [A-S93]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-60]: Independent benchmark account [2°], retrieved 2026-10-28: [A-S94]. This is a third-party benchmark account, not a vendor release identity; the book has not reproduced its measurements or established a validated combined environment.

[^oct-ix-61]: Independent deployment account [2°], retrieved 2026-10-28: [A-S95]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-66]: First-party source retrieved 2026-10-28: [A-S96]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-67]: First-party source retrieved 2026-10-28: [A-S97]. Release identities and source observations are not a validated combined environment or independent performance measurements.

[^oct-ix-71]: First-party source retrieved 2026-10-28: [A-S98]. Release identities and source observations are not a validated combined environment or independent performance measurements.

## 8. First-hand Sources (all [1P])

- DeepSeek-V4: technical report arXiv:2606.19348; model card https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro; org https://github.com/deepseek-ai
- Kimi K3: technical report arXiv:2607.24653; model card https://huggingface.co/moonshotai/Kimi-K3; https://github.com/moonshotai
- Qwen3.8-Flash-Next: technical report https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/69885871a64393807d988b27b1b5e380e8f28526/tech_report.pdf; model card https://huggingface.co/Qwen/Qwen3.8-Flash-Next
- GLM-5.3-Flash: release article https://z.ai/blog/glm-5.3-flash (2026-08-26; Flash-specific architecture and normalized attention/KV comparison); model card https://huggingface.co/zai-org/GLM-5.3-Flash. The February GLM-5 parent report arXiv:2602.15763 is background for the earlier model, not evidence for the Flash ratios.

*Compiled 2026-08-30 from the models' official technical reports and first-party model cards; all parameters/claims are vendor-reported [1P] and per this handbook's discipline carry a verify-on-own-hardware caveat.*

> **Citation integrity / frozen-snapshot note (reader-facing).** Every external identifier in this list — the arXiv IDs (arXiv:2606.19348, arXiv:2607.24653, arXiv:2602.15763) and the huggingface.co / github.com model-card and repo URLs — was captured against the frozen **2026-08-30** source snapshot for this edition. arXiv IDs and model cards are versioned and can be withdrawn, revised, re-uploaded, or re-pointed, so re-open a citation before relying on it: an identifier that now resolves to a *different* version than the one compiled on 2026-08-30 would change the [1P] claims this appendix draws on. The required checks and resolved-artifact hashes for this edition are recorded in the release `sources.csv` / release manifest (see the Sources chapter), not re-derived here — the four-family comparison is intentionally pinned to the frozen 2026-08-30 snapshot and is **not** a current model leaderboard.
