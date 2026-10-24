import json, os, zlib, struct

# Target directories
GEO_DIR = "Titan Combat/src/main/resources/assets/titancombat/geo/flight"
TEX_DIR = "Titan Combat/src/main/resources/assets/titancombat/textures/entity/flight"
ITEM_TEX_DIR = "Titan Combat/src/main/resources/assets/titancombat/textures/item"

os.makedirs(GEO_DIR, exist_ok=True)
os.makedirs(TEX_DIR, exist_ok=True)
os.makedirs(ITEM_TEX_DIR, exist_ok=True)

# ==============================================================================
# Pure Python PNG Writer (RGBA 8-bit)
# ==============================================================================
def write_png(filename, width, height, pixels):
    """pixels is a bytearray of length width * height * 4 (RGBA)"""
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    header = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0) # filter type none
        row_start = y * width * 4
        raw_data.extend(pixels[row_start : row_start + width * 4])
    idat = chunk(b"IDAT", zlib.compress(bytes(raw_data), 9))
    iend = chunk(b"IEND", b"")
    with open(filename, "wb") as f:
        f.write(header + ihdr + idat + iend)
    print(f"Saved PNG: {filename} ({width}x{height})")

# ==============================================================================
# 1. SKY-LIFTER QUAD-DRONE MODEL
# ==============================================================================
def build_drone_geo():
    bones = []
    # Main Root / Docking Pylon
    bones.append({
        "name": "root",
        "pivot": [0, 0, 0]
    })
    bones.append({
        "name": "docking_mount",
        "parent": "root",
        "pivot": [0, 0, 0],
        "cubes": [
            # Heavy central backbone chassis
            {"origin": [-5, -6, 0], "size": [10, 14, 4], "uv": [0, 0]},
            # Spine power conduits
            {"origin": [-2.5, 8, 1], "size": [5, 4, 3], "uv": [28, 0]},
            # Central fusion reactor core
            {"origin": [-3.5, -4, 4], "size": [7, 10, 4], "uv": [0, 18]},
            # Avionics & GPS dome
            {"origin": [-2, 12, 1.5], "size": [4, 2, 2.5], "uv": [44, 0]},
            # Emergency warning strobe
            {"origin": [-1, 14, 2], "size": [2, 1.5, 1.5], "uv": [56, 0]},
            # Left Outrigger Boom Front
            {"origin": [4, 4, 1.5], "size": [10, 3, 3], "uv": [28, 7]},
            # Right Outrigger Boom Front
            {"origin": [-14, 4, 1.5], "size": [10, 3, 3], "uv": [28, 7]},
            # Left Outrigger Boom Rear
            {"origin": [4, 0, 4.5], "size": [11, 3.5, 3.5], "uv": [28, 13]},
            # Right Outrigger Boom Rear
            {"origin": [-15, 0, 4.5], "size": [11, 3.5, 3.5], "uv": [28, 13]},
        ]
    })

    # Rotor Front-Left
    bones.append({
        "name": "rotor_fl",
        "parent": "docking_mount",
        "pivot": [15, 5, 3],
        "cubes": [
            # Ducted Cowling Ring
            {"origin": [11, 3, -1], "size": [8, 4, 8], "uv": [0, 32]},
            # Vector Nozzle Below
            {"origin": [12, 1, 0], "size": [6, 2, 6], "uv": [32, 32]},
            # Intake Protective Strut
            {"origin": [14.5, 7, -1], "size": [1, 1, 8], "uv": [0, 0]},
        ]
    })
    bones.append({
        "name": "fan_fl",
        "parent": "rotor_fl",
        "pivot": [15, 5, 3],
        "cubes": [
            {"origin": [14, 4.5, 2], "size": [2, 1, 2], "uv": [56, 32]},
            {"origin": [11.5, 4.8, 2.5], "size": [7, 0.4, 1], "uv": [0, 44]},
            {"origin": [14.5, 4.8, -0.5], "size": [1, 0.4, 7], "uv": [16, 44]},
        ]
    })

    # Rotor Front-Right
    bones.append({
        "name": "rotor_fr",
        "parent": "docking_mount",
        "pivot": [-15, 5, 3],
        "cubes": [
            {"origin": [-19, 3, -1], "size": [8, 4, 8], "uv": [0, 32]},
            {"origin": [-18, 1, 0], "size": [6, 2, 6], "uv": [32, 32]},
            {"origin": [-15.5, 7, -1], "size": [1, 1, 8], "uv": [0, 0]},
        ]
    })
    bones.append({
        "name": "fan_fr",
        "parent": "rotor_fr",
        "pivot": [-15, 5, 3],
        "cubes": [
            {"origin": [-16, 4.5, 2], "size": [2, 1, 2], "uv": [56, 32]},
            {"origin": [-18.5, 4.8, 2.5], "size": [7, 0.4, 1], "uv": [0, 44]},
            {"origin": [-15.5, 4.8, -0.5], "size": [1, 0.4, 7], "uv": [16, 44]},
        ]
    })

    # Rotor Rear-Left
    bones.append({
        "name": "rotor_rl",
        "parent": "docking_mount",
        "pivot": [16, 1, 7],
        "cubes": [
            {"origin": [11.5, -1, 2.5], "size": [9, 4, 9], "uv": [0, 48]},
            {"origin": [13, -3, 4], "size": [6, 2, 6], "uv": [36, 48]},
        ]
    })
    bones.append({
        "name": "fan_rl",
        "parent": "rotor_rl",
        "pivot": [16, 1, 7],
        "cubes": [
            {"origin": [15, 0.5, 6], "size": [2, 1, 2], "uv": [56, 32]},
            {"origin": [12.5, 0.8, 6.5], "size": [7, 0.4, 1], "uv": [0, 44]},
            {"origin": [15.5, 0.8, 3.5], "size": [1, 0.4, 7], "uv": [16, 44]},
        ]
    })

    # Rotor Rear-Right
    bones.append({
        "name": "rotor_rr",
        "parent": "docking_mount",
        "pivot": [-16, 1, 7],
        "cubes": [
            {"origin": [-20.5, -1, 2.5], "size": [9, 4, 9], "uv": [0, 48]},
            {"origin": [-19, -3, 4], "size": [6, 2, 6], "uv": [36, 48]},
        ]
    })
    bones.append({
        "name": "fan_rr",
        "parent": "rotor_rr",
        "pivot": [-16, 1, 7],
        "cubes": [
            {"origin": [-17, 0.5, 6], "size": [2, 1, 2], "uv": [56, 32]},
            {"origin": [-19.5, 0.8, 6.5], "size": [7, 0.4, 1], "uv": [0, 44]},
            {"origin": [-16.5, 0.8, 3.5], "size": [1, 0.4, 7], "uv": [16, 44]},
        ]
    })

    return {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.flight_module_drone_lifter",
                "texture_width": 128,
                "texture_height": 128,
                "visible_bounds_width": 5,
                "visible_bounds_height": 5,
                "visible_bounds_offset": [0, 1, 0]
            },
            "bones": bones
        }]
    }

