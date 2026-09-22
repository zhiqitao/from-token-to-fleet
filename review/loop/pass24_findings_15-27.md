# PASS-24 PUBLICATION AUDIT — PAGES 156–309 (Ch. 12 tail → Ch. 26 + Appendix A + back-matter)

Reviewer: Hermes subagent (mandatory rendered-page figure audit). Date: 2026-09-21.
Scope: PDF physical pages 156–309 of `from-token-to-fleet-v20260913.pdf` (0-indexed 155–308).
NOTE on chapter range: the assigned "chapters 15–27 + appendices" slice actually renders as
the tail of Ch. 12 (Fig 12.1 on p157), Ch. 13, Ch. 14, Ch. 15–26, then **Appendix A** (p288–298),
Glossary, References, Sources/Method, and the Architecture Worksheet (p299–309).
**There is no standalone body Chapter 27 in this render.** The `design/manuscript/chapter-27/`
directory is actually the **Appendix A** source; its four figure assets (fig-27-2701…2704) are labeled
**Fig A.1–A.4** in the book. If a separate professional-practice "decision-process" Ch. 27 was
intended, it is absent from this build — flag as a completeness item.

Method: every figure was rendered fresh at 200 dpi and inspected individually with vision analysis
(full-page + high-res zooms). Prose was extracted and the key numerical chains recomputed
independently.

---

## 1. OVERALL ASSESSMENT

**Strengths (strongly positive, already at high standard):**
- The core **numerical machinery is internally consistent and correct.** I independently
  recomputed, and all agree: prefill FLOP demand (40 rps × 9.2K × 2×70e9 = 5.15e16 FLOP/s; ratio
  = 6.5× host peak); decode MFU (12K×140e9/7.91e15 ≈ 0.21); KV per token (2×80×8192×2 = 2.62 MB/token
  = 2.5 MiB, correctly separating GB vs GiB); per-request KV (9,500×2.62 ≈ 24.9 GB; budget 436 GB →
  C≈18); the quadratic-attention share (+17% @9.2K, +60% @32K, ~2.4× @128K all verified); the entire
  **fleet-sizing matrix (Table 17-1, all 9 cells: H=⌈λW/(C·u)⌉)** — 344/552/860/1380/1720/2760 in-flight
  and 28/57/32/69/141/79/137/282/158 hosts all check out; the **ch16 TCO chain** (capex $5.8K/host→$116K,
  power 10.1kW→$22K, total $148K, $5.7/1K; cloud $72K→$2.8/1K; managed $20.8/1K; break-even
  $148K/$0.0208 = 7.1M req/mo; 70%-util $203K→$7.8/1K) all reconcile; the **agentic growth**
  (I(T): 10,365/12,095/12,960; KV 27.2/31.7/34.0 GB — text) and **interconnect** (5MB/20ms=2Gbps;
  φ·N·D/λnet = 0.8Gbps; the 50MB/φ0.5 case = 20Gbps burst, aggregate 5GB/s = 4× over 10Gbps) all align.
- The book **explicitly and correctly separates KERNEL REGIME from WORKLOAD CAPACITY DEFICIT** (Ch. 15 §4),
  and correctly rejects "MFU > 1" (the 6.5× demand is labeled a congestion check, not a utilization).
- **Evidence taxonomy is rigorous** — [1P]/[ILLUSTRATIVE]/[DERIVED]/[canonical scenario]/[2°] labels are
  used consistently; the Appendix A snapshot is date-stamped (2026-08-30) with a hard boundary note;
  Chapter 19 explicitly isolates the incremental orchestration model (β≈1.08×) from the full service
  time (W≈13.8 s) used for fleet sizing. These are exactly the discipline the review standard demands.

**Remaining weaknesses (blocking publication-readiness):**
1. **Multiple P0 rendered-figure defects** — visibly clipped/overlapping text in Fig 19.1, Fig 26.2,
   and Fig 23.1. Under the prompt's own rule ("a manuscript with even one obvious rendered-figure
   defect is not publication-ready"), the book is **NOT publication-ready**.
2. A **figure/prose numerical mismatch** in the capstone (Fig 26.2 vs Ch. 26 §4 text).
3. **Terminology/consistency collisions**: "six questions" (Table 23-1) vs a **five-gate funnel**
   (Fig 23.1); "tool-use success rate" carried as a lower-is-better target; "QPS" introduced in Ch. 26
   vs "rps" everywhere else.
4. Figure-value gaps: Fig 17.1 does not teach the three-factor sizing its caption claims.

---

## 2. HIGHEST-PRIORITY TECHNICAL / CONCEPTUAL ISSUES

