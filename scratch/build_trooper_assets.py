"""MP-01 Trooper Titan: builds geo/trooper_titan.geo.json and the base + 8 camo textures.

Run from the repo root:  python3 scratch/build_trooper_assets.py
Bone names and pivots match the old rig (animations, TitanModel IK and seat offsets rely on them).
Front of the titan is -Z, its right side is -X. Left-side parts are mirrored from the right.
"""
import json, os, random, struct, zlib

ROOT = "Titan Combat/src/main/resources/assets/titancombat"
TEX = 1024
ID = "trooper"  # build_scout_assets.py reuses this module with its own ID, BONES and SCHEMES
CAMO = False    # plain worn olive like the MP-01 reference; digital camo stays available for other builders

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

SGN = 1  # tools run along +x from the grip in the weapon bone's raw frame (Ion's barrel axis)

def ycube(cx, cz, y0, length, w, d, m, rot=None):
    """Cube spanning `length` along x from x0=y0 in the SGN direction, centred on the grip axis.
    (cx is the grip x, cz the grip z; w is the height, d the depth of the cross-section.)"""
    x = y0 if SGN > 0 else y0 - length
    c = C([x, GRIP_Y - w / 2, cz - d / 2], [length, w, d], m)
    if rot is not None:
        c["rot"], c["piv"] = [rot, 0, 0], [x + length / 2, GRIP_Y, cz]
    return c

GRIP_Y = 39.8

def drill(cx, cz, y0):
    """Spiral drill bit: motor collar at the grip, then stacked rings, each turned a bit more."""
    out = [ycube(cx, cz, y0 + 3 * -SGN, 6, 14, 14, "metal"),
           ycube(cx, cz, y0 + 3 * SGN, 2, 16, 16, "rust"),
           ycube(cx, cz, y0 + 5 * SGN, 2, 12, 12, "dark")]
    y, size = y0 + 7 * SGN, 13
    for i in range(11):
        out.append(ycube(cx, cz, y, 3, size, size, "steel", rot=(i * 22.5) % 90))
        y += 3 * SGN
        size = max(2, size - 1)
    out.append(ycube(cx, cz, y, 4, 2, 2, "steel", rot=45))
    return out

def chainsaw(cx, cz, y0):
    """Chainsaw: motor block at the grip, upright guide bar with a toothed chain on both edges."""
    out = [ycube(cx, cz, y0 - 4, 10, 14, 12, "paint"),
           ycube(cx, cz - 6.5, y0 - 2, 6, 6, 1, "vent"),
           ycube(cx, cz, y0 + 6, 2, 12, 6, "hazard"),
           ycube(cx, cz, y0 + 8, 28, 10, 2, "steel"),
           ycube(cx, cz, y0 + 8, 30, 12, 1, "dark")]
    for k in range(7):
        x = y0 + 10 + k * 4
        for dy in (-7, 5):
            out.append(C([x, GRIP_Y + dy, cz - 1], [2, 2, 2], "rust"))
    return out

def rifle(cx, cz, y0):
    """Titan Heavy Assault Rifle: Bullpup-inspired tactical rifle with holo-sight,
    vented shroud, muzzle brake, angled foregrip and combat magazine."""
    out = []
    # 1. Receiver Core & Bevel
    out.append(C([y0 - 8, GRIP_Y - 3, cz - 3], [24, 9, 6], "paint2"))
    out.append(C([y0 - 6, GRIP_Y + 6, cz - 2.5], [20, 2, 5], "dark"))
    out.append(C([y0 + 2, GRIP_Y + 1, cz + 2.8], [6, 3, 0.8], "dark")) # ejection port
    # 2. Stock & Recoil Buttpad
    out.append(C([y0 - 18, GRIP_Y - 4, cz - 2.5], [10, 8, 5], "dark"))
    out.append(C([y0 - 20, GRIP_Y - 5, cz - 3], [2, 10, 6], "metal"))
    # 3. Grip & Trigger Guard
    out.append(C([y0 - 3, GRIP_Y - 10, cz - 1.5], [4, 7, 3], "dark"))
    out.append(C([y0 + 1, GRIP_Y - 8, cz - 1], [1, 5, 2], "metal"))
    # 4. Top Picatinny Rail & Holo-Sight
    out.append(C([y0 - 6, GRIP_Y + 8, cz - 1.5], [28, 1.5, 3], "metal"))
    out.append(C([y0 + 2, GRIP_Y + 9.5, cz - 2], [8, 4.5, 4], "dark"))
    out.append(C([y0 + 4, GRIP_Y + 11, cz - 1.5], [4, 2.5, 3], "visor")) # holographic lens
    # 5. Handguard & Cooling Vents
    out.append(C([y0 + 16, GRIP_Y - 2, cz - 2.5], [20, 7, 5], "paint"))
    out.append(C([y0 + 18, GRIP_Y, cz - 3.2], [16, 3, 0.8], "vent"))
    out.append(C([y0 + 18, GRIP_Y, cz + 2.4], [16, 3, 0.8], "vent"))
    out.append(C([y0 + 22, GRIP_Y - 7, cz - 1.5], [6, 5, 3], "dark")) # foregrip
    # 6. Barrel & Muzzle Brake
    out.append(C([y0 + 36, GRIP_Y - 1, cz - 1.5], [5, 4, 3], "steel"))
    out.append(C([y0 + 41, GRIP_Y - 2, cz - 2.5], [5, 6, 5], "metal"))
    out.append(C([y0 + 42, GRIP_Y + 4, cz - 1], [3, 1, 2], "dark"))
    # 7. Combat Magazine
    out.append(C([y0 + 6, GRIP_Y - 14, cz - 2], [6, 11, 4], "steel"))
    out.append(C([y0 + 5, GRIP_Y - 15, cz - 2], [7, 2, 4], "hazard"))
    return late(out)

