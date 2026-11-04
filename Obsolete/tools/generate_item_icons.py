"""
High-Clarity 16x16 Pixel Art Icon Generator for the OBSOLETE Mecha Mod items.
Pure Python - zero external dependencies. Hand-weapon icons are rendered from exoframe.geo.json (WEAPON_ICONS).
"""
import struct
import zlib
import os
import math

def create_png_16x16(pixel_grid):
    raw = bytearray()
    for y in range(16):
        raw.append(0) # Filter type 0
        for x in range(16):
            r, g, b, a = pixel_grid[y][x]
            raw.extend([r, g, b, a])

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', 16, 16, 8, 6, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(bytes(raw), level=6))
    iend = chunk(b'IEND', b'')
    return header + ihdr + idat + iend

def parse_ascii_art(art, palette):
    grid = []
    lines = [l for l in art.strip().split('\n') if l]
    assert len(lines) == 16, f"Expected 16 lines, got {len(lines)}"
    for line in lines:
        chars = line.strip()
        assert len(chars) == 16, f"Expected 16 chars per line, got {len(chars)}: {chars}"
        row = []
        for ch in chars:
            if ch == '.':
                row.append(palette.get('.', (0, 0, 0, 0)))
            else:
                row.append(palette[ch])
        grid.append(row)
    return grid

# ==================== PALETTES ====================
_ = (0, 0, 0, 0) # Transparent
BLK = (18, 20, 24, 255)
WHT = (245, 248, 252, 255)
GRY = (160, 170, 182, 255)
DKG = (60, 68, 76, 255)
CYN = (0, 225, 255, 255)
YEL = (255, 204, 0, 255)
RED = (225, 40, 35, 255)
GLD = (220, 175, 45, 255)
ORG = (255, 120, 20, 255)
BRS = (205, 160, 50, 255)
COP = (184, 115, 51, 255)

# Faction Specific Palettes
# Sand / Industrial Standard
PAL_SAND = {
    'X': (32, 28, 24, 255),
    'M': (190, 168, 130, 255),
    'D': (130, 112, 85, 255),
    'L': (225, 205, 170, 255),
    'C': CYN,
    'Y': YEL,
}

# USMC Olive
PAL_USMC = {
    'X': (24, 30, 24, 255),
    'M': (68, 82, 58, 255),
    'D': (44, 54, 38, 255),
    'L': (98, 118, 84, 255),
    'C': (255, 185, 40, 255), # Amber visor
    'Y': WHT,
}

# Cerberus / Pegaso Black
PAL_CERBERUS = {
    'X': (16, 18, 22, 255),
    'M': (36, 40, 46, 255),
    'D': (24, 26, 30, 255),
    'L': (65, 72, 82, 255),
    'C': (235, 30, 30, 255), # Crimson visor
    'Y': (215, 25, 25, 255),
}

# Polar Front Arctic
PAL_POLAR = {
    'X': (24, 28, 34, 255),
    'M': (240, 244, 250, 255),
    'D': (165, 178, 192, 255),
    'L': WHT,
    'C': (0, 210, 255, 255), # Ice cyan visor
    'Y': (75, 85, 98, 255),
}

# Outlander / Militia Heavy
PAL_OUTLANDER = {
    'X': (24, 26, 28, 255),
    'M': (68, 72, 76, 255),
    'D': (44, 48, 52, 255),
    'L': (110, 118, 126, 255),
    'C': (255, 200, 0, 255), # Yellow/amber periscope
    'Y': (190, 60, 40, 255),
}

# Salvage Scrap
PAL_SALVAGE = {
    'X': (28, 22, 20, 255),
    'M': (95, 85, 78, 255),
    'D': (135, 72, 42, 255), # Rust
    'L': (150, 138, 128, 255),
    'C': (255, 195, 0, 255),
    'Y': (255, 200, 0, 255),
}

# Shiden East-Asian Corps
PAL_SHIDEN = {
    'X': (20, 24, 28, 255),
    'M': (48, 58, 62, 255),
    'D': (32, 40, 44, 255),
    'L': (85, 102, 110, 255),
    'C': GLD,
    'Y': WHT,
}

# Khamsin Desert Long-Range
PAL_KHAMSIN = {
    'X': (30, 26, 22, 255),
    'M': (180, 150, 105, 255),
    'D': (120, 95, 65, 255),
    'L': (215, 190, 145, 255),
    'C': (195, 90, 50, 255), # Terracotta
    'Y': (225, 200, 155, 255),
}

# Riverine Amphibious Corps
PAL_RIVERINE = {
    'X': (20, 25, 20, 255),
    'M': (65, 78, 52, 255),
    'D': (42, 52, 34, 255),
    'L': (98, 116, 78, 255),
    'C': (0, 190, 240, 255), # Water cyan
    'Y': (240, 190, 25, 255), # Yellow gasket
}

# Specter Stealth PMC
PAL_SPECTER = {
    'X': (16, 18, 22, 255),
    'M': (32, 34, 40, 255),
    'D': (48, 42, 58, 255), # Deep radar purple
    'L': (70, 75, 88, 255),
    'C': (180, 90, 255, 255), # Stealth purple/cyan
    'Y': (0, 225, 255, 255),
}

# Valkyrie High-Mobility
PAL_VALKYRIE = {
    'X': (22, 26, 32, 255),
    'M': (240, 245, 250, 255),
    'D': (155, 168, 185, 255),
    'L': WHT,
    'C': (0, 225, 255, 255),
    'Y': GLD,
}

# Police Riot
PAL_POLICE = {
    'X': (18, 20, 26, 255),
    'M': (30, 42, 60, 255),
    'D': (18, 26, 38, 255),
    'L': (70, 95, 135, 255),
    'C': (0, 180, 255, 255),
    'Y': (225, 30, 30, 255), # Red strobe
}

