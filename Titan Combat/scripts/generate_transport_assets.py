#!/usr/bin/env python3
"""
Titan Combat - Master Transport Vehicles Asset Generator (v3.0 - GeckoLib Model Architect Standard)
Iconic military transport concept showcase with high-fidelity mechanical anatomy:
1. Hauler Truck (Oshkosh HEMTT 8x8 Military Titan Transporter with full cab detailing, front recovery winch,
   headache rack, dual exhausts, spare tire carrier, toolboxes, suspension differentials, and orange ratchet tie-down straps)
2. Sky-Crane Drone (Heavy Quad Ducted-Fan Dropship with forward gunship canopy, chin EO/IR sensor turret,
   dorsal turboshafts, stator vanes, landing skids, ventral winch, and cyan mag-clamp spreader rig)
3. Cargo Landing Barge (Catamaran Landing Craft LCU with wave-piercing bows, hydraulic drop ramp,
   panoramic wheelhouse bridge with wings, rotating radar mast, mooring bitts, life buoys, and twin waterjets)

GeckoLib / Bedrock Coordinate Convention:
- Front: -Z
- Back:  +Z
- Right: -X
- Left:  +X
- Up:    +Y
"""

import json
import os
import shutil
import struct
import zlib
import math

def make_png(w, h, rgba_bytes):
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    raw = bytearray()
    for y in range(h):
        raw.append(0) # filter None
        raw.extend(rgba_bytes[y*w*4 : (y+1)*w*4])
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw), 9)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')

