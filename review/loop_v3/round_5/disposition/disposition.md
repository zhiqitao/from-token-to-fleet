# Round 5 disposition ledger

823 findings (21 common + 802 unique; text 450 + vision 373) dispositioned 1:1
across 42 batches (23 text + 19 vision), gate: 0 problems (ids match, enum valid,
fix_instruction iff CONFIRMED).

| verdict | count |
|---|---|
| CONFIRMED | 341 |
| FALSE_POSITIVE | 242 |
| DEFENSIBLE | 239 |
| UNVERIFIABLE | 1 |

Dedup by id: 341 -> 292 unique fixes (235 text + 57 vision).
Severity: P1 37, P2 133, P3 122 (P0 0 after disposition).
FP rate: text 43/493? — see per-source below.
73 ABSENT-triage text quotes: 57 real paraphrases (CONFIRMED), 10 fabricated (FP), 6 defensible.
Vision FP rate: 195/… (leads-only calibration held; all P0/P1 vision leads this round
were disproven by text-layer/pixel checks except where noted CONFIRMED P2/P3).

## Fix packs (13, disjoint targets, <=24 fixes each)

- pack 00: 20 fixes — ch15(20)
- pack 01: 24 fixes — ch08(19), ch09(5)
- pack 02: 24 fixes — ch11(19), ch14(5)
- pack 03: 24 fixes — ch17(18), ch13(6)
- pack 04: 24 fixes — ch10(17), ch02(7)
- pack 05: 24 fixes — ch20(15), ch05(9)
- pack 06: 24 fixes — ch16(14), ch12(10)
- pack 07: 24 fixes — ch19(13), ch03(11)
- pack 08: 24 fixes — ch26(13), ch04(11)
- pack 09: 23 fixes — ch24(12), ch18(11)
- pack 10: 24 fixes — ch25(10), ch06(9), ch22(5)
- pack 11: 22 fixes — ch01(8), ch07(7), ch27(7)
- pack 12: 11 fixes — ch21(6), ch23(5)

## Convergence

292 CONFIRMED actionable > 0 -> NOT converged; round 6 required (cap R=14).
