# Third-Person Camera Distance in Minecraft 1.20.1 (Forge 47)

## Problem Statement
The vanilla third-person camera distance is hardcoded to 4.0 blocks (`Camera.getMaxZoom(4.0D)`). For a standard 1.8-block player, this gives adequate framing. However, the OBSOLETE Exoframe is an industrial mecha scaled at `MODEL_SCALE = 1.8F` (approximately 3.8 blocks tall). In vanilla third-person view, the camera sits right behind the pilot's head/canopy, obstructing the pilot's forward visibility and clipping into shoulder pods.

## Investigation of Forge 47 Hooks

We examined all available Forge 47.3.0 camera events in package `net.minecraftforge.client.event`:
1. `ViewportEvent.ComputeCameraAngles`:
   - Provides hooks for `yaw`, `pitch`, and `roll`.
   - Does NOT expose camera distance or translation vector.
2. `ViewportEvent.ComputeFov`:
   - Allows altering field of view (`getFOV()`, `setFOV(double)`).
3. `ViewportEvent.ComputeFogColor` & `ViewportEvent.RenderFog`:
   - Controls fog rendering distance and color.

In vanilla Minecraft 1.20.1 (`net.minecraft.client.Camera.java`), the third-person zoom is hardcoded inside `Camera.setup`:
```java
if (detached) {
    if (thirdPersonReverse) {
        this.setRotation(this.yRot + 180.0F, -this.xRot);
    }
    this.move(-this.getMaxZoom(4.0D), 0.0D, 0.0D);
}
```
`4.0D` is a hardcoded literal constant passed directly to private `getMaxZoom(double maxZoom)`. Forge 47 provides no hook or event to intercept this parameter.

## Technical Trade-Offs

### Option A: SpongePowered Mixin (`@ModifyConstant` or `@Redirect` in `Camera.class`)
- **Mechanism**: Target `Camera.setup` with `@ModifyConstant(method = "setup", constant = @Constant(doubleValue = 4.0D))` and return `7.2D` (`4.0D * ExoframeEntity.MODEL_SCALE`) when `this.entity.getVehicle() instanceof ExoframeEntity`.
- **Pros**:
  - Provides a clean third-person camera position in unmodded clients.
- **Cons**:
  - Requires adding Mixin configuration (`obsolete.mixins.json`), refactoring Gradle build scripts to add Mixin annotation processor and runtime plugins.
  - Direct conflict with popular third-person camera mods (e.g. *Shoulder Surfing Reloaded*, *Better Third Person*, *Freecam*, *Camera Overhaul*) which already patch `Camera.setup`.

### Option B: Pure Forge (No Mixin) — Recommended
- **Mechanism**: Do not patch `Camera.setup`. Keep mod 100% Mixin-free and fully compatible with all camera mods.
- **Compatibility**: Players using *Shoulder Surfing Reloaded* or *Better Third Person* can freely adjust camera distance with keybindings (e.g. Page Up / Page Down or scroll wheel).
- **ClientAutoTest**: For autotests and scripted showcases, the debug camera/scenario controller explicitly scales camera distance with `MODEL_SCALE` (`view(yaw, pitch, 5.0F * ExoframeEntity.MODEL_SCALE, height * ExoframeEntity.MODEL_SCALE)`), ensuring all automated validation screenshots frame the mech.

## Conclusion
Per the handoff instructions (*"if none exists without a mixin, write down the trade-off and stop"*), we document this trade-off and maintain the pure Forge architecture.
