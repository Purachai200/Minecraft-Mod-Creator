"""MP-05 Exo Frame: a mobile-suit inner frame (Gundam / Titanfall proportions) on the Trooper skeleton, with
bolt-on armour for all 8 armour archetypes (TitanArmorArchetype). Builds geo/exo_frame_titan.geo.json + 9
frame colour schemes.

Bare it is the inner frame: small twin-eyed head, V-tapered chest core, segmented waist, ball joints, sculpted
limb frames and a thruster backpack with saber hilts. Each armour piece is two bones:
  armor_<slot>_<archetype>        main plates, painted a light neutral that TitanRenderer tints with the theme
  armor_<slot>_<archetype>_trim   accents (V-fins, vents, soles, stripes) that keep their own colours
Slots: head, chest, left/right_arm (pauldron), left/right_forearm, skirt, left/right_leg (thigh),
left/right_shin, left/right_foot. TitanModel shows them per worn slot (skirt and feet go with the legs).

Arm bones rest turned 180 degrees about y (see build_trooper_assets.REST), so arm armour is authored where it
should end up and flipped about the shoulder axis by arm(). Coordinates: px, front -Z, the mech's left +X.

Run from the repo root:  python3 scratch/build_exo_frame_assets.py
"""
import math
import build_trooper_assets as T
from build_trooper_assets import C, mirror

B, hub, piston, hose, fist, late, ball = T.B, T.hub, T.piston, T.hose, T.fist, T.late, T.ball

SHOULDER_X, SHOULDER_Z = -24.4, 10.7   # right arm1 pivot: arm armour flips about this vertical axis

# Accent colours (trim bones are not tinted)
T.FIXED.update({"armor": (232, 234, 230),  # clean plate: outline and highlight only, no rivet grid (tinted per theme)
                "white": (228, 230, 226), "blue": (44, 74, 168), "red": (188, 40, 38), "yellow": (236, 192, 40),
                "gold": (214, 168, 52), "orange": (226, 120, 30), "purple": (96, 60, 150),
                "cyan": (40, 230, 255)})


# ---------------------------------------------------------------- primitives

def slab(x0, x1, a, b, t, m):
    """Plate spanning x0..x1 whose centre line runs from a=(y, z) to b=(y, z), t thick."""
    (ya, za), (yb, zb) = a, b
    length = math.hypot(yb - ya, zb - za)
    ym, zm = (ya + yb) / 2, (za + zb) / 2
    ang = math.degrees(math.atan2(yb - ya, zb - za))
    ang = ang - 180 if ang > 90 else ang + 180 if ang < -90 else ang
    return C([x0, ym - t / 2, zm - length / 2], [x1 - x0, t, length], m,
             rot=[round(ang, 2), 0, 0], piv=[(x0 + x1) / 2, ym, zm])


def tilt(c, rz=0, rx=0, ry=0):
    """Turns a cube about its own centre."""
    o, s = c["o"], c["s"]
    c["rot"], c["piv"] = [rx, ry, rz], [o[0] + s[0] / 2, o[1] + s[1] / 2, o[2] + s[2] / 2]
    return c


def bar(a, b, w, m):
    """Square bar from point a to point b (both (x, y, z)) in the x-y plane at a's z: fins, horns, V-fins."""
    (xa, ya, za), (xb, yb, _) = a, b
    length = math.hypot(xb - xa, yb - ya)
    xm, ym = (xa + xb) / 2, (ya + yb) / 2
    ang = math.degrees(math.atan2(yb - ya, xb - xa))
    # GeckoLib turns a cube's z rotation the opposite way to atan2 here (checked in game: V-fins came out as ^)
    return C([xm - length / 2, ym - w / 2, za - w / 2], [length, w, w], m, rot=[0, 0, round(-ang, 2)], piv=[xm, ym, za])


def ycyl(cx, y0, y1, cz, d, m):
    o, s = [cx - d / 2, y0, cz - d / 2], [d, y1 - y0, d]
    return late([C(o, s, m), C(o, s, m, rot=[0, 45, 0], piv=[cx, y0, cz])])


def sym(*cubes):
    """Right-side cubes plus their mirror (for centred pieces like the chest and head)."""
    return list(cubes) + mirror(list(cubes))


FOREARM_X, FOREARM_Z = -23.4, 10.7
def arm_fore(cubes):
    out = []
    for c in cubes:
        m = dict(c)
        m["o"] = [2 * FOREARM_X - (c["o"][0] + c["s"][0]), c["o"][1], 2 * FOREARM_Z - (c["o"][2] + c["s"][2])]
        if "rot" in c:
            m["rot"] = [-c["rot"][0], c["rot"][1], -c["rot"][2]]
        if "piv" in c:
            m["piv"] = [2 * FOREARM_X - c["piv"][0], c["piv"][1], 2 * FOREARM_Z - c["piv"][2]]
        out.append(m)
    return out

