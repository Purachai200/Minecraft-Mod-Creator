"""MP-01 Trooper Titan: builds geo/trooper_titan.geo.json and the base + 8 camo textures.

Run from the repo root:  python3 scratch/build_trooper_assets.py
Bone names and pivots match the old rig (animations, TitanModel IK and seat offsets rely on them).
Front of the titan is -Z, its right side is -X. Left-side parts are mirrored from the right.
"""
import json, os, random, struct, zlib

ROOT = "Titan Combat/src/main/resources/assets/titancombat"
TEX = 1024

# ---------------------------------------------------------------- model

def C(o, s, m, rot=None, piv=None, decal=None):
    c = {"o": list(o), "s": list(s), "m": m}
    if rot:
        c["rot"], c["piv"] = list(rot), list(piv)
    if decal:
        c["decal"] = decal  # {face: kind}
    return c

def mirror(cubes):
    swap = {"east": "west", "west": "east"}
    out = []
    for c in cubes:
        m = dict(c)
        m["o"] = [-(c["o"][0] + c["s"][0]), c["o"][1], c["o"][2]]
        if "rot" in c:
            m["rot"] = [c["rot"][0], -c["rot"][1], -c["rot"][2]]
            m["piv"] = [-c["piv"][0], c["piv"][1], c["piv"][2]]
        if "decal" in c:
            m["decal"] = {swap.get(f, f): k for f, k in c["decal"].items()}
        out.append(m)
    return out

def mpiv(p):
    return [-p[0], p[1], p[2]]

def drill(cx, cz, top):
    """Spiral drill bit hanging down from the wrist: stacked rings, each turned a bit more."""
    out = [C([cx - 7, top - 6, cz - 7], [14, 6, 14], "metal"),
           C([cx - 8, top - 8, cz - 8], [16, 2, 16], "rust"),
           C([cx - 6, top - 10, cz - 6], [12, 2, 12], "dark")]
    y, size = top - 10, 13
    for i in range(11):
        h = 3
        y -= h
        out.append(C([cx - size / 2, y, cz - size / 2], [size, h, size], "steel",
                     rot=[0, (i * 22.5) % 90, 0], piv=[cx, y, cz]))
        size = max(2, size - 1)
    out.append(C([cx - 1, y - 4, cz - 1], [2, 4, 2], "steel", rot=[0, 45, 0], piv=[cx, y, cz]))
    return out

def claw(cx, cz, top):
    """3-finger hydraulic claw: two front fingers and a rear thumb, each curling inward."""
    out = [C([cx - 6, top - 7, cz - 7], [12, 7, 14], "metal"),
           C([cx - 4, top - 9, cz - 5], [8, 2, 10], "dark")]
    y = top - 9
    for fx, fz, curl in ((cx - 4.5, cz - 6, -18), (cx + 1.5, cz - 6, -18), (cx - 1.5, cz + 3, 18)):
        out.append(C([fx, y - 10, fz], [3, 10, 3], "metal", rot=[curl, 0, 0], piv=[fx + 1.5, y, fz + 1.5]))
        tip_z = fz + (3 if curl < 0 else -3)
        out.append(C([fx, y - 17, tip_z], [3, 8, 3], "rust", rot=[-curl * 2.2, 0, 0], piv=[fx + 1.5, y - 9, tip_z + 1.5]))
    out.append(C([cx - 1, y - 6, cz - 3], [2, 6, 2], "steel"))  # center piston
    return out

RIGHT_ARM1 = [
    C([-41, 88, -4], [19, 19, 26], "paint", decal={"west": "mp01"}),           # shoulder pad
    C([-42, 86, -5], [20, 3, 28], "hazard"),                                    # hazard lip
    C([-38, 107, -1], [14, 2, 20], "paint2"),                                    # pad cap
    C([-31, 82, 5], [9, 10, 11], "dark"),                                       # shoulder joint
    C([-30, 70, 6], [9, 14, 10], "metal"),                                      # upper arm frame
    C([-31, 73, 4], [4, 9, 3], "paint2"),                                       # bicep plate
    C([-22, 71, 9], [3, 13, 3], "steel"),                                       # bicep piston
]
RIGHT_ARM2 = [
    C([-29, 67, 6], [10, 7, 10], "dark"),                                       # elbow
    C([-32, 48, 1], [16, 20, 18], "paint", decal={"west": "hazard_bottom"}),   # forearm armor
    C([-34, 53, 3], [2, 12, 14], "paint2"),                                     # outer plate
    C([-31, 59, -1], [14, 8, 2], "metal"),                                       # front guard
    C([-19, 51, 7], [4, 15, 4], "dark"),                                        # piston housing
    C([-18.5, 47, 7.5], [3, 6, 3], "steel"),                                    # piston rod
]
RIGHT_HAND = [C([-28, 43, 6], [10, 5, 11], "dark")]

