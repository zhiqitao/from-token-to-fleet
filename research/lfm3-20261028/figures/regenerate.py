#!/usr/bin/env python3
"""Repair the source SVG, render both formats, and test actual text fit."""
from pathlib import Path
import collections
import json
import subprocess
import xml.etree.ElementTree as ET
import pymupdf

ROOT = Path(__file__).resolve().parent
SVG = ROOT / 'lfm3-architecture.svg'
NS = '{http://www.w3.org/2000/svg}'
ET.register_namespace('', NS[1:-1])
tree = ET.parse(SVG)
root = tree.getroot()
replacements = {
    'C: gated short conv, kernel 7 (13)': 'C: short conv, k=7 (13)',
    'G: partial RoPE (rotates top-frequency half, theta 1e6) · S: full RoPE (theta 1e4) · GQA 16 Q / 4 KV heads, head_dim 128': 'G: half RoPE, theta 1e6; S: full RoPE, theta 1e4; 16 Q / 4 KV heads',
    'state = last 6 tokens': 'fixed kernel-state buffer',
    '(kernel-7 ring buffer)': '(kernel size 7)',
    'KV for last 256 tokens': 'Retain 256 tokens',
    'only (sliding window)': 'if runtime crops cache',
    'O(1): ~2.6 MB total': 'O(1): 2.5 MiB total',
    'O(T): 12 KB / token': 'O(T): 12 KiB / token',
    'Only 6/24 layers grow: 12,288 B/token (bf16) × 128K tokens ≈ 1.61 GB — matches vendor claim "1.6 GB KV @ 128K"': '6 global layers: 12,288 B/token x 131,072 tokens = 1.611 GB (BF16)',
    '(vs 4.3 GB Qwen3.5-4B, 5.6 GB MiniCPM5-2B; vendor-measured, tool/precision undisclosed)': 'Vendor reports 1.6 GB at 128K; actual runtime allocation not tested here.',
    'Derived from HF config.json + Liquid AI blog (2026-10-27); retrieved 2026-10-28. No LFM3 tech report exists (arXiv: 0 hits).': 'Sources: Liquid AI blog (2026-10-27); HF config (retrieved 2026-10-28).',
}
for node in root.iter(NS+'text'):
    if node.text in replacements:
        node.text = replacements[node.text]
    if node.get('y') == '243':
        node.set('y', '238')
    if node.get('y') == '251':
        node.set('y', '249')
# Keep a real right margin. Derive cells from exact config, not grouped SVG order.
config = json.loads((ROOT.parent/'raw/hf_LFM3-1.7B_config.json').read_text())
kind_to_letter = {'conv': 'C', 'full_attention': 'G', 'sliding_attention': 'S'}
rects = sorted([n for n in root.iter(NS+'rect') if n.get('y') == '45'], key=lambda n: float(n.get('x')))
labels = sorted([n for n in root.iter(NS+'text') if n.get('y') == '56.5'], key=lambda n: float(n.get('x')))
assert len(rects) == len(labels) == len(config['layer_types']) == 24
for i, (rect, label, kind) in enumerate(zip(rects, labels, config['layer_types'])):
    assert label.text == kind_to_letter[kind], (i, label.text, kind)
    rect.set('x', str(8 + 17.4*i))
    rect.set('width', '16.4')
    label.set('x', str(16.2 + 17.4*i))
# Assign stable IDs so Inkscape reports un-clipped object bboxes.
texts = list(root.iter(NS+'text'))
for i,node in enumerate(texts):
    node.set('id', f'qa-text-{i}')
tree.write(SVG, encoding='utf-8', xml_declaration=True)
subprocess.run(['inkscape',str(SVG),'--export-type=pdf','--export-filename='+str(SVG.with_suffix('.pdf'))],check=True,capture_output=True)
subprocess.run(['inkscape',str(SVG),'--export-type=png','--export-dpi=400','--export-filename='+str(SVG.with_suffix('.png'))],check=True,capture_output=True)
query = subprocess.run(['inkscape',str(SVG),'--query-all'],check=True,capture_output=True,text=True).stdout
boxes={}
for line in query.splitlines():
    a=line.split(',')
    if len(a)==5:
        boxes[a[0]]=tuple(float(v)*.75 for v in a[1:])  # CSS px -> pt
bad=[]
for node in texts:
    x,y,w,h=boxes[node.get('id')]
    if x < -.1 or y < -.1 or x+w > 439.2+.1 or y+h > 252+.1:
        bad.append({'text':node.text,'bbox_pt':[x,y,x+w,y+h]})
# Shared-baseline text pairs must not collide. Decorative legend swatches get
# independent tests against their own adjacent label areas.
collisions=[]
for i,a in enumerate(texts):
    for b in texts[i+1:]:
        if abs(float(a.get('y'))-float(b.get('y')))>.1: continue
        x,y,w,h=boxes[a.get('id')];u,v,q,r=boxes[b.get('id')]
        if min(x+w,u+q)-max(x,u)>.2 and min(y+h,v+r)-max(y,v)>.2:
            collisions.append([a.text,b.text])
for node in texts:
    if node.text and node.text.startswith('C: short conv'):
        x,y,w,h=boxes[node.get('id')];assert x+w<159
pdf=pymupdf.open(SVG.with_suffix('.pdf'))
spans=[s for p in pdf for b in p.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans'] if s['text'].strip()]
minimum=min(s['size'] for s in spans)
type3=sorted({f[3] for p in pdf for f in p.get_fonts() if f[2]=='Type3'})
result={'width_pt':pdf[0].rect.width,'min_font_pt':minimum,'type3':type3,'text_objects_checked':len(texts),'out_of_canvas':bad,'same_baseline_collisions':collisions,'layer_types':dict(collections.Counter(config['layer_types'])),'boundary':'Standalone figure only; no built-book verification or runtime measurements.'}
(ROOT/'parent_geometry.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
assert not bad and not collisions and minimum>=8 and not type3
