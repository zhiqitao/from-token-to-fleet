# Round 3 — Text disposition ledger (127 issues, 18 chunks: 6 DeepSeek + 6 Qwen + 6 MiMo)

Method: quote-presence triage (triage.json: 38 PRESENT / 12 ABSENT), then
independent re-verification per item (source grep + arithmetic recompute) before
any fix; absent quotes = rejected as fabricated unless a flexible search finds a
paraphrase. Panel: MiMo-V2.6-Flash-RL / DeepSeek-V4.1-Flash / Qwen3.8-27B.

## Wave 0 — first pass, 52 issues → 34 fixes / 18 rejects

Representative fixes: ch18 $0.0025 → $0.0000025; ch6 prefill 1.29 PFLOP
qualifier; ch13 non-integer prefill screen; ch19 alpha semantics; App A
DeepSeek ≈14×; ch8 GB200 4,500/281 (Qwen catch of the Round-2 flopper-row
error); ch15 8.75× → 8.2× (3-model consensus); ch11 KV-35GB 13.3K alignment;
ch11 spelling -ization; ch20 41.5 = C_analytic; ch24 loop starts at red team.
Rejects: 18 items — fabricated quotes (triage ABSENT), already-satisfied
Round-2 items, and claims refuted by source arithmetic.

## MiMo ladder c2 (chapter 9) — 16 issues → 16 fixes / 0 rejects

- CH9-01 (P1): "per-step data movement is A plus B" conflated the per-sequence
  P/D KV transfer with per-step traffic → split into per-step (TP all-reduce)
  vs one-time (KV fragment at the P/D boundary).
- CH9-02 (P1): "translates to higher throughput per dollar" unqualified →
  added the conditions (comm share significant + premium repaid).
- CH9-03 (P2): "Diagonal dominant tensors … less uniform" — dense ring traffic
  is content-independent → scoped to sparse/compression.
- CH9-04/05 (P2): 40–60% of peak and 5–10× Ethernet price → [ILLUSTRATIVE].
- CH9-06 (P2): 17 slots → xref (Ch. 7, Fig 7.7: C ≈ 17.5, floor 17).
- CH9-07 (P2): 1.8 TB/s "node-level aggregate" → NVLink 5 per GPU.
- CH9-08 (P2): orphan figure-spec HTML comment → removed.
- CH9-09 (P3): ~2–3 orders → ~2 (3,350/25 = 134×).
- CH9-10 (P3): P-D → P/D.
- CH9-11 (P3): "New collectives" → compression/approximation techniques.
- CH9-12 (P3): NVLink-connected hosts → NVLink-equipped (GPUs on-node).
- CH9-13 (P3): "latency per byte" → compute may offset bandwidth savings.
- CH9-14 (P3): square matrices → standard dense buffers.
- CH9-15 (P3): crammed parenthetical split (exception + ring factor).
- CH9-16 (P3): 8×H100 "connected by NVSwitch" → NVSwitch inside each node.

## MiMo ladder c4 — 22 issues → 17 fixes / 5 rejects

Fixes: CH20-01 (§2 xref dropped — discussion is local), CH20-02 (41.5/1.04 =
21-host only; 22-host ρ-derated 41.3/1.03 added), CH20-04 (dispatch-frequency
mechanism specified), CH20-05 (video subsection 4 paras → 1, principle kept),
CH22-BW (table row → decode weight-read BW rate), CH22-S7a/b (item 2 softened
to "may ignore" + workload-dependent; item 4 unified to the hypothesis
parenthetical), CH22-2000 (~2,000-user), CH22-AGG ×2 (aggregate single-device
→ whole-model figure before TP sharding), CH23-10RPS (average-rate Q&A added
to the dialogue — Bound 1's ~10 rps now derived), CH23-B5 (forces → primary
path with cloud fallback), CH23-TBL (p95 TPOT ≤ 35 ms added to Table 23-1),
CH23-SCR (screens out → rules out), CH23-W1-3 + CH24-W + CH25-W (What We
Still Don't Know unified: "unresolved: evidence pending" / "a hypothesis
awaiting verification" vocabulary across ch22-25), CH25-30GB (derivation:
2×80×9.2K×8,192×2 B ≈ 24 GB + working tensors ≈ 30 GB), CH25-A100 (H100-only
in the H100 ADR), CH25-RQO (single-use acronym dropped), CH21-PARTVI (6
mechanisms / 5 parts disambiguated).

