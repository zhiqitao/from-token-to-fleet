import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- fig-24-2401: Red Team / Green Team cycle ----
# Clean two-row layout with a single explicit feedback loop, numbered steps,
# and shape/pattern redundancy (not color-only) so it survives grayscale.
fig, ax = plt.subplots(figsize=(8.5, 5.6))
ax.set_xlim(0, 22); ax.set_ylim(0, 9.0); ax.axis('off')

# ---- Stage styles: colour + hatch + shape variant so each is distinct in grayscale ----
STAGES = [
    ('1 Red Team',      '#a83232', '//'),    # hatched
    ('2 Probes',        '#c0392b', 'xx'),
    ('3 Exposure',      '#e67e22', 'oo'),
    ('4 Guardrails',    '#d68910', '..'),
    ('5  Metrics',       '#16a085', '\\\\'),
    ('6 Green Team',    '#2980b9', '||'),
]

# Top row (y ~ 6.2)
xs = [0.6, 4.0, 7.4, 10.8, 14.2, 17.6]
ax.text(10, 8.5, 'Red Team / Green Team cycle: probe, measure, harden, loop',
        fontsize=12.5, fontweight='bold', ha='center', color='#1a1a1a')
ax.text(10, 7.7, '(1→6 shows the forward cycle; the red arrow is the one feedback loop back to step 1)',
        fontsize=8, ha='center', color='#555')
for (label, col, hatch), x in zip(STAGES, xs):
    ax.add_patch(FancyBboxPatch((x, 6.1), 2.0, 1.05, boxstyle='round,pad=0.02',
                                fc=col, ec='#333', lw=0.8, hatch=hatch))
    ax.text(x+0.8, 6.62, label, ha='center', va='center', color='white', fontsize=7.4, fontweight='bold')
# forward arrows between top stages (no crossing)
for x in [2.8, 6.2, 9.6, 13.0, 16.4]:
    ax.annotate('', xy=(x+0.55, 6.62), xytext=(x-0.05, 6.62),
                arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#555'))

# ---- Step 3 (Exposure) expands below into the probe domains (clean vertical) ----
doms = [('Model behavior', 'jailbreak · persona'),
        ('Tool use', 'escalation · fuzz'),
        ('Retrieval / RAG', 'poisoning · injection')]
dxs = [3.2, 8.0, 12.6]
ax.text(10, 4.55, 'probe domains (under step 3)', fontsize=8.5, ha='center', color='#e67e22', style='italic')
for (t1, t2), x in zip(doms, dxs):
    ax.add_patch(FancyBboxPatch((x, 3.0), 3.6, 0.95, boxstyle='round,pad=0.02',
                                fc='#fbe9e7', ec='#e67e22', lw=1.0, hatch='oo'))
    ax.text(x+1.8, 3.6, f'{t1}\n{t2}', ha='center', va='center', fontsize=7.8, color='#333')
    ax.annotate('', xy=(x+1.8, 6.1), xytext=(x+1.8, 3.95),
                arrowprops=dict(arrowstyle='-|>', lw=1.1, color='#e67e22'))

# ---- Single feedback loop: Green Team (6) -> Red Team (1), routed BELOW the domains ----
ax.annotate('', xy=(2.0, 2.55), xytext=(18.8, 2.55),
            arrowprops=dict(arrowstyle='-|>', lw=2.0, color='#a83232',
                            connectionstyle='arc3,rad=-0.12'))
ax.text(10, 1.75, 'loop: findings from Green Team → next Red Team cycle',
        fontsize=8.5, ha='center', color='#a83232')

# ---- Metrics (5) -> backlog (change requests) as a short vertical ----
ax.add_patch(FancyBboxPatch((14.8, 0.35), 3.8, 0.95, boxstyle='round,pad=0.02',
                            fc='#d5f5e3', ec='#16a085', lw=1.0, hatch='\\\\'))
ax.text(16.7, 0.82, 'Change-request backlog\n(owner + SLA + metric)', ha='center', va='center',
        fontsize=7.8, color='#145a32')
ax.annotate('', xy=(16.7, 1.30), xytext=(15.6, 6.05),
            arrowprops=dict(arrowstyle='-|>', lw=1.2, color='#16a085',
                            connectionstyle='arc3,rad=-0.10'))
ax.text(18.6, 3.9, 'metrics failure →\nbacklog (hardening)', fontsize=7.5, ha='center', color='#16a085')

plt.tight_layout()
plt.savefig('design/manuscript/chapter-24/figures/fig-24-2401.png', dpi=150)
plt.close()
print('fig-24-2401 done')
