# Pass 25 — Adversarial Publication-Quality Review — SECOND HALF (PDF pages 156–307)

Scope: pages 156–307 of `from-token-to-fleet-v20260913.pdf` (307 pp., rendered and inspected per-figure at ~200–400 dpi). All 22 assigned figures were rendered to PNG and inspected visually + measured for ink extent / edge-clipping. Numeric and terminology items cross-checked against the PDF text layer. Figures are cited by PDF page (pymupdf index+1); printed book page noted where relevant.

Verdict scale: KEEP / POLISH / MAJOR REVISION / REDESIGN / REMOVE-MERGE. Severity: P0 critical · P1 major · P2 moderate · P3 minor.

---

# 1) OVERALL ASSESSMENT

The second half is in strong shape. The prior Review-pass-2 fix batch landed cleanly on the overwhelming majority of the previously-open items: every *visual* clipping/legibility/lay-out defect that was called out (Fig 13.1 path+STOP, 14.1 enlarge+deploy gate, 15.2 ILLUSTRATIVE×2, 16.1 x-axis, 17.1 three factors+counter-scenarios, 18.1 print-size, 19.1 four-state re-space, 21.1 stage names, 22.1 layout+warning, 23.1 green-box+6-vs-5, 24.1 simplify+feedback, 25.1 red-on-red, 26.1 grouped bars, 26.2 truncation, A.2 independent cards, A.4 scope-of-placement, Table 24-1 exploit-rate) is genuinely FIXED and verified on the rendered page. There is **no** remaining P0 (critical) defect in this slice. The figures read as professionally composed, mostly legible at print size, and no figure's content is clipped by a page margin.

However, the slice is **not yet publication-ready**, for two reasons. First, two *related* figures — Fig 19.2 and Fig 19.3 (Ch19 agentic KV growth) — contain a genuine internal **numeric inconsistency**: the token arithmetic they display ("I₀ + T·δ + T·γ; 9,200 + 800 + 65 per turn", "total = I₀+T·δ+T·γ") omits the `O_final = 300` base-output term that the book's own authoritative model (Ch17 §17.5.2, Ch19 §19.x) includes, and consequently that displayed arithmetic does **not** reproduce the KV values the figures themselves print (24.9 → 34.0 GB). This is a P1 defect in the manuscript's central agentic/capstone numbers. Second, Fig 20.1's fleet "scheduling overhead" factor was intended to be aligned to ρ ≈ 0.95/0.98 (as the book uses in Ch17 §17.5.2 and its worked example) but still reads "~90%" in both the legend and the caption — a NOT-FIXED cross-chapter inconsistency. A handful of P2/P3 polish items remain (two abbreviated/overlapping labels, a terminology drift on QPS vs rps in Ch20, and minor page-composition looseness).

Recommendation: one more focused pass limited to the Ch19 token/KV arithmetic reconciliation, the Fig 20.1 overhead factor, the Fig 26.2 "bandwd-bound" label, the Fig A.1 label overlap, and the Ch20 QPS wording. After those, the second half is publication-ready.

---

# 2) FIGURE-BY-FIGURE AUDIT

## Fig 13.1 — Reference-architecture escalation ladder (PDF p161, printed p143) — **KEEP**
- Prev-open: "horizontal escalation path + STOP-when-satisfied + triggers clear." Horizontal path: **CONFIRMED-FIXED** (Single GPU → Single host → Multi-host → Cluster/fleet, unambiguous right-arrows). STOP-when-satisfied state: **CONFIRMED-FIXED** (identical "constraints satisfied? STOP" box + green up-arrow at all four tiers).
- NEW P3 (a): the escalation/retention trigger labels ("outgrows 1 GPU / forces local", "KV overflows floor / privacy", "fleet demand / cost pressure") sit in the **gap between** tier boxes rather than on the arrow of the tier they feed, so the visual association with which tier's transition they trigger is ambiguous. Also the **Cluster/fleet** tier's up-arrow is **unlabelled** (no trigger). Recommend placing each trigger pair on its own tier's arrow, or at least labelling the terminal tier explicitly as "no further escalation."
- NEW P3 (b) page composition: the page has large top (between running head and heading) and bottom white space — the heading sits high, the figure floats mid-page, leaving an airy, unbalanced single-figure page (see §4).

