"""MP-03 Shade Titan: mass-produced cloaked infiltrator on the Trooper skeleton (same bones, pivots and
rest rotations, so the shared animations, gait and cockpit data apply), plus a "cape" bone that
TitanModel sways with movement. Builds geo/shade_titan.geo.json + 9 paint schemes ("cloth" uses the
scheme's second colour).

Run from the repo root:  python3 scratch/build_shade_assets.py
"""
import build_trooper_assets as T
from build_trooper_assets import C, mirror

RIGHT_ARM1 = [
    C([-31, 92, 2], [10, 9, 16], "metal"),                                       # low rounded pad
    C([-32, 89, 3], [11, 3, 14], "dark"),
    C([-29, 82, 6], [7, 9, 9], "dark"),
    C([-28, 71, 7], [6, 13, 7], "paint"),
]
RIGHT_ARM2 = [
    C([-27, 67, 7], [8, 6, 8], "dark"),
    C([-28, 50, 5], [10, 18, 11], "paint"),
    C([-30, 47, 8], [2, 22, 4], "steel"),                                        # forearm blade
    C([-29, 63, 6], [1, 4, 8], "glow"),
]
RIGHT_HAND = [C([-27, 43, 7], [8, 5, 9], "dark"), C([-26, 37, 8], [6, 6, 7], "metal")]
LEFT_FINGERS = [C([20, 36, 7], [6, 7, 9], "metal"), C([20, 31, 8], [2, 5, 2], "dark"),
                C([23.5, 31, 8], [2, 5, 2], "dark"), C([21.5, 31, 13], [2, 5, 2], "dark")]

RIGHT_LEG3 = [C([-18, 54, 3], [7, 9, 8], "dark"), C([-20, 50, 0], [3, 12, 12], "cloth")]  # hip tasset
RIGHT_LEG2 = [
    C([-19, 28, -2], [9, 20, 10], "paint"),
    C([-18, 24, 0], [7, 6, 6], "metal"),
    C([-16, 30, 8], [3, 16, 3], "steel"),
]
RIGHT_LEG1 = [
    C([-18, 21, -1], [7, 7, 7], "dark"),
    C([-19, 18, -8], [9, 12, 5], "paint"),                                       # long greave
    C([-18, 8, -4], [7, 13, 9], "metal"),
    C([-17, 9, 5], [5, 12, 3], "dark"),
]
RIGHT_FOOT = [
    C([-17, 4, -2], [6, 4, 6], "dark"),
    C([-19, 0, -12], [10, 4, 17], "paint"),
    C([-18, 0, -15], [8, 2, 4], "dark"),
    C([-17, 0, 5], [6, 3, 5], "metal"),
]

def robe_strips(x0, n, w, z, y_top, lengths, flare, depth_step=1.0):
    """Pleated cloth panel: n vertical strips of width w, alternating depth, flaring out at the hem."""
    out = []
    for k in range(n):
        length = lengths[k % len(lengths)]
        dz = depth_step if k % 2 else 0.0
        out.append(C([x0 + k * w, y_top - length, z + dz], [w, length, 1], "cloth",
                     rot=[flare, 0, 0], piv=[x0 + k * w + w / 2, y_top, z + dz]))
    return out

def cape():
    """Back of the robe (sways in game): pleated panel to the knees plus two side panels."""
    out = robe_strips(-17.5, 7, 5, 15, 102, (58, 62, 55, 64, 57, 61, 54), 8)
    for sx, rz in ((-20, -7), (19, 7)):                                       # side panels
        out.append(C([sx, 46, -6], [1, 56, 21], "cloth", rot=[4, 0, rz], piv=[sx + 0.5, 102, 4]))
    return out

def front_robe():
    """Open front of the robe: two pleated flaps leaving the chest armour showing in the middle."""
    return (robe_strips(-18, 3, 4, -13, 98, (50, 54, 47), -7)
            + robe_strips(6, 3, 4, -13, 98, (48, 53, 51), -7))

def sleeve():
    """Cloth draped over the right shoulder and upper arm."""
    return [C([-34, 98, -1], [13, 2, 23], "cloth"),
            C([-36, 78, -1], [1, 22, 23], "cloth", rot=[0, 0, -8], piv=[-35.5, 99, 10])]