def machine_gun(cx, cz, y0):
    """Titan Heavy Rotary Machine Gun: 6-barrel minigun with motor stator,
    side-mounted high-capacity drum magazine with caution stripes, ammo chute and spade grips."""
    import math
    out = []
    # 1. Motor Stator & Receiver
    out.append(C([y0 - 8, GRIP_Y - 6, cz - 6], [16, 12, 12], "dark"))
    out.append(C([y0 - 6, GRIP_Y - 7, cz - 5.5], [12, 14, 11], "paint2"))
    out.append(C([y0 - 4, GRIP_Y + 7, cz - 4], [8, 2, 8], "vent"))
    # 2. Rear Spade Mount & Grips
    out.append(C([y0 - 14, GRIP_Y - 4, cz - 4], [6, 8, 8], "metal"))
    out.append(C([y0 - 18, GRIP_Y - 6, cz - 5], [4, 12, 2], "dark"))
    out.append(C([y0 - 18, GRIP_Y - 6, cz + 3], [4, 12, 2], "dark"))
    # 3. Side Drum Magazine with Hazard Stripes
    out.append(C([y0 - 4, GRIP_Y - 12, cz - 16], [12, 14, 10], "metal"))
    out.append(C([y0 - 2, GRIP_Y - 10, cz - 17], [8, 10, 12], "hazard"))
    out.append(C([y0 + 2, GRIP_Y - 4, cz - 9], [4, 5, 4], "steel")) # ammo chute
    # 4. Drive Shaft & 6 Rotary Barrels
    out.append(C([y0 + 8, GRIP_Y - 2, cz - 2], [36, 4, 4], "dark"))
    for ang in [0, 60, 120, 180, 240, 300]:
        rad = math.radians(ang)
        by = GRIP_Y + math.sin(rad) * 4.2 - 1.0
        bz = cz + math.cos(rad) * 4.2 - 1.0
        out.append(C([y0 + 8, by, bz], [36, 2.2, 2.2], "steel"))
    # 5. Barrel Stabilizer & Muzzle Clamp
    out.append(C([y0 + 23, GRIP_Y - 5.5, cz - 5.5], [3, 11, 11], "paint2"))
    out.append(C([y0 + 41, GRIP_Y - 6, cz - 6], [5, 12, 12], "metal"))
    out.append(C([y0 + 42, GRIP_Y - 5, cz - 5], [4, 10, 10], "dark"))
    out.append(C([y0 + 4, GRIP_Y + 8, cz - 1.5], [10, 3, 3], "metal"))
    return late(out)

def rocket_launcher(cx, cz, y0):
    """Titan Rocket Launcher: 6-tube heavy box launcher pod with exposed warheads."""
    out = []
    # 1. Main Pod Body
    out.append(C([y0 - 6, GRIP_Y - 5, cz - 7], [32, 14, 14], "paint"))
    out.append(C([y0 - 4, GRIP_Y - 6, cz - 8], [28, 16, 1], "paint2"))
    out.append(C([y0 - 4, GRIP_Y - 6, cz + 7], [28, 16, 1], "paint2"))
    out.append(C([y0 - 4, GRIP_Y + 9, cz - 7.5], [28, 1, 15], "paint2"))
    out.append(C([y0 + 2, GRIP_Y + 9.5, cz - 6], [16, 1.5, 12], "hazard"))
    # 2. Six Rocket Tubes & Warheads
    out.append(C([y0 + 26, GRIP_Y - 4.5, cz - 6.5], [1, 13, 13], "dark"))
    for row in range(2):
        ty = GRIP_Y - 2.5 + row * 6.5
        for col in range(3):
            tz = cz - 4.5 + col * 4.5
            out.append(C([y0 + 26.5, ty - 1.8, tz - 1.8], [1.5, 3.6, 3.6], "metal"))
            out.append(C([y0 + 27.5, ty - 1.2, tz - 1.2], [2.5, 2.4, 2.4], "amber"))
            out.append(C([y0 + 29.5, ty - 0.6, tz - 0.6], [1.5, 1.2, 1.2], "glow"))
    # 3. Exhaust Ports & Grip
    out.append(C([y0 - 9, GRIP_Y - 4, cz - 6], [3, 12, 12], "dark"))
    out.append(C([y0 - 10, GRIP_Y - 2, cz - 4], [1, 8, 8], "vent"))
    out.append(C([y0 + 4, GRIP_Y - 11, cz - 1.5], [4, 6, 3], "dark"))
    out.append(C([y0 - 4, GRIP_Y - 10, cz - 2], [6, 5, 4], "metal"))
    return late(out)

