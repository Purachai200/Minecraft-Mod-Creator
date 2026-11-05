#!/usr/bin/env python3
"""Magic circle VFX texture and ammo slot icons.

  python3 tools/generate_magic_circle.py      (run from the "Youjo Senki Arms" folder)

The circle is drawn white on transparent: MagicCircleRenderer tints it with the formula colour and draws it
additively, so brightness = glow. Rendered at 2x and downsampled for smooth lines.
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter

VFX = "src/main/resources/assets/youjoarms/textures/vfx/magic_circle.png"
AMMO = "src/main/resources/tacz_youjoarms/assets/youjoarms/textures/ammo/slot"


def glyph(d, cx, cy, s, ang, rng, w):
    """A made-up rune: 2-4 strokes on a 3x3 grid, rotated to face the circle centre."""
    pts = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ca, sa = math.cos(ang), math.sin(ang)

    def tp(p):
        x, y = p[0] * s * 0.5, p[1] * s
        return cx + x * ca - y * sa, cy + x * sa + y * ca
    d.line([tp(pts[1]), tp(pts[7])], fill=255, width=w)  # spine
    for _ in range(rng.randint(1, 3)):
        a, b = rng.sample(pts, 2)
        d.line([tp(a), tp(b)], fill=255, width=w)


class Canvas:
    """2x supersampled white-on-black line canvas; finish() turns brightness into a glowing alpha mask."""

    def __init__(self, size=512):
        self.size, self.S = size, size * 2
        self.img = Image.new("L", (self.S, self.S), 0)
        self.d = ImageDraw.Draw(self.img)
        self.c = self.S / 2

    def pt(self, r, a):
        return self.c + r * math.cos(a), self.c + r * math.sin(a)

    def ring(self, r, w):
        c = self.c
        self.d.ellipse([c - r, c - r, c + r, c + r], outline=255, width=w)

    def dot(self, r, a, rad, fill=True, w=4):
        x, y = self.pt(r, a)
        box = [x - rad, y - rad, x + rad, y + rad]
        self.d.ellipse(box, fill=255) if fill else self.d.ellipse(box, outline=255, width=w)

    def spokes(self, r1, r2, n, w, every=1, off=0.0):
        for i in range(0, n, every):
            a = i / n * math.tau + off
            self.d.line([self.pt(r1, a), self.pt(r2, a)], fill=255, width=w)

    def star(self, r, points, step, w, off=-math.pi / 2):
        pts = [self.pt(r, off + k * math.tau / points) for k in range(points)]
        for k in range(points):
            self.d.line([pts[k], pts[(k + step) % points]], fill=255, width=w)

    def runes(self, r, n, size, w, seed):
        rng = random.Random(seed)
        for i in range(n):
            a = i / n * math.tau
            x, y = self.pt(r, a)
            glyph(self.d, x, y, size, a + math.pi / 2, rng, w)

    def finish(self, blur=10):
        lines = self.img.resize((self.size, self.size), Image.LANCZOS)
        glow = lines.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: min(255, v * 2))
        halo = lines.filter(ImageFilter.GaussianBlur(3))
        alpha = Image.merge("RGB", (lines, glow, halo)).convert("L").point(lambda v: min(255, int(v * 1.4)))
        return Image.merge("RGBA", (Image.new("L", (self.size, self.size), 255),) * 3 + (alpha,))


def circle():
    """Main circle: double outer ring, rune band, tick ring, hexagram, centre star."""
    k = Canvas()
    r0 = k.S / 2 - 12
    k.ring(r0, 10); k.ring(r0 - 22, 4); k.ring(r0 - 96, 6); k.ring(r0 - 112, 3)
    k.runes(r0 - 59, 30, 30, 5, 203)
    for i in range(72):
        a = i / 72 * math.tau
        k.d.line([k.pt(r0 - 112, a), k.pt(r0 - (140 if i % 6 == 0 else 124), a)], fill=255, width=4)
    rh = r0 - 150
    k.star(rh, 6, 2, 7)
    k.ring(rh, 5); k.ring(rh * 0.5, 6); k.ring(rh * 0.5 - 16, 3)
    for j in range(6):
        a = j * math.tau / 6 - math.pi / 2
        k.dot(rh, a, 22, fill=False, w=5); k.dot(rh, a, 6)
    rs = rh * 0.5 - 30
    pts = [k.pt(rs if j % 2 == 0 else rs * 0.42, j * math.tau / 16) for j in range(16)]
    k.d.polygon(pts, outline=255, width=5)
    k.dot(0, 0, 18)
    return k.finish()


def gear():
    """Clockwork circle: toothed rim, 12 hour glyphs, nested rings and a cross."""
    k = Canvas()
    r0 = k.S / 2 - 14
    teeth = 48
    rim = []
    for i in range(teeth * 2):
        a = i / (teeth * 2) * math.tau
        r = r0 if (i // 1) % 2 == 0 else r0 - 22
        rim += [k.pt(r, a - math.tau / (teeth * 4)), k.pt(r, a + math.tau / (teeth * 4))]
    k.d.polygon(rim, outline=255, width=6)
    k.ring(r0 - 40, 5); k.ring(r0 - 130, 5)
    k.runes(r0 - 85, 12, 46, 7, 77)
    k.spokes(r0 - 130, r0 - 40, 12, 3, off=math.pi / 12)
    k.ring(r0 * 0.42, 8); k.ring(r0 * 0.42 - 18, 3)
    k.spokes(0, r0 * 0.42, 4, 10, off=math.pi / 4)
    k.spokes(r0 * 0.42, r0 - 130, 24, 2)
    k.dot(0, 0, 30, fill=False, w=8)
    return k.finish()


def seal():
    """Seal: heptagram in a double ring, orbiting small circles, inner rune ring."""
    k = Canvas()
    r0 = k.S / 2 - 12
    k.ring(r0, 8); k.ring(r0 - 16, 3)
    rs = r0 - 70
    k.star(rs, 7, 3, 6)
    k.star(rs, 7, 2, 3)
    k.ring(rs, 4)
    for j in range(7):
        a = -math.pi / 2 + j * math.tau / 7
        k.dot(r0 - 42, a + math.tau / 14, 24, fill=False, w=5)
        x, y = k.pt(r0 - 42, a + math.tau / 14)
        glyph(k.d, x, y, 22, a, random.Random(j), 4)
    k.ring(rs * 0.38, 6)
    k.runes(rs * 0.38 - 34, 10, 22, 4, 9)
    k.ring(rs * 0.38 - 68, 3)
    return k.finish()


def lens():
    """Lens: thin concentric rings, long radial spokes, diamonds; the light 'sight' circles in front of the stack."""
    k = Canvas()
    r0 = k.S / 2 - 10
    for r, w in ((r0, 5), (r0 - 10, 2), (r0 * 0.78, 3), (r0 * 0.55, 6), (r0 * 0.3, 3)):
        k.ring(r, w)
    k.spokes(r0 * 0.3, r0 - 10, 8, 4)
    k.spokes(r0 * 0.55, r0 * 0.78, 64, 2)
    for j in range(8):
        a = j * math.tau / 8 + math.tau / 16
        x, y = k.pt(r0 * 0.665, a)
        s = 20
        k.d.polygon([(x, y - s), (x + s * 0.6, y), (x, y + s), (x - s * 0.6, y)], outline=255, width=4)
    k.runes(r0 * 0.89, 40, 18, 3, 31)
    return k.finish(blur=8)


def glow(size=128):
    """Soft radial glow sprite for the circle cores."""
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    px = img.load()
    for y in range(size):
        for x in range(size):
            d = math.hypot(x + 0.5 - size / 2, y + 0.5 - size / 2) / (size / 2)
            px[x, y] = (255, 255, 255, int(255 * max(0.0, 1 - d) ** 2.2))
    return img


def beam(w=64, h=256):
    """Vertical beam strip: bright core across the width, fading at the top."""
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    px = img.load()
    for y in range(h):
        for x in range(w):
            across = 1 - abs(x + 0.5 - w / 2) / (w / 2)
            px[x, y] = (255, 255, 255, int(255 * across ** 1.6 * (0.35 + 0.65 * (y / h))))
    return img


def cartridge_icon(rounds, tip, glow=False, big=False):
    """32x32 pixel-art cartridge(s) pointing up-right, like vanilla tool icons."""
    S = 32
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    px = img.load()
    case, case_d, case_l = (204, 158, 70), (138, 98, 36), (242, 214, 140)
    length, rad = (40, 4.4) if big else (28, 2.2)
    for k in range(rounds):  # each round lies along the up-right diagonal; t = along, r = across
        ox, oy = (2 + 4 * k, 18 + 4 * k) if rounds > 1 else (5, 26)  # side by side across the diagonal
        for y in range(S):
            for x in range(S):
                rx, ry = x + 0.5 - ox, y + 0.5 - oy
                t, r = (rx - ry) / 2, (rx + ry) / 2
                if not (0 <= t < length / 2):
                    continue
                f = t / (length / 2)
                w = rad * 0.75
                if f < 0.1:
                    col = case_d  # rim
                elif f < 0.62:
                    col = case_l if r < -w * 0.4 else case_d if r > w * 0.5 else case
                else:
                    w *= 1 - (f - 0.62) / 0.38 * 0.8
                    col = tuple(min(255, v + 60) for v in tip) if r < -w * 0.3 else tip
                if abs(r) <= w:
                    px[x, y] = col + (255,)
    if glow:  # elenium shimmer around the tips
        g = img.split()[3].filter(ImageFilter.MaxFilter(3))
        aura = Image.new("RGBA", (S, S), (90, 230, 255, 0))
        aura.putalpha(g.point(lambda v: 110 if v else 0))
        aura.alpha_composite(img)
        img = aura
    # 1px dark outline
    a = img.split()[3].point(lambda v: 255 if v > 0 else 0).filter(ImageFilter.MaxFilter(3))
    out = Image.new("RGBA", (S, S), (24, 18, 12, 0))
    out.putalpha(a.point(lambda v: 255 if v else 0))
    out.alpha_composite(img)
    return out


if __name__ == "__main__":
    vfx = os.path.dirname(VFX)
    os.makedirs(vfx, exist_ok=True)
    for name, fn in (("magic_circle", circle), ("circle_gear", gear), ("circle_seal", seal), ("circle_lens", lens),
                     ("glow", glow), ("beam", beam)):
        fn().save(f"{vfx}/{name}.png")
    os.makedirs(AMMO, exist_ok=True)
    cartridge_icon(3, (184, 104, 66)).save(f"{AMMO}/7_92x57.png")
    cartridge_icon(3, (90, 230, 255), glow=True).save(f"{AMMO}/7_92x57_elenium.png")
    cartridge_icon(1, (170, 110, 70), big=True).save(f"{AMMO}/13mm.png")
    cartridge_icon(2, (190, 120, 70)).save(f"{AMMO}/8x50r.png")
    cartridge_icon(3, (196, 112, 84)).save(f"{AMMO}/303.png")
    print("wrote vfx textures and ammo icons")
