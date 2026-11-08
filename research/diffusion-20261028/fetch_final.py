import concurrent.futures,json,re
from fetch_sources import fetch,ROOT
S={
 'gemma_card':'https://huggingface.co/google/diffusiongemma-26B-A4B-it/raw/main/README.md',
 'gemma_config':'https://huggingface.co/google/diffusiongemma-26B-A4B-it/raw/main/config.json',
 'gemma_generation':'https://huggingface.co/google/diffusiongemma-26B-A4B-it/raw/main/generation_config.json',
 'gemma_metadata':'https://huggingface.co/api/models/google/diffusiongemma-26B-A4B-it',
 'dflash_paper':'https://arxiv.org/html/2602.06036',
 'agent_counterexample':'https://arxiv.org/html/2601.12979',
 'order_counterexample':'https://arxiv.org/html/2601.15165',
}
for key in ('ddpm','score_sde','d3pm','mdlm','flow_matching','rectified_flow','llada_paper','dream_paper','fast_dllm_paper','dkv_paper','fast_v2_paper','flash_dllm_paper','bd3lm','llada21_paper'):
 manifest=json.loads((ROOT/'source-manifest.json').read_text()); orig=next(x['url'] for x in manifest if x['id']==key); S[key+'_identity']=orig.replace('/html/','/abs/')
repo=json.loads((ROOT/'sources/dinfer_repo.txt').read_text())
S['dinfer_readme_fixed']='https://raw.githubusercontent.com/inclusionAI/dInfer/'+repo['default_branch']+'/README.md'
S['dinfer_revision']='https://api.github.com/repos/inclusionAI/dInfer/commits/'+repo['default_branch']
rev=json.loads((ROOT/'sources/flash_github_revision.txt').read_text())['sha']
tree=json.loads((ROOT/'sources/flash_tree.txt').read_text())
for x in tree['tree']:
 p=x['path']
 if p.endswith('.py'): print('FLASH FILE',p)
 if p.endswith(('requirements.txt','setup.py','pyproject.toml')): S['flash_'+p.replace('/','_').replace('.','_')]='https://raw.githubusercontent.com/VILA-Lab/Flash-dLLM/'+rev+'/'+p
sg=json.loads((ROOT/'sources/sglang_tree.txt').read_text())
for x in sg['tree']:
 if x['path'].endswith('.py') and 'renoise' in x['path'].lower(): S['sglang_renoise']='https://raw.githubusercontent.com/sgl-project/sglang/'+sg['sha']+'/'+x['path'];print('SG REN',x['path'])
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as p: records=list(p.map(fetch,S.items()))
f=ROOT/'source-manifest.json'; old=json.loads(f.read_text()); d={r['id']:r for r in old};d.update({r['id']:r for r in records});f.write_text(json.dumps(list(d.values()),ensure_ascii=False,indent=2))
for r in records: print(r['id'],r.get('status'),r.get('bytes'),r.get('error',''))
if (ROOT/'sources/gemma_metadata.txt').exists():
 d=json.loads((ROOT/'sources/gemma_metadata.txt').read_text());print('GEMMA',d.get('sha'),d.get('createdAt'),d.get('lastModified'));print('GEMMA FILES',[x['rfilename'] for x in d.get('siblings',[])])
for name in ('agent_counterexample','order_counterexample','dflash_paper'):
 t=(ROOT/'sources'/f'{name}.txt').read_text();print('COUNTER',name,t[:5000])
