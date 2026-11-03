"""Riot Police role set (registry faction "Police"): slab-armoured riot cab with a wire-meshed vision slit,
roof light bar and PA horns, a caged crowd-scanner head, and a push-bar chest. Navy + white door panels,
Battenburg chequer bands. Riot shield and stun baton are weapons and stay in build_exoframe_geo.py."""
import json
import os

from ._common import *  # noqa: F401,F403

SET_ID = "police"
# only the top 76 rows: ../scratch/build_weapon_textures_and_uvs.py repaints y >= 736
UV_REGION = ("Police", [(0, 660, 250, 76)])

PAL = {"paint": (26, 34, 52), "paint2": (18, 24, 38), "white": (226, 230, 234), "batten": None,
       "dark": (30, 32, 36), "steel": (112, 116, 120), "rubber": (22, 22, 24), "glass": (24, 44, 62),
       "mesh": None, "lamp_blue": (40, 120, 255), "lamp_red": (235, 36, 36), "lamp_white": (255, 248, 220),
       "lamp_amber": (255, 160, 20)}

_MAT = {}


def _stripe(x, y):
    return (230, 232, 236) if (x // 3 + y // 3) % 2 else (20, 70, 200)   # Battenburg chequer


def _add(out, bone, mat, *boxes):
    out.setdefault(bone, []).extend(boxes)
    _MAT.setdefault(bone, []).extend([mat] * len(boxes))


def build(a=A):
    _MAT.clear()
    o = {}
    H, C, K = "armor_head_police", "canopy_police", "armor_chest_police"

    # ---- head: crowd-scanner block forward of the cab brow, caged behind a wire-mesh face guard ----
    _add(o, H, "paint", (-2.4, 31.4, -6.6, 4.8, 3.2, 2.8))                    # sensor housing
    _add(o, H, "paint2", (-2.0, 34.6, -6.2, 4.0, 0.6, 2.2))                   # top cap
    _add(o, H, "glass", (-1.8, 32.2, -6.8, 3.6, 1.4, 0.3))                    # wide-angle visor
    _add(o, H, "lamp_white", (-1.6, 31.6, -6.8, 0.6, 0.5, 0.3), (1.0, 31.6, -6.8, 0.6, 0.5, 0.3))
    _add(o, H, "mesh", (-2.6, 31.2, -7.6, 5.2, 3.8, 0.2))                     # wire-mesh guard
    _add(o, H, "steel", *sym((2.4, 31.0, -7.8, 0.4, 4.2, 1.4), (2.4, 35.0, -7.8, 0.4, 0.4, 4.0)),
         (-2.8, 35.0, -7.8, 5.6, 0.4, 0.4), (-2.8, 30.8, -7.8, 5.6, 0.4, 0.4))   # guard frame
    _add(o, H, "dark", *sym((2.4, 32.0, -5.8, 0.6, 1.6, 2.0)))                # side cameras
    _add(o, H, "lamp_blue", (-0.5, 35.2, -5.6, 1.0, 0.6, 1.0))                # strobe
    _add(o, H, "dark", (1.6, 35.2, -4.8, 0.2, 3.0, 0.2))                      # stub antenna

    # ---- canopy: boxy armoured cab, roof above the roll hoop ----
    _add(o, C, "paint", (-6.0, 36.2, -4.0, 12.0, 0.8, 13.8))                  # roof slab
    _add(o, C, "paint2", (-6.2, 35.4, -4.4, 12.4, 0.8, 0.8))                  # brow lip
    _add(o, C, "paint2", rot_box(4.6, 35.6, -4.0, 1.8, 0.8, 13.8, 5.5, 36.2, 3.0, 0, 0, -40),
         rot_box(-6.4, 35.6, -4.0, 1.8, 0.8, 13.8, -5.5, 36.2, 3.0, 0, 0, 40))   # chamfered roof edges
    _add(o, C, "paint", (-6.0, 31.6, -4.0, 12.0, 3.8, 0.8))                   # front plate above slit
    _add(o, C, "paint", (-6.0, 21.4, -4.0, 12.0, 6.2, 0.8))                   # front plate below slit
    _add(o, C, "glass", (-3.6, 27.6, -3.7, 7.2, 4.0, 0.3))                    # vision slit
    _add(o, C, "paint2", *sym((3.6, 27.6, -4.0, 2.4, 4.0, 0.8)))              # slit pillars
    _add(o, C, "mesh", (-3.6, 27.6, -4.3, 7.2, 4.0, 0.2))                     # wire mesh over the slit
    _add(o, C, "steel", *[(x, 27.4, -4.6, 0.3, 4.4, 0.4) for x in (-3.4, -1.8, -0.15, 1.5, 3.1)])
    _add(o, C, "paint2", (-6.2, 25.0, -4.6, 12.4, 0.6, 0.8))                  # welded seam strap
    _add(o, C, "paint", *sym((5.3, 21.4, -4.0, 0.7, 14.8, 13.4)))             # side walls
    _add(o, C, "white", *sym((6.0, 24.6, -2.0, 0.2, 6.6, 7.6)))               # white door panels
    _add(o, C, "batten", *sym((6.0, 22.4, -3.8, 0.25, 1.6, 13.0)))            # Battenburg band
    _add(o, C, "glass", *sym((6.0, 32.0, 0.0, 0.15, 1.4, 5.0)))               # side slits
    _add(o, C, "mesh", *sym((6.15, 31.8, -0.2, 0.15, 1.8, 5.4)))
    _add(o, C, "steel", *sym((6.0, 24.2, 6.6, 0.4, 0.6, 1.2), (6.0, 30.4, 6.6, 0.4, 0.6, 1.2)))   # door hinges
    _add(o, C, "paint", (-6.0, 20.4, 9.5, 12.0, 16.6, 0.3))                   # rear wall
    _add(o, C, "paint2", *sym((5.2, 20.4, 9.2, 1.0, 16.6, 1.0)))              # rear corner posts
    _add(o, C, "lamp_red", *sym((5.5, 22.0, 10.2, 0.6, 1.2, 0.2)))            # tail lamps
    # light bar + PA
    _add(o, C, "dark", (-4.8, 37.0, 0.2, 9.6, 0.5, 2.0))
    _add(o, C, "lamp_blue", (0.5, 37.5, 0.3, 1.9, 0.9, 1.8), (2.5, 37.5, 0.3, 1.9, 0.9, 1.8))
    _add(o, C, "lamp_red", (-2.4, 37.5, 0.3, 1.9, 0.9, 1.8), (-4.4, 37.5, 0.3, 1.9, 0.9, 1.8))
    _add(o, C, "dark", (-0.4, 37.5, 0.1, 0.8, 1.1, 2.2))                      # siren driver
    _add(o, C, "dark", *sym((1.0, 37.0, -3.8, 1.6, 1.2, 1.6)))               # PA horns
    _add(o, C, "rubber", *sym((1.2, 37.2, -3.9, 1.2, 0.8, 0.1)))
    _add(o, C, "paint2", (-2.4, 37.0, 3.4, 4.8, 0.4, 4.4))                    # roof hatch
    _add(o, C, "steel", (-0.6, 37.4, 6.6, 1.2, 0.3, 0.6))                     # hatch latch
    _add(o, C, "dark", (5.4, 34.0, -5.0, 1.2, 1.2, 1.4))                      # pillar spotlight
    _add(o, C, "lamp_white", (5.5, 34.1, -5.1, 1.0, 1.0, 0.1))
    _add(o, C, "dark", (-5.6, 37.0, 8.8, 0.2, 8.0, 0.2), (-5.8, 37.0, 8.6, 0.6, 0.6, 0.6))   # whip antenna

    # ---- chest: lower glacis + riot push bar ----
    _add(o, K, "paint", (-4.6, 14.4, -4.8, 9.2, 7.0, 0.8))                    # lower glacis
    _add(o, K, "batten", (-4.6, 19.4, -5.0, 9.2, 1.2, 0.2))
    _add(o, K, "white", (-2.4, 16.2, -5.0, 4.8, 2.2, 0.2))                    # unit number plate
    _add(o, K, "steel", (-5.6, 15.0, -6.6, 11.2, 1.0, 1.0), (-5.6, 18.4, -6.6, 11.2, 1.0, 1.0))
    _add(o, K, "dark", *sym((2.2, 14.4, -6.4, 0.9, 5.4, 1.8), (4.6, 14.4, -6.4, 0.9, 5.4, 1.8)))
    _add(o, K, "rubber", *sym((1.6, 15.2, -7.0, 2.0, 3.6, 0.4)))              # ram pads
    _add(o, K, "lamp_blue", (4.8, 19.4, -6.8, 0.8, 0.6, 0.3))
    _add(o, K, "lamp_red", (-5.6, 19.4, -6.8, 0.8, 0.6, 0.3))
    _add(o, K, "paint", *sym((4.1, 14.4, -4.6, 0.5, 6.8, 10.4)))              # side skirts
    _add(o, K, "batten", *sym((4.6, 18.0, -4.4, 0.2, 1.2, 10.0)))
    _add(o, K, "paint", *leg_fairing())
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
