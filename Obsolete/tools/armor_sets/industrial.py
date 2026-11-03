"""Industrial roll cage (registry faction "Industrial"): a heavy tube cage bolted round the open cockpit —
thick corner posts, a meshed roof frame, X-braced back, front grille guard, a low bumper bar, amber beacons
and work lamps. Worksite yellow / black from the fixed hazard-stripe block."""
from ._common import *  # noqa: F401,F403

SET_ID = "industrial"
UV_REGION = None   # painted by the fixed hazard-stripe block (0..75, 240..315); keep every cube's box UV < 75 px


def build(a=A):
    T = 1.0            # tube gauge
    r = sym((5.0, 21.4, -4.6, T, 16.4, T), (5.0, 21.4, 9.8, T, 16.4, T),          # corner posts
            (5.0, 37.8, -4.6, T, T, 15.4),                                          # roof side rails
            (5.0, 29.0, -3.6, T, T, 13.4),                                          # mid side rails
            (4.7, 21.0, -4.9, 1.6, 0.6, 1.6), (4.7, 21.0, 9.5, 1.6, 0.6, 1.6),     # base flanges
            (4.6, 37.4, -5.0, 1.8, 1.8, 1.8), (4.6, 37.4, 9.4, 1.8, 1.8, 1.8),     # welded corner nodes
            rot_box(5.1, 22.0, 2.0, 0.8, 0.8, 10.4, 5.5, 22.4, 2.4, 40, 0, 0),     # side diagonal
            (5.6, 38.8, -4.8, 1.2, 1.0, 1.2), (5.4, 39.8, -5.0, 1.6, 0.4, 1.6),    # amber beacons
            (3.0, 38.0, -5.4, 1.6, 1.2, 0.8), (3.2, 37.2, -4.8, 0.6, 0.8, 0.6),    # work lamps
            (5.0, 14.6, -6.2, T, 7.0, T),                                           # bumper uprights
            (2.0, 14.0, -6.6, 0.6, 1.0, 1.6))                                       # tow eyes
    r += [(-6.0, 37.8, -4.6, 12.0, T, T), (-6.0, 37.8, 9.8, 12.0, T, T),           # roof cross rails
          *[(-5.0, 38.0, z, 10.0, 0.5, 0.5) for z in (-1.0, 2.6, 6.2)],             # roof mesh bars
          (-0.25, 38.0, -4.6, 0.5, 0.5, 14.4),
          *[(x, 27.0, -5.2, 0.6, 10.8, 0.6) for x in (-3.3, -1.1, 0.5, 2.7)],       # front grille guard
          (-5.0, 27.0, -5.2, 10.0, 0.6, 0.6),
          rot_box(-5.0, 30.0, 10.0, 15.0, 0.8, 0.8, 0, 30.4, 10.4, 0, 0, 40),      # rear X-brace
          rot_box(-5.0, 30.0, 10.0, 15.0, 0.8, 0.8, 0, 30.4, 10.4, 0, 0, -40),
          (-6.0, 14.6, -6.6, 12.0, 1.2, 1.2), (-6.0, 19.4, -6.4, 12.0, 0.8, 0.8)]  # bumper bars
    return {"armor_roll_cage": r}
