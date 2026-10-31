# OBSOLETE Exoframe — role variants for every situation (handoff)

Goal: the exoframe should be useful in many situations, not just combat: riot control, rescue, amphibious
landings, construction, scouting with radar, fishing, ceremonial and improvised militia use. Each role is a set of
parts you can swap in the loadout screen (E while riding), and each part must **do something in the game**, not
only change the look. A reviewer will check your work against the checklist at the end.

Read these first. Their rules still apply:
- `HANDOFF_REMAINING_WORK.md`: generators are the source of truth, never change an existing bone's
  name/parent/pivot, back up before editing.
- `HANDOFF_FACTIONS_WEAPONS_UI.md`: `MODEL_SCALE`, the pilot clash check, how capsules are authored and the
  `round_ring` helper, the texture sheet, weapon holds, and `ExoframeVariantRegistry`.

The project is now in git (commit `be078ed` on `main`). Commit your work in small steps and **do not push**.

## Originality rule (read before designing)

The owner took inspiration from the anime OBSOLETE (project-obsolete.com). That site's models, images and names
are copyrighted. The mod is published, so:
- **Do not** download, extract, trace or copy their 3D models, textures, images or text. Do not use their machine
  names or codes (TOAD, OBAMBO, Meghdoot, Gibraltar, Perisai, Vykhukhol, JIRAIYA, AREX-03, TOPEX-12, …).
- **Do** take the *role* (a riot-police frame with a shield, a rescue frame with a sealed cockpit) and design your
  own silhouette, colours, markings and names. Use names in the style already used in the mod: close to, but not
  the same as, real or anime names.
- If a part ends up looking like a near copy of an official design, change its shape.

## Phase 0: finish the open bugs (do these first)

1. **The grenade launcher hits only sometimes**
   - Seen in the `gameplay` autotest: some runs pass with only 1.0 damage, others fail.
   - `ExoframeGrenadeLauncherItem` fires an `ExoframeRocketEntity`, which has no gravity. The reviewer already
     removed the extra upward aim.
   - Remaining suspects: spread `0.3F`, the explosion radius or damage at the impact point, and where the test
     places its target.
   - Make it a real lobbed 40 mm round: either a projectile with gravity plus a convergence solution, or a reliable
     direct-fire splash.
   - Done when it passes **3 runs in a row** and does meaningful damage.
2. **The step-height test is flaky:** "STEP HEIGHT 2.0" failed 1 of 3 runs. Find out why (timing or chunk loading)
   and make it deterministic.
3. **The frame-tier HUD isn't shown in its screenshots**
   - `autotest_tier_*_hud_firstperson.png` show no HUD at all, and the tier 0 and tier 3 shots are identical.
   - Capture each shot after the overlay renders. Each tier must look clearly different, as
     `HANDOFF_FACTIONS_WEAPONS_UI.md` Task 3 requires.
4. **Loadout screen layout:** the 3D mech preview covers the title and the slot boxes, and HUD text shows through
   behind the panel. Fix the layout so it is readable at GUI scales 2–4.
5. **`tools/verify_weapon_holds.py` disagrees with the original checks**
   - It reports the 6 original holds as FAIL on a fist depth of −6.64 against the required −6.8.
   - Either fix those holds, or use one shared threshold with a written reason. It must not report FAIL on code
     that ships.
6. **The Outlander chest shows beige patches** that come from the texture fallback colour. Find which cubes sample
   outside their region and fix the region or livery.

## Phase 1: base frame silhouette (do before the role parts; every part fits onto it)

The owner says the mech still doesn't look like the anime frame. The proportions are the problem, not the
detail. Ours reads as an upright humanoid with a big chest box and short arms. The reference (the bare
"EXOFRAME (BODY)" view on the official site; look at it, never download or trace it) reads as a **hunched, ape-like
work frame**. Match these *general proportions*. Do the detailing your own way, following the originality rule
above.

Targets for the bare frame, standing idle. Measure them in the geo with a script and report before/after numbers:

