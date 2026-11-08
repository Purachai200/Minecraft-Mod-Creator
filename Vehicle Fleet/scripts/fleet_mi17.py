"""Mil Mi-17 "Hip" (Tier 2 aerial) with ventral Titan / Exoframe sling rig."""
import math
from fleet_common import *

FL, HW, TOP, YB = 34, 21, 78, 28        # cabin floor top, half width, crown, belly
HUB = (0, 108, -2)                       # main rotor hub
TAIL_HUB = (4.8, 100, 191)
DOOR_OPEN = 110                          # +ry opens the left leaf, -ry the right (geo frame, see rot2)
DROOP, TIP_DROOP = 3, 5                  # blade droop at rest (deg); animation levels them out
SLING_UP = 46                            # stowed lift of the spreader bar


def lerp(a, b, t): return a + (b - a) * t


def mi17():
    fus, deck, cap = [], [], []
    A, X = fus.append, fus.extend

    # ---------------- nose: ellipsoid chin, then multi-pane greenhouse cockpit
    for i in range(6):
        z0 = -114 + 2.4 * i; f = math.sqrt(1 - (1 - (i + 1) / 6) ** 2)
        X(H.solid(z0, z0 + 2.4, 2.5 + 13 * f, 40 - 12 * f, 49, c=2))
    for i in range(5):                                           # cockpit slices z -100..-40
        z0 = -100 + 12 * i; z1 = z0 + 12; hw = 15.4 + (HW - 15.4) * (i + 1) / 5; yt = 71 + 5 * (i + 1) / 5
        A(box(-hw, YB, z0, hw, FL, z1, BELLY, up=INTER))
        A(box(-hw + 3, yt - 2, z0, hw - 3, yt, z1, HULL, down=INTER))
        for s in (-1, 1):
            A(wall(s, hw - 2, hw, FL, 48, z0, z1, HULL))
            A(box(s * (hw - 0.9), 48, z0, s * hw, yt - 2, z1, GLASS))
            A(box(s * (hw - 2), 48, z1 - 1.2, s * (hw + 0.3), yt, z1, HULL))                     # window post
            A(rbox(s * (hw - 3.2), yt - 2.6, (z0 + z1) / 2, 5.5, 1.8, 12, [0, 0, s * 38], HULL))   # chamfered roof edge
    for s in (-1, 1):
        A(rbox(s * 11.5, 61, -101, 10, 25, 0.9, [-12, -s * 35, 0], GLASS))                      # wrap windscreen panes
        A(rbox(s * 15.8, 56, -91, 0.9, 20, 14, [0, 0, 0], GLASS))                               # side blister glass
        A(rbox(s * 6.6, 61, -103.4, 1.4, 26, 1.4, [-12, 0, 0], HULL))                           # windscreen posts
        # lower chin windows: look straight down at the landing site
        A(rbox(s * 6.5, 40.5, -100.5, 11, 0.9, 14, [-48, 0, 0], GLASS)); A(rbox(s * 12.6, 40, -95, 0.9, 11, 13, [0, 0, 0], GLASS))
        A(rbox(s * 4, 41, -102.5, 1.2, 15, 1.2, [-48, 0, 0], HULL))
    A(rbox(0, 61, -103.2, 14, 26, 0.9, [-12, 0, 0], GLASS)); A(rbox(0, 74.4, -100, 28, 1.6, 12, [-12, 0, 0], HULL))
    A(rbox(0, 40.8, -103.5, 12, 0.9, 16, [-48, 0, 0], GLASS))
    X([tube((8, 44, -110), (8.6, 43.5, -126), 1.0, SPIN)])                                      # pitot
    # cockpit furniture
    A(box(-14, 44, -97, 14, 54, -91, INTER)); A(box(-14, 54, -95, 14, 55.4, -91, DARK))          # instrument panel / glareshield
    A(box(-3, 34, -88, 3, 44, -66, INTER)); A(box(-12, 74, -90, 12, 76, -58, INTER))             # pedestal, overhead panel
    for s in (-1, 1):
        A(box(s * 8 - 5, 34, -76, s * 8 + 5, 40, -64, INTER)); A(rbox(s * 8, 52, -63, 10, 22, 2.6, [-8, 0, 0], INTER))
        X([tube((s * 8, 34, -86), (s * 8, 50, -86.6), 1.5, DARK)]); A(box(s * 14, 34, -70, s * 17, 44, -64, INTER))
        A(box(s * 8 - 2.6, 56, -64.4, s * 8 + 2.6, 62, -62, INTER))
    # ---------------- cabin: hollow ellipsoidal cross-section
    zs = [-40 + 104 / 6 * i for i in range(7)]
    for z0, z1 in zip(zs, zs[1:]): X(H.shell(z0, z1, HW, YB, TOP, w=4, floor=True, inner=INTER, roof=True))
    for s in (-1, 1):
        for zc in (-22, -6, 10, 26, 42):                                                          # framed cabin windows
            A(box(s * 20.7, 49, zc - 6, s * 21.7, 67, zc + 6, DARK)); A(box(s * 20.8, 50.2, zc - 4.8, s * 21.9, 65.8, zc + 4.8, GLASS))
            A(box(s * 21.7, 57.6, zc - 6, s * 22.0, 58.6, zc + 6, DARK))
        A(box(s * 21, 36, -34, s * 21.5, 72, -12, DOOR) if s < 0 else box(s * 21, 36, -34, s * 21.5, 72, -16, DOOR))   # sliding door / crew door
        A(box(s * 21.5, 52, -32, s * 22.2, 56, -28, DARK))
        A(box(s * 21.5, 33, -36, s * 23.5, 35, 58, DARK))                                         # sill step / grab rail
    # windows in the sliding door
    A(box(-21.6, 52, -30, -22, 66, -16, GLASS))
    for s in (-1, 1):                                                                             # troop benches + fold-up seat backs
        for za, zb in ((-30, -4), (2, 28), (34, 58)):
            A(box(s * 13.5, 34, za, s * 19, 38.6, zb, INTER)); A(box(s * 17.6, 38.6, za, s * 19, 52, zb, INTER))
        X([tube((s * 10, 74, -34), (s * 10, 74, 62), 1.6, DARK)])                                 # overhead cargo / static line rail
    # ---------------- cargo deck (walkable; top face = non-skid)
    deck += [box(-18, 30, -37, 18, 34, 63, DARK, up=WALK)]
    for x in (-10, 0, 10):
        for z in (-20, 0, 20, 40, 58): deck += dring(x, 34, z)
    # ---------------- clamshell doors, fixed header and tail cone
    A(box(-20, 72, 64, 20, 77, 86, HULL)); A(box(-17, 71, 64, 17, 72, 86, INTER))
    X(H.solid(64, 86, 20, 74, TOP))
    for z0, z1, hw, yb, yt in ((86, 91, 16.5, 46, 77), (91, 96, 15, 49, 76), (96, 101, 13.6, 51, 75.5)):
        X(H.solid(z0, z1, hw, yb, yt, c=3))
    doors = {}
    for s in (-1, 1):
        c = []
        for i in range(4):
            z0 = 64 + 5.5 * i; z1 = z0 + 5.5; hwo = 21 - 8 * ((z0 + z1) / 2 - 64) / 36
            c.append(box(s * 0.8, 34 + 4.5 * i, z0, s * hwo, 73 - 0.6 * i, z1, DOOR, north=INTER))
        c += [box(s * x, 36, 63.6, s * (x + 2), 72, 64.4, DARK) for x in (4, 10, 15.5)]
        c += [box(s * 17.8, y, 63.2, s * 21.2, y + 4, 65.2, DARK) for y in (38, 53, 67)]            # hinge barrels
        c += [box(s * 3, 50, 85.8, s * 6.4, 56, 87.4, DARK), box(s * 0.8, 36, 63.4, s * 1.6, 72, 65, DARK)]
        doors[s] = c
    # ---------------- tail boom, swept fin, stabiliser, skid
    for i in range(9):
        z0 = 101 + 10 * i; t = (z0 + 5 - 101) / 90
        X(H.solid(z0, z0 + 10, lerp(13, 4.2, t), lerp(52, 62, t), lerp(75, 69, t), c=2))
    for i in range(7):
        A(box(-1.8, 70 + 7 * i, 168 + 3.4 * i, 1.8, 77 + 7 * i, 168 + 3.4 * i + 32 - 4.2 * i, HULL))
        A(box(-2.2, 70 + 7 * i, 168 + 3.4 * i - 1, 2.2, 77 + 7 * i, 168 + 3.4 * i, DARK))
    A(box(-2.4, 119, 191.5, 2.4, 121, 196.5, RED)); A(box(-26, 77, 158, 26, 79, 176, HULL))
    for s in (-1, 1): A(box(s * 25, 70, 158, s * 26.6, 86, 176, HULL))
    X([tube((0, 60, 168), (0, 41, 180), 3.2, DARK)]); A(box(-2, 38, 178, 2, 42, 190, DARK))
    A(box(2, 95, 189, 8, 105, 195, DARK)); A(box(5.4, 94, 188, 8, 106, 196, DARK))                 # tail rotor gearbox, bolted to the fin
    # ---------------- gearbox fairing, twin turboshafts, particle-separator intakes, swept exhausts
    X(H.solid(-18, 20, 11, TOP, 97, c=3)); A(box(-3.4, 97, -6, 3.4, 108, 2, DARK))
    for s in (-1, 1):
        cx = s * 14.5
        X(shift(H.solid(-42, 26, 6.6, 79, 94, c=3), dx=cx))
        A(box(cx - 7.2, 79.5, -47.5, cx + 7.2, 93.5, -42, HULL))
        A(box(cx - 5.4, 81.4, -48, cx + 5.4, 91.6, -47.2, DARK, north=GRILLE))
        A(box(cx - 3, 84, -48.4, cx + 3, 89, -47.6, DARK))
        X([tube((cx, 87, 24), (s * 31, 89.5, 47), 8.4, DARK)]); A(box(s * 28, 84, 46, s * 34, 94, 49.5, SOOT))
        A(box(s * 20.6, 62, 22, s * 21.3, 77, 64, SOOT)); A(box(cx - 5, 94, 30, cx + 5, 94.6, 56, SOOT))     # exhaust staining
        A(box(cx - 6.6, 92, -30, cx + 6.6, 93, 20, DARK, up=SPIN))                                    # access cowl hinge line
    for dz in (-14, -2, 10): A(box(-9, 97, dz, 9, 98.4, dz + 3, DARK))
    # ---------------- main rotor: hub, 5 blades with rest droop, nested blade bones
    hub = [box(-7, 104, -9, 7, 111, 5, DARK), box(-4, 111, -6, 4, 113, 2, SPIN)]
    blades = []
    for i in range(5):
        arm = f"main_blade_{i + 1}"
        blades += [bone(arm, "main_rotor", HUB, [box(5, 106.6, -6.4, 9, 109.6, 2.4, DARK)], rotation=[0, 72 * i, 0]),
                   bone(arm + "_droop", arm, HUB, [box(9, 107.2, -6.5, 66, 108.4, 2.5, BLADE)], rotation=[0, 0, DROOP]),
                   bone(arm + "_tip", arm + "_droop", [66, 108, -2],
                        [box(66, 107.2, -6.5, 142, 108.4, 2.5, BLADE), box(142, 107.2, -6.5, 152, 108.4, 2.5, TIP)], rotation=[0, 0, TIP_DROOP])]
    # ---------------- tail rotor (3 blades, axis X) on the left of the fin
    tail = [box(TAIL_HUB[0] - 1.5, TAIL_HUB[1] - 2.5, TAIL_HUB[2] - 2.5, TAIL_HUB[0] + 2, TAIL_HUB[1] + 2.5, TAIL_HUB[2] + 2.5, DARK)]
    for k in range(3):
        c = cbox(TAIL_HUB[0] + 1.5, TAIL_HUB[1] + 14.5, TAIL_HUB[2], 1.0, 24, 4.6, BLADE)
        c["pivot"], c["rotation"] = list(TAIL_HUB), [120 * k, 0, 0]; tail.append(c)
    # ---------------- tricycle landing gear with oleo shocks
    def gear_strut(x, z, top, ytop):
        out = [box(x - 2.4, 18, z - 2.4, x + 2.4, ytop, z + 2.4, DARK), box(x - 1.6, 9, z - 1.6, x + 1.6, 18.2, z + 1.6, SPIN),
               box(x - 2.8, 16.8, z - 2.8, x + 2.8, 18.4, z + 2.8, DARK)]
        out += [tube((x, 17.5, z - 2.5), (x, 12, z - 5), 1.2, SPIN), tube((x, 17.5, z + 2.5), (x, 12, z + 5), 1.2, SPIN)]   # torque links
        return out
    gnose = gear_strut(0, -72, None, 29) + [box(-6, 6.4, -73.2, 6, 8, -70.8, DARK), box(-5, 8, -73.4, -3.8, 12, -70.6, DARK), box(3.8, 8, -73.4, 5, 12, -70.6, DARK)]
    bones = [bone("root", None, [0, 0, 0], []),
             bone("fuselage", "root", [0, 0, 0], fus, locators={
                 "seat_pilot": [8, 40, -70], "seat_copilot": [-8, 40, -70], "cabin_entry": [0, 34, 62],
                 **{f"troop_{sn}{i}": [s * 16, 38.6, z] for sn, s in (("l", 1), ("r", -1)) for i, z in enumerate((-22, -10, 8, 20, 38, 50))},
                 "sling_attach": [0, -28, 0], "titan_hang": [0, -60, 0], "exo_hang_front": [0, -52, -20], "exo_hang_rear": [0, -52, 20]}),
             bone("cargo_deck", "fuselage", [0, FL, 0], deck),
             bone("clamshell_door_left", "fuselage", [19.5, 56, 64], doors[1]),
             bone("clamshell_door_right", "fuselage", [-19.5, 56, 64], doors[-1]),
             bone("main_rotor", "fuselage", HUB, hub), *blades,
             bone("tail_rotor", "fuselage", TAIL_HUB, tail),
             bone("gear_nose", "fuselage", [0, 29, -72], gnose),
             bone("wheel_nose", "gear_nose", [0, 7, -72], wheel12(-4.6, 7, -72, 5, 7, False, False) + wheel12(4.6, 7, -72, 5, 7, False, False))]
    for s, sn in ((1, "l"), (-1, "r")):
        gx = s * 24
        mg = gear_strut(gx, 10, None, 40) + [box(gx - 5, 6.4, 8.8, gx + 5, 8, 11.2, DARK)]
        mg += [tube((s * 20.6, 58, 22), (gx, 36, 12), 2.6, DARK), tube((s * 20.6, 52, -2), (gx, 38, 8), 2.4, DARK),
               box(s * 20, 32, 4, s * 25.6, 44, 16, DARK)]
        bones += [bone("gear_" + sn, "fuselage", [gx, 40, 10], mg),
                  bone("wheel_" + sn, "gear_" + sn, [gx + s * 1.5, 7, 10], wheel12(gx + s * 2, 7, 10, 7, 7, False, True))]
        # stub-wing pylon: tubular truss + 7-tube rocket pod + nav light
        py = [tube((s * 20.6, 66, 4), (s * 61, 58, 12), 3.2, DARK), tube((s * 20.6, 46, 22), (s * 59, 55, 15), 2.6, DARK),
              tube((s * 20.6, 66, 22), (s * 59, 57, 16), 2.2, DARK), tube((s * 61, 58, 12), (s * 61, 58, 26), 2.4, DARK),
              box(s * 57, 55.5, 10, s * 64, 58.5, 28, HULL)]
        px = s * 60
        py += [box(px - 6.5, 44, 2, px + 6.5, 56, 42, HULL), box(px - 7.3, 43.2, 14, px + 7.3, 56.8, 16, DARK), box(px - 7.3, 43.2, 30, px + 7.3, 56.8, 32, DARK),
               box(px - 4.5, 46, 42, px + 4.5, 54, 46, DARK), box(px - 4.5, 46, -1, px + 4.5, 54, 2, HULL)]
        for dx, dy in ((0, 0), (4.2, 0), (-4.2, 0), (2.1, 3.6), (-2.1, 3.6), (2.1, -3.6), (-2.1, -3.6)):
            py.append(box(px + dx - 1.7, 50 + dy - 1.7, 1.6, px + dx + 1.7, 50 + dy + 1.7, 2.4, SOOT))
        py.append(box(s * 63.4, 55, 14, s * 64.6, 58.4, 17, RED if s > 0 else GREEN))
        bones.append(bone("pylon_" + sn, "fuselage", [s * 20.6, 62, 12], py))
    # ---------------- ventral mech sling rig (Titan x1 or Exoframe x2)
    frame = [box(s * 7, 21, -32, s * 11.4, 28, 32, DARK) for s in (-1, 1)] + [box(-11.4, 21, z - 2.5, 11.4, 25, z + 2.5, DARK) for z in (-30, 0, 30)]
    frame += [box(-4, 15, -4, 4, 21, 4, DARK), box(-1.4, 8, -1.4, 1.4, 15, 1.4, SPIN)]
    cables = [tube((s * 9.2, 22, z), (s * 3, -25, z), 1.8, SPIN) for s in (-1, 1) for z in (-30, 0, 30)]
    bar = [box(-4.5, -30, -36, 4.5, -25, 36, DARK), box(-2, -25.2, -34, 2, -23.4, 34, SPIN)]
    for z in (-27, -9, 9, 27):
        bar += [box(-7, -35, z - 4.5, 7, -30, z + 4.5, DARK), box(-6, -36.4, z - 3.6, 6, -35, z + 3.6, SOOT),     # magnetic pad
                box(-7.4, -34, z - 4.9, -6.2, -29, z - 3.8, RED), box(6.2, -34, z + 3.8, 7.4, -29, z + 4.9, RED)]
        bar += [rbox(s * 7.6, -33, z, 1.4, 8, 5.4, [0, 0, s * 8], SPIN) for s in (-1, 1)]                       # clamp jaws
        bar += [tube((s * 3, -30, z), (s * 6.4, -33.4, z), 1.5, SPIN) for s in (-1, 1)]                         # hydraulic rams
    bones += [bone("sling_hook", "fuselage", [0, 24, 0], frame),
              bone("sling_cables", "fuselage", [0, 22, 0], cables),
              bone("sling_rig_clamp", "fuselage", [0, -25, 0], bar)]
    swings = [("door_l", [19.5, 56, 64], [0.8, 56, 66], [0, DOOR_OPEN, 0], 2, 1, 10), ("door_r", [-19.5, 56, 64], [-0.8, 56, 66], [0, -DOOR_OPEN, 0], 2, 1, 10)]
    meta = {"id": "mi17_hip", "name": "Mil Mi-17 Hip Heavy Tactical Transport", "tier": 2, "seat_capacity": 14,
            "payload": "1 Titan or 2 Exoframes, underslung on the ventral rig (also walkable troop hold)",
            "hull_rgb": (98, 112, 80), "belly_rgb": (66, 72, 56),
            "decks": {"cabin_deck": [[-18, 34, -37], [18, 34, 63]], "flight_deck": [[-13, 34, -96], [13, 34, -38]],
                      "sling_envelope_hang_zone": [[-24, -90, -40], [24, -30, 40]]},
            "seats": {"pilot": [8, 40, -70], "copilot": [-8, 40, -70], "troop_row_left_x": 16, "troop_row_right_x": -16,
                      "sling_attach": [0, -28, 0], "titan_hang_point": [0, -60, 0]},
            "extra": ["Sling rig is modelled deployed (bar at y=-30) but hidden (scale 0) in `idle`/`fly`/`cargo_open`; play `sling` only while a Titan/Exoframe is hooked, so an empty Mi-17 shows nothing below the belly.",
                      "Blades are modelled drooped; `fly` levels them (-3 / -5 deg on the droop bones) while `main_rotor` spins."],
            "swings": swings, "scale": 0.62, "bounds_w": 21, "bounds_h": 11, "bounds_off": [0, 3, 0], "view": (35, -22)}
    return bones, meta


