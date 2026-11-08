---
name: geckolib-model-architect
description: >-
  Master 3D geometry and bone hierarchy design standard for GeckoLib 4 vehicles, mechs, and heavy machinery in Minecraft 1.20.1 Forge.
  Guides the procedural creation of curved surfaces, 12-sided wheels, compound sloped armor, and articulated mechanics.
---

# GeckoLib Model Architect Standard

This skill governs the mathematical and structural creation of high-fidelity 3D voxel models for vehicles, aircraft, naval vessels, and mechs targeting **GeckoLib 4 / Minecraft 1.20.1 Forge**.

---

## 1. Coordinate Systems & Matrix Conventions

GeckoLib and Minecraft Bedrock geometry use a mirrored-X right-handed convention:

| Axis | World / Local Direction | GeckoLib / Script Vector | Notes |
| :--- | :--- | :--- | :--- |
| **Length (Z)** | Nose / Forward: $-Z$<br>Rear / Aft: $+Z$ | $+Z$ is Backward<br>$-Z$ is Forward | Java vehicle code uses local $+Z$ as Forward, so mirror $Z$ when mapping |
| **Width (X)** | Left (Port): $+X$<br>Right (Starboard): $-X$ | $+X$ is Vehicle Left<br>$-X$ is Vehicle Right | GeckoLib mirrors $X$ in the renderer; centerline is $X = 0$ |
| **Height (Y)**| Up: $+Y$<br>Down: $-Y$ | $Y = 0$ is Ground Plane | Wheel bottoms, skids, or keel bottom rest exactly at $Y = 0$ |
| **Scale** | $16.0\text{ units} = 1.0\text{ block} = 1.0\text{ meter}$ | $1\text{ unit} = 0.0625\text{ m} = 6.25\text{ cm}$ | Maintain authentic meter-to-block scale |

---

## 2. Advanced Geometry Construction Rules

### A. Dodecagonal (12-Sided) Rounded Wheels
Never use single rectangular boxes for wheels. A realistic military tire consists of **6 rotated strips with $30^\circ$ increments**:

```python
def make_dodec_wheel(cx, cy, cz, left, radius=11.0, width=7.5):
    """Generates a smooth 12-sided dodecagonal tire with beadlock rim disc and central hub."""
    x0 = cx - width / 2
    # 6 strips rotated by k * 30 degrees (apothem = radius)
    strip_depth = round(2 * radius * math.tan(math.radians(15)), 3)
    cubes = [{
        "origin": [x0, cy - radius, cz - radius * math.tan(math.radians(15))],
        "size": [width, 2 * radius, strip_depth],
        "pivot": [cx, cy, cz],
        "rotation": [k * 30, 0, 0],
        "uv": TYRE_CELL
    } for k in range(6)]
    
    # Recessed beadlock rim disc (6 strips at smaller radius)
    rim_r = radius * 0.62
    rx = x0 + width - 0.4 if left else x0 - 0.4
    cubes += [{
        "origin": [rx, cy - rim_r, cz - rim_r * 0.27],
        "size": [0.8, 2 * rim_r, round(2 * rim_r * 0.27, 3)],
        "pivot": [cx, cy, cz],
        "rotation": [k * 30, 0, 0],
        "uv": RIM_CELL
    } for k in range(6)]
    
    # Outer axle hub & brass valve stem
    hx = x0 + width + 0.4 if left else x0 - 1.6
    cubes.append({"origin": [hx, cy - 2.5, cz - 2.5], "size": [1.2, 5, 5], "uv": STEEL_CELL})
    return cubes
```

### B. Compound Angles and Sloped Armor (`rod()` Vector Helper)
To create aerodynamic windshields, slanted hoods, and beveled glacis plates, calculate the 3D unit vector between two 3D points $(p_0, p_1)$:

```python
def rod(p0, p1, width, thickness, uv_cell):
    """Draws a sloped plate or tubular bar connecting 3D point p0 to p1 with specified width and thickness."""
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-4:
        return {"origin": list(p0), "size": [width, thickness, thickness], "uv": uv_cell}
    # Euler rotation angles
    rx = -math.degrees(math.asin(dz / length))
    rz = math.degrees(math.atan2(dx, dy))
    origin = [p0[0] - width / 2, p0[1], p0[2] - thickness / 2]
    return {
        "origin": origin,
        "size": [width, length, thickness],
        "pivot": list(p0),
        "rotation": [rx, 0, rz],
        "uv": uv_cell
    }
```

### C. Curved Fuselage & Hull Slicing (`_zones`)
For aircraft fuselages and boat hulls, slice into quarter-ellipse bands rather than a flat box:
* 4-step rounded corners on top and bottom.
* Hollow interior to fit driver cockpit seats or walkable cargo bays.

---

## 3. Bone Hierarchy & Animation Conventions

Keep bone names strictly standardized so GeckoLib animation controllers match Java entity models:

```
root (pivot [0, 0, 0])
 └── body (pivot [0, axle_y, 0])
      ├── steer_fl (pivot [wheel_x, wheel_y, front_z])  <-- A/D steering rotation (rotY)
      │    └── wheel_fl                                  <-- Forward drive rotation (rotX)
      ├── steer_fr
      │    └── wheel_fr
      ├── wheel_rl                                       <-- Direct drive rotation (rotX)
      ├── wheel_rr
      ├── rear_tailgate (pivot [0, hinge_y, hinge_z])   <-- Articulated drop ramp (rotX 0..90)
      ├── turret (pivot [0, turret_y, turret_z])         <-- 360-degree aiming rotation
      └── cargo_straps                                   <-- Hidden when cargo is empty
```

---
## 4. Flan's Mod Studio-Grade Military Standard

When creating or remodeling military vehicles, aircraft, gunships, and armor, follow the specifications in `flan-model-design-standard`:
1. **Micro-Facet Layering:** Divide airframes and turrets into 5 functional layers (Hull, Mechanics, Optics, Pylons, Greebles).
2. **Compound ShapeBox Wedges:** Use vertex displacement techniques for curved cockpits, sponson bulges, and ballistic deflection slopes.
3. **Master 2048px UV Mapping:** 3-pixel panel relief seams (sunward specular + groove shadow), baked ambient occlusion, and military caution stencils.
4. **Bytecode Extraction Pipeline:** When porting legacy assets, use `flan_converter.py` to preserve 100% pixel-perfect UV mapping and auto-align ground clearance (`shift_y = -min_y`).

---

## 5. Verification Standard
Before approving any model:
1. Ground contact test: Lowest point of tire or skid must be $Y = 0.0$.
2. Driver eye alignment: Driver head position in Java must look directly through the windshield glass.
3. Cargo bed volume: Must accommodate the exact dimensions of its assigned Tier without clipping.
