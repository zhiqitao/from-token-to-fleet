---
# FTF-NOV1-CH3 — 2026-11-01 评审 Ch3 P1-01 / P1-02 修复证据

- 所有权（仅此）: `design/manuscript/chapter-03/chapter-03.md`、`render/fig_ch3.py`、`design/manuscript/chapter-03/figures/fig-03-0301.{png,pdf}`、本证据文件。其余章节 / 渲染器 / 根目录未改；未做全书构建、未 git、未委派。
- 修复前快照: `~/.hermes/profiles/muta/cache/scratch/ch3_p1_before/`（4 个 `.before`）；文本 diff 存 `scratch/diff_chapter-03.md.diff`、`scratch/diff_fig_ch3.py.diff`。

## sha256（before → after）

| 文件 | before | after |
|---|---|---|
| `design/manuscript/chapter-03/chapter-03.md` | `06f3b7ae6164165d8012534b2f80309937fe841210cdeee7c03e589340a5925c`（40,022 B） | `507ee232ea0ceff0c1c1344a5ca74cffde021dc07afa57e60b726242a42f44f6`（41,632 B） |
| `render/fig_ch3.py` | `c35174e63f165aa845d1dfb2f9c02f558aeb8c61d3fdddb572e6e8e6427f14bd`（5,706 B） | `b2e81c3c21e1724c7e3198e1fd7203ec6462758ea839a258c32f8785c6ba1e03`（6,274 B） |
| `figures/fig-03-0301.png` | `5c5457b8013b6768fcda8ec49dcfa4d0fccd2eaee8d1144358f330e0395483d6`（201,217 B） | `64769d5626440b87ca35f1b7199fa8b358c699652cb2e8b74bcce5f440432220`（216,196 B） |
| `figures/fig-03-0301.pdf` | `d339d5dbfe35054aae474b2b9859f1295d68d7f9cd8ce3d0b84664524adccc5b`（32,293 B） | `8409b040716d806ef6c0da43a86910ca3e673cd66205fcee4b00211a647456e2`（32,698 B） |

## 复算：单一 MoE 参数账本（本章 Table 3-2 / 3-3 / Fig 3.4 / 小案例共用）

输入全部取自本章声明：per-expert 5.7B、8 experts、top-2、always-on 1.4B、dense 70B、FP16 = 2 B/param。

| 项 | 值 | 式 |
|---|---|---|
| expert 质量 | 45.6B | 5.7 × 8 |
| total | **47.0B** | 45.6 + 1.4 |
| active / token | **12.8B** | 2 × 5.7 + 1.4 = 11.4 + 1.4 |
| weights_active | **25.6 GB** | 12.8 × 2 |
| weights_resident（MoE） | **94 GB** | 47 × 2 |
| weights_resident（dense） | 140 GB | 70 × 2 |
| Δ（dense − MoE） | **46 GB = 32.857% ≈ 32.9%** | (140 − 94) ÷ 140 |
| active / total | 27.234% ≈ 27% | 12.8 ÷ 47 |
| 陈旧 "28 GB" 来源 | 14 B × 2 = 28 | 旧 14B-active 账本残留（本章已无 14B-active） |
| KV | **不变** | 同注意力几何 / 同 context / 同 cache dtype |

结论：权重确实下降 46 GB（32.9%），KV 不变 —— 原 VERDICT "does not cut the memory budget / challenger fails" 与自身算术矛盾 ⇒ P1-01 成立。

## P1-01（RED → AFTER）

**RED（:200 原文）**

> On that accounting the MoE challenger fails: it does not cut the memory budget the team asked about, and it would add routing infrastructure — including a GPU dedicated to the routing dispatcher [ILLUSTRATIVE][ASSUMPTION], not a vendor-published requirement — on top. The team therefore keeps the Chapter 2 decision…

