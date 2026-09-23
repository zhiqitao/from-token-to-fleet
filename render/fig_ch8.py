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

ais = np.logspace(-1, 4.3, 400)

fig, ax = plt.subplots(figsize=(6.1, 4.4))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
# H100 ridge (solid) and H200 ridge (dashed); compute plateau common to both
ach100 = np.minimum(peak, ais * bw100)
ach200 = np.minimum(peak, ais * bw200)
# Distinguishable in grayscale: H100 = solid + 'o' markers, H200 = dashed + '^' markers.
ax.loglog(ais, ach100, color='#27408b', lw=2.2, ls='-', marker='o',
          markevery=22, ms=3.2, label='H100 FP16 (3.35 TB/s)')
ax.loglog(ais, ach200, color='#c0392b', lw=1.9, ls='--', marker='^',
          markevery=22, ms=3.6, label='H200 FP16 (4.8 TB/s)')
# Ridge points (solid/dashed vertical lines + labeled markers)
ax.axvline(r100, color='#27408b', ls=':', lw=1.2)
ax.axvline(r200, color='#c0392b', ls=':', lw=1.2)
ax.plot([r100], [peak*0.35], marker='o', color='#27408b', ms=6, ls='none', zorder=6)
ax.plot([r200], [peak*0.10], marker='^', color='#c0392b', ms=7, ls='none', zorder=6)
ax.text(r100, peak*0.42, f'ridge ≈ {r100:.0f}', fontsize=8.5, color='#27408b', ha='center')
ax.text(r200*0.97, peak*0.05, f'ridge ≈ {r200:.0f}', fontsize=8.5, color='#c0392b', ha='center')

# Compute plateau ceiling (shared by both parts), plus region labels made explicit.
ax.axhline(peak, color='gray', ls='-.', lw=1.0, alpha=0.75)
ax.text(0.985, 0.36, 'compute plateau\n= 989 TFLOPS',
        transform=ax.transAxes, fontsize=8.5, color='#6f9e5f',
        ha='right', va='center')
ax.text(0.06, 0.10, 'memory-bound slope\n(≈ intensity × BW)',
        transform=ax.transAxes, fontsize=8.5, color='#e67e22',
        ha='left', va='center')
# DERIVED / source tag in-plot (top-centre, clear of PER GPU at left and prefill ridge at right)
ax.text(0.50, 0.965, 'ANALYTICAL [DERIVED]', transform=ax.transAxes,
        fontsize=8, color='#8a5a00', ha='center', va='top')

# "PER GPU" stated plainly INSIDE the plotting area (top-left of the axes),
# so the figure carries its own single-GPU qualification.
ax.text(0.02, 0.965, 'PER GPU', transform=ax.transAxes, fontsize=10,
        fontweight='bold', color='#333333', ha='left', va='top',
        bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='#888888', alpha=0.9))

# Operating points. Prefill intensity is set by sequence length (weights read once,
# reused across all tokens) -> to the RIGHT of the ridge, on the plateau (compute-bound).
# Decode re-reads weights each token -> low intensity, LEFT of the ridge, on the slope.
pts = [
    ('prefill 9.2K', 9200, 989, 'prefill'),  # canonical: intensity ≈ sequence length ≈ 9.2K FLOP/byte
    ('decode batch=1', 0.5, 1.7, 'decode'),  # canonical
    ('decode batched', 8, 27, 'decode'),     # continuous batching raises intensity
]
colors = {'prefill': '#e67e22', 'decode': '#27408b'}
for name, a, t, tag in pts:
    ax.scatter([a], [min(t, peak)], color=colors[tag], zorder=5, s=45)

# label the markers, offset so they do not sit on the dots
ax.text(9200, 989*0.55, 'prefill 9.2K\n(intensity ≈ 9.2K\nFLOP/byte)', fontsize=9,
        color=colors['prefill'], ha='center', va='top')
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
