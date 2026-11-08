#!/usr/bin/env python3
"""Inventory + target-page locator for the built book PDF (render venv python)."""
import pymupdf
import re

d = pymupdf.open("render/build/from-token-to-fleet-v20260913-plain.pdf")
print("pages:", d.page_count)
toc = d.get_toc()
print("TOC entries:", len(toc))
chap = [t for t in toc if re.match(r"^(Chapter|Appendix|Part)\b", t[1])]
print("chapter/part-level TOC:", len(chap))

figs, tabs = set(), set()
targets = ["Fig 4.1", "Fig 7.6", "Fig 8.2", "Table 12-1", "Table 12-2",
           "Table 17-2", "Fig 19.2", "Fig 19.3", "Fig 1.1", "Fig 1.2", "Fig A.2"]
loc = {}
for i, pg in enumerate(d):
    t = pg.get_text()
    figs.update(m.group(0) for m in re.finditer(r"Fig [0-9A-Z]+\.[0-9]+", t))
    tabs.update(m.group(0) for m in re.finditer(r"Table [0-9A-Z]+-[0-9]+", t))
    for tg in targets:
        if tg in t and tg not in loc:
            loc[tg] = i + 1
print("unique figure ids seen:", len(figs))
print("unique table ids seen:", len(tabs))
print("target first pages:", loc)
print("first page labels:", [d[i].get_label() for i in range(0, 14)])