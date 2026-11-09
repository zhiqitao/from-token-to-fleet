# Round 3 — Vision disposition ledger (116 issues, 33/33 batches, 84-page manifest;
# +1 = MiMo b0 refill item FIG-1.1-1.2-COLOR-SEMANTICS, dispositioned after the 104-item pass)

Method: deterministic adjudication first (PDF span font scan, source-string grep,
pixel measurement, generator arithmetic), vision_analyze on rendered 200dpi pages
for geometry claims, independent re-verification before every fix.
Panel: MiMo-V2.6-Flash-RL / DeepSeek-V4.1-Flash / Qwen3.8-27B.

## P1 (10 findings → 7 fixes / 3 rejects)

FIXED:
- Fig 11.1 caption row-entity + left/right (3-model consensus) — ch11 caption rewritten.
- Fig 18.1 spurious 'no' on Request→Capability entry — generator label skip (arrow kept).
- Fig 25.1 ADR-001 '(current)' → '(superseded)'.
- Fig 26.2 DERIVED box stripped of post-pattern content.
- ch1 caption append-timing sentence.
- ch8 GB200 5,000→4,500 TFLOPS / 312→281 FLOP/byte / ridge direction (Qwen caught
  Round-2 verification error; three sources agree on B200 = 2,250 dense).
- ch15 8.75×→8.2× ×2 (70,000/8,500; 3-model consensus).

REJECTED:
- Fig 2.2 double-P1: quoted '~0.2K' does not exist; actual caption = ~9.2K right of
  ~295 ridge; markers on/below roofline by design (in-plot note states it).
- Fig 11.1-02: 'four equal-length sequences' — sequences unequal by design.

## P2 (44 findings)

FIXED:
- KV-35GB-TOKEN-COUNT: ch11 Note 13,000×2.62=34.06≠35 → ≈13.3K aligned to §9.8.
- SPELL/SPECIALISATION: fig 11.2 label + ch11 caption → US -ization (book-wide).
- FIG-10.1-01: 'on-node only' → 'on-node in the canonical config'.
- FIG-10.1-02 (+P3 LINEAR dup): 'scales linearly' → '…until a shared resource binds'.
- FIG-10.1-03: caption 'each panel names what is replicated' → replication-where-exists.
- FIG-15.1-01: 'naive / SDPA' → 'naive (materialized)' + caption; banner adds
  last-bit rounding caveat (P3 same-result merged).
- FIG-15.1-02: O(L²) note now names the L×L intermediate write.
- FIG-19.2-01: subtitle 'illustrative model' → 'bounding case' (matches [DERIVED] cap).
- FIG-13.1-03: 'orthogonal levels' → 'distinct levels … not a quality ranking'.
- FIG-13.1-01: DE-ESCALATE green → blue #1a6fa8 (distinct from STOP green).
- FIG-13.1-2: ch13 caption triggers → 'demand, KV residency, or goodput' (match drawn).
- FIG-9.1-01: subtitle now states 245 GB sent at 1.75× (times use sent bytes).
- FIG-26.1-01: axis 'Normalized intensity' → 'Authored intensity' (caption denies rescale).
- FIG-12.1-01: 'SURVIVORS' → 'CLEARS CAPACITY GATE' (caption = conditional).
- FIG-20.1-01: S solid zorder=5 covered equal-valued C_eff → S now dotted (both visible).
- FIG-20.1-1 (MODERATE): 'delivers ≈41.5 rps' → analytical capacity C_analytic(21).
- FIG-11.2-01: 'four orthogonal concerns' → 'four separable concerns (they interact…)'.
- FIG-9.3-01: setup rails bypassed ProcessGroup → redirected to layer-1 boxes
  (rendezvous/communicator IDs terminate at the framework backend).
- FIG-A3-01: fig A.4 blue/green families → 'blue = where the system runs · green = …'.
- FIG-3.4-01 (MAJOR): swatch legends ≠ box sums (grey 94 vs 6×11.4=68.4; orange 25.6
  vs 2×11.4=22.8 + unit mix) → swatches match boxes; ledger totals moved to plain text.
- FIG-1.1-02: ch1 xref 'cross-layer accumulation in Fig 2.1' → 'cache persists across
  the whole loop' (fig 2.1 KV box = conceptual).
- FIG-1.2-01: Attention sublabel → 'computes Q, K, V for this token'.
- FIG-5.1-01 was REJECTED (selection scope); FIG-5.1-02 fixed (KV → KV cache, P3).
- FIG-11.4-01 (P3): italic summary adds 'correctness' to match gate box.
- FIG-17.1-01 font: fig 17.1 annotations 7.6pt → 8.6pt (only sub-8pt figure page).

