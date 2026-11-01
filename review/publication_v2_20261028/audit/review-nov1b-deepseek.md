---
# FTF-NOV1B-DEEPSEEK — 2026-11-01 评审 P1-01（ch27 Appendix A，PDF pp~391/395：DeepSeek V4-Pro 服务状态）修复证据

- 所有权（仅此）: `design/manuscript/chapter-27/chapter-27.md`（`:7` 服务状态 caveat、`:63` A.3 段）、本证据文件。`chapter-19` 复查 = **0 处复用**（不改）；渲染器 / 根目录 / 全书构建 / git / 委派 均未动。
- 修复前快照: `~/.hermes/profiles/muta/cache/scratch/ch27_before.md`；完整 before/after diff 见文末附录（同 `scratch/ch27_p1_01.diff`）。

## 官方核验（检索日 2026-11-01）

| # | 来源 | URL | 检索日 | 关键原文（verbatim） |
|---|---|---|---|---|
| 1 | API Change Log，2026-09-10 条目（现行） | https://api-docs.deepseek.com/updates/ | 2026-11-01 | "The previous-generation models V4 Flash and V4 Flash Vision Exp have been retired; for compatibility, the model names deepseek-v4-flash and deepseek-v4-flash-vision-exp are temporarily routed to V4.1 Flash." |
| 2 | 同上，V4-Pro 现行状态 | https://api-docs.deepseek.com/updates/ | 2026-11-01 | "In response to user demand, we have decided to continue providing API services for DeepSeek V4 Pro after September 14, 2026, with the billing method remaining unchanged. We will provide further notice should there be any changes." |
| 3 | 2026-09-10 发布公告（被取代的原句） | https://www.deepseek.com/en/news/deepseek-v4-1-flash/ | 2026-11-01 | "Starting at 04:00 UTC on Sept 14, 2026, all deepseek-v4-pro requests will route to V4.1-Flash at V4.1-Flash rates. This will continue until V4.1-Pro launches."（同页: "V4-Flash & V4-Flash-Vision-Exp are retired. For compatibility, deepseek-v4-flash and deepseek-v4-flash-vision-exp temporarily route to V4.1-Flash."） |

**判定**
- **(a) 确认**：V4-Flash / V4-Flash-Vision-Exp 退役 + 两别名临时路由到 V4.1-Flash —— change log 与公告一致，现行 change log（检索日 2026-11-01）复核通过。
- **(b) 确认（R33 caveat 错）**：V4-Pro **未**迁走。公告的 09-14 路由句被现行 change log **取代**（announcement → superseding service-status correction）：09-14 之后继续提供 V4-Pro API，计费方式不变，变更将另行通知。
- **不混淆**：V4-Flash *别名路由* 是 API 名字兼容问题；V4-Pro *可用性* 是另一条服务事实 —— 两处正文均已显式切开（"must not be read as covering it" / "says nothing about V4-Pro's availability"）。
- **状态: CLOSED / VERIFIED（非 OPEN）** —— 现行 change log 表述明确（continue + billing unchanged + "further notice"），其后最新条目（2026-10-17）未再改动 V4-Pro；公告页仍留有被取代的原句，但 change log 是现行 API 服务状态的权威渠道，取代关系清楚，故不判歧义。**检索日 2026-11-01**；若后续 change log 发布 "further notice" 再动 V4-Pro，须重验。

## P1-01（RED → AFTER）

### 1. 服务状态 caveat（`:7`）

**RED（R33 原文要点）**
> **Service-status caveat (dated 2026-09-10 / 2026-09-14) — the August snapshot's DeepSeek variant names are no longer served as named.** … and that from **04:00 UTC on 2026-09-14** all `deepseek-v4-pro` requests route to **V4.1-Flash at V4.1-Flash rates**, until V4.1-Pro launches. [1P] — … (retrieved 2026-10-31) …