- **[P1] "Six questions" vs a five-gate funnel.** Table 23-1 is titled "The six questions that turn any
  vague AI ask into architectable bounds" and correctly lists SIX (users/concurrency, inputs, "fast",
  "good", data sensitive, cost). But **Fig 23.1 renders only FIVE gates** and the prose (§23.7) says
  "six Socratic questions (problem, success, data, constraints, scope)" — naming only **five**. A
  reader cannot reconcile the six-question framing with the five-gate figure. Reconcile (either add the
  missing "quality" and "cost/TCO" surfaces to the funnel, or re-label to five).
- **[P1] Table 24-1 "Tool-use success rate" has an inverted-target semantics.** The row reads
  `0.61 → 0.44 → 0.32, target < 0.5` and the mini-case says "the tool-use success rate is 0.44%."
  A *success* rate should be maximized; the lower-is-better "target < 0.5", the *declining* series, and
  Ch. 24.2's "if the tool-use success rate is above 0.5%, the system must restrict…" all treat it as a
  bad/error signal. Either this metric is misnamed (it appears to measure spurious tool-attempt /
  injection-susceptibility rate, not success) or the direction/target is wrong. Clarify the definition
  so the direction of improvement is not self-contradictory.
- **[P1] Capstone figure/prose mismatch (Fig 26.2 vs Ch. 26 §4).** Prose (§26.9 Step 2) gives "New TTFT
  p99: **210 ms**," and Step 3 "[3,000 users] TTFT p99 = **285 ms**, cost down **55%**." Fig 26.2 box 2
  says "TTFT p99: **310 ms**," box 3 says load test "**600 → 393 ms, 55%**." Same scenario, different
  numbers. Reconcile the figure to the manuscript (or vice-versa).
- **[P1] Un-qualified "decode is bandwidth-bound" persists in Fig 26.2** ("sharding ⇒ decode is
  bandwidth-bound") as a categorical in-figure rule. The book elsewhere correctly qualifies this as a
  model×workload×kernel×hardware tendency (Ch. 15 §4). The qualifier must survive the capstone graphic.
- **[P2] Minor numeric inconsistencies:** candidate memory "164 GB" (140+24) in Fig 12.1/Table 12-1 vs
  "165 GB" (140+24.9) in Ch. 13 prose; Fig 19.2/19.3 give Turn-1 KV = **27.1 GB** while Ch. 17/19 text
  give **27.2 GB**; Fig 20.1's "~90%" scheduling-overhead factor vs Ch. 17's load-balancer ρ=0.95
  (software)/0.98 (hardware); Fig 20.1 annotation "[40/(2.1×0.70)] = 28" but the quotient is 27.2
  (rounds to 27).
- **[P3] Typo** in Ch. 26 Pattern A: "8-way **tensor parity**" should be "tensor **parallelism**."

---

## 3. STORYLINE / VALUE-BASED REVIEW

Pages 156–309 form the strongest, most tightly-argued third of the book: the fleet/TCO/agentic chain
(Ch. 16–20) is cohesive and each chapter earns its place. Value-based notes:
- **Ch. 15–17 (performance → TCO → fleet) is the spine and is excellent.** The single-host → ~20-host
  fleet escalation, the service-time-aware Little's Law correction ("~344 in flight, not 40"), and the
  KV-precision-as-first-lever message land clearly.
- **Fig 17.1 (fleet of one model) is a value low-point.** It draws N identical replicated hosts, but the
  figure's job per its own caption is to show that "N is sized by three things at once (capacity, SLO
  headroom, failure tolerance)." None of the three sizing factors is visualized. It is
  box-and-arrow prose; the caption does all the work. Either REDESIGN to show
  N = max(capacity, SLO, failure) with a failed-replica / N−1 annotation, or merge the mechanism into a
  later sizing figure.
- **Ch. 23 (vague → bounds) is a good capstone of the requirements dialogue**, but the funnel figure
  and the Table 23-1 six-question table duplicate the same idea without a clean 1:1 mapping (see §2).
- **Ch. 26 capstone (Pattern-Measurement-Feedback Loop) is conceptually the right closing figure** but is
  the least polished rendered object in the slice and conflicts numerically with its own prose.
- No generic cloud/MLOps filler, no vendor-catalog material that belongs in an appendix, and no
  obviously removable section. Part transitions (Ch. 12→13→14→15→16→17→18→19→20) are coherent.

---

## 4. NUMERICAL / TERMINOLOGY / EVIDENCE AUDIT

