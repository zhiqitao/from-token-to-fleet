# FTF-nov1e — 2026-11-01 3 项新 P1 + 1 项 P2 的复算与跨章对齐证据

- **范围**：`design/manuscript/` 4 章（chapter-17 / chapter-03 / chapter-12 / chapter-15）+ 图生成器 2 个（`render/fig_ch17_capacity.py`、`render/fig_ch3.py`）+ 其图资产 4 个（`fig-17-1701.{png,pdf}`、`fig-03-0301.{png,pdf}`，原地重生成）+ 本证据文件 + `review-nov1e.diff`。
- **未做**：未改 renderer 管线文件（`render/latex/md_to_latex.py`、`render/latex/book.sty`、`render/build.sh`，三者 mtime 仍为 10-29/10-30）、未改 `render/check_*.py`、未做全书 build、未 git、未动 `review/.../work/*` 历史 proof 副本。
- **备份**：`~/.hermes/profiles/muta/cache/scratch/nov1e/before/`（6 份修复前源文件 + `sha_before.json`、`sha_after.json`）；另在 `scratch/nov1e/before_fig17/`、`before_fig3/` 用**修复前生成器**重生成旧图，用于取证（见 §1、§2）。
- **完整 diff**：`review/publication_v2_20261028/audit/review-nov1e.diff`（`diff -u` 字节精确，6 文件 = 10 个 hunk、23 条 `-` 行 / 40 条 `+` 行）。

## SHA-256（before → after）

| 文件 | before | after |
|---|---|---|
| `design/manuscript/chapter-17/chapter-17.md` | `84ef1e549d3b8425c847699614fc9742cccf6cdbe5fa8f1cd24b6ad23dbeb41c` | `f9e46333aba4c3d84b660e3d5830a201e24d7d27dec4c73ad6a15fccd4330412` |
| `render/fig_ch17_capacity.py` | `c822f3d91c26bd63712a6967d990d7f941da4e176d74d1addcea66e11b5e8951` | `3717983eb3f454fdaad07078339b7fd7d8986bbf79695031ef4c210516b89e1b` |
| `design/manuscript/chapter-17/figures/fig-17-1701.png` | `fe7ed149aca16220b08912d8a13d6ca62b1ec53f47301f0ab1159ea024f189f4` | `56f1457dc6acbe7e9ac764cb94141183de945c59468149994aef5b547ba4e247` |
| `design/manuscript/chapter-17/figures/fig-17-1701.pdf` | `15c49bbada5a0394579db5483ab7949f572096e387cb9fd4afb0e0e84e73d8ee` | `f9074bfed5189a61a9b0a713b9781a35853d4816d87caae663a45de4a9286b32` |
| `design/manuscript/chapter-03/chapter-03.md` | `507ee232ea0ceff0c1c1344a5ca74cffde021dc07afa57e60b726242a42f44f6` | `33873f449ce82cd88003962cbf374b5258b1be3c693c3123d203574500bc40cf` |
| `render/fig_ch3.py` | `b2e81c3c21e1724c7e3198e1fd7203ec6462758ea839a258c32f8785c6ba1e03` | `7e7336d5e9d1e2372bfa44f9cd668e48f80240c36dbaf393514872e6f16ee215` |
| `design/manuscript/chapter-03/figures/fig-03-0301.png` | `64769d5626440b87ca35f1b7199fa8b358c699652cb2e8b74bcce5f440432220` | `115ba1aadbc31f6ff7c9699a5973cf9dd915f26a61b81b6a931ace1c689bdb33` |
| `design/manuscript/chapter-03/figures/fig-03-0301.pdf` | `8409b040716d806ef6c0da43a86910ca3e673cd66205fcee4b00211a647456e2` | `bbb20b426b6e3143208c31972097f60269ddf74a54071082a476d271f288e742` |
| `design/manuscript/chapter-12/chapter-12.md` | `27aa2e1f4b39315f4bb5b9c66a97d2edb5377deda89aec959456fa3f75e88e7e` | `4d322fc9b69a47d5d00dad4616692ce73661f229e27dfdc31d17e049d72754c3` |
| `design/manuscript/chapter-15/chapter-15.md` | `9e6a6838fc4465ba6d81c1024f58ac4fef668bbf7805b1c1fdb036172e234dec` | `135ba88419bda60b718fa363ec3115b117dcdd559fa6caf3690bae58f8f00fc3` |