## Fig 14.1 — Capability screen then deployment benchmark (PDF p167) — **POLISH**
- Prev-open "enlarged + final-gate-to-deploy clarity": **CONFIRMED-FIXED**. Legible; TCO+SLO gate exits via a distinct green arrow to "deployed".
- NEW P3: the model-selection pipeline is implied by vertical alignment, not drawn. The only explicit arrows are Candidate→Survivors→Selection (top lane) and gate→deployed. There is **no arrow** connecting Candidate models ↓ Capability screen ↑ Survivors ↓ Deployment bench ↑ Selection ↓ TCO+SLO gate. Recommend adding the two-lane connector arrows so the cascade (screen→bench→gate) is visually explicit rather than inferred. Severity is minor because the caption conveys the logic.

## Fig 15.1 — FlashAttention same math, far less HBM traffic (PDF p173) — **KEEP**
Both panels clean, no overlap, O(L²) vs O(L) claims explicit, colors (red before / green after) reinforce contrast. No clipping. Exceptionally clean.

## Fig 15.2 — Prefix caching vs batching (PDF p175) — **KEEP**
- Prev-open "ILLUSTRATIVE in both panels + enlarged": **CONFIRMED-FIXED** (brown [ILLUSTRATIVE] tag present in lower-right of BOTH panel (a) and panel (b)). Axes legible; no clipping. The [ILLUSTRATIVE] tag sits just above each bottom axis but is fully visible; panel (a) legend slightly overhangs the plot area without obscuring data — acceptable.

## Fig 16.1 — TCO break-even self-host vs managed API (PDF p189) — **KEEP**
- Prev-open "x-axis legible (prior CRITICAL landscape rewrite)": **CONFIRMED-FIXED**. X-axis label ("Requests/month (log)") centred, tick labels 1e4–1e8 fully visible, no truncation at either page margin. Y-axis 1e3–1e7 visible. All series/legend/annotations legible and non-overlapping. Log–log break-even chart is complete.

## Fig 17.1 — Sizing a fleet of one model (PDF p192) — **KEEP**
- Prev-open "shows three sizing factors (capacity / SLO headroom / failure tolerance) + counter-scenarios": **CONFIRMED-FIXED**. Per-host capacity (~2.0 req/s dashed bound) explicit; headroom above burst; N-1 residual (~6.0) failover tolerance explicit; counter-scenario "one host cannot meet the burst on its own" added. Burst ~5.5, N=4 ~8.0, N-1 ~6.0 all annotated. No clipping/overlap.

## Fig 18.1 — Model-routing decision tree (PDF p212) — **KEEP**
- Prev-open "marked print-sized": **CONFIRMED**. Print-sized and legible; cascade (Request → Capability filter → Cost/SLO gate → Fallthrough) and all six leaf model boxes + "yes→specialist / yes→general / fallthrough" clear; "only ONE model selected per request (early exit)" note present. No clipping/overlap.

## Fig 19.1 — Agent loop four-state state machine (PDF p215) — **KEEP**
- Prev-open "four-state re-spaced/rewritten (was overlap/clip P0)": **CONFIRMED-FIXED**. Plan/Execute/Observe/Decide cleanly separated with no overlap; dashed "loop (iterate)" back to Plan unambiguous; terminal outcomes Final answer (resolved) and Stopped (turn limit) distinct. States' italic tags inside boxes. No clipping. Minor: the curved Decide→Final-answer arrow passes under the dashed loop line in empty space — acceptable.

## Fig 19.2 — Tokens + KV growth across agent turns (PDF p220) — **MAJOR REVISION** (P1 numeric)
- Prev-open "contrast, tick clipping, gamma distinguishability, 24.9→27.2…34.0 GB": **CONFIRMED-FIXED on the visual axes** — tick labels legible/unclipped on both panels, series hatches distinguishable, displayed data labels 24.9/27.2/29.4/31.7/34.0 match the caption and are the correct Ch17 KV numbers.
- **NEW P1 (numeric inconsistency):** the figure caption and panel arithmetic present the token model as **"I₀ + T·δ + T·γ; 9,200 + 800 + 65 per turn"**, which **omits the `O_final = 300` base-output term**. With that omitted formula, single-shot = 9,200 tokens (→ 24.1 GB at 2.62 MB/token) and T=4 = 12,660 tokens (→ 33.2 GB) — **not** the 24.9 GB and 34.0 GB the figure itself prints. The displayed KV values reconcile only with the book's correct full model `I(T) = I₀ + T·(δ+γ) + O_final` (base 9,500 = 9,200+300; T=4 = 12,960 → 34.0 GB), which is what Ch17 §17.5.2 and Ch19 §19.x use. Location: Fig 19.2 caption + panel (a) component breakdown.
- Why it matters: the figure claims [DERIVED: Ch19 §3 arithmetic], but the arithmetic it shows does not derive its own data labels; a reader reconciling the numbers finds a contradiction (and the base prompt is labelled 9.2K while the KV-consistent base is 9,500).
- Recommended: add "+ O_final (300)" to the figure's formula/labels and correct the base prompt label to 9.5K (or explicitly note 9,200 input + 300 output), so displayed tokens reproduce 24.9→34.0 GB.

