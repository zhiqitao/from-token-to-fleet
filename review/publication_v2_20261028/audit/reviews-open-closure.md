# reviews-open-closure — 3 条 OPEN 关闭证据（C P2-11 / D P3-15 / B P3-02）

- 仓库 `/home/ubuntu/hermes-work/from-token-to-fleet`，HEAD `614d3aa8`（R35）；执行 2026-11-01。
- 本轮只改 5 个授权文件；**未动** `render/latex/md_to_latex.py`、`book.sty`、`render/build.sh`、根文件；**未** git commit；**未**全书 build（仅 scratch 内针对性编译）；8 条 EXTERNAL-GATE 未触碰。
- **before sha 取 `git show HEAD:<file> | sha256sum`**：改前工作区 clean（`git diff --stat` 仅含本轮 5 文件；且 ch16/ch17 的 HEAD sha `4dc01246ec81` / `d96d7c94e966` 与 `reviews-consolidated.md` §2 记录一致）。

| 文件 | before (HEAD) | after | 行数 |
|---|---|---|---|
| `render/latex/preface.tex` | `1b3f96faacf5` | `701f5a5f53f0` | 292 → 298 |
| `render/latex/backmatter/glossary.tex` | `912f60683483` | `2f4c68b0f397` | 83 → 98 |
| `design/manuscript/chapter-01/chapter-01.md` | `a9b092dea12f` | `7cd4b01a09c1` | 125 → 125 |
| `design/manuscript/chapter-16/chapter-16.md` | `4dc01246ec81` | `52791059a572` | 257 → 257 |
| `design/manuscript/chapter-17/chapter-17.md` | `d96d7c94e966` | `3d7a3fbe43dc` | 274 → 274 |

---

## 1. C P2-11 — 前言 pp12–19 首读负担（`preface.tex`）

**词数**：2721 → 2665（含本轮**新增** 169 词面板；纯散文 2496，**−225 词 / −8.3%**）。
分节（HEAD → 现）：开篇 309→297、thesis 170→165、组织 232→220、读法 521→470、checklist 217→194、Evidence Discipline 917→1005（面板 +169、散文 −81）、Reading conventions 238→226、currency 84→75。

**事实保全**：55 个关键 token（`v20260913`、`2026-09-13`、`2026-08-30`、`As of 2026-08`、三条 addendum 版本号、`2026-09-27`/`2026-10-28`、DeepSeek、First-hand Sources、Post-cutoff policy、0.989 PFLOPS、3.35 TB/s、H100/B100/B200/H200、`[1P][2°][LAB][ILLUSTRATIVE][canonical scenario]`、FACT/DERIVED/ASSUMPTION/HYPOTHESIS/UNRESOLVED、ANALYTICAL/MODELED/MEASURED/UNMEASURED、Table 4-2、`fig:spine-loop`、`fig:traceability`、Edition history、release log、unit/sanity check…）逐一比对 HEAD：**missing = []**（版本史事实一条未删）。

**Before → After 摘录**

1. 开篇（去重复句）
   - before: `…in one coherent thread. What I found were deep dives into single layers…`
   - after: `…in one coherent thread; what I found were deep dives into single layers…`
2. 场景 caveat 段（保留全部 workload 枚举与 teaching-instrument 限定）
   - before: `…anchored in concrete, reproducible arithmetic rather than abstraction. One caveat… this scenario is a teaching instrument… The canonical scenario picks a single, tractable, input-heavy RAG case and carries it through so the reasoning stays continuous; a real deployment will sit somewhere else in that space, and the chapters are written to give the reader the arithmetic to re-derive the bounds for their point.`
   - after: `…anchored in reproducible arithmetic. One caveat… the scenario is a teaching instrument… The scenario picks one tractable, input-heavy RAG case and carries it through so the reasoning stays continuous; a real deployment sits somewhere else in that space, and the chapters give the arithmetic to re-derive the bounds for your point.`
3. Evidence Discipline 首段（删与面板/末段重复的章节指针）
   - before: `…Axis-3 measurement status rides along with claims whose measurement status is known, not with every claim. …the Sources, Method, and Reproducibility chapter defines these exceptions unambiguously.`
   - after: `…Axis 3, measurement status, rides along where a claim's status is known. …exceptions are defined unambiguously in the Sources, Method, and Reproducibility chapter.`
   - 另删 epistemic 段尾重复的 `and is defined in full in the Sources, Method…`（该指针现由面板末句 + two-habits 段承担，全节由 3 处减为 2 处）。
4. 例示压缩（规则与标签全保留，仅减枚举示例）
   - before: `a traffic level, a latency target, a price, a token count` / `an execution occupancy, a tokens-per-second rate, a cost-per-request, a tokens-per-dollar figure` / `worked example (a ``what-if'' that is not the canonical scenario)`
   - after: `a traffic level, a latency target, a price` / `an execution occupancy, a tokens-per-second rate, a cost-per-request` / `worked example`
