"""MP-03 Shade Titan: mass-produced cloaked infiltrator on the Trooper skeleton (same bones, pivots and
rest rotations, so the shared animations, gait and cockpit data apply), plus a "cape" bone that
TitanModel sways with movement. Builds geo/shade_titan.geo.json + 9 paint schemes ("cloth" uses the
scheme's second colour).

Run from the repo root:  python3 scratch/build_shade_assets.py
"""
import build_trooper_assets as T
from build_trooper_assets import C, mirror

def robe_strips(x0, n, w, z, y_top, lengths, flare, depth_step=1.0):
    """Pleated cloth panel: n vertical strips of width w, alternating depth, flaring out at the hem."""
    out = []
    for k in range(n):
        length = lengths[k % len(lengths)]
        dz = depth_step if k % 2 else 0.0
        out.append(C([x0 + k * w, y_top - length, z + dz], [w, length, 1], "cloth",
                     rot=[flare, 0, 0], piv=[x0 + k * w + w / 2, y_top, z + dz]))
    return out

B, hub, piston, hose = T.B, T.hub, T.piston, T.hose

# ---- Boxy heavy walker (reference: the hunched box-bodied walker with the top-mounted gun):
# one big armoured box for the torso, short heavy limbs on drum joints and rams, camo net on the back.

