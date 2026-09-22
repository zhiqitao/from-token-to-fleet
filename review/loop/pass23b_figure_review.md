# PASS-23b — DEDICATED FIGURE / DIAGRAM QUALITY REVIEW (visual-causal second pass)

Reviewer: muse-spark-1.3-contributor-free (second, figure-dedicated pass). Date: 2026-09-21.
Threshold: at normal printed-book size, is the figure comfortable, intentional, visually balanced,
immediately interpretable, and materially better than prose alone? Not "readable when zoomed."

Verdict scale: KEEP / POLISH / MAJOR REVISION / REDESIGN / REMOVE-MERGE.

---
## GLOBAL
- Figure quality uneven; quantitative charts stronger than conceptual box-and-arrow diagrams.
- Recurring issues: (1) same flowchart grammar for semantically different relationships; (2) scale —
  diagrams occupy part of text width with small labels; (3) annotation density (figure = annotated
  poster); (4) caption dependence (long captions rescue weak composition); (5) undefined visual
  semantics.
- Establish a reusable visual grammar: solid arrow=data/request flow, dashed=control/decision,
  loop=iteration, thick/double=high-volume data movement, bounded container=host/pool/system
  boundary, orange=persistent KV/state, blue=compute, gray=request/data, diamond=decision,
  stacked=replicas, interconnect drawn distinctly.

## PER FIGURE VERDICT
- Front-matter Decision Loop: KEEP/POLISH (high standard; feedback must be unmistakable; later
  chapters show a tiny version with current stage highlighted).
- Front-matter "Reading the book by number": MAJOR REVISION/POSSIBLE REDESIGN (too dense at normal
  size; split info hierarchy or full-page landscape).
- Fig 1.1 KV cache: POLISH (make persistence visible; K/V not transient-style).
- Fig 1.2 token travels: MAJOR REVISION (KV is branching stored state, not a linear pipeline stage;
  branch to OUTPUT REPRESENTATION and K/V STATE; compatible semantics with Fig 2.1).
- **Fig 2.1 canonical pipeline: REDESIGN — HIGH PRIORITY.** Visible overlap/collision at top of
  PREFILL and start of DECODE; italic header collides with first gray box; red iterate label
  squeezed; right-side green annotations too small/fitted. Too many visual channels + too many
  lessons at once. Rebuild as two clean lanes (PREFILL / DECODE), generous spacing, secondary
  observations (max 3 each), resource-regime notes in a separate bottom strip, and qualify
  "compute-bound"/"bandwidth-bound" (operating-regime language, not categorical). "read weights from
  HBM every step" → "execute model layers; repeated weight traffic" + "at low batch, weight traffic
  can make decode HBM-bandwidth sensitive."
- Fig 2.2 decode vs prefill: MAJOR REVISION. Binary "decode=bandwidth/prefill=compute" is dangerous
  if unqualified. Encode continuum/regime (arithmetic-intensity axis with example operating points),
  prepare for Ch8 roofline.
