import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe

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

# 80 GB rank rules drawn first (zorder low) so they read as structure behind the fill.
# v9 review: the old loop used the bar's LEFT edge as x, but ax.bar() CENTRES on x,
# so each rule covered only the bar's right half plus the lane beyond it: a vertical
# white gap split the rules and the left margin had none at all (asymmetric vs the
# red 640 GB line).  axhline draws each rule full-width, exactly matching the red
# line's extent; the bars still occlude their own span (structure, not noise).
for rh in range(80, 640, 80):
    ax.axhline(rh, color=rank_color, lw=0.7, alpha=0.55, zorder=1)

base = 204   # weights 140 + runtime 64 (context-independent baseline)

for x, (label, kv) in zip(xs, ctxs):
    # v9 review: give every component a NON-colour cue (hatch) so the stack reads
    # in grayscale, and label the previously unlabelled blue/grey baseline
    # segments in-bar.  White hatch texture + a stroke halo keeps the glyphs crisp.
    ax.bar(x, 64, width=bar_w, bottom=0, color=cols['runtime'],
           edgecolor='white', linewidth=0.8, hatch='xxx', zorder=3)
    ax.bar(x, 140, width=bar_w, bottom=64, color=cols['weights'],
           edgecolor='white', linewidth=0.8, hatch='///', zorder=3)
    ax.bar(x, kv, width=bar_w, bottom=base, color=cols['kv'],
           edgecolor='white', linewidth=0.8, alpha=0.92, hatch='..', zorder=3)
    ax.text(x, 32, 'runtime ~64 GB', ha='center', va='center', fontsize=8.5,
            color='#1c1c1c', zorder=6,
            path_effects=[pe.withStroke(linewidth=2.6, foreground='white')])
    ax.text(x, 134, 'weights 140 GB', ha='center', va='center', fontsize=8.5,
            color='white', zorder=6,
            path_effects=[pe.withStroke(linewidth=2.6, foreground='#27408b')])
    total = base + kv
    # KV value as a tag just ABOVE ITS OWN bar top (bars top out at 229/288/539,
    # so the tags stagger naturally and never collide with each other or the 640 line).
    # Wording says "KV" (not a bare number) so it is not misread as the bar total.
    ax.text(x, total + 12, f'KV {kv:.1f} GB'.replace('.0 GB', ' GB'),
            ha='center', va='bottom', fontsize=10.5, color='#c0392b', fontweight='bold',
            zorder=8,
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.92))
    # context label below the bar
    ax.text(x, -40, label, ha='center', fontsize=10, fontweight='bold', zorder=8)
    ax.text(x, -80, f'= {total:.0f} GB used', ha='center', fontsize=9,
            color='#555', zorder=8)

# 640 GB capacity line (the fixed ceiling — the thing KV approaches)
ax.axhline(640, color='#a93226', lw=2.0, ls='--', zorder=5)
ax.text(0.15, 655, '640 GB = 8× 80 GB ranks', fontsize=9.5, color='#a93226',
        fontweight='bold', zorder=8)
ax.text(6.6, 690, '(light rules = 80 GB rank boundaries)', fontsize=8.2, color='#777',
        ha='right', zorder=8)

# legend swatches carry the same hatches as the bars (non-colour cue in the key too)
leg = [mpatches.Patch(facecolor=cols['kv'], edgecolor='white', lw=0.5, hatch='..',
                      label='KV cache (grows with context)'),
       mpatches.Patch(facecolor=cols['weights'], edgecolor='white', lw=0.5, hatch='///',
                      label='weights 140 GB'),
       mpatches.Patch(facecolor=cols['runtime'], edgecolor='white', lw=0.5, hatch='xxx',
                      label='runtime / NCCL ~64 GB')]
ax.legend(handles=leg, loc='lower left', bbox_to_anchor=(0.0, -0.10), fontsize=9.0,
          frameon=False, ncol=3, handlelength=1.4, columnspacing=1.2)

# one focused note (moved most of the old explanation to the figure caption in the MS)
ax.text(0.2, -150, 'The baseline (weights + runtime) is fixed; only the KV cache grows with context.\nBar heights are to scale (GB).',
        fontsize=8.4, color='#555', zorder=8)

fig.subplots_adjust(top=0.90, bottom=0.02, left=0.05, right=0.97)
plt.savefig('design/manuscript/chapter-07/figures/fig-07-0705.png', dpi=350, bbox_inches='tight', pad_inches=0.05)
import matplotlib as mpl
# v9 review: the PDF was saved WITHOUT bbox_inches='tight' while the PNG used it,
# so the legend (anchored below the axes) fell outside the canvas and was dropped
# entirely from the vector output.  Match the PNG's tight crop so both outputs
# carry the same content, with TrueType (Type 42) font embedding.
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-07/figures/fig-07-0705.pdf', format='pdf',
                bbox_inches='tight', pad_inches=0.05)
plt.close()
print('fig-07-0705 done (growth-dominant redesign; KV tag above bar)')
