"""Builds the Code Geass Knightmare Frame redesign for exo_frame_titan.
Features:
- Sleek athletic humanoid Knightmare proportions (Glasgow / Sutherland / Lancelot inspired)
- Rear dorsal ejection cockpit pod with thrusters
- Chest-mounted dual Slash Harken launcher housings
- Factsphere sensor optics
- Iconic ankle-mounted Landspinner high-speed roller wheel units
- Sleek multi-faceted pauldrons and high-mobility limb armor
- 9 military camouflage color schemes with realistic metal shading
"""
import sys, os, math
sys.path.insert(0, "scratch")
import build_trooper_assets as T
from build_trooper_assets import B, C, hub, piston, hose, fist, late, ball, mirror, FONT

T.ID = "exo_frame"
T.CAMO = True

# Custom Knightmare Landspinner wheel builder
def landspinner(x_outer, y_hub, z_hub, is_left=False):
    """Landspinner high-speed roller wheel unit mounted on the outer ankle."""
    sgn = 1 if is_left else -1
    x0 = x_outer
    w = 3.5 # wheel width
    diam = 8.0 # wheel diameter
    out = [
        # Swing-arm suspension bracket from upper calf
        B(x0 - sgn * 1.5, x0 + sgn * 2.0, y_hub, y_hub + 10, z_hub - 2, z_hub + 2, "dark"),
        B(x0 - sgn * 2.0, x0 + sgn * 1.5, y_hub + 7, y_hub + 11, z_hub - 3, z_hub + 1, "metal"),
        # Hydraulic deploy cylinder
        C([x0 - sgn * 1.0, y_hub + 2, z_hub - 1], [2, 6, 2], "steel"),
        # Wheel axle hub
        B(x0 - sgn * (w + 1), x0 + sgn * 1, y_hub - 1.5, y_hub + 1.5, z_hub - 1.5, z_hub + 1.5, "steel"),
        # Main Landspinner roller tire (octagonal cylinder)
        B(x0 - sgn * w, x0, y_hub - diam/2, y_hub + diam/2, z_hub - diam/2 + 1, z_hub + diam/2 - 1, "dark"),
        B(x0 - sgn * w, x0, y_hub - diam/2 + 1, y_hub + diam/2 - 1, z_hub - diam/2, z_hub + diam/2, "dark"),
        # Center rim cap
        B(x0 - sgn * (w + 0.5), x0 - sgn * (w - 0.5), y_hub - 2, y_hub + 2, z_hub - 2, z_hub + 2, "paint2"),
        # Mudguard / deflector shroud
        B(x0 - sgn * (w + 1), x0 + sgn * 0.5, y_hub + 1, y_hub + diam/2 + 1.5, z_hub - diam/2, z_hub + 2, "paint"),
        B(x0 - sgn * (w + 0.8), x0 + sgn * 0.2, y_hub + diam/2, y_hub + diam/2 + 1.8, z_hub - diam/2, z_hub + 2, "hazard")
    ]
    return late(out)

# Chest Slash Harken launcher pod
def slash_harken(x_center, y_center, z_front):
    """Chest Slash Harken rocket-anchor launcher block."""
    w, h, d = 4.5, 4.5, 5.0
    return [
        # Launcher casing
        B(x_center - w/2, x_center + w/2, y_center - h/2, y_center + h/2, z_front, z_front + d, "dark"),
        # Outer bezel trim
        B(x_center - w/2 - 0.5, x_center + w/2 + 0.5, y_center - h/2 - 0.5, y_center + h/2 + 0.5, z_front - 0.5, z_front + 1.0, "hazard"),
        # Rocket anchor projectile head (pointed steel harken)
        B(x_center - 1.2, x_center + 1.2, y_center - 1.2, y_center + 1.2, z_front - 2.5, z_front, "steel"),
        B(x_center - 0.6, x_center + 0.6, y_center - 0.6, y_center + 0.6, z_front - 3.8, z_front - 2.5, "metal")
    ]

