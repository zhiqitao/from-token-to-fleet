import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-26-2602: Workload fingerprints (replaces misleading radar) ----
# A radar chart's enclosed-area reading is invalid (axis-order + normalisation
# dependent).  We use a grouped BAR chart instead: each workload's normalised
# profile on six comparably-scaled axes, encoded by height + hatch (grayscale-safe).
dims = ['Context\nlength', 'Traffic\n(rps)', 'Quality\nrequired', 'Cost\nsensitive',
        'Latency\nsensitive', 'Output\ntokens']
# normalised 0-1 profiles (illustrative, per the chapter's workload taxonomy)
longctx = [0.95, 0.20, 0.70, 0.55, 0.40, 0.45]
chat    = [0.35, 0.95, 0.50, 0.75, 0.90, 0.55]
batch   = [0.55, 0.60, 0.30, 0.85, 0.35, 0.90]

x = np.arange(len(dims)); wdt = 0.26
fig, ax = plt.subplots(figsize=(9.4, 4.4))
b1 = ax.bar(x-wdt, longctx, wdt, label='Long-context RAG Q&A', color='#3a6ea5', hatch='//')
b2 = ax.bar(x,     chat,    wdt, label='High-throughput chat', color='#e67e22', hatch='xx')
b3 = ax.bar(x+wdt, batch,   wdt, label='Batch inference',      color='#6f9e5f', hatch='..')

ax.set_xticks(x); ax.set_xticklabels(dims, fontsize=8.5)
ax.set_ylabel('Normalised intensity (0-1)')
ax.set_ylim(0, 1.1)
ax.set_title('Workload fingerprints on six comparable axes (grouped bars, not radar)', fontsize=11)
ax.legend(fontsize=8, loc='upper right')
ax.grid(axis='y', alpha=0.3)
ax.text(0.02, -0.18, 'lower cost-sensitive / latency-sensitive means less sensitive.\nComparable 0-1 normalisation; height encodes intensity (a radar area would not). [ILLUSTRATIVE]',
        transform=ax.transAxes, fontsize=7.5, color='#666', va='top')
plt.tight_layout()
plt.savefig('design/manuscript/chapter-26/figures/fig-26-2602.png', dpi=150)
plt.close()
print('wrote fig-26-2602 (grouped bars)')
