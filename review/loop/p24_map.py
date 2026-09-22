import pymupdf, re
doc = pymupdf.open('/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf')
print("page count:", doc.page_count)
for pno in range(155, 309):
    page = doc[pno]
    text = page.get_text()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    heads = [l for l in lines[:4] if re.search(r'(Chapter|PART|Appendix|^[0-9]+\s)', l)]
    caps = [l for l in lines if re.match(r'^(Figure|Table)\s', l)]
    tag = " | ".join(heads[:2]) if heads else ""
    if any('Chapter' in l or 'Appendix' in l or 'PART' in l for l in lines) or caps:
        print(f"p{pno+1}: {tag}   ::caps::{ ' ;; '.join(caps) }")
