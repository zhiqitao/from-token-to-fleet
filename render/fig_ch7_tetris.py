import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ---- fig-07-0705: Memory Tetris — how the 8xH100 host's 640 GB fills at three contexts
# REDESIGN (publication review): make the GROWTH lesson dominant. The old figure drew
# red KV-value annotations with leader lines ONTO the bars, plus many 80 GB rank rules
# and two dense text blocks. All of that competed with the orange KV block. Now:
#   - the three stacked bars are clean (runtime / weights / growing KV);
#   - the KV size is a value tag at the TOP of each bar (outside the fill), no overlay;
#   - 80 GB rank rules are light and drawn BEHIND the bars (structure, not noise);
#   - one focused note, moved to the caption body of the figure (single line).
fig, ax = plt.subplots(figsize=(6.1, 4.6))
fig._hermes_print_sized = True
ax.set_xlim(0, 8.0); ax.set_ylim(-180, 800)
ax.axis('off')
ax.set_title('Memory Tetris: how the 8×H100 host (640 GB) fills with context',
             fontsize=11.0, fontweight='bold', pad=10)

bar_w = 2.1
ctxs = [('9.5K context', 24.9), ('32K context', 84), ('128K context', 335)]
xs = [1.6, 4.0, 6.4]
cols = {'runtime': '#95a5a6', 'weights': '#27408b', 'kv': '#e67e22'}
rank_color = '#b9c4c4'   # light rank rules, behind the bars

# 80 GB rank rules drawn first (zorder low) so they read as structure behind the fill
for x in xs:
    for rh in range(80, 640, 80):
        ax.plot([x - 0.02, x + bar_w + 0.02], [rh, rh], color=rank_color,
                lw=0.7, alpha=0.55, zorder=1)

base = 204   # weights 140 + runtime 64 (context-independent baseline)

for x, (label, kv) in zip(xs, ctxs):
    ax.bar(x, 64, width=bar_w, bottom=0, color=cols['runtime'],
           edgecolor='white', linewidth=0.8, zorder=3)
    ax.bar(x, 140, width=bar_w, bottom=64, color=cols['weights'],
           edgecolor='white', linewidth=0.8, zorder=3)
    ax.bar(x, kv, width=bar_w, bottom=base, color=cols['kv'],
           edgecolor='white', linewidth=0.8, alpha=0.92, zorder=3)
    total = base + kv
    # KV value as a tag just ABOVE ITS OWN bar top (bars top out at 229/288/539,
    # so the tags stagger naturally and never collide with each other or the 640 line)
    ax.text(x + bar_w/2, total + 12, f'{kv:.1f} GB KV'.replace('.0 GB', ' GB'),
            ha='center', va='bottom', fontsize=10.5, color='#c0392b', fontweight='bold',
            zorder=8)
    # context label below the bar
    ax.text(x + bar_w/2, -40, label, ha='center', fontsize=10, fontweight='bold', zorder=8)
    ax.text(x + bar_w/2, -80, f'= {total:.0f} GB used', ha='center', fontsize=9,
            color='#555', zorder=8)

# 640 GB capacity line (the fixed ceiling — the thing KV approaches)
ax.axhline(640, color='#a93226', lw=2.0, ls='--', zorder=5)
ax.text(0.15, 655, '640 GB = 8× 80 GB ranks', fontsize=9.5, color='#a93226',
        fontweight='bold', zorder=8)
ax.text(6.6, 690, '(light rules = 80 GB rank boundaries)', fontsize=8, color='#777',
        ha='right', zorder=8)

leg = [mpatches.Patch(color=cols['kv'], edgecolor='white', lw=0.5, label='KV cache (grows with context)'),
       mpatches.Patch(color=cols['weights'], label='weights 140 GB'),
       mpatches.Patch(color=cols['runtime'], label='runtime / NCCL ~64 GB')]
ax.legend(handles=leg, loc='lower left', bbox_to_anchor=(0.0, -0.10), fontsize=9.0,
          frameon=False, ncol=3, handlelength=1.4, columnspacing=1.2)

# one focused note (moved most of the old explanation to the figure caption in the MS)
ax.text(0.2, -150, 'The baseline (weights + runtime) is fixed; only the KV cache grows with context.',
        fontsize=8.4, color='#555', zorder=8)

fig.subplots_adjust(top=0.90, bottom=0.02, left=0.05, right=0.97)
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0705.png', dpi=150, bbox_inches='tight', pad_inches=0.05)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-07/figures/fig-07-0705.pdf', format='pdf')
plt.close()
print('fig-07-0705 done (growth-dominant redesign; KV tag above bar)')
