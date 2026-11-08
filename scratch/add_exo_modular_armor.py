import os
import json
import sys
sys.path.insert(0, "scratch")
from build_modular_armor_geos import make_biped_armor_bones

ROOT = "Titan Combat/src/main/resources/assets/titancombat/geo"
fpath = os.path.join(ROOT, "exo_frame_titan.geo.json")

with open(fpath, "r", encoding="utf-8") as f:
    data = json.load(f)

bones = data["minecraft:geometry"][0]["bones"]
old_names = {"armor_head", "armor_chest", "armor_left_arm", "armor_right_arm", "armor_left_leg", "armor_right_leg"}
bones = [b for b in bones if not (b["name"] in old_names or b["name"].startswith("armor_"))]

# Generate all 8 modular armor sets for the Knightmare Frame
new_armor_bones = make_biped_armor_bones(scale=1.0)
bones.extend(new_armor_bones)

data["minecraft:geometry"][0]["bones"] = bones

with open(fpath, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Updated {fpath} with all 8 modular armor archetypes! Total bones: {len(bones)}")
