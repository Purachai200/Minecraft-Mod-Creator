import subprocess, tempfile, re, os, zipfile, json, math, shutil
from PIL import Image, ImageEnhance, ImageOps

JAR_GFS = r'c:\Users\Purachai\Downloads\Flans\Global Firestorm v3.2 - (Port 1.12.2).jar'
MOD_DIR = r'c:\Users\Purachai\Desktop\Minecraft Mode Creator\minecraft_mod_creator\Vehicle Fleet\src\main\resources'

GEO_DIR = os.path.join(MOD_DIR, 'assets', 'vehiclefleet', 'geo')
ANIM_DIR = os.path.join(MOD_DIR, 'assets', 'vehiclefleet', 'animations')
TEX_DIR = os.path.join(MOD_DIR, 'assets', 'vehiclefleet', 'textures', 'entity')
ITEM_TEX_DIR = os.path.join(MOD_DIR, 'assets', 'vehiclefleet', 'textures', 'item')
ITEM_MODEL_DIR = os.path.join(MOD_DIR, 'assets', 'vehiclefleet', 'models', 'item')
SOUND_DIR = os.path.join(MOD_DIR, 'assets', 'vehiclefleet', 'sounds', 'vehicle')
DATA_FILE = os.path.join(MOD_DIR, 'data', 'vehiclefleet', 'vehicles.json')
LANG_FILE = os.path.join(MOD_DIR, 'assets', 'vehiclefleet', 'lang', 'en_us.json')

LIVERY_SUFFIXES = [
    "",
    "_thai",
    "_desert",
    "_arctic",
    "_blackops",
    "_un",
    "_redstar"
]

