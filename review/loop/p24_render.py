import pymupdf, os
doc = pymupdf.open('/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf')
out = '/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/pass24_r_render'
os.makedirs(out, exist_ok=True)
# figure-heavy / suspected figure pages (1-indexed)
pages = [157,163,164,170,176,177,190,195,213,216,221,222,235,240,247,255,256,257,267,268,275,281,286,288,289,290,293,295,296,297,298]
for pn in pages:
    p = doc[pn-1]
    pm = p.get_pixmap(matrix=pymupdf.Matrix(200/72,200/72))
    pm.save(f'{out}/p{pn}.png')
print("rendered", len(pages), "pages into", out)