# ==============================================================================
# 2. VIPER AERO-BOOSTER (ROCKET JETPACK) MODEL
# ==============================================================================
def build_rocket_geo():
    bones = []
    bones.append({"name": "root", "pivot": [0, 0, 0]})
    bones.append({
        "name": "docking_mount",
        "parent": "root",
        "pivot": [0, 0, 0],
        "cubes": [
            # Reinforced Dorsal Interface
            {"origin": [-6, -8, 0], "size": [12, 18, 3.5], "uv": [0, 0]},
            # Thermal Tile Shield Array
            {"origin": [-4.5, -6, 3.5], "size": [9, 14, 2], "uv": [32, 0]},
            # High-Flow Turbopump Distributor
            {"origin": [-3.5, -3, 5.5], "size": [7, 8, 4], "uv": [0, 22]},
            # Left Tank Fuel Conduit
            {"origin": [3.5, 4, 3], "size": [3, 2, 4], "uv": [22, 22]},
            # Right Tank Fuel Conduit
            {"origin": [-6.5, 4, 3], "size": [3, 2, 4], "uv": [22, 22]},
            # Cryo Valve & Pressure Gauge
            {"origin": [-1.5, 10, 1.5], "size": [3, 3, 3], "uv": [36, 22]},
            # Warning Beacon Top
            {"origin": [-1, 13, 2.5], "size": [2, 1.5, 1.5], "uv": [48, 22]},
            # Left Booster Rocket Tank
            {"origin": [4.5, -7, 2], "size": [6, 20, 6], "uv": [54, 0]},
            # Left Tank Nosecone
            {"origin": [5, 13, 2.5], "size": [5, 3, 5], "uv": [78, 0]},
            # Left Tank Reinforcement Ring 1
            {"origin": [4, 0, 1.5], "size": [7, 1.5, 7], "uv": [78, 8]},
            # Left Tank Reinforcement Ring 2
            {"origin": [4, 8, 1.5], "size": [7, 1.5, 7], "uv": [78, 8]},
            # Right Booster Rocket Tank
            {"origin": [-10.5, -7, 2], "size": [6, 20, 6], "uv": [54, 0]},
            # Right Tank Nosecone
            {"origin": [-10, 13, 2.5], "size": [5, 3, 5], "uv": [78, 0]},
            # Right Tank Reinforcement Ring 1
            {"origin": [-11, 0, 1.5], "size": [7, 1.5, 7], "uv": [78, 8]},
            # Right Tank Reinforcement Ring 2
            {"origin": [-11, 8, 1.5], "size": [7, 1.5, 7], "uv": [78, 8]},
            # Left RCS Pod
            {"origin": [10.5, 5, 3], "size": [3, 4, 3.5], "uv": [78, 17]},
            # Right RCS Pod
            {"origin": [-13.5, 5, 3], "size": [3, 4, 3.5], "uv": [78, 17]},
        ]
    })

    # Left Gimballed Rocket Bell Nozzle
    bones.append({
        "name": "nozzle_left",
        "parent": "docking_mount",
        "pivot": [7.5, -8, 5],
        "cubes": [
            # Throat Collar
            {"origin": [5.5, -9, 3], "size": [4, 2, 4], "uv": [0, 34]},
            # Flared Combustion Bell
            {"origin": [4.5, -15, 2], "size": [6, 6, 6], "uv": [16, 34]},
            # Glowing Core
            {"origin": [5.5, -14, 3], "size": [4, 1, 4], "uv": [40, 34]},
        ]
    })

    # Right Gimballed Rocket Bell Nozzle
    bones.append({
        "name": "nozzle_right",
        "parent": "docking_mount",
        "pivot": [-7.5, -8, 5],
        "cubes": [
            # Throat Collar
            {"origin": [-9.5, -9, 3], "size": [4, 2, 4], "uv": [0, 34]},
            # Flared Combustion Bell
            {"origin": [-10.5, -15, 2], "size": [6, 6, 6], "uv": [16, 34]},
            # Glowing Core
            {"origin": [-9.5, -14, 3], "size": [4, 1, 4], "uv": [40, 34]},
        ]
    })

    return {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.flight_module_rocket_jetpack",
                "texture_width": 128,
                "texture_height": 128,
                "visible_bounds_width": 5,
                "visible_bounds_height": 5,
                "visible_bounds_offset": [0, 1, 0]
            },
            "bones": bones
        }]
    }

