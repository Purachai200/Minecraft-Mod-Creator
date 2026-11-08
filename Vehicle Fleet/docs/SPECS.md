# Vehicle Fleet - collider and seat anchors

Model space: nose -Z, +X vehicle left, +Y up, **16 px = 1 block**, ground y=0. Values are px; blocks = px / 16.

Atlas: `textures/entity/<id>.png` is **1024x1024** = 16x16 cells of 64 px (UVs are written for 1024; the painter works on 512 and doubles).
Every cube face maps one texel per model px (2 texels/px in the export) into the cell of its material, so repainting a cell repaints every part using it.

| cell | material | use |
|---|---|---|
| 0 | HULL | weathered military paint (tinted per vehicle), rust drips, chipped edges |
| 1 | BELLY | lower hull / anti-fouling / underbody, heavier grime |
| 2 | GLASS | alpha-0 glazing with streaks (needs translucent render type) |
| 3 | DARK | frames, chassis, hydraulics, greebles |
| 4 / 18 | BLADE / TIP | rotor blades / yellow tip band |
| 5 | WALK | non-skid deck grit with rust bloom |
| 6 | TIRE | tyre rubber |
| 7 | SPIN | bare steel, chrome oleo, cables |
| 9 | SOOT | exhaust staining | 
| 10 | GRILLE | radiator / intake grille |
| 11 / 12 / 17 | RED / GREEN / WHITE | lamps, binders, markings |
| 13 | WINDOW | opaque lit windows (ship superstructure) |
| 14 | INTER | interior panels and seats |
| 15 | RAMP | **diamond tread plate** (bed liners, ramps) |
| 16 | DOOR | doors and hatches, same tint as HULL |

## Heavy Tactical Technical 4x4 (`technical_4x4`) - Tier 1
Payload: **1 Obsolete Exoframe only**
Player seat capacity: **2**

Liveries: `technical_4x4.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-21.8, 21.8], y [0.3, 85.6], z [-58, 66]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `cargo_deck`: [-14, 24, 5] -> [14, 24, 55]  =  [-0.88, 1.5, 0.31] -> [0.88, 1.5, 3.44] (size [1.75, 0.0, 3.12] blocks, give the slab ~0.25 block thickness under the surface)
- `tailgate_open`: [-14, 24, 56.6] -> [14, 24, 70.6]  =  [-0.88, 1.5, 3.54] -> [0.88, 1.5, 4.41] (size [1.75, 0.0, 0.87] blocks, give the slab ~0.25 block thickness under the surface)

Seat / slot anchors (px):

- `driver`: [7.5, 29, -13.5]
- `passenger`: [-7.5, 29, -13.5]
- `gunner_stand`: [0, 24, 30]

## Heavy 6x6 Off-Road Hauler (`ural_6x6`) - Tier 2
Payload: **1 kneeling Titan or 2 Exoframes**
Player seat capacity: **3**

Liveries: `ural_6x6.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-28.5, 28.5], y [0.4, 124.6], z [-78, 84.1]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `cargo_deck`: [-19, 32, -7] -> [19, 32, 69]  =  [-1.19, 2.0, -0.44] -> [1.19, 2.0, 4.31] (size [2.38, 0.0, 4.75] blocks, give the slab ~0.25 block thickness under the surface)
- `tailgate_open`: [-19, 32, 71] -> [19, 32, 85]  =  [-1.19, 2.0, 4.44] -> [1.19, 2.0, 5.31] (size [2.38, 0.0, 0.88] blocks, give the slab ~0.25 block thickness under the surface)

Seat / slot anchors (px):

- `driver`: [-10, 47, -25]
- `passenger`: [10, 47, -25]
- `centre`: [0, 47, -25]

## Mil Mi-17 Hip Heavy Tactical Transport (`mi17_hip`) - Tier 2
Payload: **1 Titan or 2 Exoframes, underslung on the ventral rig (also walkable troop hold)**
Player seat capacity: **14**

