import struct
import zlib
import os
import math

WIDTH, HEIGHT = 512, 512

def create_png_grid(grid):
    raw = bytearray()
    for y in range(HEIGHT):
        raw.append(0)
        for x in range(WIDTH):
            r, g, b, a = grid[y][x]
            raw.extend([r, g, b, a])

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', WIDTH, HEIGHT, 8, 6, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(bytes(raw), level=6))
    iend = chunk(b'IEND', b'')
    return header + ihdr + idat + iend

grid = [[(14, 17, 22, 255) for _ in range(WIDTH)] for _ in range(HEIGHT)]

def blend(x, y, color):
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return
    r, g, b, a = color
    if a == 0:
        return
    if a == 255:
        grid[y][x] = color
        return
    bg_r, bg_g, bg_b, bg_a = grid[y][x]
    alpha = a / 255.0
    inv = 1.0 - alpha
    out_r = int(r * alpha + bg_r * inv)
    out_g = int(g * alpha + bg_g * inv)
    out_b = int(b * alpha + bg_b * inv)
    grid[y][x] = (out_r, out_g, out_b, 255)

def fill_rect(x0, y0, w, h, color):
    for y in range(max(0, y0), min(HEIGHT, y0 + h)):
        for x in range(max(0, x0), min(WIDTH, x0 + w)):
            blend(x, y, color)

# 1. Background tactical radial gradient & grid
for y in range(HEIGHT):
    for x in range(WIDTH):
        dx = x - 256
        dy = y - 240
        dist = math.sqrt(dx*dx + dy*dy)
        rad = dist / 360.0
        r = int(24 * (1 - rad*0.65))
        g = int(30 * (1 - rad*0.65))
        b = int(40 * (1 - rad*0.65))
        # Subtle tactical 32px grid lines
        if (x % 32 == 0 or y % 32 == 0) and 20 <= x <= 492 and 20 <= y <= 492:
            r += 10; g += 14; b += 20
        grid[y][x] = (r, g, b, 255)

# 2. Outer Tactical Chamfered Frame
BORDER_COLOR = (45, 58, 75, 255)
ACCENT_CYAN = (0, 225, 255, 255)
ACCENT_AMBER = (255, 185, 0, 255)

for x in range(24, 488):
    blend(x, 24, BORDER_COLOR)
    blend(x, 25, (70, 90, 115, 255))
    blend(x, 486, (70, 90, 115, 255))
    blend(x, 487, BORDER_COLOR)
for y in range(24, 488):
    blend(24, y, BORDER_COLOR)
    blend(25, y, (70, 90, 115, 255))
    blend(486, y, (70, 90, 115, 255))
    blend(487, y, BORDER_COLOR)

# Corner brackets
CORNER_SZ = 36
for c in [(24, 24), (488 - CORNER_SZ, 24), (24, 488 - CORNER_SZ), (488 - CORNER_SZ, 488 - CORNER_SZ)]:
    cx0, cy0 = c
    fill_rect(cx0, cy0, CORNER_SZ, 6, ACCENT_AMBER)
    fill_rect(cx0, cy0, 6, CORNER_SZ, ACCENT_AMBER)

