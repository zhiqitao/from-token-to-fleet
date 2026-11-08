#!/usr/bin/env python3
"""Fetch only public primary evidence; write only beside this script."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import json, subprocess, urllib.request
ROOT = Path(__file__).resolve().parent
E = ROOT / 'evidence'; E.mkdir(exist_ok=True)
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self,t,a):
        if t in ('script','style'): self.skip+=1
        if t in ('p','div','h1','h2','h3','h4','li','tr','pre','br'): self.parts.append('\n')
    def handle_endtag(self,t):
        if t in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self,d):
        if not self.skip: self.parts.append(d)
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'quantization-research/1.0 (public evidence)'})
    with urllib.request.urlopen(req,timeout=65) as r: return r.read(),r.geturl(),r.headers.get('Content-Type',''),r.headers.get('Last-Modified')
repos={'llama':'ggml-org/llama.cpp','awq':'mit-han-lab/llm-awq','gptq':'IST-DASLab/gptq','te':'NVIDIA/TransformerEngine','mo':'NVIDIA/Model-Optimizer','trt':'NVIDIA/TensorRT-LLM','vllm':'vllm-project/vllm','sglang':'sgl-project/sglang'}
pins={}
for key, repo in repos.items():
    try:
        data,_,_,_=get('https://api.github.com/repos/'+repo+'/commits/HEAD')
        obj=json.loads(data); pins[key]={'repo':repo,'sha':obj['sha'],'commit_date':obj['commit']['committer']['date']}
    except Exception as exc: pins[key]={'repo':repo,'error':str(exc)}
(E/'code_pins.json').write_text(json.dumps(pins,indent=2))
def raw(repo,path): return 'https://raw.githubusercontent.com/'+repos[repo]+'/'+pins[repo].get('sha','main')+'/'+path
sources=[
('AWQ-ABS','https://arxiv.org/abs/2306.00978'),('AWQ-V1','https://arxiv.org/pdf/2306.00978v1'),
('GPTQ-ABS','https://arxiv.org/abs/2210.17323'),('GPTQ-PAPER','https://arxiv.org/pdf/2210.17323v2'),
('AWQ-README',raw('awq','README.md')),('AWQ-QUANT',raw('awq','awq/quantize/quantizer.py')),('AWQ-LINEAR',raw('awq','awq/quantize/qmodule.py')),('AWQ-LICENSE',raw('awq','LICENSE')),
('GPTQ-README',raw('gptq','README.md')),('GPTQ-QUANT',raw('gptq','quant.py')),('GPTQ-ALGO',raw('gptq','gptq.py')),('GPTQ-LICENSE',raw('gptq','LICENSE.txt')),
('GGUF-SPEC',raw('llama','ggml/docs/gguf.md')),('GGML-BLOCKS',raw('llama','ggml/src/ggml-common.h')),('GGML-QUANTS',raw('llama','ggml/src/ggml-quants.c')),('LLAMA-MIX',raw('llama','src/llama-quant.cpp')),('LLAMA-README',raw('llama','README.md')),('LLAMA-LICENSE',raw('llama','LICENSE')),('LLAMA-CUDA',raw('llama','docs/backend/CUDA.md')),
('OCP-V1','https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf'),('OCP-V11','https://www.opencompute.org/wp-content/uploads/2026/10/OCP_MicroXcaling_Spec_v1.1.0.pdf'),
('NVFP4-BLOG','https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/'),('NVFP4-TE','https://docs.nvidia.com/deeplearning/transformer-engine/features/low_precision_training/nvfp4/nvfp4.html'),('TE-README',raw('te','README.rst')),('TE-LOWP','https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/examples/fp8_primer.html'),
('MO-QUANT','https://nvidia.github.io/Model-Optimizer/guides/1_quantization.html'),('MO-README',raw('mo','README.md')),('MO-CONFIG',raw('mo','modelopt/torch/quantization/config.py')),('MO-LICENSE',raw('mo','LICENSE')),
('TRT-PRECISION','https://nvidia.github.io/TensorRT-LLM/reference/precision.html'),('TRT-SUPPORT','https://nvidia.github.io/TensorRT-LLM/reference/support-matrix.html'),('TRT-README',raw('trt','README.md')),
('VLLM-QUANT','https://docs.vllm.ai/en/latest/features/quantization/'),('VLLM-GGUF','https://docs.vllm.ai/en/latest/features/quantization/gguf/'),('VLLM-FP8KV','https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/'),('VLLM-AWQ',raw('vllm','vllm/model_executor/layers/quantization/awq.py')),('VLLM-NVFP4',raw('vllm','vllm/model_executor/layers/quantization/modelopt.py')),
('SGLANG-QUANT','https://docs.sglang.ai/advanced_features/quantization.html'),('OPENVINO-MX','https://docs.openvino.ai/2025/openvino-workflow/model-optimization-guide/weight-compression/microscaling-quantization.html'),
('SMOOTHQUANT','https://arxiv.org/pdf/2211.10438'),('KIVI','https://arxiv.org/pdf/2402.02750'),('QLORA','https://arxiv.org/pdf/2305.14314'),('GPTOSS','https://huggingface.co/openai/gpt-oss-120b/raw/main/README.md'),('GPTOSS-CONFIG','https://huggingface.co/openai/gpt-oss-120b/raw/main/config.json'),('NVFP4-PAPER','https://arxiv.org/pdf/2509.25149')]
def fetch(item):
    ident,url=item; record={'id':ident,'url':url,'retrieved_at':datetime.now(timezone.utc).isoformat()}
    try:
        data,final,ctype,lm=get(url); ext='.pdf' if data.startswith(b'%PDF') else '.html' if 'html' in ctype else '.txt'
        path=E/(ident+ext); path.write_bytes(data)
        record.update(final_url=final,content_type=ctype,last_modified=lm,bytes=len(data),sha256=sha256(data).hexdigest(),raw_path=str(path.relative_to(ROOT)),status='fetched')
        if ext=='.pdf':
            target=E/(ident+'.txt'); p=subprocess.run(['pdftotext','-layout',str(path),str(target)],capture_output=True,text=True)
            record['extraction_exit']=p.returncode
        elif ext=='.html':
            parser=Text(); parser.feed(data.decode('utf-8',errors='replace')); (E/(ident+'.txt')).write_text(''.join(parser.parts))
        record['text_path']='evidence/'+ident+'.txt'
    except Exception as exc: record.update(status='failed',error=str(exc))
    return record
with ThreadPoolExecutor(max_workers=8) as pool:
    records=list(pool.map(fetch,sources))
manifest=E/'sources.json'
old=json.loads(manifest.read_text()) if manifest.exists() else []
byid={r['id']:r for r in old}; byid.update({r['id']:r for r in records}); manifest.write_text(json.dumps(list(byid.values()),ensure_ascii=False,indent=2))
for r in records: print(r['id'],r['status'],r.get('bytes'),r.get('error',''))
print('PINS',json.dumps(pins))
