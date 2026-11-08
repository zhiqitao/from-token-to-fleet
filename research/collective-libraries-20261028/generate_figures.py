"""Original print-width collective figures. Only writes beside this script.
Run from anywhere: python3 <this file>
Dependencies already available in this task: PyMuPDF, Pillow (no network access).
SVG uses PostScript-point coordinates; width is the book's 6.1-inch text block.
"""
from pathlib import Path
from html import escape
import hashlib
import json
import math
import platform
import pymupdf
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)
W = 439.2
INK = "#20252B"
BLUE = "#27408B"
ORANGE = "#E67E22"
RED = "#C0392B"
GRAY = "#59616A"


class Drawing:
    def __init__(self, height):
        self.h = height
        self.parts = []
        self.texts = []
        self.lines = []

    def rect(self, x, y, w, h, fill="#FFFFFF", stroke=INK, dash=False):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="0.9"'+(' stroke-dasharray="4 3"' if dash else '')+'/>')

    def text(self, x, y, value, size=10, color=INK, bold=False, anchor="start"):
        width = pymupdf.get_text_length(value, fontname="hebo" if bold else "helv", fontsize=size)
        left = x if anchor == "start" else x - width / 2 if anchor == "middle" else x - width
        # Conservative font extent, including descenders. SVG baseline is y.
        self.texts.append({"text": value, "bbox": [left, y-size*1.08, left+width, y+size*.25], "pt": size})
        self.parts.append(f'<text x="{x}" y="{y}" font-family="Helvetica,Arial,sans-serif" font-size="{size}" font-weight="'+('bold' if bold else 'normal')+f'" text-anchor="{anchor}" fill="{color}">{escape(value)}</text>')

    def line(self, x1, y1, x2, y2, color=INK, dash=False, arrow=True):
        self.lines.append((x1, y1, x2, y2))
        distance = math.hypot(x2-x1, y2-y1)
        if dash and distance:
            # Explicit subsegments survive SVG converters that ignore dasharray.
            for offset in range(0, math.ceil(distance), 10):
                a, b = offset/distance, min(offset+6, distance)/distance
                self.parts.append(f'<line x1="{x1+a*(x2-x1)}" y1="{y1+a*(y2-y1)}" x2="{x1+b*(x2-x1)}" y2="{y1+b*(y2-y1)}" stroke="{color}" stroke-width="1.15"/>')
        else:
            self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.15"/>')
        if arrow:
            angle = math.atan2(y2-y1, x2-x1)
            coords = [(x2, y2)] + [(x2-5*math.cos(angle)+s*2.3*math.sin(angle), y2-5*math.sin(angle)-s*2.3*math.cos(angle)) for s in [-1, 1]]
            self.parts.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in coords)+f'" fill="{color}"/>')

    def save(self, stem):
        failures = []
        for item in self.texts:
            x0,y0,x1,y1=item['bbox']
            if x0 < 3 or x1 > W-3 or y0 < 2 or y1 > self.h-2:
                failures.append({'outside_canvas':item})
        for i,a in enumerate(self.texts):
            for b in self.texts[i+1:]:
                x0,y0,x1,y1=a['bbox']; u0,v0,u1,v1=b['bbox']
                if min(x1,u1)-max(x0,u0)>0.5 and min(y1,v1)-max(y0,v0)>0.5:
                    failures.append({'text_overlap':[a['text'],b['text']]})
        # Exact slab intersection, shrinking text bounds slightly to ignore glyph side bearings.
        for segment in self.lines:
            x,y,xe,ye=segment; dx,dy=xe-x,ye-y
            for t in self.texts:
                a,b,c,d=t['bbox']; a+=.4; b+=.4; c-=.4; d-=.4
                lo,hi=0.,1.
                hit=True
                for p,q,l,r in [(x,dx,a,c),(y,dy,b,d)]:
                    if abs(q)<1e-10:
                        if not l<p<r: hit=False; break
                    else:
                        s0,s1=sorted(((l-p)/q,(r-p)/q)); lo=max(lo,s0); hi=min(hi,s1)
                        if lo>=hi: hit=False; break
                if hit:
                    failures.append({'line_crosses_text':t['text'],'segment':segment})
        if failures:
            raise AssertionError(json.dumps(failures,indent=2))
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="6.1in" height="{self.h/72:.8f}in" viewBox="0 0 {W} {self.h}"><rect width="{W}" height="{self.h}" fill="white"/>'+''.join(self.parts)+'</svg>'
        (OUT/f'{stem}.svg').write_text(svg)
        doc=pymupdf.open(stream=svg.encode(),filetype='svg')
        pdf=pymupdf.open(stream=doc.convert_to_pdf(),filetype='pdf')
        pdf.save(OUT/f'{stem}.pdf')
        pdf[0].get_pixmap(dpi=300).save(OUT/f'{stem}.png')
        im=Image.open(OUT/f'{stem}.png').convert('RGB')
        ImageOps.grayscale(im).save(OUT/f'{stem}-gray.png',dpi=(300,300))
        im.resize((round(6.1*96),round(self.h/72*96))).save(OUT/f'{stem}-actual96.png',dpi=(96,96))
        return {'id':stem,'svg':f'figures/{stem}.svg','png':f'figures/{stem}.png',
                'pdf':f'figures/{stem}.pdf','grayscale_png':f'figures/{stem}-gray.png',
                'actual_size_preview':f'figures/{stem}-actual96.png','width_in':6.1,
                'height_in':self.h/72,'dpi':300,'raster_pixels':list(im.size),
                'minimum_label_pt':min(t['pt'] for t in self.texts),
                'text_count':len(self.texts),'arrow_segment_count':len(self.lines),
                'geometry_failures':failures,'png_sha256':hashlib.sha256((OUT/f'{stem}.png').read_bytes()).hexdigest()}


