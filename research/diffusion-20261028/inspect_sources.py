import json,pathlib,re
from html.parser import HTMLParser
R=pathlib.Path(__file__).resolve().parent
class Links(HTMLParser):
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='a' and any(x in d.get('href','').lower() for x in ('mercury','stream','diffusion','structured','llada','sglang','dinfer')): print(d.get('href'))
for key in ('inception_blog','mercury_docs'):
 print('\nLINKS',key); Links().feed((R/'sources'/f'{key}.raw').read_text())
for key in ('llada_metadata','dream_metadata','llada22_metadata'):
 d=json.loads((R/'sources'/f'{key}.txt').read_text()); print(key,{k:d.get(k) for k in ('id','sha','createdAt','lastModified')}); print('files', [x['rfilename'] for x in d.get('siblings',[])])
for key in ('llada_config','dream_config','llada22_config'):
 print('\nCONFIG',key,(R/'sources'/f'{key}.txt').read_text())
