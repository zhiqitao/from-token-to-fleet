# Round 1 — Ornith-1.5-397B c1–c4 disposition (36 issues)

Model swap: 122B truncated even at 80K halves; 397B (im-eglb, effort=max)
took all four full chunks at depth 0. Output: text_Ornith-1.5-397B_c{1..4}.json
(c1=1, c2=1, c3=10, c4=24; severity 2×P0, 7×P1, 15×P2, 12×P3).

## FIXED (8 fixes, 12 edits, 6 files) — verified in rebuilt PDF

1. CH12-PD-POOL-RESIDENCY (P1, conf 0.90) — candidate (b) residency stated
   ~576 GB (§12.3) vs ~164 GB (summary, Table 12-1, §12.8). Fixed by carrying
   both figures with denominators in all three 164-spots: single-request fit
   164 (140+24); loaded 576 (140+436) at canonical per-host KV budget.
2. CH20-FEAS-01 (P0 as filed → verified percentages CORRECT; presentation
   fix). 93/109/101% all reproduce as demand÷ceiling; 2.7692 PFLOP/s is the
   Ch 8 35%-MFU host peak (defined ch8:171). The defect was basis-mixing:
   case (i) in tok/s, case (ii) in bare PFLOP expression. Fixed in ch17:145
   AND the twin sentence ch20:40: ratio now stated 18,400÷16,870 / ÷18,210
   with the PFLOP form as equivalent + constant defined + ">100% = prefill
   leg alone does not fit at 2 req/s" stated explicitly.
3. CH19-LEDGER-01 (P1) — ledger column "Post-call retained context" vs
   input-only `retained_history` (11,795) carried two denominators. Header
   renamed "(incl. own output)"; note added: 12,095 = 11,795 prefix + 300
   O_final at end-of-decode; peak KV 31.7 GB tied to the incl-output
   convention Ch 17 sizes T=3 with (436÷31.7≈13.8/host).
4. CH20-HOSTCOUNT-01 (P1) — ρ=0.95 applied to prefill screen by dividing
   host count, under-explained. One sentence added: ρ is a
   throughput-efficiency derate (dividing hosts ≡ dividing effective rate),
   applies to any throughput-bound screen, does not re-derive 35% MFU.
5. CH19-FALLBACK-01 (P1, arithmetic withdrawn by reviewer; optional
   accepted) — decomposition added: 39,395 = 30,195 (3 turns, no synthesis)
   + 9,200 (single-shot); 41,990−39,395 = 11,795−9,200 = 2,595.
6. CH25-ACTIVATION-01 (P2) — ~30 GB clarified as transient single-request
   prefill peak, reused across batch; 17×30 GB explicitly not implied.
7. CH20-COLDSTART-01 (P3) — mixed Gb/s premise + GB/s result. Conversion
   added: path ≈1.25–5 GB/s; result ≈37–9 Gb/s.
8. CH25-HOLD-01 (P3, optional accepted → became a real defect on verify) —
   ch4:94 formula "10 rps × 3,600 s × 8 h × 260 workdays = 6,240,000" was
   missing ÷12 (74.88M ≠ 6.24M as printed). Fixed to match ch16:86's
   correct "… × 260 workdays ÷ 12 = 6,240,000".

## REJECTED / NO-ACTION (28) with reasons

- CH8-PREFILL-ATTENTION-TERM-DOUBLE-COUNT (P0): self-withdrawn by reviewer
  on recomputation — 4·80·9200²·8192 = 0.2219 PFLOP is correct. False positive.
- CH16-TCO-01 (P1): reviewer verdict "None required... do not file" —
  ⌈344/11.305⌉+1 = 32 verified consistent. Coverage entry.
- CH17-T172-01 (P1): all 18 cells + N−1 row recomputed correct. Optional
  3,541→3,540 REJECTED: 3,541 = 200 × 17.703 (unrounded W(3)) → 3,540.6,
  consistent with 40×17.703=708 and 100×17.703=1,770 as printed; the
  reviewer used rounded 17.70. Printed value stands.
- CH17-1701-01 (P2): caption internally consistent on its stated rounded-2.0
  basis (3×2.0=6.0; 5.5/6.0=0.917). Reviewer: "Not required for release."
- CH18-ROUT-01 (P2): $8,147 = (23.75−12.59)×730 = 11.16×730 = 8,146.8 —
  printed chain consistent with its own rounded inputs. "Either defensible."
- CH18-MC-01 (P2): $1,956 = 2.68×730 = 1,956.4 — chain consistent with
  printed $2.68. "Not required."
- CH19-FALLBACK-01 arithmetic: withdrawn by reviewer (recomputed correct);
  only the optional parenthetical was applied (fix #5).
- correction=None coverage entries, all independently spot-checked true:
  CH17-AGNT-01, CH16-BE-01, CH16-CLD-01, CH15-MFU-01, CH17-NET-01,
  CH22-PREFILL-01, CH22-KV8BIT-01, CH24-POISON-01, CH24-PIES-01,
  CH23-BOUND-01, CH20-MARGINAL-01, CH19-LATENCY-01, CH19-REUSE-01,
  CH22-DECODE-BW-01, CH21-CANARY-01, CH24-FP-DENOM-01, CH20-AGGREGATE-01,
  CH22-AGG-PFLOPS-01, CH19-AMP-01, CH20-LITTLE-01, CH24-GUARDRAIL-01,
  CH25-ENVELOPE-01, CH25-HOLD-01 (its optional note became fix #8).

Round-1 text closes at 24/24 chunks (MiMo 6, DeepSeek 6, Qwen 6,
Ornith c0/c5=122B + c1–c4=397B). Vision 4 models × 5 batches complete.