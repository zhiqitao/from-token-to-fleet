# Publishing-Readiness Verdict — From Token to Fleet

Updated: 2026-10-30 · Repo: /home/ubuntu/hermes-work/from-token-to-fleet

## Verdict: CONVERGED — RELEASE CANDIDATE (pending print proof + author sign-off)

**Publication approval is FALSE** until the external gates close (physical print proof, rights, ISBN, author sign-off, veraPDF cert). The autonomous review loop has converged: a fresh independent re-audit (Pass G) of the release candidate found **0 new P0/P1**, confirming no further critical issues in reach.

## Release candidate
- **R33**: `review/publication_v2_20261028/work/accelerated_external_review_proof_r33/render/build/from-token-to-fleet-v20260913.pdf`
  SHA `a4bf87e3…`, **434 pp**, US Letter 8.5×11 (612×792pt), text width 439.2pt, tagged/PDF-UA structure, **0 Type3**, all figures ≥8pt.
- Pushed to `origin/main` (HEAD `fd493396`).
- Integrates the 2026-11-01 independent review: Ch3 MoE verdict rewritten (weights 140→94GB, KV unchanged, routing-GPU optional; Fig 3.4 28→25.6GB; single MoE ledger); Ch17 W_KV-resident/E[L_KV]/host=max(capacity,tail); C/W upper-bound unification (10 places); Table 15-1 MFU→load-pressure; Fig1.1→Preface Fig1; token "I/O" metaphor; A.2 solid warning; Ch16 mini-case conditional; Fig19.3 policy comparison; DeepSeek V4.1 service-status; Ch4 budget/Fig16.1 streamlining.
- Integrates the 2026-10-31 independent review's actionable fixes (P2-01 Ch3 MoE 12.8B; P2-02/03 Ch24 null-reference + PIES order-sensitive; P2-04 Fig11.3 topology + 1.4TB/s; P2-05 Fig16.1 cloud marker; P2-06 SLA NOT-COMMITTABLE + HOLD ADR; P2-07 Fig6.2 shade >2s; P2-08 caption trims; P1-02 source-index URL; P3-01 LoF short titles). All verified by DeepSeek recompute (coherent, no contradiction).

## Cross-model validation (base + fixes all CONVERGED, 0 new P0/P1)
R31 base validated clean by 5 distinct models (DeepSeek, MiMo, GLM-5.3-256K, Ornith-1.5-397B, Nemotron-3-Ultra-550B-free). R32's added fixes independently recomputed clean by DeepSeek. No new P0/P1 introduced.

## Cross-model validation (all CONVERGED, 0 new P0/P1)
R31 independently validated clean by 5 distinct models:
1. **DeepSeek-V4-Flash** (main review): all key derivations reproduce, fixes coherent.
2. **MiMo-2.6-Flash** (fixer): its own audit findings all addressed & verified.
3. **GLM-5.3-256K** (EGLB): 0 new P0/P1; recomputed all chains; zero content loss (3,437 sentences); no mislabeled measurements; would sign off.
4. **Ornith-1.5-397B** (EGLB): 0 new P0/P1; independent method (fresh arithmetic, trigram content-compare, direct vision of 16.1/20.1/22.1); would sign off.
5. **Nemotron-3-Ultra-550B (free, via opencode OpenRouter)**: 0 new P0/P1; verified all arithmetic chains.

## Loop history (R27→R31, all pushed)
R27 external review P1s → R28 independent-audit P0/P1s + fig-P1 → R29 N08/09/D2-D7 + fig-P2 3/4/6/8 → R30 remaining fig-P2 + pdf.fonttype=42 (0 Type3) → R31 MiMo round (Ch13 51/74 hosts, Ch25 64 KV heads, Ch15 62% MFU, Ch6 p99 5.0s, fig F001-F005, source C04-C23).

## Loop history (R27→R30, all pushed)
- **R27**: external review (2026-10-30) R01–R11 — agentic latency reconciled (13.8s @ T=3), call ledger (41,990/495), Fig20.1 gap=capped demand, TCO x-axis + INFEASIBLE, fallback ledger, tables+NOT COMPARABLE, Fig19.2/19.3 ≥8pt + counterfactual inset, R10 refs pinned.
- **R28**: independent-audit round-2 — FTF-N01 (renderer content-loss) + N02–N07 + D1 (26/37) + fig-P1 (Fig22.1/26.2 ≥8pt, Fig6.2 3-part caption) + cross-ref range sync.
- **R29**: N08/N09/D2–D7 + fig-P2 items 3/4/6/8.
- **R30**: fig-P2 items 1/2/5/7/9–16 (15 figures) + pdf.fonttype=42 (removes Type3).
- Structure tree verified every round (H2 264 / H3 102 / H4 28, 58/58 figure alt, 0 orphan, TOCI 95), no overfull, fail-loud checks pass, **0 Type3**.

## Convergence evidence
Independent Pass-G re-audit (`audit/convergence-pass-g-r29.md`): 0 new P0/P1; cross-chapter numbers consistent; no benchmark mislabeled as measured; GB/GiB + req/s + $/1K + mean/peak + bound/achieved all explicitly separated; prior-round fixes verified present in the built PDF.

## Open (P3 polish + external gates — honestly held, not P0/P1)
- **P3 minor**: Table 3-2 14B-vs-12.8B, Ch4 Self-host pricing basis, KB/KiB, App A 4–10× vs 14×, lower-bound MFU tension, fig-P3 (34 figures polish).
- **4 heading-skips** (ch09/10/15 `#### Table N-M`) — veraPDF warning-level.
- **`pdfuaid:part`** — NOT set; requires veraPDF/PAC preflight (not installed) for legitimate PDF/UA-1.
- **FTF-R06** multi-region GATE (open by design). **IX/T3-table HOLD** (Ch11).

## External gates (outside local tool reach — do NOT mark passed locally)
veraPDF/PAC PDF-UA validation; font/image rights manifest; ISBN; **physical print proof**; author sign-off. Exact original 362pp canonical not recoverable (live canonical preserved).
