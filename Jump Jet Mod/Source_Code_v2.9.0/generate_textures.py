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

def generate_base_texture(x, y):
    """Base dyeable layer: Armor plates in neutral metallic shades with shading, bevels, and rivets."""
    # ==========================================
    # 1. MAGE UNIT (Abdomen & Leg Strut)
    # ==========================================
    # Main Abdomen Propulsion Engine Housing: x=0..20, y=16..26
    if 0 <= x < 20 and 16 <= y < 26:
        dx = x - 0
        dy = y - 16
        border = (dx == 0 or dx == 19 or dy == 0 or dy == 9)
        corner_rivet = (dx in (1, 18) and dy in (1, 8))
        if corner_rivet:
            return (240, 240, 245, 255)
        if border:
            return (140, 145, 150, 255)
        lum = 190 + int(15 * (1.0 - dy / 9.0))
        return (lum, lum, lum + 5, 255)

    # Upper Cowl: x=24..42, y=16..20
    if 24 <= x < 42 and 16 <= y < 20:
        dy = y - 16
        lum = 210 - dy * 10
        return (lum, lum, lum + 4, 255)

    # Lower Cowl / Skirt: x=0..18, y=46..51
    if 0 <= x < 18 and 46 <= y < 51:
        dy = y - 46
        lum = 175 + dy * 8
        if dy == 0 or dy == 4:
            lum -= 30
        return (lum, lum, lum + 5, 255)

    # Rear Battery Case: x=40..58, y=0..10
    if 40 <= x < 58 and 0 <= y < 10:
        dy = y - 0
        dx = x - 40
        if dx == 0 or dx == 17 or dy == 0 or dy == 9:
            return (130, 135, 140, 255)
        lum = 170 + int(10 * ((dx + dy) % 3))
        return (lum, lum, lum + 3, 255)

    # Right Leg Hip Bracket: x=64..74, y=0..5
    if 64 <= x < 74 and 0 <= y < 5:
        return (180, 180, 185, 255)

    # Knee Joint Disc: x=64..74, y=15..20
    if 64 <= x < 74 and 15 <= y < 20:
        return (200, 200, 205, 255)

    # Foot Ski Runner: x=76..102, y=0..9
    if 76 <= x < 102 and 0 <= y < 9:
        dx = x - 76
        dy = y - 0
        if dx in (0, 25) or dy in (0, 8):
            return (130, 130, 135, 255)
        if (dx % 3 == 0):
            return (170, 175, 180, 255)
        return (195, 200, 205, 255)

    # Upturned Ski Tip: x=76..88, y=10..14
    if 76 <= x < 88 and 10 <= y < 14:
        dy = y - 10
        lum = 220 - dy * 12
        return (lum, lum, lum + 5, 255)

    # ==========================================
    # 2. CONVENTIONAL BACK JETPACK (y=64..80, x=0..64)
    # ==========================================
    # Dual Turbine Cylinders (left & right)
    if 0 <= x < 32 and 64 <= y < 80:
        dx = x % 16
        dy = y - 64
        # Cylinder shading curve
        curve = abs(dx - 7.5) / 7.5
        lum = int(210 - curve * 60)
        if dy in (0, 15):
            lum -= 40
        return (lum, lum, lum + 4, 255)

    # Center Manifold / Frame
    if 32 <= x < 48 and 64 <= y < 76:
        dx = x - 32
        dy = y - 64
        lum = 170 + int(15 * (1.0 - dy / 12.0))
        if dx in (0, 15) or dy in (0, 11):
            lum -= 30
        return (lum, lum, lum + 2, 255)

    # Exhaust Bells
    if 48 <= x < 64 and 64 <= y < 76:
        dx = x - 48
        dy = y - 64
        lum = 150 + dy * 5
        return (lum, lum, lum + 8, 255)

    # ==========================================
    # 3. TACTICAL WINGS (y=64..95, x=64..128)
    # ==========================================
    # Center Avionics Pack
    if 64 <= x < 80 and 64 <= y < 76:
        dx = x - 64
        dy = y - 64
        lum = 185 - dy * 3
        return (lum, lum, lum + 5, 255)

    # Delta Wing Blades (swept aerodynamic panels)
    if 64 <= x < 96 and 76 <= y < 92:
        dx = x - 64
        dy = y - 76
        # Aerodynamic panel lines
        if dx % 8 == 0 or dy % 4 == 0:
            return (130, 135, 140, 255)
        lum = 195 - int(dy * 2.5)
        return (lum, lum, lum + 6, 255)

    # Wingtip Jet Pods
    if 96 <= x < 120 and 64 <= y < 78:
        dx = (x - 96) % 12
        dy = y - 64
        lum = 190 - int(abs(dx - 5.5) * 6)
        return (lum, lum, lum + 5, 255)

    # ==========================================
    # 4. HEAVY INDUSTRIAL ROCKET (y=96..128, x=0..96)
    # ==========================================
    # Massive Fuel Rockets (Dual Heavy Cylinders)
    if 0 <= x < 60 and 96 <= y < 128:
        dx = (x % 30)
        dy = y - 96
        curve = abs(dx - 14.5) / 14.5
        lum = int(215 - curve * 70)
        # Heavy reinforcing bands
        if dy in (4, 5, 16, 17, 27, 28):
            lum = max(50, lum - 55)
        return (lum, lum, lum + 2, 255)

    # Heavy Blast Nozzles
    if 60 <= x < 90 and 96 <= y < 120:
        dy = y - 96
        lum = 140 + dy * 4
        return (lum, lum, lum + 5, 255)

    return (0, 0, 0, 0)

