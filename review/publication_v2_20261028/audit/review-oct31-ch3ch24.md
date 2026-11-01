# Review fix evidence — 2026-10-31 Publishing Readiness Review (P2-01 / P2-02 / P2-03)

来源评审：`Publishing_Readiness_Review_2026-10-31`（native-inputs/24d592f9…/doc_8bf82ad24fd9_…md）。
范围：仅 `design/manuscript/chapter-03/chapter-03.md`、`design/manuscript/chapter-24/chapter-24.md` + 本证据文件。未改动其他章节、渲染器、根文件；未做全书构建/git 提交/委派。

## SHA-256（before → after）

| 文件 | before | after |
|---|---|---|
| chapter-03/chapter-03.md | `3f3eff24793d054c78ade4d5f1739d518888d97530ba4159280189c5916a51ec` | `55ec2184746bc71e1476108c3da27b495ec5d3f0a0101f73b173a856a7d4025f` |
| chapter-24/chapter-24.md | `0a0eef8815d03de90badf08980c6ea9d8d4e737582089e9dda3f597a6687b0fa` | `260bc93bfef0a46ead779d73387965785291202f9407b62f2d3d647d50d19eb0` |

before 备份：`cache/scratch/chapter-03.before.md`、`cache/scratch/chapter-24.before.md`。

---

## P2-01 — Ch3 MoE active-parameter worked example（FIXED）

**编辑前声明的输入（Table 3-2 首行，未改）**：~47B total = 8 × 5.7B = 45.6B routed + ~1.4B always-on。

**独立重算（Python，先于编辑）**：
```
active      = 2 × 5.7 + 1.4 = 12.8 B
active/total= 12.8 / 47      = 27.234 %   → 27.23%
expert-FFN alone = 11.4 / 47 = 24.255 %   → ~24%
FP16 active = 12.8 × 2 B     = 25.6 GB
2N FLOPs    = 12.8 × 2       = 25.6 GFLOP = 0.0256 T
ratio vs 70B= 25.6 / 140     = 0.182857   → 0.183×
1/ratio     = 140 / 12.8     = 5.469      → ~5.5×
```
与评审所列 27.23% / 25.6 GB / 25.6 GFLOP / 0.183× 完全一致。原 14B 无法由 45.6B+1.4B 拆分导出（14/47=29.79%、14×2=28、28/140=0.20），确认为不一致，采用评审建议的透明方案：**~47B total；45.6B routed + 1.4B shared；12.8B active**，全部相关量随之重算。

**改动（chapter-03，23 处替换，全部精确匹配断言 count==1）**：
- Table 3-2 标题：active fraction ~25–30% → **~24–27%**。
- Table 3-2 五行：active **~14B→~12.8B**（推导改为 2×5.7B+1.4B=12.8B，~30%→~27%，~25%→~24%）；active/total **~30%→~27%**（29.8%→**27.23%**，区间 25–30%→24–27%）；FP16 **~28 GB→~25.6 GB**；FLOPs **~0.028T→~0.0256T**（28B→25.6B）；ratio **~0.20×(~5×)→~0.183×(~5.5×)**（28→25.6 GFLOP）。
- 正文 §"Why MoE saves compute"：n_a=14→12.8B；14/47≈30%→12.8/47≈27%；公式 14B×2≈0.028T→12.8B×2≈0.0256T；0.028/0.14≈0.20×→0.0256/0.14≈0.183×；5× reduction→**5.5×**（0.183 的倒数 5.47，属 0.183× 的派生量，随改以保持内部一致）。
- KV bullet：14B of 47B → 12.8B of 47B。
- Boxed rule：~14B active / ~28 GB → ~12.8B / ~25.6 GB。
- §6 Architecture Consequence：~14B active、~28 GB → ~12.8B、~25.6 GB。
- Mini-case：~14B active、~28 GB → ~12.8B、~25.6 GB。
- **Fig 3.4 note**：active-compute fraction (~100% vs ~30%) → (**~100% vs ~27%**)；caption：top-2 (~14B)/28 GB → top-2 experts plus always-on (**~12.8B**)/(**≈25.6 GB**)。
- **Table 3-3** 五行：~14B→~12.8B（推导补全 2/8=25% of expert mass ≈11.4B + 1.4B = 12.8B）；~30%/29.8%→~27%/27.23%；~28 GB→~25.6 GB；~0.028T→~0.0256T；~0.20×(~5×)→~0.183×(~5.5×)。

