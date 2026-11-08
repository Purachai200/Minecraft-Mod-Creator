# MASTER AGENT BRIEF: REALISTIC MILITARY & ASYMMETRIC TRANSPORT VEHICLES MOD

> **Project Target**: Design and build high-fidelity, ultra-realistic 3D models and Java entities for a dedicated **Minecraft 1.20.1 Forge / GeckoLib 4** vehicle & logistics mod.  
> **Core Identity**: Gritty, realistic, battle-proven military, irregular militia, and converted civilian logistics fleet (inspired by authentic real-world vehicles: Toyota Land Cruiser Technicals, Ural/KamAZ 6x6, Civilian Tramp Freighters, and Soviet Mil Mi-17 helicopters).  
> **Compatibility**: Seamlessly transports both **Obsolete** Exoframes and **Titan Combat** Titans with realistic weight/size tier limits.

---

## 1. CORE PILLARS & DESIGN PHILOSOPHY

### 🚫 What NOT to Do (Anti-Patterns):
* **Do NOT build stiff, flat, Minecraft-blocky shapes:** Real machines are not shipping containers with wheels glued to them. Real vehicles have subtle curves, compound angles, raked windshields, chamfered armor edges, and cylindrical fuselages.
* **Do NOT use single square cubes for wheels:** Real off-road wheels are round (minimum 12-sided dodecagonal geometry), with deep lug treads, recessed beadlock rims, lug-nut rings, and central axle hubs.
* **Do NOT micro-restrict the design with rigid hardcoded coordinates:** Focus on authentic anatomical proportions, functional mechanical parts, and visual silhouettes.

### 🌟 Mandatory Architectural Features:
1. **Interactive Walkable Moving Platforms (Walkable Decks):**
   - Players must be able to jump onto truck beds, walk around inside helicopter cargo holds, and roam ship decks **without pressing right-click to ride as a passenger**.
   - As the vehicle drives, flies, or sails, non-passenger players standing on top must smoothly move and rotate with the vehicle without rubberbanding, jittering, or falling off.
   - Standing players can aim, reload, and fire weapons in a 360-degree arc while someone else is driving.
2. **Strict Payload Tier & Size Limits:**
   - **Tier 1 (Light):** Armed Technical 4x4, Patrol Boats. Maximum cargo size: $\le 1.2\text{m} \times 2.4\text{m}$. **Can ONLY carry Obsolete Exoframes**. Heavy Titans are strictly rejected with an overweight warning.
   - **Tier 2 (Medium):** 6x6 Heavy Hauler Truck, Mi-17 Transport Helicopter. Can carry **1 Titan Combat Titan** OR **2 Obsolete Exoframes**.
   - **Tier 3 (Heavy / Strategic):** Lowboy Heavy Semi-Trailer, Civilian Tramp Freighter, LCAC Hovercraft. Can carry **2+ Titans** OR **a platoon of 4-6 Exoframes**.
3. **Battlefield / CoD-Style Tactical Seating HUD (Bottom-Left UI):**
   - Top-down 2D schematic wireframe of the vehicle.
   - Visual seat nodes showing: Driver [1] (Steering wheel icon), Co-pilot [2], Bed Gunner standing zones [3/4], and Cargo Dock status (name of docked mech, HP, and battery charge FE).
   - Real-time seat switching via number hotkeys.
4. **Driver Forward View-Lock:**
   - When driving inside an enclosed cab, the driver's head and torso must lock to the vehicle's forward heading, with natural looking clearance through the windshield and zero head clipping through the roof.
5. **Studio-Grade Weathered Textures:**
   - No flat solid plastic colors. Surfaces must feature Perlin/smooth noise shading, gravity-driven rain grime streaks, bare-metal paint chips along high-friction edges, non-skid grit on walking decks, and realistic weld beads along seams.

---

## 2. VEHICLE FLEET SPECIFICATIONS & REAL-WORLD ANATOMY

---

### 🚛 CATEGORY 1: GROUND TRANSPORTS (ยานพาหนะทางบก)

