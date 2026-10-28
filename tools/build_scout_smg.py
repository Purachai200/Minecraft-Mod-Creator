#!/usr/bin/env python3
"""Light Recon SMG for the SR-07 Scout: one part list, placed three ways in scout_titan.geo.json
(in the right hand on the `weapon` bone, slung barrel-up on the back on `weaponBack`), then
tools/build_cockpit_assets.py copies the hand version into the first-person rig.

Run from the repo root:  python3 tools/build_scout_smg.py && python3 tools/build_cockpit_assets.py
"""
import json
import os
import sys

from build_cockpit_assets import box_to_face_uv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scratch'))
import build_scout_assets as SCOUT  # noqa: E402  (sets up the Scout bone list on the shared Trooper builder)

GEO = 'Titan Combat/src/main/resources/assets/titancombat/geo/scout_titan.geo.json'

# Material patches in the scout atlas, borrowed from the largest Scout cube of each material
# (build_trooper_assets.swatch), so redesigning the Scout never leaves the SMG pointing at stale pixels.
# Faces are mapped per face into these, so any cube size reads only its own material.
MAT_SOURCE = {
    'paint': 'paint',      # chassis colour
    'accent': 'paint2',    # scheme accent (orange on Recon)
    'dark': 'dark',        # gunmetal
    'metal': 'metal',
    'steel': 'steel',
    'hazard': 'hazard',
    'vent': 'vent',
    'lens': 'visor',       # visor glow
}


def _patches():
    SCOUT.T.pack()
    return {k: SCOUT.T.swatch(m) for k, m in MAT_SOURCE.items()}


MAT = _patches()

# Parts in the gun's own frame, relative to the grip: x along the barrel, y up (optic side), z across.
# (x0, x1, y0, y1, z0, z1, material)
def _both_sides(x0, x1, y0, y1, z0, z1, mat):
    """A side detail and its mirror on the other side of the gun."""
    return [(x0, x1, y0, y1, z0, z1, mat), (x0, x1, y0, y1, -z1, -z0, mat)]


# Stockless bullpup-style SMG: a full-length upper tube over a slotted lower receiver, a U-shaped
# carry loop over the magazine well, a long straight magazine, ribbed foregrip and an angled grip.
PARTS = [
    # Upper tube (octagonal section), front cap with green sight lens
    (-2, 30, 3.5, 7.5, -2.5, 2.5, 'metal'),
    (-2, 30, 3, 8, -2, 2, 'metal'),
    (29.6, 30.4, 3.6, 7.4, -1.8, 1.8, 'metal'),
    (30.4, 30.8, 4.6, 6.4, -1, 1, 'lens'),
    # Rounded rear housing with a slotted take-down knob on each side
    (-6, -2, -1, 8, -2.8, 2.8, 'paint'),
    (-5.6, -2, 8, 9, -2.4, 2.4, 'paint'),
    (-4.8, -2, 9, 9.5, -1.8, 1.8, 'paint'),
    *_both_sides(-5, -2.6, 4.2, 6.6, 2.8, 3.4, 'dark'),
    *_both_sides(-4, -3.6, 4.4, 6.4, 3.4, 3.6, 'metal'),
    # Lower receiver with long side slots, bolt slot and charging knob, stepped nose
    (-2, 26, -2, 3, -2.5, 2.5, 'paint'),
    (26, 29, -1, 3, -2, 2, 'paint'),
    *_both_sides(14, 25, 0.4, 1.2, 2.5, 2.7, 'dark'),
    *_both_sides(15, 28, 5, 5.6, 2.5, 2.7, 'dark'),
    (-1, 9, 1.4, 2.2, 2.5, 2.7, 'dark'),
    (2, 4, 0.8, 2.8, 2.7, 4, 'metal'),
    (0, 2, 3, 3.6, 1.5, 2.6, 'metal'),                    # sight notch
    # U-shaped carry loop over the magazine well
    *_both_sides(9.5, 14, 0, 10.8, 3.2, 3.8, 'metal'),
    (9.5, 14, 10.2, 10.8, -3.8, 3.8, 'metal'),
    # Magazine well with three grooves, long straight magazine with a spine groove and base plate
    (10, 15, -7, -2, -2.8, 2.8, 'paint'),
    *[p for y in (-3, -4.5, -6) for p in _both_sides(10.6, 14.4, y, y + 0.6, 2.8, 3, 'dark')],
    (11, 14, -19, -7, -2, 2, 'dark'),
    *_both_sides(12.2, 12.8, -18, -8, 2, 2.2, 'metal'),
    (10.6, 14.4, -20, -19, -2.3, 2.3, 'accent'),
    # Under-rail with teeth, sling loop, ribbed vertical foregrip
    (17, 28, -3, -2, -1.8, 1.8, 'metal'),
    *[(x, x + 1, -3.6, -3, -1.5, 1.5, 'dark') for x in (18, 20.5, 23, 25.5)],
    (19.5, 23.5, -2.6, -1.6, 2, 2.3, 'metal'),
    (20.5, 22.5, -12, -3.6, -1.8, 1.8, 'dark'),
    *[(20, 23, y, y + 0.6, -2, 2, 'metal') for y in (-11.6, -10.4, -9.2)],
    # Barrel under the tube, muzzle ring with a side port
    (26, 33, 0, 2.5, -1.2, 1.2, 'steel'),
    (32, 34, -0.3, 2.8, -1.6, 1.6, 'dark'),
    (32.4, 33.4, 1, 1.5, 1.6, 1.7, 'metal'),
    # Trigger guard and trigger
    (2, 8, -4, -3.4, -0.5, 0.5, 'metal'),
    (7.4, 8, -4, -2, -0.5, 0.5, 'metal'),
    (4.5, 5.2, -3.6, -2, -0.3, 0.3, 'metal'),
    # Faceted pistol grip raked back, flared heel
    *[(-2.4 - 0.7 * i, 1 - 0.7 * i, -4 - 2 * i, -2 - 2 * i, -2, 2, 'dark') for i in range(5)],
    (-6.5, -1.5, -12.6, -11.6, -2.3, 2.3, 'dark'),
]
MUZZLE_X = 34

