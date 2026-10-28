#!/usr/bin/env python3
"""Builds cockpit 1st-person models for Trooper Titan (Mining Drill & Chainsaw),
Scout Titan (Light SMG) and Shade Titan, properly transformed from 3rd-person geometry and
mapped to each titan's 1024x1024 texture atlas.
"""
import json
import os

P3 = [-19.8, 39.8, 10.3]
P1 = [-4.3347, -48.33493, 57.2958]
SCALE = 1.25952

def box_to_face_uv(uv, size):
    """Bedrock box-UV layout for a cube of `size`, spelled out per face. A box UV is laid out from the cube's
    own size, so a scaled-up cube would read past its atlas patch into its neighbours; per-face UVs keep the
    unscaled patch."""
    u, v = uv
    w, h, d = size
    return {
        'north': {'uv': [u + d, v + d], 'uv_size': [w, h]},
        'east': {'uv': [u, v + d], 'uv_size': [d, h]},
        'south': {'uv': [u + d + w + d, v + d], 'uv_size': [w, h]},
        'west': {'uv': [u + d + w, v + d], 'uv_size': [d, h]},
        'up': {'uv': [u + d, v], 'uv_size': [w, d]},
        'down': {'uv': [u + d + w, v + d], 'uv_size': [w, -d]},
    }


def _uv_selfcheck():
    faces = box_to_face_uv([10, 20], [3, 4, 5])
    right = max(f['uv'][0] + f['uv_size'][0] for f in faces.values())
    bottom = max(f['uv'][1] + max(f['uv_size'][1], 0) for f in faces.values())
    assert (right, bottom) == (10 + 2 * (3 + 5), 20 + 5 + 4), (right, bottom)  # stays inside the box patch


def transform_cube(c, p3=P3, p1=P1, scale=SCALE):
    o3 = c['origin']
    s3 = c['size']
    o1 = [round(p1[i] + (o3[i] - p3[i]) * scale, 4) for i in range(3)]
    s1 = [round(s3[i] * scale, 4) for i in range(3)]
    uv = box_to_face_uv(c['uv'], s3) if isinstance(c['uv'], list) else c['uv']
    res = {'origin': o1, 'size': s1, 'uv': uv}
    if 'rotation' in c and c['rotation'] is not None:
        res['rotation'] = c['rotation']
    if 'pivot' in c and c['pivot'] is not None:
        piv3 = c['pivot']
        res['pivot'] = [round(p1[i] + (piv3[i] - p3[i]) * scale, 4) for i in range(3)]
    return res

def material_patches(module):
    """(uv, size) of the largest cube of each material in a titan generator's atlas, so the cockpit arms
    wear the same paint as the titan outside however its model is laid out."""
    import importlib
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scratch'))
    T = importlib.reload(importlib.import_module('build_trooper_assets'))
    if module != 'build_trooper_assets':  # the Scout/Shade builders swap their bones into the Trooper module
        importlib.reload(importlib.import_module(module))
    T.pack()
    return {m: T.swatch(m) for m in ('paint', 'dark', 'steel', 'metal')}

def map_arm_cubes(cubes, patches):
    """Gives Ion-shaped arm/finger cubes per-face UVs inside one of the titan's material patches."""
    out = []
    for i, c in enumerate(cubes):
        c_copy = dict(c)
        # Pistons / hydraulic rods
        if c.get('size', [0,0,0])[0] < 2.0 or c.get('size', [0,0,0])[2] < 2.0:
            mat = 'steel'
        elif i in [0, 1, 4, 5]:
            mat = 'paint'
        else:
            mat = 'dark'
        c_copy['uv'] = box_to_face_uv(*patches[mat])
        out.append(c_copy)
    return out

def remap_arm_bone(b, patches):
    """Arm, hand and finger bones of the Ion first-person rig, repainted from the titan's atlas."""
    name = b['name']
    hand = box_to_face_uv(*patches['metal'])
    if name in ('rightArm2', 'leftArm1', 'leftShoulderArmor', 'leftElbowArmor', 'leftArm2'):
        return map_arm_cubes(b['cubes'], patches)
    if name in ('rightHand', 'leftHand') or 'Finger' in name:
        return [{'origin': c['origin'], 'size': c['size'], 'uv': hand} for c in b['cubes']]
    return None