class TextureDrawer:
    def __init__(self, w=512, h=512):
        self.w = w
        self.h = h
        self.buf = bytearray([0] * (w * h * 4))

    def set_pixel(self, x, y, r, g, b, a=255):
        if 0 <= x < self.w and 0 <= y < self.h:
            idx = (y * self.w + x) * 4
            self.buf[idx] = max(0, min(255, int(r)))
            self.buf[idx+1] = max(0, min(255, int(g)))
            self.buf[idx+2] = max(0, min(255, int(b)))
            self.buf[idx+3] = max(0, min(255, int(a)))

    def fill_rect(self, x0, y0, w, h, r, g, b, a=255):
        for y in range(y0, min(self.h, y0 + h)):
            for x in range(x0, min(self.w, x0 + w)):
                self.set_pixel(x, y, r, g, b, a)

    def draw_panel(self, x0, y0, w, h, base_rgb, rivet=True):
        br, bg, bb = base_rgb
        for y in range(y0, min(self.h, y0 + h)):
            for x in range(x0, min(self.w, x0 + w)):
                # Subtle metallic grit & rolled-steel texture
                noise = ((x * 17 + y * 31) % 9) - 4
                self.set_pixel(x, y, max(0, min(255, br + noise)), max(0, min(255, bg + noise)), max(0, min(255, bb + noise)))

        # 3D Bevel highlight & shadow
        for x in range(x0, min(self.w, x0 + w)):
            self.set_pixel(x, y0, min(255, br + 35), min(255, bg + 35), min(255, bb + 35))
            self.set_pixel(x, min(self.h - 1, y0 + h - 1), max(0, br - 40), max(0, bg - 40), max(0, bb - 40))
        for y in range(y0, min(self.h, y0 + h)):
            self.set_pixel(x0, y, min(255, br + 28), min(255, bg + 28), min(255, bb + 28))
            self.set_pixel(min(self.w - 1, x0 + w - 1), y, max(0, br - 40), max(0, bg - 40), max(0, bb - 40))

        # Panel Seam Grid dividing large 32+ px plates
        if w >= 32:
            mid_x = x0 + w // 2
            for y in range(y0 + 1, min(self.h, y0 + h - 1)):
                self.set_pixel(mid_x, y, max(0, br - 45), max(0, bg - 45), max(0, bb - 45))
                self.set_pixel(mid_x + 1, y, min(255, br + 20), min(255, bg + 20), min(255, bb + 20))
        if h >= 32:
            mid_y = y0 + h // 2
            for x in range(x0 + 1, min(self.w, x0 + w - 1)):
                self.set_pixel(x, mid_y, max(0, br - 45), max(0, bg - 45), max(0, bb - 45))
                self.set_pixel(x, mid_y + 1, min(255, br + 20), min(255, bg + 20), min(255, bb + 20))

        # 3D Rivets with drop shadow along borders
        if rivet and w > 14 and h > 14:
            for rx in range(x0 + 4, x0 + w - 4, 12):
                for ry in (y0 + 3, y0 + h - 4):
                    self.set_pixel(rx, ry, min(255, br + 45), min(255, bg + 45), min(255, bb + 45))
                    self.set_pixel(rx, ry + 1, max(0, br - 50), max(0, bg - 50), max(0, bb - 50))
            for ry in range(y0 + 4, y0 + h - 4, 12):
                for rx in (x0 + 3, x0 + w - 4):
                    self.set_pixel(rx, ry, min(255, br + 45), min(255, bg + 45), min(255, bb + 45))
                    self.set_pixel(rx, ry + 1, max(0, br - 50), max(0, bg - 50), max(0, bb - 50))

    def draw_camo(self, x0, y0, w, h, colors, seam=16):
        """Disruptive camo over riveted plates. colors = (base, blotch A, blotch B, shadow).
        Plate seams every `seam` px from each corner, so even small faces (which sample a 64px cell's corner) show plating."""
        for y in range(y0, min(self.h, y0 + h)):
            for x in range(x0, min(self.w, x0 + w)):
                n1 = math.sin(x * 0.19 + 1.3) + math.sin(y * 0.23 + 2.2) + math.sin((x + y) * 0.11 + 0.7)
                n2 = math.sin(x * 0.13 + 4.1) + math.sin(y * 0.29 + 5.0) + math.sin((x - y) * 0.09 + 3.3)
                c = colors[0]
                if n1 > 0.9:
                    c = colors[1]
                if n2 > 1.3:
                    c = colors[2]
                if n1 < -1.7:
                    c = colors[3]
                grit = ((x * 17 + y * 31) % 7) - 3
                self.set_pixel(x, y, c[0] + grit, c[1] + grit, c[2] + grit)
        shade = lambda x, y, d: self.set_pixel(x, y, *[v + d for v in self.buf[(y * self.w + x) * 4:(y * self.w + x) * 4 + 3]])
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                lx, ly = x - x0, y - y0
                if lx % seam == 0 or ly % seam == 0:
                    shade(x, y, -38)          # seam groove
                elif lx % seam == 1 or ly % seam == 1:
                    shade(x, y, 16)           # lit plate edge
                elif lx % seam in (3, seam - 3) and ly % seam in (3, seam - 3):
                    shade(x, y, 40)           # rivet head
                    if y + 1 < y0 + h:
                        shade(x, y + 1, -30)

    ACCENTS = [(255, 170, 30), (190, 32, 30), (226, 226, 214), (240, 112, 20), (238, 198, 40), (30, 30, 32),
               (182, 188, 198), (190, 150, 70), (176, 156, 112), (82, 92, 60), (168, 172, 170), (40, 60, 100),
               (96, 78, 52), (122, 62, 36), (40, 220, 90), (60, 200, 255)]

    def draw_accents(self):
        """Row of 32x64 colour swatches at y384 (see accent()), plus muddy camo for low parts at (0,448)."""
        for i, (r, g, b) in enumerate(self.ACCENTS):
            for y in range(384, 448):
                for x in range(i * 32, i * 32 + 32):
                    n = ((x * 13 + y * 7) % 5) - 2
                    edge = 18 if y == 384 or x == i * 32 else (-22 if x == i * 32 + 31 else 0)
                    self.set_pixel(x, y, r + n + edge, g + n + edge, b + n + edge)
        self.draw_camo(0, 448, 128, 64, ((88, 84, 58), (100, 82, 54), (72, 64, 44), (58, 50, 36)))

    FONT = {"0": "111101101101111", "1": "010110010010111", "4": "101101111001001", "7": "111001010010010",
            "T": "111010010010010", "S": "111100111001111", "C": "111100100100111", "L": "100100100100111",
            "-": "000000111000000"}

    def draw_text(self, x0, y0, text, rgb, scale=2):
        """3x5 stencil lettering for unit numbers."""
        for i, ch in enumerate(text):
            bits = self.FONT[ch]
            for k, bit in enumerate(bits):
                if bit == "1":
                    self.fill_rect(x0 + i * 4 * scale + (k % 3) * scale, y0 + (k // 3) * scale, scale, scale, *rgb)

    def draw_armor_atlas(self, colors, stencil):
        """128x128 armor block at (0,0): plain camo, camo + unit number, camo + engine louvers, darker roof camo."""
        self.draw_camo(0, 0, 128, 128, colors)
        self.draw_text(68, 4, stencil, (222, 222, 205))
        for y in range(68, 92, 4):
            self.fill_rect(4, y, 40, 2, 16, 18, 16)
        dark = tuple(tuple(max(0, v - 14) for v in c) for c in colors)
        self.draw_camo(64, 64, 64, 64, dark)

    def draw_hazard_stripes(self, x0, y0, w, h, stripe_w=8):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                diag = (x - x0 + y - y0) // stripe_w
                noise = ((x * 7 + y * 11) % 5) - 2
                if diag % 2 == 0:
                    self.set_pixel(x, y, max(0, min(255, 245 + noise)), max(0, min(255, 185 + noise)), 15) # Safety Yellow
                else:
                    self.set_pixel(x, y, max(0, min(255, 28 + noise)), max(0, min(255, 28 + noise)), 32) # Dark Charcoal Black

    def draw_orange_strap(self, x0, y0, w, h):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                pattern = (x + y) % 4
                if pattern == 0:
                    self.set_pixel(x, y, 255, 145, 25) # Bright weave
                elif pattern == 2:
                    self.set_pixel(x, y, 190, 70, 0)   # Dark groove
                else:
                    self.set_pixel(x, y, 235, 95, 0)   # High-vis orange
        for x in range(x0, x0 + w):
            self.set_pixel(x, y0, 20, 20, 25)
            self.set_pixel(x, y0 + h - 1, 20, 20, 25)

    def draw_diamond_plate(self, x0, y0, w, h):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                noise = ((x * 13 + y * 23) % 7) - 3
                self.set_pixel(x, y, 50 + noise, 55 + noise, 60 + noise)
        for y in range(y0, y0 + h - 4, 6):
            for x in range(x0, x0 + w - 4, 6):
                self.set_pixel(x + 1, y + 1, 135, 145, 160)
                self.set_pixel(x + 2, y + 2, 115, 125, 140)
                self.set_pixel(x + 3, y + 3, 25, 28, 32)
                self.set_pixel(x + 4, y + 2, 135, 145, 160)
                self.set_pixel(x + 5, y + 1, 25, 28, 32)

    def draw_glass(self, x0, y0, w, h):
        # Clear pane with a dark gasket: the renderer is cutout, so alpha-0 pixels are see-through
        # (translucent glass would write depth and hide Titans standing behind it).
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                edge = x in (x0, x0 + w - 1) or y in (y0, y0 + h - 1)
                self.set_pixel(x, y, 18, 20, 22, 255 if edge else 0)

    def draw_tire(self, x0, y0, w, h):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                if (x + y) % 6 < 2:
                    self.set_pixel(x, y, 52, 54, 58) # Deep lug highlight
                else:
                    self.set_pixel(x, y, 20, 21, 23) # Dark rubber

    def draw_wheel_rim(self, x0, y0, w, h):
        cx = x0 + w // 2
        cy = y0 + h // 2
        r_outer = min(w, h) // 2 - 2
        r_inner = r_outer // 2
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if d2 <= r_outer ** 2:
                    if d2 <= r_inner ** 2:
                        self.set_pixel(x, y, 42, 45, 50)
                    else:
                        self.set_pixel(x, y, 82, 88, 96) # Heavy steel rim
                else:
                    self.set_pixel(x, y, 20, 21, 23)
        # 8 bright silver lug nuts around hub
        for i in range(8):
            ang = i * (2 * math.pi / 8)
            lx = int(cx + (r_inner + 4) * math.cos(ang))
            ly = int(cy + (r_inner + 4) * math.sin(ang))
            self.set_pixel(lx, ly, 230, 235, 245)
            self.set_pixel(lx+1, ly, 185, 190, 200)

    def draw_diamond_plate(self, x0, y0, w, h):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                if (x // 3 + y // 3) % 2 == 0:
                    self.set_pixel(x, y, 82, 86, 92)
                else:
                    self.set_pixel(x, y, 54, 57, 62)

    def draw_grille(self, x0, y0, w, h):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                if y % 4 == 0:
                    self.set_pixel(x, y, 90, 95, 100) # Chrome bar
                else:
                    self.set_pixel(x, y, 16, 17, 18) # Dark mesh
        if w >= 32 and h >= 16:
            # Dual round headlights
            for y in range(y0 + 2, y0 + 12):
                for x in range(x0 + 2, x0 + 12):
                    self.set_pixel(x, y, 255, 250, 200)
                for x in range(x0 + w - 12, x0 + w - 2):
                    self.set_pixel(x, y, 255, 250, 200)
            # Amber turn indicators below
            for y in range(y0 + 12, min(y0 + 16, y0 + h)):
                for x in range(x0 + 3, x0 + 11):
                    self.set_pixel(x, y, 255, 165, 20)
                for x in range(x0 + w - 11, x0 + w - 3):
                    self.set_pixel(x, y, 255, 165, 20)

    def draw_winch_drum(self, x0, y0, w, h):
        self.fill_rect(x0, y0, w, h, 38, 42, 46)
        # Wound braided steel cable lines
        for y in range(y0 + 2, y0 + h - 2):
            for x in range(x0 + 4, x0 + w - 4):
                if (x + y) % 3 == 0:
                    self.set_pixel(x, y, 195, 205, 215) # Silver cable highlight
                else:
                    self.set_pixel(x, y, 120, 130, 140) # Cable shadow
        # Flange rims
        self.fill_rect(x0, y0, 4, h, 60, 65, 72)
        self.fill_rect(x0 + w - 4, y0, 4, h, 60, 65, 72)

    def draw_exhaust_stack(self, x0, y0, w, h):
        self.fill_rect(x0, y0, w, h, 52, 55, 60)
        # Perforated heat guard holes
        for y in range(y0 + 4, y0 + h - 4, 4):
            for x in range(x0 + 4, x0 + w - 4, 4):
                self.set_pixel(x, y, 20, 22, 24)
                self.set_pixel(x + 1, y, 20, 22, 24)

    def draw_tail_lights(self, x0, y0, w, h):
        self.fill_rect(x0, y0, w, h, 24, 25, 27)
        third = w // 3
        # Red stop/brake
        self.fill_rect(x0 + 1, y0 + 1, third - 2, h - 2, 235, 25, 25)
        # Amber turn
        self.fill_rect(x0 + third + 1, y0 + 1, third - 2, h - 2, 255, 160, 20)
        # White reverse
        self.fill_rect(x0 + third * 2 + 1, y0 + 1, third - 2, h - 2, 240, 245, 250)

    def draw_life_ring(self, x0, y0, w, h):
        cx = x0 + w // 2
        cy = y0 + h // 2
        r_out = min(w, h) // 2 - 1
        r_in = r_out // 2
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if r_in ** 2 <= d2 <= r_out ** 2:
                    # White reflective quadrants
                    ang = math.atan2(y - cy, x - cx)
                    if abs(math.sin(ang * 2)) < 0.35:
                        self.set_pixel(x, y, 245, 245, 250)
                    else:
                        self.set_pixel(x, y, 255, 90, 10) # Safety Orange

    def draw_hydraulic_cylinder(self, x0, y0, w, h):
        # Cylinder barrel (dark industrial green/black)
        half_h = h // 2
        self.fill_rect(x0, y0, w, half_h, 45, 52, 48)
        # Chrome piston rod
        self.fill_rect(x0 + 2, y0 + half_h, w - 4, half_h, 220, 225, 235)
        for y in range(y0 + half_h, y0 + h):
            self.set_pixel(x0 + 3, y, 255, 255, 255) # Specular highlight

    def save(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data = make_png(self.w, self.h, bytes(self.buf))
        with open(filepath, 'wb') as f:
            f.write(data)
        print(f"Saved texture: {filepath} ({len(data)} bytes)")


AMBER, RED, WHITE, ORANGE, YELLOW, BLACK, CHROME, BRASS, SAND, OLIVE, LIGHT_GREY, NAVY, MUD, RUST, GREEN_LAMP, CYAN_LAMP = range(16)
MUDDY = [0, 448]


def accent(i):
    """UV of a TextureDrawer.draw_accents() colour swatch."""
    return [i * 32, 384]


def rod(base, top, w, t, uv):
    """Cube whose long (+Y) axis runs from base to top, pivoted at base.
    A cube without "pivot" rotates around the model origin in GeckoLib, so every tilted part goes through here.
    GeckoLib bakes rotation as Rz*Ry*Rx with X negated, giving direction (sin rz cos rx, cos rz cos rx, -sin rx)."""
    dx, dy, dz = (top[i] - base[i] for i in range(3))
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    rx = -math.degrees(math.asin(dz / length))
    rz = math.degrees(math.atan2(dx, dy))
    r = lambda v: round(v, 3)
    return {"origin": [r(base[0] - w / 2), r(base[1]), r(base[2] - t / 2)], "size": [w, r(length), t],
            "pivot": [r(v) for v in base], "rotation": [r(rx), 0, r(rz)], "uv": uv}


def per_face_uv(bones):
    """Box UV on big cubes unfolds across neighbouring texture regions (e.g. orange straps on hull sides).
    Map every face to its own material instead: 1 texel per unit from the cube's "uv", cropped at the 64px atlas cell."""
    for bone in bones:
        for c in bone.get("cubes", []):
            u, v = c.pop("uv")
            cw, ch = 64 - u % 64, 64 - v % 64
            sx, sy, sz = c["size"]
            dims = {"north": (sx, sy), "south": (sx, sy), "east": (sz, sy), "west": (sz, sy), "up": (sx, sz), "down": (sx, sz)}
            c["uv"] = {f: {"uv": [u, v], "uv_size": [min(max(w, 1), cw), min(max(h, 1), ch)]} for f, (w, h) in dims.items()}
    return bones


def _rod_selfcheck():
    c = rod((1, 2, 3), (5, 9, -4), 2, 2, [0, 0])
    rx, rz = math.radians(c["rotation"][0]), math.radians(c["rotation"][2])
    d = (math.sin(rz) * math.cos(rx), math.cos(rz) * math.cos(rx), -math.sin(rx))
    want = (4, 7, -7)
    n = math.sqrt(sum(v * v for v in want))
    assert all(abs(d[i] - want[i] / n) < 1e-3 for i in range(3)), d
    assert abs(c["size"][1] - n) < 1e-2


def write_geo(path, identifier, bones, bounds_w, bounds_h, bounds_y):
    model_data = {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": identifier,
                "texture_width": 512,
                "texture_height": 512,
                "visible_bounds_width": bounds_w,
                "visible_bounds_height": bounds_h,
                "visible_bounds_offset": [0, bounds_y, 0]
            },
            "bones": per_face_uv(bones)
        }]
    }
    with open(path, 'w') as f:
        json.dump(model_data, f, indent=2)
    print(f"Saved model: {path}")


# ==============================================================================
# 1. 8x8 HEAVY TRANSPORTER HAULER TRUCK (MASTER SPEC)
# ==============================================================================


def make_wheel(cx, cy, cz, x0, width, r):
    """Tyre as three square slabs turned 0/+30/-30 deg about the axle: a 12-lobed outline that reads round
    and doubles as tread lugs. Rim disc + hub on the outer face (+X is the vehicle's left)."""
    tyre = [{"origin": [x0, cy - r, cz - r], "size": [width, 2 * r, 2 * r], "pivot": [cx, cy, cz],
             "rotation": [a, 0, 0], "uv": [0, 256]} for a in (0, 30, -30)]
    rim_x = x0 + width - 0.6 if cx > 0 else x0 - 0.6
    hub_x = x0 + width + 0.4 if cx > 0 else x0 - 1.4
    rim = [{"origin": [rim_x, cy - 9, cz - 9], "size": [1.2, 18, 18], "pivot": [cx, cy, cz], "rotation": [a, 0, 0],
            "uv": [256, 256]} for a in (0, 45)]
    hub = [{"origin": [hub_x, cy - 3, cz - 3], "size": [1, 6, 6], "uv": accent(OLIVE)}]
    return tyre + rim + hub


def make_ducted_fan_cowling(cx, cz):
    """Generates a round 8-sided faceted military ducted fan nacelle with top intake lip and stator guide vanes."""
    cubes = [
        # 4 Cardinal outer armor walls (Military Olive Camo Armor: uv [0, 0])
        {"origin": [cx - 8, 20, cz - 16], "size": [16, 12, 3], "uv": [0, 0]}, # North
        {"origin": [cx - 8, 20, cz + 13], "size": [16, 12, 3], "uv": [0, 0]}, # South
        {"origin": [cx - 16, 20, cz - 8], "size": [3, 12, 16], "uv": [0, 0]}, # West
        {"origin": [cx + 13, 20, cz - 8], "size": [3, 12, 16], "uv": [0, 0]}, # East

        # 4 Diagonal Corner walls connecting the cardinal walls (forming an 8-sided aerodynamic ring)
        {"origin": [cx - 14, 20, cz - 14], "size": [6, 12, 6], "uv": [0, 0]}, # NW
        {"origin": [cx + 8,  20, cz - 14], "size": [6, 12, 6], "uv": [0, 0]}, # NE
        {"origin": [cx - 14, 20, cz + 8],  "size": [6, 12, 6], "uv": [0, 0]}, # SW
        {"origin": [cx + 8,  20, cz + 8],  "size": [6, 12, 6], "uv": [0, 0]}, # SE

        # Aerodynamic Dark Carbon Top Intake Lip (uv [384, 0])
        {"origin": [cx - 9, 31.8, cz - 16.5], "size": [18, 1.2, 3.5], "uv": [384, 0]},
        {"origin": [cx - 9, 31.8, cz + 13],   "size": [18, 1.2, 3.5], "uv": [384, 0]},
        {"origin": [cx - 16.5, 31.8, cz - 9], "size": [3.5, 1.2, 18], "uv": [384, 0]},
        {"origin": [cx + 13,   31.8, cz - 9], "size": [3.5, 1.2, 18], "uv": [384, 0]},
        {"origin": [cx - 14.5, 31.8, cz - 14.5], "size": [6.5, 1.2, 6.5], "uv": [384, 0]},
        {"origin": [cx + 8,    31.8, cz - 14.5], "size": [6.5, 1.2, 6.5], "uv": [384, 0]},
        {"origin": [cx - 14.5, 31.8, cz + 8],    "size": [6.5, 1.2, 6.5], "uv": [384, 0]},
        {"origin": [cx + 8,    31.8, cz + 8],    "size": [6.5, 1.2, 6.5], "uv": [384, 0]},

        # Aerodynamic Cross Guide Vanes & Stator Hub (uv [256, 0])
        {"origin": [cx - 13, 22, cz - 1], "size": [26, 2, 2], "uv": [256, 0]},
        {"origin": [cx - 1, 22, cz - 13], "size": [2, 2, 26], "uv": [256, 0]},
        {"origin": [cx - 3.5, 21, cz - 3.5], "size": [7, 4, 7], "uv": [256, 0]}
    ]
    return cubes


def generate_hauler_truck_texture(path):
    tex = TextureDrawer(512, 512)
    tex.fill_rect(0, 0, 512, 512, 35, 38, 42)

    # (0, 0, 128, 128): Olive drab military armor plating
    tex.draw_armor_atlas(((72, 85, 58), (52, 62, 42), (112, 102, 74), (34, 38, 30)), "T-07")
    tex.draw_wheel_rim(256, 256, 18, 18)

    # (128, 0, 64, 64): Ballistic Windshield Glass
    tex.draw_glass(128, 0, 64, 64)

    # (192, 0, 64, 64): Front Radiator Grille & Headlights
    # Drawn at the truck grille face's exact 44x16 size so both headlights land on it
    tex.draw_grille(192, 0, 44, 16)

    # (256, 0, 128, 64): Dark chassis steel frame
    tex.draw_panel(256, 0, 128, 64, (45, 48, 52), rivet=False)

    # (384, 0, 128, 128): Diamond plate cargo flatbed deck
    tex.draw_diamond_plate(384, 0, 128, 128)

    # (0, 128, 128, 64): Hazard warning stripes (bumper & sides)
    tex.draw_hazard_stripes(0, 128, 128, 64)

    # (128, 128, 128, 64): High-Vis Orange Tie-Down Straps
    tex.draw_orange_strap(128, 128, 128, 64)

    # (256, 128, 128, 64): Exhaust Smokestacks & Perforated Heat Guards
    tex.draw_exhaust_stack(256, 128, 128, 64)

    # (384, 128, 128, 64): Front Recovery Winch Drum & Steel Cable
    tex.draw_winch_drum(384, 128, 128, 64)

    # (0, 192, 128, 64): Tail Light Clusters & Amber Markers
    tex.draw_tail_lights(0, 192, 128, 64)

    # (128, 192, 128, 64): Axle Differentials & Suspension Springs
    tex.draw_panel(128, 192, 128, 64, (55, 58, 62), rivet=False)

    # (256, 192, 128, 64): Toolboxes & Air Brake Reservoirs
    tex.draw_panel(256, 192, 128, 64, (64, 74, 52))

    # (384, 192, 128, 64): Cab Roof Lightbar & Air Horns
    tex.fill_rect(384, 192, 128, 64, 40, 42, 46)
    tex.fill_rect(390, 196, 116, 16, 255, 215, 60) # Amber roof markers

    # (0, 256, 128, 128): Mud-Terrain Tire Tread Lugs
    tex.draw_tire(0, 256, 128, 128)

    # (128, 256, 128, 128): Wheel Rim with Lug Nuts
    tex.draw_wheel_rim(128, 256, 128, 128)

    tex.draw_accents()
    tex.save(path)


def generate_hauler_truck_model(path):
    # Conventional-nose 8x8 hauler, ~12.5 x 4 x 5 blocks. GeckoLib mirrors X on load: +X here is the vehicle's LEFT.
    # Cab is sized for a seated player: driver cushion top y42 (left seat, x+13, z-56), roof underside y74.
    W = 30
    glass, armor, stencil, louver, roof, steel = [128, 0], [0, 0], [64, 0], [0, 64], [64, 64], [256, 0]
    body = [
        # Ladder frame and axle differentials
        {"origin": [-15, 14, -94], "size": [4, 8, 186], "uv": steel},
        {"origin": [11, 14, -94], "size": [4, 8, 186], "uv": steel},
        *[{"origin": [-5, 10, z - 4], "size": [10, 8, 8], "uv": [128, 192]} for z in (-68, -42, 40, 66)],
        # ---- Front end: bumper, tow hooks, winch, brush guard ----
        {"origin": [-32, 10, -106], "size": [64, 12, 6], "uv": [0, 128]},
        {"origin": [-27, 12, -108], "size": [4, 6, 2], "uv": accent(RED)},       # tow hooks
        {"origin": [23, 12, -108], "size": [4, 6, 2], "uv": accent(RED)},
        {"origin": [-10, 13, -109], "size": [20, 8, 3], "uv": [384, 128]},
        *[{"origin": [x, 22, -105], "size": [2, 18, 2], "uv": accent(BLACK)} for x in (-21, -9, 7, 19)],
        {"origin": [-23, 40, -105], "size": [46, 2, 2], "uv": accent(BLACK)},
        *[{"origin": [x, 30, -104.8], "size": [9, 10, 1], "uv": accent(CHROME)} for x in (-30.5, 21.5)],  # headlight bezels
        {"origin": [-6, 16, -106.6], "size": [12, 4, 1], "uv": accent(WHITE)},   # number plate
        # ---- Bonnet with louvers, raked top, headlight pods, indicator lamps ----
        {"origin": [-24, 22, -104], "size": [48, 18, 24], "uv": louver},
        rod((0, 40, -104), (0, 46, -80), 44, 2, louver),                     # bonnet top slopes up to the cowl
        rod((23, 38, -92), (19, 42, -92), 2, 24, armor),                     # bevelled bonnet shoulders
        rod((-23, 38, -92), (-19, 42, -92), 2, 24, armor),
        {"origin": [-22, 23, -104.6], "size": [44, 15, 1], "uv": [192, 0]},  # grille
        {"origin": [-30, 28, -102], "size": [7, 8, 6], "uv": [84, 192]},     # headlight pods
        {"origin": [23, 28, -102], "size": [7, 8, 6], "uv": [84, 192]},
        {"origin": [-30, 24, -101], "size": [7, 3, 5], "uv": [42, 192]},     # amber indicators
        {"origin": [23, 24, -101], "size": [7, 3, 5], "uv": [42, 192]},
        # Front wheel arches (flat top with sloped ends)
        *[c for x0 in (-32, 20) for c in (
            {"origin": [x0, 30, -80], "size": [12, 2, 24], "uv": MUDDY},
            rod((x0 + 6, 22, -86), (x0 + 6, 31, -80), 12, 2, MUDDY),
            rod((x0 + 6, 31, -56), (x0 + 6, 22, -50), 12, 2, MUDDY),
        )],
        # ---- Cab (z -80..-40): floor y34, roof y74 ----
        {"origin": [-W, 28, -80], "size": [60, 6, 40], "uv": MUDDY},         # cab floor/sill
        *[{"origin": [x, 44, -60], "size": [1, 2, 5], "uv": accent(CHROME)} for x in (-30.6, 29.6)],  # door handles
        rod((-14, 48, -81.4), (-4, 54, -80.2), 1, 1, accent(BLACK)),        # wipers
        rod((14, 48, -81.4), (4, 54, -80.2), 1, 1, accent(BLACK)),
        {"origin": [-W, 34, -82], "size": [60, 14, 2], "uv": armor},         # cowl under the windshield
        rod((0, 48, -81), (0, 74, -76), 56, 1, glass),                       # raked windshield
        rod((-29, 48, -81.5), (-29, 74, -76.5), 2, 3, armor),                # A-pillars + centre post
        rod((29, 48, -81.5), (29, 74, -76.5), 2, 3, armor),
        rod((0, 48, -81.6), (0, 74, -76.6), 2, 2, armor),
        {"origin": [-W, 34, -78], "size": [2, 18, 36], "uv": stencil},       # doors carry the unit number
        {"origin": [W - 2, 34, -78], "size": [2, 18, 36], "uv": stencil},
        {"origin": [-W + 0.5, 52, -76], "size": [1, 20, 26], "uv": glass},   # side windows
        {"origin": [W - 1.5, 52, -76], "size": [1, 20, 26], "uv": glass},
        {"origin": [-W, 52, -50], "size": [2, 22, 10], "uv": armor},         # B-pillars
        {"origin": [W - 2, 52, -50], "size": [2, 22, 10], "uv": armor},
        {"origin": [-W, 72, -78], "size": [2, 2, 28], "uv": armor},          # window headers
        {"origin": [W - 2, 72, -78], "size": [2, 2, 28], "uv": armor},
        # Back wall with a small rear window
        {"origin": [-W, 34, -42], "size": [60, 22, 2], "uv": armor},
        {"origin": [-W, 68, -42], "size": [60, 6, 2], "uv": armor},
        {"origin": [-W, 56, -42], "size": [16, 12, 2], "uv": armor},
        {"origin": [14, 56, -42], "size": [16, 12, 2], "uv": armor},
        {"origin": [-14, 56, -41.5], "size": [28, 12, 1], "uv": glass},
        # Roof with chamfered edges, visor, marker lamps, lightbar, antenna
        {"origin": [-28, 74, -78], "size": [56, 3, 38], "uv": roof},
        rod((-30, 73, -59), (-27, 77, -59), 2, 38, roof),
        rod((30, 73, -59), (27, 77, -59), 2, 38, roof),
        {"origin": [-28, 73, -82], "size": [56, 2, 4], "uv": steel},
        *[{"origin": [x - 1.5, 77, -78], "size": [3, 1.5, 2], "uv": [392, 196]} for x in (-16, -8, 0, 8, 16)],
        {"origin": [-18, 77, -74], "size": [36, 3, 4], "uv": [384, 192]},
        rod((24, 77, -46), (24, 100, -48), 1, 1, steel),
        *[c for x in (-23, 19) for c in (                                    # amber roof beacons
            {"origin": [x, 77, -48], "size": [4, 1, 4], "uv": accent(BLACK)},
            {"origin": [x + 0.5, 78, -47.5], "size": [3, 3, 3], "uv": accent(AMBER)},
        )],
        {"origin": [-6, 77, -66], "size": [5, 4, 5], "uv": accent(CHROME)},  # roof spotlight
        # Mirrors on arms
        {"origin": [W, 60, -76], "size": [6, 2, 2], "uv": steel},
        {"origin": [W + 5, 50, -77], "size": [3, 12, 5], "uv": steel},
        {"origin": [-W - 6, 60, -76], "size": [6, 2, 2], "uv": steel},
        {"origin": [-W - 8, 50, -77], "size": [3, 12, 5], "uv": steel},
        # ---- Cab interior: dashboard, seats, wheel kept below eye line ----
        {"origin": [-28, 34, -80], "size": [56, 14, 6], "uv": steel},
        {"origin": [6, 34, -62], "size": [14, 8, 12], "uv": steel},          # driver (left)
        {"origin": [6, 42, -51], "size": [14, 22, 3], "uv": steel},
        {"origin": [-20, 34, -62], "size": [14, 8, 12], "uv": steel},        # passenger
        {"origin": [-20, 42, -51], "size": [14, 22, 3], "uv": steel},
        rod((13, 42, -76), (13, 47, -70), 3, 3, steel),
        {"origin": [9, 43, -71], "size": [8, 8, 1], "pivot": [13, 47, -70.5], "rotation": [-55, 0, 0], "uv": [256, 128]},
        # ---- Behind the cab: mesh headache rack, exhaust stacks with heat shields, air tanks ----
        {"origin": [-W, 34, -39], "size": [60, 30, 2], "uv": [256, 128]},
        *[c for x in (-35, 31) for c in (
            {"origin": [x, 22, -40], "size": [4, 54, 4], "uv": [256, 128]},
            {"origin": [x - 0.5, 42, -40.5], "size": [5, 18, 5], "uv": steel},
            rod((x + 2, 76, -38), (x + 2, 79, -35), 4, 4, accent(RUST)),
        )],
        # Jerry cans and extinguisher on the rack; fuel tank, battery box and toolbox under the deck
        *[{"origin": [x, 34, -37], "size": [6, 10, 4], "uv": accent(SAND)} for x in (-22, -15, -8)],
        {"origin": [20, 34, -37], "size": [3, 9, 3], "uv": accent(RED)},
        {"origin": [17, 14, -22], "size": [10, 11, 30], "uv": accent(CHROME)},
        *[{"origin": [16.5, 13.5, z], "size": [11, 12, 2], "uv": accent(BLACK)} for z in (-16, 0)],
        {"origin": [-27, 15, -22], "size": [10, 10, 14], "uv": accent(OLIVE)},
        {"origin": [-27, 15, -4], "size": [10, 10, 12], "uv": accent(BLACK)},
        *[{"origin": [x, 18, -28], "size": [1, 3, 54], "uv": accent(YELLOW)} for x in (-31, 30)],  # side under-run guards
        # ---- Flatbed (top y34): stake pockets, stowed loading ramps, rear fenders ----
        {"origin": [-W, 28, -37], "size": [60, 6, 129], "uv": [384, 0]},
        {"origin": [-W - 2, 28, -37], "size": [2, 8, 129], "uv": [0, 128]},
        {"origin": [W, 28, -37], "size": [2, 8, 129], "uv": [0, 128]},
        *[{"origin": [x, 29, z], "size": [1, 5, 3], "uv": [256, 128]} for x in (-W - 3, W + 2) for z in range(-30, 90, 16)],
        {"origin": [-24, 34, 86], "size": [10, 18, 3], "uv": steel},
        {"origin": [14, 34, 86], "size": [10, 18, 3], "uv": steel},
        *[{"origin": [x0, 24, 24], "size": [12, 2, 58], "uv": MUDDY} for x0 in (-32, 20)],
        # Rear bumper, lamps, mudflaps, hitch
        {"origin": [-32, 20, 92], "size": [64, 8, 3], "uv": [0, 128]},
        *[{"origin": [x, 22, 95.1], "size": [10, 4, 1], "uv": [0, 192]} for x in (-28, 18)],
        *[{"origin": [x, 22, 95.1], "size": [4, 4, 1], "uv": [42, 192]} for x in (-17, 13)],
        *[{"origin": [x, 22, 95.1], "size": [3, 4, 1], "uv": accent(WHITE)} for x in (-12, 9)],  # reversing lamps
        {"origin": [-2, 16, 94], "size": [4, 5, 4], "uv": steel},
        {"origin": [-31, 4, 82], "size": [10, 14, 1], "uv": MUDDY},
        {"origin": [21, 4, 82], "size": [10, 14, 1], "uv": MUDDY},
        # Orange tie-down straps around the deck centre (z30) over the kneeling Titan
        *[rod((26 * sx, 34, 30 + 15 * sf), (12 * sx, 51, 30 + 5 * sf), 3, 1, [128, 128]) for sx in (1, -1) for sf in (1, -1)],
        {"origin": [-23, 36, 34], "size": [46, 3, 2], "uv": [128, 128]},
        *[{"origin": [26 * sx - 2.5, 34, 12], "size": [5, 4, 3], "uv": [256, 128]} for sx in (1, -1)],
    ]

    bones = [
        {"name": "root", "pivot": [0, 0, 0]},
        {"name": "body", "parent": "root", "pivot": [0, 14, 0], "cubes": body},
    ]
    # Each front wheel gets its own steering knuckle at the wheel centre; the wheel bone inside only spins.
    for axle, z, steered in (("1", -68, True), ("2", -42, True), ("1", 40, False), ("2", 66, False)):
        for side, px, ox in (("l", 25, 20), ("r", -25, -30)):
            name = f"wheel_{'f' if steered else 'r'}{side}{axle}"
            parent = "root"
            if steered:
                parent = f"steer_f{side}{axle}"
                bones.append({"name": parent, "parent": "root", "pivot": [px, 14, z]})
            bones.append({"name": name, "parent": parent, "pivot": [px, 14, z], "cubes": make_wheel(px, 14, z, ox, 10, 14)})
    write_geo(path, "geometry.titan_hauler_truck", bones, 14.0, 7.0, 2.6)


def generate_hauler_truck_animation(path):
    anim_data = {
        "format_version": "1.8.0",
        "animations": {
            "animation.titan_hauler_truck.idle": {
                "loop": True,
                "animation_length": 0.2,
                "bones": {
                    "body": {
                        "position": {
                            "0.0": [0, 0, 0],
                            "0.1": [0, 0.12, 0],
                            "0.2": [0, 0, 0]
                        }
                    }
                }
            },
            "animation.titan_hauler_truck.drive": {
                "loop": True,
                "animation_length": 1.0,
                "bones": {
                    "body": {
                        "position": {
                            "0.0": [0, 0, 0],
                            "0.25": [0, 0.2, 0],
                            "0.5": [0, 0, 0],
                            "0.75": [0, 0.2, 0],
                            "1.0": [0, 0, 0]
                        }
                    }
                }
            }
        }
    }
    with open(path, 'w') as f:
        json.dump(anim_data, f, indent=2)
    print(f"Saved animation: {path}")


# ==============================================================================
# 2. HEAVY SKY-CRANE VTOL DROPSHIP DRONE (MASTER SPEC)
# ==============================================================================

def generate_skycrane_texture(path):
    tex = TextureDrawer(512, 512)
    tex.fill_rect(0, 0, 512, 512, 32, 35, 38)

    # (0, 0, 128, 128): Military Olive Camo Armor Plating
    tex.draw_armor_atlas(((84, 90, 84), (64, 70, 66), (104, 110, 104), (46, 50, 48)), "SC-1")

    # (128, 0, 64, 64): Gunship Cockpit Canopy Glass
    tex.draw_glass(128, 0, 64, 64)

    # (192, 0, 64, 64): Nose Sensor FLIR Optic (Glowing Cyan Lens)
    tex.fill_rect(192, 0, 64, 64, 25, 27, 30)
    tex.fill_rect(204, 16, 24, 24, 0, 220, 255) # Glowing sensor eye

    # (256, 0, 128, 64): Structural Carbon-Steel Booms & Gantry
    tex.draw_panel(256, 0, 128, 64, (40, 42, 46), rivet=False)

    # (384, 0, 128, 64): Ducted Fan Shroud Interior & Stator Vanes
    tex.fill_rect(384, 0, 128, 64, 22, 24, 26)

    # (0, 128, 128, 64): Safety Hazard Warning Stripes
    tex.draw_hazard_stripes(0, 128, 128, 64)

    # (128, 128, 128, 64): Ventral Cable Winch & Cyan Glow Hardpoints
    tex.fill_rect(128, 128, 128, 64, 0, 190, 255)
    for y in range(128, 192, 4):
        tex.fill_rect(128, y, 128, 2, 200, 245, 255)

    # (256, 128, 128, 64): Heavy Steel Lift Rigging & Spreader Bar
    tex.draw_panel(256, 128, 128, 64, (58, 62, 68))

    # (384, 128, 128, 64): Turboshaft Engine Intakes & Heat Louvers
    tex.draw_exhaust_stack(384, 128, 128, 64)

    # (0, 192, 128, 64): Landing Skids & Oleo Struts
    tex.draw_panel(0, 192, 128, 64, (48, 50, 54), rivet=False)

    # (128, 192, 128, 64): Navigation Lights (Port Red, Starboard Green, Mast White)
    tex.fill_rect(128, 192, 64, 64, 255, 30, 30)  # Red
    tex.fill_rect(192, 192, 64, 64, 30, 255, 60)  # Green

    # (0, 256, 128, 128): Turbine Rotor Blades with Yellow Safety Tips
    tex.fill_rect(0, 256, 128, 128, 30, 32, 35)
    tex.fill_rect(0, 256, 128, 16, 240, 180, 15) # Yellow tips

    # (128, 256, 128, 128): Rotor Hubs & Bearings
    tex.draw_wheel_rim(128, 256, 128, 128)

    tex.draw_accents()
    tex.save(path)


def generate_skycrane_model(path):
    # Quad ducted-fan sky crane with an enclosed, raked-canopy cockpit a seated player fits in:
    # pod 2 blocks wide, floor y16, roof underside y52; pilot cushion top y24 at (x0, z-55).
    glass, armor, stencil, roof, steel = [128, 0], [0, 0], [64, 0], [64, 64], [256, 0]
    fuselage_cubes = [
        # Main hull with chamfered edges, tail boom, fin and stabiliser
        {"origin": [-16, 16, -44], "size": [32, 22, 84], "uv": armor},
        *[rod((14 * sx, 36, -2), (10 * sx, 41, -2), 3, 84, roof) for sx in (1, -1)],
        *[rod((14 * sx, 18, -2), (10 * sx, 13, -2), 3, 84, armor) for sx in (1, -1)],
        {"origin": [-6, 22, 40], "size": [12, 10, 32], "uv": armor},
        rod((0, 32, 62), (0, 50, 74), 2, 10, armor),
        {"origin": [-18, 26, 64], "size": [36, 2, 8], "uv": armor},
        {"origin": [-1, 50, 72], "size": [2, 2, 2], "uv": accent(WHITE)},   # tail strobe
        {"origin": [-6.4, 21.6, 56], "size": [12.8, 10.8, 4], "uv": accent(ORANGE)},  # hi-vis tail band
        *[{"origin": [x, 26.2, 64], "size": [6, 2, 8], "uv": accent(ORANGE)} for x in (-18, 12)],  # stabiliser tips
        {"origin": [-1, 41, -10], "size": [2, 2, 2], "uv": accent(RED)},    # dorsal anti-collision beacon
        {"origin": [-1, 10, 10], "size": [2, 2, 2], "uv": accent(RED)},     # belly beacon
        *[{"origin": [x, 18, -24], "size": [4, 9, 30], "uv": accent(OLIVE)} for x in (-20, 16)],  # side fuel cells
        # Twin turboshafts with dark intakes and exhausts
        *[c for x in (-15, 3) for c in (
            {"origin": [x, 38, -26], "size": [12, 9, 40], "uv": roof},
            {"origin": [x + 1, 39, -29], "size": [10, 7, 3], "uv": [384, 0]},
            {"origin": [x + 1, 40, 14], "size": [10, 6, 5], "uv": accent(RUST)},
        )],
        rod((0, 47, 0), (0, 56, 4), 1, 8, steel),                            # antenna blade
        # ---- Cockpit pod (z -96..-40) ----
        {"origin": [-16, 12, -88], "size": [32, 4, 48], "uv": armor},        # floor
        {"origin": [-12, 12, -98], "size": [24, 16, 10], "uv": armor},       # nose below the glass
        {"origin": [-12, 28, -98], "size": [24, 0.6, 6], "uv": accent(BLACK)},  # anti-glare panel
        {"origin": [5, 8, -92], "size": [5, 5, 5], "uv": accent(CHROME)},   # nose searchlight
        rod((-8, 20, -98), (-8, 20, -110), 1, 1, accent(CHROME)),          # pitot probe
        rod((0, 12, -98), (0, 6, -94), 20, 4, armor),                        # chin fairing
        {"origin": [-16, 16, -88], "size": [2, 12, 48], "uv": stencil},      # lower side walls with tail number
        {"origin": [14, 16, -88], "size": [2, 12, 48], "uv": stencil},
        rod((0, 28, -92), (0, 52, -84), 28, 1, glass),                       # raked windscreen
        rod((-14.5, 28, -92.5), (-14.5, 52, -84.5), 2, 3, armor),
        rod((14.5, 28, -92.5), (14.5, 52, -84.5), 2, 3, armor),
        {"origin": [-16, 28, -84], "size": [1, 24, 40], "uv": glass},        # side glass
        {"origin": [15, 28, -84], "size": [1, 24, 40], "uv": glass},
        {"origin": [-16, 28, -62], "size": [2, 24, 2], "uv": armor},         # canopy frame ribs
        {"origin": [14, 28, -62], "size": [2, 24, 2], "uv": armor},
        {"origin": [-17, 52, -86], "size": [34, 3, 46], "uv": roof},         # roof
        *[rod((15 * sx, 52, -63), (11 * sx, 56, -63), 2, 46, roof) for sx in (1, -1)],
        {"origin": [-16, 38, -44], "size": [32, 14, 8], "uv": armor},        # pod-to-spine fairing
        {"origin": [-14, 16, -82], "size": [28, 12, 5], "uv": steel},        # instrument console
        {"origin": [-6, 16, -60], "size": [12, 8, 10], "uv": steel},         # pilot seat
        {"origin": [-6, 24, -51], "size": [12, 22, 3], "uv": steel},
        {"origin": [-1, 16, -70], "size": [2, 10, 2], "uv": steel},          # cyclic stick
        # Chin EO/IR turret with cyan optic
        {"origin": [-5, 2, -96], "size": [10, 6, 8], "uv": steel},
        {"origin": [-3, 3, -96.6], "size": [6, 4, 1], "uv": [208, 20]},
        # ---- Tapered outrigger arms, motor pods and ducts ----
        *[c for sx in (1, -1) for c in (
            rod((16 * sx, 26, 0), (46 * sx, 30, 0), 8, 14, steel),
            rod((44 * sx, 26, -4), (52 * sx, 26, -30), 6, 6, steel),
            rod((44 * sx, 26, 4), (52 * sx, 26, 30), 6, 6, steel),
            {"origin": [(64 if sx > 0 else -66), 24, -2], "size": [2, 4, 4], "uv": [128 if sx > 0 else 192, 192]},
            {"origin": [(40 if sx > 0 else -46), 25.6, -7.4], "size": [6, 8.8, 14.8], "uv": accent(YELLOW)},  # arm hazard collar
        )],
        *[{"origin": [cx - 4, 14, cz - 4], "size": [8, 8, 8], "uv": roof} for cx, cz in ((52, -34), (-52, -34), (52, 34), (-52, 34))],
        *[c for cx, cz in ((52, -34), (-52, -34), (52, 34), (-52, 34)) for c in make_ducted_fan_cowling(cx, cz)],
        # ---- Landing skids with upturned toes ----
        *[c for x in (18, -21) for c in (
            {"origin": [x, 0, -44], "size": [3, 3, 82], "uv": MUDDY},
            rod((x + 1.5, 1.5, -44), (x + 1.5, 7, -50), 3, 3, MUDDY),
            *[{"origin": [x, 3, z], "size": [3, 13, 3], "uv": [0, 192]} for z in (-34, 25)],
        )],
        # ---- Ventral sling rig (Titan shoulders hang at the y-48 clamp pads) ----
        {"origin": [-16, 14, -22], "size": [32, 2, 44], "uv": [256, 128]},
        {"origin": [-10, 12, -12], "size": [20, 2, 6], "uv": accent(YELLOW)},
        {"origin": [-10, 12, 6], "size": [20, 2, 6], "uv": accent(YELLOW)},
        *[rod((32.5 * sx, -39, 32.5 * sz), (10 * sx, 12, 9 * sz), 1.5, 1.5, [128, 128]) for sx in (1, -1) for sz in (1, -1)],
        {"origin": [-34, -42, -34], "size": [68, 3, 3], "uv": [256, 128]},
        {"origin": [-34, -42, 31], "size": [68, 3, 3], "uv": [256, 128]},
        {"origin": [-34, -42, -31], "size": [3, 3, 62], "uv": [256, 128]},
        {"origin": [31, -42, -31], "size": [3, 3, 62], "uv": [256, 128]},
        {"origin": [29, -48, 7], "size": [3, 6, 6], "uv": [256, 128]},
        {"origin": [20, -49, 6], "size": [12, 2, 8], "uv": [128, 128]},
        {"origin": [-32, -48, 7], "size": [3, 6, 6], "uv": [256, 128]},
        {"origin": [-32, -49, 6], "size": [12, 2, 8], "uv": [128, 128]},
    ]

    bones = [
        {"name": "root", "pivot": [0, 0, 0]},
        {"name": "fuselage", "parent": "root", "pivot": [0, 24, 0], "cubes": fuselage_cubes},
    ]
    for name, px, pz in (("rotor_fl", 52, -34), ("rotor_fr", -52, -34), ("rotor_rl", 52, 34), ("rotor_rr", -52, 34)):
        py = 26
        bones.append({"name": name, "parent": "fuselage", "pivot": [px, py, pz], "cubes": [
            {"origin": [px - 11, py, pz - 2], "size": [22, 1, 4], "uv": [0, 280]},
            {"origin": [px - 2, py, pz - 11], "size": [4, 1, 22], "uv": [0, 280]},
            {"origin": [px - 11, py + 0.01, pz - 2], "size": [2, 1, 4], "uv": [0, 256]},
            {"origin": [px + 9, py + 0.01, pz - 2], "size": [2, 1, 4], "uv": [0, 256]},
            {"origin": [px - 2, py + 0.01, pz - 11], "size": [4, 1, 2], "uv": [0, 256]},
            {"origin": [px - 2, py + 0.01, pz + 9], "size": [4, 1, 2], "uv": [0, 256]},
            {"origin": [px - 3, py - 1, pz - 3], "size": [6, 3, 6], "uv": [128, 256]},
        ]})
    write_geo(path, "geometry.titan_skycrane_drone", bones, 10.0, 7.0, 0.2)


def generate_skycrane_animation(path):
    anim_data = {
        "format_version": "1.8.0",
        "animations": {
            "animation.titan_skycrane_drone.idle": {
                "loop": True,
                "animation_length": 2.0,
                "bones": {
                    "fuselage": {
                        "position": {
                            "0.0": [0, 0, 0],
                            "1.0": [0, 0.5, 0],
                            "2.0": [0, 0, 0]
                        }
                    },
                    "rotor_fl": {"rotation": {"0.0": [0, 0, 0], "2.0": [0, 1440, 0]}},
                    "rotor_fr": {"rotation": {"0.0": [0, 0, 0], "2.0": [0, -1440, 0]}},
                    "rotor_rl": {"rotation": {"0.0": [0, 0, 0], "2.0": [0, -1440, 0]}},
                    "rotor_rr": {"rotation": {"0.0": [0, 0, 0], "2.0": [0, 1440, 0]}}
                }
            },
            "animation.titan_skycrane_drone.fly": {
                "loop": True,
                "animation_length": 1.0,
                "bones": {
                    "fuselage": {
                        "position": {
                            "0.0": [0, 0, 0],
                            "0.5": [0, 0.3, 0],
                            "1.0": [0, 0, 0]
                        }
                    },
                    "rotor_fl": {"rotation": {"0.0": [0, 0, 0], "1.0": [0, 2160, 0]}},
                    "rotor_fr": {"rotation": {"0.0": [0, 0, 0], "1.0": [0, -2160, 0]}},
                    "rotor_rl": {"rotation": {"0.0": [0, 0, 0], "1.0": [0, -2160, 0]}},
                    "rotor_rr": {"rotation": {"0.0": [0, 0, 0], "1.0": [0, 2160, 0]}}
                }
            }
        }
    }
    with open(path, 'w') as f:
        json.dump(anim_data, f, indent=2)
    print(f"Saved animation: {path}")


# ==============================================================================
# 3. HEAVY AMPHIBIOUS CARGO LANDING BARGE (MASTER SPEC)
# ==============================================================================

def generate_cargo_barge_texture(path):
    tex = TextureDrawer(512, 512)
    tex.fill_rect(0, 0, 512, 512, 34, 38, 42)

    # (0, 0, 128, 128): Marine Olive-Grey Steel Plating
    tex.draw_armor_atlas(((96, 104, 110), (76, 84, 90), (116, 122, 126), (58, 64, 70)), "L-04")

    # (128, 0, 64, 64): Panoramic Wheelhouse Bridge Windows
    tex.draw_glass(128, 0, 64, 64)

    # (192, 0, 64, 64): Radar Mast & Navigation Beacons
    tex.fill_rect(192, 0, 64, 64, 40, 44, 48)
    tex.fill_rect(196, 8, 8, 8, 255, 40, 40)   # Port Red
    tex.fill_rect(240, 8, 8, 8, 40, 255, 60)   # Starboard Green

    # (256, 0, 128, 64): Hull Antifouling Keel Plating
    tex.draw_panel(256, 0, 128, 64, (112, 36, 30), rivet=False)  # red antifouling below the waterline

    # (384, 0, 128, 128): Non-Skid Marine Cargo Deck
    tex.draw_diamond_plate(384, 0, 128, 128)

    # (0, 128, 128, 64): Perimeter Hazard Coamings
    tex.draw_hazard_stripes(0, 128, 128, 64)

    # (128, 128, 128, 64): Tactical Orange Tie-Down Straps & Cleats
    tex.draw_orange_strap(128, 128, 128, 64)

    # (256, 128, 128, 64): Bow Landing Drop Ramp Plating
    tex.draw_panel(256, 128, 128, 64, (68, 76, 74))

    # (384, 128, 128, 64): Hydraulic Ramp Cylinders & Rams
    tex.draw_hydraulic_cylinder(384, 128, 128, 64)

    # (0, 192, 128, 64): Safety Life Rings (Orange Buoys)
    tex.draw_life_ring(0, 192, 64, 64)
    tex.draw_life_ring(64, 192, 64, 64)

    # (128, 192, 128, 64): Marine Diesel Exhaust Mufflers
    tex.draw_exhaust_stack(128, 192, 128, 64)

    # (256, 192, 128, 64): Slotted Waveguide Radar Scanner Face
    tex.fill_rect(256, 192, 128, 64, 240, 245, 250)
    for x in range(260, 380, 8):
        tex.fill_rect(x, 210, 4, 28, 20, 22, 25)

    # (0, 256, 128, 128): Marine Outdrives & Ducted Waterjets
    tex.fill_rect(0, 256, 128, 128, 28, 30, 34)

    # (128, 256, 128, 128): Heavy Mooring Bollards (Twin Bitts)
    tex.fill_rect(128, 256, 128, 128, 88, 94, 100)
    # Small life ring sized for the 8x8 side faces of the bulkhead buoy cubes
    tex.draw_life_ring(200, 308, 8, 8)

    tex.draw_accents()
    tex.draw_camo(128, 448, 128, 64, ((176, 180, 178), (156, 160, 160), (190, 192, 188), (138, 142, 144)))  # light-grey superstructure
    tex.save(path)


def generate_cargo_barge_model(path):
    # Landing craft, 6 x 12 blocks: raked bow ramp at -Z, open well deck (top y10) for two standing Titans,
    # walk-in wheelhouse aft. Helm cushion top y26 at (x0, z73); wheelhouse ceiling y62.
    house = [128, 448]  # light-grey superstructure over the dark-grey hull
    glass, armor, stencil, roof, steel, keel = [128, 0], [0, 0], [64, 0], [64, 64], [208, 16], [256, 0]  # (256,0) is red antifouling here
    hull = [
        # ---- Hull: red antifouling bottom with sloped bilges, black boot-top, camo topsides ----
        {"origin": [-40, 0, -88], "size": [80, 4, 180], "uv": keel},
        *[rod((40 * sx, 1, 2), (47 * sx, 13, 2), 3, 180, keel) for sx in (1, -1)],
        *[{"origin": [x, 12, -88], "size": [4, 20, 180], "uv": armor} for x in (-48, 44)],
        *[{"origin": [x, 12, -88], "size": [0.6, 2, 180], "uv": [384, 0]} for x in (-48.3, 47.7)],
        *[{"origin": [x, 22, -88], "size": [1.5, 3, 180], "uv": [0, 256]} for x in (-49.5, 48)],   # rubbing strake
        *[{"origin": [x, 32, -88], "size": [4, 2, 180], "uv": [0, 128]} for x in (-48, 44)],     # hazard gunwale
        *[{"origin": [x, 16, -80], "size": [0.5, 12, 34], "uv": stencil} for x in (-48.5, 48)],  # hull number
        *[{"origin": [x, 12, z], "size": [2, 7, 6], "uv": [0, 256]} for x in (-50, 48) for z in (-60, -20, 20, 60)],  # tyre fenders
        {"origin": [-44, 0, 88], "size": [88, 26, 4], "uv": armor},          # transom
        {"origin": [-44, 4, -84], "size": [88, 6, 132], "uv": [384, 0]},     # well deck
        *[{"origin": [x, 10, -84], "size": [2, 0.3, 132], "uv": accent(YELLOW)} for x in (-36, 34)],  # deck safety lines
        *[{"origin": [x, 20, -84], "size": [0.6, 8, 6], "uv": accent(BLACK)} for x in (-48.6, 48)],   # stowed anchors
        *[rod((40 * sx, 32, -86), (40 * sx, 34, -94), 2, 2, accent(YELLOW)) for sx in (1, -1)],      # ramp hinge guides
        # Raked bow ramp with hazard lip and hydraulic rams
        rod((0, 6, -88), (0, 44, -96), 86, 4, [256, 128]),
        {"origin": [-43, 43, -98], "size": [86, 2, 4], "uv": [0, 128]},
        *[rod((40 * sx, 30, -80), (36 * sx, 40, -92), 3, 3, [384, 128]) for sx in (1, -1)],
        # ---- Raised aft deck (top y18) with stern rail ----
        {"origin": [-44, 4, 48], "size": [88, 14, 40], "uv": armor},
        *[{"origin": [x, 18, 89], "size": [1, 9, 1], "uv": steel} for x in range(-42, 43, 12)],
        {"origin": [-44, 26, 89], "size": [88, 1, 1], "uv": steel},
        # ---- Wheelhouse (floor y18, ceiling y62), bridge windows raked forward like a real ship ----
        {"origin": [-22, 18, 54], "size": [44, 16, 2], "uv": house},
        rod((0, 34, 55), (0, 56, 52), 40, 1, glass),
        *[rod((21 * sx, 34, 55), (21 * sx, 56, 52), 2, 2, house) for sx in (1, -1)],
        {"origin": [-23, 56, 49], "size": [46, 6, 7], "uv": house},          # brow over the windows
        {"origin": [-22, 18, 56], "size": [2, 16, 30], "uv": house},         # side walls
        {"origin": [20, 18, 56], "size": [2, 16, 30], "uv": house},
        {"origin": [-22, 34, 58], "size": [1, 22, 22], "uv": glass},         # side windows
        {"origin": [21, 34, 58], "size": [1, 22, 22], "uv": glass},
        *[{"origin": [x, 34, z], "size": [2, 22, d], "uv": house} for x in (-22, 20) for z, d in ((56, 2), (80, 6))],
        {"origin": [-22, 56, 56], "size": [2, 6, 30], "uv": house},
        {"origin": [20, 56, 56], "size": [2, 6, 30], "uv": house},
        {"origin": [-22, 18, 84], "size": [14, 44, 2], "uv": house},         # back wall with a door gap
        {"origin": [8, 18, 84], "size": [14, 44, 2], "uv": house},
        {"origin": [-8, 50, 84], "size": [16, 12, 2], "uv": house},
        {"origin": [-24, 62, 48], "size": [48, 3, 40], "uv": house},          # roof with chamfered edges
        *[rod((24 * sx, 62, 68), (26 * sx, 64, 68), 2, 40, house) for sx in (1, -1)],
        {"origin": [-14, 18, 56], "size": [28, 12, 4], "uv": steel},         # helm console
        {"origin": [-4, 27, 60], "size": [8, 8, 1], "pivot": [0, 31, 60.5], "rotation": [-30, 0, 0], "uv": [256, 128]},
        {"origin": [-6, 18, 68], "size": [12, 8, 10], "uv": steel},          # helm seat
        {"origin": [-6, 26, 77], "size": [12, 18, 3], "uv": steel},
        {"origin": [-23, 22, 66], "size": [1, 8, 8], "uv": [200, 308]},      # life rings
        {"origin": [22, 22, 66], "size": [1, 8, 8], "uv": [200, 308]},
        # Roof gear: searchlight, life-raft canisters, mast with yardarm and nav lamps
        {"origin": [-3, 65, 50], "size": [6, 5, 4], "uv": accent(CHROME)},
        *[c for x in (-20, 14) for c in (                                    # life-raft canisters
            {"origin": [x, 65, 74], "size": [6, 6, 10], "uv": accent(WHITE)},
            {"origin": [x - 0.2, 64.8, 78], "size": [6.4, 6.4, 2], "uv": accent(ORANGE)},
        )],
        {"origin": [1.5, 80, 67], "size": [0.4, 5, 8], "uv": accent(RED)},  # pennant on the yardarm
        {"origin": [-1.5, 65, 66], "size": [3, 22, 3], "uv": accent(LIGHT_GREY)},
        {"origin": [-12, 80, 66.5], "size": [24, 1.5, 2], "uv": accent(LIGHT_GREY)},
        {"origin": [11, 78, 66.5], "size": [2, 2, 2], "uv": [196, 8]},       # port (left) red
        {"origin": [-13, 78, 66.5], "size": [2, 2, 2], "uv": [240, 8]},      # starboard (right) green
        # Exhaust stacks with caps
        *[c for x in (-36, 30) for c in (
            {"origin": [x, 18, 74], "size": [6, 26, 6], "uv": [128, 192]},
            {"origin": [x - 1, 44, 73], "size": [8, 2, 8], "uv": accent(BLACK)},
            {"origin": [x - 0.2, 38, 73.8], "size": [6.4, 3, 6.4], "uv": accent(RED)},  # funnel band
        )],
        # Bollards and waterjets
        *[{"origin": [x, y, z], "size": [6, 6, 6], "uv": accent(BLACK)} for x, y, z in ((34, 10, -80), (-40, 10, -80), (34, 18, 80), (-40, 18, 80))],
        {"origin": [-36, 2, 92], "size": [12, 9, 6], "uv": [0, 256]},
        {"origin": [24, 2, 92], "size": [12, 9, 6], "uv": [0, 256]},
        # Tie-down straps for bay A (z-50) and bay B (z6)
        *[rod((40 * sx, 10, bz + 14 * sf), (16 * sx, 26, bz + 4 * sf), 3, 1, [128, 128])
          for bz in (-50, 6) for sx in (1, -1) for sf in (1, -1)],
        *[{"origin": [40 * sx - 2.5, 10, bz - 16], "size": [5, 4, 3], "uv": [128, 192]} for bz in (-50, 6) for sx in (1, -1)],
    ]
    bones = [
        {"name": "root", "pivot": [0, 0, 0]},
        {"name": "hull", "parent": "root", "pivot": [0, 10, 0], "cubes": hull},
        {"name": "radar", "parent": "hull", "pivot": [0, 88, 67.5],
         "cubes": [{"origin": [-12, 87, 66], "size": [24, 2, 3], "uv": [256, 192]}]},
    ]
    write_geo(path, "geometry.titan_cargo_barge", bones, 12.0, 6.5, 2.0)


def generate_cargo_barge_animation(path):
    anim_data = {
        "format_version": "1.8.0",
        "animations": {
            "animation.titan_cargo_barge.idle": {
                "loop": True,
                "animation_length": 3.0,
                "bones": {
                    "hull": {
                        "position": {
                            "0.0": [0, 0, 0],
                            "1.5": [0, 0.35, 0],
                            "3.0": [0, 0, 0]
                        },
                        "rotation": {
                            "0.0": [0, 0, 0],
                            "1.5": [-0.6, 0, -0.8],
                            "3.0": [0, 0, 0]
                        }
                    },
                    "radar": {"rotation": {"0.0": [0, 0, 0], "3.0": [0, 360, 0]}}
                }
            },
            "animation.titan_cargo_barge.sail": {
                "loop": True,
                "animation_length": 1.5,
                "bones": {
                    "hull": {
                        "position": {
                            "0.0": [0, 0, 0],
                            "0.75": [0, 0.5, 0],
                            "1.5": [0, 0, 0]
                        },
                        "rotation": {
                            "0.0": [-1.5, 0, 0],
                            "0.75": [1.0, 0, 1.2],
                            "1.5": [-1.5, 0, 0]
                        }
                    },
                    "radar": {"rotation": {"0.0": [0, 0, 0], "1.5": [0, 360, 0]}}
                }
            }
        }
    }
    with open(path, 'w') as f:
        json.dump(anim_data, f, indent=2)
    print(f"Saved animation: {path}")


def main():
    base_res = "Titan Combat/src/main/resources/assets/titancombat"

    # Paths
    truck_geo = f"{base_res}/geo/hauler_truck.geo.json"
    truck_anim = f"{base_res}/animations/hauler_truck.animation.json"
    truck_tex = f"{base_res}/textures/entity/transport/hauler_truck.png"

    drone_geo = f"{base_res}/geo/skycrane_drone.geo.json"
    drone_anim = f"{base_res}/animations/skycrane_drone.animation.json"
    drone_tex = f"{base_res}/textures/entity/transport/skycrane_drone.png"

    barge_geo = f"{base_res}/geo/cargo_barge.geo.json"
    barge_anim = f"{base_res}/animations/cargo_barge.animation.json"
    barge_tex = f"{base_res}/textures/entity/transport/cargo_barge.png"

    _rod_selfcheck()
    print(">>> Generating Hauler Truck Assets...")
    generate_hauler_truck_model(truck_geo)
    generate_hauler_truck_animation(truck_anim)
    generate_hauler_truck_texture(truck_tex)

    print(">>> Generating Sky-Crane Drone Assets...")
    generate_skycrane_model(drone_geo)
    generate_skycrane_animation(drone_anim)
    generate_skycrane_texture(drone_tex)

    print(">>> Generating Cargo Barge Assets...")
    generate_cargo_barge_model(barge_geo)
    generate_cargo_barge_animation(barge_anim)
    generate_cargo_barge_texture(barge_tex)

    # Sync to subfolders (geo/transport and animations/transport)
    for name in ["hauler_truck", "skycrane_drone", "cargo_barge"]:
        os.makedirs(f"{base_res}/geo/transport", exist_ok=True)
        shutil.copy(f"{base_res}/geo/{name}.geo.json", f"{base_res}/geo/transport/{name}.geo.json")
        os.makedirs(f"{base_res}/animations/transport", exist_ok=True)
        shutil.copy(f"{base_res}/animations/{name}.animation.json", f"{base_res}/animations/transport/{name}.animation.json")

    print(">>> All assets generated and synchronized successfully!")

if __name__ == "__main__":
    main()
