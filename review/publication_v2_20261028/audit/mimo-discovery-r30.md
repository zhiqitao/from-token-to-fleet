# MiMo Discovery Pass — R30（独立第二意见，fresh read）

- 对象：`review/publication_v2_20261028/work/accelerated_external_review_proof_r30/render/build/from-token-to-fleet-v20260913.pdf`（425pp）+ `design/manuscript/chapter-01..27/*.md`
- 方法：全 27 章 + Appendix A 源文通读；`pdftotext -layout` 全文（印刷页 = PDF 页 − 20）逐条回验；所有候选先与 `issue-ledger.md`、`audit/*.md` 去重
- ID 段：**MiMo-2001…MiMo-2007**（避开已用的 MiMo-0001 / MiMo-C07）
- 结论：**NOT-CONVERGED** —— 7 个新发现（2×P2，5×P3），0 个 P1

---

## MiMo-2001 — P2 — Ch13 §3（印刷 p202）+ §8 mini-case（印刷 p206）：100 rps 机群数 50 台与 Ch17 自己的公式冲突，且「well under its per-host ceiling」为假

**类别**：(a) 跨章数字矛盾 + (b) 误导性表述 + (d) 缺容量/余量假设

**证据（源文原文）**
- Ch13 §3：`the canonical ~2.0 req/s per-host screen (Ch 16/17; C/W = KV-residency ÷ service time ≈ 17.5 ÷ 8.6 s …), the replica count is ~100 ÷ 2.0 ≈ **50 hosts**`
- Ch13 §8：`the fleet is ~100 ÷ 2.0 ≈ 50 hosts, a real cluster rather than a handful; **each replica sits well under its per-host ceiling**`（PDF p226 已回验）
- Ch17 给出的正式公式：`N = ⌈ λ_peak · W / (C · util_target) ⌉`，`util_target = 70%`，`the provisioned fleet adds one spare on top, the N−1 rule`

**复算**
| 口径 | 计算 | 结果 |
|---|---|---|
| Ch17 公式（FP16、非 agentic、100 rps） | ⌈100×8.6 / (17×0.70)⌉ = ⌈860/11.9⌉ | **73 工作 + 1 备 = 74 台** |
| 全利用率整槽下限（书内 D1 口径） | ⌈860/17⌉ = ⌈50.59⌉ | **51 台** |
| Ch13 给出 | 100 ÷ 2.0 | **50 台** |
| 50 台实际容量 | 50 × 17/8.6 = 98.84 rps | **< 100 rps 需求（差 1.2%）** |
| 每副本负载 vs 天花板 | 100/50 = 2.000 vs 17/8.6 = 1.977 | **在天花板之上，不是 "well under"** |

**三重问题**
1. 50 台比 Ch17 同一 100-rps 流量下的 74 台少 **32%**（比全利用率下限 51 也少 1 台）；
2. `each replica sits well under its per-host ceiling` 为假 —— 50 台只能交付 98.84 rps，副本已**压满/略超**天花板；
3. Ch13 §3 用未取整的 `17.5`（17.5/8.6 = 2.035 → 49.1 → 50），与 D1 修复后全书统一的 `floor 17 + ⌈⌉` 口径不一致；且完全未提 70% 利用率与 N−1 备机，尽管它自己写的是 `screen (Ch 16/17)`。

