# OBSOLETE Exoframe — factions, weapons and frame-tier UI (handoff)

Goal: the exoframe lives in a world with many factions. Add **many more mix-and-match armor variants**, **more
weapons**, and **a cockpit UI that differs per frame tier** (cheap/old frames get crude displays, expensive/modern
frames get advanced ones). A reviewer will check your work against the checklist at the end.

Read `HANDOFF_REMAINING_WORK.md` first — its ground rules (generators are the source of truth, never change
existing bone name/parent/pivot, back up before editing because this folder is not in git, `MODEL_SCALE`) all
still apply. This file adds the rules for the new work.

## How the mech is put together now (things you must not break)

- **Scale:** `ExoframeEntity.MODEL_SCALE = 1.8F` (render, hitbox, seat, muzzles, melee). Mirrored as
  `MODEL_SCALE` in `tools/build_exoframe_geo.py`.
- **Pilot pose:** the pilot rides astride like a horse rider. `ExoframeEntity.shouldRiderSit()` returns false and
  `client/renderer/ExoframeRiderPose.java` redraws the legs (forward-down, spread) and arms (to the grips). The
  angles are mirrored in the geo generator (`LEG_FORWARD`, `LEG_SPREAD`, `ARM_FORWARD`, `ARM_SPREAD`) and drive the
  `RIDER` envelope. Change both together.
- **Pilot clash check:** the geo generator asserts nothing cuts through the seated pilot. Thin capsule walls count,
  solid hull blocks that enclose the pilot do not. Fix geometry, never weaken the check.
- **Capsules:** author capsule geometry around the *full-size* seated pilot (feet y21.6, centre z5.1, see
  existing `canopy_*` blocks), then the refit section maps it onto the real seat with `to_seat()`.
  Styles that exist: enclosed hood (Marine), open-top tub to the shoulders (Pegaso), drum (Polar),
  turtle shell (Outlander).
- **Leg fairings:** `leg_fairing()` adds waist armor around the pilot's straddling legs to every chest piece listed
  in that loop. Add new chest bones to that list.
- **Sensor head:** some sets hide the frame's own head (Marine puts cameras on its hood — see the `hasUsmcChest`
  block in `ExoframeModel`). GeckoLib does not hide children with a parent: hide every head bone explicitly.
- **Shin greaves:** parented to the shin bones (`armor_*_shin_<faction>`) so they follow the knee.
- **Texture space:** one 512×512 sheet. Armor cubes are packed per faction by the packer in the geo generator
  (`FACTION_UV_REGIONS`); colours come from the packing manifest (`tools/packed_armor_uvs.json`) in
  `tools/generate_high_fidelity_textures.py → faction_livery`. Space is nearly full. If you add many factions,
  move to a 1024×1024 sheet: update the geo `texture_width/height`, every UV region, the texture generator size,
  and re-check that weapons/frame regions still sample correctly.
- **Weapon handling:** `client/model/ExoframeArmIK.java` `Hold` table (grip point, support point, rest fist,
  aim fist, yaws, pitch share). The right fist is IK'd to the hold, the gun is aimed exactly, the grip is snapped
  into the fist and the left hand is IK'd onto the support point. Arm reach ≈ 6.5 + 11.5 model px: the support
  point must stay within ~17.2 px of the left shoulder at every look pitch, and fists must sit in front of the
  chest armor (z ≤ −6.8) and outside the head (|x| ≥ 4.6 when aiming).
- **Weapons in the world:** muzzle/pod offsets are multiplied by `MODEL_SCALE`; bullets converge on the pilot's
  aim point (`ExoframeEntity.computeTargetConvergence`) and never hit their own mech.

## Task 0 — make variants data-driven (do this first)

Today visibility is a long `if` chain per item in `ExoframeModel.setCustomAnimations`, the cockpit display is an
`if` chain on the head item in `ExoframeHudOverlay.renderCockpitMonitorScreen`, and weapon handling is
`instanceof` chains (`ExoframeArmIK.Hold.of`, `ExoframeModel` weapon section). That will not scale to dozens of
variants.

- Introduce one registry (Java) mapping each armor/weapon item to: the bones it shows, whether it hides the frame
  head, its faction, its HUD/sensor contribution, and (weapons) its `Hold`. Item classes can carry this as
  constructor data.
- Replace the `if`/`instanceof` chains with lookups. Behaviour for existing items must stay identical — prove it
  with the `armor` and `anim` autotest screenshots before/after.

## Task 1 — many more faction armor sets

