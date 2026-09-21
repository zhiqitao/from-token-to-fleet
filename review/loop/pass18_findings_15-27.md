# PASS-18 — Re-review of PASS-17 fixes — Chapters 15–27 + Back Matter
## Book: "From Token to Fleet" (from-token-to-fleet-v20260913-full.pdf, 308 pp)
## Scope: confirm PASS-17 fixes landed in the RENDERED PDF; report any NEW findings
## Review date: 2026-09-20
## Method: pymupdf page render at 160–300 dpi + vision inspection of every relevant
##   figure/table (Fig A.1 p.288; Ch16 §16.4 p.185; Ch18 §3.2 p.207; Fig 15.1 p.175;
##   Fig 16.1 p.189; Fig 17.1 p.194; Fig 18.1 p.212; Fig 19.2 p.220; Fig 20.1 p.234;
##   Fig 21.1 p.239; Fig 22.1 p.246; Fig 26.1 p.280; Fig A.2 p.292; Fig A.3 p.295;
##   Fig A.4 p.296; back-matter Sources/Method p.304). For Fig 15.1 and Fig 20.1 and
##   Fig A.4, verified against the figure's source generator (fig_ch15_flashattn.py,
##   fig_batch3.py, fig_2702.py) and against the layout's actual coordinates, because
##   auxiliary vision reads of dense/log plots are unreliable (PASS-17 methodology note).
##   Cross-checked every reported numeric discrepancy against both the generator source
##   and the rendered text layer before reporting.

--------------------------------------------------------------------------------

## A. CONFIRMATION OF PASS-17 FIXES (Did each land in the rendered PDF?)

### FIX #1 — PASS-17 Finding #1 (Fig A.1): RE-ENCODED AS LINEAR ACTIVE-FRACTION BARS
- **LANDED.** Verified on rendered p.288. Fig A.1 is now a horizontal bar chart on a
  LINEAR x-axis, 0–10%, labelled "Active parameters as % of total". Four single-orange
  bars per model, active fraction annotated at bar end, with per-row grey
  total/active annotations to the right of each bar:
    GLM-5.3-Flash          5.6%   (320B total / 18B active)
    Qwen3.8-Flash-Next     4.8%   (125B total / 6B active)
    Kimi K3                3.7%   (2800B total / 104B active)
    DeepSeek V4-Pro/Flash  4.6%   (284B total / 13B active)
  The curves discussed in the appendix text (§A.1) match these exactly (3.7/4.6/5.6/4.8).
  Fig A.1 property: DONE. The log-axis bar-length defect is fully resolved.

### FIX #2 — PASS-17 Finding #2 (Ch18 §3.2): BASIS NOTE DISTINGUISHING PER-1M FROM Ch16 $0.60/1M
- **LANDED.** Verified on rendered p.207. Ch18 §3.2 model-cost table (70B dense FP16
  8×H100 = $2.50/1M capital+energy; 70B 8-bit = $1.25; 70B MoE 8-bit = $1.00;
  70B 4-bit GGUF = $0.15) now carries a dedicated "Basis note (reconciled with Ch16's
  TCO)" paragraph directly beneath the table. It states the per-1M figures are
  per-model nominal rates for routing comparison (cost at a single host's nominal
  throughput), explicitly NOT the fleet-amortized ~$0.60/1M derived in Ch16 §16.4
  (~$148K/mo over ~20 hosts at full utilisation divided by ~2.5×10^11 tokens/mo),
  and states the ≈4× gap is a **utilization/throughput basis difference, not a
  contradiction**. Exactly the reconciliation PASS-17 requested. DONE.

### FIX #3 — PASS-17 Finding #3 (Ch16 §16.4): PROVISIONING-SENSITIVITY BLOCK
- **LANDED.** Verified on rendered p.185. Ch16 §16.4 now has an explicit
  "Provisioning sensitivity (explicit)" block that (a) states the TCO assumes the
  full-utilization fleet (≈20 hosts, provisioned exactly at the 40 rps peak, so the
  comparison does not double-count idle capacity), and (b) gives the 70%-utilization
  scenario: ≈28 hosts, capex ~1.4× → ≈$163K + ≈$30K opex + ≈$10K staff ≈ $203K/month,
  per-request ≈$203K/26M ≈ $7.8/1K (vs the $5.7/1K full-util figure), and states the
  "self-host loses to scale-to-load cloud" conclusion holds under either policy.
  The earlier "≈20 hosts (…~28 at the 70% utilization target)" sentence carries the
  same 70% target. Exactly the sensitivity addendum PASS-17 asked for. DONE.
  (Note: the requested "~$203K" figure is used, not the "~$207K" alternative in the
  PASS-17 recommendation text; this is correct and internally consistent.)

