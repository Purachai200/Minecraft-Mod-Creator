import os, json
p = 'Titan Combat/src/main/resources/assets/titancombat/animations'
for f in ['titan_exo_titan.animation.json', 'bulwark_titan.animation.json', 'exo_frame_titan.animation.json', 'trooper_titan.animation.json']:
    path = os.path.join(p, f)
    with open(path, 'r') as jf:
        data = json.load(jf)
    anims = data.get('animations', {})
    for a_name in anims:
        if any(k in a_name for k in ['move.arm', 'fire']):
            l1 = anims[a_name].get('bones', {}).get('leftArm1', {}).get('rotation')
            if l1 == [15, 0, 18]:
                print(f'{f} -> {a_name}: leftArm1 is [15, 0, 18]!')
