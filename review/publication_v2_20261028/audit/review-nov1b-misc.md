# review-nov1b-misc — 2026-11-01 评审 P2-06 / P2-08 / P2-09 / P2-10 / P2-12 处置证据

评审输入：2026-11-01 publishing-readiness review P2 条目（父任务转述，仓库内无原文，按转述条文处置）。
范围：仅 `design/manuscript/*.md` 3 个文件（chapter-01 / 16 / 27）+ Fig A.1 生成器与产物（`render/fig_2701.py`、`fig-27-2701.{png,pdf}`）+ 本证据文件。
**未**改 renderer/根配置、**未**做全书构建、**未** commit、**未**动 `render/latex/*`、`render/build/*`。
Fig 1.2（P2-12）经核验**无需重生成**（见 §5）；文字项与图注均**需 PDF 重建才能最终验证页码/版面**（见 §7）。

> 并发说明：处置期间工作区可能同时被其他 agent 修改；文件级 sha 非本任务独占，**逐条 before/after 片段为权威记录**。
> before 快照副本：`$SCRATCH/nov1b/{chapter-01,chapter-16,chapter-27}.md, fig_2701.py`（SCRATCH = `~/.hermes/profiles/muta/cache/scratch`）。

| 文件 | sha256 (before → after) |
|---|---|
| `design/manuscript/chapter-27/chapter-27.md` | `1188ca6c4944…` → `1650ed0450b0…` |
| `design/manuscript/chapter-16/chapter-16.md` | `cfa7da083567…` → `551306dece9e…` |
| `design/manuscript/chapter-01/chapter-01.md` | `f27bcc66598a…` → `a9b092dea12f…` |
| `render/fig_2701.py` | `a7de9003241e…` → `78defc3150e9…` |
| `design/manuscript/chapter-27/figures/fig-27-2701.png` | `e328fd034062…` → `9a1cf0026efd…`（重生成） |
| `design/manuscript/chapter-27/figures/fig-27-2701.pdf` | `8bae81dcd8f8…` → `f2899b247b84…`（重生成） |
| `design/manuscript/chapter-01/figures/fig-01-token-travel.png` | `a2711c3f5097…` **未变** |
| `render/archify/fig-1-2-token-travel.json` | `153bc62fc801…` **未变** |

----

## 1. P2-06 — Appendix A "Interpretation ↔ [DERIVED]" 改为分析标记 + 三寄存器例

`chapter-27.md:49`：

```diff
-- **Interpretation** ↔ [DERIVED] — the book's own analysis, a derivation from the evidence. (Where the book's taxonomy would label it [ILLUSTRATIVE], note that; the appendix uses "interpretation" only as plain prose for a derived read, never a separate sanctioned status.)
+- **Interpretation** ↔ **[INTERPRETATION]** — an explicit analysis/interpretation marker for the book's own read of the evidence. It is **not** a sixth arithmetic status and adds nothing to Axis 2: [DERIVED] stays reserved for reproducible calculation (a number anyone can recompute from stated inputs), and testable predictions use [HYPOTHESIS]. (Where the book's taxonomy would label the same passage [ILLUSTRATIVE], note that; the appendix uses "interpretation" as plain prose for an analytical read, never a sanctioned arithmetic status.)
```

`chapter-27.md:53` 后新增对照例（数字全部来自既有文本：Qwen 6B/125B、Fig A.1 的 4.8%）：

```diff
+**One fact, three registers (worked contrast).** Take the same Qwen3.8-Flash-Next figure three ways: **(a) numeric ratio** — "6 B ÷ 125 B = 4.8% active" is [DERIVED]: reproducible calculation from stated inputs, anyone can re-run it; **(b) descriptive interpretation** — "sparsity this extreme makes long-context serving a memory problem before a compute problem" is [INTERPRETATION]: our read of what the number means, analysis that could be wrong and earns no arithmetic status; **(c) measurable prediction** — "at equal context, serving this model becomes more memory-comfortable" is [HYPOTHESIS]: a testable prediction you can check on your own hardware. Only (a) is [DERIVED].
```

核验：全书 `Interpretation ↔ [DERIVED]` 计数 = 0；Axis 2 状态列表仍为 5 个（`[FACT]/[DERIVED]/[ASSUMPTION]/[HYPOTHESIS]/[UNRESOLVED]`，未新增第六个算术状态）；`[HYPOTHESIS]` 仍专用于可检验预测；6/125 = 4.8% 与 Fig A.1 一致。

