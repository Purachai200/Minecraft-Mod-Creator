import json
import os
import struct
import zlib
import copy
import math

def create_solid_png(width, height, color_func):
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # filter type 0 (None)
        for x in range(width):
            r, g, b, a = color_func(x, y)
            raw_data.extend([int(r) & 255, int(g) & 255, int(b) & 255, int(a) & 255])

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(bytes(raw_data), level=9))
    iend = chunk(b'IEND', b'')
    return header + ihdr + idat + iend

ROOT = 'Titan Combat/src/main/resources/assets/titancombat'
RECIPE_DIR = 'Titan Combat/src/main/resources/data/titancombat/recipes'
GEO_DIR = os.path.join(ROOT, 'geo')
ANIM_DIR = os.path.join(ROOT, 'animations')
TEX_DIR = os.path.join(ROOT, 'textures/entity/titan')
ITEM_TEX_DIR = os.path.join(ROOT, 'textures/item')
ITEM_MODEL_DIR = os.path.join(ROOT, 'models/item')

base_geo_path = os.path.join(GEO_DIR, 'trooper_titan.geo.json')
base_anim_path = os.path.join(ANIM_DIR, 'trooper_titan.animation.json')

with open(base_geo_path, 'r') as f:
    trooper_geo = json.load(f)

with open(base_anim_path, 'r') as f:
    trooper_anim = json.load(f)

# Helper for modular armor bones
def make_armor_bones(scale=1.0, is_spider=False):
    if is_spider:
        armor_head = {
            'name': 'armor_head',
            'parent': 'doorUp',
            'pivot': [0.0, 54.0, -6.0],
            'cubes': [
                {'origin': [-8.0 * scale, 53.0, -11.0], 'size': [16.0 * scale, 4.0, 10.0], 'uv': [120, 40]}
            ]
        }
        armor_chest = {
            'name': 'armor_chest',
            'parent': 'body3',
            'pivot': [0.0, 50.0, 0.0],
            'cubes': [
                {'origin': [-14.0 * scale, 46.0, -12.0], 'size': [28.0 * scale, 10.0, 22.0], 'uv': [120, 64]}
            ]
        }
        armor_left_arm = {
            'name': 'armor_left_arm',
            'parent': 'leftArm1',
            'pivot': [20.0, 50.0, -6.0],
            'cubes': [{'origin': [18.0, 44.0, -12.0], 'size': [10.0 * scale, 12.0, 12.0], 'uv': [200, 64]}]
        }
        armor_right_arm = {
            'name': 'armor_right_arm',
            'parent': 'rightArm1',
            'pivot': [-20.0, 50.0, -6.0],
            'cubes': [{'origin': [-18.0 - 10.0 * scale, 44.0, -12.0], 'size': [10.0 * scale, 12.0, 12.0], 'uv': [200, 64]}]
        }
        armor_left_leg = {
            'name': 'armor_left_leg',
            'parent': 'leftLeg2',
            'pivot': [28.0, 52.0, -16.0],
            'cubes': [{'origin': [26.0, 48.0, -22.0], 'size': [10.0 * scale, 12.0, 12.0], 'uv': [200, 90]}]
        }
        armor_right_leg = {
            'name': 'armor_right_leg',
            'parent': 'rightLeg2',
            'pivot': [-28.0, 52.0, -16.0],
            'cubes': [{'origin': [-26.0 - 10.0 * scale, 48.0, -22.0], 'size': [10.0 * scale, 12.0, 12.0], 'uv': [200, 90]}]
        }
    else:
        armor_head = {
            'name': 'armor_head',
            'parent': 'doorUp',
            'pivot': [0.0, 107.0, -10.0],
            'cubes': [
                {'origin': [-8.0 * scale, 98.0, -18.0], 'size': [16.0 * scale, 13.0, 6.0], 'uv': [120, 40]},
                {'origin': [-5.0 * scale, 111.0, -16.0], 'size': [10.0 * scale, 4.0, 5.0], 'uv': [160, 40]}
            ]
        }
        armor_chest = {
            'name': 'armor_chest',
            'parent': 'body3',
            'pivot': [0.0, 85.0, 0.0],
            'cubes': [
                {'origin': [-15.0 * scale, 75.0, -15.0], 'size': [30.0 * scale, 20.0, 7.0], 'uv': [120, 64]},
                {'origin': [-12.0 * scale, 70.0, -13.0], 'size': [24.0 * scale, 8.0, 5.0], 'uv': [120, 90]}
            ]
        }
        armor_left_arm = {
            'name': 'armor_left_arm',
            'parent': 'leftArm1',
            'pivot': [24.4, 94.8, 10.7],
            'cubes': [{'origin': [22.0, 86.0, 3.0], 'size': [12.0 * scale, 14.0, 14.0], 'uv': [200, 64]}]
        }
        armor_right_arm = {
            'name': 'armor_right_arm',
            'parent': 'rightArm1',
            'pivot': [-24.4, 94.8, 10.7],
            'cubes': [{'origin': [-22.0 - 12.0 * scale, 86.0, 3.0], 'size': [12.0 * scale, 14.0, 14.0], 'uv': [200, 64]}]
        }
        armor_left_leg = {
            'name': 'armor_left_leg',
            'parent': 'leftLeg2',
            'pivot': [14.8, 43.5, 2.7],
            'cubes': [{'origin': [10.0, 24.0, -5.0], 'size': [10.0 * scale, 19.0, 13.0], 'uv': [200, 90]}]
        }
        armor_right_leg = {
            'name': 'armor_right_leg',
            'parent': 'rightLeg2',
            'pivot': [-14.5, 43.5, 2.7],
            'cubes': [{'origin': [-10.0 - 10.0 * scale, 24.0, -5.0], 'size': [10.0 * scale, 19.0, 13.0], 'uv': [200, 90]}]
        }
    return [armor_head, armor_chest, armor_left_arm, armor_right_arm, armor_left_leg, armor_right_leg]

