from pathlib import Path
import json,re
r=Path(__file__).resolve().parent/'sources'
for n in ['wan22_commit','ltx_commit','hunyuan_commit']:
 d=json.loads((r/(n+'.raw')).read_text()); print(n,d['sha'],d['commit']['committer']['date'])
for d in json.loads((r/'diffusers_releases.raw').read_text()): print('diffusers',d['tag_name'],d['published_at'])
for n in ['wan_report_abs','ltx_report_abs','hunyuan_report_abs','animate2_report_abs']:
 t=(r/(n+'.txt')).read_text(); p=t.find('Submission history'); print(n,t[p:p+1000])
for n in ['hunyuan_tree']:
 print(n)
 for x in json.loads((r/(n+'.raw')).read_text()).get('tree',[]):
  p=x['path']
  if any(k in p for k in ['config','attention','transformer','pipeline','scheduler']): print(p)
