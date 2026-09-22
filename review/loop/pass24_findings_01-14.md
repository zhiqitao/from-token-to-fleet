# PASS 24 — Publication Audit — Pages 1–155 (0-indexed 0–154): Chapters 1–12 (Figures 1.1–11.3, plus front-matter Figs 1–2 and the chapter-12 Fig 12.1 at the boundary)

**PDF:** `render/build/from-token-to-fleet-v20260913.pdf` (309 pp)
**Slice:** pymupdf pages 0–154 (book pages −21 … book page 133). Book-page = PDF-index − 21.
**Scan method:** every numbered figure in the slice was rendered to PNG at 200–400 dpi with pymupdf and inspected pixel-by-pixel at normal reading scale (not inferred from captions / source / extracted text, which carry none of the figure text — it is all vector). Figures in Ch. 13 (Fig 13.1, pdf 163) and Ch. 14 (Fig 14.1, pdf 169) fall beyond the page-155 boundary and are out of this slice (see companion pass); Fig 12.1 (pdf 156) is two index pages past the boundary and is included **and flagged** here since chapter 12 is partially in-scope.
**Result of the audit: NOT publication-ready.**

---

## 1. OVERALL ASSESSMENT

The prose in this slice is unusually strong on the core quality standard: the canonical-scenario arithmetic (140 GB FP16, 2.62 MB/token full-MHA KV, 24.1 GB@9.2K, 436 GB KV budget, 1.29 PFLOP prefill → 1.19 PFLOPS vs 0.989, 5.6 TB/s decode vs 3.35, roofline ridges 295/206) recomputes correctly and is internally consistent across chapters and tables. The book explicitly and repeatedly separates **kernel regime** (compute- vs bandwidth-bound, qualified by model×workload×kernel×hardware) from **workload-capacity deficit**, marks derived vs [1P][FACT] vs vendor-reported, and names the "single-host feasibility vs fleet sizing" split. Terminology is largely disciplined (rps for arrival rate; TTFT/TPOT/ITL; goodput vs throughput; host). Chapter-to-chapter transitions and the mini-case structure support the token→workload→system→architecture progression.

