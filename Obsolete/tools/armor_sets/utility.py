"""Generic utility backpacks (UTILITY slot): a welded cargo crate with tarp and jerrycan, twin ammo cans with a
flexible feed chute, and a folding search-radar mast with a phased-array panel. Field-drab paint, bolted brackets.
All three start at z 10.3, just behind the collar back beam, and keep inside the exhaust stacks (|x| < 4.8)."""
import json
import os

from ._common import *  # noqa: F401,F403

SET_ID = "utility"
# only the top 76 rows: ../scratch/build_weapon_textures_and_uvs.py repaints y >= 736
UV_REGION = ("Radar", [(750, 660, 250, 76)])
PACKED_BONES = ("backpack_radar", "backpack_cargo", "backpack_ammo")

PAL = {"paint": (78, 84, 62), "paint2": (60, 66, 48), "white": (220, 222, 210), "batten": None,
       "tarp": (98, 92, 66), "dark": (30, 32, 36), "steel": (130, 134, 138), "rubber": (24, 24, 26),
       "glass": (30, 50, 66), "mesh": None, "gold": (200, 160, 50), "lamp_red": (255, 40, 30),
       "lamp_white": (255, 250, 225), "lamp_amber": (255, 160, 20), "lamp_blue": (40, 120, 255)}

_MAT = {}


def _stripe(x, y):
    return (230, 190, 30) if (x + y) // 3 % 2 else (28, 28, 30)   # hazard tape


def _add(out, bone, mat, *boxes):
    out.setdefault(bone, []).extend(boxes)
    _MAT.setdefault(bone, []).extend([mat] * len(boxes))


def _mount(o, bone):
    _add(o, bone, "dark", (-4.0, 21.8, 10.3, 8.0, 9.4, 0.5))                 # bolt-on plate
    _add(o, bone, "steel", *sym((2.6, 30.4, 10.1, 0.8, 0.8, 0.8), (2.6, 22.4, 10.1, 0.8, 0.8, 0.8)))