问题：(i) 标题 "no longer served as named" 把 V4-Pro 一并算作不再按名服务；(ii) 把公告的 09-14 路由句写成现行状态，只追踪了 2026-09-10 公告，未对现行 change log 复核；(iii) 未区分 V4-Flash 别名路由与 V4-Pro 可用性；(iv) 无 2026-11-01 复核日期、无 change log 来源。

**AFTER（要点）**：标题改为 "…the Flash names are no longer served as named, **but V4-Pro still is** (re-verified 2026-11-01)"；Flash 退役/别名路由标注 **confirmed by the current API change log (retrieved 2026-11-01)**；公告 09-14 路由句标注 **superseded** 并引 change log 原文（"decided to continue providing API services for DeepSeek V4 Pro after September 14, 2026, with the billing method remaining unchanged"）；显式句 "That V4-Flash *alias* routing is a separate fact from V4-Pro's availability and must not be read as covering it"；来源新增 change log（retrieved 2026-11-01），原 news/news260910（retrieved 2026-10-31）保留；段末 "This is a service/routing status, not a correction of the snapshot" 与 8 月冻结比较句、2026-10-28 指路句**原样保留**。

### 2. A.3 段（`:63`）

**RED**
> … V4-Flash and V4-Flash-Vision-Exp are retired (routed to V4.1-Flash) **and V4-Pro requests route to V4.1-Flash**. …

**AFTER**
> … V4-Flash and V4-Flash-Vision-Exp are retired (their API names temporarily route to V4.1-Flash), **while V4-Pro remains available**: the 2026-09-10 announcement that all `deepseek-v4-pro` requests would route to V4.1-Flash from 2026-09-14 was superseded by DeepSeek's current API change log, which decides to continue V4-Pro API service after 2026-09-14 with the billing method unchanged (change log retrieved 2026-11-01). The V4-Flash alias routing says nothing about V4-Pro's availability — the two are separate service facts. …

段末 "[1P] figures … historical record of what DeepSeek reported by 2026-08-30" 与 "2026-10-28 V4.1-Flash note" 指路句原样保留；标题加 "re-verified 2026-11-01"。

## sha256（before → after）

| 文件 | before | after |
|---|---|---|
| `design/manuscript/chapter-27/chapter-27.md` | `0392931404eb55be700148f9a1ad4e2c42b83d0c51171e48cfdb953ce74ee883`（65,196 B） | `1188ca6c494482afbe239eb9925bab9119e4eedae6da73dc2218b712ba0008e1`（66,555 B） |

## 定向复用搜索（service-alias / V4-Pro 路由主张）

- `design/manuscript/` 全域 grep（`V4-Pro|V4-Flash|deepseek-v4|service-alias|route to V4.1-Flash|V4.1-Flash rates|2026-09-14`）: 活稿命中**仅 ch27 `:7` / `:63`**（均已改）；**`chapter-19` = 0 处**，不重复该主张 ⇒ 无需改。
- 全仓库同义改写 grep（`(rout|alias|retir|phase).*v4-pro`）: 除上述两行外无其他活稿命中。
- 其余命中均为非活稿、非本任务所有权，未改：`render/build/_book_reflowable.md`（`:4930`/`:4986` 旧文 = 构建产物）、`render/latex/_md/ch27.md`（陈旧构建产物，连 R33 caveat 都未含）、`review/.../work/accelerated_external_review_proof_r33/`（R33 冻结 proof 快照 = 历史）、`research/model-trends-20261028/sources/`（第一方原始材料，非本书主张）。

## 验证（实测）

1. **diff 行数**: 恰 **2 行改**（`:7`、`:63`），2 删 / 2 增；其余 373 行逐字节不变（65,196 → 66,555 B，+1,359 B 全在两行内）。
2. **8 月冻结主张未动**: "Appendix verified through 2026-08-30"、"1.6 T total / 49 B"、"284 B / 13 B"、Fig A.1/A.2、A.10 硬边界句、四家族列表 —— 全部位于未改行。
3. **日期/来源齐备**: 两处均带检索日 2026-11-01 + change log URL；公告句保留 retrieved 2026-10-31；`04:00 UTC` / `2026-09-14` / `V4.1-Flash rates` 等原数字在"被取代的公告句"语境中逐字保留。
4. **约束遵守**: 未改渲染器/根目录、未全书构建、未 git、未委派；临时文件在 scratch/TMPDIR。