Liveries: `mi17_hip.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-67.3, 152], y [-37.0, 170.0], z [-114.0, 200.0]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `cabin_deck`: [-18, 34, -37] -> [18, 34, 63]  =  [-1.12, 2.12, -2.31] -> [1.12, 2.12, 3.94] (size [2.25, 0.0, 6.25] blocks, give the slab ~0.25 block thickness under the surface)
- `flight_deck`: [-13, 34, -96] -> [13, 34, -38]  =  [-0.81, 2.12, -6.0] -> [0.81, 2.12, -2.38] (size [1.62, 0.0, 3.62] blocks, give the slab ~0.25 block thickness under the surface)
- `sling_envelope_hang_zone`: [-24, -90, -40] -> [24, -30, 40]  =  [-1.5, -5.62, -2.5] -> [1.5, -1.88, 2.5] (size [3.0, 3.75, 5.0] blocks, give the slab ~0.25 block thickness under the surface)

Seat / slot anchors (px):

- `pilot`: [8, 40, -70]
- `copilot`: [-8, 40, -70]
- `troop_row_left_x`: 16
- `troop_row_right_x`: -16
- `sling_attach`: [0, -28, 0]
- `titan_hang_point`: [0, -60, 0]
- Sling rig is modelled deployed (bar at y=-30) but hidden (scale 0) in `idle`/`fly`/`cargo_open`; play `sling` only while a Titan/Exoframe is hooked, so an empty Mi-17 shows nothing below the belly.
- Blades are modelled drooped; `fly` levels them (-3 / -5 deg on the droop bones) while `main_rotor` spins.

## Civilian Coaster Tramp Freighter (`coaster_freighter`) - Tier 3
Payload: **2 Titans in the well, or 4-6 Exoframes (well + walkable deck perimeter)**
Player seat capacity: **4**

Liveries: `coaster_freighter.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-68.6, 68.6], y [0, 254.6], z [-260, 258]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `well_floor`: [-41, 28, -176] -> [41, 28, 36]  =  [-2.56, 1.75, -11.0] -> [2.56, 1.75, 2.25] (size [5.12, 0.0, 13.25] blocks, give the slab ~0.25 block thickness under the surface)
- `main_deck_port_walkway`: [45, 44, -196] -> [58, 44, 100]  =  [2.81, 2.75, -12.25] -> [3.62, 2.75, 6.25] (size [0.81, 0.0, 18.5] blocks, give the slab ~0.25 block thickness under the surface)
- `main_deck_starboard_walkway`: [-58, 44, -196] -> [-45, 44, 100]  =  [-3.62, 2.75, -12.25] -> [-2.81, 2.75, 6.25] (size [0.81, 0.0, 18.5] blocks, give the slab ~0.25 block thickness under the surface)
- `forecastle`: [-40, 58, -258] -> [40, 58, -202]  =  [-2.5, 3.62, -16.12] -> [2.5, 3.62, -12.62] (size [5.0, 0.0, 3.5] blocks, give the slab ~0.25 block thickness under the surface)
- `poop_deck`: [-44, 44, 190] -> [44, 44, 254]  =  [-2.75, 2.75, 11.88] -> [2.75, 2.75, 15.88] (size [5.5, 0.0, 4.0] blocks, give the slab ~0.25 block thickness under the surface)
- `bridge_wings`: [-68, 118, 128] -> [68, 118, 162]  =  [-4.25, 7.38, 8.0] -> [4.25, 7.38, 10.12] (size [8.5, 0.0, 2.12] blocks, give the slab ~0.25 block thickness under the surface)
- `tier1_floor`: [-42, 44, 101] -> [42, 44, 187]  =  [-2.62, 2.75, 6.31] -> [2.62, 2.75, 11.69] (size [5.25, 0.0, 5.38] blocks, give the slab ~0.25 block thickness under the surface)
- `tier2_floor`: [-36, 80, 113] -> [36, 80, 187]  =  [-2.25, 5.0, 7.06] -> [2.25, 5.0, 11.69] (size [4.5, 0.0, 4.62] blocks, give the slab ~0.25 block thickness under the surface)
- `bridge_floor`: [-32, 116, 125] -> [32, 116, 169]  =  [-2.0, 7.25, 7.81] -> [2.0, 7.25, 10.56] (size [4.0, 0.0, 2.75] blocks, give the slab ~0.25 block thickness under the surface)
- `lower_deck`: [-40, 8, 44] -> [40, 8, 236]  =  [-2.5, 0.5, 2.75] -> [2.5, 0.5, 14.75] (size [5.0, 0.0, 12.0] blocks, give the slab ~0.25 block thickness under the surface)

Walkable interior:

- lower deck (floor y=8): engine room 44..124, stair hatch 124..156 (x 8..22), crew bunks 156..236
- tier 1: cabins, stairs, mess; tier 2: officers; tier 3: bridge with wing doors

Seat / slot anchors (px):

