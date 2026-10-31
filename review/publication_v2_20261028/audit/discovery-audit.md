# Pass-G Discovery Audit — R27 新发现（FTF-N###）

- 对象：`review/publication_v2_20261028/work/accelerated_external_review_proof_r27/render/build/from-token-to-fleet-v20260913.pdf`（426 页文本层）+ `design/manuscript/` 源（ch1–15、ch21–26、附录 A=ch27 全文逐章读完）。
- 已知问题（R01–R11、R20–R26、C-02/C-03、标题跳级、pdfuaid、362pp、v20260913、外部门禁）**不重复报告**。
- 页码 = PDF 页（pdftotext 1-based；正文印刷页码 ≈ PDF 页 − 20）。
- 源与 r27 构建源逐章字节比对：**仅 chapter-27 有差异**，ch1–15/21–26 与 PDF 构建源完全一致。
- 计算均在本机复算（见各条"复算"）；不确定处显式标注。

## 结论

**19 条新发现：P1×1、P2×9、P3×9。** 其中最严重的是**源文段落未渲染进 R27 PDF（内容丢失）**，以及**跨章同一量互相矛盾（batch-1 吞吐 50 vs 8,000 tok/s；单机可达 70,000 tok/s 超 100% MFU 上限）**。

---

## P1

### FTF-N01 — Ch5 一整段 [HYPOTHESIS] 未渲染进 R27 PDF（内容丢失）
- **位置**：Ch5 §3(a)，源 `chapter-05.md:62`；PDF 第 96 页（印刷 76）该处为空缺。
- **证据**：源与 `render/latex/_md/ch05.md:61` 均含该段（"…~0.8 ms on a single CPU core, well within the ~120 ms retrieval budget… 2×FLOP cost"）；对 426 页全文检索 `0.8 ms`／`single CPU core`／`decision hinges`／`768-dim vs 384-dim` **零命中**；第 96 页 PNG 目视复核：表 → [DERIVED] 斜体注 → [ILLUSTRATIVE][DERIVED] 存储段 → **Takeaway**，中间该段不存在。同页前后段（源 58、60、64 行）均正常渲染。
- **为什么是问题**：发布候选稿相对源丢内容；且该段本身算错（见 FTF-N06），一旦修复渲染缺陷会把错数一起带出。
- **修复**：定位 md→tex 段落丢失原因（疑与相邻 `[TAG]:` 段落合并规则有关），重建后逐段 diff 源与 PDF 文本层；同时先修 N06 的数值。
- **验证**：已三重验证（全文检索 + 源/_md 存在性 + 页面图像目视）。

---

## P2

### FTF-N02 — Ch4 交叉引用指向全书不存在的数字 "3.3M"
- **位置**：Ch4 §4.3，PDF p83（源 `chapter-04.md:178`）。
- **证据**：原文 "see its throughput-basis reconciliation note — **the 9,000 is single-stream/the 3.3M is whole-fleet aggregate** — before cross-chapter comparison."；全 `design/manuscript/` 检索 `3.3M|3.3 million` **仅此 1 处（即引用本身）**。被指向的 Ch5 对账注（PDF p98）实际对账的是"单位（tokens/dollar-hour vs tokens/s per dollar）+ 吞吐口径（50 单流 vs Ch15 的 8,000 / 35,000–70,000）"，**没有 3.3M**；Ch4 自己的全队列口径是 **~2.76M 输入 / ~2.85M 合计 tokens per cloud dollar**（p83/p85）。
- **复算**：120,000 tok/s ÷ $120/hr = 1,000 tok/s/$ = 3.6M tok/dollar-hour；95,000 ÷ 120 × 3600 = 2.85M —— 都不是 3.3M。
- **修复**：改为指向真实存在的对账内容（"9,000 单流 / 全队列口径见 Ch4 §4.3 的 2.76M–2.85M"），或删除该括注。
- **验证**：已验证。

