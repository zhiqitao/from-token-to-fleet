# 四份出版就绪评审 — 勘合关闭表（reviews-consolidated）

- 仓库：`/home/ubuntu/hermes-work/from-token-to-fleet`（HEAD `614d3aa8` = R35；本表基于工作区当前状态）
- 评审原件（权威条文，仓库外缓存）：
  - **A**（441 pp，2026-11-01）`…/0d64abce…/doc_3029c3d7acce_publishing_readiness_review_20261101.md`
  - **B**（425 pp，2026-10-31）`…/24d592f9…/doc_8bf82ad24fd9_Publishing_Readiness_Review_2026-10-31.md`
  - **C**（434 pp，2026-11-01）`…/abde8e4d…/doc_7a7906f53655_publishing_readiness_review_2026-11-01.md`
  - **D**（429 pp，2026-11-01）`…/d1b4c6da…/doc_db384faf1159_from_token_to_fleet_publishing_review_20261101.md`
- 判定规则：**CLOSED** = 现行 `design/manuscript/*.md` / `render/fig_*.py` 实测命中 + 既有 audit 证据；**EXTERNAL-GATE** = 需作者/生产/法律/外部工具，源码编辑无法关闭；**OPEN** = 无证据且本轮不可安全修复（附原因）。
- 本轮新增内容修复 9 项（见 §2）；`render/check_tables.py`、`check_md_leaks.py`、`check_regressions.py` 全部 exit 0。未改 renderer/根、未做全书 build、未 git。

## 1. 关闭表（62 条）

