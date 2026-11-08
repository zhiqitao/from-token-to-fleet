"""Freeze supplied audit standard and current artifacts; do not certify inspection."""
from pathlib import Path
import csv
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
import pymupdf

REPO = Path(__file__).resolve().parents[2]
ROOT = Path(__file__).resolve().parent
STANDARD = Path('/home/ubuntu/.hermes/profiles/muta/cache/documents/native-inputs/c8b84b609447da9f47111b2ed54b47b86c7fcb6b708a79c23e7e3f2ef7bbe3cd/doc_75efc9fb04b3_GPT-6.1-Sol_Publishing_Readiness_Master_Review_Instructions_v2.md')
for folder in ['baseline', 'text', 'renders', 'work', 'logs']:
    (ROOT / folder).mkdir(exist_ok=True)
shutil.copy2(STANDARD, ROOT / 'MASTER_INSTRUCTIONS.md')
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
artifacts = []
for source in sorted((REPO / 'render/build').glob('*.pdf')):
    with pymupdf.open(source) as doc:
        item = {'path': str(source.relative_to(REPO)), 'sha256': sha(source), 'bytes': source.stat().st_size, 'pages': len(doc), 'dimensions_pt': sorted(set((round(p.rect.width, 3), round(p.rect.height, 3)) for p in doc)), 'metadata': doc.metadata, 'page_labels': doc.get_page_labels()}
    artifacts.append(item)
    if source.name in ['from-token-to-fleet-v20260913.pdf', 'from-token-to-fleet-v20260913-full.pdf', 'from-token-to-fleet-v20260913-cover.pdf']:
        shutil.copy2(source, ROOT / 'baseline' / source.name)
proof = ROOT / 'baseline/from-token-to-fleet-v20260913.pdf'
doc = pymupdf.open(proof)
pages, figures, tables = [], [], []
for i, page in enumerate(doc):
    text = page.get_text()
    (ROOT / 'text' / f'page-{i+1:04d}.txt').write_text(text)
    pages.append({'pdf_page': i+1, 'printed_page': page.get_label(), 'T': 'NOT CHECKED', 'V': 'NOT CHECKED', 'Q': 'NOT CHECKED', 'R': 'NOT CHECKED', 'status': 'OPEN', 'note': 'Text extracted; extraction is not review.', 'proof_sha256': sha(proof)})
    for match in re.finditer(r'(?m)^Figure\s+(\d+\.\d+)\s*[:.—–-]', text):
        figures.append({'figure_id': match.group(1), 'pdf_page': i+1, 'printed_page': page.get_label(), 'caption_anchor': text[match.start():match.start()+300].replace('\n',' '), 'technical': 'NOT VERIFIED', 'print': 'NOT VERIFIED', 'design': 'NOT VERIFIED', 'pedagogy': 'NOT VERIFIED', 'verdict': 'NOT VERIFIED', 'inspection': 'OPEN'})
    for match in re.finditer(r'(?m)^Table\s+(\d+[-–‑]\d+)\b', text):
        tables.append({'table_id': match.group(1), 'pdf_page': i+1, 'printed_page': page.get_label(), 'anchor':text[match.start():match.start()+160].replace('\n',' '), 'status':'NOT CHECKED'})
for name, rows in [('pages',pages),('figures_candidates',figures),('tables_candidates',tables)]:
    (ROOT / f'{name}.json').write_text(json.dumps(rows, indent=2))
    if rows:
        with (ROOT / f'{name}.csv').open('w') as stream:
            writer=csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
state = {'started_utc':datetime.now(timezone.utc).isoformat(), 'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(), 'baseline_dirty_status':subprocess.check_output(['git','status','--short'],cwd=REPO,text=True), 'standard_sha256':sha(ROOT/'MASTER_INSTRUCTIONS.md'), 'artifacts':artifacts, 'primary_proof':str(proof), 'primary_sha256':sha(proof), 'phase':'BASELINE_FROZEN_INVENTORY_PENDING', 'page_count':len(doc), 'figure_caption_candidates':len(figures), 'table_caption_candidates':len(tables), 'coverage':{'T':0,'V':0,'Q':0,'R':0}, 'limitations':['Existing uncommitted figures preserved; do not overwrite.','Caption regex yields candidates, not a verified complete inventory.','Interior and cover-combined PDF must be reconciled before choosing release artifact.','No physical print proof available.']}
(ROOT/'state.json').write_text(json.dumps(state,indent=2))
(ROOT/'STATUS.md').write_text('# Publication v2 review/rework checkpoint\n\nBaseline frozen. Inventory and independent review started.\n\nNo pages or figures certified. Read state.json for immutable artifact identity.\n\nNext: reconcile caption inventory, complete text/quantitative/evidence/visual passes, consolidate findings, correct confirmed defects, rebuild, and reverify. User v2 gates override older convergence shortcuts.\n')
print(json.dumps({k:v for k,v in state.items() if k not in ['baseline_dirty_status','artifacts']},indent=2))
print(json.dumps(artifacts,indent=2))
