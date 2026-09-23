# PASS 25 — ADVERSARIAL PUBLICATION REVIEW — PDF pp 1–155 (chapters 1–12, plus Preface Fig 1–2)

**PDF:** `render/build/from-token-to-fleet-v20260913.pdf` (307 pp)
**Slice:** pymupdf pages 0–154 (PDF pages 1–155). Book page = PDF index − 21.
**Method:** every numbered figure in the slice was rendered to PNG at ~400 dpi (page + tight figure crop) with pymupdf; vector figure labels were judged from the rendered pixels (the figure text is vector, not in the PDF text layer), with targeted pixel ink-extent/color-band measurement to corroborate every clipping/overlap/whitespace claim. The prose/terminology/numerical items were verified against the PDF text layer and recomputed independently. Prior-pass defects and the latest fix batch were each re-checked as CONFIRMED-FIXED / PARTIAL / NOT-FIXED.

**Figure verdict counts (24 numbered figures in slice):** KEEP **1** · POLISH **15** · MAJOR REVISION **8** · REDESIGN **0** · REMOVE-MERGE **0**.
**Findings by severity:** P1 **2** · P2 **21** · P3 **13** · P0 **0**.

---

## 1. OVERALL ASSESSMENT

This slice is **not publication-ready**, but the blocker is no longer the hard, unreadable "clipped-label" class of defect from the previous pass — that has largely been resolved. The remaining problem is a **concentration of P2-level figure problems and two P1 consistency/correctness items**:

- The one unresolved quantitative-integrity figure defect from prior passes (Fig 8.2 mis-plotting prefill at ~300–400 FLOP/byte instead of ~9,200) is **still not fixed**, and the promised "ANALYTICAL" tag is missing from 8.2.
- A **cross-chapter numerical inconsistency** remains: the host throughput bound is still computed as **C/W = 18 ÷ 8.6 s ≈ 2.1 req/s** (page 68), after the book elsewhere corrected the KV concurrency to **C ≈ 17.5** (→ C/W ≈ 2.0). The two are mutually inconsistent, and the 2.1 value propagates into host/fleet sizing.
- The per-rank (80 GB) **"aggregate ≠ per-rank" message** that the book's best memory figures (7.4, 7.5) are meant to carry is still conveyed by a footnote/label rather than **native** bar geometry; and **labels still sit inside hatch/dot fills** (7.4) and overlap the bars they annotate (7.5).
- Color-only encoding remains widespread (grayscale-insecure), and several figures are still box-and-arrow prose (4.1 especially, plus 11.2 which contradicts its own "not a stack" thesis with a through arrow).

**What is genuinely fixed and should be credited:** the Preface Fig 1 decision-loop redesign (clear return arrow), Preface Fig 2 (two explicit reading paths), Fig 2.1 label/connector fixes, Fig 2.2 bottom-band rebuild, Fig 10.2 → clean typeset Table 10-1 (the former P0 clipped labels are gone), Fig 12.1 condensation + X-REJECTED, Fig 7.2 resize + attention-geometry retitle, Fig 9.1 ANALYTICAL [DERIVED] tag + complete log ticks, Fig 6.1 direction-on-connectors, Fig 11.3 output-arrow direction / KV-label clearance / qualified footer, Fig 6.2 [ILLUSTRATIVE] mark, the **FP8 1.31-vs-1.42 reconciliation**, and **C = 17.5**. The prose/arithmetic of chapters 1–12 remains strong and internally consistent apart from the C/W item; the canonical scenario (70B FP16, 9.2K/300, TTFT 1.2 s, TPOT 25 ms, 8×H100 640 GB, $2.50/GPU-hr) is stable.

---

## 2. FIGURE-BY-FIGURE AUDIT

> Verdict scale: KEEP / POLISH / MAJOR REVISION / REDESIGN / REMOVE-MERGE.
> Each entry marks the item as **CONFIRMED-FIXED**, **PARTIAL**, or **NEW**.

### 2.1 Preface Fig 1 — architect's decision loop (PDF p14) — **KEEP** — *CONFIRMED-FIXED (REDESIGN resolved)*
- Status: The redesign is now sound. A thick red loop runs down the right margin from stage 04 back into the top-right of stage 01 **with a solid arrowhead**, encoding the iteration → re-characterize loop. The "define / size / justify" labels sit beside the shafts, clear of the boxes; the right-hand cue words (inputs/design/economics/decide) sit inside their boxes with padding; no pill-on-border clipping; no tiny (<8 pt) type; stage identity is carried redundantly by number + title text (not color-only). No dashed-solid convention remains, so no legend is required.
- Residual (P3, not binding): the four stage identity colors and the italic cue words are color-matched with no key, but text redundancy covers it. **No change required.**

