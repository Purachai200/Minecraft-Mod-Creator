"""Three walkable patrol ships with empty gun pedestals (hard-points) for external cannons:
fast attack craft (FAC), offshore patrol vessel (OPV) and a stealth corvette."""
import math
from fleet_common import *
from fleet_interior import *

SLICE = 12


def make_hull(zb, zs, hw0, wl, deck_fn, bow_frac=0.40, stern_frac=0.12, flare=6, inner=None, zstop=None):
    """Hull as 12 px slices. inner = {'floor': y, 'ranges': [(za, zb)], 'hatches': [(xa, xb, za, zb)]} hollows those slices into a
    below-deck compartment (floor, side walls, deck slab with stair hatches). Returns (cubes, half-width fn, inner-clear half-width fn)."""
    L = zs - zb

    def B(z):
        t = (z - zb) / (bow_frac * L)
        if t < 1: return 3 + (hw0 - 3) * max(0.0, t) ** 0.62 + flare * (1 - max(0.0, t))
        s = (z - (zs - stern_frac * L)) / (stern_frac * L)
        return hw0 * (1 - 0.26 * s) if s > 0 else hw0

    def Hb(z): return max(2.0, B(z) - 5 - 10 * max(0.0, 1 - (z - zb) / (bow_frac * L))) - 3     # clear half width at the lower walls

    out, z = [], zb
    while z < (zstop or zs) - 0.01:
        z1 = min(z + SLICE, zstop or zs); zm = (z + z1) / 2; hw = B(zm); yt = deck_fn(zm)
        bow = max(0.0, 1 - (zm - zb) / (bow_frac * L)); hb = max(2.0, hw - 5 - 10 * bow)
        if inner and any(za <= z and z1 <= zz for za, zz in inner["ranges"]):
            f = inner["floor"]
            out += [box(-hb, 0, z, hb, f, z1, BELLY, up=WALK)]
            for s in (-1, 1):
                out += [wall(s, hb - 3, hb, f, wl, z, z1, BELLY), wall(s, hw - 3, hw, wl, yt - 3, z, z1, HULL), box(s * (hb - 3), wl - 2, z, s * hw, wl, z1, BELLY)]
            hole = next(((xa, xb, z, z1) for xa, xb, za, zz in inner["hatches"] if za <= z and z1 <= zz), None)
            out += slab(-hw, hw, z, z1, yt - 3, 3, hole)
        else:
            out += [box(-max(2, hb - 9), 0, z, max(2, hb - 9), 10, z1, BELLY), box(-hb, 10, z, hb, wl, z1, BELLY), box(-hw, wl, z, hw, yt, z1, HULL, up=WALK)]
        z = z1
    if not zstop: out.append(box(-B(zs) * 0.96, wl, zs, B(zs) * 0.96, deck_fn(zs - 1), zs + 1.2, HULL))        # transom
    return out, B, Hb


def rail(B, deck_fn, z0, z1, step=14, h=11, sides=(-1, 1)):
    out, z = [], z0
    pts = []
    while z < z1 + 0.01: pts.append(min(z, z1)); z += step
    for s in sides:
        for z in pts: out.append(tube((s * (B(z) - 1.6), deck_fn(z), z), (s * (B(z) - 1.6), deck_fn(z) + h, z), 1.1, SPIN))
        for a, b in zip(pts, pts[1:]):
            for hh in (h, h * 0.5): out.append(tube((s * (B(a) - 1.6), deck_fn(a) + hh, a), (s * (B(b) - 1.6), deck_fn(b) + hh, b), 0.8, SPIN))
    return out


