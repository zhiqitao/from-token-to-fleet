import pymupdf, os
d = pymupdf.open('/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf')
outdir = '/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25_fig'
os.makedirs(outdir, exist_ok=True)
pages = [17,18,26,27,34,38,55,69,81,84,86,98,102,103,104,105,110,114,122,130,135,140,145,146,156,162,168]
for i in pages:
    pg = d[i]
    dr = pg.get_drawings()
    xs, ys = [], []
    for p in dr:
        r = p['rect']
        xs += [r.x0, r.x1]; ys += [r.y0, r.y1]
    if not xs:
        print(f"page {i}: no drawings"); continue
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    print(f"page {i}: figure rect x[{x0:.0f},{x1:.0f}] y[{y0:.0f},{y1:.0f}]  w={x1-x0:.0f} h={y1-y0:.0f}")
    # crop at high res with padding
    pad = 20
    clip = pymupdf.Rect(max(0,x0-pad), max(0,y0-pad), min(pg.rect.x1,x1+pad), min(pg.rect.y1,y1+pad))
    m = pymupdf.Matrix(5.5,5.5)  # ~400 dpi
    pix = pg.get_pixmap(matrix=m, clip=clip)
    fn = f"{outdir}/fig{i}.png"
    pix.save(fn)