### 2.2 Preface Fig 2 — reading the book two ways (PDF p15) — **POLISH** — *CONFIRMED-FIXED (redesign) + NEW minor defects*
- Status: Two large, explicit, clearly separated paths are now shown — **A · LAYER-BY-LAYER (Parts I→VI)** and **B · QUESTION-BY-QUESTION** — with distinct headings, palettes (blue vs red), card content and footer captions. This is the requested redesign.
- **NEW (P3):** In both columns the **bottom-most card is not terminated by a reading arrow** (the shaft stops below the second-to-last card, leaving the last card unconnected), and the **up-arrows** (pointing up in a top-down I→VI stack) make the intended start/end direction ambiguous; the footer captions are the smallest type on the page.
- Recommended change: attach arrowheads to the last card in each column and orient the reading arrow from the intended start card; enlarge the footer captions slightly.

### 2.3 Fig 1.1 — decoded token adds one K+V per layer/head (PDF p23) — **POLISH** — *NEW minor (was KEEP)*
- Status: The core message is clean and left-to-right. But on the rendered page the **right-hand "Next token Q" sub-label ("reaches every past K,V") sits at/very near the box's right border**, the "read all" annotation is pill-rescued over the connector, the four incoming token lines are **U-turn-routed** (token1/token2 up-and-over / down-and-under) which mildly obscures that every token writes into the cache, the three semantic regions are **color-only** (grey=token, purple=KV, orange=Q), and the secondary descriptors are small.
- Why it matters: borderline readability at print scale and a color-only 3-region encoding. This is not a hard blocker (no truncation), but at the requested standard it is flag-worthy.
- Recommended change: pad the right box, straighten the four connectors (or add "each token →" labels), add pattern/text redundancy for the three regions, bump secondary descriptors.

### 2.4 Fig 1.2 — text → tokenizer → IDs → embedding → attention → KV cache (PDF p24) — **POLISH** — *NEW minor + page-composition*
- Status: The 5-stage pipeline is sound. Minor: the tertiary descriptors ("characters/corpus-driven/ordered/one vec per token/vs past/per layer x head") are the smallest type in the figure; the **Token IDs→Embedding "lookup" connector is a long down-and-across detour** that reads more like a feedback loop than a direct dependency; the two purple boxes (Embedding and KV Cache) share the same fill so they are text-differentiated only.
- **Page-composition (verified by pixel measure, P3):** the figure sits high on the page leaving **≈33% of the page height empty at the bottom** (ink rows 125–1588 of 2376 px). Prior pass flagged this as page-6 whitespace; it persists.
- Recommended change: collapse the page whitespace (reflow the figure lower / tighten), route Token IDs→Embedding more directly, differentiate Embedding vs KV Cache beyond text.

### 2.5 Fig 2.1 — canonical inference pipeline (PDF p31) — **POLISH** — *PARTIAL (layout fixes confirmed)*
- Status: **CONFIRMED-FIXED:** step labels are now padded inside their boxes (no text behind/on borders), and the long "first token" vertical connector is rerouted to the right margin **clear of** the "one-shot burst…" annotation, the "KV cache: created in prefill…" note and the DECODE title; no arrow crosses a label; no <8 pt type.
- **NOT-FIXED (P2):** data/model/KV state are still distinguished **by fill color only** (grey/blue/orange palette + legend swatches) — a grayscale print loses the category; and the prefill stage is still drawn as a **strict 5-step serial chain** while the caption says "parallel across prompt positions," so the parallelism is only conveyed by prose.
- Recommended change: add hatch/shape/text redundancy for the three categories; add a parallel indicator (stacked glyph or note) so the chain is not read as serial prefill.

