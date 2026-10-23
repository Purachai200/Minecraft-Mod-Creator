"""Geometry source for the GeckoLib flight-rig models.

  python3 tools/model_spec.py [preview.json]

Writes assets/youjosenki/geo/<design>.geo.json from the PARTS below (child bones are named parent_child).
Coordinates are vanilla humanoid model units (y down, -z = front):
  torso x -4..4, y 0..12, z -2..2   | legs (pivot +-1.9,12,0) x -2..2, y 0..12
  arms (pivot +-5,2,0) right x -3..1, left x -1..3, y -2..10 | head y -8..0, z -4..4
Boxes are (texOffs, min corner, max corner). Left-side parts are mirrored from right-side ones.
"""
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# texOffs palette (material is assigned per texOffs in generate_textures.py)
WEB, POUCH, HOSE, RAIL, BRIGHT, GAUGE, GLASS, CORE = (0, 0), (40, 0), (40, 6), (40, 8), (24, 26), (32, 64), (36, 26), (104, 0)
NAV_G, NAV_R, STROBE = (112, 0), (116, 0), (120, 0)
HOUSING, COWL, SKIRT, FRAME, FRAME2, PANEL = (0, 16), (24, 16), (0, 46), (0, 96), (0, 110), (0, 76)
NOZ_A, NOZ_B, NOZ_C, NOZ_D, NOZ_HEEL, NOZ_BIG_L, NOZ_BIG_R = (48, 64), (48, 70), (20, 46), (28, 46), (76, 15), (60, 96), (74, 96)
TANK_L, TANK_R, TANK_BIG_L, TANK_BIG_R = (0, 64), (16, 64), (24, 96), (42, 96)
AERO, WING_L, WING_R, NACELLE_L, NACELLE_R = (64, 64), (64, 76), (64, 82), (96, 64), (106, 64)
LEG, LEG_STRUT, LEG_STRUT2, KNEE, SHIN, CUFF, SOLE, TOE = (64, 0), (64, 6), (70, 6), (64, 15), (64, 22), (64, 34), (76, 0), (76, 10)


def b(uv, x0, y0, z0, x1, y1, z1):
    return (uv, (min(x0, x1), min(y0, y1), min(z0, z1)), (max(x0, x1), max(y0, y1), max(z0, z1)))


class P:
    def __init__(self, name, boxes, pivot=(0.0, 0.0, 0.0), children=(), var=None):
        self.name, self.boxes, self.pivot, self.children, self.var = name, list(boxes), pivot, list(children), var


SWAP = {TANK_L: TANK_R, TANK_BIG_L: TANK_BIG_R, NOZ_BIG_L: NOZ_BIG_R, NOZ_C: NOZ_D, WING_L: WING_R,
        NACELLE_L: NACELLE_R, NAV_G: NAV_R, LEG_STRUT: LEG_STRUT2}
SWAP.update({v: k for k, v in list(SWAP.items())})  # mirroring works in both directions


def mbox(bx, swap=True):
    uv, (x0, y0, z0), (x1, y1, z1) = bx
    return b(SWAP.get(uv, uv) if swap else uv, -x1, y0, z0, -x0, y1, z1)


def sym(*boxes, swap=True):
    """Box plus its x-mirror."""
    out = []
    for bx in boxes:
        out += [bx, mbox(bx, swap)]
    return out


def mirror_part(p, name=None, swap=True):
    return P(name or p.name, [mbox(x, swap) for x in p.boxes], (-p.pivot[0], p.pivot[1], p.pivot[2]),
             [mirror_part(c, swap=swap) for c in p.children])


# ------------------------------------------------------------------ shared harness
def harness():
    return [
        *sym(b(WEB, 1.3, -0.2, -2.6, 3.5, 9.0, -2.0)),             # front shoulder straps
        *sym(b(WEB, 1.1, -0.8, -2.7, 4.3, 0.4, 2.7)),              # padded shoulder yokes
        b(WEB, -3.5, 3.2, -2.8, 3.5, 4.2, -2.4),                   # sternum strap
        b(BRIGHT, -1.1, 2.9, -3.1, 1.1, 4.5, -2.7),                # quick-release buckle
        b(WEB, -4.4, 9.0, -2.6, 4.4, 11.0, 2.6),                   # padded waist belt
        b(BRIGHT, -1.2, 8.8, -2.9, 1.2, 11.2, -2.6),               # cobra buckle
        *sym(b(POUCH, 1.8, 9.2, -3.4, 3.8, 11.4, -2.6)),           # magazine pouches
        *sym(b(POUCH, 3.9, 8.4, -1.6, 5.0, 11.6, 1.0)),            # hip utility pouches
        *sym(b(GAUGE, 1.9, 5.0, -2.9, 3.0, 6.0, -2.6)),            # D-rings
        b(RAIL, -3.0, 1.0, 2.0, 3.0, 9.4, 2.5),                    # pack mounting plate
    ]


