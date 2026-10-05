# PUBLICATION AUDIT — *From Token to Fleet: An AI Solution Architect's Handbook*

---

## 1. OVERALL ASSESSMENT

**What is genuinely strong.** This is not a manuscript that needs to be rescued; it is a manuscript that has been through several disciplined revision cycles and has arrived at a high technical standard in specific, identifiable places. Four contributions are, on their own, worth the book's existence:

1. **The kernel-regime vs. workload-capacity-deficit distinction** (Ch. 15 §3) — the cleanest articulation of the single most-confused concept in inference serving that I have seen in print. It is precise, it is stated where it matters, and it is *not* diluted anywhere. This should be promoted into Ch. 2 or the Preface, because the book's most common error (conflating a roofline classification with a capacity shortfall) originates in Ch. 2's own Architect's Question and recurs in Ch. 11, Fig. 11.3, and Table 6-1.
2. **The three-way bound taxonomy** (Ch. 8 §1): compute-bound / memory-bandwidth-bound / memory-capacity-constrained. Exactly right, correctly named, correctly applied to "input-heavy ≠ memory-bound."
3. **The 2NL-with-quadratic-correction accounting** (Ch. 8 §3, verified below): +17% at 9.2K, +60% at 32K, 2.4× at 128K. I recomputed all three from `4·n_layers·L²·d`. All three are correct to the stated precision. This is rare.
4. **The service-time-aware Little's Law discipline** (Ch. 17): λ·W with W ≈ 8.6 s (not TTFT) → 344 in flight, not 40; plus the identity λW/C ≡ λ/(C/W); plus the two genuine counter-scenarios (A and B) in which the *conclusion* changes while the *method* transfers. This is the model the rest of the book should be forced to follow.

Also excellent, and verified: the evidence taxonomy itself (Preface p. ix) — "arithmetic belongs on the epistemic-status axis, not the provenance axis" is a correct and cleanly stated principle, and it is honored in most of the book.

**What is weak.** Three structural problems and one class of numerical problem dominate.

- **Duplication at scale.** Ch. 22 (§4, §5, §8) is very largely Ch. 1 and Ch. 2 re-set. The four Common Mistakes in Ch. 22 §5 are near-verbatim from Ch. 1 §5, including the parenthetical. The §8 mini-case is near-verbatim from Ch. 2 §8. Ch. 20 §3 re-derives Ch. 17's C/W = 2.0 req/s and its "don't divide 35,000 by 9,500" warning. Ch. 4 carries the same canonical numbers in three separate tables plus a boxed panel. Ch. 17 and Ch. 20 are substantially one chapter wearing two.
- **A unit/denominator error with a 1000× magnitude in Ch. 18**, plus a **10× contradiction about owned-fleet cost per request between Ch. 4 and Ch. 16**. These are P0.
- **Rendered-figure defects.** I found visible text-over-text and text-over-line collisions on pp. 94, 99, 146, 160, 207, 233, 268; a title/legend overprint on p. 207; an axis that contradicts its own label on p. 268; a caption that contradicts its own plot on p. 174; a curve labeled MEASURED that the caption says was never measured on p. 221; a title/content contradiction on p. 197; a "sequential cascade" label on a figure whose caption says one model is selected, on p. 197; and a figure whose internal legend contradicts its own in-bar labels on p. 207. Under the standard set for this audit, the book is not publication-ready.

**The deep structural problem.** The book has one great idea — *architecture as causal reasoning from token to fleet* — and it is stated clearly in Ch. 2, restated in the Preface, restated in Ch. 12, restated in Ch. 21 §9, and restated in Ch. 22 §6. Four statements of the thesis, none of which is the first thing the reader meets. Meanwhile the synthesis chapter that is *supposed* to be the payoff (Ch. 22) opens with two pages of recycled Chapter 1. The argument is present; the sequencing is not.

---

## 2. HIGHEST-PRIORITY TECHNICAL / CONCEPTUAL ISSUES

### P0-A. Ch. 18 Table 18-2: the price column header contradicts the arithmetic by 1000×

The column is headed **"Token cost (USD / 1M)"** with values $2.50 / $1.25 / $1.00 / $0.15. The §3.3 arithmetic then multiplies **millions of tokens** by those numbers:

> 6.65M tokens × $1.25 = **$8.31 / hr**

For that product to be correct, $1.25 must be a price **per 1,000 tokens**, not per 1M. Under the header as printed, the correct figure is $16.63/hr, and every downstream number in §3.3 shifts by 1000×.

The chapter then compounds it: the *Basis note* explicitly reconciles the table's "$2.50" against Ch. 16's "~$0.60/1M" as a "utilization/throughput basis difference… ≈4× gap