def arm(cubes):
    """Authored where it should sit on the right arm; pre-turned 180 degrees about the shoulder's vertical axis
    so the arm bone's rest turn puts it back."""
    out = []
    for c in cubes:
        m = dict(c)
        m["o"] = [2 * SHOULDER_X - (c["o"][0] + c["s"][0]), c["o"][1], 2 * SHOULDER_Z - (c["o"][2] + c["s"][2])]
        if "rot" in c:
            m["rot"] = [-c["rot"][0], c["rot"][1], -c["rot"][2]]
            m["piv"] = [2 * SHOULDER_X - c["piv"][0], c["piv"][1], 2 * SHOULDER_Z - c["piv"][2]]
        out.append(m)
    return out


# ================================================================ inner frame (bare)

RIGHT_ARM1 = ball(-24.4, 94.8, 10.7, 10, "metal") + [
    B(-28.5, -20.5, 76, 90, 6.5, 15, "dark"),                                 # upper arm frame
    B(-31, -18, 90, 102, 1, 20, "paint2"),                                     # mass-production shoulder pauldron
    B(-31.5, -17.5, 98, 101, 3, 18, "dark"),                                  # pauldron top ridge
    B(-29, -20, 82, 86, 6, 15.5, "paint2"),                                   # frame band
    B(-27, -22, 73, 77, 7.5, 14, "metal"),
] + piston(-24.4, 88, 76, 16.5, w=2.2) + hub(-24, 72.5, 10.7, 12, 8.5, "metal")

RIGHT_ARM2 = [
    B(-29, -19.5, 54, 70, 6, 15.5, "dark"),                                   # forearm frame
    B(-31, -17.5, 52, 68, 3, 18.5, "paint2"),                                 # mass-production forearm gauntlet plate
    B(-31.5, -17, 58, 64, 4, 18, "dark"),                                     # gauntlet side block
    B(-28.5, -20, 49, 54, 6.5, 15, "metal"),                                  # wrist joint
] + piston(-24.2, 68, 55, 4.6, w=2.2)

RIGHT_HAND = fist(-28.3, 46.8, 6) + hub(-23.3, 46.8, 11.5, 10, 5)

RIGHT_LEG3 = ball(-14.5, 57, 7, 11, "metal") + [B(-18, -11, 48, 58, 3, 11, "dark")]

RIGHT_LEG2 = [
    B(-19.5, -9.5, 30, 48, -1.5, 9.5, "dark"),                                # thigh frame
    B(-20, -9, 38, 42, -2, 10, "paint2"),
    B(-18.5, -10.5, 26, 30, -0.5, 8.5, "metal"),
] + piston(-14.5, 46, 31, -3, w=2.4)

RIGHT_LEG1 = hub(-14.5, 23, 3, 14, 9, "metal") + [
    B(-19, -10, 9, 21, -2, 8, "dark"),                                        # shin frame
    B(-19.5, -9.5, 14, 17, -2.5, 8.5, "paint2"),
    B(-18, -11, 10, 20, 8, 12.5, "metal"),                                    # calf actuator housing
] + piston(-14.5, 21, 10, 13.5, w=2.2)

RIGHT_FOOT = ball(-14.5, 7, -1, 7, "metal") + [
    B(-20, -9, 0, 4, -16, 9, "dark"),                                         # foot frame
    B(-19.5, -9.5, 0, 4.5, -20, -16, "metal"),                                # toe
    B(-19, -10, 0, 5, 9, 12, "metal"),                                        # heel
]

CHEST_CORE = [
    B(-9, 9, 82, 96, -3, 13, "dark"),                                         # lower chest frame
    B(-13, 13, 96, 108, -4, 14, "dark"),                                      # upper chest frame (V taper)
] + sym(tilt(B(-14, -9, 88, 100, -2, 12, "paint2"), rz=-14)) + [              # rib frame flaring to the shoulders
    B(-13.5, 13.5, 101, 103, -4.5, 14.5, "paint2"),
    B(-21, -15, 94, 103, 5, 15, "metal"), B(15, 21, 94, 103, 5, 15, "metal"),  # shoulder connectors
    B(-3, 3, 106, 111, 0, 6, "metal"),                                        # neck
    B(-8, 8, 88, 106, 15, 21, "dark"),                                        # backpack core
    B(-7, -2, 82, 89, 16, 21, "metal"), B(2, 7, 82, 89, 16, 21, "metal"),     # main thrusters
    B(-6, -3, 82, 83, 17, 20, "glow"), B(3, 6, 82, 83, 17, 20, "glow"),
    slab(-7, -5, (106, 18), (115, 23), 2, "white"), slab(5, 7, (106, 18), (115, 23), 2, "white"),  # saber hilts
]

FRONT = [  # upper chest / mass-production armored cockpit hatch
    slab(-12, 12, (94, -9.5), (107, -6), 3.5, "paint2"),                      # heavy sloped hatch plate
    B(-10.5, 10.5, 94, 102, -9.2, -5, "dark"),
    B(-8, -3, 98, 104, -9.8, -9.0, "vent"), B(3, 8, 98, 104, -9.8, -9.0, "vent"),  # dual chest cooling intakes
]
# The bare head is its own bone so a variant wearing a full titan cockpit can hide it (TitanModel: frame_head)
# Mass-Production Grunt Tactical Head & Visor (ดุดัน สไตล์หุ่นทหารราบมาตรฐาน)
FRAME_HEAD = [
    B(-6, 6, 110, 118, -4, 6, "paint2"),                                      # main armored helmet
    B(-5.5, 5.5, 115, 118.5, -6, 5, "paint2"),                                # sloped brow brow-guard
    B(-6.5, -5.0, 109, 116, -2, 4, "dark"), B(5.0, 6.5, 109, 116, -2, 4, "dark"),  # armored ear communications pods
    B(-4, 4, 108, 111, -5.5, -2, "dark"),                                     # chin rebreather / intake
    B(-0.8, 0.8, 118, 124, 0, 2, "steel"),                                    # tactical blade comms antenna
]

