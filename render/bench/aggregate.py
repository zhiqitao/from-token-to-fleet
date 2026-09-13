#!/usr/bin/env python3
"""Aggregate bench results + LLM-judge the drafts with 2 judges (local GLM + zen nemotron-ultra)."""
import json, os, glob, importlib.util, sys, time
sys.path.insert(0,'/home/ubuntu/hermes-work/from-token-to-fleet/render/bench')
spec=importlib.util.spec_from_file_location('bf','/home/ubuntu/hermes-work/from-token-to-fleet/render/bench/bench_fleet.py')
bf=importlib.util.module_from_spec(spec); bf.__name__='bf'; spec.loader.exec_module(bf)
bf.LOCAL_BASE, bf.LOCAL_MODEL = bf.load_local()

RESULTS='/home/ubuntu/hermes-work/from-token-to-fleet/render/bench/results'
rows_all=json.load(open(RESULTS+'/_aggregate.json')) if os.path.exists(RESULTS+'/_aggregate.json') else None
rows = rows_all if isinstance(rows_all,list) and rows_all and isinstance(rows_all[0],dict) and 'model' in rows_all[0] else []
if len(rows)>30:  # corrupted double-append; keep one row per model (latest wins)
    seen={}
    for r in rows: seen[r['model']]=r
    rows=list(seen.values())
fresh=[]
for f in sorted(glob.glob(RESULTS+'/*.json')):
    if '_aggregate' in f: continue
    d=json.load(open(f))
    mid=d['model']
    P=d['probes']
    def v(p): return P.get(p,{}).get('verdict','-')
    def lat(p): return P.get(p,{}).get('latency_s')
    def tok(p): return P.get(p,{}).get('completion_tokens')
    obj=['json','math','codefix','needle','safety']
    passed=sum(1 for p in obj if v(p)=='pass')
    errored=sum(1 for p in obj if v(p)=='error')
    avail=5-errored  # out of 5 attempted-objective probes actually returning an answer
    vis=v('vision')
    rows.append({'model':mid,'obj_pass':f'{passed}/5','errored':errored,
        'json':v('json'),'math':v('math'),'codefix':v('codefix'),'needle':v('needle'),'safety':v('safety'),
        'vision':vis,'lat_json':lat('json'),'lat_draft':lat('draft'),'tok_draft':tok('draft'),
        'draft_text':P.get('draft',{}).get('text','')})
# preserve prior judgments on re-run
prev={r['model']:r.get('judge') for r in rows if r.get('judge')}
for r in rows:
    if r['model'] in prev and not r['draft_text'] is None:
        # only keep prev judge if the draft text is unchanged
        old=[x for x in (rows_all or []) if isinstance(x,dict) and x.get('model')==r['model']]
        if old and old[0].get('draft_text')==r['draft_text'] and old[0].get('judge'):
            r['judge']=old[0]['judge']
json.dump(rows,open(RESULTS+'/_aggregate.json','w'),indent=1)

# LLM-judge drafts: 2 judges, 1-10 on substance+style for a LinkedIn book intro
judge_prompt_tmpl='''You are an editorial judge. Rate this 3-sentence LinkedIn post intro for a technical book called "From Token to Fleet" (LLM systems scaling from a single token to GPU fleets).
Audience: senior engineers. Criteria: substance (specific, no hype), tone (confident engineer, no emojis), craft (would a busy engineer stop scrolling?).
Draft:
<<<
{text}
>>>
Reply with ONLY: SCORE=<1-10>; ONE_LINE=<why>'''

judges=[('local',bf.LOCAL_MODEL),('zen:nemotron-3-ultra-free','nemotron-3-ultra-free')]
import concurrent.futures as _cf
todo=[r for r in rows if r['draft_text'] and not r.get('judge')]
print(f'judging {len(todo)} drafts x {len(judges)} judges (parallel x4)',flush=True)
def _judge_one(args):
    r,tag,jmodel=args
    rr=bf.call(('local:'+jmodel) if tag=='local' else ('zen:'+jmodel), judge_prompt_tmpl.format(text=r['draft_text']), max_tokens=4000, retries=1)
    import re as _re
    if rr['ok']:
        m=rr['content']
        mm=_re.search(r'SCORE\s*=\s*(\d+)',m)
        one=_re.search(r'ONE_LINE\s*=\s*(.+)',m)
        return r['model'],{'judge':tag,'score':int(mm.group(1)) if mm else None,'why':(one.group(1).strip()[:120] if one else m[:120])}
    return r['model'],{'judge':tag,'score':None,'why':'ERR '+str(rr['error'])[:80]}
jobs=[(r,tag,jmodel) for r in todo for tag,jmodel in judges]
with _cf.ThreadPoolExecutor(max_workers=4) as ex:
    for model,jres in ex.map(_judge_one,jobs):
        row=[x for x in rows if x['model']==model][0]
        row.setdefault('judge',{'scores':[],'avg':None})['scores'].append(jres)
for r in todo:
    j=r.get('judge') or {'scores':[],'avg':None}
    valid=[s['score'] for s in j['scores'] if s['score']]
    j['avg']=round(sum(valid)/len(valid),1) if valid else None
    r['judge']=j
json.dump(rows,open(RESULTS+'/_aggregate.json','w'),indent=1)

# summary table
print(f"{'model':46} {'obj':>5} {'err':>3} {'vis':>6} {'judge':>5} {'latJ':>6} {'draft_tok':>9}")
for r in rows:
    j=r['judge']['avg'] if r.get('judge') else '-'
    print(f"{r['model']:46} {r['obj_pass']:>5} {r['errored']:>3} {r['vision']:>6} {str(j):>5} {str(r['lat_json']):>6} {str(r['tok_draft']):>9}")
print('\nSaved -> results/_aggregate.json')
