#!/usr/bin/env python3
"""Insurgent / Mercenary Tactical Technical 4x4 (Tier 1 Combat Utility Vehicle) - Revision 4 (Balanced Side Profile)
Proportion Refinements:
- Authentic rugged 4x4 truck silhouette (Toyota Land Cruiser 79 / Oshkosh Utility stance):
  * Upright rugged windshield rake (8 units rake over 15 units height, no sports-car slant).
  * Muscular, compact hood (length 26 units from z=-44 to -18).
  * Front bumper & winch tucked tight (z=-48 to -44) with steep 45° approach angle.
  * Balanced cab-to-bed ratio (Hood: 26u, Cab: 28u, Bed: 36u).
  * Front axle at z=-30, Rear axle at z=28.
  * Level 4x4 high ground clearance stance.
- Rock slider side steps tucked tight under door sill with frame brackets.
- Re-renders the 5-view concept sheet to insurgent_technical_5view.png.
"""

import json
import math
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Titan Combat", "scripts"))
from generate_transport_assets import TextureDrawer, make_png, per_face_uv, rod, write_geo

# 512x512 texture atlas with 64x64 material cells
HULL, HULL2, APPLIQUE, DECK, MUD, STEEL, BARS, GRILLE = [[i * 64, 0] for i in range(8)]
TYRE, RIM, RUBBER, GLASS, LENS, TAIL, AMBER, OPTIC = [[i * 64, 64] for i in range(8)]
WOOD, STRAP, JERRY, BRASS, GUN, STENCIL, WELD, MUDARMOR = [[i * 64, 128] for i in range(8)]

BASE = (118, 126, 92)
BASE_DARK = (92, 98, 72)