### FTF-N03 — Ch15 单机"可达"吞吐上限 70,000 tok/s 超 100% MFU 理论上限，且与本章双机小案例自相矛盾
- **位置**：Ch15 §6，PDF p246（源 `chapter-15.md:89`）；对照同章小案例 p247（源 :100）。
- **证据**：§6 "on-host concurrency rises from ~17.5 to ~35.0 … These choices together are expected to raise achieved token throughput from ~8,000 tokens/s … toward an illustrative **~35,000–70,000 tokens/s** [ILLUSTRATIVE achievable range]"（三项均为**单机**决策）；小案例 "token throughput rises from 8,000 to **70,000** tokens/s" 且是**加了第二台主机**后才到 70,000（"~2× from the second host" ⇒ 35,000/机）。
- **复算**：70,000 tok/s × 2N(1.4×10¹¹) = 9.8×10¹⁵ FLOP/s ÷ 7.91×10¹⁵（8×H100 峰值）= **124% MFU**；Ch4/Ch8 给出的 100% MFU 上限为 **~56.5K tok/s**（Ch8:161 亦以 368,000 ÷ 19,800 得 18.6 台，隐含单机 prefill 19.8K、整机峰值 7.9 PFLOP/s）。上限不可能超过 100% MFU。
- **修复**：把区间上限改为 ≤~56K（或标为"含 prefill+decode 混合、需实测"），并统一 §6 与小案例的单机/双机口径。
- **验证**：已复算验证。

### FTF-N04 — batch-1/单流吞吐：Ch5/Ch6 的 50 tok/s vs Ch15 的 8,000 tok/s（160×）
- **位置**：Ch5 PDF p98（源 `chapter-05.md:93` 附近）、Ch6 源 :62；Ch15 PDF p246/p247。
- **证据**：Ch5 "×H100 with a 70B FP16 model and 9.2K context yields **~50 tokens/s aggregate throughput**"，其对账注又称 50 是 "deliberately conservative **single-stream** / low-batch"，同时把 Ch15 的 8,000 称为 "**raw batch-1** ≈ 8,000 tok/s … the multi-request serving throughput" —— batch-1 与 single-stream 是同一工况，却给两个值；Ch6:62 也用 "raw tokens/s from 50 tok/s"。Ch15 原文："~8,000 tokens/s (**raw, no flash, batch-1**)"。
- **复算**：8,000 tok/s 作 batch-1 decode 需 140 GB × 8,000 = **1,120 TB/s**，8×H100 聚合仅 26.8 TB/s（超 41×）；规范 batch-1 = 25 ms/token = **40 tok/s**（Ch2），50 tok/s 与之一致。8,000 ≈ 9,200 ÷ 1.08 s = 8,518（**prefill-only** 速率），疑把 prefill 速率标成 batch-1 decode。
- **修复**：Ch15 把 8,000 改标为"prefill-only/整请求摊薄速率"或改为实测 batch-1 值；Ch5 对账注明确 50 与 8,000 不是同一工况。
- **验证**：已复算验证。

### FTF-N05 — Ch15 把 Ch14 的假想值说成"measures"（benchmark 结果被误标为实测）
- **位置**：Ch15 小案例，PDF p247（源 `chapter-15.md:100`）。
- **证据**："(Chapters 4/8; **Chapter 14 measures p95 TTFT at 1.9 s for this stack**)"。Ch14 原文（源 `chapter-14.md:44`）："This example is **hypothetical, not a measurement made for this book** … [ILLUSTRATIVE][ASSUMPTION][UNMEASURED]"，且其负载是 **1.3 rps**，不是本小案例的 12.5/50 rps 剖面。
- **修复**：改为 "Chapter 14's illustrative case uses p95 TTFT 1.9 s [UNMEASURED]"，并注明负载不同。
- **验证**：已验证（源对源）。

