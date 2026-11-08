#!/usr/bin/env python3
"""Patrol boat, patrol frigate and Sky Carrier: detailed geo, animation, texture and item icon each.

Shares the LCAC hovercraft's material atlas (paint, panels, non-skid deck, hazard, grilles, glass ...) so the three hulls take the
same camo / faction tint as the rest of the fleet (CamoTextures only repaints the light, unsaturated hull texels), plus a row of
extra cells for helipad, runway dashes, VLS hatches, hangar door and hull numbers.

Model space: 16 px = 1 block, bow at model -Z (= entity-local +Z in Java), +X = port. Footprints that Java relies on (deck tops, seat
spots, island / bridge / hangar blocks, cargo slots) are unchanged from the first version: see the *Entity classes.
Run: python3 scripts/gen_naval_fleet.py [--preview out.png]
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_transport_assets import TextureDrawer, make_png, rod, write_geo  # noqa: E402
from gen_armored_apc import box, both, preview, h, smooth  # noqa: E402
from gen_lcac_hovercraft import (PAINT, SALT, PANEL, DECK, HAZARD, STENCIL, GRILLE, STEEL, RUBBER, GLASS, LENS, RED,  # noqa: E402
                                 GREEN, AMBER, DARK, CHAIN, YELLOW, SEAT, WHITE, BLADE, WALK, GRIME, INSTR, paint_texture, ring, cyl, cylx)

import gen_armored_apc as _apc  # noqa: E402


def _rot(p, piv, r):
    x, y, z = p[0] - piv[0], p[1] - piv[1], p[2] - piv[2]
    ax, ay, az = math.radians(-r[0]), math.radians(-r[1]), math.radians(-r[2])
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    return (x + piv[0], y + piv[1], z + piv[2])


_apc.rot = _rot

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources", "assets", "titancombat")

# extra 64px cells on row 3 of the shared 512 atlas
HELI, DASH, VLS, DOORC, NUM_PB, NUM_FF, NUM_CV, NUM_DECK = [[i * 64, 192] for i in range(8)]
CDECK, CDECK2, CPLATE, CLIGHT = [[i * 64, 256] for i in range(4)]
MARK = (244, 238, 176)  # pale yellow: saturated enough that camo leaves markings alone

TextureDrawer.FONT.update({"P": "111101111100100", "B": "110101110101110", "F": "111100110100100", "V": "101101101101010",
                           "9": "111101111001111", "A": "010101111101101", "K": "101101110101101"})


def texture():
    t = paint_texture()
    px = lambda x, y, c, a=255: t.set_pixel(x, y, c[0], c[1], c[2], a)
    for y in range(64):
        for x in range(64):
            u, v = HELI[0] + x, HELI[1] + y
            base = (62, 64, 66) if (x * 7 + y * 13) % 11 else (70, 72, 74)
            r = math.hypot(x - 31.5, y - 31.5)
            if 25 <= r <= 29 or (abs(x - 31.5) < 8 and 18 <= y <= 46 and abs(x - 31.5) > 5.5) or (abs(y - 31.5) < 2.5 and 24 <= x <= 40):
                base = MARK
            px(u, v, base)
            # runway dashes along v, over non-skid
            d = (58, 60, 62) if (x * 5 + y * 3) % 9 else (66, 68, 70)
            if 30 <= x <= 33 and y < 40:
                d = MARK
            px(DASH[0] + x, DASH[1] + y, d)
            # VLS: 4x4 hatches
            hx, hy = x % 16, y % 16
            c = (112, 116, 120)
            if hx in (0, 15) or hy in (0, 15):
                c = (40, 42, 44)
            elif 3 <= hx <= 12 and 3 <= hy <= 12:
                c = (138, 142, 146) if not (hx in (7, 8) and hy in (7, 8)) else (70, 72, 74)
            px(VLS[0] + x, VLS[1] + y, c)
            # hangar roller door: ribs + hazard foot + centre seam
            c = (104, 108, 112) if x % 8 else (78, 82, 86)
            if y >= 56:
                c = (226, 186, 30) if (x + y) // 4 % 2 else (24, 24, 24)
            if x in (31, 32):
                c = (40, 42, 44)
            px(DOORC[0] + x, DOORC[1] + y, c)
    for y in range(64):
        for x in range(64):
            n = (smooth(x, y, 31, 3) - 0.5) * 10 + (h(x, y, 32) - 0.5) * 8
            g = 58 + n + (h(x, y, 33) > 0.96) * 14
            px(CDECK[0] + x, CDECK[1] + y, (g, g + 2, g + 4))
            w = 74 + n + (y % 13 < 2) * -6 + (smooth(x, y * 0.2, 34, 5) > 0.7) * -8
            px(CDECK2[0] + x, CDECK2[1] + y, (w, w + 2, w + 4))
            e = 126 + n * 0.6 + (x % 16 == 0 or y % 16 == 0) * -26 + (x % 16 in (3, 12) and y % 16 in (3, 12)) * 22   # riveted hull plate
            px(CPLATE[0] + x, CPLATE[1] + y, (e, e + 3, e + 6))
            px(CLIGHT[0] + x, CLIGHT[1] + y, (190, 232, 255) if (x // 8 + y // 8) % 2 else (120, 190, 240))
    for cell, text, scale, pos in ((NUM_PB, "PB41", 1, (0, 0)), (NUM_FF, "F17", 2, (0, 0)), (NUM_CV, "CV9", 2, (0, 0)), (NUM_DECK, "9", 7, (4, 4))):
        t.draw_text(cell[0] + pos[0], cell[1] + pos[1], text, MARK, scale)
    return t


# ------------------------------------------------------------------ helpers
def text(x, y, z, sx, sy, sz, cell, face):
    """Lettering plate that only shows on its outward face (a thin cube would otherwise mirror the text through its back)."""
    c = box([x, y, z], [sx, sy, sz], cell)
    c["face"] = face
    return c


def fill(x0, x1, y0, y1, z0, z1, cells):
    """Solid block tiled in <=64 px chunks so each face keeps ~1 texel per px (a big cube would stretch a 64px cell)."""
    cs = cells if isinstance(cells[0], list) else [cells]

    def split(a, b):
        k = max(1, math.ceil((b - a) / 64 - 1e-9))
        return [(a + i * (b - a) / k, (b - a) / k) for i in range(k)]
    out, n = [], 0
    for x, sx in split(x0, x1):
        for y, sy in split(y0, y1):
            for z, sz in split(z0, z1):
                out.append(box([round(x, 3), round(y, 3), round(z, 3)], [round(sx, 3), round(sy, 3), round(sz, 3)], cs[n % len(cs)]))
                n += 1
    return out


def cyly(cx, cz, y0, h, r, uv):
    """Octagonal prism standing on Y."""
    w = round(2 * r * math.tan(math.pi / 8), 3)
    return [{"origin": [cx - w / 2, y0, cz - r], "size": [w, h, 2 * r], "pivot": [cx, y0, cz], "rotation": [0, a, 0], "uv": uv} for a in (0, 45, 90, 135)]


def ringy(cx, cz, y0, h, R, t, n, uv):
    """n-gon tube standing on Y (fan shroud)."""
    L = round(2 * R * math.tan(math.pi / n) + 0.2, 3)
    return [{"origin": [cx - L / 2, y0, cz + R - t], "size": [L, h, t], "pivot": [cx, y0, cz], "rotation": [0, round(k * 360 / n, 3), 0], "uv": uv} for k in range(n)]


def rail(x, z0, z1, y, h=7, step=14, uv=STEEL):
    """Stanchions + two rails along Z at x."""
    c = [box([x - 0.4, y, z], [0.8, h, 0.8], uv) for z in [z0 + i * step for i in range(int((z1 - z0) / step) + 1)]]
    c += [box([x - 0.4, y + h - 0.8, z0], [0.8, 0.8, z1 - z0], uv), box([x - 0.4, y + h / 2, z0], [0.8, 0.6, z1 - z0], uv)]
    return c


def hull_slices(z0, z1, step, half, bot, wl, top, flare_y, flare, cells=(PAINT, PAINT, SALT, PAINT, PANEL)):
    """Ship hull cut in z slices: red antifouling, dark boot stripe at the waterline y=wl, painted topsides (flared above flare_y)."""
    c, i, z = [], 0, z0
    while z < z1 - 0.01:
        sz = min(step, z1 - z) + 0.03
        zc = z + step / 2
        h, b = half(zc), bot(zc)
        if b < wl - 3:
            c.append(box([-h, b, z], [2 * h, wl - 3 - b, sz], RED))
        lo = max(b, wl - 3)
        if lo < wl + 2:
            c.append(box([-h, lo, z], [2 * h, wl + 2 - lo, sz], DARK))
        lo = max(b, wl + 2)
        c.append(box([-h, lo, z], [2 * h, flare_y - lo, sz], cells[i % len(cells)]))
        c.append(box([-h - flare, flare_y, z], [2 * (h + flare), top - flare_y, sz], cells[i % len(cells)]))
        z += step
        i += 1
    return c


def wheelhouse(xc, hw, z0, z1, y0, y1, seat_x, seat_z, seat_top, console_z):
    """See-through bridge: floor, sills, frames + glass, roof, console and the helmsman's seat (cushion top = seat_top)."""
    x0, x1 = xc - hw, xc + hw
    c = [box([x0, y0, z0], [2 * hw, 1, z1 - z0], WALK)]
    c += [box([x0, y0, z1 - 2], [2 * hw, y1 - y0, 2], PANEL), box([x0, y0, z0], [2 * hw, 7, 2], PANEL)]
    c += [box([x, y0, z0], [2, 7, z1 - z0], PANEL) for x in (x0, x1 - 2)]
    for x in (x0, xc - hw / 2, xc, xc + hw / 2, x1 - 1.6):
        c.append(box([x, y0 + 7, z0], [1.6, y1 - y0 - 7, 1.6], STEEL))
    for x in (x0, x1 - 1.6):
        for z in ((z0 + z1) / 2, z1 - 3.6):
            c.append(box([x, y0 + 7, z], [1.6, y1 - y0 - 7, 1.6], STEEL))
    gh = y1 - y0 - 7
    c += [box([x0 + 1.6, y0 + 7, z0 + 0.2], [2 * hw - 3.2, gh, 0.6], GLASS),
          box([x0 + 0.2, y0 + 7, z0 + 1.6], [0.6, gh, z1 - z0 - 3.6], GLASS), box([x1 - 0.8, y0 + 7, z0 + 1.6], [0.6, gh, z1 - z0 - 3.6], GLASS)]
    c += [box([x0, y0 + 7, z0], [2 * hw, 0.8, 1.8], STEEL), box([x0, y1 - 1, z0], [2 * hw, 1, 1.8], STEEL)]
    c += [box([x0 - 3, y1, z0 - 4], [2 * hw + 6, 2.5, z1 - z0 + 6], PAINT), box([x0 - 3, y1 - 0.4, z0 - 5], [2 * hw + 6, 0.8, 1.5], DARK)]
    c += [box([xc - hw + 3, y0 + 1, console_z], [2 * hw - 6, 6, 6], PANEL), box([xc - hw + 4, y0 + 7, console_z + 0.5], [2 * hw - 8, 0.8, 5], INSTR),
          box([xc - 1, y0 + 8, console_z + 1], [2, 3, 2], STEEL)]
    c += [box([seat_x - 2.5, y0 + 1, seat_z - 2.5], [5, seat_top - y0 - 2.5, 5], STEEL), box([seat_x - 4, seat_top - 1.5, seat_z - 4], [8, 1.5, 8], SEAT),
          box([seat_x - 4, seat_top, seat_z + 3], [8, 9, 1.5], SEAT), box([seat_x - 2, seat_top + 9, seat_z + 3.2], [4, 2.5, 1], SEAT)]
    return c


