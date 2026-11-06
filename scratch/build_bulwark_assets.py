"""MP-07 Bulwark: heavy mass-production frame on the Trooper skeleton (same bones, pivots and rest rotations,
so the shared animations, gait and cockpit data apply). Builds geo/bulwark_titan.geo.json + 9 paint schemes.

Design: an armoured vehicle that walks. Sloped glacis plates, an off-centre sensor turret instead of a head,
fixed shoulder housings with smoke dischargers, a power pack with radiator, jerry cans and whip antennas,
shell-armoured limbs over exposed hydraulics. Plain service paint, stencils, no anime trim.

Run from the repo root:  python3 scratch/build_bulwark_assets.py
"""
import math
import build_trooper_assets as T
from build_trooper_assets import C, mirror

B, hub, piston, hose, fist, late = T.B, T.hub, T.piston, T.hose, T.fist, T.late


def slab(x0, x1, a, b, t, m, decal=None):
    """Plate spanning x0..x1 whose centre line runs from a=(y, z) to b=(y, z), t thick: a sloped glacis.
    Negative x rotation lifts the -z end (see build_trooper_assets.REST), so the angle is atan2(dy, dz)."""
    (ya, za), (yb, zb) = a, b
    length = math.hypot(yb - ya, zb - za)
    ym, zm = (ya + yb) / 2, (za + zb) / 2
    ang = math.degrees(math.atan2(yb - ya, zb - za))
    if ang > 90:
        ang -= 180
    elif ang < -90:
        ang += 180
    return C([x0, ym - t / 2, zm - length / 2], [x1 - x0, t, length], m,
             rot=[round(ang, 2), 0, 0], piv=[(x0 + x1) / 2, ym, zm], decal=decal)


def ycyl(cx, y0, y1, cz, d, m):
    """Octagonal prism on a vertical axis: a square plus the same square turned 45 degrees."""
    o, s = [cx - d / 2, y0, cz - d / 2], [d, y1 - y0, d]
    return late([C(o, s, m), C(o, s, m, rot=[0, 45, 0], piv=[cx, y0, cz])])


def tube(x, a, b, d=3, m="dark"):
    """Square tube (smoke discharger, exhaust pipe) from a=(y, z) to b=(y, z) at x."""
    return slab(x - d / 2, x + d / 2, a, b, d, m)


# ---------------------------------------------------------------- arms (double-sided: the arm bones rest
# turned 180 degrees about y, which swaps front/back and inner/outer faces)

RIGHT_ARM1 = hub(-24.4, 94.8, 10.7, 10, 11) + [
    B(-29, -20, 70, 90, 5, 16, "dark"),                                       # upper arm frame
    B(-30.5, -18.5, 74, 89, 3.5, 17.5, "paint"),                              # armour shell
    B(-31, -18, 84, 87, 3, 18, "paint2"),                                     # shell band
] + piston(-24.4, 88, 74, 1.5, w=2.6) + piston(-24.4, 88, 74, 19.5, w=2.6) + hub(-24, 72.5, 10.7, 14, 10)

RIGHT_ARM2 = [
    B(-32, -15, 49, 69, 1, 21, "paint"),                                      # forearm armour
    B(-33, -32, 53, 66, 4, 18, "paint2"), B(-15, -14, 53, 66, 4, 18, "paint2"),  # side plates
    B(-33.4, -33, 56, 63, 8, 14, "dark"), B(-14, -13.6, 56, 63, 8, 14, "dark"),  # access panels
    B(-31, -16, 67, 71, 2, 20, "metal"),                                      # elbow cuff
    B(-30, -17, 45, 49, 3, 19, "dark"),                                       # wrist
] + hose(-31.5, 68, 50, 0.5, -1.5) + hose(-15.5, 68, 50, 21.5, 1.5)

RIGHT_HAND = fist(-28.3, 46.8, 6) + hub(-23.3, 46.8, 11.5, 10, 5)

# ---------------------------------------------------------------- legs

RIGHT_LEG3 = hub(-14.5, 57, 7, 18, 12) + [
    B(-26, -21, 46, 62, -3, 16, "paint", decal={"west": "stencil"}),          # hip armour
    B(-25, -21, 46, 60, -5, -3, "paint2"),
    B(-26.6, -26, 50, 58, 2, 12, "dark"),
]

RIGHT_LEG2 = [
    B(-21, -8, 27, 48, -4, 10, "dark"),                                       # thigh frame
    B(-22, -7, 30, 47, -7, -4, "paint"),                                      # front armour
    B(-24, -21, 30, 46, -5, 10, "paint"),                                     # outer armour
    B(-22, -7, 31, 46, 10, 12.5, "paint"),                                    # rear armour
    B(-8, -6, 32, 44, -3, 8, "paint2"),                                       # inner plate
] + piston(-14.5, 46, 28, 12, w=3) + hose(-21.5, 46, 30, 11, 2)