def build_trooper_cockpit():
    base_path = 'Titan Combat/src/main/resources/assets/titancombat/geo/cockpit/ion_titan_1st.geo.json'
    with open(base_path) as f:
        ion_1st = json.load(f)
    
    with open('Titan Combat/src/main/resources/assets/titancombat/geo/trooper_titan.geo.json') as f:
        trooper_3rd = json.load(f)
    tb = {b['name']: b for b in trooper_3rd['minecraft:geometry'][0]['bones']}
    
    drill_cubes = [transform_cube(c) for c in tb['drill']['cubes']]
    saw_cubes = [transform_cube(c) for c in tb['chainsaw']['cubes']]
    
    patches = material_patches('build_trooper_assets')
    
    laser_bones = {'laser1', 'laser2', 'laser3', 'laserHead', 'laserExpand1', 'laserExpand2', 'laser_locator'}
    weapon_parts = {'rotate', 'clip', 'weaponTopOpen', 'weaponRightOpen', 'weaponLeftOpen'}
    
    new_bones = []
    for b in ion_1st['minecraft:geometry'][0]['bones']:
        name = b['name']
        if name in laser_bones or name in weapon_parts:
            continue
        
        b_copy = dict(b)
        
        if name == 'weapon':
            b_copy['cubes'] = [] # empty weapon parent bone
        elif name == 'locator_fire_1st':
            b_copy['pivot'] = [38.0, -48.33493, 57.2958]
        elif remap_arm_bone(b, patches) is not None:
            b_copy['cubes'] = remap_arm_bone(b, patches)
            
        new_bones.append(b_copy)
        
        if name == 'weapon':
            # Add drill sub-bone
            new_bones.append({
                'name': 'drill',
                'parent': 'weapon',
                'pivot': P1,
                'rotation': [0, 0, 0],
                'cubes': drill_cubes
            })
            # Add chainsaw sub-bone
            new_bones.append({
                'name': 'chainsaw',
                'parent': 'weapon',
                'pivot': P1,
                'rotation': [0, 0, 0],
                'cubes': saw_cubes
            })
    
    geo = {
        'format_version': '1.12.0',
        'minecraft:geometry': [{
            'description': {
                'identifier': 'geometry.trooper_titan.1st',
                'texture_width': 1024,
                'texture_height': 1024,
                'visible_bounds_width': 7,
                'visible_bounds_height': 7,
                'visible_bounds_offset': [0, 2, 0]
            },
            'bones': new_bones
        }]
    }
    
    out_path = 'Titan Combat/src/main/resources/assets/titancombat/geo/cockpit/trooper_titan_1st.geo.json'
    with open(out_path, 'w') as f:
        json.dump(geo, f, indent=2)
    print(f'Wrote {out_path} ({len(new_bones)} bones)')

def build_light_cockpit(titan='scout'):
    """Scout (Light SMG in hand) or Shade (no factory gun) cockpit arms on the Ion rig."""
    base_path = 'Titan Combat/src/main/resources/assets/titancombat/geo/cockpit/ion_titan_1st.geo.json'
    with open(base_path) as f:
        ion_1st = json.load(f)
    
    with open(f'Titan Combat/src/main/resources/assets/titancombat/geo/{titan}_titan.geo.json') as f:
        third = json.load(f)
    sb = {b['name']: b for b in third['minecraft:geometry'][0]['bones']}

    smg_cubes = [transform_cube(c) for c in sb['weapon'].get('cubes', [])]
    
    patches = material_patches(f'build_{titan}_assets')
    
    laser_bones = {'laser1', 'laser2', 'laser3', 'laserHead', 'laserExpand1', 'laserExpand2', 'laser_locator'}
    weapon_parts = {'rotate', 'clip', 'weaponTopOpen', 'weaponRightOpen', 'weaponLeftOpen'}
    
    new_bones = []
    for b in ion_1st['minecraft:geometry'][0]['bones']:
        name = b['name']
        if name in laser_bones or name in weapon_parts:
            continue
        
        b_copy = dict(b)
        
        if name == 'weapon':
            b_copy['cubes'] = smg_cubes # SMG cubes directly on weapon bone
        elif name == 'locator_fire_1st':
            b_copy['pivot'] = [round(P1[0] + 34 * SCALE, 4), -48.33493, 57.2958]  # SMG muzzle (build_scout_smg.MUZZLE_X)
        elif remap_arm_bone(b, patches) is not None:
            b_copy['cubes'] = remap_arm_bone(b, patches)
            
        new_bones.append(b_copy)
    
    geo = {
        'format_version': '1.12.0',
        'minecraft:geometry': [{
            'description': {
                'identifier': f'geometry.{titan}_titan.1st',
                'texture_width': 1024,
                'texture_height': 1024,
                'visible_bounds_width': 7,
                'visible_bounds_height': 7,
                'visible_bounds_offset': [0, 2, 0]
            },
            'bones': new_bones
        }]
    }
    
    out_path = f'Titan Combat/src/main/resources/assets/titancombat/geo/cockpit/{titan}_titan_1st.geo.json'
    with open(out_path, 'w') as f:
        json.dump(geo, f, indent=2)
    print(f'Wrote {out_path} ({len(new_bones)} bones)')

if __name__ == '__main__':
    _uv_selfcheck()
    build_trooper_cockpit()
    build_light_cockpit('scout')
    build_light_cockpit('shade')
