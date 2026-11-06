"""Procedural builder for the 8 3D Modular Armor Archetypes.
Expands the 6 Titan Frame models with distinct, massive, custom-crafted 3D geometry for:
1. infantry
2. siege
3. samurai
4. aero
5. scrap
6. stealth
7. sovereign
8. expedition
"""
import json, os, copy

ROOT = "Titan Combat/src/main/resources/assets/titancombat/geo"

def make_biped_armor_bones(scale=1.0):
    s = scale
    bones = []
    
    # ---------------- 1. INFANTRY ARCHETYPE ----------------
    bones.append({
        "name": "armor_head_infantry",
        "parent": "doorUp",
        "pivot": [0.0, 107.0, -10.0],
        "cubes": [
            {"origin": [-8.0 * s, 100.0, -18.0], "size": [16.0 * s, 12.0, 6.0], "uv": [120, 40]},
            {"origin": [-9.0 * s, 109.0, -19.0], "size": [18.0 * s, 3.0, 8.0], "uv": [160, 40]}, # Visor brow
            {"origin": [7.0 * s, 112.0, -15.0], "size": [1.5, 9.0, 1.5], "uv": [140, 50]} # Tactical antenna
        ]
    })
    bones.append({
        "name": "armor_chest_infantry",
        "parent": "body3",
        "pivot": [0.0, 85.0, 0.0],
        "cubes": [
            {"origin": [-15.0 * s, 74.0, -16.0], "size": [30.0 * s, 20.0, 8.0], "uv": [120, 64]},
            {"origin": [-12.0 * s, 68.0, -14.0], "size": [24.0 * s, 8.0, 5.0], "uv": [120, 94]}
        ]
    })
    for side, sgn in [("left", 1), ("right", -1)]:
        x_base = 24.0 * sgn
        bones.append({
            "name": f"armor_{side}_arm_infantry",
            "parent": f"{side}Arm1",
            "pivot": [x_base, 94.8, 10.7],
            "cubes": [
                {"origin": [x_base - (6.0 * sgn if sgn < 0 else 0.0), 84.0, 3.0], "size": [12.0 * s, 15.0, 14.0], "uv": [200, 64]}
            ]
        })
        bones.append({
            "name": f"armor_{side}_leg_infantry",
            "parent": f"{side}Leg2",
            "pivot": [14.8 * sgn, 43.5, 2.7],
            "cubes": [
                {"origin": [14.8 * sgn - (5.0 if sgn > 0 else 7.0), 22.0, -6.0], "size": [11.0 * s, 21.0, 13.0], "uv": [200, 90]}
            ]
        })

    # ---------------- 2. SIEGE ARCHETYPE (Massive Bunker Blast Shields & Hazard Stripes) ----------------
    bones.append({
        "name": "armor_head_siege",
        "parent": "doorUp",
        "pivot": [0.0, 107.0, -10.0],
        "cubes": [
            # Bunker blast face cage
            {"origin": [-9.5 * s, 98.0, -20.0], "size": [19.0 * s, 16.0, 8.0], "uv": [120, 40]},
            {"origin": [-8.0 * s, 104.0, -21.5], "size": [16.0 * s, 4.0, 2.0], "uv": [160, 40]}, # Slit cage
            {"origin": [-10.5 * s, 96.0, -17.0], "size": [21.0 * s, 4.0, 10.0], "uv": [130, 50]} # Chin blast collar
        ]
    })
    bones.append({
        "name": "armor_chest_siege",
        "parent": "body3",
        "pivot": [0.0, 85.0, 0.0],
        "cubes": [
            # Massive reactive armor slabs (ERA)
            {"origin": [-18.0 * s, 70.0, -19.0], "size": [36.0 * s, 26.0, 10.0], "uv": [120, 64]},
            {"origin": [-15.0 * s, 72.0, -21.0], "size": [30.0 * s, 14.0, 3.0], "uv": [140, 70]}, # Front ERA block
            {"origin": [-16.0 * s, 66.0, -17.0], "size": [32.0 * s, 6.0, 6.0], "uv": [120, 94]}  # Groin blast plate
        ]
    })
    for side, sgn in [("left", 1), ("right", -1)]:
        x_base = 24.0 * sgn
        bones.append({
            "name": f"armor_{side}_arm_siege",
            "parent": f"{side}Arm1",
            "pivot": [x_base, 94.8, 10.7],
            "cubes": [
                # Giant fortress shoulder mantlet flared outward
                {"origin": [x_base - (8.0 * sgn if sgn < 0 else -1.0), 80.0, 0.0], "size": [16.0 * s, 20.0, 18.0], "uv": [200, 64]},
                {"origin": [x_base - (9.5 * sgn if sgn < 0 else -2.5), 84.0, -2.0], "size": [18.0 * s, 12.0, 4.0], "uv": [220, 70]} # Shield lip
            ]
        })
        bones.append({
            "name": f"armor_{side}_leg_siege",
            "parent": f"{side}Leg2",
            "pivot": [14.8 * sgn, 43.5, 2.7],
            "cubes": [
                # Bulldozer-style wide shin bunker plate
                {"origin": [14.8 * sgn - (7.0 if sgn > 0 else 9.0), 18.0, -8.0], "size": [15.0 * s, 26.0, 15.0], "uv": [200, 90]}
            ]
        })

    # ---------------- 3. SAMURAI ARCHETYPE (Kabuto Horns & Layered O-Sode Wings) ----------------
    bones.append({
        "name": "armor_head_samurai",
        "parent": "doorUp",
        "pivot": [0.0, 107.0, -10.0],
        "cubes": [
            {"origin": [-8.0 * s, 100.0, -17.0], "size": [16.0 * s, 12.0, 6.0], "uv": [120, 40]},
            # Crescent moon horned crest (maedate)
            {"origin": [-1.5, 111.0, -20.0], "size": [3.0, 5.0, 2.0], "uv": [160, 40]},
            {"origin": [-9.0, 114.0, -20.5], "size": [18.0, 2.5, 1.5], "uv": [160, 45]},
            {"origin": [-12.0, 116.0, -20.5], "size": [4.0, 5.0, 1.5], "uv": [170, 45]},
            {"origin": [8.0, 116.0, -20.5], "size": [4.0, 5.0, 1.5], "uv": [170, 45]}
        ]
    })
    bones.append({
        "name": "armor_chest_samurai",
        "parent": "body3",
        "pivot": [0.0, 85.0, 0.0],
        "cubes": [
            # Tiered lamellar cuirass (do)
            {"origin": [-15.0 * s, 74.0, -16.0], "size": [30.0 * s, 20.0, 8.0], "uv": [120, 64]},
            {"origin": [-13.0 * s, 68.0, -15.0], "size": [26.0 * s, 7.0, 6.0], "uv": [120, 94]}, # Kusazuri hip tasset
            {"origin": [-4.0, 84.0, -17.0], "size": [8.0, 8.0, 2.0], "uv": [140, 75]} # Clan crest
        ]
    })
    for side, sgn in [("left", 1), ("right", -1)]:
        x_base = 24.0 * sgn
        bones.append({
            "name": f"armor_{side}_arm_samurai",
            "parent": f"{side}Arm1",
            "pivot": [x_base, 94.8, 10.7],
            "cubes": [
                # Tiered samurai o-sode shoulder armor wings
                {"origin": [x_base - (7.0 * sgn if sgn < 0 else -1.0), 88.0, 1.0], "size": [14.0 * s, 6.0, 16.0], "uv": [200, 64]},
                {"origin": [x_base - (8.0 * sgn if sgn < 0 else -2.0), 82.0, 2.0], "size": [15.0 * s, 6.0, 15.0], "uv": [200, 72]},
                {"origin": [x_base - (9.0 * sgn if sgn < 0 else -3.0), 76.0, 3.0], "size": [16.0 * s, 6.0, 14.0], "uv": [200, 80]}
            ]
        })
        bones.append({
            "name": f"armor_{side}_leg_samurai",
            "parent": f"{side}Leg2",
            "pivot": [14.8 * sgn, 43.5, 2.7],
            "cubes": [
                # Bladed suneate shin guards & thigh tassets (haidate)
                {"origin": [14.8 * sgn - (5.0 if sgn > 0 else 7.0), 20.0, -6.0], "size": [12.0 * s, 23.0, 12.0], "uv": [200, 90]},
                {"origin": [14.8 * sgn - (6.0 if sgn > 0 else 8.0), 38.0, -7.0], "size": [13.0 * s, 6.0, 13.0], "uv": [220, 90]} # Knee blade
            ]
        })

    # ---------------- 4. AERO ARCHETYPE (Swept Delta Winglets & Thruster Cowls) ----------------
    bones.append({
        "name": "armor_head_aero",
        "parent": "doorUp",
        "pivot": [0.0, 107.0, -10.0],
        "cubes": [
            {"origin": [-7.5 * s, 100.0, -18.0], "size": [15.0 * s, 12.0, 6.0], "uv": [120, 40]},
            {"origin": [-6.0 * s, 110.0, -19.5], "size": [12.0 * s, 3.0, 7.0], "uv": [160, 40]}, # Slanted aero brow
            {"origin": [-2.0, 112.5, -16.0], "size": [4.0, 2.5, 6.0], "uv": [140, 50]} # Top ram scoop
        ]
    })
    bones.append({
        "name": "armor_chest_aero",
        "parent": "body3",
        "pivot": [0.0, 85.0, 0.0],
        "cubes": [
            {"origin": [-14.0 * s, 74.0, -16.0], "size": [28.0 * s, 20.0, 7.0], "uv": [120, 64]},
            {"origin": [-11.0 * s, 78.0, -17.5], "size": [22.0 * s, 12.0, 2.5], "uv": [140, 64]} # Chiseled chevron cowl
        ]
    })
    for side, sgn in [("left", 1), ("right", -1)]:
        x_base = 24.0 * sgn
        bones.append({
            "name": f"armor_{side}_arm_aero",
            "parent": f"{side}Arm1",
            "pivot": [x_base, 94.8, 10.7],
            "cubes": [
                # Swept delta winglet on shoulder
                {"origin": [x_base - (5.0 * sgn if sgn < 0 else 0.0), 85.0, 2.0], "size": [11.0 * s, 14.0, 12.0], "uv": [200, 64]},
                {"origin": [x_base + (6.0 * sgn if sgn > 0 else -16.0), 90.0, 0.0], "size": [10.0, 3.0, 16.0], "uv": [210, 64]} # Outrigger winglet
            ]
        })
        bones.append({
            "name": f"armor_{side}_leg_aero",
            "parent": f"{side}Leg2",
            "pivot": [14.8 * sgn, 43.5, 2.7],
            "cubes": [
                {"origin": [14.8 * sgn - (5.0 if sgn > 0 else 7.0), 22.0, -5.0], "size": [10.0 * s, 21.0, 12.0], "uv": [200, 90]},
                {"origin": [14.8 * sgn + (4.5 * sgn if sgn > 0 else -7.5), 24.0, 4.0], "size": [3.0, 16.0, 6.0], "uv": [220, 90]} # Calf stabilizer fin
            ]
        })

    # ---------------- 5. SCRAP ARCHETYPE (Welded Rebar Cage & Post-Apocalyptic Iron Sheets) ----------------
    bones.append({
        "name": "armor_head_scrap",
        "parent": "doorUp",
        "pivot": [0.0, 107.0, -10.0],
        "cubes": [
            {"origin": [-8.0 * s, 99.0, -18.0], "size": [16.0 * s, 13.0, 6.0], "uv": [120, 40]},
            {"origin": [-8.5 * s, 103.0, -19.5], "size": [17.0 * s, 6.0, 2.0], "uv": [160, 40]}, # Welded rebar cage bars
            {"origin": [-4.0, 111.0, -19.0], "size": [8.0, 4.0, 1.5], "uv": [140, 50]}  # Bolted metal patch
        ]
    })
    bones.append({
        "name": "armor_chest_scrap",
        "parent": "body3",
        "pivot": [0.0, 85.0, 0.0],
        "cubes": [
            {"origin": [-16.0 * s, 73.0, -17.0], "size": [32.0 * s, 22.0, 8.0], "uv": [120, 64]},
            {"origin": [-12.0 * s, 70.0, -18.5], "size": [14.0 * s, 16.0, 2.0], "uv": [130, 64]}, # Asymmetrical scrap plate
            {"origin": [3.0 * s, 76.0, -18.5], "size": [10.0 * s, 10.0, 2.0], "uv": [145, 64]}
        ]
    })
    for side, sgn in [("left", 1), ("right", -1)]:
        x_base = 24.0 * sgn
        bones.append({
            "name": f"armor_{side}_arm_scrap",
            "parent": f"{side}Arm1",
            "pivot": [x_base, 94.8, 10.7],
            "cubes": [
                {"origin": [x_base - (6.0 * sgn if sgn < 0 else 0.0), 83.0, 2.0], "size": [13.0 * s, 16.0, 14.0], "uv": [200, 64]},
                {"origin": [x_base + (6.0 * sgn if sgn > 0 else -8.0), 96.0, 4.0], "size": [2.5, 7.0, 2.5], "uv": [215, 64]} # Welded rebar spike
            ]
        })
        bones.append({
            "name": f"armor_{side}_leg_scrap",
            "parent": f"{side}Leg2",
            "pivot": [14.8 * sgn, 43.5, 2.7],
            "cubes": [
                {"origin": [14.8 * sgn - (6.0 if sgn > 0 else 8.0), 20.0, -7.0], "size": [13.0 * s, 22.0, 13.0], "uv": [200, 90]}
            ]
        })

    # ---------------- 6. STEALTH ARCHETYPE (Faceted Radar-Absorbent Carbon Cowls) ----------------
    bones.append({
        "name": "armor_head_stealth",
        "parent": "doorUp",
        "pivot": [0.0, 107.0, -10.0],
        "cubes": [
            {"origin": [-7.5 * s, 101.0, -17.5], "size": [15.0 * s, 11.0, 5.5], "uv": [120, 40]},
            {"origin": [-6.0 * s, 104.0, -18.8], "size": [12.0 * s, 5.0, 2.0], "uv": [160, 40]} # Stealth optic shroud
        ]
    })
    bones.append({
        "name": "armor_chest_stealth",
        "parent": "body3",
        "pivot": [0.0, 85.0, 0.0],
        "cubes": [
            {"origin": [-14.0 * s, 74.0, -15.5], "size": [28.0 * s, 20.0, 6.5], "uv": [120, 64]},
            {"origin": [-11.0 * s, 70.0, -14.5], "size": [22.0 * s, 6.0, 4.5], "uv": [120, 94]}
        ]
    })
    for side, sgn in [("left", 1), ("right", -1)]:
        x_base = 24.0 * sgn
        bones.append({
            "name": f"armor_{side}_arm_stealth",
            "parent": f"{side}Arm1",
            "pivot": [x_base, 94.8, 10.7],
            "cubes": [
                {"origin": [x_base - (5.0 * sgn if sgn < 0 else 0.0), 85.0, 2.0], "size": [11.0 * s, 14.0, 12.0], "uv": [200, 64]}
            ]
        })
        bones.append({
            "name": f"armor_{side}_leg_stealth",
            "parent": f"{side}Leg2",
            "pivot": [14.8 * sgn, 43.5, 2.7],
            "cubes": [
                {"origin": [14.8 * sgn - (4.5 if sgn > 0 else 6.5), 22.0, -5.0], "size": [10.0 * s, 21.0, 11.0], "uv": [200, 90]}
            ]
        })

    # ---------------- 7. SOVEREIGN ARCHETYPE (Regal Gilded Imperial Commander Plate) ----------------
    bones.append({
        "name": "armor_head_sovereign",
        "parent": "doorUp",
        "pivot": [0.0, 107.0, -10.0],
        "cubes": [
            {"origin": [-8.0 * s, 100.0, -17.0], "size": [16.0 * s, 12.0, 6.0], "uv": [120, 40]},
            # Sovereign golden crown crest
            {"origin": [-5.0, 111.0, -18.0], "size": [10.0, 4.0, 3.0], "uv": [160, 40]},
            {"origin": [-7.0, 113.0, -18.5], "size": [3.0, 6.0, 2.0], "uv": [170, 40]},
            {"origin": [4.0, 113.0, -18.5], "size": [3.0, 6.0, 2.0], "uv": [170, 40]},
            {"origin": [-1.5, 114.0, -18.8], "size": [3.0, 8.0, 2.2], "uv": [180, 40]} # Center finial
        ]
    })
    bones.append({
        "name": "armor_chest_sovereign",
        "parent": "body3",
        "pivot": [0.0, 85.0, 0.0],
        "cubes": [
            # Imperial breastplate
            {"origin": [-15.0 * s, 74.0, -16.0], "size": [30.0 * s, 20.0, 7.5], "uv": [120, 64]},
            {"origin": [-8.0 * s, 77.0, -17.5], "size": [16.0 * s, 14.0, 2.5], "uv": [140, 64]}, # Golden eagle crest
            {"origin": [-12.0 * s, 68.0, -14.0], "size": [24.0 * s, 7.0, 5.0], "uv": [120, 94]}
        ]
    })
    for side, sgn in [("left", 1), ("right", -1)]:
        x_base = 24.0 * sgn
        bones.append({
            "name": f"armor_{side}_arm_sovereign",
            "parent": f"{side}Arm1",
            "pivot": [x_base, 94.8, 10.7],
            "cubes": [
                # Winged royal commander pauldrons
                {"origin": [x_base - (6.0 * sgn if sgn < 0 else -1.0), 86.0, 1.0], "size": [13.0 * s, 15.0, 14.0], "uv": [200, 64]},
                {"origin": [x_base + (6.0 * sgn if sgn > 0 else -12.0), 91.0, 0.0], "size": [6.0, 9.0, 16.0], "uv": [215, 64]} # Gilded wing crest
            ]
        })
        bones.append({
            "name": f"armor_{side}_leg_sovereign",
            "parent": f"{side}Leg2",
            "pivot": [14.8 * sgn, 43.5, 2.7],
            "cubes": [
                # Fluted knightly greaves
                {"origin": [14.8 * sgn - (5.0 if sgn > 0 else 7.0), 21.0, -6.0], "size": [11.0 * s, 22.0, 12.0], "uv": [200, 90]},
                {"origin": [14.8 * sgn - (4.0 if sgn > 0 else 6.0), 38.0, -7.5], "size": [8.0 * s, 6.0, 3.0], "uv": [220, 90]} # Golden knee boss
            ]
        })

    # ---------------- 8. EXPEDITION ARCHETYPE (Cyclone Dust Filters & Storage Packs) ----------------
    bones.append({
        "name": "armor_head_expedition",
        "parent": "doorUp",
        "pivot": [0.0, 107.0, -10.0],
        "cubes": [
            {"origin": [-8.0 * s, 100.0, -17.0], "size": [16.0 * s, 12.0, 6.0], "uv": [120, 40]},
            # Twin cyclone dust cleaner canisters flanking the head
            {"origin": [8.0 * s, 102.0, -16.0], "size": [4.0, 9.0, 4.0], "uv": [160, 40]},
            {"origin": [-12.0 * s, 102.0, -16.0], "size": [4.0, 9.0, 4.0], "uv": [160, 40]}
        ]
    })
    bones.append({
        "name": "armor_chest_expedition",
        "parent": "body3",
        "pivot": [0.0, 85.0, 0.0],
        "cubes": [
            {"origin": [-15.0 * s, 74.0, -16.0], "size": [30.0 * s, 20.0, 8.0], "uv": [120, 64]},
            {"origin": [-11.0 * s, 72.0, -18.0], "size": [10.0 * s, 8.0, 3.0], "uv": [140, 70]}, # Left cargo pouch
            {"origin": [1.0 * s, 72.0, -18.0], "size": [10.0 * s, 8.0, 3.0], "uv": [140, 70]}   # Right cargo pouch
        ]
    })
    for side, sgn in [("left", 1), ("right", -1)]:
        x_base = 24.0 * sgn
        bones.append({
            "name": f"armor_{side}_arm_expedition",
            "parent": f"{side}Arm1",
            "pivot": [x_base, 94.8, 10.7],
            "cubes": [
                {"origin": [x_base - (6.0 * sgn if sgn < 0 else 0.0), 84.0, 2.0], "size": [12.0 * s, 15.0, 14.0], "uv": [200, 64]}
            ]
        })
        bones.append({
            "name": f"armor_{side}_leg_expedition",
            "parent": f"{side}Leg2",
            "pivot": [14.8 * sgn, 43.5, 2.7],
            "cubes": [
                {"origin": [14.8 * sgn - (5.5 if sgn > 0 else 7.5), 20.0, -6.5], "size": [12.0 * s, 22.0, 13.0], "uv": [200, 90]}
            ]
        })

    return bones