- `helm`: [10, 116, 140]
- `titan_slot_a`: [0, 28, -120]
- `titan_slot_b`: [0, 28, -20]
- Hull keel y=0; design waterline y~24 (low freeboard 20 px). Coamings are 10 px above the main deck, hold them as solid collider walls.
- Walkable surfaces are decks only - superstructure tiers need their own collider if you want interior access.

## Mil Mi-26 Halo Strategic Heavy-Lift (`mi26_halo`) - Tier 3
Payload: **up to 3 Titans (or 2 Titans + 2 Exoframes) on the ventral spreader bar; hold fits 12 troops**
Player seat capacity: **28**

Liveries: `mi26_halo.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-101.0, 214], y [-57, 255.0], z [-171.0, 300.0]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `cabin_deck`: [-27, 51, -56] -> [27, 51, 95]  =  [-1.69, 3.19, -3.5] -> [1.69, 3.19, 5.94] (size [3.38, 0.0, 9.44] blocks, give the slab ~0.25 block thickness under the surface)
- `flight_deck`: [-20, 51, -144] -> [20, 51, -56]  =  [-1.25, 3.19, -9.0] -> [1.25, 3.19, -3.5] (size [2.5, 0.0, 5.5] blocks, give the slab ~0.25 block thickness under the surface)
- `sling_hang_zone`: [-40, -150, -130] -> [40, -50, 130]  =  [-2.5, -9.38, -8.12] -> [2.5, -3.12, 8.12] (size [5.0, 6.25, 16.25] blocks, give the slab ~0.25 block thickness under the surface)

Seat / slot anchors (px):

- `pilot`: [12, 60, -105]
- `copilot`: [-12, 60, -105]
- `flight_engineer`: [-14, 60, -96]
- `titan_hang_a`: [0, -118, -84]
- `titan_hang_b`: [0, -118, 0]
- `titan_hang_c`: [0, -118, 84]
- Everything is the Mi-17 geometry x1.5, then: 8-blade rotor, 5-blade tail rotor, 3-slot heavy sling. Rig hidden (scale 0) in every clip except `sling`.
- Belly is at y=42 px; the hover height of the Java entity decides how far the slung Titans clear the ground.

## Heavy 6x6 Recovery Truck (`recovery_6x6`) - Tier 2
Payload: **recovers downed Titans/vehicles with a 40-degree lattice crane + front winch; carries no deck cargo**
Player seat capacity: **3**

Liveries: `recovery_6x6.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-28.5, 28.5], y [0.4, 167.9], z [-88, 122.0]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `subframe_deck`: [-19, 31.5, -8] -> [19, 31.5, 70]  =  [-1.19, 1.97, -0.5] -> [1.19, 1.97, 4.38] (size [2.38, 0.0, 4.88] blocks, give the slab ~0.25 block thickness under the surface)

Seat / slot anchors (px):

- `driver`: [-10, 47, -25]
- `passenger`: [10, 47, -25]
- `centre`: [0, 47, -25]
- `winch_hook`: [0, 22, -80]
- `crane_tip_rest`: [0, 129.7, 117.5]
- `outriggers_down` slides the beams out 14 px and drops the jacks 12 px; `crane_work` luffs the boom 20 deg and slews the turntable 30 deg.

## M1165 Up-Armoured Humvee (`humvee_m1165`) - Tier 1
Payload: **1 Obsolete Exoframe (short bed)**
Player seat capacity: **5**

Liveries: `humvee_m1165.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-22.6, 22.6], y [0.3, 86.4], z [-52, 47]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `cargo_deck`: [-14, 24, 17] -> [14, 24, 43]  =  [-0.88, 1.5, 1.06] -> [0.88, 1.5, 2.69] (size [1.75, 0.0, 1.62] blocks, give the slab ~0.25 block thickness under the surface)
- `tailgate_open`: [-14, 24, 45] -> [14, 24, 57]  =  [-0.88, 1.5, 2.81] -> [0.88, 1.5, 3.56] (size [1.75, 0.0, 0.75] blocks, give the slab ~0.25 block thickness under the surface)

Seat / slot anchors (px):

- `driver`: [-7, 29, -12]
- `passenger`: [7, 29, -12]
- `rear_left`: [7, 29, 6]
- `rear_right`: [-7, 29, 6]
- `gunner_stand`: [0, 22.5, -2]
- `turret` bone (ring-mount .50 cal with gun shield) rotates about Y at [0, 47, -2]; aim it from Java.

## UH-60 Black Hawk Utility Helicopter (`uh60_blackhawk`) - Tier 1
Payload: **1 Obsolete Exoframe on the ventral hook (Titan is too heavy); cabin seats 8 troops**
Player seat capacity: **10**

Liveries: `uh60_blackhawk.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-52.4, 131], y [-29.6, 136.0], z [-91.2, 160.0]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `cabin_deck`: [-14, 27, -30] -> [14, 27, 50]  =  [-0.88, 1.69, -1.88] -> [0.88, 1.69, 3.12] (size [1.75, 0.0, 5.0] blocks, give the slab ~0.25 block thickness under the surface)

