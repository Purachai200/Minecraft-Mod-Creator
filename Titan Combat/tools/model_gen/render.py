"""Tiny flat-shaded preview renderer for Bedrock geo files (verification only).
usage: render.py geo.json out.png [skip_prefix,...] [sign]"""
import json, math, sys
import numpy as np
from PIL import Image, ImageDraw

def rot(rx, ry, rz, sign=1):
    rx, ry, rz = math.radians(-rx), math.radians(ry), math.radians(-rz)
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    X = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Z = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Z @ Y @ X

def load(path):
    return json.load(open(path))['minecraft:geometry'][0]

def faces(o, s, inf=0):
    x0, y0, z0 = o[0]-inf, o[1]-inf, o[2]-inf
    x1, y1, z1 = o[0]+s[0]+inf, o[1]+s[1]+inf, o[2]+s[2]+inf
    v = np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]], float)
    f = [(0,1,2,3,(0,0,-1)),(5,4,7,6,(0,0,1)),(4,0,3,7,(-1,0,0)),(1,5,6,2,(1,0,0)),(3,2,6,7,(0,1,0)),(4,5,1,0,(0,-1,0))]
    return v, f

def render(geo, out, skip=(), sign=1, view='side', scale=4, hide_bones=()):
    bones = {b['name']: b for b in geo['bones']}
    def chain(b):
        c = []
        while b:
            c.append(b); b = bones.get(b.get('parent'))
        return c
    polys = []
    for b in geo['bones']:
        if any(b['name'].startswith(p) for p in skip) or b['name'] in hide_bones: continue
        ch = chain(b)
        if any(any(x['name'].startswith(p) for p in skip) for x in ch): continue
        for c in b.get('cubes', []):
            v, f = faces(c['origin'], c['size'], c.get('inflate', 0))
            if 'rotation' in c:
                p = np.array(c.get('pivot', c['origin']), float)
                v = (rot(*c['rotation'], sign) @ (v - p).T).T + p
            for x in ch:
                if 'rotation' in x:
                    p = np.array(x['pivot'], float)
                    v = (rot(*x['rotation'], sign) @ (v - p).T).T + p
            for (a, bb, cc, d, n) in f:
                poly = v[[a, bb, cc, d]]
                polys.append((poly, c.get('_col', (150, 155, 165)), n))
    # camera: side looks along x (screen = z,y); front looks along z (screen = x,y)
    allv = np.concatenate([p[0] for p in polys])
    if view == 'side': ax, depth = 2, 0
    elif view == 'front': ax, depth = 0, 2
    else: ax, depth = 0, 1  # top
    sy_ax = 1 if view != 'top' else 2
    mn, mx = allv.min(0), allv.max(0)
    W = int((mx[ax]-mn[ax]+20)*scale); H = int((mx[sy_ax]-mn[sy_ax]+20)*scale)
    img = Image.new('RGB', (W, H), (30, 34, 40)); dr = ImageDraw.Draw(img)
    def key(p): return p[0][:, depth].mean() * (1 if view != 'top' else 1)
    polys.sort(key=lambda p: -p[0][:, depth].mean() if view != 'front' else p[0][:, depth].mean())
    L = np.array([0.3, 0.8, -0.5]); L /= np.linalg.norm(L)
    for poly, col, n in polys:
        e1, e2 = poly[1]-poly[0], poly[3]-poly[0]
        nn = np.cross(e1, e2); nl = np.linalg.norm(nn)
        sh = 0.55 + 0.45 * abs(np.dot(nn/ (nl or 1), L))
        pts = [((p[ax]-mn[ax]+10)*scale, H - (p[sy_ax]-mn[sy_ax]+10)*scale) for p in poly]
        dr.polygon(pts, fill=tuple(int(c*sh) for c in col), outline=(15, 15, 18))
    img.save(out)

if __name__ == '__main__':
    g = load(sys.argv[1])
    skip = tuple(sys.argv[3].split(',')) if len(sys.argv) > 3 and sys.argv[3] else ()
    sign = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    for v in ('side', 'front'):
        render(g, sys.argv[2].replace('.png', f'_{v}.png'), skip, sign, v)