# Disaster Rescue
PAL_RESCUE = {
    'X': (26, 22, 20, 255),
    'M': (245, 115, 20, 255), # Emergency orange
    'D': (175, 70, 12, 255),
    'L': (255, 160, 60, 255),
    'C': (255, 235, 50, 255), # Searchlight
    'Y': WHT,
}

# ==================== ICON SILHOUETTE TEMPLATES ====================

# 1. HELMET: Curved dome, distinct visor eye slit, cheek/ear guards with open bottom
ART_HELMET = """
................
.....XXXXXX.....
...XXMLLLLMXX...
..XMLLLLLLLLMX..
..XMMMMMMMMMMX..
..XMMMMMMMMMMX..
.XXDDDDDDDDDDXX.
.XMMCCCCCCCCMMX.
.XMMDDDDDDDDMMX.
.XMLX......XLMX.
.XMLX......XLMX.
.XMMX......XMMX.
..XX........XX..
................
................
................
"""

# 2. CHESTPLATE: Neck notch, shoulder straps, tapered breastplate, abdominal plates, waist belt
ART_CHEST = """
................
.XX..........XX.
XMMX..XXXX..XMMX
XMMXXXXMMXXXXMMX
XMLLMMMMMMMMLLMX
XMMMDDDDDDDDMMMX
.XMMDDDDDDDDMMX.
.XMMDMMMMMMDMMX.
.XMMMDDDDDDMMMX.
..XMMMMMMMMMMX..
..XMMMMMMMMMMX..
...XDDDDDDDDX...
...XXXXXXXXXX...
................
................
................
"""

# 3. PAULDRONS / ARMS: Two distinct curved shoulder bells with arm plates
ART_ARMS = """
................
..XXXX....XXXX..
.XMLLMX..XMLLMX.
XMLLLLMXXMLLLLMX
XMMDDMMXXMMDDMMX
XMDDDDXXXXDDDDMX
.XDDDDX..XDDDDX.
..XXXX....XXXX..
..XMMX....XMMX..
.XMLLMX..XMLLMX.
.XMDDMX..XMDDMX.
.XMDDMX..XMDDMX.
.XDDDDX..XDDDDX.
..XXXX....XXXX..
................
................
"""

# 4. LEGS / GREAVES: Waist harness belt + two separate mechanical legs with gap and boots
ART_LEGS = """
................
..XXXXXXXXXX....
.XMLLLLLLLLMX...
.XMMDDDDDDMMX...
.XMMX....XMMX...
.XMMX....XMMX...
.XMLLX..XMLLX...
.XMDDX..XMDDX...
.XMDDX..XMDDX...
.XMLLX..XMLLX...
.XMMMX..XMMMX...
.XDDDX..XDDDX...
XDDDDDX.XDDDDDX.
XXXXXXX.XXXXXXX.
................
................
"""

# 5. ROLL CAGE: Yellow tubular roll cage with internal cross-bracing
ART_ROLL_CAGE = """
................
...XXXXXXXXXX...
..XYYYYYYYYYYX..
..XYXXXXXXXXYX..
..XYX......XYX..
..XYX..XX..XYX..
..XYX.XDDX.XYX..
..XYXXDDDDXXYX..
..XYXDDDDDDXYX..
..XYX..XX..XYX..
..XYX......XYX..
..XYXXXXXXXXYX..
.XYYYYYYYYYYYYX.
.XXXXXXXXXXXXXX.
................
................
"""

# 6. ROLE WEAPONS (exoframe hand weapons are rendered from the model, see WEAPON_ICONS)


ART_RIOT_SHIELD = """
...XXXXXXXXXX...
..XYYYYYYYYYYX..
.XYYYYYYYYYYYYX.
.XYYCCCCCCCCYYX.
.XYYCCCCCCCCYYX.
.XYYYYYYYYYYYYX.
.XYYDDDDDDDDYYX.
.XYYDDDDDDDDYYX.
.XYYDDDDDDDDYYX.
.XYYYYYYYYYYYYX.
.XYYYYYYYYYYYYX.
..XYYYYYYYYYYX..
...XYYYYYYYYX...
....XXXXXXXX....
................
................
"""

ART_STUN_BATON = """
.............CC.
............CMMC
...........CMMMC
..........CMMMCC
.........CMMMC..
........CMMMC...
.......CMMMC....
......CMMMC.....
.....CMMMC......
....XMMMX.......
...XDDDX........
..XMMMX.........
.XDDDX..........
XMMMX...........
.XXX............
................
"""

ART_FISHING_ROD = """
..............X.
.............X..
............X...
...........X....
..........X.....
.........X......
........X.......
.......X........
......X...RR....
.....X...RRWW...
....X...RRWW....
...XDD...WW.....
..XDDDD.........
.XMMDDDX........
XMMMX.X.........
.XXX............
"""


# 7. INDUSTRIAL TOOLS
ART_MINING_DRILL = """
..............XX
............XXDD
...........XDDDD
.........XXDDDDX
.......XXDDDDDDX
.....XXDDDDDDDDX
...XXDDDDDDDDDDX
.XXDDDDDDDDDDDDX
XDDDDDDDDDDDDDDX
.XMMMDDDDDDDDXX.
.XMLLMDDDDDXX...
..XMMMMDDXX.....
...XMMMMX.......
....XXXX........
................
................
"""

ART_CHAINSAW = """
..............XX
............XXTT
..........XXTTTT
........XXTTTTTT
......XXTTTTTTXX
....XXTTTTTTXX..
..XXTTTTTTXX....
.XTTTTTTXX......
XTTTTTXX.XMMX...
.XXXXX..XMLLMX..
........XMMMMX..
.........XXXX...
................
................
................
................
"""

