#!/usr/bin/env python3
"""
Generates the cockpit HUD / cockpit-bay GUI textures for Titan Combat.

Pure standard library (zlib + struct), no PIL required.
Run from the project root:   python3 tools/generate_hud_textures.py

Outputs (src/main/resources/assets/titancombat/textures/gui/):
  hud_reticles.png  256x256  4x4 grid of 64x64 white reticle cells (tinted at runtime)
  hud_radar.png     256x128  [0..128) radar line-work (tinted), [128..256) dark radar glass
  hud_vignette.png  128x128  white edge vignette (tinted red / cyan at runtime)
  titan_bay.png     512x256  cockpit bay panel chassis (300x222 used)
"""
import math
import os
import struct
import zlib

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "src", "main", "resources", "assets", "titancombat", "textures", "gui")


def write_png(path, w, h, px):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        row = px[y]
        for x in range(w):
            r, g, b, a = row[x]
            raw.extend((max(0, min(255, int(round(r)))), max(0, min(255, int(round(g)))),
                        max(0, min(255, int(round(b)))), max(0, min(255, int(round(a))))))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        f.write(chunk(b"IEND", b""))
    print("wrote", os.path.relpath(path))


def blank(w, h):
    return [[(0, 0, 0, 0) for _ in range(w)] for _ in range(h)]


def over(dst, src):
    """Porter-Duff source-over, straight alpha, 0..255 channels."""
    sr, sg, sb, sa = src
    dr, dg, db, da = dst
    sa /= 255.0
    da /= 255.0
    oa = sa + da * (1 - sa)
    if oa <= 0:
        return (0, 0, 0, 0)
    r = (sr * sa + dr * da * (1 - sa)) / oa
    g = (sg * sa + dg * da * (1 - sa)) / oa
    b = (sb * sa + db * da * (1 - sa)) / oa
    return (r, g, b, oa * 255)


