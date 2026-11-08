"""Debug helper: python why.py <registry key> [deck-name]  -> lowest / highest reached states and what blocks the next move."""
import sys, collision as C, gen_fleet
reg = gen_fleet.registry(); b, m = reg[sys.argv[1]][0](); st, _ = C.solid_boxes(b); S = C.PlayerSolver(st)
res = C.walk_test(m, S); seen = C.reach(S, tuple(res["entry"]))
for label, pick in (("lowest", min), ("highest", max)):
    y, x, z = pick((y, round(x), round(z)) for (_, _, _), (x, y, z) in seen.values() if True) if False else pick(((v[1], round(v[0]), round(v[2])) for v in seen.values()))
    print(label, (x, y, z))
    for dx, dz in [(0, -3), (0, 3), (3, 0), (-3, 0)]:
        nx, nz = x + dx, z + dz
        print("  move", (dx, dz), "->", S.stand_ys(nx, nz, y), [[round(v, 1) for v in q] for q in S.near(nx, nz) if q[0] < nx + 4.78 and q[3] > nx - 4.78 and q[2] < nz + 4.78 and q[5] > nz - 4.78 and q[1] < y + 28.78 and q[4] > y + 0.02][:2])
