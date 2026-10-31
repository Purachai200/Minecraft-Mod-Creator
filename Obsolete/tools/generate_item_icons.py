"""
Generates distinct 16x16 item icons for all OBSOLETE mecha mod items.
Pure Python - zero external dependencies.
"""
import struct
import zlib
import os

def create_png_16x16(pixel_grid):
    """Encodes a 16x16 array of RGBA tuples into a valid PNG byte string."""
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
        grid.append([palette[ch] for ch in chars])
    return grid

# ==================== COMMON PALETTES ====================
_ = (0, 0, 0, 0) # Transparent
BLK = (20, 22, 24, 255)
WHT = (245, 248, 252, 255)
CYN = (40, 220, 255, 255)
YEL = (255, 204, 0, 255)
RED = (220, 40, 35, 255)
GLD = (218, 175, 45, 255)
ORG = (255, 130, 20, 255)

# Polar
P_OUT = (24, 28, 32, 255)
P_WHT = (242, 246, 250, 255)
P_GRY = (170, 180, 192, 255)
P_DKG = (72, 80, 92, 255)
P_CYN = (0, 220, 255, 255)
P_YEL = (255, 215, 0, 255)
P_RED = (225, 35, 30, 255)

# Outlander
O_OUT = (26, 28, 30, 255)
O_MET = (72, 76, 80, 255)
O_DKM = (46, 48, 52, 255)
O_HIL = (120, 128, 136, 255)
O_RIV = (215, 225, 235, 255)

# MANPADS
M_OUT = (22, 24, 26, 255)
M_OLV = (68, 78, 58, 255)
M_DKO = (44, 52, 38, 255)
M_OPT = (0, 255, 200, 255)

# Salvage (Scrap Militia)
S_OUT = (28, 24, 22, 255)
S_IRN = (88, 82, 76, 255)
S_RST = (145, 75, 42, 255)
S_DKR = (90, 48, 28, 255)
S_YEL = (255, 204, 0, 255)

# Shiden (East-Asian Heavy Corps)
SH_OUT = (22, 26, 28, 255)
SH_NAV = (52, 60, 56, 255)
SH_LGT = (85, 96, 92, 255)
SH_GLD = (218, 175, 45, 255)
SH_WHT = (235, 240, 245, 255)

# Khamsin (Desert Long-Range Guard)
K_OUT = (32, 28, 24, 255)
K_OCH = (186, 154, 108, 255)
K_SND = (222, 196, 155, 255)
K_TER = (142, 86, 62, 255)
K_DKT = (95, 55, 40, 255)

# Riverine (Amphibious Corps)
R_OUT = (22, 26, 20, 255)
R_MOS = (68, 78, 52, 255)
R_LGT = (98, 114, 76, 255)
R_GSK = (235, 185, 30, 255)
R_BLU = (40, 160, 220, 255)

# Specter (Stealth PMC)
SP_OUT = (18, 20, 22, 255)
SP_RAM = (32, 34, 38, 255)
SP_PRP = (52, 44, 62, 255)
SP_HIL = (75, 80, 92, 255)
SP_CYN = (40, 230, 220, 255)

# Valkyrie (Elite Special Forces)
V_OUT = (24, 26, 30, 255)
V_WHT = (238, 242, 248, 255)
V_SHD = (180, 190, 205, 255)
V_GLD = (220, 180, 50, 255)
V_CYN = (40, 210, 245, 255)

# Weapons
W_OUT = (20, 22, 24, 255)
W_MET = (55, 58, 64, 255)
W_DKM = (35, 38, 42, 255)
W_HIL = (110, 118, 128, 255)
W_BRS = (200, 160, 50, 255)
W_WOD = (140, 80, 40, 255)

# Role Variants Palettes
POL_OUT = (18, 22, 28, 255)
POL_NVY = (24, 32, 45, 255)
POL_LGT = (45, 60, 85, 255)
POL_BLU = (30, 120, 255, 255)
POL_RED = (230, 30, 30, 255)
POL_WHT = (245, 248, 252, 255)
POL_CYN = (20, 180, 240, 255)

RES_OUT = (28, 20, 16, 255)
RES_ORG = (255, 102, 0, 255)
RES_YEL = (255, 204, 0, 255)
RES_WHT = (245, 248, 252, 255)
RES_MET = (200, 205, 215, 255)
RES_DKM = (65, 70, 78, 255)