5. build identifier 段（事实不变，句式压缩）
   - before: `…does not change the content edition and does not extend the evidence cutoff; it only changes the PDF's generation timestamp, which is recorded in the document metadata and is not evidence.`
   - after: `…changes neither the content edition nor the evidence cutoff --- only the PDF's generation timestamp, which is recorded in the document metadata and is not evidence.`
6. 两张前言图 caption（C P2-11 的 caption 半项）
   - spine caption：删 `before an architecture is committed`、`to re-derive the candidate`、`when the committed architecture reveals a requirements revision is needed` 等冗余，保留 Stage 03 provisional / Stage 04 red-team / inner(绿)·outer(红) 双环语义（`fig:spine-loop` label 未动）。
   - traceability caption：删与图内/alt 重复的六条 prompt 枚举与尾句 `…each chapter still supplies a derived quantity that feeds a decision.`，保留 A/B 两读法、starting-points-not-coverage、Ch22/Ch25 指针（`fig:traceability` label 未动）。

---

## 2. D P3-15 — Glossary 打磨（`backmatter/glossary.tex`，1751 → 2118 词）

**措辞修复（light touch，4 条）**

| 条目 | before（awkward/auto 部分） | after |
|---|---|---|
| ITL | `…the book treats TPOT (steady-state) and ITL (per-token, incl. any measured inter-token gap) as the same canonical per-token metric and writes them ``TPOT/ITL.'' Where a measurement distinguishes them, treat ITL as…i.e. a tail-sensitive complement to bounded TPOT.` | `…per-token lag, including any queueing/scheduling gap between emitted tokens. The book writes ``TPOT/ITL'' for one canonical per-token metric; where a source separates them, TPOT is the bounded steady-state value and ITL the tail-sensitive per-token value that also carries that gap.` |
| MFU | `model FLOPs utilization: achieved FLOPs as a fraction of hardware peak.` | `…achieved model FLOPs as a fraction of hardware peak; a compute-efficiency ratio for a run (the worked examples assume 35%), not a host-occupancy number — see Utilization and efficiency below for how it differs from $u$, $\rho$ and offered-load utilization.` |
| prompt caching | `the broader system/provider term; the book uses it to mean…so it is not a separate mechanism from prefix caching above (Ch 2) — the provider-facing name for the same reuse, kept as its own entry because…` | `the provider-facing name for the prefix caching above: reusing the KV of a shared prompt prefix across requests. Not a separate mechanism (Ch 2); kept as its own entry because providers document and bill it as a feature.` |
| cache hit/miss | `the hit ratio (hits ÷ requests) is the FACT that the prefix- and semantic-cache arithmetic starts from` | `…is the FACT from which the prefix- and semantic-cache arithmetic starts` |

**新增两组（对应 D P3-15 ④ MFU 辨析 + ③ 术语排版区分）**

- `Utilization and efficiency --- four quantities that are not MFU`：`utilization target ($u$)` = 0.70 政策上限（Table 17-1，选定量非测量）；`scheduling efficiency ($\rho$)` = 0.95 LB/调度损失，与 $u$ **独立相乘、不嵌套**（Ch 17 §17.4，交叉引用 Notation 的 ρ 条）；`offered-load utilization (occupancy)` = served ÷ provisioned（Ch 16 Note 16.1-1 原句），占用率非算力效率；`qualitative scenario indicators` = Table 15-1 *Illustrative load pressure*（0–100 无 FLOP 分子分母的序数标签，**deliberately not an MFU**）。
- `Quote which quantity --- memory and latency distinctions`：`raw bytes / allocated cache / observed resident memory` 三口径（Ch 7 §7.4；2.62 / 1.31 MB/token、allocated ≥ raw）；`active weights vs resident weights`（~25.6 GB/token vs ~140 GB / ~94 GB，Ch 3）；`residency duration vs end-to-end latency`（$E[W_{KV-resident}]$ vs $W_{e2e}$，后者**不是** KV 公式里的 $W$，Ch 17；SLO-goodput 两者皆非，指向 goodput 条）。
- 数值全部取自稿内既有值（0.70 / 0.95 / 35% / 2.62 / 1.31 / 25.6 / 140 / 94），未引入新数字。

---

## 3. B P3-02 — Evidence boundary 面板 + 3 处最重重复 caveat 去重

**面板**（`preface.tex:156-164`，`\begin{center}\fbox{\parbox{0.94\linewidth}{…}}\end{center}`，居中短框、单段无 `\par`；改前全库 `Evidence boundary` = **0**，现 = **4**：1 面板 + 3 处引用）

> **Evidence boundary --- four registers, and where each is used.** **MEASURED** — an instrumented run under the Chapter 14 protocol; used only where the book reports a benchmark it actually ran, never for a planning screen. **ANALYTICAL** — arithmetic on stated inputs (roofline, KV-residency and capacity screens, the $C/W$ per-host bound and the host counts derived from it): a bound, not an observed rate — not a measured throughput, not a lower guaranteed rate, not SLO-goodput, no p95/p99 guarantee, each conditional on its stated assumptions (e.g. the assumed mean KV residency time). **ILLUSTRATIVE** — a chosen scenario input or worked example ([canonical scenario] or [ILLUSTRATIVE], paired with [ASSUMPTION] or [DERIVED]), on the book's teaching geometry, to be re-derived per deployment. **HYPOTHESIS** — reasoned but not yet validated (with [UNRESOLVED] for questions the book leaves open), used where mechanism is argued without measurement. Repeated inline caveats in the chapters are one-sentence reminders of this panel; the full label rule set lives in the Sources, Method, and Reproducibility chapter.

