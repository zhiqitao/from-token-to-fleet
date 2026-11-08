from pathlib import Path
import json
r=Path(__file__).resolve().parent/'sources'
for name in ['wan_org_repos','wan_hf_models','diffusers_releases']:
 d=json.loads((r/(name+'.raw')).read_text())
 print('\n',name)
 for x in d:
  print(x.get('full_name',x.get('id',x.get('tag_name'))),x.get('sha',''),x.get('published_at',x.get('createdAt','')))
for name in ['wan22_tree','ltx_tree']:
 print('\n',name)
 d=json.loads((r/(name+'.raw')).read_text())
 for x in d.get('tree',[]):
  p=x['path']
  if any(w in p.lower() for w in ['config','attention','text2video','textimage','ti2v','scheduler','distilled','license','model.py']): print(p)
