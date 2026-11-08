#!/usr/bin/env python3
"""Tactical Technical 4x4 (Tier 1 Light Combat & Logistics Transport)
Builds the 3D geometry, textures, and renders a 5-view orthographic/isometric concept sheet.
Output: tactical_technical_5view.png
"""

import json
import math
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Titan Combat", "scripts"))
from generate_transport_assets import TextureDrawer, make_png, per_face_uv, rod, write_geo

# Color palette / Texture cells
# 512x512 texture atlas with 64x64 material cells
ARMOR_CELL = [0, 0]      # NATO Desert Tan / Coyote
FRAME_CELL = [64, 0]     # Dark Matte Chassis Steel
DECK_CELL = [128, 0]     # Diamond plate steel bed
BUMPER_CELL = [192, 0]   # Heavy black powder-coated steel
GLASS_CELL = [256, 0]    # Tinted ballistic glass
TYRE_CELL = [320, 0]     # Lug tire tread rubber
RIM_CELL = [384, 0]      # Heavy steel beadlock rim
AMBER_CELL = [448, 0]    # Indicator / Marker lights

RED_CELL = [0, 64]       # Tail lights
HEADLIGHT_CELL = [64, 64]# Bright Xenon optic
INTERIOR_CELL = [128, 64]# Cab dash & seats
CANISTER_CELL = [192, 64]# Snorkel & accessories
STRAP_CELL = [256, 64]   # Tie-down ratchet straps
EXHAUST_CELL = [320, 64] # Burnished exhaust steel

BASE_TAN = (175, 160, 130)
DARK_STEEL = (45, 48, 52)
BED_GREY = (75, 80, 85)
TIRE_BLACK = (32, 34, 36)
GLASS_TINT = (40, 55, 65, 200)

