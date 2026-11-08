"""Modular armour for the mass-production Knightmare frame: 8 archetypes x (head, chest, arms, forearms, thighs, shins,
feet, skirt). Thin faceted cover plates (5/6-sided or a single diamond) bolt onto the bare frame; every archetype has a
different outline: infantry hex plates, siege slabs, samurai lames + horns, aero swept blades, scrap mismatched patches,
stealth facets, sovereign gilded flares, expedition tool pods. Bones keep the parent pivot so animations carry them."""
from mgen import *
from mgen import _net, poly

LIMBS = [("arm", "Arm1"), ("forearm", "Arm2"), ("leg", "Leg3"), ("shin", "Leg2"), ("foot", "Foot")]
B = "box"

# (kind, out, up, back, size, mat, face, rot) per limb piece, relative to the segment midpoint; mirrored to the left side
ARM = {
    "infantry": [("hex", 5, .5, 0, (2, 14.5, 9.6), "P", "x", None), (B, 0, 6.4, 0, (8.6, 1.6, 9.2), "A", None, None)],
    "siege": [(B, .4, 0, 0, (9.6, 14, 10), "P", None, None), (B, 6, 2, 0, (3, 11, 9), "S", None, None), (B, .4, 7.6, 0, (10.2, 1.6, 10.6), "A", None, None)],
    "samurai": [(B, 3.4 + .5 * i, 5 - 3.6 * i, 0, (8.4 - .6 * i, 2.8, 10.6 - .8 * i), "P" if i % 2 == 0 else "S", None, None) for i in range(4)]
               + [("hex", 5.4, 0, 0, (1.4, 10, 8), "A", "x", None)],
    "aero": [("hex", 4.8, .5, 0, (1.4, 15, 7.6), "P", "x", None), (B, 6.2, 2, 3, (.8, 9, 8), "A", None, None)],
    "scrap": [(B, 5, 3, -1.5, (2.6, 7, 5), "S", None, [0, 14, 0]), (B, 5, -4, 2, (2.2, 6, 2.2), "J", None, None), (B, 0, 2, -4.6, (7.6, 6, 1.4), "A", None, [0, 0, 6])],
    "stealth": [("hex", 4.8, .5, 0, (1.2, 15, 9.8), "S", "x", None), ("dia", 5.6, -1, 0, (1.2, 7, 7), "P", "x", None)],
    "sovereign": [("hex", 5, .5, 0, (2, 14, 9.8), "A", "x", None), (B, .4, 7.4, 0, (9, 1.6, 10), "A", None, None), (B, .4, -6, 0, (8.6, 1.6, 9), "A", None, None)],
    "expedition": [(B, 5.2, 0, 1.4, (3.4, 9, 5), "J", None, None), (B, 7, 0, 1.4, (1.2, 4, 2.4), "L", None, None), ("hex", 4.2, 2, -1, (1.6, 10, 7), "S", "x", None)],
}
FOREARM = {
    "infantry": [("hex", 5, 2, 0, (2, 13, 9), "P", "x", None)],
    "siege": [(B, .4, 3, 0, (9, 14, 9.6), "P", None, None), (B, 6, 3, 0, (3, 11, 8), "S", None, None)],
    "samurai": [(B, .4, 5, 0, (8.4, 3, 9.4), "S", None, None), (B, .4, .4, 0, (9, 3, 10), "P", None, None), (B, .4, -4.4, 0, (8.4, 3, 9.4), "S", None, None)],
    "aero": [("hex", 4.8, 2, 0, (1.2, 13, 7.4), "A", "x", None)],
    "scrap": [(B, 4.8, 2, 2, (2.4, 9, 4.4), "S", None, [0, 10, 0]), (B, 5.4, -3, -2, (2, 5, 2), "J", None, None)],
    "stealth": [("hex", 4.6, 2, 0, (1.2, 14, 9), "S", "x", None)],
    "sovereign": [("hex", 5, 2, 0, (1.8, 13, 9), "A", "x", None), (B, .4, 7.6, 0, (8.6, 1.4, 9.6), "A", None, None)],
    "expedition": [(B, 5.2, 2, 1, (3, 9, 5), "J", None, None), (B, 7, 2, 1, (1.2, 4, 2.4), "L", None, None)],
}
THIGH = {
    "infantry": [("hex", 6.4, 1, 0, (2, 15, 11.6), "P", "x", None)],
    "siege": [(B, 0, .6, 0, (10.6, 14, 12), "P", None, None), (B, 6.6, 1, 0, (3, 11, 10.4), "S", None, None), (B, 0, 7.8, 0, (11.2, 1.6, 12.6), "A", None, None)],
    "samurai": [(B, 0, 5 - 4.2 * i, -6 - .3 * i, (9 - .6 * i, 3.4, 2), "P" if i % 2 == 0 else "S", None, None) for i in range(3)],
    "aero": [("hex", 6.2, 2, 2, (1.2, 13, 8), "A", "x", None), ("hex", 6, 1, 0, (1.4, 15, 10.6), "P", "x", None)],
    "scrap": [(B, 6.4, 3, 3, (2.4, 6, 2.4), "J", None, None), (B, 6.4, -2, -2, (2.6, 6, 5), "S", None, [0, 14, 0])],
    "stealth": [("hex", 6.2, 1, 0, (1.2, 15, 11), "S", "x", None), ("dia", 0, 3, -6, (7, 7, 1.4), "P", "z", None)],
    "sovereign": [("hex", 6.4, 1, 0, (1.8, 15, 11), "A", "x", None)],
    "expedition": [(B, 6.8, 1, 0, (3.2, 8, 6), "J", None, None), (B, 6.8, -5, 2, (2, 4, 4), "A", None, None)],
}
SHIN = {
    "infantry": [("hex", 6, 1, .5, (2, 16, 9.8), "P", "x", None)],
    "siege": [(B, 0, 0, .2, (10, 16, 10.6), "P", None, None), (B, 6.6, 0, 0, (3, 12, 9), "S", None, None)],
    "samurai": [(B, 0, .5, -5.8, (7, 13, 1.6), "A", None, None), ("hex", 6, 1, .5, (1.6, 15, 9.4), "P", "x", None)],
    "aero": [("hex", 6, 2, 2, (1, 12, 8), "A", "x", None), ("hex", 5.6, 1, .5, (1.4, 16, 9.4), "P", "x", None)],
    "scrap": [(B, 6.2, -2, -2, (2.6, 6, 5), "S", None, [0, 14, 0]), (B, 6, 3, 2, (2.4, 6, 2.4), "J", None, None)],
    "stealth": [("hex", 5.6, 1, .5, (1.2, 16, 10), "S", "x", None)],
    "sovereign": [("hex", 6, 1, .5, (1.8, 16, 9.8), "A", "x", None), (B, 0, 8.4, 0, (9, 1.4, 10), "A", None, None)],
    "expedition": [(B, 6.4, 0, 0, (2.6, 8, 5.4), "A", None, None), ("hex", 5.4, 3, -1, (1.4, 10, 7), "S", "x", None)],
}
TABLES = {"arm": (ARM, ("Arm1", "Arm2")), "forearm": (FOREARM, ("Arm2", "Hand")), "leg": (THIGH, ("Leg3", "Leg2")), "shin": (SHIN, ("Leg2", "Leg1"))}


