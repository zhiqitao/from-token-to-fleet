"""Fetch primary evidence into this task directory only; never execute remote code."""
import concurrent.futures, datetime, hashlib, json, pathlib, subprocess, sys, urllib.request
from html.parser import HTMLParser
ROOT = pathlib.Path(__file__).resolve().parent
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip += 1
        if tag in ('p','div','li','h1','h2','h3','tr','br'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)
def fetch(item):
    name,url=item
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 collective-library-research'})
        with urllib.request.urlopen(req,timeout=55) as r: body=r.read(); final=r.url
        (ROOT/'evidence').mkdir(exist_ok=True)
        (ROOT/'evidence'/f'{name}.raw').write_bytes(body)
        if body.startswith(b'%PDF'):
            import pymupdf
            doc=pymupdf.open(stream=body,filetype='pdf')
            s='\n'.join(f'\n[physical page {i+1}]\n'+page.get_text() for i,page in enumerate(doc))
        else:
            s=body.decode('utf-8',errors='replace')
        if '<html' in s[:2000].lower() or '<!doctype html' in s[:2000].lower():
            parser=Text(); parser.feed(s); s='\n'.join(x.strip() for x in ''.join(parser.parts).splitlines() if x.strip())
        (ROOT/'evidence'/f'{name}.txt').write_text(s)
        result={'name':name,'url':url,'resolved_url':final,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(body).hexdigest(),'chars':len(s),'text_path':f'evidence/{name}.txt'}
        print(json.dumps(result),flush=True)
        return result
    except Exception as e:
        result={'name':name,'url':url,'error':str(e)}; print(json.dumps(result),flush=True); return result
if __name__=='__main__':
    items=json.loads(sys.argv[1])
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(fetch,items))
    manifest=ROOT/'retrieval.json'
    prior=json.loads(manifest.read_text()) if manifest.exists() else []
    prior += results; manifest.write_text(json.dumps(prior,ensure_ascii=False,indent=2))
    ledger=ROOT/'sources-ledger.json'
    tool='/home/ubuntu/.hermes/profiles/muta/skills/research/grounded-citations/scripts/sources.py'
    for r in results:
        if 'error' not in r:
            p=subprocess.run([sys.executable,tool,'--ledger',str(ledger),'add',r['url'],'--title',r['name']],capture_output=True,text=True)
            print('LEDGER',r['name'],p.stdout.strip(),p.stderr.strip())
