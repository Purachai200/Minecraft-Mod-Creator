"""Riverine Recon (registry faction "Riverine"): brown-water navy. A boat-prow tub with a raked spray shield, float
pontoons on the flanks and shoulders, nav lights, searchlight, life ring, snorkel stack and twin waterjet pumps."""
from ._common import *  # noqa: F401,F403

SET_ID = "riverine"
UV_REGION = ("Riverine", [(767, 0, 85, 340)])
SCHEME = {"paint": (82, 92, 66), "paint2": (58, 66, 50), "accent": (226, 176, 36), "primer": (124, 70, 46),
          "bare": (110, 108, 100), "stencil": (222, 220, 200), "canvas": (150, 132, 96), "dark": (34, 36, 34),
          "glass": (70, 120, 130), "lamp": (255, 240, 200), "red": (196, 40, 32), "chip": 0.9, "grime": 0.34,
          "mottle": 0.3}
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
    H, C, CN, BP = "armor_head_riverine", "armor_chest_riverine", "canopy_riverine", "backpack_riverine"

    # ---- head: sonar turret, twin acoustic eyes, hydrophone fin ----
    k.add(H, PAINT, (-2.2, 30.8, -4.3, 4.4, 2.8, 2.7))
    k.add(H, PAINT2, *disc_y(0.0, 33.6, -3.0, 1.9, 0.9))                                       # turret ring
    k.add(H, PAINT, *disc_y(0.0, 34.5, -3.0, 1.4, 0.7))
    k.add(H, DARK, (-2.0, 31.2, -4.55, 4.0, 2.0, 0.3))
    k.add(H, GLASS, *disc_z(-1.0, 32.2, -4.75, 0.7, 0.3), *disc_z(1.0, 32.2, -4.75, 0.7, 0.3))
    k.add(H, ACCENT, (-2.25, 30.8, -4.4, 4.5, 0.4, 2.8))                                          # gasket band
    k.add(H, DARK, rb((-0.15, 35.0, -3.6, 0.3, 1.6, 1.8), (0, 35.0, -2.7), (-25, 0, 0)))       # hydrophone fin

    # ---- chest: V-prow hull with rub rail, splash board and bow light ----
    pv = (0.0, 15.0, -7.4)
    k.add(C, (PAINT, "R4", ("north",), False), rb((0.0, 15.0, -7.4, 6.6, 13.2, 1.2), pv, (0, -28, 0)))
    k.add(C, (PAINT, "R4", ("north",), True), rb((-6.6, 15.0, -7.4, 6.6, 13.2, 1.2), pv, (0, 28, 0)))
    k.add(C, DARK, rb((-0.3, 15.0, -7.75, 0.6, 13.2, 0.6), pv, (0, 0, 0)))                     # stem bar
    k.add(C, DARK, rb((0.0, 20.2, -7.6, 6.8, 0.6, 0.5), pv, (0, -28, 0)), rb((-6.8, 20.2, -7.6, 6.8, 0.6, 0.5), pv, (0, 28, 0)))
    k.add(C, ACCENT, rb((0.0, 27.6, -7.55, 6.6, 0.4, 0.3), pv, (0, -28, 0)), rb((-6.6, 27.6, -7.55, 6.6, 0.4, 0.3), pv, (0, 28, 0)))
    k.add(C, PAINT2, rb((-6.0, 27.6, -6.4, 12.0, 0.8, 2.6), (0, 27.6, -5.0), (-20, 0, 0)))     # splash board
    k.add(C, LAMP, (-0.5, 25.0, -8.15, 1.0, 1.0, 0.4))                                            # bow light
    k.add(C, METAL, *sym(*bolts((1.2, 17.0, -7.2), (5.0, 17.0, -5.2), 4, 0.4, 0.3)))
    k.add(C, PAINT2, (-5.0, 14.4, -5.4, 10.0, 1.0, 3.0))                                          # keel shoe
    k.add(C, PAINT2, *leg_fairing())

    # ---- canopy: low armoured tub, raked spray shield, flank pontoons, life ring, nav lights, searchlight ----
    roof = 33.7
    k.add(CN, PAINT, (-6.2, roof, -3.0, 12.4, 1.0, 13.4))
    k.add(CN, PAINT2, (-4.2, roof + 1.0, 3.0, 8.4, 0.5, 5.6))
    k.both(CN, PAINT, (5.6, 18.6, -3.4, 1.2, roof - 18.6, 13.8))
    k.both(CN, PAINT, (2.6, 28.4, -4.0, 3.2, roof - 28.4, 1.0))
    k.both(CN, GLASS, (3.0, 30.6, -4.15, 2.4, 1.6, 0.2))
    sp, sr = (0.0, roof, -3.8), (-28, 0, 0)                                                       # spray shield, raked back
    k.both(CN, DARK, rb((0.2, roof - 0.2, -4.4, 6.4, 4.4, 0.5), sp, sr))
    k.both(CN, GLASS, rb((1.0, roof + 0.6, -4.55, 2.4, 3.0, 0.2), sp, sr), rb((3.8, roof + 0.6, -4.55, 2.4, 3.0, 0.2), sp, sr))
    k.both(CN, DARK, rb((6.3, roof - 0.2, -4.4, 0.5, 4.6, 3.0), sp, sr))                          # shield side cheeks
    for side in (1, -1):                                                                          # flank pontoons
        cx = 7.6 * side
        k.add(CN, PAINT2, *[(cx - 1.6, 18.4, -2.4 + 0.0, 3.2, 3.2, 12.6)])
        k.add(CN, PAINT2, (cx - 1.2, 18.0, -1.8, 2.4, 4.0, 11.4))
        k.add(CN, ACCENT, (cx - 1.7, 19.6, -2.55, 3.4, 0.6, 0.3), (cx - 1.7, 19.6, 10.25, 3.4, 0.6, 0.3))
        k.add(CN, CANVAS, (cx - 1.7, 21.5, 1.0, 3.4, 0.3, 0.4), (cx - 1.7, 21.5, 6.0, 3.4, 0.3, 0.4))
    k.add(CN, RED, (6.8, 26.0, -3.6, 0.6, 1.0, 1.0))                                              # port nav light
    k.add(CN, GLASS, (-7.4, 26.0, -3.6, 0.6, 1.0, 1.0))                                       # starboard
    k.add(CN, ACCENT, *ring_x(6.8, 28.0, 5.2, 2.1, 0.6, 12, 0.9))                                # life ring (port)
    k.add(CN, CANVAS, (6.8, 26.4, 5.0, 0.5, 3.2, 0.4))
    k.add(CN, PAINT, (-6.2, 21.6, 9.5, 12.4, roof + 1.0 - 21.6, 1.0))                            # rear wall
    k.add(CN, ACCENT, (-6.2, 32.0, 10.4, 12.4, 0.5, 0.3))
    k.add(CN, DARK, *disc_y(-3.2, roof + 1.0, -1.0, 1.0, 0.6))                                    # searchlight
    k.add(CN, DARK, rb((-4.3, roof + 1.6, -2.0, 2.2, 2.0, 2.2), (-3.2, roof + 2.6, -0.9), (-10, 0, 0)))
    k.add(CN, LAMP, rb((-4.0, roof + 1.9, -2.15, 1.6, 1.4, 0.2), (-3.2, roof + 2.6, -0.9), (-10, 0, 0)))
    k.add(CN, DARK, (4.8, roof + 1.0, 7.8, 0.8, 0.6, 0.8), (5.05, roof + 1.6, 8.05, 0.3, 8.0, 0.3))  # whip antenna
    k.add(CN, ACCENT, (4.95, roof + 9.6, 7.95, 0.5, 0.4, 0.5))
    k.add(CN, METAL, *bolts((-5.6, 33.3, 10.45), (5.6, 33.3, 10.45), 8, 0.4, 0.25))

    # ---- pauldrons: float collar pontoons with gasket bands and a spray skirt ----
    pd = "shoulder_riverine"
    k.pair(pd, PAINT2, *disc_z(9.4, 33.6, -4.2, 2.2, 8.4))                                       # pontoon
    k.pair(pd, PAINT2, *disc_z(9.4, 33.6, -4.6, 1.5, 0.4), *disc_z(9.4, 33.6, 4.2, 1.5, 0.4))     # end caps
    k.pair(pd, ACCENT, (7.1, 35.5, -2.4, 4.6, 0.3, 0.6), (7.1, 35.5, 2.0, 4.6, 0.3, 0.6))
    k.pair(pd, (PAINT, "4", ("east", "west"), ("east",)), (11.2, 25.6, -3.8, 1.2, 7.2, 7.6))         # spray skirt
    k.pair(pd, PAINT, rb((6.8, 25.4, -4.6, 5.0, 6.6, 0.9), (9.0, 31.5, -4.2), (-10, 0, 0)))
    k.pair(pd, METAL, *bolts((12.5, 31.8, -3.2), (12.5, 31.8, 3.2), 4, 0.4, 0.25, 0))
    k.pair(pd, CANVAS, (11.3, 27.6, -4.0, 1.4, 0.4, 8.0))                                       # grab line

    # ---- thighs: hull plates with outboard foam float blocks ----
    lg = "leg_riverine"
    k.pair(lg, PAINT, (2.7, 10.2, -4.6, 3.8, 7.2, 1.2), (2.8, 17.0, -3.4, 4.2, 1.0, 5.8))
    k.pair(lg, PAINT2, (6.3, 9.6, -3.6, 2.4, 7.6, 6.0))                                         # float block
    k.pair(lg, ACCENT, (6.25, 12.6, -3.7, 2.5, 0.5, 6.2))
    k.pair(lg, CANVAS, (8.6, 10.6, -2.0, 0.3, 5.6, 0.4), (8.6, 10.6, 1.6, 0.3, 5.6, 0.4))
    k.pair(lg, PAINT, (3.0, 7.6, -5.8, 3.0, 2.8, 1.4))
    k.pair(lg, METAL, *bolts((3.2, 16.4, -4.75), (6.0, 16.4, -4.75), 3, 0.35, 0.2))

    # ---- shins: greave with drain louvres and ankle spray fins ----
    sh = "shin_riverine"
    k.pair(sh, PAINT, (2.7, 3.0, -6.1, 3.8, 7.4, 1.3), (6.2, 2.6, -4.8, 1.2, 7.4, 6.2))
    k.pair(sh, DARK, *[(3.1, 4.2 + 1.1 * i, -6.25, 3.0, 0.4, 0.3) for i in range(3)])
    k.pair(sh, PAINT2, rb((7.0, 2.0, -3.6, 0.5, 3.4, 5.6), (7.2, 2.0, 0.0), (0, 0, -18)))       # spray fin
    k.pair(sh, ACCENT, (2.65, 9.6, -6.2, 3.9, 0.5, 1.4))
    k.pair(sh, PAINT2, (3.0, 4.0, 3.6, 3.0, 5.4, 1.0))

    # ---- backpack: pump housing, twin waterjet nozzles, snorkel stack, rope coil ----
    k.add(BP, PAINT, (-4.4, 19.8, 9.8, 8.8, 8.8, 3.2))
    k.add(BP, PAINT2, (-4.8, 28.6, 9.6, 9.6, 0.8, 3.8))
    k.both(BP, PAINT2, *disc_z(2.6, 22.6, 13.0, 1.8, 2.4))                                       # waterjet shrouds
    k.both(BP, DARK, *disc_z(2.6, 22.6, 15.4, 1.3, 0.8))
    k.both(BP, ACCENT, *disc_z(2.6, 22.6, 14.2, 1.95, 0.4))
    k.add(BP, PAINT, (-5.9, 20.0, 10.4, 1.4, 22.0, 1.4))                                         # snorkel stack
    k.add(BP, DARK, (-6.3, 41.6, 9.6, 2.2, 1.4, 2.6), (-6.2, 41.2, 9.2, 2.0, 0.8, 0.6))           # cowl head
    k.add(BP, ACCENT, (-6.05, 36.0, 10.25, 1.7, 0.5, 1.7))
    k.add(BP, CANVAS, *ring_x(-4.3, 25.6, 14.2, 1.4, 1.0, 10, 0.8))                              # rope coil
    k.add(BP, (PAINT2, "R4", ("south",), False), (-3.6, 24.6, 13.0, 7.2, 3.6, 0.3))
    return k


def build(a=A):
    return _kit().out()
