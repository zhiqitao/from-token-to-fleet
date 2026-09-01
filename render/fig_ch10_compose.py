# ---- fig-10-1002: Composing the dimensions (DP x TP x PP + EP all-to-all) ----
# The Matplotlib version had text-overlapping-block defects (pink "all-to-all"
# caption over the EP blocks; green "PP flow" caption over the DP/TP area) that
# required a redraw. This figure is now produced by the Archify pipeline (see
# render/archify/ch10-compose.json -> design/manuscript/chapter-10/figures) and
# checked in as fig-10-1002.{png,pdf} directly.
#
# Do NOT regenerate via matplotlib: this generator is disabled so regen_figs.py
# cannot clobber the Archify-rendered asset.
import os, sys
if os.environ.get('FIG_CH10_COMPOSE_ALLOW') != '1':
    print('fig-10-1002: Archify-rendered asset; matplotlib generator disabled (set FIG_CH10_COMPOSE_ALLOW=1 to force)')
    sys.exit(0)
