#!/usr/bin/env python3
"""C-130 Hercules four-engine transport: geo + animation + entity texture + item icon + preview render.

Model space: nose at -Z, +X = vehicle left, +Y up, 16 px = 1 block. Ground (wheel bottoms) at y=0.
The fuselage is a hollow shell so a kneeling Titan fits in the bay and can roll out of the open ramp.
Run: python3 scripts/gen_c130_hercules.py [--preview out.png]
"""
import json, math, os, random, sys

sys.path.insert(0, os.path.dirname(__file__))
import gen_v22_osprey as O  # reuse cube helpers, UV packer, texture skins, rasterizer, validator
from gen_v22_osprey import (box, cbox, stick, wheel, cell, save_png, render, validate,
                            HULL, BELLY, GLASS, DARK, BLADE, WALK, TIRE, SPIN, SOOT, GRILLE, RED, GREEN, WINDOW,
                            INTER, RAMP, DOOR, WHITE, TIP, STAR)

ROOT = O.ROOT
TEX = O.TEX
BAY, ROLLER, DEICE, NUM, NUM_R = 21, 22, 23, 24, 25

# ---------------------------------------------------------------- key dimensions (px)
FLOOR = 14          # bay floor top
CEIL = 86           # bay ceiling (72 px = 4.5 blocks clear)
TOP = 92            # fuselage crown
HW = 32             # fuselage outer half width (56 px = 3.5 blocks inside)
BAY_Z0, BAY_Z1 = -124, 68   # bay floor span; ramp hinge at BAY_Z1
RAMP_END = (46, 122)        # (y, z) of the ramp lip when closed
DOOR_HINGE = (74, 162)      # (y, z) top hinge of the upper cargo door
PROP_Y = 86
ENG_X = (70, 142)           # inboard / outboard nacelle x


def shell(z0, z1, hw, yb, yt, w=4, floor=True, inner=BAY, c=None, roof=True):
    """Hollow rounded fuselage ring slice: walls, roof, floor, with two chamfer steps so it reads round."""
    c = c if c is not None else min(10, (yt - yb) / 4, hw / 2)
    out = []
    for s in (-1, 1):
        f = {"west": inner} if s > 0 else {"east": inner}
        out += [box(s * (hw - w), yb + c, z0, s * hw, yt - c, z1, HULL, **f),
                box(s * (hw - w - c * 0.35), yt - c, z0, s * (hw - c * 0.35), yt - c * 0.35, z1, HULL, **f),
                box(s * (hw - w - c * 0.35), yb + c * 0.35, z0, s * (hw - c * 0.35), yb + c, z1, BELLY, **f)]
    if roof:
        out.append(box(-(hw - c), yt - w, z0, hw - c, yt, z1, HULL, down=inner))
    if floor:
        out.append(box(-(hw - c), yb, z0, hw - c, yb + w, z1, BELLY, up=inner))
    return out


def solid(z0, z1, hw, yb, yt, mat=HULL, c=None, **faces):
    c = c if c is not None else min(8, (yt - yb) / 3.2, hw / 2.2)
    faces.setdefault("down", BELLY)
    nd = {k: v for k, v in faces.items() if k != "down"}
    return [box(-hw, yb + c, z0, hw, yt - c, z1, mat, **faces),
            box(-hw + c * 0.35, yt - c, z0, hw - c * 0.35, yt - c * 0.35, z1, mat, **nd),
            box(-hw + c, yt - c * 0.35, z0, hw - c, yt, z1, mat, **nd),
            box(-hw + c * 0.35, yb + c * 0.35, z0, hw - c * 0.35, yb + c, z1, mat, **faces),
            box(-hw + c, yb, z0, hw - c, yb + c * 0.35, z1, mat, **faces)]


def lerp(a, b, t):
    return a + (b - a) * t


def aft_bottom(z):
    """Lower line of the upswept tail: ramp, then cargo door, then tail cone."""
    if z <= BAY_Z1: return 6
    if z <= RAMP_END[1]: return lerp(6, RAMP_END[0], (z - BAY_Z1) / (RAMP_END[1] - BAY_Z1))
    if z <= DOOR_HINGE[1]: return lerp(RAMP_END[0], DOOR_HINGE[0], (z - RAMP_END[1]) / (DOOR_HINGE[1] - RAMP_END[1]))
    return lerp(DOOR_HINGE[0], 80, (z - DOOR_HINGE[1]) / 58)


