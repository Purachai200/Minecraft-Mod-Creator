# AGENT MISSION BRIEF: TITAN TRANSPORT VEHICLE REALISM & MOUNTING OPTIMIZATION

> **Target**: Refine 3D geometry realism, texture fidelities, and Titan passenger seating/sling accuracy for 3 strategic transport vehicles in `Titan Combat` (Minecraft 1.20.1 / Forge 47.4.10 / GeckoLib 4).  
> **Skill Ref**: [.agents/skills/geckolib-model-architect/SKILL.md](../.agents/skills/geckolib-model-architect/SKILL.md)  
> **Core Generator**: [generate_transport_assets.py](scripts/generate_transport_assets.py)

---

## 1. TECHNICAL PARAMETERS & COORDINATE MATRIX

| Axis | Vector | World Direction | Scale Factor | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Length** | $\pm Z$ | $-Z = \text{Forward (Nose/Bow/Cab)}$, $+Z = \text{Aft (Bed/Stern)}$ | $16\text{ units} = 1.0\text{ block}$ | GeckoLib flips yaw $180^\circ - \text{yaw}$ |
| **Width** | $\pm X$ | $+X = \text{Port (Left)}$, $-X = \text{Starboard (Right)}$ | $1\text{ unit} = 0.0625\text{ m}$ | Centerline at $X = 0$ |
| **Height**| $\pm Y$ | $+Y = \text{Up}$, $Y = 0 = \text{Ground / Keel}$ | $1\text{ unit} = 6.25\text{ cm}$ | Ground plane contact |

### Titan Entity Dynamic Offsets
* Titan Base Dimensions: Width 2.4b, Height 4.6b, Depth 2.2b.
* **Kneeling Pose (`loaded` anim)**: Lowers root $Y$ by $-1.4\text{b}$ ($-22.4\text{u}$), shifts forward $+1.0\text{b}$ ($+16\text{u}$).
* **Upright Pose (Sky-Crane Hot-Drop)**: `shouldTitanKneel() == false`. Full height 4.6b.

---

## 2. PASSENGER ALIGNMENT & DECK OFFSETS

```
[Hauler Truck (8x8)]                  [Sky-Crane Drone (VTOL)]             [Cargo Barge (Catamaran)]
Z_model = +33 (Centered)              Z_model = 0.0, Y_model = -42.0       Bay 1: Z_model = -50.0 (Fwd, +3.1D)
Deck Y  = 16..20                      Rig Spreader: Y = -42.0              Bay 2: Z_model = -11.0 (Mid, +0.7D)
CARGO_OFFSET: (0.0, 2.50, -2.1)       VENTRAL_MOUNT: (0.0, -6.85, 0.0)     Deck Y = 6..10 (Flush Y = 0.65D)
Stance: Kneeling in straps            Stance: Upright Hot-Drop in air      CARGO_OFFSET_A: (0.0, 0.65, 3.1)
                                                                           CARGO_OFFSET_B: (0.0, 0.65, 0.7)
                                                                           Wheelhouse starts at Z_model = +54
                                                                           Clear walkway >3.5b before bridge
```

### Exact Code Anchor Files
- `TitanHaulerTruckEntity.java` -> `CARGO_OFFSET = new Vec3(0.0D, 2.50D, -2.1D)`
- `TitanSkyCraneDroneEntity.java` -> `VENTRAL_MOUNT_OFFSET = new Vec3(0.0D, -6.85D, 0.0D)`, `shouldTitanKneel() -> false`
- `TitanCargoBargeEntity.java` -> `CARGO_OFFSET_A = (0, 0.65, 3.1)`, `CARGO_OFFSET_B = (0, 0.65, 0.7)`, `shouldTitanKneel() -> false`

---

## 3. VEHICLE UPGRADE DIRECTIVES (SIGNAL DENSE)

### 🚛 Vehicle A: 8x8 Heavy Transporter Hauler Truck
- [ ] **Winch Assembly**: Central winch spool at `Z = -84`, 4-way roller fairlead, 2x forged tow shackles on bumper face.
- [ ] **Cab Ergonomics**: Split windshield (`Z = -71.1`), center divider post (`X = 0`), 5x amber roof markers, twin air horns (`Y = 59`), side snorkel with cyclone canister (`X = -29.5`).
- [ ] **Rear Bed Rigging**: 
  - Titan sits at $Z = +33$. Ratchet straps anchor at $Z = +18$ (front) and $Z = +48$ (rear).
  - Cross-knee tensioner bar at $Z = +28$, $Y = 22$. Cast-steel ratchet buckles at $(X = \pm 23..28, Y = 22, Z = 20)$.
- [ ] **Chassis Detailing**: 4x axle differentials `[-5, 9, Z_axle]`, walking beam tandem leaf springs, rear commercial tail lights (red/amber/white) + mudflaps at $Z = +88.5$.

