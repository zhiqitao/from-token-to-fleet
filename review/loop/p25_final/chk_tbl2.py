import pymupdf
pdf='/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
outdir='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_final'
d=pymupdf.open(pdf)
for pg,label in [(128,'tbl10_1'),(133,'tbl_p133')]:
    p=d[pg]
    pix=p.get_pixmap(matrix=pymupdf.Matrix(4,4))
    pix.save(f'{outdir}/{label}.png')
    print(label, pix.width, pix.height)