def arc_cannon(cx, cz, y0):
    """Arc Cannon: capacitor bank behind a long emitter barrel wrapped in glowing coils, forked prongs at the muzzle."""
    out = [C([y0 - 10, GRIP_Y - 6, cz - 6], [20, 12, 12], "paint"),            # capacitor housing
           C([y0 - 8, GRIP_Y + 6, cz - 4], [14, 3, 8], "vent"),
           C([y0 - 12, GRIP_Y - 4, cz - 4], [2, 8, 8], "dark"),
           C([y0 + 10, GRIP_Y - 3, cz - 3], [30, 6, 6], "metal")]             # emitter barrel
    for k in range(5):                                                       # charge coils
        out.append(C([y0 + 13 + k * 5, GRIP_Y - 4.5, cz - 4.5], [2, 9, 9], "visor"))
    out += [C([y0 + 40, GRIP_Y + 1, cz - 1], [8, 2, 2], "steel"), C([y0 + 40, GRIP_Y - 3, cz - 1], [8, 2, 2], "steel"),  # prongs
            C([y0 + 2, GRIP_Y - 12, cz - 2], [5, 7, 4], "dark"),                # grip
            C([y0 - 6, GRIP_Y - 7, cz - 6.5], [12, 1, 13], "hazard")]
    return late(out)

def scatter_cannon(cx, cz, y0):
    """Heavy Scatter Cannon: break-action slug shotgun with a wide double muzzle and drum shell feed."""
    out = [C([y0 - 10, GRIP_Y - 5, cz - 5], [22, 10, 10], "paint"),            # receiver
           C([y0 + 12, GRIP_Y - 3, cz - 4.5], [24, 6, 4], "metal"),            # twin barrels
           C([y0 + 12, GRIP_Y - 3, cz + 0.5], [24, 6, 4], "metal"),
           C([y0 + 34, GRIP_Y - 4, cz - 5.5], [4, 8, 11], "dark"),             # muzzle block
           C([y0 + 34.5, GRIP_Y - 2.5, cz - 4.5], [4, 5, 3.5], "vent"),
           C([y0 + 34.5, GRIP_Y - 2.5, cz + 1], [4, 5, 3.5], "vent"),
           C([y0 - 2, GRIP_Y - 13, cz - 5], [10, 9, 10], "dark"),              # shell drum
           C([y0 - 1, GRIP_Y - 12, cz - 5.5], [8, 7, 11], "amber"),
           C([y0 - 16, GRIP_Y - 4, cz - 3], [6, 8, 6], "paint2"),             # stock
           C([y0 + 14, GRIP_Y + 3, cz - 1], [16, 2, 2], "dark")]               # top rib
    return late(out)

def inferno_flamethrower(cx, cz, y0):
    """Inferno Flamethrower: twin fuel tanks feeding a vented nozzle with a pilot-light ring."""
    out = [C([y0 - 8, GRIP_Y - 4, cz - 4], [18, 8, 8], "paint"),              # pump body
           C([y0 - 10, GRIP_Y + 4, cz - 7], [16, 6, 6], "rust"),              # fuel tanks
           C([y0 - 10, GRIP_Y + 4, cz + 1], [16, 6, 6], "rust"),
           C([y0 - 9, GRIP_Y + 4.5, cz - 7.5], [2, 5, 15], "hazard"),
           C([y0 + 10, GRIP_Y - 2.5, cz - 2.5], [22, 5, 5], "metal"),         # feed pipe
           C([y0 + 32, GRIP_Y - 4, cz - 4], [6, 8, 8], "dark"),              # nozzle
           C([y0 + 33, GRIP_Y - 4.5, cz - 4.5], [2, 9, 9], "vent"),
           C([y0 + 38, GRIP_Y - 2, cz - 2], [2, 4, 4], "glow"),               # pilot light
           C([y0 + 1, GRIP_Y - 11, cz - 2], [5, 7, 4], "dark")]                # grip
    return late(out)

def grenade_launcher(cx, cz, y0):
    """Grenade Launcher: fat revolver cylinder and short wide barrel with a ladder sight."""
    out = [C([y0 - 8, GRIP_Y - 4, cz - 4], [10, 8, 8], "paint"),              # frame
           C([y0 + 2, GRIP_Y - 8, cz - 8], [12, 16, 16], "paint2"),           # revolver cylinder
           C([y0 + 2, GRIP_Y - 9, cz - 6], [12, 18, 12], "paint2"),
           C([y0 + 14, GRIP_Y - 5, cz - 5], [18, 10, 10], "metal"),           # wide barrel
           C([y0 + 31, GRIP_Y - 6, cz - 6], [3, 12, 12], "dark"),
           C([y0 + 31.5, GRIP_Y - 4, cz - 4], [3, 8, 8], "amber"),            # loaded round
           C([y0 + 18, GRIP_Y + 5, cz - 1], [4, 5, 2], "steel"),              # ladder sight
           C([y0 - 2, GRIP_Y - 12, cz - 2], [5, 8, 4], "dark"),
           C([y0 - 16, GRIP_Y - 3, cz - 3], [8, 7, 6], "paint2")]             # stock
    return late(out)

