# Titan Combat - Changelog

All notable changes to the **Titan Combat** mod will be documented in this file.

---

## [2.7.3] - 2026-11-02 (Ocean Carrier Overhaul)
- Rebuilt Oceanic Super-Carrier as an LHD-style amphibious assault ship (island, rotating radars, CIWS, numbered flight deck, red antifouling waterline).
- Fixed mirrored "MARINES" stencil on one side of the V-22.

## [2.7.2] - 2026-11-02 (Transport Vehicle Model Overhaul)
- Rebuilt V-22 Osprey (tilting nacelles, counter-rotating proprotors), 8x8 Armored APC (slat armour, RWS turret, live wheel spin/steer) and Mobile Suit Trailer (armored tractor, 24-tyre lowboy, mech cradle) models, textures and icons.

## [2.7.1] - 2026-11-02 (Transport Vehicle Fixes)
- Chinook now turns with A/D.
- V-22 Osprey descends with the Descend key (Alt) instead of Shift.
- Vehicle Wrench returns the correct item for the Osprey, APC and Mobile Suit Trailer (previously gave a Hauler Truck).
- Added missing item models for the Osprey, APC and Mobile Suit Trailer.
- Paint Spray Can now applies faction livery to transport vehicles; colour is kept through wrench/redeploy.
- Rebuilt CH-47 Chinook model, texture and icon; rotors stay still when parked.

## [2.4.0] - 2026-11-01 (Expansion Titan Frames & Epic Modular Armor Overhaul)

### Epic Modular Armor Archetype Overhaul (8 Distinct 3D Silhouettes)
- **8 Distinct 3D Armor Visual Archetypes**:
  - **Infantry**: Standard tactical military composite armor, brow searchlights, grab bars, boxy pauldrons.
  - **Siege**: Super-heavy reactive armor slabs (ERA bricks), massive bunker blast shields, bulldozer shin armor, face cage.
  - **Samurai**: Crescent moon kabuto horned crest, 3-tiered flared ō-sode shoulder armor wings, articulated thigh haidate tassets, bladed knee guards.
  - **Aero**: Swept aerodynamic delta winglets on shoulders, chevron chest intake cowl, calf stabilizer fins with jump-jet cowlings.
  - **Scrap**: Welded rebar cage, barbed wire wrap, asymmetrical bolted scrap sheets, welded rebar spikes.
  - **Stealth**: Faceted radar-absorbent diamond carbon cowls, low-profile heat sink gills, angular chamfers.
  - **Sovereign**: Regal gilded imperial eagle/lion breastplate, sovereign crown crest, winged royal commander pauldrons with gold trim.
  - **Expedition**: Twin cyclone air pre-cleaner canisters flanking the head, storage cargo canisters strapped to chest/shoulders, sealed all-terrain gaiters.
- **Dynamic 3D Armor Transformation**: Equipping armor pieces now dramatically transforms the 3D shape and silhouette of all 6 Titan Frames.
- **Armor Swapping & Dismantling**:
  - Right-click with a new theme piece to instantly swap and salvage the old armor item back into inventory.
  - Sneak + Right-Click with an empty hand to safely dismantle installed armor pieces and return them to the player.
- **Survival Crafting Recipes**: Added craftable recipes for all 4 armor items (`HEAD`, `CHEST`, `ARMS`, `LEGS`).

### Model "BULLANT" Autonomous Anti-Tank Hexapod Overhaul
- **Complete Visual & Mechanical Rebuild**:
  - Replaced legacy quadruped with an authentic **6-legged hexapod walking battle tank** based on the Canopus Model "Bullant" reference.
  - **6 Arched Articulated Legs**: Arched upper thigh beams, under-mounted hydraulic cylinders with chrome rods, rotary knee disk hubs, forward knee shields with white military triangle decals (`▼`), and segmented caterpillar crawler cleat feet.
  - **Tripod Hexapod Walking Kinematics**: $180^\circ$ anti-phase tripod walking gait with smooth knee flexion and subtle hull heave.
  - **Dual Dorsal Anti-Tank Missile Pods**: Twin 4-tube missile pods ($2 \times 2$) mounted on articulated gantry arms with hazard warning striping and exposed rocket warheads.
  - **Armored Snout & Chin Autocannons**: Slanted faceted forward snout with periscope sight slit, side cowlings, and dual chin autocannons.
  - **Canopus 360 Camera Dome**: 2-axis gimbal base with spherical camera pod and glowing cyan optical aperture lens.
  - **Coyote Desert Khaki Coating**: High-resolution tactical matte finish with panel lines, rivets, and full spray camo/dye support.

