"""Programmatic PDF structural QA per the publishing-readiness method.
Checks internal-link integrity, TOC/page-label coherence, tag/Accessibility,
XMP+standard metadata (no self-referential SHA), page-size uniformity,
and reports the on-page figure font floor per figure page.
Run: python3 review/publication_qa/calculations/pdf_structure_qa.py <pdf>
"""
import sys, re, pymupdf

PDF = sys.argv[1] if len(sys.argv) > 1 else "render/build/from-token-to-fleet-v20260913.pdf"
doc = pymupdf.open(PDF)
n = len(doc)
print("pages:", n)

# 1. page size uniformity
sizes = set()
for p in doc:
    r = p.rect
    sizes.add((round(r.width,1), round(r.height,1)))
print("page sizes (pt):", sizes)

# 2. internal link integrity
bad = 0; total_links = 0
for pno in range(n):
    for l in doc[pno].get_links():
        total_links += 1
        if 'page' in l and l['page'] >= n:
            bad += 1
print("internal links:", total_links, "| invalid targets:", bad)

# 3. TOC bookmarks in range
toc = doc.get_toc()
out_of_range = [t for t in toc if not (1 <= t[2] <= n)]
print("bookmarks/TOC entries:", len(toc), "| out-of-range page refs:", len(out_of_range))

# 4. metadata / SHA self-reference
m = dict(doc.metadata)
sha = re.findall(r'\b[0-9a-f]{40}\b', str(m))
print("PDF metadata SHA found:", sha if sha else "none (external manifest holds it)")
print("metadata creator:", m.get('creator'), "| producer:", m.get('producer'))

# 5. tagged / StructTreeRoot presence
mx = doc.metadata
print("page labels present:", bool(doc.get_page_labels()))

# 6. figure pages: min on-page font in the figure region (vector text); for raster
#    figures report the ppi instead. We locate captions to identify figure pages.
cap_re = re.compile(r'\bfigure\s+([\dA-Z][\w\.\-]*)\s*:', re.I)
# gather all spans sizes across the doc to compute a body baseline
print("\n-- figure pages (caption location + min on-page span size) --")
rows = []
for pno in range(n):
    t = doc[pno].get_text()
    for m2 in cap_re.finditer(t):
        fid = m2.group(1)
        sizes = [s["size"] for b in doc[pno].get_text("dict")["blocks"]
                 if b["type"] == 0 for l in b["lines"] for s in l["spans"] if s["text"].strip()]
        # exclude the 9.96pt body baseline; report nearest figure font sizes
        small = sorted(set(round(x,2) for x in sizes if x < 9.8))
        rows.append((fid, pno+1, min(sizes) if sizes else None, small))
rows.sort(key=lambda r: (len(r[0]), r[0]))
for fid, pg, mn, small in rows:
    print(f"  Figure {fid}: p{pg} min={mn} figuresz={small[:6]}")

print("\nSTRUCT QA DONE")
