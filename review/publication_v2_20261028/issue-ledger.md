# From Token to Fleet — Issue Ledger (consolidated)

Repo: /home/ubuntu/hermes-work/from-token-to-fleet
Release candidate: **R27** — review/publication_v2_20261028/work/accelerated_external_review_proof_r27/render/build/from-token-to-fleet-v20260913.pdf
SHA256 `d700c1979efb2a825da146ac6500d59f452c77f4bd629f054ff04e7c1fd6aec9` · 425 pp · 290+ frozen inputs · 0 Type3 · tagged.

Severity: P0/P1/P2/P3/GATE. A finding is CLOSED only with source diff + rebuild-verify + regression (not a caveat-only change).

## External-review findings (2026-10-30 review) — status
| ID | Sev | Chapter | Status | Evidence |
|---|---|---|---|---|
| FTF-R01 | P1 | Ch19 | **CLOSED** | Table 19-1 now has *Incremental orchestration* (8.8–9.5s) + *Full agentic service time W* (~10.3/12.1/**13.8**/15.6s); Ch19 & Ch17 agree 13.8s at T=3. Verif: r27 build, full-service-time row p302/p312. |
| FTF-R02 | P1 | Ch19 | **CLOSED** | Event-ledger: task_input 41,990, task_output 495, peak 12,095→31.7GB, billed 42,485/12,290, 4.47× vs α 1.27×. `31,660` removed. |
| FTF-R03 | P1 | Ch20 | **CLOSED** | Fig 20.1 caption + 3-series plot; gap = unused capacity, not scheduling overhead. |
| FTF-R04 | P1 | Ch16 | **CLOSED** | Declared fixed-40rps-peak duty-cycle case (not scalable); 7.49M frozen-fleet crossover; INFEASIBLE >24.96M shaded. |
| FTF-R05 | P1 | Ch19 | **CLOSED** | Unconditional fallback ledger (p95 660ms / p99 860ms / 24,415 tok per completed). |
| FTF-R06 | GATE | Ch4/16/17 | **OPEN (deliberate)** | Active-active multi-region unpriced/unvalidated; preserved as a scoped gate (NOT COMPARABLE). Do NOT claim single-region TCO closes the canonical active-active requirement. |
| FTF-R07 | P2 | Ch16 | **CLOSED** | Tables 16-1/16-2 rebalanced 5 numeric cols + A/B/C note; multi-region NOT COMPARABLE. |
| FTF-R08 | P2 | Ch19 | **CLOSED** | Figs 19.2/19.3 8.4pt (was 6.0), magnified inset (δ=800/γ=65/O=300), counterfactual semantics. |
| FTF-R09 | P2 | Ch20 | **CLOSED** | Cost-per-query re-scoped to a stated load path (fixed vs scaled demand). |
| FTF-R10 | P2 | App A | **OPEN** | Pin moving raw/main URLs; shrink long URLs; source-verification ledger. (Audit in progress.) |
| FTF-R11 | P2 | several | **PARTIAL** | Captions tightened for Fig 19.1/19.2/19.3; more captions may need the 3-part convention. |

## Prior-loop findings (R20–R26) — resolved or documented
All 40 R23 findings resolved or deliberately held; R24 corrections (C004 short-tail, renderer/nav), R26 PDF/UA conformance (headings H2–H4, TOC/LOF, figure alt, formula alt, table /Headers, 0 dangling MCR) verified. Ch19 figure-page gaps (C-02/C-03) documented, not applied (needs risky float change).

## Audit batch 1 (Pass D/E/G + R10) — findings (2026-10-30)
Independent audit (deleg_9f9359aa) ran arithmetic recompute (149/155 PASS), figure vision (57 figs, 0 P0), Pass-G discovery (19 new), R10 source pinning.

