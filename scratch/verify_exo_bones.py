import json

with open("Titan Combat/src/main/resources/assets/titancombat/geo/exo_frame_titan.geo.json", "r") as f:
    geo = json.load(f)
geo_bones = set(b["name"] for b in geo["minecraft:geometry"][0]["bones"])

with open("Titan Combat/src/main/resources/assets/titancombat/animations/exo_frame_titan.animation.json", "r") as f:
    anims = json.load(f)

missing = set()
for a_name, a in anims["animations"].items():
    for b_name in a.get("bones", {}):
        if b_name not in geo_bones:
            missing.add(b_name)

print("Bone names in anims missing in geo:", missing)