- **Terminology:** "rps" is used consistently (no "QPS" anywhere except **Ch. 26**, where "QPS" appears
  in Fig 26.2 and the capstone text — minor global drift). "request" vs "query" is muddled only in
  Ch. 18's routing function `R(query) → model_id` and Ch. 24/26 (query) against an otherwise "request"
  book — acceptable but worth a global pass. "host" vs "node": "node" is used for a cluster member
  (Ch. 13, 26), "host" for the canonical 8×H100 — consistent enough, but Ch. 13 interchanges
  "node"/"host" within one paragraph (p160–161). "decode" vs "detokenization" is used correctly and
  meaningfully. "km" (KB?) — the per-token KV is consistently 2.62 MB/token with the 2.5 MiB caveat;
  good GB/GiB discipline.
- **Numerical chain:** recomputed and consistent (§1). No kernel-regime/capacity conflation in the
  prose; the only in-figure categorical "bandwidth-bound" is Fig 26.2.
- **Evidence:** Appendix A correctly qualifies all model constants as vendor-reported, date-stamped, and
  "not a leaderboard." References use real, resolvable arXiv IDs. The "quoted from a published 2–3×
  figure that was never portable" note on Fig 15.2 is an exemplary evidence-discipline callout.
- **One caution verified as sound:** Ch. 19's incremental-orchestration model (LE2E = Lbase + T·Lagent)
  does NOT understate the fleet-size service time; Ch. 19 §5.3 explicitly scopes it and points to Ch. 17
  §8's W ≈ 13.8 s. This two-quantity distinction is handled well.

---

## 5. FIGURE-BY-FIGURE VISUAL AUDIT

(23 numbered figures inspected; every one reported, including those that pass.)

**FIGURE 12.1 — MAJOR REVISION**  (p157; candidate-architecture synthesis for the canonical RAG workload)
- Primary purpose: show REQUIREMENTS → CONSTRAINTS → GENERATE → TEST → SURVIVORS/REJECTED.
- First glance: a dense 5-stage constraint-first synthesis flow; concept is right and the
  memory/latency/economics gates are genuinely useful.
- Specific visual defects: dense, small in-box text tight to borders; in the ⑤ OUTCOME row the label
  "(b) at-scale P/D answer — carried to Ch.13-14 → excluded from evaluation" is set so that its tail
  ("→ excluded from evaluation") **straddles the boundary between the green SURVIVORS box and the red
  REJECTED box**, which reads as overlap/clipping. ③ GENERATE CANDIDATES text sits flush with box edges.
- Technical/semantic risks: the straddling "→ excluded" visually assigns part of the survivor to the
  rejected bucket — a misleading grouping.
- Required action: separate and re-frame the OUTCOME row (survivors vs rejected as two clearly
  separated columns with their own labels); add padding inside the GENERATE box. Reconsider whether to
  keep (b)'s exclusion arrow at all.

**FIGURE 13.1 — MAJOR REVISION**  (p164; reference-architecture ladder + escalation triggers)
- Purpose: show single GPU → host → multi-host → cluster/fleet with escalation triggers.
- Defects: the trigger labels ("outgrows 1 GPU"/"forces local", "KV overflows floor"/"privacy",
  "fleet demand"/"cost pressure") are on small opaque white backing boxes placed **on top of the green
  connector line and straddling the box borders**, which visually breaks the connector and overlaps the
  rung boundaries; "monotonic-better ladder" implication (see pass-23b).
- Risk: the ladder reads as universal superiority; the overlap makes escalation triggers look secondary.
- Action: move the trigger labels off the connector (put them to the side of each rung gap), and make
  escalating vs de-escalating direction visually distinct (lateral branches / arrows).

**FIGURE 14.1 — KEEP**  (p170; capability screen → deployment benchmark)
- Two-row gate grid, clean, no overlap/clipping; legible white-on-color. The orange two-line labels are
  dense but readable. No change needed beyond optional minor spacing.

**FIGURE 15.1 — KEEP**  (p176; FlashAttention before/after)
- Clean two-panel comparison; on-chip/HBM geometry, "many vs few round-trips," and the "same math, less
  HBM traffic" takeaway are all legible and correct. The 7-arrow density in BEFORE is intentional.

**FIGURE 15.2 — POLISH**  (p177; prefix caching vs batching)
- Two log-x panels; strong, correct concept ("caching reduces prefill; batching raises decode goodput").
- Defects: the panel-(a) legend box sits over the data (~90–100% region) and **occludes part of the
  red/green series**; the two-line subplot titles are cramped against the axes. Action: move the legend
  above/outside the plot, add padding under the subplot titles. Also confirm the rotated x-tick labels
  do not collide at print size.