# =========================================================================
# 1. TERRAIN GROUND FRAME
# Features: Military tactical ground armor, caterpillar tank treads on calves
# =========================================================================
def build_terrain_frame_geo():
    geo = copy.deepcopy(trooper_geo)
    geom = geo['minecraft:geometry'][0]
    geom['description']['identifier'] = 'geometry.terrain_frame_titan'
    bones = geom['bones']
    bmap = {b['name']: b for b in bones}

    # Add Caterpillar Tank Treads on Calves (leftLeg1 / rightLeg1)
    left_leg1 = bmap['leftLeg1']
    left_treads = [
        {'origin': [9.0, 10.0, 4.5], 'size': [10.0, 24.0, 8.0], 'uv': [300, 10]},
        {'origin': [8.5, 26.0, 5.0], 'size': [11.0, 7.0, 7.0], 'uv': [340, 10]},
        {'origin': [8.5, 11.0, 5.0], 'size': [11.0, 7.0, 7.0], 'uv': [340, 26]},
        {'origin': [8.8, 18.0, 5.5], 'size': [10.4, 6.0, 6.0], 'uv': [340, 42]},
        {'origin': [8.2, 9.0, 3.8], 'size': [11.6, 26.0, 9.4], 'uv': [300, 45]}
    ]
    left_leg1['cubes'].extend(left_treads)

    right_leg1 = bmap['rightLeg1']
    right_treads = [
        {'origin': [-19.0, 10.0, 4.5], 'size': [10.0, 24.0, 8.0], 'uv': [300, 10]},
        {'origin': [-19.5, 26.0, 5.0], 'size': [11.0, 7.0, 7.0], 'uv': [340, 10]},
        {'origin': [-19.5, 11.0, 5.0], 'size': [11.0, 7.0, 7.0], 'uv': [340, 26]},
        {'origin': [-19.2, 18.0, 5.5], 'size': [10.4, 6.0, 6.0], 'uv': [340, 42]},
        {'origin': [-19.8, 9.0, 3.8], 'size': [11.6, 26.0, 9.4], 'uv': [300, 45]}
    ]
    right_leg1['cubes'].extend(right_treads)

    # Add Heavy Angular Knee Guards to leftLeg2 / rightLeg2
    bmap['leftLeg2']['cubes'].append(
        {'origin': [9.0, 38.0, -6.5], 'size': [10.0, 8.0, 3.5], 'uv': [380, 10]}
    )
    bmap['rightLeg2']['cubes'].append(
        {'origin': [-19.0, 38.0, -6.5], 'size': [10.0, 8.0, 3.5], 'uv': [380, 10]}
    )

    # Add Stomp Claws on Feet
    bmap['leftFoot']['cubes'].append(
        {'origin': [9.0, 0.0, -18.0], 'size': [11.0, 6.0, 6.0], 'uv': [380, 30]}
    )
    bmap['rightFoot']['cubes'].append(
        {'origin': [-20.0, 0.0, -18.0], 'size': [11.0, 6.0, 6.0], 'uv': [380, 30]}
    )

    # Add Tactical Sensor Turret on body3
    body3 = bmap['body3']
    body3['cubes'].extend([
        {'origin': [-14.0, 76.0, -14.0], 'size': [28.0, 18.0, 4.0], 'uv': [380, 50]},
        {'origin': [-10.0, 113.0, -10.0], 'size': [8.0, 5.0, 8.0], 'uv': [420, 10]},
        {'origin': [-9.0, 114.0, -13.0], 'size': [6.0, 3.0, 4.0], 'uv': [420, 26]},
        {'origin': [8.0, 94.0, 22.0], 'size': [6.0, 14.0, 4.0], 'uv': [420, 36]},
        {'origin': [-14.0, 94.0, 22.0], 'size': [6.0, 14.0, 4.0], 'uv': [420, 36]}
    ])

    # Modular Armor Bones
    bones.extend(make_armor_bones(scale=1.05))
    return geo