| Feature | Reference look | Target |
|---|---|---|
| Shoulder yoke | One wide arched bar over the top. The highest point of the frame is the yoke, not a head | Outer shoulder span ≈ **1.6× hip width**. The yoke arches upward between the shoulders |
| Arms | Very long and heavy. The fists hang at about **knee-top** height | Upper arm short, forearm ≈ **1.3× upper arm length** and ≈ 1.5× its thickness. Large blocky fists |
| Torso | Almost no chest: a thin exposed spine/neck from the yoke down to the pelvis | No big chest block on the bare frame. Chest armor pieces add the bulk |
| Pelvis | A large **cylindrical drum** (motor/battery) in the centre with an open seat frame above it | Drum diameter ≈ 0.5× hip width, axis left-right, with visible ribs |
| Legs | Long; the knee bent forward; an exposed piston rod behind the shin; the ankle above a long pointed foot | Knee bent ≈ 20–25° at idle; foot length ≈ 0.35× leg length; wide stance |
| Posture | The whole upper body leans forward | Torso pitched forward ≈ 15° at idle (in the animation, not the bind pose, if easier) |
| Head | The bare frame has **no head**. Sensors come from head armor or capsule parts | The bare-frame `head` stays hidden unless head armor brings a sensor |

Changing proportions **will** move pivots, which overrides the "never change pivots" rule for frame bones only. If
you do it, change everything below together, in one commit:
- `tools/baseline_bones.json`: regenerate it, and explain in the commit which pivots moved and why.
- `tools/build_exoframe_anims.py`: it reads pivots. Re-check the leg IK so the feet stay planted.
- `client/model/ExoframeArmIK.java`: shoulder positions, segment lengths (the reach constants), and every `Hold`.
  Re-run `tools/verify_weapon_holds.py` over the full pitch range.
- **Pilot seat:** `ExoframeEntity.positionRider`, plus `SEATED` / `AUTHORED` in the geo generator, if the seat moves.
  The rider clash check must pass.
- **Muzzle and pod offsets, the melee box, and the hitbox:** `ModEntities`, plus the dimensions in
  `ExoframeEntity` if the overall height changes.
- **Every armor set must be re-fit to the new frame,** existing and new: shoulders on the new yoke, leg armor on the
  new thighs, chest pieces around the spine and drum. Take the before/after `armor` screenshots of every set.

Done when the shots below sit side by side with the reference body view and read as the same *kind* of machine:
- bare-frame front and side screenshots
- an idle pose
- a walk-cycle frame

## Phase 2: role variants

Build **at least 6** of these roles; the first 4 are required. Each role ships as parts in the existing slots (`HEAD`,
`CHEST`, `ARMS`, `LEGS`, `UTILITY`, `MAIN_WEAPON`) and is registered in `ExoframeVariantRegistry`. Check what
already exists before adding something. For example, `MODULE_DIVING_BALLAST` already gives water breathing and
ballast lift, and `MODULE_CARGO_CRATE` already exists. Extend them; don't duplicate them.

