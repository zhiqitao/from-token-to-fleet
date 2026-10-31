# Source Verification Ledger — Appendix A (finding FTF-R10)

| Item | Value |
|---|---|
| Finding | **FTF-R10** (P2, App A): pin moving `raw/main` URLs; shrink long machine URLs in print footnotes; produce this ledger |
| Manuscript file owned | `design/manuscript/chapter-27/chapter-27.md` (Appendix A) — the only manuscript file changed |
| Ledger (new) | `review/publication_v2_20261028/audit/source-verification.md` (this file) |
| References checked | **105 unique URLs** (`A-S01`–`A-S105`) — every URL in Appendix A, in pre-edit line order |
| Pin fetch date | 2026-10-30 (UTC) |
| Source retrieval dates preserved | 2026-10-28 (October addendum) · 2026-08-30 (four-family snapshot) |
| Tooling | pandoc 3.7.0.2 (isolated md→latex), Python 3 `urllib`, Hugging Face API, GitHub commits API |
| Pre-edit sha256 | `097cdcd42b6d94d6c451ad1c4d52e64061ea10737ee3b8028d112332f68f5fdd` (byte-identical to all 45 frozen proof copies of this file) |
| Post-edit sha256 | `b0448a468024336f36d547c7b499b6800945f78819e205b3a95342c389fa8082` |

## 1. Rules applied

- **R1 — pin.** Every URL carrying a moving ref (`raw/main`, `/main/`, `resolve/main`, `blob/main`, `tree/main`, `/latest/`, `HEAD`) is replaced by a commit-pinned revision. The commit is the repository tip **at the source-retrieval date** (≤ 2026-10-28T23:59:59Z), fetched from the host's own API — never a commit invented here.
- **R2 — shrink.** In footnote definitions a URL moves to this ledger and is cited in the chapter as a numbered entry `[A-Snn]` when it is **> 60 characters**, or when its footnote carries **≥ 3 URLs** (the dense list footnotes). Short standalone URLs stay inline.
- **R3 — keep if unverifiable.** If no commit can be retrieved, the URL stays as cited and is recorded in §3 as `UNVERIFIED - moving ref, commit not retrievable` with its retrieval date. No placeholder SHA is ever written into the manuscript.
- **R4 — preserve.** `[1P]`/`[2°]` provenance markers, retrieval dates, footnote IDs, footnote ref/def resolution, section headings and figure alt-text are unchanged (counts in §8).

## 2. Pinned revisions (append-only list)

Fetched 2026-10-30 from the host API; every pin was re-fetched and returned HTTP 200.

| Host | Repository | Commit (immutable) | Source entries | Commit retrieved via |
|---|---|---|---|---|
| github.com | `DreamLM/Dream` | `31f94a60d187e3fd481fee3bbc2c732eb94a879c` | A-S44 | GitHub commits API `?until=2026-10-28T23:59:59Z` |
| github.com | `ML-GSAI/LLaDA` | `9182493720ed723ef8031210d85959364e51cbe0` | A-S43 | GitHub commits API `?until=2026-10-28T23:59:59Z` |
| github.com | `QwenLM/Qwen3.8-Flash-Next` | `69885871a64393807d988b27b1b5e380e8f28526` | A-S01, A-S103 | GitHub commits API `?until=2026-10-28T23:59:59Z` |
| github.com | `Tencent-Hunyuan/HunyuanVideo-1.5` | `60783e704160023913bee78f0b47036d393d4dfa` | A-S78 | GitHub commits API `?until=2026-10-28T23:59:59Z` |
| github.com | `VILA-Lab/Flash-dLLM` | `a667345f5746bb74f060c87bae5997fc3de9710c` | A-S48 | GitHub commits API `?until=2026-10-28T23:59:59Z` |
| github.com | `huggingface/transformers` | `a672eb5f474b8b30173e9f96eab66adf292da635` | A-S15 | GitHub commits API `?until=2026-10-28T23:59:59Z` |
| github.com | `inclusionAI/LLaDA2.X` | `a79832985307bb8ac4a43ceeea54168bfb80f0cf` | A-S47 | GitHub commits API `?until=2026-10-28T23:59:59Z` |
| github.com | `zai-org/GLM-5` | `83c03d317378f86f0a012f7c4cd48b6243c7e69b` | A-S27 | GitHub commits API `?until=2026-10-28T23:59:59Z` |
| huggingface.co | `ByteDance/Ouro-2.6B` | `1ed04250da1a9936042725d302e81c8fa2ab5abd` | A-S20, A-S21, A-S22 | HF API `/commits/main`, first commit ≤ 2026-10-28 |
| huggingface.co | `Qwen/Qwen3.8-27B` | `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` | A-S13, A-S14 | HF API `/commits/main`, first commit ≤ 2026-10-28 |
| huggingface.co | `Wan-AI/Wan2.2-TI2V-5B-Diffusers` | `b8fff7315c768468a5333511427288870b2e9635` | A-S54, A-S55 | HF API `/commits/main`, first commit ≤ 2026-10-28 |
| huggingface.co | `deepseek-ai/DeepSeek-V4.1-Flash` | `314113f8a7dadb388215396ba5fbee2c610a04d6` | A-S23, A-S24 | HF API `/commits/main`, first commit ≤ 2026-10-28 |
| huggingface.co | `google/diffusiongemma-26B-A4B-it` | `f7f5b7f5fa82ffc52addd066915886d497f5517b` | A-S37 | HF API `/commits/main`, first commit ≤ 2026-10-28 |
| huggingface.co | `ornith-ai/Ornith-1.5-397B` | `8f6cc8a7aea505364523f84ccf37706e8aea0ee7` | A-S26 | HF API `/commits/main`, first commit ≤ 2026-10-28 |
| huggingface.co | `tomg-group-umd/huginn-0125` | `bb6621b65e90b6a4b9b29ef88dc83866d450470c` | A-S17 | HF API `/commits/main`, first commit ≤ 2026-10-28 |
| huggingface.co | `zai-org/GLM-5.3-Flash` | `46a050bec13002ad29ee795c16e61cf4fa3c4a9c` | A-S28 | HF API `/commits/main`, first commit ≤ 2026-10-28 |

**16 repositories · 22 pinned source entries.** Where the original URL was archived on 2026-10-28 by `research/model-trends-20261028/source-index.json`, the pinned URL's bytes are **identical** to the archived bytes (11/11); the other pins have no archived copy and are recorded as HTTP-200-only.

> **`A-S15` (`huggingface/transformers` → `modeling_qwen3_5.py`).** The moving `main` URL has *drifted* since retrieval (87,818 B now vs 87,748 B archived 2026-10-28). Pinning to the retrieval-date commit `a672eb5f474b8b30173e9f96eab66adf292da635` restores exactly the inspected bytes; pinning to today's `main` tip (`66f51e76…`) would have cited different content. This is the failure mode R10 exists to prevent.

## 3. UNVERIFIED — moving ref, commit not retrievable

| Entry | URL (kept as cited) | Status | Retrieval date | Why |
|---|---|---|---|---|
| `A-S88` | https://docs.habana.ai/en/latest/API_Reference_Guides/HCCL_APIs/index.html | **UNVERIFIED - moving ref, commit not retrievable** | 2026-10-30 | `docs.habana.ai/en/latest/…` exposes no versioned path, tag or commit id (probed the page and `/en/`: no `/en/<version>/` links); HTTP 200, but the ref moves with each docs build |
| `A-S92` | https://docs.habana.ai/en/latest/PyTorch/PyTorch_Model_Porting/Porting_PyTorch_Models_to_Gaudi.html | **UNVERIFIED - moving ref, commit not retrievable** | 2026-10-30 | `docs.habana.ai/en/latest/…` exposes no versioned path, tag or commit id (probed the page and `/en/`: no `/en/<version>/` links); HTTP 200, but the ref moves with each docs build |

