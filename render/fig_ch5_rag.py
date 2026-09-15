import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-05-0501: Model selection for RAG ----
# workload -> five selection surfaces -> two legs (retrieval/generation)
# -> RAG system decision.  [ILLUSTRATIVE conceptual]
fig, ax = plt.subplots(figsize=(9.2, 6.4))
ax.set_xlim(0, 24); ax.set_ylim(0, 17); ax.axis('off')

def box(x, y, w, h, head, sub, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.12', fc=fc, ec='#888', lw=1.1, alpha=0.9))
    ax.text(x+w/2, y+h*0.66, head, ha='center', va='center', fontsize=10, fontweight='bold', color='#222')
    ax.text(x+w/2, y+h*0.32, sub, ha='center', va='center', fontsize=8.5, color='#333')

# Top row
box(1.0, 13.2, 8.5, 2.6, 'Workload characterization', 'tokens · cost · SLO', '#dff0d8')
box(14.0, 13.2, 8.5, 2.6, 'Five selection surfaces', 'quality · latency · KV · $/tok · RAG', '#fde3e0')
ax.annotate('', xy=(14.0, 14.5), xytext=(9.5, 14.5), arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#888'))
ax.text(11.8, 15.0, 'drives', fontsize=8.5, ha='center', color='#666')

# Two legs
box(2.0, 8.0, 8.5, 2.6, 'Retrieval leg', 'embedding · 768-dim · ingest', '#eee6f7')
box(13.5, 8.0, 8.5, 2.6, 'Generation leg', '70B FP16 · serving · latency', '#dff0d8')
# split from surfaces to legs
ax.annotate('', xy=(6.25, 10.6), xytext=(18.25, 13.2), arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#888'))
ax.text(10.0, 12.1, 'split', fontsize=8, color='#666')
ax.annotate('', xy=(17.75, 10.6), xytext=(18.25, 13.2), arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#888'))
ax.text(21.4, 12.1, 'split', fontsize=8, color='#666')

# RAG system decision
box(8.0, 2.6, 8.0, 2.8, 'RAG system decision', 'base + RAG + guardrails', '#e8eef7')
ax.annotate('', xy=(10.5, 5.4), xytext=(6.25, 8.0), arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#888'))
ax.text(8.4, 6.9, 'context', fontsize=8, color='#666')
ax.annotate('', xy=(13.5, 5.4), xytext=(17.75, 8.0), arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#888'))
ax.text(15.0, 6.9, 'answer', fontsize=8, color='#666')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-05/figures/fig-05-0501.png', dpi=150)
plt.close()
print('wrote fig-05-0501')