### FTF-N06 — Ch14 引 Ch6 断言"5 s 尾部突破 p95 SLO"，与 Ch6 结论相反
- **位置**：Ch14 §5，PDF p232（源 `chapter-14.md:112`）。
- **证据**："A 0.84 s mean hides a 5 s tail that **breaches the p95 SLO (Ch6)**." Ch6（源 :51）："p50 ≈ 0.80 s, p90 ≈ 0.94 s, **p95 ≈ 0.99 s**, p99 ≈ 1.33 s … **even p99 (≈1.33 s) still looks healthy**. The 5 s stragglers are the top 1% … between the 99th and 100th"。
- **复算**：p95 = 0.99 s < 2 s SLO；5 s 尾部只在 p99.9/max 可见，属 p99 之后的 1%，**不进 p95**。
- **修复**：改为 "breaches the p99.9/max view (Ch6: p95 ≈ 0.99 s, p99 ≈ 1.33 s, both healthy)"。
- **验证**：已验证。

### FTF-N07 — Ch5 源文"0.8 ms on a single CPU core"算术上不可能（该段当前未渲染，见 N01）
- **位置**：源 `chapter-05.md:62`（PDF 中缺失）。
- **证据**：Δ = 2 × (110M − 23M) × 64 ≈ **11.1 GFLOP**（用本章表 5-1 自己的参数量与 L=64）。
- **复算**：0.8 ms ⇒ 13.9 **TFLOP/s 单核**；单核现实 30–200 GFLOP/s ⇒ **56–370 ms**，与全句所称"well within the ~120 ms retrieval budget"直接冲突（最好情况也占预算 47%，最坏 3×）。
- **修复**：改为"数十至数百 ms 量级，需与 120 ms 预算一起实测"，或改用 GPU/批量编码；并把 Takeaway 中"不引入威胁 TTFT 的每请求延迟"一并复核。
- **验证**：已复算；注意该段当前不在 PDF 中（N01）。

### FTF-N08 — Ch15 开篇/小案例的主机数与全书 ~21 台口径冲突
- **位置**：Ch15 开篇 PDF p235（源 :5）、小案例 p247（源 :100）。
- **证据**：开篇 "how do we **configure an 8×H100 host** to serve a 70B model **at 40 requests-per-second peak**"；小案例 "traffic rises to ~12.5/50 rps … The team provisions **a second 8×H100 host**"（即 2 台扛 50 rps）。Ch4:181/Ch8:65/Ch16/Ch17 同工况为 **~21 台**（40 rps 峰值；50 rps 需 ~26 台全利用/36 台@70%）。
- **复算**：λW = 50 × 8.6 = 430 在途 ÷ 17.5 = 24.6 → ~26 台；2 台差一个数量级。源 :102 的"吞吐跳变"免责注只覆盖 8,000→70,000 的读法，**不覆盖主机数**。
- **修复**：开篇改为"单机在 40 rps 峰值下的角色（per-request 容器，机队见 Ch17）"；小案例显式声明"本例为单机/双机微基准，不代表机队配置"。
- **验证**：已验证（与 Ch8:65 的 Scope 段对照）。

### FTF-N09 — Ch22 称 10/40 rps 是"derived, not stipulated"，与 Ch4 的证据标签相反
- **位置**：Ch22 Step 2，PDF p332（源 `chapter-22.md:23`）；对照 Ch4 源 :132。
- **证据**：Ch22 "The canonical scenario settles on ~10 requests/s average, with peaks of ~40 rps. **These are derived quantities [ILLUSTRATIVE][DERIVED], not stipulated.**"；Ch4 "the ~10 rps average / ~40 rps peak are **declared traffic assumptions (scenario inputs), not derived from the user count**"。
- **为什么是问题**：同一组全书核心输入，一个章标 [DERIVED]、一个章标"声明的假设、不可由用户数导出"（Ch4 自己按 2,000 用户导出只有 0.625 rps）。证据分类轴自相矛盾，且 Ch22 正是教这套分类的章。
- **修复**：Ch22 改为 "[canonical scenario][ASSUMPTION] — declared scenario inputs（同 Ch4），其下游乘积才是 [DERIVED]"。
- **验证**：已验证（源对源）。

