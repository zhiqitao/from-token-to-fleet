import pymupdf, re
pdf='/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
outdir='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_final'
d=pymupdf.open(pdf)
full=open(f'{outdir}/slice_text.txt').read()

def show(pat,ctx=150,limit=6,text=full):
    n=0
    for m in re.finditer(pat, text, re.I):
        s=max(0,m.start()-ctx); e=min(len(text),m.end()+ctx)
        print("----", pat)
        print(text[s:e].replace("\n"," "))
        n+=1
        if n>=limit:break
    if n==0: print(f"[no match {pat}]")

print("### Fig 10.2->table: search 'parallelization' strategy table")
show(r"WHAT SPLIT|What it splits|strategy.{0,30}partitioned|CP.{0,5}context",180,5)
print("### host/node/instance usage")
show(r"node\b|H100 instance|instance\b",120,10)
