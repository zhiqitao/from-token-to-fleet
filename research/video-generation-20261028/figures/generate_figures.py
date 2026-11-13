"""Original mechanism SVGs. No model inference and no vendor artwork.
Reproduce from repository root:
 python3 research/video-generation-20261028/figures/generate_figures.py
Requires Inkscape CLI and Pillow. All outputs stay beside this file.
"""
from pathlib import Path
import json, html, subprocess, hashlib, datetime
from PIL import Image, ImageOps
F=Path(__file__).resolve().parent
R=F.parent
A=json.loads((R/'calculations.json').read_text())['wan22_ti2v5_121']
W=610
WIDTH_IN=8.5-1.2-1.2
assert WIDTH_IN==6.1
INK='#1A1A1A'; BLUE='#27408B'; ORANGE='#E67E22'
class Drawing:
 def __init__(self,name,height):
  self.name=name; self.h=height; self.parts=[]; self.texts=[]; self.segments=[]; self.n=0
 def box(self,x,y,w,h,stroke=INK,fill='#FFFFFF',dash=False,sw=1.5,double=False):
  self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'+(' stroke-dasharray="5 4"' if dash else '')+'/>')
  if double:
   # Inner rule = double border marking the FINAL result, not an input. Carried
   # by stroke weight (and the extra ring), so the distinction survives grayscale.
   self.parts.append(f'<rect x="{x+3.5}" y="{y+3.5}" width="{w-7}" height="{h-7}" rx="3.5" fill="none" stroke="{stroke}" stroke-width="1"/>')
 def text(self,x,y,s,size=14,bold=False,anchor='middle'):
  self.n+=1; id=f't{self.n}'
  self.texts.append({'id':id,'text':s,'size':size})
  self.parts.append(f'<text id="{id}" x="{x}" y="{y}" font-size="{size}" font-weight="'+('bold' if bold else 'normal')+f'" text-anchor="{anchor}" fill="{INK}">{html.escape(s)}</text>')
 def arrow(self,pts,dash=False,color=INK):
  id=f'a{len(self.segments)}'; path='M '+' L '.join(f'{x},{y}' for x,y in pts)
  for p,q in zip(pts,pts[1:]): self.segments.append((id,p,q))
  self.parts.append(f'<path id="{id}" d="{path}" fill="none" stroke="{color}" stroke-width="1.7" marker-end="url(#arrow)"'+(' stroke-dasharray="5 4"' if dash else '')+'/>')
 def finish(self,caption,alt,anchors,claims):
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH_IN}in" height="{self.h/100}in" viewBox="0 0 {W} {self.h}"><title>{html.escape(caption)}</title><desc>{html.escape(alt)}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs><rect width="{W}" height="{self.h}" fill="white"/><g font-family="Liberation Sans, sans-serif">'+''.join(self.parts)+'</g></svg>'
  src=F/(self.name+'.svg'); src.write_text(svg)
  png=F/(self.name+'.png')
  subprocess.run(['inkscape',str(src),'--export-type=png',f'--export-filename={png}','--export-dpi=350'],check=True,capture_output=True)
  with Image.open(png) as im:
   im.load(); size=im.size
   ImageOps.grayscale(im).save(F/(self.name+'-gray.png'),dpi=(350,350))
   im.resize((round(WIDTH_IN*150),round(self.h/100*150)),Image.Resampling.LANCZOS).save(F/(self.name+'-actual-size-150dpi.png'),dpi=(150,150))
  # Inkscape gives actual font-shaped vector bounds in SVG CSS pixel units.
  query=subprocess.run(['inkscape',str(src),'--query-all'],check=True,text=True,capture_output=True).stdout
  # SVG physical 6.1in = 585.6 CSS px. Convert query bboxes to viewBox units.
  scale=W/(WIDTH_IN*96)
  bounds={}
  for row in query.splitlines():
   bits=row.split(',')
   if len(bits)==5:
    try: bounds[bits[0]]=tuple(float(x)*scale for x in bits[1:])
    except ValueError: pass
  out=[]; collisions=[]; crossings=[]
  tb=[]
  for t in self.texts:
   assert t['id'] in bounds,t
   x,y,w,h=bounds[t['id']]; b=(x,y,x+w,y+h); tb.append((t['id'],b))
   if x<0 or y<0 or x+w>W or y+h>self.h: out.append(t['id'])
  for i,(id,a) in enumerate(tb):
   for jd,b in tb[i+1:]:
    if max(a[0],b[0])<min(a[2],b[2]) and max(a[1],b[1])<min(a[3],b[3]): collisions.append((id,jd))
  def intersects(p,q,b):
   # Exact slab intersection, not endpoint/midpoint sampling.
   lo,hi=0.0,1.0
   for v,d,mn,mx in [(p[0],q[0]-p[0],b[0],b[2]),(p[1],q[1]-p[1],b[1],b[3])]:
    if d==0:
     if not mn<v<mx:return False
    else:
     t1,t2=(mn-v)/d,(mx-v)/d; lo=max(lo,min(t1,t2));hi=min(hi,max(t1,t2))
     if lo>=hi:return False
   return True
  for aid,p,q in self.segments:
   for tid,b in tb:
    if intersects(p,q,b):crossings.append((aid,tid))
  qa={'figure':self.name,'png_pixels':size,'intended_inches':[WIDTH_IN,self.h/100],'dpi':350,'minimum_label_pt':min(t['size'] for t in self.texts)*WIDTH_IN*72/W,'text_outside_canvas':out,'text_text_collisions':collisions,'arrow_segment_text_crossings':crossings,'method':'actual Inkscape shaped glyph bounds; exact segment/bbox intersection; raster inspection still required'}
  assert not out and not collisions and not crossings,qa
  return {'id':self.name,'svg':str(src.relative_to(R)),'png':str(png.relative_to(R)),'grayscale_png':f'figures/{self.name}-gray.png','actual_size_proof':f'figures/{self.name}-actual-size-150dpi.png','generator':'figures/generate_figures.py','data':'figures/figure-data.json','reproduction_command':'python3 research/video-generation-20261028/figures/generate_figures.py','intended_width_in':WIDTH_IN,'intended_height_in':self.h/100,'caption':caption,'alt_text':alt,'related_prose_anchors':anchors,'claim_ids':claims,'qa_geometry':qa,'sha256_png':hashlib.sha256(png.read_bytes()).hexdigest()}

