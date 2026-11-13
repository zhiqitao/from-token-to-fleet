import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-06-0602: Latency distribution (p50/p90/p95/p99 + mean) ----
# 99% of requests ~ log-normal around a healthy p50 ~0.75-0.8 s, 1% stragglers at 5 s.
# The point of Fig 6.2: the mean (~0.84 s) looks healthy, but the 1% tail is real.
# Percentiles are read off THIS SYNTHETIC stream (p50=0.80, p90=0.94, p95=0.99, p99=1.33);
# the 1% stragglers beyond the 99th percentile are the ones that cross the 2 s SLO.
rng = np.random.default_rng(42)
healthy = rng.lognormal(mean=np.log(0.8), sigma=0.12, size=9900)   # 99% around 0.8 s
stragg = np.full(100, 5.0)                                          # 1% at 5 s
lat = np.concatenate([healthy, stragg])
lat = np.clip(lat, 0.2, 6.0)

fig, ax = plt.subplots(figsize=(6.1, 4.2))
fig._hermes_print_sized = True   # regen must not re-boost/reflow
ax.hist(lat, bins=60, color='#3a6ea5', alpha=0.75, edgecolor='white', lw=0.3)
mean = lat.mean()
# p50/p90/p95 lines cluster near the left (0.8-1.0s of a 6.2s axis). Label each one
# directly above its own line (staggered vertically) instead of a far callout block:
# the old leader lines ran from x~0.9 to x~3.5 and crossed the p99 (1.33s) and SLO
# (2.0s) verticals, creating clutter. Direct labels have no leaders, so nothing crosses.
# FIG-6.2-01/04: the three greens were all identical dashed with name-only labels, so
# neither line identity nor the prose-quoted values (0.80/0.94/0.99) could be read off
# the plot. Now each line has its OWN dash style (distinguishable in grayscale) and each
# label carries its numeric value.
ytop = ax.get_ylim()[1]
# Stagger the three green percentile labels onto three clearly-separated rows
# (0.99 / 0.88 / 0.77 of ytop) so the boxes have comfortable vertical gaps; the
# p99 and SLO labels sit on the top row to the right, clear of this green stack.
leaders = [
    # (percentile, value, y-fraction, label side). p50's label goes LEFT of its line:
    # to the right it runs under the p99 label box at x=1.36, which hid the value.
    (50, np.percentile(lat, 50), 0.94, 'right'),
    (90, np.percentile(lat, 90), 0.85, 'left'),
    (95, np.percentile(lat, 95), 0.75, 'left'),
]
pct_ls = {50: '--', 90: '-.', 95: ':'}   # distinct styles, readable in grayscale
for p, v, dy_off, side in leaders:
    ax.axvline(v, color='#6f9e5f', ls=pct_ls[p], lw=1.3)
    x, ha = (v + 0.03, 'left') if side == 'left' else (v - 0.03, 'right')
    ax.text(x, ytop * dy_off, f'p{p} {v:.2f}', fontsize=8.5, color='#2f6f4f',
            fontweight='bold', va='center', ha=ha,
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='#cfcfcf', lw=0.5))
# p99 breaches the tail? NO — p99=1.33 is still under the 2s SLO. Emphasize it in red.
v99 = np.percentile(lat, 99)
ax.axvline(v99, color='#c0392b', ls='--', lw=1.9)
# the 5s stragglers sit beyond p99 — between p99 and p100 — so a p99 line alone does
# not reveal them. The shaded band below marks the straggler region; a separate dotted
# line at the max (5.0) was removed because it ran straight through the band's label.
# mean line
ax.axvline(mean, color='#555', ls='-', lw=1.7)
# 2 s SLO line
ax.axvline(2.0, color='#27408b', ls='-.', lw=2.2)
# Label p99 and SLO directly on their lines (the green p50/p90/p95 are already
# labeled; the mean is identified by the text box). p99 (1.33 s) sits on the top
# row to the right of the green stack. The SLO label now reads
# "SLO 2 s (TTFT budget)" (metric named, per review fix), which is wide enough
# that on the top row its box would run under the legend box — so it sits at
# mid-height on its own line instead, in clear space right of x=2.
ax.text(v99 + 0.03, ytop * 0.94, 'p99', fontsize=8.5, color='#c0392b',
        fontweight='bold', va='center', ha='left',
        bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='#c0392b', lw=0.5))
ax.text(2.03, ytop * 0.45, 'SLO 2 s (TTFT budget)', fontsize=8.5, color='#27408b',
        fontweight='bold', va='center', ha='left',
        bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='#27408b', lw=0.5))
# Compact legend in the clear upper-right whitespace (the annotated lines all cluster
# near x=0.8-2.0 on a 6.2s axis, so label them as a legend, not along the crowded lines).
ax.text(3.45, ax.get_ylim()[1]*0.86, 'mean = %.2fs\np99 = %.2fs\nSLO 2 s (TTFT budget)\n(p99 still looks fine)' % (mean, v99),
        fontsize=8.5, color='#333', ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.35', fc='#f7f7f7', ec='#cccccc', lw=0.8))
# P2-07: shade the ENTIRE SLO-violating region (> 2 s, everything right of the
# SLO line) lightly, and mark the 5 s straggler cluster inside it with a darker
# hatched band.  The old shading started at 4 s, which left the 2-4 s violating
# region unshaded and understated the violation area.
ax.axvspan(2.0, 6.2, facecolor='#c0392b', alpha=0.10, zorder=0)
ax.axvspan(4.5, 5.5, facecolor='#c0392b', alpha=0.22, zorder=0)
# hatch drawn as its own facecolor='none' patch: `color=` would override
# edgecolor (killing the dark hatch) and a patch-level alpha would fade it.
ax.axvspan(4.5, 5.5, facecolor='none', edgecolor='#7b241c', hatch='///',
           linewidth=0.0, alpha=0.85, zorder=1)   # lw 0 = no border rectangle
ax.text(3.3, ytop * 0.60, 'SLO-violating region (> 2 s)', fontsize=8.5,
        color='#c0392b', ha='center', va='center', fontweight='bold')
# place the stragglers label in the CLEAR upper region of the red band (the tail
# bars near x=5 are tiny, and the legend box ends at x=4.0), so it never sits on a bar.
ax.text(5.0, ytop*0.72, '1% stragglers\n~5 s (cross the SLO)', fontsize=8.5, color='#c0392b',
        ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#c0392b', lw=0.8, alpha=0.95))

ax.set_xlabel('Request latency (s)', fontsize=9.5)
ax.set_ylabel('Request count', fontsize=9.5)
ax.set_title('Latency distribution: the mean hides the tail', fontsize=10.5, pad=26)
# bold ILLUSTRATIVE tag as a distinct subtitle line (clear below the title)
ax.text(0.5, 1.055, '[ILLUSTRATIVE synthetic profile]', transform=ax.transAxes, fontsize=9,
        fontweight='bold', color='#8a3a12', ha='center', va='bottom')
ax.set_xlim(0, 6.2)
# y-axis headroom so the peak bar (≈3023) is not clipped at a round 3000 limit
ax.set_ylim(0, 3300)
ax.grid(alpha=0.2, axis='y')
ax.tick_params(labelsize=9)
plt.tight_layout()
plt.savefig('design/manuscript/chapter-06/figures/fig-06-0602.png', dpi=350)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-06/figures/fig-06-0602.pdf', format='pdf')
plt.close()
print('wrote fig-06-0602')
