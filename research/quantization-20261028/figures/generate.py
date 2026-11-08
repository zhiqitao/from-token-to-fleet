#!/usr/bin/env python3
"""Original figures. Shared vector/raster drawing records, no vendor artwork.
Run from repo root: python3 research/quantization-20261028/figures/generate.py
Requires Python and Pillow; fontconfig resolves the book's Liberation Sans.
"""
from decimal import Decimal
from pathlib import Path
import hashlib
import html
import json
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WIDTH_IN = Decimal('8.5') - Decimal('1.2') - Decimal('1.2')
W = float(WIDTH_IN * 72)
DPI = 600
S = DPI / 72
FONT = subprocess.check_output(['fc-match','-f','%{file}','Liberation Sans'], text=True).strip()
BOLD = subprocess.check_output(['fc-match','-f','%{file}','Liberation Sans:style=Bold'], text=True).strip()
assert WIDTH_IN == Decimal('6.1')
assert 32 * 4 // 8 + 1 == 17
assert 32 * 4 // 8 + 2 == 18
assert Decimal(17)/32 == Decimal('0.53125')
assert Decimal(18)/32 == Decimal('0.5625')

class Canvas:
    def __init__(self, name, height, desc):
        self.name, self.height = name, height
        self.image = Image.new('RGB',(round(W*S),round(height*S)),'white')
        self.draw = ImageDraw.Draw(self.image)
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH_IN}in" height="{height/72:.8f}in" viewBox="0 0 {W} {height}" role="img"><title>{html.escape(name)}</title><desc>{html.escape(desc)}</desc><rect width="100%" height="100%" fill="white"/>']
        self.texts = []
    def rect(self,x,y,w,h,fill='#f2f2f2',stroke='#444444',lw=.8):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{lw}"/>')
        self.draw.rectangle((x*S,y*S,(x+w)*S,(y+h)*S),fill=fill,outline=stroke,width=max(1,round(lw*S)))
    def line(self,x1,y1,x2,y2,lw=1):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#444444" stroke-width="{lw}"/>')
        self.draw.line((x1*S,y1*S,x2*S,y2*S),fill='#444444',width=round(lw*S))
    def arrow(self,x1,y1,x2,y2):
        self.line(x1,y1,x2,y2)
        angle=math.atan2(y2-y1,x2-x1)
        pts=[(x2,y2),(x2-5*math.cos(angle-.45),y2-5*math.sin(angle-.45)),(x2-5*math.cos(angle+.45),y2-5*math.sin(angle+.45))]
        self.parts.append('<polygon points="'+ ' '.join(f'{x},{y}' for x,y in pts)+'" fill="#444444"/>')
        self.draw.polygon([(x*S,y*S) for x,y in pts], fill='#444444')
    def text(self,x,y,t,fs=9,bold=False,center=False):
        font=ImageFont.truetype(BOLD if bold else FONT,round(fs*S))
        length=self.draw.textlength(t,font=font)/S
        left=x-length/2 if center else x
        bbox=self.draw.textbbox((left*S,y*S),t,font=font,anchor='ls')
        b=[a/S for a in bbox]
        assert min(b[0],b[1])>=2 and b[2]<=W-2 and b[3]<=self.height-2,(t,b)
        self.draw.text((left*S,y*S),t,font=font,fill='#222222',anchor='ls')
        # Explicit textLength makes SVG advances agree with the inspected raster.
        self.parts.append(f'<text x="{left}" y="{y}" fill="#222222" font-family="Liberation Sans" font-size="{fs}" font-weight="{700 if bold else 400}" textLength="{length}" lengthAdjust="spacingAndGlyphs">{html.escape(t)}</text>')
        self.texts.append({'text':t,'font_pt':fs,'bbox_pt':b})
    def save(self):
        self.parts.append('</svg>')
        svg=HERE/f'{self.name}.svg'
        svg.write_text('\n'.join(self.parts)+'\n')
        png=HERE/f'{self.name}.png'
        self.image.save(png,dpi=(DPI,DPI))
        gray=self.image.convert('L')
        gray.save(HERE/f'{self.name}-grayscale.png',dpi=(DPI,DPI))
        # 150dpi proof canvas: US Letter with true 1.2-inch side margins.
        page=Image.new('RGB',(1275,1650),'white')
        p= self.image.resize((915,round(self.height/72*150)),Image.Resampling.LANCZOS)
        page.paste(p,(180,150))
        page.save(HERE/f'{self.name}-letter-proof.png',dpi=(150,150))
        self.image.resize((1220,round(self.image.height*1220/self.image.width)),Image.Resampling.LANCZOS).save(HERE/f'{self.name}-whole.png')
        overlaps=[]
        for i,a in enumerate(self.texts):
            for b in self.texts[i+1:]:
                ax,ay,ar,ab=a['bbox_pt']; bx,by,br,bb=b['bbox_pt']
                if min(ar,br)>max(ax,bx)+.1 and min(ab,bb)>max(ay,by)+.1:
                    overlaps.append([a['text'],b['text']])
        assert not overlaps,overlaps
        return {'id':self.name,'width_in':float(WIDTH_IN),'height_in':self.height/72,'png_pixels':self.image.size,'dpi':DPI,'minimum_font_pt':min(t['font_pt'] for t in self.texts),'text_count':len(self.texts),'text_overlap_count':len(overlaps),'text_bounds_checked':True,'grayscale_native':True,'svg_sha256':hashlib.sha256(svg.read_bytes()).hexdigest(),'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'text_records':self.texts}

c=Canvas('qf1-quantization-layers',420,'Methods, representations, packed tensors, checkpoint container, runtime layout and compatible execution implementations. Unsupported combinations must be rejected; fallback is not guaranteed.')
c.text(W/2,19,'Quantization choices are not execution guarantees',12,True,True)
for x,title,line1,line2 in [(14,'Error-control method','AWQ / GPTQ','Calibration guides error reduction'),(226,'Numerical representation','INT4 + scheme / MXFP4 / NVFP4','Scale type and grouping are explicit')]:
    c.rect(x,36,199,66)
    c.text(x+99.5,53,title,10,True,True)
    c.text(x+99.5,73,line1,10,False,True)
    c.text(x+99.5,91,line2,9,False,True)
c.rect(14,122,411,84,'#fafafa')
c.rect(32,140,375,35,'#e7e7e7')
c.text(W/2,154,'Packed tensor: values + scales (+ zero points, if used)',9,True,True)
c.text(W/2,168,'Layout, padding and alignment are implementation-specific',9,False,True)
c.text(W/2,193,'Container wraps tensors + metadata: e.g., GGUF / safetensors',9,False,True)
c.arrow(113.5,102,113.5,140)
c.arrow(325.5,102,325.5,140)
c.arrow(W/2,206,W/2,232)
c.text(W/2+8,222,'load / repack',9)
c.rect(62,232,315,34)
c.text(W/2,246,'Runtime tensors in the kernel-required layout',10,True,True)
c.text(W/2,260,'Repacking does not imply numerical conversion.',9,False,True)
c.line(W/2,266,W/2,294)
c.text(W/2+8,284,'compatible dispatch',9)
c.line(77.5,294,361.5,294)
for x,title,a,b in [(14,'Native FP4 math','Compatible low-bit','operand arithmetic'),(156,'Fused dequant','Weight dequantization','e.g., W4A16 GEMM'),(298,'Reconstruct','Higher-precision','weights + GEMM')]:
    cx=x+63.5
    c.arrow(cx,294,cx,315)
    c.rect(x,315,127,57)
    c.text(cx,331,title,10,True,True)
    c.text(cx,348,a,9,False,True)
    c.text(cx,363,b,9,False,True)
c.text(W/2,390,'Only supported combinations can load and execute.',9,False,True)
c.text(W/2,407,'No compatible kernel: reject; fallback is not guaranteed.',9,False,True)
a=c.save()
c.image.crop((round(8*S),round(228*S),round(431*S),round(412*S))).resize((1269,552)).save(HERE/'qf1-detail.png')

c=Canvas('qf2-block-scale-bytes',312,'Same 32 E2M1 values use sixteen payload bytes. MXFP4 adds one block scale byte. Common one-dimensional NVFP4 adds two local scale bytes and a separate four-byte scale shared over the tensor. Byte accounting, not a physical packing order.')
c.text(W/2,19,'Four-bit values, different scale bills',12,True,True)
c.text(W/2,38,'Payload and local-scale bar widths are proportional to bytes.',9,False,True)
# 18 points per byte: payload16B=288pt, scale1B=18pt.
x=24; unit=18
c.text(24,62,'MXFP4: one E8M0 scale per 32 values',10,True)
c.rect(x,73,16*unit,26,'#dddddd')
c.rect(x+16*unit,73,unit,26,'#777777')
c.text(x+8*unit,90,'32 E2M1 values = 16 B',10,False,True)
c.text(x+16*unit+unit/2,112,'1 B scale',9,False,True)
c.line(x+16*unit+unit/2,99,x+16*unit+unit/2,103)
c.text(24,132,'Local: 17 B / 32 = 0.53125 B/value = 4.25 bit/value',10,True)

c.text(24,157,'NVFP4 (common 1D): one E4M3 scale per 16 values',10,True)
c.rect(x,169,16*unit,26,'#dddddd')
c.line(x+8*unit,169,x+8*unit,195)
c.rect(x+16*unit,169,unit,26,'#777777')
c.rect(x+17*unit,169,unit,26,'#777777')
c.text(x+4*unit,186,'16 values = 8 B',10,False,True)
c.text(x+12*unit,186,'16 values = 8 B',10,False,True)
c.line(x+16*unit,195,x+16*unit,199)
c.line(x+18*unit,195,x+18*unit,199)
c.line(x+16*unit,199,x+18*unit,199)
c.text(x+17*unit,212,'2 B scales',9,False,True)
c.text(24,228,'Local: 18 B / 32 = 0.5625 B/value = 4.5 bit/value',10,True)
c.text(W/2,252,'NVFP4 global FP32 scale: 4 B per tensor, not per block.',9,True,True)
c.text(W/2,279,'Byte accounting only; not a physical packing order.',9,False,True)
c.text(W/2,300,'No padding, extra copies, headers or high-precision exceptions.',9,False,True)
b=c.save()
c.image.crop((round(16*S),round(145*S),round(421*S),round(265*S))).resize((1620,480)).save(HERE/'qf2-detail.png')

# White-background black/grey text contrast is independent of colored semantics.
def luminance(v):
    t=v/255
    return t/12.92 if t<=.04045 else ((t+.055)/1.055)**2.4
contrast=(luminance(221)+.05)/(luminance(34)+.05)
assert contrast>10
checks={'text_width_derivation_in':'8.5 - 1.2 - 1.2 = 6.1','font_path':FONT,'bold_font_path':BOLD,'text_vs_darkest_text_background_contrast':contrast,'figures':[a,b],'scope':'Bounds/overlap/contrast checks are not a substitute for visual inspection.'}
(HERE/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
manifest={'scope':'Unapplied quantization research. No publication readiness claim.','page_format':'US Letter 8.5 x 11 in','text_width_in':6.1,'geometry_sources':['render/latex/book.tex:7','render/latex/book.sty:61'],'reproduction_command':'python3 research/quantization-20261028/figures/generate.py','dependencies':['Python 3','Pillow','fontconfig','Liberation Sans'],'figures':[]}
for ident,title,caption,alt,anchors,claims in [
 ('qf1-quantization-layers','Quantization choices and execution paths','A quantization method, a numerical representation, packed tensors and a checkpoint container describe different parts of a deployment. The loader prepares a kernel-required runtime layout; compatible dispatch selects native FP4 math, fused dequantization or reconstruction. No compatible kernel means rejection; fallback is not guaranteed. Shown combinations do not assert universal interoperability.','Two distinct choices, error-control method and numerical representation, feed packed tensors enclosed by a checkpoint container. Loading and repacking prepare a runtime layout. Compatible dispatch branches to native FP4 math, fused weight dequantization such as W4A16, or higher-precision reconstruction. Unsupported combinations are rejected.',['q-layers','q-kernel-gates'],['Q01','Q02','Q03','Q05','Q06','Q09','Q12','Q19','Q20','Q21','Q28','Q32']),
 ('qf2-block-scale-bytes','Four-bit payloads and shared scale storage','Compact storage for the same 32 E2M1 values. OCP 1.0 MXFP4 uses one E8M0 scale byte; common 1D NVFP4 uses two E4M3 scale bytes plus a separate FP32 global scale per tensor. Bars are proportional only for payload and local scales. This is derived storage accounting, not a speed or accuracy comparison.','The MXFP4 row has sixteen payload bytes and one local scale byte, totalling seventeen bytes for thirty-two values. The one-dimensional NVFP4 row has sixteen payload bytes and two local scale bytes, totalling eighteen bytes, plus a four-byte global scale shared across the tensor.',['q-block-bytes','q-worked-example'],['Q09','Q10','Q12','Q13','Q14','Q15','Q31'])]:
    manifest['figures'].append({'id':ident,'title':title,'source':f'figures/{ident}.svg','generator':'figures/generate.py','png':f'figures/{ident}.png','grayscale_png':f'figures/{ident}-grayscale.png','letter_size_proof':f'figures/{ident}-letter-proof.png','whole_inspection':f'figures/{ident}-whole.png','detail_inspection':'figures/qf1-detail.png' if ident.startswith('qf1') else 'figures/qf2-detail.png','intended_width_in':6.1,'dpi':600,'caption':caption,'alt_text':alt,'related_prose_anchors':anchors,'claim_ids':claims,'evidence_index':'claims.json','reproduction_command':manifest['reproduction_command'],'numerical_basis':'OCP 1.0 and NVIDIA common 1D NVFP4; exact byte arithmetic asserted in generator and independent_calculations.py; no benchmark data','integration_status':'unapplied; numbering and integrated-page checks remain with parent'})
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'text_width_in':str(WIDTH_IN),'figures':[{'id':i['id'],'pixels':i['png_pixels'],'min_font_pt':i['minimum_font_pt'],'text_overlaps':i['text_overlap_count']} for i in [a,b]],'contrast':contrast},indent=2))
