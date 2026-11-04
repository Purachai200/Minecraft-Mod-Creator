"""Mobility equipment (registry faction "Mobility").

Roller Dash Unit (UTILITY slot): a heel-mounted ground-roller pod per foot, VOTOMS "roller dash" style. Twin
rubber-tyred wheels on one axle either side of a motor/gearbox block, fenders, a damper strut and a skid shoe that
throws sparks. `roller_*_unit` pivots at the heel mount (Java folds it up when stowed); `roller_*_wheel` pivots
on the axle (Java spins it).

Hydro-Jet Propulsor (BACK slot): twin ducted water-jets on outriggers beside the power pack, saddle ballast tanks
above them, intake grilles, stator vanes and vectoring nozzles. `hydrojet_*_fan` pivots on the duct axis (Java
spins it about z). Naval grey with orange ballast bands.
"""
import json
import math
import os

from ._common import *  # noqa: F401,F403

SET_ID = "mobility"
# free band between the frame atlas (y < 520) and the role sets (y >= 660); the weapon painter owns x < 512 here
UV_REGION = ("Mobility", [(520, 524, 500, 132)])

PAL = {"paint": (88, 96, 104), "paint2": (64, 70, 78), "orange": (236, 112, 18), "dark": (30, 32, 36),
       "steel": (150, 154, 158), "chrome": (205, 210, 216), "rubber": (22, 22, 24), "tread": (40, 40, 42),
       "hazard": None, "mesh": None, "lamp_amber": (255, 160, 20), "lamp_blue": (40, 160, 255),
       "copper": (186, 106, 54)}

_MAT = {}


def _add(out, bone, mat, *boxes):
    out.setdefault(bone, []).extend(boxes)
    _MAT.setdefault(bone, []).extend([mat] * len(boxes))


def ring_z(cx, cy, z, r, d, n=12, s=0.7):
    """Ring of n small blocks round the z axis (a duct lip seen from behind)."""
    return [(cx + r * math.cos(a) - s / 2, cy + r * math.sin(a) - s / 2, z, s, s, d)
            for a in (2 * math.pi * i / n for i in range(n))]


# ---- roller pod, left foot (final model space; the right foot is the x mirror) ----
AXLE = (4.5, 1.4, 6.2)        # roller_left_wheel pivot
MOUNT = (4.5, 2.4, 4.6)       # roller_left_unit pivot: the heel hinge
WR = 1.4                      # tyre radius: the tyre bottom sits on the sole line (y 0)


def _roller(o, side):
    m = (lambda bs: list(bs)) if side == "left" else (lambda bs: [mx(b) for b in bs])
    U, Wh = f"roller_{side}_unit", f"roller_{side}_wheel"
    ax, ay, az = AXLE
    # wheels: outboard and inboard tyre on one axle, with hubs and a spoke bar so the spin reads
    for x0 in (5.6, 2.2):
        _add(o, Wh, "rubber", *m(disc_x(x0, ay, az, WR, 1.2)))
        _add(o, Wh, "tread", *m(ring_x(x0 - 0.05, ay, az, WR - 0.1, 1.3, n=10, s=0.45)))
        _add(o, Wh, "steel", *m(disc_x(x0 - 0.1, ay, az, 0.75, 1.4)))
        _add(o, Wh, "chrome", *m([(x0 - 0.15, ay - 0.15, az - 1.05, 1.5, 0.3, 2.1)]))      # spoke bar
        _add(o, Wh, "orange", *m([(x0 - 0.16, ay - 1.0, az - 0.15, 1.52, 0.5, 0.3)]))       # paint dot on the rim
    _add(o, Wh, "dark", *m([(3.4, ay - 0.3, az - 0.3, 2.2, 0.6, 0.6)]))                        # axle
    # motor / gearbox between the tyres
    _add(o, U, "paint", *m([(3.5, 0.9, 4.9, 2.0, 2.3, 2.6)]))
    _add(o, U, "dark", *m(disc_x(3.45, 2.0, 6.2, 0.9, 2.1)))                                   # motor can
    _add(o, U, "copper", *m([(4.1, 3.2, 5.3, 0.8, 0.3, 1.6)]))                                 # windings peek
    _add(o, U, "dark", *m([(3.6, 1.2, 4.7 + 0.5 * i, 1.8, 0.2, 0.25) for i in range(4)]))      # cooling ribs
    # fenders over each tyre, a bridge plate and the outboard guard
    _add(o, U, "paint2", *m([(5.5, 2.9, 4.6, 1.4, 0.4, 3.3), (2.1, 2.9, 4.6, 1.4, 0.4, 3.3),
                             (3.5, 3.2, 4.6, 2.0, 0.3, 3.0)]))
    _add(o, U, "paint2", *m([rot_box(5.5, 2.4, 7.6, 1.4, 0.4, 1.0, 6.2, 2.9, 7.9, 35, 0, 0),
                             rot_box(2.1, 2.4, 7.6, 1.4, 0.4, 1.0, 2.8, 2.9, 7.9, 35, 0, 0)]))
    _add(o, U, "hazard", *m([(6.85, 1.6, 4.9, 0.25, 1.3, 2.6)]))                                # outboard guard
    _add(o, U, "steel", *m([(6.9, 2.0, 6.0, 0.3, 0.4, 0.4)]))                                   # axle nut
    # heel hinge, damper strut to the calf and its clevis
    _add(o, U, "steel", *m(disc_x(3.3, MOUNT[1], MOUNT[2], 0.7, 2.4)))
    _add(o, U, "dark", *m([(3.0, 2.0, 4.3, 0.4, 1.2, 1.2), (5.6, 2.0, 4.3, 0.4, 1.2, 1.2)]))  # hinge cheeks
    _add(o, U, "chrome", *m([rot_box(4.25, 3.4, 5.6, 0.5, 2.6, 0.5, 4.5, 3.4, 5.85, -25, 0, 0)]))
    _add(o, U, "steel", *m([rot_box(4.1, 3.2, 5.4, 0.8, 1.2, 0.8, 4.5, 3.4, 5.8, -25, 0, 0)]))
    # skid shoe behind the tyres: steel on tarmac, this is where the sparks come from
    _add(o, U, "steel", *m([(3.4, 0.1, 7.5, 2.2, 0.6, 0.7)]))
    _add(o, U, "dark", *m([(3.5, 0.7, 7.4, 2.0, 0.9, 0.4)]))
    _add(o, U, "lamp_amber", *m([(4.2, 1.7, 7.75, 0.6, 0.4, 0.1)]))                            # dash beacon


