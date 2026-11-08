# Round 2 — disposition (3-model panel: MiMo-V2.6-Flash-RL, DeepSeek-V4.1-Flash, Qwen3.8-27B)

Panel note: Ornith removed 2026-11-08 (user directive) — see ../panel.md and render/review_loop.py.
Round-2 collection: text 18/18 (MiMo c1/c4 needed retry; c4 via chapter-boundary split), vision 15/15.
Total issues: 54; ACCEPT: 42; REJECT: 12; UNMAPPED: 0.

## P1 (3)
- **CH17-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c3.js) — ch17 §17.4: bound sentence rewritten — prefix caching/batch load change the EFFECTIVE C or W (recompute required); under fixed C and W achieved cannot exceed C/W.
- **APPA-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c5.js) — ch27 'active' definition: N-gram now 'excluded from the active-fraction denominator (Fig A.1 note)' — aligns with the Fig A.1 footnote and the 4.8% backbone ratio.
- **CH8-COST-01** [ACCEPT] (text_MiMo-V2.6-Flash-RL_c1.jso) — Scoped: ch8:179 $/1K quotations now carry 'canonical 6.24M-req/mo basis'. REJECTED the reviewer's 25.92M (24x7) recompute — the book's canonical volume basis is business-hours (Ch 4/16), so $24.97/1K stands.

