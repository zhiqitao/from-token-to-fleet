#!/usr/bin/env python3
"""Validate deliverable linkage, source hashes and generated assets; no GPU claims."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
from PIL import Image, ImageChops

R=Path(__file__).resolve().parent
required=['research.md','proposed-insertions.md','claims.json','independent_calculations.py','calculations.json','figure-plan.md','figures/manifest.json','figures/QA.md','figures/checks.json','STATUS.md']
for p in required:
    assert (R/p).is_file() and (R/p).stat().st_size>0,p
ledger=json.loads((R/'claims.json').read_text())
claim_ids={c['id'] for c in ledger['claims']}
assert len(claim_ids)==len(ledger['claims'])==38
sources={s['id']:s for s in ledger['sources']}
for sid,s in sources.items():
    p=R/s['raw_path']
    assert p.is_relative_to(R) and sha256(p.read_bytes()).hexdigest()==s['sha256'],sid
for c in ledger['claims']:
    for ref in c['source_refs']:
        t=(R/sources[ref['source_id']]['text_path']).read_text()
        assert ref['text_anchor'].casefold() in t.casefold(),c['id']
manifest=json.loads((R/'figures/manifest.json').read_text())
checks=json.loads((R/'figures/checks.json').read_text())
prose=(R/'proposed-insertions.md').read_text()
assert not re.search(r'\b(you|your)\b',prose,re.I)
word_count=len(re.findall(r"\b[\w'-]+\b",prose))
assert word_count>2000,word_count
assert 'Figure QF1' in prose and 'Figure QF2' in prose
assert len(manifest['figures'])==2
results=[]
for f,c in zip(manifest['figures'],checks['figures']):
    assert f['id']==c['id']
    for key in ['source','generator','png','grayscale_png','letter_size_proof','whole_inspection','detail_inspection']:
        p=R/f[key]
        assert p.is_relative_to(R) and p.is_file(),(f['id'],key)
    for a in f['related_prose_anchors']:
        assert f'id="{a}"' in prose,(f['id'],a)
    assert set(f['claim_ids']) <= claim_ids
    assert f['intended_width_in']==6.1 and f['caption'] and f['alt_text']
    tree=ET.parse(R/f['source'])
    texts=tree.findall('.//{http://www.w3.org/2000/svg}text')
    assert len(texts)==c['text_count']
    assert all(float(t.attrib['font-size'])>=9 for t in texts)
    with Image.open(R/f['png']) as im:
        im.load()
        assert im.width==3660 and list(im.size)==c['png_pixels']
        assert abs(im.info['dpi'][0]-600)<.1
        assert abs(im.width/im.info['dpi'][0]-6.1)<.001
        expected_gray=im.convert('L')
        actual_size=im.size
    with Image.open(R/f['grayscale_png']) as im:
        assert im.mode=='L' and im.size==actual_size
        assert ImageChops.difference(im,expected_gray).getbbox() is None
    with Image.open(R/f['letter_size_proof']) as im:
        assert im.size==(1275,1650)
        assert abs(im.info['dpi'][0]-150)<.1
    assert c['minimum_font_pt']>=9 and c['text_overlap_count']==0
    assert sha256((R/f['source']).read_bytes()).hexdigest()==c['svg_sha256']
    assert sha256((R/f['png']).read_bytes()).hexdigest()==c['png_sha256']
    results.append({'id':f['id'],'svg_xml':'parsed','png_pixels':actual_size,'dpi':'600 verified','font_min_pt':c['minimum_font_pt'],'prose_anchors':'all present','claim_ids':'all valid','grayscale':'pixel-identical luminance conversion','hashes':'verified'})
report={'validated_utc':datetime.now(timezone.utc).isoformat(),'status':'passed','scope':'Deliverable and asset validation; not publication readiness or inference validation','required_files':required,'claims':len(claim_ids),'successful_unique_sources':len(sources),'retained_retrieval_failures':len(ledger['retrieval_failures']),'all_source_hashes_and_claim_anchors':'verified','candidate_prose_word_tokens':word_count,'figure_count':len(results),'figures':results,'contrast_ratio':checks['text_vs_darkest_text_background_contrast'],'limitations':['no integrated book rendering','no physical print','no inference or quality measurements','SVG independent-engine rendering not performed']}
(R/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
