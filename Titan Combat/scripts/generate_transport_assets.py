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
        self.fill_rect(x0, y0, w, h, br, bg, bb)
        for x in range(x0, x0 + w):
            self.set_pixel(x, y0, min(255, br + 25), min(255, bg + 25), min(255, bb + 25))
            self.set_pixel(x, y0 + h - 1, max(0, br - 30), max(0, bg - 30), max(0, bb - 30))
        for y in range(y0, y0 + h):
            self.set_pixel(x0, y, min(255, br + 20), min(255, bg + 20), min(255, bb + 20))
            self.set_pixel(x0 + w - 1, y, max(0, br - 30), max(0, bg - 30), max(0, bb - 30))
        if rivet and w > 12 and h > 12:
            rivet_col = (max(0, br - 38), max(0, bg - 38), max(0, bb - 38))
            self.set_pixel(x0 + 3, y0 + 3, *rivet_col)
            self.set_pixel(x0 + w - 4, y0 + 3, *rivet_col)
            self.set_pixel(x0 + 3, y0 + h - 4, *rivet_col)
            self.set_pixel(x0 + w - 4, y0 + h - 4, *rivet_col)

    def draw_hazard_stripes(self, x0, y0, w, h, stripe_w=8):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                diag = (x - x0 + y - y0) // stripe_w
                if diag % 2 == 0:
                    self.set_pixel(x, y, 245, 185, 15) # Safety Yellow
                else:
                    self.set_pixel(x, y, 28, 28, 32) # Dark Charcoal Black

    def draw_orange_strap(self, x0, y0, w, h):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                if x == x0 or x == x0 + w - 1 or y == y0 or y == y0 + h - 1:
                    self.set_pixel(x, y, 210, 75, 0)
                elif (x - x0) % 3 == 0 or (y - y0) % 3 == 0:
                    self.set_pixel(x, y, 255, 150, 35) # Weave highlight
                else:
                    self.set_pixel(x, y, 255, 110, 0) # High-vis orange

    def draw_glass(self, x0, y0, w, h):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                self.set_pixel(x, y, 36, 52, 70)
        # Specular reflection streaks across glass
        for i in range(min(w, h)):
            if 0 <= x0 + i < self.w and 0 <= y0 + i < self.h:
                self.set_pixel(x0 + i, y0 + i, 135, 180, 215)
                if i + 1 < min(w, h):
                    self.set_pixel(x0 + i + 1, y0 + i, 105, 150, 185)
        # Gasket border
        for x in range(x0, x0 + w):
            self.set_pixel(x, y0, 18, 20, 22)
            self.set_pixel(x, y0 + h - 1, 18, 20, 22)
        for y in range(y0, y0 + h):
            self.set_pixel(x0, y, 18, 20, 22)
            self.set_pixel(x0 + w - 1, y, 18, 20, 22)

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


# ==============================================================================
# 1. 8x8 HEAVY TRANSPORTER HAULER TRUCK (MASTER SPEC)
# ==============================================================================

def generate_hauler_truck_texture(path):
    tex = TextureDrawer(512, 512)
    tex.fill_rect(0, 0, 512, 512, 35, 38, 42)

    # (0, 0, 128, 128): Olive drab military armor plating
    tex.draw_panel(0, 0, 128, 128, (72, 85, 58))

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

    tex.save(path)


