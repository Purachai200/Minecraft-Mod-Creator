"""Procedural armour painter for gen_exo_frame_titan: 9 palettes, 8 armour archetype tints, per-face panel shading."""
import numpy as np

PALETTES = [  # P primary, S secondary, A accent
    dict(P=(104, 116, 84), S=(70, 78, 62), A=(176, 150, 70)),     # 0 field olive drab
    dict(P=(38, 86, 164), S=(24, 52, 108), A=(218, 174, 62)),    # 1 royal blue
    dict(P=(92, 96, 102), S=(54, 57, 62), A=(228, 130, 34)),     # 2 gunmetal / orange
    dict(P=(152, 30, 36), S=(90, 20, 24), A=(34, 34, 38)),       # 3 crimson / black
    dict(P=(208, 214, 222), S=(150, 162, 178), A=(42, 86, 152)), # 4 arctic white
    dict(P=(152, 122, 82), S=(106, 82, 54), A=(62, 50, 36)),     # 5 desert tan
    dict(P=(38, 40, 46), S=(24, 25, 30), A=(62, 204, 214)),      # 6 stealth black / cyan
    dict(P=(214, 178, 42), S=(152, 122, 26), A=(32, 32, 34)),    # 7 solar yellow
    dict(P=(64, 100, 62), S=(42, 68, 42), A=(172, 152, 82)),     # 8 forest green
]
FIXED = dict(J=(70, 75, 88), M=(150, 156, 166), H=(205, 210, 218), T=(50, 52, 56), V=(30, 32, 38),
             R=(214, 20, 36), E=(255, 150, 40), L=(190, 225, 255), G=(255, 235, 200), C=(205, 170, 64))
ARCH = {  # (mix colour, amount) applied to P and S; accent override
    "infantry": (None, 0, None), "siege": ((70, 74, 60), .30, None), "samurai": ((160, 28, 28), .55, (230, 200, 90)),
    "aero": ((235, 240, 248), .45, None), "scrap": ((124, 84, 52), .55, (190, 120, 40)),
    "stealth": ((8, 8, 12), .65, (60, 210, 220)), "sovereign": ((236, 236, 240), .35, (232, 188, 64)),
    "expedition": ((90, 100, 60), .35, (236, 140, 30)),
}
SHADE = dict(up=1.14, north=1.0, south=.9, east=.95, west=.95, down=.7)


def mix(a, b, t): return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def role_color(mat, pal, arch):
    if mat in ("P", "S", "A"):
        c = pal[mat]
        if arch:
            tint, amt, acc = ARCH[arch]
            if mat == "A" and acc: return acc
            if tint and mat != "A": c = mix(c, tint, amt)
        return c
    return FIXED[mat]


