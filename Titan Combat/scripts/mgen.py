"""Shared helpers for the Knightmare Frame generator: bone-aware cube placement (design in world rest-pose
coordinates), per-face UV atlas packing, and a procedural armour painter. Verified against GeckoLib's rotation
convention: file rotation [x,y,z] acts as angles (-x, +y, -z) in the file's own axes, applied X, Y, then Z."""
import json, math, os, random
import numpy as np
from PIL import Image
import gen_v22_osprey as O

_orig_rot = O.rot
O.rot = lambda v, r: _orig_rot(v, [r[0], -r[1], -r[2]])      # patch the preview renderer to the titan convention


def rmat(r):
    cols = [O.rot(v, r) for v in ((1, 0, 0), (0, 1, 0), (0, 0, 1))]
    return np.array(cols).T


class Model:
    def __init__(self, src_bones, tex_size):
        self.bones = {b["name"]: dict(b, cubes=[]) for b in src_bones}
        self.order = [b["name"] for b in src_bones]
        self.tex = tex_size

    def add_bone(self, name, parent, pivot=None, rotation=None):
        pv = pivot if pivot is not None else self.bones[parent]["pivot"]
        b = {"name": name, "parent": parent, "pivot": list(pv), "cubes": []}
        if rotation: b["rotation"] = rotation
        self.bones[name] = b; self.order.append(name)

    def chain(self, name):
        out = []
        while name:
            b = self.bones[name]; out.append(b); name = b.get("parent")
        return out

    def to_local(self, bone, p):
        """World rest-pose point -> the bone's own (pre-rotation) coordinates."""
        p = np.array(p, float)
        for b in reversed(self.chain(bone)):          # root first
            if "rotation" in b:
                piv = np.array(b["pivot"], float)
                p = rmat(b["rotation"]).T @ (p - piv) + piv
        return p

    def cube(self, bone, c, s, mat="P", rot=None, inflate=0.0, **kw):
        """Cube centred at world rest-pose point c with local-axis size s. rot = extra cube rotation about its centre."""
        loc = self.to_local(bone, c)
        o = [round(loc[i] - s[i] / 2, 3) for i in range(3)]
        cube = {"origin": o, "size": [round(v, 3) for v in s], "mat": mat, "arch": kw.get("arch")}
        if inflate: cube["inflate"] = inflate
        if rot:
            cube["rotation"] = list(rot); cube["pivot"] = [round(v, 3) for v in loc]
        self.bones[bone]["cubes"].append(cube)

    def mirror_name(self, n):
        for a, b in (("right", "left"), ("Right", "Left")):
            if a in n: return n.replace(a, b)
            if b in n: return n.replace(b, a)
        return None

    def pair(self, bone, c, s, mat="P", rot=None, **kw):
        """Same cube on the bone and on its left/right twin (x mirrored)."""
        self.cube(bone, c, s, mat, rot, **kw)
        mb = self.mirror_name(bone)
        mrot = [rot[0], -rot[1], -rot[2]] if rot else None
        self.cube(mb, (-c[0], c[1], c[2]), s, mat, mrot, **kw)

    def uv_pack(self):
        """Allocate one atlas rect per cube face (shelf packing, tallest first)."""
        items = []
        for bn in self.order:
            for ci, c in enumerate(self.bones[bn]["cubes"]):
                sx, sy, sz = c["size"]
                dims = {"north": (sx, sy), "south": (sx, sy), "east": (sz, sy), "west": (sz, sy), "up": (sx, sz), "down": (sx, sz)}
                for f, (w, h) in dims.items():
                    items.append((bn, ci, f, w, h, math.ceil(w), math.ceil(h)))
        items.sort(key=lambda t: (-t[6], -t[5]))
        x = y = rowh = 0
        T = self.tex
        self.rects = []
        for bn, ci, f, w, h, rw, rh in items:
            if x + rw + 1 > T: x, y, rowh = 0, y + rowh + 1, 0
            if y + rh > T: raise RuntimeError("atlas overflow")
            c = self.bones[bn]["cubes"][ci]
            c.setdefault("uv", {})[f] = {"uv": [x, y], "uv_size": [round(w, 3), round(h, 3)]}
            self.rects.append((bn, ci, f, x, y, rw, rh))
            x += rw + 1; rowh = max(rowh, rh)
        return y + rowh

    def to_json(self, ident, vb):
        bones = []
        for n in self.order:
            b = dict(self.bones[n]); cubes = []
            for c in b["cubes"]:
                d = {k: c[k] for k in ("origin", "size", "uv", "inflate", "rotation", "pivot") if k in c}
                cubes.append(d)
            b["cubes"] = cubes
            bones.append(b)
        return {"format_version": "1.12.0", "minecraft:geometry": [{"description": dict(
            identifier=ident, texture_width=self.tex, texture_height=self.tex, **vb), "bones": bones}]}

    def render_bones(self):
        out = []
        for n in self.order:
            b = dict(self.bones[n]); b["cubes"] = [dict(c) for c in b["cubes"]]
            out.append(b)
        return out