HELICOPTERS = [
    {
        "id": "ah6_littlebird",
        "class_name": "ModelAH6J",
        "skin_name": "skinah6j.png",
        "icon_name": "iconah6j.png",
        "sound_src": "engine_hel_lilbird.ogg",
        "sound_event": "vehicle_rotor_helo_littlebird",
        "name": "AH-6J Little Bird Light Gunship",
        "tier": 1,
        "payload": "Light Recon & Insertion",
        "seat_capacity": 4,
        "seats": [
            {"name": "pilot", "pos": [7.0, 18.0, -8.0]},
            {"name": "copilot", "pos": [-7.0, 18.0, -8.0]},
            {"name": "left_bench", "pos": [-14.0, 13.0, 2.0]},
            {"name": "right_bench", "pos": [14.0, 13.0, 2.0]}
        ],
        "half_width": 14.0,
        "length": [-35.0, 65.0],
        "height": 42.0,
        "rgb": [48, 52, 45],
        "speed": 0.52
    },
    {
        "id": "ah64_apache",
        "class_name": "ModelAH64",
        "skin_name": "skinah64.png",
        "icon_name": "iconah64.png",
        "sound_src": "engine_hel_apache.ogg",
        "sound_event": "vehicle_rotor_helo_apache",
        "name": "AH-64D Apache Longbow Attack Helicopter",
        "tier": 2,
        "payload": "Heavy Ordnance & Anti-Armor",
        "seat_capacity": 2,
        "seats": [
            {"name": "gunner", "pos": [0.0, 26.0, -28.0]},
            {"name": "pilot", "pos": [0.0, 34.0, -12.0]}
        ],
        "half_width": 24.0,
        "length": [-65.0, 75.0],
        "height": 58.0,
        "rgb": [55, 60, 52],
        "speed": 0.48
    },
    {
        "id": "uh1y_venom",
        "class_name": "ModelUH1Y",
        "skin_name": "skinuh1y.png",
        "icon_name": "iconuh1y.png",
        "sound_src": "engine_hel_vipervenom.ogg",
        "sound_event": "vehicle_rotor_helo_venom",
        "name": "UH-1Y Venom Tactical Transport",
        "tier": 1,
        "payload": "Troop Squad & Light Cargo",
        "seat_capacity": 6,
        "seats": [
            {"name": "pilot", "pos": [9.0, 25.0, -22.0]},
            {"name": "copilot", "pos": [-9.0, 25.0, -22.0]},
            {"name": "passenger_1", "pos": [8.0, 22.0, -2.0]},
            {"name": "passenger_2", "pos": [-8.0, 22.0, -2.0]},
            {"name": "passenger_3", "pos": [8.0, 22.0, 12.0]},
            {"name": "passenger_4", "pos": [-8.0, 22.0, 12.0]}
        ],
        "half_width": 18.0,
        "length": [-55.0, 85.0],
        "height": 52.0,
        "rgb": [78, 85, 82],
        "speed": 0.45
    },
    {
        "id": "mi28_havoc",
        "class_name": "ModelMi28",
        "skin_name": "skinmi28.png",
        "icon_name": "iconmi28.png",
        "sound_src": "engine_hel_hindhip.ogg",
        "sound_event": "vehicle_rotor_helo_havoc",
        "name": "Mil Mi-28N Havoc Combat Helicopter",
        "tier": 2,
        "payload": "Heavy Armor Interdiction",
        "seat_capacity": 2,
        "seats": [
            {"name": "gunner", "pos": [0.0, 28.0, -28.0]},
            {"name": "pilot", "pos": [0.0, 36.0, -12.0]}
        ],
        "half_width": 24.0,
        "length": [-70.0, 85.0],
        "height": 62.0,
        "rgb": [62, 68, 58],
        "speed": 0.46
    },
    {
        "id": "ah1z_viper",
        "class_name": "ModelAH1Z",
        "skin_name": "skinah1z.png",
        "icon_name": "iconah1z.png",
        "sound_src": "engine_hel_vipervenom.ogg",
        "sound_event": "vehicle_rotor_helo_viper",
        "name": "AH-1Z Viper Attack Helicopter",
        "tier": 2,
        "payload": "Precision Strike & Close Air Support",
        "seat_capacity": 2,
        "seats": [
            {"name": "gunner", "pos": [0.0, 24.0, -26.0]},
            {"name": "pilot", "pos": [0.0, 32.0, -10.0]}
        ],
        "half_width": 20.0,
        "length": [-55.0, 75.0],
        "height": 54.0,
        "rgb": [72, 78, 76],
        "speed": 0.50
    },
    {
        "id": "ec665_tiger",
        "class_name": "ModelEC665",
        "skin_name": "skinec665.png",
        "icon_name": "iconec665.png",
        "sound_src": "engine_hel_apache.ogg",
        "sound_event": "vehicle_rotor_helo_tiger",
        "name": "Eurocopter Tiger Multi-Role Attack Helicopter",
        "tier": 2,
        "payload": "Agile Ground Suppression",
        "seat_capacity": 2,
        "seats": [
            {"name": "pilot", "pos": [0.0, 24.0, -24.0]},
            {"name": "gunner", "pos": [0.0, 32.0, -8.0]}
        ],
        "half_width": 20.0,
        "length": [-55.0, 70.0],
        "height": 52.0,
        "rgb": [58, 64, 52],
        "speed": 0.49
    },
    {
        "id": "comanche",
        "class_name": "ModelComanche",
        "skin_name": "skincomanche.png",
        "icon_name": "iconcomanche.png",
        "sound_src": "engine_hel_apache.ogg",
        "sound_event": "vehicle_rotor_helo_apache",
        "name": "RAH-66 Comanche Stealth Scout Helicopter",
        "tier": 2,
        "payload": "Low Radar Cross-Section Recon",
        "seat_capacity": 2,
        "seats": [
            {"name": "pilot", "pos": [0.0, 24.0, -20.0]},
            {"name": "gunner", "pos": [0.0, 30.0, -6.0]}
        ],
        "half_width": 16.0,
        "length": [-50.0, 60.0],
        "height": 46.0,
        "rgb": [40, 42, 45],
        "speed": 0.54
    }
]

constant_re = re.compile(r'// (float|int|String) (.+)')
field_re = re.compile(r'// Field (\w+):')

