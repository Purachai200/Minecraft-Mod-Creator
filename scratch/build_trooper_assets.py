"""MP-01 Trooper Titan: builds geo/trooper_titan.geo.json and the base + 8 camo textures.

Run from the repo root:  python3 scratch/build_trooper_assets.py
Bone names and pivots match the old rig (animations, TitanModel IK and seat offsets rely on them).
Front of the titan is -Z, its right side is -X. Left-side parts are mirrored from the right.
"""
import json, os, random, struct, zlib

ROOT = "Titan Combat/src/main/resources/assets/titancombat"
TEX = 1024
ID = "trooper"  # build_scout_assets.py reuses this module with its own ID, BONES and SCHEMES
CAMO = True     # digital camo on "paint" (the Letheus look); the Scout and Shade turn it off

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

# ---- UAF-X101 "Letheus" style mass-production frame (reference: the Letheus ground-type sheet).
# Raw frame: limbs hang straight down through their joint pivots (see REST below).

RIGHT_ARM1 = [                                                                  # shoulder + upper arm
    B(-41, -22, 88, 104, -5, 24, "paint", decal={"west": "mp01"}),            # boxy pauldron
    B(-39, -24, 104, 106, -3, 22, "paint2"),                                  # pauldron cap
    B(-41.5, -21.5, 86.5, 88.5, -5.5, 24.5, "hazard"),                         # trim
    B(-42, -38, 92, 100, -7, -3, "dark"),                                      # sensor pod
    B(-41.5, -38.5, 95, 97, -7.4, -7, "glow"),
    B(-34, -32, 106, 110, 2, 4, "steel"),                                      # grab handle
    B(-34, -32, 106, 110, 16, 18, "steel"),
    B(-34, -32, 109, 111, 2, 18, "steel"),
    B(-29, -20, 72, 88, 6, 15, "dark"),                                        # upper arm frame
    B(-31, -29, 74, 86, 5, 16, "paint"),                                       # outer bicep plate
    B(-28, -22, 76, 86, 4, 6, "paint2"),                                       # front plate
] + hub(-24, 90, 10.5, 10, 11) + piston(-20.5, 87, 73, 13, w=2.4) + hose(-30.5, 86, 74, 17, 2)

RIGHT_ARM2 = [                                                                  # forearm
    B(-33, -15, 49, 68, 1, 20, "paint", decal={"west": "hazard_bottom"}),     # heavy forearm armor
    B(-34, -33, 54, 65, 5, 15, "paint2"),                                      # outer plate
    B(-34.6, -34, 57, 63, 7.5, 12.5, "dark"),                                  # port ring
    B(-35, -34.6, 58.5, 61.5, 9, 11, "steel"),
    B(-32, -16, 66, 69, 2, 19, "metal"),                                       # elbow cuff
    B(-31, -17, 52, 66, -0.5, 1, "paint2"),                                    # front guard
    B(-31, -17, 46, 50, 3, 18, "dark"),                                        # wrist band
] + hub(-24, 70.5, 10.7, 12, 9)

RIGHT_HAND = fist(-28.3, 46.8, 6) + hub(-23.3, 46.8, 11.5, 10, 5)

RIGHT_LEG3 = [                                                                  # hip
    B(-25, -21, 48, 62, -2, 14, "paint", decal={"west": "hazard_bottom"}),    # hip side armor
    B(-19, -10, 52, 64, 2, 12, "dark"),
] + hub(-14.5, 57, 7, 18, 12)

RIGHT_LEG2 = [                                                                  # thigh
    B(-21, -8, 28, 48, -5, 10, "paint"),
    B(-20, -9, 32, 46, -7, -5, "paint2"),                                      # front plate
    B(-19, -10, 24, 30, -2, 8, "dark"),                                        # knee frame
    B(-22, -21, 31, 45, -3, 8, "paint2"),                                      # outer plate
] + piston(-14.5, 46, 30, -8.5) + hose(-19, 46, 30, 12, 2.5)

RIGHT_LEG1 = [                                                                  # knee + shin
    B(-22, -7, 16, 32, -12, -6, "paint"),                                      # tall knee guard
    B(-16, -13, 18, 30, -12.6, -12, "dark"),                                   # guard slot
    B(-21, -19, 30, 33, -14, -12, "steel"),                                    # white U-handle
    B(-10, -8, 30, 33, -14, -12, "steel"),
    B(-21, -8, 32, 34, -15, -13, "steel"),
    B(-21, -8, 6, 20, -6, 8, "paint"),                                         # shin
    B(-20, -9, 8, 18, -7, -6, "paint2"),
    B(-19, -10, 8, 18, 8, 12, "dark"),                                         # calf
] + hub(-14.5, 23, 2, 15, 10) + piston(-22, 19, 8, 1, w=2.4)

RIGHT_FOOT = [
    B(-23, -6, 0, 4, -18, 10, "dark"),                                         # sole
    B(-22, -7, 0, 6, -20, -10, "paint"),                                       # toe cap
    B(-22.5, -6.5, 0, 1.5, -20.5, -18, "hazard"),
    B(-21, -8, 4, 8, -12, 2, "paint2"),                                        # instep armor
    B(-21, -8, 0, 6, 6, 12, "metal"),                                          # heel
] + hub(-14.5, 7, -1, 12, 7)

