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

B, ball, fist = T.B, T.ball, T.fist

# ---- 30MM-style light frame (reference: the Bandai 30 Minutes Missions grey kit): slim segmented
# limbs, ball joints everywhere, small sensor head, plate packs on the back.

RIGHT_ARM1 = ball(-24.4, 92, 10.7, 9) + [
    B(-33, -22, 92, 102, 0, 20, "paint", decal={"west": "stripe"}),          # angled pauldron
    B(-33.5, -21.5, 90, 92, -0.5, 20.5, "paint2"),
    B(-27, -21, 74, 90, 7.5, 13.5, "dark"),                                   # upper arm frame
    B(-28.5, -27, 76, 88, 7, 14, "paint"),                                    # outer plate
    B(-27, -21, 80, 88, 6, 7.5, "paint2"), B(-27, -21, 75, 79, 6, 7.5, "paint2"),  # segment plates
    B(-28.9, -28.5, 82, 84, 9.5, 11.5, "dark"),                               # panel hole
]
RIGHT_ARM2 = ball(-24, 71, 10.7, 7) + [
    B(-29, -18, 50, 68, 5, 16, "paint"),                                      # forearm
    B(-30, -29, 60, 67, 6, 15, "paint2"), B(-30, -29, 51, 59, 6, 15, "paint2"),
    B(-30.4, -30, 62, 64, 9.5, 11.5, "dark"), B(-30.4, -30, 54, 56, 9.5, 11.5, "dark"),
    B(-28, -19, 67, 69, 6, 15, "metal"),                                      # elbow cuff
    B(-27, -19, 46, 50, 7, 15, "dark"),                                       # wrist
]
RIGHT_HAND = fist(-27.8, 46.8, 6.5)

RIGHT_LEG3 = ball(-14.5, 57, 7, 10) + [B(-22, -19, 50, 62, 0, 13, "paint")]   # hip + side skirt
RIGHT_LEG2 = [
    B(-18, -11, 28, 48, 0, 8, "dark"),                                        # thigh frame
    B(-19.5, -9.5, 30, 46, -2.5, 0, "paint"),                                 # front armor
    B(-21, -18, 30, 46, -1, 8, "paint2"),                                     # outer armor
    B(-21.4, -21, 40, 42, 2, 4, "dark"),
] + T.piston(-14.5, 46, 30, 10, w=2.2)
RIGHT_LEG1 = ball(-14.5, 23, 3, 8) + [
    B(-20, -9, 18, 31, -8, -3, "paint", decal={"north": "stripe"}),          # knee pad
    B(-18, -11, 6, 20, -2, 6, "dark"),                                        # shin frame
    B(-19.5, -9.5, 8, 20, -4, -2, "paint"),                                   # shin armor
    B(-20, -9, 9, 19, 6, 11, "paint2"),                                       # calf thruster pod
    B(-19, -10, 7, 9, 6.5, 10.5, "vent"),
]
RIGHT_FOOT = ball(-14.5, 7, 0, 6) + [
    B(-19, -10, 0, 4, -10, 6, "dark"),
    B(-20, -17, 0, 3, -18, -9, "paint"), B(-16, -13, 0, 3, -19, -9, "paint"), B(-12, -9, 0, 3, -18, -9, "paint"),
    B(-17, -12, 0, 3, 5, 11, "metal"),                                        # heel spur
    B(-19, -10, 4, 7, -6, 2, "paint2"),                                       # ankle guard
]

T.ID = "scout"
T.CAMO = False
T.BONES = [
    ("bb_main", None, [0, 0, 0], []),
    ("skill_locator", None, [0, 0, 0], []),
    ("titan", None, [0, 0, 0], []),
    ("body1", "titan", [0, 61.0, 7.0], [
        B(-9, 9, 55, 65, -1, 13, "dark"),
        B(-6, 6, 51, 63, -4, -1, "paint"),                                    # front skirt
        B(-13, -9, 53, 63, 0, 12, "paint2"), B(9, 13, 53, 63, 0, 12, "paint2"),
    ]),
    ("body2", "body1", [0, 74.9, 8.8], [
        B(-5, 5, 64, 80, 2, 12, "dark"),                                      # segmented spine
        B(-7, 7, 72, 78, 0, 2, "paint2"), B(-6, 6, 66, 71, 0.5, 2, "paint2"),
        B(-8, -5, 68, 76, 3, 11, "vent"), B(5, 8, 68, 76, 3, 11, "vent"),
    ]),
    ("body3", "body2", [0.5, 78.7, 17.8], [
        B(-13, 13, 81, 104, -6, 15, "paint"),                                 # chest
        B(-14, -13, 84, 100, -4, 13, "paint2", decal={"west": "stripe"}),
        B(13, 14, 84, 100, -4, 13, "paint2", decal={"east": "stripe"}),
        B(-16, -13, 92, 100, 2, 12, "dark"), B(13, 16, 92, 100, 2, 12, "dark"),  # shoulder sockets
        B(-7, 7, 104, 106, -3, 9, "dark"),                                    # collar
        B(-11, 11, 84, 102, 15, 20, "metal"),                                 # backpack
        B(-15, -11, 86, 100, 15, 22, "paint2"), B(11, 15, 86, 100, 15, 22, "paint2"),  # plate packs
        B(-9, -4, 80, 85, 16, 20, "dark"), B(4, 9, 80, 85, 16, 20, "dark"),   # thrusters
        B(8, 9, 100, 118, 16, 17, "dark"),                                    # whip antenna
    ]),
    ("doorUp", "body3", [0, 105, 3], [
        B(-5, 5, 104, 113, -7, 3, "paint"),                                   # sensor head
        B(-5.5, 5.5, 113, 114.5, -7.5, 3.5, "paint2"),
        B(-3, 3, 103, 105, -8, -4, "dark"),                                   # chin
        B(-6, -5, 107, 111, -4, 0, "dark"), B(5, 6, 107, 111, -4, 0, "dark"),  # ear sensors
        B(3.5, 4.5, 112, 120, -1, 0, "dark"),                                 # head antenna
        B(-11, 11, 96, 104, -9, -6, "paint2"),                                # upper chest plate
    ]),
    ("eye", "doorUp", [0, 107.0, -17.0], [
        B(-4, 4, 108, 110, -7.6, -7, "visor"),
        B(-1, 1, 110, 111.5, -7.8, -7.2, "visor"),
    ]),
    ("doorDown", "body3", [0, 82.7, -5.9], [
        B(-10, 10, 82, 96, -9, -6, "paint"),                                  # lower chest
        B(-2.5, 2.5, 88, 93, -9.6, -9, "dark"), B(-1, 1, 89.5, 91.5, -9.9, -9.6, "glow"),  # sensor port
        B(-10.5, 10.5, 81, 82.5, -9.4, -6, "hazard"),
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
