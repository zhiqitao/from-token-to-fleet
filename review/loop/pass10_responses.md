# PASS-10 FIXER — Responses (deep-scale convergence pass)

PASS-10 was a NEW scale: rather than the numeric/cross-ref class that PASS-1..9 converged on,
it ran the DEEPER scales of the 55-section prompt (cross-chapter coherence, claim-strength,
terminology drift, duplication, whole-book architecture, glossary completeness). It surfaced
**24 deep findings** (ch01-14: 12 [4 MAJOR, 4 MODERATE, 4 MINOR]; ch15-27: 7 [2 MAJOR, 5 MODERATE]
— plus the file notes 7 genuine findings). Findings in pass10_findings_01-14.md /
pass10_findings_15-27.md. **Independent voice audit also fixed 14 "Think of X as Y" constructions**
(谦逊语气铁律 violation) caught by my own claim-strength sweep. All 24 + 14 addressed.

## 谦逊语气 / voice (my independent audit)

- **14 × "Think of X as Y"** (Ch1,3,4,5,6,7,9,10,12,13,14,18,21,23) — every one re-cast to
  declarative form (e.g. "A token is best understood as...", "Each tier is a box...",
  "The AI Factory is best read as..."). Verified 0 remaining in built PDF.
- Reader-address sweep: "we"=360 / reader-"you"≈0; the 7 "your"/1"you need" are legitimate
  (dialogue quotes, injection-attack strings, "Attention Is All You Need" title).

## ch01-14

- **P10-1 [MAJOR] Measurement duplication Ch1/4/5/6/7** — Kept the full tokenizer/token-count
  triple in Ch1 (where the unit is taught). Removed the verbatim recopy in Ch4 §4 and Ch5 §4,
  replacing each with a one-line cross-reference to Ch1 plus the chapter's *own* addition
  (Ch4: quantify-the-six-dimensions; Ch5: selection-surfaces). Ch6 §4 is genuinely chapter-specific
  (instrument the hierarchy / qualify throughput) so kept. Ch7 §4: items are chapter-specific but
  trimmed the verbatim "token-layer answer" closing echo from item 3.
- **P10-2 [MAJOR] taxonomy mismatch book-architecture.md §5/§14** — §5 rewrote to the binding
  axes (provenance [1P]/[canonical scenario]/[2°]/[LAB]/[ILLUSTRATIVE] × status
  [FACT]/[DERIVED]/[ASSUMPTION]/[HYPOTHESIS]/[UNRESOLVED]); retired [VERIFY]/MEASURED in the
  architecture doc; §14 rewrote from "five categories" to the correct two-axis form.
- **P10-3 [MAJOR] book-architecture.md §14 stale canonical numbers** — 23.8 GB→**24.9 GB** @9.5K
  (24.1 GB @9.2K), 1.3 MB→**1.42 MB/token** (vLLM-measured 54%), added C≈18 (~2.1 req/s) and the
  naive-byte-halving 1.31 lower-bound distinction. Aligned to canonical-workload.yaml.
- **P10-4 [MAJOR] economics budget unreconciled** — The canonical "~$15,000 monthly budget" and
  Ch12's "economic ceiling $15,000" are *per-host* caps (one 8×H100 ≈ $14.6K/mo × 730 hr), not the
  workload cost. Relabeled in Ch4 canonical box and Ch12 §8 as a **per-host** ceiling, with an
  explicit note that the full canonical workload (~5–20 hosts) is ~$75K–$350K/mo (Ch 16).
- **P10-6 [MODERATE] Ch9 vs Ch10 gradient 140 GB vs 280 GB** — Ch9's all-reduce example is an
  FP16 gradient (140 GB); Ch10's DP example is FP32 (280 GB). Added explicit gradient-dType
  statement to Ch9 cross-referencing Ch10, and the note that the sync time doubles accordingly.
- **P10-5 [MODERATE] Ch12 prefix-cache hypothesis presented as established** — The 30%/50%
  amortization and "~28K tok/s" are now labeled **[HYPOTHESIS]** (pending the §7 prefix-overlap
  measurement) in both §3 candidate (a) and Table 12-1.
- **P10-7 [MODERATE] RAG never expanded + "token layer" artifact** — RAG expanded at first body
  use (Ch4 §3, where the workload becomes named; Preface also defines it). "the token layer alone"
  replaced with concrete "the unit-and-token work of Ch 1" in Ch1/2/4/7. Ch4's "as we did in Ch. 4"
  self-reference fixed to point at Ch1.