问题：(i) 与 :216/:93 的 94 GB / 25.6 GB 自相矛盾（权重降 46 GB = 32.9%）；(ii) 把"专用 dispatcher GPU"写成不可避免成本；(iii) 未在真实布局（单机 vs expert-parallel）上比较就整体否决。

**AFTER（:200 新文本，两 findings + 未决结论）**

> The architect's decision therefore rests on two findings, both stated plainly. **(a) Resident weights do drop:** ~140 GB (dense 70B) → ~94 GB (the ~47B MoE) — 46 GB, ~32.9% of FP16 weight memory — earned by the challenger's smaller total parameter count, not by routing a same-size model. **(b) With the same attention geometry the KV cache is unchanged:** the 9.2K-context budget is provisioned at the dense-model rate (~12 GB at 8-bit, ~24 GB at FP16) either way. What this accounting does *not* settle is whether the challenger is the better system. Routing and expert dispatch are integrated in serving runtimes — vLLM, for example, dispatches experts over all-to-all communication behind a runtime flag ([Expert Parallel Deployment](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)) — so a *GPU dedicated to the routing dispatcher* is an optional design hypothesis [ILLUSTRATIVE][ASSUMPTION], not an unavoidable requirement; the real added cost is placement, and it must be compared on an actual arrangement — on the canonical single 8×H100 host (640 GB, Ch 4 Table 4-2) both 140 GB and 94 GB of FP16 weights fit, so the 46 GB saving buys KV headroom rather than feasibility, while an expert-parallel layout across GPUs trades that headroom for cross-GPU all-to-all traffic (§6). The team therefore does **not** select the challenger yet: quality at equal task performance, placement on the actual single-host or expert-parallel arrangement, and measured service goodput under the target workload remain unresolved [UNRESOLVED]. The Chapter 2 dense 70B decision stands as the provisional choice, and the KV cache budget is provisioned at the dense-model rate either way.

**同向一致性修复（同文件、同 finding 类）**

- `:198` 小案例回答段：删 "does **not** automatically reduce the weight-residency floor"，改为明写 94 GB vs 140 GB = −46 GB / −32.9%，并点明降幅来自 *total* 更小（同 47B 的 dense 也是 94 GB），非 routing 本身。
- `:148` §6.1 同类句：改为 "Routing does not lower that floor by itself … 94 GB vs 140 GB, a 46 GB (~32.9%) saving"。
- `:90` Table 3-2 total 行：`= 45.6B + ~1.4B always-on (attention/shared + embeddings) = 47B`，使 45.6 + 1.4 = 47.0 与账本逐位闭合（原式把 embeddings 另计，读作 >47B）。
- 640 GB / 8×H100 出处：Ch 4 Table 4-2（`chapter-04.md:76` "8×H100 (80 GB each, 640 GB)"），非本章新造数。
- vLLM 引用已实测可取（HTTP 200，正文含 `--enable-expert-parallel` / `--all2all-backend` / EP ranks 分片），故该句可追溯而非无源断言。

## P1-02（RED → AFTER）

**RED（`render/fig_ch3.py:86` 原文）**

```python
legend_row(ax, A_RES, '#cccccc', '#888', 'resident \u2248 full expert set', '#444')
legend_row(ax, A_ACT, '#e67e22', '#333', 'active per token \u2248 28 GB', '#333')
ax.text(5, A_SENT, 'only top-2 of 8 experts compute per token', ...)
```

问题：28 GB 与 Tables/prose 的 25.6 GB 冲突；resident 行未给 94 GB；12.8B 未拆 always-on 1.4B + 两专家 11.4B。

**AFTER**

```python
legend_row(ax, A_RES, '#cccccc', '#888', 'resident weights \u2248 94 GB', '#444')
legend_row(ax, A_ACT, '#e67e22', '#333', 'per-token active-weight bytes\n\u2248 25.6 GB (12.8B \u00d7 2 bytes)', '#333')
ax.text(5, A_SENT, 'per token: 11.4B top-2 + 1.4B always-on', fontsize=9.0, color='#333', ha='center')
```