# ------------------------------------------------------------------ 1. mage unit (abdomen orb + strut)
def mage_body():
    boxes = [
        *sym(b(WEB, 1.3, -0.2, -2.6, 3.5, 4.2, -2.0)),
        *sym(b(WEB, 1.1, -0.8, -2.7, 4.3, 0.4, 2.7)),
        b(WEB, -4.4, 11.0, -2.6, 4.4, 12.4, 2.6),                  # lower hip belt
        b(HOUSING, -3.6, 4.2, -5.4, 3.6, 11.2, -2.0),              # computation-orb engine housing
        b(COWL, -3.0, 3.0, -5.2, 3.0, 4.4, -2.2),                  # valve hood
        *sym(b(COWL, 0.8, 1.8, -5.0, 2.8, 3.2, -2.6)),             # twin intake scoops
        *sym(b(RAIL, 3.4, 4.8, -5.0, 4.4, 10.8, -2.2)),            # louver frames
        *[f for y in (5.2, 6.6, 8.0, 9.4) for f in sym(b(RAIL, 4.4, y, -4.8, 4.8, y + 0.5, -2.4))],
        *sym(b(HOSE, 3.5, 5.4, -2.8, 4.5, 6.8, 2.4)),              # mana feed conduits to the back
        *sym(b(GAUGE, 3.2, 3.2, -4.8, 4.4, 5.2, -2.8)),            # calibration dials
        b(BRIGHT, -2.5, 5.4, -5.9, 2.5, 10.4, -5.3),               # bezel
        b(BRIGHT, -2.0, 5.9, -6.3, 2.0, 9.9, -5.8),
        *[f for y in (5.5, 9.8) for f in sym(b(GAUGE, 1.9, y, -6.1, 2.4, y + 0.5, -5.8))],  # bezel bolts
        b(SKIRT, -3.2, 11.0, -5.0, 3.2, 13.4, -1.6),               # keel skirt
        b(FRAME, -3.8, 1.8, 2.0, 3.8, 10.0, 4.4),                  # rear manifold
        b(TANK_L, -1.8, 1.0, 4.4, 1.8, 10.5, 6.2),                 # boiler cylinder
        *[b(RAIL, -2.0, y, 4.2, 2.0, y + 0.4, 6.4) for y in (2.4, 5.2, 8.0)],  # cylinder bands
        b(RAIL, -0.4, 2.4, 6.2, 0.4, 9.4, 6.9),                    # spine cooling fin
        *sym(b(NOZ_A, 0.8, 9.8, 4.4, 2.8, 11.8, 5.8)),             # exhaust vents
        *sym(b(CORE, 1.1, 11.82, 4.6, 2.5, 11.92, 5.6)),
        b(RAIL, 2.6, -4.0, 3.0, 3.0, 1.8, 3.4),                    # comms whip antenna
    ]
    crystal = P("mana_crystal", [b(GLASS, -1.4, -1.4, -0.35, 1.4, 1.4, 0.35)], (0.0, 7.9, -6.35))
    belly = P("belly_nozzles", [
        b(NOZ_C, -2.4, 0.0, -1.1, -0.6, 1.4, 1.1), b(NOZ_D, 0.6, 0.0, -1.1, 2.4, 1.4, 1.1),
        *sym(b(CORE, 0.8, 1.42, -0.9, 2.2, 1.52, 0.9), swap=False),
    ], (0.0, 13.2, -3.4))
    return P("body", boxes, children=[crystal, belly], var="body")


def strut_leg_right():
    boxes = [
        b(LEG, -2.4, 0.6, -2.4, 2.4, 2.0, 2.4),                    # thigh cuff
        b(WEB, -2.5, 3.0, -2.5, 2.5, 3.8, 2.5),                    # thigh strap
        b(LEG_STRUT, -3.2, 1.6, -1.5, -2.3, 6.4, -0.5),            # twin outer struts
        b(LEG_STRUT2, -3.2, 1.6, 0.5, -2.3, 6.4, 1.5),
        b(KNEE, -3.5, 5.6, -1.7, -2.1, 7.8, 1.7),                  # knee actuator housing
        b(GAUGE, -3.9, 6.0, -0.8, -3.5, 7.4, 0.8),                 # knee motor cap
        b(KNEE, -1.7, 5.4, -2.8, 1.7, 7.4, -2.1),                  # knee cap
        b(RAIL, -0.8, 3.8, 2.1, 0.8, 9.8, 3.0),                    # rear damper body
        b(BRIGHT, -0.35, 2.2, 2.3, 0.35, 3.9, 2.8),                # damper rod
        b(SHIN, -3.1, 7.8, -1.0, -2.2, 10.9, 1.0),                 # shin rail
        b(CUFF, -2.4, 8.6, -2.4, 2.4, 9.8, 2.4),                   # shin cuff
        b(LEG_STRUT2, -3.3, 8.2, -1.8, -2.5, 10.8, -1.0),          # ankle linkage
        b(GLASS, -3.25, 8.0, 0.2, -3.05, 9.4, 0.8),                # status light
        b(SOLE, -2.6, 11.6, -3.8, 2.0, 12.8, 3.8),                 # stirrup sole
        b(TOE, -2.4, 10.4, -5.6, 1.8, 11.9, -3.7),                 # toe guard
        b(SOLE, -2.7, 10.8, -2.2, -2.2, 12.2, 2.0),                # foot clamps
        b(SOLE, 1.9, 10.8, -2.2, 2.4, 12.2, 2.0),
    ]
    heel = P("heel_nozzle", [
        b(NOZ_HEEL, -1.3, 0.0, -1.25, 1.3, 2.4, 1.25),
        b(RAIL, -1.5, 0.4, -1.4, 1.5, 0.8, 1.4),                   # heat-shield collar
        b(CORE, -0.9, 2.42, -0.85, 0.9, 2.52, 0.85),
    ], (-0.4, 10.0, 4.85))
    return P("right_leg", boxes, (-1.9, 12.0, 0.0), [heel], var="rightLeg")


