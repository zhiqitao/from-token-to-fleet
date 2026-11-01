# review-oct31-sla-source — 2026-10-31 独立评审 P2-06 / P2-08 / P1-02 / P1-03 / P3-01 处置证据

评审输入：`Publishing_Readiness_Review_2026-10-31.md`（缓存 `doc_8bf82ad24fd9`），条目 P2-06、P2-08、P1-02、P1-03、P3-01。
仓库 HEAD（本轮 pin 与基线）：`27f4cd571d53ecb2ac549d5825a77c87f8736ad3`（2026-10-31 13:45:33 -0700）。
范围：仅 `design/manuscript/*.md` 9 个文件；**未**改 `render/`、**未**做全书构建、**未** commit。Fig 6.2 生成器未改（P2-07 不在本轮范围）。

**数字审计（keep other numbers）**：对 9 个文件逐文件做数字多重集 before/after 比对 → **LOST = ∅**，即没有任何数值被改动或丢失；新增数字全部是新增的交叉引用（§号、ADR 号、修订号）。唯二从 Fig 7.7 图注中移出的 `24.9037`、`17.51` 仍在书内（`24.9037` 见 ch15/ch17，`17.51` 见 ch7 §3 注、ch16/ch17/ch20/ch25），并已回写进 ch7 图下技术注。

---

## 1. P2-06 — 决策态框 / HOLD ADR / 区域故障转移的 mandatory-vs-optional

| 文件 | sha256 before | sha256 after |
|---|---|---|
| `chapter-16/chapter-16.md` | `5d85af2909813e45662a988b6dc75a09c6341310220c24ea9abe9753ef58734a` | `de15c8da4ca15cc4ebafc2aa78918a429126cf91c63e2b861e9c9e99112ef9a5` |
| `chapter-17/chapter-17.md` | `0f8c98b6c2248ee6a217a657eaf542084bce918598c82b734b6470a2403608e6` | `469b32ef6a6d8c8601c915fab7c00f72d28c78526fcc72e20b461463c43e6f57` |
| `chapter-22/chapter-22.md` | `f06a228cd771e7ade4fec527112e7482adfa575eabc7a2f12408021fcb88a5bf` | `fbbd9397fb3944e2b3c21b5e5746c6f5ffde2f496ea1f7f7d395ef362ab14779` |
| `chapter-25/chapter-25.md` | `040b50adc2ddd46aa5b308f2b38b8493815c90a9ed57bba34a01cb54142f79a2` | `86f640461d541015f8f2cf6dbdbd0395edb90c5d233d218c8f87ca3ec2e87655` |
| `chapter-03/chapter-03.md` | `55ec2184746bc71e1476108c3da27b495ec5d3f0a0101f73b173a856a7d4025f` | `06f3b7ae6164165d8012534b2f80309937fe841210cdeee7c03e589340a5925c` |
| `chapter-07/chapter-07.md` | `415f124ad319a41c46d57c0b50fad82448658ee5fa6eb27483926341b109b2a2` | `4d7589896363fd5d15b776cd63c40077c2a81132af86ea1015063444f8784385` |
| `chapter-15/chapter-15.md` | `e1dbfaedd0d892a8dfbaa6647caa04d0df80e2cea83972fc5e0e0cdbc1fa757d` | `4e3afbfe2d6d3173aa6e72a40f387a485507926ff35892ed50a2c4e024807b9a` |
| `chapter-19/chapter-19.md` | `95781134a1a60eccad2c4926f1874b9169d101a912651648c68ef6945f7c4ac2` | `92980040a6214da0b030e31bec173b6ad19ae1b6eefee4eb8673979b6ed2090f` |
| `chapter-27/chapter-27.md` | `41571b3e636f384139d49fc250d8fcd4c468f7d7edae171aad00572471e641fb` | `18e77cdbb6bd089e36eccf80f256ca80e700b0e88337a58f4da0c21c35c42d28` |

改动：
- **ch16 §16.6**：新增决策态框 `CANDIDATE SCREENED; NOT COMMITTABLE — regional availability, failover, SLO-goodput and matched-scope costs pending`，逐条列出四项 pending（99.9% 多区域 SLA UNSIZED/NOT PRICED、仅 N−1 单机故障转移、SLO-goodput 待 Ch14 实测、A/B/C 口径不匹配），并声明不得记为通过 spine 环的 **Validate & Defend → Commit**（Fig 1.1）或已提交 ADR。
- **ch16 §16.3**：把 `…consistent state/data replication (model weights + KV/index replication across regions)` 改为 **mandatory vs optional** 分述——每区域**必须**能加载权重并服务检索索引（weight/index availability mandatory）；**跨区域复制 live KV 是可选策略而非要求**，客户端可在存活区域 replay/recompute 上下文，代价是恢复时间落在 SLA 恢复目标内。
- **ch17 §17.6**：同款决策态框 + 在多区域段末补同一 mandatory/optional 分句。
- **ch22 §6**：同款决策态框 + **示例 ADR 0015（Status: HOLD）紧凑记录**，Context 给出三模式单区域成本（~$155.8K/mo ~$24.97/1K、~$87.6K/mo ~$14.04/1K、~$129.8K/mo ~$20.8/1K @6.24M req/mo），Decision 明确 **不选 least-cost 行**（$14.04/1K 云默认占用输入），Alternatives 三条（选最便宜 / 提交自建 / HOLD）与四条 exit criteria。
- **ch25 §6**：同款决策态框 + **ADR 0015 完整模板记录**（Status HOLD、Context、Decision=none、Consequences、Alternatives considered、Evidence、Trade-offs、Decision owner、Validation plan、Rollback plan、Review trigger、Falsification path），Validation plan 第 (ii) 条写明 region-failure test 中 **weight/index availability mandatory、live-KV replication optional（客户端可 replay/recompute）**。