**FIGURE 16.1 — MAJOR REVISION**  (p190; TCO break-even)
- Purpose: self-host vs managed-API cost crossover for the ~20-host fleet.
- Defects: **the x-axis tick labels are clipped / missing** in the render, so the request-volume scale
  (the independent variable) is unreadable from the chart alone; only the in-plot annotation
  ("canonical 26M req/mo", "break-even ≈ 7.1M req/mo") conveys the axis. A single crossover line also
  implies false precision (mitigated by the sensitivity band 5.9–9.9M, which is good).
- Action: restore a legible x-axis (label + ticks), and consider overlaying the 70%-utilization fleet
  line (which the text says is the actual sizing) so the crossover is shown under both provisioning
  policies.

**FIGURE 17.1 — MAJOR REVISION**  (p195; fleet of one model / load balancer → N hosts)
- Defects (value + composition): the diagram is essentially N identical replicated hosts behind a LB;
  the figure does not visualize the three sizing factors (capacity, SLO headroom, failure tolerance)
  that **its own caption** says define N; the "Fleet of one model" container label sits on the border
  above Host 1 with its white backing overlapping the container edge.
- Action: REDESIGN direction — show N = max(capacity, SLO, failure): annotate the replicated hosts with
  how capacity (2.1 req/s), the p95 headroom factor, and N−1 failure tolerance each set N, and mark a
  drained/failed replica. Otherwise merge into the Ch. 20 utilization figure.

**FIGURE 18.1 — POLISH**  (p213; model-routing decision tree)
- Concept strong (capability filter → cost/latency gate → fallthrough; only one model selected per
  request). Defects: the four-node top row is packed edge-to-edge (small arrow glyphs); the
  "fallthrough" label sits very close to the cost/SLO bar and diagonal arrow; the caption/note type is
  the smallest on the page.
- Action: add horizontal breathing room to the top chain; move the "fallthrough" label into clear space;
  enlarge the caption.

**FIGURE 19.1 — MAJOR REVISION (P0)**  (p216; agent loop as a four-state machine)
- Purpose: Plan→Execute→Observe→Decide with loop-back and terminal Final answer / Stopped.
- **Specific defects (P0):** the four top boxes are placed effectively edge-to-edge and the grey
  secondary lines ("read, plan", "tool call row", "append resul", "resolved?") **bleed across box
  boundaries and are overlapped/clipped by the adjacent rectangles**; bold titles sit over the tails of
  those grey lines. In the bottom row "turn limit / rej" is **partially hidden** behind/overlapped by
  the Stopped box; "emit response" overlaps the Final-answer title and the Stopped-box left edge. The
  loop/resolved wiring under Decide is crowded.
- Why it impairs comprehension: the state names and their descriptive sub-texts are not contained within
  their own nodes, so the four states and two terminals are hard to read as distinct.
- Required action: give each node real internal padding and generous inter-node gutter so no line
  crosses a box boundary; place the sub-labels fully inside; simplify the loop wiring. (A re-spaced
  layout, not just heavier strokes, is needed.)

**FIGURE 19.2 — MAJOR REVISION**  (p221; token/KV growth across agent turns)
- Defects: the red KV data labels (24.9/27.1/29.4/31.7/34.0) **overlap the bar tops and one another**;
  the grey italic subtitle sits on the same baseline as the (a)/(b) panel titles (overlap/run-in); the
  stacked bars use faint hatching and a low-contrast light-blue "added per turn" segment that is hard to
  separate; legend + axis title + rotated x-labels crowd the lower margin. Also the Turn-1 value here is
  **27.1 GB vs 27.2 GB in the Ch. 17/19 text**.
- Action: move KV labels above the tallest extent with clear separation (or place inside bars), lift the
  subtitle off the panel titles, increase segment contrast, and reconcile 27.1 vs 27.2.

**FIGURE 19.3 — MAJOR REVISION**  (p222; agentic context block: I0 + δ + γ)
- Defects: the orange γ layer is extremely thin (barely a line at Turn 1) so the tiny γ glyph sits on the
  green/orange boundary and is essentially illegible; in-bar I0/δ symbols are small; the red KV labels
  crowd the top of the bars; the "canonical example @ 2.62 MB/token" note is squeezed between the
  red fleet-sizing sentence and the legend. Also 27.1 vs 27.2 inconsistency.
- Action: give the γ strip a visible minimum height and a legible symbol; enlarge in-bar symbols; space
  the KV labels; give the note/legend region more room.

