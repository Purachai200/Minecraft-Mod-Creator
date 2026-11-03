# Exoframe armor sets

`tools/build_exoframe_geo.py` builds the bare frame, then imports every module listed in `SET_IDS` in `__init__.py` and writes
the geometry that module returns into the existing bones of `exoframe.geo.json`.

## Module interface

Each `tools/armor_sets/<set_id>.py` defines:

| Name | Meaning |
|---|---|
| `SET_ID` | the module id, a string |
| `UV_REGION` | `(faction_name, [(u, v, w, h), ...])`: atlas rectangles the generator packs this set's cubes into. `None` means the set uses the bones' default UVs. `faction_name` is the key the texture generator's `faction_livery()` paints. |
| `PACKED_BONES` (optional) | packs only these bones; every other bone the module builds keeps its default UV |
| `build(a: Anchors) -> dict[str, list[box]]` | maps a bone name to its cubes |
| `paint(x, y, camo_id, n_fine, n_med, n_coarse) -> (r, g, b, a) or None` (optional) | paints texels inside this module's `UV_REGION` rects for camo 0..6 (noise args are 0..1 value noise at fine/medium/coarse scale); return `None` to fall back to the shared `faction_livery()`. Called once per texel by `generate_high_fidelity_textures.py`. |

Rules:
- Bone names must already exist in `BONES` in the generator, which are the Java contract. You can't add, rename or re-parent a bone, and a module can't write into a frame bone. The generator checks all three.
- Each bone belongs to exactly one module. The generator rejects a bone built by two modules.
- A box is `(x, y, z, sx, sy, sz)`, or `(x, y, z, sx, sy, sz, px, py, pz, rx, ry, rz)` with its own pivot and rotation in degrees. Coordinates are **final model space**, not bone-local. 16 units = 1 block, forward is -Z, and the mech's left is +X.
- Build the left side, then mirror it with `mx()`, `sym()` or `mirror_pair()`.
- Import only from `._common`. It holds the primitives (`disc_x/y/z`, `ring_x`, `piston_y`, `stepped`, `round_ring`, `rot_box`, `shift`), the legacy archetype builders (`build_box_canopy`, `build_chest_glacis`, `build_throat_head`, `build_box_pauldron`, `build_leg_cuisse`, `build_shin_greave`, `MOUNT`), the fit helpers and `assemble()`. Treat `_common.py` as read-only. If you need a different silhouette, copy the builder into your own module.
- Run `python3 tools/build_exoframe_geo.py`. These checks must still pass:
  - the pilot clash check, standing and crouched
  - canopy clearance of at least 1 px around the pilot's head pitched ±30°
  - canopy rear cover of at least 95% in every clip
  - aimed guns must not clip head armor
  - UV bounds, no zero-size cubes, and the baseline pivots
- After the generator, run `python3 tools/generate_high_fidelity_textures.py`, then `python3 ../scratch/build_weapon_textures_and_uvs.py` from the `Obsolete/` folder.

## Attach bones and anchors (`Anchors`, final model space, left side; mirror x for the right)

| Slot | Attach bone(s) | Anchor / pivot | Frame envelope to clear |
|---|---|---|---|
| Head sensor | `head` | `head` (0, 32, -1) | throat ahead of the pilot. Pilot head is y 27.6–32.5, z 0.2–8.5 when pitched. |
| Chest / canopy / roll cage | `torso` | `torso` (0, 20, 0) | `torso_env` (-5.9, 14.5, -3.7)–(5.9, 36, 13). Roll hoop: \|x\| 3.9–4.6, top y 36.1. Collar: y 28.6–30.8. |
| Pauldrons | `left_arm` / `right_arm` | `shoulder_l` (9, 31, -0.5) | `upper_arm_env_l` (7.2, 23, -2.8)–(10.8, 33.5, 1.8) |
| Thigh armor | `left_thigh` / `right_thigh` | `hip_l` (4.5, 17, 0) | `thigh_env_l` (3.0, 8, -3.4)–(6.2, 19.2, 2.6) |
| Shin greaves | `left_shin` / `right_shin` | `knee_l` (4.5, 9, -2.8) | `shin_env_l` (3.0, 1.2, -4.8)–(6.1, 11, 3.8). Ankle at (4.5, 2, 2.2). |
| Foot add-ons (skis) | `left_foot` / `right_foot` | `ankle_l` (4.5, 2, 2.2) | `foot_env_l` (2.1, 0, -6.6)–(6.9, 4, 4.7). Sole sits at y 0. |
| Backpack | `torso` (pivot (0, 24, 8)) | `back_mount` (0, 21.6, 9.8): the rear face of the collar back beam | power pack z 6.8–12.8, y 14.8–21.4. Exhaust stacks at \|x\| 4.9–5.9. |
| Shoulder pods | `torso` (pivot (0, 32, 2)) | `pod_mount` | pitched with the aim by `ExoframeModel` |
| Float ring | `pelvis` (pivot (0, 17, 0)) | `float_ring` | — |

Legacy geometry is moved onto the new frame by the fit helpers:

| Helper | What it does |
|---|---|
| `shoulder_fit` | +2 x outward, +1 y |
| `back_fit` | +3 z (`back_mount` minus the legacy 6.8) |
| `head_fit` | legacy pilot-leg trim |
| `seat_space` | pilot-scale canopy authoring |
| `leg_fairing()` | the shin shell that every chest carries |

Phase 1 dropped the old split-toe boot pads from `build_shin_greave`, because the frame now has real flat feet.

## Set ids

| set_id | registry faction | bones |
|---|---|---|
| sand | Sand | armor_head, armor_chest, armor_left/right_shoulder, armor_left/right_leg, armor_left/right_shin_sand |
| usmc | USMC | armor_head_usmc, armor_chest_usmc, canopy_usmc, armor_*_shoulder_usmc, armor_*_leg_usmc, armor_*_shin_usmc, backpack_usmc |
| cerberus | Cerberus | armor_head_dome, armor_chest_cerberus, canopy_cerberus, *_shoulder_cerberus, *_leg_cerberus, *_shin_cerberus, backpack_cerberus |
| votoms | VOTOMS | armor_head_votoms, armor_right_shoulder_red, backpack_missile_pod (the arms item also shows armor_left_shoulder_usmc) |
| outlander | Outlander | armor_head_hood, armor_chest_hood, canopy_hood, *_shoulder_outlander, *_leg_outlander, *_shin_outlander |
| polar | Polar | armor_head_polar, armor_chest_polar, canopy_polar, *_shoulder_polar, *_leg_polar, *_shin_polar, armor_left/right_ski, backpack_manpads |
| salvage, shiden, khamsin, riverine, specter, valkyrie | same name, capitalised | armor_head_X, armor_chest_X, canopy_X, armor_*_shoulder_X, armor_*_leg_X, armor_*_shin_X, backpack_X |
| police | Police | armor_head_police, armor_chest_police, canopy_police |
| rescue | Rescue | armor_head_rescue, armor_chest_rescue, canopy_rescue, backpack_rescue |
| industrial | Industrial | armor_roll_cage |
| amphibious | Amphibious | armor_float_ring |
| utility | (utility slot) | backpack_cargo, backpack_ammo, backpack_radar |

Weapons and tools, including the riot shield, the stun baton and the fishing rod, stay in `build_exoframe_geo.py`.
