#!/usr/bin/env python3
"""Collision export + walkability test for the Vehicle Fleet interiors.

  python collision.py                 export assets/vehiclefleet/collision/<id>.json for every vehicle and run the walk test
  python collision.py opv corvette    only these (registry short names)
  python collision.py --no-test       export only

What the export is: every solid cube in the vehicle's rest pose as axis-aligned boxes in model px (16 px = 1 block, +X left,
nose -Z). Moving parts (wheels, rotors, turrets, sling, cranes) are left out; doors / ramps / gates / tailgates / drop sides go into
"dynamic" (closed pose) and are NOT in "static", i.e. the walk test treats them as open.
What the test is: PlayerSolver below, a reference implementation of the interior physics the Java side should port. It walks a
9.6 x 28.8 px player (0.6 x 1.8 blocks) with step height 9.6 px (0.6 block) from an entry deck and reports which deck regions
and seats can be reached. Falling into a hatch does not count as a path.
"""
import itertools, json, math, os, sys
from fleet_common import *

PLAYER_W, PLAYER_H, STEP = 9.6, 28.8, 9.6
SKIP = ("wheel", "steer", "main_rotor", "main_blade", "tail_rotor", "prop", "radar", "sling", "cargo_straps", "turret", "beacon",
        "crane_hook", "crane_boom", "derrick_boom", "derrick_hook", "crane_base", "pylon", "outrigger")
DYNAMIC = ("door", "ramp", "gate", "tailgate", "drop_side")


def _corners(c, o, s, chain, pose):
    pts = []
    for k in itertools.product((0, 1), repeat=3):
        p = [o[i] + k[i] * s[i] for i in range(3)]
        if "rotation" in c: p = about(p, c["pivot"], c["rotation"])
        for bb in chain:
            r = pose.get(bb["name"])
            if r: p = about(p, bb["pivot"], r)
        pts.append(p)
    return pts


def solid_boxes(bones):
    """-> (static boxes, {dynamic bone: boxes}); boxes are [x0,y0,z0,x1,y1,z1] in px."""
    by = {b["name"]: b for b in bones}; pose = rest_pose(bones); static, dyn = [], {}
    for b in bones:
        n = b["name"]
        if any(n.startswith(p) for p in SKIP): continue
        chain, m = [], n
        while m: chain.append(by[m]); m = by[m].get("parent")
        if any(any(x in a["name"] for x in SKIP) for a in chain): continue
        out = dyn.setdefault(n, []) if any(d in n for d in DYNAMIC) or any(any(d in a["name"] for d in DYNAMIC) for a in chain) else static
        for c in b.get("cubes", []):
            o, s = c["origin"], c["size"]; d = sorted(s)
            if not (d[0] >= 3 or (d[1] >= 8 and d[2] >= 8 and d[0] >= 0.3) or (d[0] >= 1.5 and d[1] >= 3 and d[2] >= 8) or (c.get("mat") == GLASS and d[1] >= 8)): continue   # last clause: low stair treads
            rot = [abs(v) > 0.01 for v in c.get("rotation", [0, 0, 0])]
            if sum(rot) > 1: continue                                             # tilted tubes / panes: not walkable geometry
            pieces = [(o, s)]
            if sum(rot) == 1:                                                     # single-axis tilt: staircase of short pieces along its long in-plane side
                ax = rot.index(True); L = max((i for i in range(3) if i != ax), key=lambda i: s[i]); n_p = max(1, math.ceil(s[L] / 4))
                pieces = []
                for q in range(n_p):
                    po, ps = list(o), list(s); ps[L] = s[L] / n_p; po[L] = o[L] + q * ps[L]; pieces.append((po, ps))
            for po, ps in pieces:
                pts = _corners(c, po, ps, chain, pose)
                lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
                for i in (0, 2):                                                      # thin walls / glass still block; floors keep their true height
                    if hi[i] - lo[i] < 1.6: mid = (hi[i] + lo[i]) / 2; lo[i], hi[i] = mid - 0.8, mid + 0.8   # thin glass / plates still block
                out.append([round(v, 3) for v in lo + hi])
    return merge(static), {k: merge(v) for k, v in dyn.items() if v}


def merge(boxes):
    """Greedy merge of boxes that share the same xy extent and touch along z (hull slices collapse to one box)."""
    groups = {}
    for b in boxes: groups.setdefault((round(b[0], 2), round(b[1], 2), round(b[3], 2), round(b[4], 2)), []).append(b)
    out = []
    for g in groups.values():
        g.sort(key=lambda b: b[2]); cur = list(g[0])
        for b in g[1:]:
            if b[2] <= cur[5] + 0.05: cur[5] = max(cur[5], b[5])
            else: out.append(cur); cur = list(b)
        out.append(cur)
    return out