- **P10-8 [MODERATE] KV/MoE-sparsity taught 3×** — Confirmed intentional rung-based teaching;
  added an explicit cross-reference in Ch3 §3 key-takeaway ("restates at the parameter level the
  sparsity lesson introduced conceptually in Ch 1 and developed arithmetically in Ch 7").
- **P10-9 [MINOR] Ch6 uses Ch8 roofline vocabulary before Ch8** — Added an in-line gloss
  ("the ratio of FLOPs to bytes moved") + explicit note that the roofline/ridge is developed in
  Ch 8, so Ch6 uses the concept without using undefined terms.
- **P10-11 [MINOR] Ch12 "baseline" candidate naming** — Candidate (a) now framed as the
  per-request-latency baseline, explicitly NOT a capacity baseline, with cross-ref to Ch11/13/17.
- **P10-12 [MINOR] Fig 7.1 "visual proof"** — Re-worded to "The figure illustrates the 8× reduction"
  (it is a derivation illustration, not a proof).

## ch15-27 + backmatter

- **P10-A [MAJOR] Preface taxonomy conflicts with Sources chapter** — Rewrote the Preface's
  "Architect's Evidence Discipline" to exactly match the binding sources.tex axes: provenance
  [1P]/[canonical scenario]/[2°]/[LAB]/[ILLUSTRATIVE] × status
  [FACT]/[DERIVED]/[ASSUMPTION]/[HYPOTHESIS]/[UNRESOLVED], with ILLUSTRATIVE on provenance and
  the [ILLUSTRATIVE][ASSUMPTION] composite shown. (Now all three — Preface, Sources chapter,
  book-architecture.md — agree.)
- **P10-B [MAJOR] Ch16 §6 "wins on TCO" contradicts §3/Table 16-1** — §6 now states self-host
  "beats the managed API at canonical volume but loses to scale-to-load cloud", and the surviving
  recommendation is *conditional* (sunk staff/ops term + sustained near-peak). Fixed the duplicated
  phrase in §3 too.
- **P10-M [MODERATE] Ch22 canonical inputs labeled "measured [1P]"** — Corrected to
  `[canonical scenario][ASSUMPTION]` in §3 Step 1 and Table 22-1 (the 9,200 ÷ 300 ratio now
  `[canonical scenario][DERIVED]`), consistent with sources.tex and the chapter's own adjacent
  [ILLUSTRATIVE][DERIVED] rows.
- **P10-N [MODERATE] Ch22 §2 duplicates Ch2's fire-hose/bucket metaphor** — Replaced Ch22 §2 with
  a declarative cross-reference to Ch2 §2 plus the chapter's real addition (the reasoning loop),
  removing the duplicated water/two-gears similes (which also violate the "X is like Y" convention).
- **P10-O [MODERATE] Ch22 stale "Chapter 23 (Memory)" ref** — Corrected to "Chapter 7 (Memory)".
- **P10-P [MODERATE] Ch20 §1 "marginal cost declines" claim** — Corrected to distinguish *average*
  (declines as fixed costs amortize) from *marginal* (roughly constant ~$9.5/req-s/hr; the Nth host
  is diminishing marginal *benefit*), matching §8 and Ch17 §7.
- **P10-Q [MODERATE] unused [canonical scenario] provenance bucket** — Now actually used (Ch22
  labels the canonical inputs [canonical scenario]), and the distinction from generic
  [ILLUSTRATIVE] is documented; the bucket is no longer advertised-but-never-invoked.
- **P10-R [MINOR] Ch21 "canonical canonical"** — Fixed (also fixed a typo I briefly introduced
  while repairing it).
- **P10-S [MINOR] Ch19 misstates Ch17 prefill scope** — Ch19 §4 parenthetical now matches Ch17:
  "1.08 s prefill held at the canonical 9.2K representative; the 12,095-token context would scale
  it to ~1.42 s".
- **P10-T [MINOR] Ch25 ~30 GB vs ~64 GB activation drift** — Added explicit reconciliation:
  the ~30 GB is a per-request working-set figure for the ADR's single-request arithmetic, distinct
  from the ~64 GB runtime/workspace/NCCL reserve used for the 640 GB envelope; both coexist.
- **P10-U [MINOR] glossary gaps** — Added **RQO**, **FSDP**, **CP** (Parallelism and flows) and
  **κ (kappa, per-token KV footprint)** and **ρ (rho, LB throughput fraction)** to the notation
  section.
- **P10-V [MINOR] [S#] keys used as provenance** — Added an explicit note in sources.tex that
  [S#] is a bibliography index, not a fifth provenance item; a composite label always carries a
  provenance alongside any [S#] key.

## Status
24 deep findings + 14 voice fixes = 38 items addressed. Rebuilding, then PASS-11. Convergence is
strong: PASS-8=12, PASS-9=11, PASS-10=24 (but at a NEW deeper scale, so the count jump reflects
covering the previously-uncovered whole-book/claim-strength/duplication dimensions, not regression).
