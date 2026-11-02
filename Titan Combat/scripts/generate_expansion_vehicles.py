import json, os, shutil
from generate_transport_assets import (
    make_png, TextureDrawer, accent, rod, per_face_uv, write_geo, make_wheel
)

# ==============================================================================
# 1. OCEANIC SUPER-CARRIER (SUPER DRAFT RAISED FOR REALISTIC WATERLINE)
# ==============================================================================
def generate_ocean_carrier_model(path):
    bones = []
    root = {"name": "root", "pivot": [0, 0, 0], "cubes": []}
    bones.append(root)

    # Raise hull so waterline rests realistically against the lower hull without submerging deck
    hull = {
        "name": "hull",
        "parent": "root",
        "pivot": [0, 24, 0],
        "cubes": [
            # Main Keel & Lower Hull (Catamaran stealth wedge, baseline y = 12..28)
            {"origin": [-36, 12, -96], "size": [72, 16, 192], "uv": [0, 0]},
            # Bow Wave Deflectors / Wave-piercing prow
            {"origin": [-38, 24, -108], "size": [76, 14, 16], "uv": [0, 0]},
            # Port Sponson
            {"origin": [36, 16, -90], "size": [12, 16, 180], "uv": [256, 0]},
            # Starboard Sponson
            {"origin": [-48, 16, -90], "size": [12, 16, 180], "uv": [256, 0]},
            # Main Well Deck (Flush Landing Deck at y = 28)
            {"origin": [-32, 28, -88], "size": [64, 2, 172], "uv": [256, 0]},
            # Deck Side Bulwarks (Armored Coamings)
            {"origin": [30, 30, -88], "size": [4, 10, 172], "uv": [0, 0]},
            {"origin": [-34, 30, -88], "size": [4, 10, 172], "uv": [0, 0]},
            # Stern Transom & Waterjet Shrouds
            {"origin": [-34, 14, 94], "size": [68, 16, 8], "uv": [384, 128]},
        ]
    }
    bones.append(hull)

    # Elevated Command Bridge & Wheelhouse (Starboard Island, y = 30..66)
    # Seat at x = -24, y = 52, z = 44 (inside bridge behind panoramic windows)
    bridge = {
        "name": "bridge",
        "parent": "hull",
        "pivot": [-24, 40, 40],
        "cubes": [
            # Island superstructure base
            {"origin": [-34, 30, 20], "size": [16, 20, 48], "uv": [0, 0]},
            # Command Bridge Panoramic Cabin (Roof at y = 64)
            {"origin": [-35, 50, 26], "size": [18, 14, 36], "uv": [0, 0]},
            # Front & Side Bridge Observation Windows (Panoramic at y = 53..61)
            {"origin": [-36, 53, 24], "size": [19, 8, 3], "uv": [128, 0]},
            {"origin": [-36, 53, 27], "size": [2, 8, 32], "uv": [128, 0]},
            # Bridge Interior Console & Radar Displays (in front of captain seat)
            {"origin": [-32, 51, 26], "size": [12, 4, 8], "uv": [256, 128]},
            # Captain / Driver Seat (seat cushion y = 51, backrest y = 54..62, z = 44)
            {"origin": [-28, 51, 40], "size": [8, 3, 8], "uv": [128, 192]},
            {"origin": [-28, 54, 46], "size": [8, 8, 2], "uv": [128, 192]}
        ]
    }
    bones.append(bridge)

    # Rotating Radar Mast
    radar = {
        "name": "radar",
        "parent": "bridge",
        "pivot": [-25, 66, 38],
        "cubes": [
            {"origin": [-27, 64, 36], "size": [4, 6, 4], "uv": [256, 128]},
            {"origin": [-37, 70, 36], "size": [24, 4, 3], "uv": [0, 128]}
        ]
    }
    bones.append(radar)

    # Hydraulic Cargo Crane on Port Side
    crane = {
        "name": "crane_base",
        "parent": "hull",
        "pivot": [26, 30, 30],
        "cubes": [
            {"origin": [20, 30, 24], "size": [12, 10, 12], "uv": [128, 192]},
            {"origin": [22, 40, 26], "size": [8, 32, 8], "uv": [128, 192]},
            {"origin": [-10, 68, 27], "size": [36, 6, 6], "uv": [0, 128]},
            {"origin": [-6, 48, 28], "size": [4, 20, 4], "uv": [128, 128]}
        ]
    }
    bones.append(crane)

    # Separate Cargo Straps Bone (Hideable)
    cargo_straps = {
        "name": "cargo_straps",
        "parent": "hull",
        "pivot": [0, 30, 0],
        "cubes": [
            {"origin": [-22, 30, -48], "size": [44, 1, 4], "uv": [128, 128]},
            {"origin": [-22, 30, -28], "size": [44, 1, 4], "uv": [128, 128]},
            {"origin": [-22, 30, 2], "size": [44, 1, 4], "uv": [128, 128]},
            {"origin": [-22, 30, 22], "size": [44, 1, 4], "uv": [128, 128]},
            {"origin": [-35, 40, -60], "size": [2, 10, 10], "uv": [0, 192]},
            {"origin": [33, 40, -60], "size": [2, 10, 10], "uv": [0, 192]}
        ]
    }
    bones.append(cargo_straps)

    write_geo(path, "geometry.ocean_carrier", bones, bounds_w=9.0, bounds_h=5.5, bounds_y=2.5)


