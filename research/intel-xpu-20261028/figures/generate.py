"""Original Intel backend dependency figure. All writes stay in this directory.
Reproduce from repository root: python research/intel-xpu-20261028/figures/generate.py
Requires PyMuPDF and Pillow (already available in this execution environment).
"""
from pathlib import Path
import hashlib
import html
import json
import fitz
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
ROOT.mkdir(exist_ok=True)
W,H = 610,630
WIDTH_IN = 8.5-1.2-1.2
SCALE_PT = WIDTH_IN*72/W
DPI = 300
INK='#20252A'; BLUE='#27408B'; ORANGE='#E67E22'; RED='#C0392B'; GREEN='#1E6B42'
font=fitz.Font('helv')
elements=[]; labels=[]; rectangles=[]; arrows=[]

def text(x,y,value,size=14,bold=False,anchor='middle',color=INK):
    width=font.text_length(value,fontsize=size)
    left=x-width/2 if anchor=='middle' else x
    # Helvetica bold is slightly wider; use its actual metrics for checks.
    if bold:
        width=fitz.Font('hebo').text_length(value,fontsize=size)
        left=x-width/2 if anchor=='middle' else x
    bbox=[left,y-size*1.08,left+width,y+size*.25]
    labels.append({'text':value,'size_units':size,'placed_font_pt':size*SCALE_PT,'bbox_units':bbox})
    assert bbox[0]>=5 and bbox[2]<=W-5 and bbox[1]>=3 and bbox[3]<=H-3,(value,bbox)
    elements.append(f'<text x="{x}" y="{y}" font-family="Helvetica,Arial,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color}">{html.escape(value)}</text>')

def box(x,y,w,h,fill='#F5F5F3',stroke=INK,stroke_width=1.2):
    rectangles.append([x,y,x+w,y+h])
    elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>')

def arrow(x,y1,y2,qualification=False):
    assert y2>y1
    arrows.append([x,y1,y2])
    # Explicit segments: the SVG conversion used here drops stroke-dasharray.
    segments=[(start,min(start+4,y2-9)) for start in range(y1,y2-9,8)] if qualification else [(y1,y2-6)]
    for start,end in segments:
        elements.append(f'<line x1="{x}" y1="{start}" x2="{x}" y2="{end}" stroke="{INK}" stroke-width="1.7"/>')
    elements.append(f'<polygon points="{x-4},{y2-7} {x+4},{y2-7} {x},{y2}" fill="{INK}"/>')

text(305,26,'Device visibility is not a validated serving path',18,True)
text(305,49,'Solid: dependencies. Dashed: qualify the complete path.',14)
cols=[
 {'x':12,'title':'Intel GPU','engine':['vLLM XPU / SGLang XPU','or llama.cpp SYCL'],
  'entry':['torch.xpu','or engine-native SYCL'],
  'runtime':['GPU kernels / libraries','SYCL + Level Zero','matching GPU driver'],
  'device':['Discrete GPU','or integrated GPU']},
 {'x':212,'title':'Intel Gaudi','engine':['Gaudi-specific engine','and compatible release'],
  'entry':['PyTorch hpu','Gaudi software stack'],
  'runtime':['Gaudi execution kernels','HCCL for collectives','matching Gaudi driver'],
  'device':['Gaudi accelerator','not an Intel GPU']},
 {'x':412,'title':'Client NPU','engine':['OpenVINO GenAI','supported NPU models'],
  'entry':['OpenVINO NPU plugin','not torch.xpu'],
  'runtime':['NPU execution kernels','compatible NPU runtime','matching NPU driver'],
  'device':['Client NPU','not the integrated GPU']}
]
rows=[(98,78,'engine','Serving engine'),(204,72,'entry','Backend entry'),(304,92,'runtime','Kernels / runtime'),(424,64,'device','Hardware')]
for col in cols:
    x=col['x'];cx=x+93
    text(cx,80,col['title'],18,True)
    for y,h,key,heading in rows:
        box(x,y,186,h)
        text(cx,y+20,heading,14,True)
        for i,line in enumerate(col[key]):
            yy=y+40+i*18
            # Hardware has only 64 units; compact its two labels to 16-unit lines.
            if key=='device': yy=y+38+i*16
            text(cx,yy,line,14)
    for y1,y2 in [(178,200),(278,300),(398,420)]:arrow(cx,y1,y2)
    arrow(cx,490,511,qualification=True)
box(12,513,586,90,fill='#FFFFFF',stroke=RED,stroke_width=2)
text(305,535,'Qualification gate: the complete model-serving configuration',15,True)
text(305,556,'Weights + KV + workspace | operators + attention/cache path',14)
text(305,576,'Correctness + isolation | collectives (if used) | measured SLO',14)
text(305,593,'A visible device or a loaded model does not pass this gate.',14,True)
text(305,622,'Conceptual dependency map. No cross-device API or feature equivalence implied.',14)

# Exact arrow/text bounding-box separation; all connectors are vertical.
for x,y1,y2 in arrows:
    for label in labels:
        a,b,c,d=label['bbox_units']
        assert not (a<x<c and max(y1,b)<min(y2,d)), ('connector crosses text',label)
# Check every label contained in a card stays off its border.
for label in labels:
    a,b,c,d=label['bbox_units'];cx=(a+c)/2;cy=(b+d)/2
    owners=[r for r in rectangles if r[0]<=cx<=r[2] and r[1]<=cy<=r[3]]
    if owners:
        r=min(owners,key=lambda r:(r[2]-r[0])*(r[3]-r[1]))
        assert a>r[0]+3 and c<r[2]-3 and b>r[1]+1 and d<r[3]-1,('card overflow',label,r)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH_IN}in" height="{H/W*WIDTH_IN}in" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="white"/>'+''.join(elements)+'</svg>'