# =========================================================================
# 2. CYCLOPS INDUSTRIAL ENFORCER FRAME
# Features: Glowing cyan cyclops eye dome, hunched gorilla stance, 4-claw feet
# =========================================================================
def build_cyclops_frame_geo():
    geo = copy.deepcopy(trooper_geo)
    geom = geo['minecraft:geometry'][0]
    geom['description']['identifier'] = 'geometry.cyclops_frame_titan'
    bones = geom['bones']
    bmap = {b['name']: b for b in bones}

    # Cyclops Central Eye on 'eye' bone
    eye = bmap['eye']
    eye['cubes'] = [
        {'origin': [-6.0, 101.0, -19.0], 'size': [12.0, 12.0, 4.0], 'uv': [450, 10]},
        {'origin': [-4.5, 102.5, -21.0], 'size': [9.0, 9.0, 4.0], 'uv': [12, 12]},
        {'origin': [-2.0, 105.0, -22.0], 'size': [4.0, 4.0, 2.0], 'uv': [16, 16]}
    ]

    # Torso: Hunched Gorilla Posture & Dual Industrial Smokestacks
    body3 = bmap['body3']
    body3['cubes'].extend([
        {'origin': [-16.0, 72.0, -16.0], 'size': [32.0, 22.0, 9.0], 'uv': [450, 30]},
        {'origin': [11.0, 102.0, 22.0], 'size': [6.0, 24.0, 6.0], 'uv': [450, 65]},
        {'origin': [10.0, 124.0, 21.0], 'size': [8.0, 4.0, 8.0], 'uv': [450, 98]},
        {'origin': [-17.0, 102.0, 22.0], 'size': [6.0, 24.0, 6.0], 'uv': [450, 65]},
        {'origin': [-18.0, 124.0, 21.0], 'size': [8.0, 4.0, 8.0], 'uv': [450, 98]}
    ])

    # Massive Industrial Shoulders
    bmap['leftArm1']['cubes'].append(
        {'origin': [21.0, 86.0, 1.0], 'size': [14.0, 16.0, 16.0], 'uv': [500, 10]}
    )
    bmap['rightArm1']['cubes'].append(
        {'origin': [-35.0, 86.0, 1.0], 'size': [14.0, 16.0, 16.0], 'uv': [500, 10]}
    )

    # 4-Toed Outrigger Stabilizing Feet
    def make_cyclops_foot(is_left):
        cx = 14.8 if is_left else -14.5
        return [
            {'origin': [cx - 6.0, 0.0, -10.0], 'size': [12.0, 8.0, 18.0], 'uv': [500, 45]},
            {'origin': [cx - 4.0, 0.0, -18.0], 'size': [8.0, 7.0, 9.0], 'uv': [500, 75]},
            {'origin': [cx + 5.0, 0.0, -8.0], 'size': [6.0, 6.0, 14.0], 'uv': [500, 95]},
            {'origin': [cx - 11.0, 0.0, -8.0], 'size': [6.0, 6.0, 14.0], 'uv': [500, 95]},
            {'origin': [cx - 4.0, 0.0, 7.0], 'size': [8.0, 7.0, 8.0], 'uv': [500, 75]}
        ]

    bmap['leftFoot']['cubes'] = make_cyclops_foot(True)
    bmap['rightFoot']['cubes'] = make_cyclops_foot(False)

    # Modular Armor Bones
    bones.extend(make_armor_bones(scale=1.20))
    return geo

