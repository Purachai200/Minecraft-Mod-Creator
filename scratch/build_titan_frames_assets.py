import json
import os
import struct
import zlib
import copy

# Pure standard library PNG generator
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

# 1. Load baseline trooper geo and animation
base_geo_path = 'Titan Combat/src/main/resources/assets/titancombat/geo/trooper_titan.geo.json'
base_anim_path = 'Titan Combat/src/main/resources/assets/titancombat/animations/trooper_titan.animation.json'

with open(base_geo_path, 'r') as f:
    trooper_geo = json.load(f)

with open(base_anim_path, 'r') as f:
    trooper_anim = json.load(f)

# Frames configuration
frames = [
    {
        'id': 'striker_frame',
        'name': 'Striker Frame',
        'width_scale': 0.9,
        'armor_style': 'swept'
    },
    {
        'id': 'vanguard_frame',
        'name': 'Vanguard Frame',
        'width_scale': 1.0,
        'armor_style': 'standard'
    },
    {
        'id': 'colossus_frame',
        'name': 'Colossus Frame',
        'width_scale': 1.25,
        'armor_style': 'heavy'
    }
]

# Generate Geo JSONs
geo_out_dir = 'Titan Combat/src/main/resources/assets/titancombat/geo'
anim_out_dir = 'Titan Combat/src/main/resources/assets/titancombat/animations'

for frm in frames:
    fid = frm['id']
    style = frm['armor_style']
    scale = frm['width_scale']

    # Clone geometry
    new_geo = copy.deepcopy(trooper_geo)
    geom_entry = new_geo['minecraft:geometry'][0]
    geom_entry['description']['identifier'] = f"geometry.{fid}_titan"

    bones = geom_entry['bones']
    bone_map = {b['name']: b for b in bones}

    # Add modular armor bones
    # 1. Armor Head (parented to doorUp or body3)
    armor_head = {
        'name': 'armor_head',
        'parent': 'doorUp',
        'pivot': [0.0, 107.0, -10.0],
        'cubes': [
            {
                'origin': [-7.0 * scale, 98.0, -18.0],
                'size': [14.0 * scale, 12.0, 6.0],
                'uv': [120, 40]
            },
            {
                'origin': [-4.0 * scale, 110.0, -16.0],
                'size': [8.0 * scale, 4.0, 4.0],
                'uv': [160, 40]
            }
        ]
    }

    # 2. Armor Chest (parented to body3)
    armor_chest = {
        'name': 'armor_chest',
        'parent': 'body3',
        'pivot': [0.0, 85.0, 0.0],
        'cubes': [
            {
                'origin': [-14.0 * scale, 75.0, -14.0],
                'size': [28.0 * scale, 18.0, 6.0],
                'uv': [120, 64]
            },
            {
                'origin': [-11.0 * scale, 70.0, -12.0],
                'size': [22.0 * scale, 8.0, 4.0],
                'uv': [120, 90]
            }
        ]
    }

    # 3. Armor Arms (Left and Right)
    armor_left_arm = {
        'name': 'armor_left_arm',
        'parent': 'leftArm1',
        'pivot': [24.4, 94.8, 10.7],
        'cubes': [
            {
                'origin': [22.0, 88.0, 4.0],
                'size': [10.0 * scale, 12.0, 12.0],
                'uv': [200, 64]
            }
        ]
    }
    armor_right_arm = {
        'name': 'armor_right_arm',
        'parent': 'rightArm1',
        'pivot': [-24.4, 94.8, 10.7],
        'cubes': [
            {
                'origin': [-22.0 - 10.0 * scale, 88.0, 4.0],
                'size': [10.0 * scale, 12.0, 12.0],
                'uv': [200, 64]
            }
        ]
    }

    # 4. Armor Legs (Left and Right)
    armor_left_leg = {
        'name': 'armor_left_leg',
        'parent': 'leftLeg2',
        'pivot': [14.8, 43.5, 2.7],
        'cubes': [
            {
                'origin': [10.0, 24.0, -4.0],
                'size': [9.0 * scale, 18.0, 12.0],
                'uv': [200, 90]
            }
        ]
    }
    armor_right_leg = {
        'name': 'armor_right_leg',
        'parent': 'rightLeg2',
        'pivot': [-14.5, 43.5, 2.7],
        'cubes': [
            {
                'origin': [-10.0 - 9.0 * scale, 24.0, -4.0],
                'size': [9.0 * scale, 18.0, 12.0],
                'uv': [200, 90]
            }
        ]
    }

    bones.extend([armor_head, armor_chest, armor_left_arm, armor_right_arm, armor_left_leg, armor_right_leg])

    # Save geo file
    target_geo_file = os.path.join(geo_out_dir, f"{fid}_titan.geo.json")
    with open(target_geo_file, 'w') as f:
        json.dump(new_geo, f, indent=2)
    print(f"Generated {target_geo_file}")

    # Generate Animation file
    new_anim = copy.deepcopy(trooper_anim)
    orig_anims = new_anim.get('animations', {})
    re_anims = {}
    for anim_name, anim_data in orig_anims.items():
        mapped_name = anim_name.replace('trooper_titan', f"{fid}_titan")
        re_anims[mapped_name] = anim_data
    new_anim['animations'] = re_anims

    target_anim_file = os.path.join(anim_out_dir, f"{fid}_titan.animation.json")
    with open(target_anim_file, 'w') as f:
        json.dump(new_anim, f, indent=2)
    print(f"Generated {target_anim_file}")