RIGHT_LEG3 = [
    C([-19, 53, 2], [9, 11, 10], "dark"),
    C([-22, 49, -1], [4, 13, 15], "paint2"),                                    # hip armor
    C([-22, 48, -1], [4, 2, 15], "hazard"),
]
RIGHT_LEG2 = [
    C([-20, 27, -4], [12, 21, 13], "paint"),                                    # thigh armor
    C([-21, 31, -3], [2, 13, 11], "paint2"),
    C([-18, 23, -1], [8, 6, 8], "metal"),
    C([-16, 29, 9], [4, 18, 3], "steel"),                                       # rear piston
]
RIGHT_LEG1 = [
    C([-19, 21, -2], [9, 8, 9], "dark"),                                        # knee joint
    C([-20, 19, -9], [11, 11, 5], "paint", decal={"north": "x"}),               # knee plate
    C([-20, 8, -5], [11, 13, 12], "paint", decal={"north": "hazard_bottom"}),   # shin
    C([-18, 9, 7], [7, 13, 4], "metal"),                                        # calf
    C([-17, 10, 11], [4, 10, 2], "steel"),
]
RIGHT_FOOT = [
    C([-18, 4, -3], [8, 5, 8], "dark"),                                         # ankle
    C([-22, 0, -11], [15, 5, 19], "metal"),                                     # sole
    C([-22, 0, -18], [7, 4, 8], "paint", decal={"north": "hazard"}),            # toe A
    C([-14, 0, -18], [7, 4, 8], "paint", decal={"north": "hazard"}),            # toe B
    C([-21, 5, -12], [13, 2, 10], "paint2"),                                    # instep armor
    C([-20, 0, 8], [11, 4, 6], "dark"),                                         # heel
]

def cage():
    bar = "dark"
    out = []
    for x in (-15, 13):
        out.append(C([x, 105, -12], [2, 9, 2], bar))                            # front posts
        out.append(C([x, 105, 8], [2, 7, 2], bar))                              # rear posts
        out.append(C([x, 113, -12], [2, 2, 22], bar))                           # side rails
    out.append(C([-15, 113, -12], [30, 2, 2], bar))
    out.append(C([-15, 111, 8], [30, 2, 2], bar))
    out.append(C([-1, 113, -10], [2, 2, 18], bar))                              # spine rail
    return out

def exhausts():
    out = []
    for x in (-13, 7):
        out.append(C([x, 88, 18], [6, 26, 6], "metal"))
        out.append(C([x - 0.5, 114, 17.5], [7, 8, 7], "vent"))                  # perforated tip
        out.append(C([x - 1, 122, 17], [8, 2, 8], "rust"))                      # cap
        out.append(C([x - 1, 96, 17], [8, 2, 8], "dark"))                       # clamp band
    return out

