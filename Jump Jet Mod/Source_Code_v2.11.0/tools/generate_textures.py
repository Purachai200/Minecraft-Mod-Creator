"""Regenerates the Youjo Senki flight-rig textures (stdlib only, no Pillow).

  python3 tools/generate_textures.py [preview_dir]

Writes:
  - textures/models/armor/elenium_flight_unit.png          (dyeable base, grayscale)
  - textures/models/armor/elenium_flight_unit_glowmask.png (fullbright emissive layer)
  - textures/item/<id>.png + <id>_overlay.png              (17 unique 32x32 icons)
  - models/item/<id>.json
UV boxes come from tools/model_spec.py, so model edits stay in sync.
"""
import json
import math
import os
import re
import struct
import sys
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/youjosenki")


# ---------------------------------------------------------------- PNG I/O
def write_png(path, px):
    h, w = len(px), len(px[0])
    raw = bytearray()
    for row in px:
        raw.append(0)
        for r, g, b, a in row:
            raw += bytes((clamp(r), clamp(g), clamp(b), clamp(a)))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def clamp(v):
    return max(0, min(255, int(round(v))))


def blank(w, h):
    return [[(0, 0, 0, 0) for _ in range(w)] for _ in range(h)]


def noise(x, y, seed=0):
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def blend(dst, src):
    sa = src[3] / 255.0
    if sa >= 1.0 or dst[3] == 0:
        return src if sa > 0 else dst
    da = dst[3] / 255.0
    oa = sa + da * (1 - sa)
    return tuple((src[i] * sa + dst[i] * da * (1 - sa)) / oa for i in range(3)) + (oa * 255,)


# ---------------------------------------------------------------- armor texture
# Material per texOffs origin; anything unlisted is generic armor plate.
MATERIAL = {
    (0, 0): "webbing", (40, 0): "webbing",
    (40, 6): "hose", (40, 8): "rail",
    (24, 26): "bright", (32, 64): "gauge",
    (36, 26): "glass", (104, 0): "core", (112, 0): "nav_green", (116, 0): "nav_red", (120, 0): "strobe",
    (20, 46): "nozzle", (28, 46): "nozzle", (48, 64): "nozzle", (48, 70): "nozzle",
    (60, 96): "nozzle", (74, 96): "nozzle", (76, 15): "nozzle",
    (0, 64): "tank", (16, 64): "tank", (24, 96): "tank", (42, 96): "tank",
    (64, 64): "aero", (64, 76): "aero", (64, 82): "aero", (96, 64): "aero", (106, 64): "aero",
}
EMISSIVE = {"glass", "core", "nav_green", "nav_red", "strobe"}


def parse_boxes():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import model_spec

    out = []

    def walk(p):
        for uv, lo, hi in p.boxes:
            out.append((uv[0], uv[1], hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]))
        for c in p.children:
            walk(c)
    for p in model_spec.PARTS:
        walk(p)
    return out


def faces(u, v, w, h, d):
    """Blockbench/vanilla box-UV layout -> {face: (x0, y0, x1, y1)} in texels."""
    def r(x0, y0, x1, y1):
        return (int(math.floor(x0)), int(math.floor(y0)), int(math.ceil(x1)), int(math.ceil(y1)))
    return {
        "top": r(u + d, v, u + d + w, v + d),
        "bottom": r(u + d + w, v, u + d + 2 * w, v + d),
        "east": r(u, v + d, u + d, v + d + h),
        "front": r(u + d, v + d, u + d + w, v + d + h),
        "west": r(u + d + w, v + d, u + 2 * d + w, v + d + h),
        "back": r(u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h),
    }


FACE_LIGHT = {"top": 1.12, "front": 1.0, "back": 1.0, "east": 0.86, "west": 0.86, "bottom": 0.62}


