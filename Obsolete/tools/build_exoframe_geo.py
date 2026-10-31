"""Builds high-fidelity anime-accurate exoframe.geo.json for OBSOLETE mecha mod with full faction customization."""
import json
import math
import os

OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src/main/resources/assets/obsolete/geo/exoframe.geo.json"))

# Bone hierarchy: (name, parent, pivot, uv_base)
BONES = [
    # Base skeleton (74 baseline bones)
    ("root", None, [0, 0, 0], None),
    ("pelvis", "root", [0, 18, 0], [0, 0]),
    ("pelvis_wheel", "pelvis", [0, 16.8, 3.6], [50, 0]),
    ("torso", "pelvis", [0, 20, 0], [0, 50]),
    ("upper_back_seat", "torso", [0, 25, 3.5], [80, 50]),
    ("head", "torso", [0, 32, -1], [160, 0]),

    # Head Armor Variants
    ("armor_head", "head", [0, 32, -1], [200, 0]),                   # Sand PMC
    ("armor_head_usmc", "head", [0, 32, -1], [260, 0]),              # USMC Canopy + Skull (Image 1 & 3)
    ("armor_head_dome", "head", [0, 32, -1], [330, 0]),              # Cerberus Dome (Image 2)
    ("armor_head_votoms", "head", [0, 32, -1], [400, 0]),            # VOTOMS 3-Lens Turret (Image 4)
    ("armor_head_hood", "head", [0, 32, -1], [400, 170]),            # Militia Sloped Hood Front (Image 5)

    # Chest Armor Variants
    ("armor_chest", "torso", [0, 20, 0], [200, 50]),                 # Sand PMC Chest
    ("armor_chest_usmc", "torso", [0, 20, 0], [260, 50]),            # USMC Chest with Grab Tubes (Image 1 & 3)
    ("armor_chest_cerberus", "torso", [0, 20, 0], [330, 50]),        # Cerberus Angular Chest (Image 2)
    ("armor_chest_hood", "torso", [0, 20, 0], [400, 220]),           # Militia Cockpit Turtle Shell (Image 5)
    ("armor_roll_cage", "torso", [0, 20, 0], [0, 240]),              # Industrial Roll Cage

    # Backpacks & Utility Modules
    ("backpack_cargo", "torso", [0, 24, 8], [80, 240]),              # Cargo Crate
    ("backpack_ammo", "torso", [0, 24, 8], [140, 240]),              # Ammo Canister
    ("backpack_usmc", "torso", [0, 24, 8], [260, 220]),              # USMC Twin Comms + Antennas (Image 1 & 3)
    ("backpack_cerberus", "torso", [0, 24, 8], [330, 220]),          # Cerberus Twin Tactical Packs (Image 2)
    ("backpack_missile_pod", "torso", [0, 32, 2], [400, 100]),       # VOTOMS 9-Tube Shoulder Pod (Image 4)

    # Left Arm & Shoulders
    ("left_arm", "torso", [7.0, 30, -0.5], [0, 130]),
    ("armor_left_shoulder", "left_arm", [7.0, 30, -0.5], [200, 120]),            # Sand
    ("armor_left_shoulder_usmc", "left_arm", [7.0, 30, -0.5], [260, 120]),       # USMC
    ("armor_left_shoulder_cerberus", "left_arm", [7.0, 30, -0.5], [330, 120]),   # Cerberus
    ("left_forearm", "left_arm", [7.0, 24.6, -0.5], [50, 130]),
    ("left_hand", "left_forearm", [7.0, 17.6, -0.5], [90, 130]),

    # Right Arm & Shoulders
    ("right_arm", "torso", [-7.0, 30, -0.5], [0, 130]),
    ("armor_right_shoulder", "right_arm", [-7.0, 30, -0.5], [200, 120]),          # Sand
    ("armor_right_shoulder_usmc", "right_arm", [-7.0, 30, -0.5], [260, 120]),     # USMC
    ("armor_right_shoulder_cerberus", "right_arm", [-7.0, 30, -0.5], [330, 120]), # Cerberus
    ("armor_right_shoulder_red", "right_arm", [-7.0, 30, -0.5], [400, 50]),       # VOTOMS Blood Red Shoulder (Image 4)
    ("right_forearm", "right_arm", [-7.0, 24.6, -0.5], [50, 130]),
    ("right_hand", "right_forearm", [-7.0, 17.6, -0.5], [90, 130]),
    ("right_hand_weapon_mount", "right_hand", [-7.0, 16.0, -2.0], None),

    # Weapons & Industrial Tools (mount at right_hand_weapon_mount)
    ("weapon_assault_rifle", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [0, 320]),
    ("weapon_sniper_amr", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [80, 320]),       # USMC 20mm AMR (Image 1)
    ("weapon_machine_gun", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [180, 320]),     # 12.7mm HMG with belt (Image 2 & 4)
    ("weapon_minigun_m134", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [280, 320]),    # M134 Gatling (Image 4)
    ("weapon_rocket_launcher", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [0, 400]),   # Quad AT Missile Pod
    ("weapon_rpg7_heavy", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [120, 400]),      # Demolition Warhead (Image 5)
    ("tool_mining_drill", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [240, 400]),
    ("tool_chainsaw", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [360, 400]),

    # Left Leg & Armor
    ("left_thigh", "pelvis", [4.5, 17, 0], [0, 180]),
    ("armor_left_leg", "left_thigh", [4.5, 17, 0], [200, 170]),                  # Sand
    ("armor_left_leg_usmc", "left_thigh", [4.5, 17, 0], [260, 170]),             # USMC Vented (Image 1 & 3)
    ("armor_left_leg_cerberus", "left_thigh", [4.5, 17, 0], [330, 170]),         # Cerberus Apron (Image 2)
    ("left_shin", "left_thigh", [4.5, 9, -2.8], [50, 180]),
    ("left_knee_wheel", "left_shin", [6.8, 9, -2.5], [90, 180]),
    ("left_foot", "left_shin", [4.5, 2, 2.2], [130, 180]),

    # Right Leg & Armor
    ("right_thigh", "pelvis", [-4.5, 17, 0], [0, 180]),
    ("armor_right_leg", "right_thigh", [-4.5, 17, 0], [200, 170]),                # Sand
    ("armor_right_leg_usmc", "right_thigh", [-4.5, 17, 0], [260, 170]),           # USMC Vented
    ("armor_right_leg_cerberus", "right_thigh", [-4.5, 17, 0], [330, 170]),       # Cerberus Apron
    ("right_shin", "right_thigh", [-4.5, 9, -2.8], [50, 180]),
    ("right_knee_wheel", "right_shin", [-6.8, 9, -2.5], [90, 180]),
    ("right_foot", "right_shin", [-4.5, 2, 2.2], [130, 180]),

    # Polar Front & Outlander sets
    ("armor_head_polar", "head", [0, 32, -1], [462, 0]),
    ("armor_chest_polar", "torso", [0, 20, 0], [462, 30]),
    ("backpack_manpads", "torso", [0, 32, 2], [200, 240]),
    ("armor_left_shoulder_polar", "left_arm", [7.0, 30, -0.5], [462, 70]),
    ("armor_right_shoulder_polar", "right_arm", [-7.0, 30, -0.5], [462, 70]),
    ("armor_left_shoulder_outlander", "left_arm", [7.0, 30, -0.5], [430, 170]),
    ("armor_right_shoulder_outlander", "right_arm", [-7.0, 30, -0.5], [430, 170]),
    ("armor_left_leg_polar", "left_thigh", [4.5, 17, 0], [462, 100]),
    ("armor_right_leg_polar", "right_thigh", [-4.5, 17, 0], [462, 100]),
    ("armor_left_leg_outlander", "left_thigh", [4.5, 17, 0], [430, 240]),
    ("armor_right_leg_outlander", "right_thigh", [-4.5, 17, 0], [430, 240]),

    # Pilot capsules
    ("canopy_usmc", "torso", [0, 20, 0], [260, 50]),
    ("canopy_cerberus", "torso", [0, 20, 0], [330, 50]),
    ("canopy_polar", "torso", [0, 20, 0], [462, 30]),
    ("canopy_hood", "torso", [0, 20, 0], [400, 220]),

    # Shin greaves
    ("armor_left_shin_sand", "left_shin", [4.5, 9, -2.8], [200, 0]),
    ("armor_right_shin_sand", "right_shin", [-4.5, 9, -2.8], [200, 0]),
    ("armor_left_shin_usmc", "left_shin", [4.5, 9, -2.8], [260, 0]),
    ("armor_right_shin_usmc", "right_shin", [-4.5, 9, -2.8], [260, 0]),
    ("armor_left_shin_cerberus", "left_shin", [4.5, 9, -2.8], [330, 0]),
    ("armor_right_shin_cerberus", "right_shin", [-4.5, 9, -2.8], [330, 0]),
    ("armor_left_shin_polar", "left_shin", [4.5, 9, -2.8], [462, 0]),
    ("armor_right_shin_polar", "right_shin", [-4.5, 9, -2.8], [462, 0]),
    ("armor_left_shin_outlander", "left_shin", [4.5, 9, -2.8], [400, 0]),
    ("armor_right_shin_outlander", "right_shin", [-4.5, 9, -2.8], [400, 0]),
    ("armor_left_ski", "left_foot", [4.5, 2, 2.2], [462, 130]),
    ("armor_right_ski", "right_foot", [-4.5, 2, 2.2], [462, 130]),

    # ==================== 6 NEW COMPLETE FACTION ARMOR SETS ====================
    # 1. Salvage Militia (Tekketsu scrap militia)
    ("armor_head_salvage", "head", [0, 32, -1], [512, 0]),
    ("armor_chest_salvage", "torso", [0, 20, 0], [512, 30]),
    ("canopy_salvage", "torso", [0, 20, 0], [512, 30]),
    ("armor_left_shoulder_salvage", "left_arm", [7.0, 30, -0.5], [512, 80]),
    ("armor_right_shoulder_salvage", "right_arm", [-7.0, 30, -0.5], [512, 80]),
    ("armor_left_leg_salvage", "left_thigh", [4.5, 17, 0], [512, 120]),
    ("armor_right_leg_salvage", "right_thigh", [-4.5, 17, 0], [512, 120]),
    ("armor_left_shin_salvage", "left_shin", [4.5, 9, -2.8], [512, 0]),
    ("armor_right_shin_salvage", "right_shin", [-4.5, 9, -2.8], [512, 0]),
    ("backpack_salvage", "torso", [0, 24, 8], [512, 160]),

    # 2. Shiden Corps (East-Asian Heavy Corps)
    ("armor_head_shiden", "head", [0, 32, -1], [597, 0]),
    ("armor_chest_shiden", "torso", [0, 20, 0], [597, 30]),
    ("canopy_shiden", "torso", [0, 20, 0], [597, 30]),
    ("armor_left_shoulder_shiden", "left_arm", [7.0, 30, -0.5], [597, 80]),
    ("armor_right_shoulder_shiden", "right_arm", [-7.0, 30, -0.5], [597, 80]),
    ("armor_left_leg_shiden", "left_thigh", [4.5, 17, 0], [597, 120]),
    ("armor_right_leg_shiden", "right_thigh", [-4.5, 17, 0], [597, 120]),
    ("armor_left_shin_shiden", "left_shin", [4.5, 9, -2.8], [597, 0]),
    ("armor_right_shin_shiden", "right_shin", [-4.5, 9, -2.8], [597, 0]),
    ("backpack_shiden", "torso", [0, 24, 8], [597, 160]),

    # 3. Khamsin Guard (Desert Long-Range Guard)
    ("armor_head_khamsin", "head", [0, 32, -1], [682, 0]),
    ("armor_chest_khamsin", "torso", [0, 20, 0], [682, 30]),
    ("canopy_khamsin", "torso", [0, 20, 0], [682, 30]),
    ("armor_left_shoulder_khamsin", "left_arm", [7.0, 30, -0.5], [682, 80]),
    ("armor_right_shoulder_khamsin", "right_arm", [-7.0, 30, -0.5], [682, 80]),
    ("armor_left_leg_khamsin", "left_thigh", [4.5, 17, 0], [682, 120]),
    ("armor_right_leg_khamsin", "right_thigh", [-4.5, 17, 0], [682, 120]),
    ("armor_left_shin_khamsin", "left_shin", [4.5, 9, -2.8], [682, 0]),
    ("armor_right_shin_khamsin", "right_shin", [-4.5, 9, -2.8], [682, 0]),
    ("backpack_khamsin", "torso", [0, 24, 8], [682, 160]),

    # 4. Riverine Recon (Jungle / Amphibious Riverine)
    ("armor_head_riverine", "head", [0, 32, -1], [767, 0]),
    ("armor_chest_riverine", "torso", [0, 20, 0], [767, 30]),
    ("canopy_riverine", "torso", [0, 20, 0], [767, 30]),
    ("armor_left_shoulder_riverine", "left_arm", [7.0, 30, -0.5], [767, 80]),
    ("armor_right_shoulder_riverine", "right_arm", [-7.0, 30, -0.5], [767, 80]),
    ("armor_left_leg_riverine", "left_thigh", [4.5, 17, 0], [767, 120]),
    ("armor_right_leg_riverine", "right_thigh", [-4.5, 17, 0], [767, 120]),
    ("armor_left_shin_riverine", "left_shin", [4.5, 9, -2.8], [767, 0]),
    ("armor_right_shin_riverine", "right_shin", [-4.5, 9, -2.8], [767, 0]),
    ("backpack_riverine", "torso", [0, 24, 8], [767, 160]),

    # 5. Specter PMC (Stealth Black-Ops)
    ("armor_head_specter", "head", [0, 32, -1], [852, 0]),
    ("armor_chest_specter", "torso", [0, 20, 0], [852, 30]),
    ("canopy_specter", "torso", [0, 20, 0], [852, 30]),
    ("armor_left_shoulder_specter", "left_arm", [7.0, 30, -0.5], [852, 80]),
    ("armor_right_shoulder_specter", "right_arm", [-7.0, 30, -0.5], [852, 80]),
    ("armor_left_leg_specter", "left_thigh", [4.5, 17, 0], [852, 120]),
    ("armor_right_leg_specter", "right_thigh", [-4.5, 17, 0], [852, 120]),
    ("armor_left_shin_specter", "left_shin", [4.5, 9, -2.8], [852, 0]),
    ("armor_right_shin_specter", "right_shin", [-4.5, 9, -2.8], [852, 0]),
    ("backpack_specter", "torso", [0, 24, 8], [852, 160]),

    # 6. Valkyrie Guard (Elite Spherical Capsule)
    ("armor_head_valkyrie", "head", [0, 32, -1], [937, 0]),
    ("armor_chest_valkyrie", "torso", [0, 20, 0], [937, 30]),
    ("canopy_valkyrie", "torso", [0, 20, 0], [937, 30]),
    ("armor_left_shoulder_valkyrie", "left_arm", [7.0, 30, -0.5], [937, 80]),
    ("armor_right_shoulder_valkyrie", "right_arm", [-7.0, 30, -0.5], [937, 80]),
    ("armor_left_leg_valkyrie", "left_thigh", [4.5, 17, 0], [937, 120]),
    ("armor_right_leg_valkyrie", "right_thigh", [-4.5, 17, 0], [937, 120]),
    ("armor_left_shin_valkyrie", "left_shin", [4.5, 9, -2.8], [937, 0]),
    ("armor_right_shin_valkyrie", "right_shin", [-4.5, 9, -2.8], [937, 0]),
    ("backpack_valkyrie", "torso", [0, 24, 8], [937, 160]),

    # ==================== 8 NEW WEAPONS ====================
    ("weapon_battle_rifle", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [0, 520]),
    ("weapon_autocannon_30mm", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [120, 520]),
    ("weapon_shotgun_breacher", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [240, 520]),
    ("weapon_grenade_launcher", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [360, 520]),
    ("weapon_recoilless_rifle", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [480, 520]),
    ("weapon_atgm_guided", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [600, 520]),
    ("weapon_flamethrower", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [720, 520]),
    ("weapon_vibro_blade", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [840, 520]),

    # ==================== ROLE VARIANTS ====================
    # 1. Riot Police
    ("armor_head_police", "head", [0, 32, -1], [0, 660]),
    ("canopy_police", "torso", [0, 20, 0], [0, 660]),
    ("armor_chest_police", "torso", [0, 20, 0], [0, 660]),
    ("weapon_riot_shield", "left_hand", [7.0, 17.6, -0.5], [0, 840]),
    ("weapon_stun_baton", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [120, 840]),
    # 2. Disaster Rescue NGO
    ("armor_head_rescue", "head", [0, 32, -1], [250, 660]),
    ("canopy_rescue", "torso", [0, 20, 0], [250, 660]),
    ("armor_chest_rescue", "torso", [0, 20, 0], [250, 660]),
    ("backpack_rescue", "torso", [0, 24, 8], [250, 660]),
    # 3. Amphibious Assault
    ("armor_float_ring", "pelvis", [0, 17, 0], [500, 660]),
    # 5. Radar Scout
    ("backpack_radar", "torso", [0, 24, 8], [750, 660]),
    # 6. Harbour Fishing Rod
    ("weapon_fishing_rod", "right_hand_weapon_mount", [-7.0, 16.0, -2.0], [240, 840]),
]

