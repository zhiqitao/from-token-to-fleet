import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.font_manager import FontProperties
import textwrap

# ---- fig-05-0501: Model selection for RAG [ILLUSTRATIVE conceptual] ----
# workload -> five selection surfaces -> two legs (retrieval/generation) -> RAG decision.
# Re-authored at the 6.1in print column so fonts stay at native size on placement.
# Centred vertical flow, laid out with explicit bottoms so the inter-row gaps are real.
#
# v2 fix (figure display review): the previous version's boxes were narrower than
# their text, so the "Five selection surfaces" subtitle overflowed both borders and
# the "Workload characterization" title ran flush to its edges. Now each box wraps
# its head/subtitle to fit the box width, subtitles use a darker shade for contrast,
# and every connector carries a clear arrowhead.
FS = 10.0
W = 6.1 * 72      # 439 pt
MID = W/2

fig, ax = plt.subplots(figsize=(6.1, 6.6))
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow
ax.set_xlim(0, W); ax.set_ylim(0, 6.6*72); ax.axis('off')

def edge_label(x, y, txt, fs=FS-1.5):
    ax.text(x, y, txt, fontsize=fs, color='#555', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.14', fc='white', ec='none', alpha=0.9))

def box(cx, y, w, h, head, sub, fc, head_fs=FS, sub_fs=FS-1.6):
    """Draw a box whose two text lines are wrapped to fit width w, and whose
    bottom is at y. Text is drawn inside the padded interior so no glyph
    crosses the border."""
    pad = 6          # interior padding in pt, keeps text off the border
    ax.add_patch(FancyBboxPatch((cx-w/2, y), w, h, boxstyle='round,pad=0.10',
                                fc=fc, ec='#8a8a8a', lw=1.2, alpha=0.95))
    inner_w = w - 2*pad
    head_l = textwrap.wrap(head, width=int(inner_w/(head_fs*0.52))) or [head]
    sub_l  = textwrap.wrap(sub,  width=int(inner_w/(sub_fs*0.52))) or [sub]
    # place the head (1-2 lines) in the upper half, subtitle below it
    n = len(head_l) + len(sub_l)
    if n == 1:
        lines = head_l
    else:
        y_top = y + h*0.70
        y_sub = y + h*(0.70 * (1 - (len(head_l)+0.0)/n)) - 4
        # fallback: simple two-block vertical split
        y_top = y + h*0.72
        y_sub = y + h*0.26
    for i, ln in enumerate(head_l):
        ax.text(cx, y + h*(0.74 - 0.10*i), ln, ha='center', va='center',
                fontsize=head_fs, fontweight='bold', color='#1a1a1a')
    for i, ln in enumerate(sub_l):
        ax.text(cx, y + h*(0.30 - 0.10*i), ln, ha='center', va='center',
                fontsize=sub_fs, color='#3a3a3a')
    return len(head_l), len(sub_l)

def arrow(x0, y0, x1, y1, lw=1.7):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='-|>', lw=lw, color='#6a6a6a',
                                mutation_scale=14, shrinkA=0, shrinkB=0))

BOX_H = 62
GAP   = 58
BOT   = 24          # decision box bottom
# explicit bottoms, bottom-up
dec_bot = BOT
leg_bot = dec_bot + BOX_H + GAP
sur_bot = leg_bot + BOX_H + GAP
wor_bot = sur_bot + BOX_H + GAP
Ht = wor_bot + BOX_H + 26
ax.set_ylim(0, Ht)

WBOX = 330
# row 1: workload
box(MID, wor_bot, WBOX, BOX_H, 'Workload characterization', 'tokens · cost · SLO', '#dff0d8')
# row 2: five selection surfaces (parent) -- wrap the long subtitle over two lines
box(MID, sur_bot, 392, BOX_H, 'Five selection surfaces',
    'quality · latency · KV · $/tok · retrieve-vs-generate', '#fde3e0', sub_fs=8.0)
arrow(MID, wor_bot, MID, sur_bot+BOX_H)
edge_label(MID+20, (wor_bot+sur_bot+BOX_H)/2, 'drives')

# two legs, common baseline, symmetric about the page centre
LEG_W = 175
LEG_GAP = 26
lg1_cx = MID - LEG_W/2 - LEG_GAP/2
lg2_cx = MID + LEG_W/2 + LEG_GAP/2
for (cx, head, sub, fc) in [(lg1_cx,'Retrieval leg','embedding · 768-dim','#eee6f7'),
                            (lg2_cx,'Generation leg','70B FP16 · serving','#dff0d8')]:
    box(cx, leg_bot, LEG_W, BOX_H, head, sub, fc)
    arrow(MID, sur_bot, cx, leg_bot+BOX_H)
    edge_label((MID+cx)/2, (sur_bot+leg_bot+BOX_H)/2 - 4, 'split')

# RAG system decision (centred)
box(MID, dec_bot, WBOX, BOX_H, 'RAG system decision', 'base + RAG + guardrails', '#e8eef7')
# context/answer feeds land at DISTINCT points on the decision box top edge.
for (cx, lab, land_x) in [(lg1_cx,'context', MID-58), (lg2_cx,'answer', MID+58)]:
    arrow(cx, leg_bot, land_x, dec_bot+BOX_H)
    edge_label((cx+land_x)/2, (leg_bot+dec_bot+BOX_H)/2 - 6, lab)

plt.tight_layout(pad=0.2)
plt.savefig('design/manuscript/chapter-05/figures/fig-05-0501.png', dpi=350)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-05/figures/fig-05-0501.pdf', format='pdf')
plt.close()
print('wrote fig-05-0501 (v2: wrapped text, box-fit, clear arrowheads)')
