"""Disaster Rescue role set (registry faction "Rescue"): fire-red crash cab with a raked, barred windshield,
roof floodlight rack, rotator beacons and a side ladder; thermal dome-pod head with twin floods; medic-plated
chest with a hydraulic cutter; A-frame winch pack with O2 bottles. Red/white with reflective chevrons."""
import json
import os

from ._common import *  # noqa: F401,F403

SET_ID = "rescue"
# only the top 76 rows: ../scratch/build_weapon_textures_and_uvs.py repaints y >= 736
UV_REGION = ("Rescue", [(250, 660, 250, 76)])

PAL = {"paint": (188, 28, 26), "paint2": (150, 22, 20), "white": (232, 234, 236), "batten": None,
       "orange": (255, 110, 10), "yellow": (240, 190, 30), "red": (214, 20, 20),
       "dark": (30, 32, 36), "steel": (150, 154, 158), "rubber": (22, 22, 24), "glass": (30, 50, 66),
       "mesh": None, "lamp_blue": (40, 120, 255), "lamp_red": (255, 40, 30), "lamp_white": (255, 250, 225),
       "lamp_amber": (255, 160, 20)}

_MAT = {}


def _stripe(x, y):
    return (235, 240, 60) if (x + y) // 3 % 2 else (200, 24, 22)   # reflective chevrons


def _add(out, bone, mat, *boxes):
    out.setdefault(bone, []).extend(boxes)
    _MAT.setdefault(bone, []).extend([mat] * len(boxes))


