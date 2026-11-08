import json
with open('Titan Combat/src/main/resources/assets/titancombat/animations/titan_exo_titan.animation.json', 'r') as f:
    anims = json.load(f)
for anim_name in ['animation.titan_exo_titan.move.arm', 'animation.titan_exo_titan.fire', 'animation.titan_exo_titan.preview', 'animation.titan_exo_titan.standing']:
    if anim_name in anims['animations']:
        a = anims['animations'][anim_name]
        print('===', anim_name, '===')
        for b in ['rightArm1', 'rightArm2', 'rightHand', 'leftArm1', 'leftArm2', 'leftHand']:
            if b in a.get('bones', {}):
                print(f'  {b} rot: {a["bones"][b].get("rotation")}')
