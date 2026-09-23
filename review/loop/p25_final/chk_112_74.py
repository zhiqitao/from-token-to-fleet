import pymupdf, numpy as np
from PIL import Image
pdf='/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
outdir='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_final'
d=pymupdf.open(pdf)

# --- Fig 11.2 (pdf p143 idx142): check the TOP-RIGHT orange card header "RESOURCE SPECIALISATION"
pg=d[142]
# render the upper-right quadrant of the figure at high res
clip=pymupdf.Rect(300, 180, 532, 320)
pix=pg.get_pixmap(matrix=pymupdf.Matrix(7,7), clip=clip)
pix.save(f'{outdir}/fig11_2_topright.png')
print("11.2 topright", pix.width, pix.height)

# --- Fig 7.4 (pdf p102 idx101): check scenario-reserve call-out vs red banner
pg74=d[101]
clip2=pymupdf.Rect(70, 45, 532, 260)
pix2=pg74.get_pixmap(matrix=pymupdf.Matrix(6,6), clip=clip2)
pix2.save(f'{outdir}/fig7_4_top.png')
print("7.4 top", pix2.width, pix2.height)
