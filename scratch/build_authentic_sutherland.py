"""RPI-13 Sutherland - Code Geass Knightmare Frame
100% Brand-New Scratch-Built Geometry & Textures.
ZERO trace of the old industrial MP-01 dieselpunk box model.

Features:
- Authentic chiseled Sutherland dome helmet with Factsphere forehead optic & twin swept antenna fins.
- Athletic V-tapered chest with integrated dual chest Slash Harken rocket-anchor pods.
- Iconic rear-mounted dorsal cockpit ejection capsule with dual angled rocket thrusters.
- Narrow mechanical waist with central spine and flanking hydraulic rams.
- Chamfered, aerodynamic Sutherland knight pauldrons (NO giant flat shipping boxes).
- Slender athletic arms with mechanical elbow hinges and gauntlet side rails.
- High-mobility split-toe combat feet (rightFoot, leftFoot).
- Authentic Landspinner folding roller wheel units on outer ankles with swing-arms, hydraulic struts, tires, and fenders.
- 9 authentic Code Geass liveries (Britannia Army Slate, Glinda Knights, Purist Faction, Special Ops, etc.).
- Modular armor archetype mounts for all 8 archetypes.
"""

import json, os, struct, zlib, math

TEX_SIZE = 1024
GEO_DIR = "Titan Combat/src/main/resources/assets/titancombat/geo"
TEX_DIR = "Titan Combat/src/main/resources/assets/titancombat/textures/entity/titan/exo_frame"

def C(origin, size, uv, rot=None, piv=None):
    c = {"origin": [round(x, 2) for x in origin], "size": [round(x, 2) for x in size], "uv": uv}
    if rot and piv:
        c["rotation"] = [round(x, 2) for x in rot]
        c["pivot"] = [round(x, 2) for x in piv]
    return c