# ==============================================================================
# 2. TACTICAL PICKUP (CAB INTERIOR HOLLOWED OUT FOR CLEAR DRIVER VIEW)
# ==============================================================================
def generate_tactical_truck_model(path):
    bones = []
    root = {"name": "root", "pivot": [0, 0, 0], "cubes": []}
    bones.append(root)

    chassis = {
        "name": "chassis",
        "parent": "root",
        "pivot": [0, 10, 0],
        "cubes": [
            {"origin": [-16, 8, -48], "size": [32, 6, 96], "uv": [256, 0]},
            {"origin": [-19, 10, -52], "size": [38, 8, 6], "uv": [0, 128]},
            {"origin": [-8, 11, -55], "size": [16, 6, 4], "uv": [384, 128]},
            {"origin": [-19, 10, 47], "size": [38, 6, 5], "uv": [0, 192]},
            {"origin": [-14, 6, -30], "size": [28, 3, 60], "uv": [256, 0]}
        ]
    }
    bones.append(chassis)

    # Hollow Cab Shell: Hollow inside with floor, lower doors, pillars, roof and clear glass
    cab = {
        "name": "cab",
        "parent": "chassis",
        "pivot": [0, 14, -12],
        "cubes": [
            # Hood / Engine Bay (Lowered so driver can see clearly over it!)
            {"origin": [-16, 14, -48], "size": [32, 8, 24], "uv": [0, 0]},
            # Front Radiator Grille
            {"origin": [-15, 14, -49], "size": [30, 8, 2], "uv": [192, 0]},
            # Cab Floor (y = 14..16)
            {"origin": [-17, 14, -24], "size": [34, 2, 28], "uv": [256, 0]},
            # Lower Doors Left & Right (y = 16..24 - keeps driver chest open to window)
            {"origin": [-18, 16, -24], "size": [2, 8, 28], "uv": [0, 0]},
            {"origin": [16, 16, -24], "size": [2, 8, 28], "uv": [0, 0]},
            # Armored Cab Roof (y = 35..38)
            {"origin": [-17, 35, -24], "size": [34, 3, 28], "uv": [0, 0]},
            # A-Pillars & Windshield Header
            {"origin": [-17, 24, -24], "size": [2, 11, 2], "uv": [0, 0]},
            {"origin": [15, 24, -24], "size": [2, 11, 2], "uv": [0, 0]},
            {"origin": [-16, 33, -24], "size": [32, 2, 2], "uv": [0, 0]},
            # Ballistic Windshield Glass (Clean alpha cutout)
            {"origin": [-15, 24, -23], "size": [30, 9, 1], "uv": [128, 0]},
            # Side Windows
            {"origin": [-17.5, 24, -22], "size": [1, 9, 22], "uv": [128, 0]},
            {"origin": [16.5, 24, -22], "size": [1, 9, 22], "uv": [128, 0]},
            # Rear Cab Wall with window
            {"origin": [-17, 16, 3], "size": [34, 18, 2], "uv": [0, 0]},
            # Roof LED Light Bar
            {"origin": [-14, 38, -22], "size": [28, 3, 3], "uv": [192, 0]},

            # INTERIOR COCKPIT (Engineered specifically for driver seat at x = 8, y = 20, z = -10):
            # Low Dashboard Console (Kept at y = 18..21 so it does not block the road view!)
            {"origin": [-15, 16, -23], "size": [30, 5, 5], "uv": [128, 192]},
            # Steering Wheel on left side (x = 8, y = 20, z = -18)
            {"origin": [6, 19, -19], "size": [4, 4, 1], "uv": [128, 128]},
            # Left Driver Bucket Seat (y = 16 cushion, y = 18..27 backrest)
            {"origin": [4, 16, -14], "size": [8, 2, 8], "uv": [128, 192]},
            {"origin": [4, 18, -6], "size": [8, 10, 2], "uv": [128, 192]},
            # Right Passenger Bucket Seat
            {"origin": [-12, 16, -14], "size": [8, 2, 8], "uv": [128, 192]},
            {"origin": [-12, 18, -6], "size": [8, 10, 2], "uv": [128, 192]}
        ]
    }
    bones.append(cab)

    # Rear Cargo Bed
    bed = {
        "name": "bed",
        "parent": "chassis",
        "pivot": [0, 14, 22],
        "cubes": [
            {"origin": [-18, 13, 6], "size": [36, 2, 40], "uv": [384, 0]},
            {"origin": [-18, 15, 6], "size": [3, 11, 40], "uv": [0, 0]},
            {"origin": [15, 15, 6], "size": [3, 11, 40], "uv": [0, 0]},
            {"origin": [-16, 14, 45], "size": [32, 11, 2], "uv": [0, 128]},
            {"origin": [-17, 15, 7], "size": [3, 20, 3], "uv": [256, 0]},
            {"origin": [14, 15, 7], "size": [3, 20, 3], "uv": [256, 0]},
            {"origin": [-15, 33, 7], "size": [30, 2, 3], "uv": [256, 0]}
        ]
    }
    bones.append(bed)

    cargo_straps = {
        "name": "cargo_straps",
        "parent": "bed",
        "pivot": [0, 15, 24],
        "cubes": [
            {"origin": [-15, 15, 18], "size": [30, 1, 3], "uv": [128, 128]},
            {"origin": [-15, 15, 32], "size": [30, 1, 3], "uv": [128, 128]}
        ]
    }
    bones.append(cargo_straps)

    # Wheels
    wheel_fl = {"name": "wheel_fl", "parent": "chassis", "pivot": [21, 9, -36], "cubes": make_wheel(21, 9, -36, 17, 8, 9)}
    wheel_fr = {"name": "wheel_fr", "parent": "chassis", "pivot": [-21, 9, -36], "cubes": make_wheel(-21, 9, -36, -25, 8, 9)}
    wheel_rl = {"name": "wheel_rl", "parent": "chassis", "pivot": [21, 9, 28], "cubes": make_wheel(21, 9, 28, 17, 8, 9)}
    wheel_rr = {"name": "wheel_rr", "parent": "chassis", "pivot": [-21, 9, 28], "cubes": make_wheel(-21, 9, 28, -25, 8, 9)}
    bones.extend([wheel_fl, wheel_fr, wheel_rl, wheel_rr])

    write_geo(path, "geometry.tactical_truck", bones, bounds_w=3.2, bounds_h=2.6, bounds_y=1.3)


