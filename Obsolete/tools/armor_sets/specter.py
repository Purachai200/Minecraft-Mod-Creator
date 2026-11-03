"""Specter PMC (registry faction "Specter"): stealth. Faceted low-observable tub with inward-raked chines, a slit
wedge visor, serrated RAM edging, swept faceted pauldrons and a flat shielded ECM pack. Matte charcoal."""
from ._common import *  # noqa: F401,F403

SET_ID = "specter"
UV_REGION = ("Specter", [(852, 0, 85, 340)])
SCHEME = {"paint": (40, 42, 47), "paint2": (28, 29, 33), "accent": (92, 70, 118), "primer": (70, 70, 74),
          "bare": (96, 98, 104), "stencil": (78, 80, 88), "canvas": (52, 50, 46), "dark": (18, 18, 21),
          "glass": (190, 60, 230), "lamp": (210, 120, 255), "red": (120, 30, 40), "chip": 0.93, "grime": 0.12,
          "mottle": 0.1}
# ---------------- set-local kit (copied per set module: modules may only import from _common) ----------------
import json as _json
import os as _os
import sys as _sys

PAINT, PAINT2, DARK, METAL, GLASS, LAMP, RED, CANVAS, ACCENT = range(9)


def rb(b, pivot, rot):
    """Axis box -> rotated box about pivot (degrees)."""
    return (*b[:6], *pivot, *rot)


def rgroup(boxes, pivot, rot):
    return [rb(b, pivot, rot) for b in boxes]


def bolts(p0, p1, n, s=0.4, depth=0.3, axis=2):
    """n bolt heads with centres from p0 to p1; `axis` is the face normal axis (0 x, 1 y, 2 z), negative side out."""
    out = []
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0.5
        c = [p0[k] + (p1[k] - p0[k]) * t for k in range(3)]
        sz = [s, s, s]
        sz[axis] = depth
        out.append((c[0] - sz[0] / 2, c[1] - sz[1] / 2, c[2] - sz[2] / 2, *sz))
    return out


class Kit:
    """Collects (box, material) per bone so paint() knows what each packed cube is."""
    def __init__(self):
        self.bones = {}

    def add(self, bone, mat, *boxes):
        self.bones.setdefault(bone, []).extend((tuple(b), mat) for b in boxes)

    def pair(self, stem, mat, *boxes):
        """Left bone gets boxes, right bone the mirror, index for index."""
        self.add(f"armor_left_{stem}", mat, *boxes)
        self.add(f"armor_right_{stem}", mat, *(mx(b) for b in boxes))

    def both(self, bone, mat, *boxes):
        self.add(bone, mat, *sym(*boxes))

    def out(self):
        return {n: [b for b, _ in v] for n, v in self.bones.items()}


FONT = {"0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001011001111",
        "4": "101101111001001", "5": "111100111001111", "6": "111100111101111", "7": "111001010010010",
        "8": "111101111101111", "9": "111101111001111", "K": "101110100110101", "R": "110101110101101",
        "S": "111100111001111", "V": "101101101101010", "A": "010101111101101", "-": "000000111000000",
        "N": "101111111111101", "X": "101101010101101"}

_TEX = None


def _texmap():
    """texel -> (material, face, fx, fy, fw, fh) from the generator's packed manifest."""
    global _TEX
    if _TEX is None:
        _TEX = {}
        mats = {n: [m for _, m in v] for n, v in _kit().bones.items()}
        path = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "packed_armor_uvs.json")
        try:
            manifest = _json.load(open(path))
        except (OSError, ValueError):
            manifest = []
        for e in manifest:
            if e["faction"] != UV_REGION[0]:
                continue
            ml = mats.get(e["bone"], [])
            mat = ml[e["cube_index"]] if e["cube_index"] < len(ml) else PAINT
            for face, (u0, v0, u1, v1) in e["faces"].items():
                for yy in range(v0, v1):
                    for xx in range(u0, u1):
                        _TEX[(xx, yy)] = (mat, face, xx - u0, yy - v0, u1 - u0, v1 - v0)
    return _TEX


