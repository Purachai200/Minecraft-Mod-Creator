#!/usr/bin/env python3
"""Oceanic Super-Carrier (LHD-style amphibious assault ship), carrier scale: geo, animation, textures, preview.

Model convention: bow at model -Z (renderer turns 180 deg; Java +Z offsets land at model -Z), Y = 0 is the keel,
model +X is the ship's LEFT (port), the island stands on the starboard (-X) edge. 16 px = 1 block.
Size: ~40 blocks long (stem z=-338 .. stern gate z=+304.4), 12 blocks beam at the flight deck (x=+-96).

Numbers Java builds collision from (model px; Java offset = (x, y, -z) / 16):
  * flight deck: ONE flat surface at y = DECK_Y over the rectangle DECK_RECT (asserted below);
  * island footprint ISLAND_RECT on the starboard edge (everything above the deck inside DECK_RECT lives in it);
  * bridge helm seat cushion HELM; titan spots TITAN_SPOTS; helicopter spots HELO_SPOTS;
  * waterline WATER_Y: red antifouling below it.
Big surfaces use planar UVs: a face samples its material region at its world position, so the deck markings,
hull number and porthole rows line up across neighbouring cubes.
Run from the project root:  python3 scripts/gen_ocean_carrier.py [--preview out_prefix]
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_transport_assets import TextureDrawer  # noqa: E402
import gen_v22_osprey as osp  # noqa: E402

ASSETS = "src/main/resources/assets/titancombat"
TEX = 1024
DECK_Y = 80                       # 5.0 blocks above the keel
WATER_Y = 24                      # 1.5 blocks
DECK_RECT = (-96, 96, -304, 300)  # x0, x1, z0, z1: full-beam rectangle of the flight deck (bow taper forward of it)
ISLAND_RECT = (-96, -60, -132, -8)  # pre-mirror numbers; MIRRORED versions below are what ships
HELM = (-80, 123.5, -106)         # seat cushion top centre
TITAN_SPOTS = [(-38, 70), (-38, 190)]
HELO_SPOTS = [(44, -262), (44, -172), (44, -82), (44, 8), (44, 98), (44, 188), (-40, -250)]

# material -> (u, v, w, h, x_ref, y_top_ref, z_ref): planar projection anchors (world coords at region origin)
MAT = {
    "deck":   (0, 0, 192, 640, -96, 0, -338),       # flight deck, painted 1:1 with markings
    "side":   (192, 0, 640, 84, -320, 82, -338),    # hull side (east face uses the copy at v+84)
    "grey":   (192, 168, 128, 128, 0, 0, 0),        # superstructure haze grey, panel seams, rust
    "grey2":  (320, 168, 128, 128, 0, 0, 0),        # darker grey (shadowed recesses, stacks)
    "win":    (448, 168, 128, 32, 0, 0, 0),         # bridge glass: alpha-0 panes with mullions
    "port":   (448, 200, 128, 32, 0, 0, 0),         # superstructure porthole / door band
    "grate":  (448, 232, 128, 16, 0, 0, 0),         # catwalk grating
    "gate":   (576, 168, 64, 64, 0, 0, 0),          # stern gate ribs
    "array":  (640, 168, 64, 64, 0, 0, 0),          # radar face grid
    "dome":   (704, 168, 64, 32, 0, 0, 0),          # white radome
    "soot":   (768, 168, 64, 64, 0, 0, 0),          # funnel top
    "raft":   (704, 200, 64, 16, 0, 0, 0),          # white life-raft canister rows
    "dark":   (832, 168, 16, 16, 0, 0, 0),
    "metal":  (848, 168, 16, 16, 0, 0, 0),
    "seat":   (864, 168, 16, 16, 0, 0, 0),
    "screen": (880, 168, 16, 16, 0, 0, 0),
    "black":  (896, 168, 16, 16, 0, 0, 0),
    "bootred": (912, 168, 32, 32, 0, 0, 0),         # antifouling red for underwater fittings
    "boat":   (944, 168, 32, 16, 0, 0, 0),          # RHIB orange/grey
    "red":    (976, 168, 8, 8, 0, 0, 0),
    "white":  (984, 168, 8, 8, 0, 0, 0),
    "yellow": (992, 168, 8, 8, 0, 0, 0),
    "green":  (1000, 168, 8, 8, 0, 0, 0),
}

GREY = (196, 202, 208)   # light haze grey: survives the faction tint multiply


def box(x0, y0, z0, x1, y1, z1, mat, **kw):
    lo = [min(x0, x1), min(y0, y1), min(z0, z1)]
    hi = [max(x0, x1), max(y0, y1), max(z0, z1)]
    c = {"origin": [round(v, 3) for v in lo], "size": [round(hi[i] - lo[i], 3) for i in range(3)], "mat": mat}
    c.update(kw)
    return c


def mirror(c):
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


def cyl(cx, cz, y0, y1, r, mat, angles=(0, 45)):
    """Round column: square slabs turned about Y."""
    return [box(cx - r, y0, cz - r, cx + r, y1, cz + r, mat, pivot=[cx, y0, cz], rotation=[0, a, 0]) for a in angles]


# ---------------------------------------------------------------------------- hull
def half_width(z):
    """Waterline half beam: fine bow entry forward of z=-190, full midbody."""
    if z < -190:
        t = (-190 - z) / 150.0                     # 0 at z=-190 .. 1 at the stem z=-340
        return max(2.0, 84 * (1 - t ** 1.7))
    return 84


def hull_cubes():
    C = []
    x0, x1, z0, z1 = DECK_RECT
    # parallel midbody: stepped slabs give a rounded bilge and flared topsides
    for y0, y1, hw in ((0, 4, 60), (4, 8, 72), (8, 14, 80), (14, 56, 84), (56, 66, 88), (66, 72, 91), (72, 76, 94)):
        C.append(box(-hw, y0, -190, hw, y1, 296, "side"))
    # bow: 4-px slices narrowing and raking the stem up; topsides flare out toward the deck overhang
    n = 37
    for i in range(n):
        za = -190 - i * 4
        zb = za - 4
        t = i / (n - 1.0)
        keel = 54 * t ** 2.4
        for y0, y1, k, add in ((keel, 14, 1.0, 0), (max(keel, 14), 56, 1.02, 0), (max(keel, 56), 66, 1.0, 6),
                               (max(keel, 66), 76, 1.0, 12)):
            if y1 - y0 < 0.5:
                continue
            hw = min(94, half_width(zb + 2) * k + add * (0.4 + t))
            C.append(box(-hw, y0, zb, hw, y1, za, "side"))
    # FLIGHT DECK: one slab over the whole rectangle, then the tapering bow overhang (same top y)
    C.append(box(x0, DECK_Y - 4, z0, x1, DECK_Y, z1, "deck"))
    for i in range(8):
        zb = z0 - i * 4
        hw = 96 - (i + 1) ** 1.8 * 1.25
        C.append(box(-hw, DECK_Y - 4, zb - 4, hw, DECK_Y, zb, "deck"))
    C.append(box(-90, 56, -190, 90, 76, -170, "side"))     # bow flare fill under the deck overhang
    # stern: transom, well-deck gate recess frame, stern flaps, ensign staff
    C += [box(-94, 24, 296, 94, 76, 300, "side"), box(-90, 4, 290, 90, 24, 296, "side"),
          box(-36, 24, 300, 36, 26, 304, "dark")]
    C += both(box(36, 24, 300, 44, 74, 304, "grey2"), box(60, 30, 300, 92, 74, 302, "grey2"))
    C += [box(-0.6, 40, 302, 0.6, 72, 303.2, "metal", pivot=[0, 40, 302], rotation=[-25, 0, 0]),
          box(0.6, 62, 304, 10, 68, 304.4, "red", pivot=[0, 40, 302], rotation=[-25, 0, 0])]
    # sea-stained boot-top girdle is in the texture; bilge keels, sonar bulb, shafts, struts, screws, rudders
    C += [box(-8, 2, -300, 8, 16, -230, "bootred"), box(-5, 16, -296, 5, 32, -262, "bootred")]
    C += both(box(66, 4, -80, 72, 6, 120, "bootred"),
              box(26, -2, 230, 30, 14, 266, "bootred"),                  # rudder
              box(27, 3, 150, 29, 5, 236, "metal"),                      # shaft
              box(24, 0, 196, 32, 10, 200, "bootred"),                   # A-bracket
              box(23, -1, 222, 33, 9, 228, "metal"))                     # hub
    for s in (1, -1):
        for a in range(0, 360, 72):
            C.append(box(s * 28 - 2, 0, 223, s * 28 + 2, 13, 227, "metal", pivot=[s * 28, 4, 225], rotation=[0, 0, a]))
    # anchors + hawse pipes either side of the stem
    C += both(box(36, 50, -290, 40, 58, -282, "dark"), box(38, 40, -289, 41, 50, -283, "metal"),
              box(37, 38, -292, 42, 40, -280, "metal"))
    # hangar side doors (dark recess) + lowered deck-edge elevators: port amidships, starboard aft of island
    C += [box(84, 40, 30, 88.4, 66, 80, "dark"), box(-88.4, 40, 206, -84, 66, 256, "dark")]
    for sx, za, zb in ((1, 30, 80), (-1, 206, 256)):
        xa, xb = sorted((sx * 96, sx * 134))
        C += [box(xa, 52, za, xb, 56, zb, "dark"),
              box(xa, 48, za + 6, xb, 52, za + 9, "grey2"), box(xa, 48, zb - 9, xb, 52, zb - 6, "grey2"),
              box(sx * 134 - (0.6 if sx > 0 else 0), 56, za, sx * 134 + (0 if sx > 0 else 0.6), 59, zb, "metal")]
        xc = sorted((sx * 88, sx * 96))
        C += [box(xc[0], 46, za - 2, xc[1], 80 - 4, za, "grey2"), box(xc[0], 46, zb, xc[1], 76, zb + 2, "grey2")]
    # catwalk galleries along the deck edge (below the lip), rails, life-raft canisters
    for za, zb in ((-280, -200), (-180, -100), (-90, 20), (90, 190), (200, 240)):
        C += both(box(96, 71, za, 104, 72, zb, "grate"), box(103.4, 72, za, 104, 76.5, zb, "metal"),
                  box(103.4, 74.2, za, 104.2, 74.8, zb, "metal"),
                  box(94, 62, za + 4, 100, 70, zb - 4, "raft"))
        for z in range(za, zb + 1, 10):
            C += both(box(96, 67, z, 97, 71, z + 1, "grey2", pivot=[96, 71, z], rotation=[0, 0, 0]))
    C = [c for c in C if not (c["origin"][0] < -94 and 180 < c["origin"][2] < 260 and c["mat"] in ("raft",))]
    # sponsons: CIWS bow port + stern starboard, RAM launchers bow starboard + stern port
    for sx, sz in ((1, -250), (-1, -276), (1, 270), (-1, 262)):
        xa, xb = sorted((sx * 92, sx * 124))
        C += [box(xa, 64, sz - 14, xb, 76, sz + 14, "grey"), box(xa, 60, sz - 10, xb, 64, sz + 10, "grey2")]
    C += ciws(108, 76, -250, -1) + ciws(-108, 76, 262, 1) + ram(-108, 76, -276) + ram(108, 76, 270)
    # whip antennas leaning outboard from the catwalks
    for z in (-240, -140, -40, 120, 220):
        C += both(box(104.5, 72, z, 105.5, 108, z + 1, "dark", pivot=[105, 72, z], rotation=[0, 0, -18]))
    # RHIB boats in davits on the starboard quarter
    for bz in (110, 150):
        C += [box(-104, 58, bz, -94, 63, bz + 26, "boat"), box(-102, 63, bz + 4, -96, 66, bz + 12, "white"),
              box(-104, 63, bz + 2, -88, 65, bz + 4, "metal"), box(-104, 63, bz + 22, -88, 65, bz + 24, "metal")]
    # bow navigation lights + jackstaff on the overhang tip, stern lights
    C += [box(-0.6, DECK_Y, -334, 0.6, DECK_Y + 22, -332.8, "metal"),
          box(20, 76, -322, 22, 78, -320, "green"), box(-22, 76, -322, -20, 78, -320, "red"),
          box(-2, 74, 300, 2, 76, 301, "white")]
    return C


def ciws(x, y, z, face, s=1.7):
    """Phalanx: pedestal, gun body, tall white radome, barrel cluster pointing fore (face -1) or aft (+1)."""
    out = cyl(x, z, y, y + 3 * s, 3.5 * s, "grey")
    out += [box(x - 3 * s, y + 3 * s, z - 3.5 * s, x + 3 * s, y + 8 * s, z + 3.5 * s, "grey"),
            box(x - 2.5 * s, y + 8 * s, z - 3 * s, x + 2.5 * s, y + 13 * s, z + 3 * s, "dome"),
            box(x - 2 * s, y + 13 * s, z - 2.5 * s, x + 2 * s, y + 15 * s, z + 2.5 * s, "dome"),
            box(x - 1.2 * s, y + 15 * s, z - 1.5 * s, x + 1.2 * s, y + 16 * s, z + 1.5 * s, "dome"),
            box(x - 1 * s, y + 4.5 * s, z + face * 3.5 * s, x + 1 * s, y + 6.5 * s, z + face * 13 * s, "dark"),
            box(x - 1.6 * s, y + 4 * s, z + face * 3.5 * s, x + 1.6 * s, y + 7 * s, z + face * 6 * s, "metal")]
    return out


def ram(x, y, z):
    """RAM launcher: pedestal, trainable box with a 21-cell face."""
    return cyl(x, z, y, y + 5, 6, "grey") + [
        box(x - 8, y + 5, z - 7, x + 8, y + 17, z + 7, "grey2"),
        box(x - 7.5, y + 6, z - 7.6, x + 7.5, y + 16, z - 7, "array"),
        box(x - 9, y + 8, z - 4, x - 8, y + 14, z + 4, "metal"), box(x + 8, y + 8, z - 4, x + 9, y + 14, z + 4, "metal")]


# ---------------------------------------------------------------------------- island
def island_cubes():
    C = []
    D = DECK_Y
    # base: two hangar-top office levels, porthole + door bands on both faces
    C += [box(-96, D, -130, -62, D + 28, -10, "grey"), box(-96, D + 28, -126, -64, D + 40, -12, "grey"),
          box(-62, D + 6, -128, -61.6, D + 14, -12, "port"), box(-62, D + 18, -128, -61.6, D + 26, -12, "port"),
          box(-64, D + 30, -124, -63.6, D + 38, -14, "port"),
          box(-96.4, D + 6, -128, -96, D + 14, -12, "port"), box(-96.4, D + 18, -128, -96, D + 26, -12, "port")]
    # deck-level watertight doors and access ladders on the inboard face
    for z in (-118, -84, -48, -22):
        C += [box(-61.6, D, z, -61.2, D + 7, z + 5, "dark")]
    for z in (-100, -60):
        C += [box(-61.6, D, z, -61, D + 28, z + 0.6, "metal"), box(-61.6, D, z + 5, -61, D + 28, z + 5.6, "metal")]
        C += [box(-61.6, y, z, -61, y + 0.5, z + 5.6, "metal") for y in range(D + 2, D + 28, 3)]
    # bridge level (hollow, glazed): floor y = D+40, roof y = D+70
    fy, ry = D + 40, D + 70
    x0, x1, z0, z1 = -94, -64, -126, -90
    C += [box(x0, ry, z0 - 3, x1 + 1, ry + 3, z1, "grey"),                      # roof + brow over the glass
          box(x0, fy, z0, x1, fy + 12, z0 + 1, "grey"),                           # forward bulkhead below glass
          box(x1 - 1, fy, z0, x1, fy + 12, z1, "grey"),                           # inboard bulkhead below glass
          box(x0, fy, z0, x0 + 1, ry, z1, "grey"),                                # outboard wall solid
          box(x0, fy, z1 - 1, x1, ry, z1, "grey"),                                # aft wall
          box(x0, fy + 12, z0, x1, fy + 13, z0 + 1.2, "grey2"), box(x1 - 1.2, fy + 12, z0, x1, fy + 13, z1, "grey2"),
          box(x0, ry - 2, z0, x1, ry, z0 + 1.2, "grey2"), box(x1 - 1.2, ry - 2, z0, x1, ry, z1, "grey2"),
          box(x0 + 1, fy + 13, z0 + 0.3, x1 - 1, ry - 2, z0 + 0.7, "win"),        # forward glass (alpha-0 panes)
          box(x1 - 0.7, fy + 13, z0 + 1.2, x1 - 0.3, ry - 2, z1 - 1, "win")]      # inboard glass over the deck
    for x in range(-88, -64, 6):
        C.append(box(x - 0.5, fy + 13, z0, x + 0.5, ry - 2, z0 + 1.2, "grey2"))  # mullions
    for z in range(-118, -92, 7):
        C.append(box(x1 - 1.2, fy + 13, z - 0.5, x1, ry - 2, z + 0.5, "grey2"))
    # helm: chair (cushion top = HELM y), binnacle console, chart table, overhead screens
    hx, hy, hz = HELM
    C += [box(hx - 3, fy, hz - 3, hx + 3, hy, hz + 3, "seat"), box(hx - 3, hy, hz + 3, hx + 3, hy + 9, hz + 4, "seat"),
          box(hx - 3.6, hy, hz - 3, hx - 3, hy + 2.5, hz + 3, "seat"), box(hx + 3, hy, hz - 3, hx + 3.6, hy + 2.5, hz + 3, "seat"),
          box(hx - 4, fy, hz - 14, hx + 4, fy + 9, hz - 10, "dark"), box(hx - 3.5, fy + 9, hz - 14, hx + 3.5, fy + 9.4, hz - 11, "screen"),
          box(-92, fy, -124, -66, fy + 8, -120, "dark"), box(-91.5, fy + 8, -124, -66.5, fy + 8.4, -121, "screen"),
          box(-92, fy, -100, -86, fy + 8, -93, "dark"), box(-89, ry - 4, -124, -71, ry - 1, -123, "screen")]
    # bridge wings: outboard (beyond the deck edge) and stub inboard over the island roof line
    C += [box(-108, fy - 1, -126, -94, fy, -112, "grey"), box(-108, fy, -126, -107.4, fy + 6, -112, "metal"),
          box(-108, fy, -126, -94, fy + 6, -125.4, "metal"), box(-106, fy, -122, -102, fy + 7, -118, "dark")]
    # mid block (stacks sit on it) and Pri-Fly: glazed box looking inboard over the deck
    C += [box(-94, fy, -90, -66, ry, -60, "grey"), box(-66, fy + 4, -86, -65.6, fy + 12, -64, "port")]
    C += [box(-94, fy, -60, -64, fy + 12, -36, "grey"), box(-94, fy + 12, -60, -70, ry - 4, -36, "grey"),
          box(-70, fy + 12, -60, -64.4, fy + 13, -36, "grey2"), box(-65, fy + 13, -59, -64.6, ry - 5, -37, "win"),
          box(-94, ry - 4, -61, -63, ry - 2, -35, "grey2"), box(-82, fy + 12, -40, -70, fy + 18, -38, "dark")]
    # aft block + small CIWS-free ammunition lift house
    C += [box(-94, fy, -36, -64, ry, -14, "grey"), box(-64, fy + 6, -32, -63.6, fy + 14, -18, "port")]
    # twin stacks (LHD style) with soot caps and exhaust grilles
    for zc in (-80, -64):
        C += [box(-92, ry, zc - 6, -70, ry + 26, zc + 6, "grey2"), box(-91.4, ry + 26, zc - 5.4, -70.6, ry + 26.6, zc + 5.4, "soot"),
              box(-90, ry + 26, zc - 4, -84, ry + 29, zc + 4, "dark"), box(-78, ry + 26, zc - 4, -72, ry + 29, zc + 4, "dark"),
              box(-92.4, ry + 4, zc - 5, -92, ry + 20, zc + 5, "grate")]
    # nav deck above the bridge with mast base
    C += [box(-94, ry + 3, -124, -66, ry + 10, -92, "grey"), box(-66, ry + 4, -122, -65.6, ry + 9, -94, "port"),
          box(-90, ry + 10, -118, -70, ry + 13, -98, "grey2")]
    # lattice mast: four tilted legs, cross bracing, platforms, yardarm, topmast with masthead light
    my = ry + 13
    for lx, lz in ((-88, -116), (-72, -116), (-88, -100), (-72, -100)):
        C.append(box(lx - 1, my, lz - 1, lx + 1, my + 58, lz + 1, "metal",
                     pivot=[lx, my, lz], rotation=[(lz + 108) * 0.55, 0, -(lx + 80) * 0.55]))
    for y in range(my + 10, my + 56, 11):
        k = (y - my) / 58.0 * 4
        C += [box(-88 + k, y, -116 + k, -72 - k, y + 0.8, -115.2 + k, "metal"),
              box(-88 + k, y, -100.8 - k, -72 - k, y + 0.8, -100 - k, "metal"),
              box(-88 + k, y, -116 + k, -87.2 + k, y + 0.8, -100 - k, "metal"),
              box(-72.8 - k, y, -116 + k, -72 - k, y + 0.8, -100 - k, "metal")]
    C += [box(-90, my + 56, -114, -70, my + 58, -102, "grate"), box(-90, my + 58, -114, -89.4, my + 61, -102, "metal"),
          box(-70.6, my + 58, -114, -70, my + 61, -102, "metal"),
          box(-114, my + 48, -108.8, -60, my + 49.5, -107.2, "metal"),                # yardarm
          box(-81, my + 58, -101, -79, my + 100, -99, "metal"), box(-81.5, my + 100, -101.5, -78.5, my + 103, -98.5, "red")]
    for x in (-110, -102, -70, -62):
        C.append(box(x - 0.3, my + 44, -108.3, x + 0.3, my + 48, -107.7, "dark"))      # signal halyard blocks
    C += [box(-93, my + 24, -112, -90, my + 26, -104, "grey2"), box(-96, my + 18, -112, -93, my + 30, -104, "array")]
    # SATCOM / EW radomes over Pri-Fly, ECM blisters on the outboard face
    for zc, h in ((-52, 12), (-42, 10)):
        C += [box(-90, ry - 2, zc - 4, -82, ry, zc + 4, "grey2"), box(-89.5, ry, zc - 3.5, -82.5, ry + h - 2, zc + 3.5, "dome"),
              box(-88.5, ry + h - 2, zc - 2.5, -83.5, ry + h, zc + 2.5, "dome")]
    C += [box(-100, D + 48, -84, -96, D + 60, -70, "grey2"), box(-100.4, D + 49, -83, -100, D + 59, -71, "array"),
          box(-100, D + 48, -30, -96, D + 60, -18, "grey2"), box(-100.4, D + 49, -29, -100, D + 59, -19, "array")]
    return C


def radar_cubes():
    """SPS-48 style 3-D array: big tilted planar face on a pedestal spinning at the masthead platform."""
    px, py, pz = -80, DECK_Y + 70 + 13 + 61, -108
    return [box(px - 3, py, pz - 3, px + 3, py + 3, pz + 3, "metal"),
            box(px - 18, py + 3, pz - 2, px + 18, py + 26, pz + 0.6, "array", pivot=[px, py + 3, pz], rotation=[-12, 0, 0]),
            box(px - 18.6, py + 2.4, pz + 0.6, px + 18.6, py + 26.6, pz + 2, "grey2", pivot=[px, py + 3, pz], rotation=[-12, 0, 0]),
            box(px - 15, py + 26.6, pz - 1.5, px + 15, py + 29, pz + 1.5, "metal", pivot=[px, py + 3, pz], rotation=[-12, 0, 0])]


def radar_aux_cubes():
    """SPS-49 style long-range air search: wide shallow bar on the aft island roof."""
    px, py, pz = -79, DECK_Y + 70, -25
    return [box(px - 2, py, pz - 2, px + 2, py + 6, pz + 2, "metal"),
            box(px - 15, py + 6, pz - 1.5, px + 15, py + 12, pz + 0.4, "array"),
            box(px - 15, py + 6, pz + 0.4, px + 15, py + 12, pz + 1.5, "grey2")]


def strap_cubes():
    """Flush tie-down pad eyes + chain runs at both titan spots (at most 0.3 px proud of the deck)."""
    out = []
    for sx, sz in TITAN_SPOTS:
        for dx, dz in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            out.append(box(sx + dx * 22 - 0.6, DECK_Y, sz + dz * 22 - 0.6, sx + dx * 22 + 0.6, DECK_Y + 0.3,
                           sz + dz * 22 + 0.6, "metal"))
            out.append(box(sx + dx * 8, DECK_Y, sz + dz * 8 - 0.3, sx + dx * 22, DECK_Y + 0.2, sz + dz * 8 + 0.3, "yellow"))
    return out


def gate_cubes():
    return [box(-34, 26, 302, 34, 74, 303.4, "gate"), box(-34.6, 72, 302, 34.6, 75, 304, "grey2"),
            box(-30, 27, 303.4, -27, 72, 304.4, "metal"), box(27, 27, 303.4, 30, 72, 304.4, "metal")]


def bones():
    """Built in the pre-mirror frame, then mirrored across X: in game the island must land on starboard."""
    B = _bones()
    for b in B:
        b["pivot"][0] = -b["pivot"][0]
        if "cubes" in b:
            b["cubes"] = [mirror(c) for c in b["cubes"]]
    return B


def _bones():
    return [
        {"name": "root", "pivot": [0, 0, 0]},
        {"name": "hull", "parent": "root", "pivot": [0, WATER_Y, 0], "cubes": hull_cubes()},
        {"name": "stern_gate", "parent": "hull", "pivot": [0, 26, 302], "cubes": gate_cubes()},
        {"name": "bridge", "parent": "hull", "pivot": [-79, DECK_Y, -70], "cubes": island_cubes()},
        {"name": "radar", "parent": "bridge", "pivot": [-80, DECK_Y + 144, -108], "cubes": radar_cubes()},
        {"name": "radar_aux", "parent": "bridge", "pivot": [-79, DECK_Y + 70, -25], "cubes": radar_aux_cubes()},
        {"name": "cargo_straps", "parent": "hull", "pivot": [0, DECK_Y, 130], "cubes": strap_cubes()},
    ]


# ---------------------------------------------------------------------------- planar UVs
FACE_AXES = {  # face -> (u axis, u reversed, v axis)
    "north": (0, True, 1), "south": (0, False, 1), "east": (2, True, 1), "west": (2, False, 1),
    "up": (0, False, 2), "down": (0, False, 2)}


def apply_uv(B):
    for b in B:
        for c in b.get("cubes", []):
            mat = c.pop("mat")
            u0, v0, rw, rh, xr, ytop, zr = MAT[mat]
            lo = c["origin"]
            hi = [lo[i] + c["size"][i] for i in range(3)]
            refs = (xr, None, zr)
            c["uv"] = {}
            for f, (ua, rev, va) in FACE_AXES.items():
                us_c, vs_c = min(hi[ua] - lo[ua], rw), min(hi[va] - lo[va], rh)
                su = (refs[ua] + rw - hi[ua]) if rev else (lo[ua] - refs[ua])
                sv = (ytop - hi[1]) if va == 1 else (lo[2] - zr)
                su = su % rw if su + us_c > rw or su < 0 else su
                sv = sv % rh if sv + vs_c > rh or sv < 0 else sv
                su, sv = max(0, min(su, rw - us_c)), max(0, min(sv, rh - vs_c))
                ev = 84 if (mat == "side" and f == "east") else 0   # east side has its own hull-number copy
                c["uv"][f] = {"uv": [round(u0 + su, 3), round(v0 + ev + sv, 3)], "uv_size": [round(us_c, 3), round(vs_c, 3)]}
    return B


# ---------------------------------------------------------------------------- texture
FONT = {
    "0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"], "9": ["111", "101", "111", "001", "111"],
    "H": ["101", "101", "111", "101", "101"], "T": ["111", "010", "010", "010", "010"]}


MX = lambda pts: [(-x,) + tuple(r) for x, *r in pts]


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def paint(t):
    HELO_SPOTS, TITAN_SPOTS = MX(globals()['HELO_SPOTS']), MX(globals()['TITAN_SPOTS'])
    rnd = random.Random(9)
    px = t.set_pixel

    def text(x, y, s, col, sc=2, flip=False):
        # verified in game: unmirrored glyphs read correctly
        for i, ch in enumerate(s[::-1] if flip else s):
            for gy, row in enumerate(FONT[ch]):
                for gx, bit in enumerate(row[::-1] if flip else row):
                    if bit == "1":
                        t.fill_rect(x + i * 4 * sc + gx * sc, y + gy * sc, sc, sc, *col)

    def plate(u0, v0, w, h, base, pw, ph, rust):
        for y in range(h):
            for x in range(w):
                k = 1 + rnd.uniform(-0.015, 0.015)
                lx, ly = x % pw, y % ph
                if lx == 0 or ly == 0:
                    k *= 0.84
                elif ly == 1:
                    k *= 1.04
                px(u0 + x, v0 + y, *shade(base, k))
        for _ in range(int(w * rust)):                               # rust weeps running down from seams
            x, y0 = rnd.randrange(w), rnd.randrange(0, h, ph)
            for y in range(y0, min(h, y0 + rnd.randint(3, ph + 6))):
                r, g, b = shade(base, 0.97)
                f = 1 - (y - y0) / (ph + 6)
                px(u0 + x, v0 + y, int(r * (1 - 0.18 * f) + 150 * 0.18 * f), int(g * (1 - 0.25 * f) + 80 * 0.25 * f),
                   int(b * (1 - 0.3 * f) + 50 * 0.3 * f))

    # --- flight deck (u = x + 96, v = z + 338): dark non-skid, tie-down grid, markings
    du, dv = MAT["deck"][:2]
    W, H = MAT["deck"][2:4]
    for y in range(H):
        for x in range(W):
            k = 1 + rnd.uniform(-0.05, 0.05) - (0.05 if (x * 31 + y * 17) % 23 == 0 else 0)
            if x % 12 == 6 and y % 12 == 6:
                k *= 0.7                                              # recessed tie-down pad eyes
            px(du + x, dv + y, *shade((62, 64, 68), k))
    for y in range(0, H, 24):                                         # non-skid panel joins
        t.fill_rect(du, dv + y, W, 1, 54, 56, 60)

    def dx(x):
        return du + int(round(x)) + 96

    def dz(z):
        return dv + int(round(z)) + 338

    Y, Wt, R = (222, 188, 60), (232, 232, 228), (196, 58, 48)
    for side in (-1, 1):                                              # white deck edge lines + flush edge lights
        t.fill_rect(dx(side * 92 - (1 if side > 0 else 0)), dz(-300), 2, 598, *Wt)
        for z in range(-296, 300, 16):
            t.fill_rect(dx(side * 95 - 1), dz(z), 2, 2, *((40, 190, 70) if z < 0 else Wt))
    for z in range(-330, 300, 10):                                    # dashed centreline down the port landing lane
        t.fill_rect(dx(-45), dz(z), 2, 6, *Wt)
    for z in range(-140, 0, 8):                                       # island foul line
        t.fill_rect(dx(56), dz(z), 2, 5, *Y)
    t.fill_rect(dx(56), dz(0), 2, 280, *Y)

    def ring(cx, cz, r, col, wdt=2):
        for a in range(0, 360):
            for d in range(wdt):
                rr = r - d
                t.fill_rect(dx(cx + rr * math.cos(math.radians(a))), dz(cz + rr * math.sin(math.radians(a))), 1, 1, *col)

    for i, (cx, cz) in enumerate(HELO_SPOTS):                         # helo spots: yellow ring, white lineup T, big number
        ring(cx, cz, 30, Y, 3)
        ring(cx, cz, 4, Wt, 2)
        t.fill_rect(dx(cx - 1), dz(cz - 40), 3, 80, *Wt)              # fore-aft lineup line
        t.fill_rect(dx(cx - 14), dz(cz - 40), 29, 3, *Wt)             # T bar at the head
        n = str(i + 1)
        text(dx(cx + 7), dz(cz - 15), n, Wt, 6)   # reads upright to a pilot approaching from astern
    for i, (cx, cz) in enumerate(TITAN_SPOTS):                        # titan spots: big hatched yellow box, T + number
        for d in range(3):
            for a in range(-28, 29):
                for e in (-28 + d, 28 - d):
                    t.fill_rect(dx(cx + a), dz(cz + e), 1, 1, *Y)
                    t.fill_rect(dx(cx + e), dz(cz + a), 1, 1, *Y)
        for a in range(-25, 26):                                      # corner hazard hatching
            for e in range(-25, 26):
                if (abs(a) > 17 or abs(e) > 17) and (abs(a) > 17 and abs(e) > 17) and (a + e) % 6 < 3:
                    t.fill_rect(dx(cx + a), dz(cz + e), 1, 1, *Y)
        text(dx(cx - 14), dz(cz - 10), "T" + str(i + 1), Wt, 4)
    for x in range(-94, 95, 8):                                       # stern ramp hash (red/white)
        t.fill_rect(dx(x), dz(292), 4, 6, *R)
        t.fill_rect(dx(x + 4), dz(292), 4, 6, *Wt)
    text(dx(-30), dz(-326), "47", Wt, 7)                              # big hull number on the bow
    for _ in range(900):                                              # tyre / oil smudges
        x, y = rnd.randrange(W), rnd.randrange(H)
        t.fill_rect(du + x, dv + y, rnd.randint(1, 3), rnd.randint(1, 6), 46, 47, 50)
    for cx, cz in HELO_SPOTS:                                         # rotor-wash exhaust scorch round the spots
        for _ in range(160):
            a, r = rnd.uniform(0, 6.3), rnd.uniform(6, 26)
            px(dx(cx + r * math.cos(a)), dz(cz + r * math.sin(a)), 40, 41, 43)

    # --- hull side (west face u = z + 338, v = 82 - y; east copy at v + 84 reads bow at large u)
    su, sv0 = MAT["side"][:2]
    SW, SH = MAT["side"][2:4]
    for sv in (sv0, sv0 + 84):
        plate(su, sv, SW, SH, GREY, 32, 10, 0.25)
        for y in range(SH):
            yy = 82 - y - 0.5
            for x in range(SW):
                if yy < WATER_Y:
                    px(su + x, sv + y, *shade((150, 44, 36), 1 + rnd.uniform(-0.05, 0.05)))      # antifouling red
                elif yy < WATER_Y + 4:
                    px(su + x, sv + y, *shade((44, 46, 50), 1 + rnd.uniform(-0.05, 0.05)))       # black boot-top
                elif yy < WATER_Y + 8:
                    px(su + x, sv + y, *shade(GREY, 0.8 + rnd.uniform(-0.05, 0.05)))             # sea-stained band
        for x in range(12, SW - 8, 9):                                   # two porthole rows
            for py_ in (14, 30):
                t.fill_rect(su + x, sv + py_, 2, 2, 40, 44, 52)
                px(su + x, sv + py_, 120, 140, 160)
        for x in range(40, SW - 20, 37):                                 # scuppers with rust weeps
            t.fill_rect(su + x, sv + 8, 3, 2, 40, 42, 46)
            for y in range(10, 40):
                if rnd.random() < 0.75:
                    px(su + x + 1, sv + y, 150, 98, 70)
        west = sv == sv0
        bow_u = lambda z: (z + 338) if west else (SW - (z + 338))
        text(su + bow_u(-280 if west else -230), sv + 24, "47", (44, 46, 50), 7)          # hull number near the bow
        for z in (-300, 270):                                            # draft marks at bow and stern
            for k, y in enumerate((44, 52, 60, 68)):
                text(su + bow_u(z), sv + y - 2, str(8 - k * 2 if k else 8)[-1], Wt, 1)

    # --- superstructure and fittings
    plate(*MAT["grey"][:2], 128, 128, GREY, 24, 14, 0.2)
    plate(*MAT["grey2"][:2], 128, 128, shade(GREY, 0.86), 24, 14, 0.3)
    wu, wv = MAT["win"][:2]                                           # alpha-0 glass, dark gasket mullions
    for y in range(32):
        for x in range(128):
            if y in (0, 31) or x % 12 == 0:
                px(wu + x, wv + y, 50, 54, 60)
            else:
                px(wu + x, wv + y, 0, 0, 0, 0)
    pu, pv = MAT["port"][:2]
    plate(pu, pv, 128, 32, GREY, 128, 32, 0)
    for x in range(3, 128, 8):
        t.fill_rect(pu + x, pv + 3, 3, 3, 40, 44, 52)
        px(pu + x, pv + 3, 130, 150, 170)
    gu, gv = MAT["grate"][:2]
    for y in range(16):
        for x in range(128):
            px(gu + x, gv + y, *((70, 72, 76) if (x % 3 == 0 or y % 3 == 0) else (36, 38, 40)))
    gu, gv = MAT["gate"][:2]
    plate(gu, gv, 64, 64, shade(GREY, 0.92), 64, 6, 0.4)
    t.fill_rect(gu, gv + 58, 64, 6, 190, 160, 50)
    au, av = MAT["array"][:2]
    for y in range(64):
        for x in range(64):
            px(au + x, av + y, *((92, 98, 104) if (x % 4 == 0 or y % 4 == 0) else (150, 156, 162)))
    mu, mv = MAT["dome"][:2]
    for y in range(32):
        for x in range(64):
            px(mu + x, mv + y, *shade((236, 236, 230), 1 - y * 0.006 + rnd.uniform(-0.02, 0.02)))
    t.fill_rect(*MAT["dark"][:2], 16, 16, 40, 42, 46)
    for y in range(16):
        for x in range(16):
            px(MAT["metal"][0] + x, MAT["metal"][1] + y, *shade((150, 154, 158), 0.9 + 0.15 * ((x + y) % 3 == 0)))
            px(MAT["seat"][0] + x, MAT["seat"][1] + y, 60, 66, 76)
            px(MAT["screen"][0] + x, MAT["screen"][1] + y, *((60, 200, 120) if (y % 3 == 0 and x % 5) else (20, 40, 34)))
            px(MAT["black"][0] + x, MAT["black"][1] + y, 30, 30, 32)
    for y in range(32):
        for x in range(32):
            px(MAT["bootred"][0] + x, MAT["bootred"][1] + y, *shade((150, 44, 36), 1 + rnd.uniform(-0.05, 0.05)))
    for y in range(16):
        for x in range(32):
            px(MAT["boat"][0] + x, MAT["boat"][1] + y, *((226, 110, 40) if y < 6 else (70, 74, 78)))
    su2, sv2 = MAT["soot"][:2]
    for y in range(64):
        for x in range(64):
            px(su2 + x, sv2 + y, *shade((52, 50, 48), 0.8 + rnd.uniform(0, 0.4)))
    ru, rv = MAT["raft"][:2]
    for y in range(16):
        for x in range(64):
            px(ru + x, rv + y, *((210, 212, 206) if x % 6 else (120, 124, 126)))
    for name, col in (("red", (200, 40, 36)), ("white", (236, 236, 228)), ("yellow", Y), ("green", (40, 190, 70))):
        t.fill_rect(*MAT[name][:2], 8, 8, *col)


def item_icon(path):
    """16x16 side profile: long grey hull on red bottom, island + mast at starboard amidships, flat deck."""
    t = TextureDrawer(16, 16)
    g, d, r, k = (176, 182, 188), (120, 126, 132), (150, 44, 36), (44, 46, 50)
    for x in range(0, 16):
        t.set_pixel(x, 9, *d)                                   # deck
    for x in range(1, 16):
        t.set_pixel(x, 10, *g)
        t.set_pixel(x, 11, *g)
    for x in range(2, 15):
        t.set_pixel(x, 12, *k)
        t.set_pixel(x, 13, *r)
    t.set_pixel(0, 10, *g)
    for y in range(5, 9):
        for x in range(5, 9):
            t.set_pixel(x, y, *g)
    t.set_pixel(5, 6, 60, 80, 100)
    t.set_pixel(6, 6, 60, 80, 100)
    for y in range(1, 5):
        t.set_pixel(6, y, *d)
    t.set_pixel(5, 2, *d)
    t.set_pixel(7, 2, *d)
    t.set_pixel(8, 4, *k)
    for x in (3, 10, 12, 14):
        t.set_pixel(x, 11, 40, 44, 52)
    t.save(path)


def animation(path):
    spin = lambda length, deg: {"rotation": {"0.0": [0, 0, 0], str(length): [0, deg, 0]}}
    anim = {"format_version": "1.8.0", "animations": {
        "animation.ocean_carrier.idle": {"loop": True, "animation_length": 6.0, "bones": {
            "hull": {"position": {"0.0": [0, 0, 0], "3.0": [0, -0.5, 0], "6.0": [0, 0, 0]},
                     "rotation": {"0.0": [0, 0, 0], "1.5": [0.25, 0, 0.5], "3.0": [0, 0, 0], "4.5": [-0.25, 0, -0.5],
                                  "6.0": [0, 0, 0]}},
            "radar": spin(6.0, -360), "radar_aux": spin(3.0, 360)}},
        "animation.ocean_carrier.sail": {"loop": True, "animation_length": 3.0, "bones": {
            "hull": {"position": {"0.0": [0, 0, 0], "1.5": [0, -0.8, 0], "3.0": [0, 0, 0]},
                     "rotation": {"0.0": [-0.4, 0, 0], "0.75": [0.2, 0, 0.7], "1.5": [0.5, 0, 0],
                                  "2.25": [0.1, 0, -0.7], "3.0": [-0.4, 0, 0]}},
            "radar": spin(3.0, -360), "radar_aux": spin(1.5, 360)}}}}
    with open(path, "w") as f:
        json.dump(anim, f, indent=2)
    return anim


def world_bbox(c):
    o, s = c["origin"], c["size"]
    pts = [[o[0] + i * s[0], o[1] + j * s[1], o[2] + k * s[2]] for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    if "rotation" in c:
        pts = [osp.about(p, c["pivot"], c["rotation"]) for p in pts]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def validate(geo, anim):
    bl = geo["minecraft:geometry"][0]["bones"]
    names = {b["name"] for b in bl}
    n = 0
    for b in bl:
        assert b.get("parent") in names | {None}, b["name"]
        for c in b.get("cubes", []):
            n += 1
            assert all(s > 0 for s in c["size"]), (b["name"], c)
            for fc in c["uv"].values():
                (u, v), (w, h) = fc["uv"], fc["uv_size"]
                assert 0 <= u and 0 <= v and u + w <= TEX and v + h <= TEX and w > 0 and h > 0, (b["name"], c)
    assert {"hull", "cargo_straps", "radar", "radar_aux", "stern_gate", "bridge"} <= names
    assert set(anim["animations"]) == {"animation.ocean_carrier.idle", "animation.ocean_carrier.sail"}
    for a in anim["animations"].values():
        assert set(a["bones"]) <= names, set(a["bones"]) - names
    # flat deck: one cube tops out at DECK_Y over the whole rectangle ...
    x0, x1, z0, z1 = DECK_RECT
    hull = next(b for b in bl if b["name"] == "hull")["cubes"]
    assert any(c["origin"][0] <= x0 and c["origin"][0] + c["size"][0] >= x1 and c["origin"][2] <= z0
               and c["origin"][2] + c["size"][2] >= z1 and c["origin"][1] + c["size"][1] == DECK_Y for c in hull), "deck slab"
    # ... and nothing rises above it inside the rectangle except the island (in its footprint) and flush straps
    ix0, ix1, iz0, iz1 = -ISLAND_RECT[1], -ISLAND_RECT[0], ISLAND_RECT[2], ISLAND_RECT[3]
    for b in bl:
        for c in b.get("cubes", []):
            lo, hi = world_bbox(c)
            if hi[1] <= DECK_Y + 1e-3:
                continue
            cx0, cx1, cz0, cz1 = max(lo[0], x0), min(hi[0], x1), max(lo[2], z0), min(hi[2], z1)
            if cx1 - cx0 <= 1e-3 or cz1 - cz0 <= 1e-3:
                continue                                              # wholly outside the deck rectangle
            if b["name"] == "cargo_straps":
                assert hi[1] <= DECK_Y + 0.5, c
                continue
            assert ix0 - 1e-3 <= cx0 and cx1 <= ix1 + 1e-3 and iz0 - 1e-3 <= cz0 and cz1 <= iz1 + 1e-3, \
                ("deck clutter above the flight deck", b["name"], lo, hi)
    for sx, sz in MX(HELO_SPOTS + TITAN_SPOTS):                           # spots on the deck, clear of the island
        assert x0 + 20 <= sx <= x1 - 20 and z0 + 20 <= sz <= z1 - 20
        assert not (ix0 - 30 < sx < ix1 + 30 and iz0 - 30 < sz < iz1 + 30), (sx, sz)
    return n


def main():
    B = apply_uv(bones())
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": "geometry.ocean_carrier", "texture_width": TEX, "texture_height": TEX,
                        # ~645 px long, 270 px wide incl. elevators, mast top at y=~265
                        "visible_bounds_width": 48, "visible_bounds_height": 20, "visible_bounds_offset": [0, 8, 0]},
        "bones": B}]}
    geo_path = f"{ASSETS}/geo/ocean_carrier.geo.json"
    anim_path = f"{ASSETS}/animations/ocean_carrier.animation.json"
    anim = animation(anim_path)
    n = validate(json.loads(json.dumps(geo)), anim)
    with open(geo_path, "w") as f:
        json.dump(geo, f, indent=1)
    t = TextureDrawer(TEX, TEX)
    paint(t)
    t.save(f"{ASSETS}/textures/entity/transport/ocean_carrier.png")
    item_icon(f"{ASSETS}/textures/item/ocean_carrier.png")
    print("cubes:", n, "bones:", [b["name"] for b in B])
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        osp.TEX = TEX
        tex = [[tuple(t.buf[(y * TEX + x) * 4:(y * TEX + x) * 4 + 4]) for x in range(TEX)] for y in range(TEX)]
        a = osp.render(B, tex, {}, 35, -22, W=1100, H=560, scale=1.35)
        b = osp.render(B, tex, {}, -140, -28, W=1100, H=560, scale=1.35)
        c = osp.render(B, tex, {}, 90, 0, W=1100, H=420, scale=1.6)
        osp.save_png(out + "_views.png", [row[::-1] for row in a + b + c])   # rasterizer is mirror-imaged vs the game
        top = osp.render(B, tex, {}, 90, -90, W=1100, H=780, scale=1.6)
        osp.save_png(out + "_top.png", [row[::-1] for row in top])
        print("preview", out)


if __name__ == "__main__":
    main()
