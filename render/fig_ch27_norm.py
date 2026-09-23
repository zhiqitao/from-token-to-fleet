import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-27-2704: vendor-reported KV/token and FLOP/token reductions ----
# Each percentage is a model's vendor-reported ratio of its OWN stated reference
# (e.g. DeepSeek V4 vs V3.2), so there is NO shared cross-model baseline.
# PASS-2 redesign: instead of three bar panels (whose identical bar grammar invites
# an invalid height comparison), render three independent BEFORE -> AFTER cards, each
# naming its OWN baseline explicitly. Removing the shared-bar grammar is itself the fix.
cards = [
    {"name": "DeepSeek V4-Flash", "ref": "vs V3.2", "kv": 7,  "flop": 10, "arv": "2606.19348"},
    {"name": "DeepSeek V4-Pro",   "ref": "vs V3.2", "kv": 10, "flop": 27, "arv": "2606.19348"},
    {"name": "GLM-5.3-Flash",     "ref": "vs stated ref", "kv": 23, "flop": 33, "arv": "HF zai-org"},
]

fig, ax = plt.subplots(figsize=(6.1, 4.4))
fig._hermes_print_sized = True
ax.set_xlim(0, 20); ax.set_ylim(0, 11.6); ax.axis('off')

# title
ax.text(10, 11.3, 'Vendor-reported KV / FLOP reduction', fontsize=11.5, fontweight='bold', ha='center', color='#1a1a1a')
ax.text(10, 10.75, 'EACH PANEL IS A DIFFERENT BASELINE — NOT A SHARED SCALE. Do not compare cards.', fontsize=9,
        ha='center', color='#c0392b', fontweight='bold')

cols = ['#c0392b', '#3a6ea5', '#6f9e5f']
card_x = [0.4, 7.0, 13.6]
card_w = 6.0
for (c, cx, col) in zip(cards, card_x, cols):
    ax.add_patch(FancyBboxPatch((cx, 3.0), card_w, 6.6, boxstyle='round,pad=0.05,rounding_size=0.25',
                                fc='#f8f9fb', ec=col, lw=1.8))
    ax.text(cx + card_w/2, 9.0, c['name'], fontsize=10, fontweight='bold', ha='center', color=col)
    ax.text(cx + card_w/2, 8.45, c['ref'], fontsize=8.2, ha='center', color='#555', style='italic')
    # KV before -> after
    ax.text(cx + 1.6, 6.6, 'KV/token', fontsize=8.2, color='#444', ha='center')
    ax.text(cx + 1.6, 6.0, '100%', fontsize=10, fontweight='bold', color='#555', ha='center')
    ax.add_patch(FancyArrowPatch((cx + 1.6, 5.6), (cx + 4.4, 5.6), arrowstyle='-|>',
                                 mutation_scale=16, lw=2.4, color=col))
    ax.text(cx + 4.4, 6.0, '~%d%%' % c['kv'], fontsize=11, fontweight='bold', color=col, ha='center')
    # FLOP before -> after
    ax.text(cx + 1.6, 4.5, 'FLOP/token', fontsize=8.2, color='#444', ha='center')
    ax.text(cx + 1.6, 3.9, '100%', fontsize=10, fontweight='bold', color='#555', ha='center')
    ax.add_patch(FancyArrowPatch((cx + 1.6, 3.5), (cx + 4.4, 3.5), arrowstyle='-|>',
                                 mutation_scale=16, lw=2.4, color=col))
    ax.text(cx + 4.4, 3.9, '~%d%%' % c['flop'], fontsize=11, fontweight='bold', color=col, ha='center')

# footnote
ax.text(10, 1.7, 'Each reduction is relative to the model\'s OWN stated predecessor — there is no common denominator, '
                 'so the percentages must not be read against a single baseline.', fontsize=8.2, ha='center', color='#555')
ax.text(10, 0.9, 'Value source: vendor-reported [1P] (arXiv 2606.19348; HF zai-org), not yet independently reprofiled.',
        fontsize=7.8, ha='center', color='#777', style='italic')

plt.savefig('design/manuscript/chapter-27/figures/fig-27-2704.png', dpi=200, bbox_inches='tight', pad_inches=0.08)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-27/figures/fig-27-2704.pdf', format='pdf', bbox_inches='tight')
plt.close()
print('wrote fig-27-2704 (independent before->after cards, each with its own baseline)')
