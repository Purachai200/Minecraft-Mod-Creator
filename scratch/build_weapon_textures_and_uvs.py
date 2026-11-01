#!/usr/bin/env python3
"""Procedurally packs UVs and paints rich, realistic, high-contrast mechanical textures
for all 17 Exoframe weapons across exoframe.geo.json and all 7 texture variants.

Fixes User Issue #2:
- Weapon textures were previously all mapped to single flat-gray coordinates [0, 320]
- Remaps every cube to a unique non-overlapping UV rectangle in the free Y=736..855 band
- Paints gunmetal steel, titanium heat-bluing, brass ammo belts, optical sapphire lenses,
  woodgrain insulators, illuminated reticles, plasma blades, and hazard warning chevrons.
"""

import json
import math
import os
import struct
import zlib

GEO_PATH = "Obsolete/src/main/resources/assets/obsolete/geo/exoframe.geo.json"
TEX_DIR = "Obsolete/src/main/resources/assets/obsolete/textures/entity/exoframe"

TEXTURES = [
    ("exoframe.png", "default"),
    ("exoframe_woodland.png", "woodland"),
    ("exoframe_desert.png", "desert"),
    ("exoframe_urban.png", "urban"),
    ("exoframe_arctic.png", "arctic"),
    ("exoframe_tigerstripe.png", "tigerstripe"),
    ("exoframe_hazard.png", "hazard"),
]

# ==================== 1. PNG DECODER & ENCODER (PURE PYTHON) ====================

