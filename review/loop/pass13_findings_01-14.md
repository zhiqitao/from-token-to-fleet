# PASS-13 — FINAL CONVERGENCE REVIEW, ch01-14 ('From Token to Fleet')

**Verdict: 4 NEW findings — the loop is NOT yet at zero.**

Scope: final convergence pass over `design/manuscript/chapter-01..14` (source for the 308-pp
`from-token-to-fleet-v20260913-full.pdf`). Full careful read of all 14 chapters against the book's
own rules (two-axis evidence taxonomy: provenance `[1P]/[canonical scenario]/[2°]/[LAB]/[ILLUSTRATIVE]`
× status `[FACT]/[DERIVED]/[ASSUMPTION]/[HYPOTHESIS]/[UNRESOLVED]`, no `[INTERPRETATION]`; investigative
narration; 谦逊语气: zero reader-address, zero "Think of X as Y"; fixed canonical set
canonical-workload.yaml / Ch 4 Table 4-3). Every candidate was re-verified against source and
against PASS-1..12 before being reported. All figures referenced in ch01-14 resolve to files on disk
(script check: zero missing).

PASS-12's "ZERO new findings" verdict is **not upheld**: four genuinely NEW, previously-uncaught items
exist. All are MINOR; none is a number error. The most important is #1, because it contradicts a fix
PASS-11/PASS-12 both claimed was resolved.

---

## MINOR

### [P13-1] Dangling cross-reference: ch08 cites a "175B → 0.35 TFLOP/token" Ch 3 scaling that does not exist in Ch 3
**Location:** `chapter-08/chapter-08.md:41` — "[DERIVED: 2 FLOPs/parameter × 70 ×10⁹ params; standard
dense-forward arithmetic, consistent with the dense-forward scaling of Ch 3: 175B → 2 × 175 × 10⁹ ≈ 0.35
TFLOP/token]" — and `chapter-08/chapter-08.md:69` — "…consistent with Ch 3 dense-forward scaling: 175B
≈ 0.35 TFLOP/token".
**Problem:** This is the PASS-11-1 replacement for the undefined "E5" key. But the pointer is itself
**unresolvable**: a repo-wide grep of `design/manuscript/` finds "175" only in ch08; the string "0.35
TFLOP/token" and "dense-forward" appear nowhere in `chapter-03.md`. Ch 3's dense-forward scaling example
is 70B → ~0.14T (Table 3-1 line 38), not 175B → 0.35T. So the "E5" dangling key was replaced with a
**dangling pointer to a Ch-3 claim that does not exist**. PASS-12 asserted this pointer was "a resolvable
pointer to the same 2×N formula (verified 2×175e9 = 0.35e15)" — the arithmetic checks out, but the
*attribution* to Ch 3 was never verified and is wrong. A reader reconciling the reference finds no such
Ch-3 statement; the book's core auditable-evidence discipline is again undercut (the exact defect class
PASS-11-1 flagged).
**Why it matters (MINOR):** Same severity as the P11-1 it replaced — a dangling provenance pointer that
changes no number but breaks verifiability. Since it was introduced by a prior "fix" that claimed to
resolve the dangling-key problem, it should not be left.
**Recommended change:** Either (a) drop the "Ch 3" attribution and state it as the book's own 2×N
example ("e.g. a 175B dense model would be 2 × 175 × 10⁹ ≈ 0.35 TFLOP/token"), or (b) add the 175B →
0.35T example to Ch 3's dense-scaling discussion so the pointer is real. Do not leave a reference to a
non-existent Ch-3 line.