def sensor_ball(x, y, z, r=4):
    return cyly(x, z, y, 2 * r, r, WHITE) + cyly(x, z, y + r * 0.4, r * 1.2, r + 0.7, WHITE)


def ciws(x, y, z, h=1.0):
    """Close-in weapon: pedestal, radome and a Gatling barrel pointing at the bow."""
    c = cyly(x, z, y, 6 * h, 5, PANEL) + cyly(x, z, y + 6 * h, 8 * h, 4.5, WHITE)
    c += [box([x - 3.5, y + 7 * h, z - 4.6], [7, 4 * h, 1], PANEL), box([x - 1.2, y + 8.5 * h, z - 16], [2.4, 2.4, 13], DARK),
          box([x - 1.6, y + 8.2 * h, z - 17], [3.2, 3, 2], STEEL)]
    return c


# ================================================================== PATROL BOAT (12 x 3 blocks, deck top y22)
def pb_bones():
    Z0, Z1, H = -96, 96, 22

    def half(z):
        if z < -26:
            return H * min(1.0, 0.07 + 0.93 * ((z - Z0) / 70.0) ** 0.72)
        return H * (1 - 0.1 * max(0.0, (z - 70) / 26) ** 2)

    def bot(z):
        return 15 * (1 - max(0.0, (z - Z0) / 74.0)) ** 2 if z < Z0 + 74 else 0.0

    hull = hull_slices(Z0, Z1, 6, half, bot, 10, 20, 15, 1.5)
    # deck follows the taper: 2 px plate, top y22
    z = Z0
    while z < Z1 - 0.01:
        h = half(z + 3) + 0.5
        hull += fill(-h, h, 20, 22, z, min(z + 6, Z1) + 0.03, [DECK, WALK])
        hull += [box([-h - 1.2, 20, z], [1.5, 7, 6.03], PAINT), box([h - 0.3, 20, z], [1.5, 7, 6.03], PAINT)]       # gunwale (top y27)
        z += 6
    # black inflatable collar along both sides (core + rounded caps)
    for z in range(-60, 90, 6):
        h = half(z + 3)
        for s in (1, -1):
            x = (h + 1.0) if s > 0 else -(h + 1.0) - 6
            hull += [box([x, 14, z], [6, 8, 6.03], RUBBER), box([x + 1, 22, z], [4, 1.5, 6.03], RUBBER), box([x + 1, 12.5, z], [4, 1.5, 6.03], RUBBER)]
    # deckhouse sides below the wheelhouse + roof gear
    hull += wheelhouse(0, 16, -40, 2, 22, 46, 0, -10, 26, -34)
    hull += [box([-18, 22, 2], [36, 12, 14], PANEL), box([-19, 34, 1], [38, 1.5, 16], PAINT)]                   # engine casing aft of the helm
    hull += both(box([18, 25, 4], [0.5, 5, 9], DARK), box([8, 22, 16.2], [6, 10, 0.6], DARK))                    # louvres, door
    hull += [box([-15, 46.4, -24], [30, 1.2, 3], DARK)]
    hull += [box([-9 + 6 * i, 48.5, -26], [5, 1.5, 2], [RED, LENS, GREEN][i % 3] if i in (0, 2, 4) else LENS) for i in range(4)]    # light bar
    hull += [box([-1, 48.5, -8], [2, 12, 2], STEEL), box([-6, 48.5, -4], [12, 1, 6], PANEL)]                    # radar mast base
    hull += [box([-13, 48.5, 0], [0.8, 26, 0.8], STEEL), box([12.2, 48.5, 0], [0.8, 22, 0.8], STEEL), box([-0.4, 48.5, 6], [0.8, 30, 0.8], STEEL)]
    hull += cyly(11, -34, 48.5, 4, 2.2, STEEL) + [box([9.5, 51, -38], [3, 2.5, 4], LENS)]                       # searchlight
    hull += [box([-15.6, 36, -20], [1.2, 2, 2], GREEN), box([14.4, 36, -20], [1.2, 2, 2], RED)]
    # remote weapon station on the foredeck
    hull += cyly(0, -76, 22, 5, 5, DARK) + [box([-7, 27, -83], [14, 9, 14], PANEL), box([-8.5, 29, -82], [1.5, 5, 9], DARK), box([7, 29, -82], [1.5, 5, 9], DARK)]
    hull += [box([-1.3, 31, -108], [2.6, 2.6, 26], DARK), box([-2, 30.5, -110], [4, 3.6, 4], STEEL), box([-3, 34, -86], [6, 3, 4], GLASS), box([-2, 36.5, -85], [4, 2, 3], DARK)]
    hull += [box([8, 28, -76], [4, 4, 6], STEEL)]                                                                 # ammo box
    hull += [box([-9, 22, -74], [18, 1, 8], WALK)]
    # foredeck fittings: anchor, cleats, hatch
    hull += [box([-3, 22, -56], [6, 3, 6], PANEL), box([-2.5, 25, -55.5], [5, 0.6, 5], GRILLE)]
    hull += [box([-1.5, 22, -90], [3, 4, 3], STEEL), box([-0.7, 26, -89.2], [1.4, 1.4, 1.4], STEEL)]
    for z in (-30, 40, 72):
        hull += both(box([H - 6, 22, z], [3, 2.5, 1.2], STEEL))
    # aft deck: fuel cans, life ring, rescue davit
    hull += [box([-8, 22, 40], [5, 6, 4], YELLOW), box([-2, 22, 40], [5, 6, 4], YELLOW), box([4, 22, 40], [5, 6, 4], YELLOW)]
    hull += cyly(0, 80, 22, 1.5, 6, RED) if False else []
    hull += [box([-12, 22, 58], [24, 3, 22], DARK), box([-10, 25, 60], [20, 0.8, 18], HAZARD)]
    hull += rail(-H + 1, -52, 88, 27, 6) + rail(H - 1, -52, 88, 27, 6)
    hull += [box([-H, 27, 88], [2 * H, 1, 0.8], STEEL), box([-H, 30, 88], [2 * H, 0.6, 0.6], STEEL), box([-H, 27, 88], [0.8, 4, 0.8], STEEL), box([H - 0.8, 27, 88], [0.8, 4, 0.8], STEEL)]
    # transom, twin outboards, waterjet wash
    hull += [box([-H + 1, 8, 96], [2 * H - 2, 14, 2], PANEL), box([-H + 3, 12, 98], [2 * H - 6, 3, 1], STEEL)]
    for x in (-11, 11):
        hull += [box([x - 5.5, 12, 98], [11, 22, 11], PANEL), box([x - 6, 30, 97.5], [12, 4, 12], PAINT), box([x - 4.5, 15, 99], [9, 12, 0.6], GRILLE),
                 box([x - 2.5, -2, 101], [5, 16, 5], DARK), box([x - 4, -3, 103], [8, 3, 1.4], DARK), box([x - 1, 16, 109.5], [2, 3, 1.5], STEEL)]
    # hull numbers on the collar-free flare and bow chevron
    hull += [text(H + 7.2, 14, 10, 0.2, 7, 18, NUM_PB, "east"), text(-H - 7.4, 14, 10, 0.2, 7, 18, NUM_PB, "west")]
    hull += both(box([half(-84) + 0.6, 16, -92], [0.4, 3, 12], YELLOW))
    # nav lights, mooring lights
    radar = [box([-12, 62, -9], [24, 2.2, 3], STEEL), box([-1.5, 59, -10.5], [3, 3, 6], DARK), box([-12.5, 61.5, -10], [1, 3.2, 4], STEEL), box([11.5, 61.5, -10], [1, 3.2, 4], STEEL)]
    return [{"name": "root", "pivot": [0, 0, 0], "cubes": []},
            {"name": "hull", "parent": "root", "pivot": [0, 12, 0], "cubes": hull},
            {"name": "radar", "parent": "hull", "pivot": [0, 62, -8], "cubes": radar}]