# ------------------------------------------------------------------ 2. twin-turbojet backpack
def jetpack():
    boxes = [
        b(RAIL, -4.0, 0.8, 2.5, 4.0, 10.4, 3.0),                   # frame backplate
        b(RAIL, -4.6, 0.2, 2.6, 4.6, 0.8, 5.6),                    # top crossbar
        b(TANK_L, -4.4, 1.4, 3.0, -1.0, 10.0, 6.4), b(TANK_R, 1.0, 1.4, 3.0, 4.4, 10.0, 6.4),  # turbine casings
        *sym(b(COWL, 0.7, 0.6, 2.7, 4.7, 1.6, 6.7)),               # intake lips
        *[f for y in (3.4, 7.4) for f in sym(b(RAIL, 0.8, y, 2.8, 4.6, y + 0.5, 6.6))],  # compressor bands
        *sym(b(HOSE, 4.4, 2.2, 4.2, 4.9, 8.6, 4.9)),               # bleed-air lines
        b(PANEL, -1.0, 2.6, 3.0, 1.0, 9.0, 5.6),                   # fuel control module
        b(HOSE, -1.6, 4.4, 5.0, 1.6, 5.2, 5.8),                    # crossfeed
        b(GAUGE, -0.9, 3.2, 5.6, 0.9, 5.0, 6.1),                   # gauge cluster
        *sym(b(RAIL, 1.0, 9.8, 2.9, 4.4, 10.6, 6.5)),              # exhaust heat shields
        *sym(b(RAIL, 1.3, 10.0, 4.2, 4.1, 10.6, 5.2)),             # gimbal yokes
        *sym(b(RAIL, 4.4, 8.0, -1.2, 5.2, 10.0, 0.4)),             # hip throttle grips
        *sym(b(GAUGE, 4.3, 7.4, -1.4, 5.3, 8.0, 0.6)),
    ]
    nozzle = lambda name, uv, x: P(name, [
        b(uv, -1.3, 0.0, -1.3, 1.3, 2.4, 1.3),
        b(uv, -1.6, 0.6, -1.6, 1.6, 1.3, 1.6),                     # actuator ring
        b(CORE, -1.0, 2.42, -1.0, 1.0, 2.52, 1.0),
    ], (x, 10.5, 4.7))
    fan = lambda name, x: P(name, [
        b(GAUGE, -1.5, -0.2, -0.25, 1.5, 0.0, 0.25),
        b(GAUGE, -0.25, -0.2, -1.5, 0.25, 0.0, 1.5),
        b(NOZ_A, -0.4, -0.4, -0.4, 0.4, 0.0, 0.4),
    ], (x, 0.6, 4.7))
    return P("back_jetpack", boxes, children=[nozzle("nozzle_left", NOZ_A, -2.7), nozzle("nozzle_right", NOZ_B, 2.7),
                                              fan("fan_left", -2.7), fan("fan_right", 2.7)], var="backJetpack")


# ------------------------------------------------------------------ 3. delta glider-jet
def wings():
    boxes = [
        b(AERO, -3.0, 1.6, 2.4, 3.0, 10.2, 5.0),                   # fuselage / avionics bay
        b(NACELLE_L, -2.0, 1.0, 5.0, 2.0, 8.0, 6.0),               # dorsal spine hump
        *sym(b(AERO, 2.0, 0.6, 2.2, 3.8, 3.0, 4.8)),               # shoulder intakes
        *sym(b(GAUGE, 2.4, 3.0, 2.6, 3.6, 4.6, 3.6)),              # wing root hinges
        b(AERO, -0.5, -1.2, 5.0, 0.5, 3.6, 6.2),                   # vertical stabilizer root
        b(NOZ_B, -1.4, 10.2, 3.0, 1.4, 12.0, 5.0),                 # main sustainer nozzle
        b(CORE, -1.0, 12.02, 3.4, 1.0, 12.12, 4.6),
        b(GLASS, -0.6, 2.4, 5.95, 0.6, 3.4, 6.05),                 # formation light
    ]
    rudder = P("rudder", [b(AERO, -0.45, -3.4, 0.0, 0.45, 3.4, 1.6)], (0.0, 0.0, 6.2),
               [P("strobe", [b(STROBE, -0.35, -0.7, -0.35, 0.35, 0.0, 0.35)], (0.0, -3.4, 0.8))])
    right_wing = P("right_wing", [  # right_wing sits at +x (entity's left = port, red)
        b(WING_R, 0.0, -0.6, 0.0, 9.5, 2.6, 0.7),                  # wing skin
        b(NACELLE_R, 0.0, -0.9, -0.1, 9.5, -0.4, 0.9),             # leading edge
        b(NACELLE_R, 4.8, -0.9, -0.4, 5.2, 2.4, 1.2),              # wing fence
        b(NACELLE_R, 8.0, -1.4, -0.8, 10.0, 3.2, 1.6),             # wingtip micro-jet nacelle
        b(NOZ_B, 8.3, 3.2, -0.5, 9.7, 3.8, 1.3),
        b(CORE, 8.5, 3.82, -0.3, 9.5, 3.92, 1.1),
        b(NAV_R, 10.0, -1.6, 0.1, 10.6, -1.0, 0.7),
    ], (3.0, 3.5, 2.8), [P("flap", [b(NACELLE_R, 0.0, 0.0, -0.25, 4.2, 1.3, 0.25)], (2.2, 2.6, 0.35))])
    left_wing = mirror_part(right_wing, "left_wing")
    return P("tactical_wings", boxes, children=[rudder, left_wing, right_wing], var="tacticalWings")