C = {}

def add(bone, *boxes):
    C.setdefault(bone, []).extend(boxes)

def sym(bone, *boxes):
    for b in boxes:
        add(bone, b, mx(b))

def mx(b):
    x, y, z, sx, sy, sz = b
    return (-(x + sx), y, z, sx, sy, sz)

def disc_x(x, cy, cz, r, w):
    k = 0.83 * r
    return [
        (x, cy - r, cz - k / 2, w, 2 * r, k),
        (x, cy - k / 2, cz - r, w, k, 2 * r),
        (x, cy - 0.71 * r, cz - 0.71 * r, w, 1.42 * r, 1.42 * r)
    ]

def disc_z(cx, cy, z, r, d):
    k = 0.83 * r
    return [
        (cx - r, cy - k / 2, z, 2 * r, k, d),
        (cx - k / 2, cy - r, z, k, 2 * r, d),
        (cx - 0.71 * r, cy - 0.71 * r, z, 1.42 * r, 1.42 * r, d)
    ]

def ring_x(x, cy, cz, r, w, n=12, s=0.7):
    return [(x, cy + r * math.sin(a) - s / 2, cz + r * math.cos(a) - s / 2, w, s, s)
            for a in (2 * math.pi * i / n for i in range(n))]

def piston_y(x, y0, y1, z, t=1.0):
    mid = (y0 + y1) / 2
    r = t * 0.5
    return [
        (x, mid, z, t, y1 - mid, t),
        (x + t / 2 - r / 2, y0, z + t / 2 - r / 2, r, mid - y0, r),
        (x - 0.1, y1 - 0.4, z - 0.1, t + 0.2, 0.4, t + 0.2),
        (x - 0.1, y0, z - 0.1, t + 0.2, 0.4, t + 0.2)
    ]

def stepped(x, y_top, z_top, y_bot, z_bot, sx, sz, n):
    out, dy = [], (y_top - y_bot) / n
    for i in range(n):
        y = y_top - dy * (i + 1)
        z = z_top + (z_bot - z_top) * (i + 0.5) / n
        out.append((x, y, z - sz / 2, sx, dy + 0.3, sz))
    return out

# ==================== 1. BASE SKELETON ====================
p = "pelvis"
# Pelvis central motor drum:
# Hip width = 9.0 (thighs at ±4.5).
# Target drum diameter ≈ 0.5 * 9.0 = 4.5 (radius r = 2.25). Axis left-right (X axis).
# Width = 4.4 (from x = -2.2 to +2.2). Visible radial ribs along circumference.
add(p,
    *disc_x(-2.2, 16.8, 0.0, 2.25, 4.4),                       # Main central motor/battery drum cylinder (diam 4.5 = 0.50x hip)
    *ring_x(-2.25, 16.8, 0.0, 2.35, 4.5, n=12, s=0.45),        # 12 cooling / structural radial ribs
    (-2.2, 16.5, -2.4, 4.4, 0.6, 4.8),                         # Drum perimeter reinforcement rail
    (-1.8, 19.4, -1.0, 3.6, 0.6, 4.2),                         # Open tubular seat base cradle
    (-1.4, 19.8, 0.2, 2.8, 0.5, 3.2))                          # Pilot saddle deck
sym(p,
    *disc_x(2.3, 17.0, 0.0, 1.8, 1.2),                         # Hip joint knuckle housings connecting to thighs
    (2.2, 16.2, -1.6, 1.1, 1.6, 3.2),                         # Hip mount bracket
    (1.7, 18.8, -1.2, 0.6, 0.6, 4.8),                         # Side seat cradle tube
    (1.7, 16.8, 3.2, 0.6, 2.6, 0.6),                          # Rear vertical seat support truss
    (1.7, 16.0, -1.4, 0.8, 0.8, 0.8))

w = "pelvis_wheel"
# Secondary generator spindle / lower auxiliary drive
add(w, *disc_x(-1.1, 16.8, 3.6, 1.35, 2.2),
    *ring_x(-1.15, 16.8, 3.6, 1.45, 2.3, n=8, s=0.35),
    (-1.3, 16.5, 3.3, 2.6, 0.6, 0.6))

t = "torso"
# Torso: Slender exposed spine and neck column from yoke down to pelvis.
# NO big chest block on the bare frame! Front is open frame.
# Vertebrae column:
for y in (20.0, 21.8, 23.6, 25.4, 27.2):
    add(t, (-0.9, y, -0.6, 1.8, 1.2, 1.6),                     # Articulated vertebra segment
           (-0.6, y + 1.2, -0.4, 1.2, 0.6, 1.2))                # Intervertebral shock-absorber pad
add(t,
    (-0.4, 20.0, 1.0, 0.8, 9.6, 0.6),                          # Rear spine runner / cable conduit
    (-0.7, 28.4, -4.2, 1.4, 1.2, 3.6),                         # Slender forward neck boom to sensor head mount
    (-1.2, 25.0, 1.2, 2.4, 0.8, 3.6),                          # Seat back cradle lower
    (-1.8, 25.8, 0.6, 3.6, 1.2, 4.2),                          # Seat back cradle upper
    # Arched Shoulder Yoke (one wide arched bar over top, outer span 14.4 = 1.60x hip 9.0!)
    (-2.0, 32.4, -0.8, 4.0, 1.4, 1.8),                         # Center peak of upward arch (y reaches 33.8 - highest point!)
    (-0.8, 30.6, -1.2, 1.6, 1.8, 1.6))                         # Center keel collar
sym(t,
    (1.8, 31.4, -0.8, 2.8, 1.4, 1.8),                          # Mid arch section rising from shoulders
    (4.9, 30.4, -0.8, 1.5, 1.6, 1.8),                          # Shoulder bracket
    (6.4, 29.3, -0.9, 0.8, 1.8, 2.0),                          # Outermost shoulder yoke cap (outer X = 7.2 -> outer span 14.4!)
    *piston_y(1.2, 20.4, 28.0, -0.4, 0.6),                     # Spine lateral hydraulic dampers
    (1.4, 21.6, 1.2, 0.6, 5.4, 0.6),                           # Seat back diagonal truss
    (2.6, 26.6, 4.8, 0.6, 2.8, 0.6))

s = "upper_back_seat"
# Pilot upper seat back & harness frame
add(s, (-2.4, 34.0, 1.4, 4.8, 1.2, 5.0),
    (-2.0, 35.2, 1.8, 4.0, 0.6, 4.4),
    (-2.4, 34.0, 6.2, 4.8, 5.6, 0.8),
    (-2.0, 35.8, 5.8, 4.0, 4.0, 0.4))
sym(s, (2.4, 34.8, 1.6, 0.5, 1.0, 4.6),
    (1.1, 36.0, 5.6, 0.6, 3.6, 0.3),
    (3.8, 34.2, -1.2, 0.6, 0.6, 2.6))

h = "head"
# Bare frame head has 0 cubes (empty transform on bare frame; highest point is arched shoulder yoke!)
# Sensors come from head armor pieces (armor_head, armor_head_usmc, etc.)

# ==================== 2. HEAD ARMOR VARIANTS ====================
# A. Sand Head
a = "armor_head"
# Sand PMC Head Sensor & Optics
add(a, (-2.2, 31.0, -5.0, 4.4, 3.2, 4.0),
    (-1.8, 34.2, -4.4, 3.6, 0.4, 3.2),
    (-1.4, 31.4, -5.4, 2.8, 2.4, 0.4),
    *disc_z(0, 32.6, -5.8, 0.9, 0.4),
    (-0.5, 32.1, -6.0, 1.0, 1.0, 0.2),
    (0.9, 31.5, -5.6, 0.4, 0.4, 0.2),
    (-1.0, 30.4, -1.6, 2.0, 1.0, 1.2),
    (-2.4, 33.4, -1.6, 0.5, 0.8, 0.5),
    (-2.3, 34.2, -1.5, 0.3, 8.0, 0.3),
    (-2.7, 34.2, -5.4, 5.4, 0.5, 4.6),
    (-2.2, 34.7, -4.8, 4.4, 0.3, 3.4),
    (-2.7, 33.8, -5.8, 5.4, 0.5, 0.5))
sym(a, (2.2, 31.0, -5.4, 0.5, 3.2, 4.6),
    (1.6, 31.0, -5.8, 0.6, 1.0, 0.5),
    (2.7, 32.2, -4.2, 0.2, 0.4, 2.6))

# D. VOTOMS 3-Lens Turret Optic Camera
a = "armor_head_votoms"
add(a, (-2.6, 31.2, -5.2, 5.2, 3.4, 4.4),          # Turret head block
    (-2.2, 34.6, -4.8, 4.4, 0.6, 3.8),             # Turret brow
    *disc_z(0, 33.0, -5.8, 1.8, 0.6),              # Revolving turret disk
    *disc_z(0.6, 33.6, -6.4, 0.8, 0.8),            # Main standard optic (large green)
    *disc_z(-0.7, 33.8, -6.3, 0.5, 0.7),           # Wide-angle auxiliary optic (red)
    *disc_z(-0.2, 32.1, -6.3, 0.45, 0.7),          # Precision zoom optic (cyan)
    (-2.2, 34.8, -2.4, 0.6, 0.8, 0.6),             # Sensor mast
    (-2.0, 35.6, -2.2, 0.3, 7.0, 0.3))             # Antenna
sym(a, (2.4, 32.0, -4.4, 0.5, 1.8, 2.4))

# ==================== 3. CHEST ARMOR VARIANTS ====================
# A. Sand Chest
a = "armor_chest"
add(a, (-1.1, 21.8, -5.2, 2.2, 7.4, 0.6),
    *[(-1.2, y, -5.5, 2.4, 0.3, 0.3) for y in (22.6, 23.8, 25.0, 26.2, 27.4)],
    (-1.2, 16.2, -5.4, 2.4, 5.6, 0.5),
    (-0.5, 20.6, -5.7, 1.0, 1.0, 0.3),
    (-3.6, 21.0, 1.4, 7.2, 6.4, 0.5))
sym(a, (1.1, 21.6, -5.4, 4.4, 7.0, 3.4),
    (1.3, 28.6, -5.1, 4.0, 0.4, 3.0),
    (3.3, 29.0, -4.2, 1.0, 0.8, 1.0),
    (3.2, 29.8, -4.3, 1.2, 0.3, 1.2),
    (5.5, 22.0, -5.0, 0.4, 6.2, 2.6),
    (1.1, 21.2, -5.2, 4.4, 0.4, 3.0),
    (1.6, 23.0, -5.7, 3.4, 0.3, 0.3),
    (1.6, 27.0, -5.7, 3.4, 0.3, 0.3),
    (4.6, 24.4, -5.7, 0.6, 1.6, 0.3),
    (1.4, 15.4, -5.4, 3.0, 6.6, 0.5),
    (2.4, 20.8, -5.7, 1.0, 1.2, 0.3),
    (1.8, 17.0, -5.6, 2.2, 0.2, 0.2))

# E. Industrial Roll Cage
r = "armor_roll_cage"
for z in (-3.4, 7.2):
    add(r, (-3.8, 60.2, z, 7.6, 0.7, 0.7))
add(r, (-0.35, 60.2, -3.4, 0.7, 0.7, 11.3),
    (-5.0, 44.0, 7.2, 10.0, 0.7, 0.7),
    (-1.8, 60.9, -3.6, 3.6, 0.7, 0.7),
    (-1.4, 61.0, -3.8, 0.8, 0.5, 0.2), (0.6, 61.0, -3.8, 0.8, 0.5, 0.2),
    (-3.0, 61.2, -3.8, 2.0, 1.4, 1.2), (1.0, 61.2, -3.8, 2.0, 1.4, 1.2))
sym(r, (4.6, 29.0, 7.2, 0.7, 30.0, 0.7),
    (4.6, 31.0, -3.4, 0.7, 28.0, 0.7),
    (4.2, 59.0, 7.2, 0.7, 1.2, 0.7), (3.8, 59.8, 7.2, 0.7, 1.1, 0.7),
    (4.2, 59.0, -3.4, 0.7, 1.2, 0.7), (3.8, 59.8, -3.4, 0.7, 1.1, 0.7),
    (3.8, 60.2, -3.4, 0.7, 0.7, 11.3),
    *stepped(4.6, 58.0, -3.0, 45.0, 7.2, 0.5, 0.5, 6),
    (4.4, 30.0, 6.9, 1.1, 0.6, 1.3),
    (4.4, 31.0, -3.7, 1.1, 0.6, 1.3),
    (5.4, 42.0, 0.0, 0.8, 6.0, 1.6))

# ==================== 4. BACKPACKS & REAR MODULES ====================
MOUNT = [(-3.6, 21.6, 6.6, 7.2, 9.8, 0.8),
         (-1.2, 27.0, 5.4, 2.4, 1.6, 1.4),
         *[bx for x in (2.0, -2.8) for bx in [(x, 26.8, 5.4, 0.8, 0.8, 1.4)]],
         *[bx for x in (0.6, -1.4) for bx in [(x, 23.0, 1.0, 0.8, 0.8, 5.8)]],
         *[bx for x in (1.0, -1.5) for bx in stepped(x, 26.6, 6.2, 22.0, 1.6, 0.5, 0.5, 3)]]

b = "backpack_cargo"
add(b, (-4.0, 22.4, 7.4, 8.0, 7.6, 3.6),
    (-4.3, 22.0, 7.4, 8.6, 0.6, 4.0), (-4.3, 29.6, 7.4, 8.6, 0.6, 4.0),
    *MOUNT,
    (-3.2, 25.6, 11.1, 6.4, 1.2, 0.4))
sym(b, (2.2, 22.4, 11.2, 0.6, 7.6, 0.2),
    (4.0, 23.0, 8.0, 0.3, 6.4, 2.8))

b = "backpack_ammo"
add(b, *MOUNT, (-0.6, 30.6, 9.0, 1.2, 0.6, 1.2))
sym(b, (0.4, 24.6, 7.4, 4.0, 6.0, 3.6),
    (0.6, 30.6, 7.6, 3.6, 0.4, 3.2),
    (1.8, 31.0, 8.6, 1.2, 0.4, 0.4),
    (0.3, 26.4, 7.3, 4.2, 0.3, 3.8),
    (4.4, 28.0, 8.4, 0.3, 1.2, 1.4),
    (0.6, 17.2, 11.0, 3.6, 7.6, 0.5),
    (1.6, 23.6, 11.4, 1.6, 0.8, 0.3))

