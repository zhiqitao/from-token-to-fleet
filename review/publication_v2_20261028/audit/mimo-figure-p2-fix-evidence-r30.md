# MiMo figure P2 fix evidence — round 30 (2026-10-31)

Scope: the 5 P2 findings in `mimo-figure-vision-audit-r30.md`. Legibility /
clarity / geometry only — no number, data or caption-semantic change.
Generators edited in `render/`, assets regenerated via `render/regen_one.py`
(PNG + PDF, `pdf.fonttype=42`), copied to `render/latex/figures/`.

Gate: **min on-page label ≥ 8 pt** on every figure, **Type3 = 0**, zero
word-box overlaps (>0.15 IoU), vision re-read of each PNG.

---

## F001 — Fig A.4 (`fig-27-2702`, ch27, `render/fig_2702.py`)

**Finding:** white label text on band 3 `#4d8fc4` = 3.47:1 and band 7
`#6f9e5f` = 3.12:1 — WCAG AA fail.

**Fix:** `_text_color()` no longer uses the Rec.601 `lum > 145` heuristic. It
now composites the fill at the patch's `alpha=0.92` over the white page and
picks whichever of white / `#1a1a1a` gives the higher **real WCAG contrast**.
Bands 3 and 7 flip to dark ink; the other six keep their previous ink.

**Measured (sampled from the regenerated 350 dpi PNG, fill + ink pixels):**

| band | fill (composited) | ink | before | after |
|---|---|---|---|---|
| Across a fleet of models | (56,79,148) | white | 9.58 | **7.74** |
| Inside agent runtime | (74,121,172) | white | 5.31 | **4.54** |
| **Inside tools** | (91,152,200) | **dark** | **3.47 ✗** | **5.61 ✓** |
| Inside test-time search | (118,167,219) | dark | 6.33 | **6.90** |
| Inside post-training | (152,189,226) | dark | 8.37 | **8.88** |
| Inside MoE routing | (90,125,85) | white | 5.52 | **4.67** |
| **Inside attention** | (122,165,108) | **dark** | **3.12 ✗** | **6.15 ✓** |
| Inside weights | (162,205,147) | dark | 9.20 | **9.69** |

All 8 bands ≥ 4.5:1 (worst 4.54). Vision re-read: bands 3 and 7 now dark and
"clearly readable"; no band hard to read.

**min label = 8.0000 pt** · Type3 = 0 · overlaps = 0

---

## F002 — Fig 21.1 (`fig-21-2101`, ch21, `render/fig_ch21_pipeline.py`)

**Finding:** the green feedback loop's upper segment floats above `Eval` with
no arrowhead, while the caption promises "data/evaluation".

**Root cause:** the loop is one `FancyArrowPatch(path=…, arrowstyle='-|>')`.
With matplotlib's default `mutation_scale=1` a **path-based** arrowhead renders
at **0.40 × 0.40 pt** — invisible at print size (probe: `ax.annotate` renders
4.00 pt for the same style). So the drop into `Eval` existed but read as a bare
stub.

**Fix:** `mutation_scale=16` on the loop patch, and the final vertex moved from
`y+h` to `y+h-0.12` so the tip lands *inside* the box's padded top edge.

**Measured (PDF vector geometry):**

| | before | after |
|---|---|---|
| Eval arrowhead | 0.40 × 0.40 pt, tip **1.7 pt above** box top | **6.40 × 6.40 pt**, tip **0.63 pt inside** box top |
| Data arrowhead (unchanged) | 4.00 × 4.00 pt, tip 1.76 pt short | 4.00 × 4.00 pt, tip 1.76 pt short |

Vision re-read: "clearly visible, solid (filled) triangular arrowhead … tip
reaches and touches/enters the top border of the Eval box" → **ARROWHEAD
VISIBLE: YES, TIP ON BOX: YES.**

**min label = 8.0000 pt** · Type3 = 0 · overlaps = 0

---

## F003 — Fig 7.5 (`fig-07-0701`, ch07, `render/fig_ch7.py`)

**Finding:** the "9.5K ≈ 24.9 GB" arrow points at the 10K marker; 10K = 26.2 GB.