def reduction():
    d=Drawing(434)
    d.text(14,20,'SUM first; replication second',13,bold=True)
    d.text(14,38,'Four ranks; four FP16 elements per input (8 B/rank).',10)
    xs=[15,120,225,330]; bw=94
    inputs=['[1, 2, -1, 0]','[2, 4, -2, 0]','[3, 6, -3, 0]','[4, 8, -4, 0]']
    for i,x in enumerate(xs):
        d.text(x+bw/2,58,f'Rank {i}',10,bold=True,anchor='middle')
        d.rect(x,65,bw,30,fill='#F0F3FA',stroke=BLUE)
        d.text(x+bw/2,84,inputs[i],10,anchor='middle')
    d.line(W/2,103,W/2,133)
    d.text(14,115,'Reduce-scatter',10.5,bold=True,color=BLUE)
    d.text(243,115,'3 neighbor rounds',10)
    d.text(243,130,'6 B sent + 6 B received/rank',9.5)
    vals=['[10]','[20]','[-10]','[0]']
    for x,val in zip(xs,vals):
        d.rect(x,143,bw,30,fill='#FFF4E8',stroke=ORANGE)
        d.text(x+bw/2,162,val,11,bold=True,anchor='middle')
    d.text(W/2,189,'Phase boundary: one reduced element per rank',10,anchor='middle')
    d.line(W/2,200,W/2,228)
    d.text(14,212,'All-gather',10.5,bold=True,color=BLUE)
    d.text(243,212,'3 neighbor rounds',10)
    d.text(243,227,'6 B sent + 6 B received/rank',9.5)
    for x in xs:
        d.rect(x,240,bw,31,fill='#F0F3FA',stroke=BLUE)
        d.text(x+bw/2,260,'[10, 20, -10, 0]',10,anchor='middle')
    d.text(W/2,288,'Every rank holds SUM, not the average.',10.5,bold=True,anchor='middle')
    d.text(14,310,'Balanced ring neighbor order (both phases)',10,bold=True)
    centers=[61,166,271,376]
    for i,c in enumerate(centers):
        d.rect(c-22,323,44,23)
        d.text(c,339,f'R{i}',10,anchor='middle')
        if i<3: d.line(c+26,334,centers[i+1]-26,334)
    d.line(376,351,376,364,arrow=False)
    d.line(376,364,61,364,arrow=False)
    d.line(61,364,61,351)
    d.text(W/2,383,'Each round sends one 2 B chunk to the next rank.',10,anchor='middle')
    d.rect(14,394,411,29,fill='#FFF6F4',stroke=RED)
    d.text(W/2,413,'Per rank: 12 B sent + 12 B received = 24 B endpoint total',10,bold=True,anchor='middle')
    row=d.save('CCL-F1-reduction')
    row.update({'caption':'A balanced ring computes SUM by reduce-scatter, then replicates the reduced shards by all-gather. Scope: illustrative four-rank FP16 inputs; phase-boundary states, not a complete timing trace. The small integer values and their sums are exactly representable. Each phase sends and receives 6 B per rank; both phases send 12 B and receive 12 B. No averaging or hardware offload is implied. [ILLUSTRATIVE][DERIVED] [ANALYTICAL]',
                'alt_text':'Four ranks start with vectors [1,2,-1,0], [2,4,-2,0], [3,6,-3,0], [4,8,-4,0]. Reduce-scatter leaves 10,20,-10,0 at ranks zero through three. All-gather gives [10,20,-10,0] to every rank. Directed ring order is zero to one to two to three to zero. Each rank sends twelve bytes and receives twelve bytes across both phases.',
                'related_prose_anchors':['CCL-T1','CCL-T3'],'claim_ids':['CCL-001','CCL-002','CCL-006','CCL-007'],
                'evidence_ids':['mpi50-pdf','nccl-performance'],'placement':'Chapter 9 section 1, after candidate semantics table'})
    return row


