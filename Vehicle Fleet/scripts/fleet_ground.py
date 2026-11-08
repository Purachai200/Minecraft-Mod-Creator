"""Technical 4x4 (Tier 1) and Ural-style 6x6 hauler (Tier 2)."""
from fleet_common import *


# ============================================================ Tier 1: Land Cruiser 79 style technical
def technical():
    WX, W, R, FZ, RZ = 16, 8, 10, -34, 30          # wheel x, width, radius, axle z
    CY = R
    body, deck, gate, ring = [], [], [], []
    A, X = body.append, body.extend
    for s in (-1, 1):
        A(box(s * 8, 13, -50, s * 12, 18, 56, DARK))                                   # ladder frame rails
        A(box(s * 5, 13.5, FZ - 12, s * 7.5, 15, FZ + 12, DARK))                       # leaf springs
        A(box(s * 5, 13.5, RZ - 12, s * 7.5, 15, RZ + 12, DARK))
        for z in (FZ, RZ):
            X([tube((s * 10, 10, z - 3), (s * 10.5, 20, z - 3), 1.6, SPIN),            # shocks / suspension links
               tube((s * 6, 11, z - 8), (s * 9, 16, z - 14), 1.4, DARK)])             # trailing link
        A(box(s * 14, 20.5, FZ - 12, s * 19, 22.5, FZ + 12, HULL))                     # fender flares
        A(box(s * 14, 20.5, RZ - 12, s * 19, 22.5, RZ + 12, HULL))
        A(box(s * 17, 15, -30, s * 17.4, 18.5, 3, DARK))
        X([tube((s * 18.5, 17, -29), (s * 18.5, 17, 2), 3, DARK),                      # rock slider
           tube((s * 17.5, 17, -29), (s * 18.5, 18.5, -29), 1.6, DARK), tube((s * 17.5, 17, 1), (s * 18.5, 18.5, 1), 1.6, DARK)])
    for z in (FZ, RZ):
        A(box(-13, 8, z - 1.5, 13, 12, z + 1.5, DARK)); A(box(-4, 6, z - 4, 4, 12.5, z + 4, DARK))   # axles + diffs
    X([tube((0, 13, FZ), (0, 13, RZ), 2, DARK)])                                      # propshaft
    A(box(-17, 20.5, -30, 17, 22, 4, DARK))                                            # cab floor pan
    # ---- hood, grille, lamps
    A(box(-12, 34, -49, 12, 36, -28, HULL))
    for s in (-1, 1):
        A(rbox(s * 13.7, 33.6, -38.5, 4, 3.6, 21, [0, 0, s * 40], HULL))              # chamfered hood edge
        A(box(s * 13, 21, -50, s * 17, 33, -29, HULL))
        A(box(s * 9.5, 27.5, -52.8, s * 14.5, 32.5, -51.4, WHITE))                     # headlamp
        A(box(s * 14.6, 22.5, -52.4, s * 16.8, 25, -51.2, RED))                        # indicator
    A(box(-13, 21, -52, 13, 34, -50, HULL, north=GRILLE))
    A(box(-9, 33.5, -51.8, 9, 35, -50.2, DARK))
    # ---- bullbar, winch, roller fairlead, shackles
    for x in (-13, 0, 13):
        X([tube((x, 16, -55), (x, 36, -55), 2.4, DARK)])
    X([tube((-13, 36, -55), (13, 36, -55), 2.4, DARK), tube((-13, 26, -55), (13, 26, -55), 2.4, DARK),
       tube((-13, 17, -55), (13, 17, -55), 2.4, DARK)])
    for s in (-1, 1):
        X([tube((s * 13, 26, -55), (s * 17, 26, -47), 2.2, DARK), tube((s * 13, 36, -55), (s * 17, 34, -47), 2.2, DARK)])
    A(box(-7, 19, -52.4, 7, 23.5, -48.4, DARK)); A(box(-5, 19.5, -53.4, 5, 22.5, -52.4, SPIN))        # winch drum
    A(box(-6, 21, -57.5, 6, 23.2, -55.7, SPIN))                                        # roller fairlead
    for s in (-1, 1):
        A(box(s * 6.5, 19.6, -58, s * 7.3, 24, -54.8, DARK))
        A(box(s * 8.5, 14.2, -57, s * 10.7, 16.4, -55.4, RED)); A(box(s * 9, 16.4, -56.4, s * 10.2, 19, -55.8, RED))
    # ---- raked cab, glass, pillars, roof
    A(box(-16, 49.5, -29, 16, 52.5, 4, HULL))
    for s in (-1, 1):
        A(rbox(s * 15.6, 52, -12.5, 3.4, 3, 33, [0, 0, s * 35], HULL))
        X([tube((s * 16, 36, -29), (s * 16, 50, -21), 2.6, HULL), tube((s * 16, 22, 3.5), (s * 16, 50, 3.5), 2.4, HULL),
           tube((s * 16.2, 22, -9), (s * 16.2, 50, -9), 2.0, HULL)])                   # B-pillar
        A(wall(s, 15.6, 17.2, 22, 36.5, -28, 3, HULL))                                 # door lower panels
        A(box(s * 17.2, 28, -26, s * 17.7, 30.4, -23, DARK))                           # door handle
        A(box(s * 16.3, 38, -28, s * 16.7, 49, -10.2, GLASS)); A(box(s * 16.3, 38, -7.8, s * 16.7, 49, 2.8, GLASS))
        A(box(s * 17, 32, -25, s * 21.5, 35, -23.6, DARK)); A(box(s * 20.4, 35, -28, s * 21.8, 46, -23.8, DARK))   # mirror
        A(wall(s, 12.4, 14.4, 22, 36, -30, -29, DARK))
    A(rbox(0, 43, -25, 30.5, 16.1, 0.9, [-29.7, 0, 0], GLASS))                          # raked windscreen
    A(rbox(0, 43, -25, 1.2, 16.4, 1.4, [-29.7, 0, 0], HULL))
    A(box(-13, 38, 3.3, 13, 48, 4.3, GLASS)); A(box(-16, 22, 3, 16, 38, 5, HULL)); A(box(-16, 48, 3, 16, 50, 5, HULL))
    X([tube((s * 12, 53.2, -26), (s * 12, 53.2, 2), 1.5, DARK) for s in (-1, 1)])        # roof rails
    X([tube((-12, 53.2, z), (12, 53.2, z), 1.4, DARK) for z in (-20, -10, 0)])
    # ---- interior: dash, wheel, seats
    A(box(-15, 30, -28, 15, 36, -23.5, INTER)); A(box(-14, 36, -27, 14, 37, -24.5, DARK))
    A(rbox(7.5, 33, -21.5, 7, 0.9, 7, [-60, 0, 0], DARK)); A(rbox(7.5, 33, -21.5, 6, 1, 0.9, [-60, 0, 0], DARK))
    X([tube((7.5, 31, -24), (7.5, 33, -21.8), 1.4, DARK)])
    for s in (-1, 1):
        A(box(s * 7.5 - 4.5, 22, -18, s * 7.5 + 4.5, 26, -9.5, INTER))
        A(rbox(s * 7.5, 33, -8.5, 9, 14, 2.4, [-10, 0, 0], INTER)); A(box(s * 7.5 - 2.5, 40, -9.5, s * 7.5 + 2.5, 44, -8, INTER))
    A(box(-3, 22, -23, 3, 29, -10, DARK))                                              # centre console
    # ---- snorkel with cyclone filter (left A-pillar)
    X([tube((18.6, 27, -33), (18.6, 33, -31.2), 2.6, DARK), tube((18.6, 33, -31.2), (18.6, 54, -18.8), 2.6, DARK)])
    A(box(17.2, 26, -36, 20, 32, -31.2, DARK))
    A(rbox(18.6, 56.5, -17.5, 5.4, 5.4, 5.6, [-30, 0, 0], HULL)); A(rbox(18.6, 59.2, -16.2, 3.6, 2.6, 3.6, [-30, 0, 0], HULL))
    A(rbox(18.6, 56.3, -20.2, 4.2, 4.2, 0.8, [-30, 0, 0], DARK))
    # ---- rear lamps, bumper, exhaust, hitch
    for s in (-1, 1):
        A(box(s * 13, 27, 56.6, s * 16.6, 33, 57.6, RED)); A(box(s * 12.5, 26, 56.4, s * 14.5, 27.5, 57.4, WHITE))
        A(box(s * 14.5, 14, 56, s * 17.5, 20, 60, DARK))
    A(box(-14, 13, 56, 14, 17, 60, DARK)); A(box(-13, 17, 56, 13, 18, 59, WALK)); A(box(-2, 14, 60, 2, 17, 66, DARK))
    X([tube((-10, 14.5, 38), (-10, 14.5, 58), 2.4, DARK)]); A(box(-11.2, 13.3, 58, -8.8, 15.7, 59.2, SOOT))
    # ---- walkable bed (cargo_deck bone)
    D = deck
    D += [box(-14, 20, 4, 14, 23, 56, DARK), box(-14, 23, 5, 14, 24, 55, PLATE)]
    for s in (-1, 1):
        D.append(wall(s, 14, 17, 21, 33, 4, 56, HULL))
        D.append(tube((s * 15.5, 33.6, 4), (s * 15.5, 33.6, 56), 2.2, DARK))
        D.append(box(s * 14.2, 33, 3, s * 17.2, 34.3, 5, DARK))
        for z in (12, 30, 48): D += dring(s * 12.5, 24, z)                               # bed tie-downs
        D.append(tube((s * 13, 24, 6), (s * 13, 55, 6), 2.4, DARK))                      # headache rack uprights
        D.append(tube((s * 13, 55, 6), (s * 15.5, 34, 17), 2.0, DARK))
    D += [tube((-13, 55, 6), (13, 55, 6), 2.4, DARK), tube((-13, 41, 6), (13, 41, 6), 2.0, DARK)]
    D += [tube((x, 25, 6), (x, 55, 6), 1.5, DARK) for x in (-6.5, 0, 6.5)]
    D += [box(-14, 24, 4, 14, 33, 5.2, DARK)]
    # ---- tailgate (hinged at bed floor, folds 90 deg to a walk-on extension)
    gate += [box(-14, 24, 55, 14, 38, 56.6, DARK, north=PLATE), box(-14.2, 24, 55, -12.8, 38, 56.8, HULL), box(12.8, 24, 55, 14.2, 38, 56.8, HULL),
             box(-3, 34, 56.6, 3, 37, 57.4, SPIN), box(-13.4, 24, 54.5, -9.4, 26, 56.6, DARK), box(9.4, 24, 54.5, 13.4, 26, 56.6, DARK)]
    for s in (-1, 1): gate.append(tube((s * 14, 36, 55.8), (s * 15.4, 30, 52), 1.0, SPIN))   # support chain
    bones = [bone("root", None, [0, 0, 0], []),
             bone("body", "root", [0, 0, 0], body, locators={"seat_driver": [7.5, 29, -13.5], "seat_passenger": [-7.5, 29, -13.5],
                                                             "gunner_stand": [0, 24, 30], "exo_slot_centre": [0, 24, 30]}),
             bone("cargo_deck", "body", [0, 24, 30], deck),
             bone("tailgate", "cargo_deck", [0, 24, 55.5], gate)]
    for n, x, z, st in (("fl", WX, FZ, 1), ("fr", -WX, FZ, 1), ("rl", WX, RZ, 0), ("rr", -WX, RZ, 0)):
        p = [x, CY, z]
        if st:
            bones.append(bone("steer_" + n, "body", p, []))
            bones.append(bone("wheel_" + n, "steer_" + n, p, wheel12(x, CY, z, W, R)))
        else:
            bones.append(bone("wheel_" + n, "body", p, wheel12(x, CY, z, W, R)))
    meta = {"id": "technical_4x4", "name": "Heavy Tactical Technical 4x4", "tier": 1, "seat_capacity": 2, "payload": "1 Obsolete Exoframe only",
            "hull_rgb": (150, 132, 98), "belly_rgb": (96, 84, 62),
            "decks": {"cargo_deck": [[-14, 24, 5], [14, 24, 55]], "tailgate_open": [[-14, 24, 56.6], [14, 24, 70.6]]},
            "seats": {"driver": [7.5, 29, -13.5], "passenger": [-7.5, 29, -13.5], "gunner_stand": [0, 24, 30]},
            "steer_bones": ["steer_fl", "steer_fr"], "swings": [("tailgate", [0, 24, 55.5], [0, 38, 55.5], [-90, 0, 0], 2, 1, 10)], "scale": 4.2, "bounds_w": 5, "bounds_h": 4}
    return bones, meta


