#!/usr/bin/env python3
"""Mil Mi-17 "Hip" Tactical Transport Helicopter (Tier 2/3 Insurgent / Militia Gunship)
Designed using the 5 GeckoLib Model Architect & Realism Skills:
- Cylindrical aerodynamic fuselage with multi-pane blister cockpit canopy.
- 5-blade main rotor assembly (dia 20 blocks) and 3-blade tail rotor on tail boom.
- Twin overhead turboshaft engine nacelles with forward particle separators & oval exhausts.
- Walkable interior cargo hold (fits 6-8 standing players with weapons).
- Articulated rear clamshell cargo doors (splits open for troop & light vehicle loading).
- Ventral heavy cargo sling hook for dropping mechs & heavy crates mid-air.
- Side weapon outrigger pylons with dual UB-32 unguided rocket pods.
- Heavy tricycle landing gear with 12-sided dodecagonal tires.
- Weathered irregular militia camouflage with soot stains, grime, and stencils.
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

# Insurgent / Soviet Militia Scheme: Weathered Khaki-Green & Grey-Blue Belly
BASE = (112, 120, 88)
BELLY_BLUE = (120, 138, 148)

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

    def paint_armor(cell, base_color, seam=16, s=1):
        u0, v0 = cell
        for y in range(64):
            for x in range(64):
                val = (smooth(x, y, s) - 0.5) * 16 + (hash_noise(x, y, s + 9) - 0.5) * 6
                c = add(base_color, val)
                streak = hash_noise(x, 0, s + 3)
                if streak > 0.78:
                    c = add(c, -18 * (1 - y / 64) * (streak - 0.78) * 5)
                if hash_noise(x, y, s + 5) > 0.982:
                    c = add(c, 30) # Paint chips
                if seam and (x % seam == 0 or y % seam == 0):
                    c = add(c, -28) # Panel rivets
                px(u0 + x, v0 + y, c)

    paint_armor(HULL, BASE, seam=16, s=2)
    paint_armor(HULL2, BELLY_BLUE, seam=16, s=3)
    paint_armor(APPLIQUE, (98, 106, 76), seam=0, s=4)
    paint_armor(WELD, BASE, seam=0, s=5)

    # Stencil tail number
    paint_armor(STENCIL, BASE, s=8)
    t.draw_text(STENCIL[0] + 6, STENCIL[1] + 12, "17", (230, 225, 200), 1)

    for y in range(64):
        for x in range(64):
            # Cargo deck floor non-skid
            grit = (hash_noise(x, y, 11) > 0.5) * 16 + (x % 4 == 0 and y % 4 == 0) * 10
            px(DECK[0] + x, DECK[1] + y, add((78, 82, 85), grit - 8))
            px(STEEL[0] + x, STEEL[1] + y, add((52, 55, 58), (smooth(x, y, 12) - 0.5) * 14))
            px(BARS[0] + x, BARS[1] + y, add((32, 34, 36), (x == 0 or y == 0) * 16))
            # Exhaust soot on turboshaft cowlings
            soot = (hash_noise(x, y, 13) - 0.5) * 10
            px(GRILLE[0] + x, GRILLE[1] + y, add((40, 40, 42), soot))

            # Rotor blades and tyres
            tread = 50 if y % 6 < 3 else 28
            px(TYRE[0] + x, TYRE[1] + y, (tread, tread, tread))
            px(RUBBER[0] + x, RUBBER[1] + y, add((34, 34, 32), (hash_noise(x, y, 15) - 0.5) * 8))

            # Helicopter blister cockpit glass (green/cyan high-altitude anti-glare)
            gl_c = (22, 42, 48) if (x + y) % 5 == 0 else (14, 28, 34)
            t.set_pixel(GLASS[0] + x, GLASS[1] + y, gl_c[0], gl_c[1], gl_c[2], 215)

            # Navigation lights & weapons
            px(LENS[0] + x, LENS[1] + y, (252, 248, 220) if (x + y) % 4 == 0 else (210, 210, 190))
            px(TAIL[0] + x, TAIL[1] + y, (220, 20, 20) if (x + y) % 4 == 0 else (150, 14, 14)) # Red beacon
            px(AMBER[0] + x, AMBER[1] + y, (255, 160, 20))
            px(OPTIC[0] + x, OPTIC[1] + y, (0, 220, 255) if (x + y) % 5 == 0 else (10, 100, 150))
            px(GUN[0] + x, GUN[1] + y, add((38, 40, 42), (x == 0 or y == 0) * 20))
            px(BRASS[0] + x, BRASS[1] + y, (180, 150, 70))
            px(STRAP[0] + x, STRAP[1] + y, add((240, 130, 20), ((x + y) % 3 == 0) * -20))

            # Helicopter wheel rim
            d = math.hypot(x - 9, y - 9)
            rc = add(BELLY_BLUE, -15)
            if d < 2.8: rc = (38, 40, 42)
            elif 5.0 < d < 6.6 and int(math.degrees(math.atan2(y - 9, x - 9)) + 360) % 60 < 15: rc = (220, 220, 210)
            elif d > 7.5: rc = add(BELLY_BLUE, -35)
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

def make_dodec_wheel(cx, cy, cz, left, r=7.0, w=5.0):
    a = r
    x0 = cx - w / 2
    cubes = [{"origin": [x0, cy - a, cz - a * math.tan(math.radians(15))],
              "size": [w, 2 * a, round(2 * a * math.tan(math.radians(15)), 3)],
              "pivot": [cx, cy, cz], "rotation": [k * 30, 0, 0], "uv": TYRE} for k in range(6)]
    ra = r * 0.65
    rx = x0 + w - 0.4 if left else x0 - 0.4
    cubes += [{"origin": [rx, cy - ra, cz - ra * 0.27],
               "size": [0.8, 2 * ra, round(2 * ra * 0.27, 3)],
               "pivot": [cx, cy, cz], "rotation": [k * 30, 0, 0], "uv": RIM} for k in range(6)]
    hx = x0 + w + 0.3 if left else x0 - 1.2
    cubes += [box([hx, cy - 1.8, cz - 1.8], [1.0, 3.6, 3.6], STEEL)]
    return cubes

def build_fuselage():
    c = []

    # 1. Main Fuselage Shell (z: -70 to +45, width: 38 units, height: 32 units)
    # Floor sits at y = 10, Ceiling at y = 38 (clear height = 28 units = 1.75 blocks)
    c += [box([-16, 8, -70], [32, 2, 115], HULL2)]                     # Belly keel plate
    c += [box([-15, 10, -70], [30, 1.5, 115], DECK)]                   # Walkable cabin floor

    # Lower belly contour & sponsons (slanted inwards)
    c += both(
        box([16, 9, -68], [2.5, 4, 112], HULL2),                       # Sponson undercut
        box([17.5, 13, -70], [1.8, 22, 115], HULL),                    # Lower side walls
        box([16, 35, -70], [2.5, 3.5, 115], HULL)                      # Roof curve transition
    )
    # Fuselage Ceiling & Roof
    c += [box([-16, 37, -70], [32, 2, 115], HULL)]

    # 2. Rounded Blister Nose & Cockpit (z: -105 to -70)
    # Multi-step aerodynamic nose taper
    c += [
        box([-15, 10, -82], [30, 18, 12], HULL2),                      # Forward flight deck
        rod((0, 10, -100), (0, 16, -82), 26, 2, HULL2),                # Slanted chin plate
        box([-13, 15, -102], [26, 8, 20], HULL2),                      # Nose radome box
        rod((0, 23, -102), (0, 36, -82), 26, 2, GLASS),                # Forward windshield
        rod((0, 30, -104), (0, 36, -82), 24, 1.5, GLASS)               # Upper greenhouse glass
    ]
    # Cockpit A-pillars and blister side windows
    c += both(
        rod((14, 21, -82), (12, 36, -72), 2.5, 2.5, HULL),
        box([14, 22, -80], [0.8, 14, 10], GLASS),                      # Cockpit side window
        box([12, 16, -92], [2.5, 10, 10], HULL2)                       # Nose cheek panel
    )
    # Pilot & Co-Pilot Cockpit Seats (inside at z = -76)
    c += both(
        box([4, 11.5, -78], [7.5, 2.5, 8], STEEL),                     # Seat cushion
        box([4, 14, -71], [7.5, 12, 1.8], STEEL),                      # Seat backrest
        box([2, 16, -81], [11, 4, 3], GUN),                           # Instrument console
        box([6, 17, -77], [3.5, 3.5, 1], STEEL)                        # Cyclic stick
    )

    # 3. Overhead Twin Turboshaft Engine Cowling & Intakes (y: 38..50, z: -68 to +10)
    # Twin engine doghouse hump
    c += [box([-14, 39, -65], [28, 9, 75], HULL)]
    # Dual front circular air intakes with particle separator domes
    c += both(
        box([4.5, 40, -68], [8, 8, 4], HULL2),                         # Nacelle cowl
        box([5.5, 41, -69], [6, 6, 1.5], GRILLE),                      # Mesh intake face
        box([7.5, 43, -70.5], [2, 2, 2], STEEL)                        # Intake bullet spinner
    )
    # Twin angled oval exhaust pipes (venting outward & aft at z = -15)
    c += both(
        rod((9, 44, -18), (14, 46, -10), 5, 5, GRILLE),                # Angled exhaust duct
        box([12, 43.5, -9], [5, 5, 1.5], STEEL)                        # Exhaust lip
    )
    # APU exhaust port on left side
    c += [box([14.2, 45, -2], [1.5, 2.5, 4], GRILLE)]

    # 4. Long Tapered Tail Boom (z: +45 to +170, length 125 units = ~7.8 blocks)
    # Main circular/box boom
    c += [
        rod((0, 30, 45), (0, 36, 170), 14, 12, HULL),                  # Main tubular boom
        rod((0, 22, 45), (0, 30, 170), 12, 4, HULL2)                   # Lower boom taper
    ]
    # Tail rotor driveshaft housing on top of boom
    c += [rod((0, 36.5, 45), (0, 42.5, 170), 2.5, 2.5, HULL)]

    # Vertical Tail Fin & Stabilizer (z: 165 to 185, y: 34 to 68)
    c += [
        rod((0, 36, 168), (0, 68, 182), 3.5, 18, HULL),                # Swept vertical fin
        box([-1.5, 66, 178], [3, 4, 8], HULL),                         # Tail fin cap
        box([-1.8, 68, 182], [3.6, 2, 2], TAIL)                        # Red anti-collision beacon
    ]
    # Horizontal Tail Stabilizers (swept wings at boom end)
    c += both(
        rod((3, 37, 160), (20, 37, 164), 6, 1.5, HULL),               # Stabilizer wing
        box([19.5, 36, 161], [1, 2.5, 6], HULL)                        # Endplate fin
    )

    # 5. Weapon Outrigger Pylons & Rocket Pods (Insurgent Gunship Option)
    c += both(
        # Tubular truss pylon structure
        rod((16, 24, -20), (32, 20, -18), 2.5, 2.5, STEEL),
        rod((16, 15, -20), (32, 19, -18), 2.0, 2.0, STEEL),
        box([30, 18, -26], [4, 4, 16], STEEL),                         # Stores rack beam
        # UB-32 57mm unguided rocket pod (cylindrical launcher)
        box([28.5, 12, -34], [7, 7, 24], GUN),                         # Rocket pod cylinder
        box([29.0, 12.5, -35], [6, 6, 1.2], BARS),                     # 32-tube front face
        box([30.5, 14.0, -35.5], [3, 3, 0.8], LENS)                    # Nose cone
    )

    # 6. Ventral Heavy Cargo Sling Rig (Under belly at center-of-gravity: z = -10, y = 6..8)
    c += [
        box([-4, 6.5, -14], [8, 1.5, 8], STEEL),                       # Ventral winch hatch
        box([-2.5, 4.5, -12], [5, 2.2, 4], STEEL),                      # Heavy cable spool
        box([-1.5, 2.5, -11], [3, 2.0, 2], BRASS)                       # Forged magnetic cargo hook
    ]

    # 7. Heavy Tricycle Landing Gear (Tough shock struts, ground at y = 0)
    # Nose Gear (Twin wheels under cockpit at z = -84)
    c += [
        rod((0, 11, -84), (0, 5, -84), 3, 3, STEEL),                    # Nose oleo strut
        box([-3.5, 4, -86], [7, 2, 4], STEEL)                          # Nose axle
    ]
    c += make_dodec_wheel(3.5, 4, -84, left=True, r=4.0, w=3.0)
    c += make_dodec_wheel(-3.5, 4, -84, left=False, r=4.0, w=3.0)

    # Main Gear (Port & Starboard sponson struts at z = -10, track width +-22)
    c += both(
        rod((16, 13, -10), (22, 5, -10), 3.5, 3.5, STEEL),              # Main shock strut
        rod((16, 26, -10), (22, 6, -10), 2.5, 2.5, STEEL),              # Diagonal brace
        box([20, 4, -12], [4, 2, 4], STEEL)                            # Hub carrier
    )
    c += make_dodec_wheel(22, 5, -10, left=True, r=5.0, w=3.5)
    c += make_dodec_wheel(-22, 5, -10, left=False, r=5.0, w=3.5)

    return c

def build_clamshell_doors():
    """Rear clamshell cargo doors (pivot left and right like true Mi-8/Mi-17)."""
    # Left door (hinge at x = 16, z = 45)
    left_door = [
        box([0.5, 10, 45], [15.5, 26, 8], HULL),
        box([0.5, 8, 45], [15.5, 2, 8], HULL2),
        box([0.5, 18, 53], [4, 8, 1], STEEL)                           # Latch locks
    ]
    # Right door (hinge at x = -16, z = 45)
    right_door = [
        box([-16, 10, 45], [15.5, 26, 8], HULL),
        box([-16, 8, 45], [15.5, 2, 8], HULL2),
        box([-4.5, 18, 53], [4, 8, 1], STEEL)
    ]
    return left_door, right_door

def build_rotors():
    """5-blade main rotor (dia 320 units = 20 blocks) and 3-blade tail rotor."""
    main_cubes = []
    # Rotor hub & swashplate (pivot at x=0, y=50, z=-30)
    main_cubes += [
        box([-4, 48, -34], [8, 5, 8], STEEL),
        box([-2.5, 53, -32.5], [5, 4, 5], STEEL)
    ]
    # 5 blades (length 140 units each = 8.75 blocks radius)
    for i in range(5):
        ang = i * 72.0
        r_rad = math.radians(ang)
        # Root cuff
        bx_c = math.sin(r_rad) * 12
        bz_c = -math.cos(r_rad) * 12
        main_cubes.append({"origin": [-2, 54, -3], "size": [4, 1.2, 135],
                           "pivot": [0, 54, -30], "rotation": [0, -ang, 0], "uv": GUN})
        # Yellow blade tip warning stripe
        main_cubes.append({"origin": [-2, 54, 132], "size": [4, 1.2, 10],
                           "pivot": [0, 54, -30], "rotation": [0, -ang, 0], "uv": AMBER})

    # Tail rotor (3 blades, pivot at x=3, y=66, z=182)
    tail_cubes = [
        box([2, 64.5, 180.5], [3, 3, 3], STEEL)
    ]
    for k in range(3):
        ang = k * 120.0
        tail_cubes.append({"origin": [2.5, 65.5, -1], "size": [1.0, 32, 2.5],
                           "pivot": [3, 66, 182], "rotation": [ang, 0, 0], "uv": GUN})

    return main_cubes, tail_cubes

def build_full_helicopter():
    bones = []
    root = {"name": "root", "pivot": [0, 0, 0], "cubes": []}
    bones.append(root)

    fuselage = build_fuselage()
    bones.append({"name": "fuselage", "parent": "root", "pivot": [0, 24, -10], "cubes": fuselage})

    # Clamshell Rear Cargo Doors
    left_door, right_door = build_clamshell_doors()
    bones.append({"name": "door_left", "parent": "fuselage", "pivot": [16, 20, 45], "cubes": left_door})
    bones.append({"name": "door_right", "parent": "fuselage", "pivot": [-16, 20, 45], "cubes": right_door})

    # Rotors
    main_rotors, tail_rotors = build_rotors()
    bones.append({"name": "main_rotor", "parent": "fuselage", "pivot": [0, 54, -30], "cubes": main_rotors})
    bones.append({"name": "tail_rotor", "parent": "fuselage", "pivot": [3, 66, 182], "cubes": tail_rotors})

    return bones

def rot(p, piv, r):
    x, y, z = p[0] - piv[0], p[1] - piv[1], p[2] - piv[2]
    ax, ay, az = math.radians(-r[0]), math.radians(r[1]), math.radians(-r[2])
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    return (x + piv[0], y + piv[1], z + piv[2])

def render_view(bones, tex_drawer, out_wh, yaw, pitch, pose=None, scale=2.8, offset_y=0.55):
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
    print("Designing Mil Mi-17 'Hip' Insurgent Transport Helicopter...")
    tex = paint_texture()
    bones = build_full_helicopter()

    brain_dir = os.path.abspath("C:/Users/Purachai/.gemini/antigravity/brain/d0082229-568a-4374-9437-f2414c618d6a")
    out_img = os.path.join(brain_dir, "mi17_helicopter_5view.png")

    W, H_panel = 720, 360
    scale = 2.4

    # Pose with clamshell rear doors swung open
    doors_open = {
        "door_left": [0, -65, 0],
        "door_right": [0, 65, 0]
    }

    print("Rendering View 1: 3/4 Front Isometric (Closed)...")
    p1 = render_view(bones, tex, (W, H_panel), yaw=35, pitch=-20, pose={}, scale=scale, offset_y=0.55)

    print("Rendering View 2: 3/4 Rear Isometric (Closed)...")
    p2 = render_view(bones, tex, (W, H_panel), yaw=215, pitch=-18, pose={}, scale=scale, offset_y=0.55)

    print("Rendering View 3: Direct Rear (Clamshell Doors Open 65°)...")
    p3 = render_view(bones, tex, (W, H_panel), yaw=180, pitch=-8, pose=doors_open, scale=scale * 1.3, offset_y=0.60)

    print("Rendering View 4: 3/4 Rear Isometric (Clamshell Doors Open)...")
    p4 = render_view(bones, tex, (W, H_panel), yaw=220, pitch=-22, pose=doors_open, scale=scale, offset_y=0.55)

    print("Rendering View 5: True Side Profile (Aerodynamic Fuselage & Rotors)...")
    p5 = render_view(bones, tex, (W, H_panel), yaw=90, pitch=0, pose={}, scale=scale * 0.95, offset_y=0.50)

    print("Stitching 5-view sheet...")
    stitched_bytes, total_w, total_h = stitch_vertical([p1, p2, p3, p4, p5], W, H_panel)
    png_data = make_png(total_w, total_h, stitched_bytes)

    with open(out_img, "wb") as f:
        f.write(png_data)

    print(f"SUCCESS: Rendered Mil Mi-17 5-View Concept Sheet to:\n{out_img}")

if __name__ == "__main__":
    main()