def build_sutherland_model():
    bones = []

    # ------------------------------------------------ ROOT
    bones.append({
        "name": "root",
        "pivot": [0, 0, 0],
        "cubes": []
    })

    # ------------------------------------------------ BODY 1 (Pelvis & Hip Girdle)
    b1_cubes = [
        # Central pelvic core
        C([-4.5, 46, -3.5], [9, 6, 7], [0, 0]),
        # Front grooved groin armor chevron
        C([-3.5, 45, -4.5], [7, 5, 2], [32, 0]),
        # Rear pelvic exhaust vent
        C([-3.5, 47, 3.5], [7, 4, 1.5], [50, 0]),
        # Left and right hip ball-joint housings
        C([-7.5, 46.5, -2.5], [3, 5, 5], [68, 0]),
        C([4.5, 46.5, -2.5], [3, 5, 5], [68, 0]),
        # Glancing side hip skirt plates
        C([-8.5, 45, -3.5], [1.5, 6, 7], [84, 0]),
        C([7.0, 45, -3.5], [1.5, 6, 7], [84, 0]),
    ]
    bones.append({
        "name": "body1",
        "parent": "root",
        "pivot": [0, 48, 0],
        "cubes": b1_cubes
    })

    # ------------------------------------------------ BODY 2 (Mechanical Waist & Hydraulic Rams)
    b2_cubes = [
        # Central spine / articulated column
        C([-3, 52, -2.5], [6, 10, 5], [0, 14]),
        # Twin forward hydraulic cylinder housings
        C([-4, 53, -3.5], [2.2, 8, 2.2], [22, 14]),
        C([1.8, 53, -3.5], [2.2, 8, 2.2], [22, 14]),
        # Chrome piston shafts
        C([-3.6, 55, -3.1], [1.4, 5, 1.4], [31, 14]),
        C([2.2, 55, -3.1], [1.4, 5, 1.4], [31, 14]),
        # Rear power conduits / wiring harness
        C([-2, 53, 2.5], [4, 8, 1.5], [38, 14]),
        # Flank reinforcement struts
        C([-5, 54, -1.5], [1.5, 7, 3], [50, 14]),
        C([3.5, 54, -1.5], [1.5, 7, 3], [50, 14]),
    ]
    bones.append({
        "name": "body2",
        "parent": "body1",
        "pivot": [0, 52, 0],
        "cubes": b2_cubes
    })

    # ------------------------------------------------ BODY 3 (Athletic V-Taper Torso & Cockpit Pod)
    b3_cubes = [
        # Lower ribcage / V-taper transition
        C([-5.5, 62, -4], [11, 4, 8], [0, 30]),
        # Main upper chest chassis (athletic taper, wide shoulders)
        C([-7.5, 66, -5], [15, 8, 10], [38, 30]),
        # Front chest center armor breastplate
        C([-4.5, 67, -6.2], [9, 7, 1.8], [88, 30]),
        # Factsphere chest sensor array / telemetry block
        C([-2.5, 71, -6.6], [5, 2.5, 0.8], [0, 50]),
        # Collar armor ring protecting head neck ring
        C([-5, 74, -4.5], [10, 2, 9], [12, 50]),

        # --- DUAL CHEST SLASH HARKEN PODS (The signature Code Geass weapon)
        # Right Slash Harken rocket anchor housing & pointed projectile tip
        C([-7.2, 68, -6.0], [2.6, 4.5, 1.8], [52, 50]),
        C([-6.7, 69, -6.8], [1.6, 2.5, 1.0], [62, 50]),
        # Left Slash Harken rocket anchor housing & pointed projectile tip
        C([4.6, 68, -6.0], [2.6, 4.5, 1.8], [52, 50]),
        C([5.1, 69, -6.8], [1.6, 2.5, 1.0], [62, 50]),

        # --- DORSAL EJECTION COCKPIT CAPSULE (Rear upper back pod)
        # Main ejection pod hull (angled 15 degrees backward)
        C([-5, 65, 4.5], [10, 11, 7], [0, 64], rot=[-15, 0, 0], piv=[0, 65, 4.5]),
        # Cockpit pod roof aerodynamic canopy ridge
        C([-3.5, 73, 5.0], [7, 3.5, 5], [35, 64], rot=[-15, 0, 0], piv=[0, 65, 4.5]),
        # Dual emergency rocket ejection thrusters (bottom of dorsal pod)
        C([-4.2, 63, 7.5], [2.8, 3.5, 2.8], [60, 64], rot=[-25, 0, 0], piv=[0, 63, 7.5]),
        C([1.4, 63, 7.5], [2.8, 3.5, 2.8], [60, 64], rot=[-25, 0, 0], piv=[0, 63, 7.5]),
        # Thruster exhaust bells
        C([-4.6, 61.5, 8.2], [3.6, 1.8, 3.6], [72, 64], rot=[-25, 0, 0], piv=[0, 61.5, 8.2]),
        C([1.0, 61.5, 8.2], [3.6, 1.8, 3.6], [72, 64], rot=[-25, 0, 0], piv=[0, 61.5, 8.2]),
    ]
    bones.append({
        "name": "body3",
        "parent": "body2",
        "pivot": [0, 62, 0],
        "cubes": b3_cubes
    })

    # Cockpit door bones (for hatch open/park animations)
    bones.append({
        "name": "doorUp",
        "parent": "body3",
        "pivot": [0, 74, -5],
        "cubes": []
    })
    bones.append({
        "name": "doorDown",
        "parent": "body3",
        "pivot": [0, 65, -5],
        "cubes": []
    })
    # Stowed weapon back mount
    bones.append({
        "name": "weaponBack",
        "parent": "body3",
        "pivot": [5, 68, 6],
        "rotation": [0, 180, 0],
        "cubes": []
    })

    # ------------------------------------------------ HEAD (Chiseled Sutherland Helmet & Factsphere)
    head_cubes = [
        # Neck ring
        C([-2, 74, -1.5], [4, 2, 3], [0, 85]),
        # Main chiseled helmet dome
        C([-3.5, 76, -3.5], [7, 6.5, 7], [15, 85]),
        # Slanted forehead plate
        C([-3, 78, -4.5], [6, 4.5, 1.5], [44, 85]),
        # FACTSPHERE OPTIC (Forehead Crest Sensor Lens)
        C([-1.5, 79, -5.2], [3, 2.5, 1.0], [60, 85]),
        # Lower chiseled jaw / chin guard
        C([-2, 75.5, -4.2], [4, 2.5, 2.0], [70, 85]),
        # Ear / temple sensor caps
        C([-4.2, 77, -1.5], [1, 4, 4], [82, 85]),
        C([3.2, 77, -1.5], [1, 4, 4], [82, 85]),
        # Swept Britannian Antenna Fins (Left & Right)
        C([-4.5, 80, 0], [0.8, 5, 2.5], [94, 85], rot=[20, 0, -15], piv=[-4.5, 80, 0]),
        C([3.7, 80, 0], [0.8, 5, 2.5], [94, 85], rot=[20, 0, 15], piv=[3.7, 80, 0]),
    ]
    bones.append({
        "name": "head",
        "parent": "body3",
        "pivot": [0, 75, 0],
        "cubes": head_cubes
    })

    # ------------------------------------------------ ARMS (Right & Left)
    # Right Arm 1 (Shoulder pauldron & Upper arm)
    r_arm1_cubes = [
        # Shoulder ball joint
        C([-10.5, 71, -2], [3, 3, 4], [0, 100]),
        # Sutherland Chamfered Shoulder Pauldron (aerodynamic knight shoulder)
        C([-14.5, 70, -3.5], [5, 6, 7], [15, 100]),
        C([-15.2, 72, -3.0], [1, 3.5, 6], [40, 100]),
        # Upper arm bicep strut
        C([-12.5, 63, -2], [3, 7, 4], [55, 100]),
    ]
    bones.append({
        "name": "rightArm1",
        "parent": "body3",
        "pivot": [-9, 73, 0],
        "cubes": r_arm1_cubes
    })

    # Right Arm 2 (Elbow hinge & Gauntlet)
    r_arm2_cubes = [
        # Elbow mechanical hinge
        C([-12.5, 59, -1.5], [3, 4, 3], [70, 100]),
        # Forearm armor gauntlet with outer weapon mounting rail
        C([-13.5, 48, -2.5], [4, 11, 5], [0, 115]),
        # Outer gauntlet equipment rail / armor ridge
        C([-14.5, 50, -2.0], [1.2, 8, 4], [19, 115]),
    ]
    bones.append({
        "name": "rightArm2",
        "parent": "rightArm1",
        "pivot": [-11, 61, 0],
        "cubes": r_arm2_cubes
    })

    # Right Hand (Manipulator)
    r_hand_cubes = [
        C([-13, 43, -2], [3, 5, 4], [32, 115]),
        C([-12.8, 41, -1.5], [2.6, 2, 3], [47, 115]),
    ]
    bones.append({
        "name": "rightHand",
        "parent": "rightArm2",
        "pivot": [-11.5, 47, 0],
        "cubes": r_hand_cubes
    })

    # Weapon mount bone
    bones.append({
        "name": "weapon",
        "parent": "rightHand",
        "pivot": [-11.5, 42, 0],
        "cubes": []
    })

    # Left Arm 1 (Shoulder pauldron & Upper arm)
    l_arm1_cubes = [
        C([7.5, 71, -2], [3, 3, 4], [0, 100]),
        C([9.5, 70, -3.5], [5, 6, 7], [15, 100]),
        C([14.2, 72, -3.0], [1, 3.5, 6], [40, 100]),
        C([9.5, 63, -2], [3, 7, 4], [55, 100]),
    ]
    bones.append({
        "name": "leftArm1",
        "parent": "body3",
        "pivot": [9, 73, 0],
        "cubes": l_arm1_cubes
    })

    # Left Arm 2 (Elbow hinge & Gauntlet)
    l_arm2_cubes = [
        C([9.5, 59, -1.5], [3, 4, 3], [70, 100]),
        C([9.5, 48, -2.5], [4, 11, 5], [0, 115]),
        C([13.3, 50, -2.0], [1.2, 8, 4], [19, 115]),
    ]
    bones.append({
        "name": "leftArm2",
        "parent": "leftArm1",
        "pivot": [11, 61, 0],
        "cubes": l_arm2_cubes
    })

    # Left Hand (Manipulator)
    l_hand_cubes = [
        C([10, 43, -2], [3, 5, 4], [32, 115]),
        C([10.2, 41, -1.5], [2.6, 2, 3], [47, 115]),
    ]
    bones.append({
        "name": "leftHand",
        "parent": "leftArm2",
        "pivot": [11.5, 47, 0],
        "cubes": l_hand_cubes
    })

    # ------------------------------------------------ LEGS (Thighs, Calves, Landspinners, Feet)
    # Right Leg 3 (Thigh)
    r_leg3_cubes = [
        # Thigh core and frontal armor bevel
        C([-8.5, 32, -3], [5, 14, 6], [0, 132]),
        C([-8.0, 34, -4.2], [4, 10, 1.5], [23, 132]),
        # Knee armor cap
        C([-8.5, 30, -4.5], [5, 4, 3], [36, 132]),
    ]
    bones.append({
        "name": "rightLeg3",
        "parent": "body1",
        "pivot": [-6, 46, 0],
        "cubes": r_leg3_cubes
    })

    # Right Leg 2 (Calf & Shin & Landspinner)
    r_leg2_cubes = [
        # Knee joint hinge
        C([-8, 27, -2], [4, 4, 4], [53, 132]),
        # Athletic shin armor plate
        C([-8.5, 8, -4], [5, 19, 6], [70, 132]),
        C([-8.0, 10, -5.2], [4, 14, 1.5], [0, 158]),
        # Rear calf thruster / muscular housing
        C([-8.0, 12, 1.8], [4, 12, 3], [13, 158]),

        # --- RIGHT ANKLE LANDSPINNER UNIT (Folding Roller Wheel)
        # Swing-arm suspension strut mounting to outer ankle
        C([-11.8, 4, -1], [3, 7, 2.5], [29, 158]),
        # Hydraulic deploy cylinder
        C([-11.5, 7, 0.5], [1.8, 5, 1.8], [42, 158]),
        # Landspinner roller tire (octagonal profile, radius ~3.5)
        C([-12.5, 1, -3], [2.8, 6, 6], [51, 158]),
        # Central Landspinner gold rim hub
        C([-12.8, 2.5, -1.5], [0.8, 3, 3], [70, 158]),
        # Top aerodynamic mudguard fender
        C([-12.8, 6.5, -3.5], [3.2, 1.5, 7], [79, 158]),
    ]
    bones.append({
        "name": "rightLeg2",
        "parent": "rightLeg3",
        "pivot": [-6, 30, 0],
        "cubes": r_leg2_cubes
    })

    # Right Foot (Split-Toe Combat Foot)
    r_foot_cubes = [
        # Ankle ball joint
        C([-8, 5, -2], [4, 3, 4], [0, 175]),
        # Main foot sole base
        C([-8.5, 0, -5], [5, 3.5, 8], [17, 175]),
        # Split front toes (dual articulated toe claws)
        C([-8.5, 0, -8], [2.2, 2.5, 3.5], [45, 175]),
        C([-5.7, 0, -8], [2.2, 2.5, 3.5], [45, 175]),
        # Rear heel spur
        C([-8.0, 0, 3], [4, 3, 2.5], [58, 175]),
    ]
    bones.append({
        "name": "rightFoot",
        "parent": "rightLeg2",
        "pivot": [-6, 6, 0],
        "cubes": r_foot_cubes
    })
    # Alias rightLeg1 to rightFoot for backwards compat
    bones.append({
        "name": "rightLeg1",
        "parent": "rightFoot",
        "pivot": [-6, 6, 0],
        "cubes": []
    })

    # Left Leg 3 (Thigh)
    l_leg3_cubes = [
        C([3.5, 32, -3], [5, 14, 6], [0, 132]),
        C([4.0, 34, -4.2], [4, 10, 1.5], [23, 132]),
        C([3.5, 30, -4.5], [5, 4, 3], [36, 132]),
    ]
    bones.append({
        "name": "leftLeg3",
        "parent": "body1",
        "pivot": [6, 46, 0],
        "cubes": l_leg3_cubes
    })

    # Left Leg 2 (Calf & Shin & Landspinner)
    l_leg2_cubes = [
        C([4, 27, -2], [4, 4, 4], [53, 132]),
        C([3.5, 8, -4], [5, 19, 6], [70, 132]),
        C([4.0, 10, -5.2], [4, 14, 1.5], [0, 158]),
        C([4.0, 12, 1.8], [4, 12, 3], [13, 158]),

        # --- LEFT ANKLE LANDSPINNER UNIT
        C([8.8, 4, -1], [3, 7, 2.5], [29, 158]),
        C([9.7, 7, 0.5], [1.8, 5, 1.8], [42, 158]),
        C([9.7, 1, -3], [2.8, 6, 6], [51, 158]),
        C([12.0, 2.5, -1.5], [0.8, 3, 3], [70, 158]),
        C([9.6, 6.5, -3.5], [3.2, 1.5, 7], [79, 158]),
    ]
    bones.append({
        "name": "leftLeg2",
        "parent": "leftLeg3",
        "pivot": [6, 30, 0],
        "cubes": l_leg2_cubes
    })

    # Left Foot
    l_foot_cubes = [
        C([4, 5, -2], [4, 3, 4], [0, 175]),
        C([3.5, 0, -5], [5, 3.5, 8], [17, 175]),
        C([3.5, 0, -8], [2.2, 2.5, 3.5], [45, 175]),
        C([6.3, 0, -8], [2.2, 2.5, 3.5], [45, 175]),
        C([4.0, 0, 3], [4, 3, 2.5], [58, 175]),
    ]
    bones.append({
        "name": "leftFoot",
        "parent": "leftLeg2",
        "pivot": [6, 6, 0],
        "cubes": l_foot_cubes
    })
    # Alias leftLeg1 to leftFoot
    bones.append({
        "name": "leftLeg1",
        "parent": "leftFoot",
        "pivot": [6, 6, 0],
        "cubes": []
    })

    return bones

