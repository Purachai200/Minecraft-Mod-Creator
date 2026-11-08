import subprocess, tempfile, re, os, zipfile, json, math

def convert_flan_model(class_bytes, model_name, texture_name, jar_path, out_geo_path, out_png_path):
    tmp = tempfile.gettempdir() + f'/{model_name}.class'
    with open(tmp, 'wb') as f:
        f.write(class_bytes)

    res = subprocess.run(['javap', '-p', '-c', tmp], capture_output=True, text=True)
    lines = res.stdout.splitlines()

    constant_re = re.compile(r'// (float|int|String) (.+)')
    field_re = re.compile(r'// Field (\w+):')

    # Detect texture size
    tex_w, tex_h = 1024, 1024
    for i, l in enumerate(lines[:100]):
        if 'textureX' in l and i > 0:
            prev = lines[i-1].strip()
            if 'sipush' in prev or 'bipush' in prev or 'ldc' in prev:
                tokens = prev.split()
                if len(tokens) >= 2 and tokens[-1].isdigit():
                    tex_w = int(tokens[-1])
        if 'textureY' in l and i > 0:
            prev = lines[i-1].strip()
            if 'sipush' in prev or 'bipush' in prev or 'ldc' in prev:
                tokens = prev.split()
                if len(tokens) >= 2 and tokens[-1].isdigit():
                    tex_h = int(tokens[-1])

    # We will parse method by method
    methods = {}
    current_method = None
    cur_lines = []
    for l in lines:
        if l.startswith('  private void init') or l.startswith('  public '):
            if current_method and cur_lines:
                methods[current_method] = cur_lines
            m_name = l.strip().split('(')[0].split()[-1]
            current_method = m_name
            cur_lines = []
        elif current_method:
            cur_lines.append(l)
    if current_method and cur_lines:
        methods[current_method] = cur_lines

    print(f'Model {model_name}: Texture {tex_w}x{tex_h}, {len(methods)} methods')

    def eval_val(token, line):
        if token.startswith('iconst_'):
            return int(token.replace('iconst_m1', '-1').replace('iconst_', ''))
        elif token == 'fconst_0': return 0.0
        elif token == 'fconst_1': return 1.0
        elif token == 'fconst_2': return 2.0
        elif token in ('bipush', 'sipush'):
            return int(token) # handled caller
        elif token in ('ldc', 'ldc_w'):
            m = constant_re.search(line)
            if m:
                t, v = m.group(1), m.group(2)
                if t == 'float': return float(v.rstrip('f'))
                elif t == 'int': return int(v)
            return 0.0
        return 0.0

    all_bones = {} # bone_name -> list of cubes

    for m_name, m_lines in methods.items():
        if not m_name.startswith('init'): continue
        # Identify bone group from method name
        bone_group = 'body'
        low = m_name.lower()
        if 'nose' in low or 'cockpit' in low: bone_group = 'cockpit'
        elif 'tailrotor' in low or 'helitailrotor' in low: bone_group = 'tail_rotor'
        elif 'mainrotor' in low or 'helimainrotor' in low: bone_group = 'main_rotor'
        elif 'tail' in low or 'yaw' in low or 'rudder' in low: bone_group = 'tail'
        elif 'skid' in low or 'wheel' in low or 'gear' in low: bone_group = 'skids'
        elif 'leftwing' in low: bone_group = 'wing_left'
        elif 'rightwing' in low: bone_group = 'wing_right'
        elif 'hud' in low or 'seat' in low: bone_group = 'cockpit'
        elif 'turret' in low or 'gun' in low: bone_group = 'turret'
        else: bone_group = 'body'

        if bone_group not in all_bones:
            all_bones[bone_group] = []

        # Pass 1: find UVs for each index
        uvs = {}
        # Pass 2: find addShapeBox / addBox and setRotationPoint
        stack = []
        for line in m_lines:
            line_str = line.strip()
            if not line_str: continue
            parts = line_str.split(': ')
            if len(parts) != 2: continue
            tokens = parts[1].split()
            op = tokens[0]

            if op.startswith('iconst_'):
                stack.append(int(op.replace('iconst_m1', '-1').replace('iconst_', '')))
            elif op == 'fconst_0': stack.append(0.0)
            elif op == 'fconst_1': stack.append(1.0)
            elif op == 'fconst_2': stack.append(2.0)
            elif op in ('bipush', 'sipush'):
                stack.append(int(tokens[1]))
            elif op in ('ldc', 'ldc_w'):
                m = constant_re.search(line_str)
                if m:
                    t, v = m.group(1), m.group(2)
                    if t == 'float': stack.append(float(v.rstrip('f')))
                    elif t == 'int': stack.append(int(v))
                    else: stack.append(v)
                else: stack.append(0.0)
            elif op.startswith('aload'):
                stack.append('ref')
            elif op == 'dup':
                if stack: stack.append(stack[-1])
            elif op == 'new':
                stack.append('new_obj')
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
                    if isinstance(val, tuple) and val[0] == 'mrt':
                        uvs[idx] = val[1]
            elif op == 'invokespecial':
                if 'ModelRendererTurbo' in line_str and '<init>' in line_str:
                    if len(stack) >= 5:
                        h = stack.pop()
                        w = stack.pop()
                        v = stack.pop()
                        u = stack.pop()
                        obj = stack.pop()
                        stack.append(('mrt', (int(u) if isinstance(u, (int, float)) else 0,
                                               int(v) if isinstance(v, (int, float)) else 0)))
            elif op == 'invokevirtual':
                if 'addShapeBox' in line_str:
                    if len(stack) >= 32:
                        args = [stack.pop() for _ in range(31)]
                        args.reverse()
                        obj = stack.pop()
                        elem_idx = obj[2] if isinstance(obj, tuple) and len(obj) >= 3 else len(all_bones[bone_group])
                        x, y, z = float(args[0]), float(args[1]), float(args[2])
                        w, h, d = float(args[3]), float(args[4]), float(args[5])
                        cur_uv = uvs.get(elem_idx, (0, 0))
                        all_bones[bone_group].append({
                            'idx': elem_idx,
                            'uv': cur_uv,
                            'pos': (x, y, z),
                            'size': (w, h, d),
                            'rotPoint': (0.0, 0.0, 0.0),
                            'rotAngle': (0.0, 0.0, 0.0)
                        })
                elif 'addBox' in line_str:
                    # addBox(x, y, z, w, h, d) or (x, y, z, w, h, d, expansion)
                    param_count = 7 if '(FFFIIIF)' in line_str or '(FFFFFF)' in line_str else 6
                    if len(stack) >= param_count + 1:
                        args = [stack.pop() for _ in range(param_count)]
                        args.reverse()
                        obj = stack.pop()
                        elem_idx = obj[2] if isinstance(obj, tuple) and len(obj) >= 3 else len(all_bones[bone_group])
                        x, y, z = float(args[0]), float(args[1]), float(args[2])
                        w, h, d = float(args[3]), float(args[4]), float(args[5])
                        cur_uv = uvs.get(elem_idx, (0, 0))
                        all_bones[bone_group].append({
                            'idx': elem_idx,
                            'uv': cur_uv,
                            'pos': (x, y, z),
                            'size': (w, h, d),
                            'rotPoint': (0.0, 0.0, 0.0),
                            'rotAngle': (0.0, 0.0, 0.0)
                        })
                elif 'func_78793_a' in line_str or 'setRotationPoint' in line_str:
                    if len(stack) >= 4:
                        rz = stack.pop()
                        ry = stack.pop()
                        rx = stack.pop()
                        obj = stack.pop()
                        elem_idx = obj[2] if isinstance(obj, tuple) and len(obj) >= 3 else None
                        if elem_idx is not None and all_bones[bone_group]:
                            for b in reversed(all_bones[bone_group]):
                                if b.get('idx') == elem_idx:
                                    b['rotPoint'] = (float(rx), float(ry), float(rz))
                                    break
            elif op == 'putfield':
                m = field_re.search(line_str)
                f_name = m.group(1) if m else ''
                if f_name.startswith('rotateAngle') and len(stack) >= 2:
                    val = stack.pop()
                    obj = stack.pop()
                    elem_idx = obj[2] if isinstance(obj, tuple) and len(obj) >= 3 else None
                    if elem_idx is not None and all_bones[bone_group]:
                        for b in reversed(all_bones[bone_group]):
                            if b.get('idx') == elem_idx:
                                ra = list(b.get('rotAngle', (0.0, 0.0, 0.0)))
                                deg = float(val) * 180.0 / math.pi
                                if f_name == 'rotateAngleX': ra[0] = deg
                                elif f_name == 'rotateAngleY': ra[1] = deg
                                elif f_name == 'rotateAngleZ': ra[2] = deg
                                b['rotAngle'] = tuple(ra)
                                break

    # Convert Flan coordinate system to GeckoLib Bedrock format:
    # Flan's ModelBase:
    # X is left, Y is DOWN (0 at top, +Y downwards), Z is forward/back.
    # GeckoLib:
    # X is left (negated or standard), Y is UP (0 at ground, +Y upwards), Z is nose forward.
    # In Flan ModelPlane, flipAll() flips Y and Z!
    # Let's inspect coordinates to place them accurately.
    gecko_bones = []

    # Root bone
    gecko_bones.append({
        'name': 'root',
        'pivot': [0.0, 0.0, 0.0]
    })

    total_cubes = 0
    for b_name, boxes in all_bones.items():
        if not boxes: continue
        cubes = []
        for b in boxes:
            x, y, z = b['pos']
            w, h, d = b['size']
            rx, ry, rz = b['rotPoint']
            u, v = b['uv']

            # In Flan ModelRendererTurbo:
            # Box absolute position in model space:
            # gx = rx + x
            # gy = -(ry + y + h) + 24.0 (flip Y so +Y is up, ground is at Y=0)
            # gz = -(rz + z + d) (flip Z so nose is +Z)
            # Let's use clean standard Minecraft transformation:
            box_x = rx + x
            box_y = -(ry + y + h) + 24.0
            box_z = -(rz + z + d)

            cube_data = {
                'origin': [round(box_x, 3), round(box_y, 3), round(box_z, 3)],
                'size': [max(0.1, round(w, 3)), max(0.1, round(h, 3)), max(0.1, round(d, 3))],
                'uv': [int(u), int(v)]
            }
            cubes.append(cube_data)
            total_cubes += 1

        # Calculate pivot as average of rotation points
        piv_x = sum(b['rotPoint'][0] for b in boxes) / len(boxes)
        piv_y = -sum(b['rotPoint'][1] for b in boxes) / len(boxes) + 24.0
        piv_z = -sum(b['rotPoint'][2] for b in boxes) / len(boxes)

        parent = 'root'
        gecko_bones.append({
            'name': b_name,
            'parent': parent,
            'pivot': [round(piv_x, 3), round(piv_y, 3), round(piv_z, 3)],
            'cubes': cubes
        })

    geo_data = {
        'format_version': '1.12.0',
        'minecraft:geometry': [
            {
                'description': {
                    'identifier': f'geometry.{model_name.lower()}',
                    'texture_width': tex_w,
                    'texture_height': tex_h,
                    'visible_bounds_width': 12,
                    'visible_bounds_height': 8,
                    'visible_bounds_offset': [0, 3, 0]
                },
                'bones': gecko_bones
            }
        ]
    }

    os.makedirs(os.path.dirname(out_geo_path), exist_ok=True)
    with open(out_geo_path, 'w', encoding='utf-8') as f:
        json.dump(geo_data, f, indent=2)

    print(f'Successfully wrote {out_geo_path}: {total_cubes} cubes across {len(gecko_bones)} bones!')

    # Extract texture
    if jar_path and out_png_path:
        with zipfile.ZipFile(jar_path, 'r') as z:
            tex_paths = [
                f'assets/flansmod/skins/{texture_name}.png',
                f'assets/flansmod/skins/{texture_name}',
                f'assets/flansmod/textures/entity/{texture_name}.png'
            ]
            for tp in tex_paths:
                if tp in z.namelist():
                    os.makedirs(os.path.dirname(out_png_path), exist_ok=True)
                    with open(out_png_path, 'wb') as pf:
                        pf.write(z.read(tp))
                    print(f'Extracted texture to {out_png_path}')
                    break

jar_gfs = r'c:\Users\Purachai\Downloads\Flans\Global Firestorm v3.2 - (Port 1.12.2).jar'
art_dir = r'C:\Users\Purachai\.gemini\antigravity\brain\bb2a27ed-6cbc-413b-9585-0348f0bb3912'

with zipfile.ZipFile(jar_gfs, 'r') as z:
    for m, t in [('ModelAH6J', 'skinah6j'), ('ModelUH1Y', 'skinuh1y')]:
        class_bytes = z.read(f'com/flansmod/client/model/gfs/{m}.class')
        geo_out = os.path.join(art_dir, f'{m.lower()}.geo.json')
        png_out = os.path.join(art_dir, f'{t}.png')
        convert_flan_model(class_bytes, m, t, jar_gfs, geo_out, png_out)
