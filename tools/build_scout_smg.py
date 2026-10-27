#!/usr/bin/env python3
"""Light Recon SMG for the SR-07 Scout: one part list, placed three ways in scout_titan.geo.json
(in the right hand on the `weapon` bone, slung barrel-up on the back on `weaponBack`), then
tools/build_cockpit_assets.py copies the hand version into the first-person rig.

Run from the repo root:  python3 tools/build_scout_smg.py && python3 tools/build_cockpit_assets.py
"""
import json

from build_cockpit_assets import box_to_face_uv

GEO = 'Titan Combat/src/main/resources/assets/titancombat/geo/scout_titan.geo.json'

# Existing material patches in the scout atlas: (uv, size of the cube that owns the patch).
# Faces are mapped per face into these, so any cube size reads only its own material.
MAT = {
    'paint': ([174, 48], [10, 18, 11]),   # chassis colour
    'accent': ([284, 48], [18, 8, 7]),    # scheme accent (orange on Recon)
    'dark': ([140, 48], [8, 6, 8]),       # gunmetal
    'metal': ([100, 48], [6, 13, 7]),
    'steel': ([238, 48], [2, 13, 2]),
    'hazard': ([336, 48], [3, 2, 8]),
    'vent': ([156, 2], [10, 10, 2]),
    'lens': ([824, 2], [16, 2, 1]),       # visor glow
}

# Parts in the gun's own frame, relative to the grip: x along the barrel, y up (optic side), z across.
# (x0, x1, y0, y1, z0, z1, material)
PARTS = [
    # Receiver: chassis-coloured lower, gunmetal upper, accent side plates, ejection port, charging handle
    (-4, 10, -3, 3, -3, 3, 'paint'),
    (-6, 14, 3, 6, -2.5, 2.5, 'dark'),
    (0, 8, -2, 2, 3, 3.5, 'accent'),
    (0, 8, -2, 2, -3.5, -3, 'accent'),
    (4, 8, 3.5, 5.5, -3, -2.5, 'metal'),
    (9, 11, 3, 4, 2.5, 4.5, 'metal'),
    (-1, 1, -3.2, 3.2, -3.2, 3.2, 'hazard'),
    (-3, 1, 0, 2, 3.5, 3.8, 'lens'),                 # side ammo counter
    # Picatinny rail with teeth, holographic optic
    (-4, 12, 6, 7, -1.5, 1.5, 'metal'),
    *[(x, x + 1.5, 7, 7.8, -1.5, 1.5, 'dark') for x in (-3, 0, 3, 9)],
    (2, 4, 7, 11, -2, 2, 'dark'),
    (6, 8, 7, 11, -2, 2, 'dark'),
    (2, 8, 11, 11.6, -2, 2, 'dark'),
    (6.4, 6.9, 8, 10.6, -1.5, 1.5, 'lens'),
    # Vented handguard, barrel, muzzle brake
    (14, 24, -2, 3, -2.5, 2.5, 'dark'),
    (15, 23, -1, 2, 2.5, 2.8, 'vent'),
    (15, 23, -1, 2, -2.8, -2.5, 'vent'),
    *[(x, x + 1.5, 3, 3.5, -1.5, 1.5, 'metal') for x in (15, 18, 21)],
    (24, 30, -0.5, 1.5, -1, 1, 'steel'),
    (30, 34, -1.5, 2.5, -2, 2, 'dark'),
    (31, 32, -1.8, 2.8, -2.2, 2.2, 'metal'),
    (32.8, 33.4, -1.8, 2.8, -2.2, 2.2, 'metal'),
    # Under-barrel light and vertical foregrip
    (20, 24, -2.5, -0.5, 2.5, 4, 'dark'),
    (24, 24.3, -2.2, -0.8, 2.8, 3.7, 'lens'),
    (16, 19, -9, -2, -1.5, 1.5, 'dark'),
    # Pistol grip, trigger guard, curved magazine with base plate
    (-4, -1, -9, -3, -2, 2, 'dark'),
    (-1, 3, -5, -4.4, -0.5, 0.5, 'metal'),
    (2, 7, -10, -3, -2, 2, 'dark'),
    (3, 8, -14, -10, -2, 2, 'dark'),
    (4, 9, -17, -14, -2, 2, 'dark'),
    (3.5, 9.5, -18, -17, -2.4, 2.4, 'accent'),
    # Buffer tube and stock with cheek rest and butt pad
    (-14, -6, 0, 3, -1.5, 1.5, 'metal'),
    (-18, -12, -3, 4, -2, 2, 'paint'),
    (-16, -10, 4, 5, -1.5, 1.5, 'dark'),
    (-19, -18, -4, 5, -2.5, 2.5, 'dark'),
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