### FTF-N10 — Ch23 表 23-1 给出对话中从未确立的"成本"边界，违反本章自己的覆盖度规则
- **位置**：Ch23 PDF p342（源 `chapter-23.md:70`）；对话源 :52–57；规则源 :76。
- **证据**：表 23-1 行 "How much can it cost? | TCO (Ch16) | **within self-host budget**"。但对话里建筑师把问题与数据敏感度**合并**提问，客户只回答了 on-prem（"keep it on-prem if at all possible"），**从未给出任何预算**；随后的 mirror 复述（源 :56，文本称其"locks the scope"）只含 5 项：用户/流量、token、SLO、质量、运维 —— **无成本**。而本章 §4.1 规定："Bound coverage — did the conversation surface all six numbers (traffic, tokens, SLO, quality, **cost**, ops)? **Missing one is a future scope surprise.**"
- **为什么是问题**：核心交付表含无来源的行；本章范例恰好违反本章自设的验收指标。
- **修复**：或在对话中补一句客户预算并进 mirror 复述，或把该行改为 "not surfaced in this dialogue — logged as an open assumption (to be verified)"。
- **验证**：已验证（对话全文核对）。

---

## P3

### FTF-N11 — Ch5 "~1 GFLOPs per embedding" vs 表 5-1 "~14 GFLOPs"（同量 14×）
- **位置**：Ch5 小案例 PDF p103（源 :179 附近）；表 5-1 源 :53。
- **证据**：小案例 "768‑dim embeddings give adequate retrieval quality at **~1 GFLOPs per embedding**"；表 5-1 "all‑mpnet‑base‑v2 | 768 | ~110M | **~14 GFLOPs**（64-token query）"，§3 亦写 "≈14 GFLOPs"。复算 2×110M×64 = 14.08 GFLOP ✓；小案例未声明不同的查询长度（若 L=8 才是 1 GFLOP）。
- **修复**：小案例改为 ~14 GFLOPs（64-token）或显式写明所用 L。
- **验证**：已复算。

### FTF-N12 — Ch4 成本表行标"Self-host"，实际用的是 Ch16 的 cloud 口径
- **位置**：Ch4 表，PDF p85（源 `chapter-04.md:188`）。
- **证据**：行名 "**Self-host** cost per million tokens (whole-fleet infrastructure ÷ offered token rate)"，推导列却是 "**$120/hr whole-fleet at ~6 hosts** … ~$0.362/1M input（≈2.76M input tokens per cloud dollar）"。$120/hr = 6 × $20/hr **按需云价** = Ch16 的 cloud 腿（$87,600/mo ÷ 730 = $120/hr）；Ch16 的 "self-host" 是 **$155,816.93/mo（≈$213/hr）≈ $24.97/1K**。
- **为什么是问题**：同一标签"self-host"在两章相差 1.78×，且 Ch4 行内自己写"per cloud dollar"。
- **修复**：行名改 "Cloud-equivalent whole-fleet cost per million tokens"，或换用 $155,816.93/mo 口径并注明。
- **验证**：已验证（$120/hr ↔ $87,600/mo 换算复核）。

### FTF-N13 — Ch3 表 3-2 "active ~14B" 与本表自己的推导不符（应 ~13B）
- **位置**：Ch3 表 3-2，PDF p56（源 `chapter-03.md:91`）。
- **证据**：Total 行 "~5.7B per expert × 8 ≈ 45.6B + always-on … ≈ 47B" ⇒ always-on = **1.4B**；Active 行 "2 routed FFN experts + always-on … ≈ **14B**"。
- **复算**：2 × 5.7 + 1.4 = **12.8B**（按"per-expert rounded to ~6B"也只有 13.4B）；Mixtral 8x7B 公开值 active = **12.9B**、total 46.7B。下游 "active/total ~30%（29.8%）"、"~28 GB active weight-read"、"~0.028T FLOPs"、"~0.20× vs dense" 均随 14B 走（用 12.9B 则为 27.6% / 25.8 GB / 0.0258T / 0.184×）。
- **修复**：全表统一为 ~13B（或把 always-on 改为 ~2.6B 并说明构成）。
- **验证**：已复算。

