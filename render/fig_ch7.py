import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-07-0701: KV-cache size vs context length (70B-class) ----
ctx = np.array([1, 4, 9.2, 32, 128])  # K tokens
# canonical (Ch. 7, Table 7-1): full-MHA teaching bound 2.62 MB/token ~2.5 MB/token
# real LLaMA-2-70B-class GQA (8 KV heads): 2*80*8*128*2 B = 0.33 MB/token (8x smaller)
kv_fp16 = 2.5 * ctx   # GB  (full-MHA FP16 bound)
kv_fp8  = 1.3 * ctx   # GB  8-bit bound
kv_gqa  = 0.33 * ctx  # GB  (real GQA 70B-class)
kv_fp8_avail = 500    # GB  KV-available ceiling: 640 total - 140 weights

fig, ax = plt.subplots(figsize=(7, 5.2))
ax.plot(ctx, kv_fp16, '-o', color='#c0392b', label='full-MHA FP16 (bound, ~2.5 MB/tok)')
ax.plot(ctx, kv_fp8, '-s', color='#e67e22', label='full-MHA FP8 (~1.3 MB/tok)')
ax.plot(ctx, kv_gqa, '-^', color='#27408b', label='GQA FP16 (~0.33 MB/tok)')
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('Context length (K tokens)')
ax.set_ylabel('KV-cache size (GB)')
ax.set_title('KV-cache size vs context — 70B-class model')
# ceiling: point out the KV-available budget, not the raw 640 GB total
ax.axhline(640, color='#7f8c8d', ls=':', lw=1, label='8×H100 raw (640 GB)')
ax.axhline(500, color='#27408b', ls='--', lw=1.5, label='KV-available ~500 GB (640 − 140 weights)')
ax.scatter([9.2], [2.5*9.2], color='#c0392b', zorder=5, s=25)
ax.annotate('9.2K ≈ 24 GB (FP16 bound)', xy=(9.2, 2.5*9.2), xytext=(16, 16),
            arrowprops=dict(arrowstyle='->'), fontsize=8)
ax.scatter([9.2], [0.33*9.2], color='#27408b', zorder=5, s=25)
ax.annotate('9.2K ≈ 3 GB (GQA) — 8× saving\nvs full-MHA bound (Ch. 7 attention note)', xy=(9.2, 0.33*9.2), xytext=(14, 0.9),
            arrowprops=dict(arrowstyle='->', color='#27408b'), fontsize=8, color='#27408b')
ax.legend(fontsize=7.5, loc='upper left')
ax.grid(alpha=0.3, which='both')
ax.set_xlim(0.8, 1600)
plt.tight_layout()
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0701.png', dpi=150)
plt.close()
print('wrote fig-07-0701')

# ---- fig-07-0702: Inference vs fine-tuning memory floor ----
labels = ['Inference\n(weights+KV)', 'Full fine-tune\n(weights+grad+optimizer)', 'QLoRA\n(weights+adapters)']
vals = [165, 1260, 60]
fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(labels, vals, color=['#3a6ea5', '#c0392b', '#6f9e5f'])
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v+20, f'~{v} GB', ha='center', fontsize=11, fontweight='bold')
ax.set_ylabel('GPU memory floor (GB)')
ax.set_title('Memory floor: inference vs fine-tuning (70B)')
ax.axhline(160, color='#888', ls='--', lw=1, label='2×H100 (160 GB)')
ax.axhline(640, color='#27408b', ls='--', lw=1, label='8×H100 (640 GB)')
ax.axhline(80, color='#6f9e5f', ls='--', lw=1, label='1×H100 (80 GB)')
ax.axvspan(0, 2.5, color='#6f9e5f', alpha=0.06)
ax.annotate('QLoRA runs on a single H100', xy=(2, 60), xytext=(0.05, 0.82), xycoords=('data','axes fraction'),
            fontsize=8.5, color='#3d6e35', arrowprops=dict(arrowstyle='->', color='#3d6e35'))
ax.legend(fontsize=8)
ax.grid(alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0702.png', dpi=150)
plt.close()
print('wrote fig-07-0702')