Rejects (5): CH20-03 ("Λ_fleet = N × Q" absent book-wide), CH24-3.3-BINDING
(P1 — text already states the FP16 flip: prefill ~4.1 vs KV ~4.9 at 40%),
CH24-MINICASE (P1 — text already flags BOTH metrics: FPR 2.4% and guardrail
5.4), CH22-MINICASE-CH7 (no prose Ch-7 reading-order phrasing; only source
citations), CH22-FIGNOTE-RATIO (full-square convention stated in the adjacent
paragraph + figure note).

## MiMo ladder c5 — 37 issues → 29 fixes / 8 rejects

Fixes (ch26): 01 Pattern A marked baseline-reference in the apply step (R-04);
04 ×2 editorial "old figure" references dropped; 07 load cycle defined; 09 §6
sharding = baseline configuration determines profile; 10 §7 questions vs
hypotheses conflation fixed; 11 250-ms arithmetic added (120+80+50; queue
drain at cached ~1.3 rps); 13 Step 0 fingerprint read added to the capstone;
05+06 Fig 26.1 alt trimmed, provenance moved to a note, script filename
removed; 17 Fig 26.2 alt condensed to a Note.
Fixes (ch27/App A): 02 [FACT] scope note on the Axis-2 line (runtime-measured
vs documented-first-hand; Axis 1 carries who); 14 [INTERPRETATION] →
[ASSUMPTION] when a three-axis status is required; 15 opening 4 blockquotes →
1 snapshot note, 2 dated addenda moved to the post-snapshot notes; 19 "A
striking number of" → "Four 2026 frontier open models we surveyed"; 21 "That
is why" → "We read this as a driving reason"; QWEN-TOTAL 125 B MoE total;
DS-PARAM+10X ~10–14× across V4 variants + architectural-not-smaller-model;
S6-REF dangling [S6] removed (sentence self-cites vLLM Table 3); ENGRAM gloss;
RENOISE gloss (named serving recipe); 890BPT [1P] not-re-derived note;
TRAINCOST basis note; FLOOR "teaching floor" → "foundational teaching model";
VIDEO (T,H,W) axis labels; SPARSELINEAR sparse+linear → sparse and linear;
INTEL-FOOTNOTE 18 boilerplate sentences deduped to one section-level caveat.

Rejects (8): CH26-03 (P1 — text already states 45% and 68% are separate
scenario values needing one load test under a single SM-utilization
definition), CH26-08 (P1? — ~2.0 rps explicitly framed as the host's
sustainable ceiling, "not a multiple of it"), CH26-12 (queueing exclusion
explicitly stated twice: "service-time sums with no queueing term"), CH26-18
("recovery grace-period latency" FACT name absent), CH26-20 ("Definition of
active" paragraph absent), APPX-KVBAND (band already scopes both endpoints +
"not a universal constant"; Round-2 APPA-KV-BAND also rejected), APPX-EVLABEL
([LAB]/[2°] = Axis 1, [FACT] = Axis 2, [ANALYTICAL] = Axis 3 defined in the
Sources chapter), APPX-BORDER-REMAKING ("Remaking" absent), APPX-A7-REF
(A.N = appendix section numbers with a +2 offset: A.7 = §5 canonical
arithmetic = the reprofiling/re-derivation section; A.10 = §8 sources —
reference resolves).

## Totals

- Wave 0: 52 → 34 fixes / 18 rejects
- c2: 16 → 16 / 0
- c4: 22 → 17 / 5
- c5: 37 → 29 / 8
- **Grand text: 127 → 96 fixes / 31 rejects**

Combined with vision (116 → 61 / 55): **Round 3 = 243 findings → 157 fixes /
86 rejects.** (Round-3 vision coverage expansion to 84 figure pages inflates
the raw count; severity mix: text P1 = 4 total, 2 rejected on re-verification.)