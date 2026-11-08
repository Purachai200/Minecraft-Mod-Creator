import json
for name in ['trooper', 'ion', 'scorch', 'monarch']:
    p = f'Titan Combat/src/main/resources/assets/titancombat/animations/{name}_titan.animation.json'
    with open(p, 'r') as f:
        anims = json.load(f)
    key = f'animation.{name}_titan.idle.arm'
    if key in anims['animations']:
        arm = anims['animations'][key]
        print(f'{name} idle.arm:')
        for b in ['rightArm1', 'rightArm2', 'rightHand', 'leftArm1', 'leftArm2', 'leftHand']:
            if b in arm.get('bones', {}):
                print(f'  {b} rot: {arm["bones"][b].get("rotation")}')