## 2. P2-08 — Ch16 启动 mini-case：24×7 工作负载 + 速率对账

`chapter-16.md:217` 段末新增一句（原句、原数字全部保留）：

```diff
 … so the current volume is already ~2.6× past the break-even.
+ This is **a different startup workload with 24×7 traffic**, not the canonical case's business-hours shape: 5M/mo at 2 rps = 2.5M s ≈ **29 days × 24×7**, versus the canonical **624,000 active s/mo** (10 rps × 8 h × 260 workdays ÷ 12) — same per-request price, a different duty cycle.
```

对账核验（复算）：5,000,000 ÷ 2 = 2,500,000 s ÷ 86,400 = 28.94 d ≈ **29 d × 24×7**；8 × 3,600 × 260 ÷ 12 = **624,000 s/mo**；6,240,000 ÷ 10 rps = 624,000 s（与 §16 正文一致）。限定词（~2 rps、~5M、~$0.0208、~2.6×、1.9M）未改。

## 3. P2-09 — Ch16 p~268：~$64K 机会成本与已含 ~$26K 工资的去重

`chapter-16.md:219` 段后新增小节 + 三行表（既有数字/限定词全部保留）：

```diff
+**Which term is which — no double-counting.** The ~$40K self-host cost already carries the ~$26K/mo 0.5-FTE wage, so the ~$64K opportunity cost is an **alternative valuation of the same hours**, not incremental foregone product value stacked on top of that compensation:
+
+| Term | What it prices | ~$/month | Where it is counted |
+|---|---|---|---|
+| **Wages** — 0.5-FTE operator, fully loaded (≈$624K/yr ÷ 2, scenario value) | cash compensation for the same 0.5 FTE | ~$26K | **inside** the ~$40K self-host cost (already counted) |
+| **Time redeployment** — the same 0.5 FTE's hours re-priced as product time | non-cash valuation of the *same* hours | threshold ~$64K (~$770K/yr) | an **alternative** valuation of those hours, not an added cost line |
+| **Incremental foregone contribution** — product value from hours *beyond* the priced 0.5 FTE (extra product work displaced on top of the compensation already counted) | none in the base case | ~$0 | not counted; it appears only if the two servers consume more than 0.5 FTE |
+
+Reading: the wages are cash already inside the $40K; the ~$64K is what those freed hours must be worth to offset the ~$64K API premium (the threshold equals the premium by construction of this mini-case). Adding the two would price the same 0.5 FTE twice.
```

处置结论（写入正文）：**~$64K 是同一批工时的替代估值，不是在 ~$26K 工资之上的增量 foregone value**；工资是已入 $40K 的现金，机会成本是同一批 0.5 FTE 工时的非现金价值；超出已定价 0.5 FTE 的增量 foregone contribution 在 base case 为 ~$0。两者相加 = 同一 0.5 FTE 计价两次。
核验：`render/check_tables.py` = all tables column counts consistent；`render/check_md_leaks.py` = no leak risks（均 exit 0）。$64K × 12 = $768K ≈ 既有 $770K/yr，未改。

## 4. P2-10 — Fig A.1（p~392）：Qwen 条标 backbone ratio + 分母列标注（唯一重生成项）

`render/fig_2701.py`：

```diff
 ax.set_xlim(0, axis_max)
+ax.set_ylim(-0.55, 4.05)                      # 顶部留白，容纳列头且不压 "284B/13B active"
…
-    ax.text(fr + 0.25, y[i_rev], f'{fr:.1f}%',
+    star = '*' if 'Qwen' in names[i_orig] else ''
+    ax.text(fr + 0.25, y[i_rev], f'{star}{fr:.1f}%',      # 前置 '*'：尾随 ' *' 会把与右侧注的间距压到 ~7px
…
-ax.set_yticklabels(names, fontsize=10.5)
+ax.set_yticklabels([f'{n}*' if 'Qwen' in n else n for n in names], fontsize=10.5)
…
+ax.text(param_label_x, 3.95,
+        'denominator: vendor-reported / resident total, varies by vendor',
+        ha='right', va='top', fontsize=8, color='#777', bbox=…white…)
…
+fig.text(0.04, 0.045,
+         '* Qwen bar = backbone ratio (125B backbone), excluding the 51B n-gram embedding and 4B MTP.',
+         fontsize=8.2, …)
…
-plt.subplots_adjust(left=0.36, right=0.99, top=0.90, bottom=0.20)
+plt.subplots_adjust(left=0.36, right=0.99, top=0.90, bottom=0.24)   # 给第二行脚注让位
```