def octo(x0, x1, y0, y1, z0, z1, m):
    """Vertical octagonal column: a box plus a copy turned 45 degrees about y."""
    piv = [(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]
    return [B(x0, x1, y0, y1, z0, z1, m), B(x0, x1, y0, y1, z0, z1, m, rot=[0, 45, 0], piv=piv)]

RIGHT_ARM1 = hub(-24.5, 94, 10.7, 10, 14) + [
    B(-33, -25, 88, 106, 0, 22, "paint"),                                     # outer shoulder armour
    B(-32, -24, 106, 108, 2, 20, "paint2"),
] + octo(-29, -20, 72, 90, 6, 15, "metal") + piston(-18.5, 88, 74, 15, w=2.4) + hose(-30, 88, 74, 17, 2)
RIGHT_ARM2 = hub(-24, 70.5, 10.7, 13, 11) + [
    B(-32, -16, 48, 68, 1, 20, "paint"),                                      # armoured forearm
    B(-31, -17, 50, 66, -0.5, 1, "paint2"),
    B(-30, -18, 45, 49, 4, 17, "dark"),                                       # wrist
] + piston(-15, 66, 50, 6, w=2) + piston(-15, 66, 50, 15, w=2)
RIGHT_HAND = [
    B(-29, -18, 39, 46, 5, 17, "dark"),                                       # palm
    B(-29.5, -17.5, 43, 46, 4.5, 17.5, "metal"),
    B(-28.5, -25.5, 32, 39, 13, 16.5, "dark"), B(-24.5, -21.5, 32, 39, 13, 16.5, "dark"),
    B(-20.5, -17.5, 32, 39, 13, 16.5, "dark"),                                # three heavy fingers
    B(-28.5, -17.5, 31, 32.5, 13, 16.5, "steel"),                             # finger tips
    B(-29.5, -27.5, 34, 41, 6, 9.5, "metal"),                                 # thumb
]

RIGHT_LEG3 = hub(-14.5, 57, 7, 20, 13) + [B(-26, -22, 48, 62, -4, 16, "paint")]
RIGHT_LEG2 = [
    B(-22, -7, 27, 48, -7, 11, "paint"),                                      # thick thigh
    B(-21, -8, 30, 46, -9, -7, "paint2"),
] + piston(-14.5, 46, 30, 13, w=3) + hose(-21, 46, 30, 13, 2.5)
RIGHT_LEG1 = hub(-14.5, 23, 2, 18, 12) + [
    B(-23, -6, 16, 33, -14, -6, "paint"),                                     # big knee block
    B(-19, -10, 6, 20, -4, 6, "dark"),                                        # shin frame
    B(-20, -9, 8, 18, -6, -4, "paint2"),
] + piston(-21, 20, 8, 1, w=2.4) + piston(-8, 20, 8, 1, w=2.4)
RIGHT_FOOT = hub(-14.5, 7, -1, 12, 8) + [
    B(-25, -4, 0, 6, -18, 10, "dark"),                                        # wide flat foot
    B(-24, -5, 0, 7, -20, -10, "paint"),                                      # toe plate
    B(-22, -7, 0, 7, 6, 12, "metal"),                                         # heel
]

def gun_on_top():
    """Light machine gun on a pintle mount on the roof of the box."""
    return [B(-3, 3, 114, 117, -2, 6, "metal"), B(-2.5, 2.5, 117, 121, -8, 8, "dark"),
            B(-1, 1, 118, 120, -22, -8, "steel"), B(-2, 2, 114, 117, -10, -6, "dark")]

def side_strips(x, n, w, z0, y_top, lengths, flare):
    """Torn cloth strips hanging down a side face (x), n of them along z, flaring out at the hem."""
    out = []
    for k in range(n):
        length = lengths[k % len(lengths)]
        dx = -0.6 if k % 2 else 0.0
        out.append(C([x + dx, y_top - length, z0 + k * w], [1, length, w], "cloth",
                     rot=[0, 0, flare], piv=[x + dx + 0.5, y_top, z0 + k * w + w / 2]))
    return out

def cloak():
    """Camouflage cloak thrown over the box: roof sheet, torn valance over the front edge (the sensor
    strip stays clear), long side drapes and ghillie tufts that break up the silhouette."""
    out = [B(-21.5, 21.5, 113, 114.5, -18, 19.5, "cloth"),                      # roof sheet
           B(-21.5, 21.5, 109, 113, -18.5, -17, "cloth")]                       # front fold
    out += robe_strips(-21, 9, 4.7, -19.5, 112, (6, 9, 5, 8, 4, 9, 6, 7, 5), -10, depth_step=-0.6)
    out += side_strips(-22.5, 8, 4.7, -17.5, 114, (26, 31, 22, 34, 28, 24, 33, 27), 7)
    out += mirror(side_strips(-22.5, 8, 4.7, -17.5, 114, (29, 23, 33, 26, 31, 22, 28, 34), 7))
    for x, z, h, r in ((-16, -10, 4, 20), (-7, 2, 3, -25), (9, -6, 5, 15), (15, 9, 3, -18),
                       (-12, 12, 5, 30), (4, 14, 4, -12), (-2, -14, 3, 22), (17, -13, 4, -28)):
        out.append(C([x, 114, z], [2, h, 2], "cloth", rot=[r, 0, r / 2], piv=[x + 1, 114, z + 1]))
    return out

def shoulder_cloth():
    """Cloak flap draped over the shoulder armour, hanging down its outer face."""
    return [B(-34, -23.5, 108, 109.5, -1, 23, "cloth")] + side_strips(-34.5, 5, 4.8, -1, 109, (14, 18, 12, 17, 15), 6)

def cape():
    """Back of the cloak: long torn drape down the rear of the box (sways in game)."""
    return robe_strips(-21, 9, 4.7, 19.5, 114, (38, 44, 34, 47, 40, 36, 45, 39, 42), 6)

T.ID = "shade"
T.CAMO = True
T.BONES = [
    ("bb_main", None, [0, 0, 0], []),
    ("skill_locator", None, [0, 0, 0], []),
    ("titan", None, [0, 0, 0], []),
    ("body1", "titan", [0, 61.0, 7.0], [
        B(-15, 15, 54, 64, -6, 16, "dark"),
        B(-17, -15, 52, 62, -4, 14, "paint"), B(15, 17, 52, 62, -4, 14, "paint"),
    ]),
    ("body2", "body1", [0, 74.9, 8.8], [B(-10, 10, 62, 76, -6, 14, "dark")]
        + piston(-11.5, 76, 62, 4) + mirror(piston(-11.5, 76, 62, 4))),
    ("body3", "body2", [0.5, 78.7, 17.8], [
        B(-20, 20, 76, 112, -16, 18, "paint"),                                # the box
        B(-18, 18, 112, 114, -14, 16, "paint2"),                              # roof bevel
        B(-21, -20, 80, 108, -14, 16, "paint2"), B(20, 21, 80, 108, -14, 16, "paint2"),
        B(-14, 14, 82, 104, 18, 19, "vent"),                                  # rear grille
        B(14, 15, 114, 128, 12, 13, "dark"),                                  # antenna
    ] + gun_on_top() + cloak()),
    ("cape", "body3", [0, 104, 15], cape()),
    ("robe", "body3", [0, 98, -13], []),
    ("doorUp", "body3", [0, 113, 8], [
        B(-19, 19, 94, 111, -19, -16, "paint"),                               # upper front plate
        B(-18, 18, 111, 113, -18, -14, "paint2"),
        B(-14, 14, 100, 106, -20, -19, "dark"),                               # sensor housing
    ]),
    ("eye", "doorUp", [0, 107.0, -17.0], [
        B(-12, 12, 102, 104, -20.6, -20, "visor"),                            # sensor strip
    ]),
    ("doorDown", "body3", [0, 82.7, -5.9], [
        B(-19, 19, 77, 94, -19, -16, "paint", decal={"north": "number"}),
        B(-9, -7, 82, 84, -19.6, -19, "glow"), B(-1, 1, 82, 84, -19.6, -19, "glow"),
        B(7, 9, 82, 84, -19.6, -19, "glow"),
    ]),
    ("weaponBack", "body3", [-24.0, 78.0, 26.0], [C([-27, 74, 17], [6, 12, 5], "dark")]),
    ("rightArm1", "body3", [-24.4, 94.8, 10.7], RIGHT_ARM1 + shoulder_cloth()),
    ("rightArm2", "rightArm1", [-23.4, 72.5, 10.7], RIGHT_ARM2),
    ("rightHand", "rightArm2", [-23.3, 46.8, 11.5], RIGHT_HAND),
    ("weapon", "rightHand", [-19.8, 39.8, 10.3], []),                             # borrowed guns attach here
    ("leftArm1", "body3", [24.4, 94.8, 10.7], mirror(RIGHT_ARM1 + shoulder_cloth())),
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

# (name, armour, cloak, visor)
T.SCHEMES = [
    ("shadow",  (70, 74, 80),    (132, 116, 88),  (190, 90, 255)),
    ("desert",  (170, 150, 110), (128, 106, 74),  (255, 190, 60)),
    ("snow",    (210, 214, 218), (232, 232, 226), (80, 230, 255)),
    ("forest",  (60, 76, 54),    (44, 58, 40),    (120, 255, 120)),
    ("urban",   (100, 104, 110), (60, 62, 68),    (255, 60, 50)),
    ("night",   (30, 32, 40),    (22, 24, 30),    (190, 90, 255)),
    ("crimson", (110, 30, 30),   (40, 36, 36),    (255, 60, 50)),
    ("navy",    (40, 54, 84),    (70, 74, 80),    (80, 230, 255)),
    ("bone",    (190, 180, 160), (110, 30, 30),   (255, 190, 60)),
]

if __name__ == "__main__":
    T.main()