RIGHT_LEG1 = hub(-14.5, 23, 2, 17, 11) + [
    slab(-23, -6, (34, -9), (22, -13), 3, "paint"),                           # raked knee pad
    B(-22, -7, 31, 35, -9, -4, "paint2"),
    B(-21, -8, 6, 22, -5, 9, "dark"),                                         # shin frame
    slab(-23, -6, (22, -10.5), (6, -8.5), 3, "paint", decal={"north": "x"}),  # shin glacis
    B(-24, -22, 6, 20, -8, 8, "paint"), B(-7, -5, 6, 20, -8, 8, "paint"),     # shin side armour
    B(-22, -7, 9, 21, 9, 11.5, "paint2"),                                     # calf armour
] + piston(-14.5, 21, 8, 12, w=3)

RIGHT_FOOT = hub(-14.5, 7, -1, 15, 8) + [
    B(-25, -4, 0, 3, -22, 12, "dark"),                                        # tread sole
    B(-24, -5, 3, 7, -22, -12, "paint"),                                      # toe block
    slab(-23.5, -5.5, (8, -12), (5, -21), 2, "paint2"),                       # toe glacis
    B(-23, -6, 2, 8, 6, 13, "metal"),                                         # heel
    B(-22, -7, 4, 10, -12, 4, "paint2"),                                      # ankle armour
]

# ---------------------------------------------------------------- hull


def shoulder():
    """Right shoulder housing on the hull with a three-tube smoke discharger on top."""
    out = [B(-31, -17, 90, 106, -7, 20, "paint", decal={"west": "stencil"}),
           B(-30, -18, 106, 108, -5, 18, "paint2"),                               # cap
           slab(-31, -17, (90, -9), (106, -7), 2, "paint2"),                      # raked front plate
           B(-30, -18, 107.5, 109, -6, 1, "dark")]                                # discharger bracket
    for x in (-28, -24, -20):
        out.append(tube(x, (108.5, -2), (113.5, -7)))                             # smoke grenade tubes
    out.append(B(-31.6, -31, 96, 100, 0, 14, "steel"))                            # grab rail
    return out


def powerpack():
    return [B(-14, 14, 82, 106, 17, 27, "metal"),                                # power unit
            B(-11, 11, 86, 102, 27, 27.8, "vent"),                               # radiator grille
            B(-10, 10, 106, 109, 18, 26, "paint2"),                              # toolbox
            B(-17, -12, 84, 92, 22, 30, "dark"), B(12, 17, 84, 92, 22, 30, "dark"),  # mufflers
            B(-15.5, -13.5, 80, 84, 27, 29, "dark"), B(13.5, 15.5, 80, 84, 27, 29, "dark"),
            B(-18, -14, 94, 104, 18, 26, "paint2", decal={"west": "x"}),          # jerry cans
            B(14, 18, 94, 104, 18, 26, "paint2", decal={"east": "x"}),
            B(-14, -13, 106, 133, 24, 25, "dark"), B(13, 14, 106, 128, 24, 25, "dark")]  # whip antennas


HULL = [
    B(-16, 16, 82, 106, -5, 17, "paint"),                                     # hull core
    B(-12, 12, 78, 82, -2, 14, "dark"),                                       # lower frame
    B(-15, 15, 106, 109, -3, 17, "paint2"),                                   # roof
    B(-20, -16, 84, 104, -3, 15, "paint"), B(16, 20, 84, 104, -3, 15, "paint"),  # side sponsons
    B(-19, -16, 104, 106, -2, 14, "paint2"), B(16, 19, 104, 106, -2, 14, "paint2"),
    B(-20.8, -20.2, 95, 96, 0, 12, "steel"), B(20.2, 20.8, 95, 96, 0, 12, "steel"),  # grab rails
    B(-4, 4, 111, 112, 5, 13, "paint2"),                                      # commander hatch lid
] + ycyl(0, 109, 111, 9, 10, "dark") + shoulder() + mirror(shoulder()) + powerpack()

GLACIS = [
    B(-16, 16, 95, 100, -11, -5, "paint"), B(-16, 16, 100, 104, -8, -5, "paint"),   # fill under the plate
    slab(-16, 16, (95, -13), (108, -3), 3, "paint"),                          # upper glacis
] + [B(x, x + 3, 106.5, 108.5, -5.5, -3.5, "dark") for x in (-12, -7, -2)] + [  # driver periscopes
    B(x + 0.5, x + 2.5, 107, 108, -5.8, -5.5, "visor") for x in (-12, -7, -2)] + [
    # sensor turret, offset to the left like a commander's sight
    B(1, 12, 108, 116, -7, 3, "paint"),
    slab(1, 12, (108, -8.5), (116, -6.5), 2, "paint2"),
    B(3, 10, 109.5, 114, -9.6, -8.4, "dark"),                                 # lens housing
    # rangefinder / searchlight on the right
    B(-12, -4, 108, 113, -6, 2, "metal"),
    B(-11, -5, 109, 112, -6.6, -6, "glow"),
]

