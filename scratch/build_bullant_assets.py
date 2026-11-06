"""Model BULLANT Autonomous Anti-Tank Unit (Spider Titan Frame Redesign).
Generates:
1. geo/spider_frame_titan.geo.json
2. animations/spider_frame_titan.animation.json
3. textures/entity/titan/spider_frame/spider_frame_titan.png (and _1 .. _8 camos)
"""
import json, os, random, struct, zlib, math, copy

ROOT = "Titan Combat/src/main/resources/assets/titancombat"
TEX = 1024
ID = "spider_frame"
SCALE = 1.35

def C(o, s, m, rot=None, piv=None, decal=None):
    c = {
        "o": [round(float(v) * SCALE, 3) for v in o],
        "s": [round(float(v) * SCALE, 3) for v in s],
        "m": m
    }
    if rot:
        c["rot"] = [round(float(v), 3) for v in rot]
        c["piv"] = [round(float(v) * SCALE, 3) for v in piv]
    if decal:
        c["decal"] = decal
    return c

def B(x0, x1, y0, y1, z0, z1, m, **kw):
    """Cube from min/max corners."""
    return C([x0, y0, z0], [x1 - x0, y1 - y0, z1 - z0], m, **kw)

def mirror(cubes):
    swap = {"east": "west", "west": "east"}
    out = []
    for c in cubes:
        m = dict(c)
        m["o"] = [-(c["o"][0] + c["s"][0]), c["o"][1], c["o"][2]]
        if "rot" in c:
            m["rot"] = [c["rot"][0], -c["rot"][1], -c["rot"][2]]
            m["piv"] = [-c["piv"][0], c["piv"][1], c["piv"][2]]
        if "decal" in c:
            m["decal"] = {swap.get(f, f): k for f, k in c["decal"].items()}
        out.append(m)
    return out

def mpiv(p):
    return [-p[0], p[1], p[2]]

def late(cubes):
    for c in cubes:
        c["late"] = True
    return cubes

def hub(cx, cy, cz, length, diam, m="dark"):
    """Round joint hub on an X hinge axis: octagonal drum with steel bolt cap."""
    x0 = cx - length / 2
    piv = [cx, cy, cz]
    return late([
        C([x0, cy - diam / 2, cz - diam / 2], [length, diam, diam], m),
        C([x0, cy - diam / 2, cz - diam / 2], [length, diam, diam], m, rot=[45, 0, 0], piv=piv),
        C([x0 - 0.6, cy - diam / 4, cz - diam / 4], [0.6, diam / 2, diam / 2], "steel")
    ])

def ball(cx, cy, cz, d, m="dark"):
    """Spherical joint: cube plus 45-degree rotations about X and Z."""
    o, s = [cx - d / 2, cy - d / 2, cz - d / 2], [d, d, d]
    return late([
        C(o, s, m),
        C(o, s, m, rot=[45, 0, 0], piv=[cx, cy, cz]),
        C(o, s, m, rot=[0, 0, 45], piv=[cx, cy, cz])
    ])

def leg_thigh_cubes(side, z_offset):
    """Upper arched thigh beam with under-mounted hydraulic cylinder and chrome rod."""
    # side: +1 for left (+x), -1 for right (-x)
    sgn = 1 if side > 0 else -1
    x_in = 14.0 * sgn
    x_out = 28.0 * sgn
    x_min = min(x_in, x_out)
    x_max = max(x_in, x_out)
    
    cubes = [
        # Upper arched armor beam (sloping up-outward)
        B(x_min, x_max, 24.0, 31.0, z_offset - 4.0, z_offset + 4.0, "paint"),
        B(x_min + 1.0 * sgn, x_max - 1.0 * sgn, 31.0, 33.0, z_offset - 3.0, z_offset + 3.0, "paint2"),
        # Hydraulic ram under thigh: dark sleeve + polished steel rod
        B(x_min + 2.0 * sgn, x_min + 8.0 * sgn, 21.0, 25.0, z_offset - 2.0, z_offset + 2.0, "dark"),
        B(x_min + 8.0 * sgn, x_max - 2.0 * sgn, 22.0, 24.0, z_offset - 1.2, z_offset + 1.2, "steel"),
    ]
    # Hip attachment knuckle
    cubes.extend(hub((x_in + x_in + 4.0 * sgn) / 2, 26.0, z_offset, 4.0, 7.0, "metal"))
    return cubes

def leg_knee_cubes(side, z_offset):
    """Massive circular knee rotary joint hub with forward armored knee shield and chevron decal."""
    sgn = 1 if side > 0 else -1
    cx = 28.0 * sgn
    cubes = []
    # Rotary disk hub (diameter 9)
    cubes.extend(hub(cx, 34.0, z_offset, 5.0, 9.0, "metal"))
    # Heavy front knee guard armor shield with white military triangle decal
    decal_face = "north" if z_offset <= 0 else "south"
    cubes.append(B(cx - 3.5, cx + 3.5, 27.0, 38.0, z_offset - 6.5 * sgn, z_offset - 3.5 * sgn, "paint", decal={decal_face: "triangle_down"}))
    cubes.append(B(cx - 2.5, cx + 2.5, 30.0, 37.0, z_offset - 7.2 * sgn, z_offset - 6.5 * sgn, "paint2"))
    return cubes

