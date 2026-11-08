"""US-style set (also fielded by Thailand): M1165 up-armoured Humvee with ring-mount .50 and UH-60 Black Hawk."""
import math
from fleet_common import *
import fleet_mi17 as M
from fleet_heavy import scale_bones

THAI = ((58, 74, 46), (40, 50, 34))          # Royal Thai Army dark olive
DESERT = ((178, 152, 108), (120, 100, 70))


# ============================================================ M1165 Humvee, Tier 1
def humvee():
    WX, W, R, FZ, RZ = 17, 7, 8, -27, 27
    body, deck, gate, turret = [], [], [], []
    A, X = body.append, body.extend
    for s in (-1, 1):
        A(box(s * 7, 12, -42, s * 11, 16, 44, DARK))                                           # frame
        for z in (FZ, RZ):
            A(box(s * 10, 6, z - 3, s * 15, 13, z + 3, DARK)); A(box(s * 14.5, 5, z - 2.5, s * 17.2, 12, z + 2.5, SPIN))   # portal hubs
            X([tube((s * 9, 9, z - 2), (s * 9.5, 18, z - 2), 1.6, SPIN)])
            A(box(s * 13.5, 18.2, z - 11, s * 20.5, 20.2, z + 11, HULL))                       # fender flare
        A(rbox(s * 15.6, 33.2, -33, 3, 2, 22, [0, 0, s * 35], HULL))
        A(box(s * 12, 20, -44, s * 17.5, 28, -22, HULL))
        A(box(s * 9, 24.5, -45.2, s * 13.2, 28.5, -44, WHITE)); A(box(s * 14, 22.5, -45.2, s * 16.6, 24.8, -44, RED))   # lamp, indicator
    A(box(-17.5, 14, -42, 17.5, 20, 44, BELLY)); A(box(-12, 28, -44, 12, 30, -22, HULL))
    A(rbox(0, 30.2, -34, 24, 1.4, 20, [-6, 0, 0], HULL))                                       # hood crown
    A(box(-12, 22, -45, 12, 28, -44, HULL, north=GRILLE)); A(box(-17.5, 16, -48, 17.5, 21, -44, DARK))
    A(box(-6, 17, -50, 6, 21, -48, SPIN)); A(box(-4, 17.4, -51.4, 4, 19.6, -50, SPIN))         # winch + fairlead
    for s in (-1, 1): A(box(s * 9, 14, -52, s * 11.4, 17, -48, RED))
    # armoured cab
    cz0, cz1 = -22, 16
    A(box(-17.5, 20, cz0, 17.5, 21.5, cz1, DARK))
    for s in (-1, 1):
        A(wall(s, 16.2, 17.8, 21.5, 33, cz0, cz1, HULL))
        A(box(s * 17.8, 22, cz0 + 1, s * 18.8, 32, cz1 - 1, DARK))                              # bolt-on armour appliqué
        for z in (-8, 2): A(box(s * 17.8, 22, z - 0.4, s * 19, 33, z + 0.4, DARK))              # door seams
        A(box(s * 18.8, 28, -17, s * 19.4, 30, -14, SPIN)); A(box(s * 18.8, 28, -4, s * 19.4, 30, -1, SPIN))   # handles
        A(box(s * 17.2, 33, cz0 + 1, s * 17.8, 41, -9, GLASS)); A(box(s * 17.2, 33, -7, s * 17.8, 41, 1.6, GLASS)); A(box(s * 17.2, 33, 3.6, s * 17.8, 41, cz1 - 1, GLASS))
        X([tube((s * 17.2, 33, z), (s * 17.2, 43, z), 1.8, HULL) for z in (cz0, -8, 2.5, cz1)])
        A(box(s * 20.4, 34, -24, s * 22.6, 40, -21.8, DARK)); A(box(s * 17.6, 36, -24, s * 20.4, 37, -23, DARK))   # mirrors
    A(box(-16.5, 42.4, cz0, 16.5, 44, cz1, HULL)); A(box(-17.5, 41, cz0, 17.5, 42.4, cz1, DARK))
    A(rbox(0, 37.5, cz0 - 0.3, 33, 9.4, 0.9, [-14, 0, 0], GLASS)); A(rbox(0, 37.5, cz0 - 0.3, 1.4, 9.8, 1.4, [-14, 0, 0], HULL))
    A(box(-16, 33, cz1 - 0.6, 16, 41, cz1 + 0.4, GLASS)); A(box(-17.5, 21.5, cz1, 17.5, 33, cz1 + 2, HULL))
    A(box(-9, 44, -8, 9, 46, 4, DARK)); A(box(-8, 44, -7, 8, 44.6, 3, HULL))
    A(box(-15, 21.5, -20, 15, 22.5, 15, INTER, up=WALK))
    for z, x in ((-12, -7), (-12, 7), (6, -7), (6, 7)):
        A(box(x - 4, 22.5, z - 4, x + 4, 26.4, z + 4, INTER)); A(rbox(x, 33, z + (4 if z < 0 else 5.4), 8, 13, 2.2, [-8, 0, 0], INTER))
    A(box(-15, 29, -21.4, 15, 33, -17, INTER)); A(rbox(-7, 31.5, -15.5, 6.4, 0.9, 6.4, [-60, 0, 0], DARK)); A(box(-2.4, 22.5, -14, 2.4, 29, 4, DARK))
    for s in (-1, 1): X([tube((s * 14.5, 44, 12), (s * 14.5 + s * 2, 64, 17), 0.9, DARK)])     # whip antennas
    A(box(-3, 44, 13, 3, 47, 17, DARK))
    # ring mount: turntable + gun shield + .50 cal
    turret += [box(-8, 46, -8, 8, 47.5, 6, DARK), box(-6.5, 47.5, -6.5, 6.5, 49, 4.5, SPIN)]
    turret += [box(-9, 47.5, -9, 9, 62, -7.4, HULL), rbox(0, 61.4, -9.5, 18, 1.4, 4, [-22, 0, 0], HULL), box(-9.8, 47.5, -9.8, -9, 62, -6.6, DARK), box(9, 47.5, -9.8, 9.8, 62, -6.6, DARK)]
    turret += [box(-3, 51, -12, 3, 58, -8, DARK), box(-5, 51.4, -9.4, 5, 57.6, -7.6, DARK, north=SPIN)]
    turret += [box(-2.2, 52.6, -22, 2.2, 56.2, -12, DARK), tube((0, 54.4, -10), (0, 54.4, -42), 1.8, SPIN), box(-1.8, 53.5, -46, 1.8, 55.4, -42, SOOT),
               box(-4, 55, -26, 4, 56.6, -22, DARK), box(-3, 50, -14, 3, 52, -6, DARK)]
    turret += [box(-3, 49, -6, 3, 59, -3, DARK)]
    # bed
    deck += [box(-14, 20, 16, 14, 23, 44, DARK), box(-14, 23, 17, 14, 24, 43, PLATE)]
    for s in (-1, 1):
        deck += [wall(s, 14, 17.5, 21, 32, 16, 44, HULL), tube((s * 15.8, 32.6, 16), (s * 15.8, 32.6, 44), 1.8, DARK)] + dring(s * 12, 24, 24) + dring(s * 12, 24, 38)
        deck += [box(s * 16.2, 32, 18, s * 18.2, 40, 24, DARK), box(s * 17, 34, 25, s * 18.4, 38, 27, SPIN)]       # jerry can racks
    deck.append(box(-14, 24, 16, 14, 33, 17.2, DARK))
    gate += [box(-14, 24, 43.4, 14, 36, 45, HULL, north=PLATE), box(-14.3, 24, 43, -12.7, 36, 45.3, DARK), box(12.7, 24, 43, 14.3, 36, 45.3, DARK),
             box(-3, 31, 45, 3, 34, 45.8, SPIN)]
    X([box(s * 13, 20, 45, s * 17, 27, 47, DARK) for s in (-1, 1)])
    for s in (-1, 1): A(box(s * 12.6, 26, 45, s * 16.4, 31, 45.8, RED))
    bones = [bone("root", None, [0, 0, 0], []),
             bone("body", "root", [0, 0, 0], body, locators={"seat_driver": [-7, 29, -12], "seat_passenger": [7, 29, -12], "seat_rear_l": [7, 29, 6], "seat_rear_r": [-7, 29, 6],
                                                              "gunner_stand": [0, 22.5, -2], "mount_roof": [0, 49, -2], "exo_slot_centre": [0, 24, 30]}),
             bone("turret", "body", [0, 47, -2], turret), bone("cargo_deck", "body", [0, 24, 30], deck), bone("tailgate", "cargo_deck", [0, 24, 44.2], gate)]
    for n, x, z, st in (("fl", WX, FZ, 1), ("fr", -WX, FZ, 1), ("rl", WX, RZ, 0), ("rr", -WX, RZ, 0)):
        p = [x, R, z]
        if st:
            bones += [bone("steer_" + n, "body", p, []), bone("wheel_" + n, "steer_" + n, p, wheel12(x, R, z, W, R))]
        else:
            bones.append(bone("wheel_" + n, "body", p, wheel12(x, R, z, W, R)))
    meta = {"id": "humvee_m1165", "name": "M1165 Up-Armoured Humvee", "tier": 1, "seat_capacity": 5, "payload": "1 Obsolete Exoframe (short bed)",
            "hull_rgb": (84, 92, 62), "belly_rgb": (56, 60, 42), "variants": {"thai": THAI, "desert": DESERT},
            "decks": {"cargo_deck": [[-14, 24, 17], [14, 24, 43]], "tailgate_open": [[-14, 24, 45], [14, 24, 57]]},
            "seats": {"driver": [-7, 29, -12], "passenger": [7, 29, -12], "rear_left": [7, 29, 6], "rear_right": [-7, 29, 6], "gunner_stand": [0, 22.5, -2]},
            "extra": ["`turret` bone (ring-mount .50 cal with gun shield) rotates about Y at [0, 47, -2]; aim it from Java."],
            "swings": [("tailgate", [0, 24, 44.2], [0, 36, 44.2], [-90, 0, 0], 2, 1, 8)], "scale": 4.0, "bounds_w": 5, "bounds_h": 5, "view": (35, -18)}
    return bones, meta


