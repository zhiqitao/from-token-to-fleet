#!/usr/bin/env python3
"""Supplement public sources and record failures; no external writes."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import json, subprocess, urllib.request
ROOT=Path(__file__).resolve().parent; E=ROOT/'evidence'
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('p','div','h1','h2','h3','li','tr','pre','br'): self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'quantization-research/1.0'}),timeout=65) as r: return r.read(),r.geturl(),r.headers.get('Content-Type',''),r.headers.get('Last-Modified')
def fetch(pair):
    ident,url=pair; r={'id':ident,'url':url,'retrieved_at':datetime.now(timezone.utc).isoformat()}
    try:
        data,final,ct,lm=get(url); ext='.pdf' if data.startswith(b'%PDF') else '.html' if 'html' in ct else '.txt'; p=E/(ident+ext); p.write_bytes(data)
        r.update(status='fetched',final_url=final,content_type=ct,last_modified=lm,bytes=len(data),sha256=sha256(data).hexdigest(),raw_path='evidence/'+p.name,text_path='evidence/'+ident+'.txt')
        if ext=='.pdf': subprocess.run(['pdftotext','-layout',str(p),str(E/(ident+'.txt'))],check=True)
        if ext=='.html':
            parser=Text(); parser.feed(data.decode('utf-8',errors='replace')); (E/(ident+'.txt')).write_text(''.join(parser.parts))
    except Exception as exc: r.update(status='failed',error=str(exc))
    return r
if __name__=='__main__':
    import sys
    pairs=json.loads(Path(sys.argv[1]).read_text())
    with ThreadPoolExecutor(max_workers=8) as pool: records=list(pool.map(fetch,pairs))
    manifest=E/'sources.json'; old=json.loads(manifest.read_text()); old.extend(records); manifest.write_text(json.dumps(old,ensure_ascii=False,indent=2))
    for r in records: print(r['id'],r['status'],r.get('bytes'),r.get('error',''))