## P2 (24)
- **CH3-KV-OFFLOAD-GROWTH** [ACCEPT] (text_DeepSeek-V4.1-Flash_c0.js) — 'or KV offload' removed from the attention-mechanism list + explicit clause: offload changes where the cache resides, not how fast it grows.
- **CH3-BOXED-RULE-FLOP-UNIT** [ACCEPT] (text_DeepSeek-V4.1-Flash_c0.js) — Boxed rule now reads '~25.6 GFLOP) and the active weight-read traffic (~25.6 GB ...)' — FLOPs and bytes separated.
- **CH4-TCO-API-BASIS-CONFLATION** [ACCEPT] (text_DeepSeek-V4.1-Flash_c0.js) — Economic-feasibility bullet splits the two bases (owned $20/h vs API list $0.012/req) and labels the API figure 'not a self-host TCO'.
- **CH4-2K-INPUT-TCO-LINEARITY** [ACCEPT] (text_DeepSeek-V4.1-Flash_c0.js) — Same bullet: the 2K->~$0.003 linearity now explicitly scoped 'On the API basis'.
- **CH5-ECON-UNIT-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c1.js) — 5 spots aligned to the chapter's own unit-note canonical 'tokens per dollar': ch5 table header+value, ch5:91 derivation, ch5:93 note tail, ch5:95, ch4:193 cross-ref x2.
- **CH5-ECON-CONCLUSION-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c1.js) — Takeaway conditioned: 'under this chapter's stated assumptions — the break-even dQ/Q of 3(b) is parametric here, not measured for this workload'.
- **CH7-128K-FIT-01** [REJECT] (text_DeepSeek-V4.1-Flash_c1.js) — Table label and note are consistent: 'passes aggregate bytes only' = only gate 1 established; the note itself states the 128K row clears gate 2's shard check but NOT its per-rank runtime/workspace sub-clause, which is why the label stands. Reviewer misreads the label as a full gate-2 claim.
- **CH9-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c2.js) — 1000-iter total now states both: '~56,000 s (15.6 h) at the flat lower bound — ~98,000 s (~27.2 h) under the ring factor'.
- **CH12-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c2.js) — Scoped: 436 defined inline at first ch12 use '(640 - 140 weights - ~64 runtime ~ 436 GB, Ch 7/17)'. REJECTED the reviewer's 422 recompute — 436 is the memory carve-out, not 17.5 x per-request KV; 576 stands.
- **CH12-02** [ACCEPT] (text_DeepSeek-V4.1-Flash_c2.js) — Table 12-2 (b) cost cell: '+ fabric and the decode-pool split (adders not costed in Ch 16; the ~21 hosts is the Ch 16 fleet-level screen, not a two-pool sum)'.
- **CH13-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c2.js) — 40-rps spot made explicit two-step: 'full-utilization screen — ceil(344/17)=21; under the 70% x 95% policy ... 31 working + 1 spare = 32 total, Table 17-1'. NOTE: the reviewer's claim about the 100-rps example is wrong — ch13:53 already states the full chain (51 -> 74/78); left as-is.
- **CH17-02** [ACCEPT] (text_DeepSeek-V4.1-Flash_c3.js) — SCOPE EXPANDED beyond the 5 quoted spots — 8 revision-language leaks removed: ch17:254/266/268 (13.8/13.85 s 'superseded; A-01'), ch17:118 + ch16:60 (29/30 'superseded' -> reader-facing rho-omitted variant), ch17:93 ('superseded u-only screen' -> 'rho=1 u-only comparison screen', it is a LIVE comparison row), ch17:283 ('(A-01)' review id), plus ch19:176 + ch19:302 found by sweep (same 13.85 s class, reviewer missed them).
- **CH15-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c3.js) — 'before also reserving weight residency' -> 'the 436 GB is already net of the 140 GB weights and ~64 GB runtime'.
- **CH16-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c3.js) — 'The token arithmetic alone therefore does not send this startup to the API' — the adjacent sentence already names the opportunity-cost flip; 'alone' removes the standalone misread.
- **CH24-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c4.js) — ch24 Candidate A parenthetical: KV screen now 'on the FP16-KV basis (10 rps x 8.6 s x ~24.9 GB per 9.5K-max request / 436 GB ~ 4.9, Ch 17) — Candidate A's 8-bit KV halves its own KV screen to ~2.5 hosts'; conclusion (prefill binds) preserved.
- **CH26-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c5.js) — Both hit-path statements now say '— replacing corpus retrieval —' before 'skips the engine', matching Step 2's 'no corpus retrieval and no LLM prefill'.
- **CH26-02** [ACCEPT] (text_DeepSeek-V4.1-Flash_c5.js) — 'confirms the hypothesis' -> 'illustrates the hypothesis ... (to be validated by the load test of Sec. 4)'.
- **CH23-FIG-01** [ACCEPT] (text_MiMo-V2.6-Flash-RL_c4.jso) — INVERTED fix: the figure was vision-verified — it has FIVE numbered question gates + 1 green output box, so the CAPTION ('five question gates') is correct and stays; the internal spec comment 'six labeled question gates' -> 'five'.
- **CH22-EVID-01** [ACCEPT] (text_MiMo-V2.6-Flash-RL_c4.jso) — Sentence now names the tags Table 22-1 actually uses: 'tagged [canonical scenario]/[ASSUMPTION]/[DERIVED]/[ILLUSTRATIVE] in Table 22-1'.
- **CH24-LABEL-01** [ACCEPT] (text_MiMo-V2.6-Flash-RL_c4.jso) — Red-team win rate Type HYPOTHESIS -> DERIVED (Sec. 2: DERIVED = computed from lower-level data; a proportion of cycles is computed, not an unverified claim). Target '-> 0 over time' unchanged.
- **APPA-SECNUM-01** [REJECT] (text_MiMo-V2.6-Flash-RL_c5.jso) — Verified against the built PDF as the reviewer instructed: headings render as A.1.-A.10. (LaTeX auto-numbering; the md's manual '1.-8.' prefixes are stripped — p418 'A.3. DeepSeek-V4 ...', p437 'A.10. First-hand Sources'), and cross-refs A.3/A.10 resolve correctly. No double numbering in the shipped artifact.
- **FIG-1.1-01** [ACCEPT] (vis_DeepSeek-V4.1-Flash_b0.jso) — Figure label 'one K/V per step' -> 'per layer·head' (archify JSON + regenerate_ch1 chain). Containment measured: sublabel [147.9-230.2] inside orange box [127.7-250.5]; placed floor 8.17pt. NOTE: the longer 'one K/V per layer·head' was tried first and MEASURED to overflow the fixed-width box (vision + drawing-rect check), so the final label drops 'one ... per step' (implied by 'append' + token arrows; the caption carries the full 'one K/V per layer per head').
- **FIG-1.1-02** [REJECT] (vis_DeepSeek-V4.1-Flash_b0.jso) — Vision-verified on the figure: the token column's vertical top->bottom order IS the time axis (token1 first at top, entry points ordered); left->right is the data/processing flow, not a time axis. No conflict.
- **FIG-19.2-01** [REJECT] (vis_DeepSeek-V4.1-Flash_b4.jso) — Vision-verified: the note reads 'each column = a separate completion after T turns' — T is the variable equal to the column's x position (0-4). The reviewer misread the variable T as the digit 4.

## P3 (27)
- **CH2-DECODE-BANDWIDTH-CONSTANT** [ACCEPT] (text_DeepSeek-V4.1-Flash_c0.js) — 'decode bandwidth is constant per token' -> 'the weight-read bytes per token are fixed, so at a given HBM bandwidth the decode rate is roughly constant per token'.
- **CH6-P99-CONTRADICTION-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c1.js) — 'under a 2 s SLO' -> 'against the 2 s tail budget (the SLO itself is stated at p95, Ch 4)'.
- **CH7-ORDER-MAGNITUDE-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c1.js) — 'an order of magnitude' -> 'nearly an order of magnitude (164 GB vs ~1,120 GB)' (6.8x).
- **CH8-H200-RIDGE-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c1.js) — H200's ridge direction explicit: 'more bandwidth at a similar BF16 peak, so its ridge is lower'; GB200 'higher' clause kept.
- **CH14-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c2.js) — 'a residency ceiling' -> 'a single-host residency ceiling'.
- **CH17-03** [ACCEPT] (text_DeepSeek-V4.1-Flash_c3.js) — Second 'FPGA/FP8' occurrence at ch17:283 -> 'FP8' (the first was fixed in Round 1).
- **CH25-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c4.js) — 'does not change decode speed per token' -> 'does not change the weight-read-dominated decode cost per token (it does halve the KV-read bytes, a secondary term)'.
- **CH19-01** [ACCEPT] (text_DeepSeek-V4.1-Flash_c4.js) — Mechanism made explicit: 'the fallback occupies only the top 2% — mass entirely above p95 — so it cannot move the 95th percentile'.
- **CH26-03** [ACCEPT] (text_DeepSeek-V4.1-Flash_c5.js) — 'baseline TTFT' -> 'baseline TTFT budget' and 'uses directly' -> 'declares' — a budget is the p99-appropriate object; the existing scenario-input caveat kept.
- **CH5-T51-01** [ACCEPT] (text_MiMo-V2.6-Flash-RL_c1.jso) — Same fix as CH5-ECON-UNIT-01 (duplicate finding).
- **CH7-T72-01** [ACCEPT] (text_MiMo-V2.6-Flash-RL_c1.jso) — 'Adam: ~16 B/param (m + v + dW)' -> '(FP16 weights + gradients + FP32 master copy + Adam m + v)' — sums to 16, matches the adjacent 4 B/param row.
- **CH15-FLEET-01** [REJECT] (text_MiMo-V2.6-Flash-RL_c3.jso) — Misread: ch15:100 already reads 'the canonical fleet is ceil(430/17) = 26 hosts at full utilization (~37 ... or 39 ...)'; the '~21' quoted correctly refers to the 40-rps peak in the same sentence.
- **CH18-XREF-01** [REJECT] (text_MiMo-V2.6-Flash-RL_c3.jso) — Wrong: ch18 HAS a section 8 ('End-of-Chapter Mini-Case'), so 'Sec. 18.8 mini-case' is a correct forward reference (verified from the section list).
- **CH24-POIS-01** [ACCEPT] (text_MiMo-V2.6-Flash-RL_c4.jso) — Q's period defined at first use ('$Q$ = 10,000 queries per evaluation window'); 'per cycle' -> 'per 10,000-query evaluation window'.
- **CH24-KV-01** [ACCEPT] (text_MiMo-V2.6-Flash-RL_c4.jso) — Same edit: 24.5 GB replaced by 24.9 GB with the 9.5K-max basis stated (Ch 17's own screen value).
- **CH23-BOUND-01** [ACCEPT] (text_MiMo-V2.6-Flash-RL_c4.jso) — Bound 3 now carries the decode-budget percentile: '~25 ms/token thereafter (mean decode budget; p95 TPOT <= 35 ms, Ch 4)'.
- **CH26-ALT-01** [ACCEPT] (text_MiMo-V2.6-Flash-RL_c5.jso) — Same consistency fix as CH26-01: 'cache hits remove the retrieval step' -> 'cache hits replace the retrieval step with a cache lookup and skip the engine' (Alternatives paragraph).
- **CH26-LBL-01** [REJECT] (text_MiMo-V2.6-Flash-RL_c5.jso) — Per Ch 4's own definitions the capstone runs on the canonical workload's inputs, so [canonical scenario] is the correct provenance; [ILLUSTRATIVE] is for worked examples with NON-canonical inputs. HYPOTHESIS tags on to-be-validated claims are correct (Ch 4:104).
- **CH3-MM-01** [ACCEPT] (text_Qwen3.8-27B_c0.json) — '25% of the total parameter mass' -> '25% of the EXPERT parameter mass ... (plus the always-active attention and shared layers)'.
- **CH4-MC-01** [REJECT] (text_Qwen3.8-27B_c0.json) — No conflation: text says 'per host' and writes '8 x 2,471 tok/s' explicitly (= 19,768 ~ 19,800 per host); 2,471 is the per-GPU 35%-MFU rate; 56.5K ceiling likewise per-host (8 x 989 TFLOPS / 140 GB). Arithmetic verified.
- **CH18-01** [REJECT] (text_Qwen3.8-27B_c3.json) — The cell already states both bases: the reserved-KV carve-out (436) and the weights-alone figure (~18); '(640-436)/35 ~ 5' is correct and labeled. The reviewer's suggested '436/2 = 218 GB per copy' would add an unsupported runtime-allocation number (KV pool is shared, not statically split).
- **FIG-1.2-01** [REJECT] (vis_DeepSeek-V4.1-Flash_b0.jso) — False premise: Fig 1.2's caption explicitly says 'The K/V are produced within every applicable layer (not after a single attention stage)' — there is no single-layer claim. The 'single-layer detail' phrase belongs to Fig 1.1's caption, where it is TRUE (the figure draws one layer, h1-h4).
- **FIG-1.2-02** [REJECT] (vis_DeepSeek-V4.1-Flash_b0.jso) — Same false premise; stage order verified matching (Text->Tokenizer->Token IDs->Embedding->Attention->KV Cache, no extra/missing/misordered nodes).
- **FIG-19.2-02** [ACCEPT] (vis_DeepSeek-V4.1-Flash_b4.jso) — Real overlap confirmed and fixed: annotation moved from axes (0.44,0.60) [inside the x=2 bar] to data (0.10, 12000) [clear top-left band]; leader arrow re-verified by vision — crosses no bar body, touches only the gamma sliver. Also fixed a PRE-EXISTING clip found during verification: the 4-line note's last line ran x0=-4.5/x1=441.1 (page 439.2) — dropped the leading 'processed ' (antecedent in the line above); now x0=9.9/x1=429.4, zero out-of-page spans.
- **FIG-19.3-01** [ACCEPT] (vis_DeepSeek-V4.1-Flash_b4.jso) — REAL and measured: placed floor was 7.17pt (min 8.0 x 0.896 downscale, figure 490.2pt > 439.2 column). Fixed by narrowing content (suptitle shortened+9.8pt, 3 grey annotations trimmed, defs line trimmed, right margin 0.97->0.89) + fonts 8.0/8.2/8.4 -> 8.6. Final: 438.0pt, factor 1.000, effective 8.60pt (meets the 8.5pt preferred). Vision re-check: no truncation, no collisions, '34.0 GB unchanged' complete.
- **FIG-A.1-01** [REJECT] (vis_DeepSeek-V4.1-Flash_b4.jso) — Vision-verified: single-series chart, all four bars the same orange, every bar carries its model name + value label + parameter annotation. Grayscale loses nothing; there is no color-only encoding. Placed floor also measured at 8.00pt.
- **FIG-1.1-01** [ACCEPT] (vis_MiMo-V2.6-Flash-RL_b0.json) — Figure label 'one K/V per step' -> 'per layer·head' (archify JSON + regenerate_ch1 chain). Containment measured: sublabel [147.9-230.2] inside orange box [127.7-250.5]; placed floor 8.17pt. NOTE: the longer 'one K/V per layer·head' was tried first and MEASURED to overflow the fixed-width box (vision + drawing-rect check), so the final label drops 'one ... per step' (implied by 'append' + token arrows; the caption carries the full 'one K/V per layer per head').

## Fixes applied beyond the review set (found while verifying)
- ch17:93 'superseded u-only screen' -> live comparison-row wording (same class as CH17-02).
- ch17:283 stray review id '(A-01)' removed.
- ch19:176 + ch19:302: two more 13.85-s revision-language leaks (sweep found them; reviewer missed).
- Fig 19.2 pre-existing clip: 4-line note last line ran off-canvas (x0=-4.5); fixed and re-measured.
- Splice artifact '** .' in ch19 self-caught and fixed before build.

## Figure floors after fixes (placed, 439.2pt column)
- Fig 1.1: 8.17pt (label changed, containment measured: sublabel inside orange box).
- Fig 19.2: 8.40pt (annotation moved; note clip fixed; zero out-of-page spans).
- Fig 19.3: 8.60pt (was 7.17 — below the 8pt hard floor; content narrowed + fonts 8.6).
- Fig A.1: 8.00pt (unchanged; issue rejected on color grounds anyway).