def make_spider_armor_bones(scale=1.35):
    s = scale
    bones = []
    def sc_cubes(cubes):
        out = []
        for c in cubes:
            entry = dict(c)
            entry["origin"] = [round(float(v) * s, 3) for v in c["origin"]]
            entry["size"] = [round(float(v) * s, 3) for v in c["size"]]
            out.append(entry)
        return out

    def add_bone(name, parent, pivot, cubes):
        bones.append({
            "name": name,
            "parent": parent,
            "pivot": [round(float(v) * s, 3) for v in pivot],
            "cubes": sc_cubes(cubes)
        })

    # 1. INFANTRY
    add_bone("armor_head_infantry", "doorUp", [0.0, 36.0, -12.0],
             [{"origin": [-8.5, 35.0, -24.5], "size": [17.0, 6.0, 12.0], "uv": [120, 40]}])
    add_bone("armor_chest_infantry", "body3", [0.0, 34.0, 0.0],
             [{"origin": [-13.0, 35.0, -14.0], "size": [26.0, 6.0, 14.0], "uv": [120, 64]}])
    
    # 2. SIEGE (Huge Reactive ERA Armor Bricks & Blast Plates)
    add_bone("armor_head_siege", "doorUp", [0.0, 36.0, -12.0], [
        {"origin": [-9.5, 34.0, -26.0], "size": [19.0, 8.0, 14.0], "uv": [120, 40]},
        {"origin": [-8.0, 37.0, -27.5], "size": [16.0, 4.0, 2.0], "uv": [160, 40]}
    ])
    add_bone("armor_chest_siege", "body3", [0.0, 34.0, 0.0], [
        {"origin": [-15.0, 34.0, -15.0], "size": [30.0, 8.0, 16.0], "uv": [120, 64]},
        {"origin": [-13.0, 36.0, -16.5], "size": [26.0, 5.0, 3.0], "uv": [140, 70]}
    ])

    # 3. SAMURAI (Kabuto Horns & Bladed Sponsons)
    add_bone("armor_head_samurai", "doorUp", [0.0, 36.0, -12.0], [
        {"origin": [-8.5, 35.0, -24.5], "size": [17.0, 6.0, 12.0], "uv": [120, 40]},
        {"origin": [-1.5, 41.0, -23.0], "size": [3.0, 5.0, 2.0], "uv": [160, 40]},
        {"origin": [-9.0, 44.0, -23.5], "size": [18.0, 2.5, 1.5], "uv": [160, 45]},
        {"origin": [-12.0, 46.0, -23.5], "size": [4.0, 5.0, 1.5], "uv": [170, 45]},
        {"origin": [8.0, 46.0, -23.5], "size": [4.0, 5.0, 1.5], "uv": [170, 45]}
    ])
    add_bone("armor_chest_samurai", "body3", [0.0, 34.0, 0.0], [
        {"origin": [-13.0, 35.0, -14.0], "size": [26.0, 6.0, 14.0], "uv": [120, 64]},
        {"origin": [-4.0, 39.0, -15.0], "size": [8.0, 4.0, 2.0], "uv": [140, 75]}
    ])

    # 4. AERO (Swept Winglet Sponsons)
    add_bone("armor_head_aero", "doorUp", [0.0, 36.0, -12.0],
             [{"origin": [-8.0, 35.5, -25.0], "size": [16.0, 5.5, 13.0], "uv": [120, 40]}])
    add_bone("armor_chest_aero", "body3", [0.0, 34.0, 0.0], [
        {"origin": [-13.0, 35.0, -14.0], "size": [26.0, 6.0, 14.0], "uv": [120, 64]},
        {"origin": [-15.0, 37.0, -12.0], "size": [30.0, 2.0, 8.0], "uv": [140, 64]} # Side canards
    ])

    # 5. SCRAP (Welded Rebar Mesh)
    add_bone("armor_head_scrap", "doorUp", [0.0, 36.0, -12.0], [
        {"origin": [-8.5, 35.0, -24.5], "size": [17.0, 6.0, 12.0], "uv": [120, 40]},
        {"origin": [-9.0, 38.0, -25.5], "size": [18.0, 3.0, 1.5], "uv": [160, 40]}
    ])
    add_bone("armor_chest_scrap", "body3", [0.0, 34.0, 0.0], [
        {"origin": [-14.0, 35.0, -14.5], "size": [28.0, 6.5, 15.0], "uv": [120, 64]}
    ])

    # 6. STEALTH
    add_bone("armor_head_stealth", "doorUp", [0.0, 36.0, -12.0],
             [{"origin": [-8.0, 35.5, -24.5], "size": [16.0, 5.5, 12.0], "uv": [120, 40]}])
    add_bone("armor_chest_stealth", "body3", [0.0, 34.0, 0.0],
             [{"origin": [-12.5, 35.0, -13.5], "size": [25.0, 5.5, 13.5], "uv": [120, 64]}])

    # 7. SOVEREIGN (Imperial Gilded Crests)
    add_bone("armor_head_sovereign", "doorUp", [0.0, 36.0, -12.0], [
        {"origin": [-8.5, 35.0, -24.5], "size": [17.0, 6.0, 12.0], "uv": [120, 40]},
        {"origin": [-5.0, 41.0, -22.0], "size": [10.0, 4.0, 2.0], "uv": [160, 40]},
        {"origin": [-1.5, 43.0, -22.5], "size": [3.0, 5.0, 1.5], "uv": [180, 40]}
    ])
    add_bone("armor_chest_sovereign", "body3", [0.0, 34.0, 0.0], [
        {"origin": [-13.0, 35.0, -14.0], "size": [26.0, 6.0, 14.0], "uv": [120, 64]},
        {"origin": [-6.0, 38.0, -15.0], "size": [12.0, 4.0, 2.0], "uv": [140, 64]}
    ])

    # 8. EXPEDITION
    add_bone("armor_head_expedition", "doorUp", [0.0, 36.0, -12.0], [
        {"origin": [-8.5, 35.0, -24.5], "size": [17.0, 6.0, 12.0], "uv": [120, 40]},
        {"origin": [8.5, 34.0, -22.0], "size": [3.0, 6.0, 4.0], "uv": [160, 40]},
        {"origin": [-11.5, 34.0, -22.0], "size": [3.0, 6.0, 4.0], "uv": [160, 40]}
    ])
    add_bone("armor_chest_expedition", "body3", [0.0, 34.0, 0.0], [
        {"origin": [-13.0, 35.0, -14.0], "size": [26.0, 6.0, 14.0], "uv": [120, 64]},
        {"origin": [-11.0, 36.0, -16.0], "size": [8.0, 4.0, 3.0], "uv": [140, 70]},
        {"origin": [3.0, 36.0, -16.0], "size": [8.0, 4.0, 3.0], "uv": [140, 70]}
    ])

    # Arms and Legs for all 8 archetypes on Spider
    archetypes = ["infantry", "siege", "samurai", "aero", "scrap", "stealth", "sovereign", "expedition"]
    for arch in archetypes:
        for side, sgn in [("left", 1), ("right", -1)]:
            add_bone(f"armor_{side}_arm_{arch}", f"{side}Arm1", [16.0 * sgn, 33.0, -3.0],
                     [{"origin": [15.5 * sgn - (0.0 if sgn > 0 else 6.0), 28.0, -7.0], "size": [6.0, 8.0, 8.0], "uv": [200, 64]}])
            add_bone(f"armor_{side}_leg_{arch}", f"{side}Leg2", [28.0 * sgn, 34.0, -16.0],
                     [{"origin": [26.0 * sgn - (0.0 if sgn > 0 else 6.0), 28.0, -19.0], "size": [6.0, 9.0, 7.0], "uv": [200, 90]}])

    return bones

