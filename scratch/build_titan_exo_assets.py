"""Titan Exo Frame: the MP-05 inner frame wearing the real Titanfall titans as armour.

Each armour archetype is one of the mod's titans (Ion, Legion, Ronin, Northstar, Scorch, Monarch, Tone). Their shell
cubes are transplanted onto the exo skeleton: every source bone's rest-pose transform is matched to the exo bone it
belongs to, the titan is scaled so its hips sit at the exo's hip height, and each cube keeps its shape relative to the
joint it hangs from. Faces are copied into a 2048 atlas around the exo frame's own 1024 texture.

Bones are named tfarmor_<slot>_<archetype>_<exo bone>; TitanModel shows them for the worn slot's archetype.
Writes geo/titan_exo_titan.geo.json and textures/entity/titan/titan_exo/titan_exo_titan[_N].png (9 schemes).

Run from the repo root after build_exo_frame_assets.py:  python3 scratch/build_titan_exo_assets.py
"""
import json, math, os
from PIL import Image

ROOT = "Titan Combat/src/main/resources/assets/titancombat"
ATLAS = 2048
ARCHETYPE_TITAN = {"infantry": "ion", "siege": "legion", "samurai": "ronin", "stealth": "northstar",
                   "aero": "northstar", "scrap": "scorch", "sovereign": "monarch", "expedition": "tone"}

# Source bone (first letter lowercased) -> (slot, exo bone). Bones in between resolve to their nearest listed ancestor.
ANCHORS = {"doorUp": ("head", "doorUp"), "doorTop": ("head", "doorUp"), "door": ("head", "doorUp"),
           "body3": ("chest", "body3"), "doorDown": ("chest", "doorDown"), "body2": ("chest", "body2"),
           "body1": ("legs", "body1")}
for side in ("right", "left"):
    ANCHORS.update({f"{side}Arm1": ("arms", f"{side}Arm1"), f"{side}Arm2": ("arms", f"{side}Arm2"),
                    f"{side}Hand": ("arms", f"{side}Hand"), f"{side}Leg4": ("legs", f"{side}Leg3"),
                    f"{side}Leg3": ("legs", f"{side}Leg3"), f"{side}Leg2": ("legs", f"{side}Leg2"),
                    f"{side}Leg1": ("legs", f"{side}Leg1"), f"{side}Foot": ("legs", f"{side}Foot")})
# Weapons, effects and the pilot seat are not armour (they and everything under them are dropped)
EXCLUDE = {"weapon", "clip", "line", "rotate", "laser1", "laser2", "laser3", "laserExpand1", "laserExpand2", "laserHead",
           "sword", "swordHead2", "seat", "weaponLeftOpen", "weaponRightOpen", "weaponTopOpen", "plug", "push", "circle",
           "topRotate1", "topRotate2", "bottomRotate", "fireHead", "rocketLeftFire", "rocketRightFire"}


# ---------------------------------------------------------------- 3x3 maths
def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def mv(a, v):
    return [sum(a[i][k] * v[k] for k in range(3)) for i in range(3)]


def tr(a):
    return [[a[j][i] for j in range(3)] for i in range(3)]


def rx(t):
    c, s = math.cos(t), math.sin(t)
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def ry(t):
    c, s = math.cos(t), math.sin(t)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def rz(t):
    c, s = math.cos(t), math.sin(t)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def rot(deg):
    """A bone/cube "rotation" as a matrix in the geo's own coordinates. GeckoLib mirrors x and negates the x and y
    angles, which leaves R = Rz(-z) Ry(y) Rx(-x) here (checked in game: negative x lifts the -z end, z runs clockwise)."""
    x, y, z = (math.radians(v) for v in (deg or [0, 0, 0]))
    return mul(rz(-z), mul(ry(y), rx(-x)))


def euler(r):
    """Inverse of rot(): degrees [x, y, z]."""
    sy = max(-1.0, min(1.0, -r[2][0]))
    b = math.asin(sy)
    if abs(sy) < 0.99999:
        a = math.atan2(r[1][0], r[0][0])
        c = math.atan2(r[2][1], r[2][2])
    else:  # gimbal lock: fold z into x
        a = 0.0
        c = math.atan2(-r[1][2], r[1][1])
    return [round(-math.degrees(c), 4), round(math.degrees(b), 4), round(-math.degrees(a), 4)]


def is_identity(r):
    return all(abs(r[i][j] - (1 if i == j else 0)) < 1e-4 for i in range(3) for j in range(3))