def leg_shin_cubes(side, z_offset):
    """Reinforced lower leg strut extending from knee down to ground clearance."""
    sgn = 1 if side > 0 else -1
    x_top = 28.0 * sgn
    x_bot = 36.0 * sgn
    x_min = min(x_top, x_bot)
    x_max = max(x_top, x_bot)
    cubes = [
        # Main vertical structural column
        B(x_min + 2.0 * sgn, x_max, 6.0, 34.0, z_offset - 3.0, z_offset + 3.0, "paint"),
        # Front/rear reinforcing ribs
        B(x_min + 3.0 * sgn, x_max - 1.0 * sgn, 8.0, 30.0, z_offset - 4.5, z_offset - 3.0, "paint2"),
        B(x_min + 3.0 * sgn, x_max - 1.0 * sgn, 8.0, 30.0, z_offset + 3.0, z_offset + 4.5, "paint2"),
        # Hydraulic line conduit on back of strut
        B(x_min + 4.0 * sgn, x_max - 2.0 * sgn, 10.0, 28.0, z_offset + 4.5, z_offset + 5.5, "dark"),
    ]
    return cubes

def leg_foot_cubes(side, z_offset):
    """Segmented ground crawler foot pad with rubber caterpillar grip cleats and rear recoil spur."""
    sgn = 1 if side > 0 else -1
    cx = 36.0 * sgn
    cubes = [
        # Main foot sole casting
        B(cx - 5.0, cx + 5.0, 1.5, 6.0, z_offset - 8.0, z_offset + 8.0, "dark"),
        # Segmented rubber caterpillar ground traction cleats (cleats at Y=0..1.5)
        B(cx - 4.5, cx + 4.5, 0.0, 1.5, z_offset - 7.5, z_offset - 4.5, "paint2"),
        B(cx - 4.5, cx + 4.5, 0.0, 1.5, z_offset - 3.0, z_offset - 0.0, "paint2"),
        B(cx - 4.5, cx + 4.5, 0.0, 1.5, z_offset + 1.5, z_offset + 4.5, "paint2"),
        B(cx - 4.5, cx + 4.5, 0.0, 1.5, z_offset + 5.5, z_offset + 7.5, "paint2"),
        # Ankle hinge knuckle
        B(cx - 3.5, cx + 3.5, 6.0, 9.0, z_offset - 3.0, z_offset + 3.0, "metal"),
        # Rear anti-recoil ground stabilization spur hook
        B(cx - 2.0, cx + 2.0, 1.0, 7.0, z_offset + 8.0, z_offset + 12.0, "steel")
    ]
    return cubes

def build_missile_pod(is_left=True):
    """Dual 4-pack Anti-Tank Missile Pod on dorsal gantry."""
    cubes = []
    x0, x1 = (7.0, 17.0) if is_left else (-17.0, -7.0)
    side_face = "west" if is_left else "east"
    gear_x = 6.6 if is_left else -6.6
    
    # Armored box container
    cubes.append(B(x0, x1, 42.0, 52.0, -4.0, 14.0, "paint", decal={side_face: "hazard"}))
    cubes.append(B(x0 + 0.5, x1 - 0.5, 41.5, 52.5, 13.5, 15.0, "paint2"))
    # Pod side circular rotary gear hinge with hazard ring
    cubes.extend(hub(gear_x, 47.0, 5.0, 1.2, 7.0, "metal"))
    
    # 4 Missile launch tubes (2x2) with warhead tips
    tube_coords = [
        (x0 + 1.5, x0 + 4.5, 47.5, 50.5), # Top-inner
        (x0 + 5.5, x0 + 8.5, 47.5, 50.5), # Top-outer
        (x0 + 1.5, x0 + 4.5, 43.5, 46.5), # Bot-inner
        (x0 + 5.5, x0 + 8.5, 43.5, 46.5), # Bot-outer
    ]
    for tx0, tx1, ty0, ty1 in tube_coords:
        cubes.append(B(tx0, tx1, ty0, ty1, -5.0, -4.0, "dark")) # Recessed tube opening
        # Missile warhead tip
        mx0, mx1 = tx0 + 0.6, tx1 - 0.6
        my0, my1 = ty0 + 0.6, ty1 - 0.6
        cubes.append(B(mx0, mx1, my0, my1, -6.0, -5.0, "steel"))
        
    # Rear exhaust deflection louvers
    cubes.append(B(x0 + 1.0, x1 - 1.0, 43.0, 51.0, 14.8, 15.5, "vent"))
    return cubes

