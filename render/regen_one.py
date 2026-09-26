#!/usr/bin/env python3
"""regen_one.py — run ONE figure script through the regen pipeline (writes PNG+PDF).

Usage: python3 render/regen_one.py <script_path>
Uses regen_figs._duo_savefig so print-sized exemption, font scaling and Type-42
PDF embedding all apply identically to a full regen.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import regen_figs as R
import matplotlib.pyplot as plt

SCRIPT = sys.argv[1] if len(sys.argv) > 1 else None
if not SCRIPT:
    print("usage: regen_one.py <script_path>"); sys.exit(1)

R._scaled_fignums.clear()
plt.savefig = R._duo_savefig
src = open(SCRIPT, encoding="utf-8").read()
ns = {"__name__": "__main__", "__file__": SCRIPT}
try:
    exec(compile(src, SCRIPT, "exec"), ns)
except SystemExit:
    pass
finally:
    plt.close("all")
print("ONE-DONE", os.path.basename(SCRIPT))