WAIST = piston(-11.5, 80, 64, 9) + hose(-5, 79, 65, 14, 2)

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
    """Letheus back unit: ribbed power pack, side handles and a tall whip antenna."""
    return [B(-14, 14, 82, 106, 17, 26, "metal"),
            B(-10, 10, 86, 100, 26, 27, "vent"),
            B(-15, -14, 88, 102, 19, 24, "steel"), B(14, 15, 88, 102, 19, 24, "steel"),
            B(8, 12, 104, 108, 18, 22, "dark"),
            B(9.5, 10.5, 108, 132, 19.5, 20.5, "dark")]

BONES = [
    ("bb_main", None, [0, 0, 0], []),
    ("skill_locator", None, [0, 0, 0], []),
    ("titan", None, [0, 0, 0], []),
    ("body1", "titan", [0, 61.0, 7.0], [
        B(-11, 11, 54, 66, -4, 16, "dark"),                                    # pelvis block
        B(-5, 5, 50, 62, -7, -4, "paint"),                                     # groin plate
        B(-11, -5.5, 52, 64, -6, -4, "paint"), B(5.5, 11, 52, 64, -6, -4, "paint"),
        B(-10, -6, 60, 67, -9, -6, "amber"), B(6, 10, 60, 67, -9, -6, "amber"),  # belt pouches
        B(-14, -11, 58, 66, 0, 8, "amber"), B(11, 14, 58, 66, 0, 8, "amber"),
        B(-8, 8, 54, 64, 16, 18, "paint"),                                     # rear plate
    ]),
    ("body2", "body1", [0, 74.9, 8.8], [
        B(-9, 9, 66, 79, -2, 14, "dark"),                                      # waist core
        B(-11, 11, 66, 70, -4, 16, "metal"),                                   # belt
        B(-7, 7, 71, 78, -4, -2, "paint2"),                                    # ab plates
        B(-12, -9, 70, 78, 0, 12, "vent"), B(9, 12, 70, 78, 0, 12, "vent"),
    ] + WAIST + mirror(WAIST)),
    ("body3", "body2", [0.5, 78.7, 17.8], [
        B(-16, 16, 80, 106, -8, 17, "paint"),                                  # chest core
        B(-19, -16, 82, 96, -6, 14, "paint2"), B(16, 19, 82, 96, -6, 14, "paint2"),  # side armor
        B(-20, -16, 96, 106, -4, 14, "dark"), B(16, 20, 96, 106, -4, 14, "dark"),    # shoulder sockets
        B(-12, 12, 106, 108, -6, 14, "dark"),                                  # collar
        B(-17, 17, 104, 107, -8, 6, "paint2"),                                 # chest top lip
    ] + backpack()),
    # The hatch is the whole upper chest plus the helmet: it lifts open like a canopy.
    ("doorUp", "body3", [0, 107, -8], [
        B(-15, 15, 95, 107, -15, -8, "paint"),                                 # upper chest plate
        B(-16, -2, 99, 107, -16, -14, "paint2"), B(2, 16, 99, 107, -16, -14, "paint2"),
        B(-8, 8, 108, 120, -11, 3, "dark"),                                    # helmet
        B(-8.5, 8.5, 116, 121, -11.5, 3.5, "paint"),                           # helmet crown
        B(-6, 6, 109, 116, -13, -11, "steel"),                                 # face plate
        B(-5, 5, 107, 109, -12, -6, "dark"),                                   # neck
        B(5, 6, 118, 128, -2, -1, "dark"),                                     # helmet antenna
    ] + hub(-9, 97, -16.5, 8, 4, "amber") + hub(9, 97, -16.5, 8, 4, "amber") + [
        B(-3, 3, 95, 100, -17, -15, "steel"),                                  # chest cylinder block
    ]),
    ("eye", "doorUp", [0, 107.0, -17.0], [
        B(-4.5, 4.5, 112.5, 114.5, -13.6, -13, "visor"),                       # visor slit
        B(-7, -6, 115, 119, -11.6, -11, "visor"),                              # side sensor light
    ]),
    ("doorDown", "body3", [0, 82.7, -5.9], [
        B(-13, 13, 81, 95, -14, -8, "paint", decal={"north": "number"}),
        B(-10, -4, 83, 89, -15, -14, "vent"), B(4, 10, 83, 89, -15, -14, "vent"),
        B(-13.5, 13.5, 80, 81.5, -14.5, -8, "hazard"),
    ]),
    # Pivot matches weaponBack: TitanWeaponSwapLayer anchors it at other chassis' weaponBack pivot.
    ("artillery", "body3", [-24.0, 78.0, 26.0], artillery_base()),
    ("artilleryTurret", "artillery", [0, 105, 22], artillery_turret()),
    ("artilleryBarrel", "artilleryTurret", ARTILLERY_TRUNNION, artillery_barrel()),
    ("weaponBack", "body3", [-24.0, 78.0, 26.0], [
        C([-28, 72, 22], [8, 16, 8], "metal"),                                  # stowed tool clamp
        C([-29, 80, 21], [10, 2, 10], "hazard"),
    ]),
    ("rightArm1", "body3", [-24.4, 94.8, 10.7], RIGHT_ARM1),
    ("rightArm2", "rightArm1", [-23.4, 72.5, 10.7], RIGHT_ARM2),
    ("rightHand", "rightArm2", [-23.3, 46.8, 11.5], RIGHT_HAND),
    ("weapon", "rightHand", [-19.8, 39.8, 10.3], []),
    ("drill", "weapon", [-19.8, 39.8, 10.3], drill(None, 10.3, -19.8)),
    ("chainsaw", "weapon", [-19.8, 39.8, 10.3], chainsaw(None, 10.3, -19.8)),
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
