from PIL import Image
import numpy as np, os, glob

d = '/home/ubuntu/hermes-work/from-token-to-fleet/review/loop/p25b_fig'
files = sorted(glob.glob(d+'/fig*.png'))
for f in files:
    im = Image.open(f).convert('L')
    a = np.array(im)
    h,w = a.shape
    # ink = darker than 200
    ink = a < 200
    xs = np.where(ink.any(axis=0))[0]
    ys = np.where(ink.any(axis=1))[0]
    if len(xs)==0:
        print(os.path.basename(f),'EMPTY'); continue
    x0,x1 = xs.min(), xs.max()
    y0,y1 = ys.min(), ys.max()
    # does ink touch any image edge?
    edge = []
    if x0<=0: edge.append('LEFT')
    if x1>=w-1: edge.append('RIGHT')
    if y0<=0: edge.append('TOP')
    if y1>=h-1: edge.append('BOTTOM')
    # margins in pixels
    print(f"{os.path.basename(f):22s} {w}x{h}  inkbox x[{x0},{x1}] y[{y0},{y1}]  margins L{x0} R{w-1-x1} T{y0} B{h-1-y1}  {'EDGE-TOUCH:'+','.join(edge) if edge else 'ok'}")