### New findings — status
| ID | Sev | Loc | Status | Evidence |
|---|---|---|---|---|
| FTF-N01 | P1 | Ch5 §3 | **FIXED (renderer)** | A whole `[HYPOTHESIS]` paragraph (line 62, "0.8 ms on a single CPU core / decision hinges") was missing from R27 PDF. Root cause = pandoc parsed the FIRST plain-prose `[HYPOTHESIS]: <text>` as a reference-link definition (text=URL), consuming it; later ones rendered only as *references*. Fixed in `render/latex/md_to_latex.py` convert(): insert NBSP between `]` and `:` on leading `[LABEL]:` callouts → renders `[LABEL]: prose`. Isolated ch5 rebuild confirms content restored, 0 leftover href; TARGET ≥8pt, brackets preserved. **Also fix the sub-number (FTF-N06) before/with rebuild.** |
| FTF-N02 | P2 | Ch4 §4.3 | OPEN | p83 cross-ref "the 3.3M is whole-fleet aggregate" — `3.3M` nowhere else in book; Ch5 reconciliation note actually reconciles 50 vs 8,000 tok/s, no 3.3M; Ch4's own queue-wide is 2.76M–2.85M. Fix: point to the real number/reconciliation or drop the paren. |
| FTF-N03 | P2 | Ch15 §6 | OPEN | "~35,000–70,000 tokens/s" single-host achievable = 124% MFU (ceiling ~56.5K at 100%). Contradicts own mini-case where 70,000 needs a 2nd host. Fix: cap ≤~56K or label prefill+decode mixed. |
| FTF-N04 | P2 | Ch5/6/15 | OPEN | batch-1/stream throughput 50 tok/s (Ch5/6) vs 8,000 tok/s (Ch15) = 160×; 8,000 is the prefill rate mislabeled. Fix: align the throughput basis. |
| FTF-N05 | P2 | Ch15 | OPEN | "Ch14 *measures* p95 TTFT 1.9s" — Ch14 is explicitly hypothetical, different load; and Ch14 "5s tail breaches p95 SLO (Ch6)" vs Ch6 p95=0.99s (healthy). Fix: reconcile load/status. |
| FTF-N06 | P2 | Ch5 | OPEN | the missing line-62 paragraph itself: "~0.8 ms single CPU core" needs 13.9 TFLOP/s/core (implausible); recompute. (Recovered from the missing para.) |
| FTF-N07 | P2 | Ch15 | OPEN | 1-host/40-rps framing vs book's ~21 hosts. |
| FTF-N08 | P2 | Ch22 | OPEN | "derived, not stipulated" 10/40 rps vs Ch4 "declared, not derived"; align wording. |
| FTF-N09 | P2 | Ch23 | OPEN | Table 23-1 cost row not established in the dialogue the chapter says it needs. |
| FTF-N10..N19 | P3 | various | OPEN | 0.8ms CPU-core math; Table 3-2 14B vs 12.8B; Ch4 "Self-host" priced from cloud rate; KB/KiB + binary-K slips; App A "4–10×" vs own 14×; etc. See audit/discovery-audit.md + audit/d1-*.md. |
| D1 | MED | Ch4 §4.8 | **IN FIX** | 50 rps host count 25/36 uses continuous 17.5; per whole-slot convention should be 26/37. Fix dispatched. |
| D2–D7 | LOW | Ch16/19/9 | OPEN | D2 40.2→40.1; D3 W(3)=13.854→13.9 (book discloses as Ch17 lower bound); D4 Ch19 formula{10.5,12.4,14.2,16.1} vs held-1.08 table{10.3,12.1,13.9,15.6}; D5 Ch4 prefill ~23→24; D6 Ch19 α(T=2) 1.12× vs Table 19-1 1.18× (unreconciled); D7 Ch9 15.5h→15.6. |
| R10 | P2 | App A | **FIXED** | repo/refs pinned to immutable commits (16 repos/22 refs); printed URL chars 4,029→173; Oct-28 addendum explicit; 2 habana URLs UNVERIFIED (kept); ch7/8/9 moving refs left (out of scope) — live ch27 sha b0448a46. |

### Figure-vision P1/P2 (Pass E) — status
P1: **Fig 22.1 7.8pt / Fig 26.2 7.6pt** (fix dispatched), **Fig 6.2 caption 86-char** (fix dispatched). P2 (16.1 annotation leaders/feasible-max white box, 18.1 arrows/else, 19.2 legend swatches+pattern conflict, 19.3 no y-axis/units, 21.1 feedback arrow+grayscale, 22.1 legend N reuse+red dot, 7.5 9.5K@10K, 15.2 plateau, 10.1 hatch/solid, 12.1 redundant arrow, 23.1 floating triangle, 25.1 arrow 6.5pt short, 2.2 annotation/roofline, 2 color-only, 7.8/11.1 grayscale, A.2/A.4) → next iteration. P3: 34 figures polish.
Counts: **57 numbered figures** (58 = 57 + cover Figure element). 0 scientific/arithmetic P0.