## Fig 19.3 — Agentic context accumulation (PDF p221) — **MAJOR REVISION** (P1 numeric)
- Prev-open "capstone REDESIGN, multi-label truncation fixed, decode-is-bandwidth-bound qualified, DERIVED label" — note: that prior item actually describes Fig 26.2; for Fig 19.3 the prior item was the KV-block growth + I₀/δ/γ distinguishability. Visual: **CONFIRMED-FIXED** — five stacks (Single-shot…Turn 4) labelled KV 24.9→34.0 GB, I₀/δ/γ blocks distinguishable, "~36%" growth note legible.
- **NEW P1 (numeric inconsistency, same root as 19.2):** the in-figure note reads **"canonical example @ 2.62 MB/token; total = I₀ + T·δ + T·γ"** and the caption says "initial prompt (9.2K tok)". This omitted `O_final = 300` means the stated total (9,200 + T·865) gives 12,660 tokens at T=4 → 33.2 GB, not the printed 34.0 GB; and the displayed 24.9 GB corresponds to a 9,500-token base, not the labelled 9.2K. 
- Recommended: state `total = I₀ + T·δ + T·γ + O_final`, with base 9,500 (9,200 input + 300 output) so the block arithmetic matches the printed KV.

## Fig 20.1 — Fleet capacity + offered-load utilization (PDF p234) — **POLISH** (P2)
- Prev-open "analytical-capacity terminology + DERIVED tag + overhead factor aligned (0.95/0.98 not 0.90) + no clipping": DERIVED tag: **CONFIRMED-FIXED** (brown "DERIVED [ILLUSTRATIVE]" in top panel). Terminology: bottom panel correctly says "Offered-load utilization (analytical bound, NOT GPU util)" — good. No clipping: confirmed.
- **NEW/NOT-FIXED (P2):** the scheduling-overhead line is still labelled **"with scheduling overhead (~90%)"** in the legend and the caption still says "with a ~90% scheduling-overhead line". This was intended to be aligned to ρ ≈ 0.95 / 0.98 but remains at ~90%. It is inconsistent with Ch17 §17.5.2 ("software LB achieves ρ ≈ 0.95 … hardware L7 ρ ≈ 0.98") and with the Ch17/Ch20 worked example. Recommend changing the figure legend + caption overhead factor to ≈0.95 (software LB) and reconciling with the ρ used in the provisioning arithmetic.
- Minor: annotation "≈29 hosts: 70% target (⌈40/(2.0×0.70)⌉ = 29)" checks out (28.57→29). The top-panel line at 2.0 req/s/host matches Ch17. Fine otherwise.

## Fig 21.1 — AI Factory promotion pipeline (PDF p239) — **KEEP**
- Prev-open "print-sized (stage-name clipping fixed)": **CONFIRMED-FIXED**. Data/Train/Eval/Canary/Observe/Promote/Serve fully inside boxes, centred, not clipped. All six gate conditions + "m✓ PASS" legible; FAIL rollback path explicit; production feedback loop clear.
- NEW P3: the six gate boxes are tightly spaced so adjacent gate borders essentially touch, and gate titles/metric text sit close to the gate-box top/bottom edges. No actual character overlap or border-touch, but slightly dense. Optional breathing room.

## Fig 22.1 — Prefill per request vs decode per token (PDF p246) — **KEEP**
- Prev-open "layout fixes": **CONFIRMED-FIXED**. Two panels properly aligned; red warning banner "LEFT: PER REQUEST | RIGHT: PER GENERATED TOKEN" + "DO NOT COMPARE Y-AXIS MAGNITUDES DIRECTLY" prominent and clear. X-axes/ticks legible, +17% @9.2K / +60% @32K / ~2.4× @128K annotations legible, decode "≈1.4e-4 PFLOP/token" correct (2N for a 70B model = 1.4e-4 PFLOP). No clipping/overlap.