EYES = [B(-4.2, 4.2, 112.5, 114.5, -6.1, -5.4, "visor")]                     # unified tactical combat visor slit

LOWER_FRONT = [B(-9, 9, 84, 94, -8, -4, "paint2"), B(-7, 7, 86, 88, -8.4, -8, "vent"), B(-7, 7, 90, 92, -8.4, -8, "vent")]

WAIST = piston(-7, 82, 66, 7, w=2.2) + hose(-3, 80, 66, 14, 1.5)


# ================================================================ armour
# Every archetype returns {slot: (main cubes, trim cubes)} for the right side / centre, authored in place.
# Slots: head, chest, paul, fore, skirt, thigh, shin, foot. Main cubes use "paint" (tinted); trim keeps colour.

def base_head(fin="yellow", crest="red"):
    main = [B(-6, 6, 116, 120, -5, 6, "paint")] + sym(B(-6.8, -5, 110, 118, -4.5, 5.5, "paint")) + [
        B(-5, 5, 110, 118, 5, 7, "paint"), slab(-6, 6, (117.5, -6.5), (119.5, -3), 1.6, "paint")]
    trim = sym(bar((-0.5, 118.6, -6.4), (-11, 125.5, -6.4), 1.6, fin)) + [
        B(-1.6, 1.6, 117.5, 121, -7, -5, crest), B(-2, 2, 108.5, 110.5, -5.6, -3.5, crest)]
    return main, trim


def base_chest(vent="yellow", hatch="blue"):
    main = sym(tilt(B(-15, -2.5, 96, 107, -10, -4, "paint"), ry=-12),         # pec plates, angled outward
               tilt(B(-17, -14.5, 88, 104, -6, 10, "paint"), rz=-6),          # side ribs
               B(-6, -0.6, 89.5, 95, -8.6, -4, "paint"), B(-5.4, -0.6, 84, 89, -8.2, -4, "paint")) + [  # abs
        slab(-13, 13, (106.5, -9), (110, -2), 2, "paint")]                     # collar
    trim = sym(B(-13, -9, 100, 106, -10.9, -10.2, vent), B(-12.5, -9.5, 100.5, 105.5, -11.2, -10.9, "vent")) + [
        B(-3, 3, 95, 106, -10.4, -8.5, hatch)]                                 # cockpit block between the pecs
    return main, trim


def base_paul(stripe="red", edge="white", bulk=0):
    main = [B(-31.5 - bulk, -18.5, 90, 102 + bulk / 2, 3 - bulk / 2, 18.5 + bulk / 2, "paint"),
            tilt(B(-31.5 - bulk, -18.5, 101.5 + bulk / 2, 104 + bulk / 2, 3 - bulk / 2, 18.5 + bulk / 2, "paint"), rz=10)]
    trim = [B(-32.1 - bulk, -31.4 - bulk, 92, 100, 6, 15.5, stripe), B(-31.5 - bulk, -18.5, 89, 90.5, 3.4 - bulk / 2, 18.1 + bulk / 2, edge)]
    return main, trim


def base_fore(cuff="red", bulk=0):
    main = [B(-30 - bulk, -18 + bulk / 2, 54, 68, 4 - bulk / 2, 18 + bulk / 2, "paint"),
            B(-31 - bulk, -17 + bulk / 2, 52, 56, 3 - bulk / 2, 19 + bulk / 2, "paint")]
    trim = [B(-30.6 - bulk, -17.4 + bulk / 2, 60, 62, 3.4 - bulk / 2, 18.6 + bulk / 2, cuff)]
    return main, trim


def base_skirt(mark="yellow"):
    main = sym(slab(-12, -1, (66, -8), (51, -11.5), 2.2, "paint"),            # front skirts
               tilt(B(-21, -16, 51, 66, -3, 14, "paint"), rz=-8)) + [         # side skirts
        B(-10, 10, 54, 66, 14, 17, "paint")]                                  # rear skirt
    trim = sym(bar((-1.5, 63, -10.2), (-8, 56, -10.2), 1.4, mark))
    return main, trim


def base_thigh(stripe="white"):
    main = [B(-21, -8, 30, 46, -4.5, 10.5, "paint"), B(-21.5, -7.5, 30, 34, -5, 11, "paint")]
    trim = [B(-21.6, -21, 34, 44, 0, 7, stripe)]
    return main, trim


