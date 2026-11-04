"""Builds the exoframe flight modules (OBSOLETE-style field hardware): geo, texture atlas and item icon for
flight_booster (twin turbine rocket pack), vtol_wings (swing wings with ducted fans), drone_lifter (guarded quad-rotor).

Run with any python that has numpy + Pillow:  python tools/build_flight_equipment.py
Local frame = ExoframeFlightBoosterLayer mount: torso pivot + (0, 3.2, 5.8) exoframe px. +z is the back, +x the mech's left.
Keep-out (local px): power pack z<=7.0 for y -8.4..-1.8, exhaust stacks / roll cage z<=5.4, pilot head z<=2.7.
So every part sits at z >= 7.0. Bones the Java animates (fan_*, left/right_wing, nozzle_*) carry no rest rotation.
"""
import json, math, os
import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources", "assets", "obsolete")
TEX = 256
P = 32  # atlas patch size
MATS = ["gun", "gun_dk", "olive", "olive_dk", "hazard", "stencil", "heat", "glow", "nav_r", "nav_g", "nav_w",
        "rubber", "steel", "blade", "vent", "led_b", "amber", "brass"]
rng = np.random.default_rng(7)

# ---------------------------------------------------------------- texture atlas
def noise(s, amp):
    n = rng.normal(0, 1, (s, s))
    k = np.ones(3) / 3
    for _ in range(2):
        n = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 0, n)
        n = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 1, n)
    return n / (np.abs(n).max() + 1e-6) * amp + rng.normal(0, amp * 0.35, (s, s))

