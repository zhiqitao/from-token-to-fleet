# review-nov1-p2 — 2026-11-01 评审 P2-07 / P2-08 / P2-09 / P2-10 / P2-11 / P2-12 / P2-13 处置证据

评审输入：2026-11-01 publishing-readiness review P2 条目（父任务转述）。
范围：仅 `design/manuscript/*.md` 6 个文件 + 2 个图生成器及其产物（Fig A.2、Fig 19.3）+ 本证据文件。
**未**改 renderer/根配置、**未**做全书构建、**未** commit、**未**动 `render/latex/*`、`render/build/*`。
本批除 Fig A.2 / Fig 19.3 重生成外均为 source-only；**所有文字项需 PDF 重建才能最终验证**（见 §9）。

> 并发说明：处置期间工作区同时被其他 agent 修改（`chapter-03/15/16/17/20/22` 与 `fig-03-0301.*` 均有他人改动），
> 因此**文件级 sha 非本任务独占**；逐条 before/after 片段才是本任务的权威记录。

---

## 1. P2-07 — 两处指向 spine 环的 "Fig 1.1" 改为动态引用

**核验**：`design/manuscript` 中指向 *Validate & Defend → Commit* 的 `(Fig 1.1)` 恰好 2 处：
`chapter-16.md:195`（§16.6 决策态框）与 `chapter-17.md:199→207`（§16.7 决策态框）。
**偏差记录**：评审写作 "Ch16 p~263 / Ch20 p~280"，但 `chapter-20.md` 全文无 `1.1`、无 spine 环引用；
第二处实际在 **Ch17**（两处均由 2026-10-31 修复引入，见 `audit/review-oct31-sla-source.md` L106/L123）。
按"两处"处置，Ch20 无需改动。`chapter-01.md:49` 的 Fig 1.1（KV cache）保持不动。

**动态引用机制（不硬编码数字）**：`render/latex/preface.tex:114` 定义 `\label{fig:spine-loop}`，
`render/latex/book.tex:64` 在章节（L71+）之前 `\input{preface}`，
`render/latex/build/book.aux` 实测：`\newlabel{fig:spine-loop}{{1}{ii}{The architect's decision loop --- the book's spine…}`
→ `\ref` 解析为 **1**，即 Preface 的 Figure 1（decision loop）。

```diff
- …stages (Fig 1.1) or as a committed ADR (Ch 22 → Ch 25)…      # chapter-16.md:195
+ …stages (Fig \ref{fig:spine-loop} — the Preface's decision-loop figure) or as a committed ADR (Ch 22 → Ch 25)…

- …stages (Fig 1.1), and no mode is selected on least cost…      # chapter-17.md:199
+ …stages (Fig \ref{fig:spine-loop} — the Preface's decision-loop figure), and no mode is selected on least cost…
```

**已验证**：按渲染器同参数逐章 pandoc（`markdown+pipe_tables+fenced_code_blocks-yaml_metadata_block` → latex）
+ `md_to_latex.fix_crossrefs()`：两章 tex 各含 1 个 `\ref{fig:spine-loop}`，**未被** `Fig X.Y` 的 hyperref 规则误包
（该规则要求 `\d+\.\d+`）。HTML 侧（`make_html.py` 纯 pandoc）会丢弃 raw LaTeX，降级为
`stages (Fig — the Preface's decision-loop figure)` —— 语句仍可读，数字只在 PDF 出现（见 §9）。

## 2. P2-09 — Ch22 "metered unit of thought"

```diff
- The architect treats a token as a metered unit of thought — the way a kilowatt-hour meters electricity …   # chapter-22.md:11
+ The architect treats a token as a metered unit of model I/O and accounting — the way a kilowatt-hour meters electricity …
```
其余句子、数字、限定词未动。Ch1 原文（`chapter-01.md:55` "metered unit of model I/O … not a unit of thought"）未改，
两章现在一致；全书 `metered unit of thought` 计数 = 0。

## 3. P2-10 — Fig A.2 警示带（唯一重生成项之一）

`render/fig_ch27_norm.py`：