def base_shin(mark="red", flare=1.5):
    main = [slab(-21, -8, (31, -8.5), (21, -12), 3, "paint"),                 # knee armour
            B(-20.5, -8.5, 28, 32, -9, -4, "paint"),
            B(-21, -8, 9, 22, -6.5, 8.5, "paint"),                            # shin
            B(-21 - flare, -8 + flare, 4, 12, -7, 12, "paint"),               # flared calf
            slab(-21 - flare, -8 + flare, (12, 12), (20, 9), 2, "paint")]
    trim = [B(-16, -13, 23, 27, -12.6, -11.8, mark), B(-21.5 - flare, -7.5 + flare, 9, 10.5, -7.5, 12.5, "dark")]
    return main, trim


def base_foot(sole="red"):
    main = [slab(-21, -8, (6, -12), (2.5, -21), 2.5, "paint"),                # toe cover
            B(-21, -8, 3, 9, -12, 2, "paint"), B(-20, -9, 1, 7, 6, 11, "paint")]
    trim = [B(-22, -7, 0, 1.6, -22, 12, sole)]
    return main, trim


def aero():   # RX-78 classic: yellow V-fin, red crest, blue chest, yellow vents, red soles
    return {"head": base_head(), "chest": base_chest(), "paul": base_paul(stripe="blue"), "fore": base_fore(),
            "skirt": base_skirt(), "thigh": base_thigh(), "shin": base_shin(), "foot": base_foot()}


def infantry():   # Titanfall Atlas: head folded into a trapezoid hull with a cyan eye, bevelled shoulders, fork antenna
    hm = [B(-15, 15, 104, 116, -12, 7, "paint"),                                               # upper hull over the head
          slab(-15, 15, (115, -12), (118, -2), 2, "paint"),                                    # bevelled brow
          slab(-12, 12, (118, -2), (117, 7), 2, "paint")]
    hm += sym(tilt(B(-17, -14, 104, 115, -10, 5, "paint"), rz=-14))                           # hull cheeks
    ht = [B(-3.5, 3.5, 106.5, 109.5, -12.6, -12, "dark"), B(-2.5, 2.5, 107.2, 108.8, -12.9, -12.6, "cyan"),  # sensor eye
          B(-14.6, 14.6, 113, 114, -12.4, -12, "yellow")]
    cm = [B(-10, 10, 84, 104, -12, -4, "paint")]                                               # lower hull spine
    cm += sym(tilt(B(-17, -9.5, 86, 104, -11, -4, "paint"), rz=-18),                          # side facets narrowing down
              B(-17, -14, 96, 104, -6, 12, "paint"))
    ct = [B(-2, 2, 86, 103, -12.6, -12, "dark")] + sym(B(-9.5, -8.5, 88, 102, -12.4, -12, "yellow"))
    pm = [B(-34, -18, 88, 102, 1, 20, "paint"),
          slab(-34, -18, (102, 1), (105, 5), 2, "paint"), slab(-34, -18, (105, 16), (102, 20), 2, "paint"),
          B(-34, -18, 103, 105.5, 5, 16, "paint")]                                             # bevelled top
    pt = [B(-34.6, -34, 88, 102, 4, 8, "yellow"), B(-34.7, -34, 95, 98, 13, 16, "cyan"),
          B(-27, -20, 105, 107, 7, 10, "dark"), B(-26, -25, 107, 118, 8, 9, "steel"), B(-22, -21, 107, 118, 8, 9, "steel")]  # fork antenna
    fm = [B(-32, -15, 50, 70, 1, 21, "paint"), slab(-32, -15, (70, 1), (72, 6), 2, "paint")]
    ft = [B(-32.6, -14.4, 61, 63.5, 0.4, 21.6, "yellow"), B(-32.7, -32, 54, 57, 8, 14, "cyan")]
    sm, st = base_skirt(mark="yellow")
    thm = [B(-21, -8, 31, 46, -6, 9, "paint"), tilt(B(-23, -20, 31, 45, -4, 8, "paint"), rz=6)]
    tht = [B(-21.6, -21, 33, 44, -2, 6, "yellow")]
    shm = [slab(-21, -8, (31, -8), (21, -12.5), 3, "paint"),                                   # knee guard
           slab(-21, -8, (21, -9.5), (8, -7), 3, "paint"),                                     # angled greave
           B(-20.5, -8.5, 8, 22, -6, 8.5, "paint")]
    sht = [B(-15.5, -13.5, 9, 20, -9.8, -9, "yellow")]
    fom = [B(-21, -8, 2, 8, -13, 6, "paint"), B(-20, -9, 1, 6, 6, 11, "paint")]
    fot = [B(x, x + 3, 0, 3, -21, -13, "dark") for x in (-21, -16, -11)] + [B(-22, -7, 0, 1.4, -13, 11, "dark")]  # toe claws
    return {"head": (hm, ht), "chest": (cm, ct), "paul": (pm, pt), "fore": (fm, ft), "skirt": (sm, st),
            "thigh": (thm, tht), "shin": (shm, sht), "foot": (fom, fot)}