| # | Role | Parts (our own design) | Gameplay effect (required) |
|---|------|------------------------|----------------------------|
| 1 | **Riot / counter-terror police** (required) | Enclosed capsule with visor, high-vis or police livery, tall riot shield, baton | A **shield** in the left hand. `WeaponVariantData.isShield` exists, so wire it up. It blocks frontal projectiles and melee in an arc, and the left arm must stop IK-ing onto the gun. A baton or stun melee weapon uses the melee box. |
| 2 | **Disaster rescue NGO** (required) | Sealed capsule, oxygen bottles, flood lights, rescue markings | Flood lights light up blocks around the mech (light blocks that follow it, or dynamic light). The pilot gets fire resistance and water breathing while sealed. A rescue winch or arm can carry one mob or player. |
| 3 | **Amphibious assault** (required) | Inflatable float ring around the waist, wading snorkel, rugged hull | With the float ring the mech **floats on the water surface** and can paddle. Without it, the current behaviour stays. The float ring is visible as a model part. |
| 4 | **Civil engineering / worksite** (required) | Roll cage with work lights, tool hooks, hazard stripes (extend `armor_roll_cage`) | Faster block breaking with tool weapons such as the drill and saw, plus a way to place blocks or scaffolding from the pilot's inventory. |
| 5 | Radar scout | Mast or back-mounted search radar | Hostile mobs within N blocks appear on the HUD radar and briefly glow. Respect the frame tier: salvage frames get a crude version. |
| 6 | Fishing / harbour | Mech-size fishing rod as a `MAIN_WEAPON` | Casts a bobber and uses the vanilla fishing loot table. Bigger catches are a nice extra. |
| 7 | Ceremonial guard | Spear and round shield, parade livery | The spear is a long-reach melee weapon (a longer melee box). It reuses the shield from role 1. |
| 8 | Improvised militia | Hood made of scrap camo cloth, gas-cylinder launcher | A cheap single-shot launcher with low accuracy. Its ammo is crafted from iron and gunpowder. |
| 9 | Smuggler / cargo | Hidden storage compartment | Extra inventory rows. Extend `MODULE_CARGO_CRATE`. |

Each new part needs everything a faction part needed in the last handoff:
- geometry in the generator, with any capsule authored around the full-size pilot
- UV region and livery
- the item, recipe, item model, icon and lang entry
- a creative tab entry and a registry entry
- a slot in the `armor` autotest

A shield or weapon also needs a `Hold` that is verified over the full pitch range.

Make sure:
- **Mixing still works:** any role part can be combined with any faction part.
- **First person is never blocked:** capsules, shields and lights must not cover the view.
- **The rider clash check passes.** Fix the geometry; never weaken the check.
- **Effects stay server-authoritative:** they run on the server, and the client only renders.

## Testing

```bash
JAVA_HOME=$(/usr/libexec/java_home -v 17) ./gradlew build
JAVA_HOME=$(/usr/libexec/java_home -v 17) OBSOLETE_AUTOTEST=armor ./gradlew runClient
JAVA_HOME=$(/usr/libexec/java_home -v 17) OBSOLETE_AUTOTEST=anim ./gradlew runClient
JAVA_HOME=$(/usr/libexec/java_home -v 17) OBSOLETE_AUTOTEST=gameplay ./gradlew runClient
```

Add `gameplay` steps that prove each effect. Each step logs `PASS` or `FAIL`:
- A projectile fired at the shield's front does no damage, and one fired from behind does.
- A mech with the float ring placed in deep water ends up at the surface.
- The rescue lights raise the light level next to the mech at night.
- Each new melee or long-reach weapon damages a target.
- The drill breaks blocks faster with the worksite set.

Run `gameplay` **3 times**; every step must pass every time. Screenshots go to `run/screenshots/autotest_*.png`.

Keep scratch files and backups outside `src/` and `tools/`.

## Reviewer checklist

1. Phase 0 is done: the grenade launcher and step height pass 3 runs in a row, the tier HUD shots are distinct, the
   loadout screen is readable, the weapon-hold check is consistent, and the Outlander patches are fixed.
2. Phase 1 is done: measured before/after silhouette numbers hit the targets; every hold, the seat, the clash check and every armor set were re-verified on the new frame; side-by-side screenshots are attached.
3. At least 6 roles, including the 4 required ones, each with a working gameplay effect proven by a `gameplay`
   step.
4. Nothing is copied from the official site: general proportions only; names, detailing, colours and markings are our own.
5. Generators re-run cleanly; the rider clash check passes; bone names and parents unchanged, and pivots moved only for Phase 1 with an updated baseline.
6. Every new part renders alone and mixed across factions; first person is never blocked.
7. `./gradlew build` passes, and all autotests finish with no `Caused by`.
8. Small commits on `main`, nothing pushed, and a short report of what was verified and what was not.