ART_PLOW = """
..............XX
............XXDD
...........XDDDX
.........XXDDDDX
.......XXDDDDDDX
.....XXDDDDDDDDX
...XXDDDDDDDDDDX
.XXDDDDDDDDDDDDX
XDDX...XDDDDDDDX
.XX....XDDX..XDX
.......XDX....XX
........XX......
................
................
................
................
"""

# 8. UTILITY MODULES & BACKPACKS
ART_RADIO_PACK = """
......XX........
......XX........
......XX........
...XXXXXXXXXX...
..XMLLLLLLLLMX..
..XMMMMMMMMMMX..
..XMDDDDDDDDMX..
..XMDDCCCCDDMX..
..XMDDCCCCDDMX..
..XMDDDDDDDDMX..
..XMMMMMMMMMMX..
..XMLLLLLLLLMX..
...XXXXXXXXXX...
................
................
................
"""

ART_CARGO_CRATE = """
...XXXXXXXXXX...
..XGGGGGGGGGGX..
.XGGDDDDDDDDGGX.
.XGDDDDDDDDDDGX.
.XGDXXXXXXXXDGX.
.XGDXLLLLLLXDGX.
.XGDXLLLLLLXDGX.
.XGDXLLLLLLXDGX.
.XGDXXXXXXXXDGX.
.XGDDDDDDDDDDGX.
.XGGDDDDDDDDGGX.
..XGGGGGGGGGGX..
...XXXXXXXXXX...
................
................
................
"""

ART_AMMO_PACK = """
...XXXXXXXXXX...
..XDDDDDDDDDDX..
.XDDDDDDDDDDDDX.
.XDDXXXXXXXXDDX.
.XDDXBBBBBBXDDX.
.XDDXBBBBBBXDDX.
.XDDXXXXXXXXDDX.
.XDDDDDDDDDDDDX.
.XDDDDDDDDDDDDX.
.XDDDDDDDDDDDDX.
.XDDDDDDDDDDDDX.
..XDDDDDDDDDDX..
...XXXXXXXXXX...
................
................
................
"""

ART_TARGETING_CHIP = """
.....XX..XX.....
...XXXXXXXXXX...
..XCCCCCCCCCCX..
..XCXXXXXXXXCX..
.XXCXLLLLLLXCX..
.XXCXLCCCCLXCX..
..XCXLCCCCLXCX..
..XCXLCCCCLXCX..
.XXCXLCCCCLXCX..
.XXCXLLLLLLXCX..
..XCXXXXXXXXCX..
..XCCCCCCCCCCX..
...XXXXXXXXXX...
.....XX..XX.....
................
................
"""

ART_RADAR_DISH = """
.....XXXXXX.....
....XGGGGGGX....
...XGGGGGGGGX...
..XGGGGGGGGGGX..
..XGG..CC..GGX..
...XG..CC..GX...
....XGGGGGGX....
.....XXDDXX.....
.......XX.......
.......XX.......
.......XX.......
......XXXX......
.....XMMMMX.....
.....XMMMMX.....
......XXXX......
................
"""

ART_RESCUE_WINCH = """
................
..XXXX....XXXX..
.XMMMMX..XMMMMX.
.XMMMMX..XMMMMX.
.XMMMMX..XMMMMX.
.XMMMMX..XMMMMX.
.XMMMMXXXXMMMMX.
.XMMMMXYYXMMMMX.
.XMMMMXYYXMMMMX.
..XXXXXYYXXXXX..
.....XYYYYX.....
....XDDDDDDX....
....XDDDDDDX....
.....XXXXXX.....
................
................
"""

ART_SNORKEL = """
.......XXXXXX...
......XGGGGGGX..
......XGXXXXGX..
......XGX..XGX..
......XGX.......
......XGX.......
......XGX.......
......XGX.......
......XGX.......
......XGX.......
.....XXGXX......
....XDDDDDX.....
....XDDDDDX.....
.....XXXXX......
................
................
"""

ART_ECM_JAMMER = """
..XX...XX...XX..
..XX...XX...XX..
..XX...XX...XX..
...XXXXXXXXXX...
..XCCCCCCCCCCX..
..XCPPPPPPPPPMX.
..XCPPPPPPPPPMX.
..XCPPPPPPPPPMX.
..XCPPPPPPPPPMX.
..XCPPPPPPPPPMX.
..XCPPPPPPPPPMX.
..XCPPPPPPPPPMX.
...XXXXXXXXXX...
................
................
................
"""

ART_FLOAT_RING = """
................
....XXXXXXXX....
..XXYYYYYYYYXX..
.XYYYYYYYYYYYYX.
.XYYXXXXXXXXYYX.
XYYX........XYYX
XYYX........XYYX
XYYX........XYYX
XYYX........XYYX
.XYYXXXXXXXXYYX.
.XYYYYYYYYYYYYX.
..XXYYYYYYYYXX..
....XXXXXXXX....
................
................
................
"""

ART_SEISMIC_SCANNER = """
...XXXXXXXXXX...
..XDDDDDDDDDDX..
.XDDDDDDDDDDDDX.
.XDXXXXXXXXXXDX.
.XDXCCCCCCCCXDX.
.XDXC.CCCC.CXDX.
.XDXCCCC..CCXDX.
.XDXCCCCCCCCXDX.
.XDXXXXXXXXXXDX.
.XDDDDDDDDDDDDX.
.XDDDDXXXXDDDDX.
..XDDXMMMMXDDX..
...XXXXXXXXXX...
................
................
................
"""