# =========================================================================
# ASSEMBLE MODEL BONES
# =========================================================================
BONES = [
    ("titan", None, [0.0, 0.0, 0.0], []),
    
    # ---------------- Lower Chassis & Belly (body1) ----------------
    ("body1", "titan", [0.0, 24.0, 0.0], [
        # Slanted V-hull armored belly plate for blast deflection
        B(-13.0, 13.0, 20.0, 26.0, -16.0, 16.0, "dark"),
        B(-11.0, 11.0, 19.0, 21.0, -14.0, 14.0, "paint2"),
        # Transverse structural bulkheads
        B(-14.0, 14.0, 22.0, 26.0, -3.0, 3.0, "metal"),
        # 6 Coxa Hip Knuckles (3 on left, 3 on right)
        *hub(14.5, 25.0, -14.0, 3.5, 8.0, "dark"),
        *hub(-14.5, 25.0, -14.0, 3.5, 8.0, "dark"),
        *hub(15.5, 25.0, 0.0, 3.5, 8.0, "dark"),
        *hub(-15.5, 25.0, 0.0, 3.5, 8.0, "dark"),
        *hub(14.5, 25.0, 14.0, 3.5, 8.0, "dark"),
        *hub(-14.5, 25.0, 14.0, 3.5, 8.0, "dark"),
    ]),
    
    # ---------------- Mid Chassis & Sponsons (body2) ----------------
    ("body2", "body1", [0.0, 28.0, 0.0], [
        # Central armored core
        B(-13.0, 13.0, 26.0, 34.0, -16.0, 16.0, "paint", decal={"south": "bullant"}),
        # Left armored sponson & side intake vent
        B(13.0, 16.0, 26.0, 33.0, -14.0, 14.0, "paint2"),
        B(16.0, 16.5, 27.5, 32.0, -7.0, 7.0, "vent"),
        # Right armored sponson & side intake vent
        B(-16.0, -13.0, 26.0, 33.0, -14.0, 14.0, "paint2"),
        B(-16.5, -16.0, 27.5, 32.0, -7.0, 7.0, "vent"),
        # Rear engine compartment & twin exhausts
        B(-10.0, 10.0, 26.0, 35.0, 16.0, 20.0, "dark"),
        B(5.0, 9.0, 30.0, 34.0, 20.0, 22.5, "metal"),
        B(-9.0, -5.0, 30.0, 34.0, 20.0, 22.5, "metal"),
    ]),
    
    # ---------------- Upper Carapace & Dorsal Deck (body3) ----------------
    ("body3", "body2", [0.0, 34.0, 0.0], [
        # Sloped dorsal armor shell
        B(-12.0, 12.0, 34.0, 40.0, -14.0, 15.0, "paint"),
        B(-5.0, 5.0, 40.0, 42.0, -12.0, 13.0, "paint2"),
        # Radiator cooling louvers on engine deck
        B(-8.0, 8.0, 40.1, 40.9, 4.0, 13.0, "vent"),
        # Towing shackles on rear
        B(7.0, 9.5, 35.0, 38.0, 19.5, 21.0, "metal"),
        B(-9.5, -7.0, 35.0, 38.0, 19.5, 21.0, "metal"),
        # Dorsal missile pod mounting gantry & crossbeam
        B(-6.0, 6.0, 40.0, 44.0, 1.0, 7.0, "dark"),
        B(-14.0, 14.0, 43.0, 46.0, 3.0, 6.0, "metal"),
        # Dual 4-Tube Anti-Tank Missile Pods (Bullant Signature!)
        *build_missile_pod(is_left=True),
        *build_missile_pod(is_left=False),

        # === MANNED PILOT COCKPIT & ARMORED ENTRY HATCH ===
        # Elevated Armored Cupola Ring / Cockpit Collar
        B(-6.5, 6.5, 40.0, 42.5, -11.5, -0.5, "dark"),
        # Heavy Armored Clamshell Pilot Hatch Lid (chamfered edges)
        B(-6.0, 6.0, 42.5, 44.2, -11.0, -1.0, "paint2"),
        B(-5.0, 5.0, 44.2, 45.0, -10.0, -2.0, "paint"),
        # Heavy Dual Rear Hatch Hinges
        B(3.5, 5.5, 43.0, 45.2, -1.5, 0.5, "steel"),
        B(-5.5, -3.5, 43.0, 45.2, -1.5, 0.5, "steel"),
        # Forward Armored Periscope Vision Block (Glowing Cyan Optics)
        B(-3.5, 3.5, 43.2, 44.8, -11.8, -10.5, "steel"),
        B(-2.8, 2.8, 43.5, 44.5, -12.2, -11.5, "visor"),
        # Dual Pilot Boarding / Crew Access Handles
        B(6.6, 7.4, 41.5, 43.5, -9.0, -3.0, "metal"),
        B(-7.4, -6.6, 41.5, 43.5, -9.0, -3.0, "metal"),
    ]),
    
    # ---------------- Cockpit Canopy / Armored Nose (doorUp) ----------------
    ("doorUp", "body3", [0.0, 36.0, -12.0], [
        # Forward angled snout wedge armor
        B(-8.0, 8.0, 34.0, 40.0, -24.0, -13.0, "paint"),
        # Front nose bevel plate
        B(-6.0, 6.0, 31.0, 36.0, -27.0, -23.0, "paint2"),
        # Recessed periscope sight slit
        B(-4.0, 4.0, 36.5, 38.0, -24.6, -23.8, "visor"),
        # Left & Right cheek cowlings
        B(7.5, 10.0, 32.0, 38.0, -22.0, -14.0, "paint2"),
        B(-10.0, -7.5, 32.0, 38.0, -22.0, -14.0, "paint2"),
    ]),
    
    # ---------------- Armored Chin & Chin Autocannons (doorDown) ----------------
    ("doorDown", "body3", [0.0, 27.0, -14.0], [
        # Lower chin armor plate
        B(-7.0, 7.0, 24.0, 30.0, -25.0, -14.0, "dark"),
        # Chin gun cradle
        B(-6.0, 6.0, 26.0, 29.0, -27.0, -24.0, "metal"),
        # Dual forward chin autocannon barrels
        B(2.8, 4.4, 26.5, 28.1, -33.0, -26.0, "steel"),
        B(2.4, 4.8, 26.0, 28.6, -35.0, -33.0, "dark"), # left muzzle compensator
        B(-4.4, -2.8, 26.5, 28.1, -33.0, -26.0, "steel"),
        B(-4.8, -2.4, 26.0, 28.6, -35.0, -33.0, "dark"), # right muzzle compensator
    ]),
    
    # ---------------- Canopus 360 Camera Dome (eye) ----------------
    ("eye", "body3", [0.0, 41.0, -7.0], [
        B(-3.5, 3.5, 41.0, 43.0, -9.5, -4.5, "dark"),
        *ball(0.0, 45.0, -7.0, 6.0, "paint2"),
        B(-2.0, 2.0, 44.0, 46.5, -11.5, -9.5, "dark"),
        B(-1.4, 1.4, 44.5, 46.0, -12.2, -11.4, "visor"), # Glowing cyan lens aperture
    ]),
    
    # ---------------- Arms & Weapon Hardpoints ----------------
    ("rightArm1", "body3", [-16.0, 33.0, -3.0], [
        B(-19.0, -15.0, 30.0, 36.0, -6.0, 1.0, "metal"),
        *hub(-19.5, 33.0, -2.5, 2.0, 5.0, "dark")
    ]),
    ("rightArm2", "rightArm1", [-20.0, 33.0, -2.5], [
        B(-22.0, -19.0, 29.0, 35.0, -5.0, 2.0, "paint2")
    ]),
    ("rightHand", "rightArm2", [-21.0, 31.0, -2.0], [
        B(-23.0, -19.0, 28.0, 33.0, -4.0, 2.0, "dark")
    ]),
    ("weapon", "rightHand", [-21.0, 31.0, -2.0], []),
    
    ("leftArm1", "body3", [16.0, 33.0, -3.0], mirror([
        B(-19.0, -15.0, 30.0, 36.0, -6.0, 1.0, "metal"),
        *hub(-19.5, 33.0, -2.5, 2.0, 5.0, "dark")
    ])),
    ("leftArm2", "leftArm1", [20.0, 33.0, -2.5], mirror([
        B(-22.0, -19.0, 29.0, 35.0, -5.0, 2.0, "paint2")
    ])),
    ("leftHand", "leftArm2", [21.0, 31.0, -2.0], mirror([
        B(-23.0, -19.0, 28.0, 33.0, -4.0, 2.0, "dark")
    ])),
    
    # Stowed & back weapon hardpoints
    ("weaponBack", "body3", [-18.0, 36.0, 8.0], [
        B(-21.0, -17.0, 33.0, 39.0, 6.0, 11.0, "metal")
    ]),
    ("artillery", "body3", [-18.0, 36.0, 8.0], []),
    ("artilleryTurret", "artillery", [-18.0, 38.0, 8.0], []),
    ("artilleryBarrel", "artilleryTurret", [-18.0, 40.0, 8.0], []),
    ("back_rocket_pod", "body3", [-18.0, 38.0, 8.0], []),
    ("stowed_rifle", "weaponBack", [-18.0, 36.0, 8.0], []),
    ("stowed_machine_gun", "weaponBack", [-18.0, 36.0, 8.0], []),
    ("stowed_rocket_launcher", "weaponBack", [-18.0, 36.0, 8.0], []),
    
    # ---------------- 6 HEXAPOD LEGS ----------------
    # 1. Front-Left Leg (Z = -14)
    ("leftLeg3", "titan", [14.5, 25.0, -14.0], leg_thigh_cubes(+1, -14.0)),
    ("leftLeg2", "leftLeg3", [28.0, 34.0, -16.0], leg_knee_cubes(+1, -16.0)),
    ("leftLeg1", "leftLeg2", [28.0, 34.0, -16.0], leg_shin_cubes(+1, -16.0)),
    ("leftFoot", "leftLeg1", [36.0, 6.0, -20.0], leg_foot_cubes(+1, -20.0)),
    
    # 2. Mid-Left Leg (Z = 0)
    ("midLeftLeg3", "titan", [15.5, 25.0, 0.0], leg_thigh_cubes(+1, 0.0)),
    ("midLeftLeg2", "midLeftLeg3", [30.0, 34.0, 0.0], leg_knee_cubes(+1, 0.0)),
    ("midLeftLeg1", "midLeftLeg2", [30.0, 34.0, 0.0], leg_shin_cubes(+1, 0.0)),
    ("midLeftFoot", "midLeftLeg1", [38.0, 6.0, 0.0], leg_foot_cubes(+1, 0.0)),
    
    # 3. Rear-Left Leg (Z = +14)
    ("rearLeftLeg3", "titan", [14.5, 25.0, 14.0], leg_thigh_cubes(+1, 14.0)),
    ("rearLeftLeg2", "rearLeftLeg3", [28.0, 34.0, 16.0], leg_knee_cubes(+1, 16.0)),
    ("rearLeftLeg1", "rearLeftLeg2", [28.0, 34.0, 16.0], leg_shin_cubes(+1, 16.0)),
    ("rearLeftFoot", "rearLeftLeg1", [36.0, 6.0, 20.0], leg_foot_cubes(+1, 20.0)),
    
    # 4. Front-Right Leg (Z = -14)
    ("rightLeg3", "titan", [-14.5, 25.0, -14.0], leg_thigh_cubes(-1, -14.0)),
    ("rightLeg2", "rightLeg3", [-28.0, 34.0, -16.0], leg_knee_cubes(-1, -16.0)),
    ("rightLeg1", "rightLeg2", [-28.0, 34.0, -16.0], leg_shin_cubes(-1, -16.0)),
    ("rightFoot", "rightLeg1", [-36.0, 6.0, -20.0], leg_foot_cubes(-1, -20.0)),
    
    # 5. Mid-Right Leg (Z = 0)
    ("midRightLeg3", "titan", [-15.5, 25.0, 0.0], leg_thigh_cubes(-1, 0.0)),
    ("midRightLeg2", "midRightLeg3", [-30.0, 34.0, 0.0], leg_knee_cubes(-1, 0.0)),
    ("midRightLeg1", "midRightLeg2", [-30.0, 34.0, 0.0], leg_shin_cubes(-1, 0.0)),
    ("midRightFoot", "midRightLeg1", [-38.0, 6.0, 0.0], leg_foot_cubes(-1, 0.0)),
    
    # 6. Rear-Right Leg (Z = +14)
    ("rearRightLeg3", "titan", [-14.5, 25.0, 14.0], leg_thigh_cubes(-1, 14.0)),
    ("rearRightLeg2", "rearRightLeg3", [-28.0, 34.0, 16.0], leg_knee_cubes(-1, 16.0)),
    ("rearRightLeg1", "rearRightLeg2", [-28.0, 34.0, 16.0], leg_shin_cubes(-1, 16.0)),
    ("rearRightFoot", "rearRightLeg1", [-36.0, 6.0, 20.0], leg_foot_cubes(-1, 20.0)),
    
    # ---------------- Modular Armor Bones ----------------
    ("armor_head", "doorUp", [0.0, 37.0, -16.0], [
        B(-8.5, 8.5, 36.0, 41.5, -24.5, -14.5, "paint2"),
    ]),
    ("armor_chest", "body3", [0.0, 36.0, 0.0], [
        B(-13.0, 13.0, 35.0, 41.0, -13.0, 12.0, "paint2"),
    ]),
    ("armor_left_arm", "leftArm1", [16.0, 33.0, -3.0], [
        B(16.0, 22.0, 28.0, 37.0, -8.0, 3.0, "paint2"),
    ]),
    ("armor_right_arm", "rightArm1", [-16.0, 33.0, -3.0], [
        B(-22.0, -16.0, 28.0, 37.0, -8.0, 3.0, "paint2"),
    ]),
    ("armor_left_leg", "leftLeg2", [28.0, 34.0, -16.0], [
        B(26.0, 32.0, 26.0, 37.0, -20.0, -12.0, "paint2"),
    ]),
    ("armor_right_leg", "rightLeg2", [-28.0, 34.0, -16.0], [
        B(-32.0, -26.0, 26.0, 37.0, -20.0, -12.0, "paint2"),
    ]),
]

