"""RPI-13 Sutherland (Code Geass Knightmare Frame) Asset Builder
Accurately models the Fifth Generation Britannian Mass-Production Knightmare Frame:
- Chiseled Sutherland helmet with Factsphere forehead optics and swept antenna fins
- Rear-mounted dorsal ejection cockpit capsule with twin angled thruster nozzles
- Dual chest Slash Harken rocket-anchor pods with pointed steel heads and hazard bezels
- V-tapered athletic chest and narrow mechanical waist with hydraulic rams and conduits
- Chamfered Sutherland box pauldrons with Purist orange hazard bands
- Sleek forearm gauntlets with side weapon rails
- Folding Landspinner roller wheel assemblies on outer ankles (suspension arm, brake caliper, roller tire, hub)
- High-mobility split-toe combat feet
- 9 authentic Sutherland liveries (Britannia Army Slate, Purist Faction, Royal Guard, Black Knights, etc.)
"""
import sys, os, math
sys.path.insert(0, "scratch")
import build_trooper_assets as T
from build_trooper_assets import B, C, hub, piston, hose, fist, late, ball, mirror, FONT

T.ID = "exo_frame"
T.CAMO = True

# ------------------------------------------------ Sutherland Landspinner (Folding Ankle Roller Units)
def sutherland_landspinner(x_pos, y_hub, z_hub, is_left=False):
    """Detailed RPI-13 Sutherland Landspinner roller wheel unit mounted on the outer ankle."""
    sgn = 1 if is_left else -1
    x0 = x_pos
    w = 3.6     # Tire width
    diam = 8.5  # Wheel diameter
    out = [
        # Main swing-arm suspension strut attaching to calf frame
        B(x0 - sgn * 1.6, x0 + sgn * 2.2, y_hub + 1, y_hub + 11, z_hub - 2.5, z_hub + 2.5, "dark"),
        B(x0 - sgn * 2.2, x0 + sgn * 1.4, y_hub + 6, y_hub + 12, z_hub - 3.5, z_hub + 1.5, "metal"),
        # Hydraulic deploy cylinder with chrome piston shaft
        C([x0 - sgn * 1.2, y_hub + 2, z_hub - 1.2], [2.4, 6.5, 2.4], "steel"),
        # Central wheel axle and bearing cap
        B(x0 - sgn * (w + 1.2), x0 + sgn * 1.2, y_hub - 1.8, y_hub + 1.8, z_hub - 1.8, z_hub + 1.8, "steel"),
        # High-grip Landspinner roller tire (octagonal profile)
        B(x0 - sgn * w, x0, y_hub - diam/2, y_hub + diam/2, z_hub - diam/2 + 1.2, z_hub + diam/2 - 1.2, "dark"),
        B(x0 - sgn * w, x0, y_hub - diam/2 + 1.2, y_hub + diam/2 - 1.2, z_hub - diam/2, z_hub + diam/2, "dark"),
        # Central spinner rim cap
        B(x0 - sgn * (w + 0.6), x0 - sgn * (w - 0.4), y_hub - 2.2, y_hub + 2.2, z_hub - 2.2, z_hub + 2.2, "paint2"),
        # Aerodynamic mudguard fender over top of wheel
        B(x0 - sgn * (w + 1.2), x0 + sgn * 0.6, y_hub + 1.5, y_hub + diam/2 + 1.8, z_hub - diam/2 - 0.5, z_hub + 2.5, "paint"),
        # Hazard stripe trim along fender edge
        B(x0 - sgn * (w + 1.0), x0 + sgn * 0.4, y_hub + diam/2 + 0.5, y_hub + diam/2 + 2.2, z_hub - diam/2 - 0.5, z_hub + 2.5, "hazard")
    ]
    return late(out)

# ------------------------------------------------ Sutherland Chest Slash Harkens
def sutherland_slash_harken(x_center, y_center, z_front):
    """Sutherland chest-mounted Slash Harken rocket-anchor pod."""
    w, h, d = 4.8, 4.8, 5.5
    return [
        # Launcher silo casing
        B(x_center - w/2, x_center + w/2, y_center - h/2, y_center + h/2, z_front, z_front + d, "dark"),
        # Purist orange / caution hazard bezel rim
        B(x_center - w/2 - 0.6, x_center + w/2 + 0.6, y_center - h/2 - 0.6, y_center + h/2 + 0.6, z_front - 0.6, z_front + 1.2, "hazard"),
        # Four-point guide fins
        B(x_center - 0.6, x_center + 0.6, y_center - h/2 - 1.0, y_center + h/2 + 1.0, z_front - 1.0, z_front + 0.5, "metal"),
        B(x_center - w/2 - 1.0, x_center + w/2 + 1.0, y_center - 0.6, y_center + 0.6, z_front - 1.0, z_front + 0.5, "metal"),
        # Pointed tungsten-carbide rocket anchor head
        B(x_center - 1.4, x_center + 1.4, y_center - 1.4, y_center + 1.4, z_front - 2.8, z_front, "steel"),
        B(x_center - 0.8, x_center + 0.8, y_center - 0.8, y_center + 0.8, z_front - 4.2, z_front - 2.8, "metal")
    ]