BONES = [
    ("bb_main", None, [0, 0, 0], []),
    ("skill_locator", None, [0, 0, 0], []),
    ("titan", None, [0, 0, 0], []),
    ("body1", "titan", [0, 61.0, 7.0], [
        C([-11, 55, -3], [22, 10, 16], "dark"),
        C([-10, 52, -6], [9, 9, 4], "paint2"),                                  # groin plates
        C([1, 52, -6], [9, 9, 4], "paint2"),
        C([-6, 61, 12], [12, 6, 4], "metal"),
    ]),
    ("body2", "body1", [0, 74.9, 8.8], [
        C([-10, 65, -2], [20, 14, 15], "metal"),
        C([-8, 66, -4], [16, 4, 2], "paint2"),                                  # ab plates
        C([-8, 71, -4], [16, 4, 2], "paint2"),
        C([-13, 68, 0], [3, 8, 10], "vent"),
        C([10, 68, 0], [3, 8, 10], "vent"),
    ]),
    ("body3", "body2", [0.5, 78.7, 17.8], [
        C([-17, 79, -9], [34, 27, 27], "paint"),                                # hull
        C([-19, 83, -7], [2, 20, 22], "paint2"),                                # side armor
        C([17, 83, -7], [2, 20, 22], "paint2"),
        C([-14, 106, -10], [28, 3, 20], "metal"),                               # top deck
        C([-13, 82, 16], [26, 20, 3], "metal"),                                 # reactor back
        C([-10, 85, 19], [20, 12, 2], "vent"),
        C([-20, 98, -6], [4, 8, 14], "dark"),                                   # shoulder sockets
        C([16, 98, -6], [4, 8, 14], "dark"),
        C([-15, 76, -12], [30, 6, 8], "paint2", rot=[-25, 0, 0], piv=[0, 79, -9]),  # lower chest slope
        C([12, 109, 10], [1, 14, 1], "dark"),                                   # antenna
        C([-14, 94, -11], [5, 3, 2], "glow"),                                   # running lights
        C([9, 94, -11], [5, 3, 2], "glow"),
    ] + cage() + exhausts()),
    ("doorUp", "body3", [0, 115.5, 3.8], [
        C([-13, 95, -15], [26, 11, 6], "paint", decal={"north": "visor_frame"}),
        C([-14, 104, -16], [28, 3, 8], "paint2"),                               # brow
        C([-15, 96, -14], [2, 9, 5], "metal"),                                  # cheeks
        C([13, 96, -14], [2, 9, 5], "metal"),
    ]),
    ("eye", "doorUp", [0, 107.0, -17.0], [
        C([-9, 99, -16], [18, 2, 1], "visor"),
    ]),
    ("doorDown", "body3", [0, 82.7, -5.9], [
        C([-12, 81, -14], [24, 14, 5], "paint", decal={"north": "number"}),
        C([-9, 83, -15], [6, 6, 1], "vent"),
        C([3, 83, -15], [6, 6, 1], "vent"),
    ]),
    ("weaponBack", "body3", [-24.0, 78.0, 26.0], drill(-24, 24, 92)[:3] + [
        C([-27, 78, 21], [6, 8, 6], "steel", rot=[0, 45, 0], piv=[-24, 78, 24]),
        C([-26, 74, 23], [4, 4, 4], "steel", rot=[0, 45, 0], piv=[-24, 74, 25]),
    ]),
    ("rightArm1", "body3", [-24.4, 94.8, 10.7], RIGHT_ARM1),
    ("rightArm2", "rightArm1", [-23.4, 72.5, 10.7], RIGHT_ARM2),
    ("rightHand", "rightArm2", [-23.3, 46.8, 11.5], RIGHT_HAND),
    ("weapon", "rightHand", [-19.8, 39.8, 10.3], drill(-23, 11.5, 43)),
    ("leftArm1", "body3", [24.4, 94.8, 10.7], mirror(RIGHT_ARM1)),
    ("leftArm2", "leftArm1", [23.4, 72.5, 10.7], mirror(RIGHT_ARM2)),
    ("leftHand", "leftArm2", [23.3, 46.8, 11.5], mirror(RIGHT_HAND) + claw(23, 11.5, 43)),
    ("rightLeg3", "titan", [-14.5, 61.1, 7.1], RIGHT_LEG3),
    ("rightLeg2", "rightLeg3", [-14.5, 43.5, 2.7], RIGHT_LEG2),
    ("rightLeg1", "rightLeg2", [-14.5, 22.8, 3.4], RIGHT_LEG1),
    ("rightFoot", "rightLeg1", [-14.5, 8.1, -3.4], RIGHT_FOOT),
    ("leftLeg3", "titan", [14.8, 61.1, 7.1], mirror(RIGHT_LEG3)),
    ("leftLeg2", "leftLeg3", [14.8, 43.5, 2.7], mirror(RIGHT_LEG2)),
    ("leftLeg1", "leftLeg2", [14.8, 22.8, 3.4], mirror(RIGHT_LEG1)),
    ("leftFoot", "leftLeg1", [14.8, 8.1, -3.4], mirror(RIGHT_FOOT)),
]

# ---------------------------------------------------------------- uv packing (box uv, 1 texel / px)

def pack():
    x, y, row = 2, 2, 0
    placed = []
    for name, parent, piv, cubes in BONES:
        for c in cubes:
            w, h, d = (max(1, int(round(v))) for v in c["s"])
            need_w, need_h = 2 * (d + w) + 2, d + h + 2
            if x + need_w > TEX:
                x, y, row = 2, y + row, 0
            c["uv"], c["dims"] = [x, y], (w, h, d)
            x += need_w
            row = max(row, need_h)
            placed.append(c)
    assert y + row <= TEX, "texture atlas overflow"
    return placed

