"""Tier-3 walkable giants: LPD amphibious assault ship, transport submarine, C-17 style airlifter."""
import math
from fleet_common import *
from fleet_interior import *
from fleet_ships import make_hull, rail, mount, hpad, tier, lower, bollards, finish


# ============================================================ 1. LPD with a flooded-dock well deck under the flight deck
def lpd():
    D, YF, zb, zs, hw0, wl = 52, 124, -280, 280, 52, 22
    dk = lambda z: D
    inner = {"floor": 8, "ranges": [(-196, 20)], "hatches": [(8, 24, -64, -28)]}
    hull, B, Hb = make_hull(zb, zs, hw0, wl, dk, 0.36, inner=inner, zstop=20)
    ex = lower([(-196, -148, "bunks"), (-148, -100, "bunks"), (-100, -76, "stores"), (-76, -16, "stairs"), (-16, 20, "engine")], dk, 8, Hb, (8, 24, -64, -28), end_open=50)
    z = 20                                                                                      # aft: dock well under the flight deck
    while z < zs - 0.01:
        z1 = min(z + 12, zs); hw = B((z + z1) / 2); hb = hw - 9
        hull += [box(-hb, 0, z, hb, 20, z1, BELLY, up=WALK), wall(1, 34, hw, 20, YF - 3, z, z1, HULL), wall(-1, 34, hw, 20, YF - 3, z, z1, HULL),
                 box(-hw, YF - 3, z, hw, YF, z1, DARK, up=WALK, down=INTER)]
        z = z1
    ex += wx(21.6, -34, 34, 20, YF - 3, [(-7, 7, 20, 20 + DOOR_H, "door")]) + step_run(2, 8, 20, -7, 7, 8, 8, 20, 3)     # engine room (y 8) up to the well deck (y 20)
    gate = [box(-34, 20, 278.4, 34, 112, 280, HULL, north=INTER), box(-35, 20, 277.6, -33, 112, 281, DARK), box(33, 20, 277.6, 35, 112, 281, DARK)]
    for zz in range(30, 270, 40):
        ex += [box(s * 33.2, 20, zz, s * 34, 24, zz + 3, RED) for s in (-1, 1)] + [box(-26 + k * 17, 20, zz, -23 + k * 17, 20.4, zz + 3, SPIN) for k in range(4)]   # dock tie-downs
    ex += tier(28, -76, 16, D, 36, [(-76, 16, "stairs")], doors_z=(-8,), front=[(-7, 7, D, D + DOOR_H, "door")], back=[(-7, 7, D, D + DOOR_H, "door")],
               stair=(-24, -8, -38, -10), ceil_hole=(-24, -8, -38, -10))
    ex += tier(26, -48, 12, D + 36, 36, [(-48, 12, "stairs")], doors_z=(-20,), stair=(8, 24, -36, -8), ceil_hole=(8, 24, -36, -8))
    ex += tier(24, -44, 8, YF, 36, [(-44, 8, "bridge")], doors_z=(-20,), front=[(-20, 20, YF + 12, YF + 28, "win")], back=[(-7, 7, YF, YF + DOOR_H, "door")], only=-1)
    ex += [box(-10, YF - 3, 8, 10, YF, 20, DARK, up=WALK)] + [tube((s * 10, YF, z), (s * 10, YF + 11, z), 1.0, SPIN) for s in (-1, 1) for z in (10, 18)]
    ex += hpad(-40, 40, 20, 280, YF, cz=110) + hpad(-40, 40, 20, 280, YF, cz=206)
    ex += rail(B, lambda z: YF, 24, 270, 20) + rail(B, dk, -236, 16, 14)
    ex += [tube((0, YF + 36, -14), (0, YF + 80, -14), 3.4, DARK), tube((-18, YF + 64, -14), (18, YF + 64, -14), 1.4, DARK), box(-9, YF + 80, -20, 9, YF + 96, -8, WHITE)]
    ex += bollards(B, dk, (-250, -200, -120, -60)) + [box(-40, D, -250, 40, D + 1, -90, DARK, up=WALK)]
    mounts = [mount("mount_bow", 0, D, -190, True), mount("mount_island", 0, YF + 36, -34), mount("mount_aft_l", 40, YF, 262), mount("mount_aft_r", -40, YF, 262)]
    radar = bone("radar", "hull", [0, YF + 96, -14], [box(-3, YF + 96, -17, 3, YF + 101, -11, DARK), box(-24, YF + 101, -15.2, 24, YF + 104.4, -12.8, HULL)])
    meta = {"id": "lpd_assault", "name": "LPD Amphibious Assault Ship", "tier": 3, "seat_capacity": 10,
            "payload": "well deck dock for 3+ Titans / 8 Exoframes (stern gate opens to a ramp); flight deck for 2 helicopters (Mi-26 fits)",
            "hull_rgb": (118, 124, 130), "belly_rgb": (92, 46, 40), "seats": {"helm": [10, YF, -24], "co_helm": [-10, YF, -24], "captain": [0, YF, -10], "bunks": [20, 8, -170]},
            "decks": {"foredeck": [[-24, D, -240], [24, D, -90]], "island_walkway_l": [[28, D, -52], [B(0) - 3, D, 20]], "island_walkway_r": [[-(B(0) - 3), D, -52], [-28, D, 20]],
                      "tier1_floor": [[-26, D, -51], [26, D, 15]], "tier2_floor": [[-24, D + 36, -47], [24, D + 36, 11]], "bridge_floor": [[-22, YF, -43], [22, YF, 7]],
                      "island_link": [[-10, YF, 8], [10, YF, 20]], "flight_deck": [[-40, YF, 20], [40, YF, 278]], "well_floor": [[-34, 20, 22], [34, 20, 278]],
                      "stern_gate_open": [[-34, 20, 280], [34, 20, 372]], "lower_deck": [[-30, 8, -196], [30, 8, 20]]},
            "interior": ["lower deck (floor y=8): 2 bunk rooms -196..-100, stores -100..-52, stair hatch -52..-16 (x 8..22), engine room -16..20",
                         "island: tier 1 mess + stairs, tier 2 officers, tier 3 bridge (floor 124 = flight deck level, link bridge at z 8..20)",
                         "well deck: floor y=20, clear height ~100 px (Titans fit), open to the stern gate; bulkhead door at z 21 into the engine room"],
            "mounts": [{"bone": "mount_bow", "pos": [0, D + 8, -190], "class": "large", "facing": 0, "arc": 290, "pitch": [-8, 75]},
                       {"bone": "mount_island", "pos": [0, YF + 44, -34], "class": "pintle", "facing": 0, "arc": 360, "pitch": [-5, 85]},
                       {"bone": "mount_aft_l", "pos": [40, YF + 8, 262], "class": "pintle", "facing": 90, "arc": 200, "pitch": [-10, 70]},
                       {"bone": "mount_aft_r", "pos": [-40, YF + 8, 262], "class": "pintle", "facing": -90, "arc": 200, "pitch": [-10, 70]}],
            "swings": [("stern_gate", [0, 20, 280], [0, 112, 280], [-90, 0, 0], 2, 1, 40)],
            "scale": 0.62, "bounds_w": 40, "bounds_h": 16, "bounds_off": [0, 6, 0], "view": (35, -25)}
    return finish(hull, ex, mounts, radar, meta, extra_bones=[bone("stern_gate", "hull", [0, 20, 280], gate)]), meta