Seat / slot anchors (px):

- `pilot`: [6, 32, -56]
- `copilot`: [-6, 32, -56]
- `exo_hang`: [0, -60, 0]
- Derived from the Mi-17 geometry x0.8: 4-blade rotor, 4-blade tail rotor, tail-wheel gear, ESSS stub wings with tanks. Rear doors never open (no `cargo_open` clip).
- Sling rig is hidden (scale 0) in `idle`/`fly`; play `sling` while an Exoframe is hooked.

## Fast Attack Patrol Craft (`fac_patrol`) - Tier 1
Payload: **crew only; 4 gun hard-points (2 large, 2 pintle)**
Player seat capacity: **6**

Liveries: `fac_patrol.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-30, 30], y [0, 154.6], z [-140, 141.2]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `foredeck`: [-18, 48, -118] -> [18, 48, 6]  =  [-1.12, 3.0, -7.38] -> [1.12, 3.0, 0.38] (size [2.25, 0.0, 7.75] blocks, give the slab ~0.25 block thickness under the surface)
- `side_walkway_l`: [19, 44, 6] -> [27, 44, 120]  =  [1.19, 2.75, 0.38] -> [1.69, 2.75, 7.5] (size [0.5, 0.0, 7.12] blocks, give the slab ~0.25 block thickness under the surface)
- `side_walkway_r`: [-27, 44, 6] -> [-19, 44, 120]  =  [-1.69, 2.75, 0.38] -> [-1.19, 2.75, 7.5] (size [0.5, 0.0, 7.12] blocks, give the slab ~0.25 block thickness under the surface)
- `stern_deck`: [-22, 44, 66] -> [22, 44, 134]  =  [-1.38, 2.75, 4.12] -> [1.38, 2.75, 8.38] (size [2.75, 0.0, 4.25] blocks, give the slab ~0.25 block thickness under the surface)
- `pilothouse_floor`: [-17, 44, 9] -> [17, 44, 55]  =  [-1.06, 2.75, 0.56] -> [1.06, 2.75, 3.44] (size [2.12, 0.0, 2.88] blocks, give the slab ~0.25 block thickness under the surface)
- `pilothouse_roof`: [-16, 92, 12] -> [16, 92, 52]  =  [-1.0, 5.75, 0.75] -> [1.0, 5.75, 3.25] (size [2.0, 0.0, 2.5] blocks, give the slab ~0.25 block thickness under the surface)
- `lower_deck`: [-13, 8, -44] -> [13, 8, 112]  =  [-0.81, 0.5, -2.75] -> [0.81, 0.5, 7.0] (size [1.62, 0.0, 9.75] blocks, give the slab ~0.25 block thickness under the surface)

Walkable interior:

- lower deck (floor y=8): bunk room -44..16, stair hatch 16..52 (x 4..17), engine room 52..112
- pilothouse: bridge consoles, rear door, side doors

Gun hard-points (`mount_*` bones; `pos` = gun pivot in px, facing deg: 0 = bow, +90 = left/+X; arc = traverse; pitch = elevation limits):

- `mount_bow` pos [0, 56, -92] ([0.0, 3.5, -5.75] blocks), large, facing 0, arc 280, pitch [-8, 70]
- `mount_stern` pos [0, 52, 100] ([0.0, 3.25, 6.25] blocks), large, facing 180, arc 280, pitch [-8, 70]
- `mount_mg_l` pos [13, 100, 46] ([0.81, 6.25, 2.88] blocks), pintle, facing 90, arc 200, pitch [-15, 60]
- `mount_mg_r` pos [-13, 100, 46] ([-0.81, 6.25, 2.88] blocks), pintle, facing -90, arc 200, pitch [-15, 60]

Seat / slot anchors (px):

- `helm`: [-8, 44, 28]
- `co_helm`: [-8, 44, 40]
- `bunks`: [7, 8, -20]

## Offshore Patrol Vessel (`opv_cutter`) - Tier 2
Payload: **crew + 1 helicopter on the helideck (Mi-17 / UH-60 can land); 5 gun hard-points**
Player seat capacity: **6**

Liveries: `opv_cutter.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-56.5, 56.6], y [0, 178.4], z [-210, 211.2]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `forecastle`: [-26, 58, -196] -> [26, 58, -96]  =  [-1.62, 3.62, -12.25] -> [1.62, 3.62, -6.0] (size [3.25, 0.0, 6.25] blocks, give the slab ~0.25 block thickness under the surface)
- `main_deck`: [-28, 44, -92] -> [28, 44, 36]  =  [-1.75, 2.75, -5.75] -> [1.75, 2.75, 2.25] (size [3.5, 0.0, 8.0] blocks, give the slab ~0.25 block thickness under the surface)
- `helideck`: [-34, 44, 88] -> [34, 44, 204]  =  [-2.12, 2.75, 5.5] -> [2.12, 2.75, 12.75] (size [4.25, 0.0, 7.25] blocks, give the slab ~0.25 block thickness under the surface)
- `tier1_floor`: [-28, 44, -83] -> [28, 44, -9]  =  [-1.75, 2.75, -5.19] -> [1.75, 2.75, -0.56] (size [3.5, 0.0, 4.62] blocks, give the slab ~0.25 block thickness under the surface)
- `bridge_floor`: [-23, 80, -65] -> [23, 80, -15]  =  [-1.44, 5.0, -4.06] -> [1.44, 5.0, -0.94] (size [2.88, 0.0, 3.12] blocks, give the slab ~0.25 block thickness under the surface)
- `bridge_wings`: [-56, 82, -66] -> [56, 82, -14]  =  [-3.5, 5.12, -4.12] -> [3.5, 5.12, -0.88] (size [7.0, 0.0, 3.25] blocks, give the slab ~0.25 block thickness under the surface)
- `bridge_roof`: [-23, 118, -68] -> [23, 118, -12]  =  [-1.44, 7.38, -4.25] -> [1.44, 7.38, -0.75] (size [2.88, 0.0, 3.5] blocks, give the slab ~0.25 block thickness under the surface)
- `hangar_floor`: [-24, 44, 41] -> [24, 44, 87]  =  [-1.5, 2.75, 2.56] -> [1.5, 2.75, 5.44] (size [3.0, 0.0, 2.88] blocks, give the slab ~0.25 block thickness under the surface)
- `lower_deck`: [-24, 8, -150] -> [24, 8, 102]  =  [-1.5, 0.5, -9.38] -> [1.5, 0.5, 6.38] (size [3.0, 0.0, 15.75] blocks, give the slab ~0.25 block thickness under the surface)

