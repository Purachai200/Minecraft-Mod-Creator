"""Shared helpers for the Vehicle Fleet generators. Reuses Titan Combat's cube helpers, atlas painter and software renderer.

Model space (GeckoLib): nose at -Z, +Y up, 16 px = 1 block, ground at y=0.
"""
import copy, math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Titan Combat", "scripts"))
import gen_v22_osprey as O  # noqa: E402
import gen_c130_hercules as H  # noqa: E402
from gen_v22_osprey import (box, cbox, stick, cell, save_png, render, about,  # noqa: E402,F401
                            HULL, BELLY, GLASS, DARK, BLADE, WALK, TIRE, SPIN, SOOT, GRILLE, RED, GREEN,
                            WINDOW, INTER, RAMP, DOOR, WHITE, TIP)

OUT = os.path.join(HERE, "..", "src", "main", "resources", "assets", "vehiclefleet")
DATA = os.path.join(HERE, "..", "src", "main", "resources", "data", "vehiclefleet")
ATLAS = 512      # painted atlas; written out at 2x (1024) with UVs doubled
PLATE = RAMP     # RAMP cell is repainted as diamond tread plate
LAMP = 22        # warm-white lamp panel; the only cell in the glow mask


def rbox(cx, cy, cz, sx, sy, sz, rot, mat=HULL, pivot=None, **faces):
    """Centered box turned by rot about pivot (default: its centre). Rotated cubes always carry a pivot."""
    c = cbox(cx, cy, cz, sx, sy, sz, mat, **faces)
    c["pivot"], c["rotation"] = list(pivot or [cx, cy, cz]), list(rot)
    return c


def tube(a, b, d=2.0, mat=DARK):
    return stick(a, b, d, d, mat)


def bone(name, parent, pivot, cubes, rotation=None, locators=None):
    b = {"name": name, "pivot": list(pivot), "cubes": cubes}
    if parent: b["parent"] = parent
    if rotation: b["rotation"] = list(rotation)
    if locators: b["locators"] = locators
    return b


def shift(cubes, dx=0, dy=0, dz=0):
    for c in cubes:
        c["origin"] = [round(c["origin"][0] + dx, 3), round(c["origin"][1] + dy, 3), round(c["origin"][2] + dz, 3)]
        if "pivot" in c: c["pivot"] = [round(c["pivot"][0] + dx, 3), round(c["pivot"][1] + dy, 3), round(c["pivot"][2] + dz, 3)]
    return cubes


def wall(s, x0, x1, y0, y1, z0, z1, mat=HULL):
    """Box on side s (+1 = left/+X) whose inward face shows the interior material."""
    return box(s * x0, y0, z0, s * x1, y1, z1, mat, **({"west": INTER} if s > 0 else {"east": INTER}))


def wheel12(cx, cy, cz, w, r, lugs=True, bolts=True):
    """Round wheel: 12-sided tyre (6 slabs, each end a flat), beadlock rim with bolts, staggered deep lug tread.
    Spin axis is X through (cx, cy, cz)."""
    a = r * math.cos(math.radians(15)); s = 2 * a * math.tan(math.radians(15))
    sg = 1 if cx > 0 else -1
    P = [cx, cy, cz]
    out = []
    for k in range(6):                                      # slightly different widths stop coplanar z-fighting
        c = cbox(cx, cy, cz, w - 0.02 * k, 2 * a, s, TIRE); c["pivot"], c["rotation"] = P, [30 * k, 0, 0]; out.append(c)
    if lugs:
        lh = max(1.2, r * 0.13)
        for row in (0, 1):
            for k in range(12):
                ang = 30 * k + 15 * row
                c = cbox(cx + (row - 0.5) * w * 0.5, cy + a + lh / 2 - 0.2, cz, w * 0.47, lh, s * 0.95, TIRE)
                c["pivot"], c["rotation"] = P, [ang, 0, 0]; out.append(c)
    rr = r * 0.58; ra = rr * math.cos(math.radians(15)); rs = 2 * ra * math.tan(math.radians(15))
    fx = cx + sg * (w / 2 - 0.1)
    for k in range(6):
        c = cbox(fx, cy, cz, 1.6 - 0.02 * k, 2 * ra, rs, DARK); c["pivot"], c["rotation"] = [fx, cy, cz], [30 * k, 0, 0]; out.append(c)
    if bolts:
        for k in range(12):
            c = cbox(fx + sg * 1.0, cy + rr * 0.86, cz, 0.8, 1.3, 1.3, SPIN)
            c["pivot"], c["rotation"] = [fx + sg * 1.0, cy, cz], [30 * k, 0, 0]; out.append(c)
    out.append(cbox(fx + sg * 1.0, cy, cz, 1.2, rr * 0.7, rr * 0.7, SPIN))      # hub cap
    return out