# ------------------------------------------------ Sutherland Dorsal Cockpit Pod (Ejection Block)
def sutherland_cockpit_pod():
    """Sutherland distinctive dorsal cockpit pod (ejection block) mounted on the back."""
    return [
        # Main cockpit hump structure
        B(-10.5, 10.5, 88, 116, 14, 28, "paint"),
        # Angled cockpit roof armor plate
        B(-9, 9, 109, 118, 12, 26, "paint2"),
        # Emergency separation rocket seams
        B(-10, 10, 115, 117.5, 13, 27, "hazard"),
        # Dual primary propulsion thruster bells
        B(-8.5, -2.5, 87, 97, 27, 34, "dark"),
        B(2.5, 8.5, 87, 97, 27, 34, "dark"),
        B(-7.5, -3.5, 88, 96, 33.5, 35.5, "vent"),
        B(3.5, 7.5, 88, 96, 33.5, 35.5, "vent"),
        # Side cooling intake air scoops
        B(-11.5, -10, 98, 109, 16, 24, "vent"),
        B(10, 11.5, 98, 109, 16, 24, "vent"),
        # Long-range tactical radio antenna mast
        B(7.5, 9.0, 117, 132, 20, 21.5, "steel")
    ]

# ------------------------------------------------ Sutherland Shoulder Pauldron
def sutherland_pauldron():
    """RPI-13 Sutherland box-deflector shoulder armor with Purist hazard bands."""
    return [
        # Main angular pauldron shell
        B(-39, -17, 90, 111, -8, 20, "paint", decal={"west": "hazard_bottom", "north": "number"}),
        # Upper crest armor cap
        B(-37, -19, 110, 113.5, -6, 18, "paint2"),
        # Sutherland outer deflection flare plate
        B(-41.0, -38.5, 93, 107, -5, 17, "paint2"),
        # Signature hazard/purist band along pauldron lower edge
        B(-39.5, -16.5, 87.5, 90, -8.5, 20.5, "hazard"),
        # Rear vernier cooling grille
        B(-35, -21, 94, 105, 20, 21.5, "vent"),
        # Formation marker lamp
        B(-39.5, -38.5, 100, 104, -7, -3, "glow"),
        # Heavy lift shackle
        B(-30, -28, 113.5, 117.5, 3, 5, "steel"),
        B(-30, -28, 113.5, 117.5, 11, 13, "steel"),
        B(-30, -28, 116.5, 118.5, 3, 13, "steel")
    ]

# ------------------------------------------------ Sutherland Head & Factsphere Optics
def sutherland_head():
    """RPI-13 Sutherland chiseled combat helmet with Factsphere optics."""
    return [
        # Main helmet skull casing
        B(-10.5, 10.5, 98, 110, -13, -2, "paint"),
        # Sloped forehead crest
        B(-7.5, 7.5, 109, 113, -14, -1, "paint2"),
        # Central crest ridge
        B(-2, 2, 112, 115, -15, -2, "hazard"),
        # Swept aerodynamic cheek and jaw armor
        B(-11.5, -8.5, 96, 107, -14, -3, "paint2"),
        B(8.5, 11.5, 96, 107, -14, -3, "paint2"),
        # Chin audio/air intake vent
        B(-4.5, 4.5, 96, 98.5, -13.5, -8, "vent"),
        # Dual swept-back antenna ears (Sutherland signature profile)
        B(-13.0, -10.5, 102, 115, -5, 3, "paint2"),
        B(10.5, 13.0, 102, 115, -5, 3, "paint2"),
        # Factsphere primary optic sensor housing
        B(-4, 4, 104, 108.5, -14.8, -12, "metal")
    ]

