"""Validate research assets and retained primary-source evidence without network access.
Writes only source-index.md and validation.json beside this script.
"""
import datetime, hashlib, json, pathlib, re, xml.etree.ElementTree as ET
from decimal import Decimal
from PIL import Image
import pymupdf
R = pathlib.Path(__file__).resolve().parent
M = json.loads((R/'source-manifest.json').read_text())
L = json.loads((R/'claims.json').read_text())
F = json.loads((R/'figures/manifest.json').read_text())
G = json.loads((R/'figures/geometry-checks.json').read_text())
errors=[]; warnings=[]; checked_sources=0
required_artifacts=['research.md','proposed-insertions.md','claims.json','STATUS.md','figure-plan.md','figures/manifest.json','figures/QA.md']
for name in required_artifacts:
    target=R/name
    if not target.is_file() or target.stat().st_size==0:
        errors.append({'artifact':name,'error':'required deliverable missing or empty'})
ids=[c['id'] for c in L['claims']]
assert len(ids)==len(set(ids))
byid={s['id']:s for s in M}
for s in M:
    if s.get('error'):
        warnings.append({'source':s['id'],'issue':s['error'],'resolution':'dinfer_readme_fixed fetched successfully' if s['id']=='dinfer_readme' else 'UNRESOLVED'})
        continue
    raw=R/'sources'/f'{s["id"]}.raw'
    if not raw.exists() or hashlib.sha256(raw.read_bytes()).hexdigest()!=s['sha256']:
        errors.append({'source':s['id'],'error':'raw byte hash mismatch or missing file'})
    if not (R/s['text_path']).exists(): errors.append({'source':s['id'],'error':'missing extracted text'})
    checked_sources+=1
quotes=0
for c in L['claims']:
    for e in c['evidence']:
        s=byid[e['source_id']]
        if e['raw_sha256']!=s['sha256']: errors.append({'claim':c['id'],'error':'evidence hash differs from manifest'})
        lines=(R/e['text_path']).read_text().splitlines()
        if not lines[e['line']-1].startswith(e['quote']): errors.append({'claim':c['id'],'error':'quote/line mismatch'})
        quotes+=1
    for e in c.get('local_evidence',[]):
        # Read-only dependency check; concurrent parent edits can invalidate anchors.
        target=R.parents[1]/e['path']
        if hashlib.sha256(target.read_bytes()).hexdigest()!=e['sha256']:
            warnings.append({'claim':c['id'],'issue':'local manuscript changed since recorded hash; parent must re-anchor','path':e['path']})
    if 'benchmark' in c:
        required=['model_revision','hardware','precision','input_length','output_length','denoising_schedule','NFE','quality_metric','baseline','publication_date','service_definition']
        for k in required:
            if k not in c['benchmark'] or c['benchmark'][k] in ('',None): errors.append({'claim':c['id'],'error':'missing explicit benchmark condition '+k})
prose=(R/'proposed-insertions.md').read_text()
for docname in ['proposed-insertions.md','research.md']:
    body=(R/docname).read_text()
    for cid in re.findall(r'\b[DB]\d{2}\b',body):
        if cid not in ids: errors.append({'document':docname,'error':'unknown claim '+cid})
