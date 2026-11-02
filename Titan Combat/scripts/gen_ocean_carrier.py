#!/usr/bin/env python3
"""Oceanic Super-Carrier (LHD-style amphibious assault ship): geo, animation, entity texture, item icon, preview.

Model convention: bow at model -Z (renderer turns 180 deg; Java +Z offsets land at model -Z), Y = 0 is the keel.
Java ties these numbers down:
  * flight deck surface y = 30 (BAY offsets y = 30/16) with titan spots at model (0, 30, 5) and (0, 30, 52);
  * bridge helm seat at model (26, 52.8, -38) (BRIDGE_HELM_OFFSET, y = 64/16 - 0.7);
  * buoyancy holds the waterline at 0.40 block = y 6.4, so the red antifouling ends there.
Big surfaces use planar UVs: a face samples its material region at its world position, so the deck markings,
hull number and porthole rows line up across neighbouring cubes.
Run from the project root:  python3 scripts/gen_ocean_carrier.py [--preview out.png]
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_transport_assets import TextureDrawer  # noqa: E402
from gen_v22_osprey import render, save_png  # noqa: E402

ASSETS = "src/main/resources/assets/titancombat"
TEX = 512
DECK_Y = 30
WATER_Y = 6.4

# material -> (u, v, w, h, x_ref, y_top_ref, z_ref): planar projection anchors (world coords at region origin)
MAT = {
    "deck":   (0, 0, 112, 240, -56, 0, -120),     # flight deck, painted 1:1 with markings
    "side":   (112, 0, 240, 32, -120, 30, -120),  # hull side (east face uses the copy at v+32): grey / portholes / boot-top / red, hull number
    "grey":   (352, 0, 64, 64, 0, 0, 0),          # superstructure haze grey, panel seams, rust
    "grey2":  (416, 0, 64, 64, 0, 0, 0),          # slightly darker grey (shadowed recesses, stacks)
    "win":    (352, 64, 64, 16, 0, 0, 0),         # bridge glass: alpha-0 panes with mullions
    "port":   (352, 80, 64, 16, 0, 0, 0),         # superstructure porthole/door band
    "grate":  (416, 64, 64, 16, 0, 0, 0),         # catwalk grating
    "gate":   (480, 0, 32, 32, 0, 0, 0),          # stern gate ribs
    "array":  (480, 32, 32, 32, 0, 0, 0),         # radar face grid
    "dome":   (416, 80, 32, 16, 0, 0, 0),         # white radome
    "dark":   (448, 80, 16, 16, 0, 0, 0),
    "metal":  (464, 80, 16, 16, 0, 0, 0),
    "soot":   (480, 64, 32, 32, 0, 0, 0),         # funnel top
    "red":    (496, 96, 8, 8, 0, 0, 0),
    "white":  (504, 96, 8, 8, 0, 0, 0),
    "yellow": (496, 104, 8, 8, 0, 0, 0),
    "green":  (504, 104, 8, 8, 0, 0, 0),
    "black":  (480, 96, 16, 16, 0, 0, 0),
    "seat":   (352, 96, 16, 16, 0, 0, 0),
    "screen": (368, 96, 16, 16, 0, 0, 0),
    "raft":   (384, 96, 32, 16, 0, 0, 0),         # white life-raft canister rows
    "bootred": (416, 96, 16, 16, 0, 0, 0),        # antifouling red for underwater fittings
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
    """Waterline-ish half beam along the ship: fine bow entry at -Z, full stern."""
    if z < -70:
        t = (-70 - z) / 46.0                       # 0 at z=-70 .. 1 at z=-116
        return max(1.5, 38 * (1 - t ** 1.6))
    return 38


def hull_cubes():
    C = []
    # parallel midbody: stepped slabs give a rounded bilge and flared topsides
    for y0, y1, hw in ((0, 2, 26), (2, 4, 33), (4, 8, 37), (8, 22, 38), (22, 26, 40), (26, 28, 42)):
        C.append(box(-hw, y0, -70, hw, y1, 102, "side"))
    # bow: 2-px slices that narrow and rake up the stem (cutwater climbs forward)
    for i in range(23):
        z1 = -70 - i * 2
        z0 = z1 - 2
        t = i / 22.0
        keel = 22 * t ** 2.5                        # stem rake
        for y0, y1, k in ((keel, 8, 1.0), (max(keel, 8), 22, 1.04), (max(keel, 22), 28, 1.12)):
            if y1 - y0 < 0.3:
                continue
            hw = half_width(z0 + 1) * k + (1.5 if y0 >= 22 else 0)
            C.append(box(-hw, y0, z0, hw, y1, z1, "side"))
    # flight deck: rectangular aft, tapering bow overhang, gallery deck edge below the lip
    C.append(box(-46, 28, -96, 46, DECK_Y, 106, "deck"))
    for i in range(9):
        z1 = -96 - i * 2.5
        hw = 46 - (i + 1) ** 1.55 * 1.4
        C.append(box(-hw, 28, z1 - 2.5, hw, DECK_Y, z1, "deck"))
    C += both(box(42, 25, -92, 46, 28, 100, "grey2"))                     # flare under deck edge
    # stern: transom, well-deck gate recess, flaps
    C += [box(-38, 6, 102, 38, 28, 104, "side"), box(-17, 6, 104, 17, 7, 106, "dark")]
    C += both(box(17, 6, 104, 20, 27, 106, "grey2"))
    # catwalk galleries along the deck edge with rails and life-raft canisters
    for z0, z1 in ((-84, -40), (-30, 2), (40, 80), (86, 100)):
        C += both(box(46, 27, z0, 49, 27.6, z1, "grate"), box(48.6, 27.6, z0, 49, 29.4, z1, "metal"),
                  box(44, 25, z0 + 2, 47, 27, z1 - 2, "raft"))
    # deck-edge aircraft elevator (port side, opposite the island) and aft starboard elevator
    C += [box(-58, 28.2, 22, -46, DECK_Y - 0.2, 44, "deck"), box(-58, 24, 30, -46, 28.2, 32, "grey2"),
          box(-58.4, 28, 22, -58, 29.6, 44, "metal")]
    C += [box(46, 28.2, 60, 56, DECK_Y - 0.2, 80, "deck"), box(46, 24, 68, 56, 28.2, 70, "grey2"),
          box(56, 28, 60, 56.4, 29.6, 80, "metal")]
    # sponsons for close-in weapons (bow port, stern starboard, stern port)
    for sx, sz in ((-44, -88), (40, 96), (-40, 96)):
        C += [box(sx - 6, 22, sz - 6, sx + 6, 28, sz + 6, "grey"), box(sx - 5, 21, sz - 5, sx + 5, 22, sz + 5, "grey2")]
    # anchors + hawse pipes either side of the stem
    C += both(box(28.6, 18, -88, 30.4, 21, -84, "dark"), box(29.4, 13, -87.5, 30.6, 18, -84.5, "metal"),
              box(29.4, 12, -89, 30.6, 13, -83, "metal"))
    # boot-top / waterline realism fittings below the waterline: sonar bulb, bilge keels, rudders, shafts, screws
    C += [box(-4, 0.5, -98, 4, 7, -84, "bootred"), box(-3, 1.5, -102, 3, 6, -98, "bootred")]
    C += both(box(33, 2, -40, 36, 3, 40, "bootred"),
              box(12, -3, 88, 14, 4, 98, "bootred"),
              box(12.4, -2, 60, 13.6, -0.6, 90, "metal"),
              box(9.5, -4.5, 84, 15.5, 1.5, 85, "metal", pivot=[12.5, -1.5, 84.5], rotation=[0, 0, 0]),
              box(9.5, -4.5, 84, 15.5, 1.5, 85, "metal", pivot=[12.5, -1.5, 84.5], rotation=[0, 0, 60]),
              box(9.5, -4.5, 84, 15.5, 1.5, 85, "metal", pivot=[12.5, -1.5, 84.5], rotation=[0, 0, -60]),
              box(11, 0, 60, 15, 2, 74, "bootred"))
    # foredeck fittings below the overhang: bitts, jackstaff, deck lights strip
    C += [box(-0.3, DECK_Y, -116, 0.3, 40, -115.4, "metal"),
          box(-1, DECK_Y, 104.6, 1, DECK_Y + 0.6, 105.6, "white")]
    C += both(box(30, DECK_Y, -108, 31.5, DECK_Y + 1.5, -106.5, "metal"))
    # deck-edge folding whip antennas + deck edge lights
    for z in (-60, -20, 50, 90):
        C += both(box(49, 28, z, 49.6, 44, z + 0.6, "dark", pivot=[49.3, 28, z], rotation=[0, 0, -20]))
    for z in range(-90, 104, 12):
        C += both(box(45, DECK_Y, z, 45.8, DECK_Y + 0.4, z + 0.8, "green" if z < 0 else "white"))
    # navigation lights at the stern + bow
    C += [box(41, 28, -96, 42, 29, -95, "green"), box(-42, 28, -96, -41, 29, -95, "red")]
    # CIWS turrets on the sponsons (white radome, grey mount, barrel cluster) + RAM launcher stern port
    C += ciws(-44, 28, -88, -1) + ciws(40, 28, 96, 1)
    C += [box(-45, 28, 91, -35, 30, 101, "grey"), box(-44, 30, 93, -36, 37, 99, "grey2"),
          box(-43.5, 31, 92.6, -36.5, 36, 93, "array")]
    return C


def ciws(x, y, z, face):
    """Phalanx: pedestal, gun body, tall white radome, barrel pointing outboard-forward."""
    out = cyl(x, z, y, y + 3, 3.5, "grey")
    out += [box(x - 3, y + 3, z - 3.5, x + 3, y + 8, z + 3.5, "grey"),
            box(x - 2.5, y + 8, z - 3, x + 2.5, y + 13, z + 3, "dome"),
            box(x - 2, y + 13, z - 2.5, x + 2, y + 15, z + 2.5, "dome"),
            box(x - 1.2, y + 15, z - 1.5, x + 1.2, y + 16, z + 1.5, "dome"),
            box(x - 1, y + 4.5, z - 13, x + 1, y + 6.5, z - 3.5, "dark"),
            box(x - 1.6, y + 4, z - 6, x + 1.6, y + 7, z - 3.5, "metal")]
    return out


# ---------------------------------------------------------------------------- island
def island_cubes():
    C = []
    # main block on the flight deck: two tiers of offices and hangar-top spaces
    C += [box(22, DECK_Y, -70, 44, 44, -14, "grey"), box(22, 44, -66, 44, 52, -20, "grey"),
          box(21.6, 33, -70, 22, 42, -14, "port"), box(21.6, 45, -66, 22, 51, -20, "port")]
    C += [box(23, DECK_Y, -14, 43, 40, -8, "grey2")]                     # aft step (fuel / stores)
    # bridge level (hollow, glazed): floor at y=52, helm seat at (26, 52.8, -38)
    floor_y, roof_y = 52, 76
    x0, x1, z0, z1 = 20, 46, -64, -30
    C += [box(x0, floor_y - 0.8, z0, x1, floor_y, z1, "grey2"),
          box(x0, roof_y, z0 - 1.5, x1, roof_y + 2, z1, "grey"),          # roof with brow over the glass
          box(x0, floor_y, z0, x1, 59, z0 + 0.8, "grey"),                 # forward bulkhead below glass
          box(x0, floor_y, z0, x0 + 0.8, 59, z1, "grey"),                 # inboard bulkhead below glass
          box(x1 - 0.8, floor_y, z0, x1, roof_y, z1, "grey"),             # outboard wall solid
          box(x0, floor_y, z1 - 0.8, x1, roof_y, z1, "grey"),             # aft wall
          box(x0, 59, z0, x1, 60, z0 + 1, "grey2"), box(x0, 59, z0, x0 + 1, 60, z1, "grey2"),
          box(x0, 74, z0, x1, roof_y, z0 + 1, "grey2"), box(x0, 74, z0, x0 + 1, roof_y, z1, "grey2"),
          box(x0 + 0.2, 60, z0 + 0.2, x1 - 1, 74, z0 + 0.6, "win"),       # forward glass (alpha 0 panes)
          box(x0 + 0.2, 60, z0 + 1, x0 + 0.6, 74, z1 - 1, "win")]          # inboard glass facing the deck
    for x in (27, 33, 39):
        C.append(box(x - 0.5, 60, z0, x + 0.5, 74, z0 + 1, "grey2"))      # mullions
    for z in (-56, -48, -40):
        C.append(box(x0, 60, z - 0.5, x0 + 1, 74, z + 0.5, "grey2"))
    # helm: chair, binnacle console, overhead screens
    C += [box(23, 52, -41, 29, 55, -35, "seat"), box(23, 55, -35, 29, 64, -34, "seat"),
          box(23, 55, -41, 23.8, 57, -36, "seat"), box(28.2, 55, -41, 29, 57, -36, "seat"),
          box(23, 52, -50, 29, 57, -46, "dark"), box(23.5, 57, -50, 28.5, 57.4, -47, "screen"),
          box(30, 52, -62, 44, 57, -58, "dark"), box(30.5, 57, -62, 43.5, 57.3, -59, "screen")]
    # bridge wings (both ends, open) with pelorus stands
    C += [box(12, 51, -62, 20, 52, -54, "grey"), box(12, 52, -62, 12.4, 55, -54, "metal"),
          box(12, 52, -62, 20, 55, -61.6, "metal"),
          box(46, 51, -62, 52, 52, -54, "grey"), box(51.6, 52, -62, 52, 55, -54, "metal")]
    # primary flight control: glazed box overhanging the deck, aft of the bridge
    C += [box(18, 62, -28, 30, 74, -16, "grey"), box(17.6, 64, -27, 18, 72, -17, "win"),
          box(18, 64, -16.4, 30, 72, -16, "win"), box(18, 74, -28, 30, 75, -16, "grey2"),
          box(30, 44, -28, 44, 74, -14, "grey")]
    # twin stacks (LHD style) with soot caps and exhaust grilles
    for zc in (-24, -12):
        C += [box(32, 74, zc - 5, 44, 86, zc + 3, "grey2"), box(32.6, 86, zc - 4.4, 43.4, 86.6, zc + 2.4, "soot"),
              box(33, 86, zc - 4, 36, 88, zc + 2, "dark"), box(39, 86, zc - 4, 42, 88, zc + 2, "dark")]
    C += [box(30, 40, -14, 44, 74, -8, "grey2")]
    # upper deck above the bridge: navigation radar platform, signal lamps
    C += [box(24, 78, -60, 44, 84, -36, "grey"), box(23.6, 79, -58, 24, 83, -38, "port"),
          box(27, 84, -54, 41, 86, -40, "grey2")]
    # lattice mast: four tilted legs, cross bracing, platforms, yardarm
    for lx, lz in ((28, -52), (40, -52), (28, -42), (40, -42)):
        C.append(box(lx - 0.7, 86, lz - 0.7, lx + 0.7, 112, lz + 0.7, "metal",
                     pivot=[lx, 86, lz], rotation=[(lz + 47) * 1.1, 0, -(lx - 34) * 1.0]))
    for y in (92, 98, 104):
        C += [box(28, y, -52, 40, y + 0.6, -51.4, "metal"), box(28, y, -42.6, 40, y + 0.6, -42, "metal"),
              box(28, y, -52, 28.6, y + 0.6, -42, "metal"), box(39.4, y, -52, 40, y + 0.6, -42, "metal")]
    C += [box(26, 106, -52, 42, 107, -42, "grate"), box(14, 108, -47.5, 54, 109, -46.5, "metal"),
          box(33.4, 107, -47.6, 34.6, 126, -46.4, "metal"), box(33, 126, -48, 35, 128, -46, "red")]
    for x in (16, 22, 46, 52):
        C.append(box(x - 0.2, 105, -47.2, x + 0.2, 108, -46.8, "dark"))   # signal halyard blocks
    # SATCOM and EW radomes on outriggers
    C += [box(42, 84, -34, 48, 85, -28, "grey2"), box(42.5, 85, -33.5, 47.5, 90, -28.5, "dome"),
          box(43.5, 90, -32.5, 46.5, 91.5, -29.5, "dome"),
          box(22, 84, -34, 28, 85, -28, "grey2"), box(22.5, 85, -33.5, 27.5, 89, -28.5, "dome"),
          box(23.5, 89, -32.5, 26.5, 90, -29.5, "dome")]
    # ECM blisters and side fixed arrays on the island face
    C += [box(44, 58, -40, 47, 66, -34, "grey2"), box(46.6, 59, -39, 47, 65, -35, "array"),
          box(19, 40, -50, 22, 48, -44, "grey2"), box(18.6, 41, -49, 19, 47, -45, "array")]
    # island-top CIWS aft
    C += ciws(37, 86, -6, 1)
    C += [box(31, 74, -8, 44, 86, -2, "grey")]
    # ladders and doors on the island deck face
    C += [box(21.4, DECK_Y, -30, 22, 40, -26, "dark"), box(21.4, DECK_Y, -58, 22, 40, -54, "dark")]
    return C


def radar_cubes():
    """SPS-48 style 3-D array: big tilted planar face on a pedestal, spinning about Y at the mast head."""
    px, py, pz = 34, 112, -47
    return [box(px - 2, py, pz - 2, px + 2, py + 2, pz + 2, "metal"),
            box(px - 11, py + 2, pz - 1.5, px + 11, py + 16, pz + 0.5, "array", pivot=[px, py + 2, pz], rotation=[-12, 0, 0]),
            box(px - 11.5, py + 1.5, pz + 0.5, px + 11.5, py + 16.5, pz + 1.5, "grey2", pivot=[px, py + 2, pz], rotation=[-12, 0, 0]),
            box(px - 9, py + 16.5, pz - 1, px + 9, py + 18, pz + 1, "metal", pivot=[px, py + 2, pz], rotation=[-12, 0, 0])]


def radar_aux_cubes():
    """Long-range air search: wide shallow bar on the forward platform."""
    px, py, pz = 34, 86, -60
    return [box(px - 1, py, pz - 1, px + 1, py + 3, pz + 1, "metal"),
            box(px - 9, py + 3, pz - 1, px + 9, py + 6, pz + 0.4, "array"),
            box(px - 9, py + 3, pz + 0.4, px + 9, py + 6, pz + 1, "grey2")]


def strap_cubes():
    """Deck tie-down chains + titan spot outline at both cargo slots (y just above the deck)."""
    out = []
    for z in (5, 52):
        for dx, dz in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            out.append(box(dx * 10 - 0.4, DECK_Y, z + dz * 10 - 0.4, dx * 10 + 0.4, DECK_Y + 0.3, z + dz * 10 + 0.4,
                           "metal"))
            out.append(box(dx * 4, DECK_Y, z + dz * 4 - 0.25, dx * 10, DECK_Y + 0.2, z + dz * 4 + 0.25, "yellow"))
    return out


def gate_cubes():
    return [box(-16, 6, 104, 16, 27, 105.4, "gate"), box(-16.4, 26, 104, 16.4, 27.6, 105.6, "grey2"),
            box(-14, 7, 105.4, -12, 26, 106, "metal"), box(12, 7, 105.4, 14, 26, 106, "metal")]


def bones():
    return [
        {"name": "root", "pivot": [0, 0, 0]},
        {"name": "hull", "parent": "root", "pivot": [0, WATER_Y, 0], "cubes": hull_cubes()},
        {"name": "stern_gate", "parent": "hull", "pivot": [0, 6, 105], "cubes": gate_cubes()},
        {"name": "bridge", "parent": "hull", "pivot": [33, DECK_Y, -40], "cubes": island_cubes()},
        {"name": "radar", "parent": "bridge", "pivot": [34, 112, -47], "cubes": radar_cubes()},
        {"name": "radar_aux", "parent": "bridge", "pivot": [34, 86, -60], "cubes": radar_aux_cubes()},
        {"name": "cargo_straps", "parent": "hull", "pivot": [0, DECK_Y, 28], "cubes": strap_cubes()},
    ]


# ---------------------------------------------------------------------------- planar UVs
FACE_AXES = {  # face -> (u axis, u reversed, v axis "y-down" or z, v reversed)
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
                us = hi[ua] - lo[ua]
                vs = hi[va] - lo[va]
                us_c, vs_c = min(us, rw), min(vs, rh)
                su = (refs[ua] + rw - hi[ua]) if rev else (lo[ua] - refs[ua])
                sv = (ytop - hi[1]) if va == 1 else (lo[2] - zr if f == "up" else lo[2] - zr)
                su = su % rw if su + us_c > rw or su < 0 else su
                sv = sv % rh if sv + vs_c > rh or sv < 0 else sv
                su, sv = min(su, rw - us_c), min(sv, rh - vs_c)
                ev = 32 if (mat == "side" and f == "east") else 0   # east side has its own hull-number copy
                c["uv"][f] = {"uv": [round(u0 + su, 3), round(v0 + ev + sv, 3)], "uv_size": [round(us_c, 3), round(vs_c, 3)]}
    return B


# ---------------------------------------------------------------------------- texture
FONT = {
    "0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"], "9": ["111", "101", "111", "001", "111"]}


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def paint(t):
    rnd = random.Random(9)
    px = t.set_pixel

    def text(x, y, s, col, sc=2):
        for i, ch in enumerate(s):
            for gy, row in enumerate(FONT[ch]):
                for gx, bit in enumerate(row):
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

    # --- flight deck (u = x + 56, v = z + 120): dark non-skid, markings
    du, dv = MAT["deck"][:2]
    for y in range(240):
        for x in range(112):
            k = 1 + rnd.uniform(-0.06, 0.06) - (0.05 if (x * 31 + y * 17) % 23 == 0 else 0)
            px(du + x, dv + y, *shade((62, 64, 68), k))
    for y in range(0, 240, 16):                                       # non-skid panel joins
        t.fill_rect(du, dv + y, 112, 1, 52, 54, 58)

    def dx(x):
        return du + x + 56

    def dz(z):
        return dv + z + 120

    for z in range(-112, 106, 6):                                     # dashed yellow centreline (port of island)
        t.fill_rect(dx(-1), dz(z), 2, 4, 214, 182, 58)
    t.fill_rect(dx(-42), dz(-98), 1, 202, 226, 228, 226)              # white deck edge lines
    t.fill_rect(dx(41), dz(-98), 1, 202, 226, 228, 226)
    for i, zc in enumerate((-80, -50, -18, 14, 46, 78)):               # landing spots: yellow circle, white T, number
        cx = -22
        for a in range(0, 360, 4):
            r = 9
            t.fill_rect(dx(cx + int(r * math.cos(math.radians(a)))), dz(zc + int(r * math.sin(math.radians(a)))), 1, 1,
                        222, 188, 60)
        t.fill_rect(dx(cx - 5), dz(zc - 11), 11, 1, 230, 230, 228)
        text(dx(cx - 13), dz(zc - 2), str(i + 1), (236, 236, 232), 1)
    for zc in (5, 52):                                                # titan spots: big yellow box + cross
        for x in range(-16, 17):
            for z in (-16, 16):
                t.fill_rect(dx(x), dz(zc + z), 1, 1, 222, 188, 60)
                t.fill_rect(dx(z), dz(zc + x), 1, 1, 222, 188, 60)
        t.fill_rect(dx(-6), dz(zc), 13, 1, 232, 232, 230)
        t.fill_rect(dx(0), dz(zc - 6), 1, 13, 232, 232, 230)
    for x in range(-40, 41, 8):                                       # stern ramp hash (red/white)
        t.fill_rect(dx(x), dz(100), 4, 3, 190, 60, 50)
        t.fill_rect(dx(x + 4), dz(100), 4, 3, 226, 226, 222)
    for x0, z0, w, h in ((-46, 22, 12, 22), (34, 60, 12, 20)):        # elevator outlines
        for x in range(w):
            t.fill_rect(dx(x0 + x), dz(z0), 1, 1, 214, 182, 58)
            t.fill_rect(dx(x0 + x), dz(z0 + h - 1), 1, 1, 214, 182, 58)
    text(dx(-14), dz(-104), "7", (236, 236, 232), 3)                  # big bow hull number on the deck
    text(dx(-2), dz(-104), "7", (236, 236, 232), 3)
    for _ in range(140):                                              # tyre / oil smudges
        x, y = rnd.randrange(112), rnd.randrange(240)
        px(du + x, dv + y, 44, 45, 48)

    # --- hull side (u = z + 120 forward->aft on the west face, v = 30 - y)
    su, sv0 = MAT["side"][:2]
    for sv in (sv0, sv0 + 32):
        plate(su, sv, 240, 32, GREY, 20, 8, 0.25)
        for y in range(32):
            yy = 30 - y - 0.5
            for x in range(240):
                if yy < WATER_Y:
                    k = 1 + rnd.uniform(-0.04, 0.04)
                    px(su + x, sv + y, *shade((150, 44, 36), k))          # antifouling red
                elif yy < WATER_Y + 2.5:
                    px(su + x, sv + y, *shade((44, 46, 50), 1 + rnd.uniform(-0.05, 0.05)))   # black boot-top
                elif yy < WATER_Y + 4.5:
                    px(su + x, sv + y, *shade(GREY, 0.82 + rnd.uniform(-0.05, 0.05)))      # sea-stained band
        for x in range(10, 232, 7):                                       # porthole row
            t.fill_rect(su + x, sv + 7, 2, 2, 40, 44, 52)
            t.set_pixel(su + x, sv + 7, 120, 140, 160)
        for x in range(40, 200, 23):                                      # rust weeping from hawse/scuppers
            for y in range(9, 20):
                if rnd.random() < 0.8:
                    px(su + x, sv + y, 150, 98, 70)
        # hull number near the bow: west face reads bow at small u, east face (v+32) at large u
        text(su + (24 if sv == sv0 else 194), sv + 4, "47", (44, 46, 50), 3)

    # --- superstructure greys
    plate(*MAT["grey"][:2], 64, 64, GREY, 16, 12, 0.2)
    plate(*MAT["grey2"][:2], 64, 64, shade(GREY, 0.86), 16, 12, 0.3)
    wu, wv = MAT["win"][:2]                                           # alpha-0 glass, dark gasket mullions
    for y in range(16):
        for x in range(64):
            if y in (0, 15) or x % 8 == 0:
                px(wu + x, wv + y, 50, 54, 60)
            else:
                px(wu + x, wv + y, 0, 0, 0, 0)
    pu, pv = MAT["port"][:2]
    plate(pu, pv, 64, 16, GREY, 64, 16, 0)
    for x in range(3, 64, 8):
        t.fill_rect(pu + x, pv + 5, 3, 3, 40, 44, 52)
        px(pu + x, pv + 5, 130, 150, 170)
    t.fill_rect(pu + 28, pv + 3, 6, 12, 150, 156, 162)                # watertight door
    gu, gv = MAT["grate"][:2]
    for y in range(16):
        for x in range(64):
            px(gu + x, gv + y, *((70, 72, 76) if (x % 3 == 0 or y % 3 == 0) else (36, 38, 40)))
    gu, gv = MAT["gate"][:2]
    plate(gu, gv, 32, 32, shade(GREY, 0.92), 32, 4, 0.4)
    t.fill_rect(gu, gv + 28, 32, 4, 190, 160, 50)
    au, av = MAT["array"][:2]
    for y in range(32):
        for x in range(32):
            px(au + x, av + y, *((92, 98, 104) if (x % 4 == 0 or y % 4 == 0) else (150, 156, 162)))
    mu, mv = MAT["dome"][:2]
    for y in range(16):
        for x in range(32):
            px(mu + x, mv + y, *shade((236, 236, 230), 1 - y * 0.01 + rnd.uniform(-0.02, 0.02)))
    t.fill_rect(*MAT["dark"][:2], 16, 16, 40, 42, 46)
    for y in range(16):
        for x in range(16):
            px(MAT["metal"][0] + x, MAT["metal"][1] + y, *shade((150, 154, 158), 0.9 + 0.15 * ((x + y) % 3 == 0)))
            px(MAT["seat"][0] + x, MAT["seat"][1] + y, 60, 66, 76)
            px(MAT["screen"][0] + x, MAT["screen"][1] + y, *((60, 200, 120) if (y % 3 == 0 and x % 5) else (20, 40, 34)))
            px(MAT["black"][0] + x, MAT["black"][1] + y, 30, 30, 32)
            px(MAT["bootred"][0] + x, MAT["bootred"][1] + y, *shade((150, 44, 36), 1 + rnd.uniform(-0.05, 0.05)))
    su2, sv2 = MAT["soot"][:2]
    for y in range(32):
        for x in range(32):
            px(su2 + x, sv2 + y, *shade((52, 50, 48), 0.8 + rnd.uniform(0, 0.4)))
    ru, rv = MAT["raft"][:2]
    for y in range(16):
        for x in range(32):
            px(ru + x, rv + y, *((210, 212, 206) if x % 4 else (120, 124, 126)))
    for name, col in (("red", (200, 40, 36)), ("white", (236, 236, 228)), ("yellow", (222, 188, 60)),
                      ("green", (40, 190, 70))):
        t.fill_rect(*MAT[name][:2], 8, 8, *col)


def item_icon(path):
    """16x16 side profile: grey hull on red bottom, island + mast amidships, flat deck."""
    t = TextureDrawer(16, 16)
    g, d, r, k = (176, 182, 188), (120, 126, 132), (150, 44, 36), (44, 46, 50)
    for x in range(0, 16):
        t.set_pixel(x, 8, *d)                                   # deck
    for x in range(1, 16):
        t.set_pixel(x, 9, *g)
        t.set_pixel(x, 10, *g)
    for x in range(2, 15):
        t.set_pixel(x, 11, *k)
        t.set_pixel(x, 12, *r)
    t.set_pixel(0, 9, *g)
    for y in range(4, 8):
        for x in range(6, 10):
            t.set_pixel(x, y, *g)
    t.set_pixel(7, 5, 60, 80, 100)
    t.set_pixel(8, 5, 60, 80, 100)
    for y in range(1, 4):
        t.set_pixel(8, y, *d)
    t.set_pixel(7, 1, *d)
    t.set_pixel(9, 1, *d)
    for x in (3, 6, 11, 13):
        t.set_pixel(x, 10, 40, 44, 52)
    t.save(path)


def animation(path):
    spin = lambda length, deg: {"rotation": {"0.0": [0, 0, 0], str(length): [0, deg, 0]}}
    anim = {"format_version": "1.8.0", "animations": {
        "animation.ocean_carrier.idle": {"loop": True, "animation_length": 6.0, "bones": {
            "hull": {"position": {"0.0": [0, 0, 0], "3.0": [0, -0.5, 0], "6.0": [0, 0, 0]},
                     "rotation": {"0.0": [0, 0, 0], "1.5": [0.4, 0, 0.7], "3.0": [0, 0, 0], "4.5": [-0.4, 0, -0.7],
                                  "6.0": [0, 0, 0]}},
            "radar": spin(6.0, -360), "radar_aux": spin(3.0, 360)}},
        "animation.ocean_carrier.sail": {"loop": True, "animation_length": 3.0, "bones": {
            "hull": {"position": {"0.0": [0, 0, 0], "1.5": [0, -0.8, 0], "3.0": [0, 0, 0]},
                     "rotation": {"0.0": [-0.6, 0, 0], "0.75": [0.4, 0, 1.0], "1.5": [0.8, 0, 0],
                                  "2.25": [0.2, 0, -1.0], "3.0": [-0.6, 0, 0]}},
            "radar": spin(3.0, -360), "radar_aux": spin(1.5, 360)}}}}
    with open(path, "w") as f:
        json.dump(anim, f, indent=2)
    return anim


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
    assert {"hull", "cargo_straps", "radar", "bridge"} <= names
    assert set(anim["animations"]) == {"animation.ocean_carrier.idle", "animation.ocean_carrier.sail"}
    for a in anim["animations"].values():
        assert set(a["bones"]) <= names, set(a["bones"]) - names
    deck = [c for c in next(b for b in bl if b["name"] == "hull")["cubes"]
            if c["origin"][1] + c["size"][1] == DECK_Y and c["size"][0] > 80]
    assert deck, "flight deck must top out at y=30 to match the Java cargo offsets"
    return n


def main():
    B = apply_uv(bones())
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": "geometry.ocean_carrier", "texture_width": TEX, "texture_height": TEX,
                        # ~232 px long, mast top at y=130, keel/screws to y=-6
                        "visible_bounds_width": 16, "visible_bounds_height": 9, "visible_bounds_offset": [0, 4, 0]},
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
        tex = [[tuple(t.buf[(y * TEX + x) * 4:(y * TEX + x) * 4 + 4]) for x in range(TEX)] for y in range(TEX)]
        a = render(B, tex, {}, 35, -22, W=760, H=440, scale=2.2)
        b = render(B, tex, {}, -140, -28, W=760, H=440, scale=2.2)
        c = render(B, tex, {}, 90, 0, W=760, H=440, scale=2.6)
        save_png(out, [row[::-1] for row in a + b + c])   # rasterizer is mirror-imaged vs the game
        print("preview", out)


if __name__ == "__main__":
    main()