#### 1. Heavy Tactical Technical 4x4 (Militia Gun Truck)
* **Real-World Reference:** Armed Toyota Land Cruiser 79 / Oshkosh JLTV / Desert Gun Truck.
* **Real-World Visual Characteristics:**
  - **Silhouette & Stance:** High ground clearance, aggressive off-road stance with level rake, heavy solid front and rear live axles.
  - **Front End:** Heavy welded pipe bullbar with corner brush guards, center-mounted recovery winch with roller fairlead and forged D-ring tow shackles, ribbed engine hood with cooling louvers and raised power cowl, classic slotted grille with stone-guarded round projector headlights.
  - **Cab:** Rugged, upright armored cab (not a sports-car rake), 2-seat interior (driver left, passenger right) with steering wheel, gear shifter, and dashboard gauges. A-pillar deep-fording air snorkel with cyclone pre-cleaner canister. Low-profile roof rack with LED light bar and tactical whip antenna.
  - **Rear Cargo Bed (Walkable Deck):** Heavy diamond-plate non-slip floor. Tubular steel headache rack / roll-cage directly behind cab with rear floodlights. Side tie-down rails with orange ratchet straps. Articulated drop tailgate that folds down $90^\circ$ into a level walk-on ramp. Bed-side mounted fuel Jerrycan and waffle traction recovery boards.
* **Operational Role:** Tier 1 Light Transport. Carries 2 seated crew + 2 standing bed gunners + 1 Obsolete Exoframe clamped in the bed.

#### 2. Heavy 6x6 Off-Road Hauler Truck (The Iron Workhorse)
* **Real-World Reference:** Ural-4320 / KamAZ-6350 / KrAZ-255 / Oshkosh HEMTT.
* **Real-World Visual Characteristics:**
  - **Silhouette & Stance:** Massive snout-nosed 6x6 heavy diesel truck with long hood, high cab, dual vertical exhaust stacks puffing black diesel smoke behind the cab, and tandem rear dual-axle walking beam suspension.
  - **Chassis & Running Gear:** 6 massive high-flotation mud tires with deep V-treads, visible propeller shafts, differential pumpkins, and heavy steel frame rails.
  - **Cargo Bed:** Enormous wooden or ribbed-steel open flatbed. Walkable deck accommodating an entire squad walking around. Side drop-sides and rear fold-down ladder.
* **Operational Role:** Tier 2 Medium Transport. Carries 2 seated crew + 6 standing riders + **1 Titan Combat Titan (locked in kneeling stance with heavy chains)** OR **2 Obsolete Exoframes**.

#### 3. Lowboy Heavy Semi-Trailer (Heavy Mech Transporter)
* **Real-World Reference:** Oshkosh M1070 HET (Heavy Equipment Transporter) with multi-axle lowboy trailer.
* **Real-World Visual Characteristics:**
  - **Prime Mover Tractor:** Giant 8x8 armored cab-over or long-nosed tractor unit with high-mounted winches behind the cab for hauling disabled mechs onto the trailer.
  - **Lowboy Trailer:** Extremely low deck clearance (just above ground) to allow tall Titans to pass under bridges and trees. Articulated hydraulic dual loading ramps at the rear that lower to the ground.
* **Operational Role:** Tier 3 Heavy Strategic Transport. Carries 1 Super-Heavy Titan or 4 Exoframes.

---

### 🚢 CATEGORY 2: NAVAL VESSELS (ยานพาหนะทางน้ำ)

#### 4. Civilian Coaster Tramp Freighter (เรือสินค้าชายฝั่งพลเรือนดัดแปลง)
* **Real-World Reference:** Coastal Tramp Cargo Ship / Converted Smuggler Feeder Vessel.
* **Real-World Visual Characteristics:**
  - **Hull & Keel:** Long, low-freeboard steel hull showing heavy weathering, rust streaks from hawseholes, welded patch plates, and waterlines. Raised forecastle bow with anchor windlass and mooring bitts.
  - **Cargo Hold / Open Well Deck:** Large recessed central cargo hold with raised coamings. Paved with steel deck plates where players, vehicles, and mechs can walk freely while underway.
  - **Cargo Handling:** Working deck lattice-boom derrick crane positioned between the hold and forecastle. Shipping containers (20ft) stacked alongside mech tie-down cradles.
  - **Superstructure & Bridge:** Aft multi-deck wheelhouse with panoramic outward-slanted bridge windows, navigation wing platforms with safety railings, smokestack funnel, rotating radar scanner mast, and orange circular life buoys.
* **Operational Role:** Tier 3 Heavy Strategic Naval Transport. Transports 2 full-size Titans or 4-6 Exoframes + cargo crates across oceans. Full team can walk all decks and climb to the bridge.