b = "backpack_usmc"
add(b, *MOUNT)
sym(b, (1.2, 28.0, 7.4, 3.4, 5.0, 3.2),
    (1.4, 33.0, 7.6, 3.0, 0.4, 2.8),
    (2.6, 33.4, 8.2, 0.6, 0.6, 0.6),
    (2.7, 34.0, 8.3, 0.4, 11.0, 0.4),
    (0.8, 22.0, 7.6, 3.8, 5.4, 2.8),
    (2.0, 24.0, 10.5, 1.4, 0.8, 0.4))

b = "backpack_cerberus"
add(b, *MOUNT)
sym(b, (0.6, 24.0, 7.4, 4.2, 6.4, 4.0),
    (0.8, 30.4, 7.6, 3.8, 0.5, 3.6),
    (2.0, 30.9, 8.6, 1.4, 0.4, 0.5),
    (0.6, 15.8, 11.4, 4.0, 8.2, 0.6),
    (1.8, 23.0, 11.8, 1.6, 1.0, 0.3))

b = "backpack_missile_pod"
RP_X = -11.0
add(b, (RP_X - 2.8, 33.0, -1.0, 5.6, 5.6, 10.0),
    (RP_X - 3.0, 32.8, -1.4, 6.0, 6.0, 0.6),
    (RP_X - 3.0, 32.8, 8.8, 6.0, 6.0, 0.6),
    (RP_X - 1.0, 29.8, 1.0, 2.0, 3.4, 2.4))
for row in (-1.4, 0.0, 1.4):
    for col in (-1.4, 0.0, 1.4):
        add(b, *disc_z(RP_X + col, 35.8 + row, -1.6, 0.55, 0.4),
            (RP_X + col - 0.25, 35.8 + row - 0.25, -1.8, 0.5, 0.5, 0.3))

def disc_y(cx, y, cz, r, h):
    k = 0.83 * r
    return [(cx - r, y, cz - k / 2, 2 * r, h, k), (cx - k / 2, y, cz - r, k, h, 2 * r),
            (cx - 0.71 * r, y, cz - 0.71 * r, 1.42 * r, h, 1.42 * r)]

def spike(x, y, z, base, length, axis="y", n=3):
    out, seg = [], length / n
    for i in range(n):
        s = base * (1 - i / n)
        o = (base - s) / 2
        if axis == "y":
            out.append((x + o, y + seg * i, z + o, s, seg + 0.05, s))
        elif axis == "x":
            out.append((x + seg * i, y + o, z + o, seg + 0.05, s, s))
        else:
            out.append((x + o, y + o, z - seg * (i + 1), s, s, seg + 0.05))
    return out

SHOULDERS, LEG_ARMOR = {}, {}

# ---------- 1. MARINE RAIDER ----------
a = "armor_head_usmc"
add(a, (-2.8, 34.6, -6.0, 5.6, 0.6, 5.4),
    (-2.4, 35.2, -5.4, 4.8, 0.4, 4.2),
    (-2.9, 34.2, -6.7, 5.8, 0.5, 1.0),
    (-2.6, 33.6, -6.5, 5.2, 0.6, 0.5),
    (-2.6, 30.8, -6.5, 5.2, 0.9, 0.5),
    (-2.6, 31.2, -1.4, 5.2, 3.4, 0.5),
    (-0.4, 35.6, -3.0, 0.8, 0.5, 1.6))
sym(a, (2.6, 31.4, -6.2, 0.5, 3.2, 5.2),
    (2.8, 32.4, -5.8, 0.4, 1.2, 4.4),
    (1.4, 33.8, -7.0, 0.8, 0.6, 0.6),
    (1.6, 34.0, -7.2, 0.4, 0.2, 0.3),
    (-0.2, 31.6, -6.9, 0.4, 0.4, 0.5))

a = "armor_chest_usmc"
add(a, (-1.3, 21.6, -5.5, 2.6, 7.8, 0.7),
    *[(-1.4, y, -5.9, 2.8, 0.3, 0.5) for y in (23.0, 24.5, 26.0, 27.5)],
    (-3.6, 21.0, 1.4, 7.2, 6.4, 0.5),
    (-2.2, 27.6, -5.8, 4.4, 0.7, 0.7))
sym(a, (1.3, 21.4, -5.7, 4.4, 7.4, 3.6),
    (1.3, 28.8, -5.4, 4.2, 0.6, 3.2),
    (5.7, 21.8, -5.2, 0.5, 6.6, 2.8),
    (2.2, 29.4, -4.6, 0.7, 0.7, 3.0),
    (2.2, 21.0, -4.6, 0.7, 8.4, 0.7),
    (2.2, 20.4, -4.6, 0.7, 0.7, 3.0),
    (1.4, 15.2, -5.6, 3.2, 6.8, 0.6),
    (2.2, 19.8, -5.9, 1.4, 1.6, 0.4),
    (2.4, 21.6, -6.0, 1.0, 5.0, 0.4))

SHOULDERS["usmc"] = [
    (5.4, 32.2, -3.8, 5.2, 0.8, 6.2),
    (5.8, 33.0, -3.2, 4.4, 0.6, 5.0),
    (10.6, 26.4, -3.8, 0.8, 5.8, 6.2),
    (10.0, 31.6, -3.6, 1.0, 1.0, 5.8),
    (5.6, 26.8, -4.4, 5.0, 5.2, 0.6),
    (5.6, 26.8, 2.2, 5.0, 5.2, 0.6),
    (10.2, 27.0, -4.2, 0.6, 4.8, 0.5), (10.2, 27.0, 2.1, 0.6, 4.8, 0.5),
    (10.4, 24.8, -3.2, 0.6, 2.0, 5.2),
    (11.4, 28.2, -2.2, 0.3, 2.8, 3.2)
]
LEG_ARMOR["usmc"] = [
    (1.3, 21.4, -5.7, 4.4, 7.4, 3.6),
    (1.3, 28.8, -5.4, 4.2, 0.6, 3.2),
    (5.7, 21.8, -5.2, 0.5, 6.6, 2.8),
    (1.4, 15.2, -5.6, 3.2, 6.8, 0.6)
]

# ---------- 2. CERBERUS ----------
a = "armor_head_dome"
add(a, *disc_y(0, 31.0, -3.8, 2.8, 3.8),
    *disc_y(0, 34.8, -3.8, 2.4, 0.6),
    *disc_y(0, 35.4, -3.8, 1.8, 0.4),
    (-0.4, 35.8, -4.4, 0.8, 0.4, 1.2),
    (-2.2, 32.4, -6.6, 4.4, 0.8, 0.5))
sym(a, (2.6, 32.0, -4.8, 0.5, 1.8, 1.8))

a = "armor_chest_cerberus"
add(a, (-1.2, 21.8, -5.4, 2.4, 7.6, 0.8),
    (-1.4, 22.4, -5.8, 2.8, 6.4, 0.4),
    (-3.6, 21.0, 1.4, 7.2, 6.4, 0.5),
    (-0.5, 27.0, -6.1, 1.0, 1.2, 0.4))
sym(a, (1.2, 21.4, -5.6, 4.6, 7.6, 3.6),
    (1.2, 29.0, -5.3, 4.4, 0.6, 3.2),
    (5.8, 21.8, -5.2, 0.6, 7.0, 3.0),
    (1.6, 25.0, -6.0, 3.6, 2.4, 0.5),
    (1.4, 15.0, -5.5, 3.4, 6.8, 0.6),
    (2.0, 20.2, -5.8, 2.2, 1.2, 0.4))

SHOULDERS["cerberus"] = [
    (5.2, 32.0, -3.8, 5.6, 1.0, 6.4),
    (5.6, 33.0, -3.2, 4.8, 0.8, 5.2),
    (10.8, 26.0, -4.0, 1.0, 6.4, 6.8),
    (5.4, 26.6, -4.6, 5.4, 5.6, 0.7),
    (5.4, 26.6, 2.4, 5.4, 5.6, 0.7),
    (11.8, 27.6, -2.4, 0.4, 3.6, 3.6)
]
LEG_ARMOR["cerberus"] = [
    (1.2, 21.4, -5.6, 4.6, 7.6, 3.6),
    (1.2, 29.0, -5.3, 4.4, 0.6, 3.2),
    (5.8, 21.8, -5.2, 0.6, 7.0, 3.0),
    (1.4, 15.0, -5.5, 3.4, 6.8, 0.6)
]

# ---------- 3. POLAR FRONT ----------
a = "armor_head_polar"
add(a, (-2.7, 31.0, -5.2, 5.4, 3.4, 4.4),
    (-2.4, 34.4, -4.8, 4.8, 0.8, 3.8),
    (-1.6, 32.6, -5.6, 3.2, 0.8, 0.5))
sym(a, (2.7, 31.6, -4.8, 0.4, 2.2, 3.6))

a = "armor_chest_polar"
add(a, (-1.2, 21.8, -5.3, 2.4, 7.4, 0.6),
    (-3.6, 21.0, 1.4, 7.2, 6.4, 0.5))
sym(a, (1.2, 21.6, -5.4, 4.4, 7.0, 3.4),
    (1.4, 15.4, -5.4, 3.0, 6.6, 0.5),
    (5.5, 22.0, -5.0, 0.4, 6.2, 2.6))

SHOULDERS["polar"] = [
    (5.4, 32.0, -3.6, 5.2, 0.8, 6.0),
    (10.4, 26.4, -3.6, 0.8, 5.4, 6.0),
    (5.6, 27.0, -4.2, 5.0, 4.8, 0.6),
    (5.6, 27.0, 2.2, 5.0, 4.8, 0.6)
]
LEG_ARMOR["polar"] = [
    *stepped(2.4, 16.8, -1.8, 11.2, -4.4, 3.8, 1.0, 4),
    (5.8, 13.0, -3.6, 1.0, 4.4, 3.8)
]

SKI = [(2.2, 0.2, -14.0, 4.6, 0.6, 24.0),
       *stepped(2.2, 2.4, -18.0, 0.2, -14.0, 4.6, 0.6, 4),
       (3.0, 0.8, -0.6, 0.4, 1.0, 1.6), (5.6, 0.8, -0.6, 0.4, 1.0, 1.6)]
add("armor_left_ski", *SKI)
add("armor_right_ski", *[mx(b) for b in SKI])

b = "backpack_manpads"
sym(b, *disc_z(10.2, 36.2, -10.0, 1.1, 16.0),
    *disc_z(10.2, 36.2, -10.6, 1.35, 0.8), *disc_z(10.2, 36.2, 5.6, 1.35, 0.8),
    (9.7, 34.0, -3.0, 1.0, 1.4, 1.0),
    (9.8, 33.2, -0.8, 0.8, 2.2, 0.8),
    (4.2, 32.6, -0.6, 6.4, 0.8, 0.8),
    (9.6, 37.3, -4.0, 1.2, 0.8, 1.6))

# ---------- 4. OUTLANDER HEAVY ----------
a = "armor_head_hood"
add(a, (-2.9, 30.8, -6.6, 5.8, 0.8, 5.6),
    (-2.9, 33.6, -6.6, 5.8, 1.4, 5.6),
    *stepped(-2.6, 36.2, -3.0, 35.0, -6.2, 5.2, 0.6, 3),
    (-2.9, 31.6, -1.4, 5.8, 2.0, 0.5),
    (-0.5, 31.6, -6.8, 1.0, 2.0, 0.4))
sym(a, (2.4, 31.6, -6.6, 0.5, 2.0, 5.2),
    *spike(1.6, 35.0, -4.6, 0.7, 2.0))

a = "armor_chest_hood"
def shell_ring(y, h, hx, zf, zb, front=True, t=0.6, c=1.1):
    out = [(-hx + c, y, zb - t, 2 * (hx - c), h, t)]
    if front:
        out.append((-hx + c, y, zf, 2 * (hx - c), h, t))
    for sx in (1, -1):
        out.append(((hx - t) if sx > 0 else -hx, y, zf + c, t, h, zb - zf - 2 * c))
        for zc in (zf, zb - c):
            out.append(((hx - c) if sx > 0 else -hx, y, zc, c, h, c))
    return out

def round_ring(y, h, hx, zf, zb, r=2.6, t=0.6, front=True, n=3):
    """shell_ring with quarter-round corners (n voxel steps per corner) instead of square posts."""
    out = [(-hx + r, y, zb - t, 2 * (hx - r), h, t)]
    if front:
        out.append((-hx + r, y, zf, 2 * (hx - r), h, t))
    for sx in (1, -1):
        out.append(((hx - t) if sx > 0 else -hx, y, zf + r, t, h, zb - zf - 2 * r))
        for zc, sz in ((zf, 1), (zb, -1)):
            for i in range(n):
                a0, a1 = math.pi / 2 * i / n, math.pi / 2 * (i + 1) / n
                xs = [hx - r + r * math.cos(a) for a in (a0, a1)]
                zs = [r - r * math.sin(a) for a in (a0, a1)]
                x0, x1 = min(xs), max(max(xs), min(xs) + t)
                z0, z1 = min(zs), max(max(zs), min(zs) + t)
                x0, x1 = (x0, x1) if sx > 0 else (-x1, -x0)
                z0, z1 = (zc + z0, zc + z1) if sz > 0 else (zc - z1, zc - z0)
                out.append((x0, y, z0, x1 - x0, h, z1 - z0))
    return out

add(a, (-4.6, 21.0, -5.8, 9.2, 8.6, 3.8),
    (-1.6, 15.0, -5.9, 3.2, 6.0, 0.6),
    *shell_ring(31.0, 1.6, 5.1, -9.0, 9.0),
    *shell_ring(32.6, 1.8, 5.0, -8.8, 8.8))
sym(a, *[(5.0, y, -5.0, 0.2, 0.4, 10.0) for y in (31.6, 33.4)])

SHOULDERS["outlander"] = [
    (5.4, 32.0, -4.2, 6.0, 1.0, 7.2),
    (10.6, 25.8, -4.2, 1.0, 6.6, 7.2),
    (5.6, 26.6, -4.8, 5.2, 5.6, 0.6), (5.6, 26.6, 2.4, 5.2, 5.6, 0.6),
    *spike(9.4, 33.0, -2.8, 1.0, 3.0), *spike(9.4, 33.0, 0.8, 1.0, 2.4),
    *spike(11.6, 28.4, -1.0, 1.0, 2.6, "x"),
    (10.2, 24.2, -3.4, 0.8, 1.8, 5.6)
]
LEG_ARMOR["outlander"] = [
    *stepped(2.6, 16.8, -1.9, 10.8, -4.6, 3.8, 1.2, 4),
    (6.0, 12.6, -3.8, 1.2, 4.6, 4.0),
    (2.7, 7.0, -6.0, 3.6, 3.8, 1.2),
    *spike(3.9, 8.0, -6.0, 1.2, 3.0, "-z"),
]

# ==================== 5. 6 NEW FACTION ARMOR SETS ====================
# ----- Faction 1: SALVAGE MILITIA -----
add("armor_head_salvage",
    (-2.6, 31.0, -5.2, 5.2, 3.2, 4.2),
    (-2.8, 34.2, -5.4, 5.6, 0.6, 4.4),
    (-2.0, 32.5, -5.5, 4.0, 0.8, 0.4),
    *disc_z(1.0, 32.8, -5.8, 0.7, 0.6),
    (-2.2, 34.8, -2.4, 0.6, 0.8, 0.6),
    (-2.0, 35.6, -2.2, 0.3, 5.0, 0.3))
