---
name: vehicle-texture-weathering
description: >-
  Studio-grade procedural texture generation, weathering shaders, and military camo patterns for vehicles and mechs.
  Covers rain-streaks, paint chips, weld beads, non-skid deck grit, mud accumulation, and tactical stencil lettering.
---

# Vehicle Texture Weathering & Surface Shaders

This skill details procedural texture rasterization techniques for generating realistic, battle-worn, industrial textures on 512x512 and 1024x1024 atlases without flat solid colors.

---

## 1. Texture Atlas Layout (64x64 Material Cells)

The texture atlas is organized into 64x64 pixel cells. Every cube face is mapped directly into its material cell:

```
[Row 0, y=0..63]:    [0: HULL]   [64: HULL_DARK] [128: APPLIQUE] [192: DECK_NONSKID] [256: MUD_BELLY] [320: CHASSIS_STEEL] [384: BARS_BLACK] [448: GRILLE]
[Row 1, y=64..127]:  [0: TYRE]   [64: RIM_BEAD]  [128: RUBBER]   [192: GLASS_TINT]   [256: OPTIC_CYAN] [320: LENS_HEAD]     [384: AMBER_MARK] [448: RED_TAIL]
[Row 2, y=128..191]: [0: WOOD]   [64: STRAP_ORG] [128: JERRY_CAN] [192: BRASS]        [256: GUN_METAL]  [320: STENCIL]       [384: WELD_BEAD]  [448: EXHAUST]
```

---

## 2. Procedural Weathering Algorithms

### A. Gravity-Driven Rain Grime Streaks
Rain washes dust and exhaust soot down vertical surfaces, leaving dark streaks running from top to bottom:

```python
# In procedural paint loop for cell coordinates (x, y):
streak = hash_noise(x, 0, seed + 3)
if streak > 0.78:
    # Streak darkens near the top and fades as it reaches the bottom edge
    intensity = 18.0 * (1.0 - y / 64.0) * (streak - 0.78) * 5.0
    color = apply_darkening(color, -intensity)
```

### B. High-Friction Paint Chipping & Edge Wear
High-contact edges and corners lose their topcoat, revealing bare primer or oxidized steel:

```python
if hash_noise(x, y, seed + 5) > 0.982:
    # Bright silver / bare steel chip
    color = apply_brightening(color, 28)
```

### C. Industrial Weld Bead Lines
Armor plates joined by electric arc welds display scalloped heat-tinted bead patterns:

```python
for i in range(64):
    for seam_pos in (16, 48):
        # Scalloped bead variation
        bead_lum = -22 + (i % 3) * 14
        paint_pixel(cell_u + i, cell_v + seam_pos, base_color + bead_lum)
        paint_pixel(cell_u + seam_pos, cell_v + i, base_color + bead_lum)
```

### D. High-Traction Deck Grit
Cargo beds and walkways feature rough, non-skid aggregate textures:

```python
grit = (hash_noise(x, y, 11) > 0.5) * 16 + (x % 4 == 0 and y % 4 == 0) * 12
deck_color = base_deck + grit - 8
```

### E. Low-Body Mud & Road Dust Accumulation
Chassis, axles, and lower quarter-panels accumulate dried mud and dust:

```python
mud_level = smooth_noise(x, y, seed + 7, cell=4) + hash_noise(x, y, seed + 8) * 0.3
if mud_level > (1.0 - mud_intensity):
    color = (88, 70, 46)  # Earth brown dried mud
```

---

## 3. Military Camouflage Palettes

Every vehicle texture supports 5 distinct faction / environment liveries:
1. **0: NATO Coyote Desert Tan:** `(168, 158, 132)` — Middle East / Badlands operational scheme.
2. **1: Woodland Olive Drab:** `(92, 108, 74)` — European temperate forest with black cloud patches.
3. **2: Arctic Snow White:** `(218, 222, 226)` — Tundra with slate grey disruptive splinters.
4. **3: Urban Stealth Grey:** `(110, 115, 122)` — City combat scheme with matte black accents.
5. **4: Special Ops Blackout:** `(42, 44, 46)` — Night assault stealth finish with dark crimson markers.