def generate_hauler_truck_model(path):
    # Length 156 units (~9.75 blocks), Width 60 units (~3.75 blocks), Height 58 units (~3.6 blocks)
    # Coordinate system: Front = -Z, Rear = +Z, Right = -X, Left = +X, Up = +Y
    chassis_cubes = [
        # Twin chassis I-beam frame rails
        {"origin": [-15, 10, -76], "size": [4, 8, 152], "uv": [256, 0]},
        {"origin": [11, 10, -76], "size": [4, 8, 152], "uv": [256, 0]},
        # Crossmembers
        {"origin": [-11, 12, -68], "size": [22, 4, 4], "uv": [256, 0]},
        {"origin": [-11, 12, -24], "size": [22, 4, 4], "uv": [256, 0]},
        {"origin": [-11, 12, 24], "size": [22, 4, 4], "uv": [256, 0]},
        {"origin": [-11, 12, 68], "size": [22, 4, 4], "uv": [256, 0]},

        # ----------------------------------------------------------------------
        # FRONT PUSH BUMPER & HEAVY RECOVERY WINCH ASSEMBLY (Z = -84 to -72)
        # ----------------------------------------------------------------------
        # Heavy Front Push Bumper with Hazard Chevrons
        {"origin": [-30, 4, -80], "size": [60, 12, 8], "uv": [0, 128]},
        {"origin": [-28, 16, -78], "size": [56, 3, 3], "uv": [256, 0]}, # Bumper top step plate
        # Recovery Winch Housing Box
        {"origin": [-10, 8, -84], "size": [20, 8, 6], "uv": [384, 128]},
        # Winch Cable Drum Spool
        {"origin": [-7, 9, -83.5], "size": [14, 6, 5], "uv": [384, 128]},
        # Roller Fairlead Frame & Guide Rollers
        {"origin": [-8, 9, -84.8], "size": [16, 6, 1], "uv": [256, 0]},
        # Forged Recovery Hook
        {"origin": [-1.5, 9, -86.5], "size": [3, 5, 2], "uv": [256, 128]},
        # Left & Right Tow Clevis Shackles
        {"origin": [-22, 5, -82], "size": [4, 6, 2], "uv": [256, 128]},
        {"origin": [18, 5, -82], "size": [4, 6, 2], "uv": [256, 128]},

        # ----------------------------------------------------------------------
        # FRONT CAB ASSEMBLY (Oshkosh HEMTT Military Cab: Z = -74 to -26)
        # ----------------------------------------------------------------------
        # Lower Engine Compartment / Cab Base
        {"origin": [-28, 16, -74], "size": [56, 18, 48], "uv": [0, 0]},
        # Slatted Radiator Grille & Dual Headlight Fascia
        {"origin": [-22, 18, -75.1], "size": [44, 15, 1], "uv": [192, 0]},
        # Upper Crew Cab Compartment
        {"origin": [-27, 34, -70], "size": [54, 22, 44], "uv": [0, 0]},
        # Two-piece Split Ballistic Windshield (facing forward North -Z)
        {"origin": [-25, 36, -71.1], "size": [23.5, 18, 1], "uv": [128, 0]},
        {"origin": [1.5, 36, -71.1], "size": [23.5, 18, 1], "uv": [128, 0]},
        # Windshield Center Armored Divider Post
        {"origin": [-1.5, 36, -71.2], "size": [3, 18, 1.2], "uv": [0, 0]},
        # Cab Roof & Visor Brow with 5 Amber Clearance Lights
        {"origin": [-28, 56, -72], "size": [56, 3, 48], "uv": [0, 0]},
        {"origin": [-26, 55, -74], "size": [52, 2, 4], "uv": [256, 0]},
        *[{"origin": [x - 1.5, 59, -72], "size": [3, 1.5, 2], "uv": [392, 196]} for x in (-16, -8, 0, 8, 16)],
        # Cab Roof High-Intensity LED Lightbar & Twin Air Horns
        {"origin": [-18, 59, -68], "size": [36, 3, 4], "uv": [384, 192]}, # LED Lightbar
        {"origin": [-24, 59, -60], "size": [3, 3, 14], "uv": [256, 128]}, # Left Air Horn
        {"origin": [21, 59, -60], "size": [3, 3, 14], "uv": [256, 128]}, # Right Air Horn
        # Side Windows (Left & Right)
        {"origin": [-27.1, 38, -64], "size": [1, 15, 32], "uv": [128, 0]},
        {"origin": [26.1, 38, -64], "size": [1, 15, 32], "uv": [128, 0]},
        # Articulated Side Rear-View Mirrors with Dual Brackets
        {"origin": [-33, 38, -66], "size": [3, 14, 5], "uv": [256, 0]},
        {"origin": [-30, 48, -65], "size": [3, 2, 2], "uv": [256, 0]},
        {"origin": [-30, 40, -65], "size": [3, 2, 2], "uv": [256, 0]},
        {"origin": [30, 38, -66], "size": [3, 14, 5], "uv": [256, 0]},
        {"origin": [27, 48, -65], "size": [3, 2, 2], "uv": [256, 0]},
        {"origin": [27, 40, -65], "size": [3, 2, 2], "uv": [256, 0]},
        # Cab Ingress Boarding Stirrups / Foot Steps
        {"origin": [-29, 12, -62], "size": [2, 3, 10], "uv": [256, 0]},
        {"origin": [27, 12, -62], "size": [2, 3, 10], "uv": [256, 0]},
        # High Air Intake Snorkel on Right Side (-X) with Cyclone Dust Cleaner
        {"origin": [-29.5, 26, -34], "size": [3, 30, 3], "uv": [256, 0]},
        {"origin": [-30.5, 54, -35], "size": [5, 6, 5], "uv": [256, 128]},
        # Front Wheel Fenders with Hazard Chevrons
        {"origin": [-31, 14, -72], "size": [4, 6, 48], "uv": [0, 128]},
        {"origin": [27, 14, -72], "size": [4, 6, 48], "uv": [0, 128]},

        # ----------------------------------------------------------------------
        # EQUIPMENT MODULE BEHIND CAB (Z = -26 to -16)
        # ----------------------------------------------------------------------
        # Heavy Steel Lattice Headache Rack (Cab Protector Screen)
        {"origin": [-28, 16, -26], "size": [56, 40, 4], "uv": [256, 0]},
        # Vertically Mounted Spare 8x8 Off-Road Tire behind Headache Rack
        {"origin": [-12, 24, -22], "size": [8, 22, 22], "uv": [0, 256]},
        {"origin": [-13, 31, -15], "size": [10, 8, 8], "uv": [128, 256]}, # Spare Wheel Hub
        # Dual Tall Vertical Exhaust Smokestacks with Heat Shields & Angled Rain Flappers
        {"origin": [-25, 20, -22], "size": [4, 44, 4], "uv": [256, 128]},
        {"origin": [21, 20, -22], "size": [4, 44, 4], "uv": [256, 128]},
        {"origin": [-25, 64, -22], "size": [4, 4, 6], "uv": [256, 128]}, # Left Angled Tip
        {"origin": [21, 64, -22], "size": [4, 4, 6], "uv": [256, 128]}, # Right Angled Tip
        # Dual Cylindrical Air Brake Tanks with Brass End Fittings
        {"origin": [15, 18, -20], "size": [8, 8, 18], "uv": [256, 192]},
        # Side-Mounted Heavy Toolboxes / Battery Storage
        {"origin": [-29, 11, -16], "size": [6, 8, 20], "uv": [256, 192]},
        {"origin": [23, 11, -16], "size": [6, 8, 20], "uv": [256, 192]},

        # ----------------------------------------------------------------------
        # LOWBED CARGO FLATBED DECK (Z = -22 to +88)
        # ----------------------------------------------------------------------
        # Diamond-Plate Flatbed Cargo Deck
        {"origin": [-28, 16, -22], "size": [56, 4, 110], "uv": [384, 0]},
        # Deck Side Coamings / Rub Rails with Yellow-Black Hazard Chevrons
        {"origin": [-30, 16, -22], "size": [2, 6, 110], "uv": [0, 128]},
        {"origin": [28, 16, -22], "size": [2, 6, 110], "uv": [0, 128]},
        # Rear Bumper with Hazard Chevrons, Mudflaps & Commercial Tail Light Clusters
        {"origin": [-30, 14, 88], "size": [60, 8, 2], "uv": [0, 128]},
        {"origin": [-26, 15, 90.1], "size": [14, 5, 1], "uv": [0, 192]}, # Left Tail Light
        {"origin": [12, 15, 90.1], "size": [14, 5, 1], "uv": [0, 192]}, # Right Tail Light
        {"origin": [-2, 13, 89], "size": [4, 5, 4], "uv": [256, 0]}, # Heavy Pintle Hitch
        {"origin": [-28, 6, 88.5], "size": [10, 8, 1], "uv": [0, 256]}, # Left Mudflap
        {"origin": [18, 6, 88.5], "size": [10, 8, 1], "uv": [0, 256]}, # Right Mudflap

        # ----------------------------------------------------------------------
        # HIGH-VIS ORANGE RATCHET TIE-DOWN STRAPS (Centering at Z = +33)
        # ----------------------------------------------------------------------
        # Front Diagonal Straps (Deck anchor Z=+18 up over the knees, Z=+28)
        rod((-24.5, 20, 18), (-12, 38, 28), 3, 1, [128, 128]),
        rod((24.5, 20, 18), (12, 38, 28), 3, 1, [128, 128]),
        # Rear Diagonal Straps (Rear deck anchor Z=+48 up over the hips, Z=+38)
        rod((-24.5, 20, 48), (-12, 36, 38), 3, 1, [128, 128]),
        rod((24.5, 20, 48), (12, 36, 38), 3, 1, [128, 128]),
        # Cross Knee Restraint Strap (Horizontal heavy tensioner strap over legs)
        {"origin": [-23, 22, 28], "size": [46, 3, 2], "uv": [128, 128]},
        # Heavy Cast Steel Ratchet Tensioner Buckles
        {"origin": [-28, 22, 20], "size": [5, 4, 3], "uv": [256, 128]},
        {"origin": [23, 22, 20], "size": [5, 4, 3], "uv": [256, 128]},

        # ----------------------------------------------------------------------
        # SUSPENSION DIFFERENTIALS & LEAF SPRING PACKS
        # ----------------------------------------------------------------------
        {"origin": [-5, 9, -58], "size": [10, 8, 8], "uv": [128, 192]}, # Axle 1 Diff
        {"origin": [-5, 9, -32], "size": [10, 8, 8], "uv": [128, 192]}, # Axle 2 Diff
        {"origin": [-5, 9, 30], "size": [10, 8, 8], "uv": [128, 192]},  # Axle 3 Diff
        {"origin": [-5, 9, 58], "size": [10, 8, 8], "uv": [128, 192]}   # Axle 4 Diff
    ]

    # Wheel definitions (8 massive off-road tires, diameter 24, width 10)
    # Front steering axles: Z = -56, Z = -30
    # Rear heavy drive axles: Z = +32, Z = +60
    wheel_defs = [
        ("wheel_fl1",  25, 12, -56,  20, 0, -68, 10, 24, 24),
        ("wheel_fr1", -25, 12, -56, -30, 0, -68, 10, 24, 24),
        ("wheel_fl2",  25, 12, -30,  20, 0, -42, 10, 24, 24),
        ("wheel_fr2", -25, 12, -30, -30, 0, -42, 10, 24, 24),
        ("wheel_rl1",  25, 12,  32,  20, 0,  20, 10, 24, 24),
        ("wheel_rr1", -25, 12,  32, -30, 0,  20, 10, 24, 24),
        ("wheel_rl2",  25, 12,  60,  20, 0,  48, 10, 24, 24),
        ("wheel_rr2", -25, 12,  60, -30, 0,  48, 10, 24, 24)
    ]

    bones = [
        {"name": "root", "pivot": [0, 0, 0]},
        {"name": "chassis", "parent": "root", "pivot": [0, 16, 0], "cubes": chassis_cubes}
    ]

    for name, px, py, pz, ox, oy, oz, sx, sy, sz in wheel_defs:
        bones.append({
            "name": name,
            "parent": "chassis",
            "pivot": [px, py, pz],
            "cubes": [
                {"origin": [ox, oy, oz], "size": [sx, sy, sz], "uv": [0, 256]}
            ]
        })

    model_data = {
        "format_version": "1.12.0",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": "geometry.titan_hauler_truck",
                    "texture_width": 512,
                    "texture_height": 512,
                    "visible_bounds_width": 8.5,
                    "visible_bounds_height": 4.8,
                    "visible_bounds_offset": [0, 1.8, 0]
                },
                "bones": per_face_uv(bones)
            }
        ]
    }
    with open(path, 'w') as f:
        json.dump(model_data, f, indent=2)
    print(f"Saved model: {path}")


