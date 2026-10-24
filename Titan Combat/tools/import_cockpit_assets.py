"""Import the first-person cockpit assets from the reference Bedrock addon into the mod.

Copies, for every titan, the first-person arm/weapon geometry and its 1st-person animations,
plus the shared cockpit cabin (frame + instrument base) geometry and textures. Animations are
sanitised for GeckoLib on Java: Bedrock-only keys (particles, sounds, timelines) are dropped and
Molang that GeckoLib can't evaluate (entity properties, variables, string args) is flattened.

Run from the project root:  python3 tools/import_cockpit_assets.py
"""
import json
import os
import re
import shutil

SRC = os.path.join("reference_addon", "respack_coldsink_ttf2")
DST = os.path.join("src", "main", "resources", "assets", "titancombat")
TITANS = ["ion", "scorch", "ronin", "tone", "legion", "monarch", "northstar"]

ALLOWED_IDENT = re.compile(r"^(math\.(sin|cos|abs|clamp|lerp|min|max|floor|ceil|round|sqrt|pow|pi|mod|trunc)|"
                           r"q(uery)?\.(anim_time|life_time))$")


def load(path):
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", text))


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"), ensure_ascii=False)


def clean_expr(value):
    if not isinstance(value, str):
        return value
    expr = value.strip()
    expr = re.sub(r"(?i)\bmath\.", "math.", expr)
    expr = re.sub(r"(?i)\bquery\.", "query.", expr)
    # math.random(a, b) * wave  ->  half-range amplitude, keeps the shake without randomness
    expr = re.sub(r"math\.random\(\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\)",
                  lambda m: repr((float(m.group(2)) - float(m.group(1))) / 2.0), expr)
    idents = re.findall(r"[a-zA-Z_][a-zA-Z_0-9]*(?:\.[a-zA-Z_][a-zA-Z_0-9]*)+", expr)
    if "'" in expr or any(not ALLOWED_IDENT.match(i) for i in idents):
        return 0
    try:
        return float(expr)
    except ValueError:
        return expr


def clean_channel(channel):
    if isinstance(channel, list):
        return [clean_expr(v) for v in channel]
    if isinstance(channel, dict):
        out = {}
        for key, frame in channel.items():
            if isinstance(frame, dict):
                frame = {k: (clean_channel(v) if k in ("pre", "post") else v) for k, v in frame.items()}
            elif isinstance(frame, list):
                frame = clean_channel(frame)
            else:
                frame = clean_expr(frame)
            out[key] = frame
        return out
    return clean_expr(channel)


def clean_animations(anims):
    out = {}
    for name, anim in anims.items():
        anim = {k: v for k, v in anim.items() if k not in ("particle_effects", "sound_effects", "timeline")}
        if isinstance(anim.get("animation_length"), str):
            anim.pop("animation_length")
        bones = {}
        for bone, chans in anim.get("bones", {}).items():
            bones[bone] = {c: clean_channel(v) for c, v in chans.items() if c in ("rotation", "position", "scale")}
        anim["bones"] = bones
        out[name] = anim
    return out


def main():
    cabin_anims = load(os.path.join(SRC, "animations", "titan", "titan_all.animation.json"))["animations"]
    bob = clean_animations({k: cabin_anims[k] for k in ("animation.cabin_walk", "animation.cabin_run")})

    for t in TITANS:
        geo = load(os.path.join(SRC, "models", "entity", "titan", t, f"{t}_titan.1st.geo.json"))
        save(os.path.join(DST, "geo", "cockpit", f"{t}_titan_1st.geo.json"), geo)

        anims = load(os.path.join(SRC, "animations", "titan", t, f"{t}_titan.1st.animation.json"))
        merged = clean_animations(anims["animations"])
        merged.update(bob)  # cabin sway lives in the same file so one controller set can drive it
        save(os.path.join(DST, "animations", "cockpit", f"{t}_titan_1st.animation.json"),
             {"format_version": "1.8.0", "animations": merged})
        print("imported", t)

    cabin_dir = os.path.join(SRC, "models", "entity", "titan", "z_other", "cabin")
    for name in ("titan_cabin_base", "titan_cabin_frame"):
        save(os.path.join(DST, "geo", "cockpit", f"{name}.geo.json"), load(os.path.join(cabin_dir, f"{name}.geo.json")))
    save(os.path.join(DST, "animations", "cockpit", "titan_cabin.animation.json"), {"format_version": "1.8.0", "animations": bob})

    tex_dst = os.path.join(DST, "textures", "entity", "cockpit")
    os.makedirs(tex_dst, exist_ok=True)
    tex_src = os.path.join(SRC, "textures", "entity", "titan")
    shutil.copy(os.path.join(tex_src, "titan_cabin_base_normal.png"), os.path.join(tex_dst, "titan_cabin_base.png"))
    shutil.copy(os.path.join(tex_src, "titan_cabin_black.png"), os.path.join(tex_dst, "titan_cabin_frame.png"))
    print("imported cabin")


if __name__ == "__main__":
    main()
