"""Reproduce original conceptual SVG/PDF/400-PPI figures, without model inference.
Run from any directory: python3 /absolute/path/to/figures/generate_figures.py
Requires Python 3, Pillow, PyMuPDF and Inkscape. Writes only beside this script.
"""
import html, json, pathlib, subprocess, xml.etree.ElementTree as ET
from PIL import Image, ImageFont
import fitz
R = pathlib.Path(__file__).resolve().parent
D = json.loads((R/'figure-data.json').read_text())
S = D['style']; P = D['page']; WIDTH = round((P['paper_width_in']-P['left_margin_in']-P['right_margin_in'])*100)
FONT = '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'
if not pathlib.Path(FONT).exists():
    FONT = subprocess.check_output(['fc-match','-f','%{file}', 'Liberation Sans'], text=True).strip()
checks = {}; text_boxes = []
def text(x,y,value,size=14,bold=False,anchor='start',color=None):
    font=ImageFont.truetype(FONT,size*10)
    width=font.getlength(value)/10
    left=x-(width/2 if anchor=='middle' else width if anchor=='end' else 0)
    text_boxes.append({'text':value,'bbox':[left,y-size,left+width,y+4],'size_pt':size*.72})
    label=html.escape(value).replace('pθ','p<tspan baseline-shift="sub" font-size="80%">θ</tspan>')
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color or S["ink"]}">{label}</text>'
def rect(x,y,w,h,fill='#FFFFFF',stroke=None,dash=False):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" stroke="{stroke or S["ink"]}" stroke-width="1.3"'+(' stroke-dasharray="5 3"' if dash else '')+'/>'
def arrow(x1,y1,x2,y2,reverse=False):
    col = S['compute'] if reverse else S['ink']
    return f'<path d="M {x1} {y1} L {x2} {y2}" stroke="{col}" stroke-width="2" fill="none" marker-end="url(#{"orange" if reverse else "black"})"/>'
def cells(x,y,values,w=27):
    out=''
    for i,v in enumerate(values):
        unknown=v in ('?','M'); fill='url(#hatch)' if unknown else S['state_fill']
        out+=rect(x+i*w,y,w-2,34,fill,S['memory'])
        out+=text(x+i*w+(w-2)/2,y+23,v,14,anchor='middle')
    return out

def start(key):
    global text_boxes
    text_boxes=[]; h=round(D[key]['height_in']*100)
    a=f'<svg xmlns="http://www.w3.org/2000/svg" width="6.1in" height="{D[key]["height_in"]}in" viewBox="0 0 {WIDTH} {h}" font-family="Liberation Sans">'
    a+='<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#FAFAFA"/><path d="M 0 6 L 6 0" stroke="#D0D0D0" stroke-width=".6"/></pattern>'
    for name,color in [('black',S['ink']),('orange',S['compute'])]:
        a+=f'<marker id="{name}" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M 0 0 L 6 3 L 0 6 Z" fill="{color}"/></marker>'
    a+='</defs>'+rect(0,0,WIDTH,h,'#FFFFFF','#FFFFFF')
    a+=text(18,27,D[key]['title'],18,True)
    return a,h

a,h=start('D1')
a+=text(18,52,'Forward q: add corruption. Reverse pθ: generate with learned updates.')
a+=text(18,85,'A  Continuous diffusion (schematic state values)',16,True)
for i,(x,label) in enumerate(zip([22,234,446],D['D1']['continuous_states'])):
    a+=rect(x,105,140,66,S['state_fill'],S['memory'])
    # Illustrated continuous values: no probabilities, benchmark curve or data claim.
    vals=[[.2,.35,.55,.72,.56,.4,.24,.14],[.42,.19,.68,.44,.73,.29,.57,.37],[.83,.12,.58,.24,.79,.34,.15,.65]][i]
    for j,v in enumerate(vals):
        xx=x+10+j*16; yy=163-v*48
        a+=f'<line x1="{xx}" x2="{xx}" y1="163" y2="{yy}" stroke="{S["memory"]}" stroke-width="5"/>'
    a+=text(x+70,193,label,14,anchor='middle')
for x1,x2 in [(170,226),(382,438)]:
    a+=arrow(x1,119,x2,119)+text((x1+x2)/2,109,'q',14,anchor='middle')
    a+=arrow(x2,154,x1,154,True)+text((x1+x2)/2,178,'pθ',14,anchor='middle')
a+=text(18,224,'B  Masked discrete diffusion (one categorical choice)',16,True)
for x,vals in zip([22,234,446],D['D1']['tokens']):
    a+=cells(x,251,vals,35)
for x1,x2 in [(170,226),(382,438)]:
    a+=arrow(x1,255,x2,255)+text((x1+x2)/2,245,'q',14,anchor='middle')
    a+=arrow(x2,284,x1,284,True)+text((x1+x2)/2,310,'pθ',14,anchor='middle')
