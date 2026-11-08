"""Walkable interiors: walls with doors/windows, slabs with stair holes, stairs and furnished rooms.
Rules of thumb (px): player ~29 tall, ~10 wide -> doors 14 x 30, clear height >= 32, aisle >= 14, stair rise <= 5 per step."""
from fleet_common import *

T = 1.6
DOOR_H = 30


def _nz(boxes): return [b for b in boxes if all(v > 0.05 for v in b["size"])]


def wz(s, x, y0, y1, z0, z1, opens=(), mat=HULL, t=T):
    """Wall on side s at |x| (outer plane), running along z. opens = (za, zb, ya, yb, 'door'|'win')."""
    out, z = [], z0
    for za, zb, ya, yb, k in sorted(opens):
        za, zb = max(za, z0), min(zb, z1)
        if za > z: out.append(wall(s, x - t, x, y0, y1, z, za, mat))
        if ya > y0: out.append(wall(s, x - t, x, y0, ya, za, zb, mat))
        if yb < y1: out.append(wall(s, x - t, x, yb, y1, za, zb, mat))
        if k == "win": out.append(box(s * (x - t * 0.6), ya, za, s * (x - t * 0.4), yb, zb, GLASS))
        z = zb
    if z < z1: out.append(wall(s, x - t, x, y0, y1, z, z1, mat))
    return _nz(out)


def wx(z, x0, x1, y0, y1, opens=(), mat=HULL, t=T, ext=None):
    """Wall across the ship at z (occupies z-t..z). ext = 'north'|'south' keeps that face as exterior paint."""
    def b(a, c, ya, yb):
        f = {"north": INTER, "south": INTER}
        if ext: f.pop(ext)
        return box(a, ya, z - t, c, yb, z, mat, **f)
    out, x = [], x0
    for xa, xb, ya, yb, k in sorted(opens):
        xa, xb = max(xa, x0), min(xb, x1)
        if xa > x: out.append(b(x, xa, y0, y1))
        if ya > y0: out.append(b(xa, xb, y0, ya))
        if yb < y1: out.append(b(xa, xb, yb, y1))
        if k == "win": out.append(box(xa, ya, z - t * 0.6, xb, yb, z - t * 0.4, GLASS))
        x = xb
    if x < x1: out.append(b(x, x1, y0, y1))
    return _nz(out)


def slab(x0, x1, z0, z1, y, t=2, hole=None, top=WALK, bot=INTER):
    f = lambda a0, a1, c0, c1: box(a0, y, c0, a1, y + t, c1, DARK, up=top, down=bot)
    if not hole: return [f(x0, x1, z0, z1)]
    hx0, hx1, hz0, hz1 = hole
    return _nz([f(x0, hx0, z0, z1), f(hx1, x1, z0, z1), f(hx0, hx1, z0, hz0), f(hx0, hx1, hz1, z1)])


def stairs(x0, x1, z_lo, z_hi, y_lo, y_hi, n=8):
    """Solid steps rising toward +z, with handrails."""
    out, rz, rh = [], (z_hi - z_lo) / n, (y_hi - y_lo) / n
    for i in range(n): out.append(box(x0, y_lo, z_lo + i * rz, x1, y_lo + rh * (i + 1), z_lo + (i + 1) * rz, DARK, up=WALK))
    for x in (x0, x1):
        out.append(tube((x, y_lo + 11, z_lo), (x, y_hi + 11, z_hi), 1.0, SPIN))
        out += [tube((x, y_lo + rh * (i + 1), z_lo + (i + 0.5) * rz), (x, y_lo + rh * (i + 1) + 11, z_lo + (i + 0.5) * rz), 0.8, SPIN) for i in (0, n - 1)]
    return out


# ---------------------------------------------------------------- furniture
def bunk(x, y, z, L=34, W=13, lvl=2):
    out = [tube((x + a * W / 2, y, z + b * L / 2), (x + a * W / 2, y + 12 * lvl + 4, z + b * L / 2), 1.3, DARK) for a in (-1, 1) for b in (-1, 1)]
    for k in range(lvl):
        yy = y + 5 + 12 * k
        out += [box(x - W / 2, yy, z - L / 2, x + W / 2, yy + 2.5, z + L / 2, INTER), box(x - W / 2 + 0.5, yy + 2.5, z - L / 2 + 6, x + W / 2 - 0.5, yy + 4, z + L / 2 - 0.5, DARK),
                box(x - W / 2 + 1.5, yy + 2.5, z - L / 2 + 0.6, x + W / 2 - 1.5, yy + 4.2, z - L / 2 + 5.4, WHITE)]
    return out