**3 处去重（数字/限定语逐项保留；被移走的限定语在面板中原样存在，非删除）**

1. `chapter-01.md:47`（Chs. 1/7 FP8 coefficient）
   - before: `That 8-bit figure is the raw tensor byte-halving of the BF16 value — exactly 50% (1.31 MB vs 2.62 MB). So FP8 KV = raw tensor byte-halving = 1.31 MB/token (exactly 50% of BF16). Any block-allocation/metadata overhead is NOT vendor-measured here and must be filled by a deployment benchmark. The vLLM FP8-KV blog post's often-quoted '54%' is a decode inter-token-latency (ITL) slope, not a memory ratio, so it is not a memory-footprint coefficient here. …re-derive it for the target stack (the geometry and the "do not generalize" caveat are in Ch. 7).`
   - after: `…raw tensor byte-halving of the BF16 value: 1.31 MB/token vs 2.62 MB/token, exactly 50%, with any block-allocation/metadata overhead NOT vendor-measured here and to be filled by a deployment benchmark; the vLLM FP8-KV blog post's often-quoted '54%' is a decode inter-token-latency (ITL) slope, not a memory ratio or footprint coefficient. …re-derive it for the target stack; the standing FP8-KV qualifiers are stated once in the Evidence boundary panel (Preface), and the geometry and "do not generalize" caveat are in Ch. 7.`
   - 保留：1.31 / 2.62 / 50% / NOT vendor-measured / deployment benchmark / 54% / ITL slope / not a memory ratio or footprint coefficient / 9.2K / 12.06 GB / 13.4 GB / 11% / re-derive / Ch 7。删的是**同句自我重复**（`So FP8 KV = … exactly 50% of BF16`）。
2. `chapter-16.md:47`（Chs. 16/17 C/W 上界）
   - before: `…— a necessary capacity screen inside the KV screen, not a second, independent throughput ceiling, not a measured throughput and not a lower guaranteed rate; and the *lower* bound…`
   - after: `…— a capacity screen inside the KV screen, defined in full below (``What kind of number is ~2.0 req/s?'') and in the Evidence boundary panel (Preface); and the *lower* bound…`
   - 保留：17/8.6 = 1.9767、⌈20.24⌉ = 21、case 表全部数字；被移走的三条限定语在**同章 4 行后** `:51` 逐字存在（`not an observed service rate, not a measured goodput, not a lower guaranteed rate, and not an SLO goodput` + `does not add an independent constraint`），并在面板内。
3. `chapter-17.md:136`（queueing counterexample 的 upshot）
   - before: `…— a necessary capacity screen, not a lower guaranteed rate, not a measured throughput, and not an SLO goodput.`
   - after: `…— a capacity screen only; its standing qualifiers (not a lower guaranteed rate, not a measured throughput, not an SLO goodput) are stated once in the Evidence boundary panel (Preface).`
   - 保留：限定语**原样列出** + 面板指针；C = 17.5、W = 8.6 s、2.0 req/s、⌈40/(17/8.6)⌉ = ⌈20.24⌉ = 21、N ≥ ⌈λ/(C/W)⌉ 等数字与推导一字未动。

---

## 4. 有效性验证

- **TeX**：`preface.tex` / `glossary.tex` 花括号净 0、最小深度 0、环境 begin/end 全配对、`$` 计数偶数（8 / 72）。
- **针对性编译**（scratch `texcheck/test-texcheck.tex` = book.tex 同款 preamble + `\usepackage{book}` + `\input{preface}` + `\input{backmatter/glossary}`，`TEXINPUTS=render/latex:`）：
  - `xelatex` 2 pass **exit 0**，`! ` 错误 0，无 Overfull hbox；
  - `lualatex`（`build.sh` 生产引擎）**exit 0**，`! ` 错误 0；
  - `pdftotext` 命中：`Evidence boundary`、`four registers`、`offered-load utilization`、`Quote which quantity`、`raw bytes / allocated cache`、`v20260913+addendum-20261101`、`2026-08-30`×2、`TPOT/ITL`。
- **Markdown**：`check_md_leaks.py` / `check_tables.py` / `check_regressions.py` 全 **exit 0**；三处编辑行 `**` 计数 12/12/4（偶）、反引号偶。
- 未改 renderer 管线与根文件；未做全书 build（按任务要求）。

## 5. 结论

**C P2-11、D P3-15、B P3-02 → CLOSED**（证据见 §1–§4）。`audit/reviews-consolidated.md` §1 对应三行与 §4 OPEN 汇总可据此翻转为 CLOSED（本任务未改该表，留给汇总方）。