def dring(x, y, z, mat=SPIN):
    """Recessed D-ring tie-down: base plate + loop."""
    return [box(x - 1.6, y, z - 1.6, x + 1.6, y + 0.5, z + 1.6, DARK),
            box(x - 1.2, y + 0.5, z - 0.4, x - 0.6, y + 1.7, z + 0.4, mat),
            box(x + 0.6, y + 0.5, z - 0.4, x + 1.2, y + 1.7, z + 0.4, mat),
            box(x - 1.2, y + 1.7, z - 0.4, x + 1.2, y + 2.3, z + 0.4, mat)]


# ---------------------------------------------------------------- texture (512 atlas, 8x8 cells of 64; exported 2x)
def paint(hull, belly, plate=(150, 152, 150), rust=0.6, seed=1):
    """Weathered military paint: tinted HULL/BELLY/DOOR, rust drips + chipped edges, grit non-skid (WALK),
    diamond tread plate (RAMP), clear-ish glass with streaks."""
    px = O.paint_texture(); rnd = random.Random(seed)

    def put(x, y, c): px[y][x] = tuple(max(0, min(255, int(v))) for v in c[:3]) + (255,)

    def tint(m, rgb):
        a, b = cell(m)
        for y in range(64):
            for x in range(64):
                r, g, bb, _ = px[b + y][a + x]; l = (r + g + bb) / 3 / 182
                put(a + x, b + y, [v * l for v in rgb])

    for m in (HULL, DOOR): tint(m, hull)
    tint(BELLY, belly)
    for m in (HULL, DOOR, BELLY, DARK):                         # rust drips, chips and weld streaks
        a, b = cell(m)
        for _ in range(int(7 * rust) + 2):
            x, y0 = rnd.randrange(64), rnd.randrange(40)
            for y in range(y0, min(64, y0 + rnd.randint(8, 30))):
                t = (y - y0) / 30
                if rnd.random() < 0.8 - t * 0.5:
                    r, g, bb, _ = px[b + y][a + x]
                    k = 0.55 * rust
                    put(a + x, b + y, [r * (1 - k) + 132 * k, g * (1 - k) + 66 * k, bb * (1 - k) + 30 * k])
        for _ in range(int(40 * rust) + 8):
            x, y = rnd.randrange(64), rnd.randrange(64)
            if x < 3 or y < 3 or x > 60 or y > 60 or rnd.random() < 0.15:
                put(a + x, b + y, (150 + rnd.randint(-15, 15),) * 3 if rnd.random() < 0.5 else (104, 58, 34))
    a, b = cell(WALK)                                            # non-skid deck grit
    for y in range(64):
        for x in range(64):
            v = 62 + rnd.randint(-14, 16) + (10 if rnd.random() < 0.06 else 0)
            put(a + x, b + y, (v, v + 1, v + 3))
    for _ in range(40):
        x, y = rnd.randrange(64), rnd.randrange(64); put(a + x, b + y, (120, 76, 44))     # rust bloom
    a, b = cell(PLATE)                                           # diamond tread plate
    for y in range(64):
        for x in range(64):
            u, v = x % 8, y % 8
            lozenge = (abs(u - 3.5) + abs((v - 3.5) if (x // 8 + y // 8) % 2 else (v - 3.5) * 0.5)) < 3.2
            n = rnd.uniform(-5, 5)
            put(a + x, b + y, [c + n + (28 if lozenge else -14) for c in plate])
    a, b = cell(LAMP)                                            # lamp panel: warm white with a slightly brighter centre
    for y in range(64):
        for x in range(64):
            c = 255 - 0.12 * (abs(x - 32) + abs(y - 32)); put(a + x, b + y, (c, c * 0.95, c * 0.78))
    ga, gb = cell(GLASS)                                         # alpha-0 glass with a few streaks
    for y in range(64):
        for x in range(64):
            if x < 2 or y < 2 or x > 61 or y > 61: put(ga + x, gb + y, (70, 76, 84))
            elif (x + y) % 16 in (0, 1): px[gb + y][ga + x] = (150, 200, 230, 170)
            elif (x * 3 + y) % 11 == 0: px[gb + y][ga + x] = (110, 160, 190, 90)
    return px


def upscale2(px, seed=3):
    """1024 export: nearest 2x plus +-2 grain so panels do not look like blown-up 512."""
    rnd = random.Random(seed); out = []
    for row in px:
        r1, r2 = [], []
        for t in row:
            for r in (r1, r2):
                n = rnd.randint(-2, 2) if t[3] else 0
                r.extend(((min(255, max(0, t[0] + n)), min(255, max(0, t[1] + n)), min(255, max(0, t[2] + n)), t[3]),) * 2)
        out += [r1, r2]
    return out


def glowmask2(px):
    """1024 emissive mask for GeckoLib's AutoGlowingGeoLayer: only the LAMP cell is kept, everything else alpha 0."""
    a, b = cell(LAMP); out = []
    for y, row in enumerate(px):
        r = []
        for x, t in enumerate(row): r.append(t if (a <= x < a + 64 and b <= y < b + 64) else (0, 0, 0, 0))
        out += [r, r]
        out[-2] = [t for t in r for _ in (0, 1)]; out[-1] = out[-2]
    return out


def scale_uv(bones, k=2):
    for b in bones:
        for c in b.get("cubes", []):
            for f in c["uv"].values():
                f["uv"] = [f["uv"][0] * k, f["uv"][1] * k]; f["uv_size"] = [round(f["uv_size"][0] * k, 3), round(f["uv_size"][1] * k, 3)]
    return bones


def check(bones, anims=None):
    names = {b["name"] for b in bones}
    n = 0
    for b in bones:
        assert b.get("parent") in names | {None}, b["name"]
        for c in b.get("cubes", []):
            n += 1
            assert all(v > 0 for v in c["size"]), (b["name"], c)
            for f in c["uv"].values():
                assert 0 <= f["uv"][0] and f["uv"][0] + f["uv_size"][0] <= ATLAS and 0 <= f["uv"][1] and f["uv"][1] + f["uv_size"][1] <= ATLAS, c
    for a in (anims or {}).get("animations", {}).values():
        for bn in a["bones"]: assert bn in names, bn
    return n


def rest_pose(bones):
    return {b["name"]: b["rotation"] for b in bones if "rotation" in b}


def extents(bones):
    cs = [c for b in bones for c in b.get("cubes", [])]
    return [[round(min(c["origin"][i] for c in cs), 1), round(max(c["origin"][i] + c["size"][i] for c in cs), 1)] for i in range(3)]


def anim_file(name, clips):
    return {"format_version": "1.8.0", "animations": {f"animation.{name}.{k}": v for k, v in clips.items()}}


def spin(bones_axis, period=0.25):
    """Continuous spin clip entries. bones_axis: {bone: axis_index}."""
    out = {}
    for bn, ax in bones_axis.items():
        end = [0, 0, 0]; end[ax] = 360
        out[bn] = {"rotation": {"0.0": [0, 0, 0], str(period): end}}
    return out


# ---------------------------------------------------------------- preview rotation fix
def rot2(v, r):
    """GeckoLib bakes X and Y rotation negated and mirrors model X, so in the geo frame (as rod() assumes):
    +rx tips +Y toward -Z, +rz tips +Y toward +X, +ry turns +Z toward +X. Order X, Y, Z."""
    x, y, z = v
    a = math.radians(-r[0]); y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
    a = math.radians(r[1]); x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
    a = math.radians(-r[2]); x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
    return (x, y, z)


O.rot = rot2      # the stock preview rotates Z/Y the other way round; rod() and the game agree with rot2
