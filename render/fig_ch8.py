import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as _mpl
_mpl.rcParams['axes.formatter.use_mathtext']=False


# ---- fig-08-0801: PER-GPU roofline for dense FP16, H100 vs H200 ----
# Scope: this is a per-GPU roofline. Both the compute ceiling (989 TFLOPS) and the
# bandwidth (3.35 / 4.8 TB/s) are SINGLE-GPU quantities, so the ridge point
# (peak / bw, FLOP/byte) and the memory-bound slope are per-GPU.
# Note: the ridge CLASSIFICATION (compute vs memory bound) is unchanged by ideal
# N-way replication, because both peak FLOP/s and HBM bandwidth scale with GPU
# count. A host-level (8x) chart would multiply BOTH axes by ~8; attainable
# host-level performance additionally depends on sharding and communication.
def ridge(peak_tflops, bw_tb):
    return peak_tflops / bw_tb

peak = 989
bw100 = 3.35
bw200 = 4.8
r100 = ridge(peak, bw100)   # ~295
r200 = ridge(peak, bw200)   # ~206

ais = np.logspace(-1, 3, 400)

fig, ax = plt.subplots(figsize=(6.1, 4.4))
# H100 ridge (solid) and H200 ridge (dashed); compute plateau common to both
ach100 = np.minimum(peak, ais * bw100)
ach200 = np.minimum(peak, ais * bw200)
ax.loglog(ais, ach100, color='#27408b', lw=2.2, label='H100 FP16 (3.35 TB/s)')
ax.loglog(ais, ach200, color='#c0392b', lw=1.9, ls='--', label='H200 FP16 (4.8 TB/s)')
ax.axvline(r100, color='#27408b', ls=':', lw=1.2)
ax.axvline(r200, color='#c0392b', ls=':', lw=1.2)
ax.text(r100, 240, f'ridge ≈ {r100:.0f}', fontsize=8.5, color='#27408b', ha='center')
ax.text(r200*0.97, 6.5, f'ridge ≈ {r200:.0f}', fontsize=8.5, color='#c0392b', ha='center')
ax.text(r100*2.2, 480, 'compute-bound', fontsize=9, color='#6f9e5f', ha='center')
ax.text(0.11, 6.0, 'memory-bound', fontsize=9, color='#e67e22', ha='center')

# Operating points. Prefill intensity is set by sequence length (weights read once,
# reused across all tokens) -> to the RIGHT of the ridge, on the plateau (compute-bound).
# Decode re-reads weights each token -> low intensity, LEFT of the ridge, on the slope.
pts = [
    ('prefill 9.2K', 320, 989, 'prefill'),   # canonical
    ('decode batch=1', 0.5, 1.7, 'decode'),  # canonical
    ('decode batched', 8, 27, 'decode'),     # continuous batching raises intensity
]
colors = {'prefill': '#e67e22', 'decode': '#27408b'}
for name, a, t, tag in pts:
    ax.scatter([a], [min(t, peak)], color=colors[tag], zorder=5, s=45)

# label the markers, offset so they do not sit on the dots
ax.text(320, 989*0.60, 'prefill 9.2K', fontsize=9, color=colors['prefill'], ha='center')
ax.text(0.42, 1.65, 'decode\nbatch=1', fontsize=9, color=colors['decode'], ha='center')
ax.text(11, 30, 'decode batched', fontsize=9, color=colors['decode'], ha='left')

# continuous-batching arrow: decode batch=1 -> decode batched, up the slope
ax.annotate('', xy=(8, 27), xytext=(0.6, 1.8),
            arrowprops=dict(arrowstyle='->', lw=1.9, color=colors['decode'],
                            connectionstyle='arc3,rad=0.15'))

ax.set_xlabel('Arithmetic intensity (FLOP/byte) — per GPU', fontsize=9)
ax.set_ylabel('Achievable performance (TFLOPS) — per GPU', fontsize=9)
ax.set_title('Per-GPU roofline: dense FP16, one H100 vs one H200', fontsize=9.5)
ax.tick_params(labelsize=11)
ax.grid(alpha=0.3, which='both')
ax.legend(fontsize=8, loc='lower right')
plt.tight_layout()
plt.savefig('design/manuscript/chapter-08/figures/fig-08-0801.png', dpi=150)
plt.close()
print('wrote fig-08-0801 (per-GPU roofline)')
