import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

base = 'design/manuscript/chapter-%02d/figures/fig-%02d-%02d01.png'

# ---- Ch06: three-layer metric hierarchy (causation bottom-up, diagnosis top-down) ----
# Replaced by Archify-rendered asset (render/archify/ch6-metric-hierarchy.json ->
# design/manuscript/chapter-06/figures/fig-06-0601.{png,pdf}). The matplotlib
# version had the '(resource -> workload)' caption overlapping the Workload
# metrics block with poor text/block contrast, so the source generator is
# retired here and regen_figs.py must not clobber the Archify asset.
print('fig-06-0601: Archify-rendered asset; matplotlib generator retired')

# ---- Ch12: three candidate architectures ----
fig, ax = plt.subplots(figsize=(12, 5))
ax.set_xlim(0, 14); ax.set_ylim(0, 5); ax.axis('off')
cands = ['Candidate A\n(single large model)', 'Candidate B\n(RAG + smaller gen)', 'Candidate C\n(fleet of specialised)']
col = ['#3a6ea5', '#e67e22', '#6f9e5f']
for i, (c, co) in enumerate(zip(cands, col)):
    x = 0.5 + i*4.6
    ax.add_patch(FancyBboxPatch((x, 1.5), 3.8, 2.0, boxstyle='round,pad=0.02', fc=co, ec='none'))
    ax.text(x+1.9, 2.5, c, ha='center', va='center', color='white', fontsize=10.5, fontweight='bold')
    ax.text(x+1.9, 1.1, 'tradeoffs: capability / freshness / cost / latency', ha='center', fontsize=8, color='#555')
ax.text(7, 4.4, 'Three candidate architectures synthesized from the same workload constraints (Ch12)',
        fontsize=12, fontweight='bold', ha='center')
plt.tight_layout()
plt.savefig(base % (12, 12, 12), dpi=150); plt.close()
print('Ch12 done')

# ---- Ch15: goodput vs batch (prefix cache relaxes PREFILL, not decode) ----
fig, ax = plt.subplots(figsize=(8, 5.5))
batch = np.array([1, 2, 4, 8, 16, 32, 64])
# relative goodput: decode is bandwidth-bound; batching raises util until memory saturates
no_cache = 100 * (1 - np.exp(-batch/12))
# prefix cache removes prefill recompute -> raises the ceiling, esp. for repeated prefixes
cache = np.minimum(no_cache + 60*(1-np.exp(-batch/8)), 100)
ax.plot(batch, no_cache, '-o', color='#c0392b', label='no prefix cache')
ax.plot(batch, cache, '-s', color='#3a6ea5', label='with prefix/prompt cache')
ax.set_xlabel('Decode batch size')
ax.set_ylabel('Relative goodput (a.u.)')
ax.set_title('Batching raises decode goodput;\nprefix cache raises the ceiling', fontsize=11)
ax.annotate('prefix cache removes prefill recompute\n(the decode bottleneck is unchanged)', xy=(16, cache[4]), xytext=(34, 62),
            fontsize=8.5, color='#3a6ea5', arrowprops=dict(arrowstyle='->', color='#3a6ea5'))
ax.legend(fontsize=9, loc='upper left')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(base % (15, 15, 15), dpi=150); plt.close()
print('Ch15 done')

# ---- Ch17: fleet architecture (Archify-generated: render/archify/fleet-hierarchy.json) ----
# The LB→N-hosts fan-out figure is produced by the Archify pipeline (see
# render/archify/fleet-hierarchy.*) and checked in as fig-17-1701.{png,pdf}.

# ---- Ch18: model-routing decision tree (capability filter -> cost/latency -> fallthrough) ----
# 2-row reflow with 3 DISTINCT stage boxes and rail-based routing (no crossing mesh).
fig, ax = plt.subplots(figsize=(6.6, 7.0))
ax.set_xlim(0, 9.0); ax.set_ylim(0, 8.8); ax.axis('off')
# title
ax.text(4.5, 8.4, 'Ch18 — routing every request to the right specialised model',
        fontsize=11, fontweight='bold', ha='center', color='#333')
# root (top center)
ax.add_patch(FancyBboxPatch((3.3, 6.9), 2.4, 0.95, boxstyle='round,pad=0.02', fc='#27408b', ec='none'))
ax.text(4.5, 7.37, 'Request', ha='center', va='center', color='white', fontsize=10.5, fontweight='bold')
# three DISTINCT routing stages (row 1, small boxes with gaps)
stages = [('Capability filter\n(specialised model?)', 0.4, '#e67e22'),
          ('Cost / latency gate\n(route = f(cost, SLO))', 3.3, '#e67e22'),
          ('Fallthrough\nto general model', 6.2, '#e67e22')]