def generate_overlay_texture(x, y):
    """Emissive and fixed material overlay: brass, cyan/orange mana core, leather harness, exhaust flares."""
    # ==========================================
    # 1. MAGE UNIT OVERLAY
    # ==========================================
    # Harness Straps: x=0..24, y=0..15
    if 0 <= x < 24 and 0 <= y < 15:
        dx = x - 0
        dy = y - 0
        if (dx in (10, 11, 12) and dy in (6, 7)):
            return (218, 165, 32, 255) # Gold buckle
        is_strap = (dy in (2, 3, 4, 10, 11) or dx in (2, 3, 20, 21))
        if is_strap:
            leather_c = 60 + ((dx + dy) % 3) * 8
            return (leather_c + 20, leather_c + 5, leather_c, 255)
        return (0, 0, 0, 0)

    # Intake Scoops: x=42..50, y=16..24
    if 42 <= x < 50 and 16 <= y < 24:
        dx = (x - 42) % 4
        dy = (y - 16) % 4
        if dx == 1 and dy == 1:
            return (20, 25, 35, 255)
        return (90, 100, 115, 255)

    # Cooling Radiators: x=0..8, y=27..45
    if 0 <= x < 8 and 27 <= y < 45:
        dy = y % 2
        return (30, 35, 45, 255) if dy == 0 else (160, 170, 185, 255)

    # Brass Bezel Ring: x=24..34, y=26..31
    if 24 <= x < 34 and 26 <= y < 31:
        dx = x - 24
        dy = y - 26
        if (dx in (1, 8) and dy in (1, 4)):
            return (255, 220, 110, 255)
        if dx == 0 or dx == 9 or dy == 0 or dy == 4:
            return (160, 120, 35, 255)
        return (218, 165, 32, 255)

    # Glowing Radiant Mana Crystal Core: x=36..44, y=26..30
    if 36 <= x < 44 and 26 <= y < 30:
        dx = x - 36
        dy = y - 26
        if 2 <= dx <= 5 and 1 <= dy <= 2:
            return (230, 255, 255, 255)
        if dx == 0 or dx == 7 or dy == 0 or dy == 3:
            return (0, 160, 200, 255)
        return (0, 240, 255, 255)

    # Underside Nozzles: x=20..36, y=46..49
    if 20 <= x < 36 and 46 <= y < 49:
        dx = (x - 20) % 8
        if dx in (2, 3):
            return (0, 220, 255, 255)
        return (50, 55, 65, 255)

    # Thigh Hydraulic Girders: x=64..74, y=6..11
    if 64 <= x < 74 and 6 <= y < 11:
        dx = x % 3
        return (245, 250, 255, 255) if dx == 1 else (120, 130, 140, 255)

    # Rear Heel Thruster: x=76..88, y=15..20
    if 76 <= x < 88 and 15 <= y < 20:
        dx = x - 76
        dy = y - 15
        if 4 <= dx <= 7 and 2 <= dy <= 3:
            return (0, 230, 255, 255)
        if dx in (0, 11) or dy in (0, 4):
            return (60, 65, 80, 255)
        return (100, 115, 135, 255)

    # ==========================================
    # 2. BACK JETPACK OVERLAY (y=64..80)
    # ==========================================
    # Jetpack Exhaust Bells (Active Cyan Plasma Flare inside nozzles)
    if 48 <= x < 64 and 64 <= y < 76:
        dx = (x - 48) % 8
        dy = y - 64
        if 2 <= dx <= 5 and 6 <= dy <= 9:
            return (0, 245, 255, 255) # Blazing Cyan Thrust Core
        if dx in (0, 7) or dy in (0, 11):
            return (70, 75, 85, 255)
        return (110, 120, 135, 255)

    # Chrome High-Pressure Fuel Tubes on Manifold
    if 32 <= x < 48 and 64 <= y < 76:
        dx = x - 32
        if dx in (4, 11):
            return (240, 245, 250, 255) # Polished chrome pipe
        if dx in (7, 8):
            return (218, 165, 32, 255) # Golden brass central regulator

    # ==========================================
    # 3. TACTICAL WINGS OVERLAY (y=64..95)
    # ==========================================
    # Wingtip Glowing Pods
    if 96 <= x < 120 and 64 <= y < 78:
        dx = (x - 96) % 12
        dy = y - 64
        if 4 <= dx <= 7 and 8 <= dy <= 12:
            return (0, 255, 230, 255) # Emissive wingtip plasma beacon
        return (50, 55, 65, 255)

    # Carbon Fiber Weave Pattern on Delta Wings
    if 64 <= x < 96 and 76 <= y < 92:
        dx = x - 64
        dy = y - 76
        if (dx + dy) % 2 == 0:
            return (40, 42, 48, 255)
        return (28, 30, 34, 255)

    # ==========================================
    # 4. HEAVY INDUSTRIAL ROCKET OVERLAY (y=96..128)
    # ==========================================
    # Warning Hazard Stripes on Heavy Rocket Tanks
    if 0 <= x < 60 and 96 <= y < 128:
        dx = x % 30
        dy = y - 96
        # Diagonal hazard stripe band at upper third
        if 8 <= dy <= 14:
            if (dx + dy) % 6 < 3:
                return (245, 195, 20, 255) # Hazard Yellow
            else:
                return (25, 25, 30, 255)   # Hazard Black
        # Pressure Gauge Dial
        if 18 <= dy <= 22 and 12 <= dx <= 16:
            return (255, 255, 255, 255) # White pressure gauge

    # Fiery Orange Rocket Exhaust Flare inside Heavy Nozzles
    if 60 <= x < 90 and 96 <= y < 120:
        dx = (x - 60) % 15
        dy = y - 96
        if 4 <= dx <= 10 and 12 <= dy <= 18:
            return (255, 120, 0, 255) # Blazing Orange Rocket Flame
        if 6 <= dx <= 8 and 14 <= dy <= 16:
            return (255, 240, 100, 255) # Yellow-white core fire
        return (80, 75, 70, 255)

    return (0, 0, 0, 0)

def main():
    target_dir = r"C:\Users\Purachai\source\repos\YoujoSenkiFlightUnit\src\main\resources\assets\youjosenki\textures\models\armor"
    os.makedirs(target_dir, exist_ok=True)

    base_path = os.path.join(target_dir, "elenium_flight_unit.png")
    overlay_path = os.path.join(target_dir, "elenium_flight_unit_overlay.png")

    print("Generating 128x128 elenium_flight_unit.png with all 4 model visual designs...")
    base_png = create_png(128, 128, generate_base_texture)
    with open(base_path, "wb") as f:
        f.write(base_png)
    print(f"Wrote {len(base_png)} bytes to {base_path}")

    print("Generating 128x128 elenium_flight_unit_overlay.png with glowing thrusters & hazard stripes...")
    overlay_png = create_png(128, 128, generate_overlay_texture)
    with open(overlay_path, "wb") as f:
        f.write(overlay_png)
    print(f"Wrote {len(overlay_png)} bytes to {overlay_path}")

if __name__ == "__main__":
    main()