### 2.6 Fig 2.2 — arithmetic-intensity continuum (PDF p35) — **POLISH** — *PARTIAL*
- Status: The bottom band is rebuilt into two clear bands (**memory-bound / compute-bound**) with both operating points now placed correctly — the **prefill point sits on the high-intensity compute side** to the right of the ridge with a "~9.2K FLOP/byte" annotation (the prior "marker at/beyond the ridge" defect is fixed), and the caption + top banner now carry the "operating points are NOT fixed" qualification. The regime-capacity separation is also handled by the "single-H100 capacity insufficient" table under the caption.
- **NOT-FIXED (P2):** there is still **no numeric/log intensity axis** (just a qualitative "lower → / → higher" arrow), the ridge is still a **single hard dashed line** labelled "~295" (reads as an exact law rather than a soft boundary), and the **top banner text ("…kernel/hardware all move a point across the ridge") is intersected by the dashed ridge line** — a label/line overlap. Small grey secondary text remains.
- Recommended change: add a log intensity axis (or explicitly label "conceptual, not to scale"); soften/hedge the ridge; move the banner text off the ridge line.

### 2.7 Fig 3.1 — dense vs MoE parameter allocation (PDF p50) — **MAJOR REVISION** — *PARTIAL*
- Status: **CONFIRMED-FIXED:** the two panels are now **aligned side-by-side** with legends and explanatory copy under each panel (no interior-gutter text), and the MoE experts are explicitly **E1–E8** with a "top-2 active" sub-head and a red box around the two active experts. (A "clipped red banner" at the column bottoms reported by an earlier image read was **disproven** by pixel-color-band analysis — no such banner exists; disregard that.)
- **NOT-FIXED (P2):** active vs inactive experts are still distinguished only by **fill color** (orange vs pale grey) — no hatch/pattern/texture redundancy, so grayscale is marginal; and the **visual scaling is mismatched** — the dense side is 24 small squares while the MoE side is eight much larger boxes, inviting a false "dense has more stuff" equivalence (PASS 6).
- Recommended change: add an ACTIVE hatch/pattern to the two active experts; normalize or annotate the block representation ("not to scale") so the 24-squares vs 8-boxes geometry doesn't imply equivalence of unlike units.

### 2.8 Fig 4.1 — six workload dimensions → consequences (PDF p66) — **MAJOR REVISION** — *NOT-FIXED*
- Status: Unchanged from prior pass and not in the fix batch. Six rows of **one-to-one parallel** blue→orange arrows read as a **bijection / exclusive pairing** even though the relationships are interdependent (the prose says many-to-many); there are **no "Workload dimension" / "Architectural decision" column headers**; coupling/strength is not encoded; it is box-and-arrow prose; blue/orange is color-only (no header redundancy).
- Why it matters: PASS 5/6 — the geometry teaches an exclusive mapping that the text explicitly denies.
- Recommended change: replace with a matrix (dimension × decision with weighting/strength marks) or a many-to-many link graph; add the two column headers.

### 2.9 Fig 5.1 — model-selection ladder (PDF p79) — **POLISH**
- Status: Improved and readable; the flow is clear; no arrows cross labels; edge labels ("drives", left "split", "context", "answer") are legible and on/near their shafts. Residual (P3): the **generation-leg "split" label sits in the right-hand gutter, off the arrow it annotates** (association ambiguous); the "quality·latency·KV·$/tok·RAG" second line is **tight against the box's bottom edge**; the two green boxes (Workload and Generation leg) share a hue; and the figure sits in a **large empty margin** (slide-like).
- Recommended change: move the second "split" onto its shaft; pad the second line; differentiate the two green nodes; reduce page whitespace.

### 2.10 Fig 6.1 — metric-hierarchy diagnostic chain (PDF p82) — **POLISH** — *CONFIRMED-FIXED*
- Status: **CONFIRMED-FIXED:** direction is now encoded by **arrowhead orientation** (solid green down-arrows = causation on the left, dashed red up-arrows = diagnosis on the right), not by legend alone; sub-titles are legible. Residual (P3): the explicit "causation ↓ / diagnosis ↑" wording still lives in the prose key rather than inline on the connectors, color is still used for the two flows, and the clean ladder implies a stricter linear causality/diagnosis than real systems have.
- Recommended change: label the connectors inline; consider a note that diagnosis is multi-hop.

### 2.11 Fig 6.2 — latency distribution (PDF p84) — **POLISH** — *PARTIAL*
- Status: **CONFIRMED-FIXED:** the plot now carries an explicit **"[ILLUSTRATIVE synthetic profile]"** disclosure under the title. 
- **NOT-FIXED (P2):** the "latency cleanup" was not done — the x-axis is still **0–6 s with ~55–60% blank** (the mass is compressed into the left ~15%), the **p50/p90/p95 labels still overlap one another and the tallest bars**, **p99 is not labelled on the axis** (only in the text box), and the pink "1% stragglers" band still has **no in-figure legend**.
- Recommended change: truncate/break the axis to ~2 s; stagger or leader the percentile labels; label p99 and the SLO line; add a straggler-band key.

