"""Mi-26 Halo (Tier 3 strategic lift) and 6x6 recovery truck. Both are built on the existing Mi-17 / hauler geometry."""
import math
from fleet_common import *
import fleet_mi17 as M
import fleet_ground as G

K = 1.5


def scale_bones(bones, k):
    f = lambda v: [round(x * k, 3) for x in v]
    for b in bones:
        b["pivot"] = f(b["pivot"])
        if "locators" in b: b["locators"] = {n: f(p) for n, p in b["locators"].items()}
        for c in b.get("cubes", []):
            c["origin"], c["size"] = f(c["origin"]), f(c["size"])
            if "pivot" in c: c["pivot"] = f(c["pivot"])
    return bones


# ============================================================ Mi-26 Halo
def mi26():
    src, _ = M.mi17()
    drop = ("main_blade_", "sling_")
    bones = scale_bones([b for b in src if not b["name"].startswith(drop)], K)
    by = {b["name"]: b for b in bones}
    hub = by["main_rotor"]["pivot"]
    # 8-blade main rotor, resting droop (levelled by the `fly` clips)
    R_IN, R_MID, R_TIP = 14, 100, 214; y0 = hub[1]
    for i in range(8):
        arm = f"main_blade_{i + 1}"
        bones += [bone(arm, "main_rotor", hub, [box(7, y0 - 2.4, hub[2] - 9, 14, y0 + 2.6, hub[2] + 5, DARK)], rotation=[0, 45 * i, 0]),
                  bone(arm + "_droop", arm, hub, [box(R_IN, y0 - 1.6, hub[2] - 9.5, R_MID, y0 + 0.4, hub[2] + 5.5, BLADE)], rotation=[0, 0, M.DROOP]),
                  bone(arm + "_tip", arm + "_droop", [R_MID, y0, hub[2]],
                       [box(R_MID, y0 - 1.6, hub[2] - 9.5, R_TIP - 12, y0 + 0.4, hub[2] + 5.5, BLADE), box(R_TIP - 12, y0 - 1.6, hub[2] - 9.5, R_TIP, y0 + 0.4, hub[2] + 5.5, TIP)],
                       rotation=[0, 0, M.TIP_DROOP + 2])]
    # 5-blade tail rotor
    th = by["tail_rotor"]["pivot"]
    for k in range(5):
        c = cbox(th[0] + 2.2, th[1] + 22, th[2], 1.4, 38, 7, BLADE); c["pivot"], c["rotation"] = list(th), [72 * k, 0, 0]
        by["tail_rotor"]["cubes"].append(c)
    # heavy sling: three Titan hard-points along a long spreader bar
    S = (-84, 0, 84); belly = 42
    frame = [box(s * 10, belly - 11, -112, s * 17, belly, 112, DARK) for s in (-1, 1)] + [box(-17, belly - 11, z - 3.5, 17, belly - 4, z + 3.5, DARK) for z in (-105, -84, -42, 0, 42, 84, 105)]
    frame += [box(-6, belly - 20, -6 + z, 6, belly - 11, 6 + z, DARK) for z in S] + [box(-2, belly - 32, z - 2, 2, belly - 20, z + 2, SPIN) for z in S]
    cables = [tube((s * 13, belly - 8, z), (s * 4.5, -38, z), 2.4, SPIN) for s in (-1, 1) for z in (-105, -63, -21, 21, 63, 105)]
    bar = [box(-7, -46, -116, 7, -38, 116, DARK), box(-3, -38.4, -112, 3, -35.6, 112, SPIN)]
    for z in S:
        for dz in (-15, 15):
            zz = z + dz
            bar += [box(-10, -55, zz - 6.5, 10, -46, zz + 6.5, DARK), box(-9, -57, zz - 5.5, 9, -55, zz + 5.5, SOOT),
                    box(-10.6, -53, zz - 7, -9, -45, zz - 5.4, RED), box(9, -53, zz + 5.4, 10.6, -45, zz + 7, RED)]
            bar += [rbox(s * 11, -51, zz, 2, 12, 8, [0, 0, s * 8], SPIN) for s in (-1, 1)] + [tube((s * 4.5, -46, zz), (s * 9.6, -52, zz), 2.2, SPIN) for s in (-1, 1)]
    bones += [bone("sling_hook", "fuselage", [0, belly - 4, 0], frame), bone("sling_cables", "fuselage", [0, belly - 6, 0], cables),
              bone("sling_rig_clamp", "fuselage", [0, -38, 0], bar)]
    loc = by["fuselage"]["locators"]
    for n in [n for n in loc if n.startswith(("sling", "titan_hang", "exo_hang"))]: del loc[n]
    loc.update({f"titan_hang_{t}": [0, -118, z] for t, z in zip("abc", S)})
    loc["sling_attach"] = [0, -46, 0]
    loc["flight_engineer"] = [-14, 60, -96]
    for sn, s in (("l", 1), ("r", -1)):                       # 8 extra troop seats along the longer hold
        for i, z in enumerate((-90, -64, 40, 66, 92, 118)): loc[f"troop_{sn}x{i}"] = [s * 24, 58, z]
    meta = {"id": "mi26_halo", "name": "Mil Mi-26 Halo Strategic Heavy-Lift", "tier": 3,
            "payload": "up to 3 Titans (or 2 Titans + 2 Exoframes) on the ventral spreader bar; hold fits 12 troops",
            "hull_rgb": (112, 120, 88), "belly_rgb": (74, 78, 60), "seat_capacity": 4 + 12 + 12,
            "decks": {"cabin_deck": [[-27, 51, -56], [27, 51, 95]], "flight_deck": [[-20, 51, -144], [20, 51, -56]],
                      "sling_hang_zone": [[-40, -150, -130], [40, -50, 130]]},
            "seats": {"pilot": [12, 60, -105], "copilot": [-12, 60, -105], "flight_engineer": [-14, 60, -96],
                      "titan_hang_a": [0, -118, -84], "titan_hang_b": [0, -118, 0], "titan_hang_c": [0, -118, 84]},
            "extra": ["Everything is the Mi-17 geometry x1.5, then: 8-blade rotor, 5-blade tail rotor, 3-slot heavy sling. Rig hidden (scale 0) in every clip except `sling`.",
                      "Belly is at y=42 px; the hover height of the Java entity decides how far the slung Titans clear the ground."],
            "swings": [("door_l", scale3([19.5, 56, 64]), scale3([0.8, 56, 66]), [0, M.DOOR_OPEN, 0], 2, 1, 10)],
            "scale": 0.5, "bounds_w": 30, "bounds_h": 16, "bounds_off": [0, 4, 0], "view": (35, -22)}
    return bones, meta


