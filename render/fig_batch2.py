import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

base = 'design/manuscript/chapter-%02d/figures/fig-%02d-%02d01.png'

# ---- Ch13: reference-architecture ladder + escalation triggers ----
# DISABLED: redrawn with Archify (render/archify/ch13-ladder.json + ch13-ladder-min.html)
# to fix the green de-escalation label overlapping the Cluster/fleet box.
# Asset: design/manuscript/chapter-13/figures/fig-13-1301.{pdf,png}.

# ---- Ch14: capability screen then deployment benchmark ----
fig, ax = plt.subplots(figsize=(6.4, 4.8))
ax.set_xlim(0, 16); ax.set_ylim(0, 4.5); ax.axis('off')
steps = ['Candidate\nmodels', 'Capability screen\n(MMLU/GSM8K/QA)', 'Survivors',
         'Deployment bench\n(TTFT/goodput/KV)', 'Selection + TCO']
xs = [0.3, 3.0, 5.9, 8.6, 12.0]
for i, (s, x) in enumerate(zip(steps, xs)):
    col = '#3a6ea5' if i not in (1, 3) else '#e67e22'
    ax.add_patch(FancyBboxPatch((x, 1.9), 2.6, 2.0, boxstyle='round,pad=0.02', fc=col, ec='none'))
    ax.text(x+1.3, 2.9, s, ha='center', va='center', color='white', fontsize=9, fontweight='bold')
    if i < len(steps)-1:
        ax.annotate('', xy=(x+2.8, 2.9), xytext=(x+2.6, 2.9), arrowprops=dict(arrowstyle='-|>', lw=2, color='#555'))
ax.text(8, 0.8, 'Screen on capability first, then benchmark on the real workload\nagainst the SLO gate',
        fontsize=9, fontweight='bold', ha='center', color='#333')
plt.tight_layout()
plt.savefig(base % (14, 14, 14), dpi=150); plt.close()
print('Ch14 done')

# ---- Ch16: TCO three delivery modes (regenerated from render/tco_calc.py) ----
p = np.logspace(4, 8, 200)          # requests / month
# Mode 1 self-hosted (canonical 8xH100): ~flat fixed $21.2K/mo up to ~26M req capacity
m1 = np.full_like(p, 21200)
# Mode 2 cloud on-demand (8xH100, 40% duty): ~flat $1.0K/mo
m2 = np.full_like(p, 1008)
# Mode 3 managed API: linear at $20.80/1K req
m3 = 20.80 * p / 1000
fig, ax = plt.subplots(figsize=(8.5, 5.5))
ax.loglog(p, m1, color='#3a6ea5', lw=2, label='Mode 1 self-hosted (~$21.2K/mo flat; $0.82/1K @ 26M)')
ax.loglog(p, m2, color='#6f9e5f', lw=2, label='Mode 2 cloud on-demand (~$1.0K/mo @ 40% duty)')
ax.loglog(p, m3, color='#c0392b', lw=2, label='Mode 3 managed API ($20.80/1K req)')
# break-even self-host vs API (mode1_total / per_req ~ 1.02M req/mo)
be = 1020833
ax.axvline(be, color='#888', ls='--', lw=1)
ax.annotate(f'break-even ≈ {be/1e6:.2f}M req/mo', xy=(be, 2e3), xytext=(2e4, 1e4),
            arrowprops=dict(arrowstyle='->'), fontsize=10)
# canonical volume 26M req/mo in-axis
canon = 25920000
ax.axvline(canon, color='#27408b', ls=':', lw=1.5)
ax.annotate('canonical 26M req/mo', xy=(canon, 200), xytext=(3e5, 500),
            arrowprops=dict(arrowstyle='->'), fontsize=9, color='#27408b')
# Mode 2 assumption caveat (keeps whole figure honest: flat line only valid at fixed 40% duty,
# excludes staff/integration; crossover at ~1.02M is self-host vs API, not Mode 2)
ax.annotate('Mode 2 flat @ 40% duty —\nexcludes staff/integration (see §16.4);\nbreak-even ≈1.02M is self-host vs API',
            xy=(8e5, 1000), xytext=(9e5, 20000),
            arrowprops=dict(arrowstyle='->', color='#6f9e5f'),
            fontsize=8.5, color='#6f9e5f')
ax.set_xlabel('Requests / month')
ax.set_ylabel('Cost ($ / month)')
ax.set_title('Ch16 — TCO across the three delivery modes (canonical workload)')
ax.legend(fontsize=8, loc='upper left')
ax.grid(alpha=0.3, which='both')
ax.set_xlim(1e4, 1.2e8)
plt.tight_layout()
plt.savefig(base % (16, 16, 16), dpi=150); plt.close()
print('Ch16 done')

# ---- Ch21: AI Factory promotion pipeline (evaluate-gate + rollback edge) ----
fig, ax = plt.subplots(figsize=(9, 6.5))
ax.set_xlim(0, 16); ax.set_ylim(0, 8.6); ax.axis('off')
steps = ['Data', 'Train', 'Evaluate', 'Canary', 'Observe', 'Promote', 'Rollback', 'Serve']
xs = [0.3, 2.1, 3.9, 5.7, 7.5, 9.3, 11.1, 12.9]
for i, (s, x) in enumerate(zip(steps, xs)):
    col = '#3a6ea5' if i < len(steps)-1 else '#6f9e5f'
    ax.add_patch(FancyBboxPatch((x, 4.4), 1.6, 1.7, boxstyle='round,pad=0.02', fc=col, ec='none'))
    ax.text(x+0.8, 5.25, s, ha='center', va='center', color='white', fontsize=10.5, fontweight='bold')
    if i < len(steps)-1:
        ax.annotate('', xy=(x+1.65, 5.25), xytext=(x+1.6, 5.25), arrowprops=dict(arrowstyle='-|>', lw=1.8, color='#555'))
