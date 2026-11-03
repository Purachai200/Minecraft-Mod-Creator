"""Shared, read-only helpers for armor set modules. Set modules import from here; do not edit per set.

Box format (model units, 16 = 1 block, forward = -Z, the mech's left = +X):
    (x, y, z, sx, sy, sz)                               axis-aligned cube, origin = min corner
    (x, y, z, sx, sy, sz, px, py, pz, rx, ry, rz)       same cube rotated (degrees) about its own pivot
All coordinates are FINAL model coordinates (the space of exoframe.geo.json), not bone-local.
"""
import math

# ---------------- frame anchor points (final model space) ----------------
class Anchors:
    """Joint and mount points of the frame. Bone pivots are the joints; armor is authored around them."""
    head = (0.0, 32.0, -1.0)            # head bone pivot (sensor heads sit in the throat ahead of the pilot)
    torso = (0.0, 20.0, 0.0)            # torso pivot; chest / canopy / roll cage / backpacks hang here
    seat = (0.0, 25.0, 3.5)             # upper_back_seat pivot
    shoulder_l = (9.0, 31.0, -0.5)      # left_arm pivot (right = mirrored x)
    elbow_l = (9.0, 24.6, -0.5)
    wrist_l = (9.0, 16.6, -0.5)
    hip_l = (4.5, 17.0, 0.0)            # left_thigh pivot
    knee_l = (4.5, 9.0, -2.8)           # left_shin pivot
    ankle_l = (4.5, 2.0, 2.2)           # left_foot pivot
    back_mount = (0.0, 21.6, 9.8)       # rear face of the shoulder collar back beam: backpack mount plates start here (z)
    pod_mount = (0.0, 32.0, 2.0)        # shoulder-top missile pod pivot
    float_ring = (0.0, 17.0, 0.0)       # pelvis-level float ring pivot

    # Envelope the frame occupies, so armor knows what it has to clear (min corner, max corner), left side.
    thigh_env_l = ((3.0, 8.0, -3.4), (6.2, 19.2, 2.6))
    shin_env_l = ((3.0, 1.2, -4.8), (6.1, 11.0, 3.8))
    foot_env_l = ((2.1, 0.0, -6.6), (6.9, 4.0, 4.7))
    upper_arm_env_l = ((7.2, 23.0, -2.8), (10.8, 33.5, 1.8))
    forearm_env_l = ((7.3, 16.4, -2.4), (10.7, 26.6, 1.6))
    torso_env = ((-5.9, 14.5, -3.7), (5.9, 36.0, 13.0))   # cockpit tub + collar + roll hoop + power pack


A = Anchors

# Where the pre-Phase-1 armor was authored; legacy geometry is shifted by (anchor - LEGACY_*).
LEGACY_BACK_MOUNT = (0.0, 21.6, 6.8)


def shift(boxes, d):
    """Translate boxes (and their rotation pivots) by d = (dx, dy, dz)."""
    out = []
    for b in boxes:
        if len(b) >= 12:
            x, y, z, sx, sy, sz, px, py, pz, rx, ry, rz = b
            out.append((x + d[0], y + d[1], z + d[2], sx, sy, sz, px + d[0], py + d[1], pz + d[2], rx, ry, rz))
        else:
            x, y, z, sx, sy, sz = b
            out.append((x + d[0], y + d[1], z + d[2], sx, sy, sz))
    return out


