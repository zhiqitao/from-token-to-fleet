# 图表矢量化审计（fig-vectorize）— 2026-11-01

目标：让构建 `md_to_latex.copy_figures` 嵌入矢量 PDF（更小 + 印刷锐利），而不是栅格 PNG。
守卫规则：同名 `.pdf` 的 mtime **≥** `.png` 才会被采用；否则回退栅格 PNG。
范围：仅本次触及的 9 张图 + 新增证据；未做整书构建 / git 提交 / 委派。

## 状态总览（9/9 全部走矢量，Type3 = 0）

| 图 | 类别 | 生成方式 | pdf 字节 | 页面 (in) | Type3 | 最小落版字号 | pdf ≥ png | 构建取用 |
|---|---|---|---|---|---|---|---|---|
| fig-01-kv-cache | stale-pdf | `render/regenerate_ch1.py`（archify deliver + chromium print-to-pdf） | 24,859 | 6.707×5.127 | 0 | 8.2pt | ✓ | pdf |
| fig-01-token-travel | stale-pdf | `render/regenerate_ch1_token_travel.py`（同上 + 字号下限） | 24,940 | 8.277×5.500 | 0 | 8.1pt | ✓ | pdf |
| fig-19-1902 | stale-pdf | `render/fig_ch19_trend.py` 经 `regen_figs._duo_savefig`（png→pdf，`pdf.fonttype=42`） | 112,018 | 6.100×5.400 | 0 | 8.4pt | ✓ | pdf |
| fig-20-2001 | stale-pdf | `render/fig_ch20_capacity.py` 经 `regen_figs._duo_savefig` | 33,673 | 6.100×5.400 | 0 | 8.6pt | ✓ | pdf |
| fig-27-2705-depth-execution | stale-pdf（有 .svg） | `inkscape …svg --export-type=pdf -o …pdf` | 26,717 | 6.100×4.540 | 0 | 9.4pt | ✓ | pdf |
| fig-08-0803-video-latent-work | 仅 svg（原无 pdf） | `inkscape …svg --export-type=pdf -o …pdf` | 28,938 | — | 0 | 9.4pt | ✓ | pdf |
| fig-03-0304-wan-noise-experts | 仅栅格（无源） | **新** `render/fig_ch3_wan_noise.py` 矢量重绘 | 28,238 | 6.100×3.950 | 0 | 8.5pt | ✓ | pdf |
| fig-07-0707-quantization-layers | 仅栅格（无源） | **新** `render/fig_ch7_quant_layers.py` 矢量重绘 | 31,126 | 6.100×5.830 | 0 | 8.5pt | ✓ | pdf |
| fig-07-0708-block-scale-bytes | 仅栅格（无源） | **新** `render/fig_ch7_scale_bytes.py` 矢量重绘 | 27,103 | 6.100×4.330 | 0 | 8.5pt | ✓ | pdf |

全量复扫 `design/manuscript/chapter-*/figures`（59 个图名）：**stale-pdf = 0，png-only = 0，svg-无-pdf = 0**。

## 1. stale-pdf 重生成（5 张）

按构建同路径重跑生成器；`pdffonts` 全部 0 Type3（TrueType/CID TrueType）。
sha256 前 16 位：`HEAD → 现在`。

| 图 | HEAD sha | 新 sha | 72dpi 栅格比对 |
|---|---|---|---|
| fig-01-kv-cache | `7e22507f73cce827` | `cde5fb412e01e2a4` | 0.0000% 差异（逐像素相同） |
| fig-01-token-travel | `bbb8cd1c2292a983` | `fb03035d2a0fcbc8` | 0.0000% |
| fig-19-1902 | `be6a0b8b8a1357fd` | `6069b09be9b9844f` | 0.0000% |
| fig-20-2001 | `c24513d3eac91f2b` | `91b9431b1677b885` | 0.0000% |
| fig-27-2705 | `5d3e2a3ff882cdae` | `f07fbb29dd0c4a8a` | 0.0000% |

- 页面尺寸与 HEAD 完全一致（pymupdf 逐张核对），字节差异只来自 PDF 元数据/时间戳 → **零视觉变化，纯 mtime 刷新**。
- ch1 两张由 chromium `render()` 先写 pdf 后写 png，天然 pdf 略旧；同一次渲染内两者内容一致，故渲染后 `touch` 对应 `.pdf` 使 mtime ≥ png（内容未变，仅时间戳）。
- fig-19-1902 的 `.png` 由 duo-savefig 重写：`841ebe0b08e8a3f0`(2386×2111, tight 裁切) → `11ddf5fc75f0b92c`(2440×2160 = 6.1×5.4in 整幅)。内容区对齐后仅 0.14% 像素差异（抗锯齿），且新 png 与新 pdf 画布一致（HEAD 时 png/pdf 裁切并不一致）。fig-20-2001 的 png 与 HEAD 逐字节相同（`65e33437edc6ba2f`）。