### [P13-2] ch05 §8 mini-case self-references "Chapter 5" from inside Chapter 5 (copy artifact) and retains "token-layer" phrasing
**Location:** `chapter-05/chapter-05.md:159` — "From the token-layer perspective (as we worked through in
Chapter 5), the architect can immediately check the consequences".
**Problem:** Two defects in one sentence. (a) It says "as we worked through in Chapter 5" *inside
Chapter 5* — a self-reference. The token-unit work it refers to was Ch 1, and the model-selection work is
this chapter's own; the parenthetical is a copy artifact from the Ch 1 mini-case boilerplate. (b) The
lead phrase "From the token-layer perspective" is the exact "token-layer" abstraction wording that
P10-7 / PASS-11 claimed was purged from non-Ch1 chapters (the considered-and-excluded section of PASS-11
explicitly stated ch05:159 was rewritten to "the unit-and-token work of Ch 1"; it was not — the line
still reads "token-layer perspective", and the other instances ch02:160, ch04:225 *were* rewritten, so
ch05 was missed).
**Why it matters (MINOR):** Same recurring copy-artifact class as P10-7; a running mini-case should point
forward/back at the chapter that actually did the work (Ch 1), not at itself, and should not resurrect
the "token-layer" abstraction after it was deliberately removed.
**Recommended change:** Rewrite to match the corrected pattern, e.g. "From the unit-and-token work of Ch
1 alone (Ch 5's selection surfaces), the architect can immediately check the consequences" or simply "From
the token-unit work of Ch 1, the architect can immediately check the consequences" — removing both the
self-reference and the "token-layer" wording.

### [P13-3] ch07 §8 mini-case: "(which we worked through in this chapter)" is a wrong-chapter copy artifact
**Location:** `chapter-07/chapter-07.md:171` — "From the unit-and-token work of Ch 1 alone (which we worked
through in this chapter), the architect can already establish several facts."
**Problem:** The parenthetical "which we worked through in this chapter" is a copy artifact from the ch01
mini-case (ch01:123, where it was correct). In ch07 the token-unit work was done in **Ch 1**, not in this
chapter (Ch 7 is memory); the phrase mis-states where the work occurred. The analogous lines in ch02:160
and ch04:225 correctly dropped the parenthetical; ch07:171 retained it.
**Why it matters (MINOR):** Same copy-artifact class; a reader sees "worked through in this chapter" for
work that was done in an earlier chapter, undermining the cross-chapter spine the book threads carefully.
**Recommended change:** Delete the parenthetical (matching ch02:160 / ch04:225) or correct it to
"(Ch 1)".

### [P13-4] ch01 §8 mini-case opens a paragraph with a sentence-initial lowercase "from"
**Location:** `chapter-01/chapter-01.md:123` — "from the token-level work alone (which we worked through
in this chapter), the architect can already establish: …" (begins a new paragraph after the period ending
line 121 and the blank line 122).
**Problem:** The paragraph begins with a lowercase "from" — a sentence-initial capitalization error left
from the mini-case boilerplate edit (the lead phrase was not capitalized when added). Reads as a
run-on/fragment rather than an opening sentence.
**Why it matters (MINOR):** Plain typographic defect; starting a paragraph with lowercase after a full
stop is an editing miss that survives in the printed render.
**Recommended change:** Capitalize to "From the token-level work alone …" (and, if desired, fold P13-3's
recommendation into the same line).

---

## Considered and excluded (verified not-new / not-a-defect)

- **ch08:41/69 "175B" — excluded?** No. Reported as P13-1 (see above); the Ch-3 attribution does not
  resolve.
- **ch07:143 "total-vs-active and MoE-vs-dense facts of Ch 3"** — *not* a defect: Ch 3 genuinely teaches
  total-vs-active and compute-sparsity vs memory-sparsity. Excluded.
- **ch05:159's "token-layer" in isolation** — the primary defect is the self-reference (P13-2), reported;
  the wording is called out within it.
- **All numeric cross-checks re-verified and consistent** (sample): KV 2.62 MB/token (2,621,440 B), 24.1 GB
  @9.2K / 24.9 GB @9.5K residency, 164.1/165 GB floor, ~140 GFLOP/token, 1.29 PFLOP prefill, ~12.9 PFLOP/s,
  5.6 TB/s decode vs 3.35, ~19,800 tok/s/host (8 × 2,471), C ≈ 18, 344 in flight, ~5 avg / ~19-20 peak hosts,
  Ch 9 communication (0.16/0.27 s, 6.1/98 s, 22×/350×), Ch 10 (140 GB ≥2×H100, 280 GB → 11 s/0.31 s, 32/11 ≈
  2.9×, 128/35 ≈ 3.66×), ch12 ~28K prefix-cache ([HYPOTHESIS]) and 164 GB residency, ch14 ~2.1 req/s at C≈18.
  No drift from the canonical set.
- **Bracket taxonomy** — no `[INTERPRETATION]`, no orphan status-only/provenance-only brackets beyond the
  permitted single-axis house variation; `[ASSUMPTION]`/`[UNRESOLVED]` statuses carry valid provenance.
- **Voice** — no reader-address "you/your", no "Think of X as Y", no `[INTERPRETATION]`; 谦逊语气 held.

---

*Conclusion: ch01-14 are close to convergence, but **not at zero**. PASS-12's "ZERO new findings" was
premature: P13-1 (the ch08 → "Ch 3" 175B pointer) shows a prior fix did not actually land and its claimed
resolution was never verified, and P13-2/3/4 are copy-artifacts in the shared mini-case boilerplate
(ch01/05/07). All four are one-line editorial edits with no numerical impact. Recommend a short fixer pass
addressing P13-1..4, then re-confirm zero before exiting the loop.*