for lbl, x, c in stages:
    ax.add_patch(FancyBboxPatch((x, 5.0), 2.5, 1.25, boxstyle='round,pad=0.02', fc=c, ec='none'))
    ax.text(x+1.25, 5.62, lbl, ha='center', va='center', color='white', fontsize=9, fontweight='bold')
# five families (leaves, row 2)
leaves = ['Embedding', 'Small gen', 'Large frontier', 'Math / reasoning', 'Vision']
col = ['#3a6ea5', '#6f9e5f', '#c0392b', '#e67e22', '#8055b5']
for i, (lm, c) in enumerate(zip(leaves, col)):
    x = 0.3 + i*1.75
    ax.add_patch(FancyBboxPatch((x, 1.3), 1.55, 1.0, boxstyle='round,pad=0.02', fc=c, ec='none'))
    ax.text(x+0.775, 1.8, lm, ha='center', va='center', color='white', fontsize=8.5, fontweight='bold')
# Request -> each stage (3 clean arrows from Request bottom to stage top)
for x in [1.65, 4.5, 7.45]:
    ax.annotate('', xy=(x, 6.3), xytext=(4.5, 6.88), arrowprops=dict(arrowstyle='-|>', lw=1.3, color='#555'))
# stage row -> leaf row via a horizontal rail (drops from each stage bottom to rail, then to leaves)
rail_y = 2.55
ax.plot([0.5, 8.6], [rail_y, rail_y], color='#8a8a8a', lw=1.0, zorder=1)
# vertical stubs from EACH stage box down to the rail
for sx in [1.65, 4.5, 7.45]:
    ax.plot([sx, sx], [5.0, rail_y], color='#8a8a8a', lw=1.0, zorder=0)
# from rail, short drops to each leaf
for i in range(5):
    lx = 0.3 + i*1.75 + 0.775
    ax.plot([lx, lx], [rail_y, 2.3], color='#8a8a8a', lw=1.0, zorder=1)
    ax.annotate('', xy=(lx, 2.3), xytext=(lx, rail_y), arrowprops=dict(arrowstyle='-|>', lw=0.9, color='#8a8a8a'))
ax.text(4.5, 3.1, 'capability → cost/SLO → fallthrough', fontsize=9, color='#555', ha='center', zorder=3)
plt.tight_layout()
plt.savefig(base % (18, 18, 18), dpi=150); plt.close()
print('Ch18 done')

# ---- Ch19: agent loop state machine (Archify-generated: render/archify/agent-loop-lifecycle.json) ----
# The four-state (Plan→Execute→Observe→Decide) lifecycle figure is produced by
# the Archify pipeline and checked in as fig-19-1901.{png,pdf}.

# ---- Ch20: fleet capacity — ANALYTICAL BOUND vs MEASURED DEPLOYMENT (ILLUSTRATIVE) ----
# The chapter's ~2.0 req/s/host figure drives the 5-20-host sizing reasoning, so it
# deserves a large, unambiguous two-panel treatment. DESIGNER PASS:
#   * TWO CLEAR PANELS — top = ANALYTICAL CAPACITY BOUND; bottom = MEASURED DEPLOYMENT.
#   * VISUALLY OBVIOUS distinction: the analytical bound is a THIN GREY DASHED line;
#     the measured deployment throughput is a THICK COLOURED SOLID line. Not colour alone
#     (channel redundancy: colour + line style + dash + marker + label).
#   * ANNOTATIONS LARGE (multiple lines of explanatory text, not crowded out by the curves).
# The bound is the ~2.0 req/s/host KV/service-time analytical ceiling; the measured
# curve below it reflects the ~95% scheduling efficiency and the tail that caps a
# fleet at the canonical 40 rps peak once ~20 hosts are provisioned.
fig, axs = plt.subplots(2, 1, figsize=(6.1, 8.2), gridspec_kw={'hspace': 0.5})
fig._hermes_print_sized = True   # print-size authored at column width; regen must not re-boost/reflow
hosts = np.array([1, 2, 3, 4, 6, 8, 10, 12, 16, 20, 24, 30, 40, 60])
per_host = 2.0                     # KV/service-time analytical bound (req/s/host)
bound = per_host * hosts
schedule_eff = 0.95                # ~95% scheduling efficiency
peak_load = 40.0                   # canonical peak demand (rps)
plateau = peak_load * 0.97         # tail/queueing keeps achieved slightly below the nominal peak
capacity_eff = per_host * hosts * schedule_eff
measured = np.minimum(capacity_eff, plateau)

