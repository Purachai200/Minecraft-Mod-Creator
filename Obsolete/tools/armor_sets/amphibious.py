"""Amphibious Assault role set (registry faction "Amphibious"): a fat segmented pontoon collar slung round the
pelvis outside the arms, with lashing straps, grab lines, CO2 inflation bottles, a bow light and mounting struts.
Marine orange pontoon cells, black rubber straps, stencilled reflective bands."""
import json
import os

from ._common import *  # noqa: F401,F403

SET_ID = "amphibious"
# only the top 76 rows: ../scratch/build_weapon_textures_and_uvs.py repaints y >= 736
UV_REGION = ("Amphibious", [(500, 660, 250, 76)])

PAL = {"paint": (236, 112, 18), "paint2": (190, 86, 12), "white": (232, 234, 236), "batten": None,
       "dark": (30, 32, 36), "steel": (150, 154, 158), "rubber": (24, 24, 26), "glass": (30, 50, 66),
       "mesh": None, "lamp_blue": (40, 120, 255), "lamp_red": (255, 40, 30), "lamp_white": (255, 250, 225),
       "lamp_amber": (255, 160, 20), "silver": (186, 192, 200)}

_MAT = {}


def _stripe(x, y):
    return (240, 244, 248) if (x // 4) % 2 else (40, 40, 44)   # reflective tape with black stencil breaks


def _add(out, bone, mat, *boxes):
    out.setdefault(bone, []).extend(boxes)
    _MAT.setdefault(bone, []).extend([mat] * len(boxes))


def build(a=A):
    _MAT.clear()
    o, B = {}, "armor_float_ring"
    HX, ZF, ZB = 12.4, -9.0, 14.2       # outside the hanging arms (x 10.8) and the power pack (z 12.8)
    _add(o, B, "paint", *round_ring(14.4, 2.8, HX, ZF, ZB, r=3.6, t=1.8))          # pontoon belly
    _add(o, B, "paint2", *round_ring(13.8, 0.6, HX - 0.3, ZF + 0.3, ZB - 0.3, r=3.4, t=1.2))   # keel seam
    _add(o, B, "paint2", *round_ring(17.2, 0.7, HX - 0.3, ZF + 0.3, ZB - 0.3, r=3.4, t=1.2))   # top seam
    _add(o, B, "batten", *round_ring(16.0, 0.4, HX + 0.05, ZF - 0.05, ZB + 0.05, r=3.6, t=0.2, n=2))
    # lashing straps that cut the collar into cells
    straps = [(HX - 1.9, 13.6, z, 2.0, 4.4, 0.6) for z in (-3.0, 2.4, 7.8)]
    straps += [(x, 13.6, ZF - 0.1, 0.6, 4.4, 2.0) for x in (2.0, 6.4)]
    straps += [(x, 13.6, ZB - 1.9, 0.6, 4.4, 2.0) for x in (2.0, 6.4)]
    _add(o, B, "rubber", *sym(*straps))
    # grab lines along the outside
    _add(o, B, "rubber", *sym(*[(HX + 0.05, 15.8, z, 0.3, 0.3, 2.4) for z in (-5.0, 0.0, 5.0, 10.0)]))
    # CO2 inflation bottles and valves
    _add(o, B, "silver", *sym(*disc_z(HX - 0.9, 16.4, -8.4, 0.7, 2.4)))
    _add(o, B, "dark", *sym((HX - 1.3, 15.8, -9.3, 0.8, 1.2, 0.9)))
    _add(o, B, "lamp_red", *sym((HX - 1.2, 17.3, -9.4, 0.6, 0.4, 0.4)))
    # mounting struts to the pelvis
    _add(o, B, "steel", *sym((6.4, 15.6, -1.2, HX - 8.0, 0.6, 1.0), (6.4, 15.6, 6.0, HX - 8.0, 0.6, 1.0),
                             (6.2, 15.2, -1.4, 0.8, 1.4, 8.6)))
    # bow light and tow cleat
    _add(o, B, "dark", (-1.0, 16.6, ZF - 0.6, 2.0, 1.2, 0.8))
    _add(o, B, "lamp_white", (-0.7, 16.8, ZF - 0.7, 1.4, 0.8, 0.1))
    _add(o, B, "steel", (-1.2, 17.8, ZB - 1.0, 2.4, 0.5, 0.6), (-0.3, 17.2, ZB - 0.8, 0.6, 0.6, 0.4))
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
