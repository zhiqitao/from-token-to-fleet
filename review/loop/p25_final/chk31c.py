import pymupdf, numpy as np
from PIL import Image
pdf='/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
outdir='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_final'
d=pymupdf.open(pdf)
pg=d[49]
# render full figure area at high res and detect colored banner bars
clip=pymupdf.Rect(70,45,532,680)
pix=pg.get_pixmap(matrix=pymupdf.Matrix(6,6), clip=clip)
pix.save(f'{outdir}/fig3_1_full.png')
im=np.array(Image.open(f'{outdir}/fig3_1_full.png').convert('RGB'))
h,w,_=im.shape
print("fig3_1 full render", w, h)
R,G,B=im[:,:,0].astype(int),im[:,:,1].astype(int),im[:,:,2].astype(int)
# red-ish banner: strong red, low green/blue
red=(R>120)&(G<90)&(B<90)
rows=red.sum(axis=1)
ys=np.where(rows>30)[0]
print("rows with heavy red (banner candidates):", ys[:50] if len(ys) else "none")
# find vertical extent of any red band
if len(ys):
    # cluster
    print("red row range:", ys.min(), ys.max(), "count", len(ys))
# Also check horizontal red distribution per clustered band