| ID | 来源 | 状态 | 证据 |
|---|---|---|---|
| A P1-01 ρ/u/N−1 合成 | A | CLOSED | `chapter-17.md` 政策式 `⌈λ·W_KV/(C·u·ρ)⌉+N_spare`（2 处）+ Table 17-1 权威政策表（11 处引用）；`audit/review-nov1c.md` §1（32/34/29/32、TCO $232,197.23/$37.21 复算） |
| A P1-02 Fig 17.1 ρ | A | CLOSED | `render/fig_ch17_capacity.py` 含 ideal ρ=1 / ρ=0.85 稳健下界注记（3 处）；`audit/review-nov1c.md` §2（bbox 重叠 0，vision 通过） |
| A P1-03 标签三轴出处 | A | CLOSED | `chapter-04.md:127` Note 1 三轴定义 + `chapter-23.md` `[ILLUSTRATIVE]` 5 处；`audit/review-nov1c.md` §3 |
| A P1-04 Nov-1 附录 | A | CLOSED | `chapter-27.md` Revision note `v20260913+addendum-20261101`（1 处）**且** `render/latex/preface.tex:227` 已含同版本号（原 OPEN 项已由后续轮次补齐） |
| A P1-05 网络计时 | A | CLOSED | `chapter-17.md:159-175` `t_fixed/t_transfer/t_queue` 三分解、20 ms = 服务检索 RTT、goodput=D/t_net、5 MB÷1.25 GB/s=4 ms、B_agg=φ·λ·D 对 10 Gbps ≈1.6%；`:227` offered-byte-rate vs link-budget |
| A P2-01 Table 19-1 13.85 | A | CLOSED | `chapter-19.md` `13.85`×5、`Base + orchestration subtotal`×3；`audit/review-nov1c.md` §6 |
| A P2-02 Ch22 越界结论 | A | CLOSED | `chapter-22.md` 新句 `candidate worth testing`×1；旧句 `makes clear a homogeneous` 全库 0 |
| A P2-03 多区域需求矩阵 | A | CLOSED | `chapter-25.md` + `chapter-22.md` requirement-coverage matrix 各 1，R5 = NOT VALIDATED/NOT PRICED（`chapter-25.md:213`） |
| A P2-04 附录 moving-target | A | CLOSED | 三机制齐备：2026-08-30 硬边界块 + 带日期 Service-status caveat（re-verified 2026-11-01，`chapter-27.md:7`）+ Revision note 版本标记（`:9`）+ 钉死 ledger permalink（`27f4cd57`，B P1-02） |
| A P2-05 印刷生产发布门 | A | EXTERNAL-GATE | 开版规格（trim/色彩/出血/纸张/灰度实检/整封套）需作者与 KDP 打样；对应 handoff G6/G7/G8 |
| A P2-06 例题 measured-vs-analytical 收口 | A | CLOSED（本轮修复） | `chapter-14.md` §3 新增 **Result worksheet**（9 行：load trace/TTFT/TPOT/SLO-goodput/KV allocator/rank imbalance/admission/MFU/model ID+commit，全部 `[UNMEASURED]`，无杜撰测量） |
| A P2-07 图注/表注 reflow | A | CLOSED | Note 1 / Note 11.3-1 / Note 16.1-1 / Note 22.1-1 均在（ch4/ch11×2/ch16×2/ch22）；`audit/review-nov1c.md` §8 |
| B P1-01 许可授权 | B | EXTERNAL-GATE | 作者+律师：§1(3) vs §2(2) 张力、KDP 条款；handoff **G1** |
| B P1-02 源账本可导航 | B | CLOSED | `chapter-27.md` 含 pin permalink `27f4cd57…`（1 处）；`audit/review-oct31-sla-source.md` §3（71/71 键可解析，curl 200） |
| B P1-03 印刷线宽检查 | B | EXTERNAL-GATE | 0.4 pt 页眉线 / 脚注区 5.98 pt 标号在 `book.sty`/`md_to_latex.py`（renderer），且须 KDP 预览实检；handoff **G5**；`audit/review-oct31-sla-source.md` §4 判 OPEN-构建侧 |
| B P1-04 强制出版门 | B | EXTERNAL-GATE | veraPDF/PDF-UA、字体与图片权利矩阵、ISBN；handoff **G2/G3/G4** |
| B P2-01 Ch3 MoE 12.8B | B | CLOSED | `chapter-03.md` `12.8B`×16；`audit/review-oct31-ch3ch24.md` P2-01 |
| B P2-02 Ch24 null-reference | B | CLOSED | `chapter-24.md` 改为 uniform-sampling null reference（`minimum exposure` 残留 0）；`audit/review-oct31-ch3ch24.md` P2-02 |
| B P2-03 Ch24 PIES 顺序敏感 | B | CLOSED | `chapter-24.md` `order-sensitive`×4；`audit/review-oct31-ch3ch24.md` P2-03 |
| B P2-04 Fig 11.3 拓扑+1.4 TB/s | B | CLOSED | `chapter-11.md:142` 两案例两链路（NVLink 域 / fabric）+ `1.4 TB/s`×2 + Note 11.3-1 |
| B P2-05 Fig 16.1 云线 | B | CLOSED | `chapter-16.md:213` Note 16.1-1：cloud = 单点 marker，不参与 crossover；caption 同步 |
| B P2-06 SLA 未定即近决策 | B | CLOSED | `CANDIDATE SCREENED; NOT COMMITTABLE` 在 ch16/17/22/25 各 1；Ch25 ADR 0015 Status **HOLD**（9 处 HOLD）+ 四条 exit criteria |
| B P2-07 Fig 6.2 阴影 | B | CLOSED | `render/fig_ch6_hist.py:64-74` 阴影 >2 s 全域 + 4.5–5.5 s 深色 hatch；资产 `fig-06-0602.{png,pdf}`（17:25）晚于生成器（17:23） |
| B P2-08 超长图注 | B | CLOSED | `audit/review-oct31-sla-source.md` §2（Fig 17.1/7.7/3.3/15.2 三段式，7.7 −53%）+ A P2-07 补齐 11.3/16.1/22.1 |
| B P2-09 图版面/色彩印制验收 | B | EXTERNAL-GATE | 需实体打样页照片 + standard/premium 色彩定价决定；handoff §C + G6/G8 |
| B P3-01 LoF 短标题 | B | CLOSED | `chapter-19.md` `Agent turns: token and KV growth`；`audit/review-oct31-sla-source.md` §5（55 条图注，省略号条目 0） |
| B P3-02 重复 caveat 可读性税 | B | OPEN | 无 `Evidence boundary` 面板（全库 0 命中）；已部分缓解（推导集中进编号注、图注指针化），但 Ch1/7、16/17、19、App A 的"逐处改一句提醒"是跨章编辑清扫，需整书重建验证，本轮不安全实施 |
| B P3-03 模型族术语/计数/日期钉死 | B | CLOSED（本轮补强） | 125B backbone vs 51B/4B 分离、Aug-30 vs Oct-28 分层均已在稿；`chapter-27.md` 4–10× 补注 **"a band across models, not a universal constant"**（全书无 14× 之说，故按评审"改用具名配置或显式区间"处理） |
| B P3-04 TEACHING GEOMETRY 标签 | B | CLOSED（本轮修复） | 新增 4 处：`chapter-04.md` 规范框、`chapter-07.md` §3（2.62 MB/token）、`chapter-16.md` Table 16-1 题注、`chapter-17.md:107` Table 17-1 题注 |
| C P1-01 DeepSeek V4-Pro 状态 | C | CLOSED | `chapter-27.md` `V4.1-Flash`×5（`:7`/`:9` 双源+检索日）；`audit/review-nov1b-deepseek.md`（8 月冻结主张未动） |
| C P1-02 prefill-FLOP 口径 | C | CLOSED | `chapter-08.md` 唯一三 case 约定块；19/21/22/30/33 全 case 标注；`audit/review-nov1b-flops.md` §0–1 |
| C P1-03 21-host TCO 依赖 | C | CLOSED | `chapter-16.md` 22-host 情景 `$162,760.59`×7、row A′、21-host 降为敏感性；`audit/review-nov1b-flops.md` §2 |
| C P2-04 Ch22 单卡 vs 8 卡 | C | CLOSED | `chapter-22.md` ~1.19 PFLOPS = 聚合线性口径，只与 7.91 PFLOPS 聚合峰比较，单卡标 `single-GPU counterfactual` |
| C P2-05 全方形 vs 因果三角 | C | CLOSED | `render/fig_ch22_divergence.py` causal 曲线×7 + 双交叉 53.4K/106.8K；`audit/review-nov1b-flops.md` §4 |
| C P2-06 App A 解释≠DERIVED | C | CLOSED | `chapter-27.md` `[INTERPRETATION]`×2 + 三寄存器对照例；`audit/review-nov1b-misc.md` §1 |
| C P2-07 可用性未收口 | C | CLOSED（本轮修复） | `chapter-16.md` 新增 **Parametric multi-region worksheet**（8 行，全 NOT SIZED/TESTED/PRICED/RUN，无杜撰价格，指向 ADR 0015 exit (ii)），保留 candidate-only 语言 |
| C P2-08 Ch16 mini-case 时基 | C | CLOSED | `chapter-16.md` `24×7`×3 + 5M÷2≈29 d vs 624,000 s 对账；`audit/review-nov1b-misc.md` §2 |
| C P2-09 工资/机会成本不重叠 | C | CLOSED | `chapter-16.md` `no double-counting` 三行账本表；`audit/review-nov1b-misc.md` §3 |
| C P2-10 Fig A.1 分母 | C | CLOSED | `render/fig_2701.py` 列头 `denominator: vendor-reported…` + Qwen `*` 脚注；`audit/review-nov1b-misc.md` §4 |
| C P2-11 前言/图注超载 | C | OPEN | 图注半已闭（Fig 1.2/7.7/15.2/16.1/22.1/11.3/19.3 均三段式+编号注）；**前言 pp12–19 的约定/caveat 页在 `render/latex/preface.tex`（renderer 根，本任务禁改）**，故整条不能判 CLOSED |
| C P2-12 Fig 1.2 单向读法 | C | CLOSED | `chapter-01.md` 图注改 one-time token-to-state construction；源 JSON 反向读箭头 `read past K,V` 已存在（sha 未变）；`audit/review-nov1b-misc.md` §5 |
| C P2-13 印刷图可达性门 | C | EXTERNAL-GATE | ≥8pt@成品尺寸、灰度区分、100% 实印测试须实体打样；handoff G5/G8 |
| C P2-14 封面/内文分离 | C | EXTERNAL-GATE | KDP 需独立整封套 + 内文文件；handoff **G7** |
| C P3-15 LoF 自动措辞（Fig 22.1） | C | CLOSED（本轮修复） | `chapter-22.md` 图注首句改为 `Attention vs. projection prefill FLOP crossover.`；实测 `short_title()` → `'Attention vs. projection prefill FLOP crossover'`（修复前为 `'**Takeaway'`） |
| C P3-16 Fig A.3/A.4 概念性标签 | C | CLOSED（本轮修复） | `render/fig_2703.py` 底注改 `Selected illustrative mechanism milestones — a non-comprehensive chronology`；`render/fig_2702.py` 改 `nonexclusive placement choices, not a ranking`；重生成 2702/2703 png+pdf，pdftotext 命中，measure 8.50/8.00 pt，vision 复核无重叠无裁切 |
| C P3-17 结论"计量=数 token"过窄 | C | CLOSED（本轮修复） | `chapter-22.md` §4 改为 "For the **token-accounting step**…" 并交叉链接 Ch14 基准协议 / SLO-goodput / 区域可用性 / Ch16 TCO 四道门 |
| C P3-18 附录服务状态可分离 | C | CLOSED（本轮修复） | `chapter-27.md` 新增 **Three registers** 表（Architecture snapshot 2026-08-30 冻结 / Current API serving status 09-10·09-14·re-verified 11-01 / Independent reproduction ledger `27f4cd57`），并声明重核第 2 行不改写第 1 行 |
| D P1-01 Ch3 结论 | D | CLOSED | `chapter-03.md` `two findings, both stated plainly`；94/140 GB、−46 GB、−32.9%、[UNRESOLVED]；`audit/review-nov1-ch3.md` |
| D P1-02 Fig 3.4 推导 | D | CLOSED | `render/fig_ch3.py` `resident weights ≈ 94 GB`、`25.6 GB (12.8B × 2 bytes)`；`28 GB` 全章 0；measure 8.40 pt exit 0 |
| D P1-03 KV 驻留 Little's Law | D | CLOSED | `chapter-17.md` 五个时间量 + `E[L_KV] = λ_admitted × E[W_KV-resident]` + `max(容量, 尾延迟)` + 两条禁移植；`audit/review-nov1-ch17.md` §1 |
| D P1-04 C/W 上下界同名 | D | CLOSED | 统一短语 `analytical UPPER bound…` 全库（ch16/17/20 共 10 处）；方向翻转只一次（⌈20.24⌉=21）；`audit/review-nov1-ch17.md` §2 |
| D P1-05 Table 15-1 MFU 标签 | D | CLOSED | `chapter-15.md` `Illustrative load pressure`×1，`MFU (%)`×0；`audit/review-nov1-ch17.md` §3 |
| D P1-06 SLA/TCO/方案不匹配 | D | CLOSED | 诚实停在决策门：ch16/17/22/25 `NOT COMMITTABLE` 决策框 + Ch25 **ADR 0015 Status HOLD**（Decision=none、四条 exit criteria、Validation plan、Falsification path）+ R5 NOT VALIDATED/NOT PRICED + 本轮 C P2-07 参数化工作表补齐"缺测输入"清单 |
| D P2-07 断图引用 | D | CLOSED | `chapter-16.md`/`chapter-17.md` 各 1 处 `Fig \ref{fig:spine-loop}`（动态引用，不硬编码）；`audit/review-nov1-p2.md` §1 |
| D P2-08 Ch16 mini-case 过度主张 | D | CLOSED | `chapter-16.md` `Within this equal-capability assumption set` 条件式 + 8 个决策相关项；`audit/review-nov1-p2.md` §4 |
| D P2-09 Ch1/Ch22 隐喻反转 | D | CLOSED | `chapter-22.md` `metered unit of model I/O`×1；`metered unit of thought` ch1/ch22 均 0 |
| D P2-10 Fig A.2 阴影带 | D | CLOSED | `render/fig_ch27_norm.py` `hatch='///'`×0，实心白底+深红边框+11.0 pt 标题；`audit/review-nov1-p2.md` §3（vision 复核） |
| D P2-11 Fig 16.1 / Table 4 超载 | D | CLOSED | `chapter-04.md` 预算格压缩为 `illustrative cap` + 侧栏承接 22 个数字；`chapter-16.md:213/215/217` 三段式图注 + Note 16.1-1 + 正文 Reconciliation 段 |
| D P2-12 Fig 19.2/19.3 重复 | D | CLOSED | `chapter-19.md` `Three policies`×2；`render/fig_ch19_accum.py` 三策略条（Append-only/Compaction/Prefix-cache）；`audit/review-nov1-p2.md` §6 |
| D P2-13 版本/时效导航 | D | CLOSED | `chapter-27.md:7` 带日期 Service-status caveat（09-10/09-14，re-verified 2026-11-01）+ 指向 2026-10-28 V4.1 技术注；8 月原主张逐字未动 |
| D P2-14 实体印刷交付物 | D | EXTERNAL-GATE | KDP trim 决定、内文/封面分文件、0.625 in 装订边、实体打样；handoff G6/G7/G8 |
| D P3-15 表述/导航打磨 | D | OPEN | 4 子项：①长 disclaimer 合并=部分完成（16.1/19.2/19.3/A.1 已处理）；②图名统一=已由 D P2-07 动态引用闭合；③术语排版统一=跨章清扫需重建；④**Glossary 中 MFU/利用率/调度效率辨析在 `render/latex/backmatter/glossary.tex`（renderer 根，禁改）**。③④不可在本轮内容修复范围内 → 整条 OPEN |

