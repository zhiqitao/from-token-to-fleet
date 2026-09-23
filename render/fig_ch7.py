import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-07-0701: KV cache size vs context length (70B-class) ----
ctx = np.array([1, 4, 9.2, 32, 128])  # K tokens
# canonical (Ch. 7, Table 7-1): full-MHA teaching bound 2.62 MB/token ~2.5 MB/token
# real LLaMA-2-70B-class GQA (8 KV heads): 2*80*8*128*2 B = 0.33 MB/token (8x smaller)
kv_fp16 = 2.5 * ctx   # GB  (full-MHA FP16 bound)
kv_fp8  = 1.3 * ctx   # GB  8-bit full-MHA bound
kv_gqa  = 0.33 * ctx  # GB  (real GQA 70B-class)
kv_gqa8 = 0.165 * ctx # GB  GQA + 8-bit KV (~half of GQA FP16)

fig, ax = plt.subplots(figsize=(6.1, 4.6))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.plot(ctx, kv_fp16, '-o', color='#c0392b', label='full-MHA FP16 (bound, ~2.62 MB/tok)')
ax.plot(ctx, kv_fp8, '-s', color='#e67e22', label='full-MHA FP8 (byte-halving bound, ~1.3 MB/tok)')
ax.plot(ctx, kv_gqa, '-^', color='#27408b', label='GQA FP16 (~0.33 MB/tok)')
ax.plot(ctx, kv_gqa8, '-v', color='#6f9e5f', label='GQA FP8 (~0.17 MB/tok)')
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('Context length (K tokens)', fontsize=9.5)
ax.set_ylabel('KV cache size (GB)', fontsize=9.5)
ax.set_title('KV cache size vs context, by attention geometry (full-MHA vs GQA)')
# KV budget ceiling: 640 total - 140 weights - ~64 runtime/NCCL = ~436 GB usable KV
ax.axhline(640, color='#7f8c8d', ls=':', lw=1, label='8×H100 raw (640 GB)')
ax.axhline(436, color='#27408b', ls='--', lw=1.5, label='KV budget ~436 GB (640 − 140 w − 64 rt)')
ax.scatter([9.2], [2.5*9.2], color='#c0392b', zorder=5, s=25)
ax.annotate('9.2K ≈ 24 GB (FP16 bound)', xy=(9.2, 2.5*9.2), xytext=(18, 1.2),
            arrowprops=dict(arrowstyle='->'), fontsize=8.5)
ax.scatter([9.2], [0.33*9.2], color='#27408b', zorder=5, s=25)
ax.annotate('9.2K ≈ 3 GB (GQA) — 8× saving\nvs full-MHA bound (Ch. 7 attention note)', xy=(9.2, 0.33*9.2), xytext=(20, 0.07),
            arrowprops=dict(arrowstyle='->', color='#27408b'), fontsize=8.5, color='#27408b')
ax.legend(fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.10), ncol=2, frameon=False)
ax.grid(alpha=0.3, which='both')
ax.set_xlim(0.8, 1600)
ax.set_ylim(0.05, 2000)
plt.tight_layout(rect=[0, 0.06, 1, 1])
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0701.png', dpi=150)
plt.close()
print('wrote fig-07-0701')

# ---- fig-07-0702: Inference vs fine-tuning memory floor ----
labels = ['Inference\n(weights+KV)', 'Full fine-tune\n(weights+grad+optimizer)', 'QLoRA\n(weights+adapters)']
vals = [165, 1120, 60]
fig, ax = plt.subplots(figsize=(6.5, 4.9))
bars = ax.bar(labels, vals, color=['#3a6ea5', '#c0392b', '#6f9e5f'], width=0.6)
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v+30, f'~{v} GB', ha='center', fontsize=10, fontweight='bold')
ax.set_ylabel('GPU memory floor (GB)')
ax.set_title('Memory floor: inference vs fine-tuning (70B)')
ax.axhline(160, color='#888', ls='--', lw=1, label='2×H100 (160 GB)')
ax.axhline(640, color='#27408b', ls='--', lw=1, label='8×H100 (640 GB)')
ax.axhline(80, color='#6f9e5f', ls='--', lw=1, label='1×H100 (80 GB)')
ax.set_ylim(0, 1500)
# annotations moved OUT of the bar area into clear white space (no label crossing the bars)
ax.text(1.35, 1430, 'full fine-tune exceeds an 8×H100 host:\nneeds multi-node or offload', fontsize=8, color='#c0392b', ha='center')
ax.annotate('QLoRA fits a single H100', xy=(2, 60), xytext=(2.4, 250),
            fontsize=8.5, color='#3d6e35', arrowprops=dict(arrowstyle='->', color='#3d6e35'))
ax.legend(fontsize=8, loc='upper left')
ax.grid(alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0702.png', dpi=150)
plt.close()
print('wrote fig-07-0702')