AMP_OUT = (24, 26, 20, 255)
AMP_ORG = (240, 150, 20, 255)
AMP_YEL = (255, 200, 30, 255)
AMP_MET = (180, 190, 200, 255)
AMP_DKM = (50, 55, 45, 255)

RAD_OUT = (20, 22, 24, 255)
RAD_GRY = (70, 75, 82, 255)
RAD_GLD = (218, 175, 45, 255)
RAD_CYN = (0, 255, 200, 255)

BAT_CYN = (0, 220, 255, 255)
ROD_MET = (180, 130, 50, 255)
ROD_RED = (225, 40, 35, 255)

# ==================== ICON ART DEFINITIONS ====================

ART_POLICE_HEAD = """
................
...BBRRRRBBRR...
...BBRRRRBBRR...
....XXXXXXXX....
...XMMMMMMMMX...
..XMMMMMMMMMMX..
.XMMCCCCCCCCMMX.
.XMMCCCCCCCCMMX.
.XMMXWWWWWWXMMX.
.XMMMMMMMMMMMMX.
.XMMXMMMMMMXMMX.
..XX.XMMMMX.XX..
.....XMMMMX.....
......XXXX......
................
................
"""

ART_POLICE_CHEST = """
................
...XXXXXXXXXX...
..XMMMMMMMMMMX..
.XMMWWWWWWWWMMX.
.XMMXWWWWWWXMMX.
XMMMMWWWWWWMMMMX
XMMDDDDDDDDDDMMX
XMMDDWWWWWWDDMMX
XMMDDWWWWWWDDMMX
.XMMMDDDDDDMMMX.
.XMMMMMMMMMMMMX.
..XMMMMMMMMMMX..
...XMMDDDDMMX...
....XMMMMMMX....
.....XXXXXX.....
................
"""

ART_RIOT_SHIELD = """
...XXXXXXXXXX...
..XMMMMMMMMMMX..
.XMMMMMMMMMMMMX.
.XMMMMMMMMMMMMX.
.XMMMMCCCCMMMMX.
.XMMMMCCCCMMMMX.
.XMMMMMMMMMMMMX.
.XMMMMWWWWMMMMX.
.XMMMMWWWWMMMMX.
.XMMMMMMMMMMMMX.
.XMMMMMMMMMMMMX.
.XMMMMMMMMMMMMX.
..XMMMMMMMMMMX..
..XMMMMMMMMMMX..
...XXXXXXXXXX...
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

ART_RESCUE_HEAD = """
................
....XXXXXXXX....
...XMMMMMMMMX...
..XYYMMMMMMYYX..
.XYYYMMMMMMYYYX.
.XYYYMMMMMMYYYX.
.XMMMMMMMMMMMMX.
.XMMMMWWWWMMMMX.
.XMMMMWWWWMMMMX.
.XMMMMMMMMMMMMX.
..XMMMMMMMMMMX..
...XMMMMMMMMX...
....XXXXXXXX....
.....XMMMMX.....
......XXXX......
................
"""

ART_RESCUE_CHEST = """
................
...XXXXXXXXXX...
..XMMMMMMMMMMX..
.XMMMMMMMMMMMMX.
.XMMMWWMMMWWMMX.
XMMMWWMMMWWMMMMX
XMMWWMMMWWMMMMMX
XMWWMMMWWMMMMMMX
XWWMMMWWMMMMMMMX
.XMMMWWMMMMMMMX.
.XMMMMMMMMMMMMX.
..XMMMMMMMMMMX..
...XMMMMMMMMX...
....XMMMMMMX....
.....XXXXXX.....
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

