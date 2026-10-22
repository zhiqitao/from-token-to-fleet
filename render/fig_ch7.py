import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-07-0701: KV cache size vs context length (70B-class) ----
ctx = np.array([1, 4, 9.2, 32, 128])  # K tokens
# canonical (Ch. 7, Table 7-1): full-MHA teaching bound 2.62 MB/token ~2.5 MB/token
# real LLaMA-2-70B-class GQA (8 KV heads): 2*80*8*128*2 B = 0.33 MB/token (8x smaller)
# FP8 uses the MEASURED operating constant ~1.42 MB/token (54% of BF16, NOT a naive 50%).
kv_fp16 = 2.5 * ctx   # GB  (full-MHA FP16 bound)
kv_fp8  = 1.42 * ctx  # GB  (full-MHA FP16 * 0.54 = measured FP8 operating constant, ~1.42 MB/tok)
kv_gqa  = 0.33 * ctx  # GB  (real GQA 70B-class)
kv_gqa8 = 0.33 * 0.54 * ctx  # GB  GQA + measured FP8 (~54% of GQA FP16)

fig, ax = plt.subplots(figsize=(6.1, 4.6))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.plot(ctx, kv_fp16, '-o', color='#c0392b', label='full-MHA FP16 (bound, ~2.62 MB/tok)')
ax.plot(ctx, kv_fp8, '-s', color='#e67e22', label='full-MHA FP8 (~1.42 MB/tok, 54% of BF16)')
ax.plot(ctx, kv_gqa, '-^', color='#27408b', label='GQA FP16 (~0.33 MB/tok)')
ax.plot(ctx, kv_gqa8, '-v', color='#6f9e5f', label='GQA FP8 (~0.18 MB/tok)')
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('Context length (K tokens)', fontsize=9.5)
ax.set_ylabel('KV cache size (GB)', fontsize=9.5)
ax.set_title('KV cache size vs context, by attention geometry (full-MHA vs GQA)')
# KV budget ceiling: 640 total - 140 weights - ~64 runtime/NCCL = ~436 GB usable KV
ax.axhline(640, color='#7f8c8d', ls=':', lw=1, label='8×H100 raw (640 GB)')
ax.axhline(436, color='#27408b', ls='--', lw=1.5, label='KV budget ~436 GB (640 − 140 w − 64 rt)')
ax.scatter([9.2], [2.5*9.2], color='#c0392b', zorder=5, s=25)
ax.annotate('9.2K ≈ 24 GB (FP16 bound)', xy=(9.2, 2.5*9.2), xytext=(10.2, 70),
            arrowprops=dict(arrowstyle='->', lw=0.8), fontsize=8.5)
ax.scatter([9.2], [0.33*9.2], color='#27408b', zorder=5, s=25)
ax.annotate('9.2K ≈ 3 GB (GQA)\n8× saving (Ch. 7)', xy=(9.2, 0.33*9.2), xytext=(10.0, 0.9),
            arrowprops=dict(arrowstyle='->', lw=0.8, color='#27408b'),
            fontsize=8.5, color='#27408b')
ax.legend(fontsize=8.5, loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False)
ax.grid(alpha=0.3, which='both')
ax.set_xlim(0.8, 1600)
ax.set_ylim(0.05, 2000)
plt.tight_layout(rect=[0, 0.10, 1, 1])
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0701.png', dpi=150)
plt.close()
print('wrote fig-07-0701')

# ---- fig-07-0702: Inference vs fine-tuning memory floor ----
labels = ['Inference\n(weights+KV)', 'Full fine-tune\n(weights+grad+opt)', 'QLoRA\n(weights+adapters)']
vals = [165, 1120, 60]
fig, ax = plt.subplots(figsize=(6.1, 4.9))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
bars = ax.bar(labels, vals, color=['#3a6ea5', '#c0392b', '#6f9e5f'], width=0.6)
for b, v in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v+30, f'~{v} GB', ha='center', fontsize=10, fontweight='bold')
ax.set_ylabel('GPU memory floor (GB)')
ax.tick_params(axis='x', labelsize=9)
# title 2nd line shortened so it fits the 6.1in width (was clipped on the left)
ax.set_title('Memory floor: inference vs fine-tuning (canonical 70B FP16)\nEach column is a different scenario, not a single-variable comparison', fontsize=9)
# P0-04: each bar is a *conditional floor* (parameter/optimizer floor), not a
# generally achievable deployment config. State the key assumptions compactly.
# The legend is moved inside the plot (top, 2-col) so the footnote at the
# figure bottom has the full width and does not collide with the x-axis labels.
fig.text(0.5, 0.01,
         'Each bar is a conditional floor (weights + the listed states), not a full deployment config.\n'
         'Full fine-tune: FP16 weights + FP16 grads + Adam m/v/master (~16 B/param).\n'
         'Activation, microbatch/sequence, and offload/checkpointing are NOT included (Table 7-2).\n'
         'QLoRA: 4-bit (NF4) base + LoRA adapters + a small optimizer.\n'
         'Adapter rank, activation, and offload are NOT included (Table 7-2).',
         fontsize=8.0, color='#555', ha='center', va='bottom', linespacing=1.5)
ax.axhline(160, color='#888', ls='--', lw=1, label='2×H100 (160 GB)')
ax.axhline(640, color='#27408b', ls='--', lw=1, label='8×H100 (640 GB)')
ax.axhline(80, color='#6f9e5f', ls='--', lw=1, label='1×H100 (80 GB)')
ax.set_ylim(0, 1500)
# red annotation sits directly above the red bar (x=1), just above its value
# label (1150) and clear of the top legend band.
# red annotation sits clearly ABOVE the red bar's value label (~1150) with a
# white halo so the two never collide; keep it below the top legend band.
ax.text(1, 1255, 'full fine-tune exceeds an 8×H100 host:\nneeds multi-node or offload', fontsize=8,
        color='#c0392b', ha='center', va='bottom',
        bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.9))
# green annotation centered ABOVE the QLoRA bar (inside the plot, not past the
# right border), with a white halo and an arrow down to the bar.
ax.annotate('QLoRA fits a single H100', xy=(2, 64), xytext=(2.0, 260),
            fontsize=8.5, color='#3d6e35', ha='center',
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.9),
            arrowprops=dict(arrowstyle='->', color='#3d6e35'))
# legend in the upper-LEFT (empty area above the short ~165 GB inference bar),
# so the red annotation above the tall bar and the green note above QLoRA are
# clear of it.
ax.legend(fontsize=8, loc='upper left', ncol=1, frameon=False)
ax.grid(alpha=0.3, axis='y')
# reserve the bottom ~18% for the 5-line fig.text footnote (P0-04)
plt.tight_layout(rect=(0, 0.18, 1, 1))
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0702.png', dpi=150)
plt.close()
print('wrote fig-07-0702')