# ---------------------------------------------------------------- SDF helpers
def d_seg(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    l2 = vx * vx + vy * vy
    t = 0.0 if l2 == 0 else max(0.0, min(1.0, (wx * vx + wy * vy) / l2))
    dx, dy = px - (ax + t * vx), py - (ay + t * vy)
    return math.hypot(dx, dy)


def d_ring(px, py, r):
    return abs(math.hypot(px, py) - r)


def d_arc(px, py, r, a0, a1):
    """Arc of radius r between angles a0..a1 (degrees, 0 = +x, counter-clockwise, y down => screen)."""
    ang = math.degrees(math.atan2(py, px))
    a = (ang - a0) % 360.0
    span = (a1 - a0) % 360.0
    if a <= span:
        return abs(math.hypot(px, py) - r)
    e0 = (r * math.cos(math.radians(a0)), r * math.sin(math.radians(a0)))
    e1 = (r * math.cos(math.radians(a1)), r * math.sin(math.radians(a1)))
    return min(math.hypot(px - e0[0], py - e0[1]), math.hypot(px - e1[0], py - e1[1]))


def d_dot(px, py, r):
    return max(0.0, math.hypot(px, py) - r)


def cov(d, hw):
    return max(0.0, min(1.0, hw + 0.5 - d))


# ---------------------------------------------------------------- reticles
def reticle_shapes(idx):
    """returns (list of distance functions, half width)"""
    S = []
    hw = 1.0
    if idx == 0:  # ION splitter: split brackets + horizontal split ticks
        for sx in (-1, 1):
            x = 15 * sx
            S.append(lambda p, q, x=x: d_seg(p, q, x, -8, x, 8))
            S.append(lambda p, q, x=x, sx=sx: d_seg(p, q, x, -8, x - 4 * sx, -8))
            S.append(lambda p, q, x=x, sx=sx: d_seg(p, q, x, 8, x - 4 * sx, 8))
            S.append(lambda p, q, sx=sx: d_seg(p, q, 5 * sx, 0, 9 * sx, 0))
        S.append(lambda p, q: d_dot(p, q, 1.2))
    elif idx == 1:  # SCORCH launcher: arc marker + drop ladder
        S.append(lambda p, q: d_arc(p, q, 12, 200, 340))
        S.append(lambda p, q: d_seg(p, q, -6, 7, 6, 7))
        S.append(lambda p, q: d_seg(p, q, -4, 13, 4, 13))
        S.append(lambda p, q: d_seg(p, q, -2, 19, 2, 19))
        S.append(lambda p, q: d_seg(p, q, 0, 2, 0, 22))
        S.append(lambda p, q: d_dot(p, q, 1.6))
    elif idx == 2:  # RONIN shotgun spread arcs
        S.append(lambda p, q: d_arc(p, q, 18, 145, 215))
        S.append(lambda p, q: d_arc(p, q, 18, 325, 35))
        S.append(lambda p, q: d_seg(p, q, 0, -14, 0, -10))
        S.append(lambda p, q: d_seg(p, q, 0, 10, 0, 14))
        S.append(lambda p, q: d_dot(p, q, 1.2))
    elif idx == 3:  # TONE lock diamond (broken corners)
        r = 11
        pts = [(0, -r), (r, 0), (0, r), (-r, 0)]
        for i in range(4):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % 4]
            # leave the corners open: draw middle 70% of each edge
            mx0, my0 = ax + (bx - ax) * 0.18, ay + (by - ay) * 0.18
            mx1, my1 = ax + (bx - ax) * 0.82, ay + (by - ay) * 0.82
            S.append(lambda p, q, a=(mx0, my0, mx1, my1): d_seg(p, q, *a))
        S.append(lambda p, q: d_dot(p, q, 1.3))
    elif idx == 4:  # LEGION wide circle with inward ticks
        S.append(lambda p, q: d_ring(p, q, 24))
        for a in (0, 90, 180, 270):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            S.append(lambda p, q, ca=ca, sa=sa: d_seg(p, q, 24 * ca, 24 * sa, 18 * ca, 18 * sa))
        S.append(lambda p, q: d_dot(p, q, 1.4))
        hw = 0.8
    elif idx == 5:  # MONARCH chaingun ticks
        for a in (0, 90, 180, 270):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            S.append(lambda p, q, ca=ca, sa=sa: d_seg(p, q, 7 * ca, 7 * sa, 14 * ca, 14 * sa))
        for a in (45, 135, 225, 315):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            S.append(lambda p, q, ca=ca, sa=sa: d_seg(p, q, 12 * ca, 12 * sa, 15 * ca, 15 * sa))
        S.append(lambda p, q: d_dot(p, q, 1.2))
    elif idx == 6:  # NORTHSTAR fine sniper cross + mil dots
        S.append(lambda p, q: d_seg(p, q, -30, 0, -5, 0))
        S.append(lambda p, q: d_seg(p, q, 5, 0, 30, 0))
        S.append(lambda p, q: d_seg(p, q, 0, -30, 0, -5))
        S.append(lambda p, q: d_seg(p, q, 0, 5, 0, 30))
        for k in (10, 16, 22):
            S.append(lambda p, q, k=k: d_seg(p, q, -2, k, 2, k))
            S.append(lambda p, q, k=k: d_seg(p, q, k, -2, k, 2))
            S.append(lambda p, q, k=k: d_seg(p, q, -k, -2, -k, 2))
        S.append(lambda p, q: d_dot(p, q, 0.8))
        hw = 0.6
    elif idx == 7:  # generic (Aegis striker)
        S.append(lambda p, q: d_ring(p, q, 9))
        S.append(lambda p, q: d_dot(p, q, 1.2))
    elif idx == 8:  # hit marker X
        for a in (45, 135, 225, 315):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            S.append(lambda p, q, ca=ca, sa=sa: d_seg(p, q, 7 * ca, 7 * sa, 14 * ca, 14 * sa))
        hw = 1.2
    elif idx == 9:  # target lock corner brackets
        r = 22
        L = 7
        for sx in (-1, 1):
            for sy in (-1, 1):
                S.append(lambda p, q, sx=sx, sy=sy: d_seg(p, q, sx * r, sy * r, sx * (r - L), sy * r))
                S.append(lambda p, q, sx=sx, sy=sy: d_seg(p, q, sx * r, sy * r, sx * r, sy * (r - L)))
        hw = 0.9
    elif idx == 10:  # core ring (for ready pulse)
        S.append(lambda p, q: d_ring(p, q, 28))
        hw = 1.4
    return S, hw


