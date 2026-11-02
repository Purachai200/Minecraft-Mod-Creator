#!/usr/bin/env python3
"""Mobile Suit Trailer (Type 74-style heavy transporter): armored cab-over tractor + gooseneck lowboy with
hydraulic mech cradle, 6 axle lines of dual tyres, outriggers and ratchet straps.
Model -Z is the cab end (Java vehicle +Z forward == model -Z), driver cushion y=18 at z=-72, deck top y=22.
Run: python3 scripts/gen_mobile_suit_trailer.py [--preview out_dir]"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from generate_transport_assets import TextureDrawer, make_png, per_face_uv, rod

ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources", "assets", "titancombat")
GEO = os.path.join(ROOT, "geo", "mobile_suit_trailer.geo.json")
ANIM = os.path.join(ROOT, "animations", "mobile_suit_trailer.animation.json")
TEX = os.path.join(ROOT, "textures", "entity", "transport", "mobile_suit_trailer.png")
ICON = os.path.join(ROOT, "textures", "item", "mobile_suit_trailer.png")

# 64px atlas cells (per_face_uv crops each face at its cell)
ARMOR, ARMOR2, GLASS, GRILLE, STEEL, DECK, HAZ, STRAP = [(i * 64, 0) for i in range(8)]
TIRE, RIM, CHROME, SHIELD, LAMP_A, INTERIOR, RUBBER, CYL = [(i * 64, 64) for i in range(8)]
MUD, SEAT, YELLOW, CHAIN = (0, 128), (64, 128), (128, 128), (192, 128)
LAMP_R, LAMP_W, RIM_L = (LAMP_A[0] + 32, 64), (LAMP_A[0], 96), (RIM[0] + 24, 64)

R_TRACTOR, R_TRAILER = 9, 7
TRAILER_AXLES = [4, 18, 32, 46, 60, 74]


# ---------------------------------------------------------------- geometry helpers
def box(x0, y0, z0, x1, y1, z1, uv):
    a, b = (min(x0, x1), min(y0, y1), min(z0, z1)), (max(x0, x1), max(y0, y1), max(z0, z1))
    return {"origin": [round(v, 3) for v in a], "size": [round(b[i] - a[i], 3) for i in range(3)], "uv": list(uv)}


def mir(c):
    """Mirror a cube across X=0 (rods: flip pivot x and the z-rotation)."""
    m = json.loads(json.dumps(c))
    m["origin"][0] = round(-(c["origin"][0] + c["size"][0]), 3)
    if "pivot" in c:
        m["pivot"][0] = -c["pivot"][0]
        m["rotation"][2] = -c["rotation"][2]
        m["rotation"][1] = -c["rotation"][1]
    return m


def both(*cubes):
    out = []
    for c in cubes:
        out += [c, mir(c)]
    return out


def tyre(cx, cy, cz, x0, w, r, rim_uv, outer_sign):
    t = [{"origin": [x0, cy - r, cz - r], "size": [w, 2 * r, 2 * r], "pivot": [cx, cy, cz], "rotation": [a, 0, 0],
          "uv": list(TIRE)} for a in (0, 30, -30)]
    rr = r - 2
    rim_x = x0 + w - 0.5 if outer_sign > 0 else x0 - 0.5
    t += [{"origin": [rim_x, cy - rr, cz - rr], "size": [1, 2 * rr, 2 * rr], "pivot": [cx, cy, cz],
           "rotation": [a, 0, 0], "uv": list(rim_uv)} for a in (0, 45)]
    return t


def wheel_bone(name, cx, cy, cz, r, dual, rim_uv):
    s = 1 if cx > 0 else -1
    cubes = []
    if dual:  # inner + outer tyre, 4 wide each with a 1 gap
        for off in (-4.5, 0.5):
            x0 = cx + off if s > 0 else cx - off - 4
            cubes += tyre(cx, cy, cz, x0, 4, r, rim_uv, s)
    else:
        cubes += tyre(cx, cy, cz, cx - 3, 6, r, rim_uv, s)
    hx = cx + (4.5 if dual else 3) if s > 0 else cx - (4.5 if dual else 3) - 1.5
    cubes.append(box(hx, cy - 2, cz - 2, hx + 1.5, cy + 2, cz + 2, CHROME))  # hub cap
    return {"name": name, "parent": "root", "pivot": [cx, cy, cz], "cubes": cubes}


# ---------------------------------------------------------------- model
def build_bones():
    bones = [{"name": "root", "pivot": [0, 0, 0]}, {"name": "body", "parent": "root", "pivot": [0, 10, 0]}]

    # ===== TRACTOR FRAME =====
    f = []
    f += both(box(6, 10, -104, 10, 16, -24, STEEL))                      # frame rails
    for z in (-96, -78, -60, -44, -28):
        f.append(box(-6, 11, z, 6, 15, z + 2, STEEL))                    # crossmembers
    f.append(box(-28, 7, -108, 28, 15, -104, HAZ))                       # push bumper
    f.append(box(-28, 15, -108, 28, 16, -104, STEEL))
    f += both(box(16, 4, -109, 19, 15, -106, STEEL), box(16, 5, -111, 19, 8, -108, YELLOW))  # tow hooks
    f.append(box(-8, 9, -110, 8, 14, -108, CYL))                         # winch drum
    f.append(box(-3, 9.5, -111, 3, 13.5, -110, CHAIN))                   # fairlead/cable
    f += both(box(26, 15, -109, 28, 30, -107, STEEL))                    # brush-guard uprights
    f.append(box(-28, 29, -110, 28, 31, -107, STEEL))                    # brush-guard top bar
    f.append(box(-19, 8, -90, 19, 11, -86, STEEL))                       # front axle beam
    for z in (-52, -38):
        f.append(box(-19, 7, z - 2, 19, 11, z + 2, STEEL))               # drive axle housing
        f.append(box(-5, 5, z - 4, 5, 13, z + 4, CYL))                   # differential
    f.append(box(-1.5, 8, -50, 1.5, 11, -40, CHROME))                    # inter-axle driveshaft
    f.append(box(-1.5, 9, -84, 1.5, 12, -54, CHROME))                    # main driveshaft
    f += both(box(17, 6, -56, 19, 14, -34, STEEL))                       # walking beam suspension
    f += both(box(14, 7, -76, 24, 16, -62, CYL))                         # fuel / air tanks
    f += both(box(14, 6.5, -75, 24, 7, -63, STRAP))
    f += both(box(19, 20, -98, 29, 21, -78, ARMOR2))                     # front fender
    f += both(rod((19.5, 21, -78), (19.5, 15, -74), 10, 1, ARMOR2))
    f += both(box(19, 20, -60, 29, 21, -30, ARMOR2))                     # tandem fender
    f += both(box(20, 4, -30, 28, 19, -29, RUBBER))                      # mud flaps
    f.append(box(-13, 16, -54, 13, 18, -34, STEEL))                      # fifth-wheel plate
    f.append(box(-10, 18, -52, 10, 19, -40, CHROME))
    bones.append({"name": "tractor_frame", "parent": "body", "pivot": [0, 12, -70], "cubes": f})

    # ===== CAB (hollow, see-through glass) =====
    c = []
    c.append(box(-19, 16, -104, 19, 18, -64, INTERIOR))                  # floor (between wheel arches)
    c += both(box(19, 20, -104, 25, 21, -64, INTERIOR))                  # floor over the arches
    c.append(box(-25, 18, -66, 25, 47, -64, ARMOR))                      # back wall
    c.append(box(-26, 47, -106, 26, 49, -63, ARMOR))                     # roof with visor overhang
    c.append(box(-22, 49, -96, 22, 50, -68, ARMOR2))                     # roof armour cap
    c.append(box(-6, 50, -84, 6, 51, -74, STEEL))                        # roof hatch
    c.append(box(-25, 18, -105, 25, 32, -102, ARMOR))                    # nose
    c.append(box(-14, 20, -106, 14, 30, -105, GRILLE))                   # grille
    c += both(box(16, 23, -106, 23, 28, -105, LAMP_W), box(16, 21, -106, 23, 23, -105, LAMP_A))
    c += both(box(15, 18, -106, 25, 20, -104, MUD))                      # chin armour
    c.append(rod((0, 32, -103), (0, 46, -99), 46, 0.5, GLASS))           # raked windscreen
    for x in (-24, 0, 24):
        c.append(rod((x, 32, -103.6), (x, 46.2, -99.6), 3 if x else 2, 2, STEEL))  # A-pillars + centre post
    c.append(box(-25, 31, -104, 25, 32.5, -101, STEEL))                  # windscreen sill
    c.append(rod((0, 44, -100.4), (0, 46.6, -99.6), 50, 2.6, ARMOR))     # header
    c += both(box(26, 41, -101, 32, 42, -99, ARMOR2))                    # visor wing tips / lights row
    for x in (-15, -5, 5, 15):
        c.append(box(x - 2, 47.5, -107, x + 2, 49, -106, LAMP_A))        # roof light bar
    c.append(box(-1.5, 50, -66, 1.5, 53, -63, LAMP_A))                   # beacon
    # side walls: door panel, window, B-pillar, rear panel
    c += both(box(23, 21, -102, 25, 32, -66, ARMOR),
              box(23, 32, -101, 25, 34, -66, ARMOR),
              box(24, 34, -99, 24.5, 45, -81, GLASS),
              box(23, 45, -102, 25, 47, -66, ARMOR),
              box(23, 34, -81, 25, 45, -77, STEEL),
              box(23, 34, -77, 25, 45, -66, ARMOR2),
              box(23, 34, -102, 25, 45, -99, STEEL),
              box(25, 22, -100, 26.5, 31, -80, ARMOR2),                  # bolt-on applique armour
              box(25, 27, -79, 26.5, 31, -67, ARMOR2),
              box(25.5, 28, -84, 27, 29, -81, CHROME),                   # door handle
              box(25, 32, -76, 26, 44, -75, CHROME),                     # grab rail
              box(23, 8, -84, 27, 9, -79, STEEL), box(23, 12, -84, 27, 13, -79, STEEL),  # boarding steps
              box(26, 8, -84, 27, 16, -83, STEEL),
              rod((25, 40, -100), (32, 42, -103), 1, 1, STEEL),          # mirror arm
              box(31, 35, -104, 33, 44, -102, RUBBER),
              box(31.5, 36, -104.3, 32.5, 43, -104, CHROME))
    # snorkel intake on right A-pillar
    c.append(box(-29, 22, -96, -26, 52, -93, CYL))
    c.append(box(-30, 52, -97, -25, 56, -92, STEEL))
    # interior: dash, seats, steering wheel (driver at model x=-10)
    c.append(box(-22, 18, -101, 22, 28, -96, INTERIOR))
    c.append(box(-20, 28, -100, 20, 29, -97, RUBBER))
    for x in (-10, 10):
        c.append(box(x - 5, 18, -76, x + 5, 21, -68, SEAT))
        c.append(box(x - 5, 21, -69, x + 5, 34, -67, SEAT))
        c.append(box(x - 3, 34, -68.5, x + 3, 38, -67.5, SEAT))
    c.append(rod((-10, 24, -96), (-10, 31, -88), 1.4, 1.4, STEEL))       # steering column
    c.append(rod((-10, 28, -91.2), (-10, 34, -87.2), 8, 1, RUBBER))      # steering wheel
    c.append(box(-3, 18, -86, 3, 24, -76, INTERIOR))                     # gear console
    bones.append({"name": "cab", "parent": "body", "pivot": [0, 18, -84], "cubes": c})

    # ===== POWER PACK + EXHAUST STACKS (behind cab) =====
    e = [box(-18, 18, -63, 18, 40, -56, ARMOR2), box(-16, 40, -62, 16, 42, -57, GRILLE)]
    e += both(box(21, 18, -62, 25, 52, -58, CHROME),                     # stacks
              box(20.5, 26, -63, 25.5, 44, -62.5, SHIELD),
              box(25, 26, -62, 25.5, 44, -58, SHIELD),
              rod((23, 52, -60), (23, 53.5, -62.5), 4, 4, RUBBER),       # rain flapper
              box(18, 36, -61, 21, 38, -59, STEEL))
    e.append(box(-12, 30, -56, 12, 40, -55, STEEL))                      # air/hydraulic lines panel
    for x in (-8, -3, 2, 7):
        e.append(box(x, 22, -55.5, x + 1.5, 40, -54.5, CHAIN if x % 2 else YELLOW))
    bones.append({"name": "exhaust", "parent": "body", "pivot": [0, 18, -60], "cubes": e})

    # ===== TRAILER: gooseneck + main beams =====
    t = []
    t.append(box(-17, 28, -60, 17, 34, -24, ARMOR))                      # gooseneck upper deck
    t.append(box(-17, 34, -60, 17, 35, -24, DECK))
    t.append(box(-12, 19, -50, 12, 28, -38, STEEL))                      # kingpin box
    t.append(box(-18, 26, -61, 18, 36, -59, HAZ))                        # gooseneck front face
    t += both(box(17, 26, -60, 18, 35, -24, ARMOR2))                     # neck side skirts
    t += both(rod((14, 28, -24), (14, 16, -12), 6, 6, STEEL))           # swan-neck drop beams
    t.append(rod((0, 30, -24), (0, 20, -12), 28, 2, ARMOR))              # drop plate
    t += both(box(13, 14, -14, 18, 18, 90, STEEL))                       # main beams
    for z in range(-10, 90, 12):
        t.append(box(-13, 15, z, 13, 17, z + 2, STEEL))
    t += both(box(9, 35, -58, 15, 39, -46, CYL))                         # toolboxes on neck
    t += both(box(15, 35, -44, 17, 41, -28, STEEL))                      # neck guard rails
    t += both(box(19, 26, -52, 22, 33, -49, LAMP_A))
    for z in TRAILER_AXLES:                                              # pendulum axle swing arms + struts
        t += both(box(14, 7, z - 2, 18, 15, z + 2, STEEL), rod((16, 7, z + 2), (16, 14, z + 5), 1.6, 1.6, CHROME))
    bones.append({"name": "trailer_chassis", "parent": "body", "pivot": [0, 16, -42], "cubes": t})

    # ===== LOWBOY DECK (tilt_bed) =====
    d = [box(-28, 18, -16, 28, 22, 90, DECK)]
    d += both(box(28, 17, -16, 29.5, 22.5, 90, HAZ))                     # hazard edge rails
    d.append(box(-29.5, 17, 90, 29.5, 22.5, 92, HAZ))
    d.append(box(-29.5, 12, 91, 29.5, 17, 93, STEEL))                    # rear bumper
    d += both(box(20, 13, 92, 27, 16, 93.5, LAMP_R), box(12, 13, 92, 18, 16, 93.5, LAMP_A))
    for z in range(-10, 90, 14):
        d += both(box(29.3, 18.5, z, 30, 20.5, z + 2, LAMP_A),           # side marker lights
                  box(25, 22, z + 5, 27, 23, z + 8, CHAIN))              # D-ring tie-downs
    d += both(box(8, 22, 86, 22, 48, 89, DECK), box(8, 22, 89, 22, 48, 90, HAZ),   # flip-up loading ramps
              rod((15, 22, 76), (15, 40, 86.5), 2, 2, CHROME), box(13.5, 22, 74, 16.5, 24, 78, CYL))
    d.append(box(-8, 22, 86, 8, 26, 90, STEEL))
    bones.append({"name": "tilt_bed", "parent": "trailer_chassis", "pivot": [0, 18, 80], "cubes": d})

    # ===== OUTRIGGERS (stowed stabiliser jacks) =====
    o = []
    for z in (-14, 84):
        o += both(box(29, 14, z, 36, 18, z + 4, YELLOW), box(32.5, 4, z + 0.5, 35.5, 14, z + 3.5, CYL),
                  box(31.5, 2.5, z - 0.5, 36.5, 4, z + 4.5, STEEL), box(29, 18, z, 36, 18.5, z + 4, HAZ))
    bones.append({"name": "outriggers", "parent": "tilt_bed", "pivot": [0, 16, 35], "cubes": o})

    # ===== HYDRAULIC MECH CRADLE / BACKREST =====
    k = []
    k += both(box(14, 22, -15, 20, 62, -9, ARMOR),                       # A-frame towers
              box(13, 22, -16, 21, 26, -8, STEEL),                       # hinge blocks
              box(20, 30, -14, 21, 58, -10, HAZ),
              rod((17, 22, 6), (17, 44, -9), 4, 4, CYL),                 # main lift rams (barrel)
              rod((17, 33, -1.5), (17, 52, -12), 2.4, 2.4, CHROME),      # ram rods
              box(15, 22, 3, 19, 25, 9, STEEL),                          # ram clevis on deck
              box(14, 56, -9, 20, 60, 6, ARMOR2),                        # shoulder clamp arms
              box(13, 52, 4, 21, 60, 7, YELLOW),
              box(19.5, 61, -13, 20.5, 64, -11, LAMP_A))
    k.append(box(-14, 24, -14, 14, 60, -12, ARMOR2))                     # backrest plate
    for y in (30, 40, 50):
        k.append(box(-14, y, -12, 14, y + 3, -10, STEEL))                # backrest ribs / pads
    k.append(box(-20, 60, -15, 20, 64, -9, ARMOR))                       # top crossbeam
    k.append(box(-6, 64, -14, 6, 66, -10, STEEL))
    bones.append({"name": "cradle", "parent": "tilt_bed", "pivot": [0, 22, -12], "cubes": k})

    # ===== CARGO STRAPS (hidden when empty) =====
    s = []
    for z in (6, 38):
        s += both(rod((26, 22.5, z), (13, 40, z), 2.4, 0.6, STRAP),      # ratchet strap up to the hull
                  box(19, 29, z - 1.5, 22.5, 32, z + 1.5, CHROME),       # ratchet buckle
                  box(11, 38, z - 3, 15, 43, z + 3, YELLOW))             # clamp shoe
    for z in (22, 52):
        s += both(rod((26, 22.5, z), (16, 30, z - 6), 1.2, 1.2, CHAIN))  # binder chains
    s += both(box(8, 22, 24, 16, 26, 28, YELLOW), box(8, 22, 40, 16, 26, 44, YELLOW),  # foot locks
              box(9, 26, 24, 15, 27, 44, STEEL))
    s.append(box(-24, 22, 66, 24, 25, 70, YELLOW))                       # wheel-chock beam
    bones.append({"name": "cargo_straps", "parent": "tilt_bed", "pivot": [0, 22, 25], "cubes": s})

    # ===== WHEELS =====
    for side, x in (("l", 1), ("r", -1)):
        bones.append(wheel_bone(f"wheel_f_{side}", 24 * x, R_TRACTOR, -88, R_TRACTOR, False, RIM_L))
        bones.append(wheel_bone(f"wheel_d1_{side}", 23.5 * x, R_TRACTOR, -52, R_TRACTOR, True, RIM_L))
        bones.append(wheel_bone(f"wheel_d2_{side}", 23.5 * x, R_TRACTOR, -38, R_TRACTOR, True, RIM_L))
        for i, z in enumerate(TRAILER_AXLES, 1):
            bones.append(wheel_bone(f"wheel_t{i}_{side}", 23.5 * x, R_TRAILER, z, R_TRAILER, True, RIM))
    return bones


def write_geo(bones):
    data = {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": "geometry.mobile_suit_trailer", "texture_width": 512, "texture_height": 512,
                        "visible_bounds_width": 15, "visible_bounds_height": 6, "visible_bounds_offset": [0, 2.5, 0]},
        "bones": per_face_uv(bones)}]}
    with open(GEO, "w") as f:
        json.dump(data, f, indent=1)
    return data


def write_anim(bones):
    wheels = [b["name"] for b in bones if b["name"].startswith("wheel_")]
    # 3.5 s loop: tractor (r9) turns 7x, trailer (r7) turns 9x -> same ground speed, seamless loop
    drive = {w: {"rotation": {"0.0": [0, 0, 0], "3.5": [-2520 if w[6] in "fd" else -3240, 0, 0]}} for w in wheels}
    drive["body"] = {"position": {f"{t * 0.25:.2f}": [0, -0.2 * (t % 2), 0] for t in range(15)}}  # road shimmy
    anim = {"format_version": "1.8.0", "animations": {
        "animation.mobile_suit_trailer.idle": {"loop": True, "animation_length": 3.0, "bones": {
            "body": {"position": {"0.0": [0, 0, 0], "1.5": [0, -0.15, 0], "3.0": [0, 0, 0]}},
            "cradle": {"rotation": {"0.0": [0, 0, 0], "1.5": [0.4, 0, 0], "3.0": [0, 0, 0]}}}},
        "animation.mobile_suit_trailer.drive": {"loop": True, "animation_length": 3.5, "bones": drive}}}
    with open(ANIM, "w") as f:
        json.dump(anim, f, indent=1)
    return anim


# ---------------------------------------------------------------- texture
def noise(x, y, s=0):
    return ((x * 73856093 ^ y * 19349663 ^ s * 83492791) & 0xff) / 255.0 - 0.5


def paint(td):
    px = td.set_pixel

    def armor(x0, y0, base, seam, mud=False):
        for y in range(y0, y0 + 64):
            for x in range(x0, x0 + 64):
                lx, ly = x - x0, y - y0
                n = noise(x, y) * 10 + math.sin(x * 0.3 + y * 0.05) * 2
                streak = -14 if (noise(x, 0, 7) > 0.35 and noise(x, y // 6, 3) > -0.2) else 0  # grime runs
                v = [base[i] + n + streak for i in range(3)]
                if mud and ly > 40 + noise(x, 1) * 10:
                    v = [v[0] * 0.65 + 30, v[1] * 0.6 + 22, v[2] * 0.5 + 10]
                if lx % seam == 0 or ly % seam == 0:
                    v = [c - 45 for c in v]
                elif lx % seam == 1 or ly % seam == 1:
                    v = [c + 18 for c in v]
                if lx % seam in (3, seam - 3) and ly % 6 == 3:
                    v = [c + 35 for c in v]                               # bolt head
                if noise(x, y, 9) > 0.47:
                    v = [c + 30 for c in v]                               # chipped paint
                px(x, y, *v)

    armor(*ARMOR, (178, 176, 160), 16)
    armor(*ARMOR2, (166, 166, 150), 32)
    armor(*MUD, (172, 170, 154), 16, mud=True)
    td.draw_text(ARMOR2[0] + 6, ARMOR2[1] + 6, "74", (60, 60, 56), 2)
    td.draw_glass(*GLASS, 64, 64)
    for y in range(64):                                                   # grille: slats + mesh
        for x in range(64):
            px(GRILLE[0] + x, y, *([150] * 3 if y % 3 == 0 else [40 + (x % 2) * 10] * 3))
    for y in range(STEEL[1], STEEL[1] + 64):
        for x in range(STEEL[0], STEEL[0] + 64):
            v = 112 + noise(x, y) * 14 + (-20 if (x - STEEL[0]) % 32 == 0 else 0)
            v += 30 if (x - STEEL[0]) % 8 == 4 and (y - STEEL[1]) % 8 == 4 else 0
            px(x, y, v, v, v - 4)
    for y in range(64):                                                   # light diamond plate
        for x in range(DECK[0], DECK[0] + 64):
            v = 150 + noise(x, y) * 12 - (8 if noise(x // 8, y // 8, 2) > 0.3 else 0)
            dx, dy = x % 6, y % 6
            if (dx, dy) in ((1, 1), (2, 2), (4, 4)):
                v += 40
            elif (dx, dy) in ((2, 1), (3, 2), (5, 4)):
                v -= 40
            if (x - DECK[0]) % 32 == 0 or y % 32 == 0:
                v -= 40
            px(x, y, v, v, v - 3)
    for y in range(64):                                                   # hazard chevrons
        for x in range(HAZ[0], HAZ[0] + 64):
            wear = noise(x, y, 4) > 0.42
            if ((x + y) // 6) % 2 == 0 and not wear:
                px(x, y, 236 + noise(x, y) * 10, 196, 40)
            else:
                px(x, y, 36, 36, 34)
    for y in range(64):                                                   # orange woven strap
        for x in range(STRAP[0], STRAP[0] + 64):
            v = 1 + (0.12 if (x + y) % 4 < 2 else -0.08)
            px(x, y, 236 * v, 110 * v, 20 * v)
    for y in range(64, 128):                                              # tyre tread: chevron lugs
        for x in range(64):
            lug = ((y + abs((x % 16) - 8)) // 4) % 2 == 0
            v = 52 if lug else 24
            px(x, y, v + noise(x, y) * 6, v, v + 2)
    for (u, v0, d) in ((RIM[0], 64, 10), (RIM_L[0], 64, 14)):            # rims at the face corner
        cx = cy = (d - 1) / 2
        for y in range(d):
            for x in range(d):
                r = math.hypot(x - cx, y - cy)
                c = 30 if r > d / 2 - 0.3 else (150 if r < 1.6 else (118 if r < d / 2 - 1.6 else 80))
                if 2.4 < r < 3.4 and (x + y) % 2 == 0:
                    c = 215                                               # lug nuts
                px(u + x, v0 + y, c, c, c - 6)
    for y in range(64, 128):                                              # chrome rods
        for x in range(CHROME[0], CHROME[0] + 64):
            v = 170 + 60 * math.sin((x % 8) / 8 * math.pi)
            px(x, y, v, v, v + 5)
    for y in range(64, 128):                                              # perforated heat shield
        for x in range(SHIELD[0], SHIELD[0] + 64):
            v = 40 if (x % 4 == 1 and y % 4 == 1) else 135 + noise(x, y) * 10
            px(x, y, v, v - 4, v - 10)
    for (u, v0, col) in ((LAMP_A[0], 64, (255, 168, 30)), (LAMP_R[0], 64, (200, 30, 26)), (LAMP_W[0], 96, (255, 250, 214))):
        for y in range(v0, v0 + 32):
            for x in range(u, u + 32):
                e = (x - u) % 8 in (0,) or (y - v0) % 8 == 0
                px(x, y, *[c * (0.55 if e else 1) for c in col])
    for y in range(64, 128):
        for x in range(INTERIOR[0], INTERIOR[0] + 64):
            v = 70 + noise(x, y) * 8
            px(x, y, v, v, v - 2)
        for x in range(RUBBER[0], RUBBER[0] + 64):
            v = 32 + noise(x, y) * 6
            px(x, y, v, v, v)
        for x in range(CYL[0], CYL[0] + 64):
            v = 150 + 40 * math.sin((x % 16) / 16 * math.pi) + noise(x, y) * 8
            px(x, y, v, v - 2, v - 10)
    for y in range(128, 192):
        for x in range(SEAT[0], SEAT[0] + 64):
            v = (1 if (x // 4 + y // 4) % 2 else 0.9) + noise(x, y) * 0.05
            px(x, y, 120 * v, 112 * v, 84 * v)
        for x in range(YELLOW[0], YELLOW[0] + 64):
            w = noise(x, y, 5) > 0.4
            px(x, y, *((90, 88, 80) if w else (232 + noise(x, y) * 10, 188, 46)))
            if (x - YELLOW[0]) % 16 == 0 or (y - 128) % 16 == 0:
                px(x, y, 120, 96, 30)
        for x in range(CHAIN[0], CHAIN[0] + 64):
            link = (y // 3) % 2 == 0 and (x % 3) != 0
            v = 160 if link else 60
            px(x, y, v, v, v)


def write_icon():
    """16x16 side view: cab on the right, gooseneck, low deck, cradle and a row of wheels."""
    G, D, K, W, Y, B, A = (178, 176, 160), (110, 110, 104), (30, 30, 32), (160, 210, 230), (236, 196, 40), (60, 60, 58), (255, 168, 30)
    rows = [
        "................",
        "................",
        "..GG............",
        "..GG.......GGGG.",
        "..GG.......GWWG.",
        "..GG.......GWWGG",
        "..GG...DDDDGGGGG",
        "..GG...DDDDGGGGA",
        "YYYYYYYDDDDGGGGG",
        "DDDDDDDDDBBBBBBB",
        "BKKBKKBKKB.KK.KK",
        "KKKKKKKKK.KKKKKK",
        "KBKKBKKBK.KBKKBK",
        ".KK.KK.KK..KK.KK",
        "................",
        "................"]
    pal = {"G": G, "D": D, "K": K, "W": W, "Y": Y, "B": B, "A": A}
    buf = bytearray()
    for row in rows:
        for ch in row:
            buf += bytes(pal[ch] + (255,)) if ch in pal else bytes(4)
    with open(ICON, "wb") as f:
        f.write(make_png(16, 16, buf))


# ---------------------------------------------------------------- validation + preview
def validate(geo, anim):
    g = geo["minecraft:geometry"][0]
    names = {b["name"] for b in g["bones"]}
    n = 0
    for b in g["bones"]:
        assert b.get("parent") in names | {None}, b["name"]
        for c in b.get("cubes", []):
            n += 1
            assert all(s > 0 for s in c["size"]), (b["name"], c)
            for fuv in c["uv"].values():
                (u, v), (w, h) = fuv["uv"], fuv["uv_size"]
                assert 0 <= u and u + w <= 512 and 0 <= v and v + h <= 512, (b["name"], c)
    for a in anim["animations"].values():
        for bn in a["bones"]:
            assert bn in names, bn
    assert "cargo_straps" in names and "body" in names
    return n


def mat(rx, ry, rz):
    def X(a):
        c, s = math.cos(a), math.sin(a); return [[1, 0, 0], [0, c, -s], [0, s, c]]
    def Y(a):
        c, s = math.cos(a), math.sin(a); return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    def Z(a):
        c, s = math.cos(a), math.sin(a); return [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    mm = lambda A, B: [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return mm(Z(math.radians(-rz)), mm(Y(math.radians(-ry)), X(math.radians(-rx))))


def preview(geo, tex, path, yaw, pitch=30, scale=3.2, W=900, H=520):
    tw = 512
    zb = [1e9] * (W * H)
    img = bytearray([200, 206, 212] * (W * H))
    cy_, sy_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def view(p):
        x, y, z = p
        x, z = x * cy_ + z * sy_, -x * sy_ + z * cy_
        y, z = y * cp + z * sp, -y * sp + z * cp
        return x, y, z
    light = [0.4, 0.85, -0.3]
    for b in geo["minecraft:geometry"][0]["bones"]:
        for c in b.get("cubes", []):
            o, s = c["origin"], c["size"]
            R = mat(*c["rotation"]) if "rotation" in c else None
            pv = c.get("pivot", [0, 0, 0])

            def T(p):
                if R is None:
                    return p
                q = [p[i] - pv[i] for i in range(3)]
                return [sum(R[i][k] * q[k] for k in range(3)) + pv[i] for i in range(3)]
            x0, y0, z0 = o; x1, y1, z1 = o[0] + s[0], o[1] + s[1], o[2] + s[2]
            faces = {  # origin corner, u-axis vec, v-axis vec (v goes down), normal
                "north": ((x1, y1, z0), (-s[0], 0, 0), (0, -s[1], 0), (0, 0, -1)),
                "south": ((x0, y1, z1), (s[0], 0, 0), (0, -s[1], 0), (0, 0, 1)),
                "east": ((x1, y1, z1), (0, 0, -s[2]), (0, -s[1], 0), (1, 0, 0)),
                "west": ((x0, y1, z0), (0, 0, s[2]), (0, -s[1], 0), (-1, 0, 0)),
                "up": ((x0, y1, z0), (s[0], 0, 0), (0, 0, s[2]), (0, 1, 0)),
                "down": ((x0, y0, z1), (s[0], 0, 0), (0, 0, -s[2]), (0, -1, 0))}
            for fname, (p0, ua, va, nrm) in faces.items():
                n = T([nrm[i] + pv[i] for i in range(3)]) if R else nrm
                if R:
                    n = [n[i] - pv[i] for i in range(3)]
                if view(n)[2] > 0.001:
                    continue
                sh = 0.55 + 0.45 * max(0, sum(n[i] * light[i] for i in range(3)))
                (u, v), (uw, vh) = c["uv"][fname]["uv"], c["uv"][fname]["uv_size"]
                lu = math.sqrt(sum(a * a for a in ua)); lv = math.sqrt(sum(a * a for a in va))
                nu, nv = max(1, int(lu * scale * 1.3)), max(1, int(lv * scale * 1.3))
                for j in range(nv):
                    fv = (j + 0.5) / nv
                    for i in range(nu):
                        fu = (i + 0.5) / nu
                        tx, ty = int(u + fu * uw), int(v + fv * vh)
                        k = (ty * tw + tx) * 4
                        if tex[k + 3] == 0:
                            continue
                        p = T([p0[a] + ua[a] * fu + va[a] * fv for a in range(3)])
                        vx, vy, vz = view(p)
                        sx, sy = int(W / 2 + vx * scale), int(H * 0.62 - vy * scale)
                        for ox in (0, 1):
                            for oy in (0, 1):
                                X_, Y_ = sx + ox, sy + oy
                                if 0 <= X_ < W and 0 <= Y_ < H and vz < zb[Y_ * W + X_]:
                                    zb[Y_ * W + X_] = vz
                                    img[(Y_ * W + X_) * 3:(Y_ * W + X_) * 3 + 3] = bytes(min(255, int(tex[k + q] * sh)) for q in range(3))
    rgba = bytearray()
    for i in range(W * H):
        rgba += img[i * 3:i * 3 + 3] + b"\xff"
    with open(path, "wb") as f:
        f.write(make_png(W, H, rgba))


def main():
    td = TextureDrawer(512, 512)
    paint(td)
    td.save(TEX)
    bones = build_bones()
    geo = write_geo(bones)
    anim = write_anim(bones)
    write_icon()
    n = validate(geo, anim)
    print(f"cubes={n} bones={len(geo['minecraft:geometry'][0]['bones'])}")
    if "--preview" in sys.argv:
        out = sys.argv[sys.argv.index("--preview") + 1]
        for name, yaw in (("rear", 215), ("front", 35), ("side", 270)):
            preview(geo, td.buf, os.path.join(out, f"msu_trailer_{name}.png"), yaw)


if __name__ == "__main__":
    main()
