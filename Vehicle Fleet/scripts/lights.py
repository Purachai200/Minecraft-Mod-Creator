"""Ceiling lamps for every enclosed, walkable space. Lamps are found by walking the interior (collision.reach) and looking for a
ceiling just above head height, so a lamp exists wherever a player can stand indoors and nowhere outdoors.
add_lamps() appends a 'lamps' bone (LAMP material, which the glow mask makes emissive) and returns light positions for lights/<id>.json."""
import collision as C
from fleet_common import *

GRID, MIN_GAP, HANG = 48, 30, 1.2     # one lamp per ~3 blocks, hanging on whatever ceiling is within 110 px above head height


def add_lamps(bones, meta):
    static, _ = C.solid_boxes(bones); S = C.PlayerSolver(static)
    entry = C.walk_test(meta, S)["entry"]
    if not entry: return []
    seen = C.reach(S, tuple(entry)); groups = {}
    for x, y, z in seen.values(): groups.setdefault((round(x / GRID), round(z / GRID), round(y / 24)), (x, y, z))
    lamps = []
    for x, y, z in groups.values():
        head = y + C.PLAYER_H
        ceil = [b[1] for b in S.near(x, z, 8) if b[1] >= head - 0.1 and b[1] <= head + 110 and b[0] < x + 6 and b[3] > x - 6 and b[2] < z + 6 and b[5] > z - 6]
        if not ceil: continue
        yl = min(ceil) - HANG
        if any(abs(lx - x) < MIN_GAP and abs(lz - z) < MIN_GAP and abs(ly - yl) < 24 for lx, ly, lz in lamps): continue
        lamps.append((round(x, 1), round(yl, 1), round(z, 1)))
    cubes = []
    for x, yl, z in lamps:
        cubes += [box(x - 3.2, yl + HANG - 0.5, z - 3.2, x + 3.2, yl + HANG, z + 3.2, DARK), box(x - 2.6, yl, z - 2.6, x + 2.6, yl + HANG - 0.5, z + 2.6, LAMP)]
    main = next(b["name"] for b in bones if b.get("cubes"))
    if cubes: bones.append(bone("lamps", main, [0, 0, 0], cubes))
    return lamps
