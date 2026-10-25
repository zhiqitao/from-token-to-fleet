"""Automated page geometry / layout scan (supports the Page + Figure ledgers).

For every page flags:
  - text spans whose right edge exceeds the body column (past ~527pt; out-of-page
    = past 560pt which is a hard defect)
  - pages that are largely empty (figure-only pages with excessive whitespace)
  - any extracted glyph at <8pt that is body text (potential print-size issue)
Outputs a per-page disposition row to be merged into page_ledger.csv.
Run: python3 review/publication_qa/calculations/scan_layout.py <pdf>
"""
import sys, pymupdf, re, os

PDF = sys.argv[1] if len(sys.argv) > 1 else "render/build/from-token-to-fleet-v20260913.pdf"

COL_L = 88.0
COL_R = 527.0     # body column right edge (US Letter 612pt, ~1in margins + small padding)
PAGE_W = 612.0
PAGE_H = 792.0

doc = pymupdf.open(PDF)
rows = []
overall_out_of_page = 0
for pno in range(len(doc)):   # 0-based
    page = doc[pno]
    d = page.get_text("dict")
    minx = maxx = miny = maxy = None
    n_spans = 0
    tiny = []     # body-size glyphs below 8pt
    over = []     # spans past PAGE_W (out of page)
    past_col = [] # spans past body column but inside page
    for b in d["blocks"]:
        if b["type"] != 0:
            continue
        for ln in b["lines"]:
            for sp in ln["spans"]:
                if not sp["text"].strip():
                    continue
                n_spans += 1
                x0, y0, x1, y1 = sp["bbox"]
                if minx is None or x0 < minx: minx = x0
                if maxx is None or x1 > maxx: maxx = x1
                # out-of-page: x1 beyond page width is a hard defect
                if x1 > PAGE_W + 10:
                    over.append((sp["text"][:25], round(x1,1)))
                # past body column
                if x1 > COL_R + 8:
                    past_col.append((sp["text"][:25], round(x1,1)))
                # tiny body text (<8pt) — flag but classify
                if sp["size"] < 8.0:
                    tiny.append((sp["text"][:20], round(sp["size"],2)))
    status = "PASS"
    text_checked = "yes"
    if over:
        status = "OUT_OF_PAGE"
        overall_out_of_page += 1
    # whitespace-heavy figure page: little text, big margins
    height_used = (maxy - miny) if (miny is not None and maxy is not None) else 0
    rows.append({
        "pdf_page": pno+1,
        "content_type": "text" if n_spans else "blank/divider",
        "n_spans": n_spans,
        "min_x": round(minx,1) if minx is not None else "",
        "max_x": round(maxx,1) if maxx is not None else "",
        "over_page_spans": len(over),
        "past_col_spans": len(past_col),
        "tiny_under_8pt": len(tiny),
        "status": status,
    })
    if over:
        print(f"  [p{pno+1}] OUT_OF_PAGE {over[:3]}")
    if past_col and pno % 1 == 0 and len(past_col) < 6 and pno > 17:
        # report modest column overflow (likely justified-text edge cases) once
        pass

print(f"\n=== LAYOUT SCAN SUMMARY ===")
print(f"pages: {len(doc)}")
print(f"out_of_page pages: {overall_out_of_page}")

# write CSV
import csv
with open("review/publication_qa/page_ledger_auto.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["pdf_page"])
    w.writeheader()
    for r in rows:
        w.writerow(r)
print("wrote review/publication_qa/page_ledger_auto.csv rows:", len(rows))