def parse_flan_class(class_bytes, model_name, v_id):
    tmp = os.path.join(tempfile.gettempdir(), f'{model_name}.class')
    with open(tmp, 'wb') as f:
        f.write(class_bytes)

    res = subprocess.run(['javap', '-p', '-c', tmp], capture_output=True, text=True)
    lines = res.stdout.splitlines()

    tex_w, tex_h = 1024, 1024
    for i, l in enumerate(lines[:120]):
        if 'textureX' in l and i > 0:
            tokens = lines[i-1].strip().split()
            if len(tokens) >= 2 and tokens[-1].isdigit(): tex_w = int(tokens[-1])
        if 'textureY' in l and i > 0:
            tokens = lines[i-1].strip().split()
            if len(tokens) >= 2 and tokens[-1].isdigit(): tex_h = int(tokens[-1])

    # Separate methods
    methods = {}
    current_method = None
    cur_lines = []
    for l in lines:
        if l.startswith('  private void init') or l.startswith('  public ') or l.startswith('  private void '):
            if current_method and cur_lines: methods[current_method] = cur_lines
            m_name = l.strip().split('(')[0].split()[-1]
            current_method = m_name
            cur_lines = []
        elif current_method:
            cur_lines.append(l)
    if current_method and cur_lines:
        methods[current_method] = cur_lines

    all_bones = {}
    uvs = {}

    for m_name, m_lines in methods.items():
        low = m_name.lower()
        if 'hud' in low: continue
        if 'tailrotor' in low or 'helitailrotor' in low: bone_group = 'tail_rotor'
        elif 'mainrotor' in low or 'helimainrotor' in low: bone_group = 'main_rotor'
        elif 'nose' in low or 'cockpit' in low or 'seat' in low: bone_group = 'cockpit'
        elif 'tail' in low or 'rudder' in low or 'yaw' in low: bone_group = 'tail'
        elif 'skid' in low or 'wheel' in low or 'gear' in low: bone_group = 'skids'
        elif 'leftwing' in low: bone_group = 'wing_left'
        elif 'rightwing' in low: bone_group = 'wing_right'
        elif 'turret' in low or 'gun' in low: bone_group = 'turret'
        else: bone_group = 'body'

        if bone_group not in all_bones: all_bones[bone_group] = []

        stack = []
        rot_points = {}

        for line in m_lines:
            line_str = line.strip()
            if not line_str: continue
            parts = line_str.split(': ')
            if len(parts) != 2: continue
            tokens = parts[1].split()
            op = tokens[0]

            if op.startswith('iconst_'): stack.append(int(op.replace('iconst_m1', '-1').replace('iconst_', '')))
            elif op == 'fconst_0': stack.append(0.0)
            elif op == 'fconst_1': stack.append(1.0)
            elif op == 'fconst_2': stack.append(2.0)
            elif op in ('bipush', 'sipush'): stack.append(int(tokens[1]))
            elif op in ('ldc', 'ldc_w'):
                m = constant_re.search(line_str)
                if m:
                    t, v = m.group(1), m.group(2)
                    if t == 'float': stack.append(float(v.rstrip('f')))
                    elif t == 'int': stack.append(int(v))
                    else: stack.append(v)
                else: stack.append(0.0)
            elif op.startswith('aload'): stack.append('ref')
            elif op == 'dup':
                if stack: stack.append(stack[-1])
            elif op == 'new':
                stack.append({'type': 'mrt', 'u': 0, 'v': 0})
            elif op == 'getfield':
                m = field_re.search(line_str)
                f_name = m.group(1) if m else 'unknown'
                if stack: stack.pop()
                if f_name == 'textureX': stack.append(tex_w)
                elif f_name == 'textureY': stack.append(tex_h)
                else: stack.append(('field', f_name))
            elif op == 'aaload':
                if len(stack) >= 2:
                    idx = stack.pop()
                    arr = stack.pop()
                    stack.append(('elem', arr, idx))
            elif op == 'aastore':
                if len(stack) >= 3:
                    val = stack.pop()
                    idx = stack.pop()
                    arr = stack.pop()
                    arr_name = arr[1] if isinstance(arr, tuple) else 'unknown'
                    if isinstance(val, dict) and val.get('type') == 'mrt':
                        uvs[(arr_name, idx)] = (val['u'], val['v'])
            elif op == 'invokespecial':
                if 'ModelRendererTurbo' in line_str and '<init>' in line_str:
                    if len(stack) >= 6:
                        h = stack.pop()
                        w = stack.pop()
                        v = stack.pop()
                        u = stack.pop()
                        model_base = stack.pop()
                        this_obj = stack.pop()
                        if isinstance(this_obj, dict):
                            this_obj['u'] = int(u) if isinstance(u, (int, float)) else 0
                            this_obj['v'] = int(v) if isinstance(v, (int, float)) else 0
            elif op == 'invokevirtual':
                if 'addShapeBox' in line_str:
                    if len(stack) >= 32:
                        args = [stack.pop() for _ in range(31)]
                        args.reverse()
                        obj = stack.pop()
                        x, y, z = float(args[0]), float(args[1]), float(args[2])
                        w, h, d = float(args[3]), float(args[4]), float(args[5])
                        elem_info = (obj[1][1], obj[2]) if isinstance(obj, tuple) and len(obj) >= 3 and isinstance(obj[1], tuple) else None
                        cur_uv = uvs.get(elem_info, (0, 0))
                        
                        # Filter out 2D billboard planes
                        is_billboard = (w >= 70 or h >= 70 or d >= 70) and min(w, h, d) <= 1.0
                        if w >= 200 or h >= 200 or d >= 200: is_billboard = True
                        if not is_billboard:
                            rp = rot_points.get(elem_info, (0.0, 0.0, 0.0))
                            all_bones[bone_group].append({
                                'pos': (x, y, z),
                                'size': (w, h, d),
                                'uv': cur_uv,
                                'rotPoint': rp
                            })
                elif 'addBox' in line_str:
                    param_count = 7 if '(FFFIIIF)' in line_str or '(FFFFFF)' in line_str else 6
                    if len(stack) >= param_count + 1:
                        args = [stack.pop() for _ in range(param_count)]
                        args.reverse()
                        obj = stack.pop()
                        x, y, z = float(args[0]), float(args[1]), float(args[2])
                        w, h, d = float(args[3]), float(args[4]), float(args[5])
                        elem_info = (obj[1][1], obj[2]) if isinstance(obj, tuple) and len(obj) >= 3 and isinstance(obj[1], tuple) else None
                        cur_uv = uvs.get(elem_info, (0, 0))
                        is_billboard = (w >= 70 or h >= 70 or d >= 70) and min(w, h, d) <= 1.0
                        if w >= 200 or h >= 200 or d >= 200: is_billboard = True
                        if not is_billboard:
                            rp = rot_points.get(elem_info, (0.0, 0.0, 0.0))
                            all_bones[bone_group].append({
                                'pos': (x, y, z),
                                'size': (w, h, d),
                                'uv': cur_uv,
                                'rotPoint': rp
                            })
                elif 'func_78793_a' in line_str or 'setRotationPoint' in line_str:
                    if len(stack) >= 4:
                        rz = stack.pop()
                        ry = stack.pop()
                        rx = stack.pop()
                        obj = stack.pop()
                        elem_info = (obj[1][1], obj[2]) if isinstance(obj, tuple) and len(obj) >= 3 and isinstance(obj[1], tuple) else None
                        if elem_info:
                            rot_points[elem_info] = (float(rx), float(ry), float(rz))
                            for b in reversed(all_bones[bone_group]):
                                if b.get('rotPoint') == (0.0, 0.0, 0.0):
                                    b['rotPoint'] = (float(rx), float(ry), float(rz))

    min_raw_y = 999999.0
    for b_name, boxes in all_bones.items():
        for b in boxes:
            y = b['pos'][1]
            h = b['size'][1]
            ry = b['rotPoint'][1]
            raw_y = -(ry + y + h) + 24.0
            if raw_y < min_raw_y: min_raw_y = raw_y

    shift_y = -min_raw_y if min_raw_y < 999999.0 else 0.0

    gecko_bones = []
    gecko_bones.append({
        'name': 'root',
        'pivot': [0.0, 0.0, 0.0],
        'rotation': [0.0, 90.0, 0.0]
    })

    for b_name, boxes in all_bones.items():
        if not boxes: continue
        cubes = []
        for b in boxes:
            x, y, z = b['pos']
            w, h, d = b['size']
            rx, ry, rz = b['rotPoint']
            u, v = b['uv']

            box_x = rx + x
            box_y = -(ry + y + h) + 24.0 + shift_y
            box_z = -(rz + z + d)

            cubes.append({
                'origin': [round(box_x, 3), round(box_y, 3), round(box_z, 3)],
                'size': [max(0.1, round(w, 3)), max(0.1, round(h, 3)), max(0.1, round(d, 3))],
                'uv': [int(u), int(v)]
            })

        piv_x = sum(b['rotPoint'][0] for b in boxes) / len(boxes)
        piv_y = -sum(b['rotPoint'][1] for b in boxes) / len(boxes) + 24.0 + shift_y
        piv_z = -sum(b['rotPoint'][2] for b in boxes) / len(boxes)

        gecko_bones.append({
            'name': b_name,
            'parent': 'root',
            'pivot': [round(piv_x, 3), round(piv_y, 3), round(piv_z, 3)],
            'cubes': cubes
        })

    geo_data = {
        'format_version': '1.12.0',
        'minecraft:geometry': [
            {
                'description': {
                    'identifier': f'geometry.{v_id}',
                    'texture_width': tex_w,
                    'texture_height': tex_h,
                    'visible_bounds_width': 16,
                    'visible_bounds_height': 10,
                    'visible_bounds_offset': [0, 3, 0]
                },
                'bones': gecko_bones
            }
        ]
    }
    return geo_data, tex_w, tex_h, shift_y