### 2.12 Fig 7.1 — GQA cuts per-token KV (PDF p96) — **MAJOR REVISION** — *PARTIAL*
- Status: **CONFIRMED-FIXED:** the top-most query-head rectangles are now complete (no top-edge truncation; the cap is a clean bracket), and call-out/corridor labels no longer overlap.
- **NOT-FIXED (P2):** the **MHA side is still absent** — only the GQA geometry is drawn, and the 8× saving is asserted in the call-out text ("MHA: 64 K/V → 2.62 MB/token" vs "GQA: 8 K/V → ~0.33 MB/token") rather than shown as a paired MHA vs GQA graphic, so the 8× is not visually evident; and **group identity is hue-only** (8 colors, no shape/pattern/label on each head stack), so grayscale loses the mapping.
- Recommended change: draw both MHA (64 K/V) and GQA (8 K/V) side-by-side on a common geometry; add redundant group labels/patterns.

### 2.13 Fig 7.2 — KV vs context, attention geometry (PDF p100) — **POLISH** — *CONFIRMED-FIXED*
- Status: **CONFIRMED-FIXED:** the legend is now **outside/ below the axes and legible**, the title now frames the comparison **"by attention geometry (full-MHA vs GQA)"**, the two "9.2K ≈ …" call-outs sit in clear white space with arrow leaders, and the log ticks are readable. Residual (P3): the two-line GQA call-out is the densest text and its leader crosses the FP8 line; series are continuous log–log lines through 4 markers (illustrative precision). The FP8 line is correctly labelled "byte-halving bound, ~1.3 MB/tok" (the theoretical bound), consistent with the reconciliation in §3.
- Recommended change (minor): annotate "illustrative points, not measured curve."

### 2.14 Fig 7.3 — inference vs fine-tuning floor (PDF p101) — **POLISH**
- Status: Improved — the red annotation no longer overlaps the title and the "~1120 GB" label is not on the spine (clear headroom); the three bars (~165 / ~1120 / ~60 GB) read correctly. Residual (P3): the three hardware threshold lines are **color-only with the same dash style** (grey/dark-blue/green dashed), the legend still sits **inside the plot area**, and the x tick labels are two-line and tight.
- Recommended change: give the threshold lines distinct linestyles/patterns; move the legend outside; pad the x labels.

### 2.15 Fig 7.4 — concurrency budget, 640 GB pool (PDF p102) — **MAJOR REVISION** — *PARTIAL*
- Status: **CONFIRMED-FIXED (numbers):** the koncurrency is now **"C ≈ 17.5 concurrent requests @ FP16"** and the FP8 row gives **"~32.4 slots (436 ÷ 13.448 GB/request)"** — both correct and consistent with §3 (436 ÷ 24.9037 = 17.51; FP8 uses the measured 1.42 MB/token → 13.448 GB/request). The red "AGGREGATE RESIDENCY SCREEN ≠ PER-RANK FIT GUARANTEE" banner is cleanly separated from the "scenario reserve" call-out (no overlap — verified by pixel stacking: banner → blue "~436 GB KV" line → call-out box).
- **PARTIAL (P2):** the per-rank geometry is **not native to the bars** — the two main budget bars are still one fungible 0–640 GB continuum; the 80 GB per-rank notion appears only as a small **eight-cell ruler** at the bottom ("8 × 80 GB per-rank pool") plus faint low-contrast dotted verticals and a footnote. 
- **NOT-FIXED (P2):** the **"140 GB weights" and "KV budget ~436 GB" labels are white/dark text sitting directly on diagonal-hatch / dot fills with no padding** (pattern runs through the glyphs) — reduced legibility; and FP16 vs FP8 rows are distinguished by colour/lightness + subtle pattern only (color-first).
- Recommended change: draw the bars broken into **eight 80 GB per-rank cells** (or add prominent per-rank 80 GB gridlines) so "aggregate ≠ per-rank" is in the geometry; back the value labels with white/halo padding; add non-colour FP16/FP8 redundancy.