sym("armor_head_salvage", (2.4, 31.6, -5.0, 0.4, 2.0, 3.8))

add("armor_chest_salvage",
    (-1.2, 21.6, -5.3, 2.4, 7.6, 0.6),
    (-3.6, 21.0, 1.4, 7.2, 6.4, 0.5),
    *[(-1.4, y, -5.6, 2.8, 0.4, 0.4) for y in (22.8, 24.6, 26.4)])
sym("armor_chest_salvage",
    (1.2, 21.6, -5.4, 4.2, 7.0, 3.2),
    (1.4, 15.4, -5.4, 3.0, 6.4, 0.5),
    (5.4, 22.0, -5.0, 0.4, 6.0, 2.6))

c = "canopy_salvage"   # low welded tub + one roll hoop: reads as scrap, not a box
add(c,
    *round_ring(33.0, 8.0, 9.6, -9.4, 10.2, r=2.0),
    (-6.0, 37.0, -9.8, 4.6, 3.6, 0.4), (1.8, 35.4, -9.8, 3.8, 2.6, 0.4),   # patch plates
    (-9.0, 41.0, 9.6, 0.8, 19.4, 0.8), (8.2, 41.0, 9.6, 0.8, 19.4, 0.8),    # roll hoop legs
    (-9.0, 60.4, 9.6, 18.0, 0.8, 0.8),                                    # hoop top
    (-9.6, 41.0, -9.4, 0.7, 6.0, 0.7), (8.9, 41.0, -9.4, 0.7, 6.0, 0.7),
    (-9.6, 47.0, -9.4, 0.7, 0.7, 19.0), (8.9, 47.0, -9.4, 0.7, 0.7, 19.0))  # grab rails

SHOULDERS["salvage"] = [
    (5.4, 31.8, -3.8, 5.2, 0.8, 6.2),
    (10.4, 25.8, -3.8, 0.8, 5.8, 6.2),
    (5.6, 26.6, -4.4, 5.0, 5.0, 0.6), (5.6, 26.6, 2.2, 5.0, 5.0, 0.6),
    (10.6, 27.0, -2.5, 0.4, 0.6, 3.6), (10.6, 29.0, -2.5, 0.4, 0.6, 3.6)
]
LEG_ARMOR["salvage"] = [
    *stepped(2.4, 16.6, -1.8, 11.0, -4.4, 3.8, 1.0, 4),
    (5.8, 12.8, -3.6, 1.0, 4.4, 3.8),
    (2.6, 12.0, -4.8, 3.4, 2.0, 0.6)
]
add("backpack_salvage", *MOUNT,
    (-3.8, 22.4, 7.4, 7.6, 7.4, 3.4), (-3.2, 26.0, 11.0, 6.4, 2.0, 0.6))
sym("backpack_salvage",
    *disc_z(2.0, 26.0, 8.0, 1.4, 4.0), (1.6, 29.2, 8.2, 1.6, 1.2, 1.6))

# ----- Faction 2: SHIDEN CORPS -----
add("armor_head_shiden",
    (-2.5, 31.0, -5.0, 5.0, 3.4, 4.2),
    (-1.8, 32.6, -5.4, 3.6, 0.6, 0.5),
    *stepped(-0.4, 35.0, -4.8, 38.0, -4.0, 0.8, 0.4, 3),
    (-2.6, 34.6, -4.6, 5.2, 0.6, 3.8))
sym("armor_head_shiden",
    (2.1, 30.5, -5.2, 0.5, 3.0, 3.6),
    *stepped(1.5, 35.0, -4.8, 37.5, -3.8, 0.6, 0.4, 3))

add("armor_chest_shiden",
    (-1.2, 21.8, -5.4, 2.4, 7.4, 0.7),
    (-3.6, 21.0, 1.4, 7.2, 6.4, 0.5),
    (-1.0, 24.0, -5.8, 2.0, 3.0, 0.5))
sym("armor_chest_shiden",
    (1.2, 21.6, -5.5, 4.4, 7.2, 3.4),
    (1.4, 15.4, -5.4, 3.0, 6.4, 0.5),
    (5.4, 22.0, -5.0, 0.4, 6.0, 2.6))

c = "canopy_shiden"
add(c,   # rounded tub, forward-raked visor band, dome tapering above the shoulders
    *round_ring(33.0, 15.0, 9.6, -9.6, 10.4, r=3.0),
    *round_ring(48.0, 4.0, 9.4, -9.0, 10.3, r=3.0),
    *round_ring(52.0, 3.0, 8.8, -7.4, 10.1, r=3.0),
    *round_ring(55.0, 2.4, 7.4, -5.0, 9.9, r=2.6),
    *round_ring(57.4, 2.2, 6.0, -2.6, 9.8, r=2.2),
    (-4.6, 59.7, -2.0, 9.2, 0.6, 11.2),
    (-6.0, 49.4, -9.3, 12.0, 0.8, 0.4),                 # vision slit
    (-0.4, 60.3, 4.0, 0.8, 2.6, 0.8))                  # blade antenna

SHOULDERS["shiden"] = [
    (5.4, 32.4, -3.6, 5.4, 0.8, 6.0),
    (5.2, 33.2, -3.0, 4.8, 0.6, 5.0),
    (10.6, 27.0, -3.8, 0.8, 5.2, 6.4),
    (11.4, 28.0, -3.0, 0.6, 3.6, 5.0),
    (5.6, 27.2, -4.2, 5.2, 4.8, 0.6), (5.6, 27.2, 2.2, 5.2, 4.8, 0.6)
]
LEG_ARMOR["shiden"] = [
    *stepped(2.4, 16.8, -1.8, 11.2, -4.4, 3.8, 1.0, 4),
    (5.8, 13.0, -3.6, 1.0, 4.4, 3.8),
    (3.0, 13.2, -4.9, 2.8, 3.0, 0.6)
]
add("backpack_shiden", *MOUNT, (-3.4, 22.4, 7.4, 6.8, 7.4, 3.2))
sym("backpack_shiden",
    *disc_z(2.6, 26.0, 7.6, 1.6, 4.0), *disc_z(2.6, 26.0, 11.4, 1.2, 0.8),
    (3.8, 25.0, 8.0, 0.4, 2.0, 3.0))

# ----- Faction 3: KHAMSIN GUARD -----
add("armor_head_khamsin",
    (-2.7, 31.0, -5.2, 5.4, 3.4, 4.4),
    (-2.9, 34.4, -5.6, 5.8, 0.6, 4.6),
    *[(-1.5, y, -5.5, 3.0, 0.3, 0.4) for y in (31.5, 32.2, 32.9)])
sym("armor_head_khamsin", *disc_z(2.2, 32.0, -4.8, 0.8, 3.2))

add("armor_chest_khamsin",
    (-1.2, 21.8, -5.3, 2.4, 7.4, 0.6),
    (-3.6, 21.0, 1.4, 7.2, 6.4, 0.5))
sym("armor_chest_khamsin",
    (1.2, 21.6, -5.4, 4.4, 7.0, 3.4),
    (1.4, 15.4, -5.4, 3.0, 6.4, 0.5),
    (5.4, 22.0, -5.0, 0.4, 6.0, 2.6))

c = "canopy_khamsin"
add(c,   # open desert tub with a sloped sun-shade on four posts
    *round_ring(33.0, 11.0, 9.6, -9.6, 10.4, r=3.0),
    (-9.0, 44.0, -9.0, 0.6, 17.4, 0.6), (8.4, 44.0, -9.0, 0.6, 17.4, 0.6),
    (-9.0, 44.0, 9.6, 0.6, 16.2, 0.6), (8.4, 44.0, 9.6, 0.6, 16.2, 0.6),
    *[(-9.6, 61.4 - 0.3 * k, -9.8 + 4.2 * k, 19.2, 0.5, 4.4) for k in range(5)],
    (-3.0, 41.0, -10.0, 6.0, 1.6, 0.4))                  # sand filter grille

SHOULDERS["khamsin"] = [
    (5.2, 32.0, -4.0, 5.6, 0.8, 6.8),
    (10.6, 26.2, -4.0, 0.8, 5.6, 6.8),
    (5.4, 26.8, -4.6, 5.4, 5.0, 0.6), (5.4, 26.8, 2.6, 5.4, 5.0, 0.6)
]
LEG_ARMOR["khamsin"] = [
    *stepped(2.4, 16.6, -1.8, 11.0, -4.4, 4.0, 1.0, 4),
    (6.0, 12.6, -3.8, 1.0, 4.6, 4.0),
    (2.6, 12.0, -4.8, 3.6, 1.5, 0.5)
]
add("backpack_khamsin", *MOUNT,
    (-3.6, 22.4, 7.4, 7.2, 7.4, 3.2),
    (-0.4, 30.0, 8.0, 0.8, 8.0, 0.8))
sym("backpack_khamsin",
    *disc_z(2.4, 26.0, 7.6, 1.5, 3.6),
    (1.0, 23.0, 11.2, 2.8, 5.6, 0.5))

# ----- Faction 4: RIVERINE RECON -----
add("armor_head_riverine",
    (-2.5, 31.2, -5.0, 5.0, 3.2, 4.2),
    (-1.5, 31.0, -6.0, 3.0, 1.4, 1.2))
sym("armor_head_riverine",
    (1.4, 34.4, -4.0, 0.6, 4.0, 0.6), (1.4, 37.8, -4.4, 0.6, 0.6, 1.0))

add("armor_chest_riverine",
    (-1.2, 21.8, -5.4, 2.4, 7.4, 0.7),
    (-3.6, 21.0, 1.4, 7.2, 6.4, 0.5))
sym("armor_chest_riverine",
    (1.2, 21.6, -5.4, 4.4, 7.0, 3.4),
    (1.4, 15.4, -5.4, 3.0, 6.4, 0.5),
    (5.4, 22.0, -5.0, 0.4, 6.0, 2.6))

c = "canopy_riverine"
add(c,
    *round_ring(34.0, 12.0, 9.6, -9.6, 10.4, r=3.0),
    (-6.0, 44.0, -10.2, 12.0, 2.4, 0.8),
    (-8.4, 44.0, -9.4, 1.6, 12.0, 1.6), (-8.6, 55.6, -9.8, 2.0, 0.8, 2.0),   # snorkel
    (-8.6, 60.0, 9.4, 17.2, 0.8, 0.8),
    (-8.6, 46.0, 9.4, 0.8, 14.0, 0.8),
    (7.8, 46.0, 9.4, 0.8, 14.0, 0.8))

SHOULDERS["riverine"] = [
    (5.4, 32.0, -3.6, 5.2, 0.8, 6.0),
    (10.4, 26.4, -3.6, 0.8, 5.4, 6.0),
    (5.6, 27.0, -4.2, 5.0, 4.8, 0.6), (5.6, 27.0, 2.2, 5.0, 4.8, 0.6),
    (10.8, 28.0, -2.5, 0.5, 2.4, 4.0)
]
LEG_ARMOR["riverine"] = [
    *stepped(2.4, 16.8, -1.8, 11.2, -4.4, 3.8, 1.0, 4),
    (5.8, 13.0, -3.6, 1.0, 4.4, 3.8),
    (2.8, 12.2, -4.8, 3.2, 2.0, 0.6)
]
add("backpack_riverine", *MOUNT,
    (-3.6, 22.4, 7.4, 7.2, 7.4, 3.2),
    (-0.8, 29.8, 7.8, 1.6, 8.0, 1.6), (-0.6, 37.6, 7.4, 1.2, 1.0, 2.0))
sym("backpack_riverine", *disc_z(2.6, 25.6, 7.6, 1.4, 4.0))

# ----- Faction 5: SPECTER PMC -----
add("armor_head_specter",
    (-2.6, 31.4, -4.8, 5.2, 2.8, 4.0),
    (-2.0, 32.4, -5.2, 4.0, 0.5, 0.4))
sym("armor_head_specter", (2.6, 31.0, -4.6, 0.5, 2.6, 3.6))

add("armor_chest_specter",
    (-1.2, 21.8, -5.4, 2.4, 7.4, 0.7),
    (-3.6, 21.0, 1.4, 7.2, 6.4, 0.5))
sym("armor_chest_specter",
    (1.2, 21.6, -5.4, 4.4, 7.0, 3.4),
    (1.4, 15.4, -5.4, 3.0, 6.4, 0.5),
    (5.4, 22.0, -5.0, 0.4, 6.0, 2.6))

c = "canopy_specter"
add(c,   # stealth wedge: hard single-step chamfers, steep taper from the shoulders up
    *round_ring(33.0, 13.0, 9.6, -9.6, 10.2, r=2.0, n=1),
    *round_ring(46.0, 4.0, 9.2, -8.8, 10.0, r=2.4, n=1),
    *round_ring(50.0, 4.0, 8.2, -6.4, 9.9, r=2.4, n=1),
    *round_ring(54.0, 3.0, 7.0, -3.2, 9.8, r=2.2, n=1),
    *round_ring(57.0, 2.6, 5.6, -1.0, 9.8, r=1.8, n=1),
    (-4.8, 59.7, -0.6, 9.6, 0.6, 10.4),
    (-5.0, 47.0, -9.0, 10.0, 0.6, 0.4))                  # sensor slit

SHOULDERS["specter"] = [
    (5.4, 32.6, -3.8, 5.2, 0.8, 6.2),
    (10.4, 27.0, -4.0, 0.8, 5.4, 6.4),
    (11.2, 28.5, -2.5, 0.6, 2.6, 4.0),
    (5.6, 27.2, -4.4, 5.0, 5.0, 0.6), (5.6, 27.2, 2.2, 5.0, 5.0, 0.6)
]
LEG_ARMOR["specter"] = [
    *stepped(2.4, 16.8, -1.8, 11.2, -4.4, 3.8, 1.0, 4),
    (5.8, 13.0, -3.6, 1.0, 4.4, 3.8),
    (3.0, 13.0, -4.8, 2.6, 2.8, 0.6)
]
add("backpack_specter", *MOUNT,
    (-3.4, 22.6, 7.4, 6.8, 7.0, 2.6),
    (-2.8, 23.2, 10.0, 5.6, 5.8, 0.8))
sym("backpack_specter", (3.2, 24.0, 8.0, 0.5, 4.0, 2.2))

# ----- Faction 6: VALKYRIE GUARD -----
add("armor_head_valkyrie",
    *disc_z(0, 32.5, -4.5, 2.2, 3.8),
    (-0.3, 34.5, -4.2, 0.6, 2.5, 3.0))
sym("armor_head_valkyrie",
    *disc_z(1.1, 33.2, -5.2, 0.5, 0.6),
    *disc_z(1.1, 31.8, -5.2, 0.5, 0.6))

add("armor_chest_valkyrie",
    (-1.2, 21.8, -5.5, 2.4, 7.6, 0.8),
    (-3.6, 21.0, 1.4, 7.2, 6.4, 0.5))
sym("armor_chest_valkyrie",
    (1.2, 21.6, -5.6, 4.6, 7.2, 3.6),
    (1.4, 15.4, -5.4, 3.0, 6.4, 0.5),
    (5.4, 22.0, -5.0, 0.4, 6.0, 2.6))