# Generate 9 Camo Textures for each Frame
camo_palettes = [
    # 0: Default Steel Grey
    {'base': (60, 64, 70), 'accent': (0, 220, 255), 'armor': (75, 80, 88)},
    # 1: Desert Tan
    {'base': (170, 145, 105), 'accent': (240, 190, 80), 'armor': (190, 165, 120)},
    # 2: Woodland Green
    {'base': (55, 75, 45), 'accent': (120, 220, 60), 'armor': (68, 90, 56)},
    # 3: Urban Digital
    {'base': (75, 80, 85), 'accent': (80, 180, 240), 'armor': (95, 100, 108)},
    # 4: Arctic Snow
    {'base': (200, 210, 220), 'accent': (0, 200, 255), 'armor': (220, 230, 240)},
    # 5: Crimson Red
    {'base': (135, 30, 30), 'accent': (255, 60, 60), 'armor': (160, 40, 40)},
    # 6: Cobalt Blue
    {'base': (30, 70, 150), 'accent': (0, 225, 255), 'armor': (40, 90, 180)},
    # 7: Hazard Industrial (Yellow & Black)
    {'base': (200, 160, 25), 'accent': (255, 220, 0), 'armor': (225, 180, 30)},
    # 8: Stealth Black Ops
    {'base': (28, 30, 34), 'accent': (180, 50, 255), 'armor': (38, 40, 45)}
]

titan_tex_base_dir = 'Titan Combat/src/main/resources/assets/titancombat/textures/entity/titan'

for frm in frames:
    fid = frm['id']
    f_tex_dir = os.path.join(titan_tex_base_dir, fid)
    os.makedirs(f_tex_dir, exist_ok=True)

    for camo_idx, palette in enumerate(camo_palettes):
        b_col = palette['base']
        a_col = palette['accent']
        arm_col = palette['armor']

        def make_tex_func(b=b_col, a=a_col, arm=arm_col):
            def pixel_func(x, y):
                # Chassis mechanical skeleton pattern
                grid = (x % 16 == 0 or y % 16 == 0)
                subgrid = (x % 8 == 0 or y % 8 == 0)

                # Visor & Sensor Glow region (x: 0..40, y: 0..40)
                if x < 40 and y < 40:
                    if 12 <= x <= 28 and 12 <= y <= 28:
                        return (a[0], a[1], a[2], 255) # Glowing sensor visor

                # Modular Armor UV Region (x: 120..320, y: 40..150)
                if 120 <= x <= 320 and 40 <= y <= 150:
                    if grid: return (max(0, arm[0]-25), max(0, arm[1]-25), max(0, arm[2]-25), 255)
                    return (arm[0], arm[1], arm[2], 255)

                # Base structural frame
                noise = ((x * 13 + y * 29) % 11) - 5
                if grid:
                    return (max(0, b[0] - 25), max(0, b[1] - 25), max(0, b[2] - 25), 255)
                elif subgrid:
                    return (max(0, b[0] - 12), max(0, b[1] - 12), max(0, b[2] - 12), 255)
                return (min(255, max(0, b[0] + noise)),
                        min(255, max(0, b[1] + noise)),
                        min(255, max(0, b[2] + noise)), 255)
            return pixel_func

        png_bytes = create_solid_png(512, 512, make_tex_func())
        file_suffix = "" if camo_idx == 0 else f"_{camo_idx}"
        target_png = os.path.join(f_tex_dir, f"{fid}_titan{file_suffix}.png")
        with open(target_png, 'wb') as f:
            f.write(png_bytes)

    print(f"Generated 9 camo textures for {fid}")

print("All Titan Frame Assets (Geo, Animations, Textures) generated successfully!")
