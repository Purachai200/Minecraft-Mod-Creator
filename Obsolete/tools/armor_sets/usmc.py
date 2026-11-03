"""Marine Raider (registry faction "USMC"): olive-drab armored capsule with vision blocks, smoke-discharger
cheeks, roof work lamps and twin whips; track-link glacis; vented legs; radio + jerry-can backpack."""
from ._common import *  # noqa: F401,F403

SET_ID = "usmc"
UV_REGION = ("USMC", [(260, 0, 70, 315), (260, 315, 80, 85)])

# ---- role tagging: paint() re-runs build() and colours each packed cube by its role ----
_ROLE = {}


def _k(b):
    return tuple(round(v, 3) for v in b[:3]) + tuple(round(max(v, 0.1), 3) for v in b[3:6])


def T(role, *boxes):
    for b in boxes:
        _ROLE[_k(b)] = role
        _ROLE[_k(mx(b))] = role
    return list(boxes)


def build(a=A):
    head = (T("armor", (-2.4, 31.2, -3.4, 4.8, 2.4, 2.2), rot_box(-2.6, 33.4, -3.8, 5.2, 0.8, 2.4, 0, 33.6, -3.4, -14, 0, 0))
            + T("dark", (-2.2, 31.8, -3.7, 4.4, 1.0, 0.3))
            + T("lens", (-1.9, 32.0, -3.9, 0.9, 0.6, 0.3), (-0.45, 32.0, -3.9, 0.9, 0.6, 0.3), (1.0, 32.0, -3.9, 0.9, 0.6, 0.3)))
    chest = (T("armor", (-5.6, 15.0, -5.0, 11.2, 8.0, 1.3), rot_box(-5.4, 23.0, -5.0, 10.8, 6.0, 1.1, 0, 23.0, -3.9, 14, 0, 0),
               *sym((3.2, 16.0, -5.6, 2.2, 6.0, 0.6)))                                    # glacis + bolted cheek appliques
             + T("stencil", rot_box(-2.4, 24.6, -5.4, 4.8, 3.2, 0.4, 0, 23.0, -3.9, 14, 0, 0))
             + T("track", *[(-2.6, 16.2 + i * 1.3, -5.7, 5.2, 1.0, 0.7) for i in range(3)])
             + T("dark", *sym((3.6, 13.4, -5.6, 1.0, 1.4, 1.6), (4.0, 28.6, -4.6, 1.4, 1.2, 1.0))))
    chest += T("armor", *leg_fairing())
    canopy = (T("armor", *build_box_canopy())
              + T("armor", *sym((6.7, 21.0, -1.8, 0.5, 9.0, 9.0)))                      # bolted cheek appliques
              + T("dark", *sym((7.2, 25.4, -1.4, 0.3, 0.4, 8.2), (2.6, 32.0, -3.9, 2.4, 1.0, 0.3)))
              + T("lens", *sym((2.8, 32.2, -4.0, 2.0, 0.5, 0.2)))                          # vision blocks
              + T("dark", *sym(*[rot_box(6.9, 30.0 + i * 1.0, -2.8, 0.9, 0.9, 2.2, 7.3, 30.4 + i * 1.0, -1.7, -30, 0, 0)
                                 for i in range(3)]))                                     # smoke dischargers
              + T("dark", *sym((3.8, 35.3, -2.4, 1.4, 1.2, 1.4))) + T("lamp", *sym((3.9, 35.4, -2.7, 1.2, 1.0, 0.3)))
              + T("dark", *sym((4.4, 34.7, 8.4, 0.8, 0.6, 0.8), (4.65, 35.3, 8.65, 0.3, 10.0, 0.3))))
    pauldron = (T("armor", rot_box(6.6, 33.6, -4.2, 6.2, 1.2, 8.2, 9.5, 33.6, 0.0, 0, 0, -8), (12.2, 25.6, -4.0, 1.2, 8.0, 7.6),
                  (7.2, 27.6, -4.8, 5.4, 6.0, 1.0), (7.2, 27.6, 2.2, 5.4, 6.0, 1.0))
                + T("accent", (13.4, 27.6, -2.8, 0.3, 4.0, 5.2))
                + T("dark", (7.4, 34.6, -3.0, 4.2, 0.6, 0.6), (7.4, 34.6, 1.6, 4.2, 0.6, 0.6)))
    cuisse = (T("armor", (2.6, 16.0, -2.4, 3.8, 1.2, 4.6), (6.0, 10.6, -3.0, 1.2, 6.0, 5.2), (2.6, 11.0, -4.4, 3.6, 5.4, 1.2))
              + T("dark", *[(2.9, 11.6 + i * 1.4, -4.7, 3.0, 0.5, 0.3) for i in range(3)], (2.8, 8.0, -5.4, 3.2, 3.2, 2.0))
              + T("accent", (7.2, 12.0, -2.0, 0.3, 3.6, 3.2)))
    greave = (T("armor", (2.6, 3.0, -5.8, 4.0, 6.8, 1.4), (6.1, 2.2, -3.8, 1.2, 7.4, 6.0), (3.0, 3.0, 3.8, 3.0, 5.8, 1.2))
              + T("track", (2.8, 4.2, -6.4, 3.6, 1.0, 0.6))
              + T("dark", (2.4, 8.6, -6.0, 4.4, 1.2, 1.6)))
    backpack = (T("dark", (-3.8, 21.6, 10.4, 7.6, 9.0, 0.6))
                + T("armor", (-5.2, 21.4, 11.0, 4.6, 6.4, 3.0), (-5.0, 27.8, 11.2, 4.2, 0.4, 2.6))
                + T("accent", (0.8, 21.4, 11.0, 2.0, 4.6, 2.8), (3.0, 21.4, 11.0, 2.0, 4.6, 2.8))
                + T("dark", (1.4, 26.0, 11.6, 0.8, 0.5, 1.6), (3.6, 26.0, 11.6, 0.8, 0.5, 1.6), (-4.6, 23.0, 14.0, 3.4, 2.0, 0.3))
                + T("bag", (-4.4, 28.6, 11.4, 8.8, 1.8, 2.2))
                + T("dark", (-4.6, 28.2, 13.0, 0.3, 11.0, 0.3)))
    out = {"armor_head_usmc": head, "armor_chest_usmc": chest, "canopy_usmc": canopy, "backpack_usmc": backpack,
           "armor_left_shoulder_usmc": pauldron, "armor_right_shoulder_usmc": [mx(b) for b in pauldron]}
    out.update(mirror_pair("armor_left_leg_usmc", "armor_right_leg_usmc", cuisse))
    out.update(mirror_pair("armor_left_shin_usmc", "armor_right_shin_usmc", greave))
    return out


