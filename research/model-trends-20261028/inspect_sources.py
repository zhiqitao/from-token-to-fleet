import collections,html,json,pathlib,re,sys
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parent
class Cleaner(HTMLParser):
 def __init__(self):super().__init__();self.out=[];self.skip=0
 def handle_starttag(self,tag,attrs):
  if tag in ['script','style']:self.skip+=1
  if tag in ['p','div','tr','h1','h2','h3','h4','h5','li','section','br']:self.out.append('\n')
 def handle_endtag(self,tag):
  if tag in ['script','style']:self.skip=max(0,self.skip-1)
 def handle_data(self,data):
  if not self.skip:self.out.append(data)
def clean(s):
 p=Cleaner();p.feed(s);return '\n'.join(re.sub(r'\s+',' ',x).strip() for x in ''.join(p.out).splitlines() if x.strip())
for p in (ROOT/'sources').glob('*.txt'):
 s=p.read_text(errors='replace')
 if '<html' in s[:1000].lower() or '<!doctype' in s[:1000].lower():
  (ROOT/'sources'/f'{p.stem}.clean.md').write_text(clean(s))
 if 'config' in p.stem:
  try:
   d=json.loads(s);t=d.get('text_config',d)
   print(p.stem, json.dumps({k:v for k,v in t.items() if not isinstance(v,(dict,list))},ensure_ascii=False)[:4000])
   for k,v in t.items():
    if isinstance(v,list):print(' ',k,collections.Counter(map(str,v)))
  except Exception as e:print(p.stem,e)
 if p.stem.endswith('meta'):
  d=json.loads(s);print(p.stem,{k:d.get(k) for k in ['id','sha','createdAt','lastModified','safetensors']})