## Fig 23.1 — Vague ask → architectural bounds (PDF p255) — **KEEP**
- Prev-open "green-box clipping fixed + six-vs-five gate framing reconciled": **CONFIRMED-FIXED**. Exactly five numbered orange steps (1–5) plus a separate unnumbered green "Quantified bounds → {TTFT, throughput, cost} budget" box — the previous six-vs-five ambiguity is resolved and the green box is fully contained with its text intact. No text touches borders.

## Fig 24.1 — Red Team / Green Team cycle (PDF p267) — **KEEP**
- Prev-open "simplify (move probe domains to caption) + strong feedback leg": **CONFIRMED-FIXED**. Nodes clean (1 Red Team → 2 Probes → 3 Exposure → 4 Guardrails → 5 Metrics → 6 Green Team) with no probe-domain list cluttering the diagram; the red feedback leg "findings from Green Team → next Red Team cycle" is heavy-weight and unambiguous. No clipping/overlap.

## Fig 25.1 — Architecture Decision Record (PDF p274) — **KEEP**
- Prev-open "red annotation on red loop": **CONFIRMED-FIXED**. The annotation ("consequences of one decision become the context of the next") is red text on white background, with the red dashed loop passing *behind* it — no red-on-red contrast failure. Context→Options→Decision→Rationale→Consequences + red dashed loop to Context all clear.
- Note: my initial ink-extent scan flagged a "BOTTOM edge-touch," but the full-page render confirms this is **only my figure-crop boundary cutting into the complete caption** below the diagram — the figure and the caption ("FIGURE 25.1: The Anatomy of an Architecture Decision Record [ILLUSTRATIVE conceptual]") are both fully on-page and untruncated. No real defect.

## Fig 26.1 — Workload fingerprints, grouped bars (PDF p280) — **KEEP**
- Prev-open "fingerprint grouped-bar redesign": **CONFIRMED-FIXED**. Six axes × three workload grouped bars on a common 0–1 normalised scale ("comparable 0-1 scale; bar height = intensity"), not a radar. Legend/group labels legible, "[ILLUSTRATIVE profiles — confirm against real telemetry]" subtitle present.
- NEW P3: the y-axis extends to ~1.1 though it is labelled "Normalised intensity (0-1)"; and the "comparable 0-1 scale" note is set in small grey type. Minor. (If no bar exceeds 1.0, tighten the axis to 1.0.)

## Fig 26.2 — Pattern Application Diagram (PDF p285) — **POLISH** (P2)
- Prev-open "capstone REDESIGN (multi-label truncation fixed) + unqualified decode-is-bandwidth-bound qualified + DERIVED label": multi-label truncation: **CONFIRMED-FIXED** (1·FACT, 2·DERIVED, 3·PATTERN fully legible; patterns A Inference Sharding / B Semantic Cache / C Circuit Breaker complete). DERIVED label: **CONFIRMED-FIXED** ("2 · DERIVED" headed). Feedback path (trace / validate / adjust+pick pattern / feedback) clear.
- **NEW/NOT-FIXED (P2):** the qualified-decode item is **not** done — the DERIVED node still reads **"sharding ⇒ bandwd-bound"** (an abbreviation of "bandwidth-bound") and is not qualified as *decode* bandwidth-bound. The caption qualifies it ("sharding → decode bandwidth-bound"), but the in-figure label does not. Recommend spelling out "decode bandwidth-bound" in the box (not "bandwd-bound").

## Fig A.1 — 2026 frontier MoE sparsity (PDF p287) — **POLISH** (P2)
- Data is correct: Kimi K3 = 2,800B total / 104B active = 3.7% (verified in the figure text layer; an earlier OCR read of "800B" was an OCR artifact). All four active-fraction labels (4.6/3.7/4.8/5.6%) and total/active breakdowns legible; disclaimer note present.
- **NEW P2:** on each bar the orange percentage label overlaps the grey total/active annotation to its right — e.g. "5.6%" sits over "320B total / 18B active", "4.8%" over "125B total / 6B active", "4.6%" over "284B total / 13B active". Still decipherable, but two text layers compete for the same horizontal space. Recommend offsetting the % label above the bar or right-aligning the breakdowns.

## Fig A.2 — Vendor-reported KV/FLOP reduction (PDF p291) — **KEEP**
- Prev-open "REDESIGN (independent before-after cards, no shared bar scale)": **CONFIRMED-FIXED**. Three self-contained cards (DeepSeek V4-Flash vs V3.2, DeepSeek V4-Pro vs V3.2, GLM-5.3-Flash vs stated ref), each with its own 100%→~X% and no shared bar scale; the "EACH PANEL IS A DIFFERENT BASELINE — NOT A SHARED SCALE. Do not compare cards." warning is prominent/red/uppercase. All percentages (~7/~10/~23/~27/~33%) legible, no clipping/border-touch.

