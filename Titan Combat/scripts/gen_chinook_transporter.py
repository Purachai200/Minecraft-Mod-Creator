#!/usr/bin/env python3
"""CH-47 Chinook tandem-rotor transporter: geo, animation, entity texture and item icon.

Model convention matches the other transport models: nose at -Z (Java maps vehicle-forward +Z offset onto it),
+X = port/left, Y = 0 is the ground. Pilot cushion sits at model (7, 14, -64) to match PILOT_OFFSET.
Every cube names a material; each face gets that material's own atlas rectangle (per-face UV, 1 texel per unit,
cropped to the rectangle), so panel lines and rivets never smear across unrelated regions.
Run from the project root:  python3 scripts/gen_chinook_transporter.py
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_transport_assets import TextureDrawer, rod  # noqa: E402

ASSETS = "src/main/resources/assets/titancombat"
TEX = 512

# material -> atlas rect (u, v, w, h)
MAT = {
    "hull":    (0, 0, 128, 128),     # light olive-grey skin, panel lines, rivets
    "upper":   (128, 0, 128, 128),   # roof / pylon skin, more weathered, walkway marks
    "belly":   (256, 0, 128, 128),   # underside, oil streaks
    "nacelle": (384, 0, 128, 128),   # engine cowl, louvres, exhaust soot
    "glass":   (0, 128, 64, 64),     # see-through windscreen (alpha 0 with frame)
    "tint":    (64, 128, 32, 32),    # opaque chin / porthole glass
    "port":    (96, 128, 8, 8),      # round porthole
    "dark":    (104, 128, 24, 24),   # intakes, cockpit interior, rubber
    "metal":   (128, 128, 32, 32),   # bare steel, masts, hubs
    "exhaust": (160, 128, 32, 32),   # sooted exhaust can
    "tire":    (192, 128, 32, 32),
    "rim":     (224, 128, 16, 16),
    "blade":   (240, 128, 8, 128),   # rotor blade, long axis down the atlas
    "seat":    (64, 160, 32, 32),
    "door":    (128, 160, 32, 64),   # crew door with outline + handle
    "star":    (160, 160, 32, 32),   # low-vis national star
    "number":  (192, 160, 48, 16),   # tail number stencil
    "red":     (248, 128, 4, 4),
    "green":   (252, 128, 4, 4),
    "white":   (248, 132, 4, 4),
    "yellow":  (252, 132, 4, 4),
    "walk":    (192, 176, 32, 32),   # anti-slip walkway
    "ramp":    (256, 128, 64, 64),   # ramp, with hinge + tread
}

BASE = (166, 168, 146)      # light olive-grey: stays readable under the faction tint multiply


# ---------------------------------------------------------------------------- geometry helpers
def box(x0, y0, z0, x1, y1, z1, mat, **kw):
    lo, hi = [min(a, b) for a, b in ((x0, x1), (y0, y1), (z0, z1))], [max(a, b) for a, b in ((x0, x1), (y0, y1), (z0, z1))]
    c = {"origin": [round(v, 3) for v in lo], "size": [round(hi[i] - lo[i], 3) for i in range(3)], "mat": mat}
    c.update(kw)
    return c


def mirror(c):
    """Copy of a cube reflected across X = 0 (rotation about Y/Z flips sign)."""
    m = json.loads(json.dumps(c))
    m["origin"][0] = round(-(c["origin"][0] + c["size"][0]), 3)
    if "pivot" in m:
        m["pivot"][0] = -m["pivot"][0]
        m["rotation"] = [m["rotation"][0], -m["rotation"][1], -m["rotation"][2]]
    return m


def both(*cubes):
    out = []
    for c in cubes:
        out += [c, mirror(c)]
    return out


def tilted(base, top, w, t, mat):
    c = rod(base, top, w, t, [0, 0])
    c["mat"] = mat
    del c["uv"]
    return c


def wheel(cx, cy, cz, x0, width, r):
    """Tyre as three slabs turned 0/30/-30 deg about the axle (reads round), rim disc and hub cap outboard."""
    out = [box(x0, cy - r, cz - r, x0 + width, cy + r, cz + r, "tire", pivot=[cx, cy, cz], rotation=[a, 0, 0])
           for a in (0, 30, -30)]
    rx = x0 + width if cx > 0 else x0 - 0.4
    out += [box(rx, cy - r * 0.6, cz - r * 0.6, rx + 0.4, cy + r * 0.6, cz + r * 0.6, "rim",
                pivot=[cx, cy, cz], rotation=[a, 0, 0]) for a in (0, 45)]
    hx = rx + 0.4 if cx > 0 else rx - 0.6
    out.append(box(hx, cy - 1, cz - 1, hx + 0.6, cy + 1, cz + 1, "metal"))
    return out


# ---------------------------------------------------------------------------- the airframe
def fuselage_cubes():
    C = []
    # main cabin: core box + side bulges + roof crown = rounded-rectangle cross-section
    C += [box(-16, 10, -62, 16, 38, 48, "hull"),
          box(-14, 38, -62, 14, 39, 48, "upper"),
          box(-15, 9.4, -60, 15, 10, 46, "belly")]
    C += both(box(16, 12, -62, 18, 36, 48, "hull"), box(16, 11, -60, 17, 12, 46, "belly"),
              box(16, 36, -62, 17, 37, 48, "upper"))
    # aft fuselage above the ramp, tapering into the tail
    C += [box(-16, 24, 48, 16, 38, 62, "hull"), box(-14, 26, 62, 14, 37, 66, "hull"),
          box(-11, 28, 66, 11, 35, 68, "hull"), box(-14, 38, 48, 14, 39, 60, "upper")]
    C += both(box(16, 13, 48, 18, 36, 56, "hull"), box(16, 18, 56, 18, 36, 62, "hull"),
              box(14, 22, 62, 15.5, 34, 65, "hull"))
    # cockpit: floor, low side walls, instrument console, roof, glass
    C += [box(-16, 10, -78, 16, 13, -62, "belly"), box(-15, 13, -78, 15, 20, -75, "hull"),
          box(-14, 16, -75, 14, 20, -72, "dark"), box(-14, 20, -76, 14, 21, -72, "dark"),
          box(-2, 13, -72, 2, 17, -62, "dark"),
          box(-16, 33, -74, 16, 36, -62, "upper"), box(-15, 32, -75, 15, 34, -73, "upper")]
    C += both(box(15, 13, -78, 16.4, 20, -62, "hull"),
              box(15, 20, -78, 16.4, 21, -76.6, "hull"), box(15, 20, -70.6, 16.4, 33, -69.6, "hull"),
              box(15, 20, -63, 16.4, 33, -62, "hull"), box(15.4, 32, -77, 16.2, 33.4, -62, "hull"),
              box(15.6, 21, -76.6, 16.0, 32, -70.6, "glass"), box(15.6, 21, -69.6, 16.0, 32, -63, "glass"))
    # sloped split windscreen + centre post (alpha-0 glass: pilot looks straight through)
    C += [tilted((-7.5, 20, -76.6), (-7.5, 32.5, -73.4), 14, 0.5, "glass"),
          tilted((7.5, 20, -76.6), (7.5, 32.5, -73.4), 14, 0.5, "glass"),
          tilted((0, 20, -76.9), (0, 32.8, -73.6), 1.2, 1.0, "hull")]
    C += both(tilted((14.6, 20, -76.9), (14.6, 32.8, -73.6), 1.2, 1.0, "hull"))
    # seats: pilot (port, +X) and co-pilot
    C += both(box(3, 13, -68, 11, 16, -60, "seat"), box(3, 16, -60, 11, 28, -58, "seat"),
              box(3, 16, -68, 4, 19, -61, "seat"))
    # blunt nose with chin windows and radome
    C += [box(-15, 11, -82, 15, 20, -78, "hull"), box(-13, 20, -80, 13, 21, -78, "hull"),
          box(-6, 12, -86, 6, 19, -82, "belly"), box(-4, 13, -88, 4, 18, -86, "belly")]
    C += both(box(6.5, 12, -82.4, 13.5, 19, -82, "tint"), box(14.8, 12, -81, 15.2, 18, -77, "tint"),
              tilted((6, 20.6, -80), (6, 21.4, -86), 0.5, 0.5, "metal"))  # pitot tubes
    # forward rotor pylon / transmission fairing
    C += [box(-10, 36, -70, 10, 40, -38, "upper"), box(-8, 40, -66, 8, 44, -42, "upper"),
          box(-6, 44, -62, 6, 47, -46, "upper"), box(-9, 35, -72, 9, 38, -70, "upper"),
          box(-3, 44, -66, 3, 46, -64, "dark")]                        # oil-cooler inlet
    # dorsal tunnel with walkway
    C += [box(-5, 39, -38, 5, 42, 26, "upper"), box(-3, 42, -36, 3, 42.2, 22, "walk")]
    # aft pylon (tall rear rotor tower)
    C += [box(-11, 38, 20, 11, 44, 64, "upper"), box(-9, 44, 26, 9, 52, 62, "upper"),
          box(-7, 52, 32, 7, 57, 60, "upper"), box(-6, 57, 36, 6, 59, 56, "upper"),
          box(-8, 41, 63, 8, 50, 66, "upper"), box(-3, 50, 28, 3, 52, 30, "dark")]
    C += both(box(9.0, 44, 38, 9.2, 50, 52, "number"))
    # twin turboshaft nacelles on stub pylons either side of the aft pylon
    C += both(box(10, 39, 34, 18, 44, 48, "upper"),
              box(17, 39, 22, 26, 48, 54, "nacelle"), box(18, 38.4, 24, 25, 39, 52, "nacelle"),
              box(18, 48, 24, 25, 48.6, 52, "nacelle"),
              box(17.6, 39.6, 21, 25.4, 47.4, 22, "dark"), box(20, 42, 20, 23, 45, 21, "metal"),
              box(18, 40, 54, 25, 47, 58, "exhaust"), box(19, 41, 58, 24, 46, 59, "dark"))
    # side sponsons = fuel pods, with rounded caps
    C += both(box(18, 10, -44, 25, 22, 30, "hull"), box(18, 22, -42, 23.5, 24, 28, "upper"),
              box(18, 11, -48, 23, 20, -44, "hull"), box(18, 12, -50, 21, 18, -48, "hull"),
              box(18, 11, 30, 23, 20, 34, "hull"), box(18, 12, 34, 21, 18, 36, "hull"),
              box(25, 11, -40, 25.6, 21, 26, "hull"),                               # rub strake
              box(21, 24, -12, 22.4, 24.6, -9, "metal"),                            # fuel filler
              box(25.6, 12, -10, 25.8, 20, -2, "star"),
              box(25.6, 19, -47, 26, 20, -46, "red"))
    # portholes (round, protruding rim) along both cabin sides
    for z in (-56, -42, -28, -14, 0, 14, 28, 40):
        C += both(box(18, 26, z - 2, 18.4, 30, z + 2, "port"))
    # crew door (starboard front) and boarding steps
    C += [box(-18.3, 13, -61, -18, 34, -53, "door"), box(-20, 11, -60, -18, 11.6, -54, "dark"),
          box(-15, 9, -60, -11, 9.4, -54, "dark")]
    # nav / anti-collision lights, antennas
    C += [box(-26, 19, -47, -25.6, 20, -46, "green"), box(-1, 59, 44, 1, 60.4, 46, "red"),
          box(-1, 8.4, -10, 1, 9.4, -8, "red"), box(-1, 33, 67, 1, 35, 68.4, "white"),
          box(-0.3, 39, -22, 0.3, 44, -16, "dark"), box(-0.3, 5, 20, 0.3, 9.4, 24, "dark"),
          box(-0.3, 42, 4, 0.3, 46, 7, "dark")]
    # belly cargo hooks: centre (main sling) + fore/aft
    C += [box(-2, 6, -2, 2, 9.4, 2, "dark"), box(-1, 4.4, -1.5, 1, 6, 1.5, "metal"),
          box(-1.2, 7.4, -26, 1.2, 9.4, -22, "dark"), box(-1.2, 7.4, 22, 1.2, 9.4, 26, "dark")]
    # air-to-air refuelling probe on the starboard nose
    C += [tilted((-17, 25, -62), (-17, 23.5, -98), 1.6, 1.6, "metal"),
          box(-18, 23, -66, -16, 26, -60, "hull"), box(-17.6, 22.9, -99, -16.4, 24.1, -97.6, "dark")]
    return C


def ramp_cubes():
    # closed rear loading ramp, hinged at the cabin floor, sloping up into the tail
    return [tilted((0, 10, 48), (0, 24.6, 66), 32, 2, "ramp")] + both(
        tilted((15.5, 11, 48), (15.5, 24.6, 64.8), 1.4, 3, "hull"))


def gear(side, front):
    s = 1 if side > 0 else -1
    z = -40 if front else 30
    out = [tilted((s * 21.5, 10, z), (s * 21.5, 5, z), 1.6, 1.6, "metal"),
           box(s * 19, 9.4, z - 2, s * 24, 11, z + 2, "dark")]
    if front:   # twin wheels
        out += wheel(s * 22, 5, z, 19.2 if s > 0 else -21.8, 2.6, 4.6)
        out += wheel(s * 22, 5, z, 22.2 if s > 0 else -24.8, 2.6, 4.6)
        out.append(box(s * 18.8, 4.4, z - 0.6, s * 25.2, 5.6, z + 0.6, "metal"))
    else:
        out += wheel(s * 21.5, 5, z, 19.8 if s > 0 else -23.2, 3.4, 4.8)
        out.append(box(s * 19.2, 9, z - 5, s * 23.8, 10, z + 5, "hull"))   # mudguard
    return out


def rotor(hx, hy, hz, mast_y):
    out = [box(hx - 1.5, mast_y, hz - 1.5, hx + 1.5, hy, hz + 1.5, "metal"),
           box(hx - 4.5, mast_y + 0.5, hz - 4.5, hx + 4.5, mast_y + 1.5, hz + 4.5, "dark")]
    out += [box(hx - 3.5, hy, hz - 3.5, hx + 3.5, hy + 3, hz + 3.5, "metal", pivot=[hx, hy, hz], rotation=[0, a, 0])
            for a in (0, 45)]
    out.append(box(hx - 1.5, hy + 3, hz - 1.5, hx + 1.5, hy + 4, hz + 1.5, "dark"))
    for a in (0, 120, 240):
        kw = {"pivot": [hx, hy, hz], "rotation": [0, a, 0]}
        out += [box(hx - 1.2, hy + 0.8, hz - 10, hx + 1.2, hy + 2.2, hz - 3, "metal", **kw),   # pitch housing
                box(hx - 2.5, hy + 1.2, hz - 68, hx + 2.5, hy + 1.8, hz - 8, "blade", **kw),
                box(hx - 0.4, hy + 1.8, hz - 9, hx + 0.4, hy + 3.2, hz - 4, "dark", **kw)]   # pitch link
    return out


FRONT_HUB = (0, 50, -54)
AFT_HUB = (0, 63, 46)


def bones():
    B = [
        {"name": "root", "pivot": [0, 0, 0]},
        {"name": "fuselage", "parent": "root", "pivot": [0, 24, 0], "cubes": fuselage_cubes()},
        {"name": "ramp", "parent": "fuselage", "pivot": [0, 10, 48], "cubes": ramp_cubes()},
        {"name": "cargo_straps", "parent": "fuselage", "pivot": [0, 7, 0],
         "cubes": [box(-0.5, -6, -0.5, 0.5, 4.4, 0.5, "dark"), box(-3, -7, -1, 3, -6, 1, "metal"),
                   box(-6, 3, -6, 6, 4.4, 6, "yellow")]},
        {"name": "rotor_front", "parent": "fuselage", "pivot": list(FRONT_HUB), "cubes": rotor(*FRONT_HUB, 47)},
        {"name": "rotor_aft", "parent": "fuselage", "pivot": list(AFT_HUB), "cubes": rotor(*AFT_HUB, 59)},
    ]
    for name, side, front in (("gear_fl", 1, True), ("gear_fr", -1, True), ("gear_rl", 1, False), ("gear_rr", -1, False)):
        B.append({"name": name, "parent": "fuselage", "pivot": [side * 21.5, 5, -40 if front else 30],
                  "cubes": gear(side, front)})
    return B


def apply_uv(B):
    for b in B:
        for c in b.get("cubes", []):
            u, v, rw, rh = MAT[c.pop("mat")]
            sx, sy, sz = c["size"]
            dims = {"north": (sx, sy), "south": (sx, sy), "east": (sz, sy), "west": (sz, sy), "up": (sx, sz), "down": (sx, sz)}
            c["uv"] = {f: {"uv": [u, v], "uv_size": [round(min(w, rw), 3), round(min(h, rh), 3)]} for f, (w, h) in dims.items()}
    return B


# ---------------------------------------------------------------------------- texture
def paint(t):
    rnd = random.Random(47)
    px = t.set_pixel

    def shade(c, k):
        return tuple(max(0, min(255, int(v * k))) for v in c)

    def skin(u0, v0, w, h, base, pw, ph, grime, streak):
        noise = [[rnd.uniform(-1, 1) for _ in range(w)] for _ in range(h)]
        tones = {}
        for y in range(h):
            for x in range(w):
                pid = (x // pw, (y + (x // pw % 2) * ph // 2) // ph)
                tone = tones.setdefault(pid, rnd.uniform(0.95, 1.04))
                k = tone + noise[y][x] * 0.012
                k -= grime * (y / h) ** 2                     # dirt gathers low
                if streak and (x * 7919 % 13) == 0:
                    k -= 0.03 * (y / h)                       # rain / oil streaks
                lx, ly = x % pw, (y + (x // pw % 2) * ph // 2) % ph
                if lx == 0 or ly == 0:
                    k *= 0.74                                 # recessed panel seam
                elif lx == 1 or ly == 1:
                    k *= 1.06                                 # lit edge after seam
                if (lx == 2 or ly == 2) and (x + y) % 4 == 0:
                    k *= 0.82                                 # rivet row
                px(u0 + x, v0 + y, *shade(base, k))
        for _ in range(w * h // 300):                          # paint chips
            x, y = rnd.randrange(w), rnd.randrange(h)
            px(u0 + x, v0 + y, *shade(base, 0.7))

    skin(0, 0, 128, 128, BASE, 32, 24, 0.10, True)
    skin(128, 0, 128, 128, shade(BASE, 0.97), 24, 32, 0.06, True)
    skin(256, 0, 128, 128, shade(BASE, 0.86), 32, 32, 0.12, True)
    skin(384, 0, 128, 128, shade(BASE, 0.94), 16, 32, 0.05, False)
    for y in range(128):                                       # nacelle louvres + soot toward aft
        for x in range(384, 512):
            if 40 < y < 70 and x % 6 == 0:
                t.set_pixel(x, y, 70, 72, 64)
    # glass: alpha-0 pane, 1px dark gasket frame
    for y in range(128, 192):
        for x in range(0, 64):
            edge = x in (0, 63) or y in (128, 191)
            t.set_pixel(x, y, 40, 42, 40, 255) if edge else t.set_pixel(x, y, 0, 0, 0, 0)
    for y in range(128, 160):                                  # tinted glass with reflection streak
        for x in range(64, 96):
            r = 0.25 if (x - y) % 16 in (0, 1) else 0
            t.set_pixel(x, y, 40 + r * 300, 58 + r * 300, 66 + r * 300)
    for y in range(8):                                         # porthole: hull, dark rim, tinted disc
        for x in range(8):
            d = math.hypot(x - 3.5, y - 3.5)
            col = BASE if d > 3.9 else (52, 54, 50) if d > 2.9 else (70, 92, 104) if (x, y) != (3, 2) else (200, 220, 230)
            t.set_pixel(96 + x, 128 + y, *col)
    t.fill_rect(104, 128, 24, 24, 38, 40, 38)
    for x in range(104, 128, 3):
        t.fill_rect(x, 128, 1, 24, 26, 27, 26)
    for y in range(128, 160):
        for x in range(128, 160):
            t.set_pixel(x, y, *shade((150, 152, 150), 0.9 + rnd.uniform(0, 0.15)))
            t.set_pixel(x + 32, y, *shade((70, 62, 54), 0.8 + ((x + y) % 5) * 0.06))
            t.set_pixel(x + 64, y, *shade((40, 40, 38), 0.85 + (((x + y // 3) % 4) == 0) * 0.4))   # tyre tread
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            t.set_pixel(224 + x, 128 + y, *((120, 122, 112) if d < 6 and int(d) % 3 else (80, 82, 76)))
    for y in range(128, 256):                                  # blade: dark grey, yellow tip bands at both ends
        for x in range(240, 248):
            yy = min(y - 128, 255 - y)
            col = (190, 170, 60) if 2 <= yy < 6 else (60, 62, 60)
            if x in (240, 247):
                col = shade(col, 0.8)
            t.set_pixel(x, y, *col)
    for c, (u, v) in (((200, 40, 36), (248, 128)), ((40, 190, 60), (252, 128)), ((235, 235, 225), (248, 132)),
                      ((210, 170, 40), (252, 132))):
        t.fill_rect(u, v, 4, 4, *c)
    t.fill_rect(64, 160, 32, 32, 62, 66, 58)                   # seat fabric
    for y in range(160, 192, 4):
        t.fill_rect(64, y, 32, 1, 50, 54, 48)
    skin(128, 160, 32, 64, BASE, 64, 64, 0.0, False)           # door
    for y in range(160, 224):
        for x in range(128, 160):
            if x in (129, 158) or y in (161, 222):
                t.set_pixel(x, y, 70, 72, 62)
    t.fill_rect(152, 190, 4, 2, 50, 50, 46)
    t.fill_rect(134, 166, 20, 10, 60, 72, 78)                  # door window
    skin(160, 160, 32, 32, BASE, 64, 64, 0.0, False)           # star on a light disc
    for y in range(32):
        for x in range(32):
            ang, r = math.atan2(y - 16, x - 16), math.hypot(x - 16, y - 16)
            star = r < 6 + 7 * (0.5 + 0.5 * math.cos(5 * (ang + math.pi / 2)))
            if r < 14 and not star:
                t.set_pixel(160 + x, 160 + y, 92, 96, 84)
            elif r < 15 and star:
                t.set_pixel(160 + x, 160 + y, 200, 202, 190)
    skin(192, 160, 48, 16, BASE, 64, 64, 0.0, False)           # tail number "47-147"
    font = {"4": ["101", "101", "111", "001", "001"], "7": ["111", "001", "010", "010", "010"],
            "1": ["010", "110", "010", "010", "111"], "-": ["000", "000", "111", "000", "000"]}
    for i, ch in enumerate("47-147"):
        for gy, row in enumerate(font[ch]):
            for gx, bit in enumerate(row):
                if bit == "1":
                    t.fill_rect(194 + i * 8 + gx * 2, 163 + gy * 2, 2, 2, 46, 48, 42)
    for y in range(176, 208):                                  # walkway grit
        for x in range(192, 224):
            t.set_pixel(x, y, *shade((70, 72, 66), 0.8 + rnd.uniform(0, 0.3)))
    skin(256, 128, 64, 64, shade(BASE, 0.9), 64, 8, 0.0, False)  # ramp: tread ribs + yellow hinge band
    t.fill_rect(256, 128, 64, 3, 190, 160, 50)


def item_icon(path):
    """16x16 side profile: long cabin, twin pylons, two rotor blades, sponson, wheels, nose glass."""
    t = TextureDrawer(16, 16)
    g, d, k = (150, 154, 126), (102, 106, 86), (40, 42, 40)
    rows = {
        2: [(0, 7, k), (8, 15, k)],
        3: [(3, 4, d), (11, 12, d)],
        4: [(2, 5, g), (10, 13, g)],
        5: [(2, 13, g)], 6: [(1, 14, g)], 7: [(1, 14, g)], 8: [(1, 14, g)],
        9: [(1, 13, g)], 10: [(2, 12, d)], 11: [(3, 3, k), (12, 12, k)],
    }
    for y, spans in rows.items():
        for a, b, c in spans:
            for x in range(a, b + 1):
                t.set_pixel(x, y, *c)
    for x in (4, 6, 8, 10):
        t.set_pixel(x, 6, 70, 92, 104)
    t.set_pixel(1, 6, 90, 130, 150)
    t.set_pixel(1, 7, 90, 130, 150)
    t.set_pixel(14, 6, 110, 114, 94)
    t.save(path)


def animation(path):
    spin = lambda deg: {"rotation": {"0.0": [0, 0, 0], "0.25": [0, deg, 0]}}
    anim = {"format_version": "1.8.0", "animations": {
        "animation.chinook_transporter.idle": {"loop": True, "animation_length": 2.0, "bones": {}},  # parked: blades stay still
        "animation.chinook_transporter.fly": {"loop": True, "animation_length": 0.25, "bones": {
            "fuselage": {"rotation": {"0.0": [-3.5, 0, 0], "0.12": [-3.0, 0, 0.4], "0.25": [-3.5, 0, 0]}},
            "rotor_front": spin(360), "rotor_aft": spin(-360)}}}}
    with open(path, "w") as f:
        json.dump(anim, f, indent=2)


def validate(geo, anim_path):
    names = {b["name"] for b in geo["minecraft:geometry"][0]["bones"]}
    n = 0
    for b in geo["minecraft:geometry"][0]["bones"]:
        assert b.get("parent") in names | {None}, b["name"]
        for c in b.get("cubes", []):
            n += 1
            assert all(s > 0 for s in c["size"]), c
            for fc in c["uv"].values():
                (u, v), (w, h) = fc["uv"], fc["uv_size"]
                assert 0 <= u and 0 <= v and u + w <= TEX and v + h <= TEX and w > 0 and h > 0, c
    assert {"fuselage", "cargo_straps", "rotor_front", "rotor_aft", "ramp"} <= names
    anim = json.load(open(anim_path))
    for a in anim["animations"].values():
        assert set(a["bones"]) <= names, set(a["bones"]) - names
    return n


def main():
    B = apply_uv(bones())
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": "geometry.chinook_transporter", "texture_width": TEX, "texture_height": TEX,
                        "visible_bounds_width": 15, "visible_bounds_height": 6, "visible_bounds_offset": [0, 2.5, 0]},
        "bones": B}]}
    geo_path = f"{ASSETS}/geo/chinook_transporter.geo.json"
    anim_path = f"{ASSETS}/animations/chinook_transporter.animation.json"
    with open(geo_path, "w") as f:
        json.dump(geo, f, indent=2)
    animation(anim_path)
    t = TextureDrawer(TEX, TEX)
    paint(t)
    t.save(f"{ASSETS}/textures/entity/transport/chinook_transporter.png")
    item_icon(f"{ASSETS}/textures/item/chinook_transporter.png")
    print("cubes:", validate(geo, anim_path), "bones:", [b["name"] for b in B])


if __name__ == "__main__":
    main()