# ---------------- paint ----------------
PAL = {"main": (86, 96, 62), "dark": (46, 50, 42), "accent": (70, 78, 50), "bag": (120, 112, 80),
       "track": (54, 54, 52), "lens": (120, 200, 170), "lamp": (255, 236, 170), "stencil": (225, 205, 120),
       "metal": (120, 118, 110), "rust": (118, 70, 38), "text": "21"}
# ==== shared painter (identical in sand / usmc / cerberus) ====
import json as _json, os as _os, sys as _sys  # noqa: E402

_MAP = None
_FONT = {"0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001011001111",
         "4": "101101111001001", "5": "111100111001111", "7": "111001010010010", "9": "111101111001111"}


def _map():
    global _MAP
    if _MAP is None:
        _MAP = {}
        _ROLE.clear()
        build(A)
        path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "packed_armor_uvs.json")
        for e in _json.load(open(path)):
            if e["faction"] != UV_REGION[0]:
                continue
            role = _ROLE.get(tuple(e["origin"]) + tuple(e["size"]), "armor")
            for face, (u0, v0, u1, v1) in e["faces"].items():
                for y in range(v0, v1):
                    for x in range(u0, u1):
                        _MAP[(x, y)] = (role, face, x - u0, y - v0, u1 - u0, v1 - v0)
    return _MAP


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _mul(c, k):
    return tuple(c[i] * k for i in range(3))


def _out(c):
    return tuple(max(0, min(255, int(v))) for v in c[:3]) + (255,)


def paint(x, y, camo_id, nf, nm, nc):
    info = _map().get((x, y))
    if info is None:
        return None
    role, face, lx, ly, fw, fh = info
    P = PAL
    side = face not in ("top", "bottom")
    edge = lx == 0 or ly == 0 or lx == fw - 1 or ly == fh - 1
    if role in ("lens", "lamp"):
        c = P[role]
        return _out(_mul(c, 0.55) if edge and fw > 2 else _mix(c, (255, 255, 255), 0.25 * nf))
    if role == "bag":
        c = _mul(P["bag"], 0.82 + 0.3 * nf)
        if edge or (side and lx == fw // 2):
            c = _mul(c, 0.7)
        return _out(_mix(c, (90, 72, 50), 0.4 * nc))
    if role == "track":
        c = _mul(P["track"], 0.85 + 0.3 * nf)
        if (lx + ly) % 2 == 0:
            c = _mul(c, 0.7)
        if edge:
            c = _mix(c, P["metal"], 0.6)
        return _out(_mix(c, P["rust"], 0.5 * max(0.0, nc - 0.5)))
    if role == "dark":
        base = P["dark"]
    elif role == "accent":
        base = P["accent"]
    else:
        base = P["main"]
        cb = getattr(_sys.modules.get("__main__"), "camo_base", None)
        if camo_id and cb is not None:
            try:
                base = cb(camo_id, x, y, nm, nc)
            except Exception:
                pass
    c = _mul(base, 0.93 + 0.12 * nm)
    if side:
        c = _mul(c, 1.0 - 0.18 * ly / max(1, fh))          # grime settles low
        if nc > 0.62 and lx % 5 == 2:
            c = _mix(c, P["rust"], (nc - 0.62) * 1.6 * ly / max(1, fh))   # rust streaks
    if edge and fw > 2 and fh > 2:
        c = _mul(c, 0.7)                                    # welded seam / panel line
        if nf > 0.7:
            c = _mix(c, P["metal"], 0.6)                                # chipped to bare steel
    elif fh >= 8 and ly == fh // 2 and side:
        c = _mul(c, 0.78 if lx % 2 else 0.95)               # weld bead across tall slabs
    elif fw >= 4 and fh >= 4 and ly in (1, fh - 2) and lx % 3 == 1 and 0 < lx < fw - 1:
        c = _mix(c, (225, 220, 205), 0.35)                  # bolt row
    elif fw >= 4 and fh >= 4 and ly in (2, fh - 1) and lx % 3 == 1 and 0 < lx < fw - 1:
        c = _mul(c, 0.75)                                   # bolt shadow
    elif nf > 0.86 and nm > 0.55:
        c = _mix(c, P["metal"], 0.5)                        # scattered chips
    if role == "stencil" and face == "north":
        txt = P["text"]
        tw = 4 * len(txt) - 1
        ox, oy = (fw - tw) // 2, (fh - 5) // 2
        gx, gy = lx - ox, ly - oy
        if 0 <= gy < 5 and 0 <= gx < tw and gx % 4 < 3:
            g = _FONT.get(txt[gx // 4], "")
            if g and g[gy * 3 + gx % 4] == "1" and nf < 0.8:
                c = P["stencil"]
    return _out(c)
