"""Fetch only public primary sources and retain byte hashes and text."""
import concurrent.futures, datetime, hashlib, json, pathlib, urllib.request
from html.parser import HTMLParser
ROOT = pathlib.Path(__file__).resolve().parent
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('p','div','section','h1','h2','h3','h4','tr','li','pre'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)
SOURCES = {
 'ddpm':'https://arxiv.org/html/2006.11239',
 'score_sde':'https://arxiv.org/html/2011.13456',
 'd3pm':'https://arxiv.org/html/2107.03006',
 'mdlm':'https://arxiv.org/html/2406.07524',
 'flow_matching':'https://arxiv.org/html/2210.02747',
 'rectified_flow':'https://arxiv.org/html/2209.03003',
 'llada_paper':'https://arxiv.org/html/2502.09992',
 'dream_paper':'https://arxiv.org/html/2508.15487v1',
 'fast_dllm_paper':'https://arxiv.org/html/2505.22618',
 'dkv_paper':'https://arxiv.org/html/2505.15781',
 'fast_v2_paper':'https://arxiv.org/html/2509.26328',
 'flash_dllm_paper':'https://arxiv.org/html/2609.26796',
 'llada_readme':'https://raw.githubusercontent.com/ML-GSAI/LLaDA/main/README.md',
 'llada_generate':'https://raw.githubusercontent.com/ML-GSAI/LLaDA/main/generate.py',
 'dream_readme':'https://raw.githubusercontent.com/DreamLM/Dream/main/README.md',
 'llada2_readme':'https://raw.githubusercontent.com/inclusionAI/LLaDA2.X/main/README.md',
 'fast_readme':'https://raw.githubusercontent.com/NVlabs/Fast-dLLM/main/README.md',
 'dkv_readme':'https://raw.githubusercontent.com/horseee/dKV-Cache/main/README.md',
 'flash_readme':'https://raw.githubusercontent.com/VILA-Lab/Flash-dLLM/main/README.md',
 'mercury2':'https://www.inceptionlabs.ai/blog/mercury-2-the-first-reasoning-model-fast-enough-to-pick-up-the-phone',
 'inception_blog':'https://www.inceptionlabs.ai/blog',
 'mercury_docs':'https://docs.inceptionlabs.ai/get-started/models',
 'llada_card':'https://huggingface.co/GSAI-ML/LLaDA-8B-Instruct/raw/main/README.md',
 'llada_config':'https://huggingface.co/GSAI-ML/LLaDA-8B-Instruct/raw/main/config.json',
 'llada_metadata':'https://huggingface.co/api/models/GSAI-ML/LLaDA-8B-Instruct',
 'dream_card':'https://huggingface.co/Dream-org/Dream-v0-Instruct-7B/raw/main/README.md',
 'dream_config':'https://huggingface.co/Dream-org/Dream-v0-Instruct-7B/raw/main/config.json',
 'dream_metadata':'https://huggingface.co/api/models/Dream-org/Dream-v0-Instruct-7B',
 'llada22_card':'https://huggingface.co/inclusionAI/LLaDA2.2-flash/raw/main/README.md',
 'llada22_config':'https://huggingface.co/inclusionAI/LLaDA2.2-flash/raw/main/config.json',
 'llada22_metadata':'https://huggingface.co/api/models/inclusionAI/LLaDA2.2-flash',
}
def fetch(item):
    key,url=item; record={'id':key,'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (research)'})
        with urllib.request.urlopen(req,timeout=70) as r: body=r.read(); record.update(status=r.status,final_url=r.url,content_type=r.headers.get('Content-Type',''))
        dest=ROOT/'sources'; dest.mkdir(exist_ok=True)
        (dest/(key+'.raw')).write_bytes(body)
        text=body.decode('utf-8',errors='replace')
        if 'html' in record['content_type']:
            parser=Text(); parser.feed(text); text=''.join(parser.parts)
            text='\n'.join(line.strip() for line in text.splitlines() if line.strip())
        (dest/(key+'.txt')).write_text(text)
        record.update(bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),text_path='sources/'+key+'.txt')
    except Exception as e: record['error']=str(e)
    return record
if __name__=='__main__':
    import sys
    chosen={k:v for k,v in SOURCES.items() if not sys.argv[1:] or k in sys.argv[1:]}
    manifest=ROOT/'source-manifest.json'
    old=json.loads(manifest.read_text()) if manifest.exists() else []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: records=list(pool.map(fetch,chosen.items()))
    byid={r['id']:r for r in old}; byid.update({r['id']:r for r in records})
    manifest.write_text(json.dumps(list(byid.values()),ensure_ascii=False,indent=2))
    for r in records: print(r['id'],r.get('status'),r.get('bytes'),r.get('error',''))