**保留未动**：total ~47B/45.6B/1.4B 行、94 GB residency、KV ~12 GB、dense 70B 全部数字、Wan2.2 A14B 官方 ~27B/~14B（ch3 L174/176、ch27 L243 —— 另一模型的发布计数，非本例拆分，且 ch27 不在范围）。[ILLUSTRATIVE]/[DERIVED]/[ASSUMPTION] 标签计数 before/after 相同（ch3 18/18）。

**验证（编辑后扫描 chapter-03）**：`~14B`、`14B ÷`、`29.8`、`0.028`、`0.20×`、`28 GB`、`~30%`、`≈ 30` 残留 = 0 行；`~5×`/`**5×` 残留 = 0（"5.5× less" 含子串 "5× less"，为误报，L95/L220 已核实为 ~0.183× (~5.5× less)）。Wan2.2 行含 "approximately/about 14B active" = True（按预期保留）。

---

## P2-02 — Ch24 "minimum exposure"（FIXED）

**编辑前**（§24.3.2, L76）："…flag it as the *minimum* exposure, not an estimate of the true value."
**编辑后**："…we flag it as a **uniform-sampling null reference, not a bound** — neither a floor nor a ceiling on real exposure." + 两行反例：(a) 与毒化块不相交的无关查询 → exposure near zero（Q 再大也一样）；(b) 高相似度毒化内容 → top-k 命中远超语料占比，exposure elevated well above 52。+ 度量须 conditioned on query distribution / ranking / chunk provenance / attack success。
p=50/48,000、k=5、Q=10,000、52 等数字全部保留；[ILLUSTRATIVE][DERIVED] 标签保留。`minimum` 在 chapter-24 残留 = 0 行。

---

## P2-03 — Ch24 PIES 顺序敏感（FIXED，采用"order-sensitive heuristic"方案）

未提供 canonical generation order/normalization/representative/tie-break（文本中不存在该规范，无法凭空补写），故按评审二选一，明确称 PIES 为 **order-sensitive heuristic**：
- §24.3.1 定义（L46）："This deterministic clustering rule … is what makes the count well-defined" → "This **greedy** clustering rule … is an explicitly **order-sensitive heuristic**, not a deterministic cross-run class count"，并给出非传递性说明（A~B、B~C 但 A̸~C）与三个敏感源（generation order / representative / tie-break）；补列缺失的规范项（canonical order、normalization denominator、representative rule、stable sort、tie-break、test fixture），说明 count 仅在单次固定运行内 well-defined。
- L57：217 不可复现的原因补入 "the greedy assignment is order-sensitive (generation order, representative selection, and tie-break are unspecified)"。
- L59："PIES is a reproducible operational proxy" → "PIES is an **order-sensitive operational heuristic** — not a deterministic cross-run class count"。
- Mini-case L156：217→143 跨轮比较加注 "(both values from the same order-sensitive dedup heuristic, compared under a fixed generation order — §3.1)"。
217、143、768、NLE≤0.25 等数字全部保留；[ILLUSTRATIVE]/[DERIVED] 标签计数 before/after 相同（ch24 5/5）。`deterministic clustering`、`reproducible operational proxy` 残留 = 0 行。

---

## Diff（before → after，unified，-U1）

