#!/usr/bin/env python3
"""Summarize collected public evidence and publication/source anchors."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
E=R/'evidence'
print('PINS', (E/'code_pins.json').read_text())
records=json.loads((E/'sources.json').read_text())
print('RECORDS',len(records))
for r in records: print(r['id'],r['status'],r.get('url'),r.get('error',''))
for name in ('MO','TRT','VLLM','SGLANG'):
    p=E/(name+'-RELEASE.txt')
    if p.exists():
        o=json.loads(p.read_text()); print('RELEASE',name,o.get('tag_name'),o.get('published_at'),o.get('target_commitish'))
print('FILES', '\n'.join(p.name for p in sorted(R.iterdir())))
