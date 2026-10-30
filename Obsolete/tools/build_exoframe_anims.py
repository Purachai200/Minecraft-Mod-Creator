"""Builds exoframe.animation.json locomotion + emotes with IK so feet stay planted and hands hit their targets.

Works in GeckoLib render space (JSON x negated; bone rot = Rz*Ry*Rx). Keyframe rotations are written in
Bedrock convention, which GeckoLib loads as (-x, -y, z), hence the sign flips in deg_json().
Hand-authored clips already in the file (melee, shoot, death, ...) are kept untouched.
"""
import json, math, os

ROOT = os.path.join(os.path.dirname(__file__), "..", "src/main/resources/assets/obsolete")
GEO = os.path.join(ROOT, "geo/exoframe.geo.json")
ANIM = os.path.join(ROOT, "animations/exoframe.animation.json")

bones = {b["name"]: b for b in json.load(open(GEO))["minecraft:geometry"][0]["bones"]}
piv = lambda n: [-bones[n]["pivot"][0], bones[n]["pivot"][1], bones[n]["pivot"][2]]  # render space


def r1(v):
    return round(v, 2)


# ---------------- LEG IK (sagittal plane: (y, z), forward = -z) ----------------
HIP = piv("left_thigh")
KNEE = piv("left_shin")
ANKLE = piv("left_foot")
T = (KNEE[1] - HIP[1], KNEE[2] - HIP[2])
S = (ANKLE[1] - KNEE[1], ANKLE[2] - KNEE[2])
GROUND_ANKLE_Y = ANKLE[1]
REST_ANKLE_Z = ANKLE[2]


def rot(v, a):
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def leg_ik(dy, dz):
    """Thigh/shin render rotX so the ankle sits at (dy, dz) from the hip. Picks the branch nearest rest pose."""
    d2 = dy * dy + dz * dz
    lt2, ls2 = T[0] ** 2 + T[1] ** 2, S[0] ** 2 + S[1] ** 2
    A, B = T[0] * S[0] + T[1] * S[1], T[1] * S[0] - T[0] * S[1]
    R, psi = math.hypot(A, B), math.atan2(B, A)
    c = max(-1.0, min(1.0, ((d2 - lt2 - ls2) / 2) / R))
    cands = [psi + math.acos(c), psi - math.acos(c)]
    k = min((((x + math.pi) % (2 * math.pi)) - math.pi for x in cands), key=abs)
    v = (T[0] + rot(S, k)[0], T[1] + rot(S, k)[1])
    th = math.atan2(dz, dy) - math.atan2(v[1], v[0])
    th = ((th + math.pi) % (2 * math.pi)) - math.pi
    return th, k


def legs_at(pelvis_y, ankle_l, ankle_r, toe_l=0.0, toe_r=0.0):
    """ankle_* = (world y, z). Returns json rotation x for thigh/shin/foot (foot kept flat + toe offset)."""
    out = {}
    for side, (ay, az), toe in (("left", ankle_l, toe_l), ("right", ankle_r, toe_r)):
        th, k = leg_ik(ay - (HIP[1] + pelvis_y), az - HIP[2])
        out[side] = (-math.degrees(th), -math.degrees(k), math.degrees(th + k) + toe)
    return out


# self-check: rest stance must reproduce rest angles, and feet must actually land where asked
_r = legs_at(0, (GROUND_ANKLE_Y, REST_ANKLE_Z), (GROUND_ANKLE_Y, REST_ANKLE_Z))["left"]
assert all(abs(a) < 1e-6 for a in _r), _r
for _py, _az in ((-6, REST_ANKLE_Z), (0, -1.0), (-0.5, 5.4)):
    _th, _k = leg_ik(GROUND_ANKLE_Y - (HIP[1] + _py), _az - HIP[2])
    _v = (T[0] + rot(S, _k)[0], T[1] + rot(S, _k)[1]); _v = rot(_v, _th)
    assert abs(HIP[1] + _py + _v[0] - GROUND_ANKLE_Y) < 1e-6 and abs(HIP[2] + _v[1] - _az) < 1e-6


