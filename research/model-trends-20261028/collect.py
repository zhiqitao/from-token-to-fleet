"""Fetch only public sources; retain response metadata and immutable hashes."""
import concurrent.futures, datetime, hashlib, json, pathlib, sys, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
SOURCES={
'qwen-card':'https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/README.md',
'qwen-config':'https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/config.json',
'qwen-meta':'https://huggingface.co/api/models/Qwen/Qwen3.8-27B',
'ornith-report':'https://ornith.ai/ornith_1_5.html',
'ornith397-card':'https://huggingface.co/ornith-ai/Ornith-1.5-397B/raw/main/README.md',
'ornith397-config':'https://huggingface.co/ornith-ai/Ornith-1.5-397B/raw/main/config.json',
'ornith35-card':'https://huggingface.co/ornith-ai/Ornith-1.5-35B-A3B/raw/main/README.md',
'ornith35-config':'https://huggingface.co/ornith-ai/Ornith-1.5-35B-A3B/raw/main/config.json',
'ornith9-config':'https://huggingface.co/ornith-ai/Ornith-1.5-9B/raw/main/config.json',
'ornith-models':'https://huggingface.co/api/models?author=ornith-ai&limit=100',
'deepseek-report':'https://arxiv.org/html/2606.19348',
'deepseek-abs':'https://arxiv.org/abs/2606.19348',
'deepseek-card':'https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/raw/main/README.md',
'deepseek-config':'https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/raw/main/config.json',
'deepseek-release':'https://api-docs.deepseek.com/news/news260424',
'glm-report':'https://z.ai/blog/glm-5.3-flash',
'glm-card':'https://huggingface.co/zai-org/GLM-5.3-Flash/raw/main/README.md',
'glm-config':'https://huggingface.co/zai-org/GLM-5.3-Flash/raw/main/config.json',
'mimo-report':'https://arxiv.org/html/2601.02780',
'mimo-abs':'https://arxiv.org/abs/2601.02780',
'mimo-card':'https://huggingface.co/XiaomiMiMo/MiMo-V2-Flash/raw/main/README.md',
'mimo-config':'https://huggingface.co/XiaomiMiMo/MiMo-V2-Flash/raw/main/config.json',
'mimo-github':'https://raw.githubusercontent.com/XiaomiMiMo/MiMo-V2-Flash/main/README.md',
'gemini-card':'https://deepmind.google/models/model-cards/gemini-3-8-flash/',
'gemini-release':'https://blog.google/innovation-and-ai/models-and-research/gemini-models/3-8-flash-and-3-8-flash-cyber',
'gemini-doc':'https://ai.google.dev/gemini-api/docs/latest-model',
}
def fetch(item):
 key,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (public research)'})
  with urllib.request.urlopen(req,timeout=60) as r:
   data=r.read();meta={'key':key,'url':url,'final_url':r.url,'status':r.status,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'content_type':r.headers.get('Content-Type'),'last_modified':r.headers.get('Last-Modified'),'etag':r.headers.get('ETag'),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
  dest=ROOT/'sources'/f'{key}.txt';dest.parent.mkdir(exist_ok=True);dest.write_bytes(data);meta['local_path']=str(dest.relative_to(ROOT))
 except Exception as e:meta={'key':key,'url':url,'error':str(e),'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 return meta
if __name__=='__main__':
 if (ROOT/'extra-sources.json').exists():
  SOURCES.update(json.loads((ROOT/'extra-sources.json').read_text()))
 selected={k:v for k,v in SOURCES.items() if not sys.argv[1:] or k in sys.argv[1:]}
 out=list(concurrent.futures.ThreadPoolExecutor(8).map(fetch,selected.items()))
 p=ROOT/'fetch-log.json';old=json.loads(p.read_text()) if p.exists() else [];p.write_text(json.dumps(old+out,indent=2));print(json.dumps(out,indent=2))
