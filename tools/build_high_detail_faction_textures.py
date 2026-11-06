#!/usr/bin/env python3
import json
import os
import struct
import zlib
import math
import random

# =========================================================================
# HIGH-FIDELITY FACTION & CAMO TEXTURE GENERATOR (1024x1024)
# =========================================================================

ROOT_DIR = "Titan Combat/src/main/resources/assets/titancombat"
GEO_DIR = os.path.join(ROOT_DIR, "geo")
TEX_DIR = os.path.join(ROOT_DIR, "textures/entity/titan")

# Faction Color Schemes (0..8)
# primary_armor, secondary_armor, frame_metal, hydraulic_steel, visor_glow, visor_core, hazard_color
SCHEMES = [
    # 0: Factory Standard (Graphite & Titanium)
    {
        'name': 'factory_standard',
        'primary': (65, 70, 78),
        'secondary': (195, 205, 215),
        'frame': (35, 37, 42),
        'steel': (165, 172, 180),
        'visor': (0, 220, 255),
        'visor_core': (220, 250, 255),
        'hazard': (235, 185, 30)
    },
    # 1: Desert Tan (Khaki & Dust Earth)
    {
        'name': 'desert_tan',
        'primary': (185, 158, 112),
        'secondary': (115, 92, 62),
        'frame': (42, 38, 32),
        'steel': (155, 150, 140),
        'visor': (255, 180, 40),
        'visor_core': (255, 240, 200),
        'hazard': (235, 185, 30)
    },
    # 2: Viper Syndicate (Woodland / Jungle Green)
    {
        'name': 'viper_syndicate',
        'primary': (48, 80, 42),
        'secondary': (75, 105, 58),
        'frame': (32, 38, 30),
        'steel': (140, 160, 145),
        'visor': (0, 255, 100),
        'visor_core': (210, 255, 225),
        'hazard': (235, 185, 30)
    },
    # 3: Urban Digital (Battleship Gray & Slate)
    {
        'name': 'urban_digital',
        'primary': (95, 102, 112),
        'secondary': (55, 60, 68),
        'frame': (32, 35, 40),
        'steel': (160, 168, 178),
        'visor': (80, 200, 255),
        'visor_core': (220, 245, 255),
        'hazard': (235, 185, 30)
    },
    # 4: Arctic Snow (Alpine White & Ice Steel)
    {
        'name': 'arctic_snow',
        'primary': (220, 228, 235),
        'secondary': (120, 140, 165),
        'frame': (40, 44, 52),
        'steel': (175, 185, 195),
        'visor': (40, 210, 255),
        'visor_core': (240, 255, 255),
        'hazard': (235, 185, 30)
    },
    # 5: Crimson Legion (Vibrant Crimson & Gunmetal)
    {
        'name': 'crimson_legion',
        'primary': (168, 28, 28),
        'secondary': (50, 44, 46),
        'frame': (34, 32, 35),
        'steel': (160, 155, 158),
        'visor': (255, 90, 20),
        'visor_core': (255, 230, 180),
        'hazard': (240, 160, 20)
    },
    # 6: Apex Vanguard (Military Cobalt Blue & White)
    {
        'name': 'apex_vanguard',
        'primary': (26, 72, 168),
        'secondary': (235, 240, 248),
        'frame': (32, 36, 45),
        'steel': (165, 175, 190),
        'visor': (0, 235, 255),
        'visor_core': (220, 255, 255),
        'hazard': (235, 185, 30)
    },
    # 7: Solaris Corp (Industrial Hazard Yellow & Tungsten)
    {
        'name': 'solaris_corp',
        'primary': (225, 170, 18),
        'secondary': (42, 44, 48),
        'frame': (34, 36, 40),
        'steel': (165, 168, 175),
        'visor': (255, 230, 40),
        'visor_core': (255, 255, 220),
        'hazard': (235, 185, 30)
    },
    # 8: Shadow Ops (Stealth Matte Carbon & Purple)
    {
        'name': 'shadow_ops',
        'primary': (26, 27, 30),
        'secondary': (68, 38, 92),
        'frame': (20, 21, 24),
        'steel': (110, 112, 120),
        'visor': (195, 45, 255),
        'visor_core': (245, 200, 255),
        'hazard': (200, 40, 255)
    }
]

FRAMES = [
    'striker_frame',
    'vanguard_frame',
    'colossus_frame',
    'terrain_frame',
    'cyclops_frame',
    'spider_frame'
]

