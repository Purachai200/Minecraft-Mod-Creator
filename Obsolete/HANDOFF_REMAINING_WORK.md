# OBSOLETE Exoframe — remaining work (handoff)

You are picking up a Forge 1.20.1 + GeckoLib 4.4.4 mod in this folder (`Obsolete/`). The goal is an exoframe
that looks and moves like the mechs in the anime *OBSOLETE*. A reviewer will check your work against the
checklist at the end — read it before you start, it is what "done" means.

## Ground rules (read first)

- **Generated files are never hand-edited.** Edit the generator, re-run it, commit both.
  | Output | Generator |
  |---|---|
  | `src/main/resources/assets/obsolete/geo/exoframe.geo.json` | `python3 tools/build_exoframe_geo.py` |
  | `src/main/resources/assets/obsolete/animations/exoframe.animation.json` | `python3 tools/build_exoframe_anims.py` (reads the geo for pivots — run it **after** the geo) |
  | `src/main/resources/assets/obsolete/textures/entity/exoframe/*.png` | `python3 tools/generate_high_fidelity_textures.py` |
- **Never change a bone's `name`, `parent` or `pivot`** that already exists — animations and Java reference them.
  Adding new bones is fine.
- **`Obsolete/` is not tracked by git.** Copy any file you are about to rewrite to a backup first.
- **One scale constant:** `ExoframeEntity.MODEL_SCALE = 1.8F` (render, hitbox, seat, muzzles, melee all derive
  from it). `build_exoframe_geo.py` has its own `MODEL_SCALE = 1.8` that must match. Do not hard-code new
  world-space offsets in blocks without multiplying by `MODEL_SCALE`.
- **The geo generator asserts that nothing cuts through the seated pilot** (`RIDER` envelope, end of the
  script). If it fails, fix the geometry — do not loosen or delete the check.
- **Pilot seat:** `ExoframeEntity.positionRider` derives the seat from the model cushion top (y 30.8 model px,
  z 4.3). If you move the seat in the geo, change both together.
- Java builds with JDK 17: `JAVA_HOME=$(/usr/libexec/java_home -v 17) ./gradlew build`

## How to test in game (no manual play needed)

```bash
JAVA_HOME=$(/usr/libexec/java_home -v 17) OBSOLETE_AUTOTEST=armor ./gradlew runClient
```

Scenarios live in `src/main/java/com/obsolete/client/debug/ClientAutoTest.java`; the client creates a world,
runs scripted steps, saves screenshots to `run/screenshots/autotest_*.png`, then quits.

| Scenario | Shows |
|---|---|
| `armor` | 4 faction sets front/rear (`b_*`), then piloted front/back/first-person (`c_*`) |
| `anim` | weapon rest/aim holds, crouch, emotes (`a*`) |
| `showcase` | older 20-shot tour (camera distances not yet updated for 1.8× — see task 6) |

Grep the log for `Screenshot captured` (count) and `Caused by` (crashes). Note: items must not be looked up in
static initialisers (registry not ready) — build step lists lazily, as `buildArmorSteps()` does.

## What already exists (do not redo)

- Skeleton + digitigrade legs, knee/pelvis tyres, 37 original bones (+ armor/capsule bones added since).
- Four armor sets, each per-slot (head/chest/arms/legs/utility), registry ids unchanged for save compatibility:
  Marine Raider (`*_usmc_*`), Pegaso Black (`*_cerberus_*`, dome), Polar Front (`armor_arctic_chest`,
  `*_polar_*`, skis, `module_twin_manpads`), Outlander Heavy (`armor_militia_*`, `*_outlander_*`).
- Pilot capsules `canopy_usmc|cerberus|polar|hood`, shown with the set's chest piece, hidden in first person
  (`ExoframeModel.setCustomAnimations`).
- Weapon handling: `client/model/ExoframeArmIK.java` — right fist IK to a hold target, gun aimed exactly,
  grip snapped into the fist, left hand IK'd onto the weapon's support point. Hold table at the top of the file.
- Locomotion + emotes generated with leg IK (feet planted); emote keys V/B/N/H (`ModKeyMappings.KEY_EMOTES`).
- Faction factory colours: `faction_livery()` in the texture generator, keyed by UV blocks.

