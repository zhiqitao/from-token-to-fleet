# P1 图表修复记录 — Fig 22.1 / Fig 26.2 字号 + Fig 6.2 图注（R27 figure-audit 跟进）

对象：`review/publication_v2_20261028/audit/figure-audit.md` 的 3 条 P1（Fig 22.1 图内 7.8pt、Fig 26.2 7.6pt、Fig 6.2 图注仅 86 字符标题）。
方法复刻 fig-19-1902/1903 修复：定位生成器+资产 → 按 6.10in 自然宽度重生成（放置 439.2pt 不缩放）→ 量放置后 in-PDF 最小字号 → 隔离 lualatex 章节构建（无 overflow）→ 核对语义/数字未变。未做全书构建、未跑 git、未委派；只改上述 3 图的生成器/资产/图注 + 本文件。

## 根因（与审计口径一致，程序复测）

| 图 | 资产自然宽 | 放置宽 | 放置比例 | 生成器最小字号 | 放置后最小（前） |
|---|---|---|---|---|---|
| Fig 22.1 | 439.2pt (6.10in) | **417.24pt = 0.95\linewidth**（ch22.tex `width=0.95\linewidth`） | ×0.950 | 8.2pt（ticks/legend 8.5pt） | **7.79pt**（R27 p335 实测 7.79，审计记 7.8） |
| Fig 26.2 | 439.2pt | 439.2pt（`\maxwidth{\textwidth}`） | ×1.000 | 7.6pt（DERIVED 框体） | **7.60pt**（R27 p380 实测） |
| Fig 6.2 | 439.2pt | 439.2pt | ×1.000 | 8.5pt | **8.50pt ✓**（字号本就达标，仅图注 P1） |

即：22.1 的缩水来自 tex 侧 0.95 缩放（非资产宽度），26.2 是作者字号本身 <8pt。

## 生成器 diff（仅字号/几何，数据与文案零改动）

- `render/fig_ch22_divergence.py`：tick `labelsize` 8.5→8.6（两面板）、legend `fontsize` 8.5→8.6（两面板）、右面板注释 `fontsize` 8.2→8.6；加注释说明 0.95\linewidth 放置。8.6 × 0.95 = **8.17pt ≥ 8pt**。
- `render/fig_ch26_feedback.py`：`stage_text` body 8.2→8.6、`stage_text_small` body 7.6→8.6、边标签 trace/validate/adjust+pick pattern/feedback 8.2/8.5→8.6；`BW` 7.4→8.0（加宽三个框，使 `TTFT mean 180 · p99 250 ms` 在 8.6pt 下仍留边距）；1→2 箭头起点改为 `0.8+BW+0.1`（保持原 0.9pt 净空）。放置 ×1.000 → **8.60pt ≥ 8pt**。
- `render/fig_ch6_hist.py`：**未改**（最小 8.5pt 已达标），资产未重生成，sha 不变。

重生成走 `render/regen_figs.py` 同一管线（`_hermes_print_sized` → 去 tight-bbox、按 6.1in 出图），但把 `FIG_SCRIPTS` 限定为上述两个脚本，故只动这两张图。

## 新资产 sha256（design/manuscript 与 render/latex/figures 两处一致）

| 文件 | 旧 sha256（前 12 位） | 新 sha256 |
|---|---|---|
| fig-22-2201.pdf | `ce2379b57604` | `8906712ef1bc3d42b35159e66b10eb9719fd91da2f931161235c2d10b5877fc8` |
| fig-22-2201.png | `476b68906f17`(design) / `68774676869b`(latex) | `51b46c791bd5fe9064da74ef5efc7a58927c383afce4e6e26012721dd3ba2cc1` |
| fig-26-2601.pdf | `b96302d089ae` | `9e436cde7d5a4f4e6761a58ff027fb620cf3e7e801f18b2c219908511e17c5a8` |
| fig-26-2601.png | `2eb05cd0ed7a`(design) | `b377350dbb2e15f0f8018ce15aef03877a0b870c4df0926cd7a21ff20fb1932c` |
| fig-06-0602.pdf / .png | `a15382673c3b` / `4559cd97b374` | **未变**（生成器未改，未重生成） |

