import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.font_manager import FontProperties

# ---- fig-05-0501: Model selection for RAG [ILLUSTRATIVE conceptual] ----
# workload -> five selection surfaces -> two legs (retrieval/generation) -> RAG decision.
# Re-authored at the 6.1in print column so fonts stay at native size on placement.
# Centred vertical flow, laid out with explicit bottoms so the inter-row gaps are real.
FS = 10.0
W = 6.1 * 72      # 439 pt
MID = W/2

fig, ax = plt.subplots(figsize=(6.1, 6.6))
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow
ax.set_xlim(0, W); ax.set_ylim(0, 6.6*72); ax.axis('off')

def box(cx, y, w, h, head, sub, fc, head_fs=FS, sub_fs=FS-1.8):
    ax.add_patch(FancyBboxPatch((cx-w/2, y), w, h, boxstyle='round,pad=0.10', fc=fc, ec='#888', lw=1.1, alpha=0.92))
    ax.text(cx, y+h*0.62, head, ha='center', va='center', fontsize=head_fs, fontweight='bold', color='#222')
    ax.text(cx, y+h*0.16, sub, ha='center', va='center', fontsize=sub_fs, color='#333')

BOX_H = 56
GAP   = 58
BOT   = 24          # decision box bottom
# explicit bottoms, bottom-up
dec_bot = BOT
leg_bot = dec_bot + BOX_H + GAP
sur_bot = leg_bot + BOX_H + GAP
wor_bot = sur_bot + BOX_H + GAP
Ht = wor_bot + BOX_H + 26
ax.set_ylim(0, Ht)
print("Ht =", round(Ht,1))

WBOX = 300
# row 1: workload
box(MID, wor_bot, WBOX, BOX_H, 'Workload characterization', 'tokens · cost · SLO', '#dff0d8')
# row 2: five selection surfaces (parent)
box(MID, sur_bot, 330, BOX_H, 'Five selection surfaces', 'quality · latency · KV · $/tok', '#fde3e0')
ax.annotate('', xy=(MID, sur_bot+BOX_H), xytext=(MID, wor_bot),
            arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#888'))
ax.text(MID+12, (wor_bot+sur_bot+BOX_H)/2, 'drives', fontsize=FS-1.5, color='#666', ha='left')

# two legs, common baseline, symmetric about the page centre
LEG_W = 165
LEG_GAP = 18
lg1_cx = MID - LEG_W/2 - LEG_GAP/2
lg2_cx = MID + LEG_W/2 + LEG_GAP/2
for (cx, head, sub, fc) in [(lg1_cx,'Retrieval leg','embedding · 768-dim','#eee6f7'),
                            (lg2_cx,'Generation leg','70B FP16 · serving','#dff0d8')]:
    box(cx, leg_bot, LEG_W, BOX_H, head, sub, fc)
    ax.annotate('', xy=(cx, leg_bot+BOX_H), xytext=(MID, sur_bot),
                arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#888'))
    ax.text((MID+cx)/2, (sur_bot+leg_bot+BOX_H)/2, 'split', fontsize=FS-1.5, color='#666', ha='center')

# RAG system decision (centred)
box(MID, dec_bot, 300, BOX_H, 'RAG system decision', 'base + RAG + guardrails', '#e8eef7')
# context/answer feeds land at DISTINCT points on the decision box top edge — the
# retrieval feed registers at the LEFT third, the generation feed at the RIGHT third,
# so the two arrows do not converge onto one point.
for (cx, lab, land_x) in [(lg1_cx,'context', MID-55), (lg2_cx,'answer', MID+55)]:
    ax.annotate('', xy=(land_x, dec_bot+BOX_H), xytext=(cx, leg_bot),
                arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#888'))
    ax.text((cx+land_x)/2, (leg_bot+dec_bot+BOX_H)/2 - 4, lab, fontsize=FS-1.5, color='#666', ha='center')

plt.tight_layout(pad=0.2)
plt.savefig('design/manuscript/chapter-05/figures/fig-05-0501.png', dpi=150)
import matplotlib as mpl
with mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-05/figures/fig-05-0501.pdf', format='pdf')
plt.close()
print('wrote fig-05-0501 (6.1in, explicit bottoms, real gaps)')
