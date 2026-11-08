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

trooper = get_bone_map('Titan Combat/src/main/resources/assets/titancombat/geo/trooper_titan.geo.json')
ion = get_bone_map('Titan Combat/src/main/resources/assets/titancombat/geo/ion_titan.geo.json')

common = sorted(list(set(ion.keys()) & set(trooper.keys())))
for name in ['body1', 'body2', 'body3', 'rightArm1', 'rightArm2', 'rightHand', 'rightLeg3', 'rightLeg2', 'rightLeg1', 'rightFoot']:
    if name in trooper:
        t_b = trooper[name]
        i_b = ion[name]
        print(f"=== {name} ===")
        print(f"  ION:     piv={i_b['pivot']}, rot={i_b['rotation']}")
        print(f"  TROOPER: piv={t_b['pivot']}, rot={t_b['rotation']}")