验证（脚本断言，全部 OK）：4 章均含 `CANDIDATE SCREENED; NOT COMMITTABLE`；ch22/ch25 含 `HOLD` 与 `live-KV replication`；ch16/ch17 含 `optional policy`。成本数字与 ch16 表 16-1/16-2 逐字一致，未新增任何价格。

## 2. P2-08 — 四条图注按三段式（takeaway · scope · caveat）压缩

| 图注 | before chars | after chars | Δ | before words | after words |
|---|---|---|---|---|---|
| Fig 17.1 | 604 | 555 | -8.1% | 102 | 92 |
| Fig 7.7 | 1834 | 861 | -53.1% | 286 | 136 |
| Fig 3.3 | 476 | 444 | -6.7% | 70 | 62 |
| Fig 15.2 | 461 | 415 | -10.0% | 65 | 56 |

- **Fig 7.7**（1834 → 861，−53.1%）：图注只留预算关系 + Scope + aggregate caveat + analytical-upper-bound 警告；**per-rank TP=8 推导整体移到图下新段 `**Technical note — per-rank fit (moved out of the caption).**`**，其中保留全部数字 140 / 17.5 / 64 / 436 / 54.5 / 24.9 / 8 / 3.1 / 24.9037 / 17.51 / 17 / 18 与全部限定词（aggregate 非单堆、"total bytes < total HBM" 必要非充分、rank 可能是绑定约束、Chs. 9–10）。
- **Fig 15.2**（−10.0%）：两条轴语义并入左右括注，删掉与图下正文重复的第三句；限定词（synthetic/非实测、左轴百分比语义、右轴任意 goodput 单位、HBM 饱和点）全保留。
- **Fig 17.1**（−8.1%）、**Fig 3.3**（−6.7%）：改为显式三段式并压词。**削减受限于"保留全部限定词"**：17.1 的 service-rate/非排队结果、N−1 是容量论证非 p99 证明、必须实测尾延迟；3.3 的官方舍入计数非推断拆分、宽度示意不编码步数、offload 改变驻留并增加权重传输、非内存测量——逐条都在，再削只能删限定词。
- 四图现在都显式带 `**Scope:**` / `**Caveat:**` 三段结构；`[ILLUSTRATIVE][DERIVED]`、`[ILLUSTRATIVE][ASSUMPTION]` 等证据标签原样保留。

## 3. P1-02 — Appendix A 版本钉死的源索引落地声明

- **ch27** 在 `[A-S01]–[A-S105]` 指针段之后新增 blockquote：规则 `[A-S23]` → pinned source-ledger entry 23；仓库路径 `review/publication_v2_20261028/audit/source-verification.md`；不可变修订 `27f4cd571d53ecb2ac549d5825a77c87f8736ad3`；完整 permalink：
  `https://github.com/zhiqitao/from-token-to-fleet/blob/27f4cd571d53ecb2ac549d5825a77c87f8736ad3/review/publication_v2_20261028/audit/source-verification.md`
  并说明修订已 pin、地址不随仓库前进而漂移，去掉修订即默认分支同路径（供后续版本）。
- 验证：
  - `curl` blob permalink → **200**；`raw.githubusercontent.com` 同修订 → **200**；仓库根 → **200**（公开可解析）。
  - `git diff HEAD -- …/source-verification.md` 为空、`git status` 干净 → HEAD 版 ledger 与工作区一致。
  - 键集合比对：manuscript 唯一 `[A-S#]` = **71**，HEAD 版 ledger 唯一键 = **71**，`comm` 双向差集为空 → **71/71 全部在该修订可解析**。

## 4. P1-03 — 脚注标记与线规（**OPEN**，构建侧）

实测 `render/latex/book.pdf`（425 页，`pdftohtml -xml`，尺寸按 1.5× 换算回 pt）：
- `< 7.05 pt` 的文本 span 共 **79** 个（评审记 73），全部 **5.98–6.00 pt**；
- 其中 **62** 个位于脚注区（top > 500 pt）＝**每条脚注开头的标号**（脚注正文在 `\footnotesize` 内，其上标再缩小 → ~6 pt）；
- **17** 个是图/表内数字与词（p288/307/308/404/405），非脚注；
- **正文中的脚注引用上标 = 8.00 pt（81 个 span）≥ 7 pt** → 承重的 footnote *reference* 标记已达标；
- 无任何正文散文 < 7 pt（与评审一致）。