v=Drawing('video-latent-work',600)
v.text(305,23,'Whole-clip denoising: Wan2.2 TI2V-5B',17,True)
for x,s in [(10,'Prompt'),(218,'Optional reference image'),(426,'Initial noise (FP32)')]:
 v.box(x,48,174,42,BLUE,'#F1F4FA');v.text(x+87,74,s,14)
v.box(10,117,174,60,BLUE,'#F1F4FA');v.text(97,141,'UMT5-XXL',15,True);v.text(97,163,'≤512 prompt tokens',13)
v.box(218,117,174,60,BLUE,'#F1F4FA');v.text(305,141,'VAE encode',15,True);v.text(305,163,'I2V condition only',13)
v.box(426,117,174,60,BLUE,'#F1F4FA');v.text(513,140,'Latent: T × H × W × C',14,True);v.text(513,163,'31 × 44 × 80 × 48',13)
v.arrow([(97,90),(97,117)])
v.arrow([(305,90),(305,117)])
v.arrow([(513,90),(513,117)])
v.box(40,213,530,126,ORANGE,'#FFF5EB')
v.text(305,238,'Wan2.2 dense TI2V-5B + scheduler',16,True)
v.text(305,265,'Patch (1, 2, 2): N = 27,280 video tokens',14)
v.text(305,292,'50 steps × 2 CFG branch evaluations',14)
v.text(305,319,'Loop: denoising / scheduler iteration',13)
v.arrow([(97,177),(97,195),(124,195),(124,213)],True,BLUE)
v.arrow([(305,177),(305,213)],True,BLUE)
v.arrow([(513,177),(513,213)])
v.arrow([(570,240),(591,240),(591,323),(570,323)])
v.arrow([(305,339),(305,373)])
v.box(105,373,400,86,ORANGE,'#FFF5EB');v.text(305,397,'VAE decode',16,True)
v.text(305,420,'VAE stride (T, H, W) = (4, 16, 16)',13)
v.text(305,443,'Aligned endpoint: 1 + 4 × (31 − 1) = 121 frames',13)
v.arrow([(305,459),(305,490)])
v.box(153,490,304,44,BLUE,'#F1F4FA',sw=2.5,double=True);v.text(305,517,'121 frames · 704 (H) × 1280 (W) · 24 fps',14)
v.text(305,562,'Solid: data/state flow. Dashed: denoiser conditioning. Blue: data/state. Orange: compute.',13)
v.text(305,582,'Token partitioning adds communication between devices.',13)
cap1='Figure V1 — Wan2.2 TI2V-5B whole-clip denoising. The T2V worked example starts from a 31×44×80×48 latent tensor and patchifies it into 27,280 video tokens. The fetched implementation uses T_l=(F−1)//4+1, H_l=H//16 and W_l=W//16. For aligned F=4k+1, F=1+4(T_l−1): 31 latent time positions correspond to 121 frames. The optional I2V branch is separate from the T2V budget. The feedback loop is denoising/scheduler iteration, not architectural recurrence. Fifty upstream timesteps use two CFG branch evaluations each. The VAE decode is not autoregressive text decode. [1P][FACT] geometry and loop; [1P][DERIVED] aligned inverse and token count. Schematic, not a latency or peak-memory measurement.'
alt1='Prompt encoding, labeled at most 512 prompt tokens, and optional reference-image VAE encoding condition a whole-clip denoising block. Initial FP32 latent noise enters from the right. The feedback loop is labeled denoising / scheduler iteration. The VAE stride is temporal 4 and spatial 16 by 16. The aligned endpoint formula 1+4 times (31 minus 1) gives 121 output frames at 1280 by 704 pixels and 24 frames per second. Solid data/state arrows and dashed conditioning arrows are distinct without color.'
f1=v.finish(cap1,alt1,['video-resource-budget','video-work-unit'],['VG005','VG006','VG007','VG008','VG009','VG010','VG024','VG025','VG029','VG031'])

