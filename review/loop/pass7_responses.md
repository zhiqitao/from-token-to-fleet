# PASS-7 FIXER — Responses (22 new comments total, loop continues)

PASS-7 surfaced 22 new comments (ch01-14: 8; ch15-27+backmatter: 14). Full findings in
review/loop/pass7_findings_01-14.md and pass7_findings_15-27.md. All addressed below.

## HIGH
### [P7-A] Ch17 §4 cross-host per-request bandwidth 100× error. FIXED.
B_per-req = 5/(0.02×0.1×4) = 625 MB/s ≈ 5 Gbps (not 6.25 MB/s ≈ 50 Mbps); high case
  50/(0.02×0.5×4) = 1,250 MB/s ≈ 10 Gbps (not 12.5 MB/s/100 Mbps). Re-framed: base case is now
  ~half the 10 Gbps link (~2× headroom, not order-of-magnitude margin); high case at the link
  limit. Also fixed §6 B_min ≈ 0.5 Gbps → 0.8 Gbps (0.1×4×5MB/0.02s = 100 MB/s).

## MODERATE
### [P7-B] Ch17 Table 17-1 scope note "4-turn" → T=3. FIXED.
The agentic W≈13.8s is derived at T=3 (the 95th-pct), so the note now says "T=3 (95th-pct)".

### [P7-C] Ch18 §3.2 vs §8 cost-unit mismatch. FIXED (scope note).
§3.2 uses per-1M ($2.50/1M); §8 mini-case uses illustrative per-token rates internally
  consistent with its own arithmetic but on a different basis. Added an explicit scope note
  distinguishing the two bases so they aren't read as contradictory.

### [P7-D] Ch23 five-vs-six-bounds inconsistency. FIXED.
Standardized on SIX (matching Table 23-1, §6, mini-case): split item 4 (latency/cost) into
  latency/SLO and cost ceiling; changed all "five numbers/bounds" → "six". Zero "five" remain.

### [P7-E] Ch12 Candidate (c) quality contradiction. FIXED.
§3 is careful ("not derivable from parameter count"); the mini-case/Table asserted "cannot reach
  required answer quality" and "fails quality ceiling" flatly. Softened both to "provisional —
  subject to the Ch13-14 quality-gate measurement."

## LOW
### [P7-F] Ch8 Table 8-1 stray "| metric | value | derivation |" in caption. FIXED.
### [P7-G] Ch8 §3 spurious "14.8T-token pre-train budget". FIXED (trimmed to pure 2·N·L).
### [P7-H] Ch9 §2 InfiniBand 2.8s/18× → 5.6s/~35×. FIXED (140/25=5.6s).
### [P7-I] Ch9 §5 "25 Gb/s ~56s" → stated ≈2.5 GB/s effective. FIXED.
### [P7-J] Ch9 Fig 9.1 caption "≈70 GB in BF16" → 140 GB. FIXED.
### [P7-K] Ch7 Table 7-1 KV-row derivation mislabeled. FIXED (→ 9,500 × 2,621,440 B).
### [P7-L] Ch6 §3 p99 vs p95 SLO. FIXED (framed against canonical p95 ≤ 2s, noting p99).
### [P7-M] Ch17/Ch19 W prefill-basis note. FIXED (1.08s prefill held at canonical; 12,095-token
  would scale to ~1.42s; tool term reconciled with Ch19's T·L_agent).
### [P7-N] Ch24 mini-case tool-use 0.32% → 0.44% (at PIES=143/cycle-2). FIXED.
### [P7-O] Ch15 §5 FP8 2.5→1.3 vs §6 2.62→1.42. FIXED (standardized to 2.62→1.42 [S6]).
### [P7-P] Ch16 managed-API $539K → $541K (26M × 0.0208 = 540.8K). FIXED.
### [P7-Q] Ch18 730→720 hr month. FIXED.
### [P7-R] Ch18 §3.5 "saving ~$8/hr" → ~$11.16/hr ($23.75−$12.59). FIXED.
### [P7-S] Ch18 "per hour" token-volume label → "per request". FIXED.
### [P7-T] Ch18 §4 cost target $0.002/token → per-1M basis. FIXED.
### [P7-U] Ch26 table order (26-2 before 26-1) + cross-refs (Ch21→Ch10, Ch26→Ch3). FIXED.
### [P7-V] Ch20 cold-start 30-120s vs Ch15 ~2s. FIXED (scoped as full-weight load vs KV warm-up).

## Cosmetic (no action)
- Ch26 Fig 26.1/26.2 internal filename numbers (2602/2601) reversed relative to on-page
  numbers — cosmetic-only (figures render correctly); same class as Ch10 (closed in PASS-1).