### 2.16 Fig 7.5 — Memory Tetris, three contexts (PDF p103) — **MAJOR REVISION** — *PARTIAL*
- Status: **CONFIRMED-FIXED:** the **32K bar is no longer split** into two separated rects (it is one contiguous column), and the 80 GB notion is now present as **horizontal "80 GB rank boundary" rules** + a "640 GB = 8× 80 GB ranks" subtitle. 
- **PARTIAL (P2):** the per-rank caveat is expressed as a global scale annotation, not **native per-rank sharding on the bars** — the bars are still aggregate host columns.
- **NOT-FIXED (P2):** the red KV labels still overlap the bars — "**24.9 GB KV**" sits on the top edge of the 9.5K bar and "**84 GB KV**" sits on an 80 GB rule **over the bar fill**; only "335 GB KV" is clear.
- Recommended change: move the KV labels above the bars with leader lines; optionally draw per-rank caps on the bars.

### 2.17 Fig 8.1 — memory/compute hierarchy (PDF p108) — **POLISH**
- Status: Not in the fix batch. The ladder and right-hand small·fast·close → large·slow·far gradient are correct. Residual (P2/P3): the secondary labels ("fastest·smallest", "arithmetic units", "on-chip·close", "large·slower", "farthest") are **small and close to the box bottom**; the seven rungs are tightly stacked; the blue/orange/green grouping is **color-only with no in-figure key**; and the "higher=better" ladder metaphor is misleading because the top rung is the **scarcest** resource (registers/SRAM), not the best.
- Recommended change: add a key for the colour grouping; enlarge secondary labels; retitle the vertical axis as a speed↔capacity↔distance gradient rather than a hierarchy.

### 2.18 Fig 8.2 — per-GPU roofline (PDF p112) — **MAJOR REVISION** — *NOT-FIXED (critical item)* — P1
- **NOT-FIXED (P1):** the "**prefill 9.2K**" point is still drawn at **≈300–400 FLOP/byte** on the compute plateau (just past the H100 ~295 ridge) instead of at its true **≈9,200 FLOP/byte**. The log x-axis caps at 10³, so the true intensity is off-scale; the fix (annotate "off-scale at ≈9.2K, shown just past ridge" or place it at true intensity) was not applied. A reader is led to read prefill as "barely past the ridge" when it is ~31× the ridge intensity. This is the same quantitative-figure-integrity defect flagged previously and it **remains**. (The categorical "prefill is compute-bound" survives, but the magnitude is badly understated.)
- **NOT-FIXED (P3):** the promised **[ANALYTICAL] tag is absent** — only "DERIVED [1P: vendor datasheet]" appears in-plot. (Fig 9.1 does carry ANALYTICAL; 8.2 does not.)
- Also verified OK: "decode batch=1" no longer overlaps the memory-bound slope text; the "ridge ≈ 295" label sits below the roof, not on it; the legend is not under the watermark.
- Recommended change: move the prefill marker to its true intensity (or extend the axis) and add an "[ANALYTICAL][DERIVED]" in-plot tag.

### 2.19 Fig 9.1 — all-reduce time vs volume (PDF p120) — **POLISH** — *CONFIRMED-FIXED*
- Status: **CONFIRMED-FIXED:** the in-plot tag **"ANALYTICAL [DERIVED] (t ∝ 2·V/B)"** is present, the y-axis now shows the **full decade series 10⁰…10⁶ with no missing 10⁴**, and the legend is below the axes (not cramped). Residual (P3): the **"140 GB (70B weights)"** reference is still an **analytical extrapolation** beyond the last measured marker (~41 GB), but it is now tagged ANALYTICAL/DERIVED, so the precision concern is largely addressed; consider marking the dashed reference explicitly "extrapolated."

### 2.20 Fig 10.1 — composing parallel dimensions (PDF p128) — **POLISH** — *improved*
- Status: Substantially reworked and much better. One PP stage container → 2×2 DP×TP mesh (GPUs labelled with DP/TP ranks), an EP overlay spanning **all four** GPUs (not just GPU B), an explicit TP weight-shard banner, and a summary table that now includes **CP (opt)**. Labels are proportional and legible; grouping is not color-only (each labelled in text); no slide-like margins. Residual (P3): reading order is a conventional top-down not a single forced path; EP is drawn as a full-width banner rather than visually overlaid on the GPU boxes; the six-content summary table duplicates the standalone table in §4.
- **Note (redundancy, P3):** the embedded "dimension / PARTITIONED / REPLICATED / COMMUNICATION" summary table in this figure repeats the content of the standalone typeset "Strategy / What splits / Replicated / Communicates" table (PDF p133) and partly overlaps Table 10-1 (p129). Consolidate (see §4).