# ---- hydro-jet pack (left duct; mirrored) ----
DUCT = (8.2, 18.5)        # duct axis (x, y); fan pivot z 12.0
DR = 2.3


def _hydrojet(o):
    B = "backpack_hydrojet"
    cx, cy = DUCT
    # duct shroud: two lips, a long shell and the nozzle cone
    for side, f in (("left", lambda bs: list(bs)), ("right", lambda bs: [mx(b) for b in bs])):
        _add(o, B, "paint", *f(ring_z(cx, cy, 8.8, DR, 0.9, n=14, s=0.9)))                   # intake lip
        _add(o, B, "paint", *f(ring_z(cx, cy, 9.7, DR - 0.1, 4.6, n=12, s=0.6)))             # shroud
        _add(o, B, "orange", *f(ring_z(cx, cy, 11.8, DR + 0.05, 0.7, n=12, s=0.65)))         # band
        _add(o, B, "paint2", *f(ring_z(cx, cy, 14.3, DR - 0.4, 1.2, n=12, s=0.7)))           # nozzle cone
        _add(o, B, "dark", *f(ring_z(cx, cy, 15.5, DR - 0.9, 1.0, n=10, s=0.6)))             # vectoring nozzle
        _add(o, B, "mesh", *f([(cx - 1.6, cy - 1.6, 8.85, 3.2, 3.2, 0.1)]))                  # intake grille
        _add(o, B, "steel", *f([(cx - 0.15, cy - DR + 0.3, 13.1, 0.3, 2 * DR - 0.6, 0.3),    # stator vanes
                                (cx - DR + 0.3, cy - 0.15, 13.1, 2 * DR - 0.6, 0.3, 0.3)]))
        _add(o, B, "dark", *f(disc_z(cx, cy, 12.9, 0.7, 2.6)))                               # tail cone / motor
        # saddle ballast tank above the duct with its blow valve
        _add(o, B, "paint2", *f(disc_z(cx, cy + 3.3, 8.4, 1.1, 6.8)))
        _add(o, B, "orange", *f([(cx - 1.15, cy + 2.7, 10.4, 2.3, 1.2, 0.5), (cx - 1.15, cy + 2.7, 13.0, 2.3, 1.2, 0.5)]))
        _add(o, B, "steel", *f([(cx - 0.3, cy + 4.3, 14.6, 0.6, 0.6, 0.6)]))
        _add(o, B, "lamp_blue", *f([(cx - 0.25, cy + 4.0, 15.15, 0.5, 0.5, 0.1)]))
        # outrigger: clamp plate on the power pack side, two arms out to the duct, a diagonal brace
        _add(o, B, "dark", *f([(6.0, 15.2, 9.2, 0.4, 5.6, 3.2)]))
        _add(o, B, "steel", *f([(6.0, 19.4, 9.6, 0.6, 0.6, 2.4), (6.0, 16.6, 9.6, 0.6, 0.6, 2.4)]))
        _add(o, B, "steel", *f([rot_box(5.0, 20.8, 10.2, 1.4, 0.5, 0.5, 5.7, 21.0, 10.4, 0, 0, -30)]))
        _add(o, B, "rubber", *f([(6.3, 21.4, 11.2, 0.4, 0.4, 3.6)]))                         # pump hose
    # cross beam under the power pack radiator ties both outriggers together
    _add(o, B, "dark", (-6.0, 14.6, 12.6, 12.0, 0.6, 0.8))
    _add(o, B, "hazard", (-2.0, 14.65, 13.35, 4.0, 0.5, 0.1))
    # fans: hub + 5 blades rotated about the duct axis
    for side, sgn in (("left", 1), ("right", -1)):
        Fb = f"hydrojet_{side}_fan"
        x = sgn * cx
        _add(o, Fb, "chrome", *disc_z(x, cy, 11.6, 0.6, 0.9))
        for i in range(5):
            a = 72.0 * i
            _add(o, Fb, "steel", rot_box(x - 0.2, cy, 11.8, 0.4, DR - 0.5, 0.25, x, cy, 11.9, 0, 18 * sgn, a))


