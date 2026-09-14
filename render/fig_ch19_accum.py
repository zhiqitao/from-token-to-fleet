import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ---- fig-19-1903: Agentic Context Accumulation sequence ----
# Canonical (Ch 19): I0=9200, delta=800 retrieved, gamma=65 generated per turn.
# KV @ 2.5 MB/token: single-shot 23.8 GB; with turns 25.9, 28.1, 30.2, 32.4 GB (cumulative).
# Compact narrow layout (5 columns, wrapped long text) so it places at column width.
fig, ax = plt.subplots(figsize=(6.0, 5.6))
ax.set_xlim(0, 13.8); ax.set_ylim(0, 9); ax.axis('off')

ax.text(6.9, 8.5, 'Agentic context accumulation: the KV block grows every turn', fontsize=9.5, fontweight='bold', ha='center', color='#1a1a1a')
ax.text(6.9, 8.0, 'each turn appends retrieved context (δ=800 tok) +\ngenerated reasoning (γ=65 tok); tokens persist', fontsize=7.5, ha='center', color='#555')

# columns per turn: turn 0 (baseline), 1, 2, 3, 4 -> 5 columns
cols = [
    ('Single-shot',   9200, 23.8, '(no tool)'),
    ('Turn 1',        9200+865, 25.9, '+tool 1'),
    ('Turn 2',        9200+2*865, 28.1, '+tool 2'),
    ('Turn 3',        9200+3*865, 30.2, '+tool 3'),
    ('Turn 4',        9200+4*865, 32.4, '+tool 4'),
]
xs = [0.4, 3.0, 5.6, 8.2, 10.8]
cwd = 2.4

# cumulative KV footprint scaled to show growth (23.8->32.4 as bar heights on a 34 GB axis)
for (label, toks, kv, note), x in zip(cols, xs):
    ax.text(x+cwd/2, 6.6, label, fontsize=9.5, fontweight='bold', ha='center', color='#27408b')
    base_h = 2.0
    add_h = (kv - 23.8) * 0.20
    ax.add_patch(FancyBboxPatch((x, 2.0), cwd, base_h, boxstyle='round,pad=0.01', fc='#c8d8ea', ec='#27408b', lw=1))
    ax.annotate('', xy=(x+cwd/2, 1.55), xytext=(x+cwd/2, 2.0), arrowprops=dict(arrowstyle='-|>', lw=1.2, color='#27408b'))
    ax.text(x+cwd/2, 2.85, 'initial prompt', fontsize=7, ha='center', color='#27408b')
    ax.text(x+cwd/2, 2.35, '9.2K tok', fontsize=6.5, ha='center', color='#27408b')
    if add_h > 0:
        ax.add_patch(FancyBboxPatch((x, 2.0+base_h), cwd, add_h, boxstyle='round,pad=0.01', fc='#f5c98b', ec='#e67e22', lw=1))
        ax.text(x+cwd/2, 2.0+base_h+add_h/2, note, fontsize=7, ha='center', va='center', color='#8a4b08')
    ax.text(x+cwd/2, 2.0+base_h+add_h+0.3, f'KV {kv:.1f} GB', fontsize=8, ha='center', fontweight='bold', color='#c0392b')
    ax.text(x+cwd/2, 1.25, f'{toks/1000:.1f}K tok', fontsize=7, ha='center', color='#555')

ax.annotate('', xy=(10.8, 7.2), xytext=(0.4, 7.2), arrowprops=dict(arrowstyle='-|>', lw=1.5, color='#c0392b'))
ax.text(6.9, 7.5, 'KV footprint grows ~36% (23.8 → 32.4 GB):\nagentic depth is a fleet-sizing problem', fontsize=8, ha='center', color='#c0392b', fontweight='bold')

ax.text(6.9, 0.4, 'KV = 2 × n_layers × d_hidden × bytes/token × total-tokens (2.5 MB/token FP16);\ntotal tokens = I₀ + T·δ + T·γ.  [2° DERIVED, Ch19 §3]',
        fontsize=6.8, ha='center', color='#444')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-19/figures/fig-19-1903.png', dpi=150)
plt.close()
print('fig-19-1903 done')
