import pymupdf, numpy as np
from PIL import Image
pdf='/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
outdir='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_final'
d=pymupdf.open(pdf)
# page 50 (idx49) fig3_1: inspect bottom region of figure
pg=d[49]
dr=pg.get_drawings()
xs=[];ys=[]
for p in dr:
    r=p['rect']; xs+=[r.x0,r.x1]; ys+=[r.y0,r.y1]
y0,y1=min(ys),max(ys); x0,x1=min(xs),max(xs)
print("fig3_1 drawings bbox x[%.1f,%.1f] y[%.1f,%.1f] page H %.1f"%(x0,x1,y0,y1,pg.rect.y1))
# render the bottom 15% of the figure bbox at high res
band=0.15
clip=pymupdf.Rect(x0-10, y1-(y1-y0)*band, x1+10, y1+10)
pix=pg.get_pixmap(matrix=pymupdf.Matrix(8,8), clip=clip)
pix.save(f'{outdir}/fig3_1_bottom.png')
print("saved bottom zoom", pix.width, pix.height)
# also render full figure bottom up to page bottom
clip2=pymupdf.Rect(x0-10, y1-120, x1+10, min(pg.rect.y1,y1+150))
pix2=pg.get_pixmap(matrix=pymupdf.Matrix(5,5), clip=clip2)
pix2.save(f'{outdir}/fig3_1_bottom2.png')
print("saved bottom2", pix2.width, pix2.height)