def back_rocket_pod():
    """Back-mounted 6-tube rocket launcher pod for Slot 13."""
    out = []
    # Mounting bracket & hydraulic strut
    out.append(C([-27, 88, 15], [6, 8, 7], "dark"))
    out.append(C([-26, 90, 13], [4, 6, 2], "steel"))
    out.append(C([-28, 95, 12], [8, 4, 10], "metal"))
    # Pod body angled forward (-Z)
    out.append(C([-31, 93, 2], [14, 12, 22], "paint"))
    out.append(C([-32, 92, 4], [1, 14, 18], "paint2"))
    out.append(C([-18, 92, 4], [1, 14, 18], "paint2"))
    out.append(C([-31, 105, 3], [14, 1.5, 20], "hazard"))
    out.append(C([-29, 99, 1], [10, 4, 1], "dark"))
    # 6 Tubes & Warheads
    for row in range(2):
        ty = 94.5 + row * 5.5
        for col in range(3):
            tx = -29.5 + col * 4.5
            out.append(C([tx - 1.8, ty - 1.8, 1], [3.6, 3.6, 1.5], "dark"))
            out.append(C([tx - 1.2, ty - 1.2, -0.5], [2.4, 2.4, 1.5], "amber"))
            out.append(C([tx - 0.6, ty - 0.6, -1.8], [1.2, 1.2, 1.3], "glow"))
    # Rear exhaust
    out.append(C([-29, 94.5, 24], [10, 9, 2], "dark"))
    out.append(C([-27, 96, 25.5], [6, 6, 1], "vent"))
    for c in out:
        c["o"][1] += 24  # rides on top of the pauldron instead of inside it
    return late(out)

def stowed_rifle():
    """Stowed Heavy Assault Rifle hanging on back clamp."""
    out = [
        C([-26, 70, 24], [4, 22, 6], "paint2"),
        C([-25, 48, 25], [2, 22, 3], "steel"),
        C([-26, 92, 24.5], [4, 12, 5], "dark"),
        C([-25, 74, 29], [2, 10, 4], "hazard"),
    ]
    return late(out)

def stowed_machine_gun():
    """Stowed Heavy Rotary Machine Gun hanging on back clamp."""
    out = [
        C([-28, 68, 23], [8, 18, 8], "dark"),
        C([-34, 70, 23], [6, 14, 10], "hazard"),
        C([-27, 44, 24], [6, 24, 6], "steel"),
    ]
    return late(out)

def stowed_rocket_launcher():
    """Stowed Rocket Launcher pod hanging on back clamp."""
    out = [
        C([-30, 64, 23], [12, 26, 10], "paint"),
        C([-29, 66, 22], [10, 22, 1], "dark"),
        C([-29, 88, 22.5], [10, 1.5, 9], "hazard"),
    ]
    return late(out)

def B(x0, x1, y0, y1, z0, z1, m, **kw):
    """Cube from its min/max corners."""
    return C([x0, y0, z0], [x1 - x0, y1 - y0, z1 - z0], m, **kw)

def ball(cx, cy, cz, d, m="dark"):
    """Ball joint: a cube plus copies turned 45 degrees about x and about z read as a sphere."""
    o, s = [cx - d / 2, cy - d / 2, cz - d / 2], [d, d, d]
    return late([C(o, s, m), C(o, s, m, rot=[45, 0, 0], piv=[cx, cy, cz]), C(o, s, m, rot=[0, 0, 45], piv=[cx, cy, cz])])

def fist(x0, top, z0, m="dark"):
    """Blocky mech fist under the wrist: palm, knuckle guard, four fingers and a thumb."""
    out = [B(x0, x0 + 10, top - 7, top, z0, z0 + 11, m),
           B(x0 - 0.5, x0 + 10.5, top - 4, top, z0 - 0.5, z0 + 11.5, "metal")]
    for i in range(4):
        out.append(B(x0 + 0.3 + i * 2.45, x0 + 2.4 + i * 2.45, top - 12, top - 7, z0 + 7, z0 + 10.5, m))
    out.append(B(x0 - 1.5, x0 + 0.5, top - 10, top - 3, z0 + 1, z0 + 4.5, "metal"))
    return out

def xbrace(cx, cy, z, size, m="dark"):
    """Raised X of two crossed bars on a -z facing plate (the MP-01 knee and shin stamping)."""
    L = size * 1.25
    return late([C([cx - 1, cy - L / 2, z - 1], [2, L, 1], m, rot=[0, 0, a], piv=[cx, cy, z - 0.5]) for a in (45, -45)])

def late(cubes):
    """Packed after every other cube, so adding detail never moves existing atlas patches (the cockpit
    arms and the Scout SMG borrow those by position)."""
    for c in cubes:
        c["late"] = True
    return cubes

def hub(cx, cy, cz, length, diam, m="dark"):
    """Round joint hub on an X hinge axis: a square plus a 45-degree-turned square read as an octagonal
    drum, with a steel bolt cap on the outer (-x) end."""
    x0 = cx - length / 2
    piv = [cx, cy, cz]
    return late([C([x0, cy - diam / 2, cz - diam / 2], [length, diam, diam], m),
            C([x0, cy - diam / 2, cz - diam / 2], [length, diam, diam], m, rot=[45, 0, 0], piv=piv),
            C([x0 - 0.6, cy - diam / 4, cz - diam / 4], [0.6, diam / 2, diam / 2], "steel")])

def piston(x, top, bot, z, w=3):
    """Hydraulic ram inside one bone: clevis, sleeve over the upper 60%, chrome rod, clevis."""
    split = top - (top - bot) * 0.6
    r = w * 0.55
    return late([C([x - w / 2 - 0.5, top - 2, z - w / 2 - 0.5], [w + 1, 2, w + 1], "dark"),
            C([x - w / 2, split, z - w / 2], [w, top - 2 - split, w], "metal"),
            C([x - r / 2, bot + 2, z - r / 2], [r, split - bot - 2, r], "steel"),
            C([x - w / 2 - 0.5, bot, z - w / 2 - 0.5], [w + 1, 2, w + 1], "dark")])

