"""VOTOMS (registry faction "VOTOMS"): Scopedog-style turret head (domed box, offset 3-lens rotary turret,
whip antenna), blood-red rounded right pauldron with chamfers and bolt ridge, armored 9-tube shoulder pod.
The VOTOMS arms item also shows armor_left_shoulder_usmc (owned by usmc.py)."""
from ._common import *  # noqa: F401,F403


SET_ID = "votoms"
UV_REGION = ("VOTOMS", [(0, 400, 120, 120)])   # free atlas block below the legacy armor area


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
    head = [*T("main", (-2.6, 31.2, -3.2, 5.2, 2.4, 2.4), (-2.2, 33.6, -3.0, 4.4, 0.6, 2.0), (-1.6, 34.2, -2.6, 3.2, 0.4, 1.4)),
            *T("dark", *sym((2.6, 31.4, -3.0, 0.3, 2.0, 2.0))),
            *T("dark", *disc_z(0.6, 32.5, -3.6, 1.5, 0.4)),           # rotary turret plate
            *T("dark", *disc_z(1.0, 33.0, -4.3, 0.65, 0.7)),          # main lens barrel
            *T("lens", *disc_z(-0.2, 32.0, -4.0, 0.45, 0.4), *disc_z(1.3, 31.6, -3.9, 0.35, 0.3)),
            *T("lens", (-2.4, 32.2, -3.5, 1.0, 0.6, 0.3)),           # visor slit
            *T("dark", (-2.2, 34.0, -1.6, 0.3, 5.5, 0.3))]           # whip antenna
    x, y, z = -11.0, 35.8, -1.0
    pod = [*T("stencil", (x - 2.8, y - 2.8, z, 5.6, 5.6, 9.6)), (x - 3.1, y - 3.1, z - 0.6, 6.2, 6.2, 0.6),
           (x - 3.1, y - 3.1, z + 9.6, 6.2, 6.2, 0.6), (x - 3.1, y - 0.3, z + 3.0, 6.2, 0.6, 2.0),
           (x + 2.8, y - 2.0, z + 1.0, 0.4, 4.0, 1.0), (x - 1.0, 29.8, 1.0, 2.0, 3.4, 2.4), (x - 1.6, 29.4, 0.4, 3.2, 0.6, 3.6)]
    for row in (-1.6, 0.0, 1.6):
        for col in (-1.6, 0.0, 1.6):
            pod += [*T("dark", *disc_z(x + col, y + row, z - 0.7, 0.6, 0.2)), *T("rust", (x + col - 0.3, y + row - 0.3, z - 0.75, 0.6, 0.6, 0.15))]
    # blood-red right pauldron (built left, mirrored): rounded cap from stepped slabs, chamfered edges
    red = [(6.8, 33.4, -4.0, 5.8, 1.4, 7.6), (7.4, 34.8, -3.4, 4.6, 0.6, 6.4), (8.2, 35.4, -2.6, 3.0, 0.3, 4.8),
           (12.6, 26.0, -4.0, 1.2, 7.4, 7.6), (13.8, 27.0, -3.2, 0.4, 5.6, 6.0),
           rot_box(12.1, 33.0, -4.0, 1.2, 1.2, 7.6, 12.7, 33.6, 0, 0, 0, 45),
           (7.2, 27.4, -4.8, 5.4, 6.0, 0.8), (7.2, 27.4, 2.6, 5.4, 6.0, 0.8),
           *[(14.2, 28.0 + i * 1.6, -2.0, 0.3, 0.5, 0.5) for i in range(3)]]
    red = T("red", *red)
    return {"armor_head_votoms": head, "backpack_missile_pod": pod,
            "armor_right_shoulder_red": [mx(b) for b in red]}


# ---------------- paint ----------------
PAL = {"main": (92, 104, 66), "dark": (44, 46, 42), "accent": (74, 82, 54), "red": (150, 30, 26), "bag": (120, 112, 80),
       "track": (54, 54, 52), "lens": (230, 70, 60), "lamp": (255, 236, 170), "stencil": (225, 205, 120),
       "metal": (120, 118, 110), "rust": (118, 70, 38), "text": "13"}
# ==== painter (copied from usmc.py; modules may only import from _common) ====
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
    elif role == "red":
        base = P["red"]
    elif role == "rust":
        return _out(_mul(P["red"], 0.8 + 0.3 * nf))      # missile nose caps
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
