# Titan Combat - Changelog

All notable changes to the **Titan Combat** mod will be documented in this file.

---

## [1.6.2] - 2026-10-24 (Flight Module Fixes)

### Flight modules
- Fixed titans occasionally spinning/rolling wildly: procedural aim, lean, salute and foot-placement offsets were stacking up every frame on bones the current clip didn't animate.
- Rocket jump-jet pack remodelled and retextured (shaded tanks, intake grille, flared glowing nozzles) and mounted flush on every chassis' back instead of floating off it or being buried in Scorch/Legion's backpacks.
- Jetpack exhaust now leaves the actual nozzle exits, following torso aim and lean.

## [1.6.1] - 2026-10-23 (Pilot Immersion Overhaul)

### Cockpit & HUD
- **Real first-person cockpit**: the canopy frame, instrument base and the titan's own arms + weapon are now rendered around the camera (per-chassis first-person models and animations: firing, melee punches/sword combos, walk/run sway). Replaces the old full-screen image, which was actually a model texture sheet.
- **New Titanfall-style HUD**: boot sequence on embark, compass tape, radar, angled hull/shield bars, dash cells, core meter, per-weapon reticles with target lock, critical/doomed alerts, fading control hints. Reduced HUD in third person.
- **Cockpit Bay screen redesigned**: live titan preview, status bars, framed reactor / munitions / 3x3 cargo slots with ghost icons.

### Movement, animation & sound
- Footsteps are now sound keyframes in each walk/run animation, timed to the measured moment each foot lands, with ground dust and cockpit shake. Removed the fixed-timer and vanilla step sounds.
- Ground speed is matched to each chassis' stride, so feet no longer slide. Heavy inertia when starting/stopping; **sprint** (vanilla sprint key) switches to the run gait.
- Animation controllers rebuilt (legs / arms / full-body) so kneel, drop and boarding poses no longer fight the idle arm pose (fixes crossed/backwards arms while kneeling).
- New stand-up and boarding sequences (titan lifts the pilot in before it can move).
- Melee winds up and lands mid-swing with a short lunge, impact FX and screen shake; Ronin chains core sword combos in Overdrive.
- Guns fire from the weapon muzzle and converge on the crosshair; hold the trigger for automatic fire; muzzle flash and per-weapon recoil.

### Feel & combat (playtest round 2)
- Fixed titans freezing with no animation after the first park/stand cycle (GeckoLib does not restart a stopped controller given the same clip; all controllers now force a reset on clip changes).
- Weapons now switch between hand and back like the addon (models carry two copies of each gun/sword and both were showing). Parked titans stow the gun so the lowered hand is free for the pilot; Ronin draws its sword for melee.
- Summoned titans land and settle into the parked "waiting for pilot" pose with the cockpit hatch open; boarding closes the hatch and the titan stands up automatically.
- Torso follows the pilot's aim (pitch + waist twist) while the legs turn after it; body leans into acceleration and turns.
- Shots no longer drop with gravity, so they land on the reticle at range.
- Dash: 3 charges per tank and dashes carry further; Space with no direction fires jump jets. Thruster exhaust on dash/jump/sprint, landing impact, no fall damage.
- Armor plating against gun mods (TACZ, Superb Warfare, vanilla): small arms mostly ricochet, heavy calibers and explosives still hurt, titan weapons do full damage. Hits on the seated pilot are redirected to the hull.
- Defense Matrix shows a pulsing blue energy barrier around the titan.

### Weapons (playtest round 3)
- **Swappable weapons**: 7 titan weapon modules (Splitter Rifle, T-203 Thermite Launcher, Leadwall, 40mm Tracker Cannon, Predator Cannon, XO-16 Chaingun, Plasma Railgun) fit any chassis via the new weapon slot in the cockpit bay. The gun model and first-person rig follow the mounted weapon.
- **Magazines & dedicated ammo**: each weapon has its own magazine size, reload time and ammo item; [R] reloads (titan bay first, then pilot inventory), auto-reload when dry. Old Titan Ammo still works as a generic magazine.
- **Raise before firing**: the arm must bring the gun to firing position (Predator Cannon spins up) before the first round leaves the barrel.
- **Holster**: [H] stows the gun on the titan's back and relaxes the arms; pulling the trigger draws it again.
- Per-weapon damage, spread, pellets, ignition and explosive rounds.

