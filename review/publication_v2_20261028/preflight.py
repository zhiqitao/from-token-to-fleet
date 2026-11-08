"""Objective PDF observations. Scans are not human or vision coverage."""
from pathlib import Path
import hashlib
import json
import re
import pymupdf
ROOT = Path(__file__).resolve().parent
PDF = ROOT/'baseline/from-token-to-fleet-v20260913.pdf'
doc = pymupdf.open(PDF)
figures=[]
observations={'out_of_page':[],'nul_pages':[],'raster_placements':[],'invalid_internal_links':[],'type3_fonts':[],'unembedded_fonts':[],'caption_candidates':[]}
fonts={}
for i,p in enumerate(doc):
    text=p.get_text()
    if '\x00' in text: observations['nul_pages'].append(i+1)
    for match in re.finditer(r'(?im)^figure\s+(\d+\.\d+)\s*[:.—–-]',text):
        figures.append({'figure_id':match.group(1),'pdf_page':i+1,'printed_page':p.get_label(),'caption_anchor':text[match.start():match.start()+500].replace('\n',' '),'technical':'NOT VERIFIED','print':'NOT VERIFIED','design':'NOT VERIFIED','pedagogy':'NOT VERIFIED','verdict':'NOT VERIFIED','inspection':'OPEN'})
    for b in p.get_text('dict')['blocks']:
        for line in b.get('lines',[]):
            for s in line['spans']:
                x0,y0,x1,y1=s['bbox']
                if x0 < -.5 or y0 < -.5 or x1 > p.rect.width+.5 or y1 > p.rect.height+.5:
                    observations['out_of_page'].append({'page':i+1,'text':s['text'],'bbox':s['bbox']})
    for image in p.get_image_info(xrefs=True):
        x0,y0,x1,y1=image['bbox']; w=x1-x0;h=y1-y0
        observations['raster_placements'].append({'page':i+1,'xref':image['xref'],'pixel_width':image['width'],'pixel_height':image['height'],'bbox':image['bbox'],'ppi_x':round(image['width']*72/w,2) if w else None,'ppi_y':round(image['height']*72/h,2) if h else None})
    for l in p.get_links():
        if l.get('kind')==pymupdf.LINK_GOTO and not 0<=l.get('page',-1)<len(doc): observations['invalid_internal_links'].append({'page':i+1,'link':str(l)})
    for f in p.get_fonts():fonts[f[0]]=f
for xref,f in fonts.items():
    if f[2]=='Type3': observations['type3_fonts'].append(list(f))
    try:
        extracted=doc.extract_font(xref)
        if not extracted[3]:observations['unembedded_fonts'].append(list(f))
    except Exception as e:observations['unembedded_fonts'].append({'font':list(f),'error':str(e)})
observations['catalog']={k:doc.xref_get_key(doc.pdf_catalog(),k) for k in ['StructTreeRoot','MarkInfo','Lang','Metadata']}
observations['figures_count']=len(figures)
(ROOT/'figures_candidates.json').write_text(json.dumps(figures,indent=2))
(ROOT/'work/preflight.json').write_text(json.dumps(observations,indent=2))
# Pixel transport smoke test: whole page plus detailed first-figure crop.
p=doc[24]
p.get_pixmap(dpi=110).save(ROOT/'renders/page-0025-full.png')
p.get_pixmap(dpi=230,clip=pymupdf.Rect(45,50,565,550)).save(ROOT/'renders/page-0025-detail.png')
print(json.dumps({'pages':len(doc),'numbered_caption_occurrences':len(figures),'unique_ids':len({f['figure_id'] for f in figures}),'figures':[(f['figure_id'],f['pdf_page']) for f in figures],'out_of_page':len(observations['out_of_page']),'nul_pages':observations['nul_pages'],'raster_placements':len(observations['raster_placements']),'under_300ppi':len([r for r in observations['raster_placements'] if min(r['ppi_x'],r['ppi_y'])<300]),'invalid_internal_links':len(observations['invalid_internal_links']),'type3_fonts':len(observations['type3_fonts']),'unembedded_fonts':len(observations['unembedded_fonts'])},indent=2))
