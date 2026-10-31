# OBSOLETE Exoframe — enclosed combat cockpits (handoff)

Goal: on every **combat** exoframe the pilot sits inside a closed cockpit. From any angle, standing, walking or
crouching, no part of the pilot shows through or behind the capsule. Today, seen from behind, the pilot's head and
shoulders stick out of the back of most capsules. A reviewer will check your work against the checklist at the end.

Read these first. Their rules still apply: `HANDOFF_REMAINING_WORK.md`, `HANDOFF_FACTIONS_WEAPONS_UI.md` (capsule
authoring, `round_ring`, `to_seat`, the rider clash check) and `HANDOFF_ROLE_VARIANTS.md` (the originality rule).
Commit in small steps on `main`. Do not push.

## What is wrong (measured, not guessed)

### 1. The capsules tilt away from the pilot (the main bug: it affects every set)

- Every `canopy_*` and `armor_chest_*` bone is a child of `torso`, with its pivot at the torso pivot `(0, 20, 0)`.
- Phase 1 added a hunched posture. The torso pitches forward about **15°** in `idle`, 10° in `walk` and 12° in
  `crouch` (`tools/build_exoframe_anims.py`, `stance_clip` / `gait`). The capsule tilts with it.
- The pilot is a separate entity, placed by `ExoframeEntity.positionRider`. It does not tilt.
- At head height (about 19 px above the pivot) the rear wall moves forward about **4–5 px**. The pilot's back and
  head end up behind the wall.
- `idle` also lowers the pelvis by 2 px and the seat does not follow. (Crouch is already matched: 6 px in both
  places.)
- The rider clash check in `tools/build_exoframe_geo.py` only tests the **bind pose**, so it passes while the
  animated mech leaks.

### 2. Some combat capsules really are open at the back

This is how much of the pilot's back silhouette (torso + head, seen from straight behind) is covered by capsule
cubes behind the pilot, in the bind pose:

| Capsule | Faction | Rear cover |
|---|---|---|
| `canopy_usmc` | Marine Raider | 100% |
| `canopy_hood` | Outlander | 95% |
| `canopy_shiden`, `canopy_specter`, `canopy_valkyrie`, `canopy_police`, `canopy_rescue` | | 99–100% |
| `canopy_riverine` | Riverine | **32%** |
| `canopy_cerberus` | Pegaso Black | **28%** |
| `canopy_khamsin` | Khamsin | **22%** (posts + sun shade) |
| `canopy_salvage` | Salvage | **8%** (roll hoop) |
| `canopy_polar` | Polar Front | **0%** |

### 3. Clearances are paper-thin

- The roof and back walls were raised just enough to pass the clash check. The `usmc` roof sits **0.07 px** above the
  pilot's head.
- A head pitched by looking down (vanilla rotates the head about the neck), a walk bob or the idle "breathe" pushes the
  head through the roof.

## Tasks

### Task 1 — keep the cockpit locked to the pilot (do this first)

- The pilot must stay fixed relative to the capsule in every clip: `idle`, `walk`, `sprint`, `crouch`,
  `crouch_walk`, `shoot`, `melee`, emotes.
- Pick one approach and explain the choice in the commit message:
  - **(a) Counter-rotate:** in `ExoframeModel.setCustomAnimations`, give each visible `canopy_*` / chest bone the
    inverse of the torso's animated rotation and position.
    - It shares the torso pivot, so `rotX = -torso.getRotX()` (and the same for Y and Z) cancels the tilt exactly.
    - Also cancel the pelvis drop that the seat doesn't follow.
    - The frame still hunches; the cockpit stays level with the pilot.
  - **(b) Move the pilot with the pose:** apply the same pitch and drop to the seat point and to the pilot model
    (`positionRider`, `ExoframeRiderPose`).
    - This is harder: the server doesn't know the animation state, and the pilot would lean.
  - **(c) Hunch without pitching the torso:** take the hunch out of `torso` and build it from the yoke, arms and pelvis
    instead.
    - Re-check the Phase 1 silhouette targets if you do this.
- Whatever you pick: the hold IK in `ExoframeArmIK` reads the torso pose. Re-verify the weapon holds
  (`tools/verify_weapon_holds.py`) and look at the `anim` screenshots.

### Task 2 — close every combat cockpit

- **Combat capsules:** Marine, Pegaso Black, Polar Front, Outlander, Salvage, Shiden, Khamsin, Riverine, Specter,
  Valkyrie, Police.
  - Each needs a closed rear: a back wall, an armored rear hatch or an engine/battery housing directly behind the
    pilot.
  - Each needs a roof or a closed top.
  - The pilot looks out through a vision slit, a visor or cameras.
