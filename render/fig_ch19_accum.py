import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

# ---- fig-19-1903: Agentic Context Accumulation sequence ----
# Canonical (Ch 19): I0=9200, delta=800 retrieved, gamma=65 generated per turn.
# KV @ 2.5 MB/token (canonical architecture-dependent example): 23.8..32.4 GB.
# Each column decomposes the accumulated KV into: initial prompt (blue) +
# retrieved tool output (teal) + generated reasoning (orange) — with a legend
# so the components are distinguishable (not just colour).
fig, ax = plt.subplots(figsize=(6.8, 6.6))
ax.set_xlim(0, 14.2); ax.set_ylim(0, 10.2); ax.axis('off')

ax.text(7.1, 9.8, 'Agentic context accumulation: the KV block grows every turn',
        fontsize=10, fontweight='bold', ha='center', color='#1a1a1a')

# per-turn token decomposition (canonical example)
I0, d, g = 9200, 800, 65
cols = [
    ('Single-shot', I0, 0, 0, 23.8),
    ('Turn 1',      I0, d, g,   25.9),
    ('Turn 2',      I0, 2*d, 2*g, 28.1),
    ('Turn 3',      I0, 3*d, 3*g, 30.2),
    ('Turn 4',      I0, 4*d, 4*g, 32.4),
]
xs = [0.4, 3.0, 5.6, 8.2, 10.8]
cwd = 2.4
# scale: each of the components gets height proportional to cumulative tokens
# (canonical example uses 2.5 MB/token -> total KV = (tokens)*2.5/1000 GB).
def h_of(tok): return tok * 0.00035   # arbitrary px scale so bars stay in bounds
max_tok = I0 + 4*d + 4*g
ax.set_ylim(0, 9.4)

for label, x in zip(cols, xs):
    ax.text(x+cwd/2, 7.5, label[0], fontsize=9.5, fontweight='bold', ha='center', color='#27408b')
    y = 2.4
    # initial prompt
    h0 = h_of(I0)
    ax.add_patch(FancyBboxPatch((x, y), cwd, h0, boxstyle='round,pad=0.01', fc='#c8d8ea', ec='#27408b', lw=1, hatch='//'))
    ax.text(x+cwd/2, y+h0/2, f'I0', fontsize=7.5, ha='center', va='center', color='#27408b')
    y += h0
    if label[1]>0:
        h1 = h_of(label[1])
        ax.add_patch(FancyBboxPatch((x, y), cwd, h1, boxstyle='round,pad=0.01', fc='#7fc6b5', ec='#1a7a63', lw=1, hatch='xx'))
        ax.text(x+cwd/2, y+h1/2, f'δ', fontsize=7.5, ha='center', va='center', color='#0a4a3a')
        y += h1
    if label[2]>0:
        h2 = h_of(label[2])
        ax.add_patch(FancyBboxPatch((x, y), cwd, h2, boxstyle='round,pad=0.01', fc='#f5c98b', ec='#e67e22', lw=1, hatch='..'))
        ax.text(x+cwd/2, y+h2/2, f'γ', fontsize=7.5, ha='center', va='center', color='#8a4b08')
        y += h2
    ax.text(x+cwd/2, y+0.3, f'KV {label[3]:.1f} GB', fontsize=8.5, ha='center', fontweight='bold', color='#c0392b')

# legend (colour + pattern so grayscale-safe)
legend_comps = [
    ('initial prompt (I0)', '#c8d8ea', '//'),
    ('retrieved tool output (δ)', '#7fc6b5', 'xx'),
    ('generated reasoning (γ)', '#f5c98b', '..'),
]
ax.legend(handles=[Patch(fc=c, ec='#333', hatch=h, label=l) for l,c,h in legend_comps],
          loc='lower center', bbox_to_anchor=(0.5, 0.02), fontsize=7.6, frameon=False, ncol=3)

# short conclusion below (not in the title region)
ax.text(7.1, 1.2, 'agentic depth is a fleet-sizing problem: KV grows ~36% (23.8 → 32.4 GB)',
        fontsize=8.5, ha='center', color='#c0392b', fontweight='bold')
ax.text(7.1, 0.55, 'canonical example: KV = 2·layers·d_hidden·bytes·total-tokens @ 2.5 MB/token; total = I0 + T·δ + T·γ. [2° DERIVED, Ch19 §3]',
        fontsize=7.5, ha='center', color='#444')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-19/figures/fig-19-1903.png', dpi=150)
plt.close()
print('fig-19-1903 done')