探针（`render/bin/tectonic`，`book` 11 pt 最小文档，非全书构建）：
- 默认 `\@makefnmark`：正文标 **8.00 pt**、脚注区标 **6.00 pt**（复现 5.98）；
- 重定义为 `\fontsize7.5`：两处均 **7.33 pt** → **可以抬升**，但朴素重定义会把 8.00 pt 的正文标压到 7.33 pt，必须只针对脚注区标号（如在 `\@makefntext` 内设 `\normalsize`/≥7 pt）。

线规：`render/latex/book.sty:119` `\renewcommand{\headrulewidth}{0.4pt}` < KDP 0.75 pt 线宽下限。

**结论**：正文引用标 8.00 pt → 判 *acceptable superscript*，无需改；脚注区 5.98 pt 标号与 0.4 pt 页眉线均在 `book.sty`/`md_to_latex.py`，**手稿无法改**；抬升脚注区标号会加宽脚注首行 → 可能局部 reflow → **OPEN**（需 renderer owner 改 + 重新分页/打印打样验证）。

## 5. P3-01 — List of Figures 短标题（与完整图注分离）

- 机制：`render/latex/md_to_latex.py::short_title()` 取图注正文首句（≤84 字符）作 `\caption[short]{long}`，超长则硬截断加 `…`。因此把**刻意的短标题写成图注首句**，LoF 条目即为该短标题而非截断串。
- 结果（直接 import `short_title` 跑全量，逐字核对）：
  - Fig 19.2 → `Agent turns: token and KV growth`
  - Fig 19.3 → `Agent context and compaction`
  - Fig A.2 → `Vendor-relative KV/compute ratios`
  三条与评审建议**逐字一致**；完整图注内容与全部数字/限定词不变（仅前置短标题句）。
- 全书扫描：**55 条图注，省略号 LoF 条目 = 0**（修复前 3：`from 24.9…` / `and…` / `reference,…`）。

## 6. OPEN / 遗留

1. **P1-03（OPEN）**：脚注区 5.98 pt 标号抬升到 ≥7 pt、`headrulewidth` 0.4 → ≥0.75 pt，均为构建侧；抬升可能局部 reflow，需 renderer owner + 重新分页与打印打样。正文引用标 8.00 pt 已达标。
2. **ch27 140 字符 permalink 的断行（OPEN）**：`fix_urls()` 会包成 `\url{}`（`hyphens` 选项），但本轮未做全书构建，无法确认该 URL 在正文栏宽内断行正常 → 下次构建需检查 overfull。
3. P2-08 的 Fig 16.1 / Fig 22.1（评审指定的首批原型）不在本轮范围，未改。
4. ch4 §4.3 的 `consistent state/data replication across regions` 为泛指、未点名 KV，按本轮范围未改；如需与 ch16 措辞统一可下轮处理。

## 7. 完整 diff（before → after，9 文件，unified，n=1）