# ==============================================================================
# 3. APEX STRATOS-WINGS (VTOL GLIDE) MODEL
# ==============================================================================
def build_vtol_geo():
    bones = []
    bones.append({"name": "root", "pivot": [0, 0, 0]})
    bones.append({
        "name": "docking_mount",
        "parent": "root",
        "pivot": [0, 0, 0],
        "cubes": [
            # Center Keel Fuselage
            {"origin": [-4, -6, 0], "size": [8, 16, 4], "uv": [0, 0]},
            # Dorsal Air Intake Spine
            {"origin": [-3, 4, 3], "size": [6, 8, 3.5], "uv": [24, 0]},
            # Avionics & Telemetry Cowl
            {"origin": [-2, 10, 4.5], "size": [4, 3, 3], "uv": [44, 0]},
            # Center Vertical Stabilizer Tail Fin
            {"origin": [-1, 2, 6], "size": [2, 14, 6], "uv": [0, 20]},
            # Swept Fin Tip
            {"origin": [-0.6, 16, 8], "size": [1.2, 4, 3.5], "uv": [16, 20]},
            # Strobe Beacon on Fin
            {"origin": [-0.8, 20, 9.5], "size": [1.6, 1.2, 1.5], "uv": [26, 20]},
        ]
    })

    # Left Swept Wing & Turbine
    bones.append({
        "name": "left_wing",
        "parent": "docking_mount",
        "pivot": [4, 4, 3],
        "cubes": [
            # Wing Root Fairing
            {"origin": [4, 3, 1], "size": [8, 3, 9], "uv": [40, 12]},
            # Main Swept Wing Section
            {"origin": [12, 3.5, 3], "size": [12, 2, 7], "uv": [0, 40]},
            # Outer Wingtip Section
            {"origin": [24, 4, 4.5], "size": [8, 1.5, 5], "uv": [38, 40]},
            # Vertical Winglet Tip
            {"origin": [31.5, 4, 5], "size": [1, 5, 4], "uv": [64, 40]},
            # Green Starboard Nav Light
            {"origin": [31.2, 8.5, 6.5], "size": [1.5, 1, 1.5], "uv": [74, 40]},
            # Underwing Jet Nacelle
            {"origin": [6, -1, 2], "size": [5, 4.5, 11], "uv": [0, 50]},
            # Jet Intake Lip
            {"origin": [6.2, -0.8, 1], "size": [4.6, 4.1, 1.2], "uv": [32, 50]},
            # 2D Vectoring Exhaust Nozzle
            {"origin": [6.2, -0.6, 13], "size": [4.6, 3.7, 2.5], "uv": [44, 50]},
        ]
    })

    # Right Swept Wing & Turbine
    bones.append({
        "name": "right_wing",
        "parent": "docking_mount",
        "pivot": [-4, 4, 3],
        "cubes": [
            # Wing Root Fairing
            {"origin": [-12, 3, 1], "size": [8, 3, 9], "uv": [40, 12]},
            # Main Swept Wing Section
            {"origin": [-24, 3.5, 3], "size": [12, 2, 7], "uv": [0, 40]},
            # Outer Wingtip Section
            {"origin": [-32, 4, 4.5], "size": [8, 1.5, 5], "uv": [38, 40]},
            # Vertical Winglet Tip
            {"origin": [-32.5, 4, 5], "size": [1, 5, 4], "uv": [64, 40]},
            # Red Port Nav Light
            {"origin": [-32.7, 8.5, 6.5], "size": [1.5, 1, 1.5], "uv": [74, 40]},
            # Underwing Jet Nacelle
            {"origin": [-11, -1, 2], "size": [5, 4.5, 11], "uv": [0, 50]},
            # Jet Intake Lip
            {"origin": [-10.8, -0.8, 1], "size": [4.6, 4.1, 1.2], "uv": [32, 50]},
            # 2D Vectoring Exhaust Nozzle
            {"origin": [-10.8, -0.6, 13], "size": [4.6, 3.7, 2.5], "uv": [44, 50]},
        ]
    })

    return {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.flight_module_vtol_glide",
                "texture_width": 128,
                "texture_height": 128,
                "visible_bounds_width": 6,
                "visible_bounds_height": 5,
                "visible_bounds_offset": [0, 1, 0]
            },
            "bones": bones
        }]
    }