> 图资产 before 值取自前轮证据（`review-nov1c.md` L115-116、`review-nov1-ch3.md` L13-14）；本轮用**修复前生成器**重生成的 PNG 与之**逐字节相同**（`fe7ed149…`、`64769d56…`，234,383 B / 216,196 B），PDF 因内嵌 CreationDate 字节不同但**尺寸完全相同**（47,288 B / 32,698 B），可确认修复前资产即前轮记录版本。

## 1. P1-(1) Fig 17.1 图注 tofu — FIXED（定位更正 + 双向验证）

**定位更正（重要）**：tofu **不在** `render/fig_ch17_capacity.py`，而在 **`chapter-17.md` 的 Fig 17.1 图注**（nov1c 新增的那句）。取证：

- 图注字符集 vs 书籍正文字体（`book.sty` → Linux Libertine O，`LinLibertine_R.otf` cmap）：图注全部非 ASCII 中**唯一缺失**的就是 `≳` U+2273；`ρ` U+03C1、`≈` U+2248、`≥` U+2265、`−` U+2212、`×`、`–`、`—` 均在。
- 最小 xelatex 实证（`scratch/nov1e/tofu_test/t.tex`，同字体）：日志 2 条 `Missing character: There is no ≳ (U+2273) in font Linux Libertine O`；`pdftotext` 输出该行时 `≳` **整字消失**（`rho ≈ x 0.917`），而 `\char"2265` 正常抽出 `≥`、`\char"03C1` 正常抽出 `ρ`。
- 图本身（修复前）**0 notdef**：用备份生成器重生成旧图，`pdftotext` 得 `dash-dot (rho=0.85): ~5.1 < ~5.5, need 0.917.`，无缺字；vision 复看旧 PNG 亦 0 tofu。故图侧本无 tofu，`.py` 中也从未出现 U+2265/U+2273。

**Before → After**

- `chapter-17.md` 图注：`(ρ ≳ 0.917 is needed to clear it)` → `(ρ ≥ 0.917 is needed to clear it)`（1 处替换，count==1）。
- `fig_ch17_capacity.py` 图内注记第 3 行：`'dash-dot (rho=0.85): ~5.1 < ~5.5, need 0.917.'` → `'dash-dot (rho=0.85): ~5.1 < ~5.5, need $\geq$ 0.917.'`（**mathtext 字形**，DejaVu 子集内真实 `≥`，从机制上排除 notdef），并加 3 行注释说明该约定；其余行未动（含 `\u2014` 转义已还原，diff 仅 2 个 hunk）。

**复算**：交叉点 ρ\* = 5.5 ÷ (3 × 2.0) = 0.91666… → **0.917**（3 位）；ρ = 0.85 时 3 × 2.0 × 0.85 = **5.1** < 5.5 ✓。图注与图内注记数字/限定词全部保留。

**重生成后验证**

- `pdftotext fig-17-1701.pdf` → `dash-dot (rho=0.85): ~5.1 < ~5.5, need ≥ 0.917.`（`≥` 为可抽取真实字形，**0 notdef**）。
- vision 复看新 PNG：第 3 行为 `… need ≥ 0.917.`，**全图 0 空框/0 tofu**，注记框与任何文字/线/边框**无重叠**。
- 全稿字体覆盖扫描（`design/manuscript/**/*.md` 全部非 ASCII vs Libertine cmap，排除 `book.sty` 已映射的 ✓✗⌈⌉⌊⌋）：**缺失字符 = 0** —— `≳` 是全稿唯一 tofu 源，已消除。

## 2. P1-(2) Table 3-3 / Fig 3.4 MoE KV 几何不一致 — FIXED（选定唯一几何并全章对齐）

**几何选型（三条路都从第一性原理复算，只留一条自洽的）**