# =========================================================================
# 3. SPIDER QUADRUPED ANTI-TANK FRAME
# Features: 4 articulated spider legs, low-slung chassis, 360 sensor dome
# =========================================================================
def build_spider_frame_geo():
    geo = copy.deepcopy(trooper_geo)
    geom = geo['minecraft:geometry'][0]
    geom['description']['identifier'] = 'geometry.spider_frame_titan'
    bones = geom['bones']
    bmap = {b['name']: b for b in bones}

    # Low-slung chassis adjustment
    bmap['body1']['pivot'] = [0.0, 44.0, 4.0]
    bmap['body1']['cubes'] = [
        {'origin': [-16.0, 36.0, -14.0], 'size': [32.0, 10.0, 36.0], 'uv': [550, 10]}
    ]

    bmap['body2']['pivot'] = [0.0, 48.0, 4.0]
    bmap['body2']['cubes'] = [
        {'origin': [-14.0, 44.0, -12.0], 'size': [28.0, 8.0, 32.0], 'uv': [550, 60]}
    ]

    bmap['body3']['pivot'] = [0.0, 52.0, 6.0]
    bmap['body3']['cubes'] = [
        {'origin': [-12.0, 50.0, -10.0], 'size': [24.0, 8.0, 28.0], 'uv': [550, 105]},
        {'origin': [-10.0, 42.0, 18.0], 'size': [20.0, 14.0, 16.0], 'uv': [620, 10]},
        {'origin': [-8.0, 54.0, 20.0], 'size': [16.0, 4.0, 12.0], 'uv': [620, 42]}
    ]

    # Low-profile spider cockpit hatch on doorUp / doorDown
    bmap['doorUp']['pivot'] = [0.0, 54.0, -6.0]
    bmap['doorUp']['cubes'] = [
        {'origin': [-7.0, 52.0, -10.0], 'size': [14.0, 3.0, 10.0], 'uv': [550, 40]}
    ]
    bmap['doorDown']['pivot'] = [0.0, 42.0, -6.0]
    bmap['doorDown']['cubes'] = [
        {'origin': [-6.0, 38.0, -8.0], 'size': [12.0, 3.0, 8.0], 'uv': [550, 55]}
    ]

    # 360 Sensor Ball Turret on eye
    eye = bmap['eye']
    eye['pivot'] = [0.0, 58.0, -4.0]
    eye['cubes'] = [
        {'origin': [-7.0, 54.0, -8.0], 'size': [14.0, 4.0, 14.0], 'uv': [620, 60]},
        {'origin': [-5.0, 57.0, -6.0], 'size': [10.0, 6.0, 10.0], 'uv': [620, 80]},
        {'origin': [-5.5, 58.0, -6.5], 'size': [11.0, 3.0, 11.0], 'uv': [12, 12]}
    ]

    # Arms / Weapon hardpoints repositioned for spider hull
    bmap['rightArm1']['pivot'] = [-18.0, 50.0, -6.0]
    bmap['leftArm1']['pivot'] = [18.0, 50.0, -6.0]

    # Front-Left Leg
    bmap['leftLeg3']['pivot'] = [15.0, 44.0, -10.0]
    bmap['leftLeg3']['cubes'] = [
        {'origin': [14.0, 42.0, -12.0], 'size': [14.0, 6.0, 6.0], 'uv': [660, 10]}
    ]
    bmap['leftLeg2']['pivot'] = [28.0, 48.0, -14.0]
    bmap['leftLeg2']['cubes'] = [
        {'origin': [26.0, 44.0, -17.0], 'size': [8.0, 16.0, 8.0], 'uv': [660, 24]}
    ]
    bmap['leftLeg1']['pivot'] = [32.0, 36.0, -18.0]
    bmap['leftLeg1']['cubes'] = [
        {'origin': [30.0, 8.0, -22.0], 'size': [6.0, 28.0, 6.0], 'uv': [660, 50]}
    ]
    bmap['leftFoot']['pivot'] = [33.0, 8.0, -22.0]
    bmap['leftFoot']['cubes'] = [
        {'origin': [28.0, 0.0, -26.0], 'size': [10.0, 8.0, 10.0], 'uv': [660, 86]}
    ]

    # Front-Right Leg
    bmap['rightLeg3']['pivot'] = [-15.0, 44.0, -10.0]
    bmap['rightLeg3']['cubes'] = [
        {'origin': [-28.0, 42.0, -12.0], 'size': [14.0, 6.0, 6.0], 'uv': [660, 10]}
    ]
    bmap['rightLeg2']['pivot'] = [-28.0, 48.0, -14.0]
    bmap['rightLeg2']['cubes'] = [
        {'origin': [-34.0, 44.0, -17.0], 'size': [8.0, 16.0, 8.0], 'uv': [660, 24]}
    ]
    bmap['rightLeg1']['pivot'] = [-32.0, 36.0, -18.0]
    bmap['rightLeg1']['cubes'] = [
        {'origin': [-36.0, 8.0, -22.0], 'size': [6.0, 28.0, 6.0], 'uv': [660, 50]}
    ]
    bmap['rightFoot']['pivot'] = [-33.0, 8.0, -22.0]
    bmap['rightFoot']['cubes'] = [
        {'origin': [-38.0, 0.0, -26.0], 'size': [10.0, 8.0, 10.0], 'uv': [660, 86]}
    ]

    # Rear-Left Leg
    rear_left_leg3 = {
        'name': 'rearLeftLeg3',
        'parent': 'titan',
        'pivot': [15.0, 44.0, 18.0],
        'cubes': [{'origin': [14.0, 42.0, 16.0], 'size': [14.0, 6.0, 6.0], 'uv': [700, 10]}]
    }
    rear_left_leg2 = {
        'name': 'rearLeftLeg2',
        'parent': 'rearLeftLeg3',
        'pivot': [28.0, 48.0, 22.0],
        'cubes': [{'origin': [26.0, 44.0, 19.0], 'size': [8.0, 16.0, 8.0], 'uv': [700, 24]}]
    }
    rear_left_leg1 = {
        'name': 'rearLeftLeg1',
        'parent': 'rearLeftLeg2',
        'pivot': [32.0, 36.0, 26.0],
        'cubes': [{'origin': [30.0, 8.0, 24.0], 'size': [6.0, 28.0, 6.0], 'uv': [700, 50]}]
    }
    rear_left_foot = {
        'name': 'rearLeftFoot',
        'parent': 'rearLeftLeg1',
        'pivot': [33.0, 8.0, 26.0],
        'cubes': [{'origin': [28.0, 0.0, 22.0], 'size': [10.0, 8.0, 10.0], 'uv': [700, 86]}]
    }

    # Rear-Right Leg
    rear_right_leg3 = {
        'name': 'rearRightLeg3',
        'parent': 'titan',
        'pivot': [-15.0, 44.0, 18.0],
        'cubes': [{'origin': [-28.0, 42.0, 16.0], 'size': [14.0, 6.0, 6.0], 'uv': [700, 10]}]
    }
    rear_right_leg2 = {
        'name': 'rearRightLeg2',
        'parent': 'rearRightLeg3',
        'pivot': [-28.0, 48.0, 22.0],
        'cubes': [{'origin': [-34.0, 44.0, 19.0], 'size': [8.0, 16.0, 8.0], 'uv': [700, 24]}]
    }
    rear_right_leg1 = {
        'name': 'rearRightLeg1',
        'parent': 'rearRightLeg2',
        'pivot': [-32.0, 36.0, 26.0],
        'cubes': [{'origin': [-36.0, 8.0, 24.0], 'size': [6.0, 28.0, 6.0], 'uv': [700, 50]}]
    }
    rear_right_foot = {
        'name': 'rearRightFoot',
        'parent': 'rearRightLeg1',
        'pivot': [-33.0, 8.0, 26.0],
        'cubes': [{'origin': [-38.0, 0.0, 22.0], 'size': [10.0, 8.0, 10.0], 'uv': [700, 86]}]
    }

    bones.extend([rear_left_leg3, rear_left_leg2, rear_left_leg1, rear_left_foot,
                  rear_right_leg3, rear_right_leg2, rear_right_leg1, rear_right_foot])

    # Modular Armor Bones
    bones.extend(make_armor_bones(scale=1.1, is_spider=True))
    return geo

