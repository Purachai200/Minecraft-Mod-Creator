#!/usr/bin/env python3
import struct
import zlib
import os

def make_png(w, h, rgba_bytes):
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw.extend(rgba_bytes[y*w*4 : (y+1)*w*4])
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw), 9)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')

class Canvas:
    def __init__(self, w=32, h=32):
        self.w = w
        self.h = h
        self.buf = bytearray([0] * (w * h * 4))

    def set_px(self, x, y, r, g, b, a=255):
        if 0 <= x < self.w and 0 <= y < self.h:
            idx = (y * self.w + x) * 4
            self.buf[idx] = max(0, min(255, int(r)))
            self.buf[idx+1] = max(0, min(255, int(g)))
            self.buf[idx+2] = max(0, min(255, int(b)))
            self.buf[idx+3] = max(0, min(255, int(a)))

    def fill_rect(self, x0, y0, w, h, r, g, b, a=255):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                self.set_px(x, y, r, g, b, a)

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(make_png(self.w, self.h, self.buf))
        print(f"Saved: {path}")

def generate_heavy_battery():
    c = Canvas(32, 32)
    # Terminals (X=8..12, X=20..24, Y=2..5)
    c.fill_rect(8, 2, 5, 4, 180, 130, 40)
    c.fill_rect(9, 3, 3, 2, 230, 190, 70)
    c.fill_rect(19, 2, 5, 4, 180, 130, 40)
    c.fill_rect(20, 3, 3, 2, 230, 190, 70)

    # Main Body Outer Shell (X=5..27, Y=6..29)
    c.fill_rect(5, 6, 22, 24, 25, 28, 32) # Dark outline
    c.fill_rect(6, 7, 20, 22, 48, 54, 62) # Heavy steel casing
    # Bevel highlight
    c.fill_rect(6, 7, 20, 1, 95, 105, 120)
    c.fill_rect(6, 7, 1, 22, 95, 105, 120)
    c.fill_rect(25, 8, 1, 21, 20, 22, 26)
    c.fill_rect(6, 28, 20, 1, 20, 22, 26)

    # Center Dual Heavy Plasma Cells (X=9..14, X=17..22, Y=11..24)
    for x_cell in (9, 17):
        c.fill_rect(x_cell, 10, 6, 15, 15, 20, 25) # Cell border
        c.fill_rect(x_cell+1, 11, 4, 13, 0, 180, 220) # Plasma
        c.fill_rect(x_cell+2, 12, 2, 11, 120, 240, 255) # Plasma core highlight

    # Center separator & Reinforcement ribs
    c.fill_rect(15, 8, 2, 20, 30, 34, 40)
    c.fill_rect(6, 17, 20, 2, 30, 34, 40)

    # Corner steel rivets
    for rx, ry in ((7, 8), (24, 8), (7, 27), (24, 27)):
        c.set_px(rx, ry, 200, 210, 225)

    c.save("Titan Combat/src/main/resources/assets/titancombat/textures/item/heavy_titan_battery.png")

def generate_dense_fusion_battery():
    c = Canvas(32, 32)
    # Heavy Gold/Copper Quad Terminals (Y=1..4)
    for tx in (6, 12, 18, 24):
        c.fill_rect(tx, 1, 3, 4, 210, 140, 30)
        c.set_px(tx+1, 2, 255, 220, 90)

    # Armored Tungsten Outer Shell (X=4..28, Y=5..30)
    c.fill_rect(4, 5, 24, 26, 20, 18, 22) # Outline
    c.fill_rect(5, 6, 22, 24, 38, 36, 42) # Tungsten plate
    c.fill_rect(5, 6, 22, 1, 180, 140, 45) # Gold rim top
    c.fill_rect(5, 29, 22, 1, 180, 140, 45) # Gold rim bottom

    # Yellow/Black Hazard Stripes on top & bottom bar
    for i in range(20):
        col = (245, 185, 15) if (i // 2) % 2 == 0 else (25, 25, 28)
        c.set_px(6 + i, 8, *col)
        c.set_px(6 + i, 27, *col)

    # Central Superdense Antimatter Core (X=8..24, Y=11..24)
    c.fill_rect(8, 10, 16, 15, 15, 12, 18)
    # High-intensity pulsating fusion core
    c.fill_rect(9, 11, 14, 13, 230, 110, 0)
    c.fill_rect(10, 12, 12, 11, 255, 190, 20)
    c.fill_rect(12, 14, 8, 7, 255, 255, 180)
    # Magnetic containment cross
    c.fill_rect(15, 11, 2, 13, 0, 220, 255)
    c.fill_rect(9, 17, 14, 2, 0, 220, 255)

    c.save("Titan Combat/src/main/resources/assets/titancombat/textures/item/dense_fusion_battery.png")

if __name__ == "__main__":
    generate_heavy_battery()
    generate_dense_fusion_battery()