### 3 New Modular Titan Frames (Mass-Production & Multi-Legged Archetypes)
- **Terrain Ground Titan Frame (T-04 / Mass-Production Tactical Ground Mech)**:
  - Designed based on tactical mass-production military specifications.
  - **Calf Tank Treads**: Armored caterpillar tank tracks integrated on the back of each lower leg calf (`caterpillar_left`, `caterpillar_right`) with drive sprockets, track road wheels, and heavy mudguards.
  - Forward-slanted cockpit canopy, optical sensor turret on the roof, dual rear heat radiator grills, reinforced knee guards, and stomper feet with ground traction cleats.
- **Cyclops Industrial Heavy Frame (C-05 / Gorilla Industrial Heavy Walker)**:
  - Inspired by heavy industrial and engineering walkers with a distinctive silhouette.
  - **Glowing Cyan Cyclops Eye Dome**: Prominent central panoramic dome visor lens with vivid cyan sensor glow.
  - **Hunched Gorilla Posture**: Low center of gravity, heavy boxy shoulders with hazard caution striping, and dual vertical industrial exhaust smokestacks emitting engine heat.
  - **4-Toed Outrigger Stabilizing Feet**: Wide 4-claw stabilizing claw feet for unmatched recoil mitigation and maximum stability when firing heavy howitzers or rotary cannons.
- **Spider Anti-Tank Hexapod Frame (S-06 / Autonomous Walking Tank)**:
  - Multi-legged walking anti-tank platform featuring 6 articulated legs, dual missile pods, and low-slung armor.

### Modular Customization & Compatibility Across All 6 Frames
- **Modular Armor Integration**:
  - All 6 frames start in their bare chassis form and accept all 4 modular armor pieces (`HEAD`, `CHEST`, `ARMS`, `LEGS`) across all **17 Armor Themes** (`TitanArmorTheme`) and **8 Visual Archetypes**.
- **Paint Spray & Dye System**:
  - Full support for `PaintSprayCanItem` with 9 camo finishes (Steel, Desert, Woodland, Urban, Snow, Crimson, Cobalt, Hazard, Black Ops) generated at high resolution for all 3 frames (27 total texture maps).
  - Full dynamic recoloring with all 16 Minecraft Dyes (`DyeItem`).
- **Universal Weapon & Core Module Hardpoints**:
  - Seamlessly equips all handheld primary weapons (Heavy Assault Rifle, Rotary Gatling, MLRS Rocket Pod, SMG, Leadwall, Splitter, Howitzer, Mining Drill, Chainsaw).
  - Fully supports Back Equipment Modules (M-120 Howitzer, MLRS-6 Rocket Pod, Cloaking Core, Phase Warp Core, Sonar Scanner).
  - Custom glider wing and jump-jet flight module mounting offsets.

### Deployment Beacons & Crafting
- **Dedicated Frame Beacons**:
  - `Terrain Frame Drop Beacon` (`terrain_frame_beacon`)
  - `Cyclops Frame Drop Beacon` (`cyclops_frame_beacon`)
  - `Spider Frame Drop Beacon` (`spider_frame_beacon`)
- **Universal Multi-Switch Cycling**: Right-click the universal `Titan Frame Drop Beacon` or cycle between all 6 frame models (`Striker -> Vanguard -> Colossus -> Terrain -> Cyclops -> Spider`).
- **Crafting Recipes**: Unique survival recipes for all new frame beacons using redstone components, iron, netherite, copper, and amethyst/glowstone.

---

## [2.3.0] - 2026-11-01 (Custom Weapon Arsenal Expansion: Heavy Assault Rifle, Rotary Gatling & MLRS-6 Back Rocket Pod)

### Custom-Modeled Primary & Back Weapon Arsenal
- **Titan Heavy Assault Rifle (AR / Battle Rifle)**:
  - Custom procedural 3D model: Bullpup receiver, Picatinny tactical rail, holographic reflex sight with glowing lens, vented handguard with cooling slots, 4-port muzzle compensator, ergonomic foregrip, and curved 32-round combat magazine.
  - Balanced rapid-fire kinetic assault weapon with crisp velocity, high accuracy, and spent brass casing ejection.
- **Titan Rotary Heavy Machine Gun (Gatling)**:
  - Custom procedural 3D model: 6-barrel rotary cluster, cylindrical stator motor housing, massive side drum magazine with hazard caution striping, flexible armored ammo feed chute, and dual rear spade grips.
  - Devastating sustained suppression fire (120-round drum, 10 rounds/sec fire rate, roaring sound and continuous casing cascade).
- **MLRS-6 Titan Back-Mounted Rocket Launcher Pod**:
  - Custom procedural 3D model: Armored rectangular 6-tube box missile launcher pod with hydraulic elevation arm, exposed rocket warhead cones with glowing tip sensors, rear exhaust deflection ports, and caution hazard markings.
  - Dual deployment:
    - **Back Equipment Module (Slot 13)**: Mounts above the right shoulder/back, fired via **Key [L]** to unleash a rapid 4-missile salvo barrage with smoke contrails and high-explosive area impact.
    - **Handheld / Weapon Bay (Slot 12)**: Equipped directly as a primary heavy rocket pod with 12 missiles.