### 2.21 Fig 11.1 — discrete vs continuous batching (PDF p138) — **MAJOR REVISION** — *NOT-FIXED*
- **NOT-FIXED (P2):** the "**a finishing sequence frees its slot immediately**" call-out **overlaps the green squares** in row 3; and **time is encoded orthogonally across the two panels** — discrete batching uses horizontal extent (time in the batch window) while continuous batching uses a vertical up-arrow, with **no common baseline/scale** between the panels, so utilization/idle are not directly comparable (PASS 10 fails). Sequence identity is color-only with no legend.
- Fixed sub-item: "next batch waits" no longer sits on the grey box border (it is outside, with a leader).
- Recommended change: ring the call-out off the squares; give both panels a common time axis / common baseline; add a sequence-colour legend.

### 2.22 Fig 11.2 — four serving concerns (PDF p143) — **MAJOR REVISION** — *PARTIAL + NEW defect*
- **CONFIRMED-FIXED:** the four concern names are now enlarged and bold (REUSE, REQUEST SCHEDULING, STATE MANAGEMENT legible).
- **NEW (P2, caused by the enlargement):** the **"RESOURCE SPECIALISATION" header text overruns its orange header bar** — the bar is too short, so the leading **R** and trailing **N** are split across the bar edge (white-on-orange vs white-on-pale-grey), verified at high zoom. Readable but visually broken; the "enlarged names" fix over-ran this bar.
- **NOT-FIXED (P2):** the **single central top-to-bottom arrow** still implies a linear request→concerns→output pipeline, **contradicting the figure's own "not a stack" hypothesis**; the **containment box** ("THE FOUR SERVING CONCERNS") still implies layering; the four concerns are distinguished **color-only** (green/orange/purple/red headers); body copy is small relative to the enlarged headers with tight padding.
- Recommended change: shrink/pad the RESOURCE SPECIALISATION header (or widen the card); recast the through-arrow as a fork ("request stream passes through all four in parallel"); drop the containment box or re-label it; add a legend/pattern redundancy.

### 2.23 Fig 11.3 — P/D disaggregation (PDF p144) — **POLISH** — *CONFIRMED-FIXED*
- Status: **CONFIRMED-FIXED:** the output arrow now points **down/out of the decode pool** toward "tokens out to client" (direction consistent with the label); the "KV CACHE TRANSFER" label is clear of the GPU squares; the ownership note sits in the inter-pool space **clear of** the double arrow and decode GPUs; "steady token generation / high bandwidth" is clear of the decode GPUs; and the footer is now **qualified** — "[ILLUSTRATIVE][DERIVED]" with comparative per-GPU framing ("~1.19 PFLOPS vs 0.989 peak single-H100", "5.6 TB/s vs 3.35 TB/s") rather than an absolute bound.
- Residual (P3): the transfer arrow is still **double-headed** while the note describes a **one-way write-then-read** ("prefill WRITES … decode READS … KV moves once"); and the "tokens out to client →" uses a right-pointing glyph beside a vertical arrow.

### 2.24 Fig 12.1 — candidate architecture synthesis (PDF p154) — **POLISH** — *CONFIRMED-FIXED*
- Status: **CONFIRMED-FIXED:** the figure is **condensed** (stage ④ body no longer tiny), candidate lines are separated (no run-together), the outcome row now has a distinct **"✗ REJECTED"** box **visually separated** from "⑤ OUTCOME — SURVIVORS", and status is carried by **✓/✗ text symbols** (not color-only). No 164/165 run-together or caption truncation.
- Residual (P3): the "**~19.8K << ~92K needed**" comparison still does not define the ~92K baseline or state whether it is per-host or system-wide demand; the cost comparison ("1 host ≈ $14.6K/mo ✓" vs "2 hosts + fabric (~2× capex)") has no common cost axis.
- Recommended change: define the ~92K baseline and its denominator; put both outcomes on a common cost axis.

---

## 3. CONCEPTUAL / TERMINOLOGY / NUMERICAL FINDINGS

