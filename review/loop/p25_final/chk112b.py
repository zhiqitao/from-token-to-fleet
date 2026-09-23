import pymupdf, numpy as np
from PIL import Image
pdf='/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
outdir='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_final'
d=pymupdf.open(pdf)
pg=d[142]  # fig 11.2 pdf p143
# render full figure region at high res
clip=pymupdf.Rect(86, 52, 526, 575)
pix=pg.get_pixmap(matrix=pymupdf.Matrix(7,7), clip=clip)
pix.save(f'{outdir}/fig11_2_full7.png')
im=np.array(Image.open(f'{outdir}/fig11_2_full7.png').convert('RGB'))
h,w,_=im.shape
print("full7 size", w, h)
R,G,B=im[:,:,0].astype(int),im[:,:,1].astype(int),im[:,:,2].astype(int)
# orange header bar: strong orange
orange=(R>180)&(R<255)&(G>80)&(G<180)&(B<90)
rows=orange.sum(axis=1)
ys=np.where(rows>40)[0]
print("orange rows:", ys.min() if len(ys) else None, ys.max() if len(ys) else None)
if len(ys):
    ymean=int(ys.min())+8
    # horizontal extent of orange at a row in the header
    row=orange[ymean]
    xs=np.where(row)[0]
    print("orange x extent at row", ymean, ":", xs.min(), xs.max())
    ox0,ox1=xs.min(),xs.max()
    # Check for WHITE text pixels near the left edge of orange bar (text clipped at left edge)
    # white bold text
    sub=im[ys.min():ys.max(), ox0:ox1]
    white=(sub[:,:,0]>200)&(sub[:,:,1]>200)&(sub[:,:,2]>200)
    # For each column in the leftmost 20% of the orange bar, is there white ink?
    leftw=white[:, :int((ox1-ox0)*0.10)].sum(axis=0)
    print("white-ink count per first 10% columns:", leftw.tolist())