c = "canopy_valkyrie"
add(c,   # smooth elite pod: 4-step round corners, dome, tri-lens sensor array
    *round_ring(33.0, 15.0, 9.8, -9.6, 10.6, r=3.6, n=4),
    *round_ring(48.0, 4.0, 9.4, -9.0, 10.4, r=3.6, n=4),
    *round_ring(52.0, 3.0, 8.4, -7.0, 10.2, r=3.2, n=4),
    *round_ring(55.0, 2.4, 7.0, -4.6, 9.9, r=2.8),
    *round_ring(57.4, 2.2, 5.4, -2.0, 9.8, r=2.0),
    (-3.6, 59.7, -1.4, 7.2, 0.6, 10.6),
    (-9.9, 47.0, -6.0, 0.3, 0.5, 13.0), (9.6, 47.0, -6.0, 0.3, 0.5, 13.0),   # trim lines
    *disc_z(-2.2, 50.0, -9.4, 0.7, 0.4), *disc_z(0.0, 50.6, -9.4, 0.9, 0.4), *disc_z(2.2, 50.0, -9.4, 0.7, 0.4))

SHOULDERS["valkyrie"] = [
    (5.2, 32.6, -3.8, 5.6, 0.8, 6.2),
    (5.4, 33.4, -3.2, 4.6, 0.6, 5.0),
    (10.6, 26.4, -4.0, 0.9, 6.0, 6.4),
    (11.5, 27.2, -3.0, 0.6, 4.4, 4.8),
    (5.4, 26.8, -4.4, 5.4, 5.2, 0.6), (5.4, 26.8, 2.2, 5.4, 5.2, 0.6)
]
LEG_ARMOR["valkyrie"] = [
    *stepped(2.2, 16.8, -1.8, 11.0, -4.5, 4.2, 1.2, 4),
    (6.0, 12.6, -3.8, 1.2, 4.8, 4.2),
    (2.6, 12.4, -5.0, 3.6, 3.2, 0.8)
]
add("backpack_valkyrie", *MOUNT,
    (-3.6, 22.4, 7.4, 7.2, 7.4, 3.6),
    *disc_z(0, 26.0, 11.0, 1.8, 1.2))
sym("backpack_valkyrie", (3.6, 23.0, 7.8, 0.5, 8.0, 3.2))

# ---------- SHIN GREAVES (all factions) ----------
GREAVE = [*stepped(2.9, 8.2, -4.6, 2.6, -0.2, 3.2, 0.7, 5),
          *stepped(5.8, 5.4, -1.0, 2.8, 1.4, 0.5, 2.4, 2),
          *stepped(2.6, 7.6, -2.6, 2.8, 1.2, 0.5, 2.4, 3),
          (3.0, 2.4, -0.6, 3.0, 0.8, 2.6)]

SHIN_EXTRA = {
    "sand": [],
    "usmc": [*disc_x(6.3, 4.4, 0.2, 0.5, 0.2), (3.2, 6.6, -4.9, 2.6, 0.3, 0.3), (3.2, 4.6, -3.4, 2.6, 0.3, 0.3)],
    "cerberus": [(3.0, 2.8, 2.4, 3.0, 4.8, 0.5), (3.6, 7.4, 1.0, 1.8, 0.8, 0.4)],
    "polar": [*stepped(3.3, 8.0, -5.0, 3.0, -0.6, 2.4, 0.4, 4)],
    "outlander": [*spike(3.9, 5.2, -2.6, 1.0, 2.4, "-z"), (2.8, 7.0, -5.0, 3.4, 1.2, 1.0)],
    "salvage": [(3.0, 6.8, -4.8, 2.8, 0.8, 0.5), (3.4, 4.4, -3.2, 2.2, 0.6, 0.4)],
    "shiden": [(3.0, 7.0, -5.0, 3.0, 1.4, 0.6), (3.2, 4.0, -3.4, 2.6, 1.2, 0.5)],
    "khamsin": [(2.8, 6.4, -4.8, 3.4, 1.6, 0.5), (5.9, 4.2, -0.6, 0.5, 2.0, 2.0)],
    "riverine": [(3.0, 6.6, -4.8, 3.0, 1.2, 0.6), (3.2, 4.2, -3.4, 2.6, 1.0, 0.5)],
    "specter": [(3.2, 7.0, -4.8, 2.6, 1.4, 0.5), (3.4, 4.2, -3.2, 2.2, 1.2, 0.4)],
    "valkyrie": [(2.8, 7.2, -5.2, 3.4, 1.8, 0.8), (3.0, 4.0, -3.6, 3.0, 1.6, 0.6)]
}
for faction, extra in SHIN_EXTRA.items():
    add(f"armor_left_shin_{faction}", *GREAVE, *extra)
    add(f"armor_right_shin_{faction}", *[mx(b) for b in GREAVE + extra])

# ---------- PILOT CAPSULES (existing) ----------
c = "canopy_usmc"   # enclosed hood: rounded corners, vision slit, tapering brow and roof
add(c, *round_ring(33.0, 13.6, 9.8, -9.8, 10.4, r=3.2),
    *round_ring(46.6, 2.2, 9.8, -9.8, 10.4, r=3.2, front=False),          # vision slit gap
    *round_ring(48.8, 6.2, 9.6, -9.6, 10.3, r=3.2),
    *round_ring(55.0, 2.4, 8.4, -7.4, 10.1, r=3.0),
    *round_ring(57.4, 2.2, 7.0, -4.6, 9.9, r=2.4),
    (-5.6, 59.7, -5.0, 11.2, 0.8, 14.4),
    (-0.4, 46.6, -9.7, 0.8, 2.2, 0.6),
    (-6.0, 50.2, -10.0, 12.0, 0.6, 0.4),
    (-2.0, 60.5, 1.0, 4.0, 0.6, 0.6),
    *disc_z(-2.4, 61.4, -6.0, 1.0, 2.0), *disc_z(2.4, 61.4, -6.0, 1.0, 2.0),
    *disc_z(-2.4, 61.4, -6.3, 0.6, 0.3), *disc_z(2.4, 61.4, -6.3, 0.6, 0.3))
sym(c, (9.8, 40.0, -6.0, 0.3, 0.6, 12.0), (9.8, 50.0, -6.0, 0.3, 0.6, 12.0),
    (9.8, 43.0, -2.0, 0.3, 4.6, 6.0),
    (6.0, 53.0, -10.0, 1.6, 1.0, 0.4),
    (3.0, 31.4, 8.6, 1.0, 2.0, 1.2))

c = "canopy_cerberus"
add(c, *round_ring(35.0, 5.0, 9.8, -9.4, 10.4, r=3.0),
    *round_ring(40.0, 3.4, 9.7, -9.2, 10.2, r=3.0),
    *round_ring(43.4, 1.0, 9.5, -9.0, 10.0, r=3.0),
    (-0.6, 41.0, -9.9, 1.2, 2.0, 0.6),
    (-6.8, 53.0, 9.6, 13.6, 0.8, 0.8))
sym(c, (6.0, 44.4, 9.6, 0.8, 9.4, 0.8),
    (6.0, 52.2, 3.0, 0.8, 0.8, 7.4),
    (5.6, 37.0, -9.6, 2.0, 2.4, 0.4))

c = "canopy_polar"
add(c, *disc_y(0, 35.0, 4.6, 8.8, 22.0),
    (-4.6, 37.6, -8.6, 9.2, 4.6, 6.0),
    *disc_y(0, 57.0, 4.6, 8.2, 1.0),
    *disc_y(0, 58.0, 4.6, 6.6, 1.6),
    *disc_y(0, 59.6, 4.6, 4.2, 1.2),
    *disc_y(0, 60.8, 4.6, 3.4, 0.5),
    (-0.6, 61.3, 3.4, 1.2, 0.6, 2.4),
    (-3.4, 58.4, -3.4, 1.2, 3.4, 1.2), (-3.6, 61.8, -3.8, 1.6, 1.0, 1.8),
    (-2.6, 48.0, -4.4, 5.2, 1.2, 0.4))
sym(c, (9.1, 40.0, 0.0, 0.6, 15.0, 0.6),
    (9.1, 55.0, 0.0, 0.6, 0.6, 9.0), (9.1, 40.0, 8.4, 0.6, 15.6, 0.6),
    (7.6, 56.2, -2.4, 1.6, 0.6, 0.6))

c = "canopy_hood"
add(c, *round_ring(40.4, 5.6, 8.9, -8.6, 10.0, r=3.0),
    *round_ring(46.0, 5.0, 8.8, -8.4, 9.8, r=3.0),
    *round_ring(51.0, 2.0, 8.7, -8.0, 9.9, r=3.0),
    *round_ring(53.0, 1.2, 7.6, -8.0, 9.9, front=False, r=3.0),
    *round_ring(54.2, 1.8, 7.6, -8.0, 9.9, r=3.0),
    *round_ring(56.0, 2.4, 6.8, -7.2, 9.8, r=2.4),
    *round_ring(58.4, 1.6, 5.8, -6.2, 9.7, r=2.4),
    (-5.4, 60.0, -6.0, 10.8, 0.8, 14.2),
    (-0.4, 53.0, -8.2, 0.8, 1.2, 0.5),
    (-0.5, 60.8, -5.0, 1.0, 0.6, 12.0),
    *[(-6.0 + 1.5 * k, 46.6, -8.65, 0.5, 4.0, 0.3) for k in range(9)])
sym(c, *spike(3.6, 60.8, -5.4, 1.0, 3.0), *spike(3.6, 60.8, 4.4, 1.0, 2.4),
    *spike(7.6, 50.0, -3.0, 1.0, 2.4, "x"))

for faction, boxes in SHOULDERS.items():
    add(f"armor_left_shoulder_{faction}", *boxes)
    add(f"armor_right_shoulder_{faction}", *[mx(b) for b in boxes])
for faction, boxes in LEG_ARMOR.items():
    add(f"armor_left_leg_{faction}", *boxes)
    add(f"armor_right_leg_{faction}", *[mx(b) for b in boxes])

# ==================== 5. ARMS & SHOULDERS ====================
L = {
    "left_arm": [
        *disc_x(5.4, 30.0, -0.5, 1.6, 1.8),                   # Shoulder joint disk (outer edge x = 7.2)
        (5.2, 24.8, -1.5, 2.0, 4.8, 2.0),                     # Slender upper arm cylinder (thickness 2.0, length 5.4, outer x = 7.2)
        (5.3, 25.2, -1.8, 1.8, 3.6, 0.3),                     # Upper arm front plate
        *piston_y(6.0, 24.8, 29.2, 0.4, 0.6),                  # Upper arm hydraulic line
        (5.3, 24.0, -1.4, 0.4, 1.6, 1.8), (6.7, 24.0, -1.4, 0.4, 1.6, 1.8)
    ],
    "armor_left_shoulder": [
        (5.2, 31.8, -3.4, 4.6, 0.8, 5.6),
        (5.6, 32.4, -2.8, 3.6, 0.5, 4.4),
        (9.6, 26.6, -3.4, 0.8, 5.0, 5.6),
        (9.0, 31.2, -3.2, 1.0, 1.0, 5.2),
        (5.4, 27.2, -4.0, 4.4, 4.6, 0.6),
        (5.4, 27.2, 2.2, 4.4, 4.6, 0.6),
        (9.2, 27.2, -3.8, 0.6, 4.2, 0.4), (9.2, 27.2, 2.0, 0.6, 4.2, 0.4),
        (9.2, 24.6, -2.8, 0.6, 2.0, 4.6),
        (10.2, 28.0, -1.8, 0.2, 2.6, 2.8),
        (8.8, 24.8, -1.8, 0.5, 3.0, 2.8)
    ],
    "left_forearm": [
        *disc_x(5.5, 24.6, -0.5, 1.4, 2.0),                   # Elbow joint disk
        (5.1, 18.0, -1.8, 3.0, 6.2, 3.0),                     # Heavy industrial forearm (thickness 3.0 = 1.50x upper, length 7.0 = 1.30x upper!)
        (7.7, 18.6, -1.4, 0.4, 5.0, 2.4),                     # Outer armored forearm rib
        *piston_y(6.0, 17.8, 23.6, 0.6, 0.7),                  # Forearm main hydraulic piston
        (5.1, 17.4, -1.9, 3.0, 1.0, 3.2)                      # Wrist cuff flange
    ],
    "left_hand": [
        (5.5, 15.6, -1.7, 2.0, 1.8, 2.6),                     # Wrist joint block
        (5.3, 12.8, -2.0, 2.4, 2.8, 3.2),                     # Large blocky fist palm
        *[(5.5, 10.0, z, 2.0, 2.8, 0.65) for z in (-1.8, -1.0, -0.2, 0.6)], # Heavy blocky knuckles (hang to y = 10.0 = knee top!)
        (5.0, 11.6, -2.2, 0.6, 2.2, 1.0)                      # Thumb block
    ]
}

MIRROR = {
    "left_arm": "right_arm",
    "armor_left_shoulder": "armor_right_shoulder",
    "left_forearm": "right_forearm",
    "left_hand": "right_hand"
}
for n, boxes in L.items():
    add(n, *boxes)
    if n in MIRROR:
        add(MIRROR[n], *[mx(bx) for bx in boxes])

add("armor_right_shoulder_red", *[mx(bx) for bx in SHOULDERS["usmc"]])

# ==================== 6. LEGS & LOWER BODY ====================
LEGS = {
    "left_thigh": [
        *disc_x(4.0, 17.0, 0.0, 2.2, 1.2),
        (3.4, 10.6, -1.8, 2.2, 5.8, 3.6),
        (3.3, 11.2, -2.1, 2.4, 4.6, 0.3),
        (3.5, 9.6, -2.6, 2.0, 1.8, 1.6),
        *piston_y(4.2, 10.2, 16.0, 1.2, 0.8),
        (3.0, 10.0, -2.8, 0.5, 1.2, 2.0)
    ],
    "armor_left_leg": [
        (2.6, 16.0, -2.0, 3.8, 1.0, 4.0),
        (2.8, 16.8, -1.6, 3.4, 0.4, 3.2),
        (6.0, 11.0, -2.6, 0.8, 5.4, 4.6),
        (6.2, 12.0, -2.0, 0.4, 4.0, 3.6),
        (2.8, 11.6, -3.2, 3.6, 4.8, 1.0),
        (2.6, 12.0, -3.4, 4.0, 4.0, 0.3),
        (2.8, 11.6, 1.8, 3.6, 4.8, 0.8),
        (3.2, 7.8, -4.8, 2.6, 3.2, 1.2),
        (3.0, 8.2, -5.0, 3.0, 2.4, 0.3),
        (3.2, 8.4, -2.0, 2.6, 2.0, 0.6)
    ],
    "left_shin": [
        *disc_x(3.8, 9.0, -2.8, 1.8, 1.4),
        (3.6, 3.0, -2.2, 1.8, 5.6, 2.6),
        *piston_y(4.0, 2.8, 8.4, 0.6, 0.8),                   # Exposed hydraulic piston rod behind the shin!
        (3.7, 2.4, -0.8, 1.6, 1.4, 3.2),
        *disc_x(3.7, 2.0, 2.2, 1.2, 1.6)
    ],
    "left_knee_wheel": [
        *disc_x(5.6, 9.0, -2.8, 2.2, 2.4),
        *ring_x(5.5, 9.0, -2.8, 2.2, 2.6),
        *disc_x(5.45, 9.0, -2.8, 0.9, 2.7),
        (5.3, 8.7, -3.1, 3.0, 0.6, 0.6)
    ],
    "left_foot": [
        # Long pointed foot: length = 6.0 (ratio foot_len / leg_len = 6.0 / 17.08 = 0.351 = 0.35x leg length!)
        (3.2, 0.0, -3.8, 2.6, 1.8, 6.0),                      # Sleek main foot sole
        (3.4, 0.0, -4.4, 2.2, 1.2, 0.8),                      # Pointed forward toe wedge
        (3.3, 1.8, 0.2, 2.4, 0.8, 2.2),                       # Ankle knuckle mount
        (3.4, 0.4, 1.8, 2.2, 1.2, 1.2)                        # Rear heel spur
    ]
}

