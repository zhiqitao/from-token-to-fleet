#!/usr/bin/env python3
"""Retry errored probes (429/500) after cooldown; then aggregate scores."""
import json, os, sys, time, glob, importlib.util
sys.path.insert(0,'/home/ubuntu/hermes-work/from-token-to-fleet/render/bench')
spec=importlib.util.spec_from_file_location('bf','/home/ubuntu/hermes-work/from-token-to-fleet/render/bench/bench_fleet.py')
bf=importlib.util.module_from_spec(spec)
import urllib.request, urllib.error
# prevent bench __main__ from running
bf.__name__='bf'
spec.loader.exec_module(bf)
bf.LOCAL_BASE, bf.LOCAL_MODEL = bf.load_local()

RESULTS='/home/ubuntu/hermes-work/from-token-to-fleet/render/bench/results'
max_rounds=int(sys.argv[1]) if len(sys.argv)>1 else 3
for rnd in range(max_rounds):
    pending=0
    for f in sorted(glob.glob(RESULTS+'/*.json')):
        d=json.load(open(f))
        mid=d['model']
        for p,r in d['probes'].items():
            if r['verdict']=='error':
                pending+=1
                spec2=bf.PROBES[p]
                img=None
                if spec2.get('image'):
                    if mid not in bf.VISION_MODELS: continue
                    img=__import__('base64').b64encode(open(bf.VISION_IMG,'rb').read()).decode()
                print(f'[retry r{rnd}] {mid} {p}',flush=True)
                res=bf.call(mid,spec2['prompt'],max_tokens=spec2['max_tokens'],image_b64=img,retries=2)
                verdict,detail=bf.grade(p,res)
                d['probes'][p]={'verdict':verdict,'detail':(detail or '')[:160],**{k:res[k] for k in ('ok','latency_s','completion_tokens','finish','error')}}
                if p=='draft' and res['ok']: d['probes'][p]['text']=res['content'][:2000]
                time.sleep(3)
        json.dump(d,open(f,'w'),indent=1)
    print(f'round {rnd}: {pending} errored probes remained',flush=True)
    if pending==0: break
    if rnd<max_rounds-1:
        print('cooling 120s before next round...',flush=True); time.sleep(120)
print('RETRY PASS DONE')