These two are the **only** moving refs left in Appendix A. Per R3 they stay printed in their own footnotes (`[^oct-ix-47]`, `[^oct-ix-55]`) instead of being replaced by an unverifiable pin.

## 4. Checked references — every URL in Appendix A

`Ref` = how the URL was cited before this fix; `Status` = disposition after it. Line numbers are pre-edit.

| ID | Source (as cited) | Cited at | Ref | Status | Revision / entry | HTTP | Content check |
|---|---|---|---|---|---|---|---|
| `A-S01` | technical report, 26 August 2026 | body link, L71 | moving | **PINNED** | `69885871a643…` | 200 | ≡ archived 2026-10-28 bytes |
| `A-S02` | Z.ai release article, 2026-08-26 | body link, L75+1 | page-no-ref | **PAGE** | page URL, no ref | 200 | ≡ archived 2026-10-28 bytes |
| `A-S03` | NVFP4 CUTLASS | body link, L214 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S04` | NVFP4 Marlin | body link, L214 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S05` | MXFP4 Marlin | body link, L214 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S06` | block definitions | body link, L216 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S07` | tensor selection | body link, L216 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S08` | Model Optimizer QAT/QAD example, pinned revision | body link, L218 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S09` | Transformer Engine NVFP4 | body link, L220 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S10` | OCP MicroXcaling 1.1 | body link, L222 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S11` | INT4 AWQ preset | body link, L222 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S12` | NVFP4 AWQ preset | body link, L222 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S13` | Qwen, Qwen3.8-27B model card, “Model Overview,” “Benchmark Re… | footnote oct-mt-q27, L272 | moving | **PINNED** | `1d4bf0f2ff60…` | 200 | ≡ archived 2026-10-28 bytes |
| `A-S14` | Qwen, Qwen3.8-27B model card, “Model Overview,” “Benchmark Re… | footnote oct-mt-q27, L272 | moving | **PINNED** | `1d4bf0f2ff60…` | 200 | ≡ archived 2026-10-28 bytes |
| `A-S15` | Qwen, Qwen3.8-27B model card, “Model Overview,” “Benchmark Re… | footnote oct-mt-q27, L272 | moving | **PINNED** | `a672eb5f474b…` | 200 | original drifted since 2026-10-28 — pin restores archived bytes |
| `A-S16` | Geiping et al., “Scaling up Test-Time Compute with Latent Rea… | footnote oct-mt-huginn, L274 | page-no-ref | **PAGE** | page URL, no ref | 200 | ≡ archived 2026-10-28 bytes |
| `A-S17` | Geiping et al., “Scaling up Test-Time Compute with Latent Rea… | footnote oct-mt-huginn, L274 | moving | **PINNED** | `bb6621b65e90…` | 200 | ≡ archived 2026-10-28 bytes |
| `A-S18` | Zhu et al., “Scaling Latent Reasoning via Looped Language Mod… | footnote oct-mt-ouro, L276 | page-no-ref | **PAGE** | page URL, no ref | 200 | ≡ archived 2026-10-28 bytes |
| `A-S19` | Zhu et al., “Scaling Latent Reasoning via Looped Language Mod… | footnote oct-mt-ouro, L276 | page-no-ref | **PAGE** | page URL, no ref | 200 | ≠ archive (dynamic page churn) |
| `A-S20` | ByteDance/Ouro-2.6B, released `modeling_ouro.py`, `OuroModel.… | footnote oct-mt-ouro-code, L278 | moving | **PINNED** | `1ed04250da1a…` | 200 | ≡ archived 2026-10-28 bytes |
| `A-S21` | ByteDance/Ouro-2.6B model card, adaptive-exit and vLLM notes | footnote oct-mt-ouro-card, L280 | moving | **PINNED** | `1ed04250da1a…` | 200 | ≡ archived 2026-10-28 bytes |
| `A-S22` | ByteDance/Ouro-2.6B model card, adaptive-exit and vLLM notes | footnote oct-mt-ouro-card, L280 | moving | **PINNED** | `1ed04250da1a…` | 200 | ≡ archived 2026-10-28 bytes |
| `A-S23` | DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV C… | footnote oct-mt-ds41, L282 | moving | **PINNED** | `314113f8a7da…` | 200 | ≡ archived 2026-10-28 bytes |
| `A-S24` | DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV C… | footnote oct-mt-ds41, L282 | moving | **PINNED** | `314113f8a7da…` | 200 | ≡ archived 2026-10-28 bytes |
| `A-S25` | Ornith Team, “Ornith-1.5: From Self-Scaffolding to Self-Impro… | footnote oct-mt-ornith, L284 | page-no-ref | **PAGE** | page URL, no ref | 200 | ≡ archived 2026-10-28 bytes |
| `A-S26` | Ornith Team, “Ornith-1.5: From Self-Scaffolding to Self-Impro… | footnote oct-mt-ornith, L284 | moving | **PINNED** | `8f6cc8a7aea5…` | 200 | ≡ archived 2026-10-28 bytes |
| `A-S27` | Z.ai official GLM repository, “GLM-5.3 & GLM-5.3-Flash” | footnote oct-mt-glm, L286 | moving | **PINNED** | `83c03d317378…` | 200 | ≡ archived 2026-10-28 bytes |
| `A-S28` | Z.ai official GLM repository, “GLM-5.3 & GLM-5.3-Flash” | footnote oct-mt-glm, L286 | moving | **PINNED** | `46a050bec130…` | 200 | ≡ archived 2026-10-28 bytes |
| `A-S29` | Google DeepMind, Gemini 3.8 Flash model card, published 2 Sep… | footnote oct-mt-gemini, L288 | page-no-ref | **PAGE** | page URL, no ref | 200 | ≠ archive (dynamic page churn) |
| `A-S30` | Google DeepMind, Gemini 3.8 Flash model card, published 2 Sep… | footnote oct-mt-gemini, L288 | page-no-ref | **PAGE** | page URL, no ref | 200 | ≠ archive (dynamic page churn) |
| `A-S31` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S32` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S33` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290+1 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S34` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290+1 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S35` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290+1 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S36` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S37` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290 | moving | **PINNED** | `f7f5b7f5fa82…` | 200 | pinned URL 200; no archived copy to compare |
| `A-S38` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S39` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290+1 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S40` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S41` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S42` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S43` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290 | moving | **PINNED** | `9182493720ed…` | 200 | pinned URL 200; no archived copy to compare |
| `A-S44` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-releases, L290 | moving | **PINNED** | `31f94a60d187…` | 200 | pinned URL 200; no archived copy to compare |
| `A-S45` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-engine, L292 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S46` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-evaluations, L294 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S47` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-evaluations, L294 | moving | **PINNED** | `a79832985307…` | 200 | pinned URL 200; no archived copy to compare |
| `A-S48` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-evaluations, L294 | moving | **PINNED** | `a667345f5746…` | 200 | pinned URL 200; no archived copy to compare |
| `A-S49` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-evaluations, L294 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S50` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-evaluations, L294 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S51` | Primary sources and scoped evaluations retrieved 2026-10-28: < | footnote oct-diff-evaluations, L294 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S52` | Wan official README, release history, architecture, inference… | footnote oct-vg-W22, L296 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S53` | Wan2.2 official TI2V-5B configuration | footnote oct-vg-W5, L298 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S54` | Wan2.2 official TI2V-5B configuration | footnote oct-vg-W5, L298 | moving | **PINNED** | `b8fff7315c76…` | 200 | pinned URL 200; no archived copy to compare |
| `A-S55` | Wan2.2 official TI2V-5B configuration | footnote oct-vg-W5, L298 | moving | **PINNED** | `b8fff7315c76…` | 200 | pinned URL 200; no archived copy to compare |
| `A-S56` | HunyuanVideo-1.5 Technical Report, arXiv:2511.18870, especial… | footnote oct-vg-H15, L300 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S57` | HunyuanVideo-1.5 Technical Report, arXiv:2511.18870, especial… | footnote oct-vg-H15, L300 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S58` | LTX-2: Efficient Joint Audio-Visual Foundation Model, arXiv:2… | footnote oct-vg-LTX, L302 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S59` | Official release notes | footnote oct-vg-LTX25, L304 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S60` | Official release notes | footnote oct-vg-LTX25, L304 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S61` | Official release notes | footnote oct-vg-LTX25, L304 | release-tag | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S62` | Alibaba Cloud Model Studio, current video overview and Wan3 A… | footnote oct-vg-WANAPI, L306 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S63` | Alibaba Cloud Model Studio, current video overview and Wan3 A… | footnote oct-vg-WANAPI, L306 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S64` | VACE: All-in-One Video Creation and Editing, arXiv:2503.07598… | footnote oct-vg-VACE, L308 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S65` | VACE: All-in-One Video Creation and Editing, arXiv:2503.07598… | footnote oct-vg-VACE, L308 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S66` | Official Wan-S2V technical report, §3–4 | footnote oct-vg-S2V, L310 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S67` | Official Wan-S2V technical report, §3–4 | footnote oct-vg-S2V, L310 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S68` | Wan-Dancer official code | footnote oct-vg-DANCER, L312 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S69` | Wan-Dancer official code | footnote oct-vg-DANCER, L312 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S70` | Wan-Animate-2 report | footnote oct-vg-ANIMATE, L314 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S71` | Wan-Animate-2 report | footnote oct-vg-ANIMATE, L314 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S72` | Official release metadata | footnote oct-vg-ENGINES, L316 | release-tag | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S73` | Official release metadata | footnote oct-vg-ENGINES, L316 | release-tag | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S74` | Official release metadata | footnote oct-vg-ENGINES, L316 | release-tag | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S75` | Official release metadata | footnote oct-vg-ENGINES, L316 | release-tag | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S76` | Wan license | footnote oct-vg-LICENSES, L318 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S77` | Wan license | footnote oct-vg-LICENSES, L318 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S78` | Wan license | footnote oct-vg-LICENSES, L318 | moving | **PINNED** | `60783e704160…` | 200 | pinned URL 200; no archived copy to compare |
| `A-S79` | PyTorch v2.15.0 release metadata, published 2026-10-28T17:09:… | footnote oct-ix-torch215, L320 | release-tag | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S80` | First-party source retrieved 2026-10-28: < | footnote oct-ix-7, L322 | page-no-ref | **PAGE** | page URL, no ref | 403 | 403 to audit UA (Intel bot policy); not a dead-link claim |
| `A-S81` | First-party source retrieved 2026-10-28: < | footnote oct-ix-8, L324 | page-no-ref | **PAGE** | page URL, no ref | 403 | 403 to audit UA (Intel bot policy); not a dead-link claim |
| `A-S82` | First-party source retrieved 2026-10-28: < | footnote oct-ix-13, L326 | page-no-ref | **PAGE** | page URL, no ref | 403 | 403 to audit UA (Intel bot policy); not a dead-link claim |
| `A-S83` | First-party source retrieved 2026-10-28: < | footnote oct-ix-21, L328 | release-tag | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S84` | First-party source retrieved 2026-10-28: < | footnote oct-ix-22, L330 | release-tag | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S85` | First-party source retrieved 2026-10-28: < | footnote oct-ix-26, L332 | release-tag | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S86` | First-party source retrieved 2026-10-28: < | footnote oct-ix-28, L334 | page-no-ref | **PAGE** | page URL, no ref | 403 | 403 to audit UA (Intel bot policy); not a dead-link claim |
| `A-S87` | First-party source retrieved 2026-10-28: < | footnote oct-ix-42, L336 | release-tag | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S88` | First-party source retrieved 2026-10-28: < | footnote oct-ix-47, L338 | moving | **UNVERIFIED** | kept as cited (§3) | 200 | no archived copy |
| `A-S89` | First-party source retrieved 2026-10-28: < | footnote oct-ix-49, L340 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S90` | First-party source retrieved 2026-10-28: < | footnote oct-ix-53, L342 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S91` | First-party source retrieved 2026-10-28: < | footnote oct-ix-54, L344 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S92` | First-party source retrieved 2026-10-28: < | footnote oct-ix-55, L346 | moving | **UNVERIFIED** | kept as cited (§3) | 200 | no archived copy |
| `A-S93` | First-party source retrieved 2026-10-28: < | footnote oct-ix-56, L348 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S94` | Independent benchmark account [2°], retrieved 2026-10-28: < | footnote oct-ix-60, L350 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S95` | Independent deployment account [2°], retrieved 2026-10-28: < | footnote oct-ix-61, L352 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S96` | First-party source retrieved 2026-10-28: < | footnote oct-ix-66, L354 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S97` | First-party source retrieved 2026-10-28: < | footnote oct-ix-67, L356 | commit-pinned | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S98` | First-party source retrieved 2026-10-28: < | footnote oct-ix-71, L358 | release-tag | **IMMUTABLE** | already immutable as cited | 200 | no archived copy |
| `A-S99` | - DeepSeek-V4: technical report arXiv:2606.19348; model card | body, L362 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S100` | 8; model card https://huggingface.co/deepseek-ai/DeepSeek-V4-… | body, L362 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S101` | - Kimi K3: technical report arXiv:2607.24653; model card | body, L363 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S102` | Xiv:2607.24653; model card https://huggingface.co/moonshotai/… | body, L363 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S103` | - Qwen3.8-Flash-Next: technical report | body, L364 | moving | **PINNED** | `69885871a643…` | 200 | pinned URL 200; no archived copy to compare |
| `A-S104` | b.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf; mo… | body, L364 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |
| `A-S105` | ific architecture and normalized attention/KV comparison); mo… | body, L365 | page-no-ref | **PAGE** | page URL, no ref | 200 | no archived copy |

