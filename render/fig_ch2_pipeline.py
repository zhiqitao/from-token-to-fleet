#!/usr/bin/env python3
"""fig-02-0202: CANONICAL end-to-end inference pipeline (prefill / decode).

REDESIGNED for PASS-23b. Two vertically-separated bands (PREFILL, DECODE).
Each band: a compact horizontal row of text-sized boxes with a dominant
left->right causal flow, a receded secondary-observation line beneath it, and
an explicit orange KV conduit linking the prefill-created KV to the decode
reuse. A separate bottom band carries qualified resource-regime language,
and a final strip carries the visual-grammar legend.

Layout is computed from box counts + measured text width, and the row is
uniformly scaled so boxes AND text shrink together (text always fits, nothing
clips or merges). 1 data unit == 1 point. Author at the 6.1in column width.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

BOLD = FontProperties(weight='bold')
FS = 9.4
W = 6.1 * 72                    # 439.2 pt column width
Ht = 8.4 * 72
PADX = 0.30

def tw(s, fs=FS):
    return TextPath((0, 0), s, size=fs, prop=BOLD).get_extents().width

def note_w(s, fs=FS-0.6):
    return TextPath((0, 0), s, size=fs).get_extents().width

fig, ax = plt.subplots(figsize=(6.1, 7.6))
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow
ax.set_xlim(0, W); ax.set_ylim(0, Ht); ax.axis('off')

C_MODEL='#27408b'; C_DATA='#7a7a7a'; C_KV='#e67e22'; C_SEQ='#c0392b'
C_AR='#555555'; C_PF='#eaf1fb'; C_DC='#fdf0e7'

def label(cx, cy, text, color='#444', fs=FS-0.3, ha='center', weight='normal', style='normal'):
    ax.text(cx, cy, text, ha=ha, va='center', fontsize=fs, color=color,
            fontweight=weight, style=style)

def arrow(x1,y1,x2,y2,color=C_AR,lw=1.4,style='-|>'):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                arrowprops=dict(arrowstyle=style,lw=lw,color=color,shrinkA=0,shrinkB=0))

BOX_H = 40

def draw_lane(cy, steps, boxh=BOX_H):
    """Draw a compact row of text-sized boxes, left->right, uniformly scaled so
    text always fits inside. Uses LIGHT fills + dark text (legible at book print
    and in grayscale). Returns box (x0,x1,y0,y1) list."""
    avail = W - 24
    widths = [max(tw(s)*(1+PADX)+14, 70) for (s,c) in steps]
    gap = 18
    tot = sum(widths) + (len(steps)-1)*gap
    k = 1.0
    if tot > avail:
        k = avail/tot
    # light fills so dark text is legible at print scale and in grayscale
    FILL = {C_DATA:'#e0e0e0', C_MODEL:'#d3e0f2', C_KV:'#fbe3c8'}
    EDGE = {C_DATA:'#888888', C_MODEL:'#27408b', C_KV:'#c06010'}
    TXT  = {C_DATA:'#222222', C_MODEL:'#16295c', C_KV:'#8a3a12'}
    boxes = []
    x = (W - (sum(widths)*k + (len(steps)-1)*gap*k))/2
    for (s,c), wd in zip(steps, widths):
        bw = wd*k
        cx = x+bw/2
        fsize = FS*k*1.1
        ax.add_patch(FancyBboxPatch((cx-bw/2, cy-boxh/2), bw, boxh,
                      boxstyle='round,pad=0.02,rounding_size=1.4', fc=FILL[c], ec=EDGE[c], lw=1.2, clip_on=False))
        ax.text(cx, cy, s, ha='center', va='center', fontsize=fsize,
                color=TXT[c], fontweight='bold')
        boxes.append((cx-bw/2, cx+bw/2, cy-boxh/2, cy+boxh/2))
        x += bw + gap*k
    for i in range(len(steps)-1):
        arrow(boxes[i][1]+2, cy, boxes[i+1][0]-2, cy, C_AR, 1.2)
    return boxes, k

# ===== PREFILL band =====
pf_title_y = Ht - 30
label(W/2, pf_title_y, 'PREFILL', '#1a3a6b', FS+2.0, weight='bold')
label(W/2, pf_title_y-20, 'process the whole prompt, populate the KV cache, emit the first token',
      '#4a6a9a', FS-0.7)
pf_cy = pf_title_y - 74
pf_steps = [
    ('prompt', C_DATA),
    ('embeddings', C_DATA),
    ('layers', C_MODEL),
    ('make K/V', C_KV),
    ('sample token', C_DATA),
]
pf_boxes, k = draw_lane(pf_cy, pf_steps)
pf_top_edge = pf_cy + BOX_H/2 + 6
pf_bot_edge = pf_cy - BOX_H/2 - 6
ax.add_patch(FancyBboxPatch((9, pf_bot_edge-6), W-18, (pf_top_edge-(pf_bot_edge-6)),
              boxstyle='round,pad=0.02,rounding_size=3', fc=C_PF, ec='#b9cbe8', lw=1.0,
              alpha=0.40, clip_on=False, zorder=0))
obs_pf_y = pf_bot_edge - 6 - 18
label(W/2, obs_pf_y, 'one-shot burst — parallel across prompt positions; measured by TTFT',
      '#6a7a9a', FS-1.1)
kv_idx = 3
kv_cx = (pf_boxes[kv_idx][0]+pf_boxes[kv_idx][1])/2
kv_top = pf_cy + BOX_H/2

# ===== DECODE band =====
dc_title_y = obs_pf_y - 70
label(W/2, dc_title_y, 'DECODE', '#8a3a12', FS+2.0, weight='bold')
label(W/2, dc_title_y-20, 'generate one token at a time, reusing the cached K/V',
      '#a06a3a', FS-0.7)
dc_cy = dc_title_y - 74
dc_steps = [
    ('token', C_DATA),
    ('reuse K/V', C_KV),
    ('layers', C_MODEL),
    ('append K/V', C_KV),
    ('next token', C_DATA),
]
dc_boxes, k2 = draw_lane(dc_cy, dc_steps)
dc_top_edge = dc_cy + BOX_H/2 + 6
dc_bot_edge = dc_cy - BOX_H/2 - 6
ax.add_patch(FancyBboxPatch((9, dc_bot_edge-6), W-18, (dc_top_edge-(dc_bot_edge-6)),
              boxstyle='round,pad=0.02,rounding_size=3', fc=C_DC, ec='#e8c3a8', lw=1.0,
              alpha=0.40, clip_on=False, zorder=0))
obs_dc_y = dc_bot_edge - 6 - 18
label(W/2, obs_dc_y, 'sequential loop — one token per step, reuses + appends K/V; measured by TPOT / ITL',
      '#b08a6a', FS-1.1)
reuse_idx = 1
reuse_cx = (dc_boxes[reuse_idx][0]+dc_boxes[reuse_idx][1])/2

# ---- explicit orange KV conduit: a straight dashed connector placed strictly
#      IN the inter-band whitespace (between the prefill caption and the decode
#      title), at the far left, clear of every box/title. No arrowhead into a
#      box (avoids collision); the orange KV boxes + caption carry create/reuse. ----
rail_x = 18
rail_y0 = obs_pf_y - 4        # just below the prefill caption
rail_y1 = dc_title_y + 4      # just above the decode title
ax.add_patch(FancyArrowPatch((rail_x, rail_y0), (rail_x, rail_y1),
              connectionstyle='arc3,rad=0.0', arrowstyle='-', color=C_KV, lw=2.8, ls='--', clip_on=False))
# KV caption in the far-RIGHT whitespace between the bands (opposite the rail)
label(W-116, (rail_y0+rail_y1)/2, 'KV cache: created in prefill,\nreused (not recomputed) in decode',
      '#8a3a12', FS-1.1, weight='bold')

# ---- first-token connector: prefill output -> decode entry ----
arrow(pf_boxes[-1][1]+4, pf_cy, pf_boxes[-1][1]+4, dc_title_y+22, C_AR, 1.5)
label(pf_boxes[-1][1]+8, (pf_cy+dc_title_y+22)/2, 'first token', '#555', FS-1.0, ha='left')

# ===== bottom resource-regime band (own clear space) =====
strip_y = obs_dc_y - 72
ax.add_patch(FancyBboxPatch((9, strip_y-30), W-18, 82,
              boxstyle='round,pad=0.02,rounding_size=3', fc='#f4f4f4', ec='#cccccc', lw=0.8,
              clip_on=False))
label(W/2, strip_y+26, 'resource regime', '#444', FS-0.4, weight='bold')
label(W/2, strip_y+6, 'a property of the model × workload × kernel × hardware, not a fixed rule',
      '#666', FS-1.2)
label(W/2, strip_y-16, 'Prefill: typically higher arithmetic intensity    |    Decode: often bandwidth-sensitive at low batch',
      '#555', FS-1.1)

# ===== visual grammar legend =====
legend_y = strip_y - 62
label(30, legend_y, 'visual grammar:', '#444', FS-0.9, ha='left', weight='bold')
leg=[('data / tokens',C_DATA),('model / compute',C_MODEL),('KV state (persistent)',C_KV)]
LEG_FILL={C_DATA:'#e0e0e0',C_MODEL:'#d3e0f2',C_KV:'#fbe3c8'}
LEG_EDGE={C_DATA:'#888',C_MODEL:'#27408b',C_KV:'#c06010'}
yy=legend_y-18; sx=30
for t,c in leg:
    ax.add_patch(FancyBboxPatch((sx, yy-6),14,11,boxstyle='round,pad=0.02',fc=LEG_FILL[c],ec=LEG_EDGE[c],lw=1.0,clip_on=False))
    label(sx+20, yy, t, '#444', FS-1.1, ha='left')
    sx += note_w(t, FS-1.1) + 44

plt.tight_layout(pad=0.2)
plt.savefig('design/manuscript/chapter-02/figures/fig-02-0202.png', dpi=200)
plt.close()
print('wrote fig-02-0202')