# ---- Panel 1 (top): ANALYTICAL CAPACITY BOUND ----
ax = axs[0]
ax.plot(hosts, bound, ls='--', lw=1.8, color='#8a8a8a', marker='D', ms=5,
        markevery=2, label='ANALYTICAL BOUND  ~2.0 req/s/host')
ax.axhline(peak_load, color='#c0392b', ls=':', lw=1.4, zorder=0)
ax.text(2.0, peak_load + 6, 'canonical peak load = 40 rps', fontsize=10, color='#7a2020')
ax.set_xlim(0, 68); ax.set_ylim(0, 130)
ax.set_xlabel('Host count', fontsize=11)
ax.set_ylabel('Fleet capacity (req/s)', fontsize=11)
ax.set_title('ANALYTICAL CAPACITY BOUND  (no overhead)', fontsize=11.5,
             fontweight='bold', color='#555')
ax.tick_params(labelsize=9.5)
ax.grid(alpha=0.3)
ax.legend(fontsize=10, loc='upper left', framealpha=0.92)
ax.text(0.99, 0.96, '[ILLUSTRATIVE][DERIVED]', transform=ax.transAxes, fontsize=9,
        color='#8a5a00', ha='right', va='top')
# ceiling annotation parked in the empty lower-right (below the bound line)
ax.annotate('~2.0 req/s/host\n(KV/service-time ceiling)',
            xy=(26, 52), xytext=(46, 18), fontsize=11.5, color='#7a2020',
            ha='center', arrowprops=dict(arrowstyle='-|>', color='#7a2020', lw=1.4))

# ---- Panel 2 (bottom): MEASURED DEPLOYMENT THROUGHPUT ----
ax = axs[1]
# faint analytical reference (thin dashed grey) so the gap to measured is obvious
ax.plot(hosts, bound, ls='--', lw=1.4, color='#8a8a8a', marker='D', ms=4,
        markevery=2, label='analytical bound (ceiling)')
ax.plot(hosts, measured, ls='-', lw=4.0, color='#3a6ea5', marker='o', ms=7,
        label='MEASURED deployment throughput')
ax.set_xlim(0, 68); ax.set_ylim(0, 130)
ax.set_xlabel('Host count', fontsize=11)
ax.set_ylabel('Fleet throughput (req/s)', fontsize=11)
ax.set_title('MEASURED DEPLOYMENT THROUGHPUT', fontsize=11.5,
             fontweight='bold', color='#1e4d78')
ax.tick_params(labelsize=9.5)
ax.grid(alpha=0.3)
ax.legend(fontsize=10, loc='upper left', framealpha=0.92)
# operating points that drive the 5-20-host sizing reasoning (parked in empty regions)
ax.annotate('~5 hosts \u2192 ~9.5 req/s',
            xy=(5, measured[4]), xytext=(10, 22), fontsize=11.5, color='#1e4d78',
            ha='left', arrowprops=dict(arrowstyle='-|>', color='#1e4d78', lw=1.4))
ax.annotate('\u224820 hosts \u2192 reaches the 40 rps peak;\nmeasured plateaus (gap \u224895%)',
            xy=(20, measured[9]), xytext=(38, 55), fontsize=11.5, color='#c0392b',
            ha='center', arrowprops=dict(arrowstyle='-|>', color='#c0392b', lw=1.4))
plt.subplots_adjust(left=0.13, right=0.96, top=0.93, bottom=0.08)
plt.savefig(base % (20, 20, 20), dpi=150); plt.close()
print('Ch20 done')

# ---- Ch22: prefill vs decode bottleneck divergence (9.2K marker + quadratic band) ----
fig, ax = plt.subplots(figsize=(8.5, 5.5))
ctx = np.array([1, 4, 9.2, 32, 128])
prefill = 2*70e9*ctx*1000/1e15  # PFLOP linear 2NL, grows with context
# quadratic attention term (Ch8 note): 4*nl*L^2*d ; +17% at 9.2K, ~2.4x at 128K
nl, d = 80, 8192
attn = 4*nl*(ctx*1000)**2*d/1e15   # PFLOP
ax.plot(ctx, prefill, '-o', color='#c0392b', label='prefill PFLOP (linear 2NL)')
ax.plot(ctx, prefill+attn, '--s', color='#e67e22', label='prefill incl. quadratic attention')
ax.fill_between(ctx, prefill, prefill+attn, color='#e67e22', alpha=0.12)
# decode is a fixed ~140 GFLOP/token = 0.00014 PFLOP, ~9000x below this axis' floor (0.01);
# it cannot share a PFLOP axis meaningfully and stays bandwidth-bound (see Ch6), so it is
# called out in the caption/note rather than drawn as an invisible ~0 line.
ax.scatter([9.2], [prefill[2]], color='#c0392b', zorder=5, s=25)
ax.annotate('9.2K canonical', xy=(9.2, prefill[2]), xytext=(20, 0.02),
            arrowprops=dict(arrowstyle='->'), fontsize=8.5)
