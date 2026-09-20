#!/usr/bin/env python3
"""fig-02-0202: CANONICAL end-to-end inference pipeline (prefill / decode).

Author at exactly the 6.1in book column width so regen_figs does NOT boost fonts.

The figure is the book's conceptual anchor. It must be clean and readable, so the
design is deliberately simple: two vertical bands (PREFILL, DECODE), a small
number of grouped boxes each, and a right-hand consequence column mapping the
phase to the hardware resource it stresses and the latency metric that measures
it.  Job (directive: every figure must have one):
  * answers "what physically happens prompt -> tokens, and what resource is
    stressed at each step?"
  * makes visible the continuity that matters most: K/V is *populated* in
    prefill and *reused* (not recomputed) in decode.
  * reader remembers prefill (one-shot parallel burst -> compute -> TTFT) vs
    decode (sequential loop -> bandwidth+capacity -> TPOT/ITL).
Layout is computed from box counts so nothing collides. 1 data unit == 1 point.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

BOLD = FontProperties(weight='bold')
FS = 8.4
W = 6.1 * 72                    # 439.2 pt column width
Ht = 7.9 * 72                   # tall anchor figure (full page is ~9in)
PADX = 0.30

def tw(s, fs=FS):
    return TextPath((0, 0), s, size=fs, prop=BOLD).get_extents().width

fig, ax = plt.subplots(figsize=(6.1, 7.9))
ax.set_xlim(0, W); ax.set_ylim(0, Ht); ax.axis('off')

C_MODEL='#27408b'; C_DATA='#8a8a8a'; C_KV='#e67e22'; C_SEQ='#c0392b'
C_CON='#2f6f4f'; C_AR='#555555'
C_PF='#eaf1fb'; C_DC='#fdf0e7'

def box(cx, cy, text, w, h, fc, ec, tc='white', fs=FS):
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                  boxstyle='round,pad=0.02,rounding_size=1.4',
                  fc=fc, ec=ec, lw=1.2, clip_on=False))
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fs,
            color=tc, fontweight='bold')
    return (cx-w/2, cx+w/2, cy-h/2, cy+h/2)

def label(cx, cy, text, color= '#444', fs=FS-0.4, ha='center', weight='normal', style='normal'):
    ax.text(cx, cy, text, ha=ha, va='center', fontsize=fs, color=color,
            fontweight=weight, style=style)

def arrow(x1,y1,x2,y2,color=C_AR,lw=1.4,style='-|>'):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                arrowprops=dict(arrowstyle=style,lw=lw,color=color,shrinkA=0,shrinkB=0))

BOX_H = 30; GAP = 13
# content column centre
cx = 168
con_cx = W-26

# ---- PREFILL band ----
pf_text = 'PREFILL — process the whole prompt, populate the KV cache, emit the first token'
pf_top = Ht - 16
pf_bottom = 348
pf_steps = [
    ('prompt text / context', C_DATA),
    ('tokenizer → token IDs → embeddings', C_DATA),
    ('transformer layers (×N)', C_MODEL),
    ('Q/K/V → attention (Q·Kᵀ softmax ·V)', C_MODEL),
    ('KV cache populated', C_KV),
    ('logits → sampling', C_MODEL),
    ('first output token', C_DATA),
]
# compute pf band top padding: title + subtitle + boxes
pf_title_y = pf_top - 20
pf_sub_y = pf_title_y - 16
n = len(pf_steps)
band_h = n*(BOX_H+GAP) + 24
pf_y1 = pf_sub_y - 12          # top of first box
pf_y0 = pf_y1 - n*(BOX_H+GAP) + GAP
ax.add_patch(FancyBboxPatch((12, pf_y0-8), W-24, (pf_y1+18-pf_y0)+8,
              boxstyle='round,pad=0.02,rounding_size=3', fc=C_PF, ec='#b9cbe8', lw=1.0, clip_on=False))
label(W/2, pf_title_y, pf_text, '#1a3a6b', FS+0.4, weight='bold')
label(22, pf_sub_y, 'one-shot burst over the prompt — parallel across prompt tokens', '#4a6a9a', FS-0.8, ha='left', style='italic')

# ---- DECODE band ----
dc_steps = [
    ('append newly generated token', C_DATA),
    ('reuse cached K/V from prior tokens', C_KV),
    ('read weights from HBM (every step)', C_MODEL),
    ('attention over cached K/V', C_MODEL),
    ('append this token’s K/V', C_KV),
    ('logits → sampling', C_MODEL),
]
dc_top = pf_y0 - 40
dc_title_y = dc_top - 6
dc_sub_y = dc_title_y - 16
dc_y1 = dc_sub_y - 12
dc_y0 = dc_y1 - len(dc_steps)*(BOX_H+GAP) + GAP
ax.add_patch(FancyBboxPatch((12, dc_y0-8), W-24, (dc_y1+18-dc_y0)+8,
              boxstyle='round,pad=0.02,rounding_size=3', fc=C_DC, ec='#e8c3a8', lw=1.0, clip_on=False))
label(W/2, dc_title_y, 'DECODE — generate one token at a time, reusing the cached K/V', '#8a3a12', FS+0.4, weight='bold')
label(22, dc_sub_y, 'sequential autoregressive loop — one token per step', '#a06a3a', FS-0.8, ha='left', style='italic')

# draw prefill boxes
pf_ys=[]
y = pf_y1
for text, c in pf_steps:
    w = max(tw(text)*(1+PADX)+12, 158)
    box(cx, y, text, w, BOX_H, c, '#333' if c==C_DATA else ('#8a3a12' if c==C_KV else '#16295c'), 'white')
    pf_ys.append(y); y -= (BOX_H+GAP)
for i in range(len(pf_ys)-1):
    arrow(cx, pf_ys[i]-BOX_H/2, cx, pf_ys[i+1]+BOX_H/2, C_AR, 1.0)

# draw decode boxes
dc_ys=[]
y=dc_y1
for text,c in dc_steps:
    w = max(tw(text)*(1+PADX)+12, 158)
    box(cx, y, text, w, BOX_H, c, '#333' if c==C_DATA else ('#8a3a12' if c==C_KV else '#16295c'), 'white')
    dc_ys.append(y); y -= (BOX_H+GAP)
for i in range(len(dc_ys)-1):
    arrow(cx, dc_ys[i]-BOX_H/2, cx, dc_ys[i+1]+BOX_H/2, C_AR, 1.0)

# connector prefill -> decode (feedback loop), terminating in the whitespace
# gap just above the DECODE title so the arrowhead never sits on text
arrow(cx, pf_ys[-1]-BOX_H/2, cx, dc_title_y+8, C_SEQ, 2.0, '-|>')
label(cx-16, (pf_ys[-1]+dc_title_y)/2, 'append token, iterate', C_SEQ, FS-0.6, ha='right', weight='bold')

# consequence column (right)
# prefill
label(con_cx, pf_ys[1], 'parallel over prompt tokens', C_CON, FS-0.8)
label(con_cx, pf_ys[2]+6, '→ substantial compute', C_CON, FS-0.3, weight='bold')
label(con_cx, pf_ys[2]-6, 'saturates FLOPs', C_CON, FS-0.9)
label(con_cx, pf_ys[3]+0, 'prefill compute-bound', C_CON, FS-0.9, style='italic')
label(con_cx, pf_ys[4]+4, 'KV cache → persistent', C_CON, FS-0.7)
label(con_cx, pf_ys[4]-8, 'per-request state', C_CON, FS-0.9)
label(con_cx, pf_ys[6], '→ TTFT', C_CON, FS-0.2, weight='bold')
arrow(cx+95, pf_ys[2], con_cx-52, pf_ys[2], C_CON, 1.0, '-')
# decode
label(con_cx, dc_ys[0], 'sequential → serial latency', C_CON, FS-0.8)
label(con_cx, dc_ys[1]+0, 'K/V reused (no recompute)', C_CON, FS-0.8)
label(con_cx, dc_ys[2]+6, '→ repeated weight read', C_CON, FS-0.3, weight='bold')
label(con_cx, dc_ys[2]-6, 'saturates HBM bandwidth', C_CON, FS-0.9)
label(con_cx, dc_ys[4]+0, 'KV grows with seq length', C_CON, FS-0.8)
label(con_cx, dc_ys[4]-10, '→ memory-capacity pressure', C_CON, FS-0.9)
label(con_cx, dc_ys[5], '→ TPOT / ITL', C_CON, FS-0.2, weight='bold')

# bottom note — placed clearly BELOW the decode band
note_y = dc_y0 - 22
label(W/2, note_y, 'repeat until end-of-sequence (or a stop condition)', '#666', FS-0.4)

# visual grammar legend — clear whitespace BELOW the note, bottom-left
legend_y = 16
lx = 40
label(lx, note_y-14, 'visual grammar:', '#444', FS-0.7, ha='left', weight='bold')
leg=[('data / tokens',C_DATA),('model / compute',C_MODEL),('KV state (persistent)',C_KV)]
yy=note_y-30
for t,c in leg:
    ax.add_patch(FancyBboxPatch((lx,yy-6),14,11,boxstyle='round,pad=0.02',fc=c,ec='#333',lw=0.6,clip_on=False))
    label(lx+20,yy,t,'#444',FS-1.0,ha='left'); yy-=15

plt.tight_layout(pad=0.2)
plt.savefig('design/manuscript/chapter-02/figures/fig-02-0202.png', dpi=200)
plt.close()
print('wrote fig-02-0202')
