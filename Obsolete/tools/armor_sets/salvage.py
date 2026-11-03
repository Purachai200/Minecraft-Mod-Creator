"""Salvage militia (registry faction "Salvage"): scrap-built and lopsided. Mismatched crooked plates in faded
colours, a car-hood glacis hung with spare track links, rebar face grille, corrugated roof, a tyre on one
shoulder and a road-sign slab on the other, welding-mask head, oil drum and junk on the back."""
import json
import math
import os

from ._common import *  # noqa: F401,F403

SET_ID = "salvage"
UV_REGION = ("Salvage", [(512, 0, 85, 340)])

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
    H, C, CN, BP = "armor_head_salvage", "armor_chest_salvage", "canopy_salvage", "backpack_salvage"

    # ---- head: welding-mask box, one big lens off-centre, side pipe ----
    k.add(H, "paint", [rot_box(-2.2, 31.0, -4.0, 4.4, 3.2, 2.4, 0, 32.0, -2.8, 0, 0, 4), (-1.8, 34.0, -3.6, 3.0, 0.6, 1.6)])
    k.add(H, "dark", [*disc_z(0.8, 32.6, -4.5, 1.1, 0.6)])
    k.add(H, "glass", [(0.2, 32.0, -4.6, 1.2, 1.2, 0.1)])
    k.add(H, "steel", [(-2.0, 31.6, -4.3, 1.4, 0.4, 0.3), (-2.0, 32.4, -4.3, 1.4, 0.4, 0.3), (-2.8, 31.4, -3.4, 0.6, 0.6, 2.2)])
    k.add(H, "rust", [(-3.0, 32.0, -2.4, 0.5, 2.6, 0.5)])

    # ---- chest: car-hood glacis, crooked patch plates, track-link apron, hazard panel ----
    k.add(C, "paint", [rot_box(-5.4, 22.0, -7.2, 10.8, 9.6, 1.0, 0, 22.0, -6.5, -26, 0, 0),
                       rot_box(-4.5, 16.5, -4.2, 9.0, 6.2, 1.4, 0, 17.0, -4.2, 28, 0, 0),
                       (-3.0, 29.8, -3.6, 6.0, 1.4, 1.4),
                       rot_box(-5.0, 25.0, -8.6, 5.2, 4.6, 0.6, -2.4, 27.0, -7.6, -26, 0, 7),
                       rot_box(1.2, 22.6, -8.0, 4.0, 3.6, 0.6, 3.0, 24.0, -7.0, -26, 0, -11),
                       rot_box(3.0, 14.5, -4.0, 1.4, 6.4, 4.2, 3.5, 18.0, -2.5, 0, 0, -12),
                       rot_box(-4.6, 14.2, -4.4, 1.6, 6.0, 4.0, -3.5, 18.0, -2.5, 0, 0, 20)])
    k.add(C, "hazard", [rot_box(1.4, 26.6, -8.6, 3.4, 3.0, 0.5, 3.0, 28.0, -7.4, -26, 0, -4)])
    k.add(C, "rubber", [rot_box(-4.6 + 1.9 * i, 14.6, -6.8, 1.7, 2.6, 0.6, 0, 16.0, -6.4, 18, 0, 0) for i in range(5)])
    k.add(C, "steel", [(-4.8, 17.3, -7.0, 9.6, 0.4, 0.4), (-5.2, 17.0, -6.9, 0.5, 1.0, 0.5), (4.7, 17.0, -6.9, 0.5, 1.0, 0.5)])
    k.add(C, "lamp", [(-4.6, 29.6, -6.2, 1.4, 1.4, 0.2)])
    k.add(C, "dark", [(-4.8, 29.4, -6.0, 1.8, 1.8, 1.2)])
    k.add(C, "paint", leg_fairing())

    # ---- canopy: corrugated roof, rebar grille, odd side walls, oil drum, bent exhaust ----
    roof, rear = 33.7, 9.47
    k.add(CN, "paint", [(-5.5, 19.5, rear, 11.0, roof + 1.0 - 19.5, 0.8),
                        (5.9, 19.5, -2.2, 0.8, roof - 19.5, rear + 2.2), (-6.7, 19.5, -2.2, 0.8, roof - 19.5, rear + 2.2),
                        (-3.0, 31.0, -3.6, 6.0, roof - 31.0, 1.2),
                        (2.8, 26.5, -3.6, 3.2, roof - 26.5, 1.2), (-6.0, 26.5, -3.6, 3.2, roof - 26.5, 1.2),
                        (-5.5, roof, -2.5, 11.0, 1.0, rear + 3.3),
                        rot_box(6.6, 22.0, -1.0, 0.6, 7.0, 6.0, 6.9, 25.0, 2.0, 0, 0, 6),
                        rot_box(-7.4, 25.0, 3.0, 0.7, 6.0, 7.4, -7.0, 28.0, 6.0, 0, 0, -9)])
    k.add(CN, "steel", [(-6.4 + 1.1 * i, roof + 1.0, -3.4, 0.6, 0.5, 14.2) for i in range(12)])          # corrugated sheet
    k.add(CN, "rust", [(-2.4 + 1.2 * i, 26.0, -4.4, 0.35, 5.0, 0.35) for i in range(5)] + [(-2.6, 28.4, -4.5, 5.2, 0.35, 0.35)])
    k.add(CN, "accent", [*disc_y(-2.0, 20.0, rear + 2.6, 1.8, 7.0)])
    k.add(CN, "dark", [(-3.9, 27.0, rear + 0.8, 0.4, 1.0, 3.6), (-0.1, 27.0, rear + 0.8, 0.4, 1.0, 3.6)])
    k.add(CN, "rust", [(3.4, 22.0, rear + 0.8, 1.0, 14.0, 1.0), (3.4, 36.0, rear + 0.8, 1.0, 1.0, 2.4), (3.3, 30.0, rear + 0.6, 1.2, 0.6, 1.2)])
    k.add(CN, "steel", [(-5.6, roof + 1.5, 8.0, 0.3, 7.0, 0.3), (-6.0, roof + 6.0, 8.1, 1.2, 0.2, 0.2)])

    # ---- shoulders: tyre on the left, road-sign slab on the right ----
    LSH, RSH = "armor_left_shoulder_salvage", "armor_right_shoulder_salvage"
    k.add(LSH, "paint", [(6.6, 33.2, -3.6, 5.6, 1.0, 6.8), (11.2, 27.0, -3.6, 1.0, 6.2, 6.8)])
    k.add(LSH, "rubber", [*disc_x(12.2, 30.0, -0.4, 3.4, 1.6)])
    k.add(LSH, "steel", [*disc_x(13.8, 30.0, -0.4, 1.6, 0.3)])
    k.add(LSH, "rust", [(12.0, 33.0, -0.8, 1.8, 1.4, 0.8)])
    k.add(RSH, "paint", [(-12.2, 33.0, -4.0, 5.6, 1.0, 7.4), rot_box(-13.4, 25.0, -4.6, 1.2, 8.6, 8.6, -12.8, 29.0, -0.3, 0, 0, 8)])
    k.add(RSH, "sign", [rot_box(-14.0, 26.0, -3.6, 0.6, 6.6, 6.6, -12.8, 29.0, -0.3, 45, 0, 8)])
    k.add(RSH, "steel", [(-13.0, 22.0, -0.6, 0.5, 4.0, 0.5)])

    # ---- legs: plates of different colours, wired-on, a track link on one knee ----
    for s, sg in (("left", 1), ("right", -1)):
        f = (lambda bs: bs) if sg > 0 else (lambda bs: [mx(v) for v in bs])
        k.add(f"armor_{s}_leg_salvage", "paint", f([rot_box(2.8, 10.4, -4.4, 3.6, 6.6, 0.8, 4.5, 14.0, -4.0, 0, 0, 5 * sg),
                                                    (6.3, 9.8 + sg, -3.0, 0.8, 6.8, 5.0), (2.8, 16.4, -3.4, 4.0, 1.0, 5.4)]))
        k.add(f"armor_{s}_leg_salvage", "steel", f([(2.6, 12.0 + 2.6 * j, -4.6, 4.0, 0.3, 0.3) for j in range(2)]))
        k.add(f"armor_{s}_shin_salvage", "paint", f([rot_box(2.6, 3.0, -5.6, 3.8, 6.8, 1.0, 4.5, 6.0, -5.2, -10, 0, 4 * sg),
                                                     (6.2, 2.8, -3.6, 0.8, 7.0 - sg, 6.0)]))
        k.add(f"armor_{s}_shin_salvage", "rubber", f([(2.8, 8.2, -6.6, 3.4, 2.2, 1.6)] if sg > 0 else [(3.0, 8.4, -6.2, 3.0, 2.0, 1.2)]))
        k.add(f"armor_{s}_shin_salvage", "rust", f([(3.4, 4.0, -6.0, 2.2, 0.4, 0.5)]))

    # ---- backpack: oil drum, spare tyre, crate, coiled pipe, jerry can ----
    add_bp = lambda m, bs: k.add(BP, m, back_fit(bs))     # authored against the legacy mount plane
    add_bp("paint", MOUNT[:1])
    add_bp("accent", [*disc_y(-2.0, 22.0, 9.8, 2.2, 8.0)])
    add_bp("rust", [(-4.2, 25.6, 7.6, 4.4, 0.4, 4.4), (-4.2, 29.6, 7.6, 4.4, 0.4, 4.4)])
    add_bp("rubber", [*disc_z(2.6, 27.6, 7.6, 2.8, 1.6)])
    add_bp("crate", [(0.6, 21.6, 7.6, 4.0, 3.6, 3.4)])
    add_bp("steel", [(-4.0, 30.4, 8.2, 8.0, 0.5, 0.5), (3.7, 30.4, 8.2, 0.5, 4.0, 0.5)])
    return k.out