# ==============================================================================
# 3. CHINOOK TRANSPORTER (PANORAMIC FLIGHT DECK GLASSED COCKPIT)
# ==============================================================================
def generate_chinook_model(path):
    bones = []
    root = {"name": "root", "pivot": [0, 0, 0], "cubes": []}
    bones.append(root)

    fuselage = {
        "name": "fuselage",
        "parent": "root",
        "pivot": [0, 24, 0],
        "cubes": [
            # Main Cargo Cabin Body (Hollow floor at y = 11, roof at y = 36, z = -50..56)
            {"origin": [-18, 10, -50], "size": [36, 2, 106], "uv": [384, 0]},
            {"origin": [-18, 36, -50], "size": [36, 2, 106], "uv": [0, 0]},
            {"origin": [-18, 12, -50], "size": [2, 24, 106], "uv": [0, 0]},
            {"origin": [16, 12, -50], "size": [2, 24, 106], "uv": [0, 0]},

            # Sponson Pods
            {"origin": [18, 8, -36], "size": [8, 12, 80], "uv": [256, 128]},
            {"origin": [-26, 8, -36], "size": [8, 12, 80], "uv": [256, 128]},

            # Pylons
            {"origin": [-12, 38, -52], "size": [24, 14, 20], "uv": [0, 0]},
            {"origin": [-12, 38, 40], "size": [24, 20, 26], "uv": [0, 0]},
            {"origin": [12, 32, 34], "size": [10, 12, 28], "uv": [192, 0]},
            {"origin": [-22, 32, 34], "size": [10, 12, 28], "uv": [192, 0]},

            # Forward Flight Deck / Cockpit (Hollow inside, nose at z = -78..-50)
            # Cockpit floor y = 11..13
            {"origin": [-16, 11, -76], "size": [32, 2, 26], "uv": [0, 0]},
            # Cockpit roof y = 35..37
            {"origin": [-16, 35, -74], "size": [32, 2, 24], "uv": [0, 0]},
            # Cockpit Nose Cone (y = 12..20, z = -80..-74)
            {"origin": [-15, 12, -80], "size": [30, 8, 6], "uv": [0, 0]},
            # Large Panoramic Greenhouse Windshield (y = 20..35, z = -79) - Clear view!
            {"origin": [-15, 20, -79], "size": [30, 15, 1], "uv": [128, 0]},
            # Cockpit Side Windows Left & Right
            {"origin": [-16, 20, -75], "size": [1, 15, 22], "uv": [128, 0]},
            {"origin": [15, 20, -75], "size": [1, 15, 22], "uv": [128, 0]},

            # COCKPIT INTERIOR:
            # Low Dash Console with Instruments (y = 16..20, z = -76..-72)
            {"origin": [-14, 16, -76], "size": [28, 4, 5], "uv": [128, 192]},
            # Left Pilot Seat (x = 7, y = 13 cushion, y = 16..26 backrest, z = -65)
            {"origin": [3, 13, -68], "size": [8, 3, 8], "uv": [128, 192]},
            {"origin": [3, 16, -60], "size": [8, 10, 2], "uv": [128, 192]},
            # Right Co-Pilot Seat
            {"origin": [-11, 13, -68], "size": [8, 3, 8], "uv": [128, 192]},
            {"origin": [-11, 16, -60], "size": [8, 10, 2], "uv": [128, 192]}
        ]
    }
    bones.append(fuselage)

    # Rear Ramp
    ramp = {
        "name": "ramp",
        "parent": "fuselage",
        "pivot": [0, 11, 56],
        "cubes": [
            {"origin": [-16, 11, 56], "size": [32, 2, 24], "uv": [384, 0]},
            {"origin": [-16, 13, 56], "size": [32, 16, 2], "uv": [0, 128]}
        ]
    }
    bones.append(ramp)

    # Cargo Sling Rig (Hideable)
    cargo_straps = {
        "name": "cargo_straps",
        "parent": "fuselage",
        "pivot": [0, 7, 0],
        "cubes": [
            {"origin": [-8, 7, -10], "size": [16, 3, 20], "uv": [384, 128]},
            {"origin": [-3, 3, -4], "size": [6, 4, 8], "uv": [128, 128]}
        ]
    }
    bones.append(cargo_straps)

    # Rotors
    rotor_front = {
        "name": "rotor_front",
        "parent": "fuselage",
        "pivot": [0, 52, -42],
        "cubes": [
            {"origin": [-4, 52, -46], "size": [8, 4, 8], "uv": [192, 0]},
            {"origin": [-3, 54, -106], "size": [6, 1, 60], "uv": [256, 0]},
            {"origin": [16, 54, -20], "size": [50, 1, 6], "uv": [256, 0]},
            {"origin": [-66, 54, -20], "size": [50, 1, 6], "uv": [256, 0]}
        ]
    }
    rotor_aft = {
        "name": "rotor_aft",
        "parent": "fuselage",
        "pivot": [0, 58, 52],
        "cubes": [
            {"origin": [-4, 58, 48], "size": [8, 4, 8], "uv": [192, 0]},
            {"origin": [-3, 60, 56], "size": [6, 1, 60], "uv": [256, 0]},
            {"origin": [16, 60, 40], "size": [50, 1, 6], "uv": [256, 0]},
            {"origin": [-66, 60, 40], "size": [50, 1, 6], "uv": [256, 0]}
        ]
    }
    bones.extend([rotor_front, rotor_aft])

    # Landing Gear
    gear_fl = {"name": "gear_fl", "parent": "fuselage", "pivot": [20, 4, -32], "cubes": make_wheel(20, 4, -32, 17, 6, 5)}
    gear_fr = {"name": "gear_fr", "parent": "fuselage", "pivot": [-20, 4, -32], "cubes": make_wheel(-20, 4, -32, -23, 6, 5)}
    gear_rl = {"name": "gear_rl", "parent": "fuselage", "pivot": [20, 4, 38], "cubes": make_wheel(20, 4, 38, 17, 6, 5)}
    gear_rr = {"name": "gear_rr", "parent": "fuselage", "pivot": [-20, 4, 38], "cubes": make_wheel(-20, 4, 38, -23, 6, 5)}
    bones.extend([gear_fl, gear_fr, gear_rl, gear_rr])

    write_geo(path, "geometry.chinook_transporter", bones, bounds_w=8.5, bounds_h=5.0, bounds_y=2.5)


for base in ["Titan Combat/src/main/resources/assets/titancombat/geo", "Titan Combat/src/main/resources/assets/titancombat/geo/transport"]:
    generate_ocean_carrier_model(f"{base}/ocean_carrier.geo.json")
    generate_tactical_truck_model(f"{base}/tactical_truck.geo.json")
    generate_chinook_model(f"{base}/chinook_transporter.geo.json")

print("Generated enhanced vehicle geos successfully!")