def rest_transforms(bones):
    """name -> (A, c): rest-pose world position of a model-space point x is A x + c."""
    by = {b["name"]: b for b in bones}
    out = {}

    def get(name):
        if name in out:
            return out[name]
        b = by[name]
        pa, pc = get(b["parent"]) if b.get("parent") in by else ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [0, 0, 0])
        p, r = b.get("pivot", [0, 0, 0]), rot(b.get("rotation"))
        # x -> parent(pivot + R (x - pivot)) = PA R x + PA (pivot - R pivot) + pc
        rp = mv(r, p)
        a = mul(pa, r)
        c = [v + pc[i] for i, v in enumerate(mv(pa, [p[k] - rp[k] for k in range(3)]))]
        out[name] = (a, c)
        return out[name]

    for n in by:
        get(n)
    return out


# Torso pivots sit in different places on every titan (exo: back of the chest), so torso, hatch and pelvis
# pieces line up on the centre of each model's chest block instead; limb pivots are real hinges and stay.
BODY_ANCHORS = {"body1", "body2", "body3", "door", "doorUp", "doorTop", "doorDown"}


def chest_centre(bones, rest, name="body3"):
    """World-space bounding-box centre of a chest bone's own cubes in the rest pose."""
    b = next(x for x in bones if x["name"] == name)
    a, c = rest[name]
    pts = []
    for cube in b.get("cubes", []):
        o, sz = cube["origin"], cube["size"]
        for corner in ((0, 0, 0), (1, 1, 1)):
            p = mv(a, [o[i] + corner[i] * sz[i] for i in range(3)])
            pts.append([p[i] + c[i] for i in range(3)])
    return [(min(p[i] for p in pts) + max(p[i] for p in pts)) / 2 for i in range(3)]


def norm(name):
    return name[0].lower() + name[1:]


# ---------------------------------------------------------------- atlas packing
class Packer:
    """Shelf packer over the atlas outside the top-left 1024 square (the exo frame's own texture)."""
    def __init__(self):
        self.regions = [(0, 1024, ATLAS, ATLAS), (1024, 0, ATLAS, 1024)]
        self.ri, self.x, self.y, self.row = 0, 0, 1024, 0

    def place(self, w, h):
        while True:
            x0, y0, x1, y1 = self.regions[self.ri]
            if self.x + w > x1:
                self.x, self.y, self.row = x0, self.y + self.row + 1, 0
            if self.y + h <= y1:
                pos = (self.x, self.y)
                self.x += w + 1
                self.row = max(self.row, h)
                return pos
            self.ri += 1
            assert self.ri < len(self.regions), "titan exo atlas full"
            x0, y0, _, _ = self.regions[self.ri]
            self.x, self.y, self.row = x0, y0, 0


