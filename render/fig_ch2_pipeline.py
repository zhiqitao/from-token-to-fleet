#!/usr/bin/env python3
"""fig-02-0202: CANONICAL end-to-end inference pipeline (prefill / decode).

STRUCTURAL REDESIGN (per the full-figure review) around three explicit bands:
  PREFILL rail (top)      : prompt -> embeddings -> layers -> first token
  [ PERSISTENT KV CACHE ] : an explicit reservoir; created by prefill,
                            read + extended by decode, never recomputed
  DECODE rail (bottom)    : token -> layers -> next token  (self-loop)

HOW THE TWO FLOWS ARE KEPT APART (the review's central ask):
  - STATE FLOW (orange): prefill & decode 'layers' share ONE column (XL), so
    'populate' / 'read' / 'extend' are three short verticals to/from the cache.
  - TOKEN FLOW (dark): runs along the two rails; decode iteration is a compact
    self-loop on 'next token' (no long loop-back competing for space).
  - FIRST-TOKEN FEED (dark red): drops down the right margin, runs along the
    bottom whitespace, and enters the decode 'token' box from below, touching
    nothing else.

Every rail's title above it and its description/metric below it, so the inter-rail
gaps carry ONLY the orange state arrows and their labels.  Colour carries category
(blue = model/compute, orange = KV state, grey = data); every box is sized from
measured text + an explicit padding rule.  Authored at the 6.1in column width.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

BOLD = FontProperties(weight='bold')
W = 6.1 * 72
FS  = 9.4
FSL = 8.8
FSN = 8.8
PADX = 0.30

C_AR = '#4a4a4a'; C_SEQ = '#c0392b'; C_KV = '#c06010'
C_PF = '#eaf1fb'; C_DC = '#fdf0e7'; C_KC = '#fbe3c8'
CAT = {'d': ('#e6e6e6', '#7a7a7a', '#222222'),
       'm': ('#d3e0f2', '#27408b', '#16295c'),
       'k': ('#fbe3c8', '#c06010', '#7a3410')}
KIND = {'prompt': 'd', 'embeddings': 'd', 'layers': 'm',
        'first token': 'd', 'token': 'd', 'next token': 'd'}

# ---------------- bottom-up vertical budget (bands, so nothing overlaps) -------
rg_bot = 6            # resource-regime box
rg_h   = 60
rg_c   = rg_bot + rg_h/2
rg_top = rg_bot + rg_h
feed_y = rg_top + 16              # first-token feed bottom channel
dc_meta_y = feed_y + 34           # decode metric note (below rail)
dc_desc_y = dc_meta_y + 26        # decode description (below rail)
dc_cy     = dc_desc_y + 40        # decode rail row
dc_title_y = dc_cy + 44           # decode title (above rail)
KVC_BOT  = dc_title_y + 44        # cache band (read/extend labels fill the gap)
KVC_h    = 66
KVC_TOP  = KVC_BOT + KVC_h
pf_cy     = KVC_TOP + 44          # prefill rail row (populate label fills gap)
pf_meta_y = pf_cy + 44            # prefill metric note (above rail)
pf_sub_y  = pf_meta_y + 22
pf_title_y = pf_sub_y + 22
Ht = pf_title_y + 26              # top margin

fig, ax = plt.subplots(figsize=(6.1, Ht/72))
fig._hermes_print_sized = True
ax.set_xlim(0, W); ax.set_ylim(0, Ht); ax.axis('off')


def tw(s, fs=FS):
    return TextPath((0, 0), s, size=fs, prop=BOLD).get_extents().width


def label(cx, cy, s, color='#333', fs=FSL, ha='center', weight='normal'):
    ax.text(cx, cy, s, ha=ha, va='center', fontsize=fs, color=color, fontweight=weight)


def arrow(x1, y1, x2, y2, color=C_AR, lw=1.5):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', lw=lw, color=color, shrinkA=0, shrinkB=0))


def box(cx, cy, txt):
    fill, edge, tcol = CAT[KIND[txt]]
    bw = max(tw(txt) * (1 + PADX) + 16, 78)
    ax.add_patch(FancyBboxPatch((cx-bw/2, cy-21), bw, 42,
                  boxstyle='round,pad=0.03,rounding_size=1.6', fc=fill, ec=edge,
                  lw=1.3, clip_on=False))
    ax.text(cx, cy, txt, ha='center', va='center', fontsize=FS, color=tcol,
            fontweight='bold')
    return bw


# ---------------- column centres ----------------
XL = 0.47 * W
XP = 0.115 * W
XE = 0.30 * W
XF = 0.70 * W

# ==================== PREFILL rail ====================
label(W/2, pf_title_y, 'PREFILL', '#1a3a6b', FS + 2.4, weight='bold')
label(W/2, pf_sub_y,
      'one-shot pass over the whole prompt  →  populate the cache  →  emit the first token',
      '#2a4a7a', FSL)
label(W/2, pf_meta_y, 'parallel across prompt positions    ·    measured by TTFT',
      '#2a4a7a', FSN)
pf_boxes = {}
for cx, name in [(XP, 'prompt'), (XE, 'embeddings'), (XL, 'layers'), (XF, 'first token')]:
    bw = box(cx, pf_cy, name)
    pf_boxes[name] = (cx-bw/2, cx+bw/2, pf_cy-21, pf_cy+21, cx)
pf_order = ['prompt', 'embeddings', 'layers', 'first token']
for a, b in zip(pf_order, pf_order[1:]):
    arrow(pf_boxes[a][1]+2, pf_cy, pf_boxes[b][0]-2, pf_cy, C_AR, 1.3)
ax.add_patch(FancyBboxPatch((9, pf_cy-27), W-18, 54,
              boxstyle='round,pad=0.02,rounding_size=3', fc=C_PF, ec='#b9cbe8',
              lw=1.0, alpha=0.45, clip_on=False, zorder=0))

# ==================== PERSISTENT KV CACHE ====================
kc_cx = W/2
_kc_cap = 'created by prefill   ·   read + extended by decode   ·   never recomputed'
_kc_desc = 'the accumulated key/value state of the whole conversation'
kc_w = max(TextPath((0, 0), _kc_cap, size=FSN-0.3).get_extents().width,
           TextPath((0, 0), _kc_desc, size=FSN-0.3).get_extents().width) + 70
ax.add_patch(FancyBboxPatch((kc_cx-kc_w/2, KVC_BOT), kc_w, KVC_h,
              boxstyle='round,pad=0.04,rounding_size=4', fc=C_KC, ec='#c06010',
              lw=1.8, clip_on=False, zorder=1))
label(kc_cx, KVC_TOP-14, 'PERSISTENT KV  CACHE', '#7a3410', FS, weight='bold')
label(kc_cx, KVC_TOP-34, _kc_desc, '#8a4a1a', FSN-0.3)
label(kc_cx, KVC_BOT+14, _kc_cap, '#7a3410', FSN-0.3, weight='bold')

# ==================== DECODE rail ====================
label(W/2, dc_title_y, 'DECODE', '#8a3a12', FS + 2.4, weight='bold')
label(W/2, dc_desc_y,
      'per-token loop  →  read the cache, run the layers, append new K/V',
      '#7a3410', FSL)
label(W/2, dc_meta_y, 'sequential across tokens    ·    measured by TPOT / ITL',
      '#7a3410', FSN)
dc_boxes = {}
for cx, name in [(XP, 'token'), (XL, 'layers'), (XF, 'next token')]:
    bw = box(cx, dc_cy, name)
    dc_boxes[name] = (cx-bw/2, cx+bw/2, dc_cy-21, dc_cy+21, cx)
for a, b in [('token', 'layers'), ('layers', 'next token')]:
    arrow(dc_boxes[a][1]+2, dc_cy, dc_boxes[b][0]-2, dc_cy, C_AR, 1.3)
ax.add_patch(FancyBboxPatch((9, dc_cy-27), W-18, 54,
              boxstyle='round,pad=0.02,rounding_size=3', fc=C_DC, ec='#e8c3a8',
              lw=1.0, alpha=0.45, clip_on=False, zorder=0))

# ---- compact self-loop on 'next token' (↻) ----
nt = dc_boxes['next token']
loop_cx = nt[4] + 30
ax.add_patch(Arc((loop_cx, dc_cy), 26, 22, angle=0, theta1=-60, theta2=240,
                 color=C_AR, lw=1.3))
arrow(loop_cx+12, dc_cy, loop_cx+2, dc_cy, C_AR, 1.3)

# ==================== STATE FLOW (orange, single column XL) ====================
# labels hug the cache band (KVC_BOT) so they are clear of the centred DECODE
# title, which sits in the lower part of the same corridor
pf_pop_y = (pf_boxes['layers'][2] + KVC_TOP) / 2
arrow(XL, pf_boxes['layers'][2]-2, XL, KVC_TOP-2, C_KV, 2.0)
ax.text(XL-14, pf_pop_y, 'populate', color='#7a3410',
        fontsize=FSN-0.3, fontweight='bold', ha='right', va='center')
dc_state_y = KVC_BOT - 20        # just below the cache, above the DECODE title
arrow(XL, KVC_BOT+2, XL, dc_boxes['layers'][2]-2, C_KV, 2.0)
ax.text(XL-14, dc_state_y, 'read', color='#7a3410',
        fontsize=FSN-0.3, fontweight='bold', ha='right', va='center')
ex_cx = XL + 26
arrow(ex_cx, dc_boxes['layers'][2]-2, ex_cx, KVC_BOT+2, C_KV, 2.0)
ax.text(ex_cx-14, dc_state_y, 'extend', color='#7a3410',
        fontsize=FSN-0.3, fontweight='bold', ha='right', va='center')

# ==================== FIRST-TOKEN FEED (dark red, right+bottom margins) ====================
from matplotlib.path import Path as _Path
ft = pf_boxes['first token']
tk = dc_boxes['token']
right_x = W - 20
ft_verts = [(ft[4], ft[2]), (right_x, ft[2]), (right_x, feed_y),
            (tk[4], feed_y), (tk[4], tk[2])]
ft_codes = [_Path.MOVETO, _Path.LINETO, _Path.LINETO, _Path.LINETO, _Path.LINETO]
ax.add_patch(FancyArrowPatch(path=_Path(ft_verts, ft_codes), arrowstyle='-|>',
             lw=1.7, color=C_SEQ, shrinkA=0, shrinkB=0, clip_on=False))
_feed_lab_y = (pf_cy - 21 + KVC_TOP) / 2
ax.text(right_x-8, _feed_lab_y, 'first token\nfeeds the loop', color='#8a1a1a',
        fontsize=FSN-0.3, fontweight='bold', ha='right', va='center')

# ==================== resource-regime qualification ====================
ax.add_patch(FancyBboxPatch((9, rg_c-rg_h/2), W-18, rg_h,
              boxstyle='round,pad=0.02,rounding_size=3', fc='#f7f7f7', ec='#c8c8c8',
              lw=0.9, clip_on=False, zorder=0))
label(W/2, rg_c+18, 'compute- vs bandwidth-bound is an operating-point property',
      '#222', FSL+0.2, weight='bold')
label(W/2, rg_c-4,
      'a property of the model × workload × kernel × hardware — not a fixed rule',
      '#333', FSN)
label(W/2, rg_c-26,
      'Prefill: typically higher arithmetic intensity        Decode: often bandwidth-sensitive at low batch',
      '#333', FSN)

plt.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.01)
plt.savefig('design/manuscript/chapter-02/figures/fig-02-0202.png', dpi=200)
with matplotlib.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-02/figures/fig-02-0202.pdf', format='pdf')
plt.close()
print('wrote fig-02-0202 (three-band redesign, state labels in the gaps)  Ht=%.0f' % Ht)
