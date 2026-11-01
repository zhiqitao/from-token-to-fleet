# P2 figure/plot fixes — independent review round (2026-10-31)

Scope: four findings (P2-04, P2-05, P2-07, P2-08) on Fig 11.3, Fig 16.1,
Fig 6.2, Fig 22.1. Only the affected generators, their regenerated assets
(`design/manuscript/chapter-*/figures/` + `render/latex/figures/`) and this
evidence were touched. **No number, datum or price was changed** — topology,
shading, annotation placement and caption structure only. No full-book build,
no git operations, no other figures/renderer.

Regeneration command (per figure, from repo root):

```
python3 render/regen_one.py render/fig_ch6_hist.py     # Fig 6.2
python3 render/regen_one.py render/fig_ch11_pd.py      # Fig 11.3
python3 render/regen_one.py render/fig_ch16_tco.py      # Fig 16.1
# Fig 22.1: caption-only finding (P2-08) -> generator NOT re-run, asset unchanged
```

`regen_one` uses `regen_figs._duo_savefig` (print-size exemption honoured via
`fig._hermes_print_sized`, PNG + vector PDF, `pdf.fonttype/ps.fonttype = 42`).
`fig_ch11_pd.py` previously wrote PNG only and set no font type; it now writes
PNG + PDF under the same `rc_context({'pdf.fonttype': 42, ...})` as the other
generators.

---

## 1. P2-04 — Fig 11.3 (generator `render/fig_ch11_pd.py`)

**Before:** one schematic = prefill 8×H100 host + decode 8×H100 host (an
inter-host link) with a single KV arrow; the caption quoted the on-node
450 GB/s NVLink number first and the 40 GB/s fabric second, so both bandwidths
hung off one ambiguous topology. No aggregate-budget caveat.

**After:** the figure is split into the two cases it actually describes:

* **(A) Within one NVLink domain** — one grey `8× H100 host` box containing a
  4-GPU PREFILL partition and a 4-GPU DECODE partition; KV arrow labelled
  **450 GB/s**; note `~35 GB ≈ 0.08 s (on-node)`.
* **(B) Across hosts (fabric)** — two separate boxes, each `PREFILL/DECODE` +
  `8× H100 host` with 8 GPU glyphs; KV arrow labelled **40 GB/s**; note
  `~35 GB ≈ 0.9 s (cross-host)`.
* Footer caveat (once, for both cases): `Caveat — aggregate KV migration at
  peak: 35 GB/request × 40 req/s = 1.4 TB/s of payload.` +
  `Per-request times assume an unshared link; 1.4 TB/s exceeds any single link above.`

**Caption** (`design/manuscript/chapter-11/chapter-11.md`) rewritten to name
both cases explicitly — "(A) within-NVLink-domain, on-node: … 450 GB/s …
(B) cross-host, over the fabric: … 40 GB/s …" — plus the caveat sentence
`35 GB/request × 40 req/s = 1.4 TB/s of payload`. All pre-existing qualifiers
(~35 GB / ~13K-token / 2.62 MB/token / §9.8 / §9.2 / ~1.08 s prefill /
[ILLUSTRATIVE][DERIVED]) preserved.

## 2. P2-05 — Fig 16.1 (generator `render/fig_ch16_tco.py`)

**Before:** `ax.loglog(req, cloud_line)` drew the flat $87.6K/month
(4,380 host-hours) line across the whole 1e4–1e8 volume axis, implying it can
serve every volume point, and it participated in the visual crossover set.

**After:** the cloud series is a **single marker** at the one priced operating
point — `ax.plot([req_month], [cloud_total], 'D')` at (6.24M, $87.6K) — with
a leader-annotated box `cloud $87.6K/mo (occupancy input) / priced at 6.24M
req/mo only`, and a legend entry `cloud $87.6K/mo @ 6.24M (occupancy input)`
using the diamond handle. It is no longer a curve and takes no part in the
crossover (self-host × managed API only). **One** noncomparability warning is
kept: the header `ILLUSTRATIVE SCENARIO — NOT APPLES-TO-APPLES (see Table
16-1 / Ch 16)`; the footer keeps only provenance (4,380 paid host-hours =
occupancy INPUT). Figure-spec comment in the manuscript updated to match.
`feasible max 24.96M` label bumped 8.0 → 8.1 pt (see §5).

**Caption** trimmed to the 3-part convention (see §4) and a labelled
**Technical note (Fig 16.1) — line definitions and the cloud marker** was
added immediately before the figure, carrying the moved derivation
(self-host = capex ÷ 60 mo + energy + staff/ops, zero-spare 21-host fleet;
managed API = input×$/1M + output×$/1M-out; utilization = served ÷
provisioned; cloud = 4,380 paid host-hours priced at 6.24M only; feasible
bound pointer). The feasible-bound derivation, frozen-fleet crossover and price
band were already in running text (§ "Which dimension the x-axis varies…",
"Feasible served-volume bound…") — no duplication added.

## 3. P2-07 — Fig 6.2 (generator `render/fig_ch6_hist.py`)