def faces(c):
    u, v = c["uv"]
    w, h, d = c["dims"]
    return {"up": (u + d, v, w, d), "down": (u + d + w, v, w, d),
            "east": (u, v + d, d, h), "north": (u + d, v + d, w, h),
            "west": (u + d + w, v + d, d, h), "south": (u + 2 * d + w, v + d, w, h)}

# Rest rotations of the Ion rig. trooper_titan.animation.json was cloned from Ion and its keyframes
# are offsets on top of these, so the Trooper bones carry them too. Each bone's cubes then sit in a
# "<bone>_c" child that undoes the accumulated rest transform, so the model still looks as authored.
REST = {"doorUp": [25, 0, 0], "eye": [15, 0, 0], "rightArm1": [0, -180, 30], "rightHand": [0, -180, 0],
        "weapon": [90, 0, 90], "leftArm1": [0, 180, -30], "leftHand": [0, 180, 0],
        "rightLeg3": [-15, 0, 0], "rightLeg2": [37.5, 0, 0], "rightLeg1": [-15, 0, 0], "rightFoot": [-7.5, 0, 0],
        "leftLeg3": [-15, 0, 0], "leftLeg2": [37.5, 0, 0], "leftLeg1": [-15, 0, 0], "leftFoot": [-7.5, 0, 0]}

def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def mat_vec(m, v):
    return [sum(m[i][k] * v[k] for k in range(3)) for i in range(3)]

def bone_rot(r):
    """Bedrock euler (deg) -> matrix in mirrored-x space, as GeckoLib/Blockbench apply it: Rz * Ry * Rx with x/y negated."""
    import math
    x, y, z = (math.radians(v) for v in (-r[0], -r[1], r[2]))
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    rz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    return mat_mul(rz, mat_mul(ry, rx))

def euler_of(m):
    import math
    b = math.asin(-max(-1, min(1, m[2][0])))
    if abs(m[2][0]) < 0.9999999:
        g, a = math.atan2(m[2][1], m[2][2]), math.atan2(m[1][0], m[0][0])
    else:
        g, a = 0.0, math.atan2(-m[0][1], m[1][1])
    return [-math.degrees(g), -math.degrees(b), math.degrees(a)]

def geo_json():
    bones, acc = [], {}
    ident = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    for name, parent, piv, cubes in BONES:
        P = [-piv[0], piv[1], piv[2]]
        R = bone_rot(REST.get(name, [0, 0, 0]))
        Mp, tp = acc.get(parent, (ident, [0, 0, 0]))
        M = mat_mul(Mp, R)
        RP = mat_vec(R, P)
        t = [a + b for a, b in zip(mat_vec(Mp, [P[i] - RP[i] for i in range(3)]), tp)]
        acc[name] = (M, t)
        b = {"name": name, "pivot": piv}
        if parent:
            b["parent"] = parent
        if name in REST:
            b["rotation"] = REST[name]
        bones.append(b)
        if not cubes:
            continue
        shift, holder = [0, 0, 0], b
        if any(abs(M[i][j] - ident[i][j]) > 1e-6 for i in range(3) for j in range(3)):
            Rf = [[M[j][i] for j in range(3)] for i in range(3)]
            fix = euler_of(Rf)
            assert all(abs(x - y) < 1e-6 for r1, r2 in zip(bone_rot(fix), Rf) for x, y in zip(r1, r2))
            MP = mat_vec(M, P)
            c = [MP[i] + t[i] - P[i] for i in range(3)]
            shift = [c[0], -c[1], -c[2]]  # back to bedrock (un-mirrored x)
            holder = {"name": name + "_c", "parent": name, "pivot": piv, "rotation": [round(v, 4) for v in fix]}
            bones.append(holder)
        out = []
        for c in cubes:
            o = [c["o"][i] + shift[i] for i in range(3)]
            e = {"origin": [round(v, 3) for v in o], "size": [round(v, 3) for v in c["s"]], "uv": c["uv"]}
            if "rot" in c:
                e["pivot"] = [round(c["piv"][i] + shift[i], 3) for i in range(3)]
                e["rotation"] = c["rot"]
            out.append(e)
        holder["cubes"] = out
    return {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": "geometry.trooper_titan", "texture_width": TEX, "texture_height": TEX,
                        "visible_bounds_width": 6, "visible_bounds_height": 9, "visible_bounds_offset": [0, 4, 0]},
        "bones": bones}]}