## Fig A.3 — Conceptual layering of frontier AI systems (PDF p294) — **KEEP**
Nine era bars (Transformer ~2017 → Agent Fleet ~2026) legible; legend (Efficiency-led dashed / Capability-led solid / Fleet thick) clear; caption explains the spine. No clipping/overlap. NEW P3: the progression of "one model → whole system" is conveyed only by vertical stacking + caption; there is no explicit directional arrow. Optional.

## Fig A.4 — Where should intelligence live? (PDF p295) — **KEEP**
- Prev-open "vertical axis equals scope-of-placement (not superiority)": **CONFIRMED-FIXED**. Red left arrow explicitly labelled "scope of placement … (vertical axis = WHERE it lives, not BETTER/HIGHER)". Eight layers bottom→top (Inside weights … Across a fleet of specialised models) with chapter cross-refs (Ch3/Ch8 … Ch18/Ch20) all legible; "Model intelligence ≠ system intelligence" note clear. No clipping/overlap.

---

# 3) CONCEPTUAL / TERMINOLOGY / NUMERICAL FINDINGS

- **P1 — Fig 19.2/19.3 token arithmetic inconsistency (Ch19).** The displayed KV values (24.9→34.0 GB) reconcile only with `I(T) = I₀ + T·δ + T·γ + O_final` (base 9,500 = 9,200+300; T=4 = 12,960 → 34.0 GB), which is exactly the model Ch17 §17.5.2 (line "I(T) = I0 + T·δ + T·γ + Ofinal") and Ch19 (line "Total(T) = (I0 + T·δ + T·γ) + Ofinal") use. But the Fig 19.2 caption ("I₀ + T·δ + T·γ; 9,200 + 800 + 65 per turn") and Fig 19.3 in-figure note ("total = I₀ + T·δ + T·γ") omit `O_final`. The figures' own stated arithmetic therefore does not reproduce the numbers they print. Fix the figure formulas/labels to include "+O_final (300)" and correct the base-prompt label to 9.5K.
- **P2 — Fig 20.1 overhead factor = ~90% (Ch17 cross-chapter).** Ch17 §17.5.2 gives ρ ≈ 0.95 (software LB) / 0.98 (hardware L7) and the worked examples use ρ = 0.95. Fig 20.1's legend and caption still use "~90%". Reconcile to ρ ≈ 0.95/0.98 (or explicitly define "scheduling overhead" as a distinct factor with its own stated value and justify 0.90).
- **P2 — Ch20 "QPS" vs book-canonical "rps/req·s⁻¹".** The book's rate unit is rps / req·s⁻¹ (used throughout Ch17–Ch19, glossary, and figures 17.1/20.1). But Ch20 §20.4–20.6 and the §20.9 mini-case use "QPS" heavily (e.g. "per-host QPS = Q", "Aggregate QPS", "marginal cost per QPS"). Note: Ch20 also *warns* against reducing throughput to a QPS constant, so the usage is partly rhetorical, but the term still drifts from the rest of the book. Recommend harmonising to rps (or explicitly noting QPS = rps for this date section).
- **P2/P3 — Fig A.1 label overlap** (see §2): orange % labels overlap grey total/active annotations.
- **P3 — Ch20 §20.9 mini-case illustrative "250 QPS per host / 2,000 QPS fleet."** This is ~125× the book's canonical per-host bound (~2.0 req/s) and is flagged only as "[ILLUSTRATIVE]". The table/server of the original exercise was retained deliberately ("kept [ILLUSTRATIVE]"), but the magnitude is far enough from the canonical ~2.0 req/s that it risks confusion. Consider re-labelling the illustrative numbers or replacing them with the canonical ~2.0 req/s geometry.
- **CONSISTENT — host/node/instance terminology.** Verified consistent across the slice: "host" = compute/machine, "GPU instance" = rented cloud instance, "model instance" = a model replica. No drift.
- **CONSISTENT — Table 24-1.** Renamed to "Tool-use exploit rate" with definition "percentage of Red Team tool-use probes that achieve an unintended action (an attacker-side success; lower is better), < 0.5%". Confirmed renamed with correct lower-is-better direction. (Adjacent guardrail-intervention row and the separate "false-positive / correlated success rates" discussion are distinct and fine.)