def paint_base_face(px, mat, face, rect, seed):
    x0, y0, x1, y1 = rect
    fw, fh = x1 - x0, y1 - y0
    if fw <= 0 or fh <= 0:
        return
    for y in range(y0, min(y1, 128)):
        for x in range(x0, min(x1, 128)):
            lx, ly = x - x0, y - y0
            tx = lx / max(1, fw - 1)
            ty = ly / max(1, fh - 1)
            n = noise(x, y, seed)
            if mat == "webbing":  # woven nylon: dark, cross-weave, stitched border
                lum = 118 + (10 if (lx + ly) % 2 == 0 else -4) + n * 8
                if (lx == 0 or lx == fw - 1 or ly == 0 or ly == fh - 1) and (lx + ly) % 2 == 0:
                    lum = 160
            elif mat == "hose":  # ribbed braided hose
                lum = 120 + (26 if (lx if fw > fh else ly) % 2 == 0 else 0) + n * 6
            elif mat == "rail":  # machined gunmetal rail with lightening holes
                lum = 140 + 30 * (1 - ty) + n * 6
                if fw >= 3 and fh >= 4 and lx == fw // 2 and ly % 3 == 1:
                    lum = 60
            elif mat == "bright":  # polished bezel / collars
                d2 = abs(tx - 0.5) + abs(ty - 0.5)
                lum = 245 - d2 * 70 + n * 6
                if 0.42 < d2 < 0.5:
                    lum -= 50  # engraved ring
            elif mat == "gauge":
                lum = 200 if (lx in (0, fw - 1) or ly in (0, fh - 1)) else 80 + n * 10
            elif mat == "nozzle":  # heat-scorched bell: darkens + temper bands toward the exit
                lum = 190 - ty * 80 + n * 10
                if ly % 3 == 2:
                    lum -= 18
                if face == "bottom":  # throat
                    edge = min(lx, ly, fw - 1 - lx, fh - 1 - ly)
                    lum = 150 if edge == 0 else 35 + n * 10
            elif mat == "tank":  # cylinder: fake curvature + weld seams + stencil band
                curve = math.cos((tx - 0.32) * math.pi * 0.9)
                lum = 120 + 110 * max(0.0, curve) + n * 8
                if fh > 8 and ly in (1, fh - 2):
                    lum -= 45
                if fh > 8 and ly == fh // 3:
                    lum += 18
            elif mat == "aero":  # skin panel: rivet rows, panel line, leading-edge polish
                lum = 200 - ty * 25 + n * 7
                if ly == 0:
                    lum = 240
                if fw > 6 and lx % 6 == 5:
                    lum -= 32
                if fh > 3 and ly == fh - 2 and lx % 2 == 0:
                    lum += 28
            else:  # armor plate: bevel, panel seams, corner rivets, edge wear
                lum = 196 - ty * 30 + n * 9
                if fw >= 8 and lx == fw // 2:
                    lum -= 30
                if fh >= 8 and ly == fh // 2:
                    lum -= 24
                if fw >= 5 and fh >= 5 and lx in (1, fw - 2) and ly in (1, fh - 2):
                    lum = 250
            # universal bevel + scratches
            if lx == 0 or ly == 0:
                lum += 22
            if lx == fw - 1 or ly == fh - 1:
                lum -= 34
            if n > 0.985:
                lum += 40
            lum *= FACE_LIGHT[face]
            px[y][x] = (lum, lum, lum * 1.02, 255)


def paint_overlay_face(px, mat, face, rect):
    x0, y0, x1, y1 = rect
    fw, fh = x1 - x0, y1 - y0
    for y in range(y0, min(y1, 128)):
        for x in range(x0, min(x1, 128)):
            tx = (x - x0 + 0.5) / max(1, fw)
            ty = (y - y0 + 0.5) / max(1, fh)
            r = math.hypot(tx - 0.5, ty - 0.5) * 2  # 0 centre .. ~1.4 corner
            if mat == "glass":  # faceted mana crystal
                facet = 30 if ((x - x0) + (y - y0)) % 3 == 0 else 0
                px[y][x] = (40 + facet, 200 + facet * 0.5, 255, 255 - r * 60)
                if r < 0.35:
                    px[y][x] = (210, 250, 255, 255)
            elif mat == "core":  # afterburner: white-hot centre -> mana cyan -> blue fringe
                if r < 0.45:
                    px[y][x] = (255, 255, 255, 255)
                elif r < 0.85:
                    px[y][x] = (120, 235, 255, 240)
                else:
                    px[y][x] = (40, 120, 255, 200)
            elif mat == "nav_green":
                px[y][x] = (60, 255, 110, 255)
            elif mat == "nav_red":
                px[y][x] = (255, 50, 40, 255)
            elif mat == "strobe":
                px[y][x] = (255, 255, 255, 255)