ART_NIGHT_VISION = """
................
.XXXXXXXXXXXXXX.
XGGGGGGGGGGGGGGX
XGGXXXXXXXXXXGGX
XGXCCCCCCCCCCXGX
XGXCCCCCCCCCCXGX
XGXCCCCCCCCCCXGX
XGGXXXXXXXXXXGGX
.XXXXXXXXXXXXXX.
....XDDDDDDX....
....XDDDDDDX....
.....XXXXXX.....
................
................
................
................
"""

ART_BALLAST_TANKS = """
...XXXX..XXXX...
..XDDDDXXDDDDX..
..XDDDDXXDDDDX..
..XDLLDXXDLLDX..
..XDLLDXXDLLDX..
..XDLLDXXDLLDX..
..XDDDDXXDDDDX..
..XDDDDXXDDDDX..
..XDDDDXXDDDDX..
..XDDDDXXDDDDX..
...XXXX..XXXX...
.....XX..XX.....
......XXXX......
................
................
................
"""

ART_SHIELDS_MISS_POD = """
...XXXXXXXXXX...
..XDDDDDDDDDDX..
.XDXXDDDDDDXXDX.
.XDRRXDDDDXRRXDX
.XDRRXDDDDXRRXDX
.XDDDDDDDDDDDDDX
.XDDDDDDDDDDDDDX
.XDXXDDDDDDXXDX.
.XDRRXDDDDXRRXDX
.XDRRXDDDDXRRXDX
.XDDDDDDDDDDDDDX
..XDDDDDDDDDDX..
...XXXXXXXXXX...
................
................
................
"""

# 9. AMMUNITION
ART_AMMO_BELT = """
................
.XX..XX..XX..XX.
XBBXXBBXXBBXXBBX
XBBXXBBXXBBXXBBX
XBBXXBBXXBBXXBBX
XBBXXBBXXBBXXBBX
XBBXXBBXXBBXXBBX
.XX..XX..XX..XX.
.XX..XX..XX..XX.
XDDXXDDXXDDXXDDX
XDDXXDDXXDDXXDDX
.XX..XX..XX..XX.
................
................
................
................
"""

ART_SHELL_BIG = """
......XXXX......
.....XCCCCX.....
....XCCCCCCX....
....XCCCCCCX....
....XDDDDDDX....
....XDDDDDDX....
....XDDDDDDX....
....XDDDDDDX....
....XBBBBBBX....
....XBBBBBBX....
....XBBBBBBX....
....XBBBBBBX....
...XBBBBBBBBX...
...XXXXXXXXXX...
................
................
"""

ART_SHOTGUN_SLUG = """
......XXXX......
.....XRRRRX.....
....XRRRRRRX....
....XRRRRRRX....
....XRRRRRRX....
....XRRRRRRX....
....XRRRRRRX....
....XRRRRRRX....
....XBBBBBBX....
....XBBBBBBX....
....XBBBBBBX....
...XBBBBBBBBX...
...XXXXXXXXXX...
................
................
................
"""

ART_ROCKET_AMMO = """
.......XX.......
......XGGX......
.....XGGGGX.....
....XGGGGGGX....
....XGGGGGGX....
....XDDDDDDX....
....XDDDDDDX....
....XDDDDDDX....
....XDDDDDDX....
....XDDDDDDX....
....XDDDDDDX....
...XXDDDDDDXX...
..XDDDDDDDDDDX..
..XXXXXXXXXXXX..
................
................
"""

ART_MISSILE_AMMO = """
.......XX.......
......XCCX......
.....XCCCCX.....
....XDDDDDDX....
....XDDDDDDX....
....XDDDDDDX....
....XDDDDDDX....
....XDDDDDDX....
....XDDDDDDX....
...XXDDDDDDXX...
..XDDDDDDDDDDX..
..XDDDDDDDDDDX..
...XX..XX..XX...
.......XX.......
................
................
"""

ART_NAPALM_CAN = """
......XXXX......
.....XRRRRX.....
....XRRRRRRX....
...XRRRRRRRRX...
...XRRXXXXRRX...
...XRRYYYYRRX...
...XRYYYYYYRX...
...XRYYYYYYRX...
...XRRYYYYRRX...
...XRRXXXXRRX...
...XRRRRRRRRX...
....XRRRRRRX....
.....XXXXXX.....
................
................
................
"""

# 10. CRAFTING MATERIALS
ART_CRATE_KIT = """
...XXXXXXXXXX...
..XGGGGGGGGGGX..
.XGGDDDDDDDDGGX.
.XGDDDDDDDDDDGX.
.XGDXXXXXXXXDGX.
.XGDXLLLLLLXDGX.
.XGDXLLLLLLXDGX.
.XGDXXXXXXXXDGX.
.XGDDDDDDDDDDGX.
.XGGDDDDDDDDGGX.
..XGGGGGGGGGGX..
...XXXXXXXXXX...
................
................
................
................
"""

ART_HYDRAULIC = """
..............XX
............XXCC
...........XCCCC
.........XXCCCCX
.......XXCCCCXX.
.....XXDDDDXX...
...XXDDDDDDX....
..XDDDDDDDDX....
.XDDDDDDDDDX....
.XDDDDDDDDDX....
.XXDDDDDDDDX....
...XXXXXXXX.....
................
................
................
................
"""

ART_SERVO = """
.....XXXXXX.....
....XDDDDDDX....
...XDDDDDDDDX...
..XDDDDDDDDDDX..
..XDDCCCCCCDDX..
.XDDCMMMMMMCDDX.
.XDDCMMLLMMCDDX.
.XDDCMMLLMMCDDX.
.XDDCMMMMMMCDDX.
..XDDCCCCCCDDX..
..XDDDDDDDDDDX..
...XDDDDDDDDX...
....XDDDDDDX....
.....XXXXXX.....
................
................
"""