v=Drawing('wan-noise-experts',395)
v.text(305,23,'Wan2.2 A14B: active ≠ resident parameters',17,True)
v.box(18,47,574,104,BLUE,'#F1F4FA')
v.text(305,69,'Both-on-GPU assumption: about 27B resident parameters',14,True)
v.box(40,86,242,48,BLUE);v.text(161,115,'High-noise expert checkpoint',14)
v.box(328,86,242,48,BLUE);v.text(449,115,'Low-noise expert checkpoint',14)
v.arrow([(161,134),(161,225)],True,BLUE)
v.arrow([(449,134),(449,225)],True,BLUE)
v.text(305,175,'Denoising schedule progresses',13)
v.text(305,198,'Not two experts within one forward',13)
v.box(40,225,242,54,ORANGE,'#FFF5EB');v.text(161,247,'High-noise stage',15,True);v.text(161,269,'Only high-noise expert runs',13)
v.box(328,225,242,54,ORANGE,'#FFF5EB');v.text(449,247,'Low-noise stage',15,True);v.text(449,269,'Only low-noise expert runs',13)
v.arrow([(282,252),(328,252)])
v.text(305,305,'About 14B active per forward evaluation.',13)
v.text(305,329,'If both experts stay on GPU: about 27B resident.',13)
v.text(305,353,'Schematic: stage widths do not encode step counts.',13)
v.text(305,377,'Offload lowers GPU residency but adds weight transfers.',13)
cap2='Figure V2 — Wan2.2 A14B selects experts as the denoising schedule progresses. The stage-transition arrow spans timestep evaluations; it does not chain both experts inside one forward evaluation. Each expert is stored in its respective checkpoint. Both occupy GPU weight memory only if both remain on GPU; only the selected expert runs in a branch evaluation. Official rounded counts are about 27B total and about 14B active, not an inferred per-expert parameter split. Stage widths are schematic and do not encode step counts. Explicit offload changes residency and adds transfers. This is a different model from the dense 5B example. [1P][FACT].'
alt2='A blue resident-bank outline encloses high-noise and low-noise expert checkpoints. Dashed links connect each checkpoint to its stage. Text labels progress across the denoising schedule and states that two experts do not run within one forward evaluation. A rightward stage arrow joins high-noise to low-noise processing across timesteps. About 14 billion parameters are active per evaluation; about 27 billion are GPU-resident only if both experts remain on GPU. Stage widths do not encode step counts. Offload adds weight transfers.'
f2=v.finish(cap2,alt2,['video-expert-residency'],['VG002','VG003','VG004','VG030','VG031'])
manifest={'schema_version':'1.0','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'page_format':'US Letter 8.5×11 in','text_width_source':'render/latex/book.tex:7; render/latex/book.sty:61','text_width_in':WIDTH_IN,'renderer':'Inkscape CLI; version recorded in QA.md','figures':[f1,f2]}
(F/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(F/'figure-data.json').write_text(json.dumps({'worked_geometry':A,'a14b_counts':'Official rounded total≈27B; active≈14B','evidence_claims':sorted(set(f1['claim_ids']+f2['claim_ids']))},indent=2)+'\n')
(F/'geometry-QA.json').write_text(json.dumps([f1['qa_geometry'],f2['qa_geometry']],indent=2)+'\n')
# Raster details, not merely SVG text extraction.
for name,rect in [('video-latent-work',(0,100,610,465)),('wan-noise-experts',(15,45,595,385))]:
 with Image.open(F/(name+'.png')) as im:
  scale=im.width/610
  x0,y0,x1,y1=rect
  im.crop((round(x0*scale),round(y0*scale),round(x1*scale),round(y1*scale))).save(F/(name+'-detail.png'),dpi=(350,350))
print(json.dumps([f1['qa_geometry'],f2['qa_geometry']],indent=2))