# ------------------------------------------------------------------ 4. heavy rocket pack
def heavy():
    boxes = [
        b(FRAME, -4.4, 0.8, 2.2, 4.4, 11.0, 3.0),                  # armored frame
        b(TANK_BIG_L, -5.4, -0.6, 3.0, -1.0, 11.4, 7.4), b(TANK_BIG_R, 1.0, -0.6, 3.0, 5.4, 11.4, 7.4),
        *sym(b(FRAME, 1.4, -1.4, 3.4, 5.0, -0.6, 7.0)),            # domed caps
        *[f for y in (2.2, 8.2) for f in sym(b(RAIL, 0.8, y, 2.8, 5.6, y + 0.6, 7.6))],  # tank bands
        *sym(b(FRAME2, 5.6, 0.4, 3.0, 6.2, 11.4, 3.6)),            # roll cage uprights
        *sym(b(FRAME2, 5.6, 0.4, 6.8, 6.2, 11.4, 7.4)),
        b(FRAME2, -6.2, -1.8, 6.8, 6.2, -1.2, 7.4),                # roll-over bar
        *sym(b(NOZ_BIG_L, 5.6, 1.0, 4.6, 6.4, 2.2, 5.8)),          # RCS quads
        b(HOSE, -1.6, 4.0, 4.2, 1.6, 5.0, 5.2), b(HOSE, -1.6, 7.0, 4.2, 1.6, 8.0, 5.2),  # equalizer lines
        b(FRAME, -3.6, 9.8, 2.4, 3.6, 12.6, 3.2),                  # blast deflector
        b(NAV_R, -0.3, -2.4, 6.9, 0.3, -1.8, 7.3),                 # hazard beacon
    ]
    nozzle = lambda name, uv, ring, x: P(name, [
        b(uv, -1.7, 0.0, -1.7, 1.7, 3.0, 1.7),
        b(ring, -2.0, 1.6, -2.0, 2.0, 2.2, 2.0),                   # turbopump collar
        b(CORE, -1.3, 3.02, -1.3, 1.3, 3.12, 1.3),
    ], (x, 11.4, 5.2))
    return P("heavy_tanks", boxes, children=[nozzle("nozzle_left", NOZ_BIG_L, TANK_BIG_L, -3.2),
                                             nozzle("nozzle_right", NOZ_BIG_R, TANK_BIG_R, 3.2)], var="heavyTanks")


# ------------------------------------------------------------------ 5. Type 95 twin-core exoskeleton
def twin_drive():
    boxes = [
        *sym(b(WEB, 1.3, -0.2, -2.6, 3.5, 4.2, -2.0)),
        *sym(b(WEB, 1.1, -0.8, -2.7, 4.3, 0.4, 2.7)),
        b(WEB, -4.4, 11.0, -2.6, 4.4, 12.4, 2.6),
        b(FRAME, -3.6, 1.8, 2.1, 3.6, 10.0, 4.6),                  # high-output injection manifold
        *[b(RAIL, -2.8, y, 4.6, 2.8, y + 0.4, 5.4) for y in (2.6, 4.0, 5.4, 6.8, 8.2)],  # heat-sink fins
        b(HOUSING, -3.8, 4.2, -5.4, 3.8, 11.4, -2.0),              # twin-core housing
        b(COWL, -3.2, 3.0, -5.2, 3.2, 4.4, -2.2),
        *sym(b(RAIL, 3.6, 4.8, -5.0, 4.4, 10.8, -2.2)),
        *sym(b(HOSE, 3.5, 5.8, -2.5, 4.3, 7.2, 2.1)),
        b(BRIGHT, -3.4, 5.4, -5.8, 3.4, 10.2, -5.3),               # double bezel
        *sym(b(GLASS, 0.5, 6.0, -6.3, 2.9, 9.6, -5.6), swap=False),  # synchronized cores
        b(BRIGHT, -0.4, 6.6, -6.2, 0.4, 9.0, -5.6),                # resonance coupler
        b(NOZ_C, -2.6, 12.8, -4.4, -0.8, 14.0, -2.4), b(NOZ_D, 0.8, 12.8, -4.4, 2.6, 14.0, -2.4),
        *sym(b(CORE, 1.0, 14.02, -4.2, 2.4, 14.12, -2.6), swap=False),
    ]
    radiator = lambda name, x: P(name, [
        b(COWL, -0.8, -4.2, -1.1, 0.8, 0.0, 1.1),
        b(CORE, -0.6, -3.9, 1.12, 0.6, -0.3, 1.22),
        *[b(RAIL, -1.0, y, -1.2, 1.0, y + 0.3, 1.2) for y in (-3.6, -2.4, -1.2)],  # fin stack
    ], (x, 2.4, 3.3))
    injectors = P("injectors", [
        *[b(NOZ_A, x, 0.0, -0.9, x + 1.8, 2.2, 0.9) for x in (-3.0, -0.9, 1.2)],
        *[b(CORE, x + 0.3, 2.22, -0.6, x + 1.5, 2.32, 0.6) for x in (-3.0, -0.9, 1.2)],
    ], (0.0, 10.0, 3.5))
    return P("twin_drive_torso", boxes, children=[radiator("radiator_left", -4.0), radiator("radiator_right", 4.0), injectors],
             var="twinDrive")