# Build and write geo files
geo_configs = [
    ('terrain_frame_titan', build_terrain_frame_geo()),
    ('cyclops_frame_titan', build_cyclops_frame_geo()),
    ('spider_frame_titan', build_spider_frame_geo())
]

for fid, gdata in geo_configs:
    target_path = os.path.join(GEO_DIR, f"{fid}.geo.json")
    with open(target_path, 'w') as f:
        json.dump(gdata, f, indent=2)
    print(f"Generated {target_path}")

# =========================================================================
# ANIMATION GENERATION
# =========================================================================
for fid in ['terrain_frame_titan', 'cyclops_frame_titan']:
    new_anim = copy.deepcopy(trooper_anim)
    orig_anims = new_anim.get('animations', {})
    re_anims = {}
    for anim_name, anim_data in orig_anims.items():
        mapped_name = anim_name.replace('trooper_titan', fid)
        re_anims[mapped_name] = anim_data
    new_anim['animations'] = re_anims

    target_anim = os.path.join(ANIM_DIR, f"{fid}.animation.json")
    with open(target_anim, 'w') as f:
        json.dump(new_anim, f, indent=2)
    print(f"Generated {target_anim}")

# Spider crawl animation
spider_anim = copy.deepcopy(trooper_anim)
re_spider_anims = {}
for anim_name, anim_data in spider_anim.get('animations', {}).items():
    mapped_name = anim_name.replace('trooper_titan', 'spider_frame_titan')
    re_spider_anims[mapped_name] = anim_data