def build_armor():
    base, over = blank(128, 128), blank(128, 128)
    boxes = parse_boxes()
    # Big boxes first so small details sharing a texOffs win the overlap
    for u, v, w, h, d in sorted(boxes, key=lambda b: -(b[2] * b[3] * b[4])):
        mat = MATERIAL.get((u, v), "plate")
        for face, rect in faces(u, v, w, h, d).items():
            if mat in EMISSIVE:
                paint_overlay_face(over, mat, face, rect)
            else:
                paint_base_face(base, mat, face, rect, seed=u * 131 + v)
    # Emissive-only parts must stay cut out of the base layer
    for u, v, w, h, d in boxes:
        if MATERIAL.get((u, v)) in EMISSIVE:
            for rect in faces(u, v, w, h, d).values():
                for y in range(rect[1], min(rect[3], 128)):
                    for x in range(rect[0], min(rect[2], 128)):
                        base[y][x] = (0, 0, 0, 0)
    d = os.path.join(ASSETS, "textures/models/armor")
    write_png(os.path.join(d, "elenium_flight_unit.png"), base)
    write_png(os.path.join(d, "elenium_flight_unit_glowmask.png"), over)  # GeckoLib AutoGlowingGeoLayer
    return base, over


# ---------------------------------------------------------------- item icons
class Icon:
    """Two layers: `base` is grayscale (tinted by the dye colour), `acc` is untinted accents/glow."""

    def __init__(self):
        self.base, self.acc = blank(32, 32), blank(32, 32)

    def b(self, x, y, lum, a=255):
        x, y = int(x), int(y)
        if 0 <= x < 32 and 0 <= y < 32:
            self.base[y][x] = (lum, lum, lum, a)

    def a(self, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < 32 and 0 <= y < 32:
            self.acc[y][x] = blend(self.acc[y][x], c)

    def plate(self, x0, y0, x1, y1, lum=200, seed=1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                ty = (y - y0) / max(1, y1 - y0)
                l = lum + 22 - ty * 48 + noise(x, y, seed) * 8
                if x == x0:
                    l += 14
                if x == x1:
                    l -= 26
                self.b(x, y, l)
        for x in range(x0, x1 + 1):
            self.a(x, y0, (255, 255, 255, 90))

    def cylinder(self, x0, y0, x1, y1, lum=190):
        w = max(1, x1 - x0)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                t = (x - x0) / w
                l = lum - 70 + 120 * max(0.0, math.cos((t - 0.3) * math.pi))
                if y in (y0, y1):
                    l -= 30
                self.b(x, y, l)
        hx = x0 + max(1, round(w * 0.3))
        for y in range(y0 + 1, y1):
            self.a(hx, y, (255, 255, 255, 110))

    def disc(self, cx, cy, r, lum=None, col=None):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r:
                    if lum is not None:
                        self.b(x, y, lum - (y - cy) * 8)
                    if col is not None:
                        self.a(x, y, col)

    def crystal(self, cx, cy, r, col=(70, 220, 255)):
        self.disc(cx, cy, r + 1.2, lum=240)
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                dd = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if dd <= r:
                    k = 1 - dd / (r + 0.01)
                    self.a(x, y, (col[0] + (255 - col[0]) * k * 0.7, col[1] + (255 - col[1]) * k * 0.6, 255, 255))
        self.a(int(cx - r * 0.4), int(cy - r * 0.4), (255, 255, 255, 255))

    def flame(self, x0, x1, y0, length, hot=(120, 230, 255), down=True):
        for i in range(length):
            k = i / max(1, length - 1)
            inset = int(k * (x1 - x0 + 1) / 2)
            col = (255, 255, 255) if k < 0.25 else hot
            alpha = 255 * (1 - k * 0.75)
            for x in range(x0 + inset, x1 - inset + 1):
                self.a(x, y0 + i if down else y0 - i, col + (alpha,))

    def rect_acc(self, x0, y0, x1, y1, col):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.a(x, y, col)

    def star(self, cx, cy, col=(255, 255, 255, 255)):
        for dx, dy in ((0, -2), (0, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (0, 1), (-1, 2), (1, 2), (-1, 1), (1, 1)):
            self.a(cx + dx, cy + dy, col)

    def outline(self):
        solid = [[self.base[y][x][3] > 0 or self.acc[y][x][3] > 60 for x in range(32)] for y in range(32)]
        for y in range(32):
            for x in range(32):
                if not solid[y][x] and any(0 <= x + dx < 32 and 0 <= y + dy < 32 and solid[y + dy][x + dx]
                                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    self.acc[y][x] = (18, 20, 26, 255)


def draw_mage(ic, crystal=(70, 220, 255), quad=False):
    for x in (9, 10, 21, 22):  # harness straps
        for y in range(3, 12):
            ic.b(x, y, 110 + (12 if y % 2 else 0))
    ic.plate(9, 6, 22, 8, 230)
    ic.plate(10, 4, 12, 5, 200)
    ic.plate(19, 4, 21, 5, 200)
    ic.plate(7, 9, 24, 19, 205)
    for y in range(10, 19, 2):  # louvers
        ic.b(8, y, 90)
        ic.b(23, y, 90)
    ic.crystal(15.5, 14, 3.2, crystal)
    if quad:
        for cx, cy in ((11, 11), (20, 11), (11, 17), (20, 17)):
            ic.a(cx, cy, crystal + (255,))
    ic.plate(10, 20, 21, 21, 170)
    ic.plate(11, 22, 13, 23, 140)
    ic.plate(18, 22, 20, 23, 140)
    ic.flame(11, 13, 24, 4)
    ic.flame(18, 20, 24, 4)
    for y in range(18, 27):  # single right-leg strut
        ic.b(25, y, 175 - (y - 18) * 4)
        ic.b(26, y, 150)
    ic.disc(25.5, 22, 1.4, lum=225)
    ic.plate(22, 27, 29, 28, 205)
    ic.plate(27, 25, 29, 26, 150)
    ic.flame(27, 29, 29, 3)


def draw_jetpack(ic, hot=(255, 170, 60)):
    for x in (8, 23):
        for y in range(2, 14):
            ic.b(x, y, 112)
    ic.cylinder(5, 4, 12, 22, 200)
    ic.cylinder(19, 4, 26, 22, 200)
    ic.plate(4, 2, 13, 4, 215)
    ic.plate(18, 2, 27, 4, 215)
    for x in range(6, 12):  # intake fan blades
        ic.b(x, 3, 70 if x % 2 else 140)
    for x in range(20, 26):
        ic.b(x, 3, 70 if x % 2 else 140)
    ic.plate(13, 8, 18, 18, 175)
    ic.disc(15.5, 12, 1.6, lum=90)
    ic.a(15, 12, (120, 255, 140, 255))
    ic.plate(6, 23, 11, 25, 140)
    ic.plate(20, 23, 25, 25, 140)
    ic.flame(6, 11, 26, 6, hot)
    ic.flame(20, 25, 26, 6, hot)


def draw_wings(ic, stealth=False):
    for x in range(1, 31):  # swept wings, thinning toward the tips
        span = abs(x - 15.5)
        top = 8 + int(span * 0.35)
        bot = top + max(2, 5 - int(span * 0.15))
        if span < 4:
            continue
        for y in range(top, bot + 1):
            ic.b(x, y, 205 - (y - top) * 14 + (10 if y == top else 0))
        ic.a(x, top, (255, 255, 255, 80))
    ic.plate(12, 6, 19, 22, 195)
    for y in range(1, 10):  # tail fin
        ic.b(15, y, 215 - y * 3)
        ic.b(16, y, 180)
    ic.plate(10, 7, 12, 10, 175)
    ic.plate(19, 7, 21, 10, 175)
    ic.plate(1, 12, 3, 15, 160)
    ic.plate(28, 12, 30, 15, 160)
    if not stealth:
        ic.flame(1, 3, 16, 4)
        ic.flame(28, 30, 16, 4)
        ic.flame(13, 18, 23, 5)
    ic.a(1, 11, (60, 255, 110, 255))
    ic.a(30, 11, (255, 50, 40, 255))


def draw_heavy(ic, hot=(255, 140, 40), hazard=False):
    for x in (3, 28):  # roll cage
        for y in range(5, 24):
            ic.b(x, y, 150)
    ic.cylinder(4, 3, 14, 24, 205)
    ic.cylinder(17, 3, 27, 24, 205)
    ic.plate(5, 1, 13, 2, 175)
    ic.plate(18, 1, 26, 2, 175)
    ic.plate(14, 11, 17, 14, 160)
    if hazard:
        for y in range(16, 20):
            for x in range(4, 28):
                if 4 <= x <= 14 or 17 <= x <= 27:
                    ic.a(x, y, (250, 200, 20, 255) if (x + y) % 4 < 2 else (25, 25, 25, 255))
    ic.plate(5, 25, 13, 27, 135)
    ic.plate(18, 25, 26, 27, 135)
    ic.flame(5, 13, 28, 4, hot)
    ic.flame(18, 26, 28, 4, hot)


def draw_exo(ic):
    draw_mage(ic, quad=False)
    ic.crystal(12.5, 14, 2.2)
    ic.crystal(18.5, 14, 2.2)
    for y in range(2, 9):  # radiator winglets
        ic.b(5, y, 200)
        ic.b(6, y, 170)
        ic.b(25, y, 200)
        ic.b(26, y, 170)
        ic.a(5, y, (120, 230, 255, 140))
        ic.a(26, y, (120, 230, 255, 140))
    for y in range(18, 27):  # second strut
        ic.b(5, y, 175)
        ic.b(6, y, 150)
    ic.disc(5.5, 22, 1.4, lum=225)
    ic.plate(2, 27, 9, 28, 205)
    ic.flame(2, 4, 29, 3)


def draw_siege(ic):
    ic.plate(3, 2, 8, 7, 185)
    ic.plate(23, 2, 28, 7, 185)
    ic.a(5, 4, (255, 60, 40, 255))
    ic.a(25, 4, (255, 60, 40, 255))
    ic.plate(4, 7, 27, 25, 200)
    for cx, cy in ((10, 12), (21, 12), (10, 20), (21, 20)):
        ic.disc(cx, cy, 3.2, lum=120)
        ic.disc(cx, cy, 1.6, col=(255, 170, 60, 255))
        ic.a(cx, cy, (255, 255, 230, 255))
    ic.plate(5, 26, 7, 29, 150)
    ic.plate(24, 26, 26, 29, 150)


def draw_boots(ic):
    for bx in (4, 17):
        ic.plate(bx, 4, bx + 8, 20, 200)
        ic.plate(bx + 6, 12, bx + 10, 19, 160)
        ic.plate(bx - 1, 21, bx + 9, 24, 210)
        ic.plate(bx - 2, 23, bx + 3, 24, 230)
        ic.a(bx + 1, 6, (120, 230, 255, 255))
        ic.a(bx + 1, 7, (120, 230, 255, 160))
        ic.flame(bx + 6, bx + 10, 25, 6)


def draw_skimmer(ic):
    ic.plate(10, 2, 21, 13, 190)
    ic.plate(14, 0, 16, 2, 210)
    ic.plate(12, 13, 19, 15, 160)
    for x in range(2, 30):  # long pontoon ski
        rise = 2 if x < 6 else 0
        for y in range(19 - rise, 23):
            ic.b(x, y, 210 - (y - 17) * 18)
        ic.a(x, 19 - rise, (255, 255, 255, 90))
    ic.plate(26, 15, 27, 18, 170)
    for i, (x, y) in enumerate(((3, 25), (6, 26), (9, 25), (12, 27), (16, 26), (20, 27), (24, 25), (28, 26), (4, 28), (14, 29))):
        ic.a(x, y, (120, 200, 255, 255) if i % 2 else (230, 250, 255, 255))


def draw_scuba(ic):
    ic.cylinder(6, 5, 14, 27, 210)
    ic.cylinder(17, 5, 25, 27, 210)
    for y in (10, 21):
        for x in range(5, 27):
            ic.b(x, y, 95)
    for y in range(13, 17):  # yellow high-visibility dive-tank band
        ic.rect_acc(6, y, 14, y, (235, 190, 30, 255) if y in (13, 16) else (250, 210, 50, 255))
        ic.rect_acc(17, y, 25, y, (235, 190, 30, 255) if y in (13, 16) else (250, 210, 50, 255))
    ic.rect_acc(8, 2, 12, 2, (200, 160, 70, 255))  # brass valve knobs
    ic.rect_acc(19, 2, 23, 2, (200, 160, 70, 255))
    ic.plate(8, 2, 12, 4, 230)
    ic.plate(19, 2, 23, 4, 230)
    ic.plate(12, 2, 19, 3, 200)
    ic.disc(25, 2.5, 2, lum=230)
    ic.a(25, 2, (255, 80, 60, 255))
    for i in range(9):  # breathing hose
        ic.b(27 + (i // 5), 4 + i, 80 if i % 2 else 130)


def draw_mask(ic):
    for x in range(3, 29):  # head strap
        ic.b(x, 9, 100)
        ic.b(x, 10, 120)
    ic.plate(5, 5, 26, 15, 205)
    for y in range(7, 14):  # panoramic glass
        for x in range(7, 25):
            g = (y - 7) / 7
            ic.a(x, y, (60 + g * 40, 170 + g * 30, 220, 235))
    for i in range(4):
        ic.a(9 + i, 8 + i, (255, 255, 255, 200))
    ic.plate(10, 16, 21, 23, 190)
    ic.plate(6, 17, 9, 21, 170)
    ic.plate(22, 17, 25, 21, 170)
    ic.disc(15.5, 24.5, 2.4, lum=150)
    ic.disc(15.5, 24.5, 1, col=(40, 40, 40, 255))


def draw_urban(ic):
    for y in range(2, 13):  # spine
        ic.b(15, y, 200 if y % 2 else 150)
        ic.b(16, y, 170)
    ic.plate(11, 1, 20, 4, 195)
    ic.plate(8, 12, 23, 14, 185)
    for lx in (9, 20):
        for y in range(15, 24):  # thigh struts
            ic.b(lx, y, 190)
            ic.b(lx + 1, y, 160)
        ic.disc(lx + 0.8, 21, 1.8, lum=220)
        for y in range(15, 20):  # piston
            ic.b(lx + 3, y, 235)
        ic.plate(lx + 2, 19, lx + 4, 25, 150)
        ic.plate(lx - 2, 27, lx + 4, 28, 205)
        ic.a(lx, 28, (255, 190, 40, 255))
    ic.a(13, 2, (255, 200, 60, 255))


# id -> (draw, faction decal)
def decal_empire(ic, x, y):
    for dx, dy in ((0, 0), (1, 1), (2, 2), (3, 1), (4, 0)):
        ic.a(x + dx, y + dy, (240, 190, 60, 255))


def decal_roundel(ic, x, y):
    ic.disc(x, y, 2.6, col=(30, 60, 160, 255))
    ic.disc(x, y, 1.7, col=(240, 240, 240, 255))
    ic.disc(x, y, 0.9, col=(200, 30, 30, 255))


def decal_tricolor(ic, x, y):
    for i, c in enumerate(((40, 70, 170, 255), (240, 240, 240, 255), (200, 40, 40, 255))):
        ic.rect_acc(x, y + i * 2, x + 1, y + i * 2 + 1, c)


def decal_white_star(ic, x, y):
    ic.disc(x, y, 3, col=(30, 50, 120, 255))
    ic.star(x, y)


def decal_red_star(ic, x, y):
    ic.star(x, y, (220, 30, 30, 255))


def decal_chevron(ic, x, y, col=(235, 245, 255, 255)):
    for dx in range(5):
        ic.a(x + dx, y + abs(2 - dx), col)
        ic.a(x + dx, y + abs(2 - dx) + 1, col)


ICONS = {
    "elenium_type95_flight_unit": lambda ic: (draw_mage(ic, quad=True), decal_empire(ic, 13, 7)),
    "elenium_type97_flight_unit": lambda ic: (draw_mage(ic), decal_empire(ic, 13, 7)),
    "republic_type101_flight_unit": lambda ic: (draw_wings(ic), decal_tricolor(ic, 15, 2)),
    "federation_type82_flight_unit": lambda ic: (draw_heavy(ic, hot=(255, 90, 40)), decal_red_star(ic, 9, 9), decal_red_star(ic, 22, 9)),
    "allied_type1923_flight_unit": lambda ic: (draw_jetpack(ic, hot=(120, 210, 255)), decal_white_star(ic, 15.5, 15)),
    "commonwealth_mk2_flight_unit": lambda ic: (draw_mage(ic, crystal=(110, 200, 255)), decal_roundel(ic, 15.5, 7)),
    "entente_skirig_flight_unit": lambda ic: (draw_mage(ic, crystal=(150, 255, 200)), decal_chevron(ic, 13, 6)),
    "tactical_combat_jetpack": lambda ic: (draw_jetpack(ic), decal_chevron(ic, 13, 15, (255, 170, 40, 255))),
    "heavy_industrial_rocket_pack": lambda ic: draw_heavy(ic, hazard=True),
    "shadow_recon_wings": lambda ic: (draw_wings(ic, stealth=True), ic.a(15, 14, (255, 40, 60, 255))),
    "elenium_type95_exo": lambda ic: (draw_exo(ic), decal_empire(ic, 13, 7)),
    "titan_siege_frame": lambda ic: (draw_siege(ic), decal_chevron(ic, 13, 8, (255, 200, 40, 255))),
    "valkyrie_thrust_boots": draw_boots,
    "aquasurf_skimmer_unit": lambda ic: (draw_skimmer(ic), decal_chevron(ic, 13, 6, (120, 230, 255, 255))),
    "abyssal_scuba_rig": draw_scuba,
    "abyssal_diving_mask": draw_mask,
    "urban_scout_exolegs": draw_urban,
}


def build_icons():
    out = {}
    for item_id, draw in ICONS.items():
        ic = Icon()
        draw(ic)
        ic.outline()
        tex = os.path.join(ASSETS, "textures/item")
        write_png(os.path.join(tex, item_id + ".png"), ic.base)
        write_png(os.path.join(tex, item_id + "_overlay.png"), ic.acc)
        with open(os.path.join(ASSETS, "models/item", item_id + ".json"), "w") as f:
            json.dump({"parent": "minecraft:item/generated",
                       "textures": {"layer0": "youjosenki:item/" + item_id,
                                    "layer1": "youjosenki:item/" + item_id + "_overlay"}}, f, indent=2)
            f.write("\n")
        out[item_id] = ic
    return out


# ---------------------------------------------------------------- preview sheet
def composite(base, acc, tint):
    h, w = len(base), len(base[0])
    img = blank(w, h)
    for y in range(h):
        for x in range(w):
            r, g, b, a = base[y][x]
            px = (r * tint[0] / 255, g * tint[1] / 255, b * tint[2] / 255, a) if a else (0, 0, 0, 0)
            img[y][x] = blend(px, acc[y][x]) if acc[y][x][3] else px
    return img


def preview(icons, base, over, out_dir):
    tints = {"elenium_type95_flight_unit": 0x262D33, "elenium_type97_flight_unit": 0x38444C, "republic_type101_flight_unit": 0x25384D,
             "federation_type82_flight_unit": 0x5C2424, "allied_type1923_flight_unit": 0x6C7A89, "commonwealth_mk2_flight_unit": 0x5E503F,
             "entente_skirig_flight_unit": 0x3D5A45, "tactical_combat_jetpack": 0x4D5838, "heavy_industrial_rocket_pack": 0xD4A017,
             "shadow_recon_wings": 0x1C1F24, "elenium_type95_exo": 0x22303A, "titan_siege_frame": 0x483C32, "valkyrie_thrust_boots": 0x4A6984,
             "aquasurf_skimmer_unit": 0x1F5B6E, "abyssal_scuba_rig": 0x1C2833, "abyssal_diving_mask": 0x1C2833, "urban_scout_exolegs": 0x4E5559}
    S, cols = 6, 6
    ids = list(icons)
    rows = (len(ids) + cols - 1) // cols
    sheet = [[(45, 45, 52, 255)] * (cols * 34 * S) for _ in range(rows * 34 * S)]
    for i, item_id in enumerate(ids):
        t = tints[item_id]
        img = composite(icons[item_id].base, icons[item_id].acc, ((t >> 16) & 255, (t >> 8) & 255, t & 255))
        ox, oy = (i % cols) * 34 * S + S, (i // cols) * 34 * S + S
        for y in range(32):
            for x in range(32):
                if img[y][x][3]:
                    c = blend((45, 45, 52, 255), img[y][x])
                    for yy in range(S):
                        for xx in range(S):
                            sheet[oy + y * S + yy][ox + x * S + xx] = c
    write_png(os.path.join(out_dir, "icons_preview.png"), sheet)
    arm = composite(base, over, (110, 125, 140))
    S = 4
    big = [[(45, 45, 52, 255)] * (128 * S) for _ in range(128 * S)]
    for y in range(128):
        for x in range(128):
            if arm[y][x][3]:
                for yy in range(S):
                    for xx in range(S):
                        big[y * S + yy][x * S + xx] = blend((45, 45, 52, 255), arm[y][x])
    write_png(os.path.join(out_dir, "armor_preview.png"), big)


if __name__ == "__main__":
    base, over = build_armor()
    icons = build_icons()
    if len(sys.argv) > 1:
        preview(icons, base, over, sys.argv[1])
    print("generated armor + %d icons" % len(icons))
