# RE-REVIEW FINDINGS — Part II "The Workload", Chapters 4–6
PDF: /home/ubuntu/from-token-to-fleet-v20260913-full.pdf  (307 pp)
Range reviewed: PDF p.53–89 (ch4 p.54–69, ch5 p.70–79, ch6 p.80–88; book pages 36–70).
Method: full text deep-read + raster inspection of every figure (4.1, 5.1, 6.1, 6.2) and every table
(4-1, 4-2, 4-3, canonical box, 5-1, 6-1), plus independent recalculation of all key arithmetic.
Figures/tables were inspected as rendered RASTER (vision), not text layer.

Page refs below are PDF page numbers (book page in parens).

---

## GENUINE FINDINGS

### 1. CRITICAL — Table 5-1 rendered as raw unrendered markdown (not a table at all)
- Location: PDF p.72–73 (book p.54–55), bottom of p.72 continuing onto p.73.
- Problem: The element titled "Table 5-1 — Model-selection decision: embedding vs generation model" is
  typeset as UNRENDERED MARKDOWN SOURCE. The printed page shows the literal pipe/dash characters and
  raw cell text leaking as ordinary running text: "Table 5-1 — ... | metric | value | derivation | |—|—|—|
  | Embedding dimension (recommended) | 768 | all-mpnet-base-v2 [ILLUSTRATIVE][DE-" — and the final word
  is clipped mid-token ("[DE-") at the page break, resuming on p.73 as "...RIVED] | | Embedding model size |
  ~110M parameters | ...". There is no typeset grid, no rules, no column alignment.
- Why it matters: This is the chapter's model-selection decision table, so a reader literally cannot read
  the verdict (embedding dim / generation model) — it appears as broken source text with a truncated cell.
  An unrenderable, page-break-split table is a publication-blocking defect and a visible "markdown leaked
  into the PDF" artifact.
- Recommended change: Render Table 5-1 as a proper typeset table (markdown seems not to have been
  converted for this one element). Break the table so no cell is split across the page boundary (or use a
  caption+repeat-header if it must span).

### 2. MAJOR — §6.4.1 / Fig 6.2: p99 vs the 1% stragglers is internally contradictory
- Location: PDF p.83–84 (book p.65–66), §6.4.1 "Latency Is a Distribution, Not a Mean" + Fig 6.2.
- Problem: The example constructs the stream as "99% of observations [log-normal near 0.8 s] + 1%
  straggler cluster at 5.0 s," and states p99 ≈ 1.33 s while explicitly saying the 5 s stragglers are
  "beyond the 99th percentile." Yet it then claims "The p99 reading is what brings the 1% tail into view
  ... which is why we show it explicitly." If a 1% straggler population lies ABOVE p99, then p99 ≈ 1.33 s
  does NOT reveal it. A reader shown p99 = 1.33 s (< the 2 s SLO) would correctly conclude no breach and
  never see the 5 s stragglers. The governing percentile for a sub-5%-outlier population is p99.9 (or max),
  not p99.
- Why it matters: This is the chapter's core teachable point ("mean hides the tail; SLO against the
  percentile"). As written it teaches the wrong rule — that p99 surfaces a 1% outlier cluster — which it
  does not. It undercuts the exact claim the chapter was written to make.
- Recommended change: Make the percentile match the construction. Either (a) shrink the straggler fraction
  so the stragglers genuinely sit between p99 and p100, and then state that p99.9 / the maximum is the
  percentile that exposes them (p99 alone still looks healthy), or (b) keep 1% and reframe: "even p99
  (1.33 s) misses the tail; the SLO breach only becomes visible at p99.9/max, which is why we log the
  full distribution." Fix Fig 6.2 to match (see finding 5).

### 3. MODERATE — §4.9 mini-case "cross-check" uses the roofline IDEAL prefill rate, not achieved
- Location: PDF p.68–69 (book p.50–51), §4.9 end-of-chapter mini-case host count.
- Problem: The prefill-throughput bound derives ~23 hosts from "~19,800 tokens/s per host" (50 rps ×
  9.2K = 460,000 prefill tok/s ÷ 19,800). But p.64 (book p.46) of the same chapter states the canonical
  host's ACHIEVED prefill is only ~8.5K tok/s and calls 19,800 the host's "ideal." Using ideal instead of
  achieved inflates the bound ~2.3× (460,000 ÷ 8,500 ≈ 54 hosts). So the claim that KV-residency/service-time
  (25 hosts) and prefill-FLOP-throughput (23 hosts) "point at the same order — reassuring" rests on two
  optimistic bounds that both ignore real serving efficiency; they are weaker and less independent than
  presented.
- Why it matters: The mini-case yields a concrete fleet count (25–36 hosts) framed as cross-confirmed.
  A reader could under-size the fleet, and the "two independent constraints agree" framing exaggerates the
  confidence. The 8.5K/19.8K discrepancy also reads as an internal inconsistency between the same chapter's
  own worked prefill number and the one used for sizing.
- Recommended change: Derive the prefill-throughput bound from achieved/sustained prefill throughput (or
  apply an explicit MFU); state 23 as a hard ideal lower bound; and soften "reassuring" to acknowledge both
  are optimistic analytical bounds that benchmark goodput (Ch 14) must confirm. Reconcile the 8.5K vs 19.8K
  per-host prefill figures explicitly.

### 4. MODERATE — §4.4.1 / §4.7: two different cost bases treated as equivalent
- Location: PDF p.64 & p.66–67 (book p.46 & p.48), §4.4.1 "Economic Constraints" and §4.7
  "Economic feasibility."
- Problem: "Cost per request ≈ $0.012" is computed from per-million-token PRICES ($1.20/M in,
  $2.00/M out), i.e. a market/API list-price basis (($1.20×9.2 + $2.00×0.3)/1000 = $0.01164). The host
  basis is $20/hr infrastructure, whose actual marginal cost per request at 10 rps is $20/hr ÷ 10 rps ≈
  $0.00056 — about 21× lower. §4.7 then mixes both in one sentence ("At ~$20/hour per 8×H100 host and
  ~$0.012 per request... the TCO is driven by..."). The 2K-vs-9.2K TCO lever (p.67) also uses the
  per-token-price basis.
- Why it matters: The economics dimension is meant to translate traffic into recurring cost and drive
  host-count/TCO reasoning (Ch 16). Using a market per-token price as if it were the fleet owner's cost
  overstates per-request cost ~21× and could distort the dominant-cost and host-count conclusions.
- Recommended change: State which basis each figure uses. For fleet-owner TCO, use derived-from-infrastructure
  cost/request (~$0.00056); clearly label the $1.20/M–$2.00/M and $0.012 figures as cloud API list-price
  basis, not the owned-fleet marginal cost, and do not juxtapose them as if equivalent.

### 5. MODERATE — Fig 6.2 percentile markers/skew inconsistent with the text
- Location: PDF p.84 (book p.66), Fig 6.2 "Request-latency distribution: p50/p90/p95/p99 and the mean."
- Problem: Text states p50 ≈ 0.80 s, p90 ≈ 0.94 s, p95 ≈ 0.99 s; the figure's green p50/p90/p95 lines
  appear at ~0.85–0.90 / ~0.95–1.00 / ~1.00 s, with p50 drawn essentially at the mean. Text states
  p99 = 1.33 s but the red line is drawn at ~1.4 s. The solid mean (0.85 s) is drawn LEFT of the p50
  marker — for a right-skewed log-normal body plus a 5 s tail the mean should exceed the median, so the
  figure visually reads left-skewed, contradicting the right-tail story. The p50/p90/p95 labels are
  stacked and nearly collide (descenders/ascenders), and p99 is labeled only in the inset box, not on-plot.
- Why it matters: This is the chapter's key "mean hides the tail" demonstration; plotted percentiles not
  matching the stated values, and a mean drawn left of the median, undercut the intended message and make
  figure and prose disagree.
- Recommended change: Recompute/reposition percentile markers to the values stated in the text; ensure
  mean > p50 (right-skew); de-conflict the stacked percentile labels; and draw/label the p99 line at 1.33 s
  on-plot (not only in the inset).

### 6. MODERATE — Fig 5.1: floating "split" label and misaligned row
- Location: PDF p.79 (book p.61), Fig 5.1 "Model selection for RAG."
- Problem: The second "split" edge label floats unattached in whitespace beside the vertical arrow to the
  Generation-leg box (no leader; ambiguous which arrow it labels), while the first "split" sits on the
  diagonal arrow to the Retrieval-leg box. The top and middle rows are also horizontally misaligned
  (Generation leg sits under neither the parent box nor anything aligned; Workload-characterization is
  narrower and left of center).
- Why it matters: A 3-second-read flow diagram should be unambiguous; the unattached "split" momentarily
  confuses which leg is being split and the misalignment forces a second look to confirm the mapping.
- Recommended change: Attach/label the second "split" directly on the arrow, and align each split target
  vertically under its parent (or add explicit connectors from the Five-selection-surfaces box to both legs).

### 7. MINOR — §4.4.1: implausible "reserved" price figure
- Location: PDF p.64 (book p.46), §4.4.1 "Economic Constraints."
- Problem: "~$2,500/month reserved (illustrative)" for an 8×H100 host is ~6× below the on-demand
  $14.6K/month (the canonical box computes $20/hr × 730 h ≈ $14.6K/mo, and notes the canonical box uses the
  on-demand basis). A ~83% reserved discount on H100 is unusually deep, and it silently introduces a second
  purchase mode that the canonical box explicitly excludes.
- Why it matters: An abruptly ~6×-lower "reserved" number invites confusion about which basis is
  authoritative and reads as inconsistent with the per-host ceiling arithmetic.
- Recommended change: Either remove the reserved figure or make it a defensible committed-use/amortized
  basis with an explicit note on why it diverges so much; keep the on-demand basis authoritative.

### 8. MINOR — §6.2.1 layer numbering vs Fig 6.1 ordering
- Location: PDF p.82–83 (book p.64–65), §6.2.1 "The Metric Hierarchy" vs Fig 6.1.
- Problem: The three layers are listed/numbered Workload (1), Serving (2), Resource (3), but Fig 6.1
  stacks them Workload → Resource → Serving (middle box = Resource). A reader correlating "layer 2 =
  serving" with the middle (Resource) box gets a momentary mismatch in a chapter that is explicitly about
  reading the layer order correctly.
- Why it matters: Small but avoidable friction in exactly the chapter about layer order and the
  causation/diagnosis direction.
- Recommended change: Re-order the numbering in §6.2.1 to match the figure's Workload → Resource →
  Serving causation order, or explicitly note that the listing order differs from the causal/visual order.

---

## GENUINELY EXCELLENT (noted briefly; no change requested)
- Avg/peak operating points are rendered as two explicit rows on p.62 (avg: 100 users / ~10 rps / ~86
  in-flight; peak: 400 / ~40 rps / ~344), exactly as the standard requires, and the active-user-population
  vs request-occupancy distinction is carefully and correctly explained (with the 8.6 s vs 10 s service-time
  reconciliation).
- Table 4-3 per-quantity provenance/status tags ([ILLUSTRATIVE]/[ASSUMPTION]/[2°] DERIVED/[1P] FACT) and the
  explicit "deliberately conservative full-MHA teaching baseline — a GQA 70B carries ~8× less KV" caveat are
  exemplary evidence hygiene; the ~2.62 MB/token figure is consistently flagged as an upper bound.
- §6.4.3 correctly avoids the classic overreach: it flags the 1.19-vs-0.989 PFLOPS comparison as a
  single-device deadline/capacity illustration, NOT the evidence of compute-boundness, and attributes the
  prefill/decode regimes to arithmetic intensity (the ~295 FLOP/byte ridge) and the TP-sharding note for
  decode. This is genuinely well-reasoned.
- Voice iron rule holds across all of Ch4–6: zero "you/your", zero "Think of X as Y", zero imperative
  "Consider…/Imagine…".
- The input-heavy (30×) asymmetry → prefill-dominated reasoning, and the "context window is not free
  capacity" wrong-inference guard, are handled with appropriate nuance.

---

## FINAL REMAINING-RISK ASSESSMENT (for Ch4–6)
- Strongest remaining risk: the broken Table 5-1 (must fix) and the §6.4.1 p99/straggler contradiction
  (the single most likely to teach an incorrect rule if left).
- The mini-case host-count (finding 3) and the economics basis (finding 4) are the two places where a
  reader is most likely to extract a wrong quantitative conclusion from Ch4–6.
- Recommended: one more light pass over Ch4–6 after the Table 5-1 + §6.4.1/Fig 6.2 fixes land, to confirm
  the percentile narrative and the economics basis read cleanly end to end.