def armor(m, archs):
    for a in archs:
        m.add_bone(f"armor_head_{a}", "doorUp")
        m.add_bone(f"armor_chest_{a}", "body3")
        m.add_bone(f"armor_skirt_{a}", "body1")
        for slot, suffix in LIMBS:
            for side in ("right", "left"):
                m.add_bone(f"armor_{side}_{slot}_{a}", f"{side}{suffix}")
        head(m, a); chest(m, a); skirt(m, a); feet(m, a)
        for slot, (tab, (p, c)) in TABLES.items():
            for kind, out, up, back, size, mat, face, rot in tab[a]:
                bone, org = f"armor_right_{slot}_{a}", (f"right{p}", f"right{c}")
                out *= 1.3
                if kind == B: lpair(m, bone, org, out, up, back, size, mat, rot, arch=a)
                else: poly(m, bone, org, out, up, back, size, mat, face, kind, arch=a)
        pauldron(m, a)
        shift(m, f"armor_chest_{a}", 0, 0, -3); shift(m, f"armor_head_{a}", 0, -1, -1.2)


def head(m, a):
    b = f"armor_head_{a}"
    C = lambda c, s, mat="P", rot=None: m.cube(b, c, s, mat, rot, arch=a)
    S = lambda c, s, mat="P", rot=None: sym(m, b, c, s, mat, rot, arch=a)
    if a == "infantry":
        C((0, 114.8, -1.2), (11.8, 3, 12.6)); C((0, 109.6, 5.4), (11.4, 8, 2.2), "S"); C((0, 117.4, -1.2), (2, 2.4, 10), "A")
        poly(m, b, (0, 109.6, -1.4), 7.8, 0, 0, (1.6, 7, 8), "S", "x", "hex", arch=a)
    elif a == "siege":
        C((0, 114.8, -1.4), (13.6, 4, 14)); C((0, 113.6, -9.2), (13, 2.6, 3.6), "S"); S((7.6, 109.4, -1.4), (3, 8, 9), "S")
        C((0, 105.2, -7.4), (9, 4, 4), "S"); S((5.2, 111.6, -9.8), (2.4, 2.4, 1.2), "E")
    elif a == "samurai":
        C((0, 114.8, -1.4), (12.4, 3.4, 13.4)); C((0, 106.8, 3.6), (17, 2.4, 14), "P", [8, 0, 0])
        poly(m, b, (0, 111, -3.4), 8.6, 0, 0, (1.6, 8, 9), "S", "x", "hex", arch=a)
        S((3.4, 121.4, -7), (1.2, 10, 2), "A", [0, 0, 34]); C((0, 118.4, -8.4), (3, 3, 1), "A")
    elif a == "aero":
        C((0, 114.8, -1.4), (11.8, 2.8, 12.6)); C((0, 111, -10.8), (6, 4.4, 6), "P", [-10, 0, 0])
        S((8.4, 113.4, 2.6), (7, .8, 8), "A", [0, 25, 0]); C((0, 118, 2), (1.2, 4, 9), "A", [18, 0, 0])
    elif a == "scrap":
        C((-1, 114.8, -1.8), (11.8, 3, 12.6), "S", [0, 0, 4]); C((5.6, 108.6, -8.2), (4.6, 5, 2.6), "S"); C((7.2, 114, 2), (2, 9, 2.2), "J"); C((7.2, 119, 2), (3, 1.4, 3), "M")
    elif a == "stealth":
        C((0, 116.4, -1), (10, 2, 13), "P", [10, 0, 0]); poly(m, b, (0, 110, -1.4), 7.4, 0, 0, (1.4, 8, 11), "S", "x", "hex", arch=a)
        C((0, 107.2, -8), (5.6, 4, 3.4), "S", [28, 0, 0]); C((0, 112, -10.6), (8, 1.2, .6), "L")
    elif a == "sovereign":
        C((0, 114.8, -1.2), (12.2, 1.8, 13.4), "A")
        for i, x in enumerate((-5, -2.5, 0, 2.5, 5)):
            h = 5 + (4 if i == 2 else 2 if i in (1, 3) else 0); C((x, 116 + h / 2, -1.2), (1.8, h, 1.8), "A")
        C((0, 113.4, -8.6), (2.4, 2.4, 1.2), "R"); S((7.2, 109.4, -1.4), (1.2, 6, 8), "A")
    elif a == "expedition":
        S((4.4, 113.6, -8.6), (3.6, 3.6, 2.4), "L"); S((7.4, 109, -1.8), (2.6, 5, 5), "S"); C((7.4, 116, 3), (1.4, 10, 1.4), "J"); C((0, 114.8, -1.4), (11.4, 2.6, 12.2))


