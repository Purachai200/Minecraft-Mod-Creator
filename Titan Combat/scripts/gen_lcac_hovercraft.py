#!/usr/bin/env python3
"""LCAC (Landing Craft Air Cushion) hovercraft: geo, animation, entity texture, item icon, preview.

Model space: bow at model -Z (= entity-local +Z in Java), +X = vehicle left/port (GeckoLib mirrors X). 16 px = 1 block.
Deck top y22 (x -32..32, z -82..78). Cargo slots at model z -36 and +30. Driver cushion top y56 at (x-44, z-60).
Run: python3 scripts/gen_lcac_hovercraft.py [--preview out.png]
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_transport_assets import TextureDrawer, make_png, rod, write_geo  # noqa: E402
from gen_armored_apc import h, smooth, box, mirror, both, preview  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources", "assets", "titancombat")
KEY = "lcac_hovercraft"

# ---- 64px material cells ----
PAINT, SALT, PANEL, DECK, HAZARD, STENCIL, GRILLE, STEEL = [[i * 64, 0] for i in range(8)]
RUBBER, FINGER, GLASS, LENS, RED, GREEN, AMBER, DARK = [[i * 64, 64] for i in range(8)]
CHAIN, YELLOW, SEAT, WHITE, BLADE, WALK, GRIME, INSTR = [[i * 64, 128] for i in range(8)]

BASE = (180, 184, 186)  # light haze grey so a faction tint multiplies cleanly


def paint_texture():
    t = TextureDrawer(512, 512)
    px = lambda x, y, c, a=255: t.set_pixel(x, y, c[0], c[1], c[2], a)
    add = lambda c, d: tuple(v + d for v in c)
    mix = lambda a, b, k: tuple(a[i] * (1 - k) + b[i] * k for i in range(3))

    def paint(u, v, base, seam=0, s=1, salt=0.0, grime=0.0):
        for y in range(64):
            for x in range(64):
                c = add(base, (smooth(x, y, s) - 0.5) * 12 + (h(x, y, s + 9) - 0.5) * 5)
                st = h(x, 0, s + 3)
                if st > 0.78:  # rust/grime streaks running down from fittings
                    c = mix(c, (120, 104, 88), min(0.5, (st - 0.78) * 3) * (1 - y / 80) * (1 + grime))
                if salt and smooth(x, y * 0.3, s + 4, 5) > 1 - salt:  # white salt crust bands
                    c = mix(c, (226, 226, 218), 0.45)
                if grime and y > 40:
                    c = mix(c, (96, 92, 84), grime * (y - 40) / 24 * smooth(x, y, s + 6, 3))
                if h(x, y, s + 5) > 0.986:
                    c = add(c, -30)  # chips
                if x == 0 or y == 0:
                    c = add(c, 14)
                if seam:
                    lx, ly = x % seam, y % seam
                    if x and y and (lx == 0 or ly == 0):
                        c = add(c, -30)
                    elif x and y and (lx == 1 or ly == 1):
                        c = add(c, 8)
                    elif lx in (3, seam - 3) and ly in (3, seam - 3):
                        c = add(c, 24)
                px(u + x, v + y, c)

    paint(*PAINT, BASE, s=1, salt=0.25)
    paint(*SALT, add(BASE, -6), s=2, salt=0.45, grime=0.6)
    paint(*PANEL, BASE, seam=16, s=3, salt=0.2)
    paint(*STENCIL, BASE, seam=0, s=4)
    t.draw_text(STENCIL[0] + 4, STENCIL[1] + 2, "71", (30, 30, 32), 2)  # hull number, black on grey like the real craft
    paint(*GRIME, add(BASE, -24), s=5, grime=1.0)
    for y in range(64):
        for x in range(64):
            # non-skid dark deck; tie-down track lines every 16 texels in yellow
            g = (h(x, y, 11) > 0.5) * 10 + (h(x, y, 12) > 0.97) * 18
            dc = (58 + g, 60 + g, 62 + g)
            if x % 32 in (0, 1) or y % 32 in (0, 1):
                dc = (214, 178, 40) if h(x, y, 13) > 0.12 else (120, 110, 60)
            elif x % 32 == 16 and y % 32 == 16:
                dc = (150, 150, 150)  # flush tie-down ring
            px(DECK[0] + x, DECK[1] + y, dc)
            px(HAZARD[0] + x, HAZARD[1] + y, (226, 186, 30) if (x + y) // 4 % 2 else (24, 24, 24))
            px(GRILLE[0] + x, GRILLE[1] + y, add(BASE, -40) if (y % 3 == 0 or x % 3 == 0) else (30, 32, 34))
            px(STEEL[0] + x, STEEL[1] + y, add((110, 114, 118), (smooth(x, y, 14) - .5) * 14 + (x == 0 or y == 0) * 20))
            r = add((30, 30, 32), (h(x, y, 15) - .5) * 8 + (smooth(x, y, 16, 4) > 0.75) * 30)  # wet/salt sheen
            px(RUBBER[0] + x, RUBBER[1] + y, r)
            px(FINGER[0] + x, FINGER[1] + y, add(r, -12 if x % 6 == 0 else 0) if y < 58 else (70, 64, 56))
            t.set_pixel(GLASS[0] + x, GLASS[1] + y, 0, 0, 0, 0)
            px(LENS[0] + x, LENS[1] + y, (250, 246, 214))
            px(RED[0] + x, RED[1] + y, (210, 30, 26))
            px(GREEN[0] + x, GREEN[1] + y, (40, 200, 70))
            px(AMBER[0] + x, AMBER[1] + y, (250, 170, 34))
            px(DARK[0] + x, DARK[1] + y, add((34, 36, 38), (h(x, y, 17) - .5) * 6))
            px(CHAIN[0] + x, CHAIN[1] + y, (150, 150, 146) if (y % 4) < 3 else (60, 60, 58))
            px(YELLOW[0] + x, YELLOW[1] + y, add((222, 184, 40), (h(x, y, 18) - .5) * 14))
            px(SEAT[0] + x, SEAT[1] + y, add((52, 56, 50), (x % 8 == 0) * -10))
            px(WHITE[0] + x, WHITE[1] + y, add((236, 236, 230), (h(x, y, 19) - .5) * 8))
            px(BLADE[0] + x, BLADE[1] + y, (226, 186, 30) if y < 4 else add((44, 46, 48), (h(x, y, 20) - .5) * 8))
            px(WALK[0] + x, WALK[1] + y, add((96, 100, 102), ((x + y) % 4 == 0) * 16))
            ic = (20, 22, 24)
            if h(x // 3, y // 3, 21) > 0.7:
                ic = (60, 200, 120) if h(x, y, 22) > 0.5 else (230, 170, 40)
            px(INSTR[0] + x, INSTR[1] + y, ic)
    return t


# ---------------------------------------------------------------- geometry helpers
def ring(cx, cy, z0, depth, R, t, n, uv):
    """n-gon tube around the Z axis (duct shroud), outer apothem R, wall t."""
    L = round(2 * R * math.tan(math.pi / n) + 0.2, 3)
    return [{"origin": [cx - L / 2, cy + R - t, z0], "size": [L, t, depth], "pivot": [cx, cy, z0], "rotation": [0, 0, round(k * 360 / n, 3)], "uv": uv}
            for k in range(n)]


def cyl(cx, cy, z0, depth, r, uv):
    """Octagonal solid cylinder along Z."""
    w = round(2 * r * math.tan(math.pi / 8), 3)
    return [{"origin": [cx - w / 2, cy - r, z0], "size": [w, 2 * r, depth], "pivot": [cx, cy, z0], "rotation": [0, 0, a], "uv": uv}
            for a in (0, 45, 90, 135)]


def cylx(x0, cy, cz, length, r, uv):
    """Octagonal cylinder along X (life-raft canisters, hinge barrels)."""
    w = round(2 * r * math.tan(math.pi / 8), 3)
    return [{"origin": [x0, cy - r, cz - w / 2], "size": [length, 2 * r, w], "pivot": [x0, cy, cz], "rotation": [a, 0, 0], "uv": uv}
            for a in (0, 45, 90, 135)]


DECK_Y, SS_Y = 22, 46          # deck top, superstructure top
DUCT_X, DUCT_Y, DUCT_Z, DUCT_R = 37, 67, 66, 19


def hull():
    c = []
    # Buoyancy box (lower hull), bow & stern bevels, deck plate tiles with yellow tie-down tracks
    c += [box([-52, 6, -84], [104, 15, 166], SALT)]
    c += [rod((0, 6, -84), (0, 21, -88), 104, 3, SALT), rod((0, 6, 82), (0, 21, 85), 104, 3, SALT)]
    for x0 in (-32, 0):
        for k in range(5):
            c += [box([x0, 21, -82 + k * 32], [32, 1, 32], DECK)]
    c += [box([-32, 21, 78], [64, 1, 3], WALK), box([-32, 21, -84], [64, 1, 2], WALK)]
    # Deck curbs / scuppers along the inboard walls, bollards
    c += both(box([30, 22, -80], [2, 1.5, 158], HAZARD))
    c += both(*[box([27.5, 22, z], [2.5, 2.5, 2.5], STEEL) for z in (-74, -20, 30, 72)])
    # Side superstructures (port +X, starboard -X): main box + raked bow cap + upper bevel
    c += both(box([32, 22, -74], [22, 24, 146], PANEL))
    c += both(rod((43, 22, -74), (43, 46, -80), 22, 2, PANEL), box([32, 22, -80], [22, 6, 6], SALT))
    c += both(rod((54, 40, -1), (52, 46.5, -1), 1.5, 146, PAINT))           # outer upper chamfer
    c += both(box([32, 46, -72], [21, 0.5, 142], WALK))                     # non-skid walkway on top
    # Inboard faces: watertight doors, ladders, floodlights
    for z in (-56, 10, 50):
        c += both(box([31.6, 24, z], [0.6, 14, 7], DARK), box([31.2, 30, z + 5.5], [0.6, 1, 1], STEEL))
    c += both(*[box([31.4, 24 + k * 3, -64], [0.6, 0.6, 4], STEEL) for k in range(7)])
    c += both(box([31.4, 24, -64.5], [0.6, 22, 0.6], STEEL), box([31.4, 24, -60], [0.6, 22, 0.6], STEEL))
    c += both(*[box([31, 42, z], [1.2, 2, 2], LENS) for z in (-40, 0, 40)])
    # Outboard faces: lift-fan intake grilles, hull number, salt-streaked panels, life rafts
    for z0 in (-50, 14):
        c += both(box([54, 28, z0], [0.8, 12, 26], GRILLE), box([54, 27, z0 - 1], [1.6, 1, 28], STEEL),
                  box([54, 40, z0 - 1], [1.6, 1, 28], STEEL))
        c += both(*[box([54.2, 28, z0 + k * 6.5], [1.2, 12, 0.6], STEEL) for k in range(5)])
    c += both(box([54, 30, -20], [0.2, 10, 24], STENCIL))
    c += both(box([54, 22, 44], [0.4, 18, 26], SALT))
    for z in (-12, 0):
        c += both(*cyl(47, 49.5, z, 10, 3.5, WHITE))
        c += both(box([44, 46, z + 2], [6, 1, 1.5], STEEL), box([44, 46, z + 6.5], [6, 1, 1.5], STEEL))
    # Top: lift-fan intakes (raised housings with grilled tops) fore and aft on each side
    for zc in (-30, 28):
        c += both(box([34, 46, zc - 10], [18, 5, 20], PANEL), box([35, 51, zc - 9], [16, 0.6, 18], GRILLE))
        c += both(box([34, 51, zc - 10], [18, 1, 1], STEEL), box([34, 51, zc + 9], [18, 1, 1], STEEL),
                  box([34, 51, zc - 9], [1, 1, 18], STEEL), box([51, 51, zc - 9], [1, 1, 18], STEEL))
        c += both(*[box([35 + k * 4, 51.2, zc - 9], [0.6, 0.8, 18], STEEL) for k in range(1, 4)])
    # Bow thrusters (swivelling pods) on the forward superstructure tops
    c += both(box([39, 46, -49], [10, 3, 9], STEEL), box([40.5, 49, -48], [7, 5, 7], PANEL))
    c += both(*cyl(44, 58, -49, 12, 4.5, PANEL))
    c += both(*cyl(44, 58, -49.4, 0.6, 3.2, DARK))
    c += both(*ring(44, 58, -50, 1.5, 5, 1, 8, STEEL))
    # Gas-turbine exhausts angled outboard, aft of the intakes
    c += both(box([40, 46, 44], [10, 6, 10], PANEL), rod((45, 52, 49), (49, 58, 49), 7, 7, PANEL), box([46, 57, 45.5], [6, 1, 7], DARK))
    # Duct pylons up to the shrouds
    c += both(box([DUCT_X - 8, SS_Y, DUCT_Z + 2], [3, 4, 10], STEEL), box([DUCT_X + 5, SS_Y, DUCT_Z + 2], [3, 4, 10], STEEL))
    # Railings: stanchions + rail along the outer top edge and bow corners
    for z in range(-70, 64, 12):
        c += both(box([52, 46.5, z], [0.7, 8, 0.7], STEEL))
    c += both(box([52, 54, -70], [0.7, 0.7, 128], YELLOW), box([52, 50, -70], [0.7, 0.5, 128], STEEL))
    c += both(box([33, 54, -70.7], [19.7, 0.7, 0.7], YELLOW), box([33, 46.5, -70.7], [0.7, 7.5, 0.7], STEEL))
    # Navigation lights: red to port (+X), green to starboard (-X), white stern
    c += [box([53.5, 44, -76], [1.5, 2, 2], RED), box([-55, 44, -76], [1.5, 2, 2], GREEN)]
    c += [box([-1.5, 19, 84.6], [3, 2, 1], LENS)]
    # Bow: towing pad-eyes, fendering bumper above the skirt, hazard edge at the deck lip
    c += both(box([22, 18, -89], [6, 3, 3], STEEL), box([46, 18, -89], [5, 3, 3], STEEL))
    c += [box([-52, 20, -88.5], [104, 1.5, 1], RUBBER), box([-52, 20, 84], [104, 1.5, 1], RUBBER)]
    c += both(box([52, 20, -84], [1, 1.5, 168], RUBBER))
    # Stern: lower aft bulkheads under the ducts, stern hazard lip
    c += both(box([32, 22, 70], [22, 24, 4], PANEL), box([32, 46, 70], [21, 1, 10], WALK))
    return c


def cab():
    """Starboard (-X) control cab on the superstructure top: frames + see-through glass, console and driver seat."""
    x0, x1, z0, z1, y0, y1 = -54, -34, -74, -50, SS_Y, 70
    c = [box([x0, y0, z0], [20, 1, 24], WALK)]
    c += [box([x0, y0, z1 - 1.5], [20, y1 - y0, 1.5], PANEL)]                    # aft bulkhead
    c += [box([x0, y0, z0], [20, 8, 1.5], PANEL)]                                # front sill
    c += [box([x0, y0 + 1, z0 + 1.5], [1.5, 7, 21], PANEL), box([x1 - 1.5, y0 + 1, z0 + 1.5], [1.5, 7, 21], PANEL)]
    c += [box([x0 - 1, y1, z0 - 2], [22, 2, 27], PANEL), box([x0 - 1, y1 - 0.5, z0 - 3], [22, 0.6, 3], DARK)]  # roof + sun visor
    c += [box([x, y0 + 8, z0], [1.2, y1 - y0 - 8, 1.2], STEEL) for x in (x0, x0 + 6.4, x0 + 12.6, x1 - 1.2)]
    c += [box([x, y0 + 8, z], [1.2, y1 - y0 - 8, 1.2], STEEL) for x in (x0, x1 - 1.2) for z in (z0 + 11, z1 - 2.7)]
    c += [box([x0 + 1, y0 + 8, z0 + 0.2], [18, y1 - y0 - 8, 0.6], GLASS),
          box([x0 + 0.2, y0 + 8, z0 + 1], [0.6, y1 - y0 - 8, 21], GLASS), box([x1 - 0.8, y0 + 8, z0 + 1], [0.6, y1 - y0 - 8, 21], GLASS)]
    c += [box([x0, y0 + 8, z0], [20, 0.8, 1.6], STEEL), box([x0, y1 - 1, z0], [20, 1, 1.6], STEEL)]
    c += [box([x0 + 1, y1 - 3, z0 - 0.6], [5, 2, 0.4], DARK) for x0 in (-53.5, -47, -40.5)]  # wiper housings
    # Console + yoke + driver seat (cushion top y56)
    c += [box([-52, y0 + 1, z0 + 1.5], [16, 7, 4], PANEL), rod((-44, 54, -70), (-44, 54.8, -67), 14, 0.8, INSTR)]
    c += [box([-45, y0 + 1, -67], [2, 6, 2], STEEL), box([-47.5, 54, -66], [7, 1, 1], STEEL)]
    c += [box([-47, y0 + 1, -63], [6, 5, 6], STEEL), box([-47.5, 54.5, -63.5], [7, 1.5, 7], SEAT),
          box([-47.5, 56, -57.5], [7, 10, 1.5], SEAT), box([-46, 66, -57.2], [4, 2.5, 1], SEAT)]
    c += [box([-36.2, 59, -69], [1, 0.6, 6], STEEL)]  # grab rail
    return c


def deckhouse():
    """Small port (+X) deckhouse with portholes and door."""
    c = [box([35, SS_Y, -66], [16, 12, 14], PANEL), box([34, SS_Y + 12, -67], [18, 1.2, 16], PAINT)]
    c += [box([34.8, 52, z], [0.4, 3, 3], GLASS) for z in (-63, -57)] + [box([34.4, 51.5, z - 0.5], [0.4, 4, 4], STEEL) for z in (-63, -57)]
    c += [box([39, SS_Y + 1, -66.4], [6, 10, 0.6], DARK), box([43.5, 51, -66.8], [0.6, 1, 0.6], STEEL)]
    c += [box([47, 58.2, -62], [3, 4, 3], STEEL), box([47.5, 62, -61.5], [2, 0.6, 2], GRILLE)]
    return c


def mast():
    c = [box([-45, 72, -60], [2, 26, 2], STEEL), box([-50, 90, -59.5], [12, 1, 1], STEEL),
         box([-44.75, 98, -59.75], [1.5, 2.5, 1.5], AMBER), box([-50, 91, -60], [1, 2, 2], LENS), box([-39, 91, -60], [1, 2, 2], LENS)]
    c += [rod((-44, 72, -57), (-44, 84, -59), 1, 1, STEEL), box([-52, 82, -61.5], [16, 1.5, 3], DARK)]  # radar array
    c += [box([-53, 72, -55], [1, 14, 1], STEEL), box([-36, 72, -55], [0.6, 22, 0.6], STEEL)]       # whip antennas
    c += [box([-50, 72, -72], [3, 2, 3], LENS), box([-41, 72, -72], [3, 2, 3], LENS)]               # spotlights
    return c


def duct(x):
    c = ring(x, DUCT_Y, DUCT_Z, 15, DUCT_R, 3, 16, PAINT)
    c += ring(x, DUCT_Y, DUCT_Z - 0.6, 1, DUCT_R + 0.6, 1.4, 16, STEEL)              # intake lip
    c += ring(x, DUCT_Y, DUCT_Z + 14.4, 1, DUCT_R + 0.6, 1.4, 16, SALT)
    # Stator struts (4) + forward guard bars
    c += [{"origin": [x - 0.6, DUCT_Y - DUCT_R + 2, DUCT_Z + 10], "size": [1.2, 2 * DUCT_R - 4, 1.5], "pivot": [x, DUCT_Y, DUCT_Z + 10],
           "rotation": [0, 0, a], "uv": STEEL} for a in (45, 135)]
    c += [box([x - DUCT_R + 2, DUCT_Y - 0.4 + k * 6, DUCT_Z + 0.2], [2 * DUCT_R - 4, 0.6, 0.6], STEEL) for k in (-2, -1, 1, 2)]
    c += [box([x - 0.4 + k * 6, DUCT_Y - DUCT_R + 2, DUCT_Z + 0.2], [0.6, 2 * DUCT_R - 4, 0.6], STEEL) for k in (-2, -1, 1, 2)]
    c += cyl(x, DUCT_Y, DUCT_Z + 8, 8, 3.5, PANEL)                                  # gearbox nacelle
    # Twin rudders aft of the duct, with top/bottom bearing frame
    for dx in (-7, 7):
        c += [box([x + dx - 0.8, DUCT_Y - 16, DUCT_Z + 17], [1.6, 32, 9], PAINT), box([x + dx - 0.5, DUCT_Y - 16, DUCT_Z + 16], [1, 32, 1], STEEL)]
    c += [box([x - 10, DUCT_Y + 16, DUCT_Z + 15], [20, 1.2, 11], STEEL), box([x - 10, DUCT_Y - 17.2, DUCT_Z + 15], [20, 1.2, 11], STEEL)]
    c += [box([x - 9, DUCT_Y - 0.5, DUCT_Z + 21], [18, 1, 1], STEEL)]              # rudder tie bar
    return c


def prop(x):
    hz = DUCT_Z + 5
    c = cyl(x, DUCT_Y, hz - 2, 6, 2.6, DARK) + cyl(x, DUCT_Y, hz - 4, 2, 1.6, PANEL)  # hub + spinner
    for a in range(0, 360, 90):
        c.append({"origin": [x - 2, DUCT_Y + 2, hz - 0.5], "size": [4, DUCT_R - 5, 1], "pivot": [x, DUCT_Y, hz], "rotation": [8, 0, a], "uv": BLADE})
    return c


def bow_ramp():
    """Raised bow ramp/visor, hinge at the deck lip (z -84, y22)."""
    z = -86
    c = [box([-30, 22, z], [60, 26, 2], PANEL), box([-30, 46, z - 0.5], [60, 2, 3], HAZARD)]
    c += [box([x, 23, z - 1.5], [2, 22, 1.5], PAINT) for x in (-26, -14, -1, 12, 24)]       # outer stiffeners
    c += [box([-30, 34, z - 1.5], [60, 1.5, 1.5], PAINT)]
    c += both(rod((30, 22, -85), (30, 46, -85), 2, 6, PAINT))                              # side cheeks
    c += cylx(-30, 22, -85, 60, 1.6, STEEL)                                                # hinge barrel
    c += both(box([28, 40, z - 2.5], [2, 6, 1], YELLOW))
    return c


def stern_ramp():
    """Raised stern ramp, hinge at z +80, y22."""
    z = 80
    c = [box([-30, 22, z], [60, 20, 2], PANEL), box([-30, 40, z - 0.5], [60, 2, 3], HAZARD)]
    c += [box([x, 23, z + 2], [2, 17, 1.5], PAINT) for x in (-20, -7, 6, 18)]
    c += [box([-30, 31, z + 2], [60, 1.5, 1.5], PAINT)]
    c += cylx(-30, 22, 81, 60, 1.6, STEEL)
    return c


def skirt():
    """Black rubber bag + segmented fingers around the base (y0..~14), corners chamfered."""
    c = [box([-58, 6, -94], [116, 9, 8], RUBBER), box([-58, 6, 86], [116, 9, 8], RUBBER)]
    c += both(box([52, 6, -86], [6, 9, 172], RUBBER))
    c += both(rod((52, 15, 0), (58, 6, 0), 3, 172, RUBBER))                     # rounded upper bag
    c += [rod((0, 15, -86), (0, 6, -94), 104, 3, RUBBER), rod((0, 15, 86), (0, 6, 94), 104, 3, RUBBER)]
    step = 5.0
    for i in range(int(104 / step)):                                                   # bow & stern fingers
        x = -52 + i * step + 0.3
        c += [box([x, 0, -96], [step - 0.6, 7, 4], FINGER), box([x, 0, 92], [step - 0.6, 7, 4], FINGER)]
    for i in range(int(176 / step)):                                                   # side fingers
        z = -88 + i * step + 0.3
        c += both(box([56, 0, z], [4, 7, step - 0.6], FINGER))
    for sx in (1, -1):                                                                 # chamfered corner fingers
        for sz in (1, -1):
            for k in range(3):
                a = 22.5 + k * 22.5
                px_, pz = 52 * sx + math.sin(math.radians(a)) * 6 * sx, 88 * sz + math.cos(math.radians(a)) * 6 * sz
                c += [{"origin": [px_ - 2.2, 0, pz - 2], "size": [4.4, 7, 4], "pivot": [px_, 0, pz], "rotation": [0, a * sx * sz, 0], "uv": FINGER}]
    return c


SLOTS = (-36, 30)


def straps():
    """Tie-down chains from deck pad-eyes up to each Titan slot (hidden by Java when empty)."""
    c = []
    for zc in SLOTS:
        for sx in (1, -1):
            for sz in (1, -1):
                c += [rod((27 * sx, 22, zc + 18 * sz), (12 * sx, 38, zc + 7 * sz), 0.8, 0.8, CHAIN),
                      box([27 * sx - 1.5, 22, zc + 18 * sz - 1.5], [3, 1.2, 3], YELLOW),
                      box([12 * sx - 1, 37, zc + 7 * sz - 1], [2, 2, 2], STEEL)]
        c += [box([-14, 22, zc - 1], [28, 0.6, 2], YELLOW)]  # wheel-chock / shoe beam
    return c


def bones():
    b = [{"name": "root", "pivot": [0, 0, 0]},
         {"name": "hull", "parent": "root", "pivot": [0, 16, 0], "cubes": hull()},
         {"name": "skirt", "parent": "hull", "pivot": [0, 6, 0], "cubes": skirt()},
         {"name": "cab", "parent": "hull", "pivot": [-44, SS_Y, -62], "cubes": cab()},
         {"name": "mast", "parent": "cab", "pivot": [-44, 72, -59], "cubes": mast()},
         {"name": "deckhouse", "parent": "hull", "pivot": [43, SS_Y, -60], "cubes": deckhouse()},
         {"name": "duct_l", "parent": "hull", "pivot": [DUCT_X, DUCT_Y, DUCT_Z], "cubes": duct(DUCT_X)},
         {"name": "duct_r", "parent": "hull", "pivot": [-DUCT_X, DUCT_Y, DUCT_Z], "cubes": duct(-DUCT_X)},
         {"name": "prop_l", "parent": "duct_l", "pivot": [DUCT_X, DUCT_Y, DUCT_Z + 5], "cubes": prop(DUCT_X)},
         {"name": "prop_r", "parent": "duct_r", "pivot": [-DUCT_X, DUCT_Y, DUCT_Z + 5], "cubes": prop(-DUCT_X)},
         {"name": "bow_ramp", "parent": "hull", "pivot": [0, 22, -85], "cubes": bow_ramp()},
         {"name": "stern_ramp", "parent": "hull", "pivot": [0, 22, 81], "cubes": stern_ramp()},
         {"name": "cargo_straps", "parent": "hull", "pivot": [0, 22, 0], "cubes": straps()}]
    return b


def animation():
    idle = {"skirt": {"position": {"0.0": [0, -1.2, 0], "2.0": [0, -1.0, 0], "4.0": [0, -1.2, 0]},
                      "scale": [1.0, 0.85, 1.0]},
            "prop_l": {"rotation": [0, 0, 0]}, "prop_r": {"rotation": [0, 0, 0]}}
    hover = {"skirt": {"position": {"0.0": [0, 0, 0], "0.25": [0, 0.35, 0], "0.5": [0, 0.05, 0], "0.75": [0, 0.3, 0], "1.0": [0, 0, 0]},
                       "scale": {"0.0": [1, 1, 1], "0.5": [1.004, 1.03, 1.004], "1.0": [1, 1, 1]}},
             "hull": {"position": {"0.0": [0, 0, 0], "0.5": [0, 0.25, 0], "1.0": [0, 0, 0]}},
             "prop_l": {"rotation": {"0.0": [0, 0, 0], "0.125": [0, 0, 180], "0.25": [0, 0, 360], "0.375": [0, 0, 540], "0.5": [0, 0, 720],
                                     "0.625": [0, 0, 900], "0.75": [0, 0, 1080], "0.875": [0, 0, 1260], "1.0": [0, 0, 1440]}},
             "prop_r": {"rotation": {"0.0": [0, 0, 0], "0.125": [0, 0, -180], "0.25": [0, 0, -360], "0.375": [0, 0, -540], "0.5": [0, 0, -720],
                                     "0.625": [0, 0, -900], "0.75": [0, 0, -1080], "0.875": [0, 0, -1260], "1.0": [0, 0, -1440]}}}
    return {"format_version": "1.8.0", "animations": {
        f"animation.{KEY}.idle": {"loop": True, "animation_length": 4.0, "bones": idle},
        f"animation.{KEY}.hover": {"loop": True, "animation_length": 1.0, "bones": hover}}}


def item_icon():
    """16x16 side view: bow left, cab, big stern duct, black skirt."""
    rows = [
        "................",
        "...a............",
        "...k.......ddd..",
        "..kkk.....d...d.",
        "..wgw.....d.p.d.",
        "..ggg.....d.p.d.",
        ".GGGGGGGGGGd.d..",
        ".GsGGGGnnGGGGG..",
        ".GGGGGGGGGGGGG..",
        ".hhhhhhhhhhhhhh.",
        ".bbbbbbbbbbbbbb.",
        "bbbbbbbbbbbbbbbb",
        "bfbfbfbfbfbfbfbf",
        "................",
        "................",
        "................"]
    pal = {"a": (250, 170, 34), "k": (90, 94, 98), "w": (110, 160, 200), "g": (186, 190, 192), "G": (164, 168, 170),
           "s": (150, 154, 156), "n": (30, 30, 32), "d": (200, 204, 206), "p": (40, 40, 42), "h": (226, 186, 30),
           "b": (28, 28, 30), "f": (54, 54, 56)}
    buf = bytearray()
    for r in rows:
        for ch in r:
            buf += bytes(pal[ch]) + b"\xff" if ch in pal else b"\0\0\0\0"
    return make_png(16, 16, bytes(buf))


# ---------------------------------------------------------------- validation
REQUIRED = ("root", "hull", "skirt", "bow_ramp", "stern_ramp", "prop_l", "prop_r", "cargo_straps")


def validate(geo, anim):
    g = geo["minecraft:geometry"][0]
    names = {b["name"] for b in g["bones"]}
    n = 0
    for b in g["bones"]:
        assert b.get("parent") in names | {None}, b["name"]
        for c in b.get("cubes", []):
            n += 1
            assert all(s > 0 for s in c["size"]), (b["name"], c)
            for f in c["uv"].values():
                assert f["uv"][0] >= 0 and f["uv"][1] >= 0, c
                assert f["uv"][0] + f["uv_size"][0] <= 512 and f["uv"][1] + f["uv_size"][1] <= 512, c
    for a in anim["animations"].values():
        for bn in a["bones"]:
            assert bn in names, bn
    for r in REQUIRED:
        assert r in names, r
    assert {b["name"]: b.get("parent") for b in g["bones"]}["hull"] == "root"
    return n, [b["name"] for b in g["bones"]]


def main():
    tex = paint_texture()
    tex.save(os.path.join(ROOT, f"textures/entity/transport/{KEY}.png"))
    with open(os.path.join(ROOT, f"textures/item/{KEY}.png"), "wb") as f:
        f.write(item_icon())
    geo_path = os.path.join(ROOT, f"geo/{KEY}.geo.json")
    write_geo(geo_path, f"geometry.{KEY}", bones(), 14.0, 8.0, 3.0)
    anim = animation()
    with open(os.path.join(ROOT, f"animations/{KEY}.animation.json"), "w") as f:
        json.dump(anim, f, indent=2)
    geo = json.load(open(geo_path))
    n, names = validate(geo, anim)
    print(f"OK: {n} cubes, bones: {', '.join(names)}")
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        preview(geo, tex.buf, out, sc=3.4)
        preview(geo, tex.buf, out.replace(".png", "_rear.png"), yaw=215, sc=3.4)
        preview(geo, tex.buf, out.replace(".png", "_top.png"), yaw=20, pitch=-60, sc=3.0)


if __name__ == "__main__":
    main()
