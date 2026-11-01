import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Fig A.4 — Where should intelligence live? (Appendix section 7)
# Vertical stack of 8 host layers, each mapped to book chapters.
# Rewritten: axes fills the figure (no tight_layout compression), name inside box,
# chapter annotation to the right with explicit gap.

fig, ax = plt.subplots(figsize=(6.1, 7.6))
fig._hermes_print_sized = True
ax.set_position((0.0, 0.0, 1.0, 1.0))   # axes fills the figure
ax.set_xlim(0, 8.0); ax.set_ylim(0, 10.8)
ax.axis('off')

# geometry
CTITLE = 10.35
BOX_X0, BOX_W = 0.5, 5.4          # box spans x0.5 .. 5.9
NAME_X = 0.75                     # name label left inset
CH_X = 6.35                       # chapter column (clear right of box)
ARROW_X = 0.18

layers = [
    ("Across a fleet of models", "Ch18, Ch20", '#27408b', 8.8),
    ("Inside agent runtime", "Ch17-20, Ch24", '#3a6ea5', 7.8),
    ("Inside tools", "Ch19, Ch24", '#4d8fc4', 6.8),
    ("Inside test-time search", "Ch8, Ch20", '#6aa0d8', 5.8),
    ("Inside post-training", "Ch19, Ch21", '#8fb8e0', 4.8),
    ("Inside MoE routing", "Ch10", '#4c7246', 3.8),
    ("Inside attention", "Ch7, Ch8", '#6f9e5f', 2.8),
    ("Inside weights", "Ch3, Ch8", '#9ac98a', 1.8),
]
ROH = 0.84   # row height

def _text_color(hex, alpha=0.92):
    # R30 P2 (MiMo-F001): the Rec.601 "lum > 145" heuristic left WHITE ink on
    # band 3 "Inside tools" (#4d8fc4 -> 3.47:1) and band 7 "Inside attention"
    # (#6f9e5f -> 3.12:1), both under the WCAG AA 4.5:1 floor.  Pick the ink by
    # measuring real WCAG contrast against the fill AS COMPOSITED (the patch is
    # drawn at `alpha` over the white page, which lightens every band), and take
    # whichever of white / near-black scores higher.  Verified: all 8 bands then
    # clear 4.5:1 (worst = "Inside agent runtime" 4.50:1).
    r = int(hex[1:3], 16); g = int(hex[3:5], 16); b = int(hex[5:7], 16)
    r = alpha * r + (1 - alpha) * 255.0
    g = alpha * g + (1 - alpha) * 255.0
    b = alpha * b + (1 - alpha) * 255.0

    def _lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    L_bg = 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)

    def _cr(L_fg):
        hi, lo = max(L_fg, L_bg), min(L_fg, L_bg)
        return (hi + 0.05) / (lo + 0.05)

    return 'white' if _cr(1.0) >= _cr(_lin(26)) else '#1a1a1a'

ax.text(4.0, 10.5, 'Where Should Intelligence Live?', fontsize=12.5,
        fontweight='bold', ha='center', color='#1a1a1a')
ax.text(4.0, 10.05, 'The 2026 frontier question for an AI Solution Architect\n(Appendix A, "Where Should Intelligence Live?")',
        fontsize=8.6, ha='center', color='#555', style='italic')

# upward arrow in the left margin (scope of placement, not superiority)
ax.annotate('', xy=(ARROW_X, 9.1), xytext=(ARROW_X, 1.5),
            arrowprops=dict(arrowstyle='-|>', lw=2.3, color='#c0392b'))

for i, (name, ch, color, y) in enumerate(layers):
    box = FancyBboxPatch((BOX_X0, y - ROH / 2), BOX_W, ROH,
                         boxstyle='round,pad=0.02', fc=color, ec='none', alpha=0.92)
    ax.add_patch(box)
    ax.text(NAME_X, y, name, fontsize=8.4, fontweight='bold', color=_text_color(color),
            va='center', ha='left')
    ax.text(CH_X, y, ch, fontsize=8.0, color='#333', va='center', ha='left')

# horizontalized scope annotation (vertical axis = WHERE, not BETTER) — two centered lines so it fits
ax.text(4.0, 1.25, 'scope of placement: intelligence shifts up out of the weights',
        fontsize=8.0, color='#c0392b', ha='center', va='center')
ax.text(4.0, 0.90, '(vertical axis = WHERE it lives: nonexclusive placement choices, not a ranking)',
        fontsize=8.0, color='#c0392b', ha='center', va='center')

ax.text(4.0, 0.35, 'Model intelligence \u2260 system intelligence', fontsize=9.2,
        fontweight='bold', ha='center', color='#c0392b',
        bbox=dict(boxstyle='round,pad=0.35', fc='#fdecea', ec='#c0392b'))

out = 'design/manuscript/chapter-27/figures/fig-27-2702.png'
plt.savefig(out, dpi=350)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-27/figures/fig-27-2702.pdf')
print('wrote', out)
