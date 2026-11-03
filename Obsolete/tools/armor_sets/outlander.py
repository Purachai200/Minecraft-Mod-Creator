"""Outlander raiders (registry faction "Outlander"): a gunmetal tub hidden under a sand-cloth hood, ragged
canvas drapes, reactive-armour bricks bolted everywhere, sandbagged glacis, smoke dischargers, whip antenna."""
import json
import math
import os

from ._common import *  # noqa: F401,F403

SET_ID = "outlander"
UV_REGION = ("Outlander", [(400, 165, 60, 150), (340, 315, 80, 85), (200, 240, 60, 75)])

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

GLACIS = (0, 22.0, -6.5, -26, 0, 0)          # pivot + rotation of the chest glacis plane


def glacis(x, y, z, sx, sy, sz):
    return rot_box(x, y, z, sx, sy, sz, *GLACIS)


def build(a=A, kit=None):
    k = kit or Kit()
    H, C, CN = "armor_head_hood", "armor_chest_hood", "canopy_hood"

    # ---- head: periscope block under a cloth cowl, one slit lens ----
    k.add(H, "paint", [(-2.0, 31.2, -4.2, 4.0, 2.6, 2.6), (-2.3, 30.6, -3.8, 4.6, 0.6, 2.4)])
    k.add(H, "glass", [(-1.4, 32.2, -4.5, 2.8, 0.6, 0.3)])
    k.add(H, "steel", [(-0.6, 33.8, -3.6, 1.2, 1.2, 1.2), (-0.8, 34.6, -3.9, 1.6, 0.5, 0.6)])
    k.add(H, "canvas", [(-2.6, 33.6, -4.8, 5.2, 0.6, 3.6), (-2.6, 30.8, -4.6, 0.4, 2.8, 3.2), (2.2, 30.8, -4.6, 0.4, 2.8, 3.2),
                        (-2.5, 33.2, -5.1, 5.0, 0.5, 0.5), (-1.6, 30.0, -1.6, 1.0, 1.4, 0.3), (0.8, 29.6, -1.6, 0.9, 1.8, 0.3)])

    # ---- chest: steep glacis tiled with ERA bricks, sandbag row, smoke dischargers ----
    k.add(C, "paint", [glacis(-5.4, 22.0, -7.2, 10.8, 9.6, 1.4),
                       rot_box(-4.5, 16.5, -4.2, 9.0, 6.2, 1.4, 0, 17.0, -4.2, 28, 0, 0),
                       (-3.0, 29.8, -3.6, 6.0, 1.4, 1.4),
                       rot_box(3.2, 14.5, -4.0, 1.2, 5.4, 3.8, 3.5, 18.0, -2.5, 0, 0, -16),
                       rot_box(-4.4, 14.5, -4.0, 1.2, 5.4, 3.8, -3.5, 18.0, -2.5, 0, 0, 16),
                       rot_box(3.0, 22.0, -6.5, 2.8, 7.6, 2.0, 3.2, 23.0, -5.5, -20, 16, -8),
                       rot_box(-5.8, 22.0, -6.5, 2.8, 7.6, 2.0, -3.2, 23.0, -5.5, -20, -16, 8)])
    k.add(C, "mark", [glacis(-5.0 + 2.55 * i, 22.6 + 3.0 * j, -8.0, 2.35, 2.7, 0.8) for j in range(3) for i in range(4)])
    k.add(C, "canvas", [(-4.3 + 2.9 * i, 14.6, -7.0, 2.7, 1.8, 2.4) for i in range(3)]
          + [(-2.85 + 2.9 * i, 16.2, -6.6, 2.7, 1.7, 2.2) for i in range(2)])
    k.sym(C, "paint", [(3.0, 29.0, -5.6, 3.4, 0.6, 2.0)])
    k.sym(C, "dark", [rot_box(3.2 + 1.05 * i, 29.4, -6.6, 0.9, 0.9, 2.6, 4.6, 29.8, -5.2, -40, 0, 0) for i in range(3)])
    k.add(C, "paint", leg_fairing())

    # ---- canopy: canvas hood over the box cab, ragged drapes, lamp, whip antenna, jerry can ----
    roof, rear = 33.7, 9.47
    k.add(CN, "paint", [(-5.5, 19.5, rear, 11.0, roof + 1.0 - 19.5, 0.8),
                        (5.9, 19.5, -2.2, 0.8, roof - 19.5, rear + 2.2), (-6.7, 19.5, -2.2, 0.8, roof - 19.5, rear + 2.2),
                        (-3.0, 31.0, -3.6, 6.0, roof - 31.0, 1.2),
                        (2.8, 26.5, -3.6, 3.2, roof - 26.5, 1.2), (-6.0, 26.5, -3.6, 3.2, roof - 26.5, 1.2),
                        (-5.5, roof, -2.5, 11.0, 1.0, rear + 3.3)])
    k.add(CN, "canvas", [(-6.8, roof + 1.0, -4.0, 13.6, 0.8, 14.8), (-4.8, roof + 1.8, -3.2, 9.6, 0.8, 13.0),
                         rot_box(-6.8, roof + 0.2, -6.0, 13.6, 0.6, 2.2, 0, roof + 1.4, -4.0, 22, 0, 0),
                         (-6.0, 25.6, rear + 0.8, 12.0, 9.0, 0.5)])
    drape = [(6.7, 26.6, -3.2, 0.45, 8.9, 13.2)] + \
        [(6.75, 26.6 - d, -3.0 + 1.6 * i, 0.35, d + 0.1, 1.2) for i, d in enumerate((2.4, 4.1, 1.6, 3.2, 5.0, 2.2, 3.8, 1.4))]
    k.add(CN, "canvas", sym(*drape))
    k.add(CN, "canvas", [(-5.6 + 1.5 * i, 25.6 - d, rear + 0.9, 1.2, d + 0.1, 0.35) for i, d in enumerate((2.0, 3.6, 1.2, 4.4, 2.6, 3.0, 1.8, 3.9))])
    k.add(CN, "dark", [(-6.0, roof + 1.8, -4.4, 1.8, 1.4, 1.4), (4.9, roof + 1.8, 8.4, 0.8, 0.8, 0.8)])
    k.add(CN, "lamp", [(-5.8, roof + 2.0, -4.5, 1.4, 1.0, 0.1)])
    k.add(CN, "steel", [(5.1, roof + 2.6, 8.6, 0.3, 11.0, 0.3), (4.6, 23.0, rear + 1.4, 0.4, 7.0, 0.4)])
    k.add(CN, "accent", [(1.0, 21.6, rear + 1.3, 3.2, 4.4, 1.4), (1.8, 26.0, rear + 1.5, 1.6, 0.6, 1.0)])

    # ---- pauldrons: thick slab boxes, ERA on the outer face, cloth mantle ----
    pl = [(6.6, 33.4, -4.6, 6.2, 1.2, 8.2), (11.6, 26.0, -4.4, 1.4, 7.6, 7.8),
          (6.8, 27.4, -5.0, 5.2, 6.2, 0.8), (6.8, 27.4, 2.6, 5.2, 6.2, 0.8)]
    era = [(13.0, 26.6 + 3.4 * j, -4.0 + 3.6 * i, 0.8, 3.0, 3.2) for i in range(2) for j in range(2)]
    mantle = [(6.4, 34.6, -4.2, 6.8, 0.5, 7.4), (12.8, 31.0, -4.2, 0.4, 4.1, 7.4)] + \
        [(12.85, 31.0 - d, -4.0 + 1.5 * i, 0.3, d + 0.1, 1.1) for i, d in enumerate((1.6, 3.0, 1.0, 2.4, 3.4))]
    for s, b in (("left", 1), ("right", -1)):
        f = (lambda bs: bs) if b > 0 else (lambda bs: [mx(v) for v in bs])
        bone = f"armor_{s}_shoulder_outlander"
        k.add(bone, "paint", f(pl))
        k.add(bone, "mark", f(era))
        k.add(bone, "canvas", f(mantle))

    # ---- legs: slab cuisses with ERA and canvas wraps; greaves with brick facing and mud flap ----
    cu = [(2.8, 10.4, -4.4, 3.6, 7.0, 1.0), (6.3, 9.4, -3.2, 0.9, 8.4, 5.6), (2.6, 16.6, -3.6, 4.4, 1.2, 5.6)]
    k.pair("armor_left_leg_outlander", "armor_right_leg_outlander", "paint", cu)
    k.pair("armor_left_leg_outlander", "armor_right_leg_outlander", "mark", [(7.2, 11.0, -2.6, 0.7, 2.8, 3.0), (7.2, 14.0, -2.6, 0.7, 2.6, 3.0)])
    k.pair("armor_left_leg_outlander", "armor_right_leg_outlander", "canvas", [(2.6, 13.2, -4.7, 4.9, 1.3, 7.6), (6.5, 11.2, 1.0, 0.3, 2.0, 0.9)])
    gr = [rot_box(2.6, 3.0, -5.8, 3.8, 7.4, 1.2, 4.5, 6.0, -5.2, -10, 0, 0), (6.2, 2.6, -3.8, 0.9, 7.6, 6.4),
          (3.0, 8.4, -6.2, 3.0, 2.6, 1.4)]
    k.pair("armor_left_shin_outlander", "armor_right_shin_outlander", "paint", gr)
    k.pair("armor_left_shin_outlander", "armor_right_shin_outlander", "mark",
           [rot_box(2.7 + 1.85 * i, 3.6 + 2.5 * j, -6.6, 1.65, 2.3, 0.8, 4.5, 6.0, -5.2, -10, 0, 0) for i in range(2) for j in range(2)])
    k.pair("armor_left_shin_outlander", "armor_right_shin_outlander", "rubber", [(3.0, 2.4, 3.8, 3.0, 3.4, 0.4)])
    return k.out


SAND, GUN, CLOTH = (150, 120, 84), (66, 70, 68), (176, 152, 110)


def set_colour(mat, ci, camo, x, y, nm, nc):
    if mat == "canvas":
        return _mix(CLOTH, (120, 96, 66), _h(ci, 3, 1) * 0.6) if camo == 0 else _mix(_camo(camo, x, y, nm, nc, CLOTH), CLOTH, 0.45)
    if mat == "accent":
        return (92, 98, 60) if camo == 0 else _mul(_camo(camo, x, y, nm, nc, GUN), 0.8)
    if mat == "mark":                         # ERA bricks: faded sand paint over gunmetal
        return SAND if camo == 0 else _mul(_camo(camo, x, y, nm, nc, SAND), 0.9)
    return _camo(camo, x, y, nm, nc, GUN)


def stencil(mat, ci, face, lx, ly, fw, fh):
    if fw < 9 or fh < 7:
        return None
    if mat == "paint" and face in ("east", "west", "north") and _digits("27", lx, ly, 2, 2):
        return (214, 200, 160)
    return None