def siege():   # Legion / Scorch: thick slabs, hazard trim, shoulder shields
    hm = [B(-8, 8, 110, 121, -7, 8, "paint"), B(-8.5, 8.5, 118, 121, -7.5, 8.5, "paint")]
    ht = [B(-6, 6, 113.5, 115.5, -7.6, -7, "visor"), B(-8.6, 8.6, 110, 111.5, -7.6, 8.6, "hazard")]
    cm = [B(-19, 19, 90, 110, -13, -4, "paint")] + sym(B(-21, -18, 86, 106, -7, 13, "paint")) + [B(-12, 12, 84, 92, -11, -4, "paint")]
    ct = [B(-19.5, 19.5, 88, 90.5, -13.5, -4, "hazard"), B(-8, 8, 100, 106, -13.6, -13, "vent")] + sym(B(-15, -12, 104, 107, -13.6, -13, "steel"))
    pm = [B(-38, -16, 86, 108, -3, 24, "paint"), B(-40, -37, 80, 104, -4, 25, "paint")]          # shoulder + blast shield
    pt = [B(-40.5, -39.8, 80, 84, -4.5, 25.5, "hazard"), B(-38, -16, 107.5, 109, -3, 24, "dark")]
    fm = [B(-34, -13, 47, 70, -1, 22, "paint")]
    ft = [B(-34.6, -12.4, 47, 50, -1.6, 22.6, "hazard")]
    sm, st = base_skirt(mark="dark")
    return {"head": (hm, ht), "chest": (cm, ct), "paul": (pm, pt), "fore": (fm, ft), "skirt": (sm, st),
            "thigh": ([B(-23, -6, 28, 47, -7, 12, "paint")], [B(-23.6, -5.4, 28, 31, -7.6, 12.6, "hazard")]),
            "shin": base_shin(mark="yellow", flare=3), "foot": base_foot(sole="dark")}


def samurai():   # Musha: kabuto with crescent maedate, layered sode and do lames, red and gold
    hm = [B(-7, 7, 116, 121, -6, 7, "paint"), slab(-10, 10, (116, -9), (115, 9), 1.6, "paint")] + sym(
        tilt(B(-13, -7, 111, 115, -6, 6, "paint"), rz=-28))                                       # fukigaeshi
    ht = sym(bar((-0.8, 119, -7.4), (-6, 125, -7.4), 1.6, "gold"), bar((-6, 125, -7.4), (-9.5, 131, -7.4), 1.4, "gold")) + [
        B(-2, 2, 118, 122, -8, -6, "red"), B(-2, 2, 108.5, 110.5, -5.6, -3.5, "red")]
    cm = [B(-15 - i, 15 + i, 103 - i * 5, 107 - i * 5, -11 - i * 0.7, -4, "paint") for i in range(4)]
    cm += sym(B(-18, -15, 88, 106, -6, 12, "paint"))
    ct = [B(-15.5 - i, 15.5 + i, 102.6 - i * 5, 103.4 - i * 5, -11.6 - i * 0.7, -4, "red") for i in range(4)]
    pm = [tilt(B(-36 - i * 2, -17, 100 - i * 5, 104 - i * 5, 0, 21, "paint"), rz=10 + i * 4) for i in range(4)]
    pt = [tilt(B(-36.4 - i * 2, -17, 99.4 - i * 5, 100.2 - i * 5, -0.4, 21.4, "red"), rz=10 + i * 4) for i in range(4)]
    sm = sym(*[slab(-13, -2, (66 - i * 4, -8 - i), (61 - i * 4, -10 - i), 2, "paint") for i in range(3)]) + [B(-10, 10, 54, 66, 14, 17, "paint")]
    sm += sym(tilt(B(-21, -16, 51, 66, -3, 14, "paint"), rz=-8))
    st = sym(*[slab(-13.2, -1.8, (61.4 - i * 4, -10.2 - i), (61 - i * 4, -10.4 - i), 1, "red") for i in range(3)])
    return {"head": (hm, ht), "chest": (cm, ct), "paul": (pm, pt), "fore": base_fore(cuff="gold"), "skirt": (sm, st),
            "thigh": base_thigh(stripe="red"), "shin": base_shin(mark="gold"), "foot": base_foot(sole="dark")}


def stealth():   # Deathscythe / Northstar: slim faceted plates, swept head blades, red eyes
    hm = [slab(-6, 6, (114, -6), (121, 2), 2, "paint"), slab(-6, 6, (121, 2), (118, 8), 2, "paint")] + sym(
        tilt(B(-7.5, -5, 110, 118, -4, 6, "paint"), rz=-10))
    ht = sym(bar((-3, 119, -5), (-12, 127, 4), 1.4, "dark")) + [B(-4, 4, 114, 115.6, -6.4, -6, "red")]
    cm = [slab(-15, 15, (84, -9), (96, -13), 2.5, "paint"), slab(-16, 16, (96, -13), (109, -7), 2.5, "paint")] + sym(
        tilt(B(-19, -15, 88, 106, -6, 12, "paint"), rz=12))
    ct = [slab(-2, 2, (96, -14.2), (108, -8.6), 1, "red")] + sym(B(-14, -8, 102, 104, -13, -11, "dark"))
    pm = [tilt(B(-34, -17, 97, 101, 1, 20, "paint"), rz=22), tilt(B(-35, -25, 86, 97, 1, 20, "paint"), rz=-14)]
    pt = [tilt(B(-34.4, -17, 100.6, 101.4, 0.6, 20.4, "dark"), rz=22)]
    fm = [slab(-30, -18, (68, 3), (52, 1), 2.5, "paint"), tilt(B(-32, -28, 52, 68, 4, 17, "paint"), rz=8)]
    ft = [bar((-30, 58, 10), (-38, 72, 10), 1.4, "dark")]
    return {"head": (hm, ht), "chest": (cm, ct), "paul": (pm, pt), "fore": (fm, ft), "skirt": base_skirt(mark="red"),
            "thigh": ([slab(-21, -8, (46, -6.5), (31, -3), 2.5, "paint"), tilt(B(-23, -20, 30, 46, -3, 10, "paint"), rz=-8)], [B(-21.6, -21, 36, 40, 0, 7, "red")]),
            "shin": base_shin(mark="red", flare=0.5), "foot": base_foot(sole="dark")}


