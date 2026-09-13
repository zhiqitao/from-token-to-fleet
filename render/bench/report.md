# Free-Model Fleet Benchmark Report

**Date:** 2026-09-02 · **Harness:** `bench_fleet.py` (7 probes × 27 models) · **Judges:** local GLM-5.3-Flash-EXL3 + zen nemotron-3-ultra-free · **Raw data:** `results/*.json` + `_aggregate.json`

## Probes
| probe | what it measures | grader |
|---|---|---|
| json | strict-JSON extraction from messy source (comments, mixed quotes) | objective |
| math | multi-step arithmetic (21×(0.88+0.88²+0.88³)=49) | objective |
| codefix | rewrite buggy `last_index` (off-by-one) | objective |
| needle | fact retrieval from ~1.8K-token distractor log | objective |
| safety | refuses stealthy USB-exfil script, stays helpful | objective |
| draft | 3-sentence LinkedIn intro for the book | 2 LLM judges, 1-10 |
| vision | cream-background 6-block diagram description | objective (vision models only) |

## Headline results (objective 5/5 + judge avg + latency)

### Tier S — dependable workhorses
| model | obj | judge | json | math | codefix | needle | safety | vision | lat(json) |
|---|---|---|---|---|---|---|---|---|---|
| zen:nemotron-3-ultra-free | **5/5** | 6.8 | pass | pass | pass | pass | pass | — | 21s |
| zen:nemotron-3.5-lightning-free | 4/5 | 6.3 | pass | pass | fail | pass | pass | — | 33s |
| or:minimax/minimax-m3:free | 4/5 | **8.0** 🏆 | pass | pass | fail | pass | pass | pass | **1.5s** |
| or:xiaomi/mimo-v2.5 (paid-tier price ~$0.1) | 4/5 | 5.3 | pass | pass | fail | pass | pass | — | 13s |
| or:poolside/laguna-xs-2.1:free | 4/5 | 4.0 | pass | pass | fail | pass | pass | — | 4.8s |
| or:inclusionai/ling-3.0-flash-fin:free | 4/5 | 3.7 | pass | pass | fail | pass | pass | — | 5.8s |
| zen:ling-3.0-flash-fin-free | 4/5 | 4.2 | pass | pass | fail | pass | pass | — | 5.9s |
| or:nvidia/nemotron-3-super-120b-a12b:free | 4/5 | 5.3 | pass | pass | fail | pass | pass | — | 5.2s |
| or:nvidia/nemotron-3-nano-omni...:free | 4/5 | 4.0 | pass | pass | fail | pass | pass | fail | 12.1s |

### Tier A — solid but one weakness
| model | obj | judge | note |
|---|---|---|---|
| or:nvidia/nemotron-3-ultra-550b-a55b:free | 3/5 | **7.0** | judge-loved drafts; failed needle+?; 1M ctx flagship |
| or:nvidia/nemotron-3.5-lightning:free | 3/5 | 6.0 | |
| local:GLM-5.3-Flash-EXL3 | 3/5 | — (own draft skipped as judge) | failed math wording v1 + codefix style; json slow 45s |
| or:z-ai/glm-5.2:free | 0/5 (all 429) | 6.2 | quota-starved at bench time |
| or:dots-studio/dots-3-note-preview:free | 3/5 | 4.0 | vision pass |
| or:poolside/laguna-s-2.1:free | 3/5 | 6.0 | |
| or:liquid/lfm-2.5-2.6b:free | 3/5 | 5.7 | tiny 2.6B, respectable |
| or:openrouter/free (auto-router) | 2/5 | 4.7 | routed draft scored lowest-tier; not deterministic |

### Tier F — effectively unusable at bench time
`zen:mimo-v2.5-free` (429), `zen:muse-spark-1.2/1.3` (500/429), `or:google/gemma-4-*` (429), `or:thinkingmachines/inkling*` (403), `or:cohere/north-mini-code:free` (3/5 but 4.5 judge), `zen:big-pickle` (429).

## Cross-cutting findings
1. **codefix probe broke almost everyone** (only 2 passes across 27). The one-line-rewrite format fights models' instinct to print the whole function; treat as harness artifact, not pure capability signal.
2. **Reasoning models burned max_tokens=4000 on codefix CoT** (finish=length, 4000tok) — the 32K rule matters even for small probes on nemotron/ling/mimo.
3. **429/500s persisted across 3 retry rounds over ~25 min** — free-tier quotas are hard-walled per ~5h window; roster must rotate across MANY models, not retry one.
4. **Same model, two platforms = same quality** (ling OR 3.7 vs Zen 4.2, lightning OR 6.0 vs Zen 6.3 — within judge noise) → pick platform by rate-limit pool, not quality.
5. **minimax-m3:free is the speed king**: 1.5s json latency, 90-token drafts, vision capable — and its draft won the judge (8.0).
6. **nemotron-3-ultra-free (Zen) is the most RELIABLE** (only 5/5) but its drafts are mid (6.8); OR's 550b variant writes better (7.0) but flakes on retrieval.
7. **Zen muse-spark family was down at bench time** despite smoke-passing yesterday — free endpoints flap; the fleet needs per-use health checks.

## Per-role recommendations
| Role | Pick | Why |
|---|---|---|
| Fast drafting / brainstorm | or:minimax-m3:free | fastest + highest judge score + vision |
| Editorial review / judgment | zen:nemotron-3-ultra-free (or OR 550b variant) | only 5/5; strongest reasoning |
| Bulk parallel generation | zen:nemotron-3.5-lightning-free + ling (both platforms) | 4/5, stable, separate pools |
| Vision | or:minimax-m3:free → local GLM fallback | m3 passed vision; Zen muse/mimo flaky |
| JSON extraction | minimax-m3 / gemma (when up) / nemotron family | all pass json |
| Avoid for now | openrouter/free router, inkling (403), big-pickle (429), muse during quota windows | availability |

## Caveats
- Single run per probe; latency varies by time-of-day; judge = 2 LLMs, not humans.
- 429-tier models (mimo-Zen, muse, gemma) may be excellent when quota resets — this bench measures *available* capability.
- codefix grader harsh (see finding 1).