def table(x, y, z, lx, lz):
    out = [box(x - lx / 2, y + 9, z - lz / 2, x + lx / 2, y + 10.6, z + lz / 2, DARK, up=SPIN)]
    out += [box(x + a * (lx / 2 - 1.6) - 0.8, y, z + b * (lz / 2 - 1.6) - 0.8, x + a * (lx / 2 - 1.6) + 0.8, y + 9, z + b * (lz / 2 - 1.6) + 0.8, DARK) for a in (-1, 1) for b in (-1, 1)]
    for a in (-1, 1): out.append(box(x + a * (lx / 2 + 3) - 2.5, y + 5, z - lz / 2 + 1, x + a * (lx / 2 + 3) + 2.5, y + 7, z + lz / 2 - 1, INTER))
    for a in (-1, 1): out += [box(x + a * (lx / 2 + 3) - 0.8, y, zz - 0.8, x + a * (lx / 2 + 3) + 0.8, y + 5, zz + 0.8, DARK) for zz in (z - lz / 2 + 2, z + lz / 2 - 2)]   # bench legs
    return out


def counter(x, y, z, lx, lz, stove=False):
    out = [box(x - lx / 2, y, z - lz / 2, x + lx / 2, y + 9, z + lz / 2, SPIN), box(x - lx / 2, y + 9, z - lz / 2, x + lx / 2, y + 10, z + lz / 2, DARK)]
    if stove: out += [box(x - 3 + dx, y + 10, z - 3 + dz, x + 0 + dx, y + 10.6, z + dz, SOOT) for dx in (-3, 3) for dz in (-5, 5)]
    return out


def locker(x, y, z, lx=7, lz=7, h=24): return [box(x - lx / 2, y, z - lz / 2, x + lx / 2, y + h, z + lz / 2, DARK), box(x - lx / 2 - 0.2, y + 1, z - lz / 2 + 1, x + lx / 2 + 0.2, y + h - 1, z + lz / 2 - 1, DOOR)]


def crate(x, y, z, a=9, h=9): return [box(x - a / 2, y, z - a / 2, x + a / 2, y + h, z + a / 2, DARK), box(x - a / 2 - 0.1, y + 1, z - a / 2 + 1, x + a / 2 + 0.1, y + h - 1, z + a / 2 - 1, DOOR)]