def chest(m, a):
    b = f"armor_chest_{a}"
    C = lambda c, s, mat="P", rot=None: m.cube(b, c, s, mat, rot, arch=a)
    S = lambda c, s, mat="P", rot=None: sym(m, b, c, s, mat, rot, arch=a)
    PL = lambda c, s, kind, mat="P", face="z": poly(m, b, c, 0, 0, 0, s, mat, face, kind, False, a)
    if a == "infantry":
        PL((0, 96, -6.8), (19, 14, 2.4), "pent"); S((13.2, 95, 4), (1.6, 8, 12), "A")
    elif a == "siege":
        C((0, 96.4, -7), (23, 13, 3.4)); C((0, 104.2, 4.4), (27, 3, 17), "A"); S((8, 105, 12), (5, 3, 8), "V")
    elif a == "samurai":
        for i in range(4): C((0, 99.4 - i * 3.2, -6.4 - (i % 2) * .4), (21 - i, 2.8, 1.6), "S" if i % 2 else "P")
        C((0, 99, -7.4), (4, 4, .8), "A"); S((13.8, 104, 3), (3, 1.6, 14), "A")
    elif a == "aero":
        PL((0, 96, -6.4), (17, 13, 2), "pent"); S((17, 100, 12), (9, .8, 6), "A", [0, 22, 0])
    elif a == "scrap":
        C((-5, 99, -6.6), (9, 7, 2), "S", [0, 0, -8]); C((6, 93, -6), (7, 8, 1.8), "A", [0, 0, 6])
        S((14, 105.4, 11), (2.2, 8, 2.2), "J"); S((14, 110, 11), (3.2, 1.6, 3.2), "M")
    elif a == "stealth":
        PL((0, 95.6, -6.6), (18, 11, 1.6), "hex", "S")
        for sx in (-1, 1): PL((sx * 11, 99, -5.4), (6, 6, 1.4), "dia", "P")
        C((0, 96, -7.6), (14, .8, .8), "L")
    elif a == "sovereign":
        PL((0, 96, -6.8), (19, 14, 2.4), "pent"); C((0, 101.6, -7.4), (18, 1.2, 1), "A"); C((0, 91.8, -7.4), (18, 1.2, 1), "A")
        C((0, 96, -8), (5, 5, 1), "C"); S((15, 104.4, 8), (6, 3, 14), "A")
    elif a == "expedition":
        S((12.8, 94, -4.6), (6, 6, 3.2), "S"); S((12.8, 94, -6.4), (4, 3, 1), "A"); C((0, 106.6, 12), (16, 2.2, 3), "J")


