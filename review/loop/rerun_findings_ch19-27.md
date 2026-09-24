# Re-Review (post-pass25-fix) — Ch 19–27 + Appendix A + back matter
**Built PDF:** `/home/ubuntu/from-token-to-fleet-v20260913-full.pdf` (307 pp), pages 213–307.
**Scope:** Ch19 (p213) → Ch20 (226) → Ch21 (235) → Ch22 (242) → Ch23 (251) → Ch24 (257) → Ch25 (268) → Ch26 (277) → Appendix A (286) + Glossary/References/Sources/Worksheet (297–307).
**Method:** every assigned figure raster-rendered at 200 dpi and visually inspected (PyMuPDF `get_pixmap`); caption + in-figure text read from both the text layer and the rendered raster; voice-iron-rule / taxonomy / canonical-number sweeps run programmatically across the whole slice; back-matter coherence cross-checked against the Preface and Sources taxonomy.

---

## 0. Verdict on the PASS-25 fixes (all landed — verified in the BUILT PDF raster)

The five pass-25 items targeted that fall in this slice were **confirmed FIXED on the rendered page**:
- **Fig 19.2 / 19.3 `O_final=300`** — FIXED. Caption 19.2 = "(I₀ + T·δ + T·γ + O_final; 9,200 input + 300 output + 800 + 65 per turn)"; Fig 19.2 (a) now carries a separate "output tokens" stack segment; Fig 19.3 caption = "initial prompt (9.5K = 9.2K input + 300 output)" and the in-figure footer = "total = I0 + T·δ + T·γ + O_final (base 9.5K = 9.2K input + 300 output)". KV labels 24.9→34.0 GB reconcile (9,500·2.62=24.89; 12,960·2.62=33.96).
- **Fig 20.1 scheduling overhead** — FIXED. Legend = "with scheduling overhead (~95%)"; caption = "~95% scheduling-overhead line".
- **Fig 26.2** — FIXED. DERIVED node = "sharding ⇒ **decode bandwidth-bound**" (full phrase, decode qualified).
- **Fig A.1** — FIXED. Orange % labels separated from grey total/active annotations; no overlap.
- **Fig 22.1** warning banner, **Fig A.4** axis framing — CONFIRMED present/correct: 22.1's red "LEFT: PER REQUEST | RIGHT: PER GENERATED TOKEN / DO NOT COMPARE Y-AXIS MAGNITUDES DIRECTLY" banner is prominent; A.4's red axis note = "vertical axis = WHERE it lives, not BETTER/HIGHER", eight layers correct.

Also verified clean: voice iron rule (zero reader-address "you/your", zero "Think of X as Y", zero "Consider/Note that" in the slice — the only "you/your" hits are quoted customer dialogue and quoted DAN/prompt-injection attack payloads, which are legitimate). Canonical values (2.62 MB/token, 9,200/9,500, 24.9/34.0 GB, 17.5, ~2.0 req/s, ~36% growth, 1.4e-4 PFLOP/token) all consistent. Ch19 §19.9 mini-case arithmetic recomputes correctly (10,350 → 10,650; α=1.12; μ=27.2 GB @10,365 tok). Evidence taxonomy is stated consistently (5-item provenance incl. `[canonical scenario]` × 5 statuses) across Preface (p16), Sources (p303–304), and Worksheet (p305); the `architecture.doc` does NOT ship the taxonomy, so there is no third conflicting version; `[INTERPRETATION]` is not used anywhere in the slice.

**The slice still has genuine remaining problems below. The loop is NOT converged.**

---

## Findings