ART_ARMOR_PLATE = """
.XXXXXXXXXXXXXX.
XLLLLLLLLLLLLLLX
XLCCLLLLLLLLCCLX
XLCCLLLLLLLLCCLX
XLLLLLLLLLLLLLLX
XLLLLLLLLLLLLLLX
XLLLLLLLLLLLLLLX
XLLLLLLLLLLLLLLX
XLLLLLLLLLLLLLLX
XLLLLLLLLLLLLLLX
XLCCLLLLLLLLCCLX
XLCCLLLLLLLLCCLX
XLLLLLLLLLLLLLLX
.XXXXXXXXXXXXXX.
................
................
"""

ART_PEDDLER_CORE = """
.....XXXXXX.....
....XCCCCCCX....
...XCYYYYYYCX...
..XCY......YCX..
..XCY..CC..YCX..
.XCY..CCCC..YCX.
.XCY.CCCCCC.YCX.
.XCY.CCCCCC.YCX.
.XCY..CCCC..YCX.
..XCY..CC..YCX..
..XCY......YCX..
...XCYYYYYYCX...
....XCCCCCCX....
.....XXXXXX.....
................
................
"""

ART_ASSEMBLY_STATION = """
...XXXXXXXXXX...
..XYYYYYYYYYYX..
.XYXDDDDDDDDXYX.
.XYXDDDDDDDDXYX.
.XYXXXXXXXXXXYX.
.XYX........XYX.
.XYX........XYX.
.XYX........XYX.
.XYXXXXXXXXXXYX.
.XYXDDDDDDDDXYX.
.XYYYYYYYYYYYYX.
..XXXXXXXXXXXX..
................
................
................
................
"""

ART_ROLLER_DASH = """
................
................
....XXXXXXXX....
...XMMMMMMMMX...
...XMYYMMYYMX...
...XXXXXXXXXX...
..XXXX.XX.XXXX..
.XRRRRX..XRRRRX.
XRRDDRRXXRRDDRRX
XRDLLDRXXRDLLDRX
XRDLLDRXXRDLLDRX
XRRDDRRXXRRDDRRX
.XRRRRX..XRRRRX.
..XXXX....XXXX..
................
................
"""

ART_HYDRO_JET = """
................
..XXXX....XXXX..
.XOOOOX..XOOOOX.
.XXXXXX..XXXXXX.
XMMMMMMXXMMMMMMX
XMXXXXMXXMXXXXMX
XMXCLXMXXMXCLXMX
XMXLCXMXXMXLCXMX
XMXXXXMXXMXXXXMX
XMMMMMMXXMMMMMMX
.XDDDDX..XDDDDX.
..XDDX....XDDX..
..XCCX....XCCX..
...XX......XX...
................
................
"""

