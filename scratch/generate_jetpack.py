"""Rebuilds the Titan Combat rocket jump-jet pack: geo + a shaded 128x128 texture.

Run from the repo root:  python3 scratch/generate_jetpack.py
Bone names (root / docking_mount / nozzle_left / nozzle_right) are what TitanFlightModuleLayer animates.
+Z points away from the titan's back; z=0 is the face that sits on the chassis.
"""
import json, os, struct, zlib

ROOT = "Titan Combat/src/main/resources/assets/titancombat"
W = H = 128

# --- palette ---------------------------------------------------------------
ARMOR = (148, 150, 140)      # light composite plating
GUNMETAL = (62, 66, 74)
STEEL = (104, 106, 112)
ORANGE = (226, 112, 34)
RED = (220, 40, 36)


def noise(x, y, seed):
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n >> 16) & 0xff) / 255.0 - 0.5


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# --- face painters: f(x, y, w, h, face) -> rgb -------------------------------
def plate(base, seams=True, rivets=True, seed=1):
    def paint(x, y, w, h, face):
        k = 1.0 + noise(x, y, seed) * 0.07
        if y == 0 or x == 0:
            k *= 1.18                    # bevel highlight
        elif y == h - 1 or x == w - 1:
            k *= 0.62                    # bevel shadow
        elif seams and w >= 6 and h >= 6 and (y == h // 2 or (w >= 10 and x == w // 2)):
            k *= 0.78                    # panel seam
        elif rivets and w >= 5 and h >= 5 and (x in (1, w - 2)) and (y in (1, h - 2)):
            k *= 1.3
        return shade(base, k)
    return paint


def tank(base, seed=2):
    """Edge-darkened faces read as a rounded cylinder; orange band + stencil on the outer face."""
    flat = plate(base, seams=False, rivets=False, seed=seed)

    def paint(x, y, w, h, face):
        if face in ("up", "down"):
            return flat(x, y, w, h, face)
        t = abs((x + 0.5) / w - 0.5) * 2      # 0 centre -> 1 edge
        k = 1.12 - 0.45 * t * t + noise(x, y, seed) * 0.06
        c = base
        if face == "south" and h > 8:
            if y in (2, 3):
                c = ORANGE
            elif 5 <= y <= 6 and 1 <= x <= w - 2:
                c = (40, 40, 44) if (x + y) % 2 else (212, 200, 60)   # hazard tick marks
        if y == 0:
            k *= 1.15
        if y == h - 1:
            k *= 0.7
        return shade(c, k)
    return paint


def core(seed=3):
    base = plate(ARMOR, seed=seed)

    def paint(x, y, w, h, face):
        if face == "south":
            if 2 <= y <= h - 4 and 2 <= x <= w - 3:
                return shade(GUNMETAL, 0.55 if y % 2 else 1.05)   # intake grille
            if y == h - 2 and 1 <= x <= w - 2:
                return ORANGE
        return base(x, y, w, h, face)
    return paint


def bell(seed=4):
    """Nozzle metal with heat bluing toward the exhaust; bottom face is the glowing throat."""
    def paint(x, y, w, h, face):
        if face == "down":
            cx, cy = (w - 1) / 2, (h - 1) / 2
            r = max(abs(x - cx), abs(y - cy)) / max(cx, 1)
            if r > 0.85:
                return shade(STEEL, 0.55)
            if r > 0.55:
                return (255, 120, 30)
            return (255, 236, 170)
        t = y / max(h - 1, 1)
        c = mix(STEEL, (92, 84, 120), t * 0.6)                    # bluing
        k = 1.05 - 0.3 * abs((x + 0.5) / w - 0.5) * 2 + noise(x, y, seed) * 0.08
        if y == h - 1:
            c, k = (150, 90, 60), 1.0                            # scorched lip
        return shade(c, k)
    return paint


def solid(c, seed=5):
    return lambda x, y, w, h, face: shade(c, 1.0 + noise(x, y, seed) * 0.1)


# --- geometry ----------------------------------------------------------------
# (bone, origin, size, painter key)
def mirror(cube):
    bone, (ox, oy, oz), size, key = cube
    bone = {"nozzle_left": "nozzle_right"}.get(bone, bone)
    return (bone, (-ox - size[0], oy, oz), size, key)


# Titanfall-style jump kit: reactor spine between two armoured thruster nacelles with swept winglets,
# stabiliser fins and big vectoring bells (nozzle bones are what the layer gimbals).
LEFT = [
    ("docking_mount", (5, -1, 2), (6, 12, 6), "tank"),          # thruster nacelle
    ("docking_mount", (4, 2, 1), (8, 1, 8), "band"),
    ("docking_mount", (4, 8, 1), (8, 1, 8), "band"),
    ("docking_mount", (6, 11, 3), (4, 2, 4), "dome"),           # nacelle cap
    ("docking_mount", (11, 0, 3), (1, 10, 4), "rcs"),           # outer armour skin
    ("docking_mount", (12, 6, 3), (5, 1, 4), "dome"),           # swept winglet
    ("docking_mount", (16, 4, 3), (1, 3, 4), "orange"),         # winglet tip
    ("docking_mount", (8, 13, 4), (1, 4, 3), "gunmetal"),       # stabiliser fin
    ("docking_mount", (6, 5, 8), (4, 2, 1), "glow"),            # intake light
    ("docking_mount", (12, 1, 4), (2, 2, 2), "rcs"),            # RCS jet
    ("docking_mount", (14, 1, 5), (1, 1, 1), "orange"),
    ("docking_mount", (5, -3, 2), (6, 2, 6), "collar"),
    ("nozzle_left", (6, -5, 3), (4, 2, 4), "throat"),
    ("nozzle_left", (5, -7, 2), (6, 2, 6), "bell"),
    ("nozzle_left", (4, -9, 1), (8, 2, 8), "bell"),
]
CENTRE = [
    ("docking_mount", (-8, -5, 0), (16, 16, 2), "harness"),
    ("docking_mount", (-4, -2, 2), (8, 13, 5), "core"),         # reactor spine
    ("docking_mount", (-3, 11, 2), (6, 2, 4), "cap"),
    ("docking_mount", (-2, 0, 7), (4, 8, 1), "glow"),           # reactor vent glow
    ("docking_mount", (-4, 2, 7), (8, 1, 1), "gunmetal"),       # cooling fins
    ("docking_mount", (-4, 5, 7), (8, 1, 1), "gunmetal"),
    ("docking_mount", (-4, 8, 7), (8, 1, 1), "gunmetal"),
    ("docking_mount", (-5, 9, 3), (10, 2, 2), "band"),          # fuel crossfeed
    ("docking_mount", (-1, -5, 2), (2, 3, 2), "collar"),
    ("docking_mount", (-1, 13, 3), (1, 3, 1), "gunmetal"),      # antenna
    ("docking_mount", (-1, 16, 3), (1, 1, 1), "red"),
]
CUBES = CENTRE + LEFT + [mirror(c) for c in LEFT]

PAINTERS = {
    "tank": tank(ARMOR), "band": plate(GUNMETAL, seams=False, rivets=False), "dome": plate(ARMOR, seams=False, rivets=False),
    "collar": plate(GUNMETAL, seams=False), "rcs": plate(GUNMETAL), "throat": plate(STEEL, seams=False, rivets=False),
    "bell": bell(), "harness": plate(GUNMETAL), "core": core(), "cap": plate(GUNMETAL),
    "orange": solid(ORANGE), "gunmetal": solid(GUNMETAL), "red": solid(RED), "glow": solid((90, 230, 255)),
}

# --- box-UV shelf packing (cubes with the same size + painter share a region) --
pixels = bytearray(W * H * 4)
uv_of, shelf_x, shelf_y, shelf_h = {}, 0, 0, 0


def put(px, py, rgb):
    i = (py * W + px) * 4
    pixels[i:i + 4] = bytes((*rgb, 255))


def paint_box(u, v, size, painter):
    w, h, d = size
    faces = {  # Bedrock box UV layout
        "up": (u + d, v, w, d), "down": (u + d + w, v, w, d),
        "east": (u, v + d, d, h), "north": (u + d, v + d, w, h),
        "west": (u + d + w, v + d, d, h), "south": (u + 2 * d + w, v + d, w, h),
    }
    for face, (fu, fv, fw, fh) in faces.items():
        for y in range(fh):
            for x in range(fw):
                put(fu + x, fv + y, painter(x, y, fw, fh, face))


for _, _, size, key in CUBES:
    if (size, key) in uv_of:
        continue
    w, h, d = size
    bw, bh = 2 * (w + d), d + h
    if shelf_x + bw > W:
        shelf_x, shelf_y, shelf_h = 0, shelf_y + shelf_h, 0
    assert shelf_y + bh <= H, "texture full"
    uv_of[(size, key)] = (shelf_x, shelf_y)
    paint_box(shelf_x, shelf_y, size, PAINTERS[key])
    shelf_x += bw
    shelf_h = max(shelf_h, bh)

# --- write geo ---------------------------------------------------------------
pivots = {"root": None, "docking_mount": "root", "nozzle_left": "docking_mount", "nozzle_right": "docking_mount"}
bone_pivot = {"root": [0, 0, 0], "docking_mount": [0, 0, 0], "nozzle_left": [8, -4, 5], "nozzle_right": [-8, -4, 5]}
bones = []
for name, parent in pivots.items():
    b = {"name": name, "pivot": bone_pivot[name]}
    if parent:
        b["parent"] = parent
    cubes = [{"origin": list(o), "size": list(s), "uv": list(uv_of[(s, k)])} for bn, o, s, k in CUBES if bn == name]
    if cubes:
        b["cubes"] = cubes
    bones.append(b)

geo = {"format_version": "1.12.0", "minecraft:geometry": [{
    "description": {"identifier": "geometry.flight_module_rocket_jetpack", "texture_width": W, "texture_height": H,
                    "visible_bounds_width": 5, "visible_bounds_height": 5, "visible_bounds_offset": [0, 1, 0]},
    "bones": bones}]}
with open(f"{ROOT}/geo/flight/rocket_jetpack.geo.json", "w") as f:
    json.dump(geo, f, indent=2)


def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)


raw = b"".join(b"\0" + bytes(pixels[y * W * 4:(y + 1) * W * 4]) for y in range(H))
with open(f"{ROOT}/textures/entity/flight/rocket_jetpack.png", "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
print(f"{len(CUBES)} cubes, texture rows used: {shelf_y + shelf_h}/{H}")