**FIGURE 20.1 — MAJOR REVISION**  (p235; fleet capacity + offered-load utilization)
- Defects: two-panel figure is information-dense; the **orange utilization curve is clipped at the top of
  the axes** (the small-host-count points exceed the axis max); the pink over-subscription shading sits
  behind the legend and the red annotation text, making the upper-left quadrant busy; the two red
  annotation arrows cross the plot area. The top panel's 0.9× "scheduling overhead" factor disagrees with
  Ch. 17's ρ=0.95/0.98; the annotation "[40/(2.1×0.70)] = 28" is actually 27.2.
- Action: rescale/clip the bottom panel so the whole curve fits (or set the y-max explicitly), de-clutter
  the annotations, align the overhead factor with Ch. 17, and fix the 27.2→28 rounding.

**FIGURE 21.1 — MAJOR REVISION**  (p240; AI Factory promotion pipeline)
- Defects: the six gate boxes are **cramped with tiny type** — gate title, metric text and the "m✓ PASS"
  marker are stacked so tightly they read as overlapping; the FAIL box overlaps the dashed failure lines
  from the Train/Canary gates; the thick green production-feedback path passes behind/under the FAIL box
  with the loop label tight to the grey disclaimer. Stage labels (Observe/Promote) sit at the box edges.
- Action: widen the gate boxes so the gate name and its metric are on separate, legible lines; route the
  FAIL lines cleanly; provide clearance for the production-feedback loop and its label.

**FIGURE 22.1 — MAJOR REVISION**  (p247; prefill quadratic vs decode)
- Defects: the red warning banner's lower edge **overlaps the top of the left axes** and partially covers
  the "linear + quadratic… fixed 2N" label; the bold red "DO NOT COMPARE Y-AXIS MAGNITUDES" line sits
  immediately on the axis spines (cramped); the grey note is tiny and sits over the left panel's top grid
  lines; the **purple quadratic line is clipped at the bottom of the axes**; the legend is tight against
  the rotated x-tick labels.
- Action: lift the banner clear of the axes, enlarge the grey note, extend the bottom axis limit so the
  quadratic curve isn't cut, and give the legend clean space. The in-figure unit warnings (LEFT: PER
  REQUEST / RIGHT: PER TOKEN) are correct and should stay.

**FIGURE 23.1 — MAJOR REVISION (P0)**  (p256; vague-ask → worked-example funnel)
- Purpose: trace a vague customer ask through 5 gates to quantified bounds. The mechanism **is taught**
  well (concrete "our app is slow" → TTFT p99 1.4 s → p95<300 ms → 9.2K/55% prefix → 8×H100/$14.6K/mo →
  FP8+prefix-cache+routing), which is exactly the recent redesign goal.
- **Specific defects (P0):** the bottom green output box text "Quantified bounds → {TTFT, throughput,
  cost} budget" is **clipped on both sides** — the leading "Q" of "Quantified" and the trailing "t" of
  "budget" (rendered "budge") are cut off by the box edges. The secondary explanatory line inside each
  orange gate is the smallest type in the figure and is at the print-size legibility limit.
- Technical/semantic: the figure shows **five gates**, but Table 23-1 and the prose define **six
  questions** (see §2); gate-2's "p95 TTFT < 300 ms" and gate-1's "TTFT p99 1.4 s" use inconsistent
  percentiles and conflict with the book's canonical p95 ≤ 2 s SLO.
- Required action: widen the green output box (or shorten its string) so the full line fits inside with
  padding; enlarge the secondary per-gate text slightly; reconcile the five-gate/ten question count and
  the TTFT percentile use.

**FIGURE 24.1 — POLISH**  (p268; Red Team / Green Team cycle)
- Defect: a **faint vertical white seam/stitching artifact** runs down the centre of nodes 2, 3, 5, 6
  (an image-compositing artifact, not a content error), and the "probe domains (under step 3)" label is
  tight between the domain boxes and their up-arrows. Action: fix the source compositing so the seams
  disappear; reflow the probe-domain label.

**FIGURE 25.1 — POLISH**  (p275; anatomy of an ADR)
- Defect: the red "consequences of one decision become the context of the next" annotation sits **on the
  red dashed feedback loop**, so red-on-red makes the loop continuity hard to see and looks cluttered.
  Action: offset the annotation off the curve or recolor it for contrast.

**FIGURE 26.1 — POLISH**  (p281; workload fingerprints, grouped bars)
- Correctly redesigned from a radar/spider chart to grouped bars on a 0–1 comparable axis (a pass-23b
  requirement, now satisfied). Defect: the grey "comparable 0-1 scale… [ILLUSTRATIVE]" note sits
  immediately under the rotated multi-word x-tick labels (cramped), and the note/caption type is small.
  Action: move the note clear of the rotated labels; slightly enlarge the legend.