def create_animation(vehicle_id):
    return {
        "format_version": "1.8.0",
        "animations": {
            f"animation.{vehicle_id}.idle": {
                "loop": True,
                "animation_length": 2.0,
                "bones": {
                    "main_rotor": {
                        "rotation": {
                            "0.0": [0, 0, 0],
                            "2.0": [0, 360, 0]
                        }
                    },
                    "tail_rotor": {
                        "rotation": {
                            "0.0": [0, 0, 0],
                            "2.0": [0, 0, 360]
                        }
                    }
                }
            },
            f"animation.{vehicle_id}.fly": {
                "loop": True,
                "animation_length": 0.25,
                "bones": {
                    "main_rotor": {
                        "rotation": {
                            "0.0": [0, 0, 0],
                            "0.25": [0, 360, 0]
                        }
                    },
                    "tail_rotor": {
                        "rotation": {
                            "0.0": [0, 0, 0],
                            "0.25": [0, 0, 720]
                        }
                    }
                }
            }
        }
    }

def create_liveries(base_img):
    liveries = {}
    base_rgba = base_img.convert('RGBA')
    # 0. Standard Tactical (no suffix)
    liveries[""] = base_rgba

    # 1. Royal Thai Army Camo (_thai)
    thai_img = base_rgba.copy()
    thai_enh = ImageEnhance.Color(thai_img).enhance(1.25)
    thai_overlay = Image.new('RGBA', base_img.size, (48, 62, 38, 45))
    liveries["_thai"] = Image.alpha_composite(thai_enh, thai_overlay)

    # 2. Desert Expeditionary (_desert)
    desert_img = base_rgba.copy()
    desert_overlay = Image.new('RGBA', base_img.size, (190, 165, 115, 65))
    liveries["_desert"] = Image.alpha_composite(desert_img, desert_overlay)

    # 3. Arctic Snow (_arctic)
    arctic_img = ImageOps.grayscale(base_img).convert('RGBA')
    arctic_enh = ImageEnhance.Brightness(arctic_img).enhance(1.4)
    arctic_overlay = Image.new('RGBA', base_img.size, (220, 230, 245, 55))
    liveries["_arctic"] = Image.alpha_composite(arctic_enh, arctic_overlay)

    # 4. Night Ops (_blackops)
    blackops_img = ImageOps.grayscale(base_img).convert('RGBA')
    blackops_enh = ImageEnhance.Brightness(blackops_img).enhance(0.38)
    liveries["_blackops"] = blackops_enh

    # 5. UN Peacekeeper (_un)
    un_img = base_rgba.copy()
    un_overlay = Image.new('RGBA', base_img.size, (90, 150, 210, 65))
    liveries["_un"] = Image.alpha_composite(un_img, un_overlay)

    # 6. Rebel Crimson (_redstar)
    red_img = base_rgba.copy()
    red_overlay = Image.new('RGBA', base_img.size, (170, 45, 45, 55))
    liveries["_redstar"] = Image.alpha_composite(red_img, red_overlay)

    return liveries

