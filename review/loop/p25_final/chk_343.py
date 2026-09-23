import pymupdf, re
pdf='/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
outdir='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_final'
d=pymupdf.open(pdf)
full=open(f'{outdir}/slice_text.txt').read()
def show(pat,ctx=200,limit=4,text=full):
    n=0
    for m in re.finditer(pat, text, re.I):
        s=max(0,m.start()-ctx); e=min(len(text),m.end()+ctx)
        print("----",pat)
        print(text[s:e].replace("\n"," "))
        n+=1
        if n>=limit:break
    if n==0: print(f"[no match {pat}]")
print("### 3.4.3 context")
show(r"3\.4\.3|Why MoE saves compute",220,3)
print("### 256 KB 7B")
show(r"256 KB",220,4)