def hash_noise(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0

def paint_texture():
    t = TextureDrawer(512, 512)
    def rect(cell, col, w=64, h=64):
        for y in range(h):
            for x in range(w):
                noise = (hash_noise(x, y, 1) - 0.5) * 12
                c = tuple(max(0, min(255, int(v + noise))) for v in col[:3])
                a = col[3] if len(col) > 3 else 255
                t.set_pixel(cell[0] + x, cell[1] + y, c[0], c[1], c[2], a)

    # Base materials
    rect(ARMOR_CELL, BASE_TAN)
    # Add panel lines and rivets to ARMOR_CELL
    for i in range(64):
        t.set_pixel(ARMOR_CELL[0] + i, ARMOR_CELL[1] + 63, 110, 100, 80)
        t.set_pixel(ARMOR_CELL[0] + 63, ARMOR_CELL[1] + i, 110, 100, 80)
        if i % 8 == 4:
            t.set_pixel(ARMOR_CELL[0] + i, ARMOR_CELL[1] + 4, 80, 75, 60)
            t.set_pixel(ARMOR_CELL[0] + 4, ARMOR_CELL[1] + i, 80, 75, 60)

    rect(FRAME_CELL, DARK_STEEL)
    rect(BUMPER_CELL, (35, 38, 42))
    rect(DECK_CELL, BED_GREY)
    # Diamond plate pattern on deck
    for y in range(64):
        for x in range(64):
            if (x + y) % 6 == 0 or (x - y) % 6 == 0:
                t.set_pixel(DECK_CELL[0] + x, DECK_CELL[1] + y, 110, 115, 120)

    rect(GLASS_CELL, GLASS_TINT)
    rect(TYRE_CELL, TIRE_BLACK)
    # Heavy tire tread ribs
    for y in range(64):
        if y % 8 in (0, 1, 2):
            for x in range(64):
                t.set_pixel(TYRE_CELL[0] + x, TYRE_CELL[1] + y, 18, 20, 22)

    rect(RIM_CELL, (60, 65, 70))
    for i in range(8):
        ang = i * math.pi / 4
        cx = int(32 + 18 * math.cos(ang))
        cy = int(32 + 18 * math.sin(ang))
        t.set_pixel(RIM_CELL[0] + cx, RIM_CELL[1] + cy, 210, 215, 220)

    rect(AMBER_CELL, (255, 165, 0))
    rect(RED_CELL, (220, 25, 25))
    rect(HEADLIGHT_CELL, (240, 245, 255))
    rect(INTERIOR_CELL, (50, 52, 55))
    rect(CANISTER_CELL, (40, 42, 45))
    rect(STRAP_CELL, (240, 140, 20)) # Safety Orange ratchet straps
    rect(EXHAUST_CELL, (110, 105, 100))

    return t

def make_cube(origin, size, uv):
    return {"origin": origin, "size": size, "uv": list(uv)}

def make_wheel(bone_name, parent, cx, cy, cz, steer=False):
    bones = []
    w_bone = bone_name
    if steer:
        s_bone = bone_name.replace("wheel_", "steer_")
        bones.append({"name": s_bone, "parent": parent, "pivot": [cx, cy, cz], "cubes": []})
        parent = s_bone

    r = 11.0 # 22 px diameter wheel (~1.375 blocks)
    w = 7.0  # width
    x0 = cx - w/2 if cx > 0 else cx - w/2
    cubes = [
        # Tire main body
        make_cube([x0, cy - r, cz - r], [w, r*2, r*2], TYRE_CELL),
        # Wheel rim insert
        make_cube([x0 - (0.5 if cx > 0 else -0.5), cy - 6, cz - 6], [0.5 if cx > 0 else -0.5, 12, 12], RIM_CELL),
        # Center hub
        make_cube([x0 - (1.0 if cx > 0 else -1.0), cy - 3, cz - 3], [1.0 if cx > 0 else -1.0, 6, 6], FRAME_CELL)
    ]
    bones.append({"name": w_bone, "parent": parent, "pivot": [cx, cy, cz], "cubes": cubes})
    return bones

def build_model():
    bones = []
    root = {"name": "root", "pivot": [0, 0, 0], "cubes": []}
    bones.append(root)

    body_cubes = []

    # 1. Main Ladder Chassis / Frame Rails (z: -48 to +44, y: 8..13)
    body_cubes.append(make_cube([-11, 8, -48], [4, 5, 92], FRAME_CELL))
    body_cubes.append(make_cube([7, 8, -48], [4, 5, 92], FRAME_CELL))
    # Crossmembers
    for z_c in (-42, -18, 6, 28, 42):
        body_cubes.append(make_cube([-7, 9, z_c], [14, 4, 3], FRAME_CELL))
    # Skid plate underneath engine (z: -44 to -18)
    body_cubes.append(make_cube([-10, 6, -44], [20, 2, 26], FRAME_CELL))

    # 2. Front Heavy Steel Bullbar & Winch (z: -52 to -48)
    body_cubes.append(make_cube([-18, 8, -52], [36, 6, 4], BUMPER_CELL)) # Main bumper beam
    body_cubes.append(make_cube([-16, 14, -51], [32, 2, 2], BUMPER_CELL)) # Top bullbar tube
    body_cubes.append(make_cube([-16, 10, -51], [2, 4, 2], BUMPER_CELL))  # Left upright
    body_cubes.append(make_cube([14, 10, -51], [2, 4, 2], BUMPER_CELL))   # Right upright
    # Winch spool
    body_cubes.append(make_cube([-5, 9, -50], [10, 4, 3], FRAME_CELL))
    body_cubes.append(make_cube([-3, 10, -52], [6, 2, 2], STRAP_CELL)) # Winch hook/fairlead
    # D-ring recovery shackles
    body_cubes.append(make_cube([-13, 7, -53], [2, 3, 2], AMBER_CELL))
    body_cubes.append(make_cube([11, 7, -53], [2, 3, 2], AMBER_CELL))

    # 3. Engine Hood & Grille (z: -48 to -20, y: 13..23)
    body_cubes.append(make_cube([-16, 13, -48], [32, 10, 28], ARMOR_CELL)) # Engine bay
    # Hood slope / cowl
    body_cubes.append(make_cube([-15, 23, -44], [30, 2, 24], ARMOR_CELL))  # Hood bulge
    # Radiator grille
    body_cubes.append(make_cube([-12, 15, -49], [24, 7, 1], FRAME_CELL))
    # Dual round headlights
    body_cubes.append(make_cube([-15, 17, -49], [3, 4, 1], HEADLIGHT_CELL))
    body_cubes.append(make_cube([12, 17, -49], [3, 4, 1], HEADLIGHT_CELL))
    # Amber indicator markers
    body_cubes.append(make_cube([-16, 15, -49], [2, 2, 1], AMBER_CELL))
    body_cubes.append(make_cube([14, 15, -49], [2, 2, 1], AMBER_CELL))

    # Raised Air Snorkel (Right side, x = -17)
    body_cubes.append(make_cube([-18, 16, -34], [2, 14, 2], CANISTER_CELL)) # vertical tube
    body_cubes.append(make_cube([-18, 30, -36], [3, 3, 5], CANISTER_CELL))  # intake head

    # 4. Front Fenders & Flared Wheel Arches (Front axle at z = -32)
    body_cubes.append(make_cube([-19, 14, -44], [3, 6, 24], ARMOR_CELL)) # Right fender
    body_cubes.append(make_cube([16, 14, -44], [3, 6, 24], ARMOR_CELL))  # Left fender

    # 5. Two-Door Armored Crew Cab (z: -20 to 6, y: 13..34)
    # Lower cab body
    body_cubes.append(make_cube([-18, 13, -20], [36, 10, 26], ARMOR_CELL))
    # Upper cab frame (Roof at y = 33)
    body_cubes.append(make_cube([-17, 23, -20], [34, 10, 26], ARMOR_CELL))
    # Windshield (tilted ballistic glass)
    body_cubes.append(make_cube([-15, 24, -21], [30, 8, 1], GLASS_CELL))
    # Side door windows
    body_cubes.append(make_cube([-18, 24, -16], [1, 7, 18], GLASS_CELL)) # Right window
    body_cubes.append(make_cube([17, 24, -16], [1, 7, 18], GLASS_CELL))  # Left window
    # Rear cab glass
    body_cubes.append(make_cube([-14, 25, 5], [28, 7, 1], GLASS_CELL))

    # Roof visor & LED Light Bar
    body_cubes.append(make_cube([-17, 33, -22], [34, 2, 4], BUMPER_CELL))
    body_cubes.append(make_cube([-14, 34, -21], [28, 2, 1], HEADLIGHT_CELL)) # Off-road LED bar

    # Dual Heavy Side Mirrors
    body_cubes.append(make_cube([-21, 23, -19], [3, 5, 2], FRAME_CELL))
    body_cubes.append(make_cube([18, 23, -19], [3, 5, 2], FRAME_CELL))

    # Interior Seating & Dash
    body_cubes.append(make_cube([-15, 17, -18], [30, 4, 6], INTERIOR_CELL)) # Dash
    # Driver seat (Left side x: 3..13, cushion y: 15, backrest y: 17..27)
    body_cubes.append(make_cube([4, 15, -10], [9, 3, 9], INTERIOR_CELL))
    body_cubes.append(make_cube([4, 18, -2], [9, 9, 2], INTERIOR_CELL))
    # Co-Driver seat (Right side x: -13..-3)
    body_cubes.append(make_cube([-13, 15, -10], [9, 3, 9], INTERIOR_CELL))
    body_cubes.append(make_cube([-13, 18, -2], [9, 9, 2], INTERIOR_CELL))

    # High-gain whip antenna
    body_cubes.append(make_cube([-17, 33, 4], [1, 14, 1], FRAME_CELL))

    # 6. Tubular Steel Sports Roll-Cage / Headache Rack (z = 6..12)
    body_cubes.append(make_cube([-17, 23, 6], [2, 13, 2], BUMPER_CELL)) # Right vertical bar
    body_cubes.append(make_cube([15, 23, 6], [2, 13, 2], BUMPER_CELL))  # Left vertical bar
    body_cubes.append(make_cube([-17, 34, 6], [34, 2, 2], BUMPER_CELL)) # Top crossbar
    # Rearward diagonal braces
    body_cubes.append(make_cube([-17, 20, 7], [2, 2, 14], BUMPER_CELL))
    body_cubes.append(make_cube([15, 20, 7], [2, 2, 14], BUMPER_CELL))

    # 7. Rear Walkable Cargo Bed (z: 6 to 44, floor top y = 14)
    # Bed sub-frame & diamond-plate floor (Width = 34 px = 2.125 blocks, Length = 38 px = 2.375 blocks)
    body_cubes.append(make_cube([-17, 13, 6], [34, 1, 38], DECK_CELL)) # Solid Walkable Deck Floor
    # Left bed wall & tie-down rail (x = 15..18, y: 14..22)
    body_cubes.append(make_cube([15, 14, 6], [3, 8, 38], ARMOR_CELL))
    body_cubes.append(make_cube([15, 22, 6], [3, 2, 38], BUMPER_CELL)) # Top tie-down rail
    # Right bed wall & tie-down rail (x = -18..-15)
    body_cubes.append(make_cube([-18, 14, 6], [3, 8, 38], ARMOR_CELL))
    body_cubes.append(make_cube([-18, 22, 6], [3, 2, 38], BUMPER_CELL))
    # Front bed bulkhead (behind cab)
    body_cubes.append(make_cube([-15, 14, 6], [30, 8, 2], ARMOR_CELL))

    # Rear Fenders over rear axle (Rear axle at z = 24)
    body_cubes.append(make_cube([-20, 14, 12], [3, 6, 24], ARMOR_CELL))
    body_cubes.append(make_cube([17, 14, 12], [3, 6, 24], ARMOR_CELL))

    # Rear Bumper & Tow Receiver (z = 44..46)
    body_cubes.append(make_cube([-18, 8, 44], [36, 5, 2], BUMPER_CELL))
    # Military NATO taillight clusters
    body_cubes.append(make_cube([-17, 15, 44], [3, 5, 1], RED_CELL))
    body_cubes.append(make_cube([-17, 13, 44], [3, 2, 1], AMBER_CELL))
    body_cubes.append(make_cube([14, 15, 44], [3, 5, 1], RED_CELL))
    body_cubes.append(make_cube([14, 13, 44], [3, 2, 1], AMBER_CELL))
    # Heavy exhaust tailpipe
    body_cubes.append(make_cube([11, 7, 40], [3, 3, 5], EXHAUST_CELL))

    bones.append({"name": "body", "parent": "root", "pivot": [0, 12, 0], "cubes": body_cubes})

    # 8. Articulated Rear Tailgate (Pivot at bottom lip: y = 14, z = 44)
    # In closed state: vertical wall from y 14..22.
    # In open state: pivots down 90 deg (rotX = 90) to become a level walk-on ramp!
    tailgate_cubes = [
        make_cube([-15, 14, 44], [30, 8, 2], ARMOR_CELL),
        make_cube([-15, 21, 43], [30, 1, 1], BUMPER_CELL), # Latch handle
        make_cube([-14, 15, 44], [28, 6, 1], DECK_CELL)    # Inner bed face
    ]
    bones.append({"name": "rear_tailgate", "parent": "body", "pivot": [0, 14, 44], "cubes": tailgate_cubes})

    # 9. Cargo Tie-Down Straps (hidden when empty)
    strap_cubes = [
        make_cube([-14, 16, 14], [28, 1, 2], STRAP_CELL), # Cross strap front
        make_cube([-14, 16, 30], [28, 1, 2], STRAP_CELL), # Cross strap rear
    ]
    bones.append({"name": "cargo_straps", "parent": "body", "pivot": [0, 15, 20], "cubes": strap_cubes})

    # 10. Running Gear (Axles & 4 Wheels)
    # Front axle at z = -32, y = 11; Rear axle at z = 24, y = 11
    # Axle casings
    body_cubes.append(make_cube([-14, 10, -33], [28, 3, 3], FRAME_CELL)) # Front axle tube
    body_cubes.append(make_cube([-4, 9, -34], [8, 5, 5], FRAME_CELL))    # Front diff pumpkin
    body_cubes.append(make_cube([-14, 10, 23], [28, 3, 3], FRAME_CELL))  # Rear axle tube
    body_cubes.append(make_cube([-4, 9, 22], [8, 5, 5], FRAME_CELL))     # Rear diff pumpkin

    # Wheel definitions (Track width: wheel centers at x = +-19)
    bones.extend(make_wheel("wheel_fl", "body", 19, 11, -32, steer=True))
    bones.extend(make_wheel("wheel_fr", "body", -19, 11, -32, steer=True))
    bones.extend(make_wheel("wheel_rl", "body", 19, 11, 24, steer=False))
    bones.extend(make_wheel("wheel_rr", "body", -19, 11, 24, steer=False))

    return per_face_uv(bones)

def rot(p, piv, r):
    x, y, z = p[0] - piv[0], p[1] - piv[1], p[2] - piv[2]
    ax, ay, az = math.radians(-r[0]), math.radians(r[1]), math.radians(-r[2])
    # Rot X
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    # Rot Y
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    # Rot Z
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    return (x + piv[0], y + piv[1], z + piv[2])

def render_view(bones, tex_drawer, out_wh, yaw, pitch, pose=None, scale=6.0, offset_y=0.58):
    if pose is None: pose = {}
    W, H = out_wh
    zbuf = [1e9] * (W * H)
    # Pale Sky grey background (222, 230, 238) like C-130 reference
    img = bytearray([222, 230, 238, 255] * (W * H))
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def proj(p):
        x, y, z = -p[0], p[1], p[2] # GeckoLib mirrors X
        x, z = x * cy - z * sy, x * sy + z * cy
        y, z = y * cp - z * sp, y * sp + z * cp
        return W / 2 + x * scale, H * offset_y - y * scale, z

    light = (0.4, 0.8, -0.45)
    tex = tex_drawer.buf

    # bone parent chain
    by_name = {b["name"]: b for b in bones}
    def chain(b):
        c = []
        while b:
            c.append(b); b = by_name.get(b.get("parent"))
        return c

    for b in bones:
        if b["name"] == "cargo_straps": continue # hide straps in default preview
        ch = chain(b)
        for c in b.get("cubes", []):
            (ox, oy, oz), (sx, sy_, sz) = c["origin"], c["size"]
            P = lambda a, b_, d: (ox + a * sx, oy + b_ * sy_, oz + d * sz)
            faces = {
                "north": (P(1, 1, 0), P(0, 1, 0), P(1, 0, 0), (0, 0, -1)),
                "south": (P(0, 1, 1), P(1, 1, 1), P(0, 0, 1), (0, 0, 1)),
                "east":  (P(1, 1, 1), P(1, 1, 0), P(1, 0, 1), (1, 0, 0)),
                "west":  (P(0, 1, 0), P(0, 1, 1), P(0, 0, 0), (-1, 0, 0)),
                "up":    (P(0, 1, 0), P(1, 1, 0), P(0, 1, 1), (0, 1, 0)),
                "down":  (P(0, 0, 1), P(1, 0, 1), P(0, 0, 0), (0, -1, 0))
            }
            for fn, (o, ue, ve, nrm) in faces.items():
                pts = [o, ue, ve]
                for x in ch:
                    if x["name"] in pose:
                        r = pose[x["name"]]
                        piv = x["pivot"]
                        pts = [rot(pt, piv, r) for pt in pts]
                        nrm = tuple(a - b for a, b in zip(rot(nrm, (0,0,0), r), (0,0,0)))
                o, ue, ve = pts
                lum = 0.52 + 0.48 * max(0, -nrm[0] * light[0] + nrm[1] * light[1] + nrm[2] * light[2])
                po, pu, pv = proj(o), proj(ue), proj(ve)
                du, dv = [pu[i] - po[i] for i in range(3)], [pv[i] - po[i] for i in range(3)]
                det = du[0] * dv[1] - du[1] * dv[0]
                if abs(det) < 1e-6: continue
                xs = [po[0], pu[0], pv[0], pu[0] + dv[0]]
                ys = [po[1], pu[1], pv[1], pu[1] + dv[1]]
                fuv = c["uv"][fn]
                min_x = max(0, int(min(xs)))
                max_x = min(W, int(max(xs)) + 1)
                min_y = max(0, int(min(ys)))
                max_y = min(H, int(max(ys)) + 1)
                for yy in range(min_y, max_y):
                    for xx in range(min_x, max_x):
                        qx, qy = xx + 0.5 - po[0], yy + 0.5 - po[1]
                        s = (qx * dv[1] - qy * dv[0]) / det
                        t = (du[0] * qy - du[1] * qx) / det
                        if not (0 <= s <= 1 and 0 <= t <= 1): continue
                        z = po[2] + s * du[2] + t * dv[2]
                        i = yy * W + xx
                        if z >= zbuf[i]: continue
                        tu = int(fuv["uv"][0] + min(s * fuv["uv_size"][0], fuv["uv_size"][0] - 0.5))
                        tv = int(fuv["uv"][1] + min(t * fuv["uv_size"][1], fuv["uv_size"][1] - 0.5))
                        k = (tv * 512 + tu) * 4
                        alpha = tex[k + 3]
                        if alpha < 20: continue
                        zbuf[i] = z
                        img[i * 4:i * 4 + 3] = bytes(min(255, int(tex[k + j] * lum)) for j in range(3))
    return bytes(img)

def stitch_vertical(panel_bytes_list, W, H_panel):
    total_H = H_panel * len(panel_bytes_list)
    out = bytearray(W * total_H * 4)
    for idx, p in enumerate(panel_bytes_list):
        y_start = idx * H_panel
        out[y_start * W * 4 : (y_start + H_panel) * W * 4] = p
    return bytes(out), W, total_H

def main():
    print("Generating Tactical Technical 4x4 Model & Textures...")
    tex = paint_texture()
    bones = build_model()
    geo = {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.tactical_technical",
                "texture_width": 512,
                "texture_height": 512,
                "visible_bounds_width": 6,
                "visible_bounds_height": 4,
                "visible_bounds_offset": [0, 1.5, 0]
            },
            "bones": bones
        }]
    }

    # Save to scratch / brain
    brain_dir = os.path.abspath("C:/Users/Purachai/.gemini/antigravity/brain/d0082229-568a-4374-9437-f2414c618d6a")
    out_img = os.path.join(brain_dir, "tactical_technical_5view.png")

    W, H_panel = 720, 360
    scale = 5.2

    print("Rendering View 1: Isometric Front (3/4 Front, Tailgate Closed)...")
    p1 = render_view(bones, tex, (W, H_panel), yaw=35, pitch=-22, pose={}, scale=scale, offset_y=0.62)

    print("Rendering View 2: Isometric Rear (3/4 Rear, Tailgate Closed)...")
    p2 = render_view(bones, tex, (W, H_panel), yaw=215, pitch=-22, pose={}, scale=scale, offset_y=0.62)

    print("Rendering View 3: Direct Rear Open (Tailgate Down Ramp 90°)...")
    p3 = render_view(bones, tex, (W, H_panel), yaw=180, pitch=-12, pose={"rear_tailgate": [90, 0, 0]}, scale=scale * 1.05, offset_y=0.64)

    print("Rendering View 4: Isometric Rear Open (3/4 Rear, Tailgate Down Ramp)...")
    p4 = render_view(bones, tex, (W, H_panel), yaw=220, pitch=-26, pose={"rear_tailgate": [90, 0, 0]}, scale=scale, offset_y=0.62)

    print("Rendering View 5: True Side Profile (Ground Clearance & Axle Spacing)...")
    p5 = render_view(bones, tex, (W, H_panel), yaw=90, pitch=0, pose={}, scale=scale * 0.95, offset_y=0.55)

    print("Stitching 5-view sheet...")
    stitched_bytes, total_w, total_h = stitch_vertical([p1, p2, p3, p4, p5], W, H_panel)
    png_data = make_png(total_w, total_h, stitched_bytes)

    with open(out_img, "wb") as f:
        f.write(png_data)

    print(f"SUCCESS: 5-View Concept Sheet rendered to:\n{out_img}")

if __name__ == "__main__":
    main()