- **P1 — C/W inconsistency (page 68, book ~46, Ch5 workload/model-selection): NOT-FIXED.** The text still reads "a single 8×H100 host serves **~2.1 req/s** at full modeled utilization, i.e. **C/W = 18 KV-resident requests ÷ 8.6 s**." After the correction elsewhere (C ≈ 17.5; integer ceiling 17), this bound should be **C/W = 17.5 ÷ 8.6 ≈ 2.0** (or 17/8.6 ≈ 1.98). As written it is internally inconsistent with the corrected concurrency (page 94+), and the 2.1 value feeds into the host/fleet count (~24 hosts). **Fix this value (and propagate) — it affects an architecture decision.**
- **CONFIRMED-FIXED — FP8 per-token reconciliation.** The book now explicitly separates the **measured** FP8 KV footprint (~1.42 MB/token, ≈54% of BF16, vLLM including per-token metadata, [1P][FACT]) from the **naive byte-halving lower bound** (~1.31 MB/token = 1.25 MiB), and uses ~1.42 MB (→ 13.4 GB/request) as the operating value throughout while quoting ~1.31 MB only as the theoretical bound. Fig 7.2's "byte-halving bound, ~1.3 MB/tok" label and Fig 7.4's "13.448 GB/request → ~32.4 slots" are consistent with this. (Checked: 2,621,440/2 = 1,310,720 B = 1.31 MB = 1.25 MiB ✓; 1.42 MB × 9,500 = 13.49 GB ✓; 436 ÷ 13.448 = 32.4 ✓.)
- **CONFIRMED-FIXED — C = 17.5 not 18.** Stated as "C ≈ 17.5 concurrent requests (byte-accurate 436 ÷ 24.9037 = 17.51; the conservative integer 'requests that fit' ceiling is 17, not 18)".
- **P2 — host / node / instance / GPU-node still used interchangeably (NOT unified).** e.g. "single node vs multi-node", "8×H100 cloud instance", "$20/hr per 8-GPU node", "per 8×H100 host", "8×H100 node's 640 GB HBM". Recommend one canonical term ("host") with an explicit "= 8×H100" definition at first use.
- **P3 — Ch 3 §3.4.3 KV formula: only partially qualified as full-MHA.** §3.4.3 writes "scales with the canonical Chapter 1 formula, KVper-token = 2 × nlayers × dhidden × bytes-per-value" and uses it at ~1.3 MB/token for a 70B-class model, without an inline "(this is the full-MHA case; a GQA model uses n_KV-heads × dhead)" qualifier. The qualification does exist elsewhere (Ch 7 "the full-MHA special case (n_KV-heads × head_dim = hidden_dim)", and the canonical is declared full-MHA in Ch 3/4), so this is a local clarity gap, not an error. Recommend adding the parenthetical inline.
- **Cross-checks confirmed correct (no action):** 140 GB weights; 2.62 MB/token full-MHA; 0.33 MB/token GQA; 24.1/24.9/84/335 GB KV; 229/288/539 GB; 436 GB budget; prefill 1.288 PFLOP → 1.19 PFLOPS vs 0.989; decode 5.6 TB/s vs 3.35; ridges 295/206; "~256 KB/token for a 7B-class model" and "~1.3 MB/token for a 70B" are correctly **8-bit** figures (2×32×4096×1 = 256 KB; 2×80×8192×1 = 1.31 MB); FP8-residency 153 GB (140 + 13.4) and 8-bit 152 GB are consistent. No GB/GiB confusion.
- **Storyline/value:** sections 1–12 cohere; no removal-worthy content; the canonical-workload consistency holds apart from the C/W item.

---

## 4. TABLE / PAGE-COMPOSITION FINDINGS

- **CONFIRMED-FIXED — Fig 10.2 → typeset Table 10-1 (PDF p129).** The former P0 clipped-label matrix ("PP·pipelin", "CP·contex", "W weights (row…") is now a **clean 4-column typeset table** (Strategy / What it splits / Communication need / Fits when) with complete cell text, adequate column widths, a header rule, and no truncation. This removes the worst figure defect from the book.
- **P3 — Parallelism-strategy content is now triple-presented in Ch 10** (redundancy): (1) Table 10-1 "at a glance" (p129), (2) an **embedded** "dimension / PARTITIONED / REPLICATED / COMMUNICATION" summary table inside Fig 10.1 (p128), and (3) a **standalone** "Strategy / What splits / Replicated / Communicates" typeset table (p133). (2) and (3) are near-identical. Recommend keeping one comprehensive table and dropping/merging the others.
- **P3 (verified) — page 24 (Fig 1.2) leaves ~33% of the page empty at the bottom** (ink rows 125–1588 of 2376 px). Page 50 (Fig 3.1) and the Fig 5.1 page carry large empty margins around the graphic. Reflow for balance.
- **Positive:** Table 4-3 (canonical provenance) now lists the FP8 column (KV per token FP8 vLLM ~54% = 1.42 MB [1P][FACT]) and is internally consistent; no widows/orphans/stranded headings or header-footer collisions observed in the text pages.
- **Positive verified:** Table 10-1, the provenance table and the Ch 8 metric tables show no clipped or overflow cells.

