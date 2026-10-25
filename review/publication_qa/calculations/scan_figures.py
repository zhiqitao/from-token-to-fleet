"""Automated figure inventory: reconcile each captioned figure with its PDF page,
embedded source, and effective print resolution. Writes figure_ledger_auto.csv.
Run: python3 review/publication_qa/calculations/scan_figures.py <pdf>
"""
import sys, pymupdf, re, csv, os

PDF = sys.argv[1] if len(sys.argv) > 1 else "render/build/from-token-to-fleet-v20260913.pdf"
doc = pymupdf.open(PDF)
full_pages = [doc[i].get_text() for i in range(len(doc))]

# Detect figure occurrences: captions "Figure N..." or "Fig N..."
fig_re = re.compile(r'(?:FIGURE|Fig\.?)\s*([\dA-Z][\w\-\.]*)', re.I)
# Also the figure image placements (embedded rasters)
rows = []
seen_ids = set()
for pno, txt in enumerate(full_pages):
    # raster images on this page
    imgs = doc[pno].get_images(full=True)
    for img in imgs:
        xref = img[0]
        try:
            pix = pymupdf.Pixmap(doc, xref)
            wpx = pix.width
        except:
            continue
        for r in doc[pno].get_image_rects(xref):
            w_in = r.width / 72.0
            if w_in <= 0.1:
                continue
            ppi = wpx / w_in
            rows.append({
                "pdf_page": pno+1, "xref": xref, "px_w": wpx, "place_in": round(w_in,2),
                "eff_ppi": round(ppi,0), "raster": "yes",
            })
# captions with "Figure" text
for pno, txt in enumerate(full_pages):
    for m in fig_re.finditer(txt):
        fid = m.group(1)
        rows.append({"pdf_page": pno+1, "caption_id": fid, "text_caption": "yes",
                     "px_w":"", "place_in":"", "eff_ppi":"", "raster":"caption"})

with open("review/publication_qa/figure_ledger_auto.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=["pdf_page","caption_id","xref","px_w","place_in","eff_ppi","raster","text_caption"])
    w.writeheader()
    for r in rows:
        w.writerow({k:r.get(k,"") for k in w.fieldnames})

print("figures/assets rows:", len(rows))
# summary of low-ppi rasters
lows=[r for r in rows if r.get("eff_ppi") and float(r["eff_ppi"])<300]
print("raster assets <300 ppi:", len(lows))
for l in lows[:30]:
    print("  p",l["pdf_page"],"ppi",l["eff_ppi"],"w_in",l["place_in"])
print("wrote review/publication_qa/figure_ledger_auto.csv")
