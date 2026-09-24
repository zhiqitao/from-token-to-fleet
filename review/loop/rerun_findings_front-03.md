# RE-REVIEW FINDINGS — FRONT MATTER + PREFACE + PART I (Ch 1–3)
Built PDF: `/home/ubuntu/from-token-to-fleet-v20260913-full.pdf` (307 pp)
Range inspected: pages 1–60 (cover, copyright, TOC, List of Figures, Preface pp. vi–xi,
Part I divider p19, Ch 1 pp.20–27, Ch 2 pp.28–40, Ch 3 pp.41–52, Part II divider p53, and
the Ch 4 canonical table on pp.57–60 which Part I cites).
Method: full text read of every page + raster inspection (150–300 dpi) of every figure page
(14, 15, 23, 24, 31, 35, 50) + objective on-page font-span measurement + whole-book
canonical-number drift sweep + voice-hygiene regex scan + cross-reference/markdown-leak scan.

Overall: this front-matter + Part I block is in strong shape — clean voice hygiene
(only one reader-address in the whole range), consistent canonical arithmetic (2NL prefill
floor, 5.6 TB/s decode demand, 989 TFLOPS dense, ridge ~295, 24.1/24.9 GB KV all check out),
correct evidence-tagging, and figures 1.1, 1.2, 2.1 are clean in the raster. Findings below are
the genuine remaining issues; there are no CRITICAL findings in this block.

---

## A. FIGURE / VISUAL FINDINGS

### F1. MODERATE | p15 (Preface, Figure 2 "Reading the book two ways") | Arrow direction contradicts stated order; bottom boxes unconnected
- Problem: In both columns (A · LAYER-BY-LAYER and B · QUESTION-BY-QUESTION) the vertical arrow chains point UPWARD, while the headings state "Parts I → VI" and the caption describes the trace "token → cost → KV → which phase binds → one host or a fleet" — a top-to-bottom ordering. With the boxes stacked I (top) → VI (bottom), upward arrows read the flow bottom-to-top (VI→I; "is it the right call?" → "token → cost"), the reverse of the stated progression. Additionally, in both columns the arrow shaft terminates above the second-from-bottom box (V · The Fleet / "who serves it?") and never reaches the bottom box (VI · The Architect / "is it the right call?"), so the bottom (and naturally first, given "build the substrate" then "the discipline") nodes are visually cut off from the chain.
- Why it matters: This is the book's own navigation figure read by every first-time reader. Conflicting arrow direction vs. stated reading order, plus a disconnected terminal node, makes the "read two ways" guide self-contradictory and forces the reader to decode the layout before using it (violates §23/§24 figure-causality standard).
- Recommended change: Either (a) reverse the box order so Part I/“token → cost” sits at the bottom and VI/“is it the right call?” at top (so the up-arrows correctly point the reader from substrate toward discipline / question toward the chapter that answers it and the chain reaches the start node), or (b) flip the arrowheads to point DOWN. In both cases extend each chain to the full six nodes so no box is disconnected.

### F2. MODERATE | p50 (Ch 3, Figure 3.1 "Dense vs MoE parameter allocation and KV cache behavior") | Banner caption text clipped in the raster
- Problem: The red banner strip at the bottom of EACH column carries white text that in the rendered raster is clipped to the fragment "e (matched atte" — the intended caption ("KV same as dense (matched attention geometry)") runs off both edges of the banner and is unreadable. Verified at 300 dpi in both the Dense 70B and MoE columns. The PDF text layer retains the full string (so a text-layer-only reviewer would report this as fine), but the raster clips it — the exact pass-18 trap.
- Why it matters: This is the only explicitly-drawn statement in the figure that "KV behaves the same for dense and MoE (matched attention geometry)". Losing it weakens the takeaway the figure exists to teach, and clipped text is a publication-quality defect (§49).
- Recommended change: Narrow the banner text (e.g. "KV same as dense (matched attention)" on one line) and widen the banner so the string fully fits; re-render and re-verify the raster shows the whole string.

### F3. MINOR | p24 (Ch 1, Figure 1.2 "How a token travels") | Smallest node third-line labels sit right at the 7.5 pt floor
- Problem: The third-line labels inside the six pipeline nodes ("characters", "corpus-driven", "one vec/token", "ordered", "vs past", "per layer x head") measure 7.60 pt on-page — only 0.10 pt above the 7.5 pt minimum.
- Why it matters: The labels are the figure's distinguishing detail (what each stage produces). At the floor they are the first to become marginal if the figure is downscaled, reprinted, or viewed on a smaller trim; it also reads uncomfortably small against the ~10 pt box titles.
- Recommended change: Bump the node third-line font (or drop one third-line word) so it sits at ≥8 pt comfortably above the floor.

### F4. MINOR | p35 (Ch 2, Figure 2.2 roofline) | Red dashed ridge line passes through the top explanatory copy
- Problem: The vertical red dashed roofline extends up through the centred explanatory block "operating points are NOT fixed: … all move a point across the ridge", intersecting the words "kernel/hardware" and "the ridge" and partially obscuring a few characters. (The "roofline / ridge ~295" label itself and the two operating-point annotations are readable and NOT clipped — do not chase those.)
- Why it matters: Minor but genuine visual overlap on a figure meant to be instantly legible (§23).
- Recommended change: Clip the dashed ridge line to the height of the shaded two-tone block (do not extend it into the annotation text), or pad the annotation block above it.