LENSES = [B(4.5, 7.5, 110.5, 113.5, -10, -9.6, "visor"),                     # main camera
          B(8, 9.5, 111, 112.5, -10, -9.6, "visor"),                         # thermal
          B(3.5, 4.5, 112.5, 113.5, -10, -9.6, "glow")]                      # laser emitter

LOWER_FRONT = [
    B(-15, 15, 82, 95, -13, -5, "paint", decal={"north": "num"}),             # lower front armour
    slab(-14, 14, (82, -13), (77, -7), 2, "paint2"),                          # belly plate
    B(-11, -8, 80, 84, -14.5, -12.5, "steel"), B(8, 11, 80, 84, -14.5, -12.5, "steel"),  # tow shackles
    B(-14, -11, 91, 94, -14, -13, "glow"), B(11, 14, 91, 94, -14, -13, "glow"),          # headlights
    B(-14.5, -10.5, 90.5, 91, -14.4, -13, "dark"), B(10.5, 14.5, 90.5, 91, -14.4, -13, "dark"),
]

WAIST = piston(-9.5, 82, 66, 9, w=2.6) + hose(-4, 80, 66, 15, 2)

T.ID = "bulwark"
T.CAMO = False
T.BONES = [
    ("bb_main", None, [0, 0, 0], []),
    ("skill_locator", None, [0, 0, 0], []),
    ("titan", None, [0, 0, 0], []),
    ("body1", "titan", [0, 61.0, 7.0], [
        B(-12, 12, 54, 66, -4, 16, "dark"),                                   # pelvis
        slab(-8, 8, (64, -8), (51, -6), 3, "paint"),                          # crotch armour
        B(-9, 9, 54, 64, 16, 19, "paint"),                                    # rear plate
    ]),
    ("body2", "body1", [0, 74.9, 8.8], [
        B(-9, 9, 66, 82, -1, 14, "dark"),                                     # waist core
        B(-7, 7, 70, 80, -3, -1, "paint2"),                                   # abdominal armour
        B(-7.5, 7.5, 74.5, 75.5, -3.4, -3, "dark"),
        C([-11, 65, -4.5], [22, 4, 22], "metal"),                             # slewing ring (octagon)
        C([-11, 65, -4.5], [22, 4, 22], "metal", rot=[0, 45, 0], piv=[0, 65, 6.5]),
    ] + WAIST + mirror(WAIST)),
    ("body3", "body2", [0.5, 78.7, 17.8], HULL),
    ("doorUp", "body3", [0, 107, -8], GLACIS),
    ("eye", "doorUp", [0, 107.0, -17.0], LENSES),
    ("doorDown", "body3", [0, 82.7, -5.9], LOWER_FRONT),
    ("weaponBack", "body3", [-24.0, 78.0, 26.0], [
        C([-27, 74, 26], [6, 12, 4], "metal"),                                # stowage clamp
    ]),
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
]

# (name, paint, accent, lens)
T.SCHEMES = [
    ("olive drab", (88, 96, 60),   (64, 70, 46),   (255, 150, 40)),
    ("desert",     (176, 152, 106),(130, 110, 78), (255, 150, 40)),
    ("winter",     (206, 210, 208),(140, 146, 150),(90, 220, 255)),
    ("urban",      (108, 112, 116),(74, 78, 82),   (255, 150, 40)),
    ("navy",       (58, 70, 92),   (40, 48, 64),   (90, 220, 255)),
    ("night",      (44, 46, 48),   (30, 31, 33),   (255, 60, 50)),
    ("forest",     (58, 78, 52),   (84, 70, 50),   (255, 150, 40)),
    ("tan",        (150, 128, 92), (96, 104, 70),  (255, 150, 40)),
    ("red star",   (126, 46, 40),  (70, 34, 30),   (255, 190, 60)),
]

# Stencils: "MP-07" in small white letters, the hull number "07" large.
T.FONT["7"] = ["111", "001", "010", "010", "010"]
_draw_decal = T.__dict__.setdefault("_orig_draw_decal", T.draw_decal)  # safe to import twice


def draw_decal(put, kind, fx, fy, fw, fh, rng):
    if kind not in ("stencil", "num"):
        return _draw_decal(put, kind, fx, fy, fw, fh, rng)
    text, scale = ("MP-07", 1) if kind == "stencil" else ("07", 2)
    width = (sum(len(T.FONT[ch][0]) + 1 for ch in text) - 1) * scale
    x0, y0 = fx + (fw - width) // 2, fy + (2 if kind == "stencil" else max(1, (fh - 5 * scale) // 3))
    for ch in text:
        g = T.FONT[ch]
        for r, line in enumerate(g):
            for k, bit in enumerate(line):
                if bit == "1":
                    for sy in range(scale):
                        for sx in range(scale):
                            px, py = x0 + k * scale + sx, y0 + r * scale + sy
                            if T.h2(px, py, 11) > 0.1:  # worn stencil paint
                                put(px, py, (216, 218, 210))
        x0 += (len(g[0]) + 1) * scale


T.draw_decal = draw_decal

if __name__ == "__main__":
    T.main()
