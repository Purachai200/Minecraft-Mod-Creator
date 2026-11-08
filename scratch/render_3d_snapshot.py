import json, zlib, struct, math

def write_png(path, w, h, rgba_bytes):
    raw = bytearray()
    row_bytes = w * 4
    for y in range(h):
        raw.append(0)
        start = y * row_bytes
        raw.extend(rgba_bytes[start:start+row_bytes])
    compressed = zlib.compress(bytes(raw))
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    out = b'\x89PNG\r\n\x1a\n'
    out += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    out += chunk(b'IDAT', compressed)
    out += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(out)

with open(r'Titan Combat/src/main/resources/assets/titancombat/geo/exo_frame_titan.geo.json', 'r', encoding='utf-8') as f:
    geo = json.load(f)

cubes = []
for b in geo['minecraft:geometry'][0]['bones']:
    bname = b['name']
    if bname.startswith('armor_'):
        continue
    for c in b.get('cubes', []):
        o = c['origin']
        s = c['size']
        cubes.append((bname, o[0], o[1], o[2], s[0], s[1], s[2]))

print(f"Loaded {len(cubes)} Sutherland cubes for 3D rendering.")

W, H = 760, 620
buf = bytearray(W * H * 4)
for y in range(H):
    t = y / (H - 1)
    r = int(22 * (1 - t) + 12 * t)
    g = int(26 * (1 - t) + 14 * t)
    b = int(34 * (1 - t) + 18 * t)
    for x in range(W):
        idx = (y * W + x) * 4
        buf[idx] = r
        buf[idx+1] = g
        buf[idx+2] = b
        buf[idx+3] = 255

yaw = -0.44
pitch = 0.16
zoom = 3.6
cx, cy = W // 2, H // 2 + 60

def project(x, y, z):
    y = y - 60
    cosY, sinY = math.cos(yaw), math.sin(yaw)
    x1 = x * cosY - z * sinY
    z1 = x * sinY + z * cosY
    cosP, sinP = math.cos(pitch), math.sin(pitch)
    y2 = y * cosP - z1 * sinP
    z2 = y * sinP + z1 * cosP
    px = cx + x1 * zoom
    py = cy - y2 * zoom
    return px, py, z2

def shade(rgb, factor):
    return (
        min(255, max(0, int(rgb[0] * factor))),
        min(255, max(0, int(rgb[1] * factor))),
        min(255, max(0, int(rgb[2] * factor)))
    )

PALETTE = {
    'paint': (94, 90, 112),        # Britannian Purplish Slate
    'paint2': (74, 70, 88),        # Dark Slate
    'metal': (120, 126, 134),      # Joints / Struts
    'steel': (176, 182, 190),      # Chrome pistons
    'dark': (36, 35, 42),          # Inner chassis & Landspinner tire
    'trim': (214, 162, 58),        # Britannian Imperial Gold
    'vent': (22, 24, 26),          # Thrusters
    'optic': (255, 32, 56)         # Factsphere ruby red crystal
}

quads = []
for c in cubes:
    bname, x0, y0, z0, dx, dy, dz = c
    x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz

    mat = 'paint'
    if bname == 'eye':
        mat = 'optic'
    elif bname == 'doorUp':
        if dy >= 8 and dx <= 1.6: mat = 'trim' # Antennae
        elif z0 < -8.5: mat = 'paint2'
        else: mat = 'paint'
    elif bname == 'body3':
        if z0 < -5.5 and dx <= 3.5: mat = 'trim' # Slash Harken bezels
        elif z0 > 15:
            mat = 'vent' if y0 <= 82 else 'paint2' # Dorsal Cockpit Pod
        else:
            mat = 'paint'
    elif bname == 'body2':
        mat = 'steel' if dx < 2 else 'dark'
    elif 'Arm' in bname:
        if ('rightArm1' in bname or 'leftArm1' in bname) and dx <= 2.2:
            mat = 'trim'
        elif 'Hand' in bname:
            mat = 'metal'
        else:
            mat = 'paint'
    elif 'Leg' in bname or 'Foot' in bname:
        if (x0 < -20 or x1 > 18) and y0 <= 20:
            # Landspinner
            if dx <= 1.5: mat = 'trim'
            elif dy <= 3.0 and y0 >= 15: mat = 'paint'
            elif dy >= 8: mat = 'dark'
            else: mat = 'metal'
        elif 'Foot' in bname:
            mat = 'dark' if y0 < 1 else 'paint'
        else:
            mat = 'paint'

    base_col = PALETTE[mat]

    verts = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)
    ]
    faces = [
        (0, 1, 2, 3, 0.90),
        (5, 4, 7, 6, 0.65),
        (4, 0, 3, 7, 0.78),
        (1, 5, 6, 2, 0.95),
        (3, 2, 6, 7, 1.15),
        (4, 5, 1, 0, 0.50)
    ]

    pverts = [project(*v) for v in verts]

    for f in faces:
        i0, i1, i2, i3, light = f
        p0, p1, p2, p3 = pverts[i0], pverts[i1], pverts[i2], pverts[i3]
        ax, ay = p1[0] - p0[0], p1[1] - p0[1]
        bx, by = p2[0] - p0[0], p2[1] - p0[1]
        if ax * by - ay * bx <= 0:
            continue
        avg_z = (p0[2] + p1[2] + p2[2] + p3[2]) / 4.0
        color = shade(base_col, light)
        quads.append((avg_z, [p0, p1, p2, p3], color))

quads.sort(key=lambda q: q[0], reverse=True)

for q in quads:
    _, pts, col = q
    poly = [(p[0], p[1]) for p in pts]
    min_y = max(0, int(min(p[1] for p in poly)))
    max_y = min(H - 1, int(max(p[1] for p in poly)))
    n = len(poly)
    for y in range(min_y, max_y + 1):
        intersections = []
        for i in range(n):
            p_a = poly[i]
            p_b = poly[(i + 1) % n]
            if (p_a[1] <= y < p_b[1]) or (p_b[1] <= y < p_a[1]):
                if abs(p_b[1] - p_a[1]) > 1e-4:
                    x = p_a[0] + (y - p_a[1]) * (p_b[0] - p_a[0]) / (p_b[1] - p_a[1])
                    intersections.append(x)
        intersections.sort()
        for k in range(0, len(intersections) - 1, 2):
            x_start = max(0, int(intersections[k]))
            x_end = min(W - 1, int(intersections[k + 1]))
            for x in range(x_start, x_end + 1):
                idx = (y * W + x) * 4
                buf[idx] = col[0]
                buf[idx + 1] = col[1]
                buf[idx + 2] = col[2]
                buf[idx + 3] = 255

out_png = r"C:\Users\Purachai\.gemini\antigravity\brain\dc63a5aa-ae1e-416f-8afe-779a698ca425\exo_grunt_3d_render.png"
write_png(out_png, W, H, buf)
print(f"Rendered overhauled Sutherland 3D image to: {out_png}")
