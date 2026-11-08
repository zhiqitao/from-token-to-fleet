"""Read public primary sources; all writes stay in this research directory."""
from pathlib import Path
import urllib.request, json, concurrent.futures, hashlib, datetime, re, sys
ROOT = Path(__file__).resolve().parent
SOURCES = {
 'wan22_readme':'https://raw.githubusercontent.com/Wan-Video/Wan2.2/main/README.md',
 'wan21_readme':'https://raw.githubusercontent.com/Wan-Video/Wan2.1/main/README.md',
 'wan_org_repos':'https://api.github.com/orgs/Wan-Video/repos?per_page=100',
 'wan_hf_models':'https://huggingface.co/api/models?author=Wan-AI&limit=100&full=true',
 'wan22_tree':'https://api.github.com/repos/Wan-Video/Wan2.2/git/trees/main?recursive=1',
 'wan22_commit':'https://api.github.com/repos/Wan-Video/Wan2.2/commits/main',
 'wan21_report':'https://arxiv.org/html/2503.20314',
 'animate2_readme':'https://raw.githubusercontent.com/Wan-Video/Wan-Animate-2/main/README.md',
 'ltx_readme':'https://raw.githubusercontent.com/Lightricks/LTX-2/main/README.md',
 'ltx_tree':'https://api.github.com/repos/Lightricks/LTX-2/git/trees/main?recursive=1',
 'ltx_report':'https://arxiv.org/html/2601.03233',
 'ltx25_card':'https://huggingface.co/Lightricks/LTX-2.5/raw/main/README.md',
 'ltx2_card':'https://huggingface.co/Lightricks/LTX-2/raw/main/README.md',
 'hunyuan_readme':'https://raw.githubusercontent.com/Tencent-Hunyuan/HunyuanVideo-1.5/main/README.md',
 'hunyuan_report':'https://arxiv.org/html/2511.18870',
 'ali_overview':'https://www.alibabacloud.com/help/en/model-studio/video-editing-and-generation',
 'ali_t2v':'https://www.alibabacloud.com/help/en/model-studio/text-to-video-api-reference',
 'ali_i2v':'https://www.alibabacloud.com/help/en/model-studio/image-to-video-general-api-reference',
 'diffusers_wan':'https://huggingface.co/docs/diffusers/api/pipelines/wan',
 'diffusers_releases':'https://api.github.com/repos/huggingface/diffusers/releases?per_page=5',
 'xfuser_readme':'https://raw.githubusercontent.com/xdit-project/xDiT/main/README.md',
 'ltx_releases':'https://ltx.io/release-notes',
}

def fetch(item):
 name,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'FromTokenToFleet-research/1.0'})
  with urllib.request.urlopen(req,timeout=80) as r: data=r.read(); final=r.url
  p=ROOT/'sources'/f'{name}.raw'; p.parent.mkdir(exist_ok=True); p.write_bytes(data)
  text=data.decode('utf-8',errors='replace')
  if '<html' in text[:2000].lower() or '<!doctype' in text[:200].lower():
   text=re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',text,flags=re.S|re.I)
   text=re.sub(r'</(?:p|div|h[1-6]|tr|li|section)>','\n',text,flags=re.I)
   text=re.sub('<[^>]+>',' ',text)
   import html
   text=html.unescape(text)
   text=re.sub(r'[ \t]+',' ',text)
  (ROOT/'sources'/f'{name}.txt').write_text(text)
  return {'id':name,'url':url,'resolved_url':final,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'path':str(p.relative_to(ROOT)),'status':'retrieved'}
 except Exception as e: return {'id':name,'url':url,'status':'failed','error':str(e)}
if __name__=='__main__':
 if len(sys.argv)>1:
  additional=json.loads((ROOT/sys.argv[1]).read_text()); SOURCES=additional
 out=list(concurrent.futures.ThreadPoolExecutor(max_workers=8).map(fetch,SOURCES.items()))
 manifest=ROOT/'sources'/'manifest.json'
 old=json.loads(manifest.read_text()) if manifest.exists() else []
 byid={x['id']:x for x in old}; byid.update({x['id']:x for x in out})
 manifest.write_text(json.dumps(list(byid.values()),indent=2,ensure_ascii=False))
 for x in out: print(x['id'],x['status'],x.get('bytes',x.get('error')))