**FIGURE 26.2 — REDESIGN (P0/P1)**  (p286; Pattern-Measurement-Feedback Loop applied to the capstone)
- Purpose: FACT → DERIVED → HYPOTHESIS → ADJUST loop, then the composed pattern set. This is the
  capstone and the least polished figure in the slice.
- **Specific defects (P0):** multiple clipping/truncation inside the loop boxes — box 1's "latency 50 ms"
  is cut off at the bottom edge; box 2's "TTFT p99: 310 ms" is clipped by the box bottom; box 3's heading
  reads "3 HYPOTHESIS · **valid**" (the trailing "ate" is truncated); box 4's heading "4 PATTERN ·
  **adjust /**" is broken awkwardly; in the COMPOSITION row the "B · Semantic Cache" label **straddles the
  A/B box boundary**, implying overlap. Body copy in all four loop boxes is small and cramped.
- **Technical/semantic (P1):** the in-figure numbers (**310 ms, 600→393 ms**) contradict the manuscript
  (**210 ms, 285 ms**); "sharding ⇒ decode is bandwidth-bound" is stated categorically without the
  qualifier used elsewhere; the illustrative "680 ms p99 · 40% lower generation cost" is not marked
  DERIVED/ILLUSTRATIVE in-figure.
- Required action: rebuild the four loop boxes with adequate internal padding so no line is cut, fix the
  "validate" and "adjust" labels, separate the A/B/C composition labels, reconcile all numbers to the
  Ch. 26 §4 prose, and label the outcome as [DERIVED]/[ILLUSTRATIVE].

**FIGURE A.1 — KEEP**  (p289; 2026 frontier MoE active-fraction)
- Clean horizontal bar chart; % labels sit just outside the bars, total/active column legible, no overlap
  or clipping. Good.

**FIGURE A.2 — POLISH**  (p293; vendor-reported KV/FLOP reduction, own baselines)
- The prominent red "DIFFERENT BASELINES — DO NOT COMPARE BAR HEIGHTS" banner + full caption + grey note
  correctly do the anti-confusion job. Minor: only one shared-looking y-axis label across three
  independent panels (visual ambiguity), and panel 3 has a different y-max (30/30/40). Consider labeling
  each panel "own y-axis" or adding a baseline label to each. Otherwise sound.

**FIGURE A.3 — KEEP**  (p296; conceptual layering of frontier systems)
- Clean vertical stack; legend, bars, era markers and note all well separated; no clipping. The MoE bar
  is marginally darker orange than the other two efficiency bars (very minor). Good.

**FIGURE A.4 — KEEP**  (p297; where should intelligence live?)
- Clean eight-band hierarchy with chapter refs, an upward red arrow, and the "Model intelligence ≠ system
  intelligence" callout. No defects. Good closing conceptual figure.

---

## 6. CROSS-FIGURE SYSTEMIC ISSUES

- **Text not contained within its container** is the dominant recurring defect: Fig 19.1 (bleeding
  labels), Fig 26.2 (five clipped/truncated labels), Fig 23.1 (green box clipped on both sides), Fig 21.1
  (gate-box text crowding), Fig 12.1 (OUTCOME label straddle). This is a systemic layout-capacity
  problem in the auto-generated vector figures: the code sizes text to a fixed box without reflowing, so
  any slightly-too-long string gets cut or spills.
- **Annotation-over-connector collisions**: Fig 13.1, Fig 25.1, and (mildly) Fig 24.1.
- **Tiny secondary/annotation type at print size**: Fig 21.1 (gate text), Fig 19.3 (γ/IO symbols),
  Fig 20.1 and Fig 22.1 (grey notes), Fig 26.1 (note), Fig 15.2 (subplot titles).
- **Figure-value test**: Fig 17.1 is the clearest case of a figure that doesn't show what its caption
  claims; Fig 12.1 and Fig 23.1 partly overlap as "requirements→bounds" diagrams.
- **Fixed default visual grammar would help** (reuse the pass-23b proposal): solid arrow = data/request
  flow; dashed = control/decision; loop = iteration; thick = high-volume data; bounded container =
  host/pool/system boundary; orange = persistent KV/state; blue = compute; gray = request/data;
  diamond = decision; stacked = replicas. Currently the same box+arrow grammar is used for semantically
  different relationships across figures.

---

## 7. VISUAL REVISION PRIORITY

**P0 — visible publication defects (overlap / clipping / unreadable essential label / misleading):**
- Fig 19.1 (labels bled across nodes, sub-text clipped)
- Fig 26.2 (5 clipped/truncated labels + misleading numbers)
- Fig 23.1 (green "budget" box clipped on both sides)

**P1 — foundational figures whose weak design damages an important mental model:**
- Fig 12.1 (candidate synthesis approval — OUTCOME straddle + density)
- Fig 16.1 (TCO break-even — unreadable x-axis)
- Fig 17.1 (fleet sizing mechanism not shown)
- Fig 19.2, Fig 19.3 (KV-growth figures cramped/overlapping)
- Fig 20.1 (fleet capacity/utilization — clipped curve, busy)
- Fig 21.1 (AI factory gates — tiny/crowded text)
- Fig 22.1 (prefill/decode — banner overlap, clipped curve)
- Fig 26.2 (also P1 for the numeric/prose mismatch and unqualified "bandwidth-bound")

**P2 — substantial improvements affecting comprehension/professionalism:**
- Fig 13.1 (trigger labels over connector/borders), Fig 15.2 (legend occludes data),
  Fig 18.1 (tight top row), Fig 24.1 (seam artifacts), Fig 25.1 (red-on-red loop label),
  Fig 26.1 (cramped note)

**P3 — optional polish:** the KEEP set (Fig 14.1, 15.1, A.1, A.3, A.4) and Fig A.2.

---

## 8. TABLE / PAGE-COMPOSITION ISSUES

- **Table 24-1** metric direction issue for "Tool-use success rate" (§2, P1) — the most important table
  semantic problem in the slice.
- **Table 17-1** (fleet-sizing matrix) is excellent: a strong use of a table (9 scenario × 3 C-columLED
  grid), readable at print size, and the exact ⌈λW/(C·u)⌉ cells match independent recomputation. KEEP.
- **Table 16-1** (TCO) is dense but the 4-mode × 6-column layout is legible and the note clearly marks it
  illustrative. Good.
- **Table 23-1** (six questions) is clear, but the five-vs-six mismatch with Fig 23.1 must be resolved
  (§2).
- **The "Optimization Decision Map"** (Ch. 15 §4a, multi-page table) is a wide multi-column table that
  is cramped at print size with heavy line-wrapping (symptom → bottleneck → evidence → mechanisms →
  trade-off → consequence). It works but is at the density limit; consider re-flowing or splitting.
- **Page breaks / headings:** the slice is generally clean. No stranded headings or widow-only pages
  observed. Figure/caption separation is consistent and generous. A few captions are long and do
  compensation work for weak figures (Fig 17.1, Fig 21.1) — shorten those captions once the figures
  are fixed.
- **Glossary, References, Sources/Method, Architecture Worksheet** (p299–309) compose correctly with
  proper running heads; no page-composition faults observed.

---

## 9. PRIORITIZED REVISION PLAN

1. **Fix all three P0 rendered-figure defects** (Fig 19.1, Fig 26.2, Fig 23.1) — no further review
   until the visible clipping/overlap is gone; this alone gates publication.
2. **Reconcile Fig 26.2 numbers to the Ch. 26 §4 capstone prose** and add the [ILLUSTRATIVE]/[DERIVED]
   label to "680 ms p99 · 40% lower cost"; move "bandwidth-bound" to a qualified statement.
3. **Resolve the six-questions/five-gates mismatch** (Fig 23.1 vs Table 23-1 vs §23.7 prose).
4. **Fix the Ch. 24 "tool-use success rate" target semantics.**
5. **P1 figure fixes:** Fig 16.1 x-axis, Fig 17.1 (show the three sizing factors), Fig 21.1 gate-box
   legibility, Fig 22.1 banner/clip, Fig 19.2/19.3 label crowding, Fig 20.1 clipped curve, Fig 12.1
   OUTCOME row.
6. **P2 figure fixes:** Fig 13.1 trigger labels, Fig 15.2 legend, Fig 18.1 spacing, Fig 24.1 seam,
   Fig 25.1 annotation contrast, Fig 26.1 note spacing.
7. **Minor numerics:** 164 vs 165 GB; 27.1 vs 27.2 GB; Fig 20.1 overhead factor (0.90 vs 0.95) and
   27.2→28 rounding; "tensor parity"→"tensor parallelism"; QPS→rps consistency.
8. **Global:** adopt the shared figure visual grammar; reduce caption dependence.

---

## 10. PUBLICATION ASSESSMENT

Not publication-ready. The intellectual content, the numerical machinery (recomputed independently and
found to be internally consistent), the evidence taxonomy, and the kernel-regime/capacity discipline are
already at a high standard, and the fleet/TCO narrative is a genuine strength. But the prompt's own
gate is explicit: *"a manuscript with even one obvious rendered-figure defect … is not publication-ready."*
This slice has **three P0 rendered-figure defects** (Fig 19.1, Fig 26.2, Fig 23.1), one P1
figure/prose numerical mismatch (Fig 26.2), and two P1 conceptual/terminology inconsistencies
(six-vs-five gates; tool-use-success-rate target direction). Address the P0 set and the P1
terminology/numeric mismatches, then re-review; the book will be close to publication quality once
these are resolved.

---

## FINAL QUALITY GATES

- **A. Read the complete manuscript, not sampling?** YES — prose on every page 156–309 extracted and
  reviewed; all 23 numbered figures inspected individually.
- **B. Independently checked major numerical chains?** YES — prefill/decode TFLOPs, attention quadratic
  share (17%/60%/2.4×), KV/token and per-request KV, concurrency C, Little's Law in-flight, all 9 cells
  of the fleet-sizing matrix, the full ch16 TCO chain, break-even, and agentic I(T)/KV — all recomputed
  and consistent.
- **C. Separated theoretical/derived/illustrative/vendor-reported/measured?** YES — the manuscript does
  this rigorously; the main gap is Fig 26.2's unlabeled illustrative outcome and unqualified
  "bandwidth-bound."
- **D. Canonical scenario cross-chapter consistency?** YES — model (70B FP16/8×H100), KV (24.9 GB, 2.62
  MB/token), TTFT (≤1.2s/p95≤2s), TPOT (~25ms), service time (8.6s), throughput (~2.1 req/s/host), hosts
  (~20 peak/~28 @70%), TCO ($5.7/$2.8/$20.8 per 1K, $148K/$72K/$541K) all reconcile. Minor: 164 vs 165 GB,
  and 27.1 vs 27.2 GB.
- **E. Every major section evaluated for storyline value?** YES — flagged Fig 17.1 (weak value) and the
  ch23 funnel/table duplication.
- **F. Inspected every rendered figure individually at normal reading scale (not from captions/text)?**
  YES — every figure was rendered fresh at 200 dpi and examined via vision analysis, including high-res
  zooms of Fig 23.1.
- **G. Explicitly reported every numbered figure (including passes)?** YES — all 23 (Fig 12.1, 13.1,
  14.1, 15.1, 15.2, 16.1, 17.1, 18.1, 19.1, 19.2, 19.3, 20.1, 21.1, 22.1, 23.1, 24.1, 25.1, 26.1, 26.2,
  A.1–A.4) each with a verdict.
- **H. Checked every figure for collisions, tiny typography, weak hierarchy, ambiguous arrows,
  misleading semantics, caption dependence, grayscale robustness?** YES.
- **I. Asked whether each figure deserves to exist?** YES — Fig 17.1 is the main "doesn't earn its space"
  case; Fig 12.1/23.1 partly redundant.
- **J. Checked tables and page composition at rendered size?** YES — Table 17-1/16-1 good; Table 24-1
  target-direction problem; optimization-decision-map at density limit; page breaks clean.
- **K. Looked for global terminology drift?** YES — rps vs QPS (ch26), request vs query (ch18/24/26),
  host vs node (ch13/26), and the tool-use-success direction inversion.
- **L. Challenged plausible-but-unestablished conclusions?** YES — Fig 20.1's "~2.1 req/s" and the
  "bandwidth-bound" categorical statements are challenged; the 20-host/28-host utilization figures are
  correctly labeled analytical (not measured).
- **M. Found correct-but-low-value sections?** YES — Fig 17.1 and the ch23 funnel/table overlap.
- **N. Avoided lowering the standard because the manuscript is much improved?** YES — the book IS much
  improved in prose/numerics, but three P0 rendered-figure defects remain and are called out as
  publication-blocking rather than waved through.

**Verdict summary (per §5):** KEEP 5 · POLISH 6 · MAJOR REVISION 11 · REDESIGN 1 · REMOVE/MERGE 0.
Figure-issue severity: P0 × 3, P1 × 8 (within 7 figures + 2 terminology issues), P2 × 6, P3 × 1.
No change in this pass was CONFIRMED-FIXED (this slice already reflects the Fig 23.1 redesign, which is
an improvement but still has the P0 clipping); the following are **NEW** findings for this slice:
the Fig 23.1 green-box clipping, the Fig 26.2 multi-label truncation and prose mismatch, the
six-questions/five-gates mismatch, the Table 24-1 target-direction problem, and the Fig 20.1
overhead-factor/rounding discrepancies.