# Rear Dorsal Ejection Cockpit Pod (Code Geass signature)
def knightmare_cockpit_pod():
    """Protruding rear cockpit capsule (ejection pod) on the upper back."""
    return [
        # Main cockpit hump
        B(-11, 11, 88, 115, 14, 28, "paint"),
        # Sloped armored canopy roof
        B(-9, 9, 108, 117, 12, 26, "paint2"),
        # Emergency ejection hatch seams
        B(-10.5, 10.5, 114, 116, 13, 27, "hazard"),
        # Dual dorsal thrusters
        B(-9, -3, 86, 96, 27, 34, "dark"),
        B(3, 9, 86, 96, 27, 34, "dark"),
        B(-8, -4, 87, 95, 33.5, 35, "vent"),
        B(4, 8, 87, 95, 33.5, 35, "vent"),
        # Cooling intake scoops on pod shoulders
        B(-12, -10.5, 98, 108, 16, 24, "vent"),
        B(10.5, 12, 98, 108, 16, 24, "vent"),
        # Antenna mount
        B(8, 9.5, 116, 130, 20, 21.5, "steel")
    ]

# Sleek Knightmare Pauldron (Angular deflection armor)
def knightmare_pauldron():
    """Angular, athletic Knightmare shoulder armor."""
    return [
        # Main angled shoulder cowl
        B(-40, -18, 90, 111, -8, 20, "paint", decal={"west": "hazard_bottom", "north": "number"}),
        # Upper angled crest plate
        B(-38, -20, 110, 113.5, -6, 18, "paint2"),
        # Outer thruster fin / flare
        B(-41.5, -39.5, 93, 107, -5, 17, "paint2"),
        # Lower hazard accent
        B(-40.5, -17.5, 87.5, 90, -8.5, 20.5, "hazard"),
        # Rear vernier cooling port
        B(-36, -22, 94, 104, 20, 21.5, "vent"),
        # Position light
        B(-40.2, -39.5, 99, 103, -7, -3, "glow")
    ]

# Sleek Knightmare Head & Factsphere
def knightmare_head():
    """Sleek Code Geass head with Factsphere sensor optics."""
    return [
        # Main helmet skull
        B(-11, 11, 98, 110, -13, -2, "paint"),
        # Angular crown and crest
        B(-8, 8, 109, 113, -14, -1, "paint2"),
        B(-2, 2, 112, 115, -15, -2, "hazard"),
        # Sleek cheek armor / jaw
        B(-12, -9, 96, 107, -14, -3, "paint2"),
        B(9, 12, 96, 107, -14, -3, "paint2"),
        # Chin sensor vent
        B(-5, 5, 96, 98.5, -13.5, -8, "vent"),
        # Side aerodynamic antenna fins
        B(-13.5, -11.5, 102, 114, -6, 2, "paint2"),
        B(11.5, 13.5, 102, 114, -6, 2, "paint2"),
        # Factsphere camera housing (center forehead)
        B(-4, 4, 104, 108, -14.5, -12, "metal")
    ]

# Torso / Chest with V-taper and Slash Harkens
KNIGHTMARE_CHEST = [
    # Core cabin hull (sleek V-taper)
    B(-15, 15, 85, 108, -7, 15, "paint"),
    B(-12, 12, 79, 85, -4, 13, "dark"),
    # Side armor ribs
    B(-18, -15, 87, 105, -4, 13, "paint2"),
    B(15, 18, 87, 105, -4, 13, "paint2"),
    # Collar guard around the head
    B(-14, 14, 107, 111, -5, 12, "paint2")
] + knightmare_pauldron() + mirror(knightmare_pauldron()) + knightmare_cockpit_pod()

# Lower Chest Hatch with Slash Harkens
KNIGHTMARE_HATCH = [
    # Sloped front chest breastplate
    B(-13, 13, 82, 97, -13, -7, "paint", decal={"north": "number"}),
    B(-10, 10, 96, 101, -14, -7, "paint2"),
    # Center Factsphere deployment chest hatch
    B(-5, 5, 88, 94, -14.2, -12, "metal"),
    B(-3.5, 3.5, 89.5, 92.5, -14.8, -13.5, "glow"),
    # Recovery tow point / hazard lower edge
    B(-13.5, 13.5, 80.5, 82.5, -13.5, -7, "hazard")
] + slash_harken(-8.5, 89, -13.5) + slash_harken(8.5, 89, -13.5)

