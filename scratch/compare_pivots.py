import json

def get_bone_map(path):
    with open(path, 'r') as f:
        data = json.load(f)
    m = {}
    for b in data['minecraft:geometry'][0]['bones']:
        m[b['name']] = {
            'parent': b.get('parent'),
            'pivot': b.get('pivot'),
            'rotation': b.get('rotation')
        }
    return m

ion = get_bone_map('Titan Combat/src/main/resources/assets/titancombat/geo/ion_titan.geo.json')
exo = get_bone_map('Titan Combat/src/main/resources/assets/titancombat/geo/exo_frame_titan.geo.json')

common = sorted(list(set(ion.keys()) & set(exo.keys())))
for name in common:
    if name.startswith('armor_'):
        continue
    i_b = ion[name]
    e_b = exo[name]
    print(f"=== {name} ===")
    print(f"  ION: parent={i_b['parent']}, pivot={i_b['pivot']}, rot={i_b['rotation']}")
    print(f"  EXO: parent={e_b['parent']}, pivot={e_b['pivot']}, rot={e_b['rotation']}")
