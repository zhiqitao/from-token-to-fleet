# PASS-17 REVIEW — Chapters 1–14 (rendered PDF, pp. 22–170) — NEW FINDINGS

Applied the complete 55-section review prompt to ch01–ch14 as rendered in
`/home/ubuntu/from-token-to-fleet-v20260913-full.pdf` (ch1 starts PDF p.22, ch15 starts p.171).
I read the full rendered text of every chapter and **visually inspected all 25 figure/diagram pages**
(pp. 25, 26, 33, 37, 52, 68, 81, 84, 86, 98, 102, 103, 104, 105, 110, 114, 122, 130, 135, 140, 145, 146,
156, 163, 169) plus key tables (Table 4-3, Table 7-1) and equation pages (pp. 113, 151), rendering each to
image and inspecting visually rather than relying on extracted text. I also re-ran the chapter numeric
arithmetic (KV per-token, FLOP floor, prefill/decode bandwidth, prefill throughput, C≈18, Little's-law
host counts, cost/request) independently; every one of those canonical numbers is internally consistent
and cross-chapter consistent. All findings below are NEW — I checked them against pass1–pass16 findings
files and none was previously raised.

---

## A. WHOLE-BOOK FINDINGS

No new whole-book architectural/coherence defect was found. The token→fleet causal chain is intact,
the canonical workload (9.2K+300, 70B FP16 full-MHA, 8×H100, TTFT 1.2 s / TPOT 25 ms) is applied
consistently across ch1–14, and the prefill/decode, total-vs-active, residency-vs-active, and
measured-FP8-vs-byte-halving distinctions are all maintained. The new issues are concentrated in the
*rendered figures* (label clipping, a figure-vs-prose numeric mismatch, and a figure-vs-framework
mismatch) — the exact category text-only review misses, which is why earlier passes converged at zero.

The single most important whole-book observation from this pass: **the residual defects are almost
entirely publication-quality figure defects rather than reasoning/numerical defects.** Most are in
figure label clipping that is invisible in the source .md and in extracted text.

---

## D. FIGURE / DIAGRAM / TABLE FINDINGS (primary yield of this pass)

### [P17-1] CRITICAL — Figure 8.1 ladder labels are clipped/truncated in the rendered book
- **Location:** Chapter 8 (Compute), figure 8.1 "Where inference computation and data movement actually live", PDF p.110 (book p.90). Renders from `render/fig_ch8_hierarchy.py` (docstring names it fig-08-0802; displayed as figure 8.1).
- **Problem:** The seven hierarchy boxes are 168 pt wide, but the bold 11.5-pt first-line labels are wider than the box, so text is cut by the box edges. In the published render, six of the seven boxes show clipped labels:
  - registers → "fastest · smalles" (final "t" clipped)
  - tensor cores / ALU → "ensor cores / A"
  - shared mem (SRAM) → "red mem (SR"
  - HBM (GPU memory) → "M (GPU memo"
  - GPU interconnect → "PU interconne"
  - other GPUs / remote → "er GPUs / rem"
  - Also the figure title "Where inference computation…" and the sub-title "what runs here → speed ↔ capacity" collide with/overlap the topmost registers box.
- **Why it matters:** §23/§49 of the prompt demand no clipped content in a publication-quality figure. This diagram is the book's hardware-causal-model anchor (the compute/memory/interconnect ladder). Six of seven primary labels being truncated is unacceptable and directly undermines the hardware-hierarchy lesson.
- **Recommended change:** In the generator, either widen `ladder_w` (and the box x-extent) so each first-line label fits inside its box, reduce the label `FS`, or break long labels onto two lines. Ensure `name` and `role` text stay inside the box with padding; lower the title so it no longer overlaps node 1. Regenerate `fig-08-0802.png` and rebuild.

### [P17-2] MAJOR — Figure 10.2 labels are clipped/truncated
- **Location:** Chapter 10 (Parallelism), figure 10.2 "The five parallelization strategies and what each splits", PDF p.135 (book p.115).
- **Problem:** Parent-box sub-labels are clipped at the right box edge:
  - "PP · Pipeline Parallel" renders as "PP · Pipeline Paralle" (final "l" lost)
  - "CP · Context Parallel" renders as "CP · Context Paralle" (final "l" lost)
  - Expert-Parallel child box "GPU B" reads "experts 6-1" — the "0" of "6-10" is clipped at the box edge (reader sees an incorrect expert range).