def scale3(v): return [x * K for x in v]


def mi26_anims():
    flat, gone = {}, {b: {"scale": [0, 0, 0]} for b in ("sling_hook", "sling_cables", "sling_rig_clamp")}
    for i in range(1, 9):
        flat[f"main_blade_{i}_droop"] = {"rotation": [0, 0, -M.DROOP]}; flat[f"main_blade_{i}_tip"] = {"rotation": [0, 0, -(M.TIP_DROOP + 2)]}
    shown = {b: {"scale": [1, 1, 1]} for b in gone}
    shut = {"clamshell_door_left": {"rotation": [0, 0, 0]}, "clamshell_door_right": {"rotation": [0, 0, 0]}}
    rotors = spin({"main_rotor": 1, "tail_rotor": 0}, 0.4); rotors["tail_rotor"]["rotation"]["0.4"] = [720, 0, 0]
    return anim_file("mi26_halo", {
        "idle": {"loop": True, "bones": {**gone, **shut}},
        "fly": {"loop": True, "animation_length": 0.4, "bones": {**rotors, **flat, **gone, **shut}},
        "sling": {"loop": True, "animation_length": 0.4, "bones": {**rotors, **flat, **shut, **shown}},
        "cargo_open": {"loop": True, "bones": {**gone, "clamshell_door_left": {"rotation": [0, M.DOOR_OPEN, 0]}, "clamshell_door_right": {"rotation": [0, -M.DOOR_OPEN, 0]}}}})


