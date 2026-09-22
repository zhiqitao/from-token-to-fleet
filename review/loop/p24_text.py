import pymupdf
doc = pymupdf.open('/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf')
with open('/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p24_text_156_309.txt','w') as f:
    for pno in range(155,309):
        f.write(f"\n===== PDFPAGE {pno+1} =====\n")
        f.write(doc[pno].get_text())
print("done")