- **Why it matters:** Same §23/§49 defect as P17-1. The "experts 6-1" error is not merely cosmetic — it misstates the expert split, which is a factual error introduced by clipping.
- **Recommended change:** Widen the parent/child boxes (or shorten "Parallel"→"Par." / the "experts 6-10" text) so nothing clips; regenerate and rebuild.

### [P17-3] MAJOR — Figure 7.3 full-fine-tune bar (~1260 GB) contradicts the body text (~1120 GB)
- **Location:** Chapter 7 (Memory), figure 7.3 "Memory floor: inference vs fine-tuning (70B)", PDF p.103 (book p.83). Labels the full-fine-tune bar "~1260 GB".
- **Problem:** The body text defines the full-Adam fine-tuning floor as **~1,120 GB** (Table 7-2 "~1,120 GB"; §7.7 explicitly "weights 140 GB + gradients 140 GB + Adam m/v/master states 840 GB = 1,120 GB"; §7.8 "~1,120 GB"). The figure's full-fine-tune bar is labeled **~1260 GB**, a ~140 GB / ~12% discrepancy. Also the figure's QLoRA bar (~60 GB) sits within the text's "~50–70 GB" range and inference (~165 GB) matches, so only the fine-tune value is off. (The x-tick label "Full fine-tune (weights+grad+optimizer)" is also truncated to "…optimiz…", and the QLoRA x-label is partly covered by the green "QLoRA fits a single H100" annotation arrow.)
- **Why it matters:** §5 numerical audit and §45 figure-vs-prose contradiction. This is the chapter's central memory-takeaway number (inference vs training floor). Two different authoritative values (1120 vs 1260) for the same quantity will leave a reader unsure which to trust, and the 1.75× 8×H100 framing in the text is reproduced from 1120/640, not 1260/640 (=1.97×).
- **Recommended change:** Make the figure's full-fine-tune bar match the body's ~1,120 GB (or, if a different assumption such as fp32 weights/gradients is intended, state it and update the text+Table 7-2+§7.7/§7.8 to match). Fix the truncated x-tick and the arrow/label overlap.

### [P17-4] MODERATE — Figure 4.1's "six dimensions" do not match the chapter's six-dimension framework
- **Location:** Chapter 4 (The Anatomy of an AI Workload), figure 4.1 "Six-dimension workload characterization → architectural consequences", PDF p.68 (book p.48). Renders from `render/fig_batch1.py` lines 43–44.
- **Problem:** §4.2.1 defines the six canonical dimensions as **Quality, Traffic, Token profile, Latency, Economic constraints, Operational constraints.** But the figure's six left-column axes are **Throughput / RPS, SLO / latency, Context length, KV / input, Modality, Concurrency & burst** (→ sizing/serving, TTFT/TPOT, KV & memory, KV cache, encoder/P-D split, batch/autoscale). The figure therefore swaps out Quality, Economic, and Operational (the framework's own dimensions) and substitutes Context length, KV/input, Modality, Concurrency & burst, which are sub-characteristics, not framework dimensions.
- **Why it matters:** §24 figure causality and §45 figure-vs-prose consistency. This is the chapter's signature framework, and the figure explicitly claims to map "six-dimension workload characterization." A figure that shows a different six than the six the chapter just taught will cause a careful reader to mis-remember the framework (and its quality/economic/operational axes).
- **Recommended change:** Align the figure's six left-column labels to the six framework dimensions (quality, traffic, token profile, latency, economic, operational) with their true architectural consequences, or, if the figure is meant to be a different "characteristics→decision" mapping, retitle it (e.g. "Workload characteristics → consequences") so it no longer claims to be the six-dimension framework.