### P1 | p232 | Ch20 §20.9 End-of-Chapter Mini-Case, "Fleet aggregate (8 hosts)" bullet
**Problem:** The prose provisioning result still says "the idealized minimum is ⌈40 / 2.0⌉ = 20 hosts; allowing ~10% scheduling loss raises this floor to 40 / (2.0 × 0.9) ≈ 22.2 → **23 hosts**." This uses a **0.90** efficiency factor. But the same chapter's Fig 20.1 (just fixed this pass) uses "~95%", and Ch17 §17.5.2 / the glossary (ρ) use ρ ≈ 0.95 / 0.98. The pass-25 fix updated only the FIGURE (and its caption) to ~95% and did **not** update this matching prose sentence.
**Why it matters:** A load-bearing provisioning answer (23 vs 22 hosts) is derived from a factor that contradicts the adjacent figure and the book's canonical ρ. With ρ=0.95 the floor is ⌈40/(2.0×0.95)⌉ = ⌈21.05⌉ = **22 hosts**. A reader reconciling the Ch20 prose, the Ch20 figure, and Ch17 gets three different efficiency values for the same fleet-sizing quantity.
**Recommended change:** Change the mini-case to use the same factor as the figure and Ch17: "allowing ~5% scheduling loss raises this floor to 40/(2.0×0.95) ≈ 21.1 → 22 hosts" (and reconcile any downstream count). Also note the glossary defines ρ as "fraction of theoretical peak a host actually sustains" — the prose mixes the terms "scheduling loss" / "scheduling overhead" / ρ for one quantity; pick one term and one value.

### P2 | p285 (+ p282) | Fig 26.2 caption vs. the capstone mini-case (p283–284) and the figure's own DERIVED node
**Problem:** Fig 26.2 is titled "Pattern Application Diagram … on the capstone scenario," and its caption concludes "The three patterns compose to ~680 ms p99 and ~40% lower generation cost versus the uncached, unsharded baseline." But the capstone mini-case (Step 2 "New TTFT p99: 210 ms"; Step 3 "TTFT p99 = 285 ms and cost per query down 55%") and the figure's own in-figure DERIVED node ("TTFT p99 210 ms", "cache 35% → engine load 2.0→1.3 rps") use **different numbers** (35% cache, 210/285 ms, 55% cost). The "~680 ms p99 / ~40% cost" pair is a leftover from the **Pattern-B illustration** in §26.x (40% cache assumption) — it is not the capstone scenario's value and is not derivable from the capstone's 320/80/50 ms legs (which sum to 450 ms baseline, 210 ms post-pattern).
**Why it matters:** The culminating capstone figure contradicts its own caption, its own body node, and the mini-case prose. 680 ms also cannot be an end-to-end p99 (the mini-case states the sub-second values are TTFT, not end-to-end) nor a TTFT p99 (which is 210 ms). This is exactly the kind of verifiable internal contradiction the standard says must not survive.
**Recommended change:** Reconcile Fig 26.2's caption to the capstone's own numbers (e.g. "…compose to a TTFT p99 of ~210 ms (−47% vs. 450 ms baseline) and ~55% lower cost per query"), or explicitly label the caption's "680 ms p99 / 40% cost" as the Pattern-B illustrative configuration (40% cache) distinct from the capstone scenario. Related micro-drift to fix while reconciling: cache hit ratio appears as 35% (mini-case Step 2 / Fig caption), 38% (Table 26-2 observed), and 40% (Pattern-B section); and GPU util appears as 45% (FACT) vs 68% (Table 26-2).

### P2 | p288 | Appendix A §A.2 "How to read this appendix: Observed, Interpretation, Hypothesis"
**Problem:** Appendix A introduces a **third** epistemic layering — Observed / Interpretation / Hypothesis — where "Interpretation" is defined as "our read of what architectural mechanism the report demonstrates … could be wrong." The book's canonical evidence taxonomy (Sources p303–304, Preface p16, Worksheet p305) is two axis with statuses FACT / DERIVED / ASSUMPTION / HYPOTHESIS / UNRESOLVED and **explicitly does not sanction "Interpretation"**. The appendix never maps its three layers onto the taxonomy's provenance×status labels, and "Interpretation" has no home in the two-axis scheme (it is neither a provenance item nor a sanctioned status).
**Why it matters:** The book's central methodological discipline IS the two-axis label; presenting a second, unmapped salary of "Observed/Interpretation/Hypothesis" in the appendix invites a reader to use two competing epistemic schemes and blurs where "our analysis" sits relative to the taxonomy (the appendix's own "interpretation" is roughly the taxonomy's [DERIVED] plus unsanctioned "interpretation"). This is exactly the "taxonomy stated consistently / not 2–3 conflicting versions" risk the standard targets.
**Recommended change:** Either map the three appendix layers onto the taxonomy explicitly in A.2 (Observed → [1P][FACT]; Interpretation → [DERIVED]/prose analysis (drop the word "interpretation"); Hypothesis → [HYPOTHESIS]) with a one-line note, or replace the "Interpretation" layer with the taxonomy's own term so the appendix reads as a reader-friendly on-ramp to, not a variant of, the two-axis framework. The appendix already cautions "read those as Interpretation / Hypothesis," but the mapping should be made explicit.