def gen_reticles():
    W = H = 256
    px = blank(W, H)
    for idx in range(16):
        shapes, hw = reticle_shapes(idx)
        if not shapes:
            continue
        cx0, cy0 = (idx % 4) * 64, (idx // 4) * 64
        for y in range(64):
            for x in range(64):
                p, q = x + 0.5 - 32, y + 0.5 - 32
                d = min(f(p, q) for f in shapes)
                halo = cov(d, hw + 1.2) * 0.42
                core = cov(d, hw)
                col = (0, 0, 0, 0)
                if halo > 0:
                    col = over(col, (0, 0, 0, halo * 255))
                if core > 0:
                    col = over(col, (255, 255, 255, core * 255))
                px[cy0 + y][cx0 + x] = col
    write_png(os.path.join(OUT, "hud_reticles.png"), W, H, px)


# ---------------------------------------------------------------- radar
def gen_radar():
    W, H = 256, 128
    px = blank(W, H)
    c = 64.0
    R = 61.0
    for y in range(128):
        for x in range(128):
            p, q = x + 0.5 - c, y + 0.5 - c
            r = math.hypot(p, q)
            # ---- line work (left half), white, tinted at runtime
            a = 0.0
            a = max(a, cov(abs(r - R), 0.9) * 0.95)             # outer ring
            a = max(a, cov(abs(r - R * 0.5), 0.5) * 0.35)       # half range ring
            if r < R:
                a = max(a, cov(abs(p), 0.4) * 0.16)             # cross hair
                a = max(a, cov(abs(q), 0.4) * 0.16)
                ang = math.degrees(math.atan2(p, -q))            # 0 = up
                # forward view cone (+-35 deg)
                if abs(ang) <= 35:
                    a = max(a, 0.10 + 0.10 * (1 - r / R))
                for edge in (-35, 35):
                    ex, ey = math.sin(math.radians(edge)), -math.cos(math.radians(edge))
                    a = max(a, cov(d_seg(p, q, 0, 0, ex * R, ey * R), 0.4) * 0.30)
                a = max(a, 0.05)                                 # glass tint
            # outer tick marks every 30 degrees
            ang = (math.degrees(math.atan2(p, -q)) + 360) % 360
            near = min(ang % 30, 30 - ang % 30)
            if R - 6 <= r <= R and near * math.pi / 180 * r < 0.9:
                a = max(a, 0.85)
            if a > 0:
                px[y][x] = (255, 255, 255, a * 255)
            # ---- dark glass backdrop (right half)
            da = 0.0
            if r < R + 1.5:
                da = 0.42 * min(1.0, (R + 1.5 - r))
                da *= 0.75 + 0.25 * (r / R)
            px[y][128 + x] = (4, 10, 16, da * 255)
    write_png(os.path.join(OUT, "hud_radar.png"), W, H, px)


# ---------------------------------------------------------------- vignette
def gen_vignette():
    W = H = 128
    px = blank(W, H)
    for y in range(H):
        for x in range(W):
            u = (x + 0.5) / W * 2 - 1
            v = (y + 0.5) / H * 2 - 1
            d = math.sqrt((u * u) * 0.85 + (v * v))
            t = max(0.0, min(1.0, (d - 0.55) / 0.75))
            t = t * t * (3 - 2 * t)
            px[y][x] = (255, 255, 255, t * 255)
    write_png(os.path.join(OUT, "hud_vignette.png"), W, H, px)


# ---------------------------------------------------------------- cockpit bay panel
BAY_W, BAY_H = 300, 222


def chamfer_inside(x, y, w, h, tl, tr, br, bl):
    if x < 0 or y < 0 or x >= w or y >= h:
        return False
    if x + y < tl:
        return False
    if (w - 1 - x) + y < tr:
        return False
    if (w - 1 - x) + (h - 1 - y) < br:
        return False
    if x + (h - 1 - y) < bl:
        return False
    return True


def gen_bay():
    W, H = 512, 256
    px = blank(W, H)
    cham = (10, 4, 10, 4)

    def inside(x, y):
        return chamfer_inside(x, y, BAY_W, BAY_H, *cham)

    def edge(x, y):
        if not inside(x, y):
            return False
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            if not inside(x + dx, y + dy):
                return True
        return False

    for y in range(BAY_H):
        for x in range(BAY_W):
            if not inside(x, y):
                continue
            t = y / BAY_H
            base = (12 - 4 * t, 18 - 6 * t, 26 - 8 * t)
            # faint diagonal hatch
            if (x + y) % 6 == 0:
                base = (base[0] + 2, base[1] + 3, base[2] + 4)
            # micro grid every 16
            if x % 16 == 0 or y % 16 == 0:
                base = (base[0] + 1, base[1] + 2, base[2] + 3)
            col = (base[0], base[1], base[2], 246)
            # header strip
            if y < 18:
                col = (18 + y * 0.2, 28 + y * 0.3, 40 + y * 0.4, 250)
            if y == 18:
                col = (0, 160, 190, 255) if x < 120 else (30, 60, 72, 255)
            # second bevel line inside the border
            if edge(x, y):
                col = (60, 120, 138, 255)
            elif any(edge(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                col = (6, 10, 14, 255)
            px[y][x] = col

    # bright accent segments on border (top-left and bottom-right chamfers)
    for y in range(BAY_H):
        for x in range(BAY_W):
            if not edge(x, y):
                continue
            if (x + y < 60) or ((BAY_W - 1 - x) + (BAY_H - 1 - y) < 60):
                px[y][x] = (0, 229, 255, 255)

    # divider above pilot inventory
    for x in range(10, BAY_W - 10):
        px[128][x] = (30, 60, 72, 255) if x > 70 else (0, 160, 190, 255)

    # 3D preview viewport recess (7..79 x 21..124)
    vx0, vy0, vx1, vy1 = 7, 21, 79, 124
    for y in range(vy0, vy1 + 1):
        for x in range(vx0, vx1 + 1):
            border = x in (vx0, vx1) or y in (vy0, vy1)
            if border:
                px[y][x] = (30, 70, 84, 255)
                continue
            # radial-ish dark glass with cyan grid & floor glow
            cx = (x - (vx0 + vx1) / 2) / ((vx1 - vx0) / 2)
            cy = (y - vy0) / (vy1 - vy0)
            g = 4 + 10 * max(0.0, 1 - abs(cx)) * cy
            col = (3, 7 + g * 0.6, 11 + g, 255)
            if (x - vx0) % 8 == 0 or (y - vy0) % 8 == 0:
                col = (col[0] + 4, col[1] + 14, col[2] + 18, 255)
            # floor ellipse highlight
            fx = (x - (vx0 + vx1) / 2) / 26.0
            fy = (y - 117) / 4.0
            fr = fx * fx + fy * fy
            if abs(fr - 1.0) < 0.12:
                col = (0, 150, 175, 255)
            elif fr < 1.0:
                col = (col[0] + 2, col[1] + 14, col[2] + 18, 255)
            px[y][x] = col
    # viewport corner brackets
    for (cx, cy, sx, sy) in ((vx0, vy0, 1, 1), (vx1, vy0, -1, 1), (vx0, vy1, 1, -1), (vx1, vy1, -1, -1)):
        for k in range(7):
            px[cy][cx + sx * k] = (0, 229, 255, 255)
            px[cy + sy * k][cx] = (0, 229, 255, 255)

    write_png(os.path.join(OUT, "titan_bay.png"), W, H, px)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    gen_reticles()
    gen_radar()
    gen_vignette()
    gen_bay()
