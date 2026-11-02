#!/usr/bin/env python3
"""Armored 8x8 APC (Stryker / Patria AMV / Boxer style): geo, animation, entity texture, item icon, preview.

Model space follows the hauler truck: nose at model -Z (= entity-local +Z in Java), +X = vehicle left (GeckoLib mirrors X).
Driver cushion top y14 at (x+10, z-38); commander at (x-10, z-38); troops at y14 inside the hollow hull.
Run: python3 scripts/gen_armored_apc.py [--preview out.png]
"""
import json
import math
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_transport_assets import TextureDrawer, make_png, rod, write_geo  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources", "assets", "titancombat")

# ---- 64px material cells (per_face_uv maps every face to its cell's top-left corner, 1 texel per unit) ----
ARMOR, ARMOR2, APPLIQUE, DECK, MUD, STEEL, SLAT, GRILLE = [[i * 64, 0] for i in range(8)]
TYRE, RIM, RUBBER, GLASS, LENS, TAIL, AMBER, OPTIC = [[i * 64, 64] for i in range(8)]
WOOD, STRAP, JERRY, BRASS, GUN, STENCIL, WELD, MUDARMOR = [[i * 64, 128] for i in range(8)]

BASE = (156, 160, 128)  # light NATO olive so a faction tint multiplies cleanly


