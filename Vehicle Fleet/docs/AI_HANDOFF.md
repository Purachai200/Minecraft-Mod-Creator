# Hand-off brief for the logic AI (models are done; this is everything that still needs code)

Context: `Vehicle Fleet/` holds generated GeckoLib models + `docs/SPECS.md` (decks, seats, mounts per vehicle). Titan Combat (`../Titan Combat`) has the vehicle entities. I have **not** run the game and I have **not** inspected the SBW (Superb Warfare) jar: check its real entity/item ids and mount API yourself before wiring anything.

Regenerate models: `python "Vehicle Fleet/scripts/gen_fleet.py"`. Coordinates in specs are model px (16 px = 1 block, nose -Z, +X = vehicle left); convert as `seatWorldPos` does in `BaseTransportVehicleEntity`.

## 1. Seat-switch key (small)
- `BaseTransportVehicleEntity` already has `getPlayerSeatCapacity()`, `getPlayerSeatOffset(i)`, `getSeatedPlayers()`; the HUD seat map in `TransportVehicleHudOverlay.drawSeatMap` reads them. Seat i = i-th player in passenger order (see `seatOffset`), so "switching" today means reordering.
- Do: add a KeyMapping next to `KEY_RELEASE_CARGO` in `KeyInputHandler`, a C2S packet, and server code that moves the sender to the next free seat. Cleanest fix: store a per-player seat index (synced entity data / map) and make `seatOffset` use it instead of passenger order. Keep seat 0 = the controlling driver (`getControllingPassenger`).
- Allow players into seats > 0 for every vehicle that reports capacity > 1: the base `canAddPassenger` only lets a single player in; Osprey/APC override it. Mirror that override (or make it capacity-based).
- New capacities: technical 2, hauler 3, recovery 3, mi17 14, mi26 28, humvee 5, blackhawk 10, fac 6, opv 6, corvette 8, freighter 4 (also in each `seat_capacity` in SPECS.md).

## 2. Usable turrets (Humvee ring + ship hard-points)
- Models: Humvee bone `turret` (rotates about Y at [0,47,-2], locator `mount_roof`), ships bones `mount_*` = empty pedestal with the gun pivot as locator. Table of position / class / facing / arc / pitch per mount is in SPECS.md.
- Suggested design: a mount is a seat. A player who sits in a mount seat controls it: server rotates the mount from the rider's look yaw/pitch clamped to `arc`/`pitch`, fires on attack key. Render by setting the GeckoLib bone rotation (Humvee `turret`) or by spawning/anchoring the SBW gun entity at the locator and passing it the rider's aim.
- SBW: decide per mount class: `large` = ship cannon / AA gun, `pintle` = MG / CIWS-size gun. If SBW guns are entities with their own seat, ride them on the locator; if they are items, build a thin "mount block" that holds one. Do not let a gun's barrel intersect the hull: arcs in SPECS.md already assume a ~10 px ring.
- Humvee: the gunner stands on the cab floor (`gunner_stand` locator); the ring is on the roof, so put the gunner seat at that locator and make the rider's yaw drive `turret`.

## 3. Ships (fac_patrol, opv_cutter, corvette_stealth, coaster_freighter)
- Walkable: spawn `DeckColliderEntity` tiles from the `decks` boxes in SPECS.md (surface heights; slab ~0.25 block under the surface). The OPV/corvette helidecks are sized for the Mi-17/UH-60.
- Hull keel y=0, design waterline = each hull's `wl` (FAC 11, OPV 14, corvette 16, freighter ~24 px): derive the float offset from that.
- Animations per ship: `idle`, `radar_spin`. Freighter also `derrick_luff`.

### Ship interiors (new)
- All four ships are now hollow: below-deck compartments (floor y=8 px), stair hatches and walkable deckhouse tiers with furnished rooms (bunks, mess/galley, engine, stores, officers, bridge, hangar). Each `interior` line in SPECS.md lists rooms by z range; every room floor is in `decks` (`lower_deck`, `tier1_floor`, `bridge_floor`, ...).
- Floors only need `DeckColliderEntity` slabs at those heights. Walls, bulkheads and stairs are visual only: for a first version put slabs at the floor heights plus a ramp collider along each stair (stairs rise 4.5 px per 4.5 px run, i.e. 45 deg; walk-up needs step height 0.6 block = 9.6 px, so normal step-up works with floor slabs only if you also add a slab per stair step, or one inclined AABB list). Without wall colliders the player can walk through bulkheads; add thin wall slabs from the `wx`/`wz` boxes if that matters.
- Doors are 14 x 30 px (0.9 x 1.9 blocks); clear height 32+ px; aisles >= 14 px.

### Big three (lpd_assault, transport_sub, c17_airlifter)
- LPD: `stern_gate` bone opens with `gate_open` (-90 deg = flat ramp). Well deck floor y=20, flight deck y=124 (= bridge floor), island link walkway at z 8..20. Seats 10.
- Submarine: pressure hull is a dry model volume, so the Java entity needs its own rule for submerged riders (air pocket / no drowning) and for entering through the crown hatch (stair top at y=90 meets the casing deck at z=16). `swim` spins `prop`. Seats 14, cargo = 2 Exoframes.
- Airlifter: `cargo_ramp` opens with `ramp_open` (-135 deg = slope to the ground), `taxi` spins wheels; main cargo deck y=40 for 2 Titans / 4 Exoframes, 24 jump seats, crew rest and flight deck are forward of the door at z=-190. Wings are not walkable. Seats 27.

## 4. Aircraft / helper clips
- Mi-17, Mi-26, Black Hawk: play `sling` only while a Titan/Exoframe is hooked; every other clip scales the whole sling rig to 0, so an empty aircraft shows nothing underneath. Rotors: `fly` levels the drooped blades. Clamshell doors: `cargo_open` (Mi-17 / Mi-26). If the doors close inward instead of opening, flip `DOOR_OPEN` in `fleet_mi17.py` (Y rotation sign was derived, not verified in game).
- Trucks: `drive` spins wheels (steer via `steer_*` Y rotation), `tailgate_open`, `deck_open` (6x6), recovery `outriggers_down` / `crane_work`.
- Liveries: `textures/entity/<id>.png`, `_thai.png`, `_desert.png` share UVs.

## Not done / not verified
No Java entities, registries, lang, items or recipes exist for any vehicle in `Vehicle Fleet/`. Extents in SPECS.md ignore cube rotation (approximate). Nothing has been loaded in Minecraft.