（`legend_row` 增 `va='center'` 形参，默认值与原行为一致，dense 面板行位不动。）

**Fig 3.4 图注（`chapter-03.md:205`）RED → AFTER**

- RED: "…only the top-2 experts plus always-on weights (~12.8B) are active per token (active compute footprint ≈ 25.6 GB)" —— 把 total-active 12.8B 与 "top-2 + always-on" 混写，且未给 94 GB。
- AFTER: "…keeps its full expert set as resident weights — **~94 GB**, not shown to scale — while only ~12.8B is active per token: **the always-on attention/shared weights (~1.4B) plus the two routed experts (~11.4B = 2 × 5.7B)**, an active compute footprint of ≈ 25.6 GB read per token."

## 验证（全部实测）

1. **图 gate**: `python3 render/measure_fig.py figures/fig-03-0301.pdf` → `MIN-ON-PAGE 8.40`，**exit 0**（阈值 ≥8.0；字号未降，仍为 9.2/9.0/8.4pt，natural=6.100in、scale=1.000、Type42 DejaVu）。
2. **几何（CDP 级量 bbox，dpi100）**: 裁剪 **0**、同面板文本重叠 **0**；resident 行 ↔ 折行图例块间隙 **+5.9 px**、图例块 ↔ 下方句 **+14.4 px**；最右文本 x=580.6 < 图宽 610（折行第 2 行止于 572.9，未越 axes 565.3 之外 7.6 px、未触边）。
3. **PDF 文本抽取**: 含 `resident weights ≈ 94 GB`、`per-token active-weight bytes ≈ 25.6 GB (12.8B × 2 bytes)`、`per token: 11.4B top-2 + 1.4B always-on`、`140 GB`；**`28 GB` 不存在**。
4. **视觉复核（vision，2 轮）**: 无裁切 / 无重叠 / 无 "28 GB"；判读数字自洽（11.4 + 1.4 = 12.8；12.8 × 2 = 25.6；resident 94 GB、per-token 25.6 GB）。第 1 轮的 "(12.8B with always-on)" 被误读为 12.8B 即 always-on ⇒ 已改为无歧义写法（图例给 12.8B×2 bytes，正句给 11.4B + 1.4B 拆分）。
5. **仓库检查（只读执行）**: `render/check_tables.py` = 0、`render/check_md_leaks.py` = 0、`render/check_regressions.py` = 0。
6. **标签计数（before → after）**: `[ILLUSTRATIVE` 15→15、`[ASSUMPTION]` 8→8、`[DERIVED]` 16→16、`[canonical scenario]` 8→8、`[1P]` 16→16、`[FACT]` 15→15；`[UNRESOLVED]` **2→3**（新判定旗标，预期）。
7. **章内残留**: `28 GB` = 0；`14B active` 2 处均为 Wan2.2 官方计数（`:174`/`:176`，[1P][FACT]，与本账本无关）；`challenger fails` / `does not cut the memory` = 0。

## OPEN（未在本任务内解决）

1. **构建产物过期（非本任务所有权）**: `render/latex/_md/ch03.md`、`render/build/_book.md`、`render/build/_book.latex.md` 仍是旧 14B / 28 GB 账本的快照 —— 属渲染器输出，需下次全书构建再生成；本任务按约束未改渲染器、未做全书构建。
2. **无跨章交接**: grep 全书，无其他章节引用本小案例判定（Ch1/Ch4 只引 KV 概念；Ch11/Ch20 的 "dispatcher" 为请求调度器语义，非 MoE 路由）⇒ 无需他章同步。
3. **vLLM 引用为 `latest` 浮动 URL**: 已实测可取，但未钉版本/commit；若评审要求 [1P][FACT] 级钉版，需补访问日期或 commit 链接（本章未越权加日期戳）。