# Map All 87 Items to Specific Arts & Palettes
ICONS_MAP = [
    # 1. Helmets (14)
    ("armor_sand_head.png", ART_HELMET, PAL_SAND),
    ("armor_usmc_head.png", ART_HELMET, PAL_USMC),
    ("armor_cerberus_head.png", ART_HELMET, PAL_CERBERUS),
    ("armor_polar_head.png", ART_HELMET, PAL_POLAR),
    ("armor_militia_hood.png", ART_HELMET, PAL_OUTLANDER),
    ("armor_salvage_head.png", ART_HELMET, PAL_SALVAGE),
    ("armor_shiden_head.png", ART_HELMET, PAL_SHIDEN),
    ("armor_khamsin_head.png", ART_HELMET, PAL_KHAMSIN),
    ("armor_riverine_head.png", ART_HELMET, PAL_RIVERINE),
    ("armor_specter_head.png", ART_HELMET, PAL_SPECTER),
    ("armor_valkyrie_head.png", ART_HELMET, PAL_VALKYRIE),
    ("armor_police_head.png", ART_HELMET, PAL_POLICE),
    ("armor_rescue_head.png", ART_HELMET, PAL_RESCUE),
    ("armor_votoms_head.png", ART_HELMET, PAL_USMC),

    # 2. Chestpieces (14)
    ("armor_sand_chest.png", ART_CHEST, PAL_SAND),
    ("armor_usmc_chest.png", ART_CHEST, PAL_USMC),
    ("armor_cerberus_chest.png", ART_CHEST, PAL_CERBERUS),
    ("armor_arctic_chest.png", ART_CHEST, PAL_POLAR),
    ("armor_militia_chest.png", ART_CHEST, PAL_OUTLANDER),
    ("armor_roll_cage.png", ART_ROLL_CAGE, {'.': _, 'X': BLK, 'Y': YEL, 'D': DKG}),
    ("armor_salvage_chest.png", ART_CHEST, PAL_SALVAGE),
    ("armor_shiden_chest.png", ART_CHEST, PAL_SHIDEN),
    ("armor_khamsin_chest.png", ART_CHEST, PAL_KHAMSIN),
    ("armor_riverine_chest.png", ART_CHEST, PAL_RIVERINE),
    ("armor_specter_chest.png", ART_CHEST, PAL_SPECTER),
    ("armor_valkyrie_chest.png", ART_CHEST, PAL_VALKYRIE),
    ("armor_police_chest.png", ART_CHEST, PAL_POLICE),
    ("armor_rescue_chest.png", ART_CHEST, PAL_RESCUE),

    # 3. Arms / Pauldrons (12)
    ("armor_sand_arms.png", ART_ARMS, PAL_SAND),
    ("armor_usmc_arms.png", ART_ARMS, PAL_USMC),
    ("armor_cerberus_arms.png", ART_ARMS, PAL_CERBERUS),
    ("armor_polar_arms.png", ART_ARMS, PAL_POLAR),
    ("armor_outlander_arms.png", ART_ARMS, PAL_OUTLANDER),
    ("armor_salvage_arms.png", ART_ARMS, PAL_SALVAGE),
    ("armor_shiden_arms.png", ART_ARMS, PAL_SHIDEN),
    ("armor_khamsin_arms.png", ART_ARMS, PAL_KHAMSIN),
    ("armor_riverine_arms.png", ART_ARMS, PAL_RIVERINE),
    ("armor_specter_arms.png", ART_ARMS, PAL_SPECTER),
    ("armor_valkyrie_arms.png", ART_ARMS, PAL_VALKYRIE),
    ("armor_red_shoulder_arms.png", ART_ARMS, {**PAL_USMC, 'M': (180, 35, 30, 255), 'L': (220, 50, 45, 255)}),

    # 4. Legs / Greaves (11)
    ("armor_sand_legs.png", ART_LEGS, PAL_SAND),
    ("armor_usmc_legs.png", ART_LEGS, PAL_USMC),
    ("armor_cerberus_legs.png", ART_LEGS, PAL_CERBERUS),
    ("armor_polar_legs.png", ART_LEGS, PAL_POLAR),
    ("armor_outlander_legs.png", ART_LEGS, PAL_OUTLANDER),
    ("armor_salvage_legs.png", ART_LEGS, PAL_SALVAGE),
    ("armor_shiden_legs.png", ART_LEGS, PAL_SHIDEN),
    ("armor_khamsin_legs.png", ART_LEGS, PAL_KHAMSIN),
    ("armor_riverine_legs.png", ART_LEGS, PAL_RIVERINE),
    ("armor_specter_legs.png", ART_LEGS, PAL_SPECTER),
    ("armor_valkyrie_legs.png", ART_LEGS, PAL_VALKYRIE),

    # 5. Role weapons (exoframe hand weapons are rendered from the model, see WEAPON_ICONS)
    ("exoframe_riot_shield.png", ART_RIOT_SHIELD, {'.': _, 'X': BLK, 'Y': (30, 42, 60, 255), 'C': CYN, 'D': DKG}),
    ("exoframe_stun_baton.png", ART_STUN_BATON, {'.': _, 'X': BLK, 'M': DKG, 'D': GRY, 'C': CYN}),
    ("exoframe_fishing_rod.png", ART_FISHING_ROD, {'.': _, 'X': BLK, 'M': DKG, 'D': GRY, 'R': RED, 'W': WHT}),

    # 6. Industrial Tools (3)
    ("tool_mining_drill.png", ART_MINING_DRILL, {'.': _, 'X': BLK, 'D': (220, 190, 40, 255), 'M': DKG, 'L': WHT}),
    ("tool_chainsaw.png", ART_CHAINSAW, {'.': _, 'X': BLK, 'T': GRY, 'M': (225, 115, 20, 255), 'L': WHT}),
    ("tool_cultivator_plow.png", ART_PLOW, {'.': _, 'X': BLK, 'D': (70, 110, 50, 255), 'M': DKG, 'L': WHT}),

    # 7. Utility Modules & Backpacks (19)
    ("armor_float_ring.png", ART_FLOAT_RING, {'.': _, 'X': BLK, 'Y': ORG}),
    ("module_cargo_crate.png", ART_CARGO_CRATE, {'.': _, 'X': BLK, 'G': (68, 82, 58, 255), 'D': (44, 54, 38, 255), 'L': (98, 118, 84, 255)}),
    ("module_agri_hopper.png", ART_CARGO_CRATE, {'.': _, 'X': BLK, 'G': (120, 80, 45, 255), 'D': (80, 50, 25, 255), 'L': (160, 110, 60, 255)}),
    ("module_cerberus_packs.png", ART_AMMO_PACK, {'.': _, 'X': BLK, 'D': (36, 40, 46, 255), 'B': (215, 25, 25, 255)}),
    ("module_diving_ballast.png", ART_BALLAST_TANKS, {'.': _, 'X': BLK, 'D': (225, 205, 30, 255), 'L': WHT}),
    ("module_geological_scanner.png", ART_SEISMIC_SCANNER, {'.': _, 'X': BLK, 'D': DKG, 'C': YEL, 'M': GLD}),
    ("module_khamsin_filters.png", ART_BALLAST_TANKS, {'.': _, 'X': BLK, 'D': (180, 150, 105, 255), 'L': (225, 200, 155, 255)}),
    ("module_night_vision_optic.png", ART_NIGHT_VISION, {'.': _, 'X': BLK, 'G': DKG, 'C': (50, 240, 80, 255), 'D': GRY}),
    ("module_rescue_winch.png", ART_RESCUE_WINCH, {'.': _, 'X': BLK, 'M': GRY, 'Y': YEL, 'D': DKG}),
    ("module_riverine_snorkel.png", ART_SNORKEL, {'.': _, 'X': BLK, 'G': (65, 78, 52, 255), 'D': DKG}),
    ("module_salvage_scraps.png", ART_ARMOR_PLATE, {'.': _, 'X': BLK, 'L': (135, 72, 42, 255), 'C': YEL}),
    ("module_search_radar.png", ART_RADAR_DISH, {'.': _, 'X': BLK, 'G': GLD, 'C': CYN, 'D': GRY, 'M': DKG}),
    ("module_shiden_crest.png", ART_TARGETING_CHIP, {'.': _, 'X': BLK, 'C': GLD, 'L': (48, 58, 62, 255)}),
    ("module_shoulder_missile.png", ART_SHIELDS_MISS_POD, {'.': _, 'X': BLK, 'D': (68, 82, 58, 255), 'R': RED}),
    ("module_twin_manpads.png", ART_SHIELDS_MISS_POD, {'.': _, 'X': BLK, 'D': (44, 54, 38, 255), 'R': (240, 190, 20, 255)}),
    ("module_specter_ecm.png", ART_ECM_JAMMER, {'.': _, 'X': BLK, 'C': CYN, 'P': (160, 70, 240, 255), 'M': (32, 34, 40, 255)}),
    ("module_targeting_computer.png", ART_TARGETING_CHIP, {'.': _, 'X': BLK, 'C': (40, 180, 80, 255), 'L': CYN}),
    ("module_usmc_comms.png", ART_RADIO_PACK, {'.': _, 'X': BLK, 'M': (68, 82, 58, 255), 'D': (44, 54, 38, 255), 'L': (98, 118, 84, 255), 'C': CYN}),
    ("module_valkyrie_sensor.png", ART_TARGETING_CHIP, {'.': _, 'X': BLK, 'C': CYN, 'L': GLD}),
    ("module_roller_dash.png", ART_ROLLER_DASH, {'.': _, 'X': BLK, 'M': (88, 96, 104, 255), 'Y': YEL, 'R': (30, 30, 32, 255), 'D': GRY, 'L': WHT}),
    ("module_hydro_jet.png", ART_HYDRO_JET, {'.': _, 'X': BLK, 'O': ORG, 'M': (88, 96, 104, 255), 'C': CYN, 'L': WHT, 'D': DKG}),

    # 8. Ammunition (10)
    ("ammo_762_minigun.png", ART_AMMO_BELT, {'.': _, 'X': BLK, 'B': BRS, 'D': (160, 120, 30, 255)}),
    ("ammo_20mm.png", ART_AMMO_BELT, {'.': _, 'X': BLK, 'B': (220, 180, 50, 255), 'D': (170, 130, 35, 255)}),
    ("ammo_30mm_autocannon.png", ART_SHELL_BIG, {'.': _, 'X': BLK, 'C': (30, 120, 220, 255), 'D': GRY, 'B': BRS}),
    ("ammo_shotgun_slug.png", ART_SHOTGUN_SLUG, {'.': _, 'X': BLK, 'R': RED, 'B': BRS}),
    ("ammo_40mm_grenade.png", ART_SHELL_BIG, {'.': _, 'X': BLK, 'C': (220, 180, 30, 255), 'D': (68, 82, 58, 255), 'B': BRS}),
    ("ammo_84mm_rocket.png", ART_ROCKET_AMMO, {'.': _, 'X': BLK, 'G': (68, 82, 58, 255), 'D': (44, 54, 38, 255)}),
    ("ammo_atgm_missile.png", ART_MISSILE_AMMO, {'.': _, 'X': BLK, 'C': CYN, 'D': (220, 225, 235, 255)}),
    ("ammo_napalm_canister.png", ART_NAPALM_CAN, {'.': _, 'X': BLK, 'R': RED, 'Y': YEL}),
    ("ammo_rocket.png", ART_ROCKET_AMMO, {'.': _, 'X': BLK, 'G': (220, 180, 30, 255), 'D': (68, 82, 58, 255)}),
    ("ammo_rpg_warhead.png", ART_ROCKET_AMMO, {'.': _, 'X': BLK, 'G': (68, 82, 58, 255), 'D': (130, 85, 40, 255)}),

    # 9. Crafting Materials & Stations (9)
    ("exoframe_kit.png", ART_CRATE_KIT, {'.': _, 'X': BLK, 'G': (68, 82, 58, 255), 'D': (44, 54, 38, 255), 'L': (98, 118, 84, 255)}),
    ("exoframe_kit_salvage.png", ART_CRATE_KIT, {'.': _, 'X': BLK, 'G': (135, 72, 42, 255), 'D': (90, 45, 25, 255), 'L': (180, 100, 60, 255)}),
    ("exoframe_kit_advanced.png", ART_CRATE_KIT, {'.': _, 'X': BLK, 'G': (36, 40, 46, 255), 'D': (24, 26, 30, 255), 'L': CYN}),
    ("exoframe_kit_elite.png", ART_CRATE_KIT, {'.': _, 'X': BLK, 'G': (240, 245, 250, 255), 'D': (160, 170, 180, 255), 'L': GLD}),
    ("hydraulic_cylinder.png", ART_HYDRAULIC, {'.': _, 'X': BLK, 'C': WHT, 'D': (80, 90, 100, 255)}),
    ("servo_motor.png", ART_SERVO, {'.': _, 'X': BLK, 'D': DKG, 'C': COP, 'M': (70, 80, 95, 255), 'L': WHT}),
    ("reinforced_steel_plate.png", ART_ARMOR_PLATE, {'.': _, 'X': BLK, 'L': (150, 160, 175, 255), 'C': (80, 90, 105, 255)}),
    ("peddler_core.png", ART_PEDDLER_CORE, {'.': _, 'X': BLK, 'C': (35, 40, 48, 255), 'Y': GLD}),
    ("mech_assembly_station.png", ART_ASSEMBLY_STATION, {'.': _, 'X': BLK, 'Y': YEL, 'D': DKG}),
]

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src/main/resources/assets/obsolete/textures/item"))