REJECTED:
- FIG-11.1-DISCRETE-VARIANCE: pixel measure = 70/102/58/26 px blue runs — unequal.
- FIG-11.3-01: 'the split is the same' = 50/50 partition ratio (true as drawn).
- FIG-14.1-01: label = 'MMLU/GSM8K' (vision dropped an M; (?<!M)MLU = 0 matches).
- FIG-2.2-02: capacity conclusion lives in the two-conclusion paragraph; in-plot note
  covers marker-below-roof.
- FIG-15.2-01 ×2: R27 already fixed the plateau overclaim; curve range ends before
  saturation; annotation says 'gain flattens', not plateau.
- FIG-16-1: prose accurate — star (be_mid) + horizontal span (be_lo→be_hi) + end caps
  all exist in generator.
- FIG-17-1: brace spans 5.5→8.0 with tick at 6.0 (the 0.5 margin = tick's lower span).
- FIG-17-2: generator has exactly ONE axhspan (green 6.0–8.0 data zone); no pink/blue
  label-background bands exist.
- FIG-18.1-01 ×2 (P2+MODERATE): already fixed earlier today (entry-edge 'no' removed).
- FIG-19.3-01: per-bar subtitle lines name each policy's moved quantity; identical
  34.0 bars = the documented finding ('request's own context unchanged').
- FIG-21.1-01: gates drawn at seam x with red seam ticks + vertical connectors.
- FIG-22.1-01: annotation xy = (Lstar_c, causal total) = quad/2-overtakes-lin point;
  causal-total vs full-total never intersect.
- FIG-2.1-01: vision p35 — read connector has a clear arrowhead; all destinations arrowed.
- FIG-2.1-02: init path carries its own 'initialize' text label (color redundant).
- FIG-5.1-01: figure models selection surfaces, not the data path (legs = selection scope).
- FIG-6.2-01: p99=1.33 = sample boundary; top-1% stragglers at 5s beyond it — both true.
- FIG-7.5-01/FIG-7.6-01/FIG-1.1-03/1.2-03/2.1-03/2.2-03/6.2-02/13.1-02/16.1-01:
  font claims refuted by 84-page span scan (≥8pt) — only p283 (7.6pt, fixed) and
  p208 (footnote refs/superscript + pinned-revision SHA citations, conventional
  footnote typography) were below 8pt.
- FIG-8.1-01: figure title declares mixed compute+movement scope; role label =
  'arithmetic units'; arrows occupy inter-level gaps only.
- FIG-8.2-01: generator documents H100 solid+'o' vs H200 dashed+'^' (grayscale-safe).
- FIG-11.4-02: both gate lines use '|' exclusively; no ';' present.
- FIG-11.3-FABRIC-RATE-LABEL: rates sit under domain titles A/B; Note 11.3-1 carries
  the evidence scope (the finding concedes Note is correct).
- p208 class: SHA strings = pinned-revision footnote citations (deliberate, ch5/11/27);
  6.0pt digits = footnote reference superscripts.

## P3 (55 findings) — fixes

- FIG-10.1-04: bubble label → '— pipeline-wide'.
- FIG-10.1-05: weight-delivery arrows ORAN_E → BLUE_E (orange = GPU per key).
- FIG-10.1-CANON: caption adds '(GPU counts schematic)'.
- FIG-10.1-LINEAR: merged into 10.1-02 fix.
- FIG-13.1-1: DE-ESCALATE label → 'privacy · sovereignty · cost' (3 criteria).
- FIG-12.1-02: 'each needs a ~5-host prefill pool' → '~5 hosts of prefill capacity'.
- FIG-24.1-01: caption loop now starts 'red team → probe → …'.
- FIG-A1-01: callout 'Each figure' → 'Each row' (matches caption).
- FIG-A2-01: legend row 1 explains darker effcap shade (MoE transition ~2022).
- FIG-A4-01 (book A.5): 2705 SVG 'core pass N' → 'pass N' ×3 (top/bottom/caption align).
- FIG-18.1-02/MINOR: caption 'general' → 'general-purpose' (leaf 'General' collision).
- FIG-19.1-01: caption 2.62 MB/token adds '(FP16)'.
- FIG-19.1-1: figure title 'four-state state machine' → 'four-state machine' (= caption).
- FIG-1.1-1: caption 'every decoded token' → 'every token' (token1 = prefill-sampled).
- FIG-1.2-02: tag 'ordered' → 'order = position'.
- FIG-7.5-1: legend GQA FP8 ~0.17 → ~0.16 MB/tok (0.33/2 = 0.164).
- FIG-5.1-02: surfaces 'KV' → 'KV cache'.
- FIG-8.1-02: interconnect role 'host / multi-GPU' → 'GPU↔GPU and host links'.
- FIG-9.3-02: legend 'Payload / device execution' → 'Payload / execution (device or host)'.
- FIG-9.3-03: 'Legacy plugin: MPI or OFI' → 'Plugin: MPI or OFI'.
- FIG-11.4-03: 'Serving engine' → 'Serving stack' ×3 (SVG) + ch11 caption aligned.
- FIG-16.1-02: managed base line solid → dashed (grayscale vs self-host solid).
- FIG-17.1-01 (notation): figure 'rho=1'/'5.5-rps' → 'ρ = 1'/'5.5 req/s' (9 lines,
  rendered strings only) — matches caption notation.
- FIG-1.1-1.2-COLOR-SEMANTICS (P3, b0 refill): fill-color meanings shift between
  fig 1.1 and fig 1.2 (green/orange/blue differ; purple consistent; boxes all titled,  so no meaning is lost — model's own concession) → fig 1.2 caption now declares
  color figure-local decoration.
- FIG-11.2-02: merged into SPELL fix.
- FIG-15.1-01 (P3 same-result): merged into banner caveat fix.

## P3 — rejects

- FIG-15.2-02: caption already declares [ILLUSTRATIVE][ASSUMPTION] synthetic curves;
  floor = illustrative, not a canonical-workload claim.
- FIG-15.2-03: annotation placement documented as reviewed; 150dpi clearance artifact.
- FIG-16.1-01: finding self-flags 'most likely a resolution artifact'; elements exist.
- FIG-17-3: already satisfied (7.6→8.6 this round).
- FIG-17.1-02: both bounding lines (6.0 / 8.0) carry their own labels.
- FIG-19.2-1: hatches = I0 '//' / δ '...' / γ 'xx' — three distinct patterns.
- FIG-21.1-02: loop labeled 'production feedback → data / evaluation (each cycle re-gated)'.
- FIG-23.1-01: 'success' gate carries the quality bar; caption's six = Table 23-1 columns.
- FIG-26.2-02/03/04: 02/03 already fixed earlier today; 04 = caption covers breaker idle.
- FIG-3.4-02: source = ONE KV bar naming both models + note lines (measured widths).
- FIG-8.3-01: every box carries its own active/resident text label (color redundant);
  source = 1:1 transcription of approved hand-drawn raster.
- FIG-11.4-02: see P2 rejects (all pipes).
- FIG-6.2-02: rotated labels ≥8pt (span scan).
- FIG-13.1-02: source fontsize=8.0 ≥ 8pt floor.
- FIG-14.1-01: see P2 (MMLU).
- FIG-16-1/FIG16-1: see P2 (elements exist).
- FIG-18.1-1/MODERATE + MINOR: fixed earlier today / merged into 18.1-02.
- FIG-19-1: merged into 19.1-1 fix.
- FIG-20.1-1/MODERATE: fixed (41.5).
- FIG-2.2-2: '0.980' absent book-wide (vision misread of 0.989).
- FIG-11.1-DISCRETE: see P2 (pixels).
- FIG-11.3-01/02/FABRIC: see P2.
- FIG-11.4-01: fixed (correctness).
- FIG-12.1-01/02: fixed.
- FIG-13.1-1/03: fixed.
- FIG-15.2-1: dup of 15.2-01 (reject).
- FIG17-1/2: see P2.
- FIG-19.3-01: see P2.
- FIG-20.1-01: fixed (S dotted).
- FIG-7.7-01: ticks drawn at k×24.9 GB = exactly the 17 request-slot boundaries;
  they encode slots by design, not 80GB ranks.
- FIG-11.4-02: all-pipe separators.

## Totals (vision)

Severity split as parsed: 10 P1 / 44 P2 / 55 P3 / 6 nonstandard
(1 MAJOR → P2, 2 MODERATE → P2, 3 MINOR → P3) = 115.
Effective: P1 = 10, P2 = 47, P3 = 58.

- P1: 10 → 7 fixes / 3 rejects
- P2 (47, incl. MAJOR + 2 MODERATE): 24 fixes / 23 rejects
- P3 (58, incl. 3 MINOR): 29 fixes / 29 rejects
- Grand: 116 → **61 fixes / 55 rejects** (3 sibling items merged into a paired fix,
  counted once on the fix side; +1 = b0 refill P3 color-semantics → caption note).
- Note: MiMo vision fill log showed '-> 30 chars' for b0/b3; final files = 1992 chars
  (1 issue) and 626 chars ('[]' + coverage note) — valid, no data loss.

## Tooling fixes discovered this round
- render/regenerate_ch1_token_travel.py: archify path /home/ubuntu/tools →
  /home/ubuntu/projects/tools; bare 'chromium' → 'chromium-browser'.
- regenerate_ch1.py covers fig 1.1 only; fig 1.2 has its own exporter.