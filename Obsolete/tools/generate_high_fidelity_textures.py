"""
Master High-Fidelity 512x512 Texture Synthesizer for OBSOLETE Mecha Mod.
Generates all 7 anime-accurate faction textures with:
- Heavy hydraulic chrome pistons and brass fittings
- Recessed panel lines, 3D beveled armor edges, and hex rivets
- Micro-textured rolled homogeneous armor with authentic multi-octave noise
- Faction decals: USMC stencil skull & lettering, Cerberus red #1 flash, VOTOMS 3-lens turret
- Realistic weapon finishes: Parkerized steel, heat-blued barrels, brass ammo belts, varnished wood
- 7 Camo Schemes: Factory/Sand, Woodland MARPAT, Desert Nomad, Urban Hex, Arctic Blizzard, Tigerstripe, Industrial Hazard
"""
import struct
import zlib
import os
import math
import json

def create_png(width, height, pixel_buffer):
    """Encodes a flat RGBA bytearray of width*height*4 into a valid PNG byte string."""
    raw = bytearray()
    row_bytes = width * 4
    for y in range(height):
        raw.append(0) # Filter type 0 (None)
        start = y * row_bytes
        raw.extend(pixel_buffer[start:start + row_bytes])

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(bytes(raw), level=6))
    iend = chunk(b'IEND', b'')
    return header + ihdr + idat + iend

# ----------------- Math & Noise Utilities -----------------
def h2(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2246822519) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return (n ^ (n >> 16)) / 0xffffffff

def vnoise(x, y, scale, s=0):
    gx, gy = x / scale, y / scale
    x0, y0 = int(gx), int(gy)
    fx, fy = gx - x0, gy - y0
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    a, b = h2(x0, y0, s), h2(x0 + 1, y0, s)
    c, d = h2(x0, y0 + 1, s), h2(x0 + 1, y0 + 1, s)
    top = a + (b - a) * fx
    bot = c + (d - c) * fx
    return top + (bot - top) * fy

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def rgb(r, g, b, a=255):
    return (clamp(r), clamp(g), clamp(b), clamp(a))

def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (
        clamp(c1[0] + (c2[0] - c1[0]) * t),
        clamp(c1[1] + (c2[1] - c1[1]) * t),
        clamp(c1[2] + (c2[2] - c1[2]) * t),
        255
    )

def mul(c, f):
    return (clamp(c[0] * f), clamp(c[1] * f), clamp(c[2] * f), 255)

def polar_splinter(x, y):
    """Authentic geometric splinter pattern (30-degree rotation, 24px triangular cells)."""
    u = x * 0.866 - y * 0.5
    v = x * 0.5 + y * 0.866
    gu = int(u // 24)
    gv = int(v // 24)
    fu = (u % 24) / 24.0
    fv = (v % 24) / 24.0
    triangle = 1 if (fu + fv > 1.0) else 0
    cell_id = (gu * 73856093 ^ gv * 19349663 ^ (triangle * 83492791)) & 0xffff
    val = cell_id % 3
    if val == 0:
        return (242, 245, 248) # Snow white
    elif val == 1:
        return (170, 180, 190) # Glacial slate grey
    else:
        return (72, 80, 90)     # Dark basalt charcoal

# ----------------- Pixel Stencils -----------------
SKULL_PIXELS = {
    (0, -4): 1, (1, -4): 1, (-1, -4): 1, (2, -4): 1, (-2, -4): 1,
    (0, -3): 1, (1, -3): 1, (-1, -3): 1, (2, -3): 1, (-2, -3): 1, (3, -3): 1, (-3, -3): 1,
    (0, -2): 1, (1, -2): 1, (-1, -2): 1, # Eye cavities leave holes at (+/-2, -2)
    (0, -1): 1, # Nose cavity leaves holes at (+/-1, -1)
    (0, 0): 1, (1, 0): 1, (-1, 0): 1,
    (0, 1): 1, (1, 1): 1, (-1, 1): 1, (2, 1): 1, (-2, 1): 1,
    (1, 2): 1, (-1, 2): 1, (2, 2): 1, (-2, 2): 1, # Teeth
}

# ----------------- Manifest & Map Builders -----------------
MANIFEST_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "packed_armor_uvs.json"))
PACKED_MANIFEST = []
if os.path.exists(MANIFEST_PATH):
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        PACKED_MANIFEST = json.load(f)

BONE_MAP = {}
DETAIL_MAP = {}
MARKING_MAP = {}

FRAME_MAP = {}   # (x, y) -> (material, face, x0, y0, x1, y1, bone): bare-frame cubes, painted per face by material

