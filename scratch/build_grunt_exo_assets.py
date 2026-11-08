"""Rebuilds exo_frame_titan into a solid, heavy-duty Mass-Produced Combat Grunt (รุ่นโหล).
Uses build_trooper_assets architecture for complete geometry, UVs, and 9 camouflage schemes.
"""
import sys, os
sys.path.insert(0, "scratch")
import build_trooper_assets as T
from build_trooper_assets import B, C, hub, piston, hose, fist, xbrace, late, ball, mirror, FONT

# Override ID so it writes directly to geo/exo_frame_titan.geo.json and textures/.../exo_frame/
T.ID = "exo_frame"
T.CAMO = True # Grunt uses military camo textures

# Add numbers / decals for Grunt "05" / "EF"
FONT['5'] = ["1111", "1000", "1110", "0001", "1110"]
FONT['E'] = ["1111", "1000", "1110", "1000", "1111"]
FONT['F'] = ["1111", "1000", "1110", "1000", "1000"]

# Customize pauldron for Grunt
def grunt_pauldron():
    return [
        B(-42, -18, 88, 112, -9, 23, "paint", decal={"west": "mp01", "north": "hazard_bottom"}),
        B(-40, -20, 112, 114, -7, 21, "paint2"),                              # top cap plate
        B(-42.5, -17.5, 85.5, 88, -9.5, 23.5, "hazard"),                     # lower hazard band
        B(-43, -42, 91, 109, -5, 19, "paint2"),                               # outer deflector plate
        B(-38, -22, 92, 107, 23, 24, "vent"),                                 # rear heat vent
        B(-42.6, -42, 99, 103, -8, -4, "glow"),                              # position marker light
        B(-33, -31, 114, 118, 2, 4, "steel"), B(-33, -31, 114, 118, 14, 16, "steel"),
        B(-33, -31, 117, 119, 2, 16, "steel")                                # lift handle
    ]

# Customize Head for Grunt (Infantry Combat Helmet look)
GRUNT_HEAD = [
    B(-17, 17, 94, 110, -16, -8, "paint"),                                 # armored helmet base
    B(-18, 18, 107, 112, -18, -8, "paint2"),                               # heavy brow hood over visor
    B(-14, 14, 99, 105, -16.5, -15, "dark"),                               # visor recess channel
    B(-19, -16, 94, 108, -17, -8, "paint2"), B(16, 19, 94, 108, -17, -8, "paint2"), # side cheek guards
    B(-10, 10, 94.5, 97.5, -16.6, -15.5, "vent"),                          # chin grille
    B(-15, -12, 95, 98, -17.2, -16.5, "glow"), B(12, 15, 95, 98, -17.2, -16.5, "glow"), # tactical lamps
    B(-16, 16, 105, 106.5, -16.8, -15.5, "hazard"),                        # brow warning stripe
    B(-20, -18.5, 99, 106, -13, -8, "metal"), B(18.5, 20, 99, 106, -13, -8, "metal"), # side comms ear pods
    B(17.5, 18.5, 106, 120, -11, -9.5, "steel"),                           # military radio whip antenna
]

# Customize Chest / Torso for Grunt
GRUNT_CAB = [
    B(-17, 17, 84, 109, -8, 17, "paint"),                                  # main cabin hull
    B(-14, 14, 78, 84, -4, 15, "dark"),                                    # lower chassis frame
    B(-20, -17, 86, 107, -5, 15, "paint2"), B(17, 20, 86, 107, -5, 15, "paint2"), # side armor plates
    B(-20.5, -20, 90, 103, 0, 10, "vent"), B(20, 20.5, 90, 103, 0, 10, "vent"),
    B(-16, 16, 109, 111, -7, 16, "paint2"),                                # armored roof plate
    B(-9, 9, 111, 112, -2, 11, "vent"),                                    # roof ventilation hatch
] + grunt_pauldron() + mirror(grunt_pauldron()) + T.ROLL_CAGE + T.EXHAUST + mirror(T.EXHAUST) + T.backpack()