def mount(name, x, y, z, big=False):
    """Empty gun pedestal: bolted ring plate + ready-ammo locker. The locator is the gun's pivot (centre of the ring top)."""
    r = 10 if big else 7
    c = [box(x - r * 0.62, y, z - r * 0.62, x + r * 0.62, y + 6, z + r * 0.62, DARK), box(x - r, y + 6, z - r, x + r, y + 8, z + r, SPIN),
         box(x - r + 1, y + 8, z - r + 1, x + r - 1, y + 8.4, z + r - 1, DARK)]
    for dx in (-1, 1):
        for dz in (-1, 1): c.append(box(x + dx * (r - 1.8) - 0.8, y + 8.4, z + dz * (r - 1.8) - 0.8, x + dx * (r - 1.8) + 0.8, y + 9.6, z + dz * (r - 1.8) + 0.8, DARK))
    k = -1 if x > 0 else 1                                                                       # ammo locker on the inboard side so it never overhangs
    c += [box(x + k * (r + 1), y, z - 3.5, x + k * (r + 7), y + 7, z + 3.5, HULL), box(x + k * (r + 7), y + 1, z - 2.6, x + k * (r + 7.6), y + 6, z + 2.6, DOOR)]
    c.append(box(x - r - 0.4, y + 6, z - 0.8, x - r + 0.6, y + 8, z + 0.8, RED))                 # safety stripe on the bow side
    return bone(name, "hull", [x, y + 8, z], c, locators={name: [x, y + 8, z]})


def liferaft(x, y, z): return [box(x - 3, y, z - 6, x + 3, y + 5, z + 6, WHITE), box(x - 3.2, y + 2, z - 0.8, x + 3.2, y + 3, z + 0.8, DARK)]


def hpad(x0, x1, z0, z1, y, cz=None, cx=0):
    """Helideck: 'H' and ring in WHITE, edge safety net posts."""
    cz = cz if cz is not None else (z0 + z1) / 2
    c = [box(cx - 12, y + 0.05, cz - 14, cx - 9, y + 0.5, cz + 14, WHITE), box(cx + 9, y + 0.05, cz - 14, cx + 12, y + 0.5, cz + 14, WHITE), box(cx - 9, y + 0.05, cz - 1.5, cx + 9, y + 0.5, cz + 1.5, WHITE)]
    for a in range(0, 360, 20):
        r = 30; x, z = cx + r * math.cos(math.radians(a)), cz + r * math.sin(math.radians(a))
        c.append(box(x - 1.6, y + 0.05, z - 1.6, x + 1.6, y + 0.5, z + 1.6, WHITE))
    return c


def raked_bridge(cx, y, z, w, h, lean=12):
    return [rbox(cx, y + h / 2, z, w, h, 1, [lean, 0, 0], GLASS)] + [rbox(x, y + h / 2, z - 0.2, 1.4, h + 0.6, 1.4, [lean, 0, 0], HULL) for x in range(int(cx - w / 2), int(cx + w / 2) + 1, 12)]


def windows(s, x, y, z0, z1, h=7, w=7, gap=6, mat=WINDOW):
    return [box(s * x, y, z, s * (x + 0.8), y + h, z + w, mat) for z in range(int(z0), int(z1), w + gap)]


def finish(hull, extra, mounts, radar, name_meta, extra_bones=()):
    bones = [bone("root", None, [0, 0, 0], []), bone("hull", "root", [0, 0, 0], hull + extra, locators={m["bone"]: m["pos"] for m in name_meta["mounts"]}),
             *mounts, *extra_bones]
    if radar: bones.append(radar)
    return bones


# ============================================================ walkable parts
def tier(hw, z0, z1, yb, h, rooms, doors_z=(), front=(), back=(), stair=None, ceil_hole=None, only=None):
    """Deckhouse tier: walls with doors + window openings, furnished rooms split by bulkheads, ceiling slab (stair hole)."""
    if stair: ceil_hole = (stair[0], stair[1], stair[2] - 6, stair[3])                          # hole starts 6 px early so the player's head clears the slab on the first steps
    y1, out, ot = yb + h, [], [(zc - 7, zc + 7, yb, yb + DOOR_H, "door") for zc in doors_z]
    z = z0 + 8
    while z + 8 <= z1 - 4:
        if all(abs(z + 4 - zc) > 13 for zc in doors_z): ot.append((z, z + 8, yb + 14, yb + 27, "win"))
        z += 14
    for s in (-1, 1): out += wz(s, hw, yb, y1 - 2, z0, z1, ot)
    out += wx(z0 + T, -hw, hw, yb, y1 - 2, front, ext="north") + wx(z1, -hw, hw, yb, y1 - 2, back, ext="south")
    for i, (za, zb, kind) in enumerate(rooms):
        if i: out += wx(za, -hw + T, hw - T, yb, y1 - 2, [(-7, 7, yb, yb + DOOR_H, "door")])
        out += furnish(kind, hw - T - 1, yb, za + T, zb - T, side_only=only)
    out += slab(-hw, hw, z0, z1, y1 - 2, 2, ceil_hole, top=WALK, bot=INTER)
    if stair: out += stairs(*stair[:4], yb, y1)
    return out