# evaluate->canary: gate glyph (pass/fail)
ax.text(5.65, 6.55, 'gate', fontsize=9, color='#c0392b', ha='right')
ax.annotate('', xy=(5.7, 6.0), xytext=(5.5, 6.0), arrowprops=dict(arrowstyle='-|>', lw=1.5, color='#c0392b'))
# rollback edge from Serve back to Rollback (and on to Evaluate)
ax.annotate('', xy=(11.2, 3.4), xytext=(14.2, 3.4), arrowprops=dict(arrowstyle='-|>', lw=1.7, color='#c0392b',
            connectionstyle='arc3,rad=0.22'))
ax.annotate('', xy=(10.0, 3.9), xytext=(11.15, 3.35), arrowprops=dict(arrowstyle='-|>', lw=1.5, color='#c0392b',
            connectionstyle='arc3,rad=0.18'))
# feedback arrow: from Serve box bottom back to Data box bottom
ax.annotate('', xy=(1.1, 3.4), xytext=(14.0, 3.4), arrowprops=dict(arrowstyle='-|>', lw=1.5, color='#3d6e35',
            connectionstyle='arc3,rad=0.22'))
ax.text(7.5, 1.9, 'production feedback → data / evaluation (green, bottom); rollback on SLO breach (red)',
        fontsize=9.5, color='#555', ha='center')
ax.text(7.5, 7.9, 'The AI Factory promotion pipeline (canary gate on promote, rollback path)',
        fontsize=12, fontweight='bold', ha='center')
plt.tight_layout()
plt.savefig(base % (21, 21, 21), dpi=150); plt.close()
print('Ch21 done')

# ---- Ch23: from vague ask to architectural bounds (worked example, not a generic funnel) ----
fig, ax = plt.subplots(figsize=(6.1, 6.4))
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
# A generic funnel restates the chapter; instead trace the CANONICAL vague ask
# ("our app is slow") through each gate to a quantified architectural bound.
stages = [
    ('1. What is the true problem?',
     '"our app is slow" \u2192 TTFT p99 1.4 s on a 70B model'),
    ('2. What does success look like?',
     'p95 TTFT < 300 ms, TPOT ~25 ms, 40 rps peak'),
    ('3. What data exists?',
     '9.2K-token prompts, ~55% share a common prefix'),
    ('4. What are the constraints?',
     '8\u00d7H100 host, ~$14.6K/mo, no SLO headroom'),
    ('5. What is in scope now?',
     'KV precision FP16\u2192FP8 + prefix cache + routing'),
]
for i, (q, a) in enumerate(stages):
    w = 8.6 - i*0.55
    y = 8.6 - i*1.35
    ax.add_patch(FancyBboxPatch(((10-w)/2, y), w, 1.08, boxstyle='round,pad=0.02', fc='#f0b35f', ec='#c07a2a'))
    ax.text(5, y+0.80, q, ha='center', va='center', fontsize=9.0, fontweight='bold', color='#4a2f10')
    ax.text(5, y+0.34, a, ha='center', va='center', fontsize=7.7, color='#5a3a14')
# outcome
ax.add_patch(FancyBboxPatch((1.5, 0.45), 7.0, 0.9, boxstyle='round,pad=0.02', fc='#6f9e5f', ec='#3d5a2f'))
ax.text(5, 0.9, 'Quantified bounds \u2192 {TTFT, throughput, cost} budget', ha='center', va='center',
        color='white', fontsize=8.0, fontweight='bold')
ax.text(5, 9.85, 'From a vague ask to architectural bounds (worked example)', fontsize=11.6, fontweight='bold', ha='center', color='#1a1a1a')
plt.tight_layout()
plt.savefig(base % (23, 23, 23), dpi=150); plt.close()
print('Ch23 done')

# ---- Ch25: anatomy of an ADR ----
fig, ax = plt.subplots(figsize=(12, 4.5))
ax.set_xlim(0, 16); ax.set_ylim(0, 4.5); ax.axis('off')
comps = ['Context', 'Options', 'Decision', 'Rationale', 'Consequences']
# All boxes share the width required by the longest label ('Consequences')
# so the row is uniformly balanced.
bw = [2.9, 2.9, 2.9, 2.9, 2.9]
xs = []
_cx = 0.3
for b in bw:
    xs.append(_cx)
    _cx += b + 0.35
for i, (c, x, w) in enumerate(zip(comps, xs, bw)):
    ax.add_patch(FancyBboxPatch((x, 1.5), w, 1.5, boxstyle='round,pad=0.02', fc='#3a6ea5', ec='none'))
    ax.text(x + w/2, 2.25, c, ha='center', va='center', color='white', fontsize=10, fontweight='bold')
    if i < len(comps)-1:
        ax.annotate('', xy=(x+w+0.35, 2.25), xytext=(x+w, 2.25), arrowprops=dict(arrowstyle='-|>', lw=1.6, color='#555'))
ax.text(8, 0.6, 'An ADR supersedes an old one: the why is captured at decision time', fontsize=11, fontweight='bold', ha='center', color='#333')
plt.tight_layout()
plt.savefig(base % (25, 25, 25), dpi=150); plt.close()
print('Ch25 done')

print('batch part 2 complete')
