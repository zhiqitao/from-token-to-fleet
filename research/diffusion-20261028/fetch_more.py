import concurrent.futures,json,pathlib,subprocess
from fetch_sources import fetch, ROOT
S={
'mercury3':'https://www.inceptionlabs.ai/blog/introducing-mercury-3',
'mercury25':'https://www.inceptionlabs.ai/blog/introducing-mercury-2-5',
'mercury2_launch':'https://www.inceptionlabs.ai/blog/introducing-mercury-2',
'mercury_stream':'https://docs.inceptionlabs.ai/capabilities/streaming',
'mercury_structured':'https://docs.inceptionlabs.ai/capabilities/structured-outputs',
'llada21_paper':'https://arxiv.org/html/2602.08676',
'llada20_paper':'https://arxiv.org/html/2512.15745',
'llada22_report':'https://raw.githubusercontent.com/inclusionAI/LLaDA2.X/main/LLaDA2_2_tech_report.pdf',
'dinfer_readme':'https://raw.githubusercontent.com/inclusionAI/dInfer/main/README.md',
'sglang_tree':'https://api.github.com/repos/sgl-project/sglang/git/trees/main?recursive=1',
'fast_tree':'https://api.github.com/repos/NVlabs/Fast-dLLM/git/trees/main?recursive=1',
'llada_github_revision':'https://api.github.com/repos/ML-GSAI/LLaDA/commits/main',
'llada2_github_revision':'https://api.github.com/repos/inclusionAI/LLaDA2.X/commits/main',
'flash_github_revision':'https://api.github.com/repos/VILA-Lab/Flash-dLLM/commits/main',
'dream_generate':'https://huggingface.co/Dream-org/Dream-v0-Instruct-7B/raw/05334cb9faaf763692dcf9d8737c642be2b2a6ae/generation_utils.py',
'dream_model':'https://huggingface.co/Dream-org/Dream-v0-Instruct-7B/raw/05334cb9faaf763692dcf9d8737c642be2b2a6ae/modeling_dream.py',
'llada22_model':'https://huggingface.co/inclusionAI/LLaDA2.2-flash/raw/9b78da3f9149f1e239fb6d15f20a326fde574b9f/modeling_llada2_moe.py',
'bd3lm':'https://arxiv.org/html/2503.09573',
}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as p: records=list(p.map(fetch,S.items()))
path=ROOT/'source-manifest.json'; old=json.loads(path.read_text()); byid={r['id']:r for r in old}; byid.update({r['id']:r for r in records}); path.write_text(json.dumps(list(byid.values()),ensure_ascii=False,indent=2))
for r in records: print(r['id'],r.get('status'),r.get('bytes'),r.get('error',''))
pdf=ROOT/'sources/llada22_report.raw'
if pdf.read_bytes().startswith(b'%PDF'):
 result=subprocess.run(['pdftotext','-layout',str(pdf),str(ROOT/'sources/llada22_report.txt')],capture_output=True,text=True); print('pdf extraction',result.returncode,result.stderr)
for name in ('sglang_tree','fast_tree'):
 d=json.loads((ROOT/'sources'/f'{name}.txt').read_text()); print('\nTREE',name,'sha',d.get('sha'),'truncated',d.get('truncated'))
 for x in d.get('tree',[]):
  if any(k in x['path'].lower() for k in ('dllm','llada','diffusion','dualcache')): print(x['path'])
