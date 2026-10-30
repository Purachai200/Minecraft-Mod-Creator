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

def gen_module_icon(name):
    def pixel(x, y):
        # 1. Geological Scanner: Circular radar scanner with cyan display & gold nodes
        if name == "module_geological_scanner":
            dx = x - 7.5
            dy = y - 7.5
            dist = (dx*dx + dy*dy) ** 0.5
            if dist > 6.8:
                return (0, 0, 0, 0)
            if dist > 5.5:
                return (50, 56, 64, 255) # Outer ring
            if dist <= 1.5:
                return (0, 240, 255, 255) # Center glowing core
            if abs(dx) < 0.6 or abs(dy) < 0.6:
                return (0, 200, 230, 255) # Cross reticle
            if (x in (4, 11) and y in (4, 11)):
                return (255, 200, 40, 255) # Sensor nodes
            return (15, 30, 45, 255) # Dark radar background

        # 2. Night Vision Optic: Dual night-vision / FLIR thermal lenses
        if name == "module_night_vision_optic":
            if 3 <= y <= 6 and 2 <= x <= 13:
                return (45, 50, 55, 255) # Upper helmet mount bracket
            # Left lens center (5, 10), Right lens center (10, 10)
            d1 = ((x - 5)**2 + (y - 10)**2)**0.5
            d2 = ((x - 10)**2 + (y - 10)**2)**0.5
            if d1 <= 1.2 or d2 <= 1.2:
                return (0, 255, 120, 255) # Glowing emerald NVG phosphor
            if d1 <= 2.6 or d2 <= 2.6:
                return (0, 160, 80, 255) # Mid lens reflection
            if d1 <= 3.6 or d2 <= 3.6:
                return (30, 32, 36, 255) # Lens barrel housing
            return (0, 0, 0, 0)

        # 3. Cargo Crate: Reinforced military freight container
        if name == "module_cargo_crate":
            if 2 <= x <= 13 and 3 <= y <= 13:
                # Hazard stripes or corrugated ridges
                if x in (2, 13) or y in (3, 13):
                    return (55, 60, 50, 255) # Reinforced steel border
                if (x + y) % 4 == 0:
                    return (180, 150, 40, 255) # Hazard stripe yellow
                if (x + y) % 4 == 1:
                    return (35, 40, 32, 255) # Hazard stripe black/dark olive
                return (90, 105, 75, 255) # Olive drab hull
            return (0, 0, 0, 0)

        # 4. Agri Hopper: Industrial seed hopper with soil probe
        if name == "module_agri_hopper":
            # Hopper funnel: wide at top (y=2..5, x=3..12), narrowing at bottom (y=6..10, x=5..10)
            if 2 <= y <= 5 and 3 <= x <= 12:
                if y == 2 or x in (3, 12): return (60, 70, 50, 255)
                return (120, 140, 90, 255) # Light olive hopper
            if 6 <= y <= 9 and 5 <= x <= 10:
                if x == 7 or x == 8: return (220, 180, 50, 255) # Seed gauge window
                return (85, 95, 70, 255)
            # Soil probe needle at bottom (x=7,8, y=10..14)
            if 10 <= y <= 14 and (x == 7 or x == 8):
                if y >= 13: return (220, 230, 240, 255) # Sharp steel tip
                return (140, 150, 160, 255) # Chrome probe
            return (0, 0, 0, 0)

        # 5. Diving Ballast: Twin navy submersible tanks + depth gauge
        if name == "module_diving_ballast":
            # Left tank (x=3..6, y=3..13), Right tank (x=9..12, y=3..13)
            in_t1 = (3 <= x <= 6 and 4 <= y <= 13)
            in_t2 = (9 <= x <= 12 and 4 <= y <= 13)
            if in_t1 or in_t2:
                if y == 4 or y == 13: return (180, 190, 205, 255) # End caps
                if x in (4, 10): return (40, 90, 150, 255) # Deep navy blue body
                return (25, 60, 100, 255) # Shading
            # Top valves
            if (x in (4, 10) and y == 3) or (7 <= x <= 8 and y == 7):
                return (210, 180, 60, 255) # Brass valve
            # Center pressure gauge dial (x=7..8, y=8..10)
            if 7 <= x <= 8 and 8 <= y <= 10:
                return (0, 240, 255, 255) # Cyan backlit gauge
            return (0, 0, 0, 0)

        # 6. Targeting Computer: High-tech FCS computer processor
        if name == "module_targeting_computer":
            if 3 <= x <= 12 and 3 <= y <= 12:
                if x in (3, 12) or y in (3, 12):
                    return (50, 55, 65, 255) # Steel chassis
                # Center HUD display reticle
                if x == 7 or x == 8 or y == 7 or y == 8:
                    return (0, 220, 255, 255) # Glowing cyan FCS crosshair
                return (15, 20, 30, 255) # Screen panel
            if (x in (2, 13) and y in (5, 10)) or (y in (2, 13) and x in (5, 10)):
                return (230, 180, 40, 255) # Gold connector pins
            return (0, 0, 0, 0)

        # 7. Cultivator Plow: Heavy 3-tine mechanized hydraulic agricultural plow
        if name == "tool_cultivator_plow":
            # Main mounting beam (y=2..5, x=4..11)
            if 2 <= y <= 4 and 4 <= x <= 11:
                return (70, 75, 85, 255) # Heavy frame steel
            # Center hydraulic cylinder (x=7..8, y=5..8)
            if 5 <= y <= 8 and (x == 7 or x == 8):
                if y <= 6: return (220, 230, 245, 255) # Chrome piston rod
                return (190, 120, 30, 255) # Hydraulic bronze body
            # 3 plow tines (left x=3..5, center x=7..9, right x=11..13)
            # Swept back downward (y=8..14)
            for cx in (4, 8, 12):
                if cx - 1 <= x <= cx + 1:
                    if y == 9: return (80, 85, 95, 255)
                    if y == 10: return (140, 150, 165, 255)
                    if y == 11 and x >= cx: return (190, 200, 215, 255)
                    if y == 12 and x >= cx: return (220, 230, 245, 255)
                    if y == 13 and x == cx + 1: return (255, 255, 255, 255) # Sharp plowshare point
            return (0, 0, 0, 0)

        return (0, 0, 0, 0)
    return pixel

base_dir = "Obsolete/src/main/resources/assets/obsolete"
models_item_dir = f"{base_dir}/models/item"
textures_item_dir = f"{base_dir}/textures/item"
os.makedirs(models_item_dir, exist_ok=True)
os.makedirs(textures_item_dir, exist_ok=True)

new_items = [
    "module_geological_scanner",
    "module_night_vision_optic",
    "module_cargo_crate",
    "module_agri_hopper",
    "module_diving_ballast",
    "module_targeting_computer",
    "tool_cultivator_plow"
]

for item in new_items:
    tex_path = f"{textures_item_dir}/{item}.png"
    with open(tex_path, "wb") as f:
        f.write(create_png(16, 16, gen_module_icon(item)))

    model_path = f"{models_item_dir}/{item}.json"
    model_data = {
        "parent": "minecraft:item/generated",
        "textures": {
            "layer0": f"obsolete:item/{item}"
        }
    }
    with open(model_path, "w") as f:
        json.dump(model_data, f, indent=2)

print(f"Generated {len(new_items)} new module textures and model JSONs!")
