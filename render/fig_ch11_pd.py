import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-11-1103: P/D Disaggregation Topology ----
# Left: prefill pool (compute bound, FLOPs). Right: decode pool (bandwidth bound, HBM).
# Bridge: KV cache transfer over NVLink/fabric. Canonical numbers from Ch11.
fig, ax = plt.subplots(figsize=(12.5, 6.2))
ax.set_xlim(0, 24); ax.set_ylim(0, 8); ax.axis('off')

# Title
ax.text(12, 7.6, 'P/D Disaggregation: the two pools want opposite resources', fontsize=13, fontweight='bold', ha='center', color='#1a1a1a')

# ---- Left pool: Prefill (compute-bound, orange) ----
ax.add_patch(FancyBboxPatch((0.5, 1.2), 6.6, 5.2, boxstyle='round,pad=0.02', fc='#fdecea', ec='#c0392b', lw=2))
ax.text(3.8, 6.0, 'PREFILL POOL', fontsize=11, fontweight='bold', ha='center', color='#c0392b')
ax.text(3.8, 5.6, 'Compute-bound (FLOPs)', fontsize=9, ha='center', color='#c0392b')
# GPUs in pool
for i, (gx, gy) in enumerate([(1.4, 4.3), (3.8, 4.3), (6.2, 4.3), (1.4, 2.2), (3.8, 2.2), (6.2, 2.2)]):
    ax.add_patch(FancyBboxPatch((gx-0.9, gy-0.6), 1.8, 1.2, boxstyle='round,pad=0.02', fc='#e67e22', ec='#a04000', lw=1))
    ax.text(gx, gy, 'GPU', ha='center', va='center', fontsize=7, color='white', fontweight='bold')
ax.text(3.8, 1.5, 'massive prompt processed at once\nhigh FLOP utilization', fontsize=7.5, ha='center', color='#c0392b')

# ---- Right pool: Decode (bandwidth-bound, blue) ----
ax.add_patch(FancyBboxPatch((16.9, 1.2), 6.6, 5.2, boxstyle='round,pad=0.02', fc='#eaf2f8', ec='#27408b', lw=2))
ax.text(20.2, 6.0, 'DECODE POOL', fontsize=11, fontweight='bold', ha='center', color='#27408b')
ax.text(20.2, 5.6, 'Bandwidth-bound (HBM)', fontsize=9, ha='center', color='#27408b')
for i, (gx, gy) in enumerate([(17.8, 4.3), (20.2, 4.3), (22.6, 4.3), (17.8, 2.2), (20.2, 2.2), (22.6, 2.2)]):
    ax.add_patch(FancyBboxPatch((gx-0.9, gy-0.6), 1.8, 1.2, boxstyle='round,pad=0.02', fc='#2980b9', ec='#154360', lw=1))
    ax.text(gx, gy, 'GPU', ha='center', va='center', fontsize=7, color='white', fontweight='bold')
ax.text(20.2, 1.5, 'steady token generation\nhigh bandwidth utilization', fontsize=7.5, ha='center', color='#27408b')

# ---- Bridge: KV cache transfer ----
ax.annotate('', xy=(16.9, 4.2), xytext=(7.2, 4.2), arrowprops=dict(arrowstyle='-|>', lw=3, color='#a93226', connectionstyle='arc3,rad=0.0'))
ax.text(12, 5.1, 'KV CACHE TRANSFER\nover NVLink / fabric', fontsize=10, ha='center', color='#a93226', fontweight='bold')
ax.text(12, 4.7, 'prefill writes per-token KV; decode reads it\n(shaded-dominant with Mooncake)', fontsize=8, ha='center', color='#555')

# ---- Incoming request / output outside pools ----
ax.text(3.8, 7.1, 'input prompt →', fontsize=9, ha='left', color='#333', fontweight='bold')
ax.annotate('', xy=(3.8, 6.5), xytext=(3.8, 7.05), arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#333'))
ax.text(20.2, 0.5, '← tokens out to client', fontsize=9, ha='center', color='#333', fontweight='bold')

# ---- Why: resource conflict ----
ax.text(12, -0.1, 'Why split?  prefill  ~1.19 PFLOPS required vs 0.989 peak (FLOP-starved);  decode  5.6 TB/s vs 3.35 TB/s (bandwidth-starved).  One pool forces a compromise for both.  [2° DERIVED]',
        fontsize=8, ha='center', color='#444')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-11/figures/fig-11-1103.png', dpi=150)
plt.close()
print('fig-11-1103 done')