```diff
--- a/design/manuscript/chapter-03/chapter-03.md
+++ b/design/manuscript/chapter-03/chapter-03.md
@@ -85,3 +85,3 @@
 
-**Table 3-2 — MoE model parameter arithmetic (worked example, not reference). The active fraction for top-2-of-8 routing is ~25–30% of total, not single-digit. Note the contrast with the 2026 frontier models in Appendix A, where active fractions do fall to a few percent (Qwen 6B/125B, Kimi 104B/2.8T) because those use extreme expert sparsity plus shared/offloadable parameters.**
+**Table 3-2 — MoE model parameter arithmetic (worked example, not reference). The active fraction for top-2-of-8 routing is ~24–27% of total, not single-digit. Note the contrast with the 2026 frontier models in Appendix A, where active fractions do fall to a few percent (Qwen 6B/125B, Kimi 104B/2.8T) because those use extreme expert sparsity plus shared/offloadable parameters.**
 
@@ -90,7 +90,7 @@
 | Total parameters (across 8 experts) | ~47B | ~5.7B per expert × 8 ≈ 45.6B + always-on attention/shared + embeddings ≈ 47B (per-expert rounded to ~6B) [ILLUSTRATIVE][DERIVED] |
-| Active parameters per token (top-2 routing) | ~14B | 2 routed FFN experts + always-on attention/shared weights ≈ 14B (~30% of the ~47B total; ~25% counting expert-FFN mass alone) [ILLUSTRATIVE][DERIVED] |
-| Active/total fraction | ~30% | 14B ÷ 47B ≈ 29.8% (≈25–30% for top-2-from-8) [ILLUSTRATIVE][DERIVED] |
-| FP16 active weight-read per token | ~28 GB | 14B × 2 bytes = 28 GB read per token (compute/bandwidth; does NOT set residency) [ILLUSTRATIVE][DERIVED] |
-| FLOPs per forward pass (approx.) | ~0.028T | 14B active × 2 FLOP/param = 28B [ILLUSTRATIVE][DERIVED] |
-| Compute ratio vs dense 70B | ~0.20× (~5× less) | (14B × 2) ÷ (70B × 2) = 28 GFLOP ÷ 140 GFLOP [ILLUSTRATIVE][DERIVED] |
+| Active parameters per token (top-2 routing) | ~12.8B | 2 × 5.7B routed experts + ~1.4B always-on attention/shared = 12.8B (~27% of the ~47B total; ~24% counting expert-FFN mass alone) [ILLUSTRATIVE][DERIVED] |
+| Active/total fraction | ~27% | 12.8B ÷ 47B ≈ 27.23% (≈24–27% for top-2-from-8) [ILLUSTRATIVE][DERIVED] |
+| FP16 active weight-read per token | ~25.6 GB | 12.8B × 2 bytes = 25.6 GB read per token (compute/bandwidth; does NOT set residency) [ILLUSTRATIVE][DERIVED] |
+| FLOPs per forward pass (approx.) | ~0.0256T | 12.8B active × 2 FLOP/param = 25.6B [ILLUSTRATIVE][DERIVED] |
+| Compute ratio vs dense 70B | ~0.183× (~5.5× less) | (12.8B × 2) ÷ (70B × 2) = 25.6 GFLOP ÷ 140 GFLOP [ILLUSTRATIVE][DERIVED] |
 
@@ -98,9 +98,9 @@
 
-The compute savings are straightforward: if only $n_a = 14$B of $n_t = 47$B total parameters are active per token, the FLOP count drops by the active fraction relative to a *same-size dense* model. But note the active fraction for top-2-of-8 routing is ~$14/47 \approx 30\%$, not single-digit — so the relative saving is about 5× versus the canonical 70B *dense* comparison, not 20× or 30×. Concretely,
+The compute savings are straightforward: if only $n_a = 12.8$B of $n_t = 47$B total parameters are active per token, the FLOP count drops by the active fraction relative to a *same-size dense* model. But note the active fraction for top-2-of-8 routing is ~$12.8/47 \approx 27\%$, not single-digit — so the relative saving is about 5.5× versus the canonical 70B *dense* comparison, not 20× or 30×. Concretely,
 
 $$
-\text{FLOP}_{\text{MoE/token}} = n_a \times 2 \text{ FLOP/param} = 14\text{ B} \times 2 \approx 0.028\text{ T}
+\text{FLOP}_{\text{MoE/token}} = n_a \times 2 \text{ FLOP/param} = 12.8\text{ B} \times 2 \approx 0.0256\text{ T}
 $$
 
-which is $0.028/0.14 \approx 0.20\times$ of the dense 70B figure — roughly a **5× reduction** in compute per token. (It is also $14/47 \approx 30\%$ of a hypothetical dense model of the *same* 47B total; the 5× figure uses the book's canonical 70B dense as the comparison, so always state which baseline the ratio is against.)
+which is $0.0256/0.14 \approx 0.183\times$ of the dense 70B figure — roughly a **5.5× reduction** in compute per token. (It is also $12.8/47 \approx 27\%$ of a hypothetical dense model of the *same* 47B total; the 5.5× figure uses the book's canonical 70B dense as the comparison, so always state which baseline the ratio is against.)
 
@@ -111,3 +111,3 @@
 - **Dense 70B**: KV cache ~1.31 MB per token × 9,200 tokens ≈ 12.06 GB (at 8-bit, the raw tensor byte-halving figure = 1.31 MB/token, exactly 50% of BF16 — the block-overhead and '54%' ITL-slope caveats are stated once in Ch 1; see Ch 7) or ~24 GB (at FP16 precision for the key/value storage pattern discussed in Ch. 7).
-- **MoE 70B-equivalent**: The KV cache is *identical* in size, because attention still processes all 9,200 tokens densely. The fact that only 14B of 47B total parameters are active in the feed-forward layers does not reduce the number of keys/values emitted by the attention layers.
+- **MoE 70B-equivalent**: The KV cache is *identical* in size, because attention still processes all 9,200 tokens densely. The fact that only 12.8B of 47B total parameters are active in the feed-forward layers does not reduce the number of keys/values emitted by the attention layers.
 
@@ -119,3 +119,3 @@
 > 1. **total parameters → weight residency.** The resident weights (all experts, for MoE) are what the GPUs must hold. For a 70B dense model this is ~140 GB FP16; for a ~47B MoE this is ~94 GB (full expert set) unless experts are explicitly offloaded.
-> 2. **active parameters/token → approximate compute per token.** The routed top-k fraction (e.g. ~14B active) sets the FLOPs per token (~28 GB of active weights read per token). This is not a memory-freeing lever unless offloading is in play.
+> 2. **active parameters/token → approximate compute per token.** The routed top-k fraction (e.g. ~12.8B active) sets the FLOPs per token (~25.6 GB of active weights read per token). This is not a memory-freeing lever unless offloading is in play.
 
@@ -147,3 +147,3 @@
 
-1. **Weight residency budget.** For a dense 70B model, provision 140 GB of FP16 weight memory per host. For an MoE model with ~47B total and ~14B active, distinguish two numbers: the **resident** budget (the full expert set, ~47B × 2 bytes ≈ 94 GB, unless experts are offloaded/swapped) and the **active per-token** footprint (~14B × 2 bytes ≈ 28 GB read per token). The active number governs compute; the resident number governs whether the weights stay on device. MoE therefore does not automatically lower the weight-residency floor — it only gives the *option* to offload inactives at the cost of bandwidth.
+1. **Weight residency budget.** For a dense 70B model, provision 140 GB of FP16 weight memory per host. For an MoE model with ~47B total and ~12.8B active, distinguish two numbers: the **resident** budget (the full expert set, ~47B × 2 bytes ≈ 94 GB, unless experts are offloaded/swapped) and the **active per-token** footprint (~12.8B × 2 bytes ≈ 25.6 GB read per token). The active number governs compute; the resident number governs whether the weights stay on device. MoE therefore does not automatically lower the weight-residency floor — it only gives the *option* to offload inactives at the cost of bandwidth.
 
@@ -195,5 +195,5 @@
 
-An architect is fleshing out the design of the internal Q&A tool described in Chapter 1's mini-case. The team's standing decision from Chapter 2 is the dense 70B model; a MoE model with 8 experts (roughly 47B total params, ~14B active per token) is the challenger under consideration. They ask: "If we go MoE, can we cut our GPU memory budget?"
-
-From the model-understanding chapter, the architect can answer: Active-compute memory yes — only ~14B of the ~47B total is active per token, so ~28 GB of *active* weight footprint is read per token vs. 140 GB for a dense 70B. But *resident* memory is a different question. An MoE model normally keeps its **full expert set resident** — the non-active experts still occupy HBM unless we explicitly use expert offload/swapping (Ch 3 §3.6, Ch. 18), which itself costs bandwidth. So MoE reduces compute per token, and it gives us the *option* to offload some experts to shrink residency, but it does **not** automatically reduce the weight-residency floor. And KV cache memory no — the attention layers still process every token densely, so the cache budget for a 9.2K-context input is the same regardless of whether the model is dense or MoE. We still need to provision for ~12 GB of KV cache (at 8-bit) or ~24 GB (at the precision pattern discussed in Ch. 7) per request, and we'll also need expert-routing infrastructure on top of that.
+An architect is fleshing out the design of the internal Q&A tool described in Chapter 1's mini-case. The team's standing decision from Chapter 2 is the dense 70B model; a MoE model with 8 experts (roughly 47B total params, ~12.8B active per token) is the challenger under consideration. They ask: "If we go MoE, can we cut our GPU memory budget?"
+
+From the model-understanding chapter, the architect can answer: Active-compute memory yes — only ~12.8B of the ~47B total is active per token, so ~25.6 GB of *active* weight footprint is read per token vs. 140 GB for a dense 70B. But *resident* memory is a different question. An MoE model normally keeps its **full expert set resident** — the non-active experts still occupy HBM unless we explicitly use expert offload/swapping (Ch 3 §3.6, Ch. 18), which itself costs bandwidth. So MoE reduces compute per token, and it gives us the *option* to offload some experts to shrink residency, but it does **not** automatically reduce the weight-residency floor. And KV cache memory no — the attention layers still process every token densely, so the cache budget for a 9.2K-context input is the same regardless of whether the model is dense or MoE. We still need to provision for ~12 GB of KV cache (at 8-bit) or ~24 GB (at the precision pattern discussed in Ch. 7) per request, and we'll also need expert-routing infrastructure on top of that.
 
@@ -202,5 +202,5 @@
 * * *
-![Fig 3.4 — Dense vs MoE parameter allocation and KV cache behavior. Controlled comparison: same attention geometry, same context and cache dtype — so the KV footprint is identical — while weight residency (140 GB dense vs ~94 GB for the ~47B MoE challenger) and the active-compute fraction (~100% vs ~30%) both differ. Schematic, not to scale. An MoE model that also uses GQA or a different attention mechanism is a different comparison (Ch. 7). [ILLUSTRATIVE][DERIVED]](figures/fig-03-0301.png)
-
-*Parameter-activation contrast. A dense 70B activates all 70B parameters per token (residency ≈ 140 GB, KV grows linearly with context). An 8-expert MoE still stores its full expert set as resident weights (not shown to scale), but only the top-2 (~14B) are active per token (active compute footprint ≈ 28 GB). KV cache growth with context is identical to dense — attention still processes every token.*
+![Fig 3.4 — Dense vs MoE parameter allocation and KV cache behavior. Controlled comparison: same attention geometry, same context and cache dtype — so the KV footprint is identical — while weight residency (140 GB dense vs ~94 GB for the ~47B MoE challenger) and the active-compute fraction (~100% vs ~27%) both differ. Schematic, not to scale. An MoE model that also uses GQA or a different attention mechanism is a different comparison (Ch. 7). [ILLUSTRATIVE][DERIVED]](figures/fig-03-0301.png)
+
+*Parameter-activation contrast. A dense 70B activates all 70B parameters per token (residency ≈ 140 GB, KV grows linearly with context). An 8-expert MoE still stores its full expert set as resident weights (not shown to scale), but only the top-2 experts plus always-on weights (~12.8B) are active per token (active compute footprint ≈ 25.6 GB). KV cache growth with context is identical to dense — attention still processes every token.*
 
@@ -213,9 +213,9 @@
 | total parameters | 70B | ~47B | [ILLUSTRATIVE][ASSUMPTION] expert split |
-| active params per token | 70B | ~14B | top-2 from 8 ≈ 2/8 = 25% of expert mass [ILLUSTRATIVE][DERIVED] |
-| active/total fraction | 100% | ~30% | 14B ÷ 47B ≈ 29.8% [ILLUSTRATIVE][DERIVED] |
+| active params per token | 70B | ~12.8B | top-2 from 8 = 2/8 = 25% of expert mass ≈ 11.4B + ~1.4B always-on = 12.8B [ILLUSTRATIVE][DERIVED] |
+| active/total fraction | 100% | ~27% | 12.8B ÷ 47B ≈ 27.23% [ILLUSTRATIVE][DERIVED] |
 | FP16 residency (total) | 140 GB | ~94 GB | 70B × 2 / 47B × 2 |
-| FP16 weight-read per token | 140 GB | ~28 GB | 70B × 2 / 14B × 2 (read per token, not residency) |
+| FP16 weight-read per token | 140 GB | ~25.6 GB | 70B × 2 / 12.8B × 2 (read per token, not residency) |
 | KV cache per request (9.2K ctx, 8-bit) | ~12 GB | ~12 GB | identical — attention dense |
-| FLOPs per forward pass | ~0.14T | ~0.028T | 70B × 2 / 14B × 2 |
-| compute ratio vs dense 70B | 1× | ~0.20× (~5× less) | (14B × 2) ÷ (70B × 2) = 28B ÷ 140B [ILLUSTRATIVE][DERIVED] |
+| FLOPs per forward pass | ~0.14T | ~0.0256T | 70B × 2 / 12.8B × 2 |
+| compute ratio vs dense 70B | 1× | ~0.183× (~5.5× less) | (12.8B × 2) ÷ (70B × 2) = 25.6B ÷ 140B [ILLUSTRATIVE][DERIVED] |
 
--- a/design/manuscript/chapter-24/chapter-24.md
+++ b/design/manuscript/chapter-24/chapter-24.md
@@ -45,3 +45,3 @@
 
-We define the *prompt-injection exposure surface* (PIES) as an **illustrative local attack-surface count**: the number of distinct prompt-pattern classes an adversary can successfully submit through all user‑facing entry points, where "distinct" is defined by an explicit clustering rule. **Make the rule part of the definition before any number appears**: two probe patterns are the same class if their normalized-edit-distance (NLE) is ≤ a fixed threshold — i.e. within NLE ≤ 0.25 of an existing class they are treated as equivalent; otherwise they are a distinct class (see §3 for the deduplication rule). This deterministic clustering rule (assign each new pattern to an existing class when NLE ≤ 0.25, else start a new class) is what makes the count well-defined, and it is an author-chosen operational rule, not a property of the deployment. **PIES is a local evaluation metric defined in this handbook** for our red/‑green‑team loop; it is *not* a standardized security metric, and a PIES value from one deployment is not comparable to a PIES value from another (the entry points, probe generator, and deduplication threshold are all author-defined). We report it with that caveat attached. It is a pedagogical toy metric for teaching the *loop's shape*, not a portable security measurement.
+We define the *prompt-injection exposure surface* (PIES) as an **illustrative local attack-surface count**: the number of distinct prompt-pattern classes an adversary can successfully submit through all user‑facing entry points, where "distinct" is defined by an explicit clustering rule. **Make the rule part of the definition before any number appears**: two probe patterns are the same class if their normalized-edit-distance (NLE) is ≤ a fixed threshold — i.e. within NLE ≤ 0.25 of an existing class they are treated as equivalent; otherwise they are a distinct class (see §3 for the deduplication rule). This greedy clustering rule (assign each new pattern to an existing class when NLE ≤ 0.25, else start a new class) is an explicitly **order-sensitive heuristic**, not a deterministic cross-run class count: threshold proximity is not transitive (A may sit within NLE 0.25 of B and B within 0.25 of C while A is not within 0.25 of C), so the class count — and therefore PIES — can change with the pattern generation order, the choice of class representative, and the tie-break rule. Without a canonical generation order, normalization denominator, representative-selection rule, stable sort, tie-break rule, and test fixture, the count is well-defined only within a single fixed run; it is an author-chosen operational rule, not a property of the deployment. **PIES is a local evaluation metric defined in this handbook** for our red/‑green‑team loop; it is *not* a standardized security metric, and a PIES value from one deployment is not comparable to a PIES value from another (the entry points, probe generator, and deduplication threshold are all author-defined). We report it with that caveat attached. It is a pedagogical toy metric for teaching the *loop's shape*, not a portable security measurement.
 
@@ -56,5 +56,5 @@
 - Naïve count: 4 entry points × 8 delimiters × 6 templates × 4 context segments = 768 patterns.
-- However, many combinations are semantically redundant. After deduplication by normalized edit distance at a fixed threshold (we use normalized Levenshtein distance ≤ 0.25 as the equivalence criterion), the unique exposure surface is **PIES = 217** [ILLUSTRATIVE] — author-defined operational proxy; the 217 is not reproducible from the text alone, since the dedup threshold is a local choice and normalized edit distance captures textual, not semantic, similarity.
+- However, many combinations are semantically redundant. After deduplication by normalized edit distance at a fixed threshold (we use normalized Levenshtein distance ≤ 0.25 as the equivalence criterion), the unique exposure surface is **PIES = 217** [ILLUSTRATIVE] — author-defined operational proxy; the 217 is not reproducible from the text alone, since the dedup threshold is a local choice, the greedy assignment is order-sensitive (generation order, representative selection, and tie-break are unspecified), and normalized edit distance captures textual, not semantic, similarity.
 
-This illustrative quantity — 217 distinct, non‑redundant prompt‑injection patterns — becomes the baseline by which we measure guardrail effectiveness. Normalized edit distance captures *textual* similarity, not *semantic attack equivalence*: two syntactically different attacks may be behaviorally equivalent, and two lexically similar attacks may exploit materially different pathways, so PIES is a reproducible operational proxy — not a measure of true semantic attack diversity. That is exactly why it is labeled author-defined here rather than presented as an objective property of the deployment. [ILLUSTRATIVE][DERIVED] — author-defined metric and dedup threshold
+This illustrative quantity — 217 distinct, non‑redundant prompt‑injection patterns — becomes the baseline by which we measure guardrail effectiveness. Normalized edit distance captures *textual* similarity, not *semantic attack equivalence*: two syntactically different attacks may be behaviorally equivalent, and two lexically similar attacks may exploit materially different pathways, so PIES is an order-sensitive operational heuristic — not a deterministic cross-run class count, and not a measure of true semantic attack diversity. That is exactly why it is labeled author-defined here rather than presented as an objective property of the deployment. [ILLUSTRATIVE][DERIVED] — author-defined metric and dedup threshold
 
@@ -75,3 +75,3 @@
 
-This derived quantity — 52 expected poisoned retrievals per cycle — quantifies the RAG corruption risk under a deliberately simple model. **This is a null-model baseline assuming uniform random retrieval**, not a realistic poisoning-risk estimate. In practice vector retrieval is emphatically *not* uniform sampling: a successful poisoning attack is usually constructed precisely to raise semantic similarity to targeted queries, so adversarial chunks can appear far more often in the top-k than their corpus share. Real poisoning exposure therefore has to be measured from ranked retrieval (report hit rates conditioned on the actual similarity ordering), because adversarial chunks are intentionally designed to alter retrieval probability. We present the uniform baseline first because it is the one computable by hand, and flag it as the *minimum* exposure, not an estimate of the true value. [ILLUSTRATIVE][DERIVED] — null-model uniform-retrieval baseline
+This derived quantity — 52 expected poisoned retrievals per cycle — quantifies the RAG corruption risk under a deliberately simple model. **This is a null-model baseline assuming uniform random retrieval**, not a realistic poisoning-risk estimate. In practice vector retrieval is emphatically *not* uniform sampling: a successful poisoning attack is usually constructed precisely to raise semantic similarity to targeted queries, so adversarial chunks can appear far more often in the top-k than their corpus share. Real poisoning exposure therefore has to be measured from ranked retrieval (report hit rates conditioned on the actual similarity ordering), because adversarial chunks are intentionally designed to alter retrieval probability. We present the uniform baseline first because it is the one computable by hand, and we flag it as a **uniform-sampling null reference, not a bound** — neither a floor nor a ceiling on real exposure. Two-line counterexample: unrelated queries whose distribution is disjoint from the poisoned chunks retrieve none of them, so exposure is near zero no matter how large Q is; highly-similar poison crafted for a targeted query family lands in the top-k far above its corpus share, so exposure is elevated well above 52. The measurable security metric must therefore be conditioned on the query distribution, the ranking, chunk provenance, and attack success. [ILLUSTRATIVE][DERIVED] — null-model uniform-retrieval baseline
 
@@ -155,3 +155,3 @@
 
-**Scenario:** The fleet’s Green Team observes that PIES has dropped from 217 to 143 after adding a prompt‑scanning guardrail. The poisoned‑hit rate remains at ≈0.003 per query (≈3 poisoned chunks per 1,000 queries). The tool‑use exploit rate is 0.44%. However, the false‑positive rate remains above target at 2.4% — down from 3.1% in Cycle 1, but still over the <1.5% target. The denominator is guardrail interventions, not queries: at the Cycle 2 guardrail‑trigger rate of 5.4 per 1,000 queries, a 2.4% false‑positive share blocks ≈0.13 legitimate queries per 1,000 (5.4 × 0.024 ≈ 0.13).
+**Scenario:** The fleet’s Green Team observes that PIES has dropped from 217 to 143 after adding a prompt‑scanning guardrail (both values from the same order-sensitive dedup heuristic, compared under a fixed generation order — §3.1). The poisoned‑hit rate remains at ≈0.003 per query (≈3 poisoned chunks per 1,000 queries). The tool‑use exploit rate is 0.44%. However, the false‑positive rate remains above target at 2.4% — down from 3.1% in Cycle 1, but still over the <1.5% target. The denominator is guardrail interventions, not queries: at the Cycle 2 guardrail‑trigger rate of 5.4 per 1,000 queries, a 2.4% false‑positive share blocks ≈0.13 legitimate queries per 1,000 (5.4 × 0.024 ≈ 0.13).
 
```
