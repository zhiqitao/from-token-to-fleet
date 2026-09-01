import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-26-2602: six-axis workload radar (RAG / chat / batch) ----
axis_labels = ['Quality\nrequired', 'Traffic\n(rps)', 'Context\nlength', 'Output\ntokens', 'Latency\n-sensitive', 'Cost\n-sensitive']
N = len(axis_labels)
angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
angles += angles[:1]

profiles = {
    'Long-context RAG Q&A': [0.9, 0.5, 0.9, 0.3, 0.8, 0.5],
    'High-throughput chat': [0.6, 0.9, 0.3, 0.8, 0.9, 0.5],
    'Batch inference':      [0.6, 0.8, 0.7, 0.8, 0.2, 0.9],
}
colors = {'Long-context RAG Q&A': '#3a6ea5', 'High-throughput chat': '#e67e22', 'Batch inference': '#6f9e5f'}

fig, ax = plt.subplots(figsize=(8.5, 8), subplot_kw=dict(polar=True))
for name, vals in profiles.items():
    v = vals + vals[:1]
    ax.plot(angles, v, '-o', color=colors[name], lw=2, label=name, ms=4)
    ax.fill(angles, v, color=colors[name], alpha=0.10)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(axis_labels, fontsize=9)
ax.set_ylim(0, 1)
ax.set_title('Workload fingerprints — the six axes of §4 \u00d7 the matrix of §26', fontsize=12, fontweight='bold', pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.12), fontsize=9)
plt.tight_layout()
plt.savefig('design/manuscript/chapter-26/figures/fig-26-2602.png', dpi=150)
plt.close()
print('wrote fig-26-2602')