def layers():
    d=Drawing(502)
    d.text(14,20,'The payload path is not the bootstrap path',12.5,bold=True)
    d.line(15,35,39,35,arrow=True)
    d.text(46,39,'Payload / device execution',9.5)
    d.line(250,35,275,35,color=RED,dash=True,arrow=True)
    d.text(281,39,'Control / setup',9.5)
    d.rect(16,54,407,45,fill='#FFF6F4',stroke=RED,dash=True)
    d.text(W/2,72,'Launcher, rank/device mapping, rendezvous',10.5,bold=True,anchor='middle')
    d.text(W/2,89,'MPI or a store can distribute communicator IDs.',10,anchor='middle')
    d.line(16,77,8,77,color=RED,dash=True,arrow=False)
    d.line(8,77,8,227,color=RED,dash=True,arrow=False)
    d.line(8,227,16,227,color=RED,dash=True)
    d.line(423,77,431,77,color=RED,dash=True,arrow=False)
    d.line(431,77,431,227,color=RED,dash=True,arrow=False)
    d.line(431,227,423,227,color=RED,dash=True)
    d.text(19,119,'1  Framework backend',10.5,bold=True)
    for x,label in [(16,'ProcessGroupNCCL'),(229,'ProcessGroupXCCL')]:
        d.rect(x,129,194,33,fill='#F0F3FA',stroke=BLUE)
        d.text(x+97,150,label,10.5,bold=True,anchor='middle')
    for c in [113,326]: d.line(c,168,c,186)
    d.text(19,204,'2  Collective library and algorithm',10.5,bold=True)
    for x,label,desc in [(16,'NCCL','Ring / tree / eligible offload'),(229,'oneCCL','Selected collective algorithm')]:
        d.rect(x,214,194,43,fill='#FFF4E8',stroke=ORANGE)
        d.text(x+97,231,label,11,bold=True,anchor='middle')
        d.text(x+97,248,desc,9.5,anchor='middle')
    for c in [113,326]: d.line(c,263,c,281)
    d.text(19,299,'3  Device runtime plus transport',10.5,bold=True)
    for x,rows in [(16,['CUDA device execution','GPU P2P / shared memory','Network: RDMA or sockets']),
                   (229,['SYCL / Level Zero path','Legacy plugin: MPI or OFI','Actual path depends on build'])]:
        d.rect(x,309,194,57,fill='#F7F7F7')
        for i,s in enumerate(rows): d.text(x+97,326+i*16,s,9.5,anchor='middle')
    for c in [113,326]: d.line(c,372,c,390)
    d.text(19,408,'4  Physical resources and topology',10.5,bold=True)
    for x,rows in [(16,['GPU HBM / NVLink / PCIe','NIC / switches / fabric']),
                   (229,['XPU HBM / device links / PCIe','NIC / switches / fabric'])]:
        d.rect(x,418,194,39,fill='#F0F3FA',stroke=BLUE)
        for i,s in enumerate(rows): d.text(x+97,434+i*15,s,9.5,anchor='middle')
    d.text(14,478,'GPU-aware MPI can carry payload too; MPI is not CPU-only.',10,bold=True)
    d.text(14,494,'Named paths: 2026-10-28 snapshot, not a drop-in compatibility claim.',9.5)
    row=d.save('CCL-F2-layers')
    row.update({'caption':'Collective semantics reach hardware through a framework backend, a collective implementation, and runtime/transport paths. Dashed setup paths can use MPI to distribute NCCL communicator IDs without carrying the collective payload. GPU-aware MPI is also a payload alternative, and legacy oneCCL can use MPI transport. Scope: conceptual paths with dated implementation examples; not a universal call graph or compatibility matrix. [1P][FACT] (named paths); [ILLUSTRATIVE] (composition)',
                'alt_text':'Two solid downward paths connect ProcessGroupNCCL to NCCL, CUDA and GPU or network transport, then GPU and network hardware; and ProcessGroupXCCL to oneCCL, a SYCL Level Zero path and legacy MPI or OFI transport, then XPU and network hardware. Separate dashed setup arrows enter library initialization from launcher and rendezvous. A note states that GPU-aware MPI can also carry payload.',
                'related_prose_anchors':['CCL-T2'],'claim_ids':['CCL-009','CCL-010','CCL-011','CCL-012','CCL-014','CCL-019','CCL-020','CCL-022','CCL-023'],
                'evidence_ids':['nccl-example-mpi','nccl-init','nccl-api-header','oneccl-header','oneccl-legacy-plugin','oneccl-atl-mpi','oneccl-atl-ofi','torch-v29-doc','torch-xccl-code'],
                'placement':'Chapter 9 section 2, after first paragraph of CCL-T2'})
    return row


if __name__=='__main__':
    rows=[reduction(),layers()]
    manifest={'status':'Rendered; visual inspection recorded separately in QA.md',
              'book_format':'US Letter 8.5 x 11 in','text_width_in':6.1,
              'style_basis':'render/latex/book.sty:55-62,104-112; design/book-architecture.md',
              'reproduction_command':'python3 research/collective-libraries-20261028/generate_figures.py',
              'dependencies':{'python':platform.python_version(),'PyMuPDF':pymupdf.VersionBind,'Pillow':Image.__version__},
              'figures':rows}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for row in rows:
        print(json.dumps({k:row[k] for k in ['id','raster_pixels','width_in','height_in','minimum_label_pt','geometry_failures']}))
    # Raster detail files are inspection artifacts, not publication substitutes.
    Image.open(OUT/'CCL-F1-reduction.png').crop((0,0,1830,1250)).save(OUT/'CCL-F1-detail.png')
    Image.open(OUT/'CCL-F2-layers.png').crop((0,190,1830,1085)).save(OUT/'CCL-F2-detail.png')
