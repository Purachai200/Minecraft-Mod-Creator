"""Render a Bedrock geo + texture to a PNG (right side, left side, 3/4 top views) to check gun models
without launching the game.

  python3 tools/preview_geo.py <geo.json> <texture.png> <out.png> [--hide bone1,bone2]

Bedrock geo is converted to Blockbench space (x negated, rotations [-x, -y, z], ZYX order). Per-face UVs only.
"""
import json, math, sys
from PIL import Image, ImageDraw


def rot_matrix(r):
    x, y, z = (math.radians(a) for a in (-r[0], -r[1], r[2]))
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    rz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    return mul(rz, mul(ry, rx))


def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def apply(m, p):
    return [sum(m[i][k] * p[k] for k in range(3)) for i in range(3)]


def bb(p):
    return [-p[0], p[1], p[2]]


def transforms(bones):
    """bone name -> list of (pivot, matrix) from the bone up to the root, all in Blockbench space."""
    by = {b["name"]: b for b in bones}
    out = {}
    for b in bones:
        chain, cur = [], b
        while cur:
            if cur.get("rotation"):
                chain.append((bb(cur["pivot"]), rot_matrix(cur["rotation"])))
            cur = by.get(cur.get("parent"))
        out[b["name"]] = chain
    return out


def rotate_about(p, piv, m):
    return [a + b for a, b in zip(apply(m, [p[i] - piv[i] for i in range(3)]), piv)]


FACES = {  # face -> (TL, TR, BL) corner picks (0 = min, 1 = max) for x, y, z in Blockbench space
    "north": ((1, 1, 0), (0, 1, 0), (1, 0, 0)),
    "south": ((0, 1, 1), (1, 1, 1), (0, 0, 1)),
    "east": ((1, 1, 1), (1, 1, 0), (1, 0, 1)),
    "west": ((0, 1, 0), (0, 1, 1), (0, 0, 0)),
    "up": ((0, 1, 0), (1, 1, 0), (0, 1, 1)),
    "down": ((0, 0, 0), (1, 0, 0), (0, 0, 1)),
}
NORMAL = {"north": (0, 0, -1), "south": (0, 0, 1), "east": (1, 0, 0), "west": (-1, 0, 0), "up": (0, 1, 0), "down": (0, -1, 0)}


def quads(geo, tex, hide=()):
    """Yield (corners3d, rgba, normal) for every texel of every visible face."""
    g = geo["minecraft:geometry"][0]
    tw, th = g["description"]["texture_width"], g["description"]["texture_height"]
    sx, sy = tex.width / tw, tex.height / th
    px = tex.load()
    bones = g["bones"]
    chains = transforms(bones)
    by = {b["name"]: b for b in bones}

    def hidden(name):
        while name:
            if name in hide:
                return True
            name = by[name].get("parent")
        return False

    for b in bones:
        if hidden(b["name"]):
            continue
        for c in b.get("cubes", []):
            o, s, inf = bb(c["origin"]), c["size"], c.get("inflate", 0)
            lo = [-c["origin"][0] - s[0] - inf, c["origin"][1] - inf, c["origin"][2] - inf]
            hi = [lo[0] + s[0] + 2 * inf, lo[1] + s[1] + 2 * inf, lo[2] + s[2] + 2 * inf]
            cube_rot = [(bb(c["pivot"]), rot_matrix(c["rotation"]))] if c.get("rotation") else []

            def tf(p):
                for piv, m in cube_rot + chains[b["name"]]:
                    p = rotate_about(p, piv, m)
                return p

            for fname, f in c["uv"].items():
                (u, v), (uw, vh) = f["uv"], f["uv_size"]
                tl, tr, bl = ([(lo, hi)[k[i]][i] for i in range(3)] for k in FACES[fname])
                normal = NORMAL[fname]
                for piv, m in cube_rot + chains[b["name"]]:
                    normal = apply(m, normal)
                cols, rows = max(1, math.ceil(abs(uw) - 1e-6)), max(1, math.ceil(abs(vh) - 1e-6))
                for j in range(rows):
                    for i in range(cols):
                        a0, a1, b0, b1 = i / cols, (i + 1) / cols, j / rows, (j + 1) / rows
                        tu = u + uw * (i + 0.5) / cols
                        tv = v + vh * (j + 0.5) / rows
                        col = px[min(tex.width - 1, max(0, int(tu * sx))), min(tex.height - 1, max(0, int(tv * sy)))]
                        if col[3] < 8:
                            continue

                        def at(a, bb_):
                            return [tl[k] + (tr[k] - tl[k]) * a + (bl[k] - tl[k]) * bb_ for k in range(3)]
                        yield [tf(at(a0, b0)), tf(at(a1, b0)), tf(at(a1, b1)), tf(at(a0, b1))], col, normal


def render(qs, yaw, pitch, w, h, light=(0.4, 0.8, 0.45)):
    cy, sy, cp, sp = math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def view(p):
        x, z = p[0] * cy - p[2] * sy, p[0] * sy + p[2] * cy
        x = -x  # viewer looks down +z, so mirror x to keep the image right-handed
        y, z = p[1] * cp - z * sp, p[1] * sp + z * cp
        return x, y, z

    proj = []
    for corners, col, n in qs:
        vs = [view(p) for p in corners]
        vn = view(n)
        if vn[2] > 1e-3:  # back face (camera looks down -z of view space toward +z? keep faces facing viewer)
            continue
        ln = max(0.0, n[0] * light[0] + n[1] * light[1] + n[2] * light[2]) / math.sqrt(sum(l * l for l in light))
        k = 0.55 + 0.5 * ln
        rgb = tuple(min(255, int(col[i] * k)) for i in range(3))
        proj.append((sum(v[2] for v in vs) / 4, vs, rgb))
    if not proj:
        return Image.new("RGB", (w, h), (40, 44, 52))
    xs = [v[0] for _, vs, _ in proj for v in vs]
    ys = [v[1] for _, vs, _ in proj for v in vs]
    scale = min((w - 20) / max(1e-3, max(xs) - min(xs)), (h - 20) / max(1e-3, max(ys) - min(ys)))
    ox, oy = (w - (max(xs) - min(xs)) * scale) / 2 - min(xs) * scale, (h - (max(ys) - min(ys)) * scale) / 2 + max(ys) * scale
    img = Image.new("RGB", (w, h), (40, 44, 52))
    d = ImageDraw.Draw(img)
    for _, vs, rgb in sorted(proj, key=lambda t: -t[0]):
        d.polygon([(ox + v[0] * scale, oy - v[1] * scale) for v in vs], fill=rgb)
    return img


def main():
    geo_path, tex_path, out = sys.argv[1:4]
    hide = set(sys.argv[sys.argv.index("--hide") + 1].split(",")) if "--hide" in sys.argv else set()
    hide |= {"lefthand_pos", "righthand_pos", "lefthand", "righthand"}
    geo = json.load(open(geo_path))
    qs = list(quads(geo, Image.open(tex_path).convert("RGBA"), hide))
    views = [(90, 0), (-90, 0), (125, 25), (55, -20)]  # right side, left side, 3/4 from rear-right-top, front-left-low
    W, H = 1100, 340
    sheet = Image.new("RGB", (W, H * len(views)), (40, 44, 52))
    for i, (yaw, pitch) in enumerate(views):
        sheet.paste(render(qs, yaw, pitch, W, H), (0, i * H))
    sheet.save(out)


if __name__ == "__main__":
    main()
