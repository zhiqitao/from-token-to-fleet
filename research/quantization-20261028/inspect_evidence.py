#!/usr/bin/env python3
"""Print bounded evidence excerpts or discovered public-source paths."""
from pathlib import Path
import json,sys
E=Path(__file__).resolve().parent/'evidence'
if sys.argv[1]=='trees':
    for key in ('GGML','LLAMA','VLLM'):
        obj=json.loads((E/(key+'-TREE.txt')).read_text())
        print('\nTREE',key,obj.get('sha'))
        for entry in obj.get('tree',[]):
            p=entry['path']
            if any(s in p.lower() for s in ('gguf.md','awq.py','mxfp4','nvfp4','cuda.md','quantization.md','imatrix','quantize/README','marlin')) and not p.endswith(('.cu','.cuh')): print(p)
else:
    for arg in sys.argv[1:]:
        key,pattern=arg.split(':',1); lines=(E/(key+'.txt')).read_text().splitlines(); import re
        print('\nSOURCE',key)
        indexes=set()
        for i,line in enumerate(lines):
            if re.search(pattern,line,re.I): indexes.update(range(max(0,i-2),min(len(lines),i+5)))
        for i in sorted(indexes)[:240]: print(f'{i+1}: {lines[i]}')