a+=text(22,333,'M = MASK; text states are illustrative token IDs, not generated results.')
a+=text(18,370,'Training: construct corrupted inputs; learn reverse predictions.',15,True)
a+=text(18,395,'Sampling: start from the prior; apply learned reverse updates.',15,True)
a+=text(18,425,'Flow matching learns a vector field on a chosen probability path.')
a+=text(18,447,'Related paths do not make diffusion and flow matching identical.')
figs={'D1':(a+'</svg>',h,list(text_boxes))}
a,h=start('D2')
a+=text(18,52,'Snapshots show dependency order, not elapsed time or speedup.')
rows=[(83,105,'A  Autoregressive: append one token',D['D2']['ar'],'fixed','prefix'),(222,254,'B  Full-canvas masked sampler: accept selected IDs',D['D2']['masked'],'fixed','prompt'),(419,452,'C  Block-causal diffusion: refine, commit, advance',D['D2']['blocks'],'causal','prefix')]
def prefix_bracket(x,y,n):
    return f'<path d="M {x} {y-4} L {x} {y} L {x+28*n-6} {y} L {x+28*n-6} {y-4}" stroke="{S["memory"]}" stroke-width="2" fill="none"/>'
for ri,(title_y,y,title,states,l1,l2) in enumerate(rows):
    a+=text(18,title_y,title,16,True)
    a+=rect(20,y,110,40,S['state_fill'],S['memory'])
    a+=text(75,y+17,l1,14,anchor='middle')+text(75,y+35,l2,14,anchor='middle')
    a+=arrow(140,y+20,161,y+20)
    for col,(x,vals) in enumerate(zip([171,326,481],states)):
        for i,v in enumerate(vals):
            future=(ri==0 and v=='?') or (ri==2 and col==0 and i>=2)
            label='-' if future else v
            fill='#F2F2F2' if future else 'url(#hatch)' if v=='?' else S['state_fill']
            a+=rect(x+i*28,y+3,22,34,fill,S['memory'])
            a+=text(x+i*28+11,y+26,label,14,anchor='middle')
        if ri==0:
            a+=prefix_bracket(x,y+45,col+1)
        if ri==1 and col<2:
            a+=rect(x-4,y-2,114,44,'none',S['compute'],True)
        if ri==2 and col<2:
            bx=x+(0 if col==0 else 54)
            if col==1: bx=x+56
            a+=rect(bx-3,y-2,56,44,'none',S['compute'],True)
        if ri==2 and col>0:
            a+=prefix_bracket(x,y+45,2 if col==1 else 4)
        if col<2:
            a+=arrow(x+116,y+20,x+145,y+20)
    # A self-loop attaches to an unresolved INTERMEDIATE region, not final output.
    if ri in (1,2):
        lx,rx=(332,426) if ri==1 else (388,426)
        a+=f'<path d="M {rx} {y+42} L {rx} {y+61} L {lx} {y+61} L {lx} {y+42}" stroke="{S["compute"]}" stroke-width="1.5" fill="none" marker-end="url(#orange)"/>'
        a+=text(379,y+84,'repeat evaluations',14,anchor='middle')
