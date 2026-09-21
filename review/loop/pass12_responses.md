# PASS-12 FIXER — Responses (final convergence pass, 2 MINOR)

PASS-12 confirms effective convergence. ch01-14: **NO NEW FINDINGS** (0 CRITICAL/MAJOR/MODERATE/MINOR).
ch15-27: **2 MINOR** (1 grammar, 1 illustrative-scenario parameter coherence). Trend:
PASS-8=12 → PASS-9=11 → PASS-10=24 (deep) → PASS-11=8 → **PASS-12=2**. Both subagents
re-verified every prior PASS-1..11 fix is landed and correctly did NOT re-report them, and
re-verified the canonical arithmetic end-to-end.

- **P12-1 [MINOR] worksheet.tex "the own workload"** — Missing possessive. Corrected to
  "the architect's own workload" (kept no-reader-address per the voice rule). Now the
  worksheet's opening matches its purpose statement grammatically.
- **P12-2 [MINOR] Ch18 §8 mini-case load inconsistency** — Stated "1,000 users, 20% concurrent
  (200 simultaneous), ~5 rps / 20 rps peak" was incompatible with the stated 5,000 tokens/hour
  (5 rps would be ~4.5M tokens/hour, ~900× off). The mini-case's cost arithmetic is driven by the
  5,000 tokens/hour (per-token volume), not the rps. Re-framed the load to be coherent with the
  low volume: "~1,000 registered users at a modest, deliberately low volume — 5,000 tokens/hour
  (each request ~250 tokens → ~20 requests/hour), a light load chosen to make per-token routing
  economics concrete rather than to model a busy fleet; the traffic rate is not what drives this
  arithmetic, the per-token volume is." All downstream cost figures ($0.80/$1.13/$0.75, $2.68/hr,
  $1,930/mo, $8,870/mo savings, 82%) are unchanged because they recompute from the 5,000 tokens/hour.

## Confirmed converged (no action)

Both subagents independently verified: taxonomy harmonized across all 4 published statements
(Preface, sources.tex, worksheet.tex, book-architecture.md); [S#]-is-not-provenance note in
place; glossary covers RQO/FSDP/CP/κ/ρ; Ch16 TCO "beats API, loses to cloud"; Ch17 cross-host
bandwidth reconciled; Ch19 turn distribution/α/β and full-vs-incremental service-time scope note;
Ch22 canonical-input labels `[canonical scenario][ASSUMPTION]` and "verdict" column; Ch24 PIES
768/217, host-floor 6.5/16.3, Table 24-1 cycles; Ch25 ADR 16-bit/FP8 reconciliation and 18→33
concurrency; Ch26 TTFT scoping and ~2 req/s ceiling; Ch27 Appendix A active fractions — all
recompute correctly. Voice hygiene (no reader-address, no "Think of X as Y", no `[INTERPRETATION]`)
clean everywhere; the few "you/your" hits are in-character dialogue (Ch23) or attacker/example
strings (Ch24), not reader-address.

## Status
2/2 addressed. This pass reached near-zero. Rebuild, then one final confirmation pass (PASS-13)
to lock in ZERO new comments and conclude the loop.