# =========================================================================
# UV PACKING
# =========================================================================
def pack():
    x, y, row = 2, 2, 0
    placed = []
    ordered = [c for _, _, _, cubes in BONES for c in cubes if not c.get("late")]
    ordered += [c for _, _, _, cubes in BONES for c in cubes if c.get("late")]
    for c in ordered:
        w, h, d = (max(1, int(round(v))) for v in c["s"])
        need_w, need_h = 2 * (d + w) + 2, d + h + 2
        if x + need_w > TEX:
            x, y, row = 2, y + row, 0
        c["uv"], c["dims"] = [x, y], (w, h, d)
        x += need_w
        row = max(row, need_h)
        placed.append(c)
    assert y + row <= TEX, f"Texture atlas overflow: y={y}, row={row}, total={y+row} > {TEX}"
    print(f"Packed {len(placed)} cubes. Max Y: {y + row} / {TEX}")
    return placed

def faces(c):
    u, v = c["uv"]
    w, h, d = c["dims"]
    return {
        "up": (u + d, v, w, d),
        "down": (u + d + w, v, w, d),
        "east": (u, v + d, d, h),
        "north": (u + d, v + d, w, h),
        "west": (u + d + w, v + d, d, h),
        "south": (u + 2 * d + w, v + d, w, h)
    }