# ================================================================== PATROL FRIGATE (30 x 6 blocks, deck top y42)
def ff_bones():
    Z0, Z1, H = -240, 240, 46

    def half(z):
        if z < -110:
            return H * min(1.0, 0.04 + 0.96 * ((z - Z0) / 130.0) ** 0.62)
        return H * (1 - 0.12 * max(0.0, (z - 190) / 50) ** 2)

    def bot(z):
        if z < -130:
            return 28 * (1 - (z - Z0) / 110.0) ** 2
        return 7 * max(0.0, (z - 200) / 40) ** 2

    hull = hull_slices(Z0, Z1, 8, half, bot, 22, 40, 29, 2.5)
    z = Z0
    while z < Z1 - 0.01:
        h = half(z + 4) + 2.2
        sz = min(8, Z1 - z) + 0.03
        hull += fill(-h, h, 40, 42, z, z + sz, [DECK, WALK])
        z += 8
    # bulwarks: foredeck wall and a low edge along the length
    z = Z0 + 8
    while z < -150:
        h = half(z + 4) + 2.5
        hull += both(box([h - 2, 42, z], [2, 9, 8.03], PAINT))
        hull += [box([-h, 42, z], [2 * h, 0.01, 0.01], PAINT)] if False else []
        z += 8
    hull += both(box([H + 0.5, 42, -150], [2, 3.5, 390], PAINT))
    hull += rail(H - 3, -148, 238, 45.5, 7, 16) + rail(-H + 3, -148, 238, 45.5, 7, 16)
    # --- main deckhouse (collision block x+-22, z -62..-10, y42..88)
    hull += fill(-24, 24, 42, 70, -62, -10, [PANEL, PAINT])
    hull += fill(-20, 20, 70, 88, -60, -10, [PANEL, PAINT])
    hull += both(rod((24, 70, -35), (20, 71.2, -35), 1.4, 52, PAINT)) if False else []
    hull += [box([-25, 69, -62.5], [50, 1.4, 52.5], PAINT), box([-21, 87.5, -61], [42, 1, 51], WALK)]
    for z in (-56, -44, -32, -20):                                                      # window bands + doors
        hull += both(box([24, 52, z], [0.6, 6, 7], DARK), box([20.2, 78, z], [0.6, 5, 7], DARK))
    hull += [box([-18, 52, -62.6], [36, 6, 0.6], DARK), box([-14, 78, -60.6], [28, 5, 0.6], DARK)]
    hull += both(box([24, 43, -14], [0.6, 12, 6], DARK), box([24.2, 44, -22], [0.6, 8, 5], STEEL))
    hull += [box([-24.6 - 0.2, 46, -50], [0.2, 14, 4], YELLOW)] if False else []
    hull += [box([-30, 42, -16], [6, 10, 4], DARK)]
    # bridge wings + wheelhouse (seat at z -40, cushion top y92)
    hull += wheelhouse(0, 18, -54, -22, 88, 112, 0, -40, 92, -51)
    hull += both(box([20, 88, -50], [10, 1, 20], WALK), box([29, 88, -50], [0.8, 5, 20], STEEL), *[box([20 + 8 * i, 88, -50], [0.6, 4, 0.6], STEEL) for i in (0, 1)])
    # mast, sensors, rotating radar bone above it
    hull += fill(-5, 5, 114, 140, -40, -33, [STEEL, PANEL])
    hull += [box([-1.5, 140, -38.5], [3, 22, 3], STEEL), box([-14, 150, -38], [28, 1.2, 1.2], STEEL), box([-0.8, 162, -37.8], [1.6, 8, 1.6], AMBER)]
    hull += [box([-9, 120, -33], [18, 14, 5], PANEL), box([-7, 122, -28.2], [14, 10, 0.6], GRILLE)]                # EW / comms array
    hull += sensor_ball(0, 114, -50, 5) if False else []
    hull += cyly(0, -30, 114, 10, 5.5, WHITE) + cyly(0, -30, 112, 2, 6.5, STEEL)
    hull += both(*[box([14, 114, -34 + 7 * i], [1, 14 - 4 * i, 1], STEEL) for i in range(2)])
    # forward superstructure roof gear: CIWS + chaff launchers
    hull += ciws(0, 88, -52, 1.0)
    hull += both(box([12, 88, -26], [6, 3, 6], PANEL), rod((15, 91, -26), (15, 96, -30), 4, 4, STEEL))
    # funnel casing + stack
    hull += fill(-16, 16, 42, 88, -10, 24, [PANEL, PAINT])
    hull += [box([-12, 88, -6], [24, 3, 28], STEEL)]
    hull += [box([-10, 91, -4], [20, 17, 24], DARK), box([-11, 107, -5], [22, 1.5, 26], STEEL), box([-9, 108.4, -3], [18, 0.8, 22], GRILLE)]
    hull += [rod((0, 100, 6), (0, 114, 22), 14, 6, DARK)]
    hull += both(box([16, 56, -4], [0.6, 18, 16], GRILLE), box([16, 60, 14], [0.6, 8, 5], DARK))
    # SSM canisters beside the funnel casing
    for s in (1, -1):
        for i in range(2):
            for j in range(2):
                x = s * (21 + 6 * i) - 2
                hull += [rod((s * (21 + 6 * i), 44 + 6 * j, -8), (s * (21 + 6 * i), 53 + 6 * j, 20), 5, 5, PANEL)]
    hull += both(box([19, 42, -8], [14, 2, 28], STEEL))
    # hangar (collision block x+-28, z 22..62, y42..76) + roller door aft
    hull += fill(-28, 28, 42, 76, 22, 62, [PANEL, PAINT])
    hull += [box([-24, 42, 62], [48, 30, 1.2], DOORC), box([-26, 71, 61.5], [52, 3, 2.4], STEEL), box([-26, 42, 61.6], [2, 32, 2.2], STEEL), box([24, 42, 61.6], [2, 32, 2.2], STEEL)]
    hull += [box([-27, 76, 21], [54, 1.5, 42], WALK)]
    hull += both(box([28, 50, 30], [0.6, 8, 8], DARK), box([28, 50, 44], [0.6, 8, 8], DARK))
    hull += ciws(0, 77.5, 40, 1.0)
    hull += [box([-4, 77.5, 52], [8, 12, 8], STEEL), box([-4, 90, 50], [8, 1, 12], PANEL)]                       # aft sensor pole
    # RIBs on cradles beside the hangar
    for s in (1, -1):
        x0 = 30 if s > 0 else -44
        hull += [box([x0, 42, 28], [14, 2, 30], STEEL), box([x0 + 1, 44, 24], [12, 6, 36], PAINT), box([x0, 44, 24], [14, 3, 36], RUBBER),
                 box([x0 + 1.5, 50, 40], [11, 1, 14], WALK), box([x0 + 5, 50, 44], [4, 4, 2], DARK)]
        hull += [box([x0 + 5, 46, 58], [4, 8, 4], PANEL)]                                                       # outboard
    # foredeck: main gun, VLS, windlass
    hull += [box([-17, 42, -206], [34, 8, 36], PANEL), box([-14, 50, -200], [28, 7, 26], PAINT), box([-12, 57, -196], [24, 2, 20], WALK)]
    hull += [rod((-14, 50, -206), (-12, 58, -202), 28, 1.5, PAINT)] if False else []
    hull += [box([-2.2, 52, -236], [4.4, 4.4, 36], DARK), box([-3.2, 51, -238], [6.4, 6.4, 5], STEEL), box([-3.5, 50.5, -214], [7, 7, 8], PANEL)]
    hull += fill(-32, 32, 42, 43.6, -158, -94, [VLS])
    hull += [box([-34, 42, -158], [2, 2.2, 64], STEEL), box([32, 42, -158], [2, 2.2, 64], STEEL), box([-34, 42, -160], [68, 2.2, 2], STEEL), box([-34, 42, -94], [68, 2.2, 2], STEEL)]
    hull += cyly(0, -246, 42, 10, 6, DARK) if False else []
    hull += [box([-9, 42, -176], [18, 6, 12], STEEL)] if False else []
    hull += both(box([20, 42, -178], [14, 7, 14], STEEL), box([22, 49, -176], [10, 2, 10], PANEL), box([25, 49, -180], [4, 4, 4], DARK))   # windlasses
    hull += both(*[box([36, 42, z], [3, 3, 3], STEEL) for z in (-90, -60, -10, 30)])
    hull += both(box([half(-168) + 0.5, 28, -180], [1, 3, 5], DARK), box([half(-168) + 0.8, 24, -178], [0.8, 8, 0.8], CHAIN))      # hawse pipe + chain
    # helideck + pad lights + nets
    hull += fill(-40, 40, 42, 43, 70, 222, [DECK, WALK])
    hull += [box([-32, 43, 109], [64, 0.5, 64], HELI)]
    hull += [box([-40, 43, 70], [2, 0.6, 152], YELLOW), box([38, 43, 70], [2, 0.6, 152], YELLOW), box([-40, 43, 220], [80, 0.6, 2], YELLOW), box([-40, 43, 70], [80, 0.6, 2], YELLOW)]
    hull += both(*[box([40, 43, z], [2, 1.2, 2], LENS) for z in (72, 120, 168, 216)])
    hull += both(box([42, 44, 70], [0.8, 4, 152], GRILLE))
    hull += [box([-22, 43, 190], [44, 0.5, 10], HAZARD), box([-16, 43, 178], [32, 0.4, 4], DASH)]
    # transom + boat ramp + stern gear
    hull += [box([-34, 24, 236], [68, 18, 6], DARK), box([-34, 24, 241], [68, 4, 1], STEEL), box([-24, 28, 242.6], [48, 10, 0.6], DOORC)]
    hull += [box([-1, 42, 232], [2, 30, 2], STEEL), box([-0.8, 70, 232], [0.8, 1, 0.8], STEEL), box([0, 60, 232], [1.2, 8, 0.4], WHITE)]
    hull += both(box([30, 20, 238], [10, 6, 6], DARK))
    # hull numbers, anchor recesses, waterline plates, side doors
    hull += [box([half(-50) + 2.5 + 0.2, 26, -66], [0.2, 14, 48], NUM_FF), box(-[half(-50) + 2.5 + 0.4, 0, 0][0:1] + [26, -66], [0.2, 14, 48], NUM_FF)] if False else []
    hn = half(-50) + 2.5 + 0.2
    hull += [text(hn, 26, -66, 0.2, 14, 36, NUM_FF, "east"), text(-hn - 0.2, 26, -66, 0.2, 14, 36, NUM_FF, "west")]
    hull += both(box([hn - 0.1, 26, 26], [0.3, 11, 12], DARK), box([hn - 0.1, 26, 120], [0.3, 11, 12], DARK))                                # pilot doors
    hull += both(*[box([hn - 0.1, 32, z], [0.5, 1.6, 1.6], LENS) for z in (-100, -20, 80)])
    hull += both(box([hn - 0.2, 40, -40], [0.5, 2, 90], STEEL))
    hull += [box([45, 30, -230], [2, 1.6, 2], RED), box([-47, 30, -230], [2, 1.6, 2], GREEN)] if False else []
    radar = [box([-24, 146, -39.5], [48, 11, 2.6], STEEL), box([-24.5, 144.5, -40.5], [49, 1.6, 4.5], PANEL), box([-3, 140, -40.5], [6, 6, 5], DARK),
             box([-22, 148, -41.2], [44, 7, 0.8], GRILLE)]
    return [{"name": "root", "pivot": [0, 0, 0], "cubes": []},
            {"name": "hull", "parent": "root", "pivot": [0, 22, 0], "cubes": hull},
            {"name": "radar", "parent": "hull", "pivot": [0, 146, -38], "cubes": radar}]