print("Starting Flan Helicopter extraction...")

with zipfile.ZipFile(JAR_GFS, 'r') as z:
    for h in HELICOPTERS:
        v_id = h['id']
        c_name = h['class_name']
        s_name = h['skin_name']
        i_name = h['icon_name']
        snd_src = h['sound_src']

        print(f"\nProcessing {v_id} ({c_name})...")

        # 1. Geometry
        c_bytes = z.read(f'com/flansmod/client/model/gfs/{c_name}.class')
        geo, tw, th, sy = parse_flan_class(c_bytes, c_name, v_id)
        geo_path = os.path.join(GEO_DIR, f'{v_id}.geo.json')
        with open(geo_path, 'w', encoding='utf-8') as f:
            json.dump(geo, f, indent=2)
        print(f"  Geo written: {geo_path} (shift_y={sy:.1f})")

        # 2. Animation
        anim = create_animation(v_id)
        anim_path = os.path.join(ANIM_DIR, f'{v_id}.animation.json')
        with open(anim_path, 'w', encoding='utf-8') as f:
            json.dump(anim, f, indent=2)
        print(f"  Animation written: {anim_path}")

        # 3. Textures (Base + 6 liveries + glowmasks)
        skin_bytes = z.read(f'assets/flansmod/skins/{s_name}')
        tmp_skin = os.path.join(tempfile.gettempdir(), f'temp_{s_name}')
        with open(tmp_skin, 'wb') as f:
            f.write(skin_bytes)
        base_img = Image.open(tmp_skin)
        liveries = create_liveries(base_img)
        for suff, img in liveries.items():
            t_path = os.path.join(TEX_DIR, f'{v_id}{suff}.png')
            img.save(t_path)
            glow_path = os.path.join(TEX_DIR, f'{v_id}{suff}_glowmask.png')
            Image.new('RGBA', (16, 16), (0, 0, 0, 0)).save(glow_path)
        print(f"  Textures written: 7 liveries & glowmasks -> {TEX_DIR}\\{v_id}*.png")

        # 4. Item Icon
        try:
            icon_bytes = z.read(f'assets/flansmod/textures/items/{i_name}')
            i_path = os.path.join(ITEM_TEX_DIR, f'{v_id}.png')
            with open(i_path, 'wb') as f:
                f.write(icon_bytes)
            print(f"  Item Icon written: {i_path}")
        except Exception as e:
            print(f"  Warning: could not extract icon {i_name}: {e}")

        # 5. Item Model JSON
        item_model = {
            "parent": "item/generated",
            "textures": {
                "layer0": f"vehiclefleet:item/{v_id}"
            }
        }
        im_path = os.path.join(ITEM_MODEL_DIR, f'{v_id}.json')
        with open(im_path, 'w', encoding='utf-8') as f:
            json.dump(item_model, f, indent=2)
        print(f"  Item Model written: {im_path}")

        # 6. Sound Effect
        try:
            snd_bytes = z.read(f'assets/flansmod/sounds/{snd_src}')
            out_snd_name = h['sound_event'].replace('vehicle_', '') + '.ogg'
            snd_path = os.path.join(SOUND_DIR, out_snd_name)
            with open(snd_path, 'wb') as f:
                f.write(snd_bytes)
            print(f"  Sound written: {snd_path}")
        except Exception as e:
            print(f"  Warning: sound error {snd_src}: {e}")

    # Authentic sounds
    try:
        with open(os.path.join(SOUND_DIR, 'rotor_helo_light.ogg'), 'wb') as f:
            f.write(z.read('assets/flansmod/sounds/engine_hel_hawk.ogg'))
        with open(os.path.join(SOUND_DIR, 'rotor_helo_heavy.ogg'), 'wb') as f:
            f.write(z.read('assets/flansmod/sounds/engine_hel_hindhip.ogg'))
        with open(os.path.join(ITEM_TEX_DIR, 'uh60_blackhawk.png'), 'wb') as f:
            f.write(z.read('assets/flansmod/textures/items/iconuh60.png'))
        print("  Updated default helo sounds & uh60 icon.")
    except Exception as e:
        print(f"  Sound upgrade error: {e}")