LEG_MIRROR = {
    "left_thigh": "right_thigh",
    "armor_left_leg": "armor_right_leg",
    "left_shin": "right_shin",
    "left_knee_wheel": "right_knee_wheel",
    "left_foot": "right_foot"
}
for n, boxes in LEGS.items():
    add(n, *boxes)
    if n in LEG_MIRROR:
        add(LEG_MIRROR[n], *[mx(bx) for bx in boxes])

# ==================== 7. WEAPONS & TACTICAL TOOLS ====================
X = -8.0

# 1. 20mm Assault Rifle
g = "weapon_assault_rifle"
add(g, (X - 1.0, 13.0, -9.0, 2.0, 2.4, 9.0),
    (X - 1.05, 14.4, -8.0, 0.1, 0.6, 3.0),
    (X - 0.8, 15.4, -9.0, 1.6, 0.4, 9.0),
    *[(X - 0.9, 15.8, z, 1.8, 0.2, 0.4) for z in (-8.6, -7.4, -6.2, -5.0, -3.8, -2.6)],
    (X - 0.6, 16.0, -7.6, 1.2, 0.4, 1.0), (X - 0.6, 16.0, -3.4, 1.2, 0.4, 1.0),
    (X - 0.7, 16.4, -8.4, 1.4, 1.4, 6.0),
    (X - 0.9, 16.2, -9.4, 1.8, 1.8, 1.0), (X - 0.8, 16.3, -2.6, 1.6, 1.6, 0.8),
    (X - 0.5, 16.5, -9.5, 1.0, 1.0, 0.1),
    (X - 0.8, 13.2, -18.0, 1.6, 2.0, 9.0),
    *[(X - 0.85, 14.4, z, 1.7, 0.4, 0.5) for z in (-17, -15.5, -14, -12.5, -11)],
    (X - 0.8, 12.6, -17.0, 1.6, 0.6, 4.0),
    (X - 0.4, 13.8, -25.0, 0.8, 0.8, 7.0),
    (X - 0.3, 14.9, -24.0, 0.6, 0.3, 6.0),
    (X - 0.6, 13.6, -27.0, 1.2, 1.2, 2.0),
    (X - 0.7, 13.9, -26.4, 1.4, 0.6, 0.6),
    (X - 0.3, 15.2, -24.6, 0.6, 0.8, 0.5),
    *stepped(X - 0.7, 13.0, -6.6, 8.6, -5.2, 1.4, 1.8, 4),
    (X - 0.75, 8.2, -5.9, 1.5, 0.5, 2.0),
    (X - 0.6, 10.6, -1.8, 1.2, 2.6, 1.4),
    (X - 0.3, 12.0, -3.4, 0.6, 1.0, 0.3),
    (X - 0.5, 12.2, -4.0, 1.0, 0.2, 2.2),
    (X - 0.8, 13.4, 0.0, 1.6, 1.8, 3.0),
    (X - 0.9, 12.4, 3.0, 1.8, 3.0, 1.0),
    (X - 0.4, 12.4, 1.2, 0.8, 1.0, 1.8))

# 2. USMC 20mm Anti-Materiel Precision Sniper Rifle
g = "weapon_sniper_amr"
add(g, (X - 1.2, 12.8, -12.0, 2.4, 2.8, 14.0),
    (X - 1.0, 15.6, -14.0, 2.0, 0.6, 16.0),
    (X - 0.8, 16.4, -10.0, 1.6, 1.6, 8.0),
    *disc_z(X, 17.2, -11.0, 1.2, 1.4),
    *disc_z(X, 17.2, -1.4, 1.0, 1.2),
    (X - 0.4, 17.2, -11.2, 0.8, 0.8, 0.2),
    (X - 0.5, 13.8, -34.0, 1.0, 1.0, 22.0),
    (X - 0.9, 13.4, -37.0, 1.8, 1.8, 3.0),
    (X - 1.0, 13.7, -36.4, 2.0, 1.2, 1.8),
    (X - 1.0, 13.2, -22.0, 2.0, 2.0, 10.0),
    (X - 0.4, 16.8, -18.0, 0.8, 1.8, 4.0),
    (X - 0.8, 11.2, -20.0, 1.6, 2.0, 1.4),
    (X - 1.6, 6.0, -20.6, 0.5, 5.4, 0.5),
    (X + 1.1, 6.0, -20.6, 0.5, 5.4, 0.5),
    (X - 0.8, 10.4, -3.0, 1.6, 2.6, 1.4),
    (X - 1.1, 11.6, 2.0, 2.2, 3.4, 2.0))

# 3. 12.7mm Heavy Machine Gun
g = "weapon_machine_gun"
add(g, (X - 1.2, 12.2, -10.0, 2.4, 3.0, 10.0),
    (X - 1.0, 13.4, -24.0, 2.0, 2.0, 14.0),
    *[(X - 1.2, 12.5, z, 2.4, 0.5, 0.8) for z in range(-23, -10, 2)],
    (X - 0.5, 13.5, -28.0, 1.0, 1.0, 4.0),
    *disc_z(X, 14.0, -29.0, 0.9, 1.4),
    (X + 1.4, 10.0, -9.0, 3.4, 4.8, 5.4),
    (X + 1.6, 14.8, -8.6, 3.0, 0.4, 4.6),
    (X + 0.6, 13.8, -7.0, 1.2, 1.2, 1.6),
    *[(X + 0.8 + 0.2 * i, 14.1, -7.2 + 0.4 * i, 0.4, 0.6, 0.3) for i in range(4)],
    (X - 0.7, 9.4, -3.2, 1.4, 2.8, 1.6),
    (X - 1.0, 12.8, 1.0, 2.0, 2.4, 3.4),
    (X - 1.1, 11.8, 4.0, 2.2, 3.6, 0.8))

# 4. M134 Minigun
g = "weapon_minigun_m134"
add(g, *disc_z(X, 14.0, -8.0, 2.4, 8.0),
    *disc_z(X, 14.0, -9.0, 2.2, 1.0),
    *[b for angle in (math.pi * i / 3 for i in range(6)) for b in [
        (X + 1.2 * math.cos(angle) - 0.25, 14.0 + 1.2 * math.sin(angle) - 0.25, -28.0, 0.5, 0.5, 19.0)
    ]],
    *disc_z(X, 14.0, -15.0, 1.6, 0.6),
    *disc_z(X, 14.0, -22.0, 1.6, 0.6),
    *disc_z(X, 14.0, -27.6, 1.6, 0.8),
    (X - 0.6, 16.6, -6.0, 1.2, 2.4, 4.0),
    (X - 0.8, 10.0, -2.0, 1.6, 3.0, 1.8),
    (X + 2.2, 12.4, -6.0, 1.8, 3.2, 2.6))

# 5. Quad Missile Pod
g = "weapon_rocket_launcher"
for cx in (X - 1.6, X + 1.6):
    for cy in (12.6, 15.8):
        add(g, (cx - 1.5, cy - 1.5, -15.0, 3.0, 0.4, 18.0), (cx - 1.5, cy + 1.1, -15.0, 3.0, 0.4, 18.0),
            (cx - 1.5, cy - 1.1, -15.0, 0.4, 2.2, 18.0), (cx + 1.1, cy - 1.1, -15.0, 0.4, 2.2, 18.0),
            (cx - 1.1, cy - 1.1, -13.0, 2.2, 2.2, 0.3),
            (cx - 0.4, cy - 0.4, -13.6, 0.8, 0.8, 0.6))
add(g, *[(X - 3.4, 10.8, z, 6.8, 6.8, 0.6) for z in (-15.6, -6.0, 2.6)],
    (X - 0.4, 17.6, -10.0, 0.8, 1.4, 4.0),
    (X - 0.8, 18.6, -10.6, 1.6, 1.4, 3.0),
    (X - 0.6, 18.8, -10.7, 1.2, 1.0, 0.2),
    (X - 0.7, 8.0, -4.0, 1.4, 2.8, 1.6),
    (X - 1.0, 10.4, -5.0, 2.0, 0.6, 3.6),
    (X + 3.4, 12.0, -4.0, 0.6, 4.0, 3.0))

# 6. Heavy RPG-7
g = "weapon_rpg7_heavy"
add(g,
    *disc_z(X, 14.0, -14.0, 1.0, 20.0),
    *disc_z(X, 14.0, -4.0, 1.2, 8.0),
    *disc_z(X, 14.0, 6.0, 1.5, 2.6),
    *disc_z(X, 14.0, -22.0, 2.6, 8.0),
    *disc_z(X, 14.0, -25.0, 2.0, 3.0),
    (X - 0.4, 13.6, -28.0, 0.8, 0.8, 3.0),
    (X - 0.6, 9.6, -7.0, 1.2, 2.6, 1.4),
    (X - 0.6, 9.6, 0.0, 1.2, 2.6, 1.4),
    (X - 0.5, 15.6, -8.0, 1.0, 1.6, 2.4))

# 7. Mining Drill
g = "tool_mining_drill"
add(g, (X - 2.6, 10.6, -10.0, 5.2, 6.2, 8.0),
    *[(X - 2.8, 10.4, z, 5.6, 6.6, 0.4) for z in (-9.4, -8.2, -7.0, -5.8, -4.6, -3.4)],
    (X - 1.8, 16.8, -9.0, 3.6, 0.6, 6.0),
    (X - 1.2, 9.6, -6.0, 2.4, 1.0, 3.0),
    (X - 0.6, 8.0, -4.0, 1.2, 2.4, 1.6),
    (X + 2.6, 12.0, -8.0, 0.6, 3.0, 4.0),
    *disc_z(X, 13.7, -11.0, 2.6, 1.0),
    *disc_z(X, 13.7, -12.0, 2.0, 0.6))
for i, (rad, ln) in enumerate([(2.2, 3.0), (1.7, 3.0), (1.2, 3.0), (0.75, 2.6), (0.35, 2.4)]):
    z0 = -12.0 - 3.0 * (i + 1) + (3.0 - ln)
    add(g, (X - rad, 13.7 - rad, z0, 2 * rad, 2 * rad, ln))
    for k, (dx, dy) in enumerate([(1, 0), (0, 1), (-1, 0), (0, -1)]):
        f = 0.35
        add(g, (X + dx * rad - f / 2, 13.7 + dy * rad - f / 2, z0 + ln * k / 4, f, f, ln / 4 + 0.3))
add(g, (X - 0.15, 13.55, -28.6, 0.3, 0.3, 1.2))

# 8. Forestry Chainsaw
g = "tool_chainsaw"
add(g, (X - 2.2, 10.4, -9.0, 4.4, 6.2, 7.0),
    *[(X - 2.4, 11.0 + 1.0 * i, -8.6, 4.8, 0.3, 4.0) for i in range(5)],
    (X - 1.6, 16.6, -8.0, 3.2, 1.0, 4.0),
    (X - 0.4, 17.6, -9.0, 0.8, 1.6, 0.6), (X - 0.4, 18.6, -9.0, 0.8, 0.6, 6.0),
    (X + 2.2, 11.4, -7.6, 1.0, 2.0, 3.0),
    (X - 0.6, 8.6, -4.0, 1.2, 2.0, 1.6),
    (X - 1.2, 12.6, -11.0, 2.4, 2.4, 2.0),
    (X - 0.3, 10.4, -29.0, 0.6, 7.0, 18.4),
    *disc_x(X - 0.3, 13.9, -29.0, 3.5, 0.6),
    (X - 1.6, 9.8, -11.0, 3.2, 1.0, 0.6))
for z in range(-29, -10, 1):
    add(g, (X - 0.45, 17.4, z, 0.9, 0.4, 0.5), (X - 0.45, 10.0, z, 0.9, 0.4, 0.5))

# ==================== 8 NEW WEAPONS ====================
# 9. Battle Rifle (7.62mm marksman precision)
g = "weapon_battle_rifle"
add(g,
    (X - 0.9, 13.0, -9.0, 1.8, 2.4, 9.0),
    (X - 0.4, 13.8, -26.0, 0.8, 0.8, 17.0),
    (X - 0.6, 13.6, -28.0, 1.2, 1.2, 2.0),
    (X - 0.6, 9.0, -6.0, 1.2, 4.0, 1.8),
    (X - 0.6, 10.6, -1.8, 1.2, 2.6, 1.4),
    (X - 0.8, 12.8, 0.0, 1.6, 2.6, 3.6),
    (X - 0.6, 16.0, -7.0, 1.2, 1.2, 5.0),
    *disc_z(X, 16.6, -7.8, 0.9, 1.0),
    *disc_z(X, 16.6, -1.8, 0.8, 1.0))

# 10. 30mm Heavy Autocannon
g = "weapon_autocannon_30mm"
add(g,
    (X - 1.4, 12.0, -11.0, 2.8, 3.6, 12.0),
    (X - 1.1, 13.2, -26.0, 2.2, 2.2, 15.0),
    (X - 0.6, 13.7, -32.0, 1.2, 1.2, 6.0),
    (X - 1.3, 13.2, -35.0, 2.6, 2.2, 3.0),
    *disc_x(X - 3.8, 13.0, -7.0, 3.2, 2.4),
    (X - 0.7, 9.2, -3.2, 1.4, 3.0, 1.6),
    (X - 1.2, 12.4, 1.0, 2.4, 3.0, 2.4))

# 11. Tactical Combat Breacher Shotgun
g = "weapon_shotgun_breacher"
add(g,
    (X - 1.0, 12.8, -10.0, 2.0, 2.6, 10.0),
    (X - 0.5, 14.0, -23.0, 1.0, 1.0, 13.0),
    (X - 0.5, 12.6, -21.0, 1.0, 1.0, 11.0),
    (X - 0.8, 12.2, -16.0, 1.6, 1.6, 4.0),
    (X - 0.8, 13.7, -25.0, 1.6, 1.6, 2.0),
    (X - 0.6, 10.4, -2.0, 1.2, 2.6, 1.4),
    (X - 0.8, 15.6, -8.0, 1.6, 0.8, 4.0))

# 12. 40mm Rotary Multi-Grenade Launcher
g = "weapon_grenade_launcher"
add(g,
    (X - 1.1, 12.6, -10.0, 2.2, 2.8, 10.0),
    *disc_z(X, 14.0, -11.0, 2.4, 6.0),
    (X - 0.7, 13.8, -21.0, 1.4, 1.4, 10.0),
    *disc_z(X, 14.5, -22.0, 1.0, 1.0),
    (X - 0.5, 8.4, -16.0, 1.0, 4.0, 1.2),
    (X - 0.6, 9.8, -2.2, 1.2, 2.8, 1.4),
    (X - 1.3, 15.6, -7.0, 0.4, 2.0, 2.0))

# 13. 84mm Recoilless Rifle
g = "weapon_recoilless_rifle"
add(g,
    *disc_z(X, 14.0, -18.0, 1.4, 28.0),
    *disc_z(X, 14.0, 9.0, 2.0, 3.0),
    *disc_z(X, 14.0, -19.0, 2.2, 1.0),
    (X - 1.8, 14.2, -8.0, 1.0, 2.0, 4.0),
    (X - 0.6, 9.6, -2.0, 1.2, 2.8, 1.4),
    (X - 0.6, 9.8, -9.0, 1.2, 2.6, 1.4))

# 14. Guided Heavy ATGM Launcher
g = "weapon_atgm_guided"
add(g,
    (X - 2.0, 11.6, -16.0, 4.0, 4.4, 22.0),
    (X - 1.8, 11.8, -16.4, 3.6, 4.0, 0.6),
    (X - 1.2, 16.2, -8.0, 2.4, 2.0, 4.0),
    *disc_z(X - 0.6, 17.2, -8.6, 0.6, 0.8),
    *disc_z(X + 0.6, 17.2, -8.6, 0.6, 0.8),
    (X - 0.6, 8.6, -4.0, 1.2, 3.0, 1.6),
    (X - 0.6, 9.0, -11.0, 1.2, 2.6, 1.6))