# Target geo files
target_geos = [
    ("striker_frame_titan.geo.json", 0.95),
    ("vanguard_frame_titan.geo.json", 1.0),
    ("colossus_frame_titan.geo.json", 1.2),
    ("terrain_frame_titan.geo.json", 1.05),
    ("cyclops_frame_titan.geo.json", 1.15),
    ("spider_frame_titan.geo.json", "spider")
]

for gfile, sc in target_geos:
    fpath = os.path.join(ROOT, gfile)
    if not os.path.exists(fpath):
        print(f"Skipping {fpath} (not found)")
        continue
    with open(fpath, "r") as f:
        data = json.load(f)
    
    bones = data["minecraft:geometry"][0]["bones"]
    
    old_names = {"armor_head", "armor_chest", "armor_left_arm", "armor_right_arm", "armor_left_leg", "armor_right_leg"}
    bones = [b for b in bones if not (b["name"] in old_names or b["name"].startswith("armor_head_") or b["name"].startswith("armor_chest_") or b["name"].startswith("armor_left_arm_") or b["name"].startswith("armor_right_arm_") or b["name"].startswith("armor_left_leg_") or b["name"].startswith("armor_right_leg_"))]
    
    if sc == "spider":
        new_bones = make_spider_armor_bones()
    else:
        new_bones = make_biped_armor_bones(scale=sc)
        
    bones.extend(new_bones)
    
    data["minecraft:geometry"][0]["bones"] = bones
    with open(fpath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Updated {gfile} with 8 Epic Armor Archetypes (total bones: {len(bones)})")

print("Modular armor geometry upgrade complete!")
