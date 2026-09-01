import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ---- fig-19-1903: Agentic Context Accumulation sequence ----
# Canonical (Ch 19): I0=9200, delta=800 retrieved, gamma=65 generated per turn.
# KV @ 2.5 MB/token: single-shot 23.8 GB; with turns 25.9, 28.1, 30.2, 32.4 GB (cumulative).
fig, ax = plt.subplots(figsize=(12, 6.4))
ax.set_xlim(0, 24); ax.set_ylim(0, 8); ax.axis('off')

ax.text(12, 7.7, 'Agentic context accumulation: the KV block grows every turn', fontsize=13, fontweight='bold', ha='center', color='#1a1a1a')
ax.text(12, 7.3, 'each turn appends retrieved context (δ=800 tok) + generated reasoning (γ=65 tok); tokens persist across all later turns', fontsize=8.5, ha='center', color='#555')

# columns per turn: turn 0 (baseline), 1, 2, 3, 4 -> 5 columns
cols = [
    ('Single-shot',   9200, 23.8, '(no tool)'),
    ('Turn 1',        9200+865, 25.9, '+tool out 1'),
    ('Turn 2',        9200+2*865, 28.1, '+tool out 2'),
    ('Turn 3',        9200+3*865, 30.2, '+tool out 3'),
    ('Turn 4',        9200+4*865, 32.4, '+tool out 4'),
]
xs = [1.5, 6.0, 10.5, 15.0, 19.5]

# cumulative KV footprint scaled to show growth (23.8->32.4 as bar heights on a 34 GB axis)
for (label, toks, kv, note), x in zip(cols, xs):
    # column title
    ax.text(x+1.4, 6.4, label, fontsize=11, fontweight='bold', ha='center', color='#27408b')
    # context stack: initial prompt (grey) fixed height + added per turn (orange)
    base_h = 2.0  # initial prompt
    add_h = (kv - 23.8) * 0.20  # growth scaled to keep all blocks on the 0-8 axis (max ~1.7)
    # initial prompt block
    ax.add_patch(FancyBboxPatch((x, 1.9), 2.8, base_h, boxstyle='round,pad=0.01', fc='#c8d8ea', ec='#27408b', lw=1))
    ax.annotate('', xy=(x+1.4, 1.45), xytext=(x+1.4, 1.9), arrowprops=dict(arrowstyle='-|>', lw=1.2, color='#27408b'))
    ax.text(x+1.4, 2.75, 'initial prompt', fontsize=7.5, ha='center', color='#27408b')
    ax.text(x+1.4, 2.2, '9.2K tok', fontsize=7, ha='center', color='#27408b')
    # accumulated tool context (top, orange) - only for turns>0
    if add_h > 0:
        ax.add_patch(FancyBboxPatch((x, 1.9+base_h), 2.8, add_h, boxstyle='round,pad=0.01', fc='#f5c98b', ec='#e67e22', lw=1))
        ax.text(x+1.4, 1.9+base_h+add_h/2, note, fontsize=7.5, ha='center', va='center', color='#8a4b08')
    # KV footprint label above
    ax.text(x+1.4, 1.9+base_h+add_h+0.35, f'KV {kv:.1f} GB', fontsize=9, ha='center', fontweight='bold', color='#c0392b')
    # token count under
    ax.text(x+1.4, 1.1, f'{toks/1000:.1f}K tok', fontsize=8, ha='center', color='#555')

# cumulative footprint arrow across turns
ax.annotate('', xy=(20.9, 6.8), xytext=(2.9, 6.8), arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#c0392b'))
ax.text(12, 7.0, 'KV footprint grows ~36% (23.8 → 32.4 GB) — agentic depth is a fleet-sizing problem', fontsize=9, ha='center', color='#c0392b', fontweight='bold')

ax.text(12, 0.2, 'KV = 2 × n_layers × d_hidden × bytes/token × total-tokens  (2.5 MB/token FP16);  total tokens = I₀ + T·δ + T·γ.  [2° DERIVED, Ch19 §3]',
        fontsize=7.5, ha='center', color='#444')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-19/figures/fig-19-1903.png', dpi=150)
plt.close()
print('fig-19-1903 done')
