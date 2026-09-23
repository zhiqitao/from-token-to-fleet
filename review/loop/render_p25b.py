import pymupdf, os
PDF = '/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf'
d = pymupdf.open(PDF)
out_render = '/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25b_render'
out_fig = '/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25b_fig'
os.makedirs(out_render, exist_ok=True)
os.makedirs(out_fig, exist_ok=True)

# assigned pdf pages (1-indexed) -> figure number label
figs = {
 161:'13_1', 167:'14_1', 173:'15_1', 175:'15_2', 189:'16_1', 192:'17_1',
 212:'18_1', 215:'19_1', 220:'19_2', 221:'19_3', 234:'20_1', 239:'21_1',
 246:'22_1', 255:'23_1', 267:'24_1', 274:'25_1', 280:'26_1', 285:'26_2',
 287:'A_1', 291:'A_2', 294:'A_3', 295:'A_4',
}

for pg1, name in figs.items():
    i = pg1 - 1
    pg = d[i]
    # full page at ~192 dpi
    full = pg.get_pixmap(matrix=pymupdf.Matrix(2.7,2.7))
    ff = f"{out_render}/pg{pg1:03d}_{name}.png"
    full.save(ff)
    # figure crop based on drawings bbox
    dr = pg.get_drawings()
    xs, ys = [], []
    for p in dr:
        r = p['rect']
        xs += [r.x0, r.x1]; ys += [r.y0, r.y1]
    if xs:
        x0,x1,y0,y1 = min(xs),max(xs),min(ys),max(ys)
        pad = 15
        clip = pymupdf.Rect(max(0,x0-pad), max(0,y0-pad), min(pg.rect.x1,x1+pad), min(pg.rect.y1,y1+pad))
        m = pymupdf.Matrix(4.3,4.3)  # ~310 dpi
        pix = pg.get_pixmap(matrix=m, clip=clip)
        cf = f"{out_fig}/fig{pg1:03d}_{name}.png"
        pix.save(cf)
        print(f"page {pg1} {name}: clip x[{x0:.0f},{x1:.0f}] y[{y0:.0f},{y1:.0f}] w={x1-x0:.0f} h={y1-y0:.0f} -> {cf} {pix.width}x{pix.height} | full {full.width}x{full.height}")
    else:
        print(f"page {pg1} {name}: NO drawings")