### FTF-N14 — Ch6 图 6.2 阅读注与正文结论相反
- **位置**：Ch6 图 6.2 注，PDF p108（源 `chapter-06.md` 图注）。
- **证据**：图注 "yet **p99 paints a very different picture under a 2 s SLO**"；正文（源 :51）"**even p99 (≈1.33 s) still looks healthy**"（p99 < 2 s；只有 p99.9/max 才见 5 s 尾部）。
- **修复**：图注改为 "only p99.9/max surfaces the 5 s stragglers under the 2 s SLO"。
- **验证**：已验证。

### FTF-N15 — Ch7 表 7-1 单位链不自洽："= 2,560 KB = 2.5 MiB"（KB/KiB 混用）
- **位置**：Ch7 表，PDF p120（源 `chapter-07.md:56`）。
- **证据**：行 "2 ×80 ×8192 ×2 B ≈ 2.62 MB | = **2,560 KB** = 2.5 MiB; exact decimal 2.62 MB"。复算 2,621,440 B = 2,560 **KiB** = 2.5 MiB = 2,621.44 kB；十进制 2,560 KB = 2.56 MB ≠ 2.62 MB。全书其余处严格区分 MB/MiB，此行把二进制值标成 KB。
- **修复**：改为 "= 2,560 KiB = 2.5 MiB"。
- **验证**：已复算。

### FTF-N16 — Ch8 结尾注用二进制 K，与 Ch4 声明的 SI 约定冲突
- **位置**：Ch8 §8 结尾，PDF p160（源 `chapter-08.md:298`）。
- **证据**："~0.29 PFLOP at 2K → **~4.6 PFLOP at 32K**"。Ch4:85 明确 "K = 1,000 … 32K means 32,000"。
- **复算**：2×70e9×32,000 = **4.48 PFLOP（≈4.5）**；4.6 来自 32,768。同句 2K：2,000 ⇒ 0.28（0.29 来自 2,048）。
- **修复**：改为 "~0.28 → ~4.5 PFLOP"，或注明"此处 K 取 2 的幂"。
- **验证**：已复算。

### FTF-N17 — Ch24 同一"prompt-scanning 层"的建模效果两处不同（−60% vs −34%）
- **位置**：Ch24 §6.1 PDF p354（源 :135）vs §8 小案例 p355（源 :156）。
- **证据**：§6.1 "adding a prompt‑scanning layer … we model this as … **reducing PIES by ~60%**"（217 → ~87）；§8 "**PIES has dropped from 217 to 143** after adding a prompt‑scanning guardrail"（−34%）。
- **说明**：两处均标 [ILLUSTRATIVE][ASSUMPTION]，属假设输入不一致而非实测矛盾；但同一干预两种建模效果，且 60% 会直接达标（<150）、34% 只是勉强达标，结论不同。
- **修复**：统一为一个值，或注明 §6 是"更强的 LLM 分类器"、§8 是"轻量扫描"。
- **验证**：已验证（两处引文）；性质上属假设不一致，严重度按 P3。

### FTF-N18 — Ch11 把 9.2K 的 prefill FLOPs 说成"for those 8K tokens"
- **位置**：Ch11 PDF p192（源 `chapter-11.md:72`）。
- **证据**："Without caching, every request re-runs the **~1.29 PFLOP prefill for those 8K tokens**"。1.29 PFLOP = 2×70e9×**9,200**（Ch8 表 8-1）。
- **复算**：8K 部分 = 2×70e9×8,000 = **1.12 PFLOP**（差 13.7%）。
- **修复**：改为 "the ~1.12 PFLOP attributable to the shared 8K (of the 1.29 PFLOP full prefill)"。
- **验证**：已复算。

