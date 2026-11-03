#!/usr/bin/env python3
"""Mech field repair & recharge truck (HEMTT wrecker / M984 style 8x8): geo, animation, entity texture, item icon, preview.

Model space follows the APC: nose at model -Z (= entity-local +Z in Java), +X = vehicle left (GeckoLib mirrors X).
Driver cushion top y24 at (x+10, z-54); passenger at (x-10, z-54).
Run: python3 scripts/gen_repair_truck.py [--preview out.png]
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_transport_assets import TextureDrawer, make_png, rod, write_geo  # noqa: E402
from gen_armored_apc import h, smooth, box, mirror, both, rot  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources", "assets", "titancombat")

ARMOR, ARMOR2, PLATE, DECK, MUD, STEEL, SHUTTER, GRILLE = [[i * 64, 0] for i in range(8)]
TYRE, RIM, RUBBER, GLASS, LENS, TAIL, AMBER, OPTIC = [[i * 64, 64] for i in range(8)]
TOOLRED, STRAP, BATT, BRASS, GUN, MARK, WELD, MUDARMOR = [[i * 64, 128] for i in range(8)]
HAZARD, CABLE, INSIG, BOTTLE, ARC, CHROME, RUST, HOSE = [[i * 64, 192] for i in range(8)]

BASE = (184, 180, 156)  # light neutral sand-grey so a faction tint multiplies cleanly


def paint_texture():
    t = TextureDrawer(512, 512)
    px = lambda x, y, c, a=255: t.set_pixel(x, y, *(max(0, min(255, int(v))) for v in c), a)
    add = lambda c, d: tuple(v + d for v in c)
    mix = lambda a, b, k: tuple(a[i] * (1 - k) + b[i] * k for i in range(3))

    def armor(u, v, base, seam=16, bolts=True, mud=0.0, s=1):
        for y in range(64):
            for x in range(64):
                c = add(base, (smooth(x, y, s) - 0.5) * 14 + (h(x, y, s + 9) - 0.5) * 6)
                streak = h(x, 0, s + 3)
                if streak > 0.8:
                    c = add(c, -10 * (1 - y / 64) * (streak - 0.8) * 5)
                if h(x, y, s + 5) > 0.985:
                    c = add(c, -30)  # chips show dark primer on light paint
                if mud:
                    m = smooth(x, y, s + 7, 4) + h(x, y, s + 8) * 0.3 + y / 64 * 0.4
                    if m > 1.2 - mud:
                        c = mix(c, (118, 100, 76), 0.85)
                if x == 0 or y == 0:
                    c = add(c, 14)
                if seam:
                    lx, ly = x % seam, y % seam
                    if x and y and (lx == 0 or ly == 0):
                        c = add(c, -38)
                    elif x and y and (lx == 1 or ly == 1):
                        c = add(c, 8)
                    elif bolts and lx in (3, seam - 3) and ly in (3, seam - 3):
                        c = add(c, 26)
                    elif bolts and lx in (3, seam - 3) and ly in (4, seam - 2):
                        c = add(c, -30)
                px(u + x, v + y, c)

    armor(*ARMOR, BASE)
    armor(*ARMOR2, add(BASE, -6), seam=0, s=2)
    armor(*PLATE, add(BASE, -10), seam=11, s=3)
    armor(*MUD, (122, 106, 82), seam=0, mud=0.9, s=4)
    armor(*MUDARMOR, BASE, seam=16, mud=0.5, s=5)
    armor(*WELD, BASE, seam=0, s=6)
    armor(*TOOLRED, (178, 44, 36), seam=8, s=7)
    armor(*BATT, (70, 74, 70), seam=6, s=8)
    for i in range(64):
        for k in (12, 31, 50):
            px(WELD[0] + i, WELD[1] + k, add(BASE, -20 + (i % 3) * 12))
    for y in range(64):
        for x in range(64):
            g = (h(x, y, 11) > 0.55) * 14 + ((x + y) % 4 == 0) * 10  # diamond-plate grit
            px(DECK[0] + x, DECK[1] + y, add((150, 150, 146), g - 6 + (x == 0 or y == 0) * 12))
            px(STEEL[0] + x, STEEL[1] + y, add((92, 94, 90), (smooth(x, y, 12) - .5) * 14 + (x == 0 or y == 0) * 20))
            px(SHUTTER[0] + x, SHUTTER[1] + y, add(BASE, -34 if y % 3 == 0 else (6 if y % 3 == 1 else -6)) if x else add(BASE, -40))
            px(GRILLE[0] + x, GRILLE[1] + y, (38, 40, 38) if y % 2 else add(BASE, -40))
            tread = 46 if (y + (x // 3 % 2) * 2) % 4 < 2 else 32
            px(TYRE[0] + x, TYRE[1] + y, (tread, tread - 2, tread - 4))
            px(RIM[0] + x, RIM[1] + y, add(BASE, -30 + (x == 0 or y == 0) * 20 - (h(x, y, 31) > .8) * 20))
            px(RUBBER[0] + x, RUBBER[1] + y, add((40, 40, 38), (h(x, y, 15) - .5) * 8))
            t.set_pixel(GLASS[0] + x, GLASS[1] + y, 0, 0, 0, 0)
            px(LENS[0] + x, LENS[1] + y, (255, 252, 226) if (x + y) % 5 else (232, 228, 196))
            px(TAIL[0] + x, TAIL[1] + y, (200, 30, 26) if (x + y) % 4 else (150, 20, 18))
            px(AMBER[0] + x, AMBER[1] + y, (252, 172, 34) if (x * y) % 3 else (220, 140, 20))
            px(OPTIC[0] + x, OPTIC[1] + y, (30, 44, 70) if (x + y) % 6 else (110, 150, 190))
            px(STRAP[0] + x, STRAP[1] + y, add((214, 120, 30), ((x + y) % 3 == 0) * -24))
            px(BRASS[0] + x, BRASS[1] + y, (186, 152, 70))
            px(GUN[0] + x, GUN[1] + y, add((40, 40, 42), (x == 0 or y == 0) * 22 + (h(x, y, 17) - .5) * 6))
            red = ((x + y) // 4) % 2 == 0  # red/white maintenance chevrons
            px(MARK[0] + x, MARK[1] + y, (196, 34, 30) if red else (236, 234, 226))
            yel = ((x + y) // 4) % 2 == 0
            c = (242, 186, 18) if yel else (30, 30, 32)
            if h(x, y, 33) > 0.94:
                c = add(c, -40)  # scuffs
            px(HAZARD[0] + x, HAZARD[1] + y, c)
            px(CABLE[0] + x, CABLE[1] + y, add((232, 110, 22), -30 if x % 3 == 0 else (h(x, y, 34) - .5) * 14))
            px(BOTTLE[0] + x, BOTTLE[1] + y, add((60, 110, 70) if y > 3 else (90, 90, 90), (x == 0) * 30))
            px(ARC[0] + x, ARC[1] + y, (190, 230, 255) if (x + y) % 3 else (255, 255, 255))
            px(CHROME[0] + x, CHROME[1] + y, add((196, 200, 204), (x % 2) * 18))
            px(RUST[0] + x, RUST[1] + y, add((70, 62, 54), (smooth(x, y, 35) - .5) * 30 + (h(x, y, 36) > .7) * 25))
            px(HOSE[0] + x, HOSE[1] + y, add((26, 26, 28), (y % 2) * 10))
    # insignia (top-left 12x12 of its cell): olive plate, red disc, white wrench, yellow bolt
    armor(*INSIG, BASE, seam=0, s=9)
    for y in range(12):
        for x in range(12):
            d = math.hypot(x - 5.5, y - 5.5)
            if d < 5.6:
                c = (190, 30, 28) if d > 4.6 else (236, 234, 226)
                if d <= 4.6:
                    if abs((x - 5.5) - (y - 5.5)) < 1.2 and 1 < x < 10:
                        c = (60, 62, 66)  # wrench shaft
                    if math.hypot(x - 2.5, y - 2.5) < 1.6 or math.hypot(x - 8.5, y - 8.5) < 1.6:
                        c = (60, 62, 66)
                px(INSIG[0] + x, INSIG[1] + y, c)
    for x, y in ((7, 2), (6, 3), (5, 4), (6, 4), (7, 4), (6, 5), (5, 6), (4, 7), (5, 7), (4, 8), (3, 9)):
        px(INSIG[0] + x, INSIG[1] + y, (250, 200, 20))
    return t


# ---------------------------------------------------------------- geometry
R, TW = 12.5, 8.0  # tyre radius, width
AXLES = [("f", "1", -54), ("f", "2", -32), ("r", "1", 22), ("r", "2", 42)]
WY, WX = 12.5, 19  # wheel centre height, half track


def wheel(cx, cy, cz, left):
    """12-sided tyre from 6 rotated strips, rim disc, CTIS hub and lug ring on the outer face."""
    x0, k = cx - TW / 2, math.tan(math.radians(15))
    c = [{"origin": [x0, cy - R, cz - R * k], "size": [TW, 2 * R, round(2 * R * k, 3)],
          "pivot": [cx, cy, cz], "rotation": [i * 30, 0, 0], "uv": TYRE} for i in range(6)]
    ra = 8
    rx = x0 + TW - 0.5 if left else x0 - 0.5
    c += [{"origin": [rx, cy - ra, cz - ra * k], "size": [1, 2 * ra, round(2 * ra * k, 3)],
           "pivot": [cx, cy, cz], "rotation": [i * 45, 0, 0], "uv": RIM} for i in range(4)]
    hx = x0 + TW + 0.5 if left else x0 - 2
    c += [box([hx, cy - 3, cz - 3], [1.5, 6, 6], STEEL), box([hx + (0.5 if left else 0), cy - 1, cz - 1], [1, 2, 2], BRASS)]
    c += [rod((hx + 0.75, cy, cz), (hx + 0.75 + (2 if left else -2), cy + 2, cz), 0.5, 0.5, HOSE)]  # CTIS air line
    return c


def cab():
    c = []
    c += [box([-22, 19, -71], [44, 1.5, 33], DECK)]                                       # floor
    c += [box([-22, 19, -72], [44, 15, 2], ARMOR)]                                        # front wall / engine face
    c += both(box([20.5, 20.5, -70], [1.5, 13.5, 32], ARMOR))                             # lower doors
    c += [box([-22, 20.5, -40], [44, 27, 2], ARMOR)]                                      # rear wall
    # windscreen (raked) with pillars, upper side windows with posts
    c += [rod((0, 34, -71), (0, 46, -66), 38, 1, GLASS)]
    c += both(rod((20.5, 34, -71), (20.5, 46.5, -66), 3, 2, ARMOR), rod((0.8, 34, -71), (0.8, 46, -66), 1.6, 1.5, ARMOR))
    c += [box([-22, 32, -72.5], [44, 2.5, 3], ARMOR2)]                                    # windscreen sill
    c += both(box([20.5, 34, -66], [1.5, 2, 26], ARMOR), box([20.5, 44.5, -66], [1.5, 2.5, 26], ARMOR),
              box([21, 36, -64], [0.5, 8.5, 22], GLASS), box([20.5, 36, -66], [1.5, 8.5, 2], ARMOR),
              box([20.5, 36, -42], [1.5, 8.5, 2], ARMOR), box([20.5, 36, -52], [1.5, 8.5, 1.5], ARMOR))
    c += [box([-22.5, 46.5, -67], [45, 2, 29], ARMOR), box([-18, 48.5, -60], [36, 1, 18], PLATE)]  # roof + armour kit
    # armoured window shutters hinged up on the roof edge, door handles, steps
    c += both(rod((22, 46.5, -63), (25.5, 49, -63), 1, 0.8, STEEL), box([22.2, 26, -50], [0.6, 1, 3], STEEL),
              box([20.5, 11, -52], [3.5, 1, 8], DECK), box([20.5, 15, -52], [3.5, 1, 8], DECK),
              box([22, 11, -52.5], [1, 9, 0.8], STEEL), box([22, 11, -43.5], [1, 9, 0.8], STEEL))
    # interior: seats, dash, steering wheel
    c += both(box([5, 20.5, -58], [10, 3.5, 9], RUBBER), box([5, 24, -50], [10, 11, 2.5], RUBBER))
    c += [box([-20, 26, -70], [40, 6, 6], GUN), rod((10, 27, -63), (10, 31, -61), 1.2, 1.2, GUN),
          {"origin": [6.5, 30, -62], "size": [7, 7, 0.8], "pivot": [10, 33.5, -61.6], "rotation": [-25, 0, 0], "uv": GUN}]
    c += [box([x, 32, -66], [3, 2, 1], OPTIC) for x in (2, 15, -6, -12)]                 # dash screens
    # front: grille, headlights, bumper, winch, brush guard, tow pintle, red/white marker boards
    c += [box([-12, 21, -72.6], [24, 9, 0.6], GRILLE)]
    c += both(box([14, 21.5, -73], [6.5, 5, 1.5], ARMOR2), box([14.5, 22, -73.4], [3, 4, 0.4], LENS),
              box([18, 22, -73.4], [2, 4, 0.4], AMBER), box([13.5, 26.6, -74], [7.5, 0.8, 2], GUN),
              box([13.5, 21, -74], [0.8, 6, 2], GUN), box([20.2, 21, -74], [0.8, 6, 2], GUN))
    c += [box([-23, 12, -78], [46, 7, 6], MUDARMOR), box([-23, 19, -77], [46, 1, 4], DECK)]
    c += both(box([17, 13, -78.3], [6, 5, 0.4], MARK))
    c += [box([-9, 13, -80], [18, 5, 3], STEEL), box([-7, 13.5, -81], [14, 4, 1], CABLE),
          box([-1.5, 10, -82], [3, 3, 5], STEEL), box([-2, 10.5, -84], [4, 2, 2], GUN)]
    c += both(box([10, 12, -81], [2, 8, 2], GUN), rod((11, 20, -80), (8, 30, -73), 1.5, 1.5, GUN), box([8, 10, -80], [4, 2, 3], STEEL))
    # front fenders (flat HEMTT style) + mud flaps, mirrors on long arms, roof beacons, horn, snorkel
    c += both(box([14, 25, -68], [10, 1, 44], MUDARMOR), box([22.5, 19, -68], [1.5, 6, 44], MUDARMOR),
              box([15, 4, -21], [8, 8, 0.4], RUBBER),
              rod((22, 40, -66), (28, 42, -66), 0.8, 0.8, GUN), box([27, 37, -67], [2.5, 7, 1], GUN),
              box([27.2, 37.5, -67.4], [2, 6, 0.4], CHROME), box([16, 48.5, -66], [3, 2.5, 3], AMBER),
              box([15.5, 48.5, -66.5], [4, 0.6, 4], GUN))
    c += [box([-25.5, 26, -44], [3, 26, 3], ARMOR2), box([-26, 52, -45], [4, 3, 5], GRILLE),
          box([-26, 30, -44.5], [4, 1, 4], STEEL), box([-26, 42, -44.5], [4, 1, 4], STEEL)]
    # roof light bar: 4 forward floodlights
    c += [box([-14, 49.5, -64], [28, 1.5, 2], GUN)]
    c += [box([x, 51, -65], [4, 3, 3], GUN) for x in (-13, -6.5, 2.5, 9)]
    c += [box([x + 0.5, 51.5, -65.4], [3, 2, 0.4], LENS) for x in (-13, -6.5, 2.5, 9)]
    c += [box([-3, 48.5, -48], [6, 4, 6], GUN), box([-1, 52.5, -46], [2, 1, 2], GUN)]      # radio / GPS dome
    return c


def chassis():
    c = []
    c += both(box([7, 14, -76], [4, 5, 140], STEEL))                                      # frame rails
    c += [box([-7, 15, z], [14, 3, 3], STEEL) for z in (-62, -20, 4, 32, 56)]             # crossmembers
    c += both(*[box([11, WY - 1.5, z - 1.5], [4.5, 3, 3], STEEL) for _, _, z in AXLES])  # axle stubs
    c += [box([-11, WY - 2, z - 2], [22, 4, 4], RUST) for _, _, z in AXLES]               # diff housings / axles
    c += [box([-4, WY - 4, z - 3], [8, 6, 6], RUST) for _, _, z in AXLES]
    c += [box([-1.5, 13, -54], [3, 2, 96], GUN)]                                          # drive shaft
    c += both(box([12, 14.5, -36], [3, 3, 2], STEEL), box([12, 14.5, 8], [3, 3, 34], STEEL))  # walking-beam springs
    # side lockers between the axle groups: toolbox doors with red handles
    c += both(box([13, 7, -18], [9, 12, 30], MUDARMOR), box([22, 9, -16], [0.5, 9, 12], PLATE),
              box([22, 9, -2], [0.5, 9, 12], PLATE), box([22.3, 13, -11], [0.6, 1, 2], TOOLRED),
              box([22.3, 13, 3], [0.6, 1, 2], TOOLRED), box([13, 6, -18], [10, 1, 30], STEEL))
    # fuel tank left, battery box right (under the generator)
    c += [box([13, 8, -24], [9, 9, 5], CHROME), box([-22, 8, -24], [9, 9, 5], BATT)]
    # rear mudguards and flaps
    c += both(box([14, 25.5, 9], [10, 1, 46], MUDARMOR), box([22.5, 21, 9], [1.5, 4.5, 46], MUDARMOR),
              box([15, 4, 55.5], [8, 9, 0.4], RUBBER))
    # rear bumper, tow pintle, tail lights, red/white marker boards
    c += [box([-23, 12, 62], [46, 6, 4], MUDARMOR), box([-2, 10, 65], [4, 4, 4], STEEL), box([-1, 11, 69], [2, 2, 2], GUN)]
    c += both(box([10, 12.5, 66.1], [12, 5, 0.4], MARK), box([16, 18.5, 64], [5, 2, 1], TAIL), box([12, 18.5, 64], [3, 2, 1], AMBER))
    return c


def modules():
    c = []
    # generator / power pod behind the cab: louvred housing, radiator, exhaust stack with rain cap
    c += [box([-22, 19, -38], [44, 1.5, 22], DECK), box([-22, 20.5, -37], [44, 18, 20], ARMOR2)]
    c += both(box([22, 22, -35], [0.5, 12, 16], GRILLE), box([21.6, 21.5, -35.5], [1, 13, 17], STEEL))
    c += [box([-20, 38.5, -35], [40, 1, 16], GRILLE), box([-21, 38.5, -36], [42, 0.6, 18], STEEL)]
    c += [box([-21, 38, -20], [4, 4, 4], RUST), box([-20.5, 42, -19.5], [3, 16, 3], RUST),
          box([-21, 50, -20], [4, 4, 4], GRILLE), rod((-19, 58, -18), (-19, 60, -15), 3.6, 0.6, GUN),
          box([-17.5, 30, -19.5], [3, 10, 3], RUST)]
    c += [box([4, 38.5, -30], [10, 2, 6], BATT), box([6, 40.5, -29], [2, 1, 2], TAIL), box([10, 40.5, -29], [2, 1, 2], GUN)]
    c += both(box([22.1, 35, -35], [0.4, 2.5, 16], HAZARD))
    # maintenance body: hollow-looking box with roller shutters, insignia, red/white band, roof walkway
    c += [box([-22, 19, -16], [44, 1.5, 34], DECK)]
    c += both(box([20.5, 20.5, -16], [1.5, 24, 34], ARMOR))
    c += [box([-22, 20.5, -16], [44, 24, 1.5], ARMOR), box([-22, 20.5, 16.5], [44, 24, 1.5], ARMOR),
          box([-22.5, 44.5, -17], [45, 2, 36], ARMOR)]
    c += both(box([22, 22, -14], [0.6, 20, 14], SHUTTER), box([22, 22, 1], [0.6, 20, 14], SHUTTER),
              box([22, 41.5, -14.5], [1.5, 1.5, 30], STEEL), box([22.5, 22, -0.5], [0.8, 20, 1], STEEL),
              box([22.6, 30, -10], [0.3, 12, 12], INSIG), box([22.6, 24, 1.5], [0.3, 2.5, 13], MARK))
    c += [box([-15, 46.5, -15], [30, 0.6, 32], DECK)]
    c += both(*[box([19, 46.5, z], [1, 5, 1], STEEL) for z in (-15, 0, 16)], box([19, 51.5, -15], [1, 1, 32], STEEL))
    c += [box([-10, 22, 18], [20, 18, 0.6], PLATE), box([-4, 26, 18.4], [8, 8, 0.3], INSIG)]
    # roof floodlight masts on all 4 corners (aimed out/down)
    for sx in (1, -1):
        for z in (-14, 15):
            c += [box([sx * 20 - 1, 46.5, z - 1], [2, 6, 2], GUN),
                  rod((sx * 20, 52.5, z), (sx * 23, 54, z + (2 if z > 0 else -2)), 4, 3, GUN)]
    c += both(box([22.5, 51, -16], [0.5, 3, 3], LENS), box([22.5, 51, 14], [0.5, 3, 3], LENS))
    # amber beacons on the body roof
    c += both(box([10, 46.5, 12], [3, 2.5, 3], AMBER))
    # rear flatbed: deck, side rails with hazard edging, headboard steps
    c += [box([-22, 19, 18], [44, 3, 44], DECK)]
    c += both(box([21, 19, 18], [1.5, 3, 44], HAZARD), box([21, 22, 20], [1, 4, 1], STEEL), box([21, 22, 60], [1, 4, 1], STEEL),
              box([21, 26, 20], [1, 1, 41], STEEL))
    c += [box([-22, 19, 61], [44, 3, 1.5], HAZARD)]
    # boom rest
    c += [box([-3, 22, 55], [6, 4, 3], STEEL), box([-4, 26, 55], [8, 1, 3], RUBBER), box([-4, 27, 55], [1, 2, 3], STEEL), box([3, 27, 55], [1, 2, 3], STEEL)]
    # cable reel stand (left side) and the heavy charging plug on its rack at the tail
    c += [box([7, 22, 41], [1, 10, 4], STEEL), box([21, 22, 41], [1, 10, 4], STEEL), box([7, 22, 38], [15, 1, 10], STEEL)]
    c += [box([10, 22, 55], [8, 6, 5], STEEL), box([11, 28, 55.5], [6, 1, 4], HAZARD),
          box([11, 23, 54], [6, 4, 1], GUN), box([12, 24, 53.5], [1, 2, 0.5], BRASS), box([15, 24, 53.5], [1, 2, 0.5], BRASS),
          box([12.5, 27, 52], [3, 3, 3], CABLE)]
    c += [rod((14, 30, 53.5), (14, 31, 46), 2, 2, CABLE)]
    # right side of the deck: stacked rolling toolboxes, welding gas bottles, spare battery modules, jerrycans
    c += [box([-20, 22, 22], [10, 7, 8], TOOLRED), box([-19.5, 29, 22.5], [9, 5, 7], TOOLRED),
          box([-20, 25, 21.6], [10, 0.5, 0.4], STEEL), box([-20, 31, 22.1], [9, 0.5, 0.4], STEEL),
          box([-20, 22, 32], [12, 6, 10], BATT), box([-19, 28, 33], [4, 2, 3], TAIL), box([-14, 28, 33], [4, 2, 3], GUN),
          box([-19, 28, 38], [10, 1, 3], HAZARD)]
    for i, z in enumerate((47, 51)):
        c += [box([-19.5, 22, z], [3.5, 14, 3.5], BOTTLE), box([-18.5, 36, z + 1], [1.5, 1.5, 1.5], BRASS)]
    c += [box([-20.5, 27, 46], [6, 1, 9], STRAP)]
    c += [box([-13, 22, 46], [4, 7, 6], ARMOR2), box([-12.5, 29, 47], [1.5, 1, 1.5], ARMOR2)]
    c += [rod((-17, 36, 49), (-9, 23, 44), 0.8, 0.8, HOSE)]                              # torch hose from bottles
    # rear stabiliser jack housings
    c += both(box([19, 14, 57], [5, 5, 5], HAZARD))
    return c


def outrigger(sx):
    x = 21.5 * sx
    return [box([x - 1.5, 4, 58], [3, 11, 3], CHROME), box([x - 3, 1, 56.5], [6, 3, 6], STEEL)]


def crane_base():
    c = [box([-6, 22, 21], [12, 2, 12], STEEL), box([-7, 22, 20], [14, 1, 14], RUST),
         box([-5, 24, 22], [10, 6, 10], ARMOR2), box([-5.2, 26, 21.8], [10.4, 1.5, 10.4], HAZARD),
         box([-4, 30, 24], [1.5, 4, 5], STEEL), box([2.5, 30, 24], [1.5, 4, 5], STEEL),
         box([-6, 24, 24], [1, 4, 4], GUN), box([-6.3, 25, 25], [0.3, 2, 2], OPTIC),                # control box
         rod((-3, 30, 30), (-3, 33, 34), 1, 1, HOSE), rod((3, 30, 30), (3, 33, 34), 1, 1, HOSE)]
    return c


def crane_boom():
    # boom lies along +Z from the king pin (0,32,26) to the knuckle at z58
    c = [box([-2.5, 29.5, 24], [5, 5, 6], STEEL), box([-2, 30, 30], [4, 4, 28], HAZARD),
         box([-2.3, 30.5, 34], [4.6, 3, 20], STEEL), box([-2, 29, 52], [4, 6, 7], STEEL),
         box([-1.5, 28, 32], [3, 2, 14], CHROME), box([-2, 27.5, 30], [4, 3, 3], STEEL),               # lift cylinder underside
         box([-0.5, 34, 30], [1, 1, 22], HOSE), box([2, 31, 30], [0.5, 1, 26], HOSE),
         box([-2.5, 34, 50], [5, 1.5, 4], GUN), box([-2.2, 34.5, 49.6], [4.4, 1, 0.4], LENS)]         # boom floodlight
    return c


def crane_arm():
    # arm folded back over the boom: knuckle at (0,35.5,57), arm runs -Z to z31
    c = [box([-2.5, 33, 54], [5, 5, 5], STEEL), box([-1.5, 34, 32], [3, 3, 22], HAZARD),
         box([-1, 37, 38], [2, 1.5, 14], CHROME), box([-1.5, 37, 52], [3, 2, 3], STEEL),               # fold cylinder
         box([0.5, 33.5, 33], [0.6, 0.6, 20], HOSE)]
    return c


def weld_head():
    # tool head at the arm tip: wrist, plasma/weld torch, clamp jaws, work lamp
    return [box([-2, 33.5, 29], [4, 4, 3], GUN), box([-1.5, 34, 26.5], [3, 3, 2.5], STEEL),
            box([-0.6, 34.9, 23], [1.2, 1.2, 3.5], BRASS), box([-0.3, 35.2, 22.2], [0.6, 0.6, 0.8], ARC),
            box([1.5, 34, 25], [1, 1, 3], CHROME), box([-2.5, 34, 25], [1, 1, 3], CHROME),
            box([-1, 37.5, 27.5], [2, 1.5, 2], GUN), box([-0.8, 37.7, 27.3], [1.6, 1, 0.3], LENS)]


def cable_reel():
    # transverse drum (axis X) centre (14, 31, 43): orange cable wraps + steel flanges
    cy, cz, k = 31, 43, math.tan(math.radians(22.5))
    c = []
    for i in range(4):
        c.append({"origin": [9, cy - 6, cz - 6 * k], "size": [10, 12, round(12 * k, 3)], "pivot": [14, cy, cz], "rotation": [i * 45, 0, 0], "uv": CABLE})
        for fx in (8, 19):
            c.append({"origin": [fx, cy - 8, cz - 8 * k], "size": [1, 16, round(16 * k, 3)], "pivot": [14, cy, cz], "rotation": [i * 45 + 22.5, 0, 0], "uv": STEEL})
    c += [box([6, cy - 1.5, cz - 1.5], [16, 3, 3], GUN), box([20, cy - 2.5, cz - 2.5], [2.5, 5, 5], HAZARD)]
    return c


def straps():
    # orange ratchet straps over the toolbox stack and battery modules
    return [box([-20.5, 22, 25], [11, 12.5, 0.6], STRAP), box([-20.5, 34, 25], [11, 0.6, 0.6], STRAP),
            box([-20.5, 22, 36], [13, 6.5, 0.6], STRAP), box([-21, 24, 24.5], [0.5, 2, 1.6], STEEL)]


def bones():
    b = [{"name": "root", "pivot": [0, 0, 0]},
         {"name": "body", "parent": "root", "pivot": [0, 12, 0], "cubes": cab() + chassis() + modules()},
         {"name": "cable_reel", "parent": "body", "pivot": [14, 31, 43], "cubes": cable_reel()},
         {"name": "crane_base", "parent": "body", "pivot": [0, 22, 27], "cubes": crane_base()},
         {"name": "crane_boom", "parent": "crane_base", "pivot": [0, 32, 27], "cubes": crane_boom()},
         {"name": "crane_arm", "parent": "crane_boom", "pivot": [0, 35.5, 56.5], "cubes": crane_arm()},
         {"name": "weld_head", "parent": "crane_arm", "pivot": [0, 35.5, 30.5], "cubes": weld_head()},
         {"name": "outrigger_l", "parent": "body", "pivot": [21.5, 15, 59.5], "cubes": outrigger(1)},
         {"name": "outrigger_r", "parent": "body", "pivot": [-21.5, 15, 59.5], "cubes": outrigger(-1)},
         {"name": "cargo_straps", "parent": "body", "pivot": [-15, 22, 30], "cubes": straps()}]
    for fr, n, z in AXLES:
        for side, x in (("l", WX), ("r", -WX)):
            name, parent = f"wheel_{fr}{side}{n}", "root"
            if fr == "f":
                parent = f"steer_f{side}{n}"
                b.append({"name": parent, "parent": "root", "pivot": [x, WY, z]})
            b.append({"name": name, "parent": parent, "pivot": [x, WY, z], "cubes": wheel(x, WY, z, x > 0)})
    return b


WHEELS = [f"wheel_{fr}{s}{n}" for fr, n, _ in AXLES for s in "lr"]
REPAIR_POSE = {"crane_base": [0, -100, 0], "crane_boom": [38, 0, 0], "crane_arm": [105, 0, 0], "weld_head": [-30, 0, 0],
               "outrigger_l": "drop", "outrigger_r": "drop"}


def animation():
    spin = {"rotation": {"0.0": [0, 0, 0], "1.0": [-360, 0, 0]}}
    drive = {w: spin for w in WHEELS}
    drive["body"] = {"position": {"0.0": [0, 0, 0], "0.25": [0, 0.15, 0], "0.5": [0, 0, 0], "0.75": [0, 0.15, 0], "1.0": [0, 0, 0]}}
    drive["crane_arm"] = {"rotation": {"0.0": [0, 0, 0], "0.5": [-1, 0, 0], "1.0": [0, 0, 0]}}  # stowed, slight bounce
    idle = {"body": {"position": {"0.0": [0, 0, 0], "1.5": [0, 0.08, 0], "3.0": [0, 0, 0]}},
            "crane_base": {"rotation": {"0.0": [0, 0, 0]}}, "crane_boom": {"rotation": {"0.0": [0, 0, 0]}},
            "crane_arm": {"rotation": {"0.0": [0, 0, 0]}}}
    bx, by, ax = REPAIR_POSE["crane_boom"][0], REPAIR_POSE["crane_base"][1], REPAIR_POSE["crane_arm"][0]
    wh = REPAIR_POSE["weld_head"][0]
    repair = {
        "crane_base": {"rotation": {"0.0": [0, 0, 0], "1.0": [0, by, 0], "2.5": [0, by - 4, 0], "4.0": [0, by + 3, 0], "5.5": [0, by - 4, 0], "7.0": [0, by + 3, 0], "8.0": [0, by, 0]}},
        "crane_boom": {"rotation": {"0.0": [0, 0, 0], "1.0": [bx, 0, 0], "3.0": [bx + 3, 0, 0], "5.0": [bx - 2, 0, 0], "8.0": [bx, 0, 0]}},
        "crane_arm": {"rotation": {"0.0": [0, 0, 0], "0.6": [ax * 0.4, 0, 0], "1.4": [ax, 0, 0], "2.0": [ax - 4, 0, 0], "3.0": [ax + 3, 0, 0],
                                   "4.0": [ax - 4, 0, 0], "5.0": [ax + 3, 0, 0], "6.0": [ax - 4, 0, 0], "7.0": [ax + 3, 0, 0], "8.0": [ax, 0, 0]}},
        "weld_head": {"rotation": {"0.0": [0, 0, 0], "1.4": [wh, 0, 0], "1.7": [wh, 8, 0], "2.0": [wh, -8, 0], "2.3": [wh, 8, 0], "2.6": [wh, -8, 0],
                                   "3.0": [wh, 0, 6], "3.4": [wh, 0, -6], "3.8": [wh, 6, 0], "4.2": [wh, -6, 0], "4.6": [wh, 8, 0],
                                   "5.0": [wh, -8, 0], "5.4": [wh, 0, 6], "5.8": [wh, 0, -6], "6.2": [wh, 8, 0], "6.6": [wh, -8, 0],
                                   "7.0": [wh, 6, 0], "7.5": [wh, -6, 0], "8.0": [wh, 0, 0]}},
        "cable_reel": {"rotation": {"0.0": [0, 0, 0], "8.0": [-90, 0, 0]}},
        "outrigger_l": {"position": {"0.0": [0, 0, 0], "0.8": [0, -3, 0], "8.0": [0, -3, 0]}},
        "outrigger_r": {"position": {"0.0": [0, 0, 0], "0.8": [0, -3, 0], "8.0": [0, -3, 0]}},
    }
    return {"format_version": "1.8.0", "animations": {
        "animation.repair_truck.idle": {"loop": True, "animation_length": 3.0, "bones": idle},
        "animation.repair_truck.drive": {"loop": True, "animation_length": 1.0, "bones": drive},
        # shortcut: the 0-1s unfold replays every loop; split into an intro + loop anim if Java ever plays them back-to-back
        "animation.repair_truck.repair": {"loop": True, "animation_length": 8.0, "bones": repair}}}


def item_icon():
    rows = [
        "................",
        "..........yk....",
        ".........yk.ky..",
        "...ll....k...k..",
        "..gggg....kyk...",
        "..gGGg.......k..",
        ".ggggg.GGGGGoooy",
        ".gGgggGGGGGGooog",
        ".ggggggGGrwGGGgg",
        ".mmmmmmmmmmmmmmm",
        "..tt.tt....tt.tt",
        ".tRtttRt..tRtttRt"[:16],
        "..tt.tt....tt.tt",
        "................",
        "................",
        "................"]
    pal = {"k": (34, 34, 36), "y": (242, 186, 18), "g": (196, 192, 168), "G": (164, 160, 136), "l": (60, 80, 110),
           "o": (232, 110, 22), "r": (196, 34, 30), "w": (236, 234, 226), "m": (110, 96, 72), "t": (36, 36, 36), "R": (150, 150, 140)}
    buf = bytearray()
    for r in rows:
        for ch in r.ljust(16, "."):
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
    for s in WHEELS + ["steer_fl1", "steer_fr1", "steer_fl2", "steer_fr2", "body", "crane_base", "crane_boom", "crane_arm", "cargo_straps"]:
        assert s in names, s
    parent = {b["name"]: b.get("parent") for b in g["bones"]}
    assert parent["crane_arm"] == "crane_boom" and parent["crane_boom"] == "crane_base"
    return n, [b["name"] for b in g["bones"]]


def rot3(p, piv, r):
    """Bone rotation in the same pre-mirror convention as rot(): X then Y then Z."""
    x, y, z = p[0] - piv[0], p[1] - piv[1], p[2] - piv[2]
    ax, ay, az = math.radians(-r[0]), math.radians(r[1]), math.radians(-r[2])
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    return (x + piv[0], y + piv[1], z + piv[2])


def preview(geo, tex, out, yaw=35, pitch=-28, W=1000, H=640, sc=5.0, pose=None):
    pose = pose or {}
    bones_ = {b["name"]: b for b in geo["minecraft:geometry"][0]["bones"]}

    def posed(q, bn):
        while bn:
            b = bones_[bn]
            r = pose.get(bn)
            if r == "drop":
                q = (q[0], q[1] - 3, q[2])
            elif r:
                q = rot3(q, b["pivot"], r)
            bn = b.get("parent")
        return q

    zbuf = [1e9] * (W * H)
    img = bytearray([214, 218, 222, 255] * (W * H))
    cy, sy, cp, sp = math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def proj(p):
        x, y, z = -p[0], p[1], p[2]
        x, z = x * cy - z * sy, x * sy + z * cy
        y, z = y * cp - z * sp, y * sp + z * cp
        return W / 2 + x * sc, H * 0.66 - y * sc, z

    light = (0.4, 0.8, -0.45)
    for b in bones_.values():
        for c in b.get("cubes", []):
            (ox, oy, oz), (sx, sy_, sz) = c["origin"], c["size"]
            P = lambda a, b_, d: (ox + a * sx, oy + b_ * sy_, oz + d * sz)
            faces = {"north": (P(1, 1, 0), P(0, 1, 0), P(1, 0, 0)), "south": (P(0, 1, 1), P(1, 1, 1), P(0, 0, 1)),
                     "east": (P(1, 1, 1), P(1, 1, 0), P(1, 0, 1)), "west": (P(0, 1, 0), P(0, 1, 1), P(0, 0, 0)),
                     "up": (P(0, 1, 0), P(1, 1, 0), P(0, 1, 1)), "down": (P(0, 0, 1), P(1, 0, 1), P(0, 0, 0))}
            for fn, (o, ue, ve) in faces.items():
                if "rotation" in c:
                    o, ue, ve = (rot(q, c["pivot"], c["rotation"]) for q in (o, ue, ve))
                o, ue, ve = (posed(q, b["name"]) for q in (o, ue, ve))
                a1, a2 = [ue[i] - o[i] for i in range(3)], [ve[i] - o[i] for i in range(3)]
                nrm = (a1[1] * a2[2] - a1[2] * a2[1], a1[2] * a2[0] - a1[0] * a2[2], a1[0] * a2[1] - a1[1] * a2[0])
                ln = math.sqrt(sum(v * v for v in nrm)) or 1
                nrm = tuple(-v / ln for v in nrm)
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
    tex.save(os.path.join(ROOT, "textures/entity/transport/repair_truck.png"))
    with open(os.path.join(ROOT, "textures/item/repair_truck.png"), "wb") as f:
        f.write(item_icon())
    geo_path = os.path.join(ROOT, "geo/repair_truck.geo.json")
    write_geo(geo_path, "geometry.repair_truck", bones(), 10.0, 6.0, 2.0)
    anim = animation()
    with open(os.path.join(ROOT, "animations/repair_truck.animation.json"), "w") as f:
        json.dump(anim, f, indent=2)
    geo = json.load(open(geo_path))
    n, names = validate(geo, anim)
    print(f"OK: {n} cubes, bones: {', '.join(names)}")
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        preview(geo, tex.buf, out)
        preview(geo, tex.buf, out.replace(".png", "_rear.png"), yaw=215)
        preview(geo, tex.buf, out.replace(".png", "_repair.png"), yaw=-55, pose=REPAIR_POSE)


if __name__ == "__main__":
    main()