## OPEN

1. **构建产物过期（非本任务所有权）**: `render/build/_book_reflowable.md`、`render/latex/_md/ch27.md` 仍是旧服务状态文本（后者甚至缺 R33 caveat）—— 属渲染器输出，需下次全书构建刷新；本任务按约束未动。
2. **公告页未同步**: https://www.deepseek.com/en/news/deepseek-v4-1-flash/ 至检索日 2026-11-01 仍保留被取代的 09-14 路由原句 —— 已按"公告 → 现行 change log 取代"处理并在正文注明双来源与检索日；当前状态判 CLOSED，若评审认定两官方页并存即为歧义，可据本条降级为 OPEN（检索日 2026-11-01）。

## 附录：before/after diff（`diff -u`，2026-11-01）

```diff
1|--- /home/ubuntu/.hermes/profiles/muta/cache/scratch/ch27_before.md	2026-11-01 01:08:09.674059392 -0700
2|+++ design/manuscript/chapter-27/chapter-27.md	2026-11-01 01:11:14.030555966 -0700
3|@@ -4,7 +4,7 @@
4| 
5| > **Appendix verified through 2026-08-30 (source snapshot compiled through 30 August 2026).** This appendix is a snapshot of the frontier as of that date, compiled from the first-party technical reports and model cards listed in A.10 (First-hand Sources). The models, their parameter counts, constants, and claims are vendor-reported and move quickly. **This is a hard boundary for the four-family comparison and the First-hand Sources list: nothing released after 2026-08-30 is reflected in either, and model specifications and vendor claims should be reverified against the cited first-party sources before any procurement or deployment decision — and once more immediately before publication, because these are among the fastest-changing values in the book.** (The 2026-09-27 observation in A.6 and the separately dated 2026-10-28 technology notes are outside this compile envelope and are not part of the four-family comparison.) It illustrates how to apply the framework to a changing frontier; it is **not** a current model leaderboard.
6| 
7|-> **Service-status caveat (dated 2026-09-10 / 2026-09-14) — the August snapshot's DeepSeek variant names are no longer served as named.** DeepSeek announced on **2026-09-10** that **V4-Flash and V4-Flash-Vision-Exp are retired**, with `deepseek-v4-flash` and `deepseek-v4-flash-vision-exp` temporarily routed to **V4.1-Flash** for compatibility; and that from **04:00 UTC on 2026-09-14** all `deepseek-v4-pro` requests route to **V4.1-Flash at V4.1-Flash rates**, until V4.1-Pro launches. [1P] — DeepSeek, "Introducing DeepSeek-V4.1-Flash" (2026-09-10): https://www.deepseek.com/en/news/deepseek-v4-1-flash ; API release note: https://api-docs.deepseek.com/news/news260910 (retrieved 2026-10-31). **This is a service/routing status, not a correction of the snapshot.** The 2026-08-30 four-family comparison, its figures (Fig A.1, A.2) and its First-hand Sources list stay exactly as compiled — the historical record of what the vendor reported by the cutoff, with nothing released after 2026-08-30 folded into them (boundary above). For what now answers those routes, read the 2026-10-28 technology note on `deepseek-ai/DeepSeek-V4.1-Flash` ("Phase and storage tier matter"); it sits outside the four-family comparison for the same reason.
8|+> **Service-status caveat (dated 2026-09-10 / 2026-09-14; re-verified 2026-11-01) — of the August snapshot's DeepSeek variant names, the Flash names are no longer served as named, but V4-Pro still is.** DeepSeek announced on **2026-09-10** that **V4-Flash and V4-Flash-Vision-Exp are retired**, with `deepseek-v4-flash` and `deepseek-v4-flash-vision-exp` temporarily routed to **V4.1-Flash** for compatibility — **confirmed by the current API change log (retrieved 2026-11-01)**. That V4-Flash *alias* routing is a separate fact from V4-Pro's availability and must not be read as covering it. The same 2026-09-10 announcement also said that from **04:00 UTC on 2026-09-14** all `deepseek-v4-pro` requests would route to **V4.1-Flash at V4.1-Flash rates**, until V4.1-Pro launches — **that sentence is superseded**: DeepSeek's current API change log states that "in response to user demand, we have decided to continue providing API services for DeepSeek V4 Pro after September 14, 2026, with the billing method remaining unchanged," with further notice should there be any changes. So the announcement → superseding service-status correction runs: V4-Flash/V4-Flash-Vision-Exp retirement stands; **V4-Pro did not route away and remains served under its own name and billing**. [1P] — DeepSeek API Change Log, 2026-09-10 entry: https://api-docs.deepseek.com/updates/ (retrieved 2026-11-01); announcement, DeepSeek, "Introducing DeepSeek-V4.1-Flash" (2026-09-10): https://www.deepseek.com/en/news/deepseek-v4-1-flash ; API release note: https://api-docs.deepseek.com/news/news260910 (retrieved 2026-10-31). **This is a service/routing status, not a correction of the snapshot.** The 2026-08-30 four-family comparison, its figures (Fig A.1, A.2) and its First-hand Sources list stay exactly as compiled — the historical record of what the vendor reported by the cutoff, with nothing released after 2026-08-30 folded into them (boundary above). For what now answers those routes, read the 2026-10-28 tec... [truncated]
9| 
10| **The four families at a glance (the scope of this appendix).** The four-family comparison that this appendix's figures (Fig A.1, A.2) and its First-hand Sources list (A.10) rest on comprises **exactly these four open-weight frontier MoE families — and only these four**:
11| 
12|@@ -60,7 +60,7 @@
13| 
14| **What this means for the architect (ties to Ch7 Memory, Ch8 Compute).** In our reading of the vendor reports, this is a strong confirmation that *KV-per-token is a moving target*. Chapter 7's arithmetic (per-token × context) is a floor for a given architecture; DeepSeek shows the *constant factor itself* can be cut ~10× without changing the model's parameter count. The architectural decision shifts from "how much KV memory does this context need?" to "which KV scheme does this model use, and is its vendor-published saving reproducible on my serving stack?"
15| 
16|-**Service status (dated, outside the snapshot).** These variant names have moved since the cutoff: see the 2026-09-10 / 2026-09-14 service-status caveat at the top of this appendix — V4-Flash and V4-Flash-Vision-Exp are retired (routed to V4.1-Flash) and V4-Pro requests route to V4.1-Flash. The [1P] figures above remain the historical record of what DeepSeek reported by 2026-08-30; the successor's constants are in the 2026-10-28 V4.1-Flash note.
17|+**Service status (dated, outside the snapshot; re-verified 2026-11-01).** These variant names have moved since the cutoff: see the 2026-09-10 / 2026-09-14 service-status caveat at the top of this appendix — V4-Flash and V4-Flash-Vision-Exp are retired (their API names temporarily route to V4.1-Flash), **while V4-Pro remains available**: the 2026-09-10 announcement that all `deepseek-v4-pro` requests would route to V4.1-Flash from 2026-09-14 was superseded by DeepSeek's current API change log, which decides to continue V4-Pro API service after 2026-09-14 with the billing method unchanged (change log retrieved 2026-11-01). The V4-Flash alias routing says nothing about V4-Pro's availability — the two are separate service facts. The [1P] figures above remain the historical record of what DeepSeek reported by 2026-08-30; the successor's constants are in the 2026-10-28 V4.1-Flash note.
18| 
19| ## 2. Kimi K3 — Vendor-Reported First Open 3T-Class Model, and the MoE-Sparsity Extreme
20| 
```