重生成 `fig-27-2701.png`（350 dpi，2135×1155）+ `.pdf`。核验：
- `pdftotext -layout` 读回：列头 `denominator: vendor-reported / resident total, varies by vendor`、`Qwen3.8-Flash-Next*`、`*4.8%`、两行脚注（`* Qwen bar = backbone ratio (125B backbone), excluding the 51B n-gram embedding and 4B MTP.` + 原 VENDOR-REPORTED 行）全部在图内。
- **vision 复核（整图）**：标题/列头/首条注三者互不重叠；两条脚注完整、与 x 轴标题有间隙；全图无重叠、无裁切。
- 像素测量：`*4.8%` 与右侧 `125B backbone…` 间距 = 25 px @350 dpi（≈5 pt），无粘连。
- 数字未动：284/13、2800/104、125/6、320/18、4.6/3.7/4.8/5.6%、51B n-gram、4B MTP。

## 5. P2-12 — Fig 1.2（p~28）：反向读箭头 + 图注降级为 one-time token-to-state construction

**(a) 反向/读箭头：核验为**已存在**，无需改源、无需重生成**：
- 源 `render/archify/fig-1-2-token-travel.json` 连接 `f6: kv → attn, label "read past K,V", variant emphasis, width 2.4`（HEAD 已含，文件 sha `153bc62fc801…` 前后未变）。
- 产物 `fig-01-token-travel.png`（sha `a2711c3f5097…` 未变）**vision 核验**：存在绿色反向箭头，自 KV Cache 底部出、经 Attention 下方回到 Attention 底部，标签 `read past K,V`；KV Cache 仅此一条出边。持久状态（database 型 KV 盒）与处理阶段（frontend 型 Attention 盒）在图中已由盒型 + 该读回箭头区分。
- 结论：评审所据渲染（p~28）应为旧版；**当前资产已满足条文**，未改 JSON/PNG/PDF。

**(b) 图注降级** `chapter-01.md:59`：

```diff
-![Fig 1.2 — … **Conceptual only:** this is a one-pass abstraction, not the full transformer — the K/V are produced *within every applicable layer* (not after a single "attention" stage), and the KV cache is a *persistent state* that is both written (append) and read (attend) across steps, not a terminal processing stage. The read-side and the iterative loop are shown in Fig 2.1. [ILLUSTRATIVE conceptual]]
+![Fig 1.2 — … **Conceptual only:** what is drawn is the **one-time token-to-state construction** — a one-pass abstraction of how a token becomes state, not the full transformer and not the step-to-step loop. The K/V are produced *within every applicable layer* (not after a single "attention" stage), and the KV cache is a *persistent state* — written (append) and read (attend, the backward read arrow from the KV cache back to attention) across steps — not a processing stage. The read-side and the iterative loop are shown in Fig 2.1. [ILLUSTRATIVE conceptual]]
```

保留：`one-pass abstraction`、`within every applicable layer`、`persistent state`、`written (append) / read (attend)`、`Fig 2.1` 指引、`[ILLUSTRATIVE conceptual]`；正文斜体图注（:61）与口诀注（:65）未动。

## 6. 未改项 / 范围声明

- 未改 `render/make_html.py`、`render/latex/*`、`render/build/*`、根配置、`book.yaml`、`canonical-workload.yaml`、`design/numerical-audit-ledger.md`。
- 未删图、未改编号、未改交叉引用；Fig A.1 仅原位重生成同名 png+pdf。
- 未 commit、未做全书构建。

## 7. 需重建才能最终验证的项（OPEN-ON-BUILD，非内容 OPEN）

1. **P2-06 / P2-08 / P2-09 / P2-12(b) 均为 source-only**：需全书 PDF 重建后确认 p~394 映射段、p~268 新表分页与列宽、p~28 新图注行数/图注间距。
2. **Fig A.1 新 png/pdf 需在构建时拷入 `render/latex/figures/`** 后确认嵌入尺寸与脚注两行的在页可读性（本次仅验证了源产物）。
3. **Fig 1.2 反向箭头在成书 p~28 的可见性**依赖既有资产（未重生成）；若构建采用 `copy_figures` 旧缓存，需确认拷贝的是 `a2711c3f…` 这一版。
4. 无内容性 OPEN：5 条条文均已按转述处置；P2-12(a) 为"已满足、经核验"而非"未做"。