# ------------------------------------------------------------------ 6. Juggernaut siege frame
def siege():
    boxes = [
        b(FRAME, -4.6, 0.8, 2.2, 4.6, 11.0, 5.2),                  # reactor housing
        b(RAIL, -0.8, 1.4, 5.2, 0.8, 10.6, 6.4),                   # central heat-sink column
        *sym(b(FRAME, 2.6, -3.0, -1.8, 5.0, 1.0, 4.4)),            # over-shoulder recoil gantries
        *sym(b(RAIL, 3.4, 1.0, 2.2, 4.4, 3.0, 3.0)),
        b(FRAME2, -5.2, -5.4, -1.6, -2.4, -3.0, 3.6),              # shoulder rocket pod (right)
        *[b(GAUGE, x, -5.0, -1.9, x + 0.8, -4.2, -1.6) for x in (-4.9, -4.0, -3.1)],  # launch tubes
        *[b(GAUGE, x, -4.0, -1.9, x + 0.8, -3.2, -1.6) for x in (-4.9, -4.0, -3.1)],
        b(HOUSING, -4.2, 2.2, -3.4, 4.2, 10.8, -2.0),              # chest mantlet
        *[b(COWL, x, y, -3.8, x + 3.6, y + 2.6, -3.4) for x in (-3.8, 0.2) for y in (2.8, 5.8)],  # reactive armor tiles
        b(BRIGHT, -0.8, 8.8, -3.9, 0.8, 10.2, -3.4),
        b(SKIRT, -3.6, 10.8, -3.0, 3.6, 12.6, -2.0),
        b(FRAME2, -4.6, 11.0, 2.6, -3.2, 14.6, 5.2), b((10, 110), 3.2, 11.0, 2.6, 4.6, 14.6, 5.2),  # landing skids
        *sym(b(RAIL, 3.0, 14.2, 2.0, 4.8, 14.8, 6.0)),
    ]
    thrusters = P("thrusters", [
        *[b(NOZ_BIG_L if x < 0 else NOZ_BIG_R, x, y, 0.0, x + 3.2, y + 3.2, 2.2) for x in (-4.2, 1.0) for y in (-3.8, 0.6)],
        *[b(RAIL, x - 0.2, y - 0.2, 1.4, x + 3.4, y + 3.4, 1.8) for x in (-4.2, 1.0) for y in (-3.8, 0.6)],  # nozzle lips
        *[b(CORE, x + 0.4, y + 0.4, 2.22, x + 2.8, y + 2.8, 2.32) for x in (-4.2, 1.0) for y in (-3.8, 0.6)],
    ], (0.0, 6.2, 5.2))
    sensors = P("sensors", [*sym(b(GLASS, 2.8, -0.9, -0.6, 4.6, 0.9, 0.2), swap=False),
                            *sym(b(GAUGE, 2.6, -1.2, -0.3, 4.8, -0.8, 0.6), swap=False)], (0.0, -1.3, -1.8))
    return P("siege_frame", boxes, children=[thrusters, sensors], var="siege")


# ------------------------------------------------------------------ 7. Valkyrie thrust boots
def boot_right():
    boxes = [
        b(WEB, -2.3, 2.0, -2.3, 2.3, 3.0, 2.3),                    # thigh strap
        b(KNEE, -2.0, 4.6, -2.8, 2.0, 6.8, -2.0),                  # knee guard
        b(LEG, -2.4, 6.0, -2.4, 2.4, 11.2, 2.4),                   # shin greave
        b(KNEE, -1.0, 6.2, -2.9, 1.0, 10.6, -2.4),                 # front ridge
        b(AERO, -3.6, 6.5, -0.6, -2.4, 10.4, 3.2),                 # stabilization winglet
        b(GLASS, -2.75, 6.6, -1.6, -2.45, 9.6, -1.0),              # charge indicator
        b(GAUGE, -2.9, 10.4, -0.8, -2.3, 11.8, 0.8),               # ankle actuator
        b(SOLE, -2.4, 11.4, -3.6, 2.4, 12.6, 2.8),
        b(TOE, -2.4, 10.6, -4.6, 2.0, 12.1, -2.4),
        b(NOZ_HEEL, -1.9, 11.2, 0.5, 1.9, 12.2, 4.0),              # heel absorber
    ]
    nozzle = P("nozzle", [
        b(NOZ_A, -1.8, 0.0, -1.4, 1.8, 4.5, 1.4),
        b(RAIL, -1.4, 0.4, 1.4, 1.4, 2.6, 1.8),                    # intake grille
        b(NOZ_B, -1.4, 3.5, -1.1, 1.4, 5.5, 1.1),
        b(CORE, -1.0, 5.52, -0.8, 1.0, 5.62, 0.8),
    ], (0.0, 7.0, 3.8))
    return P("thrust_boots_right", boxes, (-1.9, 12.0, 0.0), [nozzle], var="bootRight")


# ------------------------------------------------------------------ 8. hydro skimmer
def skimmer_torso():
    return P("hydro_skimmer_torso", [
        b(HOUSING, -3.8, 1.0, -3.4, 3.8, 9.0, -2.0),               # flotation vest
        b(SKIRT, -3.4, -0.6, -3.0, 3.4, 1.0, -2.0),                # flotation collar
        b(TANK_L, -3.8, 1.5, 2.0, 3.8, 10.0, 5.2),                 # waterjet pump housing
        b(RAIL, -3.0, 9.2, 5.2, 3.0, 10.0, 5.6),                   # intake grille
        *sym(b(NOZ_B, 0.8, 5.2, 5.2, 3.2, 7.6, 7.4)),              # twin waterjets (rear-facing)
        *sym(b(CORE, 1.2, 5.6, 7.42, 2.8, 7.2, 7.52)),
        b(PANEL, -0.5, -0.8, 3.6, 0.5, 8.4, 7.2),                  # dorsal stabilizer
        *sym(b(GLASS, 3.4, 2.0, -3.5, 3.8, 3.0, -3.3)),            # strobe/locator beacons
    ])


