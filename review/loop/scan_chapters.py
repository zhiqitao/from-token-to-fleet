import pymupdf, re
d = pymupdf.open('/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf')
pat = re.compile(r'^(chapter|CHAPTER|PART)\s+([IVX]+|\d+)\b')
for i in range(0, d.page_count):
    t = d[i].get_text()
    for l in t.split('\n'):
        s = l.strip()
        if pat.match(s) and len(s) < 60:
            print(f"pdf {i}: {s}")
            break