# ------------------------------------------------------------------ limb-frame placement
def sigma(name):
    return -1.0 if ("right" in name.lower()) else 1.0


def _net(m, name):
    R = np.eye(3)
    for b in m.chain(name):
        if "rotation" in b: R = rmat(b["rotation"]) @ R
    return R


def pivot_world(m, name):
    v = np.array(m.bones[name]["pivot"], float)
    for b in m.chain(name):
        if "rotation" in b:
            p = np.array(b["pivot"], float); v = rmat(b["rotation"]) @ (v - p) + p
    return v


def frame(m, name):
    U = _net(m, name) @ np.array([0, 1.0, 0])
    z = np.array([0, 0, 1.0]); Zp = z - (z @ U) * U; Zp /= np.linalg.norm(Zp)
    X = np.cross(U, Zp); X /= np.linalg.norm(X)
    return sigma(name) * X, U, Zp


def place(m, bone, org, out, up, back, size, mat="P", rot=None, **kw):
    """Cube at (out, up, back) in the bone's limb frame, measured from world point org."""
    X, U, Z = frame(m, bone)
    c = np.array(org, float) + out * X + up * U + back * Z
    m.cube(bone, c, size, mat, rot, **kw)


def lpair(m, bone, orgspec, out, up, back, size, mat="P", rot=None, **kw):
    """orgspec: 'self' (bone pivot) | name of another bone (its pivot) | (nameA, nameB) midpoint | (x, y, z) world point.
    Right bone given; left mirrored. A bone with no left/right twin (head, chest) is mirrored about x=0 instead."""
    mrot = [rot[0], -rot[1], -rot[2]] if rot else None
    twin = m.mirror_name(bone)
    if twin is None:
        o = np.array(orgspec, float)
        place(m, bone, o, -out, up, back, size, mat, rot, **kw)
        place(m, bone, o, out, up, back, size, mat, mrot, **kw)
        return
    for b, r in ((bone, rot), (twin, mrot)):
        def piv(s): return pivot_world(m, b if s == "self" else (s if b == bone else m.mirror_name(s)))
        if isinstance(orgspec, str): o = piv(orgspec)
        elif isinstance(orgspec[0], str): o = (piv(orgspec[0]) + piv(orgspec[1])) / 2
        else: o = np.array(orgspec, float) * (1 if b == bone else np.array([-1, 1, 1]))
        place(m, b, o, out, up, back, size, mat, r, **kw)


def sym(m, bone, c, s, mat="P", rot=None, **kw):
    m.cube(bone, c, s, mat, rot, **kw)
    m.cube(bone, (-c[0], c[1], c[2]), s, mat, [rot[0], -rot[1], -rot[2]] if rot else None, **kw)