def decode_png(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG: {path}"
    pos = 8
    idat = bytearray()
    w, h = 0, 0
    while pos < len(data):
        length, chunk_type = struct.unpack(">I4s", data[pos:pos+8])
        pos += 8
        content = data[pos:pos+length]
        pos += length + 4
        if chunk_type == b"IHDR":
            w, h, depth, color = struct.unpack(">IIBB", content[:10])
            assert depth == 8 and color == 6, f"Unsupported PNG format: depth={depth}, color={color}"
        elif chunk_type == b"IDAT":
            idat.extend(content)
        elif chunk_type == b"IEND":
            break
    decomp = zlib.decompress(idat)
    stride = w * 4 + 1
    raw = bytearray(w * h * 4)
    for y in range(h):
        line = decomp[y * stride : (y + 1) * stride]
        filter_type = line[0]
        row = bytearray(line[1:])
        if filter_type == 0:
            pass
        elif filter_type == 1:
            for x in range(4, w * 4):
                row[x] = (row[x] + row[x - 4]) & 0xFF
        elif filter_type == 2:
            if y > 0:
                prev = raw[(y - 1) * w * 4 : y * w * 4]
                for x in range(w * 4):
                    row[x] = (row[x] + prev[x]) & 0xFF
        elif filter_type == 3:
            prev = raw[(y - 1) * w * 4 : y * w * 4] if y > 0 else bytearray(w * 4)
            for x in range(w * 4):
                a = row[x - 4] if x >= 4 else 0
                b = prev[x]
                row[x] = (row[x] + ((a + b) // 2)) & 0xFF
        elif filter_type == 4:
            prev = raw[(y - 1) * w * 4 : y * w * 4] if y > 0 else bytearray(w * 4)
            for x in range(w * 4):
                a = row[x - 4] if x >= 4 else 0
                b = prev[x]
                c = prev[x - 4] if x >= 4 else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                row[x] = (row[x] + pr) & 0xFF
        raw[y * w * 4 : (y + 1) * w * 4] = row
    return w, h, raw


def encode_png(path, width, height, raw_rgba):
    stride = width * 4
    scanlines = bytearray((stride + 1) * height)
    for y in range(height):
        scanlines[y * (stride + 1)] = 0
        scanlines[y * (stride + 1) + 1 : (y + 1) * (stride + 1)] = raw_rgba[y * stride : (y + 1) * stride]

    compressed = zlib.compress(bytes(scanlines), 6)

    def make_chunk(chunk_type, data):
        c = chunk_type + data
        crc = zlib.crc32(c) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + c + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    out = bytearray(b"\x89PNG\r\n\x1a\n")
    out.extend(make_chunk(b"IHDR", ihdr))
    out.extend(make_chunk(b"IDAT", compressed))
    out.extend(make_chunk(b"IEND", b""))

    with open(path, "wb") as f:
        f.write(out)


# ==================== 2. SHELF UV PACKER ====================

class ShelfPacker:
    def __init__(self, start_x, start_y, max_width, max_height):
        self.start_x = start_x
        self.start_y = start_y
        self.max_w = max_width
        self.max_h = max_height
        self.cur_x = start_x
        self.cur_y = start_y
        self.row_h = 0

    def pack(self, w, h):
        pw = w + 1
        ph = h + 1
        if self.cur_x + pw > self.start_x + self.max_w:
            self.cur_x = self.start_x
            self.cur_y += self.row_h + 1
            self.row_h = 0
        if self.cur_y + ph > self.start_y + self.max_h:
            raise ValueError(f"Shelf out of space: cur_y={self.cur_y}, ph={ph}")
        pos = (self.cur_x, self.cur_y)
        self.cur_x += pw
        self.row_h = max(self.row_h, ph)
        return pos


# ==================== 3. WEAPON CUBE MATERIAL CLASSIFICATION ====================

# Roles:
# 'gunmetal', 'camo', 'steel', 'heat_blued', 'rail', 'optic_body', 'sapphire_lens',
# 'emerald_lens', 'grip', 'rubber', 'magazine', 'ammo_box', 'brass_belt',
# 'shotgun_shells', 'woodgrain', 'warhead', 'hazard_stripes', 'plasma_blade',
# 'vibro_spine', 'vibro_hilt', 'shield_plate', 'shield_glass', 'stun_prongs',
# 'chrome_shaft', 'graphite'

def classify_cube(weapon_name, idx, size, origin):
    sx, sy, sz = size
    ox, oy, oz = origin

    if weapon_name == "weapon_assault_rifle":
        if idx == 0: return "gunmetal"           # receiver
        if idx == 1: return "brass_belt"         # ejection port brass
        if idx == 2: return "rail"               # top rail
        if 3 <= idx <= 8: return "rail"          # rail teeth
        if 9 <= idx <= 10: return "steel"        # sight mount posts
        if idx == 11: return "optic_body"        # optic hood
        if 12 <= idx <= 13: return "optic_body"  # dials
        if idx == 14: return "sapphire_lens"     # optic reticle lens
        if idx == 15: return "camo"              # handguard
        if 16 <= idx <= 20: return "gunmetal"    # M-LOK slots
        if idx == 21: return "rail"              # lower rail
        if idx == 22: return "steel"             # barrel
        if idx == 23: return "gunmetal"          # gas tube
        if idx == 24: return "heat_blued"        # muzzle brake
        if 25 <= idx <= 26: return "sapphire_lens" # front sight tritium
        if 27 <= idx <= 30: return "magazine"    # PMAG
        if idx == 31: return "rubber"            # mag base
        if idx == 32: return "grip"              # pistol grip
        if 33 <= idx <= 34: return "steel"       # trigger & guard
        if idx == 35: return "steel"             # buffer tube
        if idx == 36: return "rubber"            # buttpad
        if idx == 37: return "camo"              # cheek comb

    elif weapon_name == "weapon_sniper_amr":
        if idx == 0: return "gunmetal"           # bullpup receiver
        if idx == 1: return "rail"               # top rail
        if idx == 2: return "optic_body"         # scope tube
        if 3 <= idx <= 8: return "optic_body"    # scope bells
        if idx == 9: return "sapphire_lens"      # coated lens
        if idx == 10: return "steel"             # 20mm sniper barrel
        if 11 <= idx <= 12: return "heat_blued"  # tank muzzle brake
        if idx == 13: return "camo"              # barrel jacket
        if idx == 14: return "steel"             # carry handle
        if idx == 15: return "steel"             # bipod mount
        if 16 <= idx <= 17: return "gunmetal"    # bipod legs
        if idx == 18: return "grip"              # sniper grip
        if idx == 19: return "rubber"            # cheek / stock pad

    elif weapon_name == "weapon_machine_gun":
        if idx == 0: return "gunmetal"           # receiver
        if idx == 1: return "camo"               # shroud
        if 2 <= idx <= 8: return "gunmetal"      # cooling ribs
        if idx == 9: return "steel"              # barrel tip
        if 10 <= idx <= 12: return "heat_blued"  # flash hider
        if 13 <= idx <= 14: return "ammo_box"    # ammo can
        if idx == 15: return "steel"             # feed throat
        if 16 <= idx <= 19: return "brass_belt"  # linked ammo belt
        if idx == 20: return "grip"              # spade grip
        if 21 <= idx <= 22: return "steel"       # buffer & stock

    elif weapon_name == "weapon_minigun_m134":
        if 0 <= idx <= 2: return "gunmetal"      # rotor motor housing
        if 3 <= idx <= 5: return "steel"         # front rotor plate
        if 6 <= idx <= 11: return "heat_blued"   # 6 gatling barrels
        if 12 <= idx <= 14: return "steel"       # clamp rings
        if 15 <= idx <= 17: return "grip"        # carry & grips
        if 18 <= idx <= 20: return "hazard_stripes" # motor feed shroud
        return "gunmetal"

    elif weapon_name == "weapon_rocket_launcher":
        if idx < 24:
            # 4 rocket launch tubes (ends have hazard stripes, inside has red warheads)
            if sz < 1.0: return "warhead"
            return "camo"
        if 24 <= idx <= 26: return "hazard_stripes" # pod bracket / hazard rims
        if 27 <= idx <= 29: return "emerald_lens"   # laser targeting optic
        return "grip"

    elif weapon_name == "weapon_rpg7_heavy":
        if 0 <= idx <= 2: return "camo"          # launcher tube
        if 3 <= idx <= 5: return "woodgrain"     # wooden heat shield
        if 6 <= idx <= 8: return "heat_blued"    # rear venturi cone
        if 9 <= idx <= 11: return "warhead"      # shaped charge bomb
        if 12 <= idx <= 14: return "gunmetal"    # ogive nose
        if idx == 15: return "steel"             # standoff probe
        if 16 <= idx <= 17: return "grip"        # grips
        if idx == 18: return "sapphire_lens"     # PGO-7 sight

    elif weapon_name == "weapon_battle_rifle":
        if idx in (0, 1): return "gunmetal"
        if idx == 2: return "rail"
        if idx in (3, 4): return "camo"
        if idx == 5: return "steel"
        if idx == 6: return "heat_blued"
        if idx in (7, 8): return "sapphire_lens"
        if idx == 9: return "magazine"
        if idx == 10: return "grip"
        if idx in (11, 12): return "camo"
        return "gunmetal"

    elif weapon_name == "weapon_autocannon_30mm":
        if idx in (0, 1): return "gunmetal"
        if idx == 2: return "steel"
        if idx in (3, 4): return "heat_blued"
        if idx == 5: return "steel"
        if idx in (6, 7): return "camo"
        return "steel"

    elif weapon_name == "weapon_shotgun_breacher":
        if idx in (0, 1): return "gunmetal"
        if idx == 2: return "steel"
        if idx == 3: return "shotgun_shells"
        if idx == 4: return "grip"
        if idx in (5, 6): return "camo"
        return "gunmetal"

    elif weapon_name == "weapon_grenade_launcher":
        if idx in (0, 1, 2, 3): return "brass_belt" # revolving cylinder grenade bases
        if idx == 4: return "steel"
        if 5 <= idx <= 7: return "gunmetal"
        if idx == 8: return "grip"
        if idx == 9: return "camo"
        return "optic_body"

    elif weapon_name == "weapon_recoilless_rifle":
        if 0 <= idx <= 2: return "camo"          # main tube
        if 3 <= idx <= 5: return "heat_blued"    # venturi cone
        if 6 <= idx <= 8: return "hazard_stripes"# muzzle ring hazard
        if idx == 9: return "sapphire_lens"      # sight
        return "grip"

    elif weapon_name == "weapon_atgm_guided":
        if 0 <= idx <= 1: return "camo"          # launch box
        if idx == 2: return "hazard_stripes"     # front cap hazard
        if 3 <= idx <= 5: return "sapphire_lens" # optical sensor
        if 6 <= idx <= 8: return "emerald_lens"  # thermal sensor
        return "grip"

    elif weapon_name == "weapon_flamethrower":
        if idx == 0: return "steel"              # body
        if idx == 1: return "heat_blued"         # nozzle
        if 2 <= idx <= 7: return "brass_belt"    # dual brass fuel tanks
        if idx == 8: return "hazard_stripes"     # pilot torch flame guard
        if idx == 9: return "camo"
        return "grip"

    elif weapon_name == "weapon_vibro_blade":
        if idx == 0: return "vibro_hilt"         # hilt pommel
        if idx == 1: return "vibro_hilt"         # crossguard / emitter housing
        if idx == 2: return "steel"              # emitter ring
        if idx == 3: return "vibro_spine"        # reinforced dark tungsten spine
        if idx == 4: return "plasma_blade"       # glowing plasma cutting edge
        if idx == 5: return "plasma_blade"       # plasma blade tip
        if idx == 6: return "sapphire_lens"      # pulsing power core

    elif weapon_name == "weapon_riot_shield":
        if idx == 0: return "shield_plate"       # main face
        if 1 <= idx <= 2: return "shield_plate"  # side deflector wings
        if idx == 3: return "shield_glass"       # vision viewport
        if 4 <= idx <= 5: return "hazard_stripes"# top/bottom hazard lips
        return "grip"

    elif weapon_name == "weapon_stun_baton":
        if idx == 0: return "grip"               # handle
        if idx == 1: return "steel"              # guard ring
        if idx == 2: return "chrome_shaft"       # shaft
        if idx == 3: return "stun_prongs"        # electrode head
        return "stun_prongs"                     # discharge rings

    elif weapon_name == "weapon_fishing_rod":
        if idx == 0: return "grip"
        if 1 <= idx <= 12: return "brass_belt"   # reel
        if 13 <= idx <= 15: return "graphite"    # rod blanks
        return "steel"                           # guides

    return "gunmetal"


# ==================== 4. PROCEDURAL TEXTURE SYNTHESIS ====================

def get_camo_palette(camo_type):
    if camo_type == "woodland":
        return ((52, 68, 44), (86, 62, 42), (115, 110, 80)) # green, brown, khaki
    elif camo_type == "desert":
        return ((168, 144, 110), (140, 116, 85), (185, 168, 135)) # sand, coyote, tan
    elif camo_type == "urban":
        return ((76, 84, 96), (48, 54, 62), (120, 130, 142)) # slate, dark navy, steel
    elif camo_type == "arctic":
        return ((210, 218, 224), (160, 170, 180), (60, 68, 75)) # snow white, ice gray, charcoal
    elif camo_type == "tigerstripe":
        return ((40, 42, 44), (58, 75, 48), (110, 95, 65)) # black, jungle green, khaki
    elif camo_type == "hazard":
        return ((235, 185, 25), (32, 34, 38), (245, 205, 45)) # safety yellow, dark charcoal, bright amber
    else: # default
        return ((62, 72, 54), (45, 52, 40), (78, 90, 68)) # tactical olive drab


def paint_cube_texture(raw, tex_w, tex_h, uv_x, uv_y, box_w, box_h, role, camo_type):
    palette = get_camo_palette(camo_type)

    def set_pixel(x, y, r, g, b, a=255):
        if 0 <= x < tex_w and 0 <= y < tex_h:
            idx = (y * tex_w + x) * 4
            raw[idx] = max(0, min(255, int(r)))
            raw[idx + 1] = max(0, min(255, int(g)))
            raw[idx + 2] = max(0, min(255, int(b)))
            raw[idx + 3] = max(0, min(255, int(a)))

    for dy in range(box_h):
        for dx in range(box_w):
            px = uv_x + dx
            py = uv_y + dy
            # Edge shading (Ambient Occlusion)
            is_edge = (dx == 0 or dx == box_w - 1 or dy == 0 or dy == box_h - 1)
            is_top = (dy == 0)

            # --- MATERIAL SHADERS ---
            if role == "gunmetal":
                # Dark parkerized matte steel with fine noise and bevel
                base = 40 + ((dx * 7 + dy * 13) % 9) - 4
                r, g, b = base, base + 3, base + 7
                if is_top: r, g, b = r + 24, g + 26, b + 30
                elif is_edge: r, g, b = r - 16, g - 16, b - 14

            elif role == "camo":
                # Procedural faction camouflage pattern
                p_idx = ((dx // 3 + dy // 3) + ((dx * 11) ^ (dy * 7)) % 5) % 3
                col = palette[p_idx]
                r, g, b = col[0], col[1], col[2]
                noise = ((dx * 5 + dy * 9) % 7) - 3
                r, g, b = r + noise, g + noise, b + noise
                if is_top: r, g, b = r + 20, g + 20, b + 20
                elif is_edge: r, g, b = r - 22, g - 22, b - 22

            elif role == "steel":
                # Bright machined stainless / titanium steel
                base = 135 + ((dx * 3 + dy * 11) % 11) - 5
                r, g, b = base, base + 6, base + 12
                if is_top: r, g, b = r + 35, g + 38, b + 42
                elif is_edge: r, g, b = r - 30, g - 30, b - 28

            elif role == "heat_blued":
                # Titanium heat tempering gradient: gold -> magenta/purple -> deep indigo -> cyan
                t = dx / max(1, box_w - 1)
                if t < 0.25:
                    # gunmetal steel
                    r, g, b = 50, 54, 60
                elif t < 0.50:
                    # purple / magenta
                    r, g, b = 130, 60, 140
                elif t < 0.75:
                    # deep indigo / blue
                    r, g, b = 50, 80, 185
                elif t < 0.90:
                    # electric cyan
                    r, g, b = 60, 175, 230
                else:
                    # straw gold at tip
                    r, g, b = 220, 175, 60
                if is_top: r, g, b = min(255, r + 25), min(255, g + 25), min(255, b + 25)
                elif is_edge: r, g, b = max(0, r - 20), max(0, g - 20), max(0, b - 20)

            elif role == "rail":
                # Picatinny rail with alternating teeth slots
                is_tooth = (dx % 3 < 2)
                if is_tooth:
                    r, g, b = 62, 66, 74
                else:
                    r, g, b = 24, 26, 30 # deep shadow notch
                if is_top: r, g, b = r + 15, g + 16, b + 20

            elif role == "optic_body":
                # Matte black non-reflective optic chassis with brass dial ring
                r, g, b = 28, 30, 34
                if dx == box_w // 2 and dy % 2 == 0:
                    r, g, b = 185, 150, 45 # knurled brass dial marking
                if is_edge: r, g, b = 18, 20, 22

            elif role == "sapphire_lens":
                # Multi-coated optical glass with cyan glare streak & center red reticle dot
                cx, cy = box_w / 2.0, box_h / 2.0
                dist = math.sqrt((dx - cx) ** 2 + (dy - cy) ** 2)
                if dist < 1.0:
                    r, g, b = 255, 40, 40 # illuminated red FCS aiming dot!
                elif abs(dx - dy) <= 1:
                    r, g, b = 180, 245, 255 # specular reflection streak
                else:
                    r, g, b = 30, 140, 225 # deep sapphire lens body

            elif role == "emerald_lens":
                # Thermal / night-vision optical lens
                cx, cy = box_w / 2.0, box_h / 2.0
                dist = math.sqrt((dx - cx) ** 2 + (dy - cy) ** 2)
                if dist < 1.0:
                    r, g, b = 255, 240, 60 # amber reticle
                elif abs(dx - dy) <= 1:
                    r, g, b = 160, 255, 210 # glare streak
                else:
                    r, g, b = 25, 185, 95 # vibrant emerald optical coating

            elif role == "grip":
                # Stippled tactical rubber/polymer grip
                stipple = ((dx * 7) ^ (dy * 13)) % 4
                base = 24 + stipple * 4
                r, g, b = base, base, base + 2
                if is_edge: r, g, b = 14, 14, 16

            elif role == "rubber":
                # Chevron rubber buttpad
                chevron = (dx + dy) % 3 == 0
                base = 32 if chevron else 22
                r, g, b = base, base, base

            elif role == "magazine":
                # PMAG polymer with brass cartridge round count window
                is_window = (1 <= dy <= box_h - 2 and box_w // 3 <= dx <= box_w // 2)
                if is_window:
                    r, g, b = 220, 180, 45 # visible brass cartridge
                else:
                    r, g, b = 36, 38, 42 # dark ribbed polymer
                    if dx % 2 == 0: r, g, b = r + 10, g + 10, b + 12

            elif role == "ammo_box":
                # Olive / coyote stamped metal ammo can with yellow warning triangle
                col = palette[0]
                r, g, b = col[0], col[1], col[2]
                if box_w > 4 and box_h > 4:
                    # yellow hazard stencil in center
                    if dx == box_w // 2 and dy == box_h // 2:
                        r, g, b = 245, 205, 30
                if is_edge: r, g, b = r - 25, g - 25, b - 25

            elif role == "brass_belt":
                # Linked 12.7mm / 20mm brass cartridges with copper tips
                is_tip = (dy < max(1, box_h // 4))
                if is_tip:
                    r, g, b = 185, 85, 45 # copper bullet tip
                else:
                    r, g, b = 225, 180, 45 # polished brass casing
                    if is_top: r, g, b = 250, 220, 90
                    elif is_edge: r, g, b = 175, 135, 30

            elif role == "shotgun_shells":
                # 12-gauge high-brass red tactical breacher shells
                is_brass = (dy >= box_h - max(1, box_h // 3))
                if is_brass:
                    r, g, b = 225, 180, 45 # brass base
                else:
                    r, g, b = 210, 32, 32 # crimson plastic hull

            elif role == "woodgrain":
                # RPG-7 phenolic woodgrain laminate
                grain = int(math.sin(dy * 1.2 + dx * 0.4) * 20)
                r = 135 + grain
                g = 72 + (grain // 2)
                b = 32 + (grain // 3)
                if is_edge: r, g, b = r - 20, g - 15, b - 10

            elif role == "warhead":
                # Demolition warhead: olive body with yellow hazard band
                is_band = (box_h > 4 and dy == box_h // 2)
                if is_band:
                    r, g, b = 240, 200, 30 # yellow hazard stripe
                else:
                    r, g, b = 65, 76, 52 # military olive ordnance
                if is_edge: r, g, b = r - 18, g - 18, b - 18

            elif role == "hazard_stripes":
                # 45-degree high-vis safety warning chevrons (Safety Yellow & Black)
                stripe = ((dx + dy) // 3) % 2
                if stripe == 0:
                    r, g, b = 248, 202, 22 # vibrant safety yellow
                else:
                    r, g, b = 26, 28, 30 # matte black
                if is_edge: r, g, b = max(0, r - 25), max(0, g - 25), max(0, b - 25)

            elif role == "plasma_blade":
                # Incandescent glowing high-frequency vibro plasma blade
                # White-hot interior core with electric cyan outer aura
                t = dy / max(1, box_h - 1)
                core = math.sin(t * math.pi)
                if core > 0.6:
                    r, g, b = 235, 255, 255 # incandescent white-hot core
                elif core > 0.2:
                    r, g, b = 110, 235, 255 # brilliant cyan plasma
                else:
                    r, g, b = 40, 140, 245 # deep azure energy halo
                if dx == 0:
                    r, g, b = 255, 255, 255 # razor-sharp cutting edge highlight!

            elif role == "vibro_spine":
                # Dark reinforced tungsten-carbide spine
                base = 32 + ((dx * 5 + dy * 7) % 7)
                r, g, b = base, base + 2, base + 5
                if is_top: r, g, b = 75, 85, 105
                elif is_edge: r, g, b = 18, 20, 24

            elif role == "vibro_hilt":
                # Titanium chassis with cyan LED status light
                r, g, b = 65, 70, 78
                if dx == box_w // 2 and dy == box_h // 2:
                    r, g, b = 40, 240, 255 # cyan power indicator LED
                elif is_edge: r, g, b = 38, 40, 46

            elif role == "shield_plate":
                # Heavy ballistic shield armor face
                col = palette[0]
                r, g, b = col[0] - 8, col[1] - 8, col[2] - 8
                # Heavy perimeter rivets
                if (dx in (1, box_w - 2)) and (dy in (1, box_h - 2)):
                    r, g, b = 180, 190, 205 # steel rivet
                elif is_edge: r, g, b = r - 24, g - 24, b - 24

            elif role == "shield_glass":
                # Ballistic reinforced viewport with gasket frame
                if is_edge:
                    r, g, b = 25, 27, 30 # rubber gasket frame
                else:
                    r, g, b = 90, 160, 185 # cyan ballistic glass with wire mesh

            elif role == "stun_prongs":
                # High-voltage arc discharge electrodes
                if (dx + dy) % 2 == 0:
                    r, g, b = 70, 200, 255 # electric blue zap
                else:
                    r, g, b = 220, 245, 255 # white spark
                if is_edge: r, g, b = 35, 110, 200

            elif role == "chrome_shaft":
                # Mirror-finish polished chrome steel
                base = 190 + int(math.sin(dx * 1.5) * 45)
                r, g, b = base, base + 2, base + 6

            elif role == "graphite":
                # Woven graphite composite rod blank
                base = 45 + ((dx + dy) % 2) * 12
                r, g, b = base, base, base

            else:
                r, g, b = 50, 54, 60

            set_pixel(px, py, r, g, b, 255)


# ==================== 5. MAIN GENERATION PIPELINE ====================

def main():
    print(f"Loading geometry from {GEO_PATH}...")
    with open(GEO_PATH, "r", encoding="utf-8") as f:
        geo = json.load(f)

    bones = geo["minecraft:geometry"][0]["bones"]
    weapon_bones = [b for b in bones if "weapon" in b.get("name", "") and len(b.get("cubes", [])) > 0]
    print(f"Found {len(weapon_bones)} weapon bones with active geometry cubes.")

    # Shelf pack all weapon cubes in the free Y=736..855 band
    packer = ShelfPacker(start_x=0, start_y=736, max_width=1024, max_height=288)

    assignments = [] # (weapon_name, cube_index, (uv_x, uv_y), (box_w, box_h), role)

    for b in weapon_bones:
        wname = b["name"]
        for idx, cube in enumerate(b["cubes"]):
            sz = cube["size"]
            orig = cube["origin"]
            w = int(2 * (sz[0] + sz[2]) + 0.999)
            h = int(sz[1] + sz[2] + 0.999)
            uv_pos = packer.pack(w, h)
            role = classify_cube(wname, idx, sz, orig)

            # Assign new UV to cube in geo
            cube["uv"] = [uv_pos[0], uv_pos[1]]
            assignments.append((wname, idx, uv_pos, (w, h), role))

    print(f"Packed {len(assignments)} weapon cubes. Packer reached Y={packer.cur_y + packer.row_h}.")

    # Save updated geo.json
    with open(GEO_PATH, "w", encoding="utf-8") as f:
        json.dump(geo, f, indent=2)
    print(f"Updated {GEO_PATH} with distinct non-overlapping weapon UVs.")

    # Paint textures
    for fname, ctype in TEXTURES:
        tpath = os.path.join(TEX_DIR, fname)
        if not os.path.exists(tpath):
            print(f"Warning: {tpath} not found, skipping.")
            continue
        print(f"Painting weapon textures into {fname} ({ctype} theme)...")
        tw, th, raw = decode_png(tpath)

        for wname, idx, (ux, uy), (bw, bh), role in assignments:
            paint_cube_texture(raw, tw, th, ux, uy, bw, bh, role, ctype)

        encode_png(tpath, tw, th, raw)
        print(f"  Successfully wrote {tpath} ({tw}x{th})")

    print("\nAll weapon UVs and textures generated successfully!")


if __name__ == "__main__":
    main()
