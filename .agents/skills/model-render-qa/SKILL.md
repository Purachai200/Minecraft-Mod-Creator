---
name: model-render-qa
description: >-
  Automated quality assurance, verification runbook, and 5-view orthographic concept sheet rendering for vehicles and mechs.
  Verifies ground clearance, ramp lip ground reach, driver eye-line alignment, and scale fidelity.
---

# Model Render QA & Visual Verification Runbook

This skill defines the visual inspection protocol, rendering standards, and quality-assurance checklists required before committing any vehicle or mech model to production code.

---

## 1. The Standard 5-View Concept Sheet Layout

Every model must generate a vertical 5-panel concept sheet $(720 \times 1800\text{ px})$ matching the C-130 studio benchmark:

| Panel | Viewpoint & Camera Angles | Inspection Focus |
| :--- | :--- | :--- |
| **Panel 1** | **Isometric Front (Closed):**<br>$\text{Yaw} = 35^\circ, \text{Pitch} = -22^\circ$ | Front bumper, bullbar, winch, headlights, hood louvers, windshield rake ($28^\circ$), roof lights. |
| **Panel 2** | **Isometric Rear (Closed):**<br>$\text{Yaw} = 215^\circ, \text{Pitch} = -22^\circ$ | Closed tailgate, taillight stone guards, exhaust tips, headache rack, bedside accessories. |
| **Panel 3** | **Direct Rear (Ramp Open $90^\circ$):**<br>$\text{Yaw} = 180^\circ, \text{Pitch} = -12^\circ$ | Walk-on ramp width, internal cargo bed diamond-plate floor, tie-down rails, axle clearance. |
| **Panel 4** | **Isometric Rear (Ramp Open):**<br>$\text{Yaw} = 220^\circ, \text{Pitch} = -26^\circ$ | 3D depth of lowered ramp, approach angle, walk-on clearance for players and mechs. |
| **Panel 5** | **True Side Elevation:**<br>$\text{Yaw} = 90^\circ, \text{Pitch} = 0^\circ$ | Wheelbase proportions, ground clearance ($Y=0$ contact), approach/departure angles, cab height. |

---

## 2. Mandatory Verification Checklist

Before presenting a model to the user or writing Java classes:

1. **Ground Plane Integrity ($Y = 0.0$):**
   - The lowest point of every tire tread or landing skid must equal $Y = 0.0 \pm 0.2\text{ px}$.
   - Never float above the ground or clip below $Y = 0$.
2. **Open Ramp Ground Reach:**
   - When the rear tailgate or cargo ramp is rotated open (e.g., $\text{rotX} = 90^\circ$ or $-16^\circ$), its outer lip must reach within $\le 2\text{ px}$ of the ground plane so entities do not trip when walking up.
3. **Driver Cockpit Eye Alignment:**
   - The driver cushion top must be positioned at $Y_{\text{eye}} - 11\text{ px}$ so the player's camera aligns centered through the windshield glass.
4. **Bone Naming Standards:**
   - Steering wheels: `steer_fl`, `steer_fr` as parents of `wheel_fl`, `wheel_fr`.
   - Rear wheels: `wheel_rl`, `wheel_rr`.
   - Moving ramp: `rear_tailgate` or `ramp`.
   - Cargo tie-downs: `cargo_straps` (hidden when cargo is unmounted).
5. **No Flat Solid Colors:**
   - Every surface must possess surface noise, panel seam outlines, edge highlights, or weathering.
