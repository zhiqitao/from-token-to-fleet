# LFM3 调查 — 来源索引 (source-index)

检索时间窗: 2026-10-28T21:23:59Z–2026-10-28T21:38:00Z (UTC)。所有原始证据保存在 `raw/`，hash 为 SHA-256。

| # | URL | 检索时间(UTC) | 本地文件 | 字节 | SHA-256 | 备注 |
|---|-----|--------------|----------|------|---------|------|
| 1 | https://www.liquid.ai/blog/lfm3 | 2026-10-28T21:23:59Z | `raw/blog_lfm3.html` | 8719283 | `6570a6a7be42f81807fc2f5302d44fc79d03516daccc9cca1399a1d393f4450d` | 官方博客全文 HTML(页面标注 OCT 27, 2026) |
| 2 | https://www.liquid.ai/blog/lfm3 (抽取文本) | 2026-10-28T21:24Z | `raw/blog_lfm3.txt` | 32281 | `760f9284e431432552464b9d7aaf6aad24f5c67b62783e2ece16a5a03f846ef1` | HTML 去标签纯文本，860 行 |
| 3 | https://huggingface.co/LiquidAI/LFM3-1.7B/raw/main/README.md | 2026-10-28T21:26:37Z | `raw/hf_LFM3-1.7B_README.md` | 53353 | `ca4ea3e8ddda8690b0479d0bbcdd4539f92d42e0092aa396a2bd29a75b6d59d8` | HF 模型卡(骨架交叉验证层) |
| 4 | https://huggingface.co/LiquidAI/LFM3-1.7B/raw/main/config.json | 2026-10-28T21:26:37Z | `raw/hf_LFM3-1.7B_config.json` | 1454 | `8c6ae8b8f6d88c87cfb98cf4b5e34e943d0ee07e24215c4121b3159a46e1399d` | 架构权威配置 |
| 5 | https://huggingface.co/LiquidAI/LFM3-1.7B-Base/raw/main/README.md | 2026-10-28T21:26:37Z | `raw/hf_LFM3-1.7B-Base_README.md` | 10727 | `b135e4bc5150269fe1028021dadcec8f3478f5e4ff46bcd91e34bf9ea51cf8f0` | Base 模型卡 |
| 6 | https://huggingface.co/LiquidAI/LFM3-1.7B-Base/raw/main/config.json | 2026-10-28T21:26:37Z | `raw/hf_LFM3-1.7B-Base_config.json` | 1454 | `8c6ae8b8f6d88c87cfb98cf4b5e34e943d0ee07e24215c4121b3159a46e1399d` | 与 instruct config 字节级相同(同 hash) |
| 7 | https://huggingface.co/LiquidAI/LFM3-1.7B/raw/main/LICENSE | 2026-10-28T21:27:52Z | `raw/hf_LFM3-1.7B_LICENSE.txt` | 10574 | `4d28ca14dedc0b3d0fcc2b3339f0e79931faa33874f3d24f522183a8fc70068c` | LFM Open License v1.0 全文 |
| 8 | https://huggingface.co/LiquidAI/LFM3-1.7B/raw/main/modeling_lfm3.py | 2026-10-28T21:34:18Z | `raw/modeling_lfm3.py` | 42359 | `e8cd5254ea99ce6bd731b57b10908c2e8b5010ce8315341f895a38484885eeab` | 官方建模代码(trust_remote_code) |
| 9 | https://huggingface.co/api/models/LiquidAI/LFM3-1.7B | 2026-10-28T21:27:52Z | (内联保存于报告) | — | — | lastModified/sha 元数据 |
| 10 | https://huggingface.co/api/models?author=LiquidAI&search=LFM3&limit=100 | 2026-10-28T21:34:18Z | `raw/hf_lfm3_repos.json` | 18712 | `4c6b00ebdcf4eef78c1900476e7b01670964de1fc3c9e1d2097968bfaac17dd7` | 家族/量化变体清单 |
| 11 | https://huggingface.co/api/models?author=LiquidAI&search=d1&limit=50 | 2026-10-28T21:36:48Z | (内联) | — | — | d1 决策模型清单 |
| 12 | https://export.arxiv.org/api/query?search_query=ti:%22LFM3%22+OR+abs:%22LFM3%22 | 2026-10-28T21:34:18Z | `raw/arxiv_lfm3_ti.xml` | 728 | `385b5fafec91b3b16678a7f7381be8f585d4a1d2bcd33c593ddcc01deab651c8` | 0 条 — 无 LFM3 技术报告 |
| 13 | https://export.arxiv.org/api/query?search_query=all:%22LFM3%22 | 2026-10-28T21:29:54Z | `raw/arxiv_lfm3.xml` | 698 | `aa5a0b03b93c5eb7da09010c7ad95c1668035440aa952bc68f9c17bcab95e975` | 0 条 |
| 14 | https://huggingface.co/api/papers/search?q=LFM3 | 2026-10-28T21:38:00Z | (内联: []) | — | — | HF papers 无 LFM3 |
| 15 | https://www.liquid.ai/research | 2026-10-28T21:29:54Z | `raw/research.html` | 242153 | `db7578375e38a826f205c596874d4fca0894045498d59b9de33a8404880e4185` | 无 LFM3 报告链接(含 LFM2 报告 2511.23404) |
| 16 | https://github.com/LiquidAI/lfm3 | 2026-10-28T21:27:52Z | (HTTP 404) | — | — | 官方 GitHub 仓库不存在 |
| 17 | https://api.github.com/orgs/LiquidAI/repos | 2026-10-28T21:34:18Z | `raw/gh_repos.json` | 146 | `0cc3650c49f3c14e0efbb3edd0ade9e3bc22b2ebf62f8a220bd4df8ef81c7f33` | 404(该 org 名不存在) |
| 18 | https://api.github.com/orgs/liquid-ai/repos?per_page=100 | 2026-10-28T21:36:48Z | `raw/gh_liquidai_repos.json` | 12088 | `d9b606d1db2f2edc84e99f64ac42e18e96a5c121c505a76e83546cca866dc8a3` | 仅 Plankton、Vehicles，无 LFM3 |
| 19 | https://api.github.com/search/repositories?q=lfm3+in:name | 2026-10-28T21:36:48Z | `raw/gh_search.json` | 109760 | `59935dcea58a4432a57bdf923cae56d5ef7d088026717de374ea64a71e8b46a5` | 仅第三方仓库，非官方 |
| 20 | https://docs.liquid.ai/lfm/models/lfm3-1.7b | 2026-10-28T21:31Z | (web_extract 内联) | — | — | 官方文档规格表 |
| 21 | https://docs.liquid.ai/deployment/gpu-inference/vllm | 2026-10-28T21:31Z | (web_extract 内联) | — | — | 仍仅描述 LFM2.5(vLLM) |
| 22 | https://huggingface.co/blog/LiquidAI/lfm3 | 2026-10-28T21:29Z | (web_search 摘要+抽取) | — | — | HF 官方博客，Published October 27, 2026 |

## 检索方法说明
- HTML 由 `curl -sL` 原样保存；文本抽取脚本去 script/style/标签后存 `raw/blog_lfm3.txt`。
- HF 模型卡/config/LICENSE/modeling 代码均取 `raw/main` 分支原始文件。
- arXiv 结论基于官方 export API 的 `<entry>` 计数(0)。
