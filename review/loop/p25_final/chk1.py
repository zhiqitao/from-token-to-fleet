import pymupdf, numpy as np
from PIL import Image
pdf='/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
outdir='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_final'
d=pymupdf.open(pdf)
for pgidx in [22,23]:
    pg=d[pgidx]
    pix=pg.get_pixmap(matrix=pymupdf.Matrix(3,3))
    fn=f'{outdir}/chk_p{pgidx+1}.png'
    pix.save(fn)
    im=np.array(Image.open(fn).convert('L'))
    h,w=im.shape
    dark=(im<150)
    rowink=dark.sum(axis=1)
    nonempty=np.where(rowink>2)[0]
    print(f"page {pgidx+1}: size {w}x{h}")
    if len(nonempty):
        top,bot=nonempty[0],nonempty[-1]
        print(f"  ink rows {top}..{bot} of {h}; top empty {top/h:.2f} bottom empty {(h-bot)/h:.2f} contentH {bot-top}")
    colink=dark.sum(axis=0)
    ne=np.where(colink>2)[0]
    print(f"  ink cols {ne[0]}..{ne[-1]}; left {ne[0]} right {w-ne[-1]}")
