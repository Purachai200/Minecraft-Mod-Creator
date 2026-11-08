---
name: flan-model-design-standard
description: >-
  Studio-grade military vehicle modeling and texturing standard reverse-engineered from Flan's Mod (Global Firestorm & British Military Pack).
  Covers ShapeBox micro-facet geometry, 2048px UV atlas unwrap, baked ambient occlusion, mechanical greebling hierarchy, and bytecode extraction pipelines for Minecraft 1.20.1 GeckoLib 4.
---

# Flan's Military Model Design Standard

This specification defines the studio-grade modeling, texturing, and mechanical detailing standards reverse-engineered from **Flan's Mod** (`Global Firestorm` & `British Military Pack`). It establishes the exact mathematical formulas, geometry topology, UV atlas conventions, and greeble hierarchy required to produce top-tier military vehicles in **Minecraft 1.20.1 Forge / GeckoLib 4**.

---

## 1. Architectural Modeling Philosophy: The "ShapeBox Micro-Facet" Standard

In standard Minecraft modding, vehicles are often built from large, blocky axis-aligned cubes. Flan's Mod models achieve their hyper-realistic look through **micro-facet decomposition** using `addShapeBox`:

### A. The 8-Vertex Displacement Principle
Instead of a rigid cuboid, every major structural facet is an 8-vertex deformed hexahedron with independent corner offsets $(\Delta x_i, \Delta y_i, \Delta z_i)_{i=0}^7$:

```
        v7 ---------- v6         Top Face (+Y)
       / |           / |
      v3 ---------- v2 |
      |  |          |  |
      |  v4 --------|- v5        Bottom Face (-Y)
      | /           | /
      v0 ---------- v1
```

* **Compound Tapering:** Wings, sponsons, and tail booms taper simultaneously along two axes (e.g. thinning vertically while narrowing horizontally toward the tip).
* **Canopy & Cockpit Arching:** The canopy glass is composed of 12 to 24 narrow longitudinal facet strips where top vertices are displaced inward by $15^\circ-30^\circ$, creating a curved bubble cockpit with zero visible cubic seams.
* **Sloped Armor Plates:** Turret cheeks and frontal glacis plates displace top vertices rearward, creating authentic ballistic deflection slopes ($60^\circ-70^\circ$).

### B. Structural Component Layering Hierarchy

Every vehicle must be modeled across five distinct geometric layers:

| Layer | Component Scope | Box Count Budget | Visual Role |
| :--- | :--- | :--- | :--- |
| **0: Primary Airframe / Hull** | Cockpit tub, fuselage shell, tail boom, engine cowlings, main hull chassis | 250 – 400 cubes | Establishes the silhouette, aerodynamic taper, and ground clearance |
| **1: Articulated Mechanics** | Rotor mast, swashplate, pitch rods, hinges, landing gear struts, wheel scissor links | 150 – 250 cubes | Provides mechanical credibility; animates with flight, roll, and steering |
| **2: Sensor Pods & Optics** | TADS/PNVS nose turret ball, FLIR optics, radomes, HUD projector, periscope prisms | 80 – 150 cubes | Makes the vehicle feel like an active military weapons platform |
| **3: Weapon Stations & Pylons** | Hardpoint pylons, missile launch rails, Hellfire/TOW racks, rocket pods, autocannons | 120 – 250 cubes | Displays combat payload readiness with recessed rocket tubes and ammo feeds |
| **4: Functional Greebles** | Wire strike cutters, pitot tubes, antenna blades, chaff/flare buckets, engine exhaust shrouds | 80 – 150 cubes | Eliminates flat surfaces; provides ultra-fine micro-detail |

---

## 2. Rotor & Articulation Engineering (Helicopters)

### A. Main Rotor Mast Assembly
Never attach rotor blades directly to a flat roof. An authentic military helo rotor mast consists of:
1. **Stationary Base Mast:** Hexagonal or octagonal vertical shaft rising from the transmission deck ($r = 2.5\text{ px}$, $h = 8\text{ px}$).
2. **Rotating Swashplate Disc:** Lower fixed swashplate ring connected to 3 hydraulic actuators ($45^\circ$ angles), mated to an upper rotating swashplate ring.
3. **Pitch Horn Control Rods:** 4 to 5 vertical steel rods connecting the upper swashplate to the blade root cuffs.
4. **Blade Folding Hinges & Dampers:** Horizontal elastomeric lead-lag damper cylinders at each blade root.
5. **Tapered Aerodynamic Blades:** Each blade is divided into 2–3 segments with a negative aerodynamic twist (washout) and swept blade tips.

### B. Tail Rotor & Fenestron
* **Pusher/Tractor Orientation:** Offset to the port or starboard side of the vertical fin ($8-12\text{ px}$ from fin centerline).
* **Pitch Links:** Visible central hub delta-3 pitch hinge pins.
* **Fenestron (Ducted Fan):** For enclosed tail rotors (e.g. Comanche), model an 8-sided ducted shroud cut into the vertical stabilizer with a miniature 8-blade fan inside.

---

## 3. Master UV Atlas & Texturing Standard

Flan's Mod models derive their visual depth from master-unwrapped UV atlases ($1024\times1024$ for ground armor, $2048\times2048$ for complex airframes):

