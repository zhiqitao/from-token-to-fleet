"""Reproducible capstone model for Ch. 26 (F02/F04 fix).

Two-point mixture model (fully specified, reproducible):
  - Semantic response cache hit fraction h = 0.35. A cache hit returns from the
    semantic cache at a fixed TTFT of 50 ms (retrieval + cache lookup, no LLM
    prefill). A cache miss is served by the engine at a fixed TTFT of 250 ms
    (the cached-scenario value after the 35% lower arrival rate settles the
    prefill queue; see Chapter 26 passage).
  - Baseline (uncached, unsharded): 100% of requests reach the engine at a
    fixed TTFT of 450 ms.

Because the hit TTFT (50 ms) is strictly below the miss TTFT (250 ms), the
95th/99th percentiles of the pooled mixture fall in the MISS population:
  P(TTF T <= 50)  = h          = 0.35
  P(TTFT <= 250)  = h + (1-h)  = 1.00
So the aggregate p99 = 250 ms (not a weighted average of the two values).
The weighted average 0.35*50 + 0.65*250 = 180 ms is the MEAN, not a quantile.

Run:  python3 render/capstone_calc.py
"""
import numpy as np

H = 0.35          # cache hit fraction
HIT_MS = 50.0     # cache-hit TTFT (point mass)
MISS_MS = 250.0   # engine-served TTFT (point mass, cached scenario)
BASE_MS = 450.0   # baseline (uncached/unsharded) TTFT
SHARD_COST_DISC = 0.20   # ~20% per-token cost reduction from 8-way decode sharing


def mixture_stats(h, hit_ms, miss_ms, n=200_000):
    """Return mean and p99 of the pooled two-point latency mixture."""
    rng = np.random.default_rng(20260913)
    n_hit = int(n * h)
    pooled = rng.permutation(np.concatenate(
        [np.full(n_hit, hit_ms), np.full(n - n_hit, miss_ms)]))
    return float(np.mean(pooled)), float(np.percentile(pooled, 99))


if __name__ == "__main__":
    mean, p99 = mixture_stats(H, HIT_MS, MISS_MS)
    print(f"pooled mean TTFT : {mean:.1f} ms")
    print(f"pooled p99 TTFT  : {p99:.1f} ms")
    print(f"TTFT improvement vs baseline ({BASE_MS} ms): "
          f"{(BASE_MS - p99) / BASE_MS * 100:.1f}%")
    cost = 100 * (H + (1 - H) * SHARD_COST_DISC)
    print(f"generation-cost reduction (0.35 + 0.65*0.20): {cost:.0f}%")
    # p99 check vs the chapter SLO
    print("p99 within 800 ms SLO:", p99 <= 800.0)
