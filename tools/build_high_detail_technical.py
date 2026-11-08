#!/usr/bin/env python3
"""High-Fidelity Tactical Technical 4x4 (Tier 1 Combat Utility Vehicle)
GeckoLib Model Architect Standard:
- Dodecagonal (12-sided) multi-layered wheels with lug treads, rim bolts, and brass hubs.
- Slanted A-pillars & 28-degree raked ballistic windshield.
- Compound angled hood with recessed cooling louvers & side chamfers.
- Multi-tube tubular steel bullbar with fairlead winch and tow clevises.
- Diamond-plate bed with tie-down rails and articulated drop tailgate.
- Layered texture with rain-streaks, paint chips, weld beads, and non-skid grit.
"""

import json
import math
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Titan Combat", "scripts"))
from generate_transport_assets import TextureDrawer, make_png, rod

# Texture cells (64x64 on 512x512 atlas)
HULL, HULL2, APPLIQUE, DECK, MUD, STEEL, BARS, GRILLE = [[i * 64, 0] for i in range(8)]
TYRE, RIM, RUBBER, GLASS, LENS, TAIL, AMBER, OPTIC = [[i * 64, 64] for i in range(8)]
WOOD, STRAP, JERRY, BRASS, GUN, STENCIL, WELD, MUDARMOR = [[i * 64, 128] for i in range(8)]

# Base colors: NATO Coyote Tan / Field Grey
BASE = (168, 158, 132)
BASE_DARK = (138, 128, 106)

