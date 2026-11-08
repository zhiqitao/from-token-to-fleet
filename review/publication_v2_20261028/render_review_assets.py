"""Prepare review images in parallel. Rendering never marks a page inspected."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import hashlib
import json
import time
import pymupdf
ROOT = Path(__file__).resolve().parent
PDF = ROOT/'baseline/from-token-to-fleet-v20260913.pdf'
OUT = ROOT/'renders/batch'

def render_page(number):
    with pymupdf.open(PDF) as doc:
        page=doc[number-1]
        dest=OUT/f'page-{number:04d}.png'
        if not dest.exists(): page.get_pixmap(dpi=110).save(dest)
        return {'pdf_page':number,'path':str(dest.relative_to(ROOT)),'dpi':110,'inspection':'NOT CHECKED'}

def render_figure(item):
    with pymupdf.open(PDF) as doc:
        page=doc[item['pdf_page']-1]
        stem=f"figure-{item['figure_id'].replace('.','-')}-page-{item['pdf_page']:04d}"
        dest=OUT/f'{stem}-detail.png'
        gray=OUT/f'{stem}-gray.png'
        # Full body region deliberately includes caption/neighborhood to avoid uncertain clipping.
        clip=pymupdf.Rect(40,55,page.rect.width-40,page.rect.height-45)
        if not dest.exists():page.get_pixmap(dpi=230,clip=clip).save(dest)
        if not gray.exists():page.get_pixmap(dpi=150,clip=clip,colorspace=pymupdf.csGRAY).save(gray)
        return {'figure_id':item['figure_id'],'pdf_page':item['pdf_page'],'detail_path':str(dest.relative_to(ROOT)),'gray_path':str(gray.relative_to(ROOT)),'region_pt':list(clip),'inspection':'NOT CHECKED'}

if __name__=='__main__':
    started=time.monotonic();OUT.mkdir(parents=True,exist_ok=True)
    with pymupdf.open(PDF) as doc:count=len(doc)
    figures=json.loads((ROOT/'figures_candidates.json').read_text())
    with ProcessPoolExecutor(max_workers=4) as pool:
        pages=list(pool.map(render_page,range(1,count+1)))
        results=list(pool.map(render_figure,figures))
    manifest={'proof_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'pages':pages,'figures':results,'note':'Image generation only; no visual verification implied.','elapsed_seconds':round(time.monotonic()-started,2)}
    (ROOT/'work/render_assets_manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps({'rendered_pages':len(pages),'figure_detail_regions':len(results),'grayscale_regions':len(results),'elapsed_seconds':manifest['elapsed_seconds']}),flush=True)