# ---------------------------------------------------------------- model
def build():
    fus, cockpit, wings, tail, gear, ramp, door, straps = [], [], [], [], [], [], [], []

    # --- nose (radome -> flight deck), solid below the flight deck floor
    for z0, z1, hw, yb, yt in [(-224, -219, 7, 32, 48), (-219, -213, 14, 24, 56), (-213, -206, 20, 17, 62),
                               (-206, -198, 25, 12, 66), (-198, -190, 29, 8, 68)]:
        fus += solid(z0, z1, hw, yb, yt, c=min(6, hw / 2.5), up=HULL)
    fus += [box(-26, 66, -206, 26, 68, -198, DEICE)]                    # radome / hull seam
    fus += solid(-190, -132, HW, 6, 52, c=8)                             # nose-gear bay + under-deck avionics
    fus += solid(-132, BAY_Z0, HW, 6, FLOOR, c=6)                         # forward floor block
    # flight deck shell (hollow above y=52), stepped windscreen
    fus += shell(-182, -132, HW, 50, TOP, floor=False, inner=INTER, c=10, roof=False)
    fus += [box(-HW + 10, TOP - 4, -170, HW - 10, TOP, -132, HULL, down=INTER),
            box(-HW + 3.5, TOP - 10, -170, HW - 3.5, TOP - 6.5, -132, HULL, down=INTER),
            box(-HW + 6, TOP - 6.5, -170, HW - 6, TOP - 4, -132, HULL, down=INTER)]
    # windscreen: frames + glass steps (glass = alpha-0 texels)
    for z0, z1, y0, y1, hw in [(-190, -184, 68, 74, 28), (-184, -177, 74, 81, 30), (-177, -170, 81, 88, 30)]:
        cockpit += [box(-hw, y0, z0, hw, y1, z1, GLASS)]
    cockpit += [box(-29, 66, -191, 29, 68, -189, DARK),                  # sill
                box(-1, 68, -190, 1, 88, -169, DARK)]                   # centre post
    for s in (-1, 1):
        cockpit += [box(s * 13, 68, -190, s * 15, 88, -169, DARK),       # windscreen posts
                    box(s * 28, 68, -190, s * 31, 88, -169, HULL),       # A-pillar
                    box(s * 28.5, 64, -168, s * 32.2, 80, -150, GLASS),  # side windows
                    box(s * 28.3, 64, -150, s * 32.2, 82, -148, DARK),
                    box(s * 28.5, 64, -148, s * 32.2, 78, -138, GLASS),
                    box(s * 28.2, 52, -168, s * 32, 64, -138, HULL, **({"west": INTER} if s > 0 else {"east": INTER})),
                    box(s * 28.2, 80, -168, s * 32, 82, -150, DARK),
                    box(s * 10, 58, -150, s * 20, 76, -147, INTER)]      # seat side armour
    cockpit += [box(-27, 52, -184, 27, 53, -132, WALK),                 # flight deck floor
                box(-26, 53, -190, 26, 64, -182, INTER),                 # instrument panel
                box(-27, 64, -190, 27, 66, -180, DARK),                  # glare shield
                box(-4, 53, -182, 4, 62, -160, INTER),                   # centre console / throttle quadrant
                box(-2.5, 62, -170, 2.5, 64, -164, DARK),
                box(-HW + 4, 52, -133, HW - 4, TOP - 4, -131, INTER)]    # deck rear bulkhead
    for sx in (13, -13):                                                  # pilot (left, +X) and co-pilot
        cockpit += [box(sx - 5, 53, -162, sx + 5, 57, -150, DARK),        # seat pan
                    box(sx - 4.5, 57, -158, sx + 4.5, 58.5, -150, INTER),  # cushion
                    box(sx - 5, 57, -150, sx + 5, 74, -147, DARK),        # back
                    box(sx - 3, 74, -150, sx + 3, 78, -148, DARK),        # headrest
                    stick((sx, 60, -168), (sx, 66, -174), 1, 1)]          # yoke column
    for s in (-1, 1):                                                    # pitot tubes + nose formation lights
        fus += [stick((s * 18, 52, -206), (s * 18, 52, -216), 0.8, 0.8), box(s * 25, 40, -199, s * 25.6 if s > 0 else -25.6, 44, -195, WHITE)]
    fus += [cbox(0, 30, -225, 3, 3, 2, DARK)]                             # radome tip

    # --- cargo bay (hollow), walls 4 px, ceiling at CEIL
    fus += shell(-132, BAY_Z0, HW, 6, TOP, w=4, floor=False, c=10)    # closes the slot behind the flight-deck bulkhead
    for z in range(BAY_Z0, BAY_Z1, 16):
        fus += shell(z, z + 16, HW, 6, TOP, w=4, floor=False, c=10)
    fus += [box(-HW + 4, 6, BAY_Z0, HW - 4, FLOOR, BAY_Z1, BELLY, up=BAY)]  # floor slab
    for x in (-18, -6, 6, 18):                                           # roller tracks
        fus += [box(x - 2, FLOOR, BAY_Z0 + 4, x + 2, FLOOR + 0.6, BAY_Z1, ROLLER)]
    for z in range(BAY_Z0 + 8, BAY_Z1, 24):                              # ceiling frames + wall stringers
        fus += [box(-HW + 4, CEIL - 2, z, HW - 4, CEIL, z + 2, DARK)]
        for s in (-1, 1):
            fus += [box(s * (HW - 4), FLOOR, z, s * (HW - 6), CEIL, z + 2, DARK)]
    for s in (-1, 1):                                                    # troop seat rails, side windows, paratroop doors
        fus += [box(s * (HW - 4), 34, BAY_Z0 + 8, s * (HW - 5.5), 36, BAY_Z1 - 6, DARK),
                box(s * (HW - 0.2), 22, 30, s * (HW + 0.4), 62, 46, DOOR),
                box(s * (HW - 0.2), 60, -112, s * (HW + 0.4), 66, -104, WINDOW),
                box(s * (HW - 0.2), 60, -60, s * (HW + 0.4), 66, -52, WINDOW),
                box(s * (HW - 0.3), 60, 10, s * (HW + 0.4), 66, 18, WINDOW),
                box(s * (HW - 0.2), 26, -120, s * (HW + 0.4), 62, -104, DOOR)]   # forward crew door
    # national star + tail number on the aft fuselage and fin
    for s in (-1, 1):
        fus += [box(s * (HW - 0.2), 44, -90, s * (HW + 0.3), 58, -76, HULL, east=STAR, west=STAR)]

    # --- side sponsons (main gear fairings)
    for s in (-1, 1):
        fus += [box(s * HW, 6, -40, s * 44, 30, 50), box(s * HW, 30, -34, s * 40, 38, 44),
                box(s * HW, 8, -52, s * 40, 26, -40), box(s * HW, 9, 50, s * 39, 24, 64),
                box(s * HW, 7, -58, s * 36, 22, -52), box(s * 44, 10, -34, s * 44.5 if s > 0 else -44.5, 26, 44, DARK),
                box(s * HW, 7, 64, s * 35, 20, 74)]
        fus += [cbox(s * 41, 20, -46, 4, 6, 5, GRILLE)]                  # APU / gtc intake

    # --- aft upswept fuselage (hollow over ramp/door so cargo can exit)
    zs = list(range(BAY_Z1, 226, 8))
    for z0 in zs[:-1]:
        z1 = z0 + 8
        zm = (z0 + z1) / 2
        # each slice takes the fullest outline over its length, so neighbours overlap instead of leaving stair gaps
        yb = aft_bottom(z0) - 1
        yt = TOP if z0 < 150 else lerp(TOP, 84, (z0 - 150) / 76)
        hw = HW if z0 < 110 else lerp(HW, 8, (z0 - 110) / 116)
        if zm < DOOR_HINGE[1]:
            fus += shell(z0, z1, hw, yb, yt, w=4, floor=False, c=min(10, hw / 2))
        else:
            fus += solid(z0, z1, hw, yb, yt, c=min(8, hw / 2.2))
    fus += [cbox(0, 84, 228, 6, 6, 6, DARK)]                              # tail cone cap
    # ramp: slab from hinge to lip, with toes and hydraulic rams
    hy, hz = 8, BAY_Z1
    ramp += [stick((0, hy, hz), (0, RAMP_END[0], RAMP_END[1]), 2 * HW - 9, 3, RAMP),
             box(-HW + 5, hy - 2, hz - 2, HW - 5, hy + 2, hz + 2, DARK)]
    for x in (-18, -6, 6, 18):
        ramp += [stick((x, hy + 2.2, hz + 2), (x, RAMP_END[0] + 1.5, RAMP_END[1] - 1.5), 4, 0.6, ROLLER)]
    for s in (-1, 1):
        ramp += [stick((s * (HW - 6), hy, hz), (s * (HW - 6), RAMP_END[0], RAMP_END[1]), 2, 5, DARK)]
    ramp += [box(-14, RAMP_END[0] - 1, RAMP_END[1] - 2, 14, RAMP_END[0] + 1, RAMP_END[1] + 4, DARK)]  # ramp toes
    door += [stick((0, DOOR_HINGE[0], DOOR_HINGE[1]), (0, RAMP_END[0] + 1, RAMP_END[1] + 1),
                   2 * HW - 12, 3, RAMP),
             box(-HW + 8, DOOR_HINGE[0] - 2, DOOR_HINGE[1] - 2, HW - 8, DOOR_HINGE[0] + 2, DOOR_HINGE[1] + 2, DARK)]

    # --- wing: high mount, tapered outer panels, dorsal fairing
    wings += [box(-40, TOP, -36, 40, TOP + 8, 36), box(-34, TOP + 8, -30, 34, TOP + 11, 30),   # centre box / fairing
              box(-26, TOP + 11, -22, 26, TOP + 13, 20), box(-30, TOP, 36, 30, TOP + 6, 60),   # aft fairing
              cbox(0, TOP + 14, 0, 3, 2, 3, RED)]                                                # beacon
    for s in (-1, 1):
        segs = [(40, 112, -34, 34, 8), (112, 180, -30, 28, 7), (180, 236, -26, 22, 6), (236, 256, -22, 16, 5)]
        for x0, x1, zf, zt, t in segs:
            wings += [box(s * x0, TOP + 1, zf, s * x1, TOP + 1 + t, zt),
                      box(s * x0, TOP + 1.5, zf - 3, s * x1, TOP + t - 0.5, zf, DEICE),          # de-icing boot
                      box(s * x0, TOP + 1.8, zt, s * x1, TOP + 1 + t * 0.55, zt + 8, BELLY)]       # flaps / aileron
            wings += [box(s * (x0 + 6), TOP + 1 + t, zf + 6, s * (x0 + 8), TOP + 1.2 + t, zt - 4, DARK)]  # panel seam
        wings += [box(s * 256, TOP + 2, -20, s * 258, TOP + 6, 14, HULL),
                  cbox(s * 257, TOP + 4, -22, 2, 2, 2, GREEN if s > 0 else RED),                  # nav lights (left red? see note)
                  box(s * 60, TOP + 9, -10, s * 100, TOP + 9.3, 10, WALK)]
        # external fuel tanks between nacelles
        tx = s * 106
        wings += [cbox(tx, TOP - 8, -10, 10, 10, 70), cbox(tx, TOP - 8, -48, 6, 6, 8, HULL), cbox(tx, TOP - 8, 28, 5, 5, 8),
                  cbox(tx, TOP - 2.5, -10, 3, 7, 40, DARK)]   # pylon reaches the wing
    # nacelles
    def nacelle(x, s):
        n = []
        cy = PROP_Y
        for z0, z1, r, yb_ext in [(-92, -84, 8, 0), (-84, -60, 10.5, 6), (-60, 4, 11, 4), (4, 34, 9, 0), (34, 52, 6, 0)]:
            n += [box(x - r, cy - r - yb_ext, z0, x + r, cy + r * 0.8, z1),
                  box(x - r * 0.65, cy - r * 1.3 - yb_ext, z0, x + r * 0.65, cy + r * 1.05, z1)]
        n += [box(x - 5, cy - 19, -86, x + 5, cy - 13, -66, GRILLE),               # chin oil-cooler intake
              box(x + s * 10.5, cy + 2, -10, x + s * 13, cy + 6, 10, SOOT),        # exhaust stack (outboard side)
              box(x - 11.6, cy - 6, -60, x + 11.6, cy - 5, 4, DARK),               # cowl seam
              box(x - 9, cy + 8.8, -84, x + 9, TOP + 1, 30, HULL),                 # pylon into wing
              box(x - 8, cy - 15, -40, x + 8, cy - 14.5, 0, DEICE)]
        return n

    def prop(x):
        p = []
        for z0, z1, r in [(-104, -100, 2), (-100, -96, 4.5), (-96, -92, 6.5)]:
            p += [cbox(x, PROP_Y, (z0 + z1) / 2, r * 2, r * 2, z1 - z0, SPIN),
                  dict(cbox(x, PROP_Y, (z0 + z1) / 2, r * 2, r * 2, z1 - z0 - 0.02, SPIN), pivot=[x, PROP_Y, -98], rotation=[0, 0, 45])]
        for a in (0, 90, 180, 270):
            for y0, y1, w, mat in [(5, 10, 4, DARK), (10, 27, 7, BLADE), (27, 34, 5.5, TIP)]:
                b = box(x - w / 2, PROP_Y + y0, -95.5, x + w / 2, PROP_Y + y1, -94, mat)
                b["pivot"], b["rotation"] = [x, PROP_Y, -95], [0, 12, a]   # 12 deg blade pitch
                p.append(b)
        return p

    nac, props = [], {}
    for i, (s, ex) in enumerate([(1, ENG_X[1]), (1, ENG_X[0]), (-1, ENG_X[0]), (-1, ENG_X[1])]):
        x = s * ex
        nac += nacelle(x, s)
        props[f"prop_{i + 1}"] = (x, prop(x))
    wings += nac

    # --- T-tail: tall fin with dorsal fillet, rudder; horizontal stabiliser at fin root
    for z0, z1, y0, y1 in [(150, 226, 88, 104), (162, 226, 104, 124), (174, 228, 124, 146), (186, 228, 146, 166),
                           (196, 228, 166, 178)]:
        tail += [box(-3, y0, z0, 3, y1, z1)]
    tail += [box(-2.5, 92, 126, 2.5, 96, 150, HULL),                        # dorsal fillet
             box(-3.2, 104, 150, 3.2, 106, 160, DEICE), box(-3.2, 124, 160, 3.2, 126, 172, DEICE),
             box(-2.6, 96, 226, 2.6, 174, 236, BELLY),                       # rudder
             box(-3.5, 178, 204, 3.5, 181, 232, DARK), cbox(0, 182, 230, 2, 2, 2, WHITE)]
    for s in (-1, 1):
        tail += [box(s * 3, 132, 196, s * 3.4, 146, 216, HULL, east=NUM_R if s > 0 else NUM, west=NUM if s > 0 else NUM_R),
                 box(s * 3, 112, 186, s * 3.4, 122, 196, HULL, east=STAR, west=STAR)]
        tail += [box(s * 6, 88, 176, s * 50, 93, 210), box(s * 50, 88, 182, s * 84, 92, 208),
                 box(s * 84, 88.5, 188, s * 100, 91.5, 206),
                 box(s * 6, 88.6, 210, s * 96, 91.6, 222, BELLY),                   # elevators
                 box(s * 6, 89, 172, s * 96, 92, 176, DEICE)]

    # --- landing gear: tandem main wheels in sponsons, twin nose wheels
    for s in (-1, 1):
        for z in (-14, 18):
            gear += wheel(s * 39, 7, z, 6, 6.5)
            gear += [stick((s * 39, 7, z), (s * 39, 18, z), 2.5, 2.5)]
    gear += [stick((0, 6, -176), (0, 20, -176), 2.5, 2.5), stick((0, 10, -174), (0, 18, -166), 1, 1)]
    gear += wheel(-3.5, 6, -176, 4, 5.5) + wheel(3.5, 6, -176, 4, 5.5)

    # --- cargo tie-down straps (Java hides when the bay is empty)
    for z in (-60, -20, 20, 50):
        for s in (-1, 1):
            straps += [stick((s * 24, FLOOR + 0.5, z), (s * 10, 60, z + 6), 1.5, 0.5, RAMP)]
        straps += [box(-25, FLOOR, z - 1.5, -22, FLOOR + 1.5, z + 1.5, DARK), box(22, FLOOR, z - 1.5, 25, FLOOR + 1.5, z + 1.5, DARK)]

    bones = [
        {"name": "root", "pivot": [0, 0, 0]},
        {"name": "fuselage", "parent": "root", "pivot": [0, 40, 0], "cubes": fus},
        {"name": "cockpit", "parent": "fuselage", "pivot": [0, 52, -160], "cubes": cockpit},
        {"name": "wings", "parent": "fuselage", "pivot": [0, TOP, 0], "cubes": wings},
    ]
    for name, (x, cubes) in props.items():
        bones.append({"name": name, "parent": "wings", "pivot": [x, PROP_Y, -98], "cubes": cubes})
    bones += [
        {"name": "tail", "parent": "fuselage", "pivot": [0, 90, 190], "cubes": tail},
        {"name": "ramp", "parent": "fuselage", "pivot": [0, hy, hz], "cubes": ramp},
        {"name": "cargo_door", "parent": "fuselage", "pivot": [0, DOOR_HINGE[0], DOOR_HINGE[1]], "cubes": door},
        {"name": "gear", "parent": "fuselage", "pivot": [0, 8, 0], "cubes": gear},
        {"name": "cargo_straps", "parent": "fuselage", "pivot": [0, FLOOR, 0], "cubes": straps},
    ]
    return bones


