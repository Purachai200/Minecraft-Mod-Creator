import os, json
p = 'Titan Combat/src/main/resources/assets/titancombat/animations'
for f in os.listdir(p):
    if f.endswith('.animation.json'):
        path = os.path.join(p, f)
        with open(path, 'r') as jf:
            try:
                data = json.load(jf)
            except Exception:
                continue
        anims = data.get('animations', {})
        for a_name, a in anims.items():
            if 'idle.arm' in a_name:
                bones = a.get('bones', {})
                l1 = bones.get('leftArm1', {}).get('rotation')
                r1 = bones.get('rightArm1', {}).get('rotation')
                if l1 == [15, 0, 18]:
                    print(f'{f} -> {a_name}: leftArm1 is [15, 0, 18]! (BROKEN)')
