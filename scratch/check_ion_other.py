import json
with open('Titan Combat/src/main/resources/assets/titancombat/animations/ion_titan.animation.json', 'r') as f:
    anims = json.load(f)
for k in ['animation.ion_titan.move.arm', 'animation.ion_titan.fire']:
    if k in anims['animations']:
        print(f"=== {k} ===")
        b = anims['animations'][k]['bones']
        for name in ['rightArm1', 'rightArm2', 'rightHand', 'leftArm1', 'leftArm2', 'leftHand']:
            if name in b:
                print(f"  {name}: {b[name].get('rotation')}")
