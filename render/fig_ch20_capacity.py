import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ---- fig-20-2001: Fleet capacity vs host count (R27 rebuild) ----
# SINGLE panel, 6.1 x 5.4 in (print column), linear scale, explicit units.
# Three clearly-labelled series (all MODELLED / ANALYTICAL, never measured):
#   C_analytic(N) = N x 17/8.6         analytical host capacity (KV/service-time bound)
#   C_eff(N)      = 0.95 x C_analytic  efficiency-adjusted serving capacity
#   S(N)          = min(40, C_eff)     actually-served demand (offered load capped
#                                        at the canonical 40 rps peak)
# The two gaps are DIFFERENT things and are labelled as regions:
#   below saturation: C_analytic - C_eff = the ASSUMED ~5% throughput-efficiency
#                     derate (a modelling assumption, not a measurement);
#   above saturation: C_eff - S = UNUSED capacity caused by INSUFFICIENT OFFERED
#                     DEMAND (demand is capped at 40 rps) -- NOT scheduling
#                     overhead. Queueing / tail-latency penalties are NOT
#                     determined by this two-line calculation and are not drawn.
# Canonical markers kept: 21 hosts (ideal), 22 hosts (at 95%), 40 rps peak.
# Annotations sit in CLEAR regions (>= 8 pt) with leader arrows, off the curves.
# Canvas size and the print-size guard are unchanged from R26 so the house
# renderer's fig-20-2001 [H] placement arithmetic stays valid.

hosts = np.arange(0, 61)
whole_contexts = 17
service_time_s = 8.6
per_host_rps = whole_contexts / service_time_s          # 1.977 req/s/host
peak_rps = 40.0                                        # canonical peak demand
eff = 0.95                                             # throughput-efficiency derate

analytical = per_host_rps * hosts                       # C_analytic(N)
c_eff = eff * analytical                                # C_eff(N) = 0.95 * C_analytic
served = np.minimum(peak_rps, c_eff)                   # S(N) = min(40, C_eff)

fig, ax = plt.subplots(1, 1, figsize=(6.1, 5.4))
fig._hermes_print_sized = True   # print-size authored: regen must not re-boost/reflow

# ---- regions (drawn first, behind the curves) ----
# INK BUDGET (R27): the house C004 criterion is <15% whole-page ink at the
# any-250 threshold and is NOT loosened here. A solid background wash under the
# served curve covers ~19% of the artwork and alone pushed the figure page from
# 5.77% to 16.14%, i.e. over the criterion. The served wash is therefore kept
# at alpha=0.02, which renders at grey >= 250 (255 - 0.02*(255-65) = 251)
# and so adds ZERO counted ink, while the two GAP regions -- the actual subject
# of the figure -- keep visible fills (derate band ~2% of the artwork, UNUSED
# band ~13%, together ~5 page-points, page lands ~9.5% < 15%).
ax.fill_between(hosts, 0, served, color='#27408b', alpha=0.02,
                zorder=1)                                        # served demand
ax.fill_between(hosts, c_eff, analytical, color='#888', alpha=0.30,
                zorder=1)                                        # efficiency derate
ax.fill_between(hosts, peak_rps, c_eff, where=(c_eff >= peak_rps),
                color='#d62728', alpha=0.15, interpolate=True,
                zorder=1)                                        # UNUSED capacity

# ---- the three curves ----
ax.plot(hosts, analytical, '-', color='#888', lw=1.8, zorder=4,
        label='analytical host capacity C_analytic = N x 17/8.6 (req/s)')
ax.plot(hosts, c_eff, '--', color='#4a7ebb', lw=1.8, zorder=4,
        label='efficiency-adjusted capacity C_eff = 0.95 x C_analytic (req/s)')
ax.plot(hosts, served, '-', color='#1f4e9c', lw=2.8, zorder=5,
        label='actually-served demand S = min(40, C_eff) (req/s)')

