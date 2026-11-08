"""Expand task-local citations and verify deliverables without changing manuscript files."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import re
import subprocess
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
registry=json.loads((ROOT/'claims.json').read_text())
sources={x['id']:x for x in registry['sources']}
ids={x['id'] for x in registry['claims']}
summary={}
for name in ['intel-xpu-research.md','proposed-insertions.md']:
    path=ROOT/name
    text=path.read_text().split('<!-- REFERENCES -->')[0]
    cited=set(map(int,re.findall(r'\[(\d+)\]',text)))
    for first,last in re.findall(r'\[(\d+)\][–-]\[(\d+)\]',text):
        cited.update(range(int(first),int(last)+1))
    assert cited<=set(sources),(name,cited-set(sources))
    refs=[]
    for i in sorted(cited):
        s=sources[i]
        date=s.get('publication_date') or 'not established in fetched source metadata; see claim event date'
        note='' if s['usable'] else ' EXCLUDED FROM SUPPORT: '+s['exclusion_reason']
        refs.append(f"[{i}] {s['title']} — {s['url']}\n    Publication/release: {date}. Retrieved UTC: {s['retrieved_at']}. Provenance: {s['provenance']}.{note}")
    path.write_text(text+'<!-- REFERENCES -->\n\n'+'\n\n'.join(refs)+'\n')
    summary[name]={'reference_count':len(cited),'bytes':path.stat().st_size}
# Every evidence excerpt must still equal the exact source lines.
for claim in registry['claims']:
    assert claim['evidence'],claim['id']
    for evidence in claim['evidence']:
        src=sources[evidence['source_id']]
        assert src['usable'],claim['id']
        lines=(ROOT/evidence['snapshot']).read_text().splitlines()
        assert '\n'.join(lines[evidence['line_start']-1:evidence['line_end']])==evidence['excerpt']
        assert evidence['matched_text'].lower() in evidence['excerpt'].lower()
# First-person book voice and explicit figure reference.
prose=(ROOT/'proposed-insertions.md').read_text().split('## References used')[0]
assert not re.search(r'\b(you|your)\b',prose,re.I)
assert 'figures/intel-backend-paths.png' in prose and 'IX-F1' in prose
manifest=json.loads((ROOT/'figures/manifest.json').read_text())
for figure in manifest['figures']:
    assert set(figure['claim_ids'])<=ids
    for key in ['editable_source','generator','rendered_png','vector_pdf','grayscale_png','placement_proof']:
        assert (ROOT/figure[key]).is_file(),figure[key]
    for name,digest in figure['sha256'].items():
        assert hashlib.sha256((ROOT/'figures'/name).read_bytes()).hexdigest()==digest
    image=Image.open(ROOT/figure['rendered_png'])
    assert image.width/figure['intended_width_in']>=299.99
    assert image.height/figure['intended_height_in']>=299.99
    pdf=fitz.open(ROOT/figure['vector_pdf'])
    widths=pdf[0].rect.width/72
    assert abs(widths-figure['intended_width_in'])<.001
    spans=[s for block in pdf[0].get_text('dict')['blocks'] if 'lines' in block for line in block['lines'] for s in line['spans']]
    assert min(s['size'] for s in spans)>10
    summary['figure']={'count':len(manifest['figures']),'png_pixels':list(image.size),'measured_ppi':image.width/widths,'pdf_width_in':widths,'minimum_pdf_text_font_pt':min(s['size'] for s in spans),'caption_and_alt_present':bool(figure['caption'] and figure['alt_text'])}
# Scope inventory. These are provenance hashes, NOT a claim of independent PDF-page review.
read_numbers=[5,*range(7,19),20,21,27]
inventory=[]
for n in read_numbers:
    p=REPO/f'design/manuscript/chapter-{n:02d}/chapter-{n:02d}.md'
    inventory.append({'path':str(p.relative_to(REPO)),'sha256_at_finalization':hashlib.sha256(p.read_bytes()).hexdigest(),'lines':len(p.read_text().splitlines()),'review_status':'substantive source-text reading in this research run; not a full rendered-page visual audit'})
master=REPO/'review/publication_v2_20261028/MASTER_INSTRUCTIONS.md'
proof=REPO/'review/publication_v2_20261028/baseline/from-token-to-fleet-v20260913.pdf'
doc=fitz.open(proof)
proof_hash=hashlib.sha256(proof.read_bytes()).hexdigest()
assert len(doc)==361 and doc[0].rect.width==612 and doc[0].rect.height==792
assert proof_hash=='66f8392d6b768de7af4695b3d93d70b48858eb75a944020dbcfa9f4d1768b758'
(ROOT/'manuscript-read-inventory.json').write_text(json.dumps({'scope':'text-reading coverage, not release certification','chapters':inventory,'master_instruction_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'baseline_pdf':{'path':str(proof.relative_to(REPO)),'sha256':proof_hash,'pages':len(doc),'page_size_pt':list(doc[0].rect)[2:]}},indent=2)+'\n')
summary.update(generated_at=dt.datetime.now(dt.timezone.utc).isoformat(),claim_count=len(registry['claims']),source_records=len(sources),usable_source_records=sum(bool(x['usable']) for x in sources.values()),excluded_source_records=[x for x,s in sources.items() if not s['usable']],chapter_text_read_count=len(inventory),arithmetic_verified=True,scope='Only task-local deliverables are written; baseline PDF and manuscript are read-only inputs.',runtime_benchmark='NOT RUN',full_manuscript_visual_review='NOT PERFORMED')
summary['git_status_at_finalization']=subprocess.run(['git','status','--short'],cwd=REPO,capture_output=True,text=True,check=True).stdout.splitlines()
(ROOT/'verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
