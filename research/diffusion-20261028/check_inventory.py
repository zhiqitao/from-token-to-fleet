import json,pathlib,datetime,re
R=pathlib.Path(__file__).resolve().parent
print('CLOCK',datetime.datetime.now().astimezone().isoformat())
M=json.loads((R/'source-manifest.json').read_text())
print('MANIFEST',len(M),'errors',[(x['id'],x.get('error')) for x in M if x.get('error')])
for n in ('llada','dream','llada22'):
 d=json.loads((R/'sources'/f'{n}_metadata.txt').read_text()); print('MODEL',n,{k:d.get(k) for k in ('id','sha','createdAt','lastModified')})
 print('CONFIG',n,(R/'sources'/f'{n}_config.txt').read_text())
for n in ('ddpm','d3pm','mdlm','llada_paper','dream_paper','fast_dllm_paper','dkv_paper','fast_v2_paper','flash_dllm_paper','bd3lm','llada21_paper'):
 p=R/'sources'/f'{n}.txt'
 if p.exists():
  t=p.read_text(); print('PAPER',n,' '.join(t.splitlines()[:100])[:1100])
for n in ('llada_github_revision','llada2_github_revision','flash_github_revision'):
 d=json.loads((R/'sources'/f'{n}.txt').read_text());print('REV',n,d.get('sha'),d.get('commit',{}).get('committer',{}).get('date'))
