import pymupdf, re
doc = pymupdf.open('/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf')
for pno in range(270, 309):
    page = doc[pno]
    text = page.get_text()
    lines=[l.strip() for l in text.splitlines() if l.strip()]
    # first few non-empty lines = running head area
    head = " | ".join(lines[:2]) if lines else ""
    # detect chapter/appendix heading
    mark = [l for l in lines if re.match(r'^(Chapter\s+\d+|Appendix\s+[A-Z]|PART)', l)]
    print(f"p{pno+1}: HDR[{head[:60]}] MARK:{mark[:1]}")
