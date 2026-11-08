"""Comprehensive RPI-13 Sutherland (Code Geass Knightmare Frame) Asset Builder
Overhauls the entire geometry, bone pivots, animations alignment, modular armors, and textures.

1. Bone pivots and rest-rotations strictly match the Titan animation rig (no more limb separation!).
2. Athletic V-taper silhouette, chiseled Sutherland helmet, Factsphere red optic, swept antennae,
   chest Slash Harkens, rear dorsal ejection cockpit pod with twin thrusters, Landspinner ankle units,
   and split-toe feet.
3. Modular armors tailored cleanly to the frame (no bloated cardboard boxes).
4. Textures generated with baked ambient occlusion, engraved panel lines, metallic edge highlights,
   and glowing sensor optics.
"""

import os, json, struct, zlib, math

TEX_SIZE = 1024
GEO_PATH = "Titan Combat/src/main/resources/assets/titancombat/geo/exo_frame_titan.geo.json"
TEX_DIR = "Titan Combat/src/main/resources/assets/titancombat/textures/entity/titan/exo_frame"

def C(origin, size, uv, rot=None, piv=None):
    c = {
        "origin": [round(float(x), 3) for x in origin],
        "size": [round(float(x), 3) for x in size],
        "uv": uv
    }
    if rot and piv:
        c["rotation"] = [round(float(x), 3) for x in rot]
        c["pivot"] = [round(float(x), 3) for x in piv]
    return c