def ski_right():
    boxes = [
        b(WEB, -2.3, 4.0, -2.3, 2.3, 5.0, 2.3),                    # shin strap
        b(LEG, -3.4, 4.6, -1.0, -2.0, 10.6, 1.0),                  # outer mounting pylon
        b(SOLE, -2.2, 10.6, -2.4, 2.2, 11.8, 2.4),                 # foot binding
        b(LEG, -2.2, 11.6, -6.0, 2.2, 13.2, 7.0),                  # ski body
        b(BRIGHT, -0.3, 13.2, -5.0, 0.3, 13.6, 6.0),               # keel strip
        b(TOE, -2.0, 10.6, -7.8, 2.0, 12.6, -6.0),                 # upturned prow
        b(TOE, -1.6, 10.0, -8.6, 1.6, 11.0, -7.6),
    ]
    rudder = P("rudder", [b(WING_L, -0.3, 0.0, 0.0, 0.3, 1.4, 2.0)], (0.0, 10.2, 5.0))
    return P("hydro_skimmer_right", boxes, (-1.9, 12.0, 0.0), [rudder], var="hydroRight")


# ------------------------------------------------------------------ 9. scuba rig
def scuba():
    return P("tactical_scuba", [
        b(RAIL, -3.4, 0.6, 2.0, 3.4, 10.4, 2.6),                   # backplate
        b(TANK_BIG_L, -4.4, -0.4, 2.6, -0.6, 11.6, 6.4), b(TANK_BIG_R, 0.6, -0.4, 2.6, 4.4, 11.6, 6.4),
        *sym(b(SKIRT, 0.8, 11.6, 2.8, 4.2, 12.4, 6.2)),            # tank boots
        b(WEB, -4.6, 3.0, 2.4, 4.6, 4.0, 6.6), b(WEB, -4.6, 8.0, 2.4, 4.6, 9.0, 6.6),  # cam bands
        *sym(b(BRIGHT, 2.0, -1.2, 3.9, 3.0, -0.4, 4.9)),           # valve necks
        b(RAIL, -2.6, -1.2, 4.1, 2.6, -0.6, 4.7),                  # isolation manifold
        *sym(b(BRIGHT, 1.6, -2.0, 4.0, 3.4, -1.6, 4.8)),           # valve knobs
        b(GAUGE, 2.2, -2.2, 2.8, 3.6, -1.0, 4.0),                  # first stage
        b(HOSE, -3.2, -1.6, -2.6, -2.0, -0.8, 3.6), b(HOSE, 2.0, -1.6, -2.6, 3.2, -0.8, 3.6),  # LP hoses
        b(HOUSING, -3.2, 3.2, -4.0, 3.2, 9.0, -2.2),               # scrubber canister
        b(GLASS, -1.2, 4.2, -4.6, 1.2, 6.6, -4.0),                 # depth gauge
        b(GAUGE, 3.8, 9.0, -1.8, 5.0, 10.6, -0.6), b(GLASS, 4.2, 9.3, -1.95, 4.8, 10.3, -1.8),  # SPG console
        *[f for x in (2.2, 0.2) for f in sym(b(SKIRT, x, 9.4, -3.0, x + 1.6, 11.6, -2.6))],  # lead weights
        b(WEB, -4.4, 9.6, -2.6, 4.4, 11.0, 2.6),
    ])


# ------------------------------------------------------------------ 10. CoD-AW style powered exoskeleton
def exo_torso():
    vertebrae = [b(BRIGHT if i % 2 else RAIL, -0.9 if i % 2 else -0.7, 0.6 + i * 1.3, 2.2, 0.9 if i % 2 else 0.7, 1.7 + i * 1.3, 3.4)
                 for i in range(8)]
    boxes = [
        b(TANK_L, -3.0, 0.5, 2.2, 3.0, 5.0, 4.6),                  # dorsal power pack
        b(RAIL, -3.2, 0.2, 4.6, 3.2, 0.8, 5.0),                    # pack heat-sink lid
        *[b(RAIL, -2.6, y, 4.6, 2.6, y + 0.3, 4.9) for y in (1.4, 2.4, 3.4)],  # vent slats
        b(GLASS, -2.4, 4.3, 4.62, 2.4, 4.6, 4.72),                 # charge bar
        *vertebrae,                                                # articulated spine
        *sym(b(FRAME, 3.1, -1.2, -2.2, 5.0, 0.4, 2.6)),            # shoulder bridge yokes
        *sym(b(RAIL, 1.0, 0.0, -2.6, 3.8, 1.0, -2.0)),             # clavicle bars
        b(KNEE, -1.5, 1.0, -2.7, 1.5, 4.2, -2.1),                  # sternum plate
        b(GLASS, -0.5, 1.6, -2.8, 0.5, 2.4, -2.65),                # power status LED
        *sym(b(HOSE, 1.6, 4.2, -2.4, 2.2, 8.4, -2.0)),             # rib actuator cables
        b(RAIL, -4.5, 9.0, -2.6, 4.5, 11.0, 2.6),                  # pelvic girdle
        b(KNEE, -2.5, 7.0, 2.2, 2.5, 10.0, 3.8),                   # lumbar battery
        *sym(b(GAUGE, 4.0, 9.4, -1.4, 4.8, 11.6, 1.4)),            # hip bearing plates
    ]
    thruster = lambda name, x: P(name, [
        b(NOZ_B, -0.8, 0.0, -0.8, 0.8, 1.6, 0.8),
        b(CORE, -0.6, 1.62, -0.6, 0.6, 1.72, 0.6),
    ], (x, 5.0, 3.4))
    return P("urban_exo_harness", boxes, children=[thruster("thruster_left", -2.2), thruster("thruster_right", 2.2)],
             var="exoHarness")


