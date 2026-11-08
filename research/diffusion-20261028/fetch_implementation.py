import concurrent.futures,json
from fetch_sources import fetch,ROOT
base='https://raw.githubusercontent.com/sgl-project/sglang/a1966e1b5d8b750b494d7e53cca1d2464f960038/'
S={
'google_diffusiongemma_blog':'https://blog.google/innovation-and-ai/technology/developers-tools/diffusion-gemma-faster-text-generation/',
'gemini_diffusion':'https://deepmind.google/models/gemini-diffusion/',
'sglang_dllm_docs':base+'docs/docs/supported-models/diffusion_language_models.mdx',
'sglang_llada2':base+'python/sglang/srt/models/llada2.py',
'sglang_scheduler':base+'python/sglang/srt/dllm/mixin/scheduler.py',
'sglang_joint_indel':base+'python/sglang/srt/dllm/algorithm/joint_threshold_indel.py',
'sglang_dllm_config':base+'python/sglang/srt/dllm/config.py',
'sglang_gemma_cookbook':base+'docs/cookbook/autoregressive/Google/DiffusionGemma.mdx',
'sglang_indel_test':base+'test/registered/unit/dllm/algorithm/test_joint_threshold_indel.py',
'fast_generate':'https://raw.githubusercontent.com/NVlabs/Fast-dLLM/a9b81e4caa240c8cad4f7dc1889ff4852a0fca5b/v1/llada/generate.py',
'flash_tree':'https://api.github.com/repos/VILA-Lab/Flash-dLLM/git/trees/main?recursive=1',
'dinfer_repo':'https://api.github.com/repos/inclusionAI/dInfer',
}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as p: records=list(p.map(fetch,S.items()))
f=ROOT/'source-manifest.json'; old=json.loads(f.read_text()); d={r['id']:r for r in old};d.update({r['id']:r for r in records});f.write_text(json.dumps(list(d.values()),ensure_ascii=False,indent=2))
for r in records: print(r['id'],r.get('status'),r.get('bytes'),r.get('error',''))
from html.parser import HTMLParser
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  href=dict(attrs).get('href') or ''
  if tag=='a' and any(x in href for x in ('huggingface','github','arxiv','ai.google.dev','storage.googleapis')): print(href)
Links().feed((ROOT/'sources/google_diffusiongemma_blog.raw').read_text())