| 方案 | KV/token(8-bit) ×9,200 | always-on 影响 | 结论 |
|---|---|---|---|
| A. 与 dense 同 80L/8192H full-MHA | 2×80×8192 = 1,310,720 B → **12.06 GB**（= 现表值） | attention 权重 4×80×8192² = **21.47B** → always-on ≥21.6B，total 45.6+21.7 ≈ **67.3B**、active 11.4+21.7 ≈ **33.1B(49%)** | ✗ 破坏 `~47B / ~94 GB / ~1.4B / ~12.8B / ~27% / 25.6 GB / 0.183×`（T3-2、T3-3、Fig 3.4、§3、§8 共 30+ 处）→ 否决 |
| B1. 自身 32L/4096H **full-MHA**（题面给的 0.26 MB/token） | 2×32×4096 = 262,144 B → **2.41 GB** | attention 4×32×4096² = 2.147B + embed 0.131 = **2.278B** → total **47.88B**、active **13.68B(29.1%)** | ✗ 同样破坏 1.4B/47B/12.8B/27% 链 → 否决（题面 0.26 MB/token 与 1.4B always-on **互斥**，二者只能取一） |
| **B2. 自身 32L/4096H GQA（8 KV heads × 128，KV width 1024）** | 2×32×8×128 = 65,536 B = **0.064 MB/token** → 602,931,200 B = **0.603 GB ≈ 0.6 GB**（FP16 1.21 GB ≈ 1.2 GB） | attention 32×(4096²+2×4096×1024+4096²) = 1.342B + embed 0.131 = 1.473B ≈ **~1.4B** ✓；total 45.6+1.47 = **47.07 ≈ 47** ✓；active 11.4+1.47 = **12.87 ≈ 12.8** ✓（表内 11.4+1.4 = 12.8 逐字成立） | ✓ **采用**：参数账本 0 改动，只改 KV 账；且正是 "Mixtral 8x7B class" 的真实构型 |

**采用 B2 后的对齐（10 处 ch3 编辑 + 生成器 1 处 + 重生成）**

1. **Table 3-3 KV 行**：`~12 GB | ~12 GB | identical — attention dense` → `~12 GB | ~0.6 GB | set by attention shape, not routing: dense 80L/8192H full-MHA = 1.31 MB/token × 9,200 ≈ 12.06 GB; the challenger's own 32L/4096H GQA (8 KV heads × 128) = 0.064 MB/token × 9,200 ≈ 0.60 GB — a dense model with the challenger's shape holds the same ~0.6 GB [ILLUSTRATIVE][DERIVED]`。
2. **§3 L109**：比较对象显式写成两条几何（dense 80L/8192H full-MHA vs challenger 32L/4096H GQA）。
3. **§3 L112**：`MoE 70B-equivalent: KV identical` → 逐式复算 0.60 GB / 1.2 GB，并写明"差在 shape 不在 routing；同 shape 的 dense 也是 0.60 GB；固定 attention geometry 时 dense vs MoE 仍 identical"。
4. **§3 L114**：`same as dense` → `exactly as a dense model's does at the same attention shape`。
5. **§3 L116 Key takeaway**：KV 预算按**自身 attention shape** 配，shape 未知时按 dense 配（保守界）；保留 `Do not assume MoE reduces KV cache memory`。
6. **§6 L150**：同 shape 才同 KV；challenger 的 0.6 GB 归因于 shape。
7. **Fig 3.4 图注**：`same attention geometry … so the KV footprint is identical` → `same context length and cache dtype` + 三处差异（residency / active fraction / **attention shape**）+ `KV bytes differ by shape, not by routing (~12 GB vs ~0.6 GB at 9.2K/8-bit …)` + `Routing alone never changes KV: hold the attention geometry fixed and dense vs MoE KV is identical (Ch. 7)`；原 caveat（"MoE 若用 GQA 属另一比较"）改为正面陈述本比较的 shape 差。
8. **Fig 3.4 图下文字**：`KV growth … identical to dense` → 线性增长两者相同 + 1.31 vs 0.064 MB/token + `The gap is the shape, not the routing`。
9. **§8 L198**：`same regardless of dense or MoE` → 固定 geometry 才相同；challenger 自身 shape 0.6/1.2 GB；**shape 未知时仍按 dense 速率 ~12 GB(8-bit)/~24 GB(FP16) 配**（保守界，原数字保留）。
10. **§8 L200 (b)**：`(b) With the same attention geometry the KV cache is unchanged` → `(b) Routing does not change the KV bytes` + 0.6/1.2 GB + 仍按 dense 速率 12/24 GB 配。
11. **`render/fig_ch3.py`**：红条 `KV: identical (dense = MoE)` → `dense 12 GB vs MoE 0.6 GB`；其下注 `controlled: same attention geometry, context length, and cache dtype` → `8-bit KV set by shape, not routing:` / `80L/8192H MHA vs 32L/4096H GQA`；注释块同步记录复算与**宽度预算**。