def skirt(m, a):
    b = f"armor_skirt_{a}"
    C = lambda c, s, mat="P", rot=None: m.cube(b, c, s, mat, rot, arch=a)
    S = lambda c, s, mat="P", rot=None: sym(m, b, c, s, mat, rot, arch=a)
    C((0, 55.6, -3.2), (13, 9.6, 2), "P", [14, 0, 0]); C((0, 55.8, 17), (12, 8.4, 2), "S", [-12, 0, 0])
    if a == "samurai":
        for i in range(3): S((12 + i * .6, 52.8 - i * 3.6, 7.5), (2.2, 3.4, 14), "S" if i % 2 else "P")
    elif a == "siege": S((13, 55, 7.5), (2.8, 8, 14), "S")
    elif a == "sovereign": C((0, 51.4, -4), (12, 1.4, 2), "A")
    elif a == "expedition": S((12.4, 55, 7.5), (3.6, 6, 5), "A")
    elif a == "scrap": C((2, 51.6, -4.4), (6, 3, 1.6), "J", [14, 0, 14])
    elif a == "aero": C((0, 53, 19), (10, 1.2, 8), "A", [-14, 0, 0])
    elif a == "stealth": poly(m, b, (0, 53.4, -4), 0, 0, 0, (9, 8, 1.6), "S", "z", "pent", False, a)