RAMP_OPEN = -43      # lip touches the ground (checked in self-test)
DOOR_OPEN = -42      # door swings up into the tail cone


# ---------------------------------------------------------------- texture
DIG = {"0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
       "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "011", "001", "111"],
       "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
       "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "010", "010", "010"],
       "8": ["111", "101", "111", "101", "111"], "9": ["111", "101", "111", "001", "111"]}


def paint():
    px = O.paint_texture()           # light grey HULL/BELLY/RAMP skins, dark, tyres, soot, glass(alpha 0) etc.
    rnd = random.Random(130)

    def put(x, y, c):
        px[y][x] = tuple(max(0, min(255, int(v))) for v in c[:3]) + (255,)

    def fill(m, fn):
        a, b = cell(m)
        for y in range(64):
            for x in range(64):
                put(a + x, b + y, fn(x, y))

    G = (196, 199, 201)              # lighter than the Osprey so faction tints read well
    for m in (HULL,):
        a, b = cell(m)
        for y in range(64):
            for x in range(64):
                r, g, bb, _ = px[b + y][a + x]
                put(a + x, b + y, (r + 12, g + 12, bb + 11))
    fill(BAY, lambda x, y: [74 + rnd.uniform(-4, 4) - (14 if x % 16 == 0 or y % 16 == 0 else 0)
                            - (8 if (x % 16 == 3 and y % 3 == 0) else 0)] * 2 + [70])
    fill(ROLLER, lambda x, y: (52, 54, 56) if x in (0, 3) else ((150, 152, 150) if y % 3 == 0 else (92, 94, 92)))
    fill(DEICE, lambda x, y: [38 + rnd.uniform(-3, 3) + (6 if y % 4 == 0 else 0)] * 3)
    for m, mirror in ((NUM, False), (NUM_R, True)):
        fill(m, lambda x, y: [G[i] + rnd.uniform(-3, 3) for i in range(3)])
        a, b = cell(m)
        for i, ch in enumerate("130"):         # tail number "AF 130": low-vis grey stencil, readable on a 20x14 face
            for r, row in enumerate(DIG[ch]):
                for k, bit in enumerate(row):
                    if bit == "1":
                        u = 3 + i * 5 + k
                        put(a + (19 - u if mirror else u), b + 5 + r, (70, 72, 76))
    # exhaust soot streaks: SOOT cell is already dark; add a soot-tinted wing skin isn't needed since stacks sit on nacelles
    return px


