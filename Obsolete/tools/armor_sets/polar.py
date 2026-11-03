"""Polar Front (registry faction "Polar"): rounded white arctic cab with quilted insulation, hi-vis orange panels,
twin searchlights, binocular sensor under a sun hood, long touring skis, twin MANPADS tubes over each shoulder."""
import json
import math
import os

from ._common import *  # noqa: F401,F403

SET_ID = "polar"
UV_REGION = ("Polar", [(460, 0, 52, 315), (420, 315, 92, 85)])

# ---- kit: cubes plus one paint material per cube (same block in outlander/polar/salvage/shiden) ----
class Kit:
    def __init__(self):
        self.out, self.mat = {}, {}

    def add(self, bone, mat, boxes):
        self.out.setdefault(bone, []).extend(boxes)
        self.mat.setdefault(bone, []).extend([mat] * len(boxes))

    def pair(self, left, right, mat, boxes):
        self.add(left, mat, boxes)
        self.add(right, mat, [mx(b) for b in boxes])

    def sym(self, bone, mat, boxes):
        self.add(bone, mat, sym(*boxes))


def _h(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2246822519) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return (n ^ (n >> 16)) / 0xffffffff


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _mul(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def _camo(camo, x, y, nm, nc, base):
    if camo == 1:   # woodland
        v = _h(x // 6, y // 6, 77)
        return (74, 94, 52) if v < .35 else (46, 62, 34) if v < .6 else (102, 78, 52) if v < .82 else (22, 26, 20)
    if camo == 2:   # desert
        d = math.sin(x * .05) * math.cos(y * .05) + nm * .6
        return (168, 142, 102) if d > .45 else (205, 184, 138) if d > -.15 else (128, 102, 72)
    if camo == 3:   # urban
        g = 34 + ((x // 8) + (y // 14) * 2) % 3 * 9
        return (g, g + 2, g + 5)
    if camo == 4:   # arctic
        return (226, 232, 236) if nc < .55 else (150, 160, 170) if nc < .68 else (196, 204, 210)
    if camo == 5:   # tigerstripe
        return [(24, 28, 22), (56, 82, 42), (112, 92, 58), (42, 60, 32)][(y + int(math.sin(x * .08) * 8)) // 8 % 4]
    if camo == 6:   # hazard
        return (255, 204, 0) if nc < .65 else (150, 120, 40)
    return base


DIG = {"0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001011001111",
       "4": "101101111001001", "5": "111100111001111", "6": "111100111101111", "7": "111001010010010",
       "8": "111101111101111", "9": "111101111001111"}


def _digits(s, lx, ly, ox, oy):
    """True if (lx, ly) falls on a 3x5 stencil digit of s drawn from (ox, oy)."""
    gx, gy = lx - ox, ly - oy
    if not (0 <= gy < 5 and 0 <= gx < 4 * len(s)) or gx % 4 == 3:
        return False
    return DIG[s[gx // 4]][gy * 3 + gx % 4] == "1"


FIXED = {"steel": (78, 80, 82), "dark": (36, 38, 41), "rubber": (24, 24, 26), "glass": (40, 150, 120),
         "lamp": (255, 236, 170), "rust": (112, 62, 36), "brass": (176, 140, 60), "red": (176, 36, 30)}
_MAP = None


def _texels():
    """(x, y) -> (material, face, lx, ly, fw, fh, cube index) for this set's packed cubes."""
    global _MAP
    if _MAP is None:
        _MAP, kit = {}, Kit()
        build(A, kit)
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "packed_armor_uvs.json")
        for e in json.load(open(path)):
            if e["faction"] != UV_REGION[0] or e["bone"] not in kit.mat:
                continue
            m = kit.mat[e["bone"]][e["cube_index"]]
            for face, (x0, y0, x1, y1) in e["faces"].items():
                for y in range(y0, y1):
                    for x in range(x0, x1):
                        _MAP[(x, y)] = (m, face, x - x0, y - y0, x1 - x0, y1 - y0, e["cube_index"])
    return _MAP


def paint(x, y, camo_id, n_fine, n_med, n_coarse):
    t = _texels().get((x, y))
    if t is None:
        return None
    mat, face, lx, ly, fw, fh, ci = t
    grit = 0.86 + 0.24 * n_fine
    edge = lx in (0, fw - 1) or ly in (0, fh - 1)
    side = face in ("north", "south", "east", "west")
    if mat in FIXED:
        c = FIXED[mat]
        if mat == "glass":
            c = (16, 18, 20) if edge and fw > 2 else (210, 255, 240) if lx == 1 and ly <= 1 else c
        elif mat == "lamp":
            c = (255, 170, 40) if edge else c
        elif mat == "rubber":
            c = (34, 34, 36) if (lx + ly) % 3 == 0 else c
        elif mat == "steel" and edge:
            c = _mul(c, 1.25 if ly == 0 else 0.75)
        elif mat == "brass" and edge:
            c = _mul(c, 0.7)
        return (*_mul(c, grit), 255)
    c = set_colour(mat, ci, camo_id, x, y, n_med, n_coarse)
    if mat == "canvas":                       # woven cloth: weave, sagging folds, stitched hem
        c = _mul(c, 0.93 if (lx + ly) % 2 else 1.04)
        if side and (lx + 2 * ly) % 7 == 0:
            c = _mul(c, 0.82)
        if edge:
            c = _mul(c, 0.78)
        return (*_mul(c, grit), 255)
    # painted steel: welded seams, bolt rows, chipped edges, rust runs, grime, stencils
    c = _mix(c, (60, 52, 44), (n_coarse - 0.55) * 0.9)
    if side and fh >= 4 and _h(x, 0, 9) < 0.14 and ly > fh // 3:
        c = _mix(c, (104, 58, 32), min(0.6, ly / fh * 0.8))
    if side and fh >= 3:
        c = _mix(c, (70, 60, 48), (ly / fh - 0.6) * 0.5)
    if edge and fw >= 3 and fh >= 3 and _h(x, y, 5) < 0.2:
        return (*_mul((128, 124, 114), grit), 255)
    if edge:
        c = _mul(c, 0.7)
    elif fw >= 5 and fh >= 4 and (ly in (1, fh - 2) and lx % 3 == 1 and 0 < lx < fw - 1):
        c = _mul(c, 1.38)
    elif side and fw >= 4 and fh >= 4:
        s = stencil(mat, ci, face, lx, ly, fw, fh)
        if s is not None:
            c = s
    return (*_mul(c, grit), 255)


def build(a=A, kit=None):
    k = kit or Kit()
    H, C, CN = "armor_head_polar", "armor_chest_polar", "canopy_polar"

    # ---- head: binocular sensor under a sun hood, de-icing fins ----
    k.add(H, "paint", [(-2.4, 31.0, -3.6, 4.8, 2.8, 2.4), (-2.8, 33.8, -4.6, 5.6, 0.6, 3.4)])
    k.add(H, "dark", [*disc_z(-1.1, 32.4, -4.2, 0.9, 0.6), *disc_z(1.1, 32.4, -4.2, 0.9, 0.6)])
    k.add(H, "glass", [(-1.6, 31.9, -4.3, 1.0, 1.0, 0.1), (0.6, 31.9, -4.3, 1.0, 1.0, 0.1)])
    k.add(H, "accent", [(-2.8, 31.2, -4.4, 0.4, 2.6, 2.2), (2.4, 31.2, -4.4, 0.4, 2.6, 2.2)])

    # ---- chest: rounded twin-slope glacis, orange hi-vis band, tow hooks ----
    k.add(C, "paint", [rot_box(-5.2, 25.6, -6.2, 10.4, 5.6, 1.4, 0, 26.0, -5.5, -34, 0, 0),
                       rot_box(-5.6, 20.4, -6.8, 11.2, 5.4, 1.4, 0, 21.0, -5.8, -8, 0, 0),
                       rot_box(-4.5, 16.5, -4.2, 9.0, 4.4, 1.4, 0, 17.0, -4.2, 28, 0, 0),
                       (-3.0, 29.8, -3.6, 6.0, 1.4, 1.4)])
    k.sym(C, "paint", [rot_box(4.6, 20.4, -6.2, 1.4, 9.0, 3.0, 5.2, 24.0, -4.6, -10, 0, -8)])
    k.add(C, "accent", [rot_box(-5.8, 23.2, -7.0, 11.6, 1.6, 0.5, 0, 21.0, -5.8, -8, 0, 0)])
    k.sym(C, "dark", [(2.6, 15.2, -6.6, 1.0, 1.6, 1.6)])
    k.add(C, "canvas", [(-4.0 + 2.7 * i, 26.6, -7.8, 2.4, 2.4, 0.9) for i in range(3)])   # snow-camo storage pouches
    k.add(C, "paint", leg_fairing())

    # ---- canopy: rounded roof, quilted insulation, searchlights, fuel drum ----
    roof, rear = 33.7, 9.47
    k.add(CN, "paint", [(-5.5, 19.5, rear, 11.0, roof + 1.0 - 19.5, 0.8),
                        (5.9, 19.5, -2.2, 0.8, roof - 19.5, rear + 2.2), (-6.7, 19.5, -2.2, 0.8, roof - 19.5, rear + 2.2),
                        (-3.0, 31.0, -3.6, 6.0, roof - 31.0, 1.2),
                        (2.8, 26.5, -3.6, 3.2, roof - 26.5, 1.2), (-6.0, 26.5, -3.6, 3.2, roof - 26.5, 1.2),
                        (-5.5, roof, -2.5, 11.0, 1.0, rear + 3.3), (-4.6, roof + 1.0, -2.0, 9.2, 0.7, 11.8)])
    k.sym(CN, "paint", [(5.0, roof + 0.4, -2.3, 1.4, 1.0, 12.4)])
    k.sym(CN, "canvas", [(6.7, 21.0 + 3.0 * j, -1.6 + 3.8 * i, 0.5, 2.7, 3.5) for i in range(3) for j in range(4)])
    k.add(CN, "accent", [(-3.0, roof - 0.6, -3.9, 6.0, 1.2, 0.3), (-5.5, 30.0, rear + 0.8, 11.0, 1.2, 0.3)])
    k.sym(CN, "dark", [(3.0, roof + 2.2, -3.2, 2.0, 1.8, 1.8), (3.6, roof + 1.7, -2.4, 0.8, 0.6, 0.8)])
    k.sym(CN, "lamp", [(3.2, roof + 2.4, -3.3, 1.6, 1.4, 0.1)])
    k.add(CN, "steel", [(-5.0, roof + 1.7, 8.4, 0.3, 9.0, 0.3), (-4.6, 21.0, rear + 0.8, 0.5, 8.0, 0.5)])
    k.add(CN, "accent", [*disc_y(1.6, 21.0, rear + 2.4, 1.6, 6.0)[:2], (0.2, 24.8, rear + 0.8, 2.8, 0.5, 3.4)])

    # ---- pauldrons: rounded insulated caps with orange tips ----
    pl = [(6.6, 33.2, -4.0, 5.6, 1.3, 7.2), (7.4, 34.5, -3.2, 4.0, 0.6, 5.6), (11.4, 27.0, -4.0, 1.3, 6.6, 7.2),
          (12.0, 28.0, -3.0, 0.6, 4.6, 5.2), (6.8, 28.0, -4.6, 4.6, 5.4, 0.8), (6.8, 28.0, 2.6, 4.6, 5.4, 0.8)]
    for s, sg in (("left", 1), ("right", -1)):
        f = (lambda bs: bs) if sg > 0 else (lambda bs: [mx(v) for v in bs])
        bone = f"armor_{s}_shoulder_polar"
        k.add(bone, "paint", f(pl))
        k.add(bone, "accent", f([(11.3, 25.8, -4.1, 1.5, 1.2, 7.4)]))
        k.add(bone, "canvas", f([(12.6, 28.4, -2.4, 0.6, 3.6, 4.0)]))

    # ---- legs: smooth insulated cuisses, greaves with orange cuffs and snow guards ----
    L, R = "armor_left_leg_polar", "armor_right_leg_polar"
    k.pair(L, R, "paint", [(2.8, 10.6, -4.2, 3.6, 6.8, 1.0), (6.3, 9.6, -3.0, 0.9, 8.0, 5.2), (2.6, 16.4, -3.4, 4.4, 1.2, 5.6)])
    k.pair(L, R, "canvas", [(2.7, 12.0, -4.5, 3.8, 3.4, 0.4)])
    LS, RS = "armor_left_shin_polar", "armor_right_shin_polar"
    k.pair(LS, RS, "paint", [rot_box(2.6, 3.2, -5.8, 3.8, 7.2, 1.2, 4.5, 6.0, -5.2, -10, 0, 0), (6.2, 2.8, -3.8, 0.9, 7.4, 6.4),
                             (3.0, 8.4, -6.2, 3.0, 2.6, 1.4)])
    k.pair(LS, RS, "accent", [(2.5, 2.6, -5.6, 4.6, 1.2, 9.6)])

    # ---- skis: long boards with upturned tips, bindings ----
    ski = [(2.2, 0.0, -13.0, 4.6, 0.5, 12.0), (2.2, 0.0, -1.0, 4.6, 0.5, 11.0),
           *stepped(2.2, 2.2, -16.4, 0.3, -13.0, 4.6, 0.5, 4)]
    k.pair("armor_left_ski", "armor_right_ski", "accent", ski)
    k.pair("armor_left_ski", "armor_right_ski", "dark", [(2.0, 0.5, -1.2, 0.5, 1.2, 2.4), (6.5, 0.5, -1.2, 0.5, 1.2, 2.4),
                                                        (2.0, 0.5, 3.6, 0.5, 0.9, 1.6), (6.5, 0.5, 3.6, 0.5, 0.9, 1.6),
                                                        (4.2, 0.5, 9.0, 0.6, 0.4, 0.8)])

    # ---- MANPADS: two launch tubes per side over the shoulders, sight box, IFF whip, bracket ----
    MP = "backpack_manpads"
    k.sym(MP, "tube", [(8.7, 35.5, -8.0, 1.8, 1.8, 13.0), (10.9, 35.5, -8.0, 1.8, 1.8, 13.0)])   # one cube per tube: round tubes overflow the UV region
    k.sym(MP, "dark", [*disc_z(9.6, 36.4, -8.6, 1.25, 0.6), *disc_z(11.8, 36.4, -8.6, 1.25, 0.6),
                       (8.4, 35.0, 5.6, 4.6, 2.8, 0.8), (10.4, 33.2, -1.4, 0.8, 2.4, 0.8), (6.0, 32.8, -1.6, 5.2, 0.6, 1.2)])
    k.sym(MP, "accent", [(8.4, 35.0, -5.0, 4.6, 0.6, 1.0), (8.4, 35.0, 2.0, 4.6, 0.6, 1.0)])
    k.sym(MP, "steel", [(8.4, 37.6, -2.0, 1.2, 1.0, 1.6), (12.6, 37.6, 4.0, 0.25, 5.0, 0.25)])
    return k.out


WHITE, ORANGE, TUBE = (220, 226, 230), (230, 98, 30), (92, 104, 84)


def set_colour(mat, ci, camo, x, y, nm, nc):
    if mat == "accent":
        return ORANGE if camo in (0, 4) else _mul(_camo(camo, x, y, nm, nc, ORANGE), 0.75)
    if mat == "tube":
        return TUBE if camo == 0 else _mul(_camo(camo, x, y, nm, nc, TUBE), 0.85)
    if mat == "canvas":
        return (200, 206, 204) if camo == 0 else _mix(_camo(camo, x, y, nm, nc, WHITE), (190, 190, 180), 0.35)
    if camo == 0:                             # white winter wash, dark splinter showing through where it wore off
        return (150, 160, 166) if nc > 0.68 and _h(x // 5, y // 5, 3) < 0.6 else WHITE
    return _camo(camo, x, y, nm, nc, WHITE)


def stencil(mat, ci, face, lx, ly, fw, fh):
    if fw < 9 or fh < 7:
        return None
    if mat in ("paint", "tube") and _digits("31", lx, ly, 2, 2):
        return (30, 34, 40)
    return None