a+=text(20,174,'Accepted IDs extend the prefix; K/V are cached when processed.')
a+=text(20,195,'Solid brackets mark finalized prefix state, not just accepted IDs.')
a+=text(20,361,'Full bidirectional forwards: fixed IDs can still acquire new K/V.')
a+=text(20,382,'Here, accepted IDs stay fixed; prompt-state reuse is not assumed.')
a+=text(20,558,'Refine the active block; finalize/cache its state before advancing.')
a+=text(20,579,'A valid block-causal boundary prevents later blocks changing it.')
a+=text(18,610,'Letters = accepted IDs; hatched ? = unresolved; - = inactive future.')
a+=text(18,632,'Dashed outline = recomputed output region; loops = repeated work.')
a+=text(18,654,'Editing and renoising samplers can differ from these examples.')
figs['D2']=(a+'</svg>',h,list(text_boxes))
manifest={'schema_version':1,'width_derivation':{'paper':'US Letter 8.5 x 11 in','build':'render/latex/book.tex:7','margins':'render/latex/book.sty:61','calculation':'8.5 - 1.2 - 1.2','available_text_width_in':WIDTH/100},'figures':[]}
captions={
'D1':'Corruption and learned reverse generation. Rightward q arrows specify forward corruption; leftward pθ arrows denote learned reverse updates. Continuous-valued noise and categorical MASK are different state spaces. Masked diffusion is one discrete construction, not a definition of every diffusion model. Values and tokens are conceptual illustrations, not measurements. Flow matching is related but is not the identical training objective. [1P][FACT] D01–D07; drawing [ILLUSTRATIVE].',
'D2':'Inference order, cache validity and output commitment. Autoregressive decoding extends a causal prefix; the displayed AR snapshots include processing of the newest accepted token before its K/V are shown as finalized. The illustrated full-canvas masked sampler accepts positions out of order but still recomputes bidirectional states. The block-causal design refines a mutable block before extending the immutable prefix. Loops denote repeated evaluations, not fixed counts or proportional time. Accepted token IDs do not by themselves establish reusable K/V. Approximate cache, editing and renoising implementations require their own policies. [1P][FACT] D08,D11–D15,D18,D24–D26; resource interpretation [DERIVED] D33–D34.'}
alts={
'D1':'Two lanes run left to right from clean data through partial corruption to a prior. Continuous values occupy the top lane and text tokens with MASK occupy the lower lane. Black forward arrows q point right. Separate orange learned reverse arrows p theta point left. Notes separate training corruption, reverse sampling and flow matching.',
'D2':'Three rows compare inference snapshots. AR grows A, then AB, then ABC; hyphens indicate inactive future positions. The masked canvas starts with hatched question marks, accepts A and C together, then ABCD; a dashed outline marks recomputed output representations, not editable IDs. The block-causal row refines an active two-position block and then advances. Solid brackets below cells identify finalized reusable prefix state. Repeat loops attach to unresolved intermediate regions, not final output. Fixed IDs alone do not guarantee invariant K/V; block-prefix reuse needs a causal boundary and finalization.'}
for key,(svg,h,bounds) in figs.items():
    svgpath=R/f'{key}.svg'; svgpath.write_text(svg+'\n')
    ET.fromstring(svg)
    subprocess.run(['inkscape',str(svgpath),'--export-type=png',f'--export-filename={R/key}.png','--export-dpi=400'],check=True,capture_output=True)
    subprocess.run(['inkscape',str(svgpath),'--export-type=pdf',f'--export-filename={R/key}.pdf'],check=True,capture_output=True)
    im=Image.open(R/f'{key}.png').convert('RGB')
    assert im.size==(round(WIDTH*4),round(h*4)),(key,im.size)
    gray=im.convert('L'); gray.save(R/f'{key}-gray.png',dpi=(400,400))
    gray_preview=gray.copy(); gray_preview.thumbnail((1220,1400)); gray_preview.save(R/f'{key}-gray-overview.png')
    preview=im.copy(); preview.thumbnail((1220,1400)); preview.save(R/f'{key}-overview.png')
    # High-resolution center detail includes arrows, labels and token cells.
    crop=(140*4,95*4,WIDTH*4-15*4,min(h,345)*4)
    im.crop(crop).save(R/f'{key}-detail.png')
    if key=='D2':
        im.crop((140*4,435*4,WIDTH*4-15*4,545*4)).save(R/'D2-block-detail.png')
    pdf=fitz.open(R/f'{key}.pdf'); assert abs(pdf[0].rect.width-WIDTH*.72)<.1
    proof=fitz.open(); page=proof.new_page(width=612,height=792)
    target=fitz.Rect(86.4,72,86.4+WIDTH*.72,72+h*.72)
    page.show_pdf_page(target,pdf,0)
    proof.save(R/f'{key}-letter-proof.pdf')
    page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(R/f'{key}-letter-proof.png')
    out_of_bounds=[b for b in bounds if b['bbox'][0]<7 or b['bbox'][2]>WIDTH-7 or b['bbox'][1]<7 or b['bbox'][3]>h-5]
    assert not out_of_bounds,(key,out_of_bounds)
    assert min(b['size_pt'] for b in bounds)>=10
    checks[key]={'png_dimensions_px':im.size,'width_in':WIDTH/100,'height_in':h/100,'ppi':400,'minimum_font_pt':min(b['size_pt'] for b in bounds),'text_bounds_violations':out_of_bounds,'text_bounds':bounds,'grayscale_range':gray.getextrema(),'pdf_width_pt':pdf[0].rect.width,'text_measurement':'Liberation Sans advance widths; conservative vertical extent; not a substitute for raster inspection'}
    manifest['figures'].append({'id':key,'source':f'figures/{key}.svg','generator':'figures/generate_figures.py','data':'figures/figure-data.json','png':f'figures/{key}.png','pdf':f'figures/{key}.pdf','grayscale_png':f'figures/{key}-gray.png','actual_size_proof':f'figures/{key}-letter-proof.pdf','reproduction_command':'python3 research/diffusion-20261028/figures/generate_figures.py','command_working_directory':'repository root; generator is also independent of cwd','requirements':['Python 3','Pillow','PyMuPDF','Inkscape','Liberation Sans font'],'intended_width_in':WIDTH/100,'intended_height_in':h/100,'ppi':400,'caption':captions[key],'alt_text':alts[key],'related_prose_anchors':D[key]['prose_anchors'],'evidence_claim_ids':D[key]['claims'],'data_status':'ILLUSTRATIVE_CONCEPTUAL_NOT_MEASURED'})
(R/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
(R/'geometry-checks.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'rendered':list(figs),'width_in':WIDTH/100,'checks':'figures/geometry-checks.json'},indent=2))
