"""Cerberus / Pegaso Black (registry faction "Cerberus"): charcoal PMC wedge. Mono-eye dome in an armored
collar, raked wedge capsule with crimson eye-slit band and triple whip antennas, tall finned pauldrons with
red flashes, armored skirts, twin cylindrical fuel packs."""
from ._common import *  # noqa: F401,F403

SET_ID = "cerberus"
UV_REGION = ("Cerberus", [(330, 0, 70, 315)])

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
    head = (T("armor", (-2.6, 31.2, -3.2, 5.2, 2.6, 2.2), *disc_y(0, 33.8, -2.2, 1.9, 0.8), *disc_y(0, 34.6, -2.2, 1.3, 0.5))
            + T("dark", *disc_z(0, 32.5, -3.6, 1.0, 0.4))
            + T("lens", *disc_z(0, 32.5, -3.9, 0.55, 0.3))
            + T("accent", (-2.7, 31.0, -3.4, 5.4, 0.4, 0.4)))
    glacis = rot_box(-5.0, 21.6, -5.6, 10.0, 7.4, 1.2, 0, 21.6, -4.6, 18, 0, 0)
    chest = (T("armor", glacis, (-5.4, 14.6, -5.6, 10.8, 7.2, 1.3),
               *sym(rot_box(3.6, 14.6, -6.0, 2.4, 7.0, 1.0, 4.8, 18.0, -5.5, 0, 22, 0),        # angled cheek wedges
                    (5.9, 14.2, -4.6, 0.9, 9.0, 8.6)))                                      # armored skirts
             + T("accent", rot_box(-0.6, 21.8, -5.9, 1.2, 7.0, 0.3, 0, 21.6, -4.6, 18, 0, 0))
             + T("stencil", (-2.4, 16.0, -5.9, 4.8, 3.0, 0.3))
             + T("dark", (-4.0, 13.2, -4.8, 8.0, 1.6, 7.0), *sym((5.0, 15.0, -6.2, 0.6, 0.6, 0.6), (5.0, 20.6, -6.2, 0.6, 0.6, 0.6))))
    chest += T("armor", *leg_fairing())
    canopy = (T("armor", *build_box_canopy())
              + T("armor", *sym(rot_box(6.7, 22.0, -3.0, 1.0, 11.0, 8.0, 7.2, 22.0, 2.0, 0, 0, 6)))   # raked wedge flanks
              + T("dark", (-4.0, 31.0, -3.9, 8.0, 1.2, 0.3)) + T("accent", (-3.6, 31.3, -4.1, 7.2, 0.5, 0.25))
              + T("lens", (-0.8, 31.25, -4.2, 1.6, 0.6, 0.2))
              + T("dark", *[(x, 34.8, 8.6, 0.3, h, 0.3) for x, h in ((3.6, 8.0), (-0.15, 11.0), (-3.9, 8.0))])
              + T("dark", *sym((3.4, 34.6, 8.4, 0.8, 0.5, 0.8))))
    pauldron = (T("armor", rot_box(6.4, 33.4, -4.4, 6.8, 1.2, 7.8, 9.5, 33.4, 0.0, 0, 0, -14), (12.4, 25.0, -4.0, 1.2, 8.6, 7.4),
                  (7.2, 27.0, -5.0, 5.2, 6.4, 1.0), (7.2, 27.0, 2.6, 5.2, 6.4, 1.0))
                + T("accent", rot_box(6.6, 34.6, -2.0, 6.0, 0.3, 3.8, 9.5, 33.4, 0.0, 0, 0, -14), (13.6, 26.0, -1.0, 0.3, 6.0, 1.6))
                + T("dark", (8.4, 34.2, -0.4, 0.6, 3.6, 3.2), (13.6, 32.6, -3.6, 0.6, 0.6, 7.0)))         # dorsal fin, rail
    cuisse = (T("armor", (2.6, 16.0, -2.4, 3.8, 1.2, 4.6), rot_box(6.0, 9.4, -3.4, 1.2, 7.4, 6.0, 6.6, 17.0, 0, 0, 0, 6),
                  (2.6, 10.4, -4.6, 3.8, 6.0, 1.2))
              + T("accent", (2.9, 15.0, -4.9, 3.2, 0.5, 0.3))
              + T("dark", (2.8, 8.0, -5.6, 3.4, 2.6, 2.2)))
    greave = (T("armor", rot_box(2.6, 3.0, -6.0, 4.0, 7.0, 1.4, 4.5, 3.0, -5.3, 8, 0, 0), (6.1, 2.2, -4.0, 1.2, 7.8, 6.4),
                  (3.0, 3.0, 3.8, 3.0, 6.0, 1.2))
              + T("accent", (7.3, 6.0, -3.0, 0.3, 0.6, 4.4))
              + T("dark", (2.4, 8.8, -6.4, 4.4, 1.2, 1.8)))
    backpack = (T("dark", (-3.8, 21.6, 10.4, 7.6, 8.4, 0.6))
                + T("armor", *sym(*disc_y(2.6, 21.0, 12.6, 1.9, 9.6)))
                + T("accent", *sym((0.5, 27.2, 10.6, 4.2, 0.5, 4.0)))
                + T("dark", *sym((2.0, 30.6, 12.0, 1.2, 1.2, 1.2), (2.0, 19.6, 12.0, 1.2, 1.4, 1.2))))
    out = {"armor_head_dome": head, "armor_chest_cerberus": chest, "canopy_cerberus": canopy, "backpack_cerberus": backpack,
           "armor_left_shoulder_cerberus": pauldron, "armor_right_shoulder_cerberus": [mx(b) for b in pauldron]}
    out.update(mirror_pair("armor_left_leg_cerberus", "armor_right_leg_cerberus", cuisse))
    out.update(mirror_pair("armor_left_shin_cerberus", "armor_right_shin_cerberus", greave))
    return out


# ---------------- paint ----------------
PAL = {"main": (44, 46, 50), "dark": (24, 25, 28), "accent": (176, 30, 32), "bag": (60, 62, 56),
       "track": (40, 40, 42), "lens": (255, 40, 48), "lamp": (255, 80, 70), "stencil": (190, 40, 40),
       "metal": (84, 86, 92), "rust": (90, 56, 40), "text": "03"}
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
