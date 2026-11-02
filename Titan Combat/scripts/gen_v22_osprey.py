#!/usr/bin/env python3
"""V-22 Osprey tiltrotor: geo + animation + entity texture + item icon + preview render.

Model space follows the rest of the mod (GeckoLib/Blockbench): nose at -Z, +Y up.
Java's PILOT_SEAT_OFFSET z=+74/16 is entity space; the renderer's 180-degree turn puts it at model z=-74.
Run: python3 scripts/gen_v22_osprey.py [--preview out.png]
"""
import json, math, os, random, sys

sys.path.insert(0, os.path.dirname(__file__))
from generate_transport_assets import make_png, rod

ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources", "assets", "titancombat")
TEX = 512

# ---------------------------------------------------------------- materials (64x64 atlas cells)
(HULL, BELLY, GLASS, DARK, BLADE, WALK, TIRE, SPIN, MARK, SOOT, GRILLE, RED, GREEN, WINDOW, INTER, RAMP,
 DOOR, WHITE, TIP, STAR, MARK_R) = range(21)  # MARK_R: stencil drawn mirrored for the side whose face UV runs backwards


def cell(m):
    return (m % 8) * 64, (m // 8) * 64


# ---------------------------------------------------------------- geometry helpers
def box(x0, y0, z0, x1, y1, z1, mat=HULL, **faces):
    return {"origin": [round(min(x0, x1), 3), round(min(y0, y1), 3), round(min(z0, z1), 3)],
            "size": [round(abs(x1 - x0), 3), round(abs(y1 - y0), 3), round(abs(z1 - z0), 3)], "mat": mat, "faces": faces}


def cbox(cx, cy, cz, sx, sy, sz, mat=HULL, **faces):
    return box(cx - sx / 2, cy - sy / 2, cz - sz / 2, cx + sx / 2, cy + sy / 2, cz + sz / 2, mat, **faces)


def stick(a, b, w, t, mat=DARK):
    c = rod(a, b, w, t, [0, 0])
    c.pop("uv")
    c["mat"], c["faces"] = mat, {}
    return c


def section(z0, z1, hw, yb, yt, c=2.5, mat=HULL, **faces):
    """Fuselage slice with chamfered corners: core plus narrower top and bottom bands (octagonal look)."""
    faces.setdefault("down", BELLY)
    return [box(-hw, yb + c, z0, hw, yt - c, z1, mat, **faces),
            box(-hw + c, yt - c, z0, hw - c, yt, z1, mat, **{k: v for k, v in faces.items() if k != "down"}),
            box(-hw + c, yb, z0, hw - c, yb + c, z1, mat, **faces)]


def prism_y(cx, cz, y0, y1, r, mat, c=None, **faces):
    """Octagonal prism along Y (nacelles, spinners)."""
    c = r * 0.38 if c is None else c
    return [box(cx - r, y0, cz - r + c, cx + r, y1, cz + r - c, mat, **faces),
            box(cx - r + c, y0, cz - r, cx + r - c, y1, cz + r, mat, **faces)]


def wheel(cx, cy, cz, w, r):
    """Tyre: three square slabs turned about the axle (X) - reads round."""
    out = []
    for a in (0, 30, 60):
        c = cbox(cx, cy, cz, w, r * 1.8, r * 1.8, TIRE)
        c["pivot"], c["rotation"] = [cx, cy, cz], [a, 0, 0]
        out.append(c)
    out.append(cbox(cx + (0.15 if cx > 0 else -0.15), cy, cz, w, r * 0.9, r * 0.9, DARK))
    return out


# ---------------------------------------------------------------- model
def build():
    fus, wings, tail, gear, ramp, straps, cockpit = [], [], [], [], [], [], []

    # nose -> tail profile: (z0, z1, half width, bottom, top)
    for z0, z1, hw, yb, yt in [(-101, -98, 3.5, 15, 21), (-98, -95, 6, 12.5, 23.5), (-95, -91, 8.5, 10.5, 25),
                               (-91, -87, 10.5, 9, 26), (-87, -64, 12.5, 7.5, 22.5)]:
        fus += section(z0, z1, hw, yb, yt, c=2 if hw > 6 else 1.2, up=INTER if z0 == -87 else HULL)
    fus += section(-64, -50, 13.5, 6, 34.5, c=3)          # forward cabin
    fus += section(-50, 40, 14, 6, 35, c=3)               # main cabin
    for i, (z0, z1, hw, yb, yt) in enumerate([(40, 46, 13.6, 8, 35), (46, 52, 13, 11, 34.5), (52, 58, 12.2, 14, 34),
                                              (58, 64, 11.2, 17, 33.5), (64, 71, 10, 20, 33), (71, 78, 8.5, 22.5, 32.5),
                                              (78, 85, 6.8, 24.5, 32), (85, 91, 5, 26, 31.5), (91, 95, 3, 27, 30.5)]):
        fus += section(z0, z1, hw, yb, yt, c=2.5 if hw > 6 else 1.2)
    # cockpit glazing frame: windscreen sill, A-pillars, centre post, side posts, roof
    cockpit += [box(-12, 22.5, -88, 12, 23.5, -86, DARK)]
    for s in (-1, 1):
        cockpit += [stick((s * 11.5, 22.5, -87), (s * 12.5, 33, -78), 1.4, 1.4),
                    stick((s * 12.6, 22.5, -74.5), (s * 13.2, 33.5, -73), 1.2, 1.2),
                    box(s * 12.5, 22.5, -66, s * 13.5, 34, -64, HULL),
                    box(s * 12.4, 31.5, -78, s * 13.2, 33, -64, DARK)]       # upper side frame / eyebrow
    cockpit += [stick((0, 22.5, -87.5), (0, 32.5, -79), 1, 1),
                box(-12.5, 32.5, -79, 12.5, 34.5, -64, HULL),
                box(-10, 23.5, -85, 10, 26.5, -82, INTER),                 # instrument panel
                box(-10, 26.5, -84, 10, 27.5, -81, DARK),                  # glare shield
                box(-3, 22.5, -76, 3, 23.5, -70, DARK), box(-3, 23.5, -70, 3, 31, -68.5, DARK),  # pilot seat
                box(-8, 22.5, -78, -4, 26, -76, INTER), box(4, 22.5, -78, 8, 26, -76, INTER),     # side consoles
                box(-12.5, 22.5, -64.5, 12.5, 32.5, -63.5, INTER)]           # cockpit rear bulkhead
    # chin, FLIR ball, pitot tubes, refuelling probe (starboard = -X)
    fus += [box(-8, 6.5, -92, 8, 9.5, -76, BELLY), box(-6, 7.5, -95, 6, 10.5, -92, BELLY),
            cbox(0, 9, -97, 3.5, 3.5, 3.5, DARK), cbox(0, 9, -97.4, 2, 2, 3, GLASS)]
    for s in (-1, 1):
        fus += [stick((s * 6, 18, -96), (s * 6, 18, -104), 0.6, 0.6)]
    fus += [stick((-9.5, 25, -82), (-7.5, 26.5, -116), 1.8, 1.8, HULL), cbox(-7.5, 26.5, -117, 1.4, 1.4, 2.5, DARK),
            box(-11, 23, -86, -8, 27, -78, HULL)]
    # dorsal wing fairing + engine-crossshaft hump, antennas, beacon
    fus += [box(-15.5, 34.5, -30, 15.5, 37.5, 30), box(-11, 37.5, -24, 11, 40.5, 24), box(-7, 40.5, -18, 7, 42, 14),
            cbox(0, 42.5, 10, 1.5, 1, 1.5, RED), stick((0, 35, 34), (0, 40, 40), 0.6, 2.5),
            stick((0, 34.5, -44), (0, 38, -48), 0.5, 2), box(-2, 4.5, -30, 2, 6, -26, DARK)]
    # sponsons with main gear fairings
    for s in (-1, 1):
        fus += [box(s * 13, 5, -24, s * 21.5, 15, 30), box(s * 13, 15, -20, s * 19, 17.5, 26),
                box(s * 13, 6, -30, s * 18.5, 13.5, -24), box(s * 13, 7.5, 30, s * 18, 13, 36),
                box(s * 21.5, 9, -14, s * 22, 13, 18, DARK),                      # gear-door seam
                box(s * 14, 26, -40, s * 14.6 if s > 0 else -14.6, 28, -38, WHITE)]  # formation light
        for z in (-36, -20, -4, 12, 28):                                         # cabin windows
            fus += [box(s * 14, 25, z, s * 14.5, 29, z + 4, WINDOW)]
        fus += [box(s * 14, 18, 2, s * 14.25, 23, 34, HULL, east=MARK_R if s > 0 else MARK, west=MARK if s > 0 else MARK_R),  # MARINES stencil
                box(s * 13.6, 15, 48, s * 14.0, 22, 55, HULL, east=STAR, west=STAR)]
    fus += [box(-14.5, 8, -60, -14, 30, -48, DOOR)]                           # starboard crew door
    # rear ramp + hinge + upper cargo door line
    ramp += [stick((0, 6.5, 40), (0, 18.5, 64), 25, 1.2, RAMP), box(-12, 6, 39, 12, 7.5, 41, DARK),
             box(-11, 18, 63.5, 11, 19, 65, DARK)]
    # landing gear (main: twin wheels under sponsons, nose: twin wheels)
    for s in (-1, 1):
        gear += [stick((s * 17.5, 3.5, 2), (s * 17.5, 9, 2), 1.5, 1.5), stick((s * 17.5, 5, 6), (s * 17.5, 9, -2), 0.8, 0.8)]
        gear += wheel(s * 15.8, 3.5, 2, 2.2, 3.5) + wheel(s * 19.2, 3.5, 2, 2.2, 3.5)
    gear += [stick((0, 3, -82), (0, 9, -82), 1.4, 1.4), stick((0, 4, -82), (0, 8, -78), 0.7, 0.7)]
    gear += wheel(-1.6, 3, -82, 1.8, 3) + wheel(1.6, 3, -82, 1.8, 3)
    # wing: high-mounted, slight forward sweep implied by stepped leading edge, flaperons, walkway
    wings += [box(-70, 35.5, -12, 70, 39, 12, HULL, up=HULL), box(-70, 36, -15, 70, 38.5, -12),
              box(-14, 39, -8, 14, 39.2, 6, WALK)]
    for s in (-1, 1):
        for x0 in (16, 34, 52):
            wings += [box(s * x0, 36.2, 12, s * (x0 + 16.5), 37.6, 17, BELLY)]
        wings += [box(s * 66, 34.5, -13, s * 70, 40, 13, HULL), cbox(s * 69, 37.5, -15.5, 1.5, 1.2, 1, GREEN if s > 0 else RED)]
    # H-tail with twin vertical fins and rudders
    tail += [box(-29, 30.5, 76, 29, 32.5, 89), box(-27, 31, 89, 27, 32, 92, BELLY)]
    for s in (-1, 1):
        x0, x1 = s * 26.5, s * 29.5
        tail += [box(x0, 21, 78, x1, 30.5, 90), box(x0, 32.5, 74, x1, 41, 90), box(x0, 41, 77, x1, 47, 90),
                 box(x0, 47, 80, x1, 52, 90), box(s * 27, 22, 90, s * 29, 51, 93, BELLY),
                 cbox(s * 28, 52.5, 85, 2, 1, 6, DARK), cbox(s * 28, 20.5, 84, 2, 1, 6, DARK)]

    def nacelle(s):
        c = s * 74
        n = []
        n += prism_y(c, 0, 26, 30, 5.5, DARK, down=SOOT)       # exhaust end
        n += prism_y(c, 0, 30, 57, 7.5, HULL)                   # engine pod
        n += prism_y(c, 0, 57, 61, 6.2, HULL)
        n += prism_y(c, 0, 61, 63.5, 4.5, DARK)                 # swashplate collar
        n += [box(c + s * 7.5, 44, -3.5, c + s * 8.2, 53, 3.5, GRILLE),   # intake
              box(c - 6, 46, -7.5, c + 6, 47, 7.5, DARK),                # cowl seam
              box(c - 4, 30.5, 7.5, c + 4, 54, 8, BELLY),                 # access strip
              box(c + s * 3, 26, -2, c + s * 6, 32, 2, SOOT)]             # IR suppressor
        return n

    def rotor(s):
        c, hy = s * 74, 66.5
        r = []
        for y0, y1, rr in [(63.5, 66, 5.5), (66, 68.5, 4.8), (68.5, 70.5, 3.6), (70.5, 72, 2.4), (72, 73, 1.2)]:
            r += prism_y(c, 0, y0, y1, rr, SPIN)
        for a in (0, 120, 240):
            for z0, z1, w, mat in [(4, 10, 3.5, DARK), (10, 36, 6, BLADE), (36, 52, 5, BLADE), (52, 58, 4.2, TIP)]:
                b = box(c - w / 2, hy, z0, c + w / 2, hy + (1.4 if mat == DARK else 0.8), z1, mat)
                b["pivot"], b["rotation"] = [c, hy, 0], [0, a + s * 15, 0]
                r.append(b)
        return r

    straps = [box(-2, 3, -2, 2, 5, 2, DARK)] + [stick((0, 4, 0), (sx * 9, -6, sz * 9), 1.2, 0.6, RAMP)
                                                for sx in (-1, 1) for sz in (-1, 1)]

    bones = [
        {"name": "root", "pivot": [0, 0, 0]},
        {"name": "fuselage", "parent": "root", "pivot": [0, 20, 0], "cubes": fus},
        {"name": "cockpit", "parent": "fuselage", "pivot": [0, 22, -74], "cubes": cockpit},
        {"name": "ramp", "parent": "fuselage", "pivot": [0, 7, 40], "cubes": ramp},
        {"name": "landing_gear", "parent": "fuselage", "pivot": [0, 6, 0], "cubes": gear},
        {"name": "tail", "parent": "fuselage", "pivot": [0, 31, 80], "cubes": tail},
        {"name": "wings", "parent": "fuselage", "pivot": [0, 37, 0], "cubes": wings},
        {"name": "left_nacelle", "parent": "wings", "pivot": [74, 38, 0], "cubes": nacelle(1)},
        {"name": "left_rotor", "parent": "left_nacelle", "pivot": [74, 66.5, 0], "cubes": rotor(1)},
        {"name": "right_nacelle", "parent": "wings", "pivot": [-74, 38, 0], "cubes": nacelle(-1)},
        {"name": "right_rotor", "parent": "right_nacelle", "pivot": [-74, 66.5, 0], "cubes": rotor(-1)},
        {"name": "cargo_straps", "parent": "fuselage", "pivot": [0, 4, 0], "cubes": straps},
    ]
    return bones


def assign_uv(bones):
    """Every face samples its own material cell (1 texel/unit, cropped to the cell), offset per cube for variety."""
    rnd = random.Random(7)
    for b in bones:
        for c in b.get("cubes", []):
            mat, faces = c.pop("mat"), c.pop("faces")
            sx, sy, sz = c["size"]
            dims = {"north": (sx, sy), "south": (sx, sy), "east": (sz, sy), "west": (sz, sy), "up": (sx, sz), "down": (sx, sz)}
            uv = {}
            for f, (w, h) in dims.items():
                m = faces.get(f, mat)
                u0, v0 = cell(m)
                w, h = min(max(w, 1), 64), min(max(h, 1), 64)
                fixed = m in (MARK, MARK_R, STAR, TIP, BLADE, DOOR, WINDOW, GRILLE, INTER)
                du = 0 if fixed else rnd.randint(0, int(64 - w))
                dv = 0 if fixed else rnd.randint(0, int(64 - h))
                uv[f] = {"uv": [u0 + du, v0 + dv], "uv_size": [round(w, 3), round(h, 3)]}
            c["uv"] = uv
    return bones


# ---------------------------------------------------------------- texture
FONT = {"M": ["101", "111", "101", "101", "101"], "A": ["010", "101", "111", "101", "101"],
        "R": ["110", "101", "110", "101", "101"], "I": ["111", "010", "010", "010", "111"],
        "N": ["101", "111", "111", "111", "101"], "E": ["111", "100", "110", "100", "111"],
        "S": ["011", "100", "010", "001", "110"]}


def paint_texture():
    rnd = random.Random(22)
    px = [[(0, 0, 0, 0)] * TEX for _ in range(TEX)]

    def put(x, y, c):
        if 0 <= x < TEX and 0 <= y < TEX:
            px[y][x] = tuple(max(0, min(255, int(v))) for v in c[:3]) + ((c[3] if len(c) > 3 else 255),)

    def skin(m, base, lines=16, rivets=True, grime=1.0):
        u0, v0 = cell(m)
        for y in range(64):
            for x in range(64):
                n = rnd.uniform(-4, 4) - grime * 8 * (y / 63) ** 2           # grime gathers low
                if (x * 7 + y * 3) % 23 == 0: n -= 3 * grime                  # streaks
                c = [b + n for b in base]
                if x % lines == 0 or y % lines == 0:
                    c = [b - 24 for b in c]
                elif rivets and ((x % lines == 2 and y % 4 == 0) or (y % lines == 2 and x % 4 == 0)):
                    c = [b - 14 for b in c]
                elif x % lines == 1 or y % lines == 1:
                    c = [b + 10 for b in c]                                    # panel edge highlight
                put(u0 + x, v0 + y, c)

    G = (182, 186, 189)
    skin(HULL, G); skin(BELLY, (158, 161, 163), grime=1.8); skin(RAMP, (165, 168, 170), lines=8)
    skin(DOOR, G); skin(MARK, G, rivets=False); skin(MARK_R, G, rivets=False); skin(STAR, G, rivets=False); skin(SPIN, (168, 171, 174), lines=32, rivets=False)
    skin(DARK, (78, 80, 84), lines=32, grime=0.4); skin(WALK, (66, 68, 70), lines=64, rivets=False, grime=0)
    skin(BLADE, (104, 107, 110), lines=64, rivets=False, grime=0); skin(TIP, (104, 107, 110), lines=64, rivets=False, grime=0)
    for (m, col) in ((RED, (200, 40, 36)), (GREEN, (40, 190, 70)), (WHITE, (235, 238, 240))):
        a, b = cell(m)
        for y in range(64):
            for x in range(64):
                put(a + x, b + y, [v + rnd.uniform(-8, 8) for v in col])
    a, b = cell(TIRE)
    for y in range(64):
        for x in range(64):
            put(a + x, b + y, (40 - 10 * ((x + y) % 4 < 2), 40 - 10 * ((x + y) % 4 < 2), 42 - 10 * ((x + y) % 4 < 2)))
    a, b = cell(SOOT)
    for y in range(64):
        for x in range(64):
            put(a + x, b + y, [26 + rnd.uniform(0, 14) + 30 * (abs(x % 8 - 4) > 2)] * 3)
    a, b = cell(GRILLE)
    for y in range(64):
        for x in range(64):
            put(a + x, b + y, (34, 35, 37) if y % 2 else (96, 98, 100))
    a, b = cell(WINDOW)
    for y in range(64):
        for x in range(64):
            c = (40, 52, 64) if 0 < x < 3 or 0 < y < 3 else (62, 78, 92)
            if x == 0 or y == 0 or x == 3 or y == 3 and x < 4: c = (60, 62, 64)
            if (x + y) % 9 == 1: c = (120, 140, 156)
            put(a + x, b + y, c)
    a, b = cell(INTER)
    for y in range(64):
        for x in range(64):
            c = (48, 50, 52)
            if x % 5 in (1, 2) and y % 4 == 1: c = (20, 24, 22) if (x + y) % 3 else (70, 200, 110)  # MFD screens
            put(a + x, b + y, c)
    a, b = cell(TIP)                                                           # blade tip bands
    for y in range(64):
        for x in range(64):
            if x < 4 or y < 4: put(a + x, b + y, (214, 196, 70) if (x < 2 or y < 2) else (210, 212, 214))
    a, b = cell(DOOR)                                                          # door outline + handle
    for y in range(22):
        for x in range(12):
            if x == 0 or y == 0 or x == 11 or y == 21: put(a + x, b + y, (90, 92, 95))
    for x in range(3, 6): put(a + x, b + 11, (60, 60, 62))
    a, b = cell(MARK)                                                          # "MARINES" low-vis stencil
    for i, ch in enumerate("MARINES"):
        for r, row in enumerate(FONT[ch]):
            for k, bit in enumerate(row):
                if bit == "1":
                    put(a + 2 + i * 4 + k, b + 1 + r, (98, 101, 104))
                    ar, br = cell(MARK_R)
                    put(ar + 63 - (2 + i * 4 + k), br + 1 + r, (98, 101, 104))
    a, b = cell(STAR)                                                          # low-vis national insignia
    for y in range(7):
        for x in range(7):
            d = math.hypot(x - 3, y - 3)
            if 2.6 < d < 3.6 or (abs(x - 3) <= (1 if y < 3 else 2 if y < 5 else 3) and y in (2, 3, 4) or x == 3 and y < 3):
                put(a + x, b + y, (100, 103, 106))
    return px


def save_png(path, px):
    w, h = len(px[0]), len(px)
    raw = bytearray()
    for row in px:
        for c in row: raw.extend(c)
    with open(path, "wb") as f:
        f.write(make_png(w, h, bytes(raw)))


def item_icon():
    """16x16 top-down plan view: fuselage, high wing, two rotor discs, H-tail."""
    T, O, L, D, R = (0, 0, 0, 0), (48, 50, 54, 255), (186, 190, 193, 255), (120, 124, 128, 255), (150, 154, 158, 150)
    g = [[T] * 16 for _ in range(16)]
    for cx in (2, 13):                                    # rotor discs (blurred)
        for y in range(16):
            for x in range(16):
                d = math.hypot(x - cx, y - 5)
                if d <= 2.6: g[y][x] = R
    for x in range(1, 15): g[5][x] = L; g[6][x] = D       # wing
    for cx in (2, 13): g[4][cx] = O; g[5][cx] = O; g[6][cx] = O; g[7][cx] = O   # nacelles
    for y in range(1, 14):                                # fuselage
        g[y][7] = L; g[y][8] = L
        if 2 < y < 12: g[y][6] = O; g[y][9] = O
    g[1][7] = g[1][8] = O; g[2][7] = (60, 90, 110, 255); g[2][8] = (60, 90, 110, 255)  # nose + cockpit glass
    for x in range(4, 12): g[13][x] = D                   # H-tail
    g[12][4] = g[13][4] = g[14][4] = O; g[12][11] = g[13][11] = g[14][11] = O
    g[14][7] = g[14][8] = O
    return g


# ---------------------------------------------------------------- animation
def animations():
    spin = lambda s: {"rotation": {"0.0": [0, 0, 0], "0.2": [0, s * 360, 0]}}
    return {"format_version": "1.8.0", "animations": {
        "animation.v22_osprey.idle": {"loop": True, "bones": {
            "left_nacelle": {"rotation": [0, 0, 0]}, "right_nacelle": {"rotation": [0, 0, 0]},
            "left_rotor": {"rotation": [0, 0, 0]}, "right_rotor": {"rotation": [0, 0, 0]}}},
        "animation.v22_osprey.fly": {"loop": True, "animation_length": 0.2, "bones": {
            "left_nacelle": {"rotation": [0, 0, 0]}, "right_nacelle": {"rotation": [0, 0, 0]},
            "left_rotor": spin(1), "right_rotor": spin(-1)}},
        "animation.v22_osprey.cruise": {"loop": True, "animation_length": 0.2, "bones": {
            # +X keyframe pitches the nacelle top toward -Z (the nose): airplane mode
            "left_nacelle": {"rotation": [88, 0, 0]}, "right_nacelle": {"rotation": [88, 0, 0]},
            "left_rotor": spin(1), "right_rotor": spin(-1)}}}}


# ---------------------------------------------------------------- preview rasterizer (pure python)
def rot(v, r):
    """GeckoLib order: X (negated), then Y (negated), then Z."""
    x, y, z = v
    a = math.radians(-r[0]); y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
    a = math.radians(-r[1]); x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
    a = math.radians(r[2]); x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
    return (x, y, z)


def about(p, piv, r):
    q = rot([p[i] - piv[i] for i in range(3)], r)
    return [q[i] + piv[i] for i in range(3)]


FACES = {  # corner order (u0v0, u1v0, u1v1, u0v1) as (x,y,z) unit picks, outward normal
    "north": ([(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0)]), "south": ([(0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)]),
    "east": ([(1, 1, 1), (1, 1, 0), (1, 0, 0), (1, 0, 1)]), "west": ([(0, 1, 0), (0, 1, 1), (0, 0, 1), (0, 0, 0)]),
    "up": ([(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)]), "down": ([(0, 0, 1), (1, 0, 1), (1, 0, 0), (0, 0, 0)])}


def render(bones, tex, pose, yaw, pitch, W=640, H=420, scale=2.3):
    by = {b["name"]: b for b in bones}

    def chain(name):
        out = []
        while name:
            out.append(by[name]); name = by[name].get("parent")
        return out

    zbuf = [[1e9] * W for _ in range(H)]
    img = [[(222, 230, 238, 255)] * W for _ in range(H)]
    light = (0.4, 0.8, -0.45)
    for b in bones:
        if b["name"] == "cargo_straps": continue
        ch = chain(b["name"])
        for c in b.get("cubes", []):
            o, s = c["origin"], c["size"]
            for f, corners in FACES.items():
                pts = []
                for k in corners:
                    p = [o[i] + k[i] * s[i] for i in range(3)]
                    if "rotation" in c: p = about(p, c["pivot"], c["rotation"])
                    for bb in ch:
                        r = pose.get(bb["name"])
                        if r: p = about(p, bb["pivot"], r)
                    pts.append(p)
                e1 = [pts[1][i] - pts[0][i] for i in range(3)]; e2 = [pts[3][i] - pts[0][i] for i in range(3)]
                n = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]]
                ln = math.sqrt(sum(v * v for v in n)) or 1
                shade = 0.55 + 0.45 * abs(sum(n[i] * light[i] for i in range(3)) / ln)
                uv = c["uv"][f]; (u0, v0), (us, vs) = uv["uv"], uv["uv_size"]
                cam = []
                for p in pts:
                    x, y, z = p
                    a = math.radians(yaw); x, z = x * math.cos(a) - z * math.sin(a), x * math.sin(a) + z * math.cos(a)
                    a = math.radians(pitch); y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
                    cam.append((W / 2 + x * scale, H * 0.72 - y * scale, z))
                tuv = [(0, 0), (1, 0), (1, 1), (0, 1)]
                for tri in ((0, 1, 2), (0, 2, 3)):
                    A, B, C = (cam[i] for i in tri)
                    den = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1])
                    if abs(den) < 1e-9: continue
                    for py in range(max(0, int(min(A[1], B[1], C[1]))), min(H, int(max(A[1], B[1], C[1])) + 1)):
                        for qx in range(max(0, int(min(A[0], B[0], C[0]))), min(W, int(max(A[0], B[0], C[0])) + 1)):
                            w0 = ((B[1] - C[1]) * (qx - C[0]) + (C[0] - B[0]) * (py - C[1])) / den
                            w1 = ((C[1] - A[1]) * (qx - C[0]) + (A[0] - C[0]) * (py - C[1])) / den
                            w2 = 1 - w0 - w1
                            if w0 < 0 or w1 < 0 or w2 < 0: continue
                            z = w0 * A[2] + w1 * B[2] + w2 * C[2]
                            if z >= zbuf[py][qx]: continue
                            tu = sum(w * tuv[i][0] for w, i in zip((w0, w1, w2), tri))
                            tv = sum(w * tuv[i][1] for w, i in zip((w0, w1, w2), tri))
                            t = tex[min(TEX - 1, int(v0 + tv * vs * 0.999))][min(TEX - 1, int(u0 + tu * us * 0.999))]
                            if t[3] < 128: continue
                            zbuf[py][qx] = z
                            img[py][qx] = tuple(int(v * shade) for v in t[:3]) + (255,)
    return img