def sovereign():   # Unicorn-style: single horn, gold trim and frame accents
    hm, ht = base_head(fin="gold", crest="gold")
    ht = [bar((0, 118.5, -6.4), (0.01, 133, -6.4), 2, "gold"), B(-2, 2, 108.5, 110.5, -5.6, -3.5, "gold")]  # the horn
    ht += sym(bar((-5, 119, -5), (-9, 123, -5), 1.2, "gold"))
    cm, ct = base_chest(vent="gold", hatch="purple")
    ct += [B(-2, 2, 96, 104, -12, -11, "gold")]
    pm, pt = base_paul(stripe="gold", edge="gold", bulk=2)
    pm += [B(-36, -33, 86, 96, 3, 18, "paint")]
    return {"head": (hm, ht), "chest": (cm, ct), "paul": (pm, pt), "fore": base_fore(cuff="gold"),
            "skirt": base_skirt(mark="gold"), "thigh": base_thigh(stripe="gold"), "shin": base_shin(mark="gold"),
            "foot": base_foot(sole="gold")}


def scrap():   # rugged Zaku-like: rounded head with mono-eye rail and feed pipes, spiked shoulder, rust
    hm = [B(-6, 6, 110, 120, -5.5, 6, "paint"), B(-5, 5, 120, 122, -4.5, 5, "paint"), B(-6.5, 6.5, 113, 117, -6, 6.5, "paint")]
    ht = [B(-5, 5, 114, 116, -6.6, -6, "dark"), B(-1.4, 1.4, 114.2, 115.8, -6.9, -6.6, "red")] + sym(
        slab(-5, -3.5, (111, -5.5), (106, -9), 1.6, "dark"))                                       # feed pipes
    cm, ct = base_chest(vent="dark", hatch="dark")
    ct += [B(-16.5, 16.5, 92, 93, -11.6, -4, "rust")]
    pm = [B(-34, -17, 89, 104, 0, 21, "paint")]
    pt = [bar((-34, 100, 4 + i * 6.5), (-40, 102, 4 + i * 6.5), 2, "steel") for i in range(3)]   # spikes
    fm, ft = base_fore(cuff="rust", bulk=1)
    return {"head": (hm, ht), "chest": (cm, ct), "paul": (pm, pt), "fore": (fm, ft), "skirt": base_skirt(mark="rust"),
            "thigh": base_thigh(stripe="rust"), "shin": base_shin(mark="rust", flare=2.5), "foot": base_foot(sole="dark")}


def expedition():   # GM-style utility: goggle visor, antenna, orange trim, storage on the hips
    hm = [B(-6, 6, 116, 120, -5, 6, "paint"), B(-6.5, 6.5, 110, 116, -5.5, 6, "paint")]
    ht = [B(-5.5, 5.5, 112.5, 115.5, -6.1, -5.5, "visor"), B(4.5, 5.5, 120, 130, 2, 3, "dark"), B(-2, 2, 108.5, 110.5, -5.6, -3.5, "orange")]
    cm, ct = base_chest(vent="orange", hatch="dark")
    sm, st = base_skirt(mark="orange")
    sm += sym(B(-24, -20, 52, 62, 0, 10, "paint"))                                                  # hip storage boxes
    return {"head": (hm, ht), "chest": (cm, ct), "paul": base_paul(stripe="orange", edge="dark"),
            "fore": base_fore(cuff="orange"), "skirt": (sm, st), "thigh": base_thigh(stripe="orange"),
            "shin": base_shin(mark="orange"), "foot": base_foot(sole="dark")}


T.FIXED.setdefault("rust", (126, 70, 40))
def back_shell():
    """Rear torso armour and the backpack cover every chest piece carries (the frame's spine stays covered)."""
    return [B(-14, 14, 92, 108, 13, 15.5, "paint"), B(-10, 10, 82, 92, 12.5, 15, "paint"),
            B(-9, 9, 89, 107, 21, 23, "paint")] + sym(B(-10, -8, 89, 107, 15, 22, "paint"))


def back_trim():
    return sym(B(-7, -3, 92, 104, 23, 23.6, "vent"))


def sleeve():
    """Upper-arm sleeve under the pauldron."""
    return [B(-29.5, -19.5, 74, 89, 5.5, 16, "paint")]


def belt():
    """Waist band over the pelvis, worn with the skirts."""
    return [B(-10.5, 10.5, 64, 68.5, -5.5, 14, "paint")], [B(-2.5, 2.5, 64.5, 68, -6, -5.5, "dark")]