svg_path=ROOT/'intel-backend-paths.svg';svg_path.write_text(svg)
doc=fitz.open(stream=svg.encode(),filetype='svg')
pdf=fitz.open('pdf',doc.convert_to_pdf())
pdf.save(ROOT/'intel-backend-paths.pdf')
pix=pdf[0].get_pixmap(dpi=DPI,alpha=False);pix.save(ROOT/'intel-backend-paths.png')
image=Image.open(ROOT/'intel-backend-paths.png');image.save(ROOT/'intel-backend-paths.png',dpi=(DPI,DPI))
ImageOps.grayscale(image).save(ROOT/'intel-backend-paths-gray.png',dpi=(DPI,DPI))
# A detail crop from the actual rendered pixels, never from SVG text.
image.crop((0,int(image.height*.28),int(image.width*.68),int(image.height*.80))).save(ROOT/'intel-backend-paths-detail.png',dpi=(DPI,DPI))
# Actual-size placement on US Letter; no manuscript rebuild or source edits.
proof=fitz.open();page=proof.new_page(width=612,height=792)
rect=fitz.Rect(1.2*72,1.0*72,(8.5-1.2)*72,1.0*72+pdf[0].rect.height)
page.show_pdf_page(rect,pdf,0)
page.insert_text((86.4,rect.y1+18),'IX-F1 placement proof: 6.1-inch figure in the US Letter text block.',fontsize=10)
page.insert_text((86.4,rect.y1+33),'Conceptual dependency map; not a benchmark or full-manuscript proof.',fontsize=10)
proof.save(ROOT/'letter-placement-proof.pdf')
page.get_pixmap(dpi=150,alpha=False).save(ROOT/'letter-placement-proof.png')
minimum=min(x['placed_font_pt'] for x in labels)
assert image.width==1830 and image.height==1890,(image.size,WIDTH_IN)
assert minimum>=10
# Pixel-content check: not blank; no ink on the canvas perimeter.
gray=ImageOps.grayscale(image)
bbox=ImageOps.invert(gray).point(lambda x:255 if x>40 else 0).getbbox()
assert bbox and bbox[0]>0 and bbox[1]>0 and bbox[2]<image.width and bbox[3]<image.height,bbox
# Text gray/white contrast; colors are reserved for borders, never identity alone.
linear=lambda c:c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
rgb=tuple(int(INK[i:i+2],16)/255 for i in [1,3,5])
contrast=1.05/(sum(a*linear(b) for a,b in zip([.2126,.7152,.0722],rgb))+.05)
qa={'render':'PASS','intended_width_in':WIDTH_IN,'intended_height_in':H/W*WIDTH_IN,'png_pixels':list(image.size),'dpi':DPI,'minimum_placed_font_pt':minimum,'label_count':len(labels),'downward_arrow_count':len(arrows),'ink_bbox_pixels':bbox,'connector_text_intersections':0,'text_gray_white_contrast_ratio':contrast,'labels':labels,'arrows':arrows,'notes':['Geometry checks are not a replacement for rendered visual inspection.','Color-independent labels and separate columns preserve meaning in grayscale.']}
(ROOT/'geometry-QA.json').write_text(json.dumps(qa,indent=2)+'\n')
caption='IX-F1. Three accelerator paths and one qualification gate. A serving engine depends on compatible backend integration, kernels, runtime, driver and hardware. Intel GPU, Gaudi and client NPU are distinct paths. The GPU column includes both PyTorch XPU and engine-native SYCL alternatives. Solid arrows mean dependencies; dashed arrows bring the complete path to qualification. Neither means benchmark timing. Device enumeration alone does not validate model correctness, memory residency, collectives or an SLO.'
assets=['intel-backend-paths.svg','intel-backend-paths.pdf','intel-backend-paths.png','intel-backend-paths-gray.png','letter-placement-proof.pdf']
manifest={'schema_version':1,'figures':[{'id':'IX-F1','editable_source':'figures/intel-backend-paths.svg','generator':'figures/generate.py','rendered_png':'figures/intel-backend-paths.png','vector_pdf':'figures/intel-backend-paths.pdf','grayscale_png':'figures/intel-backend-paths-gray.png','placement_proof':'figures/letter-placement-proof.pdf','reproduction_command':'python research/intel-xpu-20261028/figures/generate.py','dependencies':['PyMuPDF','Pillow'],'intended_width_in':WIDTH_IN,'intended_height_in':H/W*WIDTH_IN,'ppi':DPI,'caption':caption,'alt_text':'Three separate columns descend from serving engine to backend entry, kernels and runtime, and hardware. The Intel GPU column offers torch.xpu or engine-native SYCL. Gaudi uses hpu and its own stack. Client NPU uses the OpenVINO NPU plugin. All columns lead to a gate requiring a complete model-serving configuration, including memory, operators, correctness, isolation, collectives when used and a measured SLO.','related_prose_anchors':['IX-T1','IX-T3'],'claim_ids':['IX-001','IX-002','IX-003','IX-018','IX-019','IX-023','IX-026','IX-027'],'evidence_source_ids':[25,35,47,49,53,54,55,66,67],'data_classification':'Original conceptual diagram; no measured performance data','sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in assets}}]}
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:v for k,v in qa.items() if k not in ['labels','arrows']},indent=2))