def h(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0


def smooth(x, y, s, cell=6):
    gx, gy = x / cell, y / cell
    x0, y0 = int(gx), int(gy)
    fx, fy = gx - x0, gy - y0
    a, b = h(x0, y0, s), h(x0 + 1, y0, s)
    c, d = h(x0, y0 + 1, s), h(x0 + 1, y0 + 1, s)
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def paint_texture():
    t = TextureDrawer(512, 512)
    px = lambda x, y, c, a=255: t.set_pixel(x, y, c[0], c[1], c[2], a)
    add = lambda c, d: tuple(v + d for v in c)
    mix = lambda a, b, k: tuple(a[i] * (1 - k) + b[i] * k for i in range(3))

    def armor(u, v, base, seam=16, bolts=True, mud=0.0, s=1):
        for y in range(64):
            for x in range(64):
                c = add(base, (smooth(x, y, s) - 0.5) * 14 + (h(x, y, s + 9) - 0.5) * 6)
                streak = h(x, 0, s + 3)
                if streak > 0.8:  # rain grime streaks running down
                    c = add(c, -10 * (1 - y / 64) * (streak - 0.8) * 5)
                if h(x, y, s + 5) > 0.985:
                    c = add(c, 22)  # paint chips
                if mud:
                    m = smooth(x, y, s + 7, 4) + h(x, y, s + 8) * 0.3
                    if m > 1.0 - mud:
                        c = mix(c, (126, 108, 82), 0.85)
                if x == 0 or y == 0:
                    c = add(c, 16)  # lit outer edge on every face
                if seam:
                    lx, ly = x % seam, y % seam
                    if x and y and (lx == 0 or ly == 0):
                        c = add(c, -34)
                    elif x and y and (lx == 1 or ly == 1):
                        c = add(c, 10)
                    elif bolts and lx in (3, seam - 3) and ly in (3, seam - 3):
                        c = add(c, 34)
                    elif bolts and lx in (3, seam - 3) and ly in (4, seam - 2):
                        c = add(c, -28)
                px(u + x, v + y, c)

    armor(*ARMOR, BASE)
    armor(*ARMOR2, add(BASE, -4), seam=0, s=2)
    armor(*APPLIQUE, add(BASE, -8), seam=11, s=3)
    armor(*MUD, (128, 112, 86), seam=0, mud=0.6, s=4)
    armor(*MUDARMOR, BASE, seam=16, mud=0.35, s=5)
    armor(*WELD, BASE, seam=0, s=6)
    for i in range(64):  # weld beads along a few seams
        for k in (12, 31, 50):
            px(WELD[0] + i, WELD[1] + k, add(BASE, -18 + (i % 3) * 12))
            px(WELD[0] + k, WELD[1] + i, add(BASE, -18 + (i % 3) * 12))
    armor(*STENCIL, BASE, s=7)
    t.draw_text(STENCIL[0] + 3, STENCIL[1] + 4, "47", (232, 232, 220), 1)  # small hull number near the corner
    for y in range(64):
        for x in range(64):
            g = (h(x, y, 11) > 0.55) * 14 + (x % 4 == 0 and y % 4 == 0) * 10  # non-skid grit
            px(DECK[0] + x, DECK[1] + y, add(add(BASE, -16), g - 6 + (x == 0 or y == 0) * 12))
            px(STEEL[0] + x, STEEL[1] + y, add((86, 88, 82), (smooth(x, y, 12) - .5) * 14 + (x == 0 or y == 0) * 20))
            px(SLAT[0] + x, SLAT[1] + y, add(add(BASE, -22), (h(x, y, 13) - .5) * 10 + (h(x, y, 14) > .93) * 30))
            px(GRILLE[0] + x, GRILLE[1] + y, (40, 42, 38) if y % 2 else add(BASE, -30))
            tread = 52 if (y + (x // 4 % 2) * 2) % 4 < 2 else 30
            px(TYRE[0] + x, TYRE[1] + y, (tread, tread, tread - 2))
            px(RUBBER[0] + x, RUBBER[1] + y, add((40, 40, 38), (h(x, y, 15) - .5) * 8))
            t.set_pixel(GLASS[0] + x, GLASS[1] + y, 0, 0, 0, 0)  # see-through vision blocks
            px(LENS[0] + x, LENS[1] + y, (250, 246, 214) if (x + y) % 5 else (210, 210, 190))
            px(TAIL[0] + x, TAIL[1] + y, (196, 30, 26) if (x + y) % 4 else (150, 20, 18))
            px(AMBER[0] + x, AMBER[1] + y, (250, 170, 34))
            px(OPTIC[0] + x, OPTIC[1] + y, (30, 44, 70) if (x + y) % 6 else (110, 150, 190))
            px(WOOD[0] + x, WOOD[1] + y, add((138, 104, 66), (h(0, y, 16) - .5) * 20))
            px(STRAP[0] + x, STRAP[1] + y, add((96, 92, 64), ((x + y) % 3 == 0) * -14))
            px(JERRY[0] + x, JERRY[1] + y, add((112, 116, 84), (x % 6 == 0) * -18 + (x == 0 or y == 0) * 16))
            px(BRASS[0] + x, BRASS[1] + y, (176, 146, 70))
            px(GUN[0] + x, GUN[1] + y, add((40, 40, 42), (x == 0 or y == 0) * 22 + (h(x, y, 17) - .5) * 6))
            d = math.hypot(x - 9, y - 9)  # 18px rim disc: painted rim, lug-nut ring, dark hub
            rc = add(BASE, -14)
            if d < 3:
                rc = (60, 62, 58)
            elif 5 < d < 6.5 and int(math.degrees(math.atan2(y - 9, x - 9)) + 360) % 45 < 12:
                rc = (200, 200, 190)
            elif d > 8:
                rc = add(BASE, -40)
            px(RIM[0] + x, RIM[1] + y, rc)
    return t


# ---------------------------------------------------------------- geometry
def box(o, s, uv):
    return {"origin": list(o), "size": list(s), "uv": uv}


def mirror(c):
    """Same cube on the other side (X flipped)."""
    m = json.loads(json.dumps(c))
    m["origin"][0] = -(c["origin"][0] + c["size"][0])
    if "pivot" in m:
        m["pivot"][0] = -m["pivot"][0]
        m["rotation"] = [m["rotation"][0], -m["rotation"][1], -m["rotation"][2]]
    return m


def both(*cubes):
    return [c for cube in cubes for c in (cube, mirror(cube))]


def wheel(cx, cy, cz, left):
    """Dodecagonal tyre from 6 strips (apothem 11), dodecagonal rim disc + CTIS hub on the outer face."""
    a, w = 11.0, 7.0
    x0 = cx - w / 2
    cubes = [{"origin": [x0, cy - a, cz - a * math.tan(math.radians(15))], "size": [w, 2 * a, round(2 * a * math.tan(math.radians(15)), 3)],
              "pivot": [cx, cy, cz], "rotation": [k * 30, 0, 0], "uv": TYRE} for k in range(6)]
    ra = 6.5
    rx = x0 + w - 0.4 if left else x0 - 0.4
    cubes += [{"origin": [rx, cy - ra, cz - ra * 0.27], "size": [0.8, 2 * ra, round(2 * ra * 0.27, 3)],
               "pivot": [cx, cy, cz], "rotation": [k * 30, 0, 0], "uv": RIM} for k in range(6)]
    hx = x0 + w + 0.4 if left else x0 - 1.6
    cubes += [box([hx, cy - 2, cz - 2], [1.2, 4, 4], STEEL), box([hx + (0.4 if left else 0), cy - 0.6, cz - 0.6], [0.8, 1.2, 1.2], BRASS)]
    return cubes


AXLES = [("f", "1", -46), ("f", "2", -21), ("r", "1", 14), ("r", "2", 39)]
GZ = lambda y: -64 + (y - 22) * 18 / 14  # glacis z at height y


def hull():
    c = []
    # Lower hull: V-belly, hollow troop box (floor top y12), lower side walls
    c += [box([-14, 6, -56], [28, 6, 108], MUD)]
    c += both(rod((14, 6, -2), (16, 12, -2), 1.5, 108, MUD))                        # belly chines
    c += both(box([13, 12, -54], [2, 10, 106], MUDARMOR))
    c += [rod((0, 6, -55), (0, 22, -64), 30, 3, MUDARMOR)]                          # lower nose plate
    c += [box([-14, 10, -60], [28, 10, 6], MUD)]
    # Sponson floors over the wheels and upper side walls (vision blocks at the troop seats)
    c += both(box([15, 22, -50], [7, 1.5, 102], MUDARMOR))
    c += both(rod((15, 18.5, 1), (22, 22.5, 1), 1.2, 102, MUDARMOR))                 # sponson undercut chamfer
    for z0, z1 in ((-50, -4), (2, 12), (18, 52)):
        c += both(box([20.5, 23.5, z0], [1.5, 12, z1 - z0], ARMOR))
    for z0 in (-4, 12):
        c += both(box([20.5, 23.5, z0], [1.5, 3.5, 6], ARMOR), box([20.5, 31, z0], [1.5, 4.5, 6], ARMOR),
                  box([21, 27, z0], [0.5, 4, 6], GLASS))
    # Glacis: long shallow upper plate split around the driver's vision blocks (x 4..16, y 27.5..31)
    c += [rod((0, 22, GZ(22)), (0, 27.5, GZ(27.5)), 44, 2, WELD), rod((0, 31, GZ(31)), (0, 36, GZ(36)), 44, 2, WELD)]
    c += [rod((-9, 27.5, GZ(27.5)), (-9, 31, GZ(31)), 26, 2, WELD), rod((19, 27.5, GZ(27.5)), (19, 31, GZ(31)), 6, 2, WELD)]
    c += [rod((10, 27.5, GZ(27.5)), (10, 31, GZ(31)), 12, 1, GLASS)]
    c += [rod((x, 27.4, GZ(27.4) - 0.4), (x, 31.1, GZ(31.1) - 0.4), 0.8, 1, GUN) for x in (4, 8, 12, 16)]  # block frames
    c += both(box([15, 22, -60], [7, 1.5, 10], MUDARMOR))
    # Roof (top y36.5), with hatch holes over driver and commander seats
    c += [box([-22, 35, -46], [44, 1.5, 4], DECK), box([-22, 35, -34], [44, 1.5, 86], DECK),
          box([-6, 35, -42], [12, 1.5, 8], DECK)]
    c += both(box([14, 35, -42], [8, 1.5, 8], DECK))
    c += both(rod((21, 33, 3), (19.5, 36.5, 3), 1.2, 98, ARMOR))                      # roof edge bevel
    # Rear wall (ramp sits in the middle)
    c += both(box([11, 12, 50.5], [11, 24, 1.5], ARMOR), box([11, 6, 50.5], [3, 6, 1.5], MUD))
    c += [box([-11, 34, 50.5], [22, 2, 1.5], ARMOR)]
    # Bolt-on applique tiles
    for k in range(8):
        z0 = -48 + k * 12.5
        if not (-6 < z0 + 5 < 20):
            c += both(box([22, 24, z0], [1, 10.5, 11.5], APPLIQUE))
    c += both(box([22, 24, -4.5], [1, 2.5, 23], APPLIQUE), box([22, 31.5, -4.5], [1, 3, 23], APPLIQUE))
    # Slat armour cage (frame, standoffs, vertical bars)
    for y in (21, 28.5, 36):
        c += both(box([25, y, -47], [1, 1, 96], SLAT))
    c += both(*[box([23, 27.5, z], [2, 1, 1], STEEL) for z in range(-44, 48, 16)])
    c += both(*[box([25.2, 21, -46 + i * 3.5], [0.6, 16, 0.8], SLAT) for i in range(27)])
    c += both(box([25, 21, -48], [1, 16, 1], SLAT), box([25, 21, 48], [1, 16, 1], SLAT))
    # Headlight clusters with guards, front tow eyes, wire guard
    c += both(box([15, 22.5, -66], [6, 3.5, 3], ARMOR2), box([15.5, 23, -66.3], [2.5, 2.5, 0.4], LENS),
              box([18.5, 23, -66.3], [2, 2.5, 0.4], AMBER), box([14.5, 26.2, -67], [7, 0.6, 1], GUN),
              box([14.5, 22, -67], [0.6, 4.8, 1], GUN))
    c += both(box([8, 9, -63], [3, 4, 3], STEEL), box([8.5, 8, -64.5], [2, 2, 2], STEEL))
    # Driver periscopes and hatch, commander cupola with periscope ring
    c += [box([x, 36.5, -45], [2, 1.5, 1.5], STEEL) for x in (6.5, 9, 11.5)]
    c += [box([x + 0.3, 36.8, -45.2], [1.4, 1, 0.3], OPTIC) for x in (6.5, 9, 11.5)]
    c += [box([5.5, 36.5, -43], [9, 1, 1], STEEL), box([5.5, 36.5, -34], [9, 1, 1], STEEL),
          box([5.5, 36.5, -42], [1, 1, 8], STEEL), box([13.5, 36.5, -42], [1, 1, 8], STEEL)]
    c += [rod((10, 37.5, -33.5), (10, 45.5, -31.5), 8, 1, ARMOR2)]                   # driver hatch swung open
    c += [box([-14.5, 36.5, -43], [9, 2, 1], STEEL), box([-14.5, 36.5, -34], [9, 2, 1], STEEL),
          box([-14.5, 36.5, -42], [1, 2, 8], STEEL), box([-6.5, 36.5, -42], [1, 2, 8], STEEL)]
    c += [box([x, 38.5, -43.5], [1.6, 1.2, 1], OPTIC) for x in (-13.6, -10.8, -8)]
    c += [rod((-10, 38.5, -33.5), (-10, 45, -30), 8, 1, ARMOR2)]
    # Engine deck louvers + right-side exhaust (engine front-right like Stryker/Boxer)
    c += [box([-20, 36.5, -30], [11, 0.6, 14], GRILLE), box([-20.5, 36.4, -30.5], [12, 0.4, 15], STEEL)]
    c += [box([-23.5, 29, -32], [1.5, 5, 9], GRILLE), box([-24, 28.5, -32.5], [0.5, 6, 10], STEEL)]
    # Hull smoke grenade launchers (4 tubes each side, angled forward/out)
    c += both(*[rod((16 + i * 1.4, 36.5, -44), (17.5 + i * 1.6, 39.5, -47.5), 1.2, 1.2, GUN) for i in range(4)])
    c += both(box([15.5, 36.5, -45], [6.5, 1, 2.5], STEEL))
    # Mirrors on folding arms
    c += both(rod((21.5, 34, -46), (24.5, 38, -48), 0.6, 0.6, GUN), box([23.5, 37, -49.5], [2.2, 3, 0.6], GUN))
    # Tools on the roof edges: shovel, pickaxe, crowbar, tow cable; jerrycans on the rear
    c += [box([16, 36.5, 4], [1, 0.8, 16], WOOD), box([15.5, 36.5, 20], [2, 0.6, 4.5], STEEL),
          box([-17, 36.5, 4], [1, 0.8, 15], WOOD), box([-19.5, 36.5, 18], [6, 1, 1], STEEL),
          box([13, 36.5, 30], [0.8, 0.8, 16], STEEL), box([-14, 36.5, 30], [1.2, 1.2, 16], GUN)]
    c += both(box([15, 23, 52], [5, 8, 3], JERRY), box([16.5, 31, 52.5], [2, 1, 2], JERRY), box([14.5, 26, 51.8], [6, 1, 3.5], STRAP))
    # Rear: tail lights, tow eyes, waterjet nozzles, mudflaps, rear step
    c += both(box([17, 32, 52], [3, 2, 0.5], TAIL), box([17, 30, 52], [3, 1.5, 0.5], AMBER),
              box([8, 9, 52], [3, 4, 2], STEEL), box([5, 6.5, 52], [6, 4, 3], GUN), box([16.5, 2, 49], [7, 9, 0.4], RUBBER),
              box([16.5, 2, -10], [7, 8, 0.4], RUBBER))
    c += [box([-10, 6, 53], [20, 1, 3], STEEL)]
    # Suspension arms to every hub
    c += both(*[box([15, 9.5, z - 1.5], [2.5, 3, 3], STEEL) for _, _, z in AXLES])
    # Antenna bases
    c += both(box([16.5, 36.5, 44], [3, 2, 3], STEEL))
    return c


def ramp():
    return [box([-11, 6, 50.5], [22, 28, 2], ARMOR), box([-4, 12, 52.5], [8, 16, 1], ARMOR2),
            box([-3, 23, 52.6], [6, 3, 1], GLASS), box([-3.5, 22.5, 53.4], [7, 4, 0.3], GUN),
            box([2.5, 18, 53.5], [1, 3, 1], STEEL), box([-9, 7, 52.5], [18, 1.5, 1], GUN),
            box([-12, 6, 50], [2, 3, 3], STEEL), box([10, 6, 50], [2, 3, 3], STEEL)]


def turret():
    c = [box([-4.5, 36.5, -22.5], [9, 2, 9], STEEL), box([-3, 38.5, -21], [6, 3, 6], ARMOR2),
         box([-5.5, 40, -23], [1.5, 7, 10], ARMOR2), box([4, 40, -23], [1.5, 7, 10], ARMOR2),
         box([-1.5, 42, -24], [3, 3, 11], GUN), box([-1.5, 45, -21], [3, 1, 4], GUN),           # M2 receiver + cover
         box([-0.8, 42.7, -30], [1.6, 1.6, 6], GUN), box([-0.45, 43.05, -40], [0.9, 0.9, 10], GUN),
         box([-0.9, 42.6, -41.5], [1.8, 1.8, 1.5], GUN), box([-0.3, 41, -16], [0.6, 2, 3], GUN),  # muzzle, grip
         box([1.5, 40.5, -20], [3.5, 4, 6.5], JERRY), rod((2, 44.5, -18), (0.8, 45.5, -18), 2, 3, STRAP),  # ammo can, feed belt
         box([-10.5, 41, -23], [4.5, 5.5, 7], ARMOR2), box([-10, 42.2, -23.3], [1.6, 1.6, 0.4], OPTIC),
         box([-7.8, 42.2, -23.3], [1.4, 1.4, 0.4], OPTIC), box([-10, 44.5, -23.3], [3.5, 0.6, 0.3], GUN),
         box([-10.5, 46.5, -23.5], [4.5, 0.6, 3], ARMOR2)]                                        # sensor hood
    c += [rod((x, 39, -19), (x + 1.5 * (1 if x > 0 else -1), 42, -22), 1.2, 1.2, GUN) for x in (6, 7.4, -6, -7.4)]
    return c


def straps():
    c = [rod((21 * sx, 36.5, 20 + 14 * sf), (9 * sx, 50, 20 + 5 * sf), 2.5, 0.6, STRAP) for sx in (1, -1) for sf in (1, -1)]
    c += [box([-10, 50, z - 1], [20, 1, 2], STRAP) for z in (14, 26)]
    c += [box([20 * sx - 1.5, 36.5, z - 1.5], [3, 2, 3], STEEL) for sx in (1, -1) for z in (6, 34)]
    return c


def bones():
    b = [{"name": "root", "pivot": [0, 0, 0]},
         {"name": "body", "parent": "root", "pivot": [0, 12, 0], "cubes": hull()},
         {"name": "turret", "parent": "body", "pivot": [0, 36.5, -18], "cubes": turret()},
         {"name": "rear_ramp", "parent": "body", "pivot": [0, 7, 51.5], "cubes": ramp()},
         {"name": "cargo_straps", "parent": "body", "pivot": [0, 36, 20], "cubes": straps()}]
    for side, x in (("l", 1), ("r", -1)):
        p = [18 * x, 38.5, 45.5]
        b.append({"name": f"antenna_{side}", "parent": "body", "pivot": p,
                  "cubes": [rod(tuple(p), (18.5 * x, 72, 47), 0.5, 0.5, GUN), box([18 * x - 0.6, 38.5, 44.9], [1.2, 2, 1.2], GUN)]})
    for fr, n, z in AXLES:
        for side, x in (("l", 20), ("r", -20)):
            name, parent = f"wheel_{fr}{side}{n}", "root"
            if fr == "f":
                parent = f"steer_f{side}{n}"
                b.append({"name": parent, "parent": "root", "pivot": [x, 11, z]})
            b.append({"name": name, "parent": parent, "pivot": [x, 11, z], "cubes": wheel(x, 11, z, x > 0)})
    return b


WHEELS = [f"wheel_{fr}{s}{n}" for fr, n, _ in AXLES for s in "lr"]


def animation():
    spin = {"rotation": {"0.0": [0, 0, 0], "1.0": [-360, 0, 0]}}
    bones_drive = {w: spin for w in WHEELS}
    bones_drive["body"] = {"position": {"0.0": [0, 0, 0], "0.25": [0, 0.15, 0], "0.5": [0, 0, 0], "0.75": [0, 0.15, 0], "1.0": [0, 0, 0]}}
    for a in ("antenna_l", "antenna_r"):
        bones_drive[a] = {"rotation": {"0.0": [-6, 0, 0], "0.5": [-10, 0, 0], "1.0": [-6, 0, 0]}}
    idle = {"body": {"position": {"0.0": [0, 0, 0], "1.5": [0, 0.08, 0], "3.0": [0, 0, 0]}},
            "antenna_l": {"rotation": {"0.0": [0, 0, 0], "1.5": [0, 0, 2], "3.0": [0, 0, 0]}},
            "antenna_r": {"rotation": {"0.0": [0, 0, 0], "1.5": [0, 0, -2], "3.0": [0, 0, 0]}}}
    return {"format_version": "1.8.0", "animations": {
        "animation.armored_apc.idle": {"loop": True, "animation_length": 3.0, "bones": idle},
        "animation.armored_apc.drive": {"loop": True, "animation_length": 1.0, "bones": bones_drive}}}


def item_icon():
    """16x16 side view: sloped nose left, slat cage, RWS, 4 wheels."""
    rows = [
        "................",
        "......k.........",
        "....kkkkk.......",
        "......gg........",
        "..ggGGGGGGGGGGg.",
        ".gGGsGsGsGsGsGg.",
        "gGGGsGsGsGsGsGg.",
        "gGGGsGsGsGsGsGg.",
        ".mmmmmmmmmmmmmm.",
        "..mmmmmmmmmmmm..",
        ".tt.tt...tt.tt..",
        "tRtttRt.tRtttRt.",
        ".tt.tt...tt.tt..",
        "................",
        "................",
        "................"]
    pal = {"k": (40, 40, 42), "g": (170, 176, 140), "G": (132, 138, 104), "s": (98, 104, 78),
           "m": (110, 96, 72), "t": (36, 36, 36), "R": (150, 152, 120)}
    buf = bytearray()
    for r in rows:
        for ch in r:
            buf += bytes(pal[ch]) + b"\xff" if ch in pal else b"\0\0\0\0"
    return make_png(16, 16, bytes(buf))


# ---------------------------------------------------------------- validation + preview
def validate(geo, anim):
    g = geo["minecraft:geometry"][0]
    names = {b["name"] for b in g["bones"]}
    n = 0
    for b in g["bones"]:
        assert b.get("parent") in names | {None}, b["name"]
        for c in b.get("cubes", []):
            n += 1
            assert all(s > 0 for s in c["size"]), (b["name"], c)
            for f in c["uv"].values():
                assert f["uv"][0] + f["uv_size"][0] <= 512 and f["uv"][1] + f["uv_size"][1] <= 512, c
    for a in anim["animations"].values():
        for bn in a["bones"]:
            assert bn in names, bn
    for w in WHEELS:
        assert w in names
    for s in ("steer_fl1", "steer_fr1", "steer_fl2", "steer_fr2", "body", "turret", "cargo_straps"):
        assert s in names
    return n, [b["name"] for b in g["bones"]]


def rot(p, piv, r):
    """GeckoLib cube rotation (matches rod(): +Y maps to (sin rz cos rx, cos rz cos rx, -sin rx))."""
    x, y, z = p[0] - piv[0], p[1] - piv[1], p[2] - piv[2]
    ax, az = math.radians(-r[0]), math.radians(-r[2])
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    return (x + piv[0], y + piv[1], z + piv[2])


def preview(geo, tex, out, yaw=35, pitch=-28, W=900, H=560, sc=5.2):
    zbuf = [1e9] * (W * H)
    img = bytearray([214, 218, 222, 255] * (W * H))
    cy, sy, cp, sp = math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def proj(p):
        x, y, z = -p[0], p[1], p[2]  # GeckoLib mirrors X
        x, z = x * cy - z * sy, x * sy + z * cy
        y, z = y * cp - z * sp, y * sp + z * cp
        return W / 2 + x * sc, H * 0.62 - y * sc, z

    light = (0.4, 0.8, -0.45)
    for b in geo["minecraft:geometry"][0]["bones"]:
        for c in b.get("cubes", []):
            (ox, oy, oz), (sx, sy_, sz) = c["origin"], c["size"]
            P = lambda a, b_, d: (ox + a * sx, oy + b_ * sy_, oz + d * sz)
            faces = {"north": (P(1, 1, 0), P(0, 1, 0), P(1, 0, 0), (0, 0, -1)), "south": (P(0, 1, 1), P(1, 1, 1), P(0, 0, 1), (0, 0, 1)),
                     "east": (P(1, 1, 1), P(1, 1, 0), P(1, 0, 1), (1, 0, 0)), "west": (P(0, 1, 0), P(0, 1, 1), P(0, 0, 0), (-1, 0, 0)),
                     "up": (P(0, 1, 0), P(1, 1, 0), P(0, 1, 1), (0, 1, 0)), "down": (P(0, 0, 1), P(1, 0, 1), P(0, 0, 0), (0, -1, 0))}
            for fn, (o, ue, ve, nrm) in faces.items():
                if "rotation" in c:
                    o, ue, ve = (rot(q, c["pivot"], c["rotation"]) for q in (o, ue, ve))
                    nrm = tuple(a - b for a, b in zip(rot(nrm, (0, 0, 0), c["rotation"]), (0, 0, 0)))
                lum = 0.55 + 0.45 * max(0, -nrm[0] * light[0] + nrm[1] * light[1] + nrm[2] * light[2])
                po, pu, pv = proj(o), proj(ue), proj(ve)
                du, dv = [pu[i] - po[i] for i in range(3)], [pv[i] - po[i] for i in range(3)]
                det = du[0] * dv[1] - du[1] * dv[0]
                if abs(det) < 1e-6:
                    continue
                xs = [po[0], pu[0], pv[0], pu[0] + dv[0]]
                ys = [po[1], pu[1], pv[1], pu[1] + dv[1]]
                fuv = c["uv"][fn]
                for yy in range(max(0, int(min(ys))), min(H, int(max(ys)) + 1)):
                    for xx in range(max(0, int(min(xs))), min(W, int(max(xs)) + 1)):
                        qx, qy = xx + 0.5 - po[0], yy + 0.5 - po[1]
                        s = (qx * dv[1] - qy * dv[0]) / det
                        t = (du[0] * qy - du[1] * qx) / det
                        if not (0 <= s <= 1 and 0 <= t <= 1):
                            continue
                        z = po[2] + s * du[2] + t * dv[2]
                        i = yy * W + xx
                        if z >= zbuf[i]:
                            continue
                        tu = int(fuv["uv"][0] + min(s * fuv["uv_size"][0], fuv["uv_size"][0] - 0.5))
                        tv = int(fuv["uv"][1] + min(t * fuv["uv_size"][1], fuv["uv_size"][1] - 0.5))
                        k = (tv * 512 + tu) * 4
                        if tex[k + 3] == 0:
                            continue
                        zbuf[i] = z
                        img[i * 4:i * 4 + 3] = bytes(min(255, int(tex[k + j] * lum)) for j in range(3))
    with open(out, "wb") as f:
        f.write(make_png(W, H, bytes(img)))
    print("Preview:", out)


def main():
    tex = paint_texture()
    tex.save(os.path.join(ROOT, "textures/entity/transport/armored_apc.png"))
    with open(os.path.join(ROOT, "textures/item/armored_apc.png"), "wb") as f:
        f.write(item_icon())
    geo_path = os.path.join(ROOT, "geo/armored_apc.geo.json")
    write_geo(geo_path, "geometry.armored_apc", bones(), 10.0, 6.0, 2.0)
    anim = animation()
    with open(os.path.join(ROOT, "animations/armored_apc.animation.json"), "w") as f:
        json.dump(anim, f, indent=2)
    geo = json.load(open(geo_path))
    n, names = validate(geo, anim)
    print(f"OK: {n} cubes, bones: {', '.join(names)}")
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        preview(geo, tex.buf, out)
        preview(geo, tex.buf, out.replace(".png", "_rear.png"), yaw=215)


if __name__ == "__main__":
    main()
