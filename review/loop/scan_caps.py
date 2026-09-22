import pymupdf, re
d = pymupdf.open('/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf')
cap = re.compile(r'(Figure|图)\s*(?:\d+\.\d+|\d+)\b', re.I)
for i in range(0,158):
    pg = d[i]
    t = pg.get_text()
    hits = [l.strip() for l in t.split('\n') if cap.search(l)]
    if hits:
        print(f"PDF page {i}: {hits}")
