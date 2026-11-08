#!/usr/bin/env python3
"""MiMo c4: chunk too big for one call (65536 truncation at max/high/medium).
Split at the nearest chapter boundary and review each half at medium."""
import os, re, sys, json, importlib.util
os.chdir("/home/ubuntu/hermes-work/from-token-to-fleet")
spec=importlib.util.spec_from_file_location("rl","render/review_loop.py")
rl=importlib.util.module_from_spec(spec); spec.loader.exec_module(rl)
chunks=rl.build_chunks()
c=chunks[4]
mid=len(c)//2
# nearest chapter boundary (\n# heading or \n\n--- or file start marker) to mid
bounds=[m.start() for m in re.finditer(r"\n(?=#{1,3} )",c)]
b=min(bounds,key=lambda x:abs(x-mid)) if bounds else mid
h1,h2=c[:b],c[b:]
print("split at",b,"halves:",len(h1),len(h2),flush=True)
os.environ["REVIEW_EFFORT"]="medium"
model="MiMo-V2.6-Flash-RL"
outs=[]
for hi,h in enumerate([h1,h2]):
    prompt=rl.PROMPT_V1+"\n\n"+rl.TEXT_TASK+h
    out=rl.chat(model,prompt)
    print(f"half {hi}: {len(out)} chars",flush=True)
    outs.append(out)
# combine into ONE json array file: parse each, concat
arr=[]
for o in outs:
    arr.extend(rl.parse_issues(o))
fp="review/loop_v3/round_1/text_%s_c4.json"%model
open(fp,"w",encoding="utf-8").write(json.dumps(arr,ensure_ascii=False,indent=1))
print("wrote",fp,"issues:",len(arr),flush=True)