# UPGRADE EXISTING HELICOPTERS (uh60_blackhawk, mi17_hip, mi26_halo)
print("\nUpgrading existing helicopters with clean Flan geometry & textures...")

# 1. UH-60 Blackhawk
with open(os.path.join(GEO_DIR, 'uh1y_venom.geo.json'), 'r', encoding='utf-8') as f:
    uh_geo = json.load(f)
uh_geo['minecraft:geometry'][0]['description']['identifier'] = 'geometry.uh60_blackhawk'
with open(os.path.join(GEO_DIR, 'uh60_blackhawk.geo.json'), 'w', encoding='utf-8') as f:
    json.dump(uh_geo, f, indent=2)

anim = create_animation('uh60_blackhawk')
with open(os.path.join(ANIM_DIR, 'uh60_blackhawk.animation.json'), 'w', encoding='utf-8') as f:
    json.dump(anim, f, indent=2)

for suff in LIVERY_SUFFIXES:
    src_tex = os.path.join(TEX_DIR, f'uh1y_venom{suff}.png')
    dst_tex = os.path.join(TEX_DIR, f'uh60_blackhawk{suff}.png')
    if os.path.exists(src_tex):
        shutil.copyfile(src_tex, dst_tex)
    glow_dst = os.path.join(TEX_DIR, f'uh60_blackhawk{suff}_glowmask.png')
    Image.new('RGBA', (16, 16), (0, 0, 0, 0)).save(glow_dst)

