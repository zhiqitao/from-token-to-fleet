import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ---- fig-24-2401: Red Team / Green Team cycle (pipeline + probe domains + backlog) ----
fig, ax = plt.subplots(figsize=(13.5, 6.2))
ax.set_xlim(0, 20); ax.set_ylim(0, 8.5); ax.axis('off')

# ---- Row 1 (top, y=6.7): the cyclic pipeline in order ----
pipe = [
    ('Red Team', '#a83232'),
    ('Probes', '#c0392b'),
    ('Exposure\nsurface', '#e67e22'),
    ('Guardrails', '#d68910'),
    ('Metrics', '#16a085'),
    ('Green Team', '#2980b9'),
]
xs = [1.0, 4.4, 8.0, 11.6, 15.2, 18.4]
for (label, col), x in zip(pipe, xs):
    ax.add_patch(FancyBboxPatch((x, 6.7), 1.7, 1.15, boxstyle='round,pad=0.02', fc=col, ec='none'))
    ax.text(x+0.85, 7.27, label, ha='center', va='center', color='white', fontsize=9.5, fontweight='bold')
for x in [2.85, 6.25, 9.8, 13.4, 17.2]:
    ax.annotate('', xy=(x+0.05, 7.27), xytext=(x-0.05, 7.27), arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#555'))

# ---- Row 2 (probe domains, lower mid y=3.5) ----
doms = ['Model behavior\n(jailbreak / persona)', 'Tool use\n(escalation / fuzz)', 'Retrieval / RAG\n(poisoning, injection)']
dxs = [2.8, 8.3, 13.1]
for d, x in zip(doms, dxs):
    ax.add_patch(FancyBboxPatch((x, 3.4), 3.5, 1.05, boxstyle='round,pad=0.02', fc='#fbe9e7', ec='#c0392b', lw=1.2))
    ax.text(x+1.75, 3.9, d, ha='center', va='center', fontsize=8, color='#333')
    ax.annotate('', xy=(x+1.75, 6.7), xytext=(x+1.75, 4.5), arrowprops=dict(arrowstyle='-|>', lw=1.3, color='#c0392b'))
ax.text(10, 2.55, 'probe domains', fontsize=8, ha='center', color='#c0392b', style='italic')

# ---- Feedback loop: Green Team back to Red Team, routed BELOW probe domains ----
ax.annotate('', xy=(2.5, 5.9), xytext=(19.0, 5.9),
            arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#a83232',
                            connectionstyle='arc3,rad=0.25'))
ax.text(10, 5.05, 'loop: findings inform the next probe cycle', fontsize=8.5, ha='center', color='#a83232')

# ---- Row 3: Metrics -> backlog (change requests) ----
ax.add_patch(FancyBboxPatch((14.9, 0.4), 4.0, 1.05, boxstyle='round,pad=0.02', fc='#d5f5e3', ec='#16a085'))
ax.text(16.9, 0.9, 'Change-request backlog\n(owner + SLA + metric)', ha='center', va='center', fontsize=8, color='#145a32')
ax.annotate('', xy=(17.4, 1.5), xytext=(17.4, 6.1), arrowprops=dict(arrowstyle='-|>', lw=1.3, color='#16a085', connectionstyle='arc3,rad=-0.08'))
ax.text(17.9, 3.8, 'metrics failure →\nbacklog (hardening / fixes)', fontsize=7.5, ha='center', color='#16a085')

ax.text(10, 8.0, 'Red Team / Green Team cycle: probe, measure, harden, loop', fontsize=13, fontweight='bold', ha='center', color='#1a1a1a')
plt.tight_layout()
plt.savefig('design/manuscript/chapter-24/figures/fig-24-2401.png', dpi=150); plt.close()
print('fig-24-2401 done')
