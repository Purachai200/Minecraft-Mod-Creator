#!/usr/bin/env python3
"""Packs weapon UVs and paints every exoframe weapon cube into all 7 exoframe texture variants.

Materials come from tools/weapon_materials.json (one per cube, written by tools/build_exoframe_geo.py), so the painter
never guesses from cube indices. Each cube is painted face by face: worn gunmetal / blued barrels / wood grain /
polymer stipple / brass / canvas, face shading, grime toward the bottom, rubbed-through edges, paint chips and a
sprayed stencil on the biggest painted face. Run from the repo root (parent of Obsolete/).
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

# Free texture bands for weapon cubes (nothing else in exoframe.geo.json maps here; checked against the atlas).
WEAPON_REGIONS = [(0, 736, 1024, 288), (64, 416, 448, 224)]
MATERIALS_PATH = "Obsolete/tools/weapon_materials.json"   # written by tools/build_exoframe_geo.py


class ShelfPacker:
    """Shelf packer over several rectangles, filled in order, 1 px gutter between patches."""

    def __init__(self, regions):
        self.regions = list(regions)
        self.r = 0
        self._reset()

    def _reset(self):
        x, y, _, _ = self.regions[self.r]
        self.cur_x, self.cur_y, self.row_h = x, y, 0

    def pack(self, w, h):
        while True:
            rx, ry, rw, rh = self.regions[self.r]
            if self.cur_x + w + 1 > rx + rw:
                self.cur_x = rx
                self.cur_y += self.row_h + 1
                self.row_h = 0
            if self.cur_y + h + 1 <= ry + rh and w + 1 <= rw:
                pos = (self.cur_x, self.cur_y)
                self.cur_x += w + 1
                self.row_h = max(self.row_h, h)
                return pos
            self.r += 1
            if self.r >= len(self.regions):
                raise ValueError("weapon UV regions are full")
            self._reset()

    def used(self):
        return self.r, self.cur_y + self.row_h


# ==================== 3. MATERIALS ====================

def get_camo_palette(camo_type):
    return {
        "woodland": ((58, 72, 46), (86, 64, 44), (40, 46, 34)),
        "desert": ((170, 146, 108), (142, 116, 84), (188, 170, 136)),
        "urban": ((84, 90, 98), (56, 60, 66), (120, 128, 136)),
        "arctic": ((206, 212, 216), (158, 166, 172), (92, 98, 104)),
        "tigerstripe": ((70, 78, 52), (40, 40, 36), (112, 98, 66)),
        "hazard": ((214, 168, 32), (52, 52, 54), (230, 190, 52)),
    }.get(camo_type, ((74, 82, 58), (60, 66, 48), (88, 96, 70)))   # factory olive drab


STENCIL = {   # short stencil per weapon, painted on the biggest painted side face
    "weapon_assault_rifle": "20", "weapon_sniper_amr": "20MM", "weapon_machine_gun": "12.7", "weapon_minigun_m134": "762",
    "weapon_rocket_launcher": "HE", "weapon_rpg7_heavy": "PG7", "weapon_battle_rifle": "762", "weapon_autocannon_30mm": "30MM",
    "weapon_shotgun_breacher": "8GA", "weapon_grenade_launcher": "40", "weapon_recoilless_rifle": "84", "weapon_atgm_guided": "AT4",
    "weapon_flamethrower": "FLAM", "weapon_vibro_blade": "V2", "weapon_antitank_rifle": "20", "weapon_pile_bunker": "PB1",
    "weapon_smoke_launcher": "SMK",
}
FONT = {  # 3x5 stencil glyphs, rows top->bottom
    "0": ("111", "101", "101", "101", "111"), "1": ("010", "110", "010", "010", "111"), "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "011", "001", "111"), "4": ("101", "101", "111", "001", "001"), "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"), "7": ("111", "001", "010", "010", "010"), "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"), ".": ("000", "000", "000", "000", "010"), "A": ("010", "101", "111", "101", "101"),
    "E": ("111", "100", "110", "100", "111"), "F": ("111", "100", "110", "100", "100"), "G": ("111", "100", "101", "101", "111"),
    "H": ("101", "101", "111", "101", "101"), "K": ("101", "110", "100", "110", "101"), "L": ("100", "100", "100", "100", "111"),
    "M": ("101", "111", "111", "101", "101"), "P": ("111", "101", "111", "100", "100"), "S": ("111", "100", "111", "001", "111"),
    "T": ("111", "010", "010", "010", "010"), "V": ("101", "101", "101", "101", "010"), "B": ("110", "101", "110", "101", "110"),
}
PAINTED = {"paint", "ammo_can", "fuel", "warhead"}
WORN_EDGE = {"paint", "ammo_can", "fuel", "warhead", "gunmetal", "mag", "polymer", "wood", "optic", "blued"}


def h(x, y, s=0):
    """Deterministic pixel hash in 0..1."""
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def base_color(mat, fx, fy, fw, fh, pal, seed):
    """Material colour at face-local pixel (fx, fy) of an fw x fh face."""
    n = h(fx, fy, seed) - 0.5
    if mat == "gunmetal":
        c = 54 + n * 10
        return c, c + 3, c + 7
    if mat == "blued":
        c = 40 + n * 6 + (4 if fy % 3 == 0 else 0)
        return c, c + 4, c + 14
    if mat == "steel":
        c = 128 + n * 14 + 10 * math.sin(fx * 0.9 + seed)
        return c, c + 4, c + 9
    if mat == "chrome":
        c = 200 + 40 * math.sin(fx * 1.3) + n * 10
        return c, c + 2, c + 6
    if mat == "heat":
        t = fx / max(1, fw - 1)
        r, g, b = (70 + 70 * t, 62 + 30 * t, 70 - 20 * t) if t < 0.6 else (60, 66, 110)
        soot = 28 if t > 0.85 else 0
        return r + n * 10 - soot, g + n * 10 - soot, b + n * 10 - soot
    if mat in ("paint", "ammo_can", "fuel", "warhead"):
        if mat == "fuel":
            col = (150, 38, 30)
        elif mat == "warhead":
            col = (78, 86, 58)
        else:
            blot = int(h(fx // 3, fy // 3, seed + 7) * 5)   # chunky camo blots
            col = pal[0] if blot < 3 else pal[1 if blot == 3 else 2]
            if mat == "ammo_can":
                col = tuple(v - 12 for v in col)
        r, g, b = col
        if h(fx, fy, seed + 3) > 0.94:                      # paint chips down to bare steel
            return 112, 112, 108
        return r + n * 8, g + n * 8, b + n * 8
    if mat == "mag":
        c = 46 + n * 8 + (14 if fy % 3 == 0 else 0)
        return c, c + 2, c + 5
    if mat == "wood":
        grain = 18 * math.sin(fy * 1.7 + 3 * math.sin(fx * 0.35 + seed))
        knot = -30 if h(fx // 2, fy // 2, seed + 11) > 0.97 else 0
        return 122 + grain + knot, 72 + grain * 0.6 + knot, 38 + grain * 0.3 + knot
    if mat == "polymer":
        c = 34 + (6 if h(fx, fy, seed) > 0.6 else 0)
        return c, c, c + 2
    if mat == "rubber":
        c = 24 + (8 if (fx + fy) % 3 == 0 else 0)
        return c, c, c
    if mat == "fabric":
        c = 8 if (fx + fy) % 2 == 0 else -6
        return 92 + c + n * 8, 86 + c + n * 8, 62 + c + n * 6
    if mat == "brass":
        c = n * 16 + (24 if fy == 0 else 0)
        return 206 + c, 164 + c, 64 + c * 0.5
    if mat == "copper":
        return 182 + n * 14, 102 + n * 10, 52 + n * 6
    if mat == "rail":
        return (66, 70, 78) if fx % 3 < 2 else (22, 24, 28)
    if mat == "optic":
        c = 28 + (10 if fx % 4 == 0 else 0)
        return c, c + 2, c + 4
    if mat in ("lens", "lens_g"):
        cx, cy = fw / 2.0, fh / 2.0
        if abs(fx - cx) < 0.8 and abs(fy - cy) < 0.8:
            return (255, 50, 40) if mat == "lens" else (255, 230, 60)
        if abs(fx - fy) <= 0:
            return (190, 245, 255) if mat == "lens" else (170, 255, 210)
        return (34, 110, 190) if mat == "lens" else (30, 150, 90)
    if mat == "hazard":
        return (240, 196, 24) if ((fx + fy) // 2) % 2 == 0 else (26, 28, 30)
    if mat == "perforated":
        if fx % 2 == 1 and fy % 2 == 1:
            return 14, 14, 16
        c = 58 + n * 10
        return c, c + 3, c + 7
    if mat == "shells":
        return (200, 160, 60) if fy >= fh - max(1, fh // 3) else (176 + n * 20, 30, 28)
    if mat == "smoke":
        return (70, 140, 70) if fy == fh // 2 else (190 + n * 10, 192 + n * 10, 186 + n * 10)
    if mat == "ember":
        return (255, 170 + n * 60, 40)
    if mat == "glow":
        return (60, 230, 255) if fx % 4 else (200, 250, 255)
    if mat == "blade_edge":
        return (225, 230, 236) if fy == 0 else (178 + n * 12, 184 + n * 12, 192 + n * 12)
    if mat == "shield_plate":
        r, g, b = (v - 8 for v in pal[0])
        if fx % 8 == 1 and fy % 8 == 1:
            return 180, 190, 205
        return r + n * 8, g + n * 8, b + n * 8
    if mat == "shield_glass":
        return (90, 160, 185) if (fx + fy) % 4 else (150, 200, 215)
    if mat == "stun":
        return (70, 200, 255) if (fx + fy) % 2 == 0 else (220, 245, 255)
    if mat == "graphite":
        c = 45 + ((fx + fy) % 2) * 12
        return c, c, c
    return 60, 62, 66


def faces(u, v, sx, sy, sz):
    """Bedrock box-UV face rects (x, y, w, h, kind)."""
    return [(u + sz, v, sx, sz, "top"), (u + sz + sx, v, sx, sz, "bottom"),
            (u, v + sz, sz, sy, "side"), (u + sz, v + sz, sx, sy, "front"),
            (u + sz + sx, v + sz, sz, sy, "side"), (u + 2 * sz + sx, v + sz, sx, sy, "back")]


SHADE = {"top": 20, "bottom": -26, "side": -6, "front": 0, "back": -10}


def uv_dims(size):
    """GeckoLib box UV uses floor(size) for the face layout (BakedModelFactory.buildQuads)."""
    return tuple(int(math.floor(s + 1e-6)) for s in size)


def patch_size(size):
    """Texture patch reserved for a cube; thin (< 1 px) sides still get a 1 px strip."""
    sx, sy, sz = (max(1, d) for d in uv_dims(size))
    return 2 * (sx + sz), sz + sy


def paint_cube(raw, tw, th, u, v, size, mat, pal, seed, stencil=None):
    sx, sy, sz = uv_dims(size)

    def put(x, y, c):
        if 0 <= x < tw and 0 <= y < th:
            i = (y * tw + x) * 4
            raw[i:i + 4] = bytes((max(0, min(255, int(c[0]))), max(0, min(255, int(c[1]))), max(0, min(255, int(c[2]))), 255))

    # fill the whole patch plus its gutter first: degenerate (0 px) faces sample the patch edge
    pw, ph = patch_size(size)
    for y in range(v - 1, v + ph + 1):
        for x in range(u - 1, u + pw + 1):
            put(x, y, base_color(mat, x - u, y - v, pw, ph, pal, seed))

    for fi, (fx0, fy0, fw, fh, kind) in enumerate(faces(u, v, sx, sy, sz)):
        if fw <= 0 or fh <= 0:
            continue
        for fy in range(fh):
            for fx in range(fw):
                r, g, b = base_color(mat, fx, fy, fw, fh, pal, seed + fi)
                s = SHADE[kind]
                if kind in ("side", "front", "back") and fh > 2:
                    s -= 10 * fy / (fh - 1)                     # grime collects toward the bottom
                if mat in WORN_EDGE and fw >= 3 and fh >= 3 and (fx in (0, fw - 1) or fy in (0, fh - 1)):
                    if h(fx, fy, seed + 5) > 0.35:              # rubbed-through edges
                        r, g, b = r * 0.5 + 60, g * 0.5 + 60, b * 0.5 + 62
                put(fx0 + fx, fy0 + fy, (r + s, g + s, b + s))
        if mat == "warhead" and kind in ("side", "front", "back") and fh >= 3:
            for fx in range(fw):
                put(fx0 + fx, fy0 + fh // 2, (232, 196, 40))
        if mat == "ammo_can" and kind in ("side", "front") and fh >= 4:
            for fx in range(fw):
                put(fx0 + fx, fy0 + 1, (220, 184, 40))           # yellow HE band
        if stencil and kind in ("side", "front") and mat in PAINTED:
            text_w = 4 * len(stencil) - 1
            if fw >= text_w + 2 and fh >= 7:
                ox, oy = fx0 + (fw - text_w) // 2, fy0 + (fh - 5) // 2 + (1 if mat == "ammo_can" else 0)
                ink = (226, 222, 196) if pal[0][0] < 160 else (40, 40, 38)
                for k, ch in enumerate(stencil):
                    for gy, row in enumerate(FONT.get(ch, FONT["0"])):
                        for gx, bit in enumerate(row):
                            if bit == "1" and h(gx + k, gy, seed) > 0.12:   # sprayed, slightly broken stencil
                                put(ox + 4 * k + gx, oy + gy, ink)


# ==================== 4. MAIN ====================

def main():
    print(f"Loading geometry from {GEO_PATH}...")
    with open(GEO_PATH, "r", encoding="utf-8") as f:
        geo = json.load(f)
    with open(MATERIALS_PATH, "r", encoding="utf-8") as f:
        materials = json.load(f)

    bones = geo["minecraft:geometry"][0]["bones"]
    weapon_bones = [b for b in bones if b["name"] in materials and b.get("cubes")]
    missing = [b["name"] for b in bones if "weapon" in b["name"] and b.get("cubes") and b["name"] not in materials]
    assert not missing, f"weapon bones without materials (rerun tools/build_exoframe_geo.py): {missing}"
    print(f"Found {len(weapon_bones)} weapon bones with active geometry cubes.")

    packer = ShelfPacker(WEAPON_REGIONS)
    assignments = []   # (bone, idx, (u, v), size, material, stencil?)
    for b in weapon_bones:
        mats = materials[b["name"]]
        assert len(mats) == len(b["cubes"]), f"{b['name']}: {len(mats)} materials for {len(b['cubes'])} cubes"
        # the stencil goes on the painted cube with the biggest side face
        painted = [i for i, m in enumerate(mats) if m in PAINTED]
        st_idx = max(painted, key=lambda i: b["cubes"][i]["size"][1] * b["cubes"][i]["size"][2], default=None)
        for idx, cube in enumerate(b["cubes"]):
            uv = packer.pack(*patch_size(cube["size"]))
            cube["uv"] = [uv[0], uv[1]]
            assignments.append((b["name"], idx, uv, cube["size"], mats[idx], STENCIL.get(b["name"]) if idx == st_idx else None))

    r, y = packer.used()
    print(f"Packed {len(assignments)} weapon cubes (region {r}, y {y}).")
    with open(GEO_PATH, "w", encoding="utf-8") as f:
        json.dump(geo, f, indent=2)

    for fname, ctype in TEXTURES:
        tpath = os.path.join(TEX_DIR, fname)
        if not os.path.exists(tpath):
            print(f"Warning: {tpath} not found, skipping.")
            continue
        tw, th, raw = decode_png(tpath)
        pal = get_camo_palette(ctype)
        for k, (wname, idx, (ux, uy), size, mat, stencil) in enumerate(assignments):
            paint_cube(raw, tw, th, ux, uy, size, mat, pal, seed=k * 31 + idx, stencil=stencil)
        encode_png(tpath, tw, th, raw)
        print(f"  wrote {tpath} ({ctype})")
    print("All weapon UVs and textures generated.")


if __name__ == "__main__":
    main()