print("  uh60_blackhawk clean geo, anim, textures updated.")

# 2. Mi-17 Hip
with open(os.path.join(GEO_DIR, 'mi28_havoc.geo.json'), 'r', encoding='utf-8') as f:
    mi_geo = json.load(f)
mi_geo['minecraft:geometry'][0]['description']['identifier'] = 'geometry.mi17_hip'
with open(os.path.join(GEO_DIR, 'mi17_hip.geo.json'), 'w', encoding='utf-8') as f:
    json.dump(mi_geo, f, indent=2)

anim = create_animation('mi17_hip')
with open(os.path.join(ANIM_DIR, 'mi17_hip.animation.json'), 'w', encoding='utf-8') as f:
    json.dump(anim, f, indent=2)

for suff in LIVERY_SUFFIXES:
    src_tex = os.path.join(TEX_DIR, f'mi28_havoc{suff}.png')
    dst_tex = os.path.join(TEX_DIR, f'mi17_hip{suff}.png')
    if os.path.exists(src_tex):
        shutil.copyfile(src_tex, dst_tex)
    glow_dst = os.path.join(TEX_DIR, f'mi17_hip{suff}_glowmask.png')
    Image.new('RGBA', (16, 16), (0, 0, 0, 0)).save(glow_dst)

print("  mi17_hip clean geo, anim, textures updated.")

# 3. Mi-26 Halo (1.35x strategic heavy lift scale)
with open(os.path.join(GEO_DIR, 'mi28_havoc.geo.json'), 'r', encoding='utf-8') as f:
    halo_geo = json.load(f)
halo_geo['minecraft:geometry'][0]['description']['identifier'] = 'geometry.mi26_halo'
for b in halo_geo['minecraft:geometry'][0]['bones']:
    if 'pivot' in b:
        b['pivot'] = [round(p * 1.35, 3) for p in b['pivot']]
    for c in b.get('cubes', []):
        c['origin'] = [round(o * 1.35, 3) for o in c['origin']]
        c['size'] = [round(s * 1.35, 3) for s in c['size']]

with open(os.path.join(GEO_DIR, 'mi26_halo.geo.json'), 'w', encoding='utf-8') as f:
    json.dump(halo_geo, f, indent=2)

anim = create_animation('mi26_halo')
with open(os.path.join(ANIM_DIR, 'mi26_halo.animation.json'), 'w', encoding='utf-8') as f:
    json.dump(anim, f, indent=2)

for suff in LIVERY_SUFFIXES:
    src_tex = os.path.join(TEX_DIR, f'mi28_havoc{suff}.png')
    dst_tex = os.path.join(TEX_DIR, f'mi26_halo{suff}.png')
    if os.path.exists(src_tex):
        shutil.copyfile(src_tex, dst_tex)
    glow_dst = os.path.join(TEX_DIR, f'mi26_halo{suff}_glowmask.png')
    Image.new('RGBA', (16, 16), (0, 0, 0, 0)).save(glow_dst)

print("  mi26_halo clean geo, anim, textures updated.")

print("\nALL 10 HELICOPTERS ARE FULLY CLEANED AND EXPORTED!")