**合计：62 条 — CLOSED 51（其中本轮内容修复 9）· EXTERNAL-GATE 8 · OPEN 3。**

## 2. 本轮内容修复清单（含验证）

| 修复 | 文件（sha256 前 12 位） | 验证 |
|---|---|---|
| C P3-15 Fig 22.1 LoF 短标题 | `chapter-22.md` `7e903ea3f6cc` | `short_title()` 实测返回 `Attention vs. projection prefill FLOP crossover` |
| C P3-17 §4 计量句限定 + 四门交叉链接 | `chapter-22.md` | grep `token-accounting step` = 1；旧句 0 |
| C P3-18 三寄存器表 | `chapter-27.md` `9880c27c95f0` | 表 4 列 ×3 行；`check_tables.py` exit 0 |
| B P3-03 4–10× 区间限定 | `chapter-27.md` | grep `not a universal constant` = 1 |
| C P2-07 多区域参数化工作表 | `chapter-16.md` `4dc01246ec81` | 8 行全 NOT SIZED/TESTED/PRICED/RUN；无新增价格 |
| B P3-04 TEACHING GEOMETRY ×4 | `chapter-04.md` `250f30798868`、`chapter-07.md` `47705ac73376`、`chapter-16.md`、`chapter-17.md` `d96d7c94e966` | grep 全库 `TEACHING GEOMETRY` = 4 文件 |
| A P2-06 Ch14 结果工作表 | `chapter-14.md` `fb47caef8a44` | 9 行全 `[UNMEASURED]`；`check_tables.py` exit 0 |
| C P3-16 Fig A.3/A.4 轴标签 | `fig_2703.py` `db34f1bbd60d`、`fig_2702.py` `70183bc03a56`；产物 `fig-27-2703.{png,pdf}` `20b084df4721`/`c3fd8cb997c3`、`fig-27-2702.{png,pdf}` `1c51fb9872df`/`935b21fa66a2` | pdftotext 命中新标签；measure 8.50 / 8.00 pt；vision 复核无重叠、无裁切（A.4 的 8.00 pt→exit 1 为浮点边界，HEAD 版本同样 exit 1，非本轮回归） |
| 静态门 | — | `check_tables.py` / `check_md_leaks.py` / `check_regressions.py` 全 exit 0 |

