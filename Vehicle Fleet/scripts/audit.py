"""Continuity audit: AABB-touch graph of all cubes in rest pose; lists floating pieces (components not joined to the main body)."""
import sys, itertools
from fleet_common import *
import gen_fleet

TOL = 0.6


def world_boxes(bones):
    by = {b["name"]: b for b in bones}; pose = rest_pose(bones); out = []
    for b in bones:
        chain, n = [], b["name"]
        while n: chain.append(by[n]); n = by[n].get("parent")
        for ci, c in enumerate(b.get("cubes", [])):
            o, s = c["origin"], c["size"]; pts = []
            for k in itertools.product((0, 1), repeat=3):
                p = [o[i] + k[i] * s[i] for i in range(3)]
                if "rotation" in c: p = about(p, c["pivot"], c["rotation"])
                for bb in chain:
                    r = pose.get(bb["name"])
                    if r: p = about(p, bb["pivot"], r)
                pts.append(p)
            out.append((b["name"], ci, [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)], "rotation" in c))
    return out


def audit(key):
    reg = gen_fleet.registry(); bones, meta = reg[key][0]()
    bx = world_boxes(bones); n = len(bx); par = list(range(n))
    def f(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    order = sorted(range(n), key=lambda i: bx[i][2][0])
    for a in range(n):
        for b in range(a + 1, n):
            if all(bx[a][2][i] <= bx[b][3][i] + TOL and bx[b][2][i] <= bx[a][3][i] + TOL for i in range(3)): par[f(a)] = f(b)
    comps = {}
    for i in range(n): comps.setdefault(f(i), []).append(i)
    big = max(comps.values(), key=len)
    print(f"== {meta['id']}: {n} cubes, {len(comps)} components, main={len(big)}")
    for c in sorted(comps.values(), key=len, reverse=True):
        if c is big: continue
        lo = [round(min(bx[i][2][k] for i in c), 1) for k in range(3)]; hi = [round(max(bx[i][3][k] for i in c), 1) for k in range(3)]
        print(f"   floating x{len(c)} bones={sorted({bx[i][0] for i in c})[:4]} box={lo}..{hi}")


if __name__ == "__main__":
    for k in (sys.argv[1:] or list(gen_fleet.registry())): audit(k)
