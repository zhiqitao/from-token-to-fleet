#!/usr/bin/env python3
"""Check figure delivery, physical geometry and explicitly derived arithmetic."""
import datetime
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parent
ASSIGNMENT = ROOT.parent
SVG = '{http://www.w3.org/2000/svg}'


def luminance(color):
    rgb = [int(color[i:i+2],16)/255 for i in [1,3,5]]
    linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    return .2126*linear[0]+.7152*linear[1]+.0722*linear[2]


def contrast(first, second):
    a,b = sorted([luminance(first),luminance(second)])
    return (b+.05)/(a+.05)


def main():
    manifest = json.loads((ROOT/'manifest.json').read_text())
    geometry = json.loads((ROOT/'geometry-checks.json').read_text())
    claims = {r['id'] for r in json.loads((ASSIGNMENT/'claims.json').read_text())}
    prose = (ASSIGNMENT/'proposed-insertions.md').read_text()
    data = json.loads((ROOT/'data.json').read_text())
    assert len(manifest['figures']) == 2
    assert manifest['text_width_in'] == 6.1
    assert data['bytes_per_token'] == 2*16*4*256*2
    assert data['full_attention_component_GiB'] == {'131072':8,'262144':16}
    ex = data['adaptive_example']
    assert ex['baseline_work'] == 9 and ex['stopped_work'] == 7
    assert abs(ex['total_work_reduction'] - 2/9) < 1e-12
    assert ex['core_only_reduction'] == .25
    assets = {}
    for fig, check in zip(manifest['figures'], geometry):
        assert fig['id'] == check['id']
        assert set(fig['evidence_claim_ids']).issubset(claims)
        assert fig['png'] in prose
        assert fig['caption'] and fig['alt_text'] and fig['related_prose_anchors']
        assert check['min_font_pt'] >= 9 and not check['text_collisions']
        assert check['label_bounds'] == 'PASS'
        assert fig['intended_width_in'] == 6.1
        svg = ET.parse(ASSIGNMENT/fig['source']).getroot()
        assert svg.attrib['width'] == '6.1in'
        for path in [fig['source'],fig['png'],fig['vector_pdf'],fig['grayscale'],fig['placement_proof'],*fig['detail_crops']]:
            target = ASSIGNMENT/path
            assert target.is_file() and target.stat().st_size > 0, path
            assets[path] = hashlib.sha256(target.read_bytes()).hexdigest()
        im = Image.open(ASSIGNMENT/fig['png'])
        assert im.width == 2440 and abs(im.info['dpi'][0]-400)<.1
        doc = fitz.open(ASSIGNMENT/fig['vector_pdf'])
        assert abs(doc[0].rect.width-439.2)<.02
        assert abs(doc[0].rect.height-fig['intended_height_in']*72)<.02
        # Check actual vector text, not only the SVG label source bounds.
        spans = [s for b in doc[0].get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
        assert spans, ('missing extractable vector text', fig['id'])
        assert min(s['size'] for s in spans) >= 9, ('PDF font size',fig['id'])
        assert all(fitz.Rect(s['bbox']) in doc[0].rect for s in spans)
        doc.close()
        proof = fitz.open(ASSIGNMENT/fig['placement_proof'])
        assert tuple(proof[0].rect) == (0.,0.,612.,792.)
        assert 'RESEARCH PLACEMENT PROOF' in proof[0].get_text()
        proof.close()
        if fig['id'] == 'mt-1-history-state':
            kv = [r for r in svg.iter(SVG+'rect') if r.attrib.get('width') == '38']
            assert len(kv) == 6
            groups = [kv[:1],kv[1:3],kv[3:]]
            centers=[]
            for group, expected in zip(groups,[130,310,490]):
                left = min(float(r.attrib['x']) for r in group)
                right = max(float(r.attrib['x'])+float(r.attrib['width']) for r in group)
                centers.append((left+right)/2)
                assert abs(centers[-1]-expected)<1e-9
            assert centers == [130.,310.,490.]
        else:
            weight_box = next(r for r in svg.iter(SVG+'rect') if r.attrib.get('width') == '450')
            left = float(weight_box.attrib['x'])
            right = left + float(weight_box.attrib['width'])
            assert all(left <= x <= right for x in [130,310,490])
    # Conservative text contrast: dark labels on all fills; inactive text on white.
    backgrounds=['#ffffff','#eef3f8','#fbefee','#fff5df']
    text_min=min(contrast('#202020',bg) for bg in backgrounds)
    inactive=contrast('#555555','#ffffff')
    assert text_min>=7 and inactive>=7
    stroke_min=min(contrast(a,b) for a,b in [('#3a6ea5','#eef3f8'),('#b02a22','#fbefee'),('#8a5700','#fff5df')])
    assert stroke_min>=3
    figures_in_text = re.findall(r'!\[[^\]]*\]\((figures/[^)]+)\)',prose)
    assert len(figures_in_text)==2
    result=dict(status='PASS', checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                figure_count=2, all_referenced_assets_exist=True, svg_and_vector_pdf_geometry='PASS',
                min_pdf_font_pt=9.36, label_and_pdf_bounds='PASS', png_effective_ppi=400,
                exact_KV_group_centers=[130,310,490], all_weight_branches_attached=True,
                text_contrast_min=round(min(text_min,inactive),2), colored_stroke_contrast_min=round(stroke_min,2),
                worked_examples='PASS; derived/illustrative, not measured', asset_sha256=assets,
                vision_results='See QA.md; this script does not make visual judgments',
                integrated_manuscript_layout='NOT VERIFIED', hardcopy='NOT VERIFIED')
    (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='asset_sha256'},indent=2))

if __name__ == '__main__':
    main()
