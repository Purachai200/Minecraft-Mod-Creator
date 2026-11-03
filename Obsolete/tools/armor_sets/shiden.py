"""Shiden Corps (registry faction "Shiden"): samurai-cut field armour. Kabuto-style cab with flared fukigaeshi
wings and a forward peak, slit-visor helm with V-horn crest, layered sode shoulder plates, kusazuri skirt
tassets, lamellar suneate greaves, sashimono banner pole on a compact sealed backpack. Ink blue-grey,
lacquer-red cords and trims, white hinomaru and unit numbers."""
import json
import math
import os

from ._common import *  # noqa: F401,F403

SET_ID = "shiden"
UV_REGION = ("Shiden", [(597, 0, 85, 340)])

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
    H, C, CN, BP = "armor_head_shiden", "armor_chest_shiden", "canopy_shiden", "backpack_shiden"

    # ---- head: helm with slit visor, V-horn crest (kuwagata) and neck flap ----
    k.add(H, "paint", [(-2.2, 31.0, -3.8, 4.4, 2.8, 2.4), rot_box(-2.6, 33.6, -4.6, 5.2, 0.6, 3.2, 0, 33.8, -3.0, -10, 0, 0)])
    k.add(H, "glass", [(-1.8, 32.0, -3.9, 3.6, 0.5, 0.1)])
    k.add(H, "brass", [rot_box(0.2, 34.0, -4.4, 0.45, 4.2, 0.45, 0.3, 34.0, -4.2, 0, 0, -28),
                       rot_box(-0.65, 34.0, -4.4, 0.45, 4.2, 0.45, -0.3, 34.0, -4.2, 0, 0, 28),
                       (-0.6, 33.9, -4.5, 1.2, 0.8, 0.4)])
    k.add(H, "red", [(-0.4, 34.0, -4.6, 0.8, 0.6, 0.1)])

    # ---- chest: faceted breastplate (do), red cord rows, kusazuri tassets ----
    k.add(C, "paint", [rot_box(-5.4, 22.0, -7.2, 10.8, 9.6, 1.4, 0, 22.0, -6.5, -26, 0, 0),
                       rot_box(-3.0, 23.0, -8.2, 6.0, 7.6, 0.8, 0, 22.0, -6.5, -26, 0, 0),
                       rot_box(-4.5, 16.5, -4.2, 9.0, 6.2, 1.4, 0, 17.0, -4.2, 28, 0, 0),
                       (-3.0, 29.8, -3.6, 6.0, 1.4, 1.4),
                       rot_box(3.0, 22.0, -6.5, 2.8, 7.6, 2.0, 3.2, 23.0, -5.5, -20, 16, -8),
                       rot_box(-5.8, 22.0, -6.5, 2.8, 7.6, 2.0, -3.2, 23.0, -5.5, -20, -16, 8)])
    k.add(C, "red", [rot_box(-5.6, 22.6 + 2.6 * j, -7.5, 11.2, 0.3, 0.4, 0, 22.0, -6.5, -26, 0, 0) for j in range(3)])
    tass = []
    for i, x in enumerate((-4.6, -1.5, 1.6)):                       # front kusazuri: 3 panels x 2 lames
        tass += [rot_box(x, 14.2 - 0.0 * i, -6.4, 3.0, 2.0, 0.6, x + 1.5, 16.2, -6.0, 14, 0, 0),
                 rot_box(x, 12.4, -6.9, 3.0, 2.0, 0.6, x + 1.5, 16.2, -6.0, 14, 0, 0)]
    k.add(C, "paint", tass)
    k.add(C, "red", [rot_box(-4.6, 16.0, -6.2, 9.2, 0.4, 0.5, 0, 16.2, -6.0, 14, 0, 0)])
    k.sym(C, "paint", [rot_box(4.2, 13.6, -3.6, 0.6, 2.4, 4.6, 4.5, 16.0, -1.0, 0, 0, 12),
                       rot_box(4.6, 11.8, -3.6, 0.6, 2.2, 4.6, 4.5, 16.0, -1.0, 0, 0, 12)])
    k.add(C, "paint", leg_fairing())

    # ---- canopy: kabuto cab, flared fukigaeshi wings, forward peak, maedate, red cords ----
    roof, rear = 33.7, 9.47
    k.add(CN, "paint", [(-5.5, 19.5, rear, 11.0, roof + 1.0 - 19.5, 0.8),
                        (5.9, 19.5, -2.2, 0.8, roof - 19.5, rear + 2.2), (-6.7, 19.5, -2.2, 0.8, roof - 19.5, rear + 2.2),
                        (-3.0, 31.0, -3.6, 6.0, roof - 31.0, 1.2),
                        (2.8, 26.5, -3.6, 3.2, roof - 26.5, 1.2), (-6.0, 26.5, -3.6, 3.2, roof - 26.5, 1.2),
                        (-5.5, roof, -2.5, 11.0, 1.0, rear + 3.3), (-4.4, roof + 1.0, -1.6, 8.8, 0.8, 11.0),
                        (-0.4, roof + 1.8, -1.6, 0.8, 0.8, 11.0),
                        rot_box(-6.4, roof - 0.4, -5.6, 12.8, 0.6, 3.4, 0, roof + 0.2, -2.4, -14, 0, 0)])
    k.sym(CN, "paint", [rot_box(6.8, 27.6, -4.8, 0.7, 6.6, 5.4, 6.8, 27.6, -2.0, 0, 0, -20),
                        rot_box(6.4, 28.2, 6.0, 0.6, 5.6, 4.4, 6.6, 34.0, 8.0, 0, 0, -16),
                        rot_box(6.4, 22.4, 6.0, 0.6, 5.4, 4.4, 6.6, 34.0, 8.0, 0, 0, -12)])
    k.sym(CN, "red", [rot_box(7.5, 30.0, -4.6, 0.2, 0.4, 5.0, 6.8, 27.6, -2.0, 0, 0, -20)])
    k.add(CN, "red", [(-5.5, 26.0, rear + 0.8, 11.0, 0.5, 0.3), (-5.5, 22.0, rear + 0.8, 11.0, 0.5, 0.3)])
    k.add(CN, "brass", [(-1.0, roof + 0.6, -5.9, 2.0, 2.2, 0.4)])
    k.add(CN, "steel", [(4.8, roof + 1.0, 8.8, 0.3, 8.0, 0.3)])

    # ---- sode: four stepped lames hanging off a rounded cap, red cord down the middle ----
    sode = [(6.6, 33.2, -4.4, 5.8, 1.2, 8.0)] + \
        [rot_box(11.0 + 0.45 * i, 32.4 - 2.3 * i, -4.6, 0.9, 2.4, 8.4, 11.0, 33.0, -0.4, 0, 0, 6 + 2 * i) for i in range(4)]
    for s, sg in (("left", 1), ("right", -1)):
        f = (lambda bs: bs) if sg > 0 else (lambda bs: [mx(v) for v in bs])
        bone = f"armor_{s}_shoulder_shiden"
        k.add(bone, "paint", f(sode))
        k.add(bone, "red", f([rot_box(11.9 + 0.45 * i, 32.0 - 2.3 * i, -0.8, 0.3, 2.6, 0.8, 11.0, 33.0, -0.4, 0, 0, 6 + 2 * i)
                               for i in range(4)] + [(7.0, 34.4, -4.6, 5.0, 0.3, 0.6)]))

    # ---- legs: haidate thigh plates, suneate splints with red bindings ----
    L, R = "armor_left_leg_shiden", "armor_right_leg_shiden"
    k.pair(L, R, "paint", [(2.8, 10.4, -4.2, 3.6, 7.0, 0.9), (6.3, 9.4, -3.0, 0.8, 8.4, 5.2), (2.6, 16.4, -3.4, 4.4, 1.2, 5.6)])
    k.pair(L, R, "red", [(2.7, 12.4, -4.4, 3.8, 0.4, 0.3), (2.7, 14.8, -4.4, 3.8, 0.4, 0.3)])
    LS, RS = "armor_left_shin_shiden", "armor_right_shin_shiden"
    k.pair(LS, RS, "paint", [rot_box(2.6 + 0.8 * i, 3.0, -5.8, 0.75, 7.4, 1.0, 4.5, 6.0, -5.2, -10, 0, 0) for i in range(5)]
           + [(6.2, 2.6, -3.8, 0.8, 7.6, 6.2), (2.8, 8.6, -6.4, 3.4, 2.4, 1.4)])
    k.pair(LS, RS, "red", [rot_box(2.5, 4.2 + 3.0 * j, -6.0, 4.2, 0.4, 1.4, 4.5, 6.0, -5.2, -10, 0, 0) for j in range(2)])

    # ---- backpack: sealed pack with round ports, sashimono banner pole ----
    add_bp = lambda m, bs: k.add(BP, m, back_fit(bs))     # authored against the legacy mount plane
    add_bp("paint", MOUNT[:1] + [(-3.8, 22.4, 7.6, 7.6, 8.4, 2.6)])
    add_bp("dark", [*disc_z(-1.8, 26.6, 10.2, 1.3, 0.6), *disc_z(1.8, 26.6, 10.2, 1.3, 0.6)])
    add_bp("red", [(-3.9, 29.6, 7.5, 7.8, 0.5, 2.8)])
    add_bp("steel", [(2.6, 22.0, 9.6, 0.5, 26.0, 0.5), (2.6, 47.4, 9.6, 0.5, 0.5, 0.5)])
    add_bp("banner", [(2.85, 34.0, 9.7, 0.2, 13.4, 0.3)])
    add_bp("banner", [(3.1, 34.2, 9.75, 4.6, 13.0, 0.2)])
    return k.out


INK, RED = (50, 58, 70), (172, 34, 30)


def set_colour(mat, ci, camo, x, y, nm, nc):
    if mat == "banner":
        return (226, 222, 210) if camo == 0 else _mix(_camo(camo, x, y, nm, nc, INK), (226, 222, 210), 0.5)
    return _camo(camo, x, y, nm, nc, INK)


def stencil(mat, ci, face, lx, ly, fw, fh):
    if mat == "banner":                       # red disc on the banner
        return RED if (lx - fw / 2) ** 2 + (ly - fh * 0.35) ** 2 < (fw * 0.3) ** 2 else None
    if mat == "paint" and face in ("east", "west") and fw >= 9 and fh >= 7 and (lx - 4.5) ** 2 + (ly - 3.5) ** 2 < 5:
        return (228, 226, 216)                # hinomaru roundel ring
    if mat == "paint" and face == "north" and _digits("51", lx, ly, fw - 9, fh - 7):
        return (226, 222, 210)
    return None