def build_sutherland_geo():
    bones = []

    # 1. ROOT & TITAN
    bones.append({"name": "bb_main", "pivot": [0, 0, 0], "cubes": []})
    bones.append({"name": "skill_locator", "pivot": [0, 0, 0], "cubes": []})
    bones.append({"name": "titan", "pivot": [0, 0, 0], "cubes": []})

    # 2. BODY 1 (Pelvis & Hip Girdle - Pivot at [0, 61.0, 7.0])
    b1_cubes = [
        # Central pelvis core
        C([-9.0, 56.0, 0.0], [18.0, 9.0, 14.0], [0, 0]),
        # Front grooved groin armor chevron
        C([-6.5, 52.0, -4.5], [13.0, 11.0, 5.0], [45, 0]),
        # Rear lower hull cover
        C([-7.5, 54.0, 13.5], [15.0, 10.0, 3.5], [78, 0]),
        # Left & Right Hip Ball-Joint Housings
        C([-13.0, 56.5, 2.5], [4.5, 8.0, 9.0], [0, 24]),
        C([8.5, 56.5, 2.5], [4.5, 8.0, 9.0], [0, 24]),
        # Side skirt deflection plates
        C([-14.2, 53.0, -1.0], [1.8, 10.0, 14.0], [24, 24]),
        C([12.4, 53.0, -1.0], [1.8, 10.0, 14.0], [24, 24]),
    ]
    bones.append({
        "name": "body1",
        "parent": "titan",
        "pivot": [0, 61.0, 7.0],
        "cubes": b1_cubes
    })

    # 3. BODY 2 (Mechanical Waist & Hydraulic Rams - Pivot at [0, 74.9, 8.8])
    b2_cubes = [
        # Central articulated spine column
        C([-5.0, 64.0, 4.0], [10.0, 14.0, 9.5], [54, 24]),
        # Slewing ring turret bearing
        C([-7.5, 63.0, 2.5], [15.0, 3.0, 12.5], [0, 48]),
        # Front twin hydraulic ram cylinders
        C([-6.0, 66.0, 1.0], [3.2, 10.0, 3.2], [48, 48]),
        C([2.8, 66.0, 1.0], [3.2, 10.0, 3.2], [48, 48]),
        # Chrome piston shafts
        C([-5.2, 70.0, 1.8], [1.6, 6.0, 1.6], [62, 48]),
        C([3.6, 70.0, 1.8], [1.6, 6.0, 1.6], [62, 48]),
        # Flank reinforcement armor ribs
        C([-7.5, 67.0, 5.0], [2.2, 10.0, 7.0], [70, 48]),
        C([5.3, 67.0, 5.0], [2.2, 10.0, 7.0], [70, 48]),
        # Rear high-pressure conduits
        C([-3.0, 65.0, 13.0], [6.0, 11.0, 2.0], [90, 48]),
    ]
    bones.append({
        "name": "body2",
        "parent": "body1",
        "pivot": [0, 74.9, 8.8],
        "cubes": b2_cubes
    })

    # 4. BODY 3 (Athletic V-Taper Torso & Dorsal Cockpit Pod - Pivot at [0.5, 78.7, 17.8])
    b3_cubes = [
        # Athletic lower torso / rib transition
        C([-11.0, 77.0, 0.0], [22.0, 8.0, 16.0], [0, 68]),
        # Main athletic V-taper chest chassis (broad shoulders)
        C([-15.0, 84.0, -3.0], [30.0, 18.0, 20.0], [0, 95]),
        # Front chest armor breastplate
        C([-9.0, 86.0, -6.5], [18.0, 15.0, 4.0], [82, 95]),
        # Collar ring protecting the neck joint
        C([-8.0, 101.0, -3.0], [16.0, 3.5, 14.0], [0, 135]),

        # --- DUAL CHEST SLASH HARKEN PODS (Iconic Code Geass Rocket Anchors)
        # Right Slash Harken launcher housing & pointed steel anchor head
        C([-14.0, 89.0, -6.0], [4.5, 8.0, 3.5], [50, 135]),
        C([-13.0, 91.0, -7.5], [2.5, 4.0, 2.0], [68, 135]),
        # Left Slash Harken launcher housing & pointed steel anchor head
        C([9.5, 89.0, -6.0], [4.5, 8.0, 3.5], [50, 135]),
        C([10.5, 91.0, -7.5], [2.5, 4.0, 2.0], [68, 135]),

        # --- DORSAL EJECTION COCKPIT CAPSULE (Rear Upper Cockpit Pod)
        # Main dorsal cockpit capsule hull (angled 15 deg back)
        C([-9.0, 85.0, 16.5], [18.0, 20.0, 12.0], [80, 135], rot=[-15, 0, 0], piv=[0, 85, 16.5]),
        # Aerodynamic canopy ridge
        C([-6.0, 98.0, 17.0], [12.0, 8.0, 10.0], [0, 155], rot=[-15, 0, 0], piv=[0, 85, 16.5]),
        # Emergency rocket thruster bells (twin nozzles at base of dorsal pod)
        C([-7.5, 80.0, 22.0], [4.5, 6.0, 4.5], [46, 155], rot=[-25, 0, 0], piv=[0, 80, 22]),
        C([3.0, 80.0, 22.0], [4.5, 6.0, 4.5], [46, 155], rot=[-25, 0, 0], piv=[0, 80, 22]),
        # Exhaust bell flared nozzles
        C([-8.2, 77.0, 23.2], [6.0, 3.5, 6.0], [66, 155], rot=[-25, 0, 0], piv=[0, 77, 23.2]),
        C([2.2, 77.0, 23.2], [6.0, 3.5, 6.0], [66, 155], rot=[-25, 0, 0], piv=[0, 77, 23.2]),
    ]
    bones.append({
        "name": "body3",
        "parent": "body2",
        "pivot": [0.5, 78.7, 17.8],
        "cubes": b3_cubes
    })

    # 5. HEAD / CANOPY (doorUp - Pivot at [0, 107.0, -8.0])
    head_cubes = [
        # Neck armor collar
        C([-4.5, 103.0, -4.5], [9.0, 3.0, 9.0], [0, 175]),
        # Chiseled Sutherland helmet dome
        C([-7.0, 106.0, -7.5], [14.0, 12.0, 14.0], [38, 175]),
        # Slanted aerodynamic brow plate
        C([-6.0, 109.0, -9.5], [12.0, 8.0, 2.5], [82, 175]),
        # Lower mechanical chin / jaw protector
        C([-4.0, 105.0, -9.0], [8.0, 4.5, 3.0], [0, 195]),
        # Ear / temple telemetry housings
        C([-8.2, 108.0, -4.0], [1.8, 8.0, 8.0], [24, 195]),
        C([6.4, 108.0, -4.0], [1.8, 8.0, 8.0], [24, 195]),
        # Swept Britannian Antenna Fins (Left & Right)
        C([-8.8, 114.0, -1.0], [1.4, 10.0, 4.5], [46, 195], rot=[20, 0, -15], piv=[-8.8, 114, -1]),
        C([7.4, 114.0, -1.0], [1.4, 10.0, 4.5], [46, 195], rot=[20, 0, 15], piv=[7.4, 114, -1]),
    ]
    bones.append({
        "name": "doorUp",
        "parent": "body3",
        "pivot": [0, 107.0, -8.0],
        "cubes": head_cubes
    })

    # 6. FACTSPHERE SENSOR CORE (eye - Pivot at [0, 107.0, -17.0])
    eye_cubes = [
        # Factsphere forehead crest sensor lens (Glowing Ruby Red Crystal)
        C([-3.0, 111.0, -10.5], [6.0, 5.0, 2.0], [60, 195]),
    ]
    bones.append({
        "name": "eye",
        "parent": "doorUp",
        "pivot": [0, 107.0, -17.0],
        "cubes": eye_cubes
    })

    # 7. LOWER CHEST CAB (doorDown - Pivot at [0, 82.7, -5.9])
    doorDown_cubes = [
        # Center breastplate lower armor
        C([-8.0, 80.0, -6.0], [16.0, 6.0, 2.5], [78, 195]),
    ]
    bones.append({
        "name": "doorDown",
        "parent": "body3",
        "pivot": [0, 82.7, -5.9],
        "cubes": doorDown_cubes
    })

    # Back stowed weapon clamp
    bones.append({
        "name": "weaponBack",
        "parent": "body3",
        "pivot": [-24.0, 78.0, 26.0],
        "cubes": [
            C([-28.0, 74.0, 23.0], [8.0, 14.0, 6.0], [0, 215])
        ]
    })

    # 8. RIGHT ARM (Pivot [-24.4, 94.8, 10.7], REST rot [0, -180, 30])
    r_arm1_cubes = [
        # Shoulder ball joint core
        C([-27.0, 91.0, 7.5], [5.5, 7.0, 6.5], [30, 215]),
        # Sutherland Chamfered Knight Pauldron (aerodynamic knight shoulder)
        C([-33.0, 88.0, 4.0], [11.0, 12.0, 13.0], [56, 215]),
        # Pauldron top deflector ridge & gold trim
        C([-34.0, 93.0, 5.5], [2.0, 6.5, 10.0], [0, 242]),
        # Bicep athletic armor strut
        C([-27.0, 74.0, 7.5], [6.0, 15.0, 6.5], [26, 242]),
    ]
    bones.append({
        "name": "rightArm1",
        "parent": "body3",
        "pivot": [-24.4, 94.8, 10.7],
        "rotation": [0, -180, 30],
        "cubes": r_arm1_cubes
    })

    r_arm2_cubes = [
        # Elbow mechanical hinge joint
        C([-26.5, 68.0, 8.0], [5.0, 7.0, 5.5], [54, 242]),
        # Forearm armor gauntlet with outer weapon mounting rail
        C([-27.5, 48.0, 6.5], [7.0, 20.0, 8.5], [76, 242]),
        # Outer equipment rail / armor ridge
        C([-29.0, 52.0, 7.5], [2.0, 14.0, 6.5], [0, 273]),
    ]
    bones.append({
        "name": "rightArm2",
        "parent": "rightArm1",
        "pivot": [-23.4, 72.5, 10.7],
        "cubes": r_arm2_cubes
    })

    r_hand_cubes = [
        # Wrist joint & combat manipulator / knuckles
        C([-26.0, 40.0, 7.5], [5.5, 8.0, 7.0], [19, 273]),
        C([-25.5, 36.5, 8.5], [4.5, 4.0, 5.0], [46, 273]),
    ]
    bones.append({
        "name": "rightHand",
        "parent": "rightArm2",
        "pivot": [-23.3, 46.8, 11.5],
        "rotation": [0, -180, 0],
        "cubes": r_hand_cubes
    })

    bones.append({
        "name": "weapon",
        "parent": "rightHand",
        "pivot": [-19.8, 39.8, 10.3],
        "rotation": [90, 0, 90],
        "cubes": []
    })

    # 9. LEFT ARM (Pivot [24.4, 94.8, 10.7], REST rot [0, 180, -30])
    l_arm1_cubes = [
        C([21.5, 91.0, 7.5], [5.5, 7.0, 6.5], [30, 215]),
        C([22.0, 88.0, 4.0], [11.0, 12.0, 13.0], [56, 215]),
        C([32.0, 93.0, 5.5], [2.0, 6.5, 10.0], [0, 242]),
        C([21.0, 74.0, 7.5], [6.0, 15.0, 6.5], [26, 242]),
    ]
    bones.append({
        "name": "leftArm1",
        "parent": "body3",
        "pivot": [24.4, 94.8, 10.7],
        "rotation": [0, 180, -30],
        "cubes": l_arm1_cubes
    })

    l_arm2_cubes = [
        C([21.5, 68.0, 8.0], [5.0, 7.0, 5.5], [54, 242]),
        C([20.5, 48.0, 6.5], [7.0, 20.0, 8.5], [76, 242]),
        C([27.0, 52.0, 7.5], [2.0, 14.0, 6.5], [0, 273]),
    ]
    bones.append({
        "name": "leftArm2",
        "parent": "leftArm1",
        "pivot": [23.4, 72.5, 10.7],
        "cubes": l_arm2_cubes
    })

    l_hand_cubes = [
        C([20.5, 40.0, 7.5], [5.5, 8.0, 7.0], [19, 273]),
        C([21.0, 36.5, 8.5], [4.5, 4.0, 5.0], [46, 273]),
    ]
    bones.append({
        "name": "leftHand",
        "parent": "leftArm2",
        "pivot": [23.3, 46.8, 11.5],
        "rotation": [0, 180, 0],
        "cubes": l_hand_cubes
    })

    # 10. RIGHT LEG (Aligned to Animation Rig: Pivots [-14.5, 61.1, 7.1], etc.)
    r_leg3_cubes = [
        # Thigh armor core (centered through X = -14.5, Z = 7.1)
        C([-18.5, 44.0, 2.5], [8.0, 18.0, 9.0], [68, 273]),
        # Frontal knee deflection plate
        C([-17.5, 42.0, 0.5], [6.0, 6.0, 3.0], [0, 305]),
    ]
    bones.append({
        "name": "rightLeg3",
        "parent": "titan",
        "pivot": [-14.5, 61.1, 7.1],
        "rotation": [-15, 0, 0],
        "cubes": r_leg3_cubes
    })

    r_leg2_cubes = [
        # Knee hinge joint
        C([-17.5, 38.0, 0.5], [6.0, 6.0, 5.0], [20, 305]),
        # Athletic shin armor plate
        C([-18.5, 18.0, -1.0], [8.0, 23.0, 8.5], [45, 305]),
        # Rear calf thruster housing
        C([-17.5, 22.0, 7.0], [6.0, 16.0, 4.5], [80, 305]),

        # --- RIGHT ANKLE LANDSPINNER UNIT (Folding Roller Wheel)
        # Swing-arm suspension strut mounting to outer ankle (X = -23)
        C([-23.5, 12.0, 1.0], [5.0, 11.0, 4.0], [0, 340]),
        # Hydraulic deploy cylinder with chrome piston
        C([-23.0, 17.0, 3.0], [3.0, 8.0, 3.0], [20, 340]),
        # Landspinner roller tire (octagonal profile, diameter 9, width 4.5)
        C([-24.5, 7.0, -2.0], [4.5, 9.5, 9.5], [34, 340]),
        # Central Landspinner gold rim hub
        C([-25.2, 9.5, 0.5], [1.2, 4.5, 4.5], [64, 340]),
        # Top aerodynamic mudguard fender
        C([-25.0, 16.0, -2.5], [5.0, 2.5, 10.5], [78, 340]),
    ]
    bones.append({
        "name": "rightLeg2",
        "parent": "rightLeg3",
        "pivot": [-14.5, 43.5, 2.7],
        "rotation": [37.5, 0, 0],
        "cubes": r_leg2_cubes
    })

    r_leg1_cubes = [
        # Ankle ball joint
        C([-17.5, 12.0, -1.5], [6.0, 8.0, 5.5], [0, 365]),
    ]
    bones.append({
        "name": "rightLeg1",
        "parent": "rightLeg2",
        "pivot": [-14.5, 22.8, 3.4],
        "rotation": [-15, 0, 0],
        "cubes": r_leg1_cubes
    })

    r_foot_cubes = [
        # Main foot sole
        C([-18.5, 0.0, -6.0], [8.0, 6.0, 12.0], [25, 365]),
        # Split articulated front toe claws (Dual split-toes)
        C([-18.5, 0.0, -11.0], [3.6, 4.0, 5.5], [67, 365]),
        C([-14.1, 0.0, -11.0], [3.6, 4.0, 5.5], [67, 365]),
        # Rear heel spur
        C([-17.5, 0.0, 5.5], [6.0, 4.5, 4.0], [87, 365]),
    ]
    bones.append({
        "name": "rightFoot",
        "parent": "rightLeg1",
        "pivot": [-14.8, 8.1, -3.4],
        "rotation": [-7.5, 0, 0],
        "cubes": r_foot_cubes
    })

    # 11. LEFT LEG (Mirrored counterpart)
    l_leg3_cubes = [
        C([10.5, 44.0, 2.5], [8.0, 18.0, 9.0], [68, 273]),
        C([11.5, 42.0, 0.5], [6.0, 6.0, 3.0], [0, 305]),
    ]
    bones.append({
        "name": "leftLeg3",
        "parent": "titan",
        "pivot": [14.5, 61.1, 7.1],
        "rotation": [-15, 0, 0],
        "cubes": l_leg3_cubes
    })

    l_leg2_cubes = [
        C([11.5, 38.0, 0.5], [6.0, 6.0, 5.0], [20, 305]),
        C([10.5, 18.0, -1.0], [8.0, 23.0, 8.5], [45, 305]),
        C([11.5, 22.0, 7.0], [6.0, 16.0, 4.5], [80, 305]),

        # --- LEFT ANKLE LANDSPINNER UNIT
        C([18.5, 12.0, 1.0], [5.0, 11.0, 4.0], [0, 340]),
        C([20.0, 17.0, 3.0], [3.0, 8.0, 3.0], [20, 340]),
        C([20.0, 7.0, -2.0], [4.5, 9.5, 9.5], [34, 340]),
        C([24.0, 9.5, 0.5], [1.2, 4.5, 4.5], [64, 340]),
        C([20.0, 16.0, -2.5], [5.0, 2.5, 10.5], [78, 340]),
    ]
    bones.append({
        "name": "leftLeg2",
        "parent": "leftLeg3",
        "pivot": [14.5, 43.5, 2.7],
        "rotation": [37.5, 0, 0],
        "cubes": l_leg2_cubes
    })

    l_leg1_cubes = [
        C([11.5, 12.0, -1.5], [6.0, 8.0, 5.5], [0, 365]),
    ]
    bones.append({
        "name": "leftLeg1",
        "parent": "leftLeg2",
        "pivot": [14.5, 22.8, 3.4],
        "rotation": [-15, 0, 0],
        "cubes": l_leg1_cubes
    })

    l_foot_cubes = [
        C([10.5, 0.0, -6.0], [8.0, 6.0, 12.0], [25, 365]),
        C([10.5, 0.0, -11.0], [3.6, 4.0, 5.5], [67, 365]),
        C([14.9, 0.0, -11.0], [3.6, 4.0, 5.5], [67, 365]),
        C([11.5, 0.0, 5.5], [6.0, 4.5, 4.0], [87, 365]),
    ]
    bones.append({
        "name": "leftFoot",
        "parent": "leftLeg1",
        "pivot": [14.8, 8.1, -3.4],
        "rotation": [-7.5, 0, 0],
        "cubes": l_foot_cubes
    })

    return bones