- Fig 3.1 dense vs MoE: POLISH (three dimensions visually distinct: resident weights / active compute
  / attention-KV structure; don't imply fewer experts = proportionally less KV; align vertically).
- Fig 4.1 six-dimension: POLISH/MAJOR (map dimensions → consequences; avoid six-boxes taxonomy and
  radar aesthetics).
- Fig 5.1 model selection: MAJOR REVISION (dense relative to size; emphasize retrieval vs generation
  fork; concise labels; use page width).
- Fig 6.1 metric hierarchy: POLISH (make causal diagnosis obvious — the diagnostic-chain direction).
- Fig 6.2 latency distribution: KEEP/POLISH (tail obvious without color; avoid label crowd).
- Fig 7.1 GQA: KEEP/POLISH (many-to-one mapping dominant; grouping/brackets over tiny labels).
- Fig 7.2 KV size vs context: KEEP (label full-MHA baseline / GQA / precision in-figure; grayscale
  distinguishability; add in-plot note "KV determined by attention geometry, not parameter count").
- Fig 7.3 memory floor: POLISH (comparable aligned stacks; units visible; mark illustrative).
- Fig 7.4 concurrency budget: **MAJOR REVISION.** Put "AGGREGATE RESIDENCY SCREEN ≠ PER-RANK FIT
  GUARANTEE" directly in the figure; don't make 640GB look like one allocatable heap; draw 8 lightly
  separated GPU partitions behind the aggregate bar; distinguish weights / runtime-workspace reserve /
  KV budget / unavailable; mark 64GB "scenario reserve".
- Fig 7.5 memory Tetris: **MAJOR REVISION.** Aggregate first-order screen → not placement proof;
  identical scales across 9.5K/32K/128K; put aggregate/per-rank warning in-figure. Possibly MERGE
  with 7.4 (7.4 = where capacity goes; 7.5 = how context length changes allocation).
- Fig 8.1 hardware hierarchy: **MAJOR REVISION.** Physical hierarchy (registers/on-chip → HBM → GPU
  interconnect → other GPU/node) with distance/capacity/bandwidth/latency/location meaningful;
  map inference mechanisms (FlashAttention, weight/KV residency, tensor cores, TP communication) as
  examples; enlarge.
- Fig 8.2 roofline: KEEP/POLISH. Make memory-bound slope / compute plateau / ridge / decode / prefill
  unmistakable; grayscale-distinguishable line styles; "PER GPU" inside the plotting area.
- Fig 9.1 all-reduce: KEEP/POLISH (distinguish idealized/derived vs measured; label log axes).
- Fig 10.1 composing dims: MAJOR REVISION (make composition concrete: what partitioned/replicated/
  which boundary/what communication; common model+GPU template progressively overlaid).
- **Fig 10.2 five strategies: REDESIGN.** Repeat the SAME base visual 5×; each mini-panel shows
  PARTITIONED / REPLICATED / COMMUNICATION in identical positions; teach dimensional structure.
- Fig 11.1 discrete vs continuous batching: KEEP/POLISH (time direction obvious, request identity
  persistent, completed + refill visible without color).
- Fig 11.2 serving stack: MAJOR REVISION. Stack implies false layering; reorganize around concerns
  (request scheduling / state management / reuse / resource specialization) rather than equivalent
  stack layers.
- Fig 11.3 P/D disaggregation: MAJOR REVISION (make KV transfer visually dominant; separate
  request/control flow from KV data transfer; "prefill-optimized/decode-optimized" not categorical
  compute-bound/bandwidth-bound).
- **Fig 12.1 candidate synthesis: REDESIGN / HIGH PRIORITY.** Visualize REQUIREMENTS → CONSTRAINTS →
  CANDIDATES → TEST AGAINST (memory/latency/economics) → survivors/rejected; not just 3 config boxes.
- Fig 13.1 reference-architecture ladder: MAJOR REVISION (ladder implies monotonic better; make
  escalation triggers important; add lateral branches; scope to canonical serving if so).
- Fig 14.1 capability screen vs deployment benchmark: KEEP/POLISH (strong; two-question gate; reuse
  mini version in Ch5).
- Fig 15.1 FlashAttention: MAJOR REVISION (HBM/on-chip explicit physical regions; BEFORE/AFTER via
  visible DATA MOVEMENT not labels; arrow count/path length/repeated traffic; reuse Fig 8.1 hierarchy).
- Fig 15.2 prefix caching vs batching: POLISH (label "primary/direct effect"; distinguish LESS WORK
  from BETTER UTILIZATION).
- Fig 16.1 TCO break-even: MAJOR REVISION (single crossover implies false precision; show sensitivity
  band/scenarios; "decision changes as assumptions move").
- Fig 17.1 fleet of one model: MAJOR REVISION / POSSIBLE REMOVE (too elementary at this stage; add
  failed replica / capacity / SLO / failure domain; or visualize N = max(capacity, SLO, failure)).
- Fig 18.1 routing tree: POLISH (label illustrative policy tree; distinguish hard capability gate /
  cost-latency policy / fallback; routing itself has latency/error).
- Fig 19.1 agent loop: KEEP/POLISH (terminal outcomes distinct from loop states; clean cycle).
- Fig 19.2 agent token/KV growth: KEEP (explicit append-only assumption in-plot).
- Fig 19.3 agentic context block: KEEP/POLISH (append-only illustrative model in visual; braces/
  aggregate blocks; grayscale).
- **Fig 20.1 fleet throughput/utilization: MAJOR REVISION.** Title/label must call ~2.1 req/s an
  "analytical KV/service-time capacity bound," not observed throughput; lower panel is
  offered-load/capacity utilization, not GPU SM/HBM; distinguish 100% saturation from operational
  70% target (label 70% illustrative). (Partially done in PASS-23 text edits — figure titles/labels
  now updated; confirm plot renders.)
- Fig 21.1 AI factory pipeline: MAJOR REVISION (emphasize measurement gates — capability regression /
  workload replay / TTFT-TPOT-goodput / memory-KV / fleet capacity / economics / canary / rollback —
  not generic CI/CD stages).
- Fig 22.1 prefill quadratic vs decode: KEEP/MAJOR POLISH ("LEFT: PER REQUEST / RIGHT: PER GENERATED
  TOKEN / DO NOT COMPARE Y-AXIS" in-graphic; decompose prefill into linear + quadratic term).
- Fig 23.1 vague ask → bounds: MAJOR REVISION (concrete example row flowing across stages, e.g.
  "must feel instant" → p95 TTFT target → queue/service budget → capacity implication).
- Fig 24.1 red/green team cycle: POLISH/MAJOR (Red attacks assumptions/evidence/failure modes;
  propose→challenge→measure→revise→retest; not symmetrical decorative halves).
- Fig 25.1 anatomy of ADR: POLISH (prioritize structure: context/decision/alternatives/evidence/
  consequences/validation/invalidation-revisit; don't cram full ADR into figure).
- Fig 26.1 workload fingerprints: MAJOR REVISION (radar/spider charts exaggerate; small-multiples
  matrix rows=workload, cols=six dims, cells=low/med/high; axes are characterization dims, not a
  comparable metric space).
- Fig 26.2 pattern application: MAJOR REVISION (capstone; see remaining review text — cut off).