```diff
--- a/chapter-16/chapter-16.md
+++ b/chapter-16/chapter-16.md
@@ -116,3 +116,3 @@
 
-**Multi-region active-active availability is NOT priced in this TCO.** The canonical workload's stated SLA (Ch 4) is multi-region active-active at 99.9% availability, but **every** `$/1K` figure in this chapter (and the host counts in Ch 17) prices a **single-region** deployment — the 21-host headline rows are the **ideal zero-spare** fleet with **no N−1 reserve priced**, and only the 30-host policy row carries the **29 working + 1 reserve** N−1 single-host failover — **not** multi-region active-active. Multi-region active-active is a **different provisioning problem** from N−1 single-host failover: it requires cross-region capacity duplication (no single region's loss may take the service down), region-failure tolerance, data locality and traffic routing (geo/health-based routing, per-region caches and indices), and consistent state/data replication (model weights + KV/index replication across regions). None of that is priced or validated here, and none of it is implied by the N−1 reserve host above (the 30-host policy row). Accordingly the canonical cost figures **understate the cost of the canonical workload's own stated 99.9% availability requirement** — read the `$/1K` and monthly totals as *single-region* numbers — zero-spare at the 21-host headline, N−1-reserve only at the 30-host policy — and add a separate multi-region capacity + replication cost line (on the order of ≥2× the single-region fleet on the capacity-duplication term alone) before the availability SLA can be considered met.
+**Multi-region active-active availability is NOT priced in this TCO.** The canonical workload's stated SLA (Ch 4) is multi-region active-active at 99.9% availability, but **every** `$/1K` figure in this chapter (and the host counts in Ch 17) prices a **single-region** deployment — the 21-host headline rows are the **ideal zero-spare** fleet with **no N−1 reserve priced**, and only the 30-host policy row carries the **29 working + 1 reserve** N−1 single-host failover — **not** multi-region active-active. Multi-region active-active is a **different provisioning problem** from N−1 single-host failover: it requires cross-region capacity duplication (no single region's loss may take the service down), region-failure tolerance, data locality and traffic routing (geo/health-based routing, per-region caches and indices), and consistent state/data replication. **Mandatory vs optional in that replication:** each region must be able to load the model weights and serve its retrieval index — weight/index availability is mandatory, because a region that cannot load the model or answer retrieval cannot serve traffic — whereas **replicating live KV across regions is an optional policy, not a requirement**: clients may instead replay or recompute the context in the surviving region, trading cross-region KV transfer for recovery time inside the SLA's recovery objectives. None of that is priced or validated here, and none of it is implied by the N−1 reserve host above (the 30-host policy row). Accordingly the canonical cost figures **understate the cost of the canonical workload's own stated 99.9% availability requirement** — read the `$/1K` and monthly totals as *single-region* numbers — zero-spare at the 21-host headline, N−1-reserve only at the 30-host policy — and add a separate multi-region capacity + replication cost line (on the order of ≥2× the single-region fleet on the capacity-duplication term alone) before the availability SLA can be considered met.
 
@@ -192,2 +192,6 @@
 
+> **DECISION STATE — CANDIDATE SCREENED; NOT COMMITTABLE — regional availability, failover, SLO-goodput and matched-scope costs pending.**
+>
+> This candidate clears the capability screen and the *single-region* cost screen only; it must not be recorded as passing the spine loop's **Validate & Defend → Commit** stages (Fig 1.1) or as a committed ADR (Ch 22 → Ch 25). Four items are outstanding: **regional availability** — the canonical 99.9% multi-region active-active SLA (Ch 4) is UNSIZED and NOT PRICED here (§16.3, Table 16-2); **failover** — only N−1 single-host failover is modeled (the 30-host policy row), with no region-failure test; **SLO-goodput** — the p95 TTFT/TPOT pass is provisional until measured at the target offered load (Ch 14); **matched-scope costs** — the A/B/C modes are not compared on equal availability, failover, warm-capacity, occupancy-evidence or p95-SLO assumptions (§16.3, Table 16-1). Until all four are in hand the honest status is *screened, not committed*: no least-cost selection, no procurement recommendation. [ILLUSTRATIVE][ASSUMPTION]
+
 This completes the chain from vague requirement to a defensible, costed architecture, while being honest that the TCO gate is not an unconditional win and that the SLO pass is *provisional until benchmarked*.
--- a/chapter-17/chapter-17.md
+++ b/chapter-17/chapter-17.md
@@ -16,3 +16,3 @@
 
-![Fig 17.1 — Sizing a fleet by burst peak, headroom, and failover: a ~5.5 req/s burst a single host (~2.0 req/s analytical bound) cannot meet, so a 4-host fleet (~8.0 req/s) is sized ABOVE it and the N-1 = 3 residual (~6.0 req/s) still clears it. **Scope:** the burst is a small illustrative example; the canonical 40 rps peak is sized the same way to ≈21 hosts (Ch. 17-20). **Queueing-model note:** the ~2.0 req/s/host is a *service-rate* (capacity) bound, not a queueing result, and N-1 failover is a *capacity* argument, not a proof of p99 TTFT/TPOT — tail latency must be measured (Ch 14). [ILLUSTRATIVE][DERIVED]](figures/fig-17-1701.png)
+![Fig 17.1 — Sizing a fleet by burst peak, headroom, and failover: a ~5.5 req/s burst exceeds one host's ~2.0 req/s analytical bound, so a 4-host fleet (~8.0 req/s) is sized above it and the N-1 = 3 residual (~6.0 req/s) still clears it. **Scope:** a small illustrative burst; the same rule sizes the canonical 40 rps peak to ≈21 hosts (Chs. 17–20). **Caveat:** ~2.0 req/s/host is a *service-rate* (capacity) bound, not a queueing result; N-1 failover is a *capacity* argument, not a p99 TTFT/TPOT proof — tail latency must be measured (Ch 14). [ILLUSTRATIVE][DERIVED]](figures/fig-17-1701.png)
 
@@ -194,3 +194,7 @@
 
-**Multi-region active-active availability is NOT priced in this chapter's arithmetic.** The multi-region caveat of Ch 16 §16.3 applies verbatim to these host counts: every host count here — and the N−1 failover/redundancy model above — is a **single-region, N−1-only** number (≈21 peak / 29 working / 30 with N−1), so the counts and the sizing arithmetic that hangs off them **understate the cost of the canonical workload's own stated 99.9% availability requirement**. Add a separate multi-region capacity + replication cost line before the availability SLA can be considered met.
+**Multi-region active-active availability is NOT priced in this chapter's arithmetic.** The multi-region caveat of Ch 16 §16.3 applies verbatim to these host counts: every host count here — and the N−1 failover/redundancy model above — is a **single-region, N−1-only** number (≈21 peak / 29 working / 30 with N−1), so the counts and the sizing arithmetic that hangs off them **understate the cost of the canonical workload's own stated 99.9% availability requirement**. Add a separate multi-region capacity + replication cost line before the availability SLA can be considered met — remembering the §16.3 split: per-region **weight and index availability is mandatory**, while **live-KV replication across regions is an optional policy** (clients may replay or recompute context in the surviving region instead, within the recovery objectives).
+
+> **DECISION STATE — CANDIDATE SCREENED; NOT COMMITTABLE — regional availability, failover, SLO-goodput and matched-scope costs pending.**
+>
+> Every host count in this chapter is a *screen*, not a commitment: **regional availability** is unsized and unpriced (Ch 16 §16.3), **failover** here means one lost host (N−1), not a lost region, **SLO-goodput** at the target offered load is a Ch 14 measurement that has not been taken, and the **cost scopes** behind these counts are not matched across delivery modes (Ch 16 §16.3, Table 16-1). The counts therefore inform the candidate; they do not close the spine loop's **Validate & Defend → Commit** stages (Fig 1.1), and no mode is selected on least cost from them. [ILLUSTRATIVE][ASSUMPTION]
 
--- a/chapter-22/chapter-22.md
+++ b/chapter-22/chapter-22.md
@@ -104,2 +104,17 @@
 
+> **DECISION STATE — CANDIDATE SCREENED; NOT COMMITTABLE — regional availability, failover, SLO-goodput and matched-scope costs pending.**
+>
+> Running the loop on the canonical workload yields a *screened candidate*, not a commitment: the multi-region 99.9% SLA is unsized and unpriced (Ch 16 §16.3), failover is N−1 single-host only with no region-failure test, SLO-goodput is unmeasured at the target offered load (Ch 14), and the three delivery modes are not compared on matched scopes (Ch 16, Table 16-1). The Decision rung may therefore record a **HOLD** — a HOLD is a legitimate, auditable outcome of this loop, and it is what the example below records.
+
+**Example ADR at the Decision rung — an explicit HOLD, not a least-cost pick.**
+
+- **Title:** ADR 0015 — Delivery mode and region topology for the canonical Q&A workload
+- **Status:** **HOLD** — screened, not committed (the same record in the full Ch 25 template appears in Ch 25 §6)
+- **Context:** The loop has produced capability, capacity and *single-region* cost screens: the 70B 8×H100 self-host clears the capability screen, and the single-region arithmetic gives ~$155.8K/mo (~$24.97/1K) self-host, ~$87.6K/mo (~$14.04/1K) on the cloud default paid-occupancy input, and ~$129.8K/mo (~$20.8/1K) managed API at the canonical 6.24M requests/mo. The canonical workload's own 99.9% multi-region active-active requirement is in none of those numbers.
+- **Decision:** None yet. The least-cost row — the cloud default paid-occupancy input at ~$14.04/1K — is explicitly **not** selected, and neither is self-host or the managed API: all three rest on unmatched scopes, an unpriced availability requirement and unmeasured SLO-goodput.
+- **Rationale:** A HOLD is the honest record when a hard nonfunctional requirement (regional availability) is still unsized and the comparison basis is unequal; picking the cheapest row would encode an input assumption as a decision.
+- **Alternatives considered:** (1) *select the least-cost mode now* — rejected: the $87.6K line is a paid-occupancy INPUT, not a measured duty cycle, and no row carries the 99.9% active-active cost; (2) *commit to self-host* — rejected: its SLO-goodput pass is provisional until benchmarked (Ch 14); (3) *HOLD with explicit exit criteria* — adopted.
+- **Exit criteria / review trigger:** (i) regional capacity sized and priced for the 99.9% active-active SLA; (ii) a region-failure test defined — per-region **weight/index availability mandatory**, **live-KV replication optional** (clients may replay or recompute context in the surviving region within the recovery objectives, Ch 16 §16.3); (iii) measured p95 SLO-goodput at the target offered load; (iv) a matched-scope re-run of the three modes.
+- **Evidence tags:** [ILLUSTRATIVE][ASSUMPTION] — the three single-region cost rows are Ch 16 scenario inputs, not quotes; [DERIVED] — 6.24M req/mo and every $/1K division are Ch 16 arithmetic.
+
 ## 7. What We Still Don't Know
--- a/chapter-25/chapter-25.md
+++ b/chapter-25/chapter-25.md
@@ -178,2 +178,44 @@
 ![Fig 25.1 — The Anatomy of an Architecture Decision Record, and how one ADR supersedes the next. **Takeaway:** an ADR is a fixed five-field record — Title and status, Context (the situation), Decision (the choice), Consequences (the effects), Alternatives considered (the rejected options) — and it is *kept, not edited*: the Consequences of ADR-001 become the Context of ADR-002, which supersedes it while the original stays on file. **Scope:** the generic anatomy and supersession rule that the chapter's worked model-shape ADR (§25.3) and the copy-ready template (§25.3.1) put into practice as their five core fields (§25.1), each extended with its own apparatus. **Warning:** illustrative structure, not a measured decision record — a real ADR must carry the evidence tags its numbers are judged by. [ILLUSTRATIVE] conceptual](figures/fig-25-2501.png)
+
+> **DECISION STATE — CANDIDATE SCREENED; NOT COMMITTABLE — regional availability, failover, SLO-goodput and matched-scope costs pending.**
+>
+> An ADR may record this state. The canonical candidate has cleared the capability and *single-region* cost screens (Ch 16 §16.6, Ch 17 §17.6), but the canonical workload's 99.9% multi-region active-active requirement is unsized and unpriced, only N−1 single-host failover is modeled, SLO-goodput is unmeasured at the target offered load (Ch 14), and the delivery modes are not compared on matched scopes. Writing **HOLD** into the Status field is the correct, auditable record — and it is not the same as choosing the cheapest row.
+
+**A worked HOLD record — ADR 0015, in this chapter's template** (the compact form appears at the Decision rung in Ch 22 §6; the record is kept, not edited).
+
+#### ADR 0015 — Delivery mode and region topology for the canonical Q&A workload {.unnumbered}
+
+**Status:** **HOLD** — screened, not committed.
+
+**Context:**
+The loop has produced capability, capacity and *single-region* cost screens: the 70B 8×H100 self-host clears the capability screen, and the single-region arithmetic gives ~$155.8K/mo (~$24.97/1K) self-host, ~$87.6K/mo (~$14.04/1K) on the cloud default paid-occupancy input, and ~$129.8K/mo (~$20.8/1K) managed API at the canonical 6.24M requests/mo. The canonical workload's own 99.9% multi-region active-active requirement sits in none of those numbers (Ch 16 §16.3, Table 16-2).
+
+**Decision:**
+No delivery mode is committed. The least-cost option — the cloud default paid-occupancy input at ~$14.04/1K — is explicitly **not** selected, and neither is self-host nor the managed API. **HOLD is the decision**, with the four exit criteria below as its review trigger.
+
+**Consequences:**
+
+- **Positive:** no input assumption is promoted to a commitment; the four pending items are named, owned and testable, and the single-region baseline (21-host headline / 30-host N−1 policy) keeps operating as a *provisional* assumption.
+- **Negative:** no procurement path this quarter, and the availability requirement stays unmet on paper until regional capacity is priced; planning must carry the single-region totals as single-region totals, not as the SLA's cost.
+- **Monitoring:** regional capacity quote, region-failure test result, measured p95 SLO-goodput at the target offered load, and a matched-scope re-run of the three modes.
+
+**Alternatives considered:**
+
+1. **Select the least-cost mode now** — rejected: the $87.6K line is a paid-occupancy INPUT, not a measured duty cycle, and no row carries the 99.9% active-active cost; choosing it would encode an assumption as a decision.
+2. **Commit to self-host** — rejected: its SLO-goodput pass is provisional until benchmarked (Ch 14), and it is single-region only.
+3. **HOLD with explicit exit criteria** — adopted.
+
+**Evidence:** [ILLUSTRATIVE][ASSUMPTION] — the three single-region cost rows are Ch 16 scenario inputs, not quotes. [DERIVED] — 6.24M req/mo and every $/1K division are Ch 16 arithmetic. [ASSUMPTION] — the 99.9% active-active requirement is the canonical workload's stated SLA (Ch 4), unpriced here.
+
+**Trade-offs & consequences:** the team trades a decision's timeliness for its defensibility: HOLD costs optionality in the near term and prevents a cost ranking from silently becoming an availability commitment.
+
+**Decision owner:** the serving-platform architect who ran the Ch 22 loop, with the SRE owner accountable for the region-failure test.
+
+**Validation plan:** (i) regional capacity sized and priced for the 99.9% active-active SLA; (ii) a region-failure test defined — per-region **weight/index availability is mandatory**, **live-KV replication across regions is an optional policy** (clients may replay or recompute context in the surviving region within the recovery objectives, Ch 16 §16.3); (iii) measured p95 TTFT/TPOT SLO-goodput at the target offered load; (iv) a matched-scope re-run of the three delivery modes.
+
+**Rollback plan:** none required while HOLD stands — no mode has been commissioned; any interim spend stays month-to-month and reversible, and the single-region baseline remains the operating assumption.
+
+**Review trigger:** any validation item (i)–(iv) landing, or a change to the canonical workload's SLA or price period.
+
+**Falsification path:** if all four exit criteria are met and the matched-scope re-run still shows a stable least-cost ordering, a successor record (ADR 0018 or later) lifts the HOLD and supersedes this one; ADR 0015 stays on file unchanged. If the criteria cannot be met, the HOLD itself is the finding — the requirement and the cost model do not describe the same system.
 
--- a/chapter-03/chapter-03.md
+++ b/chapter-03/chapter-03.md
@@ -175,3 +175,3 @@
 
-![Fig 3.3 — Wan2.2 A14B selects experts as the denoising schedule progresses: two resident expert checkpoints supply the high-noise and low-noise stages, and only the selected expert runs in a branch evaluation. Official rounded counts are about 27B total and about 14B active, not an inferred per-expert parameter split. Stage widths are schematic and do not encode step counts; explicit offload changes residency and adds weight transfers. Mechanism schematic, not a memory measurement.](figures/fig-03-0304-wan-noise-experts.png)
+![Fig 3.3 — Wan2.2 A14B selects experts as the denoising schedule progresses: two resident checkpoints supply the high- and low-noise stages; only the selected expert runs in a branch evaluation. **Scope:** official rounded counts (about 27B total, about 14B active), not an inferred per-expert split; schematic widths (no step counts); offload changes residency and adds weight transfers (below). **Caveat:** mechanism schematic, not a memory measurement.](figures/fig-03-0304-wan-noise-experts.png)
 
--- a/chapter-07/chapter-07.md
+++ b/chapter-07/chapter-07.md
@@ -264,3 +264,5 @@
 
-![Fig 7.7 — The concurrency budget: where a 70B (canonical 80-layer full-MHA teaching geometry) host's 640 GB pool goes. **Aggregate-feasibility caveat:** the 640 GB figure is an *aggregate* across eight 80-GB H100s, not a single freely-allotable heap. Whether a given allocation actually fits depends on tensor-parallel sharding, KV partitioning, replication, runtime layout, per-rank fragmentation, workspace requirements, and communication topology — so "total bytes < total HBM" is a necessary but not sufficient test. Per-rank fit and sharding must also be validated (Chapters 9–10). **Per-rank example (TP=8):** the 140 GB of weights shard to ~17.5 GB per GPU; the ~64 GB runtime/NCCL reserve is per-host (not per-rank); the ~436 GB KV budget shards to ~54.5 GB per GPU, and under tensor-parallel attention the per-request KV (24.9 GB) also shards across the 8 ranks, so the per-rank KV per request is ~3.1 GB — the 17.5 concurrent figure is the *aggregate* bound, and the per-rank fit must be checked separately (a rank can be the binding constraint even when the aggregate fits). The figure shows the one dominant budget relationship: the on-host pool decomposes into weights + runtime + a leftover KV budget, and that KV budget divided by the per-request KV price sets concurrency. 140 GB weights + ~64 GB runtime/NCCL leaves ~436 GB of KV budget; at the 24.9 GB/request max-FP16 KV that gives C ≈ 17.5 concurrent requests (byte-accurate 436÷24.9037 = 17.51; the conservative integer "requests that fit" floor is 17, not 18), and FP8 (~12.45 GB/request) roughly raises it to ~35.0. This is the arithmetic behind the single-host capacity in Ch17. **This is an analytical upper bound, not a validated concurrent-request count** — the actual achievable concurrency must be measured under the target workload (Ch 14). [ILLUSTRATIVE][DERIVED]](figures/fig-07-0704.png)
+![Fig 7.7 — The concurrency budget: 140 GB weights + ~64 GB runtime/NCCL leaves ~436 GB of KV budget in a 70B (canonical 80-layer full-MHA teaching geometry) host's 640 GB pool, and that KV budget ÷ the per-request KV price sets concurrency — at 24.9 GB/request max-FP16 KV, C ≈ 17.5 concurrent (floor 17, not 18), and FP8 (~12.45 GB/request) roughly raises it to ~35.0. **Scope:** the arithmetic behind Ch 17's single-host capacity; derivation in §3 above and Ch 17. **Aggregate-feasibility caveat:** 640 GB is an *aggregate* across eight 80-GB H100s, not a freely-allotable heap — "total bytes < total HBM" is necessary but not sufficient, so per-rank fit must be validated separately (technical note below; Chs. 9–10). **This is an analytical upper bound, not a validated concurrent-request count** — measure it under the target workload (Ch 14). [ILLUSTRATIVE][DERIVED]](figures/fig-07-0704.png)
+
+**Technical note — per-rank fit (moved out of the caption).** Whether a given allocation actually fits depends on tensor-parallel sharding, KV partitioning, replication, runtime layout, per-rank fragmentation, workspace requirements and communication topology, so "total bytes < total HBM" is necessary but not sufficient. Worked TP=8 example: the 140 GB of weights shard to ~17.5 GB per GPU; the ~64 GB runtime/NCCL reserve is per-host (not per-rank); the ~436 GB KV budget shards to ~54.5 GB per GPU; and under tensor-parallel attention the per-request KV (24.9 GB) also shards across the 8 ranks, so the per-rank KV per request is ~3.1 GB. The 17.5 concurrent figure is therefore the *aggregate* bound — a rank can be the binding constraint even when the aggregate fits, so per-rank fit and sharding must be validated separately (Chapters 9–10). Byte-accurate, 436 ÷ 24.9037 = 17.51, so the conservative integer "requests that fit" floor is 17, not 18.
 
--- a/chapter-15/chapter-15.md
+++ b/chapter-15/chapter-15.md
@@ -45,3 +45,3 @@
 
-![Fig 15.2 — Prefix caching and batching act on different serving phases: caching reduces prefill work per repeated prompt; batching raises decode goodput. Illustrative (synthetic) curves, not measured benchmarks — left = prefill work vs average prefix reuse (prefill work, lower is better); right = decode goodput vs batch size (rises until HBM bandwidth saturates). Left uses percent of no-cache prefill work; right uses arbitrary goodput units. [ILLUSTRATIVE][ASSUMPTION]](figures/fig-15-1501.png)
+![Fig 15.2 — Two levers, two serving phases: prefix caching cuts prefill work per repeated prompt (left: prefill work vs average prefix reuse, as a percent of no-cache prefill work, lower is better); batching raises decode goodput (right: decode goodput vs batch size, arbitrary goodput units, rising until HBM bandwidth saturates). **Scope:** illustrative (synthetic) curves, not measured benchmarks. [ILLUSTRATIVE][ASSUMPTION]](figures/fig-15-1501.png)
 
--- a/chapter-19/chapter-19.md
+++ b/chapter-19/chapter-19.md
@@ -203,3 +203,3 @@
 
-![Fig 19.2 — Per-request tokens and FP16 KV cache climb linearly with agent turns, from 24.9 GB single-shot to 34.0 GB at four turns. Assumption: an append-only bounding case where each column is a counterfactual completion (9,200 input + 300 output + 800 + 65 per turn), status [DERIVED] from Ch 19 arithmetic. Caveat: a production stack that compacts or prefix-caches can hold this flat.](figures/fig-19-1902.png)
+![Fig 19.2 — Agent turns: token and KV growth. Per-request tokens and FP16 KV cache climb linearly with agent turns, from 24.9 GB single-shot to 34.0 GB at four turns. Assumption: an append-only bounding case where each column is a counterfactual completion (9,200 input + 300 output + 800 + 65 per turn), status [DERIVED] from Ch 19 arithmetic. Caveat: a production stack that compacts or prefix-caches can hold this flat.](figures/fig-19-1902.png)
 
@@ -207,3 +207,3 @@
 
-![Fig 19.3 — The agentic context block stacks an initial prompt, cumulative tool output and reasoning, and a fixed final answer, lifting FP16 KV 24.9 → 34.0 GB. Assumption: a strict append-only policy where each column is a counterfactual completion (I0 9.2K, delta 800, gamma 65, O 300 per turn), status [ILLUSTRATIVE][DERIVED]. Caveat: compaction, truncation or prefix caching can hold KV flat or shrink it.](figures/fig-19-1903.png)
+![Fig 19.3 — Agent context and compaction. The agentic context block stacks an initial prompt, cumulative tool output and reasoning, and a fixed final answer, lifting FP16 KV 24.9 → 34.0 GB. Assumption: a strict append-only policy where each column is a counterfactual completion (I0 9.2K, delta 800, gamma 65, O 300 per turn), status [ILLUSTRATIVE][DERIVED]. Caveat: compaction, truncation or prefix caching can hold KV flat or shrink it.](figures/fig-19-1903.png)
 
--- a/chapter-27/chapter-27.md
+++ b/chapter-27/chapter-27.md
@@ -82,3 +82,3 @@
 
-![Fig A.2 — Vendor-reported percentages remaining relative to each model's own reference, not a shared baseline. GLM's rows are per-layer/per-head scope, not total FLOPs or total cache; no predecessor row exists for Kimi K3 or Qwen3.8-Flash-Next. [1P][DERIVED] Sources: DeepSeek V4 arXiv:2606.19348; Z.ai GLM-5.3-Flash release article, 2026-08-26.](figures/fig-27-2704.png)
+![Fig A.2 — Vendor-relative KV/compute ratios. Vendor-reported percentages remaining relative to each model's own reference, not a shared baseline. GLM's rows are per-layer/per-head scope, not total FLOPs or total cache; no predecessor row exists for Kimi K3 or Qwen3.8-Flash-Next. [1P][DERIVED] Sources: DeepSeek V4 arXiv:2606.19348; Z.ai GLM-5.3-Flash release article, 2026-08-26.](figures/fig-27-2704.png)
 
@@ -154,2 +154,4 @@
 
+> **Source-index landing (version-pinned) — how every `[A-S#]` key resolves.** One rule: `[A-S23]` → pinned source-ledger entry 23. The ledger is the repository file `review/publication_v2_20261028/audit/source-verification.md`, read at this edition's immutable revision `27f4cd571d53ecb2ac549d5825a77c87f8736ad3`; the permalink below opens exactly that file at exactly that revision, and every `[A-S01]`–`[A-S105]` key cited in this edition resolves there: https://github.com/zhiqitao/from-token-to-fleet/blob/27f4cd571d53ecb2ac549d5825a77c87f8736ad3/review/publication_v2_20261028/audit/source-verification.md. The revision is pinned, so the address does not drift as the repository advances; the same repository path on the default branch carries any later edition's ledger.
+
 ### Architecture dimensions and executed depth — 2026-10-28 {.unnumbered}
```