**Audit premise correction:** 9.5K **is** a plotted point — `ctx =
[1, 4, 9.5, 32, 128]`, and the marker measures at context **9.502 K** (page
x = 174.59; the 10K gridline is at 177.00). The annotation arrow's tip is at
x = 172.09, i.e. 0.5 pt inside the marker's left edge — it already targets the
9.5K marker. The defect is **perceptual**: on a log axis 9.5 sits only
**2.41 pt** left of the 10K gridline, so the marker reads as 10K.

Relabelling to "10K ≈ 26.2 GB" was rejected: it would introduce a number the
caption does not carry (ch07 says "≈24.9 GB at 9.5K") and break figure↔caption
consistency — a caption-semantic change, out of scope.

**Fix:** make the x-position explicit — a red dotted drop-line from the marker
to the axis plus a bold red `9.5K` label just above the axis.

**Measured:**

| | value |
|---|---|
| drop-line x | 174.59 = marker centre (offset **+0.00 pt**) |
| drop-line span | y 79.32 (marker) → 155.22 (axis) |
| `9.5K` label bbox | x 163.8–185.4, y 142.6–152.5 (above axis 155.22) |
| `10` tick label bbox | x 170.7–183.4, y 160.5–172.2 (below axis) |
| overlap with `10` tick | x-overlap only, **no y-overlap → clear** |
| overlap with any curve | none (empty strip below all four curves) |

Vision re-read: label verbatim **"9.5K"**; "the combination of (a) the line's
offset from the 10 gridline and (b) the literal '9.5K' text removes the
ambiguity"; "collides with neither" the `10` tick nor any curve.

**min label = 8.5000 pt** · Type3 = 0 · overlaps = 0

---

## F004 — Fig 23.1 (`fig-23-2301`, ch23, `render/fig_batch2.py`)

**Finding:** all four down-arrow connectors float in the gaps, touching neither
box.

**Fix:** the connector is now a single arrow spanning the **full** gap —
`xytext = y-0.02` (upper box's bottom edge) → `xy = y-0.29` (0.04 units *into*
the lower box), with `shrinkA=0, shrinkB=0` and `mutation_scale=10`. The
explicit shaft from the R27 fix is retained underneath.

**Measured (PDF vector geometry, all four gaps identical):**

| | before | after |
|---|---|---|
| shaft top → upper box bottom | +0.00 pt | **+0.00 pt** |
| shaft bottom → lower box top | +0.00 pt | **+0.00 pt** |
| arrowhead tip → lower box top | **−2.68 pt (floating)** | **−0.94 pt (inside the box)** |
| arrowhead size | 3.2 × 3.2 pt | 4.0 × 4.0 pt |

Vision re-read, per connector 1→2, 2→3, 3→4, 4→5: shaft starts at the upper
border **Yes**, tip reaches/enters the lower border **Yes**, floating **No** —
"None of the four connectors floats; there is no visible white gap."

**min label = 8.5000 pt** · Type3 = 0 · overlaps = 0

---

## F005 — Fig 16.1 (`fig-16-1601`, ch16, `render/fig_ch16_tco.py`)

**Finding:** price-sensitivity band `alpha=0.12` → Rec.601 luminance 0.92, so
it vanishes in grayscale.

**Fix:** `alpha 0.12 → 0.60` (a higher-contrast shade; no hatch needed — the
band already has two dotted boundary lines, and the INFEASIBLE region owns the
`///` hatch, so a second hatch would blur that distinction).

**Measured (sampled from the regenerated 350 dpi PNG):**

| | before | after |
|---|---|---|
| band RGB | ~(247,231,230) | **(217,136,128)** |
| Rec.601 luminance | **0.92** | **0.625** |
| gray level vs white 255 | 236 (Δ19) | **159 (Δ96)** |
| contrast vs white | 1.09 | **1.56** |

Vision re-read: "a continuous, translucent salmon/pink ribbon … reads
unambiguously as a shaded region, not as a faint or missing fill"; in grayscale
"a light-to-medium gray ribbon that is still distinguishable from the white
background (not too faint)"; grid lines, managed line, legend and every
annotation box still legible and not obscured.