**去重**：`grep "Ch13|50 hosts|well under"` 在 issue-ledger + audit/*.md 中**零命中**（仅 figure-priority.md 提到 Fig 13.1 箭头）。`convergence-pass-g-r29.md:39` 与 `mimo-arithmetic-r30.md:23` 的「主机数全书一致 ✓」清单只覆盖 21/22/26/37/30/19/6/5/10/24，**未含 100-rps 情形**。

**修复**：Ch13 §3/§8 改为 `⌈100 × 8.6 / 17⌉ = 51 hosts at full utilization, 73 working + 1 spare = 74 at Ch17's 70% + N−1 rule`；删掉或改写 `well under its per-host ceiling` 为 `right at its per-host ceiling`。

---

## MiMo-2002 — P2 — Ch25 §8（印刷 p348）：`32 KV heads` 与同一括号内的 2.62 MB/token 及 Ch7/Ch4 矛盾

**类别**：(a) 跨章数字矛盾 + (e) 精度/单位错误

**证据（PDF p368 已回验）**
> `the 70B reference geometry is full multi-head attention (**32 KV heads**, 2.62 MB/token, Ch 7)`

**复算**
- 2.62144 MB/token = 2 × n_layers(80) × H_kv × D_head × 2 B ⇒ H_kv × D_head = 8192
- 书内约定 D_head = 128（Ch7 GQA 例：LLaMA-2 70B = 64 query / 8 KV / d_head 128）⇒ **H_kv = 64**
- 若真为 32 KV heads：2 × 80 × (32×128) × 2 = 1,310,720 B = **1.31 MB/token**（恰为一半）
- Ch7 原文：`GQA caches only one K/V per group (8 K/V per token) instead of one per query head (**64 K/V per token**)`
- Ch4 原文：`K/V width = hidden_dim = 8192` ⇒ 8192/128 = 64 heads

**去重**：`grep "32 KV|KV heads"` 仅命中 `mimo-source-verification.md` 的 MiMo-C07（Qwen3.8-27B 的 4 KV heads / head_dim 256，另一回事）。**未记录**。

**修复**：`32 KV heads` → `64 KV heads`（或删去头数，只留 `2.62 MB/token`）。

---

## MiMo-2003 — P3 — Ch19 §8 mini-case（印刷 p292）：`§19.3` 指错节，billable-vs-KV-resident 区分实际在 §19.6

**类别**：(c) 引用/来源错配

**证据**
- Ch19 §8 原文：`the re-fetch cost and the KV-resident length are distinct (**see the billable-vs-KV-resident distinction in §19.3**)`（PDF p312 / 印刷 p292）
- §19.3（Worked Example，PDF p296 / 印刷 p276）全文：**不含** `billable`，**不含** `KV-resident`（逐节扫描确认）
- `billable tokens` / `KV-resident tokens` 定义句出现在 **§19.6 Architecture Consequence**（PDF p305 / 印刷 p285）

**去重**：`grep "billable"` 在 issue-ledger + audit/*.md **零命中**。

**修复**：`§19.3` → `§19.6`。

---

## MiMo-2004 — P3 — Fig 5.1 图注（印刷 p85）：`those gates are measured on the target corpus (§5.4)` 指向的节不含该内容

**类别**：(c) 引用错配

**证据**
- 图注原文（PDF p105 / 印刷 p85）：`the **end-to-end evaluation gates** (retrieval quality, reranking, embedding recall, grounding, and final answer quality) … those gates are measured on the target corpus (**§5.4**)`
- §5.4 Measurement（印刷 p80）全文 2,074 字符，三条内容是：① 在真实查询上测 token 拆分 ② 测输出长度 ③ 测 p95 上下文长度 —— **不含** `target corpus`、**不含** `gate`、**不含** `retrieval quality`
- `target corpus` 实际出现在 **§5.3**（`must be validated on the target corpus`）；五道 gate 的完整清单**只存在于该图注自身**，Ch5 无任何一节枚举它

**去重**：`figure-audit.md:92` 反而断言 `评估门在 §5.4` —— 前一轮**未验证即采信**，故本条为新发现（且纠正前一轮的错误背书）。

**修复**：改为指向真正承载评估门的章节（Ch14 benchmark / Ch5 §3 的 `validated on the target corpus`），或删去 `§5.4` 只保留 `measured on the target corpus`。

---

## MiMo-2005 — P3 — Ch6 §3（印刷 p89）：`p99 ≈ 1.33 s` 无法从所述分布复现（总体 p99 = 5.0 s），仅为单个 N=10,000 样本的线性插值刀口值

**类别**：(b) 算术正确但结论误导 / 声称的算法不可复现

**证据（源文原文）**
> `a synthetic sample of N = 10,000 requests — 99% drawn from a log-normal with median 0.8 s, 1% a straggler cluster at 5.0 s — and the percentiles are read by linear interpolation on the sorted sample … p50 ≈ 0.80 s, p90 ≈ 0.94 s, p95 ≈ 0.99 s, and **p99 ≈ 1.33 s** … **even p99 (≈ 1.33 s) still looks healthy**`

**复算**
1. 由 p95 = 0.99 反解 σ = ln(0.99/0.80)/1.6449 = **0.12955**；同一 σ 给 p90 = 0.9445 ≈ 0.94 ✓（p50/p90/p95 三者自洽）
2. **总体（population）p99 = 5.0 s**：x<5 时 F(x) = 0.99·G(x) < 0.99 恒成立 ⇒ 0.99-分位数只能是 5.0。实测 F(1.33) = **0.989911 < 0.99**，F(4.999) = 0.99
3. 对数正态主体自身的 p99 = 0.8·exp(2.3263×0.12955) = **1.08 s**，也不是 1.33
4. 1.33 只能这样得到：numpy `linear` 在位置 0.99×(10000−1) = 9899.01，落在「9,900 个对数正态的最大值」与「5.0」之间 ⇒ p99 = 0.99·x_max + 0.01×5.0；要得 1.33 需 x_max ≈ 1.293
5. **种子敏感性实测**（N=10,000、恰 100 个 5.0、σ=0.1357、seed 0–7、`method='linear'`）：p99 = **1.308 / 1.320 / 1.335 / 1.353 / 1.367 / 1.400 / 1.420 / 1.424**；p999 恒为 5.0
6. **刀口性**：straggler 数为 99 → p99 ≈ 1.25；= 100 → ≈1.33；= **101（1.01%）→ p99 = 5.0 s**，本章「even p99 still looks healthy」的论点当场反转

**去重**：`discovery-audit.md:57/116` 与 `figure-audit.md:108` 都引用了 1.33，但只审了 SLO 口径（p95 vs p99.9）与粉带范围，并只验了单调性 `mode 0.7 < p50 0.8 < mean 0.85 < p99 1.33 ✓` —— **可复现性/刀口性从未被检验**。

**修复**：把 p99 标为样本统计量并给出刀口说明，例如 `p99 ≈ 1.33 s is a property of this exact N=10,000 sample (linear interpolation lands on the largest non-straggler draw); the population p99 of the stated mixture is 5.0 s, and one extra straggler (101/10,000) moves the sample p99 to 5.0 s`。

---

## MiMo-2006 — P3 — Ch20 §8（印刷 p302）：括注把 6 台归给「KV-residency bound」、21/22 台归给「throughput/latency bound」，与本章 §3 的「两界同一恒等式」表述冲突

**类别**：(b) 算术正确但归因误导

**证据**
- §8 括注：`(The KV-residency bound, Chapter 17, needs far fewer — ⌈86/17⌉ = 6 at the 10-rps average — but the throughput/latency bound binds here, so the larger requirement governs.)`（PDF p322 / 印刷 p302）
- 同章 §3 已明确：`The KV-residency bound coincides here … so the two bounds are *co-binding* at the peak … (the two views are **the same identity, λW/C = λ/(C/W)**)`；并点名 `The "far fewer hosts (~6)" figure applies **only to the 10-rps average** (⌈86/17⌉ = 6), not the 40-rps peak`

**问题**：10 rps 平均下两界都给 6，40 rps 峰值下两界都给 21 —— 6 与 21 的差是**负载（均值 vs 峰值）**，不是**界别**。§8 的措辞让读者以为要取「两个不同约束的最大值」，而 §3 刚证明它们是同一个恒等式。

**去重**：`grep "far fewer|86/17"` 只命中算术复算 PASS 记录，**未作为问题记录**。

**修复**：§8 括注改写为与 §3 一致：`⌈86/17⌉ = 6 is the same bound evaluated at the 10-rps average; at the 40-rps peak both views give ⌈344/17⌉ = 21 (→ 22 with the ρ ≈ 0.95 derate), so the peak requirement governs.`

---

## MiMo-2007 — P3 — Ch15 源文节号与 R30 PDF 渲染节号不一致（唯一一章）

**类别**：(g) 源↔PDF 交叉核对

**证据**
- 源文 `## N.` 节号 vs PDF 渲染 `C.N.`：

| 源文 | PDF 渲染 | 标题 |
|---|---|---|
| `## 5.` | **15.7** | Common Mistakes（PDF p246 / 印刷 p226） |
| `## 6.` | **15.8** | Architecture Consequence |
| `## 7.` | **15.9** | What We Still Don't Know |
| `## 8.` | **15.10** | End-of-Chapter Mini-Case: The Second Host（PDF p248 / 印刷 p228） |

- 成因：Ch15 有 3 个源文未编号的 `##` 标题（`The Architect's Question`、`The Optimization Decision Map`、`Two Mechanisms, Read as Mechanisms`），其中后两个在 PDF 中被顺序编号为 15.5 / 15.6（`The Architect's Question` 保持无号），于是把源文的 5–8 推到 15.7–15.10（源文 8 个编号节 + 2 个被编号的无号节 = PDF 10 节）
- **全 27 章逐章比对：只有 Ch15 不一致**（Ch21 源/PDF 同为 9 节；Ch27 为有意的 A.1–A.10，且 A.3/A.4/A.5/A.6/A.7/A.8/A.10 全部交叉引用已逐条验证正确）

**影响**：PDF 内部自洽（15.1–15.10），当前**没有任何 `§15.N` 交叉引用**，故读者侧不断链；但手稿源文的节号与成品不一致，是后续加引用时的定时炸弹。

**去重**：`mimo-arithmetic-r30.md` 已用 PDF 号（`§15.10`、`§15.6`），说明前一轮**知道**渲染号，但**未把源↔PDF 不一致登记为问题**。

**修复**：给 Ch15 的 3 个未编号 `##` 加 `{.unnumbered}`，或把源文 `## 5..8.` 改成 `## 7..8.` 之外的显式编号策略，使源号与渲染号一致。

---

## 已排查但**不**成立（避免误报）

| 候选 | 结论 |
|---|---|
| Fig 11.3 `§9.8` 是否指错 | **正确**。35 GB / 13.3K 段落确在 Ch9 §8 mini-case 内（PDF p177 / 印刷 p157）；先前的「缺失」是长行正则截断造成的假象。13,000×2.62 = 34.1 vs 「~35 GB」差 2.6%，属 `~13K` 对 13.3K 的正常取整，不报 |
| Ch8 `~19–20 hosts` vs Ch17 `21` | 两章都明说是**不同约束**（prefill FLOP 吞吐 vs KV 驻留），Ch8 自己写 `fundamentally different constraints … useful cross-check`；scope_ledger 亦注明 19/21 不强行相等。不报 |
| Ch15 `70,000 tok/s` / `26 hosts` / `38% MFU` | 已由 `ch15-n03.md`、`mimo-arithmetic-r30.md`（MiMo-0001）覆盖 |
| Ch16 全部 TCO 算术 | 逐条复算通过：122,500 / 23,316.93 / 10,000 → 155,816.93；6.24M；24.97 / 14.04 / 49.13 / 34.99；129,792；6.23M / 7.49M / 10.39M；24.96M；218,309.9；1.779× |
| Ch20 全部算术 | 18,400/19,780 = 93.0%；8×0.989×0.35/1.4e11 = 19,780；⌈86/17⌉ = 6；$20×8.6/17 = $10.12；8×(17/8.6) = 15.8≈16；35,000/9,500 = 3.68→3.7；3.7×8.6 = 31.8≈32；344/16.15 = 21.3→22；140/30–120 = 4.7–1.2 GB/s = 38–10 Gb/s —— 全对 |
| Ch24 PIES / Table 24-1 | 5.4×0.024 = 0.13 ✓；4.1×0.013 = 0.05 ✓；表内 Cycle1–3 与正文一致；60% vs 34% 已由 FTF-N17 覆盖 |
| Ch25 其余算术 | 140+30 = 170 GB ✓；$350,000/60 = $5,833 ✓；FP8 70 GB / FP32 280 GB ✓ |
| Ch27 / Appendix A | 四模型 active% 3.71/4.58/5.63/4.80 全对；`block_q4_K` 144 B/256 = 4.5 bit ✓；MXFP4 17 B/32 = 0.53125 B → 39.24375 GB ✓；A.1–A.10 交叉引用全部命中 |
| Ch2/3/7/8/9/11/12/18/19/21/22/23 关键算术 | 5.6 TB/s、1.29 PFLOP、1.19 PFLOPS、0.989、295/206 ridge、3.567 FLOP/B、27,280、L\* = 53.4K、245 GB/0.54 s、12.06 GB、0.52→0.13、15 GB、92,000/3,000/30×、3,600 canary —— 全对 |
| 内容丢失（源文有、PDF 无） | **零**。37 个低覆盖块复验：13 个是 `<!-- Figure spec -->` 注释（本就不渲染），其余为页/栏断行假阳性（`capabilitygaps…`、`mttrforabadrelease…`、`fp32rejected280gb…`、脚注 URL 等逐条 `PRESENT`）；21 个「缺失标题」中 8 个是 Ch27 的 A.N 重编号、1 个是 Ch15 的 8.→15.10、其余为 `{.unnumbered}` 属性串；568 个「缺失表格单元」是 `pdftotext -layout` 多列交错导致的假阳性（抽查 Ch2 词汇表/资源表/指标表均在 PDF p36–42 完整渲染） |

---

## 汇总

| ID | 严重度 | 章 + 印刷页 | 类别 | 一句话 |
|---|---|---|---|---|
| MiMo-2001 | **P2** | Ch13 p202/p206 | (a)(b)(d) | 100 rps 给 50 台，Ch17 同流量公式给 74 台；「well under ceiling」实为略超 |
| MiMo-2002 | **P2** | Ch25 p348 | (a)(e) | `32 KV heads` 与同句 2.62 MB/token、Ch7 的 64 K/V 矛盾 |
| MiMo-2003 | P3 | Ch19 p292 | (c) | `§19.3` 应为 `§19.6` |
| MiMo-2004 | P3 | Fig 5.1 p85 | (c) | `§5.4` 不含评估门/target corpus |
| MiMo-2005 | P3 | Ch6 p89 | (b) | p99 = 1.33 s 不可复现（总体 5.0 s），且 101/10,000 即翻转 |
| MiMo-2006 | P3 | Ch20 p302 | (b) | 括注把均值/峰值之差误写成界别之差，与本章 §3 冲突 |
| MiMo-2007 | P3 | Ch15 p226/p228 | (g) | 源文 §5–§8 渲染为 15.7–15.10，全书唯一一章 |

**NOT-CONVERGED**：Qwen 收敛轮报 CONVERGED，但本轮在 Ch13 主机数、Ch25 头数、两处交叉引用、Ch6 分位数可复现性、Ch20 归因、Ch15 节号上仍找到 7 个未登记问题（2×P2）。