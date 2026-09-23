import pymupdf, re
pdf='/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
outdir='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_final'
d=pymupdf.open(pdf)
full=open(f'{outdir}/slice_text.txt').read()

# find page of the C/W=18 passage
for i in range(0,155):
    if "C/W = 18 KV-resident" in d[i].get_text():
        print("C/W=18 passage on page", i+1)
# if not in 0-154, search whole doc
if not any("C/W = 18 KV-resident" in d[i].get_text() for i in range(0,155)):
    for i in range(0,307):
        t=d[i].get_text()
        if "C/W = 18" in t or ("= 2.1 req/s" in t and "18 KV-resident" in t):
            print("C/W=18 passage found on page", i+1, "OUTSIDE my slice" if i>154 else "")
            break

print("\n### FP8 per-token values 1.31 / 1.42 / 1.4")
def show(pat,ctx=130,limit=8):
    n=0
    for m in re.finditer(pat, full, re.I):
        s=max(0,m.start()-ctx); e=min(len(full),m.end()+ctx)
        print("----", pat)
        print(full[s:e].replace("\n"," "))
        n+=1
        if n>=limit:break
    if n==0: print(f"[no match {pat}]")
show(r"1\.31|1\.42|1\.4 MB",160,8)
print("\n### idealized vs realistic FP8")
show(r"idealiz|realistic FP8|53%|54%|byte-halving",150,8)