# ---------------------------------------------------------------- validation
def validate(geo, anim):
    g = geo["minecraft:geometry"][0]
    names = {b["name"] for b in g["bones"]}
    n = 0
    for b in g["bones"]:
        assert b.get("parent") in names | {None}, b["name"]
        for c in b.get("cubes", []):
            n += 1
            assert all(v > 0 for v in c["size"]), (b["name"], c)
            for f in c["uv"].values():
                assert 0 <= f["uv"][0] and f["uv"][0] + f["uv_size"][0] <= TEX and 0 <= f["uv"][1] and f["uv"][1] + f["uv_size"][1] <= TEX, c
    for a in anim["animations"].values():
        for bn in a["bones"]: assert bn in names, bn
    assert "cargo_straps" in names
    return n


def main():
    bones = assign_uv(build())
    xs = [v for b in bones for c in b.get("cubes", []) for v in (c["origin"][0], c["origin"][0] + c["size"][0])]
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{"description": {
        "identifier": "geometry.v22_osprey", "texture_width": TEX, "texture_height": TEX,
        # rotors sweep ~132 px each side of centre; height covers nacelles tilted or vertical
        "visible_bounds_width": 18, "visible_bounds_height": 9, "visible_bounds_offset": [0, 3, 0]},
        "bones": bones}]}
    anim = animations()
    cubes = validate(json.loads(json.dumps(geo)), anim)
    with open(os.path.join(ROOT, "geo", "v22_osprey.geo.json"), "w") as f: json.dump(geo, f, indent=1)
    with open(os.path.join(ROOT, "animations", "v22_osprey.animation.json"), "w") as f: json.dump(anim, f, indent=2)
    tex = paint_texture()
    save_png(os.path.join(ROOT, "textures", "entity", "transport", "v22_osprey.png"), tex)
    save_png(os.path.join(ROOT, "textures", "item", "v22_osprey.png"), item_icon())
    print(f"cubes={cubes} bones={[b['name'] for b in bones]} x-span={min(xs)}..{max(xs)}")
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        hover = render(bones, tex, {}, 35, -20)
        cruise = render(bones, tex, {"left_nacelle": [88, 0, 0], "right_nacelle": [88, 0, 0]}, -125, -20)
        save_png(out, hover + cruise)
        print("preview", out)


if __name__ == "__main__":
    main()
