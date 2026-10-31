# Publishing-Readiness Verdict — From Token to Fleet

Updated: 2026-10-30 · Repo: /home/ubuntu/hermes-work/from-token-to-fleet

## Current verdict: RELEASE CANDIDATE — pending print proof + author sign-off

Publication approval is **FALSE** until the external gates close. Content is internally consistent and all audit-critical findings are resolved.

## Release candidate
- **R29**: `review/publication_v2_20261028/work/accelerated_external_review_proof_r29/render/build/from-token-to-fleet-v20260913.pdf`
  SHA `92f57585…`, **425 pp**, US Letter 8.5×11 (612×792pt), text width 439.2pt, tagged (PDF/UA-structure), 0 Type3.
- Pushed to `origin/main` (HEAD `89a557bb`).

## Closed across 3+ autonomous loop rounds
- **External review (2026-10-30) R01–R11**: agentic latency reconciled (Ch19/17 both 13.8s at T=3), call-ledger boundary (41,990/495), Fig20.1 gap=capped demand, TCO x-axis stated + INFEASIBLE shading, fallback ledger, tables rebalanced + NOT COMPARABLE, Fig19.2/19.3 ≥8pt + counterfactual inset, cost re-scope, R10 refs pinned.
- **Independent audit round 2**: FTF-N01 (renderer content-loss) fixed; N02–N07 + D1 (26/37) closed; fig22.1/26.2 ≥8pt.
- **Round 3**: N08/N09/D2–D7 + fig-P2 items 3/4/6/8 closed.
- Structure tree verified each round (H2 264 / H3 102 / H4 28, 58/58 figure alt, 0 orphan, TOCI 95, 0 Type3), no overfull boxes, all fail-loud checks pass.

## Open (documented, honest)
- **Remaining fig-P2 polish** (items 1/2/5/7/9–16) and **fig-P3** (34 figures) — visual polish, not correctness.
- **P3 minor** (N10–N19: Table 3-2 14B-vs-12.8B, Ch4 Self-host pricing basis, KB/KiB, App A 4–10× vs 14×, lower-bound MFU tension).
- **4 heading-skips** (ch09/10/15 `#### Table N-M`) — veraPDF warning-level.
- **`pdfuaid:part`** — NOT set; requires veraPDF/PAC preflight (not installed) for legitimate PDF/UA-1.
- **FTF-R06** multi-region GATE (open by design; single-region TCO is not a multi-region recommendation).
- **IX/T3-table HOLD** (Ch11 Table 11-2 hardware row).

## External gates (outside local tool reach — do NOT mark passed locally)
- veraPDF/PAC PDF-UA validation; font/image rights manifest; ISBN; **physical print proof**; author sign-off.
- Exact original 362pp canonical not recoverable (live canonical preserved `82006201…`), documented.

## Convergence
A fresh independent re-audit (Pass G) of R29 is in flight. If it returns CONVERGED (0 new P0/P1), this verdict stands as RELEASE CANDIDATE and only the external print/proof/approval gates remain.