### Fixes (playtest round 4)
- Titans now arrive **unarmed**; they can't fire until a weapon module is installed in the bay's weapon slot (HUD and bay show "NO WEAPON").
- Lowering the weapon [H] keeps the gun in hand at a low-ready hip carry instead of making it vanish; the first-person rig dips out of the sight line.
- Fixed titans looking squashed flat / "spinning" when jumping: foot placement no longer pulls the body to the ground while airborne.
- Kneel [Z] is debounced (client and server), so holding Z no longer toggles repeatedly.
- Cockpit bay LIVE preview now shows the titan even when opened from inside the cockpit.
- Dev tooling: scripted in-game playtest with screenshots (`TITAN_AUTOTEST=... ./gradlew runClient`, see `client/debug/ClientAutoTest`).

### Fixes (playtest round 5)
- Sprinting no longer spins the first-person arm/weapon rig (the addon's sprint sway rotated it up to 180°; replaced with the walking bob). This also caused the "titan not holding its gun" look while sprinting.
- Shots land exactly on the crosshair in first and third person: the client sends the point under the reticle from the real camera (verified in-game: hits within ~2 cm).
- Unarmed titans relax both arms instead of gripping an invisible gun.

### Eject
- [X] twice (or once when critically damaged): the hatch blows, the ejection seat rockets the pilot ~30 blocks up on a flame trail with slow-fall, and the abandoned titan self-destructs 2.5 s later.
- Fixed the client blocking server-approved dismounts (pilot stuck "inside" after eject / stray "Titan is standing" messages).
- Foot placement waits for the titan to settle after landing; jump jets a little higher.

### Terrain
- Walking/running no longer sinks the titan: the model is lifted by each chassis' measured foot dip in its walk/run clips.
- Steps up/down are eased instead of snapping (chassis and cockpit camera).
- Standing on uneven ground: the pelvis lowers and the higher leg bends so both feet rest on the ground.
- Legs tuck into the thruster pose while airborne.

### Pilot position
- Pilot eye position is measured per chassis for standing and kneeling, and the pilot is hidden inside the sealed hull. Third-person camera pulled back to frame the titan.

### Items
- All 13 item textures redrawn as 32x32 pixel art; tools use handheld models.

## [1.5.0] - 2026-10-22 (Combat Overhaul & Cockpit Immersion Update)

### 🚀 Highlights & Features
- **Cockpit Riding Position Alignment**: Overrode riding positioning to `getY() + 4.85D` with directional offset, placing the pilot directly behind the chest visor and cockpit instruments instead of at the legs/crotch.
- **Dual-Channel GeckoLib Animation Architecture**:
  - Independent `legs` and `arms` controllers allowing dynamic upper/lower body articulation.
  - Continuous animated locomotion: `walk.leg` + `move.arm` while walking, `spurt.leg` on dash, and natural breathing `idle.leg` + `idle.arm`.
  - Simultaneous walking and firing: Titan walks with legs while aiming and shooting with arms.
  - Eliminated rigid/malfunctioning embark wait poses (`loaded`) by transitioning deployed mechs into natural combat-ready stance.
- **Titan Cockpit & Cargo Bay GUI (`E` Key)**:
  - Mounted pilots can now press `E` to open the Titan's integrated Cockpit Container.
  - Dedicated **Munitions Bay** slots: stores kinetic ammunition directly in the Titan, prioritized during firing.
  - Dedicated **Core Reactor Battery** slot: automatically recharges shields and overdrive core.
  - 9-slot **Cargo Bay** for field repairs, iron ingots, and supplies.
  - Also accessible from outside by Shift+Right-Click with an empty hand.
- **Melee Combat & Blade Strikes (`F` Key)**:
  - Added dedicated melee attack key (default `F`).
  - Ronin executes sweeping Broadsword slashes dealing 60–90 damage with authentic impact audio.
  - Other Titan classes execute heavy chassis punches dealing 38–45 damage with knockback and fire effects.
- **Authentic Titanfall Audio & Soundscape**:
  - Heavy rhythmic mechanical footstep stomps (`titan_step_1`..`4`) with ground resonance.
  - High-thrust rocket engine dash audio cues (`titan_dash_1`..`3`).
  - Pneumatic hydraulic airlock boarding (`cabin_enter`) and exit sounds (`cabin_exit`).
  - Weapon firing audio for all 7 classes (Scorch, Tone, Ronin, Monarch, Legion, Northstar, Ion).
- **First-Person Cockpit Dashboard Canopy Overlay**:
  - Integrated authentic high-resolution cockpit dashboard canopy framing (`cockpit_canopy.png`) in 1st person mode.

## [1.1.1] - 2026-10-21 (Hotfix: Animation Parsing & Crash Fix)

### 🐛 Bug Fixes & Stability
- **GeckoLib Bedrock Array Crash Fix**:
  - Fixed a critical startup crash (`JsonSyntaxException: Not a JSON Object`) during asset loading overlay.
  - Sanitized all 7 Titan animation files (`ion`, `scorch`, `ronin`, `tone`, `legion`, `monarch`, `northstar`) by stripping invalid Bedrock-specific particle array definitions that were incompatible with GeckoLib 4 on Minecraft Java.
  - Entities now load and play their authentic high-framerate animations smoothly without errors.

---

## [1.1.0] - 2026-10-21 (The Maintenance & Intelligent Titans Update)

### 🚀 Highlights & Major Features
- **7 Ported High-Fidelity Titan Classes**:
  - **Ion**: Energy Splitter Rifle with high-precision beam discharge.
  - **Scorch**: Incendiary Thermite Launcher dealing area fire damage.
  - **Ronin**: Leadwall kinetic shotgun firing multi-pellet spread.
  - **Tone**: Semi-automatic 40mm Tracker Cannon with explosive ordnance.
  - **Legion**: High-rate-of-fire Predator Minigun with suppressive barrage.
  - **Monarch**: XO-16 Chaingun with automated shield siphon restoration.
  - **Northstar**: High-velocity Plasma Railgun sniper delivering massive critical strike damage.
- **Intelligent Pathfinding & Hazard Avoidance (ระบบ AI หลบหลีกสิ่งกีดขวางอัจฉริยะ)**:
  - **Lava Protection**: Automatic pathfinding malus and forward probe sensor stopping Titans before entering lava pools.
  - **Steep Cliff / Ravine Fall Prevention**: Terrain height sensor detecting sheer drops (> 3 blocks). Engages emergency brakes during AI walk and cockpit brake assist for pilots.
  - **Natural Foliage Trampling**: Titans heavy march crushes natural leaves, bushes, vines, and tall grass with sound effects without littering clutter.
  - **Player Base Protection**: Completely protects player-placed leaves (`LeavesBlock.PERSISTENT == true`) and all construction blocks.
  - **Anti-Stuck Watchdog**: Remote navigation watchdog halts movement after 60 ticks of obstruction and transmits emergency coordinates back to the pilot's radio.
- **Swappable Core Battery & Charging Infrastructure (ระบบสลับแบตเตอรี่และแท่นชาร์จ)**:
  - **Depleted Core Battery (`empty_battery`)**: Inserting a battery into a Titan recharges shields/energy and returns an empty battery casing to the pilot.
  - **Battery Charging Station (`battery_charger`)**:
    - **Forge Energy (FE) Compatible**: Connects seamlessly with power cables from tech mods (Mekanism, Create, Thermal, EnderIO).
    - **Standalone Vanilla Fueling**: Accepts Coal, Charcoal, Redstone, Blaze Rods, Coal Blocks, and Lava Buckets directly via right-click.
    - **Dynamic VFX**: Live electric spark particles and audible audio cues during charging.
- **Multiplayer Security & Customization**:
  - **Biometric Pilot License**: Prevents unauthorized pilots from stealing or hijacking registered Titans.
  - **Hangar Docking Pad (`hangar_dock`)**: Architectural parking pad providing trickle repairs and standby display poses.
  - **8 Camouflage Colorways**: Dyeable using vanilla Minecraft Dyes or Faction Spray Cans.
  - **Immersive First-Person Cockpit HUD**: Reticle brackets, canopy framing, and hull/shield telemetry.

---

## [1.0.0] - 2026-10-21 (Initial Release)
- Initial release with Aegis Striker baseline chassis.
- Core GeckoLib entity integration and multiplayer network packet sync.