Walkable interior:

- lower deck (floor y=8): stores -150..-108, bunks -108..-42, stair hatch -42..-6 (x 8..22), mess/galley -6..42, engine room 42..102
- tier 1: officers' cabins + stair to bridge; tier 2: bridge with consoles and wing doors; hangar aft of the funnel

Gun hard-points (`mount_*` bones; `pos` = gun pivot in px, facing deg: 0 = bow, +90 = left/+X; arc = traverse; pitch = elevation limits):

- `mount_bow` pos [0, 66, -168] ([0.0, 4.12, -10.5] blocks), large, facing 0, arc 280, pitch [-8, 75]
- `mount_hangar` pos [0, 88, 64] ([0.0, 5.5, 4.0] blocks), large, facing 180, arc 300, pitch [-5, 85]
- `mount_waist_l` pos [33, 52, 20] ([2.06, 3.25, 1.25] blocks), pintle, facing 90, arc 180, pitch [-10, 60]
- `mount_waist_r` pos [-33, 52, 20] ([-2.06, 3.25, 1.25] blocks), pintle, facing -90, arc 180, pitch [-10, 60]
- `mount_bridge` pos [0, 126, -40] ([0.0, 7.88, -2.5] blocks), pintle, facing 0, arc 360, pitch [-10, 80]

Seat / slot anchors (px):

- `helm`: [10, 80, -50]
- `co_helm`: [-10, 80, -50]
- `captain`: [0, 80, -30]
- `bunks`: [21, 8, -80]

## Stealth Corvette (`corvette_stealth`) - Tier 3
Payload: **crew + 1 helicopter on the helideck; 5 gun hard-points incl. a main gun on the foredeck**
Player seat capacity: **8**