### 🚁 Vehicle B: Heavy Sky-Crane VTOL Drone
- [ ] **Nacelles & Stators**: 4 ducted fan cowlings (dia 28, h 12). Add internal 4-point aerodynamic stator vanes + spinning 4-blade rotors with $45^\circ$ yellow tips.
- [ ] **Canopy & Optics**: Chiseled faceted nose `Z = -64..-42`, chin FLIR sensor turret ball with cyan glowing optic lens `[0, 220, 255]`.
- [ ] **Suspension Rig**:
  - Ventral winch drums recessed in hull `Y = 12..14`.
  - 4x cyan-glowing magnetic lift cables (`Y = 12 -> -42`, angles $[4^\circ, 0^\circ, \pm 8^\circ]$).
  - Spreader-bar frame at $Y = -42$ with 4x magnetic clamp shoes mating precisely to Titan shoulder hardpoints.
- [ ] **Ground Clearance**: Quad tubular landing skids (`Y = 2..5`, length 72) with dual oleo shock struts per skid.

### 🚢 Vehicle C: Catamaran Cargo Landing Barge
- [ ] **Hull Hydrodynamics**: Twin wave-piercing pontoons with $45^\circ$ bow wedges and keel strakes (`Y = 0..3`).
- [ ] **Bow Ramp**: Hinged drop-ramp at $Z = -98..-74$ angled $-16^\circ$. Dual hydraulic lift cylinders + chrome piston rods.
- [ ] **Dual Cargo Bays**: 
  - Bay 1 ($Z = -40$): 4x orange diagonal tie-down straps around Titan 1 legs/chassis.
  - Bay 2 ($Z = +20$): 4x orange diagonal tie-down straps around Titan 2 legs/chassis.
  - Separation: 3.75 blocks clear deck between bays; no model clipping.
- [ ] **Wheelhouse Bridge**: Outward-slanted panoramic bridge glass, port/starboard bridge wings with safety railings, mast with rotating radar scanner, orange circular life buoys on bulkheads, twin transom waterjet thrusters.

---

## 4. TEXTURE ATLAS MEMORY MAP (512x512 PNG)

```
+------------------------+------------------------+
| (0,0) [128x128]        | (128,0) [64x64] Glass  |
| Armor Panels & Hull    | (192,0) [64x64] Optics |
|                        | (256,0) [128x64] Frame |
|                        | (384,0) [128x128] Deck |
+------------------------+------------------------+
| (0,128) [128x64]       | (128,128) [128x64]     |
| Hazard Stripes         | Orange Ratchet Straps  |
| (256,128) [128x64]     | (384,128) [128x64]     |
| Exhausts / Hydraulics  | Winch Spool / Louvers  |
+------------------------+------------------------+
| (0,192) [128x64]       | (128,192) [128x64]     |
| Skids / Life Buoys     | Lights / Axles         |
+------------------------+------------------------+
| (0,256) [128x128]      | (128,256) [128x128]    |
| Lug Tire Treads        | Steel Rim + 8 Lug Nuts |
+------------------------+------------------------+
```

---

## 5. VERIFICATION WORKFLOW & RUNBOOK

Execute the following sequential terminal commands to validate changes:

```bash
# 1. Regenerate JSON Models, Animations, and PNG Textures
python3 "Titan Combat/scripts/generate_transport_assets.py"

# 2. Verify Java Compilation
cd "Titan Combat" && ./gradlew compileJava

# 3. Headless/Automated In-Game Visual Test (Captures 6 camera angles)
TITAN_AUTOTEST=transport ./gradlew runClient

# 4. Inspect Visual Output Screenshots
# run/screenshots/autotest_transport_01_hauler_truck_mounted.png  (Fleet Trio)
# run/screenshots/autotest_transport_02_truck_cargo_bed.png       (Cab & Winch)
# run/screenshots/autotest_transport_03_skycrane_drone_airlift.png (Drone Rig)
# run/screenshots/autotest_transport_04_cargo_barge_twin_titans.png (Twin Bays)
# run/screenshots/autotest_transport_06_skycrane_cockpit_view.png  (Tail & Straps)

# 5. Production Build & CurseForge Instance Deploy
./gradlew build -x test
cp build/libs/titancombat-2.0.0.jar "/Users/purachai/Documents/curseforge/minecraft/Instances/Tactical Frontier Line/mods/"
```

---

## 6. DEFINITION OF DONE (ACCEPTANCE CRITERIA)

1. **Zero Clipping**: Titan feet must sit flat on diamond-plate deck ($Y_{\text{surface}}$), not float or intersect hull.
2. **Physical Straps**: Orange straps must visibly wrap over Titan armor knees/shoulders with ratchet buckle hardware.
3. **Sky-Crane Hot-Drop**: Slung Titan must hang fully airborne with 4 taut cables connecting to shoulder lifting lugs.
4. **Barge Twin-Bay Spacing**: Bay 1 and Bay 2 must maintain $\ge 3.5$ blocks clear separation with non-skid walkway.
5. **Texture Crispness**: No UV stretching or pixel bleeding across 512x512 atlas partitions.