## 2. SVG → 矢量 PDF（2 张）

- `fig-08-0803-video-latent-work`：原只有 `.svg`+`.png`（无 pdf）→ inkscape 导出，新 pdf `e5885cf9f76446b6`（28,938 B），mtime 晚于 png。
- `fig-27-2705-depth-execution`：pdf 与 png 同秒（视为过期）→ 由 svg 重新导出，`f07fbb29dd0c4a8a`，栅格与 HEAD 相同。
- 两者 `pdffonts`：TrueType / CID TrueType，**Type3 = 0**。

## 3. 三张无源手绘图的矢量重绘（before → after）

重绘依据：读原 PNG（vision 逐项转录框/箭头/文字/配色）+ 章节正文与图注；按 6.1in 版心 1 单位 = 1 英寸作图，故落版字号即所设字号（≥8.5pt）；`pdf.fonttype=42` + `ps.fonttype=42`。**只写 `.pdf`，原手绘 `.png` 原样保留**作栅格回退，新 pdf mtime 晚于 png → 构建取矢量。

| 图 | before | after | pdf sha256 | pdf ≥ png |
|---|---|---|---|---|
| fig-03-0304-wan-noise-experts | 仅 PNG 栅格 276,414 B / 2135×1383（sha `192d721810e95cb4`），无 pdf | 矢量 PDF 28,238 B / 6.100×3.950in（与原图长宽比 1.544 一致），14 个文本 span，DejaVuSans(-Bold) CID TrueType | `f97c859ddcf077c9…`（全值见下） | ✓（pdf 2026-11-01 08:22:36 > png 2026-10-28 10:09:45） |
| fig-07-0707-quantization-layers | 仅 PNG 栅格 371,819 B / 3660×3500（sha `5095160d061b2e10`），无 pdf | 矢量 PDF 31,126 B / 6.100×5.830in（比例 1.046 一致），25 个文本 span | `05942f78ad056848…` | ✓（pdf 2026-11-01 08:22:37 > png 2026-10-28 10:09:45） |
| fig-07-0708-block-scale-bytes | 仅 PNG 栅格 279,387 B / 3660×2600（sha `3a991d9e9c0d18aa`），无 pdf | 矢量 PDF 27,103 B / 6.100×4.330in（比例 1.408 一致），14 个文本 span；条形仍按字节等比 16:1 与 8:8:1:1 | `66caf9395c085071…` | ✓（pdf 2026-11-01 08:15:51 > png 2026-10-28 10:09:45） |

完整 sha256：
- fig-03-0304 `f97c859ddcf077c95700991b60760385e754bbdb24a09b4c108fdbee889e7174`（28,238 B）
- fig-07-0707 `05942f78ad056848623a6dc64b9dd5ca526d656161493bc84185cc671794d3c2`（31,126 B）
- fig-07-0708 `66caf9395c0850714ae33a4b976d23881e9925d947bc93f8b2677b302d52bdfb`（27,103 B）

内容保真（vision 复核 200dpi 渲染）：
- 3.3：标题、蓝色容器 + 两个白色 checkpoint 框、两条虚线箭头、中间两行注释、两个橙色 stage 框 + 黑色实心箭头、4 行脚注 —— 全部在位；无裁切/重叠/溢出；三个箭头尖端均贴住目标框边（首轮箭头尖与框边留 2px 白缝，已把尖端内插 0.015–0.025in 修复后复测为连续深色）。
- 7.3：标题、顶部两框、两条箭头入容器（尖端触内层 Packed tensor 框顶边）、容器内嵌框 + 说明行、`load / repack` 箭头、runtime 框、`compatible dispatch` 1→3 分支、底部三框、2 行脚注 —— 全部在位，无缺陷。
- 7.4：标题/副标题、MXFP4 16B+1B 条 + `1 B scale` 引线、NVFP4 8+8+1+1 条 + 白色括号 + `2 B scales`、两条 Local 行、3 行底部说明 —— 全部在位；两图共用同一左边距与每字节像素比例，右端差恰为 17B vs 18B。

## 4. 验证方法（可复现）

- 过期扫描：按 stem 比较 `getmtime(pdf) >= getmtime(png)`，全 59 图复扫为 0 问题。
- Type3：`pdffonts <pdf> | grep -c 'Type 3'` → 9 张全部 0。
- 落版字号：pymupdf 取全部 span `size × 439.2pt / page_width` → 最小 8.1pt（ch1）/ 8.4–8.6pt（19/20）/ 9.4pt（svg 两张）/ 8.5pt（三张重绘），均 ≥8pt。
- 视觉：pymupdf 170–200dpi 渲染到 scratch 后 vision 复核（缺陷清单 + 元素清单）。
- 未改动任何数值/图注语义；未做整书构建、git 提交或委派。