# 15. Heavy Flamethrower
g = "weapon_flamethrower"
add(g,
    (X - 1.0, 12.8, -12.0, 2.0, 2.6, 12.0),
    (X - 0.5, 13.8, -26.0, 1.0, 1.0, 14.0),
    *disc_z(X - 0.8, 10.6, -14.0, 1.0, 8.0),
    *disc_z(X + 0.8, 10.6, -14.0, 1.0, 8.0),
    (X - 0.3, 15.0, -26.6, 0.6, 0.6, 1.4),
    (X - 0.8, 12.0, -18.0, 1.6, 1.6, 4.0),
    (X - 0.6, 10.0, -3.0, 1.2, 2.8, 1.4))

# 16. Tactical Vibro-Blade
g = "weapon_vibro_blade"
add(g,
    (X - 0.5, 11.0, -3.0, 1.0, 2.4, 1.2),
    (X - 1.2, 12.8, -4.2, 2.4, 1.2, 3.6),
    (X - 0.6, 9.8, -3.0, 1.2, 1.2, 1.2),
    (X - 0.3, 13.6, -28.0, 0.6, 1.4, 24.0),
    (X - 0.15, 12.4, -28.0, 0.3, 1.2, 24.0),
    (X - 0.25, 13.0, -30.0, 0.5, 1.6, 2.0),
    (X - 0.4, 14.8, -24.0, 0.8, 0.4, 18.0))

# ==================== ROLE VARIANTS GEOMETRY ====================
# 1. Tactical Police
add("armor_head_police",
    (-2.4, 31.0, -4.8, 4.8, 3.2, 4.0), # Police sensor helmet base
    (-2.3, 33.0, -5.2, 4.6, 1.0, 0.6), # Brow visor cowl
    (-2.2, 34.2, -4.8, 2.0, 1.0, 1.0), # Strobe beacon left (blue)
    (0.2, 34.2, -4.8, 2.0, 1.0, 1.0),  # Strobe beacon right (red)
    (-0.4, 34.2, -5.2, 0.8, 1.0, 1.0), # Siren horn center
    (2.2, 32.5, -2.0, 0.5, 3.5, 0.5))  # Comms antenna

c = "canopy_police"
add(c,
    *round_ring(33.0, 14.0, 9.6, -9.6, 10.4, r=3.0),
    *round_ring(47.0, 2.0, 9.6, -9.6, 10.4, r=3.0, front=False), # Visor slot
    *round_ring(49.0, 6.0, 9.4, -9.0, 10.2, r=3.0),
    *round_ring(55.0, 3.0, 8.0, -6.0, 10.0, r=2.6),
    *round_ring(58.0, 2.0, 6.0, -3.0, 9.8, r=2.2),
    (-4.8, 60.0, -2.0, 9.6, 0.8, 11.0), # Roof plate
    (-6.0, 47.0, -9.4, 12.0, 2.0, 0.3), # Polycarbonate visor pane
    (-4.0, 60.8, 2.0, 2.0, 1.0, 1.4),  # Blue emergency bar
    (2.0, 60.8, 2.0, 2.0, 1.0, 1.4))   # Red emergency bar

add("armor_chest_police",
    (-5.0, 22.0, -6.2, 10.0, 8.0, 1.2), # Main chest plate
    (-4.5, 23.0, -6.8, 3.8, 3.0, 0.7),  # Tactical pouch left
    (0.7, 23.0, -6.8, 3.8, 3.0, 0.7),   # Tactical pouch right
    (-3.5, 17.0, -5.8, 7.0, 4.8, 0.8))  # Abdominal groin flap

add("weapon_riot_shield",
    (4.5, 9.0, -6.5, 6.0, 20.0, 0.8),   # Center shield body
    (10.5, 9.0, -5.7, 1.8, 20.0, 1.2),  # Left curved wing
    (2.7, 9.0, -5.7, 1.8, 20.0, 1.2),   # Right curved wing
    (5.5, 23.0, -6.7, 4.0, 2.0, 0.4),   # Transparent viewport insert
    (2.5, 29.0, -6.5, 10.0, 0.8, 2.0),  # Heavy top strike edge
    (2.5, 8.2, -6.5, 10.0, 0.8, 2.0),   # Bottom strike rim
    (6.0, 16.5, -4.5, 2.0, 2.0, 4.0))   # Forearm clamp bracket

add("weapon_stun_baton",
    (X - 0.5, 11.0, -3.0, 1.0, 5.0, 1.0),  # Rubberized grip handle
    (X - 1.0, 16.0, -3.5, 2.0, 0.6, 2.0),  # Shock guard disc
    (X - 0.4, 16.6, -2.9, 0.8, 16.0, 0.8), # Polycarbonate core shaft
    (X - 0.6, 32.6, -3.1, 1.2, 3.0, 1.2),  # Stun electrode tip
    (X - 0.6, 20.0, -3.1, 1.2, 0.5, 1.2),  # Arc ring 1
    (X - 0.6, 24.0, -3.1, 1.2, 0.5, 1.2),  # Arc ring 2
    (X - 0.6, 28.0, -3.1, 1.2, 0.5, 1.2))  # Arc ring 3

# 2. Disaster Rescue NGO
add("armor_head_rescue",
    (-2.4, 31.0, -4.8, 4.8, 3.2, 4.0),  # Main rescue dome base
    (-2.3, 32.2, -5.2, 1.8, 1.8, 1.2),  # Left floodlight housing
    *disc_z(-1.4, 33.1, -5.3, 0.7, 0.2), # Left floodlight lens
    (0.5, 32.2, -5.2, 1.8, 1.8, 1.2),   # Right floodlight housing
    *disc_z(1.4, 33.1, -5.3, 0.7, 0.2),  # Right floodlight lens
    (-0.6, 31.2, -5.2, 1.2, 1.0, 0.8))  # Infrared thermal life-detector

c = "canopy_rescue"
add(c,
    *round_ring(33.0, 15.0, 9.8, -9.6, 10.4, r=3.2),
    *round_ring(48.0, 5.0, 9.4, -9.0, 10.4, r=3.2),
    *round_ring(53.0, 3.0, 8.4, -7.0, 10.2, r=2.8),
    *round_ring(56.0, 2.4, 7.0, -4.0, 10.2, r=2.2),
    *round_ring(58.4, 2.0, 5.4, -1.0, 10.2, r=1.8),
    (-4.2, 60.4, -0.5, 8.4, 0.6, 10.6), # Roof plate
    (-8.0, 42.0, -9.8, 1.0, 16.0, 1.0), # Crash cage left
    (7.0, 42.0, -9.8, 1.0, 16.0, 1.0),  # Crash cage right
    (-8.0, 50.0, -9.8, 16.0, 1.0, 1.0)) # Crash crossbar

add("armor_chest_rescue",
    (-4.8, 22.0, -6.0, 9.6, 7.5, 1.2),  # Main chest shell
    (-3.8, 23.0, -6.8, 7.6, 4.5, 0.9),  # Paramedic kit container
    (-4.0, 18.0, -5.6, 8.0, 3.8, 0.8))  # Lower crash bumper

add("backpack_rescue",
    *MOUNT,
    *disc_y(-4.0, 24.0, 8.5, 1.5, 13.0),
    (-4.0, 37.0, 8.5, 1.0, 1.0, 1.0),   # Valve top left
    *disc_y(2.5, 24.0, 8.5, 1.5, 13.0),
    (2.5, 37.0, 8.5, 1.0, 1.0, 1.0),    # Valve top right
    *ring_x(-2.5, 28.0, 11.5, 2.0, 5.0), # Winch drum
    (-0.6, 25.0, 12.5, 1.2, 5.0, 1.2),  # Cable guide arm
    (-0.8, 23.5, 12.5, 1.6, 1.5, 1.6))  # Heavy forged steel rescue hook

# 3. Amphibious Assault
add("armor_float_ring",
    (-8.0, 16.0, -8.0, 16.0, 4.0, 3.5), # Front pontoon
    (6.5, 16.0, -8.0, 3.5, 4.0, 16.0),  # Left pontoon
    (-10.0, 16.0, -8.0, 3.5, 4.0, 16.0),# Right pontoon
    (-8.0, 16.0, 4.5, 16.0, 4.0, 3.5),  # Rear pontoon
    *disc_x(-10.8, 18.0, 0.0, 1.0, 1.8),# Flank CO2 canister L
    *disc_x(8.8, 18.0, 0.0, 1.0, 1.8))  # Flank CO2 canister R

# 5. Radar Scout
add("backpack_radar",
    *MOUNT,
    (-0.8, 24.0, 8.0, 1.6, 20.0, 1.6),  # Articulated mast
    (-1.5, 44.0, 7.5, 3.0, 2.0, 2.6),   # Rotator drive gearbox
    (-1.0, 46.0, 7.0, 2.0, 8.0, 1.2),   # Center hub
    (-8.0, 47.0, 6.5, 7.0, 6.0, 0.8),   # Left reflector panel
    (1.0, 47.0, 6.5, 7.0, 6.0, 0.8),    # Right reflector panel
    (-0.6, 49.0, 4.8, 1.2, 1.2, 2.0))   # Feed horn transmitter

# 6. Harbour Fishing Rod
add("weapon_fishing_rod",
    (X - 0.8, 12.0, -3.0, 1.6, 4.0, 1.6), # Mounting collar
    *ring_x(X - 1.2, 14.0, -4.5, 1.8, 2.4),# Winch spool
    (X - 0.5, 16.0, -4.0, 1.0, 12.0, 1.0), # Base rod section
    (X - 0.4, 28.0, -4.0, 0.8, 12.0, 0.8), # Mid telescoping rod
    (X - 0.3, 40.0, -4.0, 0.6, 12.0, 0.6), # Tip carbon rod
    (X - 0.3, 22.0, -4.8, 0.6, 0.6, 0.8),  # Guide ring 1
    (X - 0.3, 34.0, -4.8, 0.6, 0.6, 0.8),  # Guide ring 2
    (X - 0.3, 46.0, -4.8, 0.6, 0.6, 0.8),  # Guide ring 3
    (X - 0.3, 51.5, -4.8, 0.6, 0.6, 0.8),  # Guide ring 4
    (X - 0.5, 48.0, -6.0, 1.0, 1.6, 1.0))  # Bobber tackle

def cube(b, uv):
    return {
        "origin": [round(v, 3) for v in b[:3]],
        "size": [round(max(v, 0.1), 3) for v in b[3:]],
        "uv": uv
    }

# ==================== SEAT & CAPSULE FIT ====================
MODEL_SCALE = 1.8
SEAT_DROP = -6.0
AUTHORED = (0.0, 21.6, 5.1)
SEATED = (0.0, (30.8 * MODEL_SCALE - 10.0) / MODEL_SCALE, 4.3)
HEAD_GROUP = (
    "head", "armor_head", "armor_head_usmc", "armor_head_dome", "armor_head_votoms", "armor_head_hood", "armor_head_polar",
    "armor_head_salvage", "armor_head_shiden", "armor_head_khamsin", "armor_head_riverine", "armor_head_specter", "armor_head_valkyrie",
    "armor_head_police", "armor_head_rescue"
)
CANOPIES = (
    "canopy_usmc", "canopy_cerberus", "canopy_polar", "canopy_hood",
    "canopy_salvage", "canopy_shiden", "canopy_khamsin", "canopy_riverine", "canopy_specter", "canopy_valkyrie",
    "canopy_police", "canopy_rescue"
)

def to_seat(b):
    p = [SEATED[i] + (b[i] - AUTHORED[i]) / MODEL_SCALE for i in range(3)]
    return (*p, *(v / MODEL_SCALE for v in b[3:]))

LEG_FORWARD, LEG_SPREAD, ARM_FORWARD, ARM_SPREAD = 0.9, 0.8, 1.0, 0.12

def limb_boxes(px, py, length, fwd, spread):
    d = (math.copysign(math.cos(fwd) * math.sin(spread), px), -math.cos(fwd) * math.cos(spread), -math.sin(fwd))
    return [(px + d[0] * t - 2.0, 21.6 + py + d[1] * t - 2.0, 5.1 + d[2] * t - 2.0, 4.0, 4.0, 4.0)
            for t in (0.15 * length, 0.4 * length, 0.65 * length, 0.9 * length)]

RIDER = [to_seat(b) for b in (
    (-4.0, 33.6, 3.1, 8.0, 12.0, 4.0),
    (-4.0, 45.6, 1.1, 8.0, 8.0, 8.0),
    *limb_boxes(1.9, 12.0, 12.0, LEG_FORWARD, LEG_SPREAD), *limb_boxes(-1.9, 12.0, 12.0, LEG_FORWARD, LEG_SPREAD),
    *limb_boxes(5.0, 22.0, 10.0, ARM_FORWARD, ARM_SPREAD), *limb_boxes(-5.0, 22.0, 10.0, ARM_FORWARD, ARM_SPREAD))]
LEGS = RIDER[2:10]

def leg_fairing():
    x_out = max(max(abs(b[0]), abs(b[0] + b[3])) for b in LEGS) + 0.3
    y_lo = min(b[1] for b in LEGS) - 0.4
    z_lo = min(b[2] for b in LEGS) - 0.3
    z_hi = max(b[2] + b[5] for b in LEGS)
    hip_y = SEATED[1] + 12.0 / MODEL_SCALE
    return [(x_out, y_lo, z_lo, 0.5, hip_y - y_lo - 0.6, z_hi - z_lo),
            (x_out - 0.2, y_lo - 0.4, z_lo - 0.2, 0.9, 0.5, z_hi - z_lo + 0.2),
            (1.2, y_lo, z_lo - 0.5, x_out - 1.0, 2.6, 0.5),
            (x_out + 0.5, y_lo + 0.8, z_lo + 1.0, 0.2, 0.4, z_hi - z_lo - 2.0)]

def move(bone, dy=0.0, dz=0.0):
    if bone in C:
        C[bone] = [(x, y + dy, z + dz, sx, sy, sz) for x, y, z, sx, sy, sz in C[bone]]

def cap_top(bone, top, zmin, zmax):
    if bone not in C:
        return
    out = []
    for x, y, z, sx, sy, sz in C[bone]:
        if z < zmax and z + sz > zmin and y + sy > top:
            sy = top - y
        if sy > 0.05:
            out.append((x, y, z, sx, sy, sz))
    C[bone] = out

for chest in (
    "armor_chest", "armor_chest_usmc", "armor_chest_cerberus", "armor_chest_polar", "armor_chest_hood",
    "armor_chest_salvage", "armor_chest_shiden", "armor_chest_khamsin", "armor_chest_riverine", "armor_chest_specter", "armor_chest_valkyrie"
):
    for b in leg_fairing():
        C[chest] += [b, mx(b)]

thighs = (min(b[0] for b in LEGS), min(b[1] for b in LEGS), min(b[2] for b in LEGS), 0, 0,
          max(b[2] + b[5] for b in LEGS) - min(b[2] for b in LEGS))

for n in HEAD_GROUP:
    move(n, dy=-3.6, dz=-4.6)
    cap_top(n, thighs[1] - 0.1, thighs[2], thighs[2] + thighs[5])

move("upper_back_seat", SEAT_DROP)

for n in CANOPIES:
    C[n] = [to_seat((x, y + SEAT_DROP, z, sx, sy, sz)) for x, y, z, sx, sy, sz in C[n]]

C["armor_roll_cage"] = [(x, y + SEAT_DROP, z, sx, sy, sz) if y >= 35 else
                        (x, y, z, sx, sy + SEAT_DROP if y + sy > 44 else sy, sz)
                        for x, y, z, sx, sy, sz in C["armor_roll_cage"]]

