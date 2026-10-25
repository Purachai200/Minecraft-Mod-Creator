"""SR-07 Scout Titan: light recon frame on the Trooper skeleton (same bones, pivots and rest rotations,
so the shared animations, gait and cockpit data apply). Builds geo/scout_titan.geo.json + 9 paint schemes.

Run from the repo root:  python3 scratch/build_scout_assets.py
"""
import build_trooper_assets as T
from build_trooper_assets import C, mirror, ycube

GY = T.GRIP_Y

def smg(cz, x0):
    """Compact SMG along +x from the grip: receiver, short barrel with suppressor, box magazine, sight."""
    return [ycube(None, cz, x0 - 6, 18, 8, 7, "paint2"),
            ycube(None, cz, x0 - 4, 3, 2, 8, "hazard"),
            ycube(None, cz, x0 + 12, 12, 3, 3, "metal"),
            ycube(None, cz, x0 + 22, 6, 5, 5, "dark"),
            C([x0 + 1, GY - 12, cz - 2], [5, 9, 4], "dark"),                    # magazine
            C([x0 + 1, GY + 4, cz - 1], [6, 2, 2], "glow"),                     # red-dot sight
            C([x0 - 12, GY - 2, cz - 2], [6, 5, 4], "metal")]                   # stock

RIGHT_ARM1 = [
    C([-33, 90, 1], [11, 12, 17], "paint", decal={"west": "stripe"}),           # angled shoulder pad
    C([-34, 88, 0], [12, 2, 19], "paint2"),
    C([-29, 82, 6], [7, 9, 9], "dark"),
    C([-28, 71, 7], [6, 13, 7], "metal"),
    C([-29, 74, 5], [3, 7, 2], "paint2"),
]
RIGHT_ARM2 = [
    C([-27, 67, 7], [8, 6, 8], "dark"),
    C([-28, 50, 5], [10, 18, 11], "paint"),
    C([-29, 55, 6], [1, 9, 8], "paint2"),
    C([-20, 52, 8], [2, 13, 2], "steel"),
]
RIGHT_HAND = [C([-27, 43, 7], [8, 5, 9], "dark")]
LEFT_FINGERS = [C([20, 36, 7], [6, 7, 9], "metal"), C([20, 31, 8], [2, 5, 2], "dark"),
                C([23.5, 31, 8], [2, 5, 2], "dark"), C([21.5, 31, 13], [2, 5, 2], "dark")]

RIGHT_LEG3 = [C([-18, 54, 3], [7, 9, 8], "dark"), C([-20, 51, 1], [3, 10, 11], "paint2")]
RIGHT_LEG2 = [
    C([-19, 29, -2], [9, 19, 10], "paint"),
    C([-18, 24, 0], [7, 6, 6], "metal"),
    C([-16, 30, 8], [3, 16, 3], "steel"),
]
RIGHT_LEG1 = [
    C([-18, 21, -1], [7, 7, 7], "dark"),
    C([-19, 19, -7], [9, 10, 4], "paint", decal={"north": "stripe"}),           # knee guard
    C([-18, 8, -3], [7, 13, 8], "metal"),
    C([-20, 9, 5], [11, 10, 7], "paint2"),                                       # calf thruster pod
    C([-19, 7, 6], [9, 2, 5], "vent"),                                           # nozzle
]
RIGHT_FOOT = [
    C([-17, 4, -2], [6, 4, 6], "dark"),
    C([-19, 0, -9], [10, 4, 14], "metal"),
    C([-20, 0, -17], [3, 3, 9], "paint"),                                        # three pointed toes
    C([-16, 0, -18], [3, 3, 10], "paint"),
    C([-12, 0, -17], [3, 3, 9], "paint"),
    C([-17, 0, 5], [6, 3, 6], "dark"),                                           # heel spur
]