# Hazard stripes along bottom banner (y=458..476)
for x in range(28, 484):
    is_stripe = ((x + 460) // 16) % 2 == 0
    col = (255, 196, 0, 255) if is_stripe else (22, 26, 32, 255)
    for y in range(458, 474):
        grid[y][x] = col

# 3. Centerpiece: High-Detail Stylized Exoframe Helmet & Cockpit Icon (Center=(256, 185))
CENTER_X, CENTER_Y = 256, 180

# Radar glow rings
for y in range(HEIGHT):
    for x in range(WIDTH):
        dx = x - CENTER_X
        dy = y - CENTER_Y
        dist = math.sqrt(dx*dx + dy*dy)
        if 132 < dist < 134:
            blend(x, y, (0, 220, 255, 110))
        elif 150 < dist < 152:
            blend(x, y, (0, 190, 235, 170))
        elif 75 < dist < 77:
            blend(x, y, (0, 220, 255, 60))

# Targeting crosshairs
for x in range(CENTER_X - 165, CENTER_X + 166):
    if abs(x - CENTER_X) > 45:
        blend(x, CENTER_Y, (0, 220, 255, 75))
for y in range(CENTER_Y - 150, CENTER_Y + 151):
    if abs(y - CENTER_Y) > 45:
        blend(CENTER_X, y, (0, 220, 255, 75))

# Reticle corner ticks
for a, b in [(-125, -125), (125, -125), (-125, 125), (125, 125)]:
    fill_rect(CENTER_X + a - 8, CENTER_Y + b, 16, 2, ACCENT_CYAN)
    fill_rect(CENTER_X + a, CENTER_Y + b - 8, 2, 16, ACCENT_CYAN)

def fill_poly(pts, color):
    min_y = max(0, min(p[1] for p in pts))
    max_y = min(HEIGHT - 1, max(p[1] for p in pts))
    for y in range(min_y, max_y + 1):
        nodes = []
        n = len(pts)
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if (y1 <= y < y2) or (y2 <= y < y1):
                nodes.append(x1 + (y - y1) / (y2 - y1) * (x2 - x1))
        nodes.sort()
        for i in range(0, len(nodes), 2):
            if i + 1 < len(nodes):
                x_start = max(0, int(nodes[i]))
                x_end = min(WIDTH - 1, int(nodes[i+1]))
                for x in range(x_start, x_end + 1):
                    blend(x, y, color)

# Dual shoulder pauldrons
fill_poly([(108, 140), (160, 120), (175, 215), (118, 235)], (55, 68, 54, 255))
fill_poly([(108, 140), (160, 120), (155, 155), (103, 175)], (80, 98, 78, 255))
fill_poly([(404, 140), (352, 120), (337, 215), (394, 235)], (55, 68, 54, 255))
fill_poly([(404, 140), (352, 120), (357, 155), (409, 175)], (80, 98, 78, 255))

# Torso / Chassis Bulkhead
fill_poly([(165, 205), (347, 205), (330, 275), (182, 275)], (40, 50, 42, 255))
fill_poly([(185, 215), (327, 215), (315, 268), (197, 268)], (32, 40, 34, 255))

# Center Chest Armor Plates (Sloped composite armor)
fill_poly([(210, 220), (302, 220), (290, 262), (222, 262)], (60, 75, 58, 255))
for y in range(250, 260):
    for x in range(235, 277):
        if ((x + y) // 6) % 2 == 0:
            blend(x, y, (255, 200, 0, 255))
        else:
            blend(x, y, (30, 30, 30, 255))

# Cockpit Capsule
# Lower Ring
fill_poly([(175, 130), (337, 130), (325, 198), (187, 198)], (65, 82, 64, 255))
# Mid Ring (Tapering)
fill_poly([(185, 92), (327, 92), (335, 136), (177, 136)], (76, 96, 75, 255))
# Roof dome
fill_poly([(210, 58), (302, 58), (325, 96), (187, 96)], (58, 74, 58, 255))
# Roof hatch plate
fill_poly([(225, 62), (287, 62), (295, 88), (217, 88)], (92, 114, 90, 255))

# Dual Communications Antenna Masts
fill_poly([(205, 25), (210, 25), (210, 68), (205, 68)], (35, 40, 45, 255))
fill_poly([(302, 25), (307, 25), (307, 68), (302, 68)], (35, 40, 45, 255))
fill_rect(203, 22, 9, 4, (255, 60, 40, 255))
fill_rect(300, 22, 9, 4, (255, 60, 40, 255))

# GLOWING VISOR VISION SLIT
fill_poly([(200, 138), (312, 138), (306, 158), (206, 158)], (15, 20, 25, 255))
fill_poly([(204, 141), (308, 141), (304, 155), (208, 155)], (0, 235, 255, 255))
fill_poly([(210, 144), (302, 144), (300, 152), (212, 152)], (225, 250, 255, 255))

# Visor bloom
for y in range(130, 168):
    for x in range(192, 320):
        dy = abs(y - 148)
        dx = max(0, abs(x - 256) - 50)
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 22:
            intensity = int((1.0 - dist / 22.0) * 150)
            blend(x, y, (0, 225, 255, intensity))

# Armor rivets
for x, y in [(190, 108), (322, 108), (180, 152), (332, 152), (195, 230), (317, 230)]:
    fill_rect(x - 2, y - 2, 5, 5, (185, 200, 215, 255))
    fill_rect(x - 1, y - 1, 3, 3, (40, 45, 50, 255))

# 4. TYPOGRAPHY: "OBSOLETE" in Crisp Bold Military Typography
LETTERS = {
    'O': [
        " XXXX ",
        "XX  XX",
        "XX  XX",
        "XX  XX",
        "XX  XX",
        "XX  XX",
        "XXXXXX"
    ],
    'B': [
        "XXXXX ",
        "XX  XX",
        "XX  XX",
        "XXXXX ",
        "XX  XX",
        "XX  XX",
        "XXXXX "
    ],
    'S': [
        " XXXXX",
        "XX    ",
        "XX    ",
        " XXXX ",
        "    XX",
        "    XX",
        "XXXXX "
    ],
    'L': [
        "XX    ",
        "XX    ",
        "XX    ",
        "XX    ",
        "XX    ",
        "XX    ",
        "XXXXXX"
    ],
    'E': [
        "XXXXXX",
        "XX    ",
        "XX    ",
        "XXXXX ",
        "XX    ",
        "XX    ",
        "XXXXXX"
    ],
    'T': [
        "XXXXXX",
        "  XX  ",
        "  XX  ",
        "  XX  ",
        "  XX  ",
        "  XX  ",
        "  XX  "
    ]
}

def draw_stencil_text(text, start_x, start_y, scale, color, shadow_color):
    cur_x = start_x
    for ch in text:
        bitmap = LETTERS.get(ch)
        if not bitmap:
            cur_x += 4 * scale
            continue
        w = len(bitmap[0])
        h = len(bitmap)
        for row in range(h):
            for col in range(w):
                if bitmap[row][col] == 'X':
                    fill_rect(cur_x + col * scale + 3, start_y + row * scale + 3, scale, scale, shadow_color)
        for row in range(h):
            for col in range(w):
                if bitmap[row][col] == 'X':
                    fill_rect(cur_x + col * scale, start_y + row * scale, scale, scale, color)
        cur_x += (w + 1) * scale

# 8 letters, each (6 + 1) * 6 = 42px. 8 * 42 = 336px. Left margin = (512 - 336)/2 = 88px.
TITLE_X = 88
TITLE_Y = 315
SCALE = 6
TEXT_COLOR = (248, 250, 254, 255)
SHADOW_COLOR = (12, 14, 18, 255)
draw_stencil_text("OBSOLETE", TITLE_X, TITLE_Y, SCALE, TEXT_COLOR, SHADOW_COLOR)

# Bevel highlight on text top edge
for x in range(TITLE_X, TITLE_X + 336):
    for y in range(TITLE_Y, TITLE_Y + 3):
        if grid[y][x][:3] == TEXT_COLOR[:3]:
            blend(x, y, (255, 255, 255, 170))

# 5. Subtitle Banner: "TACTICAL EXOFRAMES"
SUB_Y = 378
fill_rect(80, SUB_Y, 352, 24, (20, 26, 35, 240))
fill_rect(80, SUB_Y, 352, 2, ACCENT_CYAN)
fill_rect(80, SUB_Y + 22, 352, 2, ACCENT_CYAN)
fill_rect(76, SUB_Y - 2, 4, 28, ACCENT_AMBER)
fill_rect(432, SUB_Y - 2, 4, 28, ACCENT_AMBER)

SMALL_FONT = {
    'A': [" X ", "X X", "XXX", "X X", "X X"],
    'B': ["XX ", "X X", "XX ", "X X", "XX "],
    'C': [" XX", "X  ", "X  ", "X  ", " XX"],
    'D': ["XX ", "X X", "X X", "X X", "XX "],
    'E': ["XXX", "X  ", "XX ", "X  ", "XXX"],
    'F': ["XXX", "X  ", "XX ", "X  ", "X  "],
    'G': [" XX", "X  ", "X X", "X X", " XX"],
    'H': ["X X", "X X", "XXX", "X X", "X X"],
    'I': ["XXX", " X ", " X ", " X ", "XXX"],
    'K': ["X X", "XX ", "X  ", "XX ", "X X"],
    'L': ["X  ", "X  ", "X  ", "X  ", "XXX"],
    'M': ["X X", "XXX", "X X", "X X", "X X"],
    'N': ["XX ", "X X", "X X", "X X", "X X"],
    'O': [" X ", "X X", "X X", "X X", " X "],
    'P': ["XX ", "X X", "XX ", "X  ", "X  "],
    'R': ["XX ", "X X", "XX ", "X X", "X X"],
    'S': [" XX", "X  ", " X ", "  X", "XX "],
    'T': ["XXX", " X ", " X ", " X ", " X "],
    'U': ["X X", "X X", "X X", "X X", "XXX"],
    'V': ["X X", "X X", "X X", "X X", " X "],
    'X': ["X X", "X X", " X ", "X X", "X X"],
    ' ': ["   ", "   ", "   ", "   ", "   "],
    '-': ["   ", "   ", "XXX", "   ", "   "],
    '.': ["   ", "   ", "   ", "   ", " X "],
    '0': ["XXX", "X X", "X X", "X X", "XXX"],
    '1': [" X ", "XX ", " X ", " X ", "XXX"],
    '2': ["XXX", "  X", "XXX", "X  ", "XXX"],
    '4': ["X X", "X X", "XXX", "  X", "  X"],
}

def draw_small_text(text, start_x, start_y, scale, color):
    cur_x = start_x
    for ch in text:
        bitmap = SMALL_FONT.get(ch, SMALL_FONT[' '])
        w = len(bitmap[0])
        h = len(bitmap)
        for row in range(h):
            for col in range(w):
                if bitmap[row][col] == 'X':
                    fill_rect(cur_x + col * scale, start_y + row * scale, scale, scale, color)
        cur_x += (w + 1) * scale

draw_small_text("TACTICAL EXOFRAMES", 98, SUB_Y + 7, 2, (0, 235, 255, 255))

# 6. Badges: "FORGE 1.20.1" & "GECKOLIB 4"
draw_small_text("FORGE 1.20.1", 42, 420, 2, (160, 180, 195, 255))
draw_small_text("GECKOLIB 4", 370, 420, 2, (160, 180, 195, 255))

os.makedirs("Obsolete/curseforge_showcase", exist_ok=True)
os.makedirs("Obsolete/src/main/resources", exist_ok=True)

png_bytes = create_png_grid(grid)
with open("Obsolete/curseforge_showcase/logo.png", "wb") as f:
    f.write(png_bytes)
with open("Obsolete/src/main/resources/logo.png", "wb") as f:
    f.write(png_bytes)
with open("Obsolete/src/main/resources/icon.png", "wb") as f:
    f.write(png_bytes)

print("Regenerated 512x512 logo with fixed typography!")