Liveries: `corvette_stealth.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-44.4, 44], y [0, 199], z [-260, 261.2]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `foredeck`: [-28, 52, -238] -> [28, 52, -156]  =  [-1.75, 3.25, -14.88] -> [1.75, 3.25, -9.75] (size [3.5, 0.0, 5.12] blocks, give the slab ~0.25 block thickness under the surface)
- `main_deck_walkway_l`: [31, 44, -150] -> [39, 44, 104]  =  [1.94, 2.75, -9.38] -> [2.44, 2.75, 6.5] (size [0.5, 0.0, 15.88] blocks, give the slab ~0.25 block thickness under the surface)
- `main_deck_walkway_r`: [-39, 44, -150] -> [-31, 44, 104]  =  [-2.44, 2.75, -9.38] -> [-1.94, 2.75, 6.5] (size [0.5, 0.0, 15.88] blocks, give the slab ~0.25 block thickness under the surface)
- `vls_deck`: [-20, 46, -152] -> [20, 46, -108]  =  [-1.25, 2.88, -9.5] -> [1.25, 2.88, -6.75] (size [2.5, 0.0, 2.75] blocks, give the slab ~0.25 block thickness under the surface)
- `helideck`: [-36, 44, 152] -> [36, 44, 256]  =  [-2.25, 2.75, 9.5] -> [2.25, 2.75, 16.0] (size [4.5, 0.0, 6.5] blocks, give the slab ~0.25 block thickness under the surface)
- `tier1_floor`: [-28, 44, -89] -> [28, 44, 59]  =  [-1.75, 2.75, -5.56] -> [1.75, 2.75, 3.69] (size [3.5, 0.0, 9.25] blocks, give the slab ~0.25 block thickness under the surface)
- `bridge_floor`: [-20, 80, -69] -> [20, 80, -7]  =  [-1.25, 5.0, -4.31] -> [1.25, 5.0, -0.44] (size [2.5, 0.0, 3.88] blocks, give the slab ~0.25 block thickness under the surface)
- `bridge_roof`: [-22, 118, -72] -> [22, 118, -4]  =  [-1.38, 7.38, -4.5] -> [1.38, 7.38, -0.25] (size [2.75, 0.0, 4.25] blocks, give the slab ~0.25 block thickness under the surface)
- `hangar_floor`: [-24, 44, 105] -> [24, 44, 151]  =  [-1.5, 2.75, 6.56] -> [1.5, 2.75, 9.44] (size [3.0, 0.0, 2.88] blocks, give the slab ~0.25 block thickness under the surface)
- `lower_deck`: [-30, 8, -152] -> [30, 8, 136]  =  [-1.88, 0.5, -9.5] -> [1.88, 0.5, 8.5] (size [3.75, 0.0, 18.0] blocks, give the slab ~0.25 block thickness under the surface)

Walkable interior:

- lower deck (floor y=8): 2 bunk rooms -152..-56, stair hatch -56..-20 (x 8..22), mess/galley -20..40, engine room 40..136
- tier 1: officers, stair to bridge, wardroom, stores; tier 2: bridge; hangar aft

Gun hard-points (`mount_*` bones; `pos` = gun pivot in px, facing deg: 0 = bow, +90 = left/+X; arc = traverse; pitch = elevation limits):

- `mount_bow_main` pos [0, 60, -202] ([0.0, 3.75, -12.62] blocks), large, facing 0, arc 300, pitch [-8, 75]
- `mount_ciws_fwd` pos [0, 126, -40] ([0.0, 7.88, -2.5] blocks), pintle, facing 0, arc 360, pitch [-5, 85]
- `mount_ciws_aft` pos [0, 88, 128] ([0.0, 5.5, 8.0] blocks), pintle, facing 180, arc 360, pitch [-5, 85]
- `mount_aux_l` pos [37, 52, -120] ([2.31, 3.25, -7.5] blocks), pintle, facing 90, arc 180, pitch [-10, 60]
- `mount_aux_r` pos [-37, 52, -120] ([-2.31, 3.25, -7.5] blocks), pintle, facing -90, arc 180, pitch [-10, 60]

Seat / slot anchors (px):

- `helm`: [10, 80, -40]
- `co_helm`: [-10, 80, -40]
- `captain`: [0, 80, -20]
- `bunks`: [27, 8, -130]

## LPD Amphibious Assault Ship (`lpd_assault`) - Tier 3
Payload: **well deck dock for 3+ Titans / 8 Exoframes (stern gate opens to a ramp); flight deck for 2 helicopters (Mi-26 fits)**
Player seat capacity: **10**

Liveries: `lpd_assault.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-52, 52], y [0, 228.4], z [-280, 281.0]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `foredeck`: [-24, 52, -240] -> [24, 52, -90]  =  [-1.5, 3.25, -15.0] -> [1.5, 3.25, -5.62] (size [3.0, 0.0, 9.38] blocks, give the slab ~0.25 block thickness under the surface)
- `island_walkway_l`: [28, 52, -52] -> [49, 52, 20]  =  [1.75, 3.25, -3.25] -> [3.06, 3.25, 1.25] (size [1.31, 0.0, 4.5] blocks, give the slab ~0.25 block thickness under the surface)
- `island_walkway_r`: [-49, 52, -52] -> [-28, 52, 20]  =  [-3.06, 3.25, -3.25] -> [-1.75, 3.25, 1.25] (size [1.31, 0.0, 4.5] blocks, give the slab ~0.25 block thickness under the surface)
- `tier1_floor`: [-26, 52, -51] -> [26, 52, 15]  =  [-1.62, 3.25, -3.19] -> [1.62, 3.25, 0.94] (size [3.25, 0.0, 4.12] blocks, give the slab ~0.25 block thickness under the surface)
- `tier2_floor`: [-24, 88, -47] -> [24, 88, 11]  =  [-1.5, 5.5, -2.94] -> [1.5, 5.5, 0.69] (size [3.0, 0.0, 3.62] blocks, give the slab ~0.25 block thickness under the surface)
- `bridge_floor`: [-22, 124, -43] -> [22, 124, 7]  =  [-1.38, 7.75, -2.69] -> [1.38, 7.75, 0.44] (size [2.75, 0.0, 3.12] blocks, give the slab ~0.25 block thickness under the surface)
- `island_link`: [-10, 124, 8] -> [10, 124, 20]  =  [-0.62, 7.75, 0.5] -> [0.62, 7.75, 1.25] (size [1.25, 0.0, 0.75] blocks, give the slab ~0.25 block thickness under the surface)
- `flight_deck`: [-40, 124, 20] -> [40, 124, 278]  =  [-2.5, 7.75, 1.25] -> [2.5, 7.75, 17.38] (size [5.0, 0.0, 16.12] blocks, give the slab ~0.25 block thickness under the surface)
- `well_floor`: [-34, 20, 22] -> [34, 20, 278]  =  [-2.12, 1.25, 1.38] -> [2.12, 1.25, 17.38] (size [4.25, 0.0, 16.0] blocks, give the slab ~0.25 block thickness under the surface)
- `stern_gate_open`: [-34, 20, 280] -> [34, 20, 372]  =  [-2.12, 1.25, 17.5] -> [2.12, 1.25, 23.25] (size [4.25, 0.0, 5.75] blocks, give the slab ~0.25 block thickness under the surface)
- `lower_deck`: [-30, 8, -196] -> [30, 8, 20]  =  [-1.88, 0.5, -12.25] -> [1.88, 0.5, 1.25] (size [3.75, 0.0, 13.5] blocks, give the slab ~0.25 block thickness under the surface)