# ================================================================== SKY CARRIER (48 x 14 blocks, deck top y52)
def cv_bones():
    Z0, Z1, H = -360, 360, 96

    def half(z):
        a = abs(z)
        return H * (1 - 0.55 * max(0.0, (a - 250) / 110) ** 1.6)

    def rise(z):  # underside lifts toward both ends
        a = abs(z)
        return 22 * max(0.0, (a - 230) / 130) ** 1.8

    hull = []
    # lower hull: three stepped tiers narrowing toward the keel, riveted plating, tapered both ends
    z, i = Z0, 0
    while z < Z1 - 0.01:
        sz = min(12, Z1 - z) + 0.03
        h = half(z + 6)
        r = rise(z + 6)
        hull += [box([-h * 0.62, 2 + r, z], [2 * h * 0.62, 10, sz], [DARK, PANEL][i % 2]),
                 box([-h * 0.82, 12 + r, z], [2 * h * 0.82, 12, sz], [CPLATE, PAINT, CPLATE][i % 3]),
                 box([-h, 24, z], [2 * h, 16, sz], [CPLATE, PAINT, SALT, CPLATE][i % 4])]
        z += 12
        i += 1
    hull += [box([-14, -8, -320], [28, 12, 630], STEEL), box([-9, -10, -290], [18, 2.5, 570], DARK)]
    hull += [box([-70, 3, -300], [140, 0.6, 3], CLIGHT), box([-70, 3, 270], [140, 0.6, 3], CLIGHT)]
    for z in range(-300, 301, 100):
        hull += [box([-40, 2, z], [80, 0.6, 3], CLIGHT)]
    # flight deck: plain non-skid in tiles, plated edge skirt, catwalk
    hull += fill(-112, 112, 40, 46, -384, 384, [CPLATE, DARK])
    hull += fill(-112, 112, 46, 52, -384, 384, [CDECK, CDECK2, CDECK, CDECK, CDECK2])
    hull += [box([-114, 36, -385], [2, 18, 770], CPLATE), box([112, 36, -385], [2, 18, 770], CPLATE), box([-114, 36, -386], [228, 18, 2], CPLATE), box([-114, 36, 384], [228, 18, 2], CPLATE)]
    hull += [box([-120, 44, -380], [6, 1.5, 760], WALK), box([114, 44, -380], [6, 1.5, 760], WALK)]
    for z in range(-380, 381, 40):
        hull += both(box([118.6, 45.5, z], [0.8, 6, 0.8], STEEL))
    hull += both(box([118.6, 51.2, -380], [0.8, 0.8, 760], STEEL), box([118.6, 48.5, -380], [0.8, 0.6, 760], STEEL))
    # markings
    for z in range(-360, 330, 64):
        hull += [box([-2, 52, z], [4, 0.3, 64], DASH)]
    hull += [box([-108, 52, -380], [1.6, 0.3, 760], YELLOW), box([106.4, 52, -380], [1.6, 0.3, 760], YELLOW)]
    hull += [box([-108, 52, -382], [216, 0.3, 1.6], YELLOW), box([-108, 52, 380.4], [216, 0.3, 1.6], YELLOW)]
    hull += [box([-15, 52, -320], [30, 0.3, 42], NUM_DECK), box([-15, 52, 280], [30, 0.3, 42], NUM_DECK)]
    for x in (-34, 34):
        hull += [box([x - 1, 52, -350], [2, 0.3, 250], DARK), box([x - 3, 52.05, -250], [6, 0.8, 14], STEEL)]
    for zc in (-200, 140):
        hull += [box([-102, 52, zc], [64, 0.3, 64], CPLATE), box([-102, 52.2, zc], [64, 0.2, 2], HAZARD), box([-102, 52.2, zc + 62], [64, 0.2, 2], HAZARD),
                 box([-102, 52.2, zc], [2, 0.2, 64], HAZARD), box([-40, 52.2, zc], [2, 0.2, 64], HAZARD)]
    hull += [box([-100, 52, 250], [56, 0.3, 2], YELLOW), box([-100, 52, 258], [56, 0.3, 2], YELLOW)]
    for z in (190, 214, 238, 262):                                            # arrester wires across the landing area
        hull += [box([-100, 52.3, z], [200, 0.5, 0.8], CHAIN)]
    for z in (-290, -250, 60, 100):                                           # deck tractors along the starboard edge, off the parking lanes
        hull += [box([-110, 52, z], [12, 5, 16], YELLOW), box([-109, 57, z + 1], [8, 4, 7], GLASS), box([-110, 57, z + 8], [12, 1, 8], PAINT), box([-107, 52, z - 3], [6, 2, 3], DARK)]
    for z in (-120, 20):
        hull += [box([-108, 52, z], [8, 7, 8], PANEL), box([-108, 59, z], [8, 0.6, 8], STEEL)]
    for z in range(-90, 380, 90):
        hull += [box([-80, 52, z], [3, 1, 3], STEEL), box([-60, 52, z + 30], [3, 1, 3], STEEL)]
    for z in range(-360, 380, 60):
        hull += both(box([108, 52, z], [3, 1.4, 3], LENS))
    hull += [box([x, 52, 382], [3, 1.4, 3], RED) for x in (-100, 100)] + [box([x, 52, -384], [3, 1.4, 3], GREEN) for x in (-100, 100)]
    for x in (-34, 34):                                                       # jet blast deflectors aft
        hull += [rod((x, 52, 322), (x, 76, 310), 56, 3, STEEL), box([x - 28, 52, 322], [56, 1.5, 6], PANEL), box([x - 28, 52, 306], [3, 24, 3], STEEL), box([x + 25, 52, 306], [3, 24, 3], STEEL)]
    # ---- island (collision block x 60..110, z -90..30, y52..130)
    hull += fill(60, 110, 52, 100, -90, 30, [CPLATE, PANEL, PAINT])
    hull += [box([58, 98, -92], [54, 2, 124], PAINT), box([60, 96, -92.8], [50, 2, 1.2], STEEL)]
    for z in (-76, -52, -28, -4, 14):
        hull += [box([109.6, 64, z], [0.6, 6, 12], DARK), box([109.6, 80, z], [0.6, 6, 12], DARK), box([59.8, 72, z], [0.6, 6, 12], DARK)]
    hull += [box([60, 54, -91], [50, 40, 1], PANEL), box([70, 62, -91.6], [30, 6, 0.6], DARK)]
    hull += [box([62, 52, 30], [46, 40, 1.4], DOORC), box([60, 90, 30], [50, 2, 2.4], STEEL)]
    hull += [text(110.3, 84, -66, 0.2, 14, 36, NUM_CV, "east")]
    hull += [box([110.4, 56, -86], [0.8, 40, 1.2], STEEL), box([110.4, 56, -80], [0.8, 40, 1.2], STEEL)] + [box([110.4, 56 + 4 * k, -86], [0.8, 0.8, 7.2], STEEL) for k in range(10)]
    hull += wheelhouse(85, 27, -92, -12, 100, 130, 85, -35, 106, -80)
    hull += fill(66, 106, 100, 124, -8, 28, [CPLATE, PANEL])
    hull += [box([62, 124, -12], [48, 2.5, 44], PAINT), box([64, 108, 28.2], [44, 9, 0.6], GLASS), box([64, 108, -8.4], [44, 9, 0.6], GLASS), box([63, 108, -8], [1.6, 9, 36], STEEL), box([106, 108, -8], [1.6, 9, 36], STEEL)]
    hull += [box([66, 112, -8.8], [18, 10, 0.6], GRILLE), box([88, 112, -8.8], [18, 10, 0.6], GRILLE)]
    hull += [box([78, 126.5, 2], [14, 5, 14], PANEL)] + sensor_ball(100, 126.5, 12, 4.5) + sensor_ball(70, 126.5, 12, 3.4)
    hull += rail(62, -12, 26, 126.5, 5, 12) + rail(108, -12, 26, 126.5, 5, 12)
    hull += [box([83, 134, -64], [4, 38, 4], STEEL), box([66, 150, -63], [38, 1.4, 1.4], STEEL), box([70, 160, -63], [30, 1.2, 1.2], STEEL), box([84, 172, -63], [2, 14, 2], STEEL),
             box([84, 186, -62.5], [2, 3, 2], AMBER), box([64, 150, -62.8], [3, 3, 3], RED), box([102, 150, -62.8], [3, 3, 3], RED)]
    hull += [rod((85, 134, -62), (66, 152, -62), 1.4, 1.4, STEEL), rod((85, 134, -62), (104, 152, -62), 1.4, 1.4, STEEL)]
    hull += [box([100, 134, -20], [8, 18, 8], STEEL), box([98, 150, -22], [12, 1, 12], PANEL), box([102, 151, -18], [4, 12, 4], STEEL)]
    hull += [box([64, 134, 6], [10, 8, 10], DARK), box([65, 142, 7], [8, 1, 8], GRILLE)]
    hull += [box([100, 126.5, -34], [3, 12, 3], STEEL), box([96, 138, -34], [11, 1, 1], STEEL), box([98.5, 138, -35], [1.6, 3, 3], LENS)]
    # CIWS on the deck corners and flanks, boxed missile launchers on the port side
    for x, z in ((100, -350), (-100, -350), (100, 350), (-100, 350), (100, 160), (100, -160)):
        hull += ciws(x, 52, z, 1.1)
    for z in (-230, 200):
        hull += [box([84, 52, z], [22, 9, 40], PANEL)] + [box([86 + 5.2 * k, 61, z + 3 + 9 * j], [4.6, 0.6, 8], VLS) for k in range(4) for j in range(4)]
    # hangar bays under the deck overhang (doors + lit frames) and hull numbers
    for z in (-186, -126, -66, -6, 54, 114, 174):
        hull += both(box([96, 26, z], [0.6, 14, 60], DOORC), box([96, 25, z], [1.2, 1.2, 60], STEEL), box([96, 40, z], [1.2, 1.2, 60], STEEL), box([96.2, 36, z + 28], [0.8, 3, 4], AMBER))
    hull += [text(half(-300) + 0.4, 26, -300, 0.2, 14, 36, NUM_CV, "east"), text(-half(-300) - 0.6, 26, -300, 0.2, 14, 36, NUM_CV, "west")]
    # ---- lift pods outboard of the deck (rotors are separate bones)
    bones = [{"name": "root", "pivot": [0, 0, 0], "cubes": []}, {"name": "hull", "parent": "root", "pivot": [0, 26, 0], "cubes": hull}]
    PX, PZ, R = 168, 270, 40
    for zz in (-PZ, PZ):
        for s in (1, -1):
            cx = s * PX
            hull += ringy(cx, zz, 20, 30, R, 4, 16, PAINT) + ringy(cx, zz, 18, 3, R + 1, 1.5, 16, STEEL) + ringy(cx, zz, 48, 3, R + 1, 1.5, 16, STEEL)
            hull += [box([cx - R + 2, 36, zz - 1.5], [2 * R - 4, 2, 3], STEEL), box([cx - 1.5, 36, zz - R + 2], [3, 2, 2 * R - 4], STEEL)]
            for k in (-3, -2, -1, 1, 2, 3):
                hull += [box([cx - R + 2, 50.2, zz + 10 * k - 0.6], [2 * R - 4, 1.2, 1.2], STEEL), box([cx + 10 * k - 0.6, 50.2, zz - R + 2], [1.2, 1.2, 2 * R - 4], STEEL)]
            span = PX - R - 96 + 2
            x0 = 96 if s > 0 else -96 - span
            for dz in (-20, 14):                                              # wing pylons joining the hull to the pod
                hull += [box([x0, 26, zz + dz], [span, 14, 6], PANEL), box([x0, 40, zz + dz - 1], [span, 1.2, 8], STEEL)]
            hull += [box([cx - 5, 17, zz - 5], [10, 2, 10], CLIGHT)]
            hull += [box([cx - R - 0.4, 28, zz - 4], [0.8, 6, 8], AMBER), box([cx + R - 0.4, 28, zz - 4], [0.8, 6, 8], AMBER)]
    for x in (-84, -36, 36, 84):                                              # stern engines: big ducts with glowing cores
        hull += ring(x, 26, 352, 26, 15, 3, 12, STEEL) + ring(x, 26, 350, 3, 16.5, 1.5, 12, PANEL) + cyl(x, 26, 358, 4, 12, AMBER) + cyl(x, 26, 354, 4, 9, DARK)
    hull += [box([-60, 28, -368], [120, 8, 6], PANEL), box([-50, 30, -370], [100, 3, 3], DARK), box([-8, 30, -372], [16, 4, 3], CLIGHT)]
    for name, s, zz in (("rotor_fl", 1, -PZ), ("rotor_fr", -1, -PZ), ("rotor_rl", 1, PZ), ("rotor_rr", -1, PZ)):
        cx = s * PX
        blades = cyly(cx, zz, 32, 8, 6, DARK) + cyly(cx, zz, 40, 2, 4.5, STEEL)
        for a in range(0, 360, 60):
            blades.append({"origin": [cx - 3, 36, zz + 4.5], "size": [6, 1.2, R - 6], "pivot": [cx, 36, zz], "rotation": [0, a, 0], "uv": BLADE})
        bones.append({"name": name, "parent": "hull", "pivot": [cx, 36, zz], "cubes": blades})
    radar = [box([60, 176, -63.5], [44, 11, 3], STEEL), box([59, 174.5, -64.5], [46, 1.6, 5], PANEL), box([80, 168, -64], [8, 8, 6], DARK), box([62, 178, -64.5], [40, 7, 0.8], GRILLE)]
    bones[1]["cubes"] = hull
    bones.append({"name": "radar", "parent": "hull", "pivot": [82, 176, -62], "cubes": radar})
    return bones