def add_modular_armor_bones(bones):
    """Adds the 48 modular armor archetype bones onto the Sutherland frame."""
    archetypes = [
        ("infantry", [250, 0]),
        ("siege", [280, 0]),
        ("samurai", [310, 0]),
        ("aero", [340, 0]),
        ("scrap", [370, 0]),
        ("stealth", [400, 0]),
        ("sovereign", [430, 0]),
        ("expedition", [460, 0])
    ]

    for arch_name, uv_base in archetypes:
        u, v = uv_base
        # Head armor
        bones.append({
            "name": f"armor_head_{arch_name}",
            "parent": "head",
            "pivot": [0, 75, 0],
            "cubes": [
                C([-4.2, 75.5, -4.2], [8.4, 7.5, 8.4], [u, v]),
                C([-3.0, 81.5, -5.0], [6.0, 2.5, 3.0], [u + 35, v])
            ]
        })
        # Chest armor
        bones.append({
            "name": f"armor_chest_{arch_name}",
            "parent": "body3",
            "pivot": [0, 62, 0],
            "cubes": [
                C([-8.2, 65.5, -5.8], [16.4, 9.0, 11.2], [u, v + 25]),
                C([-5.0, 66.0, -7.0], [10.0, 7.5, 2.0], [u + 56, v + 25])
            ]
        })
        # Right Arm armor
        bones.append({
            "name": f"armor_right_arm_{arch_name}",
            "parent": "rightArm1",
            "pivot": [-9, 73, 0],
            "cubes": [
                C([-15.5, 69.5, -4.2], [6.8, 7.5, 8.4], [u, v + 50]),
                C([-14.2, 47.5, -3.2], [5.2, 12.0, 6.2], [u + 32, v + 50])
            ]
        })
        # Left Arm armor
        bones.append({
            "name": f"armor_left_arm_{arch_name}",
            "parent": "leftArm1",
            "pivot": [9, 73, 0],
            "cubes": [
                C([8.7, 69.5, -4.2], [6.8, 7.5, 8.4], [u, v + 50]),
                C([9.0, 47.5, -3.2], [5.2, 12.0, 6.2], [u + 32, v + 50])
            ]
        })
        # Right Leg armor
        bones.append({
            "name": f"armor_right_leg_{arch_name}",
            "parent": "rightLeg3",
            "pivot": [-6, 46, 0],
            "cubes": [
                C([-9.2, 31.5, -3.8], [6.2, 14.5, 7.4], [u, v + 75]),
                C([-9.2, 7.5, -4.8], [6.2, 20.0, 7.4], [u + 28, v + 75])
            ]
        })
        # Left Leg armor
        bones.append({
            "name": f"armor_left_leg_{arch_name}",
            "parent": "leftLeg3",
            "pivot": [6, 46, 0],
            "cubes": [
                C([3.0, 31.5, -3.8], [6.2, 14.5, 7.4], [u, v + 75]),
                C([3.0, 7.5, -4.8], [6.2, 20.0, 7.4], [u + 28, v + 75])
            ]
        })