# ---------------- ARM FK + numeric IK (for emote poses) ----------------
def mat_rot(rx, ry, rz):
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    Rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    Ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    Rz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    mm = lambda a, b: [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return mm(mm(Rz, Ry), Rx)


def apply(m, v):
    return [sum(m[i][j] * v[j] for j in range(3)) for i in range(3)]


def about(p, pivot, r):
    d = apply(r, [p[i] - pivot[i] for i in range(3)])
    return [pivot[i] + d[i] for i in range(3)]


def arm_fk(side, q, palm):
    sh, el = piv(f"{side}_arm"), piv(f"{side}_forearm")
    ra, rf = mat_rot(*q[:3]), mat_rot(q[3], 0, 0)
    return about(el, sh, ra), about(about(palm, el, rf), sh, ra)


def arm_solve(side, palm_target, elbow_target, palm=None):
    """Coordinate-descent IK: arm (rx, ry, rz) + elbow hinge rx, palm on target, elbow pulled toward a hint."""
    palm = palm or [-7.9 if side == "left" else 7.9, 12.0, -0.6]   # render-space fist centre
    tgt = [-palm_target[0], palm_target[1], palm_target[2]]
    eh = [-elbow_target[0], elbow_target[1], elbow_target[2]]
    q = [0.5, 0.0, 0.0, 0.8]
    cost = lambda q: (sum((a - b) ** 2 for a, b in zip(arm_fk(side, q, palm)[1], tgt))
                      + 0.15 * sum((a - b) ** 2 for a, b in zip(arm_fk(side, q, palm)[0], eh))
                      + (100 * q[3] ** 2 if q[3] < 0 else 0) + (100 * (q[3] - 2.6) ** 2 if q[3] > 2.6 else 0))
    step = 0.5
    while step > 1e-4:
        improved = False
        for i in range(4):
            for d in (step, -step):
                t = q[:]; t[i] += d
                if cost(t) < cost(q):
                    q, improved = t, True
        if not improved:
            step /= 2
    err = math.sqrt(sum((a - b) ** 2 for a, b in zip(arm_fk(side, q, palm)[1], tgt)))
    assert err < 0.8, (side, palm_target, err)
    return {f"{side}_arm": [r1(-math.degrees(q[0])), r1(-math.degrees(q[1])), r1(math.degrees(q[2]))],
            f"{side}_forearm": [r1(-math.degrees(q[3])), 0, 0]}


# ---------------- CLIP HELPERS ----------------
def clip(length, loop=True):
    return {"loop": loop, "animation_length": length, "bones": {}}


def key(c, bone, ch, t, v):
    c["bones"].setdefault(bone, {}).setdefault(ch, {})[f"{round(t, 3)}"] = [r1(x) for x in v]


def gait(length, stride, lift, stance, pelvis_drop, bob, torso_pitch, arm_swing, twist, steps=20):
    c = clip(length)
    zf, zb = REST_ANKLE_Z - stride, REST_ANKLE_Z + stride
    for i in range(steps + 1):
        u = i / steps
        t = u * length
        py = -pelvis_drop - bob * (0.5 + 0.5 * math.cos(4 * math.pi * u))

        def foot(p):
            p %= 1.0
            if p < stance:
                return (GROUND_ANKLE_Y, zf + (zb - zf) * p / stance), 0.0
            s = (p - stance) / (1 - stance)
            e = s * s * (3 - 2 * s)
            return (GROUND_ANKLE_Y + lift * math.sin(math.pi * s), zb + (zf - zb) * e), 14 * math.sin(math.pi * s)

        (al, tl), (ar, tr) = foot(u), foot(u + 0.5)
        L = legs_at(py, al, ar, tl, tr)
        for side in ("left", "right"):
            th, k, f = L[side]
            key(c, f"{side}_thigh", "rotation", t, [th, 0, 0])
            key(c, f"{side}_shin", "rotation", t, [k, 0, 0])
            key(c, f"{side}_foot", "rotation", t, [f, 0, 0])
        w = math.cos(2 * math.pi * u)
        key(c, "pelvis", "position", t, [0, py, 0])
        key(c, "pelvis", "rotation", t, [0, -twist * w, 1.5 * w])
        key(c, "torso", "rotation", t, [torso_pitch, twist * 1.6 * w, -1.5 * w])
        key(c, "head", "rotation", t, [-torso_pitch * 0.6, -twist * 1.2 * w, 0])
        key(c, "left_arm", "rotation", t, [arm_swing * w, 0, -3])
        key(c, "right_arm", "rotation", t, [-arm_swing * w, 0, 3])
        key(c, "left_forearm", "rotation", t, [-12 - 0.4 * arm_swing * max(0, -w), 0, 0])
        key(c, "right_forearm", "rotation", t, [-12 - 0.4 * arm_swing * max(0, w), 0, 0])
    return c


def stance_clip(length, pelvis_drop, torso_pitch, breathe, head_scan=0.0, arms=(-6, -10), steps=8):
    c = clip(length)
    L = legs_at(-pelvis_drop, (GROUND_ANKLE_Y, REST_ANKLE_Z - 0.6), (GROUND_ANKLE_Y, REST_ANKLE_Z + 0.6))
    for i in range(steps + 1):
        u = i / steps
        t = u * length
        b = math.sin(2 * math.pi * u)
        key(c, "pelvis", "position", t, [0, -pelvis_drop, 0])
        for side in ("left", "right"):
            th, k, f = L[side]
            key(c, f"{side}_thigh", "rotation", t, [th, 0, 0])
            key(c, f"{side}_shin", "rotation", t, [k, 0, 0])
            key(c, f"{side}_foot", "rotation", t, [f, 0, 0])
        key(c, "torso", "position", t, [0, breathe * (0.5 + 0.5 * b), 0])
        key(c, "torso", "rotation", t, [torso_pitch + 0.8 * b, 0, 0])
        key(c, "head", "rotation", t, [-torso_pitch * 0.7, head_scan * math.sin(2 * math.pi * u), 0])
        key(c, "left_arm", "rotation", t, [arms[0] - 1.5 * b, 0, -4])
        key(c, "right_arm", "rotation", t, [arms[0] - 1.5 * b, 0, 4])
        key(c, "left_forearm", "rotation", t, [arms[1], 0, 0])
        key(c, "right_forearm", "rotation", t, [arms[1], 0, 0])
    return c


def pose_clip(length, frames, extra=None):
    """frames: [(t, {bone: [rx, ry, rz]})]; bones absent from a frame return to zero."""
    c = clip(length, loop=False)
    names = {b for _, f in frames for b in f}
    for t, f in frames:
        for b in names:
            key(c, b, "rotation", t, f.get(b, [0, 0, 0]))
    for bone, ch, t, v in extra or []:
        key(c, bone, ch, t, v)
    return c


# ---------------- BUILD ----------------
anims = json.load(open(ANIM))["animations"]
P = "animation.exoframe."

# Pelvis drop for crouch matches the rider seat drop in ExoframeEntity.positionRider (1.72 -> 1.35 blocks = ~6px).
anims[P + "idle"] = stance_clip(4.0, 0.0, 0.0, 0.18, head_scan=6.0)
anims[P + "crouch"] = stance_clip(2.0, 6.0, 12.0, 0.12, arms=(-14, -22))
anims[P + "walk"] = gait(1.0, 3.2, 2.4, 0.6, 0.3, 0.35, 3.0, 14.0, 2.5)
anims[P + "sprint"] = gait(0.6, 4.6, 3.4, 0.45, 0.9, 0.6, 12.0, 30.0, 4.0)
anims[P + "crouch_walk"] = gait(1.2, 2.4, 1.6, 0.62, 6.0, 0.25, 13.0, 8.0, 1.5)

# Jump: load (crouch), push off, tuck in the air, reach for landing.
jump = clip(0.6, loop=False)
for t, py, al, ar in ((0.0, -3.0, (GROUND_ANKLE_Y, 2.6), (GROUND_ANKLE_Y, 2.6)),
                      (0.12, 0.0, (GROUND_ANKLE_Y - 0.3, 3.4), (GROUND_ANKLE_Y - 0.3, 3.4)),
                      (0.35, 0.0, (GROUND_ANKLE_Y + 4.0, 0.6), (GROUND_ANKLE_Y + 3.0, 1.6)),
                      (0.6, 0.0, (GROUND_ANKLE_Y + 1.0, 1.4), (GROUND_ANKLE_Y + 1.0, 1.8))):
    L = legs_at(py, al, ar)
    key(jump, "pelvis", "position", t, [0, py, 0])
    for side in ("left", "right"):
        th, k, f = L[side]
        key(jump, f"{side}_thigh", "rotation", t, [th, 0, 0])
        key(jump, f"{side}_shin", "rotation", t, [k, 0, 0])
        key(jump, f"{side}_foot", "rotation", t, [f, 0, 0])
    key(jump, "torso", "rotation", t, [8 if t in (0.0, 0.6) else 3, 0, 0])
    key(jump, "left_arm", "rotation", t, [-10 if t else 15, 0, -8])
    key(jump, "right_arm", "rotation", t, [-10 if t else 15, 0, 8])
anims[P + "jump"] = jump

# ---------------- EMOTES ----------------
# brow of the sensor head (moved forward/down to the chest front by the seat refit in build_exoframe_geo.py)
salute_r = arm_solve("right", (-3.0, 30.4, -8.8), (-12.5, 28.5, -4.0))
salute_l = arm_solve("left", (3.0, 30.4, -8.8), (12.5, 28.5, -4.0))
for name, pose, side in (("salute", salute_r, "right"), ("salute_left", salute_l, "left")):
    pose[f"{side}_hand"] = [0, 0, 20 if side == "right" else -20]              # flat hand at the brow
    anims[P + name] = pose_clip(2.2, [(0.0, {}), (0.35, pose), (1.55, pose), (1.95, {}), (2.2, {})],
                                extra=[("torso", "rotation", t, v) for t, v in
                                       ((0.0, [0, 0, 0]), (0.3, [-3, 0, 0]), (1.6, [-3, 0, 0]), (2.0, [0, 0, 0]))]
                                + [("head", "rotation", t, v) for t, v in
                                   ((0.0, [0, 0, 0]), (0.3, [-6, 0, 0]), (1.6, [-6, 0, 0]), (2.0, [0, 0, 0]))])

wave_a = arm_solve("left", (12.6, 40.5, -2.0), (13.5, 30.5, -1.0))
wave_b = arm_solve("left", (16.6, 39.5, -2.0), (13.5, 30.5, -1.0))
anims[P + "wave"] = pose_clip(2.6, [(0.0, {}), (0.35, wave_a), (0.65, wave_b), (0.95, wave_a), (1.25, wave_b),
                                    (1.55, wave_a), (1.85, wave_b), (2.25, {}), (2.6, {})],
                              extra=[("head", "rotation", t, v) for t, v in
                                     ((0.0, [0, 0, 0]), (0.3, [0, -12, 4]), (2.1, [0, -12, 4]), (2.5, [0, 0, 0]))])

point = arm_solve("left", (6.5, 31.0, -19.0), (8.0, 30.0, -7.5))
anims[P + "point"] = pose_clip(2.4, [(0.0, {}), (0.3, point), (1.8, point), (2.2, {}), (2.4, {})],
                               extra=[(b, "rotation", t, v) for b, t, v in
                                      (("torso", 0.0, [0, 0, 0]), ("torso", 0.3, [-2, -8, 0]), ("torso", 1.8, [-2, -8, 0]),
                                       ("torso", 2.2, [0, 0, 0]), ("head", 0.0, [0, 0, 0]), ("head", 0.3, [0, -10, 0]),
                                       ("head", 1.8, [0, -10, 0]), ("head", 2.2, [0, 0, 0]))])

scan = clip(4.0, loop=False)
for t, hy, hx, ty in ((0.0, 0, 0, 0), (0.6, 25, -4, 12), (1.5, 25, 4, 12), (2.3, -25, -4, -12),
                      (3.2, -25, 4, -12), (3.7, 0, 0, 0), (4.0, 0, 0, 0)):
    key(scan, "head", "rotation", t, [hx, hy, 0])
    key(scan, "torso", "rotation", t, [0, ty, 0])
anims[P + "scan"] = scan

# walk used to reference left_calf/right_calf (bones that don't exist); purge any stale ones
for a in anims.values():
    for stale in ("left_calf", "right_calf"):
        a["bones"].pop(stale, None)

json.dump({"format_version": "1.8.0", "animations": anims}, open(ANIM, "w"), indent=1)
print("animations:", ", ".join(k.split(".")[-1] for k in anims))