# ------------------------------------------------------------------ animation
def spin(speed, length=1.0, sign=1):
    return {"rotation": {f"{t * length / 8:.3f}": [0, sign * speed * t * length / 8, 0] for t in range(9)}}


def animations(key, moving, spinners):
    idle = {"hull": {"position": {"0.0": [0, 0, 0], "2.0": [0, 0.15, 0], "4.0": [0, 0, 0]}}}
    mov = {"hull": {"position": {"0.0": [0, 0, 0], "0.5": [0, 0.2, 0], "1.0": [0, 0, 0]}}}
    for b, sgn in spinners.items():
        mov[b] = spin(720, 1.0, sgn)
        idle[b] = spin(120, 4.0, sgn)
    idle["radar"] = spin(60, 4.0)
    mov["radar"] = spin(180, 1.0)
    return {"format_version": "1.8.0", "animations": {
        f"animation.{key}.idle": {"loop": True, "animation_length": 4.0, "bones": idle},
        f"animation.{key}.{moving}": {"loop": True, "animation_length": 1.0, "bones": mov}}}


# ------------------------------------------------------------------ icons: a 16x16 side silhouette per vessel
def icon(kind):
    rows = {
        "patrol_boat": ["................", "................", "......gg........", ".....gGGg.......", ".....GGGG..r....", "..k..GGGG..r....",
                        ".kkGGGGGGGGGGGG.", "hhhhhhhhhhhhhhh.", "bbbbbbbbbbbbbb..", ".rrrrrrrrrrrr..."],
        "patrol_frigate": ["................", ".......r........", "......gggg......", ".....gGGGGg.....", "....gGGGGGGg.pp.", "..k.gGGGGGGg.pp.",
                           ".kkGGGGGGGGGGGGG", "hhhhhhhhhhhhhhhh", "bbbbbbbbbbbbbbbb", ".rrrrrrrrrrrrrr."],
        "sky_carrier": ["................", "...........gg...", "..........gGGg..", "ffff.....gGGGGg.", "hhhhhhhhhhhhhhhh", "GGGGGGGGGGGGGGGG",
                        "bbbbbbbbbbbbbbbb", ".bbbbbbbbbbbbbb.", "ff..ff....ff..ff", "................"],
    }[kind]
    pal = {"g": (110, 160, 200), "G": (164, 168, 170), "k": (90, 94, 98), "h": (190, 196, 198), "b": (60, 64, 68),
           "r": (190, 50, 44), "p": (80, 86, 82), "f": (240, 240, 240)}
    rows = ["." * 16] * (16 - len(rows)) + [r.ljust(16, ".")[:16] for r in rows]
    buf = bytearray()
    for r in rows:
        for ch in r:
            buf += bytes(pal[ch]) + b"\xff" if ch in pal else b"\0\0\0\0"
    return make_png(16, 16, bytes(buf))


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
                assert f["uv"][0] + f["uv_size"][0] <= 512 and f["uv"][1] + f["uv_size"][1] <= 512, c
    for a in anim["animations"].values():
        for bn in a["bones"]:
            assert bn in names, bn
    assert "hull" in names
    return n