def build(a=A):
    _MAT.clear()
    o = {}
    _roller(o, "left")
    _roller(o, "right")
    _hydrojet(o)
    return o


# ---------------- texture ----------------
_TEX = None


def _texmap():
    global _TEX
    if _TEX is None:
        _TEX = {}
        build()
        p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "packed_armor_uvs.json")
        for e in json.load(open(p)):
            mats = _MAT.get(e["bone"])
            if e["faction"] != UV_REGION[0] or not mats or e["cube_index"] >= len(mats):
                continue
            for f, (u0, v0, u1, v1) in e["faces"].items():
                for y in range(v0, v1):
                    for x in range(u0, u1):
                        _TEX[(x, y)] = (mats[e["cube_index"]], f, x - u0, y - v0, u1 - u0, v1 - v0)
    return _TEX


def _camo(c, x, y, nm, nc, camo):
    if camo == 1:
        v = ((x // 6) * 73856093 ^ (y // 6) * 19349663) % 100
        c = (74, 94, 52) if v < 35 else (46, 62, 34) if v < 60 else (102, 78, 52) if v < 82 else (22, 26, 20)
    elif camo == 2:
        c = (168, 142, 102) if nm > 0.6 else (205, 184, 138) if nm > 0.3 else (128, 102, 72)
    elif camo == 3:
        g = 34 + ((x // 8) + (y // 14) * 2) % 3 * 8
        c = (g, g + 2, g + 5)
    elif camo == 4:
        c = (232, 236, 240) if nm > 0.4 else (176, 184, 192)
    elif camo == 5:
        s = (y + int(math.sin(x * 0.08) * 8)) // 8 % 4
        c = ((24, 28, 22), (56, 82, 42), (112, 92, 58), (42, 60, 32))[s]
    elif camo == 6:
        c = (255, 204, 0) if nc < 0.65 else (150, 120, 20)
    return c


def paint(x, y, camo_id, n_fine, n_med, n_coarse):
    t = _texmap().get((x, y))
    if t is None:
        return (36, 38, 42, 255)
    m, f, lx, ly, w, h = t
    edge = lx in (0, w - 1) or ly in (0, h - 1)
    if m.startswith("lamp"):
        c = PAL[m] if not edge else tuple(v // 2 for v in PAL[m])
        return (*c, 255)
    if m == "mesh":
        c = (86, 90, 94) if lx % 2 == 0 or ly % 2 == 0 else (10, 12, 16)
        return (*c, 255)
    if m == "hazard":
        c = (236, 192, 30) if (x + y) // 2 % 2 else (28, 28, 30)
    elif m == "tread":
        c = (58, 58, 60) if (lx + ly) % 3 == 0 else (18, 18, 20)                 # chevron tread blocks
    elif m in ("paint", "paint2"):
        c = PAL[m] if camo_id == 0 else _camo(PAL[m], x, y, n_med, n_coarse, camo_id)
        if m == "paint2":
            c = tuple(int(v * 0.8) for v in c)
    else:
        c = PAL[m]
    painted = m in ("paint", "paint2", "orange", "hazard")
    k = 0.88 + 0.2 * n_fine
    if painted and w >= 6 and h >= 4 and (lx in (1, w - 2) or ly in (1, h - 2)) and (lx + ly) % 3 == 0:
        k *= 1.3                                      # rivets
    if edge:
        k *= 0.7
    if painted and n_fine > 0.9 and n_med > 0.6:
        c, k = (118, 114, 108), 1.0                   # chipped to bare steel
    if m in ("steel", "chrome") and n_fine > 0.85:
        k *= 0.8                                      # scuffs
    return (*(max(0, min(255, int(v * k))) for v in c), 255)