def paint_face(rng, w, h, mat, pal, arch, face, seed):
    base = np.array(role_color(mat, pal, arch), float)
    a = np.empty((h, w, 3)); a[:] = base
    glow = mat in ("R", "E", "L", "G")
    sh = 1.0 if glow else SHADE[face]
    a *= sh
    if not glow:
        yy, xx = np.mgrid[0:h, 0:w]
        a *= (1.10 - 0.20 * (0.6 * yy / max(h - 1, 1) + 0.4 * xx / max(w - 1, 1)))[..., None]       # light falloff
        if mat in ("P", "S") and w >= 6 and h >= 6:                                                   # camo / tone blotches
            coarse = rng.random((h // 3 + 1, w // 3 + 1))
            a *= (0.93 + 0.14 * np.kron(coarse, np.ones((3, 3)))[:h, :w])[..., None]
        a += rng.normal(0, 1.8 if mat not in ("M", "H") else 4, (h, w, 1))
        a *= rng.uniform(0.96, 1.04)                                                                  # per-plate tone shift
    if mat == "V":
        for y in range(1, h, 2): a[y, :] = np.array((120, 124, 134)) * (0.9 + 0.1 * (y % 4 == 1))
    elif mat == "T":
        for x in range(0, w, 2): a[:, x] *= 1.5
    elif mat in ("M", "H"):
        a *= (0.92 + 0.08 * ((np.arange(w) % 3) == 0))[None, :, None]
    elif glow:
        cx, cy = (w - 1) / 2, (h - 1) / 2
        d = np.sqrt(((np.arange(w) - cx) / max(cx, 1)) ** 2 + (((np.arange(h) - cy) / max(cy, 1)) ** 2)[:, None])
        a = np.clip(base * (1.25 - 0.55 * d[..., None]), 0, 255)
        if mat == "R" and w >= 3: a[h // 2, w // 2] = (255, 190, 190)
    elif mat == "C" and w >= 5 and h >= 5:
        a[h // 2, 1:-1] = (96, 40, 120); a[1:-1, w // 2] = (96, 40, 120)
    if not glow and w >= 3 and h >= 3:
        a[0, :] *= 0.55; a[-1, :] *= 0.55; a[:, 0] *= 0.55; a[:, -1] *= 0.55
        if w >= 4 and h >= 4:
            a[1, 1:-1] = np.minimum(a[1, 1:-1] * 1.28 + 8, 255); a[1:-1, 1] = np.minimum(a[1:-1, 1] * 1.18 + 5, 255)
            a[-2, 1:-1] *= 0.82; a[1:-1, -2] *= 0.86
        if mat in ("P", "S", "A") and w >= 9 and h >= 9:
            step = 3 if arch == "siege" else 5
            a[3, 3:-3] *= .7; a[-4, 3:-3] *= .7; a[3:-3, 3] *= .7; a[3:-3, -4] *= .7
            for rx in range(2, w - 2, step): a[2, rx] = np.minimum(a[2, rx] * 1.4 + 14, 255)
            for ry in range(2, h - 2, step): a[ry, 2] = np.minimum(a[ry, 2] * 1.4 + 14, 255)
            if h >= 12: a[h // 2, 4:-4] *= .8                                                         # mid panel seam
        if mat in ("P", "S") and w * h > 36:
            for _ in range(int(w * h * (0.03 if arch == "scrap" else 0.012)) + 1):                    # paint chips on edges
                y = int(rng.choice((1, h - 2, rng.integers(0, h)))); x = int(rng.choice((1, w - 2, rng.integers(0, w))))
                a[y, x] = (150, 154, 160)
            for _ in range(max(1, w // 6)):                                                           # grime streaks
                x = rng.integers(1, max(2, w - 1)); l = rng.integers(2, max(3, h // 2 + 1))
                a[h - l:, x] *= 0.82
            if arch == "scrap":
                for _ in range(max(2, w * h // 40)): a[rng.integers(1, h), rng.integers(1, w)] = (150, 82, 38)   # rust
            elif arch == "stealth" and w >= 4:
                a[(np.add.outer(np.arange(h), np.arange(w)) % 4) == 0] *= 0.84                         # carbon weave
                a[(np.add.outer(np.arange(h), np.arange(w)) % 4) == 2] *= 1.08
            elif arch == "samurai" and h >= 5: a[2, 1:-1] = (222, 190, 90)                             # lacquer gold edge
            elif arch == "sovereign" and h >= 5: a[2, 1:-1] = (232, 188, 64); a[-3, 1:-1] = (232, 188, 64)
            elif arch == "aero" and h >= 7: a[h // 2, 1:-1] = (60, 110, 190)                           # thin livery line
            elif arch == "expedition" and w >= 8 and h >= 8:
                a[2:4, 2:6] = (236, 140, 30)                                                           # stencil tab
    return np.clip(a, 0, 255).astype(np.uint8)


def paint_all(model, pal, seed=1):
    from PIL import Image
    T = model.tex
    img = np.zeros((T, T, 4), np.uint8)
    rng = np.random.default_rng(seed)
    for bn, ci, f, x, y, rw, rh in model.rects:
        c = model.bones[bn]["cubes"][ci]
        tile = paint_face(rng, rw, rh, c["mat"], pal, c.get("arch"), f, seed)
        img[y:y + rh, x:x + rw, :3] = tile; img[y:y + rh, x:x + rw, 3] = 255
    return Image.fromarray(img, "RGBA")