### [P17-5] MODERATE — Figure 6.1 "diagnostic chain" lacks directionality and a legend
- **Location:** Chapter 6 (Measuring What Matters), figure 6.1 "The metric hierarchy as a diagnostic chain", PDF p.84 (book p.64).
- **Problem:** The three-layer stack (Workload / Resource / Serving) is joined by a solid-green line on the left and a red dashed line on the right, but there are **no arrowheads and no legend** explaining the two line styles or the direction. The chapter text (§6.2.1/§6.8) stresses that "causation runs downward (workload → resource demand → serving behavior); diagnosis runs upward," i.e. the chain is directional, yet the figure conveys only "three related boxes." Also, §6.2.1 lists the hierarchy as 1. Workload, 2. Serving, 3. Resource, while the figure orders them top-to-bottom as Workload / Resource / Serving (a minor ordering inconsistency).
- **Why it matters:** §24 (figure causality). The prompt says "a technically correct figure can still be intellectually weak" and that a figure requiring prose to rescue its meaning should be improved. Here the reader must read the caption+text to learn there is a direction at all.
- **Recommended change:** Add directional arrowheads (e.g. a solid downward arrow labelled "causes" and a dashed upward arrow labelled "diagnose") and a short legend; align the layer ordering with §6.2.1's numbering.

### [P17-6] MODERATE — Figure 10.1 band titles overprint the boxes they describe
- **Location:** Chapter 10, figure 10.1 "Composing the parallel dimensions", PDF p.130 (book p.110).
- **Problem:** The orange band titles "Expert parallel (all-to-all)" and "Pipeline (DP × TP × PP)" are drawn directly on top of the box borders / top edges of the boxes they label, causing visual occlusion (the "Expert parallel…" title is intersected by the GPU-A box; the "Pipeline…" title overlays the PP stage boxes). Inside the purple composition box, the bold title "the per-stage DP × TP mesh" overprints the monospaced sentence "the same GPUs also take part in EP all-to-all".
- **Why it matters:** §23 (overlapping/cramped, weak visual hierarchy). Reduces the multi-level·composition figure's readability.
- **Recommended change:** Move band titles above (not on) their dashed containers, and separate the purple box's title from its sub-sentence (title above, sentence below, with spacing).

### [P17-7] MINOR — Figure 6.2 mean label (0.85 s) vs body text (0.84 s)
- **Location:** Chapter 6, figure 6.2 "Latency distribution" (PDF p.86 / book p.66); §6.4.1.
- **Problem:** The figure labels the mean "mean = 0.85s", while §6.4.1 states "E[L] ≈ 0.99 × 0.8 + 0.01 × 5.0 ≈ 0.84 s". (The percentile marker positions and labels are correct — I reproduced the generating stream with seed 42: p50=0.800, p90=0.940, p95=0.987→0.99, p99=1.334→1.33, mean=0.8468→0.85.)
- **Why it matters:** §27/figure-vs-prose numeric consistency; a small but visible mismatch between the figure and the worked text.
- **Recommended change:** Make the text and figure agree (e.g. state "≈0.85 s" and keep the two-point approximation as an approximation, or label the figure "mean ≈ 0.85s" and change §6.4.1 to "the exact stream mean ≈ 0.85 s, vs the two-point approximation 0.84 s"). Optionally note the figure is computed from the real stream while 0.84 is the analytic approximation.

### [P17-8] MINOR — Figure 7.4 runtime segment drawn too narrow; FP8 row unlabeled; title/caption mismatch
- **Location:** Chapter 7, figure 7.4 "Where a 640 GB host pool goes" (PDF p.104 / book p.84).
- **Problem:** (a) The "~64 GB runtime" segment is drawn only ~30–40 GB wide, so the KV-budget segment appears to start ~180 GB rather than the stated 140+64≈204 GB, i.e. the visual proportion under/over-represents the annotated numbers; (b) the FP8-KV row omits the "140 GB weights" and "~64 GB runtime" labels (meaning must be inferred from the FP16 row); (c) in-figure title "Fig 7.4 — Where a 640 GB host pool goes" vs caption "where a 70B host's 640 GB pool goes".
- **Why it matters:** §26/§23 — the figure is meant to make the 140/64/436 split and C≈18 (FP16) / ~33 (FP8) intuitive; the mis-proportioned runtime segment and missing FP8 labels weaken that.
- **Recommended change:** Draw the runtime segment at its true ~64 GB width so the KV segment edge matches 140+64; label weights/runtime on both rows; make the in-figure title match the caption.