FACEPLATE = [B(-3.4, 3.4, 110, 113.8, -5.8, -5.1, "white"), B(-2.4, 2.4, 110.8, 111.4, -6, -5.8, "dark"),
             B(-2.4, 2.4, 112.2, 112.8, -6, -5.8, "dark")]


ARCHETYPES = {"infantry": infantry, "siege": siege, "samurai": samurai, "aero": aero, "scrap": scrap,
              "stealth": stealth, "sovereign": sovereign, "expedition": expedition}

# slot -> (bone suffix, parent, pivot, side handling)
# Pauldrons attach to body3 at shoulder sockets (like Trooper) so they stay level and don't tilt 30 deg crookedly
SLOTS = [("head", "head", "doorUp", [0, 107, -8], None),
         ("chest", "chest", "body3", [0.5, 78.7, 17.8], None),
         ("skirt", "skirt", "body1", [0, 61.0, 7.0], None),
         ("paul", "arm", "body3", ([-24.4, 94.8, 10.7], [24.4, 94.8, 10.7]), "paul"),
         ("fore", "forearm", "Arm2", ([-23.4, 72.5, 10.7], [23.4, 72.5, 10.7]), "fore"),
         ("thigh", "leg", "Leg2", ([-14.5, 43.5, 2.7], [14.8, 43.5, 2.7]), "leg"),
         ("shin", "shin", "Leg1", ([-14.5, 22.8, 3.4], [14.8, 22.8, 3.4]), "leg"),
         ("foot", "foot", "Foot", ([-14.5, 8.1, -3.4], [14.8, 8.1, -3.4]), "leg")]


def armour_bones():
    bones = []
    for aid, kit in ARCHETYPES.items():
        parts = kit()
        for key, name, parent, piv, side in SLOTS:
            main, trim = parts[key]
            # shared coverage every archetype gets: back shell, upper-arm sleeve, waist belt, faceplate, calf cover
            if key == "chest":
                main, trim = main + back_shell(), trim + back_trim()
            elif key == "paul":
                main = main + sleeve()
            elif key == "skirt":
                bm, bt = belt()
                main, trim = main + bm, trim + bt
            elif key == "head":
                trim = trim + FACEPLATE
            elif key == "shin":
                main = main + [B(-20, -9, 12, 22, 8.5, 13, "paint")]               # calf cover over the actuator
            main = [dict(c) for c in main]
            for c in main:
                if c["m"] == "paint":
                    c["m"] = "armor"
            if side is None:
                bones += [(f"armor_{name}_{aid}", parent, piv, main), (f"armor_{name}_{aid}_trim", f"armor_{name}_{aid}", piv, trim)]
                continue
            if side == "paul":
                # Pauldrons sit on body3: no arm inversion, clean shoulder placement
                for lr, p, mm, tt in (("right", piv[0], main, trim), ("left", piv[1], mirror(main), mirror(trim))):
                    bones += [(f"armor_{lr}_{name}_{aid}", "body3", p, mm), (f"armor_{lr}_{name}_{aid}_trim", f"armor_{lr}_{name}_{aid}", p, tt)]
                continue
            if side == "fore":
                # Forearm flipped about forearm pivot
                main, trim = arm_fore(main), arm_fore(trim)
                for lr, p, mm, tt in (("right", piv[0], main, trim), ("left", piv[1], mirror(main), mirror(trim))):
                    bones += [(f"armor_{lr}_{name}_{aid}", lr + "Arm2", p, mm), (f"armor_{lr}_{name}_{aid}_trim", f"armor_{lr}_{name}_{aid}", p, tt)]
                continue
            pr = parent if parent.startswith(("Arm", "Leg", "Foot")) else parent
            for lr, p, mm, tt in (("right", piv[0], main, trim), ("left", piv[1], mirror(main), mirror(trim))):
                bone_parent = lr + pr if pr != "Foot" else lr + "Foot"
                bones += [(f"armor_{lr}_{name}_{aid}", bone_parent, p, mm), (f"armor_{lr}_{name}_{aid}_trim", f"armor_{lr}_{name}_{aid}", p, tt)]
    return bones