**Totals:** 105 checked · 22 PINNED · 34 already immutable as cited · 47 page URLs (no ref; content may change — logged with retrieval date) · 2 UNVERIFIED. HTTP: 101× 200, 4× 403 (Intel bot policy, page URLs only).
## 5. RED → GREEN proof (isolated source / pandoc only)

Checker: `r10_check.py <chapter> <this ledger>` — 11 checks (ledger exists, unregistered moving refs, footnote wrap budget, ledger-ID resolution, addendum explicitness, provenance/date preservation, footnote ref/def resolution, research-label leak, `[2°]` account marking, supplement headings, Fig A.2 caption length).

**RED — pre-edit source, no ledger:**

```
verdict: RED  6/11
FAIL  ledger_exists
FAIL  no_unregistered_moving_refs
FAIL  footnote_urls_within_wrap_budget
PASS  chapter_ledger_ids_resolve
FAIL  oct28_addendum_sourcing_explicit
PASS  provenance_and_dates_preserved
PASS  footnotes_resolve
PASS  research_internal_labels_absent
PASS  independent_account_not_firstparty
PASS  six_supplement_headings_present
FAIL  fig_a2_caption_not_mini_essay
```

The five failures are exactly FTF-R10: no ledger, 24 unregistered moving refs, 63 footnote URLs over the 60-char wrap budget, addendum sourcing not explicit, Fig A.2 caption 613 chars (mini-essay).