T.ID = "shade"
T.BONES = [
    ("bb_main", None, [0, 0, 0], []),
    ("skill_locator", None, [0, 0, 0], []),
    ("titan", None, [0, 0, 0], []),
    ("body1", "titan", [0, 61.0, 7.0], [
        C([-9, 56, -1], [18, 8, 13], "dark"),
        C([-6, 44, -5], [12, 16, 1], "cloth", rot=[-6, 0, 0], piv=[0, 60, -5]),   # front tabard
    ]),
    ("body2", "body1", [0, 74.9, 8.8], [
        C([-6, 64, 1], [12, 16, 10], "metal"),                                    # narrow waist
        C([-7, 69, 0], [14, 3, 12], "dark"),
    ]),
    ("body3", "body2", [0.5, 78.7, 17.8], [
        C([-15, 86, -8], [30, 18, 22], "paint"),                                  # broad chest
        C([-11, 79, -6], [22, 8, 18], "paint"),
        C([-14, 88, -11], [28, 12, 4], "paint", rot=[-15, 0, 0], piv=[0, 94, -9]),  # chest wedge
        C([-21, 97, -10], [42, 6, 27], "cloth"),                                  # shoulder mantle
        C([-19, 94, -11], [38, 4, 3], "cloth"),                                   # mantle front fold
        C([-17, 92, -2], [3, 6, 14], "dark"),
        C([14, 92, -2], [3, 6, 14], "dark"),
        C([-8, 84, 14], [16, 14, 2], "metal"),
        C([-12, 92, -12], [3, 2, 1], "glow"),
        C([9, 92, -12], [3, 2, 1], "glow"),
    ]),
    ("cape", "body3", [0, 104, 15], cape()),
    ("robe", "body3", [0, 98, -13], front_robe()),
    ("doorUp", "body3", [0, 113, 8], [
        C([-8, 97, -11], [16, 10, 10], "dark"),                                   # head in shadow
        C([-12, 95, -14], [2, 15, 20], "cloth"),                                  # hood sides
        C([10, 95, -14], [2, 15, 20], "cloth"),
        C([-12, 108, -14], [24, 3, 20], "cloth"),                                 # hood crown
        C([-11, 106, -16], [22, 3, 3], "cloth"),                                  # brim drooping over face
        C([-12, 94, -16], [3, 13, 3], "cloth"),                                   # face opening rim
        C([9, 94, -16], [3, 13, 3], "cloth"),
        C([-8, 110, -10], [16, 3, 15], "cloth"),                                  # peak
        C([-4, 112, -6], [8, 3, 10], "cloth"),
        C([-1.5, 114, -3], [3, 2, 5], "cloth"),
        C([-11, 90, 5], [22, 18, 3], "cloth"),                                    # hood falls onto the back
    ]),
    ("eye", "doorUp", [0, 107.0, -17.0], [
        C([-6, 101, -13], [12, 1, 1], "visor"),                                 # single slit
    ]),
    ("doorDown", "body3", [0, 82.7, -5.9], [
        C([-9, 80, -10], [18, 9, 4], "metal"),
    ]),
    ("weaponBack", "body3", [-24.0, 78.0, 26.0], [C([-27, 74, 17], [6, 12, 5], "dark")]),
    ("rightArm1", "body3", [-24.4, 94.8, 10.7], RIGHT_ARM1 + sleeve()),
    ("rightArm2", "rightArm1", [-23.4, 72.5, 10.7], RIGHT_ARM2),
    ("rightHand", "rightArm2", [-23.3, 46.8, 11.5], RIGHT_HAND),
    ("weapon", "rightHand", [-19.8, 39.8, 10.3], []),                             # borrowed guns attach here
    ("leftArm1", "body3", [24.4, 94.8, 10.7], mirror(RIGHT_ARM1 + sleeve())),
    ("leftArm2", "leftArm1", [23.4, 72.5, 10.7], mirror(RIGHT_ARM2)),
    ("leftHand", "leftArm2", [23.3, 46.8, 11.5], mirror(RIGHT_HAND[:1]) + LEFT_FINGERS),
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
