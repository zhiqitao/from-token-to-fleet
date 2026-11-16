import os, re, json, glob, difflib

ROOT="/home/ubuntu/hermes-work/from-token-to-fleet/design/manuscript"
FILES=sorted(glob.glob(ROOT+"/**/*.md", recursive=True))

def norm(s):
    s=s.replace("\u2019","'").replace("\u2018","'").replace("\u201c",'"').replace("\u201d",'"')
    s=s.replace("\u2014","-").replace("\u2013","-").replace("\u2212","-").replace("\u00a0"," ")
    s=re.sub(r"[*_`~]","",s)
    s=re.sub(r"\s+"," ",s)
    return s.lower()

DOCS={}
for f in FILES:
    raw=open(f, encoding="utf-8").read()
    DOCS[f]=(raw, norm(raw))

def find(clause, maxhits=3, win=380):
    n=norm(clause)
    out=[]
    for f,(raw,nraw) in DOCS.items():
        idx=nraw.find(n)
        if idx>=0:
            out.append(("EXACT", f, raw, idx))
            if len(out)>=maxhits: break
    if not out:
        # try progressively shorter anchors
        words=n.split()
        for L in (12,9,6,5):
            if len(words)<=L: continue
            for start in range(0, max(1,len(words)-L+1), max(1,L//2)):
                anchor=" ".join(words[start:start+L])
                for f,(raw,nraw) in DOCS.items():
                    idx=nraw.find(anchor)
                    if idx>=0:
                        out.append((f"ANCHOR{L}", f, raw, idx)); break
                if out: break
            if out: break
    res=[]
    for kind,f,raw,idx in out:
        # map normalized idx to raw approx: just search a raw window by using the first 40 chars' words
        # simple: take raw slice around a rough proportional position
        pos=int(idx*len(raw)/max(1,len(norm(raw))))
        a=max(0,pos-win); b=min(len(raw), pos+win*2)
        res.append({"kind":kind,"file":f.replace(ROOT+"/",""),"excerpt":raw[a:b]})
    return res

def show(clause, **kw):
    print("#"*80)
    print("CLAUSE:", clause[:150])
    r=find(clause, **kw)
    if not r:
        print("  >>> NOT FOUND")
    for x in r[:1]:
        print(f"  [{x['kind']}] {x['file']}")
        print(x['excerpt'].replace("\n"," \u00b6 "))