**GREEN — post-edit source + this ledger:** ```
verdict: GREEN  11/11   (exit code 0)
PASS  ledger_exists
PASS  no_unregistered_moving_refs
PASS  footnote_urls_within_wrap_budget
PASS  chapter_ledger_ids_resolve
PASS  oct28_addendum_sourcing_explicit
PASS  provenance_and_dates_preserved
PASS  footnotes_resolve
PASS  research_internal_labels_absent
PASS  independent_account_not_firstparty
PASS  six_supplement_headings_present
PASS  fig_a2_caption_not_mini_essay
```

Run 2026-10-30 against the post-edit source and this ledger: **11/11 PASS**. The RED run above and this GREEN run use the identical checker and the identical 11 checks.

**Isolated pandoc proof** (`pandoc 3.7.0.2 -f markdown -t latex --wrap=none`, whole Appendix A file, no book build):

| Metric | Pre-edit | Post-edit |
|---|---|---|
| pandoc exit code | 0 | 0 |
| pandoc stderr | (empty) | (empty) |
| `\footnote{}` emitted | 50 | 50 |
| URLs **printed** in the output (`\url{}`) | 45 | 2 |
| printed URL characters | 4,029 | 173 |
| printed URLs > 60 chars | 37 | 2 |
| longest printed URL | 148 chars | 99 chars |
| LaTeX bytes | 77,547 | 71,722 |

Print-footnote machine-URL load drops **4,029 → 173 characters (45 → 2 printed URLs)**; the two that remain are the UNVERIFIED Habana `latest` URLs kept on purpose (§3). Footnote count is unchanged (50 → 50), so no citation was dropped.

## 6. October 28 addendum sourcing — explicit (verified)

Verified that the 2026-10-28 material is presented as a **separately dated post-snapshot addendum**, never as a refresh of the 2026-08-30 four-family comparison table or its First-hand Sources list. Post-edit line numbers:

| Statement | Line |
|---|---|
| ## Post-snapshot technology notes — 2026-10-28 | 151 |
| outside the four-family comparison and its 2026-08-30 First-hand Sources list | 153 |
| Sources inspected 28 October 2026 | 153 |
| not a refresh of the August comparison tables | 153 |
| A retrieval date is not a release date | 157 |
| These observations concern pinned October implementations, not support at the August cutoff | 212 |
| outside Appendix A's frozen 2026-08-30 comparison | 226 |
| This note extends the book's 30 August 2026 evidence cutoff explicitly | 236 |
| observed 2026-10-28 UTC; outside the 2026-08-30 evidence snapshot | 262 |
| 2026-10-28 technology notes are outside this compile envelope | 5 |

The exact reader-facing sentence **“Sources inspected 28 October 2026 … not a refresh of the August comparison tables”** (already used in Ch19) was **missing from Appendix A** and is now added at L153, together with the pointer to this ledger. The August boundary statements (L5, L153, L157, L212, L226, L236, L262) were already present and are unchanged.

## 7. Caption review — 3-part convention (takeaway · scope · reference)

Convention: *brief takeaway, enough scope/evidence to interpret the image, correct reference; no five-paragraph derivation under the graphic* (MASTER_INSTRUCTIONS, caption section). All five Appendix A figure captions and all three tables were reviewed:

| Caption | Pre-edit chars | Post-edit chars | Disposition |
|---|---|---|---|
| Fig A.1 | 164 | 164 | already 3-part (takeaway + definition scope + `[1P]`) — unchanged |
| Fig A.2 | 613 | 373 | **mini-essay trimmed**: takeaway + scope + reference kept; the crammed denominator/metric-scope derivation removed — the adjacent post-figure note already carries it |
| Fig A.3 | 433 | 433 | already 3-part (takeaway + layering/chronology scope + `[ILLUSTRATIVE]`) — unchanged |
| Fig A.4 | 427 | 427 | already 3-part (takeaway + design-choice scope + `[ILLUSTRATIVE]`) — unchanged |
| Fig A.5 | 352 | 352 | already 3-part (takeaway + illustrative-exit scope + reference) — unchanged |

Tables: the three Appendix A tables (mechanism classification, capability levers, video paths) carry **no captions** — header rows only — so there is no table caption to trim.

## 8. Provenance and retrieval dates preserved

| Marker / date | Pre-edit | Post-edit |
|---|---|---|
| `[1P]` | 36 | 36 |
| `[2°]` | 4 | 4 |
| `2026-10-28` | 34 | 34 |
| `retrieved 2026-10-28` | 23 | 23 |
| `Sources inspected 28 October 2026` | 0 | 1 |

All `[1P]`/`[2°]` markers and every `2026-10-28` retrieval date are intact; the only delta is the **added** `Sources inspected 28 October 2026` sentence (§6). Footnote IDs, footnote refs/defs (44/44), the six supplement headings, the `{.unnumbered}` classes, all five figure alt-texts and the A.10 ten-section structure are unchanged.

## 9. Exact diff

Diff of the single owned manuscript file (pre-edit → post-edit), 4 hunks:

```
@@ -68,7 +68,7 @@
@@ -80,7 +80,7 @@
@@ -150,7 +150,7 @@
@@ -269,99 +269,99 @@
```

Full unified diff:

```diff
--- a/design/manuscript/chapter-27/chapter-27.md
+++ b/design/manuscript/chapter-27/chapter-27.md
@@ -68,7 +68,7 @@
 
 **Decisive fact [1P] — HF Qwen/Qwen3.8-Flash-Next; GitHub QwenLM/Qwen3.8-Flash-Next:** 125 B total / 6 B activated, plus a separate 51 B of **N-gram embedding** parameters (offloadable to host memory). Native 262 K context (YaRN to 1M). **Hybrid attention: Gated DeltaNet (GDN) + Qwen Sparse Attention (QSA)**, where QSA operates at the *micro-block* level; **Gated Residual** widens the residual stream; 512 MoE experts (10 routed + 1 shared per token); Muon + AdamW. Reported training cost ~1/9 of Qwen3.7-Plus.
 
-**What this means for the architect (ties to Ch3, Ch5 Model Selection, Ch16 TCO).** Qwen's [technical report, 26 August 2026](https://raw.githubusercontent.com/QwenLM/Qwen3.8-Flash-Next/main/tech_report.pdf), describes the n-gram tables as held off the accelerator and prefetched from host memory. This is a vendor-reported mechanism, not only an architectural inference. Its effect on a particular deployment still depends on placement, bandwidth, overlap and engine support; the report does not establish a general serving-performance result for every backend. The 125B backbone, separate 51B n-gram tables and separately listed MTP module remain distinct parts of the residency inventory. Model selection therefore weighs heterogeneous memory and the supported transfer path alongside total and active parameters. [1P][FACT] mechanism; deployment consequence [DERIVED].
+**What this means for the architect (ties to Ch3, Ch5 Model Selection, Ch16 TCO).** Qwen's [technical report, 26 August 2026](https://raw.githubusercontent.com/QwenLM/Qwen3.8-Flash-Next/69885871a64393807d988b27b1b5e380e8f28526/tech_report.pdf), describes the n-gram tables as held off the accelerator and prefetched from host memory. This is a vendor-reported mechanism, not only an architectural inference. Its effect on a particular deployment still depends on placement, bandwidth, overlap and engine support; the report does not establish a general serving-performance result for every backend. The 125B backbone, separate 51B n-gram tables and separately listed MTP module remain distinct parts of the residency inventory. Model selection therefore weighs heterogeneous memory and the supported transfer path alongside total and active parameters. [1P][FACT] mechanism; deployment consequence [DERIVED].
 
 ## 4. GLM-5.3-Flash — Vendor-Reported First Natively Multimodal GLM, Efficiency-Branded
 
@@ -80,7 +80,7 @@
 
 ## 5. What This Means for the Handbook's Canonical Arithmetic
 
-![Fig A.2 — Vendor-reported percentages remaining relative to each model's own reference. The DeepSeek V4 rows use V3.2; the GLM-5.3-Flash row uses GLM-5.3. GLM's KV ratio is average BF16 cache per layer; its compute ratio is attention compute per head per layer, not total inference FLOPs. These rows have different denominators and metric scopes; they do not rank total memory, throughput, or cost across models. No predecessor-relative row is shown for Kimi K3 or Qwen3.8-Flash-Next. [1P][DERIVED] Sources: DeepSeek V4 arXiv:2606.19348; Z.ai GLM-5.3-Flash release article, 2026-08-26.](figures/fig-27-2704.png)
+![Fig A.2 — Vendor-reported percentages remaining relative to each model's own reference, not a shared baseline. GLM's rows are per-layer/per-head scope, not total FLOPs or total cache; no predecessor row exists for Kimi K3 or Qwen3.8-Flash-Next. [1P][DERIVED] Sources: DeepSeek V4 arXiv:2606.19348; Z.ai GLM-5.3-Flash release article, 2026-08-26.](figures/fig-27-2704.png)
 
 *Same message as Fig 7.1's GQA line, taken to the frontier: the per-token KV and FLOP "constants" of Chapter 7/8 are not universal — they are the canonical full-MHA conservative upper-bound teaching model, which hybrid attention re-architects down at the mechanism. Each row is a model's vendor-reported ratio of its own stated reference (e.g. DeepSeek V4 vs V3.2); they do not share a common denominator, so they must not be read as percentages of a single baseline. The canonical 70B dense full-MHA model is the book's teaching floor, not the denominator for these percentages. An architect who re-derives them per candidate model avoids both over- (sizing a 7% KV model as if it were 100%) and under-provisioning. Values are vendor-published [1P], not yet independently reprofiled on a serving stack (see A.7).*
 
@@ -150,7 +150,7 @@
 
 ## Post-snapshot technology notes — 2026-10-28 {.unnumbered}
 
-The following notes are outside the four-family comparison and its 2026-08-30 First-hand Sources list. They retain separate retrieval, release and implementation dates. They do not refresh the earlier comparison or establish locally measured performance.
+The following notes are outside the four-family comparison and its 2026-08-30 First-hand Sources list. They retain separate retrieval, release and implementation dates. They do not refresh the earlier comparison or establish locally measured performance. Sources inspected 28 October 2026 as part of this separately dated addendum, not a refresh of the August comparison tables. The long machine URLs behind the numbered source entries cited in these notes ([A-S01]–[A-S105]) are held in the release source ledger `source-verification.md`, pinned to immutable commit revisions where retrievable.
 
 ### Architecture dimensions and executed depth — 2026-10-28 {.unnumbered}
 
@@ -269,99 +269,99 @@
 >
 > Hypothesis. Intel configurations may offer a useful capacity, energy or cost trade-off for particular workloads. This requires independent measurements at the same quality and SLO. Current upstream support, vendor availability announcements and a local deployment account do not establish a market-share trend or a universal winner. [^oct-ix-56]^,^[^oct-ix-60]^,^[^oct-ix-61]
 
-[^oct-mt-q27]: Qwen, Qwen3.8-27B model card, “Model Overview,” “Benchmark Results,” and long-context guidance: https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/README.md . Released configuration: https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/config.json . Public implementation: https://raw.githubusercontent.com/huggingface/transformers/main/src/transformers/models/qwen3_5/modeling_qwen3_5.py .
-
-[^oct-mt-huginn]: Geiping et al., “Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach,” arXiv:2502.05171, v2, 17 February 2025: https://arxiv.org/abs/2502.05171 . Huginn checkpoint card, “KV-cache Details” and “Per-Token Adaptive Compute”: https://huggingface.co/tomg-group-umd/huginn-0125/raw/main/README.md .
+[^oct-mt-q27]: Qwen, Qwen3.8-27B model card, “Model Overview,” “Benchmark Results,” and long-context guidance: [A-S13]. Released configuration: [A-S14]. Public implementation: [A-S15].
+
+[^oct-mt-huginn]: Geiping et al., “Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach,” arXiv:2502.05171, v2, 17 February 2025: https://arxiv.org/abs/2502.05171. Huginn checkpoint card, “KV-cache Details” and “Per-Token Adaptive Compute”: [A-S17].
 
 [^oct-mt-ouro]: Zhu et al., “Scaling Latent Reasoning via Looped Language Models,” arXiv:2510.25741v6, revised 11 October 2026, especially §5.4.2 and Table 14: https://arxiv.org/pdf/2510.25741v6 . Revision history: https://arxiv.org/abs/2510.25741 .
 
-[^oct-mt-ouro-code]: ByteDance/Ouro-2.6B, released `modeling_ouro.py`, `OuroModel.forward` and exit-logit selection in `OuroForCausalLM.forward`, fetched revision archived in source-index.json: https://huggingface.co/ByteDance/Ouro-2.6B/raw/main/modeling_ouro.py . This is a static code observation, not an executed performance measurement.
-
-[^oct-mt-ouro-card]: ByteDance/Ouro-2.6B model card, adaptive-exit and vLLM notes: https://huggingface.co/ByteDance/Ouro-2.6B/raw/main/README.md . Card/config layer-count differences remain unresolved: https://huggingface.co/ByteDance/Ouro-2.6B/raw/main/config.json .
-
-[^oct-mt-ds41]: DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression,” Abstract and §§2.1–2.4, 3.2: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/main/DeepSeek_V41_Tech_Report.pdf . Model card: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/raw/main/README.md . The numerical memory and activation claims are vendor-reported, not independently reproduced.
-
-[^oct-mt-ornith]: Ornith Team, “Ornith-1.5: From Self-Scaffolding to Self-Improvement,” August 2026: https://ornith.ai/ornith_1_5.html . Variant card: https://huggingface.co/ornith-ai/Ornith-1.5-397B/raw/main/README.md .
-
-[^oct-mt-glm]: Z.ai official GLM repository, “GLM-5.3 & GLM-5.3-Flash”: https://raw.githubusercontent.com/zai-org/GLM-5/main/README.md . Exact Flash card: https://huggingface.co/zai-org/GLM-5.3-Flash/raw/main/README.md .
-
-[^oct-mt-gemini]: Google DeepMind, Gemini 3.8 Flash model card, published 2 September 2026: https://deepmind.google/models/model-cards/gemini-3-8-flash/ . Exact-model API documentation, updated 22 October 2026: https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash .
-
-[^oct-diff-releases]: Primary sources and scoped evaluations retrieved 2026-10-28: <https://huggingface.co/inclusionAI/LLaDA2.2-flash/raw/9b78da3f9149f1e239fb6d15f20a326fde574b9f/README.md>; <https://huggingface.co/inclusionAI/LLaDA2.2-flash/raw/9b78da3f9149f1e239fb6d15f20a326fde574b9f/config.json>; <https://blog.google/innovation-and-ai/technology/developers-tools/diffusion-gemma-faster-text-generation/>; <https://huggingface.co/google/diffusiongemma-26B-A4B-it/raw/f7f5b7f5fa82ffc52addd066915886d497f5517b/README.md>; <https://raw.githubusercontent.com/sgl-project/sglang/a1966e1b5d8b750b494d7e53cca1d2464f960038/docs/cookbook/autoregressive/Google/DiffusionGemma.mdx>; <https://huggingface.co/google/diffusiongemma-26B-A4B-it/raw/f7f5b7f5fa82ffc52addd066915886d497f5517b/config.json>; <https://huggingface.co/google/diffusiongemma-26B-A4B-it/raw/main/generation_config.json>; <https://docs.inceptionlabs.ai/get-started/models>; <https://www.inceptionlabs.ai/blog/introducing-mercury-3>; <https://docs.inceptionlabs.ai/capabilities/streaming>; <https://docs.inceptionlabs.ai/capabilities/structured-outputs>; <https://deepmind.google/models/gemini-diffusion/>; <https://raw.githubusercontent.com/ML-GSAI/LLaDA/main/README.md>; <https://raw.githubusercontent.com/DreamLM/Dream/main/README.md>. Source-reported findings; not locally reproduced.
-
-[^oct-diff-engine]: Primary sources and scoped evaluations retrieved 2026-10-28: <https://raw.githubusercontent.com/sgl-project/sglang/a1966e1b5d8b750b494d7e53cca1d2464f960038/docs/cookbook/autoregressive/Google/DiffusionGemma.mdx>; <https://raw.githubusercontent.com/sgl-project/sglang/a1966e1b5d8b750b494d7e53cca1d2464f960038/python/sglang/srt/dllm/algorithm/gemma4_renoise.py>. Source-reported findings; not locally reproduced.
-
-[^oct-diff-evaluations]: Primary sources and scoped evaluations retrieved 2026-10-28: <https://arxiv.org/html/2502.09992>; <https://huggingface.co/google/diffusiongemma-26B-A4B-it/raw/f7f5b7f5fa82ffc52addd066915886d497f5517b/README.md>; <https://blog.google/innovation-and-ai/technology/developers-tools/diffusion-gemma-faster-text-generation/>; <https://www.inceptionlabs.ai/blog/introducing-mercury-3>; <https://raw.githubusercontent.com/inclusionAI/LLaDA2.X/main/LLaDA2_2_tech_report.pdf>; <https://raw.githubusercontent.com/VILA-Lab/Flash-dLLM/main/README.md>; <https://raw.githubusercontent.com/VILA-Lab/Flash-dLLM/a667345f5746bb74f060c87bae5997fc3de9710c/llada/eval_llada.py>; <https://arxiv.org/html/2601.12979>; <https://arxiv.org/html/2601.15165>. Source-reported findings; not locally reproduced.
-
-[^oct-vg-W22]: Wan official README, release history, architecture, inference, licenses. https://github.com/Wan-Video/Wan2.2/tree/1ea34ff48f87168174e12956e200b1d908b1c5ff . Wan2.2's report link resolves to the older Wan report; it is not treated as a Wan2.2-specific paper.
-
-[^oct-vg-W5]: Wan2.2 official TI2V-5B configuration. https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/wan/configs/wan_ti2v_5B.py . Cross-check: https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers/blob/main/transformer/config.json and https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers/blob/main/vae/config.json .
+[^oct-mt-ouro-code]: ByteDance/Ouro-2.6B, released `modeling_ouro.py`, `OuroModel.forward` and exit-logit selection in `OuroForCausalLM.forward`, fetched revision archived in source-index.json: [A-S20]. This is a static code observation, not an executed performance measurement.
+
+[^oct-mt-ouro-card]: ByteDance/Ouro-2.6B model card, adaptive-exit and vLLM notes: [A-S21]. Card/config layer-count differences remain unresolved: [A-S22].
+
+[^oct-mt-ds41]: DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression,” Abstract and §§2.1–2.4, 3.2: [A-S23]. Model card: [A-S24]. The numerical memory and activation claims are vendor-reported, not independently reproduced.
+
+[^oct-mt-ornith]: Ornith Team, “Ornith-1.5: From Self-Scaffolding to Self-Improvement,” August 2026: https://ornith.ai/ornith_1_5.html. Variant card: [A-S26].
+
+[^oct-mt-glm]: Z.ai official GLM repository, “GLM-5.3 & GLM-5.3-Flash”: [A-S27]. Exact Flash card: [A-S28].
+
+[^oct-mt-gemini]: Google DeepMind, Gemini 3.8 Flash model card, published 2 September 2026: https://deepmind.google/models/model-cards/gemini-3-8-flash/. Exact-model API documentation, updated 22 October 2026: [A-S30].
+
+[^oct-diff-releases]: Primary sources and scoped evaluations retrieved 2026-10-28: [A-S31], [A-S32], [A-S33], [A-S34], [A-S35], [A-S36], [A-S37], [A-S38], [A-S39], [A-S40], [A-S41], [A-S42], [A-S43], [A-S44]. Source-reported findings; not locally reproduced.
+
+[^oct-diff-engine]: Primary sources and scoped evaluations retrieved 2026-10-28: [A-S35], [A-S45]. Source-reported findings; not locally reproduced.
+
+[^oct-diff-evaluations]: Primary sources and scoped evaluations retrieved 2026-10-28: [A-S46], [A-S34], [A-S33], [A-S39], [A-S47], [A-S48], [A-S49], [A-S50], [A-S51]. Source-reported findings; not locally reproduced.
+
+[^oct-vg-W22]: Wan official README, release history, architecture, inference, licenses. [A-S52]. Wan2.2's report link resolves to the older Wan report; it is not treated as a Wan2.2-specific paper.
+
+[^oct-vg-W5]: Wan2.2 official TI2V-5B configuration. [A-S53]. Cross-check: [A-S54] and [A-S55].
 
 [^oct-vg-H15]: HunyuanVideo-1.5 Technical Report, arXiv:2511.18870, especially model architecture and §6 Tables 7–8. https://arxiv.org/html/2511.18870 . Official repository: https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5 . Timing results are vendor-reported, not measurements made for this book.
 
 [^oct-vg-LTX]: LTX-2: Efficient Joint Audio-Visual Foundation Model, arXiv:2601.03233, architecture, §6.3/Table 1, limitations and conclusion. https://arxiv.org/html/2601.03233 .
 
-[^oct-vg-LTX25]: Official release notes: https://ltx.io/release-notes ; official model page: https://ltx.io/model/ltx-2-5 ; versioned Diffusers documentation: https://github.com/huggingface/diffusers/blob/v0.42.0/docs/source/en/api/pipelines/ltx2.md . Gated raw configurations remain unverified.
-
-[^oct-vg-WANAPI]: Alibaba Cloud Model Studio, current video overview and Wan3 API reference. https://www.alibabacloud.com/help/en/model-studio/video-editing-and-generation and https://www.alibabacloud.com/help/en/model-studio/wan3-video-generation-api-reference . Retrieved 2026-10-28; preview status is material.
+[^oct-vg-LTX25]: Official release notes: [A-S59]; official model page: [A-S60]; versioned Diffusers documentation: [A-S61]. Gated raw configurations remain unverified.
+
+[^oct-vg-WANAPI]: Alibaba Cloud Model Studio, current video overview and Wan3 API reference. [A-S62] and [A-S63]. Retrieved 2026-10-28; preview status is material.
 
 [^oct-vg-VACE]: VACE: All-in-One Video Creation and Editing, arXiv:2503.07598, §3.3; official code https://github.com/ali-vilab/VACE . https://arxiv.org/html/2503.07598 .
 
-[^oct-vg-S2V]: Official Wan-S2V technical report, §3–4. https://humanaigc.github.io/wan-s2v-webpage/content/wan-s2v.pdf ; official card https://huggingface.co/Wan-AI/Wan2.2-S2V-14B .
+[^oct-vg-S2V]: Official Wan-S2V technical report, §3–4. [A-S66]; official card https://huggingface.co/Wan-AI/Wan2.2-S2V-14B.
 
 [^oct-vg-DANCER]: Wan-Dancer official code https://github.com/Wan-Video/Wan-Dancer ; report https://arxiv.org/html/2607.09581 .
 
 [^oct-vg-ANIMATE]: Wan-Animate-2 report https://arxiv.org/html/2608.06009 and official repository https://github.com/Wan-Video/Wan-Animate-2 . The report was first submitted on 6 August 2026 and revised on 8 August 2026. Its Lite three-step distillation and the README's ten-step example are different recipes.
 
-[^oct-vg-ENGINES]: Official release metadata: https://api.github.com/repos/huggingface/diffusers/releases/tags/v0.35.0 ; https://api.github.com/repos/huggingface/diffusers/releases/tags/v0.37.0 ; https://api.github.com/repos/huggingface/diffusers/releases/tags/v0.40.0 ; https://api.github.com/repos/huggingface/diffusers/releases/tags/v0.42.0 .
-
-[^oct-vg-LICENSES]: Wan license https://github.com/Wan-Video/Wan2.2/blob/1ea34ff48f87168174e12956e200b1d908b1c5ff/LICENSE.txt ; LTX-2.x license https://github.com/Lightricks/LTX-2/blob/e98f6d927d83c92ef2be6aec76c8440b19306e39/LICENSE-2_x ; Hunyuan license https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5/blob/main/LICENSE . License observations are not legal advice.
-
-[^oct-ix-torch215]: PyTorch v2.15.0 release metadata, published 2026-10-28T17:09:49Z and retrieved 2026-10-28T21:35:32Z: <https://api.github.com/repos/pytorch/pytorch/releases/tags/v2.15.0>. Release publication is not validation of the vLLM XPU environment.
-
-[^oct-ix-7]: First-party source retrieved 2026-10-28: <https://intel.com/content/dam/www/central-libraries/us/en/documents/2026-03/datasheet-b70-gpu.pdf>. Release identities and source observations are not a validated combined environment or independent performance measurements.
-
-[^oct-ix-8]: First-party source retrieved 2026-10-28: <https://intel.com/content/dam/www/central-libraries/us/en/documents/2026-03/datasheet-b65-gpu.pdf>. Release identities and source observations are not a validated combined environment or independent performance measurements.
-
-[^oct-ix-13]: First-party source retrieved 2026-10-28: <https://intel.com/content/www/us/en/newsroom/news/client-computing/intel-core-ultra-series-3-with-vpro-powers-next-gen-pcs-on-18a.html>. Release identities and source observations are not a validated combined environment or independent performance measurements.
-
-[^oct-ix-21]: First-party source retrieved 2026-10-28: <https://api.github.com/repos/vllm-project/vllm/releases/tags/v0.32.0>. Release identities and source observations are not a validated combined environment or independent performance measurements.
-
-[^oct-ix-22]: First-party source retrieved 2026-10-28: <https://api.github.com/repos/pytorch/pytorch/releases/tags/v2.14.1>. Release identities and source observations are not a validated combined environment or independent performance measurements.
-
-[^oct-ix-26]: First-party source retrieved 2026-10-28: <https://api.github.com/repos/openvinotoolkit/openvino/releases/tags/2026.4.1>. Release identities and source observations are not a validated combined environment or independent performance measurements.
-
-[^oct-ix-28]: First-party source retrieved 2026-10-28: <https://www.intel.com/content/www/us/en/newsroom/news/artificial-intelligence/intel-accelerates-open-infrastructure-agentic-ai-era.html>. Release identities and source observations are not a validated combined environment or independent performance measurements.
-
-[^oct-ix-42]: First-party source retrieved 2026-10-28: <https://api.github.com/repos/sgl-project/sglang/releases/tags/v0.5.22>. Release identities and source observations are not a validated combined environment or independent performance measurements.
+[^oct-vg-ENGINES]: Official release metadata: [A-S72], [A-S73], [A-S74], [A-S75].
+
+[^oct-vg-LICENSES]: Wan license [A-S76]; LTX-2.x license [A-S77]; Hunyuan license [A-S78]. License observations are not legal advice.
+
+[^oct-ix-torch215]: PyTorch v2.15.0 release metadata, published 2026-10-28T17:09:49Z and retrieved 2026-10-28T21:35:32Z: [A-S79]. Release publication is not validation of the vLLM XPU environment.
+
+[^oct-ix-7]: First-party source retrieved 2026-10-28: [A-S80]. Release identities and source observations are not a validated combined environment or independent performance measurements.
+
+[^oct-ix-8]: First-party source retrieved 2026-10-28: [A-S81]. Release identities and source observations are not a validated combined environment or independent performance measurements.
+
+[^oct-ix-13]: First-party source retrieved 2026-10-28: [A-S82]. Release identities and source observations are not a validated combined environment or independent performance measurements.
+
+[^oct-ix-21]: First-party source retrieved 2026-10-28: [A-S83]. Release identities and source observations are not a validated combined environment or independent performance measurements.
+
+[^oct-ix-22]: First-party source retrieved 2026-10-28: [A-S84]. Release identities and source observations are not a validated combined environment or independent performance measurements.
+
+[^oct-ix-26]: First-party source retrieved 2026-10-28: [A-S85]. Release identities and source observations are not a validated combined environment or independent performance measurements.
+
+[^oct-ix-28]: First-party source retrieved 2026-10-28: [A-S86]. Release identities and source observations are not a validated combined environment or independent performance measurements.
+
+[^oct-ix-42]: First-party source retrieved 2026-10-28: [A-S87]. Release identities and source observations are not a validated combined environment or independent performance measurements.
 
 [^oct-ix-47]: First-party source retrieved 2026-10-28: <https://docs.habana.ai/en/latest/API_Reference_Guides/HCCL_APIs/index.html>. Release identities and source observations are not a validated combined environment or independent performance measurements.
 
-[^oct-ix-49]: First-party source retrieved 2026-10-28: <https://raw.githubusercontent.com/sgl-project/sglang/a1966e1b5d8b750b494d7e53cca1d2464f960038/docs/docs/hardware-platforms/xpu.mdx>. Release identities and source observations are not a validated combined environment or independent performance measurements.
-
-[^oct-ix-53]: First-party source retrieved 2026-10-28: <https://raw.githubusercontent.com/vllm-project/vllm/5df63a7203cdb9328d824a27b682e77c7b9928be/requirements/xpu.txt>. Release identities and source observations are not a validated combined environment or independent performance measurements.
-
-[^oct-ix-54]: First-party source retrieved 2026-10-28: <https://raw.githubusercontent.com/ggml-org/llama.cpp/8ca4060b7e30e76baaa5670ee1ec1b760b7f8552/docs/backend/SYCL.md>. Release identities and source observations are not a validated combined environment or independent performance measurements.
+[^oct-ix-49]: First-party source retrieved 2026-10-28: [A-S89]. Release identities and source observations are not a validated combined environment or independent performance measurements.
+
+[^oct-ix-53]: First-party source retrieved 2026-10-28: [A-S90]. Release identities and source observations are not a validated combined environment or independent performance measurements.
+
+[^oct-ix-54]: First-party source retrieved 2026-10-28: [A-S91]. Release identities and source observations are not a validated combined environment or independent performance measurements.
 
 [^oct-ix-55]: First-party source retrieved 2026-10-28: <https://docs.habana.ai/en/latest/PyTorch/PyTorch_Model_Porting/Porting_PyTorch_Models_to_Gaudi.html>. Release identities and source observations are not a validated combined environment or independent performance measurements.
 
-[^oct-ix-56]: First-party source retrieved 2026-10-28: <https://newsroom.ibm.com/blog-intel-and-ibm-announce-the-availability-of-intel-gaudi-3-ai-accelerators-on-ibm-cloud>. Release identities and source observations are not a validated combined environment or independent performance measurements.
-
-[^oct-ix-60]: Independent benchmark account [2°], retrieved 2026-10-28: <https://embeddedllm.com/blog/benchmarking-llm-inference-intel-arc-pro-b60>. This is a third-party benchmark account, not a vendor release identity; the book has not reproduced its measurements or established a validated combined environment.
-
-[^oct-ix-61]: Independent deployment account [2°], retrieved 2026-10-28: <https://bentech.substack.com/p/running-local-llms-on-intel-arc-pro>. Release identities and source observations are not a validated combined environment or independent performance measurements.
-
-[^oct-ix-66]: First-party source retrieved 2026-10-28: <https://raw.githubusercontent.com/pytorch/pytorch/5c4886908584029761b579af026dcfb627c84070/docs/source/notes/get_start_xpu.md>. Release identities and source observations are not a validated combined environment or independent performance measurements.
-
-[^oct-ix-67]: First-party source retrieved 2026-10-28: <https://raw.githubusercontent.com/vllm-project/vllm/5df63a7203cdb9328d824a27b682e77c7b9928be/docs/getting_started/installation/gpu.xpu.inc.md>. Release identities and source observations are not a validated combined environment or independent performance measurements.
-
-[^oct-ix-71]: First-party source retrieved 2026-10-28: <https://api.github.com/repos/openvinotoolkit/openvino.genai/releases/tags/2026.4.1.0>. Release identities and source observations are not a validated combined environment or independent performance measurements.
+[^oct-ix-56]: First-party source retrieved 2026-10-28: [A-S93]. Release identities and source observations are not a validated combined environment or independent performance measurements.
+
+[^oct-ix-60]: Independent benchmark account [2°], retrieved 2026-10-28: [A-S94]. This is a third-party benchmark account, not a vendor release identity; the book has not reproduced its measurements or established a validated combined environment.
+
+[^oct-ix-61]: Independent deployment account [2°], retrieved 2026-10-28: [A-S95]. Release identities and source observations are not a validated combined environment or independent performance measurements.
+
+[^oct-ix-66]: First-party source retrieved 2026-10-28: [A-S96]. Release identities and source observations are not a validated combined environment or independent performance measurements.
+
+[^oct-ix-67]: First-party source retrieved 2026-10-28: [A-S97]. Release identities and source observations are not a validated combined environment or independent performance measurements.
+
+[^oct-ix-71]: First-party source retrieved 2026-10-28: [A-S98]. Release identities and source observations are not a validated combined environment or independent performance measurements.
 
 ## 8. First-hand Sources (all [1P])
 
 - DeepSeek-V4: technical report arXiv:2606.19348; model card https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro; org https://github.com/deepseek-ai
 - Kimi K3: technical report arXiv:2607.24653; model card https://huggingface.co/moonshotai/Kimi-K3; https://github.com/moonshotai
-- Qwen3.8-Flash-Next: technical report https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf; model card https://huggingface.co/Qwen/Qwen3.8-Flash-Next
+- Qwen3.8-Flash-Next: technical report https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/69885871a64393807d988b27b1b5e380e8f28526/tech_report.pdf; model card https://huggingface.co/Qwen/Qwen3.8-Flash-Next
 - GLM-5.3-Flash: release article https://z.ai/blog/glm-5.3-flash (2026-08-26; Flash-specific architecture and normalized attention/KV comparison); model card https://huggingface.co/zai-org/GLM-5.3-Flash. The February GLM-5 parent report arXiv:2602.15763 is background for the earlier model, not evidence for the Flash ratios.
 
 *Compiled 2026-08-30 from the models' official technical reports and first-party model cards; all parameters/claims are vendor-reported [1P] and per this handbook's discipline carry a verify-on-own-hardware caveat.*
```

