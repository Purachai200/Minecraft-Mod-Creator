"""Inject footstep sound keyframes into the titan walk/run animations.

Touchdown times were measured in tools/model_viewer.html (the moment each foot's
lowest point reaches the ground). GeckoLib fires these as sound keyframes and
TitanRenderer turns them into footstep audio, dust and cockpit shake, so the
sound always lands exactly when the foot does, at any playback speed.

Run from the project root:  python3 tools/add_step_keyframes.py
"""
import json
import os

ANIM_DIR = os.path.join("src", "main", "resources", "assets", "titancombat", "animations")

# titan -> {animation: [(time_seconds, side), ...]}
STEPS = {
    "ion":       {"walk.leg": [(0.5, "left"), (1.5, "right")],      "move.leg": [(0.391, "left"), (1.016, "right")]},
    "scorch":    {"walk.leg": [(0.667, "left"), (1.667, "right")],  "move.leg": [(0.457, "left"), (1.117, "right")]},
    "ronin":     {"walk.leg": [(0.479, "right"), (1.604, "left")],  "move.leg": [(0.43, "right"), (0.951, "left")]},
    "tone":      {"walk.leg": [(0.583, "left"), (1.583, "right")],  "move.leg": [(0.443, "left"), (1.068, "right")]},
    "legion":    {"walk.leg": [(0.625, "left"), (1.625, "right")],  "move.leg": [(0.457, "left"), (1.117, "right")]},
    "monarch":   {"walk.leg": [(0.646, "left"), (1.646, "right")],  "move.leg": [(0.508, "left"), (1.133, "right")]},
    "northstar": {"walk.leg": [(0.563, "right"), (1.563, "left")],  "move.leg": [(0.417, "right"), (0.951, "left")]},
}


def main():
    for titan, anims in STEPS.items():
        path = os.path.join(ANIM_DIR, f"{titan}_titan.animation.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for anim, steps in anims.items():
            key = f"animation.{titan}_titan.{anim}"
            effects = {}
            for t, side in steps:
                effect = ("run_step_" if anim == "move.leg" else "step_") + side
                effects[f"{t:.4f}"] = {"effect": effect}
            data["animations"][key]["sound_effects"] = effects
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, separators=(",", ":"), ensure_ascii=False)
        print("updated", path)


if __name__ == "__main__":
    main()