### P3 | p220–221 | Fig 19.2 vs Fig 19.3 — `I₀` (and `O_final`) decomposed differently in the two companion figures
**Problem:** Fig 19.2(a) decomposes the stack as **initial context (I₀) + added per turn (T·δ+T·γ) + output tokens**, i.e. I₀ = 9,200 (input only) and the 300-token `O_final` as a separate "output tokens" segment. Fig 19.3 decomposes the stack as **initial prompt (I₀) + retrieved tool output (δ) + generated reasoning (γ)** with *no* output segment, and its caption/footer tell the reader the "initial prompt" block = 9.5K (9,200 + 300). So the two companion figures use **I₀ = 9,200** and **I₀ = 9,500** for the same base quantity, and only Fig 19.2 shows `O_final` as a visible stack layer while Fig 19.3's footer formula ("total = I0 + T·δ + T·γ + O_final") treats it as separate.
**Why it matters:** Both figures are presented and cross-referenced together ("Companion Fig 19.2/19.3"); a reader mapping the bar segments to the formulas finds I₀ means two different things (9,200 vs 9,500) and `O_final` present in one decomposition but absent from the other's bars. The arithmetic is right but the notation is not harmonized.
**Recommended change:** Make both figures decompose identically. Either (a) give Fig 19.3 a separate "output (O_final)" segment and label its I₀ as 9,200 (matching Fig 19.2), or (b) relabel Fig 19.3's bottom block explicitly as "initial prompt (I₀, 9.5K = 9.2K input + 300 output)" and note that the footer's separate `O_final` term is the book's formula-level grouping, so the figure and formula align.

### P3 | p282 / p284 | Ch26 Pattern-B section names an efficiency lever as a "capability" reading (minor)
**Problem:** §26.x Pattern B ("Semantic Response Cache") is introduced as "ILLUSTRATIVE ASSUMPTION: 40% of queries repeat…". (Conflated with the P2 above; listed only for completeness.) Not a standalone defect beyond the number-set reconciliation in the P2 finding.

---

## Notes (verified non-defects, so they are not repeated as findings)
- Voice iron rule clean across the slice (only quoted dialogue / quoted attack payloads contain "you/your").
- No `[INTERPRETATION]` anywhere; taxonomy consistent across Preface / Sources / Worksheet (5-item provenance incl. `[canonical scenario]`); `architecture.html` ships no taxonomy, so no conflicting version exists.
- Ch19 §19.9 mini-case arithmetic, the `~36%` KV growth, `α=1.12`, `27.2 GB`, and the `C/W≈2.0 / 17.5 / 2.62 MB/token / 2.0 req/s` family all recompute consistently.
- Fig 20.1's "~29 hosts: 70% target (⌈40/(2.0×0.70)⌉=29)" checks out; the "2.0 req/s is an analytical bound, not measured throughput" and "NOT GPU util" qualifications are present and honest.
- Glossary is materially complete for load-bearing terms in this slice (TTFT/TPOT/ITL, goodput, κ, ρ, RPS/QPS treated as synonyms, pattern names defined in body). The only residuals are the value/terminology drift folded into Findings P1 and P3.

**Exit status:** NOT converged — P1 + 2×P2 + 1×P3 genuine findings remain. The Ch20 ρ (0.90 vs 0.95/0.98) reconciliation is the highest-value item because it changes a concrete provisioning number and directly contradicts the adjacent figure.