#### 5. Amphibious Landing Craft Air-Cushion (LCAC / Hovercraft)
* **Real-World Reference:** Military LCAC / Zubr-class hovercraft.
* **Real-World Visual Characteristics:**
  - **Air Skirt:** Thick, segmented flexible black rubber skirt surrounding the hull, visibly inflated when operating, floating 0.35m above water and ground.
  - **Propulsion:** Twin giant aft ducted aerial thrust fans with aerodynamic steerable rudders.
  - **Open Drive-Through Deck:** Full-length flat cargo deck with hinged drop ramps at both the bow and stern for roll-on/roll-off capability.
* **Operational Role:** Tier 3 Amphibious Assault. Navigates smoothly from open ocean onto land/beaches. Carries 2 Titans or 4 Exoframes.

#### 6. Riverine Assault Patrol Boat (เรือตรวจการณ์แม่น้ำ)
* **Real-World Reference:** SOC-R (Special Operations Craft-Riverine) / PBR Mk II.
* **Real-World Visual Characteristics:**
  - Low-profile armored fiberglass hull, twin waterjet propulsion nozzles at the transom, center console helm, rear flat deck with pintle gun mounts, and space for 1 light Exoframe.
* **Operational Role:** Tier 1 Fast Coastal / River Transport.

---

### 🚁 CATEGORY 3: AIR TRANSPORTS (ยานพาหนะทางอากาศ)

#### 7. Mil Mi-17 "Hip" Tactical Transport Helicopter
* **Real-World Reference:** Mil Mi-8 / Mi-17 Hip multi-role heavy transport & assault gunship.
* **Real-World Visual Characteristics:**
  - **Fuselage:** Aerodynamic rounded ellipsoidal fuselage (NOT a box!). Blister greenhouse canopy with faceted multi-pane cockpit windows offering downward visibility.
  - **Engines:** Twin Klimov/Isotov TV3-117 turboshafts mounted above the cabin, featuring oval front particle separator air filters and side-angled oval exhaust ducts with dark heat discoloration and soot stains.
  - **Rotor Systems:** Massive 5-blade articulated main rotor with hub swashplate and downward gravity blade droop. High swept vertical tail fin carrying a 3-blade tail rotor and horizontal stabilizer wings.
  - **Rear Clamshell Doors:** Rear cargo doors split down the center and swing wide open ($65^\circ-90^\circ$) to reveal a fully walkable cargo cabin interior (fits 6-8 standing players).
  - **Ventral Mech Sling Rig:** Heavy-duty external ventral suspension system mounted beneath the fuselage at the center of gravity. Features high-tensile steel cables, a spreader-bar frame, and magnetic locking shoes to hoist **1 Titan Combat Titan** or **2 Obsolete Exoframes** beneath the helicopter for in-flight Hot-Drop deployment!
  - **Armament Outriggers:** Lateral tubular truss outrigger pylons carrying dual UB-32 unguided rocket pods (insurgent gunship conversion).
  - **Running Gear:** Heavy tricycle landing gear with oleo shock struts and 12-sided tires.
* **Operational Role:** Tier 2 Heavy Tactical Helo. Fast aerial insertion, walkable troop hold, and ventral sling drop.

#### 8. Tactical Turboprop Airlifter (C-130 Style Transport)
* **Real-World Reference:** Lockheed C-130 Hercules / Antonov An-12.
* **Real-World Visual Characteristics:**
  - 4 turboprop engines with spinning 4-blade propellers, high-mounted wings, side landing gear sponsons, massive pressurized interior cargo bay, and rear cargo ramp that lowers to the ground or opens mid-air for airdrops.
* **Operational Role:** Tier 3 Strategic Airlifter.

---

## 3. DELIVERABLES REQUIRED FOR EACH VEHICLE

When designing each vehicle, provide:
1. **Model Geometry (`.geo.json`):** Full GeckoLib 4 Bedrock format with clean hierarchy, standardized bone names (`steer_fl`, `wheel_fl`, `rear_tailgate`, `cargo_straps`, `main_rotor`), 12-sided wheels, and realistic sloped/curved surfaces.
2. **Texture Atlas (`.png`):** High-resolution 512x512 or 1024x1024 atlas featuring layered weathering (rain streaks, paint chips, weld lines, non-skid grit, and camo palettes).
3. **5-View Concept Verification Sheet:** A high-resolution $(720 \times 1800\text{ px})$ 5-panel orthographic/isometric concept sheet (Front 3/4, Rear 3/4 closed, Rear open ramp, Rear 3/4 open, True Side elevation) to verify proportions, ground clearance, and ergonomics before finalizing.
4. **Deck Collider Coordinates Matrix:** Exact local bounding box coordinates for the walkable `DeckColliderEntity` platforms and cargo clamp anchor slots.