def item_icon():
    """16x16 plan view: long straight wing with 4 engines, fuselage, T-tail."""
    T, D, L, M, B = (0, 0, 0, 0), (60, 62, 66, 255), (200, 203, 206, 255), (150, 154, 158, 255), (70, 100, 125, 255)
    g = [[T] * 16 for _ in range(16)]
    for y in range(1, 15):
        g[y][7] = L; g[y][8] = L
    for y in range(3, 12):
        g[y][6] = M; g[y][9] = M
    g[1][7] = g[1][8] = M; g[2][7] = g[2][8] = B             # nose + windscreen
    for x in range(0, 16):
        g[5][x] = L; g[6][x] = M                              # wing
    for x in (2, 4, 11, 13):
        g[4][x] = D; g[3][x] = D; g[7][x] = D                 # nacelles + props
        g[3][x - 1] = M; g[3][x + 1] = M
    for x in range(4, 12):
        g[13][x] = M                                          # stabiliser
    g[14][7] = g[14][8] = D
    return g


def animations():
    spin = lambda: {"rotation": {"0.0": [0, 0, 0], "0.2": [0, 0, 360]}}
    still = {f"prop_{i}": {"rotation": [0, 0, 0]} for i in range(1, 5)}
    spinning = {f"prop_{i}": spin() for i in range(1, 5)}
    shut = {"ramp": {"rotation": [0, 0, 0]}, "cargo_door": {"rotation": [0, 0, 0]}}
    return {"format_version": "1.8.0", "animations": {
        "animation.c130_hercules.idle": {"loop": True, "bones": {**still, **shut}},
        "animation.c130_hercules.fly": {"loop": True, "animation_length": 0.2, "bones": {**spinning, **shut}},
        # looping so props keep spinning; ramp/door are held fully open for the whole loop
        "animation.c130_hercules.ramp_open": {"loop": True, "animation_length": 0.2, "bones": {
            **spinning, "ramp": {"rotation": [RAMP_OPEN, 0, 0]}, "cargo_door": {"rotation": [DOOR_OPEN, 0, 0]}}}}}