def export_geo():
    bones = build_sutherland_model()
    add_modular_armor_bones(bones)

    geo_data = {
        "format_version": "1.12.0",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": "geometry.exo_frame_titan",
                    "texture_width": TEX_SIZE,
                    "texture_height": TEX_SIZE,
                    "visible_bounds_width": 4.5,
                    "visible_bounds_height": 5.5,
                    "visible_bounds_offset": [0, 2.5, 0]
                },
                "bones": bones
            }
        ]
    }

    out_path = os.path.join(GEO_DIR, "exo_frame_titan.geo.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geo_data, f, indent=2)
    print(f"[OK] Wrote authentic Sutherland geometry: {out_path} ({len(bones)} bones)")

# ------------------------------------------------ TEXTURE GENERATION
def write_png(path, width, height, rgba_data):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    raw = bytearray()
    for y in range(height):
        raw.append(0) # filter byte none
        start = y * width * 4
        raw.extend(rgba_data[start:start + width * 4])

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")

    with open(path, "wb") as f:
        f.write(png)

# 9 Authentic Sutherland Schemes
SCHEMES = [
    # 0: Standard Britannian Army (Slate Purple / Gold)
    {"name": "Britannia Standard", "base": (92, 88, 108), "trim": (212, 160, 56), "steel": (45, 45, 54), "eye": (255, 32, 56)},
    # 1: Glinda Knights (Pure White / Royal Gold)
    {"name": "Glinda Knights", "base": (230, 230, 238), "trim": (220, 175, 45), "steel": (60, 60, 72), "eye": (40, 180, 255)},
    # 2: Purist Faction (Blood Red / Pitch Black)
    {"name": "Purist Faction", "base": (40, 38, 44), "trim": (195, 35, 40), "steel": (30, 30, 35), "eye": (255, 200, 30)},
    # 3: Special Ops Infiltrator (Matte Stealth Black / Emerald)
    {"name": "Special Ops", "base": (28, 28, 32), "trim": (48, 52, 60), "steel": (20, 20, 24), "eye": (30, 230, 110)},
    # 4: Desert Recon (Area 11 Sand Camo)
    {"name": "Desert Recon", "base": (175, 155, 125), "trim": (130, 110, 85), "steel": (50, 48, 45), "eye": (255, 120, 30)},
    # 5: Arctic Frontier (Glacier White / Navy Blue)
    {"name": "Arctic Frontier", "base": (215, 225, 235), "trim": (45, 80, 140), "steel": (55, 65, 75), "eye": (0, 210, 255)},
    # 6: Urban Suppression (Cobalt Blue / Steel Grey)
    {"name": "Urban Suppression", "base": (55, 75, 115), "trim": (180, 185, 195), "steel": (35, 40, 50), "eye": (255, 40, 40)},
    # 7: Imperial Royal Guard (Crimson / Polished Gold)
    {"name": "Royal Guard", "base": (145, 25, 35), "trim": (230, 185, 55), "steel": (45, 35, 40), "eye": (255, 220, 40)},
    # 8: Guren Vermilion (Scarlet Vermilion / Charcoal)
    {"name": "Guren Vermilion", "base": (175, 30, 30), "trim": (220, 140, 35), "steel": (35, 32, 35), "eye": (80, 255, 120)},
]

def generate_textures():
    os.makedirs(TEX_DIR, exist_ok=True)

    for idx, s in enumerate(SCHEMES):
        buf = bytearray(TEX_SIZE * TEX_SIZE * 4)
        base = s["base"]
        trim = s["trim"]
        steel = s["steel"]
        eye = s["eye"]

        def fill_rect(u, v, w, h, col):
            for y in range(v, min(v + h, TEX_SIZE)):
                for x in range(u, min(u + w, TEX_SIZE)):
                    noise = (x * 13 + y * 37) % 7 - 3
                    r = max(0, min(255, col[0] + noise))
                    g = max(0, min(255, col[1] + noise))
                    b = max(0, min(255, col[2] + noise))
                    idx_px = (y * TEX_SIZE + x) * 4
                    buf[idx_px] = r
                    buf[idx_px + 1] = g
                    buf[idx_px + 2] = b
                    buf[idx_px + 3] = 255

        # 1. Base armor regions (Pelvis, Ribs, Pauldrons, Shins, Helmet)
        fill_rect(0, 0, 120, 220, base)
        # 2. Mechanical frame & Hydraulics (Spine, Joints, Axles, Hands)
        fill_rect(0, 14, 50, 16, steel)
        fill_rect(70, 100, 30, 30, steel)
        fill_rect(53, 132, 18, 18, steel)
        fill_rect(0, 175, 17, 17, steel)
        # 3. Imperial Gold / Accent Trim (Slash Harken rings, Pauldron trim, Antennae)
        fill_rect(88, 30, 20, 15, trim)
        fill_rect(52, 50, 20, 10, trim)
        fill_rect(94, 85, 10, 15, trim)
        fill_rect(70, 158, 9, 9, trim) # Landspinner rim hub
        # 4. Landspinner High-Grip Rubber Tires
        fill_rect(51, 158, 19, 17, (25, 25, 28))
        # 5. Dorsal Cockpit Pod Thruster Nozzles
        fill_rect(60, 64, 25, 18, steel)
        fill_rect(72, 64, 15, 10, (180, 80, 40)) # Heat discoloration on thruster bells
        # 6. Factsphere Crystal Optic Lens (Ruby glowing red/custom eye)
        fill_rect(60, 85, 10, 8, eye)
        fill_rect(0, 50, 12, 8, eye) # Chest telemetry lens

        # 7. Modular Armor Archetypes Regions (Vanguard, Siege, Samurai, Aero, Scrap, Stealth, Sovereign, Expedition)
        arch_colors = [
            (50, 120, 180),   # Infantry/Vanguard: Apex Blue
            (110, 110, 120),  # Siege/Juggernaut: Heavy Steel
            (180, 45, 45),    # Samurai/Ronin: Crimson
            (210, 210, 220),  # Aero/Valkyrie: Pure White
            (140, 95, 60),    # Scrap/Raider: Rust Brown
            (35, 35, 40),     # Stealth/Phantom: Carbon Black
            (215, 175, 40),   # Sovereign/Paladin: Royal Gold
            (75, 125, 75),    # Expedition/Ranger: Forest Green
        ]
        for a_idx, ac in enumerate(arch_colors):
            u_arch = 250 + a_idx * 30
            fill_rect(u_arch, 0, 30, 150, ac)
            fill_rect(u_arch + 10, 0, 10, 150, trim)

        out_name = "exo_frame_titan.png" if idx == 0 else f"exo_frame_titan_{idx}.png"
        out_path = os.path.join(TEX_DIR, out_name)
        write_png(out_path, TEX_SIZE, TEX_SIZE, buf)
        print(f"[OK] Wrote Sutherland texture [{idx}]: {s['name']} -> {out_name}")

if __name__ == "__main__":
    export_geo()
    generate_textures()