ZOOMS = {"sky_carrier": {"island": (85, -35, 3.4, 35), "stern": (0, 300, 2.2, 215), "pod": (150, -260, 3.0, 40)},
         "patrol_frigate": {"bridge": (0, -40, 4.0, 35), "stern": (0, 150, 3.0, 215)},
         "patrol_boat": {"bow": (0, -60, 6.0, 30)}}


def shifted(geo, ox, oz):
    """Preview-only copy with the model moved so (ox, oz) is at the view centre."""
    g = json.loads(json.dumps(geo))
    for b in g["minecraft:geometry"][0]["bones"]:
        for c in b.get("cubes", []):
            c["origin"][0] -= ox
            c["origin"][2] -= oz
            if "pivot" in c:
                c["pivot"][0] -= ox
                c["pivot"][2] -= oz
    return g


def main():
    tex = texture()
    ships = {
        "patrol_boat": (pb_bones, "sail", {}, (8.0, 6.0, 1.0), dict(yaw=40, pitch=-24, sc=3.6)),
        "patrol_frigate": (ff_bones, "sail", {}, (20.0, 12.0, 4.0), dict(yaw=40, pitch=-24, sc=1.55)),
        "sky_carrier": (cv_bones, "fly", {"rotor_fl": 1, "rotor_fr": -1, "rotor_rl": -1, "rotor_rr": 1}, (52.0, 14.0, 6.0), dict(yaw=40, pitch=-26, sc=0.82)),
    }
    for key, (fn, moving, spinners, (bw, bh, by), pv) in ships.items():
        tex.save(os.path.join(ROOT, f"textures/entity/transport/{key}.png"))
        with open(os.path.join(ROOT, f"textures/item/{key}.png"), "wb") as f:
            f.write(icon(key))
        geo_path = os.path.join(ROOT, f"geo/{key}.geo.json")
        write_geo(geo_path, f"geometry.{key}", fn(), bw, bh, by)
        anim = animations(key, moving, spinners)
        with open(os.path.join(ROOT, f"animations/{key}.animation.json"), "w") as f:
            json.dump(anim, f, indent=2)
        geo = json.load(open(geo_path))
        for b in geo["minecraft:geometry"][0]["bones"]:
            for c in b.get("cubes", []):
                if "face" in c:
                    keep = c.pop("face")
                    for fn, f in c["uv"].items():
                        if fn != keep:
                            f["uv"], f["uv_size"] = [0, 500], [1, 1]  # transparent corner of the atlas
        json.dump(geo, open(geo_path, "w"), indent=2)
        print(key, "OK:", validate(geo, anim), "cubes")
        if "--preview" in sys.argv:
            out = sys.argv[sys.argv.index("--preview") + 1]
            base = out.replace(".png", f"_{key}")
            preview(geo, tex.buf, base + "_a.png", W=1100, H=640, **pv)
            preview(geo, tex.buf, base + "_b.png", W=1100, H=640, **{**pv, "yaw": 215})
            preview(geo, tex.buf, base + "_top.png", W=1100, H=640, **{**pv, "yaw": 20, "pitch": -62})
            for tag, (ox, oz, sc, yaw) in ZOOMS.get(key, {}).items():
                preview(shifted(geo, ox, oz), tex.buf, base + f"_{tag}.png", W=1100, H=640, yaw=yaw, pitch=-24, sc=sc)


if __name__ == "__main__":
    main()