T.ID = "scout"
T.BONES = [
    ("bb_main", None, [0, 0, 0], []),
    ("skill_locator", None, [0, 0, 0], []),
    ("titan", None, [0, 0, 0], []),
    ("body1", "titan", [0, 61.0, 7.0], [
        C([-9, 56, -1], [18, 8, 13], "dark"),
        C([-7, 53, -4], [14, 7, 4], "paint2"),
    ]),
    ("body2", "body1", [0, 74.9, 8.8], [
        C([-7, 64, 1], [14, 16, 11], "metal"),
        C([-5, 66, -1], [10, 10, 2], "vent"),
    ]),
    ("body3", "body2", [0.5, 78.7, 17.8], [
        C([-12, 80, -7], [24, 22, 22], "paint"),                                 # slim hull
        C([-13, 84, -5], [1, 14, 16], "paint2", decal={"west": "stripe"}),
        C([12, 84, -5], [1, 14, 16], "paint2", decal={"east": "stripe"}),
        C([-10, 78, -12], [20, 8, 8], "paint2", rot=[-30, 0, 0], piv=[0, 82, -8]),  # wedge chin
        C([-15, 92, -2], [3, 6, 14], "dark"),                                    # shoulder sockets
        C([12, 92, -2], [3, 6, 14], "dark"),
        C([-10, 86, 15], [20, 14, 4], "metal"),                                  # thruster pack
        C([-9, 80, 16], [6, 6, 6], "vent", rot=[30, 0, 0], piv=[-6, 83, 19]),    # twin jump nozzles
        C([3, 80, 16], [6, 6, 6], "vent", rot=[30, 0, 0], piv=[6, 83, 19]),
        C([-3, 102, 2], [6, 4, 6], "dark"),                                      # radar mast base
        C([-1, 106, 4], [2, 10, 2], "metal"),
        C([-7, 115, 2], [14, 4, 2], "steel", rot=[0, 20, 0], piv=[0, 117, 3]),   # radar bar
        C([8, 100, 8], [1, 16, 1], "dark"),                                      # whip antenna
        C([-11, 90, -9], [3, 2, 2], "glow"),
        C([8, 90, -9], [3, 2, 2], "glow"),
    ]),
    ("doorUp", "body3", [0, 105, 3], [
        C([-10, 94, -13], [20, 9, 6], "paint"),                                  # canopy
        C([-9, 102, -11], [18, 3, 14], "paint2"),                                # canopy roof
        C([-11, 95, -12], [1, 7, 4], "metal"),
        C([10, 95, -12], [1, 7, 4], "metal"),
    ]),
    ("eye", "doorUp", [0, 107.0, -17.0], [
        C([-8, 97, -14], [16, 2, 1], "visor"),                                   # wide visor band
        C([-3, 99.5, -14.5], [6, 2, 1], "visor"),                                # center optic
    ]),
    ("doorDown", "body3", [0, 82.7, -5.9], [
        C([-9, 82, -11], [18, 11, 4], "paint", decal={"north": "hazard_bottom"}),
    ]),
    ("weaponBack", "body3", [-24.0, 78.0, 26.0], [
        C([-27, 74, 19], [6, 12, 6], "metal"),
    ]),
    ("rightArm1", "body3", [-24.4, 94.8, 10.7], RIGHT_ARM1),
    ("rightArm2", "rightArm1", [-23.4, 72.5, 10.7], RIGHT_ARM2),
    ("rightHand", "rightArm2", [-23.3, 46.8, 11.5], RIGHT_HAND),
    ("weapon", "rightHand", [-19.8, 39.8, 10.3], smg(10.3, -19.8)),
    ("leftArm1", "body3", [24.4, 94.8, 10.7], mirror(RIGHT_ARM1)),
    ("leftArm2", "leftArm1", [23.4, 72.5, 10.7], mirror(RIGHT_ARM2)),
    ("leftHand", "leftArm2", [23.3, 46.8, 11.5], mirror(RIGHT_HAND) + LEFT_FINGERS),
    ("rightLeg3", "titan", [-14.5, 61.1, 7.1], RIGHT_LEG3),
    ("rightLeg2", "rightLeg3", [-14.5, 43.5, 2.7], RIGHT_LEG2),
    ("rightLeg1", "rightLeg2", [-14.5, 22.8, 3.4], RIGHT_LEG1),
    ("rightFoot", "rightLeg1", [-14.5, 8.1, -3.4], RIGHT_FOOT),
    ("leftLeg3", "titan", [14.8, 61.1, 7.1], mirror(RIGHT_LEG3)),
    ("leftLeg2", "leftLeg3", [14.8, 43.5, 2.7], mirror(RIGHT_LEG2)),
    ("leftLeg1", "leftLeg2", [14.8, 22.8, 3.4], mirror(RIGHT_LEG1)),
    ("leftFoot", "leftLeg1", [14.8, 8.1, -3.4], mirror(RIGHT_FOOT)),
]

# (name, paint, accent, visor)
T.SCHEMES = [
    ("recon",   (150, 156, 160), (222, 120, 36),  (80, 230, 255)),
    ("sand",    (196, 170, 120), (90, 80, 64),    (80, 230, 255)),
    ("snow",    (220, 224, 226), (60, 120, 200),  (80, 230, 255)),
    ("forest",  (66, 86, 60),    (170, 150, 90),  (255, 190, 60)),
    ("night",   (40, 44, 56),    (200, 40, 40),   (255, 60, 50)),
    ("racer",   (180, 40, 36),   (230, 230, 225), (80, 230, 255)),
    ("sky",     (80, 130, 190),  (240, 190, 40),  (255, 255, 255)),
    ("lime",    (150, 190, 50),  (40, 42, 46),    (80, 230, 255)),
    ("royal",   (100, 60, 140),  (220, 200, 60),  (255, 190, 60)),
]

if __name__ == "__main__":
    T.main()