def generate_geo_json():
    bones_out = []
    for name, parent, piv, cubes in BONES:
        b = {"name": name, "pivot": [round(float(v) * SCALE, 3) for v in piv]}
        if parent:
            b["parent"] = parent
        if cubes:
            c_list = []
            for c in cubes:
                entry = {
                    "origin": [round(float(v), 3) for v in c["o"]],
                    "size": [round(float(v), 3) for v in c["s"]],
                    "uv": c["uv"]
                }
                if "rot" in c:
                    entry["pivot"] = [round(float(v), 3) for v in c["piv"]]
                    entry["rotation"] = c["rot"]
                c_list.append(entry)
            b["cubes"] = c_list
        bones_out.append(b)
        
    return {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": f"geometry.{ID}_titan",
                "texture_width": TEX,
                "texture_height": TEX,
                "visible_bounds_width": round(8 * SCALE, 2),
                "visible_bounds_height": round(6 * SCALE, 2),
                "visible_bounds_offset": [0, round(2.5 * SCALE, 2), 0]
            },
            "bones": bones_out
        }]
    }

# =========================================================================
# TEXTURE RENDERING & CAMOUFLAGE
# =========================================================================
# Palettes: (name, paint, paint2, visor)
SCHEMES = [
    # 0. Default: Authentic Military Desert Coyote Khaki (Model BULLANT)
    ("coyote",    (168, 150, 115), (124, 110, 84),  (0, 230, 255)),
    # 1. Desert Tan
    ("desert",    (186, 160, 110), (138, 116, 80),  (0, 230, 255)),
    # 2. Woodland Green
    ("woodland",  (68, 86, 52),    (48, 62, 38),    (255, 180, 50)),
    # 3. Urban Slate Gray
    ("urban",     (110, 116, 122), (74, 80, 86),    (0, 220, 255)),
    # 4. Arctic White
    ("arctic",    (205, 210, 212), (142, 148, 154), (0, 210, 255)),
    # 5. Crimson Spec-Ops
    ("crimson",   (142, 38, 36),   (88, 26, 26),    (255, 180, 50)),
    # 6. Cobalt Naval Blue
    ("cobalt",    (44, 76, 136),   (28, 48, 92),    (0, 240, 255)),
    # 7. Hazard Construction Yellow
    ("hazard",    (225, 175, 25),  (55, 55, 58),    (0, 230, 255)),
    # 8. Black Ops Stealth
    ("blackops",  (36, 38, 42),    (22, 23, 26),    (255, 50, 50)),
]