# ---------------------------------------------------------------- texture

# (name, paint, paint2, visor)
SCHEMES = [
    ("olive",     (92, 102, 64),  (66, 74, 50),   (70, 255, 120)),
    ("desert",    (182, 156, 108),(134, 112, 78), (70, 255, 120)),
    ("arctic",    (200, 204, 202),(132, 140, 146),(90, 220, 255)),
    ("navy",      (54, 72, 104),  (36, 46, 68),   (90, 220, 255)),
    ("crimson",   (146, 42, 38),  (84, 30, 28),   (255, 190, 60)),
    ("urban",     (116, 120, 122),(78, 82, 86),   (70, 255, 120)),
    ("blackops",  (46, 48, 50),   (30, 31, 33),   (255, 60, 50)),
    ("industrial",(220, 124, 30), (60, 62, 66),   (70, 255, 120)),
    ("jungle",    (58, 92, 56),   (96, 78, 52),   (255, 190, 60)),
]
FIXED = {"metal": (78, 82, 86), "dark": (40, 42, 45), "steel": (158, 162, 166), "rust": (126, 70, 40),
         "vent": (58, 60, 63), "glow": (255, 214, 120)}
YELLOW, BLACK, WHITE = (228, 182, 32), (30, 30, 30), (226, 228, 222)

FONT = {"M": ["10001", "11011", "10101", "10001", "10001"], "P": ["110", "101", "110", "100", "100"],
        "-": ["000", "000", "111", "000", "000"], "0": ["111", "101", "101", "101", "111"],
        "1": ["010", "110", "010", "010", "111"]}

def h2(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2246822519) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return (n ^ (n >> 16)) / 0xffffffff

def vnoise(x, y, scale, s):
    gx, gy = x / scale, y / scale
    x0, y0 = int(gx), int(gy)
    fx, fy = gx - x0, gy - y0
    a, b = h2(x0, y0, s), h2(x0 + 1, y0, s)
    c, d = h2(x0, y0 + 1, s), h2(x0 + 1, y0 + 1, s)
    top, bot = a + (b - a) * fx, c + (d - c) * fx
    return top + (bot - top) * fy

def mul(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)