```diff
- ax.add_patch(Rectangle((60, T-70), W-120, 34, fc='white', ec='black', lw=2.5, hatch='///', zorder=1))
- ax.text(W/2, T-44, 'NOT A CROSS-MODEL PERFORMANCE RANKING', fontsize=FS_R-0.2, color='#c0392b', fontweight='bold', …)
- ax.text(W/2, T-62, "Each figure is relative to that model's OWN stated baseline — no shared scale", fontsize=FS_R-0.6, color='#c0392b', …)
+ ax.add_patch(Rectangle((24, T-70), W-48, 34, fc='white', ec='#8b1e13', lw=2.2, zorder=1))   # 实心白底 + 单一深红边框，无 hatch
+ ax.text(W/2, T-44, 'NOT A CROSS-MODEL PERFORMANCE RANKING', fontsize=FS_R+2.2, color='#8b1e13', fontweight='bold', …)  # 8.6 → 11.0 pt
+ ax.text(W/2, T-62, "…OWN stated baseline — no shared scale", fontsize=FS_R+0.2, color='#8b1e13', …)                    # 8.2 → 9.0 pt
```
带宽由 `W-120` 加宽到 `W-48`，两行文字均在带内（视觉核验：无溢出、无重叠）。
重生成 `fig-27-2704.png` + `.pdf`（pdf mtime ≥ png，构建会取 pdf）。
**vision 复核**：*"no hatching … solid light/white fill … single, continuous dark‑red border … heading line is large, bold, high‑contrast … no overflow or overlap."*

## 4. P2-08 — Ch16 启动 mini-case "only one term can flip" 改为条件式

```diff
- The token arithmetic therefore does not send this startup to the API; it points to self-hosting. Only one term can flip the decision: the *opportunity* cost of the GPU-ops time the two servers consume — the better part of the only engineer the startup can spare.
+ The token arithmetic therefore does not send this startup to the API; it points to self-hosting. Within this equal-capability assumption set, the only remaining **MODELED** term that can flip the decision is the *opportunity* cost of the GPU-ops time the two servers consume — the better part of the only engineer the startup can spare (the hypothetical 0.5-FTE label priced above). This is a statement about the model, not about the decision: quality parity, peak throughput, SLO-goodput, regional availability, burst behavior, procurement lead time, resilience and capital outlay are all decision-relevant too, and none of them is priced in this mini-case — any of them can flip the real decision from outside the assumption set.
```
保留：`~$64K/month`、`$770K/year`、0.5-FTE 标签（全章 `0.5-FTE` 计数仍为 2，未改写 §8 前文定价）。
8 个 decision-relevant 词全部出现（quality parity / peak throughput / SLO-goodput / regional availability / burst / procurement / resilience / capital）。

## 5. P2-11 — Ch4 Table 4 预算格 + 侧栏；Fig 16.1 三分

**Ch4 预算格**（`chapter-04.md:79`）：
```diff
- > | Monthly budget | ~$15,000 (illustrative *per-host* ceiling: one 8×H100 host at ~$20/hr × 730 hr ≈ $14.6K/mo. Note this is a **single host**… 6–21 hosts… ~$87.6K–$306.6K/mo ($87,600 ≈ $14.04/1K … $306,600 ≈ $49.13/1K … $155,816.93/mo ≈ $24.97/1K …) … |
+ > | Monthly budget | ~$15,000 *(illustrative cap; not full workload budget — see the sidebar below)* |
```
**新增带题侧栏**（紧接 canonical box 之后、Availability-topology 段之前）：`**Sidebar — what the ~$15,000 budget line is, and the 6–21-host workload comparison.**` + 4 行紧凑表
（cloud 6 hosts $87,600 ≈ $14.04/1K；self-host 21 hosts $155,816.93 ≈ $24.97/1K；cloud 21 hosts $306,600 ≈ $49.13/1K；参考行 one host ~$14.6K）。
**数字保全核验**：旧格 22 个数字 token 在"新格 + 侧栏"中全部命中（脚本比对，MISSING = []）。

**表标签安全性**：逐章跑 `fix_crossrefs()`，Ch4 未命名 longtable 标签由 `4.3,4.4,4.5,4.6` 变为 `4.3,4.4,4.5,4.6,4.7`（新侧栏取 4.4）。
全书正文只引用 `Table 4-1` / `Table 4-2`（grep：3 / 54 次，无 4-3+），故无 `\hyperref` 指向被平移的标签 → 无断链。
math span 数量 HEAD=20、改后=20（无 `$…$` 误解析新增）。

**Fig 16.1**（`chapter-16.md:203/205`，**未**改生成器 `render/fig_ch16_tco.py`，不在本批授权的生成器清单内）：
```diff
- ![Fig 16.1 — **Takeaway:** … **Scope/provenance/status:** … **Caveat:** …]
+ ![Fig 16.1 — **Three essential claims.** (1) …crosses the managed API at ~7.5M… above the API. (2) crossover 是需求的函数、cloud 为单点 marker 非线. (3) feasible bound 24.96M req/mo (40 rps × 624,000)… **Scope:** … [ILLUSTRATIVE][DERIVED]. **Caveats — sensitivity/feasibility:** … the sensitivity span and the feasibility reconciliation are worked out in the body text below.]
- *Break-even: monthly cost vs monthly volume … ~6.2–10.4 M … $15–25/1K … ~7.5 M mid-point … frozen-fleet crossover …*   # 斜体二级图注
+ **Reconciliation for Fig 16.1 — sensitivity (price band) and feasibility (the bound).** …（同一批数字，改为正文段落）
```
caption 只留 3 条 essential claims + scope + caveat；详细 reconciliation（6.2–10.4M 区间、$15–25/1K、$155,816.93 ÷ $0.0208、frozen-fleet、star/span/bound/shading）全部下沉正文。
**未做**"2 panels"变体（需改 Fig 16.1 生成器，超授权）；caption+正文路线已满足"分离 claims 与 caveats"。