# ------------------------------------------------ Sutherland Chest & Lower Hatch
SUTHERLAND_CHEST = [
    # Core cabin hull with high-speed V-taper
    B(-15, 15, 85, 108, -7, 15, "paint"),
    B(-12, 12, 79, 85, -4, 13, "dark"),
    # Side armor ribs
    B(-18, -15, 87, 105, -4, 13, "paint2"),
    B(15, 18, 87, 105, -4, 13, "paint2"),
    # Raised armored collar protecting the neck
    B(-14, 14, 107, 111, -5, 12, "paint2")
] + sutherland_pauldron() + mirror(sutherland_pauldron()) + sutherland_cockpit_pod()

SUTHERLAND_HATCH = [
    # Sloped front breastplate armor
    B(-13, 13, 82, 97, -13, -7, "paint", decal={"north": "number"}),
    B(-10, 10, 96, 101, -14, -7, "paint2"),
    # Center Factsphere deployment chest hatch
    B(-5, 5, 88, 94, -14.2, -12, "metal"),
    B(-3.5, 3.5, 89.5, 92.5, -14.8, -13.5, "glow"),
    # Lower bumper hazard stripe & recovery hook
    B(-13.5, 13.5, 80.5, 82.5, -13.5, -7, "hazard"),
    B(-2.5, 2.5, 79, 82, -15, -13.5, "steel")
] + sutherland_slash_harken(-8.5, 89, -13.5) + sutherland_slash_harken(8.5, 89, -13.5)

# ------------------------------------------------ Sutherland Arms & Gauntlets
SUTHERLAND_ARM1 = ball(-24.4, 94.8, 10.7, 9) + [
    # Sleek bicep core with mechanical hydraulic sleeve
    B(-28, -20, 75, 89, 6, 15, "dark"),
    B(-29, -19, 77, 87, 5, 16, "paint"),
    B(-28.5, -19.5, 78, 86, 4, 5.5, "paint2")
] + hub(-24, 75, 10.5, 12, 8) + piston(-24, 88, 77, 17, w=2.0)

SUTHERLAND_ARM2 = [
    # Sutherland forearm gauntlet with chamfered weapon rail
    B(-31.5, -16.5, 50, 71, 2, 19, "paint"),
    B(-33.0, -31.0, 54, 68, 4, 17, "paint2"),
    B(-17.0, -15.0, 54, 68, 4, 17, "paint2"),
    # Stun tonfa hardpoint mounting rail
    B(-33.5, -32.0, 57, 66, 8, 13, "metal"),
    B(-32.5, -15.5, 68, 72, 3, 18, "metal"),
    B(-29.5, -18.5, 46, 50, 4, 17, "dark")
]

SUTHERLAND_HAND = fist(-27, 48, 7) + hub(-23.3, 48, 11, 8, 4.5)

# ------------------------------------------------ Sutherland Pelvis, Legs & Landspinners
SUTHERLAND_LEG3 = [
    # Hip joint with Slash Harken tether spool drum housing
    B(-22, -18, 50, 62, -2, 14, "paint"),
    B(-23, -21.5, 52, 60, 1, 11, "hazard"),
    B(-17, -11, 52, 63, 1, 11, "dark")
] + hub(-14.5, 57, 6, 16, 10)

SUTHERLAND_LEG2 = [
    # Athletic thigh armor plate
    B(-20, -9, 31, 48, -4, 9, "paint"),
    B(-19.5, -9.5, 33, 46, -6, -3.5, "paint2"),
    B(-21, -20, 34, 45, -2, 7, "paint2"),
    B(-18, -11, 26, 31, -2, 7, "dark")
] + piston(-14.5, 45, 32, -7.5) + hose(-18, 45, 32, 11, 2.0)

SUTHERLAND_LEG1 = [
    # High-mobility shin with sharp knee cop and Landspinner assembly
    B(-21, -8, 20, 35, -12, -4, "paint"),
    B(-20, -9, 33, 36, -11, -5, "paint2"),
    B(-21, -8, 6, 22, -8, 8, "paint"),
    B(-19.5, -9.5, 8, 20, -9.5, -7.5, "paint2"),
    B(-22, -21, 9, 20, -5, 6, "paint2"),
    B(-19, -10, 8, 21, 8, 12, "dark")
] + hub(-14.5, 23, 1, 15, 8) + sutherland_landspinner(-22.5, 9, 8, is_left=False)

SUTHERLAND_FOOT = [
    # High-mobility split-toe combat boot with magnetic sole
    B(-22, -7, 0, 4, -20, 10, "dark"),
    B(-21, -8, 0, 7, -21, -11, "paint"),
    B(-21.5, -7.5, 0, 2, -21.5, -19, "hazard"),
    B(-20, -9, 4, 9, -12, 3, "paint2"),
    B(-20.5, -8.5, 0, 6, 5, 11, "metal")
] + hub(-14.5, 6.5, -1, 12, 6)