# ============================================================ 6x6 recovery truck
def recovery():
    src, _ = G.hauler()
    keep = [b for b in src if b["name"] not in ("cargo_deck", "drop_side_l", "drop_side_r", "tailgate", "rear_ladder", "cargo_straps")]
    body = next(b for b in keep if b["name"] == "body")
    body["locators"] = {"seat_driver": [-10, 47, -25], "seat_passenger": [10, 47, -25], "seat_centre": [0, 47, -25], "winch_hook": [0, 22, -80]}
    c = body["cubes"]; A = c.append
    # cab-roof light bar, front winch, tool lockers on a short subframe deck
    A(box(-16, 80.4, -34, 16, 83, -26, DARK))
    for i in range(8): A(box(-15 + i * 3.9, 83, -33, -12 + i * 3.9, 85, -27, RED if i % 2 else WHITE))
    A(box(-20, 28, -81, 20, 33, -75, DARK)); A(box(-12, 24, -80, 12, 31, -76, SPIN))
    A(box(-16, 22, -74, 16, 23.6, -70, SPIN))                                              # roller fairlead
    c += [tube((s * 10, 30, -81), (s * 14, 22, -84), 2.2, DARK) for s in (-1, 1)] + [box(s * 11, 18, -88, s * 14, 22, -84, RED) for s in (-1, 1)]
    c += [box(-22, 24, -8, 22, 30, 70, DARK), box(-19, 30, -8, 19, 31.5, 70, WALK)]
    for s in (-1, 1):
        for z0 in (0, 22, 44):
            c += [wall(s, 19, 22.4, 31.5, 54, z0, z0 + 20, HULL), box(s * 22.4, 33, z0 + 1.5, s * 22.9, 52, z0 + 18.5, DOOR), box(s * 22.9, 42, z0 + 15, s * 23.6, 46, z0 + 17.5, DARK)]
        c += [box(s * 19, 54, 0, s * 22.4, 55, 64, DARK), tube((s * 18, 31.5, 70), (s * 18, 64, 70), 2, DARK)]
    c += [box(-5, 24, 70, 5, 31, 78, DARK), box(-3, 26, 78, 3, 30, 80, SPIN)]              # tow pintle
    c += [box(-14, 31.5, 22, 14, 56, 50, DARK)]                                           # crane pedestal under the turntable
    # rotating crane: turntable, cab, lattice boom, hook
    pv = (0, 58, 34)
    base = [box(-14, 56, 20, 14, 58, 52, DARK), box(-11, 58, 24, 11, 74, 48, HULL), box(-9, 60, 21, 9, 71, 24, GLASS), box(-12, 74, 24, 12, 76, 50, DARK),
            box(-8, 62, 46, 8, 80, 52, DARK)]                                                    # counterweight block
    ang = math.radians(40); d = (0, math.sin(ang), math.cos(ang)); u = (0, math.cos(ang), -math.sin(ang)); L = 96
    base_pt = (0, 68, 44); boom = []
    secs = []
    for i in range(9):
        t = i / 8; cc = tuple(base_pt[k] + L * t * d[k] for k in range(3)); h = 5 - 2.6 * t
        secs.append([tuple(cc[k] + (sx * h if k == 0 else 0) + sy * h * u[k] for k in range(3)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    boom += [tube(secs[0][i], secs[-1][i], 1.8, HULL) for i in range(4)]
    for i, s4 in enumerate(secs):
        boom += [tube(s4[j], s4[(j + 1) % 4], 1.0, DARK) for j in range(4)]
        if i < 8: boom += [tube(s4[j], secs[i + 1][(j + 1) % 4], 0.9, DARK) for j in range(4)]
    tip = tuple(base_pt[k] + L * d[k] for k in range(3))
    boom += [box(-3, tip[1] - 2, tip[2] - 2, 3, tip[1] + 3, tip[2] + 3, DARK)]
    hook = [tube((0, tip[1] - 2, tip[2] + 1), (0, tip[1] - 38, tip[2] + 1), 1.2, SPIN), box(-4, tip[1] - 46, tip[2] - 2.5, 4, tip[1] - 38, tip[2] + 4.5, DARK),
            box(-1.2, tip[1] - 54, tip[2] - 0.5, 1.2, tip[1] - 46, tip[2] + 2.5, SPIN), box(-3, tip[1] - 57, tip[2] - 0.5, 3, tip[1] - 54, tip[2] + 2.5, RED)]
    rot_lamp = [box(-2.5, 83, -2 - 30 + 0, 2.5, 87, 3 - 30, DARK), box(-1.5, 87, -29, 1.5, 90, -26, RED), box(-4, 85, -30, 4, 86, -26, WHITE)]
    bones = [b for b in keep] + [
        bone("crane_base", "body", pv, base), bone("crane_boom", "crane_base", base_pt, boom), bone("crane_hook", "crane_boom", tip, hook),
        bone("beacon", "body", [0, 87, -28], rot_lamp)]
    for s, sn in ((1, "l"), (-1, "r")):                                                         # outriggers: beam extends, jack drops
        bones += [bone("outrigger_" + sn, "body", [s * 14, 26, 50], [box(s * 12, 20, 46, s * 24, 26, 54, DARK)]),
                  bone("outrigger_jack_" + sn, "outrigger_" + sn, [s * 24, 26, 50], [box(s * 22, 14, 48, s * 25.6, 26, 52, SPIN), box(s * 20.5, 11, 46.5, s * 27, 14, 53.5, DARK)])]
    meta = {"id": "recovery_6x6", "name": "Heavy 6x6 Recovery Truck", "tier": 2,
            "payload": "recovers downed Titans/vehicles with a 40-degree lattice crane + front winch; carries no deck cargo",
            "hull_rgb": (200, 124, 40), "belly_rgb": (112, 80, 40), "seat_capacity": 3,
            "decks": {"subframe_deck": [[-19, 31.5, -8], [19, 31.5, 70]]},
            "seats": {"driver": [-10, 47, -25], "passenger": [10, 47, -25], "centre": [0, 47, -25], "winch_hook": [0, 22, -80],
                      "crane_tip_rest": [round(tip[0], 1), round(tip[1], 1), round(tip[2], 1)]},
            "extra": ["`outriggers_down` slides the beams out 14 px and drops the jacks 12 px; `crane_work` luffs the boom 20 deg and slews the turntable 30 deg."],
            "scale": 3.0, "bounds_w": 9, "bounds_h": 9, "bounds_off": [0, 2, 0], "view": (35, -18)}
    return bones, meta


def recovery_anims():
    wheels = {f"wheel_{n}": 0 for n in ("fl", "fr", "ml", "mr", "rl", "rr")}
    out = {"outrigger_l": {"position": [14, 0, 0]}, "outrigger_r": {"position": [-14, 0, 0]},
           "outrigger_jack_l": {"position": [0, -12, 0]}, "outrigger_jack_r": {"position": [0, -12, 0]}}
    return anim_file("recovery_6x6", {
        "idle": {"loop": True, "bones": {}},
        "drive": {"loop": True, "animation_length": 0.4, "bones": spin(wheels, 0.4)},
        "beacon": {"loop": True, "animation_length": 1.0, "bones": spin({"beacon": 1}, 1.0)},
        "outriggers_down": {"loop": True, "bones": out},
        "crane_work": {"loop": True, "animation_length": 6.0, "bones": {
            **out, "crane_boom": {"rotation": {"0.0": [0, 0, 0], "3.0": [-20, 0, 0], "6.0": [0, 0, 0]}},
            "crane_base": {"rotation": {"0.0": [0, 0, 0], "3.0": [0, 30, 0], "6.0": [0, 0, 0]}}}}})