def make_png_bytes(width, height, raw_pixels):
    # raw_pixels is bytearray of size width * height * 4
    raw_data = bytearray()
    row_bytes = width * 4
    for y in range(height):
        raw_data.append(0) # filter type 0
        raw_data.extend(raw_pixels[y * row_bytes : (y + 1) * row_bytes])

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(bytes(raw_data), level=7))
    iend = chunk(b'IEND', b'')
    return header + ihdr + idat + iend

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def blend(c1, c2, factor):
    return (
        clamp(c1[0] * (1.0 - factor) + c2[0] * factor),
        clamp(c1[1] * (1.0 - factor) + c2[1] * factor),
        clamp(c1[2] * (1.0 - factor) + c2[2] * factor)
    )

def mul(c, f):
    return (clamp(c[0] * f), clamp(c[1] * f), clamp(c[2] * f))

def determine_material(bone_name, cube_idx, cube):
    bn = bone_name.lower()
    sz = cube.get('size', [1, 1, 1])
    is_thin = min(sz) <= 1.0

    if any(k in bn for k in ['eye', 'visor', 'optic', 'sensor', 'lens', 'glass']):
        return 'visor'
    if any(k in bn for k in ['tread', 'track', 'wheel', 'caterpillar', 'foot', 'toe', 'sole']):
        return 'tread'
    if any(k in bn for k in ['piston', 'actuator', 'hydraulic', 'shaft', 'cylinder']):
        return 'steel'
    if any(k in bn for k in ['hazard', 'stripe', 'warning', 'mantlet_edge']):
        return 'hazard'
    if any(k in bn for k in ['armor', 'pauldron', 'plate', 'shield', 'chest', 'hull', 'turret', 'cupola', 'hatch']):
        # Alternate primary and secondary armor plates based on cube index
        return 'primary_armor' if cube_idx % 3 != 1 else 'secondary_armor'
    if any(k in bn for k in ['joint', 'hinge', 'spine', 'chassis', 'pelvis', 'waist', 'collar', 'frame', 'core']):
        return 'frame'
    if is_thin:
        return 'steel'
    return 'primary_armor' if cube_idx % 2 == 0 else 'frame'