# Assemble full Bones structure
T.BONES = [
    ("bb_main", None, [0, 0, 0], []),
    ("skill_locator", None, [0, 0, 0], []),
    ("titan", None, [0, 0, 0], []),
    ("body1", "titan", [0, 61.0, 7.0], [
        B(-12, 12, 54, 66, -4, 16, "dark"),                                # heavy pelvis block
        B(-8, 8, 49, 64, -8, -4, "paint", decal={"north": "hazard_bottom"}),# groin armor plate
        B(-7, 7, 60, 63, -8.6, -8, "dark"),
        B(-8, 8, 52, 64, 16, 19, "paint"),                                 # rear skirt guard
        B(-13, -12, 56, 64, 0, 12, "vent"), B(12, 13, 56, 64, 0, 12, "vent"),
    ]),
    ("body2", "body1", [0, 74.9, 8.8], [
        B(-8, 8, 66, 80, -1, 13, "dark"),                                  # spine core
        B(-10, 10, 65, 69, -3, 15, "metal"),                               # slewing ring
        B(-6, 6, 70, 79, -3, -1, "paint2"),                                # ab armor plate
        B(-5, 5, 72.5, 74, -3.4, -3, "dark"), B(-5, 5, 76, 77.5, -3.4, -3, "dark"),
    ] + hub(0, 73, 9, 18, 9, "metal") + T.WAIST + mirror(T.WAIST)),
    ("body3", "body2", [0.5, 78.7, 17.8], GRUNT_CAB),
    ("doorUp", "body3", [0, 107, -8], GRUNT_HEAD),
    ("eye", "doorUp", [0, 107.0, -17.0], [
        B(-12, 12, 100.5, 103.5, -17, -16.4, "visor"),                     # wide glowing visor slit
    ]),
    ("doorDown", "body3", [0, 82.7, -5.9], [
        B(-15, 15, 80, 94, -15, -8, "paint", decal={"north": "number"}),   # sloped lower chest armor
        B(-11, -5, 83, 89, -15.8, -15, "vent"), B(5, 11, 83, 89, -15.8, -15, "vent"),
        B(-15.5, 15.5, 78.5, 80.5, -15.5, -8, "hazard"),
        B(-3, 3, 79, 82, -17, -15, "steel"),                               # recovery tow hook
    ]),
    ("artillery", "body3", [-24.0, 78.0, 26.0], T.artillery_base()),
    ("artilleryTurret", "artillery", [0, 105, 22], T.artillery_turret()),
    ("artilleryBarrel", "artilleryTurret", T.ARTILLERY_TRUNNION, T.artillery_barrel()),
    ("back_rocket_pod", "body3", [-24.0, 96.0, 18.0], T.back_rocket_pod()),
    ("weaponBack", "body3", [-24.0, 78.0, 26.0], [
        C([-28, 72, 22], [8, 16, 8], "metal"),                              # stowed weapon clamp
        C([-29, 80, 21], [10, 2, 10], "hazard"),
    ]),
    ("stowed_rifle", "weaponBack", [-24.0, 78.0, 26.0], T.stowed_rifle()),
    ("stowed_machine_gun", "weaponBack", [-24.0, 78.0, 26.0], T.stowed_machine_gun()),
    ("stowed_rocket_launcher", "weaponBack", [-24.0, 78.0, 26.0], T.stowed_rocket_launcher()),
    ("rightArm1", "body3", [-24.4, 94.8, 10.7], T.RIGHT_ARM1),
    ("rightArm2", "rightArm1", [-23.4, 72.5, 10.7], T.RIGHT_ARM2),
    ("rightHand", "rightArm2", [-23.3, 46.8, 11.5], T.RIGHT_HAND),
    ("weapon", "rightHand", [-19.8, 39.8, 10.3], []),
    ("drill", "weapon", [-19.8, 39.8, 10.3], T.drill(None, 10.3, -19.8)),
    ("chainsaw", "weapon", [-19.8, 39.8, 10.3], T.chainsaw(None, 10.3, -19.8)),
    ("rifle", "weapon", [-19.8, 39.8, 10.3], T.rifle(None, 10.3, -19.8)),
    ("machine_gun", "weapon", [-19.8, 39.8, 10.3], T.machine_gun(None, 10.3, -19.8)),
    ("rocket_launcher", "weapon", [-19.8, 39.8, 10.3], T.rocket_launcher(None, 10.3, -19.8)),
    ("arc_cannon", "weapon", [-19.8, 39.8, 10.3], T.arc_cannon(None, 10.3, -19.8)),
    ("scatter_cannon", "weapon", [-19.8, 39.8, 10.3], T.scatter_cannon(None, 10.3, -19.8)),
    ("inferno_flamethrower", "weapon", [-19.8, 39.8, 10.3], T.inferno_flamethrower(None, 10.3, -19.8)),
    ("grenade_launcher", "weapon", [-19.8, 39.8, 10.3], T.grenade_launcher(None, 10.3, -19.8)),
    ("leftArm1", "body3", [24.4, 94.8, 10.7], mirror(T.RIGHT_ARM1)),
    ("leftArm2", "leftArm1", [23.4, 72.5, 10.7], mirror(T.RIGHT_ARM2)),
    ("leftHand", "leftArm2", [23.3, 46.8, 11.5], mirror(T.RIGHT_HAND)),
    ("rightLeg3", "titan", [-14.5, 61.1, 7.1], T.RIGHT_LEG3),
    ("rightLeg2", "rightLeg3", [-14.5, 43.5, 2.7], T.RIGHT_LEG2),
    ("rightLeg1", "rightLeg2", [-14.5, 22.8, 3.4], T.RIGHT_LEG1),
    ("rightFoot", "rightLeg1", [-14.5, 0.0, 0.0], T.RIGHT_FOOT),
    ("leftLeg3", "titan", [14.5, 61.1, 7.1], mirror(T.RIGHT_LEG3)),
    ("leftLeg2", "leftLeg3", [14.5, 43.5, 2.7], mirror(T.RIGHT_LEG2)),
    ("leftLeg1", "leftLeg2", [14.5, 22.8, 3.4], mirror(T.RIGHT_LEG1)),
    ("leftFoot", "leftLeg1", [14.5, 0.0, 0.0], mirror(T.RIGHT_FOOT)),
]

print("Building Grunt Exo Frame assets...")
T.main()
print("SUCCESS: Grunt Exo Frame built!")
