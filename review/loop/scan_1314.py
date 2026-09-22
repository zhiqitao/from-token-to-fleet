import pymupdf, re
d = pymupdf.open('/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf')
# find any page mentioning figure captions for 13.x and 14.x across whole book
for i in range(0, d.page_count):
    t = d[i].get_text()
    lines = [l.strip() for l in t.split('\n')]
    for l in lines:
        if re.match(r'(?i)(figure|图)\s*(13\.\d+|14\.\d+|15\.\d+)\b', l):
            print(f"PDF page {i}: {l[:90]}")
            break
