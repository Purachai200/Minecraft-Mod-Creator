"""Keyframed GeckoLib animations for every flight rig.

  python3 tools/animation_spec.py

Writes assets/youjosenki/animations/<design>.animation.json. Every file holds the same eight
animations (deploy, idle, takeoff, hover, cruise, sprint, landing, boost) so RigAnimationDriver can
play them by name. Only "frame" bones are keyframed here; nozzles, fans, flaps, rudders, radiators,
pistons and rods are driven procedurally in FlightRigGeoModel.setCustomAnimations.

Units: position in pixels (y up), rotation in degrees using the vanilla ModelPart convention.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src/main/resources/assets/youjosenki/animations")

# design -> (mass, torso-mounted frame bones, leg-mounted bones, arm bones, head bones, has wings)
DESIGNS = {
    "MAGE_UNIT": (0.8, ["body"], ["right_leg"], [], [], False),
    "BACK_JETPACK": (1.0, ["back_jetpack"], [], [], [], False),
    "TACTICAL_WINGS": (0.7, ["tactical_wings"], [], [], [], True),
    "HEAVY_ROCKET": (1.7, ["heavy_tanks"], [], [], [], False),
    "TWIN_DRIVE_EXO": (1.1, ["twin_drive_torso"], ["right_leg", "left_leg"], [], [], False),
    "SIEGE_ARTILLERY": (1.9, ["siege_frame"], [], [], [], False),
    "THRUST_BOOTS": (0.8, [], ["thrust_boots_right", "thrust_boots_left"], [], [], False),
    "HYDRO_SKIMMER": (0.9, ["hydro_skimmer_torso"], ["hydro_skimmer_right", "hydro_skimmer_left"], [], [], False),
    "TACTICAL_SCUBA": (1.2, ["tactical_scuba"], [], [], [], False),
    "URBAN_EXO_LEGS": (1.0, ["urban_exo_harness"], ["urban_exo_right", "urban_exo_left"],
                       ["urban_exo_right_arm", "urban_exo_left_arm"], [], False),
    "DIVING_MASK": (0.5, [], [], [], ["diving_mask"], False),
}

WL, WR = "tactical_wings_left_wing", "tactical_wings_right_wing"
FOLD = {WL: [10.3, 48.7, -52.7], WR: [10.3, -48.7, 52.7]}
SWEPT = {WL: [0, 37.2, -5.7], WR: [0, -37.2, 5.7]}
SPREAD = {WL: [0, 0, 0], WR: [0, 0, 0]}


def v(*xs):
    return [round(x, 3) for x in xs]


def track(*frames):
    """frames: (time, vector[, easing])"""
    out = {}
    for fr in frames:
        k = {"vector": fr[1]}
        if len(fr) > 2:
            k["easing"] = fr[2]
        out["%g" % fr[0] if fr[0] else "0.0"] = k
    return out


def scale_v(vec, k):
    return [round(x * k, 3) for x in vec]


def build(design):
    m, torso, legs, arms, head, wings = DESIGNS[design]
    A = {}

    def anim(name, length, loop, bones):
        a = {"animation_length": length, "bones": bones}
        if loop:
            a["loop"] = True
        A[name] = a

    # ---------------------------------------------------------------- deploy: parts slide in and lock
    b = {}
    stagger = {}  # exo assembles limb by limb: legs, torso, then arms
    for i, bone in enumerate(legs):
        stagger[bone] = (0.0, v(0, -2.5, 0))
    for bone in torso:
        stagger[bone] = (0.2 if arms else 0.0, v(0, 1.5, 4.0))
    for bone in arms:
        stagger[bone] = (0.4, v(0, 2.5, 0))
    for bone in head:
        stagger[bone] = (0.0, v(0, 2.5, -1.0))
    for bone, (t0, d) in stagger.items():
        b[bone] = {
            "position": track((0, d), (t0 + 0.01, d), (t0 + 0.5, scale_v(d, 0.15), "easeOutCubic"),
                              (t0 + 0.65, v(0, 0, 0), "easeInQuad"), (t0 + 0.72, scale_v(d, -0.06)), (t0 + 0.82, v(0, 0, 0))),
            "scale": track((0, v(0.85, 0.85, 0.85)), (t0 + 0.01, v(0.85, 0.85, 0.85)), (t0 + 0.65, v(1, 1, 1), "easeOutCubic")),
            "rotation": track((0, v(0, 0, 0)), (t0 + 0.66, v(-2.5, 0, 0)), (t0 + 0.8, v(0, 0, 0), "easeOutBack")),
        }
    if wings:
        for w in (WL, WR):
            b[w] = {"rotation": track((0, scale_v(FOLD[w], 1.2)), (0.55, scale_v(FOLD[w], 1.2)),
                                      (0.75, FOLD[w], "easeOutBack"), (1.2, FOLD[w]))}
    anim("deploy", 1.2, False, b)

    # ---------------------------------------------------------------- idle: parked, breathing bob
    b = {bone: {"position": track((0, v(0, 0, 0)), (2.0, v(0, 0.12, 0), "easeInOutSine"), (4.0, v(0, 0, 0), "easeInOutSine"))}
         for bone in torso}
    if wings:
        for w in (WL, WR):
            b[w] = {"rotation": track((0, FOLD[w]), (4.0, FOLD[w]))}
    anim("idle", 4.0, True, b)

    # ---------------------------------------------------------------- takeoff: crouch, kick, settle
    b = {}
    for bone in torso:
        b[bone] = {
            "position": track((0, v(0, 0, 0)), (0.12, v(0, -0.6 * m, 0), "easeOutQuad"),
                              (0.3, v(0, 0.5, 0.3), "easeOutBack"), (0.7, v(0, 0, 0), "easeInOutSine")),
            "rotation": track((0, v(0, 0, 0)), (0.12, v(4 * m, 0, 0)), (0.3, v(-3, 0, 0)), (0.7, v(0, 0, 0), "easeInOutSine")),
        }
    for bone in legs:  # shock struts extend as weight comes off
        b[bone] = {"position": track((0, v(0, 0, 0)), (0.12, v(0, 0.5 * m, 0)), (0.35, v(0, -0.5, 0), "easeOutBack"),
                                     (0.7, v(0, 0, 0)))}
    if wings:
        for w in (WL, WR):
            over = [SPREAD[w][0], -5 if w == WL else 5, -4 if w == WL else 4]
            b[w] = {"rotation": track((0, FOLD[w]), (0.15, FOLD[w]), (0.5, over, "easeOutBack"), (0.7, SPREAD[w], "easeInOutSine"))}
    anim("takeoff", 0.7, False, b)

    # ---------------------------------------------------------------- hover: slow bob and sway
    b = {bone: {"position": track((0, v(0, 0, 0)), (1.2, v(0, 0.25, 0), "easeInOutSine"), (2.4, v(0, 0, 0), "easeInOutSine")),
                "rotation": track((0, v(0, 0, -0.8)), (1.2, v(0, 0, 0.8), "easeInOutSine"), (2.4, v(0, 0, -0.8), "easeInOutSine"))}
         for bone in torso}
    for bone in legs:
        b[bone] = {"rotation": track((0, v(-2, 0, 0)), (1.2, v(2, 0, 0), "easeInOutSine"), (2.4, v(-2, 0, 0), "easeInOutSine"))}
    if wings:
        for w in (WL, WR):
            s = -1 if w == WL else 1
            b[w] = {"rotation": track((0, v(0, 0, 1.5 * s)), (1.2, v(0, 0, -1.5 * s), "easeInOutSine"),
                                      (2.4, v(0, 0, 1.5 * s), "easeInOutSine"))}
    anim("hover", 2.4, True, b)

    # ---------------------------------------------------------------- cruise: forward lean, light flutter
    b = {bone: {"rotation": track((0, v(6, 0, 0)), (0.8, v(6.6, 0, 0), "easeInOutSine"), (1.6, v(6, 0, 0), "easeInOutSine")),
                "position": track((0, v(0, 0, 0.2)), (1.6, v(0, 0, 0.2)))}
         for bone in torso}
    if wings:
        for w in (WL, WR):
            s = -1 if w == WL else 1
            b[w] = {"rotation": track((0, v(0, 0, 3 * s)), (0.8, v(0, 0, 2 * s), "easeInOutSine"), (1.6, v(0, 0, 3 * s), "easeInOutSine"))}
    anim("cruise", 1.6, True, b)

    # ---------------------------------------------------------------- sprint: deep lean + buffeting
    vib = 0.4 / max(0.7, m)
    b = {bone: {"rotation": track((0, v(10, 0, vib)), (0.125, v(10.4, 0, -vib)), (0.25, v(10, 0, vib)),
                                  (0.375, v(10.3, 0, -vib)), (0.5, v(10, 0, vib))),
                "position": track((0, v(0, 0, 0.35)), (0.125, v(0, 0.08, 0.35)), (0.25, v(0, -0.08, 0.35)), (0.5, v(0, 0, 0.35)))}
         for bone in torso}
    for bone in legs:
        b[bone] = {"rotation": track((0, v(8, 0, 0)), (0.5, v(8, 0, 0)))}
    if wings:
        for w in (WL, WR):
            b[w] = {"rotation": track((0, SWEPT[w]), (0.25, [SWEPT[w][0] + 0.8, SWEPT[w][1], SWEPT[w][2]]), (0.5, SWEPT[w]))}
    anim("sprint", 0.5, True, b)

    # ---------------------------------------------------------------- landing: impact, spring back
    b = {}
    for bone in torso:
        b[bone] = {
            "position": track((0, v(0, 0, 0)), (0.08, v(0, -1.2 * m, 0), "easeOutQuad"),
                              (0.25, v(0, 0.35, 0), "easeOutBack"), (0.6, v(0, 0, 0), "easeInOutSine")),
            "rotation": track((0, v(0, 0, 0)), (0.08, v(-6 * m, 0, 0)), (0.25, v(2, 0, 0)), (0.6, v(0, 0, 0))),
        }
    for bone in legs:  # shock absorbers compress
        b[bone] = {"position": track((0, v(0, 0, 0)), (0.08, v(0, 0.9 * m, 0), "easeOutQuad"), (0.3, v(0, -0.2, 0)), (0.6, v(0, 0, 0)))}
    for bone in arms:
        b[bone] = {"position": track((0, v(0, 0, 0)), (0.1, v(0, -0.5 * m, 0)), (0.4, v(0, 0, 0), "easeOutBack"))}
    if wings:
        for w in (WL, WR):
            b[w] = {"rotation": track((0, SPREAD[w]), (0.35, FOLD[w], "easeInOutCubic"), (0.6, FOLD[w]))}
    anim("landing", 0.6, False, b)

    # ---------------------------------------------------------------- boost: recoil kick into sprint lean
    b = {bone: {"position": track((0, v(0, 0, 0)), (0.05, v(0, 0, 1.0 * m), "easeOutQuad"), (0.2, v(0, 0, -0.3)),
                                  (0.45, v(0, 0, 0.35), "easeInOutSine")),
                "rotation": track((0, v(6, 0, 0)), (0.05, v(-8, 0, 0)), (0.2, v(13, 0, 0)), (0.45, v(10, 0, 0), "easeInOutSine"))}
         for bone in torso}
    for bone in legs + arms:
        b[bone] = {"position": track((0, v(0, 0, 0)), (0.05, v(0, 0, 0.6)), (0.45, v(0, 0, 0), "easeOutBack"))}
    if wings:
        for w in (WL, WR):
            b[w] = {"rotation": track((0, SPREAD[w]), (0.06, scale_v(SWEPT[w], 1.2), "easeOutQuad"), (0.45, SWEPT[w]))}
    anim("boost", 0.45, False, b)
    return A


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for design in DESIGNS:
        with open(os.path.join(OUT, design.lower() + ".animation.json"), "w") as fh:
            json.dump({"format_version": "1.8.0", "animations": build(design)}, fh, separators=(",", ":"))
    print("wrote %d animation files" % len(DESIGNS))
