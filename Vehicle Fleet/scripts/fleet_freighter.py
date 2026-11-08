"""Civilian coaster tramp freighter (Tier 3 naval): flared bow, open well deck, lattice derrick, aft deckhouse."""
import math
from fleet_common import *
from fleet_interior import *
from fleet_ships import tier, lower

DECK, WELL_Y, WELL_X = 44, 28, 41          # main deck, well floor, well half width
WELL_Z0, WELL_Z1 = -176, 36
BOW_Z, STERN_Z = -260, 258


AFT, HATCH = (44, 236), (124, 156)          # hollow below-deck range (16 px slice grid) and stair hatch


def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def beam(z):
    """Half width at the deck line."""
    if z < -110:
        t = (z - BOW_Z) / (-110 - BOW_Z); return 4 + 56 * t ** 0.62 + 8 * (1 - t)
    if z <= 170: return 60
    return 60 - 20 * smooth((z - 170) / (STERN_Z - 170))


def deck_y(z): return 58 if z < -200 else DECK


def freighter():
    hull, house, rails, crane, boom, hook, radar, boats = [], [], [], [], [], [], [], []
    H_, A = hull, hull.append
    z = BOW_Z
    while z < STERN_Z:
        z1 = min(z + 16, STERN_Z); zm = (z + z1) / 2
        hw = beam(zm); yt = deck_y(zm); t = max(0, min(1, (zm - BOW_Z) / 150))
        hb = max(2, hw - 4 - 14 * (1 - t) - 4)
        in_well = WELL_Z0 <= z and z1 <= WELL_Z1
        hollow = AFT[0] <= z and z1 <= AFT[1]
        if hollow:
            f, hb2 = 8, max(2, hw - 8)
            H_.append(box(-hb2, 0, z, hb2, f, z1, BELLY, up=WALK))
            for s in (-1, 1): H_ += [wall(s, hb2 - 3, hb2, f, 24, z, z1, BELLY), wall(s, hw - 3, hw, 24, yt - 3, z, z1, HULL), box(s * (hb2 - 3), 22, z, s * hw, 24, z1, BELLY)]
            H_ += slab(-hw, hw, z, z1, yt - 3, 3, (8, 24, z, z1) if HATCH[0] <= z and z1 <= HATCH[1] else None)
            for s in (-1, 1): H_.append(box(s * (hw - 2), yt, z, s * hw, yt + 7, z1, HULL))
            z = z1
            continue
        H_.append(box(-max(2, hb - 10), 0, z, max(2, hb - 10), 12, z1, BELLY))
        H_.append(box(-hb, 12, z, hb, 24, z1, BELLY))
        if in_well:
            H_.append(box(-hw, 24, z, hw, WELL_Y, z1, HULL, up=WALK))
            for s in (-1, 1): H_.append(wall(s, WELL_X, hw, WELL_Y, yt, z, z1, HULL))
            for s in (-1, 1): H_.append(box(s * (hw - 2), yt, z, s * hw, yt + 7, z1, HULL))      # bulwark
        else:
            H_.append(box(-hw, 24, z, hw, yt, z1, HULL, up=WALK))
            if z1 <= WELL_Z0 or z >= WELL_Z1:
                for s in (-1, 1): H_.append(box(s * (hw - 2), yt, z, s * hw, yt + 7, z1, HULL))
        z = z1
    Hb = lambda zz: max(2, beam(zz) - 8) - 3
    hull += lower([(44, 124, "engine"), (124, 156, "stairs"), (156, 236, "bunks")], lambda zz: DECK, 8, Hb, (8, 24, 124, 156))
    # bow detail: breakwater, hawseholes, anchors, bollards
    for s in (-1, 1):
        hwz = beam(-226)
        A(box(s * (hwz - 0.5), 46, -230, s * (hwz + 0.8), 54, -222, DARK))
        A(box(s * (hwz + 0.2), 36, -229, s * (hwz + 1.4), 46, -226, SPIN)); A(box(s * (hwz + 0.2), 33, -233, s * (hwz + 1.4), 36, -222, SPIN))
        A(box(s * (hwz + 0.2), 40, -232.5, s * (hwz + 1.4), 41.5, -222.5, DARK))
    for zz in (-244, -214, -150, -60, 0, 120, 210, 244):
        for s in (-1, 1):
            x = s * (beam(zz) - 7); y = deck_y(zz)
            hull.append(box(x - 1.4, y, zz - 1.4, x + 1.4, y + 7, zz + 1.4, DARK)); hull.append(box(x - 2.4, y + 6, zz - 2.4, x + 2.4, y + 8, zz + 2.4, DARK))
    for z0 in range(-168, 30, 32):                                                              # lashing points on the well floor
        for x in (-28, -14, 0, 14, 28): hull += dring(x, WELL_Y, z0 + 8)
    # raised coamings around the open cargo well
    for s in (-1, 1):                                                                           # side coamings with a stair gap at z -100..-88
        for za, zb in ((WELL_Z0 - 4, -100), (-88, WELL_Z1 + 4)): hull.append(box(s * WELL_X, DECK, za, s * (WELL_X + 4), DECK + 10, zb, HULL, **({"west": INTER} if s > 0 else {"east": INTER})))
        hull += step_run(0, s * 25, s * 41, -100, -88, WELL_Y, WELL_Y, DECK, 4)
    hull += step_run(2, -188, -200, -32, -18, DECK, DECK, DECK + 14, 2)
    hull += [box(-WELL_X - 4, DECK, WELL_Z0 - 4, WELL_X + 4, DECK + 10, WELL_Z0, HULL), box(-WELL_X - 4, DECK, WELL_Z1, WELL_X + 4, DECK + 10, WELL_Z1 + 4, HULL)]
    hull += [box(-WELL_X, WELL_Y, WELL_Z0 - 0.4, WELL_X, DECK, WELL_Z0, INTER)]
    for zz in range(WELL_Z0, WELL_Z1, 28): hull += [box(s * (WELL_X + 4), DECK, zz, s * (WELL_X + 5.2), DECK + 10, zz + 3, DARK) for s in (-1, 1)]   # coaming stiffeners
    # ---------------- aft deckhouse: three walkable tiers (cabins / mess, officers, bridge), wings, funnel, radar
    D = DECK
    house += tier(44, 100, 188, D, 36, [(100, 188, "cabins")], doors_z=(112, 176), front=[(-7, 7, D, D + DOOR_H, "door")],
                  back=[(-7, 7, D, D + DOOR_H, "door")], stair=(-26, -10, 134, 162), ceil_hole=(-26, -10, 134, 162))
    house += tier(38, 112, 188, D + 36, 36, [(112, 188, "stairs")], doors_z=(150,), front=[], back=[(-7, 7, D + 36, D + 36 + DOOR_H, "door")], stair=(6, 22, 130, 158), ceil_hole=(6, 22, 130, 158))
    house += tier(34, 116, 170, D + 72, 36, [(116, 170, "bridge")], doors_z=(150,), front=[(-30, 30, D + 84, D + 100, "win")], back=[], only=-1)
    house += [box(-37, D + 108, 118, 37, D + 111, 174, HULL), box(-38, D + 111, 118, 38, D + 112, 175, DARK, up=WALK)]
    for s in (-1, 1):
        house += [box(s * 34, D + 72, 128, s * 68, D + 74, 162, DARK, up=WALK), box(s * 66, D + 74, 128, s * 68, D + 82, 162, HULL)]
        for xx, zz in [(s * 40, 162), (s * 52, 162), (s * 64, 162), (s * 68, 150), (s * 68, 138), (s * 68, 129), (s * 52, 128), (s * 40, 128)]:
            house.append(tube((xx, D + 74, zz), (xx, D + 88, zz), 1.2, SPIN))
        house += [tube((s * 38, D + 88, 162), (s * 68, D + 88, 162), 1.2, SPIN), tube((s * 68, D + 88, 129), (s * 68, D + 88, 162), 1.2, SPIN), tube((s * 38, D + 88, 128), (s * 68, D + 88, 128), 1.2, SPIN)]
        house.append(box(s * 66.4, D + 88, 150, s * 68.2, D + 94, 154, RED if s > 0 else GREEN))
    y0 = D + 72
    house += [rbox(0, y0 + 22, 180, 26, 44, 24, [-5, 0, 0], HULL, pivot=[0, y0, 180]), rbox(0, y0 + 47, 181.8, 27, 7, 25, [-5, 0, 0], DARK, pivot=[0, y0, 180]),
              rbox(0, y0 + 53, 182.4, 22, 4, 21, [-5, 0, 0], SOOT, pivot=[0, y0, 180]), rbox(0, y0 + 30, 180, 27, 5, 25, [-5, 0, 0], WHITE, pivot=[0, y0, 180]),
              rbox(0, y0 + 35, 180.4, 27.2, 3, 25.2, [-5, 0, 0], RED, pivot=[0, y0, 180])]
    house += [tube((0, y0, 168), (0, y0 + 62, 167), 2.0, SPIN), tube((10, y0, 168), (10, y0 + 54, 168), 1.4, DARK)]
    house += [tube((0, D + 112, 146), (0, D + 158, 146), 3, DARK), tube((-14, D + 146, 146), (14, D + 146, 146), 1.6, DARK), tube((-14, D + 146, 146), (0, D + 158, 146), 0.9, SPIN), tube((14, D + 146, 146), (0, D + 158, 146), 0.9, SPIN),
              box(-1.5, D + 158, 144.5, 1.5, D + 162, 147.5, RED)]
    radar += [box(-3, D + 158, 143, 3, D + 163, 149, DARK), box(-19, D + 163, 145, 19, D + 166, 147.2, HULL), box(-19.4, D + 163, 144.4, -17.6, D + 167, 147.8, DARK), box(17.6, D + 163, 144.4, 19.4, D + 167, 147.8, DARK)]
    # lifeboats on davits
    for s in (-1, 1):
        bx = s * 52
        boats += shift(H.solid(124, 154, 5.4, 52, 60, c=2), dx=bx)
        boats += [box(bx - 6, 59, 122, bx + 6, 60, 156, WHITE), box(bx - 3, 57, 119, bx + 3, 60, 124, HULL), box(bx - 3, 57, 154, bx + 3, 60, 159, HULL),
                  box(bx - 5, 52, 128, bx + 5, 54, 150, DARK)]
        for zz in (128, 148):
            boats += [tube((s * 58, DECK, zz), (s * 58, 84, zz), 2.2, DARK), tube((s * 58, 84, zz), (s * 50, 92, zz), 2.0, DARK), tube((s * 50, 90, zz), (bx, 62, zz), 0.9, SPIN)]
    # ---------------- stern gear: mooring winch + flagstaff + docking light
    hull += [box(-8, DECK, 212, 8, DECK + 8, 226, DARK), box(-3, DECK + 8, 215, 3, DECK + 14, 223, SPIN), tube((0, DECK, 252), (0, DECK + 34, 252), 1.4, SPIN),
             box(-4, DECK + 28, 252, 4, DECK + 29.4, 252.6, RED), box(-14, 44, 196, 14, 52, 204, HULL, up=SPIN)]
    # ---------------- lattice-boom derrick (pedestal + kingposts + boom + topping lift)
    base = (0, 62, -192); L = 150; el = math.radians(38)
    d = (0, math.sin(el), math.cos(el)); u = (0, math.cos(el), -math.sin(el))
    tip = tuple(base[i] + L * d[i] for i in range(3))
    crane += [box(-12, DECK, -200, 12, 62, -184, DARK), box(-14, 60, -202, 14, 64, -182, HULL, up=WALK)]
    for s in (-1, 1):
        crane += [tube((s * 9, 64, -196), (s * 9, 122, -196), 4, HULL), tube((s * 9, 122, -196), (s * 2, 130, -196), 2.4, DARK)]
        crane += [tube((s * 9, 64, -196), (s * 28, DECK, -176), 1.2, SPIN), tube((s * 9, 64, -196), (s * 28, DECK, -214), 1.2, SPIN)]       # guys
    crane += [tube((-9, 108, -196), (9, 108, -196), 2.4, DARK), box(-4, 128, -199, 4, 134, -193, DARK)]
    crane += [box(14, DECK, -208, 30, DECK + 12, -190, DARK), box(15, DECK + 12, -206, 29, DECK + 14, -192, HULL)]                           # derrick winch house
    def sec(t): return 5.2 - 3.2 * t
    n = 10; pts = []
    for i in range(n + 1):
        t = i / n; c = tuple(base[k] + L * t * d[k] for k in range(3)); h = sec(t)
        pts.append([tuple(c[k] + sx * h * (1 if k == 0 else 0) + sy * h * u[k] for k in range(3)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    for ci in range(4): boom.append(tube(pts[0][ci], pts[-1][ci], 1.8, HULL))
    for i in range(n + 1):
        for ci in range(4): boom.append(tube(pts[i][ci], pts[i][(ci + 1) % 4], 1.1, DARK))
        if i < n:
            for ci in range(4):
                boom.append(tube(pts[i][ci], pts[i + 1][(ci + 1) % 4], 0.9, DARK))
    boom += [tube((0, 130, -196), tip, 1.4, SPIN), tube((0, 128, -196), (0, 128, -198), 0.8, SPIN)]
    boom += [box(-3, tip[1] - 2, tip[2] - 2, 3, tip[1] + 3, tip[2] + 3, DARK)]
    hk = (0, tip[1], tip[2] + 1)
    hook += [tube((0, hk[1] - 2, hk[2]), (0, hk[1] - 60, hk[2]), 1.2, SPIN), box(-4, hk[1] - 68, hk[2] - 3, 4, hk[1] - 60, hk[2] + 3, DARK),
             box(-1.2, hk[1] - 76, hk[2] - 1.2, 1.2, hk[1] - 68, hk[2] + 1.2, SPIN), box(-3, hk[1] - 79, hk[2] - 1.2, 3, hk[1] - 76, hk[2] + 1.2, RED)]
    bones = [bone("root", None, [0, 0, 0], []),
             bone("hull", "root", [0, 0, 0], hull + house, locators={"bridge_helm": [10, DECK + 72, 140], "gangway": [0, DECK, 212],
                                                                    "titan_slot_a": [0, WELL_Y, -120], "titan_slot_b": [0, WELL_Y, -20]}),
             bone("cargo_deck", "hull", [0, WELL_Y, -70], []),
             bone("deckhouse_lifeboats", "hull", [0, 60, 140], boats),
             bone("derrick_crane", "hull", base, crane), bone("derrick_boom", "derrick_crane", base, boom),
             bone("derrick_hook", "derrick_boom", tip, hook), bone("radar", "hull", [0, DECK + 158, 146], radar)]
    meta = {"id": "coaster_freighter", "name": "Civilian Coaster Tramp Freighter", "tier": 3, "seat_capacity": 4,
            "payload": "2 Titans in the well, or 4-6 Exoframes (well + walkable deck perimeter)",
            "hull_rgb": (84, 96, 108), "belly_rgb": (120, 52, 40),
            "decks": {"well_floor": [[-WELL_X, WELL_Y, WELL_Z0], [WELL_X, WELL_Y, WELL_Z1]],
                      "main_deck_port_walkway": [[WELL_X + 4, DECK, -196], [beam(0) - 2, DECK, 100]],
                      "main_deck_starboard_walkway": [[-(beam(0) - 2), DECK, -196], [-(WELL_X + 4), DECK, 100]],
                      "forecastle": [[-40, 58, -258], [40, 58, -202]], "poop_deck": [[-44, DECK, 190], [44, DECK, 254]],
                      "bridge_wings": [[-68, DECK + 74, 128], [68, DECK + 74, 162]], "tier1_floor": [[-42, DECK, 101], [42, DECK, 187]], "tier2_floor": [[-36, DECK + 36, 113], [36, DECK + 36, 187]],
                      "bridge_floor": [[-32, DECK + 72, 125], [32, DECK + 72, 169]], "lower_deck": [[-40, 8, 44], [40, 8, 236]]},
            "interior": ["lower deck (floor y=8): engine room 44..124, stair hatch 124..156 (x 8..22), crew bunks 156..236", "tier 1: cabins, stairs, mess; tier 2: officers; tier 3: bridge with wing doors"],
            "seats": {"helm": [10, DECK + 72, 140], "titan_slot_a": [0, WELL_Y, -120], "titan_slot_b": [0, WELL_Y, -20]},
            "extra": ["Hull keel y=0; design waterline y~24 (low freeboard 20 px). Coamings are 10 px above the main deck, hold them as solid collider walls.",
                      "Walkable surfaces are decks only - superstructure tiers need their own collider if you want interior access."],
            "scale": 0.52, "bounds_w": 40, "bounds_h": 14, "bounds_off": [0, 4, 0], "view": (35, -25)}
    return bones, meta


def freighter_anims():
    return anim_file("coaster_freighter", {
        "idle": {"loop": True, "bones": {"radar": {"rotation": [0, 0, 0]}}},
        "radar_spin": {"loop": True, "animation_length": 4.0, "bones": spin({"radar": 1}, 4.0)},
        "derrick_luff": {"loop": True, "animation_length": 8.0, "bones": {"derrick_boom": {"rotation": {"0.0": [0, 0, 0], "4.0": [18, 0, 0], "8.0": [0, 0, 0]}}}}})