### FTF-N19 — 附录 A "Hybrid-attention models cut it 4–10×" 与本附录自己的 7%（=14×）不符
- **位置**：附录 A §5，PDF p388（源 `chapter-27.md:89`）；数据在 p386（源 :57）。
- **证据**：§5 "Hybrid‑attention models cut it **4–10×** at the mechanism"；§1 自己写 DeepSeek-V4 KV = "~10% (Pro) / **~7% (Flash)** of V3.2"，§4 GLM "4.4× smaller"。
- **复算**：1/0.07 = **14.3×**、1/0.10 = 10×、GLM 4.4× ⇒ 实际区间 **4.4–14.3×**。
- **修复**：改为 "4–14×"（或 "4–10× (Pro) / up to ~14× (Flash)"）。
- **验证**：已复算。

---

## 已排查、确认**不是**问题（避免后续重复发现）

- **Mooncake 525% / +75%**（Ch11 [S4]）：与 arXiv 2407.00079 摘要逐字一致（"up to a 525% increase in throughput in certain simulated scenarios … 75% more requests"）✓（FAST'25 版为 59–498%/115%/107%，但书引用的是 2024 arXiv 版，标注正确）。
- **[S4] 含 DistServe**：Ch11 源 :29 的 S4 条目确含 Splitwise+DistServe+Mooncake ✓（先前疑为引用缺失，已排除）。
- **[S1]–[S7] 标签**：references.tex 定义 7 条，正文/附录使用一致，无悬空 S 标签 ✓。
- **Ch9 环通信算术**（245 GB/0.54 s/6.1 s/98 s/11×/180×/54-610-9800 s）、**Ch10 PP 加速 32/11、128/35**、**Ch7 量化字节数**（MXFP4 8,912,896 / NVFP4 9,437,188 / INT4 8,716,288 / 70B 混合 39.24375 GB / 17→21 序列）、**Ch8 注意力二次项 +17%/+60%/+240%、L\*=53.4K、KV 修正饱和 5.8 FLOP/B**、**Ch24 PIES 768、p=0.00104、E=52、5.4×0.024=0.13**、**Ch26 均值 180 ms vs p99 250 ms、−44%/−48%、$0.013**、**Ch21 216,000/$5,394/$3,032/60×**、**附录 A 四模型 active%（3.7/4.6/5.6/4.8）** —— 全部复算通过 ✓。
- **源 vs r27 构建源**：ch1–15、21–26 字节级一致；仅 ch27 有差异（附录为 R10 在办项，未在本 pass 展开）。
- **段落级源↔PDF 丢失扫描**（全部 focus 章、>150 字段落、字母数字归一化比对）：唯一真丢失为 FTF-N01；其余 11 条候选经逐条复核均为 LaTeX 数学/链接造成的假阳性（如 "Fig 3.4" 实为 "figure 3.4:"、公式段含 `\approx`）。

## 存疑 / 未证实（如实标注）

- **FTF-N17** 性质是"两个假设输入不一致"，若编辑认为 §6/§8 是不同强度的干预，可降级为编辑性统一。
- **FTF-N13** 的 14B 若按"router + shared expert + embeddings 全算 always-on"重算需 ~2.6B always-on，与同表 Total 行的 1.4B 冲突；无论哪种读法都到不了 14B。
- **FTF-N01 的丢失机制**未定位（r27 `render/build/` 只剩 PDF，中间 `.tex` 已清理；旧构建 `ch08_integration_proof/book.tex` 中该段存在，说明是较新构建引入的回归）。
- 未做：图形文件本身的像素级核对（另有 figure vision 任务）、ch16–20 深改章、ch27 与 r27 源差异的逐字 diff（属 R10 范围）。