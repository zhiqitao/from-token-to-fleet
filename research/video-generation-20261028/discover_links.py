from pathlib import Path
import re,json
from html.parser import HTMLParser
r=Path(__file__).resolve().parent/'sources'
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  if tag=='a':
   d=dict(attrs); h=d.get('href') or ''
   if any(x in h.lower() for x in ['wan','ltx-2-5','paper','report']): print(h)
for n in ['ali_overview','ltx_releases']:
 print(n); Links().feed((r/(n+'.raw')).read_text())
print('diffusers release models')
for d in json.loads((r/'diffusers_releases.raw').read_text()):
 t=d.get('body','')
 print(d['tag_name'])
 for l in t.splitlines():
  if any(k in l.lower() for k in ['wan','ltx','hunyuan']): print(l)