### FIX #4 — PASS-17 Finding #4 (Fig 15.1): WIDENED INTER-PANEL GAP FOR THE TWO O(L²)/O(L) ANNOTATIONS
- **PARTIALLY LANDED / RESIDUAL.** Verified on rendered p.175. The two annotation
  blocks ("O(L^2) HBM traffic: every query re-reads the row-block", red; "O(L) HBM
  traffic: each tile read once, softmax online", green) are now centered under their
  own panels, which is an improvement. BUT the two long SECOND lines still sit on the
  same baseline and nearly abut: by measured coordinates the red second line ends at
  x=302.4 and the green second line starts at x=309.5 — only a ~7pt gutter between
  them — while the two panel boxes are ~19pt apart (left panel 108–296, right panel
  316–504). Both second lines extend past the box working area into the inter-panel
  gutter, so at a glance the red line read "runs into" the green line. PASS-17 marked
  this MINOR; the fix improved panel affiliation but did NOT fully resolve the cramped
  second-line colliding-in-the-gutter problem. See NEW FINDING #3 below.

--------------------------------------------------------------------------------

## B. NEW FINDINGS THIS PASS (fresh adversarial sweep)

### NEW FINDING #1 — [MINOR][figure-vs-text] Fig 20.1 annotates "~27 hosts: 70% target"
###     while the book's own sizing rule and Ch16 §16.4 use "≈28 hosts"
- Location: Fig 20.1 (rendered pp.234, generated by `render/fig_batch3.py`), the
  blue dashed 70%-utilization annotation, plus the surrounding caption.
  Compare Ch17 §4/§5.1 ("⌈344/18⌉ ≈ 20 hosts at 40 rps (≈28 at the 70% utilization
  target)"), Ch17 mini-case, and Ch16 §16.4's newly-added provisioning block ("≈28
  hosts").
- Problem: Fig 20.1 annotates the 70%-target point on the per-host-utilization panel
  as "~27 hosts: 70% target (canonical 70%-util fleet)", but the book's text uses
  "≈28 hosts" for exactly the same canonical 40 rps peak at util_target = 0.70. The
  figure computes hosts = 40/(2.1×0.70) = 27.21 and rounds DOWN to "~27" (raw,
  non-ceilinged value); the book's sizing rule H = ⌈λ·W/(C·u)⌉ applies the CEILING,
  giving 28. Verified by re-derivation: 40/(2.1×0.70)=27.21 → ⌈ ⌉ = 28 (also
  40/(2.093×0.70)=27.30 → 28). So the figure and the text disagree by one host.
- Why it matters: Section 5/21 cross-chapter numeric consistency. A reader matching
  the figure's 70%-target point ("~27 hosts") against the book's stated "≈28 hosts"
  (Ch16 §16.4, Ch17) sees a one-host gap on the same canonical frame, and the figure's
  non-ceiling convention silently contradicts the book's ceiling convention that the
  sizing rule (and the fig's own top panel's "~20 hosts: saturation", = ⌈40/2.1⌉=19→20)
  uses. It is a minor but genuine figure-vs-text mismatch.
- Recommended: In fig_batch3.py, change the 70%-target annotation from "~27 hosts" to
  "≈28 hosts" (or note "⌈40/(2.1×0.70)⌉ = 28") so the figure matches the reusable
  sizing rule and Ch16 §16.4's "≈28 hosts". Apply the same ceiling convention used for
  the "~20 hosts: saturation" annotation.

### NEW FINDING #2 — [MINOR][figure-semantics, confirm direction] Fig A.4 the red
###     leader arrow points DOWN toward "Inside weights" while its label reads
###     "more of the intelligence and compute budget"
- Location: Fig A.4 "Where should intelligence live?" (rendered pp.296, generated by
  `render/fig_2702.py`), the vertical red left-margin arrow + rotated label.
- Problem: Source confirms the arrow is drawn downward (annotate xy=(0.45,1.5) from
  xytext=(0.45,9.1), i.e. head at the BOTTOM) next to the rotated label "more of the
  intelligence and compute budget", which spans the middle of the stack. The list runs
  top→bottom from system/agent level ("Across a fleet", "Inside the agent runtime",
  "Inside tools") to model-internal level ("Inside weights", "Inside attention").
  The book's thesis (and the figure's own caption "Model intelligence ≠ system
  intelligence", plus the chapter references Ch18/Ch20/Ch19/Ch24 at the top) is that
  intelligence is increasingly EXTERNALIZED upward to fleets/agents/tools. An arrow
  pointing down toward "Inside weights", labeled "more of the intelligence and compute
  budget", reads as "more intelligence lives in the model's weights", which is the
  opposite of the figure's message.
- Why it matters: Section 23/24 figure-composition and figure-causality. The
  direction pointer is the one semantic cue a reader uses to interpret the ranking;
  pointing it opposite the intended externalization narrative can make a careful
  reader infer the reverse conclusion. (This is the one figure item where I confirm
  the geometry from source; whether the intended reading is "moving down = more
  budget in weights" is the author's call, so flagging for confirmation rather than
  as a definite error.)
- Recommended: That the arrow point UP (head near the fleet/agent rows above the
  label) — or, if the down-arrow is intentional, that the label be reworded (e.g.
  "shifting away from model-internal, toward system-level") so the arrow and label
  agree with the externalization message.

### NEW FINDING #3 — [MINOR][residual of FIX #4][figure-composition] Fig 15.1 the two
###     bottom annotation blocks still nearly abut on the second line
- Location: Fig 15.1 (rendered pp.175, `render/fig_ch15_flashattn.py`).
- Problem: Although PASS-17's fix centered each O(L²)/O(L) annotation under its own
  panel, the long second lines "every query re-reads the row-block" (red) and "each
  tile read once, softmax online" (green) are on the same baseline and collide into
  the inter-panel gutter: red second line right edge = x 302.4, green second line left
  edge = x 309.5, only ~7pt apart (panels themselves are ~19pt apart). At reading scale
  the two annotation lines join into a single continuous strip and can be misattributed.
- Why it matters: PASS-17 flagged exactly this MINOR composition defect; the intended
  widening did not fully take, so the cramped/colliding-into-the-middle issue persists.
- Recommended: Offset the two annotation blocks vertically (e.g. stack them at
  different baselines) or frame each within its own panel box, so each sits
  unambiguously under its own panel and no line crosses the gutter.

--------------------------------------------------------------------------------

## C. WHAT WAS VERIFIED THIS PASS — NO ISSUE (sweep was thorough, not shallow)

- Fig 16.1 (p.189): source confirms the red break-even star is plotted at
  be = 148000/0.0208 = 7.115M, axvline at 2.6e7 = 26M, "canonical 26M req/mo" text
  placed to the left of the axvline, self-host=148000/cloud=72000/0.0208×req line.
  An apparent vision "misplacement" of the star/axvline is a log-axis-scale reading
  artifact — the generator places them correctly at 7.1M and 26M. DROPPED as artifact.
- Fig 22.1 (p.246): the "+17% @9.2K / +60% @32K / ~2.4× @128K" annotations and the
  per-request (2NL vs 4·n·L²·d) vs per-token (fixed 2N) panels are correct; the
  two-panel "different units" warning is present; the 128K callout sits at the right
  edge of the 0.8–128K range, so it is within the plotted axis (not outside as a
  casual vision read suggested). DROPPED as artifact.
- Fig 19.2 (p.220): (a) tokens accumulate I0+T·δ+T·γ = 9,200+800·T+65·T; (b) KV
  24.9→34.0 GB rising linearly ~2.3 GB/turn, annotations match; ylim on (b) set to 38
  so the 34.0 label is not clipped. Consistent.
- Fig 17.1, 18.1, 21.1, 26.1, A.2: legible, internally consistent; no new data
  correctness defect. A.2 correctly warns "NOT COMPARABLE ACROSS PANELS" (vendor
  reductions relative to each model's own predecessor) and uses per-panel y-limits.
- Back matter Sources/Method (p.304): the two-axis [PROVENANCE][EPISTEMIC-STATUS]
  labelling taxonomy is complete and consistent; only micro-typesetting note is the
  hyphenation of "[ILLUSTRATIVE][ASSUMP- TION]" across a line break in the worked
  example — a cosmetic widow/hyphenation artifact, not a content issue.

--------------------------------------------------------------------------------

## D. REMAINING-RISK ASSESSMENT

- No CRITICAL or MAJOR finding in ch15–27+back matter this pass. The three substantive
  PASS-17 fixes (Fig A.1 linear re-encoding, Ch18 §3.2 basis note, Ch16 §16.4
  provisioning-sensitivity) are confirmed landed and correct.
- The genuinely new items are: (1) Fig 20.1 "~27 hosts" vs the book's "≈28 hosts"
  one-host rounding mismatch (source-confirmed, ceiling-convention inconsistency);
  (2) Fig A.4 leader-arrow direction vs its "more of the intelligence" label (source-
  confirmed geometry; flagged for author confirmation of intent); (3) Fig 15.1
  annotation-gap fix only partially resolved (residual MINOR composition item).
- All three are MINOR. No new MODERATE/MAJOR defects surfaced.