def hose(x, top, bot, z, sag, segs=3):
    """Rubber hose hanging in an arc away from the body (+z by `sag` at its middle)."""
    h = (top - bot) / segs
    out = []
    for k in range(segs):
        t = (k + 0.5) / segs
        out.append(C([x - 0.6, top - (k + 1) * h, z + sag * 4 * t * (1 - t) - 0.6], [1.2, h + 0.4, 1.2], "dark"))
    return late(out)

# ---- MP-01 "Trooper" mass-production frame (references: the MP-01 hangar shot and the heavy gun-pod mech).
# Silhouette: one armoured cab for head and chest, huge box pauldrons fixed to the hull (they stay level
# whatever the arms do), a narrow mechanical waist, heavy gauntlets and X-stamped knee/shin armour.
# Raw frame: limbs hang straight down through their joint pivots (see REST below). The arm bones rest turned
# 180 degrees about y, which swaps their front/back and inner/outer faces, so arm armour is double-sided.

def pauldron():
    """Right shoulder box on the hull: MP-01 stencil and chevrons on the front and outer faces, hazard band,
    grab handle, marker light and a rear vent."""
    return [B(-44, -19, 88, 114, -10, 24, "paint", decal={"west": "mp01", "north": "mp01"}),
            B(-42, -21, 114, 116, -8, 22, "paint2"),                               # cap
            B(-44.5, -18.5, 85.5, 88, -10.5, 24.5, "hazard"),                      # hazard band under it
            B(-45, -44, 92, 110, -6, 20, "paint2"),                                # outer armour skin
            B(-40, -23, 92, 108, 24, 25, "vent"),                                  # rear cooling vent
            B(-44.6, -44, 100, 104, -9, -5, "glow"),                               # marker light
            B(-34, -32, 116, 120, 1, 3, "steel"), B(-34, -32, 116, 120, 15, 17, "steel"),
            B(-34, -32, 119, 121, 1, 17, "steel")]                                 # grab handle

RIGHT_ARM1 = (ball(-24.4, 94.8, 10.7, 10) + [                                   # shoulder ball under the pauldron
    B(-30, -18, 72, 90, 4, 17, "dark"),                                        # upper arm frame
    B(-31, -29, 74, 88, 5, 16, "paint"), B(-19, -17, 74, 88, 5, 16, "paint"),  # bicep plates, both sides
    B(-28, -20, 76, 88, 2.5, 4, "paint2"), B(-28, -20, 76, 88, 17, 18.5, "paint2"),
] + hub(-24, 74, 10.5, 14, 10) + piston(-24, 89, 76, 19.5, w=2.4))

RIGHT_ARM2 = [                                                                  # gauntlet
    B(-36, -12, 47, 69, -1, 22, "paint", decal={"west": "hazard_bottom", "east": "hazard_bottom"}),
    B(-37, -36, 52, 66, 4, 18, "paint2"), B(-12, -11, 52, 66, 4, 18, "paint2"),   # side plates
    B(-37.6, -37, 56, 62, 8, 14, "dark"), B(-11, -10.4, 56, 62, 8, 14, "dark"),   # cooling ports
    B(-34, -14, 66, 71, 0, 21, "metal"),                                       # elbow cuff
    B(-33, -15, 52, 66, -2.5, -1, "paint2"), B(-33, -15, 52, 66, 22, 23.5, "paint2"),  # front / back guards
    B(-32, -16, 44, 48, 2, 19, "dark"),                                        # wrist band
]

RIGHT_HAND = fist(-28.3, 46.8, 6) + hub(-23.3, 46.8, 11.5, 10, 5)

RIGHT_LEG3 = [                                                                  # hip
    B(-26, -21, 47, 62, -3, 15, "paint", decal={"west": "hazard_bottom"}),    # hip armour
    B(-27, -26, 50, 60, 0, 12, "paint2"),
    B(-19, -10, 52, 64, 2, 12, "dark"),
] + hub(-14.5, 57, 7, 18, 12)

RIGHT_LEG2 = [                                                                  # thigh
    B(-23, -6, 28, 48, -6, 11, "paint"),
    B(-22, -7, 31, 46, -8, -6, "paint2"),                                      # front plate
    B(-24, -23, 30, 46, -4, 9, "paint2"),                                      # outer plate
    B(-20, -9, 24, 30, -3, 9, "dark"),                                         # knee frame
    B(-23.5, -5.5, 44, 46.5, -8.5, 11.5, "hazard"),
] + piston(-14.5, 46, 30, -9.5) + hose(-21, 46, 30, 13, 2.5)

RIGHT_LEG1 = [                                                                  # knee + shin
    B(-24, -5, 18, 34, -15, -5, "paint"),                                      # big square knee armour
    B(-23, -6, 33, 35, -14, -6, "paint2"),
    B(-24, -5, 5, 21, -10, 10, "paint", decal={"north": "hazard_bottom"}),    # armoured shin
    B(-22, -7, 7, 19, -11, -10, "paint2"),                                     # shin plate
    B(-25, -24, 7, 19, -7, 7, "paint2"), B(-5, -4, 7, 19, -7, 7, "paint2"),    # shin side skins
    B(-21, -8, 7, 20, 10, 14, "dark"),                                         # calf
] + xbrace(-14.5, 26, -15, 11) + xbrace(-14.5, 13, -11, 9) + hub(-14.5, 23, 2, 17, 10) + piston(-14.5, 20, 7, 15, w=2.4)