Walkable interior:

- lower deck (floor y=8): 2 bunk rooms -196..-100, stores -100..-52, stair hatch -52..-16 (x 8..22), engine room -16..20
- island: tier 1 mess + stairs, tier 2 officers, tier 3 bridge (floor 124 = flight deck level, link bridge at z 8..20)
- well deck: floor y=20, clear height ~100 px (Titans fit), open to the stern gate; bulkhead door at z 21 into the engine room

Gun hard-points (`mount_*` bones; `pos` = gun pivot in px, facing deg: 0 = bow, +90 = left/+X; arc = traverse; pitch = elevation limits):

- `mount_bow` pos [0, 60, -190] ([0.0, 3.75, -11.88] blocks), large, facing 0, arc 290, pitch [-8, 75]
- `mount_island` pos [0, 168, -34] ([0.0, 10.5, -2.12] blocks), pintle, facing 0, arc 360, pitch [-5, 85]
- `mount_aft_l` pos [40, 132, 262] ([2.5, 8.25, 16.38] blocks), pintle, facing 90, arc 200, pitch [-10, 70]
- `mount_aft_r` pos [-40, 132, 262] ([-2.5, 8.25, 16.38] blocks), pintle, facing -90, arc 200, pitch [-10, 70]

Seat / slot anchors (px):

- `helm`: [10, 124, -24]
- `co_helm`: [-10, 124, -24]
- `captain`: [0, 124, -10]
- `bunks`: [20, 8, -170]