def lpd_anims():
    return anim_file("lpd_assault", {"idle": {"loop": True, "bones": {"stern_gate": {"rotation": [0, 0, 0]}, "radar": {"rotation": [0, 0, 0]}}},
                                     "radar_spin": {"loop": True, "animation_length": 4.0, "bones": spin({"radar": 1}, 4.0)},
                                     "gate_open": {"loop": True, "bones": {"stern_gate": {"rotation": [-90, 0, 0]}}}})


# ============================================================ 2. Transport submarine
CY, R0, FLY = 46, 44, 16


def _ring(z0, z1, r, skip=()):
    out = []
    for k in range(16):
        if k in skip: continue
        a = math.radians(22.5 * k); chord = 2 * r * math.sin(math.radians(11.25)) + 0.8
        out.append(rbox(r * math.cos(a), CY + r * math.sin(a), (z0 + z1) / 2, 2.6, chord, z1 - z0, [0, 0, -22.5 * k], HULL, west=INTER))
    return out


def sub():
    hull, ex = [], []
    z = -260
    while z < 260 - 0.01:
        z1 = z + 20; zm = z + 10
        r = R0 if -170 <= zm <= 170 else (R0 * math.sqrt(max(0.02, 1 - ((-170 - zm) / 90) ** 2)) if zm < -170 else R0 - (R0 - 9) * (zm - 170) / 90)
        hatch = -60 <= z and z1 <= 20
        hull += _ring(z, z1, r, skip=(4,) if hatch else ())
        if -170 <= zm <= 170:
            hf = math.sqrt(R0 ** 2 - (CY - FLY) ** 2) - 1
            hull += [box(-hf, FLY - 3, z, hf, FLY, z1, DARK, up=WALK)]
        z = z1
    for zc, a, b, c in ((-260, 20, 14, 8), (258, 13, 9, 5)):                                    # octagon end caps
        ex += [box(-a, CY - c, zc, a, CY + c, zc + 2.4, HULL), box(-b, CY - b, zc, b, CY + b, zc + 2.4, HULL), box(-c, CY - a, zc, c, CY + a, zc + 2.4, HULL)]
    hf = math.sqrt(R0 ** 2 - (CY - FLY) ** 2) - 1
    def bulk(zz, door=True, dx=(-7, 7)):
        o = [(dx[0], dx[1], FLY, FLY + DOOR_H, "door")] if door else []
        return wx(zz, -hf - 1, hf + 1, FLY, 78, o) + [box(-x, 78, zz - T, x, y, zz, HULL, north=INTER, south=INTER) for x, y in ((26, 82), (20, 86), (12, 89))]
    rooms = [(-170, -122, "bunks"), (-122, -60, "mess"), (-60, 20, "stairs"), (20, 68, "bridge"), (68, 170, "stores")]
    for za, zb, kind in rooms:
        ex += bulk(za, za > -170) + furnish(kind, hf, FLY, za + T, zb) if kind != "stairs" else bulk(za, True, (10, 24))     # stair hall: door beside the stair, not in front of it
    ex += bulk(170, False) + step_run(2, 10, -56, -8, 8, FLY, FLY, 90, 16)
    ex += [tube((0, FLY, 44), (0, 86, 44), 4, SPIN)]                                           # periscope column
    for z0, z1 in ((-170, 28), (72, 170)):                                                      # walkable casing deck with rails
        hole = (-8, 8, -56, 10) if z0 == -170 else None
        ex += slab(-8, 8, z0, z1, 88, 2.6, hole, top=WALK, bot=DARK)
        ex += [tube((s * 8, 90, z), (s * 8, 101, z), 0.9, SPIN) for s in (-1, 1) for z in range(int(z0) + 6, int(z1), 24)]
    ex += H.solid(28, 72, 12, 86, 126, c=4) + [box(-9, 126, 30, 9, 128, 70, DARK, up=WALK)]
    ex += [tube((s * 9, 128, z), (s * 9, 137, z), 0.9, SPIN) for s in (-1, 1) for z in (32, 50, 68)] + [tube((-9, 137, 32), (-9, 137, 68), 0.8, SPIN), tube((9, 137, 32), (9, 137, 68), 0.8, SPIN)]
    ex += [tube((x, 128, 44), (x, 158, 44), 2, DARK) for x in (-4, 4)] + [tube((0, 128, 56), (0, 150, 56), 1.4, SPIN), box(-0.8, 150, 55, 0.8, 160, 57, RED)]
    ex += [box(s * 12, 98, 34, s * 32, 100, 52, DARK) for s in (-1, 1)]                          # sail planes
    ex += [box(s * 52 - 2, CY - 1, -200, s * 52 + 2, CY + 1, -176, DARK) for s in (-1, 1)] + [box(s * 28, CY - 1, -200, s * 52, CY + 1, -178, HULL) for s in (-1, 1)]   # bow planes
    ex += [box(-1.6, CY - 32, 236, 1.6, CY + 32, 262, HULL), box(-30, CY - 1.4, 238, 30, CY + 1.4, 262, HULL)]                       # rudders + stern planes
    prop = [box(-3, CY - 3, 262, 3, CY + 3, 270, DARK)] + [rbox(0, CY + 12, 266, 3, 22, 1.4, [0, 0, -72 * k], BLADE, pivot=[0, CY, 266]) for k in range(5)]
    mounts = [mount("mount_deck", 0, 90.6, -130)]
    meta = {"id": "transport_sub", "name": "Transport Submarine", "tier": 2, "seat_capacity": 14, "payload": "2 Exoframes in the stores bay (kneeling); 1 deck gun",
            "hull_rgb": (52, 60, 70), "belly_rgb": (36, 40, 46), "seats": {"helm": [0, FLY, 30], "co_helm": [16, FLY, 30], "captain": [-16, FLY, 30], "bunks": [24, FLY, -150], "exo_a": [0, FLY, 90], "exo_b": [0, FLY, 140]},
            "decks": {"interior_floor": [[-31, FLY, -170], [31, FLY, 170]], "casing_deck_fore": [[-8, 90.6, -170], [8, 90.6, -58]]},
            "interior": ["pressure hull (floor y=16, clear ~70 px): bunks -170..-122, mess/galley -122..-60, stair hall -60..20 (45 deg stair rising to the crown hatch), control room 20..68, stores bay 68..170",
                         "topside: walkable casing deck over the hull crown (x +-8) and the sail's open bridge; stair top at y=90 meets the casing deck at z=16"],
            "mounts": [{"bone": "mount_deck", "pos": [0, 98.6, -130], "class": "large", "facing": 0, "arc": 300, "pitch": [-8, 60]}],
            "extra": ["Hull centre y=46 (radius 44 px); design waterline for surfacing ~ y=60. Submerged play needs a swim/air-pocket rule in Java: the hull interior is dry model volume only.",
                      "`prop` spins about Z."],
            "scale": 0.8, "bounds_w": 36, "bounds_h": 14, "bounds_off": [0, 5, 0], "view": (35, -22)}
    bones = [bone("root", None, [0, 0, 0], []), bone("hull", "root", [0, 0, 0], hull + ex, locators={"mount_deck": [0, 98.6, -130]}), mounts[0], bone("prop", "hull", [0, CY, 266], prop)]
    return bones, meta