---

# 4) TABLE / PAGE-COMPOSITION FINDINGS

- **P3 — Fig 13.1 page (p161) vertical composition.** Large top and bottom white space leaves a stranded-looking heading high on the page and a floating figure; the single-figure page reads airy. Consider rebalancing or allowing text to share the page.
- **P3 — Fig 21.1 gate-row density.** Six gate boxes nearly touching horizontally, with gate titles and two-line metric conditions hugging the box edges. No actual overlap, but tighter than ideal.
- **P3 — Fig 26.1 y-axis to ~1.1 despite a "0-1" scale**; small-grey "comparable 0-1 scale" note.
- **P3 — Fig A.3** no explicit progression arrow (implied by stacking).
- No widows/orphans, stranded headings other than the 13.1 note, split tables, caption-figure separations, or equations overflowing columns were found in this slice; captions sit directly beneath their figures throughout.
- Tables in the slice (Table 19-1, Table 20-x, Table 24-1) are well-formed; column alignment/units/significant digits consistent with prose.

---

# 5) CROSS-FIGURE SYSTEMIC ISSUES

- **Overhead/efficiency-factor inconsistency across figures vs text.** Fig 20.1 uses ~90% scheduling overhead, while Ch17 §17.5.2 and the worked examples use ρ ≈ 0.95/0.98. Figs 17.1 and 20.1 both use the ~2.0 req/s/host analytical bound (consistent); the discrepancy is only the applied overhead factor. Recommend defining one ρ for LB/scheduling and using it consistently in the capacity figures and captions.
- **Token-model consistency between figures and the authoritative formula.** The one systemic theme in this slice: Fig 19.2/19.3 present a token model that omits `O_final`, while Ch17/Ch19 text uses the full model. Everywhere else (Fig 22.1, and the ~9,500 token / ~3.7 req/s / ~2.0 req/s family in Ch17/Ch20) the numbers are consistent with the full model. This is the single place the visual and the prose diverge.
- **Per-host request-rate bound consistency.** ~2.0 req/s appears consistently in Figs 17.1 and 20.1 and in Ch17/Ch20 prose; and the "this is an analytical bound, NOT measured throughput" qualification is present in both Fig 20.1's and Ch20's wording — good, and this is the honest framing the book's standard demands.
- **Illustrative/derived tagging discipline.** [ILLUSTRATIVE]/[DERIVED]/[1P] tags are used consistently across figures and captions; the capstone Fig 26.2 and Ch20 mini-case appropriately scope their illustrative numbers. No figure presents a manufactured benchmark as measured data.

---

# 6) FINAL RISK ASSESSMENT

The slice is **not fully publication-ready**; it needs one more targeted pass.

Strongest remaining risks:
1. **Ch19 agentic token/KV arithmetic** (Fig 19.2 + Fig 19.3, P1): figure-presented token formulas omit `O_final=300`, so they don't reproduce the figures' own 24.9→34.0 GB. This is the most likely place a careful reader (or reviewer) finds a verifiable internal contradiction, and Ch19's agentic capacity conclusion flows directly from these numbers. Must be reconciled before publish.
2. **Fig 20.1 overhead factor (~90% vs ρ≈0.95/0.98)** — a cross-chapter (Ch17 vs Ch20) numeric/terminology mismatch on a fleet-capacity figure.
3. **Fig 26.2 "bandwd-bound" abbreviation / lack of decode qualification.**
4. **Fig A.1 percentage/total label overlap.**
5. **Ch20 QPS vs rps terminology drift.**

Recommend another review pass specifically on: Ch19 §3 arithmetic + Figs 19.2/19.3; the Ch17/Ch20 ρ (overhead) factor and Fig 20.1; Fig 26.2 DERIVED box wording; Fig A.1 label layout; and Ch20 §20.4–20.9 terminology. The remaining P3 page-composition items (13.1 white space, 21.1 gate density) are optional polish.

What is genuinely excellent: the previously-fixed figure set (13.1, 14.1, 15.2, 16.1, 17.1, 18.1, 19.1, 21.1, 22.1, 23.1, 24.1, 25.1, 26.1, A.2, A.4) is now clean, legible, and well-composed; Table 24-1's exploit-rate rename is correct; the "analytical bound, not GPU util / not measured throughput" qualification discipline on the fleet figures is a strong feature. With the Ch19 arithmetic and Fig 20.1/26.2/A.1 items resolved, the second half will be publication-ready.
