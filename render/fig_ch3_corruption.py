#!/usr/bin/env python3
"""Fig 3.1 — Corruption and learned reverse generation (vector rebuild).

R7 fix (FIG-3.1-02): lane A's 'noise prior' canvas must read near-uniform and
'partly corrupted' must sit between clean and noise. The original hand-drawn
raster had no generator in-repo; this script is the new source of truth.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D

NAVY = "#1A2332"
BLUE = "#2C4A8C"
FILL = "#E8EDF7"
ORANGE = "#E87722"
BG = "#F7F9FC"
HATCH = "#D9DEE6"

fig = plt.figure(figsize=(6.1, 4.65), dpi=350)
fig.patch.set_facecolor(BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 7.5)
ax.axis("off")

# ---- header
ax.text(5, 7.18, "Corruption is specified; reverse generation is learned",
        ha="center", va="center", fontsize=10.5, fontweight="bold", color=NAVY)
ax.text(5, 6.82, "Forward q: add corruption.  Reverse p\u03b8: generate with learned updates.",
        ha="center", va="center", fontsize=8.5, color=NAVY)

def canvas(x, y, w, h, bars=None, tokens=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=FILL, ec=BLUE, lw=1.2))
    if bars is not None:
        n = len(bars)
        bw = w / (n * 2 + 1)
        for i, b in enumerate(bars):
            bx = x + bw * (i * 2 + 1)
            ax.add_patch(Rectangle((bx, y + 0.12), bw * 0.85, b / 5.0 * (h - 0.35),
                                   fc=BLUE, ec="none"))
    if tokens is not None:
        n = len(tokens)
        tw = min(0.52, (w - 0.3) / n * 0.82)
        gap = (w - n * tw) / (n + 1)
        for i, (t, masked) in enumerate(tokens):
            tx = x + gap + i * (tw + gap)
            ty = y + (h - tw) / 2
            if masked:
                ax.add_patch(FancyBboxPatch((tx, ty), tw, tw, boxstyle="round,pad=0.01,rounding_size=0.05",
                                            fc=HATCH, ec=BLUE, lw=1.0, hatch="///"))
                ax.text(tx + tw / 2, ty + tw / 2, "M", ha="center", va="center",
                        fontsize=8.5, fontweight="bold", color=NAVY)
            else:
                ax.add_patch(FancyBboxPatch((tx, ty), tw, tw, boxstyle="round,pad=0.01,rounding_size=0.05",
                                            fc=FILL, ec=BLUE, lw=1.0))
                ax.text(tx + tw / 2, ty + tw / 2, t, ha="center", va="center",
                        fontsize=8.5, color=NAVY)

def arrow_pair(x1, x2, ymid):
    ax.annotate("", xy=(x2 - 0.06, ymid + 0.22), xytext=(x1 + 0.06, ymid + 0.22),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.6))
    ax.text((x1 + x2) / 2, ymid + 0.42, "q", ha="center", va="center", fontsize=9, color=NAVY)
    ax.annotate("", xy=(x1 + 0.06, ymid - 0.22), xytext=(x2 - 0.06, ymid - 0.22),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.6))
    ax.text((x1 + x2) / 2, ymid - 0.44, "p\u03b8", ha="center", va="center", fontsize=9, color=ORANGE)

# ---- lane A (continuous diffusion)
ax.text(0.25, 5.95, "A  Continuous diffusion (schematic state values; bars \u2260 token probabilities)",
        ha="left", va="center", fontsize=8.5, fontweight="bold", color=NAVY)
# R7 fix: clean = smooth hump; partly corrupted = intermediate (structure still visible);
# noise prior = near-uniform (small variation around the mean).
clean = [2, 3, 4, 5, 4, 3, 2, 1.5]
partly = [3, 2.5, 4, 3.5, 4, 2.5, 3.5, 3]
noise = [3.1, 2.9, 3.2, 3.0, 2.9, 3.1, 3.0, 2.9]
bx, bw_, bh = 0.25, 2.4, 1.5
canvas(bx, 4.15, bw_, bh, bars=clean)
canvas(bx + 3.55, 4.15, bw_, bh, bars=partly)
canvas(bx + 7.1, 4.15, bw_, bh, bars=noise)
ax.text(bx + bw_ / 2, 3.92, "clean continuous data", ha="center", va="center", fontsize=8, color=NAVY)
ax.text(bx + 3.55 + bw_ / 2, 3.92, "partly corrupted", ha="center", va="center", fontsize=8, color=NAVY)
ax.text(bx + 7.1 + bw_ / 2, 3.92, "noise prior", ha="center", va="center", fontsize=8, color=NAVY)
arrow_pair(bx + bw_, bx + 3.55, 4.9)
arrow_pair(bx + 3.55 + bw_, bx + 7.1, 4.9)

# ---- lane B (masked discrete diffusion)
ax.text(0.25, 3.15, "B  Masked discrete diffusion (one categorical choice)",
        ha="left", va="center", fontsize=8.5, fontweight="bold", color=NAVY)
cy, ch = 1.55, 1.15
canvas(bx, cy, bw_, ch, tokens=[("A", 0), ("cat", 0), ("sat", 0), (".", 0)])
canvas(bx + 3.55, cy, bw_, ch, tokens=[("A", 0), ("M", 1), ("sat", 0), ("M", 1)])
canvas(bx + 7.1, cy, bw_, ch, tokens=[("M", 1), ("M", 1), ("M", 1), ("M", 1)])
ax.text(bx + bw_ / 2, 1.32, "clean", ha="center", va="center", fontsize=8, color=NAVY)
ax.text(bx + 3.55 + bw_ / 2, 1.32, "partly masked", ha="center", va="center", fontsize=8, color=NAVY)
ax.text(bx + 7.1 + bw_ / 2, 1.32, "fully masked", ha="center", va="center", fontsize=8, color=NAVY)
arrow_pair(bx + bw_, bx + 3.55, 2.12)
arrow_pair(bx + 3.55 + bw_, bx + 7.1, 2.12)
ax.text(5, 0.98, "M = MASK; text states are illustrative token IDs, not generated results.",
        ha="center", va="center", fontsize=8, color=NAVY)

# ---- footer
ax.text(0.25, 0.72, "Training: construct corrupted inputs; learn reverse predictions.",
        ha="left", va="center", fontsize=8.5, fontweight="bold", color=NAVY)
ax.text(0.25, 0.48, "Sampling: start from the prior; apply learned reverse updates.",
        ha="left", va="center", fontsize=8.5, fontweight="bold", color=NAVY)
ax.text(0.25, 0.24, "Flow matching learns a vector field on a chosen probability path.",
        ha="left", va="center", fontsize=8, color=NAVY)
ax.text(0.25, 0.08, "Related paths do not make diffusion and flow matching identical.",
        ha="left", va="center", fontsize=8, color=NAVY)

out_png = "design/manuscript/chapter-03/figures/fig-03-0302-diffusion-corruption.png"
out_pdf = "design/manuscript/chapter-03/figures/fig-03-0302-diffusion-corruption.pdf"
fig.savefig(out_png, dpi=350, facecolor=BG)
with matplotlib.rc_context({"pdf.fonttype": 42, "ps.fonttype": 42}):
    fig.savefig(out_pdf, format="pdf", facecolor=BG)
print("wrote fig-03-0302 (lane A: clean hump / partly corrupted intermediate / noise prior near-uniform)")