def hexp(m, bone, org, out, up, back, size, mat="P", c=2.0, axis="y", arch=None, pair=True):
    """Octagonal plate/sleeve: cross of two boxes plus four 45-degree corner cubes. axis = the thin/long axis (x|y|z);
    size = (x, y, z) extents in the limb frame; c = chamfer."""
    sx, sy, sz = size
    c = min(c, min(s for i, s in enumerate(size) if "xyz"[i] != axis) / 2 - 0.2)
    if c < 0.4:
        parts = [((0, 0, 0), size, None)]
    else:
        # plane axes (a, b) are the two extents perpendicular to `axis`
        if axis == "x": A, B, rot, mk = (sz, sy), (2, 1), [45, 0, 0], lambda a, b, t: (t, b, a)
        elif axis == "y": A, B, rot, mk = (sx, sz), (0, 2), [0, 45, 0], lambda a, b, t: (a, t, b)
        else: A, B, rot, mk = (sx, sy), (0, 1), [0, 0, 45], lambda a, b, t: (a, b, t)
        a, b = A; t = {"x": sx, "y": sy, "z": sz}[axis]
        def off(da, db):
            d = [0, 0, 0]; d[B[0]] = da; d[B[1]] = db
            return tuple(d)
        parts = [((0, 0, 0), mk(a, b - 2 * c, t), None), ((0, 0, 0), mk(a - 2 * c, b, t), None)]
        for ia in (-1, 1):
            for ib in (-1, 1):
                parts.append((off(ia * (a / 2 - c), ib * (b / 2 - c)), mk(c * 1.4142, c * 1.4142, t), rot))
    for d, s, r in parts:
        if pair: lpair(m, bone, org, out + d[0], up + d[1], back + d[2], s, mat, r, arch=arch)
        else: place(m, bone, org, out + d[0], up + d[1], back + d[2], s, mat, r, arch=arch)


def poly(m, bone, org, out, up, back, size, mat="P", face="x", kind="hex", pair=True, arch=None):
    """Cheap faceted plate: 'hex' = rectangle + two 45-degree diamonds (6 sides), 'pent' = rectangle + one diamond
    pointing down/back (5 sides), 'dia' = a single diamond. face = axis the plate faces (x|y|z); size = (x, y, z).
    The long plate dimension gets the points; thickness is the size along `face`."""
    sx, sy, sz = size
    if face == "x": a, b, t, mk, rot = sz, sy, sx, (lambda p, q, t: (t, q, p)), [45, 0, 0]
    elif face == "y": a, b, t, mk, rot = sx, sz, sy, (lambda p, q, t: (p, t, q)), [0, 45, 0]
    else: a, b, t, mk, rot = sx, sy, sz, (lambda p, q, t: (p, q, t)), [0, 0, 45]
    def off(dp, dq):
        d = [0, 0, 0]
        if face == "x": d[2], d[1] = dp, dq
        elif face == "y": d[0], d[2] = dp, dq
        else: d[0], d[1] = dp, dq
        return tuple(d)
    parts = []
    if kind == "dia":
        s = min(a, b); parts = [((0, 0, 0), mk(s, s, t), rot)]
    elif kind == "pent":                                   # point toward -q (down)
        s = min(a, b) / 1.4142
        parts = [(off(0, min(a, b) / 4), mk(a, b - min(a, b) / 2, t), None), (off(0, -(b / 2 - min(a, b) / 2)), mk(s, s, t), rot)]
    else:                                                  # hex: points on the long axis
        if b >= a:
            s = a / 1.4142
            parts = [((0, 0, 0), mk(a, b - a, t), None), (off(0, b / 2 - a / 2), mk(s, s, t), rot), (off(0, -(b / 2 - a / 2)), mk(s, s, t), rot)]
        else:
            s = b / 1.4142
            parts = [((0, 0, 0), mk(a - b, b, t), None), (off(a / 2 - b / 2, 0), mk(s, s, t), rot), (off(-(a / 2 - b / 2), 0), mk(s, s, t), rot)]
    for d, s_, r in parts:
        if pair: lpair(m, bone, org, out + d[0], up + d[1], back + d[2], s_, mat, r, arch=arch)
        else: place(m, bone, org, out + d[0], up + d[1], back + d[2], s_, mat, r, arch=arch)