quadruped_walk_bones = {
    'leftLeg3': {
        'rotation': {
            '0.0': [14.0, 0.0, 0.0],
            '0.25': [-18.0, 0.0, 0.0],
            '0.5': [-10.0, 0.0, 0.0],
            '0.75': [8.0, 0.0, 0.0],
            '1.0': [14.0, 0.0, 0.0]
        }
    },
    'leftLeg2': {
        'rotation': {
            '0.0': [-10.0, 0.0, 0.0],
            '0.25': [15.0, 0.0, 0.0],
            '0.5': [5.0, 0.0, 0.0],
            '0.75': [-5.0, 0.0, 0.0],
            '1.0': [-10.0, 0.0, 0.0]
        }
    },
    'rearRightLeg3': {
        'rotation': {
            '0.0': [14.0, 0.0, 0.0],
            '0.25': [-18.0, 0.0, 0.0],
            '0.5': [-10.0, 0.0, 0.0],
            '0.75': [8.0, 0.0, 0.0],
            '1.0': [14.0, 0.0, 0.0]
        }
    },
    'rearRightLeg2': {
        'rotation': {
            '0.0': [-10.0, 0.0, 0.0],
            '0.25': [15.0, 0.0, 0.0],
            '0.5': [5.0, 0.0, 0.0],
            '0.75': [-5.0, 0.0, 0.0],
            '1.0': [-10.0, 0.0, 0.0]
        }
    },
    'rightLeg3': {
        'rotation': {
            '0.0': [-10.0, 0.0, 0.0],
            '0.25': [8.0, 0.0, 0.0],
            '0.5': [14.0, 0.0, 0.0],
            '0.75': [-18.0, 0.0, 0.0],
            '1.0': [-10.0, 0.0, 0.0]
        }
    },
    'rightLeg2': {
        'rotation': {
            '0.0': [5.0, 0.0, 0.0],
            '0.25': [-5.0, 0.0, 0.0],
            '0.5': [-10.0, 0.0, 0.0],
            '0.75': [15.0, 0.0, 0.0],
            '1.0': [5.0, 0.0, 0.0]
        }
    },
    'rearLeftLeg3': {
        'rotation': {
            '0.0': [-10.0, 0.0, 0.0],
            '0.25': [8.0, 0.0, 0.0],
            '0.5': [14.0, 0.0, 0.0],
            '0.75': [-18.0, 0.0, 0.0],
            '1.0': [-10.0, 0.0, 0.0]
        }
    },
    'rearLeftLeg2': {
        'rotation': {
            '0.0': [5.0, 0.0, 0.0],
            '0.25': [-5.0, 0.0, 0.0],
            '0.5': [-10.0, 0.0, 0.0],
            '0.75': [15.0, 0.0, 0.0],
            '1.0': [5.0, 0.0, 0.0]
        }
    },
    'body1': {
        'position': {
            '0.0': [0.0, 0.0, 0.0],
            '0.25': [0.0, 1.2, 0.0],
            '0.5': [0.0, 0.0, 0.0],
            '0.75': [0.0, 1.2, 0.0],
            '1.0': [0.0, 0.0, 0.0]
        }
    }
}