# Save Geo JSONs
with open(os.path.join(GEO_DIR, "drone_lifter.geo.json"), "w") as f:
    json.dump(build_drone_geo(), f, indent=2)
with open(os.path.join(GEO_DIR, "rocket_jetpack.geo.json"), "w") as f:
    json.dump(build_rocket_geo(), f, indent=2)
with open(os.path.join(GEO_DIR, "vtol_glide.geo.json"), "w") as f:
    json.dump(build_vtol_geo(), f, indent=2)

print("Generated all 3 Geo JSON models successfully!")

# ==============================================================================
# TEXTURE GENERATION (128x128 High-Tech Mecha Palettes)
# ==============================================================================
def make_palette_texture(theme):
    w, h = 128, 128
    buf = bytearray(w * h * 4)

    def set_px(x, y, r, g, b, a=255):
        if 0 <= x < w and 0 <= y < h:
            idx = (y * w + x) * 4
            buf[idx] = r
            buf[idx+1] = g
            buf[idx+2] = b
            buf[idx+3] = a

    def fill_rect(x1, y1, x2, y2, r, g, b, a=255):
        for y in range(max(0, y1), min(h, y2)):
            for x in range(max(0, x1), min(w, x2)):
                set_px(x, y, r, g, b, a)

    # Base Dark Armored Titanium Chassis
    fill_rect(0, 0, 128, 128, 42, 45, 52)

    # Subtle panel line grid
    for y in range(0, 128, 8):
        for x in range(128):
            set_px(x, y, 32, 34, 40)
    for x in range(0, 128, 8):
        for y in range(128):
            set_px(x, y, 32, 34, 40)

    if theme == "drone":
        # White & Industrial Hazard Yellow / Cyan Glow
        # Primary panels: Light composite armor (Off-white / tactical grey)
        fill_rect(0, 0, 28, 18, 185, 190, 198)
        fill_rect(28, 0, 44, 7, 160, 165, 172)
        # Hazard stripes on outriggers
        for x in range(28, 60):
            for y in range(7, 18):
                if (x + y) % 6 < 3:
                    set_px(x, y, 220, 160, 20) # Amber yellow
                else:
                    set_px(x, y, 35, 38, 42)   # Dark carbon
        # Turbine Ducts (Metallic Titanium)
        fill_rect(0, 32, 32, 44, 90, 95, 105)
        fill_rect(32, 32, 56, 44, 60, 64, 72)
        # Fan Blades (Steel Grey)
        fill_rect(0, 44, 32, 48, 140, 145, 155)
        # Rear nacelles
        fill_rect(0, 48, 36, 60, 80, 85, 95)
        fill_rect(36, 48, 56, 60, 50, 55, 62)
        # Energy Core & Nozzle Glow (Cyan/Aqua LED)
        fill_rect(0, 18, 28, 28, 0, 220, 255)
        for i in range(12):
            set_px(i*2, 20, 200, 255, 255)
        # Warning Beacon (Bright Red)
        fill_rect(56, 0, 62, 5, 255, 30, 30)

    elif theme == "rocket":
        # Gunmetal, Heavy Industrial Orange & Scorched Steel
        # Main chassis mount: Dark ballistic steel
        fill_rect(0, 0, 32, 22, 55, 58, 65)
        # Thermal tile array (Hex heat tiles)
        for y in range(0, 22):
            for x in range(32, 54):
                if (x//2 + y//2) % 2 == 0:
                    set_px(x, y, 25, 26, 28)
                else:
                    set_px(x, y, 35, 37, 40)
        # Liquid Propellant Tanks (Heavy Industrial Titanium with Apex Red/Orange bands)
        fill_rect(54, 0, 78, 30, 140, 145, 152)
        fill_rect(78, 0, 95, 16, 210, 80, 30) # Orange apex nosecones
        # Reinforcement bands
        fill_rect(78, 8, 95, 16, 40, 42, 46)
        # Rocket Exhaust Bell (Heat-tempered gradient)
        for y in range(34, 48):
            blend = (y - 34) / 14.0
            r = int(50 + blend * 70)
            g = int(55 + blend * 40)
            b = int(70 - blend * 20)
            for x in range(16, 40):
                set_px(x, y, r, g, b)
        # Glowing Combustion Chamber Core (Blazing Orange/Yellow Plasma)
        fill_rect(40, 34, 52, 42, 255, 140, 0)
        fill_rect(42, 36, 48, 40, 255, 240, 120) # Core white heat
        # Warning Beacon
        fill_rect(48, 22, 54, 28, 255, 40, 40)

    elif theme == "vtol":
        # Stealth Navy Blue, Carbon Fiber & Aerodynamic White/Gold
        # Fuselage: Stealth dark blue-grey
        fill_rect(0, 0, 24, 20, 45, 52, 65)
        # Intake spine: Jet fighter matte grey
        fill_rect(24, 0, 44, 16, 130, 138, 148)
        # Tail fin & Rudder
        fill_rect(0, 20, 16, 36, 35, 42, 54)
        # Swept Wings: Stealth Camo Carbon Texture
        for y in range(40, 48):
            for x in range(0, 60):
                if (x + y) % 4 == 0:
                    set_px(x, y, 30, 35, 42)
                else:
                    set_px(x, y, 65, 75, 88)
        # Outer wingtips & winglets
        fill_rect(38, 40, 64, 48, 150, 160, 175)
        fill_rect(64, 40, 74, 48, 220, 160, 20) # Golden yellow winglet
        # Navigation lights: Green (Starboard) & Red (Port)
        fill_rect(74, 40, 78, 44, 20, 255, 80)
        fill_rect(74, 44, 78, 48, 255, 40, 40)
        # Jet Engines (Turbine housings)
        fill_rect(0, 50, 32, 64, 85, 92, 102)
        # 2D Vectoring Nozzles (Glowing Ion Blue)
        fill_rect(44, 50, 58, 62, 0, 180, 255)
        fill_rect(47, 53, 55, 59, 200, 245, 255) # Core white ion stream

    return buf

# Write entity textures
write_png(os.path.join(TEX_DIR, "drone_lifter.png"), 128, 128, make_palette_texture("drone"))
write_png(os.path.join(TEX_DIR, "rocket_jetpack.png"), 128, 128, make_palette_texture("rocket"))
write_png(os.path.join(TEX_DIR, "vtol_glide.png"), 128, 128, make_palette_texture("vtol"))

# Also write to item textures
write_png(os.path.join(ITEM_TEX_DIR, "flight_module_drone_lifter.png"), 128, 128, make_palette_texture("drone"))
write_png(os.path.join(ITEM_TEX_DIR, "flight_module_rocket_jetpack.png"), 128, 128, make_palette_texture("rocket"))
write_png(os.path.join(ITEM_TEX_DIR, "flight_module_vtol_glide.png"), 128, 128, make_palette_texture("vtol"))

print("All textures created successfully!")
