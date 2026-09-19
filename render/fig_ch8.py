import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-08-0801: Roofline for canonical 70B FP16 decoder, H100 + H200, context drift ----
# H100: 989 TFLOPS dense FP16, 3.35 TB/s -> ridge 295
# H200: 989 TFLOPS dense FP16 (same GH100 die), 4.8 TB/s -> ridge 206

def ridge(peak_tflops, bw_tb):
    return peak_tflops / bw_tb

peak = 989
bw100 = 3.35
bw200 = 4.8
r100 = ridge(peak, bw100)   # ~295
r200 = ridge(peak, bw200)   # ~206

ais = np.logspace(-1, 3, 400)

fig, ax = plt.subplots(figsize=(6.5, 4.7))
# H100 ridge (solid) and the compute plateau common to both
ach100 = np.minimum(peak, ais * bw100)
ach200 = np.minimum(peak, ais * bw200)
ax.loglog(ais, ach100, color='#27408b', lw=2.4, label='Roofline — H100 FP16 (3.35 TB/s)')
ax.loglog(ais, ach200, color='#c0392b', lw=2.0, ls='--', label='Roofline — H200 FP16 (4.8 TB/s)')
ax.axvline(r100, color='#27408b', ls=':', lw=1.3)
ax.axvline(r200, color='#c0392b', ls=':', lw=1.3)
ax.text(r100, 260, f'ridge ≈ {r100:.0f}', fontsize=8, color='#27408b', ha='center')
ax.text(r200*0.98, 5.5, f'ridge ≈ {r200:.0f}', fontsize=8, color='#c0392b', ha='center')

# operating points: decode below ridge (memory-bound, on the slope); prefill on the plateau (compute-bound).
# Prefill intensity is set by sequence length (weights read once, reused across all tokens), so it is
# well to the RIGHT of the ridge and sits on the compute-bound plateau -- never above the roofline.
pts = [
    ('prefill 9.2K (batch=1)', 320, 989, 'prefill'),
    ('prefill 32K', 480, 989, 'prefill'),
    ('prefill 128K', 720, 989, 'prefill'),
    ('decode batch=1', 0.5, 1.7, 'decode'),
    ('decode batch=32', 8, 27, 'decode'),
]
colors = {'prefill': '#e67e22', 'decode': '#27408b'}
for name, a, t, tag in pts:
    ax.scatter([a], [min(t, peak)], color=colors[tag], zorder=5, s=55)

# Continuous-batching arrow: decode batch=1 (memory-bound) -> decode batch=32 up the slope
ax.annotate('', xy=(8, 27), xytext=(0.55, 1.75),
            arrowprops=dict(arrowstyle='->', lw=2.2, color='#27408b',
                            connectionstyle='arc3,rad=0.15'))
ax.text(2.2, 0.62, 'Continuous Batching', fontsize=8.5, color='#27408b', fontweight='bold')
ax.text(2.2, 0.48, 'raises arithmetic intensity,\nclimbs the slope', fontsize=7.5, color='#27408b')

# annotations placed away from the markers (offset the labels so they do not sit on the dots)
ann = {
    'prefill 9.2K (batch=1)': (0.62, 0.80),
    'prefill 32K': (0.62, 0.92),
    'prefill 128K': (0.62, 1.02),
    'decode batch=1': (0.48, 0.92),
    'decode batch=32': (2.4, 0.78),
}
for name, a, t, tag in pts:
    ax.text(a*ann[name][0], min(t, peak)*ann[name][1], name, fontsize=8.5, color=colors[tag], ha='center')

# drift arrow between the two on-plateau points (32K -> 128K), visible above the plateau
ax.annotate('', xy=(720, 989*0.90), xytext=(480, 989*0.90),
            arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#6f9e5f', ls='--'))
# point note parked in a clear area (upper-left, above the memory-bound slope, left of the plateau labels)
ax.text(0.30, 0.05, 'prefill is compute-bound: it sits on the\nplateau (right of the ridge) and climbs it\nas context grows (+60% @32K, ~2.4× @128K)',
        fontsize=8, color='#6f9e5f')

ax.set_xlabel('Arithmetic intensity (FLOP/byte)')
ax.set_ylabel('Achievable performance (TFLOPS)')
ax.set_title('Roofline — 70B FP16 on 8×H100 / 8×H200')
ax.grid(alpha=0.3, which='both')
ax.legend(fontsize=8, loc='lower right')
ax.text(1.6*r100, 500, 'compute-bound', fontsize=9, color='#6f9e5f', ha='center')
ax.text(0.06*r100, 0.9, 'memory-bound', fontsize=9, color='#e67e22', ha='center')
plt.tight_layout()
plt.savefig('design/manuscript/chapter-08/figures/fig-08-0801.png', dpi=150)
plt.close()
print('wrote fig-08-0801')
