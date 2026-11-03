"""Khamsin Guard (registry faction "Khamsin"): desert heavy. A slab-armoured tub with a sun-shade brim, sandbags
on the belly, spare track links on the flanks, smoke dischargers and twin dust-filter canisters on the back."""
from ._common import *  # noqa: F401,F403

SET_ID = "khamsin"
UV_REGION = ("Khamsin", [(682, 0, 85, 340)])
SCHEME = {"paint": (184, 152, 104), "paint2": (150, 122, 84), "accent": (128, 62, 40), "primer": (112, 72, 52),
          "bare": (104, 100, 94), "stencil": (40, 34, 28), "canvas": (170, 150, 108), "dark": (48, 44, 40),
          "glass": (190, 120, 40), "lamp": (255, 214, 140), "red": (150, 46, 30), "chip": 0.9, "grime": 0.28,
          "mottle": 0.12}
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
    H, C, CN, BP = "armor_head_khamsin", "armor_chest_khamsin", "canopy_khamsin", "backpack_khamsin"

    # ---- head: squat dust-filter optic block in the canopy notch, hooded against the sun ----
    k.add(H, PAINT, (-2.3, 30.8, -4.5, 4.6, 3.3, 2.9))
    k.add(H, PAINT2, rb((-2.7, 34.0, -5.6, 5.4, 0.6, 3.8), (0, 34.3, -2.0), (-8, 0, 0)))    # sun hood
    k.add(H, DARK, (-1.8, 31.4, -4.75, 3.6, 1.8, 0.4))                                         # optic recess
    k.add(H, GLASS, (-1.4, 31.8, -4.9, 1.1, 1.1, 0.2), (0.3, 31.8, -4.9, 1.1, 1.1, 0.2))
    k.add(H, DARK, *[(-2.0, 33.25 + 0.0, -4.65, 4.0, 0.3, 0.3)])                              # hood drip rail
    k.add(H, METAL, *bolts((-1.9, 30.95, -4.6), (1.9, 30.95, -4.6), 5, 0.3, 0.2))
    k.add(H, DARK, *disc_x(2.3, 32.2, -3.2, 0.8, 0.9), *disc_x(-3.2, 32.2, -3.2, 0.8, 0.9))    # filter cans
    k.add(H, METAL, (2.9, 31.0, -3.5, 0.3, 2.4, 0.6), (-3.2, 31.0, -3.5, 0.3, 2.4, 0.6))

    # ---- chest: stepped belly slabs with sandbags, bolted glacis, weld beads ----
    gl_p, gl_r = (0, 22.4, -3.7), (12, 0, 0)
    k.add(C, (PAINT, "K07", ("north",), True), rb((-6.2, 22.4, -4.4, 12.4, 6.0, 1.4), gl_p, gl_r))   # upper glacis
    k.add(C, PAINT2, *rgroup([(-5.2, 23.4, -4.9, 4.2, 4.2, 0.5), (1.0, 23.4, -4.9, 4.2, 4.2, 0.5)], gl_p, gl_r))  # appliques
    k.add(C, METAL, *rgroup(bolts((-5.7, 28.0, -4.55), (5.7, 28.0, -4.55), 9, 0.4, 0.3)
                            + bolts((-5.7, 22.8, -4.55), (5.7, 22.8, -4.55), 9, 0.4, 0.3), gl_p, gl_r))
    k.add(C, PAINT, (-5.8, 15.4, -5.0, 11.6, 7.0, 1.6))                                          # belly slab
    k.add(C, METAL, (-6.0, 22.15, -5.1, 12.0, 0.35, 0.4))                                        # weld bead
    k.add(C, PAINT2, (-6.4, 14.6, -5.4, 12.8, 1.0, 2.4))                                         # bottom lip
    for i, x in enumerate((-5.9, -1.95, 2.0)):
        k.add(C, CANVAS, (x, 15.7, -7.0, 3.9, 1.7, 2.0))                                         # sandbag row 1
    for x in (-3.9, 0.05):
        k.add(C, CANVAS, (x, 17.3, -6.8, 3.85, 1.6, 1.8))                                        # sandbag row 2
    k.add(C, CANVAS, (-1.9, 18.8, -6.5, 3.8, 1.4, 1.6))
    k.add(C, DARK, (-6.1, 16.4, -7.15, 12.2, 0.25, 0.2), (-4.2, 17.9, -6.95, 8.4, 0.25, 0.2))    # tie-down straps
    k.add(C, DARK, *sym((5.4, 15.2, -5.3, 0.6, 7.4, 0.4)))                                       # strap anchors
    k.add(C, PAINT2, *[rb((x, 19.0, -4.8, 2.2, 3.2, 1.0), (x + 1.1, 19.0, -4.3), (0, 0, 0))
                       for x in (-6.6, 4.4)])                                                    # cheek blocks
    k.add(C, PAINT2, *leg_fairing())

    # ---- canopy: armoured tub, split brow with vision slits, sun brim, track links, lamps, antenna ----
    roof = 33.7
    k.add(CN, PAINT, (-6.4, roof, -3.6, 6.4, 1.4, 14.2), (0.0, roof, -3.6, 6.4, 1.4, 14.2))
    k.add(CN, PAINT2, (-5.4, roof + 1.4, -2.6, 4.6, 0.6, 5.6), (0.8, roof + 1.4, -2.6, 4.6, 0.6, 5.6),
          (-4.6, roof + 1.4, 4.0, 9.2, 0.8, 5.0))                                                # roof appliques + hatch
    k.add(CN, METAL, (-2.6, roof + 2.2, 5.2, 5.2, 0.3, 0.4), (-0.4, roof + 2.2, 7.6, 0.8, 0.5, 0.8))
    k.add(CN, PAINT2, rb((-6.8, roof + 0.2, -6.4, 13.6, 0.8, 3.2), (0, roof + 0.6, -3.4), (-10, 0, 0)))   # sun brim
    k.both(CN, PAINT, (5.6, 18.6, -3.6, 1.3, roof - 18.6, 6.6), (5.6, 18.6, 3.0, 1.3, roof - 18.6, 7.6))  # side walls
    k.both(CN, METAL, (6.75, 18.8, 2.85, 0.3, roof - 19.0, 0.3))                                 # side weld seam
    k.both(CN, PAINT, (2.6, 28.4, -4.0, 3.4, roof - 28.4, 1.2))                                  # brow cheeks
    k.both(CN, PAINT2, (2.4, 28.0, -4.4, 4.2, 1.6, 0.8))
    k.both(CN, GLASS, (3.0, 31.2, -4.15, 2.4, 0.7, 0.2))                                         # vision slits
    k.both(CN, DARK, *[(6.9, 21.0 + 1.6 * i, 3.4, 0.7, 1.2, 5.6) for i in range(6)])             # spare track links
    k.both(CN, METAL, (7.0, 20.8, 3.1, 0.5, 9.8, 0.4), (7.0, 20.8, 9.0, 0.5, 9.8, 0.4))           # link retaining bars
    k.add(CN, PAINT, (-6.4, 21.6, 9.5, 6.4, roof + 1.4 - 21.6, 1.0), (0.0, 21.6, 9.5, 6.4, roof + 1.4 - 21.6, 1.0))
    k.add(CN, PAINT2, (-4.6, 23.0, 10.5, 9.2, 5.2, 0.5))                                         # rear applique
    k.add(CN, METAL, *bolts((-4.2, 28.6, 11.05), (4.2, 28.6, 11.05), 7, 0.4, 0.3))
    k.both(CN, DARK, (4.3, roof + 1.4, -3.4, 1.8, 1.4, 1.6))                                     # work lamp housings
    k.both(CN, LAMP, (4.55, roof + 1.65, -3.6, 1.3, 0.9, 0.2))
    for i in range(3):                                                                           # smoke dischargers
        k.both(CN, DARK, rb((4.0 + i * 0.9, roof + 1.4, -1.6, 0.8, 0.8, 1.9), (4.4 + i * 0.9, roof + 1.8, -0.6), (-40, 0, 0)))
        k.both(CN, RED, rb((4.1 + i * 0.9, roof + 1.5, -1.75, 0.6, 0.6, 0.2), (4.4 + i * 0.9, roof + 1.8, -0.6), (-40, 0, 0)))
    k.add(CN, DARK, (4.6, roof + 1.4, 8.0, 1.0, 0.8, 1.0), (4.95, roof + 2.2, 8.35, 0.3, 9.0, 0.3))   # whip antenna

    # ---- pauldrons: heavy boxes with sun-shade lip, bolted applique and a sandbag on top ----
    sp, sr = (8.0, 34.4, 0.0), (0, 0, -9)
    pd = "shoulder_khamsin"
    k.pair(pd, PAINT, rb((6.6, 33.4, -4.2, 6.2, 1.6, 8.4), sp, sr))
    k.pair(pd, (PAINT, "07", ("east", "west"), ("east",)), (11.4, 25.4, -4.0, 1.5, 7.6, 8.0))
    k.pair(pd, PAINT2, (6.8, 31.0, -4.9, 6.0, 2.4, 0.9), (6.8, 31.0, 4.0, 6.0, 2.4, 0.9))
    k.pair(pd, ACCENT, (12.9, 30.0, -3.0, 0.5, 1.0, 6.0))                                        # unit band
    k.pair(pd, PAINT2, (12.9, 25.8, -2.8, 0.5, 3.8, 5.6))
    k.pair(pd, METAL, *bolts((13.4, 29.2, -2.4), (13.4, 29.2, 2.4), 3, 0.4, 0.25, 0),
           *bolts((13.4, 26.2, -2.4), (13.4, 26.2, 2.4), 3, 0.4, 0.25, 0))
    k.pair(pd, CANVAS, rb((7.4, 35.0, -2.2, 4.4, 1.5, 3.8), sp, sr))
    k.pair(pd, DARK, rb((9.3, 34.9, -2.4, 0.4, 1.8, 4.2), sp, sr))

    # ---- thighs ----
    lg = "leg_khamsin"
    k.pair(lg, PAINT, (2.6, 9.8, -4.8, 3.9, 7.6, 1.3), (6.3, 9.0, -3.8, 1.3, 8.8, 6.6))
    k.pair(lg, PAINT2, rb((2.6, 17.3, -4.2, 5.0, 1.0, 6.4), (4.5, 17.6, 0), (0, 0, -12)))
    k.pair(lg, PAINT2, (3.0, 11.6, -5.3, 3.1, 4.4, 0.5), (7.6, 10.6, -2.4, 0.4, 5.4, 3.8))
    k.pair(lg, METAL, *bolts((3.3, 15.6, -5.45), (5.8, 15.6, -5.45), 3, 0.35, 0.2),
           *bolts((3.3, 12.0, -5.45), (5.8, 12.0, -5.45), 3, 0.35, 0.2))
    k.pair(lg, PAINT, (3.0, 7.4, -6.0, 3.2, 3.0, 1.6))                                          # knee cop
    k.pair(lg, DARK, (3.4, 8.0, -6.2, 2.4, 0.4, 0.3))

    # ---- shins: thick greave with a vertical rib, track-link skirt at the ankle ----
    sh = "shin_khamsin"
    k.pair(sh, PAINT, (2.6, 3.0, -6.3, 3.9, 7.4, 1.4), (6.2, 2.6, -4.9, 1.3, 7.6, 6.4))
    k.pair(sh, PAINT2, (4.1, 3.6, -6.7, 0.8, 6.6, 0.45), (3.0, 4.0, 3.8, 3.1, 5.6, 1.0))
    k.pair(sh, DARK, *[(2.8 + 1.0 * i, 2.0, -6.6, 0.85, 1.1, 0.8) for i in range(4)])
    k.pair(sh, METAL, *bolts((2.95, 9.6, -6.35), (6.1, 9.6, -6.35), 4, 0.35, 0.2))
    k.pair(sh, ACCENT, (7.5, 7.0, -4.0, 0.3, 1.0, 4.6))

    # ---- backpack: armoured box, twin vertical dust filters, jerrycans ----
    k.add(BP, PAINT, (-4.4, 20.0, 9.8, 8.8, 9.2, 3.6))
    k.add(BP, PAINT2, (-4.8, 29.2, 9.6, 9.6, 0.8, 4.2))
    k.both(BP, PAINT, *disc_y(2.3, 20.4, 15.0, 1.7, 8.6))                                       # filter canisters
    k.both(BP, DARK, *disc_y(2.3, 29.0, 15.0, 1.9, 0.9), *disc_y(2.3, 20.0, 15.0, 1.9, 0.5))
    k.both(BP, DARK, *[d for i in range(2) for d in disc_y(2.3, 22.6 + 3.0 * i, 15.0, 1.85, 0.4)])  # filter bands
    k.both(BP, METAL, (2.0, 29.9, 14.7, 0.6, 1.2, 0.6))
    k.both(BP, PAINT2, (4.4, 20.4, 10.0, 1.7, 5.0, 3.3))                                         # jerrycans
    k.both(BP, DARK, (4.55, 25.4, 10.6, 1.4, 0.6, 2.0), (6.1, 21.6, 10.4, 0.2, 2.6, 2.5))
    return k


def build(a=A):
    return _kit().out()