def h(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0

def smooth(x, y, s, cell=6):
    gx, gy = x / cell, y / cell
    x0, y0 = int(gx), int(gy)
    fx, fy = gx - x0, gy - y0
    a, b = h(x0, y0, s), h(x0 + 1, y0, s)
    c, d = h(x0, y0 + 1, s), h(x0 + 1, y0 + 1, s)
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy

def paint_texture():
    t = TextureDrawer(512, 512)
    px = lambda x, y, c, a=255: t.set_pixel(x, y, c[0], c[1], c[2], a)
    add = lambda c, d: tuple(max(0, min(255, int(v + d))) for v in c)

    def paint_armor(cell, base_color, seam=16, mud=0.0, s=1):
        u0, v0 = cell
        for y in range(64):
            for x in range(64):
                val = (smooth(x, y, s) - 0.5) * 16 + (h(x, y, s + 9) - 0.5) * 6
                c = add(base_color, val)
                # Vertical rain streak grime
                streak = h(x, 0, s + 3)
                if streak > 0.78:
                    c = add(c, -16 * (1 - y / 64) * (streak - 0.78) * 5)
                # Paint chips / scratches on edges
                if h(x, y, s + 5) > 0.982:
                    c = add(c, 26)
                if seam and (x % seam == 0 or y % seam == 0):
                    c = add(c, -28)
                if mud:
                    m = smooth(x, y, s + 7, 4) + h(x, y, s + 8) * 0.3
                    if m > 1.0 - mud:
                        c = (90, 72, 48)
                px(u0 + x, v0 + y, c)

    paint_armor(HULL, BASE, seam=0, s=2)
    paint_armor(HULL2, BASE_DARK, seam=0, s=3)
    paint_armor(MUD, (82, 66, 46), seam=0, mud=0.5, s=4)
    paint_armor(MUDARMOR, BASE, seam=16, mud=0.35, s=5)
    paint_armor(APPLIQUE, add(BASE, -12), seam=0, s=6)

    # Weld seams
    paint_armor(WELD, BASE, seam=0, s=7)
    for i in range(64):
        for k in (16, 48):
            px(WELD[0] + i, WELD[1] + k, add(BASE, -22 + (i % 3) * 14))
            px(WELD[0] + k, WELD[1] + i, add(BASE, -22 + (i % 3) * 14))

    # Stencil unit marking
    paint_armor(STENCIL, BASE, s=8)
    t.draw_text(STENCIL[0] + 6, STENCIL[1] + 12, "01", (230, 226, 210), 1)

    # High-friction non-skid deck
    for y in range(64):
        for x in range(64):
            grit = (h(x, y, 11) > 0.5) * 16 + (x % 4 == 0 and y % 4 == 0) * 12
            px(DECK[0] + x, DECK[1] + y, add((95, 95, 90), grit - 8))
            px(STEEL[0] + x, STEEL[1] + y, add((62, 65, 68), (smooth(x, y, 12) - 0.5) * 14))
            px(BARS[0] + x, BARS[1] + y, add((40, 42, 45), (x == 0 or y == 0) * 16))
            px(GRILLE[0] + x, GRILLE[1] + y, (32, 34, 36) if y % 2 == 0 else add(BASE, -32))

            # Deep aggressive mud/rock lug tire tread
            tread = 58 if (y + (x // 4 % 2) * 2) % 4 < 2 else 26
            px(TYRE[0] + x, TYRE[1] + y, (tread, tread, tread - 2))
            px(RUBBER[0] + x, RUBBER[1] + y, add((38, 38, 36), (h(x, y, 15) - 0.5) * 8))

            # Glass with high-tech cyan ballistic anti-glare reflection
            gl_c = (28, 44, 56) if (x + y) % 6 == 0 else (18, 28, 38)
            t.set_pixel(GLASS[0] + x, GLASS[1] + y, gl_c[0], gl_c[1], gl_c[2], 220)

            # Lights & Optics
            px(LENS[0] + x, LENS[1] + y, (252, 248, 220) if (x + y) % 4 == 0 else (215, 215, 195))
            px(TAIL[0] + x, TAIL[1] + y, (210, 24, 24) if (x + y) % 4 == 0 else (145, 16, 16))
            px(AMBER[0] + x, AMBER[1] + y, (255, 168, 24))
            px(OPTIC[0] + x, OPTIC[1] + y, (0, 210, 245) if (x + y) % 5 == 0 else (15, 90, 140))
            px(WOOD[0] + x, WOOD[1] + y, add((132, 98, 62), (h(0, y, 16) - 0.5) * 20))
            px(STRAP[0] + x, STRAP[1] + y, add((240, 130, 20), ((x + y) % 3 == 0) * -20))
            px(JERRY[0] + x, JERRY[1] + y, add((105, 110, 78), (x % 6 == 0) * -16 + (x == 0 or y == 0) * 14))
            px(BRASS[0] + x, BRASS[1] + y, (180, 150, 75))
            px(GUN[0] + x, GUN[1] + y, add((38, 38, 40), (x == 0 or y == 0) * 20))

            # Beadlock 18px rim disc with ring of lug nuts
            d = math.hypot(x - 9, y - 9)
            rc = add(BASE, -18)
            if d < 2.8:
                rc = (45, 48, 52) # Dark central hub
            elif 5.2 < d < 6.8 and int(math.degrees(math.atan2(y - 9, x - 9)) + 360) % 45 < 14:
                rc = (235, 235, 225) # Silver 8-lug beadlock bolts
            elif d > 7.8:
                rc = add(BASE, -45) # Outer beadlock ring
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
    """12-sided dodecagonal wheel from 6 rotated strips + recessed beadlock rim disc."""
    a, w = 11.0, 7.5
    x0 = cx - w / 2
    # 6 strips rotated by 30 deg steps creates a smooth round tire
    cubes = [{"origin": [x0, cy - a, cz - a * math.tan(math.radians(15))],
              "size": [w, 2 * a, round(2 * a * math.tan(math.radians(15)), 3)],
              "pivot": [cx, cy, cz], "rotation": [k * 30, 0, 0], "uv": TYRE} for k in range(6)]
    ra = 6.8
    rx = x0 + w - 0.4 if left else x0 - 0.4
    cubes += [{"origin": [rx, cy - ra, cz - ra * 0.27],
               "size": [0.8, 2 * ra, round(2 * ra * 0.27, 3)],
               "pivot": [cx, cy, cz], "rotation": [k * 30, 0, 0], "uv": RIM} for k in range(6)]
    # Heavy axle hub + brass valve stem
    hx = x0 + w + 0.4 if left else x0 - 1.6
    cubes += [box([hx, cy - 2.5, cz - 2.5], [1.2, 5, 5], STEEL),
              box([hx + (0.4 if left else 0), cy - 0.8, cz - 0.8], [0.8, 1.6, 1.6], BRASS)]
    return cubes

def build_chassis_and_cab():
    c = []

    # 1. Heavy ladder frame chassis rails (z = -54 to +46)
    c += both(box([8, 8, -52], [3.5, 4.5, 96], STEEL))
    # Tubular crossmembers
    for z in (-44, -22, 4, 26, 42):
        c += [box([-8, 9, z], [16, 3, 2.5], STEEL)]
    # Front angled skid plate under engine & steering rack
    c += [rod((0, 7, -54), (0, 11, -28), 24, 2, STEEL)]

    # 2. Front Heavy Steel Bullbar & Winch Rig (z = -58 to -52)
    c += [box([-18, 9, -56], [36, 5, 3], BARS)]                      # Main heavy bumper beam
    c += both(rod((18, 9, -56), (18, 14, -51), 3, 3, BARS))           # Angled side brush guards
    c += [rod((0, 14, -55), (0, 17, -53), 28, 2.5, BARS)]             # Top bullbar loop
    c += both(box([10, 10, -55], [2, 6, 2], BARS))                    # Vertical center uprights
    # Heavy recovery winch spool & rollers
    c += [box([-6, 10, -54.5], [12, 4, 3.5], STEEL)]
    c += [box([-4, 11, -56.5], [8, 2, 2], STRAP)]                     # Fairlead & orange winch hook
    c += both(box([13, 8, -57], [2.5, 3.5, 2], AMBER))                # Forged D-ring clevises
    # Recessed bumper fog lights
    c += both(box([14, 10.5, -56.2], [2.5, 2.5, 0.4], LENS))

    # 3. Compound Hood & Nose (z = -52 to -22)
    # Lower radiator frame & grille
    c += [box([-16, 13, -52], [32, 9, 2], HULL2)]
    c += [box([-13, 14, -52.5], [26, 7, 1], GRILLE)]                  # Slotted black grille
    # Dual high-intensity projector headlights + amber indicators
    c += both(box([12.5, 15, -52.6], [3, 4, 0.5], LENS),
              box([12.5, 19.5, -52.6], [3, 1.8, 0.5], AMBER),
              box([12, 14.5, -52.8], [4, 7.2, 0.4], BARS))           # Stone guard wire mesh
    # Compound angled hood plate (slanted up towards windshield: y 21 -> 25, z -52 -> -22)
    c += [rod((0, 21, -52), (0, 25, -22), 31, 2, HULL)]
    # Center power bulge on hood
    c += [rod((0, 22.8, -48), (0, 26.2, -24), 16, 1.6, HULL2)]
    # Hood cooling louvers
    for lz in (-44, -38, -32):
        c += both(box([3, 24.5 + (lz + 52) * 4 / 30, lz], [4.5, 0.4, 2.5], GRILLE))

    # Front wheel arches with 45-degree chamfered flares (Front axle at z = -34)
    c += both(
        box([15.5, 13, -48], [3.5, 9, 10], HULL),                    # Front fender segment
        box([15.5, 13, -26], [3.5, 9, 8], HULL),                     # Rear fender segment
        rod((17, 21.5, -46), (17, 24, -34), 3, 2, HULL),              # Slanted front arch flare
        rod((17, 24, -34), (17, 21.5, -24), 3, 2, HULL),              # Slanted rear arch flare
        box([18.5, 20, -42], [1, 2, 18], RUBBER)                     # Rubber stone deflector lip
    )

    # 4. Elevated Off-Road Snorkel (Right A-pillar)
    c += [rod((-17.5, 16, -34), (-17.5, 34, -20), 2.2, 2.2, BARS)]    # Tilted snorkel riser tube
    c += [box([-18.8, 33.5, -22], [3.8, 3.5, 5], STEEL)]             # Heavy cyclone pre-cleaner box

    # 5. Armored Crew Cab (z = -22 to +8, y = 13..36)
    # Lower cab doors and sill (with rock sliders underneath)
    c += both(
        box([15.5, 13, -22], [2.5, 11, 30], HULL),
        box([17.5, 9.5, -20], [2, 2, 28], BARS),                      # Tubular steel rock slider step
        box([17.8, 17, -2], [1.2, 2, 4], STEEL)                       # Armored flush door handle
    )
    c += [box([-15.5, 13, -22], [31, 2, 30], DECK)]                   # Cab floor

    # Slanted A-pillars & Raked Windshield (28-degree slant: y 24 -> 35, z -22 -> -12)
    c += both(rod((16, 24, -22), (15, 35, -12), 2.5, 3, HULL))        # Left & Right A-Pillars
    c += [rod((0, 24, -22), (0, 35, -12), 28, 1.8, GLASS)]            # Raked Ballistic Windshield
    c += [rod((0, 24, -21.8), (0, 24.8, -21), 28.5, 1.5, HULL2)]      # Windshield cowl plate
    # Pantograph windshield wipers
    c += both(rod((6, 24.5, -21.5), (8, 32, -15), 0.6, 0.6, GUN))

    # Cab Roof (top y = 36) & B-Pillars
    c += [box([-15.5, 35, -12], [31, 2, 20], HULL)]                   # Roof plate
    c += both(rod((16.5, 34.5, -12), (16.5, 36, 8), 1.2, 20, HULL2))  # Roof side chamfer rails
    c += both(box([15.5, 24, 6], [2.5, 11, 2], HULL))                 # B-Pillar vertical posts
    # Side door ballistic windows
    c += both(box([16, 24, -12], [0.8, 10, 18], GLASS))
    # Rear cab wall & rear sliding window
    c += [box([-15.5, 15, 7], [31, 19, 1.5], HULL)]
    c += [box([-10, 25, 7.5], [20, 7, 0.6], GLASS)]

    # Roof-Mounted LED Light Bar & Tactical Whip Antenna
    c += [box([-14, 36.8, -13], [28, 2.4, 2.5], BARS)]                # Heavy aluminum casing
    c += [box([-13, 37.2, -13.5], [26, 1.6, 0.5], LENS)]              # High-output LED array
    c += [box([-16.5, 35, 6], [2, 3, 2], STEEL)]                      # Heavy spring antenna mount
    c += [rod((-15.5, 37, 7), (-14.5, 52, 10), 0.8, 0.8, STEEL)]      # Tilted high-gain tactical antenna

    # Detailed Cab Interior
    c += [box([-14, 18, -18], [28, 5, 8], GUN)]                       # Tactical dashboard
    c += [box([9, 21, -14], [5, 5, 1], STEEL)]                        # 3-spoke military steering wheel
    c += both(
        box([4, 15, -8], [9, 3.5, 10], STEEL),                        # Bucket seat cushion
        box([4, 18.5, 0], [9, 11, 2.5], STEEL),                       # High-back tactical seat
        box([6, 29.5, 0.5], [5, 3, 2], RUBBER)                        # Headrest
    )

    # 6. Tubular Steel Headache Rack / Roll-Cage (z = 8 to 18)
    c += both(
        rod((16, 14, 8.5), (16, 37, 8.5), 2.5, 2.5, BARS),            # Main vertical hoop legs
        rod((16, 36, 8.5), (16, 22, 24), 2.2, 2.2, BARS)              # Rearward diagonal kicker bars
    )
    c += [box([-16, 36, 7.5], [32, 2.5, 2.5], BARS)]                  # Top crossbar
    # Dual rear-facing LED scene work lights
    c += both(box([9, 35, 10], [3, 2.5, 2], BARS),
              box([9.5, 35.5, 11.8], [2, 1.5, 0.4], LENS))

    # 7. Rear Walkable Cargo Bed (z = 8 to +46, floor top y = 14)
    # Heavy diamond-plate bed floor: width 31 px (1.94b), length 38 px (2.38b)
    c += [box([-15.5, 13, 8], [31, 1.5, 38], DECK)]
    # Inner cargo bed walls with tie-down rail loops
    c += both(
        box([14.5, 14.5, 8], [2, 9, 38], HULL),                       # Inner bed side wall
        box([14, 23.5, 8], [3, 1.5, 38], BARS),                       # Top tubular cargo coaming rail
        box([17.5, 14, 10], [1.5, 8.5, 34], HULL2)                    # Outer stamped body panel
    )
    # Rear wheel arch flares (Rear axle at z = 25)
    c += both(
        rod((17, 21.5, 13), (17, 24, 25), 3, 2, HULL),                # Slanted front flare
        rod((17, 24, 25), (17, 21.5, 37), 3, 2, HULL),                # Slanted rear flare
        box([18.5, 20, 17], [1, 2, 18], RUBBER),                     # Rubber flare lip
        box([17.5, 6, 37.5], [2, 9, 0.5], RUBBER)                     # Rear mudflaps behind wheels
    )

    # 8. Rear Bumper & Military Blackout Light Clusters (z = 46..48)
    c += [box([-18, 9, 46], [36, 5, 2.5], BARS)]                      # Heavy rear steel bumper
    c += [box([-3, 8, 45], [6, 4, 3], STEEL)]                         # Class IV tow hitch receiver
    c += both(
        box([14, 16, 46.2], [2.8, 3.5, 0.5], TAIL),                  # Main brake/tail light
        box([14, 19.5, 46.2], [2.8, 2.2, 0.5], AMBER),                # Amber turn signal
        box([14, 13.5, 46.2], [2.8, 2.2, 0.5], LENS),                 # White reverse lamp
        box([13.5, 13, 46.5], [3.8, 9, 0.4], BARS)                   # Taillight protective cage
    )
    # Heavy twin exhaust tailpipe (curling out before rear right bumper)
    c += [rod((12, 8, 38), (14, 7, 44), 2.2, 2.2, GUN)]

    # Accessories mounted on bedside: Jerry cans & Recovery boards
    c += [box([-17.8, 16, 26], [2.2, 6, 14], APPLIQUE)]              # Dual waffle recovery traction boards
    c += [box([17.8, 15, 10], [2.8, 8, 5], JERRY),                   # Fuel jerrycan
          box([17.8, 21.5, 11], [2.5, 1.5, 3], JERRY),
          box([17.5, 18, 9.5], [3.2, 1.2, 6], STRAP)]

    return c

def build_tailgate():
    """Articulated drop tailgate with internal diamond-plate surface and heavy latch handles."""
    c = [
        box([-14.5, 14, 46], [29, 9, 2], HULL),                       # Outer stamped tailgate panel
        box([-13.5, 15, 45.5], [27, 7, 0.8], DECK),                   # Inner diamond plate walk-on face
        box([-14, 21.5, 47.5], [28, 1.2, 1.2], BARS),                 # Top edge reinforcement tube
        box([-4, 18.5, 48], [8, 2.5, 1], STEEL)                       # Center heavy latch handle
    ]
    return c

def build_full_model():
    bones = []
    root = {"name": "root", "pivot": [0, 0, 0], "cubes": []}
    bones.append(root)

    # Main Body
    body_cubes = build_chassis_and_cab()
    bones.append({"name": "body", "parent": "root", "pivot": [0, 11, 0], "cubes": body_cubes})

    # Articulated Rear Tailgate (Pivot at bottom hinge: y = 14, z = 46)
    # 0 deg = closed vertical; +90 deg rotX = drops level to ground as a walk-on ramp
    tailgate_cubes = build_tailgate()
    bones.append({"name": "rear_tailgate", "parent": "body", "pivot": [0, 14, 46], "cubes": tailgate_cubes})

    # Dynamic Cargo Straps (ratchet tiedown over cargo bed)
    straps = [
        box([-13.5, 15.5, 16], [27, 1.2, 2.5], STRAP),
        box([-13.5, 15.5, 32], [27, 1.2, 2.5], STRAP),
        box([-14.2, 15, 15], [1.5, 3, 4], STEEL),                     # Ratchet buckle left
        box([12.7, 15, 15], [1.5, 3, 4], STEEL)                      # Ratchet buckle right
    ]
    bones.append({"name": "cargo_straps", "parent": "body", "pivot": [0, 14, 24], "cubes": straps})

    # Steering Knuckles and 12-sided wheels (Front axle z = -34, Rear axle z = 25; track width center +-18.5)
    # Front Left
    bones.append({"name": "steer_fl", "parent": "body", "pivot": [18.5, 11, -34], "cubes": []})
    bones.append({"name": "wheel_fl", "parent": "steer_fl", "pivot": [18.5, 11, -34], "cubes": make_dodec_wheel(18.5, 11, -34, left=True)})
    # Front Right
    bones.append({"name": "steer_fr", "parent": "body", "pivot": [-18.5, 11, -34], "cubes": []})
    bones.append({"name": "wheel_fr", "parent": "steer_fr", "pivot": [-18.5, 11, -34], "cubes": make_dodec_wheel(-18.5, 11, -34, left=False)})
    # Rear Left
    bones.append({"name": "wheel_rl", "parent": "body", "pivot": [18.5, 11, 25], "cubes": make_dodec_wheel(18.5, 11, 25, left=True)})
    # Rear Right
    bones.append({"name": "wheel_rr", "parent": "body", "pivot": [-18.5, 11, 25], "cubes": make_dodec_wheel(-18.5, 11, 25, left=False)})

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

                # UV bounds for this face
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
    print("Building High-Detail Tactical Technical 4x4...")
    tex = paint_texture()
    bones = build_full_model()

    brain_dir = os.path.abspath("C:/Users/Purachai/.gemini/antigravity/brain/d0082229-568a-4374-9437-f2414c618d6a")
    out_img = os.path.join(brain_dir, "tactical_technical_5view.png")

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

    print("Rendering View 5: True Side Profile (Ground Clearance & Rake)...")
    p5 = render_view(bones, tex, (W, H_panel), yaw=90, pitch=0, pose={}, scale=scale * 0.95, offset_y=0.55)

    print("Stitching 5-view sheet...")
    stitched_bytes, total_w, total_h = stitch_vertical([p1, p2, p3, p4, p5], W, H_panel)
    png_data = make_png(total_w, total_h, stitched_bytes)

    with open(out_img, "wb") as f:
        f.write(png_data)

    print(f"SUCCESS: Rendered high-detail 5-view sheet to {out_img}")

if __name__ == "__main__":
    main()