- **Exceptions:** only civilian or industrial cockpits may stay open: `armor_roll_cage` (worksite) and the rescue
  winch evacuee seat.
- **Keep each faction's character** (and follow the originality rule):
  - Pegaso: armored tub with a raised rear hatch and a low roof.
  - Polar: closed insulated drum.
  - Salvage: welded scrap plates, crude but closed.
  - Khamsin: closed body with the sun shade on top.
  - Riverine: closed hull with the snorkel.
- **Use what exists:**
  - `round_ring(..., front=...)` for rings.
  - `to_seat()` for the seat fit.
  - Capsules are authored around the full-size pilot, as in the other `canopy_*` blocks.
- **Mind the neighbours:** the rear wall must clear the backpack and utility modules (`backpack_*`,
  `upper_back_seat`). Moving the pilot back was tried and hits `backpack_cargo` / `backpack_ammo`. Move the backpacks
  back or reshape them instead.

### Task 3 — real clearance, checked in the poses that ship

- Roof and walls must sit at least **1.0 model px** (after `to_seat`) clear of the rider envelope. The envelope must
  include a head pitched ±30° about the neck.
- Extend the geometry checks so they run against the **posed** capsule (torso and pelvis at the extremes the clips
  actually reach), not only the bind pose.
  - Read the extremes from the generated animation JSON. Don't hard-code 15°.
  - Fix geometry when the check fails. Never weaken the check.
- Add a **rear-cover check** like the table above: at least 95% for every combat capsule in every checked pose.
  The script below measured the table; adapt it. It runs on the generator's state before the clash check.

```python
src = open("tools/build_exoframe_geo.py").read()
g = {"__file__": "x"}; exec(compile(src[:src.index("def overlaps(a, b")], "gen", "exec"), g)
C, R = g["C"], g["RIDER"]
torso, head = R[0], R[1]
x0, x1 = torso[0], torso[0] + torso[3]
y0, y1 = torso[1], head[1] + head[4]
zback = max(torso[2] + torso[5], head[2] + head[5])
def rear_cover(cubes, n=40):
    hit = sum(any(c[0] <= x0 + (i + .5) * (x1 - x0) / n <= c[0] + c[3] and
                  c[1] <= y0 + (j + .5) * (y1 - y0) / n <= c[1] + c[4] and c[2] >= zback - 0.2 for c in cubes)
              for i in range(n) for j in range(n))
    return hit / n / n
for name in g["CANOPIES"]:
    print(name, f"{rear_cover(C[name]):.0%}")
```

### Task 4 — first person and comfort

- Capsules must still vanish in first person (`firstPersonHiddenBones` in `ExoframeVariantRegistry`), so a closed
  cockpit never blocks the view.
- If a closed set gets a cockpit-frame overlay in the HUD, it must follow the frame-tier rules in
  `HANDOFF_FACTIONS_WEAPONS_UI.md` and never cover the crosshair.

## Testing

```bash
JAVA_HOME=$(/usr/libexec/java_home -v 17) ./gradlew build
JAVA_HOME=$(/usr/libexec/java_home -v 17) OBSOLETE_AUTOTEST=armor ./gradlew runClient
JAVA_HOME=$(/usr/libexec/java_home -v 17) OBSOLETE_AUTOTEST=anim ./gradlew runClient
JAVA_HOME=$(/usr/libexec/java_home -v 17) OBSOLETE_AUTOTEST=gameplay ./gradlew runClient
```

- The `armor` autotest already takes `c_<set>_piloted_front/back/firstperson` for every set.
- **Add** a piloted rear 3/4 view and a piloted walking view for every combat set. The current shots are all idle, and
  the leak is worst in the idle hunch.
- Autotest steps now run on the **server** clock (`ClientAutoTest.onClientTick`). Don't go back to counting client
  frames.
- Run `gameplay` 3 times: every step must pass every time.
- Open the screenshots and look at them. Zoom into the rear views.

## Reviewer checklist

1. Task 1 is done: the pilot does not move relative to the capsule in any clip. Rear and 3/4 piloted shots in idle,
   walk and crouch show no pilot outside the capsule.
2. Every combat capsule is closed at the back and the top. The rear-cover check reports at least 95% in the
   bind pose and the posed checks. Only the worksite cage and the evacuee seat are open.
3. Clearance is at least 1.0 px including head pitch. The clash check and the new posed checks pass. No check was
   weakened.
4. First person is never blocked. All weapon holds still pass `verify_weapon_holds.py`.
5. Faction character and the originality rule are kept: nothing is copied from the official site.
6. Generators re-run cleanly. `./gradlew build` passes. `armor`, `anim` and `gameplay` ×3 finish with no
   `Caused by`.
7. Small commits on `main`, nothing pushed, and a short report of what was verified and what was not.