### [P17-9] MINOR — Figure 7.2 legend covers data; FP8 label vs measured FP8 value; annotation overlaps budget line
- **Location:** Chapter 7, figure 7.2 "KV cache size vs context length" (PDF p.102 / book p.82).
- **Problem:** (a) The legend box covers the upper-left of the plot (over the 640 GB line and tops of curves at 1–10K); (b) the "9.2K ≈ 24 GB (FP16 bound)" annotation text overlaps the ~436 GB KV-budget dashed line; (c) the figure labels the FP8 curve "full-MHA FP8 (~1.3 MB/tok)", i.e. the byte-halving lower bound, whereas Table 4-3 / §7.5 establish the book's *operating* measured FP8 value as ~1.42 MB/tok (~54%) — a label-vs-value inconsistency on the curve.
- **Why it matters:** §23 (legend committing unnecessary eye-movement/overlay); §11 terminology — the book elsewhere is careful to distinguish measured FP8 (1.42) from byte-halving (1.31); the figure silently uses the latter.
- **Recommended change:** Move the legend outside the plot area; reposition the 9.2K annotation so it doesn't cross the KV-budget line; label the FP8 curve using the book's operating value (~1.42 MB/tok) or explicitly mark it as the theoretical byte-halving bound (as §7.5 does).

### [P17-10] MINOR — Figure 12.1 annotation overlaps the value label
- **Location:** Chapter 12 (Designing), figure 12.1 panel (2) "Prefill throughput" (PDF p.156 / book p.136).
- **Problem:** The grey note "Throttle pool: bandwidth-bound (no digit)" is placed over the (b) P/D-disagg bar and partially overlaps the "~19.8K" value label. (The rest of figure 12.1 — 164/164/20 GB, 640/80 GB ceilings, ✓/✗ verdicts — renders correctly.)
- **Why it matters:** §23 minor label-overlap.
- **Recommended change:** Reposition the note into the axes margin so it does not sit on the bar/value label.

---

## C. CROSS-CHAPTER CONSISTENCY FINDINGS

One new cross-chapter inconsistency was found, folded into D above:

- **Figure 7.3 ~1260 GB vs body ~1120 GB (P17-3).** This is the only new figure-vs-prose numerical contradiction in ch1–14; all other canonical numbers (KV 2.62/1.31/1.42 MB/tok; 24.1/24.9 GB; 164.1/165 GB; 140 GB; 1.29 PFLOP; 5.6 TB/s; 346 TFLOPS@35%; 2,471 & 19,800 tok/s; ~295 FLOP/byte; C≈18; ~344 in flight; ~5 avg/~19–20 peak hosts; $0.012/req; 16.5M in, 540K out tokens/$) were re-verified and are consistent across ch1–14.

Otherwise no new cross-chapter contradictions, no broken cross-references, and no concept-used-before-established problems were found (the backward references to the roofline/ridge in Ch6 were already scoped in prior passes).

---

## B. PAGE-BY-PAGE / LOCATION-SPECIFIC FINDINGS

All page/location-specific findings are the figure defects listed in Section D above:
- P17-1 — ch08 figure 8.1 (PDF p.110 / book p.90).
- P17-2 — ch10 figure 10.2 (PDF p.135 / book p.115).
- P17-3 — ch07 figure 7.3 (PDF p.103 / book p.83).
- P17-4 — ch04 figure 4.1 (PDF p.68 / book p.48).
- P17-5 — ch06 figure 6.1 (PDF p.84 / book p.64).
- P17-6 — ch10 figure 10.1 (PDF p.130 / book p.110).
- P17-7 — ch06 figure 6.2 (PDF p.86 / book p.66).
- P17-8 — ch07 figure 7.4 (PDF p.104 / book p.84).
- P17-9 — ch07 figure 7.2 (PDF p.102 / book p.82).
- P17-10 — ch12 figure 12.1 (PDF p.156 / book p.136).

The remaining figures visually inspected and found clean/acceptable: fig 1.1 (p25), fig 1.2 (p26), fig 2.1 (p33), fig 2.2 (p37), fig 3.1 (p52), fig 5.1 (p81), fig 7.1 (p98), fig 7.5 (p105), fig 8.2 (p114), fig 9.1 (p122), fig 11.1 (p140), fig 11.2 (p145), fig 11.3 (p146), fig 13.1 (p163), fig 14.1 (p169).

---

## F. TECHNICAL AND NUMERICAL FINDINGS

