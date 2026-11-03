"""Builds exoframe.geo.json: the OBSOLETE-style exoframe (boxy open cockpit tub, plantigrade legs, exposed hydraulics,
rear power pack) plus every armor set (tools/armor_sets/<set_id>.py), weapons, validation and the UV manifest.

Pipeline: build_exoframe_geo.py -> build_exoframe_anims.py -> generate_high_fidelity_textures.py
          -> scratch/build_weapon_textures_and_uvs.py (repacks weapon UVs into y 736+ and paints them).
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from armor_sets import load_all                       # noqa: E402
from armor_sets._common import *                       # noqa: E402,F401,F403  (primitives, Anchors, rider envelope)

HERE = os.path.dirname(__file__)
OUT = os.path.normpath(os.path.join(HERE, "..", "src/main/resources/assets/obsolete/geo/exoframe.geo.json"))

# Bone hierarchy: (name, parent, pivot, default uv). Pivots are final; joints are the animation contract.
BONES = [
    ('root', None, [0, 0, 0], None),
    ('pelvis', 'root', [0, 18, 0], [0, 0]),
    ('pelvis_wheel', 'pelvis', [0, 16.8, 3.6], [50, 0]),
    ('torso', 'pelvis', [0, 20, 0], [0, 50]),
    ('upper_back_seat', 'torso', [0, 25, 3.5], [80, 50]),
    ('head', 'torso', [0, 32, -1], [160, 0]),
    ('armor_head', 'head', [0, 32, -1], [200, 0]),
    ('armor_head_usmc', 'head', [0, 32, -1], [260, 0]),
    ('armor_head_dome', 'head', [0, 32, -1], [330, 0]),
    ('armor_head_votoms', 'head', [0, 32, -1], [400, 0]),
    ('armor_head_hood', 'head', [0, 32, -1], [400, 170]),
    ('armor_chest', 'torso', [0, 20, 0], [200, 50]),
    ('armor_chest_usmc', 'torso', [0, 20, 0], [260, 50]),
    ('armor_chest_cerberus', 'torso', [0, 20, 0], [330, 50]),
    ('armor_chest_hood', 'torso', [0, 20, 0], [400, 220]),
    ('armor_roll_cage', 'torso', [0, 20, 0], [0, 240]),
    ('backpack_cargo', 'torso', [0, 24, 8], [80, 240]),
    ('backpack_ammo', 'torso', [0, 24, 8], [140, 240]),
    ('backpack_usmc', 'torso', [0, 24, 8], [260, 220]),
    ('backpack_cerberus', 'torso', [0, 24, 8], [330, 220]),
    ('backpack_missile_pod', 'torso', [0, 32, 2], [400, 100]),
    ('left_arm', 'torso', [9.0, 31.0, -0.5], [0, 130]),
    ('armor_left_shoulder', 'left_arm', [9.0, 31.0, -0.5], [200, 120]),
    ('armor_left_shoulder_usmc', 'left_arm', [9.0, 31.0, -0.5], [260, 120]),
    ('armor_left_shoulder_cerberus', 'left_arm', [9.0, 31.0, -0.5], [330, 120]),
    ('left_forearm', 'left_arm', [9.0, 24.6, -0.5], [50, 130]),
    ('left_hand', 'left_forearm', [9.0, 16.6, -0.5], [90, 130]),
    ('right_arm', 'torso', [-9.0, 31.0, -0.5], [0, 130]),
    ('armor_right_shoulder', 'right_arm', [-9.0, 31.0, -0.5], [200, 120]),
    ('armor_right_shoulder_usmc', 'right_arm', [-9.0, 31.0, -0.5], [260, 120]),
    ('armor_right_shoulder_cerberus', 'right_arm', [-9.0, 31.0, -0.5], [330, 120]),
    ('armor_right_shoulder_red', 'right_arm', [-9.0, 31.0, -0.5], [400, 50]),
    ('right_forearm', 'right_arm', [-9.0, 24.6, -0.5], [50, 130]),
    ('right_hand', 'right_forearm', [-9.0, 16.6, -0.5], [90, 130]),
    ('right_hand_weapon_mount', 'right_hand', [-7.0, 16.0, -2.0], None),
    ('weapon_assault_rifle', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [0, 320]),
    ('weapon_sniper_amr', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [80, 320]),
    ('weapon_machine_gun', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [180, 320]),
    ('weapon_minigun_m134', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [280, 320]),
    ('weapon_rocket_launcher', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [0, 400]),
    ('weapon_rpg7_heavy', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [120, 400]),
    ('tool_mining_drill', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [240, 400]),
    ('tool_chainsaw', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [360, 400]),
    ('left_thigh', 'pelvis', [4.5, 17, 0], [0, 180]),
    ('armor_left_leg', 'left_thigh', [4.5, 17, 0], [200, 170]),
    ('armor_left_leg_usmc', 'left_thigh', [4.5, 17, 0], [260, 170]),
    ('armor_left_leg_cerberus', 'left_thigh', [4.5, 17, 0], [330, 170]),
    ('left_shin', 'left_thigh', [4.5, 9, -2.8], [50, 180]),
    ('left_knee_wheel', 'left_shin', [6.8, 9, -2.5], [90, 180]),
    ('left_foot', 'left_shin', [4.5, 2, 2.2], [130, 180]),
    ('right_thigh', 'pelvis', [-4.5, 17, 0], [0, 180]),
    ('armor_right_leg', 'right_thigh', [-4.5, 17, 0], [200, 170]),
    ('armor_right_leg_usmc', 'right_thigh', [-4.5, 17, 0], [260, 170]),
    ('armor_right_leg_cerberus', 'right_thigh', [-4.5, 17, 0], [330, 170]),
    ('right_shin', 'right_thigh', [-4.5, 9, -2.8], [50, 180]),
    ('right_knee_wheel', 'right_shin', [-6.8, 9, -2.5], [90, 180]),
    ('right_foot', 'right_shin', [-4.5, 2, 2.2], [130, 180]),
    ('armor_head_polar', 'head', [0, 32, -1], [462, 0]),
    ('armor_chest_polar', 'torso', [0, 20, 0], [462, 30]),
    ('backpack_manpads', 'torso', [0, 32, 2], [200, 240]),
    ('armor_left_shoulder_polar', 'left_arm', [9.0, 31.0, -0.5], [462, 70]),
    ('armor_right_shoulder_polar', 'right_arm', [-9.0, 31.0, -0.5], [462, 70]),
    ('armor_left_shoulder_outlander', 'left_arm', [9.0, 31.0, -0.5], [430, 170]),
    ('armor_right_shoulder_outlander', 'right_arm', [-9.0, 31.0, -0.5], [430, 170]),
    ('armor_left_leg_polar', 'left_thigh', [4.5, 17, 0], [462, 100]),
    ('armor_right_leg_polar', 'right_thigh', [-4.5, 17, 0], [462, 100]),
    ('armor_left_leg_outlander', 'left_thigh', [4.5, 17, 0], [430, 240]),
    ('armor_right_leg_outlander', 'right_thigh', [-4.5, 17, 0], [430, 240]),
    ('canopy_usmc', 'torso', [0, 20, 0], [260, 50]),
    ('canopy_cerberus', 'torso', [0, 20, 0], [330, 50]),
    ('canopy_polar', 'torso', [0, 20, 0], [462, 30]),
    ('canopy_hood', 'torso', [0, 20, 0], [400, 220]),
    ('armor_left_shin_sand', 'left_shin', [4.5, 9, -2.8], [200, 0]),
    ('armor_right_shin_sand', 'right_shin', [-4.5, 9, -2.8], [200, 0]),
    ('armor_left_shin_usmc', 'left_shin', [4.5, 9, -2.8], [260, 0]),
    ('armor_right_shin_usmc', 'right_shin', [-4.5, 9, -2.8], [260, 0]),
    ('armor_left_shin_cerberus', 'left_shin', [4.5, 9, -2.8], [330, 0]),
    ('armor_right_shin_cerberus', 'right_shin', [-4.5, 9, -2.8], [330, 0]),
    ('armor_left_shin_polar', 'left_shin', [4.5, 9, -2.8], [462, 0]),
    ('armor_right_shin_polar', 'right_shin', [-4.5, 9, -2.8], [462, 0]),
    ('armor_left_shin_outlander', 'left_shin', [4.5, 9, -2.8], [400, 0]),
    ('armor_right_shin_outlander', 'right_shin', [-4.5, 9, -2.8], [400, 0]),
    ('armor_left_ski', 'left_foot', [4.5, 2, 2.2], [462, 130]),
    ('armor_right_ski', 'right_foot', [-4.5, 2, 2.2], [462, 130]),
    ('armor_head_salvage', 'head', [0, 32, -1], [512, 0]),
    ('armor_chest_salvage', 'torso', [0, 20, 0], [512, 30]),
    ('canopy_salvage', 'torso', [0, 20, 0], [512, 30]),
    ('armor_left_shoulder_salvage', 'left_arm', [9.0, 31.0, -0.5], [512, 80]),
    ('armor_right_shoulder_salvage', 'right_arm', [-9.0, 31.0, -0.5], [512, 80]),
    ('armor_left_leg_salvage', 'left_thigh', [4.5, 17, 0], [512, 120]),
    ('armor_right_leg_salvage', 'right_thigh', [-4.5, 17, 0], [512, 120]),
    ('armor_left_shin_salvage', 'left_shin', [4.5, 9, -2.8], [512, 0]),
    ('armor_right_shin_salvage', 'right_shin', [-4.5, 9, -2.8], [512, 0]),
    ('backpack_salvage', 'torso', [0, 24, 8], [512, 160]),
    ('armor_head_shiden', 'head', [0, 32, -1], [597, 0]),
    ('armor_chest_shiden', 'torso', [0, 20, 0], [597, 30]),
    ('canopy_shiden', 'torso', [0, 20, 0], [597, 30]),
    ('armor_left_shoulder_shiden', 'left_arm', [9.0, 31.0, -0.5], [597, 80]),
    ('armor_right_shoulder_shiden', 'right_arm', [-9.0, 31.0, -0.5], [597, 80]),
    ('armor_left_leg_shiden', 'left_thigh', [4.5, 17, 0], [597, 120]),
    ('armor_right_leg_shiden', 'right_thigh', [-4.5, 17, 0], [597, 120]),
    ('armor_left_shin_shiden', 'left_shin', [4.5, 9, -2.8], [597, 0]),
    ('armor_right_shin_shiden', 'right_shin', [-4.5, 9, -2.8], [597, 0]),
    ('backpack_shiden', 'torso', [0, 24, 8], [597, 160]),
    ('armor_head_khamsin', 'head', [0, 32, -1], [682, 0]),
    ('armor_chest_khamsin', 'torso', [0, 20, 0], [682, 30]),
    ('canopy_khamsin', 'torso', [0, 20, 0], [682, 30]),
    ('armor_left_shoulder_khamsin', 'left_arm', [9.0, 31.0, -0.5], [682, 80]),
    ('armor_right_shoulder_khamsin', 'right_arm', [-9.0, 31.0, -0.5], [682, 80]),
    ('armor_left_leg_khamsin', 'left_thigh', [4.5, 17, 0], [682, 120]),
    ('armor_right_leg_khamsin', 'right_thigh', [-4.5, 17, 0], [682, 120]),
    ('armor_left_shin_khamsin', 'left_shin', [4.5, 9, -2.8], [682, 0]),
    ('armor_right_shin_khamsin', 'right_shin', [-4.5, 9, -2.8], [682, 0]),
    ('backpack_khamsin', 'torso', [0, 24, 8], [682, 160]),
    ('armor_head_riverine', 'head', [0, 32, -1], [767, 0]),
    ('armor_chest_riverine', 'torso', [0, 20, 0], [767, 30]),
    ('canopy_riverine', 'torso', [0, 20, 0], [767, 30]),
    ('armor_left_shoulder_riverine', 'left_arm', [9.0, 31.0, -0.5], [767, 80]),
    ('armor_right_shoulder_riverine', 'right_arm', [-9.0, 31.0, -0.5], [767, 80]),
    ('armor_left_leg_riverine', 'left_thigh', [4.5, 17, 0], [767, 120]),
    ('armor_right_leg_riverine', 'right_thigh', [-4.5, 17, 0], [767, 120]),
    ('armor_left_shin_riverine', 'left_shin', [4.5, 9, -2.8], [767, 0]),
    ('armor_right_shin_riverine', 'right_shin', [-4.5, 9, -2.8], [767, 0]),
    ('backpack_riverine', 'torso', [0, 24, 8], [767, 160]),
    ('armor_head_specter', 'head', [0, 32, -1], [852, 0]),
    ('armor_chest_specter', 'torso', [0, 20, 0], [852, 30]),
    ('canopy_specter', 'torso', [0, 20, 0], [852, 30]),
    ('armor_left_shoulder_specter', 'left_arm', [9.0, 31.0, -0.5], [852, 80]),
    ('armor_right_shoulder_specter', 'right_arm', [-9.0, 31.0, -0.5], [852, 80]),
    ('armor_left_leg_specter', 'left_thigh', [4.5, 17, 0], [852, 120]),
    ('armor_right_leg_specter', 'right_thigh', [-4.5, 17, 0], [852, 120]),
    ('armor_left_shin_specter', 'left_shin', [4.5, 9, -2.8], [852, 0]),
    ('armor_right_shin_specter', 'right_shin', [-4.5, 9, -2.8], [852, 0]),
    ('backpack_specter', 'torso', [0, 24, 8], [852, 160]),
    ('armor_head_valkyrie', 'head', [0, 32, -1], [937, 0]),
    ('armor_chest_valkyrie', 'torso', [0, 20, 0], [937, 30]),
    ('canopy_valkyrie', 'torso', [0, 20, 0], [937, 30]),
    ('armor_left_shoulder_valkyrie', 'left_arm', [9.0, 31.0, -0.5], [937, 80]),
    ('armor_right_shoulder_valkyrie', 'right_arm', [-9.0, 31.0, -0.5], [937, 80]),
    ('armor_left_leg_valkyrie', 'left_thigh', [4.5, 17, 0], [937, 120]),
    ('armor_right_leg_valkyrie', 'right_thigh', [-4.5, 17, 0], [937, 120]),
    ('armor_left_shin_valkyrie', 'left_shin', [4.5, 9, -2.8], [937, 0]),
    ('armor_right_shin_valkyrie', 'right_shin', [-4.5, 9, -2.8], [937, 0]),
    ('backpack_valkyrie', 'torso', [0, 24, 8], [937, 160]),
    ('weapon_battle_rifle', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [0, 520]),
    ('weapon_autocannon_30mm', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [120, 520]),
    ('weapon_shotgun_breacher', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [240, 520]),
    ('weapon_grenade_launcher', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [360, 520]),
    ('weapon_recoilless_rifle', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [480, 520]),
    ('weapon_atgm_guided', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [600, 520]),
    ('weapon_flamethrower', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [720, 520]),
    ('weapon_vibro_blade', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [840, 520]),
    ('armor_head_police', 'head', [0, 32, -1], [0, 660]),
    ('canopy_police', 'torso', [0, 20, 0], [0, 660]),
    ('armor_chest_police', 'torso', [0, 20, 0], [0, 660]),
    ('weapon_riot_shield', 'left_hand', [9.0, 16.6, -0.5], [0, 840]),
    ('weapon_stun_baton', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [120, 840]),
    ('armor_head_rescue', 'head', [0, 32, -1], [250, 660]),
    ('canopy_rescue', 'torso', [0, 20, 0], [250, 660]),
    ('armor_chest_rescue', 'torso', [0, 20, 0], [250, 660]),
    ('backpack_rescue', 'torso', [0, 24, 8], [250, 660]),
    ('armor_float_ring', 'pelvis', [0, 17, 0], [500, 660]),
    ('backpack_radar', 'torso', [0, 24, 8], [750, 660]),
    ('weapon_fishing_rod', 'right_hand_weapon_mount', [-7.0, 16.0, -2.0], [240, 840]),
]

C = {}      # bone -> [box]
MAT = {}    # frame bone -> [material] (parallel to C[bone]); armor and weapons have no entry


def add(bone, *boxes):
    C.setdefault(bone, []).extend(boxes)


def F(bone, mat, *boxes):
    """Frame cube(s) with a paint material (see generate_high_fidelity_textures.FRAME_MATERIALS)."""
    C.setdefault(bone, []).extend(boxes)
    MAT.setdefault(bone, []).extend([mat] * len(boxes))


def FS(bone, mat, *boxes):
    F(bone, mat, *sym(*boxes))


def seg(x0, x1, p0, p1, d, zoff=0.0, t0=0.0, t1=None):
    """Box from x0..x1 laid along the sagittal segment p0 -> p1 ((y, z) points), depth d, offset zoff across the
    segment (+ = behind), covering distances t0..t1 from p0. Rotates about p0, so a box authored on the bone whose
    pivot is p0 stays glued to that joint."""
    dy, dz = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dy, dz)
    t1 = L if t1 is None else t1
    rx = math.degrees(math.atan2(-dz, -dy))
    return (x0, p0[0] - t1, p0[1] + zoff - d / 2, x1 - x0, t1 - t0, d, 0.0, p0[0], p0[1], rx, 0.0, 0.0)


# ==================== FRAME: PELVIS ====================
P = "pelvis"
F(P, "steel", (-2.8, 11.6, -2.2, 5.6, 3.0, 4.8))                     # final-drive gearbox under the cockpit tub
F(P, "dark", (-3.0, 11.2, -2.6, 6.0, 0.4, 5.6))                      # skid plate
F(P, "steel", (-2.4, 12.2, 2.6, 4.8, 2.4, 4.2))                      # rear cradle carrying the power pack
F(P, "hazard", (-1.6, 12.2, -3.0, 3.2, 1.6, 0.8))                    # front tow eye / bump stop
FS(P, "dark", (2.8, 12.0, -1.8, 0.3, 2.2, 4.0))                      # gearbox cooling ribs
FS(P, "steel", (2.8, 13.0, -1.4, 0.8, 3.0, 2.8))                     # hip brackets
FS(P, "steel", *disc_x(6.3, 17.0, 0.0, 1.4, 0.5))                    # outboard hip bearing caps
FS(P, "chrome", *disc_x(6.8, 17.0, 0.0, 0.5, 0.3))                   # hip axle nut

W = "pelvis_wheel"   # alternator drum slung under the power pack (bone kept for compatibility, not animated)
F(W, "steel", *disc_x(-1.6, 13.0, 4.6, 1.4, 3.2))
F(W, "dark", *disc_x(-1.7, 13.0, 4.6, 0.6, 3.4))
F(W, "rubber", (-0.4, 12.2, 3.0, 0.8, 0.5, 2.0))                     # drive belt

# ==================== FRAME: TORSO (open cockpit tub, collar, roll hoop, power pack) ====================
T = "torso"
F(T, "steel", (-3.2, 14.6, -3.3, 6.4, 0.6, 9.3))                     # floor pan
FS(T, "paint", (3.3, 14.6, -3.3, 0.7, 7.0, 9.3))                     # tub side walls (pilot climbs in over these)
FS(T, "dark", (3.2, 21.4, -3.5, 1.0, 0.5, 9.7))                      # welded top rail
FS(T, "steel", *[(4.0, 15.2, z, 0.3, 6.0, 0.5) for z in (-2.4, 0.6, 3.6)])   # wall stiffeners
FS(T, "hazard", (4.0, 15.2, -3.2, 0.35, 1.2, 0.8))                   # step plate
F(T, "paint", (-3.2, 14.6, -3.7, 6.4, 4.2, 0.4))                     # foot well front plate
F(T, "dark", rot_box(-3.0, 18.8, -3.7, 6.0, 1.6, 1.2, 0, 18.8, -3.1, 20, 0, 0))   # instrument dash
F(T, "glass", (-1.8, 19.4, -3.95, 1.0, 0.7, 0.2), (0.8, 19.4, -3.95, 1.0, 0.7, 0.2))  # gauges
FS(T, "dark", (2.2, 19.6, -2.9, 0.4, 2.6, 0.4))                      # control sticks
FS(T, "rubber", (2.1, 22.0, -3.0, 0.6, 0.8, 0.6))                    # stick grips
F(T, "paint", (-3.6, 14.6, 6.0, 7.2, 11.6, 0.8))                     # rear bulkhead behind the seat (below the head sweep)
FS(T, "steel", (3.6, 14.6, 5.4, 0.9, 14.6, 1.4))                     # rear uprights
FS(T, "steel", (4.4, 21.4, -3.4, 0.9, 7.4, 1.0))                     # front uprights
FS(T, "paint", (4.5, 28.6, -3.4, 1.2, 1.8, 13.4))                    # shoulder collar side beams
F(T, "paint", (-5.7, 28.6, 8.6, 11.4, 1.8, 1.4))                     # collar back beam (backpacks bolt to its rear)
FS(T, "dark", (4.3, 30.4, -3.0, 1.6, 0.4, 12.8))                     # collar cap strip
FS(T, "paint", (4.6, 28.6, -2.2, 1.6, 4.6, 3.4))                     # shoulder towers
FS(T, "steel", *disc_x(5.6, 31.0, -0.5, 2.2, 1.8))                   # shoulder bearing housings
FS(T, "dark", (5.0, 33.0, -2.4, 1.2, 0.6, 3.8))                      # tower top plates
# roll hoop over the pilot
FS(T, "steel", (3.9, 30.4, 8.8, 0.7, 5.0, 0.7), (3.9, 30.4, -2.6, 0.7, 5.0, 0.7), (3.9, 35.4, -2.6, 0.7, 0.7, 12.1))
F(T, "steel", (-4.6, 35.4, 8.8, 9.2, 0.7, 0.7), (-4.6, 35.4, -2.6, 9.2, 0.7, 0.7))
FS(T, "dark", (2.0, 34.5, -2.9, 1.4, 0.9, 0.9))                      # work lamp housings
FS(T, "lamp", (2.1, 34.6, -3.0, 1.2, 0.7, 0.1))
F(T, "dark", (4.0, 36.1, 9.1, 0.2, 5.0, 0.2))                        # whip antenna
FS(T, "lamp", (5.2, 30.4, 9.6, 0.5, 0.5, 0.5))                       # amber rear markers
# cable runs: power pack -> collar -> shoulder, with a sagging loop over the shoulder joint
FS(T, "rubber", (5.6, 21.6, 6.4, 0.5, 7.0, 0.5), (5.7, 29.0, 1.2, 0.5, 0.5, 5.6),
   rot_box(6.0, 28.2, -0.2, 0.5, 0.5, 1.6, 6.25, 28.45, 0.6, -25, 0, 0),
   rot_box(6.0, 28.0, -1.7, 0.5, 0.5, 1.6, 6.25, 28.25, -0.9, 20, 0, 0))
# power pack (diesel-electric unit) and exhaust
F(T, "paint", (-3.8, 14.8, 6.8, 7.6, 6.2, 5.2))
F(T, "dark", *[(-4.0, 15.4 + i * 1.1, 7.4, 8.0, 0.4, 4.2) for i in range(5)])   # cooling fins
F(T, "dark", (-3.2, 15.4, 12.0, 6.4, 5.0, 0.4))                      # radiator
F(T, "steel", *[(-3.0, 15.8 + i * 0.9, 12.4, 6.0, 0.3, 0.2) for i in range(5)])  # radiator guard slats
F(T, "steel", (-3.6, 21.0, 7.0, 7.2, 0.4, 4.8))                      # top deck
F(T, "hazard", (-2.0, 18.0, 12.45, 1.2, 1.2, 0.2))                   # fuel cut-off handle
FS(T, "exhaust", (3.8, 17.0, 10.2, 1.1, 1.0, 1.0), (4.9, 17.0, 10.2, 1.0, 14.0, 1.0))   # exhaust stacks
FS(T, "paint", (5.9, 22.0, 10.0, 0.3, 7.0, 1.4))                     # perforated heat shields
FS(T, "dark", (4.75, 31.0, 10.05, 1.3, 0.4, 1.3))                    # rain caps
FS(T, "steel", (4.9, 28.0, 9.8, 1.0, 0.5, 0.6))                      # stack brackets to the collar

# ==================== FRAME: PILOT SEAT (counter-rotated with the pilot by ExoframeModel) ====================
S_ = "upper_back_seat"
F(S_, "seat", (-2.4, 19.6, 1.2, 4.8, 0.8, 4.6), (-2.4, 20.4, 5.5, 4.8, 7.0, 0.6), (-1.6, 27.8, 6.6, 3.2, 2.6, 0.5))
FS(S_, "seat", (2.2, 20.4, 3.6, 0.5, 4.0, 2.4))                      # side bolsters
FS(S_, "harness", (1.2, 22.0, 5.35, 0.5, 5.2, 0.15))                 # harness straps
FS(S_, "steel", (2.5, 19.2, 1.0, 0.3, 0.4, 5.2))                     # seat rails

# ==================== FRAME: ARMS (left; right is mirrored) ====================
ARM = {
    "left_arm": [
        ("steel", disc_x(7.2, 31.0, -0.5, 2.3, 3.4)),                # shoulder actuator drum
        ("dark", disc_x(10.6, 31.0, -0.5, 1.6, 0.5)),                # drum end cap
        ("chrome", disc_x(11.1, 31.0, -0.5, 0.6, 0.3)),
        ("paint", [(7.9, 25.4, -1.7, 2.2, 4.0, 2.4)]),               # upper arm beam
        ("paint", [(10.1, 25.8, -1.5, 0.4, 3.2, 2.0)]),              # bolted outer slab
        ("dark", [(7.5, 25.8, -1.5, 0.4, 3.2, 2.0)]),
        ("steel", [(8.5, 25.6, -2.9, 1.0, 4.0, 1.0)]),               # elbow ram sleeve
        ("dark", [(8.3, 29.4, -3.0, 1.4, 0.8, 1.2)]),                # ram clevis
        ("rubber", [(8.8, 25.0, 0.7, 0.5, 5.0, 0.5)]),               # hydraulic line
        ("steel", [(7.5, 23.4, -1.8, 0.5, 2.6, 2.6), (10.0, 23.4, -1.8, 0.5, 2.6, 2.6)]),   # elbow fork
    ],
    "left_forearm": [
        ("dark", disc_x(8.0, 24.6, -0.5, 1.5, 2.0)),                 # elbow hub
        ("paint", [(7.4, 17.6, -2.3, 3.2, 5.8, 3.8)]),               # heavy forearm box
        ("paint", [(7.7, 18.2, -2.7, 2.6, 4.8, 0.4)]),               # bolted front slab
        ("chrome", [(8.75, 22.5, -2.65, 0.5, 3.3, 0.5)]),            # elbow ram rod (slides in the upper-arm sleeve)
        ("steel", [(10.6, 18.4, -1.8, 0.4, 4.2, 2.8)]),              # outer rib
        ("rubber", [(7.0, 18.0, 0.6, 0.4, 5.0, 0.5)]),               # hose
        ("dark", [(7.6, 16.8, -2.0, 2.8, 0.8, 3.2)]),                # wrist cuff
        ("hazard", [(10.62, 22.6, -1.6, 0.3, 0.6, 2.4)]),
    ],
    "left_hand": [
        ("dark", disc_x(8.2, 16.4, -0.5, 1.0, 1.6)),                 # wrist knuckle
        ("steel", [(7.7, 13.2, -2.0, 2.6, 2.6, 3.0)]),               # palm block
        ("paint", [(10.3, 13.4, -1.8, 0.4, 2.2, 2.6)]),              # back-of-hand plate
        ("dark", [(8.1, 11.6, z, 1.8, 1.6, 0.85) for z in (-1.9, -0.9, 0.1)]),   # proximal finger segments
        ("steel", [(7.9, 10.3, z, 1.6, 1.4, 0.85) for z in (-1.9, -0.9, 0.1)]),  # distal finger segments
        ("dark", [(7.1, 12.2, -1.6, 0.6, 2.4, 1.0)]),                # thumb
        ("steel", [(7.0, 11.4, -1.6, 0.6, 1.0, 1.0)]),
    ],
}

# ==================== FRAME: LEGS (left; plantigrade, right is mirrored) ====================
HIP, KNEE, ANKLE = (17.0, 0.0), (9.0, -2.8), (2.0, 2.2)
LEG = {
    "left_thigh": [
        ("dark", disc_x(3.4, 17.0, 0.0, 2.0, 2.8)),                  # hip hub
        ("paint", [seg(3.5, 5.8, HIP, KNEE, 3.2, 0.0, 0.8, 7.6)]),   # thigh beam
        ("paint", [seg(3.4, 5.8, HIP, KNEE, 0.5, -1.55, 1.6, 6.6)]),  # front slab
        ("paint", [seg(5.6, 6.1, HIP, KNEE, 2.4, 0.0, 1.2, 6.6)]),   # outer bolt-on slab
        ("dark", [seg(3.3, 3.6, HIP, KNEE, 2.0, 0.0, 1.2, 6.6)]),
        ("steel", [seg(4.1, 5.1, HIP, KNEE, 1.0, 1.9, 0.8, 5.2)]),   # knee ram sleeve (behind the thigh)
        ("chrome", [seg(4.35, 4.85, HIP, KNEE, 0.5, 1.9, 5.0, 7.8)]),  # ram rod
        ("rubber", [seg(3.3, 3.7, HIP, KNEE, 0.4, 1.3, 0.5, 7.0)]),  # hydraulic hose
    ],
    "left_shin": [
        ("dark", disc_x(3.3, 9.0, -2.8, 2.0, 3.0)),                  # knee hub
        ("steel", disc_x(6.3, 9.0, -2.8, 1.2, 0.3)),
        ("paint", [seg(3.5, 5.7, KNEE, ANKLE, 2.8, 0.0, 0.4, 7.9)]),  # thick shin
        ("paint", [seg(3.4, 5.8, KNEE, ANKLE, 1.0, -2.0, -1.4, 1.6)]),  # knee cap
        ("steel", [seg(4.1, 5.1, KNEE, ANKLE, 1.0, -1.9, 1.8, 5.0)]),  # ankle ram sleeve (front of the shin)
        ("chrome", [seg(4.35, 4.85, KNEE, ANKLE, 0.5, -1.9, 4.8, 7.4)]),
        ("dark", [seg(3.7, 5.5, KNEE, ANKLE, 0.5, 1.6, 1.0, 6.5)]),  # calf plate
        ("rubber", [seg(5.7, 6.1, KNEE, ANKLE, 0.4, 0.8, 0.5, 7.2)]),
        ("hazard", [seg(3.45, 5.75, KNEE, ANKLE, 0.2, -2.55, -0.9, 0.0)]),
    ],
    "left_knee_wheel": [                                             # outboard knee roller
        ("rubber", disc_x(6.6, 9.0, -2.8, 1.5, 0.8)),
        ("steel", disc_x(6.55, 9.0, -2.8, 0.7, 0.9)),
    ],
    "left_foot": [
        ("dark", disc_x(3.3, 2.0, 2.2, 1.5, 2.6)),                   # ankle hub
        ("rubber", [(2.1, 0.0, -6.6, 4.8, 0.9, 11.3)]),              # sole
        ("paint", [(2.4, 0.9, -5.4, 4.2, 1.4, 9.6)]),                # foot block
        ("paint", [rot_box(2.5, 0.4, -6.9, 4.0, 1.6, 0.5, 4.5, 0.4, -6.6, 30, 0, 0)]),   # raked toe plate
        ("hazard", [(2.5, 2.3, -5.4, 4.0, 0.2, 1.2)]),
        ("steel", [(2.6, 0.9, 3.4, 3.8, 1.6, 1.4)]),                 # heel block
        ("steel", [(2.2, 0.9, 0.4, 0.4, 2.6, 3.2), (6.4, 0.9, 0.4, 0.4, 2.6, 3.2)]),   # ankle yoke plates
        ("dark", [(6.9, 0.1, z, 0.2, 0.6, 0.8) for z in (-5.0, -2.0, 1.0)]),
        ("dark", [(1.9, 0.1, z, 0.2, 0.6, 0.8) for z in (-5.0, -2.0, 1.0)]),
    ],
}
for table in (ARM, LEG):
    for left, parts in table.items():
        right = left.replace("left", "right")
        for mat, boxes in parts:
            F(left, mat, *boxes)
            F(right, mat, *[mx(b) for b in boxes])
FRAME_BONES = list(MAT)

# ==================== ARMOR SETS (tools/armor_sets/<set_id>.py) ====================
BONE_NAMES = [b[0] for b in BONES]
SETS = load_all()
OWNER = {}
for mod in SETS:
    for bone, boxes in mod.build(A).items():
        assert bone in BONE_NAMES, f"{mod.SET_ID} builds unknown bone {bone}"
        assert bone not in OWNER, f"{bone} built by both {OWNER[bone]} and {mod.SET_ID}"
        assert bone not in MAT, f"{mod.SET_ID} writes into frame bone {bone}"
        OWNER[bone] = mod.SET_ID
        C[bone] = list(boxes)


# ==================== WEAPONS & TOOLS (mount at right_hand_weapon_mount) ====================
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

# the riot shield hangs off left_hand, authored around the pre-Phase-1 wrist (x 7, y 17.6)
C["weapon_riot_shield"] = shift(C["weapon_riot_shield"], (2.0, -1.0, 0.0))

# ==================== RIDER ENVELOPE & CLEARANCE CHECKS ====================
def overlaps(a, b, eps=0.05):
    return all(a[i] + eps < b[i] + b[i + 3] and b[i] + eps < a[i] + a[i + 3] for i in range(3))


def aabb(b):
    """World AABB of a (possibly rotated) box."""
    if len(b) < 12:
        return b[:6]
    x, y, z, sx, sy, sz, px, py, pz, rx, ry, rz = b
    rx, ry, rz = map(math.radians, (rx, ry, rz))
    cx, snx, cy, sny, cz, snz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    pts = []
    for dx in (0, sx):
        for dy in (0, sy):
            for dz in (0, sz):
                v = (x + dx - px, y + dy - py, z + dz - pz)
                v = (v[0], v[1] * cx - v[2] * snx, v[1] * snx + v[2] * cx)
                v = (v[0] * cy + v[2] * sny, v[1], -v[0] * sny + v[2] * cy)
                v = (v[0] * cz - v[1] * snz, v[0] * snz + v[1] * cz, v[2])
                pts.append((v[0] + px, v[1] + py, v[2] + pz))
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    return (*lo, *(hi[i] - lo[i] for i in range(3)))


HEAD_GROUP = tuple(n for n in BONE_NAMES if n == "head" or n.startswith("armor_head"))
CANOPIES = tuple(n for n in BONE_NAMES if n.startswith("canopy_"))
POSED = ("arm", "forearm", "hand", "weapon", "tool", "rifle")
FULL_RIDER = [RIDER[0]] + head_pitch_boxes() + RIDER[2:]
CLEARANCE_REQ = 1.0
INFLATED_RIDER = [(r[0] - CLEARANCE_REQ, r[1] - CLEARANCE_REQ, r[2] - CLEARANCE_REQ,
                   r[3] + 2 * CLEARANCE_REQ, r[4] + 2 * CLEARANCE_REQ, r[5] + 2 * CLEARANCE_REQ) for r in FULL_RIDER]
crouch_drop = SEAT_DROP / MODEL_SCALE
lowered = lambda boxes, dy: [(b[0], b[1] + dy, b[2], b[3], b[4], b[5]) for b in boxes]

# 1. canopies keep >= 1 px around the pilot (head swept +-30 deg), standing and crouched
for dy in (0.0, crouch_drop):
    inf = lowered(INFLATED_RIDER, dy)
    bad = [(n, b) for n in CANOPIES for b in C[n] if any(overlaps(lowered([aabb(b)], dy)[0], r, eps=0.001) for r in inf)]
    assert not bad, f"canopy clearance < 1 px (dy {dy}): " + ", ".join(f"{n}{tuple(round(v, 1) for v in b[:6])}" for n, b in bad[:12])

# 2. nothing static (frame or armor) clips the seated pilot, standing or crouched
for dy in (0.0, crouch_drop):
    rider = lowered(RIDER, dy)
    bad = [(n, b) for n, cubes in C.items() if not any(k in n for k in POSED) and n != "upper_back_seat" and n not in CANOPIES
           for b in cubes if any(overlaps(lowered([aabb(b)], dy)[0], r) for r in rider)]
    assert not bad, f"frame clashes (dy {dy}): " + ", ".join(f"{n}{tuple(round(v, 1) for v in b[:6])}" for n, b in bad[:12])

# 3. the frame (roll hoop, collar, lamps) also clears the pilot's head pitched +-30 deg
pitched = head_pitch_boxes()
bad = [(n, b) for n in FRAME_BONES if n != "upper_back_seat" and not any(k in n for k in POSED)
       for b in C[n] if any(overlaps(aabb(b), r) for r in pitched)]
assert not bad, "frame clips the pitched pilot head: " + ", ".join(f"{n}{tuple(round(v, 1) for v in b[:6])}" for n, b in bad[:12])

# 4. canopy rear cover >= 95 % standing, crouched and in every clip
torso_box, head_box = RIDER[0], RIDER[1]
x0, x1 = torso_box[0], torso_box[0] + torso_box[3]
y0, y1 = torso_box[1], head_box[1] + head_box[4]
zback = max(torso_box[2] + torso_box[5], head_box[2] + head_box[5])


def rear_cover(cubes, dy=0.0, n=40):
    hit = sum(any(c[0] <= x0 + (i + .5) * (x1 - x0) / n <= c[0] + c[3] and
                  c[1] <= y0 + dy + (j + .5) * (y1 - y0) / n <= c[1] + c[4] and
                  c[2] >= zback - 0.2 for c in cubes)
              for i in range(n) for j in range(n))
    return hit / (n * n)


anim_json_path = os.path.join(HERE, "../src/main/resources/assets/obsolete/animations/exoframe.animation.json")
clips = json.load(open(anim_json_path)).get("animations", {}) if os.path.exists(anim_json_path) else {}
for name in CANOPIES:
    for label, dy in [("bind", 0.0), ("crouch", crouch_drop)] + [(c, crouch_drop if "crouch" in c else 0.0) for c in clips if "death" not in c]:
        cov = rear_cover(lowered(C[name], dy), dy=dy)
        assert cov >= 0.95, f"{name} rear cover < 95% in {label}: {cov:.1%}"

AIM_HOLDS = {
    "weapon_assault_rifle": ((-8, 11.9, -1.1), (-5.6, 27.5, -6.8), 0.04, 1.0),
    "weapon_sniper_amr": ((-8, 11.7, -2.3), (-5.6, 27.5, -6.8), 0.04, 1.0),
    "weapon_machine_gun": ((-8, 10.8, -2.4), (-6.0, 22.5, -7.6), 0.04, 1.0),
    "weapon_minigun_m134": ((-8, 11.5, -1.1), (-6.8, 23.0, -7.6), 0.04, 0.6),
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
                x2, y2, z2, sx, sy, sz = hc[:6]
                if not (gb[1] <= x2 or gb[0] >= x2 + sx or
                        gb[3] <= y2 or gb[2] >= y2 + sy or
                        gb[5] <= z2 or gb[4] >= z2 + sz):
                    gun_head_clashes.append((w_name, hb, c, hc))
assert not gun_head_clashes, "aimed gun clips head armor: " + ", ".join(f"{w} vs {hb}" for w, hb, _, _ in gun_head_clashes[:6])

# ==================== UV PACKING ====================
class GuillotinePacker:
    def __init__(self, rects):
        self.free_rects = list(rects)

    def pack(self, w, h):
        best, best_s, best_l = -1, 1e9, 1e9
        for i, (rx, ry, rw, rh) in enumerate(self.free_rects):
            if w <= rw and h <= rh:
                s, l = min(rw - w, rh - h), max(rw - w, rh - h)
                if s < best_s or (s == best_s and l < best_l):
                    best, best_s, best_l = i, s, l
        if best == -1:
            return None
        rx, ry, rw, rh = self.free_rects.pop(best)
        if rw - w > rh - h:
            r1, r2 = (rx + w, ry, rw - w, h), (rx, ry + h, rw, rh - h)
        else:
            r1, r2 = (rx + w, ry, rw - w, rh), (rx, ry + h, w, rh - h)
        self.free_rects += [r for r in (r1, r2) if r[2] > 0 and r[3] > 0]
        return (rx, ry, w, h)


# Frame atlas: the old inner-frame block plus the free band right of the ordnance strip.
FRAME_RECTS = [(0, 0, 200, 240), (512, 340, 512, 180)]
REGIONS = [(m.UV_REGION[0], list(getattr(m, "PACKED_BONES", None) or [b for b in m.build(A)]), m.UV_REGION[1])
           for m in SETS if m.UV_REGION]
REGIONS.append(("Frame", FRAME_BONES, FRAME_RECTS))
REGIONS.append(("RoleWeapons", ["weapon_riot_shield", "weapon_stun_baton", "weapon_fishing_rod"], [(0, 840, 600, 180)]))

packed_cube_uvs, packed_manifest = {}, []
for fac_name, bone_list, free_rects in REGIONS:
    packer = GuillotinePacker(free_rects)
    todo = []
    for b_name in bone_list:
        for idx, c in enumerate(C.get(b_name, [])):
            sx, sy, sz = [math.ceil(max(v, 0.1)) for v in c[3:6]]
            todo.append((b_name, idx, c, 2 * (sz + sx), sz + sy, sx, sy, sz))
    todo.sort(key=lambda t: max(t[3], t[4]), reverse=True)
    for b_name, idx, c, w, h, sx, sy, sz in todo:
        res = packer.pack(w, h)
        assert res is not None, f"Failed to pack cube {idx} of bone {b_name} into {fac_name} UV space"
        u, v = res[0], res[1]
        packed_cube_uvs[(b_name, idx)] = [u, v]
        entry = {"faction": fac_name, "bone": b_name, "cube_index": idx,
                 "origin": [round(val, 3) for val in c[:3]], "size": [round(max(val, 0.1), 3) for val in c[3:6]],
                 "uv": [u, v], "w_uv": w, "h_uv": h,
                 "faces": {"top": [u + sz, v, u + sz + sx, v + sz], "bottom": [u + sz + sx, v, u + 2 * sz + sx, v + sz],
                           "east": [u, v + sz, u + sz, v + sz + sy], "north": [u + sz, v + sz, u + sz + sx, v + sz + sy],
                           "west": [u + sz + sx, v + sz, u + 2 * sz + sx, v + sz + sy],
                           "south": [u + 2 * sz + sx, v + sz, u + 2 * (sz + sx), v + sz + sy]}}
        if fac_name == "Frame":
            entry["material"] = MAT[b_name][idx]
        packed_manifest.append(entry)

with open(os.path.join(HERE, "packed_armor_uvs.json"), "w", encoding="utf-8") as f:
    json.dump(packed_manifest, f, indent=2)


def cube(b, uv):
    out = {"origin": [round(v, 3) for v in b[:3]], "size": [round(max(v, 0.1), 3) for v in b[3:6]]}
    if len(b) >= 12:
        out["pivot"] = [round(v, 3) for v in b[6:9]]
        out["rotation"] = [round(v, 3) for v in b[9:12]]
    out["uv"] = uv
    return out


bones = []
for name, parent, pivot, default_uv in BONES:
    bone = {"name": name}
    if parent:
        bone["parent"] = parent
    bone["pivot"] = pivot
    if name in C:
        bone["cubes"] = [cube(b, packed_cube_uvs.get((name, i), default_uv)) for i, b in enumerate(C[name])]
    bones.append(bone)

# ==================== VALIDATION ====================
with open(os.path.join(HERE, "baseline_bones.json"), "r", encoding="utf-8") as f:
    baseline_data = json.load(f)
bone_map = {b["name"]: b for b in bones}
for b_name, b_parent, b_pivot in (item[:3] for item in baseline_data):
    assert b_name in bone_map, f"Baseline bone missing: {b_name}"
    assert bone_map[b_name].get("parent") == b_parent, f"Parent mismatch for {b_name}"
    assert bone_map[b_name].get("pivot") == b_pivot, f"Pivot mismatch for {b_name}: {bone_map[b_name]['pivot']} vs {b_pivot}"
assert len(bone_map) == len(bones), "duplicate bone names"

TW = TH = 1024
for b in bones:
    for c in b.get("cubes", []):
        raw = c["size"]
        assert min(raw) >= 0.1, f"zero-size cube in {b['name']}: {raw}"
        sx, sy, sz = (math.ceil(v) for v in raw)
        u, v = c["uv"]
        assert 0 <= u and u + 2 * (sx + sz) <= TW and 0 <= v and v + sz + sy <= TH, f"UV out of bounds in {b['name']}: {c['uv']} {raw}"
for name, cubes in C.items():
    for b in cubes:
        assert min(b[3:6]) > 0.0, f"degenerate authored cube in {name}: {b}"

# every bone the Java code or the animations name must exist
import re  # noqa: E402
JAVA = os.path.join(HERE, "../src/main/java/com/obsolete")
java_refs = set()
for rel in ("client/model/ExoframeModel.java", "client/model/ExoframeArmIK.java", "registry/ExoframeVariantRegistry.java",
            "client/debug/ClientAutoTest.java", "client/renderer/ExoframeRenderer.java", "client/renderer/ExoframeRiderPose.java"):
    src = open(os.path.join(JAVA, rel), encoding="utf-8").read()
    for call in re.findall(r"List\.of\(([^)]*)\)", src):
        java_refs |= set(re.findall(r'"([a-z0-9_]+)"', call))
    java_refs |= set(re.findall(r'(?:bone|apply|getBone|setHidden|BONES\.add|_BONES\.add)\(\s*"([a-z0-9_]+)"', src))
    java_refs |= set(re.findall(r'registerWeapon\([^,]+,\s*"([a-z0-9_]+)"', src))
KNOWN_MISSING = {"tool_cultivator_plow"}   # registered weapon with no model yet (pre-existing; setHidden is null-safe)
missing = sorted(r for r in java_refs - set(bone_map) - KNOWN_MISSING if not r.endswith("_"))   # "x_" + id is a prefix
assert not missing, f"bones referenced in Java but missing from the geo: {missing}"
anim_refs = {bn for clip in clips.values() for bn in clip.get("bones", {})}
assert not (anim_refs - set(bone_map)), f"animated bones missing: {sorted(anim_refs - set(bone_map))}"

geo = {"format_version": "1.12.0",
       "minecraft:geometry": [{"description": {"identifier": "geometry.exoframe", "texture_width": TW, "texture_height": TH,
                                               "visible_bounds_width": 4.5, "visible_bounds_height": 4.8,
                                               "visible_bounds_offset": [0, 1.5, 0]}, "bones": bones}]}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(geo, f, indent=2)
json.load(open(OUT))   # round-trip parse

frame_cubes = sum(len(C[n]) for n in FRAME_BONES)
print(f"Verified {len(baseline_data)} baseline bones, {len(java_refs)} Java bone refs, {len(anim_refs)} animated bones.")
print(f"Generated {sum(len(v) for v in C.values())} cubes ({frame_cubes} frame) across {len(bones)} bones into {OUT} "
      f"(packed {len(packed_manifest)} cubes)")
