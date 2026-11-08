# Prompts for the cheaper AI

Copy a whole section as the first message. Part A = verify only (cheap, no edits to models). Part B = implement the Java side.

---

## PART A - Verify the walkable interiors (read-only)

You are verifying a generated Minecraft vehicle pack. **Do not edit any file under `Vehicle Fleet/scripts` or `Vehicle Fleet/assets`.** Your job is to run three checks, report exactly what they print, and flag anything suspicious. Be literal: quote output, do not guess or "fix".

Working directory: `Vehicle Fleet/scripts` (needs Python 3 and the sibling folder `Titan Combat/scripts`).

### Run these, in order
```bash
python collision.py --selftest
python gen_fleet.py
python audit.py
python collision.py
```

### What each one means
1. `collision.py --selftest` must print `selftest ok: ...`. If it asserts, the walk test itself is broken: stop and report.
2. `gen_fleet.py` rebuilds all 14 vehicles; it must finish without a traceback. Cube counts should be about: technical 370, ural 536, mi17 765, freighter 873, mi26 812, recovery 575+, humvee 334, blackhawk 745, fac 400, opv 690, corvette 817, lpd 813, sub 681, c17 965. Report any vehicle whose count differs by more than 10%.
3. `audit.py` lists "floating" cube groups (pieces not touching the main body). Expected: every vehicle `1 components`, except `fac_patrol` which may show one tiny floating item at y~9..11 (an engine-room pipe). Report any other floating group, with its bones and box.
4. `collision.py` exports `assets/vehiclefleet/collision/<id>.json` and walks a 9.6 x 28.8 px player (step 9.6 px) from an entry deck. Expected last line: `0 vehicle(s) with problems out of 14`. For any `!!` line, copy it with its vehicle name.

### Then sanity-check the JSON (read-only, a few lines of Python is fine)
For every `collision/<id>.json`:
- keys are exactly `unit`, `px_per_block`, `player`, `static`, `dynamic`; `px_per_block == 16`
- every box has 6 numbers with `x0 < x1`, `y0 < y1`, `z0 < z1`
- no box is larger than the vehicle extents printed by `gen_fleet.py` by more than 2 px
- `static` is non-empty; vehicles with doors/ramps/gates have a non-empty `dynamic`
- count of `static` boxes per vehicle (report them; anything above ~1500 is worth flagging)

### Known limits (do NOT report these as bugs)
- Seats are mount points; they are not walked to. Helicopter cockpits and ground-vehicle cabs are not entered on foot.
- Roof decks (`*_roof`) have no stairs and are skipped.
- Doors/ramps/gates/tailgates/drop-sides are excluded from `static` (the test treats them as open).
- The test has no jumping, swimming, or falling; stepping up/down is limited to 9.6 px.
- Tilted tubes/rails/panes (rotated on 2+ axes) and thin rails (<3 px) are not collision.

### Report format (max 25 lines)
```
selftest: ok/FAIL
gen_fleet: ok/FAIL (counts off: ...)
audit: ok / floating groups: ...
collision: N problems out of 14
  <vehicle>: <!! lines>
json: ok / violations: ...
verdict: PASS (all four clean) or FAIL (list what to hand back to the model author)
```

---

## PART B - Implement the interior physics in Java (Titan Combat / Forge 1.20.1)

Goal: players can walk inside moving, turning vehicles (ships, aircraft, trucks) and stay put relative to the hull. Do **not** spawn one collider entity per floor tile.

Data: `Vehicle Fleet/assets/vehiclefleet/collision/<id>.json` (copy to `src/main/resources/data/<modid>/vehicle_collision/<id>.json`). Units are model px, 16 px = 1 block; local frame: +X vehicle left, +Y up, nose at -Z; `static` = solid boxes `[x0,y0,z0,x1,y1,z1]`, `dynamic` = per-bone boxes for doors/ramps/gates in the closed pose.

Reference algorithm: `PlayerSolver` and `reach()` in `scripts/collision.py` (about 40 lines). Port it as-is:
1. Each tick, for each player standing on or inside a vehicle's bounding area (use the existing `DeckColliderEntity` / riding logic to know which vehicle): convert the player position to vehicle-local space (subtract vehicle position, rotate by -yaw; use the same convention as `BaseTransportVehicleEntity.seatWorldPos`, X = left; model px / 16 = blocks).
2. Apply the player's own movement (input delta) in local space, resolving against the static boxes with the same axis order as vanilla (Y, then X, then Z), step height 0.6 block, player AABB 0.6 x 1.8 blocks.
3. Carry the player with the hull: add the vehicle's per-tick position and yaw delta to the player (rotate the local offset by the yaw delta), so a turning ship does not slide the player.
4. Convert back to world space and set the player position/motion (server authoritative; send a correction packet if the client prediction differs by more than a small epsilon).
5. Doors, ramps, gates: when the animation is "open", skip that bone's `dynamic` boxes; when closed, include them.
6. Index boxes by a 16 px grid (like `PlayerSolver.grid`) so each tick only tests nearby boxes.
7. Disable vanilla gravity/ground checks for a player while the solver owns them; fall back to vanilla when the player leaves the vehicle's bounds.