ART_SEARCH_RADAR = """
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

ART_GENERIC_HEAD = """
................
.....XXXXXX.....
....XMMMMMMX....
...XMMMMMMMMX...
...XMMMMMMMMX...
..XMMMMMMMMMMX..
..XMMMMMMMMMMX..
.XXDDDDDDDDDDXX.
.XMMXCCCCCCCCXMX
.XMMDDDDDDDDDDMX
X.XMMMMMMMMMMX.X
X.XMMMMMMMMMMX.X
...XMMMMMMMMX...
....XMMMMMMX....
.....XXXXXX.....
................
"""

ART_GENERIC_CHEST = """
................
...XXXXXXXXXX...
..XMMMMMMMMMMX..
.XMMMMMMMMMMMMX.
.XMMMDDDDDDMMMX.
XMMMDDYYYYDDMMMX
XMMDDYYYYYYDDMMX
XMMDDYYYYYYDDMMX
XMMMDDYYYYDDMMMX
.XMMMDDDDDDMMMX.
.XMMMMMMMMMMMMX.
..XMMMMMMMMMMX..
...XMMDDDDMMX...
....XMMMMMMX....
.....XXXXXX.....
................
"""

ART_GENERIC_ARMS = """
................
..XXXX....XXXX..
.XMMMMX..XMMMMX.
XMMMMMMXXMMMMMMX
XMMDDMMXXMMDDMMX
XMMDDMMXXMMDDMMX
.XMDDMX..XMDDMX.
..XDDX....XDDX..
..XDDX....XDDX..
.XMMMMX..XMMMMX.
.XMMMMX..XMMMMX.
.XMDDMX..XMDDMX.
.XMDDMX..XMDDMX.
XMMDDMMXXMMDDMMX
.XXXXXX..XXXXXX.
................
"""

ART_GENERIC_LEGS = """
................
.XXXX......XXXX.
XMMMMX....XMMMMX
XMMMMX....XMMMMX
XMMDDX....XMMDDX
.XMDDX....XMDDX.
..XDDX....XDDX..
..XDDX....XDDX..
.XMMMMX..XMMMMX.
.XMMMMX..XMMMMX.
.XMMDDX..XMMDDX.
.XMMDDX..XMMDDX.
XMMDDDDXXMMDDDDX
XMMDDDDXXMMDDDDX
.XXXXXX..XXXXXX.
................
"""

ART_GENERIC_MODULE = """
................
...XXXXXXXXXX...
..XMMMMMMMMMMX..
.XMMMMMMMMMMMMX.
.XMMMDDDDDDMMMX.
XMMMDDCCCCDDMMMX
XMMDDCCCCCCDDMMX
XMMDDCCCCCCDDMMX
XMMMDDCCCCDDMMMX
.XMMMDDDDDDMMMX.
.XMMMMMMMMMMMMX.
..XMMMMMMMMMMX..
...XMMDDDDMMX...
....XXXXXXXX....
................
................
"""

# Existing 6 icons
ART_POLAR_HEAD = """
................
.....XXXXXX.....
....XWDDDWGX....
...XWDDDDDDGX...
...XWWWWGGGGX...
..XWWWWWWGGGGX..
..XWWWWWWGGGGX..
.XXDDDDDDDDDDXX.
.XWWXCCCCCCCCXGX
.XWWDDDDDDDDDGGX
X.XWWWWWWGGGGX.X
X.XWWWWWWGGGGX.X
...XWWWWWWGGX...
....XWWWWGGX....
.....XXXXXX.....
................
"""
PAL_POLAR_HEAD = {'.': _, 'X': P_OUT, 'W': P_WHT, 'G': P_GRY, 'D': P_DKG, 'C': P_CYN, 'R': P_RED}

ART_POLAR_ARMS = """
................
..XXXX....XXXX..
.XWWGGX..XWWGGX.
XWWWWGGXXWWWWGGX
XWWDDGGXXWWDDGGX
XWWDDGGXXWWDDGGX
.XWDDGX..XWDDGX.
..XDDX....XDDX..
..XDDX....XDDX..
.XWWGGX..XWWGGX.
.XWWGGX..XWWGGX.
.XWDDGX..XWDDGX.
.XWDDGX..XWDDGX.
XWWDDGGXXWWDDGGX
.XXXXXX..XXXXXX.
................
"""
PAL_POLAR_ARMS = {'.': _, 'X': P_OUT, 'W': P_WHT, 'G': P_GRY, 'D': P_DKG}

ART_POLAR_LEGS = """
................
.XXXX......XXXX.
XWWGGX....XWWGGX
XWWGGX....XWWGGX
XWWDDX....XWWDDX
.XWDDX....XWDDX.
..XDDX....XDDX..
..XDDX....XDDX..
.XWWGGX..XWWGGX.
.XWWGGX..XWWGGX.
.XWWDDX..XWWDDX.
.XWWDDX..XWWDDX.
XWWDDDDXXWWDDDDX
XWWDDDDXXWWDDDDX
.XXXXXX..XXXXXX.
................
"""
PAL_POLAR_LEGS = {'.': _, 'X': P_OUT, 'W': P_WHT, 'G': P_GRY, 'D': P_DKG}

ART_OUTLANDER_ARMS = """
................
..XXXX....XXXX..
.XHHHMX..XHHHMX.
XHHHHMMXXHHHHMMX
XHRRDMMXXHRRDMMX
XHRRDMMXXHRRDMMX
.XMDDMX..XMDDMX.
..XDDX....XDDX..
..XDDX....XDDX..
.XHHHMX..XHHHMX.
.XHMMDDX.XHMMDDX
.XHRRDMX.XHRRDMX
.XMDDDMX.XMDDDMX
XHHMDDMXXHHMDDMX
.XXXXXX..XXXXXX.
................
"""
PAL_OUTLANDER_ARMS = {'.': _, 'X': O_OUT, 'H': O_HIL, 'M': O_MET, 'D': O_DKM, 'R': O_RIV}

ART_OUTLANDER_LEGS = """
................
.XXXX......XXXX.
XHHHMX....XHHHMX
XHHHMX....XHHHMX
XHRMDDX..XHRMDDX
.XDDDDX..XDDDDX.
..XDDX....XDDX..
..XDDX....XDDX..
.XHHHMX..XHHHMX.
.XHMMDDX.XHMMDDX
.XHRMDDX.XHRMDDX
.XMMDDDX.XMMDDDX
XMMDDDDXXMMDDDDX
XHHMMDDXXHHMMDDX
.XXXXXX..XXXXXX.
................
"""
PAL_OUTLANDER_LEGS = {'.': _, 'X': O_OUT, 'H': O_HIL, 'M': O_MET, 'D': O_DKM, 'R': O_RIV}

ART_TWIN_MANPADS = """
................
...XX......XX...
..XRRYX..XRRYX..
.XRRRRYXXRRRRYX.
.XROOOODXXROOOOD
XROOOOOODXROOOOD
XROOOOOODXROOOOD
XROOODDDDXXROOOD
.XROODDX..XROODX
.XROODDX..XROODX
..XDDDXXXXXXDDX.
..XDDCXCCCCXDXX.
...XDDDXXXXDDX..
....XXDDDDDDX...
......XXXXXX....
................
"""
PAL_TWIN_MANPADS = {'.': _, 'X': M_OUT, 'O': M_OLV, 'D': M_DKO, 'R': P_RED, 'Y': P_YEL, 'C': M_OPT}

# Weapons Pixel Art
ART_BATTLE_RIFLE = """
................
................
................
................
......XCCCCX....
...XXXXMMMMXXXX.
..XMMMMMMMMMMMMX
.XMDDMMMMDDMMMMX
.XMDDXXMMXXMMMMX
XMMDX..XX..XMMX.
XDDX.......XMMX.
.XX.........XX..
................
................
................
................
"""
PAL_BATTLE_RIFLE = {'.': _, 'X': W_OUT, 'M': W_MET, 'D': W_DKM, 'C': CYN}

ART_AUTOCANNON = """
................
................
................
.....XXXX.......
...XXMMMMXXXX...
..XMMMMMMMMMMXX.
.XMDDDDDDDDMMMMX
XMDDXXBBBBXXMMMX
XMDX.XBBBBX.XMMX
XMDX.XBBBBX.XMMX
.XX..XBBBBX..XX.
......XXXX......
................
................
................
................
"""
PAL_AUTOCANNON = {'.': _, 'X': W_OUT, 'M': W_MET, 'D': W_DKM, 'B': W_BRS}

ART_SHOTGUN = """
................
................
................
................
...XXXXXXXXX....
..XMMMMMMMMMX...
.XMMRRRRRMMMMX..
XMDDXXDDXXMMMMX.
XMDX..XX.XMMMMX.
XDDX.....XDDDDX.
.XX.......XXXX..
................
................
................
................
................
"""
PAL_SHOTGUN = {'.': _, 'X': W_OUT, 'M': W_MET, 'D': W_DKM, 'R': RED}

ART_GRENADE_LAUNCHER = """
................
................
................
....XXXXXX......
..XXMMMMMMXX....
.XMMMDDDDMMMX...
XMDDXYYYYXDDMX..
XMDXYYYYYYXDDMX.
XMDXYYYYYYXDDMX.
XMDDXYYYYXDDMX..
.XMMMDDDDMMMX...
..XXMMMMMMXX....
....XXXXXX......
................
................
................
"""
PAL_GRENADE_LAUNCHER = {'.': _, 'X': W_OUT, 'M': W_MET, 'D': W_DKM, 'Y': YEL}

ART_RECOILLESS_RIFLE = """
................
................
................
................
..XXXXXX........
.XMMMMMMXXXX....
XMMYYYYMMMMMX...
XMDYYYYDDDDDDXX.
XMDDDDDDDDDDDDDX
.XMDDDDXXXXXXDDX
..XXXXXX....XXXX
................
................
................
................
................
"""
PAL_RECOILLESS_RIFLE = {'.': _, 'X': W_OUT, 'M': W_MET, 'D': W_DKM, 'Y': YEL}

ART_ATGM = """
................
................
...XXXXXXXXXX...
..XMMMMMMMMMMX..
.XMMMMMMMMMMMMX.
.XMMCCDDDDMMMMX.
XMMCCCCDDDDMMMMX
XMMCCCCDDDDMMMMX
XMMDDDDDDDDMMMMX
.XMMDDDDDDMMMMX.
.XMMMMMMMMMMMMX.
..XMMMMMMMMMMX..
...XXXXXXXXXX...
................
................
................
"""
PAL_ATGM = {'.': _, 'X': W_OUT, 'M': W_MET, 'D': W_DKM, 'C': CYN}

ART_FLAMETHROWER = """
................
................
......XXXX......
....XXRRRRXX....
...XRRRRRRRRX...
..XRRRRRRRRRRX..
..XRRDDDDDDRRX..
.XXRRDDDDDDRRXX.
.XMMXMMMMMMXMMX.
.XMMXMMMMMMXMMX.
X.XMMMMMMMMMMX.X
X..XXXXXXXXXX..X
......XOOX......
.....XOOOOX.....
......XXXX......
................
"""
PAL_FLAMETHROWER = {'.': _, 'X': W_OUT, 'M': W_MET, 'R': RED, 'D': (120, 25, 20, 255), 'O': ORG}

ART_VIBRO_BLADE = """
................
.............XX.
............XOXX
...........XOOX.
..........XOOX..
.........XOOX...
........XOOX....
.......XOOX.....
......XOOX......
.....XOOX.......
....XMMX........
...XMMX.........
..XDDX..........
.XDDX...........
.XX.............
................
"""
PAL_VIBRO_BLADE = {'.': _, 'X': W_OUT, 'M': W_MET, 'D': W_DKM, 'O': ORG}

# Ammo Pixel Art
ART_AMMO_SHELLS = """
................
................
...XX...XX...XX.
..XBBX.XBBX.XBBX
..XBBX.XBBX.XBBX
..XBBX.XBBX.XBBX
..XBBX.XBBX.XBBX
..XBBX.XBBX.XBBX
..XBBX.XBBX.XBBX
..XDDX.XDDX.XDDX
..XDDX.XDDX.XDDX
...XX...XX...XX.
................
................
................
................
"""
PAL_AMMO_SHELLS = {'.': _, 'X': W_OUT, 'B': W_BRS, 'D': W_DKM}

ART_AMMO_SLUG = """
................
................
................
.....XXXXXX.....
....XRRRRRRX....
...XRRRRRRRRX...
...XRRRRRRRRX...
...XRRRRRRRRX...
...XRRRRRRRRX...
...XBBBBBBBBX...
...XBBBBBBBBX...
....XBBBBBBX....
.....XXXXXX.....
................
................
................
"""
PAL_AMMO_SLUG = {'.': _, 'X': W_OUT, 'R': RED, 'B': W_BRS}

ART_AMMO_GRENADE = """
................
................
......XXXX......
....XXYYYYXX....
...XYYYYYYYYX...
..XYYYYYYYYYYX..
..XYYDDDDDDYYX..
..XYYDDDDDDYYX..
..XYYYYYYYYYYX..
...XYYYYYYYYX...
....XXYYYYXX....
......XXXX......
................
................
................
................
"""
PAL_AMMO_GRENADE = {'.': _, 'X': W_OUT, 'Y': YEL, 'D': W_DKM}

ART_AMMO_ROCKET = """
................
.............XX.
............XRRX
...........XRRRX
..........XRRRRX
.........XDDDDX.
........XDDDDX..
.......XDDDDX...
......XDDDDX....
.....XDDDDX.....
....XDDDDX......
...XDDDDX.......
..XDDXXDDX......
.XDDX..XDDX.....
.XX......XX.....
................
"""
PAL_AMMO_ROCKET = {'.': _, 'X': W_OUT, 'R': RED, 'D': W_DKM}

ART_AMMO_MISSILE = """
................
.............XX.
............XYYX
...........XYYYX
..........XWWWWX
.........XWWWWX.
........XWWWWX..
.......XWWWWX...
......XWWWWX....
.....XWWWWX.....
....XWWWWX......
...XDDDDX.......
..XDDXXDDX......
.XDDX..XDDX.....
.XX......XX.....
................
"""
PAL_AMMO_MISSILE = {'.': _, 'X': W_OUT, 'Y': YEL, 'W': WHT, 'D': W_DKM}

ART_AMMO_CANISTER = """
................
................
......XXXX......
.....XRRRRX.....
....XRRRRRRX....
...XRRRWWWRRX...
...XRRWOOOWRX...
...XRRWOOOWRX...
...XRRRWWWRRX...
...XRRRRRRRRX...
....XRRRRRRX....
.....XRRRRX.....
......XXXX......
................
................
................
"""
PAL_AMMO_CANISTER = {'.': _, 'X': W_OUT, 'R': RED, 'W': WHT, 'O': ORG}

# Frame Kits (Task 3)
ART_FRAME_KIT = """
................
...XXXXXXXXXX...
..XMMMMMMMMMMX..
.XMMMMMMMMMMMMX.
.XMMXXXXXXXXMMX.
XMMMX......XMMMX
XMMX........XMMX
XMMX........XMMX
XMMX........XMMX
XMMMX......XMMMX
.XMMXXXXXXXXMMX.
.XMMMMMMMMMMMMX.
..XMMMMMMMMMMX..
...XXXXXXXXXX...
................
................
"""
PAL_KIT_SALVAGE = {'.': _, 'X': S_OUT, 'M': S_IRN}
PAL_KIT_ADVANCED = {'.': _, 'X': SP_OUT, 'M': SP_HIL}
PAL_KIT_ELITE = {'.': _, 'X': V_OUT, 'M': V_WHT}

ICONS_LIST = [
    # Baseline
    ("armor_polar_head.png", ART_POLAR_HEAD, PAL_POLAR_HEAD),
    ("armor_polar_arms.png", ART_POLAR_ARMS, PAL_POLAR_ARMS),
    ("armor_polar_legs.png", ART_POLAR_LEGS, PAL_POLAR_LEGS),
    ("armor_outlander_arms.png", ART_OUTLANDER_ARMS, PAL_OUTLANDER_ARMS),
    ("armor_outlander_legs.png", ART_OUTLANDER_LEGS, PAL_OUTLANDER_LEGS),
    ("module_twin_manpads.png", ART_TWIN_MANPADS, PAL_TWIN_MANPADS),

    # 1. Salvage Faction
    ("armor_salvage_head.png", ART_GENERIC_HEAD, {'.': _, 'X': S_OUT, 'M': S_IRN, 'D': S_DKR, 'C': S_RST}),
    ("armor_salvage_chest.png", ART_GENERIC_CHEST, {'.': _, 'X': S_OUT, 'M': S_IRN, 'D': S_DKR, 'Y': S_YEL}),
    ("armor_salvage_arms.png", ART_GENERIC_ARMS, {'.': _, 'X': S_OUT, 'M': S_IRN, 'D': S_DKR}),
    ("armor_salvage_legs.png", ART_GENERIC_LEGS, {'.': _, 'X': S_OUT, 'M': S_IRN, 'D': S_DKR}),
    ("module_salvage_scraps.png", ART_GENERIC_MODULE, {'.': _, 'X': S_OUT, 'M': S_IRN, 'D': S_DKR, 'C': S_YEL}),

    # 2. Shiden Corps
    ("armor_shiden_head.png", ART_GENERIC_HEAD, {'.': _, 'X': SH_OUT, 'M': SH_NAV, 'D': SH_LGT, 'C': SH_GLD}),
    ("armor_shiden_chest.png", ART_GENERIC_CHEST, {'.': _, 'X': SH_OUT, 'M': SH_NAV, 'D': SH_LGT, 'Y': SH_WHT}),
    ("armor_shiden_arms.png", ART_GENERIC_ARMS, {'.': _, 'X': SH_OUT, 'M': SH_NAV, 'D': SH_LGT}),
    ("armor_shiden_legs.png", ART_GENERIC_LEGS, {'.': _, 'X': SH_OUT, 'M': SH_NAV, 'D': SH_LGT}),
    ("module_shiden_crest.png", ART_GENERIC_MODULE, {'.': _, 'X': SH_OUT, 'M': SH_NAV, 'D': SH_LGT, 'C': SH_GLD}),

    # 3. Khamsin Long-Range Guard
    ("armor_khamsin_head.png", ART_GENERIC_HEAD, {'.': _, 'X': K_OUT, 'M': K_OCH, 'D': K_DKT, 'C': K_TER}),
    ("armor_khamsin_chest.png", ART_GENERIC_CHEST, {'.': _, 'X': K_OUT, 'M': K_OCH, 'D': K_DKT, 'Y': K_SND}),
    ("armor_khamsin_arms.png", ART_GENERIC_ARMS, {'.': _, 'X': K_OUT, 'M': K_OCH, 'D': K_DKT}),
    ("armor_khamsin_legs.png", ART_GENERIC_LEGS, {'.': _, 'X': K_OUT, 'M': K_OCH, 'D': K_DKT}),
    ("module_khamsin_filters.png", ART_GENERIC_MODULE, {'.': _, 'X': K_OUT, 'M': K_OCH, 'D': K_DKT, 'C': K_TER}),

    # 4. Riverine Corps
    ("armor_riverine_head.png", ART_GENERIC_HEAD, {'.': _, 'X': R_OUT, 'M': R_MOS, 'D': R_LGT, 'C': R_BLU}),
    ("armor_riverine_chest.png", ART_GENERIC_CHEST, {'.': _, 'X': R_OUT, 'M': R_MOS, 'D': R_LGT, 'Y': R_GSK}),
    ("armor_riverine_arms.png", ART_GENERIC_ARMS, {'.': _, 'X': R_OUT, 'M': R_MOS, 'D': R_LGT}),
    ("armor_riverine_legs.png", ART_GENERIC_LEGS, {'.': _, 'X': R_OUT, 'M': R_MOS, 'D': R_LGT}),
    ("module_riverine_snorkel.png", ART_GENERIC_MODULE, {'.': _, 'X': R_OUT, 'M': R_MOS, 'D': R_LGT, 'C': R_GSK}),

    # 5. Specter Stealth PMC
    ("armor_specter_head.png", ART_GENERIC_HEAD, {'.': _, 'X': SP_OUT, 'M': SP_RAM, 'D': SP_PRP, 'C': SP_CYN}),
    ("armor_specter_chest.png", ART_GENERIC_CHEST, {'.': _, 'X': SP_OUT, 'M': SP_RAM, 'D': SP_PRP, 'Y': SP_HIL}),
    ("armor_specter_arms.png", ART_GENERIC_ARMS, {'.': _, 'X': SP_OUT, 'M': SP_RAM, 'D': SP_PRP}),
    ("armor_specter_legs.png", ART_GENERIC_LEGS, {'.': _, 'X': SP_OUT, 'M': SP_RAM, 'D': SP_PRP}),
    ("module_specter_ecm.png", ART_GENERIC_MODULE, {'.': _, 'X': SP_OUT, 'M': SP_RAM, 'D': SP_PRP, 'C': SP_CYN}),

    # 6. Valkyrie Special Forces
    ("armor_valkyrie_head.png", ART_GENERIC_HEAD, {'.': _, 'X': V_OUT, 'M': V_WHT, 'D': V_SHD, 'C': V_CYN}),
    ("armor_valkyrie_chest.png", ART_GENERIC_CHEST, {'.': _, 'X': V_OUT, 'M': V_WHT, 'D': V_SHD, 'Y': V_GLD}),
    ("armor_valkyrie_arms.png", ART_GENERIC_ARMS, {'.': _, 'X': V_OUT, 'M': V_WHT, 'D': V_SHD}),
    ("armor_valkyrie_legs.png", ART_GENERIC_LEGS, {'.': _, 'X': V_OUT, 'M': V_WHT, 'D': V_SHD}),
    ("module_valkyrie_sensor.png", ART_GENERIC_MODULE, {'.': _, 'X': V_OUT, 'M': V_WHT, 'D': V_SHD, 'C': V_CYN}),

    # 8 Weapons
    ("exoframe_battle_rifle.png", ART_BATTLE_RIFLE, PAL_BATTLE_RIFLE),
    ("exoframe_autocannon_30mm.png", ART_AUTOCANNON, PAL_AUTOCANNON),
    ("exoframe_shotgun_breacher.png", ART_SHOTGUN, PAL_SHOTGUN),
    ("exoframe_grenade_launcher.png", ART_GRENADE_LAUNCHER, PAL_GRENADE_LAUNCHER),
    ("exoframe_recoilless_rifle.png", ART_RECOILLESS_RIFLE, PAL_RECOILLESS_RIFLE),
    ("exoframe_atgm_guided.png", ART_ATGM, PAL_ATGM),
    ("exoframe_flamethrower.png", ART_FLAMETHROWER, PAL_FLAMETHROWER),
    ("exoframe_vibro_blade.png", ART_VIBRO_BLADE, PAL_VIBRO_BLADE),

    # Ammo
    ("ammo_30mm_autocannon.png", ART_AMMO_SHELLS, PAL_AMMO_SHELLS),
    ("ammo_shotgun_slug.png", ART_AMMO_SLUG, PAL_AMMO_SLUG),
    ("ammo_40mm_grenade.png", ART_AMMO_GRENADE, PAL_AMMO_GRENADE),
    ("ammo_84mm_rocket.png", ART_AMMO_ROCKET, PAL_AMMO_ROCKET),
    ("ammo_atgm_missile.png", ART_AMMO_MISSILE, PAL_AMMO_MISSILE),
    ("ammo_napalm_canister.png", ART_AMMO_CANISTER, PAL_AMMO_CANISTER),

    # Frame Kits
    ("exoframe_kit_salvage.png", ART_FRAME_KIT, PAL_KIT_SALVAGE),
    ("exoframe_kit_advanced.png", ART_FRAME_KIT, PAL_KIT_ADVANCED),
    ("exoframe_kit_elite.png", ART_FRAME_KIT, PAL_KIT_ELITE),

    # Role Variants
    ("armor_police_head.png", ART_POLICE_HEAD, {'.': _, 'X': POL_OUT, 'M': POL_NVY, 'C': POL_CYN, 'W': POL_WHT, 'B': POL_BLU, 'R': POL_RED}),
    ("armor_police_chest.png", ART_POLICE_CHEST, {'.': _, 'X': POL_OUT, 'M': POL_NVY, 'D': POL_LGT, 'W': POL_WHT}),
    ("exoframe_riot_shield.png", ART_RIOT_SHIELD, {'.': _, 'X': POL_OUT, 'M': POL_NVY, 'C': POL_CYN, 'W': POL_WHT}),
    ("exoframe_stun_baton.png", ART_STUN_BATON, {'.': _, 'X': W_OUT, 'M': W_MET, 'D': W_DKM, 'C': BAT_CYN}),
    ("armor_rescue_head.png", ART_RESCUE_HEAD, {'.': _, 'X': RES_OUT, 'M': RES_ORG, 'Y': RES_YEL, 'W': RES_WHT}),
    ("armor_rescue_chest.png", ART_RESCUE_CHEST, {'.': _, 'X': RES_OUT, 'M': RES_ORG, 'W': RES_WHT}),
    ("module_rescue_winch.png", ART_RESCUE_WINCH, {'.': _, 'X': RES_OUT, 'M': RES_MET, 'Y': RES_YEL, 'D': RES_DKM}),
    ("armor_float_ring.png", ART_FLOAT_RING, {'.': _, 'X': AMP_OUT, 'Y': AMP_ORG}),
    ("module_search_radar.png", ART_SEARCH_RADAR, {'.': _, 'X': RAD_OUT, 'G': RAD_GLD, 'C': RAD_CYN, 'D': RAD_GRY, 'M': W_MET}),
    ("exoframe_fishing_rod.png", ART_FISHING_ROD, {'.': _, 'X': W_OUT, 'M': W_MET, 'D': ROD_MET, 'R': ROD_RED, 'W': WHT}),
]

OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src/main/resources/assets/obsolete/textures/item"))

if __name__ == "__main__":
    print(f"Generating {len(ICONS_LIST)} distinct 16x16 pixel art item icons into {OUT_DIR}...")
    os.makedirs(OUT_DIR, exist_ok=True)
    for fname, art, pal in ICONS_LIST:
        grid = parse_ascii_art(art, pal)
        png_bytes = create_png_16x16(grid)
        target = os.path.join(OUT_DIR, fname)
        with open(target, "wb") as f:
            f.write(png_bytes)
    print(f"Successfully generated all {len(ICONS_LIST)} item icons!")
