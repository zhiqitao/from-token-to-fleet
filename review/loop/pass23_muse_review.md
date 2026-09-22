# PASS-23 REVIEW — muse-spark-1.3-contributor-free, 2026-09-21 build

Reviewer: muse-spark-1.3-contributor-free (OpenCode CLI), fed the full 55-section review prompt +
full PDF text layer (chunked). Date: 2026-09-21. Build reviewed: PASS-21 `af691e6` (308pp).

This is an independent-model re-review applying the attached governing standard. Verdict: strong
manuscript, but not yet freeze — remaining issues are higher-order (conceptual precision, residual
overclaims, transfer, visual semantics) rather than elementary errors.

Source: pasted by Zhiqi (the muse-spark run that was being set up; findings transcribed here).

---
## STRUCTURED FINDINGS (triaged from the prose review)

### A. The single most important conceptual correction (spine-wide)
A1. **Separate "kernel regime" (arithmetic intensity vs roofline ridge) from "workload capacity
    deficit" (aggregate offered demand vs achievable service capacity)** — the last big conceptual
    ambiguity running through multiple chapters.
A2. Reorder Ch6 prefill pedagogical argument: establish arithmetic-intensity/ridge first, then use
    the 1.19-vs-0.989-PFLOP/s comparison only as a single-device deadline/capacity illustration.
A3. Ch15: distinguish these; don't let "prefill is compute-capacity constrained" collapse to
    "compute-bound."
A4. Ch15: soften "FlashAttention vs SDPA is the single highest-impact optimization."
A5. Intro heuristic in List of Figures (Fig 2.1 "prefill stresses compute / decode stresses HBM")
    should be reinterpreted through the roofline framework with the canonical sentence.

### B. Causal / terminology precision
B1. Ch15 mental model: KV management is a cross-cutting state-management plane, not a sequential
    stage after generation; "output decoding" → detokenization/streaming. New pipeline:
    preprocessing/tokenization → prefill → iterative model decode → token sampling/selection →
    detokenization/streaming, with KV management spanning prefill+decode.
B2. "Full forward pass over the weights" / 140-GB-per-token — name as "logical model-weight footprint
    used as a first-order HBM traffic approximation" at first rigorous derivation; later refer to
    "the canonical weight-stream approximation."
B3. ~64-GB runtime/activation/workspace/NCCL reserve: elevate to a named canonical scenario
    assumption and sensitivity-test (C_reserve = 32/64/96 GB).
B4. ~18 req/host → 2.1 req/s → ~20 hosts: it's C/W (concurrency/service time), not an independent
    throughput model. In Fig 20.1 + captions, call the line "KV/service-time analytical bound" not
    "fleet throughput" (carry the qualifier into the plot title).

### C. Canonical workload semantics
C1. "2,000 registered users × 5% concurrent = 100 users" vs ~344 in-flight requests (Little's Law at
    40rps × 8.6s): clarify. Prefer "~100 active users in the modeled activity window" unless true
    multi-outstanding-request concurrency is intended.
C2. 40-rps peak needs a duration/window definition ("sustained over the provisioning burst interval").

### D. Ch24 Red Team
D1. Don't label Candidate B "generous concurrency headroom" before the analysis.
D2. Conclusion "flips recommendation A→B" too strong; outcome = "A is eliminated; B remains a
    candidate pending measured sustained prefill efficiency and SLO validation."
D3. "four NINES at peak with a node down" ungrounded (no 99.99% requirement established); change to
    "do we still meet the required availability/SLO at peak with a node down?"

### E. PIES
E1. Rename "illustrative local attack-surface count"; make the equivalence rule part of the
    definition before any number; consider replacing with a more operational red-team measurement
    (attack-suite success rate by family/entry + FP/utility cost).

### F. Structure / delivery
F1. Part divider pages: add "you now know X / Part answers Y / you will be able to calculate Z."
F2. Chapter openings: explicit "Question this chapter answers / number you will derive / decision it
    enables."
F3. Part IV→V transition framing; Part VI as culmination (Ch22 = theorem, earlier = lemmas).
F4. Add compact counter-scenarios at ends of Parts II–V (change 2-3 workload dimensions, ask what
    flips).