T.ID = "exo_frame"
T.CAMO = False
T.BONES = [
    ("bb_main", None, [0, 0, 0], []),
    ("skill_locator", None, [0, 0, 0], []),
    ("titan", None, [0, 0, 0], []),
    ("body1", "titan", [0, 61.0, 7.0], [
        B(-10, 10, 58, 66, -2, 14, "dark"),                                   # pelvis frame
        B(-6, 6, 52, 64, -6, 10, "paint2"),                                   # crotch block
        B(-4, 4, 55, 61, -6.6, -6, "dark"),
    ] + hub(0, 58, 7, 26, 8, "metal")),
    ("body2", "body1", [0, 74.9, 8.8], [
        B(-5, 5, 66, 71, 0, 12, "dark"), B(-6.5, 6.5, 71, 75, -1, 13, "metal"),  # segmented waist
        B(-5, 5, 75, 79, 0, 12, "dark"), B(-6, 6, 79, 82, -0.5, 12.5, "metal"),
    ] + WAIST + mirror(WAIST)),
    # Torso, hatch and lower front sit in frame_chest* bones so the Titan Exo variant can hide them under a worn
    # titan chest (TitanModel: frame_<slot> bones hide while that slot is worn).
    ("body3", "body2", [0.5, 78.7, 17.8], []),
    ("frame_chest", "body3", [0.5, 78.7, 17.8], CHEST_CORE),
    ("doorUp", "body3", [0, 107, -8], []),
    ("frame_chest_hatch", "doorUp", [0, 107, -8], FRONT),
    ("frame_head", "doorUp", [0, 107, -8], FRAME_HEAD),
    ("eye", "frame_head", [0, 107.0, -17.0], EYES),
    ("doorDown", "body3", [0, 82.7, -5.9], []),
    ("frame_chest_lower", "doorDown", [0, 82.7, -5.9], LOWER_FRONT),
    ("weaponBack", "body3", [-24.0, 78.0, 26.0], [C([-27, 74, 21], [6, 12, 4], "metal")]),
    ("rightArm1", "body3", [-24.4, 94.8, 10.7], RIGHT_ARM1),
    ("rightArm2", "rightArm1", [-23.4, 72.5, 10.7], RIGHT_ARM2),
    ("rightHand", "rightArm2", [-23.3, 46.8, 11.5], RIGHT_HAND),
    ("weapon", "rightHand", [-19.8, 39.8, 10.3], []),                         # any module is drawn by TitanWeaponSwapLayer
    ("leftArm1", "body3", [24.4, 94.8, 10.7], mirror(RIGHT_ARM1)),
    ("leftArm2", "leftArm1", [23.4, 72.5, 10.7], mirror(RIGHT_ARM2)),
    ("leftHand", "leftArm2", [23.3, 46.8, 11.5], mirror(RIGHT_HAND)),
    ("rightLeg3", "titan", [-14.5, 61.1, 7.1], RIGHT_LEG3),
    ("rightLeg2", "rightLeg3", [-14.5, 43.5, 2.7], RIGHT_LEG2),
    ("rightLeg1", "rightLeg2", [-14.5, 22.8, 3.4], RIGHT_LEG1),
    ("rightFoot", "rightLeg1", [-14.5, 8.1, -3.4], RIGHT_FOOT),
    ("leftLeg3", "titan", [14.8, 61.1, 7.1], mirror(RIGHT_LEG3)),
    ("leftLeg2", "leftLeg3", [14.8, 43.5, 2.7], mirror(RIGHT_LEG2)),
    ("leftLeg1", "leftLeg2", [14.8, 22.8, 3.4], mirror(RIGHT_LEG1)),
    ("leftFoot", "leftLeg1", [14.8, 8.1, -3.4], mirror(RIGHT_FOOT)),
] + armour_bones()

# (name, armour base [tinted per theme in game], inner frame colour, eyes)
NEUTRAL = (232, 234, 230)
T.SCHEMES = [
    ("graphite", NEUTRAL, (70, 74, 80),   (80, 255, 140)),
    ("white",    NEUTRAL, (206, 208, 206),(80, 255, 140)),
    ("navy",     NEUTRAL, (48, 60, 92),   (255, 220, 80)),
    ("olive",    NEUTRAL, (84, 92, 58),   (255, 150, 40)),
    ("sand",     NEUTRAL, (170, 146, 102),(90, 220, 255)),
    ("black",    NEUTRAL, (36, 38, 42),   (255, 50, 50)),
    ("red",      NEUTRAL, (140, 40, 36),  (255, 220, 80)),
    ("orange",   NEUTRAL, (214, 116, 34), (90, 220, 255)),
    ("purple",   NEUTRAL, (84, 56, 128),  (80, 255, 140)),
]

def pack():
    """T.pack, but cubes of the same size, material and decal share one atlas patch (mirrored left/right
    pieces, repeated lames): the armour sets do not fit a 1024 atlas otherwise."""
    x, y, row = 2, 2, 0
    placed, seen = [], {}
    ordered = [c for _, _, _, cubes in T.BONES for c in cubes if not c.get("late")]
    ordered += [c for _, _, _, cubes in T.BONES for c in cubes if c.get("late")]
    for c in ordered:
        w, h, d = (max(1, int(round(v))) for v in c["s"])
        key = (w, h, d, c["m"], tuple(sorted(c.get("decal", {}).items())))
        if key in seen:
            c["uv"], c["dims"] = seen[key], (w, h, d)
            continue
        need_w, need_h = 2 * (d + w) + 2, d + h + 2
        if x + need_w > T.TEX:
            x, y, row = 2, y + row, 0
        c["uv"], c["dims"] = [x, y], (w, h, d)
        seen[key] = c["uv"]
        x += need_w
        row = max(row, need_h)
        placed.append(c)
    assert y + row <= T.TEX, "texture atlas overflow"
    return placed


T.pack = pack
_swatch = T.__dict__.setdefault("_orig_swatch", T.swatch)  # the cockpit tool imports this module twice


def swatch(m):
    """The cockpit builder asks for a "paint" patch; the bare frame wears its colour as "paint2"."""
    return _swatch("paint2" if m == "paint" else m)


T.swatch = swatch

if __name__ == "__main__":
    T.main()