def technical_anims():
    wheels = {"wheel_fl": 0, "wheel_fr": 0, "wheel_rl": 0, "wheel_rr": 0}
    return anim_file("technical_4x4", {
        "idle": {"loop": True, "bones": {"tailgate": {"rotation": [0, 0, 0]}}},
        "drive": {"loop": True, "animation_length": 0.4, "bones": {**spin(wheels, 0.4), "tailgate": {"rotation": [0, 0, 0]}}},
        "tailgate_open": {"loop": True, "bones": {"tailgate": {"rotation": [-90, 0, 0]}}}})


# ============================================================ Tier 2: Ural-4320 style 6x6 hauler
def hauler():
    WX, WW, R = 20, 11, 12
    FZ, MZ, RZ, BZ = -52, 26, 52, 39
    body, deck, beams, ladder, chains = [], [], {}, [], []
    A, X = body.append, body.extend
    for s in (-1, 1):
        A(box(s * 9, 18, -66, s * 13, 24, 68, DARK))                                   # frame rails
        A(box(s * 5, 14, FZ - 12, s * 8, 16, FZ + 12, DARK))                           # front leaf pack
        A(wall(s, 15, 25.5, 36, 38, FZ - 14, FZ + 14, HULL))                           # front mudguard plate
        A(rbox(s * 20, 37, FZ - 17, 11, 2.4, 6, [-35, 0, 0], HULL))
        X([tube((s * 16, 10, FZ - 3), (s * 16, 20, FZ - 3), 2.2, SPIN)])
        # walking-beam tandem (left/right)
        bc = [box(s * 9, 9, MZ - 6, s * 14, 16, RZ + 6, DARK), box(s * 11, 16, BZ - 7, s * 13.5, 20, BZ + 7, DARK),
              box(s * 0, 10, MZ - 2, s * 14, 14, MZ + 2, DARK), box(s * 0, 10, RZ - 2, s * 14, 14, RZ + 2, DARK)]
        for z in (MZ, RZ): bc.append(box(s * 15, 9.5, z - 3, s * 16, 14.5, z + 3, DARK))
        beams[s] = bc
        for z in (MZ, RZ):
            A(box(s * 14.2, 25, z - 14, s * 26.5, 26.4, z + 14, HULL))                  # mudguards over rear tyres
            A(rbox(s * 20.3, 26, z + 15, 12, 2, 4, [20, 0, 0], HULL))
        A(box(s * 15, 12, 70, s * 25, 26, 71, DARK))                                    # mud flaps
        A(wall(s, 16, 22, 14, 26, -24, -4, DARK))                                       # fuel tank
        A(box(s * 15.8, 16, -24.3, s * 22.3, 17, -3.7, SPIN)); A(box(s * 15.8, 23, -24.3, s * 22.3, 24, -3.7, SPIN))
    for z in (FZ,):
        A(box(-20, 9, z - 2, 20, 14, z + 2, DARK)); A(box(-5.5, 6, z - 5, 5.5, 15, z + 5, DARK))
    A(box(-4, 7, BZ - 3, 4, 14, BZ + 3, DARK))
    X([tube((0, 14, FZ), (0, 14, MZ), 2.6, DARK), tube((0, 14, MZ), (0, 14, RZ), 2.6, DARK)])   # driveshafts
    X([box(-13, 18, z, 13, 24, z + 2, DARK) for z in (-40, -10, 20, 40, 64)])
    # ---- long snout hood: radiator slots, brush guard, lamps, fenders
    A(box(-17, 24, -40, 17, 36, -14, DARK)); A(box(-13, 24, -68, 13, 38, -42, DARK))                     # cab mount skirt + engine block
    A(box(-15, 38, -70, 15, 50, -40, HULL)); A(box(-12, 50, -68, 12, 53, -42, HULL))
    for s in (-1, 1):
        A(rbox(s * 14, 50.6, -55, 5, 3.4, 27, [0, 0, s * 40], HULL))
        A(box(s * 15, 36, -66, s * 19, 46, -40, HULL))                                  # fender body
        A(rbox(s * 19.8, 46, -53, 9, 2.2, 28, [0, 0, s * 12], HULL))
        A(box(s * 14.5, 41, -70.7, s * 19, 45.5, -69.5, WHITE)); A(box(s * 14.5, 37, -70.5, s * 19, 39.6, -69.5, RED))
        A(wall(s, 15.4, 16, 38, 50, -40.4, -39, DARK))
    A(box(-14, 28, -71, 14, 47, -69.6, HULL))
    for i in range(9): A(box(-12 + i * 3, 29, -71.7, -11 + i * 3, 46, -70.8, DARK))   # vertical radiator slots
    A(box(-14, 21, -76, 14, 28, -71, DARK)); A(box(-18, 22, -75, 18, 26, -71, DARK))     # heavy bumper
    for x in (-14, -7, 0, 7, 14):
        X([tube((x, 28, -74), (x, 49, -72.4), 2.0, DARK)])                              # brush guard bars
    X([tube((-14, 49, -72.4), (14, 49, -72.4), 2.2, DARK), tube((-14, 37, -73), (14, 37, -73), 2.0, DARK)])
    for s in (-1, 1):
        A(box(s * 10, 17, -78, s * 12.6, 19.6, -75.6, RED)); A(box(s * 10.4, 19.6, -77, s * 12.2, 24, -76, RED))   # tow shackles
        A(box(s * 7, 53, -62, s * 11, 54, -48, DARK))                                   # hood latches/louvre
    A(box(-3, 38, -62, 3, 41, -61, SPIN))
    # ---- cab
    cz0, cz1 = -40, -14
    A(box(-21, 36, cz0, 21, 42, cz1, DARK)); A(box(-20, 76, cz0 - 1, 20, 79, cz1 + 1, HULL))
    for s in (-1, 1):
        A(rbox(s * 20.2, 78.6, -27, 3, 3, 28, [0, 0, s * 40], HULL))
        A(wall(s, 19.4, 21, 42, 56, cz0, cz1, HULL))
        A(wall(s, 19.4, 21, 56, 76, cz0, cz0 + 2.5, HULL)); A(wall(s, 19.4, 21, 56, 76, cz1 - 2.5, cz1, HULL))
        A(box(s * 20.4, 58, cz0 + 4, s * 21, 74, cz1 - 4, GLASS))
        A(box(s * 21, 44, -37, s * 21.8, 46, -33, DARK)); A(box(s * 20.4, 56, -27, s * 21.4, 57.2, -26, DOOR))
        A(box(s * 21, 49, -18, s * 22, 53, -14, DARK))
        X([tube((s * 24, 58, -37), (s * 24, 78, -37), 2, DARK), tube((s * 21, 66, -37), (s * 24.4, 66, -37), 1.6, DARK),
           tube((s * 24, 78, -37), (s * 26.8, 78, -37), 1.6, DARK)])                    # mirror arm
        A(box(s * 25.5, 62, -38, s * 28.5, 82, -36, DARK))                              # mirror head
        A(wall(s, 20, 23, 36, 42, cz0 - 1, cz0 + 8, HULL))                              # step plate
    for x0, x1 in ((-19, -0.6), (0.6, 19)):
        A(rbox((x0 + x1) / 2, 66.5, cz0 - 0.4, x1 - x0, 17, 0.9, [-6, 0, 0], GLASS))
    A(rbox(0, 66.5, cz0 - 0.4, 1.4, 17.5, 1.4, [-6, 0, 0], HULL))
    A(rbox(0, 78.6, cz0 - 3, 40, 1.2, 6, [-14, 0, 0], DARK))                            # sun visor
    A(box(-19, 56, cz1 - 2.4, 19, 76, cz1, HULL)); A(box(-12, 60, cz1 - 3, 12, 72, cz1 - 2.2, GLASS))
    A(box(-6, 79, -34, 6, 80.4, -22, DARK))                                             # roof hatch
    A(box(-19, 42, cz0 + 1, 19, 56, cz0 + 4, INTER)); A(box(-19, 42, cz0 + 4, 19, 43.4, cz1, WALK))
    for sx in (-10, 0, 10):
        A(box(sx - 4.5, 43.4, -30, sx + 4.5, 47, -21, INTER)); A(rbox(sx, 53, -20.5, 9, 14, 2.4, [-10, 0, 0], INTER))
    A(rbox(-10, 56, -35, 8, 0.9, 8, [-65, 0, 0], DARK))
    X([tube((-10, 50, -37), (-10, 54, -35), 1.6, DARK)])
    # ---- twin vertical stacks with rain caps, behind the cab
    for s in (-1, 1):
        X([tube((s * 20.5, 34, -11.5), (s * 20.5, 90, -11.5), 4.4, DARK), tube((s * 18, 50, -11.5), (s * 20.5, 50, -11.5), 1.4, SPIN),
           tube((s * 18, 70, -11.5), (s * 20.5, 70, -11.5), 1.4, SPIN)])
        A(box(s * 20.5 - 3, 86, -14.5, s * 20.5 + 3, 90.4, -8.5, SOOT))                 # sooted collar
        A(rbox(s * 20.5, 92, -11.5 - 3, 6.6, 0.9, 6.6, [-55, 0, 0], HULL, pivot=[s * 20.5, 91, -14.5]))   # open rain cap
        A(box(s * 22.2, 40, -14, s * 22.8, 64, -9, DARK))
    # ---- walkable steel flatbed
    deck += [box(-19, 24, -8, 19, 30, 70, DARK), box(-19, 30, -8, 19, 32, 70, WALK)]
    deck += [box(-19, 32, -8, 19, 62, -5, HULL), box(-19, 32, -8, 19, 62, -7.2, INTER)]
    deck += [tube((x, 32, -5), (x, 66, -5), 2.4, DARK) for x in (-17, 17)] + [tube((-17, 66, -5), (17, 66, -5), 2.4, DARK), tube((-17, 50, -5), (17, 50, -5), 2.0, DARK)]
    deck += [tube((x, 52, -5), (x, 64, -5), 1.4, DARK) for x in (-10, -3, 4, 11)]
    for s in (-1, 1):
        for z in (4, 22, 40, 58): deck.append(box(s * 22, 28, z, s * 23.4, 33.5, z + 2.6, SPIN))   # stake pockets / lashing eyes
        for z in (6, 26, 46, 64): deck += dring(s * 16.5, 32, z)
    deck += [box(-3, 24, 70, 3, 28, 77, DARK), box(-4, 27.6, 74, 4, 29.6, 78, SPIN)]  # towing pintle
    # drop sides (hinged outward) and tailgate
    sides = {}
    for s in (-1, 1):
        c = [wall(s, 19, 21.6, 32, 46, -8, 70, HULL), tube((s * 21, 46.6, -8), (s * 21, 46.6, 70), 2.2, DARK), box(s * 18.4, 32, -8, s * 22.4, 33.6, 70, DARK)]
        c += [box(s * 21.6, 33.4, z, s * 22.4, 45.4, z + 2, DARK) for z in range(-6, 70, 13)]
        sides[s] = c
    gate = [box(-19, 32, 69, 19, 46, 71, HULL, north=INTER), box(-19.3, 32, 68.6, -17.2, 46, 71.4, DARK), box(17.2, 32, 68.6, 19.3, 46, 71.4, DARK),
            box(-3, 40, 71, 3, 43.6, 72, SPIN)]
    ladder += [tube((s * 8, 31, 71.8), (s * 8, 2, 85), 2.2, SPIN) for s in (-1, 1)]
    ladder += [box(-8, 31 - 29 * t - 0.7, 71.8 + 13.2 * t - 1.2, 8, 31 - 29 * t + 0.7, 71.8 + 13.2 * t + 1.2, SPIN) for t in (0.12, 0.3, 0.48, 0.66, 0.84)]
    ladder += [box(-9, 29.5, 70.8, -7, 32, 72.4, DARK), box(7, 29.5, 70.8, 9, 32, 72.4, DARK)]
    # heavy tie-down chains for one kneeling Titan (laid slack across the deck)
    for z in (14, 52):
        chains += [tube((-16.5, 32.6, z), (-4, 33.8, z + 4), 1.1, DARK), tube((-4, 33.8, z + 4), (4, 33.8, z - 4), 1.1, DARK), tube((4, 33.8, z - 4), (16.5, 32.6, z), 1.1, DARK)]
        chains += [box(x - 1, 34.3, zz - 1, x + 1, 36.3, zz + 1, RED) for x, zz in ((-4, z + 4), (4, z - 4))]      # tensioner binders
    bones = [bone("root", None, [0, 0, 0], []),
             bone("body", "root", [0, 0, 0], body, locators={"seat_driver": [-10, 47, -25], "seat_passenger": [10, 47, -25], "seat_centre": [0, 47, -25],
                                                              "exo_slot_a": [0, 32, 10], "exo_slot_b": [0, 32, 50], "titan_slot": [0, 32, 31]}),
             bone("cargo_deck", "body", [0, 32, 31], deck),
             bone("drop_side_l", "cargo_deck", [22, 32, 31], sides[1]), bone("drop_side_r", "cargo_deck", [-22, 32, 31], sides[-1]),
             bone("tailgate", "cargo_deck", [0, 32, 70], gate), bone("rear_ladder", "tailgate", [0, 30, 71.8], ladder),
             bone("cargo_straps", "cargo_deck", [0, 34, 31], chains)]
    for n, x in (("fl", WX), ("fr", -WX)):
        p = [x, R, FZ]; bones += [bone("steer_" + n, "body", p, []), bone("wheel_" + n, "steer_" + n, p, wheel12(x, R, FZ, WW, R))]
    for s, sn in ((1, "l"), (-1, "r")):
        bones.append(bone("walking_beam_" + sn, "body", [s * 12, 15, BZ], beams[s]))
        for z, tag in ((MZ, "m"), (RZ, "r")):
            bones.append(bone(f"wheel_{tag}{sn}", "walking_beam_" + sn, [s * WX, R, z], wheel12(s * WX, R, z, WW, R)))
    meta = {"id": "ural_6x6", "name": "Heavy 6x6 Off-Road Hauler", "tier": 2, "seat_capacity": 3, "payload": "1 kneeling Titan or 2 Exoframes",
            "hull_rgb": (92, 104, 72), "belly_rgb": (62, 66, 50),
            "decks": {"cargo_deck": [[-19, 32, -7], [19, 32, 69]], "tailgate_open": [[-19, 32, 71], [19, 32, 85]]},
            "seats": {"driver": [-10, 47, -25], "passenger": [10, 47, -25], "centre": [0, 47, -25]},
            "steer_bones": ["steer_fl", "steer_fr"], "swings": [("tailgate", [0, 32, 70], [0, 46, 70], [-90, 0, 0], 2, 1, 10), ("drop_side_l", [22, 32, 31], [22, 46, 31], [0, 0, 90], 0, 1, 10), ("drop_side_r", [-22, 32, 31], [-22, 46, 31], [0, 0, -90], 0, -1, 10)], "scale": 3.1, "bounds_w": 7, "bounds_h": 8}
    return bones, meta


def hauler_anims():
    wheels = {f"wheel_{n}": 0 for n in ("fl", "fr", "ml", "mr", "rl", "rr")}
    closed = {"tailgate": {"rotation": [0, 0, 0]}, "drop_side_l": {"rotation": [0, 0, 0]}, "drop_side_r": {"rotation": [0, 0, 0]}}
    return anim_file("ural_6x6", {
        "idle": {"loop": True, "bones": closed},
        "drive": {"loop": True, "animation_length": 0.4, "bones": {**spin(wheels, 0.4), **closed}},
        "deck_open": {"loop": True, "bones": {"tailgate": {"rotation": [-90, 0, 0]}, "drop_side_l": {"rotation": [0, 0, 90]},
                                               "drop_side_r": {"rotation": [0, 0, -90]}}},
        "beam_rock": {"loop": True, "animation_length": 2.0, "bones": {
            "walking_beam_l": {"rotation": {"0.0": [0, 0, 0], "1.0": [6, 0, 0], "2.0": [0, 0, 0]}},
            "walking_beam_r": {"rotation": {"0.0": [0, 0, 0], "1.0": [-6, 0, 0], "2.0": [0, 0, 0]}}}}})