FIXED = {
    "metal": (78, 82, 86),
    "dark": (38, 40, 44),
    "steel": (168, 172, 178),
    "rust": (118, 68, 38),
    "vent": (52, 54, 58),
    "glow": (255, 214, 120),
}
YELLOW, BLACK, WHITE = (228, 182, 32), (30, 30, 30), (235, 235, 230)

def h2(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2246822519) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return (n ^ (n >> 16)) / 0xffffffff

def vnoise(x, y, scale, s):
    gx, gy = x / scale, y / scale
    x0, y0 = int(gx), int(gy)
    fx, fy = gx - x0, gy - y0
    a, b = h2(x0, y0, s), h2(x0 + 1, y0, s)
    c, d = h2(x0, y0 + 1, s), h2(x0 + 1, y0 + 1, s)
    top = a + (b - a) * fx
    bot = c + (d - c) * fx
    return top + (bot - top) * fy

def mul(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)

def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def render_texture(cubes, scheme):
    _, paint, paint2, visor = scheme
    px = bytearray(TEX * TEX * 4)

    def put(x, y, col):
        if 0 <= x < TEX and 0 <= y < TEX:
            i = (y * TEX + x) * 4
            px[i:i + 4] = bytes((col[0], col[1], col[2], 255))

    def base(mat):
        return {"paint": paint, "paint2": paint2, "visor": visor}.get(mat) or FIXED.get(mat, (90, 90, 90))

    for ci, c in enumerate(cubes):
        mat = c["m"]
        rng = random.Random(ci * 7919)
        for fname, (fx, fy, fw, fh) in faces(c).items():
            side = fname not in ("up", "down")
            for j in range(fh):
                for i in range(fw):
                    gx, gy = fx + i, fy + j
                    edge = min(i, j, fw - 1 - i, fh - 1 - j)
                    n = (h2(gx, gy, 1) - 0.5) * 0.05
                    
                    if mat == "hazard":
                        col = YELLOW if ((i + j) // 3) % 2 == 0 else BLACK
                    elif mat == "visor":
                        col = mix(visor, (230, 255, 255), 0.6) if (0 < i < fw - 1 and 0 < j < fh - 1) else visor
                        put(gx, gy, col)
                        continue
                    elif mat == "glow":
                        put(gx, gy, FIXED["glow"])
                        continue
                    elif mat == "vent":
                        col = mul(FIXED["vent"], 0.45 if (j % 2 == 0 and 0 < i < fw - 1) else 1.0)
                    elif mat == "steel":
                        col = mul(FIXED["steel"], 0.85 + 0.3 * (1 - j / max(1, fh - 1)) if side else 1.0)
                        if (i + j) % 4 == 0:
                            col = mul(col, 0.85)
                    elif mat == "rust":
                        col = mix(FIXED["rust"], (70, 40, 28), vnoise(gx, gy, 3, 5))
                    else:
                        col = base(mat)
                        if mat in ("paint", "paint2"):
                            col = mul(col, 0.92 + 0.16 * vnoise(gx, gy, 8, 2))
                            # Subtle digital camo pattern
                            v = vnoise(gx // 2, gy // 2, 3, 21)
                            if v > 0.65:
                                col = mix(col, paint2, 0.7)
                            elif v < 0.32:
                                col = mul(col, 0.75)
                                
                    col = mul(col, 1 + n)
                    
                    # Beveled edge shading and highlights
                    if edge == 0:
                        col = mul(col, 0.65) # Dark edge seam
                    elif j == 1 and side:
                        col = mul(col, 1.14) # Top light highlight
                        
                    # Rivet bolts
                    if mat in ("paint", "paint2", "metal") and fw >= 10 and fh >= 10 and i in (1, fw - 2) and j in (1, fh - 2):
                        col = (180, 184, 188)
                        
                    put(gx, gy, col)
                    
            if side:
                draw_decal(put, c.get("decal", {}).get(fname), fx, fy, fw, fh)
    return px

def draw_decal(put, kind, fx, fy, fw, fh):
    if not kind:
        return
    if kind == "hazard":
        for j in range(fh):
            for i in range(fw):
                col = YELLOW if ((i + j) // 3) % 2 == 0 else BLACK
                put(fx + i, fy + j, col)
    elif kind == "triangle_down":
        # White military downward arrow triangle: ▼
        cx = fx + fw // 2
        cy = fy + fh // 2
        for dy in range(-2, 3):
            w = max(0, 3 - (dy + 2))
            for dx in range(-w, w + 1):
                put(cx + dx, cy + dy, WHITE)
    elif kind == "bullant":
        # Military unit identification marking: "06"
        cx = fx + fw // 2
        cy = fy + fh // 2
        for dy in (-2, -1, 0, 1, 2):
            put(cx - 3, cy + dy, WHITE)
            put(cx + 3, cy + dy, WHITE)
        put(cx - 2, cy - 2, WHITE)
        put(cx - 1, cy - 2, WHITE)
        put(cx - 2, cy + 2, WHITE)
        put(cx - 1, cy + 2, WHITE)
        put(cx - 2, cy, WHITE)
        put(cx - 1, cy, WHITE)

def write_png(filepath, width, height, raw_rgba):
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0) # filter 0
        idx = y * width * 4
        raw_data.extend(raw_rgba[idx:idx + width * 4])
        
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(bytes(raw_data), level=9))
    iend = chunk(b'IEND', b'')
    with open(filepath, 'wb') as f:
        f.write(header + ihdr + idat + iend)

# =========================================================================
# ANIMATION GENERATION (Tripod Hexapod Gait)
# =========================================================================
def generate_hexapod_animation():
    base_anim_path = os.path.join(ROOT, "animations/trooper_titan.animation.json")
    with open(base_anim_path, 'r') as f:
        data = json.load(f)
        
    re_anims = {}
    for anim_name, anim_data in data.get('animations', {}).items():
        mapped_name = anim_name.replace('trooper_titan', 'spider_frame_titan')
        re_anims[mapped_name] = anim_data

    # TRIPOD WALKING GAIT:
    # Group A: leftLeg (Front-Left), midRightLeg (Mid-Right), rearLeftLeg (Rear-Left)
    # Group B: rightLeg (Front-Right), midLeftLeg (Mid-Left), rearRightLeg (Rear-Right)
    
    tripod_walk_bones = {
        # Group A - Front-Left Leg
        "leftLeg3": {
            "rotation": {
                "0.0": [-12.0, 0.0, 0.0],
                "0.25": [12.0, 0.0, 0.0],
                "0.5": [8.0, -8.0, 0.0],
                "0.75": [-16.0, 4.0, 0.0],
                "1.0": [-12.0, 0.0, 0.0]
            }
        },
        "leftLeg2": {
            "rotation": {
                "0.0": [8.0, 0.0, 0.0],
                "0.25": [-6.0, 0.0, 0.0],
                "0.5": [-16.0, 0.0, 0.0],
                "0.75": [12.0, 0.0, 0.0],
                "1.0": [8.0, 0.0, 0.0]
            }
        },
        # Group A - Mid-Right Leg
        "midRightLeg3": {
            "rotation": {
                "0.0": [-10.0, 0.0, 0.0],
                "0.25": [10.0, 0.0, 0.0],
                "0.5": [6.0, 8.0, 0.0],
                "0.75": [-14.0, -4.0, 0.0],
                "1.0": [-10.0, 0.0, 0.0]
            }
        },
        "midRightLeg2": {
            "rotation": {
                "0.0": [6.0, 0.0, 0.0],
                "0.25": [-5.0, 0.0, 0.0],
                "0.5": [-14.0, 0.0, 0.0],
                "0.75": [10.0, 0.0, 0.0],
                "1.0": [6.0, 0.0, 0.0]
            }
        },
        # Group A - Rear-Left Leg
        "rearLeftLeg3": {
            "rotation": {
                "0.0": [-12.0, 0.0, 0.0],
                "0.25": [12.0, 0.0, 0.0],
                "0.5": [8.0, -6.0, 0.0],
                "0.75": [-16.0, 4.0, 0.0],
                "1.0": [-12.0, 0.0, 0.0]
            }
        },
        "rearLeftLeg2": {
            "rotation": {
                "0.0": [8.0, 0.0, 0.0],
                "0.25": [-6.0, 0.0, 0.0],
                "0.5": [-16.0, 0.0, 0.0],
                "0.75": [12.0, 0.0, 0.0],
                "1.0": [8.0, 0.0, 0.0]
            }
        },

        # Group B - Front-Right Leg (180 deg out of phase)
        "rightLeg3": {
            "rotation": {
                "0.0": [8.0, 8.0, 0.0],
                "0.25": [-16.0, -4.0, 0.0],
                "0.5": [-12.0, 0.0, 0.0],
                "0.75": [12.0, 0.0, 0.0],
                "1.0": [8.0, 8.0, 0.0]
            }
        },
        "rightLeg2": {
            "rotation": {
                "0.0": [-16.0, 0.0, 0.0],
                "0.25": [12.0, 0.0, 0.0],
                "0.5": [8.0, 0.0, 0.0],
                "0.75": [-6.0, 0.0, 0.0],
                "1.0": [-16.0, 0.0, 0.0]
            }
        },
        # Group B - Mid-Left Leg
        "midLeftLeg3": {
            "rotation": {
                "0.0": [6.0, -8.0, 0.0],
                "0.25": [-14.0, 4.0, 0.0],
                "0.5": [-10.0, 0.0, 0.0],
                "0.75": [10.0, 0.0, 0.0],
                "1.0": [6.0, -8.0, 0.0]
            }
        },
        "midLeftLeg2": {
            "rotation": {
                "0.0": [-14.0, 0.0, 0.0],
                "0.25": [10.0, 0.0, 0.0],
                "0.5": [6.0, 0.0, 0.0],
                "0.75": [-5.0, 0.0, 0.0],
                "1.0": [-14.0, 0.0, 0.0]
            }
        },
        # Group B - Rear-Right Leg
        "rearRightLeg3": {
            "rotation": {
                "0.0": [8.0, 6.0, 0.0],
                "0.25": [-16.0, -4.0, 0.0],
                "0.5": [-12.0, 0.0, 0.0],
                "0.75": [12.0, 0.0, 0.0],
                "1.0": [8.0, 6.0, 0.0]
            }
        },
        "rearRightLeg2": {
            "rotation": {
                "0.0": [-16.0, 0.0, 0.0],
                "0.25": [12.0, 0.0, 0.0],
                "0.5": [8.0, 0.0, 0.0],
                "0.75": [-6.0, 0.0, 0.0],
                "1.0": [-16.0, 0.0, 0.0]
            }
        },
        
        # Subtle Hull Heave & Roll
        "body1": {
            "rotation": {
                "0.0": [0.8, 0.0, -1.2],
                "0.25": [-0.5, 0.0, 0.0],
                "0.5": [0.8, 0.0, 1.2],
                "0.75": [-0.5, 0.0, 0.0],
                "1.0": [0.8, 0.0, -1.2]
            }
        }
    }

    if "animation.spider_frame_titan.walk.leg" in re_anims:
        re_anims["animation.spider_frame_titan.walk.leg"]["bones"] = tripod_walk_bones
    if "animation.spider_frame_titan.move.leg" in re_anims:
        re_anims["animation.spider_frame_titan.move.leg"]["bones"] = tripod_walk_bones

    out = {"format_version": "1.8.0", "animations": re_anims}
    target_anim = os.path.join(ROOT, "animations/spider_frame_titan.animation.json")
    with open(target_anim, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"Generated animation: {target_anim}")

# =========================================================================
# MAIN EXECUTION
# =========================================================================
if __name__ == "__main__":
    packed_cubes = pack()
    geo_data = generate_geo_json()
    geo_path = os.path.join(ROOT, "geo/spider_frame_titan.geo.json")
    with open(geo_path, 'w') as f:
        json.dump(geo_data, f, indent=2)
    print(f"Generated geometry: {geo_path}")

    generate_hexapod_animation()

    tex_out_dir = os.path.join(ROOT, "textures/entity/titan/spider_frame")
    os.makedirs(tex_out_dir, exist_ok=True)

    for idx, scheme in enumerate(SCHEMES):
        fname = "spider_frame_titan.png" if idx == 0 else f"spider_frame_titan_{idx}.png"
        out_path = os.path.join(tex_out_dir, fname)
        print(f"Rendering texture ({idx}/8): {scheme[0]} -> {out_path}...")
        raw_rgba = render_texture(packed_cubes, scheme)
        write_png(out_path, TEX, TEX, raw_rgba)

    print("Model BULLANT generation complete!")