if 'animation.spider_frame_titan.walk.leg' in re_spider_anims:
    re_spider_anims['animation.spider_frame_titan.walk.leg']['bones'] = quadruped_walk_bones
if 'animation.spider_frame_titan.move.leg' in re_spider_anims:
    re_spider_anims['animation.spider_frame_titan.move.leg']['bones'] = quadruped_walk_bones

spider_anim['animations'] = re_spider_anims
target_spider_anim = os.path.join(ANIM_DIR, "spider_frame_titan.animation.json")
with open(target_spider_anim, 'w') as f:
    json.dump(spider_anim, f, indent=2)
print(f"Generated {target_spider_anim}")

# =========================================================================
# CAMO TEXTURES GENERATION
# =========================================================================
camo_palettes = [
    None,
    {'base': (175, 150, 110), 'accent': (240, 190, 80), 'armor': (195, 170, 125)},
    {'base': (55, 75, 45), 'accent': (120, 220, 60), 'armor': (68, 90, 56)},
    {'base': (75, 80, 85), 'accent': (80, 180, 240), 'armor': (95, 100, 108)},
    {'base': (200, 210, 220), 'accent': (0, 200, 255), 'armor': (220, 230, 240)},
    {'base': (135, 30, 30), 'accent': (255, 60, 60), 'armor': (160, 40, 40)},
    {'base': (30, 70, 150), 'accent': (0, 225, 255), 'armor': (40, 90, 180)},
    {'base': (200, 160, 25), 'accent': (255, 220, 0), 'armor': (225, 180, 30)},
    {'base': (28, 30, 34), 'accent': (180, 50, 255), 'armor': (38, 40, 45)}
]

frame_specs = [
    {
        'id': 'terrain_frame',
        'default_palette': {'base': (70, 80, 65), 'accent': (255, 160, 30), 'armor': (85, 95, 78)},
        'tread_color': (35, 35, 38)
    },
    {
        'id': 'cyclops_frame',
        'default_palette': {'base': (190, 155, 20), 'accent': (0, 240, 255), 'armor': (220, 180, 30)},
        'tread_color': (45, 45, 48)
    },
    {
        'id': 'spider_frame',
        'default_palette': {'base': (45, 48, 54), 'accent': (255, 40, 40), 'armor': (60, 65, 72)},
        'tread_color': (30, 32, 36)
    }
]