Build at least **6 new factions**, each a complete set: head, chest (pick a capsule style or none), arms
(pauldrons), legs (thigh + shin greaves), and a utility/backpack module. Every piece must mix and match with every
other faction's pieces (no piece may assume a specific neighbour). Use names close to, but not identical to,
anime names (the owner's rule).

Suggested spread (adapt freely, but cover the tiers):
- Cheap/salvage: scrap-plate militia (welded sheet metal, mismatched panels, no capsule or a cage only).
- Regional armies: an East-Asian army set, a desert army set, a jungle/riverine set.
- Expensive/modern: a stealth PMC set (angular, low-profile capsule), an elite special-forces set (full
  enclosed capsule with sensor array).
- Civilian/industrial: construction/rescue set (cage + hazard markings) — reuse/extend the roll cage.

For each new set:
1. Geometry in the generator, new bones with pivots matching their parent (copy the existing pattern), shins on
   the shin bones, capsule authored around the full-size pilot.
2. Add its bones to `FACTION_UV_REGIONS` and its livery colours to `faction_livery` (plus markings).
3. Items (`ExoframeArmorItem` with slot, damage reduction, series name), assembly recipes
   (`data/obsolete/recipes/assembly`), item models, 16×16 icons (`tools/generate_item_icons.py`), lang, creative
   tab, registry entry from Task 0.
4. Add the set to the `armor` autotest (front/rear, piloted front/back/first-person).

Done when every new set renders correctly alone **and** mixed (add an autotest step that equips a random
cross-faction combination per slot and screenshots it), the clash check passes, and first person is never blocked.

## Task 2 — more weapons

Add at least **8 weapons** across roles, each with its own model, hold, firing behaviour and ammo:
light/heavy rifles, a shotgun/breaching gun, an automatic grenade launcher, a recoilless rifle, a guided AT
launcher, a flamethrower or similar area weapon, and a melee weapon (blade/axe) that uses the melee box.
Optionally a hand-held shield that occupies the left hand (then the left arm must not IK onto a gun).

Per weapon:
1. Bone under `right_hand_weapon_mount` in the generator (grip at the fist, barrel along −z).
2. `Hold` entry: grip, support point, rest/aim fists and yaws. Re-verify reach and fist/head clearance for the
   full pitch range (−1.05…1.15 rad) — port the check to Python like the earlier verification, do not eyeball it.
3. Item class extending `ExoframeWeaponItem`: muzzle offset × `MODEL_SCALE`, convergence aiming, cooldown,
   ammo item, sounds, recoil (`triggerRecoilAnim`).
4. Recipe, icon, lang, creative tab, registry entry, HUD ammo/readout.
5. `gameplay` autotest: target placed downrange must take damage (melee: the melee box).

## Task 3 — cockpit UI per frame tier

Each frame should feel its price and age in the cockpit.

- Add a **frame tier** to the entity (synced data + NBT), set by different kit items (e.g. salvage, standard
  military, advanced, elite). Tier may also gate which sensor modules work.
- Rebuild `ExoframeHudOverlay` around the tier:
  - Salvage/old: crude monochrome readouts, analog-style gauges, no target tracking, flicker/noise, minimal compass.
  - Standard military: current tactical HUD (compass tape, FCS reticle, armor panel, weapon/ammo).
  - Advanced: adds range finding, threat markers, armor damage per slot, thermal/NV mode from the head module.
  - Elite: clean high-resolution layout, target lock/lead indicator, mini-map/radar, full diagnostics.
  Head/utility modules keep adding their overlays (night vision, scanners) on top of the tier base.
- Restyle the loadout screen (`client/gui/ExoframeScreen.java`, opened with **E while riding** or shift+right-click)
  per tier too: panel art, slot frames, a live 3D preview of the mech (already present) and per-slot armor stats.
- Text must stay readable at GUI scales 2–4 and 1080p; never cover the crosshair.

Done when an autotest step mounts each tier and screenshots the HUD and the loadout screen.

## Testing

```bash
JAVA_HOME=$(/usr/libexec/java_home -v 17) ./gradlew build
JAVA_HOME=$(/usr/libexec/java_home -v 17) OBSOLETE_AUTOTEST=armor ./gradlew runClient
JAVA_HOME=$(/usr/libexec/java_home -v 17) OBSOLETE_AUTOTEST=anim ./gradlew runClient
JAVA_HOME=$(/usr/libexec/java_home -v 17) OBSOLETE_AUTOTEST=gameplay ./gradlew runClient
```

Screenshots go to `run/screenshots/autotest_*.png`; grep the log for `Screenshot captured`, `PASS`/`FAIL` and
`Caused by`. Build scenario step lists lazily (items are not registered when `ClientAutoTest` loads).

Housekeeping: do not leave `.bak` files inside `src/` or `tools/` — keep backups outside the project.

## Reviewer checklist

1. Generators re-run cleanly and reproduce committed outputs; pilot clash check present and passing; no existing
   bone name/parent/pivot changed.
2. Task 0 landed first and existing items look/behave identically (before/after screenshots).
3. Every new armor piece renders alone and in random cross-faction mixes; capsules never block first person;
   the frame head hides correctly for sets that bring their own sensors.
4. Every new weapon: hold verified across the pitch range (script output attached), hits a target in `gameplay`.
5. Each frame tier has a distinct HUD and loadout screen, readable at GUI scales 2–4.
6. `./gradlew build` passes, all autotests finish with no `Caused by`; no `.bak` files in the source tree.
7. A short report: what was verified, what was not, and any trade-offs (e.g. texture sheet size change).
