"""16x16 textures for the Vehicle Assembly Bay block. Run from project root."""
import random, sys
sys.path.insert(0, "scripts")
from generate_transport_assets import make_png

OUT = "src/main/resources/assets/titancombat/textures/block/"


def tex(name, fn):
    rnd = random.Random(name)
    px = bytearray()
    for y in range(16):
        for x in range(16):
            r, g, b = fn(x, y)
            n = rnd.randint(-6, 6)  # paint grain
            px += bytes([max(0, min(255, r + n)), max(0, min(255, g + n)), max(0, min(255, b + n)), 255])
    open(OUT + name + ".png", "wb").write(make_png(16, 16, px))


def steel(x, y):
    edge = x in (0, 15) or y in (0, 15)
    return (70, 76, 82) if edge else (112, 118, 124)


def top(x, y):
    if x in (0, 15) or y in (0, 15):
        return (230, 190, 30) if (x + y) % 4 < 2 else (30, 30, 30)  # hazard border
    if x in (4, 11) or y in (4, 11):
        return (160, 166, 170)  # turntable grid
    return (88, 94, 100)


def side(x, y):
    if y >= 13:
        return (230, 190, 30) if (x + y) % 4 < 2 else (30, 30, 30)
    if 2 <= x <= 13 and 2 <= y <= 9:  # blueprint terminal
        if x in (2, 13) or y in (2, 9):
            return (40, 44, 48)
        return (40, 140, 210) if (x * 3 + y) % 5 else (150, 220, 255)
    return steel(x, y)


tex("vehicle_assembly_bay_top", top)
tex("vehicle_assembly_bay_side", side)
tex("vehicle_assembly_bay_bottom", steel)
print("ok")
