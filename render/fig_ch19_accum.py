import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

# ---- fig-19-1903: Agentic Context Accumulation sequence ----
# Canonical (Ch 19): I0=9200, delta=800 retrieved, gamma=65 generated per turn.
# KV @ 2.5 MB/token: 23.8..32.4 GB.
I0, d, g = 9200, 800, 65
# clear-named column data: label, delta, gamma, kv_gb
cols = [
    ('Single-shot', 0,   0,   23.8),
    ('Turn 1',     d,   g,   25.9),
    ('Turn 2',     2*d, 2*g, 28.1),
    ('Turn 3',     3*d, 3*g, 30.2),
    ('Turn 4',     4*d, 4*g, 32.4),
]
xs = [0.4, 3.0, 5.6, 8.2, 10.8]
cwd = 2.4
def h_of(tok): return tok * 0.00035

fig, ax = plt.subplots(figsize=(5.4, 5.6))
ax.set_xlim(0, 14.2); ax.set_ylim(0, 10.2); ax.axis('off')
ax.text(7.1, 9.8, 'Agentic context accumulation: the KV block grows every turn',
        fontsize=10, fontweight='bold', ha='center', color='#1a1a1a')

for (name, dl, gm, kv), x in zip(cols, xs):
    ax.text(x+cwd/2, 7.6, name, fontsize=10, fontweight='bold', ha='center', color='#27408b')
    y = 2.4
    # initial prompt (blue, constant)
    h0 = h_of(I0)
    ax.add_patch(FancyBboxPatch((x, y), cwd, h0, boxstyle='round,pad=0.01',
                                fc='#c8d8ea', ec='#27408b', lw=1, hatch='//'))
    ax.text(x+cwd/2, y+h0/2, 'I0', fontsize=9, ha='center', va='center', color='#27408b')
    y += h0
    # retrieved tool output (teal, grows with turns)
    if dl > 0:
        h1 = h_of(dl)
        ax.add_patch(FancyBboxPatch((x, y), cwd, h1, boxstyle='round,pad=0.01',
                                    fc='#7fc6b5', ec='#1a7a63', lw=1, hatch='xx'))
        ax.text(x+cwd/2, y+h1/2, '\u03b4', fontsize=9, ha='center', va='center', color='#0a4a3a')
        y += h1
    # generated reasoning (orange, grows with turns)
    if gm > 0:
        h2 = h_of(gm)
        ax.add_patch(FancyBboxPatch((x, y), cwd, h2, boxstyle='round,pad=0.01',
                                    fc='#f5c98b', ec='#e67e22', lw=1, hatch='..'))
        ax.text(x+cwd/2, y+h2/2, '\u03b3', fontsize=9, ha='center', va='center', color='#8a4b08')
        y += h2
    ax.text(x+cwd/2, y+0.3, f'KV {kv:.1f} GB', fontsize=9.5, ha='center',
            fontweight='bold', color='#c0392b')

# legend (colour + pattern so grayscale-safe)
legend_comps = [
    ('initial prompt (I0)', '#c8d8ea', '//'),
    ('retrieved tool output (\u03b4)', '#7fc6b5', 'xx'),
    ('generated reasoning (\u03b3)', '#f5c98b', '..'),
]
ax.legend(handles=[Patch(fc=c, ec='#333', hatch=h, label=l) for l, c, h in legend_comps],
          loc='lower center', bbox_to_anchor=(0.5, 0.02), fontsize=9, frameon=False, ncol=3)

# short conclusion below (not in the title region)
ax.text(7.1, 1.2, 'agentic depth is a fleet-sizing problem: KV grows ~36% (23.8 \u2192 32.4 GB)',
        fontsize=8.5, ha='center', color='#c0392b', fontweight='bold')
ax.text(7.1, 0.55, 'canonical example @ 2.5 MB/token; total = I0 + T\u00b7\u03b4 + T\u00b7\u03b3. [2\u00b0 DERIVED]',
        fontsize=9, ha='center', color='#444')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-19/figures/fig-19-1903.png',
            dpi=200, bbox_inches='tight', pad_inches=0.08)
plt.close()
print('fig-19-1903 fixed (clear field indices)')
