#!/usr/bin/env python3
"""
Renders high-fidelity 64x64 isometric item icons with transparent background
for all vehicles in Vehicle Fleet.
"""
import sys, os, math, time
sys.path.insert(0, r'c:\Users\Purachai\Desktop\Minecraft Mode Creator\minecraft_mod_creator\Vehicle Fleet\scripts')
sys.path.insert(0, r'c:\Users\Purachai\Desktop\Minecraft Mode Creator\minecraft_mod_creator\Titan Combat\scripts')

import gen_fleet as F
from PIL import Image

FACES = {
    'north': ((0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)),
    'south': ((1, 1, 1), (0, 1, 1), (0, 0, 1), (1, 0, 1)),
    'east':  ((1, 1, 0), (1, 1, 1), (1, 0, 1), (1, 0, 0)),
    'west':  ((0, 1, 1), (0, 1, 0), (0, 0, 0), (0, 0, 1)),
    'up':    ((0, 1, 1), (1, 1, 1), (1, 1, 0), (0, 1, 0)),
    'down':  ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))
}

SKIP_BONES = {'cargo_straps', 'sling_hook', 'sling_cables', 'sling_rig_clamp'}

def render_icon(bones, tex, yaw=-45, pitch=-22, size=64):
    W = H = size
    zbuf = [[1e9] * W for _ in range(H)]
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    light = (0.55, 0.82, -0.42)
    ln_l = math.sqrt(sum(v*v for v in light))
    light = tuple(v / ln_l for v in light)

    yaw_rad, pitch_rad = math.radians(yaw), math.radians(pitch)
    cy, sy = math.cos(yaw_rad), math.sin(yaw_rad)
    cp, sp = math.cos(pitch_rad), math.sin(pitch_rad)

    min_x, max_x = 1e9, -1e9
    min_y, max_y = 1e9, -1e9
    quads = []

    for b in bones:
        if b['name'] in SKIP_BONES: continue
        for c in b.get('cubes', []):
            o, s = c['origin'], c['size']
            for f, corners in FACES.items():
                pts = []
                for k in corners:
                    px = o[0] + k[0] * s[0]
                    py = o[1] + k[1] * s[1]
                    pz = o[2] + k[2] * s[2]
                    rx = px * cy - pz * sy
                    rz = px * sy + pz * cy
                    ry = py * cp - rz * sp
                    rz = py * sp + rz * cp
                    pts.append((rx, ry, rz))
                    min_x = min(min_x, rx); max_x = max(max_x, rx)
                    min_y = min(min_y, ry); max_y = max(max_y, ry)

                e1 = (pts[1][0] - pts[0][0], pts[1][1] - pts[0][1], pts[1][2] - pts[0][2])
                e2 = (pts[3][0] - pts[0][0], pts[3][1] - pts[0][1], pts[3][2] - pts[0][2])
                n = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
                ln = math.sqrt(sum(v*v for v in n)) or 1
                norm = tuple(v / ln for v in n)
                if norm[2] > 0.05: continue
                shade = 0.52 + 0.48 * max(0.0, -sum(norm[i] * light[i] for i in range(3)))
                uv = c['uv'][f]
                quads.append((pts, norm, shade, uv['uv'], uv['uv_size']))

    dx = max_x - min_x or 1
    dy = max_y - min_y or 1
    scale = (size - 6) / max(dx, dy)
    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2

    TEX_W = len(tex[0]); TEX_H = len(tex)
    tuv = [(0, 0), (1, 0), (1, 1), (0, 1)]

    for pts, norm, shade, (u0, v0), (us, vs) in quads:
        cam = []
        for rx, ry, rz in pts:
            sx = W / 2 + (rx - mid_x) * scale
            sy = H / 2 - (ry - mid_y) * scale
            cam.append((sx, sy, rz))

        for tri in ((0, 1, 2), (0, 2, 3)):
            A, B, C = (cam[i] for i in tri)
            den = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1])
            if abs(den) < 1e-9: continue
            min_py = max(0, int(min(A[1], B[1], C[1])))
            max_py = min(H - 1, int(max(A[1], B[1], C[1])))
            min_qx = max(0, int(min(A[0], B[0], C[0])))
            max_qx = min(W - 1, int(max(A[0], B[0], C[0])))

            for py in range(min_py, max_py + 1):
                for qx in range(min_qx, max_qx + 1):
                    w0 = ((B[1] - C[1]) * (qx - C[0]) + (C[0] - B[0]) * (py - C[1])) / den
                    w1 = ((C[1] - A[1]) * (qx - C[0]) + (A[0] - C[0]) * (py - C[1])) / den
                    w2 = 1 - w0 - w1
                    if w0 < -1e-4 or w1 < -1e-4 or w2 < -1e-4: continue
                    z = w0 * A[2] + w1 * B[2] + w2 * C[2]
                    if z >= zbuf[py][qx]: continue
                    tu = w0 * tuv[tri[0]][0] + w1 * tuv[tri[1]][0] + w2 * tuv[tri[2]][0]
                    tv = w0 * tuv[tri[0]][1] + w1 * tuv[tri[1]][1] + w2 * tuv[tri[2]][1]
                    tx = min(TEX_W - 1, max(0, int(u0 + tu * us)))
                    ty = min(TEX_H - 1, max(0, int(v0 + tv * vs)))
                    tcol = tex[ty][tx]
                    if tcol[3] < 128: continue
                    zbuf[py][qx] = z
                    r = min(255, int(tcol[0] * shade))
                    g = min(255, int(tcol[1] * shade))
                    b = min(255, int(tcol[2] * shade))
                    img.putpixel((qx, py), (r, g, b, 255))
    return img

def main():
    t0 = time.time()
    out_dir = r'c:\Users\Purachai\Desktop\Minecraft Mode Creator\minecraft_mod_creator\Vehicle Fleet\src\main\resources\assets\vehiclefleet\textures\item'
    os.makedirs(out_dir, exist_ok=True)
    reg = F.registry()

    for key, (fn, _) in reg.items():
        bones, meta = fn()
        vid = meta['id']
        paint_cfg = F.PAINT.get(vid, {})
        tex = F.paint(meta['hull_rgb'], meta['belly_rgb'], **paint_cfg)
        bones = F.O.assign_uv(bones)

        yaw = -45
        pitch = -22 if not meta.get('kind') == 'ship' else -24
        img = render_icon(bones, tex, yaw=yaw, pitch=pitch, size=64)

        target_path = os.path.join(out_dir, vid + '.png')
        img.save(target_path)
        print(f"Rendered icon for {vid} -> {target_path}")

    print(f"Successfully generated all {len(reg)} vehicle icons in {time.time() - t0:.2f}s!")

if __name__ == '__main__':
    main()