def mi17_anims():
    blades_flat = {}
    for i in range(1, 6):
        blades_flat[f"main_blade_{i}_droop"] = {"rotation": [0, 0, -DROOP]}
        blades_flat[f"main_blade_{i}_tip"] = {"rotation": [0, 0, -TIP_DROOP]}
    # Empty hook = nothing under the belly: the whole rig is scaled to 0 in every clip except `sling`
    gone = {b: {"scale": [0, 0, 0]} for b in ("sling_hook", "sling_cables", "sling_rig_clamp")}
    shown = {b: {"scale": [1, 1, 1]} for b in gone}
    stowed = gone
    shut = {"clamshell_door_left": {"rotation": [0, 0, 0]}, "clamshell_door_right": {"rotation": [0, 0, 0]}}
    rotors = spin({"main_rotor": 1, "tail_rotor": 0}, 0.3)
    rotors["tail_rotor"]["rotation"]["0.3"] = [720, 0, 0]
    return anim_file("mi17_hip", {
        "idle": {"loop": True, "bones": {**stowed, **shut}},
        "fly": {"loop": True, "animation_length": 0.3, "bones": {**rotors, **blades_flat, **stowed, **shut}},
        "sling": {"loop": True, "animation_length": 0.3, "bones": {**rotors, **blades_flat, **shut, **shown}},
        "cargo_open": {"loop": True, "bones": {**stowed, "clamshell_door_left": {"rotation": [0, DOOR_OPEN, 0]}, "clamshell_door_right": {"rotation": [0, -DOOR_OPEN, 0]}}}})