for item in PACKED_MANIFEST:
    fac = item.get("faction", "")
    bone = item["bone"]
    cidx = item.get("cube_index", 0)
    faces = item["faces"]
    if fac == "Frame":
        for fname, (x0, y0, x1, y1) in faces.items():
            for py in range(y0, y1):
                for px in range(x0, x1):
                    FRAME_MAP[(px, py)] = (item["material"], fname, x0, y0, x1, y1, bone)
        continue
    for fname, (x0, y0, x1, y1) in faces.items():
        fw, fh = x1 - x0, y1 - y0
        if fw <= 0 or fh <= 0: continue
        for py in range(y0, y1):
            for px in range(x0, x1):
                BONE_MAP[(px, py)] = (fac, bone, cidx, fname)
                is_edge = (px == x0 or px == x1 - 1 or py == y0 or py == y1 - 1)
                is_inset = (px == x0 + 1 or px == x1 - 2 or py == y0 + 1 or py == y1 - 2)
                is_corner = (px in (x0 + 1, x1 - 2) and py in (y0 + 1, y1 - 2))
                if is_edge:
                    DETAIL_MAP[(px, py)] = 1 # Seam
                elif is_corner and fw >= 4 and fh >= 4:
                    DETAIL_MAP[(px, py)] = 3 # Hex bolt
                elif is_inset and fw >= 4 and fh >= 4:
                    DETAIL_MAP[(px, py)] = 2 # Bevel highlight

        # ---------------- Markings & Decals ----------------
        # 1. Pegaso Black Dome: White "1" on front crown only
        if bone == "armor_head_dome" and fname == "north" and cidx == 6 and fw >= 4 and fh >= 2:
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            for (dx, dy) in [(0, -1), (-1, -1), (0, 0), (0, 1), (-1, 1), (1, 1)]:
                MARKING_MAP[(cx + dx, cy + dy)] = (255, 255, 255, 255)

        if bone == "canopy_cerberus" and fname == "north" and cidx == 43 and fw >= 4:
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            for (dx, dy) in [(0, -1), (-1, -1), (0, 0), (0, 1), (-1, 1), (1, 1)]:
                MARKING_MAP[(cx + dx, cy + dy)] = (255, 255, 255, 255)

        # 2. Pegaso Red Shoulder Pods: White "1" on outer lateral faces
        if bone in ("armor_left_shoulder_cerberus", "armor_right_shoulder_cerberus"):
            outer_face = "west" if bone == "armor_left_shoulder_cerberus" else "east"
            if fname == outer_face:
                if cidx == 0 and fw >= 5 and fh >= 4:
                    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                    for (dx, dy) in [(0, -2), (-1, -1), (0, -1), (0, 0), (0, 1), (-1, 2), (0, 2), (1, 2)]:
                        MARKING_MAP[(cx + dx, cy + dy)] = (255, 255, 255, 255)
                elif cidx == 6 and fw >= 2 and fh >= 2:
                    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                    for (dx, dy) in [(0, -1), (0, 0), (0, 1), (-1, -1)]:
                        if x0 <= cx + dx < x1 and y0 <= cy + dy < y1:
                            MARKING_MAP[(cx + dx, cy + dy)] = (255, 255, 255, 255)

        # 3. Marine Raider Stencil: USMC canopy rear wall & helmet top & chest
        if bone == "canopy_usmc" and fname == "south" and fw >= 7 and fh >= 9:
            cx, cy = (x0 + x1) // 2, y0 + 5
            for (dx, dy), _ in SKULL_PIXELS.items():
                if x0 <= cx + dx < x1 and y0 <= cy + dy < y1:
                    MARKING_MAP[(cx + dx, cy + dy)] = (245, 248, 250, 255)
            # Stencil "USMC" letters below skull
            ty = y0 + 10
            for lx, ly in [(cx-3, ty), (cx-3, ty+1), (cx-3, ty+2), (cx-2, ty+2), (cx-1, ty+2), (cx-1, ty+1), (cx-1, ty),  # U
                           (cx+1, ty), (cx+1, ty+1), (cx+1, ty+2), (cx+2, ty+1), (cx+3, ty), (cx+3, ty+1), (cx+3, ty+2)]:  # M
                if x0 <= lx < x1 and y0 <= ly < y1:
                    MARKING_MAP[(lx, ly)] = (245, 248, 250, 255)

        if bone == "armor_head_usmc" and fname == "top" and fw >= 5 and fh >= 5:
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            for (dx, dy), _ in SKULL_PIXELS.items():
                if abs(dx) <= 2 and abs(dy) <= 2:
                    MARKING_MAP[(cx + dx, cy + dy)] = (245, 248, 250, 255)

        if bone in ("armor_left_shoulder_usmc", "armor_right_shoulder_usmc"):
            outer_face = "west" if "left" in bone else "east"
            if fname == outer_face and fw >= 5 and fh >= 4:
                cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                # Raider chevron stencil
                for (dx, dy) in [(0, -1), (-1, 0), (1, 0), (-2, 1), (2, 1)]:
                    MARKING_MAP[(cx + dx, cy + dy)] = (240, 245, 248, 255)

        # 4. Polar Front skis: hazard stripes on front tips
        if bone in ("armor_left_ski", "armor_right_ski") and fname == "north":
            for py in range(y0, y1):
                for px in range(x0, x1):
                    if (px + py) % 2 == 0:
                        MARKING_MAP[(px, py)] = (255, 215, 0, 255)
                    else:
                        MARKING_MAP[(px, py)] = (20, 20, 22, 255)

        # 5. Tactical Police: POLICE lettering on chest & shield
        if bone == "armor_chest_police" and fname == "north" and fw >= 8 and fh >= 6:
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            for (dx, dy) in [(-6, 0), (-6, 1), (-6, 2), (-5, 0), (-5, 1),
                             (-3, 0), (-3, 1), (-3, 2), (-2, 0), (-2, 2), (-1, 0), (-1, 1), (-1, 2),
                             (1, 0), (1, 1), (1, 2), (2, 2),
                             (4, 0), (4, 1), (4, 2),
                             (6, 0), (6, 1), (6, 2)]:
                if x0 <= cx + dx < x1 and y0 <= cy + dy < y1:
                    MARKING_MAP[(cx + dx, cy + dy)] = (245, 248, 252, 255)

        if bone == "weapon_riot_shield" and fname == "north" and fw >= 8 and fh >= 6:
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            for (dx, dy) in [(-4, 0), (-4, 1), (-4, 2), (-3, 0), (-3, 1),
                             (-1, 0), (-1, 1), (-1, 2), (0, 0), (0, 2), (1, 0), (1, 1), (1, 2),
                             (3, 0), (3, 1), (3, 2), (4, 2)]:
                if x0 <= cx + dx < x1 and y0 <= cy + dy < y1:
                    MARKING_MAP[(cx + dx, cy + dy)] = (255, 255, 255, 255)

        # 6. Disaster Rescue: Diagonal safety chevron stripes
        if bone == "armor_chest_rescue" and fname == "north":
            for py in range(y0, y1):
                for px in range(x0, x1):
                    if (px + py) // 4 % 2 == 0:
                        MARKING_MAP[(px, py)] = (245, 248, 252, 255)


