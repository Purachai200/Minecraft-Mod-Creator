---
name: walkable-platform-engine
description: >-
  Architecture and physics engine for vehicle walkable moving platforms and cross-mod payload systems.
  Guides the implementation of DeckColliderEntity, non-rider entity synchronization, and strict cargo tier limits.
---

# Walkable Platform Engine & Cargo Payload System

This skill defines the technical implementation of solid moving platforms in Minecraft 1.20.1 Forge, allowing non-passenger players and entities to walk, stand, shoot, and ride on moving vehicles without rubberbanding, slipping, or falling through.

---

## 1. The Moving Platform Problem & Solution

### The Vanilla Limit
In vanilla Minecraft:
* Entities can only stand on solid world blocks or be bound as a seated passenger via `startRiding()`.
* Standing on a moving entity's bounding box causes jitter, sliding off, or falling through because Minecraft does not apply the parent entity's delta translation or angular yaw velocity to external entities.

### The `DeckColliderEntity` Architecture
To allow completely free walking on moving decks:
1. **Solid Invisible Slabs:** Spawn invisible `DeckColliderEntity` tiles tiled along the vehicle's deck (`spawnRow`).
2. **`canBeCollidedWith() == true`:** Provides true physical solid collision for feet and tires.
3. **Reactive Rider Synchronization (`carryRiders`):**
   - Every tick, detects all entities whose feet touch the deck surface (`!e.isPassenger()`).
   - Calculates the vehicle's position and yaw delta between ticks:
     $$\Delta \text{yaw} = \text{yaw}_{\text{curr}} - \text{yaw}_{\text{prev}}$$
   - Transforms the rider's relative offset vector:
     $$\begin{pmatrix} x' \\ z' \end{pmatrix} = \begin{pmatrix} \cos \theta & -\sin \theta \\ \sin \theta & \cos \theta \end{pmatrix} \begin{pmatrix} x_{\text{rel}} \\ z_{\text{rel}} \end{pmatrix}$$
4. **Client-Side Ownership for Players (No Rubberbanding):**
   - For players: update position strictly on the player's own client (`level.isClientSide && p.isLocalPlayer()`).
   - For mobs / external mechs: update position on the server.
   - This single architectural rule prevents desync and rubberbanding over high-latency multiplayer connections!

---

## 2. Strict Cargo Payload Tier System

Vehicles enforce strict size and weight class limits to maintain realistic scale and prevent oversized mechs from mounting undersized vehicles:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PAYLOAD TIER MATRIX                             │
├─────────┬──────────────────────────┬───────────────────────────────────┤
│ Tier    │ Max Dimensions & Mass     │ Eligible Cargo                    │
├─────────┼──────────────────────────┼───────────────────────────────────┤
│ Tier 1  │ Width ≤ 1.2m, Height ≤ 2.4m│ 1x Obsolete Exoframe ONLY         │
│ (Light) │ Mass ≤ 3,000 kg           │ (Titans STRICTLY REJECTED)        │
├─────────┼──────────────────────────┼───────────────────────────────────┤
│ Tier 2  │ Width ≤ 2.8m, Height ≤ 4.8m│ 1x Titan Combat Titan OR           │
│ (Medium)│ Mass ≤ 35,000 kg          │ 2-3x Obsolete Exoframes           │
├─────────┼──────────────────────────┼───────────────────────────────────┤
│ Tier 3  │ Width ≤ 6.0m, Height ≤ 6.0m│ 2x Titan Combat Titans OR          │
│ (Heavy) │ Mass ≤ 90,000 kg          │ 4-6x Obsolete Exoframes           │
├─────────┼──────────────────────────┼───────────────────────────────────┤
│ Tier 4  │ Capital Ship / Flight Deck│ 4+ Titans OR                      │
│ (Fleet) │ Mass > 200,000 kg         │ Full Platoon of Exoframes         │
└─────────┴──────────────────────────┴───────────────────────────────────┘
```

### Rejection & Notification Logic
When an ineligible entity attempts to board:
1. Play warning rejection sound: `SoundEvents.SHIELD_BLOCK` (pitch 0.8F).
2. Display action bar message: `§c[PAYLOAD ERROR] Vehicle chassis too light! Max rating: Tier 1 (Exoframe only)`.
3. Disallow docking.

---

## 3. Zero-Crash Soft-Dependency Integration

To interface with external mods (`Obsolete` Exoframes and `Titan Combat` Titans) without hard compile-time dependencies:
* Use Java reflection to check class names:
  * `"com.obsolete.entity.ExoframeEntity"`
  * `"com.titancombat.entity.BaseTitanEntity"`
* Set docked state safely:
  * Titan: `titan.setSitting(true)`, `titan.setStandbyMode(true)`.
  * Exoframe: `invoke("setCrouching", true)`.
* Zero out velocity: `setDeltaMovement(Vec3.ZERO)`, `fallDistance = 0.0F`.
* If neither mod is installed, the vehicles function seamlessly carrying vanilla players, mobs, and chests!