def add_tailored_modular_armors(bones):
    """Adds the 8 modular armor archetypes tailored tightly to the Sutherland rig."""
    archetypes = [
        ("infantry", [250, 0]),
        ("siege", [290, 0]),
        ("samurai", [330, 0]),
        ("aero", [370, 0]),
        ("scrap", [410, 0]),
        ("stealth", [450, 0]),
        ("sovereign", [490, 0]),
        ("expedition", [530, 0])
    ]

    for arch_name, (u, v) in archetypes:
        # 1. Head Armor (attaches to doorUp)
        bones.append({
            "name": f"armor_head_{arch_name}",
            "parent": "doorUp",
            "pivot": [0, 107.0, -8.0],
            "cubes": [
                C([-7.5, 107.0, -8.5], [15.0, 11.5, 15.5], [u, v]),
                C([-5.5, 115.0, -10.5], [11.0, 4.0, 4.0], [u + 35, v])
            ]
        })
        # 2. Chest Armor (attaches to body3)
        bones.append({
            "name": f"armor_chest_{arch_name}",
            "parent": "body3",
            "pivot": [0.5, 78.7, 17.8],
            "cubes": [
                C([-15.8, 83.5, -3.8], [31.6, 19.0, 21.0], [u, v + 25]),
                C([-9.5, 85.0, -7.5], [19.0, 15.5, 4.5], [u + 65, v + 25])
            ]
        })
        # 3. Right Arm Armor (attaches to rightArm1)
        bones.append({
            "name": f"armor_right_arm_{arch_name}",
            "parent": "rightArm1",
            "pivot": [-24.4, 94.8, 10.7],
            "cubes": [
                C([-34.0, 87.5, 3.5], [12.0, 13.0, 14.0], [u, v + 55]),
                C([-28.0, 47.5, 6.0], [8.0, 21.0, 9.5], [u + 38, v + 55])
            ]
        })
        # 4. Left Arm Armor (attaches to leftArm1)
        bones.append({
            "name": f"armor_left_arm_{arch_name}",
            "parent": "leftArm1",
            "pivot": [24.4, 94.8, 10.7],
            "cubes": [
                C([22.0, 87.5, 3.5], [12.0, 13.0, 14.0], [u, v + 55]),
                C([20.0, 47.5, 6.0], [8.0, 21.0, 9.5], [u + 38, v + 55])
            ]
        })
        # 5. Right Leg Armor (attaches to rightLeg3)
        bones.append({
            "name": f"armor_right_leg_{arch_name}",
            "parent": "rightLeg3",
            "pivot": [-14.5, 61.1, 7.1],
            "cubes": [
                C([-19.2, 43.5, 2.0], [9.4, 19.0, 10.0], [u, v + 85]),
                C([-19.2, 17.5, -1.5], [9.4, 24.0, 9.5], [u + 32, v + 85])
            ]
        })
        # 6. Left Leg Armor (attaches to leftLeg3)
        bones.append({
            "name": f"armor_left_leg_{arch_name}",
            "parent": "leftLeg3",
            "pivot": [14.5, 61.1, 7.1],
            "cubes": [
                C([9.8, 43.5, 2.0], [9.4, 19.0, 10.0], [u, v + 85]),
                C([9.8, 17.5, -1.5], [9.4, 24.0, 9.5], [u + 32, v + 85])
            ]
        })