## 10. Boundaries and out-of-scope observations

- **Isolated proof only.** No full-book build, no `render/build.sh`, no git commit, no edits to frozen `work/accelerated_*` or `r27_*` artifacts, no changes to any chapter other than Appendix A (`chapter-27.md`).
- **Not fixed here (out of scope — other chapters still cite moving refs):**
  - `chapter-07/chapter-07.md`: 2 — `https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/config.json`; `https://huggingface.co/tomg-group-umd/huginn-0125/raw/main/README.md`
  - `chapter-08/chapter-08.md`: 6 — `https://docs.habana.ai/en/latest/API_Reference_Guides/HCCL_APIs/index.html`; `https://docs.habana.ai/en/latest/PyTorch/PyTorch_Model_Porting/Porting_PyTorch_Models_to_Gaudi.html`; `https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers/blob/main/transformer/config.json`; `https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/main/DeepSeek_V41_Tech_Report.pdf`; `https://huggingface.co/tomg-group-umd/huginn-0125/raw/main/README.md`; `https://raw.githubusercontent.com/inclusionAI/LLaDA2.X/main/LLaDA2_2_tech_report.pdf`
  - `chapter-09/chapter-09.md`: 2 — `https://docs.habana.ai/en/latest/API_Reference_Guides/HCCL_APIs/index.html`; `https://raw.githubusercontent.com/pytorch/gloo/main/README.md`
  - Appendix A itself retains only the 2 UNVERIFIED Habana URLs (§3).
- **Not re-verified here:** claim-level truth of any vendor statement. This ledger records URL identity, immutability and byte-level agreement with the 2026-10-28 archive — not independent reproduction of results.
- **Re-run:** `python3 r10_check.py design/manuscript/chapter-27/chapter-27.md review/publication_v2_20261028/audit/source-verification.md` must exit 0 (GREEN) on the integrated tree.

