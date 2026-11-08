# LFM3 架构图 — QA 与打印可读性测试

## Parent correction — supersedes the original PASS below

The original font-only PASS did not establish text fit. Parent raster inspection found three right-edge text truncations and a legend overlap. Inkscape object bounds also found the last footer below the page edge. These were real defects, not font-floor failures.

Canonical regeneration: `python3 research/lfm3-20261028/figures/regenerate.py`.

- Shortened long labels, separated the legend, and added a right margin to the 24-cell strip.
- Moved footer baselines above the page edge without reducing 8.5 pt text.
- Removed the unsupported universal “no technical report exists” statement.
- Replaced “last 6 tokens” with a fixed kernel-state buffer: the inspected implementation accepts conv-state widths 6 or 7; kernel width is not proof of one universal allocation shape.
- Made sliding-window retention conditional on runtime cache cropping.
- Reclassified the 1.6 GB figure as vendor-reported, not a confirmed runtime measurement.
- Replaced decimal `12 KB` with exact `12 KiB` per token.
- Regenerated vector PDF and 400-DPI PNG. Two successive driver runs passed: 52 text-object bounds inside canvas, zero same-baseline text collisions, min 8.5 pt, Type3=0, layer counts 13/5/6. See `parent_geometry.json`.
- Parent visual reinspection of the regenerated PNG confirmed complete label endpoints, no legend overlap, no card overflow and complete footer lines.

Boundary: standalone-figure acceptance only. Not embedded in a frozen book PDF; no runtime benchmark, physical print proof or accessibility conformance established.

## Historical worker QA (font-only; superseded where contradicted)

- 图：`lfm3-architecture.svg`（可编辑源，7,539 B）→ `lfm3-architecture.pdf`（矢量，34,081 B）+ `lfm3-architecture.png`（192 DPI 预览，290,241 B）
- 渲染：Inkscape（SVG→PDF/PNG），2026-10-28
- 性质：独立说明图（非厂商美术图）；仅传达一手确认机制：24 层 tri-hybrid 逐层序列、三类层解码状态缩放、12KB/token 推导链

## 内容正确性验证

- 逐层序列由 `raw/hf_LFM3-1.7B_config.json` 的 `layer_types` 程序化生成并程序化回验：
  - G（global attention）单元 x ∈ {44, 116, 188, 260, 332, 404}；S（sliding）x ∈ {80, 152, 224, 296, 368}；其余 13 个为 conv。
  - 颜色→类型映射回验输出 `mismatches: []`（初稿曾把 G/S 位置互换，已修复并复验）。
- 计数：conv=13、SWA=5、global=6，与博客原文、HF 卡、docs 四处一致。
- 推导数字：6×2×4×128×2B = 12,288 B/token；×131,072 ≈ 1.61 GB（与厂商 1.6GB 一致）；SWA 5×2×4×128×256×2B ≈ 2.6 MB。

## 打印可读性测试（439.2pt 栏宽，≥8pt 门槛）

方法：pymupdf 读**矢量 PDF 文本层**全部 span（非截图估算）。

```
PDF page width: 439.20pt (column 439.2pt) -> downscale factor 1.0000
span count: 227
min span: 8.50pt  text='"1.'  font=DejaVuSans
effective on-page min: 8.50pt
PASS >=8pt
fonts: {'DejaVuSans', 'DejaVuSans-Bold'}   Type3 present: False
```

- **结果：PASS**。图按栏宽 439.2pt 原尺寸授权（viewBox=439.2×252），放置时无缩放（factor=1.0），最小有效字号 **8.50pt ≥ 8pt**。
- 字体为 DejaVu Sans / Bold，无 Type3 字体（可访问性友好）。
- 5 个最小 span 均为 8.50pt（正文注记字号），无更低字号。

## 备注

- 该图为本调查独立绘制，图内页脚已标注来源、检索日期与 "Post-2026-08-30 supplemental material"。
- 未接入书稿 shared renderer / build（按任务约束）；如需入书，仅作为另行标注日期的补充材料（见 ../proposed-insertions.md）。