**Before:** `ax.axvspan(4.0, 6.0, alpha=0.08)` — only the ≥4 s tail shaded;
the 2–4 s SLO-violating region was unshaded (caption said so).

**After:**

* light band over the **entire** violating region: `axvspan(2.0, 6.2,
  facecolor='#c0392b', alpha=0.10, zorder=0)`;
* darker fill for the straggler cluster: `axvspan(4.5, 5.5, alpha=0.22)`;
* **darker hatch** for the 5 s cluster as a separate `facecolor='none'`,
  `edgecolor='#7b241c'`, `hatch='///'`, `linewidth=0.0` patch (a single
  `color=` kwarg overrides `edgecolor` and kills the hatch; patch-level alpha
  would fade it; `linewidth=0` removes the border rectangle so no line runs
  through the band label);
* new in-band label `SLO-violating region (> 2 s)` at x = 3.3 s.

**Caption** caveat updated: light band = full >2 s violating region, darker
hatch = the 5 s straggler cluster inside it, "shading marks violations of the
one 2 s SLO, not a second threshold".

## 4. P2-08 — caption trim, Fig 16.1 + Fig 22.1 (3-part convention)

Both captions now read **one-sentence takeaway / one line scope + provenance +
status / one critical caveat**, with derivation moved out:

* **Fig 16.1** — Takeaway: frozen 21-host self-host crosses the managed API at
  ~7.5M req/mo, so at canonical 6.24M self-host sits above the API. Scope:
  x-dimension (option A, fixed 40 rps peak, fixed 21-host zero-spare fleet),
  70B FP16 8×H100, 5-year amortization, $20.80/1K, 9.2K-in/300-out,
  [ILLUSTRATIVE][DERIVED] — "illustrative, not portable". Caveat: not
  apples-to-apples across demand levels; $87.6K is a paid-occupancy input
  priced only at 6.24M (marker, not a line), so break-even is a function of
  demand, not a fixed point. Moved: cost-line formulas, utilization definition,
  feasible-bound arithmetic → new **Technical note (Fig 16.1)** (the
  feasible-bound and frozen-fleet derivations were already in running text).
* **Fig 22.1** — Takeaway: quadratic term overtakes the linear term at ~53.4K
  tokens, so at 32K it is large but not yet dominant. Scope: LEFT = prefill
  FLOPs/request (2NL + 4·n_layers·L²·d), RIGHT = decode FLOPs/token (2N ≈
  1.4e-4 PFLOP/token, parameter term only), canonical 70B/80-layer/hidden-8,192
  (Ch 7), [ILLUSTRATIVE][DERIVED]. Caveat: different units, not directly
  comparable; full per-token decode also attends over the growing KV cache.
  Moved: the L\* = N/(2·n_layers·d) = 70 × 10⁹ / (2 × 80 × 8,192) ≈ 53.4K
  derivation → new **Technical note (Fig 22.1) — crossover derivation**
  (the 9.2K/128K ratios and unit note were already in the figure note below).

Essential qualifiers retained in both: illustrative/derived status, frozen-fleet
/ option-A x-dimension, zero-spare fleet, "not portable", "not directly
comparable", parameter-term-only decode, KV-attention-not-plotted.

---

## 5. Verification (all run 2026-10-31, repo root)

**Font-size gate** — `python3 render/measure_fig.py <4 PDFs>` → **rc 0,
MIN-ON-PAGE 8.10 pt** (natural width 6.100 in, scale 1.0000 for all four):

| figure | min on-page | authored | smallest span |
|---|---|---|---|
| fig-06-0602 | 8.50 pt | 8.50 | `(p99 still looks fine)` |
| fig-11-1103 | 8.20 pt | 8.20 | `4 GPUs` / `8× H100 host` |
| fig-16-1601 | 8.10 pt | 8.10 | `feasible max 24.96M` (was 8.00 → 7.9999 after the tight-bbox downscale; bumped to 8.1) |
| fig-22-2201 | 8.60 pt | 8.60 | `10²` |

**Type 3 fonts** — `pymupdf Page.get_fonts(full=True)` on all four PDFs in
*both* `design/.../figures/` and `render/latex/figures/`: font types are
subset TrueType (`DejaVuSans`, `DejaVuSans-Bold`, Type0/CID) → **Type3 = 0**.

**Layout probe** (scratch `check_fig_layout.py`: text-vs-box straddles,
text-text overlaps, canvas clipping) → fig-11-1103 **clean**; fig-06-0602 and
fig-16-1601 report only (a) the pre-existing `p50` label sitting on its own
line/bar (opaque white label box) and (b) `Annotation.get_window_extent()`
unioning the break-even leader arrow with the `canonical 6.24M req/mo` label —
geometry check shows the leader runs *below* that label for its whole length.

**`render/scan_all_figs.py`** (vector line-through / text-on-text scan):

* fig-11-1103: **0 candidates** (arrow tips pulled clear of the `prompt` /
  `generated tokens` anchors).
