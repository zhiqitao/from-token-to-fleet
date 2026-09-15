import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-11-1103: P/D Disaggregation Topology ----
# Left: prefill pool (compute bound, FLOPs). Right: decode pool (bandwidth bound, HBM).
# Bridge: KV cache transfer over NVLink/fabric. Compact narrow layout so it places
# at column width (fonts stay print size).
fig, ax = plt.subplots(figsize=(6.3, 5.6))
ax.set_xlim(0, 17); ax.set_ylim(0, 9); ax.axis('off')

# Title (wrapped so it doesn't widen the content)
ax.text(8.5, 8.4, 'P/D Disaggregation: the two pools\nwant opposite resources', fontsize=10, fontweight='bold', ha='center', color='#1a1a1a')

# ---- Left pool: Prefill (compute-bound, orange) ----
ax.add_patch(FancyBboxPatch((0.3, 1.4), 5.4, 6.2, boxstyle='round,pad=0.02', fc='#fdecea', ec='#c0392b', lw=2))
ax.text(3.0, 7.2, 'PREFILL POOL', fontsize=10, fontweight='bold', ha='center', color='#c0392b')
ax.text(3.0, 6.7, 'Compute-bound (FLOPs)', fontsize=8, ha='center', color='#c0392b')
# GPUs in pool (2x2 grid)
for i, (gx, gy) in enumerate([(1.4, 5.3), (4.6, 5.3), (1.4, 2.9), (4.0, 2.9)]):
    ax.add_patch(FancyBboxPatch((gx-0.85, gy-0.55), 1.7, 1.1, boxstyle='round,pad=0.02', fc='#e67e22', ec='#a04000', lw=1))
    ax.text(gx, gy, 'GPU', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
ax.text(3.0, 1.9, 'massive prompt at once\nhigh FLOP utilization', fontsize=7.5, ha='center', color='#c0392b')

# ---- Right pool: Decode (bandwidth-bound, blue) ----
ax.add_patch(FancyBboxPatch((11.3, 1.4), 5.4, 6.2, boxstyle='round,pad=0.02', fc='#eaf2f8', ec='#27408b', lw=2))
ax.text(14.0, 7.2, 'DECODE POOL', fontsize=10, fontweight='bold', ha='center', color='#27408b')
ax.text(14.0, 6.7, 'Bandwidth-bound (HBM)', fontsize=8, ha='center', color='#27408b')
for i, (gx, gy) in enumerate([(12.4, 5.3), (15.6, 5.3), (12.0, 2.9), (15.2, 2.9)]):
    ax.add_patch(FancyBboxPatch((gx-0.85, gy-0.55), 1.7, 1.1, boxstyle='round,pad=0.02', fc='#2980b9', ec='#154360', lw=1))
    ax.text(gx, gy, 'GPU', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
ax.text(14.0, 1.9, 'steady token generation\nhigh bandwidth utilization', fontsize=7.5, ha='center', color='#27408b')

# ---- Bridge: KV cache transfer ----
ax.annotate('', xy=(11.3, 4.5), xytext=(5.7, 4.5), arrowprops=dict(arrowstyle='-|>', lw=2.6, color='#a93226', connectionstyle='arc3,rad=0.0'))
ax.text(8.5, 5.5, 'KV CACHE\nTRANSFER (initial)', fontsize=9, ha='center', color='#a93226', fontweight='bold')
ax.text(8.5, 3.9, 'prefill writes the prompt KV, then\ndecode READS it AND keeps appending\nper generated token (ownership splits)',
        fontsize=7.5, ha='center', color='#555')

# ---- Incoming request / output outside pools (anchor endpoints) ----
ax.text(3.0, 8.0, 'input prompt →', fontsize=8, ha='left', color='#333', fontweight='bold')
ax.annotate('', xy=(3.0, 7.75), xytext=(3.0, 8.0), arrowprops=dict(arrowstyle='-|>', lw=1.5, color='#333'))
ax.text(14.0, 0.6, '← tokens out to client', fontsize=8, ha='center', color='#333', fontweight='bold')
ax.annotate('', xy=(14.0, 1.45), xytext=(14.0, 0.75), arrowprops=dict(arrowstyle='-|>', lw=1.5, color='#333'))

# ---- Why: resource conflict (wrapped so it doesn't clip at the column edge) ----
ax.text(8.5, -0.3, 'Why split?  prefill ~1.19 PFLOPS vs 0.989 peak (FLOP-starved);\ndecode 5.6 TB/s vs 3.35 TB/s (bandwidth-starved). One pool forces a compromise. [2° DERIVED]',
        fontsize=7.5, ha='center', color='#444')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-11/figures/fig-11-1103.png', dpi=150)
plt.close()
print('fig-11-1103 done')