def lower(rooms, dk, floor, Hb, hatch, end_open=None):
    """Below-deck compartments: bulkheads with doors (centre when wide, aisle side when narrow), furniture, hatch stairs."""
    out = []
    for za, zb, kind in rooms:
        hwr = min(Hb(za + 1), Hb(zb - 1)) - 1
        dx = (-7, 7) if hwr >= 22 else (-hwr + 1, min(0.0, -hwr + 15))
        out += wx(za, -(Hb(za) + 2), Hb(za) + 2, floor, dk(za) - 3, [(dx[0], dx[1], floor, floor + DOOR_H, "door")])
        if kind == "stairs": out += stairs(hatch[0], hatch[1], hatch[2] + 10, hatch[3], floor, dk(hatch[3]), n=int((dk(hatch[3]) - floor) // 4))   # 10 px landing under the hole, 4 px risers
        else: out += furnish(kind, hwr, floor, za + T, zb)
    za, zb, _ = rooms[-1]
    return out + wx(zb, -(Hb(zb) + 2), Hb(zb) + 2, floor, dk(zb) - 3, [(-7, 7, floor, end_open, "door")] if end_open else [])


def bollards(B, dk, zs):
    out = []
    for z in zs:
        for s in (-1, 1):
            x = s * (B(z) - 6); y = dk(z)
            out += [box(x - 1.4, y, z - 1.4, x + 1.4, y + 7, z + 1.4, DARK), box(x - 2.4, y + 6, z - 2.4, x + 2.4, y + 8, z + 2.4, DARK)]
    return out


# ============================================================ 1. Fast attack craft
def fac():
    D, zb, zs, hw0, wl = 44, -140, 140, 30, 18
    dk = lambda z: D + (4 if z < -96 else 0)
    inner = {"floor": 8, "ranges": [(-44, 112)], "hatches": [(1, 15, 16, 52)]}
    hull, B, Hb = make_hull(zb, zs, hw0, wl, dk, 0.45, inner=inner)
    ex = lower([(-44, 16, "bunks"), (16, 52, "stairs"), (52, 112, "engine")], dk, 8, Hb, (1, 15, 16, 52))
    ex += tier(17, 8, 68, D, 36, [(8, 68, "bridge")], doors_z=(24,), front=[(-13, 13, D + 12, D + 28, "win")], back=[(-7, 7, D, D + DOOR_H, "door")], only=-1)
    ex += H.solid(12, 50, 12, D + 36, D + 46, c=4) + [box(-13.4, D + 46, 12, 13.4, D + 48, 60, DARK, up=WALK)]
    for s in (-1, 1):
        ex += [box(s * 9, D, 72, s * 15, D + 36, 78, HULL), box(s * 9, D + 36, 72, s * 15, D + 41, 78, SOOT)]
        ex += liferaft(s * 21, D, 86) + liferaft(s * 21, D, 98) + [box(s * 8, D, 82, s * 16, D + 4, 92, DARK)]
        ex += [box(s * 15, D + 48, 20, s * 17, D + 54, 40, DARK, up=SPIN)]
    ex += rail(B, dk, -108, 128, 14) + [tube((-B(136) + 1.6, D, 136), (B(136) - 1.6, D, 136), 0.9, SPIN)]
    ex += [tube((0, D + 48, 32), (0, D + 92, 32), 3, DARK), tube((-12, D + 80, 32), (12, D + 80, 32), 1.4, DARK), box(-1.4, D + 92, 31, 1.4, D + 104, 33, RED),
           box(-5, D + 48, 14, 5, D + 54, 20, WHITE)]
    ex += bollards(B, dk, (-120, -60, 90, 126)) + [tube((0, D, 134), (0, D + 38, 134), 1.3, SPIN)]
    mounts = [mount("mount_bow", 0, D + 4, -92, True), mount("mount_stern", 0, D, 100, True), mount("mount_mg_l", 13, D + 48, 46), mount("mount_mg_r", -13, D + 48, 46)]
    radar = bone("radar", "hull", [0, D + 104, 32], [box(-2.5, D + 104, 29.5, 2.5, D + 108, 34.5, DARK), box(-16, D + 108, 31, 16, D + 110.6, 33, HULL)])
    meta = {"id": "fac_patrol", "name": "Fast Attack Patrol Craft", "tier": 1, "seat_capacity": 6, "payload": "crew only; 4 gun hard-points (2 large, 2 pintle)",
            "hull_rgb": (120, 128, 136), "belly_rgb": (96, 48, 40), "seats": {"helm": [-8, D, 28], "co_helm": [-8, D, 40], "bunks": [7, 8, -20]},
            "decks": {"foredeck": [[-18, D + 4, -118], [18, D + 4, 6]], "side_walkway_l": [[19, D, 6], [B(40) - 3, D, 120]], "side_walkway_r": [[-(B(40) - 3), D, 6], [-19, D, 120]],
                      "stern_deck": [[-22, D, 66], [22, D, 134]], "pilothouse_floor": [[-17, D, 9], [17, D, 55]], "pilothouse_roof": [[-16, D + 48, 12], [16, D + 48, 52]],
                      "lower_deck": [[-13, 8, -44], [13, 8, 112]]},
            "interior": ["lower deck (floor y=8): bunk room -44..16, stair hatch 16..52 (x 4..17), engine room 52..112", "pilothouse: bridge consoles, rear door, side doors"],
            "mounts": [{"bone": "mount_bow", "pos": [0, D + 12, -92], "class": "large", "facing": 0, "arc": 280, "pitch": [-8, 70]},
                       {"bone": "mount_stern", "pos": [0, D + 8, 100], "class": "large", "facing": 180, "arc": 280, "pitch": [-8, 70]},
                       {"bone": "mount_mg_l", "pos": [13, D + 56, 46], "class": "pintle", "facing": 90, "arc": 200, "pitch": [-15, 60]},
                       {"bone": "mount_mg_r", "pos": [-13, D + 56, 46], "class": "pintle", "facing": -90, "arc": 200, "pitch": [-15, 60]}],
            "scale": 1.3, "bounds_w": 20, "bounds_h": 10, "bounds_off": [0, 3, 0], "view": (35, -22)}
    return finish(hull, ex, mounts, radar, meta), meta


# ============================================================ 2. Offshore patrol vessel
def opv():
    D, zb, zs, hw0, wl = 44, -210, 210, 36, 18
    dk = lambda z: D + (14 if z < -96 else 0)
    inner = {"floor": 8, "ranges": [(-150, 102)], "hatches": [(8, 24, -66, -30)]}
    hull, B, Hb = make_hull(zb, zs, hw0, wl, dk, 0.38, inner=inner)
    ex = lower([(-150, -108, "stores"), (-108, -66, "bunks"), (-66, -14, "stairs"), (-14, 42, "mess"), (42, 102, "engine")], dk, 8, Hb, (8, 24, -66, -30))
    ex += step_run(2, -84, -96, 14, 26, D, D, D + 14, 2) + step_run(2, -84, -96, -26, -14, D, D, D + 14, 2)
    ex += tier(24, -84, -8, D, 36, [(-84, -8, "stairs")], doors_z=(-30,), front=[(-7, 7, D, D + DOOR_H, "door")],
               back=[(-7, 7, D, D + DOOR_H, "door")], stair=(-22, -6, -46, -18), ceil_hole=(-22, -6, -46, -18), only=-1)
    ex += tier(25, -66, -14, D + 36, 36, [(-66, -14, "bridge")], doors_z=(-40,), front=[(-21, 21, D + 48, D + 64, "win")], back=[(-7, 7, D + 36, D + 36 + DOOR_H, "door")], only=1)
    ex += [box(s * 25, D + 36, -66, s * 56, D + 38, -14, DARK, up=WALK) for s in (-1, 1)]
    for s in (-1, 1):
        ex += [tube((s * 56, D + 38, z), (s * 56, D + 49, z), 1.1, SPIN) for z in range(-66, -13, 12)] + [tube((s * 56, D + 49, -66), (s * 56, D + 49, -14), 0.9, SPIN), tube((s * 25, D + 49, -66), (s * 56, D + 49, -66), 0.9, SPIN)]
        ex += [box(s * 55, D + 49, -44, s * 56.4, D + 54, -40, RED if s > 0 else GREEN)]
    ex += [box(-23, D + 72, -68, 23, D + 74, -12, DARK, up=WALK)]
    ex += [rbox(0, D + 35, 8, 28, 70, 24, [-4, 0, 0], HULL, pivot=[0, D, 8]), rbox(0, D + 73, 8.4, 29, 6, 25, [-4, 0, 0], SOOT, pivot=[0, D, 8]),
           rbox(0, D + 50, 8.2, 29, 5, 25, [-4, 0, 0], WHITE, pivot=[0, D, 8]), rbox(0, D + 56, 8.3, 29.2, 3, 25.2, [-4, 0, 0], RED, pivot=[0, D, 8])]
    ex += [tube((0, D + 74, -40), (0, D + 112, -40), 3.2, DARK), tube((-16, D + 100, -40), (16, D + 100, -40), 1.4, DARK), box(-8, D + 112, -46, 8, D + 126, -34, WHITE)]
    ex += tier(26, 40, 88, D, 36, [(40, 88, "hangar")], doors_z=(64,), front=[(-7, 7, D, D + DOOR_H, "door")], back=[(-20, 20, D, D + 34, "door")])
    ex += [box(-34, D - 1, 88, 34, D, 204, DARK, up=WALK)] + hpad(-34, 34, 88, 204, D)
    for s in (-1, 1): ex += [box(s * 34, D, 90, s * 36, D + 2, 204, RED)] + [box(s * 33, D, z, s * 36, D + 5, z + 2, DARK) for z in range(92, 204, 22)]
    ex += rail(B, dk, -184, 36, 14) + rail(B, dk, 92, 205, 22, 5)
    for s in (-1, 1):
        ex += liferaft(s * 32, D, -2) + liferaft(s * 32, D, 12) + [tube((s * 34, D, 118), (s * 34, D + 30, 118), 2, DARK), tube((s * 34, D + 30, 118), (s * 27, D + 34, 118), 1.8, DARK)]
    ex += bollards(B, dk, (-190, -130, 64, 190))
    mounts = [mount("mount_bow", 0, D + 14, -168, True), mount("mount_hangar", 0, D + 36, 64, True), mount("mount_waist_l", 33, D, 20), mount("mount_waist_r", -33, D, 20), mount("mount_bridge", 0, D + 74, -40)]
    radar = bone("radar", "hull", [0, D + 126, -40], [box(-3, D + 126, -43, 3, D + 131, -37, DARK), box(-22, D + 131, -41.2, 22, D + 134.4, -38.8, HULL)])
    meta = {"id": "opv_cutter", "name": "Offshore Patrol Vessel", "tier": 2, "seat_capacity": 6, "payload": "crew + 1 helicopter on the helideck (Mi-17 / UH-60 can land); 5 gun hard-points",
            "hull_rgb": (206, 210, 214), "belly_rgb": (96, 44, 38), "seats": {"helm": [10, D + 36, -50], "co_helm": [-10, D + 36, -50], "captain": [0, D + 36, -30], "bunks": [21, 8, -80]},
            "decks": {"forecastle": [[-26, D + 14, -196], [26, D + 14, -96]], "main_deck": [[-28, D, -92], [28, D, 36]], "helideck": [[-34, D, 88], [34, D, 204]],
                      "tier1_floor": [[-28, D, -83], [28, D, -9]], "bridge_floor": [[-23, D + 36, -65], [23, D + 36, -15]], "bridge_wings": [[-56, D + 38, -66], [56, D + 38, -14]],
                      "bridge_roof": [[-23, D + 74, -68], [23, D + 74, -12]], "hangar_floor": [[-24, D, 41], [24, D, 87]], "lower_deck": [[-24, 8, -150], [24, 8, 102]]},
            "interior": ["lower deck (floor y=8): stores -150..-108, bunks -108..-42, stair hatch -42..-6 (x 8..22), mess/galley -6..42, engine room 42..102",
                         "tier 1: officers' cabins + stair to bridge; tier 2: bridge with consoles and wing doors; hangar aft of the funnel"],
            "mounts": [{"bone": "mount_bow", "pos": [0, D + 22, -168], "class": "large", "facing": 0, "arc": 280, "pitch": [-8, 75]},
                       {"bone": "mount_hangar", "pos": [0, D + 44, 64], "class": "large", "facing": 180, "arc": 300, "pitch": [-5, 85]},
                       {"bone": "mount_waist_l", "pos": [33, D + 8, 20], "class": "pintle", "facing": 90, "arc": 180, "pitch": [-10, 60]},
                       {"bone": "mount_waist_r", "pos": [-33, D + 8, 20], "class": "pintle", "facing": -90, "arc": 180, "pitch": [-10, 60]},
                       {"bone": "mount_bridge", "pos": [0, D + 82, -40], "class": "pintle", "facing": 0, "arc": 360, "pitch": [-10, 80]}],
            "scale": 0.95, "bounds_w": 30, "bounds_h": 14, "bounds_off": [0, 5, 0], "view": (35, -25)}
    return finish(hull, ex, mounts, radar, meta), meta


# ============================================================ 3. Stealth corvette
def corvette():
    D, zb, zs, hw0, wl = 44, -260, 260, 42, 18
    dk = lambda z: D + (8 if z < -152 else 0)
    inner = {"floor": 8, "ranges": [(-152, 136)], "hatches": [(8, 24, -56, -20)]}
    hull, B, Hb = make_hull(zb, zs, hw0, wl, dk, 0.40, flare=10, inner=inner)
    ex = lower([(-152, -104, "bunks"), (-104, -56, "bunks"), (-56, -8, "stairs"), (-8, 40, "mess"), (40, 136, "engine")], dk, 8, Hb, (8, 24, -56, -20))
    ex += tier(28, -90, 60, D, 36, [(-90, -52, "officers"), (-52, -8, "stairs"), (-8, 24, "mess"), (24, 60, "stores")], doors_z=(-70, 40),
               front=[(-7, 7, D, D + DOOR_H, "door")], back=[(-7, 7, D, D + DOOR_H, "door")], stair=(-24, -8, -42, -14), ceil_hole=(-24, -8, -42, -14), only=-1)
    ex += tier(22, -70, -6, D + 36, 36, [(-70, -6, "bridge")], doors_z=(-38,), front=[(-18, 18, D + 48, D + 64, "win")], back=[(-7, 7, D + 36, D + 36 + DOOR_H, "door")], only=1)
    for s in (-1, 1): ex += [rbox(s * 31, D + 20, -15, 1.6, 40, 150, [0, 0, s * 10], HULL)]
    ex += [box(-23, D + 72, -72, 23, D + 74, -4, DARK, up=WALK)] + H.solid(4, 34, 14, D + 36, D + 106, c=5)
    for s in (-1, 1): ex += [rbox(s * 15, D + 92, 19, 1.4, 22, 20, [0, 0, s * 12], DARK)]
    ex += [box(-11, D + 106, 14, 11, D + 118, 24, WHITE), box(-8, D + 118, 15, 8, D + 122, 23, DARK), tube((0, D + 122, 19), (0, D + 148, 19), 1.6, SPIN)]
    ex += [box(-20, D, -152, 20, D + 2, -108, DARK, up=WALK)]
    for i in range(6):
        for j in range(4): ex.append(box(-17.5 + j * 9.5, D + 2, -148 + i * 7.2, -11.5 + j * 9.5, D + 2.8, -143 + i * 7.2, DARK))
    for s in (-1, 1):
        for k in range(4): ex.append(rbox(s * 33, D + 6 + (k % 2) * 6, 76 + (k // 2) * 6, 5, 5, 24, [-25, 0, 0], DARK))
        ex.append(box(s * 29, D, 68, s * 37, D + 6, 100, HULL))
    ex += tier(26, 104, 152, D, 36, [(104, 152, "hangar")], doors_z=(128,), front=[(-7, 7, D, D + DOOR_H, "door")], back=[(-20, 20, D, D + 34, "door")])
    ex += [box(-36, D - 1, 152, 36, D, 256, DARK, up=WALK)] + hpad(-36, 36, 152, 256, D, cz=204)
    for s in (-1, 1): ex += [box(s * 36, D, 154, s * 38, D + 2, 256, RED)]
    ex += rail(B, dk, -240, 56, 14) + rail(B, dk, 160, 250, 24, 5) + bollards(B, dk, (-240, -190, -100, 90, 240))
    mounts = [mount("mount_bow_main", 0, D + 8, -202, True), mount("mount_ciws_fwd", 0, D + 74, -40), mount("mount_ciws_aft", 0, D + 36, 128), mount("mount_aux_l", 37, D, -120), mount("mount_aux_r", -37, D, -120)]
    radar = bone("radar", "hull", [0, D + 148, 19], [box(-3, D + 148, 16, 3, D + 152, 22, DARK), box(-20, D + 152, 18, 20, D + 155, 20, HULL)])
    meta = {"id": "corvette_stealth", "name": "Stealth Corvette", "tier": 3, "seat_capacity": 8, "payload": "crew + 1 helicopter on the helideck; 5 gun hard-points incl. a main gun on the foredeck",
            "hull_rgb": (112, 120, 128), "belly_rgb": (70, 44, 40), "seats": {"helm": [10, D + 36, -40], "co_helm": [-10, D + 36, -40], "captain": [0, D + 36, -20], "bunks": [27, 8, -130]},
            "decks": {"foredeck": [[-28, D + 8, -238], [28, D + 8, -156]], "main_deck_walkway_l": [[31, D, -150], [B(0) - 3, D, 104]], "main_deck_walkway_r": [[-(B(0) - 3), D, -150], [-31, D, 104]],
                      "vls_deck": [[-20, D + 2, -152], [20, D + 2, -108]], "helideck": [[-36, D, 152], [36, D, 256]], "tier1_floor": [[-28, D, -89], [28, D, 59]],
                      "bridge_floor": [[-20, D + 36, -69], [20, D + 36, -7]], "bridge_roof": [[-22, D + 74, -72], [22, D + 74, -4]], "hangar_floor": [[-24, D, 105], [24, D, 151]],
                      "lower_deck": [[-30, 8, -152], [30, 8, 136]]},
            "interior": ["lower deck (floor y=8): 2 bunk rooms -152..-56, stair hatch -56..-20 (x 8..22), mess/galley -20..40, engine room 40..136",
                         "tier 1: officers, stair to bridge, wardroom, stores; tier 2: bridge; hangar aft"],
            "mounts": [{"bone": "mount_bow_main", "pos": [0, D + 16, -202], "class": "large", "facing": 0, "arc": 300, "pitch": [-8, 75]},
                       {"bone": "mount_ciws_fwd", "pos": [0, D + 82, -40], "class": "pintle", "facing": 0, "arc": 360, "pitch": [-5, 85]},
                       {"bone": "mount_ciws_aft", "pos": [0, D + 44, 128], "class": "pintle", "facing": 180, "arc": 360, "pitch": [-5, 85]},
                       {"bone": "mount_aux_l", "pos": [37, D + 8, -120], "class": "pintle", "facing": 90, "arc": 180, "pitch": [-10, 60]},
                       {"bone": "mount_aux_r", "pos": [-37, D + 8, -120], "class": "pintle", "facing": -90, "arc": 180, "pitch": [-10, 60]}],
            "scale": 0.72, "bounds_w": 38, "bounds_h": 14, "bounds_off": [0, 5, 0], "view": (35, -25)}
    return finish(hull, ex, mounts, radar, meta), meta


def ships_anims(name):
    return lambda: anim_file(name, {"idle": {"loop": True, "bones": {"radar": {"rotation": [0, 0, 0]}}},
                                    "radar_spin": {"loop": True, "animation_length": 4.0, "bones": spin({"radar": 1}, 4.0)}})
