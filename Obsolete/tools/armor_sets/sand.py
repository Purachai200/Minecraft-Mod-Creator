"""Sand PMC (registry faction "Sand"): open-top desert technical. Sandbag parapet on a bolted slab glacis,
spare track links, sun-shaded twin-lens sensor with a whip antenna, sandbagged pauldrons. No canopy or backpack."""
from ._common import *  # noqa: F401,F403

SET_ID = "sand"
UV_REGION = ("Sand", [(200, 0, 60, 240)])

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
    # ---- head: sun-shaded sensor box, twin lenses, whip antenna ----
    head = (T("armor", (-2.4, 31.2, -3.6, 4.8, 2.6, 2.4), (2.4, 31.0, -3.4, 0.4, 2.8, 2.0), (-2.8, 31.0, -3.4, 0.4, 2.8, 2.0))
            + T("armor", rot_box(-2.9, 33.6, -4.6, 5.8, 0.4, 2.6, 0, 33.8, -2.0, 12, 0, 0))      # sunshade
            + T("dark", (-2.0, 31.6, -3.9, 4.0, 1.8, 0.3), (1.9, 33.6, -2.2, 0.8, 0.5, 0.8))
            + T("lens", *disc_z(-1.0, 32.5, -4.2, 0.6, 0.4), *disc_z(1.0, 32.5, -4.2, 0.6, 0.4))
            + T("dark", (2.15, 34.1, -1.95, 0.3, 7.0, 0.3)))                                  # whip antenna
    # ---- chest: slab glacis, sandbag parapet, track links, side skirts, lamps, smoke dischargers ----
    chest = (T("armor", (-5.6, 15.4, -5.0, 11.2, 8.6, 1.2),                                     # lower glacis slab
               rot_box(-5.4, 23.8, -5.0, 10.8, 4.6, 1.0, 0, 24.0, -4.4, -22, 0, 0))            # raked upper glacis
             + T("stencil", (-2.6, 21.0, -5.4, 5.2, 2.6, 0.4))
             + T("track", *[(-3.8, 16.0 + i * 1.3, -5.8, 7.6, 1.0, 0.8) for i in range(3)])
             + T("dark", (-4.6, 13.4, -4.6, 9.2, 1.8, 8.4), (-5.8, 15.2, -5.3, 11.6, 0.4, 0.4))
             + T("bag", (-5.6, 27.6, -6.6, 3.6, 1.5, 2.4), (-1.8, 27.7, -6.8, 3.6, 1.6, 2.6), (2.0, 27.6, -6.6, 3.6, 1.5, 2.4),
                 (-3.8, 29.0, -6.3, 3.6, 1.3, 2.2), (0.2, 29.0, -6.3, 3.6, 1.3, 2.2))
             + T("armor", *sym((5.9, 15.0, -4.8, 0.9, 11.6, 9.0)))                             # side skirts
             + T("dark", *sym((6.8, 20.2, -4.6, 0.25, 0.4, 8.6), (6.8, 15.4, 3.6, 0.3, 10.8, 0.5)))
             + T("dark", (6.2, 25.8, -5.6, 1.4, 1.4, 1.4)) + T("lamp", (6.3, 25.9, -5.9, 1.2, 1.2, 0.3))
             + T("dark", *[rot_box(-7.6, 22.6 + i * 1.1, -3.6, 0.9, 0.9, 2.0, -7.2, 23.0 + i * 1.1, -2.6, -25, 0, 0)
                           for i in range(3)], (-7.0, 22.4, -2.4, 0.4, 3.4, 1.4)))
    chest = chest + T("armor", *leg_fairing())
    # ---- pauldron: angular slab, sandbag on top, track link drape ----
    pauldron = (T("armor", (6.6, 33.8, -3.8, 5.8, 1.0, 6.8), rot_box(12.0, 26.4, -3.8, 1.0, 7.6, 6.8, 12.4, 34.0, -0.4, 0, 0, 6),
                  (7.2, 28.6, -4.6, 5.0, 5.4, 0.8), (7.2, 28.6, 2.0, 5.0, 5.4, 0.8))
                + T("accent", (12.9, 29.0, -2.4, 0.3, 3.4, 4.0))
                + T("bag", (7.2, 34.8, -3.0, 3.8, 1.3, 4.8))
                + T("track", (11.0, 34.7, -3.4, 1.2, 0.6, 6.0))
                + T("dark", (6.8, 33.4, -3.4, 0.6, 0.4, 6.0)))
    # ---- thigh ----
    cuisse = (T("armor", (2.6, 10.6, -4.4, 4.0, 7.0, 1.0), (6.2, 9.6, -3.4, 1.0, 8.6, 5.6), (2.6, 16.6, -3.6, 4.0, 1.0, 5.6))
              + T("dark", (2.8, 8.0, -5.2, 3.6, 2.6, 1.4), (6.9, 13.0, -3.6, 0.5, 0.5, 6.0))
              + T("bag", (7.2, 10.4, -2.6, 1.2, 3.0, 3.6)))
    # ---- shin greave with track-link applique ----
    greave = (T("armor", (2.6, 3.0, -5.8, 4.0, 6.8, 1.2), (6.1, 2.4, -4.2, 1.0, 7.6, 6.2), (2.8, 3.0, 3.8, 3.2, 6.0, 1.0))
              + T("track", (2.8, 4.0, -6.4, 3.6, 1.0, 0.6), (2.8, 5.4, -6.4, 3.6, 1.0, 0.6))
              + T("dark", (2.4, 8.8, -6.2, 4.4, 1.0, 1.6)))
    out = {"armor_head": head, "armor_chest": chest,
           "armor_left_shoulder": pauldron, "armor_right_shoulder": [mx(b) for b in pauldron]}
    out.update(mirror_pair("armor_left_leg", "armor_right_leg", cuisse))
    out.update(mirror_pair("armor_left_shin_sand", "armor_right_shin_sand", greave))
    return out


# ---------------- paint ----------------
PAL = {"main": (196, 168, 118), "dark": (72, 66, 56), "accent": (150, 70, 40), "bag": (132, 124, 82),
       "track": (58, 54, 50), "lens": (90, 220, 255), "lamp": (255, 228, 150), "stencil": (40, 36, 30),
       "metal": (128, 122, 112), "rust": (128, 70, 36), "text": "07"}
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