ax.annotate('quadratic attention term\n(+17% @ 9.2K → ~2.4× @ 128K)', xy=(30, prefill[3]+attn[3]), xytext=(40, 0.6),
            fontsize=8.5, color='#e67e22', ha='center', arrowprops=dict(arrowstyle='->', color='#e67e22'))
ax.set_xlabel('Context length (K tokens)')
ax.set_ylabel('Compute (PFLOP)')
ax.set_xscale('log')
ax.set_title('Ch22 — prefill and decode diverge as context grows')
ax.legend(fontsize=8.5)
ax.grid(alpha=0.3)
ax.set_ylim(0.01, 4)
plt.tight_layout()
plt.savefig(base % (22, 22, 22), dpi=150); plt.close()
print('Ch22 done')

# ---- Ch24: red team / green team cycle ----
fig, ax = plt.subplots(figsize=(7, 7))
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')
ax.add_patch(FancyBboxPatch((1.5, 5.3), 3.2, 1.8, boxstyle='round,pad=0.02', fc='#c0392b', ec='none'))
ax.text(3.1, 6.2, 'Red Team\n(adversarial)', ha='center', va='center', color='white', fontsize=11, fontweight='bold')
ax.add_patch(FancyBboxPatch((5.3, 5.3), 3.2, 1.8, boxstyle='round,pad=0.02', fc='#3a6ea5', ec='none'))
ax.text(6.9, 6.2, 'Green Team\n(defender)', ha='center', va='center', color='white', fontsize=11, fontweight='bold')
ax.annotate('', xy=(5.3, 6.2), xytext=(4.7, 6.2), arrowprops=dict(arrowstyle='-|>', lw=2, color='#555'))
ax.annotate('', xy=(5.5, 5.0), xytext=(5.5, 4.4), arrowprops=dict(arrowstyle='-|>', lw=1.5, color='#555'))
ax.add_patch(FancyBboxPatch((3.1, 3.0), 3.8, 1.4, boxstyle='round,pad=0.02', fc='#e67e22', ec='none'))
ax.text(5, 3.7, 'combined outcome\n→ architecture change', ha='center', va='center', color='white', fontsize=9)
ax.annotate('', xy=(3.1, 3.3), xytext=(3.1, 4.4), arrowprops=dict(arrowstyle='-|>', lw=1.5, color='#555'))
ax.annotate('', xy=(3.1, 5.2), xytext=(2.6, 3.0), arrowprops=dict(arrowstyle='-|>', lw=1.2, color='#555', connectionstyle='arc3,rad=-0.3'))
ax.text(5, 9.2, 'Ch24 — Red Team / Green Team cycle', fontsize=13, fontweight='bold', ha='center')
plt.tight_layout()
plt.savefig(base % (24, 24, 24), dpi=150); plt.close()
print('Ch24 done')

# ---- Ch26: pattern application diagram ----
fig, ax = plt.subplots(figsize=(8.5, 5.8))
ax.set_xlim(0, 14); ax.set_ylim(0, 6.2); ax.axis('off')
patterns = ['Canary\ndeploy', 'Autoscale', 'Prefix cache', 'P/D split', 'Circuit\nbreaker', 'ADR']
col = '#3a6ea5'
for i, p in enumerate(patterns):
    x = 0.4 + i*2.2
    ax.add_patch(FancyBboxPatch((x, 2.2), 1.8, 1.8, boxstyle='round,pad=0.02', fc=col, ec='none'))
    ax.text(x+0.9, 3.1, p, ha='center', va='center', color='white', fontsize=10, fontweight='bold')
ax.text(7, 5.3, 'Ch26 — applying the pattern library to a new architecture problem', fontsize=12.5, fontweight='bold', ha='center')
ax.text(7, 1.0, 'detect the situation → recall the pattern → apply with the ADR loop', fontsize=10, ha='center', color='#555')
plt.tight_layout()
plt.savefig(base % (26, 26, 26), dpi=150); plt.close()
print('Ch26 done')

print('batch part 3 complete')