**诚实结论保留**：`MoE alone does not reduce KV bytes` 全程成立 —— 路由从不改变 KV；固定 attention geometry 时 dense ≡ MoE；12 → 0.6 GB 的差**全部**归因于 shape（同 shape 的 dense 也 0.6 GB）；配预算仍取 dense 速率作保守界。Ch1 L47 的表述（"controlled comparison 固定 attention geometry…；用 GQA 的 MoE 可有更小 KV"）与新写法**自洽**，未改。

**图验证**：`measure_fig.py fig-03-0301.pdf` → `MIN-ON-PAGE 8.40` **exit 0**（与前轮 `review-nov1-ch3.md` 记录的 8.40/exit 0 相同，无回退）；pymupdf 实测红条 154.4 pt、条内文字 135.6 pt（左右各 9.4 pt 余量，**完全在条内**）、注记 144.6/150.1 pt < 原最宽行 156.9 pt（**axes/网格几何与修复前逐点相同，无 reflow、未缩字号**）；vision 复看：条内文字无裁切、注记不越界、**0 tofu**。

## 3. P1-(3) Table 12-2 candidate(c) prefill 主机数 — FIXED（单 H100 口径）

**复算**（与 Ch8 同法）：989e12 × 0.35 ÷ 14e9 = **24,725 tok/s**（校验 70B：989e12 × 0.35 ÷ 140e9 = 2,472.5 → ×8 = 19,780 ≈ 书中 ~19,800 ✓）；92,000 ÷ 24,725 = 3.7209 → **~4**；368,000 ÷ 24,725 = 14.8837 → **~15**；8 × 24,725 = **197,800 ≈ 197K** —— 旧格用的正是 **8 卡节点**速率，与 Table 12-1 `1 ×H100` 布局矛盾。

**Before → After（5 处，均 count==1）**

- **Table 12-2 (c) 行**：`~1 (92K ÷ ~197K)` → `~4 (92,000 ÷ 24,725 ≈ 3.72)`；`~2 (368K ÷ ~197K), before headroom` → `~15 (368,000 ÷ 24,725 ≈ 14.88), before headroom`；成本格 `low (single H100)` → `low — single-H100 hosts (~4 avg / ~15 peak cards, not an 8×H100 node)`。
- **Table 12-1 (c) verdict**：`✗ ~2 hosts at peak (Table 12-2)` → `✗ ~4 avg / ~15 peak hosts at the single-H100 rate (Table 12-2)`。
- **§12.3（L25）**：`a single card sustains tens of thousands of prefill tokens/s` → `~24,700 prefill tokens/s (989 TFLOP/s × 35% MFU ÷ 14 GFLOP/token = 24,725; vs ~2,471 per GPU for the 70B, Ch 8)`。
- **Table 12-2 导语（L101）**：`~197K tok/s for the 7B` → `~24,700 tok/s for the 7B on the single H100 its layout declares …; the ~197K figure is the 8-GPU node, 8 × 24,725 ≈ 197,800, not this layout`。
- **读法规则（L109 rule 1）**：补 `candidate (c)'s ~4 / ~15 uses its own single-GPU rate (~24,700 tok/s), not the 8-GPU node's ~197K`。

**一致性**：Table 12-1（`1 ×H100`、`high per-GPU prefill tok/s`、verdict ~4/~15）× Table 12-2（~4/~15、单卡成本口径）× §12.3（单卡 24,700 tok/s）三处同口径；全稿 `~2 hosts at peak` 残留 **0**，`197K` 仅剩 2 处**有意**的来源说明；(a)/(b) 的 ~5/~19、~19,800 未动。