def build(a=A):
    _MAT.clear()
    o = {}
    H, C, K, B = "armor_head_rescue", "canopy_rescue", "armor_chest_rescue", "backpack_rescue"

    # ---- head: thermal dome pod with twin floods ----
    _add(o, H, "paint", (-2.2, 31.4, -6.8, 4.4, 2.8, 3.0))
    _add(o, H, "white", (-1.6, 34.2, -6.4, 3.2, 1.0, 2.4), (-1.0, 35.2, -6.0, 2.0, 0.5, 1.6))   # dome
    _add(o, H, "dark", *sym((1.0, 31.8, -7.4, 1.4, 1.4, 0.6)))
    _add(o, H, "lamp_white", *sym((1.15, 31.95, -7.5, 1.1, 1.1, 0.1)))
    _add(o, H, "glass", (-0.6, 32.2, -7.0, 1.2, 1.2, 0.3))                    # IR lens
    _add(o, H, "lamp_amber", (-0.3, 35.7, -5.6, 0.6, 0.4, 0.8))
    _add(o, H, "batten", *sym((2.2, 32.4, -6.6, 0.2, 0.8, 2.6)))
    _add(o, H, "steel", *sym((2.2, 31.0, -5.6, 0.5, 0.8, 1.6)))               # mount lugs

    # ---- canopy: crash cab with raked windshield ----
    _add(o, C, "paint", (-6.0, 36.2, -2.6, 12.0, 0.8, 12.4))                  # roof
    _add(o, C, "glass", rot_box(-5.0, 26.0, -4.6, 10.0, 10.4, 0.4, 0, 26.0, -4.4, 16, 0, 0))
    _add(o, C, "paint2", *sym(rot_box(5.0, 26.0, -5.0, 1.0, 10.4, 0.6, 5.5, 26.0, -4.4, 16, 0, 0)))
    _add(o, C, "steel", (-5.4, 29.0, -4.7, 10.8, 0.4, 0.4), (-5.4, 32.6, -3.7, 10.8, 0.4, 0.4))   # guard bars
    _add(o, C, "paint", (-6.0, 21.4, -4.6, 12.0, 4.6, 0.8))                   # lower front
    _add(o, C, "batten", (-6.0, 25.2, -4.8, 12.0, 0.8, 0.2))
    _add(o, C, "paint", *sym((5.3, 21.4, -4.4, 0.7, 15.6, 14.2)))             # side walls
    _add(o, C, "white", *sym((6.0, 31.0, -3.0, 0.2, 5.2, 12.0)))              # white upper band
    _add(o, C, "batten", *sym((6.0, 25.0, -4.2, 0.25, 1.2, 13.8)))
    _add(o, C, "glass", *sym((6.2, 32.0, 0.0, 0.15, 2.6, 6.0)))
    _add(o, C, "paint", (-6.0, 20.4, 9.5, 12.0, 16.6, 0.3))                   # rear wall
    _add(o, C, "paint2", *sym((5.2, 20.4, 9.2, 1.0, 16.6, 1.0)))
    # floodlight rack
    _add(o, C, "steel", (-5.6, 37.6, -2.8, 11.2, 0.5, 0.5), *sym((5.0, 37.0, -2.8, 0.5, 0.6, 0.5)))
    _add(o, C, "dark", *[(x, 38.1, -3.2, 1.8, 1.4, 1.2) for x in (-5.2, -2.3, 0.5, 3.4)])
    _add(o, C, "lamp_white", *[(x + 0.2, 38.3, -3.3, 1.4, 1.0, 0.1) for x in (-5.2, -2.3, 0.5, 3.4)])
    _add(o, C, "lamp_red", *sym((4.4, 37.0, 7.6, 1.2, 1.0, 1.2)))            # rotator beacons
    _add(o, C, "dark", *sym((4.3, 38.0, 7.5, 1.4, 0.3, 1.4)))
    _add(o, C, "orange", (-3.6, 37.0, 0.6, 7.2, 0.5, 6.4))                    # spine board on the roof
    _add(o, C, "dark", *sym((3.0, 37.0, 1.6, 0.8, 0.7, 0.4), (3.0, 37.0, 5.6, 0.8, 0.7, 0.4)))   # straps
    # side ladder (right)
    _add(o, C, "steel", (-6.5, 21.6, 6.6, 0.3, 15.0, 0.3), (-6.5, 21.6, 8.4, 0.3, 15.0, 0.3))
    _add(o, C, "steel", *[(-6.6, y, 6.6, 0.3, 0.3, 2.1) for y in (23.0, 25.4, 27.8, 30.2, 32.6, 35.0)])

    # ---- chest: medic glacis, tow hooks, hydraulic cutter, hose reel ----
    _add(o, K, "paint", (-4.6, 14.4, -5.0, 9.2, 7.0, 0.8))
    _add(o, K, "white", (-2.0, 16.2, -5.2, 4.0, 3.2, 0.2))
    _add(o, K, "red", (-0.4, 16.6, -5.35, 0.8, 2.4, 0.15), (-1.2, 17.4, -5.35, 2.4, 0.8, 0.15))
    _add(o, K, "batten", (-4.6, 20.2, -5.2, 9.2, 0.8, 0.2))
    _add(o, K, "steel", *sym((2.6, 14.4, -6.2, 0.8, 1.0, 1.2)))               # tow hooks
    _add(o, K, "yellow", (4.4, 15.6, -6.4, 1.2, 1.2, 5.0))                    # spreader body
    _add(o, K, "dark", (4.6, 15.8, -7.8, 0.4, 0.8, 1.4), (5.0, 15.8, -7.8, 0.4, 0.8, 1.4), (4.5, 16.8, -2.0, 1.0, 1.0, 1.4))
    _add(o, K, "yellow", *disc_x(-4.9, 17.6, 1.0, 1.6, 0.8))                  # hose reel
    _add(o, K, "red", *disc_x(-5.0, 17.6, 1.0, 0.6, 1.0))
    _add(o, K, "paint", *sym((4.1, 14.4, -4.6, 0.3, 6.8, 10.4)))
    _add(o, K, "paint", *leg_fairing())

    # ---- backpack: A-frame winch, O2 bottles ----
    _add(o, B, "dark", (-4.2, 21.8, 10.3, 8.4, 9.6, 0.6))                     # mount plate
    _add(o, B, "yellow", *disc_x(-3.0, 26.0, 12.6, 1.8, 6.0))                 # winch drum
    _add(o, B, "dark", *disc_x(-3.4, 26.0, 12.6, 2.3, 0.4), *disc_x(3.0, 26.0, 12.6, 2.3, 0.4))
    _add(o, B, "steel", (-2.8, 24.0, 10.9, 5.6, 0.6, 1.6))                    # cable fairlead
    _add(o, B, "steel", *sym((3.4, 31.4, 11.0, 0.8, 8.0, 0.8)), (-4.2, 39.4, 11.0, 8.4, 0.8, 0.8))   # A-frame
    _add(o, B, "steel", *sym((3.4, 31.4, 11.0, 0.8, 0.8, 4.0, 3.8, 31.8, 11.4, 30, 0, 0)))          # stays
    _add(o, B, "dark", *disc_x(-0.4, 39.0, 13.0, 1.0, 0.8))                   # sheave
    _add(o, B, "steel", (-0.6, 39.0, 11.4, 1.2, 0.5, 1.8))
    _add(o, B, "dark", (-0.15, 30.0, 13.8, 0.3, 9.0, 0.3))                    # cable
    _add(o, B, "yellow", (-0.6, 28.6, 13.4, 1.2, 1.4, 1.0))                   # hook block
    _add(o, B, "white", *sym((2.4, 21.8, 14.2, 2.0, 7.0, 2.0)))               # O2 bottles
    _add(o, B, "dark", *sym((3.0, 28.8, 14.8, 0.8, 0.8, 0.8)))
    _add(o, B, "batten", *sym((2.4, 23.0, 16.2, 2.0, 0.6, 0.05)))
    _add(o, B, "lamp_amber", (-0.5, 31.4, 10.6, 1.0, 0.6, 0.6))
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