def overlaps(a, b, eps=0.05):
    return all(a[i] + eps < b[i] + b[i + 3] and b[i] + eps < a[i] + a[i + 3] for i in range(3))

POSED = ("arm", "forearm", "hand", "weapon", "tool", "rifle")
clashes = [(n, b) for n, cubes in C.items() if not any(k in n for k in POSED) and n != "upper_back_seat"
           for b in cubes if any(overlaps(b, r) for r in RIDER) and not (n in CANOPIES and min(b[3:]) >= 1.0 / MODEL_SCALE)]
assert not clashes, "rider clashes: " + ", ".join(f"{n}{tuple(round(v, 1) for v in b)}" for n, b in clashes[:12])

crouch_drop = SEAT_DROP / MODEL_SCALE
crouch_rider = [(r[0], r[1] + crouch_drop, r[2], r[3], r[4], r[5]) for r in RIDER]
crouch_clashes = [(n, b) for n, cubes in C.items() if not any(k in n for k in POSED) and n != "upper_back_seat"
                  for b in cubes if any(overlaps((b[0], b[1] + crouch_drop, b[2], b[3], b[4], b[5]), cr) for cr in crouch_rider)
                  and not (n in CANOPIES and min(b[3:]) >= 1.0 / MODEL_SCALE)]
assert not crouch_clashes, "crouch rider clashes: " + ", ".join(f"{n}{tuple(round(v, 1) for v in b)}" for n, b in crouch_clashes[:12])

AIM_HOLDS = {
    "weapon_assault_rifle": ((-8, 11.9, -1.1), (-5.6, 27.5, -6.8), 0.04, 1.0),
    "weapon_sniper_amr": ((-8, 11.7, -2.3), (-5.6, 27.5, -6.8), 0.04, 1.0),
    "weapon_machine_gun": ((-8, 10.8, -2.4), (-6.4, 22.5, -7.0), 0.04, 1.0),
    "weapon_minigun_m134": ((-8, 11.5, -1.1), (-7.2, 24.0, -7.5), 0.02, 1.0),
    "weapon_rocket_launcher": ((-8, 9.4, -3.2), (-7.6, 28.0, -7.0), 0.02, 1.0),
    "weapon_rpg7_heavy": ((-8, 10.9, 0.7), (-5.8, 27.5, -7.0), 0.04, 1.0),
    # 8 New Weapons
    "weapon_battle_rifle": ((-8, 11.9, -1.1), (-5.6, 27.2, -7.2), 0.04, 1.0),
    "weapon_autocannon_30mm": ((-8, 10.8, -2.4), (-6.5, 23.5, -7.4), 0.03, 0.75),
    "weapon_shotgun_breacher": ((-8, 11.8, -1.2), (-5.8, 26.5, -7.2), 0.04, 1.0),
    "weapon_grenade_launcher": ((-8, 11.2, -1.5), (-6.2, 25.0, -7.3), 0.03, 0.85),
    "weapon_recoilless_rifle": ((-8, 11.0, 0.5), (-5.8, 27.0, -7.2), 0.04, 0.85),
    "weapon_atgm_guided": ((-8, 10.0, -2.0), (-7.0, 27.5, -7.3), 0.02, 0.80),
    "weapon_flamethrower": ((-8, 11.0, -1.8), (-6.4, 24.0, -7.4), 0.03, 0.75),
    "weapon_vibro_blade": ((-8, 12.0, -1.0), (-5.5, 24.0, -7.0), 0.02, 0.50),
    "weapon_stun_baton": ((-8, 12.0, -1.0), (-5.5, 24.0, -7.0), 0.02, 0.50),
    "weapon_fishing_rod": ((-8, 12.0, -1.0), (-5.5, 25.0, -7.0), 0.02, 0.50),
}

gun_head_clashes = []
for w_name, (grip, fist, yaw, pshare) in AIM_HOLDS.items():
    w_cubes = C.get(w_name, [])
    cos_y, sin_y = math.cos(yaw), math.sin(yaw)
    grip_r = (-grip[0], grip[1], grip[2])
    fist_r = (-fist[0], fist[1], fist[2])
    for c in w_cubes:
        pts = []
        for dx in (0, c[3]):
            for dy in (0, c[4]):
                for dz in (0, c[5]):
                    px, py, pz = c[0] + dx, c[1] + dy, c[2] + dz
                    rx, ry, rz = -px - grip_r[0], py - grip_r[1], pz - grip_r[2]
                    rx2 = cos_y * rx + sin_y * rz
                    rz2 = -sin_y * rx + cos_y * rz
                    pts.append((-rx2 - fist_r[0], ry + fist_r[1], rz2 + fist_r[2]))
        gb = (min(p[0] for p in pts), max(p[0] for p in pts),
              min(p[1] for p in pts), max(p[1] for p in pts),
              min(p[2] for p in pts), max(p[2] for p in pts))
        for hb in HEAD_GROUP:
            for hc in C.get(hb, []):
                x2, y2, z2, sx, sy, sz = hc
                if not (gb[1] <= x2 or gb[0] >= x2 + sx or
                        gb[3] <= y2 or gb[2] >= y2 + sy or
                        gb[5] <= z2 or gb[4] >= z2 + sz):
                    gun_head_clashes.append((w_name, hb, c, hc))
assert not gun_head_clashes, "aimed gun clips head armor: " + ", ".join(f"{w} vs {hb}" for w, hb, _, _ in gun_head_clashes[:6])

# ==================== 2D GUILLOTINE PACKER FOR ARMOR CUBES ====================
class GuillotinePacker:
    def __init__(self, rects):
        self.free_rects = list(rects)

    def pack(self, w, h):
        best_idx = -1
        best_short_fit = 999999
        best_long_fit = 999999
        for i, (rx, ry, rw, rh) in enumerate(self.free_rects):
            if w <= rw and h <= rh:
                short_fit = min(rw - w, rh - h)
                long_fit = max(rw - w, rh - h)
                if short_fit < best_short_fit or (short_fit == best_short_fit and long_fit < best_long_fit):
                    best_short_fit = short_fit
                    best_long_fit = long_fit
                    best_idx = i
        if best_idx == -1:
            return None
        rx, ry, rw, rh = self.free_rects.pop(best_idx)
        if rw - w > rh - h:
            r1 = (rx + w, ry, rw - w, h)
            r2 = (rx, ry + h, rw, rh - h)
        else:
            r1 = (rx + w, ry, rw - w, rh)
            r2 = (rx, ry + h, w, rh - h)
        if r1[2] > 0 and r1[3] > 0: self.free_rects.append(r1)
        if r2[2] > 0 and r2[3] > 0: self.free_rects.append(r2)
        return (rx, ry, w, h)

FACTION_UV_REGIONS = {
    "Sand": (
        ["armor_head", "armor_chest", "armor_left_shoulder", "armor_right_shoulder", "armor_left_leg", "armor_right_leg", "armor_left_shin_sand", "armor_right_shin_sand"],
        [(200, 0, 60, 240)]
    ),
    "USMC": (
        ["armor_head_usmc", "armor_chest_usmc", "canopy_usmc", "armor_left_shoulder_usmc", "armor_right_shoulder_usmc", "armor_left_leg_usmc", "armor_right_leg_usmc", "backpack_usmc", "armor_left_shin_usmc", "armor_right_shin_usmc"],
        [(260, 0, 70, 315)]
    ),
    "Cerberus": (
        ["armor_head_dome", "armor_chest_cerberus", "canopy_cerberus", "armor_left_shoulder_cerberus", "armor_right_shoulder_cerberus", "armor_left_leg_cerberus", "armor_right_leg_cerberus", "backpack_cerberus", "armor_left_shin_cerberus", "armor_right_shin_cerberus"],
        [(330, 0, 70, 315)]
    ),
    "Outlander": (
        ["armor_head_hood", "armor_chest_hood", "canopy_hood", "armor_left_shoulder_outlander", "armor_right_shoulder_outlander", "armor_left_leg_outlander", "armor_right_leg_outlander", "armor_left_shin_outlander", "armor_right_shin_outlander"],
        [(400, 165, 60, 150), (340, 315, 80, 85), (200, 240, 60, 75)]
    ),
    "Polar": (
        ["armor_head_polar", "armor_chest_polar", "canopy_polar", "backpack_manpads", "armor_left_shoulder_polar", "armor_right_shoulder_polar", "armor_left_leg_polar", "armor_right_leg_polar", "armor_left_ski", "armor_right_ski", "armor_left_shin_polar", "armor_right_shin_polar"],
        [(460, 0, 52, 315), (420, 315, 92, 85)]
    ),
    # 6 New Factions in 1024 space (512..1024, 0..340)
    "Salvage": (
        ["armor_head_salvage", "armor_chest_salvage", "canopy_salvage", "armor_left_shoulder_salvage", "armor_right_shoulder_salvage", "armor_left_leg_salvage", "armor_right_leg_salvage", "backpack_salvage", "armor_left_shin_salvage", "armor_right_shin_salvage"],
        [(512, 0, 85, 340)]
    ),
    "Shiden": (
        ["armor_head_shiden", "armor_chest_shiden", "canopy_shiden", "armor_left_shoulder_shiden", "armor_right_shoulder_shiden", "armor_left_leg_shiden", "armor_right_leg_shiden", "backpack_shiden", "armor_left_shin_shiden", "armor_right_shin_shiden"],
        [(597, 0, 85, 340)]
    ),
    "Khamsin": (
        ["armor_head_khamsin", "armor_chest_khamsin", "canopy_khamsin", "armor_left_shoulder_khamsin", "armor_right_shoulder_khamsin", "armor_left_leg_khamsin", "armor_right_leg_khamsin", "backpack_khamsin", "armor_left_shin_khamsin", "armor_right_shin_khamsin"],
        [(682, 0, 85, 340)]
    ),
    "Riverine": (
        ["armor_head_riverine", "armor_chest_riverine", "canopy_riverine", "armor_left_shoulder_riverine", "armor_right_shoulder_riverine", "armor_left_leg_riverine", "armor_right_leg_riverine", "backpack_riverine", "armor_left_shin_riverine", "armor_right_shin_riverine"],
        [(767, 0, 85, 340)]
    ),
    "Specter": (
        ["armor_head_specter", "armor_chest_specter", "canopy_specter", "armor_left_shoulder_specter", "armor_right_shoulder_specter", "armor_left_leg_specter", "armor_right_leg_specter", "backpack_specter", "armor_left_shin_specter", "armor_right_shin_specter"],
        [(852, 0, 85, 340)]
    ),
    "Valkyrie": (
        ["armor_head_valkyrie", "armor_chest_valkyrie", "canopy_valkyrie", "armor_left_shoulder_valkyrie", "armor_right_shoulder_valkyrie", "armor_left_leg_valkyrie", "armor_right_leg_valkyrie", "backpack_valkyrie", "armor_left_shin_valkyrie", "armor_right_shin_valkyrie"],
        [(937, 0, 85, 340)]
    ),
    # Role Variants in 1024 space (y >= 660)
    "Police": (
        ["armor_head_police", "canopy_police", "armor_chest_police"],
        [(0, 660, 250, 180)]
    ),
    "Rescue": (
        ["armor_head_rescue", "canopy_rescue", "armor_chest_rescue", "backpack_rescue"],
        [(250, 660, 250, 180)]
    ),
    "Amphibious": (
        ["armor_float_ring"],
        [(500, 660, 250, 180)]
    ),
    "Radar": (
        ["backpack_radar"],
        [(750, 660, 250, 180)]
    ),
    "RoleWeapons": (
        ["weapon_riot_shield", "weapon_stun_baton", "weapon_fishing_rod"],
        [(0, 840, 600, 180)]
    )
}

packed_cube_uvs = {}
packed_manifest = []

for fac_name, (bone_list, free_rects) in FACTION_UV_REGIONS.items():
    packer = GuillotinePacker(free_rects)
    cubes_to_pack = []
    for b_name in bone_list:
        for idx, c in enumerate(C.get(b_name, [])):
            sx, sy, sz = [math.ceil(max(v, 0.1)) for v in c[3:]]
            w = 2 * (sz + sx)
            h = sz + sy
            cubes_to_pack.append((b_name, idx, c, w, h, sx, sy, sz))

    cubes_to_pack.sort(key=lambda item: max(item[3], item[4]), reverse=True)

    for b_name, idx, c, w, h, sx, sy, sz in cubes_to_pack:
        res = packer.pack(w, h)
        assert res is not None, f"Failed to pack cube {idx} of bone {b_name} into {fac_name} UV space"
        u, v, pw, ph = res
        packed_cube_uvs[(b_name, idx)] = [u, v]
        w_x, w_y, w_z = sx, sy, sz
        packed_manifest.append({
            "faction": fac_name,
            "bone": b_name,
            "cube_index": idx,
            "origin": [round(val, 3) for val in c[:3]],
            "size": [round(max(val, 0.1), 3) for val in c[3:]],
            "uv": [u, v],
            "w_uv": w,
            "h_uv": h,
            "faces": {
                "top": [u + w_z, v, u + w_z + w_x, v + w_z],
                "bottom": [u + w_z + w_x, v, u + 2 * w_z + w_x, v + w_z],
                "east": [u, v + w_z, u + w_z, v + w_z + w_y],
                "north": [u + w_z, v + w_z, u + w_z + w_x, v + w_z + w_y],
                "west": [u + w_z + w_x, v + w_z, u + 2 * w_z + w_x, v + w_z + w_y],
                "south": [u + 2 * w_z + w_x, v + w_z, u + 2 * (w_z + w_x), v + w_z + w_y]
            }
        })

MANIFEST_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "packed_armor_uvs.json"))
with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(packed_manifest, f, indent=2)

bones = []
for name, parent, pivot, default_uv in BONES:
    bone = {"name": name}
    if parent:
        bone["parent"] = parent
    bone["pivot"] = pivot
    if name in C:
        bone_cubes = []
        for idx, b in enumerate(C[name]):
            cube_uv = packed_cube_uvs.get((name, idx), default_uv)
            bone_cubes.append(cube(b, cube_uv))
        bone["cubes"] = bone_cubes
    bones.append(bone)

# Verify against baseline_bones.json
BASELINE_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "baseline_bones.json"))
if os.path.exists(BASELINE_PATH):
    with open(BASELINE_PATH, "r", encoding="utf-8") as f:
        baseline_data = json.load(f)
    bone_map = {b["name"]: b for b in bones}
    for item in baseline_data:
        b_name, b_parent, b_pivot = item[0], item[1], item[2]
        assert b_name in bone_map, f"Baseline bone missing: {b_name}"
        assert bone_map[b_name].get("parent") == b_parent, f"Parent mismatch for {b_name}: {bone_map[b_name].get('parent')} vs {b_parent}"
        assert bone_map[b_name].get("pivot") == b_pivot, f"Pivot mismatch for {b_name}: {bone_map[b_name].get('pivot')} vs {b_pivot}"
    print(f"Verified all {len(baseline_data)} baseline bones match baseline_bones.json perfectly.")

geo = {
    "format_version": "1.12.0",
    "minecraft:geometry": [{
        "description": {
            "identifier": "geometry.exoframe",
            "texture_width": 1024,
            "texture_height": 1024,
            "visible_bounds_width": 4.5,
            "visible_bounds_height": 4.8,
            "visible_bounds_offset": [0, 1.5, 0]
        },
        "bones": bones
    }]
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(geo, f, indent=2)

total_cubes = sum(len(v) for v in C.values())
print(f"Generated {total_cubes} cubes across {len(bones)} bones into {OUT} (packed {len(packed_manifest)} armor cubes)")
