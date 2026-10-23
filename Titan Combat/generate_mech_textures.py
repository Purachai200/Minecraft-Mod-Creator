import struct
import zlib
import os

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

def gen_base_texture(x, y):
    # Base metallic gunmetal armor with panel seams & bevels
    grid = (x % 8 == 0 or y % 8 == 0)
    rivet = (x % 8 in (1, 7) and y % 8 in (1, 7))
    
    # Hydraulic / Mechanical regions
    if y >= 96: # Legs
        base = 50 + (x * 7 + y * 13) % 15
        if grid: return (35, 38, 42, 255)
        if rivet: return (160, 165, 170, 255)
        return (base, base + 2, base + 5, 255)
    elif y >= 64: # Arms / Cannons
        base = 60 + (x * 11 + y * 5) % 12
        if grid: return (40, 42, 46, 255)
        return (base, base + 3, base + 6, 255)
    else: # Torso & Cockpit
        base = 55 + (x * 3 + y * 7) % 18
        if grid: return (38, 40, 44, 255)
        if rivet: return (170, 175, 180, 255)
        return (base, base + 4, base + 8, 255)

def gen_paint_layer(x, y):
    # Faction paint stripes: chest chevron, shoulder stripes, knee armor
    # Transparent everywhere except decorative armor panels
    # Shoulder stripes: x=4..12, y=66..72 or mirrored
    is_shoulder = (4 <= (x % 32) <= 12 and 66 <= y <= 72)
    # Chest stripe: x=14..24, y=6..16
    is_chest = (10 <= x <= 22 and 8 <= y <= 16)
    # Leg guard stripe: y=100..106
    is_leg = (6 <= (x % 24) <= 18 and 100 <= y <= 106)
    
    if is_shoulder or is_chest or is_leg:
        # High-brightness white/light-gray so dynamic color tint applies vividly
        lum = 230 + (x + y) % 20
        return (lum, lum, lum, 255)
    return (0, 0, 0, 0)

def gen_glow_layer(x, y):
    # Visor slit: x=76..88, y=22..27
    is_visor = (76 <= x <= 88 and 22 <= y <= 27)
    # Thruster nozzles: x=70..90, y=42..48
    is_thruster = (70 <= x <= 90 and 42 <= y <= 48)
    
    if is_visor or is_thruster:
        return (255, 255, 255, 255)
    return (0, 0, 0, 0)

def gen_beacon_item(x, y):
    # 16x16 Titan Drop Beacon item
    # Antenna stick: x=7..8, y=1..7
    # Base transmitter box: x=4..11, y=8..14
    # Blinking LED on top: x=7..8, y=1..2
    if 7 <= x <= 8 and 1 <= y <= 2:
        return (0, 240, 255, 255) # Cyan signal LED
    if 7 <= x <= 8 and 3 <= y <= 7:
        return (180, 185, 190, 255) # Metal antenna
    if 4 <= x <= 11 and 8 <= y <= 14:
        if x in (4, 11) or y in (8, 14):
            return (40, 45, 50, 255) # Dark bezel
        if 7 <= x <= 8 and 10 <= y <= 11:
            return (255, 60, 60, 255) # Red arming button
        return (90, 95, 100, 255) # Military casing
    return (0, 0, 0, 0)

def gen_spray_can_item(x, y):
    # 16x16 Spray Can item
    # Nozzle: x=7..9, y=2..4
    # Can body: x=5..11, y=5..14
    if 7 <= x <= 8 and y == 2:
        return (255, 255, 255, 255) # White nozzle button
    if 7 <= x <= 8 and 3 <= y <= 4:
        return (140, 140, 140, 255)
    if 5 <= x <= 11 and 5 <= y <= 14:
        if x in (5, 11) or y in (5, 14):
            return (35, 38, 42, 255)
        # Faction color band in center of can
        if 8 <= y <= 11:
            return (30, 120, 255, 255) # Blue faction stripe
        return (180, 185, 190, 255)
    return (0, 0, 0, 0)

out_dir = r"C:\Users\Purachai\Desktop\Mod Minecraft Creator\Titan Combat\src\main\resources\assets\titancombat\textures"
mech_dir = os.path.join(out_dir, "entity", "mech")
item_dir = os.path.join(out_dir, "item")
os.makedirs(mech_dir, exist_ok=True)
os.makedirs(item_dir, exist_ok=True)

with open(os.path.join(mech_dir, "aegis_striker.png"), "wb") as f:
    f.write(create_png(128, 128, gen_base_texture))
with open(os.path.join(mech_dir, "aegis_striker_paint.png"), "wb") as f:
    f.write(create_png(128, 128, gen_paint_layer))
with open(os.path.join(mech_dir, "aegis_striker_glow.png"), "wb") as f:
    f.write(create_png(128, 128, gen_glow_layer))

with open(os.path.join(item_dir, "titan_drop_beacon.png"), "wb") as f:
    f.write(create_png(16, 16, gen_beacon_item))
with open(os.path.join(item_dir, "paint_spray_can.png"), "wb") as f:
    f.write(create_png(16, 16, gen_spray_can_item))

print("Textures generated successfully!")