def build(a=A):
    _MAT.clear()
    o = {}
    # ---- cargo crate ----
    G = "backpack_cargo"
    _mount(o, G)
    _add(o, G, "paint", (-4.2, 22.2, 10.8, 8.4, 7.6, 4.2))                    # crate
    _add(o, G, "paint2", *sym((3.8, 22.0, 10.6, 0.6, 8.0, 4.6)), (-4.4, 22.0, 15.0, 8.8, 0.6, 0.4),
         (-4.4, 29.4, 15.0, 8.8, 0.6, 0.4))                                    # welded angle frame
    _add(o, G, "tarp", (-4.0, 29.8, 10.9, 8.0, 1.6, 4.0), (-3.6, 31.4, 11.3, 7.2, 0.6, 3.2))   # tarp bundle
    _add(o, G, "rubber", *sym((1.6, 21.9, 15.1, 0.6, 10.2, 0.2), (1.6, 31.9, 10.9, 0.6, 0.2, 4.4)))  # straps
    _add(o, G, "steel", *sym((1.5, 26.0, 15.2, 0.8, 0.8, 0.3)))               # ratchets
    _add(o, G, "white", (-2.8, 24.0, 15.05, 3.4, 2.4, 0.1))                   # stencilled cargo plate
    _add(o, G, "batten", (-4.2, 22.4, 15.05, 8.4, 0.6, 0.1))
    _add(o, G, "paint2", (-4.6, 22.4, 11.2, 0.4, 5.2, 3.4))                   # jerrycan (right side)
    _add(o, G, "steel", (-4.7, 27.6, 12.2, 0.4, 0.6, 1.2))

    # ---- ammo cans ----
    M = "backpack_ammo"
    _mount(o, M)
    _add(o, M, "paint", *sym((0.3, 22.4, 10.8, 4.0, 6.4, 3.8)))               # cans
    _add(o, M, "paint2", *sym((0.2, 28.8, 10.7, 4.2, 0.6, 4.0)))              # lids
    _add(o, M, "steel", *sym((1.6, 29.4, 12.0, 1.4, 0.4, 1.4), (4.3, 25.0, 11.6, 0.3, 1.4, 2.2)))   # handles, latches
    _add(o, M, "white", *sym((0.8, 24.6, 14.65, 3.0, 1.2, 0.1)))              # lot stencils
    _add(o, M, "batten", *sym((0.3, 22.8, 14.65, 4.0, 0.4, 0.1)))
    _add(o, M, "dark", *[(1.2 - 0.0, 29.4 + i * 0.9, 11.6 - i * 0.55, 2.0, 0.9, 1.2) for i in range(6)])  # feed chute
    _add(o, M, "dark", (1.2, 34.6, 7.6, 2.0, 0.9, 1.6))
    _add(o, M, "steel", *[(1.1, 29.6 + i * 1.8, 11.5 - i * 1.1, 2.2, 0.3, 1.4) for i in range(3)])

    # ---- search radar ----
    R = "backpack_radar"
    _mount(o, R)
    _add(o, R, "paint", (-3.0, 22.4, 10.8, 6.0, 5.0, 3.0))                    # electronics box
    _add(o, R, "dark", *[(-2.6, 23.0 + i * 0.9, 13.85, 5.2, 0.4, 0.1) for i in range(4)])   # cooling slots
    _add(o, R, "steel", (-0.8, 27.4, 11.6, 1.6, 15.0, 1.6))                   # mast
    _add(o, R, "paint2", (-1.1, 33.0, 11.3, 2.2, 0.8, 2.2), (-1.1, 38.0, 11.3, 2.2, 0.8, 2.2))   # telescope collars
    _add(o, R, "dark", (-1.4, 42.4, 11.0, 2.8, 1.6, 2.8))                     # slew ring
    _add(o, R, "paint", (-6.0, 44.0, 11.6, 12.0, 5.6, 0.8))                   # phased-array panel
    _add(o, R, "gold", *[(x, 44.6, 11.4, 1.0, 4.4, 0.2) for x in (-5.4, -3.6, -1.8, 0.8, 2.6, 4.4)])
    _add(o, R, "paint2", (-6.2, 43.8, 12.4, 12.4, 6.0, 0.4), *sym((5.8, 43.8, 11.4, 0.4, 6.0, 1.4)))
    _add(o, R, "steel", *sym(rot_box(0.6, 37.0, 12.0, 0.4, 7.4, 0.4, 0.8, 37.0, 12.2, 0, 0, -38)))  # struts
    _add(o, R, "lamp_red", (-0.3, 49.8, 11.8, 0.6, 0.6, 0.6))                 # aircraft warning lamp
    _add(o, R, "dark", (2.4, 27.4, 11.8, 0.2, 9.0, 0.2), (2.2, 27.0, 11.6, 0.6, 0.6, 0.6))   # whip
    return o   # authored directly in final model space (no back_fit)


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
    if m == "glass":
        c = (150, 190, 220) if (lx + ly) % 7 == 0 and not edge else PAL[m]
        return (*c, 255)
    if m == "mesh":
        c = (86, 90, 94) if lx % 3 == 0 or ly % 3 == 0 else (10, 12, 16)
        return (*c, 255)
    if m == "batten":
        c = _stripe(x, y)
    elif m in ("paint", "paint2"):
        c = PAL[m] if camo_id == 0 else _camo(PAL[m], x, y, n_med, n_coarse, camo_id)
        if m == "paint2":
            c = tuple(int(v * 0.8) for v in c)
    else:
        c = PAL[m]
    painted = m in ("paint", "paint2", "white", "batten")
    k = 0.88 + 0.2 * n_fine
    if painted and w >= 8 and h >= 6 and (lx in (1, w - 2) or ly in (1, h - 2)) and (lx + ly) % 3 == 0:
        k *= 1.35                                     # bolt heads along the plate edge
    if edge:
        k *= 0.7                                      # weld seam / shadow line
    if painted and n_fine > 0.9 and n_med > 0.6:
        c, k = (118, 114, 108), 1.0                   # chipped to bare steel
    if painted:
        k *= 1.0 - 0.25 * max(0.0, n_coarse - 0.5) * (ly / max(h, 1))   # grime collects low
    return (*(max(0, min(255, int(v * k))) for v in c), 255)