for fspec in frame_specs:
    fid = fspec['id']
    f_tex_dir = os.path.join(TEX_DIR, fid)
    os.makedirs(f_tex_dir, exist_ok=True)

    for camo_idx in range(9):
        palette = fspec['default_palette'] if camo_idx == 0 else camo_palettes[camo_idx]
        b_col = palette['base']
        a_col = palette['accent']
        arm_col = palette['armor']
        tread_col = fspec['tread_color']

        def make_pixel_func(b=b_col, a=a_col, arm=arm_col, tr=tread_col, fid=fid):
            def pixel(x, y):
                grid = (x % 16 == 0 or y % 16 == 0)
                subgrid = (x % 8 == 0 or y % 8 == 0)

                # Glowing Visor / Optical Eye Region (x: 0..40, y: 0..40)
                if x < 40 and y < 40:
                    if 10 <= x <= 30 and 10 <= y <= 30:
                        if 18 <= x <= 22 and 18 <= y <= 22:
                            return (255, 255, 255, 255)
                        return (a[0], a[1], a[2], 255)

                # Modular Armor UV Region (x: 120..320, y: 40..150)
                if 120 <= x <= 320 and 40 <= y <= 150:
                    if grid: return (max(0, arm[0]-25), max(0, arm[1]-25), max(0, arm[2]-25), 255)
                    return (arm[0], arm[1], arm[2], 255)

                # Caterpillar Treads Region (x: 300..380, y: 0..120)
                if 300 <= x <= 380 and y <= 120:
                    stripe = ((x + y) // 4) % 2 == 0
                    if stripe: return (tr[0] + 15, tr[1] + 15, tr[2] + 15, 255)
                    return (tr[0], tr[1], tr[2], 255)

                # Hazard Stripes Region on Cyclops shoulders
                if fid == 'cyclops_frame' and 500 <= x <= 560 and y <= 60:
                    hazard = ((x + y) // 8) % 2 == 0
                    if hazard: return (255, 220, 0, 255)
                    return (20, 20, 25, 255)

                # Base mechanical structure
                noise = ((x * 17 + y * 31) % 11) - 5
                if grid:
                    return (max(0, b[0] - 25), max(0, b[1] - 25), max(0, b[2] - 25), 255)
                elif subgrid:
                    return (max(0, b[0] - 12), max(0, b[1] - 12), max(0, b[2] - 12), 255)
                return (min(255, max(0, b[0] + noise)),
                        min(255, max(0, b[1] + noise)),
                        min(255, max(0, b[2] + noise)), 255)
            return pixel

        png_data = create_solid_png(512, 512, make_pixel_func())
        file_suffix = "" if camo_idx == 0 else f"_{camo_idx}"
        target_file = os.path.join(f_tex_dir, f"{fid}_titan{file_suffix}.png")
        with open(target_file, 'wb') as f:
            f.write(png_data)

    print(f"Generated 9 camo textures for {fid}")

# =========================================================================
# BEACON ITEM ICONS (16x16 PNG), MODELS & RECIPES
# =========================================================================
os.makedirs(ITEM_TEX_DIR, exist_ok=True)
os.makedirs(ITEM_MODEL_DIR, exist_ok=True)
os.makedirs(RECIPE_DIR, exist_ok=True)

beacons = [
    {
        'id': 'terrain_frame_beacon',
        'primary': (80, 100, 75),
        'accent': (255, 170, 30),
        'detail': (40, 42, 45),
        'recipe_dye': 'minecraft:green_dye'
    },
    {
        'id': 'cyclops_frame_beacon',
        'primary': (210, 175, 20),
        'accent': (0, 240, 255),
        'detail': (25, 25, 30),
        'recipe_dye': 'minecraft:cyan_dye'
    },
    {
        'id': 'spider_frame_beacon',
        'primary': (50, 54, 62),
        'accent': (255, 50, 50),
        'detail': (30, 32, 36),
        'recipe_dye': 'minecraft:spider_eye'
    }
]

for b in beacons:
    bid = b['id']
    p_col = b['primary']
    a_col = b['accent']
    d_col = b['detail']

    def make_beacon_icon(p=p_col, a=a_col, d=d_col, bid=bid):
        def pixel(x, y):
            if x == 0 or x == 15 or y == 0 or y == 15:
                return (0, 0, 0, 0)
            if (x == 7 or x == 8) and 1 <= y <= 3:
                return (a[0], a[1], a[2], 255)
            if 6 <= x <= 9 and 6 <= y <= 9:
                if 7 <= x <= 8 and 7 <= y <= 8:
                    return (255, 255, 255, 255)
                return (a[0], a[1], a[2], 255)
            if 11 <= y <= 14:
                if x in (2, 3, 12, 13) or (y == 14 and 4 <= x <= 11):
                    return (d[0], d[1], d[2], 255)
            if 4 <= y <= 12 and (6 - (y - 4) // 2) <= x <= (9 + (y - 4) // 2):
                return (p[0], p[1], p[2], 255)
            return (0, 0, 0, 0)
        return pixel

    icon_data = create_solid_png(16, 16, make_beacon_icon())
    icon_path = os.path.join(ITEM_TEX_DIR, f"{bid}.png")
    with open(icon_path, 'wb') as f:
        f.write(icon_data)

    model_json = {
        "parent": "minecraft:item/generated",
        "textures": {
            "layer0": f"titancombat:item/{bid}"
        }
    }
    model_path = os.path.join(ITEM_MODEL_DIR, f"{bid}.json")
    with open(model_path, 'w') as f:
        json.dump(model_json, f, indent=2)

    recipe_json = {
        "type": "minecraft:crafting_shapeless",
        "category": "equipment",
        "ingredients": [
            {"item": "titancombat:chassis_frame"},
            {"item": "minecraft:iron_ingot"},
            {"item": "minecraft:iron_ingot"},
            {"item": "minecraft:copper_ingot"},
            {"item": "minecraft:copper_ingot"},
            {"item": "minecraft:redstone"},
            {"item": "minecraft:redstone"},
            {"item": b['recipe_dye']}
        ],
        "result": {
            "item": f"titancombat:{bid}",
            "count": 1
        }
    }
    recipe_path = os.path.join(RECIPE_DIR, f"{bid}.json")
    with open(recipe_path, 'w') as f:
        json.dump(recipe_json, f, indent=2)

    print(f"Generated beacon icon, model, recipe for {bid}")

print("All expansion frames assets successfully generated!")