**min label = 8.0000 pt** · Type3 = 0 · overlaps = 0

---

## Gate summary

| figure | min on-page label | Type3 | word overlaps | vision |
|---|---|---|---|---|
| fig-27-2702 (A.4) | **8.0000 pt** | 0 | 0 | pass |
| fig-21-2101 (21.1) | **8.0000 pt** | 0 | 0 | pass |
| fig-07-0701 (7.5) | **8.5000 pt** | 0 | 0 | pass |
| fig-23-2301 (23.1) | **8.5000 pt** | 0 | 0 | pass |
| fig-16-1601 (16.1) | **8.0000 pt** | 0 | 0 | pass |

`render/measure_fig.py` exits 1 on three of these. That is a float32 artifact,
not a real sub-8pt label: the PDF page width is stored as `439.20001220703125`
pt instead of `439.2`, so the tool computes `scale = 6.10 / 6.1000001695 =
0.9999999722` and reports `8.0 × 0.9999999722 = 7.999999778`. The authored size
is exactly 8.0000 pt and the figure is placed 1:1 (scale 1.0000 to 7 s.f.).
This affects every 6.1 in figure in the repo with an 8.0 pt minimum and is
unchanged from before this round.

## Asset shas (sha256, full)

| asset | before (HEAD) | after |
|---|---|---|
| fig-27-2702.pdf | `668184f2bbac92a17208cc9248f7ebc4955bae5c7e2b6ae49d029995fed8a9ac` | `c7e1fa6e442fedfb…` |
| fig-27-2702.png | `3ed3018665507bba836eb9641057ae849affa303c4ea57751fb8c7bf302e7d15` | `e0d2e18edf4dae84…` |
| fig-21-2101.pdf | `32ab6961fa367f9c95c0a3620d8dad5512a62fc8fc0c04c35f8cfb9a177a2561` | `d5f175bcca49af76…` |
| fig-21-2101.png | `078366104ec32f1d4b214575c61d7af43b96cdc300d076db228e5d7586741dfd` | `7aad78b94db59e6d…` |
| fig-07-0701.pdf | `c751c5fd755efade417e9bd83f75caadb9a40a64160f52336959164a0c16b0d2` | `efd70e267cb28c51…` |
| fig-07-0701.png | `697dc0bf3801906ac406edcb9dc07252d7504ef255f4ba4332b8daacd80f95df` | `1309606c21445c43…` |
| fig-23-2301.pdf | `85b5d7ee85003d58c118e39e930d631c3274b1393023acaba2c8ec923841036e` | `407151220bf87139…` |
| fig-23-2301.png | `6f35dbcc8bd51e76510f32bf3af4034cd0303acaa43e7ed175748f8e8339af66` | `b199efd50922cb64…` |
| fig-16-1601.pdf | `048608f39fc3f65dea8e261ad361fe2ad56d0e3b1fa24368aeeb8ac5c06739c4` | `bffacd82060699ad…` |
| fig-16-1601.png | `4e7215a430d5eb30068ddce4b7e44248c802182d8e87611e38690f0fd3488621` | `efe88e258745bfe0…` |

Full shas: `~/.hermes/profiles/muta/cache/scratch/r30_p2_shas.json`.
Every `render/latex/figures/` copy is byte-identical to its `design/` source.

## Files touched

- `render/fig_2702.py`, `render/fig_ch21_pipeline.py`, `render/fig_ch7.py`,
  `render/fig_batch2.py`, `render/fig_ch16_tco.py`
- `design/manuscript/chapter-{07,16,21,23,27}/figures/fig-*.{pdf,png}`
- `render/latex/figures/fig-*.{pdf,png}` (copies)
- this evidence file

**Not touched:** captions, chapter text, numbers, data, other figures, the
renderer, the root, no full-book build, no git commit, no delegation.

## Notes

- `fig-07-0702.pdf` was rewritten as a sibling of `fig_ch7.py`. Its content
  signature (text + drawing geometry) is **unchanged**:
  `ef42a0ad832a2914` before and after — only PDF metadata bytes differ.
- Pre-existing modifications to `design/manuscript/chapter-*.md` in the working
  tree are not from this round (figure scripts do not write chapter markdown).