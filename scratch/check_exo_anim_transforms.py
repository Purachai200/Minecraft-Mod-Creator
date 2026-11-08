import json
with open('Titan Combat/src/main/resources/assets/titancombat/animations/exo_frame_titan.animation.json', 'r') as f:
    anims = json.load(f)
for k in ['animation.exo_frame_titan.standing', 'animation.exo_frame_titan.walk.leg', 'animation.exo_frame_titan.idle.arm']:
    if k in anims['animations']:
        print('===', k, '===')
        b = anims['animations'][k].get('bones', {})
        for name in ['body1', 'body2', 'body3', 'head', 'rightLeg3', 'rightLeg2', 'rightFoot']:
            if name in b:
                print(f"  {name} pos: {b[name].get('position')}, rot: {b[name].get('rotation')}")