class PlayerSolver:
    """Reference interior physics (port to Java): axis-aligned player vs. vehicle-local boxes, step-up <= STEP."""
    CELL = 16.0

    def __init__(self, boxes):
        self.boxes, self.grid = boxes, {}
        for i, b in enumerate(boxes):
            for gx in range(int(b[0] // self.CELL), int(b[3] // self.CELL) + 1):
                for gz in range(int(b[2] // self.CELL), int(b[5] // self.CELL) + 1): self.grid.setdefault((gx, gz), []).append(i)

    def near(self, x, z, r=PLAYER_W / 2 + 1):
        ids = set()
        for gx in range(int((x - r) // self.CELL), int((x + r) // self.CELL) + 1):
            for gz in range(int((z - r) // self.CELL), int((z + r) // self.CELL) + 1): ids.update(self.grid.get((gx, gz), ()))
        return [self.boxes[i] for i in ids]

    def free(self, x, y, z, near=None):
        h = PLAYER_W / 2 - 0.02
        for b in (near if near is not None else self.near(x, z)):
            if b[0] < x + h and b[3] > x - h and b[2] < z + h and b[5] > z - h and b[1] < y + PLAYER_H - 0.02 and b[4] > y + 0.02: return False
        return True

    def stand_ys(self, x, z, y_from):
        """Every feet height within one step of y_from where the player can stand at (x, z) (supported by something under the footprint)."""
        near = self.near(x, z); h = PLAYER_W / 2
        tops = sorted({b[4] for b in near if b[0] < x + h - 0.02 and b[3] > x - h + 0.02 and b[2] < z + h - 0.02 and b[5] > z - h + 0.02 and abs(b[4] - y_from) <= STEP + 1e-6}, reverse=True)
        return [t for t in tops if self.free(x, t, z, near)]

    def stand_y(self, x, z, y_from):
        r = self.stand_ys(x, z, y_from)
        return r[0] if r else None


def reach(solver, start, step=3.0, limit=400000):
    x0, y0, z0 = start
    key = lambda x, y, z: (round(x / step), round(z / step), round(y * 4))
    seen = {key(x0, y0, z0): (x0, y0, z0)}; q = [(x0, y0, z0)]
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    while q and len(seen) < limit:
        x, y, z = q.pop()
        for dx, dz in dirs:
            nx, nz = x + dx * step, z + dz * step
            for ny in solver.stand_ys(nx, nz, y):
                k = key(nx, ny, nz)
                if k not in seen: seen[k] = (nx, ny, nz); q.append((nx, ny, nz))
    return seen


def targets(meta):
    for n, (a, b) in meta["decks"].items():
        if any(w in n for w in ("open", "envelope", "sling", "zone", "roof")) or abs(a[1] - b[1]) > 0.01: continue
        yield "deck", n, a, b
    for n, p in meta.get("seats", {}).items():
        if isinstance(p, list) and len(p) == 3: yield "seat", n, p, p


def walk_test(meta, solver):
    decks = [t for t in targets(meta) if t[0] == "deck"]
    start = None
    for _, n, a, b in decks:                                                     # entry = first deck that has a free standing spot
        for x in [a[0] + 6 + i * 4 for i in range(max(0, int((b[0] - a[0] - 12) // 4) + 1))] or [(a[0] + b[0]) / 2]:
            for z in [a[2] + 6 + j * 4 for j in range(max(0, int((b[2] - a[2] - 12) // 4) + 1))] or [(a[2] + b[2]) / 2]:
                ys = [y for y in solver.stand_ys(x, z, a[1]) if abs(y - a[1]) < 0.5]
                if ys: start = (x, ys[0], z); break
            if start: break
        if start: break
    if not start: return {"entry": None, "states": 0, "problems": ["no free standing spot found on any deck"]}
    seen = reach(solver, start); cells = {}
    for (ix, iz, iy), (x, y, z) in seen.items(): cells.setdefault((ix, iz), []).append(y)
    def ok(x, y, z, tol=2.5): return any(abs(yy - y) <= tol for yy in cells.get((round(x / 3.0), round(z / 3.0)), ()))
    problems, rep = [], {}
    for kind, n, a, b in targets(meta):
        if kind == "deck":
            pts = [(x, z) for x in [a[0] + 2 + i * 4 for i in range(max(1, int((b[0] - a[0]) // 4)))] for z in [a[2] + 2 + j * 4 for j in range(max(1, int((b[2] - a[2]) // 4)))]]
            good = sum(ok(x, a[1], z) for x, z in pts); rep[n] = round(100 * good / len(pts))
            if good == 0:
                cx, cz = (a[0] + b[0]) / 2, (a[2] + b[2]) / 2
                near = min((((x - cx) ** 2 + (z - cz) ** 2, (round(x), round(y, 1), round(z))) for (_, _, _), (x, y, z) in seen.items() if abs(y - a[1]) <= 40), default=None)
                problems.append(f"deck '{n}' (y={a[1]}) unreachable from entry; closest reached state {near[1] if near else None}")
        else:
            near = any(ok(a[0] + dx, a[1] + dy, a[2] + dz, 12) for dx in (-6, -3, 0, 3, 6) for dz in (-6, -3, 0, 3, 6) for dy in (-3, 0, 3))
            rep["seat:" + n] = 100 if near else 0                                   # info only: seats are mount points, riders do not have to walk to them
    return {"entry": [round(v, 1) for v in start], "states": len(seen), "coverage_pct": rep, "problems": problems}


def selftest():
    """The walk test must be able to FAIL: wall blocks, 12 px riser blocks, 4.5 px risers pass, 16 px hole blocks only if no landing."""
    floor = [-100, -5, -100, 100, 0, 100]
    wall = [-100, 0, 10, 100, 40, 12]
    assert (30, 0, 30) not in {tuple(round(c, 1) for c in v) for v in reach(PlayerSolver([floor, wall]), (0, 0, 0)).values()}, "wall did not block"
    riser12 = [-100, 0, 10, 100, 12, 100]
    assert not any(v[2] > 20 for v in reach(PlayerSolver([floor, riser12]), (0, 0, 0)).values()), "12 px riser should block"
    stairs = [[-100, 0, 10 + 6 * i, 100, 4.5 * (i + 1), 16 + 6 * i] for i in range(6)]
    assert any(v[1] >= 27 for v in reach(PlayerSolver([floor] + stairs), (0, 0, 0)).values()), "4.5 px risers should be climbable"
    door = [[-100, 0, 10, -7, 40, 12], [7, 0, 10, 100, 40, 12]]
    assert any(v[2] > 20 for v in reach(PlayerSolver([floor] + door), (0, 0, 0)).values()), "14 px door should pass the player"
    narrow = [[-100, 0, 10, -4, 40, 12], [4, 0, 10, 100, 40, 12]]
    assert not any(v[2] > 20 for v in reach(PlayerSolver([floor] + narrow), (0, 0, 0)).values()), "8 px gap must not pass a 9.6 px player"
    print("selftest ok: wall blocks, 12 px riser blocks, 4.5 px stairs climb, 14 px door passes, 8 px gap blocks")


def main():
    if "--selftest" in sys.argv: return selftest()
    import gen_fleet
    reg = gen_fleet.registry(); args = [a for a in sys.argv[1:] if not a.startswith("--")]
    keys = [k for k in args if k in reg] or list(reg); test = "--no-test" not in sys.argv
    out_dir = os.path.join(DATA, "vehicle_collision"); os.makedirs(out_dir, exist_ok=True); bad = 0
    for k in keys:
        bones, meta = reg[k][0]()
        static, dyn = solid_boxes(bones)
        with open(os.path.join(out_dir, meta["id"] + ".json"), "w") as f:
            json.dump({"unit": "px", "px_per_block": 16, "player": {"w": PLAYER_W, "h": PLAYER_H, "step": STEP}, "static": static, "dynamic": dyn}, f)
        line = f"{meta['id']}: static={len(static)} boxes dynamic={ {n: len(v) for n, v in dyn.items()} }"
        if test:
            r = walk_test(meta, PlayerSolver(static)); bad += bool(r["problems"])
            line += f"\n   entry={r['entry']} reachable_states={r['states']} problems={len(r['problems'])}"
            for p in r["problems"]: line += f"\n   !! {p}"
            line += "\n   coverage%: " + ", ".join(f"{n}={v}" for n, v in r.get("coverage_pct", {}).items())
        print(line)
    if test: print(f"\n{bad} vehicle(s) with problems out of {len(keys)}")


if __name__ == "__main__":
    main()