## 4. P2 Ch15 `~37 at the 70% target` 缺政策值 — FIXED

- **Before**：`⌈430/17⌉ = **26 hosts** at full utilization (~37 at the 70% target, Chapter 4), just as the 40 rps peak needs ~21 (Scope note above).`
- **After**：`… (~37 at the 70% target on the ρ = 1 u-only screen, or **39** under the book's provisioning policy that also multiplies the independent ρ = 0.95 — ⌈430/(17 × 0.70 × 0.95)⌉ = ⌈38.04⌉, Chapter 4), …`
- **复算**：⌈430/17⌉ = ⌈25.29⌉ = **26** ✓；u-only ⌈430/11.9⌉ = ⌈36.13⌉ = **37** ✓；政策 ⌈430/11.305⌉ = ⌈38.04⌉ = **39** ✓（与 Ch4 L271 的 37/39 对、Ch17 Table 17-1 政策式一致）。原 26 / 37 / ~21 数字与限定词全部保留，仅补口径与政策值。

## 5. 验证汇总

- `python3 render/check_tables.py` → `all markdown tables: column counts consistent`，**exit 0**。
- `python3 render/check_md_leaks.py` → `no markdown leak risks detected`，**exit 0**。
- `python3 render/check_regressions.py` → `OK - all numeric regression checks passed`，**exit 0**。
- 残留扫描（全稿 `*.md`）：`≳` = 0、`ρ ≳` = 0、`identical — attention dense` = 0、`KV: identical` = 0、`MoE 70B-equivalent` = 0、`need 0.917` = 0、`~2 hosts at peak` = 0；`same attention geometry` 仅剩 3 处且均为**条件式正确表述**（L112/L200/L203 的 "hold/with the same attention geometry … identical"）。
- 图门：`fig-03-0301.pdf` MIN-ON-PAGE **8.40 exit 0**（与前轮相同）；`fig-17-1701.pdf` MIN-ON-PAGE **7.60 exit 1** —— **修复前后完全相同**（用备份生成器实测旧图同为 7.60/exit 1），见 §6-O1。
- 两张图均 `pdftotext` 0 notdef + vision 复看 0 tofu / 0 重叠 / 0 裁切。
- 全稿字体覆盖：缺失字形 **0**（`≳` 为唯一源，已消除）。

## 6. OPEN / 观察项（只报告，本轮不改）

- **O1（既有，非本轮引入）**：`fig-17-1701.pdf` 最小上机字号 **7.60 pt < 8.0 pt 门**（`measure_fig.py` exit 1）。修复前旧图（备份生成器重生成）实测同为 7.60/exit 1，系 nov1c 新增右上 3 行注记时既已存在。要闭门须把该注记 7.6 → 8.0 pt 并重排（宽度 +5.3%），属版面改动，超出本轮 P1 范围 → **OPEN**，建议单独一轮处理。
- **O2（构建侧）**：`render/latex/chapters/*.tex` 与 `render/latex/figures/*` 是**过期构建产物**（`ch17.tex` 中根本没有 `0.917`，`fig-03-0301.pdf` 仍是旧条文），只有越权的全书 build 才会刷新；本轮按约束未做 build → 内容修复以 `design/manuscript/*.md` + `design/manuscript/*/figures/*` 为准。
- **O3（既有舍入）**：Table 3-2/3-3 的 `~1.4B always-on`，按本轮写明的 32L/4096H GQA 构型精确值为 1.342B(attention) + 0.131B(embed) = **1.473B**（≈ "~1.4B"，5% 舍入）。该值为前轮既有、且表内 `45.6+1.4 = 47`、`11.4+1.4 = 12.8` 自洽；KV 推导只用 layers × KV width（精确），故本轮**未改**该数字，仅在此备案。
- **O4（同句兄弟项，未在本轮 P2 范围）**：Ch15 L100 同句的 `~21`（40 rps 峰值，满利用率屏 ⌈344/17⌉ = 21；政策值 31 working / 32 total）仍无口径标注 —— 既有状态，本轮只按指示处理 `~37/39`，`~21` 未动。