def feet(m, a):
    for sx in (-1, 1):
        f = f"armor_{'right' if sx < 0 else 'left'}_foot_{a}"; X = sx * 14.8
        m.cube(f, (X, 5, 8), (9.6, 8, 9.4), "P", arch=a)                               # heel cuff
        m.cube(f, (X, 7.6, 1.6), (9.4, 1.8, 10), "S", arch=a)                          # instep
        if a == "siege": m.cube(f, (X, 4.4, -8.2), (9.6, 5, 3.6), "S", arch=a)
        elif a == "aero": m.cube(f, (X, 4.6, 15), (5, 1, 8), "A", [-10, 0, 0], arch=a)
        elif a in ("sovereign", "samurai"): m.cube(f, (X, 1.2, -6.8), (9.6, 1.6, 8), "A", arch=a)
        elif a == "stealth": poly(m, f, (X, 5, 10.8), 0, 0, 0, (7, 7, 1.6), "S", "z", "dia", False, a)


def level(m, bone):
    """File rotation that cancels the bone chain's tilt so a cube stays world-aligned."""
    import math
    R = _net(m, bone).T   # rmat(r) = Rz Ry Rx with angles (-x, +y, -z)
    ay = -math.asin(max(-1, min(1, R[2, 0]))); az = math.atan2(R[1, 0], R[0, 0]); ax = math.atan2(R[2, 1], R[2, 2])
    return [-math.degrees(ax), math.degrees(ay), -math.degrees(az)]


def pauldron(m, a):
    """Extra, world-level shoulder silhouette per archetype (rides the arm bone, stays level)."""
    for sx in (-1, 1):
        b = f"armor_{'right' if sx < 0 else 'left'}_arm_{a}"

        def L(c, s, mat="P", rx=0):
            r = level(m, b)
            m.cube(b, (sx * c[0], c[1], c[2]), s, mat, [r[0] + rx, r[1], r[2]], arch=a)
        if a == "infantry": L((26.6, 108.6, 10.7), (6, 1.6, 15), "A")
        elif a == "siege": L((31, 99, 10.7), (6, 22, 21)); L((34.6, 99, 10.7), (1.4, 16, 15), "S"); L((31, 111, 10.7), (6, 2, 15), "A")
        elif a == "samurai":
            for i in range(3): L((30 + i * 1.4, 104 - i * 3.6, 10.7), (3, 3.2, 17 - i * 1.4), "P" if i % 2 == 0 else "S")
        elif a == "aero": L((26.6, 110, 10.7), (5, .9, 15), "A"); L((26.6, 105, 2), (5, 10, 1), "A")
        elif a == "scrap":
            if sx > 0: L((29, 105, 8), (9, 8, 11), "S")
            else: L((27, 104, 13), (6, 5, 8), "S")
            L((31, 100, 13), (3, 10, 3), "J")
        elif a == "stealth": L((29.4, 104, 10.7), (6, 6, 15), "S"); L((31.6, 98, 10.7), (2, 8, 13), "S")
        elif a == "sovereign": L((30, 102, 10.7), (3, 16, 17), "A"); L((26.6, 109.4, 10.7), (5, 2.6, 13), "A")
        elif a == "expedition": L((26.6, 105, 10.7), (8, 9, 9), "S"); L((26.6, 105, 10.7), (8, 9, 9), "S", 45); L((26.6, 105, 10.7), (8.6, 2, 2), "A")


def shift(m, bone, dx, dy, dz):
    for c in m.bones[bone]["cubes"]:
        c["origin"] = [round(c["origin"][0] + dx, 3), round(c["origin"][1] + dy, 3), round(c["origin"][2] + dz, 3)]
        if "pivot" in c: c["pivot"] = [c["pivot"][0] + dx, c["pivot"][1] + dy, c["pivot"][2] + dz]