## 3. EXTERNAL-GATE 汇总（作者/生产动作，不得本地判过）

A P2-05（开版规格）、B P1-01（许可 G1）、B P1-03（线宽 G5）、B P1-04（veraPDF/权利/ISBN G2–G4）、B P2-09（打样页+色彩定价 G6/G8）、C P2-13（印刷可达性 G5/G8）、C P2-14（封面/内文 G7）、D P2-14（实体印刷交付 G6–G8）。总门清单见 `review/publication_v2_20261028/publish-gates-handoff.md` G1–G9。

## 4. OPEN 汇总（附原因）

1. **B P3-02** — 无 `Evidence boundary` 面板（全库 0）；编号注集中化已部分缓解，但逐处改写是跨章编辑清扫，需整书重建验证，本轮不安全实施。
2. **C P2-11** — 图注半已闭；前言 pp12–19 约定页在 `render/latex/preface.tex`（renderer 根，本任务禁改）。
3. **D P3-15** — ②已闭、①部分；③术语排版清扫需重建，④Glossary 辨析在 `render/latex/backmatter/glossary.tex`（renderer 根，禁改）。

## 5. 未纳入

`native-inputs` 中另有两份 *Let Us Brew an AI Model*（228/229 pp）评审，属另一本书，不在本次四评审范围。