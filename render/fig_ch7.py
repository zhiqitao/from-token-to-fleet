import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ---- fig-07-0701: KV cache size vs context length (70B-class) ----
ctx = np.array([1, 4, 9.2, 32, 128])  # K tokens
# canonical (Ch. 7, Table 7-1): full-MHA teaching bound 2.62 MB/token ~2.5 MB/token
# real LLaMA-2-70B-class GQA (8 KV heads): 2*80*8*128*2 B = 0.33 MB/token (8x smaller)
# FP8 = raw tensor byte-halving (exactly 50% of BF16): 2,621,440/2 = 1,310,720 B = 1.31 MB/tok.
# (The vLLM "54%" figure is a decode-inter-token-latency slope ratio, NOT a memory footprint.)
kv_fp16 = 2.5 * ctx   # GB  (full-MHA FP16 bound)
kv_fp8  = 1.31 * ctx  # GB  (full-MHA raw byte-halving = 50% of BF16, ~1.31 MB/tok)
kv_gqa  = 0.33 * ctx  # GB  (real GQA 70B-class)
kv_gqa8 = 0.33 * 0.5 * ctx  # GB  GQA + raw FP8 byte-halving (~50% of GQA FP16)

fig, ax = plt.subplots(figsize=(6.1, 4.6))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.plot(ctx, kv_fp16, '-o', color='#c0392b', label='full-MHA FP16 (bound, ~2.62 MB/tok)')
ax.plot(ctx, kv_fp8, '-s', color='#e67e22', label='full-MHA FP8 (raw byte-halving, 50%)')
ax.plot(ctx, kv_gqa, '-^', color='#27408b', label='GQA FP16 (~0.33 MB/tok)')
ax.plot(ctx, kv_gqa8, '-v', color='#6f9e5f', label='GQA FP8 (raw, ~0.17 MB/tok)')
ax.set_xscale('log'); ax.set_yscale('log')
# v9 review: the default log formatter draws tick exponents as mathtext
# superscripts = 0.7 x tick size = 7.0pt on page (sub-8pt).  Plain decimal tick
# labels keep every tick glyph at the full 10pt tick size.
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%g'))
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%g'))
ax.set_xlabel('Context length (K tokens)', fontsize=9.5)
ax.set_ylabel('KV cache size (GB)', fontsize=9.5)
ax.set_title('KV cache size vs context, by attention geometry (full-MHA vs GQA)', fontsize=10)
# KV budget ceiling: 640 total - 140 weights - ~64 runtime/NCCL = ~436 GB usable KV
ax.axhline(640, color='#7f8c8d', ls=':', lw=1, label='8×H100 raw (640 GB)')
ax.axhline(436, color='#27408b', ls='--', lw=1.5, label='KV budget ~436 GB')
ax.scatter([9.2], [2.5*9.2], color='#c0392b', zorder=5, s=25)
# Loop-2 review (N1): at xytext=(10.2, 70) the label sat just above the red
# FP16 curve and its right end crossed the line (measured: 0.0 pt clearance,
# arrow shaft 0.1 pt) - same-colour annotation-on-curve.  In log-log space the
# red curve climbs 1 decade per decade, so a 122pt-wide label can only clear it
# (and the 436 GB rule) by moving into the open upper-LEFT band, above every
# curve and below the KV-budget rule.  Measured clearances: label 9.7 pt off the
# red curve, 10.1 pt off the 436 GB rule, 19.1 pt inside the left frame; the
# leader drops onto the 9.2K point from above and crosses no curve.
ax.annotate('9.5K ≈ 24.9 GB (FP16 bound)', xy=(9.5, 2.62*9.5), xytext=(1.2, 107),
            arrowprops=dict(arrowstyle='->', lw=0.8), fontsize=8.5)
ax.scatter([9.5], [0.33*9.5], color='#27408b', zorder=5, s=25)
# v9 review: this tag sat ON the GQA FP16/FP8 markers at 9.2K and used the same
# blue as the GQA-FP16 curve.  Move it into the open right-hand whitespace
# (no data beyond x=128K) and recolour to neutral dark grey.  The leader starts
# inside the empty band between the two GQA curves, so in log-log space it stays
# between them (convex strip) and crosses no curve or marker.
ax.annotate('9.5K ≈ 3.1 GB (GQA)\n8× saving (Ch. 7)', xy=(9.5, 0.33*9.5), xytext=(240, 55),
            ha='left',
            arrowprops=dict(arrowstyle='->', lw=0.8, color='#555555'),
            fontsize=8.5, color='#3a3a3a')
