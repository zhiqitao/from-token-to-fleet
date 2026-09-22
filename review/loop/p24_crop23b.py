import pymupdf, PIL.Image as I
doc = pymupdf.open('/home/ubuntu/hermes-work/from-token-to-fleet/render/build/from-token-to-fleet-v20260913.pdf')
out='/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/pass24_r_render/'
p = doc[255]
pm = p.get_pixmap(matrix=pymupdf.Matrix(400/72,400/72))
pm.save(out+'p256_hi.png')
im = I.open(out+'p256_hi.png'); w,h=im.size
im.crop((int(w*0.12), int(h*0.30), int(w*0.88), int(h*0.75))).save(out+'p256fig_crop2.png')
print("ok")