def delta(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def mx(b):
    """Mirror a box across x = 0 (left <-> right)."""
    if len(b) >= 12:
        x, y, z, sx, sy, sz, px, py, pz, rx, ry, rz = b
        return (-(x + sx), y, z, sx, sy, sz, -px, py, pz, rx, -ry, -rz)
    x, y, z, sx, sy, sz = b
    return (-(x + sx), y, z, sx, sy, sz)


def sym(*boxes):
    """Each box plus its mirror."""
    return [v for b in boxes for v in (b, mx(b))]


def rot_box(ox, oy, oz, sx, sy, sz, px, py, pz, rx, ry, rz):
    return (ox, oy, oz, sx, sy, sz, px, py, pz, rx, ry, rz)


# ---------------- primitives ----------------
def disc_x(x, cy, cz, r, w):
    k = 0.83 * r
    return [(x, cy - r, cz - k / 2, w, 2 * r, k), (x, cy - k / 2, cz - r, w, k, 2 * r),
            (x, cy - 0.71 * r, cz - 0.71 * r, w, 1.42 * r, 1.42 * r)]


def disc_z(cx, cy, z, r, d):
    k = 0.83 * r
    return [(cx - r, cy - k / 2, z, 2 * r, k, d), (cx - k / 2, cy - r, z, k, 2 * r, d),
            (cx - 0.71 * r, cy - 0.71 * r, z, 1.42 * r, 1.42 * r, d)]


def disc_y(cx, y, cz, r, h):
    k = 0.83 * r
    return [(cx - r, y, cz - k / 2, 2 * r, h, k), (cx - k / 2, y, cz - r, k, h, 2 * r),
            (cx - 0.71 * r, y, cz - 0.71 * r, 1.42 * r, h, 1.42 * r)]


def ring_x(x, cy, cz, r, w, n=12, s=0.7):
    return [(x, cy + r * math.sin(a) - s / 2, cz + r * math.cos(a) - s / 2, w, s, s)
            for a in (2 * math.pi * i / n for i in range(n))]


def piston_y(x, y0, y1, z, t=1.0):
    mid = (y0 + y1) / 2
    r = t * 0.5
    return [(x, mid, z, t, y1 - mid, t), (x + t / 2 - r / 2, y0, z + t / 2 - r / 2, r, mid - y0, r),
            (x - 0.1, y1 - 0.4, z - 0.1, t + 0.2, 0.4, t + 0.2), (x - 0.1, y0, z - 0.1, t + 0.2, 0.4, t + 0.2)]


def stepped(x, y_top, z_top, y_bot, z_bot, sx, sz, n):
    out, dy = [], (y_top - y_bot) / n
    for i in range(n):
        y = y_top - dy * (i + 1)
        z = z_top + (z_bot - z_top) * (i + 0.5) / n
        out.append((x, y, z - sz / 2, sx, dy + 0.3, sz))
    return out


def round_ring(y, h, hx, zf, zb, r=2.6, t=0.6, front=True, n=3):
    out = [(-hx + r, y, zb - t, 2 * (hx - r), h, t)]
    if front:
        out.append((-hx + r, y, zf, 2 * (hx - r), h, t))
    for sx in (1, -1):
        out.append(((hx - t) if sx > 0 else -hx, y, zf + r, t, h, zb - zf - 2 * r))
        for zc, sz in ((zf, 1), (zb, -1)):
            for i in range(n):
                a0, a1 = math.pi / 2 * i / n, math.pi / 2 * (i + 1) / n
                xs = [hx - r + r * math.cos(a) for a in (a0, a1)]
                zs = [r - r * math.sin(a) for a in (a0, a1)]
                x0, x1 = min(xs), max(max(xs), min(xs) + t)
                z0, z1 = min(zs), max(max(zs), min(zs) + t)
                x0, x1 = (x0, x1) if sx > 0 else (-x1, -x0)
                z0, z1 = (zc + z0, zc + z1) if sz > 0 else (zc - z1, zc - z0)
                out.append((x0, y, z0, x1 - x0, h, z1 - z0))
    return out


# ---------------- rider (pilot) envelope ----------------
MODEL_SCALE = 1.8
SEAT_DROP = -6.0
AUTHORED = (0.0, 21.6, 5.1)
SEAT_LOWER = 11.0
SEATED = (0.0, ((30.8 - SEAT_LOWER) * MODEL_SCALE - 10.0) / MODEL_SCALE, 4.3)   # mirrors ExoframeEntity.SEAT_CUSHION_Y


def to_seat(b):
    """Pilot-scale authored space (1 px = 1 player pixel, seat at AUTHORED) -> model space."""
    p = [SEATED[i] + (b[i] - AUTHORED[i]) / MODEL_SCALE for i in range(3)]
    if len(b) >= 12:
        pivot = [SEATED[i] + (b[6 + i] - AUTHORED[i]) / MODEL_SCALE for i in range(3)]
        return (*p, *(v / MODEL_SCALE for v in b[3:6]), *pivot, *b[9:12])
    return (*p, *(v / MODEL_SCALE for v in b[3:6]))


def limb_boxes(px, py, length, fwd, spread):
    d = (math.copysign(math.cos(fwd) * math.sin(spread), px), -math.cos(fwd) * math.cos(spread), -math.sin(fwd))
    return [(px + d[0] * t - 2.0, 21.6 + py + d[1] * t - 2.0, 5.1 + d[2] * t - 2.0, 4.0, 4.0, 4.0)
            for t in (0.15 * length, 0.4 * length, 0.65 * length, 0.9 * length)]


RIDER = [to_seat(b) for b in (
    (-4.0, 33.6, 3.1, 8.0, 12.0, 4.0),
    (-4.0, 45.6, 1.1, 8.0, 8.0, 8.0),
    *limb_boxes(1.9, 12.0, 12.0, 0.9, 0.28), *limb_boxes(-1.9, 12.0, 12.0, 0.9, 0.28),
    *limb_boxes(5.0, 22.0, 10.0, 1.0, 0.12), *limb_boxes(-5.0, 22.0, 10.0, 1.0, 0.12))]
RIDER_LEGS = RIDER[2:10]


def head_pitch_boxes():
    """Pilot head swept +-30 deg about the neck, in model space."""
    neck_y, neck_z, out = 45.6, 5.1, []
    for deg in range(-30, 31, 2):
        c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        pts = []
        for y in (0.0, 8.0):
            for z in (-4.0, 4.0):
                pts.append((neck_y + y * c - z * s, neck_z + y * s + z * c))
                pts.append((neck_y + y * c + z * s, neck_z - y * s + z * c))
        y0, y1 = min(p[0] for p in pts), max(p[0] for p in pts)
        z0, z1 = min(p[1] for p in pts), max(p[1] for p in pts)
        out.append(to_seat((-4.0, y0, z0, 8.0, y1 - y0, z1 - z0)))
    return out


# ---------------- legacy fit helpers (keep pre-Phase-1 armor working on the new frame) ----------------
def leg_fairing():
    """Shell over the pilot's shins; every chest piece carries it (both sides via sym)."""
    L = RIDER_LEGS
    x_out = max(max(abs(b[0]), abs(b[0] + b[3])) for b in L) + 0.3
    y_lo = min(b[1] for b in L) - 0.4
    z_lo = min(b[2] for b in L) - 0.3
    z_hi = max(b[2] + b[5] for b in L)
    hip_y = SEATED[1] + 12.0 / MODEL_SCALE
    return sym((x_out, y_lo, z_lo, 0.5, hip_y - y_lo - 0.6, z_hi - z_lo),
               (x_out - 0.2, y_lo - 0.4, z_lo - 0.2, 0.9, 0.5, z_hi - z_lo + 0.2),
               (1.2, y_lo, z_lo - 0.5, x_out - 1.0, 2.6, 0.5),
               (x_out + 0.5, y_lo + 0.8, z_lo + 1.0, 0.2, 0.4, z_hi - z_lo - 2.0))


def head_fit(boxes):
    """Legacy head trim: drop/cut cubes that reach above the pilot-leg line inside the leg z band."""
    L = RIDER_LEGS
    top = min(b[1] for b in L) - 0.1
    zmin, zmax = min(b[2] for b in L), max(b[2] + b[5] for b in L)
    out = []
    for b in boxes:
        b = list(b)
        if b[2] < zmax and b[2] + b[5] > zmin and b[1] + b[4] > top:
            b[4] = top - b[1]
        if b[4] > 0.05:
            out.append(tuple(b))
    return out


def shoulder_fit(boxes, side):
    """Pauldrons were authored around the old shoulder (x 7, y 30); the joint now sits at x 9, y 31."""
    return shift(boxes, (2.0 * side, 1.0, 0.0))


def seat_space(boxes):
    """Pilot-scale capsule geometry (authored around the seated player) -> model space."""
    return [to_seat(shift([b], (0, SEAT_DROP, 0))[0]) for b in boxes]


def back_fit(boxes):
    """Backpacks were authored against the old mount plane (z 6.8); move them onto the collar's rear face."""
    return shift(boxes, delta(A.back_mount, LEGACY_BACK_MOUNT))


def mirror_pair(left_name, right_name, boxes):
    return {left_name: list(boxes), right_name: [mx(b) for b in boxes]}


# ---------------- legacy archetype builders (shared silhouettes many sets started from) ----------------
def build_box_canopy(extras=()):
    roof_y, rear_z = 33.7, 9.47
    base = [
        (-5.5, roof_y, -2.5, 5.5, 1.0, 6.0), (0.0, roof_y, -2.5, 5.5, 1.0, 6.0),
        (-5.5, roof_y, 3.5, 5.5, 1.0, rear_z + 0.8 - 3.5), (0.0, roof_y, 3.5, 5.5, 1.0, rear_z + 0.8 - 3.5),
        (-3.2, roof_y + 1.0, 1.5, 6.4, 0.6, 5.5),                       # commander hatch
        (-3.4, roof_y + 1.0, 6.8, 6.8, 0.7, 0.6),                       # hatch rim
        (3.6, roof_y + 1.0, 3.2, 0.4, 0.4, 2.6), (-4.0, roof_y + 1.0, 3.2, 0.4, 0.4, 2.6),
        (-5.5, 19.5, rear_z, 5.5, roof_y + 1.0 - 19.5, 0.8), (0.0, 19.5, rear_z, 5.5, roof_y + 1.0 - 19.5, 0.8),
        (-4.0, 20.5, rear_z + 0.8, 8.0, roof_y - 20.5, 0.6),            # rear radiator louvers
        (-1.5, 30.0, rear_z + 0.8, 3.0, 3.0, 0.4),                      # egress latch
        (5.9, 19.5, -2.2, 0.8, roof_y - 19.5, rear_z + 2.2), (-6.7, 19.5, -2.2, 0.8, roof_y - 19.5, rear_z + 2.2),
        (-3.0, 31.0, -3.6, 6.0, roof_y - 31.0, 1.2),                    # brow
        (2.8, 26.5, -3.6, 3.2, roof_y - 26.5, 1.2), (-6.0, 26.5, -3.6, 3.2, roof_y - 26.5, 1.2),
        rot_box(4.8, roof_y - 0.7, -2.5, 1.4, 0.8, rear_z + 2.5, 5.5, roof_y - 0.3, 3.2, 0, 0, -45),
        rot_box(-6.2, roof_y - 0.7, -2.5, 1.4, 0.8, rear_z + 2.5, -5.5, roof_y - 0.3, 3.2, 0, 0, 45),
    ]
    return base + list(extras)


def build_chest_glacis(extras=()):
    base = [
        rot_box(-5.4, 22.0, -7.2, 10.8, 9.6, 1.4, 0, 22.0, -6.5, -26, 0, 0),
        rot_box(-4.5, 16.5, -4.2, 9.0, 6.2, 1.4, 0, 17.0, -4.2, 28, 0, 0),
        (-3.0, 29.8, -3.6, 6.0, 1.4, 1.4),
        (-3.6, 19.5, -4.6, 7.2, 0.8, 1.2), (-3.4, 18.2, -4.4, 6.8, 0.8, 1.2), (-3.2, 16.9, -4.2, 6.4, 0.8, 1.2),
        rot_box(-2.0, 14.2, -5.2, 4.0, 4.8, 1.4, 0, 15.0, -4.8, 18, 0, 0),
        rot_box(3.2, 14.5, -4.0, 1.2, 5.4, 3.8, 3.5, 18.0, -2.5, 0, 0, -16),
        rot_box(-4.4, 14.5, -4.0, 1.2, 5.4, 3.8, -3.5, 18.0, -2.5, 0, 0, 16),
        rot_box(3.0, 22.0, -6.5, 2.8, 7.6, 2.0, 3.2, 23.0, -5.5, -20, 16, -8),
        rot_box(-5.8, 22.0, -6.5, 2.8, 7.6, 2.0, -3.2, 23.0, -5.5, -20, -16, 8),
    ]
    return base + list(extras)


def build_throat_head(apertures=(), extras=()):
    base = [(-2.2, 31.4, -3.2, 4.4, 2.4, 2.0), (-1.8, 32.2, -3.4, 3.6, 0.8, 0.4),
            rot_box(-2.2, 33.6, -3.4, 4.4, 0.8, 1.8, 0, 33.6, -3.4, -18, 0, 0)]
    return base + list(apertures) + list(extras)


def build_box_pauldron(extras=()):
    """Left pauldron in legacy shoulder space; pass through shoulder_fit()."""
    base = [rot_box(4.8, 31.5, -4.0, 6.4, 1.2, 8.0, 5.5, 31.5, 0.0, 0, 0, -8),
            (10.2, 24.5, -3.8, 1.2, 7.5, 7.6),
            rot_box(4.8, 25.0, -4.6, 5.4, 6.5, 1.2, 6.0, 29.0, -4.0, -12, 0, 0),
            rot_box(4.8, 25.0, 3.4, 5.4, 6.5, 1.2, 6.0, 29.0, 4.0, 12, 0, 0)]
    return base + list(extras)


def build_leg_cuisse(extras=()):
    """Left thigh armor around hip (4.5, 17, 0)."""
    base = [(2.6, 16.0, -2.2, 3.8, 1.2, 4.4), (5.8, 10.8, -2.6, 1.2, 5.6, 4.8), (2.8, 11.2, -3.2, 3.4, 5.2, 1.2),
            (2.8, 8.0, -5.2, 3.2, 3.6, 2.2), (6.0, 9.2, -4.2, 0.6, 1.4, 1.4),
            (3.4, 8.5, -3.2, 0.8, 5.5, 0.8), (4.8, 8.5, -3.2, 0.8, 5.5, 0.8)]
    return base + list(extras)


def build_shin_greave(extras=()):
    """Left shin armor around knee (4.5, 9, -2.8). The old split-toe boot pads were dropped in Phase 1:
    the frame now has real flat feet (left_foot) and pads on the shin bone poked through them when walking."""
    base = [rot_box(2.8, 2.0, -4.4, 3.4, 7.0, 1.4, 4.5, 6.0, -3.5, -16, 0, 0),
            rot_box(6.0, 1.8, -3.0, 1.2, 7.2, 5.4, 6.0, 7.0, 0.0, 0, 0, -14),
            rot_box(3.0, 2.2, 2.2, 3.0, 6.2, 1.4, 4.5, 6.0, 2.0, 14, 0, 0)]
    return base + list(extras)


MOUNT = [(-3.6, 21.6, 6.8, 7.2, 9.8, 0.8), (-1.2, 27.0, 6.8, 2.4, 1.6, 1.0),
         *[(x, 26.8, 6.8, 0.8, 0.8, 1.0) for x in (2.0, -2.8)],
         *[(x, 23.0, 6.8, 0.8, 0.8, 1.0) for x in (0.6, -1.4)],
         *[bx for x in (1.0, -1.5) for bx in stepped(x, 26.6, 7.2, 22.0, 6.8, 0.5, 0.5, 3)]]


def assemble(sid, head=None, head_bone=None, chest=None, chest_bone=None, canopy=None, canopy_bone=None,
             pauldron=None, cuisse=None, greave=None, backpack=None, backpack_bone=None):
    """Standard full set -> {bone: boxes}. All inputs are LEFT-side / centre geometry in final model space,
    except `pauldron`, which is in legacy shoulder space and goes through shoulder_fit()."""
    out = {}
    if head is not None:
        out[head_bone or f"armor_head_{sid}"] = head_fit(head)
    if chest is not None:
        out[chest_bone or f"armor_chest_{sid}"] = list(chest) + leg_fairing()
    if canopy is not None:
        out[canopy_bone or f"canopy_{sid}"] = list(canopy)
    if pauldron is not None:
        out[f"armor_left_shoulder_{sid}"] = shoulder_fit(pauldron, 1)
        out[f"armor_right_shoulder_{sid}"] = shoulder_fit([mx(b) for b in pauldron], -1)
    if cuisse is not None:
        out.update(mirror_pair(f"armor_left_leg_{sid}", f"armor_right_leg_{sid}", cuisse))
    if greave is not None:
        out.update(mirror_pair(f"armor_left_shin_{sid}", f"armor_right_shin_{sid}", greave))
    if backpack is not None:
        out[backpack_bone or f"backpack_{sid}"] = back_fit(backpack)
    return out