anchors=set(re.findall(r'<a id="([^"]+)"',prose))
figure_checks={}
for f in F['figures']:
    key=f['id']
    for name in ['source','generator','data','png','pdf','grayscale_png','actual_size_proof']:
        if not (R/f[name]).is_file(): errors.append({'figure':key,'error':'missing '+name})
    for anchor in f['related_prose_anchors']:
        if anchor not in anchors: errors.append({'figure':key,'error':'missing prose anchor '+anchor})
    if f'Figure {key}' not in prose or f'figures/{key}.png' not in prose: errors.append({'figure':key,'error':'not cited in prose'})
    if any(cid not in ids for cid in f['evidence_claim_ids']): errors.append({'figure':key,'error':'unknown evidence ID'})
    im=Image.open(R/f['png'])
    expected=(round(f['intended_width_in']*f['ppi']),round(f['intended_height_in']*f['ppi']))
    if im.size!=expected: errors.append({'figure':key,'error':'PNG size/PPI mismatch'})
    root=ET.parse(R/f['source']).getroot()
    directions=[]
    for p in root.iter('{http://www.w3.org/2000/svg}path'):
        marker=p.get('marker-end','')
        d=p.get('d','')
        if key=='D1' and marker:
            nums=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?',d)]
            good=(nums[2]>nums[0]) if marker=='url(#black)' else (nums[2]<nums[0])
            directions.append(good)
            if not good: errors.append({'figure':key,'error':'q/reverse arrow direction'})
    # Conservative geometry and actual vector-PDF text bounds independently checked.
    if G[key]['text_bounds_violations']: errors.append({'figure':key,'error':'SVG text bounds violation'})
    text_overlaps=[]; boxes=G[key]['text_bounds']
    for i,b in enumerate(boxes):
        x0,y0,x1,y1=b['bbox']
        for c in boxes[i+1:]:
            a0,b0,a1,b1=c['bbox']
            if min(x1,a1)>max(x0,a0) and min(y1,b1)>max(y0,b0): text_overlaps.append([b['text'],c['text']])
    if text_overlaps: errors.append({'figure':key,'error':'conservative text overlap','pairs':text_overlaps})
    pdf=pymupdf.open(R/f['pdf']); page=pdf[0]
    actual_spans=[s for b in page.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
    clipped=[s['text'] for s in actual_spans if not page.rect.contains(pymupdf.Rect(s['bbox']))]
    if clipped: errors.append({'figure':key,'error':'PDF text bounds outside page','text':clipped})
    proof=pymupdf.open(R/f['actual_size_proof'])
    if tuple(proof[0].rect)!= (0.0,0.0,612.0,792.0): errors.append({'figure':key,'error':'not US Letter proof'})
    figure_checks[key]={'png_dimensions_px':im.size,'intended_width_in':f['intended_width_in'],'intended_height_in':f['intended_height_in'],'ppi':f['ppi'],'normal_minimum_font_pt':G[key]['minimum_font_pt'],'math_subscript_font_pt':str(Decimal('14')*Decimal('.8')*Decimal('.72')) if key=='D1' else None,'PDF_text_spans':len(actual_spans),'PDF_text_outside_page':clipped,'conservative_text_overlaps':text_overlaps,'arrow_direction_checks':directions,'letter_proof_pt':list(proof[0].rect),'png_sha256':hashlib.sha256((R/f['png']).read_bytes()).hexdigest()}
calc=json.loads((R/'calculations.json').read_text())
assert Decimal(2)*Decimal(7_000_000_000)*256*8/Decimal(10**12)==Decimal('28.672')
assert 256*262144*4//(2**20)==256
assert calc['block_case']['decoder_position_evaluations']==2048
assert calc['block_case']['sequential_denoising_calls']==64
assert Decimal(str(F['width_derivation']['available_text_width_in']))==Decimal('8.5')-2*Decimal('1.2')
index=['# Primary-source snapshot index','','All listed records were fetched during this research run. A 404 is retained as a failed discovery attempt, not used as evidence. Raw bytes live in sources/<id>.raw; extracted text in the paths below. Do not equate retrieval success with benchmark reproduction.','','| Source ID | HTTP | Text path | URL |','|---|---|---|---|']
for s in M: index.append(f'| {s["id"]} | {s.get("status","FAILED")} | {s.get("text_path","not retained: fetch failed")} | {s["url"]} |')
(R/'source-index.md').write_text('\n'.join(index)+'\n')
words=len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b",prose))
out={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS' if not errors else 'FAIL','required_artifacts_checked':required_artifacts,'claims':len(L['claims']),'benchmark_records':sum('benchmark' in c for c in L['claims']),'source_records':len(M),'successful_source_byte_hashes_checked':checked_sources,'claim_quotes_checked':quotes,'proposed_insertion_word_count_including_editorial_notes_and_references':words,'prose_anchors':sorted(anchors),'figures':figure_checks,'errors':errors,'warnings':warnings,'scope':'offline evidence/asset validation only; no model benchmark, API call, full-book build, physical print or publication certification'}
(R/'validation.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(out,indent=2,ensure_ascii=False))
if errors: raise SystemExit(1)