## 6. P2-12 — Figs 19.2 / 19.3 去重（选评审给的第 2 方案：19.3 改为独立的策略对比）

**范围说明**：任务书写的是 "19.2/19.3 if merged"，但评审条文同时允许 "give 19.3 a distinct policy comparison"；
该方案**必然**要改 19.3 的生成器，故按条文授权改写 `render/fig_ch19_accum.py`（未删除任何图/资产/编号，交叉引用零平移）。

- `chapter-19.md:200`：`(Fig 19.2/19.3)` → `(Fig 19.2)`，段末新增 "Fig 19.3 then compares that bounding case with the compaction and cache-policy levers named above…"
- `chapter-19.md:208` caption 改为策略对比；`chapter-19.md:210` 斜体图注改为正文段 `**Three policies, three different levers.**`
- 生成器重写为 3 条水平条：Append-only **34.0 GB**（+36% vs 24.9，[DERIVED]）/ Compaction **≈24.9 GB**（held roughly flat，[ILLUSTRATIVE]）/ Prefix-cache eviction **34.0 GB (unchanged)**（只动 cached-prefix 内存与 re-prefill，[ILLUSTRATIVE]）；24.9 单发参考虚线；底部保留
  `counterfactual: each bar = a separate completed request after 4 turns (one final 300-token answer) — not an intermediate state of a live agent.`
  与 `append-only total = I₀ + T·δ + T·γ + O_final @ 2.62 MB/token (I₀=9.2K, δ=800, γ=65, O=300)`。
- 数字/限定词全部来自既有文本（24.9 / 34.0 / +36% / 9,200 / 300 / 800 / 65 / 2.62 MB），两条非 append-only 条明确标 [ILLUSTRATIVE]。
- 重生成 `fig-19-1903.png` + `.pdf`（新增 pdf 保存，避免旧 pdf 因 mtime 被构建优先采用）。
- **vision 复核**：三标签、三数值、底部 4 行注释全部完整可读，无裁切/无文字重叠（仅虚线穿过注释行，不影响识读）。

## 7. P2-13 — Appendix A 服务状态 caveat（不改 8 月历史主张）

`chapter-27.md` 在 "Appendix verified through 2026-08-30" 边界块之后新增带日期 blockquote，并在 §1 DeepSeek-V4 段末加一句指路：

> **Service-status caveat (dated 2026-09-10 / 2026-09-14) …** DeepSeek 于 **2026-09-10** 宣布 **V4-Flash 与 V4-Flash-Vision-Exp 退役**，
> `deepseek-v4-flash` / `deepseek-v4-flash-vision-exp` 临时路由到 **V4.1-Flash**；自 **2026-09-14 04:00 UTC** 起所有 `deepseek-v4-pro` 请求
> 路由到 **V4.1-Flash 并按 V4.1-Flash 费率**（直至 V4.1-Pro 上线）。[1P]
> https://www.deepseek.com/en/news/deepseek-v4-1-flash （2026-09-10）；https://api-docs.deepseek.com/news/news260910 （retrieved 2026-10-31）。
> **这是服务/路由状态，不是对快照的更正**：2026-08-30 四家族比较、Fig A.1/A.2 与 First-hand Sources 保持原样；
> 现由谁承接这些路由 → 指向 2026-10-28 技术注记 `deepseek-ai/DeepSeek-V4.1-Flash`（"Phase and storage tier matter"）。

**核验**：两个日期与两条事实均由第一方页面确认（DeepSeek news + API change log，检索于 2026-10-31）；
`V4-Flash 284 B / 13 B activated`、`Appendix verified through 2026-08-30` 等 8 月主张逐字未动；新来源**未**并入 A.10（硬边界保持）。

## 8. sha256（before = 本任务开始时；after = 处置完成）

