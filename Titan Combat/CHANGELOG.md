# Titan Combat - Changelog

All notable changes to the **Titan Combat** mod will be documented in this file.

---

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