def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def render(cubes, scheme):
    _, paint, paint2, visor = scheme
    px = bytearray(TEX * TEX * 4)

    def put(x, y, col):
        i = (y * TEX + x) * 4
        px[i:i + 4] = bytes((col[0], col[1], col[2], 255))

    def base(mat):
        return {"paint": paint, "paint2": paint2, "visor": visor}.get(mat) or FIXED.get(mat, (90, 90, 90))

    for ci, c in enumerate(cubes):
        mat = c["m"]
        rng = random.Random(ci * 7919)
        for fname, (fx, fy, fw, fh) in faces(c).items():
            side = fname not in ("up", "down")
            for j in range(fh):
                for i in range(fw):
                    gx, gy = fx + i, fy + j
                    edge = min(i, j, fw - 1 - i, fh - 1 - j)
                    n = (h2(gx, gy, 1) - 0.5) * 0.06
                    if mat == "hazard":
                        col = YELLOW if ((i + j) // 3) % 2 == 0 else BLACK
                    elif mat == "visor":
                        col = mix(visor, (230, 255, 240), 0.6) if 0 < i < fw - 1 and 0 < j < fh - 1 else visor
                        put(gx, gy, col)
                        continue
                    elif mat == "glow":
                        put(gx, gy, FIXED["glow"])
                        continue
                    elif mat == "vent":
                        col = mul(FIXED["vent"], 0.45 if (j % 2 == 0 and 0 < i < fw - 1) else 1.0)
                    elif mat == "steel":
                        col = mul(FIXED["steel"], 0.8 + 0.35 * (1 - j / max(1, fh - 1)) if side else 1.0)
                        if (i + j) % 4 == 0:
                            col = mul(col, 0.82)
                    elif mat == "rust":
                        col = mix(FIXED["rust"], (70, 40, 28), vnoise(gx, gy, 3, 5))
                    else:
                        col = base(mat)
                        if mat in ("paint", "paint2"):
                            col = mul(col, 0.9 + 0.2 * vnoise(gx, gy, 9, 2))  # faded mottling
                    col = mul(col, 1 + n)
                    # panel seams, top-edge highlight, rivets
                    if edge == 0:
                        col = mul(col, 0.62)
                    elif j == 1 and side:
                        col = mul(col, 1.15)
                    if mat in ("paint", "paint2", "metal") and fw >= 12 and i in (fw // 2,):
                        col = mul(col, 0.72)
                    if mat in ("paint", "paint2", "metal") and fh >= 14 and j == int(fh * 0.4):
                        col = mul(col, 0.72)
                    if fw >= 12 and fh >= 12 and i in (2, fw - 3) and j in (2, fh - 3):
                        col = (170, 172, 168)
                    elif fw >= 12 and fh >= 12 and i in (2, fw - 3) and j in (3, fh - 2):
                        col = mul(col, 0.6)
                    # chipped paint on edges, grime near the bottom, rust streaks
                    if mat in ("paint", "paint2", "hazard") and edge == 1 and h2(gx, gy, 3) < 0.10:
                        col = (128, 128, 124) if h2(gx, gy, 4) < 0.7 else FIXED["rust"]
                    if side and mat not in ("steel",):
                        t = j / max(1, fh - 1)
                        if t > 0.7:
                            col = mix(col, (52, 44, 34), (t - 0.7) * 0.9)
                    if side and mat in ("paint", "paint2") and h2(gx, 0, 6) < 0.03 and j > 2 and h2(gx, gy, 7) < 0.75:
                        col = mix(col, FIXED["rust"], 0.45)
                    put(gx, gy, col)
            if side:
                draw_decal(put, c.get("decal", {}).get(fname), fx, fy, fw, fh, rng)
    return px

def draw_decal(put, kind, fx, fy, fw, fh, rng):
    if not kind:
        return
    if kind in ("hazard_bottom", "mp01", "hazard"):
        rows = fh if kind == "hazard" else 3
        for j in range(fh - rows, fh):
            for i in range(fw):
                col = YELLOW if ((i + j) // 2) % 2 == 0 else BLACK
                if h2(fx + i, fy + j, 9) < 0.15:
                    col = (110, 108, 100)
                put(fx + i, fy + j, col)
    if kind in ("mp01", "number"):
        text = "MP-01" if kind == "mp01" else "01"
        width = sum(len(FONT[ch][0]) + 1 for ch in text) - 1
        x0, y0 = fx + (fw - width) // 2, fy + (3 if kind == "mp01" else 1)
        for ch in text:
            g = FONT[ch]
            for r, line in enumerate(g):
                for k, bit in enumerate(line):
                    if bit == "1" and h2(x0 + k, y0 + r, 11) > 0.12:
                        put(x0 + k, y0 + r, WHITE)
            x0 += len(g[0]) + 1
    if kind == "mp01":
        cx = fx + fw // 2
        for n in range(2):  # chevrons
            top = fy + 10 + n * 4
            for k in range(4):
                for t in (0, 1):
                    put(cx - 3 + k, top + k + t, WHITE)
                    put(cx + 3 - k, top + k + t, WHITE)
    if kind == "x":
        for k in range(1, min(fw, fh) - 1):
            for dx in (0, 1):
                put(fx + min(fw - 2, k + dx), fy + k, (34, 34, 34))
                put(fx + max(1, fw - 1 - k - dx), fy + k, (34, 34, 34))
    if kind == "visor_frame":
        for i in range(2, fw - 2):  # dark visor recess band
            for j in range(3, 6):
                put(fx + i, fy + j, (24, 26, 28))

def write_png(path, raw):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    rows = bytearray()
    for y in range(TEX):
        rows.append(0)
        rows.extend(raw[y * TEX * 4:(y + 1) * TEX * 4])
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", TEX, TEX, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + chunk(b"IEND", b""))

def main():
    cubes = pack()
    with open(f"{ROOT}/geo/trooper_titan.geo.json", "w") as f:
        json.dump(geo_json(), f, indent=1)
    tex_dir = f"{ROOT}/textures/entity/titan/trooper"
    for idx, scheme in enumerate(SCHEMES):
        name = "trooper_titan.png" if idx == 0 else f"trooper_titan_{idx}.png"
        write_png(os.path.join(tex_dir, name), render(cubes, scheme))
        print("wrote", name, scheme[0])
    print(len(cubes), "cubes")

if __name__ == "__main__":
    main()