资产自检：两图 MediaBox 仍为 439.2×374.4 / 439.2×352.8pt（自然宽 = 6.10in，放置不缩放）；span 文本逐条比对**完全一致**（31/31、18/18 条，无语义/数字变化）；无 span 出画布、无 span 相互重叠；26.2 三框内文字与框边最小净空 ≥3pt（程序 + 200dpi 放大视觉复核均无压边/压字）。

## 放置后 in-PDF 最小字号（隔离 lualatex 构建实测）

隔离构建：scratch `p1_iso/`（复制 `book.sty` + ch06/ch22/ch26 + 5 个 figure 资产，`\DocumentMetadata{testphase=latest}` + `\documentclass[letterpaper,10pt]{book}`，geometry 同书：左右 1.2in → `\textwidth`=439.2pt），`lualatex` 2 遍，27 页，**Overfull \hbox/\vbox = 0，无 `!` 错误**。字号取图内 DejaVu span 的 min size，并用同名 span 宽度比对资产算出放置比例：

| 图 | 前（R27 冻结 PDF） | 后（隔离构建） | 判定 |
|---|---|---|---|
| Fig 22.1 | **7.79pt** | **8.170pt**（scale 0.95000 实测） | RED → **GREEN** |
| Fig 26.2 | **7.60pt** | **8.600pt**（scale 1.00000 实测） | RED → **GREEN** |
| Fig 6.2 | 8.50pt | **8.500pt**（scale 1.00000） | 已 GREEN |

## Fig 6.2 图注（86 → 378 字符，三段式，含义/数字未改）

最终正文（md 源 `design/manuscript/chapter-06/chapter-06.md`、`render/latex/_md/ch06.md` 与 `render/latex/chapters/ch06.tex` 三处一致；tex 用 `\caption[Request-latency distribution]{…}`，短题由 `md_to_latex.short_title` 沙箱实跑得出）：

> Request-latency distribution: the mean looks healthy while a 1% tail at ~5 s breaches the 2 s SLO. Assumption: a synthetic stream of 99% log-normal requests around 0.8 s plus 1% at 5 s, with p50/p90/p95/p99 read off this stream [ILLUSTRATIVE synthetic profile]. Caveat: the shaded band marks the ≥4 s tail only, not the full SLO-violating region between 2 s and 4 s.

三段对应：① takeaway（均值健康、1% ≈5s 尾部击穿 2s SLO）② 假设+证据+状态（99% 对数正态@0.8s + 1%@5s 合成流、分位从本流读出、`[ILLUSTRATIVE synthetic profile]` 与图内标签一致）③ 单条验证 caveat（粉带只标 ≥4s 尾部，非完整违规区 —— 即审计建议的 P2 带语义限定）。所用数字（1%、~5 s、2 s、99%、0.8 s、≥4 s、p50/p90/p95/p99）全部来自图内/正文既有口径，未引入冲突数值；原图注 74 字符内容（p50/p90/p95/p99 + mean）被保留。隔离构建 p4 已确认渲染无误。

## 改动文件清单

- 改：`render/fig_ch22_divergence.py`、`render/fig_ch26_feedback.py`
- 改（重生成资产，design + latex 两处）：`fig-22-2201.{png,pdf}`、`fig-26-2601.{png,pdf}`
- 改（仅 Fig 6.2 图注行）：`design/manuscript/chapter-06/chapter-06.md`、`render/latex/_md/ch06.md`、`render/latex/chapters/ch06.tex`
- 新增：本文件
- 未动：其他章节/图、renderer、style、根目录文件；未做全书构建

## 遗留（非本轮 P1，见 figure-audit）

- Fig 22.1 P2：`2·N` 符号双义、10K 红点无注释；P3：图例线型与曲线不一致。
- Fig 26.2 P3：红边双标签（feedback / adjust + pick pattern）、`sharding ⇒` 悬空。
- Fig 6.2 P2：粉带起点 4s 而非 2s SLO 线（本轮仅在图注加 caveat 限定，未动图形）。
- ch22.tex 的 `width=0.95\linewidth` 使该图永久 ×0.95：本轮以作者字号 8.6pt 吸收；若日后下调作者字号需记得该系数。