* fig-06-0602: 1 — the p50 vline through its own white-boxed label (pre-existing).
* fig-16-1601: candidates are (i) minor **gridlines** behind the frameless
  legend and behind the annotation's opaque white box, (ii) `1e4` vs `1e3`
  axis-corner tick labels. Vision on 3×/4× crops: legend rows clean, no line
  strikes the annotation text (white fill masks the grid), corner labels
  adjacent but separated by white space → no real collision.
* fig-22-2201: 35 candidates, figure untouched this round (pre-existing
  leader-lines through their own labels).

**Vision re-inspection** of the regenerated PNGs (fig-11-1103, fig-06-0602,
fig-16-1601 + 3 crops): no text-text overlap, no text crossing a box border,
no edge clipping; panel A confirmed as one host split 4+4, panel B as two
separate 8-GPU hosts; light >2 s band + hatched 4.5–5.5 s band confirmed.

**Repo gates (read-only, no build):** `check_tables.py` rc 0,
`check_md_leaks.py` rc 0, `check_regressions.py` rc 0 (canonical numbers
unchanged; `L* = 53405.8` matches the caption's ≈53.4K).

**Asset identity:** `design/manuscript/chapter-{06,11,16}/figures/*` and
`render/latex/figures/*` are byte-identical (sha256 match) for the three
regenerated figures.

## 6. sha256 before → after

| asset | before | after |
|---|---|---|
| fig-06-0602.pdf | `a15382673c3b7b6a6388d3795d8e9171ff1fd9bd8f547976652f8e560b36c6b5` | `feeab9247249b6434044f2dd43dc2fe4c2a67bafe3d0945450759bf9d08ef010` |
| fig-06-0602.png | `4559cd97b3740f69f8d3371f65d0db0b55f9a88dfc8414ede56065b70cb4b1d1` | `1223adf6a1abd1713b9a59e82c282b0ddb2ce124180423bad01e0b215e3b3d97` |
| fig-11-1103.pdf | `90dab086fb2726f78f6016c69f44b9e36b6a97b4c9dc34f48a0b888b71d5432c` | `65acb9a26065824cee685c72e2f18d0bb8eadf7f803b075832e8ee6fb0fa4ef3` |
| fig-11-1103.png | `53aecbb75559686c6e20b2ed00cd35314334d516f17b9ef999e9035e98aa88fc` | `343bfc00764f1c40d16c4c1737769db96c3c8feff6ba4032de2d2386b8d0cda4` |
| fig-16-1601.pdf | `bffacd82060699ad94b7c4854cb759017119183973360bd429854ef9ac57c790` | `5bce1bd1944e3f56081362e0bb774005b552698d65a10e1e5a7c2cde6e127b9a` |
| fig-16-1601.png | `efe88e258745bfe0f7d2fa4c6acfb0d0aed641ad7a710b867ea904afbcf65755` | `1b0f3a1ff19d405feab3965475f61d4bf4fc44504e517403f5aceb5551e48320` |
| fig-22-2201.pdf | `0c3d6077de5e07d6267a5bee9332c6448e77f891e39fb470d00f5becf6cb1aa7` | unchanged (caption-only finding) |
| fig-22-2201.png | `1f0a9a92730d08c7e008452020f42c96d9a05d21032031bc47f472d16bb2c708` | unchanged (caption-only finding) |

## 7. Files changed

Generators: `render/fig_ch11_pd.py`, `render/fig_ch16_tco.py`,
`render/fig_ch6_hist.py` (`fig_ch22_divergence.py` untouched — P2-08 is a
caption finding).
Assets: `design/manuscript/chapter-{06,11,16}/figures/fig-*.{png,pdf}` and the
matching copies in `render/latex/figures/`.
Captions/notes: `design/manuscript/chapter-06/chapter-06.md` (Fig 6.2 caveat),
`chapter-11/chapter-11.md` (Fig 11.3), `chapter-16/chapter-16.md` (Fig 16.1
caption + technical note + figure-spec comment), `chapter-22/chapter-22.md`
(Fig 22.1 caption + technical note).
Evidence: this file.

## 8. Not fixed / out of scope (stated, not hidden)

1. **`render/latex/chapters/ch{06,11,16,22}.tex` still carry the old caption
   alt-text.** Those files are produced by `render/latex/md_to_latex.py`, which
   regenerates every chapter (a full-book build step, excluded by the task).
   The new captions reach the built PDF on the next `bash render/build.sh`.
2. **`render/latex/figures/fig-22-2201.{png,pdf}` differ from the design
   copies** — a pre-existing divergence (P2-08 required no regeneration, so no
   asset was rewritten); `md_to_latex.py` re-copies at build time.
3. **Pre-existing benign scan flags left in place**: fig-06 `p50` line through
   its own opaque label; fig-22 leader lines through their own labels;
   fig-16 frameless-legend gridlines and axis-corner tick adjacency (all
   vision-confirmed as non-collisions, none introduced this round).
4. **Ch 11 running text** ("transferring KV across via the fabric") was left
   as written: it describes case (B) and the figure/caption now name both
   cases explicitly; running-text edits were outside the assigned scope.