### A. 3-Pixel Panel Seam Algorithm
Flat Minecraft textures look cartoonish. Authentic military sheet metal panels use a 3-pixel relief bevel:
1. **Pixel 0 (Sunward Highlight):** Base color lightened by $+15\text{ to }+25$ luminance (simulates sun reflection on sheet edge).
2. **Pixel 1 (Groove / Shadow):** Base color darkened by $-40\text{ to }-60$ luminance (the recessed panel gap).
3. **Pixel 2 (Ambient Shadow):** Base color darkened by $-15\text{ to }-25$ luminance (ambient shadow inside the joint).

### B. Rivet Spacing & Hardware Fasteners
* Place perimeter rivets at regular intervals along armor plate edges ($4\text{ to }6\text{ pixels}$ pitch).
* Each rivet consists of a **bright specular center pixel** surrounded by a **crescent dark shadow pixel** underneath.
* Use hex-bolt patterns for removable service access hatches and engine cowling latches.

### C. Baked Ambient Occlusion (AO)
Simulate global illumination directly in the texture map:
* **Recesses & Undersides:** Darken underwings, sponson bellies, and landing gear wells by $30-45\%$.
* **Exhaust Soot Burn:** Apply a soft-gradient radial mask of carbon black `(28, 28, 30)` spreading from exhaust outlets rearward along the airflow path.
* **Non-Skid Walkways:** Add high-frequency noise grit to cabin entry thresholds, wing walks, and flat deck surfaces.

### D. Tactical Stencil & Decal Density
Authentic military vehicles must include high-resolution tactical stencils:
* `"DANGER - KEEP AWAY FROM ROTOR"` on tail booms in tactical white or black stencil lettering.
* Yellow rescue arrows pointing to emergency cockpit release handles.
* Red/white intake warning triangles around turbine air intakes.
* Subdued national roundels and low-visibility faction serial numbering.

---

## 4. The Bytecode Extraction & Conversion Pipeline

To port legacy models from Flan's Mod (1.7.2 through 1.12.2) into modern GeckoLib 4 with 100% fidelity:

### A. The Bytecode Stack VM Parser
Flan's models are compiled Java classes with hardcoded `ModelRendererTurbo` calls. Extract them using the following bytecode virtual machine pipeline:

```python
# 1. Disassemble class with javap
javap -p -c ModelName.class

# 2. Track stack operations:
#    - iconst_*, bipush, sipush, ldc -> push numbers
#    - invokespecial ModelRendererTurbo.<init>(u, v, w, h) -> capture UV offset
#    - invokevirtual addShapeBox(...) -> extract 31 parameters:
#        (x, y, z, w, h, d, 0, x0..z7)
#    - invokevirtual setRotationPoint(rx, ry, rz) -> capture bone pivot

# 3. Ground Clearance Compensation:
#    shift_y = -min(raw_y_of_all_cubes)
#    Every cube origin y becomes: -(ry + y + h) + 24.0 + shift_y

# 4. Heading Alignment:
#    GeckoLib 'root' bone gets rotation [0.0, 90.0, 0.0]
#    This rotates Flan's longitudinal X axis to Minecraft's -Z nose forward
#    WITHOUT altering any UV mappings! Textures remain 100% pixel-perfect.
```

### B. Standard Bone Grouping Map
When parsing Flan's method names, automatically group boxes into GeckoLib animation bones:

| Flan's Method Substring | Target GeckoLib Bone | Animation Role |
| :--- | :--- | :--- |
| `mainrotor`, `helimainrotor` | `main_rotor` | Rotates around local Y axis (flight/idle) |
| `tailrotor`, `helitailrotor` | `tail_rotor` | Rotates around local Z axis (flight/idle) |
| `nose`, `cockpit`, `seat`, `hud` | `cockpit` | Cockpit interior & instrument displays |
| `skid`, `wheel`, `gear` | `skids` / `wheels` | Ground contact running gear |
| `leftwing`, `rightwing` | `wing_left` / `wing_right` | Weapon hardpoint pylons & stores |
| `turret`, `gun` | `turret` | Articulated autocannon or sensor ball |
| `tail`, `yaw`, `rudder` | `tail` | Tail boom & vertical/horizontal stabilizers |
| (Default / Hull) | `body` / `fuselage` | Tilts with vehicle pitch and hull roll |

---

## 5. Verification & Quality Checklist

Before finalizing any model following this standard, verify:
- [ ] **Ground Clearance:** Lowest skid/tire facet sits at $Y = 0.0 \pm 0.1\text{ units}$.
- [ ] **Forward Heading:** Vehicle nose points toward $-Z$ in Minecraft coordinates.
- [ ] **Rotor Pivots:** Main rotor pivot is centered on the mast axis $(X \approx 0, Z \approx 0)$.
- [ ] **Animation Integrity:** `main_rotor` spins continuously in `fly` (fast) and `idle` (slow).
- [ ] **No Flat Colors:** Every facet uses ambient occlusion, panel bevels, or weathered metal noise.
- [ ] **Faction Camouflage:** Supports all 7 tactical liveries (`Base`, `Woodland`, `Desert`, `Arctic`, `Urban`, `Naval`, `Stealth`).