def exo_arm_right():
    boxes = [
        b(GAUGE, -3.9, -2.3, -1.9, -3.0, 1.3, 1.9),                # shoulder motor housing
        b(BRIGHT, -4.2, -1.3, -0.9, -3.9, 0.3, 0.9),               # motor hub cap
        b(FRAME, -3.4, -2.6, -2.3, 0.6, -1.9, 2.3),                # shoulder cap arch
        b(RAIL, -3.6, 1.0, -1.7, -3.0, 4.8, -1.1),                 # twin upper-arm rails
        b(RAIL, -3.6, 1.0, 1.1, -3.0, 4.8, 1.7),
        b(TANK_L, -2.0, 0.4, 2.0, -0.8, 4.5, 2.9),                 # triceps hydraulic cylinder
        b(GAUGE, -3.9, 4.5, -1.3, -2.9, 6.6, 1.3),                 # elbow actuator
        b(BRIGHT, -4.1, 5.1, -0.6, -3.9, 6.0, 0.6),
        b(KNEE, -2.4, 5.0, 2.0, 0.4, 6.6, 2.8),                    # elbow guard
        b(SHIN, -3.6, 6.6, -1.8, -3.0, 9.4, 1.8),                  # forearm frame
        b(HOSE, -3.2, 3.6, 1.8, -2.8, 8.8, 2.2),                   # power cable to wrist
        b(CUFF, -3.4, 8.8, -2.4, 1.4, 10.0, 2.4),                  # wrist cuff
        b(GLASS, -3.55, 9.0, -1.2, -3.4, 9.8, -0.4),               # wrist status light
    ]
    rod = P("rod", [b(BRIGHT, -0.3, 0.0, -0.3, 0.3, 2.0, 0.3)], (-1.4, 4.5, 2.45))
    return P("urban_exo_right_arm", boxes, (-5.0, 2.0, 0.0), [rod], var="exoRightArm")


def exo_leg_right():
    boxes = [
        b(GAUGE, -3.0, -0.5, -1.5, -2.1, 2.5, 1.5),                # hip motor
        b(BRIGHT, -3.3, 0.3, -0.7, -3.0, 1.7, 0.7),
        b(RAIL, -2.8, 2.5, -1.0, -2.1, 5.5, 1.0),                  # thigh rail
        b(KNEE, -1.8, 1.0, -2.6, 1.8, 5.0, -2.0),                  # thigh plate
        b(WEB, -2.3, 3.4, -2.3, 2.3, 4.2, 2.3),                    # thigh strap
        b(GAUGE, -3.0, 5.5, -1.4, -2.1, 7.8, 1.4),                 # knee actuator
        b(BRIGHT, -3.3, 6.1, -0.6, -3.0, 7.2, 0.6),
        b(KNEE, -1.5, 5.5, -2.8, 1.5, 7.3, -2.0),                  # knee cap
        b(TANK_L, -1.0, 4.5, 2.0, 1.0, 10.0, 3.0),                 # calf hydraulic cylinder
        b(SHIN, -2.8, 7.8, -0.8, -2.1, 10.2, 0.8),                 # shin rail
        b(LEG, -1.8, 7.5, -2.6, 1.8, 10.5, -2.0),                  # shin guard
        b(GLASS, -2.95, 8.2, -0.3, -2.8, 9.6, 0.3),
        b(GAUGE, -3.0, 10.2, -1.0, -2.1, 11.8, 1.0),               # ankle motor
        b(SOLE, -2.3, 11.6, -3.2, 2.3, 12.6, 2.6),                 # load-bearing sole plate
        b(TOE, -2.2, 11.0, -3.2, 2.2, 11.8, -2.4),                 # toe cap
        b(NOZ_HEEL, -1.2, 10.8, 2.0, 1.2, 11.6, 3.0),              # heel spring
    ]
    piston = P("piston", [b(BRIGHT, -0.4, 0.0, -0.4, 0.4, 2.5, 0.4)], (0.0, 2.0, 2.5))
    return P("urban_exo_right", boxes, (-1.9, 12.0, 0.0), [piston], var="exoRight")


# ------------------------------------------------------------------ 11. diving mask (head space)
def mask():
    return P("diving_mask", [
        b(POUCH, -4.4, -6.4, -4.6, 4.4, -2.0, -4.0),               # silicone face seal
        b(GLASS, -3.8, -6.0, -5.0, 3.8, -3.4, -4.4),               # panoramic visor
        b(BRIGHT, -4.2, -6.4, -5.1, 4.2, -6.0, -4.4), b(BRIGHT, -4.2, -3.4, -5.1, 4.2, -3.0, -4.4),
        *sym(b(BRIGHT, 3.8, -6.4, -5.1, 4.2, -3.0, -4.4)),
        b(HOUSING, -2.8, -3.2, -5.4, 2.8, 0.4, -4.0),              # oral-nasal rebreather
        *sym(b(BRIGHT, 2.8, -2.4, -5.0, 4.2, -0.2, -3.8)),         # regulator valves
        b(NOZ_A, -1.2, -1.0, -5.9, 1.2, 0.8, -5.3),                # purge / exhaust
        b(WEB, -4.5, -5.2, -4.2, 4.5, -4.2, 4.6), b(WEB, -4.5, -2.4, -3.8, 4.5, -1.6, 4.6),  # head straps
        b(GAUGE, -1.0, -8.8, -3.4, 1.0, -7.2, -1.6), b(GLASS, -0.8, -8.6, -4.4, 0.8, -7.4, -3.4),  # headlamp
        b(GAUGE, -4.6, -4.6, -1.0, -4.2, -2.6, 1.0),               # comms earpiece
    ])


PARTS = [
    P("harness", harness()),
    mage_body(),
    strut_leg_right(), mirror_part(strut_leg_right(), "left_leg"),
    jetpack(), wings(), heavy(), twin_drive(), siege(),
    boot_right(), mirror_part(boot_right(), "thrust_boots_left"),
    skimmer_torso(), ski_right(), mirror_part(ski_right(), "hydro_skimmer_left"),
    scuba(),
    exo_torso(), exo_arm_right(), mirror_part(exo_arm_right(), "urban_exo_left_arm"),
    exo_leg_right(), mirror_part(exo_leg_right(), "urban_exo_left"),
    mask(),
]


