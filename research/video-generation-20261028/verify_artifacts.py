"""Validate research artefacts and evidence without running a model.
Run from anywhere: python3 /absolute/path/to/verify_artifacts.py
All reports are written inside this research directory.
"""
from pathlib import Path
import json, hashlib, re, ast, datetime
from collections import Counter
from PIL import Image, ImageChops
R=Path(__file__).resolve().parent
checks=[]
def check(name,condition,detail=None):
 checks.append({'check':name,'passed':bool(condition),'detail':detail})
def load(p): return json.loads((R/p).read_text())
required=['research.md','claims.json','proposed-insertions.md','figure-plan.md','figures/manifest.json','figures/QA.md','calculations.json','benchmark-evidence.json','source-catalogue.md','STATUS.md']
for p in required:check('required file '+p,(R/p).is_file() and (R/p).stat().st_size>0)
# Syntax only: no import/exec side effects from helper scripts.
for p in R.rglob('*.py'):
 try: ast.parse(p.read_text()); good=True
 except SyntaxError: good=False
 check('python syntax '+str(p.relative_to(R)),good)
for p in R.rglob('*.json'):
 try: json.loads(p.read_text()); good=True
 except Exception:good=False
 check('JSON syntax '+str(p.relative_to(R)),good)
M=load('sources/manifest.json');success=[m for m in M if m['status']=='retrieved']; failed=[m for m in M if m['status']!='retrieved']
for m in success:
 p=R/m['path'];check('raw hash '+m['id'],p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256'])
C=load('claims.json'); ids=[x['id'] for x in C['claims']]
check('unique claims',len(ids)==len(set(ids)),len(ids))
known={m['id']:m for m in success}
for c in C['claims']:
 check('claim boundaries '+c['id'],bool(c['support_boundaries']) and isinstance(c['unresolved_gaps'],list))
 if c['evidence_status'] not in ['proposal','manuscript_source_observation']:check('claim has primary evidence '+c['id'],bool(c['sources']))
 for s in c['sources']:
  check('claim source '+c['id']+'/'+s['source_id'],s['source_id'] in known and s['raw_sha256']==known[s['source_id']]['sha256'] and bool(s['retrieval_date']) and bool(s['section']))
# Numerical regression checks, independent expressions.
a=load('calculations.json')['wan22_ti2v5_121']
check('latent and token geometry',a['latent_frames']==31 and a['latent_height']==44 and a['latent_width']==80 and a['video_tokens']==31*22*40==27280)
check('FP32 initial latent bytes',a['initial_latent_FP32_bytes']==31*44*80*48*4==20951040)
check('attention core all branch evaluations',a['full_attention_core_FLOP_50_steps_two_CFG_branches']==4*(31*22*40)**2*3072*30*50*2)
check('hypothetical materialized score bytes',a['one_materialized_score_BF16_bytes']==24*(31*22*40)**2*2==35721523200)
check('container/timestamp duration separation',a['frame_timestamp_span_seconds']==5 and a['clip_seconds_container']==121/24)
check('aligned temporal endpoint inverse',1+4*(a['latent_frames']-1)==a['frames']==121)
wan_shape=(R/'sources/wan22_ti2v.txt').read_text()
check('endpoint convention matches archived implementation','(F - 1) // self.vae_stride[0] + 1' in wan_shape and 'size[1] // self.vae_stride[1]' in wan_shape and 'size[0] // self.vae_stride[2]' in wan_shape)
text=(R/'proposed-insertions.md').read_text()
check('substantive English text',len(re.findall(r'\b[A-Za-z]+\b',text))>2000)
check('non-instructive English',not re.search(r'\b(you|your)\b',text,re.I))
footdefs=set(re.findall(r'^\[\^([^\]]+)\]:',text,re.M));footuses=set(re.findall(r'\[\^([^\]]+)\](?!:)',text))
check('all English footnotes defined',footuses<=footdefs,sorted(footuses-footdefs))
source_urls=[m['url'] for m in success]
for p in ['research.md','proposed-insertions.md']:
 body=(R/p).read_text()
 for arxiv in set(re.findall(r'(?:arxiv\.org/(?:html|abs)/|arXiv:)(\d{4}\.\d{4,5})',body)):
  check('retrieved report identifier '+p+' '+arxiv,any(arxiv in u for u in source_urls))
 # Local figure image paths.
 for link in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',body):check('local image '+link,(R/link).is_file())
 # Adjacent Markdown table rows must keep column counts (avoids silent Pandoc table loss).
 prev=None
 for i,line in enumerate(body.splitlines(),1):
  if line.startswith('|'):
   cols=len(line.split('|'))-2
   if prev is not None:check(f'table columns {p}:{i}',cols==prev)
   prev=cols
  else:prev=None
F=load('figures/manifest.json')
for f in F['figures']:
 for key in ['svg','png','grayscale_png','actual_size_proof','generator','data']:check('figure asset '+f['id']+'/'+key,(R/f[key]).is_file())
 check('figure citation '+f['id'],f['png'] in text)
 check('figure claims '+f['id'],set(f['claim_ids'])<=set(ids))
 for anchor in f['related_prose_anchors']:check('figure prose anchor '+anchor,'{#'+anchor+'}' in text)
 im=Image.open(R/f['png']);check('figure correct pixels '+f['id'],list(im.size)==f['qa_geometry']['png_pixels'])
 check('figure PNG checksum '+f['id'],hashlib.sha256((R/f['png']).read_bytes()).hexdigest()==f['sha256_png'])
 check('figure width and label scale '+f['id'],f['intended_width_in']==8.5-1.2-1.2 and f['qa_geometry']['minimum_label_pt']>=9)
 q=f['qa_geometry'];check('geometry no collisions '+f['id'],not q['text_outside_canvas'] and not q['text_text_collisions'] and not q['arrow_segment_text_crossings'])
 rgb=im.convert('RGB');check('nonblank raster '+f['id'],ImageChops.difference(rgb,Image.new('RGB',rgb.size,'white')).getbbox() is not None)
 # Annotation/caption regressions are textual checks, not substitutes for raster inspection.
 import xml.etree.ElementTree as ET
 root=ET.parse(R/f['svg']).getroot(); labels=' '.join(root.itertext())
 prose_caption=next(line for line in text.splitlines() if line.startswith('Figure V'+('1' if f['id']=='video-latent-work' else '2')+' —'))
 check('prose and manifest captions synchronized '+f['id'],re.sub(r'\[\^[^\]]+\]','',prose_caption).rstrip('.')==f['caption'].rstrip('.'))
 check('detail crop exists '+f['id'],(R/'figures'/ (f['id']+'-detail.png')).is_file())
 check('print raster DPI '+f['id'],all(abs(x-350)<0.1 for x in im.info.get('dpi',(0,0))))
 if f['id']=='video-latent-work':
  check('V1 requested mechanism annotations',all(s in labels for s in ['Whole-clip denoising','≤512 prompt tokens','Loop: denoising / scheduler iteration','VAE stride (T, H, W) = (4, 16, 16)','1 + 4 × (31 − 1) = 121 frames']))
 else:
  check('V2 requested mechanism annotations',all(s in labels for s in ['High-noise expert checkpoint','Low-noise expert checkpoint','Denoising schedule progresses','Not two experts within one forward','If both experts stay on GPU: about 27B resident.','stage widths do not encode step counts']))
  check('V2 preserves rounded unsplit counts','About 14B active' in labels and '14B+13B' not in labels and '14B + 13B' not in labels)
# Assert actual primary-report date and performance scopes, avoiding draft citation/unit regressions.
abs2=(R/'sources/animate2_report_abs.txt').read_text()
check('Animate2 exact report and first-submission anchor','2608.06009' in abs2 and '6 Aug 2026' in abs2)
absd=(R/'sources/wan_dancer_abs.txt').read_text();check('Dancer first submission anchor','10 Jul 2026' in absd)
hr=(R/'sources/hunyuan_report.txt').read_text();check('Hunyuan source timing unit and hardware','Time/Step (s)' in hr and '8 NVIDIA H800 GPUs' in hr)
hc=load('sources/hunyuan_hfconfig.txt');check('Hunyuan exact configuration',hc['heads_num']==16 and hc['hidden_size']==2048 and hc['mm_double_blocks_depth']==54 and hc['patch_size']==[1,1,1])
lr=(R/'sources/ltx_report.txt').read_text();check('LTX source shape and schedule','121 frames at 720p' in lr and 'single-step Euler' in lr and 'CFG=1' in lr)
for key,date in [('035','2025-08-19'),('037','2026-03-05'),('040','2026-08-20'),('042','2026-10-23')]:
 release=load('sources/diffusers_release_v'+key+'.raw');check('engine release date v'+key,release['published_at'].startswith(date))
pins=load('sources/pinned-sources.json');check('all recorded pin checks match',all(x.get('same_bytes_as_snapshot') for x in pins),len(pins))
report={'validated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','checks_run':len(checks),'failed_checks':[c for c in checks if not c['passed']],'claim_count':len(ids),'source_counts':{'total':len(M),'retrieved':len(success),'failed_or_gated':len(failed)},'wan_public_inventory_entries':len(load('official-wan-model-inventory.json')),'figure_count':len(F['figures']),'checks':checks,'limitations':['Validation is artifact/source-hash/arithmetic/scope consistency, not independent factual peer review.','No video inference or deployment benchmark executed.','No historical cutoff checkout or final manuscript page inspection performed.','Three gated LTX2.5 requests remain inaccessible.']}
(R/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False,indent=2))
raise SystemExit(0 if report['status']=='PASS' else 1)