ax.legend(fontsize=8.6, loc='upper center', bbox_to_anchor=(0.5, -0.24), ncol=2, frameon=False)
ax.grid(alpha=0.3, which='both')
ax.set_xlim(0.8, 1600)
ax.set_ylim(0.05, 2000)
# FP8 relabel: raw tensor byte-halving (50% of BF16), NOT a vLLM-measured serving footprint.
# v9 review: footnote was 6.8pt (sub-8pt on page).  Raise to 8.6pt; the single
# line no longer fits the 6.10in column at that size, so split it in two.
fig.text(0.5, 0.010,
         'FP8 shown as raw tensor byte-halving (exactly 50% of BF16, ~1.31 MB/tok)\n'
         '— not a vLLM-measured serving footprint.',
         fontsize=8.6, color='#555', ha='center', va='bottom', linespacing=1.3)
plt.tight_layout(rect=[0, 0.17, 1, 1])
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0701.png', dpi=350)
plt.close()
print('wrote fig-07-0701')

# ---- fig-07-0702: Inference vs fine-tuning memory floor ----
labels = ['Inference\n(weights+KV)', 'Full fine-tune\n(weights+grad+opt)', 'QLoRA\n(weights+adapters)']
vals = [165, 1120, 60]
fig, ax = plt.subplots(figsize=(6.1, 4.9))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
bars = ax.bar(labels, vals, color=['#3a6ea5', '#c0392b', '#6f9e5f'], width=0.6)
# v9 review: value tags must clear the host-reference rules (80/160/640 cross
# every column).  The QLoRA tag can't sit at 60+30 (the 80 GB rule ran through
# it) nor centred above the bar (the green annotation's arrow shaft is there),
# so it moves above the 160 GB rule and right of the shaft.
for i, (b, v) in enumerate(zip(bars, vals)):
    cx = b.get_x() + b.get_width() / 2.0
    if i == 2:
        ax.text(cx + 0.10, 200, f'~{v} GB', ha='left', fontsize=10, fontweight='bold')
    else:
        ax.text(cx, v + 30, f'~{v} GB', ha='center', fontsize=10, fontweight='bold')
ax.set_ylabel('GPU memory floor (GB)')
ax.set_xlabel('Workload scenario', fontsize=9.5)
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
         fontsize=8.2, color='#555', ha='center', va='bottom', linespacing=1.5)
# v9 review: all three host rules shared one dash pattern, so they were
# inseparable in grayscale.  Each now carries its own dash pattern as a
# NON-colour cue (dashed / dash-dot / dotted); the legend shows the samples.
ax.axhline(160, color='#888', ls='--', lw=1.1, label='2×H100 (160 GB)')
ax.axhline(640, color='#27408b', ls='-.', lw=1.5, label='8×H100 (640 GB)')
ax.axhline(80, color='#6f9e5f', ls=':', lw=1.4, label='1×H100 (80 GB)')
ax.set_ylim(0, 1500)
# red annotation sits directly above the red bar (x=1), just above its value
# label (1150) and clear of the top legend band.
# red annotation sits clearly ABOVE the red bar's value label (~1150) with a
# white halo so the two never collide; keep it below the top legend band.
ax.text(1, 1255, 'full fine-tune exceeds an 8×H100 host:\nneeds multi-node or offload', fontsize=8.2,
        color='#c0392b', ha='center', va='bottom',
        bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.9))
# green annotation centered ABOVE the QLoRA bar (inside the plot, not past the
# right border), with a white halo and an arrow down to the bar.  Raised to 300
# so its shaft clears the relocated '~60 GB' tag (top ~242) with >9pt of air.
# Loop-2 review: centred on x=2 the label's right edge (incl. its white halo)
# came within 0.5 pt of the right spine - it read as clipping.  Inset to x=1.9
# (still above the QLoRA bar, still 23 pt right of the red bar) for 13.3 pt of
# halo clearance to the frame.
ax.annotate('QLoRA fits a single H100', xy=(2, 64), xytext=(1.9, 300),
            fontsize=8.5, color='#3d6e35', ha='center',
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.9),
            arrowprops=dict(arrowstyle='->', color='#3d6e35'))
# legend in the upper-LEFT (empty area above the short ~165 GB inference bar),
# so the red annotation above the tall bar and the green note above QLoRA are
# clear of it.
ax.legend(fontsize=8.2, loc='upper left', ncol=1, frameon=False)
ax.grid(alpha=0.3, axis='y')
# reserve the bottom ~18% for the 5-line fig.text footnote (P0-04)
plt.tight_layout(rect=(0, 0.18, 1, 1))
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0702.png', dpi=350)
plt.close()
print('wrote fig-07-0702')