def export_geometry():
    bones = build_sutherland_geo()
    add_tailored_modular_armors(bones)

    geo_data = {
        "format_version": "1.12.0",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": "geometry.exo_frame_titan",
                    "texture_width": TEX_SIZE,
                    "texture_height": TEX_SIZE,
                    "visible_bounds_width": 5.0,
                    "visible_bounds_height": 6.5,
                    "visible_bounds_offset": [0, 3.0, 0]
                },
                "bones": bones
            }
        ]
    }

    with open(GEO_PATH, "w", encoding="utf-8") as f:
        json.dump(geo_data, f, indent=2)
    print(f"[OK] Wrote fully overhauled Sutherland geometry to {GEO_PATH} ({len(bones)} bones)")

# ------------------------------------------------ SHADED TEXTURE ENGINE
def write_png(path, w, h, rgba):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    raw = bytearray()
    row_bytes = w * 4
    for y in range(h):
        raw.append(0)
        start = y * row_bytes
        raw.extend(rgba[start:start + row_bytes])

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")

    with open(path, "wb") as f:
        f.write(png)

# 9 Authentic Sutherland Schemes
SCHEMES = [
    # 0: Standard Britannian Army (Purplish Slate / Gold / Steel)
    {"name": "Britannia Standard", "base": (94, 90, 112), "trim": (214, 162, 58), "steel": (46, 45, 54), "eye": (255, 32, 56)},
    # 1: Glinda Knights (Pure White / Royal Gold)
    {"name": "Glinda Knights", "base": (232, 232, 240), "trim": (222, 178, 48), "steel": (62, 62, 74), "eye": (40, 185, 255)},
    # 2: Purist Faction (Blood Red / Pitch Black)
    {"name": "Purist Faction", "base": (42, 38, 46), "trim": (198, 36, 42), "steel": (30, 30, 36), "eye": (255, 205, 32)},
    # 3: Special Ops Infiltrator (Matte Stealth Black / Emerald)
    {"name": "Special Ops", "base": (28, 28, 34), "trim": (48, 54, 62), "steel": (20, 20, 24), "eye": (30, 235, 112)},
    # 4: Desert Recon (Area 11 Sand Camo)
    {"name": "Desert Recon", "base": (178, 158, 128), "trim": (132, 112, 88), "steel": (52, 48, 46), "eye": (255, 125, 32)},
    # 5: Arctic Frontier (Glacier White / Navy Blue)
    {"name": "Arctic Frontier", "base": (218, 228, 238), "trim": (46, 82, 144), "steel": (56, 66, 76), "eye": (0, 215, 255)},
    # 6: Urban Suppression (Cobalt Blue / Steel Grey)
    {"name": "Urban Suppression", "base": (56, 76, 118), "trim": (182, 188, 198), "steel": (36, 42, 52), "eye": (255, 42, 42)},
    # 7: Imperial Royal Guard (Crimson / Polished Gold)
    {"name": "Royal Guard", "base": (148, 26, 36), "trim": (232, 188, 58), "steel": (46, 36, 42), "eye": (255, 225, 42)},
    # 8: Guren Vermilion (Scarlet Vermilion / Charcoal)
    {"name": "Guren Vermilion", "base": (178, 32, 32), "trim": (224, 142, 36), "steel": (36, 32, 36), "eye": (82, 255, 124)},
]