# ==================== WEAPON ICONS RENDERED FROM THE MODEL ====================
# Exoframe weapon icons are drawn from the weapon bones of exoframe.geo.json (left-side orthographic view, tilted
# 30 degrees muzzle-up, muzzle to the right), coloured by tools/weapon_materials.json, so an icon always matches its in-game model.
HERE = os.path.dirname(__file__)
GEO = os.path.join(HERE, "..", "src/main/resources/assets/obsolete/geo/exoframe.geo.json")
WEAPON_ICONS = {   # item texture -> weapon bone
    "exoframe_assault_rifle.png": "weapon_assault_rifle", "exoframe_sniper_rifle.png": "weapon_sniper_amr",
    "exoframe_machine_gun.png": "weapon_machine_gun", "exoframe_minigun.png": "weapon_minigun_m134",
    "exoframe_rocket_launcher.png": "weapon_rocket_launcher", "exoframe_rpg7.png": "weapon_rpg7_heavy",
    "exoframe_battle_rifle.png": "weapon_battle_rifle", "exoframe_autocannon_30mm.png": "weapon_autocannon_30mm",
    "exoframe_shotgun_breacher.png": "weapon_shotgun_breacher", "exoframe_grenade_launcher.png": "weapon_grenade_launcher",
    "exoframe_recoilless_rifle.png": "weapon_recoilless_rifle", "exoframe_atgm_guided.png": "weapon_atgm_guided",
    "exoframe_flamethrower.png": "weapon_flamethrower", "exoframe_vibro_blade.png": "weapon_vibro_blade",
    "exoframe_antitank_rifle.png": "weapon_antitank_rifle", "exoframe_pile_bunker.png": "weapon_pile_bunker",
    "exoframe_smoke_launcher.png": "weapon_smoke_launcher",
}
ICON_COLORS = {
    "gunmetal": (70, 74, 80), "blued": (52, 58, 74), "steel": (150, 156, 164), "chrome": (205, 210, 216), "heat": (112, 92, 84),
    "paint": (92, 102, 70), "ammo_can": (84, 94, 62), "fuel": (168, 44, 34), "warhead": (92, 102, 66), "mag": (64, 66, 70),
    "wood": (138, 82, 42), "polymer": (40, 40, 42), "rubber": (30, 30, 30), "fabric": (110, 102, 74), "brass": (214, 172, 66),
    "copper": (186, 106, 54), "rail": (58, 62, 70), "optic": (34, 36, 40), "lens": (50, 140, 220), "lens_g": (50, 190, 110),
    "hazard": (236, 192, 30), "perforated": (60, 64, 70), "shells": (186, 36, 30), "smoke": (196, 198, 190), "ember": (255, 170, 40),
    "glow": (70, 230, 255), "blade_edge": (230, 234, 240),
}