HAND_GRIP = (-19.8, 39.8, 10.3)    # weapon bone pivot in the right hand
BACK_GRIP = (-18.0, 62.0, 24.0)    # where the grip sits when slung on the back


def cube(lo, hi, mat):
    uv, patch = MAT[mat]
    return {'origin': [round(v, 3) for v in lo], 'size': [round(h - l, 3) for l, h in zip(lo, hi)],
            'uv': box_to_face_uv(uv, patch)}


def hand_cubes():
    gx, gy, gz = HAND_GRIP
    return [cube((gx + x0, gy + y0, gz + z0), (gx + x1, gy + y1, gz + z1), m) for x0, x1, y0, y1, z0, z1, m in PARTS]


def back_cubes():
    """Barrel up the back (gun x -> +y), optic toward the spine (gun y -> +x), across stays across (z),
    so the magazine points out over the right shoulder blade instead of into the hull."""
    gx, gy, gz = BACK_GRIP
    out = [cube((gx + y0, gy + x0, gz + z0), (gx + y1, gy + x1, gz + z1), m) for x0, x1, y0, y1, z0, z1, m in PARTS]
    out += [cube((-21, 66, 15), (-15, 80, 20), 'metal'),            # back mount
            cube((-22, 68, 19.4), (-14, 69.5, 28.6), 'dark'),        # clamp straps
            cube((-22, 76, 19.4), (-14, 77.5, 28.6), 'dark')]
    return out


def _selfcheck():
    xs = [p[0] for p in PARTS] + [p[1] for p in PARTS]
    assert max(xs) == MUZZLE_X, max(xs)
    assert all(p[0] < p[1] and p[2] < p[3] and p[4] < p[5] for p in PARTS)
    # Slung on the back the gun must stay behind the hull's back face (z 15)
    assert min(c['origin'][2] for c in back_cubes()) >= 15


def main():
    _selfcheck()
    with open(GEO) as f:
        geo = json.load(f)
    bones = {b['name']: b for b in geo['minecraft:geometry'][0]['bones']}
    bones['weapon']['cubes'] = hand_cubes()
    bones['weaponBack']['cubes'] = back_cubes()
    with open(GEO, 'w') as f:
        json.dump(geo, f, indent=2)
    print(f'Wrote {GEO}: {len(PARTS)} SMG parts')


if __name__ == '__main__':
    main()