---

## B. TERMINOLOGY / NUMERIC-CONSISTENCY FINDINGS

### F5. MODERATE | p22 (Ch 1 §1.2.5), p44/p50 (Ch 3 §3.4.3, §3.9, Table 3-1) | "8-bit KV ≈ 1.3 MB/token → ~12 GB @ 9.2K" uses the naive-halving value without the nominal-vs-measured caveat
- Problem: Ch 1 and Ch 3 quote the 8-bit KV as "~1.3 MB per token" and "~12 GB" for the 9.2K context. That is the theoretical byte-halving figure (2×80×8192×1 B = 1,310,720 B ≈ 1.31 MB). The book's own operating FP8 constant — established in Ch 7 and used consistently in Chs. 17–20 and Appendix A — is the *measured* ~1.42 MB/token (= 54% of BF16, not a naive 50%), i.e. ~13.1 GB at 9.2K. Nowhere in Ch 1/Ch 3 is the reader told that "8-bit" here means nominal halving and that the measured serving footprint is ~1.42 MB/token.
- Why it matters: The book is elsewhere extremely rigorous about this exact distinction (Ch 7 §7.x and the Sources chapter explicitly warn "the 1.31 vs 1.42 MB/token distinction is nominal-halving vs measured"). A reader who commits the Ch 1/Ch 3 figure of ~1.3 MB/token and ~12 GB will under-provision the KV budget by ~9% when the practical FP8 value is used. It is an internal-consistency gap (§5, §45), the kind a numeric pass otherwise surfaces late.
- Recommended change: Add a one-line note in Ch 1 §KV-cache and Ch 3 (e.g. "8-bit here = naive byte-halving (≈1.31 MB/token); the measured FP8 serving constant is ≈1.42 MB/token (54% of BF16 → ≈13 GB at 9.2K) — see Ch 7"), so Ch 1/Ch 3 carry the same caveat Ch 7 exercises.

---

## C. VOICE-HYGIENE FINDING

### F6. MINOR | p36 (Ch 2 §2.4, "Worked example arithmetic details") | Reader-address "you" violates the voice iron rule
- Problem: "…it is the footprint you get from reading every parameter once per decode step…"
- Why it matters: The voice-hygiene iron rule is zero reader-address ("you/your"). This is the only occurrence in the entire pp.1–60 range (verified by whole-book regex), so it is an isolated slip rather than systemic.
- Recommended change: Reword to "…it is the footprint obtained by reading every parameter once per decode step…" (or "the footprint from reading…").

---

## D. CROSS-REFERENCE FINDING

### F7. MINOR | p49 (Ch 3 §3.9 mini-case) | Cross-reference "(Ch. 3 §6, Ch. 18)" is wrong — expert offload/swapping is not in §6
- Problem: "…unless we explicitly use expert offload/swapping (Ch. 3 §6, Ch. 18)". Ch 3 §6 is "Common Mistakes"; the expert-offload discussion lives in §3.7 ("the option to offload inactives at the cost of bandwidth") and §3.7.1 (offloadable N-gram). The §6 pointer points at the wrong section.
- Why it matters: Cross-references are the book's navigation system (§29); a reader sent to §6 for offloading will not find it.
- Recommended change: Change to "(Ch. 3 §3.7, Ch. 18)".

---

## E. TABLE / ARITHMETIC-FRAMING FINDING

### F8. MINOR | p43 (Ch 3 §3.4.2, Table 3.2) | Derived active-parameter derivation line is internally inconsistent
- Problem: The "Active parameters per token (top-2 routing) ≈ 14B" row's derivation reads "Top-2 from 8 experts ≈ 2/8 = 25% of expert mass". 25% of the ~48 B expert mass is ~12 B, not 14 B. The reported ~14 B (≈30% of total) is only consistent because the active count also includes the never-routed attention/shared weights, not just the two routed FFN experts.
- Why it matters: A reader recomputing 25% × 8×6B will not recover 14 B and will conclude the table is arithmetically loose; the two percentage framings (25% of expert mass vs ~30% of total) are used interchangeably nearby (§26, §45).
- Recommended change: Reword the derivation to "2 routed FFN experts + always-on attention/shared weights ≈ 14 B (≈30% of the ~47 B total; ~25% if counting expert-FFN mass alone)", so the 25%-vs-30% ambiguity is resolved explicitly.

---

## F. FINAL REMAINING-RISK NOTE (for the parent)
- This block has NO CRITICAL and NO MAJOR findings; the three MODERATE items (F1 direction/disconnection, F2 clipped banner, F5 8-bit-vs-measured-FP8) are the ones worth fixing before this range is considered converged.
- The eight-bit vs measured-FP8 KV distinction (F5) is the highest-value consistency item because the same 1.42 MB/token fixed point recurs across Chs. 17–20; confirm Ch 7's own wording is aligned so Ch 1/Ch 3, Ch 7, and Sources all agree.
- Nothing in Part I forces another full-page sweep; a targeted re-check of p15, p35, p50 (figures) plus the three one-line text edits (F5/F6/F7) should close this block.