def humvee_anims():
    w = {f"wheel_{n}": 0 for n in ("fl", "fr", "rl", "rr")}
    return anim_file("humvee_m1165", {
        "idle": {"loop": True, "bones": {"tailgate": {"rotation": [0, 0, 0]}}},
        "drive": {"loop": True, "animation_length": 0.4, "bones": {**spin(w, 0.4), "tailgate": {"rotation": [0, 0, 0]}}},
        "tailgate_open": {"loop": True, "bones": {"tailgate": {"rotation": [-90, 0, 0]}}}})


# ============================================================ UH-60 Black Hawk, Tier 1 aerial
KB = 0.8


def blackhawk():
    src, _ = M.mi17()
    bones = scale_bones([b for b in src if not b["name"].startswith(("main_blade_", "pylon_"))], KB)
    by = {b["name"]: b for b in bones}
    hub = by["main_rotor"]["pivot"]; y0 = hub[1]
    for i in range(4):                                                                      # 4-blade rotor, R = 131 px
        arm = f"main_blade_{i + 1}"
        bones += [bone(arm, "main_rotor", hub, [box(4, y0 - 2, hub[2] - 5.5, 8, y0 + 2, hub[2] + 3, DARK)], rotation=[0, 90 * i, 0]),
                  bone(arm + "_droop", arm, hub, [box(8, y0 - 1.4, hub[2] - 5.4, 58, y0 + 0.2, hub[2] + 3.4, BLADE)], rotation=[0, 0, M.DROOP]),
                  bone(arm + "_tip", arm + "_droop", [58, y0, hub[2]], [box(58, y0 - 1.4, hub[2] - 5.4, 121, y0 + 0.2, hub[2] + 3.4, BLADE), box(121, y0 - 1.4, hub[2] - 5.4, 131, y0 + 0.2, hub[2] + 3.4, TIP)],
                       rotation=[0, 0, M.TIP_DROOP])]
    th = by["tail_rotor"]["pivot"]; by["tail_rotor"]["cubes"] = by["tail_rotor"]["cubes"][:1]
    by["fuselage"]["cubes"].append(box(1.6, th[1] - 5, th[2] - 5, 5.6, th[1] + 5, th[2] + 5, DARK))
    for k in range(4):
        c = cbox(th[0] + 1.4, th[1] + 12.5, th[2], 1.0, 21, 4, BLADE); c["pivot"], c["rotation"] = list(th), [90 * k, 0, 0]; by["tail_rotor"]["cubes"].append(c)
    fus = by["fuselage"]
    fus["cubes"] += [tube((0, 46, 146), (0, 9, 158), 2.6, DARK), box(-2, 40, 144, 2, 46, 150, DARK)]                    # tail-wheel strut
    for s in (-1, 1):
        fus["cubes"] += [box(s * 20, 48, 20, s * 52, 50, 42, HULL), tube((s * 18, 58, 24), (s * 36, 49, 30), 2.2, DARK)]       # ESSS stub wings
        fus["cubes"] += [box(s * 40 - 5, 38, 16, s * 40 + 5, 48, 52, HULL), box(s * 40 - 3, 40, 52, s * 40 + 3, 46, 58, HULL), box(s * 40 - 3, 41, 12, s * 40 + 3, 45, 16, DARK)]   # fuel tank
        fus["cubes"] += [box(s * 50 - 1.4, 40, 20, s * 50 + 1.4, 48, 44, DARK), box(s * 50 - 2.4, 44, 22, s * 50 + 2.4, 46, 42, HULL), box(s * 49, 47, 36, s * 51, 49, 38, RED if s > 0 else GREEN)]
    loc = fus["locators"]
    for n in [n for n in loc if n.startswith("troop_")][8:]: del loc[n]
    meta = {"id": "uh60_blackhawk", "name": "UH-60 Black Hawk Utility Helicopter", "tier": 1, "seat_capacity": 2 + 8,
            "payload": "1 Obsolete Exoframe on the ventral hook (Titan is too heavy); cabin seats 8 troops",
            "hull_rgb": (74, 82, 62), "belly_rgb": (50, 56, 42), "variants": {"thai": THAI, "desert": DESERT},
            "decks": {"cabin_deck": [[-14, 27, -30], [14, 27, 50]]}, "seats": {"pilot": [6, 32, -56], "copilot": [-6, 32, -56], "exo_hang": [0, -60, 0]},
            "extra": ["Derived from the Mi-17 geometry x0.8: 4-blade rotor, 4-blade tail rotor, tail-wheel gear, ESSS stub wings with tanks. Rear doors never open (no `cargo_open` clip).",
                      "Sling rig is hidden (scale 0) in `idle`/`fly`; play `sling` while an Exoframe is hooked."],
            "scale": 0.75, "bounds_w": 18, "bounds_h": 11, "bounds_off": [0, 3, 0], "view": (35, -22)}
    return bones, meta


def blackhawk_anims():
    gone = {b: {"scale": [0, 0, 0]} for b in ("sling_hook", "sling_cables", "sling_rig_clamp")}
    shown = {b: {"scale": [1, 1, 1]} for b in gone}
    flat = {}
    for i in range(1, 5):
        flat[f"main_blade_{i}_droop"] = {"rotation": [0, 0, -M.DROOP]}; flat[f"main_blade_{i}_tip"] = {"rotation": [0, 0, -M.TIP_DROOP]}
    rot = spin({"main_rotor": 1, "tail_rotor": 0}, 0.3); rot["tail_rotor"]["rotation"]["0.3"] = [720, 0, 0]
    return anim_file("uh60_blackhawk", {
        "idle": {"loop": True, "bones": gone},
        "fly": {"loop": True, "animation_length": 0.3, "bones": {**rot, **flat, **gone}},
        "sling": {"loop": True, "animation_length": 0.3, "bones": {**rot, **flat, **shown}}})