# ---- canonical markers: 21 hosts (ideal) / 22 hosts (at 95%) / 40 rps ----
ax.axhline(peak_rps, color='#1f4e9c', ls='--', lw=1.0, alpha=0.8, zorder=3)
ax.axvline(21, color='#888', ls=':', lw=1.2, alpha=0.9, zorder=3)
ax.axvline(22, color='#1f4e9c', ls=':', lw=1.2, alpha=0.9, zorder=3)
ax.plot([21], [eff * per_host_rps * 21], 'o', ms=5, color='#888', zorder=6)
ax.plot([22], [peak_rps], 'o', ms=5, color='#1f4e9c', zorder=6)

# ---- placed labels (all >= 8 pt), each in a clear region, arrows off-curve ----
# Layout constraints found by R27 visual audit: the N=21 and N=22 vlines span the
# full panel height, so NO text may cross x in [21, 22]; every label therefore
# sits either left of x=21 or right of x=23, and the UNUSED block is kept inside
# the pink region (below C_eff, above 40 rps) with clearance from the right axis.
ax.text(0.8, 41.6, 'canonical peak = 40 rps', ha='left', va='bottom',
        fontsize=8.6, color='#1f4e9c', zorder=7)

ax.text(30, 18, 'actually-served demand region', ha='left', va='bottom',
        fontsize=8.6, color='#12386e', zorder=7,
        bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.75))

ax.text(31.5, 42, 'UNUSED capacity (N >= 22):\ninsufficient offered demand;\nS capped at 40 rps -\nnot scheduling overhead',
        ha='left', va='bottom', fontsize=8.6, color='#8c2d2d', zorder=7,
        bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.75))

ax.annotate('21 hosts (ideal) / 22 at 95%:\nserved demand plateaus at 40 rps',
            xy=(22, peak_rps), xytext=(23.6, 37),
            fontsize=8.6, color='#1a1a1a', ha='left', va='top', zorder=7,
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85),
            arrowprops=dict(arrowstyle='->', color='#555', lw=0.9))

ax.annotate('throughput-efficiency\nderate (~5%): C_eff =\n0.95 x C_analytic',
            xy=(52, eff * per_host_rps * 52 + 0.025 * per_host_rps * 52),
            xytext=(24, 92),
            fontsize=8.6, color='#333', ha='left', va='bottom', zorder=7,
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85),
            arrowprops=dict(arrowstyle='->', color='#555', lw=0.9))

ax.set_xlim(0, 60)
ax.set_ylim(0, 125)
ax.set_xlabel('Host count N (hosts)', fontsize=9)
ax.set_ylabel('Fleet rate (req/s)', fontsize=9)
ax.set_title('Fleet capacity vs host count - canonical workload\n(17 contexts / 8.6 s per host; analytical construction, not measured)',
             fontsize=9.0, fontweight='bold', color='#1a1a1a', loc='left')
ax.grid(alpha=0.3)
ax.legend(fontsize=8.6, loc='upper left', frameon=True, framealpha=0.9,
          edgecolor='#ccc')
ax.tick_params(labelsize=8.6)

fig.text(0.5, 0.015, '[ILLUSTRATIVE][DERIVED]', ha='center', fontsize=9, color='#444')

plt.tight_layout(rect=(0, 0.02, 1, 1))
import matplotlib as _mpl
# NOTE (R27): bbox_inches='tight' is deliberately NOT used. The house renderer
# applies trim=0 3.58 0 8.80 to this artwork (md_to_latex.fix_ch20_figure_
# placement), i.e. it strips 8.80 pt of white off the top and 3.58 pt off the
# bottom of the placed image. A tight crop leaves only pad_inches=0.05 in
# (3.6 pt) of white at the top, so the trim would cut into the title. Saving
# the plain 6.1 x 5.4 in canvas keeps the canonical 439.2 x 388.8 pt page
# (identical to R26) AND keeps >8.8 pt of white above the topmost artist.
with _mpl.rc_context({'pdf.fonttype': 42, 'ps.fonttype': 42}):
    plt.savefig('design/manuscript/chapter-20/figures/fig-20-2001.pdf', format='pdf')
# also emit a PNG (the build copies the .png when no sibling .pdf exists; keep both
# in sync so a stale PNG can never shadow the new vector)
plt.savefig('design/manuscript/chapter-20/figures/fig-20-2001.png', dpi=400)
plt.close()
print('wrote fig-20-2001 (R27: three labelled series + derate/unused/served regions, 21/22/40 markers)')