def sub_anims():
    return anim_file("transport_sub", {"idle": {"loop": True, "bones": {"prop": {"rotation": [0, 0, 0]}}},
                                       "swim": {"loop": True, "animation_length": 0.5, "bones": spin({"prop": 2}, 0.5)}})


# ============================================================ 3. C-17 style airlifter, walkable from the flight deck to the ramp
def airlifter():
    HW, YB, TOP, FLR = 44, 16, 118, 40
    fus, deck, ramp, gear = [], [], [], []
    A, X = fus.append, fus.extend
    for i in range(7):                                                                          # flight deck + nose, hollow, tapering
        z1 = -190 - 20 * i; z0 = z1 - 20; hw = HW - 16 * (i + 1) / 7; yt = TOP - 30 * (i + 1) / 7
        X(H.shell(z0, z1, hw, YB + 8 * (i + 1) / 7, yt, w=4, floor=True, inner=INTER, roof=True))
        if i >= 2:                                                                              # side windows follow the tapering nose
            for s in (-1, 1): A(box(s * (hw - 1.4), 62, z0, s * (hw + 0.2), yt - 6, z1, GLASS)); A(box(s * (hw - 1.8), 62, z1 - 1.2, s * (hw + 0.6), yt - 4, z1, HULL))
    A(box(-24, 24, -334, 24, 58, -330, HULL)); A(box(-26, 85, -334, 26, 89, -330, HULL)); A(rbox(0, 72, -331.6, 50, 30, 1, [-14, 0, 0], GLASS))
    for s in (-1, 1): A(rbox(s * 14, 72, -332, 1.8, 31, 1.8, [-14, 0, 0], HULL))
    A(rbox(0, 72, -332, 1.8, 31, 1.8, [-14, 0, 0], HULL))
    zs = [-190 + 20 * i for i in range(24)]
    for z0, z1 in zip(zs, zs[1:]): X(H.shell(z0, z1, HW, YB, TOP, w=4, floor=True, inner=INTER, roof=True))
    # upswept tail cone above and behind the ramp
    zt = [270, 287, 304, 321, 338]
    for i, (z0, z1) in enumerate(zip(zt, zt[1:])):
        X(H.solid(z0, z1, 44 - 9 * (i + 1), 100 + 6 * i, 118 + 5 * i, c=4))
    for i, (z0, z1) in enumerate(zip(zt[:3], zt[1:4])):
        X(H.solid(z0, z1, 38 - 10 * (i + 1), 40 + 18 * i, 100 + 6 * i, c=3))
    # ---- flight deck, crew rest, cargo bay interiors
    deck += [box(-40, 36, -188, 40, 40, 270, DARK, up=WALK), box(-26, 36, -330, 26, 40, -188, DARK, up=WALK)]
    for z in (-296, -276):
        for s in (-1, 1): A(box(s * 12 - 5, 40, z - 6, s * 12 + 5, 46, z + 6, INTER)); A(rbox(s * 12, 53, z + 7, 10, 22, 2.6, [-8, 0, 0], INTER))
    X(console(0, 40, -322, 40, 1) + [box(-20, 86, -318, 20, 88.4, -290, INTER)] + console(-22, 40, -296, 8, -1) + console(22, 40, -296, 8, -1))
    X(wx(-250, -31, 31, 40, 97, [(-7, 7, 40, 40 + DOOR_H, "door")]))
    X(furnish("bunks", 34, 40, -248, -190) + head(24, 40, -196) + wx(-190, -40, 40, 40, 114, [(-7, 7, 40, 40 + DOOR_H, "door")]))
    for s in (-1, 1):                                                                           # jump seats + cargo roller tracks + tie-down grid
        for z in range(-172, 230, 36): A(box(s * 36, 40, z, s * 41, 47, z + 26, INTER)); A(box(s * 40.4, 47, z, s * 41.4, 62, z + 26, INTER))
        deck.append(box(s * 17, 40, -186, s * 21, 41.6, 268, DARK, up=SPIN))
        for z in range(-160, 250, 40): deck += dring(s * 30, 40, z)
    # ---- ramp (closed = vertical door, open = -135 deg slope to the ground)
    ramp += [box(-40, 40, 270, 40, 100, 272.4, HULL, north=PLATE), box(-41.6, 40, 268, -38, 100, 273, DARK), box(38, 40, 268, 41.6, 100, 273, DARK), box(-40, 98, 268, 40, 101, 273, DARK)]
    ramp += [box(-40, 40 + 12 * k, 272.4, 40, 41.4 + 12 * k, 273.4, DARK) for k in range(4)]
    # ---- swept high wings, engines, T-tail
    wing, eng = [], []
    for i in range(12):
        ch = 128 - 6.8 * i; z0 = -40 + 14 * i; y = 118 - 0.5 * i; th = 12 - 0.6 * i
        for s in (-1, 1): wing.append(box(s * (44 + 26 * i) - (0 if s > 0 else 26), y, z0, s * (44 + 26 * i) + (26 if s > 0 else 0), y + th, z0 + ch, HULL))
    wing.append(box(-44, 118, -40, 44, 130, 88, HULL))                                           # wing carry-through box sitting on the fuselage crown
    for ex_, i in ((110, 2.6), (190, 5.7)):
        z0 = -40 + 14 * i
        for s in (-1, 1):
            cx = s * ex_; cz = z0 - 6
            eng += [box(cx - 9, 92, cz - 6, cx + 9, 110, cz + 44, HULL), box(cx - 7, 93.5, cz - 8, cx + 7, 108.5, cz - 6, DARK, north=GRILLE), box(cx - 6, 95, cz + 44, cx + 6, 107, cz + 52, SOOT),
                    tube((cx, 110, cz + 10), (cx, 118 - 0.5 * i + 4, cz + 10), 3, DARK)]
    for i in range(12):
        fin = [box(-2.2, 118 + 12 * i, 236 + 6 * i, 2.2, 130 + 12 * i, 236 + 6 * i + 70 - 3.6 * i, HULL)]
        wing += fin
    wing += [box(-92, 262, 300, 92, 269, 340, HULL), box(-92, 262, 300, 92, 269, 304, DARK), box(-2.4, 269, 316, 2.4, 272, 322, RED)]
    # ---- landing gear: nose twin + main sponsons with 3 wheel pairs
    gear += [box(-4, 16, -246, 4, 32, -240, DARK), box(-1.6, 11, -244, 1.6, 17, -242, SPIN)]
    for s in (-1, 1):
        fus += [box(s * 44, 14, 84, s * 64, 64, 224, HULL), box(s * 50, 10, 90, s * 62, 14, 218, DARK)]
    bones = [bone("root", None, [0, 0, 0], []),
             bone("fuselage", "root", [0, 0, 0], fus + wing + eng, locators={"seat_pilot": [12, 46, -296], "seat_copilot": [-12, 46, -296], "loadmaster": [0, 40, -200],
                                                                          "titan_slot_a": [0, 40, -60], "titan_slot_b": [0, 40, 100], "exo_slot_a": [-18, 40, 20], "exo_slot_b": [18, 40, 20],
                                                                          **{f"jump_{sn}{i}": [s * 34, 47, z + 13] for sn, s in (("l", 1), ("r", -1)) for i, z in enumerate(range(-172, 230, 36))}}),
             bone("cargo_deck", "fuselage", [0, 40, 40], deck), bone("cargo_ramp", "fuselage", [0, 40, 270], ramp),
             bone("gear_nose", "fuselage", [0, 32, -243], gear),
             bone("wheel_nose", "gear_nose", [0, 11, -243], wheel12(-6.5, 11, -243, 6, 11, False, False) + wheel12(6.5, 11, -243, 6, 11, False, False))]
    for s, sn in ((1, "l"), (-1, "r")):
        for k, z in enumerate((104, 140, 176)):
            bones.append(bone(f"wheel_m{sn}{k}", "fuselage", [s * 56, 14, z], wheel12(s * 52, 14, z, 9, 14, False, False) + wheel12(s * 62, 14, z, 9, 14, False, False)))
    meta = {"id": "c17_airlifter", "name": "C-17 Style Strategic Airlifter", "tier": 3, "seat_capacity": 3 + 24,
            "payload": "2 Titans (standing) or up to 4 Exoframes on the cargo deck; 24 jump seats", "hull_rgb": (108, 116, 122), "belly_rgb": (76, 82, 88),
            "seats": {"pilot": [12, 46, -296], "copilot": [-12, 46, -296], "loadmaster": [0, 40, -200], "titan_slot_a": [0, 40, -60], "titan_slot_b": [0, 40, 100]},
            "decks": {"flight_deck": [[-24, 40, -328], [24, 40, -252]], "crew_rest": [[-32, 40, -248], [32, 40, -192]], "cargo_deck": [[-40, 40, -188], [40, 40, 270]],
                      "ramp_open": [[-40, -2, 273], [40, 40, 330]]},
            "interior": ["flight deck (-328..-252): 2 pilot seats, consoles, windscreen; crew rest (-248..-190): bunks + head; door to the cargo bay at z=-190",
                         "cargo bay (-188..270): 24 jump seats along the walls, 2 roller tracks, tie-down ring grid; clear height ~76 px; rear ramp is the entrance (open -135 deg: slope from y=40 at z=270 to ground at ~z=313)"],
            "extra": ["Wings are decoration (you cannot stand on them without a collider); T-tail fin reaches y~275. Engines are static (no fan animation)."],
            "swings": [("ramp", [0, 40, 270], [0, 100, 270], [-135, 0, 0], 2, 1, 30)],
            "scale": 0.5, "bounds_w": 52, "bounds_h": 28, "bounds_off": [0, 10, 0], "view": (35, -20)}
    return bones, meta


def airlifter_anims():
    w = {f"wheel_m{sn}{k}": 0 for sn in "lr" for k in range(3)}; w["wheel_nose"] = 0
    return anim_file("c17_airlifter", {"idle": {"loop": True, "bones": {"cargo_ramp": {"rotation": [0, 0, 0]}}},
                                       "taxi": {"loop": True, "animation_length": 0.4, "bones": {**spin(w, 0.4), "cargo_ramp": {"rotation": [0, 0, 0]}}},
                                       "ramp_open": {"loop": True, "bones": {"cargo_ramp": {"rotation": [-135, 0, 0]}}}})
