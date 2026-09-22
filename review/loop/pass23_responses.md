# PASS-23 RESPONSES — muse-spark-1.3 review (conceptual + dedicated figure pass)

Two reviews land together as PASS-23 (manuscript/technical) and PASS-23b (dedicated
figure/diagram quality). Both from muse-spark-1.3-contributor-free, 2026-09-21 build.
The reviewer's conclusion: the manuscript is strong; remaining issues are higher-order
(conceptual precision, residual overclaims, transfer, visual semantics), NOT elementary.
The reviewer explicitly separates kernel-regime from capacity-deficit, and for figures
asks "is this book-quality at print size, or slide-quality scaled down?"

## A. CONCEPTUAL / TECHNICAL (PASS-23) — addressed
A1/A3. Introduced the hard **kernel-regime vs workload-capacity-deficit** distinction spine-wide
   (Ch6, Ch15). Reordered Ch6 prefill argument (arithmetic-intensity first, then the single-device
   1.19-vs-0.989 capacity illustration). Replaced categorical prefill/decode pronouncements with
   operating-regime/qualified language.
A4. Softened "FlashAttention = single highest-impact optimization" to "one of the first kernel-level
   optimizations to validate" (Ch15 mental model).
A5. Reinterpreted Fig 2.1 heuristic ("commonly occupies a higher/lower arithmetic-intensity regime";
   "a property of the model × workload × kernel × hardware operating point").
B1. Rewrote Ch15 mental model: KV management is a cross-cutting state plane (spans prefill+decode),
   not a stage after generation; "output decoding" -> "detokenization / streaming." New pipeline:
   preprocessing/tokenization -> prefill -> iterative model decode -> sampling -> detokenization.
B2. Named the 140-B weight read the "logical model-weight footprint / canonical weight-stream
   approximation" at first rigorous derivation (Ch2), with a scope caveat.
B3. (Still open) 64-GB runtime reserve as named scenario assumption + sensitivity C_reserve=32/64/96.
B4. Renamed ~2.1 req/s the "KV/service-time analytical bound (not measured throughput)" in Fig 20.1
   title/caption and Ch20.
C1/C2. Clarified 100 "active users" vs ~344 in-flight requests (Ch4), and defined the 40-rps peak as
   sustained over the provisioning burst interval.
D1-D3. Ch24 Red Team: removed premature "generous concurrency headroom" label; changed "flips A->B" to
   "A is eliminated; B remains a candidate pending measured sustained prefill efficiency + SLO
   validation"; removed the ungrounded "four NINES" (now "do we still meet the required
   availability/SLO at peak with a node down").
E1. PIES renamed an "illustrative local attack-surface count," equivalence rule (NLE <=0.25 put in the
   definition before any number), explicitly a pedagogical toy metric.
F. (Open/extended) Part-divider orientation lines, chapter-opening question/number/decision,
   counter-scenarios at Part ends, moving the quadratic-attention correction earlier into Ch8,
   Ch22 as synthesis-not-repair, Ch21/25/26 structural tightening.
H. (Partly addressed; H4 GB/GiB, H5 glossary, H6 evidence-tag density — see open-items note.)
I1. Copyright page: "All rights reserved" + source-available contradiction fixed
   ("Copyright © 2026 Zhiqi Tao. Licensed under...") in book.tex and titlepage.tex.
I2. Appendix A retitled "2026 Frontier Architecture Signals: Four Open-Weight Model Families" +
   "Snapshot: September 2026"; Fig A.2 caption strengthened ("do NOT compare bar heights as
   absolute efficiency").
I3. (Open) references integrity audit. I5. (Open) word-join/discretionary-hyphen source pass.

## B. FIGURES (PASS-23b) — addressed
P0. **Fig 2.1 REDESIGNED** (was a visible publication defect: overlapping labels). Rebuilt as two
   clean bands, text-sized boxes, 10 labels verified legible, light-fill + dark-text (grayscale-
   friendly), explicit KV-conduit + "created in prefill / reused in decode" caption, qualified
   resource-regime language in a bottom strip. Verified at source and at book print scale.
Fig 2.2 rebuilt as an **arithmetic-intensity continuum** (decode at low batch on the memory-bound
   side, long-prompt prefill toward the compute side, roofline ridge, knobs that move a point).
Fig 8.2: added in-plot "PER GPU" box + grayscale-distinguishable H100/H200 line/marker styles.
Fig 7.2: restored (reviewer "preserve" list — avoided over-engineering a good figure).
Fig 7.4: added AGGREGATE-RESIDENCY-SCREEN warning, 8 GPU partition lines, "scenario reserve" label.
Fig 22.1: added the prominent LEFT/ RIGHT units "DO NOT COMPARE" warning and decomposed the prefill
   panel into linear + quadratic attention term.
Fig A.2: already independent panels; strengthened the "DIFFERENT BASELINES" banner + caption.
Fig 19.2/19.3: added "append-only illustrative model" in-plot, grayscale hatchable components.
Fig 16.1: added the [ILLUSTRATIVE] price-sensitivity band (break-even range 5.9-9.9M req/mo).
Fig 12.1: **REDESIGNED** as the candidate-synthesis reasoning chain (Requirements -> Constraints ->
   Candidates -> Test against memory/latency/economics -> Survivors/Rejected).
Fig 11.3: KV transfer now the dominant thick arrow, separated from thin request flow; pools labeled
   "prefill-optimized"/"decode-optimized" (not categorical compute/bound).
Fig 15.1: HBM + on-chip memory as explicit physical regions; BEFORE 7 arrows vs AFTER 2 (data-movement
   visible without labels); all labels clear of arrows.

Remaining figure work (still OPEN): Fig 10.2 repeated-template REDESIGN, Fig 8.1 physical-hierarchy
mapping, Fig 17.1 failed-replica/N=max redesign, Fig 10.1/5.1/11.2/13.1/21.1/23.1/26.1/A.4
MAJOR-revisions, Fig 26.2 capstone, and the systematic font-floor / overlap-QA / grayscale test /
figure-width rules.

## Honest status
The highest-priority items — the P0 Fig 2.1 publication defect, the spine-wide kernel-vs-capacity
correction, the Ch15 mental model, the Ch24 Red-Team rigor, the PIES framing, the copyright page,
the Appendix title/date, and the highest-value figure redesigns (2.1/2.2/7.4/12.1/11.3/15.1/16.1/
22.1/19.x/A.2/8.2) — are addressed and (for figures) verified. A meaningful tail of MAJOR-revision
figure redesigns and structural/open-items remain; the review is being worked iteratively, not
declared fully closed.