No new technical/numerical defects in the prose were found in this pass. Re-verified as correct and internally consistent:
- KV/token = 2×layers×hidden×bytes = 2,621,440 B ≈ 2.62 MB (FP16), 1,310,720 B ≈ 1.31 MB (8-bit), GQA 2×80×8×128×2 ≈ 0.33 MB/token.
- 9.2K→24.1 GB; 9.5K max→24.9 GB; 32K→83.8 GB; 128K→335.4 GB; residency 140+24.9≈165 GB (32K→224, 128K→475); KV budget 640−140−64=436 GB; C≈18 FP16 (436÷24.9), ~33 FP8 (436÷13.4).
- Prefill FLOP floor 2×70e9×9.2e3 = 1.288 PFLOP; rate 1.29/1.08 ≈ 1.19 PFLOPS; sustained 989×0.35≈346 TFLOPS; 2,471 tok/s per GPU; ×8≈19,800/host; ridge 989/3.35≈295 FLOP/byte; decode intensity 140 GFLOP/140 GB ≈ 1.0 FLOP/byte; decode 140/0.025=5.6 TB/s.
- Little's law 100/10 = 10 rps, 400/10 = 40 rps; 92,000 & 368,000 in/3,000 & 12,000 out tokens/s; $0.01164/req; 16.5M & 540K tokens/$.  — all consistent.
- The single-host "doesn't meet the workload" framing, the 164.1 vs 165 (9.2K vs 9.5K) distinction, and the measured-FP8-vs-byte-halving (1.42 vs 1.31) distinction are all preserved and correct.

The only numerical inconsistency tied to content is the **figure 7.3 1260-vs-1120 GB** value (P17-3).

---

## E. STORYLINE / STRUCTURAL FINDINGS

No new storyline/structural defect. The chapters remain correctly sequenced (unit → inference modes → model → workload → selection → metrics → memory → compute → communication → parallelism → serving → design → reference → benchmark), each deepens rather than restarts the causal chain, and no chapter needs to be split/merged/moved based on this pass.

One small sequencing/topical note tied to the figures: figure 4.1 (P17-4) is the only place the book's own six-dimension framework is visually present, and it is mislabeled relative to the framework, which is a structural/consistency risk for an otherwise very well-sequenced chapter.

---

## G. SOURCE / EVIDENCE FINDINGS

No new source/evidence issues. (The FP8 ~1.42 MB/tok [1P] vLLM value, the 989/3.35/4.8 TB/s vendor figures, and the [1P]/[2°]/[ILLUSTRATIVE][DERIVED] provenance labels continue to be applied correctly and consistently in ch1–14.)

---

## H. FINAL REMAINING-RISK ASSESSMENT

- **Strongest remaining risk:** publication-quality figure defects in the rendered PDF. The three serious ones are the clipped figure 8.1 ladder labels (P17-1), the clipped figure 10.2 labels including the erroneous "experts 6-1" (P17-2), and the figure 7.3 ~1260-vs-1120 GB fine-tune value (P17-3). All three are invisible in source .md/text-only review and are exactly the class of defect a visual pass catches.
- **Why these slipped past 16 passes:** prior passes reported convergence to zero, but the loop was apparently reviewing source/markdown/extracted text; the clipping and the figure-vs-text numeric mismatch only appear in the raster/PDF render.
- **Which chapters/transitions deserve one more pass:** re-verify ch08, ch07, ch10, ch04 after the figure fixes; then a focused full-figure sweep of the whole built PDF (ch15–27) using the same render-then-inspect method, since the sibling pass (pass17_findings_15-27.md) may surface analogous figure defects in the back half of the book.
- **Which claims require verification:** nothing new beyond the P17-3 figure value; the FP8 measured value is already sourced.
- **Which figures still deserve redesign:** fig 8.1 (redesign box widths/font), fig 10.2 (widths), fig 7.3 (correct 1120 value + fix overlap), fig 4.1 (align to six-dimension framework), fig 6.1 (add arrows/legend).
- **Likely locus of subtle undiscovered problems:** the figures themselves, particularly any diagram whose text is set at the box width (or near the figure edge) and any figure that encodes a numeric quantity (bars/stacked segments) whose segments may not be drawn to the stated value. The rest of the ch1–14 prose/numerics appear converged.
