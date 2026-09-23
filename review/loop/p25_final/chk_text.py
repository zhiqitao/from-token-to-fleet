import pymupdf, re
pdf='/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
outdir='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_final'
d=pymupdf.open(pdf)
# extract text of pages 0-154
txt=[]
for i in range(0,155):
    txt.append(f"\n===PAGE {i+1}===\n"+d[i].get_text())
full="".join(txt)
open(f'{outdir}/slice_text.txt','w').write(full)
print("chars", len(full))

def show(pat, ctx=120, limit=6):
    n=0
    for m in re.finditer(pat, full, re.I):
        s=max(0,m.start()-ctx); e=min(len(full), m.end()+ctx)
        print("----", pat, "----")
        print(full[s:e].replace("\n"," "))
        n+=1
        if n>=limit: break
    if n==0: print(f"[no match: {pat}]")

print("\n### Ch3 KV formula")
show(r"KV.{0,20}2\s*[x×]\s*nlayers")
print("\n### full-MHA qualification")
show(r"full-MHA|full MHA", 150, 8)
print("\n### C = 17.5")
show(r"17\.5", 120, 10)
print("\n### C/W or C ÷ W or 2\.0")
show(r"C\s*[/÷]\s*W", 130, 5)