def build():
    exo = json.load(open(f"{ROOT}/geo/exo_frame_titan.geo.json"))
    exo_bones = [b for b in exo["minecraft:geometry"][0]["bones"] if not b["name"].startswith("armor_")]
    exo_by = {b["name"]: b for b in exo_bones}
    exo_rest = rest_transforms(exo_bones)
    exo_hip = mv(exo_rest["rightLeg3"][0], exo_by["rightLeg3"]["pivot"])[1] + exo_rest["rightLeg3"][1][1]

    atlas_extra = Image.new("RGBA", (ATLAS, ATLAS), (0, 0, 0, 0))
    textures = {}
    rects = {}  # (titan, u, v, w, h) -> (u0, v0, bw, bh): source texel block of one face, packed once per titan
    bones = list(exo_bones)
    for aid, titan in ARCHETYPE_TITAN.items():
        geo = json.load(open(f"{ROOT}/geo/{titan}_titan.geo.json"))["minecraft:geometry"][0]
        textures[titan] = Image.open(f"{ROOT}/textures/entity/titan/{titan}/{titan}_titan.png").convert("RGBA")
        src = geo["bones"]
        src_by = {b["name"]: b for b in src}
        src_rest = rest_transforms(src)

        def joint(rest, by, name):
            a, c = rest[name]
            p = mv(a, by[name]["pivot"])
            return [p[i] + c[i] for i in range(3)]

        hip_name = "rightLeg3" if "rightLeg3" in src_by else "rightLeg4"
        src_chest, exo_chest = chest_centre(src, src_rest), chest_centre(exo_bones, exo_rest, "frame_chest")
        scale = max(0.7, min(1.3, exo_hip / joint(src_rest, src_by, hip_name)[1]))

        groups = {}  # exo bone + slot -> cubes
        for b in src:
            if not b.get("cubes"):
                continue
            # nearest anchor ancestor; drop excluded branches
            n, anchor, dropped = b["name"], None, False
            while n:
                if norm(n) in EXCLUDE or "Finger" in n:
                    dropped = True
                    break
                if norm(n) in ANCHORS:
                    anchor = n
                    break
                n = src_by[n].get("parent")
            if dropped or anchor is None:
                continue
            slot, target = ANCHORS[norm(anchor)]
            ab, ac = src_rest[b["name"]]
            if norm(anchor) in BODY_ANCHORS:
                js, jt = src_chest, exo_chest
            else:
                js, jt = joint(src_rest, src_by, anchor), joint(exo_rest, exo_by, target)
            ta, tc = exo_rest[target]
            tinv = tr(ta)  # rest transforms are rotations: inverse = transpose
            rrel = mul(tinv, ab)
            # x' = s*Rrel x + t
            t = mv(tinv, [jt[i] + scale * (ac[i] - js[i]) - tc[i] for i in range(3)])
            out = groups.setdefault((slot, target), [])
            for c in b["cubes"]:
                o, size = c["origin"], c["size"]
                piv = c.get("pivot", o)
                rc = rot(c.get("rotation"))
                p2 = [scale * v + t[i] for i, v in enumerate(mv(rrel, piv))]
                r2 = mul(rrel, rc)
                cube = {"origin": [round(p2[i] + scale * (o[i] - piv[i]), 4) for i in range(3)],
                        "size": [round(scale * v, 4) for v in size]}
                if "inflate" in c:
                    cube["inflate"] = round(scale * c["inflate"], 4)
                if not is_identity(r2):
                    cube["pivot"] = [round(v, 4) for v in p2]
                    cube["rotation"] = euler(r2)
                faces = {}
                for f, v in c["uv"].items():
                    (u, vv), (w, h) = v["uv"], v["uv_size"]
                    key = (titan, u, vv, w, h)
                    if key not in rects:
                        u0, v0 = math.floor(min(u, u + w)), math.floor(min(vv, vv + h))
                        u1, v1 = math.ceil(max(u, u + w)), math.ceil(max(vv, vv + h))
                        rects[key] = (u0, v0, max(1, u1 - u0), max(1, v1 - v0))
                    faces[f] = key  # resolved to atlas uvs once everything is packed
                cube["uv"] = faces
                out.append(cube)
        for (slot, target), cubes in groups.items():  # noqa: B007
            bones.append({"name": f"tfarmor_{slot}_{aid}_{target}", "parent": target,
                          "pivot": exo_by[target]["pivot"], "cubes": cubes})
        print(f"{aid:<10} <- {titan:<9} scale {scale:.2f}  {sum(len(c) for c in groups.values())} cubes")

    # Pack tallest faces first so shelves stay full, then point every face at its packed block
    packer, placed = Packer(), {}
    for key, (u0, v0, bw, bh) in sorted(rects.items(), key=lambda kv: (-kv[1][3], -kv[1][2])):
        X, Y = packer.place(bw, bh)
        atlas_extra.paste(textures[key[0]].crop((u0, v0, u0 + bw, v0 + bh)), (X, Y))
        placed[key] = (X - u0, Y - v0)
    for b in bones:
        if not b["name"].startswith("tfarmor_"):
            continue
        for c in b["cubes"]:
            c["uv"] = {f: {"uv": [k[1] + placed[k][0], k[2] + placed[k][1]], "uv_size": [k[3], k[4]]} for f, k in c["uv"].items()}

    # The exo frame's box UVs stay valid as they are: texel coordinates, and its texture sits at the atlas origin
    desc = dict(exo["minecraft:geometry"][0]["description"], identifier="geometry.titan_exo_titan",
                texture_width=ATLAS, texture_height=ATLAS)
    with open(f"{ROOT}/geo/titan_exo_titan.geo.json", "w") as f:
        json.dump({"format_version": "1.12.0", "minecraft:geometry": [{"description": desc, "bones": bones}]}, f)

    out_dir = f"{ROOT}/textures/entity/titan/titan_exo"
    os.makedirs(out_dir, exist_ok=True)
    for i in range(9):
        suffix = "" if i == 0 else f"_{i}"
        base = Image.open(f"{ROOT}/textures/entity/titan/exo_frame/exo_frame_titan{suffix}.png").convert("RGBA")
        img = atlas_extra.copy()
        img.paste(base, (0, 0))
        img.save(f"{out_dir}/titan_exo_titan{suffix}.png")
    print(f"atlas region {packer.ri}, y {packer.y}; {sum(1 for b in bones if b['name'].startswith('tfarmor_'))} armour bones")


if __name__ == "__main__":
    # round-trip check of the euler convention
    for d in ([10, 20, 30], [-45, 0, 90], [0, -180, 30], [37.5, 0, 0]):
        e = euler(rot(d))
        assert all(abs(a - b) < 1e-6 for r1, r2 in zip(rot(d), rot(e)) for a, b in zip(r1, r2)), (d, e)
    build()