def engine(x, y, z, lx, lz):
    out = [box(x - lx / 2, y, z - lz / 2, x + lx / 2, y + 7, z + lz / 2, DARK), box(x - lx / 2 + 1, y + 7, z - lz / 2 + 2, x + lx / 2 - 1, y + 20, z + lz / 2 - 2, SPIN),
           box(x - lx / 2 + 2, y + 20, z - lz / 2 + 3, x + lx / 2 - 2, y + 24, z + lz / 2 - 3, DARK)]
    out += [box(x - lx / 2 + 2.5, y + 24, z - lz / 2 + 4 + 8 * i, x + lx / 2 - 2.5, y + 28, z - lz / 2 + 9 + 8 * i, DARK) for i in range(max(1, int(lz // 9) - 1))]
    out += [tube((x - lx / 4, y + 24, z), (x - lx / 4, y + 31, z), 3, SOOT), box(x + lx / 2 - 3, y + 12, z - 1, x + lx / 2 - 1.6, y + 15, z + 1, RED)]
    return out


def console(x, y, z, w, face=-1):
    return [box(x - w / 2, y, z - 3.5, x + w / 2, y + 9, z + 3.5, DARK), rbox(x, y + 11, z + face * 0.4, w - 1, 0.8, 7, [-30 * face, 0, 0], INTER),
            box(x - w / 2 + 1, y + 13, z + 1.5 * -face, x + w / 2 - 1, y + 17, z + 2.4 * -face, INTER)]


def bed_desk(x, y, z):
    return [box(x - 7, y + 5, z - 17, x + 7, y + 8, z + 17, INTER), box(x - 6.5, y + 8, z - 5, x + 6.5, y + 9.5, z + 16, DARK), box(x - 6, y + 8, z - 16.5, x + 6, y + 10, z - 8, WHITE),
            box(x - 7, y, z - 17, x - 6, y + 5, z - 16, DARK), box(x + 6, y, z + 16, x + 7, y + 5, z + 17, DARK)]


def head(x, y, z): return [box(x - 3, y, z - 3, x + 3, y + 7, z + 3, WHITE), box(x - 3, y + 7, z - 3, x + 3, y + 14, z - 2, WHITE), box(x - 3.4, y + 12, z + 5, x + 3.4, y + 14, z + 7, SPIN)]


def furnish(kind, hwr, y, z0, z1, side_only=None):
    """Furniture for a room (floor at y, usable half width hwr, z0..z1). Keeps |x| < 8 clear for the aisle / doors."""
    out, both = [], hwr >= 30
    sides = (-1, 1) if (both and not side_only) else (side_only or 1,)
    zc = lambda lo, hi, step: [lo + step / 2 + i * step for i in range(int((hi - lo) // step))]
    xo = hwr - 7                                   # centre of an item hugging the wall
    if kind == "bunks":
        for s in sides:
            for z in zc(z0 + 2, z1 - 2, 38): out += bunk(s * xo, y, z)
    elif kind == "mess":
        for s in sides[:1]:
            for z in zc(z0 + 2, z1 - 14, 26): out += table(s * (xo - 3), y, z, 14, 22)
        for s in sides[-1:]:
            out += counter(-s * (hwr - 5), y, z0 + 14, 8, 22, True) + counter(-s * (hwr - 5), y, z0 + 36, 8, 14) if z1 - z0 > 42 else counter(-s * (hwr - 5), y, (z0 + z1) / 2, 8, 20, True)
    elif kind == "engine":
        for s in sides: out += engine(s * (hwr / 2 + 4), y, (z0 + z1) / 2, min(hwr - 10, 22), z1 - z0 - 12)
        out += [tube((x, y + 2, z0 + 3), (x, y + 2, z1 - 3), 1.6, SPIN) for x in (-hwr + 0.2, hwr - 0.2)]
    elif kind == "stores":
        for s in sides:
            for z in zc(z0 + 2, z1 - 2, 10): out += crate(s * (xo - 2), y, z) + crate(s * (xo - 2), y + 9, z, 8, 8)
    elif kind in ("officers", "cabins"):
        for s in sides:
            for z in zc(z0 + 2, z1 - 2, 38): out += bed_desk(s * (hwr - 8), y, z)
    elif kind == "bridge":
        for x in ([side_only * hwr * 0.5] if side_only else (-hwr * 0.55, 0, hwr * 0.55)): out += console(x, y, z0 + 8, min(16, hwr * 0.5))
        out += [box(-2, y, z0 + 18, 2, y + 9, z0 + 22, DARK), box(-4, y + 9, z0 + 17, 4, y + 11, z0 + 23, INTER), box(-1, y + 11, z0 + 22, 1, y + 22, z0 + 23.4, INTER)]   # helm chair
    elif kind == "hangar":
        out += [box(s * (hwr - 5) - 4, y, z0 + 5, s * (hwr - 5) + 4, y + 9, z1 - 5, DARK, up=SPIN) for s in (1,)]
        out += crate(-(hwr - 8), y, z0 + 8) + crate(-(hwr - 8), y, z0 + 18, 7, 12) + [box(-hwr + 4, y, z1 - 12, -hwr + 11, y + 9, z1 - 4, RED)]
    return out


def room(z0, z1, hwr, y, y1, kind, doors_x=(-7, 7), bulkhead_z0=True):
    """Hull compartment: bulkhead at z0 with a centre door + furniture."""
    out = wx(z0 + 0.0, -hwr - 3, hwr + 3, y, y1, [(doors_x[0], doors_x[1], y, y + DOOR_H, "door")]) if bulkhead_z0 else []
    return out + furnish(kind, hwr, y, z0 + T, z1)


def step_run(axis, a_from, a_to, o0, o1, y_base, top_from, top_to, n):
    """Solid steps along z (axis=2) or x (axis=0): step i spans its share of a_from..a_to and is topped at top_from + (top_to-top_from)*(i+1)/n."""
    out = []
    for i in range(n):
        lo, hi = sorted((a_from + (a_to - a_from) * i / n, a_from + (a_to - a_from) * (i + 1) / n)); top = top_from + (top_to - top_from) * (i + 1) / n
        out.append(box(lo, y_base, o0, hi, top, o1, DARK, up=WALK) if axis == 0 else box(o0, y_base, lo, o1, top, hi, DARK, up=WALK))
    return out