def faction_livery(x, y):
    """Factory colours mapped per bone from packed manifest, with block fallbacks."""
    if (x, y) in BONE_MAP:
        fac, bone, cidx, _ = BONE_MAP[(x, y)]
        if fac == "Cerberus":
            if bone == "armor_head_dome":
                if cidx == 6: return (255, 30, 42) # Glowing Crimson Mono-eye
                if cidx == 5: return (18, 20, 22)  # Deep shadow visor backing
            if "shoulder_cerberus" in bone:
                if cidx == 0: return (185, 32, 30) # Crimson red top flash accent
                return (42, 44, 48)                 # Matte charcoal pauldron
            if "backpack_cerberus" in bone: return (55, 62, 50)
            if "chest" in bone and cidx in (2, 3, 4, 5):
                return (24, 25, 28)                 # Dark corrugated bellows
            return (40, 42, 46)                     # Pegaso Black main plates
        elif fac == "USMC":
            return (78, 88, 58)                                 # Marine Raider olive drab
        elif fac == "Polar":
            return polar_splinter(x, y)                         # Arctic splinter camo
        elif fac == "Outlander":
            return (64, 68, 66)                                 # Outlander Heavy gunmetal
        elif fac == "Sand":
            return (194, 178, 128)                              # Sand PMC
        elif fac == "Salvage":
            if "canopy" in bone or "chest" in bone:
                if (x + y) // 6 % 2 == 0 and cidx == 0:
                    return (255, 204, 0) # Hazard stripe, one panel only
            return (88, 82, 76) # Welded sheet iron
        elif fac == "Shiden":
            return (52, 60, 56) # East-Asian military navy/olive
        elif fac == "Khamsin":
            if "backpack" in bone:
                return (142, 86, 62) # Terracotta vents
            return (186, 154, 108) # Ochre desert dust
        elif fac == "Riverine":
            if "canopy" in bone or "chest" in bone:
                if cidx % 12 == 0:
                    return (235, 185, 30) # Gasket yellow
            return (68, 78, 52) # Duck-boat camo
        elif fac == "Specter":
            if "head" in bone or "backpack" in bone:
                return (48, 42, 58) # Stealth purple sheen
            return (32, 34, 38) # Matte RAM carbon
        elif fac == "Valkyrie":
            if "canopy" in bone or "shoulder" in bone:
                if cidx % 9 == 4:
                    return (218, 175, 45) # Gold trim, sparse (every other cube read as bee stripes)
            return (235, 240, 245) # Royal titanium white
        elif fac == "Police":
            if "canopy" in bone or "head" in bone:
                if cidx in (2, 7): return (20, 140, 240) # Visor tint
                if cidx in (3, 8): return (30, 120, 255) # Blue strobe
                if cidx in (4, 9): return (230, 30, 30) # Red strobe
            return (24, 32, 45) # Tactical police navy blue
        elif fac == "Rescue":
            if "head" in bone and cidx in (2, 4):
                return (255, 250, 220) # Halogen floodlight lens
            if "backpack" in bone:
                if cidx in (0, 1, 2, 3, 4, 5):
                    return (210, 215, 225) # Silver oxygen cylinders
                return (235, 185, 30) # Winch yellow
            if "chest" in bone and cidx == 1:
                return (240, 245, 250) # Medical kit white
            return (255, 102, 0) # High-vis emergency orange
        elif fac == "Amphibious":
            if cidx in (4, 5):
                return (180, 190, 200) # Silver CO2 inflation canisters
            return (240, 160, 20) # Marine pontoon orange-yellow
        elif fac == "Radar":
            if cidx in (3, 4):
                return (218, 175, 45) # Gold phased-array element
            return (48, 52, 56) # Tactical graphite mast
        elif fac == "RoleWeapons":
            if "shield" in bone:
                if cidx == 3: return (40, 180, 240) # Viewport glass
                return (26, 30, 36) # Ballistic polymer black
            if "baton" in bone:
                if cidx in (3, 4, 5, 6): return (0, 220, 255) # High-voltage arc
                return (35, 38, 42)
            if "fishing" in bone:
                if cidx == 1: return (180, 130, 50) # Bronze winch spool
                if cidx == 9: return (225, 40, 35) # Red tackle bobber
                return (42, 46, 52) # Carbon blank rod

    # Fallback by UV block
    if 0 <= x < 250 and 660 <= y < 840: return (24, 32, 45) # Police
    if 250 <= x < 500 and 660 <= y < 840: return (255, 102, 0) # Rescue
    if 500 <= x < 750 and 660 <= y < 840: return (240, 160, 20) # Amphibious
    if 750 <= x < 1000 and 660 <= y < 840: return (48, 52, 56) # Radar
    if 0 <= x < 600 and 840 <= y < 1024: return (35, 38, 42) # Role Weapons
    if 330 <= x < 400 and y < 315:
        if 120 <= y < 170: return (176, 32, 30)
        if 220 <= y < 315: return (70, 82, 50)
        return (40, 42, 46)
    if 260 <= x < 330 and y < 315: return (78, 88, 58)
    if (460 <= x < 512 and y < 315) or (420 <= x < 512 and 315 <= y < 400):   # <512: the new factions own x>=512
        return polar_splinter(x, y)
    if (400 <= x < 460 and 165 <= y < 315) or (340 <= x < 420 and 315 <= y < 400) or (200 <= x < 260 and 240 <= y < 315):
        return (64, 68, 66)
    if 512 <= x < 597 and y < 340: return (88, 82, 76)
    if 597 <= x < 682 and y < 340: return (52, 60, 56)
    if 682 <= x < 767 and y < 340: return (186, 154, 108)
    if 767 <= x < 852 and y < 340: return (68, 78, 52)
    if 852 <= x < 937 and y < 340: return (32, 34, 38)
    if 937 <= x < 1024 and y < 340: return (235, 240, 245)
    return (194, 178, 128)