def render_weapon_icon(bone_name, geo_bones, materials, tilt=math.radians(-30), ss=4):
    cubes = next(b for b in geo_bones if b["name"] == bone_name)["cubes"]
    mats = materials[bone_name]
    boxes = [(c["origin"], c["size"], mats[i]) for i, c in enumerate(cubes)]
    zs = [o[2] for o, s, m in boxes] + [o[2] + s[2] for o, s, m in boxes]
    ys = [o[1] for o, s, m in boxes] + [o[1] + s[1] for o, s, m in boxes]
    ct, st = math.cos(tilt), math.sin(tilt)
    # screen: u runs muzzle-ward (-z) and up, v runs down
    corners = [(-z * ct + y * st, -(z * st + y * ct)) for z in zs for y in ys]
    umin, umax = min(c[0] for c in corners), max(c[0] for c in corners)
    vmin, vmax = min(c[1] for c in corners), max(c[1] for c in corners)
    scale = 14.0 / max(umax - umin, vmax - vmin)
    uc, vc = (umin + umax) / 2, (vmin + vmax) / 2
    grid = [[None] * 16 for _ in range(16)]
    for py in range(16):
        for px in range(16):
            acc = []
            for sy in range(ss):
                for sx in range(ss):
                    u = (px + (sx + 0.5) / ss - 8) / scale + uc
                    v = (py + (sy + 0.5) / ss - 8) / scale + vc
                    z = -(u * ct - (-v) * st)        # invert the tilt
                    y = u * st + (-v) * ct
                    best = None
                    for o, s, m in boxes:
                        if o[2] <= z <= o[2] + s[2] and o[1] <= y <= o[1] + s[1]:
                            near = o[0] + s[0]       # seen from the left (+x) side
                            if best is None or near > best[0]:
                                best = (near, m, (y - o[1]) / max(s[1], 1e-3))
                    if best:
                        acc.append((best[1], 1.15 - 0.35 * (1 - best[2])))   # (material, light from above)
            if len(acc) >= ss * ss * 0.35:
                mat = max(set(m for m, _ in acc), key=lambda m: sum(1 for a, _ in acc if a == m))   # crisp material edges
                k = sum(l for m, l in acc if m == mat) / sum(1 for m, _ in acc if m == mat)
                grid[py][px] = tuple(min(255, int(c * k)) for c in ICON_COLORS.get(mat, (90, 90, 90))) + (255,)
    out = [[grid[y][x] or (0, 0, 0, 0) for x in range(16)] for y in range(16)]
    for y in range(16):        # dark outline around the silhouette
        for x in range(16):
            if grid[y][x] is None and any(0 <= y + dy < 16 and 0 <= x + dx < 16 and grid[y + dy][x + dx]
                                          for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0))):
                out[y][x] = BLK
    return out


if __name__ == "__main__":
    import json
    print(f"Generating item icons into {OUT_DIR}...")
    os.makedirs(OUT_DIR, exist_ok=True)
    for fname, art, pal in ICONS_MAP:
        grid = parse_ascii_art(art, pal)
        png_bytes = create_png_16x16(grid)
        target = os.path.join(OUT_DIR, fname)
        with open(target, "wb") as f:
            f.write(png_bytes)
    geo_bones = json.load(open(GEO, encoding="utf-8"))["minecraft:geometry"][0]["bones"]
    materials = json.load(open(os.path.join(HERE, "weapon_materials.json"), encoding="utf-8"))
    for fname, bone in WEAPON_ICONS.items():
        with open(os.path.join(OUT_DIR, fname), "wb") as f:
            f.write(create_png_16x16(render_weapon_icon(bone, geo_bones, materials)))
    print(f"Wrote {len(ICONS_MAP)} ASCII icons and {len(WEAPON_ICONS)} model-rendered weapon icons.")
