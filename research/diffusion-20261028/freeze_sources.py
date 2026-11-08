import concurrent.futures,json,re,hashlib,datetime
from fetch_sources import fetch,ROOT
S={}
for name,repo in [('llada','GSAI-ML/LLaDA-8B-Instruct'),('dream','Dream-org/Dream-v0-Instruct-7B'),('llada22','inclusionAI/LLaDA2.2-flash'),('gemma','google/diffusiongemma-26B-A4B-it')]:
 d=json.loads((ROOT/'sources'/f'{name}_metadata.txt').read_text()); rev=d['sha']
 for key,file in [('card','README.md'),('config','config.json')]: S[f'{name}_{key}_pinned']=f'https://huggingface.co/{repo}/raw/{rev}/{file}'
rev=json.loads((ROOT/'sources/flash_github_revision.txt').read_text())['sha']
for key,p in [('flash_kernel','llada/flash_cache_triton.py'),('flash_generate','llada/generate.py'),('flash_eval','llada/eval_llada.py')]:S[key]=f'https://raw.githubusercontent.com/VILA-Lab/Flash-dLLM/{rev}/{p}'
sg=json.loads((ROOT/'sources/sglang_tree.txt').read_text())['sha']
S['sglang_renoise_algorithm']=f'https://raw.githubusercontent.com/sgl-project/sglang/{sg}/python/sglang/srt/dllm/algorithm/gemma4_renoise.py'
S['sglang_renoise_test']=f'https://raw.githubusercontent.com/sgl-project/sglang/{sg}/test/registered/unit/dllm/test_gemma4_renoise.py'
S['gemma_docs']='https://ai.google.dev/gemma/docs/diffusiongemma'
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as p: rec=list(p.map(fetch,S.items()))
f=ROOT/'source-manifest.json'; old=json.loads(f.read_text());d={r['id']:r for r in old};d.update({r['id']:r for r in rec});f.write_text(json.dumps(list(d.values()),ensure_ascii=False,indent=2))
for x in rec:print(x['id'],x.get('status'),x.get('error',''))
for x in d.values():
 if x['id'].endswith('_identity'):
  t=(ROOT/x['text_path']).read_text();i=t.find('Submission history'); print('IDENTITY',x['id'],t[i:i+550])
for n in ('dream_readme','llada_readme'):
 t=(ROOT/'sources'/f'{n}.txt').read_text();print('RELEASE',n,'\n'.join(l for l in t.splitlines() if any(s in l.lower() for s in ('2025','release','2026')) )[:2000])