def camo_base(camo_id, x, y, n_med, n_coarse, default=None):
    """Base paint for camo scheme camo_id (0 = factory livery, or `default` for frame paint)."""
    if camo_id == 1: # USMC Woodland (Authentic 4-color MARPAT)
        bx, by = x // 6, y // 6
        camo_val = (h2(bx, by, 77) * 100)
        if camo_val < 35: base_armor = (74, 94, 52)
        elif camo_val < 60: base_armor = (46, 62, 34)
        elif camo_val < 82: base_armor = (102, 78, 52)
        else: base_armor = (22, 26, 20)

    elif camo_id == 2: # Desert Nomad (3-Color Middle-East Desert)
        dn = math.sin(x * 0.05) * math.cos(y * 0.05) + n_med * 0.6
        if dn > 0.45: base_armor = (168, 142, 102)
        elif dn > -0.15: base_armor = (205, 184, 138)
        else: base_armor = (128, 102, 72)

    elif camo_id == 3: # Cerberus Urban Hex (Stealth Dark Hexagons)
        hex_grid = ((x // 8) + (y // 14) * 2) % 3
        base_val = 32 + hex_grid * 8
        base_armor = (base_val, base_val + 2, base_val + 5)

    elif camo_id == 4: # Arctic Blizzard (Clean Splinter)
        base_armor = polar_splinter(x, y)

    elif camo_id == 5: # Tigerstripe (Jungle Vietnam Brushstrokes)
        stripe = (y + int(math.sin(x * 0.08) * 8)) // 8
        if stripe % 4 == 0: base_armor = (24, 28, 22)
        elif stripe % 4 == 1: base_armor = (56, 82, 42)
        elif stripe % 4 == 2: base_armor = (112, 92, 58)
        else: base_armor = (42, 60, 32)

    elif camo_id == 6: # Industrial Hazard (CAT Safety Yellow & Grime)
        base_armor = (255, 204, 0)
        if n_coarse > 0.65:
            base_armor = mix(base_armor, (60, 50, 30), (n_coarse - 0.65) * 2.0)

    else: # Default 0: faction factory livery
        base_armor = faction_livery(x, y) if default is None else default
    return base_armor


# ---------------- Bare frame (per-face, by material) ----------------
FRAME_PAINT = (88, 94, 70)      # factory frame colour: worn olive drab
DIGITS = {"0": ["111", "101", "101", "101", "111"], "7": ["111", "001", "010", "010", "010"],
          "3": ["111", "001", "011", "001", "111"]}


def paint_frame(x, y, info, camo_id, n_fine, n_med, n_coarse):
    mat, face, x0, y0, x1, y1, bone = info
    fw, fh = x1 - x0, y1 - y0
    lx, ly = x - x0, y - y0
    edge = lx == 0 or ly == 0 or lx == fw - 1 or ly == fh - 1
    near = lx <= 1 or ly <= 1 or lx >= fw - 2 or ly >= fh - 2
    grit = 0.9 + 0.18 * n_fine
    if mat == "paint":
        c = mul(camo_base(camo_id, x, y, n_med, n_coarse, default=FRAME_PAINT), grit)
        if edge and fw >= 4 and fh >= 4 and h2(x, y, 5) < 0.15:
            c = mul((118, 114, 104), grit)                       # chipped edge, bare steel
        if face in ("north", "south", "east", "west") and fh >= 4 and h2(x, 0, 9) < 0.18 and ly > fh // 3:
            c = mix(c, (96, 58, 34), min(0.55, (ly / fh) * 0.7))  # rust run below a weld
        if edge:
            c = mul(c, 0.72)                                     # welded seam
        elif fw >= 5 and fh >= 5 and lx in (1, fw - 2) and ly in (1, fh - 2):
            c = mul(c, 1.35)                                     # bolt head
        if bone == "torso" and face in ("east", "west") and fw >= 9 and fh >= 7:   # tub side stencil "07"
            for i, ch in enumerate("07"):
                gx, gy = lx - (fw // 2 - 3) - i * 4, ly - 1
                if 0 <= gx < 3 and 0 <= gy < 5 and DIGITS[ch][gy][gx] == "1":
                    c = (226, 222, 208)
        return c
    if mat == "steel":
        c = mul((74, 76, 78), grit)
        return mul(c, 1.25) if (ly == 0 or lx == 0) else mul(c, 0.75) if edge else c
    if mat == "dark":
        c = mul((42, 44, 47), grit)
        return mul(c, 0.7) if edge else c
    if mat == "chrome":
        band = abs(lx - fw / 2) < max(1, fw / 4) if face in ("north", "south", "east", "west") else False
        return mul((205, 210, 216) if band else (150, 156, 164), 0.95 + 0.08 * n_fine)
    if mat == "rubber":
        return (18, 18, 20) if (lx + ly) % 3 == 0 else (30, 30, 33)
    if mat == "hazard":
        return (238, 188, 18) if (x + y) // 3 % 2 == 0 else (24, 24, 26)
    if mat == "lamp":
        return (255, 236, 170) if not near else (255, 168, 30)
    if mat == "glass":
        return (40, 140, 110) if not edge else (16, 18, 20)
    if mat == "exhaust":
        c = mix((104, 70, 50), (30, 26, 24), 0.35 + 0.4 * n_med)
        return mul(c, grit)
    if mat == "seat":
        return (64, 52, 40) if (lx + ly) % 6 == 0 else mul((42, 38, 34), grit)
    if mat == "harness":
        return (170, 40, 30) if not edge else (120, 26, 20)
    return mul((60, 62, 66), grit)


def armor_painters():
    """Armor-set modules that define paint(x, y, camo_id, n_fine, n_med, n_coarse) -> rgba or None, with the UV rects they own."""
    import importlib, sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from armor_sets import SET_IDS
    out = []
    for sid in SET_IDS:
        m = importlib.import_module("armor_sets." + sid)
        if hasattr(m, "paint") and getattr(m, "UV_REGION", None):
            out.append((m.paint, m.UV_REGION[1]))
    return out


def generate_texture_buffer(camo_id):
    W, H = 1024, 1024
    painters = armor_painters()
    buf = bytearray(W * H * 4)

    def set_px(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            idx = (y * W + x) * 4
            buf[idx:idx+4] = bytes([c[0], c[1], c[2], c[3] if len(c) > 3 else 255])

    for y in range(H):
        for x in range(W):
            n_fine = vnoise(x, y, 3, 101)
            n_med = vnoise(x, y, 12, 202)
            n_coarse = vnoise(x, y, 36, 303)

            col = (42, 45, 50, 255) # Fallback

            if (x, y) in FRAME_MAP:
                set_px(x, y, paint_frame(x, y, FRAME_MAP[(x, y)], camo_id, n_fine, n_med, n_coarse))
                continue

            # Armor-set modules may paint their own UV region (None = fall through to the shared livery)
            custom = None
            for paint, rects in painters:
                if any(u <= x < u + w and v <= y < v + h for u, v, w, h in rects):
                    custom = paint(x, y, camo_id, n_fine, n_med, n_coarse)
                    break
            if custom is not None:
                set_px(x, y, custom)
                continue

            # ==============================================================
            # REGION 1: PELVIS, TORSO, ARMS & LEGS INNER FRAME (0..200, 0..240)
            # ==============================================================
            if x < 200 and y < 240:
                # 1.1 Pilot Seat Bucket & Harness (80..155, 50..120)
                if 80 <= x <= 155 and 50 <= y <= 120:
                    if 94 <= x <= 138 and 62 <= y <= 108:
                        # Cushioned quilted seat: diamond stitch
                        stitch = ((x + y) % 8 == 0 or (x - y) % 8 == 0)
                        base_seat = (28, 26, 25) if not stitch else (55, 45, 35)
                        col = mul(base_seat, 0.95 + 0.1 * n_fine)
                        # Red 4-point harness straps
                        if x in (104, 105, 127, 128) and y < 100:
                            col = (190, 32, 28, 255)
                        elif y in (88, 89) and 102 <= x <= 130:
                            col = (190, 32, 28, 255)
                        elif x in (115, 116, 117) and y in (87, 88, 89):
                            col = (230, 230, 240, 255) # Silver buckle
                    else:
                        edge = (x in (80, 155) or y in (50, 120))
                        col = (30, 32, 36, 255) if edge else (58, 62, 68, 255)

                # 1.2 Assist Wheels (Pelvis: 50..80, 0..30 & Knee: 90..125, 180..215)
                elif (50 <= x <= 80 and 0 <= y <= 30) or (90 <= x <= 125 and 180 <= y <= 215):
                    cx, cy = (65, 15) if y < 100 else (107, 197)
                    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                    if dist <= 3.2:
                        col = (220, 225, 235, 255) # Polished axle center bolt
                    elif dist <= 4.5:
                        col = (60, 65, 75, 255)   # Grease ring
                    elif dist <= 8.5:
                        lug = False
                        for angle_deg in range(0, 360, 60):
                            lx = cx + 6.5 * math.cos(math.radians(angle_deg))
                            ly = cy + 6.5 * math.sin(math.radians(angle_deg))
                            if math.sqrt((x - lx)**2 + (y - ly)**2) < 1.3:
                                lug = True; break
                        col = (200, 205, 215, 255) if lug else (115, 120, 130, 255)
                    elif dist <= 10.5:
                        col = (30, 32, 35, 255)   # Inner rim shadow
                    else:
                        chevron = (int(dist * 2) + int(math.atan2(y - cy, x - cx) * 10)) % 4 == 0
                        tread_shade = 22 if chevron else 38
                        col = (tread_shade, tread_shade + 2, tread_shade + 4, 255)

                # 1.3 Head Sensor Camera Turret (160..195, 0..35)
                elif 160 <= x <= 195 and 0 <= y <= 35:
                    dist = math.sqrt((x - 173)**2 + (y - 13)**2)
                    if dist <= 4.5:
                        if dist <= 1.5 and x < 173 and y < 13:
                            col = (245, 255, 255, 255) # Specular reflection dot
                        elif dist <= 3.0:
                            col = (0, 255, 220, 255)   # Cyan optical core
                        else:
                            col = (0, 140, 180, 255)   # Coated glass rim
                    elif 5.0 <= dist <= 6.5:
                        col = (25, 26, 30, 255)        # Black rubber lens gasket
                    elif 180 <= x <= 186 and 10 <= y <= 16:
                        d2 = math.sqrt((x - 183)**2 + (y - 13)**2)
                        col = (255, 50, 60, 255) if d2 <= 2.2 else (40, 20, 25, 255)
                    else:
                        border = (x in (160, 195) or y in (0, 35) or x == 179)
                        col = (24, 26, 30, 255) if border else mul((68, 74, 82), 0.9 + 0.15 * n_fine)

                # 1.4 Chrome Hydraulic Cylinders & Brass Pivot Joints
                # (dense chrome bars / hose spirals removed: they read as white speckle on every frame part)
                elif x % 32 in (2, 3) and y % 40 < 12:
                    col = mul((132, 138, 148), 0.9 + 0.15 * n_fine)   # sparse dull piston highlight

                # 1.6 Radiator Vents & Heat Sinks
                elif (x % 8 in (0, 1) and y % 16 < 8 and x < 50):
                    col = (16, 18, 20, 255) # Recessed vent slat

                # 1.7 Heavy Steel Structural Frame
                else:
                    seam = (x % 24 == 0 or y % 24 == 0)
                    if seam:
                        col = (40, 43, 50, 255)
                    else:
                        base_chassis = (54, 58, 66)
                        col = mul(base_chassis, 0.88 + 0.22 * n_fine)

            # ==============================================================
            # REGION 2: MODULAR ARMOR PLATES & FACTION CAMOUFLAGE
            # (200..512, 0..315), (340..512, 315..400), and all 11 factions in (x,y) in BONE_MAP
            # ==============================================================
            elif (x, y) in BONE_MAP or (200 <= x < 512 and y < 315) or (340 <= x < 512 and 315 <= y < 400) or (x >= 512 and y < 340):
                # Check for unit stencil or marking first
                if (x, y) in MARKING_MAP:
                    col = MARKING_MAP[(x, y)]

                # Special legacy features in unmapped zones (e.g. VOTOMS red shoulder block)
                elif 400 <= x <= 460 and 50 <= y <= 95 and (x, y) not in BONE_MAP:
                    base_red = (195, 32, 28)
                    col = mul(base_red, 0.9 + 0.18 * n_fine)
                elif 400 <= x <= 450 and 0 <= y <= 45 and (x, y) not in BONE_MAP:
                    d_green = math.sqrt((x - 415)**2 + (y - 15)**2)
                    d_red = math.sqrt((x - 428)**2 + (y - 12)**2)
                    d_blue = math.sqrt((x - 425)**2 + (y - 25)**2)
                    if d_green <= 4.5:
                        col = (255, 255, 255, 255) if (d_green <= 1.2 and x < 415) else (0, 240, 110, 255)
                    elif d_red <= 3.2:
                        col = (255, 255, 255, 255) if (d_red <= 1.0 and x < 428) else (255, 45, 50, 255)
                    elif d_blue <= 2.8:
                        col = (255, 255, 255, 255) if (d_blue <= 0.8 and x < 425) else (0, 210, 255, 255)
                    else:
                        col = mul((60, 68, 55), 0.9 + 0.15 * n_fine)
                elif 400 <= x <= 460 and 100 <= y <= 160 and (x, y) not in BONE_MAP:
                    tube_x = (x - 400) % 18
                    tube_y = (y - 100) % 18
                    dt = math.sqrt((tube_x - 9)**2 + (tube_y - 9)**2)
                    if dt <= 3.2: col = (225, 38, 35, 255)
                    elif dt <= 5.2: col = (20, 22, 24, 255)
                    elif dt <= 6.5: col = (180, 185, 195, 255)
                    else: col = mul((75, 88, 62), 0.9 + 0.15 * n_fine)

                else:
                    base_armor = camo_base(camo_id, x, y, n_med, n_coarse)

                    # Micro-texture noise
                    col = mul(base_armor, 0.92 + 0.16 * n_fine)

                    # Authentic per-cube seams, bevels, and hex bolts (NO 14px grid stripes!)
                    detail = DETAIL_MAP.get((x, y), 0)
                    # soft relative shading: fixed black/white seams+bolts on every tiny cube made frames look noisy
                    if detail == 1:
                        col = mul(col, 0.78)        # 1px Panel Seam Recess
                    elif detail == 2:
                        col = mul(col, 1.1)         # 1px Bevel Highlight
                    elif detail == 3:
                        col = mul(col, 1.3)         # Bolt head

            # ==============================================================
            # REGION 3: INDUSTRIAL ROLL CAGE & UTILITY BACKPACKS (0..200, 240..315)
            # ==============================================================
            elif x < 200 and 240 <= y < 315:
                # 3.1 Industrial Roll Cage (0..75, 240..315)
                if x <= 75:
                    hazard = (x + y) // 6 % 2 == 0
                    base_yellow = (255, 205, 0)
                    base_black = (24, 25, 28)
                    col = base_yellow if hazard else base_black
                    if (x in (0, 75) or y in (240, 314)): col = (14, 15, 16, 255)

                # 3.2 Ammo Canister Module (140..195, 240..315)
                elif x >= 140:
                    seam_ammo = (x in (140, 195) or y in (240, 314))
                    if 155 <= x <= 178 and 262 <= y <= 268:
                        col = (245, 195, 25, 255) # Yellow Stencil Text "20MM HE-I"
                    elif seam_ammo:
                        col = (20, 24, 18, 255)
                    else:
                        col = mul((58, 68, 48), 0.9 + 0.15 * n_fine)

                # 3.3 Cargo Crate Module (80..139, 240..315)
                else:
                    frame_metal = (x in (80, 81, 138, 139) or y in (240, 241, 313, 314) or x == 110)
                    if frame_metal:
                        col = (145, 152, 162, 255)
                    else:
                        col = mul((72, 86, 56), 0.9 + 0.2 * n_fine)

            # ==============================================================
            # REGION 4: PRECISION & AUTOMATIC WEAPONS (0..340, 320..395)
            # ==============================================================
            elif x < 340 and 320 <= y < 395:
                # 4.1 Sniper AMR 20mm & Assault Rifle (0..180, 320..395)
                if x < 180:
                    d_scope = math.sqrt((x - 117)**2 + (y - 337)**2)
                    if d_scope <= 5.5:
                        if d_scope <= 1.8 and x < 117 and y < 337:
                            col = (255, 255, 255, 255)
                        elif d_scope <= 3.8:
                            col = (20, 190, 255, 255)
                        else:
                            col = (0, 70, 140, 255)
                    elif d_scope <= 7.0:
                        col = (20, 22, 25, 255)
                    elif 20 <= x <= 45 and 350 <= y <= 370:
                        stipple = (x % 2 == 0 and y % 2 == 0)
                        col = (18, 19, 20, 255) if stipple else (38, 40, 42, 255)
                    else:
                        flute = (y % 4 == 0 and x < 100)
                        col = (26, 28, 30, 255) if flute else mul((48, 52, 58), 0.9 + 0.18 * n_fine)

                # 4.2 Heavy Machine Gun & M134 Minigun (180..340, 320..395)
                else:
                    if 215 <= x <= 238 and 345 <= y <= 362:
                        cartridge = (x % 6 in (1, 2, 3, 4))
                        tip = (y < 348 and cartridge)
                        if tip: col = (180, 50, 45, 255)
                        elif cartridge: col = (240, 190, 35, 255)
                        else: col = (45, 48, 52, 255)
                    elif 280 <= x <= 335 and y < 350:
                        heat_t = (x - 280) / 55.0
                        if heat_t > 0.8: col = (45, 120, 215, 255)
                        elif heat_t > 0.6: col = (165, 65, 175, 255)
                        elif heat_t > 0.4: col = (210, 145, 40, 255)
                        else: col = (38, 40, 44, 255)
                    else:
                        col = mul((52, 56, 62), 0.9 + 0.15 * n_fine)

            # ==============================================================
            # REGION 5: EXPLOSIVE ORDNANCE & INDUSTRIAL TOOLS (0..512, 400..512)
            # ==============================================================
            elif y >= 400:
                # 5.1 Quad Missile Pod (0..120, 400..512)
                if x < 120:
                    quad_x = x % 30
                    quad_y = (y - 400) % 30
                    dq = math.sqrt((quad_x - 15)**2 + (quad_y - 15)**2)
                    if dq <= 6.5:
                        col = (235, 180, 20, 255) if dq <= 2.5 else (22, 24, 26, 255)
                    elif dq <= 8.5:
                        col = (160, 168, 178, 255)
                    else:
                        col = mul((65, 78, 54), 0.9 + 0.15 * n_fine)

                # 5.2 RPG-7 Heavy Demolition Launcher (120..240, 400..512)
                elif x < 240:
                    if 150 <= x <= 195 and 420 <= y <= 465:
                        dw = math.sqrt((x - 172)**2 + (y - 442)**2)
                        if dw <= 4.0: col = (225, 175, 40, 255)
                        elif dw <= 18.0:
                            cone_shade = (45, 165, 215)
                            col = mul(cone_shade, 0.88 + 0.22 * n_fine)
                        else:
                            col = (55, 68, 48, 255)
                    elif 125 <= x <= 148 and 420 <= y <= 455:
                        woodgrain = int(math.sin(y * 0.4 + math.cos(x * 0.8)) * 18)
                        col = (145 + woodgrain, 78 + woodgrain // 2, 32, 255)
                    else:
                        col = mul((62, 75, 50), 0.9 + 0.15 * n_fine)

                # 5.3 Tungsten Mining Drill (240..360, 400..512)
                elif x < 360:
                    if 285 <= x <= 355 and 420 <= y <= 475:
                        spiral = ((x * 2 + y * 3) // 8) % 2 == 0
                        col = (205, 215, 230, 255) if spiral else (105, 112, 125, 255)
                    else:
                        stripes = (x + y) // 8 % 2 == 0
                        col = (255, 200, 10, 255) if stripes else (30, 32, 35, 255)

                # 5.4 Forestry Chainsaw (360..512, 400..512)
                else:
                    chain = (x + y) % 4 == 0
                    if x >= 460:
                        groove = (y % 6 in (2, 3))
                        col = (45, 48, 52, 255) if groove else (160, 168, 176, 255)
                    elif chain:
                        col = (240, 245, 250, 255)
                    else:
                        col = mul((245, 95, 18), 0.9 + 0.18 * n_fine)

            # ==============================================================
            # REGION 6: 8 NEW HEAVY & SPECIAL WEAPONS (0..960, 520..660)
            # ==============================================================
            elif 520 <= y < 660 and x < 960:
                # 6.1 Marksman Battle Rifle (0..120)
                if x < 120:
                    d_scope = math.sqrt((x - 60)**2 + (y - 540)**2)
                    if d_scope <= 4.0:
                        col = (25, 180, 240, 255) # Lens
                    elif 10 <= (x % 30) <= 20 and y > 580:
                        col = (26, 28, 30, 255) # Polymer grip
                    else:
                        col = mul((42, 45, 48), 0.9 + 0.15 * n_fine)

                # 6.2 30mm Heavy Autocannon (120..240)
                elif x < 240:
                    dx, dy = (x - 180), (y - 590)
                    d_drum = math.sqrt(dx*dx + dy*dy)
                    if d_drum <= 20.0:
                        col = (195, 155, 50, 255) if d_drum > 16.0 or d_drum < 5.0 else (160, 125, 40, 255)
                    else:
                        col = mul((36, 38, 42), 0.9 + 0.15 * n_fine)

                # 6.3 Tactical Combat Breacher Shotgun (240..360)
                elif x < 360:
                    if 260 <= x <= 300 and 535 <= y <= 550:
                        col = (165, 35, 30, 255) # Heat shield red
                    elif 310 <= x <= 340 and 560 <= y <= 580:
                        col = (22, 24, 26, 255) # Ribbed pump
                    else:
                        col = mul((32, 34, 38), 0.9 + 0.15 * n_fine)

                # 6.4 40mm Rotary Multi-Grenade Launcher (360..480)
                elif x < 480:
                    if 400 <= x <= 440 and 550 <= y <= 590:
                        col = (230, 190, 40, 255) if (x + y) % 8 == 0 else (45, 48, 42, 255)
                    else:
                        col = mul((50, 54, 46), 0.9 + 0.15 * n_fine)

                # 6.5 84mm Anti-Tank Recoilless Rifle (480..600)
                elif x < 600:
                    if 520 <= x <= 535 and 530 <= y <= 560:
                        col = (235, 185, 30, 255) # Caution band
                    elif x > 570 and y > 610:
                        col = (55, 58, 62, 255) # Venturi nozzle
                    else:
                        col = mul((130, 125, 95), 0.9 + 0.15 * n_fine)

                # 6.6 Guided Heavy ATGM Launcher (600..720)
                elif x < 720:
                    d_optic = math.sqrt((x - 630)**2 + (y - 545)**2)
                    if d_optic <= 5.0:
                        col = (20, 220, 180, 255) # Optic seeker
                    elif 640 <= x <= 690 and 560 <= y <= 600:
                        col = (210, 160, 40, 255) # Launch container
                    else:
                        col = mul((38, 40, 42), 0.9 + 0.15 * n_fine)

                # 6.7 Heavy Pressurized Flamethrower (720..840)
                elif x < 840:
                    if 740 <= x <= 790 and 560 <= y <= 620:
                        col = mul((185, 42, 36), 0.9 + 0.15 * n_fine) # Napalm tank red
                    elif 800 <= x <= 830 and 530 <= y <= 550:
                        col = (225, 180, 55, 255) # Brass manifold
                    else:
                        col = mul((50, 52, 56), 0.9 + 0.15 * n_fine)

                # 6.8 Tactical High-Frequency Vibro-Blade (840..960)
                else:
                    if 860 <= x <= 940 and 530 <= y <= 550:
                        col = (255, 140, 20, 255) # Superheated thermal edge
                    elif 850 <= x <= 880 and 570 <= y <= 610:
                        col = (25, 26, 28, 255) # Textured grip
                    else:
                        col = mul((40, 42, 48), 0.9 + 0.18 * n_fine) # Tungsten spine

            set_px(x, y, col)

    return buf

# ----------------- Execution -----------------
OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src/main/resources/assets/obsolete/textures/entity/exoframe"))
os.makedirs(OUT_DIR, exist_ok=True)

SCHEMES = [
    ("exoframe.png", 0),             # Default Sand PMC Factory
    ("exoframe_woodland.png", 1),    # USMC Woodland MARPAT
    ("exoframe_desert.png", 2),      # Desert Nomad Tri-Color
    ("exoframe_urban.png", 3),       # Cerberus Urban Hex
    ("exoframe_arctic.png", 4),      # Arctic Blizzard
    ("exoframe_tigerstripe.png", 5), # VOTOMS Jungle Tigerstripe
    ("exoframe_hazard.png", 6),      # Industrial Hazard Yellow
]

if __name__ == "__main__":
    print("Synthesizing 7 High-Fidelity 1024x1024 Textures...")
    for fname, cid in SCHEMES:
        target_path = os.path.join(OUT_DIR, fname)
        buf = generate_texture_buffer(cid)
        png_bytes = create_png(1024, 1024, buf)
        with open(target_path, "wb") as f:
            f.write(png_bytes)
        print(f"  [+] Generated {fname} ({len(png_bytes):,} bytes)")

    print("All 7 Master Faction Textures Successfully Generated!")