## Round 2 (independent audit findings) — R28
All fixes below are in live and being integrated into **R28** (`accelerated_external_review_proof_r28`, 291 inputs, 14 overlays). Status lines updated.
| ID | Sev | Status | Notes |
|---|---|---|---|
| FTF-N01 | P1 | **CLOSED** | renderer fix (NBSP in `convert()`) restores the lost Ch5 `[HYPOTHESIS]` paragraph; isolated ch5 build confirms content back; brackets preserved. |
| FTF-N02 | P2 | **CLOSED** | Ch4 "3.3M" dangling ref removed → points to real Ch5 9,000 (single-stream) vs Ch4 ~2.76M/2.85M. `3.3M`=0. |
| FTF-N03 | P2 | **CLOSED** | Ch15 single-host range capped `70,000→56,000` (124%→99% MFU; 100% ceiling 56,500). Cross-refs (ch5/6/17/20) synced to `35,000–56,000`. |
| FTF-N04 | P2 | **CLOSED** | Ch15 8,000 labeled prefill-side/whole-request (≈8.5K = 9,200/1.08), NOT batch-1 decode (~40 tok/s); ch5/6 phase labels added. |
| FTF-N05 | P2 | **CLOSED** | Ch15 no longer calls Ch14's 1.9s a *measurement* — it's `*assumes* [UNMEASURED]` under lighter 1.3 rps. |
| FTF-N06 | P2 | **CLOSED** | Ch5 `[HYPOTHESIS]` 0.8 ms single-core → recomputed Δ≈11.1 GFLOP; single-core 56–370 ms (over budget) vs local-GPU ~1.1 ms (within ~120 ms budget). `0.8 ms` gone. |
| FTF-N07 | P2 | **CLOSED** | Ch15 1-host/40-rps framing scoped as per-request/micro-benchmark vs the ~21-host fleet canonical. |
| FTF-N08 | P2 | OPEN | Ch22 "derived, not stipulated" 10/40 rps vs Ch4 "declared, not derived"; align wording. |
| FTF-N09 | P2 | OPEN | Ch23 Table 23-1 cost row not established in dialogue. |
| FTF-N10..N19 | P3 | PARTIAL | 0.8ms, Table 3-2 14B, Ch4 Self-host pricing, KB/KiB, App A 4–10×; see discovery-audit.md. |
| D1 | MED | **CLOSED** | Ch4 50 rps 25/36 → **26/37** (whole-slot ceil 430/17=25.29→26, 430/11.9=36.13→37); conclusion unchanged (26>21). |
| D2–D7 | LOW | OPEN | 40.2→40.1; W(3) 13.9; Ch19 formula-vs-table {10.5,12.4,14.2,16.1}; prefill ~24; α(T=2) 1.12 vs 1.18; Ch9 15.6h. |
| fig-P1 | P1 | **CLOSED** | Fig 22.1 7.79→**8.17pt** (width 0.95 shrinkage; labels 8.5→8.6), Fig 26.2 7.60→**8.60pt** (labels 7.6/8.2→8.6); Fig 6.2 caption 86→378 chars (3-part). New shas fig-22-2201 `8906712e…`, fig-26-2601 `9e436cde…`. |
| R10 | P2 | **CLOSED** | Appendix A refs pinned to immutable commits; URL chars 4,029→173; 2 habana UNVERIFIED; ch27 `b0448a46`. |
| fig-P2 | P2 | OPEN | 16.1 annotation leaders/feasible-max box, 18.1 arrows/else, 19.2 legend/pattern, 19.3 y-axis, 21.1 feedback arrow/grayscale, 22.1 N reuse/red dot, 7.5 9.5K@10K, 15.2 plateau, 10.1 hatch, 12.1 arrow, 23.1 triangle, 25.1 arrow, 2.2, 2, 7.8/11.1 grayscale, A.2/A.4. |
| fig-P3 | P3 | OPEN | 34 figures polish (grayscale redundancy, margins, wording). |
| Ch16 D2 / Ch19 D3-D6 / Ch9 D7 | LOW | OPEN | — |

**Round-2 verdict:** every confirmed P0/P1 is closed (0 open P0/P1 from the independent audit). Remaining P2s (fig-polish, N08/N09, D-low arithmetic) + external gates. R28 in build.
- **4 heading-skips** (ch09/10/15 `#### Table N-M` → H4 under H2): veraPDF warning-level; left in uncontracted R27.
- **`pdfuaid:part`**: NOT set — requires veraPDF/PAC preflight (not installed) to legitimately declare PDF/UA-1.
- **Exact original 362pp canonical**: not recoverable (accidentally overwritten); live canonical preserved but not the original.
- **Release-version consistency**: `v20260913` spans multiple content states; to resolve at publish.
- **External gates**: font/image rights manifest, ISBN, physical print proof, author sign-off.

## Audit batch in progress (autonomous loop)
- deleg_9f9359aa (4 readers): independent arithmetic recompute; figure vision (58 figs); Pass-G discovery (new FTF-N###); Appendix-A source audit + R10.
Results to be folded here. Verdict current: **RELEASE CANDIDATE** (content + P1 fixed). Publication approval still **FALSE** until external gates.
