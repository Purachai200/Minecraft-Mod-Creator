#!/usr/bin/env python3
"""Generate the 32x32 item textures for Titan Combat.

Pure standard library (zlib + struct), no Pillow required.

Style rules shared by every item:
  * dark gunmetal / graphite bodies, light from the top-left
    (1-px highlights on top/left edges, shadows bottom/right)
  * an automatic 1-px darker outline around the silhouette
  * small saturated accents: cyan = tech/energy, amber = power/warning,
    red = ammo/danger
  * fully opaque or fully transparent pixels only (no AA noise)

Diagonal items (tools) are drawn in a rotated coordinate frame:
  a = x - y  (along the bottom-left -> top-right axis)
  c = x + y  (across the axis; small c = upper-left side = lit side)
which gives crisp 45-degree pixel staircases.

Usage:
  python3 tools/generate_item_textures.py            # writes into the mod resources
  python3 tools/generate_item_textures.py --out DIR  # writes somewhere else
  python3 tools/generate_item_textures.py --sheet FILE.png  # also writes a preview contact sheet
"""
import math
import os
import struct
import sys
import zlib

W = H = 32

# --------------------------------------------------------------------------- palette


def hx(s):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)


# gunmetal ramp, dark -> light
G = [hx(c) for c in ('#171a1f', '#262b33', '#363d47', '#4c5562', '#6c7887', '#9aa7b6', '#cfd8e2')]
# energy cyan
C = [hx(c) for c in ('#004650', '#00879a', '#00c4dc', '#00e5ff', '#8ff4ff', '#e6feff')]
# amber
A = [hx(c) for c in ('#5a3300', '#a86a00', '#e09400', '#ffab00', '#ffd27a')]
# red
R = [hx(c) for c in ('#4a0a0a', '#8f1717', '#d42424', '#ff3b3b', '#ff9a9a')]
# brass
B = [hx(c) for c in ('#4a3210', '#7d5a1e', '#b8862f', '#e0b04a', '#f8dd96')]
# battery green
N = [hx(c) for c in ('#064a32', '#0c8a55', '#16c878', '#45f2a2', '#b4ffd9', '#f0fff8')]
# depleted battery core
E = [hx(c) for c in ('#111716', '#18211f', '#1f2b28', '#283834', '#355049')]
# flame blue
F = [hx(c) for c in ('#13307a', '#1f55d6', '#3d8bff')]
WHITE = hx('#f4fbff')
# trooper olive drab
O = [hx(c) for c in ('#1c2114', '#2b331e', '#3c4629', '#4f5c35', '#677646', '#86965c', '#aab97e')]
SLATE = [hx(c) for c in ('#232a33', '#323b47', '#46525f', '#5f6d7c', '#8494a5')]


def darken(c, k):
    return (int(c[0] * k), int(c[1] * k), int(c[2] * k), 255)


# --------------------------------------------------------------------------- canvas


def cyl_index(t, n):
    """Cylinder shading profile across a body. t in [0,1] (0 = lit edge).
    Returns an index into a ramp of length n (0 = darkest)."""
    if t < 0.10:
        k = n - 2
    elif t < 0.30:
        k = n - 1
    elif t < 0.50:
        k = n - 2
    elif t < 0.72:
        k = n - 3
    elif t < 0.90:
        k = n - 4
    else:
        k = n - 5
    return max(0, min(n - 1, k))


def ac(x, y):
    return x - y, x + y


class Canvas:
    def __init__(self):
        self.p = [[None] * W for _ in range(H)]

    def set(self, x, y, col):
        if 0 <= x < W and 0 <= y < H and col is not None:
            self.p[y][x] = col

    def get(self, x, y):
        if 0 <= x < W and 0 <= y < H:
            return self.p[y][x]
        return None

    # ---- masks -----------------------------------------------------------
    @staticmethod
    def rect_m(x0, y0, x1, y1):
        return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}

    @staticmethod
    def rows_m(spans):
        m = set()
        for y, (x0, x1) in spans.items():
            for x in range(x0, x1 + 1):
                m.add((x, y))
        return m

    @staticmethod
    def disc_m(cx, cy, r):
        return {(x, y) for y in range(H) for x in range(W)
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r}

    @staticmethod
    def diag_m(a0, a1, cc, half, half_fn=None):
        m = set()
        for y in range(H):
            for x in range(W):
                a, c = ac(x, y)
                if a0 <= a <= a1:
                    h = half_fn(a) if half_fn else half
                    if h is not None and abs(c - cc) <= h:
                        m.add((x, y))
        return m

    # ---- painting --------------------------------------------------------
    def fill(self, m, col):
        """Fill a mask; col=None erases (cuts holes / gaps)."""
        for x, y in m:
            if col is None:
                if 0 <= x < W and 0 <= y < H:
                    self.p[y][x] = None
            else:
                self.set(x, y, col)

    def mat(self, m, sh, base, hi):
        """Flat material with 1-px bevel: highlight top/left, shadow bottom/right."""
        for x, y in m:
            up = (x, y - 1) in m
            lf = (x - 1, y) in m
            dn = (x, y + 1) in m
            rt = (x + 1, y) in m
            if not up or not lf:
                col = hi
            elif not dn or not rt:
                col = sh
            else:
                col = base
            self.set(x, y, col)

    def vcyl(self, m, ramp):
        """Cylinder standing vertically: shade by column."""
        xs = [x for x, _ in m]
        x0, x1 = min(xs), max(xs)
        w = max(1, x1 - x0)
        for x, y in m:
            self.set(x, y, ramp[cyl_index((x - x0) / w, len(ramp))])

    def hcyl(self, m, ramp):
        """Cylinder lying horizontally: shade by row."""
        ys = [y for _, y in m]
        y0, y1 = min(ys), max(ys)
        h = max(1, y1 - y0)
        for x, y in m:
            self.set(x, y, ramp[cyl_index((y - y0) / h, len(ramp))])

    def dcyl(self, m, cc, half, ramp):
        """Cylinder along the 45-degree axis: shade by c (across)."""
        for x, y in m:
            _, c = ac(x, y)
            t = (c - (cc - half)) / max(1, 2 * half)
            self.set(x, y, ramp[cyl_index(min(1, max(0, t)), len(ramp))])

    def outline(self):
        """Add a 1-px outline outside the silhouette (4-neighbourhood).
        Outline colour = darkest neighbour, darkened, so glowing parts get a
        tinted rim instead of a flat black one."""
        add = {}
        for y in range(H):
            for x in range(W):
                if self.p[y][x] is not None:
                    continue
                nb = [self.get(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                nb = [n for n in nb if n is not None]
                if nb:
                    d = min(nb, key=lambda c: c[0] + c[1] + c[2])
                    o = darken(d, 0.42)
                    # keep outlines in the dark graphite family for metal parts
                    add[(x, y)] = (max(10, o[0]), max(11, o[1]), max(13, o[2]), 255)
        for (x, y), col in add.items():
            self.p[y][x] = col

    def png(self):
        raw = bytearray()
        for y in range(H):
            raw.append(0)
            for x in range(W):
                c = self.p[y][x]
                raw.extend(c if c is not None else (0, 0, 0, 0))
        return encode_png(W, H, bytes(raw))


def encode_png(w, h, raw_with_filters):
    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data
                + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw_with_filters, 9))
            + chunk(b'IEND', b''))


# --------------------------------------------------------------------------- items


