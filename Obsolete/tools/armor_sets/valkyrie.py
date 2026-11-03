"""Valkyrie Guard (registry faction "Valkyrie"): elite. Swept everything: a crest-finned tub, V-prow chest with gold
trim, layered swept pauldrons with trailing fins, knee spikes, and a backpack with two big angular wings."""
from ._common import *  # noqa: F401,F403

SET_ID = "valkyrie"
UV_REGION = ("Valkyrie", [(937, 0, 85, 340)])
SCHEME = {"paint": (226, 230, 234), "paint2": (52, 72, 112), "accent": (214, 170, 52), "primer": (150, 154, 160),
          "bare": (120, 122, 126), "stencil": (40, 56, 96), "canvas": (180, 170, 150), "dark": (36, 40, 50),
          "glass": (60, 170, 255), "lamp": (160, 230, 255), "red": (190, 36, 40), "chip": 0.92, "grime": 0.16,
          "mottle": 0.06, "bolt": 0.82}
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


def _kit():
    k = Kit()
    H, C, CN, BP = "armor_head_valkyrie", "armor_chest_valkyrie", "canopy_valkyrie", "backpack_valkyrie"

    # ---- head: omni-eye pod with swept antenna fins ----
    k.add(H, PAINT, (-2.0, 30.8, -4.2, 4.0, 2.8, 2.6))
    k.add(H, PAINT2, rb((-2.2, 33.2, -4.8, 4.4, 0.6, 3.4), (0, 33.4, -1.6), (10, 0, 0)))
    k.add(H, ACCENT, *disc_z(0.0, 32.2, -4.4, 1.25, 0.3))
    k.add(H, GLASS, *disc_z(0.0, 32.2, -4.6, 0.85, 0.3))
    k.add(H, LAMP, (-0.25, 31.95, -4.75, 0.5, 0.5, 0.2))
    k.both(H, PAINT, rb((1.9, 32.6, -3.6, 0.3, 1.0, 3.0), (2.0, 32.6, -3.6), (-35, 0, -20)))   # swept fins
    k.both(H, ACCENT, rb((1.9, 33.6, -3.0, 0.3, 0.3, 2.4), (2.0, 32.6, -3.6), (-35, 0, -20)))

    # ---- chest: V-prow, gold chevron, blue belly ----
    pv = (0.0, 15.4, -6.6)
    k.add(C, (PAINT, "V1", ("north",), False), rb((0.0, 15.4, -6.6, 6.4, 13.2, 1.0), pv, (8, -22, 0)))
    k.add(C, (PAINT, "V1", ("north",), True), rb((-6.4, 15.4, -6.6, 6.4, 13.2, 1.0), pv, (8, 22, 0)))
    k.add(C, ACCENT, rb((0.0, 25.4, -6.8, 6.0, 0.6, 0.4), pv, (8, -22, 0)), rb((-6.0, 25.4, -6.8, 6.0, 0.6, 0.4), pv, (8, 22, 0)))
    k.add(C, ACCENT, rb((0.0, 26.4, -6.8, 5.0, 0.4, 0.4), pv, (8, -22, 0)), rb((-5.0, 26.4, -6.8, 5.0, 0.4, 0.4), pv, (8, 22, 0)))
    k.add(C, PAINT2, rb((-0.3, 15.4, -6.9, 0.6, 13.0, 0.5), pv, (8, 0, 0)))
    k.add(C, PAINT2, rb((-5.6, 14.2, -5.6, 11.2, 2.0, 2.6), (0, 15.2, -4.4), (-18, 0, 0)))
    k.add(C, LAMP, (-1.6, 22.0, -7.25, 3.2, 0.4, 0.3))
    k.add(C, PAINT2, *leg_fairing())

    # ---- canopy: clean tub, blue side flashes, tall swept crest fin, canards ----
    roof = 33.7
    k.add(CN, PAINT, (-5.8, roof, -3.0, 11.6, 1.0, 13.4))
    k.add(CN, PAINT2, (-3.6, roof + 1.0, -1.0, 7.2, 0.4, 9.0))
    k.both(CN, PAINT, (5.6, 18.6, -3.4, 1.1, roof - 18.6, 13.8))
    k.both(CN, PAINT2, rb((6.7, 21.0, 0.0, 0.3, 4.0, 9.0), (6.85, 23.0, 0.0), (-22, 0, 0)))     # side flash
    k.both(CN, ACCENT, rb((6.7, 25.2, 0.6, 0.3, 0.5, 8.4), (6.85, 23.0, 0.0), (-22, 0, 0)))
    k.both(CN, PAINT, rb((2.6, 28.4, -4.0, 3.2, roof - 28.4, 1.0), (4.2, 28.4, -3.5), (0, -14, 0)))
    k.both(CN, GLASS, rb((3.0, 30.4, -4.15, 2.4, 2.0, 0.2), (4.2, 28.4, -3.5), (0, -14, 0)))
    k.add(CN, PAINT, rb((-0.25, roof + 1.0, 0.0, 0.5, 3.4, 8.0), (0, roof + 1.0, 0.0), (-24, 0, 0)))   # crest fin
    k.add(CN, ACCENT, rb((-0.3, roof + 4.0, 0.2, 0.6, 0.4, 7.4), (0, roof + 1.0, 0.0), (-24, 0, 0)))
    k.add(CN, PAINT2, rb((-0.3, roof + 1.0, 4.0, 0.6, 2.2, 4.0), (0, roof + 1.0, 0.0), (-24, 0, 0)))
    k.both(CN, PAINT, rb((5.8, roof - 0.6, -3.0, 3.2, 0.4, 3.6), (5.8, roof - 0.4, -3.0), (0, 30, -12)))  # canards
    k.add(CN, PAINT, (-6.2, 21.6, 9.5, 12.4, roof + 1.0 - 21.6, 1.0))
    k.add(CN, PAINT2, (-4.0, 24.0, 10.5, 8.0, 7.0, 0.4))
    k.add(CN, ACCENT, (-4.4, 31.4, 10.5, 8.8, 0.5, 0.4))
    k.both(CN, LAMP, (4.6, roof + 1.0, -2.6, 1.0, 0.5, 1.2))

    # ---- pauldrons: three layered swept plates with a trailing fin ----
    pd = "shoulder_valkyrie"
    sp = (9.0, 33.6, 0.0)
    k.pair(pd, PAINT, rb((6.6, 33.0, -4.8, 6.6, 1.0, 9.6), sp, (0, 0, -12)))
    k.pair(pd, PAINT2, rb((7.4, 32.0, -4.2, 6.0, 1.0, 9.4), (9.0, 32.5, 0.0), (0, 0, -24)))
    k.pair(pd, (PAINT, "1", ("east", "west"), ("east",)), rb((11.4, 25.8, -4.0, 1.0, 6.6, 8.0), (11.9, 30.0, 0.0), (0, 0, 8)))
    k.pair(pd, ACCENT, rb((6.6, 34.0, -4.8, 6.6, 0.3, 0.6), sp, (0, 0, -12)))
    k.pair(pd, PAINT, rb((9.0, 34.0, 1.0, 0.5, 3.6, 5.6), (9.2, 34.0, 1.0), (-40, 0, -14)))     # trailing fin
    k.pair(pd, PAINT2, rb((9.0, 37.2, 1.4, 0.5, 0.6, 4.6), (9.2, 34.0, 1.0), (-40, 0, -14)))
    k.pair(pd, PAINT, rb((7.0, 25.4, -5.0, 5.0, 6.4, 0.8), (9.5, 31.0, -4.6), (-12, -14, 0)))

    # ---- thighs / shins: swept plates, gold knee spike ----
    lg = "leg_valkyrie"
    k.pair(lg, PAINT, rb((2.6, 10.0, -4.8, 3.9, 7.4, 1.0), (4.5, 13.0, -4.3), (6, -10, 0)))
    k.pair(lg, PAINT2, (6.3, 9.4, -3.4, 1.0, 8.0, 6.0))
    k.pair(lg, PAINT, rb((2.8, 17.0, -4.0, 4.8, 0.8, 6.0), (4.5, 17.4, -1.0), (0, 0, -14)))
    k.pair(lg, ACCENT, rb((6.4, 13.0, -3.6, 1.0, 0.5, 6.4), (6.8, 13.2, 0.0), (-20, 0, 0)))
    k.pair(lg, PAINT, (3.0, 7.4, -6.0, 3.0, 2.8, 1.4))
    sh = "shin_valkyrie"
    k.pair(sh, PAINT, rb((2.6, 2.6, -6.2, 3.9, 7.6, 1.0), (4.5, 6.4, -5.7), (-6, 0, 0)))
    k.pair(sh, PAINT2, (6.1, 2.4, -4.6, 1.0, 7.4, 6.0))
    k.pair(sh, ACCENT, rb((4.1, 9.0, -7.0, 0.8, 0.8, 3.0), (4.5, 9.4, -6.0), (-50, 0, 0)))      # knee spike
    k.pair(sh, PAINT, rb((6.6, 6.0, -2.0, 0.4, 4.0, 4.0), (6.8, 6.0, -2.0), (-30, 0, -10)))     # calf fin
    k.pair(sh, PAINT2, (3.0, 4.0, 3.6, 3.0, 5.6, 0.8))

    # ---- backpack: thruster pod with two big swept wings ----
    k.add(BP, PAINT, (-3.8, 20.4, 9.8, 7.6, 8.4, 3.0))
    k.add(BP, PAINT2, *disc_z(0.0, 24.6, 12.8, 2.2, 1.4))
    k.add(BP, DARK, *disc_z(0.0, 24.6, 14.2, 1.5, 0.6))
    k.add(BP, LAMP, *disc_z(0.0, 24.6, 14.8, 0.8, 0.2))
    wp, wr = (3.6, 27.0, 11.0), (0, -32, 26)
    k.both(BP, PAINT, rb((3.6, 26.4, 10.4, 9.0, 1.0, 2.0), wp, wr))                           # wing spar
    k.both(BP, PAINT2, rb((4.6, 25.2, 10.8, 8.0, 1.2, 1.0), wp, wr))
    k.both(BP, PAINT, rb((6.0, 24.0, 11.0, 5.6, 1.2, 0.6), wp, wr))
    k.both(BP, ACCENT, rb((3.6, 27.4, 10.6, 9.4, 0.4, 1.6), wp, wr))
    k.both(BP, LAMP, rb((12.4, 26.4, 10.6, 0.4, 0.6, 0.6), wp, wr))                          # wingtip light
    k.both(BP, PAINT, rb((3.4, 28.6, 11.0, 0.6, 3.4, 2.4), (3.7, 28.6, 12.0), (-25, 0, -12)))  # tail fins
    return k


def build(a=A):
    return _kit().out()