**Where it falls short is the figure floor.** This is where the publication gate fails. Of 25 numbered figures inspected, only **2 pass as KEEP**. The dominant failure is not wrong math but **rendered-figure quality**: text clipped by box edges, labels overlapping data/annotations, arrows whose semantics contradict the textual message, color-only encoding that breaks in grayscale, tiny (~8 pt and below) internal typography, and several figures that are "box-and-arrow prose" (the geometry encodes nothing prose couldn't). One figure (10.2) has **literally clipped labels** ("PP·pipelin", "CP·contex", "W weights (row", "token sequenc", "transformer laye") in ~6–8 pt type — an unambiguous P0 defect. Figures 7.1, 11.3 have content clipped/overlapped. The fraction of figures needing more than cosmetic polish is high (17/25 = MAJOR REVISION or REDESIGN).

There are no catastrophic *technical* errors in the prose of pages 1–155 (chapters 1–12), and the canonical scenario holds together. The blocker to publication is the figure-by-figure visual standard and a small number of figure-side quantitative/terminology inconsistencies (drawn in §4).

---

## 2. HIGHEST-PRIORITY TECHNICAL / CONCEPTUAL ISSUES

1. **Figure 8.2 mis-places the prefill operating point on the x-axis.** Prefill arithmetic intensity for a 9.2K prompt is 2·N·L / (2·N bytes) = **L ≈ 9,200 FLOP/byte**, i.e. ~31× the H100 ridge (~295). The figure caps its x-axis at ~10³ and draws the "prefill 9.2K" marker at ≈ 300–400 FLOP/byte (just past the ridge). The categorical reading (prefill is compute-bound) survives, but the plot **understates how far into the compute-bound regime prefill sits** and invites the reader to read prefill as "barely past the ridge." This is a PASS-8 quantitative-figure-integrity defect: the plotted x-position does not represent the encoded quantity.
2. **Two conflicting FP8–KV per-token figures coexist.** The idealized 8-bit halving is **~1.31 MB/token** (used in Fig 7.2's "byte-halving bound" and chapter 1's reference); the realistic FP8 KV with scale metadata is **~1.42 MB/token (54% of BF16)** (used for the "13.4 GB/request" and the **~33 slots** in Fig 7.4, and in Ch 12 §7.4 note). Divide differently and the FP8 concurrency is **~35** (436 ÷ 12.4), not 33. Both figures are defensible but should be reconciled/one should be labeled "idealized vs realistic FP8 KV" or the concurrency count stated with the per-token value it assumes.
3. **Chapter-3 KV formula is the full-MHA special case stated as the canonical formula.** §3.4.3 writes "KVper-token = 2 × nlayers × dhidden × bytes-per-value." This is only valid when n_KV-heads × d_head = d_hidden (full MHA, as here: 2×80×8192×2 = 2.62 MB). Chapter 7 correctly generalizes to 2 × nlayers × n_KV-heads × dhead × B. The Ch. 3 form should be qualified "full-MHA (n_KV × dhead = dhidden)"; otherwise it silently overstates KV for the GQA models the book itself uses elsewhere.
4. **Fig 11.3 "bound" vs "starved" inconsistency + per-GPU/per-pool ambiguity.** The caption labels the pools "compute-bound" / "bandwidth-bound"; the in-figure note says prefill is "FLOP-starved" (~1.19 PFLOPS vs 0.989) and decode "bandwidth-starved" (5.6 TB/s vs 3.35). "Starved" ≠ "bound," and neither 1.19 PFLOPS nor 5.6 TB/s is qualified as per-GPU vs the 4-GPU pool aggregate (both are actually whole-70B-model quantities that cannot fit one GPU). The visual therefore makes an unqualified bound claim on a per-GPU-looking diagram.
5. **Fig 12.1 mixes per-host prefill with system-wide demand.** Candidate (a) is judged "prefill ~19.8K << ~92K needed" without defining the ~92K baseline or showing the host-scaling factor; a reader must parse prose to see (b) needs two pools while (a) and (b) both display "164 GB." Color-only candidate status (blue/green/red) with no redundant cue.

**Strengths to preserve (verified):** the 2.62 MB/token full-MHA upper bound and its ~8× GQA reduction; the "parameter count ≠ KV footprint" lesson (Fig 7.2); the explicit full-MHA-hypothetical framing of the "single H100" decode/prefill arithmetic; the per-GPU watermark and caption in Fig 8.2; the aggregate-vs-per-rank red banner in Fig 7.4; the [ILLUSTRATIVE][DERIVED]/[1P][FACT] labeling discipline.

---

## 3. STORYLINE / VALUE-BASED REVIEW

The slice (Parts I–IV, Ch 1–12) forms a coherent causal chain: token unit → tokenizer/embedding/attention/KV cache → inference pipeline & prefill/decode → parameter regime (dense vs MoE) → workload six-dimension characterization → model selection → measurement/metrics → memory → compute/roofline → interconnect/communication → parallelism → serving → architecture synthesis. The "End-of-Chapter Mini-Case" pattern is effective and ties each chapter's quantity to the next chapter's decision.

Section-level observations:
- **Ch 1–2** introduce the token and the prefill/decode split; valuable and tightly connected. No removal-worthy content.
- **§2.4.1 Table 2-1** duplicates the per-token FLOP/bandwidth logic that Ch 8 develops; the two are cross-referenced rather than duplicated. Acceptable.
- **Ch 3 §3.4.3** ("why MoE saves compute but not KV") is a high-value conceptual pivot — keep.
- **Ch 4 Table 4-3** ("single reference set") is the linchpin; the consistency ledgers across the slice hang off it. It is doing a lot of work and should stay. Its presentation needs work (see §8).
- **Ch 6 §6** on goodput vs throughput is a genuine contribution and a good "the same number, three stories" teaching point.
- **Ch 7** is the strongest chapter; the Tetris/concurrency figures are the ones carrying the just-in-time "aggregate ≠ per-rank" concept, which is exactly the right argument — but the *figures* undercut the argument (see §5).
- **Ch 11 §11** (serving stack "four concerns, not a stack") is a good conceptual correction, but the figure (11.2) visually contradicts it (see below).
- **Ch 12** (constraint-first synthesis) is a strong capstone for Part IV and correctly anticipates Ch 13–14.
- No generic MLOps filler or vendor-catalog chapters appear in this slice. Nothing here "does not depend on AI architecture."

Lowest-value / trim-able: none rise to removal. The mini-case endnotes occasionally restate the chapter's summary rather than advancing (e.g., the Ch 2 and Ch 5 mini-cases mostly re-assert canonical numbers). These are compressible but not wrong.

---

## 4. NUMERICAL / TERMINOLOGY / EVIDENCE AUDIT

### Independent recomputation (all verified correct)
- 70B × 2 B = **140 GB** ✓
- full-MHA KV = 2×80×8192×2 = **2,621,440 B ≈ 2.62 MB/token** (2.5 MiB) ✓; GQA = 2×80×8×128×2 ≈ **0.33 MB/token** ✓ (8×)
- KV @ 9.2K = 2.62 MB×9,200 ≈ **24.1 GB**; @ 9.5K = **24.9 GB**; @ 32K = **84 GB**; @ 128K = **335 GB** ✓
- runtime 64 GB + weights 140 GB + KV ⇒ 229 / 288 / 539 GB ✓
- KV budget = 640 − 140 − 64 = **436 GB** ✓; 436 ÷ 24.1 ≈ **18** concurrency (FP16) ✓
- prefill FLOPs = 2×70e9×9.2e3 = **1.288e15 ≈ 1.29 PFLOP** ✓; /1.08 s = **≈1.19 PFLOPS** > 0.989 ✓
- decode BW = 140 GB / 0.025 s = **5.6 TB/s** > 3.35 ✓
- roofline ridges = 989/3.35 = **295**, 989/4.8 = **206** ✓
- decode intensity ≈ 2N/(2N) = **1 FLOP/byte** ✓
- in-flight = λ·W = 40 rps × 8.58 s ≈ **344** ✓; price 2.50×8 = $20/hr ≈ **$14.6K/mo** ✓
- MoE 47B/14B ≈ 29.8% active, ~5× less than 70B dense ✓ (flagged [2°]/[ILLUSTRATIVE])

### Cross-chapter consistency ledger
The canonical scenario is stable across Ch 1, 2, 4, 5, 7, 8, 11, 12: 70B dense FP16; 9.2K in / 300 out; TTFT 1.2 s (120 ms + 1.08 s), p95 ≤ 2 s; TPOT 25 ms (p95 ≤ 35 ms); 8×H100 640 GB; $2.50/GPU-hr. **No contradictions found.** "Model size / KV cache / TTFT / TPOT / host count" cohere.

### Terminology drift
- **host / node / instance / GPU node** are used interchangeably for the 8×H100 box (e.g. "single node vs multi-node" p.2184, "$20/hr per 8-GPU node" p.2294, "H100 instance" p.2645, "8×H100 node's 640 GB" p.3166 vs "host" throughout figures). Recommend one canonical term ("host") with an explicit "= 8×H100" glossary at first use.
- **query** is used both for the attention Q projection and for the retrieval/user query; contextually clear but worth a one-line disambiguation.
- QPS vs RPS: the book uses **rps** throughout for arrival rate; consistent. **ITL vs TPOT** both used, defined at first use; acceptable but should assert TPOT as canonical and ITL as the instant value.
- **request vs query vs prompt**: Ch 4 uses "prompt/query" for the user input. Minor.
- **KV cache vs prefix cache vs prompt cache**: consistently "KV cache" for state, "prefix cache" for reuse — good.
- No `GB`/`GiB` confusion: the book uses 2.5 MiB vs 2.62 MB explicitly — good.

### Evidence taxonomy
- Clearly separates **measured / derived / illustrative / vendor-reported ([1P][FACT])**, dates Appendix-style snapshots, and adds dense-vs-sparse TFLOPS and sustained-vs-peak HBM caveats. This is a model for the genre.
- Minor: Fig 6.2 (latency histogram with mean=0.85 s, p50=0.80, p90=0.94, p95=0.99, p99=1.33, SLO 2 s) is presented as a quantitative chart but is **not marked** ILLUSTRATIVE/synthetic; the axis (0–6 s, ~70% empty) plus a smooth "1% stragglers" shaded band could overstate empirical authority. Mark it.
- Fig 9.1 annotates a specific time at "140 GB" using a dashed line **outside the plotted data range** (data stop near 10² GB), implying precision of an extrapolation.

---

## 5. FIGURE-BY-FIGURE VISUAL AUDIT (25 figures; every numbered figure in slice reported)

> Verdict scale: KEEP / POLISH / MAJOR REVISION / REDESIGN / REMOVE-MERGE.

### Front matter

**FIGURE 1 (architect's decision loop) — MAJOR REVISION**
Page: xii (pdf 17, book xii) | Primary purpose: the book's spine — vague ask → characterize → constraints → candidates → benchmark → bottleneck → TCO → red-team → commit.
First glance: four colored Part strips with pill labels in the gaps; clean but reads as a slide.
Specific visual defects: the "define/size/justify" pill labels overlap and clip the card top borders; the "iterate" pill overlaps card-02 right border; bottom tags ("inputs/work/economics/decide") and subtitles are small, low-contrast monospace; connector rules have **no arrowheads** (solid left / dashed right), so the loop-back is undecodable; color-only stage identity.
Technical/semantic risks: the iteration/feedback is not visibly a closed loop (no return arrow to stage 01); the dashed-right vs solid-left has no in-figure key; a reader can't tell whether iteration is 02↔03, 03↔04, or a loop to 01. It also sits where a "spine" should be maximally legible.
Required action: add an explicit return arrow (feedback loop) to stage 01 with an arrowhead and a short label ("iterate → re-characterize"); remove the pill-on-border clipping by placing labels fully in the gap; enlarge the tags; add a legend for the solid/dashed distinction or drop it. Prefer showing one dominant left→right flow with a clear loop-back.

**FIGURE 2 (reading the book by number) — MAJOR REVISION**
Page: xiii (pdf 18) | Primary purpose: Part strips + chapter chips; each chapter supplies a derived quantity that feeds a decision.
First glance: six pale-blue panels with chips and "topic → decision" rows; dense but legible at distance.
Specific visual defects: **missing arrows** (Part III Ch 8 run together as "roofline vs ridge compute/mem-bound"; Part V Ch 18 "route by cap/cost multi-model routing") — the topic→decision arrow is absent, so topic and outcome concatenate; **dual/ambiguous arrows** (Ch 23 "vague ask → bounds → scope it", Ch 26 "workload → strategy → pick pattern" use the same "→" for both in-topic and structural separation); tiny chips; reading order I→VI broken across two columns with no cross-panel row alignment (defeating "reading across any chapter's chip"); color-only (single pale-blue palette); slide-like.
Technical/semantic risks: the whole point — traceability of "which number for which question" — is compromised where arrows are missing or ambiguous.
Required action: every row must have exactly one structural topic→decision arrow, visually distinct from any in-topic "→"; restore the missing arrows; align rows into a common grid across panels so cross-part traceability is visual; bump chip/row text above body-minimum.

### Chapter 1

**FIGURE 1.1 — KEEP**
Page: 5 (pdf 26) | Purpose: every decoded token adds one K+V per layer per head. Clean left-to-right flow; labels legible; convergence slightly dense but not defective. No change required.

**FIGURE 1.2 — KEEP**
Page: 6 (pdf 27) | Purpose: text → tokenizer → IDs → embedding → attention → KV cache. Well-balanced two-row pipeline; generous spacing; unambiguous "split/emit/lookup/attend/append K,V." Page-level whitespace above/below is large but figure itself is sound. No change required. (Minor: page 6 is most empty page in slice; consider reflowing.)

### Chapter 2

**FIGURE 2.1 (canonical inference pipeline) — MAJOR REVISION**
Page: 13 (pdf 34) | Purpose: prefill vs decode, TTFT vs TPOT/ITL.
First glance: two horizontal 5-step chains; informative but dense.
Specific visual defects: step labels sit on/over the box bottom border (text touching/clipped by box); the long vertical "first token → decode" connector crosses the "one-shot burst…TTFT" annotation and the "KV cache: created in prefill…" note; the concurrent middle steps prompt-tokens→embeddings→layers→create K/V are drawn as a strict serial chain (misleading for parallel prefill); data/model/KV-state distinguished by **fill colour alone** (grey/blue/orange) with no redundant shape/hatch — grayscale breaks; high density (sub-heads + TTFT/TPOT note + KV note + resource-regime box + legend stacked).
Technical/semantic risks: implies prefill phases are temporally serial (they're parallel across prompt positions); the single hand-off arrow understates that decode is an iterative loop; color-only violates PASS 4/11.
Required action: reduce to two (not five) stages per phase or add a parallel-indicating glyph; pull labels inside boxes with padding; route the connector around, not through, annotations; add pattern/hatch redundancy for data/compute/KV state; keep the (good) qualified "resource regime is a function of model×workload×kernel×hardware" call-out.

**FIGURE 2.2 (arithmetic-intensity continuum) — MAJOR REVISION**
Page: 17 (pdf 38) | Purpose: prefill/decode on an intensity continuum split by the ridge.
First glance: single qualitative continuum; nice idea, weakly executed.
Specific visual defects: **no numeric axis** — no ticks/scale, only "lower → / → higher"; the ridge is a hard vertical rule with "~295" that reads as a precise universal law; "prefill @ 9.2K prompt" label overlaps "roofline ridge ~295"; sub-axis notes are tiny low-contrast grey; the qualifying "these are operating points…" only lives in the caption and a small italic note, **not visually encoded** (no fuzzy boundary / error band / "≈").
Technical/semantic risks: PASS 7 failure — the graphic itself communicates an unconditional rule that the prose qualifies; ridge shown as exact; prefill marker sits at/beyond the ridge implying near-ridge rather than ~31× the ridge intensity.
Required action: add a numeric log intensity axis (decades) so the ridge and the points have true positions; mark prefill at its actual ≈9.2K FLOP/byte; make the boundary visually soft (gradient/fuzz) to preserve the heuristic; enlarge the qualification note.

### Chapter 3

**FIGURE 3.1 (dense vs MoE) — MAJOR REVISION**
Page: 32 (pdf 53) | Purpose: total vs active params, same KV.
Specific visual defects: active/inactive experts distinguished **by fill colour only** (orange vs light grey) — grayscale loses the distinction; 24 equal-blue dense squares are visually equated 1:1 with 8 expert boxes (equal sizes imply equivalence of unlike units); the metric text ("resident 140 GB / active 140 GB" vs "resident full / active 28 GB") is small, squeezed, and the Dense metrics sit in the inter-panel gutter so "every token" ownership is ambiguous; columns asymmetric, forcing zig-zag reading.
Technical/semantic risks: equal-box-size equivalence is a PASS-6 false implication (a "dense square" is not an "expert"); color-only breaks grayscale.
Required action: add "ACTIVE" hatching/pattern + a numeric count label per expert (E1…E8, "top-2 active"); put dense metrics under the dense panel and MoE metrics under the MoE panel (no gutter text); consider scaling block representation to the ratio (or annotating "not to scale").

### Chapter 4

**FIGURE 4.1 (six-dimension → decisions) — MAJOR REVISION**
Page: 48 (pdf 69) | Purpose: map six workload dimensions to architectural consequences.
First glance: two columns of colored boxes with identical right-arrows; reads as a list.
Specific visual defects: box-arrow-prose weakness — geometry encodes nothing beyond "A is linked to B" (no coupling strength, no many-to-many, no feedback); **one-to-one parallel arrows misleadingly imply a bijective exclusive mapping** when the relationships are interdependent (caption/prose say many-to-many); blue=dimension / orange=consequence is color-only with no column headers; rows cramped; reading order inferred from the figure's heading, not the figure.
Technical/semantic risks: PASS 5/6 — teaches a false bijection; PASS 11 breakdown.
Required action: replace with a visual that shows the coupling — e.g., a matrix (dimension × decision with density/weighting marks) or a many-to-many link graph; add explicit "Workload dimension" / "Architectural decision" headers; encode strength via line weight or the goods that pass between.

### Chapter 5

**FIGURE 5.1 (model selection ladder) — MAJOR REVISION**
Page: 60 (pdf 81) | Purpose: workload → five surfaces → retrieval/generation legs → system decision.
Specific visual defects: arrows cross/graze labels ("split" labels duplicated and ambiguous — one above the diagonal shaft to retrieval, one to the right of the vertical shaft to generation); edge labels ("drives/split/context/answer") tiny light-grey; second line "quality·latency·KV·$/tok·RAG" cramped against box right edge; color-only (workload node and generation-leg node share a green fill despite being different stages); box-arrow-prose; large empty margins above/below → slide-like.
Technical/semantic risks: ambiguous which "split" belongs to which leg; color-only grouping; the flow reads as disconnected boxes rather than the workload-driven branching decision it should be.
Required action: give each outgoing edge a label placed on the shaft, not in a gutter; differentiate the two legs visually and separate the shared-source ordering; increase edge-label size/contrast; reduce page-margin whitespace relative to the graphic.

### Chapter 6

**FIGURE 6.1 (metric hierarchy diagnostic chain) — POLISH**
Page: 63 (pdf 84) | Purpose: workload/resource/serving metrics with causation-down, diagnosis-up.
Specific visual defects: the chain has **no arrowheads** and meaning is offloaded to a prose legend ("green solid = causation, red dashed = diagnosis"); that directionality is also **color-only** (green vs red) though the solid/dashed linestyle is a redundant cue — re-label the connectors themselves; the vertical ladder implies "higher = more abstract/important" while the diagnostic use is bottom-up (serving → workload); sub-titles tiny/cramped.
Technical/semantic risks: ladder reading suggests Serving is subordinate, but serving metrics are the user-facing outcomes the others explain.
Required action: put arrowheads and inline labels on the two connectors ("causation ↓", "diagnosis ↑"); de-emphasize the ladder rank by reordering or labelling "observed at serving, explained at workload"; enlarge sub-titles.

**FIGURE 6.2 (latency distribution) — POLISH**
Page: 65 (pdf 86) | Purpose: the mean hides the tail; p50/p90/p95/p99 vs SLO.
Specific visual defects: the p50/p90/p95 labels overlap each other and the tallest bars; x-axis 0–6 s is ~70% empty (informative mass crushed into 0–1.5 s); the pink "1% stragglers" band has no in-figure legend/key; **not marked ILLUSTRATIVE/synthetic** (presents as empirical); the single ~5 s straggler bar sits in a big empty shaded region.
Technical/semantic risks: PASS 8 — a derived/illustrative distribution is given benchmark-like visual authority; label clutter undercuts reading of percentiles.
Required action: truncate x-axis to ~2 s (or annotate a break) so the mass and the tail read; stagger the percentile labels off the bars; add a legend for the shaded straggler band; mark the figure ILLUSTRATIVE (synthetic).

### Chapter 7

**FIGURE 7.1 (GQA cuts per-token KV) — MAJOR REVISION**
Page: 77 (pdf 98) | Purpose: 64 query heads → 8 shared KV heads, 8× smaller.
Specific visual defects: **the top rectangle of all eight stacks is clipped** (the top-most query-head rect is truncated at its top edge); the call-out box text is small/dense and the red bold line sits close to the border; group identity is **hue-only** (8 colors, no pattern/label) — grayscale loses the 8× mapping; the "8 shared KV heads" label sits in the corridor of the 8 descending lines; PASS 10 FAIL — only GQA is drawn, MHA appears only as text ("MHA (full): 64 K/V per token → 2.62 MB/token"), so the 8× comparison is asserted, not shown on a common visual scale.
Technical/semantic risks: no visual MHA-side stacks to compare; the size difference between 64 small query rects and 8 KV squares does not encode the sharing ratio; color-only breaks grayscale.
Required action: draw BOTH the MHA (64 K/V) and the GQA (8 K/V) configurations side-by-side on the same geometry so the 8× is visible; fix the clipped top rects; add redundant group labels/patterns; give the KV row proper clearance.

**FIGURE 7.2 (KV vs context; MHA vs GQA vs FP8) — POLISH**
Page: 81 (pdf 102) | Purpose: KV footprint driven by attention shape, not parameter count (the lesson is delivered well).
Specific visual defects: legend text and axis ticks tiny; the legend sits outside/overlapping the plot with the two call-outs; the "9.2K ≈ 24 GB (FP16 bound)" and "9.2K ≈ 3 GB (GQA)…" labels overlap curves; each series drawn as a continuous straight log–log line through only 4 markers — misleading precision (though explicitly [ILLUSTRATIVE][DERIVED]).
Required action: enlarge legend/ticks; move call-outs to clear zones; draw as marked points with light connecting lines (or annotate "illustrative points, not measured curve").

**FIGURE 7.3 (inference vs fine-tuning floor) — POLISH**
Page: 82 (pdf 103) | Purpose: 165 GB vs ~1,120 GB vs 60 GB versus 1/2/8×H100.
Specific visual defects: the red annotation "full fine tune exceeds an 8×H100 host…" overlaps the plot title and the legend box; "~1120 GB" value label is cramped against the top spine; two-line x-labels (weights+KV / +grad+optim / +adapters) sit tight to the axis; legend inside the data area; hardware threshold lines are color-only (grey/dark-blue/green, same dashed style; green==QLoRA hue, blue≈Inference hue). The linear 0–1400 scale is legitimate and the 18.7:1 ratio is real — not a defect.
Required action: move annotations above/below the axes with clear leaders; give the value labels padding; place legend outside; add linestyle/pattern redundancy to the threshold lines.

**FIGURE 7.4 (concurrency budget, 640 GB pool) — MAJOR REVISION**
Page: 83 (pdf 104) | Purpose: where a 70B host's 640 GB goes; 18 (FP16) / 33 (FP8) concurrent.
Specific visual defects: the "scenario reserve (not a hardware constant)" call-out **overlaps** the red "AGGREGATE RESIDENCY SCREEN ≠ PER-RANK FIT GUARANTEE" warning; the white "140 GB / weights" and "KV budget ~436 GB" labels sit **over** hatch/dot patterns (reduced legibility) with little padding; FP16 vs FP8 rows distinguished by blue vs pale-blue / green vs pale-green (color-only); "C ≈ 18 concurrent requests @ FP16" abuts the bar edge; **PASS 9 fail** — one continuous 0→640 GB bar reinforces a single fungible heap; no 80 GB per-rank gridlines (per-rank caveat relegated to the small italic note).
Technical/semantic risks: the graphic's single-pool geometry fights the very caveat the caption/textures add; grayscale ambiguity.
Required action: fix the warning/call-out collision; draw per-rank 80 GB delineation (or a "per-rank" strip) so "aggregate ≠ per-rank" is in the graphic, not only the footnote; move value labels off the hatch; add pattern redundancy for FP16/FP8 and for weights/reserve/KV.

**FIGURE 7.5 (Memory Tetris, 3 contexts) — MAJOR REVISION**
Page: 84 (pdf 105) | Purpose: baseline constant + KV grows with context: 229 / 288 / 539 GB vs 640.
Specific visual defects: "24.9 GB KV" label straddles/clips the 9.5K/32K bars; "84 GB KV" sits immediately adjacent (crowded red label band); the 32K bar is drawn as two adjacent rects with a separator (reads as a rendering artifact); "= 229/288/539 GB used" in much smaller grey; **no per-rank 80 GB ceiling / sharding lines** (aggregate-as-fungible-pool), so 539 GB < 640 GB visually "fits," contradicting the caption's aggregate-only caveat; color+light-pattern primarily.
Technical/semantic risks: PASS 9 — the visual asserts fit from "total < total" while the caption warns it isn't a fit guarantee; KV growth hard to judge because the 9.5K KV segment is a sliver.
Required action: fix the red KV-label overlaps; draw per-rank 80 GB limits and a "KV sharded across ranks" marker so the per-rank caveat is visible; show the KV segment growth with clearer scale/anchor; un-split the 32K bar.

### Chapter 8

**FIGURE 8.1 (memory/compute hierarchy) — POLISH**
Page: 89 (pdf 110) | Purpose: registers→SRAM→L2→HBM→interconnect→other GPUs, and what runs where.
Specific visual defects: secondary labels ("fastest·smallest", "arithmetic units", "large·slower", "farthest") tiny and close to box bottoms; ladder levels nearly touching (little breathing room); color-only grouping (blue/orange/green) with no in-figure key; the "tensor cores / ALU" box mixes a compute unit into a memory ladder; "memory-bound" region vs compute ordering is conceptual.
Technical/semantic risks: the ladder strongly implies "higher = better / more important," but the top rung is the *scarcest* resource (smallest/fastest), so the ranking metaphor can be read as "registers are best"; L2-above-shared-memory ordering is debatable for many GPUs.
Required action: add a redundant legend for the compute/memory/interconnect grouping; label the axis as a speed↔capacity↔distance gradient rather than a hierarchy; add explicit "not to scale"; enlarge secondary labels.

**FIGURE 8.2 (per-GPU roofline) — MAJOR REVISION**
Page: 93 (pdf 114) | Purpose: H100 vs H200 roofline; decode/decode-batched/prefill placement.
Specific visual defects: "decode batch=1" label overlaps the orange "memory-bound slope" text; "ridge ≈ 295" sits on top of the red dashed (H200) roofline; "prefill 9.2K" marker is ambiguous vs the ridge dotted lines; "decode batched" label sits on the line; the legend is cramped inside the axes and partially under the "PER-GPU" watermark; rotated small tick labels; straight log–log memory-bound line + flat plateau (with [DERIVED] caption). **Plus the x-position issue in §2.1** (prefill drawn at ≈300–400 FLOP/byte instead of ≈9,200).
Technical/semantic risks: multiple overlapping annotations reduce comprehension; prefill intensity misrepresented; straight-line noise implies measured precision.
Required action: separate the annotation zones; place "prefill 9.2K" at its true intensity (or annotate "off-scale at ≈9.2K, shown just past ridge"); move the legend out of the plot; enlarge ticks; add a "per-GPU" axis note.

### Chapter 9

**FIGURE 9.1 (all-reduce time vs data volume) — POLISH**
Page: 101 (pdf 122) | Purpose: four interconnect tiers, time vs volume.
Specific visual defects: y-axis log ticks **skip a decade — 10⁰,10¹,10²,10³,10⁵,10⁶** (no 10⁴), a legibility/logical inconsistency; the "140 GB (70B weights)" annotation is drawn **outside the plotted data range** (data stop near 10² GB) implying precision for an extrapolation; legend cramped (two rows) directly under the x-axis title; rotated small ticks.
Technical/semantic risks: extrapolated 140 GB point overstates certainty; inconsistent log ticks.
Required action: fix the missing 10⁴ tick; either extend the data markers to 140 GB or label the 140 GB reference as "extrapolated"; give the legend breathing room. (Grayscale robustness is good — solid/dashed/dash-dot/dotted × circle/square/triangle/diamond provide redundancy.)

### Chapter 10

**FIGURE 10.1 (composing parallel dimensions) — MAJOR REVISION**
Page: 109 (pdf 130) | Purpose: CP/TP/DP/EP/PP composition.
Specific visual defects: secondary monospace text ("the same GPUs also take part in EP all-to-all", "EP composes with the per-stage mesh", "composition") tiny; single ambiguous upward arrow from the per-stage mesh to GPU B only (does EP compose with all of GPU A/B/C or one?); color-only grouping (orange EP / purple mesh / teal PP) — CP absent, TP not shown independently (only as "DP × TP"); reading-order ambiguous (pipeline at bottom, EP top, arrow up); slide-like with large margins.
Technical/semantic risks: the composition (how the three GPUs in the EP box relate to the DP×TP mesh) is asserted in prose, not diagrammed; the missing CP under-specifies the dimension set the caption claims to cover.
Required action: draw the EP layer explicitly over the full per-stage mesh (all GPUs) with the all-to-all; label TP explicitly; add CP as a fourth row/so it isn't dropped; enlarge secondary labels; add an explicit reading-order path.

**FIGURE 10.2 (five parallelization strategies) — REDESIGN** (worst figure in slice)
Page: 114 (pdf 135) | Purpose: comparison matrix — what each of TP/PP/DP/EP/CP splits, replicates, communicates.
First glance: dense 5-row matrix; **text is clipped**.
Specific visual defects: **clipped/truncated labels** — strategy column "PP·pipelin", "CP·contex" (cut), WHAT-SPLITS "W weights (row" / "transformer laye" / "token sequenc" (cut), header "WHAT SPLIT" (cut); body type ~6–8 pt, footnote ~5 pt; four columns squeezed into ~30% of text width (chars against cell borders, tight leading); color-only strategy encoding (blue gradient) + color-only column headers (blue/grey/red); header row not visually separated from data rows; **pure tabular prose** (no boxes/arrows showing fan-out or communication pattern) under a "conceptual" caption.
Technical/semantic risks: the comparison does not function because labels cannot be read; communication patterns are only short text phrases; color-only.
Required action: **REDESIGN** the matrix at usable type with column widths that fit the strings (or abbreviate with an in-figure key); preserve strategy name in full; separate the header row; make communication pattern visual (icon/arrow per cell) rather than prose; add text redundancy for the blue gradient. This is the P0 figure to fix first.

### Chapter 11

**FIGURE 11.1 (discrete vs continuous batching) — MAJOR REVISION**
Page: 119 (pdf 140) | Purpose: slot diagram; idle bubbles vs immediate slot reuse.
Specific visual defects: "a finishing sequence frees its slot immediately" annotation **overlaps the green squares** in row 3; "next batch waits" sits over the grey box border; **no axis labels** — the left panel uses horizontal extent for time within a batch window while the right panel uses a vertical arrow for time, so time is encoded **orthogonally** across panels; color-only (blue/orange/red/green with no in-figure legend); the two panels share no common baseline (PASS-10 FAIL).
Technical/semantic risks: reader can't compare idle/utilization on a common time scale; the discrete vs continuous comparison is qualitative.
Required action: give both panels a common time axis (or annotate which axis is time in each); legend the sequence colors and the idle color; place annotations off the squares; align the two panels on a shared baseline so utilization is directly comparable.

**FIGURE 11.2 (serving stack: four concerns) — MAJOR REVISION**
Page: 124 (pdf 145) | Purpose: batching, KV management, prefix caching, P/D split are orthogonal, not a stack.
Specific visual defects: body text in each card ~8–9 pt, italic notes ~8 pt, tight padding; the **central top-to-bottom arrow visually contradicts the figure's own thesis** ("not a stack", "orthogonal") by implying a linear Request→concerns→Output pipeline; the outer "THE FOUR SERVING CONCERNS" box + inner cards imply containment/layering; "all four in parallel" label collides with the right cards; color-only (green/orange/purple/red); box-arrow-prose; slide-like; competing scan paths (vertical arrow vs 2×2 grid).
Technical/semantic risks: PASS 6/14 — the visual actively teaches a stack that the text says is false.
Required action: remove the through-arrow or recast it as "request stream passes through all four in parallel" with a fork, not a pipeline; drop the containment box (or label it "orthogonal set, not layering"); enlarge card text; add a legend for the concern types.

**FIGURE 11.3 (P/D disaggregation) — MAJOR REVISION**
Page: 125 (pdf 146) | Purpose: prefill pool (compute) / decode pool (bandwidth) + KV transfer.
Specific visual defects: "KV CACHE TRANSFER (initial)" label **overlaps the top GPU squares** in both pools; the 3-line ownership note ("prefill writes the prompt KV, then decode READS it…") overlaps the double arrow and the lower-left decode GPU; "steady token generation / high bandwidth" text overlaps the lower decode GPUs; "massive prompt at once / high FLOP utilization" flush against the pool bottom border; **the output arrow points up into the decode pool** while labelled "← tokens out to client" (directionally contradictory); a **double-headed** transfer arrow but the note describes a **one-way** write-then-read (ownership split not encoded); compute-bound/bandwidth-bound caption vs "FLOP-starved"/"bandwidth-starved" note (starved ≠ bound) with per-GPU-vs-pool ambiguity; pools distinguished by red vs blue (color-only).
Technical/semantic risks: PASS 7/8 — unqualified bound claims + per-GPU/aggregate ambiguity + contradictory arrow semantics.
Required action: fix the overlaps (move transfer label and ownership note to a clear band); set output arrow direction consistent with the text; use a one-way (or clearly annotated) transfer arrow showing direction and "initial"; qualify compute-/bandwidth-bound (state per-GPU, and "starved/marginal," not absolute); add a legend for prefill/decode pools.

### Chapter 12 (boundary figure — included and flagged)

**FIGURE 12.1 (candidate architecture synthesis) — MAJOR REVISION**
Page: 135 (pdf 156; two pages beyond the page-155 boundary) | Purpose: 3 candidate architectures, constraint satisfaction.
Specific visual defects: tiny body type (esp. stage ④); candidate (a) and (b) lines run together ("…164 GB   weights 140 GB + KV 24 GB = 164 GB/pool") with no separator; SURVIVORS box abuts/overlaps REJECTED ("→ excluded from evaluation" crosses the SURVIVORS right edge); the single arrow from ④ lands in the gap between SURVIVORS/REJECTED (not to either); color-only candidate status (blue/green/red); "~19.8K << ~92K" mixes per-host with system-wide demand; economics "1 host ≈ $14.6K/mo ✓" vs "2 hosts + fabric (~2× capex)" with no common cost axis; box-arrow-prose (dense prose in boxes).
Technical/semantic risks: prefill-throughput comparison across inconsistent denominators; color-only outcome classification.
Required action: separate candidate lines and add separators; route the ④ arrow to the SURVIVORS branch explicitly (or draw a decision gate); add text/pattern redundancy for status; state the ~92K baseline and per-host vs system scaling; give the two outcome boxes clearance.

---

## 6. CROSS-FIGURE SYSTEMIC ISSUES

1. **Prevalence of text/data overlap & clipping.** At least 8 figures (1, 5.1, 6.2, 7.1, 7.3, 7.4, 7.5, 11.3, 12.1, 8.2, 10.2, 2.1) show label-over-box, label-over-data, label-over-annotation, or clipped glyph collisions. This is a systemic engineer, not isolated.
2. **Color-only encoding is widespread.** 3.1 (active/inactive), 4.1 (source/target), 5.1 (node types), 6.1 (causation/diagnosis — partially saved by dash/solid), 7.1 (8 expert hues), 7.3 (hardware lines), 8.1 (compute/memory/interconnect groups), 10.1 (TP/EP/PP), 10.2 (strategy + columns), 11.1 (sequences), 11.2 (concerns), 11.3 (pools), 12.1 (status), 2.1 (data/model/KV). Grayscale/color-vision-impaired reading fails on a large fraction of the figures. **This is the single most important system-level figure issue.**
3. **Box-and-arrow prose.** 4.1, 5.1, 10.1, 10.2, 11.2, 12.1 (and, milder, 3.1, 6.1) encode information in sentence-length box text rather than in position/scale/topology/quantitative encoding — the geometry adds little over prose (PASS 5/15/16).
4. **Unannotated axis/scale convention.** 2.2 (no numeric axis), 6.2 (~70% empty), 8.2 (prefill off true scale), 9.1 (missing 10⁴ tick + out-of-range reference), 11.1 (time encoded orthogonally), 10.2 (tiny type).
5. **Tiny internal typography.** Secondary/italic/legend/monospace text falls to ~8 pt or below in 2.1, 2.2, 3.1, 5.1, 6.1, 7.1, 7.3, 7.4, 7.5, 8.1, 8.2, 9.1, 10.1, 10.2, 11.2, 11.3, 12.1, Fig 1, Fig 2.
6. **Presentation-slide aesthetic.** Large centered titles + colored cards + generous outer margins appear in 2.1, 3.1, 5.1, 8.1, 10.1, 11.2, Fig 1, Fig 2 — "slides shrunk into a book page."
7. **Qualification often survives only in the caption.** 2.2 (operating points), 6.2 (synthetic), 8.2 (per-GPU handled well), 11.3 (bound). The "prefill compute-bound / decode bandwidth-bound" rule is defensible in prose but re-hardens into an unconditional statement in figures (2.1, 2.2, 11.3). PASS 7 is not satisfied on the figure side.
8. **Aggregate-as-fungible-pool recurrence** in 7.4 and 7.5 (the two most important memory figures) — despite the red "aggregate ≠ per-rank" warning in 7.4, the bars themselves still read as one heap; no per-rank 80 GB gridline anywhere.

---

## 7. VISUAL REVISION PRIORITY

**P0 — visible publication defects (overlap, clipping, unreadable essential labels, misleading relationships):**
- **Figure 10.2** (clipped labels, ~6–8 pt) — fix first.
- **Figure 7.1** (clipped top rectangles of all stacks; no visual MHA comparison).
- **Figure 11.3** (label/GPU overlaps; contradictory output arrow; unqualified bound).
- **Figure 2.1** (labels behind boxes; connector through annotations; color-only data/compute/KV).
- **(figs 7.3/7.4/7.5/5.1/6.2/8.2/12.1 also carry P0-grade overlaps — prioritize within the MAJOR batch.)**

**P1 — foundational figures whose weak design damages an important mental model:**
- 7.4 and 7.5 (aggregate ≠ per-rank message undermined by the visual).
- 8.2 (prefill intensity misposition), 11.1 and 11.2 (batching/serving comparisons not on a common basis; stack contradiction), 10.1 (composition under-specified, CP missing), 4.1 (false bijection), 3.1 (equal-box equivalence), 5.1 (ladder/labels).

**P2 — substantial improvements to comprehension/professionalism:**
- 6.1, 6.2, 7.2, 7.3, 8.1, 9.1, Fig 1, Fig 2.

**P3 — optional polish:**
- 1.1, 1.2 (already clean). Page 6 reflow (whitespace).

---

## 8. TABLE / PAGE-COMPOSITION ISSUES

- **Table 4-3 (canonical provenance, page 41):** the **Monthly budget** cell is ~10 lines of prose inside a table (should be a footnote); no interior rules, so the tall cell breaks Field/Value pairing; multi-line values wrap **without a hanging indent** (continuation lines flush with column start → hard to see value end); KV-price and TTFT rows break mid-parenthetical ("~24.1 GB @ / 9.2K)", "~1.08 / s); p95 ≤ 2 s"); the **users** figure (~2,000) is not in the table — only rps appear in the note — undermining "single reference set" self-containment. Otherwise the table is a strong provenance anchor, units consistent.
- **Table 2-1 / 8-1 (per-token FLOP / prefill PFLOP):** consistent with Ch 8; verify units "PFLOP" vs "PFLOPS" never collide (they refer to work vs rate — keep the distinction explicit).
- **Table 3.2:** "~0.20× (~5× less)" and active fraction ~30% are consistent; the foot-note correctly calls out the contrast with Appendix-A frontier MoEs.
- **Page-level:** page 6 (Fig 1.2) is a mostly-empty page (large white above/below); Fig 12.1 sits at the very bottom of page 135; several figures sit centered with large outer margins (5.1, 10.1) giving a floating appearance. No widows/orphans or stranded headings were observed in the text pages as rendered. Header/page-number/rule collisions: none observed.

---

## 9. PRIORITIZED REVISION PLAN (by impact, not chapter order)

1. **Fix the P0 figure defects** (10.2, 7.1, 11.3, 2.1) — overlap/clipping/unreadable labels. (Fixes publication gate.)
2. **Add redundant (non-color) encoding across the color-only figures** (7.1, 7.4, 7.5, 4.1, 5.1, 8.1, 10.1, 10.2, 11.1, 11.2, 11.3, 12.1, 3.1, 6.1, 2.1) — hatch/pattern/linetype/text labels so grayscale works.
3. **Make the aggregate ≠ per-rank point visual** in 7.4/7.5 (per-rank 80 GB lines / sharded-KV marker). This is the book's best idea and its figures currently fight it.
4. **Fix figure-side quantitative integrity:** 8.2 (prefill at true intensity), 9.1 (10⁴ tick, out-of-range reference), 6.2 (mark synthetic), 11.3 (per-GPU/aggregate + bound-vs-starved), 12.1 (per-host vs system denominator).
5. **Reconcile the FP8–KV figure** (1.31 vs 1.42 MB/token) across Ch 1/7/12 and state which the ~33-slot figure uses; document it in Table 4-3 or a note.
6. **Rework the box-arrow-prose figures** (4.1, 5.1, 10.1, 10.2, 11.2, 12.1) so geometry encodes the relationship (matrix, link graph, comparison-on-common-scale) rather than repeating prose.
7. **Qualify the compute-/bandwidth-bound rule in-figure** (2.1, 2.2, 11.3) so PASS 7 holds; consider a soft/hedged ridge.
8. **Table 4-3** cleanup (move Monthly budget to a footnote; hanging indent; fix mid-expression breaks; add users field).
9. **Terminology:** unify host/node/instance/GPU-node; assert TPOT canonical (ITL as instant); one-line query disambiguation.
10. **Qualify the Ch-3 KV formula** as full-MHA special case.

---

## 10. PUBLICATION ASSESSMENT

The manuscript is **not publication-ready.** The prose and the arithmetic of pages 1–155 meet a high standard — the canonical scenario is internally consistent, derivations recompute correctly, derived/measured/illustrative are separated, and the kernel-regime-vs-capacity distinction is honored in the text. But the **figure floor fails the mandated standard**:

- 17 of 25 numbered figures (68%) are MAJOR REVISION or REDESIGN; only 2 are KEEP.
- At least one figure (10.2) has **literally clipped, unreadable labels**, and several others (7.1, 11.3, 2.1, 7.4, 7.5) show text hidden behind or overlapping structural elements.
- A large fraction of figures rely on **color-only encoding** (grayscale failure) and on **box-arrow-prose** that adds little over prose.
- Several figure-side quantitative/semantic inconsistencies (8.2 prefill intensity, 9.1 out-of-range annotation, 11.3 bound-vs-starved + per-GPU ambiguity, 12.1 per-host/system mixing) and an FP8–KV figure conflict (1.31 vs 1.42 MB/token) remain.

Per the review prompt, a manuscript with even one obvious rendered-figure defect is not publication-ready; this slice has many. The next pass should focus on the P0 defects and the color/grayscale and aggregate-vs-per-rank systemic issues, then re-verify at rendered size before any publication claim.

---

## FINAL QUALITY GATES — A–N

- **A. Read the complete manuscript rather than sampling?** YES — prose of pdf pages 0–154 (book pages −21…133, chapters 1–12) read in full via extracted text; all 25 figures in the slice rendered and inspected.
- **B. Independently checked the major numerical chains?** YES — 2.62/0.33 MB/token, 24.1/24.9/84/335 GB KV, 229/288/539 GB, 436 GB budget, 18/33 concurrency, 1.29 PFLOP→1.19 PFLOPS, 5.6 TB/s, ridges 295/206, in-flight 344, price 20/hr→14.6K/mo all recomputed and confirmed (with the one FP8 1.31-vs-1.42 issue noted).
- **C. Separated theoretical/derived/illustrative/vendor/measured?** YES — the book does this well; noted Fig 6.2 as the one under-labeled illustrative chart.
- **D. Checked canonical scenario cross-chapter consistency?** YES — stable across Ch 1,2,4,5,7,8,11,12; no contradictions; FP8 per-token figure is the one open item.
- **E. Evaluated every major section for storyline value?** YES — sections assessed; no removal-worthy content; mini-case endnotes occasionally re-assert rather than advance (compressible).
- **F. Actually inspected every rendered figure individually at normal scale?** YES — 25 figures rendered at 200–400 dpi and inspected pixel-by-pixel (no contact-sheet, no caption-only inference).
- **G. Explicitly reported every numbered figure incl. passers?** YES — 25 entries, including KEEP for 1.1/1.2.
- **H. Checked each figure for collisions, tiny type, weak hierarchy, ambiguous arrows, misleading semantics, caption dependence, grayscale robustness?** YES — itemized per figure (§5, §6).
- **I. Asked whether each figure deserves to exist?** YES — PASS-15 applied; none recommended for removal* (10.2 recommended for REDESIGN, not removal), but 4.1/5.1/10.1/11.2/12.1 flagged as box-arrow-prose at risk if not reworked.
- **J. Checked tables and page composition at rendered size?** YES — Table 4-3 issues (§8); page 6 whitespace noted.
- **K. Looked for terminology drift globally?** YES — host/node/instance identified (§4); TPOT/ITL, rps, request/query discussed.
- **L. Challenged plausible-but-unestablished conclusions?** YES — 11.3 bound/starved, 12.1 per-host/system, 8.2 prefill placement, 7.4/7.5 aggregate-fit.
- **M. Identified correct-but-low-value sections?** YES — mini-case re-statements (Ch 2, Ch 5) as compressible.
- **N. Avoided lowering the standard because the manuscript is much improved?** YES — the figure floor is judged against the mandated standard, not relative improvement.

**Conclusion: NOT publication-ready.**