Acceptance (write them as JUnit/GameTest or a debug command `/vehicle_walk_test <id>`):
- Walk from the entry deck to every deck listed under "Walkable deck colliders" in `docs/SPECS.md` without noclip.
- Cannot walk through bulkheads, stand inside furniture, or pass a gap narrower than 0.6 block.
- Stays in place when the ship yaws 90 degrees over 2 seconds.
- Submarine: define what happens to a player inside when the hull is submerged (no drowning inside the pressure hull volume).

Do not change the models or the generator; if a room is unreachable, report it back with the output of `python collision.py` and `python why.py <key>`.

---

## PART C - Real light from the lamps (so interiors are not dark at night)

What exists now (generated, do not edit): every enclosed walkable space has ceiling lamps in the model.
- Bone `lamps` in each `geo/<id>.geo.json` (small panels, material cell 22).
- `assets/vehiclefleet/lights/<id>.json`: `{"unit":"px","px_per_block":16,"level":13,"lamps":[[x,y,z],...]}` in the vehicle's local model frame (+X left, +Y up, nose -Z). Counts: fac 4, opv 12, corvette 14, lpd 24, sub 7, c17 23, freighter 14, mi17 2, mi26 3, blackhawk 2; trucks 0.
- `textures/entity/<id>[_thai|_desert]_glowmask.png`: 1024 mask where only the lamp panel is opaque.

Do these two things (both are needed; they solve different problems):

1. **Glow (visual, GeckoLib 4):** add `AutoGlowingGeoLayer` (or a hand-written emissive layer rendering `<texture>_glowmask.png` with `RenderType.eyes`/full-bright light) to every vehicle renderer, so the lamp panels stay bright in the dark. Check the active livery's glowmask name matches (`<id>_thai_glowmask.png` etc.).
2. **Real illumination (gameplay):** the glow does not light the world. Make the lamps emit block light:
   - Preferred: place vanilla `minecraft:light` blocks (level 13, `waterlogged=false`) in AIR at each lamp's world position (transform lamp local px -> blocks -> rotate by vehicle yaw -> add vehicle position, same convention as `BaseTransportVehicleEntity.seatWorldPos`; lamp y is the panel; place the light block 1 block below it so it is in the air).
   - Only update when a vehicle moved/turned enough that a lamp changed block cell (compare the set of target block positions with the previously placed set; remove only the difference). Never place into non-air blocks; never place when the chunk is not loaded; remove all of a vehicle's light blocks when it despawns, unloads, or moves away from all players by more than 64 blocks.
   - Keep a per-vehicle registry (`Set<BlockPos>`) saved in the entity NBT so light blocks are cleaned up after a crash/reload.
   - Optional switch: lamps on only when `level.isNight()`/sky light is low or when a player is aboard (cheap) and a toggle key for the pilot.
   - Alternative if a dynamic-lights mod is already a dependency (e.g. Forge 1.20.1 "Dynamic Lights" compat): register each lamp as a light source at its world position instead of placing blocks; use that if it exists, else the block approach.
3. **Entity render brightness inside:** the hull is not blocks, so the renderer samples world light at the entity position (often full sky light even indoors). In each vehicle renderer, override `getPackedLight` for the interior view: use `max(blockLight from the lamps, 4)` and ignore skylight when the camera is inside the vehicle's `lower_deck` / tier / hangar volumes (the decks listed in `docs/SPECS.md`).

Acceptance:
- At night, standing in the OPV lower deck and the corvette bridge: `/gamerule` unchanged, the room is visibly lit, the lamp panels glow, and F3 shows block light about 10-13 at head height near a lamp.
- Driving/sailing for 60 s leaves no stray `minecraft:light` blocks behind (check with `/fill ~-60 ~-20 ~-60 ~60 ~20 ~60 air replace minecraft:light` before and count with `/execute if blocks`, or log the registry size).
- 24 lamps (LPD) updating while turning stays under 0.3 ms/tick of server time.