# High-Mobility Knightmare Arm
KNIGHTMARE_ARM1 = ball(-24.4, 94.8, 10.7, 9) + [
    # Sleek bicep core
    B(-28, -20, 75, 89, 6, 15, "dark"),
    B(-29, -19, 77, 87, 5, 16, "paint"),
    B(-28.5, -19.5, 78, 86, 4, 5.5, "paint2")
] + hub(-24, 75, 10.5, 12, 8) + piston(-24, 88, 77, 17, w=2.0)

KNIGHTMARE_ARM2 = [
    # Forearm gauntlet with angular side deflection plates
    B(-32, -16, 50, 71, 2, 19, "paint"),
    B(-33.5, -31.5, 54, 68, 4, 17, "paint2"),
    B(-16.5, -14.5, 54, 68, 4, 17, "paint2"),
    # Stun tonfa / weapon rail hardpoint
    B(-34, -32.5, 58, 66, 8, 13, "metal"),
    B(-33, -15, 68, 72, 3, 18, "metal"),
    B(-30, -18, 46, 50, 4, 17, "dark") # wrist ring
]

KNIGHTMARE_HAND = fist(-27, 48, 7) + hub(-23.3, 48, 11, 8, 4.5)

# High-Mobility Knightmare Leg with Landspinner
KNIGHTMARE_LEG3 = [
    # Hip joint & slash harken drum skirt
    B(-22, -18, 50, 62, -2, 14, "paint"),
    B(-23, -21.5, 52, 60, 1, 11, "hazard"),
    B(-17, -11, 52, 63, 1, 11, "dark")
] + hub(-14.5, 57, 6, 16, 10)

KNIGHTMARE_LEG2 = [
    # Sleek thigh armor
    B(-20, -9, 31, 48, -4, 9, "paint"),
    B(-19.5, -9.5, 33, 46, -6, -3.5, "paint2"),
    B(-21, -20, 34, 45, -2, 7, "paint2"),
    B(-18, -11, 26, 31, -2, 7, "dark")
] + piston(-14.5, 45, 32, -7.5) + hose(-18, 45, 32, 11, 2.0)

KNIGHTMARE_LEG1 = [
    # High-mobility shin with Landspinner assembly
    B(-21, -8, 20, 35, -12, -4, "paint"), # sharp knee cop armor
    B(-20, -9, 33, 36, -11, -5, "paint2"),
    B(-21, -8, 6, 22, -8, 8, "paint"), # sleek shin guard
    B(-19.5, -9.5, 8, 20, -9.5, -7.5, "paint2"),
    B(-22, -21, 9, 20, -5, 6, "paint2"),
    B(-19, -10, 8, 21, 8, 12, "dark") # rear calf
] + hub(-14.5, 23, 1, 15, 8) + landspinner(-22.5, 9, 8, is_left=False)

KNIGHTMARE_FOOT = [
    # Sleek split-toe combat boot with magnetic tread
    B(-22, -7, 0, 4, -20, 10, "dark"),
    B(-21, -8, 0, 7, -21, -11, "paint"),
    B(-21.5, -7.5, 0, 2, -21.5, -19, "hazard"),
    B(-20, -9, 4, 9, -12, 3, "paint2"),
    B(-20.5, -8.5, 0, 6, 5, 11, "metal")
] + hub(-14.5, 6.5, -1, 12, 6)

