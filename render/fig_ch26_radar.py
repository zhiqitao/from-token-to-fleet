import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-26-2602: six-axis workload radar (RAG / chat / batch) ----
# Profiles given as distinct dash patterns AND colours so the overlapping
# polygons stay distinguishable in print (and in grayscale).  Low fill opacity
# so the centre overlap doesn't muddy; larger perimeter labels.
axis_labels = ['Quality\nrequired', 'Traffic\n(rps)', 'Context\nlength', 'Output\ntokens',
               'Latency\n-sensitive', 'Cost\n-sensitive']
N = len(axis_labels)
angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
angles += angles[:1]

profiles = {
    'Long-context RAG Q&A': [0.9, 0.5, 0.9, 0.3, 0.8, 0.5],
    'High-throughput chat': [0.6, 0.9, 0.3, 0.8, 0.9, 0.5],
    'Batch inference':      [0.6, 0.8, 0.7, 0.8, 0.2, 0.9],
}
colors = {'Long-context RAG Q&A': '#3a6ea5', 'High-throughput chat': '#e67e22', 'Batch inference': '#6f9e5f'}
dashes = {'Long-context RAG Q&A': (0, (4, 2)), 'High-throughput chat': (0, (8, 3)), 'Batch inference': (0, ())}

fig, ax = plt.subplots(figsize=(9, 8.5), subplot_kw=dict(polar=True))
for name, vals in profiles.items():
    v = vals + vals[:1]
    ax.plot(angles, v, '-o', color=colors[name], lw=2.2, label=name, ms=5,
            ls=dashes[name])
    ax.fill(angles, v, color=colors[name], alpha=0.06)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(axis_labels, fontsize=10)
ax.tick_params(axis='x', pad=16)
ax.set_ylim(0, 1)
ax.set_title('Workload fingerprints on six axes', fontsize=13,
             fontweight='bold', pad=28)
# Legend below the chart (clear of the title/perimeter), single row.
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.06), fontsize=9.5,
          ncol=3, frameon=False)
ax.grid(alpha=0.35)
plt.tight_layout()
# RETIRED: the radar was superseded by the grouped-bar fingerprint (fig_ch26_fingerprint.py)
# because a radar chart's enclosed-area reading is invalid (axis-order + normalisation
# dependent) per the chapter's own reasoning. Do not write fig-26-2602 from here.
# plt.savefig('design/manuscript/chapter-26/figures/fig-26-2602.png', dpi=150)
plt.close()
print('RETIRED radar (fig_ch26_radar.py); grouped-bar fingerprint writes fig-26-2602')
