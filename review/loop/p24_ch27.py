import pymupdf, re
doc = pymupdf.open('/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf')
for pno in range(0, doc.page_count):
    t = doc[pno].get_text()
    for kw in ['Chapter 27', 'chapter 27', 'The AI Solution Architect', 'Architect\u2019s Decision', '27.1', '25.1', '26.1', '24.1', '23.1']:
        if kw in t:
            print(f"p{pno+1}: contains '{kw}'")
            break