# ------------------------------------------------------------------ GeckoLib export
GEO_DIR = os.path.join(ROOT, "src/main/resources/assets/youjosenki/geo")
ARMOR_BONES = {  # GeoArmorRenderer bone -> bedrock pivot (humanoid joints)
    "armorHead": (0, 24, 0), "armorBody": (0, 24, 0), "armorRightArm": (-5, 22, 0), "armorLeftArm": (5, 22, 0),
    "armorRightLeg": (-1.9, 12, 0), "armorLeftLeg": (1.9, 12, 0), "armorRightBoot": (-1.9, 12, 0), "armorLeftBoot": (1.9, 12, 0),
}
MOUNT = {"right_leg": "armorRightLeg", "thrust_boots_right": "armorRightLeg", "hydro_skimmer_right": "armorRightLeg",
         "urban_exo_right": "armorRightLeg", "left_leg": "armorLeftLeg", "thrust_boots_left": "armorLeftLeg",
         "hydro_skimmer_left": "armorLeftLeg", "urban_exo_left": "armorLeftLeg",
         "urban_exo_right_arm": "armorRightArm", "urban_exo_left_arm": "armorLeftArm", "diving_mask": "armorHead"}
# FlightDesign -> parts it renders (geo file name = design in lower case)
DESIGNS = {
    "MAGE_UNIT": ["body", "right_leg"], "BACK_JETPACK": ["harness", "back_jetpack"],
    "TACTICAL_WINGS": ["harness", "tactical_wings"], "HEAVY_ROCKET": ["harness", "heavy_tanks"],
    "TWIN_DRIVE_EXO": ["twin_drive_torso", "right_leg", "left_leg"], "SIEGE_ARTILLERY": ["harness", "siege_frame"],
    "THRUST_BOOTS": ["harness", "thrust_boots_right", "thrust_boots_left"],
    "HYDRO_SKIMMER": ["harness", "hydro_skimmer_torso", "hydro_skimmer_right", "hydro_skimmer_left"],
    "TACTICAL_SCUBA": ["harness", "tactical_scuba"],
    "URBAN_EXO_LEGS": ["urban_exo_harness", "urban_exo_right_arm", "urban_exo_left_arm", "urban_exo_right", "urban_exo_left"],
    "DIVING_MASK": ["diving_mask"],
}
BY_NAME = {p.name: p for p in PARTS}


def r3(v):
    return [round(x, 3) for x in v]


def geo_bones(p, parent, origin, out, name=None):
    """Java model space (y down) -> bedrock (y up, feet at 0): X = x, Y = 24 - y, Z = z."""
    o = tuple(origin[i] + p.pivot[i] for i in range(3))
    name = name or p.name
    cubes = []
    for uv, lo, hi in p.boxes:
        size = tuple(hi[i] - lo[i] for i in range(3))
        check_uv(uv, size, name)
        cubes.append({"origin": r3((lo[0] + o[0], 24 - (hi[1] + o[1]), lo[2] + o[2])), "size": r3(size), "uv": list(uv)})
    out.append({"name": name, "parent": parent, "pivot": r3((o[0], 24 - o[1], o[2])), "cubes": cubes})
    for c in p.children:
        geo_bones(c, name, o, out, name + "_" + c.name)


def write_geo():
    os.makedirs(GEO_DIR, exist_ok=True)
    names = {}
    for design, parts in DESIGNS.items():
        bones = [{"name": n, "pivot": list(pv)} for n, pv in ARMOR_BONES.items()]
        for part in parts:
            geo_bones(BY_NAME[part], MOUNT.get(part, "armorBody"), (0, 0, 0), bones)
        assert len({bn["name"] for bn in bones}) == len(bones), design
        names[design] = [bn["name"] for bn in bones]
        geo = {"format_version": "1.12.0", "minecraft:geometry": [{
            "description": {"identifier": "geometry." + design.lower(), "texture_width": 128, "texture_height": 128,
                            "visible_bounds_width": 4, "visible_bounds_height": 3.5, "visible_bounds_offset": [0, 1.25, 0]},
            "bones": bones}]}
        with open(os.path.join(GEO_DIR, design.lower() + ".geo.json"), "w") as fh:
            json.dump(geo, fh, separators=(",", ":"))
    return names


def check_uv(uv, size, where):
    w, h, d = size
    assert uv[0] + 2 * d + 2 * w <= 128.01 and uv[1] + d + h <= 128.01, ("UV out of bounds", where, uv, size)


def flatten(p, origin=(0, 0, 0), acc=None):
    o = tuple(origin[i] + p.pivot[i] for i in range(3))
    for uv, lo, hi in p.boxes:
        acc.append({"part": p.name, "uv": uv, "lo": [lo[i] + o[i] for i in range(3)], "hi": [hi[i] + o[i] for i in range(3)]})
    for c in p.children:
        flatten(c, o, acc)


if __name__ == "__main__":
    names = write_geo()
    print("wrote %d geo models, %d boxes" % (len(names), sum(len(p.boxes) for p in PARTS)))
    for d, n in names.items():
        print(" ", d, ":", ", ".join(x for x in n if not x.startswith("armor")))
    if len(sys.argv) > 1:
        dump = {}
        for p in PARTS:
            acc = []
            flatten(p, acc=acc)
            dump[p.name] = acc
        json.dump(dump, open(sys.argv[1], "w"))