## Remaining tasks (priority order)

### 1. Textures that read like the anime (biggest visual gap)
Today every cube of a bone samples the same UV origin (box UV at the bone's base), and the paint is flat colour
+ noise + a 14 px seam grid → repeated black stripes (very visible on Polar), no real panel lines, no markings.
- Give each armor/capsule cube its own UV rectangle (pack them in the generator; keep inside that faction's
  livery block or extend `faction_livery`), then paint per-face detail: panel lines along cube edges, bolts,
  vents, hazard/unit markings.
- Required markings: **white "1"** on the Pegaso dome and both red shoulder pods; Marine Raider unit stencil;
  Polar splinter camo without the stripe artefacts.
- Keep the 6 non-default camo schemes working (they repaint every set).
- Done when: `armor` screenshots show the markings on the right faces, no stripe artefacts, texture ≤ 512×512
  or the geo `texture_width/height` updated consistently.

### 2. Item icons for the 6 new items
`armor_polar_head|arms|legs`, `armor_outlander_arms|legs`, `module_twin_manpads` currently reuse a sibling's PNG
(see `textures/item/`). Draw distinct 16×16 icons.

### 3. Real-terrain gameplay check at 1.8×
Untested: walking/stepping (step height 2.0) on uneven terrain, collision with walls/doorways, bullets/rockets
actually hitting targets from the new muzzle heights (`Exoframe*Item.java`, `fireShoulderMissile`), melee box
(`performMeleeAttack`), crouch hitbox. Add an autotest scenario (spawn targets/terrain, fire, assert hits in log)
rather than relying on manual play. Fix what breaks.

### 4. Third-person camera distance
Vanilla third-person distance (4 blocks) is close for a ~4-block mech. Investigate a Forge 47 hook to push the
camera back while riding the exoframe; if none exists without a mixin, write down the trade-off and stop.

### 5. Pose-time collision check
The pilot-clash assert only checks the rest pose. Extend it (or add a separate check) for the shouldered-aim
pose and the crouch pose: armor/capsule must not cut the pilot; the gun must not pass through the head armor.
Reuse the hold maths in `ExoframeArmIK` (port it to Python the same way the assert does geometry).

### 6. Showcase scenario camera
`SHOWCASE` steps in `ClientAutoTest` still use pre-scale camera distances/heights. Scale them with
`ExoframeEntity.MODEL_SCALE` like `view()` does, so all 20 shots frame the mech.

### 7. Pilot-in-the-loop animation check
Aim pitch following the pilot's look, and walk/sprint/crouch-walk, have only been seen without a rider. Add an
`anim` sub-scenario that mounts the player, pitches the view up/down and drives movement, and screenshot it.

## Things that bit us (avoid repeating)

- GeckoLib render space mirrors X (pivots/cube x negated), bone rotation order is Z·Y·X, bone position
  translates by (−posX, posY, posZ). Keyframe rotations are Bedrock-convention (X/Y flipped on load):
  in the animation JSON **negative X raises an arm/leg forward**.
- Texture UV blocks overlap easily: the VOTOMS red block runs to x=460 inclusive — Polar UVs start at 462.
- The rider offset was once changed outside the planned work; always re-read `positionRider` before fitting
  anything to the pilot.
- `ExoframeArmIK` holds were tuned so the left hand can reach the support point at every pitch (arm reach
  ≈ 6.5 + 11.5 model px; support distance must stay < ~17.2). Changing a hold needs that re-check.

## Reviewer checklist (what will be verified)

1. Generators re-run cleanly from scratch; outputs match what is committed; pilot-clash assert still present
   and passing.
2. No existing bone name/parent/pivot changed (diff the bone list against the current geo).
3. `./gradlew build` passes; `armor`, `anim`, `showcase` autotests complete with the expected screenshot count
   and no `Caused by` in the log.
4. Screenshots compared side by side with the anime references for each faction (colours, markings, silhouette).
5. New world-space numbers derive from `MODEL_SCALE`; no unexplained magic offsets.
6. Each task above states what was verified and what was not.
