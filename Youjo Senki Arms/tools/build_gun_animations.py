"""Writes one animation file per youjoarms gun (assets/youjoarms/animations/<gun>.animation.json).

  python3 tools/build_gun_animations.py            (run from the "Youjo Senki Arms" folder)

Each file is the donor's TACZ animation set with `inspect` / `inspect_empty` replaced by a real check-over:
the magazine (or break-open barrel, belt cover, pump) goes out to where its rounds can be seen, holds, and comes
back; bolt and pump guns then work the action to show the chamber. The motion is the donor's own reload
keyframes, resampled and played out-and-back, so hands and camera stay in step with the model.
"""
import json, os, re, sys, zipfile

sys.path.insert(0, os.path.dirname(__file__))
from build_gun_assets import GUNS, JAR, PACK

ANIM = "assets/tacz/custom/tacz_default_gun/assets/tacz/animations/{}.animation.json"
STEP = 1 / 30
# donor -> (reload animation to play out and back, time its magazine is clear of the gun, hold there, then work this action)
CFG = {
    "m700": ("reload_tactical", 0.8, 1.6, "bolt"),
    "m1911": ("reload_tactical", 0.7, 1.4, None),
    "hk_mp5a5": ("reload_tactical", 0.6, 1.4, None),
    "m249": ("reload_tactical", 1.9, 1.6, None),
    "rpk": ("reload_tactical", 1.15, 1.5, None),
    "m320": ("reload_empty", 0.9, 1.5, None),
    "m870": (None, 0, 0, "bolt"),
}


def key_vec(k, side):
    if isinstance(k, list):
        return k
    return k.get(side, k.get("pre" if side == "post" else "post"))


def sample(ch, t):
    """Linear sample of a keyframe dict at time t (clamped at both ends)."""
    pts = sorted((float(a), b) for a, b in ch.items())
    if t <= pts[0][0]:
        return key_vec(pts[0][1], "post")
    if t >= pts[-1][0]:
        return key_vec(pts[-1][1], "pre")
    for (t0, k0), (t1, k1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            a, b = key_vec(k0, "post"), key_vec(k1, "pre")
            f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
            return [round(x + (y - x) * f, 5) for x, y in zip(a, b)]


def segments(anims, base, T, hold, extra):
    """List of (animation, source-time function, duration) played back to back."""
    segs, at = [], 0.0
    if base:
        segs.append((anims[base], lambda t: t, 0.0, T))
        at = T
        segs.append((anims[base], lambda t: T, at, at + hold))
        at += hold
        segs.append((anims[base], lambda t, a=at: T - (t - a), at, at + T))
        at += T
    if extra:
        at += 0.15 if base else 0.0
        a0 = at
        segs.append((anims[extra], lambda t, a=a0: t - a, a0, a0 + anims[extra]["animation_length"]))
        at = a0 + anims[extra]["animation_length"]
    return segs, at


def build_inspect(anims, cfg, with_extra):
    base, T, hold, extra = cfg
    segs, length = segments(anims, base, T, hold, extra if (with_extra or not base) else None)
    out = {"animation_length": round(length + 0.2, 4), "bones": {}, "sound_effects": {}}
    chans = {}  # (bone, channel) -> {time: vec}
    for anim, f, t0, t1 in segs:
        for bone, bch in anim["bones"].items():
            for name, ch in bch.items():
                if not isinstance(ch, dict):
                    out["bones"].setdefault(bone, {}).setdefault(name, ch)  # static pose: take the first one
                    continue
                d = chans.setdefault((bone, name), {})
                n = max(1, round((t1 - t0) / STEP))
                for i in range(n + 1):
                    t = t0 + (t1 - t0) * i / n
                    d[round(t, 4)] = sample(ch, max(0.0, f(t)))
    for (bone, name), d in chans.items():
        first = min(d)
        if first > 0:  # channel only used by a later part: sit at its rest pose until then
            d[0.0] = d[first]
        out["bones"].setdefault(bone, {})[name] = {str(t): v for t, v in sorted(d.items())}
    if base:  # lift/mag-out sounds on the way out, mag-in/end sounds mirrored on the way back
        for t, e in anims[base].get("sound_effects", {}).items():
            t = float(t)
            if t <= T:
                out["sound_effects"][str(t)] = e
            elif re.search(r"mag.?in|end|close", json.dumps(e)):
                out["sound_effects"][str(round(2 * T + hold - (t - T) * 0.3 + 0.1, 3))] = e
    if extra and (with_extra or not base):
        a0 = segs[-1][2]
        for t, e in anims[extra].get("sound_effects", {}).items():
            out["sound_effects"][str(round(a0 + float(t), 3))] = e
    if not out["sound_effects"]:
        del out["sound_effects"]
    return out


def main():
    z = zipfile.ZipFile(JAR)
    os.makedirs(f"{PACK}/animations", exist_ok=True)
    for gun_id, (donor, _) in GUNS.items():
        src = json.loads(re.sub(r"^\s*//.*$", "", z.read(ANIM.format(donor)).decode("utf-8"), flags=re.M))
        anims = src["animations"]
        anims["inspect"] = build_inspect(anims, CFG[donor], True)
        anims["inspect_empty"] = build_inspect(anims, CFG[donor], False)
        json.dump(src, open(f"{PACK}/animations/{gun_id}.animation.json", "w"), separators=(",", ":"))
        dp = f"{PACK}/display/guns/{gun_id}_display.json"
        d = json.load(open(dp))
        d["animation"] = f"youjoarms:{gun_id}"
        json.dump(d, open(dp, "w"), indent=2)
        print(f"{gun_id:13} inspect {anims['inspect']['animation_length']:.2f}s  empty {anims['inspect_empty']['animation_length']:.2f}s")


if __name__ == "__main__":
    main()