## Transport Submarine (`transport_sub`) - Tier 2
Payload: **2 Exoframes in the stores bay (kneeling); 1 deck gun**
Player seat capacity: **14**

Liveries: `transport_sub.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-54, 54], y [-7.0, 173.0], z [-260.0, 270]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `interior_floor`: [-31, 16, -170] -> [31, 16, 170]  =  [-1.94, 1.0, -10.62] -> [1.94, 1.0, 10.62] (size [3.88, 0.0, 21.25] blocks, give the slab ~0.25 block thickness under the surface)
- `casing_deck_fore`: [-8, 90.6, -170] -> [8, 90.6, -58]  =  [-0.5, 5.66, -10.62] -> [0.5, 5.66, -3.62] (size [1.0, 0.0, 7.0] blocks, give the slab ~0.25 block thickness under the surface)

Walkable interior:

- pressure hull (floor y=16, clear ~70 px): bunks -170..-122, mess/galley -122..-60, stair hall -60..20 (45 deg stair rising to the crown hatch), control room 20..68, stores bay 68..170
- topside: walkable casing deck over the hull crown (x +-8) and the sail's open bridge; stair top at y=90 meets the casing deck at z=16

Gun hard-points (`mount_*` bones; `pos` = gun pivot in px, facing deg: 0 = bow, +90 = left/+X; arc = traverse; pitch = elevation limits):

- `mount_deck` pos [0, 98.6, -130] ([0.0, 6.16, -8.12] blocks), large, facing 0, arc 300, pitch [-8, 60]

Seat / slot anchors (px):

- `helm`: [0, 16, 30]
- `co_helm`: [16, 16, 30]
- `captain`: [-16, 16, 30]
- `bunks`: [24, 16, -150]
- `exo_a`: [0, 16, 90]
- `exo_b`: [0, 16, 140]
- Hull centre y=46 (radius 44 px); design waterline for surfacing ~ y=60. Submerged play needs a swim/air-pocket rule in Java: the hull interior is dry model volume only.
- `prop` spins about Z.

## C-17 Style Strategic Airlifter (`c17_airlifter`) - Tier 3
Payload: **2 Titans (standing) or up to 4 Exoframes on the cargo deck; 24 jump seats**
Player seat capacity: **27**

Liveries: `c17_airlifter.png` (default), `_thai.png` (Royal Thai Army olive), `_desert.png`

Model extents px: x [-356, 356], y [0.4, 272], z [-334, 340]

Walkable deck colliders (walking surface; box min / max, px -> blocks):

- `flight_deck`: [-24, 40, -328] -> [24, 40, -252]  =  [-1.5, 2.5, -20.5] -> [1.5, 2.5, -15.75] (size [3.0, 0.0, 4.75] blocks, give the slab ~0.25 block thickness under the surface)
- `crew_rest`: [-32, 40, -248] -> [32, 40, -192]  =  [-2.0, 2.5, -15.5] -> [2.0, 2.5, -12.0] (size [4.0, 0.0, 3.5] blocks, give the slab ~0.25 block thickness under the surface)
- `cargo_deck`: [-40, 40, -188] -> [40, 40, 270]  =  [-2.5, 2.5, -11.75] -> [2.5, 2.5, 16.88] (size [5.0, 0.0, 28.62] blocks, give the slab ~0.25 block thickness under the surface)
- `ramp_open`: [-40, -2, 273] -> [40, 40, 330]  =  [-2.5, -0.12, 17.06] -> [2.5, 2.5, 20.62] (size [5.0, 2.62, 3.56] blocks, give the slab ~0.25 block thickness under the surface)

Walkable interior:

- flight deck (-328..-252): 2 pilot seats, consoles, windscreen; crew rest (-248..-190): bunks + head; door to the cargo bay at z=-190
- cargo bay (-188..270): 24 jump seats along the walls, 2 roller tracks, tie-down ring grid; clear height ~76 px; rear ramp is the entrance (open -135 deg: slope from y=40 at z=270 to ground at ~z=313)

Seat / slot anchors (px):

- `pilot`: [12, 46, -296]
- `copilot`: [-12, 46, -296]
- `loadmaster`: [0, 40, -200]
- `titan_slot_a`: [0, 40, -60]
- `titan_slot_b`: [0, 40, 100]
- Wings are decoration (you cannot stand on them without a collider); T-tail fin reaches y~275. Engines are static (no fan animation).
