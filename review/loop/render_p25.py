import pymupdf, os
d = pymupdf.open('/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf')
outdir = '/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_render'
os.makedirs(outdir, exist_ok=True)
pages = [17,18,26,27,34,38,55,69,81,84,86,98,102,103,104,105,110,114,122,130,135,140,145,146,156,162,168]
for i in pages:
    pg = d[i]
    m = pymupdf.Matrix(3,3)   # ~216 dpi
    pix = pg.get_pixmap(matrix=m)
    fn = f"{outdir}/p{i}.png"
    pix.save(fn)
    print(f"page {i} -> {fn}  ({pix.width}x{pix.height})")
