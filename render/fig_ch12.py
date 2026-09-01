import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-12-1201: Three candidate architectures (TAB 12.1) ----
# Figure values traced to the authoritative Table 12.1 in chapter-12.md.
# (b) is a P/D-disaggregated TWO-POOL = 2 × 8×H100 hosts (2×8, not 2×4).
# Throughput: (a) prefill ~1,200 / decode ~300; (b) prefill pool ~2,471,
# decode pool bandwidth-bound (no single digit); (c) fails the quality
# ceiling and is EXCLUDED at the quality gate, so no throughput bar.
# All digits are [2 DEG DERIVED] worked examples from the §14 canonical case.
cands = ['(a) 8×H100\n+prefix cache', '(b) P/D-disagg\n2×8×H100', '(c) KV-quant\n7B 1×H100']
weight = [140, 140, 14]   # GB (Table 12.1)
kv     = [24, 24, 6]      # GB

total = [a+b for a, b in zip(weight, kv)]

fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))

# Panel 1: memory SLO satisfaction (weight+KV stacked, ceiling lines)
ax = axes[0]
ax.bar(range(3), weight, label='weights', color='#3a6ea5')
ax.bar(range(3), kv, bottom=weight, label='KV-cache', color='#e67e22')
for i, t in enumerate(total):
    ax.text(i, t+8, f'{t} GB', ha='center', fontsize=10, fontweight='bold')
ax.axhline(640, color='#27408b', ls='--', lw=1.5, label='8×H100 ceiling')
ax.axhline(80, color='#888', ls=':', lw=1.2, label='1×H100 ceiling')
ax.set_xticks(range(3)); ax.set_xticklabels(cands, fontsize=8)
ax.set_ylabel('Resident memory (GB)')
ax.set_title('(1) Memory footprint')
ax.legend(fontsize=7, loc='upper right')
ax.grid(alpha=0.3, axis='y')
ax.set_ylim(0, 700)

# Panel 2: throughput — only where Table 12.1 gives an authoritative digit.
ax = axes[1]
w = 0.38
# (a) prefill 1200/decode 300; (b) prefill-pool 2471, decode bandwidth-bound
bars = ax.bar([-w/2, 1-w/2], [1200, 2471], w, color='#3a6ea5', label='prefill')
ax.bar([w/2], [300], w, color='#6f9e5f', label='decode')
ax.text(-w/2, 1280, '1,200', ha='center', fontsize=8, fontweight='bold')
ax.text(1-w/2, 2550, '2,471', ha='center', fontsize=8, fontweight='bold')
ax.text(w/2, 380, '300', ha='center', fontsize=8, fontweight='bold')
ax.set_xticks([0, 1, 2]); ax.set_xticklabels(cands, fontsize=8)
ax.set_ylabel('Throughput (tokens/s)')
ax.set_title('(2) Throughput')
ax.legend(fontsize=8, loc='upper left')
ax.grid(alpha=0.3, axis='y')
ax.set_ylim(0, 3000)
# qualitative labels where the table has no single digit
ax.text(1.5, 900, 'decode pool:\nbandwidth-bound\n(no digit)', ha='center',
        fontsize=7, color='#555')
ax.text(1.9, 2350, '(c) excluded at\nquality gate', ha='center', fontsize=7.5,
        color='#c0392b', fontweight='bold')

# Panel 3: latency / SLO verdict (assertions, no uncertainty '?')
ax = axes[2]
verdicts = ['✓ in 5 s', '✓ at scale', '✗ quality']
colors = ['#6f9e5f', '#6f9e5f', '#c0392b']
bars = ax.bar(cands, [1,1,1], color=colors)
for b, v in zip(bars, verdicts):
    ax.text(b.get_x()+b.get_width()/2, 0.5, v, ha='center', va='center',
            fontsize=9, color='white', fontweight='bold')
ax.set_ylim(0, 1.6)
ax.set_yticks([])
ax.set_title('(3) Constraint verdict')
for s in ['top','right']:
    ax.spines[s].set_visible(False)

plt.tight_layout()
plt.savefig('design/manuscript/chapter-12/figures/fig-12-1201.png', dpi=150)
plt.close()
print('wrote fig-12-1201.png')