def generate_textures():
    os.makedirs(TEX_DIR, exist_ok=True)

    for idx, s in enumerate(SCHEMES):
        buf = bytearray(TEX_SIZE * TEX_SIZE * 4)
        base = s["base"]
        trim = s["trim"]
        steel = s["steel"]
        eye = s["eye"]

        def paint_rect(u, v, w, h, color, ao=True, panel_border=True):
            for y in range(v, min(v + h, TEX_SIZE)):
                dy = y - v
                for x in range(u, min(u + w, TEX_SIZE)):
                    dx = x - u
                    r, g, b = color

                    # Ambient Occlusion gradient along edges
                    factor = 1.0
                    if ao:
                        dist_edge = min(dx, dy, (w - 1) - dx, (h - 1) - dy)
                        if dist_edge == 0:
                            factor = 0.65  # Dark recessed seam
                        elif dist_edge == 1:
                            factor = 0.85
                        elif dist_edge == 2:
                            factor = 0.95

                    # Panel seam engraved line
                    if panel_border and (dx == 0 or dy == 0):
                        factor = 0.60
                    elif panel_border and (dx == 1 or dy == 1):
                        factor = 1.15  # Specular chamfer highlight

                    # Micro metallic grain
                    noise = ((x * 19 + y * 41) % 9) - 4
                    fr = max(0, min(255, int(r * factor) + noise))
                    fg = max(0, min(255, int(g * factor) + noise))
                    fb = max(0, min(255, int(b * factor) + noise))

                    px = (y * TEX_SIZE + x) * 4
                    buf[px] = fr
                    buf[px + 1] = fg
                    buf[px + 2] = fb
                    buf[px + 3] = 255

        # 1. Base Sutherland Armor Regions
        paint_rect(0, 0, 150, 420, base, ao=True)

        # 2. Mechanical Joints & Hydraulics (Spine, Bearing, Axles, Hands)
        paint_rect(54, 24, 50, 40, steel)
        paint_rect(48, 48, 20, 20, (190, 195, 205)) # Chrome piston
        paint_rect(19, 273, 35, 30, steel) # Hands
        paint_rect(0, 365, 25, 25, steel) # Ankle joint

        # 3. Imperial Gold / Accent Trim (Slash Harkens, Pauldron Trim, Antennae)
        paint_rect(50, 135, 25, 18, trim)
        paint_rect(0, 242, 10, 30, trim)
        paint_rect(46, 195, 12, 20, trim) # Antennae
        paint_rect(64, 340, 14, 14, trim) # Landspinner rim hub

        # 4. Landspinner High-Grip Rubber Tires
        paint_rect(34, 340, 28, 24, (28, 28, 32))

        # 5. Dorsal Cockpit Pod Thruster Nozzles & Heat Tinting
        paint_rect(46, 155, 18, 18, steel)
        paint_rect(66, 155, 20, 18, (185, 85, 45)) # Heat-tinted bronze/copper nozzle

        # 6. Factsphere Ruby Red Sensor Lens with radial glow
        cx, cy = 63, 197
        for y in range(193, 203):
            for x in range(58, 68):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                if dist <= 4.5:
                    t = dist / 4.5
                    r = int(eye[0] * (1 - t * 0.4))
                    g = int(eye[1] * (1 - t * 0.6))
                    b = int(eye[2] * (1 - t * 0.6))
                    px = (y * TEX_SIZE + x) * 4
                    buf[px] = min(255, r + 40)
                    buf[px + 1] = max(0, g)
                    buf[px + 2] = max(0, b)
                    buf[px + 3] = 255

        # 7. Tailored Modular Armor Archetypes
        arch_palettes = [
            ((45, 115, 185), trim),   # Vanguard (Infantry - Apex Blue)
            ((105, 108, 118), steel), # Juggernaut (Siege - Reinforced Steel)
            ((175, 40, 42), trim),    # Ronin (Samurai - Crimson Lacquer)
            ((215, 218, 225), (45, 85, 155)), # Valkyrie (Aero - High-G White)
            ((135, 90, 55), steel),   # Raider (Scrap - Rusted Iron)
            ((32, 32, 38), (50, 55, 65)),     # Phantom (Stealth - Carbon Black)
            ((218, 178, 45), (145, 25, 35)),  # Paladin (Sovereign - Royal Gold)
            ((70, 120, 72), steel),   # Ranger (Expedition - Forest Camo)
        ]

        for a_idx, (p_main, p_accent) in enumerate(arch_palettes):
            u_arch = 250 + a_idx * 40
            paint_rect(u_arch, 0, 38, 130, p_main, ao=True, panel_border=True)
            paint_rect(u_arch + 12, 0, 8, 130, p_accent, ao=True, panel_border=False)

        out_name = "exo_frame_titan.png" if idx == 0 else f"exo_frame_titan_{idx}.png"
        out_path = os.path.join(TEX_DIR, out_name)
        write_png(out_path, TEX_SIZE, TEX_SIZE, buf)
        print(f"[OK] Rendered shaded texture [{idx}]: {s['name']} -> {out_name}")

if __name__ == "__main__":
    export_geometry()
    generate_textures()