RIGHT_FOOT = [
    B(-26, -3, 0, 4, -23, 12, "dark"),                                         # wide tread sole
    B(-25, -4, 0, 8, -24, -12, "paint"),                                       # toe cap
    B(-25.5, -3.5, 0, 2, -24.5, -22, "hazard"),
    B(-23, -6, 4, 10, -13, 4, "paint2"),                                       # instep armour
    B(-24, -5, 0, 7, 6, 13, "metal"),                                          # heel
    B(-26.5, -2.5, 0, 1.5, -18, 8, "metal"),                                   # tread rim
] + hub(-14.5, 7, -1, 14, 7)

WAIST = piston(-9.5, 82, 64, 9) + hose(-4, 80, 65, 15, 2)

ARTILLERY_ELEVATION = 35  # resting barrel elevation in degrees; TitanModel turns it to the firing solution
ARTILLERY_TRUNNION = [0, 110, 22]

# Back-mounted howitzer for the Artillery weapon, in three bones so TitanModel can aim it:
# artillery (fixed pedestal) > artilleryTurret (traverses about y) > artilleryBarrel (elevates about the
# trunnion). The barrel is modelled level along -z; its rest rotation lifts it to ARTILLERY_ELEVATION.
# All late-packed so the existing atlas keeps its layout.
def artillery_base():
    return late([C([-5, 88, 19], [10, 16, 6], "metal"),                          # pedestal
                 C([-6, 104, 17], [12, 3, 10], "dark")])                         # traverse ring

def artillery_turret():
    return late([C([-6.5, 105, 18], [1.5, 9, 8], "paint2"),                      # trunnion cheeks
                 C([5, 105, 18], [1.5, 9, 8], "paint2")]) + hub(0, 110, 22, 15, 5)

def artillery_barrel():
    return late([C([-4.5, 105.5, 18], [9, 9, 12], "paint"),                     # breech
                 C([-3.5, 106.5, 0], [7, 7, 18], "metal"),                       # recoil sleeve
                 C([-2, 108, -26], [4, 4, 26], "steel"),                         # barrel
                 C([-3, 107, -30], [6, 6, 4], "dark"),                           # muzzle brake
                 C([-3.2, 108.5, -29], [6.4, 1, 2], "vent"),
                 C([-1.5, 103.5, 4], [3, 3, 12], "dark"),                        # recuperator
                 C([-1, 104, -6], [2, 2, 10], "steel"),
                 C([4.5, 104, 20], [4, 8, 8], "hazard")])                       # shell feed box

def backpack():
    """Ribbed power pack between the exhaust stacks, with side handles."""
    return [B(-12, 12, 82, 106, 18, 27, "metal"),
            B(-9, 9, 86, 102, 27, 28, "vent"),
            B(-13, -12, 88, 102, 20, 25, "steel"), B(12, 13, 88, 102, 20, 25, "steel"),
            B(-4, 4, 104, 108, 19, 23, "dark")]

ROLL_CAGE = [B(x0, x0 + 2, 112, 122, z0, z0 + 2, "steel") for x0 in (-15, 13) for z0 in (-9, 13)] + [
    B(-15, 15, 120, 122, -9, -7, "steel"), B(-15, 15, 120, 122, 13, 15, "steel"),   # cross bars
    B(-15, -13, 120, 122, -7, 13, "steel"), B(13, 15, 120, 122, -7, 13, "steel"),   # side rails
    B(-1, 1, 120, 122, -7, 13, "steel"),                                            # spine
    B(9, 10, 122, 138, 10, 11, "dark")]                                             # whip antenna

EXHAUST = [B(-17, -11, 100, 128, 18, 24, "metal"),                                  # exhaust stack
           B(-17.5, -10.5, 126, 131, 17.5, 24.5, "dark"),                           # perforated cap
           B(-16, -12, 128, 131.5, 19, 23, "vent"),
           B(-17.5, -10.5, 106, 108, 17.5, 24.5, "hazard")]

