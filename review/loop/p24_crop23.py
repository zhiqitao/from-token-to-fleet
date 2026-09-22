import pymupdf
doc = pymupdf.open('/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf')
out='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/pass24_r_render/'
p = doc[255]  # p256 1-indexed
# high dpi
pm = p.get_pixmap(matrix=pymupdf.Matrix(400/72,400/72))
pm.save(out+'p256_hi.png')
print("p256_hi size", pm.width, pm.height)
# also crop the figure region at 400dpi: figure likely centered vertically mid page
# crop full figure area (y from ~25% to ~80%)
import PIL.Image as I
im = I.open(out+'p256_hi.png')
w,h = im.size
# crop central band containing the funnel
box = (int(w*0.15), int(h*0.18), int(w*0.85), int(h*0.62))
im.crop(box).save(out+'p256fig_crop.png')
print("crop saved", box)