def render_model_textures():
    for frm in FRAMES:
        geo_name = f"{frm}_titan.geo.json"
        geo_path = os.path.join(GEO_DIR, geo_name)
        if not os.path.exists(geo_path):
            print(f"Skipping {geo_name} (not found)")
            continue

        with open(geo_path, 'r') as f:
            geo_data = json.load(f)

        geom = geo_data['minecraft:geometry'][0]
        tw = geom['description']['texture_width']
        th = geom['description']['texture_height']
        bones = geom['bones']

        print(f"Processing {frm} ({tw}x{th}) with {len(bones)} bones...")

        out_dir = os.path.join(TEX_DIR, frm)
        os.makedirs(out_dir, exist_ok=True)

        for s_idx, scheme in enumerate(SCHEMES):
            # 1024x1024 pixel buffer initialized with subtle dark metal background
            buf = bytearray(tw * th * 4)
            # Fill default background: dark textured metal plate
            bg_col = scheme['frame']
            for y in range(th):
                row_off = y * tw * 4
                for x in range(tw):
                    noise = ((x * 17 + y * 31) % 9) - 4
                    grid = (x % 32 == 0 or y % 32 == 0)
                    base_lum = 0.85 if grid else 1.0
                    r = clamp((bg_col[0] + noise) * base_lum)
                    g = clamp((bg_col[1] + noise) * base_lum)
                    b = clamp((bg_col[2] + noise) * base_lum)
                    buf[row_off + x * 4 : row_off + x * 4 + 4] = bytes((r, g, b, 255))

            def put_pixel(x, y, r, g, b, a=255):
                if 0 <= x < tw and 0 <= y < th:
                    idx = (y * tw + x) * 4
                    buf[idx : idx + 4] = bytes((clamp(r), clamp(g), clamp(b), clamp(a)))

            # Iterate all bones and their cubes
            for b in bones:
                b_name = b.get('name', '')
                cubes = b.get('cubes', [])
                for ci, c in enumerate(cubes):
                    mat = determine_material(b_name, ci, c)
                    uv = c.get('uv')
                    sz = c.get('size', [1, 1, 1])
                    w_cube, h_cube, d_cube = int(sz[0]), int(sz[1]), int(sz[2])

                    # Collect face UV rectangles: list of (fx, fy, fw, fh, face_name)
                    faces = []
                    if isinstance(uv, dict):
                        for face_name, finfo in uv.items():
                            if isinstance(finfo, dict) and 'uv' in finfo:
                                u0, v0 = int(finfo['uv'][0]), int(finfo['uv'][1])
                                u_sz = finfo.get('uv_size', [1, 1])
                                fw, fh = abs(int(u_sz[0])), abs(int(u_sz[1]))
                                faces.append((u0, v0, fw, fh, face_name))
                    elif isinstance(uv, list) and len(uv) >= 2:
                        # Box UV format: [u, v]
                        u, v = int(uv[0]), int(uv[1])
                        # Box faces:
                        # up: [u + d, v, w, d]
                        # down: [u + d + w, v, w, d]
                        # east: [u, v + d, d, h]
                        # north: [u + d, v + d, w, h]
                        # west: [u + d + w, v + d, d, h]
                        # south: [u + d + w + d, v + d, w, h]
                        faces.append((u + d_cube, v, w_cube, d_cube, 'up'))
                        faces.append((u + d_cube + w_cube, v, w_cube, d_cube, 'down'))
                        faces.append((u, v + d_cube, d_cube, h_cube, 'east'))
                        faces.append((u + d_cube, v + d_cube, w_cube, h_cube, 'north'))
                        faces.append((u + d_cube + w_cube, v + d_cube, d_cube, h_cube, 'west'))
                        faces.append((u + 2 * d_cube + w_cube, v + d_cube, w_cube, h_cube, 'south'))

                    # Render each face into buffer
                    for fx, fy, fw, fh, fname in faces:
                        if fw <= 0 or fh <= 0: continue
                        for j in range(fh):
                            for i in range(fw):
                                px, py = fx + i, fy + j
                                edge = min(i, j, fw - 1 - i, fh - 1 - j)
                                micro_noise = ((px * 13 + py * 29) % 7) - 3

                                if mat == 'visor':
                                    # Visor optic: bright glowing core in center, glowing ring around
                                    is_core = (1 <= i <= fw - 2 and 1 <= j <= fh - 2)
                                    col = scheme['visor_core'] if is_core else scheme['visor']
                                    put_pixel(px, py, col[0], col[1], col[2], 255)
                                elif mat == 'hazard':
                                    stripe = ((i + j) // 4) % 2 == 0
                                    col = scheme['hazard'] if stripe else (25, 25, 28)
                                    put_pixel(px, py, col[0] + micro_noise, col[1] + micro_noise, col[2] + micro_noise, 255)
                                elif mat == 'tread':
                                    t_stripe = ((i + j) // 3) % 2 == 0
                                    base_c = (42, 44, 48) if t_stripe else (26, 27, 30)
                                    if edge == 0: base_c = mul(base_c, 0.7)
                                    put_pixel(px, py, base_c[0] + micro_noise, base_c[1] + micro_noise, base_c[2] + micro_noise, 255)
                                elif mat == 'steel':
                                    base_c = scheme['steel']
                                    # Directional specular sheen
                                    sheen = 1.0 + 0.15 * math.sin((i + j) * 0.5)
                                    if edge == 0: sheen *= 0.75
                                    put_pixel(px, py, base_c[0] * sheen + micro_noise, base_c[1] * sheen + micro_noise, base_c[2] * sheen + micro_noise, 255)
                                elif mat == 'frame':
                                    base_c = scheme['frame']
                                    shade = 1.0
                                    if edge == 0: shade = 0.65
                                    elif edge == 1: shade = 0.85
                                    put_pixel(px, py, base_c[0] * shade + micro_noise, base_c[1] * shade + micro_noise, base_c[2] * shade + micro_noise, 255)
                                else:
                                    # Armor plating: primary or secondary
                                    base_c = scheme['primary'] if mat == 'primary_armor' else scheme['secondary']
                                    shade = 1.0
                                    # Bevels & Panel seams
                                    if edge == 0:
                                        shade = 0.62 # Dark recessed seam line
                                    elif (j == 1 and fname not in ('down', 'up')) or (i == 1 and fname in ('north', 'south')):
                                        shade = 1.20 # Light highlight edge
                                    elif (j == fh - 2 and fname not in ('down', 'up')) or (i == fw - 2 and fname in ('north', 'south')):
                                        shade = 0.80 # Lower chamfer shadow

                                    # Rivet bolts in corners of larger armor plates
                                    if fw >= 8 and fh >= 8 and i in (1, fw - 2) and j in (1, fh - 2):
                                        col = (210, 215, 220) # Chrome rivet
                                        put_pixel(px, py, col[0], col[1], col[2], 255)
                                        continue

                                    put_pixel(px, py, base_c[0] * shade + micro_noise, base_c[1] * shade + micro_noise, base_c[2] * shade + micro_noise, 255)

            # Write out PNG file
            suffix = "" if s_idx == 0 else f"_{s_idx}"
            out_file = os.path.join(out_dir, f"{frm}_titan{suffix}.png")
            png_bytes = make_png_bytes(tw, th, buf)
            with open(out_file, 'wb') as f_out:
                f_out.write(png_bytes)
            print(f"  -> Generated {out_file} ({scheme['name']})")

if __name__ == '__main__':
    render_model_textures()
    print("ALL 54 HIGH-FIDELITY FACTION TEXTURES GENERATED SUCCESSFULLY!")