| 文件 | before | after |
|---|---|---|
| `design/manuscript/chapter-04/chapter-04.md` | `956544676f6db88ba1a4b43b4804cebd3a6f32c5347df8c730d25d3c76c94385` | `a891632dbf81159a9e021efd1d3ed0071e9150aba22df20fe2128aa0b8b4863a` |
| `design/manuscript/chapter-16/chapter-16.md` | `1b164fe05fb3de0d8dd28ef3a1d1a95a0618baf88d7cd29ca202d1c868ce1dc4` | `cfa7da083567031458a2ecfda0afe87576cf931bebdf288ab5cbb6bf517c22b8` |
| `design/manuscript/chapter-17/chapter-17.md` | `f9d70faa84c47aa96f1ff0188b8bfc3cbdb981a8a176cca897ee194347743d2c` | `055ac6af36ae46776785db6c0b267b9fa31c43fb590d4fd5c96151155f5f6c58` |
| `design/manuscript/chapter-19/chapter-19.md` | `92980040a6214da0b030e31bec173b6ad19ae1b6eefee4eb8673979b6ed2090f` | `56fd9b539c8c69f6867221f46dba61c88aa0406a6d962bdd76c445cb6bfa46c6` |
| `design/manuscript/chapter-22/chapter-22.md` | `fbbd9397fb3944e2b3c21b5e5746c6f5ffde2f496ea1f7f7d395ef362ab14779` | `44dc1ab407e8da1957463428eacac3b0de492a3ffeebc143bfab365ad5083d0d` |
| `design/manuscript/chapter-27/chapter-27.md` | `18e77cdbb6bd089e36eccf80f256ca80e700b0e88337a58f4da0c21c35c42d28` | `0392931404eb55be700148f9a1ad4e2c42b83d0c51171e48cfdb953ce74ee883` |
| `render/fig_ch27_norm.py` | `f8f2db755cf5a1f2345743d10d5fe4122b2fb142ecf6c6ec0463b4c714675f39` | `26374876035e38ff8ecbc9a9a710aac25ee9ca4df16875533db6b0b536644fd5` |
| `render/fig_ch19_accum.py` | `036ca27bd74e9f2fcb42ff0b02c679da5918f40d43dc13fd578787f0a69cbf45` | `65a3663bb9d73957a5a9097ad2bfad563ceff15742f20596bf05df754542298a` |
| `design/manuscript/chapter-27/figures/fig-27-2704.png` | `ab741197d681f68d943415035ab2f957fe87fbbe54e466b59d2bc413b6e0f5aa` | `7c5a9e29c9fe3e517423b2e07bdc5409e814893ef8c7c3861ce7cfeb77df746a` |
| `design/manuscript/chapter-27/figures/fig-27-2704.pdf` | `5ed876948d60ee08330716bee8bc5155c34c1a14616f9755c925f0bf7976ef7e` | `bbce035121590df921136272b35152239586eaaa415fb093331c7ff492c47999` |
| `design/manuscript/chapter-19/figures/fig-19-1903.png` | `610527f6c0478edc554c79eb8fae83b502158c4e60de5c1e8345e1bf024a25dc` | `72059d4611b7bebd3395a24afe5a08442ee8128e05c73f1f8bb1d0a71e366e71` |
| `design/manuscript/chapter-19/figures/fig-19-1903.pdf` | `b947e8fcc28c17e7bccf258421c19e5568f4319e7131558ebb72c634ff5f8674` | `559cd6fc29e53d24c719a23d5332032340595a9c496565a539da5ac279b216f0` |

## 9. 需重建才能验证 / OPEN

1. **全部文字项（P2-07/08/09/11/12 文案/13）需 PDF 重建**：本批只做了逐章 pandoc + `fix_crossrefs` 的源级验证，未跑全书构建（按任务禁令）。
2. **P2-07 的 `\ref` 只在 PDF 生效**：`book.aux` 已证明解析为 `1`，但需重建确认排版与超链；HTML 复核构建会显示 `Fig — the Preface's decision-loop figure`（数字缺失但语句可读）。若要求 HTML 也出数字，需改 `render/make_html.py`（renderer，超本批授权）→ **OPEN（跨批）**。
3. **P2-11 Fig 16.1 只改了 caption + 正文**：评审的 "(or 2 panels)" 变体未做，需改 `render/fig_ch16_tco.py`（不在授权生成器清单）→ 若评审坚持图内分栏，**OPEN（需授权/重建）**。
4. **P2-12 采用"独立策略对比"而非"合并"**：因此未删图、未改编号；若父任务坚持 merge 方案，需回退本条并改 `fig_ch19_trend.py` + 删 19.3 资产 → 见 §6 范围说明。
5. **P2-10 / P2-12 资产已重生成并 vision 通过**，但仍需在全书构建中确认嵌入尺寸与图注间距（构建会把 png/pdf 拷入 `render/latex/figures/`）。
6. **并发编辑**：`chapter-16/17/22` 同时含其他 agent 的改动，重建前建议先做一次全书 diff 审阅。