# Assemble Complete Bone Rig
T.BONES = [
    ("bb_main", None, [0, 0, 0], []),
    ("skill_locator", None, [0, 0, 0], []),
    ("titan", None, [0, 0, 0], []),
    ("body1", "titan", [0, 61.0, 7.0], [
        B(-10, 10, 55, 65, -3, 14, "dark"),
        B(-7, 7, 51, 63, -6, -3, "paint", decal={"north": "hazard_bottom"}),
        B(-6, 6, 59, 62, -6.5, -6, "dark"),
        B(-7, 7, 53, 63, 14, 17, "paint")
    ]),
    ("body2", "body1", [0, 74.9, 8.8], [
        B(-7, 7, 66, 80, 0, 12, "dark"),
        B(-9, 9, 65, 69, -2, 14, "metal"),
        B(-5, 5, 70, 79, -2, 0, "paint2")
    ] + hub(0, 73, 8, 16, 8, "metal") + T.WAIST + mirror(T.WAIST)),
    ("body3", "body2", [0.5, 78.7, 17.8], KNIGHTMARE_CHEST),
    ("doorUp", "body3", [0, 107, -8], knightmare_head()),
    ("eye", "doorUp", [0, 107.0, -17.0], [
        # Glowing Factsphere scanning visor
        B(-8, 8, 102, 105, -14.8, -13.8, "visor")
    ]),
    ("doorDown", "body3", [0, 82.7, -5.9], KNIGHTMARE_HATCH),
    ("artillery", "body3", [-24.0, 78.0, 26.0], T.artillery_base()),
    ("artilleryTurret", "artillery", [0, 105, 22], T.artillery_turret()),
    ("artilleryBarrel", "artilleryTurret", T.ARTILLERY_TRUNNION, T.artillery_barrel()),
    ("back_rocket_pod", "body3", [-24.0, 96.0, 18.0], T.back_rocket_pod()),
    ("weaponBack", "body3", [-24.0, 78.0, 26.0], [
        C([-28, 72, 22], [8, 16, 8], "metal"),
        C([-29, 80, 21], [10, 2, 10], "hazard")
    ]),
    ("stowed_rifle", "weaponBack", [-24.0, 78.0, 26.0], T.stowed_rifle()),
    ("stowed_machine_gun", "weaponBack", [-24.0, 78.0, 26.0], T.stowed_machine_gun()),
    ("stowed_rocket_launcher", "weaponBack", [-24.0, 78.0, 26.0], T.stowed_rocket_launcher()),
    ("rightArm1", "body3", [-24.4, 94.8, 10.7], KNIGHTMARE_ARM1),
    ("rightArm2", "rightArm1", [-23.4, 72.5, 10.7], KNIGHTMARE_ARM2),
    ("rightHand", "rightArm2", [-23.3, 46.8, 11.5], KNIGHTMARE_HAND),
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
    ("leftArm1", "body3", [24.4, 94.8, 10.7], mirror(KNIGHTMARE_ARM1)),
    ("leftArm2", "leftArm1", [23.4, 72.5, 10.7], mirror(KNIGHTMARE_ARM2)),
    ("leftHand", "leftArm2", [23.3, 46.8, 11.5], mirror(KNIGHTMARE_HAND)),
    ("rightLeg3", "titan", [-14.5, 61.1, 7.1], KNIGHTMARE_LEG3),
    ("rightLeg2", "rightLeg3", [-14.5, 43.5, 2.7], KNIGHTMARE_LEG2),
    ("rightLeg1", "rightLeg2", [-14.5, 22.8, 3.4], KNIGHTMARE_LEG1),
    ("rightFoot", "rightLeg1", [-14.5, 0.0, 0.0], KNIGHTMARE_FOOT),
    ("leftLeg3", "titan", [14.5, 61.1, 7.1], mirror(KNIGHTMARE_LEG3)),
    ("leftLeg2", "leftLeg3", [14.5, 43.5, 2.7], mirror(KNIGHTMARE_LEG2)),
    ("leftLeg1", "leftLeg2", [14.5, 22.8, 3.4], [
        # Left Leg1 with left-sided Landspinner
        B(8, 21, 20, 35, -12, -4, "paint"),
        B(9, 20, 33, 36, -11, -5, "paint2"),
        B(8, 21, 6, 22, -8, 8, "paint"),
        B(9.5, 19.5, 8, 20, -9.5, -7.5, "paint2"),
        B(21, 22, 9, 20, -5, 6, "paint2"),
        B(10, 19, 8, 21, 8, 12, "dark")
    ] + hub(14.5, 23, 1, 15, 8) + landspinner(22.5, 9, 8, is_left=True)),
    ("leftFoot", "leftLeg1", [14.5, 0.0, 0.0], mirror(KNIGHTMARE_FOOT)),
]

print("Building Code Geass Knightmare Frame assets...")
T.main()
print("SUCCESS: Code Geass Knightmare Frame built!")