def worn(base, chip=(150, 150, 140), grime=(40, 36, 30), chips=0.035, panel=True):
    a = np.array(base, float)[None, None] + noise(P, 14)[..., None]
    y, x = np.mgrid[0:P, 0:P]
    a *= (0.9 + 0.12 * (y / P))[..., None] ** -1                         # top-lit, grime pooling low
    a = a * (1 - 0.35 * (y / P) ** 3)[..., None] + np.array(grime) * 0.35 * ((y / P) ** 3)[..., None]
    if panel:
        a[[0, P - 1], :] *= 0.62; a[:, [0, P - 1]] *= 0.62
        a[P // 2, :] *= 0.75
        for bx, by in ((2, 2), (P - 3, 2), (2, P - 3), (P - 3, P - 3)):
            a[by, bx] = (190, 186, 170)                                   # rivets
    m = rng.random((P, P)) < chips
    a[m] = chip
    edge = (x < 2) | (x > P - 3) | (y < 2) | (y > P - 3)
    a[edge & (rng.random((P, P)) < 0.25)] = chip                          # worn edges
    return a

def patch(name):
    y, x = np.mgrid[0:P, 0:P]
    if name == "gun": return worn((78, 84, 88))
    if name == "gun_dk": return worn((46, 50, 54), chip=(110, 112, 110))
    if name == "olive": return worn((92, 98, 58), chip=(140, 138, 120))
    if name == "olive_dk": return worn((64, 70, 40), chip=(120, 118, 100))
    if name == "hazard":
        a = np.where((((x + y) // 6) % 2 == 0)[..., None], np.array([214, 168, 30.]), np.array([30, 28, 26.]))
        return a + noise(P, 10)[..., None] - (rng.random((P, P)) < 0.06)[..., None] * 80
    if name == "stencil":
        a = worn((92, 98, 58), chip=(140, 138, 120))
        glyphs = {"T": ["111", "010", "010", "010", "010"], "H": ["101", "101", "111", "101", "101"],
                  "R": ["110", "101", "110", "101", "101"], "2": ["111", "001", "111", "100", "111"],
                  "-": ["000", "000", "111", "000", "000"], "0": ["111", "101", "101", "101", "111"],
                  "7": ["111", "001", "010", "010", "010"], "!": ["010", "010", "010", "000", "010"]}
        for row, text in ((5, "THR-07"), (14, "!0-H2")):
            for i, ch in enumerate(text):
                for gy, line in enumerate(glyphs[ch]):
                    for gx, c in enumerate(line):
                        if c == "1" and rng.random() > 0.12:
                            a[row + gy, 4 + i * 4 + gx] = (214, 210, 190)
        a[23:26, 3:29] = (190, 50, 40)                                     # red warning band
        return a
    if name == "heat":                                                     # straw -> bronze -> blue -> purple temper bands
        t = y / (P - 1)
        stops = np.array([(150, 140, 120), (176, 128, 64), (120, 70, 110), (54, 76, 150), (40, 54, 92)], float)
        idx = t * (len(stops) - 1); i0 = np.floor(idx).astype(int).clip(0, len(stops) - 2); f = (idx - i0)[..., None]
        return stops[i0] * (1 - f) + stops[i0 + 1] * f + noise(P, 10)[..., None]
    if name == "glow":
        r = np.hypot(x - P / 2, y - P / 2) / (P / 2)
        return np.stack([255 - 10 * r, 230 - 120 * r, 160 - 150 * r], -1).clip(0, 255)
    if name in ("nav_r", "nav_g", "nav_w", "led_b", "amber"):
        c = {"nav_r": (255, 60, 50), "nav_g": (70, 255, 110), "nav_w": (255, 255, 240), "led_b": (90, 200, 255),
             "amber": (255, 170, 40)}[name]
        r = np.hypot(x - P / 2, y - P / 2) / (P / 2)
        return np.array(c, float)[None, None] * (1 - 0.25 * r)[..., None] + 40 * (r < 0.4)[..., None]
    if name == "rubber": return np.full((P, P, 3), 30.) + noise(P, 6)[..., None]
    if name == "steel": return worn((128, 132, 134), chip=(180, 182, 180), chips=0.02, panel=False)
    if name == "blade":
        a = np.full((P, P, 3), 38.) + noise(P, 6)[..., None]
        a[:, :5] = (220, 180, 30); a[:, -5:] = (220, 180, 30)             # hi-vis tips on both ends
        return a
    if name == "vent":
        a = np.full((P, P, 3), 26.) + noise(P, 5)[..., None]
        a[::3, :] = (70, 74, 76); return a
    if name == "brass": return worn((150, 116, 52), chip=(200, 170, 100), panel=False)
    raise KeyError(name)

def build_atlas():
    img = np.zeros((TEX, TEX, 4), np.uint8)
    for i, m in enumerate(MATS):
        u, v = (i % 8) * P, (i // 8) * P
        img[v:v + P, u:u + P, :3] = np.clip(patch(m), 0, 255).astype(np.uint8)
        img[v:v + P, u:u + P, 3] = 255
    return img

def mat_origin(m):
    i = MATS.index(m); return (i % 8) * P, (i // 8) * P

# ---------------------------------------------------------------- geometry helpers
FACE_DIMS = {"north": (0, 1), "south": (0, 1), "east": (2, 1), "west": (2, 1), "up": (0, 2), "down": (0, 2)}

class Geo:
    def __init__(self, ident):
        self.ident, self.bones = ident, []
    def bone(self, name, pivot, parent=None, rotation=None):
        b = {"name": name, "pivot": [round(v, 3) for v in pivot], "cubes": []}
        if parent: b["parent"] = parent
        if rotation: b["rotation"] = rotation
        self.bones.append(b); return b
    def box(self, b, o, s, mat, rot=None, pv=None):
        faces = mat if isinstance(mat, dict) else {}
        default = faces.get("*", mat if isinstance(mat, str) else "gun")
        uv = {}
        for f, (a1, a2) in FACE_DIMS.items():
            m = faces.get(f, default)
            u0, v0 = mat_origin(m)
            w, h = max(1.0, min(s[a1] * 2, P - 2)), max(1.0, min(s[a2] * 2, P - 2))
            ou, ov = rng.uniform(0, P - 2 - w) + 1, rng.uniform(0, P - 2 - h) + 1
            if m in ("glow", "nav_r", "nav_g", "nav_w", "led_b", "amber"):
                ou, ov = (P - w) / 2, (P - h) / 2                          # lights sample their hot centre
            uv[f] = {"uv": [round(u0 + ou, 2), round(v0 + ov, 2)], "uv_size": [round(w, 2), round(h, 2)]}
        c = {"origin": [round(v, 3) for v in o], "size": [round(v, 3) for v in s], "uv": uv}
        if rot:
            c["rotation"] = rot
            c["pivot"] = [round(v, 3) for v in (pv if pv else [o[i] + s[i] / 2 for i in range(3)])]
        b["cubes"].append(c)
    def cbox(self, b, c, s, mat, rot=None, pv=None):
        self.box(b, [c[i] - s[i] / 2 for i in range(3)], s, mat, rot, pv)
    def octo(self, b, c, d, h, mat, axis="y"):
        """Octagonal prism (two boxes, one turned 45 deg) centred at c, diameter d, length h along axis."""
        s = {"y": [d * 0.83, h, d * 0.83], "x": [h, d * 0.83, d * 0.83], "z": [d * 0.83, d * 0.83, h]}[axis]
        r = {"y": [0, 45, 0], "x": [45, 0, 0], "z": [0, 0, 45]}[axis]
        self.cbox(b, c, s, mat); self.cbox(b, c, s, mat, r, c)
    def ring(self, b, c, r, t, h, mat, axis="y"):
        """Octagonal hoop: 8 tangent segments of thickness t, height h, around axis through c."""
        L = 2 * r * math.tan(math.pi / 8) + t * 0.45
        for k in range(4):
            ang = k * 45
            for sgn in (1, -1):
                if axis == "y":
                    seg, rot = [t, h, L], [0, ang, 0]
                else:  # axis z
                    seg, rot = [t, L, h], [0, 0, ang]
                cen = [c[0] + sgn * r, c[1], c[2]]
                o = [cen[i] - seg[i] / 2 for i in range(3)]
                self.box(b, o, seg, mat, rot if ang else None, c)
    def write(self, path, bw, bh):
        bones = []
        for b in self.bones:
            if not b["cubes"]: del b["cubes"]
            bones.append(b)
        d = {"format_version": "1.12.0", "minecraft:geometry": [{"description": {
            "identifier": self.ident, "texture_width": TEX, "texture_height": TEX, "visible_bounds_width": bw,
            "visible_bounds_height": bh, "visible_bounds_offset": [0, 1, 0]}, "bones": bones}]}
        with open(path, "w") as f: json.dump(d, f, indent=1)

def mount(g):
    """Common dock: clamp plate on the pack's rear face with rails, lugs and a hazard-striped release lever."""
    root = g.bone("root", [0, 0, 0])
    dm = g.bone("docking_mount", [0, 0, 7.2], "root")
    g.box(dm, [-5.5, -9, 7.0], [11, 18, 1.2], "gun_dk")
    for sx in (-1, 1):
        g.box(dm, [sx * 4.2 - 0.45, -9.2, 8.2], [0.9, 18.4, 0.8], "steel")                 # dovetail rails
        for y in (-7.5, 6.5):
            g.box(dm, [sx * 5.1 - 0.6, y, 7.3], [1.2, 1.4, 1.4], "gun")                    # clamp lugs
    g.box(dm, [-1.5, -9.8, 7.4], [3, 0.8, 1.6], {"*": "hazard", "up": "gun"})               # quick-release lever
    return root, dm

# ---------------------------------------------------------------- flight booster: twin turbine rocket pack
def flight_booster():
    g = Geo("geometry.exoframe_flight_booster"); _, dm = mount(g)
    g.box(dm, [-4, -6.5, 8.4], [8, 15, 5], {"*": "olive", "south": "stencil"})             # armoured cowl
    g.box(dm, [-3.5, 8.5, 8.8], [7, 1, 4], "olive_dk")
    g.box(dm, [-3.6, -2, 13.4], [7.2, 8, 0.7], {"*": "olive_dk", "south": "stencil"})      # bolt-on rear plate
    g.box(dm, [-4.2, -6.2, 13.2], [8.4, 1.4, 0.4], "hazard")
    g.box(dm, [-1.8, 3.2, 14.1], [3.6, 0.5, 0.5], "steel")                                 # grab handle
    for sx in (-1, 1):
        g.box(dm, [sx * 1.6 - 0.25, 3.2, 13.9], [0.5, 0.5, 0.7], "steel")
    for y in (-5, -3.5):
        g.box(dm, [-3, y, 13.3], [6, 0.6, 0.2], "vent")                                    # cooling louvres
    # saddle fuel tank across the top, hazard-banded, strapped down
    g.octo(dm, [0, 11, 10.6], 3.8, 12.5, "olive", "x")
    for sx in (-1, 1):
        g.octo(dm, [sx * 6.4, 11, 10.6], 3.3, 0.6, "gun_dk", "x")                           # end caps
        g.box(dm, [sx * 3.6 - 0.3, 8.9, 8.6], [0.6, 4.2, 4.0], "steel")                      # straps
        g.box(dm, [sx * 5.2 - 0.4, 10.4, 8.3], [0.8, 0.8, 0.8], "hazard")
    g.octo(dm, [0, 12.9, 10.6], 1.2, 0.8, "brass")                                          # filler cap
    g.box(dm, [2.6, 12.4, 12.3], [0.3, 6, 0.3], "rubber")                                   # whip antenna
    g.box(dm, [-0.6, 12.9, 9.4], [1.2, 0.8, 1.2], "amber")                                  # beacon
    for sx in (-1, 1):
        x = sx * 7.0
        # turbine nacelle: core, intake lip, fan face, exhaust collar
        g.octo(dm, [x, 1.5, 11.5], 4.8, 11, "gun")
        g.octo(dm, [x, 7.6, 11.5], 5.6, 1.4, "gun_dk")
        g.cbox(dm, [x, 8.36, 11.5], [3.6, 0.1, 3.6], "vent")
        g.octo(dm, [x, 8.3, 11.5], 1.2, 0.5, "steel")                                        # spinner
        g.octo(dm, [x, -4.6, 11.5], 4.2, 1.2, "heat")
        g.cbox(dm, [x, 1.5, 11.5], [5.1, 0.6, 5.1], "steel")                                 # mid flange
        # olive armour cowling over the outer half + corrugated heat shield
        g.box(dm, [x + (0.6 if sx > 0 else -3.8), -3, 8.6], [3.2, 9.6, 1.2], "olive")
        g.box(dm, [x + (2.7 if sx > 0 else -3.3), -3.6, 9.2], [0.6, 10.4, 4.6], {"*": "olive_dk", "east" if sx > 0 else "west": "stencil"})
        for k in range(4):
            g.box(dm, [x + (3.3 if sx > 0 else -3.6), -3 + k * 2.4, 9.6], [0.3, 1.2, 3.8], "heat")
        g.box(dm, [x + (3.4 if sx > 0 else -3.8), 4.2, 11.0], [0.4, 0.8, 0.8], "nav_r" if sx > 0 else "nav_g")
        # fuel line tank -> nacelle, RCS quad on the shoulder
        g.box(dm, [sx * 4.6 - 0.3, 7.0, 12.4], [0.6, 2.6, 0.6], "brass")
        g.cbox(dm, [x, 9.0, 13.9], [1.2, 1.2, 1.2], "gun_dk")
        g.cbox(dm, [x, 9.0, 14.7], [0.6, 0.6, 0.5], "heat")
        g.cbox(dm, [x + sx * 0.8, 9.0, 13.9], [0.5, 0.6, 0.6], "heat")
        # gimballed bell: throat ring, bell stages, glowing throat, actuators (move with the bone)
        n = g.bone("nozzle_left" if sx > 0 else "nozzle_right", [x, -5.2, 11.5], "docking_mount")
        g.octo(n, [x, -5.6, 11.5], 3.4, 0.8, "steel")
        g.octo(n, [x, -6.5, 11.5], 2.8, 1.0, "heat")
        g.octo(n, [x, -7.7, 11.5], 3.6, 1.4, "heat")
        g.octo(n, [x, -9.2, 11.5], 4.4, 1.6, "heat")
        g.octo(n, [x, -10.4, 11.5], 5.0, 0.8, "gun_dk")
        g.cbox(n, [x, -10.75, 11.5], [3.4, 0.1, 3.4], "glow")
        for dz in (-1, 1):
            g.box(n, [x - 0.2, -8.4, 11.5 + dz * 2.1 - 0.2], [0.4, 3.0, 0.4], "steel")      # gimbal actuators
    return g

# ---------------------------------------------------------------- VTOL: swing wings with wingtip ducted fans
def vtol_wings():
    g = Geo("geometry.flight_module_vtol_glide"); _, dm = mount(g)
    g.box(dm, [-3.2, -6, 8.2], [6.4, 14, 4.2], {"*": "olive", "south": "stencil"})          # dorsal spine fairing
    g.box(dm, [-2.6, 8, 8.6], [5.2, 1.6, 3.4], "olive_dk")
    g.box(dm, [-2.2, -4, 12.4], [4.4, 9, 1.0], "gun")                                        # turboshaft housing
    for k in range(3):
        g.box(dm, [-1.8, -3 + k * 2.2, 13.4], [3.6, 0.7, 0.2], "vent")
    g.octo(dm, [0, -6.6, 10.4], 3.2, 1.2, "heat")                                            # APU exhaust
    g.box(dm, [-0.25, 9.6, 10.6], [0.5, 2.6, 2.0], "gun_dk")                                  # dorsal fin antenna
    g.box(dm, [-0.4, 12.2, 11.2], [0.8, 0.6, 0.8], "nav_w")                                   # tail strobe
    g.box(dm, [-3.3, 7.6, 8.2], [6.6, 0.4, 4.2], "hazard")
    for sx in (-1, 1):
        g.box(dm, [sx * 5.2 - 1.3, 4.8, 8.4], [2.6, 3.6, 4.6], "gun_dk")                      # wing-root hinge block
        g.octo(dm, [sx * 5.5, 6.6, 10.4], 1.4, 4.4, "steel")                                   # hinge pin
        g.box(dm, [sx * 3.6 - 0.3, 2, 8.4], [0.6, 3, 3.2], "steel")                            # actuator strut
    for sx in (-1, 1):
        name = "left_wing" if sx > 0 else "right_wing"
        rx = sx * 5.5
        w = g.bone(name, [rx, 6.6, 10.4], "docking_mount")
        def X(a, b):  # outboard span a..b (a<b) mirrored per side
            return (a, b - a) if sx > 0 else (-b, b - a)
        o, l = X(6.2, 16.2); g.box(w, [o, 6.0, 8.0], [l, 1.2, 5.6], {"*": "olive", "up": "olive", "down": "gun_dk"})
        o, l = X(6.2, 16.2); g.box(w, [o, 6.2, 7.2], [l, 0.8, 0.8], "gun")                    # leading edge
        o, l = X(6.4, 8.0); g.box(w, [o, 7.2, 8.2], [l, 0.15, 5.2], "hazard")                 # walk-no-step band
        o, l = X(10.5, 13.5); g.box(w, [o, 7.2, 9.2], [l, 0.1, 3.0], "stencil")
        o, l = X(5.0, 6.4); g.box(w, [o, 5.6, 8.8], [l, 2.0, 3.2], "gun_dk")                   # root knuckle
        f = g.bone(name.replace("wing", "flap"), [rx, 6.4, 13.6], name, [-14, 0, 0])           # drooped trailing flaps
        o, l = X(6.6, 11.2); g.box(f, [o, 6.1, 13.6], [l, 0.5, 2.2], "olive_dk")
        o, l = X(11.4, 15.8); g.box(f, [o, 6.1, 13.6], [l, 0.5, 2.2], "olive_dk")
        o, l = X(8.0, 14.0); g.box(w, [o, 4.8, 10.0], [l, 1.2, 1.4], "gun_dk")                 # under-wing fuel pod
        # wingtip ducted fan: octagonal duct, stator cross, hub, static blades, lip lights
        c = [sx * 20.4, 6.6, 10.8]
        g.ring(w, c, 4.4, 0.9, 2.6, "olive")
        g.ring(w, [c[0], 7.95, c[2]], 4.75, 0.5, 0.3, "gun_dk")                                # duct lip
        g.cbox(w, c, [8.6, 0.4, 0.5], "gun_dk"); g.cbox(w, c, [0.5, 0.4, 8.6], "gun_dk")       # stators
        g.octo(w, [c[0], 6.9, c[2]], 1.8, 2.0, "steel")
        g.cbox(w, [c[0], 7.4, c[2]], [8.0, 0.15, 0.9], "blade", [0, 30, 0], c)
        g.cbox(w, [c[0], 7.4, c[2]], [8.0, 0.15, 0.9], "blade", [0, -60, 0], c)
        g.cbox(w, [c[0], 5.3, c[2]], [7.0, 0.1, 7.0], "vent")                                  # bottom grille
        g.box(w, [c[0] + sx * 4.9 - 0.4, 6.2, c[2] - 0.6], [0.8, 1.0, 1.2], "nav_r" if sx > 0 else "nav_g")
        g.box(w, [c[0] - 0.4, 6.4, c[2] + 5.0], [0.8, 0.6, 0.6], "nav_w")
        o, l = X(16.0, 16.4); g.box(w, [o, 4.6, 9.8], [l, 2.0, 2.0], "hazard")                 # duct pylon collar
    return g

# ---------------------------------------------------------------- drone lifter: guarded quad-rotor carrier
def drone_lifter():
    g = Geo("geometry.flight_module_drone_lifter"); _, dm = mount(g)
    g.box(dm, [-4, -5, 8.2], [8, 12.5, 5.2], {"*": "gun", "south": "stencil"})               # battery / controller box
    for k in range(3):
        g.box(dm, [-3.4, -4 + k * 3.6, 13.4], [6.8, 2.6, 0.5], "olive")                        # battery cassettes
        g.box(dm, [-3.6, -2 + k * 3.6, 13.4], [0.4, 0.4, 0.6], "led_b")
    g.box(dm, [-4.1, 6.5, 8.1], [8.2, 0.8, 5.4], "hazard")
    g.box(dm, [-1.2, 7.5, 9.6], [2.4, 6.2, 2.4], "steel")                                       # mast
    g.cbox(dm, [0, 14.2, 11], [5, 1.6, 5], {"*": "gun_dk", "up": "stencil"})                    # rotor hub plate
    g.box(dm, [-0.2, 15.0, 12.8], [0.3, 4, 0.3], "rubber")                                      # GPS stalk
    g.octo(dm, [0, 19.2, 12.95], 1.2, 0.6, "nav_w")
    # cargo winch + twin hooks
    g.box(dm, [-3.4, -7.2, 9.6], [6.8, 2.2, 2.6], "gun_dk")
    g.octo(dm, [0, -6.1, 10.9], 2.2, 5.6, "brass", "x")
    for sx in (-1, 1):
        x = sx * 2.0
        g.box(dm, [x - 0.15, -12, 10.75], [0.3, 4.8, 0.3], "rubber")                            # cable
        g.box(dm, [x - 0.5, -12.8, 10.4], [1.0, 1.0, 1.0], "steel")                             # swivel
        g.box(dm, [x - 0.3, -15.2, 10.6], [0.6, 2.4, 0.6], "hazard")                            # shank
        g.box(dm, [x - 0.3, -15.8, 10.6], [0.6, 0.6, 2.2], "hazard")                            # bend
        g.box(dm, [x - 0.3, -15.6, 12.2], [0.6, 1.4, 0.6], "hazard")                            # tip
    for key, sx, sz in (("fl", 1, -1), ("fr", -1, -1), ("rl", 1, 1), ("rr", -1, 1)):
        c = [sx * 14.0, 16.0, 11.0 + sz * 8.0]
        r = g.bone("rotor_" + key, c, "docking_mount")
        dx, dz = c[0], c[2] - 11.0
        L = math.hypot(dx, dz); ang = math.degrees(math.atan2(-dz, dx)) * (1 if sx > 0 else 1)
        mid = [dx / 2, 14.2, 11.0 + dz / 2]
        # carbon arm: square tube from hub to motor (rotated about Y) + olive fairing on top
        g.cbox(r, mid, [L, 0.9, 0.9], "gun_dk", [0, ang if sx > 0 else ang - 180, 0], mid)
        g.cbox(r, [mid[0], 14.75, mid[2]], [L * 0.6, 0.3, 1.3], "olive", [0, ang if sx > 0 else ang - 180, 0], [mid[0], 14.75, mid[2]])
        # motor pod, guard hoop with struts, LEDs
        g.octo(r, [c[0], 14.6, c[2]], 2.2, 2.4, "gun")
        g.octo(r, [c[0], 15.9, c[2]], 1.6, 0.4, "steel")
        g.ring(r, c, 6.2, 0.45, 1.3, "olive_dk")
        g.ring(r, [c[0], 16.75, c[2]], 6.2, 0.6, 0.2, "hazard")
        for a in (45, -45):
            g.cbox(r, [c[0], 15.2, c[2]], [12.4, 0.35, 0.35], "steel", [0, a, 0], [c[0], 15.2, c[2]])
        g.octo(r, [c[0], 13.1, c[2]], 1.0, 0.6, "nav_r" if sx > 0 else "nav_g")                 # under-pod nav light
        g.box(r, [c[0] + sx * 6.4 - 0.3, 15.5, c[2] - 0.3], [0.6, 0.8, 0.6], "led_b")
        # spinning rotor: hub + four composite blades with hi-vis tips (Java spins fan_* about Y)
        f = g.bone("fan_" + key, c, "rotor_" + key)
        g.octo(f, [c[0], 16.3, c[2]], 1.2, 0.6, "gun_dk")
        g.cbox(f, [c[0], 16.25, c[2]], [11.2, 0.15, 1.0], "blade")
        g.cbox(f, [c[0], 16.25, c[2]], [1.0, 0.15, 11.2], "blade")
    return g

# ---------------------------------------------------------------- tiny splat renderer for item icons
def to_faces(geo, atlas):
    bones = {b["name"]: b for b in geo.bones}
    def chain(n):  # bone rest rotations, child first
        out = []
        while n:
            b = bones[n]
            if b.get("rotation"): out.append((np.array(b["pivot"], float), b["rotation"]))
            n = b.get("parent")
        return out
    faces = []
    for b in geo.bones:
        ch = chain(b["name"])
        for c in b.get("cubes", []):
            o, s = np.array(c["origin"], float), np.array(c["size"], float)
            X, Y, Z = s
            defs = {"north": (o + [X, Y, 0], [-X, 0, 0], [0, -Y, 0]), "south": (o + [0, Y, Z], [X, 0, 0], [0, -Y, 0]),
                    "east": (o + [X, Y, Z], [0, 0, -Z], [0, -Y, 0]), "west": (o + [0, Y, 0], [0, 0, Z], [0, -Y, 0]),
                    "up": (o + [X, Y, Z], [-X, 0, 0], [0, 0, -Z]), "down": (o + [X, 0, 0], [-X, 0, 0], [0, 0, Z])}
            mats = [(np.array(c.get("pivot", [0, 0, 0]), float), c.get("rotation", [0, 0, 0]))] + ch
            for k, (p0, e1, e2) in defs.items():
                p0, e1, e2 = np.array(p0, float), np.array(e1, float), np.array(e2, float)
                for pv, r in mats:
                    M = Rm(*r); p0 = M @ (p0 - pv) + pv; e1 = M @ e1; e2 = M @ e2
                uv = c["uv"][k]; u, v = uv["uv"]; w, h = uv["uv_size"]
                col = atlas[int(v + h / 2), int(u + w / 2), :3].astype(float)
                faces.append((p0, e1, e2, col))
    return faces

def Rm(rx, ry, rz):
    rx, ry, rz = map(math.radians, (rx, ry, rz))
    Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx

def icon(geo, atlas, out, S=128):
    faces = to_faces(geo, atlas)
    Rv = Rm(20, 0, 0) @ Rm(0, 145, 0)
    pts = np.concatenate([np.array([f[0], f[0] + f[1], f[0] + f[2]]) for f in faces]) @ Rv.T
    lo, hi = pts.min(0), pts.max(0); sc = (S - 8) / max(hi[0] - lo[0], hi[1] - lo[1]); mid = (lo + hi) / 2
    img = np.zeros((S, S, 4)); zb = np.full((S, S), -1e9)
    light = np.array([0.3, 0.8, 0.5]); light /= np.linalg.norm(light)
    for p0, e1, e2, col in faces:
        n = np.cross(e2, e1); ln = np.linalg.norm(n)
        if ln < 1e-9: continue
        nv = Rv @ (n / ln)
        if nv[2] > 0.02: continue
        n1 = max(2, int(np.linalg.norm(e1) * sc * 1.5) + 1); n2 = max(2, int(np.linalg.norm(e2) * sc * 1.5) + 1)
        A, B = np.meshgrid((np.arange(n1) + .5) / n1, (np.arange(n2) + .5) / n2, indexing="ij")
        q = (p0[None] + A.ravel()[:, None] * e1 + B.ravel()[:, None] * e2) @ Rv.T
        sx = (S / 2 + (q[:, 0] - mid[0]) * sc).astype(int); sy = (S / 2 - (q[:, 1] - mid[1]) * sc).astype(int)
        d = -q[:, 2]; ok = (sx >= 0) & (sx < S) & (sy >= 0) & (sy < S); sx, sy, d = sx[ok], sy[ok], d[ok]
        shade = 0.55 + 0.6 * max(0.0, float((n / ln) @ light))
        m = d > zb[sy, sx]; zb[sy[m], sx[m]] = d[m]
        img[sy[m], sx[m], :3] = np.clip(col * shade, 0, 255); img[sy[m], sx[m], 3] = 255
    im = Image.fromarray(img.astype(np.uint8), "RGBA").resize((32, 32), Image.LANCZOS)
    a = np.array(im); a[..., 3] = np.where(a[..., 3] > 100, 255, 0)                         # crisp cutout edges
    Image.fromarray(a).save(out)

# ---------------------------------------------------------------- validation + main
REQUIRED = {"flight_booster": ["root", "docking_mount", "nozzle_left", "nozzle_right"],
            "vtol_wings": ["root", "docking_mount", "left_wing", "right_wing"],
            "drone_lifter": ["root", "docking_mount", "fan_fl", "fan_fr", "fan_rl", "fan_rr"]}
ANIMATED = {"nozzle_left", "nozzle_right", "left_wing", "right_wing", "fan_fl", "fan_fr", "fan_rl", "fan_rr"}

def validate(name, path):
    g = json.load(open(path))["minecraft:geometry"][0]
    names = [b["name"] for b in g["bones"]]
    assert len(set(names)) == len(names), "duplicate bones"
    for r in REQUIRED[name]: assert r in names, f"{name}: missing {r}"
    n = 0
    for b in g["bones"]:
        assert not (b["name"] in ANIMATED and b.get("rotation")), f"{b['name']} must have no rest rotation"
        for c in b.get("cubes", []):
            n += 1
            assert min(c["size"]) > 0, f"zero-size cube in {b['name']}"
            for f, uv in c["uv"].items():
                assert 0 <= uv["uv"][0] and uv["uv"][0] + uv["uv_size"][0] <= TEX and 0 <= uv["uv"][1] and uv["uv"][1] + uv["uv_size"][1] <= TEX, (b["name"], f)
            # keep-out: nothing forward of the pack's rear face
            o = c["origin"]; assert o[2] >= 6.9 or o[1] >= 13 or o[0] >= 8 or o[0] + c["size"][0] <= -8 or c.get("rotation"), f"{b['name']} cube intrudes into pack/pilot zone: {c['origin']}"
    return n

if __name__ == "__main__":
    atlas = build_atlas()
    for name, fn, (bw, bh) in (("flight_booster", flight_booster, (4, 4)), ("vtol_wings", vtol_wings, (6, 4)),
                               ("drone_lifter", drone_lifter, (6, 5))):
        geo = fn()
        gp = os.path.join(ROOT, "geo", "equipment", name + ".geo.json")
        geo.write(gp, bw, bh)
        Image.fromarray(atlas, "RGBA").save(os.path.join(ROOT, "textures", "entity", "equipment", name + ".png"))
        icon(geo, atlas, os.path.join(ROOT, "textures", "item", "module_" + name + ".png"))
        print(f"{name}: {validate(name, gp)} cubes, {len(geo.bones)} bones")