def _mul(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _camo(camo_id, x, y, n_med, n_coarse, fallback):
    """camos 1..6 use the shared scheme of the running texture generator; camo 0 is this faction's own."""
    main = _sys.modules.get("__main__")
    if camo_id and hasattr(main, "camo_base"):
        return tuple(main.camo_base(camo_id, x, y, n_med, n_coarse)[:3])
    return fallback


def _glyph(text, fx, fy, fw, fh, flip):
    """True where the stencil text covers texel (fx, fy); text centred on the face."""
    tw = len(text) * 4 - 1
    if tw > fw - 2 or fh < 7:
        return False
    if flip:
        fx = fw - 1 - fx
    ox, oy = (fw - tw) // 2, (fh - 5) // 2
    gx, gy = fx - ox, fy - oy
    if not (0 <= gx < tw and 0 <= gy < 5) or gx % 4 == 3:
        return False
    g = FONT.get(text[gx // 4], "0" * 15)
    return g[gy * 3 + gx % 4] == "1"


def paint(x, y, camo_id, n_fine, n_med, n_coarse):
    info = _texmap().get((x, y))
    if info is None:
        return None
    mat, face, fx, fy, fw, fh = info
    text = None
    if isinstance(mat, tuple):
        mat, text, faces, flip = mat
        if face not in faces:
            text = None
        if isinstance(flip, tuple):
            flip = face in flip
    P = SCHEME
    edge = fx == 0 or fy == 0 or fx == fw - 1 or fy == fh - 1
    if mat in (PAINT, PAINT2, ACCENT):
        base = P["paint"] if mat == PAINT else P["paint2"] if mat == PAINT2 else P["accent"]
        if mat != ACCENT or camo_id:
            base = _camo(camo_id, x, y, n_med, n_coarse, base)
            if mat == PAINT2 and camo_id:
                base = _mul(base, 0.82)
        c = _mul(base, 0.9 + 0.18 * n_med + P.get("mottle", 0.0) * (n_coarse - 0.5))
        side = face in ("north", "south", "east", "west")
        if side and fh > 2:
            c = _mul(c, 1.0 - P.get("grime", 0.22) * (fy / fh) ** 2)          # dirt settles low
            if (x * 7 + 3) % 13 == 0 and n_med > 0.45:
                c = _mul(c, 0.86)                                            # rain / dust streaks
        if face == "up":
            c = _mul(c, 1.06)
        if fw >= 3 and fh >= 3 and edge:
            c = _mul(c, 1.16 if (fy == 0 or fx == 0) else 0.7)               # worn top edge, shadowed lower edge
        if fw >= 7 and fh >= 6 and side and fx in (1, fw - 2) and fy % 3 == 1:
            c = _mul(c, P.get("bolt", 0.55))                                              # bolt-row shadows along the seams
        if fw >= 10 and side and fx == fw // 2 and not edge:
            c = _mul(c, 0.72)                                                # weld seam between applique halves
        chip_t = P.get("chip", 0.86) - (0.08 if edge else 0.0)
        if n_fine > chip_t and n_coarse > 0.55:
            c = P["primer"] if n_fine < chip_t + 0.06 else P["bare"]         # chipped paint: primer ring, bare steel core
        if text and _glyph(text, fx, fy, fw, fh, flip):
            c = _mul(P["stencil"], 0.9 + 0.2 * n_fine)
        return (*c, 255)
    if mat == CANVAS:
        c = P["canvas"]
        c = _mul(c, 0.86 + 0.1 * ((fx + fy) % 2) + 0.12 * n_med)
        if edge or (fh >= 4 and fy == fh // 2):
            c = _mul(c, 0.72)
        return (*c, 255)
    if mat == GLASS:
        g = P["glass"]
        return (*(_mix(g, (235, 245, 255), 0.55) if fx + fy < 2 else _mul(g, 0.8 + 0.3 * (1 - fy / max(fh, 1)))), 255)
    if mat == LAMP:
        return (*(_mix(P["lamp"], (255, 255, 240), 0.5) if not edge else P["lamp"]), 255)
    if mat == RED:
        return (*_mul(P["red"], 0.85 + 0.25 * n_med), 255)
    if mat == METAL:
        return (*_mul((128, 124, 116), 0.8 + 0.35 * n_fine + (0.15 if fy == 0 else 0.0)), 255)
    return (*_mul(P["dark"], 0.85 + 0.3 * n_fine - (0.15 if edge else 0.0)), 255)   # DARK


def _saw(x0, x1, y, z, n, s=0.6):
    """Serrated RAM edge: a row of 45-degree diamonds along x."""
    return [rb((x0 + (x1 - x0) * (i + 0.5) / n - s / 2, y - s / 2, z, s, s, 0.3),
               (x0 + (x1 - x0) * (i + 0.5) / n, y, z), (0, 0, 45)) for i in range(n)]


def _kit():
    k = Kit()
    H, C, CN, BP = "armor_head_specter", "armor_chest_specter", "canopy_specter", "backpack_specter"

    # ---- head: low wedge with a single glowing slit and raked chines ----
    k.add(H, PAINT, (-2.2, 30.8, -4.2, 4.4, 2.4, 2.6))
    k.add(H, PAINT2, rb((-2.4, 33.0, -4.9, 4.8, 0.6, 3.6), (0, 33.0, -1.4), (14, 0, 0)))       # raked top facet
    k.add(H, PAINT, rb((-2.0, 30.0, -5.0, 4.0, 1.2, 0.8), (0, 30.6, -4.4), (-30, 0, 0)))       # chin facet
    k.add(H, DARK, (-1.9, 32.0, -4.45, 3.8, 0.7, 0.3))
    k.add(H, GLASS, (-1.6, 32.15, -4.6, 3.2, 0.4, 0.2))
    k.both(H, PAINT2, rb((2.0, 30.8, -4.4, 0.6, 2.6, 2.8), (2.2, 32.0, -3.0), (0, -18, -10)))  # side chines
    k.add(H, ACCENT, (-0.15, 33.4, -3.4, 0.3, 0.3, 2.0))

    # ---- chest: two big angled facets meeting in a chine, serrated lower edge ----
    pv = (0.0, 15.2, -5.6)
    k.add(C, (PAINT, "S9", ("north",), False), rb((0.0, 15.2, -5.6, 6.4, 13.4, 1.0), pv, (10, -18, 0)))
    k.add(C, (PAINT, "S9", ("north",), True), rb((-6.4, 15.2, -5.6, 6.4, 13.4, 1.0), pv, (10, 18, 0)))
    k.add(C, PAINT2, rb((-0.25, 15.2, -5.9, 0.5, 13.0, 0.5), pv, (10, 0, 0)))                    # centre chine
    k.add(C, PAINT2, rb((-6.0, 14.0, -5.4, 12.0, 1.4, 2.4), (0, 14.7, -4.2), (-20, 0, 0)))
    k.add(C, DARK, *_saw(-5.8, 5.8, 14.2, -5.7, 9))
    k.add(C, ACCENT, rb((3.6, 24.0, -6.0, 2.2, 0.3, 0.3), pv, (10, -18, 0)), rb((-5.8, 24.0, -6.0, 2.2, 0.3, 0.3), pv, (10, 18, 0)))
    k.add(C, PAINT2, *leg_fairing())

    # ---- canopy: vertical lower walls, inward-raked upper chines, sloped brow, narrow roof ----
    roof = 33.7
    k.add(CN, PAINT, (-4.5, roof, -2.6, 9.0, 0.8, 12.8))
    k.add(CN, PAINT2, (-3.2, roof + 0.8, 0.0, 6.4, 0.4, 7.0))
    k.both(CN, PAINT, (5.6, 18.6, -3.4, 1.0, 10.2, 13.6))                                       # lower walls
    k.both(CN, PAINT, rb((5.4, 28.4, -3.4, 1.0, 5.2, 13.6), (5.9, 28.4, 3.4), (0, 0, 18)))      # raked chines
    k.both(CN, DARK, rb((6.5, 28.3, -3.4, 0.4, 0.4, 13.6), (6.7, 28.5, 3.4), (45, 0, 0)))       # chine seam
    k.both(CN, PAINT2, rb((2.6, 28.4, -4.4, 3.4, 5.6, 0.8), (4.3, 28.4, -4.0), (16, -12, 0)))   # sloped brow
    k.both(CN, GLASS, rb((3.0, 31.2, -4.55, 2.6, 0.35, 0.2), (4.3, 28.4, -4.0), (16, -12, 0)))
    k.both(CN, DARK, *_saw(5.6, 6.6, 18.4, -3.6, 1))
    k.add(CN, DARK, *_saw(-6.0, 6.0, 18.4, -3.65, 8))
    k.add(CN, PAINT, (-6.2, 21.6, 9.5, 12.4, roof + 0.8 - 21.6, 1.0))
    k.add(CN, PAINT2, rb((-5.0, 26.0, 10.5, 10.0, 6.0, 0.5), (0, 26.0, 10.5), (-8, 0, 0)))
    k.both(CN, PAINT2, rb((6.6, 19.4, 0.0, 0.5, 8.0, 8.0), (6.6, 23.4, 4.0), (0, 14, 0)))       # flank RAM tiles
    k.add(CN, DARK, rb((3.2, roof + 0.6, 6.0, 0.25, 0.6, 3.6), (3.3, roof + 0.6, 6.0), (0, 0, 0)),
          rb((3.2, roof + 1.1, 7.0, 0.25, 0.3, 4.0), (3.3, roof + 1.1, 7.0), (-22, 0, 0)))       # low blade antenna
    k.add(CN, ACCENT, (-6.25, 26.0, -3.45, 0.3, 0.3, 13.0), (5.95, 26.0, -3.45, 0.3, 0.3, 13.0))

    # ---- pauldrons: swept faceted wedges with a raked trailing fin ----
    pd = "shoulder_specter"
    sp = (9.0, 33.6, 0.0)
    k.pair(pd, PAINT, rb((6.6, 33.0, -4.6, 6.4, 1.0, 9.0), sp, (0, 0, -16)))
    k.pair(pd, PAINT2, rb((6.8, 33.6, -5.2, 5.2, 0.6, 3.0), (9.0, 33.6, -3.8), (-20, 0, -16)))
    k.pair(pd, (PAINT, "9", ("east", "west"), ("east",)), rb((11.4, 25.8, -3.6, 1.0, 7.0, 7.6), (11.9, 30, 0), (0, 10, 6)))
    k.pair(pd, PAINT2, rb((7.0, 25.6, -4.8, 4.8, 6.4, 0.7), (9.4, 31.0, -4.4), (-14, -16, 0)))
    k.pair(pd, PAINT, rb((10.0, 33.0, 3.0, 0.5, 2.6, 4.0), (10.2, 33.0, 3.0), (-35, 0, -10)))   # trailing fin
    k.pair(pd, DARK, rb((12.0, 25.6, -3.8, 0.4, 0.4, 7.6), (12.2, 25.8, 0), (45, 0, 0)))

    # ---- thighs / shins: angled facets ----
    lg = "leg_specter"
    k.pair(lg, PAINT, rb((2.6, 10.0, -4.8, 3.9, 7.4, 1.0), (4.5, 13.0, -4.3), (0, -16, 0)))
    k.pair(lg, PAINT2, rb((6.3, 9.4, -3.6, 1.0, 8.2, 6.4), (6.8, 13.0, -0.4), (0, 12, 8)))
    k.pair(lg, PAINT2, rb((2.8, 16.8, -4.0, 4.8, 0.8, 6.0), (4.5, 17.2, -1.0), (8, 0, -14)))
    k.pair(lg, PAINT, rb((3.0, 7.4, -6.0, 3.0, 2.6, 1.2), (4.5, 8.7, -5.4), (-20, 0, 0)))
    k.pair(lg, ACCENT, rb((3.4, 15.4, -4.95, 2.6, 0.3, 0.3), (4.5, 13.0, -4.3), (0, -16, 0)))
    sh = "shin_specter"
    k.pair(sh, PAINT, rb((2.6, 2.6, -6.2, 3.9, 7.8, 1.0), (4.5, 6.5, -5.7), (-6, -14, 0)))
    k.pair(sh, PAINT2, rb((6.1, 2.4, -4.8, 1.0, 7.4, 6.4), (6.6, 6.0, -1.6), (0, 10, -6)))
    k.pair(sh, DARK, *_saw(2.8, 6.3, 2.4, -6.3, 4))
    k.pair(sh, PAINT2, rb((3.0, 4.0, 3.6, 3.0, 5.6, 0.8), (4.5, 6.8, 4.0), (10, 0, 0)))

    # ---- backpack: flat angled ECM slab, blade emitters, shielded exhaust louvres ----
    k.add(BP, PAINT, (-4.6, 20.0, 9.8, 9.2, 9.6, 2.2))
    k.add(BP, PAINT2, rb((-4.2, 20.6, 12.0, 8.4, 8.4, 0.8), (0, 20.6, 12.0), (-10, 0, 0)))
    k.add(BP, (PAINT2, "X", ("south",), False), rb((-2.6, 22.0, 12.8, 5.2, 7.0, 0.3), (0, 20.6, 12.0), (-10, 0, 0)))
    k.both(BP, PAINT, rb((4.6, 20.4, 10.0, 0.5, 9.6, 3.2), (4.6, 25.0, 10.0), (0, -25, 0)))     # side fairings
    k.both(BP, DARK, *[(1.0, 20.2 + 0.0, 10.6 + 0.8 * i, 3.0, 0.3, 0.4) for i in range(3)])     # downward louvres
    k.both(BP, PAINT2, rb((3.0, 29.4, 10.4, 0.4, 3.6, 2.0), (3.2, 29.4, 11.4), (-30, 0, -12)))  # ECM blades
    k.both(BP, LAMP, rb((3.0, 32.6, 11.0, 0.45, 0.3, 0.6), (3.2, 29.4, 11.4), (-30, 0, -12)))
    return k


def build(a=A):
    return _kit().out()