---

## 5. CROSS-FIGURE SYSTEMIC ISSUES

1. **Color-only encoding remains the dominant systemic defect** — present in 2.1 (data/model/KV), 3.1 (active/inactive), 4.1 (source/target + no header text), 6.2 (color stands in but has text), 7.1 (8 group hues), 7.3 (threshold lines), 7.4 (FP16/FP8), 8.1 (on-chip/device/interconnect), 11.1 (sequence colours), 11.2 (four concerns), 6.1 (causation/diagnosis — partly saved by linestyle/arrows). **Grayscale / color-vision reading still fails on a large fraction of figures.** This is the most important book-level figure issue that remains.
2. **The "aggregate ≠ per-rank" message is still not native geometry** in 7.4/7.5 (the book's best idea is still carried by footnotes/rulers rather than by per-rank bar geometry).
3. **Labels sitting inside fills / overlapping their data** again appear in 6.2 (percentile overlap), 7.4 (labels on hatch), 7.5 (KV labels on bars), 11.1 (call-out over squares), 2.2 (banner over ridge). This is the residual "text/data collision" class.
4. **Box-and-arrow prose** persists (4.1, 11.2, and milder 3.1/5.1) — geometry that repeats prose rather than encodes the relationship.
5. **Qualification still caption/legend-resident** rather than in-figure in 2.2 (operating points), 6.2 (synthetic), 8.1 (hierarchy caution), 12.1 (denominator) — the bound/regime claims that the prose hedges tend to re-harden in the figures.
6. **Annotation-choice inconsistency:** the promised "ANALYTICAL" tag landed on 9.1 but not 8.2; the FP8 per-token figure (7.2) is a "bound" series while the operating values (7.4/Ch7 prose) use the measured 1.42 MB — this is now *labelled* correctly but a reader must reconcile the two series.

---

## 6. FINAL RISK ASSESSMENT

- **Publication readiness: NOT publication-ready.** The slice has no unreadable P0-clipped figure anymore (10.2 fixed), and the prose/arithmetic of chapters 1–12 is strong. But it is not publishable as-is because of: (a) the unresolved **Fig 8.2 prefill-intensity mis-plot** (P1, quantitative figure integrity), (b) the **C/W = 2.1-vs-2.0 inconsistency** (P1, affects host/fleet count), and (c) a **large P2 cluster** — 8 figures at MAJOR REVISION (3.1, 4.1, 7.1, 7.4, 7.5, 8.2, 11.1, 11.2) plus the widespread color-only and label-on-fill defects.
- **Strongest remaining risks:** the two P1 items (fig 8.2 intensity; C/W), and the fact that the two "important" memory figures (7.4/7.5) still visually assert aggregate-only fit. Fig 11.2 and 11.1 still teach the opposite of their captions.
- **Most likely to contain a subtle undiscovered problem:** the host/fleet arithmetic downstream of the C/W bound (the 2.1 value propagates to host count), and the FP8-vs-binary "8-bit" KV figures (two different per-token constants now reconciled but worth a final cross-check in Ch 17).
- **Recommended next pass:** fix the two P1 items; convert Figs 7.4/7.5 to per-rank geometry; break the color-only dependency via hatch/linestyle/text redundancy (biggest systemic win); rework Fig 11.2's arrow + RESOURCE SPECIALISATION bar, Fig 11.1's time axes, 3.1/4.1, and 7.1's missing MHA side; de-duplicate the Ch 10 strategy tables; unify host/node/instance; then re-verify at rendered scale before any publication claim.

---

## QUALITY-GATE SELF-CHECK
- Every numbered figure in the slice (24) rendered at high resolution and inspected from the rendered pixels (not captions/source). ✓
- Clipping/overlap/whitespace claims corroborated by pixel ink-extent/color-band measurement (e.g., Fig 1.2 page-24 whitespace 33%; Fig 11.2 header overrun; Fig 3.1 "clipped banner" disproven; Fig 7.4 banner/call-out overlap disproven). ✓
- The fix-batch items and previously-open conceptual items each re-checked and reported as CONFIRMED-FIXED / PARTIAL / NOT-FIXED, plus NEW findings surfaced. ✓
- Major numerical chains recomputed. ✓
- No findings manufactured; borderline/uncertain vision-model claims were either pixel-verified or dropped (e.g., the Fig 3.1 banner, the Fig 7.4 collision). ✓
