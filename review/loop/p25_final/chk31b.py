import pymupdf
pdf='/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
outdir='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_final'
d=pymupdf.open(pdf)
pg=d[49]
# figure bbox y up to 661. Crop the bottom band 560-680 full width, high res
clip=pymupdf.Rect(70, 560, 532, 685)
pix=pg.get_pixmap(matrix=pymupdf.Matrix(7,7), clip=clip)
pix.save(f'{outdir}/fig3_1_band.png')
print("saved", pix.width, pix.height)
