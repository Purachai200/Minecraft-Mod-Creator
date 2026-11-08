import json

def get_arm_bones(name):
    p = f'Titan Combat/src/main/resources/assets/titancombat/geo/{name}_titan.geo.json'
    with open(p, 'r') as f:
        geo = json.load(f)
    model = geo['minecraft:geometry'][0]
    res = {}
    for b in model['bones']:
        if b['name'] in ['body3', 'rightArm1', 'rightArm2', 'rightHand', 'weapon', 'leftArm1', 'leftArm2', 'leftHand']:
            res[b['name']] = {
                'parent': b.get('parent'),
                'pivot': b.get('pivot'),
                'rotation': b.get('rotation')
            }
    return res

print("ION:")
import pprint
pprint.pprint(get_arm_bones('ion'))
print("\nTITAN_EXO:")
pprint.pprint(get_arm_bones('titan_exo'))