F5. Move the 4·n_layers·L²·d quadratic-attention correction earlier into Ch8 (not just Ch22).
F6. Ch22 should synthesize not repair — move new technical deepening to its technical home.
F7. Ch21 "AI Factory": anchor to token-to-fleet promotion gates; trim generic MLOps overlap.
F8. Ch25 ADR: record rejected alternatives, evidence class, assumptions, sensitivity, validation
    criteria, invalidation triggers.
F9. Ch26 patterns: disciplined fields (symptom/diagnostic evidence/bottleneck/mechanism/applicability
    conditions/trade-off/failure mode/measurement/consequence).

### G. Figures (visual/causal, not just readable — redo the weak ones)
G1. General visual grammar: solid=data flow, dashed=control/decision, cylinder=state, grouped
    enclosure=host/pool, stacked=replicas, diamond=decision; explain once in Preface.
G2. FlashAttention figure: make HBM a persistent bottom visual layer, on-chip SRAM a bounded layer,
    arrow multiplicity/width for traffic reduction; "computes the same mathematical attention
    operation" not "result identical."
G3. Fig 7.4/7.5: "aggregate screen ≠ per-rank fit" callout inside the graphic; shorten captions.
G4. Fig 10.2: redesign as common model/request template repeated 5× with the split dimension
    highlighted (partitioned/replicated/communication).
G5. Fig 11.3 P/D: make the KV transfer visually dominant, separate from request/control flow,
    annotate scale dependence.
G6. Fig 12.1: visually trace requirement → constraint → candidate difference → reject/accept.
G7. Fig 13.1: ladder implies monotonic escalation — rename or add lateral branches.
G8. Fig 14.1: capability-screen vs deployment-benchmark distinction earlier (Ch5 preview).
G9. Fig 15.2: label "primary/direct effect"; don't imply cache only affects prefill, batching only
    decode.
G10. Fig 16.1 TCO: add sensitivity band / alternate utilization curves; separate marginal vs fully
    loaded ownership economics.
G11. Fig 17.1: add failure domains / unavailable replica / capacity+SLO annotation.
G12. Fleet host-count: one canonical equation N = max(N_compute, N_KV/service, N_reliability, …).
G13. Fig 18.1 routing: label "illustrative policy tree"; routing can be wrong / costs latency.
G14. Figs 19.2/19.3: label linear context-growth as append-only baseline; add a bounded/summarized
    curve.
G15. Ch20 utilization: call it "capacity utilization under the analytical service bound" not GPU
    utilization.
G16. Grayscale test; ensure semantic coding survives monochrome (hatching/borders/labels).
G17. Some figures too small / too much whitespace; use more of the text width.
G18. Tables >4 dimensions: split or move detail to appendix.

### H. Terminology / global
H1. host/node ("host = one server containing 8 GPUs"); use node only for topology.
H2. QPS/RPS — prefer req/s; reserve QPS for user-visible query==request.
H3. token throughput: avoid aggregate tokens/s where input/output composition matters.
H4. GB/GiB: one-time statement that canonical values use decimal GB.
H5. Glossary audit against book usage (host/node, concurrency, active user, in-flight, throughput/
    goodput, service time/latency, TPOT/ITL, KV/prefix/prompt cache, instance/replica, total/active
    params, FLOP/FLOP/s).
H6. Evidence-tag density: consider badges only on figures/tables/numbers/contested claims, let
    stable prose read normally.

### I. Front matter / legal / references
I1. Copyright/license: "Copyright © 2026 Zhiqi Tao. Licensed under…"; verify LICENSE text matches the
    summary.
I2. Appendix title "What the Latest Open Models Tell Us" too broad → "2026 Frontier Architecture
    Signals: Four Open-Weight Model Families" (or similar); strong date-stamp "Snapshot: September
    2026"; keep vendor-reported phrasing for "first open 3T-class"/"first natively multimodal GLM."
I3. References integrity: key resolution, URL/arXivId/model-card path match, vendor-claim labels,
    access dates. Automated final pass.
I4. Membership/scope: reduce duplicate frontier-model detail in core chapters; prefer architectural
    property first, model name second.
I5. Word-join/discretionary-hyphen artifacts ("itstresses", "runsfrom", "total-costreality") — source
    copyedit pass.

### J. Publication judgment
The book's architecture is now strong; path to quality = (1) line-by-line canonical arithmetic and
terminology consistency audit, (2) figure-by-figure visual/causal audit at print size. Do NOT expand
scope; sharpen causal relationships, eliminate overclaims, improve transfer, redesign weakest figures.
