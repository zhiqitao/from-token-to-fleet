import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-17-1702: host-count contours H = lambda*L / (C*util) over (lambda_peak x L) ----
# FP16 KV baseline C_16 = 18 ; FP8 KV C_8 = 35 ; util_target = 0.85
C16, C8, util = 18, 35, 0.85

lam = np.linspace(10, 120, 400)     # peak rps
Lat = np.linspace(0.2, 4.0, 400)    # avg latency s
Lam, Lg = np.meshgrid(lam, Lat)

H16 = np.maximum(1, np.ceil(Lam*Lg/(C16*util)))
H8  = np.maximum(1, np.ceil(Lam*Lg/(C8*util)))

fig, ax = plt.subplots(figsize=(9, 6.5))
levels = [1, 2, 3, 4, 6, 8, 12, 16]
cs16 = ax.contourf(Lg, Lam, H16, levels=levels, cmap='YlOrRd', alpha=0.55)
ax.contour(Lg, Lam, H16, levels=levels, colors='#b03a2e', linewidths=1.2)
# FP8 family dashed
cs8 = ax.contour(Lg, Lam, H8, levels=levels, colors='#27408b', linestyles='--', linewidths=1.4)
ax.clabel(cs8, inline=1, fontsize=8, fmt='%d')

ax.set_xlabel('Average latency L (s)')
ax.set_ylabel('Peak request rate λ (rps)')
ax.set_title('Ch17 — host count H = ⌈λ·L/(C·util)⌉  (filled=FP16 KV, dashed=FP8 KV)')

# mark the canonical operating points as (lambda, latency) -> plot (x=L, y=lambda)
canon = [(40,1.0),(100,1.0),(100,2.0),(40,0.5)]
offsets = {(40,1.0):(0.18,0),(100,1.0):(0.18,0),(100,2.0):(0.18,0),(40,0.5):(-0.3,-14)}
for (la, l) in canon:
    ox, oy = offsets[(la,l)]
    ax.plot(l, la, '*', ms=16, color='#c0392b', mec='#7b241c', zorder=6)
    ax.annotate(f'λ={la}, L={l}s', xy=(l,la), xytext=(l+ox, la+oy), fontsize=8, fontweight='bold')
# 'You are here' callout at the canonical 40 rps / 100 rps scenarios
ax.annotate('You are here (40 rps, 1.0 s)\nFP16 ≈ 3 hosts', xy=(1.0, 40), xytext=(2.6, 78),
            fontsize=9, fontweight='bold', color='#c0392b',
            arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.6))
ax.set_xlim(0.2, 4.0)
ax.set_ylim(10, 120)

cb = fig.colorbar(cs16, ax=ax, label='hosts (FP16 KV)')
plt.tight_layout()
plt.savefig('design/manuscript/chapter-17/figures/fig-17-1702.png', dpi=150)
plt.close()
print('wrote fig-17-1702')