# ------------------------------------------------ Assemble Complete Bone Hierarchy
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
    ("body3", "body2", [0.5, 78.7, 17.8], SUTHERLAND_CHEST),
    ("doorUp", "body3", [0, 107, -8], sutherland_head()),
    ("eye", "doorUp", [0, 107.0, -17.0], [
        # Sutherland cyan Factsphere scanning camera visor
        B(-8, 8, 102, 105, -14.8, -13.8, "visor")
    ]),
    ("doorDown", "body3", [0, 82.7, -5.9], SUTHERLAND_HATCH),
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
    ("rightArm1", "body3", [-24.4, 94.8, 10.7], SUTHERLAND_ARM1),
    ("rightArm2", "rightArm1", [-23.4, 72.5, 10.7], SUTHERLAND_ARM2),
    ("rightHand", "rightArm2", [-23.3, 46.8, 11.5], SUTHERLAND_HAND),
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
    ("leftArm1", "body3", [24.4, 94.8, 10.7], mirror(SUTHERLAND_ARM1)),
    ("leftArm2", "leftArm1", [23.4, 72.5, 10.7], mirror(SUTHERLAND_ARM2)),
    ("leftHand", "leftArm2", [23.3, 46.8, 11.5], mirror(SUTHERLAND_HAND)),
    ("rightLeg3", "titan", [-14.5, 61.1, 7.1], SUTHERLAND_LEG3),
    ("rightLeg2", "rightLeg3", [-14.5, 43.5, 2.7], SUTHERLAND_LEG2),
    ("rightLeg1", "rightLeg2", [-14.5, 22.8, 3.4], SUTHERLAND_LEG1),
    ("rightFoot", "rightLeg1", [-14.5, 0.0, 0.0], SUTHERLAND_FOOT),
    ("leftLeg3", "titan", [14.5, 61.1, 7.1], mirror(SUTHERLAND_LEG3)),
    ("leftLeg2", "leftLeg3", [14.5, 43.5, 2.7], mirror(SUTHERLAND_LEG2)),
    ("leftLeg1", "leftLeg2", [14.5, 22.8, 3.4], [
        B(8, 21, 20, 35, -12, -4, "paint"),
        B(9, 20, 33, 36, -11, -5, "paint2"),
        B(8, 21, 6, 22, -8, 8, "paint"),
        B(9.5, 19.5, 8, 20, -9.5, -7.5, "paint2"),
        B(21, 22, 9, 20, -5, 6, "paint2"),
        B(10, 19, 8, 21, 8, 12, "dark")
    ] + hub(14.5, 23, 1, 15, 8) + sutherland_landspinner(22.5, 9, 8, is_left=True)),
    ("leftFoot", "leftLeg1", [14.5, 0.0, 0.0], mirror(SUTHERLAND_FOOT)),
]

# ------------------------------------------------ Authentic Sutherland Color Palettes
# (name, paint, paint2, visor)
T.SCHEMES = [
    # 0: Standard Britannia Military Sutherland (Slate Blue-Gray / Lilac)
    ("sutherland_standard", (82, 96, 114), (60, 72, 88), (56, 232, 255)),
    # 1: Purist Faction (Jeremiah Gottwald - Orange shoulder flare)
    ("sutherland_purist", (84, 98, 116), (228, 124, 28), (56, 232, 255)),
    # 2: Royal Guard (Gloucester Crimson)
    ("sutherland_royal", (148, 42, 40), (108, 28, 26), (255, 210, 40)),
    # 3: Desert Camo (Britannian Middle-East campaign)
    ("sutherland_desert", (186, 158, 116), (146, 122, 88), (56, 220, 255)),
    # 4: Arctic Snow (Euro-Britannia winter front)
    ("sutherland_arctic", (212, 216, 220), (168, 174, 180), (48, 230, 255)),
    # 5: Tokyo Settlement Urban Security
    ("sutherland_urban", (112, 118, 124), (82, 86, 92), (255, 102, 51)),
    # 6: Black Knights Captured Sutherland (Zero command)
    ("sutherland_blackknights", (34, 36, 40), (22, 24, 26), (255, 59, 48)),
    # 7: Hazard Testing Prototype
    ("sutherland_prototype", (224, 124, 30), (172, 92, 20), (255, 214, 40)),
    # 8: Area 11 Forest Camo
    ("sutherland_forest", (64, 88, 60), (46, 66, 44), (82, 255, 133))
]

print("Building RPI-13 Sutherland Knightmare Frame assets...")
T.main()
print("SUCCESS: RPI-13 Sutherland Knightmare Frame built!")
