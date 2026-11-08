#!/usr/bin/env python3
"""Knightmare Frame (RPI-13 Sutherland style) rebuild for the exo_frame titan: geo + 9 skins + preview.
Keeps the original GeckoLib skeleton (names, parents, pivots, rest rotations) so every existing animation still plays;
only the cubes are new. Cubes are designed in world rest-pose coordinates / limb frames (see mgen.py).
Run: python scripts/gen_exo_frame_titan.py [--preview out.png]"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from mgen import *
from mgen import poly, hexp
from mgen import hexp
import exo_paint

GEO = os.path.join(O.ROOT, "geo", "exo_frame_titan.geo.json")
TEXDIR = os.path.join(O.ROOT, "textures", "entity", "titan", "exo_frame")
ARCHS = ["infantry", "siege", "samurai", "aero", "scrap", "stealth", "sovereign", "expedition"]
R_ = "right"


def base(m):
    """Mass-production heavy-infantry walker: domed cockpit torso, huge rounded shoulder pods, slab thighs/shins with round
    knee discs, blocky feet. Dark exposed frame under thin cover plates, amber hardpoint rails for add-ons."""
    pv = lambda n: pivot_world(m, n)
    H = lambda bone, c, size, mat, ch, axis, org_rel=(0, 0, 0): hexp(m, bone, c, 0, 0, 0, size, mat, ch, axis, None, False)
    # ---------------------------------------------------------------- pelvis (body1)
    m.cube("body1", (0, 58, 7.5), (18, 8, 14), "J")
    m.cube("body1", (0, 63.4, 7.5), (20, 2.2, 16), "A")
    poly(m, "body1", (0, 57.2, -0.8), 0, 0, 0, (14, 10, 3), "P", "z", "pent", False)
    m.cube("body1", (0, 58.4, 16), (14, 8, 2.6), "S")
    for sx in (-1, 1):
        hexp(m, "body1", (sx * 11.6, 59, 7.5), 0, 0, 0, (4.4, 10, 12), "P", 3, "x", None, False)
        m.cube("body1", (sx * 14.2, 59, 7.5), (1, 6, 8), "A")
    # ---------------------------------------------------------------- waist (body2)
    m.cube("body2", (0, 70.5, 8.2), (8.4, 14, 7.6), "J")
    m.cube("body2", (0, 66, 8.2), (11, 2.4, 10), "S")
    m.cube("body2", (0, 75, 8.2), (11, 2.4, 10), "S")
    sym(m, "body2", (6, 70, 4), (2.8, 12, 2.8), "M")
    sym(m, "body2", (6, 76.5, 4), (1.5, 6, 1.5), "H")
    # ---------------------------------------------------------------- chest (body3): domed cockpit
    m.cube("body3", (0, 86, 5), (22, 16, 16), "J")
    m.cube("body3", (0, 81.4, 5), (16, 4, 13), "S")
    hexp(m, "body3", (0, 91.4, 4.6), 0, 0, 0, (30, 8, 23), "P", 6, "y", None, False)
    hexp(m, "body3", (0, 98.4, 4.4), 0, 0, 0, (28, 7, 21), "P", 6.4, "y", None, False)
    hexp(m, "body3", (0, 103.6, 4), 0, 0, 0, (20, 3.4, 15), "S", 4.4, "y", None, False)
    for sx in (-1, 1):
        poly(m, "body3", (sx * 8, 93, -6.2), 0, 0, 0, (12, 13, 3), "P", "z", "pent", False)      # faceted front plates
        m.cube("body3", (sx * 5.2, 86.6, -3.6), (5.6, 5, 2.4), "J")                              # Slash Harken ports
        m.cube("body3", (sx * 5.2, 86.6, -4.9), (3.8, 3.2, 0.8), "V")
        m.cube("body3", (sx * 5.2, 86.6, -5.6), (2.2, 2.2, 1.4), "H")
        m.cube("body3", (sx * 5.2, 89.8, -3.8), (1.3, 1.3, 0.8), "R")
        m.cube("body3", (sx * 17, 96.6, 8.6), (9, 12, 12), "J")                                   # shoulder mounts
        m.cube("body3", (sx * 17, 102.8, 8.6), (6, 1.2, 10), "A")
        hexp(m, "body3", (sx * 27.2, 99.6, 10.7), 0, 0, 0, (10, 16, 19), "P", 5.6, "x", None, False)   # huge rounded shoulder pods
        hexp(m, "body3", (sx * 27.2, 108.2, 10.7), 0, 0, 0, (7, 3, 13), "S", 2.2, "x", None, False)
        m.cube("body3", (sx * 32.4, 99.6, 10.7), (0.8, 9, 9), "A")
    m.cube("body3", (0, 97, -5.6), (3.4, 6, 1.2), "C")
    m.cube("body3", (0, 92, 12.8), (16, 12, 2.4), "S")                                         # back plate (jet pack seats here)
    m.cube("body3", (0, 91.6, 17), (10, 14, 6.6), "P")                                         # dorsal pod
    m.cube("body3", (0, 100, 16.8), (7.4, 2.4, 5.6), "S")
    m.cube("body3", (0, 92, 20.6), (7, 9.5, 0.8), "A")
    m.cube("body3", (0, 97, 20.8), (5.4, 3.2, 0.8), "L")
    sym(m, "body3", (4, 84, 18.6), (3.6, 3.6, 6), "J")
    sym(m, "body3", (4, 84, 22.2), (4.6, 4.6, 1.4), "M")
    sym(m, "body3", (4, 84, 23.1), (2.8, 2.8, 0.6), "E")
    m.cube("doorDown", (0, 82.4, -3.4), (12, 4, 2.2), "S")
    m.cube("weaponBack", (-22.2, 80, 26.5), (4, 10, 5.5), "S")
    m.cube("weaponBack", (-22.2, 92, 26.5), (2, 14, 2.2), "M")
    m.cube("weaponBack", (-22.2, 70.5, 26.5), (3.4, 9, 4.5), "J")
    # ---------------------------------------------------------------- head: small sensor head sunk between the shoulders
    m.cube("doorUp", (0, 102.4, -3), (6, 5, 6), "J")
    hexp(m, "doorUp", (0, 108.4, -2.4), 0, 0, 0, (10, 7.6, 11), "P", 3, "y", None, False)
    hexp(m, "doorUp", (0, 113.6, -2.2), 0, 0, 0, (8, 3.6, 8.6), "S", 2.4, "y", None, False)
    m.cube("doorUp", (0, 109.6, -8), (8.4, 3.4, 1), "J")                                       # visor recess
    m.cube("eye", (0, 109.6, -8.8), (7.2, 1.8, 1), "R")                                        # twin-slit sensor
    m.cube("eye", (0, 109.6, -9.4), (2.2, 1.2, 0.5), "G")
    m.cube("doorUp", (0, 105.4, -7), (5, 2.6, 2), "V")
    sym(m, "doorUp", (3.6, 118.4, 1), (0.9, 8, 0.9), "M")                                      # whip antennas
    # ---------------------------------------------------------------- arms (limb frames, 30 deg splay)
    sh, el, hd = "rightArm1", "rightArm2", "rightHand"
    lpair(m, sh, "self", 0, -0.8, 0, (9.4, 9.4, 9.4), "J")
    lpair(m, sh, (sh, el), 0, 0, 0, (8.4, 23, 8.6), "J")
    hexp(m, sh, (sh, el), 5.4, 0.5, 0, (3.2, 19, 10.4), "P", 3.4, "x")
    hexp(m, sh, el, 5.4, 0, 0, (4, 9.4, 9.4), "S", 3, "x")                                       # round elbow disc
    lpair(m, el, (el, hd), 0, 0, 0, (8.4, 26, 8.6), "J")
    hexp(m, el, (el, hd), 0.4, 1.6, 0, (11, 21, 11.6), "P", 3, "y")                            # armoured forearm block
    lpair(m, el, (el, hd), 6.4, 6, 0, (1, 9, 3), "A")                                            # hardpoint rail
    lpair(m, el, (el, hd), 0, 4, -6.2, (7, 8, 1.4), "S")
    lpair(m, el, hd, 0, 1.2, 0, (6.4, 3.4, 7), "J")
    lpair(m, hd, "self", 0, -4.2, 0, (8, 9, 8.6), "S")
    lpair(m, hd, "self", 0, -10.4, -0.2, (7.6, 5, 8.2), "J")
    for dz in (-3, -1, 1, 3): lpair(m, hd, "self", 0, -13.6, dz, (1.7, 3.4, 1.7), "M")
    lpair(m, hd, "self", 3.4, -6, -4, (2.2, 5, 2.2), "M")
    # ---------------------------------------------------------------- legs
    L3, L2, L1, FT = "rightLeg3", "rightLeg2", "rightLeg1", "rightFoot"
    hexp(m, L3, "self", 0, -0.5, 0, (10, 10, 10), "J", 3, "x")
    lpair(m, L3, (L3, L2), 0, 0, 0, (9, 17, 10), "J")
    hexp(m, L3, (L3, L2), 6.6, 1, 0, (3.4, 18, 12.6), "P", 4, "x")                              # slab thigh plate
    poly(m, L3, (L3, L2), 0, 2, -6.4, (10, 14, 3), "P", "z", "pent")
    lpair(m, L3, (L3, L2), 0, 0, 6.4, (4, 12, 3), "M")
    lpair(m, L3, (L3, L2), 0, -6.4, 6.4, (2, 5, 2), "H")
    hexp(m, L3, L2, 7.8, 0.4, 0, (4.4, 11, 11), "S", 3.8, "x")                                  # round knee disc
    hexp(m, L3, L2, 0, 1.2, -5.4, (8.6, 8.6, 3.6), "P", 2.8, "z")
    lpair(m, L3, L2, 0, 0.4, 0, (8, 7, 8), "J")
    lpair(m, L2, (L2, L1), 0, 0, 0.2, (8.4, 22, 9.2), "J")
    poly(m, L2, (L2, L1), 0, 1, -5.6, (9.4, 17, 3), "P", "z", "pent")
    hexp(m, L2, (L2, L1), 6.2, 1, 0.5, (3.2, 18, 11), "P", 4, "x")
    lpair(m, L2, (L2, L1), 0, 1.5, 5.4, (7.6, 11, 3.6), "S")
    lpair(m, L2, L1, 0, 0.5, 0, (7.4, 6, 7.6), "J")
    lpair(m, L1, (L1, FT), 0, 0, 0, (7, 17, 7.6), "S")
    lpair(m, L1, (L1, FT), 0, 1.5, -4.6, (6, 9, 1.8), "P")
    for sx in (1, -1):                                                                          # blocky feet, three toes
        f = "rightFoot" if sx < 0 else "leftFoot"; X = sx * 14.8
        m.cube(f, (X, 9.8, 2.4), (7.4, 5, 7.6), "J")
        m.cube(f, (X, 4, 9.6), (10, 7.4, 9), "P")
        m.cube(f, (X, 3.6, 1.4), (10.4, 6.6, 9), "P")
        for t in (-1, 0, 1):
            m.cube(f, (X + t * 3.4, 2.2, -6), (3, 4.4, 8), "P")
            m.cube(f, (X + t * 3.4, 1.1, -10.6), (2.6, 2.2, 2.8), "M", rot=[-18, 0, 0])
        m.cube(f, (X, 0.8, 4.6), (10.8, 1.6, 21), "J")


def build_model():
    src = json.load(open(GEO))["minecraft:geometry"][0]["bones"]
    src = [b for b in src if not b["name"].startswith("armor_")]
    m = Model(src, 1024)
    base(m)
    import exo_armor
    exo_armor.armor(m, ARCHS)
    return m


def main():
    m = build_model()
    used = m.uv_pack()
    ncubes = sum(len(b["cubes"]) for b in m.bones.values())
    geo = m.to_json("geometry.exo_frame_titan", dict(visible_bounds_width=5.0, visible_bounds_height=6.5, visible_bounds_offset=[0, 3.0, 0]))
    os.makedirs(TEXDIR, exist_ok=True)
    json.dump(geo, open(GEO, "w"), indent=1)
    for i, pal in enumerate(exo_paint.PALETTES):
        img = exo_paint.paint_all(m, pal, seed=7)
        img.save(os.path.join(TEXDIR, "exo_frame_titan.png" if i == 0 else f"exo_frame_titan_{i}.png"))
    print(f"cubes={ncubes} atlas rows used={used}/1024")
    if "--preview" in sys.argv:
        a = sys.argv[sys.argv.index("--armor") + 1] if "--armor" in sys.argv else None
        pal = int(sys.argv[sys.argv.index("--pal") + 1]) if "--pal" in sys.argv else 0
        preview(m, sys.argv[sys.argv.index("--preview") + 1], a, pal)


def preview(m, out, arch=None, pal=0, views=((35, -12), (180, -8), (90, -6), (0, 0))):
    O.TEX = m.tex
    img = exo_paint.paint_all(m, exo_paint.PALETTES[pal], seed=7)
    tex = [[tuple(int(v) for v in p) for p in row] for row in np.array(img)]
    bones = [b for b in m.render_bones() if not b["name"].startswith("armor_") or (arch and b["name"].endswith("_" + arch))]
    rows = None
    for yaw, pitch in views:
        pose = {b['name']: b['rotation'] for b in bones if 'rotation' in b}
        r = O.render(bones, tex, pose, yaw, pitch, W=400, H=480, scale=2.6)
        rows = r if rows is None else [a + b for a, b in zip(rows, r)]
    O.save_png(out, rows)


if __name__ == "__main__":
    main()
