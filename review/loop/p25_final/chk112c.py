import pymupdf
pdf='/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
outdir='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_final'
d=pymupdf.open(pdf)
pg=d[142]
# orange header bar region, generous bounds incl. left edge
clip=pymupdf.Rect(300, 272, 512, 296)
pix=pg.get_pixmap(matrix=pymupdf.Matrix(12,12), clip=clip)
pix.save(f'{outdir}/fig11_2_orangear.png')
print("saved", pix.width, pix.height)