def battery(full=True):
    cv = Canvas()
    core = N if full else E
    # terminal nub
    cv.vcyl(cv.rect_m(13, 2, 18, 3), G[1:6])
    # top cap
    cv.vcyl(cv.rect_m(10, 4, 21, 7) - {(10, 4), (21, 4)}, G[1:7])
    # top collar
    cv.vcyl(cv.rect_m(9, 8, 22, 9), G[0:5])
    # glowing core
    cv.vcyl(cv.rect_m(11, 10, 20, 21), core)
    # cage rails
    cv.fill(cv.rect_m(9, 10, 9, 21), G[4])
    cv.fill(cv.rect_m(10, 10, 10, 21), G[3])
    cv.fill(cv.rect_m(21, 10, 21, 21), G[2])
    cv.fill(cv.rect_m(22, 10, 22, 21), G[1])
    # cage ribs across the core
    for y in (14, 17):
        for x in range(11, 21):
            cv.set(x, y, G[2] if x > 15 else G[3])
    # bright energy streak
    if full:
        for y in (11, 12, 15, 18, 19, 20):
            cv.set(13, y, N[5])
    # lower collar
    cv.vcyl(cv.rect_m(9, 22, 22, 23), G[0:5])
    # bottom cap with hazard band
    cv.vcyl(cv.rect_m(10, 24, 21, 27), G[1:7])
    for x in range(11, 21):
        cv.set(x, 25, A[3] if (x // 2) % 2 == 0 else G[0])
    # base foot
    cv.vcyl(cv.rect_m(12, 28, 19, 29), G[0:5])
    # status lights on the top cap
    lamp = C[4] if full else R[2]
    cv.set(12, 6, lamp)
    cv.set(14, 6, (C[2] if full else R[0]))
    cv.set(16, 6, (C[2] if full else R[0]))
    cv.outline()
    return cv


def titan_ammo():
    cv = Canvas()
    rounds = [(4, 2), (10, 0), (16, 3), (22, 1)]
    for x0, dy in rounds:
        top = 3 + dy
        tip = {(x0 + 2, top)} | cv.rect_m(x0 + 1, top + 1, x0 + 3, top + 1) | cv.rect_m(x0, top + 2, x0 + 4, top + 4)
        cv.vcyl(tip, B)
        cv.vcyl(cv.rect_m(x0, top + 5, x0 + 4, top + 5), R[1:5])
        cv.vcyl(cv.rect_m(x0, top + 6, x0 + 4, 17), G[2:7])
    # crate
    crate = cv.rect_m(2, 16, 29, 29) - {(2, 29), (29, 29)}
    cv.mat(crate, G[1], G[2], G[4])
    # lid rim
    cv.fill(cv.rect_m(3, 18, 28, 18), G[1])
    cv.fill(cv.rect_m(2, 16, 29, 16), G[5])
    cv.fill(cv.rect_m(3, 17, 28, 17), G[3])
    # front label: red stencil plate with dark round icons
    cv.mat(cv.rect_m(5, 21, 26, 26), R[0], R[2], R[3])
    for x in (8, 12, 16, 20, 24):
        cv.fill(cv.rect_m(x - 1, 23, x - 1, 24), R[0])
        cv.set(x - 1, 22, R[1])
    # amber latch
    cv.mat(cv.rect_m(14, 17, 17, 19), A[1], A[3], A[4])
    # corner rivets
    for x, y in ((4, 20), (27, 20), (4, 27), (27, 27)):
        cv.set(x, y, G[5])
    cv.outline()
    return cv


def fusion_reactor():
    cv = Canvas()
    cx = cy = 15.5
    octa = {(x, y) for y in range(2, 30) for x in range(2, 30)
            if abs(x - cx) + abs(y - cy) <= 20}
    cv.mat(octa, G[1], G[3], G[5])
    # inner bevel step
    inner = {(x, y) for (x, y) in octa if abs(x - cx) + abs(y - cy) <= 18
             and 3 <= x <= 28 and 3 <= y <= 28}
    cv.mat(inner, G[4], G[2], G[1])  # inverted bevel = recessed
    # groove
    cv.fill(cv.disc_m(cx, cy, 11.6), G[0])
    # glowing ring
    for x, y in cv.disc_m(cx, cy, 10.6) - cv.disc_m(cx, cy, 7.4):
        d = (x - cx) + (y - cy)
        r = math.hypot(x - cx, y - cy)
        if d < -6:
            col = C[5] if r > 8.6 and d < -11 else C[4]
        elif d > 6:
            col = C[1]
        else:
            col = C[3]
        if r < 8.2:
            col = C[2] if d < 0 else C[1]
        cv.set(x, y, col)
    # dark inner chamber
    cv.fill(cv.disc_m(cx, cy, 7.0), G[1])
    for x, y in cv.disc_m(cx, cy, 7.0) - cv.disc_m(cx, cy, 6.0):
        cv.set(x, y, G[0])
    # core
    cv.fill(cv.disc_m(cx, cy, 3.6), C[3])
    cv.fill(cv.disc_m(cx - 0.5, cy - 0.5, 2.2), C[5])
    cv.set(14, 14, WHITE)
    # four clamps over the ring
    for (x0, y0, x1, y1) in ((14, 3, 17, 7), (14, 24, 17, 28), (3, 14, 7, 17), (24, 14, 28, 17)):
        cv.mat(cv.rect_m(x0, y0, x1, y1), G[1], G[3], G[5])
    # amber warning lamps on the clamps
    for x, y in ((15, 5), (16, 26), (5, 16), (26, 15)):
        cv.set(x, y, A[3])
    # corner bolts
    for x, y in ((7, 7), (24, 7), (7, 24), (24, 24)):
        cv.set(x, y, G[6])
        cv.set(x + 1, y + 1, G[0])
    cv.outline()
    return cv


def cockpit_module():
    cv = Canvas()
    spans = {3: (10, 21), 4: (8, 23), 5: (6, 25), 6: (5, 26), 7: (4, 27)}
    for y in range(8, 22):
        spans[y] = (3, 28)
    spans.update({22: (4, 27), 23: (5, 26), 24: (7, 24), 25: (7, 24), 26: (8, 23), 27: (9, 22), 28: (11, 20)})
    hull = cv.rows_m(spans)
    cv.mat(hull, G[1], G[3], G[5])
    # canopy dome (upper section) slightly lighter
    dome = {(x, y) for (x, y) in hull if y <= 9 and 0 < x < 31}
    dome = {(x, y) for (x, y) in dome if (x - 1, y) in hull and (x + 1, y) in hull and (x, y - 1) in hull}
    cv.mat(dome, G[3], G[4], G[5])
    # brow plate
    cv.fill(cv.rect_m(4, 10, 27, 10), G[5])
    cv.fill(cv.rect_m(4, 11, 27, 11), G[2])
    # visor slit
    cv.fill(cv.rect_m(5, 12, 26, 15), G[0])
    for x in range(7, 25):
        cv.set(x, 13, C[5] if 10 <= x <= 13 else C[4])
        cv.set(x, 14, C[2])
    cv.set(6, 13, C[1]); cv.set(25, 13, C[1])
    cv.set(6, 14, C[0]); cv.set(25, 14, C[0])
    # centre seam
    for y in range(17, 27):
        cv.set(15, y, G[1])
        cv.set(16, y, G[4])
    # side vents
    for y in (18, 20, 22):
        cv.fill(cv.rect_m(6, y, 11, y), G[0])
        cv.fill(cv.rect_m(20, y, 25, y), G[0])
        cv.fill(cv.rect_m(6, y + 1, 11, y + 1), G[4])
        cv.fill(cv.rect_m(20, y + 1, 25, y + 1), G[4])
    # hinge / status lights
    cv.set(3, 17, A[3]); cv.set(28, 17, A[3])
    cv.set(15, 6, A[3]); cv.set(16, 6, A[2])
    # chin warning chevron
    cv.set(14, 25, A[3]); cv.set(17, 25, A[3])
    cv.outline()
    return cv


def chassis_frame():
    cv = Canvas()
    # torso: broad chest tapering to the waist
    spans = {}
    for y in range(5, 17):
        spans[y] = (6, 25)
    spans.update({4: (8, 23), 17: (7, 24), 18: (7, 24), 19: (8, 23), 20: (8, 23)})
    torso = cv.rows_m(spans)
    cv.mat(torso, G[1], G[3], G[5])
    # open frame cavity with ribs
    cv.fill(cv.rect_m(10, 7, 21, 17), G[0])
    for y in (9, 12, 15):
        cv.fill(cv.rect_m(10, y, 21, y), G[2])
        cv.fill(cv.rect_m(10, y - 1, 21, y - 1), G[1])
    # spine power line
    for y in range(7, 18):
        cv.set(15, y, C[3] if y % 3 else C[5])
        cv.set(16, y, C[1] if y % 3 else C[3])
    # shoulder pauldrons
    for x0, flip in ((1, False), (24, True)):
        sh = cv.rect_m(x0, 3, x0 + 6, 13) - {(x0, 3), (x0 + 6, 3), (x0, 13), (x0 + 6, 13)}
        cv.mat(sh, G[1], G[4], G[5])
        for x in range(x0 + 1, x0 + 6):
            for y in (5, 6):
                k = (x + y + (1 if flip else 0)) % 4
                cv.set(x, y, A[3] if k < 2 else G[0])
        cv.set(x0 + 3, 10, G[6]); cv.set(x0 + 3, 11, G[1])
    # collar / neck mount
    cv.mat(cv.rect_m(11, 2, 20, 4), G[2], G[4], G[6])
    cv.set(15, 3, A[3]); cv.set(16, 3, A[3])
    # segmented abdomen plates (no thin stem, reads as one armoured block)
    ab1 = cv.rows_m({22: (9, 22), 23: (9, 22), 24: (10, 21)})
    cv.mat(ab1, G[1], G[3], G[5])
    ab2 = cv.rows_m({26: (11, 20), 27: (11, 20), 28: (12, 19)})
    cv.mat(ab2, G[1], G[3], G[5])
    cv.fill(cv.rect_m(10, 25, 21, 25), G[0])
    cv.set(15, 27, R[3]); cv.set(16, 27, R[2])
    cv.set(12, 23, A[3]); cv.set(19, 23, A[3])
    cv.outline()
    return cv


def hydraulic_actuator():
    cv = Canvas()
    cc = 31
    # eyelet mounts
    for a_mid in (-23, 21):
        x, y = (a_mid + cc) // 2, (cc - a_mid) // 2
        eye = cv.disc_m(x, y, 3.3)
        cv.mat(eye, G[1], G[3], G[5])
        cv.fill(cv.disc_m(x, y, 1.0), G[0])
        cv.set(x, y, G[0])
    # chrome rod
    rod = cv.diag_m(0, 19, cc, 2)
    cv.dcyl(rod, cc, 2, G[2:7] + [WHITE])
    # cylinder barrel
    body = cv.diag_m(-18, 1, cc, 6)
    cv.dcyl(body, cc, 6, G[0:6])
    # end cap + gland collar
    cv.dcyl(cv.diag_m(-19, -16, cc, 7), cc, 7, G[0:5])
    cv.dcyl(cv.diag_m(0, 3, cc, 7), cc, 7, G[0:5])
    # amber pressure band
    cv.dcyl(cv.diag_m(-9, -7, cc, 6), cc, 6, A)
    # hydraulic line + cyan pressure gauge
    for a in range(-14, -1):
        for c in (cc - 7,):
            if (a + c) % 2 == 0:
                cv.set((a + c) // 2, (c - a) // 2, G[4])
    for (a, c) in ((-4, 28), (-3, 29), (-5, 29), (-4, 30)):
        cv.set((a + c) // 2, (c - a) // 2, C[3])
    cv.outline()
    return cv


def weapon_mount():
    cv = Canvas()
    # base plate
    cv.mat(cv.rect_m(3, 25, 22, 28), G[1], G[3], G[5])
    for x in (5, 20):
        cv.set(x, 26, G[6]); cv.set(x, 27, G[0])
    cv.fill(cv.rect_m(8, 27, 17, 27), A[3])
    for x in range(8, 18, 2):
        cv.set(x, 27, G[0])
    # pedestal
    cv.vcyl(cv.rect_m(9, 18, 16, 24), G[1:7])
    # yoke arms
    cv.mat(cv.rect_m(6, 11, 9, 21), G[1], G[3], G[5])
    # receiver
    rec = cv.rect_m(8, 9, 22, 17) - {(8, 9), (22, 17)}
    cv.mat(rec, G[1], G[3], G[5])
    cv.fill(cv.rect_m(10, 15, 20, 15), G[1])
    cv.fill(cv.rect_m(10, 11, 20, 11), R[2])
    cv.fill(cv.rect_m(10, 12, 20, 12), R[1])
    # pivot hub
    hub = cv.disc_m(12, 15, 3.3)
    cv.mat(hub, G[1], G[4], G[6])
    cv.set(12, 15, G[0])
    # optic
    cv.mat(cv.rect_m(13, 5, 19, 8), G[1], G[2], G[4])
    cv.set(19, 6, C[4]); cv.set(19, 7, C[2])
    # barrel shroud + muzzle
    cv.hcyl(cv.rect_m(22, 10, 27, 14), G[1:7])
    for x in (23, 25):
        cv.set(x, 11, G[0]); cv.set(x, 12, G[0])
    cv.hcyl(cv.rect_m(28, 9, 29, 15), G[0:6])
    cv.set(29, 12, G[0])
    cv.outline()
    return cv


def titan_drop_beacon(head=G, lamp=R):
    cv = Canvas()
    cc = 31
    # ground spike
    cv.dcyl(cv.diag_m(-26, -20, cc, 0, lambda a: (a + 26) // 2), cc, 3, G[2:7])
    # grip
    grip = cv.diag_m(-20, -3, cc, 4)
    cv.dcyl(grip, cc, 4, G[0:5])
    for x, y in grip:
        a, c = ac(x, y)
        if a in (-17, -13, -9) and abs(c - cc) < 4:
            cv.set(x, y, G[0])
    # hazard collar
    col = cv.diag_m(-3, 2, cc, 5)
    for x, y in col:
        a, c = ac(x, y)
        cv.set(x, y, A[3] if ((c // 2) % 2 == 0) else G[0])
    for x, y in col:
        a, c = ac(x, y)
        if c == cc - 5:
            cv.set(x, y, A[4])
    # head
    cv.dcyl(cv.diag_m(2, 10, cc, 5), cc, 5, head[1:7])
    # dome lamp
    cv.dcyl(cv.diag_m(10, 15, cc, 0, lambda a: {10: 4, 11: 4, 12: 3, 13: 3, 14: 2, 15: 1}[a]), cc, 4, lamp)
    # antenna
    for x, y in cv.diag_m(6, 24, cc - 9, 1):
        a, c = ac(x, y)
        cv.set(x, y, G[5] if c < cc - 9 else G[3])
    # cyan tip light
    for x, y in cv.diag_m(23, 27, cc - 9, 2):
        cv.set(x, y, C[4])
    cv.outline()
    return cv


def hangar_transponder():
    cv = Canvas()
    cc = 31
    # antenna (behind body)
    ant = cv.diag_m(8, 25, cc - 5, 1)
    for x, y in ant:
        a, c = ac(x, y)
        cv.set(x, y, G[5] if c < cc - 5 else G[2])
    for x, y in cv.diag_m(24, 27, cc - 5, 2):
        cv.set(x, y, A[3])
    # body
    def half(a):
        if a in (-19, 13):
            return 6
        return 7
    body = cv.diag_m(-19, 13, cc, 0, half)
    cv.mat(body, G[1], G[3], G[5])
    # screen bezel + screen
    cv.fill(cv.diag_m(-1, 11, cc, 5), G[0])
    scr = cv.diag_m(1, 9, cc, 3)
    for x, y in scr:
        a, c = ac(x, y)
        cv.set(x, y, C[3] if (c - cc) % 3 else C[1])
    for x, y in cv.diag_m(4, 5, cc - 1, 0):
        cv.set(x, y, C[5])
    # keypad: three columns of buttons
    for x, y in cv.diag_m(-15, -4, cc, 4):
        cv.set(x, y, G[1])
    for a0 in (-14, -10, -6):
        for c0 in (cc - 3, cc + 1):
            for x, y in cv.diag_m(a0, a0 + 2, c0 + 1, 1):
                a, c = ac(x, y)
                cv.set(x, y, G[5] if c <= c0 else G[3])
    # red transmit key
    for x, y in cv.diag_m(-18, -17, cc, 1):
        cv.set(x, y, R[3])
    cv.outline()
    return cv


def pilot_license():
    cv = Canvas()
    card = cv.rect_m(2, 6, 29, 25) - {(2, 6), (29, 6), (2, 25), (29, 25)}
    cv.mat(card, SLATE[0], SLATE[2], SLATE[4])
    # amber header band
    cv.fill(cv.rect_m(3, 7, 28, 9), A[3])
    cv.fill(cv.rect_m(3, 9, 28, 9), A[1])
    for x in range(14, 27, 2):
        cv.set(x, 8, A[0])
    cv.fill(cv.rect_m(4, 7, 9, 8), A[4])
    # photo
    cv.fill(cv.rect_m(4, 11, 12, 22), G[0])
    cv.fill(cv.rect_m(5, 12, 11, 21), hx('#1d3644'))
    helmet = cv.disc_m(8, 16, 2.9) | cv.rect_m(6, 16, 10, 19)
    cv.mat(helmet, G[2], G[4], G[5])
    cv.fill(cv.rect_m(6, 16, 10, 16), C[4])
    cv.set(10, 16, C[2])
    cv.fill(cv.rect_m(5, 20, 11, 21), G[2])
    cv.fill(cv.rect_m(7, 20, 9, 20), G[3])
    # chip
    chip = cv.rect_m(22, 12, 26, 16)
    cv.mat(chip, B[1], B[3], B[4])
    cv.fill(cv.rect_m(24, 12, 24, 16), B[1])
    cv.fill(cv.rect_m(22, 14, 26, 14), B[1])
    # text lines
    for y, x1 in ((12, 19), (14, 18), (18, 26), (20, 23), (22, 25)):
        cv.fill(cv.rect_m(14, y, x1, y), SLATE[4] if y < 16 else SLATE[3])
    # cyan stripe
    cv.fill(cv.rect_m(14, 16, 20, 16), C[3])
    cv.outline()
    return cv


def paint_spray_can():
    cv = Canvas()
    cc = 31
    # actuator cap (top-right)
    cv.dcyl(cv.diag_m(9, 15, cc, 0, lambda a: 4 if a < 14 else 3), cc, 4, G[2:7] + [WHITE])
    # red push-button with nozzle on the lit side
    cv.dcyl(cv.diag_m(15, 18, cc, 0, lambda a: 2 if a < 18 else 1), cc, 2, R[1:5])
    for x, y in cv.diag_m(15, 16, cc - 3, 0):
        cv.set(x, y, G[0])
    # body
    cv.dcyl(cv.diag_m(-21, 5, cc, 6), cc, 6, G[0:6])
    # shoulder
    cv.dcyl(cv.diag_m(6, 8, cc, 0, lambda a: {6: 6, 7: 5, 8: 5}[a]), cc, 6, G[1:7])
    # colour bands
    for (a0, a1, ramp) in ((-12, -10, R), (-8, -6, A), (-4, -2, C[0:5])):
        cv.dcyl(cv.diag_m(a0, a1, cc, 6), cc, 6, ramp)
    # rims
    cv.dcyl(cv.diag_m(-24, -21, cc, 5), cc, 5, G[0:5])
    cv.dcyl(cv.diag_m(4, 6, cc, 6), cc, 6, G[1:7])
    cv.outline()
    return cv


def blowtorch():
    cv = Canvas()
    cc = 31
    # flame
    def fh(a):
        return {16: 3, 17: 3, 18: 4, 19: 4, 20: 4, 21: 3, 22: 3, 23: 2, 24: 2, 25: 1, 26: 1, 27: 0}.get(a)
    flame = cv.diag_m(16, 27, cc, 0, fh)
    for x, y in flame:
        a, c = ac(x, y)
        d = abs(c - cc)
        if a >= 24:
            col = A[3] if d == 0 else A[2]
        elif d <= 1 and a <= 21:
            col = WHITE if a <= 18 else C[5]
        elif d <= 2:
            col = C[3]
        else:
            col = F[2]
        cv.set(x, y, col)
    # tip
    cv.dcyl(cv.diag_m(13, 15, cc, 2), cc, 2, G[2:7])
    # nozzle tube (brass)
    cv.dcyl(cv.diag_m(1, 12, cc, 1), cc, 1, B[1:5])
    # valve body
    cv.dcyl(cv.diag_m(-8, 1, cc, 5), cc, 5, G[1:7])
    # amber valve knob sticking out on the lit side
    for x, y in cv.diag_m(-6, -3, cc - 8, 2):
        a, c = ac(x, y)
        cv.set(x, y, A[4] if c < cc - 8 else A[2])
    # grip
    grip = cv.diag_m(-23, -9, cc, 3)
    cv.dcyl(grip, cc, 3, SLATE[0:5])
    for x, y in grip:
        a, c = ac(x, y)
        if a in (-20, -17, -14, -11):
            cv.set(x, y, G[0])
    # end cap with red hose port
    cv.dcyl(cv.diag_m(-27, -24, cc, 4), cc, 4, G[0:5])
    for x, y in cv.diag_m(-27, -27, cc, 1):
        cv.set(x, y, R[3])
    cv.outline()
    return cv


# --------------------------------------------------------------------------- titan weapon modules
# Each weapon has one accent colour that its ammo item repeats so players can pair them:
#   splitter = blue, thermite = orange, leadwall = red, tracker = amber,
#   predator = lime, xo16 = violet, railgun = cyan

BL = [hx(c) for c in ('#0d2266', '#1a46b8', '#2f6fff', '#5c9dff', '#bcd8ff')]
O = [hx(c) for c in ('#4d1600', '#992e00', '#e65200', '#ff7a1a', '#ffb070')]
L = [hx(c) for c in ('#1f4a00', '#3c8a00', '#62c812', '#8dff3d', '#d0ffa8')]
V = [hx(c) for c in ('#2e0a52', '#561a99', '#8a3ddb', '#b46eff', '#e2c4ff')]
CC = 31  # diagonal axis for weapons (x + y = 31)


def dm(a0, a1, c0, c1):
    """Diagonal box covering a in [a0,a1] and c in [c0,c1]."""
    return Canvas.diag_m(a0, a1, (c0 + c1) / 2, (c1 - c0) / 2)


def dcyl_box(cv, a0, a1, c0, c1, ramp):
    cv.dcyl(dm(a0, a1, c0, c1), (c0 + c1) / 2, (c1 - c0) / 2, ramp)


def dmat(cv, a0, a1, c0, c1, sh=None, base=None, hi=None):
    cv.mat(dm(a0, a1, c0, c1), sh or G[1], base or G[3], hi or G[5])


def dfill(cv, a0, a1, c0, c1, col):
    cv.fill(dm(a0, a1, c0, c1), col)


def stock_and_grip(cv, s0, s1, sc0, sc1, g0, gc0, gc1):
    dmat(cv, s0, s1, sc0, sc1, G[1], G[2], G[4])
    dfill(cv, s0 + 2, s1 - 2, sc0 + 2, sc0 + 2, G[1])
    dmat(cv, g0, g0 + 3, gc0, gc1, G[0], G[1], G[3])


def weapon_splitter_rifle():
    cv = Canvas()
    stock_and_grip(cv, -27, -16, CC - 2, CC + 5, -12, CC + 5, CC + 12)
    dcyl_box(cv, -17, 3, CC - 5, CC + 5, G[1:7])
    # blue energy conduit along the receiver
    dfill(cv, -14, 1, CC - 2, CC - 2, BL[3])
    dfill(cv, -14, 1, CC - 1, CC - 1, BL[1])
    # split barrel: two prongs with an open fork and an energy arc between them
    dcyl_box(cv, 3, 23, CC - 8, CC - 4, G[2:7])
    dcyl_box(cv, 3, 23, CC + 4, CC + 8, G[1:6])
    for x, y in dm(3, 17, CC - 3, CC + 3):
        _, c = ac(x, y)
        d = abs(c - CC)
        cv.set(x, y, BL[4] if d == 0 else BL[3] if d == 1 else BL[2] if d == 2 else G[0])
    dfill(cv, 18, 19, CC - 1, CC + 1, WHITE)
    dfill(cv, 18, 23, CC - 3, CC + 3, None)
    dfill(cv, 18, 19, CC - 1, CC + 1, WHITE)
    for c in (CC - 6, CC + 6):
        dfill(cv, 22, 23, c - 1, c + 1, BL[3])
    cv.outline()
    return cv


def weapon_thermite_launcher():
    cv = Canvas()
    stock_and_grip(cv, -26, -14, CC - 2, CC + 5, -10, CC + 7, CC + 14)
    dcyl_box(cv, -14, 13, CC - 7, CC + 7, G[0:6])
    # glowing heat vents
    for a in (1, 5, 9):
        for x, y in dm(a, a, CC - 6, CC + 6):
            _, c = ac(x, y)
            cv.set(x, y, O[4] if c < CC - 2 else O[3] if c < CC + 3 else O[2])
    # orange hazard band at the breech
    dcyl_box(cv, -11, -9, CC - 7, CC + 7, O)
    # carry handle on top
    dmat(cv, -6, 6, CC - 11, CC - 9, G[2], G[3], G[5])
    dfill(cv, -4, 4, CC - 8, CC - 8, G[0])
    # big muzzle with hot bore
    dcyl_box(cv, 13, 18, CC - 8, CC + 8, G[1:6])
    dfill(cv, 16, 18, CC - 5, CC + 5, O[2])
    dfill(cv, 17, 18, CC - 3, CC + 3, O[3])
    dfill(cv, 18, 18, CC - 1, CC + 1, O[4])
    cv.outline()
    return cv


def weapon_leadwall():
    cv = Canvas()
    stock_and_grip(cv, -27, -15, CC - 3, CC + 6, -13, CC + 7, CC + 13)
    dmat(cv, -15, 1, CC - 7, CC + 7)
    # two short, fat barrels
    dcyl_box(cv, 1, 21, CC - 7, CC - 1, G[1:7])
    dcyl_box(cv, 1, 21, CC + 1, CC + 7, G[0:6])
    dfill(cv, 12, 21, CC, CC, None)
    dfill(cv, 20, 21, CC - 5, CC - 3, G[0])
    dfill(cv, 20, 21, CC + 3, CC + 5, G[0])
    # barrel clamp
    dcyl_box(cv, 9, 11, CC - 8, CC + 8, G[1:6])
    # red shells on the side saddle
    for a0 in (-12, -7, -2):
        dcyl_box(cv, a0, a0 + 3, CC - 2, CC + 4, R[1:5])
        dfill(cv, a0, a0 + 3, CC + 4, CC + 5, B[3])
    cv.outline()
    return cv


def weapon_tracker_cannon():
    cv = Canvas()
    stock_and_grip(cv, -27, -16, CC - 3, CC + 5, -12, CC + 6, CC + 13)
    dmat(cv, -16, 3, CC - 6, CC + 6)
    # heavy 40mm barrel + muzzle brake
    dcyl_box(cv, 3, 21, CC - 3, CC + 3, G[1:7])
    dcyl_box(cv, 21, 26, CC - 5, CC + 5, G[0:5])
    dfill(cv, 23, 23, CC - 4, CC + 4, G[0])
    # lock-on optic on the lit side
    dfill(cv, -7, -4, CC - 8, CC - 7, G[2])
    dcyl_box(cv, -12, 3, CC - 13, CC - 8, G[1:7])
    dfill(cv, 3, 4, CC - 12, CC - 9, A[3])
    dfill(cv, 4, 4, CC - 11, CC - 11, A[4])
    # amber lock-on marks on the receiver
    for a in (-12, -8, -4):
        dfill(cv, a, a + 1, CC + 1, CC + 2, A[3])
    cv.outline()
    return cv


def weapon_predator_cannon():
    cv = Canvas()
    dmat(cv, -24, -10, CC - 5, CC + 5)
    dfill(cv, -21, -13, CC - 1, CC - 1, G[1])
    # ammo box below
    dmat(cv, -11, 0, CC + 7, CC + 15, G[1], G[2], G[4])
    dfill(cv, -10, -1, CC + 10, CC + 11, L[3])
    # motor housing
    dcyl_box(cv, -10, 5, CC - 7, CC + 7, G[0:6])
    dcyl_box(cv, -3, -1, CC - 7, CC + 7, L)
    # carry handle
    dmat(cv, -8, 0, CC - 11, CC - 9, G[2], G[3], G[5])
    # rotary barrel cluster
    for off, ramp in ((-5, G[2:7]), (0, G[1:6]), (5, G[0:5])):
        dcyl_box(cv, 5, 26, CC + off - 1, CC + off + 1, ramp)
    for a0 in (11, 20):
        dcyl_box(cv, a0, a0 + 2, CC - 7, CC + 7, G[1:6])
    dfill(cv, 26, 26, CC - 7, CC + 7, None)
    cv.outline()
    return cv


def weapon_xo16_chaingun():
    cv = Canvas()
    stock_and_grip(cv, -27, -15, CC - 3, CC + 4, -14, CC + 5, CC + 11)
    dmat(cv, -15, 3, CC - 5, CC + 5)
    # vented shroud + barrel
    dcyl_box(cv, 3, 18, CC - 4, CC + 4, G[1:7])
    for a in (6, 10, 14):
        dfill(cv, a, a + 1, CC - 2, CC + 1, G[0])
    dcyl_box(cv, 18, 26, CC - 1, CC + 1, G[2:7])
    dcyl_box(cv, 24, 26, CC - 3, CC + 3, G[0:5])
    # violet drum magazine
    drum = Canvas.disc_m(17, 22, 5.6)
    cv.mat(drum, G[1], G[3], G[5])
    for x, y in Canvas.disc_m(17, 22, 3.9) - Canvas.disc_m(17, 22, 2.2):
        cv.set(x, y, V[3] if x + y < 39 else V[2])
    cv.fill(Canvas.disc_m(17, 22, 1.5), G[2])
    cv.set(17, 22, V[4])
    # receiver accent
    dfill(cv, -12, -2, CC - 3, CC - 3, V[3])
    cv.outline()
    return cv


def weapon_plasma_railgun():
    cv = Canvas()
    stock_and_grip(cv, -28, -18, CC - 2, CC + 5, -14, CC + 5, CC + 12)
    dmat(cv, -18, -2, CC - 5, CC + 5)
    # scope
    dfill(cv, -11, -9, CC - 7, CC - 6, G[2])
    dcyl_box(cv, -16, -4, CC - 11, CC - 7, G[1:7])
    dfill(cv, -4, -4, CC - 10, CC - 8, C[4])
    # twin rails with a plasma channel
    dcyl_box(cv, -2, 27, CC - 4, CC - 2, G[2:7])
    dcyl_box(cv, -2, 27, CC + 2, CC + 4, G[1:6])
    for x, y in dm(-2, 25, CC - 1, CC + 1):
        _, c = ac(x, y)
        cv.set(x, y, C[4] if c == CC else C[2])
    # cyan coils
    for a0 in (2, 8, 14, 20):
        dcyl_box(cv, a0, a0 + 1, CC - 5, CC + 5, C[0:5])
    cv.outline()
    return cv


# --------------------------------------------------------------------------- weapon magazines


def ammo_splitter_rifle():
    cv = Canvas()
    for x0 in (12, 18):
        cv.vcyl(cv.rect_m(x0, 3, x0 + 1, 5), G[2:7])
    body = cv.rect_m(9, 6, 22, 28) - {(9, 6), (22, 6), (9, 28), (22, 28)}
    cv.mat(body, G[1], G[3], G[5])
    cv.fill(cv.rect_m(11, 8, 20, 25), G[0])
    for y0 in (9, 13, 17, 21):
        cv.vcyl(cv.rect_m(12, y0, 19, y0 + 2), BL)
    cv.set(13, 9, BL[4]); cv.set(13, 13, BL[4])
    cv.fill(cv.rect_m(11, 26, 20, 26), BL[2])
    cv.outline()
    return cv


def ammo_thermite_launcher():
    cv = Canvas()
    # carry handle
    cv.fill(cv.rect_m(12, 3, 19, 3), G[4])
    cv.fill(cv.rect_m(11, 4, 11, 6), G[4]); cv.fill(cv.rect_m(20, 4, 20, 6), G[2])
    cv.vcyl(cv.rect_m(10, 6, 21, 7), G[1:7])
    cv.vcyl(cv.rect_m(7, 8, 24, 28) - {(7, 28), (24, 28)}, G[0:6])
    cv.vcyl(cv.rect_m(7, 12, 24, 22), O)
    # flame glyph
    for x, y in ((15, 14), (16, 15), (14, 16), (15, 16), (16, 16), (17, 17), (14, 17), (15, 18), (16, 18),
                 (14, 19), (15, 19), (16, 19), (17, 19), (15, 20), (16, 20)):
        cv.set(x, y, O[0])
    for x in range(8, 24):
        cv.set(x, 25, A[3] if (x // 2) % 2 == 0 else G[0])
    cv.outline()
    return cv


def ammo_leadwall():
    cv = Canvas()
    for x0, top in ((5, 6), (10, 4), (15, 7), (20, 5)):
        cv.vcyl(cv.rect_m(x0, top, x0 + 4, 16), R[1:5])
        cv.fill(cv.rect_m(x0 + 1, top, x0 + 3, top), R[0])
        cv.set(x0 + 2, top, R[1])
        cv.vcyl(cv.rect_m(x0, 17, x0 + 4, 18), B[1:5])
    box = cv.rect_m(3, 19, 28, 28) - {(3, 28), (28, 28)}
    cv.mat(box, G[1], G[2], G[4])
    cv.fill(cv.rect_m(3, 19, 28, 19), G[5])
    cv.mat(cv.rect_m(6, 22, 25, 26), R[0], R[2], R[3])
    for x in range(8, 24, 3):
        cv.fill(cv.rect_m(x, 24, x + 1, 24), R[0])
    cv.outline()
    return cv


def ammo_tracker_cannon():
    cv = Canvas()
    for x0 in (4, 12, 20):
        head = cv.rows_m({4: (x0 + 2, x0 + 5), 5: (x0 + 1, x0 + 6), 6: (x0, x0 + 7), 7: (x0, x0 + 7), 8: (x0, x0 + 7)})
        cv.vcyl(head, A)
        cv.vcyl(cv.rect_m(x0, 9, x0 + 7, 9), G[0:5])
        cv.vcyl(cv.rect_m(x0, 10, x0 + 7, 25), B)
        cv.vcyl(cv.rect_m(x0, 26, x0 + 7, 27), B[0:4])
    # steel clip
    cv.mat(cv.rect_m(3, 18, 28, 21), G[1], G[3], G[5])
    for x in (7, 15, 23):
        cv.set(x, 19, G[6]); cv.set(x, 20, G[1])
    cv.outline()
    return cv


def ammo_predator_cannon():
    cv = Canvas()
    # belt of rounds coming out of the box in an arc
    for i, x0 in enumerate((4, 8, 12, 16, 20, 24)):
        top = (8, 6, 5, 5, 6, 8)[i]
        cv.vcyl(cv.rect_m(x0 + 1, top, x0 + 2, top + 1), G[3:7])
        cv.vcyl(cv.rect_m(x0, top + 2, x0 + 3, 15), B)
        cv.fill(cv.rect_m(x0, 12, x0 + 3, 12), G[1])
    box = cv.rect_m(2, 15, 29, 29) - {(2, 29), (29, 29)}
    cv.mat(box, G[1], G[2], G[4])
    cv.fill(cv.rect_m(2, 15, 29, 15), G[5])
    cv.fill(cv.rect_m(3, 16, 28, 16), G[1])
    cv.mat(cv.rect_m(5, 20, 26, 25), L[0], L[2], L[4])
    for x in range(7, 25, 4):
        cv.fill(cv.rect_m(x, 22, x + 1, 23), L[0])
    cv.outline()
    return cv


def ammo_xo16_chaingun():
    cv = Canvas()
    cv.mat(cv.rect_m(13, 2, 18, 7), G[1], G[3], G[5])
    cv.fill(cv.rect_m(14, 3, 17, 3), B[3])
    drum = Canvas.disc_m(15.5, 17.5, 12.4)
    cv.mat(drum, G[1], G[3], G[5])
    cv.fill(Canvas.disc_m(15.5, 17.5, 10.4), G[2])
    for x, y in Canvas.disc_m(15.5, 17.5, 8.4) - Canvas.disc_m(15.5, 17.5, 5.4):
        cv.set(x, y, V[3] if x + y < 33 else V[2] if x + y < 37 else V[1])
    cv.mat(Canvas.disc_m(15.5, 17.5, 3.6), G[2], G[4], G[6])
    cv.fill(Canvas.disc_m(15.5, 17.5, 1.2), V[4])
    for x, y in ((15, 7), (16, 7), (6, 17), (25, 18), (15, 28), (16, 28)):
        cv.set(x, y, G[6])
    cv.outline()
    return cv


def ammo_plasma_railgun():
    cv = Canvas()
    tip = cv.rows_m({2: (15, 16), 3: (14, 17), 4: (13, 18), 5: (12, 19)})
    cv.vcyl(tip, G[2:7])
    cv.vcyl(cv.rect_m(11, 6, 20, 7), G[0:5])
    cv.vcyl(cv.rect_m(12, 8, 19, 22), C)
    cv.fill(cv.rect_m(14, 9, 14, 21), C[5])
    for y in (12, 17):
        cv.vcyl(cv.rect_m(11, y, 20, y + 1), G[1:6])
    cv.vcyl(cv.rect_m(10, 23, 21, 26), G[1:7])
    cv.vcyl(cv.rect_m(12, 27, 19, 29), G[0:5])
    cv.fill(cv.rect_m(11, 24, 20, 24), C[3])
    cv.outline()
    return cv


WEAPON_IDS = ('splitter_rifle', 'thermite_launcher', 'leadwall', 'tracker_cannon',
              'predator_cannon', 'xo16_chaingun', 'plasma_railgun', 'mining_drill', 'chainsaw', 'light_smg')


def flight_module_rocket_jetpack():
    cv = Canvas()
    cv.mat(cv.rect_m(11, 7, 20, 22), G[1], G[3], G[5])
    cv.fill(cv.rect_m(14, 9, 17, 15), C[3])
    cv.fill(cv.rect_m(15, 10, 16, 14), WHITE)
    for x in range(12, 20):
        cv.set(x, 18, A[3] if (x % 2 == 0) else G[0])
        cv.set(x, 19, A[3] if ((x + 1) % 2 == 0) else G[0])
    left_tank = cv.rect_m(4, 5, 10, 21)
    cv.fill({(6, 3), (7, 3), (8, 3), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4)}, R[2])
    cv.vcyl(left_tank, G[1:7])
    cv.fill(cv.rect_m(4, 8, 10, 9), R[3])
    cv.fill(cv.rect_m(4, 15, 10, 16), R[2])
    right_tank = cv.rect_m(21, 5, 27, 21)
    cv.fill({(23, 3), (24, 3), (25, 3), (22, 4), (23, 4), (24, 4), (25, 4), (26, 4)}, R[2])
    cv.vcyl(right_tank, G[1:7])
    cv.fill(cv.rect_m(21, 8, 27, 9), R[3])
    cv.fill(cv.rect_m(21, 15, 27, 16), R[2])
    cv.fill(cv.rect_m(9, 11, 12, 12), G[5])
    cv.fill(cv.rect_m(19, 11, 22, 12), G[5])
    nozzle_l = cv.rows_m({22: (5, 9), 23: (4, 10), 24: (3, 11), 25: (3, 11)})
    cv.vcyl(nozzle_l, G[0:5])
    nozzle_r = cv.rows_m({22: (22, 26), 23: (21, 27), 24: (20, 28), 25: (20, 28)})
    cv.vcyl(nozzle_r, G[0:5])
    plume_l = cv.rows_m({26: (5, 9), 27: (6, 8), 28: (6, 8), 29: (7, 7)})
    for x, y in plume_l:
        cv.set(x, y, WHITE if x == 7 and y <= 27 else A[3] if y <= 27 else R[3])
    plume_r = cv.rows_m({26: (22, 26), 27: (23, 25), 28: (23, 25), 29: (24, 24)})
    for x, y in plume_r:
        cv.set(x, y, WHITE if x == 24 and y <= 27 else A[3] if y <= 27 else R[3])
    cv.outline()
    return cv


def flight_module_drone_lifter():
    cv = Canvas()
    hub = cv.disc_m(15.5, 15.5, 5.0)
    cv.mat(hub, G[1], G[3], G[5])
    core = cv.disc_m(15.5, 15.5, 2.5)
    cv.fill(core, C[3])
    cv.set(15, 15, WHITE); cv.set(16, 15, WHITE)
    nacelles = [(6, 6), (25, 6), (6, 25), (25, 25)]
    for x0, y0 in nacelles:
        for t in range(5):
            x = int(15.5 + (x0 - 15.5) * t / 5.0)
            y = int(15.5 + (y0 - 15.5) * t / 5.0)
            cv.set(x, y, G[2])
            cv.set(x + 1, y, G[1])
    for x0, y0 in nacelles:
        ring = cv.disc_m(x0, y0, 4.4) - cv.disc_m(x0, y0, 2.2)
        cv.mat(ring, G[1], G[4], G[6])
        cv.set(int(x0 - 2), int(y0), A[3])
        cv.set(int(x0 + 2), int(y0), A[3])
        cv.fill(cv.disc_m(x0, y0, 1.2), G[0])
        cv.set(int(x0), int(y0), C[4])
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            cv.set(int(x0 + dx), int(y0 + dy), G[5])
    cv.set(15, 8, R[3]); cv.set(16, 8, R[2])
    cv.outline()
    return cv


def flight_module_vtol_glide():
    cv = Canvas()
    fuse = cv.rows_m({
        3: (15, 16), 4: (15, 16), 5: (14, 17), 6: (14, 17),
        7: (13, 18), 8: (13, 18), 9: (13, 18), 10: (13, 18),
        11: (13, 18), 12: (13, 18), 13: (13, 18), 14: (14, 17),
        15: (14, 17), 16: (14, 17), 17: (14, 17), 18: (14, 17),
        19: (14, 17), 20: (15, 16), 21: (15, 16), 22: (15, 16),
        23: (15, 16), 24: (15, 16)
    })
    cv.mat(fuse, G[1], G[3], G[5])
    cv.fill(cv.rect_m(15, 6, 16, 9), C[3])
    cv.set(15, 6, C[4])
    for y in range(9, 23):
        x_left = 13 - int((y - 9) * 0.85)
        w = max(2, int((23 - y) * 0.7))
        for x in range(max(2, x_left - w), max(3, x_left + 1)):
            cv.set(x, y, G[3] if y % 2 == 0 else G[2])
        x_right = 18 + int((y - 9) * 0.85)
        for x in range(min(28, x_right), min(30, x_right + w + 1)):
            cv.set(x, y, G[3] if y % 2 == 0 else G[2])
    cv.fill(cv.rect_m(2, 17, 3, 23), G[4])
    cv.set(2, 17, R[3]); cv.set(2, 18, R[2])
    cv.fill(cv.rect_m(28, 17, 29, 23), G[4])
    cv.set(29, 17, N[3]); cv.set(29, 18, N[2])
    cv.vcyl(cv.rect_m(8, 14, 12, 24), G[1:6])
    cv.fill(cv.rect_m(9, 25, 11, 26), C[3])
    cv.set(10, 25, WHITE)
    cv.vcyl(cv.rect_m(19, 14, 23, 24), G[1:6])
    cv.fill(cv.rect_m(20, 25, 22, 26), C[3])
    cv.set(21, 25, WHITE)
    cv.outline()
    return cv


def weapon_mining_drill():
    cv = Canvas()
    stock_and_grip(cv, -26, -14, CC - 3, CC + 5, -12, CC + 5, CC + 12)
    dcyl_box(cv, -15, -2, CC - 7, CC + 7, G[0:6])
    for a in range(-14, -2, 2):
        dfill(cv, a, a, CC - 4, CC + 4, A[3])
    dcyl_box(cv, -2, 3, CC - 8, CC + 8, G[1:7])
    dfill(cv, -1, 1, CC - 7, CC + 7, G[5])
    for a in range(3, 24):
        half = max(1, int(7.0 * (1.0 - (a - 3) / 22.0)))
        for c in range(int(CC - half), int(CC + half + 1)):
            dist = abs(c - CC)
            is_flute = ((a + c) % 5 < 2)
            if is_flute:
                col = C[4] if dist <= 1 else G[1]
            elif c < CC:
                col = G[5]
            else:
                col = G[2]
            x = (a + c) // 2
            y = (c - a) // 2
            cv.set(x, y, col)
    dfill(cv, 23, 25, CC - 1, CC + 1, C[4])
    dfill(cv, 25, 26, CC, CC, WHITE)
    cv.outline()
    return cv


def ammo_mining_drill():
    cv = Canvas()
    cv.mat(cv.rect_m(4, 15, 27, 28), G[1], G[2], G[4])
    cv.vcyl(cv.rect_m(6, 4, 12, 17), C)
    cv.vcyl(cv.rect_m(14, 4, 20, 17), C)
    cv.fill(cv.rect_m(8, 6, 10, 15), WHITE)
    cv.fill(cv.rect_m(16, 6, 18, 15), WHITE)
    cv.set(9, 2, G[5]); cv.set(9, 3, G[1])
    cv.set(17, 2, G[5]); cv.set(17, 3, G[1])
    cv.vcyl(cv.rect_m(22, 6, 26, 17), G[2:7])
    for y in range(7, 16, 3):
        cv.set(23, y, C[4]); cv.set(24, y, C[4])
    for x in range(5, 27):
        cv.set(x, 21, A[3] if x % 2 == 0 else G[0])
    cv.outline()
    return cv


def weapon_light_smg():
    cv = Canvas()
    stock_and_grip(cv, -22, -13, CC - 2, CC + 4, -10, CC + 4, CC + 11)
    dcyl_box(cv, -13, 6, CC - 5, CC + 5, G[1:7])
    dfill(cv, -10, 4, CC - 2, CC - 2, A[3])          # amber recon stripe
    dfill(cv, -6, -2, CC + 5, CC + 12, G[1])          # straight box magazine
    dfill(cv, -6, -2, CC + 11, CC + 12, A[2])
    dcyl_box(cv, 6, 20, CC - 2, CC + 2, G[2:7])       # short barrel
    dcyl_box(cv, 18, 22, CC - 3, CC + 3, G[0:5])      # suppressor tip
    cv.outline()
    return cv


def ammo_light_smg():
    cv = Canvas()
    body = cv.rect_m(11, 5, 20, 28) - {(11, 5), (20, 5), (11, 28), (20, 28)}
    cv.mat(body, G[1], G[3], G[5])
    for y in range(7, 26, 3):
        cv.vcyl(cv.rect_m(13, y, 18, y + 1), A)
    cv.fill(cv.rect_m(12, 26, 19, 26), A[2])
    cv.outline()
    return cv


def weapon_chainsaw():
    cv = Canvas()
    stock_and_grip(cv, -26, -14, CC - 3, CC + 5, -12, CC + 5, CC + 12)
    dmat(cv, -14, -2, CC - 6, CC + 6, G[1], G[3], G[5])
    dmat(cv, -13, -11, CC - 10, CC - 7, G[2], G[4], G[6])
    for a in (-10, -7, -4):
        dfill(cv, a, a + 1, CC - 3, CC + 2, G[0])
    dfill(cv, -9, -3, CC + 3, CC + 5, A[3])
    bar_m = dm(-2, 22, CC - 4, CC + 4)
    cv.dcyl(bar_m, CC, 4, G[2:6])
    dfill(cv, 2, 18, CC - 1, CC + 1, G[0])
    for a in range(-2, 23, 2):
        cv.set((a + (CC - 5)) // 2, ((CC - 5) - a) // 2, C[4] if a % 4 == 0 else WHITE)
        cv.set((a + (CC + 5)) // 2, ((CC + 5) - a) // 2, G[6] if a % 4 == 0 else G[1])
    dfill(cv, 22, 24, CC - 3, CC + 3, G[1])
    dfill(cv, 23, 24, CC - 1, CC + 1, C[4])
    dfill(cv, 25, 25, CC - 2, CC + 2, G[5])
    cv.outline()
    return cv


def ammo_chainsaw():
    cv = Canvas()
    cv.mat(cv.rect_m(5, 7, 18, 27), G[1], G[3], G[5])
    cv.fill(cv.rect_m(7, 10, 16, 24), A[2])
    cv.fill(cv.rect_m(8, 12, 10, 22), A[4])
    cv.set(9, 3, G[4]); cv.fill(cv.rect_m(8, 4, 10, 6), G[2])
    roll = cv.disc_m(23.5, 17.5, 6.0) - cv.disc_m(23.5, 17.5, 2.0)
    cv.mat(roll, G[1], G[4], G[6])
    for x, y in cv.disc_m(23.5, 17.5, 7.0) - cv.disc_m(23.5, 17.5, 5.0):
        if (x + y) % 3 == 0:
            cv.set(x, y, C[4])
    cv.outline()
    return cv


ITEMS = {
    'flight_module_rocket_jetpack': flight_module_rocket_jetpack,
    'flight_module_drone_lifter': flight_module_drone_lifter,
    'flight_module_vtol_glide': flight_module_vtol_glide,

    'titan_battery': lambda: battery(True),
    'empty_battery': lambda: battery(False),
    'titan_ammo': titan_ammo,
    'fusion_reactor': fusion_reactor,
    'cockpit_module': cockpit_module,
    'chassis_frame': chassis_frame,
    'hydraulic_actuator': hydraulic_actuator,
    'weapon_mount': weapon_mount,
    'titan_drop_beacon': titan_drop_beacon,
    'trooper_beacon': lambda: titan_drop_beacon(O, N),
    'hangar_transponder': hangar_transponder,
    'pilot_license': pilot_license,
    'paint_spray_can': paint_spray_can,
    'blowtorch': blowtorch,
}
for _wid in WEAPON_IDS:
    ITEMS['weapon_' + _wid] = globals()['weapon_' + _wid]
for _wid in WEAPON_IDS:
    ITEMS['ammo_' + _wid] = globals()['ammo_' + _wid]


# --------------------------------------------------------------------------- contact sheet


def contact_sheet(canvases, path):
    """Preview: every item at 8x on inventory-grey slots, then all items at 1x and 2x."""
    names = list(canvases)
    S = 8
    cols = 7
    cell = W * S + 24
    rows = (len(names) + cols - 1) // cols
    sw = cols * cell + 8
    per1 = (sw - 8) // (W + 12)
    per2 = (sw - 8) // (2 * W + 10)
    r1 = (len(names) + per1 - 1) // per1
    r2 = (len(names) + per2 - 1) // per2
    sh = 8 + rows * cell + r1 * (W + 12) + 8 + r2 * (2 * W + 10) + 8
    bg = (198, 198, 198)
    img = [[bg] * sw for _ in range(sh)]

    def slot(x0, y0, size):
        for y in range(y0, y0 + size):
            for x in range(x0, x0 + size):
                tl = (y - y0 < 2) or (x - x0 < 2)
                br = (y0 + size - 1 - y < 2) or (x0 + size - 1 - x < 2)
                img[y][x] = (55, 55, 55) if tl and not br else (255, 255, 255) if br and not tl else (139, 139, 139)

    def blit(cv, x0, y0, s):
        for y in range(H):
            for x in range(W):
                c = cv.p[y][x]
                if c is None:
                    continue
                for yy in range(s):
                    for xx in range(s):
                        img[y0 + y * s + yy][x0 + x * s + xx] = c[:3]

    for i, n in enumerate(names):
        cx, cy = 8 + (i % cols) * cell, 8 + (i // cols) * cell
        slot(cx, cy, W * S + 16)
        blit(canvases[n], cx + 8, cy + 8, S)
    y1 = 8 + rows * cell
    for i, n in enumerate(names):
        x0, y0 = 8 + (i % per1) * (W + 12), y1 + (i // per1) * (W + 12)
        slot(x0, y0, W + 4)
        blit(canvases[n], x0 + 2, y0 + 2, 1)
    y2 = y1 + r1 * (W + 12) + 8
    for i, n in enumerate(names):
        x0, y0 = 8 + (i % per2) * (2 * W + 10), y2 + (i // per2) * (2 * W + 10)
        slot(x0, y0, 2 * W + 4)
        blit(canvases[n], x0 + 2, y0 + 2, 2)
    raw = bytearray()
    for row in img:
        raw.append(0)
        for c in row:
            raw.extend((c[0], c[1], c[2], 255))
    with open(path, 'wb') as f:
        f.write(encode_png(sw, sh, bytes(raw)))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, '..', 'src', 'main', 'resources', 'assets', 'titancombat', 'textures', 'item')
    sheet = None
    args = sys.argv[1:]
    if '--out' in args:
        out = args[args.index('--out') + 1]
    if '--sheet' in args:
        sheet = args[args.index('--sheet') + 1]
    os.makedirs(out, exist_ok=True)
    canvases = {}
    for name, fn in ITEMS.items():
        cv = fn()
        canvases[name] = cv
        with open(os.path.join(out, name + '.png'), 'wb') as f:
            f.write(cv.png())
        print('wrote', name)
    if sheet:
        if '--only' in args:
            pre = args[args.index('--only') + 1]
            canvases = {k: v for k, v in canvases.items() if k.startswith(tuple(pre.split(',')))}
        contact_sheet(canvases, sheet)
        print('sheet', sheet)


if __name__ == '__main__':
    main()