def generate_hauler_truck_animation(path):
    anim_data = {
        "format_version": "1.8.0",
        "animations": {
            "animation.titan_hauler_truck.idle": {
                "loop": True,
                "animation_length": 2.0,
                "bones": {
                    "chassis": {
                        "position": {
                            "0.0": [0, 0, 0],
                            "1.0": [0, 0.25, 0],
                            "2.0": [0, 0, 0]
                        }
                    }
                }
            },
            "animation.titan_hauler_truck.drive": {
                "loop": True,
                "animation_length": 1.0,
                "bones": {
                    "chassis": {
                        "position": {
                            "0.0": [0, 0, 0],
                            "0.25": [0, 0.4, 0],
                            "0.5": [0, 0, 0],
                            "0.75": [0, 0.4, 0],
                            "1.0": [0, 0, 0]
                        }
                    },
                    "wheel_fl1": {"rotation": {"0.0": [0, 0, 0], "1.0": [-360, 0, 0]}},
                    "wheel_fr1": {"rotation": {"0.0": [0, 0, 0], "1.0": [-360, 0, 0]}},
                    "wheel_fl2": {"rotation": {"0.0": [0, 0, 0], "1.0": [-360, 0, 0]}},
                    "wheel_fr2": {"rotation": {"0.0": [0, 0, 0], "1.0": [-360, 0, 0]}},
                    "wheel_rl1": {"rotation": {"0.0": [0, 0, 0], "1.0": [-360, 0, 0]}},
                    "wheel_rr1": {"rotation": {"0.0": [0, 0, 0], "1.0": [-360, 0, 0]}},
                    "wheel_rl2": {"rotation": {"0.0": [0, 0, 0], "1.0": [-360, 0, 0]}},
                    "wheel_rr2": {"rotation": {"0.0": [0, 0, 0], "1.0": [-360, 0, 0]}}
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
    tex.draw_panel(0, 0, 128, 128, (66, 78, 54))

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

    tex.save(path)


def generate_skycrane_model(path):
    # Wingspan 120 units (~7.5 blocks), Length 100 units (~6.2 blocks), Height 44 units (~2.75 blocks)
    # Coordinate system: Front = -Z, Rear = +Z, Right = -X, Left = +X, Up = +Y
    fuselage_cubes = [
        # Main center armored hull (Z = -42 to +42)
        {"origin": [-18, 16, -42], "size": [36, 20, 84], "uv": [0, 0]},
        # Dorsal Engine Deck: Dual Turboshaft Engine Nacelles
        {"origin": [-16, 36, -30], "size": [14, 8, 48], "uv": [384, 128]}, # Right Engine
        {"origin": [2, 36, -30], "size": [14, 8, 48], "uv": [384, 128]},   # Left Engine
        # Dorsal Air Intake Scoops (facing North -Z)
        {"origin": [-15, 37, -34], "size": [12, 6, 4], "uv": [256, 0]},
        {"origin": [3, 37, -34], "size": [12, 6, 4], "uv": [256, 0]},
        # Rear Engine Exhaust Heat Nozzles
        {"origin": [-15, 37, 18], "size": [12, 6, 4], "uv": [256, 0]},
        {"origin": [3, 37, 18], "size": [12, 6, 4], "uv": [256, 0]},
        # Avionics Dorsal Spine & Antenna Blades
        {"origin": [-2, 36, -10], "size": [4, 10, 20], "uv": [256, 0]},
        {"origin": [-0.5, 46, -4], "size": [1, 8, 8], "uv": [256, 128]},

        # ----------------------------------------------------------------------
        # FORWARD COCKPIT NOSE & SENSOR TURRET (Z = -64 to -42)
        # ----------------------------------------------------------------------
        # Forward Chiseled Nose
        {"origin": [-16, 18, -64], "size": [32, 16, 22], "uv": [0, 0]},
        # Multifacet Gunship Canopy Glass (facing North -Z)
        {"origin": [-14, 22, -62.1], "size": [28, 11, 16], "uv": [128, 0]},
        # Canopy Center Armored Frame Rib
        {"origin": [-1, 22, -62.2], "size": [2, 11, 16.2], "uv": [0, 0]},
        # Raked upper canopy facet & side cheek windows
        rod((0, 33, -63), (0, 38, -46), 26, 1, [128, 0]),
        {"origin": [-16.1, 24, -60], "size": [1, 8, 14], "uv": [128, 0]},
        {"origin": [15.1, 24, -60], "size": [1, 8, 14], "uv": [128, 0]},
        # Chin EO/IR FLIR Sensor Turret Ball with Glowing Cyan Optic
        {"origin": [-6, 12, -70], "size": [12, 10, 10], "uv": [256, 0]},
        {"origin": [-3, 14, -71], "size": [6, 5, 1], "uv": [208, 20]},

        # ----------------------------------------------------------------------
        # OUTRIGGER WING STRUCTURES & DIAGONAL BRACING
        # ----------------------------------------------------------------------
        # Port wing outrigger boom (+X) with fore/aft pylons into the fan shrouds
        {"origin": [18, 22, -10], "size": [46, 10, 20], "uv": [256, 0]},
        {"origin": [46, 22, -20], "size": [8, 6, 10], "uv": [256, 0]},
        {"origin": [46, 22, 10], "size": [8, 6, 10], "uv": [256, 0]},
        # Diagonal Pylon Truss Bracing
        rod((18, 17, 0), (44, 22, 0), 4, 8, [256, 0]),

        # Starboard wing outrigger boom (-X)
        {"origin": [-64, 22, -10], "size": [46, 10, 20], "uv": [256, 0]},
        {"origin": [-54, 22, -20], "size": [8, 6, 10], "uv": [256, 0]},
        {"origin": [-54, 22, 10], "size": [8, 6, 10], "uv": [256, 0]},
        # Diagonal Pylon Truss Bracing
        rod((-18, 17, 0), (-44, 22, 0), 4, 8, [256, 0]),

        # Wingtip Navigation Lights (Port Red: +X, Starboard Green: -X)
        {"origin": [64, 24, -2], "size": [2, 4, 4], "uv": [128, 192]}, # Port
        {"origin": [-66, 24, -2], "size": [2, 4, 4], "uv": [192, 192]}, # Starboard

        # ----------------------------------------------------------------------
        # 4 OPEN DUCTED FAN COWLINGS (28 wide, 12 tall) with 4-point stator cross & motor hub
        # ----------------------------------------------------------------------
        *[c for cx, cz in ((52, -34), (-52, -34), (52, 34), (-52, 34)) for c in (
            {"origin": [cx - 14, 20, cz - 14], "size": [28, 12, 2], "uv": [0, 128]},
            {"origin": [cx - 14, 20, cz + 12], "size": [28, 12, 2], "uv": [0, 128]},
            {"origin": [cx - 14, 20, cz - 12], "size": [2, 12, 24], "uv": [0, 128]},
            {"origin": [cx + 12, 20, cz - 12], "size": [2, 12, 24], "uv": [0, 128]},
            {"origin": [cx - 12, 22, cz - 1], "size": [24, 2, 2], "uv": [256, 0]},
            {"origin": [cx - 1, 22, cz - 12], "size": [2, 2, 24], "uv": [256, 0]},
            {"origin": [cx - 3, 21, cz - 3], "size": [6, 4, 6], "uv": [256, 0]},
        )],

        # ----------------------------------------------------------------------
        # QUAD LANDING GEAR SKIDS & SHOCK OLEOS
        # ----------------------------------------------------------------------
        # Left Landing Skid (+X)
        {"origin": [16, 2, -36], "size": [3, 3, 72], "uv": [0, 192]},
        {"origin": [16, 5, -28], "size": [3, 11, 3], "uv": [0, 192]}, # Forward Oleo Strut
        {"origin": [16, 5, 25], "size": [3, 11, 3], "uv": [0, 192]},  # Aft Oleo Strut
        # Right Landing Skid (-X)
        {"origin": [-19, 2, -36], "size": [3, 3, 72], "uv": [0, 192]},
        {"origin": [-19, 5, -28], "size": [3, 11, 3], "uv": [0, 192]}, # Forward Oleo Strut
        {"origin": [-19, 5, 25], "size": [3, 11, 3], "uv": [0, 192]},  # Aft Oleo Strut

        # ----------------------------------------------------------------------
        # VENTRAL SLING RIG & SUSPENSION CABLES (Hanging down to Y = -42)
        # ----------------------------------------------------------------------
        # Main ventral winch gantry frame under fuselage
        {"origin": [-16, 14, -22], "size": [32, 2, 44], "uv": [256, 128]},
        # Winch Cable Spool Drums hanging below the gantry (Y = 12..14)
        {"origin": [-10, 12, -12], "size": [20, 2, 6], "uv": [384, 128]},
        {"origin": [-10, 12, 6], "size": [20, 2, 6], "uv": [384, 128]},
        # 4 taut hoist cables from drum ends down to the spreader-bar corners at Y = -39
        *[rod((32.5 * sx, -39, 32.5 * sz), (10 * sx, 12, 9 * sz), 1.5, 1.5, [128, 128])
          for sx in (1, -1) for sz in (1, -1)],
        # Hollow spreader-bar frame (Y = -42..-39), wide enough for any Titan torso/head to pass through
        {"origin": [-34, -42, -34], "size": [68, 3, 3], "uv": [256, 128]},
        {"origin": [-34, -42, 31], "size": [68, 3, 3], "uv": [256, 128]},
        {"origin": [-34, -42, -31], "size": [3, 3, 62], "uv": [256, 128]},
        {"origin": [31, -42, -31], "size": [3, 3, 62], "uv": [256, 128]},
        # Shoulder clamp arms with glowing cyan magnetic pads (shoulder lugs sit at x +-24, z +10)
        {"origin": [29, -48, 7], "size": [3, 6, 6], "uv": [256, 128]},
        {"origin": [20, -49, 6], "size": [12, 2, 8], "uv": [128, 128]},
        {"origin": [-32, -48, 7], "size": [3, 6, 6], "uv": [256, 128]},
        {"origin": [-32, -49, 6], "size": [12, 2, 8], "uv": [128, 128]}
    ]

    # 4 Spinning Rotor Blades inside shrouds
    rotor_defs = [
        ("rotor_fl",  52, 26, -34),
        ("rotor_fr", -52, 26, -34),
        ("rotor_rl",  52, 26,  34),
        ("rotor_rr", -52, 26,  34)
    ]

    bones = [
        {"name": "root", "pivot": [0, 0, 0]},
        {"name": "fuselage", "parent": "root", "pivot": [0, 24, 0], "cubes": fuselage_cubes}
    ]

    for name, px, py, pz in rotor_defs:
        bones.append({
            "name": name,
            "parent": "fuselage",
            "pivot": [px, py, pz],
            "cubes": [
                {"origin": [px - 11, py, pz - 2], "size": [22, 1, 4], "uv": [0, 280]},
                {"origin": [px - 2, py, pz - 11], "size": [4, 1, 22], "uv": [0, 280]},
                # Yellow safety tips
                {"origin": [px - 11, py + 0.01, pz - 2], "size": [2, 1, 4], "uv": [0, 256]},
                {"origin": [px + 9, py + 0.01, pz - 2], "size": [2, 1, 4], "uv": [0, 256]},
                {"origin": [px - 2, py + 0.01, pz - 11], "size": [4, 1, 2], "uv": [0, 256]},
                {"origin": [px - 2, py + 0.01, pz + 9], "size": [4, 1, 2], "uv": [0, 256]},
                {"origin": [px - 3, py - 1, pz - 3], "size": [6, 3, 6], "uv": [128, 256]}
            ]
        })

    model_data = {
        "format_version": "1.12.0",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": "geometry.titan_skycrane_drone",
                    "texture_width": 512,
                    "texture_height": 512,
                    "visible_bounds_width": 9.0,
                    "visible_bounds_height": 7.0,
                    "visible_bounds_offset": [0, 0.2, 0]
                },
                "bones": per_face_uv(bones)
            }
        ]
    }
    with open(path, 'w') as f:
        json.dump(model_data, f, indent=2)
    print(f"Saved model: {path}")


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
                        },
                        "rotation": {
                            "0.0": [6.0, 0, 0],
                            "0.5": [5.0, 0, 0],
                            "1.0": [6.0, 0, 0]
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
    tex.draw_panel(0, 0, 128, 128, (62, 72, 65))

    # (128, 0, 64, 64): Panoramic Wheelhouse Bridge Windows
    tex.draw_glass(128, 0, 64, 64)

    # (192, 0, 64, 64): Radar Mast & Navigation Beacons
    tex.fill_rect(192, 0, 64, 64, 40, 44, 48)
    tex.fill_rect(196, 8, 8, 8, 255, 40, 40)   # Port Red
    tex.fill_rect(240, 8, 8, 8, 40, 255, 60)   # Starboard Green

    # (256, 0, 128, 64): Hull Antifouling Keel Plating
    tex.fill_rect(256, 0, 128, 64, 30, 32, 36)

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

    tex.save(path)


def generate_cargo_barge_model(path):
    # Length 164 units (~10.2 blocks), Width 100 units (~6.2 blocks), Height 48 units (~3 blocks)
    # Coordinate system: Front (Bow) = -Z, Rear (Stern) = +Z, Right = -X, Left = +X, Up = +Y
    hull_cubes = [
        # ----------------------------------------------------------------------
        # TWIN CATAMARAN SPONSONS & WAVE-PIERCING BOWS
        # ----------------------------------------------------------------------
        # Port Catamaran Pontoon (+X)
        {"origin": [28, 0, -80], "size": [20, 16, 160], "uv": [0, 0]},
        rod((38, 2.83, -77.17), (38, 18.83, -93.17), 20, 8, [0, 0]), # 45-degree bow wedge
        {"origin": [28, 0, -78], "size": [2, 3, 156], "uv": [256, 0]}, # Lower Keel Strake
        # Starboard Catamaran Pontoon (-X)
        {"origin": [-48, 0, -80], "size": [20, 16, 160], "uv": [0, 0]},
        rod((-38, 2.83, -77.17), (-38, 18.83, -93.17), 20, 8, [0, 0]), # 45-degree bow wedge
        {"origin": [-30, 0, -78], "size": [2, 3, 156], "uv": [256, 0]}, # Lower Keel Strake

        # ----------------------------------------------------------------------
        # LOW-SLUNG CENTER WELL DECK & COAMINGS (Z = -74 to +48)
        # ----------------------------------------------------------------------
        # Diamond-Plate Well Deck Floor
        {"origin": [-28, 6, -74], "size": [56, 4, 122], "uv": [384, 0]},
        # Deck Perimeter Coamings with Yellow-Black Hazard Stripes
        {"origin": [-30, 9, -74], "size": [2, 7, 122], "uv": [0, 128]},
        {"origin": [28, 9, -74], "size": [2, 7, 122], "uv": [0, 128]},
        # Heavy Marine Mooring Bollards (Twin Bitts)
        {"origin": [36, 16, -72], "size": [6, 6, 6], "uv": [128, 256]}, # Bow Port
        {"origin": [-42, 16, -72], "size": [6, 6, 6], "uv": [128, 256]}, # Bow Starboard
        {"origin": [36, 16, 68], "size": [6, 6, 6], "uv": [128, 256]},  # Stern Port
        {"origin": [-42, 16, 68], "size": [6, 6, 6], "uv": [128, 256]},  # Stern Starboard

        # ----------------------------------------------------------------------
        # ARTICULATED BOW LANDING DROP RAMP & HYDRAULIC RAMS (Z = -98 to -74)
        # ----------------------------------------------------------------------
        # Bow Landing Drop Ramp hinged at the well-deck lip, sloping down to Z = -98
        rod((0, 8, -74), (0, 2, -96), 54, 4, [256, 128]),
        rod((0, 2, -96), (0, 1.5, -98), 54, 4, [0, 128]), # Ramp Lip Hazard Stripe
        # Hydraulic lift cylinder mounts on the sponson inner walls
        {"origin": [24, 10, -80], "size": [4, 13, 4], "uv": [256, 0]},
        {"origin": [-28, 10, -80], "size": [4, 13, 4], "uv": [256, 0]},
        # Port/Starboard cylinders (dark barrel) with chrome rams down to the ramp mid-span
        *[c for x in (25.5, -25.5) for c in (
            rod((x, 22, -78), (x, 14.8, -83.4), 3, 3, [384, 128]),
            rod((x, 14.8, -83.4), (x, 6, -88), 2, 2, [384, 164]),
        )],

        # ----------------------------------------------------------------------
        # AFT WHEELHOUSE COMMAND BRIDGE & BRIDGE WINGS (Z = +48 to +78)
        # ----------------------------------------------------------------------
        # Lower Superstructure Compartment
        {"origin": [-26, 10, 48], "size": [52, 24, 30], "uv": [0, 0]},
        # Forward Panoramic Bridge Windows (Looking North -Z across cargo deck)
        # Raked outward 15 degrees (tops lean out) like a real wheelhouse
        {"origin": [-24, 22, 47.4], "size": [48, 9, 1], "pivot": [0, 22, 47.9], "rotation": [15, 0, 0], "uv": [128, 0]},
        # Side Bridge Windows (Port & Starboard)
        {"origin": [-26.6, 22, 54], "size": [1, 9, 20], "pivot": [-26.1, 22, 64], "rotation": [0, 0, -15], "uv": [128, 0]},
        {"origin": [25.6, 22, 54], "size": [1, 9, 20], "pivot": [26.1, 22, 64], "rotation": [0, 0, 15], "uv": [128, 0]},
        # Port Bridge-Wing Catwalk & Safety Railing (+X)
        {"origin": [26, 20, 52], "size": [14, 2, 16], "uv": [384, 0]},
        {"origin": [39, 22, 52], "size": [1, 8, 16], "uv": [0, 0]}, # Safety Railing
        # Starboard Bridge-Wing Catwalk & Safety Railing (-X)
        {"origin": [-40, 20, 52], "size": [14, 2, 16], "uv": [384, 0]},
        {"origin": [-40, 22, 52], "size": [1, 8, 16], "uv": [0, 0]}, # Safety Railing
        # Orange Marine Life Rings mounted on Superstructure Walls
        {"origin": [-27.1, 14, 58], "size": [1, 8, 8], "uv": [200, 308]}, # Port Wall
        {"origin": [26.1, 14, 58], "size": [1, 8, 8], "uv": [200, 308]},  # Starboard Wall
        # Bridge Roof
        {"origin": [-28, 34, 46], "size": [56, 3, 34], "uv": [0, 0]},
        # Dual Marine Diesel Exhaust Stacks with Rain Caps
        {"origin": [-20, 36, 68], "size": [4, 12, 4], "uv": [128, 192]},
        {"origin": [16, 36, 68], "size": [4, 12, 4], "uv": [128, 192]},
        # Forward Searchlight on Bridge Brow
        {"origin": [-3, 37, 46], "size": [6, 6, 4], "uv": [192, 0]},

        # ----------------------------------------------------------------------
        # LATTICE RADAR & COMMUNICATIONS MAST
        # ----------------------------------------------------------------------
        {"origin": [-2, 37, 62], "size": [4, 14, 4], "uv": [192, 0]},
        # Port & Starboard Navigation Light Arms
        {"origin": [2, 44, 63], "size": [8, 1, 1], "uv": [192, 0]},
        {"origin": [9, 44, 62.5], "size": [2, 3, 2], "uv": [192, 0]}, # Port Green Light
        {"origin": [-10, 44, 63], "size": [8, 1, 1], "uv": [192, 0]},
        {"origin": [-11, 44, 62.5], "size": [2, 3, 2], "uv": [192, 0]}, # Starboard Red Light

        # ----------------------------------------------------------------------
        # ORANGE RATCHET TIE-DOWN STRAPS (Rendered on Deck for 2 Titans)
        # ----------------------------------------------------------------------
        # Independent strap set per bay: deck anchors 14u fore/aft of the bay, up over knees/hips
        *[rod((26 * sx, 10, bz + 14 * sf), (12 * sx, 30, bz + 4 * sf), 3, 1, [128, 128])
          for bz in (-40, 20) for sx in (1, -1) for sf in (1, -1)],
        # Ratchet buckles at each bay's forward anchors
        *[{"origin": [26 * sx - 2.5, 10, bz - 16], "size": [5, 4, 3], "uv": [128, 192]}
          for bz in (-40, 20) for sx in (1, -1)],

        # ----------------------------------------------------------------------
        # DUAL TRANSOM WATERJET PROPULSION UNITS (Aft Transom: Z = +78 to +84)
        # ----------------------------------------------------------------------
        {"origin": [-44, 2, 78], "size": [12, 9, 6], "uv": [0, 256]},
        {"origin": [-42, 3, 84], "size": [8, 7, 4], "uv": [0, 256]}, # Port Nozzle
        {"origin": [32, 2, 78], "size": [12, 9, 6], "uv": [0, 256]},
        {"origin": [34, 3, 84], "size": [8, 7, 4], "uv": [0, 256]}  # Starboard Nozzle
    ]

    bones = [
        {"name": "root", "pivot": [0, 0, 0]},
        {"name": "hull", "parent": "root", "pivot": [0, 10, 0], "cubes": hull_cubes},
        {
            "name": "radar",
            "parent": "hull",
            "pivot": [0, 51, 64],
            "cubes": [
                {"origin": [-14, 50, 63], "size": [28, 2, 2], "uv": [256, 192]}
            ]
        }
    ]

    model_data = {
        "format_version": "1.12.0",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": "geometry.titan_cargo_barge",
                    "texture_width": 512,
                    "texture_height": 512,
                    "visible_bounds_width": 9.0,
                    "visible_bounds_height": 4.8,
                    "visible_bounds_offset": [0, 1.5, 0]
                },
                "bones": per_face_uv(bones)
            }
        ]
    }
    with open(path, 'w') as f:
        json.dump(model_data, f, indent=2)
    print(f"Saved model: {path}")


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