- **1st-Person Cockpit View Integration**:
  - Full first-person visual rigs for all new weapons inside the cockpit (`trooper_titan_1st.geo.json`), dynamically toggled based on the active weapon.
- **Universal Chassis Compatibility**:
  - Fully compatible with all 13 chassis (Trooper, Scout, Shade, Ion, Scorch, Ronin, Tone, Legion, Monarch, Northstar, Striker Frame, Vanguard Frame, Colossus Frame) with seamless 3rd-person held and stowed back-clamp rendering.

---

## [2.2.0] - 2026-11-01 (Modular Titan Frames, 3D Kinetic Ballistics & Tactical Smoke Mortar)

### Modular Titan Frames (New Chassis Archetypes)
- **Titan Frame System**: Bare mechanical frames displaying exposed skeletal hydraulics, linkages, and rollcage cockpit.
- **3 Frame Variants**:
  - **Striker Frame (S-01)**: Lightweight, swept agile chassis with twin-dash mobility and high speed.
  - **Vanguard Frame (V-02)**: Balanced main battle chassis with standard box-section I-beams and all-round combat efficiency.
  - **Colossus Frame (C-03)**: Super-heavy siege juggernaut with massive dual hydraulic columns, 100% knockback resistance, and maximum mortar stability.
- **Modular Armor Attachments**:
  - Right-click with `TitanArmorItem` to equip modular armor pieces on `HEAD`, `CHEST`, `ARMS`, and `LEGS`.
  - Seamless 3D bone visibility toggling directly integrates armor plates onto the frame.
- **Full Color & Camo Customization**:
  - Complete support for `PaintSprayCanItem` (9 Camo indexes: Steel, Desert, Woodland, Urban, Snow, Crimson, Cobalt, Hazard, Black Ops).
  - Full compatibility with all 16 Minecraft dyes (`DyeItem`).
  - Dynamic synchronized coloring ensures all equipped armor plates match the chassis camo/tint.

### 3D Kinetic Ballistics & Spent Shell Casings (Ported & Titan-Scaled from Obsolete)
- **3D Kinetic Bullet Tracer**: Replaced simple item throwable with high-velocity 3D incandescent tracer rounds (`TitanBulletEntity` & `TitanBulletRenderer`) featuring supersonic flyby snap sounds, smoke contrails, and heavy impact sparks.
- **Spent Shell Casings**: Firing ballistic titan weaponry automatically flings heavy caliber brass casings (`TitanCasingEntity` & `TitanCasingRenderer`) out the right ejection port, complete with 3-axis tumbling spin, ground bounce physics, copper clink collision audio, and lingering hot smoke wisps.

### M-120 Howitzer Smoke System & Concussive Blast
- **Heavy Concussive Muzzle Blast**: Howitzer shots now produce expanding smoke shockwave rings, breech venting, ground dust displacement around titan footings, and intense camera feedback.
- **M-120 Tactical Smoke Shells**: New shell rack item (`HOWITZER_SMOKE_SHELLS`). Lobbed shells burst into a dense 12m volumetric smoke screen lasting 25s that pacifies enemy mob targeting and conceals allied mechs.

---

## [2.1.0] - 2026-10-28 (Mass-Production Redesign & M-120 Howitzer)

### Mass-production titans
- **Trooper rebuilt in the Letheus style**: helmet with visor slit, amber chest cylinders and belt pouches, digital camo, boxy pauldrons with grab handles, tall knee guards.
- **Scout rebuilt as a 30MM-style light frame**: ball joints everywhere, segmented plates, small sensor head, back plate packs, three-toed feet.
- **Shade rebuilt as a boxy heavy walker** under a torn camouflage cloak with ghillie tufts; roof-mounted gun.
- Joint hubs, hydraulic rams and hoses on all three; loaded stance (bent knees, torso hunched over the hips) on every titan.
- Light Recon SMG redesigned (top tube, carry loop, long straight magazine, ribbed foregrip).

### M-120 back howitzer (new)
- Skill module for the back equipment slot: the titan keeps its hand weapon.
- **[K] tactical map**: blue top-down map of loaded terrain with range rings; left-click designates, right-click designates and fires on lock. Also **[N]** rangefinder mark, typed coordinates, and **Up/Down** range corrections.
- **[L] fire**. The gun traverses and elevates onto the target before it can fire (LAYING / LOCKED on the HUD), recoils, and the titan braces in a firing stance.
- Range 24-160 m, loaded terrain only; the server re-checks every target. Shells come in 4-round racks loaded automatically.

### Fixes
- Unarmed titans no longer flail their arms: the swing follows the leg stride.
- Salute raised the hand behind the head; it now comes up to the visor.
- Transports: **[B]** releases / hot-drops the carried titan and **[Left Alt]** descends the drone; Shift is only for getting out.
- Generators borrow texture patches by material, so model changes no longer recolour the SMG or cockpit arms.

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
