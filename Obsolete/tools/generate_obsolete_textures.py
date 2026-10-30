"""Synthesizes high-definition 512x512 textures for OBSOLETE mecha mod with anime-accurate faction colors and decals."""
import struct
import zlib
import os
import json

def create_png(width, height, get_pixel_func):
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # filter type 0 (None)
        for x in range(width):
            r, g, b, a = get_pixel_func(x, y)
            raw_data.extend([int(r) & 255, int(g) & 255, int(b) & 255, int(a) & 255])

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(bytes(raw_data), level=9))
    iend = chunk(b'IEND', b'')
    return header + ihdr + idat + iend

def gen_exoframe_512(x, y):
    # --- 1. Assist Wheels (uv: 50..80, 0..30 & 90..120, 180..210) ---
    is_wheel = (50 <= x <= 80 and 0 <= y <= 30) or (90 <= x <= 125 and 180 <= y <= 215)
    if is_wheel:
        cx, cy = (65, 15) if y < 100 else (107, 197)
        dist = abs(x - cx) + abs(y - cy)
        if dist <= 3:
            return (215, 220, 230, 255) # Center axle bolt
        elif dist <= 8:
            return (95, 100, 110, 255)  # Machined steel wheel hub
        elif (x + y) % 3 == 0:
            return (18, 20, 22, 255)    # Deep chevron tread groove
        return (36, 40, 44, 255)        # Heavy duty tyre rubber

    # --- 2. Head Sensor Camera (uv: 160..195, 0..35) ---
    if 160 <= x <= 195 and 0 <= y <= 35:
        if 168 <= x <= 176 and 8 <= y <= 16:
            return (0, 240, 255, 255)   # Glowing cyan optical camera lens
        if 178 <= x <= 182 and 8 <= y <= 12:
            return (50, 255, 80, 255)   # Green sensor diode
        if (x + y) % 4 == 0:
            return (30, 32, 36, 255)
        return (48, 52, 58, 255)        # Sensor chassis gunmetal

    # --- 3. Sand PMC Armor (uv: 200..255, 0..220) ---
    if 200 <= x <= 255 and 0 <= y <= 220:
        noise = (x * 7 + y * 13) % 10
        if (x % 10 in (0, 9) and y % 10 in (0, 9)):
            return (85, 78, 62, 255)    # Hex mounting rivet
        if x in (201, 254) or y in (1, 49, 51, 119, 121, 169, 171):
            return (160 - noise, 145 - noise, 105 - noise, 255) # Edge bevel
        return (194 - noise, 178 - noise, 128 - noise, 255)     # Desert Sand

    # --- 4. USMC Armor (Olive Drab + Skull Insignia) (uv: 260..325, 0..280) ---
    if 260 <= x <= 325 and 0 <= y <= 280:
        # Skull emblem on USMC head canopy (Image 1)
        if 260 <= x <= 320 and 0 <= y <= 45:
            # Stencil skull decal centered at (278, 20)
            dx = abs(x - 278)
            dy = abs(y - 20)
            if (dx <= 6 and dy <= 6) or (dx <= 4 and 6 <= y - 20 <= 9):
                # Eye sockets and nose cavity
                if (dx in (2, 3) and dy in (1, 2)) or (dx == 0 and y == 23):
                    return (60, 72, 45, 255)
                return (240, 242, 245, 255) # White skull stencil
        # Contoured Olive Drab plate
        noise = (x * 11 + y * 7) % 8
        if (x in (261, 324) or y in (1, 49, 119, 169, 219)):
            return (55, 68, 40, 255)    # Dark OD seam
        return (82 - noise, 100 - noise, 58 - noise, 255)       # USMC Olive Drab

    # --- 5. Cerberus PMC Black Ops Armor (uv: 330..395, 0..280) ---
    if 330 <= x <= 395 and 0 <= y <= 280:
        # Red #1 marking panel on shoulder and dome
        if 345 <= x <= 358 and 130 <= y <= 155:
            if 348 <= x <= 353 and 133 <= y <= 150:
                return (245, 245, 250, 255) # White "1" numeral
            return (215, 30, 30, 255)       # Red Cerberus flash
        # Amber visor slit on dome helmet
        if 340 <= x <= 360 and 12 <= y <= 18:
            return (255, 185, 10, 255)      # Amber glowing sensor slit
        noise = (x * 5 + y * 13) % 6
        if (x in (331, 394) or y in (1, 49, 119, 169)):
            return (18, 20, 22, 255)        # Carbon seam
        return (32 - noise, 34 - noise, 38 - noise, 255)        # Tactical Matte Black

    # --- 6. VOTOMS Red Shoulder & Scopedog Green (uv: 400..510, 0..160) ---
    if 400 <= x <= 510 and 0 <= y <= 160:
        # Red Shoulder special (uv: 400..460, 50..95) - Image 4
        if 400 <= x <= 460 and 50 <= y <= 95:
            noise = (x * 7 + y * 11) % 8
            if x % 8 == 0 or y % 8 == 0:
                return (160, 25, 20, 255)   # Rivet line
            return (210 - noise, 35 - noise, 30 - noise, 255)   # Blood Sucker Crimson Red!

        # 3-Lens Turret Camera (uv: 400..450, 0..45)
        if 400 <= x <= 450 and 0 <= y <= 45:
            # Main lens (emerald green)
            if 410 <= x <= 420 and 10 <= y <= 20:
                return (0, 255, 120, 255)
            # Auxiliary red lens
            if 425 <= x <= 432 and 8 <= y <= 15:
                return (255, 40, 50, 255)
            # Zoom cyan lens
            if 422 <= x <= 428 and 22 <= y <= 28:
                return (0, 220, 255, 255)
            return (40, 44, 48, 255)

        # 9-Tube Shoulder Missile Pod (uv: 400..460, 100..160)
        if 400 <= x <= 460 and 100 <= y <= 160:
            if (x % 14 in (4, 5, 6, 7) and y % 14 in (4, 5, 6, 7)):
                return (220, 35, 35, 255)   # Red rocket warhead tips inside tubes
            return (70, 85, 55, 255)        # Olive drab launcher casing

    # --- 7. Militia / Guerrilla Woodland Camo Turtle Hood (uv: 400..510, 165..310) ---
    if 400 <= x <= 510 and 165 <= y <= 310:
        # Organic Woodland Camo pattern (Image 5)
        pattern = ((x // 8) * 13 + (y // 8) * 19) % 7
        if pattern in (0, 1):
            return (48, 62, 34, 255)        # Dark forest green
        elif pattern in (2, 3):
            return (105, 88, 55, 255)       # Earth brown
        elif pattern == 4:
            return (26, 28, 24, 255)        # Black shadow patch
        return (82, 104, 60, 255)           # Foliage green

    # --- 8. Industrial Safety Yellow Roll Cage (uv: 0..75, 240..315) ---
    if 0 <= x <= 75 and 240 <= y <= 315:
        # Diagonal black hazard warning stripes
        if (x + y) % 12 in (0, 1, 2, 3):
            return (28, 28, 30, 255)        # Black chevron
        return (255, 205, 0, 255)           # Caterpillar Safety Yellow

    # --- 9. Backpack Utility Modules (uv: 80..195, 240..315) ---
    if 80 <= x <= 195 and 240 <= y <= 315:
        if 140 <= x <= 195:
            # Ammo drum stencil
            if 155 <= x <= 170 and 260 <= y <= 266:
                return (245, 195, 20, 255)  # Caliber markings
            return (50, 58, 46, 255)        # Ammo olive
        return (72, 88, 52, 255)            # Cargo canvas green

    # --- 10. Precision Weapons (20mm Assault Rifle & USMC Sniper AMR) (uv: 0..175, 320..395) ---
    if 0 <= x <= 175 and 320 <= y <= 395:
        # Sniper scope lens (uv: 110..125, 330..345)
        if 112 <= x <= 122 and 332 <= y <= 342:
            return (30, 180, 255, 255)      # Anti-reflective coated scope lens
        if 20 <= x <= 45 and 350 <= y <= 370:
            return (28, 25, 24, 255)        # Textured polymer grip
        if (x + y) % 4 == 0:
            return (24, 26, 28, 255)
        return (45, 48, 54, 255)            # Parkerized sniper rifle steel

    # --- 11. Heavy Automatic Weapons (12.7mm HMG & M134 Minigun) (uv: 180..395, 320..395) ---
    if 180 <= x <= 395 and 320 <= y <= 395:
        # Brass bullet belt (uv: 215..235, 345..360)
        if 215 <= x <= 235 and 345 <= y <= 360:
            if (x % 5 in (1, 2, 3)):
                return (235, 185, 40, 255)  # Polished brass cartridge
            return (40, 42, 45, 255)        # Steel link belt
        if (x + y) % 4 == 0:
            return (30, 32, 35, 255)
        return (50, 54, 60, 255)            # Gunmetal receiver

    # --- 12. Explosive Launchers (Quad Pod & RPG-7 Heavy) (uv: 0..235, 400..510) ---
    if 0 <= x <= 235 and 400 <= y <= 510:
        # RPG-7 Demolition Warhead (uv: 150..190, 420..460) - Image 5
        if 150 <= x <= 190 and 420 <= y <= 460:
            # Massive blue/turquoise demolition bomb warhead
            if (x + y) % 6 in (0, 1):
                return (40, 150, 190, 255)
            return (55, 175, 215, 255)      # Standoff shaped-charge blue
        # Wooden heat wrap on RPG launcher
        if 125 <= x <= 145 and 420 <= y <= 450:
            return (130, 75, 35, 255)       # Varnished wood guard
        return (65, 78, 52, 255)            # Olive launcher tube

    # --- 13. Industrial Tools (Mining Drill & Forestry Chainsaw) (uv: 240..510, 400..510) ---
    if 240 <= x <= 510 and 400 <= y <= 510:
        # Mining Drill tungsten bit
        if 290 <= x <= 350 and 420 <= y <= 470:
            if (x + y) % 4 in (0, 1):
                return (185, 195, 210, 255) # Polished tungsten carbide
            return (115, 120, 130, 255)     # Flute depth
        # Chainsaw orange body & steel teeth
        if x >= 420:
            if (x + y) % 3 == 0:
                return (235, 240, 245, 255) # Hardened cutting teeth
            if x >= 460:
                return (130, 135, 142, 255) # Steel guide bar
            return (245, 100, 20, 255)      # Stihl Forestry Orange
        return (245, 190, 15, 255)          # Industrial Safety Yellow

    # --- 14. Pilot Seat & Controls (uv: 80..155, 50..120) ---
    if 80 <= x <= 155 and 50 <= y <= 120:
        if 95 <= x <= 135 and 65 <= y <= 105:
            return (34, 32, 30, 255)        # Cushioned pilot seat
        return (56, 60, 66, 255)            # Metal seat bucket

    # --- 15. Hydraulic Cylinders & Chrome Pistons ---
    if (x % 16 in (2, 3, 4) and y % 20 < 10) or (y % 20 in (5, 6)):
        return (205, 215, 230, 255)         # Polished hydraulic chrome

    # --- 16. Base Exoframe Skeleton (Default for all structural bones) ---
    noise = (x * 7 + y * 13) % 12
    base = 42 + noise
    if x % 10 == 0 or y % 10 == 0:
        return (28, 30, 34, 255)            # Structural joint recess
    return (base, base + 2, base + 6, 255)

base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src/main/resources/assets/obsolete"))

# Generate 512x512 Main Texture
tex_path = f"{base_dir}/textures/entity/exoframe/exoframe.png"
with open(tex_path, "wb") as f:
    f.write(create_png(512, 512, gen_exoframe_512))
print(f"Generated 512x512 texture: {tex_path}")

# Generate Item Icons
all_items = [
    # Deployment
    "exoframe_kit",
    # Sand PMC (Desert Tan)
    "armor_sand_head", "armor_sand_chest", "armor_sand_arms", "armor_sand_legs",
    # Roll Cage (Industrial Yellow)
    "armor_roll_cage",
    # Cerberus Black PMC (Night Ops)
    "armor_cerberus_head", "armor_cerberus_chest", "armor_cerberus_arms", "armor_cerberus_legs",
    # USMC Recon (Olive Drab)
    "armor_usmc_head", "armor_usmc_chest", "armor_usmc_arms", "armor_usmc_legs",
    # VOTOMS Red Shoulder & Camo
    "armor_votoms_head", "armor_red_shoulder_arms", "armor_militia_hood", "armor_militia_chest", "armor_arctic_chest",
    # Utility Backpack Modules
    "module_usmc_comms", "module_cerberus_packs", "module_shoulder_missile",
    # Working Tools
    "tool_mining_drill", "tool_chainsaw",
    # Tactical Weapons
    "exoframe_assault_rifle", "exoframe_sniper_rifle", "exoframe_machine_gun",
    "exoframe_minigun", "exoframe_rocket_launcher", "exoframe_rpg7",
    # Ammunition
    "ammo_20mm", "ammo_rocket", "ammo_762_minigun", "ammo_rpg_warhead",
    # Components
    "hydraulic_cylinder", "servo_motor", "reinforced_steel_plate", "peddler_core"
]

def gen_item_icon(name):
    def pixel(x, y):
        border = (x == 0 or x == 15 or y == 0 or y == 15)
        if border: return (0, 0, 0, 0)

        # Sniper AMR
        if name == "exoframe_sniper_rifle":
            if 1 <= x <= 14 and 7 <= y <= 8: return (35, 38, 44, 255) # Long barrel
            if 5 <= x <= 9 and 5 <= y <= 6: return (30, 180, 255, 255) # Scope
            if 7 <= x <= 10 and 9 <= y <= 11: return (82, 100, 58, 255) # Stock
            if 13 <= x <= 14 and 6 <= y <= 9: return (25, 25, 25, 255) # Muzzle brake
            return (0, 0, 0, 0)

        # Minigun M134
        if name == "exoframe_minigun":
            if 3 <= x <= 13 and 6 <= y <= 9:
                if x % 2 == 0: return (55, 60, 68, 255)
                return (35, 38, 42, 255) # 6 rotating barrels
            if 1 <= x <= 4 and 6 <= y <= 10: return (70, 75, 82, 255) # Rotor
            if 2 <= x <= 4 and 10 <= y <= 12: return (20, 20, 20, 255) # Spade grip
            return (0, 0, 0, 0)

        # RPG-7 Heavy
        if name == "exoframe_rpg7":
            if 1 <= x <= 14 and 7 <= y <= 8: return (130, 75, 35, 255) # Wood tube
            if 10 <= x <= 14 and 5 <= y <= 10: return (40, 160, 210, 255) # Big blue demolition warhead
            if 4 <= x <= 5 and 9 <= y <= 11: return (30, 30, 30, 255) # Grip
            return (0, 0, 0, 0)

        # VOTOMS Red Shoulder Arms
        if name == "armor_red_shoulder_arms":
            if 3 <= x <= 7 and 4 <= y <= 11: return (82, 100, 58, 255) # Left green arm
            if 8 <= x <= 13 and 4 <= y <= 11: return (215, 35, 30, 255) # BLOOD RED right shoulder!
            return (0, 0, 0, 0)

        # VOTOMS Head (3-lens turret)
        if name == "armor_votoms_head":
            if 4 <= x <= 11 and 4 <= y <= 11:
                if x == 7 and y == 7: return (0, 255, 120, 255) # Emerald lens
                if x == 9 and y == 6: return (255, 40, 50, 255) # Ruby lens
                if x == 8 and y == 9: return (0, 220, 255, 255) # Cyan lens
                return (85, 105, 65, 255) # Green helmet
            return (0, 0, 0, 0)

        # Shoulder Missile Pod (3x3)
        if name == "module_shoulder_missile":
            if 3 <= x <= 12 and 3 <= y <= 12:
                if x in (5, 8, 11) and y in (5, 8, 11): return (230, 30, 30, 255) # 9 red rockets
                return (65, 78, 52, 255)
            return (0, 0, 0, 0)

        # USMC Comms Module
        if name == "module_usmc_comms":
            if 4 <= x <= 11 and 6 <= y <= 12: return (82, 100, 58, 255)
            if x in (5, 10) and 1 <= y <= 5: return (180, 185, 190, 255) # Antennas
            return (0, 0, 0, 0)

        # Cerberus Tactical Packs
        if name == "module_cerberus_packs":
            if (x in (3, 4, 5, 6) or x in (9, 10, 11, 12)) and 5 <= y <= 12:
                return (50, 60, 45, 255)
            return (0, 0, 0, 0)

        # Militia Hood
        if "militia" in name:
            if 3 <= x <= 12 and 3 <= y <= 12:
                if (x + y) % 3 == 0: return (50, 65, 35, 255)
                return (110, 90, 55, 255) # Camo
            return (0, 0, 0, 0)

        # Cerberus Arms / Legs
        if "cerberus" in name:
            if 3 <= x <= 12 and 3 <= y <= 12:
                if x in (4, 5) and y in (4, 5): return (230, 30, 30, 255)
                return (32, 34, 38, 255)
            return (0, 0, 0, 0)

        # USMC Arms / Legs / Chest / Head
        if "usmc" in name:
            if 3 <= x <= 12 and 3 <= y <= 12:
                if name == "armor_usmc_head" and 7 <= x <= 8 and 7 <= y <= 8: return (240, 240, 245, 255) # Skull
                return (82, 100, 58, 255)
            return (0, 0, 0, 0)

        # Roll cage
        if name == "armor_roll_cage":
            if (x in (2, 13) and 2 <= y <= 13) or (y in (2, 13) and 2 <= x <= 13) or (x in (5, 10) and 2 <= y <= 13):
                return (245, 190, 0, 255)
            if 6 <= x <= 9 and 1 <= y <= 3: return (255, 100, 0, 255)
            return (0, 0, 0, 0)

        # Mining drill
        if name == "tool_mining_drill":
            if 3 <= x <= 7 and 5 <= y <= 10: return (245, 190, 0, 255)
            if 8 <= x <= 14 and 6 <= y <= 9:
                if (x + y) % 2 == 0: return (220, 225, 235, 255)
                return (120, 130, 140, 255)
            return (0, 0, 0, 0)

        # Chainsaw
        if name == "tool_chainsaw":
            if 2 <= x <= 6 and 6 <= y <= 10: return (240, 95, 20, 255)
            if 7 <= x <= 14 and 7 <= y <= 9:
                if x in (7, 14) or y in (7, 9): return (230, 230, 230, 255)
                return (110, 115, 120, 255)
            return (0, 0, 0, 0)

        # Machine gun
        if name == "exoframe_machine_gun":
            if 2 <= x <= 14 and 7 <= y <= 8: return (35, 38, 42, 255)
            if 6 <= x <= 9 and 9 <= y <= 12: return (70, 85, 55, 255)
            return (0, 0, 0, 0)

        # Arctic
        if "arctic" in name:
            if 3 <= x <= 12 and 3 <= y <= 12:
                if (x + y) % 3 == 0: return (180, 185, 190, 255)
                return (235, 240, 245, 255)
            return (0, 0, 0, 0)

        # Sand armor
        if "armor_sand" in name:
            if 3 <= x <= 12 and 3 <= y <= 12:
                if x in (3, 12) or y in (3, 12): return (140, 125, 90, 255)
                return (194, 178, 128, 255)
            return (0, 0, 0, 0)

        # Ammunition
        if name == "ammo_762_minigun":
            if 3 <= x <= 12 and 5 <= y <= 11:
                if x % 2 == 0: return (235, 185, 40, 255) # Brass
                return (40, 42, 45, 255) # Links
            return (0, 0, 0, 0)

        if name == "ammo_rpg_warhead":
            if 5 <= x <= 10 and 3 <= y <= 13: return (40, 160, 210, 255)
            return (0, 0, 0, 0)

        if name == "ammo_20mm":
            if 5 <= x <= 10 and 3 <= y <= 13: return (215, 160, 50, 255)
            return (0, 0, 0, 0)

        if name == "ammo_rocket":
            if 6 <= x <= 9 and 2 <= y <= 13: return (255, 190, 20, 255)
            return (0, 0, 0, 0)

        # Components
        if name == "peddler_core":
            dx = abs(x - 8); dy = abs(y - 8)
            if dx + dy <= 3: return (0, 255, 230, 255)
            elif dx + dy <= 5: return (220, 225, 220, 255)
            return (0, 0, 0, 0)

        if name == "hydraulic_cylinder":
            if 6 <= x <= 9 and 2 <= y <= 13:
                if y <= 5: return (200, 210, 225, 255)
                return (70, 75, 85, 255)
            return (0, 0, 0, 0)

        if name == "servo_motor":
            if 4 <= x <= 11 and 4 <= y <= 11:
                if (x + y) % 3 == 0: return (190, 120, 35, 255)
                return (45, 50, 55, 255)
            return (0, 0, 0, 0)

        if name == "reinforced_steel_plate":
            if 3 <= x <= 12 and 3 <= y <= 12:
                return (120, 128, 140, 255)
            return (0, 0, 0, 0)

        if name == "exoframe_kit":
            if (x in (5, 10) and 3 <= y <= 13) or (y in (4, 8) and 5 <= x <= 10):
                return (160, 170, 180, 255)
            return (0, 0, 0, 0)

        if name == "exoframe_assault_rifle":
            if 2 <= x <= 14 and 7 <= y <= 9: return (35, 38, 42, 255)
            return (0, 0, 0, 0)

        if name == "exoframe_rocket_launcher":
            if 4 <= x <= 12 and 4 <= y <= 11: return (70, 80, 60, 255)
            return (0, 0, 0, 0)

        return (100, 100, 100, 255)
    return pixel

models_item_dir = f"{base_dir}/models/item"
textures_item_dir = f"{base_dir}/textures/item"
os.makedirs(models_item_dir, exist_ok=True)
os.makedirs(textures_item_dir, exist_ok=True)

for it in all_items:
    # Item Texture PNG
    tex_file = f"{textures_item_dir}/{it}.png"
    with open(tex_file, "wb") as f:
        f.write(create_png(16, 16, gen_item_icon(it)))

    # Item Model JSON
    model_file = f"{models_item_dir}/{it}.json"
    model_data = {
        "parent": "minecraft:item/generated",
        "textures": {
            "layer0": f"obsolete:item/{it}"
        }
    }
    with open(model_file, "w") as f:
        json.dump(model_data, f, indent=2)

print(f"Generated {len(all_items)} item textures and models successfully!")