BONES = [
    ("bb_main", None, [0, 0, 0], []),
    ("skill_locator", None, [0, 0, 0], []),
    ("titan", None, [0, 0, 0], []),
    ("body1", "titan", [0, 61.0, 7.0], [
        B(-12, 12, 54, 66, -4, 16, "dark"),                                    # pelvis block
        B(-8, 8, 49, 64, -8, -4, "paint", decal={"north": "hazard_bottom"}),   # front skirt plate
        B(-7, 7, 60, 63, -8.6, -8, "dark"),
        B(-8, 8, 52, 64, 16, 19, "paint"),                                     # rear skirt plate
        B(-13, -12, 56, 64, 0, 12, "vent"), B(12, 13, 56, 64, 0, 12, "vent"),
    ]),
    ("body2", "body1", [0, 74.9, 8.8], [                                       # narrow mechanical waist
        B(-8, 8, 66, 80, -1, 13, "dark"),                                      # spine core
        B(-10, 10, 65, 69, -3, 15, "metal"),                                   # slewing ring
        B(-6, 6, 70, 79, -3, -1, "paint2"),                                    # ab plate
        B(-5, 5, 72.5, 74, -3.4, -3, "dark"), B(-5, 5, 76, 77.5, -3.4, -3, "dark"),
    ] + hub(0, 73, 9, 18, 9, "metal") + WAIST + mirror(WAIST)),
    ("body3", "body2", [0.5, 78.7, 17.8], [
        B(-18, 18, 84, 110, -8, 18, "paint"),                                  # cockpit cab
        B(-14, 14, 78, 84, -4, 15, "dark"),                                    # lower chest frame
        B(-21, -18, 86, 108, -5, 15, "paint2"), B(18, 21, 86, 108, -5, 15, "paint2"),  # side armour
        B(-21.5, -21, 90, 104, 0, 10, "vent"), B(21, 21.5, 90, 104, 0, 10, "vent"),
        B(-17, 17, 110, 112, -7, 17, "paint2"),                                # roof plate
        B(-10, 10, 112, 113, -2, 12, "vent"),                                  # roof hatch
    ] + pauldron() + mirror(pauldron()) + ROLL_CAGE + EXHAUST + mirror(EXHAUST) + backpack()),
    # The hatch is the whole upper cab front: it lifts open like a canopy.
    ("doorUp", "body3", [0, 107, -8], [
        B(-18, 18, 94, 111, -16, -8, "paint"),                                 # armoured cab front (head and chest are one block)
        B(-19, 19, 108, 112.5, -18.5, -8, "paint2"),                          # brow hood over the visor
        B(-15, 15, 99, 105, -16.6, -16, "dark"),                               # visor recess
        B(-20, -17, 93, 110, -17.5, -8, "paint2"), B(17, 20, 93, 110, -17.5, -8, "paint2"),  # cheek guards
        B(-11, 11, 94.5, 97.5, -16.6, -16, "vent"),                            # chin grille
        B(-16, -12.5, 95, 98, -17.2, -16.6, "glow"), B(12.5, 16, 95, 98, -17.2, -16.6, "glow"),  # work lights
        B(-17, 17, 105.5, 107, -16.8, -16, "hazard"),                          # warning band under the brow
    ]),
    ("eye", "doorUp", [0, 107.0, -17.0], [
        B(-13, 13, 100.5, 103.5, -17, -16.4, "visor"),                         # wide visor slit
    ]),
    ("doorDown", "body3", [0, 82.7, -5.9], [
        B(-16, 16, 80, 94, -15, -8, "paint", decal={"north": "number"}),       # lower cab armour
        B(-12, -5, 83, 89, -15.8, -15, "vent"), B(5, 12, 83, 89, -15.8, -15, "vent"),
        B(-16.5, 16.5, 78.5, 80.5, -15.5, -8, "hazard"),
        B(-3, 3, 79, 82, -17, -15, "steel"),                                   # tow hook
    ]),
    # Pivot matches weaponBack: TitanWeaponSwapLayer anchors it at other chassis' weaponBack pivot.
    ("artillery", "body3", [-24.0, 78.0, 26.0], artillery_base()),
    ("artilleryTurret", "artillery", [0, 105, 22], artillery_turret()),
    ("artilleryBarrel", "artilleryTurret", ARTILLERY_TRUNNION, artillery_barrel()),
    ("back_rocket_pod", "body3", [-24.0, 96.0, 18.0], back_rocket_pod()),
    ("weaponBack", "body3", [-24.0, 78.0, 26.0], [
        C([-28, 72, 22], [8, 16, 8], "metal"),                                  # stowed tool clamp
        C([-29, 80, 21], [10, 2, 10], "hazard"),
    ]),
    ("stowed_rifle", "weaponBack", [-24.0, 78.0, 26.0], stowed_rifle()),
    ("stowed_machine_gun", "weaponBack", [-24.0, 78.0, 26.0], stowed_machine_gun()),
    ("stowed_rocket_launcher", "weaponBack", [-24.0, 78.0, 26.0], stowed_rocket_launcher()),
    ("rightArm1", "body3", [-24.4, 94.8, 10.7], RIGHT_ARM1),
    ("rightArm2", "rightArm1", [-23.4, 72.5, 10.7], RIGHT_ARM2),
    ("rightHand", "rightArm2", [-23.3, 46.8, 11.5], RIGHT_HAND),
    ("weapon", "rightHand", [-19.8, 39.8, 10.3], []),
    ("drill", "weapon", [-19.8, 39.8, 10.3], drill(None, 10.3, -19.8)),
    ("chainsaw", "weapon", [-19.8, 39.8, 10.3], chainsaw(None, 10.3, -19.8)),
    ("rifle", "weapon", [-19.8, 39.8, 10.3], rifle(None, 10.3, -19.8)),
    ("machine_gun", "weapon", [-19.8, 39.8, 10.3], machine_gun(None, 10.3, -19.8)),
    ("rocket_launcher", "weapon", [-19.8, 39.8, 10.3], rocket_launcher(None, 10.3, -19.8)),
    ("arc_cannon", "weapon", [-19.8, 39.8, 10.3], arc_cannon(None, 10.3, -19.8)),
    ("scatter_cannon", "weapon", [-19.8, 39.8, 10.3], scatter_cannon(None, 10.3, -19.8)),
    ("inferno_flamethrower", "weapon", [-19.8, 39.8, 10.3], inferno_flamethrower(None, 10.3, -19.8)),
    ("grenade_launcher", "weapon", [-19.8, 39.8, 10.3], grenade_launcher(None, 10.3, -19.8)),
    ("leftArm1", "body3", [24.4, 94.8, 10.7], mirror(RIGHT_ARM1)),
    ("leftArm2", "leftArm1", [23.4, 72.5, 10.7], mirror(RIGHT_ARM2)),
    ("leftHand", "leftArm2", [23.3, 46.8, 11.5], mirror(RIGHT_HAND)),
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
    ordered = [c for _, _, _, cubes in BONES for c in cubes if not c.get("late")]
    ordered += [c for _, _, _, cubes in BONES for c in cubes if c.get("late")]
    for c in ordered:
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

def swatch(m):
    """(uv, size) of the largest packed cube of material m: a patch other builders (SMG, cockpit arms)
    can map faces into. Call pack() first."""
    cubes = [c for _, _, _, cs in BONES for c in cs if c["m"] == m and "dims" in c]
    c = max(cubes, key=lambda c: c["dims"][0] * c["dims"][1] * c["dims"][2])
    return c["uv"], list(c["dims"])

def faces(c):
    u, v = c["uv"]
    w, h, d = c["dims"]
    return {"up": (u + d, v, w, d), "down": (u + d + w, v, w, d),
            "east": (u, v + d, d, h), "north": (u + d, v + d, w, h),
            "west": (u + d + w, v + d, d, h), "south": (u + 2 * d + w, v + d, w, h)}

# Rest rotations of the Ion rig. trooper_titan.animation.json was cloned from Ion and its keyframes
# are offsets on top of these. (Not the hatch: it is modelled closed and hinged at its own top-back edge.) Like Ion, cubes are authored "raw" (limbs hanging straight down
# through the joint pivots); the rest rotation is never seen because an animation always plays.
REST = {"artilleryBarrel": [-ARTILLERY_ELEVATION, 0, 0],  # negative x tips the -z end up
        "rightArm1": [0, -180, 30], "rightHand": [0, -180, 0],
        "weapon": [90, 0, 90], "leftArm1": [0, 180, -30], "leftHand": [0, 180, 0],
        "rightLeg3": [-15, 0, 0], "rightLeg2": [37.5, 0, 0], "rightLeg1": [-15, 0, 0], "rightFoot": [-7.5, 0, 0],
        "leftLeg3": [-15, 0, 0], "leftLeg2": [37.5, 0, 0], "leftLeg1": [-15, 0, 0], "leftFoot": [-7.5, 0, 0]}

def geo_json():
    bones = []
    for name, parent, piv, cubes in BONES:
        b = {"name": name, "pivot": piv}
        if parent:
            b["parent"] = parent
        if name in REST:
            b["rotation"] = REST[name]
        if cubes:
            out = []
            for c in cubes:
                e = {"origin": [round(v, 3) for v in c["o"]], "size": [round(v, 3) for v in c["s"]], "uv": c["uv"]}
                if "rot" in c:
                    e["pivot"], e["rotation"] = [round(v, 3) for v in c["piv"]], c["rot"]
                out.append(e)
            b["cubes"] = out
        bones.append(b)
    return {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": f"geometry.{ID}_titan", "texture_width": TEX, "texture_height": TEX,
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
         "vent": (58, 60, 63), "glow": (255, 214, 120),
         "amber": (206, 146, 46)}
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
                        if mat == "paint" and CAMO:  # 2-px digital camo in three tones of the scheme
                            v = vnoise(gx // 2, gy // 2, 3, 21)
                            if v > 0.62:
                                col = mix(col, paint2, 0.75)
                            elif v < 0.34:
                                col = mul(col, 0.7)
                        elif mat == "cloth":  # worn woven fabric (paint2): weave, fold streaks, stains, frayed hem
                            if side and j >= fh - 3 and h2(gx, gy, 12) < 0.18 + 0.12 * (j - (fh - 3)):
                                continue  # hole in the hem: left transparent (cutout)
                            fold = 0.86 + 0.18 * vnoise(gx * 3, gy // 6, 1, 13)  # soft irregular folds
                            stain = 0.8 + 0.3 * vnoise(gx, gy, 7, 8)
                            col = mul(paint2, (0.9 + 0.1 * ((i + j) % 2)) * fold * stain)
                    col = mul(col, 1 + n)
                    # panel seams, top-edge highlight, rivets
                    if edge == 0 and mat != "cloth":
                        col = mul(col, 0.62)
                    elif j == 1 and side and mat != "cloth":
                        col = mul(col, 1.15)
                    if mat in ("paint", "paint2", "metal") and fw >= 12 and i in (fw // 2,):
                        col = mul(col, 0.72)
                    if mat in ("paint", "paint2", "metal") and fh >= 14 and j == int(fh * 0.4):
                        col = mul(col, 0.72)
                    if mat == "cloth":
                        pass
                    elif fw >= 12 and fh >= 12 and i in (2, fw - 3) and j in (2, fh - 3):
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
    if kind == "stripe":  # recon racing stripes: two bold bands
        for i in range(fw):
            for j in range(fh):
                band = (i + j) % 12
                if band in (2, 3, 4) or band == 7:
                    put(fx + i, fy + j, WHITE if band != 7 else (40, 40, 40))
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
    with open(f"{ROOT}/geo/{ID}_titan.geo.json", "w") as f:
        json.dump(geo_json(), f, indent=1)
    tex_dir = f"{ROOT}/textures/entity/titan/{ID}"
    os.makedirs(tex_dir, exist_ok=True)
    for idx, scheme in enumerate(SCHEMES):
        name = f"{ID}_titan.png" if idx == 0 else f"{ID}_titan_{idx}.png"
        write_png(os.path.join(tex_dir, name), render(cubes, scheme))
        print("wrote", name, scheme[0])
    print(len(cubes), "cubes")

if __name__ == "__main__":
    main()