def self_test(bones):
    """Open ramp lip must reach ~ground; open door must clear the bay height."""
    hy, hz = 8, BAY_Z1
    lip = O.about([0, RAMP_END[0], RAMP_END[1]], [0, hy, hz], [RAMP_OPEN, 0, 0])
    assert -4 <= lip[1] <= 2, lip
    low = O.about([0, RAMP_END[0], RAMP_END[1]], [0, DOOR_HINGE[0], DOOR_HINGE[1]], [DOOR_OPEN, 0, 0])
    assert low[1] > 66, low   # Titan (kneeling ~4.5 blocks) walks out under it at the ramp
    return lip, low


def main():
    bones = O.assign_uv(build())
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{"description": {
        "identifier": "geometry.c130_hercules", "texture_width": TEX, "texture_height": TEX,
        "visible_bounds_width": 36, "visible_bounds_height": 14, "visible_bounds_offset": [0, 6, 0]},
        "bones": bones}]}
    anim = animations()
    cubes = validate(json.loads(json.dumps(geo)), anim)
    lip, low = self_test(bones)
    for p in ("geo/c130_hercules.geo.json", "animations/c130_hercules.animation.json"):
        os.makedirs(os.path.dirname(os.path.join(ROOT, p)), exist_ok=True)
    with open(os.path.join(ROOT, "geo", "c130_hercules.geo.json"), "w") as f: json.dump(geo, f, indent=1)
    with open(os.path.join(ROOT, "animations", "c130_hercules.animation.json"), "w") as f: json.dump(anim, f, indent=2)
    tex = paint()
    save_png(os.path.join(ROOT, "textures", "entity", "transport", "c130_hercules.png"), tex)
    save_png(os.path.join(ROOT, "textures", "item", "c130_hercules.png"), item_icon())
    pts = [(c["origin"][i], c["origin"][i] + c["size"][i]) for b in bones for c in b.get("cubes", []) for i in range(3)]
    ext = [(min(c["origin"][i] for b in bones for c in b.get("cubes", [])),
            max(c["origin"][i] + c["size"][i] for b in bones for c in b.get("cubes", []))) for i in range(3)]
    print(f"cubes={cubes} bones={[b['name'] for b in bones]} extents(px)={ext} ramp_lip={lip} door_low={low}")
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        kw = dict(W=900, H=420, scale=1.45)
        a = render(bones, tex, {}, 35, -18, **kw)
        b = render(bones, tex, {"ramp": [RAMP_OPEN, 0, 0], "cargo_door": [DOOR_OPEN, 0, 0]}, -140, -12, **kw)
        c = render(bones, tex, {}, 90, 0, **kw)
        d = render(bones, tex, {}, 150, -10, W=900, H=420, scale=2.6)          # nose close-up
        e = render(bones, tex, {"ramp": [RAMP_OPEN, 0, 0], "cargo_door": [DOOR_OPEN, 0, 0]}, 180, -8, W=900, H=420, scale=2.0)
        a += d + e
        save_png(out, a + b + c)
        print("preview", out)


if __name__ == "__main__":
    main()
