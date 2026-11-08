import json, os

ION_PATH = 'Titan Combat/src/main/resources/assets/titancombat/animations/ion_titan.animation.json'
with open(ION_PATH, 'r') as f:
    ion = json.load(f)

ion_idle_arm = ion['animations']['animation.ion_titan.idle.arm']['bones']
ion_move_arm = ion['animations']['animation.ion_titan.move.arm']['bones']
ion_fire_arm = ion['animations']['animation.ion_titan.fire']['bones']

LEFT_ARM_BONES = [
    'leftArm1', 'leftArm2', 'leftHand',
    'leftBigFinger1', 'leftBigFinger2',
    'leftEatFinger1', 'leftEatFinger2', 'leftEatFinger3',
    'leftMidFinger1', 'leftMidFinger2', 'leftMidFinger3',
    'leftLitFinger1', 'leftLitFinger2', 'leftLitFinger3'
]

targets = [
    ('titan_exo_titan.animation.json', 'titan_exo_titan'),
    ('trooper_titan.animation.json', 'trooper_titan'),
    ('bulwark_titan.animation.json', 'bulwark_titan'),
    ('exo_frame_titan.animation.json', 'exo_frame_titan')
]

for filename, prefix in targets:
    p = os.path.join('Titan Combat/src/main/resources/assets/titancombat/animations', filename)
    if not os.path.exists(p):
        continue
    with open(p, 'r') as f:
        data = json.load(f)

    anims = data.get('animations', {})

    # Fix idle.arm
    idle_key = f'animation.{prefix}.idle.arm'
    if idle_key in anims:
        bones = anims[idle_key].setdefault('bones', {})
        for b in LEFT_ARM_BONES:
            if b in ion_idle_arm:
                bones[b] = ion_idle_arm[b]
        print(f"Fixed {idle_key}")

    # Fix move.arm
    move_key = f'animation.{prefix}.move.arm'
    if move_key in anims:
        bones = anims[move_key].setdefault('bones', {})
        for b in LEFT_ARM_BONES:
            if b in ion_move_arm:
                bones[b] = ion_move_arm[b]
        print(f"Fixed {move_key}")

    # Fix fire
    fire_key = f'animation.{prefix}.fire'
    if fire_key in anims:
        bones = anims[fire_key].setdefault('bones', {})
        for b in LEFT_ARM_BONES:
            if b in ion_fire_arm:
                bones[b] = ion_fire_arm[b]
        print(f"Fixed {fire_key}")

    with open(p, 'w') as f:
        json.dump(data, f, indent=2)

print("Done updating animation arm poses.")
