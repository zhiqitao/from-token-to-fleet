# Task: Liquid AI LFM3 调查 (2026-10-28)

## 目标
从官方一手来源调查 Liquid AI LFM3：
- 官方博客: https://www.liquid.ai/blog/lfm3
- 跟随官方技术报告/论文、HF 模型卡/config、GitHub 代码、license/部署文档

## 交付物 (本目录 research/lfm3-20261028/)
- [x] task.md (本文件)
- [x] report.md (中文，精确，引用一手 URL)
- [x] claims.json (32 条 claim: 逐字证据/来源/status)
- [x] source-index.md (检索时间/hash/URL；原始证据保存于 raw/)
- [x] proposed-insertions.md (映射书稿 Ch3/5/7/8/AppendixA，仅作为 2026-08-30 之后的补充材料)
- [x] 图: figures/lfm3-architecture.svg (可编辑源) + .pdf/.png (渲染件) + figures/QA.md (439.2pt 打印测试: min 8.50pt ≥ 8pt, PASS)

## 约束
- 不得从 LFM2 推断 LFM3 规格 ✓ (所有数字直接来自 LFM3 一手来源)
- 技术报告为骨架，HF/GitHub 交叉验证 ✓ (LFM3 技术报告不存在 → 博客为骨架, HF config/代码交叉验证)
- 记录矛盾/不可得工件 ✓ (report §8: 7 项)
- 不虚构 benchmark 运行 ✓ (全部为厂商披露, 本调查未跑任何 benchmark)
- 不动 manuscript/sharedrenderer/build/commit/push/委派 ✓
- 最终摘要用中文 ✓

## 状态: 完成 (2026-10-28)
关键发现: LFM3 无技术报告(arXiv 0 条)、无官方 GitHub 仓库(404)；24 层 tri-hybrid
(13 conv k=7 / 5 SWA w=256 / 6 global) 由 config layer_types 逐层验证；KV 膨胀仅由
6/24 全局注意力层承担(12KB/token 推导 ≈ 厂商 1.6GB@128K)；基准全部 vendor-run 无独立复现。