SCRAP = [(112, 74, 50), (78, 96, 108), (96, 104, 76), (120, 116, 104), (140, 96, 52)]


def set_colour(mat, ci, camo, x, y, nm, nc):
    if mat == "hazard":
        return (238, 188, 18) if (x + y) // 3 % 2 == 0 else (24, 24, 26)
    if mat == "sign":                         # faded red road sign with a white bar
        return (230, 226, 216) if 7 <= y % 12 <= 9 or camo else (168, 40, 34)
    if mat == "crate":
        return (122, 96, 62) if x % 5 else (80, 62, 40)
    if mat == "accent":                       # oil drum: blue with a white band
        return (230, 226, 216) if y % 9 == 0 else (52, 84, 120) if camo == 0 else _camo(camo, x, y, nm, nc, (52, 84, 120))
    base = SCRAP[int(_h(ci, 7, 2) * len(SCRAP))]
    return base if camo == 0 else _mix(_camo(camo, x, y, nm, nc, base), base, 0.3)


def stencil(mat, ci, face, lx, ly, fw, fh):
    if fw < 9 or fh < 7:
        return None
    if mat == "paint" and ci % 3 == 0 and _digits("6", lx, ly, 2, 2):
        return (232, 228, 214)
    if mat == "paint" and ci % 3 == 1 and abs(lx - ly) <= 0 and lx < 7:   # crude painted slash
        return (210, 40, 30)
    return None