def hash_noise(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0

def smooth(x, y, s, cell=6):
    gx, gy = x / cell, y / cell
    x0, y0 = int(gx), int(gy)
    fx, fy = gx - x0, gy - y0
    a, b = hash_noise(x0, y0, s), hash_noise(x0 + 1, y0, s)
    c, d = hash_noise(x0, y0 + 1, s), hash_noise(x0 + 1, y0 + 1, s)
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy

def paint_texture():
    t = TextureDrawer(512, 512)
    px = lambda x, y, c, a=255: t.set_pixel(x, y, c[0], c[1], c[2], a)
    add = lambda c, d: tuple(max(0, min(255, int(v + d))) for v in c)

    def paint_armor(cell, base_color, seam=16, mud=0.0, s=1):
        u0, v0 = cell
        for y in range(64):
            for x in range(64):
                val = (smooth(x, y, s) - 0.5) * 16 + (hash_noise(x, y, s + 9) - 0.5) * 6
                c = add(base_color, val)
                streak = hash_noise(x, 0, s + 3)
                if streak > 0.78:
                    c = add(c, -16 * (1 - y / 64) * (streak - 0.78) * 5)
                if hash_noise(x, y, s + 5) > 0.982:
                    c = add(c, 28)
                if seam and (x % seam == 0 or y % seam == 0):
                    c = add(c, -30)
                if mud:
                    m = smooth(x, y, s + 7, 4) + hash_noise(x, y, s + 8) * 0.3
                    if m > 1.0 - mud:
                        c = (78, 62, 42)
                px(u0 + x, v0 + y, c)

    paint_armor(HULL, BASE, seam=0, s=2)
    paint_armor(HULL2, BASE_DARK, seam=0, s=3)
    paint_armor(MUD, (74, 58, 38), seam=0, mud=0.55, s=4)
    paint_armor(MUDARMOR, BASE, seam=16, mud=0.38, s=5)
    paint_armor(APPLIQUE, add(BASE, -14), seam=0, s=6)

    paint_armor(WELD, BASE, seam=0, s=7)
    for i in range(64):
        for k in (16, 48):
            px(WELD[0] + i, WELD[1] + k, add(BASE, -24 + (i % 3) * 14))
            px(WELD[0] + k, WELD[1] + i, add(BASE, -24 + (i % 3) * 14))

    paint_armor(STENCIL, BASE, s=8)
    t.draw_text(STENCIL[0] + 6, STENCIL[1] + 12, "07", (220, 216, 195), 1)

    for y in range(64):
        for x in range(64):
            grit = (hash_noise(x, y, 11) > 0.5) * 16 + (x % 4 == 0 and y % 4 == 0) * 12
            px(DECK[0] + x, DECK[1] + y, add((85, 88, 82), grit - 8))
            px(STEEL[0] + x, STEEL[1] + y, add((55, 58, 62), (smooth(x, y, 12) - 0.5) * 14))
            px(BARS[0] + x, BARS[1] + y, add((35, 37, 40), (x == 0 or y == 0) * 16))
            px(GRILLE[0] + x, GRILLE[1] + y, (28, 30, 32) if y % 2 == 0 else add(BASE, -32))

            tread = 54 if (y + (x // 4 % 2) * 2) % 4 < 2 else 24
            px(TYRE[0] + x, TYRE[1] + y, (tread, tread, tread - 2))
            px(RUBBER[0] + x, RUBBER[1] + y, add((34, 34, 32), (hash_noise(x, y, 15) - 0.5) * 8))

            gl_c = (24, 40, 52) if (x + y) % 6 == 0 else (16, 26, 36)
            t.set_pixel(GLASS[0] + x, GLASS[1] + y, gl_c[0], gl_c[1], gl_c[2], 220)

            px(LENS[0] + x, LENS[1] + y, (252, 248, 220) if (x + y) % 4 == 0 else (210, 210, 190))
            px(TAIL[0] + x, TAIL[1] + y, (210, 24, 24) if (x + y) % 4 == 0 else (145, 16, 16))
            px(AMBER[0] + x, AMBER[1] + y, (255, 165, 20))
            px(OPTIC[0] + x, OPTIC[1] + y, (0, 210, 245) if (x + y) % 5 == 0 else (15, 90, 140))
            px(WOOD[0] + x, WOOD[1] + y, add((125, 92, 58), (hash_noise(0, y, 16) - 0.5) * 20))
            px(STRAP[0] + x, STRAP[1] + y, add((235, 125, 18), ((x + y) % 3 == 0) * -20))
            px(JERRY[0] + x, JERRY[1] + y, add((95, 102, 70), (x % 6 == 0) * -16 + (x == 0 or y == 0) * 14))
            px(BRASS[0] + x, BRASS[1] + y, (175, 145, 70))
            px(GUN[0] + x, GUN[1] + y, add((35, 35, 38), (x == 0 or y == 0) * 20))

            d = math.hypot(x - 9, y - 9)
            rc = add(BASE, -20)
            if d < 2.8:
                rc = (40, 42, 45)
            elif 5.2 < d < 6.8 and int(math.degrees(math.atan2(y - 9, x - 9)) + 360) % 45 < 14:
                rc = (230, 230, 220)
            elif d > 7.8:
                rc = add(BASE, -45)
            px(RIM[0] + x, RIM[1] + y, rc)

    return t

def box(o, s, uv):
    return {"origin": list(o), "size": list(s), "uv": uv}

def mirror(c):
    m = json.loads(json.dumps(c))
    m["origin"][0] = -(c["origin"][0] + c["size"][0])
    if "pivot" in m:
        m["pivot"][0] = -m["pivot"][0]
        m["rotation"] = [m["rotation"][0], -m["rotation"][1], -m["rotation"][2]]
    return m

def both(*cubes):
    return [c for cube in cubes for c in (cube, mirror(cube))]

def make_dodec_wheel(cx, cy, cz, left):
    a, w = 11.0, 7.5
    x0 = cx - w / 2
    cubes = [{"origin": [x0, cy - a, cz - a * math.tan(math.radians(15))],
              "size": [w, 2 * a, round(2 * a * math.tan(math.radians(15)), 3)],
              "pivot": [cx, cy, cz], "rotation": [k * 30, 0, 0], "uv": TYRE} for k in range(6)]
    ra = 6.8
    rx = x0 + w - 0.4 if left else x0 - 0.4
    cubes += [{"origin": [rx, cy - ra, cz - ra * 0.27],
               "size": [0.8, 2 * ra, round(2 * ra * 0.27, 3)],
               "pivot": [cx, cy, cz], "rotation": [k * 30, 0, 0], "uv": RIM} for k in range(6)]
    hx = x0 + w + 0.4 if left else x0 - 1.6
    cubes += [box([hx, cy - 2.5, cz - 2.5], [1.2, 5, 5], STEEL),
              box([hx + (0.4 if left else 0), cy - 0.8, cz - 0.8], [0.8, 1.6, 1.6], BRASS)]
    return cubes

def build_chassis_and_cab():
    c = []

    # 1. Ladder frame rails (z = -46 to +46, length 92 units)
    c += both(box([8, 6, -46], [3.5, 4.5, 92], STEEL))
    for z in (-38, -18, 4, 26, 42):
        c += [box([-8, 7, z], [16, 3, 2.5], STEEL)]
    # Front angled skid plate (steep 45-degree approach clearance)
    c += [rod((0, 6, -46), (0, 9, -24), 24, 2, STEEL)]

    # 2. Front Heavy Steel Pipe Bullbar & Winch Rig (Tucked tight at z = -48 to -44)
    c += [box([-17, 8, -48], [34, 4.5, 3], BARS)]                      # Main bumper bar
    c += both(rod((17, 8, -48), (17, 13, -44), 2.5, 2.5, BARS))        # Corner brush guards
    c += [rod((0, 12, -47.5), (0, 16, -45.5), 26, 2.2, BARS)]          # Center loop
    c += both(box([9, 8, -47], [2, 6, 2], BARS))                       # Center uprights
    # Winch spool
    c += [box([-5, 8.5, -46.5], [10, 3.5, 3], STEEL)]
    c += [box([-3.5, 9.5, -48.2], [7, 1.8, 1.8], STRAP)]
    c += both(box([12, 7, -48.5], [2.2, 3.0, 1.8], AMBER))
    c += both(box([13, 9.0, -48.0], [2.2, 2.2, 0.4], LENS))

    # 3. Muscular Hood & Grille (z = -44 to -18, length 26 units)
    c += [box([-15.5, 11, -44], [31, 10, 2], HULL2)]                  # Grille surround
    c += [box([-12.5, 12, -44.5], [25, 8, 1], GRILLE)]                 # Grille insert
    c += both(box([12.0, 13, -44.6], [3, 4, 0.5], LENS),
              box([12.0, 17.5, -44.6], [3, 1.8, 0.5], AMBER),
              box([11.5, 12.5, -44.8], [4, 7.2, 0.4], BARS))
    # Slanted hood plate (y: 20 -> 23.5, z: -44 -> -18)
    c += [rod((0, 20, -44), (0, 23.5, -18), 30, 2, HULL)]
    c += [rod((0, 21.8, -40), (0, 24.5, -20), 16, 1.5, HULL2)]         # Center power cowl
    for lz in (-38, -32, -26):
        c += both(box([3, 23.0, lz], [4.5, 0.4, 2.2], GRILLE))

    # Front wheel arches with clean 45-degree chamfers (Front axle at z = -30)
    c += both(
        box([15.5, 11, -42], [3.2, 9, 8], HULL),
        box([15.5, 11, -24], [3.2, 9, 6], HULL),
        rod((17, 19.5, -40), (17, 22.5, -30), 2.8, 2, HULL),
        rod((17, 22.5, -30), (17, 19.5, -22), 2.8, 2, HULL),
        box([18.2, 18.5, -38], [1, 2, 16], RUBBER)
    )

    # 4. Elevated Snorkel (Right side)
    c += [rod((-17.2, 14, -30), (-17.2, 34, -16), 2.2, 2.2, BARS)]
    c += [box([-18.5, 33.5, -18], [3.8, 3.5, 5], STEEL)]

    # 5. Clean Balanced Armored Cab (z = -18 to +10, length 28 units)
    # Cab floor at y = 10
    c += [box([-15.5, 10, -18], [31, 1.5, 28], DECK)]

    # Lower Cab Doors and Sills
    c += both(
        box([15.5, 11, -18], [2.2, 13, 28], HULL),                     # Door outer skin
        box([17.5, 9.5, -16], [2.2, 2.0, 24], BARS),                   # Rock slider step tucked tight
        box([17.6, 15, -3], [0.8, 1.8, 3.5], STEEL),                   # Flush door handle
        box([15.5, 9.5, -12], [2.0, 1.5, 2.0], STEEL),                 # Front mounting bracket
        box([15.5, 9.5, -4], [2.0, 1.5, 2.0], STEEL),                  # Center mounting bracket
        box([15.5, 9.5, 4], [2.0, 1.5, 2.0], STEEL)                    # Rear mounting bracket
    )

    # Authentic Truck Windshield Rake (Steeper, rugged: z: -18 -> -10, y: 23 -> 36)
    c += both(rod((16, 23, -18), (15, 36, -10), 2.2, 2.5, HULL))       # A-pillars
    c += [rod((0, 23, -18), (0, 36, -10), 28, 1.5, GLASS)]             # Windshield glass
    c += [rod((0, 23, -17.8), (0, 23.8, -17), 28.5, 1.2, HULL2)]       # Cowl trim
    c += both(rod((6, 23.5, -17.5), (8, 32, -12), 0.5, 0.5, GUN))      # Wipers

    # Cab Roof (z = -11 to +10, length 21 units)
    c += [box([-15.5, 36, -11], [31, 1.5, 21], HULL)]
    c += both(box([15.5, 36.5, -11], [1.2, 1.0, 21], HULL2))           # Side drip rails
    c += [box([-15.5, 36.5, -11], [31, 1.0, 1.2], HULL2)]

    # Cab Door Windows & B-Pillars
    c += both(
        box([15.8, 24, -10], [0.6, 12, 16], GLASS),                    # Door side glass
        box([15.5, 24, 6], [2.0, 12, 4], HULL)                         # Solid B-pillar rear post
    )

    # Rear Cab Wall with Centered Window
    c += [box([-15.5, 11, 9], [31, 25, 1.5], HULL)]
    c += [box([-10, 24, 9.2], [20, 8, 0.6], GLASS)]

    # Roof LED Light Bar & Whip Antenna
    c += [box([-13.5, 37.5, -11], [27, 2.0, 2.2], BARS)]
    c += [box([-12.5, 37.8, -11.5], [25, 1.4, 0.4], LENS)]
    c += [box([-16, 36.5, 7], [1.8, 2.5, 1.8], STEEL)]
    c += [rod((-15.2, 38, 8), (-14.2, 53, 11), 0.7, 0.7, STEEL)]

    # Cockpit Interior (Driver Left x = 3..12, Passenger Right x = -12..-3)
    c += [box([-14, 16, -15], [28, 4.5, 6], GUN)]                      # Dash
    c += [box([8.5, 18.5, -11.5], [4.5, 4.5, 1.0], STEEL)]             # Steering wheel
    c += [box([0, 12, -6], [2.5, 4.5, 1.2], STEEL)]                    # Shifter
    # Bucket Seats (Cushion y = 13, eye height y = 30)
    c += both(
        box([4, 11.5, -6], [8.5, 2.5, 9.5], STEEL),
        box([4, 14, 3.5], [8.5, 14, 2.0], STEEL),
        box([5.5, 28, 3.8], [5.5, 3.5, 1.5], RUBBER)
    )

    # 6. Tubular Steel Headache Rack (Mounted right behind cab at z = 10.5)
    c += both(
        rod((16, 11, 10.5), (16, 36.5, 10.5), 2.2, 2.2, BARS),
        rod((16, 35.5, 10.5), (16, 18, 24), 2.0, 2.0, BARS)
    )
    c += [box([-16, 35.5, 9.5], [32, 2.2, 2.2], BARS)]
    c += both(box([9, 34, 11.5], [2.8, 2.2, 1.8], BARS),
              box([9.4, 34.4, 13.2], [2.0, 1.4, 0.4], LENS))

    # 7. Walkable Cargo Bed (z = 10 to 46, length 36 units)
    c += [box([-15.5, 11, 10], [31, 1.5, 36], DECK)]
    c += both(
        box([14.5, 12.5, 10], [2, 8.5, 36], HULL),                     # Bed inner wall
        box([14, 21, 10], [3, 1.5, 36], BARS),                         # Top tie-down rail
        box([17.5, 12, 12], [1.5, 8.5, 32], HULL2)                     # Outer bedside skin
    )
    # Rear wheel arch flares (Rear axle at z = 28)
    c += both(
        rod((17, 19.5, 18), (17, 22.5, 28), 3, 2, HULL),
        rod((17, 22.5, 28), (17, 19.5, 38), 3, 2, HULL),
        box([18.5, 18.5, 22], [1, 2, 16], RUBBER),
        box([17.5, 5, 38.5], [2, 9, 0.5], RUBBER)
    )

    # 8. Rear Bumper & Lighting (z = 46..48)
    c += [box([-18, 7, 46], [36, 5, 2.5], BARS)]
    c += [box([-3, 6, 45], [6, 4, 3], STEEL)]
    c += both(
        box([14, 14, 46.2], [2.8, 3.5, 0.5], TAIL),
        box([14, 17.5, 46.2], [2.8, 2.2, 0.5], AMBER),
        box([14, 11.5, 46.2], [2.8, 2.2, 0.5], LENS),
        box([13.5, 11, 46.5], [3.8, 9, 0.4], BARS)
    )
    c += [rod((12, 6, 38), (14, 5, 44), 2.2, 2.2, GUN)]

    # Bed accessories
    c += [box([-17.8, 14, 26], [2.2, 6, 14], APPLIQUE)]
    c += [box([17.8, 13, 12], [2.8, 8, 5], JERRY),
          box([17.8, 19.5, 13], [2.5, 1.5, 3], JERRY),
          box([17.5, 16, 11.5], [3.2, 1.2, 6], STRAP)]

    return c

def build_tailgate():
    c = [
        box([-14.5, 12, 46], [29, 9, 2], HULL),
        box([-13.5, 13, 45.5], [27, 7, 0.8], DECK),
        box([-14, 19.5, 47.5], [28, 1.2, 1.2], BARS),
        box([-4, 16.5, 48], [8, 2.5, 1], STEEL)
    ]
    return c

def build_full_model():
    bones = []
    root = {"name": "root", "pivot": [0, 0, 0], "cubes": []}
    bones.append(root)

    body_cubes = build_chassis_and_cab()
    bones.append({"name": "body", "parent": "root", "pivot": [0, 11, 0], "cubes": body_cubes})

    tailgate_cubes = build_tailgate()
    bones.append({"name": "rear_tailgate", "parent": "body", "pivot": [0, 12, 46], "cubes": tailgate_cubes})

    straps = [
        box([-13.5, 13.5, 18], [27, 1.2, 2.5], STRAP),
        box([-13.5, 13.5, 34], [27, 1.2, 2.5], STRAP),
        box([-14.2, 13, 17], [1.5, 3, 4], STEEL),
        box([12.7, 13, 17], [1.5, 3, 4], STEEL)
    ]
    bones.append({"name": "cargo_straps", "parent": "body", "pivot": [0, 12, 26], "cubes": straps})

    # Steering & Wheels (Axles at y = 11; front at z=-30, rear at z=28)
    bones.append({"name": "steer_fl", "parent": "body", "pivot": [18.5, 11, -30], "cubes": []})
    bones.append({"name": "wheel_fl", "parent": "steer_fl", "pivot": [18.5, 11, -30], "cubes": make_dodec_wheel(18.5, 11, -30, left=True)})
    bones.append({"name": "steer_fr", "parent": "body", "pivot": [-18.5, 11, -30], "cubes": []})
    bones.append({"name": "wheel_fr", "parent": "steer_fr", "pivot": [-18.5, 11, -30], "cubes": make_dodec_wheel(-18.5, 11, -30, left=False)})
    bones.append({"name": "wheel_rl", "parent": "body", "pivot": [18.5, 11, 28], "cubes": make_dodec_wheel(18.5, 11, 28, left=True)})
    bones.append({"name": "wheel_rr", "parent": "body", "pivot": [-18.5, 11, 28], "cubes": make_dodec_wheel(-18.5, 11, 28, left=False)})

    return bones

def rot(p, piv, r):
    x, y, z = p[0] - piv[0], p[1] - piv[1], p[2] - piv[2]
    ax, ay, az = math.radians(-r[0]), math.radians(r[1]), math.radians(-r[2])
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    return (x + piv[0], y + piv[1], z + piv[2])

def render_view(bones, tex_drawer, out_wh, yaw, pitch, pose=None, scale=6.0, offset_y=0.58):
    if pose is None: pose = {}
    W, H = out_wh
    zbuf = [1e9] * (W * H)
    img = bytearray([222, 230, 238, 255] * (W * H))
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def proj(p):
        x, y, z = -p[0], p[1], p[2]
        x, z = x * cy - z * sy, x * sy + z * cy
        y, z = y * cp - z * sp, y * sp + z * cp
        return W / 2 + x * scale, H * offset_y - y * scale, z

    light = (0.42, 0.82, -0.42)
    tex = tex_drawer.buf

    by_name = {b["name"]: b for b in bones}
    def chain(b):
        c = []
        while b:
            c.append(b); b = by_name.get(b.get("parent"))
        return c

    for b in bones:
        if b["name"] == "cargo_straps": continue
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
            cube_piv = c.get("pivot", c["origin"])
            cube_rot = c.get("rotation", [0, 0, 0])
            for fn, (o, ue, ve, nrm) in faces.items():
                pts = [o, ue, ve]
                if cube_rot != [0, 0, 0]:
                    pts = [rot(pt, cube_piv, cube_rot) for pt in pts]
                    nrm = tuple(a - b for a, b in zip(rot(nrm, (0, 0, 0), cube_rot), (0, 0, 0)))
                for x in ch:
                    if x["name"] in pose:
                        r = pose[x["name"]]
                        piv = x["pivot"]
                        pts = [rot(pt, piv, r) for pt in pts]
                        nrm = tuple(a - b for a, b in zip(rot(nrm, (0, 0, 0), r), (0, 0, 0)))
                o, ue, ve = pts
                lum = 0.52 + 0.48 * max(0, -nrm[0] * light[0] + nrm[1] * light[1] + nrm[2] * light[2])
                po, pu, pv = proj(o), proj(ue), proj(ve)
                du, dv = [pu[i] - po[i] for i in range(3)], [pv[i] - po[i] for i in range(3)]
                det = du[0] * dv[1] - du[1] * dv[0]
                if abs(det) < 1e-6: continue
                xs = [po[0], pu[0], pv[0], pu[0] + dv[0]]
                ys = [po[1], pu[1], pv[1], pu[1] + dv[1]]

                base_uv = c["uv"]
                if isinstance(base_uv, dict):
                    fuv = base_uv[fn]
                    u0, v0 = fuv["uv"]
                    uw, vh = fuv["uv_size"]
                else:
                    u0, v0 = base_uv
                    uw, vh = 64, 64

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
                        tu = int(u0 + (s * uw) % uw)
                        tv = int(v0 + (t * vh) % vh)
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
    print("Re-rendering Insurgent Tactical Technical 4x4 (Balanced Side Profile Revision 4)...")
    tex = paint_texture()
    bones = build_full_model()

    brain_dir = os.path.abspath("C:/Users/Purachai/.gemini/antigravity/brain/d0082229-568a-4374-9437-f2414c618d6a")
    out_img = os.path.join(brain_dir, "insurgent_technical_5view.png")

    W, H_panel = 720, 360
    scale = 5.4

    print("Rendering View 1: 3/4 Front Isometric (Closed)...")
    p1 = render_view(bones, tex, (W, H_panel), yaw=35, pitch=-22, pose={}, scale=scale, offset_y=0.62)

    print("Rendering View 2: 3/4 Rear Isometric (Closed)...")
    p2 = render_view(bones, tex, (W, H_panel), yaw=215, pitch=-22, pose={}, scale=scale, offset_y=0.62)

    print("Rendering View 3: Direct Rear (Tailgate Dropped 90° as Walk Ramp)...")
    p3 = render_view(bones, tex, (W, H_panel), yaw=180, pitch=-12, pose={"rear_tailgate": [90, 0, 0]}, scale=scale * 1.05, offset_y=0.64)

    print("Rendering View 4: 3/4 Rear Isometric (Tailgate Open + Open Cargo Bed)...")
    p4 = render_view(bones, tex, (W, H_panel), yaw=220, pitch=-26, pose={"rear_tailgate": [90, 0, 0]}, scale=scale, offset_y=0.62)

    print("Rendering View 5: True Side Profile (Balanced Off-Road Truck Stance)...")
    p5 = render_view(bones, tex, (W, H_panel), yaw=90, pitch=0, pose={}, scale=scale * 0.95, offset_y=0.55)

    print("Stitching 5-view sheet...")
    stitched_bytes, total_w, total_h = stitch_vertical([p1, p2, p3, p4, p5], W, H_panel)
    png_data = make_png(total_w, total_h, stitched_bytes)

    with open(out_img, "wb") as f:
        f.write(png_data)

    print(f"SUCCESS: Rendered balanced revision to:\n{out_img}")

if __name__ == "__main__":
    main()
